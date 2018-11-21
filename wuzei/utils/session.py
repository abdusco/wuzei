from collections import defaultdict
from enum import Enum
import win32api
import win32con
import win32gui
import win32ts


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
    CLASS_NAME = "SessionMonitor"
    WINDOW_TITLE = "Session Event Monitor"

    def __init__(self):
        self.window_handle = None
        self.event_handlers = defaultdict(list)
        self._register_listener()

    def _register_listener(self):
        wc = win32gui.WNDCLASS()
        wc.hInstance = handle_instance = win32api.GetModuleHandle(None)
        wc.lpszClassName = self.CLASS_NAME
        wc.lpfnWndProc = self._window_procedure
        window_class = win32gui.RegisterClass(wc)

        style = 0
        self.window_handle = win32gui.CreateWindow(window_class,
                                                   self.WINDOW_TITLE,
                                                   style,
                                                   0, 0, win32con.CW_USEDEFAULT, win32con.CW_USEDEFAULT,
                                                   0, 0, handle_instance, None)
        win32gui.UpdateWindow(self.window_handle)

        # scope = win32ts.NOTIFY_FOR_THIS_SESSION
        scope = win32ts.NOTIFY_FOR_ALL_SESSIONS
        win32ts.WTSRegisterSessionNotification(self.window_handle, scope)

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
        for handler, args, kwargs in self.event_handlers[event]:
            handler(*args, **kwargs)
        for handler, args, kwargs in self.event_handlers[SessionEvent.ANY]:
            handler(*args, **kwargs)

    def subscribe(self, event: SessionEvent, handler: callable, *args, **kwargs):
        self.event_handlers[event].append((handler, args, kwargs))


if __name__ == '__main__':
    m = SessionMonitor()
    m.subscribe(SessionEvent.ANY, handler=print)
    m.listen()
