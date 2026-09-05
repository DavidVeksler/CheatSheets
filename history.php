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
$commit = isset($_GET['commit']) ? trim(str_replace("\0", '', $_GET['commit'])) : '';
$file   = isset($_GET['file'])   ? trim(str_replace("\0", '', $_GET['file']))   : '';
$q      = isset($_GET['q'])      ? trim(str_replace("\0", '', $_GET['q']))      : '';
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
$baseUrl = 'https://cheatsheets.davidveksler.com/';
$pageTitle = match ($view) {
    'commit' => 'Commit ' . substr($commit, 0, 10) . ' · Change History',
    'file'   => h($file) . ' · Change History',
    default  => 'Change History',
} . ' · Cheatsheets';

require __DIR__ . '/lib/chrome.php';
chrome_open(
    $pageTitle,
    "Browse the full git change history of David Veksler's cheatsheet collection — every commit, diff, and per-file revision, rendered straight from the repository.",
    '🕓',
    $baseUrl . $selfUrl,
    'history'
);
?>
<style>
.searchbar{display:flex;gap:8px;max-width:520px;margin:0 0 20px}
.searchbar input{flex:1;min-width:0;font:14px var(--sans);padding:9px 12px;border:1px solid var(--rule);border-radius:8px;background:var(--surface);color:var(--ink)}
.searchbar input:focus-visible{border-color:var(--accent)}
.searchbar button{padding:9px 16px;border:1px solid var(--accent);background:var(--accent);color:var(--page);border-radius:8px;font-weight:600;cursor:pointer;font-size:14px}
.searchbar .clear{border:1px solid var(--rule);background:var(--surface);color:var(--ink);border-radius:8px;padding:9px 14px;font-size:14px;text-decoration:none}
.searchbar .clear:hover{border-color:var(--accent)}

