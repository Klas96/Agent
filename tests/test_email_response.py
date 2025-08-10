#!/usr/bin/env python3
"""
Test script to verify email response functionality after the routing fix.
"""

import sys
import os

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_email_response_flow():
    """Test the complete email response flow."""
    print("🧪 Testing Email Response Flow...")
    
    try:
        from src.pocketflow.core.types import SharedState
        from src.pocketflow.flows.email_processor import email_processor_flow
        
        # Create a test shared state that simulates the scenario
        shared = SharedState()
        shared.email = {
            'id': 'test_848',
            'subject': 'Test podcast request',
            'from': 'Klas Holmgren <klas0holmgren@gmail.com>',
            'body': 'Generate a podcast about local LLMs',
            'message_id': '<test@example.com>',
            'thread_id': '<test@example.com>'
        }
        shared.user = 'klas0holmgren@gmail.com'
        
        # Simulate the state after tool execution
        shared.action_queue = [
            {
                'action': 'send', 
                'parameters': {
                    'to': '{sender_email}', 
                    'body': "I've created a podcast about local LLMs for you! Here's your high-quality podcast episode.", 
                    'attachment': '<generated file>'
                }
            },
            {'action': 'finish', 'parameters': {}}
        ]
        
        # This should be updated by pop_action to contain the 'send' action
        shared.agent_action = {'action': 'use_tool', 'parameters': {'tool_name': 'podcastify'}}
        
        # Simulate tool results
        shared.tool_results = [
            {
                'tool_name': 'podcastify',
                'parameters': {
                    'topic': 'Local LLMs and their applications',
                    'duration_minutes': 10,
                    'style': 'conversational',
                    'target_audience': 'general',
                    'voice_preference': 'professional',
                    'output_format': 'wav'
                },
                'result': {
                    'file_path': '/tmp/pocketflow_podcasts/test_podcast.wav',
                    'script': 'Test podcast script content...',
                    'duration': 10,
                    'topic': 'Local LLMs and their applications'
                }
            }
        ]
        
        print("✅ Test data prepared")
        print(f"📧 Email: {shared.email['from']}")
        print(f"📝 Body: {shared.email['body']}")
        print(f"📋 Action Queue: {len(shared.action_queue)} actions")
        print(f"🔧 Current Agent Action: {shared.agent_action['action']}")
        
        # Run the flow
        print("\n🔄 Running email processor flow...")
        result = email_processor_flow.run(shared)
        
        print(f"\n📊 Results:")
        print(f"✅ Success: {result['success']}")
        print(f"❌ Error: {result['error']}")
        
        if result['success']:
            print("🎉 Email response flow completed successfully!")
        else:
            print("💥 Email response flow failed!")
            
        return result['success']
        
    except Exception as e:
        print(f"💥 Test failed with exception: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_email_response_flow()
    sys.exit(0 if success else 1) 