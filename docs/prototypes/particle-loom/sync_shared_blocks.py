"""Copy the shared blocks (#sm-data, #lessons, #weaver) from weaver-debug.html into learning-test.html.

weaver-debug.html is the source of truth for physics data, lesson scripts and the engine. The gate
(scripts/particle_loom_audit.cjs) fails if learning-test.html carries a different copy.
Usage: python docs/prototypes/particle-loom/sync_shared_blocks.py
"""
import pathlib
import re

HERE = pathlib.Path(__file__).parent
src = (HERE / "weaver-debug.html").read_text(encoding="utf-8")
dst_path = HERE / "learning-test.html"
dst = dst_path.read_text(encoding="utf-8")
for block in ("sm-data", "lessons", "weaver"):
    pat = re.compile(r'(<script[^>]*id="%s">)(.*?)(</script>)' % block, re.S)
    body = pat.search(src).group(2)
    dst, n = pat.subn(lambda m: m.group(1) + body + m.group(3), dst)
    assert n == 1, f"{block}: expected one block in learning-test.html, found {n}"
dst_path.write_text(dst, encoding="utf-8", newline="\n")
print("synced sm-data, lessons, weaver into", dst_path.name)
