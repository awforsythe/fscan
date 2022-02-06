from PySide6.QtCore import Signal
from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton

from .. import g
from ..state.scan import ScanWorkerState


class ScanControlGroup(QWidget):

    configureRequested = Signal()
    scanRequested = Signal()

    def __init__(self):
        super().__init__()

        self.button_configure = QPushButton()
        self.button_configure.setText('Configure...')
        self.button_configure.clicked.connect(self.configureRequested)
        self.button_configure.setEnabled(True)

        self.button_scan = QPushButton()
        self.button_scan.setText('Scan')
        self.button_scan.clicked.connect(self.scanRequested)
        self.button_scan.setEnabled(False)

        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(4, 4, 4, 4)
        self.layout.setSpacing(4)
        self.setLayout(self.layout)

        self.layout.addWidget(self.button_configure)
        self.layout.addWidget(self.button_scan)

    def onScanWorkerStateChanged(self, newState):
        if newState == ScanWorkerState.UNINITIALIZED:
            self.button_configure.setEnabled(True)
            self.button_scan.setEnabled(False)
        elif newState == ScanWorkerState.READY_TO_SCAN:
            self.button_configure.setEnabled(True)
            self.button_scan.setEnabled(True)
        elif newState == ScanWorkerState.SCANNING:
            self.button_configure.setEnabled(False)
            self.button_scan.setEnabled(False)
        else:
            raise ValueError('Unhandled scan worker state %r' % newState)
