"""Figures B-S1 and B-S3 of the phase-energy capstone paper (paper work-list item 14).

What is checked, and why:

* The builder regenerates the two committed SVGs byte for byte, so a figure cannot drift from the registered
  values it draws.
* A changed source changes the figure, and a source that no longer has the shape or the sentence a figure was drawn
  from makes the builder refuse instead of drawing a stale number.
* Every drawn shape sits inside a group that names it, every such name is written in the figure itself, and the
  caption file lists every name and every labelled instance. No shape is left for the reader to guess.
* Every number in the caption file is accounted for by a comment in its own paragraph, by the conventions of the
  paper's lexicon (``docs/paper/paper-b/01-terms.md``): ``src:`` (a section of the registration or the analysis
  plan), ``rv:`` (an entry of the registered-values table), ``calc:`` (arithmetic on sourced numbers) or
  ``synthetic:`` (an invented example value).

A ``src:`` comment's line numbers are for the reader. The check is that the number occurs in the named section, so
an edit that only moves lines does not fail this test. That check is a coarse net: a section holds many numbers.
The tight checks are on the values the builder itself reads: each must be stated in the caption in the builder's
own rendering, each agrees with the registered-values table where the table has it, and each value read from
registration prose is tied to an exact sentence fragment that the builder refuses to build without.
"""

from __future__ import annotations

import copy
import importlib.util
import json
import re
import sys
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
B5 = ROOT / "docs" / "paper" / "figures" / "b5"
BUILDER = B5 / "build_window_and_flow.py"
CAPTIONS = B5 / "captions-s1-s3.md"
REGISTERED_VALUES = ROOT / "docs" / "paper" / "paper-b" / "registered-values.json"
DOCUMENTS = {
    "registration": ROOT / "configs" / "campaigns" / "v5_claim_25g83" / "registration_block5.md",
    "analysis plan": ROOT / "configs" / "campaigns" / "v5_claim_25g83" / "analysis_plan_block5.md",
}
PACK_DIRS = {
    "ALPHA": "configs/campaigns/d117_floor_qwen3-1p7b_v5",
    "BETA": "configs/campaigns/d117_floor_qwen3-8b_v5",
    "GAMMA": "configs/campaigns/d117_contrast_qwen3-1p7b_vs_qwen3-8b_v5",
}
SVG = "{http://www.w3.org/2000/svg}"
SHAPES = {"rect", "line", "polygon", "polyline", "path", "circle", "ellipse"}

