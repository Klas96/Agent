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
            
            # Build messages for LLM
            messages = self._build_messages(shared)
            
            if not messages:
                self.logger.warning("No messages to send to LLM")
                return {"route": "finish", "error": "No conversation context"}
            
            # Call LLM service
            response = self.llm_service.call_llm(messages)
            self.logger.info(f"LLM response received: {response[:100]}...")
            
            # Extract actions from response
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
            
        except Exception as e:
            self.logger.error(f"Unexpected error in ToolAgentNode: {e}")
            return {"route": "finish", "error": f"Tool agent error: {e}"}
    
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
- **Podcast generation**: Use the podcastify tool for high-quality podcast creation

When using tools, include them in your action list before sending the response.
"""
        
        return base_prompt + tool_prompt
    
    def _register_tools(self) -> None:
        """Register all available tools with the registry."""
        from ...tools import (
            WebSearchTool, CalculatorTool, FileReadTool, FileWriteTool,
            DatabaseQueryTool, WeatherTool, PolymarketTool, EmailSearchTool, EmailSendTool,
            PodcastifyTool
        )
        
        tools = [
            WebSearchTool(),
            CalculatorTool(),
            FileReadTool(),
            FileWriteTool(),
            DatabaseQueryTool(),
            WeatherTool(),
            PolymarketTool(),
            EmailSearchTool(),
            EmailSendTool(),
            PodcastifyTool()
        ]
        
        for tool in tools:
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

### SPECIAL INSTRUCTIONS FOR PODCAST GENERATION
When users ask for podcast generation (e.g., "make a podcast", "generate a podcast", "create a podcast"), you MUST use the podcastify tool instead of the basic content generation. The podcastify tool creates high-quality podcast episodes with proper structure, script, and audio.

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
    The user wants a podcast about local LLMs. I should use the podcastify tool to create a high-quality podcast episode.

response: |
    I'll create a podcast about local LLMs for you using the podcastify tool.

tools:
  - name: podcastify
    parameters:
      topic: "Local LLMs and their applications"
      duration_minutes: 10
      style: "conversational"
      target_audience: "general"
      voice_preference: "professional"
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