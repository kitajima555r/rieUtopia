let POEMS = [];

const CATEGORY_LABELS = { poem: "詩", diary: "日記", life: "生きる" };

const poemGrid = document.getElementById("poem-grid");
const filterBtns = document.querySelectorAll(".filter-btn");
const modal = document.getElementById("poem-modal");
const modalTitle = document.getElementById("modal-title");
const modalDate = document.getElementById("modal-date");
const modalCategory = document.getElementById("modal-category");
const modalBody = document.getElementById("modal-body");
const modalThumb = document.getElementById("modal-thumb");
const modalImage = document.getElementById("modal-image");
const modalClose = document.querySelector(".modal-close");

function previewText(lines) {
  return lines.filter(Boolean).slice(0, 4).join("\n");
}

function normalizeCategory(category) {
  if (Array.isArray(category)) return category[0] || "poem";
  return category || "poem";
}

function normalizePost(item) {
  const category = normalizeCategory(item.category);
  const lines = (item.body || "").split("\n");

  return {
    id: item.id,
    title: item.title,
    date: item.date,
    category,
    categoryLabel: CATEGORY_LABELS[category] || category,
    image: item.eyecatch?.url || "",
    lines,
  };
}

function renderPoems(filter = "all") {
  if (!poemGrid) return;

  const filtered =
    filter === "all" ? POEMS : POEMS.filter((p) => p.category === filter);

  if (filtered.length === 0) {
    poemGrid.innerHTML =
      '<p class="poem-empty">まだ投稿がありません。microCMS で詩を追加してください。</p>';
    return;
  }

  poemGrid.innerHTML = filtered
    .map(
      (poem) => `
    <button class="poem-card glass-panel" data-id="${poem.id}" aria-label="${poem.title}を読む">
      <div class="poem-card-thumb">
        <img src="${poem.image}" alt="" loading="lazy" width="800" height="500">
      </div>
      <div class="poem-card-body">
        <div class="poem-card-meta">
          <time datetime="${poem.date}">${poem.date}</time>
          <span class="poem-card-tag">${poem.categoryLabel}</span>
        </div>
        <h3>${poem.title}</h3>
        <p class="poem-card-preview">${previewText(poem.lines)}</p>
        <span class="poem-card-more">続きを読む →</span>
      </div>
    </button>
  `
    )
    .join("");

  poemGrid.querySelectorAll(".poem-card").forEach((card) => {
    card.addEventListener("click", () => openModal(card.dataset.id));
  });
}

function openModal(id) {
  const poem = POEMS.find((p) => p.id === id);
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

  modal.showModal();
}

filterBtns.forEach((btn) => {
  btn.addEventListener("click", () => {
    filterBtns.forEach((b) => {
      b.classList.remove("active");
      b.setAttribute("aria-selected", "false");
    });
    btn.classList.add("active");
    btn.setAttribute("aria-selected", "true");
    renderPoems(btn.dataset.filter);
  });
});

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

  const endpoint = `https://${config.serviceDomain}.microcms.io/api/v1/posts?orders=-date&limit=100`;
  const res = await fetch(endpoint, {
    headers: { "X-MICROCMS-API-KEY": config.apiKey },
  });

  if (!res.ok) throw new Error("microCMS fetch failed");
  const data = await res.json();
  return (data.contents || []).map(normalizePost);
}

async function fetchFromFallback() {
  const res = await fetch("posts.json");
  if (!res.ok) throw new Error("posts.json not found");
  return (await res.json()).map((post) => ({
    ...post,
    categoryLabel: post.categoryLabel || CATEGORY_LABELS[post.category] || post.category,
  }));
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

  renderPoems();
}

init();
