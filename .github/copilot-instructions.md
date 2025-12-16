# AI Agent Instructions for CheatSheets Project

## Project Overview
Interactive HTML cheatsheet collection covering technology, philosophy, AI, cryptocurrencies, martial arts, and more. Each cheatsheet is a **standalone, self-contained HTML file** with no build process—ready for static hosting.

## Core Architecture

### Key Components
1. **Standalone HTML Files** (47+) - Self-contained cheatsheets with embedded CSS/JS
   - Bootstrap 5.3.3 via CDN, Bootstrap Icons
   - Interactive features: collapsible sections, filters, localStorage persistence
   - Print-optimized styles
   
2. **`index.php`** - Dynamic portfolio gallery
   - Scans root directory for `.html` files automatically
   - Extracts metadata using DOMDocument/DOMXPath
   - Generates card-based layout with thumbnails
   
3. **`sitemap.php`** - SEO-optimized XML sitemap
   - Auto-discovers HTML files in root
   - Priority: 1.0 for index, 0.8 for cheatsheets
   - Uses file modification times for `<lastmod>`
   
4. **`generate-image-previews.py`** - Metadata & screenshot automation
   - Playwright-based screenshot generation (1200x630px for social media)
   - BeautifulSoup HTML parsing with intelligent metadata injection
   - Dry-run by default; use `--apply` flag to commit changes

### File Organization
```
root/
├── *.html              # All cheatsheets (flat structure)
├── index.php           # Main gallery (auto-discovers HTML)
├── sitemap.php         # SEO sitemap (auto-discovers HTML)
├── generate-image-previews.py  # Metadata validator & screenshot tool
└── images/             # Social media preview images (filename.png)
```

## Critical Workflows

### Adding a New Cheatsheet
1. Create `topic-name.html` in root (lowercase, hyphen-separated)
2. Include ALL required metadata (see below)
3. PHP files automatically discover and list it
4. Generate preview: `python3 generate-image-previews.py --apply`

### Metadata Management
Run dry-run to audit: `python3 generate-image-previews.py`  
Apply fixes: `python3 generate-image-previews.py --apply`

The script intelligently:
- Adds missing technical tags (canonical, og:image, twitter:card)
- Preserves creative content tags (og:title, descriptions)
- Updates outdated URLs/paths
- Generates screenshots only for missing images

### Local Testing
```bash
python3 serve.py  # Starts local server (likely on port 8000)
```
Or use PHP built-in: `php -S localhost:8000`

## Required Metadata Template

**Every cheatsheet MUST include this complete metadata package:**

```html
<!-- Essential SEO -->
<title>Topic: Descriptive Subtitle</title>
<meta name="description" content="150-200 char comprehensive description"/>
<meta name="keywords" content="primary, technology stack, related concepts"/>
<link rel="canonical" href="https://cheatsheets.davidveksler.com/filename.html"/>

<!-- Open Graph -->
<meta property="og:title" content="Title"/>
<meta property="og:description" content="Description"/>
<meta property="og:type" content="website"/>
<meta property="og:url" content="https://cheatsheets.davidveksler.com/filename.html"/>
<meta property="og:image" content="images/filename.png"/>
<meta property="og:image:alt" content="Descriptive alt text"/>

<!-- Twitter Card -->
<meta name="twitter:card" content="summary_large_image"/>
<meta name="twitter:title" content="Title"/>
<meta name="twitter:description" content="Description"/>
<meta name="twitter:image" content="images/filename.png"/>
<meta name="twitter:creator" content="@heroiclife"/>

<!-- JSON-LD Structured Data (REQUIRED) -->
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "TechArticle",
  "headline": "Title with Version",
  "description": "Detailed description",
  "author": {"@type": "Person", "name": "David Veksler (AI Generated)"},
  "publisher": {"@type": "Organization", "name": "David Veksler Cheatsheets"},
  "datePublished": "YYYY-MM-DD",
  "dateModified": "YYYY-MM-DD",
  "keywords": "keyword list"
}
</script>
```

## Project-Specific Patterns

### HTML Structure Convention
- Use `<details>`/`<summary>` or Bootstrap collapse for sections
- Add toggle controls with localStorage persistence
- Include print-specific CSS (`@media print`)
- External links: `target="_blank" rel="noopener noreferrer"`

### PHP Metadata Extraction Pattern
```php
$dom = new DOMDocument();
@$dom->loadHTML('<?xml encoding="utf-8" ?>' . $content, LIBXML_NOERROR | LIBXML_NOWARNING);
$xpath = new DOMXPath($dom);
$titleNode = $xpath->query('//title')->item(0);
```
Files are auto-discovered via `scandir()`, filtered by `$excludedItems` array.

### Python Script Architecture
- `ChangeProposal` class accumulates all changes before applying
- Dry-run by default prevents accidental overwrites
- Creative tags (og:title) are ADD-ONLY; technical tags (og:image) are ADD-or-UPDATE
- Screenshot generation requires: `pip install playwright beautifulsoup4 lxml`
- Browser installation: `python3 -m playwright install`

### Naming Conventions
- Files: `topic-subtopic.html` (lowercase, hyphens)
- Images: `{filename}.png` (matches HTML filename)
- URLs: `https://cheatsheets.davidveksler.com/{filename}.html`

## External Dependencies
- **Bootstrap 5.3.3** (CDN) - UI framework
- **Bootstrap Icons** (CDN) - Icon library
- **Playwright** (optional) - Screenshot generation
- **BeautifulSoup4** (optional) - HTML parsing
- **lxml** (optional) - Faster HTML parsing

## Common Gotchas
- PHP files use `str_ends_with()` (PHP 8+) for file extension checks
- Image paths in og:image must be relative: `images/filename.png`
- Python script normalizes absolute URLs to relative format
- All HTML files must be in root directory (flat structure)
- The `$excludedItems` array in both PHP files must stay synchronized

## Quality Checklist
- [ ] All metadata sections present (SEO, OG, Twitter, JSON-LD)
- [ ] Image generated in `/images/` directory
- [ ] Responsive design tested (mobile/tablet/desktop)
- [ ] Print styles functional
- [ ] Interactive elements work without JavaScript fallback
- [ ] Filename follows `topic-name.html` convention
- [ ] File appears automatically in `index.php` gallery
