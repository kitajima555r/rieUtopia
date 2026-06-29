# デプロイ手順 — GitHub Pages + microCMS

## すでに完了していること

- コードは https://github.com/kitajima555r/rieUtopia に push 済み
- `main` に push すると GitHub Actions が `gh-pages` ブランチへ自動デプロイ
- microCMS 未設定でも `posts.json` の詩が表示される

## あなたがやること（2分）

### 1. GitHub Pages を有効化

1. https://github.com/kitajima555r/rieUtopia/settings/pages を開く
2. **Build and deployment** → Source: **Deploy from a branch**
3. Branch: **gh-pages** / **/ (root)** を選んで Save

数分後、サイトが公開されます:

**https://kitajima555r.github.io/rieUtopia/**

### 2. microCMS を使う場合（任意・後から OK）

[MICROCMS.md](MICROCMS.md) の手順で API を作成したあと:

```bash
# 書き込み用 API キーで既存データを一括登録
MICROCMS_SERVICE_DOMAIN=あなたのサービスID \
MICROCMS_API_KEY=書き込み用キー \
node scripts/migrate-to-microcms.mjs
```

GitHub → Settings → Secrets → Actions に登録:

| Name | Value |
|---|---|
| `MICROCMS_SERVICE_DOMAIN` | サービス ID |
| `MICROCMS_API_KEY` | 読み取り専用 API キー |

登録後、`main` に空コミットを push すると microCMS 連携が有効になります。

### 3. 独自ドメイン（rie-utopia.com）

Settings → Pages → Custom domain に `rie-utopia.com` を入力し、DNS を GitHub の案内に従って設定。

## ローカル確認

```bash
./scripts/preview.sh
```

http://localhost:8080

## 更新の流れ

| やりたいこと | 方法 |
|---|---|
| 詩を追加・編集（microCMS 利用時） | microCMS 管理画面 |
| 詩を追加・編集（今すぐ） | `public/posts.json` を編集して push |
| デザイン変更 | `public/` 内のファイルを編集して push |
