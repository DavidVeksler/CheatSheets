<?php
/**
 * history.php — Browse the git history of this cheatsheet collection.
 *
 * Three views, all driven by read-only git plumbing:
 *   - list   (default)         : paginated commit log, with message/author search
 *   - commit (?commit=<hash>)  : a single commit's metadata, file stats, and diff
 *   - file   (?file=<path>)    : the change history of one tracked file
 *
 * Security model: every argument that reaches git is passed through
 * escapeshellarg(), refs are validated against a strict hash/ref pattern,
 * paths are checked against the set of tracked files, and a `--` separator
 * always precedes pathspecs so user input can never be read as a git option.
 */

header('Content-Type: text/html; charset=utf-8');
// The list view changes on every commit; individual commit/file views are effectively
// immutable once written. A short shared TTL is a safe default for both.
header('Cache-Control: public, max-age=300');

$REPO = __DIR__;
$PER_PAGE = 25;
$MAX_DIFF_BYTES = 600 * 1024; // cap rendered patch size to keep the page responsive

/* ----------------------------------------------------------------------------
 * Git helper — run a read-only git command in this repo and capture output.
 * safe.directory neutralises "dubious ownership" when the web user (e.g.
 * www-data) differs from the repo owner; core.quotepath=false keeps unicode
 * filenames readable.
 * ------------------------------------------------------------------------- */
function git(array $args): array {
    global $REPO;
    $cmd = 'git -C ' . escapeshellarg($REPO)
         . ' -c safe.directory=' . escapeshellarg($REPO)
         . ' -c core.quotepath=false'
         . ' --no-pager';
    foreach ($args as $a) {
        $cmd .= ' ' . escapeshellarg($a);
    }
    $descriptors = [1 => ['pipe', 'w'], 2 => ['pipe', 'w']];
    $proc = @proc_open($cmd, $descriptors, $pipes);
    if (!is_resource($proc)) {
        return ['out' => '', 'err' => 'Unable to launch git.', 'code' => 127];
    }
    $out = stream_get_contents($pipes[1]); fclose($pipes[1]);
    $err = stream_get_contents($pipes[2]); fclose($pipes[2]);
    $code = proc_close($proc);
    return ['out' => $out, 'err' => trim($err), 'code' => $code];
}

function git_ok(): bool {
    $r = git(['rev-parse', '--is-inside-work-tree']);
    return $r['code'] === 0 && trim($r['out']) === 'true';
}

/** A valid ref: short/long hash or a branch/tag name. Never starts with '-'. */
function valid_ref(string $ref): bool {
    return (bool) preg_match('/^[0-9A-Za-z][0-9A-Za-z._\/-]{0,200}$/', $ref);
}

/** Set of files git currently tracks — used to whitelist the ?file= param. */
function tracked_files(): array {
    static $cache = null;
    if ($cache !== null) return $cache;
    $r = git(['ls-files']);
    $cache = $r['code'] === 0 ? array_filter(explode("\n", trim($r['out']))) : [];
    return $cache;
}

function h(?string $s): string {
    return htmlspecialchars((string) $s, ENT_QUOTES, 'UTF-8');
}

/** Human-friendly relative time from a unix timestamp. */
function rel_time(int $ts): string {
    $d = time() - $ts;
    if ($d < 0) $d = 0;
    $units = [
        [31536000, 'year'], [2592000, 'month'], [604800, 'week'],
        [86400, 'day'], [3600, 'hour'], [60, 'minute'], [1, 'second'],
    ];
    foreach ($units as [$secs, $name]) {
        if ($d >= $secs) {
            $n = (int) floor($d / $secs);
            return $n . ' ' . $name . ($n === 1 ? '' : 's') . ' ago';
        }
    }
    return 'just now';
}

/** Deterministic avatar colour from an email, for the author chip. */
function author_color(string $email): string {
    $h = crc32(strtolower(trim($email))) % 360;
    return "hsl($h 55% 42%)";
}

