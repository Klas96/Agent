import os
import sqlite3
import logging
from typing import List, Optional

logger = logging.getLogger(__name__)

# Database path
DB_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "users.db")

def init_db():
    """Initialize the user database."""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Create users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            email TEXT PRIMARY KEY,
            tokens INTEGER DEFAULT 10,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create BTC addresses table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS btc_addresses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT,
            address TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (email) REFERENCES users (email)
        )
    ''')
    
    conn.commit()
    conn.close()

def set_user(email: str, tokens: int = 10):
    """Set or update a user."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT OR REPLACE INTO users (email, tokens) VALUES (?, ?)
    ''', (email, tokens))
    
    conn.commit()
    conn.close()

def get_tokens(email: str) -> int:
    """Get token balance for a user."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('SELECT tokens FROM users WHERE email = ?', (email,))
    result = cursor.fetchone()
    
    conn.close()
    return result[0] if result else 0

def consume_tokens(email: str, amount: int = 1) -> bool:
    """Consume tokens for a user."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('SELECT tokens FROM users WHERE email = ?', (email,))
    result = cursor.fetchone()
    
    if not result or result[0] < amount:
        conn.close()
        return False
    
    cursor.execute('''
        UPDATE users SET tokens = tokens - ? WHERE email = ?
    ''', (amount, email))
    
    conn.commit()
    conn.close()
    return True

def add_btc_address(email: str, address: str):
    """Add a BTC address for a user."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO btc_addresses (email, address) VALUES (?, ?)
    ''', (email, address))
    
    conn.commit()
    conn.close()

def get_btc_addresses(email: str) -> List[str]:
    """Get all BTC addresses for a user."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('SELECT address FROM btc_addresses WHERE email = ?', (email,))
    results = cursor.fetchall()
    
    conn.close()
    return [row[0] for row in results]

def is_greenlisted_email(email: str) -> bool:
    """Check if email is greenlisted."""
    greenlisted_emails = [
        "klas0holmgren@gmail.com",
        "test@example.com"
    ]
    return email.lower() in greenlisted_emails

def is_greenlisted_domain(domain: str) -> bool:
    """Check if domain is greenlisted."""
    greenlisted_domains = [
        "gmail.com",
        "example.com", 
        "trusted.org"
    ]
    return domain.lower() in greenlisted_domains
