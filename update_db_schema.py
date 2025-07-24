#!/usr/bin/env python3
"""
Database Schema Update Script for PocketFlow
This script ensures both local and production databases have the correct schema.
"""

import sqlite3
import os
from pathlib import Path

def update_database_schema(db_path):
    """Update database schema to include all required columns."""
    print(f"Updating schema for: {db_path}")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Check current schema
    cursor.execute("PRAGMA table_info(users)")
    columns = [row[1] for row in cursor.fetchall()]
    print(f"Current columns: {columns}")
    
    # Add missing columns
    if 'personality' not in columns:
        cursor.execute("ALTER TABLE users ADD COLUMN personality TEXT")
        print("Added personality column")
    
    # Verify final schema
    cursor.execute("PRAGMA table_info(users)")
    final_columns = [row[1] for row in cursor.fetchall()]
    print(f"Final columns: {final_columns}")
    
    conn.commit()
    conn.close()
    print("Schema update complete!")

def main():
    """Update both local and production databases."""
    # Local database
    local_db = Path("pocketflow.db")
    if local_db.exists():
        update_database_schema(str(local_db))
    
    # Production database
    prod_db = Path("/opt/pocketflow/data/pocketflow.db")
    if prod_db.exists():
        update_database_schema(str(prod_db))
    else:
        print("Production database not found at /opt/pocketflow/data/pocketflow.db")

if __name__ == "__main__":
    main() 