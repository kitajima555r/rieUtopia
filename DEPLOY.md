# デプロイ手順 — GitHub Pages + microCMS

`main` に push すると GitHub Actions（`.github/workflows/deploy.yml`）が `npm run build` を実行し、`dist/` を `gh-pages` ブランチへ公開します。毎時0分（UTC）にも自動でビルドされ、microCMS の更新が反映されます。

## 初回設定

1. GitHub の Settings → Pages で Source を **Deploy from a branch**、Branch を **gh-pages / (root)** に設定
2. Settings → Secrets and variables → Actions に登録:

   | Name | Value |
   |---|---|
   | `MICROCMS_SERVICE_DOMAIN` | サービス ID（`xxx.microcms.io` の `xxx`） |
   | `MICROCMS_API_KEY` | **読み取り専用**（GET のみ）の API キー |

3. 独自ドメイン: Settings → Pages → Custom domain に `rie-utopia.com`、**Enforce HTTPS** を ON

## 反映を早めたいとき

Actions タブ → 「Deploy to GitHub Pages」 → **Run workflow**。

## 補足

- 未設定でも `src/data/posts.fallback.json` の詩でビルドできます。
- リポジトリに長期間コミットが無いと GitHub が定期実行を止めることがあります。その場合は Run workflow で再開してください。
