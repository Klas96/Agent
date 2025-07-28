#!/usr/bin/env python3
"""
Payment monitoring script for PocketFlow.

This script monitors Bitcoin payments and automatically assigns tokens to users.
Run this as a separate service to monitor payments continuously.
"""

import sys
import os
import time
import logging
from pathlib import Path

# Add the src directory to the Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from pocketflow.services.payment_monitor import PaymentMonitor
from pocketflow.config.settings import get_settings

def setup_logging():
    """Setup logging for the payment monitor."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('/opt/pocketflow/logs/payment_monitor.log')
        ]
    )

def main():
    """Main function to run the payment monitor."""
    setup_logging()
    logger = logging.getLogger(__name__)
    
    logger.info("Starting PocketFlow Payment Monitor")
    
    try:
        # Initialize the payment monitor
        monitor = PaymentMonitor()
        
        # Start monitoring with 5-minute intervals
        monitor.start_monitoring(interval_seconds=300)
        
    except KeyboardInterrupt:
        logger.info("Payment monitor stopped by user")
    except Exception as e:
        logger.error(f"Payment monitor failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 