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

from flask import Flask, render_template, request, jsonify, Blueprint, redirect
from flask_cors import CORS
import sqlite3
from datetime import datetime
import json

# Create Flask app
app = Flask(__name__)
CORS(app)

# Configure static files
static_folder = Path(__file__).parent / "src" / "pocketflow" / "web" / "static"
app.static_folder = str(static_folder)
app.static_url_path = "/static"

# Create static directory if it doesn't exist
static_folder.mkdir(exist_ok=True)

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
        
        # Create greenlist table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS greenlist (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email_or_domain TEXT NOT NULL UNIQUE,
            type TEXT NOT NULL CHECK(type IN ('email', 'domain')),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        conn.commit()
        conn.close()
        print(f"Created local database at {DB_PATH}")

def get_db_connection():
    """Get database connection."""
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn

def get_all_users():
    """Get all users from database."""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users ORDER BY created_at DESC")
        users = cursor.fetchall()
        return [dict(user) for user in users]
    finally:
        conn.close()

def get_system_stats():
    """Get system statistics."""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        
        # Count users
        cursor.execute("SELECT COUNT(*) as count FROM users")
        total_users = cursor.fetchone()['count']
        
        # Sum tokens
        cursor.execute("SELECT SUM(tokens) as total FROM users")
        result = cursor.fetchone()
        total_tokens = result['total'] or 0
        
        # Count payments
        cursor.execute("SELECT COUNT(*) as count FROM payment_transactions")
        total_payments = cursor.fetchone()['count']
        
        # Count greenlist entries
        cursor.execute("SELECT COUNT(*) as count FROM greenlist")
        greenlist_count = cursor.fetchone()['count']
        
        return {
            "total_users": total_users,
            "total_tokens": total_tokens,
            "total_payments": total_payments,
            "greenlist_emails": greenlist_count,
            "greenlist_domains": 0  # Placeholder
        }
    finally:
        conn.close()

# Routes
@app.route('/')
def index():
    """Redirect to admin dashboard."""
    return redirect('/admin/')

