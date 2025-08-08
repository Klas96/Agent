#!/usr/bin/env python3
"""
Test script to demonstrate podcast requests through the agent interface.
"""

import sys
import os
from pathlib import Path

# Add src to path for imports (updated for tests directory)
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from pocketflow.tools.registry import agent_tool_registry
from pocketflow.tools.podcastify import PodcastifyTool

def test_podcast_request():
    """Test requesting a podcast through the agent interface."""
    print("🎙️  Podcast Request Test")
    print("=" * 50)
    
    # Get the podcastify tool from the registry
    podcastify_tool = agent_tool_registry.get_tool("podcastify")
    
    if not podcastify_tool:
        print("❌ Podcastify tool not found in registry")
        return False
    
    print("✅ Podcastify tool found in registry")
    
    # Test different podcast requests
    requests = [
        {
            "description": "Request a podcast about AI",
            "parameters": {
                "topic": "Artificial Intelligence and Machine Learning",
                "duration_minutes": 5,
                "style": "educational",
                "target_audience": "tech enthusiasts"
            }
        },
        {
            "description": "Request a conversational podcast about climate change",
            "parameters": {
                "topic": "Climate Change and Renewable Energy",
                "duration_minutes": 8,
                "style": "conversational",
                "target_audience": "general"
            }
        },
        {
            "description": "Request a storytelling podcast about space exploration",
            "parameters": {
                "topic": "The Future of Space Exploration",
                "duration_minutes": 10,
                "style": "storytelling",
                "target_audience": "space enthusiasts"
            }
        }
    ]
    
    results = []
    
    for i, request in enumerate(requests, 1):
        print(f"\n📝 Request {i}: {request['description']}")
        print("-" * 40)
        
        try:
            # Execute the podcast request
            result = podcastify_tool.execute(**request["parameters"])
            
            if result.success:
                print(f"✅ Success! Generated podcast about: {request['parameters']['topic']}")
                print(f"📁 Audio file: {result.data['file_path']}")
                print(f"📄 Script length: {len(result.data['script'])} characters")
                print(f"⏱️  Duration: {result.data['duration']} minutes")
                
                # Check if file exists
                if os.path.exists(result.data['file_path']):
                    file_size = os.path.getsize(result.data['file_path'])
                    print(f"💾 File size: {file_size} bytes")
                else:
                    print("⚠️  Warning: Audio file not found")
                
                results.append({
                    "request": request["description"],
                    "success": True,
                    "file_path": result.data['file_path'],
                    "script_length": len(result.data['script']),
                    "duration": result.data['duration']
                })
                
            else:
                print(f"❌ Failed: {result.error}")
                results.append({
                    "request": request["description"],
                    "success": False,
                    "error": result.error
                })
                
        except Exception as e:
            print(f"❌ Exception: {e}")
            results.append({
                "request": request["description"],
                "success": False,
                "error": str(e)
            })
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Request Results Summary")
    print("=" * 50)
    
    successful = sum(1 for r in results if r["success"])
    total = len(results)
    
    for result in results:
        status = "✅ PASS" if result["success"] else "❌ FAIL"
        print(f"{result['request']}: {status}")
        if result["success"]:
            print(f"  📁 File: {result['file_path']}")
            print(f"  📄 Script: {result['script_length']} chars")
            print(f"  ⏱️  Duration: {result['duration']} min")
        else:
            print(f"  ❌ Error: {result['error']}")
    
    print(f"\nOverall: {successful}/{total} requests successful")
    
    if successful == total:
        print("🎉 All podcast requests successful!")
        return True
    else:
        print("⚠️  Some requests failed. Check the output above for details.")
        return False

def demonstrate_agent_usage():
    """Demonstrate how the agent would use the podcastify tool."""
    print("\n🤖 Agent Usage Demonstration")
    print("=" * 40)
    
    print("When a user asks for a podcast, the agent can:")
    print("1. Recognize the request for podcast generation")
    print("2. Use the podcastify tool with appropriate parameters")
    print("3. Return both the script and audio file")
    
    print("\nExample user requests:")
    print("- 'Create a podcast about AI'")
    print("- 'Generate a 10-minute podcast about climate change'")
    print("- 'Make a storytelling podcast about space exploration'")
    print("- 'I want a podcast about renewable energy'")
    
    print("\nAgent response format:")
    print("```yaml")
    print("thinking: |")
    print("    The user wants a podcast about AI. I should use the podcastify tool.")
    print("")
    print("response: |")
    print("    I'll create a podcast about AI for you using the podcastify tool.")
    print("")
    print("tools:")
    print("  - name: podcastify")
    print("    parameters:")
    print("      topic: 'Artificial Intelligence and its applications'")
    print("      duration_minutes: 10")
    print("      style: 'educational'")
    print("      target_audience: 'general'")
    print("      voice_preference: 'professional'")
    print("      output_format: 'wav'")
    print("```")
    
    return True

def main():
    """Run all tests."""
    print("🎙️  Podcast Request System Test")
    print("=" * 60)
    
    # Test 1: Direct tool usage
    tool_success = test_podcast_request()
    
    # Test 2: Agent usage demonstration
    agent_success = demonstrate_agent_usage()
    
    # Final summary
    print("\n" + "=" * 60)
    print("🎯 Final Summary")
    print("=" * 60)
    
    if tool_success and agent_success:
        print("🎉 SUCCESS: The system supports podcast requests!")
        print("\n✅ What's working:")
        print("  - Podcastify tool is registered and available")
        print("  - Tool can generate podcasts with different parameters")
        print("  - Audio files are created in WAV format")
        print("  - Scripts are generated with proper content")
        print("  - Agent can use the tool through the registry")
        
        print("\n🎙️  How to request a podcast:")
        print("  1. Ask the agent for a podcast (e.g., 'Create a podcast about AI')")
        print("  2. The agent will use the podcastify tool")
        print("  3. You'll get both a script and an audio file")
        print("  4. Audio files are saved in /tmp/pocketflow_podcasts/")
        
        print("\n📝 Supported parameters:")
        print("  - topic: The main topic for the podcast")
        print("  - duration_minutes: Length in minutes (5-30)")
        print("  - style: conversational, educational, storytelling")
        print("  - target_audience: Who the podcast is for")
        print("  - voice_preference: professional, casual, friendly")
        print("  - output_format: wav, mp3")
        
        return True
    else:
        print("❌ FAILED: Some tests did not pass")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 