"""Regression tests for the G2-a emitter and unattended G2-b block stop."""

from __future__ import annotations

import hashlib
import io
import json
import os
import subprocess
import importlib.util
import re
import shutil
import shlex
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest import mock


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = REPO_ROOT / "scripts" / "gen_g2_phase_d.py"
RUNSHEET_PATH = REPO_ROOT / "docs" / "process_traces" / "2026-08-28-live-smoke" / "SHAKEDOWN-G2-RUNSHEET.md"


def _load_generator():
    spec = importlib.util.spec_from_file_location("gen_g2_phase_d_test", SCRIPT_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _section(source: str, heading: str) -> str:
    start = source.index(heading)
    following = re.search(r"^## ", source[start + len(heading) :], re.MULTILINE)
    return source[start:] if following is None else source[start : start + len(heading) + following.start()]


def _independent_fence_inventory(source: str) -> list[tuple[int, int, str]]:
    """Fence parser intentionally independent of the production emitter."""

    result: list[tuple[int, int, str]] = []
    for heading in ("## Plan-derived measurement variables", "## G2-a — first machine evening"):
        section = _section(source, heading)
        offset = source.index(section)
        for match in re.finditer(r"^```(?:sh|zsh)\n(.*?)^```$", section, re.MULTILINE | re.DOTALL):
            start = source.count("\n", 0, offset + match.start()) + 1
            end = source.count("\n", 0, offset + match.end()) + 1
            result.append((start, end, match.group(1)))
    return result


class G2aNightChainTests(unittest.TestCase):
    def setUp(self) -> None:
        self.generator = _load_generator()
        self.runsheet = RUNSHEET_PATH.read_text(encoding="utf-8")

    def test_inventory_has_every_shell_block_in_the_two_target_sections(self) -> None:
        independent = _independent_fence_inventory(self.runsheet)
        self.assertEqual(
            [(start, end) for start, end, _body in independent],
            [(1550, 1614), (328, 351), (374, 385), (389, 564), (575, 587)],
        )
        self.assertEqual(self.generator.inventory_g2a_shell_blocks(self.runsheet), independent)

    def test_identity_date_equals_the_full_reviewed_reconstruction(self) -> None:
        blocks = _independent_fence_inventory(self.runsheet)
        chain = self.generator.render_g2a_night_chain(self.runsheet, "20260830")
        required_inputs = (
            "# The desk producer runs while agents are present; require its outputs here.\n"
            'test -f "$G2A_INPUT_INVENTORY"\n'
            'test -f "$G2A_FROZEN_PLAN"\n'
            'test -f "$G2A_PROMPT_LADDER"\n'
        )
        expected = "#!/bin/zsh\nset -euo pipefail\n"
        for start, end, body in (blocks[0], blocks[1]):
            expected += f"\n# runsheet L{start}-{end}\n{body}"
        expected += "\n# arm-time input assertions\n" + required_inputs
        for start, end, body in (blocks[3], blocks[4]):
            expected += f"\n# runsheet L{start}-{end}\n{body}"
        self.assertEqual(chain, expected)
        self.assertNotEqual(chain + "# mutant line\n", expected)

    def test_date_substitution_is_confined_to_g2a_exports(self) -> None:
        blocks = _independent_fence_inventory(self.runsheet)
        replacement = "20300102"
        chain = self.generator.render_g2a_night_chain(self.runsheet, replacement)
        self.assertIn(blocks[1][2].replace("20260830", replacement), chain)
        for start, end, body in (blocks[0], blocks[3], blocks[4]):
            self.assertIn(f"# runsheet L{start}-{end}\n{body}", chain)
        self.assertNotIn("20260830", chain)

    def test_counterfactual_literal_survives_in_emitted_chain(self) -> None:
        chain = self.generator.render_g2a_night_chain(self.runsheet, "20260908")
        for literal in ("JouleWise-measurement-20260813", "code/JouleWise/.venv"):
            self.assertNotIn(literal, chain)

    @unittest.skipUnless(shutil.which("zsh"), "zsh required for emitted chain")
    def test_counterfactual_missing_measurement_root_not_refused(self) -> None:
        chain = self.generator.render_g2a_night_chain(self.runsheet, "20260908")
        # Only the routing block: never execute probe, ledger, or measurement work.
        routing = chain.split("\n# runsheet ")[1].split("\n", 1)[1]
        environment = {key: value for key, value in os.environ.items()
                       if key not in ("MEASUREMENT_ROOT", "MEASUREMENT_HEAD")}
        result = subprocess.run(["/bin/zsh", "-c", routing], env=environment,
                                text=True, capture_output=True)
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("FAIL measurement_root is required", result.stderr)

    @unittest.skipUnless(shutil.which("zsh"), "zsh required for emitted chain")
    def test_routing_checks_head_and_derives_interpreter_before_any_work(self) -> None:
        chain = self.generator.render_g2a_night_chain(self.runsheet, "20260908")
        routing = chain.split("\n# runsheet ")[1].split("\n", 1)[1]
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / "measurement with spaces"
            python = root / ".venv/bin/python"
            python.parent.mkdir(parents=True)
            python.write_text("#!/bin/sh\necho UNEXPECTED_EXECUTION >&2\nexit 99\n")
            python.chmod(0o755)
            fake_bin = Path(temporary) / "bin"
            fake_bin.mkdir()
            git = fake_bin / "git"
            git.write_text('#!/bin/sh\n[ "$1" = -C ] && [ "$2" = "$EXPECTED_ROOT" ] || exit 99\n'
                           'printf "%s\\n" "$OBSERVED_HEAD"\n')
            git.chmod(0o755)
            environment = {**os.environ, "PATH": f"{fake_bin}:/usr/bin:/bin",
                           "MEASUREMENT_ROOT": str(root), "EXPECTED_ROOT": str(root),
                           "MEASUREMENT_HEAD": "a" * 40, "OBSERVED_HEAD": "a" * 40,
                           "PY": "/wrong/python", "REPO": "/wrong/repo"}
            def run():
                return subprocess.run(["/bin/zsh", "-c", routing +
                                       '\nprintf "%s\\n" "$REPO" "$PY" "$PYTHONPATH"\n'],
                                      env=environment, text=True, capture_output=True)
            result = run()
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertEqual(result.stdout, f"{root}\n{python}\n{root}\n")
            for field, value, refusal in (
                ("MEASUREMENT_HEAD", "b" * 40, "checkout HEAD does not equal measurement_head"),
                ("MEASUREMENT_HEAD", "", "measurement_head must be a full 40-character lowercase SHA-1"),
                ("MEASUREMENT_ROOT", "relative", "measurement_root must be an absolute path"),
            ):
                with self.subTest(field=field, value=value):
                    original = environment[field]
                    environment[field] = value
                    result = run()
                    self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
                    self.assertIn("FAIL " + refusal, result.stderr)
                    environment[field] = original
            python.unlink()
            result = run()
            self.assertEqual(result.returncode, 1)
            self.assertIn("FAIL measurement venv Python is missing or not executable", result.stderr)

    def test_source_fence_drift_is_refused(self) -> None:
        with self.assertRaisesRegex(ValueError, "shell-fence inventory drifted"):
            self.generator.render_g2a_night_chain("\n" + self.runsheet, "20260908")

    def test_emit_writes_gnu_sidecar(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "night-chain.zsh"
            self.generator.emit_g2a_night_chain(output, "20260830")
            contents = output.read_bytes()
            sidecar = output.with_name("night-chain.zsh.sha256").read_text(encoding="utf-8")
            self.assertEqual(
                sidecar,
                f"{hashlib.sha256(contents).hexdigest()}  night-chain.zsh\n",
            )
            self.assertTrue(output.stat().st_mode & 0o111)

    def test_screen_check_detects_stale_source_and_rendered_literals(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            runbook = root / "window_runbook.md"
            runsheet = root / "runsheet.md"
            current_runbook = self.generator.RUNBOOK_PATH.read_text()
            for source in ("runbook", "runsheet-source", "runsheet-generated", "both-stale"):
                with self.subTest(source=source):
                    runbook.write_text(current_runbook)
                    runsheet.write_text(self.runsheet)
                    target = runbook if source == "runbook" else runsheet
                    text = target.read_text()
                    if source == "both-stale":
                        for path in (runbook, runsheet):
                            path.write_text(re.sub(
                                r"(?m)^((?:export )?PRE_CAL_FIDUCIAL_MAX_S=).+$",
                                r"\g<1>0.0", path.read_text()))
                        text = target.read_text()
                    elif source == "runsheet-generated":
                        start = text.index(self.generator.G2A_BEGIN_MARKER)
                        text = text[:start] + re.sub(
                            r"(?m)^PRE_CAL_FIDUCIAL_MAX_S=.+$",
                            "PRE_CAL_FIDUCIAL_MAX_S=0.0", text[start:], count=1)
                    else:
                        text = re.sub(r"(?m)^((?:export )?PRE_CAL_FIDUCIAL_MAX_S=).+$",
                                      r"\g<1>0.0", text, count=1)
                    target.write_text(text)
                    with (mock.patch.object(self.generator, "REPO_ROOT", root),
                          mock.patch.object(self.generator, "RUNBOOK_PATH", runbook),
                          mock.patch.object(self.generator, "RUNSHEET_PATH", runsheet),
                          redirect_stdout(io.StringIO()) as output):
                        self.assertEqual(self.generator.main(["--check"]), 1)
                        self.assertIn("FAIL", output.getvalue())
                        self.assertEqual(self.generator.main([]), 0)
                        self.assertEqual(self.generator.main(["--check"]), 0)
                    self.assertEqual(runbook.read_text(), current_runbook)
                    self.assertEqual(runsheet.read_text(), self.runsheet)

    def test_emission_derives_screen_even_from_stale_source(self) -> None:
        from scripts.validate_powermetrics_fiducial import _derive_preflight_systematic_screen_s

        stale = re.sub(r"(?m)^((?:export )?PRE_CAL_FIDUCIAL_MAX_S=).+$",
                       r"\g<1>0.0", self.runsheet)
        chain = self.generator.render_g2a_night_chain(stale, "20261003")
        assignments = re.findall(r"(?m)^(?:export )?PRE_CAL_FIDUCIAL_MAX_S=(.+)$", chain)
        self.assertEqual(assignments, [str(_derive_preflight_systematic_screen_s())] * 2)
        self.assertNotIn("# acceptance artifact d079_calibration_acceptance_v2_n17_r3", chain)


class RunbookSymbolAnchorTests(unittest.TestCase):
    """Runbook anchors are byte-exact symbols, not line numbers (lane L7)."""

    def setUp(self) -> None:
        self.generator = _load_generator()
        self.runbook = self.generator.RUNBOOK_PATH.read_text(encoding="utf-8")

    def test_every_anchor_is_found_once_in_order(self) -> None:
        located = self.generator.locate_pinned_anchors(self.runbook)
        symbols = [symbol for symbol, _pin_line, _text in self.generator.PINNED_ANCHORS]
        self.assertEqual(list(located), symbols)
        self.assertEqual(sorted(located.values()), list(located.values()))
        lines = self.runbook.splitlines()
        for symbol, _pin_line, text in self.generator.PINNED_ANCHORS:
            self.assertEqual(lines[located[symbol] - 1], text)

    def test_line_shift_above_the_anchors_is_not_drift(self) -> None:
        # The #479 failure: an unrelated runbook note moved every later line.
        shifted = "<!-- unrelated note -->\n\n" + self.runbook
        self.generator.validate_pinned_anchors(shifted)
        self.assertEqual(self.generator.render_generated_region(shifted),
                         self.generator.render_generated_region(self.runbook))
        self.assertEqual(self.generator.render_g2a_generated_region(shifted),
                         self.generator.render_g2a_generated_region(self.runbook))
        located = self.generator.locate_pinned_anchors(shifted)
        self.assertEqual(located["settle_sleep"],
                         self.generator.locate_pinned_anchors(self.runbook)["settle_sleep"] + 2)

    def test_edited_anchor_is_refused_with_its_pin_label(self) -> None:
        mutated = self.runbook.replace('  /bin/sleep "$SETTLE_S"', "  /bin/sleep 999", 1)
        with self.assertRaisesRegex(ValueError, "pinned anchor 1516 drifted: symbol settle_sleep occurs 0"):
            self.generator.render_generated_region(mutated)

    def test_deleted_duplicated_and_reordered_anchors_are_refused(self) -> None:
        settle = '  settle || return $?\n'
        deleted = self.runbook.replace(settle, "", 1)
        duplicated = self.runbook.replace(settle, settle + settle, 1)
        first = "run_stage_list() {\n"
        second = 'screen_pre_calibration "$PRE_CAL_CUSTODY"\n'
        reordered = (self.runbook.replace(first, "\0", 1).replace(second, first, 1).replace("\0", second, 1))
        for label, text in (("deleted", deleted), ("duplicated", duplicated), ("reordered", reordered)):
            with self.subTest(label=label):
                self.assertNotEqual(text, self.runbook)
                with self.assertRaisesRegex(ValueError, "runbook pinned anchor [0-9]+ drifted"):
                    self.generator.validate_pinned_anchors(text)


class G2bOneBlockChainTests(unittest.TestCase):
    def setUp(self):
        self.generator = _load_generator()
        self.chain = self.generator.render_generated_region(self.generator.RUNBOOK_PATH.read_text())

    def test_v5_reference_routing_preserves_the_pinned_historical_chain(self):
        runsheet = RUNSHEET_PATH.read_text()
        start = runsheet.index(self.generator.BEGIN_MARKER)
        end = runsheet.index(self.generator.END_MARKER, start) + len(self.generator.END_MARKER) + 1
        self.assertEqual(self.chain, runsheet[start:end])
        prospective = self.generator.render_generated_region(
            self.generator.RUNBOOK_PATH.read_text(), v5_references=True)
        self.assertEqual(prospective.replace("/window_references_v5\"", "/window_references\"")
                                   .replace("/neg8_reference_corpus_v5\"", "/neg8_reference_corpus\""),
                         self.chain)

    def test_chain_asserts_registered_stop_rc_and_preserves_bracket_path(self):
        from scripts.run_campaign import MAX_BLOCKS_REACHED_RC, CAMPAIGN_STOP_RETURN_CODES

        self.assertEqual(CAMPAIGN_STOP_RETURN_CODES["max_blocks_reached"], MAX_BLOCKS_REACHED_RC)
        self.assertNotIn(MAX_BLOCKS_REACHED_RC, (0, 1, 2, 130))
        self.assertIn(f'test "$SCIENCE_RC" = {MAX_BLOCKS_REACHED_RC}\n', self.chain)
        self.assertEqual(self.chain.count("--max-blocks 1"), 1)
        self.assertNotIn("SIGINT", self.chain)
        self.assertNotIn("kill -INT", RUNSHEET_PATH.read_text())
        self.assertNotIn('run_stage_list "$WINDOW_PLAN_ROOT/after_midpoint_stages.txt"', self.chain)
        self.assertLess(self.chain.index('test "$SCIENCE_RC" = '), self.chain.index('  midpoint-reference'))
        self.assertIn('POST_CAL_CUSTODY="$(calibrate_slot post', self.chain)
        self.assertIn('post-bracket-terminal-boundary.json', self.chain)

    @unittest.skipUnless(shutil.which("zsh"), "zsh required for generated chain")
    def test_rendered_g2b_dispatches_unique_75_second_idle_run_ids(self):
        """Execute the rendered dispatch body with a read-only roster collector."""
        pack = REPO_ROOT / "configs/campaigns/d117_contrast_qwen3-1p7b_vs_qwen3-8b_v5"
        tree = json.loads((pack / "plan_tree.json").read_bytes())
        science = [row for row in tree["stage_graph"]
                   if row["stage_id"].startswith("gamma-science-")]
        chain = self.generator.render_generated_region(
            self.generator.RUNBOOK_PATH.read_text(), v5_references=True)
        # Execute the renderer's actual root assignments; environment overrides
        # would conceal a historical 30-second dispatch route.
        bindings = chain[chain.index('POLICY="$REPO/'):
                         chain.index('\nmkdir -p')]
        body = chain[chain.index("# The reference corpus"):
                     chain.index('POST_CAL_CUSTODY="$(calibrate_slot post')]
        with tempfile.TemporaryDirectory(prefix="g2b-roster-") as temporary:
            root = Path(temporary)
            (root / "before_midpoint_stages.txt").write_text("\n".join(
                row["launch"]["commands"][0]["argv_template"]["arguments"][0]["value"]
                for row in science[:2]) + "\n")
            collector = root / "collect.py"
            collector.write_text(
                "import json, pathlib, sys\n"
                "directory = pathlib.Path(sys.argv[1])\n"
                "limited = '--max-blocks' in sys.argv\n"
                "manifest = json.loads((directory / 'order_manifest.json').read_bytes())\n"
                "for row in manifest['executed_order']:\n"
                "    if limited and row['block_index'] > 1: continue\n"
                "    config = json.loads((directory / row['config']).read_bytes())\n"
                "    assert config['run_id'] == row['run_id']\n"
                "    assert config['sampling']['idle_seconds'] == 75.0\n"
                "    print(config['run_id'])\n"
                "sys.exit(3 if limited else 0)\n"
            )
            shell = ('set -euo pipefail\ntimestamp() { echo roster; }\n'
                     'run_stage() { ' + shlex.quote(sys.executable) + ' -B '
                     + shlex.quote(str(collector)) + ' "$3" "$@"; }\n' + bindings + '\n' + body)
            environment = {**os.environ, "REPO": str(REPO_ROOT), "PY": "/usr/bin/true",
                "BOUND_RUNS_ROOT": str(root / "bound"), "BOUND_LOG": str(root / "bound.log"),
                "NEG8_DRIFT_BOUND": str(root / "bound.json"),
                "RUNS_ROOT": str(root / "claim"), "CLAIM_LOG": str(root / "claim.log"),
                "PRE_CAL_CUSTODY": "roster-only", "WINDOW_PLAN_ROOT": str(root),
                "WINDOW_CUSTODY_ROOT": str(root)}
            (root / "operator_logs").mkdir()
            result = subprocess.run(["/bin/zsh", "-c", shell], env=environment,
                                    capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            run_ids = result.stdout.splitlines()
            self.assertEqual(len(run_ids), 23)
            self.assertEqual(len(set(run_ids)), 23)
            self.assertEqual(sum("contrast-b01-" in run_id for run_id in run_ids), 4)
            self.assertEqual(sum("midpoint" in run_id for run_id in run_ids), 1)
            midpoint_stage = next(row for row in tree["stage_graph"]
                                  if row["stage_id"] == "gamma-reference-decode-midpoint")
            external = next(row for row in tree["external_inputs"]
                            if row["input_id"] == midpoint_stage["input_ref"]["input_id"])
            self.assertEqual(run_ids[19], external["members"][0]["run_id"])

    @unittest.skipUnless(shutil.which("zsh"), "zsh required for generated chain")
    def test_first_stage_only_and_failure_propagation_with_errexit_disabled(self):
        helper = self.chain[self.chain.index("run_stage() {"):self.chain.index("run_stage_list() {")]
        science = self.chain[self.chain.index("# G2-b: one complete"):self.chain.index(
            'run_stage "$RUNS_ROOT" "$CLAIM_LOG" "$REF_ROOT/midpoint"')]
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "before_midpoint_stages.txt").write_text("# frozen stages\n\nfirst-stage\nsecond-stage\n")
            client = root / "fake-campaign"
            client.write_text('#!/bin/sh\nprintf "%s\\n" "$@" >> "$ARGV_LOG"\nexit "$CAMPAIGN_RC"\n')
            client.chmod(0o755)
            environment = {**os.environ, "PY": str(client), "REPO": str(root),
                "RUNS_ROOT": str(root / "runs"), "CLAIM_LOG": str(root / "campaign.jsonl"),
                "PRE_CAL_CUSTODY": "fixture-calibration", "POLICY": "fixture-policy",
                "POWER_POLICY": "fixture-power", "WINDOW_PLAN_ROOT": str(root),
                "OPERATOR_LOG_ROOT": str(root), "ARGV_LOG": str(root / "argv")}
            script = ('set -euo pipefail\nsettle() { :; }\nquarantine_stale_lock() { :; }\n'
                      'timestamp() { echo fixture; }\n' + helper + science +
                      'echo post-bracket-path >> "$OPERATOR_LOG_ROOT/post"\n')
            for rc in (3, 1, 2, 130, 0):
                with self.subTest(rc=rc):
                    result = subprocess.run(["/bin/zsh", "-c", script],
                        env={**environment, "CAMPAIGN_RC": str(rc)}, text=True, capture_output=True)
                    self.assertEqual(result.returncode, 0 if rc == 3 else 1, result.stderr)
                    argv = (root / "argv").read_text().splitlines()
                    self.assertIn(str(root / "first-stage"), argv)
                    self.assertNotIn(str(root / "second-stage"), argv)
                    self.assertEqual(argv[-2:], ["--max-blocks", "1"])
                    self.assertEqual((root / "post").exists(), rc == 3)
                    (root / "argv").unlink()
                    (root / "post").unlink(missing_ok=True)

    @unittest.skipUnless(shutil.which("zsh"), "zsh required for generated chain")
    def test_run_stage_propagates_both_log_write_failures_with_errexit_disabled(self):
        g2a = self.generator.render_g2a_night_chain(RUNSHEET_PATH.read_text(), "20260830")
        for variant, chain in (("g2a", g2a), ("g2b", self.chain)):
            start = chain.index("run_stage() {")
            helper = chain[start:chain.index("\n}\n", start) + 3]
            for failure in ("stage_start", "stage_end"):
                with self.subTest(variant=variant, failure=failure), tempfile.TemporaryDirectory() as temporary:
                    root = Path(temporary)
                    client = root / "fake-campaign"
                    client.write_text('#!/bin/sh\ntouch "$DISPATCHED"\nexit 0\n')
                    client.chmod(0o755)
                    script = ('set -uo pipefail\nset +e\n'
                        'settle() { :; }\nquarantine_stale_lock() { :; }\n'
                        'timestamp() { builtin echo fixture; }\n'
                        'echo() { [[ "$1" = *"$FAILURE"* ]] && return 7; builtin echo "$@"; }\n'
                        + helper + 'run_stage root log configs calibration label\nexit $?\n')
                    result = subprocess.run(["/bin/zsh", "-c", script], text=True, capture_output=True,
                        env={**os.environ, "PY": str(client), "REPO": str(root), "POLICY": "desk",
                            "POWER_POLICY": "desk", "OPERATOR_LOG_ROOT": str(root),
                            "G2A_OPERATOR_LOG_ROOT": str(root), "FAILURE": failure,
                            "DISPATCHED": str(root / "dispatched")})
                    self.assertEqual(result.returncode, 7, result.stderr)
                    self.assertEqual((root / "dispatched").exists(), failure == "stage_end")


if __name__ == "__main__":
    unittest.main()
