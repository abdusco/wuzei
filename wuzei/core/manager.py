import pathlib
import typing
import tempfile
from wuzei.utils import activedesktop as ad
from wuzei.utils.finder import find_images
from .dispenser import Dispenser
from .blur import blur


class WallpaperManager:
    def __init__(self, paths: typing.List[str],
                 cache_dir: str = None):
        if not paths:
            raise ValueError('Specify at least one path')
        if not cache_dir:
            cache_dir = tempfile.gettempdir()

        self._cache_dir = cache_dir
        self._wallpaper: str = None
        self._source: str = None
        self._shuffled = True
        self._blurred = True
        self._screen_geometry = ad.get_screen_size()

        self.paths = Dispenser(paths)
        self.source = self.paths.current

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
        if self._blurred:
            self.blur(image_path=self.images.current)
        else:
            self.wallpaper = self.images.current

    def next_source(self):
        self.source = self.paths + 1

    def prev_source(self):
        self.source = self.paths - 1

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
            self.images.shuffle()
        else:
            self.images.unshuffle()
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
        ad.change_wallpaper(image_path, True)