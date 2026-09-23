#!/usr/bin/env python3
"""Deterministic core of the page-focused cold outreach program (docs/cold-outreach.md).

The runbook is the spec; this script enforces the parts a machine can check so the agent does not
re-derive them: the email-confidence score (drafts only when > 0.5), dedupe, caps, kill switches,
and the rendering + gating of a ready-to-send HTML email with a plain-text twin.

    python scripts/cold_outreach.py plan                    # JSON: slots, due follow-ups, ready/blocked
    python scripts/cold_outreach.py add prospect.json       # append a prospect (validated, id assigned)
    python scripts/cold_outreach.py score co-0001           # confidence breakdown (fetches evidence, MX)
    python scripts/cold_outreach.py render spec.json        # gate + write HTML/text/payload for gmail_draft.py
    python scripts/cold_outreach.py confirm payload.json created.json   # record a verified Gmail draft
    python scripts/cold_outreach.py record co-0001 key=value [key=value ...]
    python scripts/cold_outreach.py tally                   # markdown tally for log.md

stdlib only. Network use: fetching evidence pages, the live target page, and DNS-over-HTTPS MX
lookups. Every network failure fails closed (the gate refuses; nothing is guessed).
"""
from __future__ import annotations

import argparse
import html
import json
import os
import re
import sys
import urllib.parse
import urllib.request
from datetime import date, datetime, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PAGES = ROOT / "marketing" / "cold-outreach" / "pages.json"
# Prospect names and addresses never enter this repo: it is public on GitHub AND its whole tree is
# served on the live site. Ledger, rendered drafts, and log live in the private cheatsheets-outreach repo.
DATA = Path(os.environ.get("CHEATSHEETS_OUTREACH_DIR", Path.home() / "Projects" / "cheatsheets-outreach"))
PROSPECTS = DATA / "prospects.json"
DRAFTS = DATA / "drafts"
CATALOG = ROOT / "catalog.json"
SITE = "https://cheatsheets.davidveksler.com/"
UA = "Mozilla/5.0 (compatible; cheatsheets-outreach-check/1.0; +https://cheatsheets.davidveksler.com/)"

THRESHOLD = 0.5            # draft only when confidence is strictly greater
MAX_FIRST_TOUCHES = 6      # per run
MAX_FOLLOWUPS = 6          # per run
UNSENT_BACKLOG_CAP = 12    # drafted-but-unsent first touches that stop new drafting
FOLLOWUP_AFTER_DAYS = 7
CLOSE_AFTER_DAYS = 14      # after the follow-up was sent
EVIDENCE_MAX_AGE_DAYS = 30
BOUNCE_STORM = (3, 14)     # 3 bounces within 14 days
DEDUPE_DAYS = 180
CALIBRATION_MIN_SENDS = 4
FIRST_TOUCH_WORDS = 150
FOLLOWUP_WORDS = 90

# Evidence rubric (runbook section 4). The agent records the kind and its sources; the score is
# computed here, never self-reported.
EVIDENCE = {
    "published_personal_own_site": (0.95, "address printed on the prospect's own site"),
    "published_personal_elsewhere": (0.85, "address printed under their name elsewhere (bio, talk page, GitHub, podcast notes)"),
    "published_role_inbox": (0.80, "role inbox (editor@, tips@, webmaster@) printed on the target org's own site"),
    "pattern_multi": (0.70, "name + convention confirmed by >= 2 published addresses on the same domain"),
    "pattern_single": (0.55, "convention inferred from exactly 1 published address on the same domain"),
    "unpublished_generic": (0.40, "unpublished contact@/hello@/info@ guess"),
    "common_pattern_guess": (0.30, "first@ / first.last@ with no convention evidence"),
}
PUBLISHED_KINDS = {"published_personal_own_site", "published_personal_elsewhere", "published_role_inbox"}
PATTERN_KINDS = {"pattern_multi": 2, "pattern_single": 1}
RENDERED_ONLY_PENALTY = 0.25   # seen only in a browser-rendered page; the static fetch cannot confirm it
FREEMAIL = {"gmail.com", "googlemail.com", "outlook.com", "hotmail.com", "yahoo.com", "icloud.com",
            "me.com", "proton.me", "protonmail.com", "aol.com", "gmx.com", "fastmail.com", "hey.com"}
