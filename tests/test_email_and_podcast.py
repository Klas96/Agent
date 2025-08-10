#!/usr/bin/env python3
"""
Comprehensive test script for email processing and podcast generation.
This script tests the full flow from email retrieval to podcast creation.
"""

import os
import sys
import imaplib
import email
from datetime import datetime

# Add the source directory to the path
sys.path.insert(0, "/opt/pocketflow/src")

def test_email_connection():
    """Test direct IMAP connection to email server."""
    print("🔧 Testing email connection...")
    
    try:
        # Load environment variables from production
        import dotenv
        dotenv.load_dotenv("/opt/pocketflow/.env")
        
        email_host = os.getenv("EMAIL_HOST")
        email_username = os.getenv("EMAIL_USERNAME") 
        email_password = os.getenv("EMAIL_PASSWORD")
        
        print(f"   Host: {email_host}")
        print(f"   Username: {email_username}")
        print(f"   Password: {'*' * len(email_password) if email_password else 'NOT SET'}")
        
        # Connect to IMAP
        mail = imaplib.IMAP4_SSL(email_host)
        mail.login(email_username, email_password)
        
        # Select inbox
        mail.select('inbox')
        
        # Search for recent emails
        status, messages = mail.search(None, 'ALL')
        if status == 'OK':
            email_count = len(messages[0].split())
            print(f"✅ Connected successfully! Found {email_count} total emails")
            
            # Check for unread emails specifically
            status, unread_messages = mail.search(None, 'UNSEEN')
            if status == 'OK':
                unread_count = len(unread_messages[0].split()) if unread_messages[0] else 0
                print(f"📧 Unread emails: {unread_count}")
                
                # Get details of recent emails
                if email_count > 0:
                    print("\n📬 Recent emails:")
                    recent_emails = messages[0].split()[-5:]  # Last 5 emails
                    
                    for email_id in recent_emails:
                        status, msg_data = mail.fetch(email_id, '(RFC822)')
                        if status == 'OK':
                            email_message = email.message_from_bytes(msg_data[0][1])
                            subject = email_message['Subject'] or 'No Subject'
                            sender = email_message['From']
                            date = email_message['Date']
                            
                            # Check if email is unread
                            status, flags = mail.fetch(email_id, '(FLAGS)')
                            is_unread = b'\\Seen' not in flags[0] if flags and flags[0] else False
                            unread_marker = " [UNREAD]" if is_unread else ""
                            
                            print(f"   ID: {email_id.decode()}{unread_marker}")
                            print(f"   From: {sender}")
                            print(f"   Subject: {subject}")
                            print(f"   Date: {date}")
                            print()
        
        mail.close()
        mail.logout()
        return True
        
    except Exception as e:
        print(f"❌ Email connection failed: {e}")
        return False

def test_email_service():
    """Test the PocketFlow EmailService."""
    print("\n🔧 Testing PocketFlow EmailService...")
    
    try:
        from pocketflow.services.email_service import EmailService
        
        service = EmailService()
        print("✅ EmailService initialized successfully")
        
        # Test fetching emails
        emails = service.fetch_unread_emails()
        print(f"📧 Fetched {len(emails)} unread emails via EmailService")
        
        for i, email_data in enumerate(emails):
            print(f"   Email {i+1}: {email_data.get('subject', 'No Subject')}")
            print(f"   From: {email_data.get('sender', 'Unknown')}")
            
        return len(emails) > 0
        
    except Exception as e:
        print(f"❌ EmailService test failed: {e}")
        import traceback
        print(f"   Traceback: {traceback.format_exc()}")
        return False

def test_podcast_tool():
    """Test the PodcastifyTool directly."""
    print("\n🔧 Testing PodcastifyTool...")
    
    try:
        from pocketflow.tools.podcastify import PodcastifyTool
        
        tool = PodcastifyTool()
        print("✅ PodcastifyTool initialized successfully")
        
        # Test podcast generation
        print("🎙️ Testing podcast generation...")
        
        test_params = {
            "topic": "Local LLMs and their applications",
            "duration_minutes": 3,  # Short test
            "style": "conversational",
            "target_audience": "general",
            "voice_preference": "professional",
            "output_format": "wav"
        }
        
        result = tool.run(**test_params)
        
        if result.success:
            print(f"✅ Podcast generated successfully!")
            print(f"   File: {result.data.get('file_path')}")
            print(f"   Duration: {result.data.get('duration')} minutes")
            
            # Check if file exists
            file_path = result.data.get('file_path')
            if file_path and os.path.exists(file_path):
                file_size = os.path.getsize(file_path)
                print(f"   File size: {file_size} bytes")
            else:
                print(f"⚠️  Audio file not found at {file_path}")
                
        else:
            print(f"❌ Podcast generation failed: {result.error}")
            
        return result.success
        
    except Exception as e:
        print(f"❌ PodcastifyTool test failed: {e}")
        import traceback
        print(f"   Traceback: {traceback.format_exc()}")
        return False

def test_llm_service():
    """Test the LLM service for content generation."""
    print("\n🔧 Testing LLM Service...")
    
    try:
        from pocketflow.services.llm_service import LLMService
        
        llm = LLMService()
        print("✅ LLMService initialized successfully")
        
        # Test a simple generation
        test_prompt = "Generate a brief podcast outline about local LLMs."
        
        response = llm.generate(test_prompt)
        print(f"✅ LLM generated response ({len(response)} characters)")
        print(f"   Preview: {response[:100]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ LLM Service test failed: {e}")
        import traceback
        print(f"   Traceback: {traceback.format_exc()}")
        return False

def test_audio_directory():
    """Test the audio output directory."""
    print("\n🔧 Testing audio output directory...")
    
    audio_dir = "/tmp/pocketflow_podcasts"
    
    try:
        # Check if directory exists and is writable
        if os.path.exists(audio_dir):
            print(f"✅ Audio directory exists: {audio_dir}")
            
            # Check permissions
            if os.access(audio_dir, os.W_OK):
                print("✅ Directory is writable")
            else:
                print("❌ Directory is not writable")
                
            # List existing files
            files = os.listdir(audio_dir)
            print(f"📁 Found {len(files)} files in audio directory")
            
            for file in files[:5]:  # Show first 5 files
                file_path = os.path.join(audio_dir, file)
                if os.path.isfile(file_path):
                    size = os.path.getsize(file_path)
                    print(f"   {file} ({size} bytes)")
                    
        else:
            print(f"❌ Audio directory does not exist: {audio_dir}")
            
        return os.path.exists(audio_dir) and os.access(audio_dir, os.W_OK)
        
    except Exception as e:
        print(f"❌ Audio directory test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("🧪 PocketFlow Email & Podcast Diagnostic Test")
    print("=" * 60)
    print(f"Time: {datetime.now().isoformat()}")
    print()
    
    results = {
        "email_connection": test_email_connection(),
        "email_service": test_email_service(), 
        "audio_directory": test_audio_directory(),
        "llm_service": test_llm_service(),
        "podcast_tool": test_podcast_tool(),
    }
    
    print("\n📊 Test Results Summary:")
    print("=" * 30)
    
    all_passed = True
    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{test_name:<20}: {status}")
        if not passed:
            all_passed = False
    
    print()
    if all_passed:
        print("🎉 All tests passed! The system should be working correctly.")
    else:
        print("⚠️  Some tests failed. Check the output above for details.")
        
    return all_passed

if __name__ == "__main__":
    main() 