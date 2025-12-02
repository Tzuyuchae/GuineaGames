"""
Utility module for sound effects.
Generates a simple button click sound if no sound file is available.
"""
import pygame
import os
import wave
import struct
import math
import sys

# Add parent directory to path to import volume_settings
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
try:
    from volume_settings import get_sfx_volume
except ImportError:
    # Fallback if volume_settings not available
    def get_sfx_volume():
        return 0.8

# Global variable to store the button click sound
_button_click_sound = None

def _generate_click_sound():
    """Generate a simple button click sound programmatically."""
    sample_rate = 22050
    duration = 0.1
    frequency = 600  # Higher frequency for a more "clicky" sound
    
    frames = int(sample_rate * duration)
    samples = []
    
    for i in range(frames):
        # Create a simple sine wave with exponential fade out
        t = float(i) / sample_rate
        wave_value = math.sin(2 * math.pi * frequency * t)
        # Apply exponential fade out for a more natural sound
        fade = math.exp(-t * 15)  # Exponential decay
        sample = int(wave_value * 32767 * fade * 0.3)  # 30% volume
        samples.append(sample)
        samples.append(sample)  # Stereo (duplicate for both channels)
    
    # Convert to bytes for WAV file
    sample_bytes = b''.join(struct.pack('<h', s) for s in samples)
    
    # Create a temporary WAV file in memory
    import io
    wav_buffer = io.BytesIO()
    
    with wave.open(wav_buffer, 'wb') as wav_file:
        wav_file.setnchannels(2)  # Stereo
        wav_file.setsampwidth(2)  # 16-bit
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(sample_bytes)
    
    wav_buffer.seek(0)
    # pygame.mixer.Sound can load from a file-like object
    return pygame.mixer.Sound(wav_buffer)

def init_button_sfx():
    """Initialize the button click sound effect."""
    global _button_click_sound
    
    if _button_click_sound is not None:
        return _button_click_sound
    
    # Ensure mixer is initialized
    if not pygame.mixer.get_init():
        pygame.mixer.init()
    
    # Try to load from file first
    sound_paths = [
        "button_click.wav",
        "sfx/button_click.wav",
        "assets/sfx/button_click.wav",
        "frontend/Global Assets/Game Sprites/Mini-game/audio/button_click.wav"
    ]
    
    for path in sound_paths:
        if os.path.exists(path):
            try:
                _button_click_sound = pygame.mixer.Sound(path)
                return _button_click_sound
            except (pygame.error, Exception):
                continue
    
    # If no file found, generate a simple click sound
    try:
        _button_click_sound = _generate_click_sound()
    except Exception as e:
        # Fallback: create a minimal silent sound
        print(f"Warning: Could not generate button click sound: {e}")
        # Create a minimal silent sound using pygame
        try:
            import array
            arr = array.array('h', [0] * 100)
            _button_click_sound = pygame.sndarray.make_sound(arr)
        except Exception:
            _button_click_sound = None
    
    return _button_click_sound

def play_button_click():
    """Play the button click sound effect."""
    global _button_click_sound
    
    # Ensure mixer is initialized
    if not pygame.mixer.get_init():
        pygame.mixer.init()
    
    # Initialize sound if not already done
    if _button_click_sound is None:
        init_button_sfx()
    
    # Play the sound with volume control
    if _button_click_sound is not None:
        try:
            # Set volume based on SFX volume setting
            sfx_volume = get_sfx_volume()
            _button_click_sound.set_volume(sfx_volume)
            _button_click_sound.play()
        except Exception:
            # Silently fail if sound can't play
            pass