DEAD_LOCALPARTS = re.compile(r"^(no-?reply|do-?not-?reply|mailer-daemon|postmaster|abuse|bounce)", re.I)

SPAM_TERMS = re.compile(r"\b(backlinks?|link exchange|guest post|seo|link juice|domain authority|dofollow|"
                        r"sponsored post|guarantee[d]?|act now|100% free)\b", re.I)
PLACEHOLDER = re.compile(r"(\[VERIFY|\{\{|\}\}|\bTODO\b|\bTBD\b|\bXXX\b|lorem ipsum|<name>|\[name\]|\[first)", re.I)
DASHES = re.compile("[—–]")
URL_RE = re.compile(r"https?://[^\s<>()\"']+[^\s<>()\"'.,;:!?]")
MD_LINK = re.compile(r"\[([^\]\n]+)\]\((https?://[^\s)]+)\)")

SIGNATURE_TEXT = "David Veksler\nhttps://cheatsheets.davidveksler.com/"
FONT = "font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Helvetica,Arial,sans-serif"
LINK_STYLE = "color:#0b57d0;text-decoration:underline"


# ---------------------------------------------------------------- data

def today() -> date:
    return date.today()


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def save_prospects(data: dict) -> None:
    PROSPECTS.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def pages_by_file() -> dict:
    return {p["file"]: p for p in load(PAGES)["pages"]}


def catalog_anchors(file: str) -> set[str]:
    try:
        for s in load(CATALOG)["sheets"]:
            if s.get("file") == file:
                return {h["id"] for h in s.get("headings", []) if h.get("id")}
    except (OSError, KeyError, ValueError):
        pass
    return set()


def d(value) -> date | None:
    if not value:
        return None
    try:
        return date.fromisoformat(str(value)[:10])
    except ValueError:
        return None


def find(data: dict, pid: str) -> dict:
    for p in data["prospects"]:
        if p["id"] == pid:
            return p
    sys.exit(f"no prospect {pid}")


def email_domain(email: str) -> str:
    return email.rsplit("@", 1)[-1].lower().strip()


def dedupe_key(email: str) -> str:
    """Domain for org mailboxes; the full address for freemail and academic hosts (many unrelated people)."""
    dom = email_domain(email)
    if dom in FREEMAIL or dom.endswith(".edu") or ".ac." in dom:
        return email.lower()
    return dom[4:] if dom.startswith("www.") else dom


# ---------------------------------------------------------------- network (fail closed)

def http_get(url: str, timeout: int = 20) -> tuple[int, str]:
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "text/html,*/*"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, r.read(3_000_000).decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        return e.code, ""
    except Exception as e:  # noqa: BLE001 - any transport failure is "unknown", which fails closed
        return 0, f"{type(e).__name__}: {e}"


def mx_status(domain: str) -> str:
    """'mx' | 'a-only' | 'none' | 'error'. Uses Cloudflare DNS-over-HTTPS (no dnspython dependency)."""
    def q(rtype: str):
        url = f"https://cloudflare-dns.com/dns-query?name={urllib.parse.quote(domain)}&type={rtype}"
        req = urllib.request.Request(url, headers={"Accept": "application/dns-json", "User-Agent": UA})
        with urllib.request.urlopen(req, timeout=15) as r:
            return json.loads(r.read().decode())
    try:
        mx = q("MX")
        if mx.get("Status") == 0 and any(a.get("type") == 15 for a in mx.get("Answer", [])):
            return "mx"
        a = q("A")
        if a.get("Status") == 0 and a.get("Answer"):
            return "a-only"
        return "none"
    except Exception:  # noqa: BLE001
        return "error"


def cf_decode(hexstr: str) -> str:
    """Decode a Cloudflare email-protection token (/cdn-cgi/l/email-protection#<hex>)."""
    try:
        key = int(hexstr[:2], 16)
        return "".join(chr(int(hexstr[i:i + 2], 16) ^ key) for i in range(2, len(hexstr), 2))
    except ValueError:
        return ""


