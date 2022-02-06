import os

from ... import g
from ..process import run_process
from .data import NAPS2Install


def invoke_naps2_scan(install: NAPS2Install, profile_name: str, output_filepath: str):
    console_exe_path = os.path.join(install.app_dir, 'NAPS2.Console.exe')
    args = [console_exe_path, '-v', '-p', profile_name, '-o', output_filepath]

    g.log.info("Invoking NAPS2.Console.exe with profile '%s'..." % profile_name)
    exitcode = run_process(args)
    if exitcode != 0:
        raise RuntimeError('NAPS2.Console.exe failed with exit code %d' % exitcode)
    if not os.path.isfile(output_filepath):
        raise RuntimeError('NAPS2.Console.exe failed to write file: %s' % output_filepath)
    g.log.info('Scan finished.')
