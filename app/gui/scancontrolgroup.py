from PySide6.QtCore import Signal
from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton

from .. import g


class ScanControlGroup(QWidget):

    scanRequested = Signal()

    def __init__(self):
        super().__init__()

        self.button_scan = QPushButton()
        self.button_scan.setText('Scan')
        self.button_scan.clicked.connect(self.scanRequested)

        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(4, 4, 4, 4)
        self.layout.setSpacing(4)
        self.setLayout(self.layout)

        self.layout.addWidget(self.button_scan)