def page_has_email(page: str, email: str) -> bool:
    email = email.lower()
    text = html.unescape(page).lower()
    if email in text or f"mailto:{email}" in text:
        return True
    local, dom = email.split("@", 1)
    obf = re.escape(local) + r"\s*(\[at\]|\(at\)|\{at\}|\sat\s)\s*" + re.escape(dom).replace(r"\.", r"\s*(\.|\[dot\]|\(dot\)|\sdot\s)\s*")
    if re.search(obf, text):
        return True
    for token in re.findall(r"email-protection#([0-9a-f]+)", text) + re.findall(r'data-cfemail="([0-9a-f]+)"', text):
        if cf_decode(token).lower() == email:
            return True
    return False


# ---------------------------------------------------------------- scoring

def calibration(prospects: list[dict]) -> dict:
    """Per evidence kind: sends, bounces, and empirical deliverability once there are enough sends."""
    out: dict[str, dict] = {}
    for p in prospects:
        o = p.get("outreach", {})
        if not o.get("sent"):
            continue
        k = p.get("evidence", {}).get("kind", "?")
        c = out.setdefault(k, {"sends": 0, "bounces": 0})
        c["sends"] += 1
        c["bounces"] += 1 if o.get("outcome") == "bounced" else 0
    for c in out.values():
        c["deliverability"] = round((c["sends"] - c["bounces"]) / c["sends"], 2) if c["sends"] >= CALIBRATION_MIN_SENDS else None
    return out


def score(p: dict, prospects: list[dict], *, fetch=http_get, mx=mx_status) -> tuple[float, list[str]]:
    """Return (confidence, reasons). Confidence <= THRESHOLD means no draft."""
    reasons: list[str] = []
    email = (p.get("email") or "").strip()
    ev = p.get("evidence") or {}
    kind = ev.get("kind")
    if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[a-z]{2,}", email, re.I):
        return 0.0, ["no valid address"]
    if DEAD_LOCALPARTS.match(email):
        return 0.0, ["unmonitored mailbox (no-reply/postmaster)"]
    if kind not in EVIDENCE:
        return 0.0, [f"unknown evidence kind {kind!r}; use one of {sorted(EVIDENCE)}"]
    base, label = EVIDENCE[kind]
    reasons.append(f"{kind} = {base} ({label})")
    dom = email_domain(email)

    checked = d(ev.get("checked"))
    if not checked or (today() - checked).days > EVIDENCE_MAX_AGE_DAYS:
        return 0.0, reasons + [f"evidence.checked missing or older than {EVIDENCE_MAX_AGE_DAYS} days; re-verify"]

    if dom in FREEMAIL and kind not in PUBLISHED_KINDS:
        return 0.0, reasons + ["freemail address can only be used when published"]

    if kind in PUBLISHED_KINDS:
        src = ev.get("source_url")
        if not src:
            return 0.0, reasons + ["published kind needs evidence.source_url"]
        status, body = fetch(src)
        if status == 200 and page_has_email(body, email):
            reasons.append("address found on source_url by static fetch")
        elif ev.get("rendered_only"):
            base -= RENDERED_ONLY_PENALTY
            reasons.append(f"not in static HTML (status {status}); rendered_only attested, -{RENDERED_ONLY_PENALTY}")
        else:
            return 0.0, reasons + [f"address not found on source_url (status {status}); if it only appears after "
                                   "JS rendering, set evidence.rendered_only=true"]
    elif kind in PATTERN_KINDS:
        need = PATTERN_KINDS[kind]
        confirmed = 0
        for ex in ev.get("examples") or []:
            ex_email, ex_src = (ex.get("email") or "").lower(), ex.get("source_url")
            if not ex_email or email_domain(ex_email) != dom or ex_email == email.lower() or not ex_src:
                reasons.append(f"example {ex_email or '?'} ignored (other domain, same address, or no source)")
                continue
            status, body = fetch(ex_src)
            if status == 200 and page_has_email(body, ex_email):
                confirmed += 1
            else:
                reasons.append(f"example {ex_email} not found on its source (status {status})")
        reasons.append(f"{confirmed} published example(s) confirmed on {dom}")
        if confirmed < need:
            if kind == "pattern_multi" and confirmed == 1:
                base, kind = EVIDENCE["pattern_single"][0], "pattern_single"
                reasons.append("downgraded to pattern_single = 0.55")
            else:
                return 0.0, reasons + [f"{kind} needs {need} confirmed example(s)"]
        if not p.get("name"):
            return 0.0, reasons + ["pattern evidence requires a named person"]

    m = mx(dom)
    if m == "error":
        return 0.0, reasons + [f"MX lookup for {dom} failed; fail closed, retry later"]
    if m == "none":
        return 0.0, reasons + [f"{dom} has no MX or A record"]
    if m == "a-only":
        base -= 0.15
        reasons.append(f"{dom} has no MX (A-record fallback only), -0.15")
    else:
        reasons.append(f"{dom} has MX")

    cal = calibration(prospects).get(kind, {})
    if cal.get("deliverability") is not None and cal["deliverability"] < base:
        reasons.append(f"calibrated: {kind} delivered {cal['deliverability']} of {cal['sends']} sends, capped")
        base = cal["deliverability"]

    return round(max(base, 0.0), 2), reasons


