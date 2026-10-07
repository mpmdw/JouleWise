"""Acceptance tests for the Paper B schematic figures B-S2, B-S4 and B-S5.

The figures are built by ``docs/paper/figures/b5/build_boundary_survivors_gate.py`` and explained in
``docs/paper/figures/b5/captions-s2-s4-s5.md``.  The tests check four things:

1. the builder regenerates the three committed SVG files byte for byte, and a changed input changes them;
2. every shape and every text in a figure sits inside one named element, each name is printed in the
   figure, and the caption explains exactly the names that are drawn;
3. every number the figures print is recomputed here, independently of the builder, from the registration's
   text and from the production code (the frequency gate's two worked points among them);
4. the caption text keeps project shorthand inside parentheses.

No test reads a measurement.  The worked examples are the registration's own synthetic numbers.
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
import math
import os
import re
import shutil
import statistics
import subprocess
import sys
import tempfile
import unittest
from fractions import Fraction
from pathlib import Path
from xml.etree import ElementTree

from joulewise import aggregate, kernel_clock, whole_window
from joulewise.b5 import reference_spares
from joulewise.hazards import clock as clock_hazard

ROOT = Path(__file__).resolve().parents[1]
B5 = ROOT / "docs" / "paper" / "figures" / "b5"
BUILDER = B5 / "build_boundary_survivors_gate.py"
CAPTIONS = B5 / "captions-s2-s4-s5.md"
REGISTRATION = ROOT / "configs" / "campaigns" / "v5_claim_25g83" / "registration_block5.md"
FILES = {
    "B-S2": "figB_S2_measurement_boundary.svg",
    "B-S4": "figB_S4_reference_survivors.svg",
    "B-S5": "figB_S5_frequency_gate.svg",
}
SVG_NS = "{http://www.w3.org/2000/svg}"
DRAWN_TAGS = {"rect", "line", "polyline", "polygon", "path", "circle", "ellipse", "text", "image", "use"}
MINUS = "\N{MINUS SIGN}"


def _load_builder():
    spec = importlib.util.spec_from_file_location("paper_b_figures_s2_s4_s5_builder", BUILDER)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


builder = _load_builder()


def _tag(element) -> str:
    return element.tag.removeprefix(SVG_NS)


def _squash(text: str) -> str:
    return " ".join(text.split())


def _svg_root(key: str):
    return ElementTree.fromstring((B5 / FILES[key]).read_bytes())


def _groups(key: str):
    """The figure's named elements: (label, <g> element) in document order."""

    return [(group.get("data-label"), group) for group in _svg_root(key) if group.get("data-label") is not None]


def _group_text(group) -> str:
    return _squash(" ".join(node.text or "" for node in group.iter(f"{SVG_NS}text")))


def _figure_text(key: str) -> str:
    return _squash(" ".join(node.text or "" for node in _svg_root(key).iter(f"{SVG_NS}text")))


def _caption_sections() -> dict[str, str]:
    """Figure key -> the caption file's text under that figure's heading, HTML comments kept."""

    text = CAPTIONS.read_text(encoding="utf-8")
    parts = re.split(r"^## (Figure (B-S\d)\..*)$", text, flags=re.MULTILINE)
    return {parts[index + 1]: parts[index] + "\n" + parts[index + 2] for index in range(1, len(parts), 3)}


def _without_comments(text: str) -> str:
    return re.sub(r"<!--.*?-->", "", text, flags=re.DOTALL)


def _caption_element_names(section: str) -> list[str]:
    marker = "**Every element, by the name printed in the figure.**"
    body = section.split(marker, 1)[1]
    return re.findall(r"^- \*\*(.+?)\*\*:", body, flags=re.MULTILINE)


def _registration() -> str:
    return REGISTRATION.read_text(encoding="utf-8")


def _registered_thresholds() -> dict:
    """The JSON block of registration section 4.3 (the thresholds every window plan copies)."""

    blocks = re.findall(r"```json\n(.*?)\n```", _registration(), flags=re.DOTALL)
    found = [json.loads(block) for block in blocks if '"frequency_margin_ppm"' in block]
    if len(found) != 1:
        raise AssertionError(f"expected one threshold block in the registration, found {len(found)}")
    return found[0]


