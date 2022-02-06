import os
import sys
import zipfile
import subprocess
import requests
import urllib.request
from dataclasses import dataclass
from typing import Optional

from .. import g
from ..config import get_config_var, update_config
from .process import run_process

GITHUB_API_HEADERS = {'Accept': 'application/vnd.github.v3+json'}
NAPS2_GITHUB_API_URL = 'https://api.github.com/repos/cyanfish/naps2/releases/latest'
NAPS2_ASSET_FILENAME_PATTERN = 'naps2-%s-portable.zip'


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


def _capitalize_drive_letter(s):
        if len(s) >= 2 and s[1] == ':' and s[0] >= 'a' and s[0] <= 'z':
            return s[0].upper() + s[1:]
        return s


def _get_binary_dir() -> str:
    if hasattr(sys, 'frozen'):
        return _capitalize_drive_letter(os.path.dirname(sys.executable))
    else:
        return _capitalize_drive_letter(os.path.normpath(os.path.join(os.path.dirname(__file__), '..', '..')))


def _normalize_config_path(path: str) -> str:
    if os.path.isabs(path):
        return _capitalize_drive_letter(os.path.normpath(path))
    return _capitalize_drive_letter(os.path.normpath(os.path.join(_get_binary_dir(), path)))


def get_naps2_portable_install_path() -> str:
    return os.path.join(_get_binary_dir(), 'naps2')


def get_naps2_default_app_dir() -> str:
    program_files_x86_dir = os.getenv('ProgramFiles(x86)', 'C:\\Program Files (x86)')
    return os.path.join(program_files_x86_dir, 'NAPS2')


def get_naps2_default_data_dir() -> str:
    appdata_dir = os.getenv('APPDATA')
    if not appdata_dir:
        return ''
    return os.path.join(appdata_dir, 'NAPS2')


def disable_naps2():
    """
    Adds NAPS2_DISABLED=true to the user config file, indicating that the user doesn't
    want to use the program's NAPS2 scanning functionality at all.
    """
    update_config({
        'NAPS2_DISABLED': 'true',
    })


def set_configured_naps2_install(install: NAPS2Install):
    binary_dir = _get_binary_dir()

    app_dir = os.path.normpath(install.app_dir)
    if os.path.isabs(app_dir) and app_dir.lower().startswith(binary_dir.lower()):
        app_dir = '.' + os.sep + app_dir[len(binary_dir):].lstrip(os.sep)

    data_dir = os.path.normpath(install.data_dir)
    if os.path.isabs(data_dir) and data_dir.lower().startswith(binary_dir.lower()):
        data_dir = '.' + os.sep + data_dir[len(binary_dir):].lstrip(os.sep)

    update_config({
        'NAPS2_DISABLED': None,
        'NAPS2_APP_DIR': app_dir,
        'NAPS2_DATA_DIR': data_dir,
    })


def get_configured_naps2_install() -> Optional[NAPS2Install]:
    """
    Checks NAPS2_APP_DIR and NAPS2_DATA_DIR: if set to valid paths, and if NAPS2
    binaries are found in NAPS2_APP_DIR, returns a NAPS2Install object. Otherwise,
    returns None.
    """
    # If we have no config whatsoever, log no warnings; we just don't have an install
    app_dir = get_config_var('NAPS2_APP_DIR')
    data_dir = get_config_var('NAPS2_DATA_DIR')
    if not app_dir and not data_dir:
        g.log.debug('No NAPS2 installation: NAPS2_APP_DIR and NAPS2_DATA_DIR not configured')
        return None

    # If one path is set but not the other, warn about incomplete configuration
    if bool(app_dir) != bool(data_dir):
        valid_var_name = 'NAPS2_APP_DIR' if app_dir else 'NAPS2_DATA_DIR'
        invalid_var_name = 'NAPS2_DATA_DIR' if app_dir else 'NAPS2_APP_DIR'
        g.log.warn('%s is set, but %s is not' % (valid_var_name, invalid_var_name))
        return None

    # Make sure paths are normalized, and convert relative paths to absolute, making
    # the assumption that they're relative to this executable (not relative to working
    # directory or .ini file)
    assert app_dir and data_dir
    app_dir = _normalize_config_path(app_dir)
    data_dir = _normalize_config_path(data_dir)

    # We have a valid config: check the paths to make sure they point to a NAPS2 install
    if not os.path.isdir(app_dir):
        g.log.warn("NAPS2_APP_DIR refers to a directory that doesn't exist: %s" % app_dir)
        return None

    if not os.path.isdir(data_dir):
        g.log.warn("NAPS2_DATA_DIR refers to a directory that doesn't exist: %s" % data_dir)
        return None

    gui_exe_path = os.path.join(app_dir, 'NAPS2.exe')
    if not os.path.isfile(gui_exe_path):
        g.log.warn('NAPS2_APP_DIR does not contain NAPS2.exe (%s)' % gui_exe_path)
        return None

    console_exe_path = os.path.join(app_dir, 'NAPS2.Console.exe')
    if not os.path.isfile(console_exe_path):
        g.log.warn('NAPS2_APP_DIR does not contain NAPS2.Console.exe (%s)' % console_exe_path)
        return None

    # All paths are good; we have a valid install
    g.log.debug('Resolved a valid NAPS2 installation:')
    g.log.debug(' NAPS2_APP_DIR: %s' % app_dir)
    g.log.debug('NAPS2_DATA_DIR: %s' % data_dir)
    return NAPS2Install(app_dir, data_dir)


