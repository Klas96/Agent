#!/usr/bin/env python3
"""
Agent Integration Example
Shows how to integrate Podcastify tool into existing PocketFlow agent workflows
"""

from typing import Dict, Any, List
from pocketflow import Node, Flow

# Import the Podcastify tool
from podcastify_tool import PodcastifyTool, PodcastifyRequest, ToolRegistry

class ContentRequestNode(Node):
    """Node that receives content requests and decides on tools to use."""
    
    def prep(self, shared: Dict[str, Any]) -> str:
        """Extract content request from shared store."""
        return shared.get("content_request", "")
    
    def exec(self, content_request: str) -> Dict[str, Any]:
        """Analyze content request and decide on appropriate tools."""
        try:
            from langchain_ollama import OllamaLLM
            
            llm = OllamaLLM(model="llama3:latest")
            
            prompt = f"""
            Analyze this content request: "{content_request}"
            
            Determine what type of content creation is needed:
            1. Is this suitable for a podcast? (yes/no)
            2. What tools would be most appropriate?
            3. What parameters should be used?
            
            Return as JSON:
            {{
                "content_type": "podcast/blog/video/etc",
                "suitable_for_podcast": true/false,
                "recommended_tool": "tool_name",
                "parameters": {{
                    "topic": "suggested_topic",
                    "duration_minutes": 10,
                    "style": "conversational",
                    "target_audience": "general"
                }},
                "reasoning": "explanation"
            }}
            """
            
            response = llm.invoke(prompt)
            
            # Try to extract JSON from response
            import re
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            else:
                return {
                    "content_type": "podcast",
                    "suitable_for_podcast": True,
                    "recommended_tool": "podcastify",
                    "parameters": {
                        "topic": content_request,
                        "duration_minutes": 10,
                        "style": "conversational",
                        "target_audience": "general"
                    },
                    "reasoning": "Default analysis"
                }
        except Exception as e:
            return {
                "content_type": "podcast",
                "suitable_for_podcast": True,
                "recommended_tool": "podcastify",
                "parameters": {
                    "topic": content_request,
                    "duration_minutes": 10,
                    "style": "conversational",
                    "target_audience": "general"
                },
                "reasoning": f"Error in analysis: {e}"
            }
    
    def post(self, shared: Dict[str, Any], prep_res: str, exec_res: Dict[str, Any]) -> str:
        """Store analysis and route to appropriate tool."""
        shared["content_analysis"] = exec_res
        
        if exec_res.get("suitable_for_podcast", False):
            shared["tool_request"] = exec_res
            return "use_podcastify"
        else:
            return "skip_content"

