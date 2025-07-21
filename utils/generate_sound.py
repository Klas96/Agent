"""
Simple music generation utility for PocketFlow.

This module provides basic music generation functionality using simple audio synthesis.
"""

import os
import numpy as np
import soundfile as sf
from typing import Dict, Any, Optional
import uuid


def generate_sound(prompt: str, subtype: str = "music", config: Optional[Dict[str, Any]] = None, urls: Optional[list] = None) -> str:
    """
    Generate a simple audio file based on the prompt.
    
    Args:
        prompt: Text description of the music to generate
        subtype: Type of audio (music, podcast, etc.)
        config: Configuration dictionary with duration, language, etc.
        urls: Optional list of URLs (for podcast generation)
        
    Returns:
        Path to the generated audio file
    """
    try:
        # Default configuration
        if config is None:
            config = {}
        
        duration = config.get("duration", 15)  # Default 15 seconds
        language = config.get("language", "en")
        
        # Create output directory if it doesn't exist
        output_dir = "generated"
        os.makedirs(output_dir, exist_ok=True)
        
        # Generate filename
        filename = f"{subtype}_{uuid.uuid4().hex[:8]}.wav"
        output_path = os.path.join(output_dir, filename)
        
        # Generate simple music based on prompt
        audio_data = _generate_simple_music(prompt, duration)
        
        # Save audio file
        sf.write(output_path, audio_data, 44100)
        
        print(f"Generated {subtype} file: {output_path}")
        return output_path
        
    except Exception as e:
        print(f"Error generating sound: {e}")
        # Return a placeholder file path
        return f"generated/{subtype}_placeholder.wav"


def _generate_simple_music(prompt: str, duration: int) -> np.ndarray:
    """
    Generate simple music based on prompt.
    
    Args:
        prompt: Text description of the music
        duration: Duration in seconds
        
    Returns:
        Audio data as numpy array
    """
    # Parse prompt for musical characteristics
    prompt_lower = prompt.lower()
    
    # Determine tempo and key based on prompt
    if any(word in prompt_lower for word in ["happy", "upbeat", "energetic"]):
        tempo = 120  # BPM
        key_freq = 440  # A4
    elif any(word in prompt_lower for word in ["sad", "melancholy", "slow"]):
        tempo = 60  # BPM
        key_freq = 330  # E4
    elif any(word in prompt_lower for word in ["electronic", "techno", "dance"]):
        tempo = 140  # BPM
        key_freq = 523  # C5
    else:
        tempo = 90  # BPM
        key_freq = 440  # A4
    
    # Generate audio
    sample_rate = 44100
    samples = int(duration * sample_rate)
    
    # Create time array
    t = np.linspace(0, duration, samples)
    
    # Generate melody
    melody = _create_melody(prompt, tempo, key_freq, duration)
    
    # Add some harmonics
    harmonics = 0.3 * np.sin(2 * np.pi * key_freq * 2 * t) + \
               0.2 * np.sin(2 * np.pi * key_freq * 3 * t)
    
    # Combine melody and harmonics
    audio = melody + harmonics
    
    # Normalize audio
    audio = audio / np.max(np.abs(audio)) * 0.7
    
    return audio


def _create_melody(prompt: str, tempo: int, base_freq: float, duration: int) -> np.ndarray:
    """
    Create a simple melody based on the prompt.
    
    Args:
        prompt: Text description
        tempo: Tempo in BPM
        base_freq: Base frequency
        duration: Duration in seconds
        
    Returns:
        Melody as numpy array
    """
    sample_rate = 44100
    samples = int(duration * sample_rate)
    t = np.linspace(0, duration, samples)
    
    # Simple scale based on prompt
    prompt_lower = prompt.lower()
    
    if any(word in prompt_lower for word in ["major", "happy", "bright"]):
        # Major scale frequencies (C major)
        scale_freqs = [base_freq, base_freq * 1.125, base_freq * 1.25, base_freq * 1.333,
                      base_freq * 1.5, base_freq * 1.667, base_freq * 1.875, base_freq * 2]
    elif any(word in prompt_lower for word in ["minor", "sad", "dark"]):
        # Minor scale frequencies (A minor)
        scale_freqs = [base_freq, base_freq * 1.125, base_freq * 1.2, base_freq * 1.333,
                      base_freq * 1.5, base_freq * 1.6, base_freq * 1.8, base_freq * 2]
    else:
        # Pentatonic scale (more neutral)
        scale_freqs = [base_freq, base_freq * 1.25, base_freq * 1.5, base_freq * 1.667, base_freq * 2]
    
    # Create melody pattern
    beat_duration = 60.0 / tempo  # seconds per beat
    notes_per_beat = 2  # 8th notes
    
    melody = np.zeros(samples)
    
    for i in range(int(duration / beat_duration * notes_per_beat)):
        # Choose random note from scale
        freq = np.random.choice(scale_freqs)
        
        # Calculate timing
        start_sample = int(i * beat_duration * sample_rate / notes_per_beat)
        end_sample = int((i + 1) * beat_duration * sample_rate / notes_per_beat)
        
        if start_sample < samples and end_sample <= samples:
            # Generate note with simple envelope
            note_samples = end_sample - start_sample
            note_t = np.linspace(0, beat_duration / notes_per_beat, note_samples)
            
            # Simple ADSR envelope
            attack = 0.1
            decay = 0.1
            sustain = 0.7
            release = 0.2
            
            envelope = np.ones(note_samples)
            attack_samples = int(attack * sample_rate)
            decay_samples = int(decay * sample_rate)
            release_samples = int(release * sample_rate)
            
            if attack_samples < note_samples:
                envelope[:attack_samples] = np.linspace(0, 1, attack_samples)
                if attack_samples + decay_samples < note_samples:
                    envelope[attack_samples:attack_samples + decay_samples] = np.linspace(1, sustain, decay_samples)
                    if note_samples - release_samples > attack_samples + decay_samples:
                        envelope[note_samples - release_samples:] = np.linspace(sustain, 0, release_samples)
            
            # Generate note
            note = np.sin(2 * np.pi * freq * note_t) * envelope
            melody[start_sample:end_sample] = note
    
    return melody


def generate_song(prompt: str, duration: int = 120) -> str:
    """
    Generate a song based on the prompt.
    
    Args:
        prompt: Text description of the song
        duration: Duration in seconds
        
    Returns:
        Path to the generated song file
    """
    config = {
        "duration": min(duration, 15),  # Limit to 15 seconds for demo
        "language": "en"
    }
    
    return generate_sound(prompt, "song", config)


def generate_podcast(prompt: str, duration: int = 60) -> str:
    """
    Generate a podcast based on the prompt.
    
    Args:
        prompt: Text description of the podcast
        duration: Duration in seconds
        
    Returns:
        Path to the generated podcast file
    """
    config = {
        "duration": min(duration, 15),  # Limit to 15 seconds for demo
        "language": "en"
    }
    
    return generate_sound(prompt, "podcast", config)


# Test function
if __name__ == "__main__":
    # Test music generation
    print("Testing music generation...")
    
    # Test different types of music
    test_prompts = [
        "A happy upbeat song about coding",
        "A sad melancholy tune about lost love",
        "An electronic dance track",
        "A peaceful ambient melody"
    ]
    
    for prompt in test_prompts:
        print(f"\nGenerating: {prompt}")
        file_path = generate_sound(prompt, "music", {"duration": 10})
        print(f"Generated: {file_path}")
