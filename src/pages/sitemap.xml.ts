import type { APIRoute } from "astro";
import { getPosts, absoluteUrl } from "../lib/posts";

export const GET: APIRoute = async () => {
  const posts = await getPosts();
  const urls = [
    `  <url><loc>${absoluteUrl("/")}</loc></url>`,
    `  <url><loc>${absoluteUrl("/poems")}</loc></url>`,
    ...posts.map(
      (post) =>
        `  <url><loc>${absoluteUrl(`/posts/${post.id}.html`)}</loc><lastmod>${post.date}</lastmod></url>`,
    ),
  ];
  const xml = `<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
${urls.join("\n")}
</urlset>
`;
  return new Response(xml, { headers: { "Content-Type": "application/xml; charset=utf-8" } });
};
