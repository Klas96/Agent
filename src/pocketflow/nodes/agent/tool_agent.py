"""
Tool-enabled agent node for PocketFlow.

This node allows the agent to use various tools to accomplish tasks.
"""

import json
import yaml
from typing import Dict, Any, List, Optional
from ...core.node import SimpleNode
from ...core.types import SharedState
from ...services.llm_service import LLMService
from ...utils.logging import get_logger
from ...tools.registry import agent_tool_registry
from ..agent.core import extract_all_actions_from_json
from ...utils.email_utils import extract_email


class ToolAgentNode(SimpleNode):
    """Node for LLM agent interactions with tool access."""
    
    def __init__(self, name: str = "tool_agent"):
        super().__init__(name)
        self.logger = get_logger("ToolAgentNode")
        self.llm_service = LLMService()
        self._register_tools()
    
    def process(self, shared: SharedState) -> Dict[str, Any]:
        """
        Process user request through LLM and extract actions.
        
        Args:
            shared: Shared state containing email and conversation context
            
        Returns:
            Processing result with routing information
        """
        try:
            self.logger.info("Processing tool-enabled agent request...")
            
            # Validate shared state has required data
            if not shared.email and not shared.user:
                self.logger.error("No email or user data in shared state")
                raise ValueError("Missing email or user data in shared state")
            
            # Build messages for LLM
            try:
                messages = self._build_messages(shared)
            except Exception as build_error:
                self.logger.error(f"Failed to build messages: {build_error}")
                import traceback
                self.logger.error(f"Traceback: {traceback.format_exc()}")
                raise
            
            if not messages:
                self.logger.warning("No messages to send to LLM")
                return {"route": "finish", "error": "No conversation context"}
            
            self.logger.info(f"Calling LLM with {len(messages)} messages")
            
            # Call LLM service
            try:
                response = self.llm_service.call_llm(messages)
                self.logger.info(f"LLM response received: {response[:100] if response else 'None'}...")
            except Exception as llm_error:
                self.logger.error(f"LLM service call failed: {llm_error}")
                import traceback
                self.logger.error(f"LLM error traceback: {traceback.format_exc()}")
                raise
            
            if not response or not response.strip():
                self.logger.error("LLM returned empty response")
                raise ValueError("LLM returned empty response")
            
            # Extract actions from response
            try:
                actions = extract_all_actions_from_json(response or "")
                self.logger.info(f"Extracted actions: {actions}")
            except Exception as extract_error:
                self.logger.error(f"Failed to extract actions from LLM response: {extract_error}")
                self.logger.error(f"LLM response was: {response[:500]}")
                import traceback
                self.logger.error(f"Extraction error traceback: {traceback.format_exc()}")
                raise
            
            # Validate actions
            valid = (
                isinstance(actions, list) and
                all(isinstance(a, dict) and "action" in a for a in actions)
            )
            
            self.logger.info(f"Actions valid: {valid}, actions count: {len(actions) if isinstance(actions, list) else 0}")
            
            if not valid:
                self.logger.warning("Invalid actions extracted from LLM response")
                self.logger.warning(f"Actions data: {actions}")
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
            
        except Exception as e:
            import traceback
            error_traceback = traceback.format_exc()
            self.logger.error(f"Unexpected error in ToolAgentNode: {e}")
            self.logger.error(f"Full traceback:\n{error_traceback}")
            
            # Store error in shared state for debugging
            shared.last_error = str(e)
            
            # If LLM fails, create a fallback response to ensure user gets a reply
            self.logger.warning("LLM call failed, creating fallback response")
            
            # Create a simple fallback action to send a response
            email = shared.email or {}
            email_body = email.get("body", "")
            
            # Generate a more informative acknowledgment response
            # Include the error type but not the full traceback (for user-facing message)
            error_type = type(e).__name__
            if "LLM" in error_type or "Connection" in error_type or "Timeout" in error_type:
                fallback_response = f"""Hi there!

I received your email, but I'm having trouble connecting to the AI service right now. This might be a temporary issue.

Please try sending your message again in a few moments. If the problem persists, the issue may be with the AI service connection.

Error type: {error_type}

Thanks for your patience!

Best regards,
PocketFlow Assistant"""
            else:
                fallback_response = f"""Hi there!

I received your email, but I encountered an unexpected error while processing it.

Error: {error_type}

Please try rephrasing your request or sending it again. If the problem continues, please contact support.

Thanks for using PocketFlow!

Best regards,
PocketFlow Assistant"""
            
            # Create a send action as fallback
            fallback_action = {
                "action": "send",
                "parameters": {
                    "to": shared.user or email.get("from", ""),
                    "subject": f"Re: {email.get('subject', 'Your message')}",
                    "body": fallback_response
                }
            }
            
            # Store the fallback action
            shared.action_queue = [fallback_action]
            shared.agent_response = fallback_response
            
            self.logger.info("Created fallback response action")
            return {"route": "send", "error": f"LLM failed, using fallback: {e}"}
    
    def _build_messages(self, shared: SharedState) -> List[Dict[str, str]]:
        """
        Build messages for LLM based on context with tool information.
        
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
            
            # Use the system prompt with tool information
            system_prompt = self._build_system_prompt_with_tools(shared, sender_email)
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
    
    def _build_system_prompt_with_tools(self, shared: SharedState, sender_email: str) -> str:
        """
        Build system prompt with tool information.
        
        Args:
            shared: Shared state
            sender_email: Sender's email address
            
        Returns:
            System prompt with tool information
        """
        from ...utils.prompt_utils import build_system_prompt
        
        # Get the base system prompt
        base_prompt = build_system_prompt(shared, sender_email)
        
        # Add tool information
        tools_description = agent_tool_registry.get_available_tools_prompt()
        
        tool_prompt = f"""
{tools_description}

