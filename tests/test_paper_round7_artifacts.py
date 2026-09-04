"""Tests for the round-7 DX artifact fence.

The always-on tests read every digest, field path, rendering rule, and expected
value from the registry parser exported by the fence; this file intentionally
contains no pinned digest.  Figure 4 stores coordinates to 0.01 px, so the
fence's 0.0008 ms y tolerance is the upward-rounded half-unit inversion
``0.005 px * 50 ms / 326 px``; its x tolerance is derived the same way.

The replay test is corpus-gated, like the Section 2 fence test.  A skip is not a
pass: the CLI test separately proves that an absent corpus exits 3 and names
the missing path.  ``R7F_CORPUS_ROOT`` overrides the corpus root; point it at a
directory without the corpus to skip the ~8-minute replay locally.
"""

from __future__ import annotations

import copy
from contextlib import redirect_stderr, redirect_stdout
from decimal import Decimal
import hashlib
import importlib.util
import io
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
FENCE_PATH = ROOT / "scripts" / "check_paper_round7_artifacts.py"
REGISTRY_PATH = Path(
    os.environ.get("R7F_REGISTRY", ROOT / "docs" / "paper" / "results-fill-registry.md")
)
SKELETON_PATH = ROOT / "docs" / "paper" / "draft-v2-skeleton.md"
CHECKLIST_PATH = ROOT / "docs" / "paper" / "round7" / "fill-checklist.md"
CORPUS_ROOT = Path(
    os.environ.get("R7F_CORPUS_ROOT", "/Users/edr/code/JouleWise")
)
SCRATCH_PARENT = Path(os.environ.get("TMPDIR", tempfile.gettempdir()))

FENCE_SPEC = importlib.util.spec_from_file_location("check_paper_round7_artifacts", FENCE_PATH)
assert FENCE_SPEC is not None and FENCE_SPEC.loader is not None
FENCE = importlib.util.module_from_spec(FENCE_SPEC)
sys.modules[FENCE_SPEC.name] = FENCE
FENCE_SPEC.loader.exec_module(FENCE)

AS_PATH = ROOT / "scripts" / "paper_anchor_correction_quantified.py"
AS_SPEC = importlib.util.spec_from_file_location(
    "paper_anchor_correction_quantified", AS_PATH
)
assert AS_SPEC is not None and AS_SPEC.loader is not None
ANCHOR = importlib.util.module_from_spec(AS_SPEC)
sys.modules[AS_SPEC.name] = ANCHOR
AS_SPEC.loader.exec_module(ANCHOR)

CORPUS_PRESENT = all(
    path.exists()
    for path in (
        CORPUS_ROOT
        / "runs_window_a_20260722"
        / "instrument_validation"
        / "20260722T145535-e941c821"
        / "instrument_evidence.json",
        CORPUS_ROOT
        / "runs_window_a_20260722"
        / "instrument_validation"
        / "20260722T145535-e941c821"
        / "raw"
        / "powermetrics.plist",
        CORPUS_ROOT / "runs" / "instrument_validation",
    )
)


def _copy_checker_inputs(root: Path) -> None:
    paths = [
        FENCE.REGISTRY_RELATIVE_PATH,
        FENCE.SKELETON_RELATIVE_PATH,
        FENCE.EXPECTED_R7F_PATH,
        *FENCE.EXPECTED_SOURCE_PATHS.values(),
    ]
    for relative_path in paths:
        target = root / relative_path
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(ROOT / relative_path, target)


def _update_scratch_json_pin(root: Path, code: str) -> None:
    artifact_path = root / FENCE.EXPECTED_SOURCE_PATHS[code]
    registry_path = root / FENCE.REGISTRY_RELATIVE_PATH
    registry_text = registry_path.read_text(encoding="utf-8")
    old_pin = FENCE.parse_registry_text(registry_text).sources[code]
    new_sha256 = hashlib.sha256(artifact_path.read_bytes()).hexdigest()
    new_size = artifact_path.stat().st_size
    registry_text = registry_text.replace(old_pin.sha256, new_sha256)
    old_source = (
        f"- {code} = {old_pin.path}, sha256 {new_sha256} "
        f"({old_pin.size:,} B)"
    )
    new_source = f"- {code} = {old_pin.path}, sha256 {new_sha256} ({new_size:,} B)"
    if old_source not in registry_text:
        raise AssertionError(f"scratch {code} source pin was not found")
    registry_path.write_text(
        registry_text.replace(old_source, new_source, 1), encoding="utf-8"
    )


def _update_scratch_aq_pin(root: Path) -> None:
    _update_scratch_json_pin(root, "AQ")


def _run_scratch_checker(root: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            sys.executable,
            str(FENCE_PATH),
            "--repository-root",
            str(root),
            "--registry",
            str(root / FENCE.REGISTRY_RELATIVE_PATH),
            "--skeleton",
            str(root / FENCE.SKELETON_RELATIVE_PATH),
            "--literals-only",
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )


def _registry_with_current_source_pins(directory: Path) -> Path:
    """Make an audit registry whose producer pins follow this in-flight diff."""

    registry_text = REGISTRY_PATH.read_text(encoding="utf-8")
    spec = FENCE.parse_registry_text(registry_text)
    for code in ("XS", "AS"):
        current_sha256 = hashlib.sha256(
            (ROOT / spec.sources[code].path).read_bytes()
        ).hexdigest()
        registry_text = registry_text.replace(
            spec.sources[code].sha256, current_sha256, 1
        )
    path = directory / "results-fill-registry.md"
    path.write_text(registry_text, encoding="utf-8")
    return path


class RegistryAndDigestTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.text = REGISTRY_PATH.read_text(encoding="utf-8")
        cls.spec = FENCE.parse_registry_text(cls.text)
        cls.artifacts, json_checks = FENCE.load_json_artifacts(ROOT, cls.spec)
        if not all(check.match for check in json_checks):
            raise AssertionError(json_checks)

    def test_registry_has_the_closed_dx_row_set(self) -> None:
        self.assertEqual(tuple(self.spec.rows), FENCE.EXPECTED_DX_IDS)
        self.assertEqual(len(self.spec.rows), 19)

    def test_registry_pinned_files_match(self) -> None:
        comparisons = FENCE.check_file_pins(ROOT, self.spec)
        self.assertTrue(all(row.match for row in comparisons), comparisons)

    def test_every_supplier_field_resolves(self) -> None:
        comparisons = FENCE.check_supplier_fields(self.spec, self.artifacts)
        self.assertGreater(len(comparisons), len(self.spec.rows))
        self.assertTrue(all(row.match for row in comparisons), comparisons)

    def test_every_registry_marker_renders_from_its_supplier(self) -> None:
        comparisons = FENCE.check_rendered_rows(self.spec, self.artifacts)
        self.assertEqual(
            len(comparisons), len(self.spec.rows) - len(FENCE.IDENTITY_ROWS)
        )
        self.assertTrue(all(row.match for row in comparisons), comparisons)

    def test_identity_rows_are_checked_by_file_pins_only(self) -> None:
        comparisons = FENCE.check_file_pins(ROOT, self.spec)
        identity_labels = {
            row.label for row in comparisons if row.label.startswith("identity DX-")
        }
        self.assertEqual(
            identity_labels,
            {f"identity {row_id}" for row_id in FENCE.IDENTITY_ROWS},
        )

    def test_artifact_gates_are_true(self) -> None:
        comparisons = FENCE.check_gates(self.artifacts)
        self.assertEqual(len(comparisons), 3)
        self.assertTrue(all(row.match for row in comparisons), comparisons)

    def test_every_governed_gate_names_a_registered_dx_row(self) -> None:
        governed = [row_id for _source, _path, row_id in FENCE.GATE_SPECS if row_id]
        self.assertEqual(governed, ["DX-002"])
        for row_id in governed:
            self.assertIn(row_id, self.spec.rows)

    def test_all_118_figure_marks_invert_to_xd(self) -> None:
        comparisons = FENCE.check_figure(ROOT, self.spec, self.artifacts)
        marks = [row for row in comparisons if re.fullmatch(r"figure (?:onset|offset) mark [0-9]+", row.label)]
        self.assertEqual(len(marks), 118)
        self.assertTrue(all(row.match for row in comparisons), comparisons)

    def test_current_skeleton_has_no_malformed_dx_literal(self) -> None:
        comparisons = FENCE.check_skeleton_literals(
            SKELETON_PATH.read_text(encoding="utf-8"), self.spec
        )
        self.assertTrue(all(row.match for row in comparisons), comparisons)

    def test_comparison_requires_identical_python_types(self) -> None:
        for expected, observed in ((True, 1), (True, 1.0), (1, 1.0)):
            with self.subTest(expected=expected, observed=observed):
                self.assertFalse(FENCE._comparison("x", expected, observed).match)
        self.assertTrue(
            FENCE._comparison("x", Decimal("1"), Decimal("1.0")).match
        )

    def test_typed_resolver_accepts_and_refuses_dictated_shapes(self) -> None:
        rejected = {
            "int": (Decimal("15.9"), Decimal("15.0"), True, "15", None),
            "number": ("4.05", True, None, []),
            "bool": (1, Decimal("1.0"), "true", None),
            "str": (1, True, None),
        }
        for kind, values in rejected.items():
            for value in values:
                with self.subTest(kind=kind, value=value):
                    with self.assertRaises(ValueError) as raised:
                        FENCE._typed(value, kind, "SRC#path")
                    self.assertEqual(
                        str(raised.exception),
                        f"SRC#path: expected {kind}, found "
                        f"{type(value).__name__}: {value!r}",
                    )

        accepted = (
            (15, "int", 15, int),
            (15, "number", Decimal(15), Decimal),
            (Decimal("4.05"), "number", Decimal("4.05"), Decimal),
            (True, "bool", True, bool),
            ("x", "str", "x", str),
        )
        for value, kind, expected, expected_type in accepted:
            with self.subTest(kind=kind, value=value):
                observed = FENCE._typed(value, kind, "SRC#path")
                self.assertEqual(observed, expected)
                self.assertIs(type(observed), expected_type)

    def test_placement_rows_are_the_16_parsed_nonidentity_rows(self) -> None:
        expected = {
            *(f"DX-{number:03d}" for number in range(10, 18)),
            *(f"DX-{number:03d}" for number in range(20, 28)),
        }
        self.assertEqual(set(FENCE._placement_row_ids(self.spec)), expected)
        self.assertEqual(len(FENCE._placement_row_ids(self.spec)), 16)

    def test_standing_sentence_head_is_pinned_to_the_registry(self) -> None:
        self.assertIn(FENCE.DX_STANDING_SENTENCE_HEAD, self.text)

    def test_current_skeleton_passes_zero_placement_census(self) -> None:
        skeleton_text = SKELETON_PATH.read_text(encoding="utf-8")
        comparisons = FENCE.check_placement(skeleton_text, self.spec)
        self.assertEqual(len(comparisons), 1)
        self.assertTrue(comparisons[0].match, comparisons)
        self.assertEqual(FENCE._placed_row_count(skeleton_text, self.spec), 0)


class RefusalTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.text = REGISTRY_PATH.read_text(encoding="utf-8")
        cls.spec = FENCE.parse_registry_text(cls.text)
        cls.artifacts, _ = FENCE.load_json_artifacts(ROOT, cls.spec)

    def test_malformed_dx_row_is_refused(self) -> None:
        original = next(line for line in self.text.splitlines() if line.startswith("| DX-010 "))
        mutated = original.replace("| MEASURED |", "| UNKNOWN |")
        self.assertNotEqual(mutated, original)
        with self.assertRaises(FENCE.RegistryError):
            FENCE.parse_registry_text(self.text.replace(original, mutated, 1))

    def test_altered_registered_digest_is_refused(self) -> None:
        digest = self.spec.sources["XD"].sha256
        replacement = ("0" if digest[0] != "0" else "1") + digest[1:]
        mutated_text = self.text.replace(digest, replacement)
        mutated_spec = FENCE.parse_registry_text(mutated_text)
        comparisons = FENCE.check_file_pins(ROOT, mutated_spec)
        self.assertTrue(any(not row.match and row.label == "digest XD" for row in comparisons))

    def test_altered_json_field_is_refused(self) -> None:
        artifacts = copy.deepcopy(self.artifacts)
        artifacts["XD"]["summary"]["onset_best_fit_lag"]["median_ms"] = 13.1
        comparisons = FENCE.check_rendered_rows(self.spec, artifacts)
        self.assertTrue(any(not row.match and row.label == "row DX-010" for row in comparisons))

    def test_altered_registry_value_is_refused(self) -> None:
        original = next(line for line in self.text.splitlines() if line.startswith("| DX-010 "))
        mutated = original.replace("| +13.0 ms |", "| +13.1 ms |")
        self.assertNotEqual(mutated, original)
        spec = FENCE.parse_registry_text(self.text.replace(original, mutated, 1))
        comparisons = FENCE.check_rendered_rows(spec, self.artifacts)
        self.assertTrue(any(not row.match and row.label == "row DX-010" for row in comparisons))

    def test_altered_successor_literal_is_refused(self) -> None:
        comparisons = FENCE.check_skeleton_literals("[FILL:DX-010] +13.1 ms\n", self.spec)
        self.assertEqual(len(comparisons), 1)
        self.assertFalse(comparisons[0].match)

    def test_exact_successor_literal_is_accepted(self) -> None:
        comparisons = FENCE.check_skeleton_literals("[FILL:DX-010] +13.0 ms\n", self.spec)
        self.assertEqual(len(comparisons), 1)
        self.assertTrue(comparisons[0].match)

    def test_bare_successor_literals_reject_ambiguous_continuations(self) -> None:
        cases = (
            ("DX-020", "150 captures"),
            ("DX-012", "59 of 599 pulses"),
            ("DX-026", "4.05 %%%"),
        )
        for row_id, literal in cases:
            with self.subTest(row_id=row_id):
                comparisons = FENCE.check_skeleton_literals(
                    f"[FILL:{row_id}] {literal}\n", self.spec
                )
                self.assertEqual(len(comparisons), 1)
                self.assertFalse(comparisons[0].match)
                self.assertEqual(comparisons[0].observed, literal)

    def test_exact_bare_and_backticked_successor_literals_are_accepted(self) -> None:
        for row_id in ("DX-020", "DX-012", "DX-026"):
            expected = self.spec.rows[row_id].marker
            for rendered in (expected, f"`{expected}`"):
                with self.subTest(row_id=row_id, rendered=rendered):
                    comparisons = FENCE.check_skeleton_literals(
                        f"[FILL:{row_id}] {rendered}\n", self.spec
                    )
                    self.assertEqual(len(comparisons), 1)
                    self.assertTrue(comparisons[0].match, comparisons)

    def test_legacy_literal_separator_is_not_stripped(self) -> None:
        comparisons = FENCE.check_skeleton_literals(
            "[FILL:DX-020] = 15\n", self.spec
        )
        self.assertEqual(len(comparisons), 1)
        self.assertFalse(comparisons[0].match)

    def test_count_aware_bucket_wording_and_refused_failure_count(self) -> None:
        artifacts = copy.deepcopy(self.artifacts)
        summary = artifacts["AQ"]["summary"]

        summary["v3_derived_count"] = 13
        summary["v3_refused_count"] = 2
        summary["v3_refusals_by_token"]["anchor_unresolved"] = ["a", "b"]
        rendered = FENCE.render_row(
            self.spec.rows["DX-021"], self.spec, artifacts
        )
        self.assertEqual(rendered, "13 derived / 2 refused (both anchor_unresolved)")

        summary["admissibility_flip_count"] = 3
        summary["admissibility_flips"] = [
            {"flip_direction": "refused_by_v3"} for _ in range(3)
        ]
        rendered = FENCE.render_row(
            self.spec.rows["DX-022"], self.spec, artifacts
        )
        self.assertEqual(rendered, "3 (all refused_by_v3)")

        summary["control_v2_reproduction_failures"] = ["a", "b"]
        comparisons = FENCE.check_rendered_rows(self.spec, artifacts)
        control = next(row for row in comparisons if row.label == "row DX-023")
        self.assertFalse(control.match)
        self.assertIn("REFUSED", control.observed)
        self.assertIn("failure count is 2", control.observed)

    def test_non_mapping_per_pulse_entry_is_refused_without_traceback(self) -> None:
        artifacts = copy.deepcopy(self.artifacts)
        artifacts["XD"]["per_pulse"][0] = "not-a-pulse-record"
        figure_comparisons = FENCE.check_figure(ROOT, self.spec, artifacts)
        refused = [row for row in figure_comparisons if not row.match]
        self.assertTrue(refused)
        self.assertTrue(all(row.observed.startswith("REFUSED") for row in refused))

        output = io.StringIO()
        with mock.patch.object(
            FENCE, "digest_half", return_value=(self.spec, figure_comparisons)
        ), redirect_stdout(output):
            exit_code = FENCE.main(["--literals-only"])
        self.assertEqual(exit_code, 2, output.getvalue())
        self.assertNotIn("Traceback", output.getvalue())

    def test_as_filenotfounderror_is_a_producer_failure_not_unavailable(self) -> None:
        def fake_run(
            command: list[str], repository_root: Path
        ) -> subprocess.CompletedProcess[str]:
            if str(FENCE.EXPECTED_SOURCE_PATHS["XS"]) in command[1]:
                out = Path(command[command.index("--out") + 1])
                svg = Path(command[command.index("--svg") + 1])
                out.write_bytes((ROOT / FENCE.EXPECTED_SOURCE_PATHS["XD"]).read_bytes())
                svg.write_bytes((ROOT / FENCE.EXPECTED_SOURCE_PATHS["F4"]).read_bytes())
                return subprocess.CompletedProcess(command, 0, "", "")
            return subprocess.CompletedProcess(
                command,
                1,
                "",
                "Traceback (most recent call last):\n"
                "FileNotFoundError: [Errno 2] No such file or directory: out parent\n",
            )

        output = io.StringIO()
        with mock.patch.object(FENCE, "digest_half", return_value=(self.spec, [])), mock.patch.object(
            FENCE, "_required_corpus_paths", return_value=[]
        ), mock.patch.object(FENCE, "_run_producer", side_effect=fake_run), redirect_stdout(output):
            exit_code = FENCE.main(["--corpus-root", str(ROOT)])

        self.assertEqual(exit_code, 2, output.getvalue())
        self.assertIn("MISMATCH replay AS exit", output.getvalue())
        self.assertIn("FileNotFoundError", output.getvalue())
        self.assertNotIn("R7F CORPUS UNAVAILABLE", output.getvalue())

    def test_as_population_unavailable_exits_three(self) -> None:
        error = ANCHOR.PopulationUnavailable("/missing/population")
        stderr = io.StringIO()
        with mock.patch.object(ANCHOR, "build_payload", side_effect=error), redirect_stderr(
            stderr
        ):
            exit_code = ANCHOR.main(
                [
                    "--corpus-root",
                    "/missing",
                    "--out",
                    str(SCRATCH_PARENT / "not-written.json"),
                ]
            )
        self.assertEqual(exit_code, 3)
        self.assertEqual(
            stderr.getvalue(), "population unavailable: /missing/population\n"
        )

    def test_bad_repository_root_flag_in_pinned_command_fails_replay(self) -> None:
        mutated = FENCE.F4_REPLAY_COMMAND.replace(
            "scripts/paper_excursion_decomposition.py ",
            "scripts/paper_excursion_decomposition.py --repository-rooot nowhere ",
            1,
        )
        self.assertNotEqual(mutated, FENCE.F4_REPLAY_COMMAND)

        def reject_unknown_flag(
            command: list[str], repository_root: Path
        ) -> subprocess.CompletedProcess[str]:
            self.assertIn("--repository-rooot", command)
            return subprocess.CompletedProcess(
                command, 2, "", "error: unrecognized arguments: --repository-rooot\n"
            )

        with mock.patch.object(FENCE, "F4_REPLAY_COMMAND", mutated), mock.patch.object(
            FENCE, "_required_corpus_paths", return_value=[]
        ), mock.patch.object(FENCE, "_run_producer", side_effect=reject_unknown_flag):
            comparisons = FENCE.replay_half(ROOT, ROOT, self.spec)

        self.assertEqual(len(comparisons), 1)
        self.assertEqual(comparisons[0].label, "replay XS exit")
        self.assertFalse(comparisons[0].match)

    def test_renamed_out_flag_in_pinned_command_is_refused(self) -> None:
        mutated = FENCE.F4_REPLAY_COMMAND.replace("--out ", "--outt ", 1)
        self.assertNotEqual(mutated, FENCE.F4_REPLAY_COMMAND)
        with mock.patch.object(FENCE, "F4_REPLAY_COMMAND", mutated), mock.patch.object(
            FENCE, "_required_corpus_paths", return_value=[]
        ):
            comparisons = FENCE.replay_half(ROOT, ROOT, self.spec)

        self.assertEqual(len(comparisons), 1)
        self.assertEqual(comparisons[0].label, "replay F4 command")
        self.assertFalse(comparisons[0].match)
        self.assertEqual(
            comparisons[0].observed,
            "pinned F4 command must contain exactly one --out",
        )

    def test_missing_json_is_refused(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for code, pin in self.spec.sources.items():
                if code == "XD":
                    continue
                target = root / pin.path
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(ROOT / pin.path, target)
            comparisons = FENCE.check_file_pins(root, self.spec)
            self.assertTrue(any(not row.match and row.label == "digest XD" for row in comparisons))
            artifacts, json_checks = FENCE.load_json_artifacts(root, self.spec)
            self.assertNotIn("XD", artifacts)
            self.assertTrue(any(not row.match and row.label == "JSON XD" for row in json_checks))

    def test_fractional_population_size_reissue_is_refused(self) -> None:
        with tempfile.TemporaryDirectory(
            prefix="r7f-fractional-population-", dir=SCRATCH_PARENT
        ) as directory:
            root = Path(directory)
            _copy_checker_inputs(root)
            aq_path = root / FENCE.EXPECTED_SOURCE_PATHS["AQ"]
            aq_text = aq_path.read_text(encoding="utf-8")
            mutated = aq_text.replace(
                '"population_size": 15,', '"population_size": 15.9,', 1
            )
            self.assertNotEqual(mutated, aq_text)
            aq_path.write_text(mutated, encoding="utf-8")
            _update_scratch_aq_pin(root)

            completed = _run_scratch_checker(root)

        output = completed.stdout + completed.stderr
        self.assertEqual(completed.returncode, 2, output)
        self.assertIn("row DX-020", output)
        self.assertIn("AQ#summary.population_size", output)

    def test_extra_v3_refusal_bucket_reissue_is_refused(self) -> None:
        with tempfile.TemporaryDirectory(
            prefix="r7f-extra-refusal-bucket-", dir=SCRATCH_PARENT
        ) as directory:
            root = Path(directory)
            _copy_checker_inputs(root)
            aq_path = root / FENCE.EXPECTED_SOURCE_PATHS["AQ"]
            payload = json.loads(aq_path.read_text(encoding="utf-8"))
            payload["summary"]["v3_refusals_by_token"]["other_refusal"] = [
                "not-an-anchor-unresolved-row"
            ]
            aq_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
            _update_scratch_aq_pin(root)

            completed = _run_scratch_checker(root)

        output = completed.stdout + completed.stderr
        self.assertEqual(completed.returncode, 2, output)
        self.assertIn("row DX-021", output)
        self.assertIn("AQ#summary.v3_refusals_by_token", output)

    def test_dx003_without_svg_in_full_replay_command_is_refused(self) -> None:
        with tempfile.TemporaryDirectory(
            prefix="r7f-f4-command-", dir=SCRATCH_PARENT
        ) as directory:
            root = Path(directory)
            _copy_checker_inputs(root)
            registry_path = root / FENCE.REGISTRY_RELATIVE_PATH
            registry_text = registry_path.read_text(encoding="utf-8")
            mutated = registry_text.replace(
                " --svg docs/paper/figures/fig4_edge_excursions.svg", "", 1
            )
            self.assertNotEqual(mutated, registry_text)
            registry_path.write_text(mutated, encoding="utf-8")

            completed = _run_scratch_checker(root)

        output = completed.stdout + completed.stderr
        self.assertEqual(completed.returncode, 2, output)
        self.assertIn("DX-003", output)
        self.assertIn("full F4 replay command including --svg", output)

    def test_dx027_unsigned_percent_renderer_is_refused(self) -> None:
        with tempfile.TemporaryDirectory(
            prefix="r7f-unsigned-median-percent-", dir=SCRATCH_PARENT
        ) as directory:
            root = Path(directory)
            _copy_checker_inputs(root)
            registry_path = root / FENCE.REGISTRY_RELATIVE_PATH
            registry_text = registry_path.read_text(encoding="utf-8")
            current = next(
                line for line in registry_text.splitlines() if line.startswith("| DX-027 ")
            )
            mutated = current.replace("| +0.61 % |", "| 0.61 % |").replace(
                "render an explicit sign and two decimals followed by ` %`; "
                "`R7F_RENDER=signed_2_percent`",
                "round once to two decimals and append ` %`; "
                "`R7F_RENDER=fixed_2_percent`",
            )
            self.assertNotEqual(mutated, current)
            registry_path.write_text(
                registry_text.replace(current, mutated, 1), encoding="utf-8"
            )

            completed = _run_scratch_checker(root)

        output = completed.stdout + completed.stderr
        self.assertEqual(completed.returncode, 2, output)
        self.assertIn("DX-027", output)
        self.assertIn("R7F_RENDER=signed_2_percent", output)


class TypedArtifactCliTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.spec = FENCE.parse_registry(REGISTRY_PATH)

    def test_multiline_producer_unavailable_is_flattened_to_last_line(self) -> None:
        completed_producer = subprocess.CompletedProcess(
            ["stub-producer"],
            3,
            "producer line one\nproducer line two\n",
            "",
        )
        output = io.StringIO()
        with (
            mock.patch.object(FENCE, "digest_half", return_value=(self.spec, [])),
            mock.patch.object(FENCE, "_required_corpus_paths", return_value=[]),
            mock.patch.object(FENCE, "_run_producer", return_value=completed_producer),
            redirect_stdout(output),
        ):
            exit_code = FENCE.main(["--corpus-root", str(ROOT)])

        lines = output.getvalue().splitlines()
        self.assertEqual(exit_code, 3, output.getvalue())
        self.assertTrue(
            lines[-1].startswith("R7F CORPUS UNAVAILABLE: "), output.getvalue()
        )
        self.assertIn("producer line one | producer line two", lines[-1])
        self.assertFalse(any("COMPARED" in line for line in lines))

    def test_string_number_in_aq_is_refused_by_dx026(self) -> None:
        with tempfile.TemporaryDirectory(
            prefix="r7f-aq-string-number-", dir=SCRATCH_PARENT
        ) as directory:
            root = Path(directory)
            _copy_checker_inputs(root)
            aq_path = root / FENCE.EXPECTED_SOURCE_PATHS["AQ"]
            aq_text = aq_path.read_text(encoding="utf-8")
            mutated = aq_text.replace(
                '"max_absolute_pct": 4.046812,',
                '"max_absolute_pct": "4.046812",',
                1,
            )
            self.assertNotEqual(mutated, aq_text)
            aq_path.write_text(mutated, encoding="utf-8")
            _update_scratch_json_pin(root, "AQ")

            completed = _run_scratch_checker(root)

        output = completed.stdout + completed.stderr
        self.assertEqual(completed.returncode, 2, output)
        self.assertIn("row DX-026", output)
        self.assertIn("expected number, found str", output)

    def test_integer_bool_in_xd_is_refused_by_gate(self) -> None:
        self.assertFalse(FENCE._comparison("P2 bool/int", True, 1).match)
        with tempfile.TemporaryDirectory(
            prefix="r7f-xd-int-bool-", dir=SCRATCH_PARENT
        ) as directory:
            root = Path(directory)
            _copy_checker_inputs(root)
            xd_path = root / FENCE.EXPECTED_SOURCE_PATHS["XD"]
            xd_text = xd_path.read_text(encoding="utf-8")
            mutated = xd_text.replace(
                '"b_fiducial_s_matches_exactly": true,',
                '"b_fiducial_s_matches_exactly": 1,',
                1,
            )
            self.assertNotEqual(mutated, xd_text)
            xd_path.write_text(mutated, encoding="utf-8")
            _update_scratch_json_pin(root, "XD")

            completed = _run_scratch_checker(root)

        output = completed.stdout + completed.stderr
        self.assertEqual(completed.returncode, 2, output)
        self.assertIn("gate XD#calibration_gate.b_fiducial_s_matches_exactly", output)
        self.assertIn("expected bool, found int", output)

    def test_string_per_pulse_number_is_refused_by_figure(self) -> None:
        with tempfile.TemporaryDirectory(
            prefix="r7f-xd-string-pulse-", dir=SCRATCH_PARENT
        ) as directory:
            root = Path(directory)
            _copy_checker_inputs(root)
            xd_path = root / FENCE.EXPECTED_SOURCE_PATHS["XD"]
            xd_text = xd_path.read_text(encoding="utf-8")
            mutated = xd_text.replace(
                '"onset_best_fit_lag_ms": 16.0,',
                '"onset_best_fit_lag_ms": "16.0",',
                1,
            )
            self.assertNotEqual(mutated, xd_text)
            xd_path.write_text(mutated, encoding="utf-8")
            _update_scratch_json_pin(root, "XD")

            completed = _run_scratch_checker(root)

        output = completed.stdout + completed.stderr
        self.assertEqual(completed.returncode, 2, output)
        self.assertIn("figure onset mark 0", output)
        self.assertIn("expected number, found str", output)

    def test_json_integer_is_accepted_for_number_and_renders_unchanged(self) -> None:
        with tempfile.TemporaryDirectory(
            prefix="r7f-xd-integer-number-", dir=SCRATCH_PARENT
        ) as directory:
            root = Path(directory)
            _copy_checker_inputs(root)
            xd_path = root / FENCE.EXPECTED_SOURCE_PATHS["XD"]
            xd_text = xd_path.read_text(encoding="utf-8")
            mutated = xd_text.replace(
                '"median_absolute_deviation_ms": 4.0,',
                '"median_absolute_deviation_ms": 4,',
                1,
            )
            self.assertNotEqual(mutated, xd_text)
            xd_path.write_text(mutated, encoding="utf-8")
            _update_scratch_json_pin(root, "XD")

            completed = _run_scratch_checker(root)

        output = completed.stdout + completed.stderr
        self.assertEqual(completed.returncode, 0, output)
        self.assertIn("ok   row DX-015", output)

    def test_decimal_loader_preserves_fixed_literal_across_float_roundtrip_edge(self) -> None:
        token = "1.0000014999999999999999"
        self.assertEqual(f"{Decimal(token):.6f}", "1.000001")
        self.assertEqual(f"{Decimal(str(float(token))):.6f}", "1.000002")
        with tempfile.TemporaryDirectory(
            prefix="r7f-aq-decimal-token-", dir=SCRATCH_PARENT
        ) as directory:
            root = Path(directory)
            _copy_checker_inputs(root)
            aq_path = root / FENCE.EXPECTED_SOURCE_PATHS["AQ"]
            aq_text = aq_path.read_text(encoding="utf-8")
            mutated = aq_text.replace(
                '"max_absolute_ms": 1.090519,',
                f'"max_absolute_ms": {token},',
                1,
            )
            self.assertNotEqual(mutated, aq_text)
            aq_path.write_text(mutated, encoding="utf-8")

            registry_path = root / FENCE.REGISTRY_RELATIVE_PATH
            registry_text = registry_path.read_text(encoding="utf-8")
            mutated_registry = registry_text.replace(
                "| 1.090519 ms |", "| 1.000001 ms |", 1
            )
            self.assertNotEqual(mutated_registry, registry_text)
            registry_path.write_text(mutated_registry, encoding="utf-8")
            _update_scratch_json_pin(root, "AQ")

            artifacts, json_checks = FENCE.load_json_artifacts(
                root, FENCE.parse_registry(registry_path)
            )
            self.assertTrue(all(check.match for check in json_checks), json_checks)
            loaded = artifacts["AQ"]["summary"]["delta_v3_vs_stored_absolute"][
                "max_absolute_ms"
            ]
            self.assertIs(type(loaded), Decimal)
            self.assertEqual(loaded, Decimal(token))
            completed = _run_scratch_checker(root)

        output = completed.stdout + completed.stderr
        self.assertEqual(completed.returncode, 0, output)
        self.assertIn("ok   row DX-025", output)

    def test_standing_sentence_with_15_markers_refuses_the_16th(self) -> None:
        row_ids = FENCE._placement_row_ids(self.spec)
        missing = row_ids[-1]
        skeleton = [FENCE.DX_STANDING_SENTENCE_HEAD]
        skeleton.extend(
            f"[FILL:{row_id}] {self.spec.rows[row_id].marker}"
            for row_id in row_ids[:-1]
        )
        with tempfile.TemporaryDirectory(
            prefix="r7f-placement-missing-", dir=SCRATCH_PARENT
        ) as directory:
            root = Path(directory)
            _copy_checker_inputs(root)
            (root / FENCE.SKELETON_RELATIVE_PATH).write_text(
                "\n".join(skeleton) + "\n", encoding="utf-8"
            )
            completed = _run_scratch_checker(root)

        output = completed.stdout + completed.stderr
        self.assertEqual(completed.returncode, 2, output)
        self.assertIn(f"MISMATCH placement {missing}", output)
        self.assertIn("R7F PLACED 15/16", output)

    def test_marker_without_standing_sentence_is_refused(self) -> None:
        with tempfile.TemporaryDirectory(
            prefix="r7f-placement-no-standing-", dir=SCRATCH_PARENT
        ) as directory:
            root = Path(directory)
            _copy_checker_inputs(root)
            (root / FENCE.SKELETON_RELATIVE_PATH).write_text(
                "[FILL:DX-010] +13.0 ms\n", encoding="utf-8"
            )
            completed = _run_scratch_checker(root)

        output = completed.stdout + completed.stderr
        self.assertEqual(completed.returncode, 2, output)
        self.assertIn("MISMATCH placement standing sentence", output)
        self.assertIn("observed '1 [FILL:DX- markers'", output)

    def _checklist_standing_sentence(self) -> str:
        checklist = CHECKLIST_PATH.read_text(encoding="utf-8")
        marker = "  The mandatory standing sentence is:\n\n"
        quoted = checklist.split(marker, 1)[1].split("\n\n", 1)[0]
        sentence = " ".join(
            line.removeprefix("  > ").strip() for line in quoted.splitlines()
        )
        self.assertTrue(sentence.startswith(FENCE.DX_STANDING_SENTENCE_HEAD))
        return sentence

    def _real_shaped_dx_region(self, *extra_lines: str) -> str:
        skeleton = SKELETON_PATH.read_text(encoding="utf-8")
        reconstruction = skeleton.split("### One diagnostic reconstruction", 1)[1]
        opening = reconstruction.split("\n\n", 2)[1]
        marker = {
            row_id: f"[FILL:{row_id}] {self.spec.rows[row_id].marker}"
            for row_id in FENCE._placement_row_ids(self.spec)
        }
        paragraphs = [
            self._checklist_standing_sentence(),
            opening,
            (
                f"Across the retained excursion reconstruction, the onset and "
                f"offset medians were {marker['DX-010']} and {marker['DX-011']}; "
                f"the signed directions held for {marker['DX-012']} onsets and "
                f"{marker['DX-013']} offsets. Their median absolute deviations "
                f"were {marker['DX-014']} and {marker['DX-015']}; these are "
                f"sample summaries, not claim evidence."
            ),
            (
                f"The ramp explained {marker['DX-016']} of the apparent shift, "
                f"while the worst onset exceeded the center by {marker['DX-017']}; "
                f"both remain diagnostic."
            ),
            (
                f"The anchor comparison covered {marker['DX-020']} captures: "
                f"{marker['DX-021']}, with {marker['DX-022']} admissibility "
                f"flips and a v2 control of {marker['DX-023']}; the control "
                f"failure stays named."
            ),
            (
                f"The bound changes had median {marker['DX-024']}, maximum "
                f"{marker['DX-025']}, maximum relative change {marker['DX-026']}, "
                f"and median relative change {marker['DX-027']}; none supplies "
                f"a claim."
            ),
            *extra_lines,
        ]
        return "\n\n".join(paragraphs) + "\n"

    def test_prose_fixture_uses_checklist_sentence_and_real_skeleton_prose(self) -> None:
        region = self._real_shaped_dx_region()
        self.assertTrue(region.startswith(self._checklist_standing_sentence()))
        self.assertIn(
            "The following table and arithmetic reconstruct one retained "
            "diagnostic capture",
            region,
        )
        self.assertEqual(region.count("[FILL:DX-"), 16)

    def test_unmarked_rendered_literal_inside_dx_prose_region_is_refused(self) -> None:
        skeleton = self._real_shaped_dx_region(
            "The retained calibration refused 49 of 59 pulses."
        )
        with tempfile.TemporaryDirectory(
            prefix="r7f-prose-unmarked-", dir=SCRATCH_PARENT
        ) as directory:
            root = Path(directory)
            _copy_checker_inputs(root)
            (root / FENCE.SKELETON_RELATIVE_PATH).write_text(
                skeleton, encoding="utf-8"
            )
            completed = _run_scratch_checker(root)

        output = completed.stdout + completed.stderr
        self.assertEqual(completed.returncode, 2, output)
        self.assertIn("MISMATCH prose DX-013", output)

    def test_unmarked_rendered_literal_outside_dx_prose_region_passes(self) -> None:
        skeleton = self._real_shaped_dx_region(
            "# Next section",
            "The retained calibration refused 49 of 59 pulses.",
        )
        with tempfile.TemporaryDirectory(
            prefix="r7f-prose-outside-", dir=SCRATCH_PARENT
        ) as directory:
            root = Path(directory)
            _copy_checker_inputs(root)
            (root / FENCE.SKELETON_RELATIVE_PATH).write_text(
                skeleton, encoding="utf-8"
            )
            completed = _run_scratch_checker(root)

        output = completed.stdout + completed.stderr
        self.assertEqual(completed.returncode, 0, output)
        self.assertNotIn("MISMATCH prose DX-013", output)

    def test_rendered_literal_with_own_marker_inside_dx_prose_region_passes(self) -> None:
        skeleton = self._real_shaped_dx_region(
            "The retained calibration refused [FILL:DX-013] 49 of 59 pulses."
        )
        with tempfile.TemporaryDirectory(
            prefix="r7f-prose-marked-", dir=SCRATCH_PARENT
        ) as directory:
            root = Path(directory)
            _copy_checker_inputs(root)
            (root / FENCE.SKELETON_RELATIVE_PATH).write_text(
                skeleton, encoding="utf-8"
            )
            completed = _run_scratch_checker(root)

        output = completed.stdout + completed.stderr
        self.assertEqual(completed.returncode, 0, output)
        self.assertNotIn("MISMATCH prose DX-013", output)


class InvocationTests(unittest.TestCase):
    def test_literals_only_cli_passes(self) -> None:
        with tempfile.TemporaryDirectory(
            prefix="r7f-current-pins-", dir=SCRATCH_PARENT
        ) as directory:
            registry = _registry_with_current_source_pins(Path(directory))
            completed = subprocess.run(
                [
                    sys.executable,
                    str(FENCE_PATH),
                    "--registry",
                    str(registry),
                    "--literals-only",
                ],
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=False,
            )
        self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)
        lines = completed.stdout.splitlines()
        self.assertEqual(lines[-2], "R7F PLACED 0/16")
        self.assertEqual(
            lines[-1],
            "R7F LITERALS-ONLY COMPARED 181 / MISMATCHES 0",
        )
        self.assertLess(lines.index("R7F PLACED 0/16"), len(lines) - 1)

    def test_absent_corpus_exits_three_and_names_path(self) -> None:
        with tempfile.TemporaryDirectory(
            prefix="r7f-unavailable-", dir=SCRATCH_PARENT
        ) as directory:
            # The fence prints the RESOLVED corpus root; resolve here too so a
            # symlinked TMPDIR (macOS /var -> /private/var) cannot fail the exact
            # last-line comparison.
            scratch = Path(directory).resolve()
            missing_root = scratch / "no-such-corpus"
            registry = _registry_with_current_source_pins(scratch)
            completed = subprocess.run(
                [
                    sys.executable,
                    str(FENCE_PATH),
                    "--registry",
                    str(registry),
                    "--corpus-root",
                    str(missing_root),
                ],
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=False,
            )
        self.assertEqual(completed.returncode, 3, completed.stdout + completed.stderr)
        self.assertIn(str(missing_root), completed.stdout)
        self.assertEqual(
            completed.stdout.splitlines()[-1],
            f"R7F CORPUS UNAVAILABLE: {missing_root / 'runs_window_a_20260722' / 'instrument_validation' / '20260722T145535-e941c821' / 'instrument_evidence.json'}",
        )
        self.assertFalse(
            any("COMPARED" in line for line in completed.stdout.splitlines())
        )


@unittest.skipUnless(
    CORPUS_PRESENT,
    "retained XD/AQ corpora are not present; run the default R7F CLI where both corpora live",
)
class ReplayAgainstRetainedCorporaTests(unittest.TestCase):
    def test_both_producers_are_byte_identical(self) -> None:
        spec, digest_comparisons = FENCE.digest_half(
            ROOT, REGISTRY_PATH, SKELETON_PATH
        )
        self.assertIsNotNone(spec)
        assert spec is not None
        self.assertEqual(len(digest_comparisons), 181)
        self.assertTrue(
            all(row.match for row in digest_comparisons), digest_comparisons
        )
        comparisons = FENCE.replay_half(ROOT, CORPUS_ROOT, spec)
        self.assertEqual([row.label for row in comparisons], [
            "replay XD bytes",
            "replay F4 bytes",
            "replay AQ bytes",
        ])
        self.assertTrue(all(row.match for row in comparisons), comparisons)
        self.assertEqual(len(digest_comparisons) + len(comparisons), 184)


if __name__ == "__main__":
    unittest.main()
