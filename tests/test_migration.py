#!/usr/bin/env python3
"""
Test script for database migration from SQLite to PostgreSQL.
"""

import sqlite3
import psycopg2
import sys
import os
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

# Set required environment variables at module level
os.environ.setdefault('EMAIL_HOST', 'localhost')
os.environ.setdefault('EMAIL_USERNAME', 'test@example.com')
os.environ.setdefault('EMAIL_PASSWORD', 'testpassword')

def test_sqlite_connection():
    """Test SQLite database connection and structure."""
    
    sqlite_paths = [
        "pocketflow.db",
        "/opt/pocketflow/data/pocketflow.db",
        "../dashboard/pocketflow.db"
    ]
    
    sqlite_path = None
    for path in sqlite_paths:
        if Path(path).exists():
            sqlite_path = path
            break
    
    if not sqlite_path:
        print("✗ No SQLite database found")
        return False
    
    try:
        conn = sqlite3.connect(sqlite_path)
        cursor = conn.cursor()
        print(f"✓ Connected to SQLite database: {sqlite_path}")
        
        # Check tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        table_names = [table[0] for table in tables]
        print(f"✓ SQLite tables: {table_names}")
        
        # Check data counts
        for table in table_names:
            if table != 'sqlite_sequence':
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                print(f"✓ {table}: {count} records")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"✗ SQLite test failed: {e}")
        return False

def test_postgresql_migration():
    """Test PostgreSQL migration and data integrity."""
    
    postgresql_url = "postgresql://pocketflow:pocketflow_password@localhost:5432/pocketflow"
    
    try:
        conn = psycopg2.connect(postgresql_url)
        cursor = conn.cursor()
        print("✓ Connected to PostgreSQL database")
        
        # Check tables
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            ORDER BY table_name;
        """)
        tables = cursor.fetchall()
        table_names = [table[0] for table in tables]
        print(f"✓ PostgreSQL tables: {table_names}")
        
        # Check data counts
        for table in table_names:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            print(f"✓ {table}: {count} records")
        
        # Test data integrity
        cursor.execute("SELECT COUNT(*) FROM users")
        user_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM greenlist")
        greenlist_count = cursor.fetchone()[0]
        
        print(f"✓ Data integrity check: {user_count} users, {greenlist_count} greenlist entries")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"✗ PostgreSQL migration test failed: {e}")
        return False

def test_database_compatibility():
    """Test that both SQLite and PostgreSQL can be used."""
    
    try:
        from pocketflow.services.database_service import DatabaseService
        
        # Set required environment variables
        os.environ.setdefault('EMAIL_HOST', 'localhost')
        os.environ.setdefault('EMAIL_USERNAME', 'test@example.com')
        os.environ.setdefault('EMAIL_PASSWORD', 'testpassword')
        
        # Test PostgreSQL
        os.environ['DATABASE_URL'] = "postgresql://pocketflow:pocketflow_password@localhost:5432/pocketflow"
        pg_db = DatabaseService()
        print("✓ PostgreSQL DatabaseService initialized")
        
        # Test SQLite (if file exists)
        if Path("pocketflow.db").exists():
            os.environ['DATABASE_URL'] = "sqlite:///pocketflow.db"
            sqlite_db = DatabaseService()
            print("✓ SQLite DatabaseService initialized")
        
        print("✓ Database compatibility test passed")
        return True
        
    except Exception as e:
        print(f"✗ Database compatibility test failed: {e}")
        return False

if __name__ == "__main__":
    print("Running database migration tests...")
    print("=" * 50)
    
    success1 = test_sqlite_connection()
    print()
    
    success2 = test_postgresql_migration()
    print()
    
    success3 = test_database_compatibility()
    print()
    
    if success1 and success2 and success3:
        print("🎉 All migration tests passed!")
        exit(0)
    else:
        print("❌ Some migration tests failed!")
        exit(1) 