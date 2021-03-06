import os
import threading
import time
from enum import Enum, auto
from functools import partial

import keyboard
import mouse
from pymitter import EventEmitter

from wuzei.app.config import WuzeiConfig
from wuzei.core.manager import WallpaperManager
from wuzei.utils.session import SessionEvent, SessionMonitor
from wuzei.utils.singleton import InterruptibleEvent
from wuzei.utils.throttle import throttle
from wuzei.utils.windesktop import WindowSpy
from wuzei.utils.winfs import DirectoryWatcher


class Action(Enum):
    PREV_WALLPAPER = auto()
    NEXT_WALLPAPER = auto()
    PREV_SOURCE = auto()
    NEXT_SOURCE = auto()

    BLUR = auto()
    UNBLUR = auto()
    TOGGLE_BLUR = auto()

    SHUFFLE = auto()
    UNSHUFFLE = auto()
    TOGGLE_SHUFFLE = auto()

    EXIT = auto()
    PAUSE = auto()
    VIEW = auto()


class Wuzei:
    def __init__(self,
                 config: WuzeiConfig,
                 logger=None):
        if not logger:
            logger = partial(print, sep='\t')
        self.logger = logger
        self.ee = EventEmitter()
        self.ee.on('lock', self._on_lock)
        self.ee.on('unlock', self._on_unlock)
        self.ee.on('hotkey', self._on_hotkey)
        self.ee.on('timer', self._on_timer)
        self.threads = []
        self.running_event = InterruptibleEvent()
        self._update_time()

        self.config = config
        self.paused = config.paused
        self.interval = config.interval

        self._sources = [path for key, path in config.sources.items()]
        self.manager = WallpaperManager(paths=self._sources,
                                        cache_dir=config.cache_dir,
                                        blurred=config.blurred,
                                        shuffled=config.shuffled,
                                        logger=self.logger)

    def _monitor_hotkeys(self):
        actions = dict(
                prev=Action.PREV_WALLPAPER,
                next=Action.NEXT_WALLPAPER,
                prev_source=Action.PREV_SOURCE,
                next_source=Action.NEXT_SOURCE,
                toggle_shuffle=Action.TOGGLE_SHUFFLE,
                toggle_blur=Action.TOGGLE_BLUR,
                blur=Action.BLUR,
                exit=Action.EXIT,
                pause=Action.PAUSE,
                view=Action.VIEW,
        )
        hotkeys = {hotkey: actions[name] for name, hotkey in self.config.hotkeys.items()}
        for combination, action in hotkeys.items():
            keyboard.add_hotkey(combination,
                                callback=self.ee.emit,
                                args=['hotkey', action])

    def _monitor_session(self):
        sm = SessionMonitor()
        sm.subscribe(SessionEvent.SESSION_LOCK, self.ee.emit, 'lock')
        sm.subscribe(SessionEvent.SESSION_UNLOCK, self.ee.emit, 'unlock')
        sm.listen()

    def _monitor_dirs(self):
        cooldown = self.config.dir_monitor_cooldown

        def make_callback(path: str):
            @throttle(cooldown=cooldown + 5)
            def cb(*args):
                self.logger('SOURCE CHANGED', path)
                time.sleep(cooldown)
                self.manager.sync(path)

            return cb

        for path in self._sources:
            callback = make_callback(path)
            watcher = DirectoryWatcher(path=path,
                                       on_deleted=callback,
                                       on_created=callback,
                                       on_renamed=callback)

        while True:
            time.sleep(10)

    def _setup_timer(self):
        while True and self.interval > 0:
            time.sleep(1)
            elapsed = time.time() - self.last_change
            if elapsed < self.interval:
                continue
            if not self.paused:
                self.ee.emit('timer')

    def _on_timer(self):
        self.logger('TIMER')
        self.manager.next_wallpaper()
        self._update_time()

    def _on_lock(self):
        self.logger('LOCKED')
        self.manager.blur()

    def _on_unlock(self):
        self.logger('UNLOCKED')
        keyboard.stash_state()

    def _on_mouse(self, desktop: WindowSpy, taskbar: WindowSpy):
        if desktop.is_under_mouse:
            self.logger('DESKTOP CLICKED')
            self.manager.toggle_blur()
        if taskbar.is_under_mouse:
            self.logger('TASKBAR CLICKED')
            if keyboard.is_pressed('alt'):
                self.manager.blur()
            else:
                self.manager.toggle_blur()

    def _rehook(self):
        while True:
            time.sleep(self.config.hook_refresh_interval)
            keyboard.stash_state()

    def _hook_mouse(self):
        desktop = WindowSpy.desktop()
        taskbar = WindowSpy.taskbar()
        mouse.on_double_click(self._on_mouse, args=(desktop, taskbar))

    def _on_hotkey(self, action: Action):
        self.logger('HOTKEY', action)
        self.handle_action(action)

    def handle_action(self, action: Action):
        try:
            handlers = {
                Action.PREV_WALLPAPER: self.manager.prev_wallpaper,
                Action.NEXT_WALLPAPER: self.manager.next_wallpaper,
                Action.PREV_SOURCE: self.manager.prev_source,
                Action.NEXT_SOURCE: self.manager.next_source,
                Action.TOGGLE_SHUFFLE: self.manager.toggle_shuffle,
                Action.TOGGLE_BLUR: self.manager.toggle_blur,
                Action.BLUR: self.manager.blur,
                Action.PAUSE: self.pause,
                Action.VIEW: self.view_current,
                Action.EXIT: self.exit,
            }
            handlers[action]()
            self._update_time()
        except KeyError:
            self.logger('Unhandled action', action)
            raise NotImplementedError

    def _update_time(self):
        self.last_change = time.time()

    def pause(self):
        self.paused = not self.paused
        self.logger('PAUSED' if self.paused else 'RUNNING')

    def view_current(self):
        os.startfile(self.manager.wallpaper)

    def exit(self):
        self.running_event.set()
        self.logger('Bye')
        os._exit(0)

    def run(self):
        threads = dict(
                keyboard=threading.Thread(target=self._monitor_hotkeys),
                timer=threading.Thread(target=self._setup_timer),
                rehook=threading.Thread(target=self._rehook),
        )
        if self.config.blur_on_lock:
            threads['session'] = threading.Thread(target=self._monitor_session)
        if self.config.monitor_dirs:
            threads['directory'] = threading.Thread(target=self._monitor_dirs)
        if self.config.hook_mouse:
            threads['mouse'] = threading.Thread(target=self._hook_mouse)

        self.threads = threads
        for name, th in threads.items():
            th.start()
        self.running_event.wait()