**AVAILABLE TOOLS:**
You have access to the following tools:
{tools_description}

**TOOL USAGE RULES:**
You MUST use tools when users ask about:
- **Calculations**: Use the calculator tool
- **Weather**: Use the weather tool  
- **Web searches**: Use the web search tool
- **File operations**: Use file read/write tools
- **Database queries**: Use the database tool
- **Document generation**: Use the generate_document tool (via Libriscribe MCP) for professional documents
- **Podcast generation**: Use the podcastify tool (via Podcastfy MCP) for high-quality podcast episodes

When using tools, include them in your action list before sending the response.
"""
        
        return base_prompt + tool_prompt
    
    def _register_tools(self) -> None:
        """Register all available tools with the registry."""
        # Import MCP tools (external processes)
        from ...tools.mcp_tools import (
            LibriscribeDocumentTool,
            LibriscribeResearchTool,
            LibriscribeOutlineTool,
            PodcastfyTool
        )
        
        # Import remaining internal tools (utilities that don't have MCP equivalents)
        from ...tools import (
            DatabaseQueryTool, EmailSearchTool, EmailSendTool
        )
        
        # Tools moved to MPC processes:
        # - WebSearchTool -> Research-MPC
        # - CalculatorTool, FileReadTool, FileWriteTool -> Tools-MPC
        # - WeatherTool, PolymarketTool -> Tools-MPC
        
        # Register MCP tools (external processes)
        mcp_tools = [
            LibriscribeDocumentTool(),  # Replaces internal document generation
            LibriscribeResearchTool(),  # Research via Libriscribe
            LibriscribeOutlineTool(),   # Outline creation via Libriscribe
            PodcastfyTool(),            # Podcast generation via Podcastfy MCP
        ]
        
        # Register utility tools (internal, lightweight utilities)
        # Note: WebSearchTool, CalculatorTool, FileReadTool, FileWriteTool, WeatherTool, 
        # and PolymarketTool have been moved to MPC processes
        utility_tools = [
            DatabaseQueryTool(),
            EmailSearchTool(),
            EmailSendTool(),
        ]
        
        # Register all tools
        for tool in mcp_tools + utility_tools:
            agent_tool_registry.register_tool(tool)
    
    def _generate_agent_prompt(self, user_input: str, context: str, user_email: str, available_tools: List[Dict[str, Any]]) -> str:
        """
        Generate the agent prompt with available tools.
        
        Args:
            user_input: User's input
            context: Conversation context
            user_email: User's email
            available_tools: List of available tools
            
        Returns:
            Formatted prompt for the agent
        """
        tools_description = agent_tool_registry.get_available_tools_prompt()
        
        prompt = f"""
