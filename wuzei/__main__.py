import sys
import tempfile
from argparse import ArgumentParser
from pathlib import Path

from wuzei.app import Wuzei
from wuzei.app.config import WuzeiConfig
from wuzei.utils.singleton import run_as_singleton


def get_parser() -> ArgumentParser:
    parser = ArgumentParser(prog='Wuzei',
                            description='Wallpaper manager for Windows')
    parser.add_argument('config_file',
                        action='store',
                        help='path to config.ini file',
                        nargs='?')
    return parser


def main():
    config_paths = ['wuzei.ini', 'config.ini']
    parser = get_parser()
    args = parser.parse_args()
    if not args.config_file:
        for cp in config_paths:
            if Path(cp).exists():
                args.config_file = cp
                break
        else:
            sys.stderr.write(f'Cannot access config file: {config_path.absolute()}\n')
            parser.print_help()
            exit(1)

    config_path = Path(args.config_file)
    try:
        config = WuzeiConfig(config_path)
    except (ValueError, KeyError):
        sys.stderr.write(f'Cannot parse config file: {config_path.absolute()}\n')
        raise

    print('Parsed Config:')
    print('==============')
    print(str(config))
    print()

    if not config.cache_dir:
        with tempfile.TemporaryDirectory(prefix='wuzei') as temp:
            config.cache_dir = temp.name
            w = Wuzei(config)
            w.run()
    else:
        cache_path = Path(config.cache_dir)
        cache_path.mkdir(exist_ok=True)
        w = Wuzei(config)
        w.run()


def wuzei_singleton():
    run_as_singleton(callback=main,
                     instance_name='wuzei')


if __name__ == '__main__':
    wuzei_singleton()
