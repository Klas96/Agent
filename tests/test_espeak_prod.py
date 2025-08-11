#!/usr/bin/env python3

import subprocess
import os

# Test espeak in production environment
try:
    output_file = "/tmp/pocketflow_podcasts/test_espeak_prod.wav"
    
    # Create directory
    os.makedirs("/tmp/pocketflow_podcasts", exist_ok=True)
    
    # Same command as in the code
    espeak_cmd = [
        '/usr/bin/espeak',
        '-s', '150',  # Speech rate
        '-v', 'en',   # English voice
        '-w', output_file,  # Write to file
        "Hello world this is a test from the production environment"
    ]
    
    print(f"Running: {' '.join(espeak_cmd)}")
    result = subprocess.run(espeak_cmd, check=True, capture_output=True, text=True)
    print(f"Return code: {result.returncode}")
    print(f"Stdout: {result.stdout}")
    print(f"Stderr: {result.stderr}")
    
    if os.path.exists(output_file):
        size = os.path.getsize(output_file)
        print(f"✅ File created: {output_file} ({size} bytes)")
    else:
        print(f"❌ File not created: {output_file}")
        
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
