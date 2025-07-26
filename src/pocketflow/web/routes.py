"""
Admin routes for PocketFlow control panel.
"""
from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from typing import Dict, Any, List, Optional
import json
from ..services import database_service
from ..core.types import User, BTCAddress, PaymentTransaction
from ..utils.logging import get_logger

admin_bp = Blueprint("admin", __name__)
logger = get_logger("AdminRoutes")

# Database connection function
def get_db_connection():
    """Get database connection."""
    import sqlite3
    from pathlib import Path
    
    # Try production database first
    db_path = Path("/opt/pocketflow/data/users.db")
    if not db_path.exists():
        # Fallback to local development database
        db_path = Path("data/users.db")
        if not db_path.exists():
            # Create local database for development
            db_path.parent.mkdir(exist_ok=True)
            conn = sqlite3.connect(str(db_path))
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
            print(f"Created local database at {db_path}")
    
    return sqlite3.connect(str(db_path))

def get_all_users() -> List[Dict[str, Any]]:
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
        logger.error(f"Error getting users: {e}")
        return []

def get_system_stats() -> Dict[str, Any]:
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
        logger.error(f"Error getting system stats: {e}")
        return {
            "total_users": 0,
            "total_tokens": 0,
            "total_payments": 0
        }

def add_user(email: str, name: Optional[str] = None, personality: Optional[str] = None, initial_tokens: int = 10, notes: str = "") -> bool:
    """Add a new user to the database."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if user already exists
        cursor.execute("SELECT email FROM users WHERE email = ?", (email,))
        if cursor.fetchone():
            logger.warning(f"User {email} already exists")
            conn.close()
            return False
        
        # Add user
        cursor.execute("""
            INSERT INTO users (email, name, personality, tokens, created_at, updated_at)
            VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
        """, (email, name, personality, initial_tokens))
        
        conn.commit()
        conn.close()
        
        logger.info(f"Successfully added user: {email} with {initial_tokens} tokens")
        return True
    except Exception as e:
        logger.error(f"Error adding user {email}: {e}")
        return False

def get_user_by_email(email: str) -> Optional[Dict[str, Any]]:
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
        logger.error(f"Error getting user {email}: {e}")
        return None

def update_user_tokens(email: str, new_tokens: int) -> bool:
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
        
        logger.info(f"Updated user {email} tokens to {new_tokens}")
        return True
    except Exception as e:
        logger.error(f"Error updating user {email}: {e}")
        return False

def update_user(email: str, name: Optional[str] = None, personality: Optional[str] = None, new_tokens: Optional[int] = None) -> bool:
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
        
        logger.info(f"Updated user {email}")
        return True
    except Exception as e:
        logger.error(f"Error updating user {email}: {e}")
        return False

def delete_user(email: str) -> bool:
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
        
        logger.info(f"Deleted user: {email}")
        return True
    except Exception as e:
        logger.error(f"Error deleting user {email}: {e}")
        return False

@admin_bp.route("/")
def dashboard():
    """Dashboard page."""
    try:
        stats = get_system_stats()
        return render_template("dashboard.html", stats=stats)
    except Exception as e:
        logger.error(f"Error in dashboard: {e}")
        return render_template("dashboard.html", stats={})

@admin_bp.route("/users")
def users_list():
    """Users list page."""
    try:
        users = get_all_users()
        return render_template("users.html", users=users)
    except Exception as e:
        logger.error(f"Error in users list: {e}")
        return render_template("users.html", users=[])

@admin_bp.route("/users/add", methods=["GET", "POST"])
def add_user_page():
    """Add user page."""
    if request.method == "POST":
        email = request.form.get("email", "").strip()
        name = request.form.get("name", "").strip() or None
        personality = request.form.get("personality", "").strip() or None
        initial_tokens = int(request.form.get("initial_tokens", 10))
        notes = request.form.get("notes", "").strip()
        
        # Validate input
        if not email:
            flash("Email is required", "error")
            return render_template("add_user.html")
        
        if initial_tokens < 0:
            flash("Initial tokens cannot be negative", "error")
            return render_template("add_user.html")
        
        # Try to add user
        if add_user(email, name, personality, initial_tokens, notes):
            flash(f"User {email} added successfully with {initial_tokens} tokens", "success")
            return redirect(url_for("admin.users_list"))
        else:
            flash(f"Failed to add user {email}. User may already exist.", "error")
            return render_template("add_user.html")
    
    return render_template("add_user.html")

@admin_bp.route("/users/<email>")
def user_detail(email):
    """User detail page."""
    try:
        user = get_user_by_email(email)
        if not user:
            flash(f"User {email} not found", "error")
            return redirect(url_for("admin.users_list"))
        
        # Get user's BTC addresses
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT address, created_at 
            FROM btc_addresses 
            WHERE email = ?
            ORDER BY created_at DESC
        """, (email,))
        btc_addresses = [{"address": row[0], "created_at": row[1]} for row in cursor.fetchall()]
        
        # Get user's payment history
        cursor.execute("""
            SELECT amount_btc, amount_usd, status, created_at 
            FROM payment_transactions 
            WHERE email = ?
            ORDER BY created_at DESC
        """, (email,))
        payments = [{
            "amount_btc": row[0], 
            "amount_usd": row[1], 
            "status": row[2], 
            "created_at": row[3]
        } for row in cursor.fetchall()]
        
        conn.close()
        
        return render_template("user_detail.html", user=user, btc_addresses=btc_addresses, payments=payments)
    except Exception as e:
        logger.error(f"Error in user detail: {e}")
        flash("Error loading user details", "error")
        return redirect(url_for("admin.users_list"))