# ---------------------------------------------------------------- plan

def plan(data: dict, *, with_scores: bool = True) -> dict:
    ps = data["prospects"]
    pages = pages_by_file()
    t = today()

    bounces_recent = [p["id"] for p in ps if p.get("outreach", {}).get("outcome") == "bounced"
                      and (d(p["outreach"].get("bounced")) or d(p["outreach"].get("sent")) or date.min) >= t - timedelta(days=BOUNCE_STORM[1])]
    bounce_storm = len(bounces_recent) >= BOUNCE_STORM[0]
    spam_flag = any(p.get("outreach", {}).get("outcome") == "spam-complaint" for p in ps)

    paused = []
    for f, pg in pages.items():
        sent = [p for p in ps if p.get("page") == f and p.get("outreach", {}).get("sent")]
        replied = [p for p in sent if p["outreach"].get("replied")]
        if len(sent) >= pg.get("kill_after", 12) and not replied:
            paused.append(f)

    unsent = [p["id"] for p in ps if p.get("state") == "drafted" and not p.get("outreach", {}).get("sent")]
    slots = 0 if (bounce_storm or spam_flag) else max(0, min(MAX_FIRST_TOUCHES, UNSENT_BACKLOG_CAP - len(unsent)))

    contacted = {}
    for p in ps:
        o = p.get("outreach", {})
        when = d(o.get("sent")) or d(o.get("drafted"))
        if when and p.get("email"):
            contacted.setdefault(dedupe_key(p["email"]), []).append((p["id"], when))

    ready, blocked = [], []
    for p in sorted((p for p in ps if p.get("state") == "queued"),
                    key=lambda p: (pages.get(p.get("page"), {}).get("priority", 9), p["id"])):
        why = []
        if p.get("page") not in pages:
            why.append("page not in pages.json")
        elif p["page"] in paused:
            why.append("page paused by kill switch")
        for other, when in contacted.get(dedupe_key(p.get("email") or ""), []):
            if other != p["id"] and (t - when).days <= DEDUPE_DAYS:
                why.append(f"dedupe: {other} contacted {when}")
        conf, reasons = score(p, ps) if with_scores and not why else (None, [])
        entry = {"id": p["id"], "org": p.get("org"), "name": p.get("name"), "email": p.get("email"),
                 "page": p.get("page"), "confidence": conf, "reasons": reasons}
        if why or (conf is not None and conf <= THRESHOLD):
            entry["blocked_by"] = why or [f"confidence {conf} <= {THRESHOLD}"]
            blocked.append(entry)
        else:
            ready.append(entry)

    due_followups, to_close = [], []
    for p in ps:
        o = p.get("outreach", {})
        if o.get("replied") or o.get("outcome") in {"bounced", "declined", "live", "spam-complaint"}:
            continue
        sent = d(o.get("sent"))
        if sent and not o.get("followup_drafted") and (t - sent).days >= FOLLOWUP_AFTER_DAYS:
            due_followups.append({"id": p["id"], "email": p.get("email"), "page": p.get("page"),
                                  "thread_id": o.get("thread_id"), "rfc_message_id": o.get("rfc_message_id"),
                                  "sent": o.get("sent")})
        fsent = d(o.get("followup_sent"))
        if fsent and (t - fsent).days >= CLOSE_AFTER_DAYS and p.get("state") != "closed":
            to_close.append(p["id"])

    return {
        "date": t.isoformat(),
        "threshold": THRESHOLD,
        "first_touch_slots": slots,
        "followup_slots": 0 if spam_flag else MAX_FOLLOWUPS,
        "bounce_storm": bounce_storm, "recent_bounces": bounces_recent,
        "spam_complaint": spam_flag,
        "unsent_drafts": unsent,
        "paused_pages": paused,
        "ready_first_touch": ready,
        "blocked": blocked,
        "due_followups": due_followups[:MAX_FOLLOWUPS],
        "to_close": to_close,
        "calibration": calibration(ps),
        "watch_addresses": sorted({p["email"] for p in ps if p.get("outreach", {}).get("drafted") and p.get("email")}),
    }


