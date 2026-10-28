#!/usr/bin/env python3
"""
ロゴマーク原本(design/mark-source.webp)から背景(チェッカー柄)を除去し、
favicon一式を生成する。

原本のチェッカー柄は画像に焼き込まれた灰/白で、マーク本体は彩度が高い青なので、
彩度をもとに透明度を作る。マーク内の白いハイライトが抜けないよう、小さな隙間は埋める。

使い方: python3 scripts/make_favicon.py   (Pillow と numpy が必要)
"""

from pathlib import Path

import numpy as np
from PIL import Image, ImageFilter

ROOT = Path(__file__).resolve().parent.parent
IMAGES = ROOT / "public" / "images"
MARK_SOURCE = ROOT / "design" / "mark-source.webp"

SAT_LOW, SAT_HIGH = 12, 45  # この範囲で透明→不透明へ
CLOSE_SIZE = 9  # 閉じる処理のカーネル(奇数)。ハイライトの細い隙間を埋める
MASTER_SIZE = 1024


def remove_background(src):
    rgb = np.asarray(src.convert("RGB")).astype(float)
    sat = rgb.max(2) - rgb.min(2)
    alpha = np.clip((sat - SAT_LOW) / (SAT_HIGH - SAT_LOW), 0, 1)

    # 閉じる処理(膨張→収縮)で、マーク内部の細い白ハイライトを不透明に戻す
    mask = Image.fromarray((alpha * 255).astype(np.uint8))
    closed = mask.filter(ImageFilter.MaxFilter(CLOSE_SIZE)).filter(ImageFilter.MinFilter(CLOSE_SIZE))
    alpha = np.maximum(alpha, np.asarray(closed) / 255)

    out = np.dstack([rgb, alpha * 255]).astype(np.uint8)
    return Image.fromarray(out)


def place(mark, size, fill, background=None):
    canvas = Image.new("RGBA", (size, size), background or (0, 0, 0, 0))
    scale = fill * size / max(mark.size)
    resized = mark.resize((round(mark.width * scale), round(mark.height * scale)), Image.LANCZOS)
    canvas.alpha_composite(resized, ((size - resized.width) // 2, (size - resized.height) // 2))
    return canvas


def main():
    mark = remove_background(Image.open(MARK_SOURCE))
    mark = mark.crop(mark.getchannel("A").getbbox())

    favicon = place(mark, MASTER_SIZE, fill=0.94)
    for size in (16, 32):
        favicon.resize((size, size), Image.LANCZOS).save(IMAGES / f"favicon-{size}.png")
    favicon.resize((48, 48), Image.LANCZOS).save(
        ROOT / "public" / "favicon.ico", format="ICO", sizes=[(16, 16), (32, 32), (48, 48)]
    )

    # apple-touch-icon: iOSは透過を黒で塗るので白背景の不透明画像にする
    apple = place(mark, MASTER_SIZE, fill=0.74, background=(255, 255, 255, 255))
    apple.resize((180, 180), Image.LANCZOS).convert("RGB").save(IMAGES / "apple-touch-icon.png")

    print("生成: favicon.ico, favicon-16/32.png, apple-touch-icon.png")


if __name__ == "__main__":
    main()
