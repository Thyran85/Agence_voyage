from functools import lru_cache
from pathlib import Path
from tkinter import PhotoImage

try:
    from PIL import Image, ImageTk
except ImportError:
    Image = None
    ImageTk = None


DESTINATION_PALETTES = {
    "paris": ("#20343f", "#82d3de", "#ffb59a"),
    "rome": ("#39251f", "#ffb59a", "#e0c0b5"),
    "barcelone": ("#16343a", "#82d3de", "#ffdbce"),
    "marrakech": ("#3a2418", "#ffb59a", "#765d54"),
    "florence": ("#2f261d", "#e0c0b5", "#ffb59a"),
    "santorin": ("#18323f", "#82d3de", "#e5e2e1"),
    "kyoto": ("#2e1d24", "#ffb59a", "#82d3de"),
}


def _hex_to_rgb(color):
    color = color.lstrip("#")
    return tuple(int(color[index : index + 2], 16) for index in (0, 2, 4))


def _rgb_to_hex(rgb):
    return "#%02x%02x%02x" % rgb


def _blend(start, end, ratio):
    return tuple(int(start[i] + (end[i] - start[i]) * ratio) for i in range(3))


@lru_cache(maxsize=128)
def destination_image(key, image_path=None, size=(128, 72)):
    if image_path:
        image = _load_file_image(image_path, size)
        if image:
            return image
    key = (key or "").lower()
    base, accent, warm = DESTINATION_PALETTES.get(key, ("#1c1b1b", "#82d3de", "#ffb59a"))
    return _travel_image(size, base, accent, warm)


@lru_cache(maxsize=16)
def hero_image(kind, size=(560, 220)):
    if kind == "safari":
        return _travel_image(size, "#2b1f18", "#ffb59a", "#765d54", sun=True)
    return _travel_image(size, "#0e3036", "#82d3de", "#ffb59a", water=True)


def _travel_image(size, base, accent, warm, sun=False, water=False):
    width, height = size
    image = PhotoImage(width=width, height=height)
    start = _hex_to_rgb(base)
    end = _hex_to_rgb(accent)

    for y in range(height):
        ratio = y / max(height - 1, 1)
        color = _rgb_to_hex(_blend(start, end, ratio * 0.45))
        image.put(color, to=(0, y, width, y + 1))

    if sun:
        _rectangle(image, int(width * 0.68), int(height * 0.16), int(width * 0.9), int(height * 0.5), warm)
    if water:
        for y in range(int(height * 0.5), height, 8):
            image.put(accent, to=(0, y, width, min(y + 2, height)))

    horizon = int(height * 0.6)
    image.put("#101010", to=(0, horizon, width, height))
    for index in range(7):
        x = int(width * (0.05 + index * 0.16))
        top = horizon - 10 - (index % 3) * 7
        _triangle(image, x, top, 46, horizon, "#080808")

    _rectangle(image, 0, 0, width, height, "#000000", every=5)
    return image


def _load_file_image(path, size):
    file_path = Path(path).expanduser()
    if not file_path.exists():
        return None
    if Image and ImageTk:
        try:
            image = Image.open(file_path)
            image.thumbnail(size)
            return ImageTk.PhotoImage(image)
        except Exception:
            return None
    try:
        image = PhotoImage(file=str(file_path))
    except Exception:
        return None
    return _fit_photo_image(image, size)


def _fit_photo_image(image, size):
    width, height = size
    if image.width() <= width and image.height() <= height:
        return image
    factor = max((image.width() + width - 1) // width, (image.height() + height - 1) // height)
    return image.subsample(max(factor, 1), max(factor, 1))


def _rectangle(image, x1, y1, x2, y2, color, every=1):
    for y in range(max(y1, 0), min(y2, image.height()), every):
        image.put(color, to=(max(x1, 0), y, min(x2, image.width()), min(y + 1, image.height())))


def _triangle(image, center_x, top_y, half_width, bottom_y, color):
    height = max(bottom_y - top_y, 1)
    for y in range(max(top_y, 0), min(bottom_y, image.height())):
        progress = (y - top_y) / height
        half = int(half_width * progress)
        image.put(color, to=(max(center_x - half, 0), y, min(center_x + half, image.width()), y + 1))
