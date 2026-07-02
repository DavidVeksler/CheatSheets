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
$cacheFile = __DIR__ . '/.metadata-cache.json';

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

/* ---------- Load metadata cache for proper titles ---------- */
$metaCache = [];
if (is_readable($cacheFile)) {
    $raw = @file_get_contents($cacheFile);
    if ($raw !== false) {
        $decoded = json_decode($raw, true);
        if (is_array($decoded)) $metaCache = $decoded;
    }
}

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
$top3Share = $totalScore > 0 ? round(array_sum(array_slice($scoreVals, 0, 3)) / $totalScore * 100, 1) : 0;

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
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="color-scheme" content="light dark">
    <link rel="icon" href="data:image/svg+xml,<svg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 100 100%22><text y=%22.9em%22 font-size=%2290%22>📊</text></svg>">

    <title>Popularity · David Veksler's Cheatsheets</title>
    <meta name="description" content="30-day trending view counts for every cheatsheet, pulled nightly from Cloudflare Analytics.">
    <meta name="robots" content="noindex, follow">

    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.8/dist/css/bootstrap.min.css" rel="stylesheet" integrity="sha384-sRIl4kxILFvY47J16cr9ZwB07vP4J8+LH7qKQnuqkuIAvNWLzeN8tE5YBujZqJLB" crossorigin="anonymous">
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.13.1/font/bootstrap-icons.min.css" integrity="sha384-CK2SzKma4jA5H/MXDUU7i1TqZlCFaD4T01vtyDFvPlD97JQyS+IsSh1nI2EFbpyk" crossorigin="anonymous">

    <style>
      @layer site {
        :root {
          color-scheme: light dark;
          --bg:        light-dark(#f0f2f5, #14171c);
          --surface:   light-dark(#ffffff, #1d2128);
          --surface-2: light-dark(#f6f8fa, #161a20);
          --border:    light-dark(#dee2e6, #303642);
          --text:      light-dark(#1a1f27, #e7eaf0);
          --muted:     light-dark(#5a6472, #9aa4b2);
          --accent:    light-dark(#1a508b, #6ea8ff);
          --accent-bg: light-dark(#e7f0fb, #1a2330);
          --bar-track: light-dark(#e9ecef, #2a2f3a);
          --bar-fill:  light-dark(#4f46e5, #818cf8);
          --gold:      #f59e0b;
          --silver:    light-dark(#6b7280, #9ca3af);
          --bronze:    #b45309;
          --top3-bg:   light-dark(#fffbeb, #1c1a0f);
        }
        .navbar { background: light-dark(#2c3034, #0f1216); }
        .navbar-brand, .navbar .nav-link { color: #f1f3f5 !important; }

        /* ---- stat boxes ---- */
        .stat-box {
          background: var(--surface); border: 1px solid var(--border);
          border-radius: .5rem; padding: 1rem 1.2rem; height: 100%;
        }
        .stat-box .num { font-size: 1.7rem; font-weight: 700; line-height: 1.1; }
        .stat-box .lbl { color: var(--muted); font-size: .78rem; text-transform: uppercase; letter-spacing: .05em; margin-top: .15rem; }

        /* ---- mini panels (rising stars / distribution / referrers) ---- */
        .mini-panel {
          background: var(--surface); border: 1px solid var(--border);
          border-radius: .5rem; padding: 1rem 1.1rem; height: 100%;
        }
        .mini-panel h2 {
          font-size: .95rem; font-weight: 700; margin-bottom: .8rem;
          display: flex; align-items: center; gap: .4rem;
        }
        .mini-row {
          display: grid;
          grid-template-columns: 1.3rem 1fr auto;
          gap: .5rem; align-items: center;
          padding: .4rem 0;
        }
        .mini-row + .mini-row { border-top: 1px dashed var(--border); }
        .mini-row .mini-icon { color: var(--muted); text-align: center; }
        .mini-row .mini-label {
          min-width: 0; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
          font-size: .88rem; text-decoration: none; color: var(--text);
        }
        .mini-row a.mini-label:hover { color: var(--accent); }
        .mini-row .mini-value {
          font-size: .82rem; font-variant-numeric: tabular-nums; color: var(--muted);
          white-space: nowrap;
        }
        .mini-bar-track {
          grid-column: 2 / 4; height: 5px; border-radius: 3px;
          background: var(--bar-track); margin-top: .3rem; overflow: hidden;
        }
        .mini-bar-fill { height: 100%; border-radius: 3px; background: var(--bar-fill); width: var(--bar-w, 0%); }
        .mini-empty { color: var(--muted); font-size: .85rem; font-style: italic; }
        .mini-age { color: var(--muted); font-size: .76rem; }

        /* ---- score distribution ---- */
        .dist-row { display: grid; grid-template-columns: 3.4rem 1fr 1.6rem; gap: .6rem; align-items: center; padding: .35rem 0; }
        .dist-row .dist-label { font-size: .8rem; color: var(--muted); font-variant-numeric: tabular-nums; }
        .dist-row .dist-count { font-size: .8rem; text-align: right; font-variant-numeric: tabular-nums; }
        .dist-track { height: 10px; border-radius: 3px; background: var(--bar-track); overflow: hidden; }
        .dist-fill  { height: 100%; border-radius: 3px; background: var(--bar-fill); width: var(--bar-w, 0%); }

        /* ---- ranked list ---- */
        .rank-list {
          background: var(--surface); border: 1px solid var(--border);
          border-radius: .5rem; overflow: hidden;
        }
        .rank-row {
          display: grid;
          grid-template-columns: 2.4rem 1fr auto;
          gap: .25rem 1rem;
          padding: .8rem 1.1rem;
          border-bottom: 1px solid var(--border);
          align-items: center;
        }
        .rank-row:last-child { border-bottom: 0; }
        .rank-row.top-3 { background: var(--top3-bg); }
        .rank-row:not(.top-3):hover { background: var(--surface-2); }

        /* rank number pill */
        .rank-num {
          font-weight: 700; font-size: .95rem; text-align: center;
          width: 2rem; height: 2rem; line-height: 2rem;
          border-radius: 50%; flex-shrink: 0;
          background: var(--accent-bg); color: var(--accent);
        }
        .rank-num.gold   { background: #fef3c7; color: var(--gold);   }
        .rank-num.silver { background: #f3f4f6; color: var(--silver); }
        .rank-num.bronze { background: #fef3c7; color: var(--bronze); }

        /* title + bar area */
        .rank-info { min-width: 0; }
        .rank-title {
          font-weight: 600; white-space: nowrap; overflow: hidden;
          text-overflow: ellipsis; text-decoration: none; color: var(--text);
          font-size: .95rem;
        }
        .rank-title:hover { color: var(--accent); }
        .rank-bar-track {
          height: 6px; border-radius: 3px;
          background: var(--bar-track); margin-top: .4rem; overflow: hidden;
        }
        .rank-bar-fill {
          height: 100%; border-radius: 3px;
          background: var(--bar-fill);
          width: var(--bar-w, 0%);
          transition: width .4s ease;
        }
        .rank-row.top-3 .rank-bar-fill { background: var(--gold); }

        /* score + pct column */
        .rank-score { text-align: right; white-space: nowrap; }
        .rank-score .score-val { font-weight: 700; font-size: 1rem; font-variant-numeric: tabular-nums; }
        .rank-score .score-pct { color: var(--muted); font-size: .78rem; }

        .muted { color: var(--muted); }
        footer.site { color: var(--muted); border-top: 1px solid var(--border); }
        #themeToggle { background: transparent; border: 0; color: #f1f3f5; font-size: 1.15rem; cursor: pointer; }
        :focus-visible { outline: 2px solid var(--accent); outline-offset: 2px; }

        .callout {
          background: var(--accent-bg); border-left: 3px solid var(--accent);
          border-radius: 0 .4rem .4rem 0; padding: .75rem 1rem;
          font-size: .88rem; color: var(--muted);
        }

        @media (prefers-reduced-motion: no-preference) {
          .rank-row { transition: background .1s ease; }
        }
        @media (max-width: 575px) {
          .rank-row { grid-template-columns: 2rem 1fr; }
          .rank-score { display: none; }
        }
      }
      [data-theme="light"] { color-scheme: light; }
      [data-theme="dark"]  { color-scheme: dark; }

      /* Unlayered on purpose: @layer rules always lose to Bootstrap's unlayered
         CSS regardless of source order, so body/link overrides must live outside
         @layer site to actually beat bootstrap.min.css's body/a rules. */
      body {
        background: var(--bg); color: var(--text);
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        min-height: 100vh;
      }
      a { color: var(--accent); }
      a:hover { color: var(--accent); }
    </style>
</head>
<body>
    <nav class="navbar navbar-expand-lg sticky-top shadow-sm">
        <div class="container">
            <a class="navbar-brand fw-semibold" href="index.php"><i class="bi bi-journal-richtext me-2"></i>David Veksler's Cheatsheet Portfolio</a>
            <div class="d-flex align-items-center gap-3">
                <a class="nav-link d-none d-sm-inline" href="how-its-built.html"><i class="bi bi-gear-wide-connected me-1"></i>How it's built</a>
                <a class="nav-link d-none d-sm-inline" href="history.php"><i class="bi bi-clock-history me-1"></i>Change History</a>
                <button id="themeToggle" type="button" aria-label="Toggle colour theme" title="Toggle theme"><i class="bi bi-circle-half"></i></button>
            </div>
        </div>
    </nav>

    <main class="container py-4">

        <header class="mb-4">
            <h1 class="h3 mb-1"><i class="bi bi-bar-chart-fill me-2"></i>Popularity</h1>
            <p class="muted mb-0">
                30-day trending scores pulled nightly from Cloudflare Analytics.
                <?php if ($lastUpdated): ?>
                    Last updated <strong><?php echo h($lastUpdated); ?></strong>
                    <span class="muted">(<?php echo rel_time($lastUpdated); ?>)</span>.
                <?php else: ?>
                    No data yet — run <code>fetch-popularity.py</code> to seed.
                <?php endif; ?>
            </p>
        </header>

        <?php if ($rankedCount === 0): ?>
            <div class="alert alert-warning">
                <i class="bi bi-exclamation-triangle me-2"></i>
                <code>popularity.json</code> is empty or missing.
                Run <code>python3 fetch-popularity.py</code> to fetch data from Cloudflare.
            </div>
        <?php else: ?>

        <!-- Stat boxes -->
        <div class="row g-3 mb-4">
            <div class="col-6 col-md-3">
                <div class="stat-box">
                    <div class="num"><?php echo number_format($rankedCount); ?></div>
                    <div class="lbl">Pages tracked</div>
                </div>
            </div>
            <div class="col-6 col-md-3">
                <div class="stat-box">
                    <div class="num"><?php echo number_format((int) $maxScore); ?></div>
                    <div class="lbl">Top page score</div>
                </div>
            </div>
            <div class="col-6 col-md-3">
                <div class="stat-box">
                    <div class="num"><?php echo number_format((int) $totalScore); ?></div>
                    <div class="lbl">Total score sum</div>
                </div>
            </div>
            <div class="col-6 col-md-3">
                <div class="stat-box">
                    <div class="num" style="font-size:1.1rem;"><?php echo $lastUpdated ? h($lastUpdated) : '—'; ?></div>
                    <div class="lbl">Last updated</div>
                </div>
            </div>
            <div class="col-6 col-md-3">
                <div class="stat-box">
                    <div class="num"><?php echo number_format($avgScore, 1); ?></div>
                    <div class="lbl">Avg score / page</div>
                </div>
            </div>
            <div class="col-6 col-md-3">
                <div class="stat-box">
                    <div class="num"><?php echo number_format($medianScore, 1); ?></div>
                    <div class="lbl">Median score</div>
                </div>
            </div>
            <div class="col-6 col-md-3">
                <div class="stat-box">
                    <div class="num"><?php echo $top3Share; ?>&thinsp;%</div>
                    <div class="lbl">Top 3 share of views</div>
                </div>
            </div>
            <div class="col-6 col-md-3">
                <div class="stat-box">
                    <div class="num"><?php echo number_format($risingStarCount); ?></div>
                    <div class="lbl">Rising stars (&le;30d old)</div>
                </div>
            </div>
        </div>

        <!-- Explanation callout -->
        <div class="callout mb-4">
            <i class="bi bi-info-circle me-1"></i>
            Each day's raw view count is added to the score after multiplying existing values by <strong>29/30</strong>.
            After 30 days a single visit contributes ~37 % of its original weight, so this reflects
            <em>consistently popular</em> pages — not one-day spikes. Scores reset to zero over ~3 months of inactivity.
        </div>

        <!-- Rising stars / Score distribution / Top referrers -->
        <div class="row g-3 mb-4">
            <div class="col-12 col-lg-4">
                <div class="mini-panel">
                    <h2><i class="bi bi-rocket-takeoff-fill"></i>Rising Stars <span class="mini-age">(published &le;30d ago)</span></h2>
                    <?php if (empty($risingStars)): ?>
                        <p class="mini-empty mb-0">No pages published in the last 30 days.</p>
                    <?php else: ?>
                        <?php foreach ($risingStars as $star): ?>
                        <div class="mini-row">
                            <span class="mini-icon"><i class="bi bi-star-fill"></i></span>
                            <a class="mini-label" href="<?php echo h($star['filename']); ?>" target="_blank" rel="noopener" title="<?php echo h($star['title']); ?>">
                                <?php echo h($star['title']); ?>
                            </a>
                            <span class="mini-value"><?php echo number_format($star['score'], 0); ?></span>
                            <div class="mini-age" style="grid-column: 2 / 4;">published <?php echo rel_time(date('c', $star['ctime'])); ?></div>
                        </div>
                        <?php endforeach; ?>
                    <?php endif; ?>
                </div>
            </div>

            <div class="col-12 col-lg-4">
                <div class="mini-panel">
                    <h2><i class="bi bi-bar-chart-steps"></i>Score Distribution</h2>
                    <?php foreach ($buckets as $b): $w = round($b['count'] / $maxBucketCount * 100, 1); ?>
                    <div class="dist-row">
                        <span class="dist-label"><?php echo h($b['label']); ?></span>
                        <div class="dist-track"><div class="dist-fill" style="--bar-w: <?php echo $w; ?>%"></div></div>
                        <span class="dist-count"><?php echo $b['count']; ?></span>
                    </div>
                    <?php endforeach; ?>
                </div>
            </div>

            <div class="col-12 col-lg-4">
                <div class="mini-panel">
                    <h2><i class="bi bi-clock-history"></i>Last 24 Hours</h2>
                    <?php if (empty($dailyRows)): ?>
                        <p class="mini-empty mb-0">No daily view data yet — populated by the next nightly run.</p>
                    <?php else: ?>
                        <?php foreach ($dailyRows as $day): ?>
                        <div class="mini-row">
                            <span class="mini-icon"><i class="bi bi-eye-fill"></i></span>
                            <a class="mini-label" href="<?php echo h($day['filename']); ?>" target="_blank" rel="noopener" title="<?php echo h($day['title']); ?>">
                                <?php echo h($day['title']); ?>
                            </a>
                            <span class="mini-value"><?php echo number_format($day['count']); ?></span>
                        </div>
                        <?php endforeach; ?>
                    <?php endif; ?>
                </div>
            </div>
        </div>

        <!-- Ranked list -->
        <div class="rank-list" role="list">
            <?php foreach ($rows as $row):
                $rankClass = match ($row['rank']) {
                    1 => 'gold',
                    2 => 'silver',
                    3 => 'bronze',
                    default => '',
                };
                $rowClass = $row['rank'] <= 3 ? 'top-3' : '';
            ?>
            <div class="rank-row <?php echo $rowClass; ?>" role="listitem">
                <!-- Rank pill -->
                <div class="rank-num <?php echo $rankClass; ?>" aria-label="Rank <?php echo $row['rank']; ?>">
                    <?php if ($row['rank'] === 1): ?>
                        <i class="bi bi-trophy-fill" title="1st"></i>
                    <?php elseif ($row['rank'] === 2): ?>
                        <i class="bi bi-award-fill" title="2nd"></i>
                    <?php elseif ($row['rank'] === 3): ?>
                        <i class="bi bi-award" title="3rd"></i>
                    <?php else: ?>
                        <?php echo $row['rank']; ?>
                    <?php endif; ?>
                </div>

                <!-- Title + bar -->
                <div class="rank-info">
                    <a class="rank-title" href="<?php echo h($row['filename']); ?>" target="_blank" rel="noopener"
                       title="<?php echo h($row['filename']); ?>">
                        <?php echo h($row['title']); ?>
                    </a>
                    <div class="rank-bar-track" aria-hidden="true">
                        <div class="rank-bar-fill" style="--bar-w: <?php echo $row['bar']; ?>%"></div>
                    </div>
                </div>

                <!-- Score + share -->
                <div class="rank-score">
                    <div class="score-val"><?php echo number_format($row['score'], 0); ?></div>
                    <div class="score-pct"><?php echo $row['pct']; ?>&thinsp;%</div>
                </div>
            </div>
            <?php endforeach; ?>
        </div>

        <?php endif; ?>
    </main>

    <footer class="site py-4 mt-5">
        <div class="container text-center small">
            <a href="index.php"><i class="bi bi-collection-fill me-1"></i>All cheatsheets</a>
            <span class="mx-2">·</span>
            <a href="history.php"><i class="bi bi-clock-history me-1"></i>Change history</a>
            <span class="mx-2">·</span>
            Scores decay 1/30 per day · updated nightly via GitHub Actions
            <span class="mx-2">·</span>
            © <?php echo date('Y'); ?> David Veksler
        </div>
    </footer>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.8/dist/js/bootstrap.bundle.min.js" integrity="sha384-FKyoEForCGlyvwx9Hj09JcYn3nv7wiPVlz7YYwJrWVcXK/BmnVDxM+D2scQbITxI" crossorigin="anonymous" defer></script>
    <script>
      (function () {
        const KEY  = 'cheatsheet-theme';
        const root = document.documentElement;
        const saved = (function () { try { return localStorage.getItem(KEY); } catch (e) { return null; } })();
        if (saved === 'light' || saved === 'dark') root.setAttribute('data-theme', saved);
        document.addEventListener('DOMContentLoaded', function () {
          const btn = document.getElementById('themeToggle');
          if (!btn) return;
          btn.addEventListener('click', function () {
            const cur  = root.getAttribute('data-theme')
              || (window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light');
            const next = cur === 'dark' ? 'light' : 'dark';
            root.setAttribute('data-theme', next);
            try { localStorage.setItem(KEY, next); } catch (e) {}
          });
        });
      })();
    </script>
</body>
</html>