def _round(value, places: int) -> str:
    """Round half up from an exact value, written with a typographic minus like the figures."""

    exact = Fraction(value)
    scaled = exact * 10 ** places
    whole = math.floor(abs(scaled) + Fraction(1, 2))
    digits = f"{whole:0{places + 1}d}"
    text = f"{digits[:-places]}.{digits[-places:]}" if places else digits
    return (MINUS if exact < 0 and whole else "") + text


class BuilderOutputTests(unittest.TestCase):
    def test_builder_regenerates_the_three_svgs_byte_for_byte(self) -> None:
        built = builder.build()
        self.assertEqual(sorted(built), sorted(FILES.values()))
        for name, text in built.items():
            with self.subTest(file=name):
                self.assertEqual((B5 / name).read_bytes(), text.encode("utf-8"))

    def test_fresh_interpreters_with_different_hash_seeds_give_the_committed_bytes(self) -> None:
        program = (
            "import hashlib, importlib.util, json, sys\n"
            f"spec = importlib.util.spec_from_file_location('b', {str(BUILDER)!r})\n"
            "module = importlib.util.module_from_spec(spec); sys.modules['b'] = module\n"
            "spec.loader.exec_module(module)\n"
            "print(json.dumps({name: hashlib.sha256(text.encode('utf-8')).hexdigest()"
            " for name, text in sorted(module.build().items())}))\n"
        )
        committed = {name: hashlib.sha256((B5 / name).read_bytes()).hexdigest() for name in sorted(FILES.values())}
        for seed in ("1", "2"):
            with self.subTest(hash_seed=seed):
                completed = subprocess.run(
                    [sys.executable, "-B", "-c", program], cwd=ROOT, text=True, capture_output=True, check=False,
                    env={**os.environ, "PYTHONHASHSEED": seed, "PYTHONDONTWRITEBYTECODE": "1"},
                )
                self.assertEqual(completed.returncode, 0, completed.stderr)
                self.assertEqual(json.loads(completed.stdout), committed)

    def test_check_mode_passes_on_the_committed_files_and_names_a_changed_one(self) -> None:
        with tempfile.TemporaryDirectory() as scratch:
            copy = Path(scratch) / "b5"
            copy.mkdir()
            for name in [BUILDER.name, *FILES.values()]:
                shutil.copyfile(B5 / name, copy / name)
            command = [sys.executable, "-B", str(copy / BUILDER.name), "--check"]
            environment = {**os.environ, "PYTHONDONTWRITEBYTECODE": "1"}
            clean = subprocess.run(command, text=True, capture_output=True, check=False, env=environment)
            self.assertEqual(clean.returncode, 0, clean.stderr)
            target = copy / FILES["B-S5"]
            target.write_bytes(target.read_bytes().replace(b"4.846", b"4.847"))
            changed = subprocess.run(command, text=True, capture_output=True, check=False, env=environment)
            self.assertEqual(changed.returncode, 1)
            self.assertIn(FILES["B-S5"], changed.stderr)
            self.assertNotIn(FILES["B-S2"], changed.stderr)

    def test_a_changed_registered_value_or_synthetic_input_changes_the_figure(self) -> None:
        cases = [
            ("B-S5", builder.REGISTERED, "clock.limit_ms", Fraction("5.01"), "3.6604"),
            ("B-S5", builder.REGISTERED, "clock.t_stream_max_s", Fraction(336), "4.849"),
            ("B-S2", builder.SYNTHETIC, "meter.request_battery_w", Fraction("2.5"), "910"),
            ("B-S4", builder.SYNTHETIC, "reference.midpoint_j", Fraction("100.40"), "100.40"),
        ]
        makers = {"B-S2": builder.figure_boundary, "B-S4": builder.figure_survivors, "B-S5": builder.figure_gate}
        for key, table, name, value, expected_text in cases:
            with self.subTest(figure=key, changed=name):
                original = table[name]
                table[name] = (value, original[1])
                try:
                    mutated = makers[key]().svg()
                finally:
                    table[name] = original
                self.assertNotEqual(mutated.encode("utf-8"), (B5 / FILES[key]).read_bytes())
                self.assertIn(expected_text, mutated)
        self.assertEqual(builder.build()[FILES["B-S5"]].encode("utf-8"), (B5 / FILES["B-S5"]).read_bytes())

    def test_the_builder_refuses_to_draw_a_statement_its_inputs_make_false(self) -> None:
        cases = [
            # a 5.1 ms limit would make point B pass, and the figure calls point B refused
            (builder.REGISTERED, "clock.limit_ms", Fraction("5.1"), builder.figure_gate),
            # an end reference far from the start would fail the check, and the figure's verdict says it passes
            (builder.SYNTHETIC, "reference.end_planned_j",
             (Fraction("100.96"), Fraction("100.89"), Fraction("101.08")), builder.figure_survivors),
            # a battery that takes charge would lower the share, and the strip says leaving it out reads too high
            (builder.SYNTHETIC, "meter.request_battery_w", Fraction("-1.5"), builder.figure_boundary),
        ]
        for table, name, value, make in cases:
            with self.subTest(changed=name):
                original = table[name]
                table[name] = (value, original[1])
                try:
                    with self.assertRaises(ValueError):
                        make()
                finally:
                    table[name] = original


