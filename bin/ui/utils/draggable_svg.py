# pylint: disable=no-name-in-module
"""pass"""
from PyQt6.QtSvgWidgets import QSvgWidget
from PyQt6.QtCore import Qt, QPoint, QPointF
from PyQt6.QtGui import QMouseEvent


class DraggableSvgWidget(QSvgWidget):
    """pass"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.dragging = False
        self.drag_start_position = QPoint()
        self.setMouseTracking(True)

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            self.dragging = True
            self.drag_start_position = QPointF(event.pos())
            self.setCursor(Qt.CursorShape.ClosedHandCursor)
            event.accept()

    def mouseMoveEvent(self, event: QMouseEvent):
        if self.dragging and event.buttons() == Qt.MouseButton.LeftButton:
            current_pos = QPointF(event.pos())
            delta = current_pos - self.drag_start_position
            new_position = self.pos() + delta.toPoint()

            # Limiting movement to the borders of the parent widget
            if self.parent():
                parent_rect = self.parent().rect()
                widget_rect = self.rect()

                # Проверяем границы
                if new_position.x() < 15:
                    new_position.setX(15)
                elif new_position.x() + widget_rect.width() > parent_rect.width():
                    new_position.setX(parent_rect.width() -
                                      widget_rect.width() - 15)

                if new_position.y() < 0:
                    new_position.setY(0)
                elif new_position.y() + widget_rect.height() > parent_rect.height():
                    new_position.setY(parent_rect.height() -
                                      widget_rect.height())

            self.move(new_position)
            event.accept()

    def mouseReleaseEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            self.dragging = False
            self.setCursor(Qt.CursorShape.OpenHandCursor)
            event.accept()

    def enterEvent(self, event):
        self.setCursor(Qt.CursorShape.OpenHandCursor)
        super().enterEvent(event)

    def leaveEvent(self, event):
        if not self.dragging:
            self.setCursor(Qt.CursorShape.ArrowCursor)
        super().leaveEvent(event)
