import sqlite3
import os
from flask import current_app

def get_db_connection():
    """Get SQLite database connection"""
    db_path = current_app.config['SQLALCHEMY_DATABASE_URI'].replace('sqlite:///', '')
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize database with tables"""
    from app import db
    db.create_all()
    print("Database tables created successfully!")

def drop_db():
    """Drop all tables"""
    from app import db
    db.drop_all()
    print("Database tables dropped!")

def reset_db():
    """Reset database"""
    drop_db()
    init_db()
