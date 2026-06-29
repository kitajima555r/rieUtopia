#!/usr/bin/env python3
"""WordPress の画像 URL を public/images/wp/ にダウンロードして posts.json を更新"""

import hashlib
import json
import re
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
POSTS_FILE = ROOT / "public" / "posts.json"
IMAGES_DIR = ROOT / "public" / "images" / "wp"


def download(url: str) -> str:
    ext = Path(re.sub(r"\?.*", "", url)).suffix or ".jpg"
    filename = hashlib.md5(url.encode()).hexdigest()[:12] + ext
    dest = IMAGES_DIR / filename
    if dest.exists():
        return f"images/wp/{filename}"

    req = urllib.request.Request(url, headers={"User-Agent": "RieUtopiaImporter/1.0"})
    with urllib.request.urlopen(req, timeout=30) as res:
        dest.write_bytes(res.read())
    return f"images/wp/{filename}"


def main():
    posts = json.loads(POSTS_FILE.read_text(encoding="utf-8"))
    IMAGES_DIR.mkdir(parents=True, exist_ok=True)
    cache = {}

    for post in posts:
        url = post.get("image", "")
        if not url or url.startswith("images/"):
            continue
        if url not in cache:
            try:
                cache[url] = download(url)
                print(f"OK: {post['title'][:20]} → {cache[url]}")
            except Exception as e:
                print(f"SKIP: {url} ({e})")
                cache[url] = ""
        if cache[url]:
            post["image"] = cache[url]

    POSTS_FILE.write_text(json.dumps(posts, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"\n✅ {len(cache)} 画像を処理しました")


if __name__ == "__main__":
    main()
