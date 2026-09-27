#!/usr/bin/env python3
"""Unit tests for scripts/referrer_accumulate.py (stdlib only, synthetic data, no logs).

Run with:
    python3 -m unittest scripts.test_referrer_accumulate -v
"""

from __future__ import annotations

import sys
import unittest
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import referrer_accumulate as ra  # noqa: E402

D1, D2 = date(2026, 9, 25), date(2026, 9, 26)


class CleanSourceTests(unittest.TestCase):
    def test_public_host_kept_lowercase(self):
        self.assertEqual(ra.clean_source("WWW.Google.com"), "www.google.com")

    def test_private_hosts_collapse(self):
        for h in ("10.0.0.5", "localhost", "wiki.corp", "intranet", "[::1]", "nas.local"):
            self.assertEqual(ra.clean_source(h), "(private network)", h)

    def test_utm_tags_sanitised(self):
        self.assertEqual(ra.clean_source("utm:ChatGPT.com"), "utm:chatgpt.com")
        self.assertEqual(ra.clean_source("utm:<script>"), "utm:(other)")

    def test_empty_source_stays_empty(self):
        self.assertEqual(ra.clean_source(""), "")


class AggregateTests(unittest.TestCase):
    def test_counts_channels_sources_and_landings_per_day(self):
        days = ra.aggregate([
            (D1, "Search engine", "www.google.com", "/a.html"),
            (D1, "Search engine", "www.google.com", "/b.html"),
            (D1, "Direct / no referrer", "", "/a.html"),
            (D1, "Internal", "cheatsheets.davidveksler.com", "/b.html"),
            (D2, "AI assistant", "utm:chatgpt.com", "/a.html"),
        ])
        d1 = days["2026-09-25"]
        self.assertEqual(d1["channels"], {"Search engine": 2, "Direct / no referrer": 1, "Internal": 1})
        self.assertEqual(d1["sources"], {"Search engine": {"www.google.com": 2}})
        self.assertEqual(d1["landing"]["Direct / no referrer"], {"/a.html": 1})
        self.assertNotIn("Internal", d1["landing"])
        self.assertEqual(days["2026-09-26"]["sources"], {"AI assistant": {"utm:chatgpt.com": 1}})

    def test_caps_long_tails(self):
        events = [(D1, "Other site", f"s{i}.example.com", f"/p{i}.html") for i in range(100)]
        rec = ra.aggregate(events)["2026-09-25"]
        self.assertEqual(len(rec["sources"]["Other site"]), ra.SOURCE_CAP)
        self.assertEqual(len(rec["landing"]["Other site"]), ra.LANDING_CAP)
        self.assertEqual(rec["channels"]["Other site"], 100)


class MergeTests(unittest.TestCase):
    def test_adds_only_new_complete_days(self):
        store = {"days": {"2026-09-25": {"channels": {"Search engine": 9}}}}
        new = {"2026-09-25": {"channels": {"Search engine": 1}},
               "2026-09-26": {"channels": {"Reddit": 2}},
               "2026-09-27": {"channels": {"Reddit": 3}}}
        store, added = ra.merge(store, new, date(2026, 9, 27))
        self.assertEqual(added, ["2026-09-26"])
        self.assertEqual(store["days"]["2026-09-25"]["channels"], {"Search engine": 9})
        self.assertNotIn("2026-09-27", store["days"])

    def test_prunes_beyond_retention(self):
        store = {"days": {"2019-01-01": {}, "2026-09-25": {}}}
        store, _ = ra.merge(store, {}, date(2026, 9, 27))
        self.assertEqual(list(store["days"]), ["2026-09-25"])


if __name__ == "__main__":
    unittest.main()
