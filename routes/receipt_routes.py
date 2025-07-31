from flask import Blueprint, request
from controllers.receipt_controller import ReceiptController

receipt_bp = Blueprint('receipts', __name__)
receipt_controller = ReceiptController()

@receipt_bp.route('/receipts', methods=['GET'])
def get_receipts():
    """Get all receipts or filter by merchant"""
    if 'merchant_name' in request.args:
        return receipt_controller.get_receipts_by_merchant()
    return receipt_controller.get_all_receipts()

@receipt_bp.route('/receipts/<string:receipt_id>', methods=['GET'])
def get_receipt(receipt_id):
    """Get specific receipt"""
    return receipt_controller.get_receipt_by_id(receipt_id)

@receipt_bp.route('/receipts/<string:receipt_id>', methods=['PUT'])
def update_receipt(receipt_id):
    """Update receipt"""
    return receipt_controller.update_receipt(receipt_id)

@receipt_bp.route('/receipts/<string:receipt_id>', methods=['DELETE'])
def delete_receipt(receipt_id):
    """Delete receipt"""
    return receipt_controller.delete_receipt(receipt_id)
