<?php
// Set content type and encoding
header('Content-Type: text/html; charset=utf-8');

// --- Configuration ---
$excludedItems = [
    '.',
    '..',
    'index.php', // Exclude this script itself
    'images',    // Exclude images directory if it's in the root
    'LICENSE',
    'README.md',
    'PROMPT.txt', // Assuming this was part of your dev files
    'etz-chaim-tree-of-life.html',
    // Add any other specific files or directories to exclude by name:
    // 'old_gallery.html',
];

$cheatsheetDir = '.'; // Current directory where cheatsheet HTML files are located

// --- Email signup endpoint ---
// Same-origin native-PHP handler (subscribe.php): validates the address, records
// it to a gitignored local store, and emails a notification via mail(). The form
// posts here directly so it degrades gracefully without JavaScript; no third-party
// scripts or trackers are loaded. See AGENTS.md → "Email signup endpoint" for the
// one env var to set (CHEATSHEET_NOTIFY_EMAIL).
$emailSignupEndpoint = 'subscribe.php';

// --- Category Map ---
// Single source of truth: filename => category. Unmapped sheets fall back to "Other".
// Add one line here when you publish a new cheatsheet.
$categoryMap = [
    // AI & Safety
    'agi-development-guide.html' => 'AI & Safety',
    'ai-frontier.html' => 'AI & Safety',
    'ai-progress-dashboard.html' => 'AI & Safety',
    'ai-risk-timeline.html' => 'AI & Safety',
    'airisk.html' => 'AI & Safety',
    'aisafety.html' => 'AI & Safety',
    'google-ai-studio-guide.html' => 'AI & Safety',
    'governing-agentic-ai.html' => 'AI & Safety',
    'how-its-built.html' => 'AI & Safety',
    'p-doom-calculator.html' => 'AI & Safety',
    'p-doom-test-harness.html' => 'AI & Safety',
    'prompt-builder.html' => 'AI & Safety',
    'yudkowsky-rationality-ai-cheatsheet.html' => 'AI & Safety',

    // Software & DevOps
    'aws-vs-azure.html' => 'Software & DevOps',
    'azure-devops.html' => 'Software & DevOps',
    'clean-architecture-dotnet.html' => 'Software & DevOps',
    'compression-algorithms.html' => 'Software & DevOps',
    'databases.html' => 'Software & DevOps',
    'dotnet-cheatsheet.html' => 'Software & DevOps',
    'git-scm.html' => 'Software & DevOps',
    'javascript-for-architects.html' => 'Software & DevOps',
    'modern-devops-pipelines.html' => 'Software & DevOps',
    'postgresql.html' => 'Software & DevOps',
    'python-for-architects.html' => 'Software & DevOps',
    'scrum.html' => 'Software & DevOps',
    'ubuntu-linux-for-ai-developers.html' => 'Software & DevOps',
    'versioncontrol.html' => 'Software & DevOps',

    // Security & Privacy
    'linux-server-hardening.html' => 'Security & Privacy',
    'post-quantum-cryptography.html' => 'Security & Privacy',
    'privacy-data-broker-opt-out.html' => 'Security & Privacy',

    // Bitcoin & Finance
    'bitcoin-exchanges-cards.html' => 'Bitcoin & Finance',
    'bitcoin-self-custody-guide.html' => 'Bitcoin & Finance',
    'bitcoin-wallet.html' => 'Bitcoin & Finance',
    'bitcoin-whitepaper.html' => 'Bitcoin & Finance',
    'currency-timeline.html' => 'Bitcoin & Finance',
    'housing-comparison.html' => 'Bitcoin & Finance',
    'index-investing-tax-advantaged.html' => 'Bitcoin & Finance',
    'lifestyle-calculator.html' => 'Bitcoin & Finance',

    // Martial Arts & Strategy
    'art-of-war-sun-tzu.html' => 'Martial Arts & Strategy',
    'ashihara-karate.html' => 'Martial Arts & Strategy',
    'brazilian-jiu-jitsu.html' => 'Martial Arts & Strategy',
    'judo.html' => 'Martial Arts & Strategy',
    'martial-arts-cheatsheet.html' => 'Martial Arts & Strategy',

    // Firearms & Military
    'future-of-warfare-technology.html' => 'Firearms & Military',
    'handgun-calibers.html' => 'Firearms & Military',
    'military-aphorisms.html' => 'Firearms & Military',
    'modern-firearms.html' => 'Firearms & Military',
    'operator-loadouts.html' => 'Firearms & Military',

    // Radio
    'baofeng-uv5r-ham-guide.html' => 'Radio',
    'baofeng-uv5r-quick-ref.html' => 'Radio',
    'emergency-radio-card.html' => 'Radio',
    'ham-radio-technician.html' => 'Radio',

    // Health & Fitness
    'cycling.html' => 'Health & Fitness',
    'human-skeleton.html' => 'Health & Fitness',
    'medical-school-curriculum.html' => 'Health & Fitness',
    'running.html' => 'Health & Fitness',
    'sleep-optimization.html' => 'Health & Fitness',
    'strength-training.html' => 'Health & Fitness',
    'veterinary-diagnostics.html' => 'Health & Fitness',
    'weight-loss-levers.html' => 'Health & Fitness',
    'weightloss-cheatsheet.html' => 'Health & Fitness',

    // Philosophy & Religion
    'anapanasati-mindfulness-of-breathing.html' => 'Philosophy & Religion',
    'buddhism.html' => 'Philosophy & Religion',
    'capitalism.html' => 'Philosophy & Religion',
    'conscious-leadership-contexts.html' => 'Philosophy & Religion',
    'islam.html' => 'Philosophy & Religion',
    'israel-history.html' => 'Philosophy & Religion',
    'judaism.html' => 'Philosophy & Religion',
    'leadership.html' => 'Philosophy & Religion',
    'objectivism.html' => 'Philosophy & Religion',
    'shabbat-services-cheatsheet.html' => 'Philosophy & Religion',

    // Engineering & Science
    'automotive-innovation-timeline.html' => 'Engineering & Science',
    'boom-supersonic.html' => 'Engineering & Science',
    'engineering-materials-future.html' => 'Engineering & Science',
    'engineering-metals-selection.html' => 'Engineering & Science',
    'geoengineering-approaches.html' => 'Engineering & Science',
    'human-evolution.html' => 'Engineering & Science',
    'humanoid-robots.html' => 'Engineering & Science',
    'orbital-rockets-comparison.html' => 'Engineering & Science',
    'tesla-products.html' => 'Engineering & Science',

    // Home & Lifestyle
    'command-deck.html' => 'Home & Lifestyle',
    'cooking-guide.html' => 'Home & Lifestyle',
    'global_cuisine_guide.html' => 'Home & Lifestyle',
    'home-maintenance-guide.html' => 'Home & Lifestyle',
    'hot-tub-treatment.html' => 'Home & Lifestyle',
    'living-richly-guide.html' => 'Home & Lifestyle',
    'samsung-bespoke-oven-guide.html' => 'Home & Lifestyle',
];

