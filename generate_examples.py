#!/usr/bin/env python3
"""Generate example processed images for every TRMNL device model."""

import io
import pathlib
import sys
import tempfile
import builtins
import requests
from PIL import Image, ImageDraw
from app import ImageUploader, BWRY_PALETTE

TRMNL_MODELS_URL = "https://trmnl.com/api/models"
OUTPUT_DIR = pathlib.Path("example_images")

_real_open = builtins.open


def _open_no_data(path, mode="r", *args, **kwargs):
    if str(path).startswith("/data"):
        return _real_open("/dev/null", "wb")
    return _real_open(path, mode, *args, **kwargs)


def fetch_models():
    resp = requests.get(TRMNL_MODELS_URL, headers={"accept": "application/json"}, timeout=10)
    resp.raise_for_status()
    return resp.json()["data"]


def make_demo_image() -> Image.Image:
    """Colorful synthetic image: gradient background + color blocks + grayscale ramp."""
    w, h = 800, 480
    img = Image.new("RGB", (w, h))
    pixels = img.load()

    for y in range(h):
        for x in range(w):
            pixels[x, y] = (int(x * 255 / w), int(y * 255 / h), 128)

    draw = ImageDraw.Draw(img)
    block_w = w // 8
    block_h = h // 5
    colors = [(255,0,0),(255,128,0),(255,255,0),(0,200,0),(0,128,255),(0,0,255),(128,0,255),(255,0,128)]
    for i, color in enumerate(colors):
        draw.rectangle([i * block_w, 0, (i + 1) * block_w, block_h], fill=color)

    ramp_y = h - block_h
    for x in range(w):
        v = int(x * 255 / w)
        draw.line([(x, ramp_y), (x, h)], fill=(v, v, v))

    return img


def output_mode_for(model: dict) -> str:
    if model["bit_depth"] == 24:
        return "color"
    if "bwry" in model["name"]:
        return "bwry"
    return "grayscale"


def main():
    source_arg = sys.argv[1] if len(sys.argv) > 1 else None

    OUTPUT_DIR.mkdir(exist_ok=True)

    print("Fetching device models...")
    models = fetch_models()
    print(f"Found {len(models)} models\n")

    if source_arg:
        source_path = pathlib.Path(source_arg)
        tmp_file = None
    else:
        demo = make_demo_image()
        tmp = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
        demo.save(tmp, format="PNG")
        tmp.close()
        source_path = pathlib.Path(tmp.name)
        tmp_file = source_path

    try:
        for model in models:
            name = model["name"]
            mode = output_mode_for(model)
            ext = "webp" if model["mime_type"] == "image/webp" else "png"

            uploader = ImageUploader(
                webhook_url="http://fake",
                images_dir="/tmp",
                interval_minutes=60,
                display_width=model["width"],
                display_height=model["height"],
                bit_depth=model["bit_depth"],
                mime_type=model["mime_type"],
                output_mode=mode,
            )

            import unittest.mock as mock
            with mock.patch("builtins.open", side_effect=_open_no_data), \
                 mock.patch("pathlib.Path.glob", return_value=[]):
                image_bytes, _ = uploader.process_image(source_path)

            out_path = OUTPUT_DIR / f"{name}.{ext}"
            out_path.write_bytes(image_bytes)
            print(f"  {name:<50} {model['width']}x{model['height']} {mode}")
    finally:
        if tmp_file:
            tmp_file.unlink(missing_ok=True)

    print(f"\nWrote {len(models)} images to {OUTPUT_DIR}/")


if __name__ == "__main__":
    main()
