#!/usr/bin/env python3
"""
Test script to send an email from an external address to test the agent.
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def send_test_email_external():
    """Send a test email from an external address."""
    
    # Use Gmail SMTP for sending (you'll need to enable app passwords)
    # For now, let's just simulate what would happen
    
    print("📧 To test the agent properly, you need to:")
    print("1. Send an email from a different email address (not agent@klasholmgren.se)")
    print("2. Send it to: agent@klasholmgren.se")
    print("3. The agent should then process it and respond")
    print("")
    print("🔍 Current issue: When sending to the same address, emails are marked as read automatically")
    print("")
    print("💡 Alternative solutions:")
    print("1. Send from a different email address")
    print("2. Modify the service to process recent emails instead of just unread ones")
    print("3. Check email server settings for auto-read behavior")
    
    return True

if __name__ == "__main__":
    send_test_email_external() 