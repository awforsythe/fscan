from PySide6.QtWidgets import QLabel, QSizePolicy
from PySide6.QtGui import QImage


class WorkArea(QLabel):

    def __init__(self):
        super().__init__()

        self.image = QImage()

        self.setSizePolicy(QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding))
