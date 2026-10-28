#!/usr/bin/env python3
"""
ロゴ原本(design/logo-source.png)から「R」と星のきらめきを切り出し、
青グラデーション(#3366ff→#0080ff)の上に白抜きで乗せたfavicon一式を生成する。

使い方: python3 scripts/make_favicon.py
"""

from pathlib import Path
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parent.parent
IMAGES = ROOT / "public" / "images"
LOGO_SOURCE = ROOT / "design" / "logo-source.png"

# 原本(2171x724)上で "R" と星だけを残す範囲（"i" の縦線や後続の文字を除く）
KEEP_BOXES = [(20, 100, 400, 520), (375, 100, 570, 285)]
CROP_BOX = (20, 100, 570, 520)

MASTER_SIZE = 1024
CORNER_RADIUS_RATIO = 0.22
MARK_RATIO = 0.64
GRADIENT_START = (51, 102, 255)  # #3366ff
GRADIENT_END = (0, 128, 255)  # #0080ff


def white_mark():
    src = Image.open(LOGO_SOURCE).convert("RGBA")
    alpha = src.getchannel("A")
    keep = Image.new("L", src.size, 0)
    draw = ImageDraw.Draw(keep)
    for box in KEEP_BOXES:
        draw.rectangle(box, fill=255)
    masked = Image.composite(alpha, Image.new("L", src.size, 0), keep)
    mark = Image.new("RGBA", src.size, (255, 255, 255, 255))
    mark.putalpha(masked)
    mark = mark.crop(CROP_BOX)
    return mark.crop(mark.getchannel("A").getbbox())


def gradient(size):
    bg = Image.new("RGB", (size, size))
    px = bg.load()
    for y in range(size):
        for x in range(size):
            t = (x + y) / (2 * (size - 1))
            px[x, y] = tuple(
                round(GRADIENT_START[i] + (GRADIENT_END[i] - GRADIENT_START[i]) * t)
                for i in range(3)
            )
    return bg.convert("RGBA")


def build_base(size):
    base = gradient(size)
    mark = white_mark()
    scale = MARK_RATIO * size / max(mark.size)
    mark = mark.resize((round(mark.width * scale), round(mark.height * scale)), Image.LANCZOS)
    base.alpha_composite(mark, ((size - mark.width) // 2, (size - mark.height) // 2))
    return base


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
        rounded_icon.resize((size, size), Image.LANCZOS).save(IMAGES / f"favicon-{size}.png")

    rounded_icon.resize((48, 48), Image.LANCZOS).save(
        ROOT / "public" / "favicon.ico", format="ICO", sizes=[(16, 16), (32, 32), (48, 48)]
    )

    # apple-touch-icon: iOS側が角丸を付けるのでフチなし正方形・不透明で渡す
    base.resize((180, 180), Image.LANCZOS).convert("RGB").save(IMAGES / "apple-touch-icon.png")

    print("生成: favicon.ico, favicon-16/32.png, apple-touch-icon.png")


if __name__ == "__main__":
    main()
