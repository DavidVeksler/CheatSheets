<?php
/**
 * popularity.php — Visualize the 30-day decayed Cloudflare view scores
 * stored in popularity.json, which is updated nightly by fetch-popularity.py.
 *
 * Score semantics: each day's raw view count is added to the accumulated total
 * after multiplying every existing score by 29/30.  After 30 days a single
 * visit contributes ~37 % of its original weight — naturally surfaces
 * consistently popular pages rather than one-day spikes.
 */

header('Content-Type: text/html; charset=utf-8');
// popularity.json only updates once nightly (fetch-popularity.py), so an hour of caching is safe.
header('Cache-Control: public, max-age=3600');

$dataFile  = __DIR__ . '/popularity.json';
// Titles and first-commit dates come from catalog.json (built by
// scripts/build_catalog.py). This used to read .metadata-cache.json, a
// by-product of the old index.php's runtime HTML parser; that parser and its
// cache are gone, and the catalog is the single extraction source now.
$cacheFile = __DIR__ . '/catalog.json';

/* ---------- Load popularity.json ---------- */
$popData = ['lastUpdated' => null, 'scores' => []];
if (is_readable($dataFile)) {
    $raw = @file_get_contents($dataFile);
    if ($raw !== false) {
        $decoded = json_decode($raw, true);
        if (is_array($decoded)) $popData = $decoded;
    }
}

$scores = $popData['scores'] ?? [];
arsort($scores);  // highest score first

/* ---------- Load the catalog for proper titles and creation dates ---------- */
// Reshaped to the {filename => ['title' =>, 'git_ctime' =>]} map this page has
// always consumed, so the rendering below is unchanged.
$metaCache = [];
if (is_readable($cacheFile)) {
    $raw = @file_get_contents($cacheFile);
    if ($raw !== false) {
        $decoded = json_decode($raw, true);
        if (is_array($decoded) && !empty($decoded['sheets']) && is_array($decoded['sheets'])) {
            foreach ($decoded['sheets'] as $sheet) {
                if (empty($sheet['file'])) continue;
                $metaCache[(string)$sheet['file']] = [
                    'title'     => (string)($sheet['title'] ?? ''),
                    'git_ctime' => (int)($sheet['created'] ?? 0),
                ];
            }
        }
    }
}

/* ---------- Category map (single source of truth: filename => category) ---------- */
$categoryMap = require __DIR__ . '/category-map.php';

/* ---------- Which cheatsheets actually exist on disk right now ---------- */
// Computed early so every panel below can drop scores/history for pages that
// have since been deleted — popularity.json (and its dailyHistory ring buffer)
// keeps a filename's old Cloudflare numbers forever, since fetch-popularity.py
// only ever adds to it. Without this filter a deleted page (e.g.
// anduril-products.html, removed from the repo but still holding a decayed
// score of ~279 from before deletion) outranks the median and shows up in
// "Needs attention" as perpetually "never reviewed", in the ranked list, and
// in every other panel below — a dead link nobody can act on.
$excludedFromCoverage = ['etz-chaim-tree-of-life.html'];
$allHtmlFiles = array_filter(glob(__DIR__ . '/*.html') ?: [], fn($p) => is_file($p));
$allHtmlNames = array_map('basename', $allHtmlFiles);
$allHtmlNames = array_values(array_diff($allHtmlNames, $excludedFromCoverage));
$totalPageCount = count($allHtmlNames);
$existingLookup = array_flip($allHtmlNames);

$scores = array_intersect_key($scores, $existingLookup);
arsort($scores);

/* ---------- Cumulative (never-decayed) lifetime view counts + 90-day history ---------- */
$totalViews        = $popData['totalViews'] ?? [];
$totalViewsHistory = $popData['totalViewsHistory'] ?? [];
ksort($totalViewsHistory); // chronological, oldest first

/* ---------- Helpers ---------- */
function h(?string $s): string {
    return htmlspecialchars((string) $s, ENT_QUOTES, 'UTF-8');
}

function filename_to_title(string $filename): string {
    $name = preg_replace('/\.html$/i', '', $filename);
    return ucwords(str_replace(['-', '_'], ' ', $name));
}

function rel_time(?string $dateStr): string {
    if ($dateStr === null) return 'never';
    $ts = strtotime($dateStr);
    if ($ts === false) return h($dateStr);
    $d = time() - $ts;
    foreach ([[86400,'day'],[3600,'hour'],[60,'minute'],[1,'second']] as [$secs,$name]) {
        if ($d >= $secs) {
            $n = (int) floor($d / $secs);
            return $n . ' ' . $name . ($n === 1 ? '' : 's') . ' ago';
        }
    }
    return 'just now';
}

