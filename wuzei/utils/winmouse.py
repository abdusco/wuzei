import mouse

from .windesktop import WindowSpy


def listen_desktop_double_click(callback, *args, **kwargs):
    desktop = WindowSpy.desktop()

    def cb():
        if not desktop.is_under_mouse:
            return
        callback(*args, **kwargs)

    mouse.on_double_click(cb)
    from threading import Lock
    lock = Lock()
    lock.acquire()
    lock.acquire()
