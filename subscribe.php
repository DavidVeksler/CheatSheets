<?php
/**
 * subscribe.php — double opt-in email signup handler.
 *
 * Same-origin endpoint for the signup forms on index.php and how-its-built.html.
 * On a valid POST it (1) appends the address to a gitignored local intake log,
 * (2) emails the visitor a Resend-sent confirmation link (confirm.php mints the
 * sendable-list entry only once that link is clicked — see docs/newsletter.md
 * §2.3), and (3) emails a notification to the site owner via PHP mail(). No
 * third-party scripts on the page, no tracking, no cookies. A honeypot field
 * guards against trivial bots.
 *
 * Personal data is kept OUT of this (public) repository:
 *   - attempted signups are written to .subscribers.jsonl  (gitignored, audit log)
 *   - confirmed addresses live only in .confirmed.jsonl (gitignored, via confirm.php)
 *     and in Resend — this file never treats .subscribers.jsonl as the sendable list
 *   - the notify address comes from the CHEATSHEET_NOTIFY_EMAIL env var, not source
 *   - the Resend key here is RESEND_SENDING_KEY — send-scoped only, never the
 *     full-access key the newsletter pipeline scripts use
 * See AGENTS.md → "Email signup endpoint" and docs/newsletter.md for configuration.
 *
 * Responses:
 *   - AJAX (Accept: application/json) → JSON {ok, message|error}
 *   - plain form post (no JS)         → a tiny self-contained confirmation page
 */

require __DIR__ . '/lib/newsletter.php';
require __DIR__ . '/lib/resend.php';

// ---------------------------------------------------------------- Config ----
header('Cache-Control: no-store'); // form-submission endpoint; never cache the response

$NOTIFY_EMAIL  = getenv('CHEATSHEET_NOTIFY_EMAIL') ?: '';        // set in the server environment
$SENDING_KEY   = getenv('RESEND_SENDING_KEY') ?: '';             // send-scoped Resend key
$FROM_ADDRESS  = getenv('NEWSLETTER_FROM_ADDRESS') ?: 'Cheatsheets <hello@updates.cheatsheets.davidveksler.com>';
$REPLY_TO      = getenv('NEWSLETTER_REPLY_TO') ?: '';            // optional
$STORE_FILE    = __DIR__ . '/.subscribers.jsonl';                // gitignored; intake/audit log only
$HONEYPOT      = 'website';                                      // must stay empty

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
       . '<title>' . ($ok ? 'Check your inbox' : 'Signup error') . ' · Cheatsheets</title>'
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

/** Absolute site origin, sanitized the same way the owner-notification From: header is. */
function site_base_url(): string {
    $scheme = (isset($_SERVER['HTTPS']) && $_SERVER['HTTPS'] === 'on') ? 'https' : 'http';
    $host   = preg_replace('/[^a-z0-9.\-]/i', '', $_SERVER['HTTP_HOST'] ?? 'cheatsheets.davidveksler.com');
    return $scheme . '://' . $host;
}

/** Email-client-safe confirmation email (inline styles, no external assets). */
function build_confirmation_email(string $confirmUrl): array {
    $safeUrl = htmlspecialchars($confirmUrl, ENT_QUOTES, 'UTF-8');
    $html =
        '<!DOCTYPE html><html><body style="margin:0;padding:0;background:#f4f4f5;'
        . 'font-family:-apple-system,Segoe UI,Roboto,Helvetica,Arial,sans-serif;">'
        . '<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background:#f4f4f5;padding:32px 0;">'
        . '<tr><td align="center">'
        . '<table role="presentation" width="480" cellpadding="0" cellspacing="0" '
        . 'style="background:#ffffff;border-radius:8px;padding:32px;max-width:480px;">'
        . '<tr><td style="font-size:16px;line-height:1.5;color:#1a1a1a;">'
        . '<p style="margin:0 0 16px;">Confirm your subscription to get an email when a new reference '
        . 'ships on cheatsheets.davidveksler.com, or the pipeline changes.</p>'
        . '<p style="margin:0 0 24px;"><a href="' . $safeUrl . '" '
        . 'style="display:inline-block;background:#0d6efd;color:#ffffff;text-decoration:none;'
        . 'padding:12px 24px;border-radius:6px;font-weight:600;">Confirm subscription</a></p>'
        . '<p style="margin:0;font-size:13px;color:#6b7280;">If you did not request this, ignore this '
        . 'email — you will not be subscribed unless you click the link above. This link expires in 7 days.</p>'
        . '</td></tr></table></td></tr></table></body></html>';

    $text = "Confirm your subscription to cheatsheets.davidveksler.com:\n\n{$confirmUrl}\n\n"
        . "If you did not request this, ignore this email — you will not be subscribed unless you "
        . "click the link. This link expires in 7 days.";

    return ['html' => $html, 'text' => $text];
}

