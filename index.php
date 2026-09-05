<?php
/**
 * index.php — the Explorer: one page, one catalog, one search box that reaches
 * inside every sheet.
 *
 * Data comes from catalog.json (built by scripts/build_catalog.py), plus
 * popularity.json, refresh-status.json, paths.json and a single `git log -1`.
 * Nothing is parsed out of the sheets at request time any more: the deploy gate
 * (scripts/deploy.py --check) guarantees the catalog is current, so this file
 * only formats data it is handed.
 *
 * Phase 1 of TODO/index-explorer-redesign.md: Grid lens, facet rail, search
 * palette, drawer, Pulse strip, serendipity, category landing pages. The Map
 * and Paths lenses arrive in Phase 2; the Paths section below is the static,
 * no-JS list the spec requires now.
 *
 * No frameworks, no CDN assets, no web fonts, no backdrop-filter, no continuous
 * animation. The only external script is the Microsoft Clarity tag.
 */

header('Content-Type: text/html; charset=utf-8');
// Short edge/browser cache: the grid changes whenever a sheet ships, but a
// 5-minute TTL lets Cloudflare absorb repeat hits without staling it noticeably.
header('Cache-Control: public, max-age=300');

$ROOT = __DIR__;

/* ------------------------------------------------------------------ utils -- */

function h($s): string { return htmlspecialchars((string)$s, ENT_QUOTES, 'UTF-8'); }

/** Read one GET parameter as a trimmed string; never notices on a missing key. */
function q_str(string $key): string {
    $v = $_GET[$key] ?? '';
    return is_string($v) ? trim($v) : '';
}

/** Clamp to $n characters on a word boundary, appending an ellipsis if cut. */
function clamp_text(string $s, int $n): string {
    if (mb_strlen($s) <= $n) return $s;
    $cut = mb_substr($s, 0, $n - 1);
    $sp = mb_strrpos($cut, ' ');
    if ($sp !== false && $sp > $n * 0.6) $cut = mb_substr($cut, 0, $sp);
    return rtrim($cut, " ,;:.") . '…';
}

/** Human relative time, past tense, from a unix timestamp. */
function rel_time(int $ts): string {
    $d = time() - $ts;
    if ($d < 0) $d = 0;
    foreach ([[31536000,'year'],[2592000,'month'],[604800,'week'],[86400,'day'],[3600,'hour'],[60,'minute']] as $u) {
        if ($d >= $u[0]) { $n = (int)floor($d / $u[0]); return $n . ' ' . $u[1] . ($n === 1 ? '' : 's') . ' ago'; }
    }
    return 'just now';
}

/**
 * Read-only git, same shape as history.php's helper: every argument goes
 * through escapeshellarg(), safe.directory neutralises "dubious ownership"
 * when the web user differs from the repo owner.
 */
function cs_git(array $args): array {
    global $ROOT;
    $cmd = 'git -C ' . escapeshellarg($ROOT)
         . ' -c safe.directory=' . escapeshellarg($ROOT)
         . ' --no-pager';
    foreach ($args as $a) $cmd .= ' ' . escapeshellarg($a);
    $descriptors = [1 => ['pipe', 'w'], 2 => ['pipe', 'w']];
    $proc = @proc_open($cmd . ' 2>/dev/null', $descriptors, $pipes);
    if (!is_resource($proc)) return ['out' => '', 'code' => 127];
    $out = stream_get_contents($pipes[1]); fclose($pipes[1]);
    if (isset($pipes[2])) { stream_get_contents($pipes[2]); fclose($pipes[2]); }
    $code = proc_close($proc);
    return ['out' => (string)$out, 'code' => $code];
}

function read_json(string $path) {
    if (!is_readable($path)) return null;
    $raw = @file_get_contents($path);
    if ($raw === false) return null;
    $data = json_decode($raw, true);
    return is_array($data) ? $data : null;
}

/* ------------------------------------------------------------- base URL --- */

$scheme = (isset($_SERVER['HTTPS']) && $_SERVER['HTTPS'] === 'on') ? 'https' : 'http';
$host = isset($_SERVER['HTTP_HOST']) && $_SERVER['HTTP_HOST'] !== ''
    ? (string)$_SERVER['HTTP_HOST'] : 'cheatsheets.davidveksler.com';
$scriptDir = dirname(isset($_SERVER['SCRIPT_NAME']) ? (string)$_SERVER['SCRIPT_NAME'] : '/index.php');
if ($scriptDir === '.' || $scriptDir === DIRECTORY_SEPARATOR) $scriptDir = '';
$baseUrl = rtrim($scheme . '://' . $host . $scriptDir, '/') . '/';

/* -------------------------------------------------------------- catalog --- */

$catalog = read_json($ROOT . '/catalog.json');
if (!$catalog || empty($catalog['sheets']) || !is_array($catalog['sheets'])) {
    // Fail closed and loud, exactly once, with the command that fixes it.
    // No runtime HTML parsing fallback: the deploy gate guarantees the file.
    http_response_code(503);
    header('Cache-Control: no-store');
    echo '<!DOCTYPE html><html lang="en"><head><meta charset="utf-8">'
       . '<meta name="viewport" content="width=device-width, initial-scale=1">'
       . '<meta name="robots" content="noindex"><title>Catalog missing</title>'
       . '<style>body{font:16px/1.6 system-ui,sans-serif;margin:3rem auto;max-width:44rem;padding:0 1.25rem;color:#16181d;background:#f6f6f2}'
       . 'code{font:15px ui-monospace,Menlo,Consolas,monospace;background:#e8e7fb;padding:.15em .4em;border-radius:4px}</style>'
       . '</head><body><h1>The catalog has not been built</h1>'
       . '<p>This page renders from <code>catalog.json</code>, which is missing or unreadable. Build it from the repository root:</p>'
       . '<p><code>python3 scripts/build_catalog.py</code></p>'
       . '</body></html>';
    exit;
}

$sheets = $catalog['sheets'];
$generated = isset($catalog['generated']) && is_string($catalog['generated']) ? $catalog['generated'] : '';
$catalogVersion = substr(preg_replace('/[^0-9A-Za-z]/', '', $generated), 0, 14);
$stats = isset($catalog['stats']) && is_array($catalog['stats']) ? $catalog['stats'] : [];
$catalogCats = (isset($catalog['categories']) && is_array($catalog['categories'])) ? $catalog['categories'] : [];

// Category name -> ordinal, used for the .k<n> hue class and the lite payload.
$catNames = [];
$catCounts = [];
$catHues = [];
foreach ($catalogCats as $c) {
    if (!isset($c['name'])) continue;
    $catNames[] = (string)$c['name'];
    $catCounts[(string)$c['name']] = (int)($c['count'] ?? 0);
    $hue = (isset($c['hue']) && is_array($c['hue'])) ? $c['hue'] : [];
    $catHues[(string)$c['name']] = [
        'light' => isset($hue['light']) ? (string)$hue['light'] : '#374151',
        'dark'  => isset($hue['dark'])  ? (string)$hue['dark']  : '#526178',
    ];
}
$catIndex = array_flip($catNames);

/* ---------------------------------------------------- popularity + review -- */

$popularity = read_json($ROOT . '/popularity.json') ?: [];
$scores = (isset($popularity['scores']) && is_array($popularity['scores'])) ? $popularity['scores'] : [];
$viewsHistory = (isset($popularity['totalViewsHistory']) && is_array($popularity['totalViewsHistory']))
    ? $popularity['totalViewsHistory'] : [];

$refresh = read_json($ROOT . '/refresh-status.json') ?: [];
$refreshFiles = (isset($refresh['files']) && is_array($refresh['files'])) ? $refresh['files'] : [];
$reviewedThisWeek = 0;
$weekAgo = time() - 7 * 86400;
foreach ($refreshFiles as $f => $entry) {
    if (!is_array($entry) || empty($entry['last_reviewed'])) continue;
    $ts = strtotime((string)$entry['last_reviewed']);
    if ($ts && $ts >= $weekAgo) $reviewedThisWeek++;
}

$paths = read_json($ROOT . '/paths.json') ?: [];
$trails = (isset($paths['paths']) && is_array($paths['paths'])) ? $paths['paths'] : [];

// One git call, cached by the 300 s page cache.
$lastCommitSubject = '';
$lastCommitTime = 0;
$gitOut = cs_git(['log', '-1', '--format=%s%n%ct']);
if ($gitOut['code'] === 0 && $gitOut['out'] !== '') {
    $lines = explode("\n", trim($gitOut['out']));
    $lastCommitSubject = trim($lines[0] ?? '');
    $lastCommitTime = isset($lines[1]) && ctype_digit(trim($lines[1])) ? (int)trim($lines[1]) : 0;
}

/* ------------------------------------------------- normalise sheet records - */

$now = time();
$NEW_WINDOW = 30 * 86400;
$UPDATED_WINDOW = 30 * 86400;
$REVIEW_WINDOW = 90 * 86400;

$shapeCounts = [];
$rows = [];
foreach ($sheets as $s) {
    if (!is_array($s) || empty($s['file'])) continue;
    $file = (string)$s['file'];
    $cat = isset($s['category']) ? (string)$s['category'] : 'Other';
    $shape = (isset($s['shape']) && is_array($s['shape'])) ? array_values(array_map('strval', $s['shape'])) : [];
    foreach ($shape as $sh) $shapeCounts[$sh] = ($shapeCounts[$sh] ?? 0) + 1;
    $reviewedTs = 0;
    if (!empty($s['reviewed'])) {
        $t = strtotime((string)$s['reviewed']);
        if ($t) $reviewedTs = $t;
    }
    // Card images are same-origin; store them relative so 197 cards do not each
    // carry the absolute origin (about 9 KB of HTML across the page).
    $img = isset($s['image']) ? (string)$s['image'] : '';
    if ($img !== '' && str_starts_with($img, 'https://cheatsheets.davidveksler.com/')) {
        $img = substr($img, strlen('https://cheatsheets.davidveksler.com/'));
    }
    $rows[] = [
        'file' => $file,
        'title' => isset($s['title']) ? (string)$s['title'] : $file,
        'description' => isset($s['description']) ? (string)$s['description'] : '',
        'keywords' => (isset($s['keywords']) && is_array($s['keywords'])) ? array_map('strval', $s['keywords']) : [],
        'image' => $img,
        'category' => $cat,
        'catk' => $catIndex[$cat] ?? (count($catNames) ? count($catNames) : 0),
        'shape' => $shape,
        'interactive' => !empty($s['interactive']),
        'words' => (int)($s['words'] ?? 0),
        'tables' => (int)($s['tables'] ?? 0),
        'sections' => (int)($s['sections'] ?? 0),
        'headings' => (isset($s['headings']) && is_array($s['headings'])) ? $s['headings'] : [],
        'outlinks' => (isset($s['outlinks']) && is_array($s['outlinks'])) ? array_map('strval', $s['outlinks']) : [],
        'created' => (int)($s['created'] ?? 0),
        'updated' => (int)($s['updated'] ?? 0),
        'reviewed' => isset($s['reviewed']) && is_string($s['reviewed']) ? $s['reviewed'] : '',
        'reviewedTs' => $reviewedTs,
        'pop' => (float)($scores[$file] ?? 0),
    ];
}
$totalCount = count($rows);
$fieldCount = count($catNames);

// Reverse edges for the server-rendered drawer block.
$linkedFrom = [];
foreach ($rows as $r) {
    foreach ($r['outlinks'] as $target) $linkedFrom[$target][] = $r['file'];
}
$byFile = [];
foreach ($rows as $i => $r) $byFile[$r['file']] = $i;

// Popularity rank, most popular first, over the whole catalog.
$rankOrder = $rows;
usort($rankOrder, fn($a, $b) => $b['pop'] <=> $a['pop']);
$popRank = [];
foreach ($rankOrder as $i => $r) $popRank[$r['file']] = $i + 1;

/* -------------------------------------------------------- request state --- */

$SORTS = [
    'new'      => 'Newest',
    'updated'  => 'Recently updated',
    'popular'  => 'Most popular',
    'reviewed' => 'Recently reviewed',
    'title'    => 'Title',
];
// The old index shipped these values in shared links; keep them working.
$SORT_ALIASES = [
    'date-desc' => 'new', 'recently-updated' => 'updated', 'date-asc' => 'oldest',
    'title-asc' => 'title', 'title-desc' => 'title-desc',
];

$qRaw   = q_str('q');
$catRaw = q_str('cat');
$sortRaw = q_str('sort');
$sort = $SORT_ALIASES[$sortRaw] ?? $sortRaw;
if (!isset($SORTS[$sort]) && !in_array($sort, ['oldest', 'title-desc'], true)) $sort = 'new';

$shapeRaw = q_str('shape');
$activeShapes = array_values(array_filter(array_map('trim', explode(',', $shapeRaw)), fn($x) => $x !== '' && isset($shapeCounts[$x])));
$freshRaw = q_str('fresh');
$VALID_FRESH = ['reviewed90', 'updated30', 'new30'];
$activeFresh = array_values(array_filter(array_map('trim', explode(',', $freshRaw)), fn($x) => in_array($x, $VALID_FRESH, true)));
$wantInteractive = q_str('interactive') === '1';
$sheetParam = q_str('sheet');
$viewParam = q_str('view');
$pathParam = q_str('path');

// Lens: grid (default), map or paths. The value rides on <body data-view>, so
// the CSS decides what is visible and a no-JS reader still gets a real document
// for every lens.
$view = in_array($viewParam, ['grid', 'map', 'paths'], true) ? $viewParam : 'grid';
$activePath = null;
if ($pathParam !== '') {
    foreach ($trails as $tr) {
        if (is_array($tr) && (string)($tr['id'] ?? '') === $pathParam) { $activePath = $tr; break; }
    }
    if ($activePath) $view = 'paths';
}

$catValid = ($catRaw !== '' && isset($catIndex[$catRaw]));
$activeCat = $catValid ? $catRaw : '';
$catUnknown = ($catRaw !== '' && !$catValid);

// noindex on every parameter that expresses client state rather than a distinct
// document, and on an unknown category (which renders the unfiltered index).
$noindex = ($qRaw !== '' || $sortRaw !== '' || $shapeRaw !== '' || $viewParam !== ''
    || $sheetParam !== '' || $pathParam !== '' || $freshRaw !== ''
    || q_str('interactive') !== '' || $catUnknown);

$openSheet = ($sheetParam !== '' && isset($byFile[$sheetParam])) ? $rows[$byFile[$sheetParam]] : null;

/* ------------------------------------------------------------ filtering --- */

// The category is a hard filter (it is its own indexable document). Everything
// else is client state: those cards stay in the DOM and are hidden with a class,
// so the JS filter has the whole collection to work with.
$rendered = $activeCat === '' ? $rows : array_values(array_filter($rows, fn($r) => $r['category'] === $activeCat));

$qLower = mb_strtolower($qRaw);
function row_matches(array $r, string $qLower, array $shapes, array $fresh, bool $wantInteractive, int $now, int $newW, int $updW, int $revW): bool {
    if ($qLower !== '') {
        $hay = mb_strtolower($r['title'] . ' ' . $r['description'] . ' ' . implode(' ', $r['keywords']));
        if (!str_contains($hay, $qLower)) return false;
    }
    if ($shapes) {
        $hit = false;
        foreach ($shapes as $sh) { if (in_array($sh, $r['shape'], true)) { $hit = true; break; } }
        if (!$hit) return false;
    }
    if ($wantInteractive && !$r['interactive']) return false;
    if ($fresh) {
        $hit = false;
        foreach ($fresh as $f) {
            if ($f === 'reviewed90' && $r['reviewedTs'] && $r['reviewedTs'] >= $now - $revW) $hit = true;
            if ($f === 'updated30' && $r['updated'] && $r['updated'] >= $now - $updW) $hit = true;
            if ($f === 'new30' && $r['created'] && $r['created'] >= $now - $newW) $hit = true;
        }
        if (!$hit) return false;
    }
    return true;
}

$visibleCount = 0;
foreach ($rendered as $i => $r) {
    $ok = row_matches($r, $qLower, $activeShapes, $activeFresh, $wantInteractive, $now, $NEW_WINDOW, $UPDATED_WINDOW, $REVIEW_WINDOW);
    $rendered[$i]['_visible'] = $ok;
    if ($ok) $visibleCount++;
}

usort($rendered, function ($a, $b) use ($sort) {
    switch ($sort) {
        case 'updated':    return $b['updated'] <=> $a['updated'];
        case 'popular':    return $b['pop'] <=> $a['pop'];
        case 'reviewed':   return $b['reviewedTs'] <=> $a['reviewedTs'];
        case 'title':      return strcasecmp($a['title'], $b['title']);
        case 'title-desc': return strcasecmp($b['title'], $a['title']);
        case 'oldest':     return $a['created'] <=> $b['created'];
        default:           return $b['created'] <=> $a['created'];
    }
});

