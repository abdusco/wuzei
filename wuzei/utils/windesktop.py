import ctypes
import win32api
import win32gui
import win32process

import pythoncom
import pywintypes
import win32com
import win32con
from win32com.shell import shell, shellcon


class Window:
    def __init__(self, class_name: str, title: str, message_map: dict, style: int = None):
        if not style:
            style = win32con.WS_SYSMENU
        self.style = style
        self.title = title
        self.class_name = class_name
        self.message_map = message_map
        self._create()

    def _create(self):
        w_class = win32gui.WNDCLASS()
        self.h_inst = w_class.hInstance = win32gui.GetModuleHandle(None)
        w_class.lpszClassName = self.class_name
        w_class.lpfnWndProc = self.message_map
        self.atom = win32gui.RegisterClass(w_class)
        # w_class.style = win32con.CS_VREDRAW | win32con.CS_HREDRAW
        # w_class.hCursor = win32gui.LoadCursor(0, win32con.IDC_ARROW)
        # w_class.hbrBackground = win32con.COLOR_WINDOW
        # Create the Window.
        self.h_window = win32gui.CreateWindow(self.atom,
                                              self.title,
                                              self.style,
                                              0, 0, win32con.CW_USEDEFAULT, win32con.CW_USEDEFAULT, 0, 0,
                                              self.h_inst,
                                              None)
        win32gui.UpdateWindow(self.h_window)


class WindowSpy:
    def __init__(self, h_window: int):
        self.h_window = h_window

    @property
    def title(self):
        return win32gui.GetWindowText(self.h_window)

    @property
    def visible(self) -> bool:
        return bool(win32gui.IsWindowVisible(self.h_window))

    @property
    def enabled(self) -> bool:
        return bool(win32gui.IsWindowEnabled(self.h_window))

    @property
    def process_id(self) -> int:
        thread_id, process_id = win32process.GetWindowThreadProcessId(self.h_window)
        return process_id

    @property
    def is_under_mouse(self):
        return self.h_window == win32gui.WindowFromPoint(win32api.GetCursorPos())

    @property
    def window_class(self):
        return win32gui.GetClassName(self.h_window)

    def close(self):
        win32gui.CloseWindow(self.h_window)

    def send_message(self, *params):
        return ctypes.windll.user32.SendMessageW(self.h_window, *params)

    def __eq__(self, other):
        return self.h_window == other.h_window

    def __int__(self):
        return self.h_window

    @classmethod
    def from_mouse_pos(cls):
        h_window = win32gui.WindowFromPoint(win32api.GetCursorPos())
        return cls(h_window)

    @classmethod
    def _make_filter_cb(cls, class_name, title):
        def filter_cb(handle, h_list):
            if not (class_name or title):
                h_list.append(handle)
            w = cls(handle)
            if class_name:
                if w.window_class != class_name:
                    return True  # continue enumeration
            if title:
                if w.title != title:
                    return True  # continue enumeration
            h_list.append(handle)

        return filter_cb

    @classmethod
    def find_handles(cls, class_name: str = None, title: str = None) -> list:
        cb = cls._make_filter_cb(class_name, title)
        try:
            handle_list = []
            win32gui.EnumWindows(cb, handle_list)
            return handle_list
        except pywintypes.error as e:
            return []

    def find_children(self, class_name: str = None, title: str = None) -> list:
        cb = self._make_filter_cb(class_name, title)
        try:
            handle_list = []
            win32gui.EnumChildWindows(self.h_window, cb, handle_list)
            return handle_list
        except pywintypes.error as e:
            return []

    @classmethod
    def find(cls, class_name: str, title: str = ''):
        try:
            return cls(cls.find_handles(class_name, title)[0])
        except IndexError:
            return None

    def find_child(self, class_name: str, title: str = ''):
        try:
            return self.__class__(self.find_children(class_name, title)[0])
        except IndexError:
            return None

    @classmethod
    def desktop(cls):
        for h_worker in cls.find_handles(class_name='WorkerW'):
            worker = cls(h_worker)
            folder_view = worker.find_child(class_name='SysListView32', title='FolderView')
            if not folder_view:
                continue
            return folder_view
        return None

    @classmethod
    def taskbar(cls):
        w_tray = cls.find(class_name='Shell_TrayWnd')
        return w_tray.find_child(class_name='MSTaskListWClass')


def get_processes():
    wmi = win32com.client.GetObject('winmgmts:')
    processes = {}
    for p in wmi.InstancesOf('win32_process'):
        processes[p.ProcessID] = p.Name
    return processes


def get_screen_size():
    ctypes.windll.user32.SetProcessDPIAware()
    return (ctypes.windll.user32.GetSystemMetrics(0),
            ctypes.windll.user32.GetSystemMetrics(1))


def force_refresh():
    # RUNDLL32.EXE USER32.DLL,UpdatePerUserSystemParameters 1, True
    ctypes.windll.user32.UpdatePerUserSystemParameters(1)


def enable_active_desktop():
    """
    Taken from:
    https://stackoverflow.com/a/16351170

    In case of a link rot:

    You have to tell windows that you want to enable ActiveDesktop. I tell it every time right before setting the wallpaper through ActiveDesktop.

        public static void EnableActiveDesktop()
        {
            IntPtr result = IntPtr.Zero;
            WinAPI.SendMessageTimeout(WinAPI.FindWindow("Progman", null), 0x52c, IntPtr.Zero, IntPtr.Zero, 0, 500, out result);
        }
    """
    progman = WindowSpy.find(class_name='Progman')
    cryptic_params = (0x52c, 0, 0, 0, 500, None)
    ctypes.windll.User32.SendMessageTimeoutW(progman.h_window, *cryptic_params)


def change_wallpaper(abs_path_to_image: str, activate_active_desktop: bool = False):
    if activate_active_desktop:
        enable_active_desktop()
    pythoncom.CoInitialize()
    iad = pythoncom.CoCreateInstance(shell.CLSID_ActiveDesktop,
                                     None,
                                     pythoncom.CLSCTX_INPROC_SERVER,
                                     shell.IID_IActiveDesktop)
    iad.SetWallpaper(str(abs_path_to_image), 0)
    opts = (shellcon.AD_APPLY_ALL
            # | shellcon.AD_APPLY_FORCE
            # | shellcon.AD_APPLY_BUFFERED_REFRESH
            # | shellcon.AD_APPLY_DYNAMICREFRESH
            )
    iad.ApplyChanges(opts)
    force_refresh()
