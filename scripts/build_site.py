#!/usr/bin/env python3
"""
詩ごとの静的ページ (public/posts/{id}.html) と
public/sitemap.xml / public/feed.xml を生成するビルドスクリプト。

Node不要・標準ライブラリのみ。microCMS が未設定/取得失敗のときは
public/posts.json をフォールバックとして使う（サイト本体と同じ挙動）。

使い方:
  python3 scripts/build_site.py
  MICROCMS_SERVICE_DOMAIN=xxx MICROCMS_API_KEY=xxx python3 scripts/build_site.py
"""

import html
import json
import os
import urllib.request
from datetime import datetime, timezone
from email.utils import format_datetime
from pathlib import Path
from urllib.error import URLError

ROOT = Path(__file__).resolve().parent.parent
PUBLIC = ROOT / "public"
SITE_URL = "https://rie-utopia.com"

CATEGORY_LABELS = {"poem": "詩", "diary": "日記", "life": "生きる"}
CATEGORY_ALIASES = {"詩": "poem", "日記": "diary", "生きる": "life"}

GTAG_SNIPPET = """<!-- Google tag (gtag.js) -->
  <script async src="https://www.googletagmanager.com/gtag/js?id=G-0W215WX6JL"></script>
  <script>
    window.dataLayer = window.dataLayer || [];
    function gtag(){dataLayer.push(arguments);}
    gtag('js', new Date());
    gtag('config', 'G-0W215WX6JL');
  </script>"""


def normalize_category(category):
    raw = category[0] if isinstance(category, list) else category
    if not raw:
        return "poem"
    return CATEGORY_ALIASES.get(raw, raw)


def normalize_image(item):
    image = item.get("image")
    if isinstance(image, str) and image:
        return image
    eyecatch = item.get("eyecatch")
    if isinstance(eyecatch, dict) and eyecatch.get("url"):
        return eyecatch["url"]
    if isinstance(eyecatch, str):
        return eyecatch
    return ""


def normalize_post(item):
    category = normalize_category(item.get("category"))
    lines = item.get("lines") or (item.get("body") or "").split("\n")
    date = str(item.get("date") or "")[:10]

    return {
        "id": str(item.get("id")),
        "title": item.get("title") or "",
        "date": date,
        "category": category,
        "categoryLabel": CATEGORY_LABELS.get(category, category),
        "image": normalize_image(item),
        "lines": [line for line in lines],
    }


def fetch_from_microcms():
    service_domain = os.environ.get("MICROCMS_SERVICE_DOMAIN")
    api_key = os.environ.get("MICROCMS_API_KEY")
    if not service_domain or not api_key:
        return []

    base = f"https://{service_domain}.microcms.io/api/v1/posts"
    limit = 100
    offset = 0
    contents = []

    try:
        while True:
            url = f"{base}?orders=-date&limit={limit}&offset={offset}"
            req = urllib.request.Request(url, headers={"X-MICROCMS-API-KEY": api_key})
            with urllib.request.urlopen(req, timeout=15) as res:
                data = json.loads(res.read().decode("utf-8"))

            page = data.get("contents") or []
            contents.extend(page)
            offset += limit
            if offset >= data.get("totalCount", 0) or len(page) < limit:
                break
    except (URLError, OSError, ValueError) as err:
        print(f"microCMS 取得をスキップ（フォールバックを使用）: {err}")
        return []

    return [normalize_post(item) for item in contents]


def fetch_from_fallback():
    posts_json = PUBLIC / "posts.json"
    if not posts_json.exists():
        return []
    items = json.loads(posts_json.read_text(encoding="utf-8"))
    return [normalize_post(item) for item in items]


def load_posts():
    microcms_posts = fetch_from_microcms()
    fallback_posts = fetch_from_fallback()

    if microcms_posts and fallback_posts:
        titles = {p["title"] for p in microcms_posts}
        return microcms_posts + [p for p in fallback_posts if p["title"] not in titles]
    return microcms_posts or fallback_posts


def preview_text(lines, limit=100):
    text = " ".join(line for line in lines if line.strip())
    if len(text) > limit:
        return text[:limit] + "…"
    return text


