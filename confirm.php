<?php
/**
 * confirm.php — double opt-in landing page for the newsletter.
 *
 * See docs/newsletter.md §2.3. Verifies the HMAC token minted by
 * subscribe.php; on success appends the address to the sendable queue
 * (.confirmed.jsonl, gitignored — the newsletter routine pulls from this,
 * never from .subscribers.jsonl directly) and shows a confirmation page.
 * Re-confirming an already-confirmed address is a no-op that still shows
 * success: the response never reveals whether an address was new or
 * already on the list.
 */

require __DIR__ . '/lib/newsletter.php';

header('Cache-Control: no-store');
header('Content-Type: text/html; charset=utf-8');

/** Render a small self-contained confirmation/error page and exit. */
function render(bool $ok, string $heading, string $body): void
{
    http_response_code($ok ? 200 : 400);
    $h = htmlspecialchars($heading, ENT_QUOTES, 'UTF-8');
    $b = htmlspecialchars($body, ENT_QUOTES, 'UTF-8');
    echo '<!DOCTYPE html><html lang="en"><head><meta charset="utf-8">'
       . '<meta name="viewport" content="width=device-width, initial-scale=1">'
       . '<meta name="robots" content="noindex">'
       . '<title>' . $h . ' · Cheatsheets</title>'
       . '<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.8/dist/css/bootstrap.min.css" rel="stylesheet" '
       . 'integrity="sha384-sRIl4kxILFvY47J16cr9ZwB07vP4J8+LH7qKQnuqkuIAvNWLzeN8tE5YBujZqJLB" crossorigin="anonymous"></head>'
       . '<body class="d-flex min-vh-100 align-items-center justify-content-center bg-light text-center">'
       . '<main class="p-4" style="max-width:32rem;">'
       . '<div class="display-5 mb-3">' . ($ok ? '&#10003;' : '&#9888;&#65039;') . '</div>'
       . '<h1 class="h4 mb-2">' . $h . '</h1>'
       . '<p class="lead mb-4">' . $b . '</p>'
       . '<a class="btn btn-primary" href="index.php">Back to the cheatsheets</a>'
       . '</main></body></html>';
    exit;
}

$secret = newsletter_secret();
if ($secret === null) {
    render(false, 'Signup error', 'Newsletter confirmation is not configured right now. Please try again later.');
}

$payload = (string) ($_GET['p'] ?? '');
$sig     = (string) ($_GET['s'] ?? '');
if ($payload === '' || $sig === '') {
    render(false, 'Invalid link', 'This confirmation link is missing its token.');
}

$email = newsletter_verify_token($payload, $sig, $secret);
if ($email === null) {
    render(false, 'Link expired or invalid', 'This confirmation link is no longer valid. Sign up again on the homepage to get a new one.');
}

$store = __DIR__ . '/.confirmed.jsonl';
if (!newsletter_jsonl_contains_email($store, $email)) {
    newsletter_append_jsonl($store, ['email' => $email, 'ts' => gmdate('c')]);
}

render(true, 'Subscribed', "You're confirmed. You'll get an email when a new reference ships or the pipeline changes — no spam, unsubscribe anytime.");
