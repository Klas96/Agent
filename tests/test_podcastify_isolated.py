#!/usr/bin/env python3
"""
Isolated test for podcastify tool without full PocketFlow dependencies.
"""

import sys
import os
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from dataclasses import dataclass
from typing import Dict, Any, Optional
import requests


@dataclass
class PodcastifyRequest:
    """Request structure for podcast generation."""
    topic: str
    duration_minutes: int = 10
    style: str = "conversational"
    target_audience: str = "general"
    voice_preference: str = "professional"
    output_format: str = "wav"


class MockSharedState:
    """Mock SharedState for testing."""
    
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
    
    def get(self, key, default=None):
        return getattr(self, key, default)


class TopicAnalysisNode:
    """Mock topic analysis node."""
    
    def process(self, shared) -> Optional[Dict[str, Any]]:
        """Analyze topic and create episode structure."""
        topic = getattr(shared, "topic", "Unknown Topic")
        
        # Mock episode structure
        episode_structure = {
            "introduction": f"Welcome to our episode about {topic}",
            "main_content": f"Today we'll explore {topic} in detail",
            "conclusion": f"Thanks for joining us to discuss {topic}"
        }
        
        # Mock episode title
        episode_title = f"Episode: {topic.title()}"
        
        # Update shared state
        shared.episode_structure = episode_structure
        shared.episode_title = episode_title
        
        return {"action": "default"}


class ContentGenerationNode:
    """Mock content generation node."""
    
    def process(self, shared) -> Optional[Dict[str, Any]]:
        """Generate content sections."""
        structure = getattr(shared, "episode_structure", {})
        style = getattr(shared, "style", "conversational")
        
        # Mock content sections
        content_sections = {
            "introduction": f"{structure.get('introduction', '')} - {style} style",
            "main_content": f"{structure.get('main_content', '')} - engaging content",
            "conclusion": f"{structure.get('conclusion', '')} - wrap up"
        }
        
        shared.content_sections = content_sections
        return {"action": "default"}


class ScriptAssemblyNode:
    """Mock script assembly node."""
    
    def process(self, shared) -> Optional[Dict[str, Any]]:
        """Assemble final script."""
        sections = getattr(shared, "content_sections", {})
        
        # Mock final script
        final_script = "\n\n".join([
            sections.get("introduction", ""),
            sections.get("main_content", ""),
            sections.get("conclusion", "")
        ])
        
        shared.final_script = final_script
        return {"action": "default"}


class AudioGenerationNode:
    """Mock audio generation node."""
    
    def process(self, shared) -> Optional[Dict[str, Any]]:
        """Generate audio file."""
        script = getattr(shared, "final_script", "")
        output_format = getattr(shared, "output_format", "wav")
        
        # Mock audio file path
        audio_file = f"/tmp/mock_podcast.{output_format}"
        
        shared.audio_file = audio_file
        return {"action": "default"}


class PodcastifyWorkflow:
    """Mock podcastify workflow."""
    
    def __init__(self, request: PodcastifyRequest):
        self.request = request
        self.topic_analysis = TopicAnalysisNode()
        self.content_generation = ContentGenerationNode()
        self.script_assembly = ScriptAssemblyNode()
        self.audio_generation = AudioGenerationNode()
    
    def generate_podcast(self) -> Dict[str, Any]:
        """Generate podcast using mock workflow."""
        # Initialize shared state
        shared = MockSharedState(
            topic=self.request.topic,
            duration_minutes=self.request.duration_minutes,
            style=self.request.style,
            target_audience=self.request.target_audience,
            voice_preference=self.request.voice_preference,
            output_format=self.request.output_format
        )
        
        # Run workflow
        self.topic_analysis.process(shared)
        self.content_generation.process(shared)
        self.script_assembly.process(shared)
        self.audio_generation.process(shared)
        
        return {
            "episode_title": getattr(shared, "episode_title", "Untitled"),
            "episode_structure": getattr(shared, "episode_structure", {}),
            "content_sections": getattr(shared, "content_sections", {}),
            "final_script": getattr(shared, "final_script", ""),
            "audio_file": getattr(shared, "audio_file", "")
        }


def test_podcastify_request():
    """Test PodcastifyRequest dataclass."""
    print("🎙️  Testing PodcastifyRequest")
    print("=" * 50)
    
    try:
        # Test basic request
        request = PodcastifyRequest(topic="AI Safety")
        assert request.topic == "AI Safety"
        assert request.duration_minutes == 10
        assert request.style == "conversational"
        print("✅ Basic request creation works")
        
        # Test custom parameters
        request = PodcastifyRequest(
            topic="Climate Change",
            duration_minutes=15,
            style="educational",
            target_audience="experts",
            voice_preference="casual",
            output_format="mp3"
        )
        assert request.topic == "Climate Change"
        assert request.duration_minutes == 15
        assert request.style == "educational"
        assert request.target_audience == "experts"
        assert request.voice_preference == "casual"
        assert request.output_format == "mp3"
        print("✅ Custom parameters work")
        
        return True
        
    except Exception as e:
        print(f"❌ Request test failed: {e}")
        return False


def test_podcastify_workflow():
    """Test podcastify workflow."""
    print("\n🎙️  Testing Podcastify Workflow")
    print("=" * 50)
    
    try:
        # Test basic workflow
        request = PodcastifyRequest(topic="Space Exploration")
        workflow = PodcastifyWorkflow(request)
        result = workflow.generate_podcast()
        
        # Check result structure
        assert "episode_title" in result
        assert "episode_structure" in result
        assert "content_sections" in result
        assert "final_script" in result
        assert "audio_file" in result
        print("✅ Workflow result structure is correct")
        
        # Check content
        assert "Space Exploration" in result["episode_title"]
        assert len(result["final_script"]) > 0
        assert result["audio_file"].endswith(".wav")
        print("✅ Workflow content generation works")
        
        return True
        
    except Exception as e:
        print(f"❌ Workflow test failed: {e}")
        return False


def test_ollama_connection():
    """Test Ollama connection."""
    print("\n🎙️  Testing Ollama Connection")
    print("=" * 50)
    
    try:
        # Test connection to local Ollama server
        response = requests.get("http://127.0.0.1:11434/api/tags", timeout=5)
        if response.status_code == 200:
            data = response.json()
            models = data.get("models", [])
            if models:
                model_names = [model.get("name", "") for model in models]
                print(f"✅ Ollama connection successful - Available models: {model_names}")
                return True
            else:
                print("✅ Ollama connection successful - No models available")
                return True
        else:
            print(f"❌ Ollama returned status code: {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Ollama connection failed - server not reachable")
        return False
    except Exception as e:
        print(f"❌ Ollama test failed: {e}")
        return False


def main():
    """Run all tests."""
    print("🎙️  Podcastify Tool Isolated Test Suite")
    print("=" * 60)
    
    tests = [
        ("PodcastifyRequest", test_podcastify_request),
        ("Podcastify Workflow", test_podcastify_workflow),
        ("Ollama Connection", test_ollama_connection)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 Test Results Summary")
    print("=" * 60)
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("🎉 All tests passed!")
    else:
        print("⚠️  Some tests failed. Check the output above for details.")


if __name__ == "__main__":
    main() 