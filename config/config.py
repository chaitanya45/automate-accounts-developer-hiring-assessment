import os
from datetime import timedelta

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///receipts.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # File upload settings
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'uploads', 'receipts')
    MAX_CONTENT_LENGTH = int(os.environ.get('MAX_CONTENT_LENGTH', 16 * 1024 * 1024))  # 16MB max file size
    ALLOWED_EXTENSIONS = {'pdf'}
    
    # OCR settings
    TESSERACT_CMD = os.environ.get('TESSERACT_CMD') or r'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'
    
    # LLM API Keys (set these as environment variables for security)
    OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
    GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')
    CLAUDE_API_KEY = os.environ.get('CLAUDE_API_KEY')
    GOOGLE_VISION_API_KEY = os.environ.get('GOOLGE_VISION_API_KEY')
    
    # API settings
    JSONIFY_PRETTYPRINT_REGULAR = True
