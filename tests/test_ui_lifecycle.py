import os
os.environ.setdefault('QT_QPA_PLATFORM','offscreen')
import time
import numpy as np
from PySide6.QtWidgets import QApplication
from app.settings_manager import ROOT, Settings
from app.clothing_manager import ClothingManager
from ui.main_window import MainWindow

def test_capture_cancels_and_idle_resets(tmp_path):
    app = QApplication.instance() or QApplication([])
    window = MainWindow(Settings(tmp_path/'config.json'),ClothingManager(ROOT/'assets/clothes'),False)
    window.timer.stop()
    window.frame = np.zeros((480,640,3),np.uint8)
    window.present = True
    window.last_frame = time.monotonic()
    window.capture()
    assert window.capture_deadline is not None
    window.present = False
    window.poll()
    assert window.capture_deadline is None
    assert window.photo_dialog is None
    window.last_person = time.monotonic()-30
    window.poll()
    assert window.stack.currentIndex() == 0
    assert window.frame is None
    window.close()
    app.processEvents()
