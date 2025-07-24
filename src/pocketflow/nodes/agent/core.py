"""
Core agent node for PocketFlow.

This node handles LLM interactions and action extraction.
"""

import json
import re
from typing import Dict, Any, List, Optional

from ...core.node import SimpleNode
from ...core.types import SharedState, AgentAction
from ...services import llm_service
from ...utils.logging import get_logger
from ...utils.errors import LLMError


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
    
    def process(self, shared: SharedState) -> Dict[str, Any]:
        """
        Process user request through LLM and extract actions.
        
        Args:
            shared: Shared state containing email and conversation context
            
        Returns:
            Processing result with routing information
        """
        try:
            self.logger.info("Processing agent request...")
            
            # Build messages for LLM
            messages = self._build_messages(shared)
            if not messages:
                self.logger.warning("No messages to send to LLM")
                return {"route": "finish", "error": "No conversation context"}
            
            # Call LLM service
            response = llm_service.call_llm(messages)
            self.logger.info(f"LLM response received: {response[:100]}...")
            
            # Extract actions from response
            actions = extract_all_actions_from_json(response or "")
            
            # Validate actions
            valid = (
                isinstance(actions, list) and
                all(isinstance(a, dict) and "action" in a for a in actions)
            )
            
            if not valid:
                self.logger.warning("Invalid actions extracted from LLM response")
                return {"route": "finish", "error": "Invalid LLM response format"}
            
            # Store actions in shared state
            shared["action_queue"] = actions[:]
            
            self.logger.info(f"Extracted {len(actions)} actions from LLM response")
            
            if not actions:
                return {"route": "finish"}
            
            return {"route": "default"}
            
        except LLMError as e:
            self.logger.error(f"LLM service error: {e}")
            return {"route": "finish", "error": str(e)}
        except Exception as e:
            self.logger.error(f"Unexpected error in AgentNode: {e}")
            return {"route": "finish", "error": str(e)}
    
    def _build_messages(self, shared: SharedState) -> List[Dict[str, str]]:
        """
        Build messages for LLM based on context.
        
        Args:
            shared: Shared state containing context
            
        Returns:
            List of message dictionaries
        """
        messages = []
        
        # Get email and user info
        email = shared.get("email", {})
        sender = email.get("from") or shared.get("sender", "unknown")
        sender_email = self._extract_email(sender).strip().lower() if sender else "unknown"
        
        # Build system prompt
        system_prompt = self._build_system_prompt(shared, sender_email)
        messages.append({"role": "system", "content": system_prompt})
        
        # Add conversation history
        conversation = shared.get("conversation", [])
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
        
        return messages
    
    def _build_system_prompt(self, shared: SharedState, sender_email: str) -> str:
        """
        Build system prompt for LLM.
        
        Args:
            shared: Shared state containing context
            sender_email: Email of the sender
            
        Returns:
            System prompt string
        """
        # Get user personality from database
        personality_instruction = ""
        try:
            from ..web.routes import get_user_by_email
            user = get_user_by_email(sender_email)
            if user and user.get("personality"):
                personality_instruction = f"\n\nIMPORTANT: When responding, you must behave as follows: {user['personality']}"
        except Exception as e:
            self.logger.warning(f"Could not get user personality for {sender_email}: {e}")
        
        base_prompt = f"""You are an email assistant. The sender of the current email is: {sender_email}{personality_instruction}

Your job is to answer the user's email above as helpfully and conversationally as possible.

You can choose one of these actions:
- send: Reply to the sender or to a specified recipient.
- generate: Generate content (sound, image, or document).
  - type: sound, image, or document
  - prompt: a description of what to generate
  - duration: (optional, in seconds)
- investigate: Research a topic or answer a question using web search.
- finish: End the conversation and trigger a guaranteed response to the sender.

**IMPORTANT:**
If the user requests content to be sent (e.g., "generate a song and send it to X"), ALWAYS output a list of actions:
1. First, a 'generate' action to create the content.
2. Then, a 'send' action to send the generated file as an attachment.
3. When you are done, always call 'finish' as the last action.

Reply ONLY in JSON format, and nothing else. Do NOT add any text before or after the JSON block.

Example:
```json
[
  {{
    "action": "generate",
    "parameters": {{
      "type": "sound",
      "prompt": "A 2-minute song in the style of Daft Punk",
      "duration": 120
    }}
  }},
  {{
    "action": "send",
    "parameters": {{
      "to": "user@example.com",
      "body": "Here is your requested song!",
      "attachment": "<generated file>"
    }}
  }},
  {{
    "action": "finish",
    "parameters": {{}}
  }}
]
```"""
        
        # Add context-specific information
        if shared.get("last_error"):
            base_prompt += f"\n\nNote: The last operation failed with the following error: {shared['last_error']}"
        
        if shared.get("generated_file_path"):
            base_prompt += f"\n\nThe last generated file is: {shared['generated_file_path']}. If you want to send it, use this exact filename as the attachment."
        
        return base_prompt
    
    def _extract_email(self, sender: str) -> str:
        """Extract email address from sender string."""
        import re
        # Use raw string and single backslash for dot
        match = re.search(r'<([A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,})>', sender)
        if match:
            return match.group(1)
        # fallback: if sender is just the email
        match = re.search(r'([A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,})', sender)
        return match.group(1) if match else sender 