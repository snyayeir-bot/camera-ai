"""Bounded real-camera and model diagnostic; never saves camera images."""
import json
import time
import cv2
import numpy as np
from app.settings_manager import ROOT, Settings
from app.pose_detector import PoseDetector
from app.hand_gesture import HandGesture

def main():
    settings = Settings().data
    report = {}
    blank = np.zeros((480,640,3),np.uint8)
    for name, cls, filename in [('pose',PoseDetector,'pose_landmarker_lite.task'),
                                ('hands',HandGesture,'hand_landmarker.task')]:
        detector = cls(ROOT/'models'/filename, .55)
        try:
            detector.detect(blank, 1)
            report[name] = 'Model initialized; blank-frame inference completed'
        finally:
            detector.close()
    camera = cv2.VideoCapture(settings['camera'], cv2.CAP_DSHOW)
    try:
        camera.set(cv2.CAP_PROP_FRAME_WIDTH,settings['width'])
        camera.set(cv2.CAP_PROP_FRAME_HEIGHT,settings['height'])
        count, start = 0, time.monotonic()
        shape = None
        for _ in range(30):
            ok, frame = camera.read()
            if not ok:
                break
            count += 1
            shape = list(frame.shape)
        report['camera'] = dict(opened=camera.isOpened(),frames_read=count,shape=shape,
                                elapsed_seconds=round(time.monotonic()-start,3))
    finally:
        camera.release()
    print(json.dumps(report,indent=2))
    (ROOT/'hardware_report.json').write_text(json.dumps(report,indent=2),'utf-8')

if __name__ == '__main__':
    main()
