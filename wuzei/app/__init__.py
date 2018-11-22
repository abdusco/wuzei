import os
import threading
import time
from enum import Enum, auto

import keyboard
import mouse
from pymitter import EventEmitter

from wuzei.app.config import WuzeiConfig
from wuzei.core.manager import WallpaperManager
from wuzei.utils.session import SessionEvent, SessionMonitor
from wuzei.utils.singleton import InterruptibleEvent
from wuzei.utils.windesktop import WindowSpy


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


class Wuzei:
    def __init__(self, config: WuzeiConfig):
        self.ee = EventEmitter()
        self.ee.on('lock', self._on_lock)
        self.ee.on('unlock', self._on_unlock)
        self.ee.on('hotkey', self._on_hotkey)
        self.ee.on('timer', self._on_timer)
        self.threads = []
        self.running_event = InterruptibleEvent()
        self.last_change = time.time()

        self.paused = config.start_paused
        self.interval = config.interval

        sources = [path for key, path in config.sources.items()]
        self.manager = WallpaperManager(paths=sources,
                                        cache_dir=config.cache_dir,
                                        start_blurred=config.start_blurred,
                                        start_shuffled=config.start_shuffled)

    def _monitor_hotkeys(self):
        hotkeys = {
            'alt+shift+left': Action.PREV_WALLPAPER,
            'alt+shift+right': Action.NEXT_WALLPAPER,
            'alt+shift+s': Action.TOGGLE_SHUFFLE,
            'alt+shift+b': Action.TOGGLE_BLUR,
            'alt+shift+/': Action.BLUR,
            'alt+shift+\\': 'exit',
            'alt+shift+p': 'pause',
        }
        for combination, action in hotkeys.items():
            keyboard.add_hotkey(combination,
                                callback=self.ee.emit,
                                args=['hotkey', action])

    def _monitor_session(self):
        sm = SessionMonitor()
        sm.subscribe(SessionEvent.SESSION_LOCK, self.ee.emit, 'lock')
        sm.subscribe(SessionEvent.SESSION_UNLOCK, self.ee.emit, 'unlock')
        sm.listen()

    def _setup_timer(self):
        while True and self.interval > 0:
            time.sleep(self.interval)
            if abs(time.time() - self.last_change) < self.interval:
                continue
            if not self.paused:
                self.ee.emit('timer')

    def _on_timer(self):
        print('TIMER')
        self.manager.next_wallpaper()

    def _on_lock(self):
        print('LOCKED')
        self.manager.blur()

    def _on_unlock(self):
        print('UNLOCKED')
        keyboard.stash_state()

    def _on_desktop_click(self):
        print('DESKTOP CLICKED')
        self.manager.toggle_blur()

    def _rehook(self):
        while True:
            time.sleep(5)
            keyboard.stash_state()

    def _hook_mouse(self):
        desktop = WindowSpy.desktop()

        def cb():
            if not desktop.is_under_mouse:
                return
            self._on_desktop_click()

        mouse.on_double_click(cb)

    def _on_hotkey(self, action: Action):
        print('HOTKEY', action)
        handlers = {
            Action.PREV_WALLPAPER: self.manager.prev_wallpaper,
            Action.NEXT_WALLPAPER: self.manager.next_wallpaper,
            Action.TOGGLE_SHUFFLE: self.manager.toggle_shuffle,
            Action.TOGGLE_BLUR: self.manager.toggle_blur,
            Action.BLUR: self.manager.blur,
            'exit': self.exit,
            'pause': self.pause,
        }
        handlers[action]()
        self.last_change = time.time()

    def pause(self):
        self.paused = not self.paused
        print('PAUSED' if self.paused else 'RUNNING')

    def exit(self):
        self.running_event.set()
        print('Bye')
        os._exit(0)

    def run(self):
        threads = dict(
            session=threading.Thread(target=self._monitor_session),
            keyboard=threading.Thread(target=self._monitor_hotkeys),
            timer=threading.Thread(target=self._setup_timer),
            rehook=threading.Thread(target=self._rehook),
            mouse=threading.Thread(target=self._hook_mouse),
        )

        self.threads = threads
        for name, th in threads.items():
            th.start()
        self.running_event.wait()
