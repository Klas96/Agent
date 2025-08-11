#!/usr/bin/env python3
"""
Test script to verify that the SendEmailNode now properly replaces variables in the attachment path.
"""

import sys
import os

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_send_email_variable_replacement():
    """Test that the SendEmailNode properly replaces variables in attachment paths."""
    print("🧪 Testing SendEmailNode Variable Replacement...")
    
    try:
        from src.pocketflow.core.types import SharedState
        from src.pocketflow.nodes.email.send import SendEmailNode
        
        # Create a test shared state with tool results
        shared = SharedState()
        shared.email = {
            'id': 'test_123',
            'subject': 'Test podcast request',
            'from': 'test@example.com',
            'body': 'Generate a podcast about AI',
            'message_id': '<test@example.com>'
        }
        shared.tool_results = [
            {
                'tool_name': 'podcastify',
                'result': {
                    'file_path': '/tmp/pocketflow_podcasts/podcast_1754816022.wav',
                    'success': True
                }
            }
        ]
        
        # Create SendEmailNode
        node = SendEmailNode()
        
        # Test the prep method with attachment variable
        print("\n📋 Testing prep method with {generated_file} variable...")
        
        # Mock the agent_action with attachment
        shared.agent_action = {
            'action': 'send',
            'parameters': {
                'to': '{sender_email}',
                'body': 'Here is your podcast!',
                'attachment': '{generated_file}'
            }
        }
        
        # Call prep method
        prep_result = node.prep(shared)
        
        if prep_result:
            email_service, to, subject, body, attachment, email, shared = prep_result
            print(f"✅ Prep method returned successfully")
            print(f"   To: {to}")
            print(f"   Subject: {subject}")
            print(f"   Body: {body[:50]}...")
            print(f"   Attachment: {attachment}")
            
            # Check if attachment variable was replaced
            if attachment and '/tmp/pocketflow_podcasts/podcast_1754816022.wav' in attachment:
                print("✅ Attachment variable was properly replaced!")
                return True
            else:
                print("❌ Attachment variable was not replaced correctly")
                print(f"   Expected: /tmp/pocketflow_podcasts/podcast_1754816022.wav")
                print(f"   Got: {attachment}")
                return False
        else:
            print("❌ Prep method returned None")
            return False
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_send_email_variable_replacement()
    if success:
        print("\n🎉 SendEmailNode variable replacement test passed!")
    else:
        print("\n💥 SendEmailNode variable replacement test failed!") 