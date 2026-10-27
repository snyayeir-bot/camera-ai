import logging
import threading
import time
import cv2
import numpy as np
from PySide6.QtCore import QThread, Signal
from app.settings_manager import ROOT
from app.pose_detector import PoseDetector
from app.hand_gesture import HandGesture
from app.clothing_engine import ClothingEngine

class CameraWorker(QThread):
    status = Signal(str)
    gesture = Signal(str)

    def __init__(self, settings, catalog):
        super().__init__()
        self.settings = settings.copy()
        self.catalog = catalog
        self.outfit = catalog.items[0]
        self.lock = threading.Lock()
        self.latest = None

    def take_latest(self):
        with self.lock:
            packet, self.latest = self.latest, None
            return packet

    def run(self):
        camera = pose = hands = None
        try:
            try:
                pose = PoseDetector(ROOT/'models/pose_landmarker_lite.task', self.settings['sensitivity'])
                hands = HandGesture(ROOT/'models/hand_landmarker.task', self.settings['sensitivity'])
            except Exception as exc:
                logging.exception('Model initialization failed')
                self.status.emit(f'Tracking unavailable: run setup.bat. {exc}')
            engine = ClothingEngine(self.catalog)
            count, previous, fps = 0, time.monotonic(), 0
            while not self.isInterruptionRequested():
                if camera is None:
                    camera = cv2.VideoCapture(self.settings['camera'], cv2.CAP_DSHOW)
                    camera.set(cv2.CAP_PROP_FRAME_WIDTH, self.settings['width'])
                    camera.set(cv2.CAP_PROP_FRAME_HEIGHT, self.settings['height'])
                    camera.set(cv2.CAP_PROP_FPS, 30)
                ok, frame = camera.read()
                if not ok:
                    camera.release()
                    camera = None
                    with self.lock:
                        self.latest = (None, False, False, 0)
                    self.status.emit('Camera unavailable — reconnect it or choose another camera in Settings.')
                    for _ in range(20):
                        if self.isInterruptionRequested():
                            break
                        self.msleep(100)
                    continue
                if self.settings['mirror']:
                    frame = cv2.flip(frame, 1)
                now = time.monotonic()
                timestamp = int(now*1000)
                ratio = min(1, self.settings['inference_width']/frame.shape[1])
                small = cv2.resize(frame, None, fx=ratio, fy=ratio)
                rgb = np.ascontiguousarray(cv2.cvtColor(small, cv2.COLOR_BGR2RGB))
                points = pose.detect(rgb, timestamp) if pose else None
                if hands and count % self.settings['hand_interval'] == 0:
                    event = hands.detect(rgb, timestamp)
                    if event:
                        self.gesture.emit(event)
                full = points is not None and min(points[27,3], points[28,3]) > .5 and np.all((points[[27,28],1] > 0) & (points[[27,28],1] < .98))
                if points is not None:
                    frame = engine.render(frame, points, self.outfit, self.settings['clothing_scale'])
                fps = .9*fps + .1/max(.001, now-previous)
                previous = now
                count += 1
                with self.lock:
                    self.latest = (frame, points is not None, full, fps)
                remaining = 1/30-(time.monotonic()-now)
                if remaining > 0:
                    self.msleep(int(remaining*1000))
        except Exception as exc:
            logging.exception('Camera pipeline failed')
            self.status.emit(f'Camera pipeline stopped: {exc}. Reapply Settings to restart.')
        finally:
            if camera:
                camera.release()
            for detector in (pose, hands):
                if detector:
                    detector.close()
