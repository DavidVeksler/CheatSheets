#!/usr/bin/env python3
"""Unit tests for scripts/build_catalog.py. stdlib unittest only (no pytest).

Run with:
    .venv/bin/python3 -m unittest scripts.test_build_catalog -v
or, from the scripts/ directory:
    ../.venv/bin/python3 -m unittest test_build_catalog -v
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import build_catalog as bc  # noqa: E402
from bs4 import BeautifulSoup  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
PARSER = bc.get_html_parser()


def load_soup(filename: str) -> BeautifulSoup:
    content = (ROOT / filename).read_text(encoding="utf-8", errors="replace")
    return BeautifulSoup(content, PARSER)


class HeadingExtractionTests(unittest.TestCase):
    """The 5 representative sheets named in the spec."""

    def test_fastener_torque_h2_has_torque_id(self):
        soup = load_soup("fastener-torque-tap-drill.html")
        headings, level = bc.extract_headings(soup)
        self.assertEqual(level, "h2")
        self.assertGreaterEqual(len(headings), 3)
        ids = {h["id"] for h in headings}
        self.assertIn("torque", ids)

    def test_judo_falls_back_to_h5_with_unlinked_ukemi(self):
        soup = load_soup("judo.html")
        headings, level = bc.extract_headings(soup)
        self.assertEqual(level, "h5")
        self.assertGreaterEqual(len(headings), 3)
        ukemi = [h for h in headings if "ukemi" in h["text"].lower()]
        self.assertTrue(ukemi, "expected a heading mentioning Ukemi")
        # judo.html's h5 headings carry no id and sit outside any <section id>,
        # so per spec they are searchable but not deep-linkable.
        self.assertIsNone(ukemi[0]["id"])

    def test_ai_frontier_sanity(self):
        soup = load_soup("ai-frontier.html")
        headings, level = bc.extract_headings(soup)
        self.assertEqual(level, "h2")
        self.assertGreaterEqual(len(headings), 3)
        # frontier-map-title carries its own id directly on the h2.
        self.assertIn("frontier-map-title", {h["id"] for h in headings})

    def test_linux_server_hardening_sanity(self):
        soup = load_soup("linux-server-hardening.html")
        headings, level = bc.extract_headings(soup)
        self.assertEqual(level, "h2")
        self.assertGreaterEqual(len(headings), 3)
        # These h2 tags carry no id of their own; the id comes from the
        # enclosing <section id="quickref">.
        self.assertIn("quickref", {h["id"] for h in headings})

    def test_shabbat_services_sanity(self):
        soup = load_soup("shabbat-services-cheatsheet.html")
        headings, level = bc.extract_headings(soup)
        # Only 2 h2 and nothing in h3/h4/h5: none reaches the 3+ threshold,
        # so the extractor falls back to the richest level (h2, with 2).
        self.assertEqual(level, "h2")
        self.assertEqual(len(headings), 2)
        ids = {h["id"] for h in headings}
        self.assertIn("quick-heading", ids)


class HeadingIdTests(unittest.TestCase):
    def test_own_id_wins_over_enclosing_section(self):
        soup = BeautifulSoup(
            '<section id="outer"><h2 id="inner">Title</h2></section>', PARSER
        )
        tag = soup.find("h2")
        self.assertEqual(bc.heading_id(tag), "inner")

    def test_falls_back_to_enclosing_section_id(self):
        soup = BeautifulSoup(
            '<section id="outer"><div><h2>Title</h2></div></section>', PARSER
        )
        tag = soup.find("h2")
        self.assertEqual(bc.heading_id(tag), "outer")

    def test_none_when_no_id_anywhere(self):
        soup = BeautifulSoup("<section><h2>Title</h2></section>", PARSER)
        tag = soup.find("h2")
        self.assertIsNone(bc.heading_id(tag))


class OutlinkTests(unittest.TestCase):
    def test_dedupes_and_drops_self_links(self):
        html = """
        <a href="b.html">one</a>
        <a href="b.html#section">two</a>
        <a href="a.html">self</a>
        <a href="c.html?x=1">three</a>
        <a href="https://cheatsheets.davidveksler.com/d.html">absolute</a>
        <a href="https://example.com/e.html">external</a>
        <a href="not-catalogued.html">unknown</a>
        """
        soup = BeautifulSoup(html, PARSER)
        known = {"a.html", "b.html", "c.html", "d.html"}
        outlinks = bc.extract_outlinks(soup, "a.html", known)
        self.assertEqual(outlinks, ["b.html", "c.html", "d.html"])


class ShapeHeuristicTests(unittest.TestCase):
    def base_counts(self) -> dict:
        return {
            "tables": 0, "max_table_rows": 0, "ordered_lists": 0, "checkboxes": 0,
            "number_range_output": 0, "has_script": False, "has_local_storage": False,
            "pre_code_kbd": 0, "svg": 0, "canvas": 0, "sections": 0, "form_inputs": 0,
            "words": 100,
        }

    def test_default_is_reference(self):
        shapes = bc.compute_shapes(self.base_counts(), "A Sheet", [], [])
        self.assertEqual(shapes, ["reference"])

    def test_comparison_by_table_count(self):
        counts = self.base_counts()
        counts["tables"] = 3
        self.assertIn("comparison", bc.compute_shapes(counts, "T", [], []))

    def test_comparison_by_big_table(self):
        counts = self.base_counts()
        counts["tables"] = 1
        counts["max_table_rows"] = 12
        self.assertIn("comparison", bc.compute_shapes(counts, "T", [], []))

    def test_procedure_by_ordered_lists(self):
        counts = self.base_counts()
        counts["ordered_lists"] = 3
        self.assertIn("procedure", bc.compute_shapes(counts, "T", [], []))

    def test_procedure_by_checklist(self):
        counts = self.base_counts()
        counts["checkboxes"] = 10
        self.assertIn("procedure", bc.compute_shapes(counts, "T", [], []))

    def test_calculator_needs_inputs_and_script(self):
        counts = self.base_counts()
        counts["number_range_output"] = 3
        counts["has_script"] = False
        self.assertNotIn("calculator", bc.compute_shapes(counts, "T", [], []))
        counts["has_script"] = True
        self.assertIn("calculator", bc.compute_shapes(counts, "T", [], []))

    def test_tracker_needs_localstorage_and_checkboxes(self):
        counts = self.base_counts()
        counts["has_local_storage"] = True
        counts["checkboxes"] = 10
        self.assertIn("tracker", bc.compute_shapes(counts, "T", [], []))

    def test_commands_by_pre_code_kbd(self):
        counts = self.base_counts()
        counts["pre_code_kbd"] = 10
        self.assertIn("commands", bc.compute_shapes(counts, "T", [], []))

    def test_device_by_model_number(self):
        counts = self.base_counts()
        self.assertIn("device", bc.compute_shapes(counts, "Baofeng UV-5R Quick Reference", [], []))

    def test_device_by_programming_keyword(self):
        counts = self.base_counts()
        self.assertIn("device", bc.compute_shapes(counts, "Keypad programming guide", [], []))

    def test_essay_by_word_count_and_few_tables(self):
        counts = self.base_counts()
        counts["words"] = 4500
        counts["tables"] = 1
        self.assertIn("essay", bc.compute_shapes(counts, "T", [], []))

    def test_essay_excluded_when_many_tables(self):
        counts = self.base_counts()
        counts["words"] = 4500
        counts["tables"] = 3
        self.assertNotIn("essay", bc.compute_shapes(counts, "T", [], []))

    def test_timeline_by_title_word_boundary(self):
        counts = self.base_counts()
        self.assertIn("timeline", bc.compute_shapes(counts, "AI Risk Timeline", [], []))

    def test_timeline_does_not_false_positive_on_substring(self):
        # "terminology"/"methodology"/"catalog" contain "log" as a substring
        # but not as a whole word; the \b-bounded regex must not fire here.
        counts = self.base_counts()
        shapes = bc.compute_shapes(counts, "Terminology and Methodology Catalog", [], [])
        self.assertNotIn("timeline", shapes)

    def test_visual_by_svg_count(self):
        counts = self.base_counts()
        counts["svg"] = 3
        self.assertIn("visual", bc.compute_shapes(counts, "T", [], []))

    def test_visual_by_canvas(self):
        counts = self.base_counts()
        counts["canvas"] = 1
        self.assertIn("visual", bc.compute_shapes(counts, "T", [], []))

    def test_multivalued(self):
        counts = self.base_counts()
        counts["tables"] = 3
        counts["pre_code_kbd"] = 10
        shapes = bc.compute_shapes(counts, "T", [], [])
        self.assertIn("comparison", shapes)
        self.assertIn("commands", shapes)
        self.assertEqual(len(shapes), 2)


class PathsValidatorTests(unittest.TestCase):
    def test_valid_paths_produce_no_errors(self):
        known = {"a.html", "b.html"}
        data = {"paths": [{"id": "p1", "steps": [{"file": "a.html"}, {"file": "b.html"}]}]}
        self.assertEqual(bc.validate_paths(data, known), [])

    def test_bogus_file_is_reported_with_path_id(self):
        known = {"a.html"}
        data = {"paths": [{"id": "bogus-path", "steps": [{"file": "a.html"}, {"file": "does-not-exist.html"}]}]}
        errors = bc.validate_paths(data, known)
        self.assertEqual(len(errors), 1)
        self.assertIn("bogus-path", errors[0])
        self.assertIn("does-not-exist.html", errors[0])

    def test_real_paths_json_validates_against_real_catalog_files(self):
        import json
        paths_path = ROOT / "paths.json"
        if not paths_path.exists():
            self.skipTest("paths.json not present")
        data = json.loads(paths_path.read_text(encoding="utf-8"))
        known = set(bc.discover_files({}))
        errors = bc.validate_paths(data, known)
        self.assertEqual(errors, [], f"paths.json references missing files: {errors}")


class LayoutDeterminismTests(unittest.TestCase):
    def test_same_inputs_produce_identical_positions(self):
        files = [f"sheet-{i}.html" for i in range(12)]
        cats = ["AI & Safety", "Radio", "Other"]
        node_categories = [cats[i % len(cats)] for i in range(len(files))]
        edges = [(0, 1), (1, 2), (2, 3), (3, 0), (4, 5), (5, 6), (7, 8), (9, 10)]

        run1 = bc.compute_layout(files, node_categories, edges, seed=7, iterations=40)
        run2 = bc.compute_layout(files, node_categories, edges, seed=7, iterations=40)

        self.assertEqual(len(run1), len(files))
        self.assertEqual(run1, run2)

    def test_positions_are_normalized_to_unit_square(self):
        files = [f"sheet-{i}.html" for i in range(8)]
        node_categories = ["Radio"] * len(files)
        edges = [(0, 1), (2, 3), (4, 5)]
        positions = bc.compute_layout(files, node_categories, edges, seed=1, iterations=30)
        xs = [p[0] for p in positions]
        ys = [p[1] for p in positions]
        self.assertAlmostEqual(min(xs), 0.0, places=6)
        self.assertAlmostEqual(max(xs), 1.0, places=6)
        self.assertAlmostEqual(min(ys), 0.0, places=6)
        self.assertAlmostEqual(max(ys), 1.0, places=6)

    def test_empty_graph_returns_empty_list(self):
        self.assertEqual(bc.compute_layout([], [], []), [])


class CategoryMapParsingTests(unittest.TestCase):
    def test_parses_real_category_map(self):
        mapping = bc.parse_category_map(bc.CATEGORY_MAP_PATH)
        self.assertGreater(len(mapping), 190)
        self.assertEqual(mapping.get("judo.html"), "Martial Arts & Strategy")


class DarkHueTests(unittest.TestCase):
    def test_generated_dark_hue_meets_contrast_floor(self):
        for cat, light in bc.CATEGORY_LIGHT_HUES.items():
            dark = bc.generate_dark_hue(light)
            rgb = bc._hex_to_rgb(dark)
            bg = bc._hex_to_rgb(bc.DARK_PAGE_BG)
            ratio = bc._contrast_ratio(rgb, bg)
            self.assertGreaterEqual(ratio, bc.MIN_CONTRAST - 0.01, f"{cat}: {dark} only {ratio:.2f}:1")

    def test_already_sufficient_hue_is_left_unchanged(self):
        # #0891b2 already clears 3:1 against #0e1013 at its own lightness,
        # so the generator should not alter it.
        self.assertEqual(bc.generate_dark_hue("#0891b2"), "#0891b2")


class DiscoverFilesTests(unittest.TestCase):
    def test_excludes_etz_chaim_and_finds_known_sheets(self):
        files = bc.discover_files({})
        self.assertNotIn("etz-chaim-tree-of-life.html", files)
        self.assertIn("judo.html", files)
        self.assertEqual(files, sorted(files))

    def test_hide_override_removes_a_file(self):
        files = bc.discover_files({"judo.html": {"hide": True}})
        self.assertNotIn("judo.html", files)


class InputsHashTests(unittest.TestCase):
    """The --check gate compares content hashes, never mtimes."""

    def test_hash_is_stable_across_calls(self):
        self.assertEqual(bc.compute_inputs_hash(), bc.compute_inputs_hash())

    def test_hash_is_a_sha256_hex_digest(self):
        digest = bc.compute_inputs_hash()
        self.assertEqual(len(digest), 64)
        self.assertTrue(all(c in "0123456789abcdef" for c in digest))

    def test_touching_a_file_does_not_change_the_hash(self):
        """A rebase or fresh clone rewrites mtimes; content-identical stays equal."""
        before = bc.compute_inputs_hash()
        target = ROOT / "judo.html"
        original_mtime = target.stat().st_mtime
        try:
            target.touch()
            self.assertEqual(bc.compute_inputs_hash(), before)
        finally:
            import os
            os.utime(target, (original_mtime, original_mtime))

    def test_content_change_changes_the_hash(self):
        before = bc.compute_inputs_hash()
        extra = ROOT / "zzz-inputs-hash-probe.html"
        self.assertFalse(extra.exists(), "probe file name is already taken")
        try:
            extra.write_text("<html><title>probe</title></html>", encoding="utf-8")
            self.assertNotEqual(bc.compute_inputs_hash(), before)
        finally:
            extra.unlink(missing_ok=True)
        self.assertEqual(bc.compute_inputs_hash(), before)

    def test_committed_catalog_records_a_matching_hash(self):
        import json
        catalog = json.loads((ROOT / "catalog.json").read_text(encoding="utf-8"))
        self.assertIn("inputs_hash", catalog)
        self.assertEqual(catalog["inputs_hash"], bc.compute_inputs_hash())


class CheckGateTests(unittest.TestCase):
    def test_check_passes_on_the_committed_tree(self):
        self.assertEqual(bc.run_check(), 0)


if __name__ == "__main__":
    unittest.main()