# ---------------------------------------------------------------- render

def inline_html(text: str) -> str:
    """Escape text, turning [label](url) and bare URLs into anchors."""
    out, pos = [], 0
    tokens = []
    for m in MD_LINK.finditer(text):
        tokens.append((m.start(), m.end(), m.group(1), m.group(2)))
    taken = [(s, e) for s, e, _, _ in tokens]
    for m in URL_RE.finditer(text):
        if not any(s <= m.start() < e for s, e in taken):
            tokens.append((m.start(), m.end(), m.group(0), m.group(0)))
    for s, e, label, url in sorted(tokens):
        out.append(html.escape(text[pos:s]))
        out.append(f'<a href="{html.escape(url, quote=True)}" style="{LINK_STYLE}">{html.escape(label)}</a>')
        pos = e
    out.append(html.escape(text[pos:]))
    return "".join(out)


def blocks(body: str) -> list[tuple[str, list[str]]]:
    """Split the spec body into ('p', [line]) and ('ul', [items]) blocks. Blank line = new block."""
    result = []
    for chunk in re.split(r"\n\s*\n", body.strip()):
        lines = [ln.rstrip() for ln in chunk.strip().splitlines() if ln.strip()]
        if lines and all(ln.lstrip().startswith("- ") for ln in lines):
            result.append(("ul", [ln.lstrip()[2:].strip() for ln in lines]))
        else:
            result.append(("p", [" ".join(ln.strip() for ln in lines)]))
    return result


def to_plain(body: str) -> str:
    parts = []
    for kind, items in blocks(body):
        if kind == "ul":
            parts.append("\n".join(f"- {MD_LINK.sub(lambda m: f'{m.group(1)} ({m.group(2)})', i)}" for i in items))
        else:
            parts.append(MD_LINK.sub(lambda m: f"{m.group(1)} ({m.group(2)})", items[0]))
    return "\n\n".join(parts) + "\n\n" + SIGNATURE_TEXT + "\n"


def to_html_fragment(body: str) -> str:
    p_style = "margin:0 0 14px"
    parts = [f'<div style="{FONT};font-size:15px;line-height:1.55;color:#1f2328;max-width:600px">']
    for kind, items in blocks(body):
        if kind == "ul":
            lis = "".join(f'<li style="margin:0 0 6px">{inline_html(i)}</li>' for i in items)
            parts.append(f'<ul style="margin:0 0 14px;padding-left:22px">{lis}</ul>')
        else:
            parts.append(f'<p style="{p_style}">{inline_html(items[0])}</p>')
    parts.append(f'<p style="margin:20px 0 0">David Veksler<br>'
                 f'<a href="{SITE}" style="{LINK_STYLE}">cheatsheets.davidveksler.com</a></p></div>')
    return "".join(parts)


def to_html_document(subject: str, fragment: str, to: str) -> str:
    return ("<!DOCTYPE html>\n<html lang=\"en\"><head><meta charset=\"utf-8\">"
            "<meta name=\"viewport\" content=\"width=device-width,initial-scale=1\">"
            f"<title>{html.escape(subject)}</title></head>\n"
            f"<body style=\"margin:0;padding:24px 16px;background:#ffffff\">\n"
            f"<!-- To: {html.escape(to)} | Subject: {html.escape(subject)} -->\n{fragment}\n</body></html>\n")


