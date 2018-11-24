import win32api
import win32gui
import win32ts
from collections import defaultdict
from enum import Enum

import win32con

from .windesktop import WindowSpy


class SessionEvent(Enum):
    ANY = 0
    # window messages
    CHANGE = 0x2B1  # WM_WTSSESSION_CHANGE
    # WM_WTSSESSION_CHANGE events (wparam)
    CONSOLE_CONNECT = 0x1  # WTS_CONSOLE_CONNECT
    CONSOLE_DISCONNECT = 0x2  # WTS_CONSOLE_DISCONNECT
    REMOTE_CONNECT = 0x3  # WTS_REMOTE_CONNECT
    REMOTE_DISCONNECT = 0x4  # WTS_REMOTE_DISCONNECT
    SESSION_LOGON = 0x5  # WTS_SESSION_LOGON
    SESSION_LOGOFF = 0x6  # WTS_SESSION_LOGOFF
    SESSION_LOCK = 0x7  # WTS_SESSION_LOCK
    SESSION_UNLOCK = 0x8  # WTS_SESSION_UNLOCK
    SESSION_REMOTE_CONTROL = 0x9  # WTS_SESSION_REMOTE_CONTROL


class SessionMonitor:
    def __init__(self):
        self.h_window = self.h_instance = None
        self._window_class = 'SessionMonitor'
        self._title = 'Session Event Monitor'
        self._listeners = defaultdict(list)
        self._register_listener()

    def _register_listener(self):
        w_class_struct = win32gui.WNDCLASS()

        # From: https://docs.microsoft.com/en-us/windows/desktop/api/libloaderapi/nf-libloaderapi-getmodulehandlea
        # If this parameter is NULL, GetModuleHandle returns a handle
        # to the file used to create the calling process (.exe file).
        self.h_instance = w_class_struct.hInstance = win32api.GetModuleHandle(None)

        w_class_struct.lpszClassName = self._window_class
        w_class_struct.lpfnWndProc = self._window_procedure
        atom = win32gui.RegisterClass(w_class_struct)

        style = 0
        self.h_window = win32gui.CreateWindow(atom,
                                              self._title,
                                              style,
                                              0, 0, win32con.CW_USEDEFAULT, win32con.CW_USEDEFAULT,
                                              0, 0, self.h_instance, None)
        win32gui.UpdateWindow(self.h_window)

        # scope = win32ts.NOTIFY_FOR_THIS_SESSION
        scope = win32ts.NOTIFY_FOR_ALL_SESSIONS
        win32ts.WTSRegisterSessionNotification(self.h_window, scope)

    def _clean_up(self):
        for h_window in WindowSpy.find_handles(class_name=self._window_class):
            win32gui.CloseWindow(h_window)
        win32gui.UnregisterClass(self._window_class, self.h_instance)

    def listen(self):
        win32gui.PumpMessages()

    def stop(self):
        exit_code = 0
        win32gui.PostQuitMessage(exit_code)

    def _window_procedure(self, window_handle: int, message: int, event_id, session_id):
        """
        # WindowProc callback function

        https://msdn.microsoft.com/en-us/library/ms633573(v=VS.85).aspx
        """
        if message == SessionEvent.CHANGE.value:
            self._handle_session_change(SessionEvent(event_id), session_id)
        elif message == win32con.WM_CLOSE:
            win32gui.DestroyWindow(window_handle)
        elif message == win32con.WM_DESTROY:
            win32gui.PostQuitMessage(0)
        elif message == win32con.WM_QUERYENDSESSION:
            return True

    def _handle_session_change(self, event: SessionEvent, session_id: int):
        for handler, args, kwargs in self._listeners[event]:
            handler(*args, **kwargs)
        for handler, args, kwargs in self._listeners[SessionEvent.ANY]:
            handler(*args, **kwargs)

    def subscribe(self, event: SessionEvent, handler: callable, *args, **kwargs):
        self._listeners[event].append((handler, args, kwargs))


if __name__ == '__main__':
    m = SessionMonitor()
    m.subscribe(SessionEvent.ANY, handler=print)
    m.listen()
