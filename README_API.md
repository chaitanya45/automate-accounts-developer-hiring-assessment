# Receipt Processing API

A Flask-based web application for processing scanned receipts using OCR/AI techniques to extract key information and store it in a structured database.

## 🚀 Features

- **PDF Upload**: Upload scanned receipt files in PDF format
- **PDF Validation**: Validate uploaded files to ensure they are valid PDFs
- **OCR Processing**: Extract text and key details using Tesseract OCR
- **Data Extraction**: Parse merchant name, total amount, tax, date, and payment method
- **REST API**: Full CRUD operations for receipts and files
- **Database Storage**: SQLite database with structured schema
- **Error Handling**: Comprehensive error handling and validation

## 📁 Project Structure

```
C:\Pdf extraction zoho project\automate-accounts-developer-hiring-assessment\
├── app.py                          # Main Flask application
├── run.py                          # Application runner
├── requirements.txt                # Python dependencies
├── .env                           # Environment variables
├── .env.example                   # Environment template
├── receipts.db                    # SQLite database
├── config/
│   ├── __init__.py
│   ├── config.py                  # Application configuration
│   └── database.py                # Database utilities
├── models/
│   ├── __init__.py
│   ├── receipt.py                 # Receipt model
│   └── receipt_file.py            # ReceiptFile model
├── repositories/
│   ├── __init__.py
│   ├── base_repository.py         # Base repository pattern
│   ├── receipt_repository.py      # Receipt data access
│   └── receipt_file_repository.py # ReceiptFile data access
├── services/
│   ├── __init__.py
│   ├── ocr_service.py             # OCR text extraction
│   ├── pdf_validation_service.py  # PDF validation
│   └── file_processing_service.py # File processing workflow
├── controllers/
│   ├── __init__.py
│   ├── receipt_controller.py      # Receipt endpoints
│   └── upload_controller.py       # Upload endpoints
├── routes/
│   ├── __init__.py
│   ├── receipt_routes.py          # Receipt API routes
│   └── upload_routes.py           # Upload API routes
├── middleware/
│   ├── __init__.py
│   └── error_handler.py           # Error handling middleware
├── utils/
│   ├── __init__.py
│   ├── logger.py                  # Logging utilities
│   └── helpers.py                 # Helper functions
├── uploads/
│   └── receipts/                  # Uploaded files storage
└── tests/
    ├── __init__.py
    └── test_models.py             # Unit tests
```

## 🛠 Technology Stack

- **Backend**: Python 3.8+ with Flask
- **Database**: SQLite with raw SQL queries
- **OCR**: Tesseract OCR with pytesseract
- **PDF Processing**: PyPDF2 and pdf2image
- **Image Processing**: OpenCV and Pillow
- **File Upload**: Werkzeug
- **Testing**: pytest
- **Environment**: python-dotenv

## 📋 **Prerequisites**

1. **Python 3.8+**
2. **Tesseract OCR** - Download and install from: https://github.com/UB-Mannheim/tesseract/wiki
   - Default installation path: `C:\Program Files\Tesseract-OCR\tesseract.exe`
3. **Poppler** (for pdf2image) - Download from: https://poppler.freedesktop.org/

## 🚀 **Quick Start**

### **Option 1: Complete Setup (Recommended)**

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Start the server
python run.py

# 3. In another terminal, run setup to process existing PDFs
python setup.py setup
```

### **Option 2: Manual Setup**

### 1. Install Dependencies

```bash
# Install Python dependencies
pip install -r requirements.txt
```

### 2. Configure Environment

Copy `.env.example` to `.env` and update the Tesseract path if needed:

```bash
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///receipts.db
TESSERACT_CMD=C:\Program Files\Tesseract-OCR\tesseract.exe
FLASK_ENV=development
FLASK_DEBUG=True
UPLOAD_FOLDER=uploads/receipts
MAX_CONTENT_LENGTH=16777216
```

### 3. Run the Application

```bash
python run.py
```

The application will be available at: http://localhost:5000

## 📚 API Documentation

### Base URL
```
http://localhost:5000/api
```

### Endpoints

#### 1. Upload Receipt File
```http
POST /api/upload
Content-Type: multipart/form-data

