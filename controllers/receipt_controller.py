from flask import jsonify, request
from repositories.receipt_repository import ReceiptRepository
from repositories.receipt_file_repository import ReceiptFileRepository
import logging

logger = logging.getLogger(__name__)

class ReceiptController:
    
    def get_all_receipts(self):
        """Get all receipts endpoint"""
        try:
            receipts = ReceiptRepository.get_all()
            
            return jsonify({
                'receipts': receipts,
                'total': len(receipts)
            }), 200
            
        except Exception as e:
            logger.error(f"Get receipts error: {str(e)}")
            return jsonify({'error': 'Internal server error'}), 500
    
    def get_receipt_by_id(self, receipt_id):
        """Get specific receipt by ID endpoint"""
        try:
            receipt = ReceiptRepository.get_by_id(receipt_id)
            
            if not receipt:
                return jsonify({'error': 'Receipt not found'}), 404
            
            # Get associated file information
            receipt_file = ReceiptFileRepository.get_by_id(receipt['file_id'])
            
            if receipt_file:
                receipt['file_info'] = receipt_file
            
            return jsonify({'receipt': receipt}), 200
            
        except Exception as e:
            logger.error(f"Get receipt error: {str(e)}")
            return jsonify({'error': 'Internal server error'}), 500
    
    def update_receipt(self, receipt_id):
        """Update receipt endpoint"""
        try:
            data = request.get_json()
            
            if not data:
                return jsonify({'error': 'No data provided'}), 400
            
            receipt = ReceiptRepository.update(receipt_id, **data)
            
            if not receipt:
                return jsonify({'error': 'Receipt not found'}), 404
            
            return jsonify({
                'message': 'Receipt updated successfully',
                'receipt': receipt
            }), 200
            
        except Exception as e:
            logger.error(f"Update receipt error: {str(e)}")
            return jsonify({'error': 'Internal server error'}), 500
    
    def delete_receipt(self, receipt_id):
        """Delete receipt endpoint"""
        try:
            success = ReceiptRepository.delete(receipt_id)
            
            if not success:
                return jsonify({'error': 'Receipt not found'}), 404
            
            return jsonify({'message': 'Receipt deleted successfully'}), 200
            
        except Exception as e:
            logger.error(f"Delete receipt error: {str(e)}")
            return jsonify({'error': 'Internal server error'}), 500
    
    def get_receipts_by_merchant(self):
        """Get receipts by merchant name endpoint"""
        try:
            merchant_name = request.args.get('merchant_name')
            
            if not merchant_name:
                return jsonify({'error': 'merchant_name parameter is required'}), 400
            
            receipts = ReceiptRepository.get_by_merchant(merchant_name)
            
            return jsonify({
                'receipts': receipts,
                'total': len(receipts),
                'merchant_name': merchant_name
            }), 200
            
        except Exception as e:
            logger.error(f"Get receipts by merchant error: {str(e)}")
            return jsonify({'error': 'Internal server error'}), 500