// Hand-drawn 16x16 stroke icons for the top stat tiles — matches the
// inline-SVG convention chrome.php already uses for the topbar (no icon
// font, no extra CDN dependency to SRI-pin).
function stat_icon(string $name): string {
    $icons = [
        'pages'  => '<path d="M4 1.5h4.5L12 5v9.5a.5.5 0 0 1-.5.5h-7a.5.5 0 0 1-.5-.5v-13a.5.5 0 0 1 .5-.5Z"/><path d="M8.5 1.5V5H12"/>',
        'top'    => '<path d="M8 1.8l1.7 3.5 3.9.6-2.8 2.7.7 3.9L8 10.6l-3.5 1.9.7-3.9-2.8-2.7 3.9-.6L8 1.8Z"/>',
        'sum'    => '<rect x="2" y="9" width="2.4" height="5" rx=".6" fill="currentColor" stroke="none"/><rect x="6.8" y="5.5" width="2.4" height="8.5" rx=".6" fill="currentColor" stroke="none"/><rect x="11.6" y="2" width="2.4" height="12" rx=".6" fill="currentColor" stroke="none"/>',
        'clock'  => '<circle cx="8" cy="8" r="6.3"/><path d="M8 4.5V8l3 1.8"/>',
        'avg'    => '<path d="M1.5 8.5h3l1.5-4 3 7 1.5-4h3.5"/>',
        'median' => '<path d="M3 3v10M8 1.5v13M13 5v6"/><circle cx="3" cy="6" r="1.3" fill="currentColor" stroke="none"/><circle cx="8" cy="10" r="1.3" fill="currentColor" stroke="none"/><circle cx="13" cy="8.5" r="1.3" fill="currentColor" stroke="none"/>',
        'share'  => '<circle cx="8" cy="8" r="6"/><path d="M8 8V2a6 6 0 0 1 6 6H8Z" fill="currentColor" stroke="none"/>',
        'rising' => '<path d="M2 12.5l4-4.5 3 3 5-6"/><path d="M10.5 4.5H14V8"/>',
        'eye'    => '<path d="M1.3 8S3.8 3 8 3s6.7 5 6.7 5-2.5 5-6.7 5-6.7-5-6.7-5Z"/><circle cx="8" cy="8" r="2"/>',
        'layers' => '<path d="M8 2 14 5.5 8 9 2 5.5 8 2Z"/><path d="M2 8.5 8 12l6-3.5"/><path d="M2 11.5 8 15l6-3.5"/>',
        'list'   => '<path d="M6 3.5h8M6 8h8M6 12.5h8"/><circle cx="2.2" cy="3.5" r=".9" fill="currentColor" stroke="none"/><circle cx="2.2" cy="8" r=".9" fill="currentColor" stroke="none"/><circle cx="2.2" cy="12.5" r=".9" fill="currentColor" stroke="none"/>',
        'eyeoff' => '<path d="M1.3 8S3.8 3 8 3s6.7 5 6.7 5-2.5 5-6.7 5-6.7-5-6.7-5Z"/><circle cx="8" cy="8" r="2"/><path d="M2 2l12 12"/>',
    ];
    return '<svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">' . ($icons[$name] ?? '') . '</svg>';
}

/* ---------- Derived stats ---------- */
$rankedCount = count($scores);
$totalScore  = array_sum($scores);
$maxScore    = $rankedCount > 0 ? (float) reset($scores) : 1.0;
$lastUpdated = $popData['lastUpdated'];

$scoreVals   = array_values($scores);  // already arsort'd → descending
$avgScore    = $rankedCount > 0 ? $totalScore / $rankedCount : 0;
$medianScore = 0;
if ($rankedCount > 0) {
    $mid = intdiv($rankedCount, 2);
    $medianScore = $rankedCount % 2 === 1
        ? $scoreVals[$mid]
        : ($scoreVals[$mid - 1] + $scoreVals[$mid]) / 2;
}
$top3Share  = $totalScore > 0 ? round(array_sum(array_slice($scoreVals, 0, 3)) / $totalScore * 100, 1) : 0;
$top10Share = $totalScore > 0 ? round(array_sum(array_slice($scoreVals, 0, 10)) / $totalScore * 100, 1) : 0;

/* ---------- All-time (never-decayed) view total ---------- */
$totalViewsAllTime = array_sum($totalViews);

/* ---------- Coverage: published cheatsheets with zero recorded views ---------- */
// $allHtmlNames / $totalPageCount come from the existence filter above.
// Mirrors index.php's own $excludedItems — the one other place that decides what counts as a real cheatsheet.
$untrackedPages = array_values(array_diff($allHtmlNames, array_keys($scores)));
$untrackedCount = count($untrackedPages);

/* ---------- Category breakdown: sum of decayed scores per category ---------- */
$categoryTotals = [];
foreach ($scores as $filename => $score) {
    $cat = $categoryMap[$filename] ?? 'Other';
    $categoryTotals[$cat] = ($categoryTotals[$cat] ?? 0) + $score;
}
arsort($categoryTotals);
$categoryRows = [];
foreach ($categoryTotals as $cat => $catScore) {
    $categoryRows[] = [
        'category' => $cat,
        'score'    => $catScore,
        'pct'      => $totalScore > 0 ? round($catScore / $totalScore * 100, 1) : 0,
    ];
}
$maxCategoryScore = $categoryRows ? $categoryRows[0]['score'] : 1.0;

/* ---------- Trending now: today's raw views far outpacing the page's accumulated score ---------- */
$dailyViewsRaw = array_intersect_key($popData['dailyViews'] ?? [], $existingLookup);
$trending = [];
foreach ($dailyViewsRaw as $filename => $dayCount) {
    if ($dayCount < 5) continue; // filter noise from single-digit blips
    $baseScore = $scores[$filename] ?? 0.0;
    $priorScore = max($baseScore - $dayCount, 0.0); // score before today's contribution
    $surge = ($priorScore + 1) > 0 ? $dayCount / ($priorScore + 1) : $dayCount;
    $trending[] = [
        'filename' => $filename,
        'title'    => $metaCache[$filename]['title'] ?? filename_to_title($filename),
        'today'    => $dayCount,
        'surge'    => $surge,
    ];
}
usort($trending, fn($a, $b) => $b['surge'] <=> $a['surge']);
$trending = array_slice($trending, 0, 5);

