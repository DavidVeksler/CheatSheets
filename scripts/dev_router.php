<?php
/**
 * Router for PHP's built-in server, so a local `php -S` behaves like the
 * production nginx config in conf/nginx/category-hubs.conf:
 *
 *   php -S 127.0.0.1:8000 scripts/dev_router.php
 *
 * Real files are served as-is (return false). A single-segment extensionless
 * path (/ai-safety) is handed to index.php with ?hub=<slug>, and the
 * trailing-slash spelling 301s to the bare slug. Everything else 404s like
 * nginx's `try_files $uri $uri/ =404` would. scripts/_devserver.py uses this.
 */
$root = dirname(__DIR__);
$path = (string)parse_url((string)($_SERVER['REQUEST_URI'] ?? '/'), PHP_URL_PATH);
if ($path === '/' || $path === '') {
    $_SERVER['SCRIPT_NAME'] = '/index.php';
    require $root . '/index.php';
    return true;
}
if (is_file($root . $path)) return false;
if (preg_match('#^/([a-z0-9][a-z0-9-]*)/$#', $path, $m)) {
    header('Location: /' . $m[1], true, 301);
    return true;
}
if (preg_match('#^/([a-z0-9][a-z0-9-]*)$#', $path, $m)) {
    $_GET['hub'] = $m[1];
    $_SERVER['SCRIPT_NAME'] = '/index.php';
    require $root . '/index.php';
    return true;
}
http_response_code(404);
echo '404 Not Found';
return true;
