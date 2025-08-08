"""
Tool-enabled agent node for PocketFlow.

This node allows the agent to use various tools to accomplish tasks.
"""

import json
import yaml
from typing import Dict, Any, List, Optional
from ...core.node import SimpleNode
from ...core.types import SharedState, NodeResult
from ...services.llm_service import LLMService
from ...utils.logging import get_logger
from ...tools import agent_tool_registry
from ...tools.base import ToolResult


class ToolAgentNode(SimpleNode):
    """
    Agent node that can use tools to accomplish tasks.
    """
    
    def __init__(self, name: str = "tool_agent"):
        super().__init__(name)
        self.logger = get_logger("ToolAgentNode")
        self.llm_service = LLMService()
        
        # Register available tools
        self._register_tools()
    
    def prep(self, shared: SharedState) -> Dict[str, Any]:
        """
        Prepare the agent with context and available tools.
        
        Args:
            shared: Shared state containing user input and context
            
        Returns:
            Dict containing user input, context, and available tools
        """
        user_input = shared.get("user_input", "")
        context = shared.get("context", "")
        user_email = shared.get("user", "")
        
        # Get available tools
        available_tools = agent_tool_registry.list_tools()
        
        return {
            "user_input": user_input,
            "context": context,
            "user_email": user_email,
            "available_tools": available_tools
        }
    
    def exec(self, prep_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the tool-enabled agent.
        
        Args:
            prep_result: Prepared data from prep()
            
        Returns:
            Dict containing agent response and tool usage
        """
        user_input = prep_result["user_input"]
        context = prep_result["context"]
        user_email = prep_result["user_email"]
        available_tools = prep_result["available_tools"]
        
        # Generate the agent prompt
        prompt = self._generate_agent_prompt(user_input, context, user_email, available_tools)
        
        # Get agent response
        messages = [{"role": "user", "content": prompt}]
        agent_response = self.llm_service.call_llm(messages)
        
        # Parse the response to extract tool usage
        parsed_response = self._parse_agent_response(agent_response)
        
        # Execute tools if requested
        tool_results = []
        if parsed_response.get("tools"):
            tool_results = self._execute_tools(parsed_response["tools"])
        
        return {
            "response": parsed_response.get("response", agent_response),
            "tools_used": tool_results,
            "thinking": parsed_response.get("thinking", "")
        }
    
    def process(self, shared: SharedState) -> Optional[Dict[str, Any]]:
        """
        Process the shared state and return any additional data.
        
        Args:
            shared: Shared state
            
        Returns:
            Optional dict with additional data
        """
        # This method is required by SimpleNode but not used in our implementation
        return None
    
    def post(self, shared: SharedState, prep_result: Dict[str, Any], exec_result: Dict[str, Any]) -> str:
        """
        Process the agent's response and tool results.
        
        Args:
            shared: Shared state
            prep_result: Data from prep()
            exec_result: Data from exec()
            
        Returns:
            Action to take next
        """
        response = exec_result["response"]
        tools_used = exec_result["tools_used"]
        thinking = exec_result["thinking"]
        
        # Store results in shared state
        shared["agent_response"] = response
        shared["tool_results"] = tools_used
        shared["agent_thinking"] = thinking
        
        # If tools were used, we might want to continue processing
        if tools_used:
            return "continue_with_tools"
        else:
            return "default"
    
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