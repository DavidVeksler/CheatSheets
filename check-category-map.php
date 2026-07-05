<?php
// Checks that every cheatsheet .html file in this directory has a category-map.php
// entry, and flags stale entries that point at files which no longer exist.
//
// Usage: php check-category-map.php
// Exit code: 0 if in sync, 1 if unmapped or stale entries were found.

$root = __DIR__;
$categoryMap = require $root . '/category-map.php';

// Mirrors index.php's $excludedItems: files present on disk but not shown as
// cheatsheet cards, so they're allowed to be absent from category-map.php.
$excludedItems = [
    'index.php',
    'images',
    'LICENSE',
    'README.md',
    'PROMPT.txt',
    'etz-chaim-tree-of-life.html',
];

$files = scandir($root);
if ($files === false) {
    fwrite(STDERR, "Could not scan directory: $root\n");
    exit(1);
}

$allHtml = [];
foreach ($files as $file) {
    $path = $root . '/' . $file;
    if (!is_file($path) || !str_ends_with(strtolower($file), '.html')) {
        continue;
    }
    $allHtml[$file] = true;
}

$siteHtml = array_diff_key($allHtml, array_flip($excludedItems));

$unmapped = array_values(array_diff(array_keys($siteHtml), array_keys($categoryMap)));
$stale = array_values(array_diff(array_keys($categoryMap), array_keys($allHtml)));

sort($unmapped);
sort($stale);

$exitCode = 0;

if ($unmapped) {
    $exitCode = 1;
    echo "Unmapped .html files (add to category-map.php):\n";
    foreach ($unmapped as $f) {
        echo "  - $f\n";
    }
} else {
    echo "All .html files are mapped.\n";
}

if ($stale) {
    $exitCode = 1;
    echo "\nStale category-map.php entries (file no longer exists):\n";
    foreach ($stale as $f) {
        echo "  - $f\n";
    }
}

exit($exitCode);