/* ---------- Daily-history prep, shared by the momentum panel and row sparklines ---------- */
// "dailyHistory" is fetch-popularity.py's per-file 30-day ring buffer —
// collected nightly but never rendered anywhere until now.
$dailyHistory = array_intersect_key($popData['dailyHistory'] ?? [], $existingLookup);
$allHistoryDates = [];
foreach ($dailyHistory as $days) {
    foreach (array_keys($days) as $d) { $allHistoryDates[$d] = true; }
}
$historyDatesSorted = array_keys($allHistoryDates);
sort($historyDatesSorted);
$historySpanDaysAvailable = count($historyDatesSorted);

// Sparklines only switch on once a few real days have accumulated, so early
// on every row quietly omits the chart instead of drawing a misleading flat
// line from a single day of data.
$sparklineReady = $historySpanDaysAvailable >= 4;
$sparkDates = $sparklineReady ? array_slice($historyDatesSorted, -14) : [];
function row_sparkline_points(array $days, array $dates, float $w, float $h): string {
    $n = count($dates);
    if ($n < 2) return '';
    $max = 0.0;
    foreach ($dates as $d) $max = max($max, (float) ($days[$d] ?? 0));
    if ($max <= 0) return '';
    $pts = [];
    foreach ($dates as $i => $d) {
        $x = round($i / ($n - 1) * $w, 1);
        $y = round($h - ((float) ($days[$d] ?? 0) / $max) * $h, 1);
        $pts[] = "$x,$y";
    }
    return implode(' ', $pts);
}

/* ---------- Build ranked rows ---------- */
$rows = [];
$rank = 0;
foreach ($scores as $filename => $score) {
    $rank++;
    $title    = $metaCache[$filename]['title'] ?? filename_to_title($filename);
    $pct      = $totalScore > 0 ? round($score / $totalScore * 100, 1) : 0;
    $bar      = $maxScore > 0   ? round($score / $maxScore * 100, 2) : 0;
    $category = $categoryMap[$filename] ?? 'Other';
    $views    = (int) ($totalViews[$filename] ?? 0);
    $spark    = $sparklineReady ? row_sparkline_points($dailyHistory[$filename] ?? [], $sparkDates, 60, 18) : '';
    $rows[] = compact('rank', 'filename', 'title', 'score', 'pct', 'bar', 'category', 'views', 'spark');
}

/* ---------- Rising stars: pages published in the last 30 days, ranked by score ---------- */
$risingCutoff = time() - 30 * 86400;
$risingStars  = [];
foreach ($scores as $filename => $score) {
    $ctime = $metaCache[$filename]['git_ctime'] ?? 0;
    if ($ctime >= $risingCutoff) {
        $risingStars[] = [
            'filename' => $filename,
            'title'    => $metaCache[$filename]['title'] ?? filename_to_title($filename),
            'score'    => $score,
            'ctime'    => $ctime,
        ];
    }
}
usort($risingStars, fn($a, $b) => $b['score'] <=> $a['score']);
$risingStarCount = count($risingStars);
$risingStars      = array_slice($risingStars, 0, 5);

/* ---------- Needs attention: well-trafficked pages overdue for a fact review ---------- */
// Cross-references refresh-status.json (written only by the weekly-freshness
// routine) against the popularity score, so the busiest pages with the
// stalest facts surface first — the highest-leverage review queue.
$refreshFile = __DIR__ . '/refresh-status.json';
$refreshData = [];
if (is_readable($refreshFile)) {
    $raw = @file_get_contents($refreshFile);
    if ($raw !== false) {
        $decoded = json_decode($raw, true);
        if (is_array($decoded) && !empty($decoded['files']) && is_array($decoded['files'])) {
            $refreshData = $decoded['files'];
        }
    }
}
$staleCutoffDays = 60;
$needsAttention = [];
foreach ($scores as $filename => $score) {
    if ($score < $medianScore) continue; // only pages that actually get traffic
    $lastReviewed = $refreshData[$filename]['last_reviewed'] ?? null;
    $daysSince = $lastReviewed !== null ? (int) floor((time() - strtotime($lastReviewed)) / 86400) : null;
    if ($daysSince !== null && $daysSince < $staleCutoffDays) continue;
    $needsAttention[] = [
        'filename'  => $filename,
        'title'     => $metaCache[$filename]['title'] ?? filename_to_title($filename),
        'score'     => $score,
        'daysSince' => $daysSince,
    ];
}
usort($needsAttention, fn($a, $b) => $b['score'] <=> $a['score']);
$needsAttention = array_slice($needsAttention, 0, 6);

