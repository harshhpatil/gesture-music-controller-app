"""
Gesture detection module using MediaPipe for hand tracking.
Detects various hand gestures for music control.
"""
import cv2
import mediapipe as mp
import time

class GestureDetector:
    def __init__(self, cooldown=1.0):
        """
        Initialize the gesture detector.
        
        Args:
            cooldown (float): Time in seconds between gesture triggers to prevent repeated detections
        """
        self.last_gesture = None
        self.last_time = 0
        self.cooldown = cooldown
        
        # Store hand position for swipe detection
        self.last_hand_x = None
        self.swipe_threshold = 0.15  # Minimum x-axis movement for swipe detection
        
        # Initialize MediaPipe Hands
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=1,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.7
        )
        self.mp_draw = mp.solutions.drawing_utils
        
    def fingers_up(self, landmarks):
        """
        Determine which fingers are up.
        
        Args:
            landmarks: Hand landmarks from MediaPipe
            
        Returns:
            List of 1s and 0s indicating which fingers are up (thumb, index, middle, ring, pinky)
        """
        fingers = []

        # Thumb (x comparison - different for left/right hand)
        if landmarks[4].x < landmarks[3].x:
            fingers.append(1)
        else:
            fingers.append(0)

        # Other 4 fingers (y comparison - tip vs middle joint)
        tips = [8, 12, 16, 20]
        for tip in tips:
            if landmarks[tip].y < landmarks[tip - 2].y:
                fingers.append(1)
            else:
                fingers.append(0)

        return fingers

    def detect_swipe(self, hand_x):
        """
        Detect horizontal swipe gestures.
        
        Args:
            hand_x: Current x-coordinate of hand center
            
        Returns:
            "SWIPE_LEFT" or "SWIPE_RIGHT" if swipe detected, None otherwise
        """
        if self.last_hand_x is not None:
            delta_x = hand_x - self.last_hand_x
            
            # Check if movement exceeds threshold
            if abs(delta_x) > self.swipe_threshold:
                self.last_hand_x = hand_x
                if delta_x > 0:
                    return "SWIPE_RIGHT"
                else:
                    return "SWIPE_LEFT"
        
        self.last_hand_x = hand_x
        return None

    def detect(self, frame):
        """
        Detect hand gestures in the given frame.
        
        Supported gestures:
        - PLAY: Open palm (all 5 fingers up)
        - PAUSE: Fist (all fingers closed)
        - SWIPE_LEFT: Hand moves left across screen
        - SWIPE_RIGHT: Hand moves right across screen
        - VOLUME_UP: Two fingers up (index and middle)
        - VOLUME_DOWN: Two fingers down (different from up)
        
        Args:
            frame: Video frame from camera
            
        Returns:
            Tuple of (processed_frame, detected_gesture)
        """
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.hands.process(rgb)

        gesture = None

        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                # Draw hand landmarks on frame
                self.mp_draw.draw_landmarks(
                    frame, hand_landmarks, self.mp_hands.HAND_CONNECTIONS
                )

                landmarks = hand_landmarks.landmark
                fingers = self.fingers_up(landmarks)
                
                # Calculate hand center for swipe detection (using wrist landmark)
                hand_x = landmarks[0].x  # Wrist landmark for tracking
                
                # Detect specific gestures based on finger positions
                if sum(fingers) == 5:
                    # All fingers up = PLAY
                    gesture = "PLAY"
                elif sum(fingers) == 0:
                    # All fingers closed = PAUSE
                    gesture = "PAUSE"
                elif fingers == [0, 1, 1, 0, 0]:
                    # Index and middle fingers up = VOLUME_UP
                    gesture = "VOLUME_UP"
                elif fingers == [0, 0, 0, 1, 1]:
                    # Ring and pinky fingers up = VOLUME_DOWN
                    gesture = "VOLUME_DOWN"
                else:
                    # Check for swipe gestures
                    swipe = self.detect_swipe(hand_x)
                    if swipe:
                        gesture = swipe
        else:
            # Reset hand position when no hand detected
            self.last_hand_x = None

        # Apply cooldown to prevent rapid repeated triggers
        current_time = time.time()

        # Only trigger if it's a new gesture different from the last one, or cooldown has passed
        if gesture and gesture != self.last_gesture:
            if (current_time - self.last_time) > self.cooldown:
                self.last_gesture = gesture
                self.last_time = current_time
                return frame, gesture
        
        return frame, None
    
    def cleanup(self):
        """Release resources used by the detector."""
        if self.hands:
            self.hands.close()


