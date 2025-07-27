#!/usr/bin/env python3
"""
Debug script for personality editing issues
"""

import sqlite3
import os

def check_database():
    """Check the database for personality-related issues."""
    db_paths = ["pocketflow.db", "/opt/pocketflow/data/pocketflow.db", "/opt/pocketflow/data/users.db"]
    
    for db_path in db_paths:
        if os.path.exists(db_path):
            print(f"\n=== Checking database: {db_path} ===")
            
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Check table structure
            cursor.execute("PRAGMA table_info(users)")
            columns = cursor.fetchall()
            print("Table columns:")
            for col in columns:
                print(f"  - {col[1]} ({col[2]})")
            
            # Check for users with personality data
            cursor.execute("SELECT email, name, personality, tokens FROM users LIMIT 5")
            users = cursor.fetchall()
            print(f"\nSample users:")
            for user in users:
                print(f"  - {user[0]}: name='{user[1]}', personality='{user[2]}', tokens={user[3]}")
            
            conn.close()

def test_update_function():
    """Test the update_user function directly."""
    print("\n=== Testing update_user function ===")
    
    try:
        from src.pocketflow.web.routes import update_user, get_user_by_email
        
        # Test data
        test_email = "debug@example.com"
        test_personality = "Debug personality test"
        
        # First, check if user exists
        user = get_user_by_email(test_email)
        if not user:
            print(f"User {test_email} not found, creating...")
            from src.pocketflow.web.routes import add_user
            add_user(test_email, "Debug User", "Original personality", 10)
        
        # Test updating personality
        print(f"Updating personality for {test_email}...")
        success = update_user(test_email, personality=test_personality)
        
        if success:
            print("✅ Update successful!")
            # Verify the update
            updated_user = get_user_by_email(test_email)
            print(f"Updated personality: '{updated_user['personality']}'")
        else:
            print("❌ Update failed!")
            
    except Exception as e:
        print(f"❌ Error testing update function: {e}")

if __name__ == "__main__":
    check_database()
    test_update_function() 