@admin_bp.route("/users/<email>/edit", methods=["GET", "POST"])
def edit_user(email):
    """Edit user page."""
    try:
        user = get_user_by_email(email)
        if not user:
            flash(f"User {email} not found", "error")
            return redirect(url_for("admin.users_list"))
        
        if request.method == "POST":
            name = request.form.get("name", "").strip() or None
            personality = request.form.get("personality", "").strip() or None
            new_tokens = int(request.form.get("tokens", 0))
            
            if new_tokens < 0:
                flash("Tokens cannot be negative", "error")
                return render_template("edit_user.html", user=user)
            
            # Update user with new name, personality and tokens
            if update_user(email, name, personality, new_tokens):
                flash(f"User {email} updated successfully", "success")
                return redirect(url_for("admin.user_detail", email=email))
            else:
                flash(f"Failed to update user {email}", "error")
                return render_template("edit_user.html", user=user)
        
        return render_template("edit_user.html", user=user)
    except Exception as e:
        logger.error(f"Error in edit user: {e}")
        flash("Error loading user", "error")
        return redirect(url_for("admin.users_list"))

@admin_bp.route("/users/<email>/delete", methods=["POST"])
def delete_user_route(email):
    """Delete user."""
    try:
        if delete_user(email):
            flash(f"User {email} deleted successfully", "success")
        else:
            flash(f"Failed to delete user {email}", "error")
    except Exception as e:
        logger.error(f"Error deleting user {email}: {e}")
        flash("Error deleting user", "error")
    
    return redirect(url_for("admin.users_list"))



@admin_bp.route("/api/users")
def api_users():
    """API endpoint for users."""
    try:
        users = get_all_users()
        return jsonify({"success": True, "users": users})
    except Exception as e:
        logger.error(f"Error in API users: {e}")
        return jsonify({"success": False, "error": str(e)})

@admin_bp.route("/api/stats")
def api_stats():
    """API endpoint for system stats."""
    try:
        stats = get_system_stats()
        return jsonify({"success": True, "stats": stats})
    except Exception as e:
        logger.error(f"Error in API stats: {e}")
        return jsonify({"success": False, "error": str(e)})

@admin_bp.route("/api/users", methods=["POST"])
def api_add_user():
    """API endpoint for adding users."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"success": False, "error": "No data provided"})
        
        email = data.get("email", "").strip()
        name = data.get("name", "").strip() or None
        personality = data.get("personality", "").strip() or None
        initial_tokens = int(data.get("initial_tokens", 10))
        notes = data.get("notes", "").strip()
        
        if not email:
            return jsonify({"success": False, "error": "Email is required"})
        
        if initial_tokens < 0:
            return jsonify({"success": False, "error": "Initial tokens cannot be negative"})
        
        if add_user(email, name, personality, initial_tokens, notes):
            return jsonify({
                "success": True, 
                "message": f"User {email} added successfully",
                "user": {"email": email, "name": name, "personality": personality, "tokens": initial_tokens}
            })
        else:
            return jsonify({"success": False, "error": f"Failed to add user {email}"})
    
    except Exception as e:
        logger.error(f"Error in API add user: {e}")
        return jsonify({"success": False, "error": str(e)})

@admin_bp.route("/api/users/<email>", methods=["GET"])
def api_get_user(email):
    """Get user details by email."""
    try:
        user = get_user_by_email(email)
        if user:
            return jsonify({
                "success": True,
                "user": user
            })
        else:
            return jsonify({
                "success": False,
                "error": "User not found"
            }), 404
    except Exception as e:
        logger.error(f"Error getting user {email}: {e}")
        return jsonify({
            "success": False,
            "error": "Failed to get user details"
        }), 500

@admin_bp.route("/api/users/<email>", methods=["DELETE"])
def api_delete_user(email):
    """API endpoint for deleting users."""
    try:
        if delete_user(email):
            return jsonify({"success": True, "message": f"User {email} deleted successfully"})
        else:
            return jsonify({"success": False, "error": "Failed to delete user"})
    except Exception as e:
        logger.error(f"Error in API delete user: {e}")
        return jsonify({"success": False, "error": str(e)})

@admin_bp.route("/api/users/<email>", methods=["PUT"])
def api_update_user(email):
    """API endpoint for updating users."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"success": False, "error": "No data provided"})
        
        name = data.get("name", "").strip() or None
        personality = data.get("personality", "").strip() or None
        tokens = int(data.get("tokens", 10))
        
        if tokens < 0:
            return jsonify({"success": False, "error": "Tokens cannot be negative"})
        
        if update_user(email, name, personality, tokens):
            return jsonify({
                "success": True,
                "message": f"User {email} updated successfully",
                "user": {"email": email, "name": name, "personality": personality, "tokens": tokens}
            })
        else:
            return jsonify({"success": False, "error": "Failed to update user"})
    
    except Exception as e:
        logger.error(f"Error in API update user: {e}")
        return jsonify({"success": False, "error": str(e)}) 