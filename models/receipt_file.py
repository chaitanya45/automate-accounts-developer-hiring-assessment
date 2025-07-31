from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import uuid

db = SQLAlchemy()

class ReceiptFile(db.Model):
    __tablename__ = 'receipt_file'
    
    id = db.Column(db.String, primary_key=True, default=lambda: str(uuid.uuid4()))
    file_name = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(500), nullable=False)
    is_valid = db.Column(db.Boolean, default=False, nullable=False)
    invalid_reason = db.Column(db.Text, nullable=True)
    is_processed = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationship with receipt
    receipt = db.relationship('Receipt', backref='file', uselist=False, cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'file_name': self.file_name,
            'file_path': self.file_path,
            'is_valid': self.is_valid,
            'invalid_reason': self.invalid_reason,
            'is_processed': self.is_processed,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        return f'<ReceiptFile {self.file_name}>'