def get_suggested_naps2_install() -> Optional[NAPS2Install]:
    """
    Checks the filesystem to see whether there's an existing NAPS2 installation that's
    not yet configured via NAPS2_APP_DIR and NAPS2_DATA_DIR. First checks for a
    portable version installed in a 'naps2' subdirectory alongside this program, then
    falls back to the default paths for a standard, non-portable install. If neither is
    found, returns None.
    """    
    # Check for a valid portable install in ./naps2, relative to fscan
    portable_app_dir = os.path.join(_get_binary_dir(), 'naps2', 'App')
    portable_data_dir = os.path.join(_get_binary_dir(), 'naps2', 'Data')
    if os.path.isdir(portable_app_dir) and os.path.isdir(portable_data_dir):
        gui_exe_path = os.path.join(portable_app_dir, 'NAPS2.exe')
        console_exe_path = os.path.join(portable_app_dir, 'NAPS2.Console.exe')
        if os.path.isfile(gui_exe_path) and os.path.isfile(console_exe_path):
            return NAPS2Install(portable_app_dir, portable_data_dir)

    # Check the default non-portable install path
    installed_app_dir = get_naps2_default_app_dir()
    if os.path.isdir(installed_app_dir):
        gui_exe_path = os.path.join(installed_app_dir, 'NAPS2.exe')
        console_exe_path = os.path.join(installed_app_dir, 'NAPS2.Console.exe')
        if os.path.isfile(gui_exe_path) and os.path.isfile(console_exe_path):
            return NAPS2Install(installed_app_dir, get_naps2_default_data_dir())


def install_naps2_portable() -> Optional[NAPS2Install]:
    install_dirpath = os.path.join(_get_binary_dir(), 'naps2')
    g.log.info('Will install NAPS2 portable to: %s' % install_dirpath)
    if os.path.isdir(install_dirpath):
        g.log.warn('Directory exists: %s' % install_dirpath)
    else:
        g.log.info('Creating directory: %s' % install_dirpath)
        os.makedirs(install_dirpath)

    g.log.info('Checking GitHub for latest NAPS2 release...')
    try:
        r = requests.get(NAPS2_GITHUB_API_URL, headers=GITHUB_API_HEADERS, timeout=5.0)
    except Exception as exc:
        g.log.error('Failed to get release data from GitHub API: %s' % exc)
        return None

    if not r.ok:
        desc = ''
        try:
            desc = ': ' + r.json()['message']
        except:
            pass
        g.log.error('Failed to get release data from GitHub API: Error %d%s' % (r.status_code, desc))
        return None

    try:
        release_data = r.json()
    except Exception as exc:
        g.log.error('Failed to decode response data as JSON: %s' % exc)
        return None

    release_name = release_data['name']
    release_id = release_data['id']
    g.log.info('Latest version is %s; release ID %d' % (release_name, release_id))

    asset_filename = NAPS2_ASSET_FILENAME_PATTERN % release_name
    asset_data = next((x for x in release_data['assets'] if x['name'] == asset_filename), None)
    if not asset_data:
        g.log.debug('Could not find portable .zip archive with expected name; dumping %d asset names:' % len(release_data['assets']))
        for asset in release_data['assets']:
            g.log.debug('- %s' % asset['name'])
        g.log.error('Release contains no asset named %s!' % asset_filename)
        return None
    
    asset_id = asset_data['id']
    asset_updated_at = asset_data['updated_at']
    asset_size_in_bytes = asset_data['size']
    g.log.info('%s is asset ID %d; last updated %s; %d bytes total' % (asset_filename, asset_id, asset_updated_at, asset_size_in_bytes))
    
    zip_filepath = os.path.join(install_dirpath, asset_filename)

    asset_url = asset_data['browser_download_url']
    g.log.info('Downloading NAPS2 v%s portable release...' % release_name)
    g.log.info('From: %s' % asset_url)
    g.log.info('  To: %s' % zip_filepath)
    urllib.request.urlretrieve(asset_url, zip_filepath)
    g.log.info('Downloaded %s.' % asset_filename)

    g.log.info('Extracting NAPS2 to %s...' % install_dirpath)
    with zipfile.ZipFile(zip_filepath, 'r') as zf:
        zf.extractall(install_dirpath)

    g.log.info('Deleting %s...' % asset_filename)
    os.remove(zip_filepath)

    g.log.info('Installed NAPS2 v%s Portable to %s.' % (release_name, install_dirpath))
    return NAPS2Install(os.path.join(install_dirpath, 'App'), os.path.join(install_dirpath, 'Data'))


def invoke_naps2_scan(install, profile_name, output_filepath):
    console_exe_path = os.path.join(install.app_dir, 'NAPS2.Console.exe')
    args = [console_exe_path, '-v', '-p', profile_name, '-o', output_filepath]

    g.log.info("Invoking NAPS2.Console.exe with profile '%s'..." % profile_name)
    exitcode = run_process(args)
    if exitcode != 0:
        raise RuntimeError('NAPS2.Console.exe failed with exit code %d' % exitcode)
    if not os.path.isfile(output_filepath):
        raise RuntimeError('NAPS2.Console.exe failed to write file: %s' % output_filepath)
    g.log.info('Scan finished.')
