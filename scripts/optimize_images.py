#!/usr/bin/env python3
"""
public/images 内の写真（wp/ の投稿写真、eyecatch-*.jpg、about-profile.jpg）を
表示に十分なサイズへリサイズ・再圧縮する。ロゴ(png)や sky-bg.png は対象外。

事前にリポジトリ外へバックアップ済み（../rieu-topia-images-backup.tar.gz）。

使い方:
  python3 scripts/optimize_images.py
"""

from pathlib import Path
from PIL import Image, ImageOps

ROOT = Path(__file__).resolve().parent.parent
IMAGES = ROOT / "public" / "images"

MAX_DIMENSION = 1600
JPEG_QUALITY = 82

TARGETS = [
    *IMAGES.glob("wp/*.jpg"),
    *IMAGES.glob("eyecatch-*.jpg"),
    IMAGES / "about-profile.jpg",
]


def optimize(path: Path):
    if not path.exists():
        return None

    before = path.stat().st_size
    with Image.open(path) as im:
        im = ImageOps.exif_transpose(im)  # apply rotation before dropping EXIF
        im = im.convert("RGB")
        im.thumbnail((MAX_DIMENSION, MAX_DIMENSION), Image.LANCZOS)
        im.save(path, "JPEG", quality=JPEG_QUALITY, optimize=True, progressive=True)

    after = path.stat().st_size
    return before, after


def main():
    total_before = 0
    total_after = 0
    for path in TARGETS:
        result = optimize(path)
        if result is None:
            continue
        before, after = result
        total_before += before
        total_after += after
        print(f"{path.relative_to(ROOT)}: {before // 1024}KB -> {after // 1024}KB")

    print(
        f"\n合計: {total_before / 1024 / 1024:.1f}MB -> {total_after / 1024 / 1024:.1f}MB"
    )


if __name__ == "__main__":
    main()
