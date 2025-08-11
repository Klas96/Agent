#!/usr/bin/env python3
"""
Test script to verify PostgreSQL connectivity and database operations.
"""

import psycopg2
import os
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

# Set required environment variables at module level
os.environ.setdefault('EMAIL_HOST', 'localhost')
os.environ.setdefault('EMAIL_USERNAME', 'test@example.com')
os.environ.setdefault('EMAIL_PASSWORD', 'testpassword')

def test_postgresql_connection():
    """Test PostgreSQL connection and basic operations."""
    
    # Set database URL
    os.environ['DATABASE_URL'] = "postgresql://pocketflow:pocketflow_password@localhost:5432/pocketflow"
    
    try:
        # Connect to PostgreSQL
        conn = psycopg2.connect(os.environ['DATABASE_URL'])
        cursor = conn.cursor()
        print("✓ Connected to PostgreSQL successfully")
        
        # Test basic query
        cursor.execute("SELECT version();")
        version = cursor.fetchone()
        print(f"✓ PostgreSQL version: {version[0]}")
        
        # Test table existence
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name IN ('users', 'scheduled_jobs', 'job_executions', 'greenlist')
            ORDER BY table_name;
        """)
        tables = cursor.fetchall()
        print(f"✓ Found tables: {[table[0] for table in tables]}")
        
        # Test inserting a test user
        cursor.execute("""
            INSERT INTO users (email, name, personality) 
            VALUES (%s, %s, %s)
            ON CONFLICT (email) DO NOTHING
        """, ('test@example.com', 'Test User', 'Test personality'))
        
        # Test reading the user
        cursor.execute("SELECT email, name FROM users WHERE email = %s", ('test@example.com',))
        user = cursor.fetchone()
        if user:
            print(f"✓ Successfully created and read user: {user[0]} ({user[1]})")
        
        conn.commit()
        conn.close()
        print("✓ PostgreSQL test completed successfully!")
        return True
        
    except Exception as e:
        print(f"✗ PostgreSQL test failed: {e}")
        return False

def test_database_service():
    """Test the DatabaseService with PostgreSQL."""
    try:
        from pocketflow.services.database_service import DatabaseService
        
        # Set required environment variables
        os.environ['DATABASE_URL'] = "postgresql://pocketflow:pocketflow_password@localhost:5432/pocketflow"
        os.environ.setdefault('EMAIL_HOST', 'localhost')
        os.environ.setdefault('EMAIL_USERNAME', 'test@example.com')
        os.environ.setdefault('EMAIL_PASSWORD', 'testpassword')
        
        # Initialize database service
        db = DatabaseService()
        print("✓ DatabaseService initialized successfully")
        
        # Test basic database operations without User model validation
        # Get all users (this should work)
        all_users = db.get_all_users()
        print(f"✓ Retrieved {len(all_users)} users from database")
        
        # Test scheduled jobs operations
        jobs = db.get_scheduled_jobs()
        print(f"✓ Retrieved {len(jobs)} scheduled jobs")
        
        print("✓ DatabaseService test completed successfully!")
        return True
        
    except Exception as e:
        print(f"✗ DatabaseService test failed: {e}")
        return False

if __name__ == "__main__":
    print("Running PostgreSQL tests...")
    print("=" * 50)
    
    success1 = test_postgresql_connection()
    print()
    
    success2 = test_database_service()
    print()
    
    if success1 and success2:
        print("🎉 All tests passed!")
        exit(0)
    else:
        print("❌ Some tests failed!")
        exit(1) 