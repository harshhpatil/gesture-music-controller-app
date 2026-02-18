# Gesture Music Controller 🎵

A web application that allows you to control Spotify playback using hand gestures detected through your webcam.

## Features

- **Real-time hand gesture recognition** using MediaPipe
- **Spotify integration** for music playback control
- **Web-based interface** with live webcam feed
- **Gesture cooldown** to prevent repeated triggers
- **Thread-safe detection** loop

## Supported Gestures

| Gesture | Action |
|---------|--------|
| ✋ Open Palm (5 fingers up) | Play |
| ✊ Fist (0 fingers up) | Pause |
| 👈 Swipe Left | Previous Track |
| 👉 Swipe Right | Next Track |
| ✌️ Two Fingers Up (index + middle) | Volume Up |
| 🤘 Two Fingers Down (ring + pinky) | Volume Down |

## Project Structure

```
gesture-music-controller-app/
│
├── app.py                      # Flask backend server
├── config.py                   # Configuration management
├── requirements.txt            # Python dependencies
├── .env.example               # Environment variables template
│
├── gesture/
│   └── gesture_detector.py    # Hand gesture detection using MediaPipe
│
├── spotify/
│   └── spotify_controller.py  # Spotify API integration
│
├── templates/
│   └── index.html             # Main web interface
│
└── static/
    ├── style.css              # Dark theme styling
    └── script.js              # Frontend JavaScript
```

## Installation

### Prerequisites

- Python 3.10 or higher
- Webcam
- Spotify Premium account

### Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd gesture-music-controller-app
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure Spotify credentials**

   a. Go to [Spotify Developer Dashboard](https://developer.spotify.com/dashboard)
   
   b. Create a new app
   
   c. Copy your Client ID and Client Secret
   
   d. Add `http://localhost:5000/callback` to your app's Redirect URIs
   
   e. Create a `.env` file (copy from `.env.example`):
   ```bash
   cp .env.example .env
   ```
   
   f. Edit `.env` and add your credentials:
   ```
   SPOTIFY_CLIENT_ID=your_client_id_here
   SPOTIFY_CLIENT_SECRET=your_client_secret_here
   SPOTIFY_REDIRECT_URI=http://localhost:5000/callback
   FLASK_SECRET_KEY=your_random_secret_key
   ```

## Usage

1. **Start the Flask server**
   ```bash
   python app.py
   ```

2. **Open your browser**
   ```
   Navigate to http://localhost:5000
   ```

3. **Connect to Spotify**
   - Click the "Connect to Spotify" button
   - Authorize the application
   - You'll be redirected back to the app

4. **Start the camera**
   - Click the "Start Camera" button
   - Allow browser camera permissions
   - The gesture detection will start automatically

5. **Control your music**
   - Make gestures in front of the camera
   - The app will detect them and control Spotify playback
   - Current track information will be displayed

## API Endpoints

- `GET /` - Main web interface
- `POST /start-camera` - Start camera and gesture detection
- `POST /stop-camera` - Stop camera and detection
- `GET /gesture` - Get latest detected gesture (JSON)
- `GET /current-track` - Get current Spotify track info (JSON)
- `GET /video_feed` - Webcam video stream
- `GET /auth/spotify` - Initiate Spotify OAuth
- `GET /callback` - Spotify OAuth callback
- `GET /auth-status` - Check Spotify authentication status

## Configuration

Edit `config.py` to customize:

- `GESTURE_COOLDOWN` - Time in seconds between gesture triggers (default: 1.0)
- `CAMERA_INDEX` - Camera device index (default: 0)
- Other Flask and Spotify settings

## Technical Details

### Gesture Detection

- Uses **MediaPipe Hands** for hand landmark detection
- Analyzes finger positions to identify gestures
- Implements **swipe detection** based on hand movement
- **1-second cooldown** prevents repeated gesture triggers
- Thread-safe implementation for concurrent camera access

### Spotify Integration

- Uses **Spotipy** library for Spotify Web API
- Implements **OAuth 2.0** authentication flow
- Handles API errors gracefully
- Requires **Spotify Premium** for playback control

### Frontend

- **Vanilla JavaScript** - no heavy frameworks
- Polls `/gesture` endpoint every 500ms
- Polls `/current-track` every 2 seconds
- **Visual feedback** with animations on gesture detection
- **Dark theme** UI with modern design

### Backend

- **Flask** web framework with threaded mode
- **Background thread** for continuous gesture detection
- **Thread-safe** gesture state management using locks
- **Proper cleanup** of camera resources on exit
- **Error handling** for camera and Spotify API failures

## Troubleshooting

### Camera not working
- Ensure no other application is using the webcam
- Check `CAMERA_INDEX` in config.py (try 0, 1, or 2)
- Grant camera permissions in your browser

### Spotify not connecting
- Verify credentials in `.env` file
- Ensure Redirect URI matches exactly in Spotify Dashboard
- Check that you have Spotify Premium account
- Make sure Spotify is playing on an active device

### Gestures not detected
- Ensure good lighting conditions
- Keep hand within camera frame
- Try adjusting camera angle
- Wait for cooldown period between gestures (1 second)

## Development

The application uses:
- **Python 3.12**
- **Flask 3.0.0**
- **OpenCV 4.9.0.80**
- **MediaPipe 0.10.14**
- **Spotipy 2.23.0**

## License

This project is open source and available for educational purposes.

## Credits

Built with:
- [Flask](https://flask.palletsprojects.com/)
- [MediaPipe](https://google.github.io/mediapipe/)
- [OpenCV](https://opencv.org/)
- [Spotify Web API](https://developer.spotify.com/documentation/web-api/)
- [Spotipy](https://spotipy.readthedocs.io/)
