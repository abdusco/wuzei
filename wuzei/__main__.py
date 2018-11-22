import sys
import tempfile
from argparse import ArgumentParser
from pathlib import Path

from wuzei.app import Wuzei
from wuzei.app.config import WuzeiConfig
from wuzei.utils.singleton import singleton


def get_parser() -> ArgumentParser:
    parser = ArgumentParser(prog='Wuzei',
                            description='Wallpaper manager for Windows')
    parser.add_argument('config_file',
                        action='store',
                        help='path to config.ini file',
                        nargs='?',
                        default='./config.ini')
    return parser


def main():
    parser = get_parser()
    args = parser.parse_args()
    config_path = Path(args.config_file)
    if not config_path.exists():
        sys.stderr.write(f'Cannot access config file: {config_path.absolute()}\n')
        parser.print_help()
        exit(1)

    config = WuzeiConfig(config_path)

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


singleton(main,
          instance_name='wuzei')
