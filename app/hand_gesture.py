from collections import deque
import math
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

class GestureFilter:
    def __init__(self):
        self.history = deque()
        self.candidate = None
        self.since = 0
        self.cooldown = 0
        self.latched = set()

    def update(self, hand, now):
        if hand is None:
            self.history.clear()
            self.candidate = None
            self.latched.clear()
            return None
        wrist = hand[0]
        dist = lambda a, b: math.hypot(a.x-b.x, a.y-b.y)
        extended = [dist(hand[t], wrist) > dist(hand[j], wrist)*1.25 for t, j in ((8,6),(12,10),(16,14),(20,18))]
        palm = all(extended)
        thumb = not any(extended) and hand[4].y < hand[3].y < hand[2].y and abs(hand[4].y-hand[2].y) > .06
        candidate = 'photo' if thumb else 'palm' if palm else None
        if candidate != self.candidate:
            self.candidate, self.since = candidate, now
            self.latched.clear()
            self.history.clear()
        if palm:
            self.history.append((now, wrist.x, wrist.y))
            while self.history and now-self.history[0][0] > .55:
                self.history.popleft()
        if now < self.cooldown:
            return None
        event = None
        if palm and len(self.history) >= 3:
            start = self.history[0]
            dx, dy = wrist.x-start[1], wrist.y-start[2]
            if abs(dx) > .18 and abs(dy) < .12:
                event = 'next' if dx > 0 else 'previous'
                self.history.clear()
        held = now-self.since
        if not event and candidate == 'photo' and held > .8 and 'photo' not in self.latched:
            event = 'photo'
        if not event and palm and held > 1.8 and wrist.y < .45 and 'select' not in self.latched:
            event = 'select'
        if not event and palm and held > .65 and 'menu' not in self.latched:
            event = 'menu'
        if event:
            self.latched.add(event)
            self.cooldown = now + 1.0
        return event

class HandGesture:
    def __init__(self, model, confidence):
        self.detector = vision.HandLandmarker.create_from_options(vision.HandLandmarkerOptions(
            base_options=python.BaseOptions(model_asset_path=str(model)),
            running_mode=vision.RunningMode.VIDEO, num_hands=1,
            min_hand_detection_confidence=confidence, min_tracking_confidence=confidence))
        self.filter = GestureFilter()

    def detect(self, rgb, timestamp):
        result = self.detector.detect_for_video(mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb), timestamp)
        return self.filter.update(result.hand_landmarks[0] if result.hand_landmarks else None, timestamp/1000)

    def close(self):
        self.detector.close()