/* ---------- Momentum: trailing 7-day traffic swing per page ---------- */
// Reuses the $dailyHistory / $historyDatesSorted prep above. Needs at least
// two full trailing 7-day windows of real history before the comparison
// means anything, so it degrades to an honest "collecting data" message
// rather than showing noise from a handful of days.
$momentumReady = $historySpanDaysAvailable >= 10;
$movers = [];
if ($momentumReady) {
    $recentWindow = array_slice($historyDatesSorted, -7);
    $priorWindow  = array_slice($historyDatesSorted, -14, 7);
    foreach ($dailyHistory as $filename => $days) {
        $recentSum = 0; foreach ($recentWindow as $d) $recentSum += $days[$d] ?? 0;
        $priorSum  = 0; foreach ($priorWindow as $d)  $priorSum  += $days[$d] ?? 0;
        if ($recentSum + $priorSum < 5) continue; // skip pages too quiet to read a trend from
        $delta = $recentSum - $priorSum;
        $pct = $priorSum > 0 ? round($delta / $priorSum * 100) : ($recentSum > 0 ? 100 : 0);
        $movers[] = [
            'filename' => $filename,
            'title'    => $metaCache[$filename]['title'] ?? filename_to_title($filename),
            'recent'   => $recentSum,
            'prior'    => $priorSum,
            'pct'      => $pct,
        ];
    }
    usort($movers, fn($a, $b) => abs($b['pct']) <=> abs($a['pct']));
    $movers = array_slice($movers, 0, 6);
}

/* ---------- Zero-view pages, grouped by category (detail behind the summary stat) ---------- */
$untrackedByCategory = [];
foreach ($untrackedPages as $filename) {
    $cat = $categoryMap[$filename] ?? 'Other';
    $untrackedByCategory[$cat][] = [
        'filename' => $filename,
        'title'    => $metaCache[$filename]['title'] ?? filename_to_title($filename),
    ];
}
ksort($untrackedByCategory);

/* ---------- Score distribution histogram ---------- */
$buckets = [
    ['label' => '0–1',    'min' => 0.0,  'max' => 1.0],
    ['label' => '1–5',    'min' => 1.0,  'max' => 5.0],
    ['label' => '5–20',   'min' => 5.0,  'max' => 20.0],
    ['label' => '20–50',  'min' => 20.0, 'max' => 50.0],
    ['label' => '50–200', 'min' => 50.0, 'max' => 200.0],
    ['label' => '200+',   'min' => 200.0,'max' => INF],
];
foreach ($buckets as $i => $b) { $buckets[$i]['count'] = 0; }
foreach ($scores as $score) {
    foreach ($buckets as $i => $b) {
        if ($score >= $b['min'] && $score < $b['max']) { $buckets[$i]['count']++; break; }
    }
}
$maxBucketCount = max(1, max(array_column($buckets, 'count')));

/* ---------- Last 24 hours (raw, undecayed view counts) ---------- */
$dailyViews = array_intersect_key($popData['dailyViews'] ?? [], $existingLookup);
arsort($dailyViews);
$totalDailyViews = array_sum($dailyViews);
$dailyRows = [];
$i = 0;
foreach ($dailyViews as $filename => $count) {
    if (++$i > 5) break;
    $dailyRows[] = [
        'filename' => $filename,
        'title'    => $metaCache[$filename]['title'] ?? filename_to_title($filename),
        'count'    => $count,
        'pct'      => $totalDailyViews > 0 ? round($count / $totalDailyViews * 100, 1) : 0,
    ];
}

/* ---------- 90-day site-wide traffic trend (sparkline) ---------- */
$historyVals   = array_values($totalViewsHistory);
$historyDays   = count($historyVals);
$maxHistoryVal = $historyVals ? max(max($historyVals), 1) : 1;
$sparkWidth  = 600;
$sparkHeight = 60;
$sparkPoints = '';
if ($historyDays > 1) {
    $pts = [];
    foreach ($historyVals as $idx => $val) {
        $x = round($idx / ($historyDays - 1) * $sparkWidth, 1);
        $y = round($sparkHeight - ($val / $maxHistoryVal) * $sparkHeight, 1);
        $pts[] = "$x,$y";
    }
    $sparkPoints = implode(' ', $pts);
}
$historyTotal = array_sum($historyVals);
$historyDates = array_keys($totalViewsHistory);
$historySpanLabel = $historyDays > 0
    ? (date('M j', strtotime($historyDates[0])) . ' – ' . date('M j', strtotime($historyDates[$historyDays - 1])))
    : '';
$baseUrl = 'https://cheatsheets.davidveksler.com/';
require __DIR__ . '/lib/chrome.php';
chrome_open(
    "Popularity · Cheatsheets",
    '30-day trending view counts for every cheatsheet, pulled nightly from Cloudflare Analytics.',
    '📊',
    $baseUrl . 'popularity.php',
    'popularity'
);
?>
<style>
.stat{display:flex;align-items:center;gap:11px}
.stat-icon{flex:none;width:32px;height:32px;border-radius:8px;display:flex;align-items:center;justify-content:center;background:var(--accent-surface);color:var(--accent)}
.stat-icon svg{width:17px;height:17px}
.stat-body{min-width:0}
.mini-panel{border:1px solid var(--rule);border-radius:8px;background:var(--surface);padding:14px 16px;height:100%}
.mini-panel h2{font-size:13px;margin-bottom:10px;display:flex;align-items:baseline;gap:8px}
.mini-panel h2 .age{font-size:11.5px;color:var(--muted);font-weight:500;text-transform:none;letter-spacing:0}
.mini-row{display:grid;grid-template-columns:1fr auto;gap:2px 10px;align-items:center;padding:6px 0}
.mini-row+.mini-row{border-top:1px dashed var(--rule)}
.mini-row .mini-label{min-width:0;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;font-size:13px;color:var(--ink)}
.mini-row .mini-value{font-family:var(--mono);font-size:12px;color:var(--muted);white-space:nowrap;text-align:right}
.mini-bar{grid-column:1/3;height:5px;border-radius:3px;background:var(--rule);overflow:hidden}
.mini-bar i{display:block;height:100%;background:var(--accent)}
.mini-empty{color:var(--muted);font-size:13px;font-style:italic}
.mini-age{color:var(--muted);font-size:12px}

