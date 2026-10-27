from PySide6.QtCore import Qt
from PySide6.QtGui import QImage, QPainter, QColor
from PySide6.QtWidgets import QWidget
import cv2

class CameraWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.image = None
        self.message = ''
        self.countdown = ''
        self.setMinimumSize(480, 320)

    def set_frame(self, frame):
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        self.image = QImage(rgb.data, rgb.shape[1], rgb.shape[0], rgb.strides[0], QImage.Format_RGB888).copy()
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.fillRect(self.rect(), QColor('#070e1b'))
        if self.image:
            size = self.image.size().scaled(self.size(), Qt.KeepAspectRatio)
            x, y = (self.width()-size.width())//2, (self.height()-size.height())//2
            painter.drawImage(x, y, self.image.scaled(size, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        painter.setPen(QColor('#dcecff'))
        painter.drawText(self.rect().adjusted(20,20,-20,-20), Qt.AlignBottom | Qt.AlignHCenter | Qt.TextWordWrap, self.message)
        if self.countdown:
            painter.fillRect(self.rect(), QColor(5,10,25,100))
            font = painter.font()
            font.setPointSize(96)
            painter.setFont(font)
            painter.drawText(self.rect(), Qt.AlignCenter, self.countdown)
