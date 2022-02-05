import os
import sys
import zipfile
import requests
import urllib.request

from .. import g

GITHUB_API_HEADERS = {'Accept': 'application/vnd.github.v3+json'}
NAPS2_GITHUB_API_URL = 'https://api.github.com/repos/cyanfish/naps2/releases/latest'
NAPS2_ASSET_FILENAME_PATTERN = 'naps2-%s-portable.zip'


def get_naps2_portable_install_dir():
    if hasattr(sys, 'frozen'):
        return os.path.join(os.path.dirname(sys.executable), 'naps2')
    else:
        return os.path.normpath(os.path.join(os.path.dirname(__file__), '..', '..', 'naps2'))


def install_naps2_portable():
    g.log.info('Checking GitHub for latest NAPS2 release...')
    try:
        r = requests.get(NAPS2_GITHUB_API_URL, headers=GITHUB_API_HEADERS, timeout=5.0)
    except Exception as exc:
        g.log.error('Failed to get release data from GitHub API: %s' % exc)
        return False

    if not r.ok:
        desc = ''
        try:
            desc = ': ' + r.json()['message']
        except:
            pass
        g.log.error('Failed to get release data from GitHub API: Error %d%s' % (r.status_code, desc))
        return False

    try:
        release_data = r.json()
    except Exception as exc:
        g.log.error('Failed to decode response data as JSON: %s' % exc)
        return False

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
        return False
    
    asset_id = asset_data['id']
    asset_updated_at = asset_data['updated_at']
    asset_size_in_bytes = asset_data['size']
    g.log.info('%s is asset ID %d; last updated %s; %d bytes total' % (asset_filename, asset_id, asset_updated_at, asset_size_in_bytes))

    install_dirpath = get_naps2_portable_install_dir()
    if os.path.isdir(install_dirpath):
        g.log.debug('Directory exists: %s' % install_dirpath)
    else:
        g.log.info('Creating directory: %s' % install_dirpath)
        os.makedirs(install_dirpath)
    
    zip_filepath = os.path.join(get_naps2_portable_install_dir(), asset_filename)

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
