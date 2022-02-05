import os
import re
import sys

COMMENT_REGEX = re.compile(r';.*')
VALUE_REGEX = re.compile(r'\s*([0-9A-Za-z_\-]+)\s*=(.*)')

__config__ = None


def _get_fscan_ini_path():
    if hasattr(sys, 'frozen'):
        return os.path.join(os.path.dirname(sys.executable), 'fscan.ini')
    else:
        return os.path.normpath(os.path.join(os.path.dirname(__file__), '..', 'fscan.ini'))


def _merge_config_from_file(filepath, out_dict):
    with open(filepath) as fp:
        for line in fp:
            comment_match = COMMENT_REGEX.search(line)
            if comment_match:
                line = line[:comment_match.span()[0]]
            value_match = VALUE_REGEX.match(line)
            if value_match:
                key = value_match.group(1)
                value = value_match.group(2).strip()
                out_dict[key] = value


def _get_config():
    global __config__
    if __config__ is None:
        __config__ = {}

        # Load defaults from the fscan.ini that's distributed with the application
        _merge_config_from_file(_get_fscan_ini_path(), __config__)

        # If the user has a ~/fscan.ini file, patch in overridden values from it
        user_config = os.path.join(os.path.expanduser('~'), 'fscan.ini')
        if os.path.isfile(user_config):
            _merge_config_from_file(user_config, __config__)

    return __config__


def get_config_var(name, default=None):
    if name in os.environ:
        return os.environ[name]
    return _get_config().get(name, default)
