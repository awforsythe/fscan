from PySide6.QtCore import Signal
from PySide6.QtWidgets import QWidget, QGridLayout, QLabel, QLineEdit, QPushButton


class CollectionControlGroup(QWidget):

    def __init__(self):
        super().__init__()

        self.label_collection = QLabel()
        self.label_collection.setText('Collection:')

        self.edit_collection = QLineEdit()
        self.edit_collection.setReadOnly(True)

        self.button_collection = QPushButton()
        self.button_collection.setText('...')
        self.button_collection.setEnabled(False)

        self.grid = QGridLayout()
        self.grid.setContentsMargins(4, 4, 4, 4)
        self.grid.setSpacing(4)
        self.setLayout(self.grid)

        self.grid.addWidget(self.label_collection, 0, 0)
        self.grid.addWidget(self.edit_collection, 0, 1)
        self.grid.addWidget(self.button_collection, 0, 2)
