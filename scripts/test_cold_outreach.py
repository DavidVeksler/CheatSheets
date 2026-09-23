#!/usr/bin/env python3
"""Unit tests for scripts/cold_outreach.py. stdlib unittest only, no network (fetch/MX are faked).

Run with:
    python -m unittest scripts.test_cold_outreach -v
"""

from __future__ import annotations

import sys
import unittest
from datetime import date, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import cold_outreach as co  # noqa: E402

TODAY = date.today().isoformat()
PAGE = "linux-server-hardening.html"
TARGET = co.SITE + PAGE


def fake_fetch(pages: dict):
    def fetch(url, timeout=20):
        return (200, pages[url]) if url in pages else (404, "")
    return fetch


def mx_ok(domain):
    return "mx"


def prospect(**kw):
    p = {"id": "co-0001", "state": "queued", "org": "Example Homelab", "name": "Dana Reyes",
         "page": PAGE, "type": "article", "email": "dana@homelab.example",
         "evidence": {"kind": "published_personal_own_site", "source_url": "https://homelab.example/about",
                      "checked": TODAY},
         "outreach": {}}
    p.update(kw)
    return p


class ScoreTests(unittest.TestCase):
    def test_published_found_scores_high(self):
        f = fake_fetch({"https://homelab.example/about": '<a href="mailto:dana@homelab.example">mail</a>'})
        conf, _ = co.score(prospect(), [], fetch=f, mx=mx_ok)
        self.assertEqual(conf, 0.95)

    def test_published_not_found_blocks(self):
        f = fake_fetch({"https://homelab.example/about": "<p>no address here</p>"})
        conf, reasons = co.score(prospect(), [], fetch=f, mx=mx_ok)
        self.assertEqual(conf, 0.0)
        self.assertIn("rendered_only", reasons[-1])

    def test_rendered_only_is_penalised_but_passes(self):
        p = prospect()
        p["evidence"]["rendered_only"] = True
        conf, _ = co.score(p, [], fetch=fake_fetch({}), mx=mx_ok)
        self.assertEqual(conf, 0.70)

    def test_cloudflare_obfuscated_address_is_found(self):
        email = "dana@homelab.example"
        key = 0x42
        token = f"{key:02x}" + "".join(f"{ord(c) ^ key:02x}" for c in email)
        page = f'<a href="/cdn-cgi/l/email-protection#{token}">[email protected]</a>'
        self.assertTrue(co.page_has_email(page, email))
        self.assertTrue(co.page_has_email("write to dana [at] homelab [dot] example", email))
        self.assertTrue(co.page_has_email("email dana @ homelab . example", email))

    def test_pattern_single_is_just_above_threshold(self):
        p = prospect(evidence={"kind": "pattern_single", "checked": TODAY,
                               "examples": [{"email": "sam@homelab.example", "source_url": "https://homelab.example/team"}]})
        f = fake_fetch({"https://homelab.example/team": "sam@homelab.example"})
        conf, _ = co.score(p, [], fetch=f, mx=mx_ok)
        self.assertEqual(conf, 0.55)
        self.assertGreater(conf, co.THRESHOLD)

    def test_pattern_multi_with_one_example_downgrades(self):
        p = prospect(evidence={"kind": "pattern_multi", "checked": TODAY,
                               "examples": [{"email": "sam@homelab.example", "source_url": "https://homelab.example/team"},
                                            {"email": "lee@homelab.example", "source_url": "https://homelab.example/gone"}]})
        f = fake_fetch({"https://homelab.example/team": "sam@homelab.example"})
        conf, _ = co.score(p, [], fetch=f, mx=mx_ok)
        self.assertEqual(conf, 0.55)

    def test_guesses_never_pass(self):
        for kind in ("unpublished_generic", "common_pattern_guess"):
            conf, _ = co.score(prospect(evidence={"kind": kind, "checked": TODAY}), [], fetch=fake_fetch({}), mx=mx_ok)
            self.assertLessEqual(conf, co.THRESHOLD, kind)

    def test_mx_failure_fails_closed(self):
        f = fake_fetch({"https://homelab.example/about": "dana@homelab.example"})
        conf, _ = co.score(prospect(), [], fetch=f, mx=lambda dom: "error")
        self.assertEqual(conf, 0.0)

    def test_stale_evidence_blocks(self):
        p = prospect()
        p["evidence"]["checked"] = (date.today() - timedelta(days=45)).isoformat()
        conf, _ = co.score(p, [], fetch=fake_fetch({}), mx=mx_ok)
        self.assertEqual(conf, 0.0)

    def test_calibration_caps_a_kind_that_bounces(self):
        sent = [prospect(id=f"co-00{i}", email=f"x{i}@a{i}.example", evidence={"kind": "pattern_single"},
                         outreach={"sent": TODAY, "outcome": "bounced" if i < 3 else None}) for i in range(4)]
        p = prospect(evidence={"kind": "pattern_single", "checked": TODAY,
                               "examples": [{"email": "sam@homelab.example", "source_url": "https://homelab.example/team"}]})
        f = fake_fetch({"https://homelab.example/team": "sam@homelab.example"})
        conf, _ = co.score(p, sent, fetch=f, mx=mx_ok)
        self.assertEqual(conf, 0.25)