def word_count(body: str) -> int:
    return len(re.findall(r"\b[\w'’-]+\b", MD_LINK.sub(r"\1", URL_RE.sub("", body))))


def gate(spec: dict, p: dict, data: dict, *, fetch=http_get, mx=mx_status, check_live: bool = True) -> list[str]:
    """Return a list of failures; empty means send-ready."""
    errs: list[str] = []
    touch = spec.get("touch", "first")
    body = spec.get("body", "")
    subject = spec.get("subject", "") if touch == "first" else p.get("subject", "")
    page = pages_by_file().get(p.get("page"))
    if not page:
        return [f"prospect page {p.get('page')!r} is not in pages.json"]
    target = SITE + page["file"]
    o = p.get("outreach", {})

    if touch == "first":
        if p.get("state") != "queued":
            errs.append(f"first touch needs state=queued (is {p.get('state')})")
        pl = plan(data, with_scores=False)
        if pl["first_touch_slots"] <= 0:
            errs.append("no first-touch slots (bounce storm, spam complaint, or unsent backlog)")
        if p["page"] in pl["paused_pages"]:
            errs.append("page paused by kill switch")
        if not subject or len(subject) > 60:
            errs.append("subject missing or > 60 chars")
        if subject and (SPAM_TERMS.search(subject) or "!" in subject or subject.isupper()):
            errs.append("subject has spam-trigger wording")
        limit = FIRST_TOUCH_WORDS
    elif touch == "followup":
        if not o.get("sent") or o.get("followup_drafted") or o.get("replied"):
            errs.append("follow-up needs a sent first touch with no reply and no earlier follow-up")
        elif (today() - d(o["sent"])).days < FOLLOWUP_AFTER_DAYS:
            errs.append(f"follow-up not due until {FOLLOWUP_AFTER_DAYS} days after send")
        if not (o.get("thread_id") and o.get("rfc_message_id")):
            errs.append("follow-up needs outreach.thread_id and outreach.rfc_message_id (record them at reconcile)")
        limit = FOLLOWUP_WORDS
    else:
        return [f"unknown touch {touch!r}"]

    conf, reasons = score(p, data["prospects"], fetch=fetch, mx=mx)
    if conf <= THRESHOLD:
        errs.append(f"email confidence {conf} <= {THRESHOLD}: " + "; ".join(reasons[-2:]))

    words = word_count(body)
    if words > limit:
        errs.append(f"body is {words} words (limit {limit})")
    if DASHES.search(body + subject):
        errs.append("em/en dash present (David voice: none)")
    if PLACEHOLDER.search(body + subject):
        errs.append("placeholder text present")
    if SPAM_TERMS.search(body):
        errs.append("spam/SEO jargon in body (backlink, SEO, guest post, ...)")
    if "google.com/url" in body or re.search(r"[?&](utm_|fbclid|gclid)", body):
        errs.append("tracking or Google-wrapped URL in body; use the clean canonical URL")
    if re.search(r"david veksler\s*$", body.strip(), re.I) or "cheatsheets.davidveksler.com/\n" in body[-60:]:
        errs.append("remove the sign-off; the script appends the fixed signature")
    if p.get("name"):
        first = p["name"].split()[0]
        if first.lower() not in body.lower()[:200]:
            errs.append(f"greeting should use the prospect's name ({first})")

    urls = [m.group(2) for m in MD_LINK.finditer(body)]
    urls += [m.group(0) for m in URL_RE.finditer(MD_LINK.sub("", body))]
    ours = [u for u in urls if u.startswith(SITE)]
    if not any(u.split("#")[0] == target for u in ours):
        errs.append(f"body must link the target page {target}")
    if any(u.split("#")[0] != target for u in ours):
        errs.append("only the one target page may be linked (anchors on it are fine)")
    if len(urls) > 2:
        errs.append("at most 2 links in the body")
    anchors = {u.split("#", 1)[1] for u in ours if "#" in u}
    if anchors - catalog_anchors(page["file"]):
        errs.append(f"unknown anchor(s) {sorted(anchors - catalog_anchors(page['file']))}")

    if check_live:
        status, page_html = fetch(target)
        if status != 200:
            errs.append(f"target page returned {status}; not live")
        else:
            for a in anchors:
                if f'id="{a}"' not in page_html and f"id='{a}'" not in page_html:
                    errs.append(f"anchor #{a} not on the live page")
    return errs


