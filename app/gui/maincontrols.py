from PySide6.QtWidgets import QWidget, QHBoxLayout

from .scancontrolgroup import ScanControlGroup
from .collectioncontrolgroup import CollectionControlGroup


class MainControls(QWidget):

    def __init__(self):
        super().__init__()

        self.scan = ScanControlGroup()
        self.collection = CollectionControlGroup()

        self.layout = QHBoxLayout()
        self.layout.setContentsMargins(4, 4, 4, 4)
        self.layout.setSpacing(4)
        self.setLayout(self.layout)

        self.layout.addWidget(self.scan)
        self.layout.addWidget(self.collection)
