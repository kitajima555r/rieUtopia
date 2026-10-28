/**
 * サイトの文言・リンクはここだけ編集すれば更新できます。
 * （詩・日記は microCMS、noteの記事は note のRSSから自動で入ります）
 */
export const site = {
  name: "Rie-Utopia",
  url: "https://rie-utopia.com",
  penName: "空色りえ",
  /** ロゴ・faviconを差し替えたら +1。ブラウザの古いキャッシュを確実に更新させる */
  assetVersion: 2,
  role: "詩人 / エッセイスト",
  description:
    "青空の下で綴る詩のポートフォリオ。双極性障害とともに生きながら、空の色を言葉にする詩人 空色りえ（rie-Utopia）の作品集。",

  /** トップの見出し下に出るキャッチコピー（1要素=1行） */
  tagline: ["空の色を言葉にする。", "生きた証を書きとめていく。"],

  about: {
    paragraphs: [
      "幼少のころから詩を書くのが趣味。空の色、日々の気配、生きることの重さとやわらかさを、短い行の詩にしています。",
    ],
    note: "元統合失調症。寛解して結婚、出産。現在は双極性障害Ⅱ型とともに、言葉を書き続けています。",
  },

  /** トップの引用。sourceTitle を含むタイトルの詩へリンクします */
  quote: {
    lines: ["ここまで", "よくがんばったね。"],
    sourceTitle: "よくここまでがんばったね",
  },

  links: {
    instagram: { label: "Instagram", handle: "@rieutopia", url: "https://www.instagram.com/rieutopia/" },
    x: { label: "X", handle: "@rieutopia", url: "https://x.com/rieutopia" },
    note: { label: "note", handle: "空色りえ", url: "https://note.com/riesorairo_" },
  },
} as const;

export const nav = [
  { label: "詩を読む", href: "/poems", primary: true },
  { label: "About", href: "/#about" },
  { label: "note", href: site.links.note.url, external: true },
  { label: "Instagram", href: site.links.instagram.url, external: true },
] as const;
