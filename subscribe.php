<?php
/**
 * subscribe.php — minimal, privacy-respecting email signup handler.
 *
 * Same-origin endpoint for the signup forms on index.php and how-its-built.html.
 * On a valid POST it (1) appends the address to a gitignored local log and
 * (2) emails a notification to the site owner via PHP mail(). No third-party
 * services, no tracking, no cookies. A honeypot field guards against trivial bots.
 *
 * Personal data is kept OUT of this (public) repository:
 *   - subscribers are written to .subscribers.jsonl  (gitignored)
 *   - the notify address comes from the CHEATSHEET_NOTIFY_EMAIL env var, not source
 * See AGENTS.md → "Email signup endpoint" for configuration.
 *
 * Responses:
 *   - AJAX (Accept: application/json) → JSON {ok, message|error}
 *   - plain form post (no JS)         → a tiny self-contained confirmation page
 */

// ---------------------------------------------------------------- Config ----
$NOTIFY_EMAIL = getenv('CHEATSHEET_NOTIFY_EMAIL') ?: '';   // set in the server environment
$STORE_FILE   = __DIR__ . '/.subscribers.jsonl';           // gitignored; the source of truth
$HONEYPOT     = 'website';                                 // must stay empty

// --------------------------------------------------------------- Helpers ----
function wants_json(): bool {
    $accept = $_SERVER['HTTP_ACCEPT'] ?? '';
    $xrw    = $_SERVER['HTTP_X_REQUESTED_WITH'] ?? '';
    return stripos($accept, 'application/json') !== false || $xrw !== '';
}

function respond(bool $ok, string $msg, int $code = 200): void {
    http_response_code($code);
    if (wants_json()) {
        header('Content-Type: application/json; charset=utf-8');
        echo json_encode($ok ? ['ok' => true, 'message' => $msg] : ['ok' => false, 'error' => $msg]);
        exit;
    }
    // No-JS fallback: a small standalone confirmation page (SRI-pinned, matches the site).
    header('Content-Type: text/html; charset=utf-8');
    $safe = htmlspecialchars($msg, ENT_QUOTES, 'UTF-8');
    echo '<!DOCTYPE html><html lang="en"><head><meta charset="utf-8">'
       . '<meta name="viewport" content="width=device-width, initial-scale=1">'
       . '<meta name="robots" content="noindex">'
       . '<title>' . ($ok ? 'Subscribed' : 'Signup error') . ' · Cheatsheets</title>'
       . '<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.8/dist/css/bootstrap.min.css" rel="stylesheet" '
       . 'integrity="sha384-sRIl4kxILFvY47J16cr9ZwB07vP4J8+LH7qKQnuqkuIAvNWLzeN8tE5YBujZqJLB" crossorigin="anonymous"></head>'
       . '<body class="d-flex min-vh-100 align-items-center justify-content-center bg-light text-center">'
       . '<main class="p-4">'
       . '<div class="display-5 mb-3">' . ($ok ? '&#10003;' : '&#9888;&#65039;') . '</div>'
       . '<p class="lead mb-4">' . $safe . '</p>'
       . '<a class="btn btn-primary" href="index.php">Back to the cheatsheets</a>'
       . '</main></body></html>';
    exit;
}

// ----------------------------------------------------------------- Guards ----
if (($_SERVER['REQUEST_METHOD'] ?? 'GET') !== 'POST') {
    respond(false, 'Method not allowed.', 405);
}

// Honeypot tripped by a bot → pretend success, record nothing.
if (!empty($_POST[$HONEYPOT])) {
    respond(true, 'Thanks — you’re on the list.');
}

// Validate the email (FILTER_VALIDATE_EMAIL also rejects CRLF, so it's header-safe).
$email = trim((string) ($_POST['email'] ?? ''));
$email = filter_var($email, FILTER_VALIDATE_EMAIL);
if ($email === false || strlen($email) > 254) {
    respond(false, 'Please enter a valid email address.', 422);
}

// ---------------------------------------------------------------- Record ----
// Best-effort local append; never block the user on a write failure.
$record = json_encode(
    ['email' => $email, 'ts' => gmdate('c'), 'src' => substr((string) ($_SERVER['HTTP_REFERER'] ?? ''), 0, 200)],
    JSON_UNESCAPED_SLASHES
) . "\n";
@file_put_contents($STORE_FILE, $record, FILE_APPEND | LOCK_EX);

// ---------------------------------------------------------------- Notify ----
// Only attempts mail() when an owner address is configured in the environment.
if ($NOTIFY_EMAIL && filter_var($NOTIFY_EMAIL, FILTER_VALIDATE_EMAIL)) {
    $host    = preg_replace('/[^a-z0-9.\-]/i', '', $_SERVER['HTTP_HOST'] ?? 'cheatsheets.davidveksler.com');
    $headers = implode("\r\n", [
        'From: Cheatsheets <no-reply@' . $host . '>',
        'Reply-To: ' . $email,
        'Content-Type: text/plain; charset=utf-8',
        'X-Mailer: cheatsheets-subscribe',
    ]);
    @mail($NOTIFY_EMAIL, 'New cheatsheet subscriber', "New signup: {$email}\nWhen: " . gmdate('c') . "\n", $headers);
}

respond(true, 'Thanks — you’re on the list.');
