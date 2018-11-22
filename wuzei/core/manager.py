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
        self._source: str = None
        self._screen_geometry = windesktop.get_screen_size()

        self.sources = Dispenser(paths)
        self.source = self.sources.current

    @property
    def wallpaper(self):
        return self._wallpaper

    @wallpaper.setter
    def wallpaper(self, value: str):
        self._wallpaper = value
        self._set_wallpaper(value)

    @property
    def source(self):
        return self._source

    @source.setter
    def source(self, value):
        self._source = value
        self.images = Dispenser(find_images(value),
                                shuffled=self._shuffled)

        if self._shuffled:
            image = self.images.random()
        else:
            image = self.images.current

        if self._blurred:
            self.blur(image_path=image)
        else:
            self.wallpaper = image

    def next_source(self):
        self.source = self.sources + 1

    def prev_source(self):
        self.source = self.sources - 1

    def next_wallpaper(self):
        next = self.images + 1
        if self._blurred:
            return self.blur(image_path=next)
        self.wallpaper = next

    def prev_wallpaper(self):
        prev = self.images - 1
        if self._blurred:
            return self.blur(image_path=prev)
        self.wallpaper = prev

    def toggle_shuffle(self):
        if self._shuffled:
            self.images.unshuffle()
        else:
            self.images.shuffle()
        self._shuffled = not self._shuffled

    def blur(self, image_path: str = None):
        if not image_path:
            image_path = self.images.current
        long_side = max(self._screen_geometry)
        blurred_image = blur(image_path,
                             size=(long_side, long_side),
                             radius=long_side // 10,
                             save_dir=self._cache_dir,
                             use_cache=True)
        self.wallpaper = blurred_image
        self._blurred = True

    def unblur(self):
        self.wallpaper = self.images.current
        self._blurred = False

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
        print('WP:', image_path)
        windesktop.change_wallpaper(image_path, True)
