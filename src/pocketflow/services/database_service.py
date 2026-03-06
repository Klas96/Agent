"""
Database service for PocketFlow.

This module provides database operations for user management.
"""

import os
import sqlite3
import logging
from typing import List, Optional, Dict, Any
from pathlib import Path

from ..core.types import User
from ..config.settings import get_settings
from ..utils.errors import DatabaseError
from ..utils.logging import get_logger


class DatabaseService:
    """Service for handling database operations."""
    
    def __init__(self):
        self.settings = get_settings()
        self.logger = get_logger("DatabaseService")
        self.db_path = self._get_db_path()
        self._init_database()
    
    def _get_db_path(self) -> str:
        """Get the database file path."""
        # Try to use the configured path first
        if hasattr(self.settings, 'DATABASE_URL') and self.settings.DATABASE_URL:
            if self.settings.DATABASE_URL.startswith('sqlite:///'):
                return self.settings.DATABASE_URL.replace('sqlite:///', '')
        
        # Use absolute path for production
        data_dir = Path("/opt/pocketflow/data")
        data_dir.mkdir(exist_ok=True)
        return str(data_dir / "pocketflow.db")
    
    def _init_database(self):
        """Initialize the database with required tables."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Create users table (simplified - no Bitcoin or payment fields)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    email TEXT UNIQUE NOT NULL,
                    name TEXT,
                    personality TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            

            
            conn.commit()
            conn.close()
            self.logger.info(f"Database initialized at {self.db_path}")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize database: {e}")
            raise DatabaseError(f"Database initialization failed: {e}")
    
    def get_user(self, email: str) -> Optional[User]:
        """Get user by email."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT email, name, personality, created_at, updated_at 
                FROM users WHERE email = ?
            ''', (email,))
            
            result = cursor.fetchone()
            conn.close()
            
            if result:
                return User(
                    email=result[0],
                    name=result[1],
                    personality=result[2],
                    tokens=0,  # Tokens are deprecated - always return 0
                    created_at=result[3],
                    updated_at=result[4]
                )
            return None
            
        except Exception as e:
            self.logger.error(f"Failed to get user {email}: {e}")
            raise DatabaseError(f"Failed to get user: {e}")
    
    def get_all_users(self) -> List[Dict]:
        """Get all users with their information."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT id, email, name, personality, created_at, updated_at
                FROM users
            ''')
            
            columns = [description[0] for description in cursor.description]
            users = []
            
            for row in cursor.fetchall():
                user_dict = dict(zip(columns, row))
                users.append(user_dict)
            
            conn.close()
            return users
            
        except Exception as e:
            self.logger.error(f"Failed to get all users: {e}")
            return []
    
    def create_user(self, email: str, name: Optional[str] = None, personality: Optional[str] = None) -> User:
        """Create a new user."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO users (email, name, personality, updated_at) 
                VALUES (?, ?, ?, CURRENT_TIMESTAMP)
            ''', (email, name, personality))
            
            conn.commit()
            conn.close()
            
            self.logger.info(f"Created user {email}")
            return self.get_user(email)
            
        except Exception as e:
            self.logger.error(f"Failed to create user {email}: {e}")
            raise DatabaseError(f"Failed to create user: {e}")
    
    def update_user_personality(self, email: str, personality: Optional[str] = None) -> bool:
        """Update user personality."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE users SET personality = ?, updated_at = CURRENT_TIMESTAMP 
                WHERE email = ?
            ''', (personality, email))
            
            if cursor.rowcount == 0:
                conn.close()
                return False
            
            conn.commit()
            conn.close()
            
            self.logger.info(f"Updated personality for {email}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to update personality for {email}: {e}")
            return False
    
 