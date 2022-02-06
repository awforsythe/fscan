import time
import traceback
from dataclasses import dataclass
from queue import Queue

from PySide6.QtCore import QObject, Signal, Slot

from .. import g
from ..config import get_config_var
from ..core.naps2 import (
    NAPS2Install,
    disable_naps2,
    set_configured_naps2_install,
    get_configured_naps2_install,
    get_suggested_naps2_install,
    install_naps2_portable,
)


@dataclass
class ExitCommand:
    pass


@dataclass
class InitScanCommand:
    def run(self, worker):
        is_disabled = get_config_var('NAPS2_DISABLED', 'false').lower() in ('true', '1')
        if is_disabled:
            g.log.info('NAPS2 scanning is disabled. Remove NAPS2_DISABLED from ~/fscan.ini to re-enable.')
            return

        install: Optional[NAPS2Install] = get_configured_naps2_install()
        if not install:
            # Open a dialog prompting the user to configure a NAPS2 installation: and
            # wait a beat so we don't open a dialog immediately on application startup
            time.sleep(0.5)
            suggested_install: Optional[NAPS2Install] = get_suggested_naps2_install()
            worker.promptInstallRequested.emit(suggested_install)
            return

        # Configure
        worker.setInstall(install)


@dataclass
class DisableScanCommand:
    def run(self, worker):
        disable_naps2()
        g.log.info('Disabled NAPS2 integration.')
        worker.command_queue.put(InitScanCommand())


@dataclass
class SetInstallCommand:
    install: NAPS2Install
    def run(self, worker):
        set_configured_naps2_install(self.install)
        g.log.info('Now using NAPS2 installation at %s.' % self.install.app_dir)
        worker.command_queue.put(InitScanCommand())


@dataclass
class AutoInstallCommand:
    def run(self, worker):
        install: Optional[NAPS2Install] = install_naps2_portable()
        if not install:
            g.log.error('Failed to install NAPS2 portable.')
            return
        g.log.info('Successfully installed a portable copy of NAPS2.')
        worker.command_queue.put(SetInstallCommand(install))


@dataclass
class ScanCommand:
    def run(self, worker):
        if not worker.install:
            g.log.warning('Scan command ignored! NAPS2 integration not configured.')
            return
        if worker.is_scanning:
            g.log.warning('Scan command ignored! Scanning already in progress.')
            return

        worker.is_scanning = True
        worker.canScanChanged.emit(worker.canScan)
        g.log.info('Scan!')
        time.sleep(1)
        g.log.info('3 seconds remaining...')
        time.sleep(1)
        g.log.info('2 seconds remaining...')
        time.sleep(1)
        g.log.info('1 second remaining...')
        time.sleep(1)
        g.log.info('Done!')
        worker.is_scanning = False
        worker.canScanChanged.emit(worker.canScan)


class ScanWorker(QObject):
    finished = Signal()
    crashed = Signal(str)

    promptInstallRequested = Signal(object)

    canScanChanged = Signal(bool)

    def __init__(self):
        super().__init__()
        self.exit_requested = False
        self.command_queue = Queue()
        self.command_queue.put(InitScanCommand())

        self.install = None
        self.is_scanning = False

    def setInstall(self, install):
        assert not self.is_scanning
        self.install = install
        self.canScanChanged.emit(self.canScan)

    @property
    def canScan(self):
        return self.install is not None and not self.is_scanning

    @Slot()
    def start(self):
        try:
            self.run()
        except Exception:
            self.crashed.emit(traceback.format_exc())

    @Slot()
    def stop(self):
        self.command_queue.put(ExitCommand())

    def disableNAPS2(self):
        self.command_queue.put(DisableScanCommand())

    def setNAPS2Install(self, install: NAPS2Install):
        self.command_queue.put(SetInstallCommand(install))

    def autoInstallNAPS2(self):
        self.command_queue.put(AutoInstallCommand())
    
    def requestScan(self):
        self.command_queue.put(ScanCommand())

    def run(self):
        while True:
            command = self.command_queue.get()
            if isinstance(command, ExitCommand):
                break
            command.run(self)
        self.finished.emit()
