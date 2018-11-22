import os
import tempfile
import threading
from pathlib import Path


class InterruptibleEvent(threading.Event):
    def wait(self):
        while True:
            if threading.Event.wait(self, 0.5):
                break


def singleton(callback: callable, instance_name: str):
    tempdir = Path(tempfile.gettempdir())
    lockfile = tempdir / f'{instance_name}.lock'
    try:
        if lockfile.exists():
            lockfile.unlink()
    except WindowsError:
        print(f'Another instance of {instance_name} is already running')
        os._exit(1)
    with open(lockfile, 'wb') as handle:
        callback()
    lockfile.unlink()