def absolute_image_url(image):
    if not image:
        return ""
    if image.startswith("http://") or image.startswith("https://"):
        return image
    return f"{SITE_URL}/{image}"


def rfc822(date_str):
    try:
        dt = datetime.strptime(date_str, "%Y-%m-%d")
    except ValueError:
        dt = datetime.now(timezone.utc)
    dt = dt.replace(tzinfo=timezone.utc)
    return format_datetime(dt, usegmt=True)


NAV_HEAD = """<!DOCTYPE html>
<html lang="ja">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  {gtag}
  <meta name="description" content="{description}">
  <title>{title} | Rie-Utopia</title>
  <link rel="canonical" href="{canonical}">
  <link rel="alternate" type="application/rss+xml" title="Rie-Utopia" href="{site_url}/feed.xml">
  <link rel="icon" href="../favicon.ico" sizes="any">
  <link rel="icon" type="image/png" sizes="32x32" href="../images/favicon-32.png">
  <link rel="icon" type="image/png" sizes="16x16" href="../images/favicon-16.png">
  <link rel="apple-touch-icon" href="../images/apple-touch-icon.png">
  <meta property="og:type" content="article">
  <meta property="og:title" content="{title}">
  <meta property="og:description" content="{description}">
  <meta property="og:url" content="{canonical}">
  {og_image}
  <meta name="twitter:card" content="summary_large_image">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Noto+Sans+JP:wght@400;500;700&family=Shippori+Mincho:wght@400;600;700&family=Zen+Maru+Gothic:wght@500;700&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="../styles.css">
  <script type="application/ld+json">{json_ld}</script>
</head>
<body>
  <div class="sky" aria-hidden="true">
    <div class="sky-photo"></div>
    <div class="sky-overlay"></div>
    <div class="orb orb-1"></div>
    <div class="orb orb-2"></div>
  </div>

  <header class="header glass">
    <nav class="nav">
      <a href="../index.html" class="logo">
        <img src="../images/rie-utopia-logo.png" alt="Rie-Utopia" class="logo-img" width="1024" height="271">
      </a>
      <button class="nav-toggle" aria-label="メニューを開く" aria-expanded="false">
        <span></span><span></span><span></span>
      </button>
      <ul class="nav-links">
        <li><a href="../index.html#poems">作品集</a></li>
        <li><a href="../index.html#about">詩人について</a></li>
        <li><a href="../index.html#instagram">Instagram</a></li>
        <li><a href="../index.html#journal">日記・記録</a></li>
      </ul>
    </nav>
  </header>

  <main>
    <section class="section section-poem-single">
      <div class="container">
        <article class="poem-single glass-panel">
"""

NAV_FOOT = """        </article>
      </div>
    </section>
  </main>

  <footer class="footer glass">
    <div class="container footer-inner">
      <p class="footer-logo">
        <img src="../images/rie-utopia-logo.png" alt="Rie-Utopia" class="footer-logo-img" width="1024" height="271">
      </p>
      <p class="footer-copy">&copy; RIE-Utopia</p>
    </div>
  </footer>

  <script>
    var navToggle = document.querySelector(".nav-toggle");
    var navLinks = document.querySelector(".nav-links");
    if (navToggle && navLinks) {
      navToggle.addEventListener("click", function () {
        var expanded = navToggle.getAttribute("aria-expanded") === "true";
        navToggle.setAttribute("aria-expanded", String(!expanded));
        navLinks.classList.toggle("open");
      });
    }
  </script>
</body>
</html>
"""


