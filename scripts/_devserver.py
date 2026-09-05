"""Shared helper: start `php -S 127.0.0.1:<port>` from the repo root and wait
for it to accept connections. Used by scripts/render_og_map.py and
scripts/shot_index.py so the two headless-Chromium tools that both need a
live index.php don't duplicate the same subprocess/poll logic.
"""

from __future__ import annotations

import shutil
import socket
import subprocess
import sys
import time
from pathlib import Path


def serve_php(root: Path, port: int, timeout: float = 10.0) -> subprocess.Popen:
    php = shutil.which("php")
    if not php:
        print("php is not on PATH; needed to serve index.php locally.", file=sys.stderr)
        sys.exit(1)
    proc = subprocess.Popen(
        [php, "-S", f"127.0.0.1:{port}"],
        cwd=str(root),
        stdout=subprocess.DEVNULL,
        stderr=subprocess.PIPE,
        text=True,
    )
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            with socket.create_connection(("127.0.0.1", port), timeout=0.3):
                return proc
        except OSError:
            time.sleep(0.1)
    proc.terminate()
    print(f"php -S did not come up on port {port} within {timeout}s", file=sys.stderr)
    sys.exit(1)


def stop_php(proc: subprocess.Popen) -> None:
    proc.terminate()
    try:
        proc.wait(timeout=5)
    except subprocess.TimeoutExpired:
        proc.kill()
