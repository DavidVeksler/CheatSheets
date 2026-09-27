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
/* ---------- Referrers: long-term daily aggregates from the origin nginx logs ---------- */
// .referrers.json is written nightly on the server by scripts/referrer_accumulate.py
// (Cloudflare Free exposes no referrers; the logs rotate out after ~3 weeks, the store
// keeps every day). Gitignored and 404'd over HTTP; absent locally unless copied down.
$refStore = [];
$refFile = __DIR__ . '/.referrers.json';
if (is_readable($refFile)) {
    $decoded = json_decode((string) @file_get_contents($refFile), true);
    if (is_array($decoded) && is_array($decoded['days'] ?? null)) $refStore = $decoded['days'];
}
ksort($refStore);
$refDates = array_keys($refStore);
$refDayCount = count($refDates);
// Chart channels in fixed palette order; everything else referred folds into "Other".
$refChartChannels = ['Search engine' => 'c1', 'AI assistant' => 'c2', 'Reddit' => 'c3', 'Social' => 'c4', 'Other referrals' => 'c5'];
function ref_chart_channel(string $ch): ?string {
    if ($ch === 'Internal' || $ch === 'Direct / no referrer') return null;
    return in_array($ch, ['Search engine', 'AI assistant', 'Reddit', 'Social'], true) ? $ch : 'Other referrals';
}
function ref_page_label(string $path, array $metaCache): string {
    if ($path === '/') return 'Home (Explorer)';
    $file = ltrim($path, '/');
    if (isset($metaCache[$file])) return $metaCache[$file]['title'];
    return str_ends_with($file, '.html') ? filename_to_title($file) : '/' . $file . ' hub';
}
$refReady = $refDayCount > 0;
if ($refReady) {
    $refLast = $refDates[$refDayCount - 1];
    $refWin = min(30, max(1, intdiv($refDayCount, 2)));  // compare equal windows while history is short
    $refCurStart  = date('Y-m-d', strtotime("$refLast -" . ($refWin - 1) . ' days'));
    $refPrevStart = date('Y-m-d', strtotime("$refCurStart -$refWin days"));
    $refHasPrev = $refDates[0] <= $refPrevStart;

    $chCur = $chPrev = $chAll = [];
    $srcAgg = [];   // "channel\thost" => [cur, prev, all, first]
    $landCur = [];  // channel => path => n (current window)
    $weeks = [];    // ISO week => ['days' => n, 'start' => date, channel => n]
    foreach ($refStore as $d => $rec) {
        $inCur = $d >= $refCurStart;
        $inPrev = !$inCur && $d >= $refPrevStart;
        $wk = date('o-\WW', strtotime($d));
        $weeks[$wk]['days'] = ($weeks[$wk]['days'] ?? 0) + 1;
        $weeks[$wk]['start'] = $weeks[$wk]['start'] ?? $d;
        foreach (($rec['channels'] ?? []) as $ch => $n) {
            if ($ch === 'Internal') continue;
            $chAll[$ch] = ($chAll[$ch] ?? 0) + $n;
            if ($inCur)  $chCur[$ch]  = ($chCur[$ch] ?? 0) + $n;
            if ($inPrev) $chPrev[$ch] = ($chPrev[$ch] ?? 0) + $n;
            if (($cc = ref_chart_channel($ch)) !== null) $weeks[$wk][$cc] = ($weeks[$wk][$cc] ?? 0) + $n;
        }
        foreach (($rec['sources'] ?? []) as $ch => $hosts) {
            foreach ($hosts as $host => $n) {
                $k = $ch . "\t" . $host;
                $srcAgg[$k] ??= [0, 0, 0, $d];
                $srcAgg[$k][2] += $n;
                if ($inCur)  $srcAgg[$k][0] += $n;
                if ($inPrev) $srcAgg[$k][1] += $n;
            }
        }
        if ($inCur) {
            foreach (($rec['landing'] ?? []) as $ch => $pages) {
                foreach ($pages as $p => $n) $landCur[$ch][$p] = ($landCur[$ch][$p] ?? 0) + $n;
            }
        }
    }
    arsort($chCur);
    $refCurTotal  = array_sum($chCur);
    $refPrevTotal = array_sum($chPrev);
    $refReferredCur  = $refCurTotal - ($chCur['Direct / no referrer'] ?? 0);
    $refReferredPrev = $refPrevTotal - ($chPrev['Direct / no referrer'] ?? 0);
    $refMaxCh = $chCur ? max($chCur) : 1;
    $refPct = fn(int $cur, int $prev): ?int => $prev > 0 ? (int) round(($cur - $prev) / $prev * 100) : null;

    // Top sources for the current window; "new" = first seen in the last 14 days, once the store is older than that.
    $refNewCutoff = date('Y-m-d', strtotime("$refLast -13 days"));
    $refCanFlagNew = $refDates[0] < $refNewCutoff;
    $refSources = [];
    foreach ($srcAgg as $k => [$cur, $prev, $all, $first]) {
        if ($cur === 0) continue;
        [$ch, $host] = explode("\t", $k, 2);
        $refSources[] = compact('ch', 'host', 'cur', 'prev', 'all', 'first') + ['isNew' => $refCanFlagNew && $first >= $refNewCutoff];
    }
    usort($refSources, fn($a, $b) => [$b['cur'], $b['all']] <=> [$a['cur'], $a['all']]);
    $refSources = array_slice($refSources, 0, 20);

    // Landing pages per referred channel (current window), channels by volume.
    $refLanding = [];
    foreach ($chCur as $ch => $n) {
        if (empty($landCur[$ch])) continue;
        arsort($landCur[$ch]);
        $refLanding[$ch] = array_slice($landCur[$ch], 0, 8, true);
    }
    // Referred channels first in the picker; direct is the least actionable.
    if (isset($refLanding['Direct / no referrer'])) {
        $direct = $refLanding['Direct / no referrer'];
        unset($refLanding['Direct / no referrer']);
        $refLanding['Direct / no referrer'] = $direct;
    }

    // Weekly stacked bars of referred landings (last 26 weeks), direct excluded.
    ksort($weeks);
    $weeks = array_slice($weeks, -26, null, true);
    $refWeekMax = 1;
    foreach ($weeks as $w) {
        $t = 0; foreach ($refChartChannels as $cc => $_) $t += $w[$cc] ?? 0;
        $refWeekMax = max($refWeekMax, $t);
    }
}

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
.mini-panel h2 .ico{width:13px;height:13px;margin-right:2px;align-self:center}
.rank-toolbar .field{flex:1 1 200px;min-width:0;position:relative;display:flex;align-items:center}
.rank-toolbar .field .ico{position:absolute;left:9px;width:13px;height:13px;color:var(--muted);pointer-events:none}
.rank-toolbar .field input[type=search]{flex:1;padding-left:28px}
.rank-toolbar .selwrap{position:relative;display:inline-flex;align-items:center}
.rank-toolbar .selwrap .ico{position:absolute;left:9px;width:12px;height:12px;color:var(--muted);pointer-events:none}
.rank-toolbar .selwrap select{padding-left:26px}
.rank-sort .ico{width:12px;height:12px;margin-right:3px;opacity:.7}
.rank-sort button{display:inline-flex;align-items:center}
.rank-medal{flex:none;width:14px;height:14px;color:var(--gold)}
.rank-row.top2 .rank-medal{color:light-dark(#6b7280,#c4c9d2)}
.rank-row.top3 .rank-medal{color:light-dark(#9a5b2a,#d9a06c)}
@media (max-width:575px){ .rank-medal{display:none} }
.zero-detail summary .ico{width:13px;height:13px;margin-right:4px}
.zero-cat h3 .ico{width:11px;height:11px;margin-right:3px;vertical-align:-.1em}
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

/* Referrers: channel hues are the dataviz reference categorical slots 1-5, in fixed order */
.c1{--c:light-dark(#2a78d6,#3987e5)}.c2{--c:light-dark(#eb6834,#d95926)}.c3{--c:light-dark(#1baf7a,#199e70)}
.c4{--c:light-dark(#eda100,#c98500)}.c5{--c:light-dark(#e87ba4,#d55181)}
.ref-legend{display:flex;flex-wrap:wrap;gap:4px 14px;font-size:12px;color:var(--muted);margin-bottom:10px}
.ref-legend span{display:inline-flex;align-items:center;gap:5px}
.ref-legend i{width:10px;height:10px;border-radius:2px;background:var(--c)}
.ref-chart{display:flex;align-items:stretch;gap:4px;height:150px;padding-bottom:18px;border-bottom:1px solid var(--rule)}
.ref-col{flex:1 1 0;min-width:0;display:flex;flex-direction:column;justify-content:flex-end;position:relative}
.ref-col:hover .ref-stack{filter:brightness(1.08)}
.ref-col.partial .ref-stack{opacity:.7}
.ref-col.partial .ref-x{font-style:italic}
.ref-stack{display:flex;flex-direction:column-reverse;gap:2px;min-height:0;border-radius:4px 4px 0 0;overflow:hidden}
.ref-stack i{display:block;background:var(--c);min-height:2px}
.ref-x{position:absolute;bottom:-18px;left:0;right:0;text-align:center;font-size:10.5px;color:var(--muted);white-space:nowrap;overflow:hidden}
.ref-col:nth-child(even) .ref-x{visibility:hidden}
.src-row{display:grid;grid-template-columns:minmax(0,1fr) auto auto;gap:10px;align-items:baseline;padding:5px 0}
.src-row+.src-row{border-top:1px dashed var(--rule)}
.src-host{min-width:0;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;font-size:13px;color:var(--ink)}
.src-ch{font-size:11px;color:var(--muted);white-space:nowrap}
.src-row .mini-value{font-family:var(--mono);font-size:12px;color:var(--muted);white-space:nowrap;text-align:right}
.src-new{font-size:10px;font-weight:650;text-transform:uppercase;letter-spacing:.05em;color:var(--success);border:1px solid currentColor;border-radius:3px;padding:0 3px;margin-left:4px}
.ref-sel{width:100%;margin-bottom:6px;padding:6px 8px;border:1px solid var(--rule);border-radius:6px;background:var(--surface);color:var(--ink);font:inherit;font-size:13px}
.ref-land-h{font-size:12px;text-transform:uppercase;letter-spacing:.07em;color:var(--muted);margin:10px 0 2px}
.ref-land[hidden]{display:none}
.ref-stackcol{display:flex;flex-direction:column;gap:14px;min-width:0}
.ref-stackcol .mini-panel{height:auto}
@media (max-width:575px){ .src-ch{display:none} .ref-col:nth-child(4n+3) .ref-x{visibility:hidden} }

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
  <div class="note warn"><?php echo chrome_icon('warning'); ?><code>popularity.json</code> is empty or missing. Run <code>python3 fetch-popularity.py</code> to fetch data from Cloudflare.</div>
<?php else: ?>

<div class="stats">
  <div class="stat"><div class="n"><?php echo number_format($rankedCount); ?></div><div class="l"><?php echo chrome_icon('file'); ?>Pages tracked</div></div>
  <div class="stat"><div class="n"><?php echo number_format((int) $maxScore); ?></div><div class="l"><?php echo chrome_icon('star'); ?>Top page score</div></div>
  <div class="stat"><div class="n"><?php echo number_format((int) $totalScore); ?></div><div class="l"><?php echo chrome_icon('chart'); ?>Total score sum</div></div>
  <div class="stat"><div class="n" style="font-size:14px"><?php echo $lastUpdated ? h($lastUpdated) : '—'; ?></div><div class="l"><?php echo chrome_icon('clock'); ?>Last updated</div></div>
  <div class="stat"><div class="n"><?php echo number_format($avgScore, 1); ?></div><div class="l"><?php echo chrome_icon('activity'); ?>Avg score / page</div></div>
  <div class="stat"><div class="n"><?php echo number_format($medianScore, 1); ?></div><div class="l"><?php echo chrome_icon('median'); ?>Median score</div></div>
  <div class="stat"><div class="n"><?php echo $top3Share; ?>&thinsp;%</div><div class="l"><?php echo chrome_icon('pie'); ?>Top 3 share of views</div></div>
  <div class="stat"><div class="n"><?php echo number_format($risingStarCount); ?></div><div class="l"><?php echo chrome_icon('rising'); ?>Rising stars (&le;30d)</div></div>
  <div class="stat"><div class="n"><?php echo number_format($totalDailyViews); ?></div><div class="l"><?php echo chrome_icon('eye'); ?>Views yesterday</div></div>
  <div class="stat"><div class="n"><?php echo number_format($totalViewsAllTime); ?></div><div class="l"><?php echo chrome_icon('layers'); ?>All-time views tracked</div></div>
  <div class="stat"><div class="n"><?php echo $top10Share; ?>&thinsp;%</div><div class="l"><?php echo chrome_icon('list'); ?>Top 10 share of views</div></div>
  <div class="stat"><div class="n"><?php echo number_format($untrackedCount); ?> <span style="color:var(--muted);font-size:.85em">/ <?php echo number_format($totalPageCount); ?></span></div><div class="l"><?php echo chrome_icon('eye-off'); ?>Pages with zero views</div></div>
</div>

<div class="note" style="margin-bottom:22px">
  <?php echo chrome_icon('info'); ?>Each day's raw view count is added to the score after multiplying existing values by <strong>29/30</strong>.
  After 30 days a single visit contributes ~37&nbsp;% of its original weight, so this reflects
  <em>consistently popular</em> pages — not one-day spikes. Scores reset to zero over ~3 months of inactivity.
  "All-time views tracked" accumulates from the day this counter was added and does not include views from before then.
</div>

<?php if ($historyDays > 1): ?>
<div class="mini-panel" style="margin-bottom:22px">
  <h2><?php echo chrome_icon('activity'); ?>Site-wide traffic <span class="age">(<?php echo h($historySpanLabel); ?> · <?php echo number_format($historyTotal); ?> views)</span></h2>
  <svg viewBox="0 0 <?php echo $sparkWidth; ?> <?php echo $sparkHeight; ?>" preserveAspectRatio="none" style="width:100%;height:60px;display:block" role="img" aria-label="Daily site-wide view count over the last <?php echo $historyDays; ?> days">
    <polyline points="<?php echo h($sparkPoints); ?>" fill="none" stroke="var(--accent)" stroke-width="1.6" vector-effect="non-scaling-stroke" stroke-linejoin="round" />
  </svg>
</div>
<?php endif; ?>

<?php if ($refReady): ?>
<p class="lbl sectlbl"><?php echo chrome_icon('link'); ?>Where readers come from</p>
<div class="note" style="margin-bottom:14px">
  <?php echo chrome_icon('info'); ?>Human page landings from the origin nginx logs (bots, scrapers, and IPs with over 40 pages a day filtered out; one hit per reader, page, and hour), stored daily since <strong><?php echo h(date('M j, Y', strtotime($refDates[0]))); ?></strong> (<?php echo number_format($refDayCount); ?> day<?php echo $refDayCount === 1 ? '' : 's'; ?>, through <?php echo h(date('M j', strtotime($refLast))); ?>).
  Search counts here run above Search Console clicks; take search volume from GSC. "Direct" also covers bookmarks, apps that strip the referrer, and bots with browser-like user agents.
  Comparisons are the last <?php echo $refWin; ?> days against the <?php echo $refWin; ?> before<?php echo $refHasPrev ? '' : ' (partial: history is still shorter than two windows)'; ?>.
</div>
<?php $refDelta = $refPct($refReferredCur, $refReferredPrev); ?>
<div class="stats" style="margin-bottom:14px">
  <div class="stat"><div class="n"><?php echo number_format($refCurTotal); ?></div><div class="l"><?php echo chrome_icon('eye'); ?>External landings (<?php echo $refWin; ?>d)</div></div>
  <div class="stat"><div class="n"><?php echo number_format($refReferredCur); ?><?php if ($refDelta !== null): ?> <span class="mv-pct <?php echo $refDelta >= 0 ? 'up' : 'down'; ?>" style="font-size:.6em"><?php echo ($refDelta > 0 ? '+' : '') . $refDelta; ?>&thinsp;%</span><?php endif; ?></div><div class="l"><?php echo chrome_icon('link'); ?>Referred landings (<?php echo $refWin; ?>d)</div></div>
  <div class="stat"><div class="n"><?php echo number_format($chCur['Search engine'] ?? 0); ?></div><div class="l"><?php echo chrome_icon('search'); ?>From search (<?php echo $refWin; ?>d)</div></div>
  <div class="stat"><div class="n"><?php echo number_format($chCur['AI assistant'] ?? 0); ?></div><div class="l"><?php echo chrome_icon('sparkles'); ?>From AI assistants (<?php echo $refWin; ?>d)</div></div>
</div>

<div class="mini-panel" style="margin-bottom:14px">
  <h2><?php echo chrome_icon('bars'); ?>Referred landings per week <span class="age">(direct / no-referrer excluded; lighter bars with italic dates are partial weeks)</span></h2>
  <div class="ref-legend">
    <?php foreach ($refChartChannels as $cc => $cls): ?><span><i class="<?php echo $cls; ?>"></i><?php echo h($cc); ?></span><?php endforeach; ?>
  </div>
  <div class="ref-chart" role="img" aria-label="Weekly referred landings by channel, <?php echo count($weeks); ?> weeks">
    <?php foreach ($weeks as $wk => $w):
      $t = 0; foreach ($refChartChannels as $cc => $_) $t += $w[$cc] ?? 0;
      $tip = date('M j', strtotime($w['start'])) . ' week' . ($w['days'] < 7 ? ' (partial, ' . $w['days'] . 'd)' : '') . ': ' . number_format($t) . ' referred';
      foreach ($refChartChannels as $cc => $_) if (!empty($w[$cc])) $tip .= "\n" . $cc . ': ' . number_format($w[$cc]);
    ?>
    <div class="ref-col<?php echo $w['days'] < 7 ? ' partial' : ''; ?>" title="<?php echo h($tip); ?>">
      <div class="ref-stack" style="height:<?php echo round($t / $refWeekMax * 100, 2); ?>%">
        <?php foreach ($refChartChannels as $cc => $cls): if (empty($w[$cc])) continue; ?>
          <i class="<?php echo $cls; ?>" style="flex-grow:<?php echo (int) $w[$cc]; ?>"></i>
        <?php endforeach; ?>
      </div>
      <span class="ref-x"><?php echo h(date('M j', strtotime($w['start']))); ?></span>
    </div>
    <?php endforeach; ?>
  </div>
</div>

<div class="panels-2">
  <div class="ref-stackcol">
  <div class="mini-panel">
    <h2><?php echo chrome_icon('pie'); ?>Channel mix <span class="age">(last <?php echo $refWin; ?>d, change vs. prior <?php echo $refWin; ?>d)</span></h2>
    <?php foreach ($chCur as $ch => $n): $p = $refPct($n, $chPrev[$ch] ?? 0); ?>
    <div class="mini-row">
      <span class="mini-label"><?php echo h($ch); ?></span>
      <span class="mini-value"><?php echo number_format($n); ?> · <?php echo $refCurTotal ? round($n / $refCurTotal * 100, 1) : 0; ?>&thinsp;%<?php if ($refHasPrev && $p !== null): ?> · <span class="mv-pct <?php echo $p >= 0 ? 'up' : 'down'; ?>"><?php echo ($p > 0 ? '+' : '') . $p; ?>&thinsp;%</span><?php endif; ?></span>
      <div class="mini-bar"><i style="width:<?php echo round($n / $refMaxCh * 100, 1); ?>%"></i></div>
    </div>
    <?php endforeach; ?>
  </div>

  <div class="mini-panel">
    <h2><?php echo chrome_icon('signpost'); ?>Landing pages by channel <span class="age">(last <?php echo $refWin; ?>d)</span></h2>
    <select id="refLandSel" class="ref-sel" aria-label="Channel" hidden>
      <?php foreach ($refLanding as $ch => $_): ?><option><?php echo h($ch); ?></option><?php endforeach; ?>
    </select>
    <?php foreach ($refLanding as $ch => $pages): $mx = max($pages); ?>
    <div class="ref-land" data-ch="<?php echo h($ch); ?>">
      <h3 class="ref-land-h"><?php echo h($ch); ?></h3>
      <?php foreach ($pages as $p => $n): ?>
      <div class="mini-row">
        <a class="mini-label" href="<?php echo h($p === '/' ? './' : ltrim($p, '/')); ?>" target="_blank" title="<?php echo h($p); ?>"><?php echo h(ref_page_label($p, $metaCache)); ?></a>
        <span class="mini-value"><?php echo number_format($n); ?></span>
        <div class="mini-bar"><i style="width:<?php echo round($n / $mx * 100, 1); ?>%"></i></div>
      </div>
      <?php endforeach; ?>
    </div>
    <?php endforeach; ?>
  </div>
  </div>

  <div class="mini-panel">
    <h2><?php echo chrome_icon('external'); ?>Top sources <span class="age">(last <?php echo $refWin; ?>d · all-time)</span></h2>
    <?php if (empty($refSources)): ?>
      <p class="mini-empty">No referred landings in this window.</p>
    <?php else: foreach ($refSources as $s): ?>
      <div class="src-row">
        <span class="src-host" title="<?php echo h($s['ch'] . ' · first seen ' . $s['first']); ?>"><?php echo h($s['host']); ?><?php if ($s['isNew']): ?> <span class="src-new">new</span><?php endif; ?></span>
        <span class="src-ch"><?php echo h($s['ch']); ?></span>
        <span class="mini-value"><?php echo number_format($s['cur']); ?> · <?php echo number_format($s['all']); ?></span>
      </div>
    <?php endforeach; endif; ?>
  </div>

</div>
<?php endif; ?>

<div class="panels">
  <div class="mini-panel">
    <h2><?php echo chrome_icon('rising'); ?>Rising stars <span class="age">(published &le;30d ago)</span></h2>
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
    <h2><?php echo chrome_icon('bars'); ?>Score distribution</h2>
    <?php foreach ($buckets as $b): $w = round($b['count'] / $maxBucketCount * 100, 1); ?>
    <div class="dist-row">
      <span class="dl"><?php echo h($b['label']); ?></span>
      <div class="dist-track"><div class="dist-fill" style="width:<?php echo $w; ?>%"></div></div>
      <span class="dc"><?php echo $b['count']; ?></span>
    </div>
    <?php endforeach; ?>
  </div>

  <div class="mini-panel">
    <h2><?php echo chrome_icon('clock'); ?>Last 24 hours</h2>
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
    <h2><?php echo chrome_icon('tag'); ?>By category</h2>
    <?php foreach ($categoryRows as $cr): $w = round($cr['score'] / $maxCategoryScore * 100, 1); ?>
    <div class="dist-row" style="grid-template-columns:9rem 1fr 2.8rem">
      <span class="dl" style="white-space:nowrap;overflow:hidden;text-overflow:ellipsis" title="<?php echo h($cr['category']); ?>"><?php echo h($cr['category']); ?></span>
      <div class="dist-track"><div class="dist-fill" style="width:<?php echo $w; ?>%"></div></div>
      <span class="dc"><?php echo $cr['pct']; ?>&thinsp;%</span>
    </div>
    <?php endforeach; ?>
  </div>

  <div class="mini-panel">
    <h2><?php echo chrome_icon('bolt'); ?>Trending now <span class="age">(today's views vs. accumulated score)</span></h2>
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
    <h2><?php echo chrome_icon('alert'); ?>Needs attention <span class="age">(popular, ≥<?php echo $staleCutoffDays; ?>d since fact review)</span></h2>
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
    <h2><?php echo chrome_icon('rising'); ?>Momentum <span class="age">(last 7 days vs. the 7 before)</span></h2>
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
  <summary><?php echo chrome_icon('eye-off'); ?><?php echo number_format($untrackedCount); ?> page<?php echo $untrackedCount === 1 ? '' : 's'; ?> with zero recorded views — show which ones, by category</summary>
  <?php foreach ($untrackedByCategory as $cat => $pages): ?>
    <div class="zero-cat">
      <h3><?php echo chrome_icon('tag'); ?><?php echo h($cat); ?> (<?php echo count($pages); ?>)</h3>
      <div class="zero-list">
        <?php foreach ($pages as $p): ?>
          <a href="<?php echo h($p['filename']); ?>" target="_blank"><?php echo h($p['title']); ?></a>
        <?php endforeach; ?>
      </div>
    </div>
  <?php endforeach; ?>
</details>
<?php endif; ?>

<p class="lbl sectlbl"><?php echo chrome_icon('trophy'); ?>Ranked by decayed 30-day score</p>
<div class="rank-toolbar">
  <span class="field"><?php echo chrome_icon('search'); ?><input type="search" id="rankSearch" placeholder="Filter by title&hellip;" aria-label="Filter ranked list by title" autocomplete="off" spellcheck="false"></span>
  <span class="selwrap"><?php echo chrome_icon('funnel'); ?><select id="rankCategory" aria-label="Filter by category">
    <option value="">All categories</option>
    <?php foreach (array_keys($categoryTotals) as $cat): ?>
      <option value="<?php echo h($cat); ?>"><?php echo h($cat); ?></option>
    <?php endforeach; ?>
  </select></span>
  <div class="rank-sort" role="group" aria-label="Sort ranked list">
    <button type="button" data-sort="score" class="cur"><?php echo chrome_icon('star'); ?>Score</button>
    <button type="button" data-sort="views"><?php echo chrome_icon('eye'); ?>All-time views</button>
    <button type="button" data-sort="title"><?php echo chrome_icon('sort'); ?>Title A&ndash;Z</button>
  </div>
</div>
<div class="list-card" role="list" id="rankList">
  <?php foreach ($rows as $row): $medal = $row['rank'] <= 3 ? ' top' . $row['rank'] : ''; ?>
  <div class="rank-row<?php echo $medal; ?>" role="listitem"
       data-title="<?php echo h(mb_strtolower($row['title'])); ?>" data-category="<?php echo h($row['category']); ?>"
       data-score="<?php echo $row['score']; ?>" data-views="<?php echo $row['views']; ?>">
    <div class="rank-num" aria-label="Rank <?php echo $row['rank']; ?>"><?php echo $row['rank']; ?></div>
    <?php if ($medal !== ''): ?><?php echo chrome_icon('award', 'rank-medal'); ?><?php endif; ?>
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
  <p class="rank-empty" id="rankEmpty" hidden><?php echo chrome_icon('inbox'); ?> No pages match that filter.</p>
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

  var refSel = document.getElementById('refLandSel');
  if (refSel) {
    var lands = Array.prototype.slice.call(document.querySelectorAll('.ref-land'));
    var showLand = function(){
      lands.forEach(function(l){ l.hidden = l.dataset.ch !== refSel.value; });
    };
    refSel.hidden = false;
    document.querySelectorAll('.ref-land-h').forEach(function(el){ el.hidden = true; });
    refSel.addEventListener('change', showLand);
    showLand();
  }

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

