#!/usr/bin/env python3
"""
Tests that process_image produces correct output for every device supported
by the TRMNL /api/models endpoint.

Run with: python -m pytest test_devices.py -v
"""

import io
import builtins
import pathlib
import pytest
from PIL import Image
from unittest.mock import patch, MagicMock
from app import ImageUploader, BWRY_PALETTE


# All devices from GET https://trmnl.com/api/models
DEVICE_MODELS = [
    {"name": "v2",                               "width": 1872, "height": 1404, "bit_depth": 4,  "colors": 16,       "mime_type": "image/png"},
    {"name": "og_png",                           "width": 800,  "height": 480,  "bit_depth": 1,  "colors": 2,        "mime_type": "image/png"},
    {"name": "amazon_kindle_2024",               "width": 1400, "height": 840,  "bit_depth": 8,  "colors": 256,      "mime_type": "image/png"},
    {"name": "amazon_kindle_paperwhite_6th_gen", "width": 1024, "height": 768,  "bit_depth": 8,  "colors": 256,      "mime_type": "image/png"},
    {"name": "amazon_kindle_paperwhite_7th_gen", "width": 1448, "height": 1072, "bit_depth": 8,  "colors": 256,      "mime_type": "image/png"},
    {"name": "inkplate_10",                      "width": 1200, "height": 825,  "bit_depth": 3,  "colors": 8,        "mime_type": "image/png"},
    {"name": "amazon_kindle_7",                  "width": 800,  "height": 600,  "bit_depth": 8,  "colors": 256,      "mime_type": "image/png"},
    {"name": "inky_impression_7_3",              "width": 800,  "height": 480,  "bit_depth": 1,  "colors": 2,        "mime_type": "image/png"},
    {"name": "kobo_libra_2",                     "width": 1680, "height": 1264, "bit_depth": 8,  "colors": 256,      "mime_type": "image/png"},
    {"name": "amazon_kindle_oasis_2",            "width": 1680, "height": 1264, "bit_depth": 8,  "colors": 256,      "mime_type": "image/png"},
    {"name": "og_plus",                          "width": 800,  "height": 480,  "bit_depth": 2,  "colors": 4,        "mime_type": "image/png"},
    {"name": "kobo_aura_one",                    "width": 1872, "height": 1404, "bit_depth": 8,  "colors": 256,      "mime_type": "image/png"},
    {"name": "kobo_aura_hd",                     "width": 1440, "height": 1080, "bit_depth": 4,  "colors": 16,       "mime_type": "image/png"},
    {"name": "inky_impression_13_3",             "width": 1600, "height": 1200, "bit_depth": 1,  "colors": 2,        "mime_type": "image/png"},
    {"name": "m5_paper_s3",                      "width": 960,  "height": 540,  "bit_depth": 4,  "colors": 16,       "mime_type": "image/png"},
    {"name": "amazon_kindle_scribe",             "width": 2480, "height": 1860, "bit_depth": 8,  "colors": 256,      "mime_type": "image/png"},
    {"name": "seeed_e1001",                      "width": 800,  "height": 480,  "bit_depth": 2,  "colors": 4,        "mime_type": "image/png"},
    {"name": "seeed_e1002",                      "width": 800,  "height": 480,  "bit_depth": 2,  "colors": 4,        "mime_type": "image/png"},
    {"name": "waveshare_4_26",                   "width": 800,  "height": 480,  "bit_depth": 2,  "colors": 4,        "mime_type": "image/png"},
    {"name": "waveshare_7_5_bw",                 "width": 800,  "height": 480,  "bit_depth": 1,  "colors": 2,        "mime_type": "image/png"},
    {"name": "tidbyt",                           "width": 64,   "height": 32,   "bit_depth": 24, "colors": 16777216, "mime_type": "image/webp"},
    {"name": "generic_16_9",                     "width": 1920, "height": 1080, "bit_depth": 8,  "colors": 256,      "mime_type": "image/png"},
    {"name": "palma",                            "width": 1648, "height": 824,  "bit_depth": 8,  "colors": 256,      "mime_type": "image/png"},
    {"name": "onyx_boox_go_7",                   "width": 1880, "height": 1264, "bit_depth": 4,  "colors": 16,       "mime_type": "image/png"},
    {"name": "kobo_glo",                         "width": 1024, "height": 768,  "bit_depth": 4,  "colors": 16,       "mime_type": "image/png"},
    {"name": "waveshare_7_5_bwr",                "width": 800,  "height": 480,  "bit_depth": 1,  "colors": 2,        "mime_type": "image/png"},
    {"name": "waveshare_7_5_bwry",               "width": 800,  "height": 480,  "bit_depth": 1,  "colors": 2,        "mime_type": "image/png"},
    {"name": "onxy_boox_nova_air_c",             "width": 1872, "height": 1404, "bit_depth": 12, "colors": 4096,     "mime_type": "image/png"},
    {"name": "xteink_x4",                        "width": 800,  "height": 480,  "bit_depth": 2,  "colors": 4,        "mime_type": "image/png"},
    {"name": "nook_simple_touch",                "width": 800,  "height": 600,  "bit_depth": 8,  "colors": 256,      "mime_type": "image/png"},
    {"name": "kobo_sage",                        "width": 1920, "height": 1440, "bit_depth": 4,  "colors": 16,       "mime_type": "image/png"},
    {"name": "og_bwry",                          "width": 800,  "height": 480,  "bit_depth": 1,  "colors": 2,        "mime_type": "image/png"},
    {"name": "amazon_kindle_voyage",             "width": 1448, "height": 1072, "bit_depth": 8,  "colors": 256,      "mime_type": "image/png"},
    {"name": "inkplate_5_2",                     "width": 1280, "height": 720,  "bit_depth": 4,  "colors": 16,       "mime_type": "image/png"},
    {"name": "raspberry_pi_touch_2",             "width": 1280, "height": 720,  "bit_depth": 24, "colors": 16777216, "mime_type": "image/png"},
    {"name": "ed133ut2",                         "width": 1600, "height": 1200, "bit_depth": 4,  "colors": 16,       "mime_type": "image/png"},
    {"name": "avalue_epd_42s",                   "width": 2880, "height": 2160, "bit_depth": 4,  "colors": 16,       "mime_type": "image/png"},
    {"name": "kobo_touch",                       "width": 800,  "height": 600,  "bit_depth": 4,  "colors": 16,       "mime_type": "image/png"},
    {"name": "kobo_forma",                       "width": 1920, "height": 1440, "bit_depth": 4,  "colors": 16,       "mime_type": "image/png"},
    {"name": "openframe",                        "width": 800,  "height": 480,  "bit_depth": 24, "colors": 16777216, "mime_type": "image/webp"},
    {"name": "amazon_kindle_paperwhite_signature_11th_gen", "width": 1648, "height": 1236, "bit_depth": 4, "colors": 16, "mime_type": "image/png"},
]

