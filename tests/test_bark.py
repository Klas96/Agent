#!/usr/bin/env python3

import os
import sys

# Force CPU for Bark
os.environ['CUDA_VISIBLE_DEVICES'] = ''

# Fix PyTorch weights_only issue
import torch
original_load = torch.load
def safe_load(*args, **kwargs):
    kwargs['weights_only'] = False
    return original_load(*args, **kwargs)
torch.load = safe_load

try:
    from bark import generate_audio, SAMPLE_RATE
    import soundfile as sf
    
    print("Testing Bark audio generation...")
    
    # Generate a simple audio
    audio_array = generate_audio('Hello world', history_prompt='v2/en_speaker_6')
    
    # Save to file
    output_file = '/tmp/test_bark.wav'
    sf.write(output_file, audio_array, SAMPLE_RATE)
    
    print(f"Bark audio generation successful: {output_file}")
    print(f"Audio array shape: {audio_array.shape}")
    print(f"Sample rate: {SAMPLE_RATE}")
    
except Exception as e:
    print(f"Bark audio generation failed: {e}")
    import traceback
    traceback.print_exc() 