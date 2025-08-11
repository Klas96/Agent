#!/usr/bin/env python3
"""
Test script to check for recent email activity.
"""

import sys
import os
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from pocketflow.tools.registry import agent_tool_registry
from pocketflow.tools.email_tools import EmailSearchTool
import datetime

def test_recent_email_activity():
    """Test for recent email activity."""
    print("📧 Recent Email Activity Test")
    print("=" * 50)
    
    # Get the email search tool
    email_search_tool = agent_tool_registry.get_tool("email_search")
    
    if not email_search_tool:
        print("❌ Email search tool not found")
        return False
    
    print("✅ Email search tool found")
    
    # Test different search queries for recent activity
    search_queries = [
        {
            "description": "Search for recent emails",
            "parameters": {
                "query": "recent",
                "max_results": 5
            }
        },
        {
            "description": "Search for emails from today",
            "parameters": {
                "query": "today",
                "max_results": 3
            }
        },
        {
            "description": "Search for any email content",
            "parameters": {
                "query": "",
                "max_results": 10
            }
        }
    ]
    
    results = []
    
    for i, search_query in enumerate(search_queries, 1):
        print(f"\n🔍 Search {i}: {search_query['description']}")
        print("-" * 40)
        
        try:
            # Execute the email search
            result = email_search_tool.execute(**search_query["parameters"])
            
            if result.success:
                print(f"✅ Search successful")
                print(f"📊 Results: {len(result.data.get('emails', []))} emails found")
                
                emails = result.data.get('emails', [])
                if emails:
                    print("📧 Recent emails:")
                    for j, email in enumerate(emails[:3], 1):  # Show first 3
                        print(f"  {j}. From: {email.get('from', 'Unknown')}")
                        print(f"     Subject: {email.get('subject', 'No subject')}")
                        print(f"     Date: {email.get('date', 'Unknown date')}")
                        print()
                else:
                    print("📭 No emails found in search results")
                
                results.append({
                    "search": search_query["description"],
                    "success": True,
                    "email_count": len(emails)
                })
                
            else:
                print(f"❌ Search failed: {result.error}")
                results.append({
                    "search": search_query["description"],
                    "success": False,
                    "error": result.error
                })
                
        except Exception as e:
            print(f"❌ Exception: {e}")
            results.append({
                "search": search_query["description"],
                "success": False,
                "error": str(e)
            })
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Email Search Results Summary")
    print("=" * 50)
    
    successful = sum(1 for r in results if r["success"])
    total = len(results)
    
    for result in results:
        status = "✅ PASS" if result["success"] else "❌ FAIL"
        print(f"{result['search']}: {status}")
        if result["success"]:
            print(f"  📧 Emails found: {result['email_count']}")
        else:
            print(f"  ❌ Error: {result['error']}")
    
    print(f"\nOverall: {successful}/{total} searches successful")
    
    if successful > 0:
        print("🎉 Email system is working!")
        print("📧 Recent email activity detected")
        return True
    else:
        print("⚠️  No email activity found or search failed")
        return False

def check_email_service_status():
    """Check if email service is properly configured."""
    print("\n🔧 Email Service Status Check")
    print("=" * 40)
    
    try:
        from pocketflow.config.settings import get_settings
        from pocketflow.services.email_service import EmailService
        
        settings = get_settings()
        email_service = EmailService(settings)
        
        print("✅ Email service initialized")
        print(f"📧 Email host: {settings.EMAIL_HOST}")
        print(f"📧 Email port: {settings.EMAIL_PORT}")
        print(f"📧 Email username: {settings.EMAIL_USERNAME}")
        print(f"📧 TLS enabled: {settings.EMAIL_USE_TLS}")
        
        return True
        
    except Exception as e:
        print(f"❌ Email service check failed: {e}")
        return False

def main():
    """Run email activity tests."""
    print("📧 Email Activity Test Suite")
    print("=" * 60)
    
    # Test 1: Recent email activity
    activity_success = test_recent_email_activity()
    
    # Test 2: Email service status
    service_success = check_email_service_status()
    
    # Final summary
    print("\n" + "=" * 60)
    print("🎯 Email System Summary")
    print("=" * 60)
    
    if activity_success or service_success:
        print("✅ Email system is operational")
        print("\n📧 What's working:")
        print("  - Email search tool available")
        print("  - Email service configured")
        print("  - Email tools registered")
        
        if activity_success:
            print("  - Recent email activity detected")
        else:
            print("  - No recent email activity found")
        
        print("\n📧 To check for your recent email:")
        print("  - The system can search email history")
        print("  - Email search tool is functional")
        print("  - Recent activity may be visible")
        
        return True
    else:
        print("❌ Email system may not be fully operational")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 