// --- Category Styles ---
// Per-category accent color, light background tint, and Bootstrap Icons class.
$categoryStyles = [
    'AI & Safety'             => ['color' => '#0891b2', 'bg' => '#cffafe', 'icon' => 'bi-robot'],
    'Software & DevOps'       => ['color' => '#4338ca', 'bg' => '#e0e7ff', 'icon' => 'bi-terminal-fill'],
    'Security & Privacy'      => ['color' => '#dc2626', 'bg' => '#fee2e2', 'icon' => 'bi-shield-lock-fill'],
    'Bitcoin & Finance'       => ['color' => '#d97706', 'bg' => '#fef3c7', 'icon' => 'bi-currency-bitcoin'],
    'Martial Arts & Strategy' => ['color' => '#9f1239', 'bg' => '#ffe4e6', 'icon' => 'bi-person-arms-up'],
    'Firearms & Military'     => ['color' => '#3f6212', 'bg' => '#ecfccb', 'icon' => 'bi-crosshair2'],
    'Radio'                   => ['color' => '#1e40af', 'bg' => '#dbeafe', 'icon' => 'bi-broadcast-pin'],
    'Health & Fitness'        => ['color' => '#065f46', 'bg' => '#d1fae5', 'icon' => 'bi-heart-pulse-fill'],
    'Philosophy & Religion'   => ['color' => '#6b21a8', 'bg' => '#f3e8ff', 'icon' => 'bi-yin-yang'],
    'Engineering & Science'   => ['color' => '#0c4a6e', 'bg' => '#e0f2fe', 'icon' => 'bi-gear-fill'],
    'Home & Lifestyle'        => ['color' => '#0f766e', 'bg' => '#ccfbf1', 'icon' => 'bi-house-heart-fill'],
    'Other'                   => ['color' => '#374151', 'bg' => '#f3f4f6', 'icon' => 'bi-file-earmark-text'],
];

// --- Base URL Calculation ---
$scheme = isset($_SERVER['HTTPS']) && $_SERVER['HTTPS'] === 'on' ? 'https' : 'http';
$host = $_SERVER['HTTP_HOST'];
$scriptName = $_SERVER['SCRIPT_NAME'];
$scriptDir = dirname($scriptName);
$scriptDir = ($scriptDir === '.' || $scriptDir === DIRECTORY_SEPARATOR) ? '' : $scriptDir;
$baseUrl = rtrim($scheme . '://' . $host . $scriptDir, '/') . '/';


// --- Helper Function: Extract raw, host-independent metadata (the expensive part) ---
// Reads + parses the file. Returns only values that do NOT depend on the request
// host, so the result is safe to cache across requests. URL/image resolution that
// needs $host happens later in resolveMetadata().
function extractRawMetadata(string $filepath, int $mtime): array {
    global $baseUrl; // host-independent base; the 'url' below is re-resolved in resolveMetadata()
    $filename = basename($filepath);
    $defaultTitle = preg_replace('/\.html$/i', '', $filename); // Remove .html extension
    $defaultTitle = ucwords(str_replace(['-', '_'], ' ', $defaultTitle)); // Capitalize and replace hyphens/underscores

    $raw = [
        'title' => $defaultTitle,
        'description' => 'Explore this ' . htmlspecialchars($defaultTitle) . ' cheatsheet for a concise overview of key concepts.',
        'image' => null,
        'url' => $baseUrl . $filename,
        'mtime' => @filectime($filepath) ?: 0,
        'error' => null
    ];

    $content = @file_get_contents($filepath);
    if ($content === false) {
        $raw['error'] = "Could not read file: " . htmlspecialchars($filename);
        return $raw;
    }

    $dom = new DOMDocument();
    // Suppress warnings during loading of potentially invalid HTML, and add XML encoding hint for better parsing
    @$dom->loadHTML('<?xml encoding="utf-8" ?>' . $content, LIBXML_NOERROR | LIBXML_NOWARNING);
    $xpath = new DOMXPath($dom);

    $titleNode = $xpath->query('//title')->item(0);
    if ($titleNode) {
        $raw['title'] = trim($titleNode->textContent);
    }

    $descNode = $xpath->query('//meta[@name="description"]/@content')->item(0);
    if ($descNode) {
        $raw['description'] = trim($descNode->nodeValue);
    } else {
        $ogDescNode = $xpath->query('//meta[@property="og:description"]/@content')->item(0);
        if ($ogDescNode) {
            $raw['description'] = trim($ogDescNode->nodeValue);
        }
    }

    $imgNode = $xpath->query('//meta[@property="og:image"]/@content')->item(0);
    if ($imgNode) {
        $raw['image_raw'] = trim($imgNode->nodeValue);
    }

    // Ensure description isn't excessively long for the card display
    if (mb_strlen($raw['description']) > 150) {
        $raw['description'] = mb_substr($raw['description'], 0, 147) . '...';
    }

    return $raw;
}

// --- Helper Function: Resolve cached raw metadata into request-specific URLs ---
function resolveMetadata(array $raw, string $filename): array {
    global $baseUrl, $scheme, $host;

    $meta = $raw;
    $meta['url'] = $baseUrl . $filename;
    $meta['image'] = null;

    $imageUrl = $raw['image_raw'] ?? null;
    if ($imageUrl) {
        if (preg_match('/^https?:\/\//i', $imageUrl)) { // Absolute URL
            $meta['image'] = $imageUrl;
        } elseif (str_starts_with($imageUrl, '/')) { // Root-relative URL
            $meta['image'] = $scheme . '://' . $host . $imageUrl;
        } else { // Relative URL to the cheatsheet's path
            $baseCheatsheetWebPath = dirname($meta['url']);
            $resolvedImageUrl = rtrim($baseCheatsheetWebPath, '/') . '/' . $imageUrl;

            // Normalize path (e.g., /path/../image.png to /image.png)
            $parsedResolved = parse_url($resolvedImageUrl);
            if ($parsedResolved && isset($parsedResolved['scheme']) && isset($parsedResolved['host']) && isset($parsedResolved['path'])) {
                $path = $parsedResolved['path'];
                $newPathParts = [];
                $pathSegments = explode('/', $path);
                foreach ($pathSegments as $segment) {
                    if ($segment === '.' || $segment === '') continue;
                    if ($segment === '..') {
                        if (count($newPathParts) > 0) array_pop($newPathParts);
                    } else {
                        $newPathParts[] = $segment;
                    }
                }
                $finalPath = '/' . implode('/', $newPathParts);
                 // Correct for cases like /../ resolving to root
                if (empty($newPathParts) && str_starts_with($path, '/')) {
                    $finalPath = '/';
                }

                $meta['image'] = $parsedResolved['scheme'] . '://' . $parsedResolved['host'] .
                                     (isset($parsedResolved['port']) ? ':' . $parsedResolved['port'] : '') .
                                     $finalPath;
            } else {
                $meta['image'] = $resolvedImageUrl; // Fallback if parsing or normalization fails
            }
        }
    }
    unset($meta['image_raw']);

    return $meta;
}

