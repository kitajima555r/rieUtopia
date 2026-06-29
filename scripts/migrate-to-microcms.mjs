#!/usr/bin/env node
/**
 * posts.json の内容を microCMS に一括登録するスクリプト
 *
 * 使い方:
 *   MICROCMS_SERVICE_DOMAIN=rie-utopia \
 *   MICROCMS_API_KEY=xxxxxxxx \
 *   node scripts/migrate-to-microcms.mjs
 *
 * API キーは microCMS 管理画面 → サービス設定 → API キー → 書き込み用
 */

import { readFileSync } from "fs";
import { dirname, join } from "path";
import { fileURLToPath } from "url";

const __dirname = dirname(fileURLToPath(import.meta.url));
const ROOT = join(__dirname, "..");

const serviceDomain = process.env.MICROCMS_SERVICE_DOMAIN;
const apiKey = process.env.MICROCMS_API_KEY;

if (!serviceDomain || !apiKey) {
  console.error("環境変数 MICROCMS_SERVICE_DOMAIN と MICROCMS_API_KEY を設定してください");
  process.exit(1);
}

const posts = JSON.parse(
  readFileSync(join(ROOT, "public/posts.json"), "utf-8")
);

const baseUrl = `https://${serviceDomain}.microcms.io/api/v1`;

async function uploadImage(localPath) {
  const imagePath = join(ROOT, "public", localPath);
  const filename = localPath.split("/").pop();
  const blob = new Blob([readFileSync(imagePath)]);
  const form = new FormData();
  form.append("file", blob, filename);

  const res = await fetch(`${baseUrl}/media`, {
    method: "POST",
    headers: { "X-MICROCMS-API-KEY": apiKey },
    body: form,
  });

  if (!res.ok) {
    const text = await res.text();
    throw new Error(`画像アップロード失敗 (${localPath}): ${text}`);
  }

  const data = await res.json();
  return data.url;
}

async function createPost(post, eyecatchUrl) {
  const body = {
    title: post.title,
    date: post.date,
    category: post.category,
    eyecatch: eyecatchUrl,
    body: post.lines.join("\n"),
  };

  const res = await fetch(`${baseUrl}/posts`, {
    method: "POST",
    headers: {
      "X-MICROCMS-API-KEY": apiKey,
      "Content-Type": "application/json",
    },
    body: JSON.stringify(body),
  });

  if (!res.ok) {
    const text = await res.text();
    throw new Error(`投稿作成失敗 (${post.title}): ${text}`);
  }

  return res.json();
}

async function main() {
  console.log(`${posts.length} 件を microCMS に登録します...\n`);

  for (const post of posts) {
    process.stdout.write(`「${post.title}」... `);
    const eyecatchUrl = await uploadImage(post.image);
    await createPost(post, eyecatchUrl);
    console.log("OK");
  }

  console.log("\n完了！読み取り専用 API キーを GitHub Secrets に登録してください。");
}

main().catch((err) => {
  console.error(err.message);
  process.exit(1);
});
