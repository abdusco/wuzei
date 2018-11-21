import ctypes
from win32com.shell import shell, shellcon
from win32api import GetSystemMetrics
import pythoncom
import win32com
import win32gui


def get_processes():
    wmi = win32com.client.GetObject('winmgmts:')
    processes = {}
    for p in wmi.InstancesOf('win32_process'):
        processes[p.ProcessID] = p.Name
    return processes


def get_window_handles() -> list:
    def cb(handle, argument):
        argument.append(handle)

    argument = []
    win32gui.EnumWindows(cb, argument)
    return argument


def get_window_class(window_handle: int):
    return win32gui.GetClassName(window_handle)


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