@app.route('/admin/')
def dashboard():
    """Admin dashboard."""
    stats = get_system_stats()
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>PocketFlow Control Panel</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
        <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    </head>
    <body>
        <div class="container-fluid">
            <div class="row">
                <nav class="col-md-3 col-lg-2 d-md-block bg-dark sidebar">
                    <div class="position-sticky pt-3">
                        <div class="text-center mb-4">
                            <h4 class="text-white"><i class="fas fa-cogs"></i> PocketFlow</h4>
                            <small class="text-light">Control Panel</small>
                        </div>
                        <ul class="nav flex-column">
                            <li class="nav-item">
                                <a class="nav-link text-light" href="/admin/">
                                    <i class="fas fa-tachometer-alt"></i> Dashboard
                                </a>
                            </li>
                            <li class="nav-item">
                                <a class="nav-link text-light" href="/admin/users">
                                    <i class="fas fa-users"></i> Users
                                </a>
                            </li>
                        </ul>
                    </div>
                </nav>
                
                <main class="col-md-9 ms-sm-auto col-lg-10 px-md-4">
                    <div class="d-flex justify-content-between flex-wrap flex-md-nowrap align-items-center pt-3 pb-2 mb-3 border-bottom">
                        <h1 class="h2">Dashboard</h1>
                    </div>
                    
                    <div class="row">
                        <div class="col-md-3">
                            <div class="card bg-primary text-white">
                                <div class="card-body">
                                    <h3>{stats['total_users']}</h3>
                                    <p>Total Users</p>
                                </div>
                            </div>
                        </div>
                        <div class="col-md-3">
                            <div class="card bg-success text-white">
                                <div class="card-body">
                                    <h3>{stats['total_tokens']}</h3>
                                    <p>Total Tokens</p>
                                </div>
                            </div>
                        </div>
                        <div class="col-md-3">
                            <div class="card bg-info text-white">
                                <div class="card-body">
                                    <h3>{stats['total_payments']}</h3>
                                    <p>Total Payments</p>
                                </div>
                            </div>
                        </div>
                        <div class="col-md-3">
                            <div class="card bg-warning text-white">
                                <div class="card-body">
                                    <h3>{stats['greenlist_emails']}</h3>
                                    <p>Greenlist Entries</p>
                                </div>
                            </div>
                        </div>
                    </div>
                    
                    <div class="row mt-4">
                        <div class="col-12">
                            <div class="card">
                                <div class="card-header">
                                    <h5><i class="fas fa-info-circle"></i> System Status</h5>
                                </div>
                                <div class="card-body">
                                    <p><i class="fas fa-check text-success"></i> Database: Connected</p>
                                    <p><i class="fas fa-check text-success"></i> Control Panel: Running</p>
                                    <p><i class="fas fa-check text-success"></i> PocketFlow: Active</p>
                                </div>
                            </div>
                        </div>
                    </div>
                </main>
            </div>
        </div>
        
        <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    </body>
    </html>
    """

@app.route('/admin/users')
def users():
    """User management page."""
    users = get_all_users()
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Users - PocketFlow Control Panel</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
        <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    </head>
    <body>
        <div class="container-fluid">
            <div class="row">
                <nav class="col-md-3 col-lg-2 d-md-block bg-dark sidebar">
                    <div class="position-sticky pt-3">
                        <div class="text-center mb-4">
                            <h4 class="text-white"><i class="fas fa-cogs"></i> PocketFlow</h4>
                            <small class="text-light">Control Panel</small>
                        </div>
                        <ul class="nav flex-column">
                            <li class="nav-item">
                                <a class="nav-link text-light" href="/admin/">
                                    <i class="fas fa-tachometer-alt"></i> Dashboard
                                </a>
                            </li>
                            <li class="nav-item">
                                <a class="nav-link text-light active" href="/admin/users">
                                    <i class="fas fa-users"></i> Users
                                </a>
                            </li>
                        </ul>
                    </div>
                </nav>
                
                <main class="col-md-9 ms-sm-auto col-lg-10 px-md-4">
                    <div class="d-flex justify-content-between flex-wrap flex-md-nowrap align-items-center pt-3 pb-2 mb-3 border-bottom">
                        <h1 class="h2">User Management</h1>
                        <button class="btn btn-primary" onclick="addUser()">
                            <i class="fas fa-user-plus"></i> Add User
                        </button>
                    </div>
                    
                    <div class="card">
                        <div class="card-header">
                            <h5><i class="fas fa-users"></i> Users</h5>
                        </div>
                        <div class="card-body">
                            <div class="table-responsive">
                                <table class="table table-hover">
                                    <thead>
                                        <tr>
                                            <th>Email</th>
                                            <th>Tokens</th>
                                            <th>Created</th>
                                            <th>Updated</th>
                                            <th>Status</th>
                                            <th>Actions</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        {''.join([f'''
                                        <tr>
                                            <td><strong>{user['email']}</strong></td>
                                            <td><span class="badge bg-{'success' if user['tokens'] > 0 else 'danger'}">{user['tokens']} tokens</span></td>
                                            <td>{user['created_at']}</td>
                                            <td>{user['updated_at']}</td>
                                            <td><span class="badge bg-{'success' if user['tokens'] > 0 else 'warning'}">{'Active' if user['tokens'] > 0 else 'Tokenless'}</span></td>
                                            <td>
                                                <div class="btn-group" role="group">
                                                    <button class="btn btn-sm btn-outline-primary" onclick="viewUser('{user['email']}')">
                                                        <i class="fas fa-eye"></i>
                                                    </button>
                                                    <button class="btn btn-sm btn-outline-warning" onclick="editUser('{user['email']}', {user['tokens']})">
                                                        <i class="fas fa-edit"></i>
                                                    </button>
                                                </div>
                                            </td>
                                        </tr>
                                        ''' for user in users]) if users else '''
                                        <tr>
                                            <td colspan="6" class="text-center text-muted">
                                                <i class="fas fa-info-circle"></i> No users found
                                            </td>
                                        </tr>
                                        '''}
                                    </tbody>
                                </table>
                            </div>
                        </div>
                    </div>
                </main>
            </div>
        </div>
        
        <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
        <script>
        function addUser() {{
            alert('Add user functionality coming soon!');
        }}
        
        function viewUser(email) {{
            alert('View user: ' + email);
        }}
        
        function editUser(email, tokens) {{
            alert('Edit user: ' + email + ' (tokens: ' + tokens + ')');
        }}
        </script>
    </body>
    </html>
    """

@app.route('/admin/api/users')
def api_users():
    """API endpoint for users."""
    users = get_all_users()
    return jsonify({"success": True, "users": users})

@app.route('/admin/api/stats')
def api_stats():
    """API endpoint for system statistics."""
    stats = get_system_stats()
    return jsonify({"success": True, "stats": stats})

def main():
    """Run the control panel."""
    host = os.getenv("CONTROL_PANEL_HOST", "0.0.0.0")
    port = int(os.getenv("CONTROL_PANEL_PORT", "5000"))
    debug = os.getenv("CONTROL_PANEL_DEBUG", "false").lower() == "true"
    
    print(f"Starting PocketFlow Control Panel on {host}:{port}")
    print(f"Access the control panel at: http://localhost:{port}/admin/")
    
    app.run(host=host, port=port, debug=debug)

if __name__ == "__main__":
    main() 