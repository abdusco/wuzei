from pathlib import Path

from PIL import Image
from PIL.ImageFilter import GaussianBlur


def blur(image_path: str,
         radius=200,
         size: tuple = None,
         save_dir: str = None,
         use_cache=True) -> Path:
    img_path = Path(image_path)
    # skip PNGs
    if img_path.suffix == '.png':
        return img_path

    modified = int(img_path.stat().st_mtime)
    save_path = img_path.with_suffix(f'.v{modified}.blurred.jpg')

    if save_dir:
        save_path = Path(save_dir) / save_path.name

    if use_cache and save_path.exists():
        return save_path

    with Image.open(img_path) as img, \
            open(save_path, mode='w') as destination:
        if not size:
            size = max(img.size)
        img.thumbnail(size, resample=Image.NEAREST)
        blurred = img.filter(GaussianBlur(radius=radius))
        blurred.save(destination, 'JPEG')
        return save_path
