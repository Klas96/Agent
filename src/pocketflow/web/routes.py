"""
Admin routes for PocketFlow control panel.
"""
from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from typing import Dict, Any, List, Optional
import json
from datetime import datetime, timedelta
from ..services import database_service
from ..core.types import User, BTCAddress, DonationTransaction
from ..utils.logging import get_logger

admin_bp = Blueprint("admin", __name__)
logger = get_logger("AdminRoutes")

# Global error tracking (in production, use Redis or database)
_recent_errors = []
_max_errors = 50

def add_error(error_type: str, message: str, details: str = None, severity: str = "error"):
    """Add an error to the recent errors list."""
    global _recent_errors
    
    error_entry = {
        "timestamp": datetime.now().isoformat(),
        "type": error_type,
        "message": message,
        "details": details,
        "severity": severity
    }
    
    _recent_errors.append(error_entry)
    
    # Keep only the most recent errors
    if len(_recent_errors) > _max_errors:
        _recent_errors = _recent_errors[-_max_errors:]
    
    logger.error(f"Dashboard Error: {error_type} - {message}")

def get_recent_errors(hours: int = 24) -> List[Dict[str, Any]]:
    """Get recent errors from the last N hours."""
    global _recent_errors
    
    cutoff_time = datetime.now() - timedelta(hours=hours)
    
    recent_errors = []
    for error in reversed(_recent_errors):  # Most recent first
        try:
            error_time = datetime.fromisoformat(error["timestamp"])
            if error_time >= cutoff_time:
                recent_errors.append(error)
        except:
            # If timestamp parsing fails, include it anyway
            recent_errors.append(error)
    
    return recent_errors

def get_system_health() -> Dict[str, Any]:
    """Get real system health status."""
    health_status = {
        "database": {"status": "unknown", "last_check": None, "error": None},
        "email_service": {"status": "unknown", "last_check": None, "error": None},
        "llm_service": {"status": "unknown", "last_check": None, "error": None},

    }
    
    try:
        # Check database
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        cursor.fetchone()
        conn.close()
        health_status["database"]["status"] = "connected"
        health_status["database"]["last_check"] = datetime.now().isoformat()
    except Exception as e:
        health_status["database"]["status"] = "disconnected"
        health_status["database"]["error"] = str(e)
        health_status["database"]["last_check"] = datetime.now().isoformat()
        add_error("database", f"Database connection failed: {e}")
    
    try:
        # Check email service (basic check)
        from ..services.email_service import EmailService
        from ..config.settings import get_settings
        settings = get_settings()
        email_service = EmailService(settings)
        # Try to get IMAP connection
        imap_server = email_service._get_imap_server()
        if imap_server:
            health_status["email_service"]["status"] = "active"
            health_status["email_service"]["last_check"] = datetime.now().isoformat()
    except Exception as e:
        health_status["email_service"]["status"] = "inactive"
        health_status["email_service"]["error"] = str(e)
        health_status["email_service"]["last_check"] = datetime.now().isoformat()
        add_error("email_service", f"Email service check failed: {e}")
    
    try:
        # Check LLM service
        from ..services.llm_service import LLMService
        llm_service = LLMService()
        # Try a simple test call
        test_response = llm_service.call_llm([{"role": "user", "content": "test"}])
        if test_response:
            health_status["llm_service"]["status"] = "ready"
            health_status["llm_service"]["last_check"] = datetime.now().isoformat()
    except Exception as e:
        health_status["llm_service"]["status"] = "unavailable"
        health_status["llm_service"]["error"] = str(e)
        health_status["llm_service"]["last_check"] = datetime.now().isoformat()
        add_error("llm_service", f"LLM service check failed: {e}")
    
    
    return health_status

# Database connection function
def get_db_connection():
    """Get database connection."""
    import sqlite3
    from pathlib import Path
    
    # Use the same database as the main application
    db_path = Path("/opt/pocketflow/data/pocketflow.db")
    if not db_path.exists():
        # Fallback to local development database
        db_path = Path("data/pocketflow.db")
        if not db_path.exists():
            # Create local database for development
            db_path.parent.mkdir(exist_ok=True)
            conn = sqlite3.connect(str(db_path))
            cursor = conn.cursor()
            
            # Create users table
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                email TEXT PRIMARY KEY,
                name TEXT,
                personality TEXT,
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
    """Get all users."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT email, name, personality, created_at, updated_at
            FROM users
            ORDER BY created_at DESC
        """)
        rows = cursor.fetchall()
        conn.close()
        
        users = []
        for row in rows:
            users.append({
                "email": row[0],
                "name": row[1],
                "personality": row[2],
                "created_at": row[3],
                "updated_at": row[4]
            })
        
        return users
    except Exception as e:
        logger.error(f"Error getting all users: {e}")
        return []


