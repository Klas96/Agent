#!/usr/bin/env python3
"""
Test script to send an email to test the {result} variable fix.
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def send_test_email_fix():
    """Send a test email to test the {result} variable fix."""
    
    # Email settings from .env
    EMAIL_HOST = "mailcluster.loopia.se"
    EMAIL_USERNAME = "agent@klasholmgren.se"
    EMAIL_PASSWORD = "40qE7xKJuz"
    
    # Create message
    msg = MIMEMultipart()
    msg['From'] = EMAIL_USERNAME
    msg['To'] = EMAIL_USERNAME  # Send to self for testing
    msg['Subject'] = "Test {result} Variable Fix"
    
    body = """
Hello Agent,

Please calculate: 5 * 7 + 3

This should test if the {result} variable is now working correctly.

Best regards,
Test User
"""
    
    msg.attach(MIMEText(body, 'plain'))
    
    try:
        # Create SMTP session
        print(f"🔗 Connecting to {EMAIL_HOST}...")
        server = smtplib.SMTP(EMAIL_HOST, 587)
        server.starttls()
        
        # Login
        print(f"🔐 Logging in as {EMAIL_USERNAME}...")
        server.login(EMAIL_USERNAME, EMAIL_PASSWORD)
        
        # Send email
        print("📧 Sending test email...")
        text = msg.as_string()
        server.sendmail(EMAIL_USERNAME, EMAIL_USERNAME, text)
        
        # Close connection
        server.quit()
        
        print("✅ Test email sent successfully!")
        print("📬 Check the agent inbox for the email")
        print("🔧 This should test the {result} variable fix")
        return True
        
    except Exception as e:
        print(f"❌ Failed to send email: {e}")
        return False

if __name__ == "__main__":
    success = send_test_email_fix()
    if not success:
        exit(1) 