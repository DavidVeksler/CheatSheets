<?php
/**
 * prerender.php: render one PHP page to stdout the way nginx + php-fpm served it,
 * for the Cloudflare Workers build (scripts/build_site.py). One process per page.
 *
 *   php scripts/prerender.php <page.php> <request-uri> [<GET query string>]
 *
 * <request-uri> is what the visitor asked for ("/", "/radio", "/popularity.php");
 * the query string is what the page sees in $_GET (nginx's category-hubs.conf
 * rewrote /radio to index.php?hub=radio, so a hub renders with "hub=radio").
 * Fails (exit 1) if the page sets a non-200 status or a Location header, so a
 * build never publishes an error page as content.
 * Spec: docs/specs/cloudflare-migration.md §2.1.
 */

if ($argc < 3) {
    fwrite(STDERR, "usage: php scripts/prerender.php <page.php> <request-uri> [query]\n");
    exit(2);
}
[$_, $page, $uri] = $argv;
$query = $argv[3] ?? '';

$root = getcwd();
$file = $root . '/' . $page;
if (!preg_match('/^[a-z0-9_-]+\.php$/', $page) || !is_file($file)) {
    fwrite(STDERR, "prerender: no such page: $page\n");
    exit(2);
}

date_default_timezone_set('UTC');
$_GET = [];
parse_str($query, $_GET);
$_POST = [];
$_COOKIE = [];
$_REQUEST = $_GET;
$_SERVER['HTTPS'] = 'on';
$_SERVER['HTTP_HOST'] = 'cheatsheets.davidveksler.com';
$_SERVER['SERVER_NAME'] = 'cheatsheets.davidveksler.com';
$_SERVER['REQUEST_METHOD'] = 'GET';
$_SERVER['REQUEST_URI'] = $uri;
$_SERVER['SCRIPT_NAME'] = '/' . $page;
$_SERVER['PHP_SELF'] = '/' . $page;
$_SERVER['QUERY_STRING'] = $query;

// A page that redirects or errors calls exit(); catch that here and fail loudly.
register_shutdown_function(function () {
    $status = http_response_code();
    $location = null;
    foreach (headers_list() as $h) {
        if (stripos($h, 'Location:') === 0) $location = trim(substr($h, 9));
    }
    if (($status !== false && $status !== 200) || $location !== null) {
        fwrite(STDERR, "prerender: page answered " . var_export($status, true)
            . ($location ? " Location: $location" : '') . "\n");
        exit(1);
    }
});

chdir($root);
require $file;
