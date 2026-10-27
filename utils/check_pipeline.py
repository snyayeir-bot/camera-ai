"""Exercise the real threaded camera pipeline without saving camera images."""
import json
import statistics
from PySide6.QtCore import QCoreApplication, QTimer
from app.settings_manager import ROOT, Settings
from app.clothing_manager import ClothingManager
from app.camera_manager import CameraWorker

def main():
    app = QCoreApplication([])
    worker = CameraWorker(Settings().data,ClothingManager(ROOT/'assets/clothes'))
    counts = {'frames':0,'person_frames':0,'full_body_frames':0,'errors':[]}
    rates = []
    worker.status.connect(counts['errors'].append)
    def poll():
        packet = worker.take_latest()
        if packet and packet[0] is not None:
            frame,present,full,fps = packet
            counts['frames'] += 1
            counts['person_frames'] += int(present)
            counts['full_body_frames'] += int(full)
            counts['frame_shape'] = list(frame.shape)
            rates.append(float(fps))
    timer = QTimer()
    timer.timeout.connect(poll)
    timer.start(30)
    def finish():
        timer.stop()
        worker.requestInterruption()
        worker.finished.connect(app.quit)
        if not worker.isRunning():
            app.quit()
    QTimer.singleShot(12000,finish)
    worker.start()
    app.exec()
    worker.wait()
    counts['median_reported_fps'] = round(statistics.median(rates[5:] or rates),2) if rates else 0
    counts['camera_images_saved'] = False
    (ROOT/'pipeline_report.json').write_text(json.dumps(counts,indent=2),'utf-8')
    print(json.dumps(counts,indent=2))

if __name__ == '__main__':
    main()
