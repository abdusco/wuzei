import threading
import time


class throttle:
    def __init__(self, cooldown: int):
        self.cooldown = cooldown
        self.has_run = False

    def __call__(self, fn):
        def runnable(*args, **kwargs):
            if self.has_run:
                return
            self.has_run = True
            threading.Thread(target=self._cool).start()
            return fn(*args, **kwargs)

        return runnable

    def _cool(self):
        time.sleep(self.cooldown)
        self.has_run = False
