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

// Category landing pages: ?cat=<Category> is server-rendered by index.php with
// its own title, description, canonical and JSON-LD, so each one is a distinct
// indexable document. The list comes from catalog.json (the single source of
// category truth downstream of category-map.php); if the catalog is missing the
// sitemap simply omits them rather than guessing.
$categoryUrls = [];
$catalogPath = __DIR__ . '/catalog.json';
if (is_readable($catalogPath)) {
    $catalog = json_decode((string)@file_get_contents($catalogPath), true);
    if (is_array($catalog) && !empty($catalog['categories']) && is_array($catalog['categories'])) {
        $catalogMtime = @filemtime($catalogPath) ?: time();
        foreach ($catalog['categories'] as $category) {
            if (empty($category['name'])) continue;
            $categoryUrls[] = [
                'url' => $baseUrl . '?cat=' . rawurlencode((string)$category['name']),
                'lastmod' => date('c', $catalogMtime),
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