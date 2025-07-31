#!/usr/bin/env python3
"""
Test LLM extraction with the actual problematic receipt text
"""

import sys
import os
sys.path.append('.')

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

def test_llm_extraction():
    print("=== Testing LLM Extraction with Real Receipt ===\n")
    
    # The actual problematic text from Venetian receipt
    venetian_text = """
THE VENETIAN* THE PALAZZO
LAS VEGAS
3355 Las Vegas Blvd. So.
Las Vegas, NV 89109
PAYMENTS/
CREDITS! )DATE REFERENCE NO.DESCRIPTION CHARGES BALANCE
11/25/18 434289101289 RESORT FEE
RESORT FEE-$20 PIUS TAX
1,937.66
FOLlOBALANCE 00
TOTALBlLLEDTOSUITE
TOTALDEPS/PYMTS/CRDTS FS;]
11/25/2018
12/02/2018
"""
    
    from services.llm_extraction_service import LLMExtractionService
    
    # Test LLM extraction directly
    llm_service = LLMExtractionService()
    
    print("Testing direct LLM extraction:")
    print("-" * 50)
    
    result = llm_service.extract_receipt_data_from_text(venetian_text)
    
    if result:
        print("✅ LLM extraction successful!")
        print(f"Merchant: {result.get('merchant_name')}")
        print(f"Total: ${result.get('total_amount')}")
        print(f"Date: {result.get('purchased_at')}")
        print(f"Payment: {result.get('payment_method')}")
        print(f"Tax: ${result.get('tax_amount')}")
        
        # Check if LLM found the correct total (should be 2174.62 based on the PDF image)
        if result.get('total_amount'):
            print(f"\n💡 Note: LLM extracted ${result.get('total_amount')}")
            print("   Expected from PDF image: $2,174.62")
            print("   OCR was only finding: $1,937.66 (from earlier in document)")
    else:
        print("❌ LLM extraction failed")
        
    print(f"\n🔧 Available providers: {_get_available_providers(llm_service)}")

def _get_available_providers(llm_service):
    providers = []
    if llm_service.openai_client:
        providers.append("OpenAI")
    if llm_service.gemini_client:
        providers.append("Gemini")
    if llm_service.claude_client:
        providers.append("Claude")
    return ", ".join(providers) if providers else "None"

if __name__ == "__main__":
    test_llm_extraction()
