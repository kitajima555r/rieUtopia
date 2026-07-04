#!/usr/bin/env python3
"""
ロゴ(public/images/rie-utopia-logo.png)の「R」の字を切り出して
favicon一式を生成する。

使い方: python3 scripts/make_favicon.py
"""

from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
IMAGES = ROOT / "public" / "images"
LOGO = IMAGES / "rie-utopia-logo.png"

# ロゴ画像の左端、"R" の字だけを含む範囲（実測で調整済み）
CROP_BOX = (0, 0, 195, 271)


def square_canvas(im):
    size = max(im.size)
    canvas = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    offset = ((size - im.width) // 2, (size - im.height) // 2)
    canvas.paste(im, offset, im)
    return canvas


def main():
    with Image.open(LOGO) as logo:
        r_mark = logo.crop(CROP_BOX)
        r_mark = square_canvas(r_mark)

    sizes = [16, 32, 48, 180]
    resized = {size: r_mark.resize((size, size), Image.LANCZOS) for size in sizes}

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
