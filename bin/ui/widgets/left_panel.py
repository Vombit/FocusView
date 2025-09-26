# pylint: disable=no-name-in-module
"""**QPushButton is used as the label because it is simply stylized beautifully in a standard way"""
from PyQt6.QtWidgets import (
    QWidget,
    QPushButton,
    QSpinBox,
    QVBoxLayout,
    QComboBox,
)
from PyQt6.QtCore import pyqtSignal, QDir
from bin.modules.i18n import tr
from bin.modules.utils import resource_path


class LeftSettings(QWidget):
    """left panel"""
    # Signals
    svg_changed = pyqtSignal(str)
    exposure_changed = pyqtSignal(int)
    camera_changed = pyqtSignal(str)
    size_changed = pyqtSignal(tuple)

    PANEL_WIDTH = 200
    EXPOSURE_RANGE = (10, 60)
    DEFAULT_EXPOSURE = 30
    SIZE_OPTIONS = [
        (4000, 3000),
        (4000, 2000),
        (2000, 1500),
        (2000, 1000),
        (1000, 750),
        (800, 600),
        (640, 480),
    ]

    def __init__(self):
        super().__init__()
        self.init_ui()

        self.setFixedWidth(self.PANEL_WIDTH)

    def init_ui(self):
        """pass"""
        self.main_layout = QVBoxLayout(self)

        # self.camera_picker()
        self._set_size()
        self._set_exposure()
        self._select_blueprint()

        self.main_layout.addStretch()

    def _camera_picker(self):
        """pass"""
        label = QPushButton(tr("camera_picker_label"))
        box = QComboBox()

        self.add_to_layout(label, box)

    def _set_size(self):
        """pass"""
        label = QPushButton(tr("size_label"))
        box = QComboBox()

        for size_option in self.SIZE_OPTIONS:
            box.addItem(f"{size_option[0]}x{size_option[1]}", size_option)

        box.currentIndexChanged.connect(
            lambda index: self.size_changed.emit(box.itemData(index))
        )

        self.add_to_layout(label, box)

    def _set_exposure(self):
        """pass"""
        label = QPushButton(tr("exposure_label"))
        box = QSpinBox()
        box.setRange(*self.EXPOSURE_RANGE)
        box.setValue(self.DEFAULT_EXPOSURE)
        box.valueChanged.connect(self.exposure_changed.emit)

        self.add_to_layout(label, box)

    def _select_blueprint(self):
        """pass"""
        label = QPushButton(tr("blueprint_label"))
        box = QComboBox()

        blueprints_dir = resource_path("bin/resources/blueprints")
        box.addItem("none")

        qdir = QDir(blueprints_dir)
        if qdir.exists():
            files = qdir.entryList(QDir.Filter.Files)
            box.addItems(files)

        box.currentTextChanged.connect(self.svg_changed.emit)

        self.add_to_layout(label, box)

    def add_to_layout(self, label, layout):
        """Adding new items to the panel (with the name)"""
        self.main_layout.addWidget(label)
        self.main_layout.addWidget(layout)
