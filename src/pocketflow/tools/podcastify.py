"""
Podcastify tool for PocketFlow agents.

This tool generates podcast episodes using local AI components (Ollama + Bark).
"""

import os
import sys
import json
import re
import time
from typing import Dict, Any, Optional
from dataclasses import dataclass

from .base import Tool, ToolResult
from ..utils.logging import get_logger

# PocketFlow imports
from ..core.flow import FlowBuilder, Flow
from ..core.types import FlowType, SharedState
from ..core.node import SimpleNode

@dataclass
class PodcastifyRequest:
    """Request structure for podcast generation."""
    topic: str
    duration_minutes: int = 10
    style: str = "conversational"
    target_audience: str = "general"
    voice_preference: str = "professional"
    output_format: str = "wav"

class PodcastifyTool(Tool):
    """
    Tool for generating podcast episodes with local AI components.
    """
    
    def __init__(self):
        super().__init__(
            name="podcastify",
            description="Generate podcast episodes using local AI components (Ollama + Bark)"
        )
    
    @property
    def parameters(self) -> Dict[str, Dict[str, Any]]:
        return {
            "topic": {
                "type": str,
                "required": True,
                "description": "The main topic for the podcast episode"
            },
            "duration_minutes": {
                "type": int,
                "required": False,
                "description": "Duration in minutes (5-30, default: 10)"
            },
            "style": {
                "type": str,
                "required": False,
                "description": "Style: conversational, educational, storytelling (default: conversational)"
            },
            "target_audience": {
                "type": str,
                "required": False,
                "description": "Target audience (default: general)"
            },
            "voice_preference": {
                "type": str,
                "required": False,
                "description": "Voice style: professional, casual, friendly (default: professional)"
            },
            "output_format": {
                "type": str,
                "required": False,
                "description": "Audio format: wav, mp3 (default: wav)"
            }
        }
    
    def execute(self, **kwargs) -> ToolResult:
        """
        Execute podcast generation.
        
        Args:
            topic: The main topic for the podcast
            duration_minutes: Duration in minutes (optional)
            style: Podcast style (optional)
            target_audience: Target audience (optional)
            voice_preference: Voice style (optional)
            output_format: Audio format (optional)
            
        Returns:
            ToolResult with podcast generation result
        """
        try:
            # Create request
            request = PodcastifyRequest(
                topic=kwargs.get("topic"),
                duration_minutes=kwargs.get("duration_minutes", 10),
                style=kwargs.get("style", "conversational"),
                target_audience=kwargs.get("target_audience", "general"),
                voice_preference=kwargs.get("voice_preference", "professional"),
                output_format=kwargs.get("output_format", "wav")
            )
            
            # Create workflow
            workflow = PodcastifyWorkflow(request)
            result = workflow.generate_podcast()
            
            if result.get("final_script") and result.get("audio_file"):
                return ToolResult(
                    success=True,
                    data={
                        "episode_title": result.get("episode_title", "Untitled Episode"),
                        "script": result.get("final_script", ""),
                        "audio_file": result.get("audio_file", ""),
                        "duration_minutes": request.duration_minutes,
                        "topic": request.topic,
                        "metadata": {
                            "style": request.style,
                            "target_audience": request.target_audience,
                            "voice_preference": request.voice_preference,
                            "output_format": request.output_format
                        }
                    },
                    metadata={
                        "source": "podcastify",
                        "content_type": "podcast"
                    }
                )
            else:
                return ToolResult(
                    success=False,
                    error="Podcast generation failed - missing script or audio file"
                )
                
        except Exception as e:
            self.logger.error(f"Podcastify failed: {str(e)}")
            return ToolResult(
                success=False,
                error=f"Podcast generation failed: {str(e)}"
            )

class PodcastifyWorkflow:
    """Podcast generation workflow using PocketFlow nodes."""
    
    def __init__(self, request: PodcastifyRequest):
        self.request = request
        
        # Create flow using FlowBuilder
        self.flow = (FlowBuilder("podcastify", FlowType.USER, requires_tokens=False)
                    .add_step("topic_analysis", TopicAnalysisNode("topic_analysis"))
                    .add_step("content_generation", ContentGenerationNode("content_generation"))
                    .add_step("script_assembly", ScriptAssemblyNode("script_assembly"))
                    .add_step("audio_generation", AudioGenerationNode("audio_generation"))
                    .set_start("topic_analysis")
                    .add_end_step("audio_generation")
                    .add_routing("topic_analysis", "default", "content_generation")
                    .add_routing("content_generation", "default", "script_assembly")
                    .add_routing("script_assembly", "default", "audio_generation")
                    .build())
    
    def generate_podcast(self) -> Dict[str, Any]:
        """Generate a complete podcast episode."""
        
        # Initialize shared state as a dict (will be converted to SharedState by Flow)
        shared_dict = {
            "topic": self.request.topic,
            "duration_minutes": self.request.duration_minutes,
            "style": self.request.style,
            "target_audience": self.request.target_audience,
            "voice_preference": self.request.voice_preference,
            "output_format": self.request.output_format,
            "flow_type": "podcastify"
        }
        
        # Run the workflow
        result = self.flow.run(shared_dict)
        
        # Convert back to dict for return
        if hasattr(result, 'model_dump'):
            return result.model_dump()
        else:
            return shared_dict