Form Data:
- file: (PDF file)
```

**Response:**
```json
{
  "message": "File uploaded successfully",
  "file": {
    "id": "uuid",
    "file_name": "receipt.pdf",
    "file_path": "uploads/receipts/receipt.pdf",
    "is_valid": false,
    "is_processed": false,
    "created_at": "2024-01-01T00:00:00",
    "updated_at": "2024-01-01T00:00:00"
  }
}
```

#### 2. Validate PDF File
```http
POST /api/validate
Content-Type: application/json

{
  "file_id": "uuid"
}
```

**Response:**
```json
{
  "message": "Valid PDF",
  "is_valid": true,
  "file": {
    "id": "uuid",
    "is_valid": true,
    "invalid_reason": null
  }
}
```

#### 3. Process File with OCR
```http
POST /api/process
Content-Type: application/json

{
  "file_id": "uuid"
}
```

**Response:**
```json
{
  "message": "File processed successfully",
  "receipt": {
    "id": "uuid",
    "merchant_name": "Target",
    "total_amount": 25.99,
    "tax_amount": 2.34,
    "purchased_at": "2024-01-01T12:00:00",
    "payment_method": "Credit",
    "file_id": "uuid",
    "created_at": "2024-01-01T00:00:00"
  }
}
```

#### 4. Get All Receipts
```http
GET /api/receipts
```

**Response:**
```json
{
  "receipts": [...],
  "total": 10
}
```

#### 5. Get Receipt by ID
```http
GET /api/receipts/{receipt_id}
```

**Response:**
```json
{
  "receipt": {
    "id": "uuid",
    "merchant_name": "Target",
    "total_amount": 25.99,
    "file_info": {
      "file_name": "receipt.pdf",
      "file_path": "uploads/receipts/receipt.pdf"
    }
  }
}
```

#### 6. Update Receipt
```http
PUT /api/receipts/{receipt_id}
Content-Type: application/json

{
  "merchant_name": "Updated Store Name",
  "total_amount": 30.00
}
```

#### 7. Delete Receipt
```http
DELETE /api/receipts/{receipt_id}
```

#### 8. Filter by Merchant
```http
GET /api/receipts?merchant_name=Target
```

#### 9. Discover Existing PDF Files
```http
GET /api/batch/discover
```

**Response:**
```json
{
  "message": "Found 150 PDF files",
  "total_files": 150,
  "files": [
    {
      "file_path": "C:\\...\\2021\\bestbuy_20211211_006.pdf",
      "filename": "bestbuy_20211211_006.pdf",
      "year": "2021",
      "category": "retail",
      "relative_path": "2021\\bestbuy_20211211_006.pdf"
    }
  ]
}
```

#### 10. Process All Existing PDFs
```http
POST /api/batch/process
```

**Response:**
```json
{
  "message": "Batch processing completed",
  "summary": {
    "total_files": 150,
    "processed": 120,
    "failed": 15,
    "skipped": 15
  },
  "details": [
    {
      "filename": "bestbuy_20211211_006.pdf",
      "status": "processed",
      "file_id": "uuid",
      "receipt_id": "uuid",
      "merchant_name": "Best Buy",
      "total_amount": 299.99,
      "year": "2021",
      "category": "retail"
    }
  ]
}
```

#### 11. Get Processing Statistics
```http
GET /api/batch/stats
```

**Response:**
```json
{
  "statistics": {
    "total_files_in_db": 150,
    "valid_files": 135,
    "processed_files": 120,
    "total_receipts": 120,
    "receipts_by_merchant": {
      "Best Buy": 25,
      "Target": 30,
      "CVS": 15
    }
  }
}
```

## 🗄️ Database Schema

The application uses SQLite with the existing schema:

### receipt_file table
- `id` (TEXT, PRIMARY KEY) - UUID
- `file_name` (TEXT) - Original filename
- `file_path` (TEXT) - Storage path
- `is_valid` (BOOLEAN) - PDF validation status
- `invalid_reason` (TEXT) - Validation error message
- `is_processed` (BOOLEAN) - Processing status
- `created_at` (TIMESTAMP) - Creation time
- `updated_at` (TIMESTAMP) - Last update time

### receipt table
- `id` (TEXT, PRIMARY KEY) - UUID
- `file_id` (TEXT, FOREIGN KEY) - Reference to receipt_file
- `purchased_at` (TIMESTAMP) - Purchase date/time
- `merchant_name` (TEXT) - Store/merchant name
- `total_amount` (DECIMAL) - Total amount
- `file_path` (TEXT) - PDF file path
- `created_at` (TIMESTAMP) - Creation time
- `updated_at` (TIMESTAMP) - Last update time

## 🧪 Testing

Run tests using pytest:

```bash
pytest tests/
```

## 📝 Usage Examples

### 1. Complete Workflow Example

```bash
# 1. Upload a PDF file
curl -X POST -F "file=@receipt.pdf" http://localhost:5000/api/upload

