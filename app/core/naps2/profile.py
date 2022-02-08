import os
import xml.etree.ElementTree as ET
from typing import Optional

from ... import g
from ...config import get_config_var, update_config
from .data import ProfileConfig


def _parse_profiles_xml(data_dir: str) -> Optional[ET.Element]:
    profiles_xml_path = os.path.join(data_dir, 'profiles.xml')
    if os.path.isfile(profiles_xml_path):
        with open(profiles_xml_path) as fp:
            tree = ET.parse(fp)
        root = tree.getroot()
        assert root.tag == 'ArrayOfScanProfile'
        return root


def list_naps2_device_ids_and_names(data_dir: str) -> list[tuple[str, str]]:
    profiles_xml = _parse_profiles_xml(data_dir)
    if not profiles_xml:
        return []

    device_names_by_id = {}
    for profile in profiles_xml:
        device_elem = profile.find('Device')
        assert device_elem is not None
        id_elem, name_elem = device_elem.find('ID'), device_elem.find('Name')
        assert id_elem is not None and name_elem is not None
        device_names_by_id[id_elem.text] = name_elem.text
    return sorted(device_names_by_id.items(), key=lambda x: x[1])


def list_naps2_profile_names(data_dir: str) -> list[str]:
    profiles_xml = _parse_profiles_xml(data_dir)
    if not profiles_xml:
        return []

    profile_names = set()
    for profile in profiles_xml:
        name_elem = profile.find('DisplayName')
        assert name_elem is not None
        profile_names.add(name_elem.text)
    return sorted(profile_names)


def get_profile_config(data_dir: str) -> Optional[ProfileConfig]:
    front_profile_name = get_config_var('SCAN_PROFILE_NAME_FRONT')
    back_profile_name = get_config_var('SCAN_PROFILE_NAME_BACK')
    if not front_profile_name and not back_profile_name:
        g.log.debug('NAPS2 profile names (SCAN_PROFILE_NAME_FRONT, SCAN_PROFILE_NAME_BACK) not configured.')
        return None

    if not front_profile_name or not back_profile_name:
        var_name = 'SCAN_PROFILE_NAME_BACK' if front_profile_name else 'SCAN_PROFILE_NAME_FRONT'
        g.log.warn('Incomplete profile configuration: %s is not set.' % var_name)
        return None

    profile_names = list_naps2_profile_names(data_dir)
    if front_profile_name not in profile_names:
        g.log.warn("Invalid SCAN_PROFILE_NAME_FRONT: no profile named '%s' exists in the currently-configured NAPS2 installation." % front_profile_name)
        return None
    if back_profile_name not in profile_names:
        g.log.warn("Invalid SCAN_PROFILE_NAME_BACK: no profile named '%s' exists in the currently-configured NAPS2 installation." % front_profile_name)
        return None

    return ProfileConfig(front_profile_name, back_profile_name)


def set_profile_config(new_config: ProfileConfig):
    update_config({
        'SCAN_PROFILE_NAME_FRONT': new_config.front_profile_name,
        'SCAN_PROFILE_NAME_BACK': new_config.back_profile_name,
    })
