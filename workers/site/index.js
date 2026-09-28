// Site Worker for cheatsheets.davidveksler.com on Workers static assets.
//
// Runs only for the run_worker_first globs in wrangler.jsonc: "/", "/*.php",
// "/_x/*", the category hub slugs (with and without a trailing slash),
// "/favicon.ico" and the two provenance files. Everything else is a static asset.
//
// It does per request what nginx + PHP did (spec: docs/specs/cloudflare-migration.md):
//   - the Explorer (index.php) and hubs are prerendered by scripts/build_site.py into
//     dist/_x/; this picks the right one for the URL and marks client-state URLs
//     noindex exactly where index.php did;
//   - ?cat= / ?category= / ?hub= 301 to the hub slug (index.php's redirects);
//   - /history.php 301s to the GitHub history (D-2: the git browser is retired);
//   - /subscribe.php and /confirm.php go to the forms Worker (service binding FORMS);
//   - /popularity.php and /sitemap.php serve their prerendered output.
// Responses built here don't get dist/_headers, so the security headers and the
// droplet's Cache-Control values are set in code.

import routes from "../../build/site-routes.json";

const ORIGIN_HOST = "cheatsheets.davidveksler.com";
const GITHUB = "https://github.com/DavidVeksler/CheatSheets";
const SECURITY = {
  "x-frame-options": "SAMEORIGIN",
  "x-content-type-options": "nosniff",
  "referrer-policy": "strict-origin-when-cross-origin",
};
// index.php's $noindex: any of these params (non-empty) marks client state.
const STATE_PARAMS = ["q", "sort", "shape", "view", "sheet", "path", "fresh", "interactive", "og"];
const NOINDEX = '<meta name="robots" content="noindex, follow">\n';
const HUBS = routes.hubs; // slug -> category
const CATEGORIES = routes.categories; // category -> slug
const SHEET_FILES = new Set(routes.sheetFiles);
const PATHS = new Set(routes.paths);
const PROVENANCE = new Set(routes.provenance.map((p) => "/" + p));
// WordOps location = /favicon.ico falls back to nginx's empty_gif (43 bytes).
const EMPTY_GIF = Uint8Array.from(atob("R0lGODlhAQABAIABAAAAAP///yH5BAEAAAEALAAAAAABAAEAAAICTAEAOw=="), (c) => c.charCodeAt(0));

function withHeaders(resp, extra = {}) {
  const r = new Response(resp.body, resp);
  for (const [k, v] of Object.entries({ ...SECURITY, ...extra })) r.headers.set(k, v);
  return r;
}

// index.php's redirect_permanent() sent max-age=3600; nginx's own `return 301` sent none.
function redirect(location, cache = "public, max-age=3600") {
  const headers = { location, ...SECURITY };
  if (cache) headers["cache-control"] = cache;
  return new Response(null, { status: 301, headers });
}

async function asset(env, request, path, extra = {}) {
  const url = new URL(request.url);
  url.pathname = path;
  url.search = "";
  const resp = await env.ASSETS.fetch(new Request(url, { method: "GET", headers: request.headers }));
  return withHeaders(resp, resp.status === 200 ? extra : {});
}

async function notFound(env, request) {
  const url = new URL(request.url);
  url.pathname = "/__not_found__";
  const resp = await env.ASSETS.fetch(new Request(url, { headers: request.headers }));
  return withHeaders(resp, { "cache-control": "no-store" });
}

// PHP's $_GET keeps the first occurrence as a string; arrays (a[]=) are not strings.
function q(params, key) {
  const v = params.get(key);
  return v === null ? "" : v.trim();
}

// index.php hub_redirect_url(): the slug plus every other non-empty param, in order,
// encoded like http_build_query (spaces as +).
function hubRedirect(url, slug, drop) {
  const out = new URLSearchParams();
  for (const [k, v] of url.searchParams) if (!drop.includes(k) && v !== "") out.append(k, v);
  const qs = out.toString();
  return redirect(`${url.origin}/${slug}${qs ? "?" + qs : ""}`);
}

function isClientState(params) {
  return STATE_PARAMS.some((k) => q(params, k) !== "");
}

