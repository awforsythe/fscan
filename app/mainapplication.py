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

        controls = self.main.w.controls
        controls.scan.scanRequested.connect(lambda: self.scan_worker.requestScan())

        g.log.info(get_config_var('SOME_CONFIG_VAR', 'defualtvar'))

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
