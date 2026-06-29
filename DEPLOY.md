# デプロイ手順 — GitHub Pages + microCMS

## 1. microCMS の準備

[MICROCMS.md](MICROCMS.md) に従って API を作成し、投稿データを登録してください。

## 2. GitHub リポジトリの設定

リポジトリ: https://github.com/kitajima555r/rieUtopia

### Secrets の登録

Settings → Secrets and variables → Actions → New repository secret

| Name | Value |
|---|---|
| `MICROCMS_SERVICE_DOMAIN` | サービス ID（例: `rie-utopia`） |
| `MICROCMS_API_KEY` | 読み取り専用 API キー |

### GitHub Pages の有効化

Settings → Pages → Build and deployment

- **Source**: GitHub Actions

`main` ブランチに push すると `.github/workflows/deploy.yml` が自動実行され、サイトが公開されます。

## 3. 独自ドメイン（rie-utopia.com）の設定

Settings → Pages → Custom domain に `rie-utopia.com` を入力します。

DNS（さくらインターネット等）で以下を設定：

| タイプ | ホスト | 値 |
|---|---|---|
| CNAME | `www` | `kitajima555r.github.io` |
| A | `@` | GitHub Pages の IP（GitHub の案内に従う） |

## 4. 更新の流れ

1. microCMS の管理画面で詩・日記を編集・公開
2. サイトは API から最新データを取得するため、**コードの再デプロイは不要**

画像を差し替える場合は microCMS のメディア欄、または `public/images/` に追加して push してください。

## ローカルでの確認

```bash
cp public/config.example.js public/config.js
# config.js を編集

cd public && python3 -m http.server 8080
```

## 旧構成からの移行メモ

| 以前 | 現在 |
|---|---|
| MySQL / serve.py | 廃止 |
| admin/ 投稿管理 | microCMS 管理画面 |
| さくらサーバー FTP | GitHub Pages |
| posts.json 直接編集 | microCMS API（posts.json はローカル用フォールバック） |
