#!/usr/bin/env python3
"""
PocketFlow Control Panel (Minimal Version)
A web-based control panel for managing users, tokens, Bitcoin addresses,
and system configuration for PocketFlow.
"""
import os
import sys
from pathlib import Path
# Add src to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from flask import Flask, render_template, request, jsonify, Blueprint, redirect, url_for, flash
from flask_cors import CORS
import sqlite3
from datetime import datetime
import json

# Database path
DB_PATH = Path("/opt/pocketflow/data/pocketflow.db")
if not DB_PATH.exists():
    # Fallback to local development database
    DB_PATH = Path("data/pocketflow.db")
    if not DB_PATH.exists():
        # Create local database for development
        DB_PATH.parent.mkdir(exist_ok=True)
        import sqlite3
        conn = sqlite3.connect(str(DB_PATH))
        cursor = conn.cursor()
        
        # Create users table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            email TEXT PRIMARY KEY,
            tokens INTEGER DEFAULT 10,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # Create btc_addresses table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS btc_addresses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT NOT NULL,
            address TEXT NOT NULL UNIQUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (email) REFERENCES users(email)
        )
        ''')
        
        # Create payment_transactions table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS payment_transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT NOT NULL,
            amount_btc REAL NOT NULL,
            amount_usd REAL NOT NULL,
            status TEXT DEFAULT 'pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (email) REFERENCES users(email)
        )
        ''')
        
        
        
        conn.commit()
        conn.close()
        print(f"Created local database at {DB_PATH}")

def get_db_connection():
    """Get database connection."""
    return sqlite3.connect(str(DB_PATH))

def get_all_users():
    """Get all users from database."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT email, name, personality, tokens, created_at, updated_at 
            FROM users 
            ORDER BY created_at DESC
        """)
        users = []
        for row in cursor.fetchall():
            users.append({
                "email": row[0],
                "name": row[1],
                "personality": row[2],
                "tokens": row[3],
                "created_at": row[4],
                "updated_at": row[5]
            })
        conn.close()
        return users
    except Exception as e:
        print(f"Error getting users: {e}")
        return []

def get_system_stats():
    """Get system statistics."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get user count
        cursor.execute("SELECT COUNT(*) as count FROM users")
        total_users = cursor.fetchone()[0]
        
        # Get total tokens
        cursor.execute("SELECT COALESCE(SUM(tokens), 0) as total FROM users")
        total_tokens = cursor.fetchone()[0]
        
        # Get total payments
        cursor.execute("SELECT COUNT(*) as count FROM payment_transactions")
        total_payments = cursor.fetchone()[0]
        

        
        conn.close()
        
        return {
            "total_users": total_users,
            "total_tokens": total_tokens,
            "total_payments": total_payments
        }
    except Exception as e:
        print(f"Error getting system stats: {e}")
        return {
            "total_users": 0,
            "total_tokens": 0,
            "total_payments": 0
        }

def add_user(email, name=None, personality=None, tokens=10):
    """Add a new user."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if user already exists
        cursor.execute("SELECT email FROM users WHERE email = ?", (email,))
        if cursor.fetchone():
            print(f"User {email} already exists")
            conn.close()
            return False
        
        # Add user
        cursor.execute("""
            INSERT INTO users (email, name, personality, tokens, created_at, updated_at)
            VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
        """, (email, name, personality, tokens))
        
        conn.commit()
        conn.close()
        
        print(f"Successfully added user: {email} with {tokens} tokens")
        return True
    except Exception as e:
        print(f"Error adding user {email}: {e}")
        return False

def get_user_by_email(email):
    """Get user by email."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT email, name, personality, tokens, created_at, updated_at 
            FROM users 
            WHERE email = ?
        """, (email,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return {
                "email": row[0],
                "name": row[1],
                "personality": row[2],
                "tokens": row[3],
                "created_at": row[4],
                "updated_at": row[5]
            }
        return None
    except Exception as e:
        print(f"Error getting user {email}: {e}")
        return None

def update_user_tokens(email, new_tokens):
    """Update user tokens."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE users 
            SET tokens = ?, updated_at = CURRENT_TIMESTAMP
            WHERE email = ?
        """, (new_tokens, email))
        
        if cursor.rowcount == 0:
            conn.close()
            return False
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error updating user tokens {email}: {e}")
        return False

