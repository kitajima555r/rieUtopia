import { defineConfig } from "astro/config";

export default defineConfig({
  site: "https://rie-utopia.com",
  // /posts/{id}.html の形式を維持し、公開済みURLを壊さない
  build: { format: "file" },
  trailingSlash: "never",
});
