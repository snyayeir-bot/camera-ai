import time
from pathlib import Path
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QKeySequence, QShortcut, QPixmap
from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                              QLabel, QPushButton, QStackedWidget, QDialog,
                              QFileDialog, QMessageBox)
from PIL.ImageQt import ImageQt
from app.camera_manager import CameraWorker
from app.photo_booth import prepare_photo, save_photo
from app.settings_manager import ROOT
from ui.i18n import TEXT
from ui.camera_widget import CameraWidget
from ui.clothing_panel import ClothingPanel
from ui.welcome_screen import WelcomeScreen
from ui.settings_dialog import SettingsDialog

class MainWindow(QMainWindow):
    def __init__(self, settings, catalog, start_camera=True):
        super().__init__()
        self.settings, self.catalog = settings, catalog
        self.worker = None
        self.frame = None
        self.last_frame = 0
        self.last_person = time.monotonic()
        self.detected_since = None
        self.present = False
        self.capture_deadline = None
        self.photo_dialog = None
        self.camera_enabled = start_camera
        self.pipeline_error = ''
        self.setWindowTitle('Khmer AI Virtual Try-On')
        self.resize(1280, 860)
        self.build()
        for key, action in [('Right',lambda: self.panel.step(1)), ('Left',lambda: self.panel.step(-1)),
                            ('Space',self.capture), ('F11',self.fullscreen), ('Escape',self.escape)]:
            shortcut = QShortcut(QKeySequence(key), self)
            shortcut.activated.connect(action)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.poll)
        self.timer.start(30)
        if start_camera:
            self.start_worker()
        if settings.data['fullscreen']:
            self.showFullScreen()

    def build(self):
        self.text = TEXT[self.settings.data['language']]
        t = self.text
        root = QWidget()
        layout = QVBoxLayout(root)
        layout.setContentsMargins(28,20,28,20)
        layout.setSpacing(16)
        header = QHBoxLayout()
        title = QLabel(t['title'])
        title.setObjectName('title')
        header.addWidget(title)
        header.addStretch()
        language = QPushButton('ខ្មែរ / EN')
        language.clicked.connect(self.switch_language)
        header.addWidget(language)
        settings = QPushButton(t['settings'])
        settings.clicked.connect(self.open_settings)
        header.addWidget(settings)
        full = QPushButton('⛶  F11')
        full.clicked.connect(self.fullscreen)
        header.addWidget(full)
        layout.addLayout(header)
        self.status = QLabel('●  CAMERA / CONNECTING')
        self.status.setWordWrap(True)
        self.status.setObjectName('muted')
        layout.addWidget(self.status)
        self.stack = QStackedWidget()
        self.welcome = WelcomeScreen(t, self.begin)
        self.camera = CameraWidget()
        self.stack.addWidget(self.welcome)
        self.stack.addWidget(self.camera)
        layout.addWidget(self.stack, 1)
        controls = QHBoxLayout()
        for label, callback, primary in [(t['previous'],lambda:self.panel.step(-1),False),
                                         (t['capture'],self.capture,True),
                                         (t['next'],lambda:self.panel.step(1),False),
                                         (t['menu'],self.toggle_menu,False)]:
            button = QPushButton(label)
            if primary:
                button.setObjectName('primary')
            button.clicked.connect(callback)
            controls.addWidget(button)
        layout.addLayout(controls)
        self.panel = ClothingPanel(self.catalog, t)
        self.panel.selected.connect(self.select_outfit)
        layout.addWidget(self.panel)
        footer = QLabel(t['placeholder']+'   ·   '+t['privacy'])
        footer.setObjectName('muted')
        footer.setWordWrap(True)
        footer.setAlignment(Qt.AlignCenter)
        layout.addWidget(footer)
        self.setCentralWidget(root)

    def begin(self):
        self.stack.setCurrentIndex(1)
        self.last_person = time.monotonic()

    def toggle_menu(self):
        self.panel.setVisible(not self.panel.isVisible())

    def select_outfit(self, outfit):
        if self.worker:
            self.worker.outfit = outfit

    def start_worker(self):
        self.pipeline_error = ''
        self.worker = CameraWorker(self.settings.data, self.catalog)
        self.worker.status.connect(self.pipeline_status)
        self.worker.gesture.connect(self.gesture)
        self.worker.start()

    def pipeline_status(self, message):
        if 'Tracking unavailable' in message or 'pipeline stopped' in message:
            self.pipeline_error = message
        self.status.setText(message)

    def stop_worker(self):
        if self.worker:
            self.worker.requestInterruption()
            # Keep the event loop responsive while the camera/inference call finishes.
            from PySide6.QtWidgets import QApplication
            while not self.worker.wait(30):
                QApplication.processEvents()
            self.worker = None

    def poll(self):
        now = time.monotonic()
        packet = self.worker.take_latest() if self.worker else None
        if packet:
            frame, present, full, fps = packet
            self.frame, self.present = frame, present
            if frame is not None:
                self.last_frame = now
                self.camera.set_frame(frame)
                self.camera.message = self.text['ready' if full else 'guide']
                if self.pipeline_error:
                    self.status.setText(self.pipeline_error)
                elif not self.isFullScreen():
                    self.status.setText(f'●  CAMERA LIVE    {fps:.0f} FPS    /    LOCAL PROCESSING')
                else:
                    self.status.setText(self.text['ready' if present else 'wait'])
            else:
                self.camera.image = None
                self.camera.message = self.text['wait']
                self.camera.update()
            if present:
                self.last_person = now
                if self.detected_since is None:
                    self.detected_since = now
                if now-self.detected_since > .6:
                    self.stack.setCurrentIndex(1)
            else:
                self.detected_since = None
        if now-self.last_frame > 2:
            self.present = False
            self.frame = None
        if now-self.last_person > self.settings.data['idle_seconds']:
            self.stack.setCurrentIndex(0)
            self.camera.image = None
            self.frame = None
            self.capture_deadline = None
            self.camera.countdown = ''
            if self.photo_dialog:
                self.photo_dialog.reject()
        if self.capture_deadline:
            if not self.present or self.frame is None:
                self.capture_deadline = None
                self.camera.countdown = ''
            elif now >= self.capture_deadline:
                self.capture_deadline = None
                self.camera.countdown = ''
                self.show_photo(self.frame.copy())
            else:
                import math
                self.camera.countdown = str(math.ceil(self.capture_deadline-now))
            self.camera.update()

    def gesture(self, event):
        from PySide6.QtWidgets import QApplication
        if QApplication.activeModalWidget() or self.photo_dialog or self.stack.currentIndex() == 0:
            return
        if event == 'next':
            self.panel.step(1)
        elif event == 'previous':
            self.panel.step(-1)
        elif event == 'photo':
            self.capture()
        else:
            self.panel.show()
            if event == 'select':
                self.panel.list.setFocus()
                self.status.setText(self.text['select'])

    def capture(self):
        if self.photo_dialog or self.capture_deadline:
            return
        if self.frame is None or not self.present:
            self.begin()
            self.camera.message = self.text['guide']
            return
        self.begin()
        self.capture_deadline = time.monotonic()+3

    def show_photo(self, frame):
        image = prepare_photo(frame, self.settings.data['frame'])
        dialog = QDialog(self)
        self.photo_dialog = dialog
        dialog.setWindowTitle(self.text['photo'])
        layout = QVBoxLayout(dialog)
        preview = QLabel()
        preview.setPixmap(QPixmap.fromImage(ImageQt(image)).scaled(900,550,Qt.KeepAspectRatio,Qt.SmoothTransformation))
        layout.addWidget(preview)
        notice = QLabel(self.text['privacy'])
        notice.setWordWrap(True)
        layout.addWidget(notice)
        buttons = QHBoxLayout()
        save = QPushButton(self.text['save'])
        export = QPushButton(self.text['export'])
        retake = QPushButton(self.text['retake'])
        close = QPushButton(self.text['close'])
        buttons.addWidget(retake)
        buttons.addWidget(save)
        buttons.addWidget(export)
        buttons.addWidget(close)
        layout.addLayout(buttons)
        def save_image():
            try:
                directory = Path(self.settings.data['photo_dir'])
                if not directory.is_absolute():
                    directory = ROOT/directory
                target = save_photo(image, directory)
                notice.setText(self.text['saved']+'\n'+str(target))
                save.setEnabled(False)
            except OSError as exc:
                QMessageBox.warning(dialog, self.text['photo'], str(exc))
        save.clicked.connect(save_image)
        def export_image():
            chooser = QFileDialog(dialog, self.text['export'])
            chooser.setAcceptMode(QFileDialog.AcceptSave)
            chooser.setNameFilter('PNG (*.png)')
            chooser.setDefaultSuffix('png')
            chooser.selectFile('khmer-photo.png')
            if chooser.exec():
                try:
                    image.save(chooser.selectedFiles()[0],format='PNG')
                    notice.setText(self.text['saved'])
                except OSError as exc:
                    QMessageBox.warning(dialog,self.text['photo'],str(exc))
        export.clicked.connect(export_image)
        retake.clicked.connect(lambda: dialog.done(2))
        close.clicked.connect(dialog.reject)
        result = dialog.exec()
        self.photo_dialog = None
        if result == 2:
            self.capture()

    def switch_language(self):
        data = self.settings.data.copy()
        data['language'] = 'km' if data['language']=='en' else 'en'
        try:
            self.settings.save(data)
            self.build()
            self.select_outfit(self.catalog.items[0])
        except OSError as exc:
            QMessageBox.warning(self, 'Settings', str(exc))

    def open_settings(self):
        dialog = SettingsDialog(self.settings.data, self.text, self)
        if dialog.exec():
            try:
                self.settings.save(dialog.values())
            except (ValueError, OSError) as exc:
                QMessageBox.warning(self, self.text['settings'], str(exc))
                return
            self.timer.stop()
            self.setEnabled(False)
            self.stop_worker()
            self.frame = None
            self.capture_deadline = None
            self.build()
            self.setEnabled(True)
            if self.camera_enabled:
                self.start_worker()
            self.timer.start()
            self.showFullScreen() if self.settings.data['fullscreen'] else self.showNormal()

    def fullscreen(self):
        self.showNormal() if self.isFullScreen() else self.showFullScreen()

    def escape(self):
        if self.isFullScreen():
            self.showNormal()
        else:
            self.stack.setCurrentIndex(0)

    def closeEvent(self, event):
        self.timer.stop()
        self.setEnabled(False)
        self.stop_worker()
        event.accept()
