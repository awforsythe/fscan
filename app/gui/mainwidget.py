from PySide6.QtWidgets import QWidget, QVBoxLayout

from .maincontrols import MainControls
from .workarea import WorkArea
from .consolewidget import ConsoleWidget


class MainWidget(QWidget):

    def __init__(self):
        super().__init__()

        self.controls = MainControls()
        self.workarea = WorkArea()
        self.console = ConsoleWidget()

        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(4, 4, 4, 4)
        self.layout.setSpacing(4)
        self.setLayout(self.layout)

        self.layout.addWidget(self.controls)
        self.layout.addWidget(self.workarea)
        self.layout.addWidget(self.console)