function escapeAttr(s) {
  return s.replace(/&/g, "&amp;").replace(/"/g, "&quot;").replace(/'/g, "&#039;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
}

// Mirror index.php's head for a request state the prerender did not bake in.
function rewriteHead(resp, { noindex, sheet }) {
  if (!noindex && !sheet) return resp;
  let rw = new HTMLRewriter();
  if (noindex) {
    rw = rw.on('link[rel="canonical"]', { element(e) { e.before(NOINDEX, { html: true }); } });
  }
  if (sheet) {
    // index.php: title = clamp_text(sheet title, 58), canonical = base URL + file.
    const title = routes.sheetTitles[sheet];
    const canonical = `https://${ORIGIN_HOST}/${sheet}`;
    rw = rw
      .on("title", { element(e) { e.setInnerContent(title); } })
      .on('meta[property="og:title"], meta[name="twitter:title"]', { element(e) { e.setAttribute("content", title); } })
      .on('link[rel="canonical"]', { element(e) { e.setAttribute("href", canonical); } })
      .on('meta[property="og:url"]', { element(e) { e.setAttribute("content", canonical); } });
  }
  return rw.transform(resp);
}

async function explorer(request, env, url) {
  const p = url.searchParams;
  // Every other spelling of a hub 301s to its slug (index.php, "Hub URLs").
  const hub = q(p, "hub");
  if (hub !== "") {
    if (HUBS[hub]) return hubRedirect(url, hub, ["hub", "cat", "category"]);
    if (/^[a-z0-9][a-z0-9-]*$/.test(hub) && SHEET_FILES.has(hub)) return redirect(`${url.origin}/${hub}.html`);
    return notFound(env, request);
  }
  const cat = q(p, "cat");
  if (cat !== "" && CATEGORIES[cat]) return hubRedirect(url, CATEGORIES[cat], ["cat", "category"]);
  const legacy = q(p, "category");
  if (legacy !== "" && CATEGORIES[legacy]) return hubRedirect(url, CATEGORIES[legacy], ["cat", "category"]);

  // Lens documents the prerender carries separately; everything else is the grid,
  // whose JS applies the filter/sort/lens state from the URL.
  const path = q(p, "path");
  let file = "/_x/index.html";
  if (path !== "" && PATHS.has(path)) file = `/_x/path/${path}.html`;
  else if (q(p, "view") === "paths") file = "/_x/paths.html";
  const resp = await asset(env, request, file, { "cache-control": "public, max-age=300" });
  if (resp.status !== 200 || file !== "/_x/index.html") return resp; // lens pages are noindex already
  const sheet = q(p, "sheet");
  const unknownCat = cat !== "" && !CATEGORIES[cat];
  return rewriteHead(resp, {
    noindex: isClientState(p) || unknownCat,
    sheet: sheet !== "" && routes.sheetTitles[sheet] !== undefined ? sheet : "",
  });
}

async function hubPage(request, env, url, slug) {
  const resp = await asset(env, request, `/_x/hub/${slug}.html`, { "cache-control": "public, max-age=300" });
  // On a hub the category wins over ?sheet= for the head (index.php), so only noindex.
  return rewriteHead(resp, { noindex: isClientState(url.searchParams), sheet: "" });
}

// /history.php[?commit=|?file=] -> the same view on GitHub (spec §2.3).
function history(url) {
  const commit = q(url.searchParams, "commit");
  if (/^[0-9a-f]{4,40}$/i.test(commit)) return redirect(`${GITHUB}/commit/${commit.toLowerCase()}`);
  const file = q(url.searchParams, "file").replace(/\0/g, "");
  if (file && /^[A-Za-z0-9._\/ -]+$/.test(file) && !file.split("/").some((s) => s === "" || s === "." || s === "..")) {
    return redirect(`${GITHUB}/commits/main/${file.split("/").map(encodeURIComponent).join("/")}`);
  }
  return redirect(`${GITHUB}/commits/main/`);
}

export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    const path = url.pathname;

    if (path === "/" || path === "/index.php") return explorer(request, env, url);
    if (path === "/subscribe.php" || path === "/confirm.php") return withHeaders(await env.FORMS.fetch(request));
    if (path === "/history.php") return history(url);
    if (path === "/popularity.php") return asset(env, request, "/_x/popularity.html", { "cache-control": "public, max-age=3600" });
    if (path === "/sitemap.php") {
      return asset(env, request, "/_x/sitemap.xml", { "cache-control": "public, max-age=3600", "content-type": "text/xml; charset=utf-8" });
    }
    if (path === "/favicon.ico") {
      return new Response(EMPTY_GIF, { headers: { "content-type": "image/gif", "cache-control": "max-age=315360000", ...SECURITY } });
    }
    if (PROVENANCE.has(path)) return asset(env, request, path, { "content-type": "text/plain; charset=utf-8" });

    const m = /^\/([a-z0-9][a-z0-9-]*)(\/?)$/.exec(path);
    if (m && HUBS[m[1]]) return m[2] ? redirect(`${url.origin}/${m[1]}`, null) : hubPage(request, env, url, m[1]);

    // Any other .php, /_x/* (build internals) and whatever else reaches here.
    return notFound(env, request);
  },
};
