import os
import imaplib
import email
import smtplib
import logging
import re
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from src.pocketflow.utils.logging import get_logger

logger = get_logger("email_utils")

def extract_email(sender: str) -> str:
    """
    Extract email address from sender string.
    
    Args:
        sender: String containing email address (e.g., "John Doe <john@example.com>" or "john@example.com")
        
    Returns:
        Extracted email address or original string if no email found
    """
    # Try to extract email from angle brackets format: "Name <email@domain.com>"
    match = re.search(r'<([A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,})>', sender)
    if match:
        return match.group(1)
    
    # Try to extract standalone email address
    match = re.search(r'([A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,})', sender)
    if match:
        return match.group(1)
    
    # Return original string if no email found
    return sender