def render(spec_path: Path) -> int:
    spec = load(spec_path)
    data = load(PROSPECTS)
    p = find(data, spec["id"])
    errs = gate(spec, p, data)
    if errs:
        print(json.dumps({"ok": False, "id": p["id"], "errors": errs}, indent=2))
        return 1
    touch = spec.get("touch", "first")
    subject = spec["subject"] if touch == "first" else "Re: " + re.sub(r"^re:\s*", "", p["subject"], flags=re.I)
    to = f'{p["name"]} <{p["email"]}>' if p.get("name") else p["email"]
    fragment = to_html_fragment(spec["body"])
    payload = {"to": to, "subject": subject, "body": to_plain(spec["body"]), "htmlBody": fragment,
               "_prospect": p["id"], "_touch": touch, "_expect": SITE + p["page"]}
    if touch == "followup":
        payload["threadId"] = p["outreach"]["thread_id"]
        payload["inReplyTo"] = p["outreach"]["rfc_message_id"]
    out = DRAFTS / today().isoformat()
    out.mkdir(parents=True, exist_ok=True)
    stem = f"{p['id']}-{touch}"
    (out / f"{stem}.html").write_text(to_html_document(subject, fragment, to), encoding="utf-8")
    (out / f"{stem}.txt").write_text(f"To: {to}\nSubject: {subject}\n\n{payload['body']}", encoding="utf-8")
    (out / f"{stem}.payload.json").write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"ok": True, "id": p["id"], "payload": str(out / f"{stem}.payload.json"),
                      "preview": str(out / f"{stem}.html"), "expect": payload["_expect"]}, indent=2))
    return 0


# ---------------------------------------------------------------- ledger writes

REQUIRED_ON_ADD = ("org", "page", "type", "hook_url", "hook_note", "email", "evidence")
TYPES = {"resource-page", "newsletter", "course", "article", "club", "stale-link"}


def add(path: Path) -> int:
    data = load(PROSPECTS)
    new = load(path)
    items = new if isinstance(new, list) else [new]
    pages = pages_by_file()
    n = max([int(p["id"].split("-")[1]) for p in data["prospects"]] or [0])
    added = []
    for item in items:
        missing = [k for k in REQUIRED_ON_ADD if not item.get(k)]
        if missing:
            sys.exit(f"missing {missing} in {item.get('org')}")
        if item["page"] not in pages:
            sys.exit(f"{item['page']} is not a focus page in pages.json")
        if item["type"] not in TYPES:
            sys.exit(f"type must be one of {sorted(TYPES)}")
        if any(p.get("email", "").lower() == item["email"].lower() for p in data["prospects"]):
            print(f"skip duplicate address {item['email']}", file=sys.stderr)
            continue
        n += 1
        item = {"id": f"co-{n:04d}", "state": "queued", "added": today().isoformat(), **item, "outreach": {}}
        data["prospects"].append(item)
        added.append(item["id"])
    save_prospects(data)
    print(json.dumps({"added": added}))
    return 0


STATES = {"queued", "drafted", "sent", "closed", "skipped", "rejected"}
OUTCOMES = {"bounced", "replied", "auto-reply", "declined", "live", "spam-complaint"}


def set_path(obj: dict, key: str, value) -> None:
    parts = key.split(".")
    for part in parts[:-1]:
        obj = obj.setdefault(part, {})
    if value in ("", "null", None):
        obj.pop(parts[-1], None)
    else:
        obj[parts[-1]] = value


def record(pid: str, pairs: list[str]) -> int:
    data = load(PROSPECTS)
    p = find(data, pid)
    for pair in pairs:
        key, _, value = pair.partition("=")
        if key == "state" and value not in STATES:
            sys.exit(f"state must be one of {sorted(STATES)}")
        if key == "outreach.outcome" and value not in OUTCOMES:
            sys.exit(f"outcome must be one of {sorted(OUTCOMES)}")
        if key.startswith("evidence.examples"):
            value = json.loads(value)
        if key == "evidence.rendered_only":
            value = value.lower() == "true"
        if key in {"id", "added"}:
            sys.exit(f"{key} is immutable")
        set_path(p, key, value)
    save_prospects(data)
    print(json.dumps({"id": pid, "state": p.get("state"), "outreach": p.get("outreach")}, ensure_ascii=False))
    return 0


