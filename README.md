# Rie-Utopia — 青空の詩

[rie-utopia.com](http://rie-utopia.com) のサイト。**GitHub Pages** で公開し、詩・日記は **microCMS** で管理します。

リポジトリ: https://github.com/kitajima555r/rieUtopia

## クイックスタート（ローカル確認）

```bash
cd rieu-topia
cp public/config.example.js public/config.js
# config.js に microCMS の serviceDomain と apiKey を設定

cd public
python3 -m http.server 8080
```

http://localhost:8080 を開く

`config.js` が未設定の場合は `posts.json` をフォールバックとして表示します。

## microCMS の設定

**[MICROCMS.md](MICROCMS.md)** に API の作り方と既存データの移行手順をまとめています。

## GitHub Pages へのデプロイ

**[DEPLOY.md](DEPLOY.md)** を参照してください。

`main` ブランチへの push で自動デプロイされます。GitHub リポジトリの Settings → Secrets に以下を登録してください。

| Secret 名 | 内容 |
|---|---|
| `MICROCMS_SERVICE_DOMAIN` | microCMS のサービス ID（`xxx.microcms.io` の `xxx` 部分） |
| `MICROCMS_API_KEY` | 読み取り専用 API キー |

## ディレクトリ構成

```
rieu-topia/
├── public/                  ← GitHub Pages の公開ソース
│   ├── index.html
│   ├── styles.css
│   ├── script.js
│   ├── config.example.js
│   ├── posts.json           ← ローカル確認用フォールバック
│   └── images/
├── .github/workflows/
│   └── deploy.yml           ← GitHub Pages 自動デプロイ
├── MICROCMS.md
├── DEPLOY.md
└── README.md
```

## 詩の追加・編集

[microCMS の管理画面](https://microcms.io/) から投稿を追加・編集します。サイトへの反映は API 経由で即時です。
