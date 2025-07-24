"""
Web interface for PocketFlow control panel.

This package provides a web-based control panel for managing users,
tokens, Bitcoin addresses, and system configuration.
"""

from .app import create_app
from .routes import admin_bp

__all__ = ["create_app", "admin_bp"] 