from deepface import DeepFace
import cv2
import time

class EmotionDetector:
    def __init__(self):
        self.last_time = 0
        self.interval = 3  # seconds

    def detect(self, frame):
        current_time = time.time()

        if current_time - self.last_time > self.interval:
            try:
                result = DeepFace.analyze(
                    frame,
                    actions=['emotion'],
                    enforce_detection=False
                )
                emotion = result[0]['dominant_emotion']
                self.last_time = current_time
                return emotion
            except:
                return None

        return None
