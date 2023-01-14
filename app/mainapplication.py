import os
import sys
import time
import socket
import traceback

from PySide6.QtCore import QObject, QThread, Signal, Slot
from PySide6.QtWidgets import QApplication, QMessageBox

from . import g
from .version import VERSION
from .resources import Resources
from .loggers import ConsoleLogger
from .config import get_config_var
from .state.scan import ScanWorker
from .gui.darkpalette import DarkPalette
from .gui.mainwindow import MainWindow
from .gui.initnaps2dialog import InitNAPS2Dialog
from .gui.configureprofilesdialog import ConfigureProfilesDialog


class MainApplication(QApplication):

    def __init__(self, argv):
        super().__init__(argv)

        self.setApplicationName('FScan')
        self.setStyle('Fusion')
        self.setPalette(DarkPalette())
        self.setStyleSheet("""
            QPushButton::disabled {
                background-color: #303030;
                color: #2e2e2e;
            }
        """)

        self.log = ConsoleLogger.new(__name__)
        self.r = Resources()
        g.init(self.log, self.r)

        self.main = MainWindow()
        self.main.setWindowIcon(self.r.iconApp)
        self.main.show()

        self.exceptionDialog = None
        sys.excepthook = self.handleGlobalException

        self.scan_thread = QThread()
        self.scan_worker = ScanWorker()
        self.scan_worker.promptInstallRequested.connect(self.onPromptInstall)
        self.scan_worker.promptConfigureProfilesRequested.connect(self.onPromptConfigureProfiles)

        controls = self.main.w.controls
        controls.scan.configureRequested.connect(self.onConfigureRequested)
        controls.scan.configureProfilesRequested.connect(self.onConfigureProfilesRequested)
        controls.scan.scanRequested.connect(self.onScanRequested)
        self.scan_worker.stateChanged.connect(controls.scan.onScanWorkerStateChanged)

        self.init_naps2_dialog = None
        self.configure_profiles_dialog = None

        g.log.info('FScan v%s | %s | %s' % (VERSION, time.strftime('%r | %A, %B %d, %Y'), socket.gethostname()))
        g.log.debug('Running from %s%s' % (sys.executable, ' (frozen)' if hasattr(sys, 'frozen') else ''))

        if True:
            self.scan_worker.crashed.connect(self.onThreadCrash)
            self.scan_worker.moveToThread(self.scan_thread)
            self.scan_worker.finished.connect(self.scan_thread.quit)
            self.scan_thread.started.connect(self.scan_worker.start)
            self.scan_thread.finished.connect(self.quit)
            self.aboutToQuit.connect(self.onUserQuit)
            self.scan_thread.start()
        else:
            self.scan_worker.run()

    def onUserQuit(self):
        if self.scan_thread and self.scan_worker:
            self.scan_worker.stop()
            self.scan_thread.quit()
            self.scan_thread.wait()

    def onPromptInstall(self, suggested_install):
        if suggested_install:
            g.log.debug('Found existing %s installation:' % ('portable' if suggested_install.is_portable else 'standard'))
            g.log.debug(' App: %s' % suggested_install.app_dir)
            g.log.debug('Data: %s' % suggested_install.data_dir)
        else:
            g.log.debug('No existing NAPS2 installation found.')
        self.showInitNAPS2Dialog(suggested_install)

    def onPromptConfigureProfiles(self, install, profile_config):
        self.showConfigureProfilesDialog(install, profile_config)

    def onConfigureRequested(self):
        self.scan_worker.requestConfigure()

    def onConfigureProfilesRequested(self):
        self.scan_worker.requestConfigureProfiles()
    
    def onScanRequested(self):
        self.scan_worker.requestScan(is_front=True)

    def showInitNAPS2Dialog(self, install):
        if self.init_naps2_dialog or self.configure_profiles_dialog:
            return

        self.init_naps2_dialog = InitNAPS2Dialog(install)
        self.init_naps2_dialog.onSelectAutoInstall.connect(self.onSelectAutoInstall)
        self.init_naps2_dialog.onSelectManualInstall.connect(self.onSelectManualInstall)
        self.init_naps2_dialog.finished.connect(self.onInitNAPS2DialogClosed)
        self.init_naps2_dialog.show()

    def onInitNAPS2DialogClosed(self):
        self.init_naps2_dialog = None

    def onSelectAutoInstall(self):
        if self.init_naps2_dialog:
            self.init_naps2_dialog.close()
            self.init_naps2_dialog = None
            self.scan_worker.autoInstallNAPS2()

    def onSelectManualInstall(self, install):
        if self.init_naps2_dialog:
            self.init_naps2_dialog.close()
            self.init_naps2_dialog = None
            self.scan_worker.setNAPS2Install(install)

    def showConfigureProfilesDialog(self, install, profile_config):
        if self.init_naps2_dialog or self.configure_profiles_dialog:
            return

        self.configure_profiles_dialog = ConfigureProfilesDialog(install, profile_config)
        self.configure_profiles_dialog.finished.connect(self.onConfigureProfilesDialogClosed)
        self.configure_profiles_dialog.show()

    def onConfigureProfilesDialogClosed(self):
        self.configure_profiles_dialog = None

    def onThreadCrash(self, s):
        lines = ['A problem has occurred and this application must exit.', '']
        g.log.critical('>>> ENCOUNTERED AN UNHANDLED EXCEPTION IN WORKER THREAD!')
        for line in s.splitlines():
            g.log.critical(line)
            lines.append(line)
        g.log.critical('>>> THIS ERROR IS FATAL. THE APPLICATION MUST BE RESTARTED.')
        lines.append('')
        lines.append('Please copy and paste the text from this message box to report the issue.')

        QMessageBox.critical(None, 'Error', '\n'.join(lines))
        self.exit(1)

    @staticmethod
    def handleGlobalException(exc_type, exc_val, exc_tb):
        lines = ['A problem has occurred and this application must exit.', '']
        g.log.critical('>>> ENCOUNTERED AN UNHANDLED APPLICATION EXCEPTION!')
        for exc_line in traceback.format_exception(exc_type, exc_val, exc_tb):
            for line in exc_line.splitlines():
                g.log.critical(line)
                lines.append(line)
        g.log.critical('>>> THIS ERROR MAY BE FATAL. THE APPLICATION MAY NOT WORK AS EXPECTED UNTIL RESTARTED.')
        lines.append('')
        lines.append('Please copy and paste the text from this message box to report the issue.')

        QMessageBox.critical(None, 'Error', '\n'.join(lines))

    @classmethod
    def run(cls):
        app = cls(sys.argv)
        result = app.exec_()
        sys.exit(result)
