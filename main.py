import cv2
from gesture.gesture_detector import GestureDetector
from emotion.emotion_detector import EmotionDetector
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))


gesture_detector = GestureDetector()
emotion_detector = EmotionDetector()

cap = cv2.VideoCapture(1)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame, gesture = gesture_detector.detect(frame)
    emotion = emotion_detector.detect(frame)

    if gesture:
        print("Gesture:", gesture)

    if emotion:
        print("Emotion:", emotion)

    cv2.imshow("Gesture Music Control", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
