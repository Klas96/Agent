#!/usr/bin/env python3
"""
Script to run the PocketFlow n8n-like workflow API server.
This script starts the Flask API server for the workflow system that builds on top of the original PocketFlow.
"""

import os
import sys
from pathlib import Path

# Add the src directory to the Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from pocketflow.web.workflow_api import workflow_app
from pocketflow.config.settings import get_settings
from pocketflow.utils.logging import setup_logging, get_logger


def main():
    """Main function to start the workflow API server."""
    setup_logging(level="INFO", log_format="standard")
    logger = get_logger("WorkflowAPI")
    settings = get_settings()
    
    logger.info("Starting PocketFlow Workflow API Server")
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    logger.info(f"Debug mode: {settings.DEBUG}")
    logger.info(f"Database URL: {settings.DATABASE_URL}")
    
    # Ensure data directory exists
    data_dir = Path("/opt/pocketflow/data")
    data_dir.mkdir(parents=True, exist_ok=True)
    logger.info(f"Data directory: {data_dir}")
    
    # Get host and port from environment or use defaults
    host = os.environ.get("HOST", "0.0.0.0")
    port = int(os.environ.get("PORT", 5000))
    
    logger.info(f"Starting server on {host}:{port}")
    logger.info("Workflow API endpoints:")
    logger.info("  GET  /api/health - Health check")
    logger.info("  GET  /api/workflows - List workflows")
    logger.info("  POST /api/workflows - Create workflow")
    logger.info("  GET  /api/nodes - List available nodes")
    logger.info("  POST /api/workflows/{id}/run - Run workflow")
    
    try:
        workflow_app.run(
            host=host,
            port=port,
            debug=settings.DEBUG,
            threaded=True
        )
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 