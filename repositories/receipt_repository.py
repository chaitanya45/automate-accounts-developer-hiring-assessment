import sqlite3
from typing import List, Optional, Dict, Any
from config.database import get_db_connection
import uuid
from datetime import datetime

class ReceiptRepository:
    
    @staticmethod
    def create(file_id: str, file_path: str, **kwargs) -> Dict[str, Any]:
        """Create a new receipt record"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if receipt already exists for this file
        existing = cursor.execute(
            'SELECT id FROM receipt WHERE file_id = ?', 
            (file_id,)
        ).fetchone()
        
        if existing:
            # Update existing receipt
            receipt_id = existing['id']
            update_fields = []
            update_values = []
            
            for key, value in kwargs.items():
                if key in ['purchased_at', 'merchant_name', 'total_amount', 'tax_amount', 
                          'subtotal', 'payment_method', 'raw_text']:
                    update_fields.append(f"{key} = ?")
                    update_values.append(value)
            
            if update_fields:
                update_values.append(receipt_id)
                cursor.execute(
                    f'''UPDATE receipt 
                        SET {', '.join(update_fields)}, updated_at = CURRENT_TIMESTAMP 
                        WHERE id = ?''',
                    update_values
                )
                conn.commit()
            
            # Get updated record
            result = cursor.execute(
                'SELECT * FROM receipt WHERE id = ?', 
                (receipt_id,)
            ).fetchone()
        else:
            # Create new receipt
            receipt_id = str(uuid.uuid4())
            cursor.execute(
                '''INSERT INTO receipt 
                   (id, file_id, purchased_at, merchant_name, total_amount, file_path, created_at, updated_at)
                   VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)''',
                (receipt_id, file_id, kwargs.get('purchased_at'), 
                 kwargs.get('merchant_name'), kwargs.get('total_amount'), file_path)
            )
            conn.commit()
            
            # Get created record
            result = cursor.execute(
                'SELECT * FROM receipt WHERE id = ?', 
                (receipt_id,)
            ).fetchone()
        
        conn.close()
        return dict(result) if result else None
    
    @staticmethod
    def get_by_id(receipt_id: str) -> Optional[Dict[str, Any]]:
        """Get receipt by ID"""
        conn = get_db_connection()
        result = conn.execute(
            'SELECT * FROM receipt WHERE id = ?', 
            (receipt_id,)
        ).fetchone()
        conn.close()
        return dict(result) if result else None
    
    @staticmethod
    def get_by_file_id(file_id: str) -> Optional[Dict[str, Any]]:
        """Get receipt by file ID"""
        conn = get_db_connection()
        result = conn.execute(
            'SELECT * FROM receipt WHERE file_id = ?', 
            (file_id,)
        ).fetchone()
        conn.close()
        return dict(result) if result else None
    
    @staticmethod
    def get_all() -> List[Dict[str, Any]]:
        """Get all receipts"""
        conn = get_db_connection()
        results = conn.execute('SELECT * FROM receipt ORDER BY created_at DESC').fetchall()
        conn.close()
        return [dict(row) for row in results]
    
    @staticmethod
    def update(receipt_id: str, **kwargs) -> Optional[Dict[str, Any]]:
        """Update receipt data"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        update_fields = []
        update_values = []
        
        for key, value in kwargs.items():
            if key in ['purchased_at', 'merchant_name', 'total_amount', 'tax_amount', 
                      'subtotal', 'payment_method', 'raw_text', 'file_path']:
                update_fields.append(f"{key} = ?")
                update_values.append(value)
        
        if update_fields:
            update_values.append(receipt_id)
            cursor.execute(
                f'''UPDATE receipt 
                    SET {', '.join(update_fields)}, updated_at = CURRENT_TIMESTAMP 
                    WHERE id = ?''',
                update_values
            )
            conn.commit()
        
        # Get updated record
        result = cursor.execute(
            'SELECT * FROM receipt WHERE id = ?', 
            (receipt_id,)
        ).fetchone()
        conn.close()
        return dict(result) if result else None
    
    @staticmethod
    def delete(receipt_id: str) -> bool:
        """Delete receipt"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM receipt WHERE id = ?', (receipt_id,))
        deleted_count = cursor.rowcount
        conn.commit()
        conn.close()
        
        return deleted_count > 0
    
    @staticmethod
    def get_by_merchant(merchant_name: str) -> List[Dict[str, Any]]:
        """Get receipts by merchant name"""
        conn = get_db_connection()
        results = conn.execute(
            'SELECT * FROM receipt WHERE merchant_name LIKE ? ORDER BY created_at DESC',
            (f'%{merchant_name}%',)
        ).fetchall()
        conn.close()
        return [dict(row) for row in results]