class ElementNamingTests(unittest.TestCase):
    def test_every_shape_and_text_is_inside_one_named_element(self) -> None:
        for key in FILES:
            with self.subTest(figure=key):
                root = _svg_root(key)
                self.assertEqual(root.get("data-figure"), key)
                for child in root:
                    tag, role = _tag(child), child.get("data-role")
                    if tag in ("title", "desc"):
                        self.assertTrue((child.text or "").strip())
                    elif role == "background":
                        self.assertEqual(tag, "rect")
                    elif role == "figure-title":
                        self.assertEqual({_tag(node) for node in child}, {"text"})
                    else:
                        self.assertEqual(tag, "g", f"{tag} is drawn outside any named element")
                        label = child.get("data-label")
                        self.assertTrue(label, "a group without a name")
                        kinds = [_tag(node) for node in child]
                        self.assertEqual(kinds[0], "title")
                        self.assertEqual(child[0].text, label)
                        self.assertTrue(set(kinds[1:]) <= DRAWN_TAGS, f"{label}: unexpected content {kinds}")
                        self.assertTrue(kinds[1:], f"{label}: a named element with nothing drawn")
                        self.assertFalse(list(child.iter(f"{SVG_NS}g"))[1:], f"{label}: a nested group")

    def test_each_name_is_printed_in_the_figure(self) -> None:
        for key in FILES:
            printed: dict[str, bool] = {}
            for label, group in _groups(key):
                printed[label] = printed.get(label, False) or label in _group_text(group)
            for label, found in printed.items():
                with self.subTest(figure=key, element=label):
                    self.assertTrue(found, "no group with this name prints the name itself")

    def test_the_caption_explains_exactly_the_elements_that_are_drawn(self) -> None:
        sections = _caption_sections()
        self.assertEqual(sorted(sections), sorted(FILES))
        labels = builder.element_labels()
        for key in FILES:
            with self.subTest(figure=key):
                drawn = []
                for label, _ in _groups(key):
                    if label not in drawn:
                        drawn.append(label)
                self.assertEqual(drawn, labels[key])
                named = _caption_element_names(sections[key])
                self.assertEqual(len(named), len(set(named)), "an element is explained twice")
                self.assertEqual(sorted(named), sorted(drawn))

    def test_the_caption_heading_is_the_figure_title(self) -> None:
        text = CAPTIONS.read_text(encoding="utf-8")
        for key in FILES:
            with self.subTest(figure=key):
                root = _svg_root(key)
                title = root.find(f"{SVG_NS}title").text
                self.assertIn(f"## {title}\n", text)
                self.assertIn(f"![{title}]({FILES[key]})", text)
                heading = root.find(f"{SVG_NS}g[@data-role='figure-title']")
                self.assertEqual(heading[0].text, title)

    def test_each_figure_states_what_kind_of_numbers_it_shows(self) -> None:
        self.assertIn("SYNTHETIC worked example", _figure_text("B-S2"))
        self.assertIn("SYNTHETIC worked example", _figure_text("B-S4"))
        self.assertIn("Computed from the registered constants", _figure_text("B-S5"))


