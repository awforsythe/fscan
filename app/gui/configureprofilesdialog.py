from PySide6.QtCore import Qt, QSize
from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel

from .. import g
from ..core.naps2.profile import list_naps2_devices, list_naps2_profile_names


class ConfigureProfilesDialog(QDialog):

    def __init__(self, install, profile_config):
        super().__init__()
        self.install = install
        self.profile_config = profile_config

        self.setWindowFlags(Qt.Dialog | Qt.WindowStaysOnTopHint)
        self.setWindowTitle('Configure Profiles')

        devices = list_naps2_devices(self.install.data_dir)
        profile_names = list_naps2_profile_names(self.install.data_dir)
        g.log.debug(devices)
        g.log.debug(profile_names)

        # Start with a brief blurb explaining what this dialog is about
        self.label_statement = QLabel()
        self.label_statement.setWordWrap(True)
        self.label_statement.setText(self.install.app_dir)

        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(12, 12, 12, 12)
        self.layout.setSpacing(8)
        self.setLayout(self.layout)

        self.layout.addWidget(self.label_statement)

    def sizeHint(self):
        return QSize(480, 100)
