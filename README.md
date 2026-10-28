# Rie-Utopia — 詩のポートフォリオ

[rie-utopia.com](https://rie-utopia.com) のサイト。[Astro](https://astro.build/) で静的生成し、**GitHub Pages** で公開します。詩・日記は **microCMS** で管理します。

リポジトリ: https://github.com/kitajima555r/rieUtopia

## ローカルで動かす

```bash
npm install
cp .env.example .env   # microCMS の値を設定（未設定なら src/data/posts.fallback.json を使用）
npm run dev            # http://localhost:4321
```

| コマンド | 内容 |
|---|---|
| `npm run dev` | 開発サーバー |
| `npm run build` | `dist/` に本番ビルド |
| `npm run preview` | ビルド結果の確認 |
| `npm run check` | 型チェック |

## 構成

```
src/
├── pages/
│   ├── index.astro        トップ（ヒーロー・新着・About・日記）
│   ├── poems.astro        詩一覧（カテゴリタブ・検索）
│   ├── posts/[id].astro   詩の個別ページ（/posts/{id}.html）
│   ├── feed.xml.ts        RSS
│   └── sitemap.xml.ts     sitemap
├── layouts/Base.astro     head（GA4・OGP・favicon）・ヘッダー・フッター
├── components/PostCard.astro
├── lib/posts.ts           データ取得（microCMS 優先 + posts.fallback.json）
├── data/posts.fallback.json
└── styles/global.css      デザイン（白基調・#3366ff / #0080ff）
public/                    favicon・画像・robots.txt
design/logo-source.png     ロゴ原本（favicon生成用。公開されません）
scripts/                   画像最適化・favicon生成（Python）
```

## 更新の流れ

- 詩の追加・編集は **microCMS の管理画面**から。**最大1時間以内**にサイトへ反映されます（毎時ビルド）。すぐに反映したいときは GitHub の Actions タブから「Deploy to GitHub Pages」を **Run workflow**。
- デザイン変更は `src/` を編集して `main` に push（自動デプロイ）。
- microCMS の API キーはビルド時のみ使われ、ブラウザには配信されません。

## デプロイ

[DEPLOY.md](DEPLOY.md) を参照してください。

## スクリプト

- `python3 scripts/optimize_images.py` — `public/images` の写真をリサイズ・再圧縮
- `python3 scripts/make_favicon.py` — `design/logo-source.png` から favicon 一式を生成（Pillow が必要）
