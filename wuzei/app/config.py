import typing
from configparser import ConfigParser
from pprint import pformat

import keyboard


class WuzeiConfig:
    def __init__(self, config_path: str):
        parsed = ConfigParser()
        parsed.read(config_path)

        self.sources: typing.Dict[str, str] = dict(parsed['sources'])
        self.cache_dir: str = parsed['config'].get('cache_dir', '')
        self.blurred: bool = parsed['config'].getboolean('blurred', True)
        self.shuffled: bool = parsed['config'].getboolean('shuffled', True)
        self.paused: bool = parsed['config'].getboolean('paused', False)
        self.interval: int = max(30, parsed['config'].getint('interval', 60 * 10))
        self.hook_refresh_interval: int = parsed['config'].getint('hook_refresh_interval', 60)

        self.hotkeys = {}
        if 'hotkeys' in parsed:
            self.hotkeys = {name: hotkey
                            for name, hotkey in parsed['hotkeys'].items()
                            if hotkey}
        self._validate_hotkeys()

    def _validate_hotkeys(self):
        errors = []
        for name, hotkey in self.hotkeys.items():
            try:
                keyboard.parse_hotkey(hotkey)
            except ValueError:
                errors.append(f'Invalid hotkey for "{name}". Cannot parse "{hotkey}"')
        if errors:
            for e in errors:
                print(e)
            exit(1)

    def __str__(self):
        out = []
        for k, v in self.__dict__.items():
            if isinstance(v, dict):
                out.append(f'{k.upper()}\n\t{pformat(v, indent=4)}')
            else:
                out.append(f'{k.upper()}\n\t{v}')
        return '\n'.join(out)
