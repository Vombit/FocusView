# pylint: disable=no-name-in-module, invalid-name
"""pass"""
from PyQt6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QApplication,
)
from bin.ui.widgets.main_area import MainArea
from bin.ui.widgets.left_panel import LeftSettings


class MainWindow(QMainWindow):
    """pass"""

    def __init__(self):
        super(MainWindow, self).__init__()
        self.init_ui()
        self.connect_signals()

    def init_ui(self):
        """main window layout"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QHBoxLayout()
        central_widget.setLayout(main_layout)

        self.main_area = QWidget()
        main_area_layout = QVBoxLayout()
        self.main_area.setLayout(main_area_layout)

        self.left_panel = LeftSettings()
        self.main_area = MainArea()

        main_layout.addWidget(self.left_panel)
        main_layout.addWidget(self.main_area, stretch=1)

        main_layout.setStretch(0, 0)
        main_layout.setStretch(1, 1)

    def connect_signals(self):
        """Signals"""
        self.left_panel.svg_changed.connect(
            self.main_area.update_svg)  # type: ignore

        self.left_panel.exposure_changed.connect(
            self.main_area.camera_thread.set_exposure)  # type: ignore

    def closeEvent(self, event):  # type: ignore
        """pass"""
        if self.main_area.camera_thread is not None:
            self.main_area.camera_thread.stop()
        QApplication.quit()
        event.accept()
