import sys

from PySide6.QtWidgets import QApplication
from modules.controller.controller import MainController

class Application(QApplication):
    def __init__(self, argv):
        super().__init__(argv)

        self.setApplicationName("IndexTool")
        self.setApplicationVersion("1.0.0")
        self.setOrganizationName("Region Västerbotten")
        self.setOrganizationDomain("regionvasterbotten.se")


def main():
    app = QApplication(sys.argv)
    controller = MainController()
    controller.main_window.show()
    app.exec()


if __name__ == "__main__":
    sys.exit(main())

