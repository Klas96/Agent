#!/usr/bin/env python3
import os
import sys

# Change to the deployed directory
os.chdir('/opt/pocketflow')

# Add the path
sys.path.append('/opt/pocketflow')

from control_panel import app
from flask import render_template

# Test data
test_users = [
    {
        "email": "test@example.com",
        "name": "Test User",
        "tokens": 10,
        "created_at": "2025-07-24 15:00:00",
        "updated_at": "2025-07-24 15:00:00"
    }
]

# Test template rendering
with app.app_context():
    try:
        result = render_template('users.html', users=test_users)
        print(f"✅ Template rendered successfully, length: {len(result)}")
        
        # Check if the result contains user data
        if "test@example.com" in result:
            print("✅ Template contains user data")
        else:
            print("❌ Template does not contain user data")
            
    except Exception as e:
        print(f"❌ Template rendering error: {e}") 