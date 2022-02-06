import os
import re
import sys
from typing import Optional

from . import g

COMMENT_REGEX = re.compile(r';.*')
VALUE_REGEX = re.compile(r'\s*([0-9A-Za-z_\-]+)\s*=(.*)')

__config__: Optional[dict[str, str]] = None


def _get_fscan_ini_path() -> str:
    if hasattr(sys, 'frozen'):
        return os.path.join(os.path.dirname(sys.executable), 'fscan.ini')
    else:
        return os.path.normpath(os.path.join(os.path.dirname(__file__), '..', 'fscan.ini'))


def _merge_config_from_file(filepath: str, out_dict: dict[str, str]):
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


def _update_config_line(new_values_by_name: dict[str, Optional[str]], line: str) -> tuple[Optional[str], Optional[str]]:
    comment_match = COMMENT_REGEX.search(line)
    if comment_match:
        pos = comment_match.span()[0]
        line, comment = (line[:pos].strip(), ' ' + line[pos:].strip())
    else:
        line, comment = line.strip(), ''
    
    value_match = VALUE_REGEX.match(line)
    if value_match:
        key = value_match.group(1)
        if key in new_values_by_name:
            new_value = new_values_by_name[key]
            if new_value is None:
                return None, key
            else:
                return ('%s=%s%s' % (key, new_value, comment), key)
    return line + comment, None


def _get_config() -> dict[str, str]:
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


def get_config_var(name: str, default: Optional[str] = None) -> Optional[str]:
    if name in os.environ:
        return os.environ[name]
    return _get_config().get(name, default)


def update_config(new_values_by_name: dict[str, Optional[str]]):
    global __config__

    # Ensure our config object is loaded, and update it so that subsequent
    # get_config_var() calls will reflect the new values
    _get_config()
    for key, value in new_values_by_name.items():
        if value is not None:
            __config__[key] = value
        elif key in __config__:
            del __config__[key]
        # Ensure that any environment overrides are disabled for this process
        if key in os.environ and os.environ[key] != value:
            g.log.warn('fscan.ini is overridden via environment variable %s=%s' % (key, os.environ[key]))
            g.log.warn('Value will be changed')
            os.environ[key] = value

    # Get the existing contents of the user-local config file, if any, line-by-line
    user_config = os.path.join(os.path.expanduser('~'), 'fscan.ini')
    if os.path.isfile(user_config):
        with open(user_config) as fp:
            config_lines = fp.readlines()
    else:
        config_lines = []

    # Update any lines that contain the variables we want to change, and add lines for
    # any that weren't previously defined in the file
    new_config_lines = []
    config_keys_to_add = set(new_values_by_name.keys())
    for line in config_lines:
        new_line, updated_key = _update_config_line(new_values_by_name, line)
        if new_line is not None:
            new_config_lines.append(new_line)
        if updated_key:
            config_keys_to_add.remove(updated_key)
    for new_key in config_keys_to_add:
        new_value = new_values_by_name[new_key]
        if new_value is not None:
            new_config_lines.append('%s=%s' % (new_key, new_value))

    # Write the new user config contents to disk, so they'll persist past the lifetime
    # of this process
    with open(user_config, 'w') as fp:
        fp.write('\n'.join(new_config_lines) + '\n')