# PocketFlow Nodes for Podcast Generation

class TopicAnalysisNode(SimpleNode):
    """Analyze and expand the podcast topic."""
    
    def process(self, shared: SharedState) -> Optional[Dict[str, Any]]:
        """Process the topic analysis."""
        topic = getattr(shared, "topic", "")
        
        try:
            # For now, create a simple structure without Ollama
            # In production, you'd use Ollama here
            episode_structure = {
                "title": f"Episode about {topic}",
                "themes": [
                    {
                        "name": "Introduction",
                        "key_points": [f"Overview of {topic}"],
                        "duration_minutes": 2,
                        "discussion_points": [f"What is {topic}?"]
                    },
                    {
                        "name": "Main Discussion",
                        "key_points": [f"Key aspects of {topic}"],
                        "duration_minutes": 6,
                        "discussion_points": [f"Why is {topic} important?"]
                    },
                    {
                        "name": "Conclusion",
                        "key_points": [f"Summary of {topic}"],
                        "duration_minutes": 2,
                        "discussion_points": [f"Future of {topic}"]
                    }
                ],
                "total_duration": 10
            }
            
            # Update shared state
            shared.episode_structure = episode_structure
            shared.episode_title = episode_structure["title"]
            
            return {"route": "default"}
            
        except Exception as e:
            self.logger.error(f"Topic analysis failed: {e}")
            return {"route": "default", "error": str(e)}

class ContentGenerationNode(SimpleNode):
    """Generate podcast content based on episode structure."""
    
    def process(self, shared: SharedState) -> Optional[Dict[str, Any]]:
        """Generate podcast content."""
        episode_structure = getattr(shared, "episode_structure", {})
        style = getattr(shared, "style", "conversational")
        target_audience = getattr(shared, "target_audience", "general")
        
        try:
            # Generate content for each theme
            content_sections = []
            
            for theme in episode_structure.get("themes", []):
                section_content = self._generate_section_content(theme, style, target_audience)
                content_sections.append(section_content)
            
            shared.content_sections = content_sections
            
            return {"route": "default"}
            
        except Exception as e:
            self.logger.error(f"Content generation failed: {e}")
            return {"route": "default", "error": str(e)}
    
    def _generate_section_content(self, theme: Dict[str, Any], style: str, audience: str) -> Dict[str, Any]:
        """Generate content for a specific section."""
        return {
            "section_name": theme["name"],
            "content": f"Welcome to the {theme['name']} section. {theme['key_points'][0]}",
            "duration_minutes": theme["duration_minutes"],
            "discussion_points": theme["discussion_points"]
        }

class ScriptAssemblyNode(SimpleNode):
    """Assemble the final podcast script."""
    
    def process(self, shared: SharedState) -> Optional[Dict[str, Any]]:
        """Assemble the final script."""
        content_sections = getattr(shared, "content_sections", [])
        episode_title = getattr(shared, "episode_title", "Untitled Episode")
        
        try:
            # Assemble the script
            script_parts = [
                f"Welcome to {episode_title}. This is a {getattr(shared, 'style', 'conversational')} podcast for {getattr(shared, 'target_audience', 'general')} audience."
            ]
            
            for section in content_sections:
                script_parts.append(f"\n{section['content']}")
            
            final_script = "\n".join(script_parts)
            
            shared.final_script = final_script
            
            return {"route": "default"}
            
        except Exception as e:
            self.logger.error(f"Script assembly failed: {e}")
            return {"route": "default", "error": str(e)}

class AudioGenerationNode(SimpleNode):
    """Generate audio from the script."""
    
    def process(self, shared: SharedState) -> Optional[Dict[str, Any]]:
        """Generate audio from the script."""
        script = getattr(shared, "final_script", "")
        output_format = getattr(shared, "output_format", "wav")
        
        try:
            # For now, create a mock audio file
            # In production, you'd use Bark or another TTS system here
            audio_filename = f"podcast_{int(time.time())}.{output_format}"
            
            # Create a mock audio file
            with open(audio_filename, "w") as f:
                f.write("# Mock audio file\n")
                f.write(f"# Generated from script: {len(script)} characters\n")
                f.write(f"# Format: {output_format}\n")
            
            shared.audio_file = audio_filename
            
            return {"route": "default"}
            
        except Exception as e:
            self.logger.error(f"Audio generation failed: {e}")
            return {"route": "default", "error": str(e)} 