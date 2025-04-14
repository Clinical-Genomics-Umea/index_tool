from PySide6.QtWidgets import QMainWindow, QStatusBar
from PySide6.QtCore import QTimer

from modules.view.central_widget.central_widget import CentralWidget
import qtawesome as qta

from modules.view.logging.statusbar import StatusBar


class MainWindow(QMainWindow):
    def __init__(self, central_widget: CentralWidget, statusbar: StatusBar):
        super().__init__()

        self.setWindowIcon(qta.icon('fa5b.jedi-order', color='blue'))
        self.setWindowTitle("index_tool")
        self.setCentralWidget(central_widget)
        self.setMinimumSize(600, 600)
        
        # Create status bar
        self.setStatusBar(statusbar)



