# Content quick path — add / edit / publish a cheatsheet

Front-to-back index for producing content. This is a thin router: the binding
rules live in [`../AGENTS.md`](../AGENTS.md) and [`../TODO/README.md`](../TODO/README.md).
Where this file and AGENTS.md disagree, AGENTS.md wins.

## Where content lives

- **Cheatsheets** are standalone `.html` files in the **repo root** (lowercase, hyphens,
  e.g. `linux-server-hardening.html`). Each is fully self-contained (embedded CSS/JS).
- **Specs** for planned pages live one-per-file in [`../TODO/`](../TODO) as `<topic>.md`,
  deleted after the build ships.
- `index.php` (gallery) and `sitemap.php` auto-discover root `.html`; `images/{filename}.png`
  holds the 1200x630 preview. There is **no build step**.

## Create a cheatsheet (summary — full steps in AGENTS.md)

1. **Research first**, then outline to three depths, then fill to the density floor
   (Generation Protocol + Content Comprehensiveness Standard in AGENTS.md).
2. Write `topic-subtopic.html` in root using the Modern Platform Baseline and **all**
   metadata blocks (title, meta description, canonical, OG/X, TechArticle JSON-LD).
   JSON-LD must match visible content; set a real `Last verified` date.
3. Add the file to the `$categoryMap` array in `index.php`, or it lands under "Other"
   (AGENTS.md > *Adding New Cheatsheets*).
4. Generate + optimize the `images/{filename}.png` preview.
5. Commit the `.html` + its `images/*.png` by explicit path. One cheatsheet per commit.

Reviewing an existing page: run [`../TODO/CHEATSHEET-AUDIT.md`](../TODO/CHEATSHEET-AUDIT.md).
Writing/reviewing a spec: [`../TODO/SPEC-AUDIT.md`](../TODO/SPEC-AUDIT.md).

## Build + QA locally

No build step — serve the static files and verify in a real browser
(AGENTS.md > *Build & Verify Workflow*):

```bash
python3 -m http.server 8765     # then load http://127.0.0.1:8765/<file>.html
```

Assert: console clean (a `favicon.ico` 404 is the only allowed error), Bootstrap
loaded (`typeof window.bootstrap !== 'undefined'` so a bad SRI hash can't pass
silently), interactive bits work, light + dark themes both render.

## The gate that must pass

- **SEO gate** — `scripts/seo_check.py` on changed `.html`: title <= 60 chars, meta
  description 150-200, canonical present, valid JSON-LD.
- **Link/asset integrity, JSON parse, `php -l`** — also run by the deploy validator.
- **`.githooks/pre-push`** guards the `production` remote only (it runs
  `python scripts/deploy.py --check`). Pushes to `origin` are **not** blocked.
  Enable it once per clone with `git config core.hooksPath .githooks`.

## Who deploys

- **You**: commit and push to `origin` without asking (commits are the backup).
- **David deploys.** Deploy is the guarded pipeline `./deploy.sh` (`./deploy.ps1` on
  PowerShell), which pushes `main` to the `production` remote (`git push production main`).
  Never run a deploy script, push to `production`, or purge caches without his go-ahead.
  Full runbook: [`../deploy/DEPLOY.md`](../deploy/DEPLOY.md).
