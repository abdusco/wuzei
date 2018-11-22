import typing
from configparser import ConfigParser


class WuzeiConfig:
    def __init__(self, config_path: str):
        parsed = ConfigParser()
        parsed.read(config_path)

        self.sources: typing.Dict[str, str] = dict(parsed['sources'])
        self.cache_dir: str = parsed['config'].get('cache_dir', '')
        self.blurred: bool = parsed['config'].getboolean('blurred', True)
        self.shuffled: bool = parsed['config'].getboolean('shuffled', True)
        self.paused: bool = parsed['config'].getboolean('paused', False)
        # set interval to min 30 seconds
        self.interval: int = max(30, parsed['config'].getint('interval', 60 * 10))

    def __str__(self):
        return '\n'.join([f'{k.upper()}:\t{v}'
                          for k, v in self.__dict__.items()])
