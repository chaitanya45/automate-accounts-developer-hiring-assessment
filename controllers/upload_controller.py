from flask import request, jsonify, current_app
from services.file_processing_service import FileProcessingService
from repositories.receipt_file_repository import ReceiptFileRepository
import logging

logger = logging.getLogger(__name__)

class UploadController:
    
    def __init__(self):
        self.file_service = None
    
    def _get_file_service(self):
        """Get file processing service instance"""
        if self.file_service is None:
            self.file_service = FileProcessingService(
                current_app.config['UPLOAD_FOLDER'],
                current_app.config.get('TESSERACT_CMD')
            )
        return self.file_service
    
    def upload_file(self):
        """Upload receipt file endpoint"""
        try:
            # Check if file is in request
            if 'file' not in request.files:
                return jsonify({'error': 'No file provided'}), 400
            
            file = request.files['file']
            
            # Check if file is selected
            if file.filename == '':
                return jsonify({'error': 'No file selected'}), 400
            
            file_service = self._get_file_service()
            
            # Check if file type is allowed
            if not file_service.allowed_file(file.filename):
                return jsonify({'error': 'Only PDF files are allowed'}), 400
            
            # Save file
            file_id, file_path, error = file_service.save_uploaded_file(file)
            
            if error:
                return jsonify({'error': f'File upload failed: {error}'}), 500
            
            # Get file record
            receipt_file = ReceiptFileRepository.get_by_id(file_id)
            
            return jsonify({
                'message': 'File uploaded successfully',
                'file': receipt_file
            }), 201
            
        except Exception as e:
            logger.error(f"Upload error: {str(e)}")
            return jsonify({'error': 'Internal server error'}), 500
    
    def validate_file(self):
        """Validate PDF file endpoint"""
        try:
            data = request.get_json()
            
            if not data or 'file_id' not in data:
                return jsonify({'error': 'file_id is required'}), 400
            
            file_id = data['file_id']
            file_service = self._get_file_service()
            
            # Get file record to get the file path
            receipt_file = ReceiptFileRepository.get_by_id(file_id)
            if not receipt_file:
                return jsonify({'error': 'File not found'}), 404
            
            # Validate file using file path, not file ID
            is_valid, message = file_service.validate_file(receipt_file['file_path'])
            
            # Update the file record with validation results
            ReceiptFileRepository.update_validation(file_id, is_valid, message if not is_valid else None)
            
            # Get updated file record
            updated_receipt_file = ReceiptFileRepository.get_by_id(file_id)
            
            return jsonify({
                'message': message,
                'is_valid': is_valid,
                'file': updated_receipt_file
            }), 200
            
        except Exception as e:
            logger.error(f"Validation error: {str(e)}")
            return jsonify({'error': 'Internal server error'}), 500
    
    def process_file(self):
        """Process file with OCR endpoint"""
        try:
            data = request.get_json()
            
            if not data or 'file_id' not in data:
                return jsonify({'error': 'file_id is required'}), 400
            
            file_id = data['file_id']
            file_service = self._get_file_service()
            
            # Process file
            success, receipt_data, error = file_service.process_file(file_id)
            
            if not success:
                return jsonify({'error': f'Processing failed: {error}'}), 400
            
            return jsonify({
                'message': 'File processed successfully',
                'receipt': receipt_data
            }), 200
            
        except Exception as e:
            logger.error(f"Processing error: {str(e)}")
            return jsonify({'error': 'Internal server error'}), 500