class RegisteredValueTests(unittest.TestCase):
    """The builder's table of registered values against the registration's text and the code."""

    def test_clock_thresholds_equal_the_registration_block_and_the_hazard_module(self) -> None:
        thresholds = _registered_thresholds()["clock"]
        for name, key in (("clock.h_ms", "h_ms"), ("clock.frequency_margin_ppm", "frequency_margin_ppm"),
                          ("clock.t_stream_max_s", "t_stream_max_s"), ("clock.limit_ms", "limit_ms")):
            with self.subTest(value=name):
                self.assertEqual(builder.reg(name), Fraction(str(thresholds[key])))
                self.assertEqual(builder.reg(name), Fraction(str(clock_hazard.DEFAULT_THRESHOLDS[key])))

    def test_the_registration_still_prints_the_values_the_figures_use(self) -> None:
        text = _squash(_registration())
        sentences = [
            # the gate and its two worked points (section 4.2)
            "3.7 ms + (|f| + 0.25 ppm) × 335 s ≤ 5 ms",
            "block 3's largest half-width 3.6 ms plus a 0.1 ms placement margin",
            f"f = {MINUS}3.17 ppm the bound is 3.7 + 3.42 × 0.335 = 4.846 ms, PASS",
            "at |f| = 3.7 ppm it is 3.7 + 3.95 × 0.335 = 5.023 ms, REFUSE",
            "this holds for |f| ≤ 3.6306 ppm",
            f"On 2026-10-05 f was {MINUS}3.17 ppm",
            "**T_stream_max**, is 335 s",
            # the measurement path (sections 0.2 and 5.8)
            "[adapter, 140 W] --USB-C cable, 28 V--> [KM003C meter]",
            "50 samples/s",
            "B0AC x B0AV, SMC, 1 read/s",
            "one **power record** every 100 ms",
            "Apple M3 Max laptop",
            # the meter's synthetic worked example (section 5.8)
            "a meter mean of 9.0 W and a battery power of 0 W",
            "lasts 20.0 s with a meter mean of 52.0 W and a battery mean of 1.5 W",
            "52.0 × 20 − 9.0 × 20 = 860 J",
            "1.5 × 20 − 0 = 30 J",
            "With ΔE_rail = 712 J, ρ = 712 ÷ 890 = 0.80",
            "712 ÷ 860 = 0.83",
            # the reference members (section 0.12)
            "Each window runs 12 at its start",
            "a **start triplet** (three reference members), one **midpoint reference**, and an **end triplet**",
            "There are three for each triplet",
            "and one for the midpoint",
            "the screen needs n_s ≥ 2 and n_e ≥ 2",
            # the survivors' synthetic worked example (section 0.12)
            "99.62, 99.71, 99.80, 99.88, 99.93, 99.97, 100.04, 100.09, 100.15, 100.22, 100.31, 100.38 J",
            "t(0.975, 11) = 2.201",
            "r1 = 100.02 J, r2 aborted by idle admission",
            "r3 = 99.91 J",
            "`neg8-window-start-spare-1` = 99.95 J",
            "Midpoint 100.20 J",
            "End triplet [100.26, 100.19, 101.08] J",
        ]
        for sentence in sentences:
            with self.subTest(registration_prints=sentence):
                self.assertIn(_squash(sentence), text)

    def test_reference_counts_equal_the_code(self) -> None:
        self.assertEqual(builder.reg("reference.start_members"), whole_window.NEG8_REPLICATED_ENDPOINT_N)
        self.assertEqual(builder.reg("reference.end_members"), whole_window.NEG8_REPLICATED_ENDPOINT_N)
        self.assertEqual(builder.reg("reference.min_endpoint_survivors"), min(whole_window.NEG8_SURVIVOR_ENDPOINT_COUNTS))
        self.assertEqual(builder.reg("reference.midpoint_members"), max(whole_window.NEG8_SURVIVOR_MIDPOINT_COUNTS))
        for stage in ("start", "midpoint", "end"):
            with self.subTest(spares_of=stage):
                self.assertEqual(builder.reg(f"reference.{stage}_spares"), reference_spares.SLOTS[stage][3])
        self.assertEqual(float(builder.reg("reference.t_975_df11")),
                         aggregate.student_t_critical_95(builder.reg("reference.corpus_members") - 1))
        self.assertGreaterEqual(builder.reg("reference.corpus_members"), whole_window.NEG8_DRIFT_MINIMUM_N)

    def test_every_table_entry_names_where_it_was_read(self) -> None:
        for table in (builder.REGISTERED, builder.SYNTHETIC):
            for name, (_, source) in table.items():
                with self.subTest(value=name):
                    self.assertRegex(source, r"^registration §\d+(\.\d+)? l\.\d+")


