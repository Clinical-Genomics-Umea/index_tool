from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout, QGraphicsOpacityEffect, QPushButton, QHBoxLayout, QFrame
from PySide6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve
from PySide6.QtGui import QColor, QFont


class Toast(QFrame):
    def __init__(self, parent=None, message="", duration=5000, warn=False):
        super().__init__(parent)
        self.setMinimumWidth(300)  # Set minimum width
        self.setMinimumHeight(80)  # Set minimum height

        if warn:
            self.setStyleSheet("""
                    background-color: rgba(180, 10, 10, 180);
                    border-radius: 8px;
                    """)
        else:
            self.setStyleSheet("""
                    background-color: rgba(50, 50, 50, 180);
                    border-radius: 8px;
                    """)

        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)

        main_layout = QVBoxLayout()

        # Create a widget for the top bar (close button)
        top_bar_layout = QHBoxLayout()
        top_bar_layout.setContentsMargins(0, 0, 0, 0)
        top_bar_layout.setSpacing(0)

        # Add a spacer to push the close button to the right
        top_bar_layout.addStretch()

        # Create close button
        close_button = QPushButton("×")
        close_button.setFixedSize(25, 25)
        close_button.setStyleSheet("""
                   QPushButton {
                       background-color: transparent;
                       color: white;
                       font-size: 16px;
                   }
                   QPushButton:hover {
                       background-color: rgba(255, 255, 255, 30);
                   }
               """)
        close_button.clicked.connect(self.close)
        top_bar_layout.addWidget(close_button)

        main_layout.addLayout(top_bar_layout)

        self.label = QLabel(message)
        self.label.setStyleSheet("""
                background-color: transparent;
                color: white;
                padding: 10px;
            """)
        font = QFont()
        font.setPointSize(12)  # Increase font size
        self.label.setFont(font)
        self.label.setWordWrap(True)  # Enable word wrapping
        main_layout.addWidget(self.label)
        self.setLayout(main_layout)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.fade_out)
        self.timer.setSingleShot(True)
        self.timer.start(duration)

        self.opacity_effect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self.opacity_effect)

        self.fade_anim = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.fade_anim.setStartValue(1.0)
        self.fade_anim.setEndValue(0.0)
        self.fade_anim.setDuration(500)
        self.fade_anim.setEasingCurve(QEasingCurve.InOutQuad)
        self.fade_anim.finished.connect(self.close)


    def fade_out(self):
        self.fade_anim.start()

    def show_toast(self):
        self.adjustSize()  # Ensure the widget size is updated
        parent_rect = self.parent().rect()

        # Calculate position to keep the widget fully visible
        x = min(parent_rect.right() - self.width() - 20,
                max(parent_rect.left() + 20, parent_rect.right() - self.width() - 20))
        y = parent_rect.top() + 10

        self.move(x, y)
        super().show()