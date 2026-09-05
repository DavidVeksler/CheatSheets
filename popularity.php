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
// Mirrors index.php's own $excludedItems — the one other place that decides what counts as a real cheatsheet.
$excludedFromCoverage = ['etz-chaim-tree-of-life.html'];
$allHtmlFiles = array_filter(glob(__DIR__ . '/*.html') ?: [], fn($p) => is_file($p));
$allHtmlNames = array_map('basename', $allHtmlFiles);
$allHtmlNames = array_values(array_diff($allHtmlNames, $excludedFromCoverage));
$totalPageCount = count($allHtmlNames);
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
$dailyViewsRaw = $popData['dailyViews'] ?? [];
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

/* ---------- Build ranked rows ---------- */
$rows = [];
$rank = 0;
foreach ($scores as $filename => $score) {
    $rank++;
    $title = $metaCache[$filename]['title'] ?? filename_to_title($filename);
    $pct   = $totalScore > 0 ? round($score / $totalScore * 100, 1) : 0;
    $bar   = $maxScore > 0   ? round($score / $maxScore * 100, 2) : 0;
    $rows[] = compact('rank', 'filename', 'title', 'score', 'pct', 'bar');
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
$dailyViews = $popData['dailyViews'] ?? [];
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
    <a href="https://stats.davidveksler.com/" target="_blank" rel="noopener">Full analytics →</a>
  </p>
</section>

<?php if ($rankedCount === 0): ?>
  <div class="note warn"><code>popularity.json</code> is empty or missing. Run <code>python3 fetch-popularity.py</code> to fetch data from Cloudflare.</div>
<?php else: ?>

<div class="stats">
  <div class="stat"><div class="n"><?php echo number_format($rankedCount); ?></div><div class="l">Pages tracked</div></div>
  <div class="stat"><div class="n"><?php echo number_format((int) $maxScore); ?></div><div class="l">Top page score</div></div>
  <div class="stat"><div class="n"><?php echo number_format((int) $totalScore); ?></div><div class="l">Total score sum</div></div>
  <div class="stat"><div class="n" style="font-size:14px"><?php echo $lastUpdated ? h($lastUpdated) : '—'; ?></div><div class="l">Last updated</div></div>
  <div class="stat"><div class="n"><?php echo number_format($avgScore, 1); ?></div><div class="l">Avg score / page</div></div>
  <div class="stat"><div class="n"><?php echo number_format($medianScore, 1); ?></div><div class="l">Median score</div></div>
  <div class="stat"><div class="n"><?php echo $top3Share; ?>&thinsp;%</div><div class="l">Top 3 share of views</div></div>
  <div class="stat"><div class="n"><?php echo number_format($risingStarCount); ?></div><div class="l">Rising stars (&le;30d)</div></div>
  <div class="stat"><div class="n"><?php echo number_format($totalDailyViews); ?></div><div class="l">Views yesterday</div></div>
  <div class="stat"><div class="n"><?php echo number_format($totalViewsAllTime); ?></div><div class="l">All-time views tracked</div></div>
  <div class="stat"><div class="n"><?php echo $top10Share; ?>&thinsp;%</div><div class="l">Top 10 share of views</div></div>
  <div class="stat"><div class="n"><?php echo number_format($untrackedCount); ?> <span style="color:var(--muted);font-size:.85em">/ <?php echo number_format($totalPageCount); ?></span></div><div class="l">Pages with zero views</div></div>
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
</div>

<p class="lbl sectlbl">Ranked by decayed 30-day score</p>
<div class="list-card" role="list">
  <?php foreach ($rows as $row): $isTop1 = $row['rank'] === 1; ?>
  <div class="rank-row<?php echo $isTop1 ? ' top1' : ''; ?>" role="listitem">
    <div class="rank-num" aria-label="Rank <?php echo $row['rank']; ?>"><?php echo $row['rank']; ?></div>
    <div class="rank-info">
      <a class="rank-title" href="<?php echo h($row['filename']); ?>" target="_blank" title="<?php echo h($row['filename']); ?>"><?php echo h($row['title']); ?></a>
      <div class="rank-bar-track" aria-hidden="true"><div class="rank-bar-fill" style="width:<?php echo $row['bar']; ?>%"></div></div>
    </div>
    <div class="rank-score">
      <div class="val num"><?php echo number_format($row['score'], 0); ?></div>
      <div class="pct"><?php echo $row['pct']; ?>&thinsp;%</div>
    </div>
  </div>
  <?php endforeach; ?>
</div>

<?php endif; ?>
</div>
<?php chrome_close(); ?>