class RenderTests(unittest.TestCase):
    BODY = ("Hi Dana,\n\nYour 2021 post on locking down a VPS links a hardening checklist that now 404s.\n\n"
            "I maintain a phase-by-phase version with copy-paste commands:\n\n"
            "- SSH keys and daemon settings\n- ufw default-deny and fail2ban\n\n"
            f"[Linux server hardening checklist]({TARGET}#phase1)\n\n"
            "Would it be a fit as a replacement link?")

    def test_html_and_plain_twins(self):
        frag = co.to_html_fragment(self.BODY)
        self.assertIn(f'href="{TARGET}#phase1"', frag)
        self.assertIn("<ul", frag)
        self.assertIn("cheatsheets.davidveksler.com</a>", frag)
        plain = co.to_plain(self.BODY)
        self.assertIn(f"Linux server hardening checklist ({TARGET}#phase1)", plain)
        self.assertTrue(plain.rstrip().endswith("https://cheatsheets.davidveksler.com/"))

    def test_escaping(self):
        self.assertIn("&lt;script&gt;", co.inline_html("<script>"))

    def _gate(self, body, subject="Your VPS hardening post", p=None):
        p = p or prospect()
        data = {"prospects": [p]}
        pages = {"https://homelab.example/about": "dana@homelab.example", TARGET: '<h2 id="phase1">x</h2>'}
        original = co.catalog_anchors
        co.catalog_anchors = lambda f: {"phase1", "quickref"}
        try:
            return co.gate({"id": p["id"], "touch": "first", "subject": subject, "body": body}, p, data,
                           fetch=fake_fetch(pages), mx=mx_ok)
        finally:
            co.catalog_anchors = original

    def test_clean_draft_passes(self):
        self.assertEqual(self._gate(self.BODY), [])

    def test_gate_catches_voice_and_links(self):
        errs = " | ".join(self._gate(self.BODY.replace("Would", "Would — SEO backlink") + "\n\n{{PS}}"))
        self.assertIn("dash", errs)
        self.assertIn("spam", errs)
        self.assertIn("placeholder", errs)
        errs = " | ".join(self._gate("Hi Dana, see https://cheatsheets.davidveksler.com/judo.html"))
        self.assertIn("must link the target page", errs)
        errs = " | ".join(self._gate(self.BODY.replace(TARGET, TARGET + "?utm_source=x")))
        self.assertIn("tracking", errs)

    def test_gate_blocks_low_confidence(self):
        p = prospect(evidence={"kind": "unpublished_generic", "checked": TODAY})
        self.assertTrue(any("confidence" in e for e in self._gate(self.BODY, p=p)))


if __name__ == "__main__":
    unittest.main()
