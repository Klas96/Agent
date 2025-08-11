#!/usr/bin/env python3
"""
Test script to verify that the _get_generated_file_path function now properly handles ToolResult objects.
"""

import sys
import os

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_toolresult_handling():
    """Test that _get_generated_file_path properly handles ToolResult objects."""
    print("🧪 Testing ToolResult Handling in _get_generated_file_path...")
    
    try:
        from src.pocketflow.core.types import SharedState
        from src.pocketflow.utils.prompt_utils import _get_generated_file_path
        
        # Create a mock ToolResult class to simulate the actual structure
        class MockToolResult:
            def __init__(self, success, data):
                self.success = success
                self.data = data
        
        # Create a test shared state with tool results
        shared = SharedState()
        shared.tool_results = [
            {
                'tool_name': 'podcastify',
                'result': MockToolResult(
                    success=True,
                    data={'file_path': '/tmp/pocketflow_podcasts/podcast_1754816434.wav'}
                )
            }
        ]
        
        # Test the function
        print("\n📋 Testing with ToolResult object...")
        file_path = _get_generated_file_path(shared)
        print(f"Generated file path: {file_path}")
        
        expected_path = "/tmp/pocketflow_podcasts/podcast_1754816434.wav"
        if file_path == expected_path:
            print("✅ ToolResult handling is working correctly!")
            return True
        else:
            print("❌ ToolResult handling failed")
            print(f"   Expected: {expected_path}")
            print(f"   Got: {file_path}")
            return False
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_toolresult_handling()
    if success:
        print("\n🎉 ToolResult handling test passed!")
    else:
        print("\n💥 ToolResult handling test failed!") 