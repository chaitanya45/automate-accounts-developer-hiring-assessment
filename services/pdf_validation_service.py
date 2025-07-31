import PyPDF2
import os
from typing import Tuple
import logging

logger = logging.getLogger(__name__)

class PDFValidationService:
    
    @staticmethod
    def validate_pdf(file_path: str) -> Tuple[bool, str]:
        """
        Validate if file is a valid PDF
        Returns: (is_valid, error_message)
        """
        try:
            # Debug logging
            logger.info(f"Validating PDF file: {file_path}")
            logger.info(f"File exists check: {os.path.exists(file_path)}")
            
            # Check if file exists
            if not os.path.exists(file_path):
                logger.error(f"File does not exist at path: {file_path}")
                # Try to list the directory to see what's there
                try:
                    directory = os.path.dirname(file_path)
                    if os.path.exists(directory):
                        files_in_dir = os.listdir(directory)
                        logger.info(f"Files in directory {directory}: {files_in_dir}")
                    else:
                        logger.error(f"Directory does not exist: {directory}")
                except Exception as dir_e:
                    logger.error(f"Error checking directory: {str(dir_e)}")
                return False, "File does not exist"
            
            # Check file extension
            if not file_path.lower().endswith('.pdf'):
                return False, "File is not a PDF"
            
            # Check if file is not empty
            if os.path.getsize(file_path) == 0:
                return False, "File is empty"
            
            # Try to open and read PDF
            with open(file_path, 'rb') as file:
                try:
                    pdf_reader = PyPDF2.PdfReader(file)
                    
                    # Check if PDF has pages
                    if len(pdf_reader.pages) == 0:
                        return False, "PDF has no pages"
                    
                    # Try to read first page to ensure it's not corrupted
                    first_page = pdf_reader.pages[0]
                    _ = first_page.extract_text()
                    
                    logger.info(f"PDF validation successful: {file_path}")
                    return True, "Valid PDF"
                    
                except PyPDF2.errors.PdfReadError as e:
                    return False, f"Invalid PDF format: {str(e)}"
                except Exception as e:
                    return False, f"PDF read error: {str(e)}"
            
        except Exception as e:
            logger.error(f"PDF validation error: {str(e)}")
            return False, f"Validation failed: {str(e)}"
    
    @staticmethod
    def get_pdf_info(file_path: str) -> dict:
        """Get PDF metadata information"""
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                return {
                    'page_count': len(pdf_reader.pages),
                    'metadata': pdf_reader.metadata,
                    'file_size': os.path.getsize(file_path)
                }
        except Exception as e:
            logger.error(f"Failed to get PDF info: {str(e)}")
            return {}
