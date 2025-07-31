#!/usr/bin/env python3
"""
Test the complete OCR + LLM fallback system by reprocessing the actual receipt
"""

import sys
import os
sys.path.append('.')

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

from flask import Flask
from config.config import Config
from services.file_processing_service import FileProcessingService

def test_complete_system():
    print("=== Testing Complete OCR + LLM Fallback System ===\n")
    
    # Create Flask app context
    app = Flask(__name__)
    app.config.from_object(Config)
    
    with app.app_context():
        # Initialize the file processing service
        processing_service = FileProcessingService(
            upload_folder=app.config['UPLOAD_FOLDER']
        )
        
        # Get the existing file ID from database
        from config.database import get_db_connection
        conn = get_db_connection()
        cursor = conn.cursor()
        receipt = cursor.execute('SELECT file_id FROM receipt LIMIT 1').fetchone()
        
        if receipt:
            file_id = receipt['file_id']
            print(f"Processing file: {file_id}")
            print("Note: OCR will try first, then LLM fallback if OCR extraction quality is poor")
            
            # Process the file with the new hybrid system
            success, receipt_data, error = processing_service.process_file(file_id)
            
            if success:
                print("\n✅ File processed successfully!")
                print(f"Extraction Method: {receipt_data.get('extraction_method', 'Unknown')}")
                print(f"Merchant: {receipt_data.get('merchant_name')}")
                print(f"Total Amount: ${receipt_data.get('total_amount')}")
                print(f"Purchase Date: {receipt_data.get('purchased_at')}")
                print(f"Payment Method: {receipt_data.get('payment_method')}")
                
                print("\n🔍 Analysis:")
                method = receipt_data.get('extraction_method', 'OCR')
                if method == 'OCR':
                    print("   - OCR extraction was successful")
                elif method == 'LLM_Text':
                    print("   - OCR failed, LLM text extraction was used")
                elif method == 'LLM_Vision':
                    print("   - OCR and LLM text failed, LLM vision was used")
                elif method == 'OCR_Failed':
                    print("   - All extraction methods failed, using OCR data as fallback")
                    
            else:
                print(f"❌ Error processing file: {error}")
        else:
            print("No receipts found in database")
        
        conn.close()

    print("\n💡 System Features:")
    print("   1. OCR extraction tries first (fast and cost-effective)")
    print("   2. If OCR quality is poor, LLM analyzes the text")
    print("   3. If LLM text fails, LLM vision analyzes receipt image")
    print("   4. Graceful fallback ensures data is always extracted")
    print("\n🔧 Configuration:")
    print(f"   - Gemini API: {'✅ Configured' if os.getenv('GEMINI_API_KEY') else '❌ Not configured'}")
    print(f"   - OpenAI API: {'✅ Configured' if os.getenv('OPENAI_API_KEY') else '❌ Not configured'}")
    print(f"   - Claude API: {'✅ Configured' if os.getenv('CLAUDE_API_KEY') else '❌ Not configured'}")

if __name__ == "__main__":
    test_complete_system()