# Entries of the registered-values table (paper work-list item 1) that state a value this builder also reads from
# its own sources: table id -> (builder value, factor by which the table's unit exceeds the builder's).
RV_SAME = {
    "chain.settle_s": ("settle_s", 1),
    "chain.countdown_s.post_calibration": ("post_countdown_s", 1),
    "reference.corpus_minimum_n": ("corpus_minimum", 1),
    "reference.endpoint_references_planned": ("start_members", 1),
    "reference.spares.start": ("start_spares", 1),
    "reference.spares.midpoint": ("midpoint_spares", 1),
    "reference.spares.end": ("end_spares", 1),
    "pack.ALPHA.reference_corpus_members": ("corpus_members", 1),
    "pack.ALPHA.collection_stages": ("collection_stages", 1),
    "pack.ALPHA.span_part_s.settles": ("settles_total_s", 1),
    "pack.ALPHA.members": ("members_single", 1),
    "pack.BETA.members": ("members_single", 1),
    "pack.ALPHA.science_members": ("science_single", 1),
    "pack.BETA.science_members": ("science_single", 1),
    "pack.GAMMA.members": ("members_two", 1),
    "pack.GAMMA.science_members": ("science_two", 1),
    "arm.clock.t_stream_max_s": ("t_stream_max_s", 1),
    "arm.clock.limit_ms": ("clock_limit_ms", 1),
    "arm.clock.residual_max_ns": ("clock_step_ms", 1_000_000),
    "arm.battery.limit_ma": ("battery_limit_ma", 1),
    "arm.thermal.max_level": ("thermal_max_level", 1),
    "arm.contention.cpu_limit_s_per_s": ("cpu_limit", 1),
    "arm.contention.interval_s": ("dwell_interval_s", 1),
    "arm.contention.clean_s": ("dwell_clean_s", 1),
    "arm.contention.cap_s": ("dwell_cap_s", 1),
    "arm.contention.window_interval_s": ("window_interval_s", 1),
    "arm.disk.headroom_bytes": ("disk_headroom_gib", 1024 ** 3),
    "arm.disk.low_bytes": ("disk_low_gib", 1024 ** 3),
    "arm.instrument.frames": ("sampler_frames", 1),
    "arm.instrument.bound_s": ("sampler_bound_s", 1),
    "arm.instrument.median_ms_max": ("sampler_median_ms", 1),
    "arm.instrument.max_ms_max": ("sampler_max_ms", 1),
    "cooldown.subwindow_s": ("cooldown_reading_s", 1),
    "cooldown.cap_s": ("cooldown_cap_s", 1),
    "driver.monitor_post_chain_hold_s": ("monitor_hold_s", 1),
    "driver.monitor_outage_s": ("monitor_outage_min", 60),
    "catalog.codes": ("catalog_codes", 1),
    "catalog.effect.DISCLOSE": ("catalog_disclose", 1),
    "catalog.effect.EXCLUDE_MEMBER": ("catalog_exclude_member", 1),
    "catalog.effect.EXCLUDE_WINDOW": ("catalog_exclude_window", 1),
    "catalog.cell_unit_minimum": ("unit_minimum", 1),
}
# Values the builder reads from registration prose, and the words in which the caption file states each.
PROSE_IN_CAPTION = {
    "arm_reads_s": "take about {} s",
    "arm_span_min": "about {} minutes after the scheduled start",
    "pre_screen_s": "the pre screen, {} s",
    "acceptance_captures": "among the {} pulse calibrations",
    "calibration_pulses": "switched on and off {} times",
    "idle_baseline_s": "for about {} s, its idle baseline",
    "expected_chain_alpha_h": "{} h in the 1.7B window",
    "expected_chain_beta_h": "{} h in the 8B window",
    "expected_chain_gamma_h": "{} h in the contrast window",
    "block_duration_projected_h": "about {} h on the projection",
    "block_duration_earlier_basis_h": "about {} h on the slower figure",
    "p_usable_with_minimum": "a probability of about {} of keeping both",
    "p_usable_all_members": "(36/37)^119, about {}",
}
# Table entries the captions cite whose value the builder holds as text, or in another form.
RV_TEXT = {
    "workload.decode.prompt_tokens": "decode_prompt_tokens",
    "workload.decode.output_tokens": "output_tokens",
    "workload.prefill.prompt_tokens": "prefill_prompt_tokens",
}

NUMBER = re.compile(r"(?<![\w.,-])(\d(?:[\d,]*\d)?(?:\.\d+)?)(?![\w]|[.,]\d)")
COMMENT = re.compile(r"<!--(.*?)-->", re.S)
HEADING = re.compile(r"^#{1,6} .*$", re.M)
# A count below thirteen may be printed as a word.
WORDS = {word: str(index) for index, word in enumerate(
    "one two three four five six seven eight nine ten eleven twelve".split(), start=1)}


def _load_builder():
    spec = importlib.util.spec_from_file_location("paper_b_build_window_and_flow", BUILDER)
    module = importlib.util.module_from_spec(spec)
    before = sys.dont_write_bytecode
    sys.dont_write_bytecode = True
    try:
        sys.modules[spec.name] = module
        spec.loader.exec_module(module)
    finally:
        sys.dont_write_bytecode = before
    return module


builder = _load_builder()
FIGURES = {builder.S1_NAME: "Figure B-S1", builder.S3_NAME: "Figure B-S3"}


def _plain(text: str) -> str:
    """Text as compared here: no emphasis marks, one space between words, lower case."""

    text = text.replace(" ", " ").replace("*", "").replace("`", "").replace("’", "'")
    return re.sub(r"\s+", " ", text).strip().casefold()


def _numbers(text: str) -> set[str]:
    return {match.replace(",", "") for match in NUMBER.findall(text.replace(" ", " "))}


