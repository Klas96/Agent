#!/usr/bin/env python3
"""
Final test to verify the {result} variable fix.
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def send_final_test():
    """Send a final test email to verify the fix."""
    
    # Email settings from .env
    EMAIL_HOST = "mailcluster.loopia.se"
    EMAIL_USERNAME = "agent@klasholmgren.se"
    EMAIL_PASSWORD = "40qE7xKJuz"
    
    # Create message
    msg = MIMEMultipart()
    msg['From'] = EMAIL_USERNAME
    msg['To'] = EMAIL_USERNAME  # Send to self for testing
    msg['Subject'] = "Final Test - Calculate 10 + 20"
    
    body = """
Hello Agent,

Please calculate: 10 + 20

This is the final test to verify that the {result} variable fix is working.

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
        print("📧 Sending final test email...")
        text = msg.as_string()
        server.sendmail(EMAIL_USERNAME, EMAIL_USERNAME, text)
        
        # Close connection
        server.quit()
        
        print("✅ Final test email sent successfully!")
        print("📬 The agent should now process this and show the actual result (30) instead of {result}")
        return True
        
    except Exception as e:
        print(f"❌ Failed to send email: {e}")
        return False

if __name__ == "__main__":
    success = send_final_test()
    if not success:
        exit(1) 