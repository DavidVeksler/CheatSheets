#!/usr/bin/env python3
"""Shared helpers for the newsletter pipeline scripts (Phase 2 of docs/newsletter.md).

Stdlib only. The full-access RESEND_API_KEY lives in ~/Projects/.resend.env
(central env file per the fleet convention — see refresh-popularity.py's
.cloudflare.env for the same pattern) and never runs on the web server; the
web server's subscribe.php uses a separate, send-scoped RESEND_SENDING_KEY.
See docs/newsletter.md §2.2.
"""
from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any, Dict, Optional

REPO_DIR = Path(__file__).resolve().parent.parent
ENV_FILE = Path(os.path.expanduser("~/Projects/.resend.env"))
RESEND_API_BASE = "https://api.resend.com"


def load_env_file(path: Path = ENV_FILE) -> None:
    """Populate os.environ from a simple KEY=VALUE file, without overriding vars already set."""
    if not path.exists():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


def resend_api_key() -> str:
    load_env_file()
    key = os.environ.get("RESEND_API_KEY", "").strip()
    if not key:
        raise SystemExit(
            f"ERROR: RESEND_API_KEY is not set.\n"
            f"Put it in {ENV_FILE} (RESEND_API_KEY=re_...) or export it before running.\n"
            f"This must be the full-access key — never RESEND_SENDING_KEY (that one only sends)."
        )
    return key


def resend_request(method: str, path: str, payload: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Minimal Resend API call. Raises RuntimeError with the response body on any non-2xx."""
    key = resend_api_key()
    url = f"{RESEND_API_BASE}{path}"
    data = json.dumps(payload).encode("utf-8") if payload is not None else None
    req = urllib.request.Request(url, data=data, method=method)
    req.add_header("Authorization", f"Bearer {key}")
    req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            body = resp.read().decode("utf-8")
            return json.loads(body) if body else {}
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"Resend {method} {path} -> HTTP {exc.code}: {body}") from exc


def newsletter_dir() -> Path:
    d = REPO_DIR / "newsletter"
    d.mkdir(exist_ok=True)
    return d