// --- Main Logic: Scan Directory and Build Cheatsheet List ---
$cheatsheets = [];
$categories = [];
$errors = [];

// Per-mtime metadata cache: avoids re-parsing every HTML file on every request.
// Stores only host-independent raw fields, keyed by filename; an entry is reused
// only while its cached mtime matches the file's current mtime.
$cacheFile = rtrim($cheatsheetDir, '/') . '/.metadata-cache.json';
$cache = [];
if (is_readable($cacheFile)) {
    $decoded = json_decode((string)@file_get_contents($cacheFile), true);
    if (is_array($decoded)) {
        $cache = $decoded;
    }
}
$cacheDirty = false;
$seenFiles = [];

try {
    $files = scandir($cheatsheetDir);
    if ($files === false) {
        throw new Exception("Could not scan directory: " . htmlspecialchars($cheatsheetDir));
    }

    foreach ($files as $file) {
        $filePath = rtrim($cheatsheetDir, '/') . '/' . $file;
        if (in_array($file, $excludedItems, true) || !is_file($filePath) || !is_readable($filePath) || !str_ends_with(strtolower($file), '.html')) {
            continue;
        }
        $seenFiles[$file] = true;
        $mtime = @filemtime($filePath) ?: 0;

        // Reuse cached raw metadata only if the file hasn't changed since it was cached.
        if (isset($cache[$file]) && ($cache[$file]['mtime'] ?? null) === $mtime) {
            $raw = $cache[$file];
        } else {
            $raw = extractRawMetadata($filePath, $mtime);
            $cache[$file] = $raw;
            $cacheDirty = true;
        }

        if (!empty($raw['error'])) {
            $errors[] = $raw['error'];
            continue;
        }
        $meta = resolveMetadata($raw, $file);
        $meta['category'] = $categoryMap[$file] ?? 'Other';
        $catStyle = $categoryStyles[$meta['category']] ?? $categoryStyles['Other'];
        $meta['cat_color'] = $catStyle['color'];
        $meta['cat_bg']    = $catStyle['bg'];
        $meta['cat_icon']  = $catStyle['icon'];
        $cheatsheets[] = $meta;
    }

    // Drop cache entries for files that no longer exist.
    foreach (array_keys($cache) as $cachedFile) {
        if (!isset($seenFiles[$cachedFile])) {
            unset($cache[$cachedFile]);
            $cacheDirty = true;
        }
    }
    // Persist the cache if anything changed (best-effort; ignore read-only filesystems).
    if ($cacheDirty) {
        @file_put_contents($cacheFile, json_encode($cache), LOCK_EX);
    }

    // Sort cheatsheets by newest edit date first by default
    usort($cheatsheets, fn($a, $b) => $b['mtime'] <=> $a['mtime']);

    // Distinct categories for the filter dropdown (alphabetical, "Other" last)
    $categories = array_values(array_unique(array_column($cheatsheets, 'category')));
    usort($categories, function ($a, $b) {
        if ($a === 'Other') return 1;
        if ($b === 'Other') return -1;
        return strcasecmp($a, $b);
    });

} catch (Exception $e) {
    $errors[] = "An error occurred: " . $e->getMessage();
}

