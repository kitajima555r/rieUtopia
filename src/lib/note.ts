export const NOTE_URL = "https://note.com/riesorairo_";

export interface NoteArticle {
  title: string;
  url: string;
  date: string;
  image: string;
}

const decode = (s: string) =>
  s
    .replace(/<!\[CDATA\[([\s\S]*?)\]\]>/g, "$1")
    .replace(/&lt;/g, "<")
    .replace(/&gt;/g, ">")
    .replace(/&quot;/g, '"')
    .replace(/&#39;|&apos;/g, "'")
    .replace(/&amp;/g, "&")
    .trim();

const tag = (xml: string, name: string) =>
  xml.match(new RegExp(`<${name}>([\\s\\S]*?)</${name}>`))?.[1];

const toJstDate = (pubDate: string) => {
  const d = new Date(pubDate);
  return Number.isNaN(d.getTime())
    ? ""
    : d.toLocaleDateString("sv-SE", { timeZone: "Asia/Tokyo" });
};

/** note の公式RSSから最新記事を取得する。失敗時は空配列（ビルドは止めない）。 */
export async function getNoteArticles(limit = 3): Promise<NoteArticle[]> {
  try {
    const res = await fetch(`${NOTE_URL}/rss`);
    if (!res.ok) throw new Error(`note ${res.status}`);
    const xml = await res.text();
    return [...xml.matchAll(/<item>([\s\S]*?)<\/item>/g)]
      .slice(0, limit)
      .map(([, item]) => ({
        title: decode(tag(item, "title") ?? ""),
        url: decode(tag(item, "link") ?? ""),
        date: toJstDate(decode(tag(item, "pubDate") ?? "")),
        image: decode(tag(item, "media:thumbnail") ?? ""),
      }))
      .filter((a) => a.title && a.url);
  } catch (err) {
    console.warn(`note の取得をスキップ: ${err}`);
    return [];
  }
}