// ----------------------------------------------------------------- Guards ----
if (($_SERVER['REQUEST_METHOD'] ?? 'GET') !== 'POST') {
    respond(false, 'Method not allowed.', 405);
}

// Fail closed: double opt-in has no path to completion without both of these,
// so don't collect an address we can never confirm. See docs/newsletter.md §5/§9.
$secret = newsletter_secret();
if ($secret === null || $SENDING_KEY === '') {
    respond(false, 'Signup is temporarily unavailable. Please try again soon.', 503);
}

// Honeypot tripped by a bot → pretend success, record nothing.
if (!empty($_POST[$HONEYPOT])) {
    respond(true, 'Thanks — check your inbox to confirm your subscription.');
}

// Validate the email (FILTER_VALIDATE_EMAIL also rejects CRLF, so it's header-safe).
$email = trim((string) ($_POST['email'] ?? ''));
$email = filter_var($email, FILTER_VALIDATE_EMAIL);
if ($email === false || strlen($email) > 254) {
    respond(false, 'Please enter a valid email address.', 422);
}

// ---------------------------------------------------------------- Record ----
// Best-effort local append; never block the user on a write failure. Intake/audit
// log only — the sendable list is .confirmed.jsonl, written by confirm.php.
$record = json_encode(
    ['email' => $email, 'ts' => gmdate('c'), 'src' => substr((string) ($_SERVER['HTTP_REFERER'] ?? ''), 0, 200)],
    JSON_UNESCAPED_SLASHES
) . "\n";
@file_put_contents($STORE_FILE, $record, FILE_APPEND | LOCK_EX);

// ------------------------------------------------------------- Confirmation ----
$token = newsletter_mint_token($email, $secret);
$confirmUrl = site_base_url() . '/confirm.php?p=' . rawurlencode($token['p']) . '&s=' . rawurlencode($token['s']);
$message = build_confirmation_email($confirmUrl);

$sendResult = resend_send_email($SENDING_KEY, [
    'from'     => $FROM_ADDRESS,
    'to'       => $email,
    'subject'  => 'Confirm your subscription',
    'html'     => $message['html'],
    'text'     => $message['text'],
    'reply_to' => $REPLY_TO, // '' is fine — resend_send_email() drops empty values itself
]);

// ---------------------------------------------------------------- Notify ----
// Owner notification fires regardless of confirmation-send outcome — it's a
// heads-up that someone attempted to sign up, not proof they're on the list.
if ($NOTIFY_EMAIL && filter_var($NOTIFY_EMAIL, FILTER_VALIDATE_EMAIL)) {
    $host    = preg_replace('/[^a-z0-9.\-]/i', '', $_SERVER['HTTP_HOST'] ?? 'cheatsheets.davidveksler.com');
    $status  = $sendResult['ok'] ? 'confirmation sent' : ('confirmation FAILED: ' . $sendResult['error']);
    $headers = implode("\r\n", [
        'From: Cheatsheets <no-reply@' . $host . '>',
        'Reply-To: ' . $email,
        'Content-Type: text/plain; charset=utf-8',
        'X-Mailer: cheatsheets-subscribe',
    ]);
    @mail($NOTIFY_EMAIL, 'New cheatsheet subscriber', "New signup attempt: {$email}\nWhen: " . gmdate('c') . "\nStatus: {$status}\n", $headers);
}

if (!$sendResult['ok']) {
    respond(false, 'Something went wrong sending the confirmation email. Please try again.', 502);
}

respond(true, 'Thanks — check your inbox to confirm your subscription.');
