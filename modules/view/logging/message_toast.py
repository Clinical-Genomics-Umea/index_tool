from PySide6.QtWidgets import QApplication, QFrame, QVBoxLayout, QLabel, QPushButton, QSizePolicy, \
    QGraphicsOpacityEffect
from PySide6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, QPoint


class MessageToast(QFrame):
    _instance = None  # Singleton instance

    def __new__(cls, parent=None):
        if not cls._instance:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, parent=None):
        if hasattr(self, "_initialized"):  # Prevent re-initializing
            return
        super().__init__(parent)
        self._initialized = True
        self.layout = QVBoxLayout(self)
        self.close_button = QPushButton("×", clicked=self.hide)
        self.label = QLabel("")

        self.setup_ui()
        self.setup_animation()
        self.hide()  # Initially hidden

    def setup_ui(self):
        self.setFixedWidth(350)
        self.setMinimumHeight(100)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.MinimumExpanding)

        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(10, 10, 10, 10)

        self.close_button.setFixedSize(25, 25)
        self.close_button.setStyleSheet("background-color: transparent; color: white; font-size: 16px;")
        self.layout.addWidget(self.close_button, alignment=Qt.AlignRight)

        self.label.setWordWrap(True)
        self.label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.MinimumExpanding)
        self.label.setStyleSheet("color: white; padding: 10px;")
        self.layout.addWidget(self.label)

        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setStyleSheet("background-color: rgba(50, 50, 50, 180); border-radius: 8px;")

    def setup_animation(self):
        self.opacity_effect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self.opacity_effect)

        self.fade_anim = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.fade_anim.setDuration(500)
        self.fade_anim.setStartValue(1.0)
        self.fade_anim.setEndValue(0.0)
        self.fade_anim.setEasingCurve(QEasingCurve.InOutQuad)
        self.fade_anim.finished.connect(self.hide)

        self.timer = QTimer(self)
        self.timer.setSingleShot(True)
        self.timer.timeout.connect(self.fade_out)

    def show_message(self, message, duration=5000, warn=False):
        """Show a new message in the existing toast instance"""
        self.label.setText(message)
        bg_color = "rgba(180, 10, 10, 180)" if warn else "rgba(50, 50, 50, 180)"
        self.setStyleSheet(f"background-color: {bg_color}; border-radius: 8px;")

        self.timer.start(duration)  # Reset timer
        self.fade_anim.stop()  # Stop any ongoing fade-out
        self.opacity_effect.setOpacity(1.0)  # Reset opacity

        if not self.isVisible():
            self.adjustSize()
            self.position_popup()
            self.show()

    def fade_out(self):
        self.fade_anim.start()

    def position_popup(self):
        main_window = next((w for w in QApplication.instance().topLevelWidgets() if isinstance(w, QFrame)), None)
        if main_window:
            pos_x = main_window.geometry().right() - self.width() - 20
            pos_y = 20
            self.move(pos_x, pos_y)

# Usage Example:
# toast = MessageToast()
# toast.show_message("Hello, World!", duration=3000, warn=True)


# from PySide6.QtWidgets import (QWidget, QLabel, QVBoxLayout, QGraphicsOpacityEffect, QPushButton,
#                                QHBoxLayout, QFrame, QMainWindow, QApplication, QSizePolicy)
# from PySide6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, QPoint
# from PySide6.QtGui import QColor, QFont
#
#
# class MessageToast(QFrame):
#     def __init__(self, parent=None, message="", duration=5000, warn=False):
#         super().__init__(parent)
#         self.warn = warn
#         self.close_button = QPushButton("×", clicked=self.close)
#         self.setup_ui(message)
#         self.setup_animation(duration)
#
#     def setup_ui(self, message):
#         main_layout = QVBoxLayout(self)
#         main_layout.setContentsMargins(0, 0, 0, 0)
#
#         top_bar_layout = QHBoxLayout()
#         top_bar_layout.addStretch()
#
#
#         self.close_button.setFixedSize(25, 25)
#         self.close_button.setStyleSheet("""
#             QPushButton {
#                 background-color: transparent;
#                 color: white;
#                 font-size: 16px;
#             }
#             QPushButton:hover {
#                 background-color: rgba(255, 255, 255, 30);
#             }
#         """)
#         top_bar_layout.addWidget(self.close_button)
#
#         main_layout.addLayout(top_bar_layout)
#
#         self.label = QLabel(message)
#         self.label.setWordWrap(True)
#         self.label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.MinimumExpanding)
#         self.label.setStyleSheet("""
#             background-color: transparent;
#             color: white;
#             padding: 10px;
#         """)
#         font = QFont()
#         font.setPointSize(12)
#         self.label.setFont(font)
#
#         main_layout.addWidget(self.label)
#
#         self.setFixedWidth(350)
#         self.setMinimumHeight(100)
#         self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.MinimumExpanding)
#
#         bg_color = "rgba(180, 10, 10, 180)" if self.warn else "rgba(50, 50, 50, 180)"
#         self.setStyleSheet(f"""
#             background-color: {bg_color};
#             border-radius: 8px;
#         """)
#
#         self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
#
#     def setup_animation(self, duration):
#         self.opacity_effect = QGraphicsOpacityEffect(self)
#         self.setGraphicsEffect(self.opacity_effect)
#
#         self.fade_anim = QPropertyAnimation(self.opacity_effect, b"opacity")
#         self.fade_anim.setStartValue(1.0)
#         self.fade_anim.setEndValue(0.0)
#         self.fade_anim.setDuration(500)
#         self.fade_anim.setEasingCurve(QEasingCurve.InOutQuad)
#         self.fade_anim.finished.connect(self.close)
#
#         self.timer = QTimer(self)
#         self.timer.timeout.connect(self.fade_out)
#         self.timer.setSingleShot(True)
#         self.timer.start(duration)
#
#     def fade_out(self):
#         self.fade_anim.start()
#
#     def get_main_window(self):
#         return next((w for w in QApplication.instance().topLevelWidgets() if isinstance(w, QMainWindow)), None)
#
#     def show_toast(self):
#         self.adjustSize()
#         main_window = self.get_main_window()
#         if main_window:
#             self.position_popup(main_window)
#         super().show()
#
#     def position_popup(self, main_window):
#         main_rect = main_window.geometry()
#         popup_size = self.size()
#         pos_x = main_rect.width() - popup_size.width() - 10
#         pos_y = 10
#         self.move(pos_x, pos_y)
