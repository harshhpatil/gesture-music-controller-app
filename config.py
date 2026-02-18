"""
Configuration module for the gesture music controller application.
Loads environment variables and provides configuration settings.
"""
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """Application configuration class"""
    
    # Flask settings
    SECRET_KEY = os.getenv('FLASK_SECRET_KEY', 'dev-secret-key-change-in-production')
    DEBUG = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    
    # Spotify API settings
    SPOTIFY_CLIENT_ID = os.getenv('SPOTIFY_CLIENT_ID')
    SPOTIFY_CLIENT_SECRET = os.getenv('SPOTIFY_CLIENT_SECRET')
    SPOTIFY_REDIRECT_URI = os.getenv('SPOTIFY_REDIRECT_URI', 'http://localhost:5000/callback')
    
    # Spotify OAuth scopes required for playback control
    SPOTIFY_SCOPE = 'user-read-playback-state user-modify-playback-state user-read-currently-playing'
    
    # Camera settings
    CAMERA_INDEX = 0  # Default camera index
    
    # Gesture detection settings
    GESTURE_COOLDOWN = 1.0  # seconds between gesture triggers
