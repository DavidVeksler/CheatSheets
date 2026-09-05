<?php
/**
 * lib/chrome.php — shared page chrome (head boilerplate, design tokens,
 * topbar, footer) for the site's utility pages: history.php and
 * popularity.php. Keeps them reading as the same product as the index.php
 * Explorer instead of a bolted-on admin panel.
 *
 * Palette and layout primitives (--page/--surface/--rule/--ink/--muted/
 * --accent, .wrap, .topbar, .tbtn, .num, .lbl, footer.site) are copied from
 * index.php's @layer base/layout — if the Explorer's palette is retuned,
 * mirror the change here. Theme state shares index.php's localStorage key
 * (cs-explorer:v1:theme) so the toggle stays in sync across all three pages.
 */

function chrome_h(?string $s): string
{
    return htmlspecialchars((string) $s, ENT_QUOTES, 'UTF-8');
}

/** Shared design tokens + topbar/footer primitives. Page-specific component
 *  CSS (stat tiles, commit rows, diff colours, rank bars, …) stays local to
 *  each page's own <style> block. */
function chrome_css(): string
{
    return <<<'CSS'
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
  --danger: light-dark(#b91c1c, #f87171);
  --gold: light-dark(#92660a, #f5c451);
  --sans: system-ui, -apple-system, "Segoe UI", Roboto, sans-serif;
  --mono: ui-monospace, "SF Mono", Menlo, Consolas, monospace;
}
:root[data-theme="light"]{ color-scheme: light; }
:root[data-theme="dark"]{ color-scheme: dark; }
*,*::before,*::after{box-sizing:border-box}
body{margin:0;background:var(--page);color:var(--ink);font:15px/1.55 var(--sans);text-wrap:pretty;-webkit-text-size-adjust:100%}
h1,h2,h3{text-wrap:balance;margin:0 0 .4em;line-height:1.2}
h1{font-size:clamp(28px,4vw,38px);font-weight:650;letter-spacing:-.015em}
h2{font-size:16px;font-weight:620}
p{margin:0 0 1em}
a{color:var(--accent);text-decoration:none}
a:hover{text-decoration:underline}
:focus-visible{outline:2px solid var(--accent);outline-offset:2px;border-radius:3px}
button{font:inherit;color:inherit}
code{font-family:var(--mono);background:var(--accent-surface);padding:.1em .4em;border-radius:4px;font-size:.92em}
.sr{position:absolute;width:1px;height:1px;padding:0;margin:-1px;overflow:hidden;clip:rect(0 0 0 0);white-space:nowrap;border:0}
.skip{position:absolute;left:-999px;top:0;background:var(--raised);padding:.6rem 1rem;z-index:60}
.skip:focus{left:.5rem;top:.5rem}
.num{font-family:var(--mono);font-variant-numeric:tabular-nums}
.lbl{font-size:11px;letter-spacing:.09em;text-transform:uppercase;color:var(--muted);font-weight:600}
.wrap{max-width:1200px;margin:0 auto;padding:0 clamp(14px,3vw,28px)}
.topbar{position:sticky;top:0;z-index:30;background:var(--page);border-bottom:1px solid var(--rule)}
.topbar .wrap{display:flex;align-items:center;gap:12px;min-height:52px}
.brand{font-weight:650;color:var(--ink);letter-spacing:-.01em;white-space:nowrap}
.topnav{display:flex;gap:14px;margin-left:auto;font-size:13px;align-items:center}
.topnav a{color:var(--muted)}
.topnav a:hover{color:var(--ink);text-decoration:underline}
.topnav a.cur{color:var(--ink);font-weight:620}
.tbtn{display:inline-flex;align-items:center;gap:6px;background:var(--surface);border:1px solid var(--rule);border-radius:6px;padding:5px 9px;font-size:13px;cursor:pointer;color:var(--ink)}
.tbtn:hover{border-color:var(--accent)}
main{display:block;padding:22px 0 8px}
.hero{padding:8px 0 22px;border-bottom:1px solid var(--rule);margin-bottom:22px}
.hero p.lead{color:var(--muted);max-width:74ch;margin:6px 0 0;font-size:14.5px}
.crumb{font-size:12.5px;color:var(--muted);margin:0 0 10px}
.crumb a{color:var(--muted)}
.crumb a:hover{color:var(--ink)}
.note{border:1px solid var(--rule);border-left:3px solid var(--accent);border-radius:0 8px 8px 0;background:var(--surface);padding:12px 16px;font-size:13.5px;color:var(--muted)}
.note.warn{border-left-color:var(--danger)}
.note strong{color:var(--ink)}
.stats{display:grid;grid-template-columns:repeat(auto-fit,minmax(130px,1fr));gap:10px;margin:0 0 22px}
.stat{border:1px solid var(--rule);border-radius:8px;background:var(--surface);padding:10px 14px}
.stat .n{font-family:var(--mono);font-size:20px;font-weight:650;font-variant-numeric:tabular-nums}
.stat .l{font-size:11px;letter-spacing:.09em;text-transform:uppercase;color:var(--muted);font-weight:600;margin-top:2px}
.list-card{border:1px solid var(--rule);border-radius:8px;background:var(--surface);overflow:hidden;margin-bottom:18px}
.sectlbl{margin:0 0 8px}
footer.site{border-top:1px solid var(--rule);padding:22px 0 34px;color:var(--muted);font-size:13px;margin-top:36px}
footer.site a{color:var(--muted)}
footer.site .frow{display:flex;flex-wrap:wrap;gap:8px 16px;align-items:center}
@media (max-width:600px){ .topnav a.hidesm{display:none} }
CSS;
}

/** Opens <html>…<body>, prints <head>, the skip link, and the topbar.
 *  $active is 'history' or 'popularity' — bolds the matching nav link. */
function chrome_open(string $title, string $desc, string $icon, string $canonical, string $active, string $robots = 'noindex, follow'): void
{
    ?>
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<script>
document.documentElement.className='js';
try{var t=localStorage.getItem('cs-explorer:v1:theme');if(t==='light'||t==='dark')document.documentElement.dataset.theme=t;}catch(e){}
</script>
<link rel="icon" href="data:image/svg+xml,<svg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 100 100%22><text y=%22.9em%22 font-size=%2290%22><?php echo $icon; ?></text></svg>">
<title><?php echo chrome_h($title); ?></title>
<meta name="description" content="<?php echo chrome_h($desc); ?>">
<meta name="robots" content="<?php echo chrome_h($robots); ?>">
<link rel="canonical" href="<?php echo chrome_h($canonical); ?>">
<style>
<?php echo chrome_css(); ?>
</style>
</head>
<body>
<a class="skip" href="#main">Skip to content</a>
<header class="topbar">
  <div class="wrap">
    <a class="brand" href="./">Cheatsheets<span class="sr"> home</span></a>
    <nav class="topnav" aria-label="Site">
      <a class="hidesm" href="how-its-built.html">How it's built</a>
      <a class="hidesm<?php echo $active === 'history' ? ' cur' : ''; ?>" href="history.php">Change history</a>
      <a class="hidesm<?php echo $active === 'popularity' ? ' cur' : ''; ?>" href="popularity.php">Popularity</a>
      <button class="tbtn" id="themeToggle" type="button" aria-label="Toggle dark mode" title="Toggle theme">
        <svg width="14" height="14" viewBox="0 0 16 16" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M13.2 9.6A5.6 5.6 0 0 1 6.4 2.8 5.6 5.6 0 1 0 13.2 9.6Z"/></svg>
      </button>
    </nav>
  </div>
</header>
<main id="main">
<?php
}

/** Closes <main>, prints the footer, theme-toggle script, and </body></html>. */
function chrome_close(): void
{
    ?>
</main>
<footer class="site">
  <div class="wrap frow">
    <span>Cheatsheets © <?php echo date('Y'); ?> David Veksler.</span>
    <a href="./">All cheatsheets</a>
    <a href="how-its-built.html">How it's built</a>
    <a href="history.php">Change history</a>
    <a href="popularity.php">Popularity</a>
    <a href="https://github.com/DavidVeksler/CheatSheets" rel="noopener">GitHub</a>
  </div>
</footer>
<script>
(function(){
  var NS='cs-explorer:v1:';
  function ls(k,v){try{if(v===undefined)return localStorage.getItem(NS+k);localStorage.setItem(NS+k,v);}catch(e){}return null;}
  function current(){var d=document.documentElement.dataset.theme;if(d)return d;return window.matchMedia('(prefers-color-scheme: dark)').matches?'dark':'light';}
  document.getElementById('themeToggle').addEventListener('click',function(){
    var next=current()==='dark'?'light':'dark';
    document.documentElement.dataset.theme=next;
    ls('theme',next);
  });
})();
</script>
</body>
</html>
<?php
}
