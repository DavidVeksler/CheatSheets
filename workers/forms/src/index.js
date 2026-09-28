/**
 * Newsletter forms Worker for cheatsheets.davidveksler.com: replaces subscribe.php
 * and confirm.php (double opt-in, docs/newsletter.md §2.3). The site Worker hands
 * it /subscribe, /subscribe.php and /confirm through a service binding (the public
 * URLs dropped .php on 2026-09-28; the site Worker 301s /confirm.php to /confirm).
 *
 * Shape from cf-static-kit/templates/contact-worker (D1 log, per-IP rate limit that
 * fails open, ?health=1, JSON for fetch() callers vs a page for plain posts); the
 * contract (fields, token format, messages, status codes, pages, email text) is
 * the PHP one, so the signup forms and every confirm link already sent keep working.
 *
 *   POST /subscribe          email (+ honeypot "website") -> intake row, confirmation email
 *   GET  /subscribe?health=1                              -> 200/503 JSON, booleans only
 *   GET  /confirm?p=&s=      HMAC token, 7-day TTL        -> confirmed row, page
 * The .php spellings are still answered, so deploy order against the site Worker
 * does not matter and a form cached before the rename still posts.
 *
 * Secrets (wrangler secret put, never in files): NEWSLETTER_TOKEN_SECRET,
 * RESEND_SENDING_KEY, CHEATSHEET_NOTIFY_EMAIL (optional), IP_HASH_SALT (optional).
 * Vars: NEWSLETTER_FROM_ADDRESS, NEWSLETTER_REPLY_TO (optional).
 * Never logs an email address.
 */
import { MSG, confirmPage, confirmationEmail, subscribePage } from "./pages.js";

const TOKEN_TTL = 7 * 24 * 60 * 60;
const HONEYPOT = "website";
const DEFAULT_FROM = "Cheatsheets <hello@updates.cheatsheets.davidveksler.com>";
const RATE = { max: 10, windowSeconds: 3600 };

// ------------------------------------------------------------------ helpers --
const enc = new TextEncoder();

function b64urlEncode(bytes) {
  let bin = "";
  for (const b of bytes) bin += String.fromCharCode(b);
  return btoa(bin).replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/, "");
}

// PHP base64_decode($s, strict: true) after the -_ -> +/ swap: null on bad input.
function b64urlDecode(s) {
  if (!/^[A-Za-z0-9_-]*$/.test(s)) return null;
  const pad = s.length % 4;
  if (pad === 1) return null;
  try {
    const bin = atob(s.replace(/-/g, "+").replace(/_/g, "/") + "=".repeat(pad ? 4 - pad : 0));
    return Uint8Array.from(bin, (c) => c.charCodeAt(0));
  } catch {
    return null;
  }
}

async function hmacB64url(payload, secret) {
  const key = await crypto.subtle.importKey("raw", enc.encode(secret), { name: "HMAC", hash: "SHA-256" }, false, ["sign"]);
  return b64urlEncode(new Uint8Array(await crypto.subtle.sign("HMAC", key, enc.encode(payload))));
}

function timingSafeEqual(a, b) {
  const x = enc.encode(a), y = enc.encode(b);
  let diff = x.length ^ y.length;
  for (let i = 0; i < Math.max(x.length, y.length); i++) diff |= (x[i] ?? 0) ^ (y[i] ?? 0);
  return diff === 0;
}

