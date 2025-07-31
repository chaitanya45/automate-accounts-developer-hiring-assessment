import pytesseract
from PIL import Image
import cv2
import numpy as np
import re
from datetime import datetime
from typing import Dict, Optional
import logging
import os

logger = logging.getLogger(__name__)

class OCRService:
    
    def __init__(self, tesseract_cmd: str = None):
        if tesseract_cmd and os.path.exists(tesseract_cmd):
            pytesseract.pytesseract.tesseract_cmd = tesseract_cmd
        
        # Initialize LLM service for fallback
        self.llm_service = None
        try:
            from services.llm_extraction_service import LLMExtractionService
            self.llm_service = LLMExtractionService()
            logger.info("LLM extraction service initialized as fallback")
        except Exception as e:
            logger.warning(f"LLM service not available: {str(e)}")
    
    def extract_text_from_image(self, image_path: str) -> str:
        """Extract text from image using Tesseract OCR"""
        try:
            # Load and preprocess image
            image = cv2.imread(image_path)
            if image is None:
                return ""
            
            preprocessed = self._preprocess_image(image)
            
            # Extract text
            text = pytesseract.image_to_string(preprocessed, config='--psm 6')
            return text.strip()
        except Exception as e:
            logger.error(f"OCR extraction failed: {str(e)}")
            return ""
    
    def _preprocess_image(self, image):
        """Preprocess image for better OCR results"""
        try:
            # Convert to grayscale
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Apply denoising
            denoised = cv2.fastNlMeansDenoising(gray)
            
            # Apply threshold for better text recognition
            _, thresh = cv2.threshold(denoised, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            
            return thresh
        except Exception as e:
            logger.error(f"Image preprocessing failed: {str(e)}")
            return image
    
    def extract_receipt_data(self, text: str, image_path: str = None) -> Dict:
        """
        Extract structured data from OCR text with LLM fallback
        """
        logger.info("Starting receipt data extraction with OCR")
        
        # First try traditional OCR extraction
        ocr_data = self._extract_with_ocr(text)
        
        # Check if OCR extraction was successful
        if self._is_extraction_successful(ocr_data):
            logger.info("OCR extraction successful")
            ocr_data['extraction_method'] = 'OCR'
            return ocr_data
        
        # If OCR failed and LLM service is available, try LLM extraction
        if self.llm_service:
            logger.info("OCR extraction failed, trying LLM fallback")
            
            # Try LLM text extraction first
            llm_data = self.llm_service.extract_receipt_data_from_text(text)
            if self._is_extraction_successful(llm_data):
                logger.info("LLM text extraction successful")
                llm_data['extraction_method'] = 'LLM_Text'
                llm_data['raw_text'] = text
                return llm_data
            
            # If image path is provided, try LLM vision extraction
            if image_path and os.path.exists(image_path):
                logger.info("Trying LLM vision extraction")
                llm_vision_data = self.llm_service.extract_receipt_data_from_image(image_path)
                if self._is_extraction_successful(llm_vision_data):
                    logger.info("LLM vision extraction successful")
                    llm_vision_data['extraction_method'] = 'LLM_Vision'
                    llm_vision_data['raw_text'] = text
                    return llm_vision_data
        
        # If all methods failed, return OCR data with fallback flag
        logger.warning("All extraction methods failed, returning OCR data")
        ocr_data['extraction_method'] = 'OCR_Failed'
        return ocr_data
    
    def _extract_with_ocr(self, text: str) -> Dict:
        """Traditional OCR-based extraction"""
        data = {
            'merchant_name': self._extract_merchant_name(text),
            'total_amount': self._extract_total_amount(text),
            'tax_amount': self._extract_tax_amount(text),
            'subtotal': self._extract_subtotal(text),
            'purchased_at': self._extract_date(text),
            'payment_method': self._extract_payment_method(text),
            'raw_text': text
        }
        return data
    
    def _is_extraction_successful(self, data: Dict) -> bool:
        """
        Check if extraction was successful based on key fields
        """
        if not data:
            return False
        
        # Consider successful if we have merchant name AND (total amount OR date)
        has_merchant = data.get('merchant_name') is not None
        has_total = data.get('total_amount') is not None
        has_date = data.get('purchased_at') is not None
        
        # At minimum, we need merchant name and either total or date
        return has_merchant and (has_total or has_date)
    
    def _extract_merchant_name(self, text: str) -> Optional[str]:
        """Extract merchant name from text"""
        try:
            lines = text.split('\n')
            # Usually merchant name is in the first few lines
            for line in lines[:5]:
                line = line.strip()
                if len(line) > 3 and not re.search(r'\d', line):
                    # Filter out common receipt headers
                    if not any(word in line.lower() for word in ['receipt', 'invoice', 'bill', 'order']):
                        return line
        except Exception as e:
            logger.error(f"Merchant name extraction failed: {str(e)}")
        return None
    
    def _extract_total_amount(self, text: str) -> Optional[float]:
        """Extract total amount from text"""
        try:
            # Hotel folio specific patterns (high priority) - handle variations
            hotel_patterns = [
                r'total\s*billed\s*to\s*suite[:\s]*(\d+,?\d*\.?\d*)',
                r'totalbilledtosuite[:\s]*(\d+,?\d*\.?\d*)',  # No spaces
                r'total\s*billed[:\s]*(\d+,?\d*\.?\d*)',
                r'folio\s*balance[:\s]*(\d+,?\d*\.?\d*)',
                r'account\s*balance[:\s]*(\d+,?\d*\.?\d*)',
            ]
            
            # General receipt patterns (medium priority)
            general_patterns = [
                r'total[:\s]*\$?\s*(\d+,?\d*\.?\d*)',
                r'amount\s*due[:\s]*\$?\s*(\d+,?\d*\.?\d*)',
                r'grand\s*total[:\s]*\$?\s*(\d+,?\d*\.?\d*)',
                r'balance[:\s]*\$?\s*(\d+,?\d*\.?\d*)',
                r'amount[:\s]*\$?\s*(\d+,?\d*\.?\d*)',
            ]
            
            # Look for context-aware amounts near folio/total keywords
            contextual_patterns = [
                # Look for amounts after "total" keywords with some flexibility
                r'total[^0-9]{0,50}(\d{1,4}[,.]?\d{2,3}\.\d{2})',
                r'billed[^0-9]{0,50}(\d{1,4}[,.]?\d{2,3}\.\d{2})',
                r'suite[^0-9]{0,50}(\d{1,4}[,.]?\d{2,3}\.\d{2})',
            ]
            
            # Try hotel-specific patterns first (highest priority)
            for pattern in hotel_patterns:
                matches = re.findall(pattern, text, re.IGNORECASE | re.MULTILINE)
                for match in matches:
                    try:
                        amount_str = match.replace(',', '').strip()
                        amount = float(amount_str)
                        if amount > 0:
                            logger.info(f"Found hotel total amount: {amount}")
                            return amount
                    except ValueError:
                        continue
            
            # Try contextual patterns (look for amounts near keywords)
            for pattern in contextual_patterns:
                matches = re.findall(pattern, text, re.IGNORECASE | re.MULTILINE | re.DOTALL)
                for match in matches:
                    try:
                        amount_str = match.replace(',', '').strip()
                        amount = float(amount_str)
                        if amount > 100:  # Only consider substantial amounts for totals
                            logger.info(f"Found contextual total amount: {amount}")
                            return amount
                    except ValueError:
                        continue
            
            # Then try general receipt patterns
            for pattern in general_patterns:
                matches = re.findall(pattern, text, re.IGNORECASE | re.MULTILINE)
                for match in matches:
                    try:
                        amount_str = match.replace(',', '').strip()
                        amount = float(amount_str)
                        if amount > 0:
                            logger.info(f"Found general total amount: {amount}")
                            return amount
                    except ValueError:
                        continue
            
            # Finally, look for standalone large amounts in the last part of document
            # Split text into lines and look for amounts in the last third
            lines = text.split('\n')
            last_third_start = len(lines) * 2 // 3
            last_third_text = '\n'.join(lines[last_third_start:])
            
            # Look for substantial amounts (likely totals) in various formats
            amount_patterns = [
                r'(\d{1,4},\d{3}\.\d{2})',      # Like 2,174.62
                r'(\d{1,4}\.\d{2})',           # Like 174.62 or 2174.62
                r'\$\s*(\d+,?\d*\.\d{2})',     # Dollar amounts
            ]
            
            all_amounts = []
            for pattern in amount_patterns:
                matches = re.findall(pattern, last_third_text, re.IGNORECASE | re.MULTILINE)
                for match in matches:
                    try:
                        amount_str = match.replace(',', '').strip()
                        amount = float(amount_str)
                        # For hotel folios, look for amounts over $100 (likely room charges)
                        if amount >= 100:
                            all_amounts.append(amount)
                    except ValueError:
                        continue
            
            if all_amounts:
                # Return the largest amount from the last third of the document
                largest_amount = max(all_amounts)
                logger.info(f"Found standalone amount in last third: {largest_amount}")
                return largest_amount
                
            # If no substantial amounts found, fall back to the largest amount in entire text
            all_text_amounts = []
            for pattern in amount_patterns:
                matches = re.findall(pattern, text, re.IGNORECASE | re.MULTILINE)
                for match in matches:
                    try:
                        amount_str = match.replace(',', '').strip()
                        amount = float(amount_str)
                        if amount > 0:
                            all_text_amounts.append(amount)
                    except ValueError:
                        continue
            
            if all_text_amounts:
                largest_total = max(all_text_amounts)
                logger.info(f"Found fallback largest amount: {largest_total}")
                return largest_total
                
        except Exception as e:
            logger.error(f"Total amount extraction failed: {str(e)}")
        return None
    
    def _extract_tax_amount(self, text: str) -> Optional[float]:
        """Extract tax amount from text"""
        try:
            patterns = [
                r'tax[:\s]*\$?(\d+\.?\d*)',
                r'gst[:\s]*\$?(\d+\.?\d*)',
                r'vat[:\s]*\$?(\d+\.?\d*)'
            ]
            
            for pattern in patterns:
                matches = re.findall(pattern, text.lower())
                if matches:
                    try:
                        return float(matches[0])
                    except ValueError:
                        continue
        except Exception as e:
            logger.error(f"Tax amount extraction failed: {str(e)}")
        return None
    
    def _extract_subtotal(self, text: str) -> Optional[float]:
        """Extract subtotal from text"""
        try:
            patterns = [
                r'subtotal[:\s]*\$?(\d+\.?\d*)',
                r'sub total[:\s]*\$?(\d+\.?\d*)',
                r'sub-total[:\s]*\$?(\d+\.?\d*)'
            ]
            
            for pattern in patterns:
                matches = re.findall(pattern, text.lower())
                if matches:
                    try:
                        return float(matches[0])
                    except ValueError:
                        continue
        except Exception as e:
            logger.error(f"Subtotal extraction failed: {str(e)}")
        return None
    
    def _extract_date(self, text: str) -> Optional[str]:
        """Extract purchase date from text"""
        try:
            # More comprehensive date patterns
            date_patterns = [
                r'(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',     # MM/DD/YYYY, DD/MM/YYYY
                r'(\d{2,4}[/-]\d{1,2}[/-]\d{1,2})',     # YYYY/MM/DD, YYYY/DD/MM
                r'(\w+ \d{1,2}, \d{4})',                # Month DD, YYYY
                r'(\d{1,2} \w+ \d{4})',                 # DD Month YYYY
                r'(\d{1,2}-\w{3}-\d{4})',               # DD-MMM-YYYY
                r'(\w{3} \d{1,2}, \d{4})',              # MMM DD, YYYY
                r'(\d{4}-\d{2}-\d{2})',                 # YYYY-MM-DD (ISO format)
                r'(\d{2}\.\d{2}\.\d{4})',               # DD.MM.YYYY
                r'date[:\s]*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',  # "Date: MM/DD/YYYY"
                r'(\d{1,2}[/-]\d{1,2}[/-]\d{2})',       # MM/DD/YY
            ]
            
            # Look for dates in multiple formats
            for pattern in date_patterns:
                matches = re.findall(pattern, text, re.IGNORECASE)
                if matches:
                    for date_str in matches:
                        try:
                            # Try multiple date formats
                            date_formats = [
                                '%m/%d/%Y', '%d/%m/%Y', '%Y/%m/%d',
                                '%m/%d/%y', '%d/%m/%y', '%y/%m/%d',
                                '%B %d, %Y', '%d %B %Y', '%b %d, %Y',
                                '%d-%b-%Y', '%Y-%m-%d', '%d.%m.%Y'
                            ]
                            
                            for fmt in date_formats:
                                try:
                                    parsed_date = datetime.strptime(date_str, fmt)
                                    return parsed_date.isoformat()
                                except ValueError:
                                    continue
                        except:
                            continue
                            
        except Exception as e:
            logger.error(f"Date extraction failed: {str(e)}")
        return None
    
    def _extract_payment_method(self, text: str) -> Optional[str]:
        """Extract payment method from text"""
        try:
            payment_methods = ['cash', 'credit', 'debit', 'visa', 'mastercard', 'amex', 'paypal']
            text_lower = text.lower()
            
            for method in payment_methods:
                if method in text_lower:
                    return method.capitalize()
        except Exception as e:
            logger.error(f"Payment method extraction failed: {str(e)}")
        return None
