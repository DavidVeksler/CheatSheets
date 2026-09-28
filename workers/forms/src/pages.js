// Markup and email text ported byte for byte from subscribe.php / confirm.php
// (and chrome_icon() in lib/chrome.php). Change them only together with the
// contract in docs/newsletter.md §2.3.

const SVG_OPEN = (cls) =>
  `<svg class="ico${cls ? " " + cls : ""}" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" focusable="false">`;
export const ICON = {
  envelope: (c) => `${SVG_OPEN(c)}<rect x="1.5" y="3.5" width="13" height="9" rx="1.2"/><path d="m1.5 5 6.5 4.5L14.5 5"/></svg>`,
  warning: (c) =>
    `${SVG_OPEN(c)}<path d="M8 2 1.6 13.2a.6.6 0 0 0 .5.8h11.8a.6.6 0 0 0 .5-.8L8 2Z"/><path d="M8 6.2v3.6"/><circle cx="8" cy="12" r=".75" fill="currentColor" stroke="none"/></svg>`,
  checkCircle: (c) => `${SVG_OPEN(c)}<circle cx="8" cy="8" r="6.3"/><path d="M5 8.2l2 2 4-4.2"/></svg>`,
  arrowLeft: () => `${SVG_OPEN("")}<path d="M14 8H2M6.5 3.5 2 8l4.5 4.5"/></svg>`,
};

// PHP htmlspecialchars($s, ENT_QUOTES, 'UTF-8')
export function h(s) {
  return String(s)
    .replace(/&/g, "&amp;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;");
}

const HEAD = (title) =>
  '<!DOCTYPE html><html lang="en"><head><meta charset="utf-8">' +
  '<meta name="viewport" content="width=device-width, initial-scale=1">' +
  '<meta name="robots" content="noindex">' +
  `<title>${title} · Cheatsheets</title>` +
  '<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.8/dist/css/bootstrap.min.css" rel="stylesheet" ' +
  'integrity="sha384-sRIl4kxILFvY47J16cr9ZwB07vP4J8+LH7qKQnuqkuIAvNWLzeN8tE5YBujZqJLB" crossorigin="anonymous">' +
  "<style>.ico{width:56px;height:56px;display:inline-block}.ico-ok{color:#198754}.ico-warn{color:#dc3545}.ico-mail{color:#0d6efd}.btn .ico{width:1em;height:1em;vertical-align:-.15em;margin-right:.35em}</style></head>" +
  '<body class="d-flex min-vh-100 align-items-center justify-content-center bg-light text-center">';

const BACK = `<a class="btn btn-primary" href="index.php">${ICON.arrowLeft()}Back to the cheatsheets</a>`;

// subscribe.php respond(): the no-JS page.
export function subscribePage(ok, msg) {
  return (
    HEAD(ok ? "Check your inbox" : "Signup error") +
    '<main class="p-4">' +
    `<div class="mb-3">${ok ? ICON.envelope("ico-mail") : ICON.warning("ico-warn")}</div>` +
    `<p class="lead mb-4">${h(msg)}</p>` +
    BACK +
    "</main></body></html>"
  );
}

// confirm.php render()
export function confirmPage(ok, heading, body) {
  return (
    HEAD(h(heading)) +
    '<main class="p-4" style="max-width:32rem;">' +
    `<div class="mb-3">${ok ? ICON.checkCircle("ico-ok") : ICON.warning("ico-warn")}</div>` +
    `<h1 class="h4 mb-2">${h(heading)}</h1>` +
    `<p class="lead mb-4">${h(body)}</p>` +
    BACK +
    "</main></body></html>"
  );
}

// subscribe.php build_confirmation_email()
export function confirmationEmail(confirmUrl) {
  const safeUrl = h(confirmUrl);
  const html =
    '<!DOCTYPE html><html><body style="margin:0;padding:0;background:#f4f4f5;' +
    'font-family:-apple-system,Segoe UI,Roboto,Helvetica,Arial,sans-serif;">' +
    '<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background:#f4f4f5;padding:32px 0;">' +
    '<tr><td align="center">' +
    '<table role="presentation" width="480" cellpadding="0" cellspacing="0" ' +
    'style="background:#ffffff;border-radius:8px;padding:32px;max-width:480px;">' +
    '<tr><td style="font-size:16px;line-height:1.5;color:#1a1a1a;">' +
    '<p style="margin:0 0 16px;">Confirm your subscription to get an email when a new reference ' +
    "ships on cheatsheets.davidveksler.com, or the pipeline changes.</p>" +
    `<p style="margin:0 0 24px;"><a href="${safeUrl}" ` +
    'style="display:inline-block;background:#0d6efd;color:#ffffff;text-decoration:none;' +
    'padding:12px 24px;border-radius:6px;font-weight:600;">Confirm subscription</a></p>' +
    '<p style="margin:0;font-size:13px;color:#6b7280;">If you did not request this, ignore this ' +
    "email — you will not be subscribed unless you click the link above. This link expires in 7 days.</p>" +
    "</td></tr></table></td></tr></table></body></html>";
  const text =
    `Confirm your subscription to cheatsheets.davidveksler.com:\n\n${confirmUrl}\n\n` +
    "If you did not request this, ignore this email — you will not be subscribed unless you " +
    "click the link. This link expires in 7 days.";
  return { html, text };
}

export const MSG = {
  methodNotAllowed: "Method not allowed.",
  unavailable: "Signup is temporarily unavailable. Please try again soon.",
  thanks: "Thanks — check your inbox to confirm your subscription.",
  badEmail: "Please enter a valid email address.",
  sendFailed: "Something went wrong sending the confirmation email. Please try again.",
  // New with the Worker (the PHP endpoint had no rate limit).
  rateLimited: "Too many signup attempts. Please try again later.",
};
