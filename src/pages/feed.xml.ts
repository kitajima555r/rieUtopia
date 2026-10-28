import type { APIRoute } from "astro";
import { getPosts, description, absoluteUrl } from "../lib/posts";

const esc = (s: string) =>
  s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");

export const GET: APIRoute = async () => {
  const posts = (await getPosts()).slice(0, 30);
  const items = posts
    .map((post) => {
      const link = absoluteUrl(`/posts/${post.id}.html`);
      return `  <item>
    <title>${esc(post.title)}</title>
    <link>${link}</link>
    <guid>${link}</guid>
    <pubDate>${new Date(`${post.date}T00:00:00Z`).toUTCString()}</pubDate>
    <description>${esc(description(post, 200))}</description>
  </item>`;
    })
    .join("\n");

  const xml = `<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
<channel>
  <title>Rie-Utopia</title>
  <link>https://rie-utopia.com/</link>
  <description>空の色を言葉にする詩人 Rie-Utopia の作品集</description>
  <language>ja</language>
${items}
</channel>
</rss>
`;
  return new Response(xml, { headers: { "Content-Type": "application/rss+xml; charset=utf-8" } });
};
