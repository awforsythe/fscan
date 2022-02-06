import os
import sys

from PySide6.QtCore import Qt, Signal, QSize
from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QGroupBox, QPushButton, QGridLayout, QLineEdit, QFileDialog, QMessageBox

from .. import g
from ..core.naps2 import NAPS2Install, get_naps2_portable_install_path, get_naps2_default_app_dir, get_naps2_default_data_dir


class InitNAPS2Dialog(QDialog):

    onSelectAutoInstall = Signal()
    onSelectManualInstall = Signal(object)
    onSelectDisable = Signal()

    def __init__(self, install):
        super().__init__()
        self.install = install

        self.setWindowFlags(Qt.Dialog | Qt.WindowStaysOnTopHint)
        self.setWindowTitle('Configure NAPS2')

        # Start with a brief blurb explaining what this dialog is about
        self.label_statement = QLabel()
        self.label_statement.setWordWrap(True)
        self.label_statement.setText(
            'FScan includes support for NAPS2, allowing you to control your scanner '
            'and trigger new scans from directly within this program.'
        )

        # Include some background info re: NAPS2, inset within a group box
        self.group_naps2 = QGroupBox()

        self.label_naps2_info = QLabel()
        self.label_naps2_info.setWordWrap(True)
        self.label_naps2_info.setText(
            'NAPS2 (Not Another PDF Scanner 2) is a free and open-source scanning '
            'application developed by Ben Olden-Cooligan. You can learn more about '
            'NAPS2 at its official website:'
        )

        self.button_naps2_url = QPushButton()
        self.button_naps2_url.setText('https://www.naps2.com/')

        self.label_naps2_disclaimer = QLabel()
        self.label_naps2_disclaimer.setWordWrap(True)
        self.label_naps2_disclaimer.setText(
            'NAPS2 is not affiliated with FScan: it just happens to be one of the '
            'tools available on Windows for interfacing with scanners.'
        )

        # Explain the choices: first, we can automatically download a portable build
        self.label_auto_install = QLabel()
        self.label_auto_install.setWordWrap(True)
        self.label_auto_install.setText(
            'FScan can automatically download its own version of NAPS2 - this is a '
            'portable installation that will be kept alongside FScan, in %s. Your '
            'system configuration will not be modified in any way, and this portable '
            'copy of NAPS2 will be removed when you uninstall FScan.' % (
                get_naps2_portable_install_path()
            )
        )

        self.button_auto_install = QPushButton()
        self.button_auto_install.setText('Install NAPS2 for me')
        self.button_auto_install.clicked.connect(self.onSelectAutoInstall.emit)

        # Alternatively, we can use a version of NAPS2 installed by the user: if we've
        # already detected a valid installation, suggest using it outright
        self.label_manual_install = QLabel()
        self.label_manual_install.setWordWrap(True)
        if self.install:
            coda = 'It looks like you already have a compatible version of NAPS2 installed'
        else:
            coda = 'You can simply download and run the installer from the URL above, then click the button below'
        self.label_manual_install.setText(
            'Alternatively, you can install NAPS2 yourself and configure FScan with '
            'the path to that installation. %s:' % coda
        )

        self.label_app_dir = QLabel()
        self.label_app_dir.setText('App:')

        self.label_data_dir = QLabel()
        self.label_data_dir.setText('Data:')

        self.edit_app_dir = QLineEdit()
        self.edit_app_dir.setText(self.install.app_dir if self.install else get_naps2_default_app_dir())

        self.edit_data_dir = QLineEdit()
        self.edit_data_dir.setText(self.install.data_dir if self.install else get_naps2_default_data_dir())

        self.button_app_dir = QPushButton()
        self.button_app_dir.setText('...')
        self.button_app_dir.clicked.connect(self.onBrowseToAppDir)

        self.button_data_dir = QPushButton()
        self.button_data_dir.setText('...')
        self.button_data_dir.clicked.connect(self.onBrowseToDataDir)

        self.grid_manual_install = QGridLayout()
        self.grid_manual_install.setContentsMargins(4, 0, 4, 0)
        self.grid_manual_install.setSpacing(4)
        self.grid_manual_install.addWidget(self.label_app_dir, 0, 0)
        self.grid_manual_install.addWidget(self.label_data_dir, 1, 0)
        self.grid_manual_install.addWidget(self.edit_app_dir, 0, 1)
        self.grid_manual_install.addWidget(self.edit_data_dir, 1, 1)
        self.grid_manual_install.addWidget(self.button_app_dir, 0, 2)
        self.grid_manual_install.addWidget(self.button_data_dir, 1, 2)

        self.button_manual_install = QPushButton()
        self.button_manual_install.setText('Use my NAPS2 installation')
        self.button_manual_install.clicked.connect(self.onCommitManualInstallation)

        # Finally, we can disable NAPS2 support entirely
        self.label_disable_naps2 = QLabel()
        self.label_disable_naps2.setWordWrap(True)
        self.label_disable_naps2.setText(
            'If you\'d prefer to use a different scanning solution, you can also '
            'disable NAPS2 integration completely:'
        )

        self.button_disable_naps2 = QPushButton()
        self.button_disable_naps2.setText('Disable NAPS2 integration')
        self.button_disable_naps2.clicked.connect(self.onSelectDisable.emit)

        self.layout_naps2 = QVBoxLayout()
        self.layout_naps2.setContentsMargins(12, 12, 12, 12)
        self.layout_naps2.setSpacing(16)
        self.group_naps2.setLayout(self.layout_naps2)
        self.layout_naps2.addWidget(self.label_naps2_info)
        self.layout_naps2.addWidget(self.button_naps2_url)
        self.layout_naps2.addWidget(self.label_naps2_disclaimer)

        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(12, 12, 12, 12)
        self.layout.setSpacing(8)
        self.setLayout(self.layout)

        self.layout.addWidget(self.label_statement)
        self.layout.addWidget(self.group_naps2)
        self.layout.addSpacing(8)
        self.layout.addWidget(self.label_auto_install)
        self.layout.addWidget(self.button_auto_install)
        self.layout.addSpacing(8)
        self.layout.addWidget(self.label_manual_install)
        self.layout.addLayout(self.grid_manual_install)
        self.layout.addWidget(self.button_manual_install)
        self.layout.addSpacing(8)
        self.layout.addWidget(self.label_disable_naps2)
        self.layout.addWidget(self.button_disable_naps2)

    def sizeHint(self):
        return QSize(480, 100)

    def onBrowseToAppDir(self):
        # Start from a reasonable default directory
        default_dir = None
        app_dir = self.edit_app_dir.text()
        if os.path.isdir(app_dir):
            default_dir = app_dir
        elif os.path.isdir(os.path.dirname(app_dir)):
            default_dir = os.path.dirname(app_dir)
        else:
            program_files_x86_dir = os.getenv('ProgramFiles(x86)', 'C:\\Program Files (x86)')
            if os.path.isdir(program_files_x86_dir):
                default_dir = program_files_x86_dir

        # Open a directory picker to find app_dir, i.e. the directory containing NAPS2.exe
        selected_dir = QFileDialog.getExistingDirectory(self, 'Select NAPS2 App Directory', default_dir)
        if not selected_dir or not os.path.isdir(selected_dir):
            return

        # When the user picks an app dir, we'll automatically update the data dir as well, if we can guess it
        new_app_dir = None
        new_data_dir = None

        # If the user picked the root of a portable install, automatically fix it and set both paths
        if os.path.isdir(os.path.join(selected_dir, 'App')) and os.path.isdir(os.path.join(selected_dir, 'Data')):
            new_app_dir = os.path.join(selected_dir, 'App')
            new_data_dir = os.path.join(selected_dir, 'Data')
        else:
            new_app_dir = selected_dir
            
            # If the selected dir points to a portable installation's 'App' dir, use the corresponding 'Data' dir
            # Otherwise, assume it's a standard installation which uses %APPDATA%/NAPS2
            app_parent_dir, app_dirname = os.path.split(new_app_dir)
            if app_dirname.lower() == 'app' and os.path.isfile(os.path.join(app_parent_dir, 'NAPS2.Portable.exe')):
                if os.path.isdir(os.path.join(app_parent_dir, 'Data')):
                    new_data_dir = os.path.join(app_parent_dir, 'Data')
            else:
                new_data_dir = get_naps2_default_data_dir()

        # Update our paths
        assert new_app_dir
        self.edit_app_dir.setText(os.path.normpath(new_app_dir))
        if new_data_dir:
            self.edit_data_dir.setText(os.path.normpath(new_data_dir))

    def onBrowseToDataDir(self):
        # Start from a reasonable default directory
        default_dir = None
        data_dir = self.edit_data_dir.text()
        if os.path.isdir(data_dir):
            default_dir = data_dir
        elif os.path.isdir(os.path.dirname(data_dir)):
            default_dir = os.path.dirname(data_dir)
        else:
            appdata_dir = os.getenv('APPDATA')
            if appdata_dir and os.path.isdir(appdata_dir):
                default_dir = appdata_dir

        # Open a directory picker to find data_dir, i.e. the directory containing profiles.xml
        new_data_dir = QFileDialog.getExistingDirectory(self, 'Select NAPS2 Data Directory', default_dir)
        if not new_data_dir or not os.path.isdir(new_data_dir):
            return

        # Update our stored data_dir path
        self.edit_data_dir.setText(os.path.normpath(new_data_dir))

    def onCommitManualInstallation(self):
        # Do some very light validation to make sure these paths are good
        app_dir = self.edit_app_dir.text()
        data_dir = self.edit_data_dir.text()
        if not app_dir or not data_dir:
            QMessageBox.warning(
                self, 'Invalid NAPS2 Paths',
                'You must specify an App and Data directory\n'
                'for an existing NAPS2 installation.'
            )
            return

        if not os.path.isdir(app_dir):
            QMessageBox.warning(
                self, 'Invalid NAPS2 Paths',
                'App directory does not exist:\n\n'
                ' %s\n\n'
                'Please select a valid NAPS2 app installation.' % app_dir
            )
            return

        if not os.path.isfile(os.path.join(app_dir, 'NAPS2.exe')):
            QMessageBox.warning(
                self, 'Invalid NAPS2 Paths',
                'Not a valid NAPS2 installation:\n\n'
                ' %s\n\n'
                'Please select a directory that contains NAPS2.exe.' % app_dir
            )
            return

        new_install = NAPS2Install(app_dir, data_dir)
        self.onSelectManualInstall.emit(new_install)
