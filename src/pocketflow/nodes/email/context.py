"""
Conversation context node for PocketFlow.

This node manages conversation history and context for email threads.
"""

from typing import Dict, Any, List, Optional

from ...core.node import SimpleNode
from ...core.types import SharedState
from ...utils.logging import get_logger


class ConversationContextNode(SimpleNode):
    """Node for managing conversation context and history."""
    
    def __init__(self, name: str = "conversation_context"):
        super().__init__(name)
        self.logger = get_logger("ConversationContextNode")
    
    def process(self, shared: SharedState) -> Dict[str, Any]:
        """
        Build conversation context from email and history.
        
        Args:
            shared: Shared state containing email and conversation data
            
        Returns:
            Processing result with routing information
        """
        try:
            email = shared.get("email")
            if not email:
                self.logger.info("No email found, skipping conversation context")
                shared["conversation"] = None
                return {"route": "no_context"}
            
            # Get thread ID for conversation tracking
            thread_id = email.get("thread_id", email.get("id", "default"))
            
            # Initialize conversations if not present
            conversations = shared.setdefault("conversations", {})
            history = conversations.get(thread_id, [])
            
            # Add the new user message to the history
            user_message = {
                "role": "user",
                "content": email.get("body", "")
            }
            history.append(user_message)
            
            # Update conversation in shared state
            shared["conversation"] = history
            shared["conversations"][thread_id] = history
            
            self.logger.info(f"Updated conversation context for thread {thread_id}, history length: {len(history)}")
            
            return {"route": "default"}
            
        except Exception as e:
            self.logger.error(f"Error in ConversationContextNode: {e}")
            shared["conversation"] = None
            return {"route": "no_context", "error": str(e)} 