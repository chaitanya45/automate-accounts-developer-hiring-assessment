import os
from werkzeug.utils import secure_filename
from services.ocr_service import OCRService
from services.pdf_validation_service import PDFValidationService
from repositories.receipt_file_repository import ReceiptFileRepository
from repositories.receipt_repository import ReceiptRepository
import logging
import tempfile

# Import for PDF to image conversion
try:
    from pdf2image import convert_from_path
    PDF2IMAGE_AVAILABLE = True
except ImportError:
    PDF2IMAGE_AVAILABLE = False

logger = logging.getLogger(__name__)

class FileProcessingService:
    def process_file(self, file_id: str) -> tuple:
        """
        Process PDF file with LLM/AI extraction only (no OCR, no image conversion)
        Returns: (success, receipt_data, error_message)
        """
        receipt_file = ReceiptFileRepository.get_by_id(file_id)
        if not receipt_file:
            return False, None, "File not found"
        if not receipt_file['is_valid']:
            return False, None, "File is not valid"

        # Use only LLM/AI extraction from PDF file directly
        if hasattr(self.ocr_service, 'llm_service') and self.ocr_service.llm_service:
            logger.info("Starting LLM extraction process (using PDF file directly, no OCR, no image conversion)...")
            llm_data = self.ocr_service.llm_service.extract_receipt_data_from_pdf(receipt_file['file_path'])
            logger.info(f"LLM extraction result: {llm_data}")
            # Check if LLM extraction was successful
            has_merchant = llm_data.get('merchant_name') is not None
            has_total = llm_data.get('total_amount') is not None
            has_date = llm_data.get('purchased_at') is not None
            extraction_success = has_merchant and (has_total or has_date)
            logger.info(f"LLM Extraction success: {extraction_success} (merchant: {llm_data.get('merchant_name')}, total: {llm_data.get('total_amount')}, date: {llm_data.get('purchased_at')})")
            if extraction_success:
                # Mark file as processed and create receipt
                existing_receipt = ReceiptRepository.get_by_file_id(file_id)
                if existing_receipt:
                    updated_receipt = ReceiptRepository.update(existing_receipt['id'], **llm_data)
                    llm_data = updated_receipt
                else:
                    new_receipt = ReceiptRepository.create(
                        file_id=file_id,
                        file_path=receipt_file['file_path'],
                        **llm_data
                    )
                    llm_data = new_receipt
                ReceiptFileRepository.mark_processed(file_id)
                return True, llm_data, None
            else:
                return False, llm_data, f"LLM extraction failed. LLM output: {llm_data}"
        else:
            logger.error("No LLM service available for extraction.")
            return False, None, "No LLM service available for extraction."
    
    def __init__(self, upload_folder: str, tesseract_cmd: str = None):
        self.upload_folder = upload_folder
        self.ocr_service = OCRService(tesseract_cmd)
        self.pdf_validator = PDFValidationService()
        
        # Ensure upload folder exists
        os.makedirs(upload_folder, exist_ok=True)
    
    def allowed_file(self, filename: str) -> bool:
        """Check if file extension is allowed"""
        return '.' in filename and \
               filename.rsplit('.', 1)[1].lower() == 'pdf'
    
    def validate_file(self, file_path: str) -> tuple:
        """
        Validate uploaded PDF file
        Returns: (is_valid, error_message)
        """
        try:
            is_valid, error_message = self.pdf_validator.validate_pdf(file_path)
            return is_valid, error_message
        except Exception as e:
            logger.error(f"File validation error: {str(e)}")
            return False, f"Validation failed: {str(e)}"
    
    def save_uploaded_file(self, file, filename: str = None) -> tuple:
        """
        Save uploaded file and create database record
        Returns: (receipt_file_id, file_path, error_message)
        """
        try:
            if filename is None:
                filename = file.filename
            # Secure the filename
            filename = secure_filename(filename)
            
            # Ensure receipts subdirectory exists
            receipts_folder = os.path.join(self.upload_folder, 'receipts')
            os.makedirs(receipts_folder, exist_ok=True)
            
            # Check for duplicate files
            existing_file = ReceiptFileRepository.get_by_file_name(filename)
            if existing_file:
                # Update existing file
                file_path = existing_file['file_path']
                file.save(file_path)
                return existing_file['id'], file_path, None
            
            # Create new file with receipts subdirectory
            file_path = os.path.join(receipts_folder, filename)
            file.save(file_path)
            
            # Create database record
            receipt_file = ReceiptFileRepository.create(filename, file_path)
            return receipt_file['id'], file_path, None
        except Exception as e:
            logger.error(f"File save error: {str(e)}")
            return None, None, str(e)
