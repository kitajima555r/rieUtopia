#!/usr/bin/env python3
"""
sky-bg.png（トップのヒーロー画像と同じ空の写真）を背景に、
白抜きの"R"を乗せたfaviconを生成する。

使い方: python3 scripts/make_favicon.py
"""

from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
IMAGES = ROOT / "public" / "images"
SKY_PHOTO = IMAGES / "sky-bg.png"
FONT_PATH = "/System/Library/Fonts/Supplemental/Georgia Bold.ttf"

MASTER_SIZE = 1024
# sky-bg.png(768x1024)から正方形として切り出す範囲
SKY_CROP_BOX = (0, 250, 768, 1018)
CORNER_RADIUS_RATIO = 0.22
LETTER_HEIGHT_RATIO = 0.62


def build_base(size):
    sky = Image.open(SKY_PHOTO).convert("RGB")
    crop = sky.crop(SKY_CROP_BOX).resize((size, size), Image.LANCZOS)

    font = ImageFont.truetype(FONT_PATH, int(size * LETTER_HEIGHT_RATIO))
    draw = ImageDraw.Draw(crop)
    bbox = draw.textbbox((0, 0), "R", font=font)
    w, h = bbox[2] - bbox[0], bbox[3] - bbox[1]
    x = size / 2 - w / 2 - bbox[0]
    y = size / 2 - h / 2 - bbox[1]
    draw.text((x, y), "R", font=font, fill=(255, 255, 255, 255))
    return crop.convert("RGBA")


def rounded(im, radius_ratio):
    size = im.size[0]
    mask = Image.new("L", (size, size), 0)
    ImageDraw.Draw(mask).rounded_rectangle(
        [0, 0, size, size], radius=int(size * radius_ratio), fill=255
    )
    out = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    out.paste(im, (0, 0), mask)
    return out


def main():
    base = build_base(MASTER_SIZE)
    rounded_icon = rounded(base, CORNER_RADIUS_RATIO)

    for size in (16, 32):
        rounded_icon.resize((size, size), Image.LANCZOS).save(
            IMAGES / f"favicon-{size}.png"
        )

    ico_path = ROOT / "public" / "favicon.ico"
    rounded_icon.resize((48, 48), Image.LANCZOS).save(
        ico_path, format="ICO", sizes=[(16, 16), (32, 32), (48, 48)]
    )

    # apple-touch-icon: iOS側が角丸・影を付けるのでフチなし正方形・不透明で渡す
    apple_icon = base.resize((180, 180), Image.LANCZOS).convert("RGB")
    apple_icon.save(IMAGES / "apple-touch-icon.png")

    print("生成: favicon.ico, favicon-16/32.png, apple-touch-icon.png")


if __name__ == "__main__":
    main()
