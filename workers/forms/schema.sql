-- D1 schema for the newsletter forms Worker (workers/forms/). Apply once from this
-- directory: npx wrangler d1 execute cheatsheets-davidveksler-com-forms --remote --file schema.sql
-- with CLOUDFLARE_D1_TOKEN from ~/Projects/.cloudflare.env (cf-static-kit runbook step 4).
-- Holds subscribers' email addresses: never print rows; query counts.

-- Intake / audit log, was .subscribers.jsonl (subscribe.php). Not the sendable list.
CREATE TABLE IF NOT EXISTS subscribers (
  id    INTEGER PRIMARY KEY,
  ts    TEXT    NOT NULL,   -- PHP gmdate('c'), e.g. 2026-09-12T01:27:00+00:00
  email TEXT    NOT NULL,
  src   TEXT                -- Referer, max 200 chars; NULL when the old row had no src
);
CREATE INDEX IF NOT EXISTS subscribers_ts ON subscribers (ts);

-- Sendable queue, was .confirmed.jsonl (confirm.php). One row per address.
CREATE TABLE IF NOT EXISTS confirmed (
  id    INTEGER PRIMARY KEY,
  ts    TEXT    NOT NULL,
  email TEXT    NOT NULL
);
CREATE UNIQUE INDEX IF NOT EXISTS confirmed_email ON confirmed (email COLLATE NOCASE);

-- Rate-limit ledger (kit template): pruned to 24 h by the Worker.
CREATE TABLE IF NOT EXISTS hits (
  ts      INTEGER NOT NULL,
  ip_hash TEXT    NOT NULL,
  kind    TEXT    NOT NULL
);
CREATE INDEX IF NOT EXISTS hits_lookup ON hits (ip_hash, kind, ts);