class _Drawing:
    """One SVG, read back: its named elements, its labels, its text and any shape that has no name."""

    def __init__(self, text: str) -> None:
        self.root = ET.fromstring(text)
        self.names: set[str] = set()
        self.labels: set[str] = set()
        self.unnamed: list[str] = []
        self.texts: list[str] = []
        self._walk(self.root, named=False, in_defs=False)

    def _walk(self, node: ET.Element, named: bool, in_defs: bool) -> None:
        tag = node.tag.replace(SVG, "")
        in_defs = in_defs or tag == "defs"
        if tag == "g" and node.get("data-element"):
            named = True
            self.names.add(node.get("data-element"))
            if node.get("data-label"):
                self.labels.add(node.get("data-label"))
        if tag == "text":
            self.texts.append("".join(node.itertext()))
        if tag in SHAPES and not in_defs and not named:
            self.unnamed.append(ET.tostring(node, encoding="unicode")[:120])
        for child in node:
            self._walk(child, named, in_defs)


def _caption_sections() -> dict[str, str]:
    """The caption file cut at its second-level headings: {'Figure B-S1': text, 'Figure B-S3': text}."""

    text = CAPTIONS.read_text(encoding="utf-8")
    sections: dict[str, str] = {}
    for match in re.finditer(r"^## (Figure B-S\d)\b.*?(?=^## |\Z)", text, re.S | re.M):
        sections[match.group(1)] = match.group(0)
    return sections


def _element_table(section: str) -> list[str]:
    """First cells of the caption's table of drawn elements."""

    rows = [line for line in section.splitlines() if line.startswith("|")]
    names = [row.split("|")[1].strip() for row in rows]
    return [name for name in names if name and not set(name) <= {"-", ":", " "} and name != "Drawn element"]


class RegenerationTests(unittest.TestCase):
    def test_committed_figures_equal_a_fresh_build(self) -> None:
        built = builder.build(ROOT)
        self.assertEqual(set(built), set(FIGURES))
        for name, text in built.items():
            with self.subTest(figure=name):
                self.assertEqual((B5 / name).read_text(encoding="utf-8"), text,
                                 f"{name} differs from a fresh build; run {BUILDER.relative_to(ROOT)}")

    def test_check_mode_passes_on_the_committed_figures(self) -> None:
        self.assertEqual(builder.main(["--check"]), 0)

    def test_two_builds_are_identical(self) -> None:
        self.assertEqual(builder.build(ROOT), builder.build(ROOT))

    def test_a_changed_source_changes_the_figure(self) -> None:
        sources = builder.load_sources(ROOT)
        baseline = builder.values(sources)

        slower = copy.deepcopy(sources)
        slower["chain"]["SETTLE_S"] = 90
        s1 = builder.build_s1(builder.values(slower))
        self.assertNotEqual(s1, builder.build_s1(baseline))
        self.assertIn("settles of 90 s = 990 s", s1)
        self.assertNotIn("60 s", s1)

        reclassified = copy.deepcopy(sources)
        code = next(name for name, entry in reclassified["catalog"]["codes"].items() if entry["effect"] == "DISCLOSE")
        reclassified["catalog"]["codes"][code]["effect"] = "EXCLUDE_WINDOW"
        s3 = builder.build_s3(builder.values(reclassified))
        self.assertIn(f"{baseline['catalog_disclose'] - 1} codes", s3)
        self.assertIn(f"{baseline['catalog_exclude_window'] + 1} codes", s3)

        stricter = copy.deepcopy(sources)
        stricter["thresholds"]["contention"]["clean_s"] = 600
        self.assertIn("600 s", builder.build_s1(builder.values(stricter)))
        self.assertIn("for 600 s in a row", builder.build_s3(builder.values(stricter)))

    def test_a_source_with_another_shape_is_refused(self) -> None:
        sources = builder.load_sources(ROOT)

        no_midpoint = copy.deepcopy(sources)
        stages = no_midpoint["sizing"]["packs"]["GAMMA"]["stages"]
        stages[:] = [stage for stage in stages if stage.get("spare_retry", {}).get("slot") != "midpoint"]
        with self.assertRaises(builder.SourceError):
            builder.values(no_midpoint)

        unequal = copy.deepcopy(sources)
        unequal["sizing"]["packs"]["BETA"]["stages"][2]["members"] = 11
        with self.assertRaises(builder.SourceError):
            builder.values(unequal)

        seventh = copy.deepcopy(sources)
        seventh["thresholds"]["humidity"] = {"limit": 1}
        with self.assertRaises(builder.SourceError):
            builder.values(seventh)

        fourth_effect = copy.deepcopy(sources)
        code = next(iter(fourth_effect["catalog"]["codes"]))
        fourth_effect["catalog"]["codes"][code]["effect"] = "EXCLUDE_STAGE"
        with self.assertRaises(builder.SourceError):
            builder.values(fourth_effect)

    def test_a_reworded_registration_sentence_is_refused(self) -> None:
        text = DOCUMENTS["registration"].read_text(encoding="utf-8")
        self.assertEqual(set(builder.prose_values(text)), {key for key, *_ in builder.PROSE_VALUES})
        for key, _value, _section, fragment in builder.PROSE_VALUES:
            with self.subTest(value=key):
                with self.assertRaises(builder.SourceError):
                    builder.prose_values(text.replace(fragment, "a sentence that says something else"))


