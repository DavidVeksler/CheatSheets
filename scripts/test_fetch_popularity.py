#!/usr/bin/env python3
"""Unit tests for fetch-popularity.py's pure accumulate_daily_history step.

stdlib unittest only, synthetic counts only — never calls the Cloudflare API
(fetch-popularity.py needs CLOUDFLARE_API_TOKEN, which is not available in
this environment; see docs/index-explorer.md's OG/history section).

Run with:
    .venv/bin/python3 -m unittest scripts.test_fetch_popularity -v
"""

from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# fetch-popularity.py has a hyphen in its filename, so it can't be imported
# with a normal `import` statement; load it by path instead.
_spec = importlib.util.spec_from_file_location("fetch_popularity", ROOT / "fetch-popularity.py")
fp = importlib.util.module_from_spec(_spec)
sys.modules["fetch_popularity"] = fp
_spec.loader.exec_module(fp)  # type: ignore[union-attr]


class AccumulateDailyHistoryTests(unittest.TestCase):
    def test_adds_a_new_day_for_each_html_file(self):
        result = fp.accumulate_daily_history(
            {}, {"judo.html": 12, "airisk.html": 4}, "2026-09-01", "2026-08-01",
        )
        self.assertEqual(result, {
            "judo.html": {"2026-09-01": 12},
            "airisk.html": {"2026-09-01": 4},
        })

    def test_filters_non_html_paths_out_of_new_counts(self):
        # fetch_path_counts already restricts to top-level .html files, but
        # the pure function re-filters defensively so a caller passing raw
        # data can't leak e.g. "404" or "popularity.json" in as a key.
        result = fp.accumulate_daily_history(
            {}, {"judo.html": 5, "404": 2, "popularity.json": 1}, "2026-09-01", "2026-08-01",
        )
        self.assertEqual(result, {"judo.html": {"2026-09-01": 5}})

    def test_merges_onto_existing_history_without_touching_other_files(self):
        existing = {"judo.html": {"2026-08-30": 9, "2026-08-31": 11}, "airisk.html": {"2026-08-31": 3}}
        result = fp.accumulate_daily_history(existing, {"judo.html": 7}, "2026-09-01", "2026-08-01")
        self.assertEqual(result["judo.html"], {"2026-08-30": 9, "2026-08-31": 11, "2026-09-01": 7})
        # airisk.html got no new count today, but its existing history is untouched.
        self.assertEqual(result["airisk.html"], {"2026-08-31": 3})

    def test_prunes_dates_older_than_cutoff(self):
        existing = {"judo.html": {"2026-07-01": 1, "2026-08-15": 2, "2026-08-31": 3}}
        result = fp.accumulate_daily_history(existing, {}, "2026-09-01", "2026-08-01")
        # 2026-07-01 is before the 2026-08-01 cutoff and is dropped; the rest survive.
        self.assertEqual(result["judo.html"], {"2026-08-15": 2, "2026-08-31": 3})

    def test_prunes_a_file_entirely_once_all_its_dates_age_out(self):
        existing = {"judo.html": {"2026-07-01": 1}}
        result = fp.accumulate_daily_history(existing, {}, "2026-09-01", "2026-08-01")
        self.assertEqual(result, {})

    def test_rolling_window_is_30_days_in_real_usage(self):
        # Simulate 35 consecutive daily runs and confirm only the most recent
        # 30 calendar dates survive per file, exactly matching the spec's
        # "rolling 30 days" requirement (not a length cap, a date cutoff).
        from datetime import date, timedelta
        history: dict = {}
        start = date(2026, 1, 1)
        for i in range(35):
            day = (start + timedelta(days=i)).isoformat()
            cutoff = (start + timedelta(days=i - 29)).isoformat()
            history = fp.accumulate_daily_history(history, {"judo.html": i}, day, cutoff)
        self.assertEqual(len(history["judo.html"]), 30)
        self.assertEqual(min(history["judo.html"]), (start + timedelta(days=5)).isoformat())
        self.assertEqual(max(history["judo.html"]), (start + timedelta(days=34)).isoformat())

    def test_seeds_one_point_from_existing_dailyviews_when_history_is_empty(self):
        result = fp.accumulate_daily_history(
            {}, {}, "2026-09-01", "2026-08-01",
            seed_views={"judo.html": 20, "airisk.html": 0}, seed_date="2026-08-31",
        )
        # airisk.html had a zero-view seed, which carries no information, so
        # it is not fabricated into a data point.
        self.assertEqual(result, {"judo.html": {"2026-08-31": 20}})

    def test_seed_never_fires_once_real_history_exists(self):
        existing = {"judo.html": {"2026-08-30": 4}}
        result = fp.accumulate_daily_history(
            existing, {}, "2026-09-01", "2026-08-01",
            seed_views={"judo.html": 999}, seed_date="2026-08-31",
        )
        # The seed value (999) must never appear: real history already exists.
        self.assertEqual(result, {"judo.html": {"2026-08-30": 4}})

    def test_seed_is_skipped_without_seed_date_or_seed_views(self):
        self.assertEqual(fp.accumulate_daily_history({}, {}, "2026-09-01", "2026-08-01"), {})
        self.assertEqual(
            fp.accumulate_daily_history({}, {}, "2026-09-01", "2026-08-01", seed_views={"judo.html": 1}),
            {},
        )

    def test_existing_popularity_json_keys_are_unaffected_by_this_module(self):
        # accumulate_daily_history only ever computes the dailyHistory value;
        # confirm it does not require or mutate scores/dailyViews/totalViews/
        # totalViewsHistory (those are handled entirely elsewhere in main()).
        import inspect
        params = inspect.signature(fp.accumulate_daily_history).parameters
        self.assertEqual(
            set(params),
            {"daily_history", "new_counts", "day", "cutoff", "seed_views", "seed_date"},
        )


if __name__ == "__main__":
    unittest.main()
