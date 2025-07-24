"""
Database service for PocketFlow.

This module provides database operations for user management, tokens, and BTC addresses.
"""

import os
import sqlite3
import logging
from typing import List, Optional, Dict, Any
from pathlib import Path

from ..core.types import User, BTCAddress, PaymentTransaction
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
        
        # Fallback to default path
        data_dir = Path("data")
        data_dir.mkdir(exist_ok=True)
        return str(data_dir / "pocketflow.db")
    
    def _init_database(self):
        """Initialize the database with required tables."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Create users table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    email TEXT PRIMARY KEY,
                    name TEXT,
                    personality TEXT,
                    tokens INTEGER DEFAULT 10,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create BTC addresses table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS btc_addresses (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    email TEXT NOT NULL,
                    address TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (email) REFERENCES users (email)
                )
            ''')
            
            # Create BTC payments table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS btc_payments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    email TEXT NOT NULL,
                    btc_amount REAL,
                    usd_amount REAL,
                    tokens_credited INTEGER NOT NULL,
                    tx_id TEXT UNIQUE NOT NULL,
                    timestamp TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create greenlist table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS greenlist (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    email TEXT,
                    domain TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
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
                SELECT email, name, personality, tokens, created_at, updated_at 
                FROM users WHERE email = ?
            ''', (email,))
            
            result = cursor.fetchone()
            conn.close()
            
            if result:
                return User(
                    email=result[0],
                    name=result[1],
                    personality=result[2],
                    tokens=result[3],
                    created_at=result[4],
                    updated_at=result[5]
                )
            return None
            
        except Exception as e:
            self.logger.error(f"Failed to get user {email}: {e}")
            raise DatabaseError(f"Failed to get user: {e}")
    
    def create_user(self, email: str, name: Optional[str] = None, personality: Optional[str] = None, tokens: int = 10) -> User:
        """Create a new user."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO users (email, name, personality, tokens, updated_at) 
                VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
            ''', (email, name, personality, tokens))
            
            conn.commit()
            conn.close()
            
            self.logger.info(f"Created user {email} with {tokens} tokens")
            return self.get_user(email)
            
        except Exception as e:
            self.logger.error(f"Failed to create user {email}: {e}")
            raise DatabaseError(f"Failed to create user: {e}")
    
    def get_tokens(self, email: str) -> int:
        """Get token balance for a user."""
        try:
            user = self.get_user(email)
            return user.tokens if user else 0
        except Exception as e:
            self.logger.error(f"Failed to get tokens for {email}: {e}")
            return 0
    
    def consume_tokens(self, email: str, amount: int = 1) -> bool:
        """Consume tokens for a user."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('SELECT tokens FROM users WHERE email = ?', (email,))
            result = cursor.fetchone()
            
            if not result or result[0] < amount:
                conn.close()
                self.logger.warning(f"Insufficient tokens for {email}: {result[0] if result else 0} < {amount}")
                return False
            
            cursor.execute('''
                UPDATE users SET tokens = tokens - ?, updated_at = CURRENT_TIMESTAMP 
                WHERE email = ?
            ''', (amount, email))
            
            conn.commit()
            conn.close()
            
            self.logger.info(f"Consumed {amount} tokens for {email}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to consume tokens for {email}: {e}")
            return False
    
    def add_tokens(self, email: str, amount: int) -> bool:
        """Add tokens to a user."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE users SET tokens = tokens + ?, updated_at = CURRENT_TIMESTAMP 
                WHERE email = ?
            ''', (amount, email))
            
            conn.commit()
            conn.close()
            
            self.logger.info(f"Added {amount} tokens for {email}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to add tokens for {email}: {e}")
            return False
    
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
    
    def add_btc_address(self, email: str, address: str) -> bool:
        """Add a BTC address for a user."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO btc_addresses (email, address) VALUES (?, ?)
            ''', (email, address))
            
            conn.commit()
            conn.close()
            
            self.logger.info(f"Added BTC address {address} for {email}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to add BTC address for {email}: {e}")
            return False
    
    def get_btc_addresses(self, email: str) -> List[str]:
        """Get all BTC addresses for a user."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('SELECT address FROM btc_addresses WHERE email = ?', (email,))
            results = cursor.fetchall()
            
            conn.close()
            return [row[0] for row in results]
            
        except Exception as e:
            self.logger.error(f"Failed to get BTC addresses for {email}: {e}")
            return []
    
    def is_greenlisted_email(self, email: str) -> bool:
        """Check if an email is in the greenlist."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('SELECT 1 FROM greenlist WHERE email = ?', (email,))
            result = cursor.fetchone()
            
            conn.close()
            return result is not None
            
        except Exception as e:
            self.logger.error(f"Failed to check greenlist for {email}: {e}")
            return False
    
    def is_greenlisted_domain(self, domain: str) -> bool:
        """Check if a domain is in the greenlist."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('SELECT 1 FROM greenlist WHERE domain = ?', (domain,))
            result = cursor.fetchone()
            
            conn.close()
            return result is not None
            
        except Exception as e:
            self.logger.error(f"Failed to check greenlist for domain {domain}: {e}")
            return False
    
    def add_greenlist_email(self, email: str) -> bool:
        """Add an email to the greenlist."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('INSERT OR IGNORE INTO greenlist (email) VALUES (?)', (email,))
            
            conn.commit()
            conn.close()
            
            self.logger.info(f"Added {email} to greenlist")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to add {email} to greenlist: {e}")
            return False
    
    def add_greenlist_domain(self, domain: str) -> bool:
        """Add a domain to the greenlist."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('INSERT OR IGNORE INTO greenlist (domain) VALUES (?)', (domain,))
            
            conn.commit()
            conn.close()
            
            self.logger.info(f"Added domain {domain} to greenlist")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to add domain {domain} to greenlist: {e}")
            return False
    
    def record_payment(self, email: str, btc_amount: float, usd_amount: float, 
                      tokens_credited: int, tx_id: str) -> bool:
        """Record a Bitcoin payment transaction."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO btc_payments 
                (email, btc_amount, usd_amount, tokens_credited, tx_id, timestamp)
                VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            ''', (email, btc_amount, usd_amount, tokens_credited, tx_id))
            
            conn.commit()
            conn.close()
            
            self.logger.info(f"Recorded payment for {email}: {tokens_credited} tokens")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to record payment for {email}: {e}")
            return False


# Global database service instance
database_service = DatabaseService() 