// reddit-extract.js — DOM extractor for the cheatsheets-reddit-daily-drafts routine.
//
// Injected (via the browser tool's javascript_tool) into an OLD.REDDIT search results
// page already loaded in David's logged-in Chrome. Returns scored, structured thread
// candidates as JSON text. READ-ONLY: it only reads the DOM, never clicks or posts.
//
// Why the browser and not an API: Reddit blocks unauthenticated JSON (403) and is not
// issuing "script" OAuth apps, so discovery runs by reading search pages in a real
// logged-in session. Binding spec: docs/reddit-daily-drafts.md.
//
// IMPORTANT: the browser tool blocks any javascript_tool result that looks like it
// contains cookie/query-string data. So this returns RELATIVE paths with the "?query"
// stripped and never echoes location.href. Rebuild the full thread URL as
// "https://www.reddit.com" + path in the routine. Selectors verified on live
// old.reddit 2026-07 (.search-result-link layout).
//
// Usage from the routine, per target subreddit:
//   1. navigate to
//      https://old.reddit.com/r/<sub>/search/?q=<OR-terms>&restrict_sr=1&sort=new&t=week
//   2. javascript_tool: paste this whole IIFE; parse the returned JSON.

(() => {
  const QW = ["how", "what", "which", "why", "where", "when", "who", "should i",
    "help", "recommend", "beginner", "vs", "compare", "best", "?"];
  const SKIP = ["megathread", "daily thread", "weekly thread", "[meta]", "wts", "wtb", "for sale"];
  const now = Date.now();

  const results = [...document.querySelectorAll(".search-result-link")].map((el) => {
    const a = el.querySelector("a.search-title, a.title");
    const title = (a?.innerText || "").trim();
    // Relative path, query string removed — required to pass the browser-tool guardrail.
    const path = (a?.getAttribute("href") || "").split("?")[0].replace(/^https?:\/\/[^/]+/, "");
    const iso = el.querySelector("time")?.getAttribute("datetime") || null;
    const ts = iso ? Date.parse(iso) : NaN;
    const ageH = isFinite(ts) ? Math.max(0, (now - ts) / 3.6e6) : null;
    const comments = parseInt(((el.querySelector(".search-comments")?.innerText) || "").match(/\d+/)?.[0] || "0", 10);
    const tl = title.toLowerCase();

    let score = 0;
    if (QW.some((q) => tl.includes(q))) score += 15;      // a question invites an answer
    if (ageH != null && ageH < 24) score += 12;
    else if (ageH != null && ageH < 72) score += 6;
    else if (ageH != null && ageH < 168) score += 2;
    if (comments < 5) score += 8;                          // low-traffic: an answer is seen
    else if (comments < 20) score += 3;

    return { title, path, age_hours: ageH == null ? null : Math.round(ageH * 10) / 10, comments, score };
  }).filter((r) => r.title && !SKIP.some((s) => r.title.toLowerCase().includes(s)));

  results.sort((a, b) => b.score - a.score);
  return JSON.stringify({ count: results.length, results: results.slice(0, 8) }, null, 2);
})();
