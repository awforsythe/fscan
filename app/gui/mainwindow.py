from PySide6.QtCore import Qt
from PySide6.QtWidgets import QMainWindow

from ..version import VERSION
from .mainwidget import MainWidget


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.resize(1140, 800)
        self.move(100, 80)
        self.setWindowTitle("FScan v%s" % VERSION)
        self.setDockOptions(QMainWindow.AnimatedDocks | QMainWindow.AllowNestedDocks | QMainWindow.AllowTabbedDocks | QMainWindow.GroupedDragging)

        self.w = MainWidget()
        self.setCentralWidget(self.w)
