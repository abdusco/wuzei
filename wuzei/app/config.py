import typing
from configparser import ConfigParser


class WuzeiConfig:
    def __init__(self, config_path: str):
        parsed = ConfigParser()
        parsed.read(config_path)

        self.sources: typing.Dict[str, str] = dict(parsed['sources'])
        self.cache_dir: str = parsed['config'].get('cache_dir', '')
        self.start_blurred: bool = parsed['config'].getboolean('start_blurred', True)
        self.start_shuffled: bool = parsed['config'].getboolean('start_shuffled', True)
        self.start_paused: bool = parsed['config'].getboolean('start_paused', False)
        self.interval: int = parsed['config'].getint('interval', 60 * 10)
