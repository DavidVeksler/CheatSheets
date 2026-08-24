<?php
/**
 * lib/resend.php — minimal Resend API client.
 *
 * Sending-only. This file is loaded by subscribe.php with RESEND_SENDING_KEY,
 * a send-scoped key. The full-access RESEND_API_KEY (contacts, broadcasts)
 * never runs on the web server — see docs/newsletter.md §2.2.
 */

/**
 * Send a single transactional email via Resend's /emails endpoint.
 *
 * @param string $apiKey Resend API key (send-scoped).
 * @param array{from:string,to:string,subject:string,html:string,text?:string,reply_to?:string} $email
 * @return array{ok:bool,id?:string,error?:string}
 */
function resend_send_email(string $apiKey, array $email): array
{
    $payload = array_filter(
        [
            'from'     => $email['from']     ?? null,
            'to'       => $email['to']       ?? null,
            'subject'  => $email['subject']  ?? null,
            'html'     => $email['html']     ?? null,
            'text'     => $email['text']     ?? null,
            'reply_to' => $email['reply_to'] ?? null,
        ],
        static fn($v) => $v !== null && $v !== ''
    );

    $ch = curl_init('https://api.resend.com/emails');
    curl_setopt_array($ch, [
        CURLOPT_RETURNTRANSFER => true,
        CURLOPT_POST           => true,
        CURLOPT_HTTPHEADER     => [
            'Authorization: Bearer ' . $apiKey,
            'Content-Type: application/json',
        ],
        CURLOPT_POSTFIELDS     => json_encode($payload, JSON_UNESCAPED_SLASHES),
        CURLOPT_TIMEOUT        => 10,
        CURLOPT_CONNECTTIMEOUT => 5,
    ]);
    $body = curl_exec($ch);
    $code = curl_getinfo($ch, CURLINFO_HTTP_CODE);
    $curlErr = curl_error($ch);
    curl_close($ch);

    if ($body === false) {
        return ['ok' => false, 'error' => 'curl: ' . $curlErr];
    }

    $json = json_decode($body, true);
    if ($code >= 200 && $code < 300 && is_array($json) && isset($json['id'])) {
        return ['ok' => true, 'id' => (string) $json['id']];
    }

    $msg = is_array($json) && isset($json['message']) ? (string) $json['message'] : ('HTTP ' . $code);
    return ['ok' => false, 'error' => $msg];
}
