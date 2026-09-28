#!/usr/bin/env python3
"""Shared access to the newsletter's D1 database (forms Worker, workers/forms/).

`cheatsheets-davidveksler-com-forms` holds subscribers' email addresses, so:
never print rows; callers report counts. `redact()` scrubs addresses out of any
tool output before it is shown. Queries run `wrangler d1 execute --remote --json`
from workers/forms/ (its config pins account_id and the database id) with the
D1-only token CLOUDFLARE_D1_TOKEN from ~/Projects/.cloudflare.env.
Used by scripts/import_subscribers.py and scripts/newsletter_sync.py. Stdlib only.
"""
from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FORMS_DIR = ROOT / "workers" / "forms"
DB = "cheatsheets-davidveksler-com-forms"
CF_ENV = Path.home() / "Projects" / ".cloudflare.env"
EMAIL = re.compile(r"[\w.+'!#$%&*/=?^`{|}~-]+@[\w-]+(?:\.[\w-]+)+")


class D1Error(RuntimeError):
    pass


def redact(text: str) -> str:
    return EMAIL.sub("<email>", text or "")


def _token() -> str:
    if os.environ.get("CLOUDFLARE_D1_TOKEN"):
        return os.environ["CLOUDFLARE_D1_TOKEN"]
    if not CF_ENV.is_file():
        raise D1Error(f"missing {CF_ENV}")
    m = re.search(r"^CLOUDFLARE_D1_TOKEN=(\S+)", CF_ENV.read_text(encoding="utf-8"), re.M)
    if not m:
        raise D1Error(f"no CLOUDFLARE_D1_TOKEN in {CF_ENV}")
    return m.group(1)


def _wrangler() -> list[str]:
    js = ROOT / "node_modules" / "wrangler" / "bin" / "wrangler.js"
    node = shutil.which("node")
    if not js.is_file() or not node:
        raise D1Error(f"node or wrangler missing; run npm ci in {ROOT}")
    return [node, str(js)]


def execute(command: str | None = None, statements: list[str] | None = None) -> list[dict]:
    """Run SQL remotely; return the result rows of the last statement. Rows may hold
    addresses: keep them in memory. Error text is redacted."""
    env = dict(os.environ, CLOUDFLARE_API_TOKEN=_token())
    args = _wrangler() + ["d1", "execute", DB, "--remote", "--json"]
    tmpdir = None
    try:
        if statements is not None:
            tmpdir = tempfile.mkdtemp(prefix="cs-d1-")
            path = Path(tmpdir) / "batch.sql"
            path.write_text("\n".join(statements) + "\n", encoding="utf-8")
            args += ["--file", str(path), "--yes"]
        else:
            args += ["--command", command]
        res = subprocess.run(args, cwd=FORMS_DIR, env=env, capture_output=True, text=True,
                             encoding="utf-8", errors="replace")
    finally:
        if tmpdir:
            shutil.rmtree(tmpdir, ignore_errors=True)
    out = res.stdout.strip()
    try:
        data = json.loads(out[out.index("["):]) if "[" in out else None
    except ValueError:
        data = None
    if res.returncode != 0 or not isinstance(data, list) or not all(r.get("success", False) for r in data):
        tail = (res.stderr or out).strip().splitlines()[-3:]
        raise D1Error("wrangler d1 execute failed: " + redact(" | ".join(tail)))
    return data[-1].get("results", []) if data else []


def sql_str(s) -> str:
    return "NULL" if s is None else "'" + str(s).replace("'", "''") + "'"
