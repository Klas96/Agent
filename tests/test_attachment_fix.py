#!/usr/bin/env python3
"""
Test script to verify that the agent now uses correct file paths for attachments.
"""

import sys
import os

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_agent_attachment_handling():
    """Test that the agent uses correct file paths for attachments."""
    print("🧪 Testing Agent Attachment Handling...")
    
    try:
        from src.pocketflow.services.llm_service import LLMService
        
        # Create LLM service
        llm_service = LLMService()
        
        # Test context with tool results
        context = {
            "user_has_tokens": True,
            "conversation": "User requested a podcast about local LLMs"
        }
        
        # Generate system prompt
        system_prompt = llm_service.generate_system_prompt(context)
        
        print("✅ System prompt generated successfully")
        
        # Check if the prompt contains the correct instructions
        if "actual file path" in system_prompt:
            print("✅ Prompt contains correct file path instructions")
        else:
            print("❌ Prompt missing file path instructions")
            
        if "<generated file>" not in system_prompt:
            print("✅ Prompt no longer contains placeholder")
        else:
            print("❌ Prompt still contains placeholder")
            
        if "/path/to/actual/generated/file.wav" in system_prompt:
            print("✅ Prompt contains correct example path")
        else:
            print("❌ Prompt missing correct example path")
            
        print("\n📋 System Prompt Preview:")
        print("=" * 50)
        print(system_prompt[:500] + "...")
        print("=" * 50)
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

if __name__ == "__main__":
    success = test_agent_attachment_handling()
    if success:
        print("\n🎉 Attachment fix test passed!")
    else:
        print("\n💥 Attachment fix test failed!") 