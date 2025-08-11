import sys
import os
import unittest
from unittest.mock import patch
from pathlib import Path

# Ensure src is in the path for both direct and unittest discovery
if not any("pocketflow" in p for p in sys.path):
    sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

class TestLLMGuaranteedResponse(unittest.TestCase):
    def setUp(self):
        from pocketflow.core.types import SharedState
        self.shared = SharedState(
            user="test@example.com",
            email={
                "id": "test_email_1",
                "from": "user@example.com",
                "to": "agent@klasholmgren.se",
                "subject": "Test guaranteed response",
                "body": "What is 2 + 2?",
                "thread_id": "test_thread_1"
            }
        )

    @patch("pocketflow.services.llm_service.LLMService.call_openai")
    @patch("pocketflow.services.llm_service.LLMService.call_local")
    def test_fallback_to_ollama(self, mock_local, mock_openai):
        """Test fallback to Ollama when OpenAI is down."""
        from pocketflow.flows.manager import flow_manager
        # Simulate OpenAI being down
        mock_openai.side_effect = Exception("OpenAI is down!")
        mock_local.return_value = "Fallback response from Ollama"

        print("\n[TEST] Simulating OpenAI down, Ollama available...")
        result = flow_manager.run_flow("email_processor", self.shared)
        final_state = result.get("final_state", {})
        self.assertTrue(result.get("success"))
        self.assertIn("Fallback response from Ollama", str(final_state))
        print("✅ Fallback to Ollama test passed")

    @patch("pocketflow.services.llm_service.LLMService.call_openai")
    @patch("pocketflow.services.llm_service.LLMService.call_local")
    def test_fallback_to_default_message(self, mock_local, mock_openai):
        """Test fallback to default message if all LLMs are down."""
        from pocketflow.flows.manager import flow_manager
        # Simulate both OpenAI and Ollama being down
        mock_openai.side_effect = Exception("OpenAI is down!")
        mock_local.side_effect = Exception("Ollama is down!")

        print("\n[TEST] Simulating both OpenAI and Ollama down...")
        result = flow_manager.run_flow("email_processor", self.shared)
        final_state = result.get("final_state", {})
        self.assertTrue(result.get("success"))
        # Check for a default/fallback message in the state
        found = False
        for v in final_state.values():
            if isinstance(v, str) and ("Sorry" in v or "error" in v.lower() or "unavailable" in v.lower()):
                found = True
        self.assertTrue(found, "No default fallback message found in final state")
        print("✅ Fallback to default message test passed")

if __name__ == "__main__":
    unittest.main(verbosity=2) 