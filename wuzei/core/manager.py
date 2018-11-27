import pathlib
import typing

from wuzei.utils import windesktop
from wuzei.utils.finder import find_images
from .blur import blur
from .dispenser import Dispenser


class WallpaperManager:
    def __init__(self,
                 paths: typing.List[str],
                 cache_dir: str,
                 blurred: bool = True,
                 shuffled: bool = True,
                 logger=None):
        if not logger:
            logger = print
        if not paths or not cache_dir:
            raise ValueError('Specify at least one path')

        self.logger = logger
        self._cache_dir = cache_dir
        self._blurred = blurred
        self._shuffled = shuffled
        self._wallpaper: str = None
        self._screen_geometry = windesktop.get_screen_size()

        self.sources = Dispenser(paths)
        self.images: Dispenser = None
        self.source = self.sources.current

    @property
    def wallpaper(self):
        return self._wallpaper

    @wallpaper.setter
    def wallpaper(self, image_path: str):
        self._wallpaper = image_path
        if self._blurred:
            self.blur(image_path)
        else:
            self._set_wallpaper(image_path)

    @property
    def source(self):
        return self._source

    @source.setter
    def source(self, path: str):
        self._source = path
        self.images = Dispenser(find_images(path),
                                shuffled=self._shuffled)
        if self._shuffled:
            image = self.images.random()
        else:
            image = self.images.current
        self.wallpaper = image

    def sync(self, path: str):
        # prevent unnecessary syncs for inactive sources
        if self._source != path:
            return self.logger('WONT SYNC', path)
        self.images.things = find_images(path)
        self.logger('SYNCED', self._source)

    def next_source(self):
        self.source = self.sources + 1

    def prev_source(self):
        self.source = self.sources - 1

    def next_wallpaper(self):
        self.wallpaper = self.images + 1

    def prev_wallpaper(self):
        self.wallpaper = self.images - 1

    def toggle_shuffle(self):
        if self._shuffled:
            self.images.unshuffle()
        else:
            self.images.shuffle()
        self._shuffled = not self._shuffled

    def blur(self, image_path: str = None):
        if not image_path:
            image_path = self._wallpaper
        long_side = max(self._screen_geometry)
        blurred_image = blur(image_path,
                             radius=long_side // 10,
                             size=(long_side, long_side),
                             save_dir=self._cache_dir,
                             use_cache=True)
        self._set_wallpaper(str(blurred_image))
        self._blurred = True

    def unblur(self):
        self._blurred = False
        self._set_wallpaper(self._wallpaper)

    def toggle_blur(self):
        if self._blurred:
            self.unblur()
        else:
            self.blur()

    def _set_wallpaper(self, image_path: str = ''):
        if not image_path:
            image_path = self.wallpaper
        if not pathlib.Path(image_path).exists():
            raise FileNotFoundError(image_path)
        self.logger('WP', image_path)
        windesktop.change_wallpaper(image_path, True)
