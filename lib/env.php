<?php
/**
 * lib/env.php — loads the server-local .newsletter.env file into the
 * process environment via putenv(), if present.
 *
 * Why this exists: subscribe.php and confirm.php read their secrets with
 * getenv(), and docs/newsletter.md originally assumed those would be set in
 * the site's php-fpm pool (env[KEY] = value). This server has no dedicated
 * pool for cheatsheets.davidveksler.com — it shares WordOps' default `www`
 * pool with other sites — so a pool-level env[] entry would leak these
 * secrets to every other site on that pool. A local, gitignored file next
 * to the code is the same shape as .cloudflare.env (already used by
 * refresh-popularity.py) and keeps the secret scoped to this one site.
 *
 * Existing environment variables always win (getenv($key) !== false is
 * checked before putenv()), so a real php-fpm pool env[] set up later, or a
 * value exported for local testing, silently takes precedence without any
 * code change here.
 */

function load_local_env_file(string $path): void
{
    if (!is_readable($path)) {
        return;
    }
    $lines = file($path, FILE_IGNORE_NEW_LINES | FILE_SKIP_EMPTY_LINES);
    if ($lines === false) {
        return;
    }
    foreach ($lines as $line) {
        $line = trim($line);
        if ($line === '' || $line[0] === '#' || strpos($line, '=') === false) {
            continue;
        }
        [$key, $value] = explode('=', $line, 2);
        $key = trim($key);
        $value = trim(trim($value), "\"'");
        if ($key !== '' && getenv($key) === false) {
            putenv($key . '=' . $value);
        }
    }
}

load_local_env_file(__DIR__ . '/../.newsletter.env');
