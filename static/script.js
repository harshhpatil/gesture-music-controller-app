/**
 * JavaScript for Gesture Music Controller
 * Handles UI interactions, API polling, and visual feedback
 */

// DOM Elements
const startCameraBtn = document.getElementById('start-camera');
const stopCameraBtn = document.getElementById('stop-camera');
const authButton = document.getElementById('auth-button');
const authStatus = document.getElementById('auth-status');
const gestureIcon = document.getElementById('gesture-icon');
const gestureName = document.getElementById('gesture-name');
const gestureFeedback = document.getElementById('gesture-feedback');
const trackName = document.getElementById('track-name');
const artistName = document.getElementById('artist-name');
const albumName = document.getElementById('album-name');
const playbackStatus = document.getElementById('playback-status');

// Polling intervals
let gesturePollingInterval = null;
let trackPollingInterval = null;

// Gesture icon mapping
const gestureIcons = {
    'PLAY': '✋',
    'PAUSE': '✊',
    'SWIPE_LEFT': '👈',
    'SWIPE_RIGHT': '👉',
    'VOLUME_UP': '✌️',
    'VOLUME_DOWN': '🤘'
};

// Gesture descriptions
const gestureDescriptions = {
    'PLAY': 'Resuming playback...',
    'PAUSE': 'Pausing playback...',
    'SWIPE_LEFT': 'Previous track',
    'SWIPE_RIGHT': 'Next track',
    'VOLUME_UP': 'Volume increased',
    'VOLUME_DOWN': 'Volume decreased'
};

/**
 * Check authentication status with Spotify
 */
async function checkAuthStatus() {
    try {
        const response = await fetch('/auth-status');
        const data = await response.json();
        
        if (data.authenticated) {
            authStatus.textContent = '✓ Connected to Spotify';
            authStatus.className = 'status-badge authenticated';
            authButton.style.display = 'none';
        } else {
            authStatus.textContent = '✗ Not connected to Spotify';
            authStatus.className = 'status-badge not-authenticated';
            authButton.style.display = 'inline-block';
        }
    } catch (error) {
        console.error('Error checking auth status:', error);
        authStatus.textContent = 'Error checking connection';
    }
}

/**
 * Start camera and detection loop
 */
async function startCamera() {
    try {
        const response = await fetch('/start-camera', { method: 'POST' });
        const data = await response.json();
        
        if (data.error) {
            alert('Error starting camera: ' + data.error);
            return;
        }
        
        // Update button states
        startCameraBtn.disabled = true;
        stopCameraBtn.disabled = false;
        
        // Start polling for gestures
        startGesturePolling();
        
        console.log('Camera started successfully');
    } catch (error) {
        console.error('Error starting camera:', error);
        alert('Failed to start camera');
    }
}

/**
 * Stop camera and detection loop
 */
async function stopCamera() {
    try {
        const response = await fetch('/stop-camera', { method: 'POST' });
        const data = await response.json();
        
        // Update button states
        startCameraBtn.disabled = false;
        stopCameraBtn.disabled = true;
        
        // Stop polling for gestures
        stopGesturePolling();
        
        // Reset gesture display
        resetGestureDisplay();
        
        console.log('Camera stopped successfully');
    } catch (error) {
        console.error('Error stopping camera:', error);
    }
}

/**
 * Poll for detected gestures every 500ms
 */
function startGesturePolling() {
    gesturePollingInterval = setInterval(async () => {
        try {
            const response = await fetch('/gesture');
            const data = await response.json();
            
            if (data.gesture && data.timestamp) {
                // Check if this is a new gesture (within last 2 seconds)
                const now = Date.now() / 1000;
                if (now - data.timestamp < 2) {
                    updateGestureDisplay(data.gesture);
                }
            }
        } catch (error) {
            console.error('Error polling gesture:', error);
        }
    }, 500);
}

/**
 * Stop polling for gestures
 */
function stopGesturePolling() {
    if (gesturePollingInterval) {
        clearInterval(gesturePollingInterval);
        gesturePollingInterval = null;
    }
}

/**
 * Update gesture display with visual feedback
 */
function updateGestureDisplay(gesture) {
    // Update icon
    const icon = gestureIcons[gesture] || '?';
    gestureIcon.innerHTML = `<span style="color: #1db954;">${icon}</span>`;
    
    // Update name
    gestureName.textContent = gesture.replace('_', ' ');
    
    // Update feedback
    gestureFeedback.textContent = gestureDescriptions[gesture] || '';
    
    // Add animation
    gestureIcon.classList.remove('active');
    setTimeout(() => {
        gestureIcon.classList.add('active');
    }, 10);
    
    // Remove animation after it completes
    setTimeout(() => {
        gestureIcon.classList.remove('active');
    }, 600);
}

/**
 * Reset gesture display to default state
 */
function resetGestureDisplay() {
    gestureIcon.innerHTML = '<span class="icon-placeholder">?</span>';
    gestureName.textContent = 'No gesture detected';
    gestureFeedback.textContent = '';
}

/**
 * Poll for current track information
 */
async function updateCurrentTrack() {
    try {
        const response = await fetch('/current-track');
        const data = await response.json();
        
        if (data.error) {
            trackName.textContent = 'No track playing';
            artistName.textContent = data.error;
            albumName.textContent = '';
            playbackStatus.textContent = '';
            playbackStatus.className = 'playback-status';
            return;
        }
        
        // Update track information
        trackName.textContent = data.track_name;
        artistName.textContent = data.artist;
        albumName.textContent = data.album;
        
        // Update playback status
        if (data.is_playing) {
            playbackStatus.textContent = '▶ Playing';
            playbackStatus.className = 'playback-status playing';
        } else {
            playbackStatus.textContent = '⏸ Paused';
            playbackStatus.className = 'playback-status paused';
        }
    } catch (error) {
        console.error('Error fetching current track:', error);
    }
}

/**
 * Start polling for current track (every 2 seconds)
 */
function startTrackPolling() {
    // Initial update
    updateCurrentTrack();
    
    // Poll every 2 seconds
    trackPollingInterval = setInterval(updateCurrentTrack, 2000);
}

/**
 * Stop polling for current track
 */
function stopTrackPolling() {
    if (trackPollingInterval) {
        clearInterval(trackPollingInterval);
        trackPollingInterval = null;
    }
}

// Event Listeners
startCameraBtn.addEventListener('click', startCamera);
stopCameraBtn.addEventListener('click', stopCamera);
authButton.addEventListener('click', () => {
    window.location.href = '/auth/spotify';
});

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    // Check authentication status
    checkAuthStatus();
    
    // Start polling for track information if authenticated
    startTrackPolling();
    
    // Re-check auth status periodically
    setInterval(checkAuthStatus, 30000); // Every 30 seconds
});

// Cleanup on page unload
window.addEventListener('beforeunload', () => {
    stopGesturePolling();
    stopTrackPolling();
});
