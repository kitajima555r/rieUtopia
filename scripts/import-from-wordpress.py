#!/usr/bin/env python3
"""rie-utopia.com (WordPress) から投稿を取得して posts.json を生成"""

import html
import json
import re
import time
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Optional

ROOT = Path(__file__).resolve().parent.parent
OUTPUT = ROOT / "public" / "posts.json"
SITEMAP = "http://rie-utopia.com/post-sitemap.xml"

CATEGORY_LABELS = {"poem": "詩", "diary": "日記", "life": "生きる"}


def fetch(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": "RieUtopiaImporter/1.0"})
    with urllib.request.urlopen(req, timeout=30) as res:
        return res.read().decode("utf-8", errors="replace")


def get_post_urls() -> list[str]:
    xml = fetch(SITEMAP)
    root = ET.fromstring(xml)
    ns = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    urls = [loc.text for loc in root.findall(".//sm:loc", ns)]
    return [u for u in urls if re.search(r"/\d{4}/\d{2}/\d{2}/", u)]


def map_category(categories: list[str]) -> str:
    cats = set(categories)
    if "詩" in cats:
        return "poem"
    if "日記" in cats:
        return "diary"
    if "生きる" in cats or "双極性障害" in cats:
        return "life"
    return "poem"


def parse_post(url: str) -> Optional[dict]:
    page = fetch(url)

    title_m = re.search(r"<title>([^<|]+)", page)
    if not title_m:
        return None
    title = html.unescape(title_m.group(1).strip())

    date_m = re.search(r"/(\d{4})/(\d{2})/(\d{2})/", url)
    date = f"{date_m.group(1)}-{date_m.group(2)}-{date_m.group(3)}" if date_m else ""

    categories = re.findall(r'rel="category tag">([^<]+)<', page)
    category = map_category(categories)

    image_m = re.search(r'property="og:image" content="([^"]+)"', page)
    image = image_m.group(1) if image_m else ""

    content_start = page.find("entry-content")
    lines = []
    if content_start >= 0:
        content_end = page.find("entry-footer", content_start)
        if content_end == -1:
            content_end = page.find("</article>", content_start)
        chunk = page[content_start:content_end] if content_end > content_start else page[content_start:]
        for p in re.findall(r"<p[^>]*>(.*?)</p>", chunk, re.S):
            text = html.unescape(re.sub(r"<[^>]+>", "", p)).strip()
            if not text:
                lines.append("")
                continue
            if any(x in text for x in ("Instagram", "twitter.com", "pic.twitter", "シェア")):
                continue
            if text.startswith("http"):
                continue
            lines.append(text)

    if not lines:
        return None

    return {
        "title": title,
        "date": date,
        "category": category,
        "categoryLabel": CATEGORY_LABELS[category],
        "image": image,
        "lines": lines,
    }


def main():
    urls = get_post_urls()
    print(f"取得対象: {len(urls)} 件\n")

    posts = []
    for i, url in enumerate(urls, 1):
        try:
            post = parse_post(url)
            if post:
                posts.append(post)
                print(f"[{i}/{len(urls)}] OK: {post['title']}")
            else:
                print(f"[{i}/{len(urls)}] SKIP: {url}")
        except Exception as e:
            print(f"[{i}/{len(urls)}] ERR: {url} ({e})")
        time.sleep(0.3)

    posts.sort(key=lambda p: (p["date"], p["title"]), reverse=True)
    for idx, post in enumerate(posts, 1):
        post["id"] = idx

    OUTPUT.write_text(json.dumps(posts, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"\n✅ {len(posts)} 件を {OUTPUT} に保存しました")


if __name__ == "__main__":
    main()
