"""
Flask web application for gesture-controlled music player.
Provides REST API endpoints and webcam streaming for real-time gesture detection.
"""
from flask import Flask, render_template, Response, jsonify, request, redirect
import cv2
import threading
import time
from gesture.gesture_detector import GestureDetector
from spotify.spotify_controller import SpotifyController
from config import Config

# Initialize Flask app
app = Flask(__name__)
app.config.from_object(Config)

# Global variables for camera and detection
camera = None
gesture_detector = None
spotify_controller = None
detection_thread = None
detection_running = False
lock = threading.Lock()

# Store latest detected gesture
latest_gesture = {
    "gesture": None,
    "timestamp": None
}

def init_camera():
    """Initialize camera with error handling."""
    global camera
    try:
        camera = cv2.VideoCapture(Config.CAMERA_INDEX)
        if not camera.isOpened():
            print(f"Warning: Could not open camera {Config.CAMERA_INDEX}")
            return False
        return True
    except Exception as e:
        print(f"Error initializing camera: {e}")
        return False

def cleanup_camera():
    """Safely release camera resources."""
    global camera
    if camera is not None:
        camera.release()
        camera = None

def generate_frames():
    """
    Generator function for streaming video frames.
    Yields JPEG-encoded frames for display in browser.
    """
    global camera
    
    while True:
        if camera is None or not camera.isOpened():
            break
            
        success, frame = camera.read()
        if not success:
            break
        
        # Encode frame as JPEG
        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()
        
        # Yield frame in multipart format for streaming
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

def detection_loop():
    """
    Background thread for continuous gesture detection.
    Thread-safe implementation with proper cleanup.
    """
    global camera, gesture_detector, spotify_controller, detection_running, latest_gesture
    
    print("Detection loop started")
    
    while detection_running:
        if camera is None or not camera.isOpened():
            time.sleep(0.1)
            continue
        
        # Read frame from camera
        success, frame = camera.read()
        if not success:
            continue
        
        # Detect gesture (thread-safe with detector's internal state)
        processed_frame, gesture = gesture_detector.detect(frame)
        
        # If gesture detected, update latest gesture and execute Spotify action
        if gesture:
            with lock:
                latest_gesture["gesture"] = gesture
                latest_gesture["timestamp"] = time.time()
            
            print(f"Detected gesture: {gesture}")
            
            # Execute Spotify action if controller is authenticated
            if spotify_controller and spotify_controller.is_authenticated():
                result = spotify_controller.execute_gesture(gesture)
                print(f"Spotify action result: {result}")
        
        # Small delay to prevent CPU overuse
        time.sleep(0.01)
    
    print("Detection loop stopped")

@app.route('/')
def index():
    """Render main application page."""
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    """
    Video streaming route.
    Returns multipart response with JPEG frames.
    """
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/start-camera', methods=['POST'])
def start_camera():
    """
    Start camera and detection loop in background thread.
    Returns success/error status.
    """
    global camera, gesture_detector, detection_thread, detection_running
    
    try:
        # Initialize camera if not already initialized
        if camera is None:
            if not init_camera():
                return jsonify({"error": "Failed to initialize camera"}), 500
        
        # Initialize gesture detector if not already initialized
        if gesture_detector is None:
            gesture_detector = GestureDetector(cooldown=Config.GESTURE_COOLDOWN)
        
        # Start detection thread if not already running
        if not detection_running:
            detection_running = True
            detection_thread = threading.Thread(target=detection_loop, daemon=True)
            detection_thread.start()
        
        return jsonify({"status": "success", "message": "Camera started"})
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/stop-camera', methods=['POST'])
def stop_camera():
    """
    Stop detection loop and release camera.
    Returns success status.
    """
    global detection_running, detection_thread
    
    try:
        # Stop detection loop
        detection_running = False
        
        # Wait for thread to finish
        if detection_thread is not None:
            detection_thread.join(timeout=2.0)
        
        # Clean up camera
        cleanup_camera()
        
        return jsonify({"status": "success", "message": "Camera stopped"})
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/gesture', methods=['GET'])
def get_gesture():
    """
    Get latest detected gesture.
    Returns JSON with gesture name and timestamp.
    """
    with lock:
        return jsonify(latest_gesture)

@app.route('/current-track', methods=['GET'])
def get_current_track():
    """
    Get currently playing track information from Spotify.
    Returns JSON with track details.
    """
    global spotify_controller
    
    if spotify_controller is None:
        return jsonify({"error": "Spotify not initialized"}), 500
    
    track_info = spotify_controller.get_current_track()
    return jsonify(track_info)

@app.route('/auth/spotify')
def spotify_auth():
    """Redirect to Spotify authorization page."""
    global spotify_controller
    
    if spotify_controller is None:
        spotify_controller = SpotifyController()
    
    auth_url = spotify_controller.get_auth_url()
    if auth_url:
        return redirect(auth_url)
    else:
        return "Spotify credentials not configured", 500

@app.route('/callback')
def spotify_callback():
    """
    Handle Spotify OAuth callback.
    Receives authorization code and completes authentication.
    """
    global spotify_controller
    
    code = request.args.get('code')
    if code:
        if spotify_controller and spotify_controller.handle_callback(code):
            return redirect('/')
        else:
            return "Authentication failed", 500
    else:
        return "No authorization code received", 400

@app.route('/auth-status', methods=['GET'])
def auth_status():
    """Check if user is authenticated with Spotify."""
    global spotify_controller
    
    if spotify_controller is None:
        spotify_controller = SpotifyController()
    
    is_auth = spotify_controller.is_authenticated()
    return jsonify({"authenticated": is_auth})

def cleanup():
    """Cleanup function called on application exit."""
    global detection_running, gesture_detector
    
    print("Cleaning up...")
    detection_running = False
    cleanup_camera()
    
    if gesture_detector:
        gesture_detector.cleanup()

# Register cleanup function
import atexit
atexit.register(cleanup)

if __name__ == '__main__':
    # Initialize Spotify controller on startup
    spotify_controller = SpotifyController()
    
    print("Starting Gesture Music Controller...")
    print("Navigate to http://localhost:5000 in your browser")
    
    # Run Flask app
    app.run(host='0.0.0.0', port=5000, debug=Config.DEBUG, threaded=True)
