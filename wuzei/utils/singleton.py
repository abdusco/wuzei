import os
import tempfile
import threading
from pathlib import Path

import psutil


class InterruptibleEvent(threading.Event):
    def wait(self):
        while True:
            if threading.Event.wait(self, 0.5):
                break


def run_as_singleton(callback: callable, instance_name: str):
    tempdir = Path(tempfile.gettempdir())
    lockfile = tempdir / f'{instance_name}.lock'
    pidfile = tempdir / f'{instance_name}.pid'

    is_running = False
    if lockfile.exists():
        # another one might be running
        try:
            lockfile.unlink()
            pidfile.unlink()
        except WindowsError:
            is_running = True
            pass

    if is_running and pidfile.exists():
        try:
            # try to kill older process
            old_pid = int(pidfile.read_text().strip())
            old_process = psutil.Process(old_pid)
            old_process.kill()
            print(f'Killed older {instance_name} instance')
        except ValueError:
            # no pid, nothing we can do
            print(f'Another instance of {instance_name} is already running.')
            print('Exiting')
            os._exit(1)

    with open(lockfile, 'wb') as handle:
        with open(pidfile, 'w') as handle:
            handle.write(str(os.getpid()))
        callback()
    lockfile.unlink()
    pidfile.unlink()