// FILTER_VALIDATE_EMAIL (no unicode flag): dot-atom local part <= 64, a domain of
// LDH labels with at least one dot, total <= 254 (subscribe.php's own cap).
const LOCAL = /^[A-Za-z0-9!#$%&'*+\/=?^_`{|}~-]+(?:\.[A-Za-z0-9!#$%&'*+\/=?^_`{|}~-]+)*$/;
const LABEL = /^[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?$/;
export function validEmail(s) {
  if (typeof s !== "string" || s.length > 254 || /[\s\x00-\x1f\x7f]/.test(s)) return false;
  const at = s.lastIndexOf("@");
  if (at < 1) return false;
  const local = s.slice(0, at), domain = s.slice(at + 1);
  if (local.length > 64 || !LOCAL.test(local)) return false;
  const labels = domain.split(".");
  return labels.length >= 2 && domain.length <= 253 && labels.every((l) => LABEL.test(l));
}

// PHP gmdate('c'): 2026-09-12T01:27:00+00:00
function gmdateC(d = new Date()) {
  return d.toISOString().replace(/\.\d{3}Z$/, "+00:00");
}

export async function mintToken(email, secret, now = Math.floor(Date.now() / 1000)) {
  const p = `${b64urlEncode(enc.encode(email))}.${now}`;
  return { p, s: await hmacB64url(p, secret) };
}

// lib/newsletter.php newsletter_verify_token(): the email, or null on any failure.
export async function verifyToken(payload, sig, secret, now = Math.floor(Date.now() / 1000)) {
  if (!timingSafeEqual(await hmacB64url(payload, secret), sig)) return null;
  const dot = payload.indexOf(".");
  if (dot < 0) return null;
  const encEmail = payload.slice(0, dot), ts = payload.slice(dot + 1);
  if (!/^[0-9]+$/.test(ts) || now - Number(ts) > TOKEN_TTL) return null;
  const bytes = b64urlDecode(encEmail);
  if (!bytes) return null;
  const email = new TextDecoder().decode(bytes);
  return validEmail(email) ? email : null;
}

function wantsJson(req) {
  return (req.headers.get("accept") || "").toLowerCase().includes("application/json") || !!req.headers.get("x-requested-with");
}

const NO_STORE = { "cache-control": "no-store" };

// subscribe.php respond()
function respond(req, ok, msg, status = 200) {
  if (wantsJson(req)) {
    return new Response(JSON.stringify(ok ? { ok: true, message: msg } : { ok: false, error: msg }), {
      status, headers: { "content-type": "application/json; charset=utf-8", ...NO_STORE },
    });
  }
  return new Response(subscribePage(ok, msg), { status, headers: { "content-type": "text/html; charset=utf-8", ...NO_STORE } });
}

function page(ok, heading, body) {
  return new Response(confirmPage(ok, heading, body), {
    status: ok ? 200 : 400, headers: { "content-type": "text/html; charset=utf-8", ...NO_STORE },
  });
}

async function ipHash(req, env) {
  const ip = req.headers.get("cf-connecting-ip") || "0.0.0.0";
  const digest = await crypto.subtle.digest("SHA-256", enc.encode(`${env.IP_HASH_SALT || "cheatsheets"}|${ip}`));
  return [...new Uint8Array(digest)].slice(0, 12).map((b) => b.toString(16).padStart(2, "0")).join("");
}

// Kit template limiter: fixed window per hashed IP, fails open on D1 errors.
async function rateLimited(env, hash) {
  const since = Math.floor(Date.now() / 1000) - RATE.windowSeconds;
  try {
    await env.DB.prepare("INSERT INTO hits (ts, ip_hash, kind) VALUES (unixepoch(), ?, 'subscribe')").bind(hash).run();
    const row = await env.DB.prepare("SELECT COUNT(*) AS n FROM hits WHERE ip_hash = ? AND kind = 'subscribe' AND ts > ?")
      .bind(hash, since).first();
    if (Math.random() < 0.05) await env.DB.prepare("DELETE FROM hits WHERE ts < unixepoch() - 86400").run();
    return (row?.n ?? 0) > RATE.max;
  } catch (e) {
    console.error("rate limit check failed, allowing", String(e));
    return false;
  }
}

async function resendSend(env, message) {
  const body = Object.fromEntries(Object.entries(message).filter(([, v]) => v !== undefined && v !== null && v !== ""));
  try {
    const res = await fetch(env.RESEND_API_BASE || "https://api.resend.com/emails", {
      method: "POST",
      headers: { authorization: `Bearer ${env.RESEND_SENDING_KEY}`, "content-type": "application/json" },
      body: JSON.stringify(body),
    });
    const out = await res.json().catch(() => null);
    if (res.ok && out && out.id) return { ok: true };
    return { ok: false, error: (out && out.message) || `HTTP ${res.status}` };
  } catch (e) {
    return { ok: false, error: "fetch: " + String(e) };
  }
}

// ---------------------------------------------------------------- handlers --
async function health(env) {
  let db = false;
  try { db = !!(await env.DB.prepare("SELECT COUNT(*) AS n FROM confirmed").first()); } catch {}
  const out = { ok: db && !!env.NEWSLETTER_TOKEN_SECRET && !!env.RESEND_SENDING_KEY, store: db ? "writable" : "unwritable",
    token_secret: !!env.NEWSLETTER_TOKEN_SECRET, sending_key: !!env.RESEND_SENDING_KEY, notify: !!env.CHEATSHEET_NOTIFY_EMAIL };
  return new Response(JSON.stringify(out), { status: out.ok ? 200 : 503, headers: { "content-type": "application/json; charset=utf-8", ...NO_STORE } });
}

async function subscribe(req, env, ctx) {
  const url = new URL(req.url);
  if (req.method === "GET" && url.searchParams.has("health")) return health(env);
  if (req.method !== "POST") return respond(req, false, MSG.methodNotAllowed, 405);
  // Fail closed: no path to a confirmed subscriber without both (docs/newsletter.md §5/§9).
  if (!env.NEWSLETTER_TOKEN_SECRET || !env.RESEND_SENDING_KEY) return respond(req, false, MSG.unavailable, 503);

  let form = null;
  try { form = await req.formData(); } catch {}
  const field = (k) => ((form && form.get(k)) ?? "").toString();
  // PHP !empty(): "0" counts as empty too.
  if (field(HONEYPOT) !== "" && field(HONEYPOT) !== "0") return respond(req, true, MSG.thanks);

  if (await rateLimited(env, await ipHash(req, env))) return respond(req, false, MSG.rateLimited, 429);

  const email = field("email").trim();
  if (!validEmail(email)) return respond(req, false, MSG.badEmail, 422);

  // Intake/audit row, best effort (subscribe.php appended .subscribers.jsonl the same way).
  try {
    await env.DB.prepare("INSERT INTO subscribers (ts, email, src) VALUES (?, ?, ?)")
      .bind(gmdateC(), email, (req.headers.get("referer") || "").slice(0, 200)).run();
  } catch (e) {
    console.error("intake write failed", String(e));
  }

  const token = await mintToken(email, env.NEWSLETTER_TOKEN_SECRET);
  const host = (url.host || "cheatsheets.davidveksler.com").replace(/[^a-z0-9.\-:]/gi, "");
  const confirmUrl = `${url.protocol}//${host}/confirm?p=${encodeURIComponent(token.p)}&s=${encodeURIComponent(token.s)}`;
  const mail = confirmationEmail(confirmUrl);
  const from = env.NEWSLETTER_FROM_ADDRESS || DEFAULT_FROM;
  const sent = await resendSend(env, { from, to: email, subject: "Confirm your subscription", html: mail.html, text: mail.text, reply_to: env.NEWSLETTER_REPLY_TO });

  // Owner heads-up regardless of the send outcome. PHP used the droplet's mail();
  // here it goes through Resend from the sending domain.
  const notify = env.CHEATSHEET_NOTIFY_EMAIL;
  if (notify && validEmail(notify)) {
    const status = sent.ok ? "confirmation sent" : `confirmation FAILED: ${sent.error}`;
    ctx.waitUntil(resendSend(env, { from, to: notify, reply_to: email, subject: "New cheatsheet subscriber",
      text: `New signup attempt: ${email}\nWhen: ${gmdateC()}\nStatus: ${status}\n` }));
  }
  if (!sent.ok) {
    console.error("confirmation send failed", sent.error);
    return respond(req, false, MSG.sendFailed, 502);
  }
  return respond(req, true, MSG.thanks);
}

async function confirm(req, env) {
  if (!env.NEWSLETTER_TOKEN_SECRET) {
    return page(false, "Signup error", "Newsletter confirmation is not configured right now. Please try again later.");
  }
  const params = new URL(req.url).searchParams;
  const p = params.get("p") ?? "", s = params.get("s") ?? "";
  if (p === "" || s === "") return page(false, "Invalid link", "This confirmation link is missing its token.");
  const email = await verifyToken(p, s, env.NEWSLETTER_TOKEN_SECRET);
  if (email === null) {
    return page(false, "Link expired or invalid", "This confirmation link is no longer valid. Sign up again on the homepage to get a new one.");
  }
  // Unique on email (NOCASE): re-confirming is a silent no-op, as in confirm.php.
  try {
    await env.DB.prepare("INSERT OR IGNORE INTO confirmed (ts, email) VALUES (?, ?)").bind(gmdateC(), email).run();
  } catch (e) {
    console.error("confirmed write failed", String(e));
  }
  return page(true, "Subscribed", "You're confirmed. You'll get an email when a new reference ships or the pipeline changes — no spam, unsubscribe anytime.");
}

export default {
  async fetch(req, env, ctx) {
    const path = new URL(req.url).pathname;
    if (path === "/subscribe" || path === "/subscribe.php") return subscribe(req, env, ctx);
    if (path === "/confirm" || path === "/confirm.php") return confirm(req, env);
    return new Response("Not found", { status: 404 });
  },
};
