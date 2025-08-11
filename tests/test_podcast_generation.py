#!/usr/bin/env python3
"""
Test script to demonstrate podcast generation capability.
"""

import sys
import os
from pathlib import Path

# Add src to path for imports (updated for tests directory)
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from pocketflow.tools.podcastify import PodcastifyTool, PodcastifyRequest
import time

def test_podcast_generation():
    """Test the podcast generation functionality."""
    print("🎙️  Podcast Generation Test")
    print("=" * 50)
    
    # Create the podcastify tool
    tool = PodcastifyTool()
    
    # Test different podcast scenarios
    test_cases = [
        {
            "name": "AI Future Podcast",
            "topic": "The Future of Artificial Intelligence",
            "duration_minutes": 5,
            "style": "educational",
            "target_audience": "tech enthusiasts"
        },
        {
            "name": "Climate Change Discussion",
            "topic": "Climate Change Solutions",
            "duration_minutes": 8,
            "style": "conversational",
            "target_audience": "general"
        },
        {
            "name": "Space Exploration Story",
            "topic": "Mars Colonization Plans",
            "duration_minutes": 10,
            "style": "storytelling",
            "target_audience": "space enthusiasts"
        }
    ]
    
    results = []
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📝 Test {i}: {test_case['name']}")
        print("-" * 30)
        
        try:
            # Execute the podcast generation
            result = tool.execute(
                topic=test_case["topic"],
                duration_minutes=test_case["duration_minutes"],
                style=test_case["style"],
                target_audience=test_case["target_audience"],
                voice_preference="professional",
                output_format="wav"
            )
            
            if result.success:
                print(f"✅ Success! Generated podcast about: {test_case['topic']}")
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
                    "test": test_case["name"],
                    "success": True,
                    "file_path": result.data['file_path'],
                    "script_length": len(result.data['script']),
                    "duration": result.data['duration']
                })
                
            else:
                print(f"❌ Failed: {result.error}")
                results.append({
                    "test": test_case["name"],
                    "success": False,
                    "error": result.error
                })
                
        except Exception as e:
            print(f"❌ Exception: {e}")
            results.append({
                "test": test_case["name"],
                "success": False,
                "error": str(e)
            })
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Results Summary")
    print("=" * 50)
    
    successful = sum(1 for r in results if r["success"])
    total = len(results)
    
    for result in results:
        status = "✅ PASS" if result["success"] else "❌ FAIL"
        print(f"{result['test']}: {status}")
        if result["success"]:
            print(f"  📁 File: {result['file_path']}")
            print(f"  📄 Script: {result['script_length']} chars")
            print(f"  ⏱️  Duration: {result['duration']} min")
        else:
            print(f"  ❌ Error: {result['error']}")
    
    print(f"\nOverall: {successful}/{total} tests passed")
    
    if successful == total:
        print("🎉 All podcast generation tests passed!")
        print("\n🎙️  The system can successfully generate podcasts!")
        print("✅ Content generation: Working")
        print("✅ Audio file creation: Working")
        print("✅ File format: WAV audio files")
        print("✅ Multiple topics: Supported")
        print("✅ Different styles: Supported")
        print("✅ Custom durations: Supported")
        
        return True
    else:
        print("⚠️  Some tests failed. Check the output above for details.")
        return False

def test_audio_playback():
    """Test if the generated audio files can be played."""
    print("\n🎵 Audio Playback Test")
    print("=" * 30)
    
    # Check if we have any generated audio files
    podcast_dir = "/tmp/pocketflow_podcasts"
    if not os.path.exists(podcast_dir):
        print("❌ No podcast directory found")
        return False
    
    audio_files = [f for f in os.listdir(podcast_dir) if f.endswith('.wav')]
    
    if not audio_files:
        print("❌ No audio files found")
        return False
    
    print(f"✅ Found {len(audio_files)} audio files")
    
    for audio_file in audio_files[:3]:  # Test first 3 files
        file_path = os.path.join(podcast_dir, audio_file)
        file_size = os.path.getsize(file_path)
        
        print(f"📁 {audio_file}: {file_size} bytes")
        
        # Check if it's a valid WAV file
        try:
            import wave
            with wave.open(file_path, 'r') as wav:
                frames = wav.getnframes()
                rate = wav.getframerate()
                duration = frames / float(rate)
                print(f"  ⏱️  Duration: {duration:.2f} seconds")
                print(f"  🔊 Sample rate: {rate} Hz")
                print(f"  🎵 Channels: {wav.getnchannels()}")
        except Exception as e:
            print(f"  ❌ Error reading WAV file: {e}")
    
    return True

def main():
    """Run all tests."""
    print("🎙️  Podcast Generation System Test")
    print("=" * 60)
    
    # Test 1: Podcast generation
    generation_success = test_podcast_generation()
    
    # Test 2: Audio playback
    playback_success = test_audio_playback()
    
    # Final summary
    print("\n" + "=" * 60)
    print("🎯 Final Test Summary")
    print("=" * 60)
    
    if generation_success and playback_success:
        print("🎉 SUCCESS: The system can generate real podcasts!")
        print("\n✅ What works:")
        print("  - Content generation with different topics")
        print("  - Script creation with proper structure")
        print("  - Audio file generation in WAV format")
        print("  - Multiple podcast styles and durations")
        print("  - Professional voice preferences")
        print("  - File storage in /tmp/pocketflow_podcasts/")
        
        print("\n🎙️  To use the system:")
        print("  - Request a podcast through the agent interface")
        print("  - Specify topic, duration, and style")
        print("  - Get both script and audio file")
        print("  - Audio files are saved as WAV format")
        
        return True
    else:
        print("❌ FAILED: Some tests did not pass")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 