class PodcastifyToolNode(Node):
    """Node that uses the Podcastify tool."""
    
    def __init__(self):
        super().__init__()
        self.tool_registry = ToolRegistry()
        self.podcastify_tool = self.tool_registry.get_tool("podcastify")
    
    def prep(self, shared: Dict[str, Any]) -> Dict[str, Any]:
        """Extract tool request from shared store."""
        return shared.get("tool_request", {})
    
    def exec(self, tool_request: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the Podcastify tool."""
        parameters = tool_request.get("parameters", {})
        
        # Create PodcastifyRequest
        request = PodcastifyRequest(
            topic=parameters.get("topic", "General Discussion"),
            duration_minutes=parameters.get("duration_minutes", 10),
            style=parameters.get("style", "conversational"),
            target_audience=parameters.get("target_audience", "general"),
            voice_preference=parameters.get("voice_preference", "professional"),
            output_format=parameters.get("output_format", "wav")
        )
        
        # Execute the tool
        return self.podcastify_tool.execute(request)
    
    def post(self, shared: Dict[str, Any], prep_res: Dict[str, Any], exec_res: Dict[str, Any]) -> str:
        """Store tool results in shared store."""
        shared["tool_result"] = exec_res
        
        if exec_res.get("success", False):
            return "success"
        else:
            return "error"

class ContentDeliveryNode(Node):
    """Node that formats and delivers the final content."""
    
    def prep(self, shared: Dict[str, Any]) -> Dict[str, Any]:
        """Extract tool result from shared store."""
        return shared.get("tool_result", {})
    
    def exec(self, tool_result: Dict[str, Any]) -> Dict[str, Any]:
        """Format the content for delivery."""
        if tool_result.get("success", False):
            return {
                "status": "success",
                "content_type": tool_result.get("content_type", "unknown"),
                "title": tool_result.get("episode_title", "Untitled"),
                "script": tool_result.get("script", ""),
                "audio_file": tool_result.get("audio_file", ""),
                "metadata": tool_result.get("metadata", {}),
                "summary": f"Successfully created {tool_result.get('content_type', 'content')} about {tool_result.get('topic', 'unknown topic')}"
            }
        else:
            return {
                "status": "error",
                "error": tool_result.get("error", "Unknown error"),
                "summary": "Content creation failed"
            }
    
    def post(self, shared: Dict[str, Any], prep_res: Dict[str, Any], exec_res: Dict[str, Any]) -> str:
        """Store final content in shared store."""
        shared["final_content"] = exec_res
        return "default"

class ContentCreationAgent:
    """Agent that integrates Podcastify tool for content creation."""
    
    def __init__(self):
        # Create nodes
        self.content_request = ContentRequestNode()
        self.podcastify_tool = PodcastifyToolNode()
        self.content_delivery = ContentDeliveryNode()
        
        # Create flow with conditional branching
        self.content_request - "use_podcastify" >> self.podcastify_tool >> self.content_delivery
        self.content_request - "skip_content" >> self.content_delivery  # Skip tool execution
        
        self.flow = Flow(start=self.content_request)
    
    def create_content(self, content_request: str) -> Dict[str, Any]:
        """Create content based on the request."""
        shared = {"content_request": content_request}
        
        # Run the flow
        self.flow.run(shared)
        
        return {
            "content_analysis": shared.get("content_analysis", {}),
            "tool_result": shared.get("tool_result", {}),
            "final_content": shared.get("final_content", {})
        }

def main():
    """Demo the agent integration."""
    
    print("🤖 Content Creation Agent Demo")
    print("=" * 50)
    
    # Create agent
    agent = ContentCreationAgent()
    
    # Test different content requests
    test_requests = [
        "Create a podcast about artificial intelligence and its impact on society",
        "Write a blog post about cooking recipes",  # This might not be suitable for podcast
        "Generate a podcast episode about sustainable living and environmental conservation",
        "Make a video about machine learning algorithms"  # This might not be suitable for podcast
    ]
    
    for i, request in enumerate(test_requests, 1):
        print(f"\n{'='*60}")
        print(f"Test {i}: {request}")
        print(f"{'='*60}")
        
        result = agent.create_content(request)
        
        # Print results
        analysis = result.get("content_analysis", {})
        tool_result = result.get("tool_result", {})
        final_content = result.get("final_content", {})
        
        print(f"📊 Analysis:")
        print(f"   Content type: {analysis.get('content_type', 'N/A')}")
        print(f"   Suitable for podcast: {analysis.get('suitable_for_podcast', False)}")
        print(f"   Recommended tool: {analysis.get('recommended_tool', 'N/A')}")
        print(f"   Reasoning: {analysis.get('reasoning', 'N/A')}")
        
        if tool_result.get("success", False):
            print(f"\n🎙️ Tool Result:")
            print(f"   Title: {tool_result.get('episode_title', 'N/A')}")
            print(f"   Audio file: {tool_result.get('audio_file', 'N/A')}")
            print(f"   Script length: {len(tool_result.get('script', ''))} characters")
        elif tool_result:
            print(f"\n❌ Tool failed: {tool_result.get('error', 'Unknown error')}")
        
        print(f"\n📤 Final Content:")
        print(f"   Status: {final_content.get('status', 'N/A')}")
        print(f"   Summary: {final_content.get('summary', 'N/A')}")
        
        if final_content.get("status") == "success":
            print(f"   Content type: {final_content.get('content_type', 'N/A')}")
            print(f"   Title: {final_content.get('title', 'N/A')}")

if __name__ == "__main__":
    main() 