let POEMS = [];

const CATEGORY_LABELS = { poem: "詩", diary: "日記", life: "生きる" };
const CATEGORY_ALIASES = { 詩: "poem", 日記: "diary", 生きる: "life" };

const poemGrid = document.getElementById("poem-grid");
const featuredGrid = document.getElementById("featured-grid");
const portfolioStats = document.getElementById("portfolio-stats");
const filterBtns = document.querySelectorAll(".filter-btn");
const modal = document.getElementById("poem-modal");
const modalTitle = document.getElementById("modal-title");
const modalDate = document.getElementById("modal-date");
const modalCategory = document.getElementById("modal-category");
const modalBody = document.getElementById("modal-body");
const modalThumb = document.getElementById("modal-thumb");
const modalImage = document.getElementById("modal-image");
const modalClose = document.querySelector(".modal-close");

function escapeHtml(str) {
  return String(str)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

function formatDate(dateStr) {
  if (!dateStr) return "";
  return dateStr.slice(0, 10);
}

function normalizeImage(item) {
  if (typeof item.image === "string" && item.image) return item.image;
  if (item.eyecatch?.url) return item.eyecatch.url;
  if (typeof item.eyecatch === "string") return item.eyecatch;
  return "";
}

function previewText(lines) {
  return lines.filter(Boolean).slice(0, 4).join("\n");
}

function normalizeCategory(category) {
  const raw = Array.isArray(category) ? category[0] : category;
  if (!raw) return "poem";
  return CATEGORY_ALIASES[raw] || raw;
}

function normalizePost(item) {
  const category = normalizeCategory(item.category);
  const lines = item.lines || (item.body || "").split("\n");

  return {
    id: String(item.id),
    title: item.title,
    date: formatDate(item.date),
    category,
    categoryLabel: CATEGORY_LABELS[category] || category,
    image: normalizeImage(item),
    lines,
  };
}

function createPoemCard(poem, variant = "default") {
  const card = document.createElement("a");
  card.href = `posts/${encodeURIComponent(poem.id)}.html`;
  card.className = variant === "featured" ? "featured-card glass-panel" : "poem-card glass-panel";
  card.setAttribute("aria-label", `${poem.title}を読む`);

  const thumb = document.createElement("div");
  thumb.className = variant === "featured" ? "featured-card-thumb" : "poem-card-thumb";
  if (poem.image) {
    const img = document.createElement("img");
    img.src = poem.image;
    img.alt = "";
    img.loading = "lazy";
    img.width = 800;
    img.height = 500;
    thumb.appendChild(img);
  }

  const body = document.createElement("div");
  body.className = variant === "featured" ? "featured-card-body" : "poem-card-body";
  body.innerHTML = `
    <div class="poem-card-meta">
      <time datetime="${escapeHtml(poem.date)}">${escapeHtml(poem.date)}</time>
      <span class="poem-card-tag">${escapeHtml(poem.categoryLabel)}</span>
    </div>
    <h3>${escapeHtml(poem.title)}</h3>
    <p class="poem-card-preview">${escapeHtml(previewText(poem.lines))}</p>
    <span class="poem-card-more">続きを読む →</span>
  `;

  card.append(thumb, body);
  card.addEventListener("click", (e) => {
    e.preventDefault();
    openModal(poem);
  });
  return card;
}

function renderFeaturedPoems() {
  if (!featuredGrid) return;

  const poems = POEMS.filter((p) => p.category === "poem").slice(0, 3);
  featuredGrid.innerHTML = "";

  if (!poems.length) {
    featuredGrid.innerHTML = '<p class="poem-empty">代表作を読み込み中です。</p>';
    return;
  }

  poems.forEach((poem) => {
    featuredGrid.appendChild(createPoemCard(poem, "featured"));
  });
}

function renderPortfolioStats() {
  if (!portfolioStats) return;

  const poemCount = POEMS.filter((p) => p.category === "poem").length;
  const totalCount = POEMS.length;

  portfolioStats.innerHTML = `
    <span class="stat-item"><strong>${poemCount}</strong> 編の詩</span>
    <span class="stat-divider" aria-hidden="true">·</span>
    <span class="stat-item"><strong>${totalCount}</strong> 作品</span>
  `;
}

let currentFilter = "poem";
let currentQuery = "";

function matchesQuery(poem, query) {
  if (!query) return true;
  const haystack = `${poem.title}\n${poem.lines.join("\n")}`.toLowerCase();
  return haystack.includes(query);
}

function renderPoems() {
  if (!poemGrid) return;

  const byCategory =
    currentFilter === "all" ? POEMS : POEMS.filter((p) => p.category === currentFilter);
  const query = currentQuery.trim().toLowerCase();
  const filtered = byCategory.filter((p) => matchesQuery(p, query));

  poemGrid.innerHTML = "";

  if (filtered.length === 0) {
    poemGrid.innerHTML = query
      ? '<p class="poem-empty">一致する詩が見つかりませんでした。</p>'
      : '<p class="poem-empty">まだ投稿がありません。microCMS で詩を追加してください。</p>';
    return;
  }

  filtered.forEach((poem) => {
    poemGrid.appendChild(createPoemCard(poem));
  });
}

function openModal(poem) {
  if (!poem || !modal) return;

  modalTitle.textContent = poem.title;
  modalDate.textContent = poem.date;
  modalCategory.textContent = poem.categoryLabel;
  modalBody.textContent = poem.lines.join("\n");

  if (poem.image) {
    modalImage.src = poem.image;
    modalImage.alt = poem.title;
    modalThumb.hidden = false;
  } else {
    modalThumb.hidden = true;
    modalImage.removeAttribute("src");
  }

  if (typeof modal.showModal === "function") {
    if (!modal.open) modal.showModal();
  } else {
    modal.setAttribute("open", "");
  }
}

const poemSearch = document.getElementById("poem-search");

filterBtns.forEach((btn) => {
  btn.addEventListener("click", () => {
    filterBtns.forEach((b) => {
      b.classList.remove("active");
      b.setAttribute("aria-selected", "false");
    });
    btn.classList.add("active");
    btn.setAttribute("aria-selected", "true");
    currentFilter = btn.dataset.filter;
    renderPoems();
  });
});

if (poemSearch) {
  poemSearch.addEventListener("input", () => {
    currentQuery = poemSearch.value;
    renderPoems();
  });
}

if (modal && modalClose) {
  modalClose.addEventListener("click", () => modal.close());
  modal.addEventListener("click", (e) => {
    if (e.target === modal) modal.close();
  });
}

document.addEventListener("keydown", (e) => {
  if (e.key === "Escape" && modal && modal.open) modal.close();
});

const navToggle = document.querySelector(".nav-toggle");
const navLinks = document.querySelector(".nav-links");

if (navToggle && navLinks) {
  navToggle.addEventListener("click", () => {
    const expanded = navToggle.getAttribute("aria-expanded") === "true";
    navToggle.setAttribute("aria-expanded", String(!expanded));
    navLinks.classList.toggle("open");
  });

  navLinks.querySelectorAll("a").forEach((link) => {
    link.addEventListener("click", () => {
      navToggle.setAttribute("aria-expanded", "false");
      navLinks.classList.remove("open");
    });
  });
}

async function fetchFromMicroCMS() {
  const config = window.MICROCMS_CONFIG;
  if (!config?.serviceDomain || !config?.apiKey) {
    throw new Error("microCMS config missing");
  }

  const limit = 100;
  let offset = 0;
  let contents = [];

  while (true) {
    const endpoint = `https://${config.serviceDomain}.microcms.io/api/v1/posts?orders=-date&limit=${limit}&offset=${offset}`;
    const res = await fetch(endpoint, {
      headers: { "X-MICROCMS-API-KEY": config.apiKey },
    });

    if (!res.ok) throw new Error("microCMS fetch failed");
    const data = await res.json();
    const page = data.contents || [];
    contents = contents.concat(page);
    offset += limit;
    if (offset >= (data.totalCount || 0) || page.length < limit) break;
  }

  return contents.map(normalizePost);
}

async function fetchFromFallback() {
  const res = await fetch("posts.json");
  if (!res.ok) throw new Error("posts.json not found");
  return (await res.json()).map((post) =>
    normalizePost({
      ...post,
      categoryLabel: post.categoryLabel || CATEGORY_LABELS[post.category] || post.category,
    })
  );
}

async function init() {
  let microcmsPosts = [];
  let fallbackPosts = [];

  try {
    microcmsPosts = await fetchFromMicroCMS();
  } catch {
    microcmsPosts = [];
  }

  try {
    fallbackPosts = await fetchFromFallback();
  } catch {
    fallbackPosts = [];
  }

  if (microcmsPosts.length > 0 && fallbackPosts.length > 0) {
    const titles = new Set(microcmsPosts.map((p) => p.title));
    POEMS = [
      ...microcmsPosts,
      ...fallbackPosts.filter((p) => !titles.has(p.title)),
    ];
  } else {
    POEMS = microcmsPosts.length > 0 ? microcmsPosts : fallbackPosts;
  }

  renderPortfolioStats();
  renderFeaturedPoems();
  renderPoems();
}

init();