/** Render a unified-diff patch as classed HTML lines. */
function render_diff(string $patch): string {
    $truncated = false;
    if (strlen($patch) > $GLOBALS['MAX_DIFF_BYTES']) {
        $patch = substr($patch, 0, $GLOBALS['MAX_DIFF_BYTES']);
        $truncated = true;
    }
    $lines = explode("\n", $patch);
    $html = '';
    foreach ($lines as $line) {
        $cls = 'd-ctx';
        if (str_starts_with($line, 'diff --git') || str_starts_with($line, 'index ')
            || str_starts_with($line, 'new file') || str_starts_with($line, 'deleted file')
            || str_starts_with($line, 'rename ') || str_starts_with($line, 'similarity ')
            || str_starts_with($line, 'old mode') || str_starts_with($line, 'new mode')) {
            $cls = 'd-meta';
        } elseif (str_starts_with($line, '@@')) {
            $cls = 'd-hunk';
        } elseif (str_starts_with($line, '+++') || str_starts_with($line, '---')) {
            $cls = 'd-file';
        } elseif (str_starts_with($line, '+')) {
            $cls = 'd-add';
        } elseif (str_starts_with($line, '-')) {
            $cls = 'd-del';
        }
        $html .= '<span class="dl ' . $cls . '">' . h($line === '' ? "\n" : $line) . "</span>\n";
    }
    if ($truncated) {
        $html .= '<span class="dl d-meta">… diff truncated (exceeds '
               . round($GLOBALS['MAX_DIFF_BYTES'] / 1024) . " KB) …</span>\n";
    }
    return $html;
}

/* ----------------------------------------------------------------------------
 * Routing
 * ------------------------------------------------------------------------- */
$view   = 'list';
$commit = isset($_GET['commit']) ? trim($_GET['commit']) : '';
$file   = isset($_GET['file'])   ? trim($_GET['file'])   : '';
$q      = isset($_GET['q'])      ? trim($_GET['q'])      : '';
$page   = max(1, (int) ($_GET['page'] ?? 1));

$repoReady = git_ok();

if ($repoReady) {
    if ($commit !== '' && valid_ref($commit)) {
        $view = 'commit';
    } elseif ($file !== '' && in_array($file, tracked_files(), true)) {
        $view = 'file';
    }
}

/* ---- Repo summary (shown on the list view) ---- */
$summary = ['commits' => 0, 'authors' => 0, 'files' => 0, 'first' => null, 'last' => null, 'branch' => ''];
if ($repoReady) {
    $summary['commits'] = (int) trim(git(['rev-list', '--count', 'HEAD'])['out']);
    $summary['files']   = count(tracked_files());
    $authors = git(['shortlog', '-sne', 'HEAD']);
    $summary['authors'] = $authors['code'] === 0
        ? count(array_filter(explode("\n", trim($authors['out'])))) : 0;
    $summary['last']   = (int) trim(git(['log', '-1', '--format=%at', 'HEAD'])['out']);
    $summary['first']  = (int) trim(git(['log', '-1', '--format=%at', '--max-parents=0', 'HEAD'])['out']);
    $br = git(['rev-parse', '--abbrev-ref', 'HEAD']);
    $summary['branch'] = $br['code'] === 0 ? trim($br['out']) : '';
}

/* ---- Build the data for the active view ---- */
$US = "\x1f"; // unit separator between log fields
$commitsList = [];
$hasNext = false;
$detail = null;

if ($repoReady && $view === 'list') {
    $args = ['log', '--no-color',
             '--pretty=format:%H' . $US . '%h' . $US . '%an' . $US . '%ae' . $US . '%at' . $US . '%s',
             '-n', (string) ($PER_PAGE + 1),
             '--skip', (string) (($page - 1) * $PER_PAGE)];
    if ($q !== '') {
        $args[] = '--regexp-ignore-case';
        $args[] = '--all-match';
        // search both message and author; --grep is OR'd with --author via separate terms
        $args[] = '--grep=' . $q;
    }
    $r = git($args);
    if ($r['code'] === 0) {
        $rows = array_filter(explode("\n", $r['out']), fn($l) => $l !== '');
        // If the message search returned nothing, retry as an author search.
        if ($q !== '' && count($rows) === 0) {
            $args2 = ['log', '--no-color',
                      '--pretty=format:%H' . $US . '%h' . $US . '%an' . $US . '%ae' . $US . '%at' . $US . '%s',
                      '-n', (string) ($PER_PAGE + 1),
                      '--skip', (string) (($page - 1) * $PER_PAGE),
                      '--regexp-ignore-case', '--author=' . $q];
            $r2 = git($args2);
            if ($r2['code'] === 0) {
                $rows = array_filter(explode("\n", $r2['out']), fn($l) => $l !== '');
            }
        }
        if (count($rows) > $PER_PAGE) {
            $hasNext = true;
            $rows = array_slice($rows, 0, $PER_PAGE);
        }
        foreach ($rows as $row) {
            $f = explode($US, $row);
            if (count($f) < 6) continue;
            $commitsList[] = [
                'hash' => $f[0], 'short' => $f[1], 'an' => $f[2],
                'ae' => $f[3], 'at' => (int) $f[4], 'subject' => $f[5],
            ];
        }
    }
}