_real_open = builtins.open


def _open_no_data(path, mode="r", *args, **kwargs):
    """Redirect /data/ writes to a throwaway BytesIO sink."""
    if str(path).startswith("/data"):
        return _real_open("/dev/null", "wb")
    return _real_open(path, mode, *args, **kwargs)


def make_uploader(model: dict) -> ImageUploader:
    return ImageUploader(
        webhook_url="http://fake",
        images_dir="/tmp",
        interval_minutes=60,
        display_width=model["width"],
        display_height=model["height"],
        bit_depth=model["bit_depth"],
        mime_type=model["mime_type"],
    )


def make_test_image_file(tmp_path, width=200, height=200) -> pathlib.Path:
    img = Image.new("RGB", (width, height))
    pixels = img.load()
    for y in range(height):
        for x in range(width):
            v = int(x * 255 / width)
            pixels[x, y] = (v, v, v)
    path = tmp_path / "test.jpg"
    img.save(path, format="JPEG")
    return path


def process(model, tmp_path):
    uploader = make_uploader(model)
    img_path = make_test_image_file(tmp_path)
    with patch("builtins.open", side_effect=_open_no_data), \
         patch("pathlib.Path.glob", return_value=[]):
        return uploader.process_image(img_path)


@pytest.mark.parametrize("model", DEVICE_MODELS, ids=[m["name"] for m in DEVICE_MODELS])
def test_mime_type(model, tmp_path):
    _, content_type = process(model, tmp_path)
    assert content_type == model["mime_type"]


@pytest.mark.parametrize("model", DEVICE_MODELS, ids=[m["name"] for m in DEVICE_MODELS])
def test_dimensions(model, tmp_path):
    image_bytes, content_type = process(model, tmp_path)
    result = Image.open(io.BytesIO(image_bytes))
    assert result.size == (model["width"], model["height"])


BWRY_MODELS = [m for m in DEVICE_MODELS if "bwry" in m["name"]]


def make_bwry_uploader(model: dict) -> ImageUploader:
    return ImageUploader(
        webhook_url="http://fake",
        images_dir="/tmp",
        interval_minutes=60,
        display_width=model["width"],
        display_height=model["height"],
        bit_depth=model["bit_depth"],
        mime_type=model["mime_type"],
        output_mode="bwry",
    )


def make_color_test_image(tmp_path) -> pathlib.Path:
    """Colorful test image with red, yellow, black, white, and blended regions."""
    img = Image.new("RGB", (200, 200))
    pixels = img.load()
    for y in range(200):
        for x in range(200):
            if x < 50:
                pixels[x, y] = (255, 0, 0)      # red
            elif x < 100:
                pixels[x, y] = (255, 255, 0)    # yellow
            elif x < 150:
                pixels[x, y] = (0, 0, 0)        # black
            else:
                pixels[x, y] = (255, 255, 255)  # white
    path = tmp_path / "color_test.png"
    img.save(path, format="PNG")
    return path


@pytest.mark.parametrize("model", BWRY_MODELS, ids=[m["name"] for m in BWRY_MODELS])
def test_bwry_is_palette_png(model, tmp_path):
    uploader = make_bwry_uploader(model)
    img_path = make_color_test_image(tmp_path)
    with patch("builtins.open", side_effect=_open_no_data), \
         patch("pathlib.Path.glob", return_value=[]):
        image_bytes, content_type = uploader.process_image(img_path)
    result = Image.open(io.BytesIO(image_bytes))
    assert content_type == "image/png"
    assert result.mode == "P"
    assert result.size == (model["width"], model["height"])


@pytest.mark.parametrize("model", BWRY_MODELS, ids=[m["name"] for m in BWRY_MODELS])
def test_bwry_only_palette_colors(model, tmp_path):
    uploader = make_bwry_uploader(model)
    img_path = make_color_test_image(tmp_path)
    with patch("builtins.open", side_effect=_open_no_data), \
         patch("pathlib.Path.glob", return_value=[]):
        image_bytes, _ = uploader.process_image(img_path)
    result = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    used_colors = set(result.get_flattened_data())
    allowed = set(BWRY_PALETTE)
    assert used_colors <= allowed, f"Unexpected colors: {used_colors - allowed}"