class FrequencyGateTests(unittest.TestCase):
    """Figure B-S5: the curve and its two worked points, recomputed without the builder's arithmetic."""

    def setUp(self) -> None:
        clock = _registered_thresholds()["clock"]
        self.h = Fraction(str(clock["h_ms"]))
        self.margin = Fraction(str(clock["frequency_margin_ppm"]))
        self.stream = Fraction(str(clock["t_stream_max_s"]))
        self.limit = Fraction(str(clock["limit_ms"]))
        self.thresholds = clock

    def bound_ms(self, abs_f_ppm) -> Fraction:
        # 1 ppm held for 1 s is 1 microsecond; 1000 microseconds are 1 ms.
        return self.h + (Fraction(abs_f_ppm) + self.margin) * self.stream / 1000

    def to_plot(self, abs_f_ppm, bound_ms) -> tuple[float, float]:
        p = builder.GATE_PLOT
        x = p["x0"] + (float(abs_f_ppm) - p["f_min"]) / (p["f_max"] - p["f_min"]) * (p["x1"] - p["x0"])
        y = p["y_bottom"] - (float(bound_ms) - p["ms_min"]) / (p["ms_max"] - p["ms_min"]) * (p["y_bottom"] - p["y_top"])
        return x, y

    def test_the_two_worked_points_and_the_largest_passing_rate(self) -> None:
        point_a, point_b = self.bound_ms("3.17"), self.bound_ms("3.7")
        largest = (self.limit - self.h) * 1000 / self.stream - self.margin
        self.assertEqual(_round(point_a, 3), "4.846")
        self.assertEqual(_round(point_b, 3), "5.023")
        self.assertEqual(_round(largest, 4), "3.6306")
        self.assertLessEqual(point_a, self.limit)
        self.assertGreater(point_b, self.limit)
        self.assertEqual(self.bound_ms(largest), self.limit)
        self.assertEqual(_round(self.bound_ms(0), 3), "3.784")
        printed = builder.worked_values()["B-S5"]
        self.assertEqual(printed, {
            "slope_ms_per_ppm": "0.335", "intercept_ms": "3.784", "pass_bound_ms": "4.846",
            "refuse_bound_ms": "5.023", "max_abs_f_ppm": "3.6306",
        })

    def test_the_production_gate_gives_the_same_verdicts(self) -> None:
        scale = kernel_clock.FREQUENCY_SCALE
        at_zero = clock_hazard.frequency_bound(0, self.thresholds)
        self.assertEqual(f"{at_zero['max_abs_frequency_ppm']:.4f}", "3.6306")
        self.assertEqual(f"{at_zero['bound_ms']:.3f}", "3.784")
        passing = clock_hazard.frequency_bound(-round(3.17 * scale), self.thresholds)
        self.assertTrue(passing["passes"])
        self.assertEqual(f"{passing['bound_ms']:.3f}", "4.846")
        refused = clock_hazard.frequency_bound(round(3.7 * scale), self.thresholds)
        self.assertFalse(refused["passes"])
        self.assertEqual(f"{refused['bound_ms']:.3f}", "5.023")

    def test_the_drawn_marks_sit_where_the_formula_puts_them(self) -> None:
        groups = _groups("B-S5")
        marks = {label: group for label, group in groups if group.get("data-role") == "worked-point"}
        self.assertEqual(sorted(marks), ["Point A", "Point B"])
        expected = {
            "Point A": ("3.17", "PASS", "4.846"),
            "Point B": ("3.7", "REFUSE", "5.023"),
        }
        for label, (rate, verdict, printed) in expected.items():
            with self.subTest(point=label):
                group = marks[label]
                self.assertEqual(group.get("data-abs-f-ppm"), rate)
                self.assertEqual(group.get("data-bound-ms"), printed)
                self.assertEqual(group.get("data-verdict"), verdict)
                x, y = self.to_plot(rate, self.bound_ms(rate))
                circle, diamond = group.find(f"{SVG_NS}circle"), group.find(f"{SVG_NS}polygon")
                if circle is not None:
                    drawn = (float(circle.get("cx")), float(circle.get("cy")))
                else:
                    corners = [tuple(map(float, pair.split(","))) for pair in diamond.get("points").split()]
                    drawn = (statistics.fmean(c[0] for c in corners), statistics.fmean(c[1] for c in corners))
                self.assertAlmostEqual(drawn[0], x, delta=0.011)
                self.assertAlmostEqual(drawn[1], y, delta=0.011)
                self.assertIn(f"{rate} ppm → {printed} ms, {verdict}", _group_text(group))

        single = {label: group for label, group in groups}
        curve = single["predicted bound"].find(f"{SVG_NS}line")
        start, end = self.to_plot(0, self.bound_ms(0)), self.to_plot(5, self.bound_ms(5))
        for attribute, value in (("x1", start[0]), ("y1", start[1]), ("x2", end[0]), ("y2", end[1])):
            self.assertAlmostEqual(float(curve.get(attribute)), value, delta=0.011)
        limit_line = single["5 ms limit"].find(f"{SVG_NS}line")
        _, limit_y = self.to_plot(0, self.limit)
        self.assertEqual(float(limit_line.get("y1")), float(limit_line.get("y2")))
        self.assertAlmostEqual(float(limit_line.get("y1")), limit_y, delta=0.011)
        largest = (self.limit - self.h) * 1000 / self.stream - self.margin
        crossing = [group for label, group in groups if label == "largest passing rate"][0].find(f"{SVG_NS}line")
        self.assertAlmostEqual(float(crossing.get("x1")), self.to_plot(largest, self.limit)[0], delta=0.011)
        self.assertEqual(crossing.get("x1"), crossing.get("x2"))

    def test_the_caption_table_prints_the_same_arithmetic(self) -> None:
        caption = _without_comments(_caption_sections()["B-S5"])
        self.assertIn("3.7 + (3.17 + 0.25) × 0.335 = 4.846 ms | 4.846 ≤ 5 | PASS", caption)
        self.assertIn("3.7 + (3.7 + 0.25) × 0.335 = 5.023 ms | 5.023 > 5 | REFUSE", caption)
        self.assertIn(f"(5 {MINUS} 3.7) ÷ 0.335 {MINUS} 0.25 = 3.6306 ppm", caption)
        self.assertIn("predicted bound = 3.7 ms + (|f| + 0.25 ppm) × 335 s", caption)


