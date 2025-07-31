#!/usr/bin/env python3

import sys
sys.path.append('.')
from services.ocr_service import OCRService

# Use the actual extracted text from the database
actual_text = """THE VENETIAN* THE PALAZZO
LAS VEGAS
3355 Las Vegas Blvd. So.
Las Vegas, NV 89109
PAYMENTS/
CREDITS! )DATE REFERENCE NO.DESCRIPTION CHARGES BALANCE
11/25/18 434289101289 RESORT FEE
RESORT FEE-$20 PIUS TAX
ROOM CHARGE UPGRADE VEN
UPGRADE CHARGE - ADDITION
ROOM CHARGE VE33310
ΤΑΧ2
APPLIED DEPOSIT
1,937.66
VE 33310 Suite#:
KVType:
Guests:JENS WALTER
1
FRIEDRICHSIR. 123
BERLIN432340865678 Res#:
1011711/25/2018 Arrival:
Departure:
cc*12/02/2018
Folio Type:
Folio ID:
Page#:5
'5052
434280912998
01
FOLIOIIP
Your Account Statement:
It has been our pleasure serving you,
and we hope you will think of US as your
home in las Vegas on a future visit.
For reservations call: 1.888.283.6423
FOLlOBALANCE 00
TOTALBlLLEDTOSUITE
TOTALDEPS/PYMTS/CRDTS FS;]
"""

# Test the OCR service with actual text
ocr_service = OCRService()
result = ocr_service.extract_receipt_data(actual_text)

print("=== OCR EXTRACTION RESULTS WITH ACTUAL TEXT ===")
for key, value in result.items():
    if key != 'raw_text':  # Skip raw text for cleaner output
        print(f"{key}: {value}")
        
print(f"\nNote: Based on the PDF image you shared, the correct total should be 2,174.62")
print(f"The extracted text appears to be missing the final total page or has OCR issues.")
