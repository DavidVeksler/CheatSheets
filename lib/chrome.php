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
 *
 * Also home to the site's inline icon set (chrome_icon / chrome_icon_paths),
 * which index.php and the newsletter pages pull in on their own.
 */

function chrome_h(?string $s): string
{
    return htmlspecialchars((string) $s, ENT_QUOTES, 'UTF-8');
}

/**
 * Icon set: hand-drawn 16×16 stroke glyphs in the Bootstrap Icons idiom
 * (1.5px stroke, round caps and joins, optical weight tuned for 12–16px).
 * Inline SVG rather than an icon font so there is no webfont to SRI-pin, no
 * FOIT on a slow link, no extra request, and every glyph inherits
 * currentColor and the page's light/dark tokens for free. Shared by
 * index.php, history.php, popularity.php, and the newsletter pages so the
 * same concept always gets the same glyph (Change history is always the
 * clock-with-arrow, Popularity is always the bar chart, and so on).
 *
 * Fill-only shapes set fill="currentColor" stroke="none" on the element;
 * everything else is a stroke on a transparent fill.
 */
function chrome_icon_paths(): array
{
    return [
        // -- navigation & site chrome ------------------------------------
        'search'      => '<circle cx="7" cy="7" r="4.5"/><path d="M10.5 10.5 14 14"/>',
        'moon'        => '<path d="M13.2 9.6A5.6 5.6 0 0 1 6.4 2.8 5.6 5.6 0 1 0 13.2 9.6Z"/>',
        'sun'         => '<circle cx="8" cy="8" r="3"/><path d="M8 1.5v1.8M8 12.7v1.8M1.5 8h1.8M12.7 8h1.8M3.4 3.4l1.3 1.3M11.3 11.3l1.3 1.3M3.4 12.6l1.3-1.3M11.3 4.7l1.3-1.3"/>',
        'hammer'      => '<path d="M9 2.5 13.5 7l-1.7 1.7-4.5-4.5L9 2.5Z"/><path d="M7.9 6.4 2.5 11.8l1.7 1.7 5.4-5.4"/>',
        'history'     => '<path d="M8 1.7a6.3 6.3 0 1 1-4.45 1.85"/><path d="M3.55 1.5v2.05H1.5"/><path d="M8 4.5V8l2.6 1.6"/>',
        'chart'       => '<rect x="2" y="9" width="2.4" height="5" rx=".6" fill="currentColor" stroke="none"/><rect x="6.8" y="5.5" width="2.4" height="8.5" rx=".6" fill="currentColor" stroke="none"/><rect x="11.6" y="2" width="2.4" height="12" rx=".6" fill="currentColor" stroke="none"/>',
        'git'         => '<circle cx="4" cy="3" r="1.7"/><circle cx="4" cy="13" r="1.7"/><circle cx="12" cy="5" r="1.7"/><path d="M4 4.7v6.6M12 6.7c0 2.5-3.5 2.6-6 3.3-1 .3-2 .8-2 1.3"/>',
        'braces'      => '<path d="M6 1.5c-1.5 0-2 .8-2 2v2.3c0 1-.5 1.7-1.5 2.2 1 .5 1.5 1.2 1.5 2.2v2.3c0 1.2.5 2 2 2M10 1.5c1.5 0 2 .8 2 2v2.3c0 1 .5 1.7 1.5 2.2-1 .5-1.5 1.2-1.5 2.2v2.3c0 1.2-.5 2-2 2"/>',
        'people'      => '<circle cx="6" cy="5.5" r="2.5"/><path d="M1.5 14c0-3 2-4.5 4.5-4.5s4.5 1.5 4.5 4.5"/><circle cx="11.5" cy="6" r="2"/><path d="M12.5 9.7c1.4.4 2 1.9 2 4.3"/>',
        'keyboard'    => '<rect x="1.5" y="4" width="13" height="8" rx="1.2"/><path d="M4 6.5h1M6.5 6.5h1M9 6.5h1M11.5 6.5h1M4 9.5h8"/>',
        'dice'        => '<rect x="2" y="2" width="12" height="12" rx="2"/><circle cx="5.2" cy="5.2" r="1" fill="currentColor" stroke="none"/><circle cx="10.8" cy="5.2" r="1" fill="currentColor" stroke="none"/><circle cx="8" cy="8" r="1" fill="currentColor" stroke="none"/><circle cx="5.2" cy="10.8" r="1" fill="currentColor" stroke="none"/><circle cx="10.8" cy="10.8" r="1" fill="currentColor" stroke="none"/>',
        'external'    => '<path d="M13 9.5V13a1 1 0 0 1-1 1H3a1 1 0 0 1-1-1V4a1 1 0 0 1 1-1h3.5"/><path d="M9.5 2H14v4.5M14 2 7.5 8.5"/>',
        'link'        => '<path d="M6.5 9.5a3 3 0 0 0 4.2 0l2-2a3 3 0 0 0-4.2-4.2l-1 1"/><path d="M9.5 6.5a3 3 0 0 0-4.2 0l-2 2a3 3 0 0 0 4.2 4.2l1-1"/>',
        'arrow-left'  => '<path d="M14 8H2M6.5 3.5 2 8l4.5 4.5"/>',
        'arrow-right' => '<path d="M2 8h12M9.5 3.5 14 8l-4.5 4.5"/>',
        'chevron-left'  => '<path d="M10 3 5 8l5 5"/>',
        'chevron-right' => '<path d="M6 3l5 5-5 5"/>',
        'reset'       => '<path d="M2.7 6.3A5.5 5.5 0 1 1 2.5 9.5"/><path d="M1.5 3v3.5H5"/>',
        'x'           => '<path d="M4 4l8 8M12 4l-8 8"/>',
        'x-circle'    => '<circle cx="8" cy="8" r="6.3"/><path d="M5.8 5.8l4.4 4.4M10.2 5.8l-4.4 4.4"/>',
        'check'       => '<path d="M3 8.5l3 3 7-7"/>',
        'check-circle'=> '<circle cx="8" cy="8" r="6.3"/><path d="M5 8.2l2 2 4-4.2"/>',
        'info'        => '<circle cx="8" cy="8" r="6.3"/><path d="M8 7.3v4.2"/><circle cx="8" cy="5.1" r=".9" fill="currentColor" stroke="none"/>',
        'warning'     => '<path d="M8 2 1.6 13.2a.6.6 0 0 0 .5.8h11.8a.6.6 0 0 0 .5-.8L8 2Z"/><path d="M8 6.2v3.6"/><circle cx="8" cy="12" r=".75" fill="currentColor" stroke="none"/>',
        'alert'       => '<circle cx="8" cy="8" r="6.3"/><path d="M8 4.5v4.3"/><circle cx="8" cy="11.3" r=".85" fill="currentColor" stroke="none"/>',
        'shield'      => '<path d="M8 1.5 2.5 3.5v4c0 3.5 2.3 5.8 5.5 7 3.2-1.2 5.5-3.5 5.5-7v-4L8 1.5Z"/><path d="M5.5 8l1.8 1.8 3.4-3.6"/>',
        // -- mail ------------------------------------------------------------
        'envelope'    => '<rect x="1.5" y="3.5" width="13" height="9" rx="1.2"/><path d="m1.5 5 6.5 4.5L14.5 5"/>',
        'bell'        => '<path d="M8 2a4 4 0 0 0-4 4v3l-1.5 2.5h11L12 9V6a4 4 0 0 0-4-4Z"/><path d="M6.5 13.5a1.5 1.5 0 0 0 3 0"/>',
        'send'        => '<path d="M14.5 1.5 1.5 6.8l5.4 2.3 2.3 5.4 5.3-13Z"/><path d="M6.9 9.1 14.5 1.5"/>',
        // -- explorer lenses & facets -------------------------------------------
        'grid'        => '<rect x="1.5" y="1.5" width="5.5" height="5.5" rx="1"/><rect x="9" y="1.5" width="5.5" height="5.5" rx="1"/><rect x="1.5" y="9" width="5.5" height="5.5" rx="1"/><rect x="9" y="9" width="5.5" height="5.5" rx="1"/>',
        'map'         => '<circle cx="3.5" cy="4" r="1.6"/><circle cx="12" cy="3" r="1.6"/><circle cx="8" cy="9.5" r="1.6"/><circle cx="13" cy="12.5" r="1.6"/><circle cx="3" cy="12" r="1.6"/><path d="M4.6 5.2 6.9 8.1M11.3 4.4 8.9 8M9.4 10.3l2.3 1.4M6.6 10.3 4.3 11.2"/>',
        'signpost'    => '<path d="M8 1.5v13M5.5 14.5h5"/><path d="M8 3.5h5l1.5 1.5L13 6.5H8M8 8H3l-1.5 1.5L3 11h5"/>',
        'tag'         => '<path d="M1.5 2.5v5l7 7 6-6-7-7h-5a1 1 0 0 0-1 1Z"/><circle cx="5" cy="6" r="1.1"/>',
        'shapes'      => '<circle cx="4.5" cy="4.5" r="3"/><path d="M11.5 1.5 14.5 7h-6l3-5.5Z"/><rect x="1.5" y="9" width="5.5" height="5.5" rx="1"/><path d="M8.8 12.5a2.8 2.8 0 1 0 5.6 0 2.8 2.8 0 0 0-5.6 0Z"/>',
        'sparkles'    => '<path d="M6.5 1.5l1.3 3.4L11.2 6.2 7.8 7.5 6.5 10.9 5.2 7.5 1.8 6.2l3.4-1.3L6.5 1.5Z"/><path d="M12.3 9.5l.7 1.7 1.7.7-1.7.7-.7 1.7-.7-1.7-1.7-.7 1.7-.7.7-1.7Z"/>',
        'funnel'      => '<path d="M1.5 2.5h13L9.5 8.5v5L6.5 15V8.5L1.5 2.5Z"/>',
        'sort'        => '<path d="M3 3v10M1 11l2 2 2-2"/><path d="M7 3.5h7M7 7h5M7 10.5h3"/>',
        'gem'         => '<path d="M4 1.5h8l2.5 4L8 14.5 1.5 5.5 4 1.5Z"/><path d="M1.5 5.5h13M6 1.5 8 5.5l2-4M4.5 5.5 8 14.5l3.5-9"/>',
        'inbox'       => '<path d="M1.5 9.5 3.5 3.5h9l2 6v4a1 1 0 0 1-1 1h-11a1 1 0 0 1-1-1v-4Z"/><path d="M1.5 9.5h4l1 2h3l1-2h4"/>',
        'collection'  => '<rect x="1.5" y="5" width="13" height="9.5" rx="1"/><path d="M3.5 3h9M5.5 1.5h5"/>',
        'list'        => '<path d="M6 3.5h8M6 8h8M6 12.5h8"/><circle cx="2.2" cy="3.5" r=".9" fill="currentColor" stroke="none"/><circle cx="2.2" cy="8" r=".9" fill="currentColor" stroke="none"/><circle cx="2.2" cy="12.5" r=".9" fill="currentColor" stroke="none"/>',
        'layers'      => '<path d="M8 2 14 5.5 8 9 2 5.5 8 2Z"/><path d="M2 8.5 8 12l6-3.5"/><path d="M2 11.5 8 15l6-3.5"/>',
        // -- git history ------------------------------------------------------
        'commit'      => '<circle cx="8" cy="8" r="2.6"/><path d="M1.5 8h3.9M10.6 8h3.9"/>',
        'file'        => '<path d="M4 1.5h4.5L12 5v9.5a.5.5 0 0 1-.5.5h-7a.5.5 0 0 1-.5-.5v-13a.5.5 0 0 1 .5-.5Z"/><path d="M8.5 1.5V5H12"/>',
        'files'       => '<path d="M5.5 4.5h5l3 3v6.5a.5.5 0 0 1-.5.5h-7.5a.5.5 0 0 1-.5-.5v-9a.5.5 0 0 1 .5-.5Z"/><path d="M10.5 4.5v3h3"/><path d="M3 11V2a.5.5 0 0 1 .5-.5H9"/>',
        'diff'        => '<path d="M4 1.5h4.5L12 5v9.5a.5.5 0 0 1-.5.5h-7a.5.5 0 0 1-.5-.5v-13a.5.5 0 0 1 .5-.5Z"/><path d="M8 6.2v3.6M6.2 8h3.6M6.2 12h3.6"/>',
        'calendar'    => '<rect x="2" y="3" width="12" height="11" rx="1.2"/><path d="M2 6.5h12M5 1.5v3M11 1.5v3"/>',
        'hash'        => '<path d="M5.7 1.5 4.3 14.5M11.7 1.5l-1.4 13M2.5 5.5h12M1.5 10.5h12"/>',
        'branch'      => '<circle cx="4" cy="3.5" r="1.7"/><circle cx="4" cy="12.5" r="1.7"/><circle cx="12" cy="3.5" r="1.7"/><path d="M4 5.2v5.6M12 5.2c0 3-8 1.6-8 5.3"/>',
        'binary'      => '<rect x="1.5" y="3" width="13" height="10" rx="1.2"/><path d="M4.5 6v4M4.5 6h1M7.5 6.5a1 1 0 0 1 2 0v3a1 1 0 0 1-2 0v-3ZM11.5 6v4M11.5 6h1"/>',
        // -- popularity stats ----------------------------------------------------
        'star'        => '<path d="M8 1.8l1.7 3.5 3.9.6-2.8 2.7.7 3.9L8 10.6l-3.5 1.9.7-3.9-2.8-2.7 3.9-.6L8 1.8Z"/>',
        'clock'       => '<circle cx="8" cy="8" r="6.3"/><path d="M8 4.5V8l3 1.8"/>',
        'activity'    => '<path d="M1.5 8.5h3l1.5-4 3 7 1.5-4h3.5"/>',
        'median'      => '<path d="M3 3v10M8 1.5v13M13 5v6"/><circle cx="3" cy="6" r="1.3" fill="currentColor" stroke="none"/><circle cx="8" cy="10" r="1.3" fill="currentColor" stroke="none"/><circle cx="13" cy="8.5" r="1.3" fill="currentColor" stroke="none"/>',
        'pie'         => '<circle cx="8" cy="8" r="6"/><path d="M8 8V2a6 6 0 0 1 6 6H8Z" fill="currentColor" stroke="none"/>',
        'rising'      => '<path d="M2 12.5l4-4.5 3 3 5-6"/><path d="M10.5 4.5H14V8"/>',
        'eye'         => '<path d="M1.3 8S3.8 3 8 3s6.7 5 6.7 5-2.5 5-6.7 5-6.7-5-6.7-5Z"/><circle cx="8" cy="8" r="2"/>',
        'eye-off'     => '<path d="M1.3 8S3.8 3 8 3s6.7 5 6.7 5-2.5 5-6.7 5-6.7-5-6.7-5Z"/><circle cx="8" cy="8" r="2"/><path d="M2 2l12 12"/>',
        'trophy'      => '<path d="M5 1.5h6v4.5a3 3 0 0 1-6 0V1.5Z"/><path d="M5 3H2.5a2.5 2.5 0 0 0 2.5 3M11 3h2.5A2.5 2.5 0 0 1 11 6"/><path d="M8 9v2.5M5.5 14.5h5M6.5 11.5h3v3"/>',
        'award'       => '<circle cx="8" cy="6" r="4"/><path d="M5.6 9.3 4.5 14.5l3.5-2 3.5 2-1.1-5.2"/>',
        'bolt'        => '<path d="M9 1.5 3.5 9h4l-1 5.5L12.5 7h-4l.5-5.5Z"/>',
        'bars'        => '<path d="M2 13.5h12"/><rect x="2.5" y="8" width="2.4" height="4.5" rx=".5"/><rect x="6.8" y="4" width="2.4" height="8.5" rx=".5"/><rect x="11.1" y="6" width="2.4" height="6.5" rx=".5"/>',
    ];
}

