#!/usr/bin/env python3
"""
Migration script to deprecate Bitcoin-related tables.

This script renames BTC-related tables with a _deprecated suffix
to remove them from active use while preserving the data.
"""

import sqlite3
import sys
from pathlib import Path
from datetime import datetime

def migrate_btc_deprecation(db_path):
    """Deprecate BTC-related tables by renaming them."""
    
    try:
        # Connect to database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print(f"Starting BTC deprecation migration at {datetime.now()}")
        print(f"Database: {db_path}")
        
        # List of BTC-related tables to deprecate
        btc_tables = [
            'btc_addresses',
            'btc_payments', 
            'user_btc_addresses',
            'address_balances',
            'payment_logs',
            'payment_transactions'
        ]
        
        # Check which tables exist
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        existing_tables = [row[0] for row in cursor.fetchall()]
        
        tables_to_migrate = []
        for table in btc_tables:
            if table in existing_tables:
                tables_to_migrate.append(table)
                print(f"✓ Found table: {table}")
            else:
                print(f"ℹ️  Table not found: {table}")
        
        if not tables_to_migrate:
            print("No BTC-related tables found to deprecate.")
            return True
            
        # Rename tables
        for table in tables_to_migrate:
            deprecated_name = f"{table}_deprecated"
            
            # Check if deprecated table already exists
            if deprecated_name in existing_tables:
                print(f"⚠️  Deprecated table {deprecated_name} already exists, skipping {table}")
                continue
                
            try:
                cursor.execute(f"ALTER TABLE {table} RENAME TO {deprecated_name}")
                print(f"✅ Renamed {table} to {deprecated_name}")
            except sqlite3.Error as e:
                print(f"❌ Error renaming {table}: {e}")
                return False
        
        # Remove any btc_address column from users table if it exists
        try:
            cursor.execute("PRAGMA table_info(users)")
            user_columns = [col[1] for col in cursor.fetchall()]
            
            if 'btc_address' in user_columns:
                print("Removing btc_address column from users table...")
                
                # Create new users table without btc_address
                cursor.execute("""
                    CREATE TABLE users_new (
                        email TEXT PRIMARY KEY,
                        name TEXT DEFAULT '',
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        personality TEXT DEFAULT 'Friendly AI'
                    )
                """)
                
                # Copy data (excluding btc_address)
                cursor.execute("""
                    INSERT INTO users_new (email, name, created_at, updated_at, personality)
                    SELECT email, name, created_at, updated_at, personality
                    FROM users
                """)
                
                # Replace old table
                cursor.execute("DROP TABLE users")
                cursor.execute("ALTER TABLE users_new RENAME TO users")
                print("✅ Removed btc_address column from users table")
            else:
                print("ℹ️  No btc_address column found in users table")
                
        except sqlite3.Error as e:
            print(f"❌ Error updating users table: {e}")
            return False
        
        # Commit changes
        conn.commit()
        print(f"✅ BTC deprecation migration completed successfully at {datetime.now()}")
        
        return True
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        return False
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    # Default to production database path
    default_db = "/opt/pocketflow/data/pocketflow.db"
    db_path = sys.argv[1] if len(sys.argv) > 1 else default_db
    
    if not Path(db_path).exists():
        print(f"❌ Database file not found: {db_path}")
        sys.exit(1)
    
    print("🔧 PocketFlow BTC Deprecation Migration")
    print("=" * 50)
    
    success = migrate_btc_deprecation(db_path)
    
    if success:
        print("✅ Migration completed successfully!")
        sys.exit(0)
    else:
        print("❌ Migration failed!")
        sys.exit(1) 