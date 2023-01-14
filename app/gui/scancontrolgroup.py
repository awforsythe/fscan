from PySide6.QtCore import Signal
from PySide6.QtWidgets import QWidget, QGridLayout, QLabel, QLineEdit, QPushButton

from .. import g
from ..state.scan import ScanWorkerState


class ScanControlGroup(QWidget):

    configureRequested = Signal()
    configureProfilesRequested = Signal()
    scanRequested = Signal()

    def __init__(self):
        super().__init__()

        self.label_naps2 = QLabel()
        self.label_naps2.setText('NAPS2:')

        self.edit_naps2 = QLineEdit()
        self.edit_naps2.setReadOnly(True)

        self.button_naps2 = QPushButton()
        self.button_naps2.setText('...')
        self.button_naps2.clicked.connect(self.configureRequested)
        self.button_naps2.setEnabled(False)

        self.label_profiles = QLabel()
        self.label_profiles.setText('Profiles:')

        self.edit_profiles = QLineEdit()
        self.edit_profiles.setReadOnly(True)

        self.button_profiles = QPushButton()
        self.button_profiles.setText('...')
        self.button_profiles.clicked.connect(self.configureProfilesRequested)
        self.button_profiles.setEnabled(False)

        self.label_status = QLabel()
        self.label_status.setText('Status:')

        self.edit_status = QLineEdit()
        self.edit_status.setReadOnly(True)

        self.button_scan = QPushButton()
        self.button_scan.setText('Scan')
        self.button_scan.clicked.connect(self.scanRequested)
        self.button_scan.setEnabled(False)

        self.grid = QGridLayout()
        self.grid.setContentsMargins(4, 4, 4, 4)
        self.grid.setSpacing(4)
        self.setLayout(self.grid)

        self.grid.addWidget(self.label_naps2, 0, 0)
        self.grid.addWidget(self.edit_naps2, 0, 1)
        self.grid.addWidget(self.button_naps2, 0, 2)
        self.grid.addWidget(self.label_profiles, 1, 0)
        self.grid.addWidget(self.edit_profiles, 1, 1)
        self.grid.addWidget(self.button_profiles, 1, 2)
        self.grid.addWidget(self.label_status, 2, 0)
        self.grid.addWidget(self.edit_status, 2, 1)
        self.grid.addWidget(self.button_scan, 2, 2)

    def onScanWorkerStateChanged(self, newState, newInstall, newProfileConfig):
        if newInstall:
            self.edit_naps2.setText(newInstall.app_dir)
        else:
            self.edit_naps2.setText('n/a')

        if newProfileConfig:
            self.edit_profiles.setText('%s / %s' % (newProfileConfig.front_profile_name, newProfileConfig.back_profile_name))
        else:
            self.edit_profiles.setText('n/a')

        if newState == ScanWorkerState.UNINITIALIZED:
            self.button_naps2.setEnabled(True)
            self.button_profiles.setEnabled(False)
            self.button_scan.setEnabled(False)
        elif newState == ScanWorkerState.NO_PROFILES:
            self.button_naps2.setEnabled(True)
            self.button_profiles.setEnabled(True)
            self.button_scan.setEnabled(False)
        elif newState == ScanWorkerState.READY_TO_SCAN:
            self.button_naps2.setEnabled(True)
            self.button_profiles.setEnabled(True)
            self.button_scan.setEnabled(True)
        elif newState == ScanWorkerState.SCANNING:
            self.button_naps2.setEnabled(False)
            self.button_profiles.setEnabled(True)
            self.button_scan.setEnabled(False)
        else:
            raise ValueError('Unhandled scan worker state %r' % newState)
