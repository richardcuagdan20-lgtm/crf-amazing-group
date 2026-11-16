import { defineConfig } from "astro/config";

export default defineConfig({
  site: "https://crf-amazing-group.pages.dev",
  output: "static",
  compressHTML: true,
  trailingSlash: "never",
});
