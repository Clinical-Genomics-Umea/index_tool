import sys
import logging
from typing import NoReturn

from PySide6.QtWidgets import QApplication
from modules.controller.controller import MainController

class Application(QApplication):
    """Main application class extending QApplication with custom initialization."""
    
    def __init__(self, argv: list[str]) -> None:
        """Initialize the application with custom settings.
        
        Args:
            argv: Command line arguments
        """
        super().__init__(argv)

        self.setApplicationName("IndexTool")
        self.setApplicationVersion("1.0.0")
        self.setOrganizationName("Region Västerbotten")
        self.setOrganizationDomain("regionvasterbotten.se")


def setup_logging() -> None:
    """Configure application-wide logging settings."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('index_tool.log')
        ]
    )


def main() -> NoReturn:
    """Application entry point."""
    setup_logging()
    logger = logging.getLogger(__name__)
    logger.info("Starting IndexTool")
    
    try:
        app = Application(sys.argv)
        controller = MainController()
        controller.main_window.show()
        sys.exit(app.exec())
    except Exception as e:
        logger.error(f"Application crashed: {str(e)}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
