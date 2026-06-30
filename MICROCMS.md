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

サービス設定 → API キー で **2 つ** 発行します。

| 種類 | 用途 | 設定先 |
|---|---|---|
| **読み取り** | サイト表示 | `MICROCMS_READ_API_KEY` / GitHub Secret `MICROCMS_API_KEY` |
| **書き込み** | データ移行・管理画面以外からの投稿 | `.env` の `MICROCMS_WRITE_API_KEY` |

読み取り専用キーでは投稿の一括登録（`setup-microcms.py`）はできません。

## 4. 一括セットアップ（推奨）

`.env` を用意してから:

```bash
cp .env.example .env
# .env に SERVICE_DOMAIN / WRITE / READ を設定

python3 scripts/setup-microcms.py
```

- 未登録の詩だけ `posts.json` から microCMS へ移行
- `public/config.js` を自動生成

## 5. 本番反映（GitHub Secrets）

GitHub → Settings → Secrets → Actions に登録:

| Name | Value |
|---|---|
| `MICROCMS_SERVICE_DOMAIN` | サービス ID（例: `rie-utopia`） |
| `MICROCMS_API_KEY` | **読み取り専用** API キー |

登録後、`main` に push すると本番サイトが microCMS 連携になります。

## 6. スマホから詩を追加

[microCMS 管理画面](https://rie-utopia.microcms.io/) にスマホブラウザでログイン → **posts** → 新規作成。

保存すれば **数秒でサイトに反映** されます（push 不要）。

### 投稿の入力例

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

## 7. ローカル設定

```bash
cp public/config.example.js public/config.js
# または python3 scripts/setup-microcms.py で自動生成
```

## 8. 動作確認

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
