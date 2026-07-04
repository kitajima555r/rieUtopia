#!/usr/bin/env python3
"""
ロゴ(public/images/rie-utopia-logo.png)の「R」の字を、
青空グラデーション背景の上に白抜きで乗せたfaviconを生成する。

使い方: python3 scripts/make_favicon.py
"""

from pathlib import Path
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parent.parent
IMAGES = ROOT / "public" / "images"
LOGO = IMAGES / "rie-utopia-logo.png"

# ロゴ画像の左端、"R" の字だけを含む範囲（実測で調整済み）
CROP_BOX = (0, 0, 195, 271)

MASTER_SIZE = 512
SKY_TOP = (77, 163, 255)  # 明るい空色
SKY_BOTTOM = (0, 87, 217)  # 深い青

R_PADDING_RATIO = 0.62  # マスター内でRが占める高さの割合


def sky_background(size):
    bg = Image.new("RGB", (size, size))
    draw = ImageDraw.Draw(bg)
    for y in range(size):
        t = y / (size - 1)
        color = tuple(
            int(SKY_TOP[i] + (SKY_BOTTOM[i] - SKY_TOP[i]) * t) for i in range(3)
        )
        draw.line([(0, y), (size, y)], fill=color)
    return bg


def white_r_mark():
    with Image.open(LOGO) as logo:
        r_mark = logo.crop(CROP_BOX)
    alpha = r_mark.getchannel("A")
    white = Image.new("RGBA", r_mark.size, (255, 255, 255, 255))
    white.putalpha(alpha)
    return white


def main():
    bg = sky_background(MASTER_SIZE).convert("RGBA")
    r_mark = white_r_mark()

    target_h = int(MASTER_SIZE * R_PADDING_RATIO)
    scale = target_h / r_mark.height
    target_w = int(r_mark.width * scale)
    r_mark = r_mark.resize((target_w, target_h), Image.LANCZOS)

    offset = ((MASTER_SIZE - target_w) // 2, (MASTER_SIZE - target_h) // 2)
    bg.alpha_composite(r_mark, offset)
    master = bg.convert("RGB")

    sizes = [16, 32, 48, 180]
    resized = {size: master.resize((size, size), Image.LANCZOS) for size in sizes}

    resized[32].save(IMAGES / "favicon-32.png")
    resized[16].save(IMAGES / "favicon-16.png")
    resized[180].save(IMAGES / "apple-touch-icon.png")

    ico_path = ROOT / "public" / "favicon.ico"
    resized[48].save(
        ico_path, format="ICO", sizes=[(16, 16), (32, 32), (48, 48)]
    )

    print("生成: favicon.ico, favicon-16.png, favicon-32.png, apple-touch-icon.png")


if __name__ == "__main__":
    main()
