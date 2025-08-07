# Podcastify Tool for PocketFlow Agents

## 🎯 Overview

Podcastify is now structured as a proper PocketFlow tool that can be easily integrated into agent workflows. The tool follows PocketFlow's standard tool pattern and provides a clean interface for content creation.

## 🏗️ Tool Structure

### Core Components

1. **`PodcastifyTool`**: Main tool class with standard interface
2. **`PodcastifyRequest`**: Request structure for podcast generation
3. **`ToolRegistry`**: Registry for managing tools
4. **PocketFlow Nodes**: Modular workflow components

### Tool Interface

```python
class PodcastifyTool:
    def __init__(self):
        self.name = "podcastify"
        self.description = "Generate podcast episodes with local AI components"
        self.capabilities = [
            "podcast_generation",
            "script_writing", 
            "audio_synthesis",
            "topic_analysis",
            "content_structure"
        ]
    
    def get_info(self) -> Dict[str, Any]:
        """Get tool information."""
    
    def execute(self, request: PodcastifyRequest) -> Dict[str, Any]:
        """Execute the podcast generation tool."""
```

## 🔧 Usage Examples

### Basic Tool Usage

```python
from podcastify_tool import PodcastifyTool, PodcastifyRequest

# Create tool
tool = PodcastifyTool()

# Create request
request = PodcastifyRequest(
    topic="The Future of AI",
    duration_minutes=15,
    style="conversational",
    target_audience="general"
)

# Execute tool
result = tool.execute(request)

if result.get("success", False):
    print(f"Podcast created: {result['episode_title']}")
    print(f"Audio file: {result['audio_file']}")
```

### Agent Integration

```python
from podcastify_tool import ToolRegistry, PodcastifyRequest

# Create tool registry
registry = ToolRegistry()

# Get tool
podcastify_tool = registry.get_tool("podcastify")

# Use in agent workflow
request = PodcastifyRequest(topic="Your Topic")
result = podcastify_tool.execute(request)
```

### Full Agent Workflow

```python
from agent_integration_example import ContentCreationAgent

# Create agent
agent = ContentCreationAgent()

# Create content
result = agent.create_content("Create a podcast about AI")

# Check results
if result["final_content"]["status"] == "success":
    print("Content created successfully!")
```

## 📋 Tool Parameters

### PodcastifyRequest

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `topic` | str | Required | Main topic for the podcast |
| `duration_minutes` | int | 10 | Duration in minutes (5-30) |
| `style` | str | "conversational" | Style: conversational, educational, storytelling |
| `target_audience` | str | "general" | Target audience |
| `voice_preference` | str | "professional" | Voice style: professional, casual, friendly |
| `output_format` | str | "wav" | Audio format: wav, mp3 |

## 🎙️ Tool Capabilities

### Available Capabilities

- **`podcast_generation`**: Generate complete podcast episodes
- **`script_writing`**: Create engaging podcast scripts
- **`audio_synthesis`**: Convert text to high-quality audio
- **`topic_analysis`**: Analyze and structure podcast topics
- **`content_structure`**: Organize content into logical sections

### Tool Information

```python
tool_info = tool.get_info()
print(f"Name: {tool_info['name']}")
print(f"Description: {tool_info['description']}")
print(f"Capabilities: {tool_info['capabilities']}")
print(f"Parameters: {tool_info['parameters']}")
```

## 🔄 Workflow Integration

### Node-Based Integration

The tool can be integrated into PocketFlow workflows using nodes:

```python
class PodcastifyToolNode(Node):
    def __init__(self):
        super().__init__()
        self.tool_registry = ToolRegistry()
        self.podcastify_tool = self.tool_registry.get_tool("podcastify")
    
    def exec(self, tool_request: Dict[str, Any]) -> Dict[str, Any]:
        # Execute the tool
        request = PodcastifyRequest(**tool_request)
        return self.podcastify_tool.execute(request)
```

### Conditional Workflow

```python
# Create flow with conditional branching
content_analysis - "use_podcastify" >> podcastify_tool >> content_delivery
content_analysis - "skip_content" >> content_delivery
```

## 📊 Tool Results

### Success Response

```python
{
    "success": True,
    "tool": "podcastify",
    "content_type": "podcast",
    "script": "Complete podcast script...",
    "audio_file": "output/generated_podcast.wav",
    "episode_title": "Episode Title",
    "duration_minutes": 15,
    "topic": "The Future of AI",
    "metadata": {
        "style": "conversational",
        "target_audience": "general",
        "voice_preference": "professional",
        "output_format": "wav"
    }
}
```

### Error Response

```python
{
    "success": False,
    "tool": "podcastify",
    "error": "Error message",
    "content_type": "podcast"
}
```

## 🛠️ Customization

### Adding New Tools

```python
class CustomTool:
    def __init__(self):
        self.name = "custom_tool"
        self.description = "Custom tool description"
        self.capabilities = ["capability1", "capability2"]
    
    def get_info(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "capabilities": self.capabilities
        }
    
    def execute(self, request) -> Dict[str, Any]:
        # Tool implementation
        pass

# Register custom tool
registry = ToolRegistry()
registry.register_tool(CustomTool())
```

### Extending Podcastify

```python
class ExtendedPodcastifyTool(PodcastifyTool):
    def __init__(self):
        super().__init__()
        self.capabilities.append("custom_capability")
    
    def execute(self, request: PodcastifyRequest) -> Dict[str, Any]:
        # Add custom logic
        result = super().execute(request)
        # Modify result
        return result
```

## 🔗 Integration Patterns

### Pattern 1: Direct Tool Usage

```python
# Simple direct usage
tool = PodcastifyTool()
result = tool.execute(request)
```

### Pattern 2: Registry-Based Usage

```python
# Using tool registry
registry = ToolRegistry()
tool = registry.get_tool("podcastify")
result = tool.execute(request)
```

### Pattern 3: Agent Workflow Integration

```python
# Integrated into agent workflow
agent = ContentCreationAgent()
result = agent.create_content("Create podcast about AI")
```

### Pattern 4: Node-Based Integration

```python
# Using as PocketFlow node
podcastify_node = PodcastifyToolNode()
flow = Flow(start=podcastify_node)
```

## 📚 Best Practices

1. **Error Handling**: Always check `success` field in tool results
2. **Parameter Validation**: Validate request parameters before execution
3. **Resource Management**: Clean up temporary files and resources
4. **Logging**: Add appropriate logging for debugging
5. **Testing**: Test tools with various input parameters

## 🎯 Next Steps

1. **Customize Prompts**: Modify prompts in nodes for your specific use case
2. **Add Error Handling**: Implement robust error handling and retry logic
3. **Optimize Performance**: Add caching and parallel processing
4. **Extend Capabilities**: Add new tools and capabilities to the registry
5. **Integration**: Integrate with your existing PocketFlow applications

---

**Ready to create amazing content with PocketFlow tools! 🎙️✨** 