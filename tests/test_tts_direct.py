#!/usr/bin/env python3
"""
Direct TTS test to isolate audio generation issues.
"""

import os
import subprocess
import sys

def test_pyttsx3():
    """Test pyttsx3 directly."""
    print("🔧 Testing pyttsx3...")
    try:
        import pyttsx3
        engine = pyttsx3.init()
        voices = engine.getProperty('voices')
        print(f"✅ pyttsx3 initialized with {len(voices)} voices")
        
        # Try to save a test file
        test_file = "/tmp/pocketflow_podcasts/pyttsx3_test.wav"
        engine.save_to_file("This is a test of pyttsx3 text to speech", test_file)
        engine.runAndWait()
        
        if os.path.exists(test_file) and os.path.getsize(test_file) > 0:
            print(f"✅ pyttsx3 successfully created: {test_file} ({os.path.getsize(test_file)} bytes)")
            return True
        else:
            print(f"❌ pyttsx3 failed to create file or file is empty")
            return False
    except Exception as e:
        print(f"❌ pyttsx3 failed: {e}")
        return False

def test_espeak_direct():
    """Test espeak directly."""
    print("🔧 Testing espeak directly...")
    try:
        test_file = "/tmp/pocketflow_podcasts/espeak_test.wav"
        cmd = [
            '/usr/bin/espeak',
            '-s', '150',
            '-v', 'en',
            '-w', test_file,
            'This is a test of espeak text to speech'
        ]
        
        result = subprocess.run(cmd, check=True, capture_output=True, text=True, timeout=30)
        print(f"✅ espeak command completed: {result.returncode}")
        print(f"   stdout: {result.stdout[:100]}...")
        print(f"   stderr: {result.stderr[:100]}...")
        
        if os.path.exists(test_file) and os.path.getsize(test_file) > 0:
            print(f"✅ espeak successfully created: {test_file} ({os.path.getsize(test_file)} bytes)")
            return True
        else:
            print(f"❌ espeak failed to create file or file is empty")
            return False
    except subprocess.TimeoutExpired:
        print("❌ espeak command timed out")
        return False
    except subprocess.CalledProcessError as e:
        print(f"❌ espeak command failed: {e}")
        print(f"   stderr: {e.stderr}")
        return False
    except Exception as e:
        print(f"❌ espeak failed: {e}")
        return False

def test_espeak_with_file():
    """Test espeak with text file input."""
    print("🔧 Testing espeak with text file...")
    try:
        test_file = "/tmp/pocketflow_podcasts/espeak_file_test.wav"
        text_file = "/tmp/pocketflow_podcasts/test_text.txt"
        
        # Create text file
        with open(text_file, 'w') as f:
            f.write("This is a test of espeak with text file input")
        
        cmd = [
            '/usr/bin/espeak',
            '-s', '150',
            '-v', 'en',
            '-w', test_file,
            '-f', text_file
        ]
        
        result = subprocess.run(cmd, check=True, capture_output=True, text=True, timeout=30)
        print(f"✅ espeak file command completed: {result.returncode}")
        
        if os.path.exists(test_file) and os.path.getsize(test_file) > 0:
            print(f"✅ espeak file successfully created: {test_file} ({os.path.getsize(test_file)} bytes)")
            return True
        else:
            print(f"❌ espeak file failed to create file or file is empty")
            return False
    except Exception as e:
        print(f"❌ espeak file failed: {e}")
        return False

def main():
    print("🎙️ Direct TTS Test")
    print("=" * 50)
    
    # Ensure directory exists
    os.makedirs("/tmp/pocketflow_podcasts", exist_ok=True)
    print(f"📂 Using directory: /tmp/pocketflow_podcasts")
    
    results = []
    
    # Test each TTS method
    results.append(("pyttsx3", test_pyttsx3()))
    results.append(("espeak direct", test_espeak_direct()))
    results.append(("espeak file", test_espeak_with_file()))
    
    print("\n📊 Results:")
    for method, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"   {method}: {status}")
    
    # Check what files were created
    print(f"\n📁 Files in /tmp/pocketflow_podcasts:")
    for file in os.listdir("/tmp/pocketflow_podcasts"):
        path = os.path.join("/tmp/pocketflow_podcasts", file)
        size = os.path.getsize(path)
        print(f"   {file}: {size} bytes")

if __name__ == "__main__":
    main() 