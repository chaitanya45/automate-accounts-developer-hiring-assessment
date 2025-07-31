import sqlite3
from typing import List, Optional, Dict, Any
from config.database import get_db_connection
import uuid
from datetime import datetime

class ReceiptFileRepository:
    
    @staticmethod
    def create(file_name: str, file_path: str) -> Dict[str, Any]:
        """Create a new receipt file record"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check for existing file
        existing = cursor.execute(
            'SELECT id FROM receipt_file WHERE file_name = ?', 
            (file_name,)
        ).fetchone()
        
        if existing:
            # Update existing file
            cursor.execute(
                '''UPDATE receipt_file 
                   SET file_path = ?, updated_at = CURRENT_TIMESTAMP 
                   WHERE file_name = ?''',
                (file_path, file_name)
            )
            conn.commit()
            
            # Get updated record
            result = cursor.execute(
                'SELECT * FROM receipt_file WHERE file_name = ?', 
                (file_name,)
            ).fetchone()
        else:
            # Create new record
            file_id = str(uuid.uuid4())
            cursor.execute(
                '''INSERT INTO receipt_file 
                   (id, file_name, file_path, is_valid, is_processed, created_at, updated_at)
                   VALUES (?, ?, ?, FALSE, FALSE, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)''',
                (file_id, file_name, file_path)
            )
            conn.commit()
            
            # Get created record
            result = cursor.execute(
                'SELECT * FROM receipt_file WHERE id = ?', 
                (file_id,)
            ).fetchone()
        
        conn.close()
        return dict(result) if result else None
    
    @staticmethod
    def get_by_id(file_id: str) -> Optional[Dict[str, Any]]:
        """Get receipt file by ID"""
        conn = get_db_connection()
        result = conn.execute(
            'SELECT * FROM receipt_file WHERE id = ?', 
            (file_id,)
        ).fetchone()
        conn.close()
        return dict(result) if result else None
    
    @staticmethod
    def get_by_file_name(file_name: str) -> Optional[Dict[str, Any]]:
        """Get receipt file by file name"""
        conn = get_db_connection()
        result = conn.execute(
            'SELECT * FROM receipt_file WHERE file_name = ?', 
            (file_name,)
        ).fetchone()
        conn.close()
        return dict(result) if result else None
    
    @staticmethod
    def get_all() -> List[Dict[str, Any]]:
        """Get all receipt files"""
        conn = get_db_connection()
        results = conn.execute('SELECT * FROM receipt_file ORDER BY created_at DESC').fetchall()
        conn.close()
        return [dict(row) for row in results]
    
    @staticmethod
    def update_validation(file_id: str, is_valid: bool, invalid_reason: str = None) -> Optional[Dict[str, Any]]:
        """Update validation status"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            '''UPDATE receipt_file 
               SET is_valid = ?, invalid_reason = ?, updated_at = CURRENT_TIMESTAMP 
               WHERE id = ?''',
            (is_valid, invalid_reason, file_id)
        )
        conn.commit()
        
        # Get updated record
        result = cursor.execute(
            'SELECT * FROM receipt_file WHERE id = ?', 
            (file_id,)
        ).fetchone()
        conn.close()
        return dict(result) if result else None
    
    @staticmethod
    def mark_processed(file_id: str) -> Optional[Dict[str, Any]]:
        """Mark file as processed"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            '''UPDATE receipt_file 
               SET is_processed = TRUE, updated_at = CURRENT_TIMESTAMP 
               WHERE id = ?''',
            (file_id,)
        )
        conn.commit()
        
        # Get updated record
        result = cursor.execute(
            'SELECT * FROM receipt_file WHERE id = ?', 
            (file_id,)
        ).fetchone()
        conn.close()
        return dict(result) if result else None
    
    @staticmethod
    def delete(file_id: str) -> bool:
        """Delete receipt file"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM receipt_file WHERE id = ?', (file_id,))
        deleted_count = cursor.rowcount
        conn.commit()
        conn.close()
        
        return deleted_count > 0
