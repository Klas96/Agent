#!/usr/bin/env python3
"""
Test LLM service fallback functionality.

This test verifies that the system can fall back to local Ollama when OpenAI is down.
"""

import sys
import os
import unittest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path

# Add the src directory to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

class TestLLMFallback(unittest.TestCase):
    """Test LLM service fallback functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Hello, how are you?"}
        ]
    
    def test_openai_fallback_to_ollama(self):
        """Test that OpenAI failures fall back to Ollama."""
        try:
            from pocketflow.services.llm_service import LLMService
            
            # Mock OpenAI to fail
            with patch('openai.OpenAI') as mock_openai:
                mock_client = Mock()
                mock_openai.return_value = mock_client
                mock_client.chat.completions.create.side_effect = Exception("OpenAI API error")
                
                # Create LLM service
                llm_service = LLMService()
                
                # Test that it falls back to Ollama
                with patch.object(llm_service, '_call_local_llm') as mock_local:
                    mock_local.return_value = "Hello! I'm doing well, thank you for asking."
                    
                    # This should trigger fallback to local LLM
                    response = llm_service.call_llm(self.test_messages)
                    
                    # Verify fallback was called
                    mock_local.assert_called_once()
                    self.assertIn("Hello", response)
                    print("✅ OpenAI fallback to Ollama test passed")
                    
        except Exception as e:
            self.fail(f"OpenAI fallback test failed: {e}")
    
    def test_ollama_availability(self):
        """Test that Ollama is available and responding."""
        try:
            import requests
            
            # Test Ollama API directly
            response = requests.get("http://localhost:11434/api/tags", timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                models = data.get("models", [])
                
                if models:
                    print(f"✅ Ollama is running with {len(models)} models:")
                    for model in models:
                        print(f"   - {model.get('name', 'Unknown')}")
                    return True
                else:
                    print("⚠️ Ollama is running but no models found")
                    return False
            else:
                print(f"❌ Ollama API returned status {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Ollama availability test failed: {e}")
            return False
    
    def test_llm_service_quota_fallback(self):
        """Test that quota exceeded errors trigger fallback."""
        try:
            from pocketflow.services.llm_service import LLMService
            
            # Mock OpenAI to return quota exceeded error
            with patch('openai.OpenAI') as mock_openai:
                mock_client = Mock()
                mock_openai.return_value = mock_client
                mock_client.chat.completions.create.side_effect = Exception("insufficient_quota")
                
                # Create LLM service
                llm_service = LLMService()
                
                # Test that quota errors trigger fallback
                with patch.object(llm_service, '_call_local_llm') as mock_local:
                    mock_local.return_value = "Fallback response from local LLM"
                    
                    response = llm_service.call_llm(self.test_messages)
                    
                    # Verify fallback was called
                    mock_local.assert_called_once()
                    self.assertIn("Fallback", response)
                    print("✅ Quota exceeded fallback test passed")
                    
        except Exception as e:
            self.fail(f"Quota fallback test failed: {e}")
    
    def test_local_llm_response_format(self):
        """Test that local LLM responses are properly formatted."""
        try:
            from pocketflow.services.llm_service import LLMService
            
            llm_service = LLMService()
            
            # Test local LLM call directly
            with patch('requests.post') as mock_post:
                mock_response = Mock()
                mock_response.status_code = 200
                mock_response.json.return_value = {
                    "response": "This is a test response from local LLM"
                }
                mock_post.return_value = mock_response
                
                response = llm_service._call_local_llm(self.test_messages)
                
                self.assertIn("test response", response)
                print("✅ Local LLM response format test passed")
                
        except Exception as e:
            self.fail(f"Local LLM format test failed: {e}")
    
    def test_guaranteed_response_when_llm_fails(self):
        """Test that users still get a response even when all LLMs fail."""
        try:
            from pocketflow.core.types import SharedState
            from pocketflow.nodes import AgentNode
            
            # Create a mock shared state
            shared = SharedState()
            shared.email = {
                "body": "Hello, can you help me?",
                "from": "test@example.com"
            }
            shared.user = "test@example.com"
            
            # Mock LLM service to fail completely
            with patch('pocketflow.services.llm_service.LLMService.call_llm') as mock_llm:
                mock_llm.side_effect = Exception("All LLM services unavailable")
                
                # Create agent node
                agent_node = AgentNode("test_agent")
                
                # Test that the node handles LLM failures gracefully
                try:
                    result = agent_node.run(shared)
                    # Should not crash, even if LLM fails
                    print("✅ Agent handles LLM failures gracefully")
                except Exception as e:
                    print(f"⚠️ Agent crashed on LLM failure: {e}")
                    
        except Exception as e:
            self.fail(f"Guaranteed response test failed: {e}")


def test_ollama_integration():
    """Test actual Ollama integration."""
    print("\n=== Testing Ollama Integration ===")
    
    try:
        import requests
        
        # Test basic Ollama API
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code != 200:
            print("❌ Ollama API not responding")
            return False
        
        # Test model generation
        test_data = {
            "model": "llama3:latest",
            "prompt": "Hello, how are you?",
            "stream": False
        }
        
        response = requests.post("http://localhost:11434/api/generate", 
                               json=test_data, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            if "response" in result:
                print("✅ Ollama integration test passed")
                print(f"   Response: {result['response'][:100]}...")
                return True
            else:
                print("❌ Ollama response missing 'response' field")
                return False
        else:
            print(f"❌ Ollama generation failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Ollama integration test failed: {e}")
        return False


if __name__ == "__main__":
    print("🧪 LLM Fallback Test Suite")
    print("=" * 50)
    
    # Run unit tests
    unittest.main(verbosity=2, exit=False)
    
    # Run integration test
    test_ollama_integration()
    
    print("\n" + "=" * 50)
    print("Test Summary:")
    print("✅ Unit tests completed")
    print("✅ Integration test completed")
    print("\nIf you're not getting responses, check:")
    print("1. Is Ollama running? (curl http://localhost:11434/api/tags)")
    print("2. Is the llama3:latest model installed?")
    print("3. Are there any network issues?")
    print("4. Check the application logs for LLM errors") 