#!/usr/bin/env python3
"""Copy the newsletter secrets from the droplet's .newsletter.env into the forms Worker.

    python3 scripts/newsletter_secrets_to_worker.py           # put the secrets
    python3 scripts/newsletter_secrets_to_worker.py --check   # names present on the Worker?

Reads /var/www/cheatsheets.davidveksler.com/htdocs/.newsletter.env over ssh
(`sudo -n cat`, read-only; the file is www-data 600) into memory and pipes each
value into `wrangler secret put` on stdin. Values are never printed, logged or
written to disk; output names keys only. Spec: docs/specs/cloudflare-migration.md §2.4.

Deploy token: CLOUDFLARE_API_TOKEN from ~/Projects/.cloudflare.env (or the environment).
If the Worker's latest version is only uploaded, not deployed, `secret put` refuses;
this falls back to `versions secret put` (cf-static-kit runbook §4.3).
"""
from __future__ import annotations

import argparse
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FORMS = ROOT / "workers" / "forms"
SSH = os.environ.get("CS_SSH", "johngalt@198.211.102.9")
ENV_FILE = "/var/www/cheatsheets.davidveksler.com/htdocs/.newsletter.env"
# RESEND_SEGMENT_ID stays out: only scripts/newsletter_sync.py uses it, from ~/Projects/.resend.env.
KEYS = ["NEWSLETTER_TOKEN_SECRET", "RESEND_SENDING_KEY", "CHEATSHEET_NOTIFY_EMAIL"]
OPTIONAL_VARS = ["NEWSLETTER_REPLY_TO", "NEWSLETTER_FROM_ADDRESS"]


def wrangler() -> list[str]:
    js = ROOT / "node_modules" / "wrangler" / "bin" / "wrangler.js"
    node = shutil.which("node")
    if not js.is_file() or not node:
        sys.exit("node or wrangler missing; run npm ci")
    return [node, str(js)]


def token_env() -> dict:
    env = dict(os.environ)
    if not env.get("CLOUDFLARE_API_TOKEN"):
        cf = Path.home() / "Projects" / ".cloudflare.env"
        m = re.search(r"^CLOUDFLARE_API_TOKEN=(\S+)", cf.read_text(encoding="utf-8"), re.M) if cf.is_file() else None
        if not m:
            sys.exit("no CLOUDFLARE_API_TOKEN")
        env["CLOUDFLARE_API_TOKEN"] = m.group(1)
    return env


def read_droplet_env() -> dict:
    r = subprocess.run(["ssh", "-o", "BatchMode=yes", "-o", "ConnectTimeout=15", SSH, f"sudo -n cat {ENV_FILE}"],
                       capture_output=True, text=True, encoding="utf-8")
    if r.returncode != 0:
        sys.exit(f"ssh read of {ENV_FILE} failed (exit {r.returncode}); nothing changed")
    out = {}
    for line in r.stdout.splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)  # lib/env.php load_local_env_file()
        out[k.strip()] = v.strip().strip("\"'")
    return out


def secret_names(env: dict) -> set:
    r = subprocess.run(wrangler() + ["secret", "list", "--format", "json"], cwd=FORMS, env=env,
                       capture_output=True, text=True, encoding="utf-8")
    return set(re.findall(r'"name":\s*"([A-Z0-9_]+)"', r.stdout))


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--check", action="store_true", help="only report which secret names exist")
    a = ap.parse_args()
    env = token_env()
    if a.check:
        have = secret_names(env)
        for k in KEYS:
            print(f"  {k}: {'present' if k in have else 'MISSING'}")
        return 0 if all(k in have for k in KEYS) else 1

    values = read_droplet_env()
    missing = [k for k in KEYS if not values.get(k)]
    if missing:
        sys.exit(f"droplet .newsletter.env lacks {missing}; nothing changed")
    extra = [k for k in OPTIONAL_VARS if values.get(k)]
    if extra:
        print(f"  note: droplet also sets {extra}; set them as vars in workers/forms/wrangler.jsonc if they differ")
    failed = False
    for k in KEYS:
        for cmd in (["secret", "put", k], ["versions", "secret", "put", k]):
            r = subprocess.run(wrangler() + cmd, cwd=FORMS, env=env, input=values[k],  # no newline: it would become part of the secret
                               capture_output=True, text=True, encoding="utf-8")
            if r.returncode == 0:
                print(f"  {k}: set ({' '.join(cmd[:-1])})")
                break
        else:
            failed = True
            # wrangler's error text never contains the value (it came in on stdin).
            tail = [ln for ln in (r.stderr or r.stdout).splitlines() if ln.strip()][-2:]
            print(f"  {k}: FAILED: {' | '.join(tail)}", file=sys.stderr)
    values.clear()
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
