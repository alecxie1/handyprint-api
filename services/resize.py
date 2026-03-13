import os
from PIL import Image
from config import FORMATS, GENERATED_DIR


def resize_to_canvas(src_path: str, format_key: str) -> str:
    """
    Resize/crop image to exact target canvas dimensions.
    Strategy: scale to fill (cover), then center-crop. No distortion.
    Returns path to the resized image.
    """
    fmt = FORMATS[format_key]
    target_w = fmt["width"]
    target_h = fmt["height"]

    img = Image.open(src_path).convert("RGBA")
    src_w, src_h = img.size

    # Scale to fill: find the scale that makes the image cover the target
    scale = max(target_w / src_w, target_h / src_h)
    new_w = int(src_w * scale)
    new_h = int(src_h * scale)

    img = img.resize((new_w, new_h), Image.LANCZOS)

    # Center crop to exact target dimensions
    left = (new_w - target_w) // 2
    top = (new_h - target_h) // 2
    img = img.crop((left, top, left + target_w, top + target_h))

    # Save as PNG (high quality, lossless)
    base = os.path.splitext(os.path.basename(src_path))[0]
    out_filename = base.replace("_raw", "_final") + ".png"
    out_path = os.path.join(GENERATED_DIR, out_filename)
    img.save(out_path, "PNG", optimize=False)

    return out_path


def resize_all(raw_paths: list[str], format_key: str) -> list[str]:
    """Resize a list of raw generated images to canvas dimensions."""
    return [resize_to_canvas(p, format_key) for p in raw_paths]
