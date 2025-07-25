"""
Core agent node for PocketFlow.

This node handles LLM interactions and action extraction.
"""

import json
import re
from typing import Dict, Any, List, Optional

from ...core.node import SimpleNode
from ...core.types import SharedState, AgentAction
from ...services.llm_service import LLMService
from ...utils.logging import get_logger
from ...utils.errors import LLMError
from ...utils.prompt_utils import build_system_prompt
from utils.email_utils import extract_email


def extract_all_actions_from_json(response: str) -> List[Dict[str, Any]]:
    """
    Extract actions from LLM JSON response.
    
    Args:
        response: Raw LLM response
        
    Returns:
        List of action dictionaries
    """
    try:
        # Try to extract the first JSON code block
        match = re.search(r"```json\s*([\s\S]+?)```", response)
        if match:
            json_str = match.group(1).strip()
        else:
            # Remove any leading code fence if present
            json_str = response.strip()
            if json_str.startswith("```json"):
                json_str = json_str[len("```json"):].strip()
            if json_str.startswith("```"):
                json_str = json_str[len("```"):].strip()
            if json_str.endswith("```"):
                json_str = json_str[:-3].strip()
        
        parsed = json.loads(json_str)
        if isinstance(parsed, list):
            return parsed
        elif isinstance(parsed, dict):
            return [parsed]
        else:
            return []
    except Exception as e:
        print(f"[extract_all_actions_from_json] JSON parse error: {e}")
        return []


class AgentNode(SimpleNode):
    """Node for LLM agent interactions and action extraction."""
    
    def __init__(self, name: str = "agent"):
        super().__init__(name)
        self.logger = get_logger("AgentNode")
        from ...services import llm_service
        self.llm_service = llm_service
    
    def process(self, shared: SharedState) -> Dict[str, Any]:
        """
        Process user request through LLM and extract actions.
        
        Args:
            shared: Shared state containing email and conversation context
            
        Returns:
            Processing result with routing information
        """
        try:
            self.logger.error("CRITICAL: AgentNode.process method is being called!")
            self.logger.info("Processing agent request...")
            self.logger.info("AgentNode.process called - about to call _build_messages")
            
            # Build messages for LLM
            self.logger.info("About to call _build_messages")
            self.logger.info(f"Shared state: {shared}")
            self.logger.info(f"Shared email: {getattr(shared, 'email', None)}")
            self.logger.info(f"Shared user: {getattr(shared, 'user', None)}")
            
            try:
                messages = self._build_messages(shared)
                self.logger.info(f"_build_messages returned {len(messages)} messages")
            except Exception as e:
                self.logger.error(f"Exception in _build_messages call: {e}")
                import traceback
                self.logger.error(f"Traceback: {traceback.format_exc()}")
                raise
            
            if not messages:
                self.logger.warning("No messages to send to LLM")
                return {"route": "finish", "error": "No conversation context"}
            
            # Call LLM service
            self.logger.error("CRITICAL: About to call llm_service.call_llm in AgentNode.process!")
            response = self.llm_service.call_llm(messages)
            self.logger.info(f"LLM response received: {response[:100]}...")
            self.logger.info(f"LLM response type: {type(response)}")
            self.logger.info(f"LLM response length: {len(response) if response else 0}")
            
            # Extract actions from response
            self.logger.info(f"About to extract actions from response: {response[:200]}...")
            actions = extract_all_actions_from_json(response or "")
            self.logger.info(f"Extracted actions: {actions}")
            
            # Validate actions
            valid = (
                isinstance(actions, list) and
                all(isinstance(a, dict) and "action" in a for a in actions)
            )
            
            self.logger.info(f"Actions valid: {valid}, actions count: {len(actions) if isinstance(actions, list) else 0}")
            
            if not valid:
                self.logger.warning("Invalid actions extracted from LLM response")
                return {"route": "finish", "error": "Invalid LLM response format"}
            
            # Store actions in shared state
            shared.action_queue = actions[:]
            
            self.logger.info(f"Extracted {len(actions)} actions from LLM response")
            
            if not actions:
                self.logger.info("No actions found, returning finish")
                return {"route": "finish"}
            
            self.logger.info("Actions found, returning default route")
            return {"route": "default"}
            
        except LLMError as e:
            self.logger.error(f"LLM service error: {e}")
            raise e
        except Exception as e:
            self.logger.error(f"Unexpected error in AgentNode: {e}")
            raise LLMError(f"Unexpected error in agent processing: {e}")
    
    def _build_messages(self, shared: SharedState) -> List[Dict[str, str]]:
        """
        Build messages for LLM based on context.
        
        Args:
            shared: Shared state containing context
            
        Returns:
            List of message dictionaries
        """
        self.logger.info("_build_messages called")
        
        try:
            messages = []
            
            # Get email and user info
            email = shared.email or {}
            sender = email.get("from") or shared.user or "unknown"
            sender_email = extract_email(sender).strip().lower() if sender else "unknown"
            
            self.logger.info(f"Extracted sender_email: {sender_email}")
            
            # Use the new utility function
            system_prompt = build_system_prompt(shared, sender_email)
            messages.append({"role": "system", "content": system_prompt})
            
            # Add conversation history
            conversation = shared.conversation or []
            if conversation:
                for msg in conversation:
                    messages.append(msg)
            
            # Add current email if not already in conversation
            if email and email.get("body"):
                current_message = {
                    "role": "user",
                    "content": email.get("body", "")
                }
                messages.append(current_message)
            
            self.logger.info(f"_build_messages completed, returning {len(messages)} messages")
            return messages
            
        except Exception as e:
            self.logger.error(f"Error in _build_messages: {e}")
            import traceback
            self.logger.error(f"Traceback: {traceback.format_exc()}")
            raise 