def update_user(email, name=None, personality=None, new_tokens=None):
    """Update user name, personality and/or tokens."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        if name is not None and personality is not None and new_tokens is not None:
            cursor.execute("""
                UPDATE users 
                SET name = ?, personality = ?, tokens = ?, updated_at = CURRENT_TIMESTAMP
                WHERE email = ?
            """, (name, personality, new_tokens, email))
        elif name is not None and personality is not None:
            cursor.execute("""
                UPDATE users 
                SET name = ?, personality = ?, updated_at = CURRENT_TIMESTAMP
                WHERE email = ?
            """, (name, personality, email))
        elif name is not None and new_tokens is not None:
            cursor.execute("""
                UPDATE users 
                SET name = ?, tokens = ?, updated_at = CURRENT_TIMESTAMP
                WHERE email = ?
            """, (name, new_tokens, email))
        elif personality is not None and new_tokens is not None:
            cursor.execute("""
                UPDATE users 
                SET personality = ?, tokens = ?, updated_at = CURRENT_TIMESTAMP
                WHERE email = ?
            """, (personality, new_tokens, email))
        elif name is not None:
            cursor.execute("""
                UPDATE users 
                SET name = ?, updated_at = CURRENT_TIMESTAMP
                WHERE email = ?
            """, (name, email))
        elif personality is not None:
            cursor.execute("""
                UPDATE users 
                SET personality = ?, updated_at = CURRENT_TIMESTAMP
                WHERE email = ?
            """, (personality, email))
        elif new_tokens is not None:
            cursor.execute("""
                UPDATE users 
                SET tokens = ?, updated_at = CURRENT_TIMESTAMP
                WHERE email = ?
            """, (new_tokens, email))
        else:
            conn.close()
            return False
        
        if cursor.rowcount == 0:
            conn.close()
            return False
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error updating user {email}: {e}")
        return False

def delete_user(email):
    """Delete user and related data."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Delete related records first (due to foreign key constraints)
        cursor.execute("DELETE FROM payment_transactions WHERE email = ?", (email,))
        cursor.execute("DELETE FROM btc_addresses WHERE email = ?", (email,))
        cursor.execute("DELETE FROM users WHERE email = ?", (email,))
        
        if cursor.rowcount == 0:
            conn.close()
            return False
        
        conn.commit()
        conn.close()
        
        print(f"Deleted user: {email}")
        return True
    except Exception as e:
        print(f"Error deleting user {email}: {e}")
        return False

# Create Flask app
app = Flask(__name__)
app.secret_key = 'pocketflow-control-panel-secret-key'
CORS(app)

# Configure static files
app.static_folder = 'src/pocketflow/web/static'
app.template_folder = 'src/pocketflow/web/templates'

# Create admin blueprint
admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_bp.route('/', methods=['GET', 'POST'])
def dashboard():
    """Dashboard page - now uses simple control panel."""
    message = ""
    if request.method == 'POST':
        if 'add_user' in request.form:
            email = request.form.get('email', '').strip()
            name = request.form.get('name', '').strip()
            personality = request.form.get('personality', '').strip()
            tokens = int(request.form.get('tokens', 10))
            if email:
                if add_user(email, name, personality, tokens):
                    message = f"User {email} added."
                else:
                    message = f"Failed to add user {email}."
        elif 'delete_user' in request.form:
            email = request.form.get('delete_user')
            if delete_user(email):
                message = f"User {email} deleted."
            else:
                message = f"Failed to delete user {email}."
        elif 'edit_user' in request.form:
            email = request.form.get('edit_email')
            name = request.form.get('edit_name', '').strip()
            personality = request.form.get('edit_personality', '').strip()
            tokens = int(request.form.get('edit_tokens', 10))
            if update_user(email, name, personality, tokens):
                message = f"User {email} updated."
            else:
                message = f"Failed to update user {email}."
    users = get_all_users()
    return render_template("simple_control_panel.html", users=users, message=message)

# API Routes
@admin_bp.route('/api/users', methods=['GET'])
def api_get_users():
    """Get all users."""
    try:
        users = get_all_users()
        return jsonify({"success": True, "users": users})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@admin_bp.route('/api/users', methods=['POST'])
def api_add_user():
    """Add a new user."""
    try:
        data = request.get_json()
        email = data.get('email', '').strip()
        name = data.get('name', '').strip() or None
        personality = data.get('personality', '').strip() or None
        initial_tokens = int(data.get('initial_tokens', 10))
        notes = data.get('notes', '').strip()
        
        if not email:
            return jsonify({"success": False, "error": "Email is required"}), 400
        
        if add_user(email, name, personality, initial_tokens):
            return jsonify({
                "success": True,
                "message": f"User {email} added successfully",
                "user": {"email": email, "name": name, "personality": personality, "tokens": initial_tokens}
            })
        else:
            return jsonify({"success": False, "error": "Failed to add user"}), 500
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@admin_bp.route('/api/users/<email>', methods=['DELETE'])
def api_delete_user(email):
    """Delete a user."""
    try:
        if delete_user(email):
            return jsonify({"success": True, "message": f"User {email} deleted successfully"})
        else:
            return jsonify({"success": False, "error": "Failed to delete user"}), 500
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@admin_bp.route('/api/users/<email>', methods=['PUT'])
def api_update_user(email):
    """Update a user."""
    try:
        data = request.get_json()
        name = data.get('name', '').strip() or None
        personality = data.get('personality', '').strip() or None
        tokens = int(data.get('tokens', 10))
        
        if update_user(email, name, personality, tokens):
            return jsonify({
                "success": True,
                "message": f"User {email} updated successfully",
                "user": {"email": email, "name": name, "personality": personality, "tokens": tokens}
            })
        else:
            return jsonify({"success": False, "error": "Failed to update user"}), 500
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

# Register blueprint
app.register_blueprint(admin_bp)

# Redirect root to admin
@app.route('/')
def index():
    return redirect(url_for('admin.dashboard'))

if __name__ == '__main__':
    host = os.environ.get('CONTROL_PANEL_HOST', '0.0.0.0')
    port = int(os.environ.get('CONTROL_PANEL_PORT', 5001))
    debug = os.environ.get('CONTROL_PANEL_DEBUG', 'false').lower() == 'true'
    
    print(f"Starting PocketFlow Control Panel on {host}:{port}")
    print(f"Access the control panel at: http://localhost:{port}/admin/")
    
    app.run(host=host, port=port, debug=debug) 