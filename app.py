from flask import Flask
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

def create_app():
    app = Flask(__name__)
    
    # Load configuration
    from config.config import Config
    app.config.from_object(Config)
    
    # Create upload directory
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    # Register blueprints
    from routes.receipt_routes import receipt_bp
    from routes.upload_routes import upload_bp
    from routes.batch_routes import batch_bp
    
    app.register_blueprint(receipt_bp, url_prefix='/api')
    app.register_blueprint(upload_bp, url_prefix='/api')
    app.register_blueprint(batch_bp, url_prefix='/api')
    
    # Error handlers
    from middleware.error_handler import register_error_handlers
    register_error_handlers(app)
    
    # Setup logging
    from utils.logger import setup_logger
    setup_logger()
    
    @app.route('/')
    def index():
        return {
            'message': 'Receipt Processing API',
            'version': '1.0.0',
            'endpoints': {
                'upload': '/api/upload',
                'validate': '/api/validate', 
                'process': '/api/process',
                'receipts': '/api/receipts',
                'receipt_by_id': '/api/receipts/{id}',
                'batch_discover': '/api/batch/discover',
                'batch_process': '/api/batch/process',
                'batch_stats': '/api/batch/stats'
            }
        }
    
    @app.route('/health')
    def health():
        return {'status': 'healthy'}
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)
