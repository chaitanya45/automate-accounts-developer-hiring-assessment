from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import uuid

db = SQLAlchemy()

class Receipt(db.Model):
    __tablename__ = 'receipt'
    
    id = db.Column(db.String, primary_key=True, default=lambda: str(uuid.uuid4()))
    purchased_at = db.Column(db.DateTime, nullable=True)
    merchant_name = db.Column(db.String(255), nullable=True)
    total_amount = db.Column(db.Numeric(10, 2), nullable=True)
    file_path = db.Column(db.String(500), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Foreign key to receipt_file
    file_id = db.Column(db.String, db.ForeignKey('receipt_file.id'), nullable=False)
    
    # Additional fields for enhanced extraction
    tax_amount = db.Column(db.Numeric(10, 2), nullable=True)
    subtotal = db.Column(db.Numeric(10, 2), nullable=True)
    payment_method = db.Column(db.String(100), nullable=True)
    raw_text = db.Column(db.Text, nullable=True)  # Store raw OCR text
    
    def to_dict(self):
        return {
            'id': self.id,
            'purchased_at': self.purchased_at.isoformat() if self.purchased_at else None,
            'merchant_name': self.merchant_name,
            'total_amount': float(self.total_amount) if self.total_amount else None,
            'tax_amount': float(self.tax_amount) if self.tax_amount else None,
            'subtotal': float(self.subtotal) if self.subtotal else None,
            'payment_method': self.payment_method,
            'file_path': self.file_path,
            'file_id': self.file_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        return f'<Receipt {self.merchant_name} - {self.total_amount}>'
