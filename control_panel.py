#!/usr/bin/env python3
"""
PocketFlow Control Panel Entry Point

This is the main entry point for the PocketFlow control panel web application.
It uses the centralized web app structure from src/pocketflow/web/.
"""

import os
import sys
from pathlib import Path

# Add the src directory to the Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.pocketflow.web.app import run_control_panel
from src.pocketflow.utils.logging import setup_logging, get_logger
from src.pocketflow.config.settings import get_settings


def main():
    """Main entry point for the control panel."""
    # Set up logging
    setup_logging(level="INFO", log_format="standard")
    logger = get_logger("ControlPanel")
    
    logger.info("Starting PocketFlow Control Panel...")
    
    # Get configuration from centralized settings
    settings = get_settings()
    
    # Get configuration from environment variables (fallback for backward compatibility)
    host = os.environ.get('CONTROL_PANEL_HOST', '0.0.0.0')
    port = int(os.environ.get('CONTROL_PANEL_PORT', 5001))
    debug = os.environ.get('CONTROL_PANEL_DEBUG', 'false').lower() == 'true'
    
    logger.info(f"Control Panel Configuration:")
    logger.info(f"  Host: {host}")
    logger.info(f"  Port: {port}")
    logger.info(f"  Debug: {debug}")
    logger.info(f"  Environment: {settings.ENVIRONMENT}")
    logger.info(f"  Log Level: {settings.LOG_LEVEL}")
    
    try:
        # Run the control panel using the centralized web app
        run_control_panel(host=host, port=port, debug=debug)
    except KeyboardInterrupt:
        logger.info("Control Panel stopped by user")
    except Exception as e:
        logger.error(f"Control Panel failed to start: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 