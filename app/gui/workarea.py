import numpy as np
import cv2

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QSizePolicy
from PySide6.QtGui import QImage, QPainter, QBrush, QColor


class WorkArea(QWidget):

    def __init__(self):
        super().__init__()
        self.setSizePolicy(QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding))
        self.mat = None
        self.image = None

    def resizeEvent(self, event):
        w, h = event.size().width(), event.size().height()
        self.mat = np.zeros((h, w, 3), np.uint8)
        self.mat[:,0:w//2] = (35,35,35)
        self.mat[:,w//2:w] = (35,35,35)

        self.image = QImage(self.mat.data, w, h, 3 * w, QImage.Format_BGR888)

    def paintEvent(self, event):
        p = QPainter(self)
        p.fillRect(self.rect(), QBrush(QColor(192, 208, 222), Qt.DiagCrossPattern))
        if self.image:
            p.drawImage(self.rect(), self.image, self.rect())
