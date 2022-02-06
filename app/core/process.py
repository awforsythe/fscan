import os
import subprocess

from .. import g


def run_process(args):
    # Echo the command we're about the run
    g.log.debug('> %s' % (args if isinstance(args, str) else ' '.join(args)))

    # Prepare the subprocess args, piping STDOUT and STDERR so we can capture output.
    # If running on Windows, suppress the console window that would ordinarily be spawned when running a pyinstaller-built EXE.
    kwargs = {'stdout': subprocess.PIPE, 'stderr': subprocess.STDOUT}
    if hasattr(subprocess, 'STARTUPINFO'):
        kwargs['startupinfo'] = subprocess.STARTUPINFO()
        kwargs['startupinfo'].dwFlags |= subprocess.STARTF_USESHOWWINDOW
        kwargs['stdin'] = subprocess.PIPE
    process = subprocess.Popen(args, **kwargs)

    with process.stdout:
        for line in iter(process.stdout.readline, b''):
            g.log.debug(line.rstrip().decode('utf-8'))
    exitcode = process.wait()
    if exitcode != 0:
        log.warning('exitcode: %d' % exitcode)
    return exitcode
