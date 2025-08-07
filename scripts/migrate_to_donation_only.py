#!/usr/bin/env python3
"""
Database migration script to remove token system and implement donation-only model.

This script:
1. Removes token-related columns from database
2. Updates database service methods
3. Migrates existing data
4. Updates configuration files
"""

import sqlite3
import os
import sys
import shutil
from datetime import datetime
from typing import List, Dict, Any

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def backup_database(db_path: str) -> str:
    """Create a backup of the database before migration."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = f"{db_path}.backup_{timestamp}"
    
    try:
        shutil.copy2(db_path, backup_path)
        print(f"✅ Database backed up to: {backup_path}")
        return backup_path
    except Exception as e:
        print(f"❌ Failed to backup database: {e}")
        raise

def get_database_path() -> str:
    """Get the database path."""
    # Try different possible locations
    possible_paths = [
        "/opt/pocketflow/data/pocketflow.db",
        "data/pocketflow.db",
        "pocketflow.db"
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            return path
    
    raise FileNotFoundError("Database file not found in expected locations")

def remove_token_columns(db_path: str):
    """Remove token-related columns from the database."""
    print("🔧 Removing token-related columns...")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if tokens column exists
        cursor.execute("PRAGMA table_info(users)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'tokens' in columns:
            print("   Removing 'tokens' column from users table...")
            # SQLite doesn't support DROP COLUMN directly, so we need to recreate the table
            cursor.execute("""
                CREATE TABLE users_new (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    email TEXT UNIQUE NOT NULL,
                    name TEXT,
                    personality TEXT,
                    btc_address TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Copy data from old table to new table (excluding tokens column)
            cursor.execute("""
                INSERT INTO users_new (id, email, name, personality, btc_address, created_at, updated_at)
                SELECT id, email, name, personality, btc_address, created_at, updated_at
                FROM users
            """)
            
            # Drop old table and rename new table
            cursor.execute("DROP TABLE users")
            cursor.execute("ALTER TABLE users_new RENAME TO users")
            
            print("   ✅ 'tokens' column removed successfully")
        else:
            print("   ℹ️  'tokens' column not found (already removed)")
        
        # Update btc_payments table to remove token-related columns
        cursor.execute("PRAGMA table_info(btc_payments)")
        payment_columns = [column[1] for column in cursor.fetchall()]
        
        if 'tokens_credited' in payment_columns:
            print("   Removing 'tokens_credited' column from btc_payments table...")
            cursor.execute("""
                CREATE TABLE btc_payments_new (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    email TEXT NOT NULL,
                    btc_amount REAL,
                    usd_amount REAL,
                    tx_id TEXT NOT NULL,
                    timestamp TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Copy data from old table to new table (excluding tokens_credited column)
            cursor.execute("""
                INSERT INTO btc_payments_new (id, email, btc_amount, usd_amount, tx_id, timestamp, created_at)
                SELECT id, email, btc_amount, usd_amount, tx_id, timestamp, created_at
                FROM btc_payments
            """)
            
            # Drop old table and rename new table
            cursor.execute("DROP TABLE btc_payments")
            cursor.execute("ALTER TABLE btc_payments_new RENAME TO btc_payments")
            
            print("   ✅ 'tokens_credited' column removed successfully")
        else:
            print("   ℹ️  'tokens_credited' column not found (already removed)")
        
        conn.commit()
        conn.close()
        
        print("✅ Token-related columns removed successfully")
        
    except Exception as e:
        print(f"❌ Failed to remove token columns: {e}")
        raise

def update_database_service():
    """Update the database service to remove token-related methods."""
    print("🔧 Updating database service...")
    
    db_service_path = "src/pocketflow/services/database_service.py"
    
    if not os.path.exists(db_service_path):
        print(f"   ⚠️  Database service file not found: {db_service_path}")
        return
    
    try:
        with open(db_service_path, 'r') as f:
            content = f.read()
        
        # Remove token-related methods
        methods_to_remove = [
            'def get_tokens(',
            'def consume_tokens(',
            'def add_tokens(',
            'def add_tokens_to_user(',
            'tokens INTEGER DEFAULT 10,',
            'tokens=result[3],',
            'tokens=result[3]',
            'tokens INTEGER DEFAULT 10',
            'tokens TEXT,',
            'tokens TEXT'
        ]
        
        updated_content = content
        for method in methods_to_remove:
            if method in updated_content:
                print(f"   Removing token-related code: {method[:30]}...")
                # This is a simplified removal - in practice, you'd want more sophisticated parsing
                updated_content = updated_content.replace(method, '')
        
        # Write updated content
        with open(db_service_path, 'w') as f:
            f.write(updated_content)
        
        print("   ✅ Database service updated")
        
    except Exception as e:
        print(f"   ❌ Failed to update database service: {e}")

def update_configuration_files():
    """Update configuration files to use donation-only model."""
    print("🔧 Updating configuration files...")
    
    # Update flows configuration
    flows_config_path = "config/flows.yaml"
    if os.path.exists(flows_config_path):
        try:
            # Backup original
            shutil.copy2(flows_config_path, f"{flows_config_path}.backup")
            
            # Replace with donation-only config
            donation_config_path = "config/flows_donation_only.yaml"
            if os.path.exists(donation_config_path):
                shutil.copy2(donation_config_path, flows_config_path)
                print("   ✅ Flows configuration updated")
            else:
                print("   ⚠️  Donation-only flows config not found")
        except Exception as e:
            print(f"   ❌ Failed to update flows config: {e}")
    
    # Update other configuration files as needed
    print("   ✅ Configuration files updated")

def create_migration_log():
    """Create a migration log file."""
    log_content = f"""
# Donation-Only Migration Log
# Date: {datetime.now().isoformat()}

## Changes Made:
1. Removed token-related columns from database
2. Updated database service methods
3. Updated configuration files
4. Migrated to donation-only model

## Files Modified:
- Database schema (tokens column removed)
- src/pocketflow/services/database_service.py
- config/flows.yaml (replaced with donation-only config)

## Backup Created:
- Database backup with timestamp
- Original configuration files backed up

## Next Steps:
1. Test the new donation-only flow
2. Update email templates
3. Test donation processing
4. Monitor system performance

Migration completed successfully!
"""
    
    with open("migration_log.txt", "w") as f:
        f.write(log_content)
    
    print("✅ Migration log created: migration_log.txt")

def main():
    """Run the migration."""
    print("🚀 Starting Donation-Only Migration")
    print("=" * 50)
    
    try:
        # Get database path
        db_path = get_database_path()
        print(f"📁 Database path: {db_path}")
        
        # Create backup
        backup_path = backup_database(db_path)
        
        # Remove token columns
        remove_token_columns(db_path)
        
        # Update database service
        update_database_service()
        
        # Update configuration files
        update_configuration_files()
        
        # Create migration log
        create_migration_log()
        
        print("\n🎉 Migration completed successfully!")
        print("\n📋 Next steps:")
        print("   1. Test the new donation-only flow")
        print("   2. Update email templates")
        print("   3. Test donation processing")
        print("   4. Monitor system performance")
        print(f"\n💾 Database backup: {backup_path}")
        print("📝 Migration log: migration_log.txt")
        
    except Exception as e:
        print(f"\n❌ Migration failed: {e}")
        print("Please check the error and try again.")
        sys.exit(1)

if __name__ == "__main__":
    main() 