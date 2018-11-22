import ctypes
import win32api
import win32gui
import win32process

import pythoncom
import pywintypes
import win32com
from win32com.shell import shell, shellcon


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

    def __eq__(self, other):
        return self.h_window == other.h_window

    @staticmethod
    def get_all_handles() -> list:
        def cb(handle, argument):
            argument.append(handle)

        argument = []
        win32gui.EnumWindows(cb, argument)
        return argument

    @classmethod
    def from_mouse_pos(cls):
        h_window = win32gui.WindowFromPoint(win32api.GetCursorPos())
        return cls(h_window)

    @classmethod
    def desktop(cls):
        """
        Returns window handle to desktop (where icons live)

        Read: https://stackoverflow.com/a/5691808

        :return: desktop handle
        """

        def _callback(hwnd, extra):
            if win32gui.GetClassName(hwnd) == "WorkerW":
                child = win32gui.FindWindowEx(hwnd, 0, "SHELLDLL_DefView", "")
                if child != 0:
                    sys_listview = win32gui.FindWindowEx(child, 0, "SysListView32", "FolderView")
                    extra.append(sys_listview)
                    return False
            return True

        """Get the window of the icons, the desktop window contains this window"""
        h_shell = ctypes.windll.user32.GetShellWindow()
        shell_dll_defview = win32gui.FindWindowEx(h_shell, 0, "SHELLDLL_DefView", "")
        if shell_dll_defview == 0:
            sys_listview_container = []
            try:
                win32gui.EnumWindows(_callback, sys_listview_container)
            except pywintypes.error as e:
                if e.winerror != 0:
                    raise
            sys_listview = sys_listview_container[0]
        else:
            sys_listview = win32gui.FindWindowEx(shell_dll_defview, 0, "SysListView32", "FolderView")
        return cls(sys_listview)


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
    progman = ctypes.windll.User32.FindWindowW('Progman', 0)
    cryptic_params = (0x52c, 0, 0, 0, 500, None)
    ctypes.windll.User32.SendMessageTimeoutW(progman, *cryptic_params)


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
