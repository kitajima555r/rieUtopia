#!/bin/bash
# ローカル確認用 — public/ を簡易サーバーで起動
cd "$(dirname "$0")/../public"
echo "http://localhost:8080 で開いてください"
python3 -m http.server 8080
