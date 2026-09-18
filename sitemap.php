<?php
// Set content type for XML sitemap
header('Content-Type: text/xml; charset=utf-8');
// Crawlers re-fetch infrequently; an hour of caching is plenty and cuts origin load.
header('Cache-Control: public, max-age=3600');

// Configuration - reuse from index.php
$excludedItems = [
    '.',
    '..',
    'index.php',
    'index2.php',
    'images',
    'LICENSE',
    'README.md',
    'PROMPT.txt',
    'CLAUDE.md',
    'generate-image-previews.py',
    'sitemap.php',
    // Add any other files you want to exclude from sitemap
];

$cheatsheetDir = '.';

// Base URL calculation - same as index.php
$scheme = isset($_SERVER['HTTPS']) && $_SERVER['HTTPS'] === 'on' ? 'https' : 'http';
$host = $_SERVER['HTTP_HOST'];
$scriptName = $_SERVER['SCRIPT_NAME'];
$scriptDir = dirname($scriptName);
$scriptDir = ($scriptDir === '.' || $scriptDir === DIRECTORY_SEPARATOR) ? '' : $scriptDir;
$baseUrl = rtrim($scheme . '://' . $host . $scriptDir, '/') . '/';

// Scan for HTML files
$htmlFiles = [];
try {
    $files = scandir($cheatsheetDir);
    if ($files !== false) {
        foreach ($files as $file) {
            $filePath = rtrim($cheatsheetDir, '/') . '/' . $file;
            if (in_array($file, $excludedItems, true) || !is_file($filePath) || !is_readable($filePath) || !str_ends_with(strtolower($file), '.html')) {
                continue;
            }
            
            // Get file modification time for lastmod
            $lastmod = filemtime($filePath);
            $htmlFiles[] = [
                'url' => $baseUrl . $file,
                'lastmod' => date('c', $lastmod), // ISO 8601 format
                'priority' => '0.8' // High priority for cheatsheets
            ];
        }
    }
} catch (Exception $e) {
    // Continue with empty array if scanning fails
}

// Category hub pages: /<slug> (declared in category-hubs.json) is server-rendered
// by index.php with its own title, description, canonical and JSON-LD, so each
// one is a distinct indexable document. The category list comes from
// catalog.json (the single source of category truth downstream of
// category-map.php); a category with no hub slug falls back to ?cat=, which
// index.php still serves. lastmod is the newest commit touching any sheet in
// the category, not the catalog's build time, so it only moves when the hub's
// content actually changed.
$categoryUrls = [];
$catalogPath = __DIR__ . '/catalog.json';
$hubsPath = __DIR__ . '/category-hubs.json';
$hubs = [];
if (is_readable($hubsPath)) {
    $hubsFile = json_decode((string)@file_get_contents($hubsPath), true);
    if (is_array($hubsFile) && !empty($hubsFile['hubs']) && is_array($hubsFile['hubs'])) $hubs = $hubsFile['hubs'];
}
if (is_readable($catalogPath)) {
    $catalog = json_decode((string)@file_get_contents($catalogPath), true);
    if (is_array($catalog) && !empty($catalog['categories']) && is_array($catalog['categories'])) {
        $latestByCat = [];
        foreach ((is_array($catalog['sheets'] ?? null) ? $catalog['sheets'] : []) as $sheet) {
            if (empty($sheet['category'])) continue;
            $ts = max((int)($sheet['updated'] ?? 0), (int)($sheet['created'] ?? 0));
            $latestByCat[$sheet['category']] = max($latestByCat[$sheet['category']] ?? 0, $ts);
        }
        $hubsMtime = @filemtime($hubsPath) ?: 0;
        foreach ($catalog['categories'] as $category) {
            if (empty($category['name'])) continue;
            $name = (string)$category['name'];
            $slug = isset($hubs[$name]['slug']) ? (string)$hubs[$name]['slug'] : '';
            $lastmod = max($latestByCat[$name] ?? 0, $hubsMtime) ?: time();
            $categoryUrls[] = [
                'url' => $slug !== '' ? $baseUrl . $slug : $baseUrl . '?cat=' . rawurlencode($name),
                'lastmod' => date('c', $lastmod),
                'priority' => '0.7',
                'changefreq' => 'weekly',
            ];
        }
    }
}
$htmlFiles = array_merge($htmlFiles, $categoryUrls);

// Add the main index page
array_unshift($htmlFiles, [
    'url' => $baseUrl,
    'lastmod' => date('c', filemtime(__DIR__ . '/index.php')),
    'priority' => '1.0' // Highest priority for main page
]);

// Output XML sitemap
echo '<?xml version="1.0" encoding="UTF-8"?>' . "\n";
?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
<?php foreach ($htmlFiles as $file): ?>
    <url>
        <loc><?php echo htmlspecialchars($file['url']); ?></loc>
        <lastmod><?php echo htmlspecialchars($file['lastmod']); ?></lastmod>
        <changefreq><?php echo htmlspecialchars($file['changefreq'] ?? 'monthly'); ?></changefreq>
        <priority><?php echo htmlspecialchars($file['priority']); ?></priority>
    </url>
<?php endforeach; ?>
</urlset>