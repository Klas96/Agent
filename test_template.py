#!/usr/bin/env python3
import os
import sys

# Change to the deployed directory
os.chdir('/opt/pocketflow')

# Add the path
sys.path.append('/opt/pocketflow')

from control_panel import app, get_all_users
from flask import render_template

# Get users
users = get_all_users()
print(f"Users found: {len(users)}")
if users:
    print(f"First user: {users[0]}")

# Test template rendering
with app.app_context():
    try:
        result = render_template('users.html', users=users)
        print(f"Template rendered successfully, length: {len(result)}")
        
        # Check if the result contains user data
        if "test5@example.com" in result:
            print("✅ Template contains user data")
        else:
            print("❌ Template does not contain user data")
            
    except Exception as e:
        print(f"❌ Template rendering error: {e}") 