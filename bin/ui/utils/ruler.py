# pylint: disable=no-name-in-module, invalid-name
"""pass"""
from PyQt6.QtWidgets import QWidget
from PyQt6.QtGui import QPainter, QPen, QBrush, QColor


class RulerCanvas(QWidget):
    """Custom ruler canvas"""

    def __init__(self, parent, screen_dpi, zoom_level):
        super().__init__(parent)
        self.screen_dpi = screen_dpi
        self.zoom_level = zoom_level
        self.setMinimumHeight(50)

    def update_zoom(self, zoom_level):
        """Update scale according to zoom level"""
        self.zoom_level = zoom_level
        self.update()

    def paintEvent(self, event):  # type: ignore
        """pass"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Setting
        width = self.width()
        height = self.height()

        start_ruler_x = 20
        end_ruler_x = width - 20

        # Color
        painter.setPen(QPen(QColor(255, 255, 255), 2))
        painter.setBrush(QBrush(QColor(255, 255, 255)))

        # will need to move it to a higher level in the main window in order to reuse it.
        cm_in_pixels = self.screen_dpi / 2.54  # DPI to pixels per cm
        zoomed_cm_pixels = cm_in_pixels * self.zoom_level

        # Determining the appropriate interval for the labels
        if zoomed_cm_pixels > 100:
            interval_pixels = zoomed_cm_pixels / 10  # to 1 mm
            unit_multiplier = 1
        else:
            interval_pixels = zoomed_cm_pixels
            unit_multiplier = 10

        # If the interval is too small, we increase it
        while interval_pixels < 20 and unit_multiplier < 100:
            interval_pixels *= 5
            unit_multiplier *= 5

        # Drawing the main line
        painter.drawLine(start_ruler_x, height - 20, end_ruler_x, height - 20)

        # Divisions and signatures
        x_pos = start_ruler_x
        mark_count = 0

        font = painter.font()
        font.setPointSize(10)
        painter.setFont(font)

        # We define the step for the divisions depending on the zoom
        if zoomed_cm_pixels < 60:  # mead zoom
            # Показываем каждый 1 cm
            step_pixels = zoomed_cm_pixels
            step_value_cm = 1
            unit_display = "cm"
        elif zoomed_cm_pixels < 150:  # big zoom
            # every 5 mm
            step_pixels = zoomed_cm_pixels / 2
            step_value_cm = 0.5  # cm
            unit_display = "mm"
        else:  # large zoom
            step_pixels = zoomed_cm_pixels / 10
            step_value_cm = 0.1
            unit_display = "mm"

        while x_pos < end_ruler_x:
            painter.drawLine(int(x_pos), height - 30, int(x_pos), height - 10)

            total_cm = mark_count * step_value_cm

            if unit_display == "mm":
                value = int(total_cm * 10)
                text = str(value)
            else:
                if step_value_cm >= 1:
                    value = int(total_cm)
                else:
                    value = total_cm
                text = str(value)

            scale_x_offset = len(text) * 4
            painter.drawText(int(x_pos - scale_x_offset), height - 35, text)

            # Small divisions
            if step_pixels > 20:  # Only if there is enough space
                for i in range(1, 6):
                    small_x = x_pos + (step_pixels * i / 6)
                    if small_x < end_ruler_x:
                        painter.drawLine(int(small_x), height -
                                         22, int(small_x), height - 18)

            x_pos += step_pixels
            mark_count += 1

        painter.drawText(int(width/2), height, unit_display)