.dist-row{display:grid;grid-template-columns:3.6rem 1fr 1.8rem;gap:8px;align-items:center;padding:4px 0}
.dist-row .dl{font-size:12px;color:var(--muted);font-variant-numeric:tabular-nums}
.dist-row .dc{font-size:12px;text-align:right;font-variant-numeric:tabular-nums;color:var(--ink)}
.dist-track{height:8px;border-radius:3px;background:var(--rule);overflow:hidden}
.dist-fill{height:100%;border-radius:3px;background:var(--accent)}

.panels{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:14px;margin-bottom:22px}
.panels-2{display:grid;grid-template-columns:repeat(auto-fit,minmax(320px,1fr));gap:14px;margin-bottom:22px}

.rank-row{display:flex;align-items:center;gap:14px;padding:10px 16px;border-bottom:1px solid var(--rule)}
.rank-row[hidden]{display:none}
.rank-row:last-child{border-bottom:0}
.rank-row:hover{background:var(--accent-surface)}
.rank-row.top1{border-left:3px solid var(--gold)}
.rank-num{font-family:var(--mono);font-weight:650;font-size:13px;text-align:center;width:26px;height:26px;line-height:26px;border-radius:50%;flex:none;background:var(--accent-surface);color:var(--accent)}
.rank-row.top1 .rank-num{background:color-mix(in srgb,var(--gold) 20%,transparent);color:var(--gold)}
.rank-info{min-width:0;flex:1}
.rank-title{font-weight:600;font-size:14px;color:var(--ink);white-space:nowrap;overflow:hidden;text-overflow:ellipsis;display:block}
.rank-title:hover{text-decoration:underline}
.rank-bar-track{height:5px;border-radius:3px;background:var(--rule);margin-top:5px;overflow:hidden}
.rank-bar-fill{height:100%;border-radius:3px;background:var(--accent)}
.rank-row.top1 .rank-bar-fill{background:var(--gold)}
.rank-score{text-align:right;white-space:nowrap;flex:none}
.rank-score .val{font-family:var(--mono);font-weight:650;font-size:14px}
.rank-score .pct{color:var(--muted);font-size:11.5px}
@media (max-width:575px){ .rank-score{display:none} }
.rank-spark{flex:none;color:var(--muted);opacity:.8}
@media (max-width:800px){ .rank-spark{display:none} }

.mv-row{display:grid;grid-template-columns:1fr auto auto;gap:2px 10px;align-items:center;padding:6px 0}
.mv-row+.mv-row{border-top:1px dashed var(--rule)}
.mv-row .mv-label{min-width:0;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;font-size:13px;color:var(--ink)}
.mv-pct{font-family:var(--mono);font-size:12px;font-weight:650;text-align:right;white-space:nowrap}
.mv-pct.up{color:var(--success)}
.mv-pct.down{color:var(--danger)}
.mv-detail{color:var(--muted);font-size:11.5px;text-align:right;white-space:nowrap}
.na-row{display:flex;align-items:baseline;gap:8px;padding:6px 0}
.na-row+.na-row{border-top:1px dashed var(--rule)}
.na-row .na-label{min-width:0;flex:1;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;font-size:13px;color:var(--ink)}
.na-row .na-days{font-family:var(--mono);font-size:11.5px;color:var(--danger);white-space:nowrap;flex:none}

.rank-toolbar{display:flex;flex-wrap:wrap;gap:8px;align-items:center;margin-bottom:10px}
.rank-toolbar input[type=search]{flex:1 1 200px;min-width:0;padding:7px 10px;border:1px solid var(--rule);border-radius:6px;background:var(--surface);color:var(--ink);font:inherit;font-size:13px}
.rank-toolbar select{padding:7px 10px;border:1px solid var(--rule);border-radius:6px;background:var(--surface);color:var(--ink);font:inherit;font-size:13px}
.rank-sort{display:inline-flex;border:1px solid var(--rule);border-radius:6px;overflow:hidden}
.rank-sort button{background:var(--surface);border:0;padding:7px 10px;font-size:13px;cursor:pointer;color:var(--muted)}
.rank-sort button+button{border-left:1px solid var(--rule)}
.rank-sort button.cur{background:var(--accent-surface);color:var(--accent);font-weight:620}
.rank-empty{padding:20px 16px;color:var(--muted);font-size:13.5px;text-align:center}
.zero-detail{margin-bottom:22px}
.zero-detail summary{cursor:pointer;font-size:13.5px;color:var(--muted);padding:2px 0}
.zero-detail summary:hover{color:var(--ink)}
.zero-cat{margin:12px 0}
.zero-cat h3{font-size:12px;text-transform:uppercase;letter-spacing:.07em;color:var(--muted);margin:0 0 6px}
.zero-list{display:flex;flex-wrap:wrap;gap:6px 10px}
.zero-list a{font-size:13px}

