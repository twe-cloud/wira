#!/usr/bin/env node
/**
 * Sync the brand name + description from src/lib/brand.ts into the static
 * <title> and <meta> tags in index.html. Run on `npm run build` so the
 * rendered HTML matches the canonical brand config.
 *
 * Usage:  node scripts/sync-brand.mjs
 */
import { readFileSync, writeFileSync } from "node:fs";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const root = resolve(dirname(fileURLToPath(import.meta.url)), "..");
const brandPath = resolve(root, "src/lib/brand.ts");
const htmlPath = resolve(root, "index.html");

const brand = readFileSync(brandPath, "utf8");

function pull(key) {
  const m = brand.match(new RegExp(`${key}:\\s*"([^"]+)"`));
  if (!m) throw new Error(`brand.ts missing key: ${key}`);
  return m[1];
}

const name = pull("name");
const tagline = pull("tagline");
const description = pull("description");

let html = readFileSync(htmlPath, "utf8");
const before = html;

const title = `${name} — ${tagline}`;
html = html.replace(/<title>[^<]*<\/title>/, `<title>${title}</title>`);
html = html.replace(
  /(<meta name="description" content=")[^"]*(")/,
  `$1${description}$2`,
);
html = html.replace(
  /(<meta property="og:title" content=")[^"]*(")/,
  `$1${title}$2`,
);
html = html.replace(
  /(<meta property="og:description" content=")[^"]*(")/,
  `$1${description}$2`,
);

if (html === before) {
  console.log("sync-brand: nothing to update");
} else {
  writeFileSync(htmlPath, html);
  console.log(`sync-brand: updated index.html → ${title}`);
}