if ($repoReady && $view === 'commit') {
    $meta = git(['show', '-s', '--no-color',
        '--pretty=format:%H' . $US . '%h' . $US . '%an' . $US . '%ae' . $US . '%at' . $US . '%cI' . $US . '%P' . $US . '%s' . $US . '%b',
        $commit]);
    if ($meta['code'] === 0 && trim($meta['out']) !== '') {
        $f = explode($US, $meta['out']);
        $stat = git(['show', '--numstat', '--no-color', '--format=', $commit]);
        $files = [];
        $totAdd = 0; $totDel = 0;
        foreach (explode("\n", trim($stat['out'])) as $sl) {
            if ($sl === '') continue;
            $parts = preg_split('/\t/', $sl);
            if (count($parts) < 3) continue;
            [$add, $del, $path] = $parts;
            $add = $add === '-' ? null : (int) $add;
            $del = $del === '-' ? null : (int) $del;
            $totAdd += (int) $add; $totDel += (int) $del;
            $files[] = ['add' => $add, 'del' => $del, 'path' => $path];
        }
        $patch = git(['show', '--no-color', '--format=', $commit]);
        $detail = [
            'hash' => $f[0] ?? '', 'short' => $f[1] ?? '', 'an' => $f[2] ?? '',
            'ae' => $f[3] ?? '', 'at' => (int) ($f[4] ?? 0), 'iso' => $f[5] ?? '',
            'parents' => trim($f[6] ?? ''), 'subject' => $f[7] ?? '',
            'body' => trim($f[8] ?? ''),
            'files' => $files, 'totAdd' => $totAdd, 'totDel' => $totDel,
            'patch' => $patch['code'] === 0 ? $patch['out'] : '',
        ];
    }
}

if ($repoReady && $view === 'file') {
    $r = git(['log', '--no-color', '--follow',
        '--pretty=format:%H' . $US . '%h' . $US . '%an' . $US . '%ae' . $US . '%at' . $US . '%s',
        '--', $file]);
    $rows = $r['code'] === 0 ? array_filter(explode("\n", $r['out']), fn($l) => $l !== '') : [];
    foreach ($rows as $row) {
        $f = explode($US, $row);
        if (count($f) < 6) continue;
        $commitsList[] = [
            'hash' => $f[0], 'short' => $f[1], 'an' => $f[2],
            'ae' => $f[3], 'at' => (int) $f[4], 'subject' => $f[5],
        ];
    }
}