class SourceAgreementTests(unittest.TestCase):
    """The builder's own readings against two other committed statements of the same values."""

    def test_stage_order_and_counts_match_the_plan_trees(self) -> None:
        sizing = builder.load_sources(ROOT)["sizing"]
        in_chain = ("bracket_reservation", "calibration_capture", "campaign_collection", "bound_derivation")
        for label, directory in PACK_DIRS.items():
            with self.subTest(pack=label):
                tree = json.loads((ROOT / directory / "plan_tree.json").read_text(encoding="utf-8"))
                planned = [(stage["stage_id"], stage["kind"],
                            stage["expected_count"] if stage["kind"] == "campaign_collection" else None,
                            stage.get("spare_retry", {}).get("max_spares"))
                           for stage in tree["stage_graph"] if stage["kind"] in in_chain]
                drawn = [(stage["stage_id"], stage["kind"], stage.get("members"),
                          stage.get("spare_retry", {}).get("max_spares"))
                         for stage in sizing["packs"][label]["stages"]]
                self.assertEqual(drawn, planned)

    def test_values_match_the_registered_values_table(self) -> None:
        if not REGISTERED_VALUES.exists():
            self.skipTest("the registered-values table of paper work-list item 1 is not in this tree")
        table = json.loads(REGISTERED_VALUES.read_text(encoding="utf-8"))["values"]
        values = builder.values(builder.load_sources(ROOT))
        for rv_id, (key, factor) in RV_SAME.items():
            with self.subTest(entry=rv_id):
                self.assertTrue(rv_id in table, f"the registered-values table has no entry {rv_id}")
                self.assertEqual(table[rv_id]["value"], values[key] * factor)
        for rv_id, key in RV_TEXT.items():
            with self.subTest(entry=rv_id):
                self.assertEqual(f"{table[rv_id]['value']:,}", values[key])
        self.assertEqual(1 + table["cooldown.tolerance_fraction"]["value"], values["cooldown_factor"])
        deadlines = [table[f"pack.{label}.window_max_s"]["value"] / 3600 for label in PACK_DIRS]
        self.assertEqual((int(min(deadlines)), int(max(deadlines))),
                         (values["deadline_h_min"], values["deadline_h_max"]))

    def test_the_planning_probabilities_recompute(self) -> None:
        values = builder.values(builder.load_sources(ROOT))
        self.assertEqual(values["abort_rate"], "1/37")
        keep = 36 / 37
        self.assertEqual(f"{keep ** values['members_single']:.2f}", values["p_usable_all_members"])

        def at_most_two_lost(p_lost: float) -> float:
            return sum(p_lost ** k * (1 - p_lost) ** (10 - k) * {0: 1, 1: 10, 2: 45}[k] for k in range(3))

        # One paper cell keeps at least 8 of 10 absolute repeats and 8 of 10 quads; a single-model window has two.
        self.assertEqual((values["repeats"], values["quads"], values["unit_minimum"]), (10, 10, 8))
        one_cell = at_most_two_lost(1 - keep) * at_most_two_lost(1 - keep ** 4)
        self.assertEqual(f"{one_cell ** 2:.2f}", values["p_usable_with_minimum"])


class NamedElementTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.drawings = {name: _Drawing((B5 / name).read_text(encoding="utf-8")) for name in FIGURES}
        cls.captions = _caption_sections()

    def test_every_drawn_shape_is_inside_a_named_element(self) -> None:
        for name, drawing in self.drawings.items():
            with self.subTest(figure=name):
                self.assertEqual(drawing.unnamed, [])

    def test_every_element_name_is_written_in_the_figure(self) -> None:
        for name, drawing in self.drawings.items():
            written = _plain(" | ".join(drawing.texts))
            for element in sorted(drawing.names - set(builder.FURNITURE)):
                with self.subTest(figure=name, element=element):
                    self.assertIn(_plain(element), written)

    def test_the_caption_table_lists_exactly_the_drawn_elements(self) -> None:
        self.assertEqual(set(self.captions), set(FIGURES.values()))
        for name, drawing in self.drawings.items():
            with self.subTest(figure=name):
                listed = _element_table(self.captions[FIGURES[name]])
                self.assertEqual(len(listed), len(set(listed)), "an element is listed twice")
                self.assertEqual(set(listed), drawing.names - {"background"})

    def test_the_caption_names_every_labelled_instance(self) -> None:
        for name, drawing in self.drawings.items():
            caption = _plain(COMMENT.sub("", self.captions[FIGURES[name]]))
            for label in sorted(drawing.labels):
                with self.subTest(figure=name, label=label):
                    self.assertIn(_plain(label), caption)

    def test_each_figure_has_a_title_and_a_description(self) -> None:
        for name, drawing in self.drawings.items():
            with self.subTest(figure=name):
                for tag in ("title", "desc"):
                    node = drawing.root.find(SVG + tag)
                    self.assertIsNotNone(node)
                    self.assertGreater(len(node.text or ""), 20)

    def test_no_figure_shows_an_energy_a_power_or_a_result_slot(self) -> None:
        for name, drawing in self.drawings.items():
            with self.subTest(figure=name):
                shown = " | ".join(drawing.texts).replace(" ", " ")
                self.assertIsNone(re.search(r"\d\s?(?:m|k)?[JW]\b", shown))
                self.assertNotIn("{{slot", shown)


