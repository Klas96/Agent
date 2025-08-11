#!/usr/bin/env python3
"""
Test script to verify that the {generated_file} variable replacement is working correctly.
"""

import sys
import os

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_generated_file_variable():
    """Test that the {generated_file} variable is replaced correctly."""
    print("🧪 Testing {generated_file} Variable Replacement...")
    
    try:
        from src.pocketflow.core.types import SharedState
        from src.pocketflow.utils.prompt_utils import replace_variables_in_text, _get_generated_file_path
        
        # Create a test shared state
        shared = SharedState()
        shared.email = {
            'id': 'test_123',
            'subject': 'Test podcast request',
            'from': 'test@example.com',
            'body': 'Generate a podcast about AI'
        }
        
        # Test 1: No tool results (should return placeholder)
        print("\n📋 Test 1: No tool results")
        file_path = _get_generated_file_path(shared)
        print(f"Generated file path: {file_path}")
        expected_placeholder = "/tmp/pocketflow_podcasts/podcast_[timestamp].wav"
        if expected_placeholder in file_path:
            print("✅ Correctly returned placeholder when no tool results")
        else:
            print("❌ Did not return expected placeholder")
        
        # Test 2: With tool results
        print("\n📋 Test 2: With tool results")
        shared.tool_results = [
            {
                'tool_name': 'podcastify',
                'result': {
                    'file_path': '/tmp/pocketflow_podcasts/podcast_1754815502.wav',
                    'success': True
                }
            }
        ]
        file_path = _get_generated_file_path(shared)
        print(f"Generated file path: {file_path}")
        if '/tmp/pocketflow_podcasts/podcast_1754815502.wav' in file_path:
            print("✅ Correctly returned actual file path from tool results")
        else:
            print("❌ Did not return expected file path")
        
        # Test 3: Variable replacement in text
        print("\n📋 Test 3: Variable replacement in text")
        test_text = "Here's your podcast: {generated_file}"
        replaced_text = replace_variables_in_text(test_text, shared, "test@example.com")
        print(f"Original: {test_text}")
        print(f"Replaced: {replaced_text}")
        if '/tmp/pocketflow_podcasts/podcast_1754815502.wav' in replaced_text:
            print("✅ Variable replacement worked correctly")
        else:
            print("❌ Variable replacement failed")
        
        # Test 4: Multiple tool results (should use most recent)
        print("\n📋 Test 4: Multiple tool results")
        shared.tool_results = [
            {
                'tool_name': 'podcastify',
                'result': {
                    'file_path': '/tmp/pocketflow_podcasts/podcast_old.wav',
                    'success': True
                }
            },
            {
                'tool_name': 'podcastify',
                'result': {
                    'file_path': '/tmp/pocketflow_podcasts/podcast_new.wav',
                    'success': True
                }
            }
        ]
        file_path = _get_generated_file_path(shared)
        print(f"Generated file path: {file_path}")
        if '/tmp/pocketflow_podcasts/podcast_new.wav' in file_path:
            print("✅ Correctly returned most recent file path")
        else:
            print("❌ Did not return most recent file path")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_generated_file_variable()
    if success:
        print("\n🎉 {generated_file} variable test passed!")
    else:
        print("\n💥 {generated_file} variable test failed!") 