# 2. Validate the uploaded file
curl -X POST -H "Content-Type: application/json" \
     -d '{"file_id":"your-file-id"}' \
     http://localhost:5000/api/validate

# 3. Process with OCR
curl -X POST -H "Content-Type: application/json" \
     -d '{"file_id":"your-file-id"}' \
     http://localhost:5000/api/process

# 4. Get all receipts
curl http://localhost:5000/api/receipts
```

### 2. Python Script Example

```python
import requests

# Upload file
with open('receipt.pdf', 'rb') as f:
    response = requests.post('http://localhost:5000/api/upload', 
                           files={'file': f})
    file_data = response.json()

file_id = file_data['file']['id']

# Validate
requests.post('http://localhost:5000/api/validate', 
              json={'file_id': file_id})

# Process
response = requests.post('http://localhost:5000/api/process', 
                        json={'file_id': file_id})
receipt_data = response.json()

print(f"Extracted: {receipt_data['receipt']['merchant_name']} - ${receipt_data['receipt']['total_amount']}")
```

### 3. Batch Processing Existing PDFs

```bash
# Start the server first
python run.py

# In another terminal, run complete setup
python setup.py setup

# Or run individual commands
python setup.py discover    # Discover all PDFs
python setup.py process     # Process all PDFs
python setup.py stats       # Get statistics
```

## 🔧 Configuration

### Environment Variables

- `SECRET_KEY`: Flask secret key for sessions
- `DATABASE_URL`: SQLite database connection string
- `TESSERACT_CMD`: Path to Tesseract executable
- `UPLOAD_FOLDER`: Directory for uploaded files
- `MAX_CONTENT_LENGTH`: Maximum file size (bytes)

### OCR Configuration

The OCR service uses Tesseract with preprocessing:
- Grayscale conversion
- Noise reduction
- Threshold application for better text recognition

## 🚨 Error Handling

The application includes comprehensive error handling:

- **400**: Bad request (missing parameters, invalid data)
- **404**: Resource not found
- **413**: File too large
- **500**: Internal server error

All errors return JSON responses with descriptive messages.

## 📊 Logging

Logs are written to both console and `app.log` file with timestamps and log levels.

## 🤝 Contributing

1. Follow the existing code structure
2. Add tests for new features
3. Update documentation
4. Follow Python PEP 8 style guidelines

## 📄 License

This project is created for the Automate Accounts Developer Hiring Assessment.

## 🎯 Future Enhancements

- Add user authentication
- Implement receipt categorization
- Add support for more file formats
- Implement batch processing
- Add data export functionality
- Integrate with cloud storage
- Add receipt duplicate detection
- Implement advanced OCR with Azure Computer Vision
