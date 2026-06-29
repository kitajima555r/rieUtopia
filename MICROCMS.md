# microCMS セットアップ

## 1. サービス作成

1. [microCMS](https://microcms.io/) でアカウント作成
2. 新しいサービスを作成（例: `rie-utopia`）
3. **サービス ID**（`xxx.microcms.io` の `xxx`）をメモ

## 2. API の作成

**API 名**: `posts`（エンドポイント名。変更不可なので注意）

**API タイプ**: リスト形式

### フィールド定義

| フィールド ID | 表示名 | 種類 | 必須 | 備考 |
|---|---|---|---|---|
| `title` | タイトル | テキストフィールド | ✓ | |
| `date` | 日付 | 日時 | ✓ | 日付のみ使用 |
| `category` | カテゴリ | セレクト | ✓ | 選択肢: `poem` / `diary` / `life` |
| `eyecatch` | アイキャッチ | 画像 | ✓ | microCMS メディアにアップロード |
| `body` | 本文 | テキストエリア | ✓ | 1行が詩の1行（改行区切り） |

## 3. API キーの発行

サービス設定 → API キー → **読み取り専用** キーを発行

このキーを `public/config.js` または GitHub Secrets の `MICROCMS_API_KEY` に設定します。

## 4. 既存データの移行

`public/posts.json` の各投稿を microCMS に手動登録するか、管理画面からコピーしてください。

### 登録例（「人生の途中で。」）

| フィールド | 値 |
|---|---|
| title | 人生の途中で。 |
| date | 2026-06-11 |
| category | diary |
| eyecatch | `images/eyecatch-098.jpg` を microCMS にアップロード |
| body | posts.json の `lines` を改行で結合したテキスト |

```text
計り知れない
僕らの未来が
押し寄せてきても
...
```

## 5. ローカル設定

```bash
cp public/config.example.js public/config.js
```

```javascript
window.MICROCMS_CONFIG = {
  serviceDomain: "rie-utopia",
  apiKey: "xxxxxxxxxxxxxxxx",
};
```

## 6. 動作確認

ブラウザの開発者ツール → Network で以下が 200 になることを確認：

```
GET https://{serviceDomain}.microcms.io/api/v1/posts?orders=-date&limit=100
```

## カテゴリと表示ラベル

| category 値 | サイト上の表示 |
|---|---|
| `poem` | 詩 |
| `diary` | 日記 |
| `life` | 生きる |

ラベルは `script.js` 内で自動変換されます。microCMS 側で `categoryLabel` フィールドは不要です。
