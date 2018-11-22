from pathlib import Path

from PIL import Image
from PIL.ImageFilter import GaussianBlur


def blur(image_path: str, size: tuple, radius=200, save_dir: str = None, use_cache=True) -> Path:
    image = Path(image_path)
    save_path = image.with_suffix('.blurred.jpg')

    # skip PNGs
    if image.suffix == '.png':
        return image

    if save_dir:
        save_path = Path(save_dir) / (save_path.stem + save_path.suffix)

    if use_cache and save_path.exists():
        return save_path

    with Image.open(image) as img, \
            open(save_path, mode='w') as destination:
        img.thumbnail(size, resample=Image.NEAREST)
        blurred = img.filter(GaussianBlur(radius=radius))
        blurred.save(destination, 'JPEG')
        return save_path
