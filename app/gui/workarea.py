from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QSizePolicy
from PySide6.QtGui import QImage, QPainter, QBrush, QColor


class WorkArea(QWidget):

    def __init__(self):
        super().__init__()
        self.setSizePolicy(QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding))

    def resizeEvent(self, event):
        pass

    def paintEvent(self, event):
        p = QPainter(self)
        p.fillRect(self.rect(), QBrush(QColor(192, 208, 222), Qt.DiagCrossPattern))
