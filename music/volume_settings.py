"""
Volume settings management for music and sound effects.
Allows users to adjust volume levels for music and SFX.
"""
import json
import os

# Default volume levels (0.0 to 1.0)
DEFAULT_MUSIC_VOLUME = 0.7
DEFAULT_SFX_VOLUME = 0.8

# Settings file path
SETTINGS_FILE = "volume_settings.json"

# Global volume variables
_music_volume = DEFAULT_MUSIC_VOLUME
_sfx_volume = DEFAULT_SFX_VOLUME

def load_settings():
    """Load volume settings from file."""
    global _music_volume, _sfx_volume
    
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, 'r') as f:
                settings = json.load(f)
                _music_volume = settings.get('music_volume', DEFAULT_MUSIC_VOLUME)
                _sfx_volume = settings.get('sfx_volume', DEFAULT_SFX_VOLUME)
                # Clamp values between 0.0 and 1.0
                _music_volume = max(0.0, min(1.0, _music_volume))
                _sfx_volume = max(0.0, min(1.0, _sfx_volume))
        except Exception as e:
            print(f"Error loading volume settings: {e}")
            _music_volume = DEFAULT_MUSIC_VOLUME
            _sfx_volume = DEFAULT_SFX_VOLUME
    else:
        # Use defaults if file doesn't exist
        _music_volume = DEFAULT_MUSIC_VOLUME
        _sfx_volume = DEFAULT_SFX_VOLUME

def save_settings():
    """Save volume settings to file."""
    global _music_volume, _sfx_volume
    
    try:
        settings = {
            'music_volume': _music_volume,
            'sfx_volume': _sfx_volume
        }
        with open(SETTINGS_FILE, 'w') as f:
            json.dump(settings, f)
    except Exception as e:
        print(f"Error saving volume settings: {e}")

def get_music_volume():
    """Get the current music volume (0.0 to 1.0)."""
    return _music_volume

def get_sfx_volume():
    """Get the current SFX volume (0.0 to 1.0)."""
    return _sfx_volume

def set_music_volume(volume):
    """Set the music volume (0.0 to 1.0)."""
    global _music_volume
    _music_volume = max(0.0, min(1.0, volume))
    save_settings()
    # Update currently playing music volume
    try:
        import pygame
        if pygame.mixer.get_init():
            pygame.mixer.music.set_volume(_music_volume)
    except Exception:
        pass

def set_sfx_volume(volume):
    """Set the SFX volume (0.0 to 1.0)."""
    global _sfx_volume
    _sfx_volume = max(0.0, min(1.0, volume))
    save_settings()

def increase_music_volume(amount=0.1):
    """Increase music volume by specified amount."""
    set_music_volume(_music_volume + amount)

def decrease_music_volume(amount=0.1):
    """Decrease music volume by specified amount."""
    set_music_volume(_music_volume - amount)

def increase_sfx_volume(amount=0.1):
    """Increase SFX volume by specified amount."""
    set_sfx_volume(_sfx_volume + amount)

def decrease_sfx_volume(amount=0.1):
    """Decrease SFX volume by specified amount."""
    set_sfx_volume(_sfx_volume - amount)

# Load settings on import
load_settings()

