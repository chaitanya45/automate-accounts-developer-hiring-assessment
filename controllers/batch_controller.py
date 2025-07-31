from flask import jsonify, current_app
from services.batch_processing_service import BatchProcessingService
import logging
import os

logger = logging.getLogger(__name__)

class BatchController:
    """Controller for batch processing existing PDF files"""
    
    def __init__(self):
        self.batch_service = None
    
    def _get_batch_service(self):
        """Get batch processing service instance"""
        if self.batch_service is None:
            # Use the project root directory for discovering PDFs
            base_directory = os.path.dirname(os.path.dirname(__file__))
            self.batch_service = BatchProcessingService(
                base_directory,
                current_app.config.get('TESSERACT_CMD')
            )
        return self.batch_service
    
    def discover_files(self):
        """Discover all PDF files in directory structure"""
        try:
            batch_service = self._get_batch_service()
            pdf_files = batch_service.discover_pdf_files()
            
            return jsonify({
                'message': f'Found {len(pdf_files)} PDF files',
                'total_files': len(pdf_files),
                'files': pdf_files
            }), 200
            
        except Exception as e:
            logger.error(f"File discovery error: {str(e)}")
            return jsonify({'error': 'Failed to discover files'}), 500
    
    def process_all_files(self):
        """Process all discovered PDF files"""
        try:
            batch_service = self._get_batch_service()
            results = batch_service.process_all_pdfs()
            
            return jsonify({
                'message': 'Batch processing completed',
                'summary': {
                    'total_files': results['total_files'],
                    'processed': results['processed'],
                    'failed': results['failed'],
                    'skipped': results['skipped']
                },
                'details': results['details']
            }), 200
            
        except Exception as e:
            logger.error(f"Batch processing error: {str(e)}")
            return jsonify({'error': 'Batch processing failed'}), 500
    
    def get_stats(self):
        """Get processing statistics"""
        try:
            batch_service = self._get_batch_service()
            stats = batch_service.get_processing_stats()
            
            return jsonify({
                'statistics': stats
            }), 200
            
        except Exception as e:
            logger.error(f"Stats retrieval error: {str(e)}")
            return jsonify({'error': 'Failed to get statistics'}), 500
