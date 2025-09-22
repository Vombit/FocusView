# pylint: disable=no-name-in-module, logging-fstring-interpolation, broad-exception-caught
"""pass"""
import os
import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QIcon
from qt_material import apply_stylesheet
from bin.modules.logger_config import setup_logger
from bin.modules.utils import resource_path
from bin.ui.main_window import MainWindow

logger = setup_logger(__name__)
logger.info("Starting...")

DEBUG = os.getenv('DEBUG', 'true').lower() == 'true'
PROGRAM_NAME = "Focus View"

if __name__ == "__main__":
    if DEBUG:
        logger.info("Debug mode enabled")
        os.environ["QT_DEBUG_PLUGINS"] = "1"

    try:
        app = QApplication(sys.argv)
        apply_stylesheet(app, theme='dark_blue.xml',
                         css_file=resource_path("bin/ui/stylesheet/style.qss"))

        app.setWindowIcon(
            QIcon(resource_path("bin/resources/images/logo.svg")))

        window = MainWindow()
        window.setWindowTitle(PROGRAM_NAME)
        window.setMinimumSize(900, 700)
        window.showMaximized()

        logger.info("Application started successfully")

        sys.exit(app.exec())
    except Exception as e:
        logger.error(f"Failed to start: {e}")
        sys.exit(1)
