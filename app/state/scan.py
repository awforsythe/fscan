import time
import traceback
from enum import Enum
from dataclasses import dataclass
from queue import Queue

from PySide6.QtCore import QObject, Signal, Slot

from .. import g
from ..config import get_config_var
from ..core.naps2.data import NAPS2Install
from ..core.naps2.install import disable_naps2, set_configured_naps2_install, get_configured_naps2_install, get_suggested_naps2_install, install_naps2_portable
from ..core.naps2.scan import invoke_naps2_scan

class ScanWorkerState(Enum):
    UNINITIALIZED = 1  # No NAPS2 paths have been configured
    READY_TO_SCAN = 2  # Configured and idle, ready to begin a new scan
    SCANNING = 3       # Currently running a scan


@dataclass
class ExitCommand:
    pass


@dataclass
class InitScanCommand:
    def run(self, worker):
        worker.setInstall(None)
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
class ConfigureScanCommand:
    def run(self, worker):
        install: Optional[NAPS2Install] = get_configured_naps2_install()
        if not install:
            install = get_suggested_naps2_install()
        worker.promptInstallRequested.emit(install)


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
        worker.stateChanged.emit(worker.state)
        invoke_naps2_scan(worker.install, 'TEST', 'E:\\fscan_files\\test\\scan_001.png')
        worker.is_scanning = False
        worker.stateChanged.emit(worker.state)


class ScanWorker(QObject):
    finished = Signal()
    crashed = Signal(str)

    promptInstallRequested = Signal(object)

    stateChanged = Signal(object)

    def __init__(self):
        super().__init__()
        self.exit_requested = False
        self.command_queue = Queue()
        self.command_queue.put(InitScanCommand())

        self.install = None
        self.is_scanning = False
    
    @property
    def state(self):
        if not self.install:
            return ScanWorkerState.UNINITIALIZED
        return ScanWorkerState.SCANNING if self.is_scanning else ScanWorkerState.READY_TO_SCAN

    def setInstall(self, install):
        assert self.state != ScanWorkerState.SCANNING
        self.install = install
        self.stateChanged.emit(self.state)

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
    
    def requestConfigure(self):
        self.command_queue.put(ConfigureScanCommand())

    def requestScan(self):
        self.command_queue.put(ScanCommand())

    def run(self):
        while True:
            command = self.command_queue.get()
            if isinstance(command, ExitCommand):
                break
            command.run(self)
        self.finished.emit()
