import typing
from configparser import ConfigParser
from pathlib import Path
from pprint import pformat

import keyboard


class WuzeiConfig:
    def __init__(self, config_path: str):
        self.parser = ConfigParser()
        self.parser.read(config_path)

        self._parse()

        errors = []
        errors += self._validate_hotkeys()
        errors += self._validate_paths()

        if errors:
            for e in errors:
                print(e)
            exit(1)

    def _validate_paths(self):
        errors = []
        for source_name, source_path in self.sources.items():
            if not Path(source_path).exists():
                errors.append(f'"{source_path}" does not exist')
        return errors

    def _validate_hotkeys(self):
        errors = []
        for name, hotkey in self.hotkeys.items():
            try:
                keyboard.parse_hotkey(hotkey)
            except ValueError:
                errors.append(f'Invalid hotkey for "{name}". Cannot parse "{hotkey}"')
        return errors

    def __str__(self):
        out = []
        for k, v in self.__dict__.items():
            if isinstance(v, dict):
                out.append(f'{k.upper()}\n\t{pformat(v, indent=4)}')
            else:
                out.append(f'{k.upper()}\n\t{v}')
        return '\n'.join(out)

    def _parse(self):
        self.sources: typing.Dict[str, str] = dict(self.parser['sources'])
        self.cache_dir: str = self.parser['config'].get('cache_dir', '')
        self.blurred: bool = self.parser['config'].getboolean('blurred', True)
        self.shuffled: bool = self.parser['config'].getboolean('shuffled', True)
        self.paused: bool = self.parser['config'].getboolean('paused', False)
        # Dont allow intervals shorter than 20 seconds
        self.interval: int = max(20, self.parser['config'].getint('interval', 60 * 10))
        self.blur_on_lock: bool = self.parser['config'].getboolean('blur_on_lock', True)
        self.monitor_dirs: bool = self.parser['config'].getboolean('monitor_dirs', True)
        self.hook_mouse: bool = self.parser['config'].getboolean('hook_mouse', True)
        self.hook_refresh_interval: int = self.parser['config'].getint('hook_refresh_interval', 60)
        self.dir_monitor_cooldown: int = self.parser['config'].getint('dir_monitor_cooldown', 20)

        self.hotkeys = {}
        if 'hotkeys' in self.parser:
            self.hotkeys = {name: hotkey
                            for name, hotkey in self.parser['hotkeys'].items()
                            if hotkey}
