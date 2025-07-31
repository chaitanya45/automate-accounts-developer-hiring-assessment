import logging
import sys
from datetime import datetime

def setup_logger(name: str = None, level: int = logging.INFO) -> logging.Logger:
    """Setup logger with console and file handlers"""
    
    # If no name provided, configure the root logger
    if name is None:
        logger = logging.getLogger()
    else:
        logger = logging.getLogger(name)
    
    logger.setLevel(level)
    
    # Remove all handlers before adding new ones to avoid duplicate logs
    if logger.hasHandlers():
        logger.handlers.clear()

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)

    # File handler
    file_handler = logging.FileHandler('app.log', mode='a', encoding='utf-8')
    file_handler.setLevel(level)

    # Formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    console_handler.setFormatter(formatter)
    file_handler.setFormatter(formatter)

    # Add handlers
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    
    # Also set up Flask's logger
    flask_logger = logging.getLogger('werkzeug')
    flask_logger.setLevel(level)
    if not flask_logger.hasHandlers():
        flask_logger.addHandler(console_handler)
        flask_logger.addHandler(file_handler)

    return logger