class CaptionNumberTests(unittest.TestCase):
    """Every number of the caption file is accounted for by a comment in its own paragraph."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.values = builder.values(builder.load_sources(ROOT))
        cls.table = (json.loads(REGISTERED_VALUES.read_text(encoding="utf-8"))["values"]
                     if REGISTERED_VALUES.exists() else None)
        cls.sections = {}
        for label, path in DOCUMENTS.items():
            by_section: dict[str, str] = {}
            current = "preamble"
            for line in path.read_text(encoding="utf-8").split("\n"):
                match = re.match(r"#{2,3} (\d+(?:\.\d+)?)[. ]", line)
                if match:
                    current = match.group(1)
                by_section[current] = by_section.get(current, "") + line + "\n"
            cls.sections[label] = by_section

    def _accounted(self, comment: str) -> set[str] | None:
        """The numbers one comment vouches for, or None when it is not a source comment."""

        kind, _, body = comment.strip().partition(":")
        body = body.strip()
        if kind in ("calc", "synthetic"):
            return _numbers(body)
        if kind == "rv":
            found: set[str] = set()
            for rv_id in re.findall(r"[a-z][\w.-]*\.[\w.-]+", body):
                if self.table is not None:
                    self.assertTrue(rv_id in self.table, f"an rv comment names an entry the table lacks: {rv_id}")
                    value = self.table[rv_id]["value"]
                    if isinstance(value, (int, float)) and not isinstance(value, bool):
                        found |= _numbers(f"{value:,}") | _numbers(f"{value:g}")
                if rv_id in RV_SAME:
                    found |= _numbers(builder.num(self.values[RV_SAME[rv_id][0]]))
                elif rv_id in RV_TEXT:
                    found |= _numbers(self.values[RV_TEXT[rv_id]])
                else:
                    self.assertIsNotNone(self.table, f"rv comment {rv_id} cannot be resolved without the table")
            return found
        if kind == "src":
            found = set()
            for part in body.split(";"):
                part = part.strip()
                label = next((name for name in DOCUMENTS if part.startswith(name)), None)
                self.assertIsNotNone(label, f"src comment names no known document: {part!r}")
                for section in re.findall(r"§(\d+(?:\.\d+)?)", part):
                    self.assertTrue(section in self.sections[label], f"{label} has no section {section}")
                    found |= _numbers(self.sections[label][section])
            return found
        return None

    def test_every_number_has_a_source_in_its_paragraph(self) -> None:
        text = CAPTIONS.read_text(encoding="utf-8")
        self.assertNotIn("{{slot", text)
        unaccounted = []
        for paragraph in re.split(r"\n\s*\n", text):
            vouched: set[str] = set()
            for comment in COMMENT.findall(paragraph):
                numbers = self._accounted(comment)
                if numbers is not None:
                    vouched |= numbers
            visible = HEADING.sub("", COMMENT.sub("", paragraph))  # a heading is navigation, not a statement
            visible = re.sub(r"`[^`]*`|\]\([^)]*\)", "", visible)
            for number in sorted(_numbers(visible) - vouched):
                unaccounted.append((number, " ".join(visible.split())[:70]))
        self.assertEqual(unaccounted, [])

    def test_the_caption_states_each_prose_value_as_the_builder_read_it(self) -> None:
        caption = _plain(COMMENT.sub("", CAPTIONS.read_text(encoding="utf-8")))
        for key, words in PROSE_IN_CAPTION.items():
            with self.subTest(value=key):
                self.assertIn(_plain(words.format(self.values[key])), caption)
        self.assertEqual(self.values["abort_rate"], "1/37")
        self.assertIn("a rate of 1 failed run in 37", caption)
        self.assertEqual(self.values["clock_error_energy"], "0.2 J at 40 W")
        self.assertIn("draws 40 w moves at most 0.2 j", caption)

    def test_the_caption_states_positions_and_deadlines_as_the_builder_computed_them(self) -> None:
        caption = _plain(COMMENT.sub("", CAPTIONS.read_text(encoding="utf-8")))
        v = self.values
        for words in (
                f"after science member {v['midpoint_after_single']} of {v['science_single']} in a single-model window",
                f"after science member {v['midpoint_after_two']} of {v['science_two']} in the contrast window",
                f"after science members {v['diagnostic_after_two']}",
                f"the deadline is {v['deadline_h_min']} to {v['deadline_h_max']} hours after the scheduled start",
                f"has {v['settles']} settles",
                f"{builder.num(v['settles_total_s'])} s in all"):
            with self.subTest(words=words):
                self.assertIn(_plain(words), caption)

    def test_cited_registered_values_appear_beside_their_comment(self) -> None:
        """An rv comment sits in the paragraph that prints the value it names, in the builder's own rendering."""

        for paragraph in re.split(r"\n\s*\n", CAPTIONS.read_text(encoding="utf-8")):
            prose = COMMENT.sub("", paragraph)
            visible = _numbers(prose) | {digit for word, digit in WORDS.items()
                                        if re.search(rf"\b{word}\b", prose, re.I)}
            for comment in COMMENT.findall(paragraph):
                kind, _, body = comment.strip().partition(":")
                if kind != "rv":
                    continue
                for rv_id in re.findall(r"[a-z][\w.-]*\.[\w.-]+", body):
                    if rv_id in RV_SAME:
                        with self.subTest(entry=rv_id):
                            printed = _numbers(builder.num(self.values[RV_SAME[rv_id][0]]))
                            self.assertTrue(printed <= visible,
                                            f"{rv_id}: {sorted(printed)} is not printed in its paragraph")


if __name__ == "__main__":
    unittest.main()