/** One inline SVG icon. $class is appended to the base "ico" class so callers
 *  can size or colour a specific use (e.g. "ico lg"). Unknown names render an
 *  empty box rather than throwing, so a typo degrades to blank, not to a 500. */
function chrome_icon(string $name, string $class = ''): string
{
    $paths = chrome_icon_paths();
    $cls = 'ico' . ($class !== '' ? ' ' . chrome_h($class) : '');
    return '<svg class="' . $cls . '" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" focusable="false">'
         . ($paths[$name] ?? '') . '</svg>';
}

/** The theme toggle's two glyphs: the moon shows in light mode, the sun in
 *  dark, so the button previews the state you are about to switch to. The
 *  swap is pure CSS (see chrome_icon_css) so it works before any JS runs. */
function chrome_theme_icon(): string
{
    return chrome_icon('moon', 'moon') . chrome_icon('sun', 'sun');
}

/** Sizing and the theme-glyph swap. Included by chrome_css() and inlined by
 *  index.php's own stylesheet. Icons are 1em square and sit on the text
 *  baseline slightly lowered, which is where a 16-grid glyph reads as part
 *  of the word next to it rather than floating above it. */
function chrome_icon_css(): string
{
    return <<<'CSS'
.ico{display:inline-block;width:1em;height:1em;vertical-align:-.16em;flex:none;overflow:visible}
.ico.sun{display:none}
:root[data-theme="dark"] .ico.moon{display:none}
:root[data-theme="dark"] .ico.sun{display:inline-block}
@media (prefers-color-scheme:dark){
  :root:not([data-theme="light"]) .ico.moon{display:none}
  :root:not([data-theme="light"]) .ico.sun{display:inline-block}
}
.topnav a{display:inline-flex;align-items:center;gap:5px}
.topnav a .ico{width:13px;height:13px;opacity:.75}
.topnav a:hover .ico,.topnav a.cur .ico{opacity:1}
.brand{display:inline-flex;align-items:center;gap:7px}
.brand .ico{width:16px;height:16px;color:var(--accent)}
footer.site a{display:inline-flex;align-items:center;gap:5px}
footer.site .ico{width:13px;height:13px;opacity:.75}
footer.site a:hover .ico{opacity:1}
.lbl .ico{width:12px;height:12px;vertical-align:-.2em;margin-right:4px}
.note .ico{width:15px;height:15px;color:var(--accent);margin-right:6px;vertical-align:-.22em}
.note.warn .ico{color:var(--danger)}
.stat .l{display:flex;align-items:center;gap:5px}
.stat .l .ico{width:12px;height:12px;color:var(--muted)}
.crumb .sep{display:inline-block;width:12px;height:12px;vertical-align:-.15em;margin:0 2px;color:var(--rule)}
h2 .ico{width:14px;height:14px;color:var(--accent);margin-right:6px;vertical-align:-.15em}
CSS;
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
CSS
    . "
" . chrome_icon_css();
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
    <a class="brand" href="./"><?php echo chrome_icon('layers'); ?>Cheatsheets<span class="sr"> home</span></a>
    <nav class="topnav" aria-label="Site">
      <a class="hidesm" href="how-its-built.html"><?php echo chrome_icon('hammer'); ?>How it's built</a>
      <a class="hidesm<?php echo $active === 'history' ? ' cur' : ''; ?>" href="history.php"><?php echo chrome_icon('history'); ?>Change history</a>
      <a class="hidesm<?php echo $active === 'popularity' ? ' cur' : ''; ?>" href="popularity.php"><?php echo chrome_icon('chart'); ?>Popularity</a>
      <button class="tbtn" id="themeToggle" type="button" aria-label="Toggle dark mode" title="Toggle theme">
        <?php echo chrome_theme_icon(); ?>
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
    <a href="./"><?php echo chrome_icon('grid'); ?>All cheatsheets</a>
    <a href="how-its-built.html"><?php echo chrome_icon('hammer'); ?>How it's built</a>
    <a href="history.php"><?php echo chrome_icon('history'); ?>Change history</a>
    <a href="popularity.php"><?php echo chrome_icon('chart'); ?>Popularity</a>
    <a href="https://github.com/DavidVeksler/CheatSheets" rel="noopener"><?php echo chrome_icon('git'); ?>GitHub</a>
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
