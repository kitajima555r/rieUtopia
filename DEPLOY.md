# デプロイ手順 — GitHub Pages + microCMS

`main` に push すると GitHub Actions（`.github/workflows/deploy.yml`）が `npm run build` を実行し、`dist/` を `gh-pages` ブランチへ公開します。microCMS で保存・公開すると、Webhook 経由で数分後にサイトへ反映されます（設定は下記）。念のための定期ビルドもありますが、GitHub の定期実行は遅れやすく**数時間おき**になるため、Webhook の設定をおすすめします。

## 初回設定

1. GitHub の Settings → Pages で Source を **Deploy from a branch**、Branch を **gh-pages / (root)** に設定
2. Settings → Secrets and variables → Actions に登録:

   | Name | Value |
   |---|---|
   | `MICROCMS_SERVICE_DOMAIN` | サービス ID（`xxx.microcms.io` の `xxx`） |
   | `MICROCMS_API_KEY` | **読み取り専用**（GET のみ）の API キー |

3. 独自ドメイン: Settings → Pages → Custom domain に `rie-utopia.com`、**Enforce HTTPS** を ON

## microCMS の更新を数分で反映する（Webhook）

1. **GitHub のトークンを作る**: GitHub → 右上アイコン → Settings → Developer settings → Personal access tokens → Fine-grained tokens → Generate new token
   - Repository access: **Only select repositories** → `rieUtopia` だけ
   - Permissions → Repository permissions → **Contents: Read and write**
   - 発行された文字列（`github_pat_...`）をコピー（再表示できません）
2. **microCMS に Webhook を登録**: サービス設定 → Webhook → 追加 → カスタム通知
   - URL: `https://api.github.com/repos/kitajima555r/rieUtopia/dispatches`
   - カスタムヘッダー: `Authorization` = `Bearer github_pat_...`、`Accept` = `application/vnd.github+json`
   - カスタムボディ: `{"event_type":"microcms-update"}`
   - トリガー: posts API の「コンテンツの公開」「公開中コンテンツの編集」「公開の取り下げ」「削除」
3. microCMS で詩を保存して、GitHub の Actions タブに「Deploy to GitHub Pages」が `repository_dispatch` で走れば成功です。

トークンは microCMS の設定にだけ保存します。リポジトリやチャットには貼らないでください。

## すぐ反映したいとき

Actions タブ → 「Deploy to GitHub Pages」 → **Run workflow**。

## 補足

- 未設定でも `src/data/posts.fallback.json` の詩でビルドできます。
- リポジトリに長期間コミットが無いと GitHub が定期実行を止めることがあります。その場合は Run workflow で再開してください。
