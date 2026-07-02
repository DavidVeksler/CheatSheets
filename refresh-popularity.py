#!/usr/bin/env python3
"""
Manually refresh popularity.json on this server, outside the nightly
GitHub Actions schedule (.github/workflows/update-popularity.yml).

Loads CLOUDFLARE_API_TOKEN from .cloudflare.env (gitignored, see
.gitignore) if it isn't already set in the environment, runs
fetch-popularity.py, and — if popularity.json changed — commits and
pushes it to origin/main so this server, GitHub, and the nightly
`git pull --ff-only` cron job (cheatsheets-pull.sh) all stay in sync.

Setup (one-time): create .cloudflare.env next to this script with:
  CLOUDFLARE_API_TOKEN=your-token-here

Usage:
  python3 refresh-popularity.py
"""
import os
import subprocess
import sys

REPO_DIR = os.path.dirname(os.path.abspath(__file__))
ENV_FILE = os.path.join(REPO_DIR, ".cloudflare.env")
FETCH_SCRIPT = os.path.join(REPO_DIR, "fetch-popularity.py")


def load_env_file(path: str) -> None:
    """Populate os.environ from a simple KEY=VALUE file, without overriding vars already set."""
    if not os.path.exists(path):
        return
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, value = line.partition("=")
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            os.environ.setdefault(key, value)


def run(cmd: list[str]) -> str:
    result = subprocess.run(cmd, cwd=REPO_DIR, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"{' '.join(cmd)} failed:\n{result.stdout}{result.stderr}")
    return result.stdout


def main() -> None:
    load_env_file(ENV_FILE)

    if not os.environ.get("CLOUDFLARE_API_TOKEN"):
        print(
            f"ERROR: CLOUDFLARE_API_TOKEN is not set.\n"
            f"Put it in {ENV_FILE} (CLOUDFLARE_API_TOKEN=...) or export it before running.",
            file=sys.stderr,
        )
        sys.exit(1)

    print("Running fetch-popularity.py…")
    fetch_result = subprocess.run([sys.executable, FETCH_SCRIPT], cwd=REPO_DIR)
    if fetch_result.returncode != 0:
        print("fetch-popularity.py failed — aborting, not touching git.", file=sys.stderr)
        sys.exit(fetch_result.returncode)

    status = run(["git", "status", "--porcelain", "--", "popularity.json"])
    if not status.strip():
        print("popularity.json unchanged (already up to date today) — nothing to commit.")
        return

    print("Committing and pushing popularity.json…")
    run(["git", "add", "popularity.json"])
    run(["git", "commit", "-m", "chore: manual popularity refresh [skip ci]"])
    run(["git", "push", "origin", "HEAD:main"])
    print("Done — popularity.json updated and pushed to origin/main.")


if __name__ == "__main__":
    main()