def confirm(payload_path: Path, created_path: Path) -> int:
    """Record a draft that gmail_draft.py created AND verified CLEAN."""
    payload, created = load(payload_path), load(created_path)
    if not (created.get("id") and created.get("messageId") and created.get("threadId")):
        sys.exit("created.json lacks id/messageId/threadId: treat as a failed create")
    data = load(PROSPECTS)
    p = find(data, payload["_prospect"])
    o = p.setdefault("outreach", {})
    if payload["_touch"] == "first":
        p["state"] = "drafted"
        p["subject"] = payload["subject"]
        o.update(drafted=today().isoformat(), draft_id=created["id"], thread_id=created["threadId"])
    else:
        o.update(followup_drafted=today().isoformat(), followup_draft_id=created["id"])
    save_prospects(data)
    print(json.dumps({"id": p["id"], "state": p["state"], "outreach": o}))
    return 0


def tally() -> int:
    data = load(PROSPECTS)
    rows = ["| Page | Queued | Drafted | Sent | Replies | Live links | Bounces |", "|---|---|---|---|---|---|---|"]
    for f in pages_by_file():
        ps = [p for p in data["prospects"] if p.get("page") == f]
        o = [p.get("outreach", {}) for p in ps]
        rows.append(f"| {f} | {sum(p.get('state') == 'queued' for p in ps)} | {sum(bool(x.get('drafted')) for x in o)} | "
                    f"{sum(bool(x.get('sent')) for x in o)} | {sum(bool(x.get('replied')) for x in o)} | "
                    f"{sum(x.get('outcome') == 'live' for x in o)} | {sum(x.get('outcome') == 'bounced' for x in o)} |")
    cal = calibration(data["prospects"])
    rows += ["", "| Evidence kind | Base | Sends | Bounces | Delivered |", "|---|---|---|---|---|"]
    for k, (base, _) in EVIDENCE.items():
        c = cal.get(k, {"sends": 0, "bounces": 0, "deliverability": None})
        rows.append(f"| {k} | {base} | {c['sends']} | {c['bounces']} | {c['deliverability'] if c['deliverability'] is not None else '-'} |")
    print("\n".join(rows))
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("plan")
    sub.add_parser("tally")
    sub.add_parser("add").add_argument("file", type=Path)
    sub.add_parser("score").add_argument("id")
    sub.add_parser("render").add_argument("spec", type=Path)
    c = sub.add_parser("confirm")
    c.add_argument("payload", type=Path)
    c.add_argument("created", type=Path)
    r = sub.add_parser("record")
    r.add_argument("id")
    r.add_argument("pairs", nargs="+")
    a = ap.parse_args(argv)
    if not PROSPECTS.is_file():
        sys.exit(f"ledger not found at {PROSPECTS}; clone the private cheatsheets-outreach repo there "
                 "or set CHEATSHEETS_OUTREACH_DIR. Never create it inside this public repo.")
    if ROOT in PROSPECTS.resolve().parents:
        sys.exit("refusing: the ledger must not live inside the public CheatSheets repo")
    if a.cmd == "plan":
        print(json.dumps(plan(load(PROSPECTS)), indent=2, ensure_ascii=False))
        return 0
    if a.cmd == "score":
        data = load(PROSPECTS)
        conf, reasons = score(find(data, a.id), data["prospects"])
        print(json.dumps({"id": a.id, "confidence": conf, "draftable": conf > THRESHOLD, "reasons": reasons}, indent=2))
        return 0 if conf > THRESHOLD else 1
    return {"tally": lambda: tally(), "add": lambda: add(a.file), "render": lambda: render(a.spec),
            "confirm": lambda: confirm(a.payload, a.created), "record": lambda: record(a.id, a.pairs)}[a.cmd]()


if __name__ == "__main__":
    sys.exit(main())
