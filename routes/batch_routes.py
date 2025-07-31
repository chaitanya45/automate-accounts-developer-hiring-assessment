from flask import Blueprint
from controllers.batch_controller import BatchController

batch_bp = Blueprint('batch', __name__)
batch_controller = BatchController()

@batch_bp.route('/batch/discover', methods=['GET'])
def discover_files():
    """Discover all PDF files in directory structure"""
    return batch_controller.discover_files()

@batch_bp.route('/batch/process', methods=['POST'])
def process_all_files():
    """Process all discovered PDF files with OCR"""
    return batch_controller.process_all_files()

@batch_bp.route('/batch/stats', methods=['GET'])
def get_stats():
    """Get processing statistics"""
    return batch_controller.get_stats()
