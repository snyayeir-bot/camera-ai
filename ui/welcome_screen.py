from PySide6.QtCore import QPropertyAnimation, QEasingCurve
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QGraphicsOpacityEffect
from PySide6.QtCore import Qt

class WelcomeScreen(QWidget):
    def __init__(self, text, start):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.addStretch()
        self.orbit = QLabel('◇')
        self.orbit.setStyleSheet('font-size: 120px; color: #65d9ef;')
        self.orbit.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.orbit)
        effect = QGraphicsOpacityEffect(self.orbit)
        self.orbit.setGraphicsEffect(effect)
        self.animation = QPropertyAnimation(effect, b'opacity', self)
        self.animation.setDuration(2400)
        self.animation.setStartValue(.35)
        self.animation.setKeyValueAt(.5, 1)
        self.animation.setEndValue(.35)
        self.animation.setLoopCount(-1)
        self.animation.setEasingCurve(QEasingCurve.InOutSine)
        self.animation.start()
        for key in ('welcome', 'subtitle', 'wait'):
            label = QLabel(text[key])
            label.setAlignment(Qt.AlignCenter)
            label.setWordWrap(True)
            label.setStyleSheet('font-size: 28px;' if key == 'welcome' else 'font-size: 16px; color: #a9b8ce;')
            layout.addWidget(label)
        button = QPushButton(text['start'])
        button.setObjectName('primary')
        button.clicked.connect(start)
        layout.addWidget(button, alignment=Qt.AlignCenter)
        layout.addStretch()
