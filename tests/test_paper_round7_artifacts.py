"""Tests for the round-7 DX artifact fence.

The always-on tests read every digest, field path, rendering rule, and expected
value from the registry parser exported by the fence; this file intentionally
contains no pinned digest.  Figure 4 stores coordinates to 0.01 px, so the
fence's 0.0008 ms y tolerance is the upward-rounded half-unit inversion
``0.005 px * 50 ms / 326 px``; its x tolerance is derived the same way.

The replay test is corpus-gated, like the Section 2 fence test.  A skip is not a
pass: the CLI test separately proves that an absent corpus exits 3 and names
the missing path.
"""

from __future__ import annotations

import copy
from contextlib import redirect_stderr, redirect_stdout
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
CORPUS_ROOT = Path("/Users/edr/code/JouleWise")
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


def _update_scratch_aq_pin(root: Path) -> None:
    aq_path = root / FENCE.EXPECTED_SOURCE_PATHS["AQ"]
    registry_path = root / FENCE.REGISTRY_RELATIVE_PATH
    registry_text = registry_path.read_text(encoding="utf-8")
    old_pin = FENCE.parse_registry_text(registry_text).sources["AQ"]
    new_sha256 = hashlib.sha256(aq_path.read_bytes()).hexdigest()
    new_size = aq_path.stat().st_size
    registry_text = registry_text.replace(old_pin.sha256, new_sha256)
    old_source = (
        f"- AQ = {old_pin.path}, sha256 {new_sha256} "
        f"({old_pin.size:,} B)"
    )
    new_source = f"- AQ = {old_pin.path}, sha256 {new_sha256} ({new_size:,} B)"
    if old_source not in registry_text:
        raise AssertionError("scratch AQ source pin was not found")
    registry_path.write_text(
        registry_text.replace(old_source, new_source, 1), encoding="utf-8"
    )


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
        self.assertEqual(
            completed.stdout.splitlines()[-1],
            "R7F LITERALS-ONLY COMPARED 181 / MISMATCHES 0",
        )

    def test_absent_corpus_exits_three_and_names_path(self) -> None:
        with tempfile.TemporaryDirectory(
            prefix="r7f-unavailable-", dir=SCRATCH_PARENT
        ) as directory:
            scratch = Path(directory)
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