def render_post_page(post, prev_post, next_post):
    description = html.escape(preview_text(post["lines"]))
    title = html.escape(post["title"])
    canonical = f"{SITE_URL}/posts/{post['id']}.html"
    image_url = absolute_image_url(post["image"])

    og_image = ""
    if image_url:
        og_image = f'<meta property="og:image" content="{html.escape(image_url)}">'

    json_ld = json.dumps(
        {
            "@context": "https://schema.org",
            "@type": "CreativeWork",
            "genre": post["categoryLabel"],
            "name": post["title"],
            "datePublished": post["date"],
            "image": image_url or None,
            "text": "\n".join(post["lines"]),
            "url": canonical,
        },
        ensure_ascii=False,
    )

    thumb_html = ""
    if post["image"]:
        thumb_html = f"""
          <div class="poem-single-thumb">
            <img src="{html.escape(absolute_image_url(post['image']) if post['image'].startswith('http') else '../' + post['image'])}" alt="{title}" width="800" height="500">
          </div>"""

    body_html = "\n".join(
        f"            <p>{html.escape(line)}</p>" if line.strip() else "            <p>&nbsp;</p>"
        for line in post["lines"]
    )

    nav_links = []
    if prev_post:
        nav_links.append(
            f'<a class="poem-single-nav-link" href="{prev_post["id"]}.html">← {html.escape(prev_post["title"])}</a>'
        )
    if next_post:
        nav_links.append(
            f'<a class="poem-single-nav-link poem-single-nav-next" href="{next_post["id"]}.html">{html.escape(next_post["title"])} →</a>'
        )
    nav_html = f'<nav class="poem-single-nav">{"".join(nav_links)}</nav>' if nav_links else ""

    head = NAV_HEAD.format(
        description=description,
        title=title,
        canonical=canonical,
        site_url=SITE_URL,
        og_image=og_image,
        json_ld=json_ld,
        gtag=GTAG_SNIPPET,
    )

    content = f"""{thumb_html}
          <header class="poem-single-header">
            <time datetime="{html.escape(post['date'])}">{html.escape(post['date'])}</time>
            <h1>{title}</h1>
            <span class="poem-card-tag">{html.escape(post['categoryLabel'])}</span>
          </header>
          <div class="poem-single-body">
{body_html}
          </div>
          {nav_html}
          <p class="poem-single-back"><a href="../index.html#poems">← 作品集に戻る</a></p>
"""

    return head + content + NAV_FOOT


def build_sitemap(posts):
    urls = [f"  <url><loc>{SITE_URL}/</loc></url>"]
    for post in posts:
        urls.append(
            f'  <url><loc>{SITE_URL}/posts/{post["id"]}.html</loc>'
            f'<lastmod>{html.escape(post["date"])}</lastmod></url>'
        )
    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + "\n".join(urls)
        + "\n</urlset>\n"
    )


def build_feed(posts):
    items = []
    for post in sorted(posts, key=lambda p: p["date"], reverse=True)[:30]:
        link = f"{SITE_URL}/posts/{post['id']}.html"
        items.append(
            "  <item>\n"
            f"    <title>{html.escape(post['title'])}</title>\n"
            f"    <link>{link}</link>\n"
            f"    <guid>{link}</guid>\n"
            f"    <pubDate>{rfc822(post['date'])}</pubDate>\n"
            f"    <description>{html.escape(preview_text(post['lines'], 200))}</description>\n"
            "  </item>"
        )

    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<rss version="2.0">\n'
        "<channel>\n"
        "  <title>Rie-Utopia</title>\n"
        f"  <link>{SITE_URL}/</link>\n"
        "  <description>空の色を言葉にする詩人 Rie-Utopia の作品集</description>\n"
        "  <language>ja</language>\n"
        + "\n".join(items)
        + "\n</channel>\n</rss>\n"
    )


def main():
    posts = load_posts()
    if not posts:
        print("投稿データが見つかりませんでした。ビルドをスキップします。")
        return

    posts_dir = PUBLIC / "posts"
    posts_dir.mkdir(exist_ok=True)

    by_category = {}
    for post in posts:
        by_category.setdefault(post["category"], []).append(post)
    for category_posts in by_category.values():
        category_posts.sort(key=lambda p: p["date"])

    for category_posts in by_category.values():
        for i, post in enumerate(category_posts):
            prev_post = category_posts[i - 1] if i > 0 else None
            next_post = category_posts[i + 1] if i + 1 < len(category_posts) else None
            page = render_post_page(post, prev_post, next_post)
            (posts_dir / f"{post['id']}.html").write_text(page, encoding="utf-8")

    (PUBLIC / "sitemap.xml").write_text(build_sitemap(posts), encoding="utf-8")
    (PUBLIC / "feed.xml").write_text(build_feed(posts), encoding="utf-8")

    print(f"生成完了: posts/*.html {len(posts)}件, sitemap.xml, feed.xml")


if __name__ == "__main__":
    main()