@media (prefers-reduced-motion: no-preference){
  .rank-bar-fill,.mini-bar i,.dist-fill{transition:width .8s cubic-bezier(.16,1,.3,1)}
  .mini-panel,.rank-toolbar,.list-card{animation:fadeInUp .45s ease both}
  .panels .mini-panel:nth-child(2){animation-delay:.06s}
  .panels .mini-panel:nth-child(3){animation-delay:.12s}
  .panels-2 .mini-panel:nth-child(2){animation-delay:.06s}
  @keyframes fadeInUp{from{opacity:0;transform:translateY(6px)}to{opacity:1;transform:translateY(0)}}
}
</style>

<div class="wrap">
<section class="hero">
  <h1>Popularity</h1>
  <p class="lead">
    30-day trending scores pulled nightly from Cloudflare Analytics.
    <?php if ($lastUpdated): ?>
      Last updated <strong style="color:var(--ink)"><?php echo h($lastUpdated); ?></strong> (<?php echo rel_time($lastUpdated); ?>).
    <?php else: ?>
      No data yet — run <code>fetch-popularity.py</code> to seed.
    <?php endif; ?>
  </p>
</section>

<?php if ($rankedCount === 0): ?>
  <div class="note warn"><code>popularity.json</code> is empty or missing. Run <code>python3 fetch-popularity.py</code> to fetch data from Cloudflare.</div>
<?php else: ?>

<div class="stats">
  <div class="stat"><div class="stat-icon"><?php echo stat_icon('pages'); ?></div><div class="stat-body"><div class="n"><?php echo number_format($rankedCount); ?></div><div class="l">Pages tracked</div></div></div>
  <div class="stat"><div class="stat-icon"><?php echo stat_icon('top'); ?></div><div class="stat-body"><div class="n"><?php echo number_format((int) $maxScore); ?></div><div class="l">Top page score</div></div></div>
  <div class="stat"><div class="stat-icon"><?php echo stat_icon('sum'); ?></div><div class="stat-body"><div class="n"><?php echo number_format((int) $totalScore); ?></div><div class="l">Total score sum</div></div></div>
  <div class="stat"><div class="stat-icon"><?php echo stat_icon('clock'); ?></div><div class="stat-body"><div class="n" style="font-size:14px"><?php echo $lastUpdated ? h($lastUpdated) : '—'; ?></div><div class="l">Last updated</div></div></div>
  <div class="stat"><div class="stat-icon"><?php echo stat_icon('avg'); ?></div><div class="stat-body"><div class="n"><?php echo number_format($avgScore, 1); ?></div><div class="l">Avg score / page</div></div></div>
  <div class="stat"><div class="stat-icon"><?php echo stat_icon('median'); ?></div><div class="stat-body"><div class="n"><?php echo number_format($medianScore, 1); ?></div><div class="l">Median score</div></div></div>
  <div class="stat"><div class="stat-icon"><?php echo stat_icon('share'); ?></div><div class="stat-body"><div class="n"><?php echo $top3Share; ?>&thinsp;%</div><div class="l">Top 3 share of views</div></div></div>
  <div class="stat"><div class="stat-icon"><?php echo stat_icon('rising'); ?></div><div class="stat-body"><div class="n"><?php echo number_format($risingStarCount); ?></div><div class="l">Rising stars (&le;30d)</div></div></div>
  <div class="stat"><div class="stat-icon"><?php echo stat_icon('eye'); ?></div><div class="stat-body"><div class="n"><?php echo number_format($totalDailyViews); ?></div><div class="l">Views yesterday</div></div></div>
  <div class="stat"><div class="stat-icon"><?php echo stat_icon('layers'); ?></div><div class="stat-body"><div class="n"><?php echo number_format($totalViewsAllTime); ?></div><div class="l">All-time views tracked</div></div></div>
  <div class="stat"><div class="stat-icon"><?php echo stat_icon('list'); ?></div><div class="stat-body"><div class="n"><?php echo $top10Share; ?>&thinsp;%</div><div class="l">Top 10 share of views</div></div></div>
  <div class="stat"><div class="stat-icon"><?php echo stat_icon('eyeoff'); ?></div><div class="stat-body"><div class="n"><?php echo number_format($untrackedCount); ?> <span style="color:var(--muted);font-size:.85em">/ <?php echo number_format($totalPageCount); ?></span></div><div class="l">Pages with zero views</div></div></div>
</div>

<div class="note" style="margin-bottom:22px">
  Each day's raw view count is added to the score after multiplying existing values by <strong>29/30</strong>.
  After 30 days a single visit contributes ~37&nbsp;% of its original weight, so this reflects
  <em>consistently popular</em> pages — not one-day spikes. Scores reset to zero over ~3 months of inactivity.
  "All-time views tracked" accumulates from the day this counter was added and does not include views from before then.
</div>

<?php if ($historyDays > 1): ?>
<div class="mini-panel" style="margin-bottom:22px">
  <h2>Site-wide traffic <span class="age">(<?php echo h($historySpanLabel); ?> · <?php echo number_format($historyTotal); ?> views)</span></h2>
  <svg viewBox="0 0 <?php echo $sparkWidth; ?> <?php echo $sparkHeight; ?>" preserveAspectRatio="none" style="width:100%;height:60px;display:block" role="img" aria-label="Daily site-wide view count over the last <?php echo $historyDays; ?> days">
    <polyline points="<?php echo h($sparkPoints); ?>" fill="none" stroke="var(--accent)" stroke-width="1.6" vector-effect="non-scaling-stroke" stroke-linejoin="round" />
  </svg>
</div>
<?php endif; ?>

