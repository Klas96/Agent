#!/usr/bin/env python3
"""
PocketFlow Control Panel

A web-based control panel for managing users, tokens, Bitcoin addresses,
and system configuration for PocketFlow.
"""

import os
import sys
from pathlib import Path

# Add src to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from pocketflow.web.app import run_control_panel
from pocketflow.config.settings import get_settings
from pocketflow.utils.logging import get_logger


def main():
    """Run the PocketFlow control panel."""
    settings = get_settings()
    logger = get_logger("ControlPanel")
    
    # Get configuration
    host = os.getenv("CONTROL_PANEL_HOST", "0.0.0.0")
    port = int(os.getenv("CONTROL_PANEL_PORT", "5000"))
    debug = os.getenv("CONTROL_PANEL_DEBUG", "false").lower() == "true"
    
    logger.info(f"Starting PocketFlow Control Panel on {host}:{port}")
    logger.info(f"Debug mode: {debug}")
    
    try:
        run_control_panel(host=host, port=port, debug=debug)
    except KeyboardInterrupt:
        logger.info("Control panel stopped by user")
    except Exception as e:
        logger.error(f"Control panel error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 