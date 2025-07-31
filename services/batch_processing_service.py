import os
import glob
from typing import List, Dict, Any
from services.file_processing_service import FileProcessingService
from repositories.receipt_file_repository import ReceiptFileRepository
from repositories.receipt_repository import ReceiptRepository
import logging

logger = logging.getLogger(__name__)

class BatchProcessingService:
    """Service to process existing PDF files in directory structure"""
    
    def __init__(self, base_directory: str):
        self.base_directory = base_directory
        self.file_service = FileProcessingService("uploads/receipts")
    
    def discover_pdf_files(self) -> List[Dict[str, str]]:
        """
        Discover all PDF files in the directory structure
        Returns list of dictionaries with file info
        """
        pdf_files = []
        
        # Search for PDF files in year directories (2018/, 2019/, etc.)
        year_pattern = os.path.join(self.base_directory, "[0-9][0-9][0-9][0-9]")
        year_dirs = glob.glob(year_pattern)
        
        for year_dir in year_dirs:
            # Search recursively in each year directory
            pdf_pattern = os.path.join(year_dir, "**", "*.pdf")
            pdf_files_in_year = glob.glob(pdf_pattern, recursive=True)
            
            for pdf_file in pdf_files_in_year:
                # Extract year and category from path
                relative_path = os.path.relpath(pdf_file, self.base_directory)
                path_parts = relative_path.split(os.sep)
                
                year = path_parts[0] if len(path_parts) > 0 else "unknown"
                category = path_parts[1] if len(path_parts) > 2 else "uncategorized"
                filename = os.path.basename(pdf_file)
                
                pdf_files.append({
                    'file_path': pdf_file,
                    'filename': filename,
                    'year': year,
                    'category': category,
                    'relative_path': relative_path
                })
        
        return pdf_files
    
    def process_all_pdfs(self) -> Dict[str, Any]:
        """
        Process all discovered PDF files
        Returns summary of processing results
        """
        pdf_files = self.discover_pdf_files()
        
        results = {
            'total_files': len(pdf_files),
            'processed': 0,
            'failed': 0,
            'skipped': 0,
            'details': []
        }
        
        logger.info(f"Found {len(pdf_files)} PDF files to process")
        
        for pdf_info in pdf_files:
            try:
                result = self._process_single_pdf(pdf_info)
                results['details'].append(result)
                
                if result['status'] == 'processed':
                    results['processed'] += 1
                elif result['status'] == 'failed':
                    results['failed'] += 1
                elif result['status'] == 'skipped':
                    results['skipped'] += 1
                    
            except Exception as e:
                logger.error(f"Error processing {pdf_info['filename']}: {str(e)}")
                results['failed'] += 1
                results['details'].append({
                    'filename': pdf_info['filename'],
                    'status': 'failed',
                    'error': str(e)
                })
        
        return results
    
    def _process_single_pdf(self, pdf_info: Dict[str, str]) -> Dict[str, Any]:
        """Process a single PDF file"""
        filename = pdf_info['filename']
        file_path = pdf_info['file_path']
        
        # Check if file already exists in database
        existing_file = ReceiptFileRepository.get_by_file_name(filename)
        
        if existing_file and existing_file['is_processed']:
            return {
                'filename': filename,
                'status': 'skipped',
                'reason': 'Already processed',
                'file_id': existing_file['id']
            }
        
        try:
            # Create or update file record
            if existing_file:
                file_id = existing_file['id']
                # Update file path if different
                if existing_file['file_path'] != file_path:
                    ReceiptFileRepository.update_validation(file_id, False, None)
            else:
                # Create new file record
                file_record = ReceiptFileRepository.create(filename, file_path)
                file_id = file_record['id']
            
            # Validate PDF
            is_valid, validation_message = self.file_service.validate_file(file_id)
            
            if not is_valid:
                return {
                    'filename': filename,
                    'status': 'failed',
                    'error': f'Invalid PDF: {validation_message}',
                    'file_id': file_id
                }
            
            # Process with LLM extraction
            success, receipt_data, error = self.file_service.process_file(file_id)
            
            if success:
                return {
                    'filename': filename,
                    'status': 'processed',
                    'file_id': file_id,
                    'receipt_id': receipt_data['id'] if receipt_data else None,
                    'merchant_name': receipt_data.get('merchant_name') if receipt_data else None,
                    'total_amount': receipt_data.get('total_amount') if receipt_data else None,
                    'year': pdf_info['year'],
                    'category': pdf_info['category']
                }
            else:
                return {
                    'filename': filename,
                    'status': 'failed',
                    'error': error,
                    'file_id': file_id
                }
                
        except Exception as e:
            logger.error(f"Processing error for {filename}: {str(e)}")
            return {
                'filename': filename,
                'status': 'failed',
                'error': str(e)
            }
    
    def get_processing_stats(self) -> Dict[str, Any]:
        """Get statistics about processed files"""
        
        # Get all files from database
        all_files = ReceiptFileRepository.get_all()
        all_receipts = ReceiptRepository.get_all()
        
        stats = {
            'total_files_in_db': len(all_files),
            'valid_files': len([f for f in all_files if f['is_valid']]),
            'processed_files': len([f for f in all_files if f['is_processed']]),
            'total_receipts': len(all_receipts),
            'files_by_year': {},
            'receipts_by_merchant': {}
        }
        
        # Count receipts by merchant
        for receipt in all_receipts:
            merchant = receipt.get('merchant_name', 'Unknown')
            stats['receipts_by_merchant'][merchant] = stats['receipts_by_merchant'].get(merchant, 0) + 1
        
        return stats
    
    def process_uploaded_files(self, files) -> Dict[str, Any]:
        """
        Process multiple uploaded PDF files
        Returns summary of processing results
        """
        from werkzeug.utils import secure_filename
        import os
        
        results = {
            'total_files': len(files),
            'processed': 0,
            'failed': 0,
            'skipped': 0,
            'details': []
        }
        
        logger.info(f"Processing {len(files)} uploaded files")
        
        for file in files:
            try:
                # Skip empty files
                if file.filename == '':
                    continue
                
                filename = secure_filename(file.filename)
                
                # Check if file already exists in database
                existing_file = ReceiptFileRepository.get_by_file_name(filename)
                
                if existing_file and existing_file['is_processed']:
                    results['skipped'] += 1
                    results['details'].append({
                        'filename': filename,
                        'status': 'skipped',
                        'reason': 'Already processed',
                        'file_id': existing_file['id']
                    })
                    continue
                
                # Save uploaded file
                upload_result = self.file_service.save_uploaded_file(file)
                if not upload_result['success']:
                    results['failed'] += 1
                    results['details'].append({
                        'filename': filename,
                        'status': 'failed',
                        'error': upload_result['error']
                    })
                    continue
                
                file_id = upload_result['file_id']
                
                # Validate PDF
                is_valid, validation_message = self.file_service.validate_file(file_id)
                
                if not is_valid:
                    results['failed'] += 1
                    results['details'].append({
                        'filename': filename,
                        'status': 'failed',
                        'error': f'Invalid PDF: {validation_message}',
                        'file_id': file_id
                    })
                    continue
                
                # Process with LLM extraction
                success, receipt_data, error = self.file_service.process_file(file_id)
                
                if success:
                    results['processed'] += 1
                    results['details'].append({
                        'filename': filename,
                        'status': 'processed',
                        'file_id': file_id,
                        'receipt_id': receipt_data['id'] if receipt_data else None,
                        'merchant_name': receipt_data.get('merchant_name') if receipt_data else None,
                        'total_amount': receipt_data.get('total_amount') if receipt_data else None
                    })
                else:
                    results['failed'] += 1
                    results['details'].append({
                        'filename': filename,
                        'status': 'failed',
                        'error': error,
                        'file_id': file_id
                    })
                    
            except Exception as e:
                logger.error(f"Error processing uploaded file {file.filename}: {str(e)}")
                results['failed'] += 1
                results['details'].append({
                    'filename': file.filename,
                    'status': 'failed',
                    'error': str(e)
                })
        
        return results
