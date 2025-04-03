from PySide6.QtWidgets import QMainWindow

from modules.view.central_widget.central_widget import CentralWidget
import qtawesome as qta

from modules.view.logging.message_toast import MessageToast


class MainWindow(QMainWindow):
    def __init__(self, central_widget: CentralWidget, message_toast: MessageToast):
        super().__init__()

        self.setWindowIcon(qta.icon('fa5b.jedi-order', color='blue'))
        self.setWindowTitle("index_tool")
        self.setCentralWidget(central_widget)
        self.setMinimumSize(600, 600)
        self._message_toast = message_toast
