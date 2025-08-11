#!/usr/bin/env python3
import sys
sys.path.insert(0, "/opt/pocketflow/src")

# Test pyttsx3 directly
try:
    import pyttsx3
    print("✅ pyttsx3 imported successfully")
    
    # Try to initialize engine
    engine = pyttsx3.init()
    print("✅ pyttsx3 engine initialized")
    
    # Get available voices
    voices = engine.getProperty('voices')
    print(f"✅ Found {len(voices)} voices")
    
    # Test saving to file
    engine.save_to_file("Hello world, this is a test", "/tmp/test_audio.wav")
    engine.runAndWait()
    print("✅ Audio generation completed")
    
    # Check file
    import os
    if os.path.exists("/tmp/test_audio.wav"):
        size = os.path.getsize("/tmp/test_audio.wav")
        print(f"✅ Audio file created: {size} bytes")
    else:
        print("❌ Audio file not created")
        
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