.commit-row{display:flex;justify-content:space-between;align-items:center;gap:14px;padding:11px 16px;border-bottom:1px solid var(--rule);color:inherit;text-decoration:none}
.commit-row:last-child{border-bottom:0}
.commit-row:hover{background:var(--accent-surface);text-decoration:none}
.commit-subject{font-weight:600;font-size:14px;line-height:1.35;color:var(--ink)}
.commit-meta{display:flex;flex-wrap:wrap;gap:4px 12px;align-items:center;margin-top:4px;font-size:12.5px;color:var(--muted)}
.author-chip{display:inline-flex;align-items:center;gap:6px;font-weight:600;color:var(--ink)}
.author-dot{width:18px;height:18px;border-radius:50%;color:#fff;font-size:10px;font-weight:700;display:inline-flex;align-items:center;justify-content:center;flex:none}
.sha{font-family:var(--mono);font-size:12px;background:var(--accent-surface);color:var(--accent);padding:1px 7px;border-radius:5px;white-space:nowrap;text-decoration:none}
.commit-row .sha{flex:none}

.pager{display:flex;justify-content:space-between;align-items:center;margin-top:4px;font-size:13px;color:var(--muted)}
.pager a{border:1px solid var(--rule);border-radius:999px;padding:5px 14px;color:var(--ink);background:var(--surface);text-decoration:none}
.pager a:hover{border-color:var(--accent)}

.detail{border:1px solid var(--rule);border-radius:8px;background:var(--surface);padding:16px 18px;margin:0 0 20px}
.detail .meta-row{display:flex;flex-wrap:wrap;gap:8px 16px;align-items:center;margin-bottom:6px;font-size:13.5px;color:var(--muted)}
.detail .body{white-space:pre-wrap;line-height:1.6;margin-top:10px;font-size:14px;color:var(--ink)}
.parents{font-size:12.5px;color:var(--muted);margin-top:6px}

.filelist{border:1px solid var(--rule);border-radius:8px;background:var(--surface);overflow:hidden;margin-bottom:20px}
.filerow{display:flex;justify-content:space-between;align-items:center;gap:12px;padding:8px 14px;border-bottom:1px solid var(--rule);font-size:13.5px}
.filerow:last-child{border-bottom:0}
.filerow .path{word-break:break-all}
.filestat{font-family:var(--mono);font-size:12.5px;white-space:nowrap}
.filestat .a{color:var(--success)}
.filestat .d{color:var(--danger)}
.bars{letter-spacing:-1px}

.diff{background:var(--surface);border:1px solid var(--rule);border-radius:8px;overflow-x:auto;font-family:var(--mono);font-size:12.5px;line-height:1.55;margin:0 0 20px;padding:6px 0}
.diff .dl{display:block;padding:0 14px;white-space:pre}
.diff .d-add{background:color-mix(in srgb,var(--success) 14%,transparent);color:var(--success)}
.diff .d-del{background:color-mix(in srgb,var(--danger) 14%,transparent);color:var(--danger)}
.diff .d-hunk{color:var(--accent);background:var(--accent-surface)}
.diff .d-file{color:var(--muted);font-weight:600}
.diff .d-meta{color:var(--muted);background:var(--accent-surface)}
</style>

<div class="wrap">
<?php if (!$repoReady): ?>
  <div class="note warn">
    <strong>History unavailable.</strong> This page reads from the site's git repository, but git is not reachable here
    (not a git checkout, or the <code>git</code> binary is unavailable to the web server).
    <?php $why = git(['status'])['err']; if ($why): ?><br><br><code><?php echo h($why); ?></code><?php endif; ?>
  </div>

<?php elseif ($view === 'commit'): ?>
  <?php if (!$detail): ?>
    <div class="note warn">Commit <code><?php echo h($commit); ?></code> was not found. <a href="history.php">Back to history</a>.</div>
  <?php else: ?>
    <p class="crumb"><a href="history.php">Change history</a> / <span class="sha"><?php echo h($detail['short']); ?></span></p>
    <h1><?php echo h($detail['subject']); ?></h1>
    <div class="detail">
      <div class="meta-row">
        <span class="author-chip">
          <span class="author-dot" style="background:<?php echo h(author_color($detail['ae'])); ?>"><?php echo h(strtoupper(substr($detail['an'], 0, 1))); ?></span>
          <?php echo h($detail['an']); ?>
        </span>
        <span><time datetime="<?php echo h($detail['iso']); ?>"><?php echo h(date('M j, Y g:i A', $detail['at'])); ?></time> · <?php echo h(rel_time($detail['at'])); ?></span>
        <span class="sha" title="Full SHA"><?php echo h($detail['hash']); ?></span>
      </div>
      <?php if ($detail['parents'] !== ''): ?>
        <div class="parents">
          Parent<?php echo strpos($detail['parents'], ' ') !== false ? 's' : ''; ?>:
          <?php foreach (explode(' ', $detail['parents']) as $p): ?>
            <a class="sha" href="?commit=<?php echo h($p); ?>"><?php echo h(substr($p, 0, 9)); ?></a>
          <?php endforeach; ?>
        </div>
      <?php endif; ?>
      <?php if ($detail['body'] !== ''): ?>
        <div class="body"><?php echo h($detail['body']); ?></div>
      <?php endif; ?>
    </div>

    <?php if ($detail['files']): ?>
    <p class="lbl sectlbl">
      <?php echo count($detail['files']); ?> file<?php echo count($detail['files']) === 1 ? '' : 's'; ?> changed
      <span class="filestat"><span class="a">+<?php echo $detail['totAdd']; ?></span> <span class="d">−<?php echo $detail['totDel']; ?></span></span>
    </p>
    <div class="filelist">
      <?php foreach ($detail['files'] as $fl):
          $isTracked = in_array($fl['path'], tracked_files(), true);
          $tot = ($fl['add'] ?? 0) + ($fl['del'] ?? 0);
          $aBars = $tot > 0 ? (int) round(($fl['add'] ?? 0) / $tot * 5) : 0;
          $dBars = $tot > 0 ? (int) round(($fl['del'] ?? 0) / $tot * 5) : 0;
      ?>
      <div class="filerow">
        <span class="path">
          <?php if ($isTracked): ?>
            <a href="?file=<?php echo h(urlencode($fl['path'])); ?>"><?php echo h($fl['path']); ?></a>
          <?php else: ?>
            <?php echo h($fl['path']); ?>
          <?php endif; ?>
        </span>
        <span class="filestat">
          <?php if ($fl['add'] === null && $fl['del'] === null): ?>
            <span class="l" style="color:var(--muted)">binary</span>
          <?php else: ?>
            <span class="a">+<?php echo $fl['add']; ?></span>
            <span class="d">−<?php echo $fl['del']; ?></span>
            <span class="bars"><span class="a"><?php echo str_repeat('▰', $aBars); ?></span><span class="d"><?php echo str_repeat('▰', $dBars); ?></span></span>
          <?php endif; ?>
        </span>
      </div>
      <?php endforeach; ?>
    </div>
    <?php endif; ?>

    <?php if (trim($detail['patch']) !== ''): ?>
      <p class="lbl sectlbl">Diff</p>
      <pre class="diff"><?php echo render_diff($detail['patch']); ?></pre>
    <?php endif; ?>
  <?php endif; ?>

<?php elseif ($view === 'file'): ?>
  <p class="crumb"><a href="history.php">Change history</a> / <?php echo h($file); ?></p>
  <h1><?php echo h($file); ?></h1>
  <p class="lead" style="color:var(--muted);margin:0 0 18px">
    <?php echo count($commitsList); ?> commit<?php echo count($commitsList) === 1 ? '' : 's'; ?> touched this file.
    <?php $isHtml = str_ends_with(strtolower($file), '.html'); if ($isHtml): ?>
      <a href="<?php echo h($file); ?>" target="_blank">View current version →</a>
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
            <span><?php echo h(rel_time($c['at'])); ?></span>
          </div>
        </div>
        <span class="sha"><?php echo h($c['short']); ?></span>
      </a>
    <?php endforeach; ?>
  </div>

<?php else: /* ---------------- list view ---------------- */ ?>
  <section class="hero">
    <h1>Change history</h1>
    <p class="lead">Every change to this cheatsheet collection, straight from the git repository<?php echo $summary['branch'] ? ' (<code>' . h($summary['branch']) . '</code>)' : ''; ?>.</p>
  </section>

  <div class="stats">
    <div class="stat"><div class="n"><?php echo number_format($summary['commits']); ?></div><div class="l">Commits</div></div>
    <div class="stat"><div class="n"><?php echo number_format($summary['files']); ?></div><div class="l">Tracked files</div></div>
    <div class="stat"><div class="n"><?php echo number_format($summary['authors']); ?></div><div class="l">Contributors</div></div>
    <div class="stat"><div class="n" style="font-size:15px"><?php echo $summary['last'] ? h(date('M j, Y', $summary['last'])) : '—'; ?></div><div class="l">Last change</div></div>
  </div>

  <form method="get" action="history.php" class="searchbar" role="search">
    <label class="sr" for="hq">Search commit messages or authors</label>
    <input type="search" id="hq" name="q" value="<?php echo h($q); ?>" placeholder="Search commit messages or authors…" autocomplete="off">
    <button type="submit">Search</button>
    <?php if ($q !== ''): ?><a class="clear" href="history.php">Clear</a><?php endif; ?>
  </form>

  <?php if (empty($commitsList)): ?>
    <div class="note">No commits<?php echo $q !== '' ? ' match "' . h($q) . '"' : ' found'; ?>.</div>
  <?php else: ?>
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
              <span><time datetime="<?php echo h(date('c', $c['at'])); ?>"><?php echo h(rel_time($c['at'])); ?></time></span>
            </div>
          </div>
          <span class="sha"><?php echo h($c['short']); ?></span>
        </a>
      <?php endforeach; ?>
    </div>

    <nav class="pager" aria-label="History pages">
      <?php
        $qParam = $q !== '' ? '&q=' . urlencode($q) : '';
        $prevPage = $page - 1; $nextPage = $page + 1;
      ?>
      <div><?php if ($page > 1): ?><a href="?page=<?php echo $prevPage . $qParam; ?>">← Newer</a><?php endif; ?></div>
      <span class="num">Page <?php echo $page; ?></span>
      <div><?php if ($hasNext): ?><a href="?page=<?php echo $nextPage . $qParam; ?>">Older →</a><?php endif; ?></div>
    </nav>
  <?php endif; ?>
<?php endif; ?>
</div>
<?php chrome_close(); ?>

