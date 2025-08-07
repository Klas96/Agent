#!/usr/bin/env python3
"""
Simple database migration to remove token system.
"""

import sqlite3
import os
import sys
from datetime import datetime

def migrate_database():
    """Migrate the database to remove token system."""
    db_path = "/opt/pocketflow/data/pocketflow.db"
    
    print("🔧 Starting database migration...")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check current schema
        cursor.execute("PRAGMA table_info(users)")
        columns = [column[1] for column in cursor.fetchall()]
        print(f"Current users table columns: {columns}")
        
        # Remove tokens column from users table
        if 'tokens' in columns:
            print("Removing 'tokens' column from users table...")
            
            # Create new table without tokens column
            cursor.execute("""
                CREATE TABLE users_new (
                    email TEXT PRIMARY KEY,
                    name TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    personality TEXT,
                    btc_address TEXT
                )
            """)
            
            # Copy data excluding tokens column
            cursor.execute("""
                INSERT INTO users_new (email, name, created_at, updated_at, personality, btc_address)
                SELECT email, name, created_at, updated_at, personality, btc_address
                FROM users
            """)
            
            # Drop old table and rename new table
            cursor.execute("DROP TABLE users")
            cursor.execute("ALTER TABLE users_new RENAME TO users")
            print("✅ Tokens column removed from users table")
        else:
            print("ℹ️  Tokens column already removed from users table")
        
        # Check btc_payments table
        cursor.execute("PRAGMA table_info(btc_payments)")
        payment_columns = [column[1] for column in cursor.fetchall()]
        print(f"Current btc_payments table columns: {payment_columns}")
        
        # Remove tokens_credited column from btc_payments table
        if 'tokens_credited' in payment_columns:
            print("Removing 'tokens_credited' column from btc_payments table...")
            
            # Create new table without tokens_credited column
            cursor.execute("""
                CREATE TABLE btc_payments_new (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    email TEXT NOT NULL,
                    btc_amount REAL,
                    usd_amount REAL,
                    tx_id TEXT UNIQUE NOT NULL,
                    timestamp TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Copy data excluding tokens_credited column
            cursor.execute("""
                INSERT INTO btc_payments_new (id, email, btc_amount, usd_amount, tx_id, timestamp, created_at)
                SELECT id, email, btc_amount, usd_amount, tx_id, timestamp, created_at
                FROM btc_payments
            """)
            
            # Drop old table and rename new table
            cursor.execute("DROP TABLE btc_payments")
            cursor.execute("ALTER TABLE btc_payments_new RENAME TO btc_payments")
            print("✅ tokens_credited column removed from btc_payments table")
        else:
            print("ℹ️  tokens_credited column already removed from btc_payments table")
        
        conn.commit()
        conn.close()
        print("✅ Database migration completed successfully!")
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        raise

if __name__ == "__main__":
    migrate_database() 