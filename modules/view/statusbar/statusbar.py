from PySide6.QtWidgets import QLabel, QStatusBar, QWidget
from PySide6.QtCore import Qt, QTimer


class StatusBar(QStatusBar):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.color_map = {
            "DEBUG": "#808080",  # Gray
            "INFO": "#008000",  # Black
            "WARNING": "#CC0000",  # Red
            "ERROR": "#8B0000",  # Dark Red
            "CRITICAL": "#8B0000"  # Dark Red
        }

        # Add spacer widget
        spacer = QWidget()
        spacer.setFixedWidth(20)  # Adjust width as needed
        self.addWidget(spacer)

        self.label = QLabel()
        self.label.setTextFormat(Qt.TextFormat.RichText)  # Enable HTML formatting
        self.addWidget(self.label)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.clear_message)

    def display_message(self, level: str, message: str, timeout: int = 5000):
        """Show a colored message for a given time (in milliseconds)."""
        color = self.color_map.get(level, "#000000")  # Default to black
        self.label.setText(f'<span style="color:{color}; margin-left: 10px;">{message}</span>')

        # Restart the timer with the new timeout
        self.timer.stop()
        self.timer.start(timeout)

    def clear_message(self):
        """Clears the message when the timer expires."""
        self.label.clear()
