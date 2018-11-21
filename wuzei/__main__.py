import sys
from pathlib import Path
from wuzei.app import Wuzei
from wuzei.app.config import WuzeiConfig
from argparse import ArgumentParser
import tempfile
import shelve

parser = ArgumentParser(prog='Wuzei',
                        description='Wallpaper manager for Windows')
parser.add_argument('config_file',
                    action='store',
                    help='path to config.ini file',
                    default='./config.ini')
args = parser.parse_args()

config_path = Path(args.config_file)
if not config_path.exists():
    sys.stderr.write(f'Cannot access config file: {config_path.absolute()}')
    exit(1)

config = WuzeiConfig(config_path)

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
