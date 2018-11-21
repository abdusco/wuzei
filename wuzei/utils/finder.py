import pathlib
import typing


def find_images(directory: str,
                extensions: list = None) -> typing.List[str]:
    if not extensions:
        extensions = ['.jpg', '.jpeg', '.png']
    source_dir = pathlib.Path(directory)
    return list(str(im)
                for im in source_dir.iterdir()
                if any(im.suffix == ext for ext in extensions))
