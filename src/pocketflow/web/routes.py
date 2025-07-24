"""
Admin routes for PocketFlow control panel.
"""

from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from typing import Dict, Any, List, Optional
import json

from ..services.database_service import database_service
from ..core.types import User, BTCAddress, PaymentTransaction
from ..utils.logging import get_logger

admin_bp = Blueprint("admin", __name__)
logger = get_logger("AdminRoutes")


@admin_bp.route("/")
def dashboard():
    """Admin dashboard."""
    try:
        # Get system statistics
        stats = _get_system_stats()
        return render_template("dashboard.html", stats=stats)
    except Exception as e:
        logger.error(f"Dashboard error: {e}")
        return render_template("error.html", error=str(e))


@admin_bp.route("/users")
def users():
    """User management page."""
    try:
        users = _get_all_users()
        return render_template("users.html", users=users)
    except Exception as e:
        logger.error(f"Users page error: {e}")
        return render_template("error.html", error=str(e))


@admin_bp.route("/users/add", methods=["GET", "POST"])
def add_user():
    """Add new user."""
    if request.method == "POST":
        try:
            data = request.get_json()
            email = data.get("email")
            tokens = data.get("tokens", 10)
            
            if not email:
                return jsonify({"success": False, "error": "Email is required"})
            
            # Create user
            user = database_service.create_user(email, tokens)
            
            logger.info(f"Created user: {email} with {tokens} tokens")
            return jsonify({"success": True, "user": user.dict()})
            
        except Exception as e:
            logger.error(f"Add user error: {e}")
            return jsonify({"success": False, "error": str(e)})
    
    return render_template("add_user.html")


@admin_bp.route("/users/<email>")
def user_detail(email):
    """User detail page."""
    try:
        user = database_service.get_user(email)
        if not user:
            return render_template("error.html", error="User not found")
        
        btc_addresses = database_service.get_btc_addresses(email)
        payments = _get_user_payments(email)
        
        return render_template("user_detail.html", 
                            user=user, 
                            btc_addresses=btc_addresses,
                            payments=payments)
    except Exception as e:
        logger.error(f"User detail error: {e}")
        return render_template("error.html", error=str(e))


@admin_bp.route("/users/<email>/edit", methods=["POST"])
def edit_user(email):
    """Edit user."""
    try:
        data = request.get_json()
        tokens = data.get("tokens")
        
        if tokens is None:
            return jsonify({"success": False, "error": "Tokens field is required"})
        
        # Update user tokens
        current_user = database_service.get_user(email)
        if not current_user:
            return jsonify({"success": False, "error": "User not found"})
        
        # Calculate token difference
        token_diff = tokens - current_user.tokens
        
        if token_diff > 0:
            database_service.add_tokens(email, token_diff)
        elif token_diff < 0:
            # For safety, we don't allow negative token changes via web
            return jsonify({"success": False, "error": "Cannot reduce tokens via web interface"})
        
        updated_user = database_service.get_user(email)
        logger.info(f"Updated user {email}: {tokens} tokens")
        
        return jsonify({"success": True, "user": updated_user.dict()})
        
    except Exception as e:
        logger.error(f"Edit user error: {e}")
        return jsonify({"success": False, "error": str(e)})


@admin_bp.route("/users/<email>/delete", methods=["POST"])
def delete_user(email):
    """Delete user."""
    try:
        # Note: This is a placeholder - implement actual deletion
        # For safety, we might want to just deactivate users instead
        return jsonify({"success": False, "error": "User deletion not implemented for safety"})
        
    except Exception as e:
        logger.error(f"Delete user error: {e}")
        return jsonify({"success": False, "error": str(e)})


@admin_bp.route("/greenlist")
def greenlist():
    """Greenlist management page."""
    try:
        greenlist_emails = _get_greenlist_emails()
        greenlist_domains = _get_greenlist_domains()
        
        return render_template("greenlist.html", 
                            emails=greenlist_emails,
                            domains=greenlist_domains)
    except Exception as e:
        logger.error(f"Greenlist page error: {e}")
        return render_template("error.html", error=str(e))


@admin_bp.route("/greenlist/add", methods=["POST"])
def add_greenlist():
    """Add to greenlist."""
    try:
        data = request.get_json()
        email = data.get("email")
        domain = data.get("domain")
        
        if email:
            success = database_service.add_greenlist_email(email)
        elif domain:
            success = database_service.add_greenlist_domain(domain)
        else:
            return jsonify({"success": False, "error": "Email or domain is required"})
        
        if success:
            logger.info(f"Added to greenlist: {email or domain}")
            return jsonify({"success": True})
        else:
            return jsonify({"success": False, "error": "Failed to add to greenlist"})
            
    except Exception as e:
        logger.error(f"Add greenlist error: {e}")
        return jsonify({"success": False, "error": str(e)})


@admin_bp.route("/api/users")
def api_users():
    """API endpoint for users."""
    try:
        users = _get_all_users()
        return jsonify({"success": True, "users": [user.dict() for user in users]})
    except Exception as e:
        logger.error(f"API users error: {e}")
        return jsonify({"success": False, "error": str(e)})


@admin_bp.route("/api/stats")
def api_stats():
    """API endpoint for system statistics."""
    try:
        stats = _get_system_stats()
        return jsonify({"success": True, "stats": stats})
    except Exception as e:
        logger.error(f"API stats error: {e}")
        return jsonify({"success": False, "error": str(e)})


def _get_all_users() -> List[User]:
    """Get all users from database."""
    # This is a placeholder - implement actual user listing
    # For now, return empty list
    return []


def _get_system_stats() -> Dict[str, Any]:
    """Get system statistics."""
    try:
        # Placeholder stats - implement actual statistics
        stats = {
            "total_users": 0,
            "total_tokens": 0,
            "total_payments": 0,
            "greenlist_emails": 0,
            "greenlist_domains": 0
        }
        return stats
    except Exception as e:
        logger.error(f"Stats error: {e}")
        return {}


def _get_user_payments(email: str) -> List[Dict[str, Any]]:
    """Get user payment history."""
    # Placeholder - implement actual payment history
    return []


def _get_greenlist_emails() -> List[str]:
    """Get all greenlisted emails."""
    # Placeholder - implement actual greenlist query
    return []


def _get_greenlist_domains() -> List[str]:
    """Get all greenlisted domains."""
    # Placeholder - implement actual greenlist query
    return [] 