import openai
import google.generativeai as genai
import anthropic
import json
import logging
from typing import Dict, Optional, Any
from config.config import Config
import base64
import requests

logger = logging.getLogger(__name__)

class LLMExtractionService:
    def extract_receipt_data_from_pdf(self, pdf_path: str) -> Dict[str, Any]:
        """
        Extract receipt data from a PDF file by extracting text and passing to LLM
        """
        import PyPDF2
        try:
            with open(pdf_path, 'rb') as f:
                reader = PyPDF2.PdfReader(f)
                text = "\n".join(page.extract_text() or '' for page in reader.pages)
            if not text.strip():
                logger.error(f"No text extracted from PDF: {pdf_path}")
                return {}
            
            # Log the extracted text for debugging
            logger.info(f"Extracted text from PDF: {pdf_path}")
            logger.info(f"Text content: {text}")
            
            return self.extract_receipt_data_from_text(text)
        except Exception as e:
            logger.error(f"Failed to extract text from PDF: {str(e)}")
            return {}
    """
    LLM-based document extraction service with multiple provider support
    Used as a fallback when OCR fails
    """
    
    def __init__(self):
        self.config = Config()
        self._setup_clients()
    
    def _setup_clients(self):
        """Initialize LLM clients based on available API keys"""
        self.openai_client = None
        self.gemini_client = None
        self.claude_client = None
        
        # OpenAI setup
        if hasattr(self.config, 'OPENAI_API_KEY') and self.config.OPENAI_API_KEY:
            openai.api_key = self.config.OPENAI_API_KEY
            self.openai_client = openai
            logger.info("OpenAI client initialized")
        
        # Google Gemini setup
        if hasattr(self.config, 'GEMINI_API_KEY') and self.config.GEMINI_API_KEY:
            genai.configure(api_key=self.config.GEMINI_API_KEY)
            self.gemini_client = genai.GenerativeModel('gemini-1.5-flash')
            logger.info("Gemini client initialized")
            logger.info(f"GEMINI_API_KEY loaded: {self.config.GEMINI_API_KEY is not None}")
        
        # Anthropic Claude setup
        if hasattr(self.config, 'CLAUDE_API_KEY') and self.config.CLAUDE_API_KEY:
            self.claude_client = anthropic.Anthropic(api_key=self.config.CLAUDE_API_KEY)
            logger.info("Claude client initialized")

        # Google Vision setup (just log presence)
        if hasattr(self.config, 'GOOGLE_VISION_API_KEY') and self.config.GOOGLE_VISION_API_KEY:
            logger.info(f"GOOGLE_VISION_API_KEY loaded: {self.config.GOOGLE_VISION_API_KEY is not None}")

    def _extract_with_google_vision(self, image_path: str) -> dict:
        """Extract text from image using Google Vision API (OCR)"""
        import base64
        import requests
        if not hasattr(self.config, 'GOOGLE_VISION_API_KEY') or not self.config.GOOGLE_VISION_API_KEY:
            logger.error("No Google Vision API key configured.")
            return {}
        try:
            with open(image_path, "rb") as image_file:
                encoded_image = base64.b64encode(image_file.read()).decode()
            url = f"https://vision.googleapis.com/v1/images:annotate?key={self.config.GOOGLE_VISION_API_KEY}"
            payload = {
                "requests": [
                    {
                        "image": {"content": encoded_image},
                        "features": [{"type": "TEXT_DETECTION"}]
                    }
                ]
            }
            logger.info("Calling Google Vision API for OCR...")
            response = requests.post(url, json=payload)
            logger.info(f"Google Vision API response status: {response.status_code}")
            if response.status_code == 200:
                result = response.json()
                logger.info(f"Google Vision API result: {result}")
                # Parse the result for text
                text = result['responses'][0].get('fullTextAnnotation', {}).get('text', '')
                # Use the existing text extraction logic
                return self.extract_receipt_data_from_text(text)
            else:
                logger.error(f"Google Vision API error: {response.text}")
                return {}
        except Exception as e:
            logger.error(f"Google Vision API call failed: {str(e)}")
            return {}
    
    def extract_receipt_data_from_text(self, text: str) -> Dict[str, Any]:
        """
        Extract receipt data from text using LLM
        Tries multiple providers in order of preference
        """
        try:
            # Try OpenAI first (usually most reliable)
            if self.openai_client:
                result = self._extract_with_openai(text)
                if result:
                    logger.info("Successfully extracted data using OpenAI")
                    return result
            
            # Try Gemini as fallback
            if self.gemini_client:
                result = self._extract_with_gemini(text)
                if result:
                    logger.info("Successfully extracted data using Gemini")
                    return result
            
            # Try Claude as final fallback
            if self.claude_client:
                result = self._extract_with_claude(text)
                if result:
                    logger.info("Successfully extracted data using Claude")
                    return result
            
            logger.error("No LLM providers available or all failed")
            return {}
            
        except Exception as e:
            logger.error(f"LLM extraction failed: {str(e)}")
            return {}
    
    def extract_receipt_data_from_image(self, image_path: str) -> Dict[str, Any]:
        """
        Extract receipt data from image using LLM vision capabilities
        """
        try:
            # Try OpenAI Vision first
            if self.openai_client:
                logger.info(f"Calling OpenAI Vision API for image: {image_path}")
                result = self._extract_from_image_openai(image_path)
                logger.info(f"OpenAI Vision API result: {result}")
                if result:
                    logger.info("Successfully extracted data from image using OpenAI Vision")
                    return result
            
            # Try Gemini Vision
            if self.gemini_client:
                logger.info(f"Calling Gemini Vision API for image: {image_path}")
                result = self._extract_from_image_gemini(image_path)
                logger.info(f"Gemini Vision API result: {result}")
                if result:
                    logger.info("Successfully extracted data from image using Gemini Vision")
                    return result
            
            # Try Google Vision as final fallback
            if hasattr(self.config, 'GOOGLE_VISION_API_KEY') and self.config.GOOGLE_VISION_API_KEY:
                logger.info(f"Calling Google Vision API for image: {image_path}")
                result = self._extract_with_google_vision(image_path)
                logger.info(f"Google Vision API OCR result: {result}")
                if result:
                    logger.info("Successfully extracted data from image using Google Vision API")
                    return result
            
            logger.error("No vision-capable LLM providers available or all failed")
            return {}
            
        except Exception as e:
            logger.error(f"LLM image extraction failed: {str(e)}")
            return {}
    
    def _get_extraction_prompt(self) -> str:
        """Get the standardized prompt for receipt data extraction"""
        return """
Act as a receipt data extraction expert. You MUST carefully analyze ANY transaction document (receipts, invoices, tickets, passes) and extract ALL available information with high accuracy.

CRITICAL INSTRUCTIONS FOR MERCHANT NAME:
1. Look for business/organization names at the TOP of the document
2. Accept ANY type of merchant: restaurants ("APPLEBEE'S"), stores ("WALMART"), transit systems ("San Francisco Transit"), services, government agencies
3. For transit passes/tickets: use city name + "Transit" or the transit authority name
4. For government/public services: use the agency or location name
5. NEVER return null for merchant_name - always find SOME identifying name/organization
6. If no clear business name, use location or service provider name

DOCUMENT TYPE RECOGNITION:
- Restaurant receipts: Business name at top, food items, tax, total
- Retail receipts: Store name, product items, tax, total  
- Transit passes/tickets: Transit authority, pass type, zones, fare amount
- Service receipts: Service provider, description, amount
- Parking tickets: Location, duration, fee

EXTRACTION RULES:
- merchant_name: ANY business, organization, or service provider name (REQUIRED)
- total_amount: Final amount paid (look for "Total", "Amount Due", fare, fee)
- tax_amount: Tax if specified (may not apply to transit/government)
- subtotal: Amount before tax if shown
- purchased_at: Transaction date in YYYY-MM-DD format
- payment_method: Payment type if mentioned
- items: Services, products, or pass types with prices

EXAMPLES:
Restaurant: {"merchant_name": "APPLEBEE'S", "total_amount": 128.23, "purchased_at": "2018-12-01"}
Transit: {"merchant_name": "San Francisco Transit", "total_amount": 7.50, "purchased_at": "2018-07-23", "items": [{"name": "DAY PASS ZONE 1", "price": 7.50}]}
Retail: {"merchant_name": "WALMART", "total_amount": 45.67, "purchased_at": "2024-01-15"}

Return ONLY a valid JSON object. Use null only if information is completely absent from the document.

Document text:
"""
    
    def _extract_with_openai(self, text: str) -> Optional[Dict[str, Any]]:
        """Extract using OpenAI GPT"""
        try:
            response = self.openai_client.ChatCompletion.create(
                model="gpt-4o-mini",  # Cost-effective model
                messages=[
                    {
                        "role": "system",
                        "content": "You are a receipt data extraction expert. Extract information accurately and return only valid JSON."
                    },
                    {
                        "role": "user",
                        "content": self._get_extraction_prompt() + text
                    }
                ],
                max_tokens=500,
                temperature=0.1
            )
            
            result_text = response.choices[0].message.content.strip()
            return json.loads(result_text)
            
        except Exception as e:
            logger.error(f"OpenAI extraction failed: {str(e)}")
            return None
    
    def _extract_with_gemini(self, text: str) -> Optional[Dict[str, Any]]:
        """Extract using Google Gemini"""
        try:
            prompt = self._get_extraction_prompt() + text
            response = self.gemini_client.generate_content(prompt)
            
            result_text = response.text.strip()
            # Clean up response if it has markdown formatting
            if result_text.startswith('```json'):
                result_text = result_text.replace('```json', '').replace('```', '').strip()
            
            return json.loads(result_text)
            
        except Exception as e:
            logger.error(f"Gemini extraction failed: {str(e)}")
            return None
    
    def _extract_with_claude(self, text: str) -> Optional[Dict[str, Any]]:
        """Extract using Anthropic Claude"""
        try:
            response = self.claude_client.messages.create(
                model="claude-3-haiku-20240307",  # Cost-effective model
                max_tokens=500,
                messages=[
                    {
                        "role": "user",
                        "content": self._get_extraction_prompt() + text
                    }
                ]
            )
            
            result_text = response.content[0].text.strip()
            return json.loads(result_text)
            
        except Exception as e:
            logger.error(f"Claude extraction failed: {str(e)}")
            return None
    
    def _extract_from_image_openai(self, image_path: str) -> Optional[Dict[str, Any]]:
        """Extract from image using OpenAI Vision"""
        try:
            with open(image_path, 'rb') as image_file:
                image_data = base64.b64encode(image_file.read()).decode('utf-8')
            
            response = self.openai_client.ChatCompletion.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": "Extract receipt data from this image and return as JSON: " + self._get_extraction_prompt()
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{image_data}"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=500
            )
            
            result_text = response.choices[0].message.content.strip()
            return json.loads(result_text)
            
        except Exception as e:
            logger.error(f"OpenAI Vision extraction failed: {str(e)}")
            return None
    
    def _extract_from_image_gemini(self, image_path: str) -> Optional[Dict[str, Any]]:
        """Extract from image using Gemini Vision"""
        try:
            with open(image_path, 'rb') as image_file:
                image_data = image_file.read()
            
            # Upload image to Gemini
            image_part = {
                "mime_type": "image/jpeg",
                "data": image_data
            }
            
            prompt = "Extract receipt data from this image: " + self._get_extraction_prompt()
            response = self.gemini_client.generate_content([prompt, image_part])
            
            result_text = response.text.strip()
            if result_text.startswith('```json'):
                result_text = result_text.replace('```json', '').replace('```', '').strip()
            
            return json.loads(result_text)
            
        except Exception as e:
            logger.error(f"Gemini Vision extraction failed: {str(e)}")
            return None