// Cheatsheets updated within this window are flagged "New" in the grid.
$newThreshold = time() - 30 * 24 * 60 * 60;
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">

    <link rel="icon" href="data:image/svg+xml,<svg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 100 100%22><text y=%22.9em%22 font-size=%2290%22>🧠</text></svg>">

    <!-- === SEO & Portfolio Metadata === -->
    <title>David Veksler's Cheatsheets | Governed Agentic-AI Output at Scale</title>
    <meta name="description" content="80+ interactive reference guides produced by a governed Claude Code pipeline: a version-controlled AGENTS.md spec as acceptance criteria, a self-verification gate, and a public git audit trail. A working exhibit of agentic-AI architecture and information design at scale.">
    <meta name="keywords" content="agentic AI, Claude Code, AI governance, AGENTS.md, AI delivery, information design at scale, interactive reference guides, software architecture, AI pipeline, structured generation, version control, cheatsheets, david veksler">
    <meta name="author" content="David Veksler">
    <link rel="canonical" href="<?php echo htmlspecialchars($baseUrl); ?>">

    <!-- Sitemap reference for search engines -->
    <link rel="sitemap" type="application/xml" href="<?php echo htmlspecialchars($baseUrl); ?>sitemap.php">

    <!-- === Open Graph / Facebook / LinkedIn === -->
    <meta property="og:title" content="David Veksler's Cheatsheets | Governed Agentic-AI Output at Scale">
    <meta property="og:description" content="80+ interactive references produced by a governed Claude Code pipeline — a version-controlled spec as acceptance criteria, a self-verification gate, and a public git audit trail. A working exhibit of agentic-AI architecture and information design at scale.">
    <meta property="og:type" content="website">
    <meta property="og:url" content="<?php echo htmlspecialchars($baseUrl); ?>">
    <meta property="og:image" content="<?php echo htmlspecialchars(rtrim($baseUrl, '/')); ?>/images/cheatsheets-og-portfolio.png">
    <meta property="og:image:alt" content="A collage of interactive reference guides generated by a governed agentic-AI pipeline.">
    <meta property="og:site_name" content="David Veksler's Cheatsheets">
    <meta property="og:locale" content="en_US">

    <!-- === Twitter Card === -->
    <meta name="twitter:card" content="summary_large_image">
    <meta name="twitter:title" content="David Veksler's Cheatsheets | Governed Agentic-AI Output at Scale">
    <meta name="twitter:description" content="80+ interactive references from a governed Claude Code pipeline: a version-controlled spec as acceptance criteria, a self-verification gate, and a public git audit trail.">
    <meta name="twitter:url" content="<?php echo htmlspecialchars($baseUrl); ?>">
    <meta name="twitter:image" content="<?php echo htmlspecialchars(rtrim($baseUrl, '/')); ?>/images/cheatsheets-og-portfolio.png">
    <meta name="twitter:image:alt" content="Interactive reference guides generated by a governed agentic-AI pipeline.">
    <meta name="twitter:creator" content="@HeroicLife" />

    <!-- Schema.org Markup for CollectionPage -->
    <script type="application/ld+json">
    {
      "@context": "https://schema.org",
      "@type": "CollectionPage",
      "name": "David Veksler's Cheatsheets | Governed Agentic-AI Output at Scale",
      "description": "A collection of 80+ interactive reference guides produced by a governed Claude Code pipeline — a version-controlled AGENTS.md specification as binding acceptance criteria, a self-verification gate, human review, and a public git audit trail. A working exhibit of agentic-AI architecture and information design at scale.",
      "url": "<?php echo htmlspecialchars($baseUrl); ?>",
      "author": {
        "@type": "Person",
        "name": "David Veksler",
        "url": "https://www.linkedin.com/in/davidveksler/"
      },
      "publisher": {
        "@type": "Person",
        "name": "David Veksler",
        "url": "https://www.linkedin.com/in/davidveksler/"
      },
      "mainEntity": {
        "@type": "ItemList",
        "itemListElement": [
          <?php foreach ($cheatsheets as $index => $sheet): ?>
          {
            "@type": "ListItem",
            "position": <?php echo $index + 1; ?>,
            "item": {
              "@type": "CreativeWork",
              "name": "<?php echo htmlspecialchars($sheet['title']); ?>",
              "url": "<?php echo htmlspecialchars($sheet['url']); ?>",
              "description": "<?php echo htmlspecialchars($sheet['description']); ?>"
              <?php if (!empty($sheet['category']) && $sheet['category'] !== 'Other'): ?>
              ,"genre": "<?php echo htmlspecialchars($sheet['category']); ?>"
              <?php endif; ?>
              <?php if (!empty($sheet['mtime'])): ?>
              ,"dateModified": "<?php echo htmlspecialchars(date('Y-m-d', $sheet['mtime'])); ?>"
              <?php endif; ?>
              <?php if (!empty($sheet['image'])): ?>
              ,"image": "<?php echo htmlspecialchars($sheet['image']); ?>"
              <?php endif; ?>
            }
          }<?php if ($index < count($cheatsheets) - 1) echo ','; ?>
          <?php endforeach; ?>
        ]
      }
    }
    </script>

    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.8/dist/css/bootstrap.min.css" rel="stylesheet" integrity="sha384-sRIl4kxILFvY47J16cr9ZwB07vP4J8+LH7qKQnuqkuIAvNWLzeN8tE5YBujZqJLB" crossorigin="anonymous">
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.13.1/font/bootstrap-icons.min.css" integrity="sha384-CK2SzKma4jA5H/MXDUU7i1TqZlCFaD4T01vtyDFvPlD97JQyS+IsSh1nI2EFbpyk" crossorigin="anonymous">

    <style>
        :root {
             --card-lift-height: -5px; /* Slightly more subtle lift */
             --card-shadow-intensity: rgba(0, 0, 0, .1); /* Softer shadow */
        }
        html { scroll-behavior: smooth; }
        body { display: flex; flex-direction: column; min-height: 100vh; background-color: #f4f5fb; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; color: #333; }
        /* Fixed, lightly-tinted animated mesh so the frosted cards refract colour.
           position: fixed keeps it out of the flex flow and off the scroll path. */
        body::before {
            content: "";
            position: fixed;
            inset: 0;
            z-index: -1;
            pointer-events: none;
            background-color: #f4f5fb;
            background-image:
                radial-gradient(40% 50% at 15% 18%, rgba(99, 102, 241, .18) 0%, transparent 60%),  /* indigo */
                radial-gradient(45% 55% at 85% 25%, rgba(139, 92, 246, .16) 0%, transparent 60%),  /* violet */
                radial-gradient(50% 60% at 78% 85%, rgba(34, 211, 238, .14) 0%, transparent 60%),  /* cyan  */
                radial-gradient(45% 55% at 18% 90%, rgba(67, 56, 202, .14) 0%, transparent 62%);   /* deep indigo */
            background-size: 200% 200%;
            background-position: 0% 50%;
            animation: heroGradientShift 28s ease-in-out infinite alternate;
        }
        .main-content { flex: 1; }
        .navbar { background-image: linear-gradient(to bottom, #343a40, #2c3034); } /* Darker, less contrast gradient */
        .navbar-brand { font-weight: 500; color: #f8f9fa !important; }
        .card {
            transition: transform .15s ease-out, box-shadow .15s ease-out; /* Quicker, smoother transition */
            border: 1px solid rgba(255, 255, 255, .45);
            border-radius: .3rem; overflow: hidden;
            background-color: rgba(255, 255, 255, .55); /* Frosted glass */
            backdrop-filter: blur(10px) saturate(130%);
            -webkit-backdrop-filter: blur(10px) saturate(130%);
            display: flex; flex-direction: column;
            border-top: 3px solid var(--cat-color, #dee2e6);
        }
        .card:hover { transform: translateY(var(--card-lift-height)); box-shadow: 0 0.5rem 1rem var(--card-shadow-intensity); }
        .card-img-top-container {
            aspect-ratio: 16 / 9;
            width: 100%;
            overflow: hidden;
            background: linear-gradient(135deg, var(--cat-bg, #e9ecef) 0%, #fff 100%);
            border-bottom: 1px solid #dee2e6;
            position: relative;
            display: flex; align-items: center; justify-content: center;
        }
        .card-img-top-container img {
            width: 100%; height: 100%; object-fit: cover; display: block;
            position: relative; z-index: 1; /* Cover the ::before placeholder icon */
        }
        .card-img-top-container img.error { display: none; } /* Reveal ::before icon on broken image */

        .card-title a { text-decoration: none; color: #1a508b; font-weight: 600; } /* Darker blue */
        .card-title a:hover { color: #003d73; text-decoration: underline; }



/* --- UPDATED CARD TEXT AND TITLE STYLES --- */
.card-title { /* This is an <h5> */
    font-size: 1.25rem;  /* Standard Bootstrap H5 font-size */
    font-weight: 600;    /* Set on H5, will be inherited by <a> */
    line-height: 1.3;    /* Consistent line height for calculation.
                           1.25rem * 1.3 = 1.625rem per line. */

    /* Explicit height for 2 lines on the H5 container. */
    /* 2 lines * 1.625rem/line = 3.25rem */
    height: 3.25rem;

    overflow: hidden; /* CRITICAL: H5 must clip its content if it overflows this height. */
    margin-bottom: .5rem; /* Standard Bootstrap h5 margin. */
    padding: 0; /* Ensure no padding on H5 itself interferes with height. */
    position: relative; /* For positioning child if needed, though not used here. */
}

.card-title a {
    text-decoration: none;
    color: #1a508b;
    /* Inherits font-size, font-weight, line-height from .card-title (h5) */

    /* Apply line clamping directly to the <a> tag */
    display: -webkit-box;
    -webkit-box-orient: vertical;
    -webkit-line-clamp: 2; /* Target 2 lines */
    overflow: hidden; /* Needed for -webkit-line-clamp to work effectively on the <a> */
    text-overflow: ellipsis;

    /* Make the <a> tag take up the full height of its parent h5.
       This helps ensure the clamping mechanism has the correct box to work with. */
    /* It might not be strictly necessary if the h5's overflow:hidden is enough,
       but can help in some cases. */
    /* max-height: 100%; /* Consider if needed if h5 overflow doesn't catch it. */
}

.card-body {
    flex-grow: 1;
    display: flex;
    flex-direction: column;
    padding: 1rem;
}

.card-text {
    flex-grow: 1;
    margin-bottom: .8rem;
    color: #495057;
    font-size: 0.875rem;
    line-height: 1.5;
    min-height: calc(0.875rem * 1.5 * 3); /* Reserve space for 3 lines */

    display: -webkit-box;
    -webkit-box-orient: vertical;
    -webkit-line-clamp: 3;
    overflow: hidden;
    text-overflow: ellipsis;
}
/* --- END UPDATED CARD TEXT AND TITLE STYLES --- */





        .card-footer {
            background-color:transparent;
            border-top: 1px solid #e9ecef;
            padding: 0.75rem 1rem;
            text-align:center;
            margin-top: auto; /* This is critical for pushing footer to bottom */
        }
        .footer { background-color: #343a40; color: #adb5bd; border-top: 1px solid #495057; }
        .footer a { color: #f8f9fa; } .footer a:hover { color: #ced4da; }
        /* === Animated glassmorphism hero (cool indigo / violet / cyan mesh) === */
        .page-hero {
            position: relative;
            overflow: hidden;
            isolation: isolate;
            padding: 4.5rem 0;
            margin-bottom: 2rem;
            border-bottom: 1px solid rgba(255, 255, 255, .15);
            background-color: #1e1b4b; /* Deep indigo base behind the blobs */
            background-image:
                radial-gradient(42% 55% at 18% 28%, rgba(99, 102, 241, .85) 0%, transparent 60%),  /* indigo */
                radial-gradient(46% 60% at 82% 22%, rgba(139, 92, 246, .80) 0%, transparent 60%),  /* violet */
                radial-gradient(50% 65% at 72% 80%, rgba(34, 211, 238, .55) 0%, transparent 60%),  /* cyan  */
                radial-gradient(46% 60% at 25% 82%, rgba(67, 56, 202, .80) 0%, transparent 62%);   /* deep indigo */
            background-size: 200% 200%;
            background-position: 0% 50%;
            animation: heroGradientShift 22s ease-in-out infinite alternate;
        }
        @keyframes heroGradientShift {
            0%   { background-position: 0%   50%; }
            50%  { background-position: 100% 50%; }
            100% { background-position: 50%  100%; }
        }
        /* Cursor-following highlight; --mx/--my default to centre until JS updates them */
        .hero-glow {
            position: absolute;
            inset: 0;
            z-index: -1;
            pointer-events: none;
            background: radial-gradient(
                30rem 30rem at var(--mx, 50%) var(--my, 40%),
                rgba(255, 255, 255, .22) 0%,
                rgba(255, 255, 255, .08) 25%,
                transparent 60%);
            transition: background .12s linear;
        }
        .hero-glass {
            max-width: 760px;
            margin: 0 auto;
            padding: 2.25rem 2.5rem;
            background: rgba(255, 255, 255, .12);
            border: 1px solid rgba(255, 255, 255, .25);
            border-radius: 1rem;
            box-shadow: 0 8px 32px rgba(30, 27, 75, .35);
            backdrop-filter: blur(14px) saturate(140%);
            -webkit-backdrop-filter: blur(14px) saturate(140%);
        }
        .page-hero h1 { color: #fff; font-weight: 600; text-shadow: 0 2px 12px rgba(30, 27, 75, .45); }
        .page-hero .lead { color: rgba(255, 255, 255, .9); font-size: 1.1rem; margin-bottom: 1.25rem; }
        #filterInput { border-radius: .25rem; font-size: 1rem; padding: .6rem 1rem; }
        #filterInput:focus { border-color: #86b7fe; box-shadow: 0 0 0 0.2rem rgba(13, 110, 253, 0.25); }
        .cta-scroll-link { font-size: 0.9rem; text-decoration: none; color: #e0e7ff; font-weight: 500; }
        .cta-scroll-link:hover { color: #fff; text-decoration: underline; }
        /* Frosted filter/search toolbar (sits on the light page, so the frost is subtle) */
        .filter-toolbar .input-group-text,
        .filter-toolbar .form-control,
        .filter-toolbar .form-select {
            background-color: rgba(255, 255, 255, .6) !important; /* override Bootstrap .bg-white */
            backdrop-filter: blur(8px) saturate(130%);
            -webkit-backdrop-filter: blur(8px) saturate(130%);
            border-color: rgba(255, 255, 255, .55);
        }
        .cta-section { background-color: #ffffff; border-top: 1px solid #dee2e6; border-bottom: 1px solid #dee2e6; padding: 3rem 0; margin: 3rem 0;}
        .cta-section h3 {font-weight: 600; color: #212529;}
        .portfolio-item .card {
            height: 100%; /* This is critical for making cards in a row the same height */
        }
        .category-badge {
            background-color: var(--cat-bg, #e7f1ff);
            color: var(--cat-color, #1a508b);
            font-weight: 500;
            font-size: 0.7rem;
            letter-spacing: .02em;
        }
        .new-badge {
            position: absolute;
            top: .5rem;
            right: .5rem;
            z-index: 2; /* Above the preview image */
            background-color: #198754;
            color: #fff;
            font-size: 0.7rem;
            font-weight: 600;
            letter-spacing: .03em;
            text-transform: uppercase;
            box-shadow: 0 1px 3px rgba(0, 0, 0, .25);
        }
        .cat-placeholder-icon {
            position: absolute;
            font-size: 3.5rem;
            color: var(--cat-color, #adb5bd);
            opacity: 0.3;
            z-index: 0;
        }
        /* Graceful fallback where backdrop-filter is unsupported: solid surfaces */
        @supports not ((backdrop-filter: blur(1px)) or (-webkit-backdrop-filter: blur(1px))) {
            .card { background-color: #fff; }
            .hero-glass { background: rgba(30, 27, 75, .55); }
            .filter-toolbar .input-group-text,
            .filter-toolbar .form-control,
            .filter-toolbar .form-select { background-color: #fff !important; }
        }
        /* Hero call-to-action buttons */
        .hero-cta { display: flex; flex-wrap: wrap; gap: .6rem; justify-content: center; }
        .hero-cta .btn-light { color: #1e1b4b; }
        .hero-cta .btn-outline-light:hover { color: #1e1b4b; }
        /* Email signup card (sits on the white CTA section) */
        .signup-card {
            max-width: 560px;
            background: #f8f9fc;
            border: 1px solid #e3e6ef;
            border-radius: .75rem;
            padding: 1.5rem;
            text-align: center;
        }
        .signup-card h4 { font-weight: 600; color: #212529; font-size: 1.1rem; margin-bottom: .35rem; }
        .signup-card p.signup-sub { color: #6c757d; font-size: .9rem; margin-bottom: 1rem; }
        .signup-card .signup-note { color: #6c757d; font-size: .78rem; margin: .6rem 0 0; }
        .signup-card .signup-status { font-size: .9rem; font-weight: 600; margin: .6rem 0 0; color: #198754; }
        .signup-card .signup-status.is-error { color: #dc3545; }
        .cta-actions { display: flex; flex-wrap: wrap; gap: .6rem; justify-content: center; }
        /* Respect reduced-motion: freeze the drift and disable the cursor-follow easing */
        @media (prefers-reduced-motion: reduce) {
            .page-hero,
            body::before { animation: none; }
            .hero-glow { transition: none; }
        }
    </style>
</head>
<body class="d-flex flex-column min-vh-100">
    <nav class="navbar navbar-expand-lg navbar-dark sticky-top shadow-sm">
        <div class="container">
            <a class="navbar-brand" href="<?php echo htmlspecialchars($baseUrl); ?>">
                 <i class="bi bi-journal-richtext me-2"></i>David Veksler's Cheatsheet Portfolio
            </a>
            <div class="ms-auto d-flex gap-2">
                <a class="btn btn-sm btn-outline-light" href="<?php echo htmlspecialchars($baseUrl); ?>how-its-built.html">
                    <i class="bi bi-gear-wide-connected me-1"></i>How it's built
                </a>
                <a class="btn btn-sm btn-outline-light" href="<?php echo htmlspecialchars($baseUrl); ?>history.php">
                    <i class="bi bi-clock-history me-1"></i>Change History
                </a>
            </div>
        </div>
    </nav>

    <main class="main-content">
        <header class="page-hero text-center" id="pageHero">
            <span class="hero-glow" aria-hidden="true"></span>
            <div class="container">
                <div class="hero-glass">
                    <h1 class="display-5">Cheatsheet Directory</h1>
                    <p class="lead">80+ interactive references, generated by a disciplined, version-controlled Claude Code pipeline — a written spec as acceptance criteria, a self-verification gate, and a public git audit trail. Not hand-authored one-offs.</p>
                    <div class="hero-cta">
                        <a href="how-its-built.html" class="btn btn-light btn-lg fw-semibold">
                            <i class="bi bi-gear-wide-connected me-1"></i>How this site is built
                        </a>
                        <a href="https://www.linkedin.com/in/davidveksler/" target="_blank" rel="noopener noreferrer" class="btn btn-outline-light btn-lg">
                            <i class="bi bi-linkedin me-1"></i>Connect on LinkedIn
                        </a>
                    </div>
                </div>
            </div>
        </header>

        <div class="container mt-4 mb-5">
            <div class="row mb-4 justify-content-center g-2 filter-toolbar">
                <div class="col-md-8 col-lg-5">
                    <div class="input-group input-group-lg shadow-sm">
                        <span class="input-group-text bg-white border-end-0 text-primary" id="filter-addon"><i class="bi bi-search"></i></span>
                        <input type="search" id="filterInput" class="form-control border-start-0" placeholder="Filter by title or topic (e.g., Buddhism, Python)..." aria-label="Filter cheatsheets" aria-describedby="filter-addon">
                    </div>
                </div>
                <div class="col-md-8 col-lg-4">
                    <div class="input-group input-group-lg shadow-sm">
                        <label class="input-group-text bg-white border-end-0 text-primary" for="categorySelect"><i class="bi bi-tags"></i></label>
                        <select id="categorySelect" class="form-select border-start-0" aria-label="Filter by category">
                            <option value="" selected>All categories</option>
                            <?php foreach ($categories as $cat): ?>
                                <option value="<?php echo htmlspecialchars($cat); ?>"><?php echo htmlspecialchars($cat); ?></option>
                            <?php endforeach; ?>
                        </select>
                    </div>
                </div>
                <div class="col-md-8 col-lg-3">
                    <div class="input-group input-group-lg shadow-sm">
                        <label class="input-group-text bg-white border-end-0 text-primary" for="sortSelect"><i class="bi bi-sort-down"></i></label>
                        <select id="sortSelect" class="form-select border-start-0" aria-label="Sort cheatsheets">
                            <option value="date-desc" selected>Newest first</option>
                            <option value="date-asc">Oldest first</option>
                            <option value="title-asc">Title (A–Z)</option>
                            <option value="title-desc">Title (Z–A)</option>
                        </select>
                    </div>
                </div>
            </div>

            <?php if (!empty($errors)): ?>
                <div class="alert alert-warning alert-dismissible fade show" role="alert">
                    <h4 class="alert-heading"><i class="bi bi-exclamation-triangle-fill me-2"></i>Notice</h4>
                    <p>There were some issues loading details for all cheatsheets:</p>
                    <ul class="mb-0">
                        <?php foreach ($errors as $error): ?>
                            <li><?php echo $error; ?></li>
                        <?php endforeach; ?>
                    </ul>
                    <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
                </div>
            <?php endif; ?>

            <?php if (empty($cheatsheets) && empty($errors)): ?>
                <div class="alert alert-info text-center mt-4 py-4" role="alert">
                    <i class="bi bi-info-circle-fill me-2 fs-4 align-middle"></i>No cheatsheet examples found. Please check back soon for updates!
                </div>
            <?php endif; ?>

            <div id="cheatsheetGrid" class="row row-cols-1 row-cols-md-2 row-cols-lg-3 g-4">
                <?php foreach ($cheatsheets as $sheet): ?>
                    <div class="col portfolio-item" data-title="<?php echo htmlspecialchars($sheet['title']); ?>" data-mtime="<?php echo (int)$sheet['mtime']; ?>" data-category="<?php echo htmlspecialchars($sheet['category']); ?>">
                        <article class="card shadow-sm" style="--cat-color: <?php echo htmlspecialchars($sheet['cat_color']); ?>; --cat-bg: <?php echo htmlspecialchars($sheet['cat_bg']); ?>;">
                            <a href="<?php echo htmlspecialchars($sheet['url']); ?>" target="_blank" rel="noopener" class="card-img-top-container" aria-label="Open <?php echo htmlspecialchars($sheet['title']); ?>">
                                <i class="bi <?php echo htmlspecialchars($sheet['cat_icon']); ?> cat-placeholder-icon" aria-hidden="true"></i>
                                <?php if (!empty($sheet['mtime']) && $sheet['mtime'] >= $newThreshold): ?>
                                    <span class="badge new-badge"><i class="bi bi-stars me-1"></i>New</span>
                                <?php endif; ?>
                                <?php if (!empty($sheet['image'])): ?>
                                    <img src="<?php echo htmlspecialchars($sheet['image']); ?>" alt="Preview for <?php echo htmlspecialchars($sheet['title']); ?>" loading="lazy" onerror="this.classList.add('error');">
                                <?php endif; ?>
                            </a>
                            <div class="card-body">
                                <?php if (!empty($sheet['category'])): ?>
                                    <span class="badge category-badge mb-2 align-self-start"><i class="bi <?php echo htmlspecialchars($sheet['cat_icon']); ?> me-1"></i><?php echo htmlspecialchars($sheet['category']); ?></span>
                                <?php endif; ?>
                                <h5 class="card-title">
                                    <a href="<?php echo htmlspecialchars($sheet['url']); ?>" target="_blank" rel="noopener">
                                        <?php echo htmlspecialchars($sheet['title']); ?>
                                    </a>
                                </h5>
                                <p class="card-text">
                                    <?php echo htmlspecialchars($sheet['description']); ?>
                                </p>
                                <?php if (!empty($sheet['mtime'])): ?>
                                    <p class="card-date text-muted small mb-0">
                                        <i class="bi bi-calendar3 me-1"></i>Updated <?php echo htmlspecialchars(date('M j, Y', $sheet['mtime'])); ?>
                                    </p>
                                <?php endif; ?>
                            </div>
                            <div class="card-footer">
                                <a href="<?php echo htmlspecialchars($sheet['url']); ?>" target="_blank" rel="noopener" class="btn btn-sm btn-outline-primary w-100" style="--bs-btn-color: var(--cat-color); --bs-btn-border-color: var(--cat-color); --bs-btn-hover-bg: var(--cat-color); --bs-btn-hover-border-color: var(--cat-color); --bs-btn-hover-color: #fff; --bs-btn-active-bg: var(--cat-color); --bs-btn-active-border-color: var(--cat-color); --bs-btn-active-color: #fff;">
                                    View Cheatsheet <i class="bi bi-box-arrow-up-right ms-1"></i>
                                </a>
                            </div>
                        </article>
                    </div>
                <?php endforeach; ?>
            </div>

            <div id="noResults" class="alert alert-warning text-center mt-4 py-3 d-none" role="alert">
                <i class="bi bi-emoji-frown me-2"></i>No cheatsheets match your filter. Try a different term.
            </div>
        </div>
    </main>

    <section id="custom-cheatsheet-cta" class="cta-section text-center">
        <div class="container">
              <h3 class="mb-3">How this collection is built</h3>
              <p class="text-muted mb-4 mx-auto" style="max-width: 720px;">
                  This whole collection is a working exhibit: a Claude Code pipeline producing polished, accurate references at scale, kept honest by a version-controlled spec, a self-verification gate, and a public git audit trail. If that's the kind of thing you're working on, I'm happy to compare notes.
              </p>
              <div class="cta-actions mb-5">
                  <a href="how-its-built.html" class="btn btn-primary btn-lg px-4">
                      <i class="bi bi-gear-wide-connected me-2"></i>See how it's built
                  </a>
                  <a href="https://www.linkedin.com/in/davidveksler/" target="_blank" rel="noopener noreferrer" class="btn btn-outline-primary btn-lg px-4">
                      <i class="bi bi-linkedin me-2"></i>Let's talk on LinkedIn
                  </a>
              </div>

              <div class="signup-card mx-auto">
                  <h4><i class="bi bi-envelope-paper me-1"></i>Get new references &amp; build notes</h4>
                  <p class="signup-sub">Occasional email when a new reference ships or the pipeline changes. No spam, no tracking, unsubscribe anytime.</p>
                  <!-- Form posts to $emailSignupEndpoint (subscribe.php, same origin). Degrades
                       gracefully without JS; JS enhances to an inline confirmation. No tracking scripts. -->
                  <form action="<?php echo htmlspecialchars($emailSignupEndpoint); ?>" method="post" class="email-signup">
                      <label class="visually-hidden" for="emailSignupField">Email address</label>
                      <div class="visually-hidden" aria-hidden="true">
                          <label for="website-hp">Leave this field empty</label>
                          <input type="text" id="website-hp" name="website" tabindex="-1" autocomplete="off">
                      </div>
                      <div class="input-group input-group-lg shadow-sm">
                          <span class="input-group-text bg-white text-primary"><i class="bi bi-envelope"></i></span>
                          <input type="email" id="emailSignupField" name="email" class="form-control" required autocomplete="email" inputmode="email" placeholder="you@example.com" aria-label="Email address">
                          <button class="btn btn-primary" type="submit"><i class="bi bi-bell me-1"></i>Notify me</button>
                      </div>
                      <p class="signup-note">A single field, no third-party scripts. Falls back to a plain form post without JavaScript.</p>
                      <p class="signup-status" role="status" aria-live="polite" hidden></p>
                  </form>
              </div>
        </div>
    </section>

    <footer class="footer py-4 mt-auto">
        <div class="container text-center">
            <p class="mb-2 small">
                Cheatsheet Portfolio © <?php echo date("Y"); ?> David Veksler. All rights reserved.
            </p>
            <div>
              <a href="https://www.linkedin.com/in/davidveksler/" title="David Veksler on LinkedIn" target="_blank" rel="noopener noreferrer" class="mx-2 small">
                <i class="bi bi-linkedin"></i> LinkedIn
              </a>
              <span class="mx-1 small">|</span>
              <a href="<?php echo htmlspecialchars($baseUrl); ?>how-its-built.html" title="How this site is built" class="mx-2 small">
                <i class="bi bi-gear-wide-connected"></i> How It's Built
              </a>
              <span class="mx-1 small">|</span>
              <a href="<?php echo htmlspecialchars($baseUrl); ?>" title="Browse all cheatsheets" class="mx-2 small">
                <i class="bi bi-collection-fill"></i> All Cheatsheets
              </a>
              <span class="mx-1 small">|</span>
              <a href="<?php echo htmlspecialchars($baseUrl); ?>history.php" title="Browse the git change history" class="mx-2 small">
                <i class="bi bi-clock-history"></i> Change History
              </a>
            </div>
        </div>
    </footer>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.8/dist/js/bootstrap.bundle.min.js" integrity="sha384-FKyoEForCGlyvwx9Hj09JcYn3nv7wiPVlz7YYwJrWVcXK/BmnVDxM+D2scQbITxI" crossorigin="anonymous" defer></script>
    <script>
    document.addEventListener('DOMContentLoaded', function() {
        const filterInput = document.getElementById('filterInput');
        const categorySelect = document.getElementById('categorySelect');
        const sortSelect = document.getElementById('sortSelect');
        const grid = document.getElementById('cheatsheetGrid');
        const noResultsMessage = document.getElementById('noResults');
        const items = grid ? Array.from(grid.querySelectorAll('.portfolio-item')) : [];

        if (sortSelect && grid && items.length > 0) {
            const sortItems = function() {
                const mode = sortSelect.value;
                const sorted = items.slice().sort((a, b) => {
                    switch (mode) {
                        case 'title-desc':
                            return b.dataset.title.localeCompare(a.dataset.title, undefined, { sensitivity: 'base' });
                        case 'date-desc':
                            return (Number(b.dataset.mtime) || 0) - (Number(a.dataset.mtime) || 0);
                        case 'date-asc':
                            return (Number(a.dataset.mtime) || 0) - (Number(b.dataset.mtime) || 0);
                        case 'title-asc':
                        default:
                            return a.dataset.title.localeCompare(b.dataset.title, undefined, { sensitivity: 'base' });
                    }
                });
                sorted.forEach(item => grid.appendChild(item));
            };
            sortSelect.addEventListener('change', sortItems);
        }

        if (filterInput && grid && items.length > 0) {
            const applyFilters = function() {
                const filterText = filterInput.value.toLowerCase().trim();
                const selectedCategory = categorySelect ? categorySelect.value : '';
                let itemsVisible = 0;

                items.forEach(item => {
                    const titleElement = item.querySelector('.card-title a');
                    const descriptionElement = item.querySelector('.card-text');
                    const title = titleElement ? titleElement.textContent.toLowerCase() : '';
                    const description = descriptionElement ? descriptionElement.textContent.toLowerCase() : '';

                    const matchesText = filterText === '' || title.includes(filterText) || description.includes(filterText);
                    const matchesCategory = selectedCategory === '' || item.dataset.category === selectedCategory;
                    const isVisible = matchesText && matchesCategory;

                    if (isVisible) {
                        item.style.display = '';
                        itemsVisible++;
                    } else {
                        item.style.display = 'none';
                    }
                });
                noResultsMessage.classList.toggle('d-none', itemsVisible > 0);
            };

            filterInput.addEventListener('input', applyFilters);
            if (categorySelect) categorySelect.addEventListener('change', applyFilters);
        } else if (filterInput) {
             filterInput.disabled = true;
             filterInput.placeholder = "No cheatsheets available to filter.";
        }

        // Catch images cached as broken: a 'complete' image with zero dimensions
        // may never fire 'error', so the inline onerror handler won't run for it.
        document.querySelectorAll('.card-img-top-container img').forEach(img => {
            if (img.complete && img.naturalWidth === 0 && img.src) {
                img.classList.add('error');
            }
        });

        // Email signup: progressive enhancement over a plain same-origin form post.
        //   No JS  → posts natively to subscribe.php, which renders a confirmation page.
        //   With JS → submits asynchronously and confirms inline from the JSON response.
        document.querySelectorAll('form.email-signup').forEach(function (form) {
            const status = form.querySelector('.signup-status');
            const show = function (msg, isError) {
                if (!status) return;
                status.hidden = false;
                status.textContent = msg;
                status.classList.toggle('is-error', !!isError);
            };
            form.addEventListener('submit', function (e) {
                const email = form.querySelector('input[type="email"]');
                if (email && !email.checkValidity()) return; // native validation surfaces the error
                e.preventDefault();
                const btn = form.querySelector('button');
                if (btn) btn.disabled = true;
                fetch(form.action, { method: 'POST', headers: { 'Accept': 'application/json' }, body: new FormData(form) })
                    .then(function (r) { return r.json().catch(function () { return { ok: r.ok }; }); })
                    .then(function (d) {
                        if (d && d.ok) { show('Thanks — you’re on the list.'); form.reset(); }
                        else { show((d && d.error) || 'Sorry, that didn’t go through. Please try again.', true); }
                    })
                    .catch(function () { show('Network error — please try again later.', true); })
                    .finally(function () { if (btn) btn.disabled = false; });
            });
        });

        // Hero highlight follows the cursor (fine pointers only, skipped under reduced-motion).
        // Updates are coalesced into one rAF tick per frame to avoid layout thrash.
        const hero = document.getElementById('pageHero');
        const wantsMotion = !window.matchMedia('(prefers-reduced-motion: reduce)').matches;
        if (hero && wantsMotion && window.matchMedia('(pointer: fine)').matches) {
            let ticking = false, mx = 50, my = 40;
            hero.addEventListener('pointermove', function(e) {
                const rect = hero.getBoundingClientRect();
                mx = ((e.clientX - rect.left) / rect.width) * 100;
                my = ((e.clientY - rect.top) / rect.height) * 100;
                if (!ticking) {
                    ticking = true;
                    requestAnimationFrame(function() {
                        hero.style.setProperty('--mx', mx + '%');
                        hero.style.setProperty('--my', my + '%');
                        ticking = false;
                    });
                }
            });
        }
    });
    </script>

</body>
</html>