<?php
/**
 * lib/newsletter.php — double opt-in token + intake-queue helpers shared by
 * subscribe.php and confirm.php. See docs/newsletter.md §2.3.
 *
 * The confirm link carries a stateless HMAC token (no database, nothing to
 * expire on a cron): payload = base64url(email) . "." . issued_unix_ts,
 * signed with NEWSLETTER_TOKEN_SECRET. Verification is constant-time and
 * never distinguishes "bad signature" from "expired" from "already
 * confirmed" in what it tells the caller — callers decide their own
 * user-facing copy for each case, but must not use timing or response
 * shape to let an attacker probe which addresses are on the list.
 */

const NEWSLETTER_TOKEN_TTL = 7 * 24 * 60 * 60; // 7 days

/** The signing secret, or null if the server isn't configured for it yet. */
function newsletter_secret(): ?string
{
    $secret = getenv('NEWSLETTER_TOKEN_SECRET') ?: '';
    return $secret !== '' ? $secret : null;
}

function newsletter_b64url_encode(string $data): string
{
    return rtrim(strtr(base64_encode($data), '+/', '-_'), '=');
}

/** @return string|false decoded bytes, or false on malformed input */
function newsletter_b64url_decode(string $data)
{
    $remainder = strlen($data) % 4;
    if ($remainder) {
        $data .= str_repeat('=', 4 - $remainder);
    }
    return base64_decode(strtr($data, '-_', '+/'), true);
}

/** Mint {p, s} for a confirm link: confirm.php?p=<p>&s=<s> */
function newsletter_mint_token(string $email, string $secret): array
{
    $payload = newsletter_b64url_encode($email) . '.' . time();
    $sig = newsletter_b64url_encode(hash_hmac('sha256', $payload, $secret, true));
    return ['p' => $payload, 's' => $sig];
}

/**
 * Verify a confirm token and return the confirmed email, or null on any
 * failure (bad signature, malformed payload, expired). hash_equals() keeps
 * the signature check constant-time.
 */
function newsletter_verify_token(string $payload, string $sig, string $secret): ?string
{
    $expectedSig = newsletter_b64url_encode(hash_hmac('sha256', $payload, $secret, true));
    if (!hash_equals($expectedSig, $sig)) {
        return null;
    }

    $parts = explode('.', $payload, 2);
    if (count($parts) !== 2) {
        return null;
    }
    [$encEmail, $ts] = $parts;

    if (!ctype_digit($ts) || (time() - (int) $ts) > NEWSLETTER_TOKEN_TTL) {
        return null;
    }

    $email = newsletter_b64url_decode($encEmail);
    if ($email === false) {
        return null;
    }

    $email = filter_var($email, FILTER_VALIDATE_EMAIL);
    return $email !== false ? $email : null;
}

/** Best-effort append; a write failure must never block the caller's response. */
function newsletter_append_jsonl(string $file, array $record): void
{
    $line = json_encode($record, JSON_UNESCAPED_SLASHES) . "\n";
    @file_put_contents($file, $line, FILE_APPEND | LOCK_EX);
}

/**
 * Linear scan for an exact (case-insensitive) email match. Queues here are
 * small (single-digit thousands at most); a full scan per confirm click is
 * cheap and avoids a second moving part (index/db) for a stateless design.
 */
function newsletter_jsonl_contains_email(string $file, string $email): bool
{
    if (!is_readable($file)) {
        return false;
    }
    $needle = strtolower($email);
    $handle = @fopen($file, 'r');
    if ($handle === false) {
        return false;
    }
    try {
        while (($line = fgets($handle)) !== false) {
            $record = json_decode($line, true);
            if (is_array($record) && isset($record['email']) && strtolower((string) $record['email']) === $needle) {
                return true;
            }
        }
    } finally {
        fclose($handle);
    }
    return false;
}
