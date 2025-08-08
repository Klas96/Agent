"""
Core agent node for PocketFlow.

This module contains the AgentNode for LLM-based decision making.
"""

import json
import re
from typing import Dict, Any, List, Optional

from ...core.node import SimpleNode
from ...core.types import SharedState, AgentAction, ActionType
from ...services.llm_service import LLMService
from ...utils.logging import get_logger
from ...utils.errors import LLMError
from ...utils.prompt_utils import build_system_prompt
from ...utils.email_utils import extract_email
from ...tools.registry import agent_tool_registry


def extract_all_actions_from_json(response: str) -> List[Dict[str, Any]]:
    """
    Extract actions from LLM JSON response.
    
    Args:
        response: Raw LLM response
        
    Returns:
        List of action dictionaries
    """
    if not response:
        print("[extract_all_actions_from_json] Empty response")
        return []
    
    json_str = ""
    
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

        # Clean control characters and normalize newlines
        json_str = re.sub(r'[\x00-\x1f]', '', json_str)  # Remove control characters
        json_str = re.sub(r'\r\n', '\n', json_str)  # Normalize line endings
        json_str = re.sub(r'\r', '\n', json_str)  # Convert remaining \r to \n
        
        # Escape newlines in string values
        json_str = re.sub(r'"([^"]*?)\n([^"]*?)"', r'"\1\\n\2"', json_str)
        
        # Try to find the end of the JSON array/object
        brace_count = 0
        bracket_count = 0
        in_string = False
        escape_next = False
        json_end = 0
        
        for i, char in enumerate(json_str):
            if escape_next:
                escape_next = False
                continue
                
            if char == '\\':
                escape_next = True
                continue
                
            if char == '"' and not escape_next:
                in_string = not in_string
                continue
                
            if not in_string:
                if char == '{':
                    brace_count += 1
                elif char == '}':
                    brace_count -= 1
                elif char == '[':
                    bracket_count += 1
                elif char == ']':
                    bracket_count -= 1
                    
                # If we've closed all braces/brackets, this is the end
                if brace_count == 0 and bracket_count == 0 and i > 0:
                    json_end = i + 1
                    break
        
        # Extract only the valid JSON part
        if json_end > 0:
            json_str = json_str[:json_end]
        
        # Attempt to parse the cleaned JSON
        actions = json.loads(json_str)
        
        # Validate the structure
        if not isinstance(actions, list):
            actions = [actions]
            
        # Validate each action
        valid_actions = []
        for action in actions:
            if isinstance(action, dict) and "action" in action:
                valid_actions.append(action)
                
        return valid_actions
        
    except json.JSONDecodeError as e:
        # Use print for error logging since logger is not available in this function
        print(f"[extract_all_actions_from_json] JSON parse error: {e}")
        print(f"[extract_all_actions_from_json] Problematic JSON: {json_str[:500]}...")
        
        # Try to fix common JSON issues
        fixed_json = _attempt_json_fix(json_str)
        if fixed_json:
            try:
                actions = json.loads(fixed_json)
                if not isinstance(actions, list):
                    actions = [actions]
                valid_actions = []
                for action in actions:
                    if isinstance(action, dict) and "action" in action:
                        valid_actions.append(action)
                if valid_actions:
                    print(f"[extract_all_actions_from_json] Successfully fixed JSON, extracted {len(valid_actions)} actions")
                    return valid_actions
            except:
                pass
        
        return []
    except Exception as e:
        print(f"[extract_all_actions_from_json] Unexpected error: {e}")
        return []


def _attempt_json_fix(json_str: str) -> str:
    """
    Attempt to fix common JSON formatting issues.
    
    Args:
        json_str: Potentially malformed JSON string
        
    Returns:
        Fixed JSON string or empty string if unfixable
    """
    if not json_str:
        return ""
    
    # Remove any text before the first [
    start_bracket = json_str.find('[')
    if start_bracket > 0:
        json_str = json_str[start_bracket:]
    
    # Remove any text after the last ]
    end_bracket = json_str.rfind(']')
    if end_bracket > 0:
        json_str = json_str[:end_bracket + 1]
    
    # Fix common issues
    json_str = json_str.replace('}\n{', '},\n{')  # Add missing commas
    json_str = json_str.replace('}\n  {', '},\n  {')  # Add missing commas with indentation
    
    # Fix unquoted keys
    json_str = re.sub(r'(\s*)(\w+)(\s*):', r'\1"\2"\3:', json_str)
    
    # Fix single quotes to double quotes
    json_str = json_str.replace("'", '"')
    
    # Remove trailing commas
    json_str = re.sub(r',(\s*[}\]])', r'\1', json_str)
    
    return json_str


class AgentNode(SimpleNode):
    """Node for LLM agent interactions and action extraction."""
    
    def __init__(self, name: str = "agent"):
        super().__init__(name)
        self.logger = get_logger("AgentNode")
        self.llm_service = LLMService()
    
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
            
            # Return the first action type as the route
            first_action = actions[0]
            action_type = first_action.get("action", "default")
            self.logger.info(f"First action type: {action_type}, returning as route")
            return {"route": action_type}
            
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
            raise e


class ToolExecutionNode(SimpleNode):
    """Node for executing tools based on agent decisions."""
    
    def __init__(self, name: str = "tool_execution"):
        super().__init__(name)
        self.logger = get_logger("ToolExecutionNode")
    
    def process(self, shared: SharedState) -> Dict[str, Any]:
        """
        Execute tools based on agent action.
        
        Args:
            shared: Shared state containing tool action
            
        Returns:
            Tool execution result
        """
        try:
            # Get the current agent action
            agent_action = getattr(shared, 'agent_action', None)
            if not agent_action or agent_action.get('action') != 'use_tool':
                self.logger.warning("No use_tool action found in shared state")
                return {"route": "finish", "error": "No tool action to execute"}
            
            # Extract tool information
            parameters = agent_action.get('parameters', {})
            tool_name = parameters.get('tool_name')
            # Extract tool parameters - they are directly in the parameters field, not nested
            tool_params = {k: v for k, v in parameters.items() if k != 'tool_name'}
            
            if not tool_name:
                self.logger.error("No tool name specified in use_tool action")
                return {"route": "finish", "error": "No tool name specified"}
            
            self.logger.info(f"Executing tool: {tool_name} with parameters: {tool_params}")
            
            # Execute the tool
            try:
                tool = agent_tool_registry.get_tool(tool_name)
                if not tool:
                    self.logger.error(f"Tool not found: {tool_name}")
                    return {"route": "finish", "error": f"Tool not found: {tool_name}"}
                
                # Execute the tool
                result = tool.execute(**tool_params)
                
                # Store the result in shared state
                shared.tool_results = [{
                    "tool_name": tool_name,
                    "parameters": tool_params,
                    "result": result
                }]
                
                self.logger.info(f"Tool execution successful: {tool_name}")
                return {"route": "send", "tool_result": result}
                
            except Exception as e:
                self.logger.error(f"Tool execution failed: {e}")
                shared.tool_results = [{
                    "tool_name": tool_name,
                    "parameters": tool_params,
                    "error": str(e)
                }]
                return {"route": "send", "error": f"Tool execution failed: {e}"}
                
        except Exception as e:
            self.logger.error(f"Unexpected error in ToolExecutionNode: {e}")
            return {"route": "finish", "error": f"Tool execution error: {e}"} 