class SurvivorExampleTests(unittest.TestCase):
    """Figure B-S4: the synthetic example against the production bound function."""

    def setUp(self) -> None:
        self.corpus = [float(value) for value in builder.syn("reference.corpus_j")]
        self.start = [100.02, 99.91, 99.95]
        self.end = [100.26, 100.19]
        self.printed = builder.worked_values()["B-S4"]

    def test_the_bound_equals_the_production_function(self) -> None:
        realised = whole_window.neg8_count_adjusted_bound(self.corpus, len(self.start), len(self.end))
        planned = whole_window.neg8_count_adjusted_bound(self.corpus, 3, 3)
        self.assertEqual(f"{realised['envelope_j']:.4f}", self.printed["gap_term_j"])
        self.assertEqual(f"{realised['prediction_j']:.4f}", self.printed["repeatability_term_j"])
        self.assertEqual(f"{realised['bound_j']:.4f}", self.printed["bound_j"])
        self.assertEqual(f"{planned['bound_j']:.4f}", self.printed["planned_bound_j"])
        self.assertEqual(f"{statistics.stdev(self.corpus):.4f}", self.printed["stddev_j"])
        self.assertEqual((self.printed["gap_term_j"], self.printed["repeatability_term_j"],
                          self.printed["bound_j"], self.printed["planned_bound_j"]),
                         ("0.6383", "0.4727", "0.6383", "0.5933"))

    def test_the_check_itself(self) -> None:
        ordered = sorted(self.corpus)
        self.assertEqual(f"{statistics.fmean(ordered[-3:]):.4f}", self.printed["upper_start_j"])
        self.assertEqual(f"{statistics.fmean(ordered[:2]):.4f}", self.printed["lower_end_j"])
        start_mean, end_mean = statistics.fmean(self.start), statistics.fmean(self.end)
        self.assertEqual(f"{start_mean:.4f}", self.printed["start_mean_j"])
        self.assertEqual(f"{end_mean:.4f}", self.printed["end_mean_j"])
        self.assertEqual(f"{abs(end_mean - start_mean):.4f}", self.printed["difference_j"])
        self.assertEqual(self.printed["difference_j"], "0.2650")
        bound = whole_window.neg8_count_adjusted_bound(self.corpus, 3, 2)["bound_j"]
        self.assertLessEqual(abs(end_mean - start_mean), bound)
        only_in_caption = builder.caption_values()["B-S4"]
        self.assertEqual(f"{statistics.fmean(ordered[-2:]):.4f}", only_in_caption["upper_end_j"])
        self.assertEqual(f"{statistics.fmean(ordered[:3]):.4f}", only_in_caption["lower_start_j"])
        self.assertEqual(f"{statistics.fmean(ordered[-2:]) - statistics.fmean(ordered[:3]):.4f}",
                         only_in_caption["gap_end_high_j"])
        midpoint = float(builder.syn("reference.midpoint_j"))
        trio = (start_mean, midpoint, end_mean)
        self.assertEqual(f"{max(trio) - min(trio):.4f}", only_in_caption["spread_j"])
        self.assertEqual(f"{max(max(trio) - min(trio), bound):.4f}", only_in_caption["allowance_j"])
        kept_all = statistics.fmean([100.26, 100.19, 101.08])
        self.assertEqual(f"{kept_all:.4f}", only_in_caption["kept_all_end_mean_j"])
        self.assertEqual(f"{kept_all - start_mean:.4f}", only_in_caption["kept_all_difference_j"])

    def test_the_drawn_roster_has_the_registered_counts(self) -> None:
        shapes = {"corpus member": "rect", "reference that survives": "circle", "lost reference": "circle",
                  "spare that ran": "polygon", "spare that did not run": "polygon"}
        counts = {label: 0 for label in shapes}
        for label, group in _groups("B-S4"):
            if label in shapes:
                counts[label] += len(group.findall(f"{SVG_NS}{shapes[label]}"))
        corpus = builder.reg("reference.corpus_members")
        spares = sum(builder.reg(f"reference.{stage}_spares") for stage in ("start", "midpoint", "end"))
        # panel (a) + panel (b) + one in the key
        self.assertEqual(counts["corpus member"], corpus + corpus + 1)
        self.assertEqual(counts["reference that survives"], 5 + 5 + 1)
        self.assertEqual(counts["lost reference"], 2 + 1 + 1)
        self.assertEqual(counts["spare that ran"], 1 + 1 + 1)
        self.assertEqual(counts["spare that did not run"], (spares - 1) + 0 + 1)

    def test_the_two_arrows_are_drawn_to_one_scale(self) -> None:
        position = {}
        for label, group in _groups("B-S4"):
            if label in ("mean of the 2 lowest", "mean of the 3 highest", "start mean", "end mean"):
                position[label] = float(group.find(f"{SVG_NS}line").get("x1"))
        gap = position["mean of the 3 highest"] - position["mean of the 2 lowest"]
        difference = position["end mean"] - position["start mean"]
        self.assertAlmostEqual(difference / gap, 0.2650 / (100.3033333 - 99.665), places=3)


