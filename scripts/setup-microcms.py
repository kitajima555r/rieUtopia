#!/usr/bin/env python3
"""microCMS セットアップ: 接続確認・データ移行・config.js 生成"""

import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ENV_FILE = ROOT / ".env"
POSTS_FILE = ROOT / "public" / "posts.json"
CONFIG_FILE = ROOT / "public" / "config.js"
IMAGE_BASE_URL = os.environ.get(
    "MICROCMS_IMAGE_BASE_URL",
    "https://rie-utopia.com",
)


def load_env():
    if not ENV_FILE.exists():
        print("❌ .env がありません")
        sys.exit(1)
    env = {}
    for line in ENV_FILE.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        env[key.strip()] = value.strip()
    return env


def api_request(url, api_key, method="GET", data=None, content_type="application/json"):
    headers = {"X-MICROCMS-API-KEY": api_key}
    body = None
    if data is not None:
        headers["Content-Type"] = content_type
        body = data if isinstance(data, bytes) else json.dumps(data).encode("utf-8")

    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req) as res:
            return json.loads(res.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        if e.code == 400 and "POST is forbidden" in body:
            raise RuntimeError(
                "書き込み API キーが読み取り専用です。"
                "microCMS 管理画面 → サービス設定 → API キー → 書き込み用 を発行し、"
                ".env の MICROCMS_WRITE_API_KEY に設定してください。"
            ) from e
        raise RuntimeError(f"HTTP {e.code}: {body}") from e


def image_url(local_path: str) -> str:
    return f"{IMAGE_BASE_URL.rstrip('/')}/{local_path.lstrip('/')}"


def main():
    env = load_env()
    domain = env.get("MICROCMS_SERVICE_DOMAIN")
    write_key = env.get("MICROCMS_WRITE_API_KEY")
    read_key = env.get("MICROCMS_READ_API_KEY")

    if not domain or not write_key or not read_key:
        print("❌ .env の設定が不足しています")
        sys.exit(1)

    base_url = f"https://{domain}.microcms.io/api/v1"
    posts = json.loads(POSTS_FILE.read_text(encoding="utf-8"))

    print(f"\n🔧 microCMS セットアップ開始 ({domain}.microcms.io)\n")

    for label, key in [("読み取り", read_key), ("書き込み", write_key)]:
        api_request(f"{base_url}/posts?limit=1", key)
        print(f"✅ {label} API 接続 OK")

    existing_titles = set()
    offset = 0
    while True:
        batch = api_request(f"{base_url}/posts?limit=100&offset={offset}&fields=title", read_key)
        for item in batch.get("contents", []):
            existing_titles.add(item["title"])
        if offset + batch.get("limit", 100) >= batch.get("totalCount", 0):
            break
        offset += 100

    to_migrate = [p for p in posts if p["title"] not in existing_titles]
    if not to_migrate:
        print(f"\n✅ 全 {len(posts)} 件は microCMS に登録済みです。")
    else:
        print(f"\n📤 {len(to_migrate)} 件を登録中（既存 {len(existing_titles)} 件）...\n")
        for post in to_migrate:
            print(f"  「{post['title']}」...", end=" ", flush=True)
            api_request(
                f"{base_url}/posts",
                write_key,
                method="POST",
                data={
                    "title": post["title"],
                    "date": post["date"],
                    "category": post["category"],
                    "eyecatch": image_url(post["image"]),
                    "body": "\n".join(post["lines"]),
                },
            )
            print("OK")

    CONFIG_FILE.write_text(
        f'window.MICROCMS_CONFIG = {{\n'
        f'  serviceDomain: "{domain}",\n'
        f'  apiKey: "{read_key}",\n'
        f'}};\n',
        encoding="utf-8",
    )
    print("\n✅ public/config.js を生成しました")
    print(f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
GitHub Secrets を登録してください:
https://github.com/kitajima555r/rieUtopia/settings/secrets/actions

  MICROCMS_SERVICE_DOMAIN = {domain}
  MICROCMS_API_KEY        = （読み取り専用キー）

登録後、main に push で本番反映されます。
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
""")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n❌ {e}")
        print("\nフィールド ID: title / date / category / eyecatch / body")
        print("エンドポイント名: posts")
        sys.exit(1)