You are a helpful AI assistant with access to various tools. You can use these tools to help answer questions and accomplish tasks.

### USER INPUT
{user_input}

### CONTEXT
{context if context else "No previous context"}

### USER EMAIL
{user_email if user_email else "No user email provided"}

### AVAILABLE TOOLS
{tools_description}

### INSTRUCTIONS
1. Analyze the user's request
2. Decide if you need to use any tools to help answer
3. If you need tools, specify which ones to use and with what parameters
4. Provide a helpful response based on the results

### SPECIAL INSTRUCTIONS FOR CONTENT GENERATION
- **Document generation**: When users ask for document generation (e.g., "create a report", "generate a document", "write a document"), you MUST use the generate_document tool (via Libriscribe MCP) instead of the basic content generation. The generate_document tool creates professional documents with proper structure and formatting.
- **Podcast generation**: When users ask for podcast generation (e.g., "make a podcast", "generate a podcast", "create a podcast"), you MUST use the podcastify tool (via Podcastfy MCP) instead of the basic content generation. The podcastify tool creates high-quality podcast episodes with proper structure, script, and audio.

### RESPONSE FORMAT
Respond in the following YAML format:

```yaml
thinking: |
    Your step-by-step reasoning about what the user needs and how to help them

response: |
    Your main response to the user

tools:
  - name: tool_name
    parameters:
      param1: value1
      param2: value2
  - name: another_tool
    parameters:
      param1: value1
```

If you don't need to use any tools, omit the "tools" section.

### EXAMPLES

Example 1 - No tools needed:
```yaml
thinking: |
    The user is asking a general question that I can answer without tools.

response: |
    Here's the answer to your question...
```

Example 2 - Using a calculator:
```yaml
thinking: |
    The user wants to calculate something, so I'll use the calculator tool.

response: |
    Let me calculate that for you.

tools:
  - name: calculator
    parameters:
      expression: "2 + 3 * 4"
```

Example 3 - Using podcastify for podcast generation:
```yaml
thinking: |
    The user wants a podcast about local LLMs. I should use the podcastify tool (via Podcastfy MCP) to create a high-quality podcast episode.

response: |
    I'll create a podcast about local LLMs for you using the podcastify tool.

tools:
  - name: podcastify
    parameters:
      topic: "Local LLMs and their applications"
      duration_minutes: 10
      style: "conversational"
      voice_preference: "professional"
      output_format: "mp3"
```

Example 4 - Using generate_document for document generation:
```yaml
thinking: |
    The user wants a document about local LLMs. I should use the generate_document tool (via Libriscribe MCP) to create a professional document.

response: |
    I'll create a document about local LLMs for you using the generate_document tool.

tools:
  - name: generate_document
    parameters:
      prompt: "Local LLMs and their applications"
      document_type: "report"
      output_format: "wav"
```

Now, please help the user with their request.
"""
        
        return prompt
    
    def _parse_agent_response(self, response: str) -> Dict[str, Any]:
        """
        Parse the agent's response to extract tool usage.
        
        Args:
            response: Raw agent response
            
        Returns:
            Parsed response with tools and response text
        """
        try:
            # Extract YAML from the response
            if "```yaml" in response:
                yaml_start = response.find("```yaml") + 7
                yaml_end = response.find("```", yaml_start)
                yaml_content = response[yaml_start:yaml_end].strip()
                
                parsed = yaml.safe_load(yaml_content)
                return parsed
            else:
                # No YAML found, treat as plain response
                return {"response": response}
                
        except Exception as e:
            self.logger.error(f"Failed to parse agent response: {str(e)}")
            return {"response": response}
    
    def _execute_tools(self, tools_to_execute: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Execute the tools requested by the agent.
        
        Args:
            tools_to_execute: List of tool specifications
            
        Returns:
            List of tool execution results
        """
        results = []
        
        for tool_spec in tools_to_execute:
            tool_name = tool_spec.get("name")
            parameters = tool_spec.get("parameters", {})
            
            if not tool_name:
                continue
            
            # Execute the tool
            result = agent_tool_registry.execute_tool_with_validation(tool_name, **parameters)
            
            results.append({
                "tool_name": tool_name,
                "parameters": parameters,
                "success": result.success,
                "data": result.data,
                "error": result.error
            })
        
        return results 