class MeterExampleTests(unittest.TestCase):
    """Figure B-S2: the synthetic rail-share example, recomputed."""

    def test_the_arithmetic(self) -> None:
        idle_meter, idle_battery, seconds, meter, battery, rail = 9.0, 0.0, 20.0, 52.0, 1.5, 712.0
        meter_term = (meter - idle_meter) * seconds
        battery_term = (battery - idle_battery) * seconds
        printed = builder.worked_values()["B-S2"]
        self.assertEqual(printed, {
            "meter_term_j": f"{meter_term:.0f}", "battery_term_j": f"{battery_term:.0f}",
            "machine_energy_j": f"{meter_term + battery_term:.0f}", "rail_energy_j": f"{rail:.0f}",
            "rail_share": f"{rail / (meter_term + battery_term):.2f}",
            "rail_share_without_battery": f"{rail / meter_term:.2f}",
        })
        self.assertEqual((printed["meter_term_j"], printed["battery_term_j"], printed["machine_energy_j"],
                          printed["rail_share"], printed["rail_share_without_battery"]),
                         ("860", "30", "890", "0.80", "0.83"))


class PrintedNumberTests(unittest.TestCase):
    def test_figure_and_caption_print_every_computed_number(self) -> None:
        sections = _caption_sections()
        for key in FILES:
            figure, caption = _figure_text(key), _without_comments(sections[key])
            for name, value in builder.worked_values()[key].items():
                with self.subTest(figure=key, number=name):
                    self.assertRegex(figure, rf"(?<![\d.]){re.escape(value)}(?!\d)")
                    self.assertRegex(caption, rf"(?<![\d.]){re.escape(value)}(?!\d)")
            for name, value in builder.caption_values()[key].items():
                with self.subTest(figure=key, caption_only=name):
                    self.assertRegex(caption, rf"(?<![\d.]){re.escape(value)}(?!\d)")


