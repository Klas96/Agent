"""
Flask application factory for PocketFlow control panel.
"""

from flask import Flask, redirect, url_for
from flask_cors import CORS
import os
from pathlib import Path

from .routes import admin_bp
from ..config.settings import get_settings
from ..utils.logging import get_logger


def create_app(config_name=None):
    """Create and configure the Flask application."""
    app = Flask(__name__)
    
    # Load settings
    settings = get_settings()
    app.config.from_object(settings)
    
    # Set Flask secret key for sessions
    app.config['SECRET_KEY'] = settings.SECRET_KEY
    
    # Enable CORS for development
    CORS(app)
    
    # Configure static files
    static_folder = Path(__file__).parent / "static"
    app.static_folder = str(static_folder)
    app.static_url_path = "/static"
    
    # Register blueprints
    app.register_blueprint(admin_bp, url_prefix="/admin")
    
    # Create static directory if it doesn't exist
    static_folder.mkdir(exist_ok=True)
    
    # Root route that redirects to admin dashboard
    @app.route('/')
    def index():
        """Redirect root to admin dashboard."""
        return redirect(url_for('admin.dashboard'))
    
    logger = get_logger("WebApp")
    logger.info("PocketFlow Control Panel initialized")
    
    return app


def run_control_panel(host="0.0.0.0", port=5000, debug=False):
    """Run the control panel web application."""
    app = create_app()
    
    logger = get_logger("WebApp")
    logger.info(f"Starting PocketFlow Control Panel on {host}:{port}")
    
    app.run(host=host, port=port, debug=debug) 