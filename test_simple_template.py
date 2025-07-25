#!/usr/bin/env python3
import os
import sys

# Change to the deployed directory
os.chdir('/opt/pocketflow')

# Add the path
sys.path.append('/opt/pocketflow')

from src.pocketflow.web.app import create_app
from flask import render_template

# Create app
app = create_app()

# Test template rendering
with app.app_context():
    try:
        result = render_template('simple_control_panel.html', users=[], message="")
        print(f"Template rendered successfully, length: {len(result)}")
        print("✅ Template rendering works")
            
    except Exception as e:
        print(f"❌ Template rendering error: {e}") 