$selfUrl = strtok($_SERVER['REQUEST_URI'] ?? 'history.php', '?');
$pageTitle = match ($view) {
    'commit' => 'Commit ' . substr($commit, 0, 10) . ' · Change History',
    'file'   => h($file) . ' · Change History',
    default  => 'Change History',
};
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="color-scheme" content="light dark">
    <link rel="icon" href="data:image/svg+xml,<svg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 100 100%22><text y=%22.9em%22 font-size=%2290%22>🕓</text></svg>">

    <title><?php echo $pageTitle; ?> | David Veksler's Cheatsheets</title>
    <meta name="description" content="Browse the full git change history of David Veksler's cheatsheet collection — every commit, diff, and per-file revision, rendered straight from the repository.">
    <meta name="robots" content="noindex, follow">
    <link rel="canonical" href="<?php echo h($selfUrl); ?>">

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
          --add:       light-dark(#1a7f37, #56d364);
          --add-bg:    light-dark(#e6ffec, #12261b);
          --del:       light-dark(#cf222e, #f85149);
          --del-bg:    light-dark(#ffebe9, #2a1416);
          --hunk:      light-dark(#6639ba, #d2a8ff);
        }
        .navbar { background: light-dark(#2c3034, #0f1216); }
        .navbar-brand, .navbar .nav-link { color: #f1f3f5 !important; }
        .card, .list-card {
          background: var(--surface); border: 1px solid var(--border);
          border-radius: .5rem;
        }
        .stat-box {
          background: var(--surface); border: 1px solid var(--border);
          border-radius: .5rem; padding: 1rem 1.1rem; height: 100%;
        }
        .stat-box .num { font-size: 1.6rem; font-weight: 700; line-height: 1; }
        .stat-box .lbl { color: var(--muted); font-size: .8rem; text-transform: uppercase; letter-spacing: .04em; }

        /* Commit list ------------------------------------------------------ */
        .commit-row {
          display: grid; grid-template-columns: 1fr auto; gap: .25rem 1rem;
          padding: .85rem 1.1rem; border-bottom: 1px solid var(--border);
          text-decoration: none; color: inherit;
        }
        .commit-row:last-child { border-bottom: 0; }
        .commit-row:hover { background: var(--surface-2); }
        .commit-row:focus-visible { outline: 2px solid var(--accent); outline-offset: -2px; }
        .commit-subject { font-weight: 600; line-height: 1.35; text-wrap: pretty; }
        .commit-meta { color: var(--muted); font-size: .85rem; display: flex; flex-wrap: wrap; gap: .35rem .9rem; align-items: center; }
        .author-chip {
          display: inline-flex; align-items: center; gap: .35rem; font-weight: 600;
        }
        .author-dot {
          width: 1.25rem; height: 1.25rem; border-radius: 50%; color: #fff;
          font-size: .7rem; display: inline-flex; align-items: center; justify-content: center; font-weight: 700;
        }
        .sha {
          font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
          background: var(--accent-bg); color: var(--accent);
          padding: .05rem .4rem; border-radius: .3rem; font-size: .8rem; white-space: nowrap;
        }

        /* Diff ------------------------------------------------------------- */
        .diff {
          background: var(--surface); border: 1px solid var(--border); border-radius: .5rem;
          overflow-x: auto; font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
          font-size: .82rem; line-height: 1.5; margin: 0;
        }
        .diff .dl { display: block; padding: 0 .9rem; white-space: pre; }
        .diff .d-ctx  { color: var(--text); }
        .diff .d-add  { background: var(--add-bg); color: var(--add); }
        .diff .d-del  { background: var(--del-bg); color: var(--del); }
        .diff .d-hunk { color: var(--hunk); background: var(--surface-2); }
        .diff .d-file { color: var(--muted); font-weight: 600; }
        .diff .d-meta { color: var(--muted); background: var(--surface-2); }

        .filestat { font-family: ui-monospace, monospace; font-size: .85rem; }
        .filestat .a { color: var(--add); } .filestat .d { color: var(--del); }
        .bars { letter-spacing: -1px; }

        .muted { color: var(--muted); }
        .text-balance { text-wrap: balance; }
        footer.site { color: var(--muted); border-top: 1px solid var(--border); }
        #themeToggle { background: transparent; border: 0; color: #f1f3f5; font-size: 1.15rem; cursor: pointer; }
        :focus-visible { outline: 2px solid var(--accent); outline-offset: 2px; }
        @media (prefers-reduced-motion: no-preference) {
          .commit-row, .stat-box { transition: background .12s ease; }
        }
      }
      /* Manual theme override */
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
    </style>
</head>
<body>
    <nav class="navbar navbar-expand-lg sticky-top shadow-sm">
        <div class="container">
            <a class="navbar-brand fw-semibold" href="index.php"><i class="bi bi-journal-richtext me-2"></i>David Veksler's Cheatsheet Portfolio</a>
            <div class="d-flex align-items-center gap-3">
                <a class="nav-link d-none d-sm-inline" href="how-its-built.html"><i class="bi bi-gear-wide-connected me-1"></i>How it's built</a>
                <a class="nav-link d-none d-sm-inline" href="popularity.php"><i class="bi bi-bar-chart-fill me-1"></i>Popularity</a>
                <button id="themeToggle" type="button" aria-label="Toggle colour theme" title="Toggle theme"><i class="bi bi-circle-half"></i></button>
            </div>
        </div>
    </nav>

    <main class="container py-4">
    <?php if (!$repoReady): ?>
        <div class="alert alert-warning">
            <h4 class="alert-heading"><i class="bi bi-exclamation-triangle me-2"></i>History unavailable</h4>
            <p class="mb-0">This page reads from the site's git repository, but git is not reachable here
            (not a git checkout, or the <code>git</code> binary is unavailable to the web server).</p>
            <?php $why = git(['status'])['err']; if ($why): ?><hr><pre class="mb-0 small"><?php echo h($why); ?></pre><?php endif; ?>
        </div>

    <?php elseif ($view === 'commit'): ?>
        <?php if (!$detail): ?>
            <div class="alert alert-warning">Commit <code><?php echo h($commit); ?></code> was not found.
                <a href="history.php">Back to history</a>.</div>
        <?php else: ?>
            <nav aria-label="breadcrumb" class="mb-3">
              <ol class="breadcrumb small mb-0">
                <li class="breadcrumb-item"><a href="history.php">Change History</a></li>
                <li class="breadcrumb-item active"><span class="sha"><?php echo h($detail['short']); ?></span></li>
              </ol>
            </nav>
            <h1 class="h4 text-balance mb-3"><?php echo h($detail['subject']); ?></h1>
            <div class="card p-3 mb-4">
              <div class="d-flex flex-wrap gap-3 align-items-center mb-2">
                <span class="author-chip">
                  <span class="author-dot" style="background:<?php echo h(author_color($detail['ae'])); ?>"><?php echo h(strtoupper(substr($detail['an'], 0, 1))); ?></span>
                  <?php echo h($detail['an']); ?>
                </span>
                <span class="muted"><i class="bi bi-clock me-1"></i><time datetime="<?php echo h($detail['iso']); ?>"><?php echo h(date('M j, Y g:i A', $detail['at'])); ?></time> · <?php echo h(rel_time($detail['at'])); ?></span>
                <span class="sha" title="Full SHA"><?php echo h($detail['hash']); ?></span>
              </div>
              <?php if ($detail['parents'] !== ''): ?>
                <div class="small muted mb-2">
                  Parent<?php echo strpos($detail['parents'], ' ') !== false ? 's' : ''; ?>:
                  <?php foreach (explode(' ', $detail['parents']) as $p): ?>
                    <a class="sha" href="?commit=<?php echo h($p); ?>"><?php echo h(substr($p, 0, 9)); ?></a>
                  <?php endforeach; ?>
                </div>
              <?php endif; ?>
              <?php if ($detail['body'] !== ''): ?>
                <div class="mt-2" style="white-space:pre-wrap; line-height:1.6;"><?php echo h($detail['body']); ?></div>
              <?php endif; ?>
            </div>

            <?php if ($detail['files']): ?>
            <h2 class="h6 muted text-uppercase mb-2">
              <?php echo count($detail['files']); ?> file<?php echo count($detail['files']) === 1 ? '' : 's'; ?> changed
              <span class="filestat ms-2"><span class="a">+<?php echo $detail['totAdd']; ?></span> <span class="d">−<?php echo $detail['totDel']; ?></span></span>
            </h2>
            <div class="card mb-4">
              <ul class="list-group list-group-flush">
                <?php foreach ($detail['files'] as $fl):
                    $isTracked = in_array($fl['path'], tracked_files(), true);
                    $tot = ($fl['add'] ?? 0) + ($fl['del'] ?? 0);
                    $aBars = $tot > 0 ? (int) round(($fl['add'] ?? 0) / $tot * 5) : 0;
                    $dBars = $tot > 0 ? (int) round(($fl['del'] ?? 0) / $tot * 5) : 0;
                ?>
                <li class="list-group-item d-flex justify-content-between align-items-center flex-wrap gap-2" style="background:var(--surface); border-color:var(--border); color:var(--text);">
                  <span class="text-break">
                    <i class="bi bi-file-earmark-text me-1 muted"></i>
                    <?php if ($isTracked): ?>
                      <a href="?file=<?php echo h(urlencode($fl['path'])); ?>"><?php echo h($fl['path']); ?></a>
                    <?php else: ?>
                      <?php echo h($fl['path']); ?>
                    <?php endif; ?>
                  </span>
                  <span class="filestat">
                    <?php if ($fl['add'] === null && $fl['del'] === null): ?>
                      <span class="muted">binary</span>
                    <?php else: ?>
                      <span class="a">+<?php echo $fl['add']; ?></span>
                      <span class="d">−<?php echo $fl['del']; ?></span>
                      <span class="bars"><span class="a"><?php echo str_repeat('▰', $aBars); ?></span><span class="d"><?php echo str_repeat('▰', $dBars); ?></span></span>
                    <?php endif; ?>
                  </span>
                </li>
                <?php endforeach; ?>
              </ul>
            </div>
            <?php endif; ?>

            <?php if (trim($detail['patch']) !== ''): ?>
              <h2 class="h6 muted text-uppercase mb-2">Diff</h2>
              <pre class="diff"><?php echo render_diff($detail['patch']); ?></pre>
            <?php endif; ?>
        <?php endif; ?>

    <?php elseif ($view === 'file'): ?>
        <nav aria-label="breadcrumb" class="mb-3">
          <ol class="breadcrumb small mb-0">
            <li class="breadcrumb-item"><a href="history.php">Change History</a></li>
            <li class="breadcrumb-item active"><?php echo h($file); ?></li>
          </ol>
        </nav>
        <h1 class="h4 text-balance mb-1"><i class="bi bi-file-earmark-text me-1"></i><?php echo h($file); ?></h1>
        <p class="muted mb-4">
          <?php echo count($commitsList); ?> commit<?php echo count($commitsList) === 1 ? '' : 's'; ?> touched this file.
          <?php $isHtml = str_ends_with(strtolower($file), '.html'); if ($isHtml): ?>
            <a href="<?php echo h($file); ?>" target="_blank" rel="noopener">View current version <i class="bi bi-box-arrow-up-right"></i></a>
          <?php endif; ?>
        </p>
        <div class="list-card">
          <?php foreach ($commitsList as $c): ?>
            <a class="commit-row" href="?commit=<?php echo h($c['hash']); ?>">
              <div>
                <div class="commit-subject"><?php echo h($c['subject']); ?></div>
                <div class="commit-meta">
                  <span class="author-chip">
                    <span class="author-dot" style="background:<?php echo h(author_color($c['ae'])); ?>"><?php echo h(strtoupper(substr($c['an'], 0, 1))); ?></span>
                    <?php echo h($c['an']); ?>
                  </span>
                  <span><i class="bi bi-clock me-1"></i><?php echo h(rel_time($c['at'])); ?></span>
                </div>
              </div>
              <div class="text-end align-self-center"><span class="sha"><?php echo h($c['short']); ?></span></div>
            </a>
          <?php endforeach; ?>
        </div>

    <?php else: /* ---------------- list view ---------------- */ ?>
        <header class="mb-4">
          <h1 class="h3 text-balance mb-1"><i class="bi bi-clock-history me-2"></i>Change History</h1>
          <p class="muted mb-0">Every change to this cheatsheet collection, straight from the git repository<?php echo $summary['branch'] ? ' (<code>' . h($summary['branch']) . '</code>)' : ''; ?>.</p>
        </header>

        <div class="row g-3 mb-4">
          <div class="col-6 col-md-3"><div class="stat-box"><div class="num"><?php echo number_format($summary['commits']); ?></div><div class="lbl">Commits</div></div></div>
          <div class="col-6 col-md-3"><div class="stat-box"><div class="num"><?php echo number_format($summary['files']); ?></div><div class="lbl">Tracked files</div></div></div>
          <div class="col-6 col-md-3"><div class="stat-box"><div class="num"><?php echo number_format($summary['authors']); ?></div><div class="lbl">Contributors</div></div></div>
          <div class="col-6 col-md-3"><div class="stat-box"><div class="num" style="font-size:1.05rem;"><?php echo $summary['last'] ? h(date('M j, Y', $summary['last'])) : '—'; ?></div><div class="lbl">Last change</div></div></div>
        </div>

        <form method="get" action="history.php" class="mb-4" role="search">
          <div class="input-group">
            <span class="input-group-text bg-transparent"><i class="bi bi-search"></i></span>
            <input type="search" name="q" class="form-control" value="<?php echo h($q); ?>"
                   placeholder="Search commit messages or authors…" aria-label="Search history">
            <button class="btn btn-primary" type="submit">Search</button>
            <?php if ($q !== ''): ?><a class="btn btn-outline-secondary" href="history.php">Clear</a><?php endif; ?>
          </div>
        </form>

        <?php if (empty($commitsList)): ?>
          <div class="alert alert-info">No commits<?php echo $q !== '' ? ' match “' . h($q) . '”' : ' found'; ?>.</div>
        <?php else: ?>
          <div class="list-card mb-4">
            <?php foreach ($commitsList as $c): ?>
              <a class="commit-row" href="?commit=<?php echo h($c['hash']); ?>">
                <div>
                  <div class="commit-subject"><?php echo h($c['subject']); ?></div>
                  <div class="commit-meta">
                    <span class="author-chip">
                      <span class="author-dot" style="background:<?php echo h(author_color($c['ae'])); ?>"><?php echo h(strtoupper(substr($c['an'], 0, 1))); ?></span>
                      <?php echo h($c['an']); ?>
                    </span>
                    <span><i class="bi bi-clock me-1"></i><time datetime="<?php echo h(date('c', $c['at'])); ?>"><?php echo h(rel_time($c['at'])); ?></time></span>
                  </div>
                </div>
                <div class="text-end align-self-center"><span class="sha"><?php echo h($c['short']); ?></span></div>
              </a>
            <?php endforeach; ?>
          </div>

          <nav class="d-flex justify-content-between align-items-center" aria-label="History pages">
            <?php
              $qParam = $q !== '' ? '&q=' . urlencode($q) : '';
              $prevPage = $page - 1; $nextPage = $page + 1;
            ?>
            <div>
              <?php if ($page > 1): ?>
                <a class="btn btn-outline-secondary" href="?page=<?php echo $prevPage . $qParam; ?>"><i class="bi bi-arrow-left"></i> Newer</a>
              <?php endif; ?>
            </div>
            <span class="muted small">Page <?php echo $page; ?></span>
            <div>
              <?php if ($hasNext): ?>
                <a class="btn btn-outline-secondary" href="?page=<?php echo $nextPage . $qParam; ?>">Older <i class="bi bi-arrow-right"></i></a>
              <?php endif; ?>
            </div>
          </nav>
        <?php endif; ?>
    <?php endif; ?>
    </main>

    <footer class="site py-4 mt-5">
      <div class="container text-center small">
        <a href="index.php"><i class="bi bi-collection-fill me-1"></i>All cheatsheets</a>
        <span class="mx-2">·</span>
        Rendered from git <?php echo $summary['branch'] ? 'on <code>' . h($summary['branch']) . '</code>' : ''; ?>
        · © <?php echo date('Y'); ?> David Veksler
      </div>
    </footer>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.8/dist/js/bootstrap.bundle.min.js" integrity="sha384-FKyoEForCGlyvwx9Hj09JcYn3nv7wiPVlz7YYwJrWVcXK/BmnVDxM+D2scQbITxI" crossorigin="anonymous" defer></script>
    <script>
      // Manual light/dark override, persisted; defaults to OS preference.
      (function () {
        const KEY = 'cheatsheet-theme';
        const root = document.documentElement;
        const saved = (function () { try { return localStorage.getItem(KEY); } catch (e) { return null; } })();
        if (saved === 'light' || saved === 'dark') root.setAttribute('data-theme', saved);
        document.addEventListener('DOMContentLoaded', function () {
          const btn = document.getElementById('themeToggle');
          if (!btn) return;
          btn.addEventListener('click', function () {
            const current = root.getAttribute('data-theme')
              || (window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light');
            const next = current === 'dark' ? 'light' : 'dark';
            root.setAttribute('data-theme', next);
            try { localStorage.setItem(KEY, next); } catch (e) {}
          });
        });
      })();
    </script>
</body>
</html>