def get_system_stats() -> Dict[str, Any]:
    """Get system statistics."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get total users
        cursor.execute("SELECT COUNT(*) FROM users")
        total_users = cursor.fetchone()[0]
        
        # Get total payments
        cursor.execute("SELECT COUNT(*) FROM payment_transactions")
        total_payments = cursor.fetchone()[0]
        
        # Get total BTC received
        cursor.execute("SELECT COALESCE(SUM(amount_btc), 0) as total FROM payment_transactions")
        total_btc = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            "total_users": total_users,
            "total_payments": total_payments,
            "total_btc": total_btc,
            "status": "operational"
        }
    except Exception as e:
        logger.error(f"Error getting system stats: {e}")
        return {
            "total_users": 0,
            "total_payments": 0,
            "total_btc": 0,
            "status": "error"
        }


def add_user(email: str, name: Optional[str] = None, personality: Optional[str] = None, notes: str = "") -> bool:
    """Add a new user."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO users (email, name, personality, created_at, updated_at)
            VALUES (?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
        """, (email, name, personality))
        
        conn.commit()
        conn.close()
        
        logger.info(f"Successfully added user: {email}")
        return True
    except Exception as e:
        logger.error(f"Error adding user {email}: {e}")
        return False


def update_user(email: str, name: Optional[str] = None, personality: Optional[str] = None) -> bool:
    """Update user name and/or personality."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        if name is not None and personality is not None:
            cursor.execute("""
                UPDATE users 
                SET name = ?, personality = ?, updated_at = CURRENT_TIMESTAMP
                WHERE email = ?
            """, (name, personality, email))
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
        else:
            conn.close()
            return False
        
        conn.commit()
        conn.close()
        
        logger.info(f"Successfully updated user: {email}")
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
        health_status = get_system_health()
        recent_errors = get_recent_errors()
        return render_template("dashboard.html", stats=stats, health_status=health_status, recent_errors=recent_errors)
    except Exception as e:
        logger.error(f"Error in dashboard: {e}")
        add_error("dashboard", f"Dashboard failed to load: {e}")
        return render_template("dashboard.html", stats={}, health_status={}, recent_errors=[])

@admin_bp.route("/users")
def users_list():
    """Users list page."""
    try:
        users = get_all_users()
        return render_template("users.html", users=users)
    except Exception as e:
        logger.error(f"Error in users list: {e}")
        add_error("users", f"Failed to load users list: {e}")
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
        if add_user(email, name, personality, notes):
            flash(f"User {email} added successfully with {initial_tokens} tokens", "success")
            return redirect(url_for("admin.users_list"))
        else:
            error_msg = f"Failed to add user {email}. User may already exist."
            flash(error_msg, "error")
            add_error("user_management", error_msg, f"Email: {email}, Tokens: {initial_tokens}")
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
        add_error("user_detail", f"Failed to load user details for {email}: {e}")
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
            print(f"DEBUG: POST request to edit_user for {email}")
            print(f"DEBUG: Content-Type: {request.content_type}")
            print(f"DEBUG: is_json: {request.is_json}")
            print(f"DEBUG: form data: {dict(request.form)}")
            
            # Handle both JSON and form data
            if request.is_json:
                data = request.get_json()
                print(f"DEBUG: JSON data: {data}")
                name = data.get("name", "").strip() or None
                personality = data.get("personality", "").strip() or None
                new_tokens = int(data.get("tokens", 0))
            else:
                name = request.form.get("name", "").strip() or None
                personality = request.form.get("personality", "").strip() or None
                new_tokens = int(request.form.get("tokens", 0))
            
            print(f"DEBUG: Parsed data - name: {name}, personality: {personality}, tokens: {new_tokens}")
            
            if new_tokens < 0:
                if request.is_json:
                    return jsonify({"success": False, "error": "Tokens cannot be negative"})
                else:
                    flash("Tokens cannot be negative", "error")
                    return render_template("edit_user.html", user=user)
            
            # Update user with new name, personality and tokens
            print(f"DEBUG: Calling update_user with email={email}, name={name}, personality={personality}, tokens={new_tokens}")
            if update_user(email, name, personality):
                if request.is_json:
                    return jsonify({
                        "success": True,
                        "message": f"User {email} updated successfully",
                        "user": {"email": email, "name": name, "personality": personality, "tokens": new_tokens}
                    })
                else:
                    flash(f"User {email} updated successfully", "success")
                    return redirect(url_for("admin.user_detail", email=email))
            else:
                error_msg = f"Failed to update user {email}"
                add_error("user_management", error_msg, f"Email: {email}, New tokens: {new_tokens}")
                if request.is_json:
                    return jsonify({"success": False, "error": error_msg})
                else:
                    flash(error_msg, "error")
                    return render_template("edit_user.html", user=user)
        
        return render_template("edit_user.html", user=user)
    except Exception as e:
        logger.error(f"Error in edit user: {e}")
        add_error("user_edit", f"Failed to edit user {email}: {e}")
        if request.is_json:
            return jsonify({"success": False, "error": str(e)})
        else:
            flash("Error loading user", "error")
            return redirect(url_for("admin.users_list"))

@admin_bp.route("/users/<email>/delete", methods=["POST"])
def delete_user_route(email):
    """Delete user."""
    try:
        if delete_user(email):
            flash(f"User {email} deleted successfully", "success")
        else:
            error_msg = f"Failed to delete user {email}"
            flash(error_msg, "error")
            add_error("user_management", error_msg, f"Email: {email}")
    except Exception as e:
        logger.error(f"Error deleting user {email}: {e}")
        add_error("user_delete", f"Failed to delete user {email}: {e}")
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
        add_error("api", f"API users endpoint failed: {e}")
        return jsonify({"success": False, "error": str(e)})

@admin_bp.route("/api/stats")
def api_stats():
    """API endpoint for system stats."""
    try:
        stats = get_system_stats()
        return jsonify({"success": True, "stats": stats})
    except Exception as e:
        logger.error(f"Error in API stats: {e}")
        add_error("api", f"API stats endpoint failed: {e}")
        return jsonify({"success": False, "error": str(e)})

@admin_bp.route("/api/health")
def api_health():
    """API endpoint for system health."""
    try:
        health_status = get_system_health()
        return jsonify({"success": True, "health": health_status})
    except Exception as e:
        logger.error(f"Error in API health: {e}")
        add_error("api", f"API health endpoint failed: {e}")
        return jsonify({"success": False, "error": str(e)})


@admin_bp.route("/api/errors")
def api_errors():
    """API endpoint for recent errors."""
    try:
        hours = request.args.get("hours", 24, type=int)
        errors = get_recent_errors(hours)
        return jsonify({"success": True, "errors": errors})
    except Exception as e:
        logger.error(f"Error in API errors: {e}")
        add_error("api", f"API errors endpoint failed: {e}")
        return jsonify({"success": False, "error": str(e)})

@admin_bp.route("/api/errors", methods=["POST"])
def api_add_error():
    """API endpoint for adding errors."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"success": False, "error": "No data provided"})
        
        error_type = data.get("type", "unknown")
        message = data.get("message", "Unknown error")
        details = data.get("details")
        severity = data.get("severity", "error")
        
        add_error(error_type, message, details, severity)
        return jsonify({"success": True, "message": "Error logged successfully"})
    except Exception as e:
        logger.error(f"Error in API add error: {e}")
        add_error("api", f"API add error endpoint failed: {e}")
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
        
        if add_user(email, name, personality, notes):
            return jsonify({
                "success": True, 
                "message": f"User {email} added successfully",
                "user": {"email": email, "name": name, "personality": personality, "tokens": initial_tokens}
            })
        else:
            error_msg = f"Failed to add user {email}"
            add_error("api", error_msg, f"Email: {email}, Tokens: {initial_tokens}")
            return jsonify({"success": False, "error": error_msg})
    
    except Exception as e:
        logger.error(f"Error in API add user: {e}")
        add_error("api", f"API add user endpoint failed: {e}")
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
            add_error("api", f"User not found: {email}")
            return jsonify({
                "success": False,
                "error": "User not found"
            }), 404
    except Exception as e:
        logger.error(f"Error getting user {email}: {e}")
        add_error("api", f"API get user endpoint failed for {email}: {e}")
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
            error_msg = f"Failed to delete user {email}"
            add_error("api", error_msg)
            return jsonify({"success": False, "error": error_msg})
    except Exception as e:
        logger.error(f"Error in API delete user: {e}")
        add_error("api", f"API delete user endpoint failed for {email}: {e}")
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
        
        if update_user(email, name, personality):
            return jsonify({
                "success": True,
                "message": f"User {email} updated successfully",
                "user": {"email": email, "name": name, "personality": personality, "tokens": tokens}
            })
        else:
            error_msg = f"Failed to update user {email}"
            add_error("api", error_msg, f"Email: {email}, Tokens: {tokens}")
            return jsonify({"success": False, "error": error_msg})
    
    except Exception as e:
        logger.error(f"Error in API update user: {e}")
        add_error("api", f"API update user endpoint failed for {email}: {e}")
        return jsonify({"success": False, "error": str(e)}) 