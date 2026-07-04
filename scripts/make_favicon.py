#!/usr/bin/env python3
"""
sky-bg.png（トップのヒーロー画像と同じ空の写真）を背景に、
白抜きの"R"を乗せたfaviconを生成する。

使い方: python3 scripts/make_favicon.py
"""

from pathlib import Path
from PIL import Image, ImageDraw, ImageEnhance

ROOT = Path(__file__).resolve().parent.parent
IMAGES = ROOT / "public" / "images"
SKY_PHOTO = IMAGES / "sky-bg.png"
LOGO = IMAGES / "rie-utopia-logo.png"

MASTER_SIZE = 1024
# sky-bg.png(768x1024)から正方形として切り出す範囲
SKY_CROP_BOX = (0, 250, 768, 1018)
# ロゴ画像の左端、"R" の字だけを含む範囲（実測で調整済み）
LOGO_R_CROP_BOX = (0, 0, 195, 271)
CORNER_RADIUS_RATIO = 0.22
LETTER_HEIGHT_RATIO = 0.62
SATURATION_FACTOR = 3.0


def white_r_mark():
    with Image.open(LOGO) as logo:
        r_mark = logo.crop(LOGO_R_CROP_BOX)
    alpha = r_mark.getchannel("A")
    white = Image.new("RGBA", r_mark.size, (255, 255, 255, 255))
    white.putalpha(alpha)
    return white


def build_base(size):
    sky = Image.open(SKY_PHOTO).convert("RGB")
    crop = sky.crop(SKY_CROP_BOX).resize((size, size), Image.LANCZOS)
    crop = ImageEnhance.Color(crop).enhance(SATURATION_FACTOR).convert("RGBA")

    r_mark = white_r_mark()
    target_h = int(size * LETTER_HEIGHT_RATIO)
    scale = target_h / r_mark.height
    target_w = int(r_mark.width * scale)
    r_mark = r_mark.resize((target_w, target_h), Image.LANCZOS)

    offset = ((size - target_w) // 2, (size - target_h) // 2)
    crop.alpha_composite(r_mark, offset)
    return crop


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
