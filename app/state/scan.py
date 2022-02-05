import time
import traceback

from PySide6.QtCore import QObject, Signal, Slot

from ..core.naps2 import install_naps2_portable


class ScanWorker(QObject):
    finished = Signal()
    crashed = Signal(str)

    def __init__(self):
        super().__init__()
        self.exit_requested = False
        self.scan_requested = False

    @Slot()
    def start(self):
        try:
            self.run()
        except Exception:
            self.crashed.emit(traceback.format_exc())

    @Slot()
    def stop(self):
        self.exit_requested = True

    @Slot()
    def requestScan(self):
        self.scan_requested = True

    def run(self):
        while not self.exit_requested:
            time.sleep(0.2)
            if self.scan_requested:
                install_naps2_portable()
                self.scan_requested = False
        self.finished.emit()