$hasFilters = ($qRaw !== '' || $activeShapes || $activeFresh || $wantInteractive);

/* ------------------------------------------------------------ deep cut ----- */
// Deterministic for a full UTC day, drawn from the bottom two-thirds by
// popularity so the long tail gets its turn. Server-rendered, so it caches.
$deepCut = null;
if (!$hasFilters && $activeCat === '' && !$openSheet) {
    $pool = $rankOrder;
    $start = (int)floor(count($pool) / 3);
    $pool = array_slice($pool, $start);
    if ($pool) {
        $today = gmdate('Y-m-d');
        $best = null; $bestKey = '';
        foreach ($pool as $cand) {
            $key = sha1($today . $cand['file']);
            if ($best === null || $key < $bestKey) { $best = $cand; $bestKey = $key; }
        }
        $deepCut = $best;
    }
}

/* ------------------------------------------------------- URL construction -- */

/** Build a query string for the grid state, dropping empty values. */
function grid_url(array $overrides = []): string {
    global $qRaw, $activeCat, $sortRaw, $activeShapes, $activeFresh, $wantInteractive;
    $params = [
        'cat'   => $activeCat,
        'q'     => $qRaw,
        'shape' => implode(',', $activeShapes),
        'fresh' => implode(',', $activeFresh),
        'interactive' => $wantInteractive ? '1' : '',
        'sort'  => $sortRaw,
    ];
    foreach ($overrides as $k => $v) $params[$k] = $v;
    $params = array_filter($params, fn($v) => $v !== '' && $v !== null);
    return $params ? '?' . http_build_query($params) : './';
}

function toggle_list(array $current, string $value): string {
    $i = array_search($value, $current, true);
    if ($i === false) $current[] = $value; else array_splice($current, $i, 1);
    sort($current);
    return implode(',', $current);
}

/* ------------------------------------------------------------- metadata --- */

$SITE_TITLE = 'Cheatsheets by David Veksler: Explore 190+ References';
$SITE_DESC = 'Search inside 190+ interactive reference guides on AI, software, security, crypto custody, radio, health, philosophy and more. Built by a governed Claude Code pipeline with a public git audit trail.';

/**
 * Category description: lead with the count, then name sheets until the string
 * clears the 150-character SEO floor, clamped to 200. No prose claims.
 */
function category_description(string $cat, int $n, array $titles): string {
    $lead = $n . ' cheatsheet' . ($n === 1 ? '' : 's') . ' on ' . $cat . ': ';
    $parts = [];
    $len = mb_strlen($lead);
    foreach ($titles as $t) {
        $t = trim(preg_replace('/\s+/u', ' ', (string)$t));
        if ($t === '') continue;
        $add = ($parts ? 2 : 0) + mb_strlen($t);
        if ($len + $add > 188) {
            if ($parts) break;              // a title is never cut mid-word to fit
            $t = clamp_text($t, max(20, 188 - $len));
            $add = mb_strlen($t);
        }
        $parts[] = $t;
        $len += $add;
    }
    $out = $lead . implode('; ', $parts) . '.';
    if (mb_strlen($out) < 150) {
        // Longest tail that still fits under 200; the shortest always does.
        foreach ([' Dense, verified references from the David Veksler cheatsheet collection.',
                  ' Dense, verified references you can keep open while you work.',
                  ' Dense, verified references.'] as $tail) {
            if (mb_strlen($out . $tail) <= 200) { $out .= $tail; break; }
        }
    }
    if (mb_strlen($out) > 200) $out = clamp_text($out, 199);
    return $out;
}

$pageTitle = $SITE_TITLE;
$pageDesc = $SITE_DESC;
$canonical = $baseUrl;
$h1 = "Find the one page you'll keep open.";
$catIntro = '';

if ($activeCat !== '') {
    $n = count($rendered);
    $spec = $activeCat . ' Cheatsheets (' . $n . ') | David Veksler';
    // The 60-character gate wins over the suffix when the category name is long.
    $pageTitle = mb_strlen($spec) <= 60 ? $spec : $activeCat . ' Cheatsheets (' . $n . ')';
    $firstTitles = array_slice(array_column($rendered, 'title'), 0, 8);
    $pageDesc = category_description($activeCat, $n, $firstTitles);
    $canonical = $baseUrl . '?cat=' . rawurlencode($activeCat);
    $h1 = $activeCat;
    $topThree = array_values(array_filter($rankOrder, fn($r) => $r['category'] === $activeCat));
    $topThree = array_slice(array_column($topThree, 'title'), 0, 3);
    $catIntro = $n . ' reference' . ($n === 1 ? '' : 's') . ' filed under ' . $activeCat . '.'
        . ($topThree ? ' Most read right now: ' . implode('; ', $topThree) . '.' : '');
} elseif ($openSheet) {
    $pageTitle = clamp_text($openSheet['title'], 58);
    $pageDesc = $SITE_DESC;
    $canonical = $baseUrl . $openSheet['file'];
}

/* ------------------------------------------------------- catalog-lite ----- */
// Columnar so the field names are paid for once, not 197 times, and carrying
// only what the DOM cannot already supply. Titles are read off the rendered
// cards rather than duplicated here (11 KB), and keywords, descriptions,
// headings, outlinks and edges arrive with the lazy catalog.json fetch that
// the palette kicks off the moment it opens (another 40 KB saved). Dates are
// days since the epoch, not seconds, because the filter only compares days.
$shapeVocab = array_keys($shapeCounts);
sort($shapeVocab);
$shapeIdx = array_flip($shapeVocab);
$lite = [
    'cats' => $catNames,
    'shapes' => $shapeVocab,
    'f' => [], 'c' => [], 's' => [], 'p' => [],
    'cr' => [], 'up' => [], 'rv' => [], 'ix' => [],
];
foreach ($rows as $r) {
    $lite['f'][] = $r['file'];
    $lite['c'][] = $r['catk'];
    $sh = [];
    foreach ($r['shape'] as $x) if (isset($shapeIdx[$x])) $sh[] = $shapeIdx[$x];
    $lite['s'][] = $sh;
    $lite['p'][] = round($r['pop'], 1);
    $lite['cr'][] = intdiv($r['created'], 86400);
    $lite['up'][] = intdiv($r['updated'], 86400);
    $lite['rv'][] = $r['reviewedTs'] ? intdiv($r['reviewedTs'], 86400) : 0;
    $lite['ix'][] = $r['interactive'] ? 1 : 0;
}

/* ---------------------------------------------------------- sparkline ----- */

$sparkPoints = '';
$sparkLast = 0;
if ($viewsHistory) {
    ksort($viewsHistory);
    $vals = array_slice(array_map('intval', array_values($viewsHistory)), -24);
    if (count($vals) >= 2) {
        $max = max($vals); $min = min($vals);
        $span = max(1, $max - $min);
        $w = 118; $hgt = 26; $n = count($vals);
        $pts = [];
        foreach ($vals as $i => $v) {
            $x = round($i * ($w / ($n - 1)), 1);
            $y = round($hgt - 2 - (($v - $min) / $span) * ($hgt - 4), 1);
            $pts[] = $x . ',' . $y;
        }
        $sparkPoints = implode(' ', $pts);
        $sparkLast = end($vals);
    }
}

/* --------------------------------------------------------- shape labels --- */

$SHAPE_LABEL = [
    'comparison' => 'Comparison', 'procedure' => 'Procedure', 'calculator' => 'Calculator',
    'tracker' => 'Tracker', 'commands' => 'Commands', 'device' => 'Device',
    'essay' => 'Essay', 'timeline' => 'Timeline', 'visual' => 'Visual', 'reference' => 'Reference',
];
function shape_label(string $s): string {
    global $SHAPE_LABEL;
    return $SHAPE_LABEL[$s] ?? ucfirst($s);
}

/* ------------------------------------------------------- card renderer ---- */

/**
 * Card markup is deliberately terse: 197 of these ship in one document, so
 * every attribute is paid for 197 times. Structure is carried by element type
 * rather than class names (see the "Card element map" comment in the CSS):
 *   img = preview, b = category badge (b.r carries the reviewed marker and the
 *   date in its title), h3>a = title link, p = description, em = shape chips,
 *   small = dates,
 *   the trailing bare <a> = Open, span.n = NEW badge. The file is read off the
 *   title link, so it is not repeated in a data attribute.
 */
function render_card(array $r, int $now, int $newWindow, int $reviewWindow, bool $visible = true): void {
    $isNew = $r['created'] && $r['created'] >= $now - $newWindow;
    $fresh = $r['reviewedTs'] && $r['reviewedTs'] >= $now - $reviewWindow;
    $chips = array_map('shape_label', array_slice($r['shape'], 0, 2));
    $f = h($r['file']);
    echo '<article class="c k' . (int)$r['catk'] . ($visible ? '' : ' off') . '">';
    // No width/height attributes: .c img pins aspect-ratio:40/21 in CSS, which
    // reserves the box just as well and costs 26 bytes less on every card.
    if ($r['image']) echo '<img src="' . h($r['image']) . '" alt="" loading="lazy">';
    if ($isNew) echo '<span class="n">New</span>';
    echo $fresh
        ? '<b class="r" title="Reviewed ' . h($r['reviewed']) . '">' . h($r['category']) . '</b>'
        : '<b>' . h($r['category']) . '</b>';
    echo '<h3><a href="' . $f . '">' . h($r['title']) . '</a></h3>';
    echo '<p>' . h(clamp_text($r['description'], 104)) . '</p>';
    if ($chips) echo '<em>' . h(implode(' · ', $chips)) . '</em>';
    echo '<small>' . ($r['created'] ? h(gmdate('M j, Y', $r['created'])) : '')
       . ($r['updated'] ? ' · upd ' . h(gmdate('M j, Y', $r['updated'])) : '') . '</small>';
    echo '<a href="' . $f . '">Open</a></article>' . "\n";
}

/**
 * One trail as a card: title link into ?path=, promise, a progress line the JS
 * fills in from localStorage, and the full ordered list so a reader without
 * JavaScript still gets the trail itself rather than a teaser.
 */
function trail_card(array $tr, array $rows, array $byFile): void {
    $id = (string)($tr['id'] ?? '');
    $steps = is_array($tr['steps'] ?? null) ? $tr['steps'] : [];
    echo '<article class="trail" id="path-' . h($id) . '" data-path="' . h($id) . '">';
    echo '<h3><a href="?view=paths&amp;path=' . h(rawurlencode($id)) . '">' . h((string)($tr['title'] ?? '')) . '</a></h3>';
    echo '<p>' . h((string)($tr['promise'] ?? '')) . '</p>';
    echo '<p class="tprog" data-steps="' . count($steps) . '">' . count($steps) . ' steps</p><ol>';
    foreach ($steps as $st) {
        if (!is_array($st) || empty($st['file'])) continue;
        $sf = (string)$st['file'];
        $stitle = isset($byFile[$sf]) ? $rows[$byFile[$sf]]['title'] : $sf;
        echo '<li><a href="' . h($sf) . '">' . h(clamp_text($stitle, 64)) . '</a><span>' . h((string)($st['why'] ?? '')) . '</span></li>';
    }
    echo '</ol></article>' . "\n";
}
?>
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<script>
/* Theme before first paint: no flash, two statements, no dependencies. */
document.documentElement.className='js';
try{var t=localStorage.getItem('cs-explorer:v1:theme');if(t==='light'||t==='dark')document.documentElement.dataset.theme=t;}catch(e){}
</script>
<link rel="icon" href="data:image/svg+xml,<svg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 100 100%22><text y=%22.9em%22 font-size=%2290%22>🧠</text></svg>">

<title><?php echo h($pageTitle); ?></title>
<meta name="description" content="<?php echo h($pageDesc); ?>">
<meta name="keywords" content="cheatsheets, reference guides, david veksler, AI, software, security, crypto custody, ham radio, health, philosophy, engineering">
<meta name="author" content="David Veksler">
<?php if ($noindex): ?><meta name="robots" content="noindex, follow">
<?php endif; ?><link rel="canonical" href="<?php echo h($canonical); ?>">
<link rel="sitemap" type="application/xml" href="<?php echo h($baseUrl); ?>sitemap.php">
<link rel="alternate" type="text/plain" title="Cheatsheets LLM summary" href="https://cheatsheets.davidveksler.com/llms.txt">
<link rel="alternate" type="application/json" title="Cheatsheets machine-readable catalog" href="https://cheatsheets.davidveksler.com/catalog.json">

<meta property="og:title" content="<?php echo h($pageTitle); ?>">
<meta property="og:description" content="<?php echo h($pageDesc); ?>">
<meta property="og:type" content="website">
<meta property="og:url" content="<?php echo h($canonical); ?>">
<meta property="og:image" content="<?php echo h(rtrim($baseUrl, '/')); ?>/images/cheatsheets-og-portfolio.png">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="A preview card for David Veksler's cheatsheet collection.">
<meta property="og:site_name" content="David Veksler's Cheatsheets">
<meta property="og:locale" content="en_US">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="<?php echo h($pageTitle); ?>">
<meta name="twitter:description" content="<?php echo h($pageDesc); ?>">
<meta name="twitter:image" content="<?php echo h(rtrim($baseUrl, '/')); ?>/images/cheatsheets-og-portfolio.png">
<meta name="twitter:image:alt" content="A preview card for David Veksler's cheatsheet collection.">
<meta name="twitter:creator" content="@HeroicLife">

<script type="application/ld+json">
<?php
// Items trimmed to name / url / genre to stay inside the HTML budget with all
// 197 cards server-rendered (see the spec's Budgets table).
$ld = [
    '@context' => 'https://schema.org',
    '@type' => 'CollectionPage',
    'name' => $pageTitle,
    'description' => $pageDesc,
    'url' => $canonical,
    'author' => ['@type' => 'Person', 'name' => 'David Veksler', 'url' => 'https://www.linkedin.com/in/davidveksler/'],
    'publisher' => ['@type' => 'Person', 'name' => 'David Veksler', 'url' => 'https://www.linkedin.com/in/davidveksler/'],
];
$items = [];
$pos = 0;
foreach ($rendered as $r) {
    if (!$r['_visible']) continue;
    $pos++;
    // Minimum viable ListItem: the spec's Budgets table authorises trimming the
    // items when 197 server-rendered cards squeeze the HTML budget, and every
    // one of these URLs is also a real <a href> on the page and a sitemap entry.
    $items[] = ['@type' => 'ListItem', 'position' => $pos, 'url' => $baseUrl . $r['file']];
}
$ld['mainEntity'] = ['@type' => 'ItemList', 'numberOfItems' => count($items), 'itemListElement' => $items];
echo json_encode($ld, JSON_UNESCAPED_SLASHES | JSON_UNESCAPED_UNICODE);
?>
</script>

<style>
/* ============================================================================
   Chart Room: paper and ink, thin rules, small-caps labels, monospace numerals.
   Colour encodes category and nothing else.

   Category hue pairs (light / dark), generated by scripts/build_catalog.py
   --print-hues and checked to 3:1 against the dark page (#0e1013) for
   non-text use. Hue is never used for body text.

     AI & Safety                   #0891b2 / #0891b2
     Software & DevOps             #4338ca / #564ccf
     Security & Privacy            #dc2626 / #dc2626
     Risk & Preparedness           #0f766e / #0f766e
     Bitcoin & Finance             #d97706 / #d97706
     Crypto Custody & Compliance   #a21caf / #a21caf
     Martial Arts & Strategy       #9f1239 / #bf1644
     Firearms & Military           #3f6212 / #456b14
     Radio                         #1e40af / #2b54db
     Health & Fitness              #065f46 / #076d51
     Economics & Politics          #7c2d12 / #a93d18
     Philosophy & Religion         #6b21a8 / #892cd5
     Engineering & Science         #0c4a6e / #116697
     Home & Lifestyle              #0f766e / #0f766e
     Life Admin & Consumer Defense #4b5563 / #566172
     (fallback / Other)            #374151 / #526178
   ========================================================================== */
@layer base, layout, components, state;

