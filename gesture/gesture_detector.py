import cv2
import gesture
import mediapipe as mp

class GestureDetector:
    def __init__(self):
        import time
        self.last_gesture = None
        self.last_time = 0
        self.cooldown = 1  # seconds

        
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=1,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.7
        )
        self.mp_draw = mp.solutions.drawing_utils
        
    def fingers_up(self, landmarks):
        fingers = []

        # Thumb (x comparison)
        if landmarks[4].x < landmarks[3].x:
            fingers.append(1)
        else:
            fingers.append(0)

        # Other 4 fingers (y comparison)
        tips = [8, 12, 16, 20]
        for tip in tips:
            if landmarks[tip].y < landmarks[tip - 2].y:
                fingers.append(1)
            else:
                fingers.append(0)

        return fingers


    def detect(self, frame):
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.hands.process(rgb)

        gesture = None

        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                self.mp_draw.draw_landmarks(
                    frame, hand_landmarks, self.mp_hands.HAND_CONNECTIONS
                )

                landmarks = hand_landmarks.landmark
                fingers = self.fingers_up(landmarks)

                if sum(fingers) == 5:
                    gesture = "OPEN_HAND"
                elif sum(fingers) == 0: 
                    gesture = "FIST"


        current_time = time.time()

        if gesture != self.last_gesture and (current_time - self.last_time) > self.cooldown:
            self.last_gesture = gesture
            self.last_time = current_time
            return frame, gesture

        return frame, None


