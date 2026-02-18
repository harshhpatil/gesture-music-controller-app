"""
Spotify integration module for gesture-controlled music playback.
Handles OAuth authentication and playback control via Spotify Web API.
"""
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from config import Config

class SpotifyController:
    def __init__(self):
        """Initialize Spotify controller with OAuth authentication."""
        self.sp = None
        self.auth_manager = None
        self._setup_auth()
    
    def _setup_auth(self):
        """Set up Spotify OAuth authentication manager."""
        if not Config.SPOTIFY_CLIENT_ID or not Config.SPOTIFY_CLIENT_SECRET:
            print("Warning: Spotify credentials not configured")
            return
        
        try:
            self.auth_manager = SpotifyOAuth(
                client_id=Config.SPOTIFY_CLIENT_ID,
                client_secret=Config.SPOTIFY_CLIENT_SECRET,
                redirect_uri=Config.SPOTIFY_REDIRECT_URI,
                scope=Config.SPOTIFY_SCOPE,
                cache_path=".spotify_cache"
            )
            self.sp = spotipy.Spotify(auth_manager=self.auth_manager)
        except Exception as e:
            print(f"Error setting up Spotify authentication: {e}")
    
    def is_authenticated(self):
        """Check if user is authenticated with Spotify."""
        return self.sp is not None and self.auth_manager is not None
    
    def get_auth_url(self):
        """Get the Spotify OAuth authorization URL."""
        if self.auth_manager:
            return self.auth_manager.get_authorize_url()
        return None
    
    def handle_callback(self, code):
        """
        Handle OAuth callback with authorization code.
        
        Args:
            code: Authorization code from Spotify
        """
        if self.auth_manager:
            try:
                self.auth_manager.get_access_token(code)
                self.sp = spotipy.Spotify(auth_manager=self.auth_manager)
                return True
            except Exception as e:
                print(f"Error handling callback: {e}")
                return False
        return False
    
    def play(self):
        """Resume playback on the active device."""
        if not self.is_authenticated():
            return {"error": "Not authenticated"}
        
        try:
            self.sp.start_playback()
            return {"status": "success", "action": "play"}
        except spotipy.SpotifyException as e:
            return {"error": str(e), "action": "play"}
        except Exception as e:
            return {"error": f"Unexpected error: {str(e)}", "action": "play"}
    
    def pause(self):
        """Pause playback on the active device."""
        if not self.is_authenticated():
            return {"error": "Not authenticated"}
        
        try:
            self.sp.pause_playback()
            return {"status": "success", "action": "pause"}
        except spotipy.SpotifyException as e:
            return {"error": str(e), "action": "pause"}
        except Exception as e:
            return {"error": f"Unexpected error: {str(e)}", "action": "pause"}
    
    def next_track(self):
        """Skip to the next track."""
        if not self.is_authenticated():
            return {"error": "Not authenticated"}
        
        try:
            self.sp.next_track()
            return {"status": "success", "action": "next"}
        except spotipy.SpotifyException as e:
            return {"error": str(e), "action": "next"}
        except Exception as e:
            return {"error": f"Unexpected error: {str(e)}", "action": "next"}
    
    def previous_track(self):
        """Skip to the previous track."""
        if not self.is_authenticated():
            return {"error": "Not authenticated"}
        
        try:
            self.sp.previous_track()
            return {"status": "success", "action": "previous"}
        except spotipy.SpotifyException as e:
            return {"error": str(e), "action": "previous"}
        except Exception as e:
            return {"error": f"Unexpected error: {str(e)}", "action": "previous"}
    
    def volume_up(self):
        """Increase volume by 10%."""
        if not self.is_authenticated():
            return {"error": "Not authenticated"}
        
        try:
            # Get current volume
            playback = self.sp.current_playback()
            if playback and playback.get('device'):
                current_volume = playback['device'].get('volume_percent', 50)
                new_volume = min(100, current_volume + 10)
                self.sp.volume(new_volume)
                return {"status": "success", "action": "volume_up", "volume": new_volume}
            else:
                return {"error": "No active device", "action": "volume_up"}
        except spotipy.SpotifyException as e:
            return {"error": str(e), "action": "volume_up"}
        except Exception as e:
            return {"error": f"Unexpected error: {str(e)}", "action": "volume_up"}
    
    def volume_down(self):
        """Decrease volume by 10%."""
        if not self.is_authenticated():
            return {"error": "Not authenticated"}
        
        try:
            # Get current volume
            playback = self.sp.current_playback()
            if playback and playback.get('device'):
                current_volume = playback['device'].get('volume_percent', 50)
                new_volume = max(0, current_volume - 10)
                self.sp.volume(new_volume)
                return {"status": "success", "action": "volume_down", "volume": new_volume}
            else:
                return {"error": "No active device", "action": "volume_down"}
        except spotipy.SpotifyException as e:
            return {"error": str(e), "action": "volume_down"}
        except Exception as e:
            return {"error": f"Unexpected error: {str(e)}", "action": "volume_down"}
    
    def set_volume(self, volume_percent):
        """
        Set volume to a specific level.
        
        Args:
            volume_percent: Volume level (0-100)
            
        Returns:
            Dictionary with action result
        """
        if not self.is_authenticated():
            return {"error": "Not authenticated"}
        
        try:
            # Clamp volume to valid range
            volume = max(0, min(100, int(volume_percent)))
            self.sp.volume(volume)
            return {"status": "success", "action": "set_volume", "volume": volume}
        except spotipy.SpotifyException as e:
            return {"error": str(e), "action": "set_volume"}
        except Exception as e:
            return {"error": f"Unexpected error: {str(e)}", "action": "set_volume"}
    
    def get_current_track(self):
        """Get information about the currently playing track."""
        if not self.is_authenticated():
            return {"error": "Not authenticated"}
        
        try:
            current = self.sp.current_playback()
            if current and current.get('item'):
                track = current['item']
                return {
                    "track_name": track['name'],
                    "artist": ", ".join([artist['name'] for artist in track['artists']]),
                    "album": track['album']['name'],
                    "is_playing": current['is_playing'],
                    "progress_ms": current.get('progress_ms', 0),
                    "duration_ms": track['duration_ms']
                }
            else:
                return {"error": "No track currently playing"}
        except spotipy.SpotifyException as e:
            return {"error": str(e)}
        except Exception as e:
            return {"error": f"Unexpected error: {str(e)}"}
    
    def execute_gesture(self, gesture):
        """
        Execute the appropriate Spotify action based on detected gesture.
        
        Args:
            gesture: Detected gesture string (PLAY, PAUSE, SWIPE_LEFT, etc.)
            
        Returns:
            Dictionary with action result
        """
        gesture_map = {
            "PLAY": self.play,
            "PAUSE": self.pause,
            "SWIPE_LEFT": self.previous_track,
            "SWIPE_RIGHT": self.next_track,
            "VOLUME_UP": self.volume_up,
            "VOLUME_DOWN": self.volume_down
        }
        
        action = gesture_map.get(gesture)
        if action:
            return action()
        else:
            return {"error": f"Unknown gesture: {gesture}"}
