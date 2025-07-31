from flask import Blueprint
from controllers.upload_controller import UploadController

upload_bp = Blueprint('upload', __name__)
upload_controller = UploadController()

@upload_bp.route('/upload', methods=['POST'])
def upload_file():
    """Upload receipt file"""
    return upload_controller.upload_file()

@upload_bp.route('/validate', methods=['POST'])
def validate_file():
    """Validate PDF file"""
    return upload_controller.validate_file()

@upload_bp.route('/process', methods=['POST'])
def process_file():
    """Process file with OCR"""
    return upload_controller.process_file()