<div class="panels">
  <div class="mini-panel">
    <h2>Rising stars <span class="age">(published &le;30d ago)</span></h2>
    <?php if (empty($risingStars)): ?>
      <p class="mini-empty">No pages published in the last 30 days.</p>
    <?php else: foreach ($risingStars as $star): ?>
      <div class="mini-row">
        <a class="mini-label" href="<?php echo h($star['filename']); ?>" target="_blank" title="<?php echo h($star['title']); ?>"><?php echo h($star['title']); ?></a>
        <span class="mini-value"><?php echo number_format($star['score'], 0); ?></span>
      </div>
      <div class="mini-age" style="margin:-2px 0 6px"><?php echo h(rel_time(date('c', $star['ctime']))); ?></div>
    <?php endforeach; endif; ?>
  </div>

  <div class="mini-panel">
    <h2>Score distribution</h2>
    <?php foreach ($buckets as $b): $w = round($b['count'] / $maxBucketCount * 100, 1); ?>
    <div class="dist-row">
      <span class="dl"><?php echo h($b['label']); ?></span>
      <div class="dist-track"><div class="dist-fill" style="width:<?php echo $w; ?>%"></div></div>
      <span class="dc"><?php echo $b['count']; ?></span>
    </div>
    <?php endforeach; ?>
  </div>

  <div class="mini-panel">
    <h2>Last 24 hours</h2>
    <?php if (empty($dailyRows)): ?>
      <p class="mini-empty">No daily view data yet — populated by the next nightly run.</p>
    <?php else: foreach ($dailyRows as $day): ?>
      <div class="mini-row">
        <a class="mini-label" href="<?php echo h($day['filename']); ?>" target="_blank" title="<?php echo h($day['title']); ?>"><?php echo h($day['title']); ?></a>
        <span class="mini-value"><?php echo number_format($day['count']); ?></span>
      </div>
    <?php endforeach; endif; ?>
  </div>
</div>