@layer base {
:root{
  color-scheme: light dark;
  --page: light-dark(#f6f6f2, #0e1013);
  --surface: light-dark(#ffffff, #161a20);
  --raised: light-dark(#ffffff, #1c2129);
  --rule: light-dark(#d9d9d2, #2a3038);
  --ink: light-dark(#16181d, #e8e9ec);
  --muted: light-dark(#5b6068, #9aa1ab);
  --accent: light-dark(#4338ca, #a5b4fc);
  --accent-surface: light-dark(#e8e7fb, #26294a);
  --success: light-dark(#15803d, #4ade80);
  --sans: system-ui, -apple-system, "Segoe UI", Roboto, sans-serif;
  --mono: ui-monospace, "SF Mono", Menlo, Consolas, monospace;
  --cat: var(--muted);
}
:root[data-theme="light"]{ color-scheme: light; }
:root[data-theme="dark"]{ color-scheme: dark; }
<?php foreach ($catNames as $i => $cn): $hu = $catHues[$cn]; ?>
.k<?php echo $i; ?>{--cat:light-dark(<?php echo h($hu['light']); ?>,<?php echo h($hu['dark']); ?>)}
<?php endforeach; ?>
*,*::before,*::after{box-sizing:border-box}
body{margin:0;background:var(--page);color:var(--ink);font:15px/1.55 var(--sans);text-wrap:pretty;-webkit-text-size-adjust:100%}
h1,h2,h3{text-wrap:balance;margin:0 0 .4em;line-height:1.2}
h1{font-size:clamp(34px,5vw,44px);font-weight:650;letter-spacing:-.015em}
h2{font-size:22px;font-weight:620}
h3{font-size:17px;font-weight:600}
a{color:var(--accent)}
a:where(.plain,.brand,.chip,.nbr),.c h3 a,.c>a,.deepcut h3 a{text-decoration:none}
:focus-visible{outline:2px solid var(--accent);outline-offset:2px;border-radius:3px}
button{font:inherit;color:inherit}
.sr{position:absolute;width:1px;height:1px;padding:0;margin:-1px;overflow:hidden;clip:rect(0 0 0 0);white-space:nowrap;border:0}
.skip{position:absolute;left:-999px;top:0;background:var(--raised);padding:.6rem 1rem;z-index:60}
.skip:focus{left:.5rem;top:.5rem}
.num{font-family:var(--mono);font-variant-numeric:tabular-nums}
.lbl{font-size:11px;letter-spacing:.09em;text-transform:uppercase;color:var(--muted);font-weight:600}
}

@layer layout {
.wrap{max-width:1440px;margin:0 auto;padding:0 clamp(14px,3vw,28px)}
.topbar{position:sticky;top:0;z-index:30;background:var(--page);border-bottom:1px solid var(--rule)}
.topbar .wrap{display:flex;align-items:center;gap:12px;min-height:52px}
.brand{font-weight:650;color:var(--ink);letter-spacing:-.01em;white-space:nowrap}
.topnav{display:flex;gap:14px;margin-left:auto;font-size:13px;align-items:center}
.topnav a{color:var(--muted);text-decoration:none}
.topnav a:hover{color:var(--ink);text-decoration:underline}
.tbtn{display:inline-flex;align-items:center;gap:6px;background:var(--surface);border:1px solid var(--rule);border-radius:6px;padding:5px 9px;font-size:13px;cursor:pointer;color:var(--ink)}
.tbtn:hover{border-color:var(--accent)}
.tbtn kbd{font-family:var(--mono);font-size:11px;color:var(--muted);border:1px solid var(--rule);border-radius:3px;padding:0 4px}
.hero{padding:clamp(18px,3.5vh,34px) 0 clamp(12px,2vh,18px)}
.hero p.lead{color:var(--muted);max-width:60ch;margin:0 0 16px;font-size:16px}
.herosearch{display:flex;gap:8px;max-width:620px}
.herosearch input{flex:1;min-width:0;font:16px var(--sans);padding:11px 14px;border:1px solid var(--rule);border-radius:8px;background:var(--surface);color:var(--ink)}
.herosearch input:focus-visible{border-color:var(--accent)}
.herosearch button{padding:11px 16px;border:1px solid var(--accent);background:var(--accent);color:var(--page);border-radius:8px;font-weight:600;cursor:pointer}
.herohint{margin:10px 0 0;font-size:13px;color:var(--muted);display:flex;flex-wrap:wrap;gap:10px;align-items:center}
.linkbtn{background:none;border:0;padding:0;color:var(--accent);cursor:pointer;text-decoration:underline;font-size:13px}
.explorer{display:grid;grid-template-columns:240px minmax(0,1fr);gap:26px;align-items:start;padding-bottom:36px}
.rail{position:sticky;top:64px;max-height:calc(100vh - 80px);overflow-y:auto;padding-right:4px;font-size:13px}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:20px}
footer.site{border-top:1px solid var(--rule);padding:22px 0 34px;color:var(--muted);font-size:13px}
footer.site a{color:var(--muted)}
/* Under 600 px the hero drops the lead paragraph so it stays under 30vh with the
   search box as its focal element; the Pulse strip directly below carries the
   same counts, so nothing is actually lost. */
@media (max-width:600px){
  .hero{padding:6px 0 8px}
  .hero h1{font-size:clamp(27px,7.4vw,34px);margin-bottom:.25em}
  .hero p.lead{display:none}
  .herohint{gap:14px;margin-top:8px}
}
@media (max-width:860px){
  .explorer{grid-template-columns:1fr;gap:14px}
  .rail{position:static;max-height:none}
  .topnav a.hidesm{display:none}
}
}

@layer components {
/* --- Pulse strip ------------------------------------------------------- */
.pulse{border-top:1px solid var(--rule);border-bottom:1px solid var(--rule);padding:10px 0;margin-bottom:14px}
.pulse .wrap{display:flex;flex-wrap:wrap;gap:8px 20px;align-items:center;font-size:13px;color:var(--muted)}
.pulse b{font-weight:620;color:var(--ink)}
.pulse .sep{color:var(--rule)}
.spark{display:inline-flex;align-items:center;gap:6px;text-decoration:none;color:var(--muted)}
.spark svg{display:block}
.band{font-size:14px;color:var(--muted);padding:0 0 18px}
.band p{margin:0;max-width:78ch}

/* --- Facet rail -------------------------------------------------------- */
.fgroup{border:0;margin:0 0 16px;padding:0}
.fgroup .lbl{display:block;margin-bottom:6px}
.fgroup ul{list-style:none;margin:0;padding:0}
.fgroup li a{display:flex;gap:8px;align-items:baseline;padding:3px 6px;border-radius:5px;text-decoration:none;color:var(--ink)}
.fgroup li a:hover{background:var(--accent-surface)}
.fgroup li a[aria-pressed="true"]{background:var(--accent-surface);font-weight:620}
.fgroup .cdot{width:8px;height:8px;border-radius:50%;background:var(--cat);flex:none;translate:0 -1px}
.fgroup .n{margin-left:auto;font-family:var(--mono);font-size:12px;color:var(--muted)}
.railtoggle{display:none}
@media (max-width:860px){
  .railtoggle{display:block;width:100%;text-align:left;padding:9px 12px;border:1px solid var(--rule);border-radius:8px;background:var(--surface);cursor:pointer}
  .rail .fbody{display:none}
  .rail.open .fbody{display:block;padding-top:12px}
}

/* --- Toolbar and chips ------------------------------------------------- */
.toolbar{display:flex;flex-wrap:wrap;gap:10px 16px;align-items:center;padding:0 0 14px}
.count{font-family:var(--mono);font-size:13px;color:var(--muted)}
.chips{display:flex;flex-wrap:wrap;gap:6px}
.chip{display:inline-flex;align-items:center;gap:6px;border:1px solid var(--rule);border-radius:999px;padding:2px 10px;font-size:12px;text-decoration:none;color:var(--ink);background:var(--surface)}
.chip:hover{border-color:var(--accent)}
.chip .x{color:var(--muted)}
.sorts{display:flex;gap:4px;margin-left:auto;flex-wrap:wrap}
.sorts a{font-size:12px;padding:3px 9px;border:1px solid var(--rule);border-radius:999px;text-decoration:none;color:var(--muted);background:var(--surface)}
.sorts a[aria-current="true"]{color:var(--ink);border-color:var(--accent);font-weight:620}

/* --- Cards -------------------------------------------------------------
   Card element map (markup is terse because it ships 197 times):
     img = preview   b = category badge (b.r = reviewed, title = the date)
     h3>a = title    p  = description     em = shape chips
     small = dates   .c>a = Open link      span.n = NEW badge
   ---------------------------------------------------------------------- */
.c{container-type:inline-size;position:relative;background:var(--surface);border:1px solid var(--rule);border-top:3px solid var(--cat);border-radius:8px;overflow:hidden;display:flex;flex-direction:column;cursor:pointer}
.c.off{display:none}
.c img{width:100%;aspect-ratio:40/21;object-fit:contain;display:block;background:color-mix(in srgb,var(--cat) 9%,var(--surface));border-bottom:1px solid var(--rule)}
.c>span.n{position:absolute;top:8px;right:8px;background:var(--success);color:var(--page);font-size:10px;font-weight:700;letter-spacing:.08em;text-transform:uppercase;padding:2px 7px;border-radius:4px}
.c b{align-self:flex-start;margin:12px 14px 8px;font-size:11px;font-weight:500;letter-spacing:.02em;padding:1px 8px;border-radius:999px;border:1px solid color-mix(in srgb,var(--cat) 45%,transparent);background:color-mix(in srgb,var(--cat) 12%,transparent);color:var(--ink)}
.c b.r::after{content:"";display:inline-block;width:6px;height:6px;border-radius:50%;background:var(--success);margin-left:7px;translate:0 -1px}
.c h3{margin:0 14px 6px}
.c h3 a{color:var(--ink)}
.c:hover h3 a{text-decoration:underline}
.c>p{margin:0 14px 10px;font-size:13.5px;color:var(--muted);display:-webkit-box;-webkit-box-orient:vertical;-webkit-line-clamp:3;line-clamp:3;overflow:hidden}
.c em{font-style:normal;font-size:10.5px;letter-spacing:.05em;text-transform:uppercase;color:var(--muted);margin:0 14px 8px}
.c small{margin:auto 14px 10px;font-family:var(--mono);font-size:11.5px;color:var(--muted);font-variant-numeric:tabular-nums}
.c>a{display:block;padding:9px 14px;border-top:1px solid var(--rule);font-size:13px;font-weight:600;color:var(--accent);text-align:center}
.c>a:hover{background:var(--accent-surface)}
.c.seen h3 a{color:var(--muted)}
@container (max-width: 339px){ .c img{display:none} }

.deepcut{margin:0 0 20px;padding:14px 16px;border:1px solid var(--rule);border-left:3px solid var(--cat);border-radius:8px;background:var(--surface)}
.deepcut h2{font-size:13px;letter-spacing:.09em;text-transform:uppercase;color:var(--muted);margin-bottom:6px}
.deepcut p{margin:.3em 0 0;color:var(--muted);font-size:13.5px}
.empty{padding:28px 0;color:var(--muted)}

/* --- Sheet detail (no-JS ?sheet=) and drawer share this markup --------- */
.crow{display:flex;align-items:center;gap:6px;flex-wrap:wrap;margin:0 0 10px}
.cbadge{font-size:11px;letter-spacing:.02em;padding:1px 8px;border-radius:999px;border:1px solid color-mix(in srgb,var(--cat) 45%,transparent);background:color-mix(in srgb,var(--cat) 12%,transparent);color:var(--ink)}
.detail{border:1px solid var(--rule);border-top:3px solid var(--cat);border-radius:8px;background:var(--surface);padding:16px 18px;margin:0 0 20px}
.detail h2{margin-bottom:8px}
.detail .facts{font-family:var(--mono);font-size:12.5px;color:var(--muted);font-variant-numeric:tabular-nums}
.detail ul{margin:.3em 0 1em;padding-left:1.1em;font-size:13.5px}
.detail li{margin:.15em 0}
.acts{display:flex;gap:8px;flex-wrap:wrap;margin-top:10px}
.acts a,.acts button{font-size:13px;padding:6px 12px;border:1px solid var(--rule);border-radius:6px;background:var(--surface);text-decoration:none;color:var(--ink);cursor:pointer}
.acts .primary{background:var(--accent);border-color:var(--accent);color:var(--page);font-weight:600}
.acts [disabled]{opacity:.5;cursor:not-allowed}

/* --- Paths ------------------------------------------------------------- */
.paths{padding:26px 0;border-top:1px solid var(--rule)}
.trails{display:grid;grid-template-columns:repeat(auto-fill,minmax(320px,1fr));gap:18px;margin-top:14px}
.trail{border:1px solid var(--rule);border-radius:8px;background:var(--surface);padding:14px 16px}
.trail h3{margin-bottom:4px}
.trail>p{margin:0 0 10px;color:var(--muted);font-size:13.5px}
.trail ol{margin:0;padding-left:1.3em;font-size:13.5px}
.trail li{margin:.35em 0}
.trail li span{display:block;color:var(--muted);font-size:12.5px}

/* --- Lens switcher ----------------------------------------------------- */
.lenses{display:flex;gap:6px;margin:0 0 16px;flex-wrap:wrap}
.lenses a{font-size:13px;padding:5px 15px;border:1px solid var(--rule);border-radius:999px;text-decoration:none;color:var(--muted);background:var(--surface)}
.lenses a:hover{border-color:var(--accent)}
.lenses a[aria-current="page"]{color:var(--ink);border-color:var(--accent);background:var(--accent-surface);font-weight:620}

/* --- Map lens ----------------------------------------------------------
   The canvas is the only pixel surface on the page. It redraws on interaction
   and never in a loop; every colour it paints is read back out of the tokens
   above through a probe element, so the theme toggle repaints it correctly. */
#mapwrap{display:none}
.maptop{display:flex;flex-wrap:wrap;gap:6px;align-items:center;margin:0 0 10px}
.lgd{display:inline-flex;align-items:center;gap:6px;border:1px solid var(--rule);border-radius:999px;background:var(--surface);padding:2px 10px;font-size:12px;cursor:pointer;color:var(--ink)}
.lgd:hover{border-color:var(--accent)}
.lgd .cdot{width:8px;height:8px;border-radius:50%;background:var(--cat);flex:none}
.lgd .n{font-family:var(--mono);font-size:11px;color:var(--muted)}
.lgd[aria-pressed="true"]{border-color:var(--accent);background:var(--accent-surface);font-weight:620}
.maptop .grow{margin-left:auto;display:flex;gap:6px}
#mapfig{position:relative;margin:0;border:1px solid var(--rule);border-radius:8px;background:var(--surface);overflow:hidden;touch-action:none;height:clamp(360px,calc(100dvh - 190px),840px)}
#mapc{display:block;width:100%;height:100%;cursor:grab}
#mapc.drag{cursor:grabbing}
#maptip{position:absolute;pointer-events:none;background:var(--raised);border:1px solid var(--rule);border-radius:6px;padding:6px 10px;font-size:12.5px;max-width:280px;z-index:2;box-shadow:0 6px 18px rgb(0 0 0 / .2)}
#maptip[hidden]{display:none}
#maptip b{display:block;font-weight:620}
#maptip span{color:var(--muted);font-family:var(--mono);font-size:11.5px}
#egoAll{position:absolute;left:12px;bottom:12px;background:var(--raised);border:1px solid var(--accent);color:var(--ink);border-radius:6px;padding:6px 12px;font-size:13px;cursor:pointer}
#egoAll[hidden]{display:none}
.maphint{margin:8px 0 0;font-size:12.5px;color:var(--muted)}
#maplist{margin:14px 0 0;font-size:13.5px}
#maplist[hidden]{display:none}
#maplist>ul{list-style:none;margin:0;padding:0;columns:2;column-gap:28px}
#maplist>ul>li{break-inside:avoid;margin:0 0 12px}
#maplist ul ul{margin:.2em 0 .6em;padding-left:1.1em;color:var(--muted);font-size:12.5px}
#maplist h3{font-size:13px;letter-spacing:.06em;text-transform:uppercase;color:var(--muted);margin:0 0 4px}
@media (max-width:760px){#maplist>ul{columns:1}}
/* Phone: the 15 legend chips would otherwise push the canvas a screen and a
   half down, so the controls take their own row and the chips scroll. */
@media (max-width:700px){
  .maptop{max-height:104px;overflow-y:auto;align-content:flex-start}
  .maptop .grow{order:-1;margin-left:0;flex:1 0 100%}
  #mapfig{height:min(64dvh,520px)}
  .maphint{display:none}
}

/* --- Paths lens --------------------------------------------------------- */
.trail h3 a{color:var(--ink);text-decoration:none}
.trail h3 a:hover{text-decoration:underline}
.tprog{margin:0 0 8px;font-family:var(--mono);font-size:12px;color:var(--muted);font-variant-numeric:tabular-nums}
.tprog .bar{display:inline-block;width:70px;height:5px;border-radius:3px;background:var(--rule);vertical-align:middle;margin-left:6px;overflow:hidden}
.tprog .bar i{display:block;height:100%;background:var(--success);width:0}
.trail.open{border-top:3px solid var(--accent)}
.stepper{display:flex;gap:14px;list-style:none;margin:14px 0 6px;padding:0;align-items:stretch}
.stepper li{flex:1 1 0;min-width:0;border-top:2px solid var(--rule);padding:10px 0 0;position:relative}
.stepper li.done{border-top-color:var(--success)}
.stepper .sn{display:inline-flex;align-items:center;justify-content:center;width:22px;height:22px;border-radius:50%;border:1px solid var(--rule);background:var(--surface);font-family:var(--mono);font-size:12px;margin-bottom:6px}
.stepper li.done .sn{border-color:var(--success);color:var(--success)}
.stepper a{display:block;font-weight:600;font-size:14px;color:var(--ink);text-decoration:none;margin-bottom:4px}
.stepper a:hover{text-decoration:underline}
.stepper .why{display:block;color:var(--muted);font-size:12.5px;margin-bottom:8px}
.stepbtn{margin-top:auto;background:var(--surface);border:1px solid var(--rule);border-radius:999px;padding:2px 11px;font-size:12px;cursor:pointer;color:var(--muted)}
.stepbtn:hover{border-color:var(--accent);color:var(--ink)}
.stepbtn[aria-pressed="true"]{border-color:var(--success);color:var(--success);font-weight:620}
.related{margin-top:26px}
@media (max-width:760px){
  .stepper{display:block}
  .stepper li{border-top:0;border-left:2px solid var(--rule);padding:0 0 14px 14px;margin-left:10px}
  .stepper li.done{border-top:0;border-left-color:var(--success)}
  .stepper .sn{position:absolute;left:-12px;top:0}
  .stepper li>*:first-child+a{margin-top:0}
}

/* --- Signup band + footer --------------------------------------------- */
.signup{border-top:1px solid var(--rule);background:var(--surface);padding:22px 0}
.signup .wrap{display:flex;flex-wrap:wrap;gap:14px 28px;align-items:center}
.signup .copy{flex:1 1 280px}
.signup h2{font-size:17px;margin-bottom:2px}
.signup p{margin:0;color:var(--muted);font-size:13px}
.email-signup{display:flex;gap:8px;flex-wrap:wrap;align-items:center}
.email-signup input[type=email]{padding:9px 12px;border:1px solid var(--rule);border-radius:6px;background:var(--page);color:var(--ink);font:14px var(--sans);min-width:230px}
.email-signup button{padding:9px 16px;border:1px solid var(--accent);background:var(--accent);color:var(--page);border-radius:6px;font-weight:600;cursor:pointer}
.signup-status{width:100%;margin:0;font-size:13px;font-weight:600;color:var(--success)}
.signup-status.is-error{color:light-dark(#b91c1c,#fca5a5)}
.hp{position:absolute;left:-9999px;width:1px;height:1px;overflow:hidden}
footer.site .frow{display:flex;flex-wrap:wrap;gap:8px 16px;align-items:center}
footer.site .fcta{margin-left:auto}

/* --- Palette ----------------------------------------------------------- */
dialog#palette{width:min(640px,94vw);max-height:70vh;margin:12vh auto auto;padding:0;border:1px solid var(--rule);border-radius:12px;background:var(--raised);color:var(--ink);box-shadow:0 18px 48px rgb(0 0 0 / .28);overflow:hidden}
dialog::backdrop{background:rgb(9 10 12 / .45)}
#palette form{margin:0;border-bottom:1px solid var(--rule)}
#palette input{width:100%;border:0;background:transparent;color:var(--ink);font:17px var(--sans);padding:15px 18px;outline:none}
#pres{list-style:none;margin:0;padding:6px;overflow-y:auto;max-height:46vh}
#pres li{border-radius:7px}
#pres .row{display:flex;gap:9px;align-items:baseline;padding:7px 10px;cursor:pointer;text-decoration:none;color:var(--ink)}
#pres .row.sel{background:var(--accent-surface)}
#pres .row .cdot{width:8px;height:8px;border-radius:50%;background:var(--cat);flex:none}
#pres .row .meta{margin-left:auto;font-size:11px;color:var(--muted);font-family:var(--mono)}
#pres .sub{padding:4px 10px 4px 34px;font-size:13px;color:var(--muted);text-decoration:none;display:block;border-radius:6px}
#pres .sub.sel{background:var(--accent-surface);color:var(--ink)}
#pres .sub .hash{color:var(--accent);font-family:var(--mono)}
#pres .glabel{padding:8px 10px 3px}
#pfoot{border-top:1px solid var(--rule);padding:7px 12px;font-size:11.5px;color:var(--muted);display:flex;gap:14px;flex-wrap:wrap}
#pfoot kbd{font-family:var(--mono);border:1px solid var(--rule);border-radius:3px;padding:0 4px}

/* --- Drawer ------------------------------------------------------------ */
#drawer{position:fixed;top:0;right:0;width:420px;max-width:100vw;height:100dvh;overflow-y:auto;background:var(--raised);border-left:1px solid var(--rule);padding:18px 20px 40px;z-index:40;box-shadow:-8px 0 32px rgb(0 0 0 / .18)}
#drawer[hidden]{display:none}
#drawer .dhead{display:flex;align-items:flex-start;gap:10px}
#drawer .dclose{margin-left:auto;background:none;border:1px solid var(--rule);border-radius:6px;padding:3px 9px;cursor:pointer}
#drawer .dshot{aspect-ratio:40/21;width:100%;border:1px solid var(--rule);border-radius:6px;overflow:hidden;background:var(--surface);margin:10px 0}
#drawer .dshot img{width:100%;height:100%;object-fit:contain;display:block}
#drawer .nbr{display:block;padding:4px 6px;border-radius:5px;font-size:13.5px;text-decoration:none;color:var(--ink);cursor:pointer}
#drawer .nbr:hover{background:var(--accent-surface)}
@media (max-width:700px){
  #drawer{top:auto;bottom:0;right:0;left:0;width:auto;height:85dvh;border-left:0;border-top:1px solid var(--rule);border-radius:14px 14px 0 0}
  #drawer::before{content:"";display:block;width:40px;height:4px;border-radius:2px;background:var(--rule);margin:0 auto 12px}
}

dialog#help{width:min(420px,92vw);border:1px solid var(--rule);border-radius:12px;background:var(--raised);color:var(--ink);padding:18px 20px}
dialog#help dl{display:grid;grid-template-columns:auto 1fr;gap:6px 14px;margin:10px 0 0;font-size:13.5px}
dialog#help dt{font-family:var(--mono);color:var(--muted)}
dialog#help dd{margin:0}
.toast{position:fixed;left:50%;bottom:22px;translate:-50% 0;background:var(--raised);border:1px solid var(--rule);border-radius:8px;padding:9px 16px;font-size:13.5px;z-index:70;box-shadow:0 8px 24px rgb(0 0 0 / .22)}
.toast[hidden]{display:none}
}

@layer state {
@media (prefers-reduced-motion: no-preference){
  .c{transition:transform .12s ease-out,border-color .12s ease-out}
  .c:hover{transform:translateY(-2px);border-color:var(--accent);border-top-color:var(--cat)}
  #drawer{animation:slidein .2s ease-out}
  dialog#palette{animation:fadein .12s ease-out}
  @keyframes slidein{from{transform:translateX(16px);opacity:.4}to{transform:none;opacity:1}}
  @keyframes fadein{from{opacity:0}to{opacity:1}}
}
@media (prefers-reduced-motion: reduce){
  .c:hover{border-color:var(--accent)}
}
/* Lens visibility. `html.js` is set by the pre-paint head script, so the rules
   that only make sense with a canvas never fire for a no-JS reader: ?view=map
   then keeps the grid plus one explanatory line. */
body[data-view="grid"] .paths,
body[data-view="map"] .paths,
body[data-view="paths"] .explorer{display:none}
.nojsmap{display:none}
body[data-view="map"] .nojsmap{display:block;margin:0 0 16px;color:var(--muted);font-size:13.5px}
html.js body[data-view="map"] .nojsmap{display:none}
html.js body[data-view="map"] .results{display:none}
html.js body[data-view="map"] #mapwrap{display:block}

/* Print: the Grid becomes a two-column list of title, URL and category; the
   Paths section keeps its ordered lists, which are already its print form. */
@media print{
  .topbar,.hero,.pulse,.band,.rail,.toolbar,.signup,.skip,#palette,#drawer,#help,#toast,
  .lenses,#mapwrap,
  .c img,.c>a,.c em,.c small,.c>p{display:none !important}
  body{background:#fff;color:#000}
  .explorer{display:block}
  .grid{display:block;column-count:2;column-gap:24px}
  .c{break-inside:avoid;border:0;border-top:1px solid #999;border-radius:0;margin:0 0 8px;display:block;padding:4px 0}
  .c b{margin:0;border:0;background:none;padding:0;font-size:10px;color:#555;display:block}
  .c h3{margin:0;font-size:12px}
  .c h3 a{color:#000}
  .c h3 a::after{content:" · " attr(href);font-family:monospace;font-weight:400;font-size:10px;color:#555}
  .trails{display:block;column-count:2}
  .trail{break-inside:avoid;border:0;padding:0;margin:0 0 10px}
}
}
</style>
<!-- Clarity tracking code for https://cheatsheets.davidveksler.com/ -->
<script>
    (function(c,l,a,r,i,t,y){
        c[a]=c[a]||function(){(c[a].q=c[a].q||[]).push(arguments)};
        t=l.createElement(r);t.async=1;t.src="https://www.clarity.ms/tag/"+i+"?ref=bwt";
        y=l.getElementsByTagName(r)[0];y.parentNode.insertBefore(t,y);
    })(window, document, "clarity", "script", "y8ixg9wg4h");
</script>
</head>
<body data-view="<?php echo h($view); ?>">
<a class="skip" href="#grid">Skip to the grid</a>

<header class="topbar">
  <div class="wrap">
    <a class="brand" href="./">Cheatsheets<span class="sr"> home</span></a>
    <nav class="topnav" aria-label="Site">
      <a class="hidesm" href="how-its-built.html">How it's built</a>
      <a class="hidesm" href="history.php">Change history</a>
      <a class="hidesm" href="popularity.php">Popularity</a>
      <button class="tbtn" id="openPalette" type="button" aria-haspopup="dialog">
        <svg width="14" height="14" viewBox="0 0 16 16" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="1.6"><circle cx="7" cy="7" r="4.5"/><path d="M10.5 10.5 14 14"/></svg>
        Search <kbd>⌘K</kbd>
      </button>
      <button class="tbtn" id="themeToggle" type="button" aria-label="Toggle dark mode" title="Toggle theme (t)">
        <svg width="14" height="14" viewBox="0 0 16 16" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M13.2 9.6A5.6 5.6 0 0 1 6.4 2.8 5.6 5.6 0 1 0 13.2 9.6Z"/></svg>
      </button>
    </nav>
  </div>
</header>

<main>
<section class="hero">
  <div class="wrap">
    <h1><?php echo h($h1); ?></h1>
    <?php if ($activeCat !== ''): ?>
      <p class="lead"><?php echo h($catIntro); ?></p>
    <?php else: ?>
      <p class="lead"><span class="num"><?php echo (int)$totalCount; ?></span> dense, verified references across <span class="num"><?php echo (int)$fieldCount; ?></span> fields, built by one person plus AI agents under a public, git-audited spec. The search box reads inside every page, not just the titles.</p>
    <?php endif; ?>
    <form class="herosearch" method="get" action="./" role="search">
      <?php if ($activeCat !== ''): ?><input type="hidden" name="cat" value="<?php echo h($activeCat); ?>"><?php endif; ?>
      <label class="sr" for="heroq">Search the cheatsheets</label>
      <input type="search" id="heroq" name="q" value="<?php echo h($qRaw); ?>" placeholder="Search inside every page (try torque, ukemi, ufw)" autocomplete="off" spellcheck="false">
      <button type="submit">Search</button>
    </form>
    <p class="herohint">
      <span>Press <kbd class="num">⌘K</kbd> or <kbd class="num">/</kbd> to search section headings.</span>
      <button class="linkbtn" type="button" id="surprise">Surprise me</button>
      <button class="linkbtn" type="button" id="helpBtn">Keyboard map</button>
    </p>
  </div>
</section>

<section class="pulse" aria-label="Collection pulse">
  <div class="wrap">
    <span><b class="num"><?php echo (int)$totalCount; ?></b> references <span class="sep">·</span>
      <b class="num"><?php echo (int)$fieldCount; ?></b> fields <span class="sep">·</span>
      <b class="num"><?php echo (int)($stats['sections'] ?? 0); ?></b> sections indexed <span class="sep">·</span>
      <b class="num"><?php echo (int)($stats['edges'] ?? 0); ?></b> cross-links</span>
    <?php if ($lastCommitSubject !== '' && $lastCommitTime): ?>
    <span>Last change: <a class="plain" href="history.php"><b><?php echo h(clamp_text($lastCommitSubject, 62)); ?></b></a> <span class="num"><?php echo h(rel_time($lastCommitTime)); ?></span></span>
    <?php endif; ?>
    <?php if ($reviewedThisWeek > 0): ?>
    <span>Reviewed this week: <b class="num"><?php echo (int)$reviewedThisWeek; ?></b></span>
    <?php endif; ?>
    <?php if ($sparkPoints !== ''): ?>
    <a class="spark" href="popularity.php" title="Site views, last 24 days">
      <svg width="118" height="26" viewBox="0 0 118 26" aria-label="Site views over the last 24 days" role="img"><polyline points="<?php echo h($sparkPoints); ?>" fill="none" stroke="currentColor" stroke-width="1.4" stroke-linejoin="round"/></svg>
      <span class="num"><?php echo number_format($sparkLast); ?> views/day</span>
    </a>
    <?php endif; ?>
    <?php
    $trend = array_slice(array_filter($rankOrder, fn($r) => $r['pop'] > 0), 0, 3);
    if ($trend): ?>
    <span>Trending: <?php $first = true; foreach ($trend as $t) { echo $first ? '' : ' <span class="sep">·</span> '; $first = false; echo '<a class="plain" href="' . h($t['file']) . '">' . h(clamp_text($t['title'], 34)) . '</a>'; } ?></span>
    <?php endif; ?>
  </div>
</section>

<div class="band"><div class="wrap">
  <p>Every sheet here is produced by a governed Claude Code pipeline: a version-controlled spec as acceptance criteria, primary-source research, a self-verification gate, and a public git audit trail. <a href="how-its-built.html">Read how it is built</a> or <a href="https://github.com/DavidVeksler/CheatSheets" rel="noopener">browse the source on GitHub</a>.</p>
</div></div>

<div class="wrap">
<?php if ($openSheet):
    $os = $openSheet;
    $inbound = $linkedFrom[$os['file']] ?? [];
    ?>
<section class="detail k<?php echo (int)$os['catk']; ?>" id="sheet-detail">
  <p class="crow"><span class="cbadge"><?php echo h($os['category']); ?></span><?php foreach (array_slice($os['shape'], 0, 3) as $sc): ?><span class="cbadge"><?php echo h(shape_label($sc)); ?></span><?php endforeach; ?></p>
  <h2><?php echo h($os['title']); ?></h2>
  <p><?php echo h($os['description']); ?></p>
  <?php if ($os['headings']): ?>
  <p class="lbl">What's inside</p>
  <ul>
    <?php foreach (array_slice($os['headings'], 0, 14) as $hd):
        $ht = isset($hd['text']) ? (string)$hd['text'] : '';
        $hi = isset($hd['id']) && $hd['id'] ? (string)$hd['id'] : ''; ?>
    <li><?php if ($hi): ?><a href="<?php echo h($os['file']); ?>#<?php echo h($hi); ?>"><?php echo h($ht); ?></a><?php else: echo h($ht); endif; ?></li>
    <?php endforeach; ?>
    <?php if (count($os['headings']) > 14): ?><li>and <?php echo count($os['headings']) - 14; ?> more</li><?php endif; ?>
  </ul>
  <?php endif; ?>
  <p class="lbl">Neighbours</p>
  <p class="facts">Links to <?php echo count($os['outlinks']); ?> · Linked from <?php echo count($inbound); ?></p>
  <ul>
    <?php foreach (array_slice($os['outlinks'], 0, 8) as $ol): if (!isset($byFile[$ol])) continue; ?>
    <li><a href="?sheet=<?php echo h(rawurlencode($ol)); ?>"><?php echo h($rows[$byFile[$ol]]['title']); ?></a></li>
    <?php endforeach; ?>
  </ul>
  <p class="lbl">Facts</p>
  <p class="facts">
    <?php if ($os['created']): ?>Created <?php echo h(gmdate('M j, Y', $os['created'])); ?> · <?php endif; ?>
    <?php if ($os['updated']): ?>Updated <?php echo h(gmdate('M j, Y', $os['updated'])); ?> · <?php endif; ?>
    <?php if ($os['reviewed']): ?>Reviewed <?php echo h($os['reviewed']); ?> · <?php endif; ?>
    ~<?php echo number_format($os['words']); ?> words · <?php echo (int)$os['tables']; ?> tables · <?php echo (int)$os['sections']; ?> sections
    <?php if (isset($popRank[$os['file']])): ?>· #<?php echo (int)$popRank[$os['file']]; ?> of <?php echo (int)$totalCount; ?> this month<?php endif; ?>
  </p>
  <p class="acts"><a class="primary" href="<?php echo h($os['file']); ?>">Open</a> <a href="./">Back to all cheatsheets</a></p>
</section>
<?php endif; ?>

<nav class="lenses" aria-label="Lens">
  <?php
  // Real links first: every lens is a document the server can render on its own.
  // JS intercepts them and flips <body data-view> instead of navigating.
  $lensList = ['grid' => 'Grid', 'map' => 'Map', 'paths' => 'Paths'];
  foreach ($lensList as $lv => $ll):
    $lurl = $lv === 'grid' ? grid_url(['view' => '']) : grid_url(['view' => $lv]);
  ?><a data-view="<?php echo h($lv); ?>" aria-current="<?php echo $view === $lv ? 'page' : 'false'; ?>" href="<?php echo h($lurl); ?>"><?php echo h($ll); ?></a><?php endforeach; ?>
</nav>

<div class="explorer">
  <aside class="rail" id="rail" aria-label="Filters">
    <button class="railtoggle" type="button" id="railToggle" aria-expanded="false">Filters and categories</button>
    <div class="fbody">
      <fieldset class="fgroup"><span class="lbl">Category</span>
        <ul>
          <?php foreach ($catNames as $ci => $cn): if (empty($catCounts[$cn])) continue;
            $on = ($activeCat === $cn); ?>
          <li><a class="k<?php echo (int)$ci; ?>" data-facet="cat" data-val="<?php echo h($cn); ?>" aria-pressed="<?php echo $on ? 'true' : 'false'; ?>" href="<?php echo h(grid_url(['cat' => $on ? '' : $cn])); ?>"><span class="cdot"></span><?php echo h($cn); ?><span class="n"><?php echo (int)$catCounts[$cn]; ?></span></a></li>
          <?php endforeach; ?>
        </ul>
      </fieldset>
      <fieldset class="fgroup"><span class="lbl">Shape</span>
        <ul>
          <?php ksort($shapeCounts); foreach ($shapeCounts as $sname => $sn):
            $on = in_array($sname, $activeShapes, true); ?>
          <li><a data-facet="shape" data-val="<?php echo h($sname); ?>" aria-pressed="<?php echo $on ? 'true' : 'false'; ?>" href="<?php echo h(grid_url(['shape' => toggle_list($activeShapes, $sname)])); ?>"><?php echo h(shape_label($sname)); ?><span class="n"><?php echo (int)$sn; ?></span></a></li>
          <?php endforeach; ?>
        </ul>
      </fieldset>
      <fieldset class="fgroup"><span class="lbl">Freshness</span>
        <ul>
          <?php
          $freshLabels = ['reviewed90' => 'Reviewed in 90 days', 'updated30' => 'Updated in 30 days', 'new30' => 'New in 30 days'];
          foreach ($freshLabels as $fk => $fl):
            $on = in_array($fk, $activeFresh, true); ?>
          <li><a data-facet="fresh" data-val="<?php echo h($fk); ?>" aria-pressed="<?php echo $on ? 'true' : 'false'; ?>" href="<?php echo h(grid_url(['fresh' => toggle_list($activeFresh, $fk)])); ?>"><?php echo h($fl); ?></a></li>
          <?php endforeach; ?>
          <li><a data-facet="interactive" data-val="1" aria-pressed="<?php echo $wantInteractive ? 'true' : 'false'; ?>" href="<?php echo h(grid_url(['interactive' => $wantInteractive ? '' : '1'])); ?>">Interactive</a></li>
        </ul>
      </fieldset>
      <p><a class="plain" href="./">Clear all filters</a></p>
    </div>
  </aside>

  <div class="results">
    <div class="toolbar">
      <span class="count" id="count"><span id="countN"><?php echo (int)$visibleCount; ?></span> of <?php echo (int)$totalCount; ?></span>
      <span class="chips" id="chips">
        <?php if ($activeCat !== ''): ?><a class="chip" href="<?php echo h(grid_url(['cat' => ''])); ?>"><?php echo h($activeCat); ?><span class="x">×</span></a><?php endif; ?>
        <?php if ($qRaw !== ''): ?><a class="chip" href="<?php echo h(grid_url(['q' => ''])); ?>">"<?php echo h(clamp_text($qRaw, 28)); ?>"<span class="x">×</span></a><?php endif; ?>
        <?php foreach ($activeShapes as $s): ?><a class="chip" href="<?php echo h(grid_url(['shape' => toggle_list($activeShapes, $s)])); ?>"><?php echo h(shape_label($s)); ?><span class="x">×</span></a><?php endforeach; ?>
        <?php foreach ($activeFresh as $f): ?><a class="chip" href="<?php echo h(grid_url(['fresh' => toggle_list($activeFresh, $f)])); ?>"><?php echo h($freshLabels[$f] ?? $f); ?><span class="x">×</span></a><?php endforeach; ?>
        <?php if ($wantInteractive): ?><a class="chip" href="<?php echo h(grid_url(['interactive' => ''])); ?>">Interactive<span class="x">×</span></a><?php endif; ?>
      </span>
      <nav class="sorts" aria-label="Sort">
        <?php foreach ($SORTS as $sk => $sl): $cur = ($sort === $sk); ?>
        <a data-sort="<?php echo h($sk); ?>" aria-current="<?php echo $cur ? 'true' : 'false'; ?>" href="<?php echo h(grid_url(['sort' => $sk === 'new' ? '' : $sk])); ?>"><?php echo h($sl); ?></a>
        <?php endforeach; ?>
      </nav>
    </div>

    <?php if ($deepCut): ?>
    <section class="deepcut k<?php echo (int)$deepCut['catk']; ?>" id="deepcut">
      <h2>Deep cut of the day</h2>
      <h3><a href="<?php echo h($deepCut['file']); ?>"><?php echo h($deepCut['title']); ?></a></h3>
      <p><?php echo h(clamp_text($deepCut['description'], 190)); ?></p>
    </section>
    <?php endif; ?>

    <div class="grid" id="grid">
      <?php foreach ($rendered as $r) render_card($r, $now, $NEW_WINDOW, $REVIEW_WINDOW, $r['_visible']); ?>
    </div>
    <p class="empty" id="empty"<?php echo $visibleCount > 0 ? ' hidden' : ''; ?>>Nothing matches those filters. <a href="./">Clear them</a> and start again.</p>
  </div>

  <section id="mapwrap" aria-label="Constellation map">
    <p class="nojsmap">The map draws itself with JavaScript, which is off. The grid below lists every sheet, and each sheet's detail view names its neighbours.</p>
    <div class="maptop">
      <?php foreach ($catNames as $ci => $cn): if (empty($catCounts[$cn])) continue; ?>
      <button class="lgd k<?php echo (int)$ci; ?>" type="button" data-lg="<?php echo (int)$ci; ?>" aria-pressed="false"><span class="cdot"></span><?php echo h($cn); ?><span class="n"><?php echo (int)$catCounts[$cn]; ?></span></button>
      <?php endforeach; ?>
      <span class="grow"><button class="tbtn" id="maplistBtn" type="button" aria-pressed="false">List this map</button><button class="tbtn" id="mapreset" type="button">Reset view</button></span>
    </div>
    <figure id="mapfig">
      <canvas id="mapc" role="img" aria-label="Constellation map of <?php echo (int)$totalCount; ?> cheatsheets joined by <?php echo (int)($stats['edges'] ?? 0); ?> cross-links, clustered into <?php echo (int)$fieldCount; ?> category regions. Use the List this map button for a text equivalent."></canvas>
      <div id="maptip" hidden></div>
      <button id="egoAll" type="button" hidden>Show the whole map</button>
    </figure>
    <p class="maphint">Drag to pan, scroll to zoom, double-click to reset. Click a node to open its detail. Colour is category; size is how much it is read this month.</p>
    <div id="maplist" hidden></div>
  </section>
</div>

<?php /* The trails carry their full step lists, about 15 KB, so they are rendered
         only in their own lens; the switcher navigates there instead of paying
         for them on every grid and map view. */ ?>
<?php if ($view === 'paths'): ?>
<section class="paths" id="paths">
<?php if ($activePath):
  $apId = (string)($activePath['id'] ?? '');
  $apSteps = is_array($activePath['steps'] ?? null) ? array_values(array_filter($activePath['steps'], fn($x) => is_array($x) && !empty($x['file']))) : [];
  $apFiles = array_column($apSteps, 'file');
  ?>
  <h2>Curated paths</h2>
  <p class="maphint" style="margin:0 0 10px"><a href="<?php echo h(grid_url(['view' => 'paths', 'path' => ''])); ?>">All paths</a></p>
  <article class="trail open" id="path-<?php echo h($apId); ?>" data-path="<?php echo h($apId); ?>">
    <h3><?php echo h((string)($activePath['title'] ?? '')); ?></h3>
    <p><?php echo h((string)($activePath['promise'] ?? '')); ?></p>
    <p class="tprog" data-steps="<?php echo count($apSteps); ?>"><?php echo count($apSteps); ?> steps</p>
    <ol class="stepper">
      <?php foreach ($apSteps as $si => $st):
        $sf = (string)$st['file'];
        $stitle = isset($byFile[$sf]) ? $rows[$byFile[$sf]]['title'] : $sf; ?>
      <li data-i="<?php echo (int)$si; ?>"><span class="sn num"><?php echo (int)$si + 1; ?></span><a href="<?php echo h($sf); ?>"><?php echo h(clamp_text($stitle, 58)); ?></a><span class="why"><?php echo h((string)($st['why'] ?? '')); ?></span><button class="stepbtn" type="button" data-i="<?php echo (int)$si; ?>" aria-pressed="false">Mark done</button></li>
      <?php endforeach; ?>
    </ol>
  </article>
  <?php
  $related = [];
  foreach ($trails as $tr) {
      if (!is_array($tr) || (string)($tr['id'] ?? '') === $apId || empty($tr['steps'])) continue;
      foreach ($tr['steps'] as $st) {
          if (is_array($st) && !empty($st['file']) && in_array((string)$st['file'], $apFiles, true)) { $related[] = $tr; break; }
      }
  }
  if ($related): ?>
  <div class="related">
    <h2>Related paths</h2>
    <p class="maphint" style="margin:0 0 10px">Trails that share at least one sheet with this one.</p>
    <div class="trails"><?php foreach ($related as $tr) trail_card($tr, $rows, $byFile); ?></div>
  </div>
  <?php endif; ?>
<?php else: ?>
  <h2>Curated paths</h2>
  <p style="color:var(--muted);margin:0">Hand-written trails, in the order the sheets actually make sense. Open one to track your way through it; progress stays in this browser.</p>
  <div class="trails"><?php foreach ($trails as $tr) { if (is_array($tr) && !empty($tr['steps'])) trail_card($tr, $rows, $byFile); } ?></div>
<?php endif; ?>
</section>
<?php endif; ?>
</div><!-- /wrap -->
</main>

<section class="signup">
  <div class="wrap">
    <div class="copy">
      <h2>Get new references and build notes</h2>
      <p>Occasional email when a new reference ships or the pipeline changes. No spam, no tracking, unsubscribe anytime.</p>
    </div>
    <form action="subscribe.php" method="post" class="email-signup">
      <label class="sr" for="emailSignupField">Email address</label>
      <div class="hp" aria-hidden="true">
        <label for="website-hp">Leave this field empty</label>
        <input type="text" id="website-hp" name="website" tabindex="-1" autocomplete="off">
      </div>
      <input type="email" id="emailSignupField" name="email" required autocomplete="email" inputmode="email" placeholder="you@example.com" aria-label="Email address">
      <button type="submit">Notify me</button>
      <p class="signup-status" role="status" aria-live="polite" hidden></p>
    </form>
  </div>
</section>

<footer class="site">
  <div class="wrap frow">
    <span>Cheatsheets © <?php echo date('Y'); ?> David Veksler.</span>
    <a href="how-its-built.html">How it's built</a>
    <a href="history.php">Change history</a>
    <a href="popularity.php">Popularity</a>
    <a href="https://github.com/DavidVeksler/CheatSheets" rel="noopener">GitHub</a>
    <a href="catalog.json">catalog.json</a>
    <span class="fcta"><a href="https://www.linkedin.com/in/davidveksler/" rel="noopener" data-ga-linkedin="footer">Working on something similar? Compare notes on LinkedIn.</a></span>
  </div>
</footer>

<dialog id="palette" aria-label="Search the collection">
  <form method="dialog" onsubmit="return false">
    <label class="sr" for="pq">Search inside every cheatsheet</label>
    <input id="pq" type="search" autocomplete="off" spellcheck="false" placeholder="Search inside every page">
  </form>
  <ul id="pres"></ul>
  <p class="sr" id="plive" role="status" aria-live="polite"></p>
  <div id="pfoot"><span><kbd>↑</kbd><kbd>↓</kbd> move</span><span><kbd>enter</kbd> open</span><span><kbd>g</kbd> then <kbd>g</kbd>/<kbd>m</kbd>/<kbd>p</kbd> lens</span><span><kbd>esc</kbd> close</span></div>
</dialog>

<aside id="drawer" hidden aria-label="Sheet detail" tabindex="-1"></aside>

<dialog id="help" aria-label="Keyboard map">
  <h2>Keyboard</h2>
  <dl>
    <dt>⌘K / Ctrl K / /</dt><dd>Open the search palette</dd>
    <dt>↑ ↓ enter</dt><dd>Move and open inside results</dd>
    <dt>esc</dt><dd>Close the palette or the drawer</dd>
    <dt>g then g</dt><dd>Grid lens</dd>
    <dt>g then m</dt><dd>Map lens</dd>
    <dt>g then p</dt><dd>Paths</dd>
    <dt>t</dt><dd>Toggle theme</dd>
    <dt>?</dt><dd>This map</dd>
  </dl>
  <p class="acts"><button type="button" class="primary" onclick="document.getElementById('help').close()">Close</button></p>
</dialog>

<div class="toast" id="toast" hidden role="status"></div>

<script type="application/json" id="catalog-lite"><?php echo json_encode($lite, JSON_UNESCAPED_SLASHES | JSON_UNESCAPED_UNICODE); ?></script>
<script>
(function(){
'use strict';
var NS='cs-explorer:v1:';
// Bridge to the map/paths block below: it registers setView, showOnMap and the
// two redraw hooks, and reads the lite catalog and helpers back out of here.
var CS=window.CS={setView:function(){},showOnMap:function(){},onFilter:null,onTheme:null};
var CATV=<?php echo json_encode($catalogVersion); ?>;
var SERVER_CAT=<?php echo json_encode($activeCat); ?>;
var TOTAL=<?php echo (int)$totalCount; ?>;
// The server may have rendered a sheet or category title, so the "no filters"
// title is passed in rather than read back off document.title.
var SITE_TITLE=<?php echo json_encode($SITE_TITLE); ?>;

function ls(k,v){try{if(v===undefined)return localStorage.getItem(NS+k);localStorage.setItem(NS+k,v);}catch(e){}return null;}
function lsj(k,d){try{var r=JSON.parse(ls(k)||'null');return r===null?d:r;}catch(e){return d;}}
function ga(name,params){try{if(typeof gtag==='function')gtag('event',name,params||{});}catch(e){}}
function el(id){return document.getElementById(id);}
function esc(s){return String(s).replace(/[&<>"]/g,function(c){return{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c];});}

/* ---------------------------------------------------------------- data --- */
var L=JSON.parse(el('catalog-lite').textContent);
var N=L.f.length;
var byFile={};
function toks(s){return String(s).toLowerCase().split(/[^a-z0-9]+/).filter(Boolean);}
for(var i=0;i<N;i++)byFile[L.f[i]]=i;
// Titles come off the rendered cards; they are already in the document, so the
// lite payload does not carry them. On a ?cat= page only that category's cards
// are present, and the rest arrive with catalog.json a moment later.
var TITLE=new Array(N),tokTitle=new Array(N);
for(i=0;i<N;i++){TITLE[i]='';tokTitle[i]=[];}
var FULL=null,fullPending=null,tokHead=null,tokDesc=null,tokKw=null,inbound=null;

function loadFull(){
  if(FULL)return Promise.resolve(FULL);
  if(fullPending)return fullPending;
  fullPending=fetch('catalog.json?v='+encodeURIComponent(CATV)).then(function(r){return r.json();}).then(function(d){
    FULL=d;
    var idx={};d.sheets.forEach(function(s,i){idx[s.file]=i;});
    FULL.idx=idx;
    inbound={};
    d.sheets.forEach(function(s){(s.outlinks||[]).forEach(function(t){(inbound[t]=inbound[t]||[]).push(s.file);});});
    tokHead={};tokDesc={};tokKw={};
    d.sheets.forEach(function(s){
      tokHead[s.file]=(s.headings||[]).map(function(hh){return{t:hh.text,id:hh.id,k:toks(hh.text)};});
      tokDesc[s.file]=toks(s.description||'');
      tokKw[s.file]=toks((s.keywords||[]).join(' '));
      var k=byFile[s.file];
      if(k!==undefined&&!TITLE[k]){TITLE[k]=s.title;tokTitle[k]=toks(s.title);}
    });
    return FULL;
  }).catch(function(){fullPending=null;return null;});
  return fullPending;
}

/* --------------------------------------------------------------- toast --- */
var toastT=null;
function toast(msg){var t=el('toast');t.textContent=msg;t.hidden=false;clearTimeout(toastT);toastT=setTimeout(function(){t.hidden=true;},2600);}

/* --------------------------------------------------------------- theme --- */
function currentTheme(){
  var d=document.documentElement.dataset.theme;
  if(d)return d;
  return window.matchMedia('(prefers-color-scheme: dark)').matches?'dark':'light';
}
function toggleTheme(){
  var next=currentTheme()==='dark'?'light':'dark';
  document.documentElement.dataset.theme=next;ls('theme',next);ga('explorer_theme',{theme:next});
  if(CS.onTheme)CS.onTheme();
}
el('themeToggle').addEventListener('click',toggleTheme);

/* -------------------------------------------------------------- visited -- */
var visited=lsj('visited',{});
function markVisited(f){visited[f]=1;try{ls('visited',JSON.stringify(visited));}catch(e){}paintVisited();}
function paintVisited(){cards.forEach(function(c,k){if(visited[cardFile[k]])c.classList.add('seen');});}

/* ------------------------------------------------------------ filtering -- */
var grid=el('grid'),cards=Array.prototype.slice.call(grid.querySelectorAll('.c'));
var cardFile=[];
cards.forEach(function(c,k){
  var a=c.querySelector('h3 a');
  var f=a?a.getAttribute('href'):'';
  cardFile[k]=f;
  var i=byFile[f];
  if(i!==undefined){TITLE[i]=a.textContent;tokTitle[i]=toks(TITLE[i]);}
});
function fileOf(card){return cardFile[cards.indexOf(card)]||'';}
var state={cat:SERVER_CAT||'',q:'',shape:[],fresh:[],interactive:false,sort:''};
(function initState(){
  var p=new URLSearchParams(location.search);
  state.q=p.get('q')||'';
  state.cat=p.get('cat')||'';
  state.shape=(p.get('shape')||'').split(',').filter(Boolean);
  state.fresh=(p.get('fresh')||'').split(',').filter(Boolean);
  state.interactive=p.get('interactive')==='1';
  state.sort=p.get('sort')||'';
})();
var TODAY=Math.floor(Date.now()/86400000);

function matches(i){
  if(state.q){
    var q=state.q.toLowerCase();
    var hay=TITLE[i].toLowerCase();
    if(FULL){var s=FULL.sheets[FULL.idx[L.f[i]]];hay+=' '+(s.description||'')+' '+(s.keywords||[]).join(' ');hay=hay.toLowerCase();}
    if(hay.indexOf(q)<0)return false;
  }
  if(state.cat&&L.cats[L.c[i]]!==state.cat)return false;
  if(state.shape.length){
    var hit=false;
    for(var j=0;j<state.shape.length;j++){if(L.s[i].indexOf(L.shapes.indexOf(state.shape[j]))>=0){hit=true;break;}}
    if(!hit)return false;
  }
  if(state.interactive&&!L.ix[i])return false;
  if(state.fresh.length){
    var f=false;
    if(state.fresh.indexOf('reviewed90')>=0&&L.rv[i]&&TODAY-L.rv[i]<=90)f=true;
    if(state.fresh.indexOf('updated30')>=0&&L.up[i]&&TODAY-L.up[i]<=30)f=true;
    if(state.fresh.indexOf('new30')>=0&&L.cr[i]&&TODAY-L.cr[i]<=30)f=true;
    if(!f)return false;
  }
  return true;
}

var SORTS={'new':function(a,b){return L.cr[b]-L.cr[a];},
 'updated':function(a,b){return L.up[b]-L.up[a];},
 'popular':function(a,b){return L.p[b]-L.p[a];},
 'reviewed':function(a,b){return L.rv[b]-L.rv[a];},
 'title':function(a,b){return TITLE[a].localeCompare(TITLE[b],undefined,{sensitivity:'base'});}};

function apply(reorder){
  var n=0;
  cards.forEach(function(c,k){
    var i=byFile[cardFile[k]];
    var ok=(i!==undefined)&&matches(i);
    c.classList.toggle('off',!ok);
    if(ok)n++;
  });
  el('countN').textContent=n;
  el('empty').hidden=n>0;
  if(reorder&&SORTS[state.sort||'new']){
    var cmp=SORTS[state.sort||'new'];
    cards.slice().sort(function(a,b){return cmp(byFile[fileOf(a)],byFile[fileOf(b)]);})
      .forEach(function(c){grid.appendChild(c);});
  }
  var dc=el('deepcut');
  if(dc)dc.hidden=!!(state.q||state.shape.length||state.fresh.length||state.interactive);
  if(CS.onFilter)CS.onFilter();
  syncURL();
  paintFacets();
  document.title=state.cat?state.cat+' Cheatsheets | David Veksler':SITE_TITLE;
  return n;
}

function syncURL(){
  var p=new URLSearchParams();
  if(state.cat)p.set('cat',state.cat);
  if(state.q)p.set('q',state.q);
  if(state.shape.length)p.set('shape',state.shape.join(','));
  if(state.fresh.length)p.set('fresh',state.fresh.join(','));
  if(state.interactive)p.set('interactive','1');
  if(state.sort)p.set('sort',state.sort);
  var lens=document.body.dataset.view;
  if(lens&&lens!=='grid')p.set('view',lens);
  var s=p.toString();
  history.replaceState(history.state,'',s?'?'+s:location.pathname);
}

function paintFacets(){
  document.querySelectorAll('[data-facet]').forEach(function(a){
    var f=a.dataset.facet,v=a.dataset.val,on=false;
    if(f==='cat')on=state.cat===v;
    else if(f==='shape')on=state.shape.indexOf(v)>=0;
    else if(f==='fresh')on=state.fresh.indexOf(v)>=0;
    else if(f==='interactive')on=state.interactive;
    a.setAttribute('aria-pressed',on?'true':'false');
  });
  document.querySelectorAll('.sorts a').forEach(function(a){
    a.setAttribute('aria-current',(state.sort||'new')===a.dataset.sort?'true':'false');
  });
  renderChips();
}

var FRESH_LABEL={reviewed90:'Reviewed in 90 days',updated30:'Updated in 30 days',new30:'New in 30 days'};
function shapeLabel(s){return s.charAt(0).toUpperCase()+s.slice(1);}
function renderChips(){
  var out=[];
  if(state.cat)out.push(['cat',state.cat,state.cat]);
  if(state.q)out.push(['q','','"'+state.q+'"']);
  state.shape.forEach(function(s){out.push(['shape',s,shapeLabel(s)]);});
  state.fresh.forEach(function(f){out.push(['fresh',f,FRESH_LABEL[f]||f]);});
  if(state.interactive)out.push(['interactive','1','Interactive']);
  el('chips').innerHTML=out.map(function(c){
    return '<button class="chip" type="button" data-chip="'+esc(c[0])+'" data-val="'+esc(c[1])+'">'+esc(c[2])+'<span class="x">×</span></button>';
  }).join('');
}

document.addEventListener('click',function(e){
  var chip=e.target.closest('[data-chip]');
  if(chip){e.preventDefault();clearFacet(chip.dataset.chip,chip.dataset.val);return;}
  var fa=e.target.closest('[data-facet]');
  if(fa){
    // A server-rendered category page holds only its own cards, so changing the
    // category there has to be a real navigation.
    if(fa.dataset.facet==='cat'&&SERVER_CAT)return;
    e.preventDefault();toggleFacet(fa.dataset.facet,fa.dataset.val);return;
  }
  var so=e.target.closest('.sorts a');
  if(so){e.preventDefault();state.sort=so.dataset.sort==='new'?'':so.dataset.sort;apply(true);return;}
});

function toggleFacet(f,v){
  if(f==='cat')state.cat=state.cat===v?'':v;
  else if(f==='interactive')state.interactive=!state.interactive;
  else{
    var arr=state[f],k=arr.indexOf(v);
    if(k<0)arr.push(v);else arr.splice(k,1);
    arr.sort();
  }
  apply(false);
}
function clearFacet(f,v){
  if(f==='cat'){if(SERVER_CAT){location.href='./';return;}state.cat='';}
  else if(f==='q'){state.q='';var hq=el('heroq');if(hq)hq.value='';}
  else if(f==='interactive')state.interactive=false;
  else{var arr=state[f],k=arr.indexOf(v);if(k>=0)arr.splice(k,1);}
  apply(false);
}

/* -------------------------------------------------------- rail on mobile -- */
el('railToggle').addEventListener('click',function(){
  var r=el('rail');r.classList.toggle('open');
  this.setAttribute('aria-expanded',r.classList.contains('open')?'true':'false');
});

/* ---------------------------------------------------------------- search -- */
var dlg=el('palette'),pq=el('pq'),pres=el('pres'),plive=el('plive');
var EXAMPLES=['torque','ukemi','ufw'],exN=0;
var pmodel=[],psel=0;

function openPalette(seed){
  if(!dlg.open){
    pq.placeholder='Search inside every page (try '+EXAMPLES[exN%EXAMPLES.length]+')';
    exN++;
    dlg.showModal();
    loadFull().then(function(){if(dlg.open)rank(pq.value);});
  }
  if(seed!==undefined){pq.value=seed;}
  pq.focus();pq.select();
  rank(pq.value);
}
el('openPalette').addEventListener('click',function(){openPalette();});
dlg.addEventListener('close',function(){pmodel=[];pres.innerHTML='';});

function score(i,qt){
  var total=0;
  for(var a=0;a<qt.length;a++){
    var t=qt[a],w=0,j;
    for(j=0;j<tokTitle[i].length;j++)if(tokTitle[i][j].indexOf(t)===0){w=5;break;}
    if(w<3&&tokKw){var kw=tokKw[L.f[i]]||[];for(j=0;j<kw.length;j++)if(kw[j].indexOf(t)===0){w=3;break;}}
    if(w<3&&tokHead){
      var hs=tokHead[L.f[i]]||[];
      for(j=0;j<hs.length&&w<3;j++)for(var m=0;m<hs[j].k.length;m++)if(hs[j].k[m].indexOf(t)===0){w=3;break;}
    }
    if(w<1&&tokDesc){
      var dt=tokDesc[L.f[i]]||[];
      for(j=0;j<dt.length;j++)if(dt[j].indexOf(t)===0){w=1;break;}
    }
    if(w===0)return 0;
    total+=w;
  }
  return total+Math.log10(L.p[i]+1)*0.5;
}

function matchHeadings(f,qt){
  if(!tokHead)return [];
  var out=[],hs=tokHead[f]||[];
  for(var j=0;j<hs.length&&out.length<3;j++){
    for(var a=0;a<qt.length;a++){
      var hit=false;
      for(var m=0;m<hs[j].k.length;m++)if(hs[j].k[m].indexOf(qt[a])===0){hit=true;break;}
      if(hit){out.push(hs[j]);break;}
    }
  }
  return out;
}

function commandsFor(qt){
  var cmds=[
    {label:'Open map',act:function(){dlg.close();CS.setView('map','palette');}},
    {label:'Open paths',act:function(){dlg.close();CS.setView('paths','palette');}},
    {label:'Surprise me',act:function(){dlg.close();surprise();}},
    {label:'Toggle theme',act:toggleTheme}
  ];
  // The four fixed commands are always offered; the category commands are the
  // top 3 whose name matches what has been typed so far.
  var q=qt.join(' ');
  L.cats.filter(function(c){return !q||c.toLowerCase().indexOf(q)>=0;}).slice(0,3)
    .forEach(function(c){cmds.push({label:'Category: '+c,act:function(){dlg.close();if(SERVER_CAT){location.href='?cat='+encodeURIComponent(c);}else{state.cat=c;apply(false);}}});});
  return cmds;
}

function rank(qs){
  var qt=toks(qs),rows=[];
  if(qt.length){
    var scored=[];
    for(var i=0;i<N;i++){var s=score(i,qt);if(s>0)scored.push([s,i]);}
    scored.sort(function(a,b){return b[0]-a[0];});
    scored.slice(0,10).forEach(function(p){
      rows.push({kind:'sheet',i:p[1],heads:matchHeadings(L.f[p[1]],qt)});
    });
  }else{
    var recent=lsj('recent',[]).slice(0,5);
    if(recent.length){
      rows.push({kind:'label',text:'Recent'});
      recent.forEach(function(f){if(byFile[f]!==undefined)rows.push({kind:'sheet',i:byFile[f],heads:[]});});
    }
    var trend=L.f.map(function(_,i){return i;}).sort(function(a,b){return L.p[b]-L.p[a];}).slice(0,5);
    rows.push({kind:'label',text:'Trending'});
    trend.forEach(function(i){rows.push({kind:'sheet',i:i,heads:[]});});
  }
  var cmds=commandsFor(qt);
  if(cmds.length){
    rows.push({kind:'label',text:'Commands'});
    cmds.forEach(function(c){rows.push({kind:'cmd',cmd:c});});
  }
  pmodel=[];
  var html=rows.map(function(r){
    if(r.kind==='label')return '<li class="glabel lbl">'+esc(r.text)+'</li>';
    if(r.kind==='cmd'){
      var ci=pmodel.push({type:'cmd',cmd:r.cmd})-1;
      return '<li><a class="row" data-p="'+ci+'" href="#">'+esc(r.cmd.label)+'</a></li>';
    }
    var i=r.i,si=pmodel.push({type:'sheet',file:L.f[i]})-1;
    var out='<li><a class="row k'+L.c[i]+'" data-p="'+si+'" href="'+esc(L.f[i])+'"><span class="cdot"></span><span>'+esc(TITLE[i]||L.f[i])+'</span><span class="meta">'+esc(L.cats[L.c[i]])+'</span></a>';
    r.heads.forEach(function(hh){
      if(hh.id){
        var hi=pmodel.push({type:'sheet',file:L.f[i],hash:hh.id})-1;
        out+='<a class="sub" data-p="'+hi+'" href="'+esc(L.f[i])+'#'+esc(hh.id)+'"><span class="hash">#</span> '+esc(hh.t)+'</a>';
      }else{
        out+='<span class="sub"><span class="hash">#</span> '+esc(hh.t)+' <em>(no anchor)</em></span>';
      }
    });
    return out+'</li>';
  }).join('');
  pres.innerHTML=html;
  psel=0;paintSel();
  var sheetCount=pmodel.filter(function(p){return p.type==='sheet'&&!p.hash;}).length;
  plive.textContent=sheetCount+' result'+(sheetCount===1?'':'s');
}

function paintSel(){
  var nodes=pres.querySelectorAll('[data-p]');
  nodes.forEach(function(n){n.classList.toggle('sel',Number(n.dataset.p)===psel);});
  var cur=pres.querySelector('.sel');
  if(cur&&cur.scrollIntoView)cur.scrollIntoView({block:'nearest'});
}

function activate(p,fromKey){
  var item=pmodel[p];
  if(!item)return;
  ga('explorer_search',{chars:pq.value.length,results:pmodel.length});
  if(item.type==='cmd'){item.cmd.act();return;}
  dlg.close();
  if(item.hash){markVisited(item.file);location.href=item.file+'#'+item.hash;}
  else openDrawer(item.file,'palette');
}

pq.addEventListener('input',function(){rank(pq.value);});
pres.addEventListener('click',function(e){
  var a=e.target.closest('[data-p]');
  if(!a)return;
  if(e.metaKey||e.ctrlKey||e.shiftKey||e.button===1)return;
  e.preventDefault();activate(Number(a.dataset.p));
});
dlg.addEventListener('keydown',function(e){
  var max=pmodel.length-1;
  if(e.key==='ArrowDown'){e.preventDefault();psel=Math.min(max,psel+1);paintSel();}
  else if(e.key==='ArrowUp'){e.preventDefault();psel=Math.max(0,psel-1);paintSel();}
  else if(e.key==='Enter'){e.preventDefault();activate(psel,true);}
});

/* ---------------------------------------------------------------- drawer -- */
var drawer=el('drawer'),lastFocus=null;
function fmtDate(ts){if(!ts)return '';var d=new Date(ts*1000);return d.toLocaleDateString(undefined,{year:'numeric',month:'short',day:'numeric',timeZone:'UTC'});}
function popRankOf(file){
  var i=byFile[file];if(i===undefined)return 0;
  var order=L.f.map(function(_,k){return k;}).sort(function(a,b){return L.p[b]-L.p[a];});
  return order.indexOf(i)+1;
}
function drawerHTML(s){
  var i=byFile[s.file],cls='k'+L.c[i];
  var heads=(s.headings||[]);
  var shown=heads.slice(0,14);
  var ins=shown.map(function(hh){
    return '<li>'+(hh.id?'<a href="'+esc(s.file)+'#'+esc(hh.id)+'">'+esc(hh.text)+'</a>':esc(hh.text))+'</li>';
  }).join('');
  if(heads.length>14)ins+='<li>and '+(heads.length-14)+' more</li>';
  var outs=(s.outlinks||[]).map(function(f){
    var j=FULL.idx[f];return j===undefined?'':'<a class="nbr" data-nbr="'+esc(f)+'">'+esc(FULL.sheets[j].title)+'</a>';
  }).join('');
  var ins2=(inbound[s.file]||[]).slice(0,12).map(function(f){
    var j=FULL.idx[f];return j===undefined?'':'<a class="nbr" data-nbr="'+esc(f)+'">'+esc(FULL.sheets[j].title)+'</a>';
  }).join('');
  var img=s.image?String(s.image).replace('https://cheatsheets.davidveksler.com/',''):'';
  return '<div class="detail '+cls+'" style="border:0;padding:0;margin:0">'
   +'<div class="dhead"><p class="crow" style="margin:0"><span class="cbadge">'+esc(s.category)+'</span>'
   +(s.shape||[]).slice(0,3).map(function(x){return '<span class="cbadge">'+esc(shapeLabel(x))+'</span>';}).join('')
   +'</p><button class="dclose" type="button" id="dclose" aria-label="Close">Close</button></div>'
   +(img?'<div class="dshot"><img src="'+esc(img)+'" alt="" loading="lazy" onerror="this.hidden=true"></div>':'')
   +'<h2>'+esc(s.title)+'</h2><p>'+esc(s.description||'')+'</p>'
   +(ins?'<p class="lbl">What\'s inside</p><ul>'+ins+'</ul>':'')
   +'<p class="lbl">Neighbours</p><p class="facts">Links to '+((s.outlinks||[]).length)+' · Linked from '+((inbound[s.file]||[]).length)+'</p>'
   +outs+ins2
   +'<p class="lbl">Facts</p><p class="facts">'
   +(s.created?'Created '+fmtDate(s.created)+' · ':'')
   +(s.updated?'Updated '+fmtDate(s.updated)+' · ':'')
   +(s.reviewed?'Reviewed '+esc(s.reviewed)+' · ':'')
   +'~'+(s.words||0).toLocaleString()+' words · '+(s.tables||0)+' tables · '+(s.sections||0)+' sections · #'
   +popRankOf(s.file)+' of '+TOTAL+' this month</p>'
   +'<p class="acts"><a class="primary" href="'+esc(s.file)+'" data-open="'+esc(s.file)+'">Open</a>'
   +'<button type="button" id="dcopy">Copy link</button>'
   +'<button type="button" data-map="'+esc(s.file)+'">Show on map</button></p>'
   +'</div>';
}

var drawerPushed=false;
function openDrawer(file,from,replace){
  loadFull().then(function(d){
    if(!d||d.idx[file]===undefined)return;
    var s=d.sheets[d.idx[file]];
    lastFocus=document.activeElement;
    drawer.innerHTML=drawerHTML(s);
    drawer.hidden=false;
    drawer.focus();
    var det=el('sheet-detail');if(det)det.hidden=true;
    var url='?sheet='+encodeURIComponent(file);
    if(replace){history.replaceState({sheet:file},'',url);}
    else{history.pushState({sheet:file},'',url);drawerPushed=true;}
    ga('explorer_drawer',{file:file,from:from||'grid'});
    var rec=lsj('recent',[]).filter(function(x){return x!==file;});
    rec.unshift(file);try{ls('recent',JSON.stringify(rec.slice(0,10)));}catch(e){}
  });
}
function hideDrawer(){
  if(drawer.hidden)return;
  drawer.hidden=true;drawer.innerHTML='';
  if(lastFocus&&lastFocus.focus)lastFocus.focus();
}
/* Close: step back through the pushState entry when this session created one;
   otherwise (the drawer came from a ?sheet= landing) strip the parameter in
   place so Esc never navigates the reader off the site. */
function closeDrawer(){
  if(drawerPushed){drawerPushed=false;history.back();return;}
  hideDrawer();
  var det=el('sheet-detail');if(det)det.hidden=false;
  apply(false);   // also restores the title the server rendered for the sheet
}
drawer.addEventListener('click',function(e){
  if(e.target.closest('#dclose')){closeDrawer();return;}
  var nb=e.target.closest('[data-nbr]');
  if(nb){e.preventDefault();openDrawer(nb.dataset.nbr,'neighbour');return;}
  if(e.target.closest('#dcopy')){
    var st=history.state&&history.state.sheet;
    var u=location.origin+location.pathname+(st?'?sheet='+encodeURIComponent(st):'');
    if(navigator.clipboard)navigator.clipboard.writeText(u).then(function(){toast('Link copied.');},function(){toast(u);});
    else toast(u);
    return;
  }
  var mp=e.target.closest('[data-map]');
  if(mp){CS.showOnMap(mp.dataset.map);return;}
  var op=e.target.closest('[data-open]');
  if(op)markVisited(op.dataset.open);
});

grid.addEventListener('click',function(e){
  if(e.metaKey||e.ctrlKey||e.shiftKey||e.altKey)return;
  var link=e.target.closest('a');
  var card=e.target.closest('.c');
  if(!card)return;
  var f=fileOf(card);
  if(link&&(link.parentElement===card||link.closest('h3'))){markVisited(f);return;}
  e.preventDefault();
  openDrawer(f,'grid');
});

window.addEventListener('popstate',function(e){
  var pp=new URLSearchParams(location.search);
  var st=(e.state&&e.state.sheet)||pp.get('sheet');
  drawerPushed=false;
  CS.setView(pp.get('view')||'grid','history',true);
  if(st)openDrawer(st,'history',true);
  else hideDrawer();
});

/* ------------------------------------------------------------ serendipity - */
function surprise(){
  var order=L.f.map(function(_,i){return i;}).sort(function(a,b){return L.p[b]-L.p[a];});
  var pool=order.slice(Math.floor(order.length/3));
  var recentS=lsj('surprises',[]);
  var choices=pool.filter(function(i){return recentS.indexOf(L.f[i])<0;});
  if(!choices.length)choices=pool;
  var pick=choices[Math.floor(Math.random()*choices.length)];
  var f=L.f[pick];
  recentS.unshift(f);try{ls('surprises',JSON.stringify(recentS.slice(0,10)));}catch(e){}
  ga('explorer_surprise',{file:f});
  openDrawer(f,'surprise');
}
el('surprise').addEventListener('click',surprise);

/* --------------------------------------------------------------- keys ----- */
var chord=false,chordT=null;
el('helpBtn').addEventListener('click',function(){el('help').showModal();});
document.addEventListener('keydown',function(e){
  var tag=(e.target.tagName||'').toLowerCase();
  var typing=tag==='input'||tag==='textarea'||tag==='select'||e.target.isContentEditable;
  if((e.metaKey||e.ctrlKey)&&e.key.toLowerCase()==='k'){e.preventDefault();openPalette();return;}
  if(e.key==='Escape'){if(!drawer.hidden&&!dlg.open){e.preventDefault();closeDrawer();}return;}
  if(typing||e.metaKey||e.ctrlKey||e.altKey)return;
  if(e.key==='/'){e.preventDefault();openPalette();return;}
  if(e.key==='?'){e.preventDefault();el('help').showModal();return;}
  if(e.key==='t'){e.preventDefault();toggleTheme();return;}
  if(chord){
    chord=false;clearTimeout(chordT);
    if(e.key==='g'){e.preventDefault();CS.setView('grid','key');}
    else if(e.key==='m'){e.preventDefault();CS.setView('map','key');}
    else if(e.key==='p'){e.preventDefault();CS.setView('paths','key');}
    return;
  }
  if(e.key==='g'){chord=true;chordT=setTimeout(function(){chord=false;},1200);}
});

/* -------------------------------------------------------------- signup ---- */
document.querySelectorAll('form.email-signup').forEach(function(form){
  var status=form.querySelector('.signup-status');
  function show(msg,isError){if(!status)return;status.hidden=false;status.textContent=msg;status.classList.toggle('is-error',!!isError);}
  form.addEventListener('submit',function(e){
    var email=form.querySelector('input[type="email"]');
    if(email&&!email.checkValidity())return;
    e.preventDefault();
    var btn=form.querySelector('button');
    if(btn)btn.disabled=true;
    fetch(form.action,{method:'POST',headers:{'Accept':'application/json'},body:new FormData(form)})
      .then(function(r){return r.json().catch(function(){return{ok:r.ok};});})
      .then(function(d){
        if(d&&d.ok){show('Thanks, you are on the list.');form.reset();}
        else show((d&&d.error)||'Sorry, that did not go through. Please try again.',true);
      })
      .catch(function(){show('Network error, please try again later.',true);})
      .finally(function(){if(btn)btn.disabled=false;});
  });
});

/* ------------------------------------------------------------ analytics --- */
document.querySelectorAll('[data-ga-linkedin]').forEach(function(a){
  a.addEventListener('click',function(){ga('linkedin_click',{link_location:a.dataset.gaLinkedin});});
});

/* ------------------------------------------------------------- start up --- */
CS.L=L;CS.byFile=byFile;CS.TITLE=TITLE;CS.loadFull=loadFull;CS.openDrawer=openDrawer;
CS.matches=matches;CS.toast=toast;CS.ga=ga;CS.ls=ls;CS.lsj=lsj;CS.el=el;CS.esc=esc;
CS.syncURL=syncURL;
paintVisited();
renderChips();
paintFacets();
(function(){
  var sp=new URLSearchParams(location.search).get('sheet');
  if(sp&&byFile[sp]!==undefined)openDrawer(sp,'url',true);
})();
})();
</script>
<script>
/* ============================================================================
   Map and Paths lenses. A second inline block, parsed after the one above, so
   the grid, palette and drawer are interactive before any of this runs. It
   reads window.CS from that block; it adds no network request of its own
   beyond the catalog.json fetch the palette already knows how to make.
   ========================================================================== */
(function(){
'use strict';
var CS=window.CS;if(!CS||!CS.L)return;
var L=CS.L,N=L.f.length,el=CS.el,esc=CS.esc,body=document.body;

/* ---------------------------------------------------------------- lenses -- */
var VIEWS={grid:1,map:1,paths:1};
function setView(v,src,quiet){
  if(!VIEWS[v])v='grid';
  var was=body.dataset.view||'grid';
  body.dataset.view=v;
  document.querySelectorAll('.lenses a').forEach(function(a){
    a.setAttribute('aria-current',a.dataset.view===v?'page':'false');
  });
  if(!quiet){
    var p=new URLSearchParams(location.search);
    if(v==='grid')p.delete('view');else p.set('view',v);
    if(v!=='paths')p.delete('path');
    var qs=p.toString();
    history.replaceState(history.state,'',qs?'?'+qs:location.pathname);
    if(was!==v)CS.ga('explorer_view',{view:v});
  }
  if(v==='map'){openMap().then(scrollMapIntoView);return;}
  if(v==='paths'){
    // The trails are only rendered in their own lens, so reach them by
    // navigating when this document does not carry them.
    if(!el('paths')){location.href='?view=paths';return;}
    paintPaths();
  }
  if(was!==v&&!quiet)window.scrollTo(0,0);
}
CS.setView=setView;

/* ------------------------------------------------------------------ map --- */
var fig=el('mapfig'),cv=el('mapc'),tip=el('maptip'),ctx=cv&&cv.getContext('2d');
var POS=null,EDG=null,NBR=null,OUT=null,PMAX=1,ALWAYS=null,READY=false,FULLREF=null;
var HUE=[],INK='#111',SURF='#fff',MUT='#888';
var M={k:1,tx:0,ty:0,hover:null,legend:[],ego:null,whole:false};
var W=0,H=0,DPR=1,PAD=30,EGO=null,EGOIDX=null,ALLIDX=null,drawMs=0;
var TAU=Math.PI*2;

/* Colours are read back out of the CSS tokens through a probe element, so the
   canvas always agrees with the theme, including the manual toggle. */
function readPalette(){
  var pr=document.createElement('span');
  pr.style.cssText='position:absolute;left:-9999px;top:0';
  body.appendChild(pr);
  HUE=[];
  for(var i=0;i<L.cats.length;i++){pr.className='k'+i;pr.style.color='var(--cat)';HUE.push(getComputedStyle(pr).color);}
  pr.className='';
  pr.style.color='var(--ink)';INK=getComputedStyle(pr).color;
  pr.style.color='var(--surface)';SURF=getComputedStyle(pr).color;
  pr.style.color='var(--muted)';MUT=getComputedStyle(pr).color;
  pr.parentNode.removeChild(pr);
}

function prep(d){
  FULLREF=d;
  POS=new Array(N);OUT=new Array(N);NBR=new Array(N);ALLIDX=new Array(N);
  var i,s;
  for(i=0;i<N;i++){
    s=d.sheets[d.idx[L.f[i]]];
    POS[i]=s?[s.x||0,s.y||0]:[.5,.5];
    OUT[i]=s&&s.outlinks?s.outlinks.length:0;
    NBR[i]={};ALLIDX[i]=i;
  }
  var m=new Array(d.sheets.length);
  for(i=0;i<d.sheets.length;i++)m[i]=CS.byFile[d.sheets[i].file];
  EDG=[];
  (d.edges||[]).forEach(function(e){
    var a=m[e[0]],b=m[e[1]];
    if(a===undefined||b===undefined||a===b)return;
    EDG.push([a,b]);NBR[a][b]=1;NBR[b][a]=1;
  });
  PMAX=0;for(i=0;i<N;i++)if(L.p[i]>PMAX)PMAX=L.p[i];
  if(!PMAX)PMAX=1;
  // Always-on labels: the 25 most read plus every hub. "Hub" is out-degree 12+
  // (13 sheets); total degree would qualify 144 of 197 and bury the map in text.
  ALWAYS={};
  ALLIDX.slice().sort(function(a,b){return L.p[b]-L.p[a];}).slice(0,25).forEach(function(i){ALWAYS[i]=1;});
  for(i=0;i<N;i++)if(OUT[i]>=12)ALWAYS[i]=1;
  READY=true;
}

function sizeCanvas(){
  var r=fig.getBoundingClientRect();
  var w=Math.max(1,Math.round(r.width)),h=Math.max(1,Math.round(r.height));
  DPR=Math.min(window.devicePixelRatio||1,2);
  if(w!==W||h!==H||cv.width!==Math.round(w*DPR)){
    W=w;H=h;cv.width=Math.round(w*DPR);cv.height=Math.round(h*DPR);
    cv.style.width=w+'px';cv.style.height=h+'px';
  }
  ctx.setTransform(DPR,0,0,DPR,0,0);
}
function proj(i){
  if(EGO)return EGO[i];
  var p=POS[i];
  return [(PAD+p[0]*(W-2*PAD))*M.k+M.tx,(PAD+p[1]*(H-2*PAD))*M.k+M.ty];
}
function rad(i){return 4+6*Math.sqrt((L.p[i]||0)/PMAX);}
function alphaOf(i){
  if(!CS.matches(i))return .15;
  if(M.legend.length&&M.legend.indexOf(L.c[i])<0)return .15;
  if(M.hover!==null&&i!==M.hover&&!NBR[M.hover][i])return .35;
  return 1;
}
function shortTitle(i){
  var t=CS.TITLE[i]||L.f[i],c=t.indexOf(':');
  if(c>6)t=t.slice(0,c);
  return t.length>30?t.slice(0,29)+'…':t;
}

function draw(){
  if(!READY)return;
  var t0=performance.now(),i,j,e,p,vi;
  sizeCanvas();
  ctx.clearRect(0,0,W,H);
  var vis=EGO?EGOIDX:ALLIDX,P=new Array(N),hv=M.hover;
  for(vi=0;vi<vis.length;vi++){i=vis[vi];P[i]=proj(i);}
  ctx.lineWidth=.5;ctx.strokeStyle=MUT;
  ctx.globalAlpha=hv===null?.12:.04;
  ctx.beginPath();
  for(j=0;j<EDG.length;j++){
    e=EDG[j];if(!P[e[0]]||!P[e[1]])continue;
    if(hv!==null&&(e[0]===hv||e[1]===hv))continue;
    ctx.moveTo(P[e[0]][0],P[e[0]][1]);ctx.lineTo(P[e[1]][0],P[e[1]][1]);
  }
  ctx.stroke();
  if(hv!==null){
    ctx.globalAlpha=.6;ctx.strokeStyle=INK;ctx.beginPath();
    for(j=0;j<EDG.length;j++){
      e=EDG[j];if(!P[e[0]]||!P[e[1]])continue;
      if(e[0]!==hv&&e[1]!==hv)continue;
      ctx.moveTo(P[e[0]][0],P[e[0]][1]);ctx.lineTo(P[e[1]][0],P[e[1]][1]);
    }
    ctx.stroke();
  }
  ctx.lineWidth=1;ctx.strokeStyle=SURF;
  for(vi=0;vi<vis.length;vi++){
    i=vis[vi];p=P[i];
    if(p[0]<-40||p[0]>W+40||p[1]<-40||p[1]>H+40)continue;
    var r=rad(i)*(i===hv?1.5:1);
    ctx.globalAlpha=alphaOf(i);ctx.fillStyle=HUE[L.c[i]]||MUT;
    ctx.beginPath();ctx.arc(p[0],p[1],r,0,TAU);ctx.fill();ctx.stroke();
  }
  // Labels sit on the surface colour as a halo so they stay readable where they
  // cross an edge; the fill is the on-surface ink token, never the category hue.
  ctx.globalAlpha=1;ctx.fillStyle=INK;ctx.strokeStyle=SURF;ctx.lineWidth=2.5;
  ctx.lineJoin='round';
  ctx.font='11px system-ui,-apple-system,"Segoe UI",Roboto,sans-serif';
  ctx.textAlign='center';ctx.textBaseline='top';
  var cands=[];
  for(vi=0;vi<vis.length;vi++){i=vis[vi];if(i===hv||EGO||M.k>1.6||ALWAYS[i])cands.push(i);}
  cands.sort(function(a,b){return (b===hv?1e9:L.p[b])-(a===hv?1e9:L.p[a]);});
  var rects=[],rc,o,ok,q;
  for(vi=0;vi<cands.length;vi++){
    i=cands[vi];p=P[i];if(!p)continue;
    if(i!==hv&&alphaOf(i)<.4)continue;
    var t=shortTitle(i),w=ctx.measureText(t).width;
    var x=p[0],y=p[1]+rad(i)*(i===hv?1.5:1)+3;
    if(x-w/2<0||x+w/2>W||y<0||y>H-13)continue;
    rc=[x-w/2-3,y-2,w+6,15];ok=true;
    for(q=0;q<rects.length;q++){
      o=rects[q];
      if(rc[0]<o[0]+o[2]&&o[0]<rc[0]+rc[2]&&rc[1]<o[1]+o[3]&&o[1]<rc[1]+rc[3]){ok=false;break;}
    }
    if(!ok)continue;
    rects.push(rc);ctx.strokeText(t,x,y);ctx.fillText(t,x,y);
  }
  drawMs=performance.now()-t0;
}

function hit(mx,my){
  if(!READY)return null;
  var vis=EGO?EGOIDX:ALLIDX,best=null,bd=1e9;
  for(var vi=0;vi<vis.length;vi++){
    var i=vis[vi],p=proj(i);if(!p)continue;
    var dx=mx-p[0],dy=my-p[1],d=dx*dx+dy*dy,r=rad(i)+4;
    if(d<r*r&&d<bd){bd=d;best=i;}
  }
  return best;
}
function showTip(i,x,y){
  var deg=0;for(var k in NBR[i])deg++;
  tip.innerHTML='<b>'+esc(CS.TITLE[i]||L.f[i])+'</b><span>'+esc(L.cats[L.c[i]])+' · '+deg+' link'+(deg===1?'':'s')+'</span>';
  tip.hidden=false;
  var tw=tip.offsetWidth,th=tip.offsetHeight;
  tip.style.left=Math.max(4,Math.min(W-tw-4,x+14))+'px';
  tip.style.top=Math.max(4,Math.min(H-th-4,y+14))+'px';
}
function hideTip(){tip.hidden=true;}
function clampK(k){return Math.max(.6,Math.min(4,k));}
function resetView(){M.k=1;M.tx=0;M.ty=0;M.hover=null;hideTip();draw();}
function centerNode(i){
  if(EGO){M.ego=L.f[i];egoLayout();draw();return;}
  sizeCanvas();
  M.k=Math.max(M.k,1.6);
  var p=POS[i];
  M.tx=W/2-(PAD+p[0]*(W-2*PAD))*M.k;
  M.ty=H/2-(PAD+p[1]*(H-2*PAD))*M.k;
  draw();
}

/* Under 768 px the whole graph is unreadable, so the map opens as the ego graph
   of the sheet in the drawer (or the most read sheet) until "show the whole
   map" is pressed. */
function egoLayout(){
  if(!READY)return;
  sizeCanvas();
  var btn=el('egoAll');
  if(window.innerWidth>=768||M.whole){EGO=null;EGOIDX=ALLIDX;if(btn)btn.hidden=(window.innerWidth>=768);return;}
  var f=M.ego,c=(f!==null&&f!==undefined)?CS.byFile[f]:undefined;
  if(c===undefined){c=0;for(var i=1;i<N;i++)if(L.p[i]>L.p[c])c=i;}
  var nb=Object.keys(NBR[c]).map(Number);
  nb.sort(function(a,b){return L.p[b]-L.p[a];});
  nb=nb.slice(0,26);
  nb.sort(function(a,b){return L.c[a]-L.c[b]||L.p[b]-L.p[a];});
  EGO={};EGO[c]=[W/2,H/2];
  var RX=W*.38,RY=H*.36,rings=nb.length>13?2:1,per=Math.ceil(nb.length/rings)||1;
  nb.forEach(function(i,k){
    var ring=Math.floor(k/per),inRing=k%per,cnt=Math.min(per,nb.length-ring*per);
    var ang=inRing/cnt*TAU-Math.PI/2+(ring?Math.PI/cnt:0);
    var f=rings===1?1:(ring===0?.56:1);
    EGO[i]=[W/2+RX*f*Math.cos(ang),H/2+RY*f*Math.sin(ang)];
  });
  EGOIDX=Object.keys(EGO).map(Number);
  M.k=1;M.tx=0;M.ty=0;
  if(btn)btn.hidden=false;
}

/* The map is the content of its lens, so bring it up under the sticky topbar
   rather than leaving it below the fold. */
function scrollMapIntoView(){
  var w=el('mapwrap');if(!w)return;
  var top=Math.max(0,w.getBoundingClientRect().top+window.pageYOffset-58);
  if(Math.abs(window.pageYOffset-top)>8)window.scrollTo(0,top);
}

var mapP=null;
function openMap(){
  if(!cv)return Promise.resolve();
  if(!mapP)mapP=CS.loadFull().then(function(d){
    if(!d)return null;
    prep(d);readPalette();bindMap();return d;
  });
  return mapP.then(function(d){
    if(!d){CS.toast('The catalog did not load, so the map is unavailable.');return;}
    egoLayout();draw();
  });
}

var bound=false;
function bindMap(){
  if(bound)return;bound=true;
  var pts={},dragFrom=null,dragged=false,pinchD=0;
  function ids(){return Object.keys(pts);}
  function two(){var k=ids();return[pts[k[0]],pts[k[1]]];}
  function pdist(){var t=two();return Math.hypot(t[0][0]-t[1][0],t[0][1]-t[1][1])||1;}
  function pcenter(){var t=two();return[(t[0][0]+t[1][0])/2,(t[0][1]+t[1][1])/2];}
  cv.addEventListener('pointerdown',function(e){
    try{cv.setPointerCapture(e.pointerId);}catch(err){}
    pts[e.pointerId]=[e.offsetX,e.offsetY];
    if(ids().length===2){pinchD=pdist();dragFrom=null;return;}
    dragFrom=[e.offsetX,e.offsetY,M.tx,M.ty];dragged=false;cv.classList.add('drag');
  });
  cv.addEventListener('pointermove',function(e){
    if(pts[e.pointerId])pts[e.pointerId]=[e.offsetX,e.offsetY];
    if(ids().length>=2){
      if(!EGO){
        var d=pdist();
        if(pinchD){
          var f=clampK(M.k*(d/pinchD))/M.k,c=pcenter();
          M.tx=c[0]-(c[0]-M.tx)*f;M.ty=c[1]-(c[1]-M.ty)*f;M.k*=f;draw();
        }
        pinchD=d;
      }
      return;
    }
    if(dragFrom&&!EGO){
      var dx=e.offsetX-dragFrom[0],dy=e.offsetY-dragFrom[1];
      if(!dragged&&Math.abs(dx)+Math.abs(dy)<4)return;
      dragged=true;M.tx=dragFrom[2]+dx;M.ty=dragFrom[3]+dy;hideTip();draw();return;
    }
    var h=hit(e.offsetX,e.offsetY);
    if(h!==M.hover){M.hover=h;draw();}
    if(h!==null)showTip(h,e.offsetX,e.offsetY);else hideTip();
  });
  function up(e){
    delete pts[e.pointerId];pinchD=0;cv.classList.remove('drag');
    if(dragFrom&&!dragged){
      var h=hit(e.offsetX,e.offsetY);
      if(h!==null){CS.openDrawer(L.f[h],'map');centerNode(h);}
    }
    dragFrom=null;
  }
  cv.addEventListener('pointerup',up);
  cv.addEventListener('pointercancel',function(e){delete pts[e.pointerId];pinchD=0;dragFrom=null;cv.classList.remove('drag');});
  cv.addEventListener('pointerleave',function(){if(M.hover!==null){M.hover=null;draw();}hideTip();});
  cv.addEventListener('wheel',function(e){
    if(EGO)return;
    e.preventDefault();
    var f=e.deltaY<0?1.12:1/1.12,k2=clampK(M.k*f);
    f=k2/M.k;
    M.tx=e.offsetX-(e.offsetX-M.tx)*f;M.ty=e.offsetY-(e.offsetY-M.ty)*f;M.k=k2;
    hideTip();draw();
  },{passive:false});
  cv.addEventListener('dblclick',function(e){e.preventDefault();resetView();});
  var rt=null;
  window.addEventListener('resize',function(){
    clearTimeout(rt);
    rt=setTimeout(function(){if(body.dataset.view==='map'){egoLayout();draw();}},150);
  });
  var ea=el('egoAll');
  if(ea)ea.addEventListener('click',function(){M.whole=true;egoLayout();this.hidden=true;draw();});
  var mr=el('mapreset');
  if(mr)mr.addEventListener('click',function(){M.whole=false;M.legend=[];document.querySelectorAll('.lgd').forEach(function(b){b.setAttribute('aria-pressed','false');});egoLayout();resetView();});
  var mb=el('maplistBtn');
  if(mb)mb.addEventListener('click',function(){
    var on=this.getAttribute('aria-pressed')!=='true';
    this.setAttribute('aria-pressed',on?'true':'false');
    var ml=el('maplist');
    if(on&&!ml.dataset.built)buildList(ml);
    ml.hidden=!on;
  });
}

/* The keyboard and screen-reader equivalent of the canvas: the same nodes and
   the same edges, as category > sheet > links to. */
function buildList(ml){
  var d=FULLREF,groups={},i;
  for(i=0;i<N;i++)(groups[L.c[i]]=groups[L.c[i]]||[]).push(i);
  var out='<h3>Every sheet, by category, with what it links to</h3><ul>';
  Object.keys(groups).sort(function(a,b){return L.cats[a].localeCompare(L.cats[b]);}).forEach(function(c){
    out+='<li><b>'+esc(L.cats[c])+'</b><ul>';
    groups[c].sort(function(a,b){return L.p[b]-L.p[a];}).forEach(function(i){
      var s=d.sheets[d.idx[L.f[i]]],o=(s&&s.outlinks)||[];
      out+='<li><a href="'+esc(L.f[i])+'">'+esc(CS.TITLE[i]||L.f[i])+'</a>';
      if(o.length)out+='<ul>'+o.map(function(f){
        var j=d.idx[f];
        return j===undefined?'':'<li><a href="'+esc(f)+'">'+esc(d.sheets[j].title)+'</a></li>';
      }).join('')+'</ul>';
      out+='</li>';
    });
    out+='</ul></li>';
  });
  ml.innerHTML=out+'</ul>';ml.dataset.built='1';
}

CS.showOnMap=function(file){
  var i=CS.byFile[file];
  if(i===undefined)return;
  M.ego=file;M.hover=null;
  setView('map','drawer');
  openMap().then(function(){if(READY)centerNode(i);});
};
CS.onTheme=function(){if(READY){readPalette();if(body.dataset.view==='map')draw();}};
CS.onFilter=function(){if(READY&&body.dataset.view==='map')draw();};

/* ---------------------------------------------------------------- paths --- */
function pget(id){var v=CS.lsj('path:'+id,[]);return Array.isArray(v)?v:[];}
function pset(id,a){try{CS.ls('path:'+id,JSON.stringify(a));}catch(e){}}
function paintPaths(){
  document.querySelectorAll('.trail[data-path]').forEach(function(t){
    var id=t.dataset.path,done=pget(id),pr=t.querySelector('.tprog');
    var n=pr?parseInt(pr.dataset.steps,10)||0:0;
    var k=0,i;
    for(i=0;i<n;i++)if(done.indexOf(i)>=0)k++;
    var first=-1;
    for(i=0;i<n;i++)if(done.indexOf(i)<0){first=i;break;}
    if(pr)pr.innerHTML=k?k+' of '+n+' done<span class="bar"><i style="width:'+Math.round(k/n*100)+'%"></i></span>':n+' steps';
    t.querySelectorAll('.stepper li').forEach(function(li){
      var si=parseInt(li.dataset.i,10),is=done.indexOf(si)>=0,btn=li.querySelector('.stepbtn');
      li.classList.toggle('done',is);
      if(!btn)return;
      btn.setAttribute('aria-pressed',is?'true':'false');
      btn.textContent=is?'Done':(si===first?(k?'Continue':'Start'):'Mark done');
      btn.title=is?'Mark this step not done':'Mark this step done';
    });
  });
}

/* --------------------------------------------------------------- clicks --- */
document.addEventListener('click',function(e){
  var a=e.target.closest('.lenses a');
  if(a){
    if(e.metaKey||e.ctrlKey||e.shiftKey||e.button===1)return;
    e.preventDefault();setView(a.dataset.view,'lens');return;
  }
  var lg=e.target.closest('.lgd');
  if(lg){
    var ci=parseInt(lg.dataset.lg,10),k=M.legend.indexOf(ci);
    if(k<0)M.legend.push(ci);else M.legend.splice(k,1);
    lg.setAttribute('aria-pressed',k<0?'true':'false');
    draw();return;
  }
  var sb=e.target.closest('.stepbtn');
  if(sb){
    var t=sb.closest('.trail'),id=t.dataset.path,si=parseInt(sb.dataset.i,10),d=pget(id),j=d.indexOf(si);
    if(j<0){d.push(si);CS.ga('explorer_path_step',{id:id,step:si});}else d.splice(j,1);
    pset(id,d);paintPaths();return;
  }
  var sl=e.target.closest('.stepper a');
  if(sl){
    // Optimistic: the reader is leaving for the sheet, so the step is done.
    var li=sl.closest('li'),tr=sl.closest('.trail');
    if(!li||!tr)return;
    var pid=tr.dataset.path,pi=parseInt(li.dataset.i,10),pd=pget(pid);
    if(pd.indexOf(pi)<0){pd.push(pi);pset(pid,pd);CS.ga('explorer_path_step',{id:pid,step:pi});paintPaths();}
  }
});

/* ------------------------------------------------------------- start up --- */
setView(body.dataset.view||'grid','init',true);
paintPaths();
(function(){
  var open=document.querySelector('.trail.open');
  if(open)CS.ga('explorer_path_start',{id:open.dataset.path});
})();
// Measurement hook for the performance budget (see the spec's Map lens section).
window.csExplorer={mapDrawMs:function(){return drawMs;},redraw:draw,mapState:M};
})();
</script>
</body>
</html>
