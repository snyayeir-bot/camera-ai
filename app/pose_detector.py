import numpy as np
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

class PoseDetector:
    def __init__(self, model, confidence):
        self.detector = vision.PoseLandmarker.create_from_options(vision.PoseLandmarkerOptions(
            base_options=python.BaseOptions(model_asset_path=str(model)),
            running_mode=vision.RunningMode.VIDEO, num_poses=1,
            min_pose_detection_confidence=confidence,
            min_tracking_confidence=confidence))
        self.previous = None

    def detect(self, rgb, timestamp):
        result = self.detector.detect_for_video(mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb), timestamp)
        if not result.pose_landmarks:
            self.previous = None
            return None
        p = np.array([[v.x, v.y, v.z, v.visibility] for v in result.pose_landmarks[0]], np.float32)
        if min(p[11, 3], p[12, 3], p[23, 3], p[24, 3]) < .45:
            self.previous = None
            return None
        if self.previous is not None:
            movement = np.linalg.norm(p[:, :2]-self.previous[:, :2], axis=1).mean()
            alpha = np.clip(.3 + movement*6, .3, .85)
            p[:, :3] = alpha*p[:, :3] + (1-alpha)*self.previous[:, :3]
        self.previous = p.copy()
        return p

    def close(self):
        self.detector.close()