<div class="panels-2">
  <div class="mini-panel">
    <h2>By category</h2>
    <?php foreach ($categoryRows as $cr): $w = round($cr['score'] / $maxCategoryScore * 100, 1); ?>
    <div class="dist-row" style="grid-template-columns:9rem 1fr 2.8rem">
      <span class="dl" style="white-space:nowrap;overflow:hidden;text-overflow:ellipsis" title="<?php echo h($cr['category']); ?>"><?php echo h($cr['category']); ?></span>
      <div class="dist-track"><div class="dist-fill" style="width:<?php echo $w; ?>%"></div></div>
      <span class="dc"><?php echo $cr['pct']; ?>&thinsp;%</span>
    </div>
    <?php endforeach; ?>
  </div>

  <div class="mini-panel">
    <h2>Trending now <span class="age">(today's views vs. accumulated score)</span></h2>
    <?php if (empty($trending)): ?>
      <p class="mini-empty">No pages surging above the noise floor right now.</p>
    <?php else: foreach ($trending as $t): ?>
      <div class="mini-row">
        <a class="mini-label" href="<?php echo h($t['filename']); ?>" target="_blank" title="<?php echo h($t['title']); ?>"><?php echo h($t['title']); ?></a>
        <span class="mini-value"><?php echo number_format($t['today']); ?> today</span>
      </div>
    <?php endforeach; endif; ?>
  </div>

  <div class="mini-panel">
    <h2>Needs attention <span class="age">(popular, ≥<?php echo $staleCutoffDays; ?>d since fact review)</span></h2>
    <?php if (empty($needsAttention)): ?>
      <p class="mini-empty">Every well-trafficked page has been reviewed within <?php echo $staleCutoffDays; ?> days. Nothing overdue.</p>
    <?php else: foreach ($needsAttention as $na): ?>
      <div class="na-row">
        <a class="na-label" href="<?php echo h($na['filename']); ?>" target="_blank" title="<?php echo h($na['title']); ?>"><?php echo h($na['title']); ?></a>
        <span class="na-days"><?php echo $na['daysSince'] === null ? 'never reviewed' : $na['daysSince'] . 'd stale'; ?></span>
      </div>
    <?php endforeach; endif; ?>
  </div>

  <div class="mini-panel">
    <h2>Momentum <span class="age">(last 7 days vs. the 7 before)</span></h2>
    <?php if (!$momentumReady): ?>
      <p class="mini-empty">Collecting daily history — this panel unlocks once <?php echo 10 - $historySpanDaysAvailable; ?> more day<?php echo (10 - $historySpanDaysAvailable) === 1 ? '' : 's'; ?> of Cloudflare data has accumulated.</p>
    <?php elseif (empty($movers)): ?>
      <p class="mini-empty">No page has enough recent traffic yet to read a clear trend from.</p>
    <?php else: foreach ($movers as $m): $dir = $m['pct'] > 0 ? 'up' : ($m['pct'] < 0 ? 'down' : ''); ?>
      <div class="mv-row">
        <a class="mv-label" href="<?php echo h($m['filename']); ?>" target="_blank" title="<?php echo h($m['title']); ?>"><?php echo h($m['title']); ?></a>
        <span class="mv-pct <?php echo $dir; ?>"><?php echo $m['pct'] > 0 ? '+' : ''; ?><?php echo $m['pct']; ?>&thinsp;%</span>
        <span class="mv-detail"><?php echo number_format($m['prior']); ?>→<?php echo number_format($m['recent']); ?></span>
      </div>
    <?php endforeach; endif; ?>
  </div>
</div>

<?php if (!empty($untrackedByCategory)): ?>
<details class="zero-detail">
  <summary><?php echo number_format($untrackedCount); ?> page<?php echo $untrackedCount === 1 ? '' : 's'; ?> with zero recorded views — show which ones, by category</summary>
  <?php foreach ($untrackedByCategory as $cat => $pages): ?>
    <div class="zero-cat">
      <h3><?php echo h($cat); ?> (<?php echo count($pages); ?>)</h3>
      <div class="zero-list">
        <?php foreach ($pages as $p): ?>
          <a href="<?php echo h($p['filename']); ?>" target="_blank"><?php echo h($p['title']); ?></a>
        <?php endforeach; ?>
      </div>
    </div>
  <?php endforeach; ?>
</details>
<?php endif; ?>

<p class="lbl sectlbl">Ranked by decayed 30-day score</p>
<div class="rank-toolbar">
  <input type="search" id="rankSearch" placeholder="Filter by title&hellip;" aria-label="Filter ranked list by title" autocomplete="off" spellcheck="false">
  <select id="rankCategory" aria-label="Filter by category">
    <option value="">All categories</option>
    <?php foreach (array_keys($categoryTotals) as $cat): ?>
      <option value="<?php echo h($cat); ?>"><?php echo h($cat); ?></option>
    <?php endforeach; ?>
  </select>
  <div class="rank-sort" role="group" aria-label="Sort ranked list">
    <button type="button" data-sort="score" class="cur">Score</button>
    <button type="button" data-sort="views">All-time views</button>
    <button type="button" data-sort="title">Title A&ndash;Z</button>
  </div>
</div>
<div class="list-card" role="list" id="rankList">
  <?php foreach ($rows as $row): $isTop1 = $row['rank'] === 1; ?>
  <div class="rank-row<?php echo $isTop1 ? ' top1' : ''; ?>" role="listitem"
       data-title="<?php echo h(mb_strtolower($row['title'])); ?>" data-category="<?php echo h($row['category']); ?>"
       data-score="<?php echo $row['score']; ?>" data-views="<?php echo $row['views']; ?>">
    <div class="rank-num" aria-label="Rank <?php echo $row['rank']; ?>"><?php echo $row['rank']; ?></div>
    <div class="rank-info">
      <a class="rank-title" href="<?php echo h($row['filename']); ?>" target="_blank" title="<?php echo h($row['filename']); ?>"><?php echo h($row['title']); ?></a>
      <div class="rank-bar-track" aria-hidden="true"><div class="rank-bar-fill" style="width:<?php echo $row['bar']; ?>%"></div></div>
    </div>
    <?php if ($row['spark'] !== ''): ?>
    <svg class="rank-spark" width="60" height="18" viewBox="0 0 60 18" preserveAspectRatio="none" aria-hidden="true">
      <polyline points="<?php echo h($row['spark']); ?>" fill="none" stroke="currentColor" stroke-width="1.4" vector-effect="non-scaling-stroke" stroke-linejoin="round" />
    </svg>
    <?php endif; ?>
    <div class="rank-score">
      <div class="val num"><?php echo number_format($row['score'], 0); ?></div>
      <div class="pct"><?php echo $row['pct']; ?>&thinsp;%</div>
    </div>
  </div>
  <?php endforeach; ?>
  <p class="rank-empty" id="rankEmpty" hidden>No pages match that filter.</p>
</div>

<script>
(function(){
  var list = document.getElementById('rankList');
  if (!list) return;
  var rows = Array.prototype.slice.call(list.querySelectorAll('.rank-row'));
  var search = document.getElementById('rankSearch');
  var catSel = document.getElementById('rankCategory');
  var sortBtns = Array.prototype.slice.call(document.querySelectorAll('.rank-sort button'));
  var empty = document.getElementById('rankEmpty');
  var curSort = 'score';

  function applyFilter(){
    var q = (search.value || '').toLowerCase().trim();
    var cat = catSel.value;
    var visible = 0;
    rows.forEach(function(r){
      var match = (!q || r.dataset.title.indexOf(q) !== -1) && (!cat || r.dataset.category === cat);
      r.hidden = !match;
      if (match) visible++;
    });
    empty.hidden = visible !== 0;
  }
  function applySort(){
    rows.slice().sort(function(a, b){
      if (curSort === 'title') return a.dataset.title.localeCompare(b.dataset.title);
      return (parseFloat(b.dataset[curSort]) || 0) - (parseFloat(a.dataset[curSort]) || 0);
    }).forEach(function(r){ list.insertBefore(r, empty); });
  }
  search.addEventListener('input', applyFilter);
  catSel.addEventListener('change', applyFilter);
  sortBtns.forEach(function(btn){
    btn.addEventListener('click', function(){
      curSort = btn.dataset.sort;
      sortBtns.forEach(function(b){ b.classList.toggle('cur', b === btn); });
      applySort();
    });
  });

  if (!(window.matchMedia && matchMedia('(prefers-reduced-motion: reduce)').matches)) {
    document.querySelectorAll('.rank-bar-fill, .mini-bar i, .dist-fill').forEach(function(el){
      var w = el.style.width;
      el.style.width = '0%';
      requestAnimationFrame(function(){ requestAnimationFrame(function(){ el.style.width = w; }); });
    });
  }
})();
</script>

<?php endif; ?>
</div>
<?php chrome_close(); ?>