class CaptionProseTests(unittest.TestCase):
    SHORTHAND = (r"NEG-8", r"\bALPHA\b", r"\bBETA\b", r"\bGAMMA\b", r"\bint5\b", r"H_claim", r"cold pass",
                 r"\bcold gate\b", r"magistrate", r"\bD-\d+", r"\blane\b", r"\bblock \d", r"\bharvest\b",
                 r"\bthesis\b", r"B0A[CV]", r"\bSMC\b", r"ΔE", r"ρ")

    def test_project_shorthand_appears_only_inside_parentheses(self) -> None:
        prose = _without_comments(CAPTIONS.read_text(encoding="utf-8"))
        prose = re.sub(r"`[^`\n]*`", "", prose)
        for paragraph in re.split(r"\n\s*\n", prose):
            depth, inside = 0, []
            for char in paragraph:
                if char == "(":
                    depth += 1
                inside.append(depth > 0)
                if char == ")":
                    depth = max(depth - 1, 0)
            for pattern in self.SHORTHAND:
                for match in re.finditer(pattern, paragraph):
                    with self.subTest(shorthand=match.group(0), near=paragraph[max(match.start() - 40, 0):match.end() + 20]):
                        self.assertTrue(inside[match.start()], "project shorthand outside parentheses")

    def test_the_figures_print_no_project_shorthand(self) -> None:
        for key in FILES:
            text = _figure_text(key)
            for pattern in self.SHORTHAND:
                with self.subTest(figure=key, shorthand=pattern):
                    self.assertIsNone(re.search(pattern, text))

    def test_no_dash_chains_and_no_result_slots_are_needed(self) -> None:
        text = CAPTIONS.read_text(encoding="utf-8")
        self.assertNotIn("\N{EM DASH}", text)
        self.assertNotIn("{{slot:", text)
        for key in FILES:
            self.assertNotIn("\N{EM DASH}", _figure_text(key))


if __name__ == "__main__":
    unittest.main()
