#!/usr/bin/env python3
"""
Test script to check email configuration and connectivity.
"""

import os
import sys
from pathlib import Path

# Add the src directory to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from pocketflow.config.settings import get_settings
from pocketflow.services.email_service import EmailService
from pocketflow.utils.logging import setup_logging, get_logger

def test_email_config():
    """Test email configuration and connectivity."""
    setup_logging(level="INFO", log_format="standard")
    logger = get_logger("EmailConfigTest")
    
    logger.info("=== Testing Email Configuration ===")
    
    # Get settings
    settings = get_settings()
    
    logger.info("Email Configuration:")
    logger.info(f"  EMAIL_HOST: {settings.EMAIL_HOST}")
    logger.info(f"  EMAIL_PORT: {settings.EMAIL_PORT}")
    logger.info(f"  EMAIL_USERNAME: {settings.EMAIL_USERNAME}")
    logger.info(f"  EMAIL_PASSWORD: {'*' * len(settings.EMAIL_PASSWORD) if settings.EMAIL_PASSWORD else 'NOT SET'}")
    logger.info(f"  EMAIL_USE_TLS: {settings.EMAIL_USE_TLS}")
    
    # Check if email credentials are set
    if not settings.EMAIL_USERNAME or settings.EMAIL_USERNAME == "your-email@gmail.com":
        logger.error("EMAIL_USERNAME is not properly configured!")
        logger.error("Please set EMAIL_USERNAME environment variable or update config file")
        return False
    
    if not settings.EMAIL_PASSWORD or settings.EMAIL_PASSWORD == "your-app-password":
        logger.error("EMAIL_PASSWORD is not properly configured!")
        logger.error("Please set EMAIL_PASSWORD environment variable or update config file")
        return False
    
    if not settings.EMAIL_HOST or settings.EMAIL_HOST == "smtp.gmail.com":
        logger.error("EMAIL_HOST is not properly configured!")
        logger.error("Please set EMAIL_HOST environment variable or update config file")
        return False
    
    logger.info("Email configuration appears to be set up correctly")
    
    # Test email service
    try:
        email_service = EmailService()
        logger.info("EmailService created successfully")
        
        # Test fetching emails
        logger.info("Testing email fetching...")
        emails = email_service.fetch_unread_emails()
        logger.info(f"Successfully fetched {len(emails)} unread emails")
        
        return True
        
    except Exception as e:
        logger.error(f"Email service test failed: {e}")
        return False

if __name__ == "__main__":
    success = test_email_config()
    if success:
        print("✅ Email configuration test passed")
    else:
        print("❌ Email configuration test failed")
        sys.exit(1) 