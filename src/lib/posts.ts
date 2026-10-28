import fallbackJson from "../data/posts.fallback.json";

export type Category = "poem" | "diary" | "life";

export interface Post {
  id: string;
  title: string;
  date: string;
  category: Category;
  categoryLabel: string;
  image: string;
  lines: string[];
}

export const CATEGORY_LABELS: Record<Category, string> = {
  poem: "詩",
  diary: "日記",
  life: "生きる",
};

const CATEGORY_ALIASES: Record<string, Category> = {
  詩: "poem",
  日記: "diary",
  生きる: "life",
};

const env = (name: string): string | undefined =>
  (import.meta.env as Record<string, string | undefined>)[name] ?? process.env[name];

function normalizeCategory(category: unknown): Category {
  const raw = Array.isArray(category) ? category[0] : category;
  if (!raw || typeof raw !== "string") return "poem";
  return (CATEGORY_ALIASES[raw] ?? raw) as Category;
}

function normalizeImage(item: any): string {
  if (typeof item.image === "string" && item.image) {
    return item.image.startsWith("http") ? item.image : `/${item.image.replace(/^\//, "")}`;
  }
  if (item.eyecatch?.url) return item.eyecatch.url;
  if (typeof item.eyecatch === "string") return item.eyecatch;
  return "";
}

function normalizePost(item: any): Post {
  const category = normalizeCategory(item.category);
  const lines: string[] = item.lines ?? String(item.body ?? "").split("\n");
  return {
    id: String(item.id),
    title: item.title ?? "",
    date: String(item.date ?? "").slice(0, 10),
    category,
    categoryLabel: CATEGORY_LABELS[category] ?? category,
    image: normalizeImage(item),
    lines,
  };
}

async function fetchFromMicroCMS(): Promise<Post[]> {
  const serviceDomain = env("MICROCMS_SERVICE_DOMAIN");
  const apiKey = env("MICROCMS_API_KEY") ?? env("MICROCMS_READ_API_KEY");
  if (!serviceDomain || !apiKey) return [];

  const limit = 100;
  let offset = 0;
  const contents: any[] = [];

  try {
    while (true) {
      const url = `https://${serviceDomain}.microcms.io/api/v1/posts?orders=-date&limit=${limit}&offset=${offset}`;
      const res = await fetch(url, { headers: { "X-MICROCMS-API-KEY": apiKey } });
      if (!res.ok) throw new Error(`microCMS ${res.status}`);
      const data = await res.json();
      const page: any[] = data.contents ?? [];
      contents.push(...page);
      offset += limit;
      if (offset >= (data.totalCount ?? 0) || page.length < limit) break;
    }
  } catch (err) {
    console.warn(`microCMS 取得をスキップ（フォールバックを使用）: ${err}`);
    return [];
  }

  return contents.map(normalizePost);
}

let cache: Promise<Post[]> | undefined;

/** microCMS を優先し、同じタイトルのものは posts.json 側を除外して日付降順で返す */
export function getPosts(): Promise<Post[]> {
  cache ??= (async () => {
    const microcms = await fetchFromMicroCMS();
    const fallback = (fallbackJson as any[]).map(normalizePost);
    const titles = new Set(microcms.map((p) => p.title));
    const merged = [...microcms, ...fallback.filter((p) => !titles.has(p.title))];
    return merged.sort((a, b) => (a.date < b.date ? 1 : a.date > b.date ? -1 : 0));
  })();
  return cache;
}

export function preview(post: Post, count = 2): string {
  return post.lines.filter((l) => l.trim()).slice(0, count).join("\n");
}

export function description(post: Post, limit = 100): string {
  const text = post.lines.filter((l) => l.trim()).join(" ");
  return text.length > limit ? `${text.slice(0, limit)}…` : text;
}

export function stanzas(post: Post): string[][] {
  const out: string[][] = [];
  let current: string[] = [];
  for (const line of post.lines) {
    if (line.trim()) {
      current.push(line);
    } else if (current.length) {
      out.push(current);
      current = [];
    }
  }
  if (current.length) out.push(current);
  return out;
}

export function absoluteUrl(path: string): string {
  if (path.startsWith("http")) return path;
  return `https://rie-utopia.com${path.startsWith("/") ? "" : "/"}${path}`;
}
