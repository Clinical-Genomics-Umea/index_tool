from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout, QGraphicsOpacityEffect, QPushButton, QHBoxLayout, QFrame, \
    QMainWindow, QApplication, QSizePolicy
from PySide6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, QPoint
from PySide6.QtGui import QColor, QFont


class Toast(QFrame):
    def __init__(self, parent=None, message="", duration=5000, warn=False):
        super().__init__(parent)

        self.warn = warn

        main_layout = QVBoxLayout()

        # Create a widget for the top bar (close button)
        top_bar_layout = QHBoxLayout()
        top_bar_layout.setContentsMargins(0, 0, 0, 0)
        top_bar_layout.setSpacing(0)

        # Add a spacer to push the close button to the right
        top_bar_layout.addStretch()

        # Create close button
        self.close_button = QPushButton("×")
        self.close_button.clicked.connect(self.close)
        top_bar_layout.addWidget(self.close_button)

        main_layout.addLayout(top_bar_layout)

        self.label = QLabel(message)
        self.font = QFont()

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

        self.setup()

    def setup(self):
        self.setFixedWidth(350)
        self.setMinimumHeight(100)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.MinimumExpanding)

        if self.warn:
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

        self.close_button.setFixedSize(25, 25)
        self.close_button.setStyleSheet("""
                   QPushButton {
                       background-color: transparent;
                       color: white;
                       font-size: 16px;
                   }
                   QPushButton:hover {
                       background-color: rgba(255, 255, 255, 30);
                   }
               """)
        self.label.setWordWrap(True)
        self.label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.MinimumExpanding)
        self.label.setStyleSheet("""
                background-color: transparent;
                color: white;
                padding: 10px;
            """)

        self.font.setPointSize(12)  # Increase font size
        self.label.setFont(self.font)


    def fade_out(self):
        self.fade_anim.start()

    def get_main_window(self):
        app = QApplication.instance()
        for widget in app.topLevelWidgets():
            if isinstance(widget, QMainWindow):
                return widget
        return None

    def show_toast(self):
        self.adjustSize()  # Ensure the widget size is updated

        main_window = self.get_main_window()
        print(main_window)
        self.position_popup()

        super().show()

    def position_popup(self):
        # Get the main window instance
        main_window = self.get_main_window()
        if main_window:
            main_rect = main_window.geometry()
            popup_size = self.size()

            # Calculate the position to center the popup within the main window
            pos_x = main_rect.width() - popup_size.width() - 10
            pos_y = 10
            self.move(pos_x, pos_y)
