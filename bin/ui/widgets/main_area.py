# pylint: disable=no-name-in-module, pointless-string-statement, invalid-name
"""pass"""
import os
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap, QImage, QPainter
from PyQt6.QtWidgets import (
    QWidget,
    QPushButton,
    QVBoxLayout,
    QSizePolicy,
    QLabel,
    QApplication,
    QMessageBox,
)
from bin.ui.utils.ruler import RulerCanvas
from bin.ui.utils.camera import CameraThread
from bin.ui.utils.draggable_svg import DraggableSvgWidget
from bin.modules.logger_config import setup_logger
from bin.modules.utils import resource_path
from bin.modules.i18n import tr

logger = setup_logger(__name__)


class MainArea(QWidget):
    """pass"""
    ZOOM_LEVEL_DEFAULT = 10
    COEFFICIENT_ZOOM_OPTICAL = 15.5

    def __init__(self):
        super().__init__()
        screen = QApplication.primaryScreen()
        self.screen_dpi = screen.physicalDotsPerInch()
        self.zoom_level = self.ZOOM_LEVEL_DEFAULT

        self.camera_thread = None

        self.init_ui()
        self.start_camera()
        self.setSizePolicy(QSizePolicy.Policy.Expanding,
                           QSizePolicy.Policy.Expanding)

    def init_ui(self):
        """pass"""
        self.video_label = QLabel(self)
        self.video_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.video_label.setStyleSheet("background-color: black;")

        # Main overlay widget
        self.overlay_widget = QWidget(self.video_label)
        self.overlay_widget.setStyleSheet("background-color: transparent;")

        # SVG blueprint
        self.svg_widget = DraggableSvgWidget(self.overlay_widget)

        # Increases the zoom
        self.zoom_in_btn = QPushButton("+", self.overlay_widget)
        self.zoom_in_btn.setFixedSize(48, 48)
        self.zoom_in_btn.setProperty('class', 'btn_zoom')
        self.zoom_in_btn.clicked.connect(self.zoom_in)

        # Reduces the zoom
        self.zoom_out_btn = QPushButton("-", self.overlay_widget)
        self.zoom_out_btn.setFixedSize(48, 48)
        self.zoom_out_btn.setProperty('class', 'btn_zoom')
        self.zoom_out_btn.clicked.connect(self.zoom_out)

        # Text with zoom level
        self.zoom_label = QLabel(
            f"{self.zoom_level:.1f}x", self.overlay_widget)
        self.zoom_label.setProperty('class', 'zoom_label')
        self.zoom_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.zoom_label.adjustSize()

        # ruler
        self.ruler_widget = QWidget(self.overlay_widget)
        self.ruler_widget.setProperty('class', 'ruler_widget')

        self.ruler_canvas = RulerCanvas(
            self.ruler_widget, self.screen_dpi, self.zoom_level)

        ruler_layout = QVBoxLayout(self.ruler_widget)
        ruler_layout.setContentsMargins(5, 5, 5, 5)
        ruler_layout.addWidget(self.ruler_canvas)

        self.position_overlay_elements()

        # Layout
        layout = QVBoxLayout()
        layout.addWidget(self.video_label)
        self.setLayout(layout)

    def position_overlay_elements(self):
        """Positions the elements on top of the image"""
        video_label_width = self.video_label.width()
        video_label_height = self.video_label.height()

        self.zoom_label.move(10, 10)
        self.zoom_in_btn.move(10, 50)
        self.zoom_out_btn.move(10, 110)

        ruler_width = self.width()
        ruler_height = 60
        ruler_x = (video_label_width - ruler_width) // 2
        ruler_y = video_label_height - ruler_height

        self.ruler_widget.setGeometry(
            ruler_x, ruler_y, ruler_width, ruler_height)

        self.svg_size()

    def resizeEvent(self, event):  # type: ignore
        """Updates the positions of the elements when window size changes"""
        super().resizeEvent(event)
        if hasattr(self, 'overlay_widget'):
            self.overlay_widget.resize(self.video_label.size())
            self.position_overlay_elements()

    def start_camera(self):
        """Starting the camera stream"""
        try:
            self.camera_thread = CameraThread()
            self.camera_thread.frame_ready.connect(self.update_image)
            self.camera_thread.start()
        except Exception as e:
            QMessageBox.warning(self, "Camera error",
                                f"{tr("camera_connect_error")} {str(e)}")

    def zoom_in(self):
        """Increases the zoom"""
        if self.zoom_level < 20.0:
            self.zoom_level += 1.0
            self.update_zoom_display()

    def zoom_out(self):
        """Reduces the zoom"""
        if self.zoom_level > 1.0:
            self.zoom_level -= 1.0
            self.update_zoom_display()

    def update_zoom_display(self):
        """Updates the zoom level display"""
        self.zoom_label.setText(f"{self.zoom_level:.1f}x")
        self.zoom_label.adjustSize()
        # Updating the scale of the ruler
        if hasattr(self, 'ruler_canvas'):
            self.ruler_canvas.update_zoom(self.zoom_level)

        self.svg_size()

    def update_image(self, img):
        """pass"""
        try:
            h, w, ch = img.shape
            qImg = QImage(img.data, w, h, ch * w, QImage.Format.Format_RGB888)
            pixmap = QPixmap.fromImage(qImg)

            # apply zoom
            coef_zoom_optic = self.COEFFICIENT_ZOOM_OPTICAL
            scale_factor = self.zoom_level / coef_zoom_optic
            new_w = int(w * scale_factor)
            new_h = int(h * scale_factor)
            scaled_pixmap = pixmap.scaled(
                new_w, new_h,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.FastTransformation
            )

            label_width = self.video_label.width()
            label_height = self.video_label.height()
            final_pixmap = QPixmap(label_width, label_height)

            painter = QPainter(final_pixmap)
            # center image
            x = (label_width - scaled_pixmap.width()) // 2
            y = (label_height - scaled_pixmap.height()) // 2
            painter.drawPixmap(x, y, scaled_pixmap)
            painter.end()

            self.video_label.setPixmap(final_pixmap)

            # self.video_label.setPixmap(scaled_pixmap)

        except Exception as e:
            logger.error(f"Error in update_image: {e}")

    def update_svg(self, svg_name: str):
        """change SVG blueprint"""
        print(self.svg_widget.size())

        self.svg_widget.load(resource_path(
            f'bin/resources/blueprints/{svg_name}'))

        name = os.path.splitext(os.path.basename(svg_name))[0]

        parts = name.split("-")

        w = h = 0.0
        for part in parts:
            if part.startswith("w"):
                w = float(part[1:].replace(",", "."))
            elif part.startswith("h"):
                h = float(part[1:].replace(",", "."))

        self.svg_size(w, h)

    def svg_size(self, width: float = 5.6, height: float = 9.0):
        """in mm"""
        cm_in_pixels = self.screen_dpi / 2.54
        zoomed_cm_pixels = cm_in_pixels * self.zoom_level
        svg_w = int(zoomed_cm_pixels * width / 10 * 1.05)
        svg_h = int(zoomed_cm_pixels * height / 10 * 1.05)
        self.svg_widget.setFixedSize(svg_w, svg_h)

        # center SVG
        svg_x = (self.video_label.width() - self.svg_widget.width()) // 2
        svg_y = (self.video_label.height() - self.svg_widget.height()) // 2
        self.svg_widget.move(svg_x, svg_y)
