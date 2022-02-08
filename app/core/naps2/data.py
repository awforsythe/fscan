import os
from dataclasses import dataclass


@dataclass
class NAPS2Install:
    """
    Represents an installation of NAPS2 (portable or non-portable) that we've confirmed
    is available locally on this system.
    """
    app_dir: str  # Directory containing NAPS2.exe and NAPS2.Console.exe
    data_dir: str # Directory containing profiles.xml

    @property
    def is_portable(self) -> bool:
        app_parent_dir, app_dirname = os.path.split(self.app_dir)
        data_parent_dir, data_dirname = os.path.split(self.data_dir)
        if app_dirname.lower() == 'app' and data_dirname.lower() == 'data':
            return os.path.normpath(app_parent_dir).lower() == os.path.normpath(data_parent_dir).lower()
        return False


@dataclass
class ProfileConfig:
    front_profile_name: str
    back_profile_name: str
