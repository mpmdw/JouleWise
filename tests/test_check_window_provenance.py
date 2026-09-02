from __future__ import annotations

import copy
import hashlib
import io
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest import mock

from joulewise.analysis_manifest_v3 import (
    FINALIZED_SCHEMA_VERSION,
    analysis_semantics_sha256_v1,
    calculate_manifest_id,
    render_manifest,
)
from joulewise.calibration_ledger import canonical_sha256 as ledger_canonical_sha256
from joulewise.idle_admission import ADAPTER_CONTINUITY_SCHEMA
from joulewise.whole_window import build_row_provenance, canonical_sha256
from scripts.check_window_provenance import (
    DEFAULT_EXPECTED_REFUSALS,
    main as check_main,
)
from scripts.gen_g2_phase_d import (
    BEGIN_MARKER as PHASE_D_BEGIN_MARKER,
    END_MARKER as PHASE_D_END_MARKER,
    G2A_BEGIN_MARKER,
    G2A_END_MARKER,
    render_g2a_generated_region,
    render_generated_region,
    validate_pinned_anchors,
)
from tests.test_analysis_finalizer import install_synthetic_finalization_fixture

# The finalizer authenticates custody containment lexically and rejects symlinked
# components below the root as spelled (analysis_manifest_v3.py:1479);
# NR14-LAYOUT mirrors it. macOS's default tempdir lives under /var ->
# /private/var, so anchor fixtures at the real path without rewriting tempfile's
# process-wide policy or risking mixed lexical spellings in helper-created paths.
_REAL_TMP = os.path.realpath(tempfile.gettempdir())
from tests.test_run_campaign import read_all_jsonl, run_campaign_module


def _write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")


def _tree_digest(root: Path) -> dict[str, str]:
    return {
        path.relative_to(root).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in sorted(root.rglob("*"))
        if path.is_file()
    }


def _normal_argv(fixture: dict) -> list[str]:
    return [
        "--runs-root",
        str(fixture["runs_root"]),
        "--pack-root",
        str(fixture["prospective_path"].parent),
        "--custody-root",
        str(fixture["root"]),
        "--bracket-binding",
        str(fixture["bracket_path"]),
        "--whole-window-verdict",
        str(fixture["verdict_path"]),
        "--calibration-ledger",
        str(fixture["ledger_path"]),
        "--head-pin",
        str(fixture["root"] / "calibration_ledger_head.json"),
        "--terminal-boundary-record",
        str(fixture["terminal_boundary_record"]),
    ]


def _finalizer_argv(fixture: dict, scratch: Path) -> list[str]:
    return [
        "--expect-finalize-refusal",
        "--scratch-dir",
        str(scratch),
        "--prospective-manifest",
        str(fixture["prospective_path"]),
        "--plan-tree",
        str(fixture["plan_tree_path"]),
        "--custody-root",
        str(fixture["root"]),
        "--runs-root",
        str(fixture["runs_root"]),
        "--whole-window-verdict",
        str(fixture["verdict_path"]),
        "--bracket-binding",
        str(fixture["bracket_path"]),
        "--calibration-ledger",
        str(fixture["ledger_path"]),
        "--aggregate-floor-artifact",
        str(fixture["floor_path"]),
        "--output-dir",
        str(fixture["root"]),
    ]


def _run(argv: list[str]) -> tuple[int, str]:
    stdout = io.StringIO()
    with redirect_stdout(stdout):
        code = check_main(argv)
    return code, stdout.getvalue()


def _install_s11_checker_fixture(root: Path) -> dict:
    fixture = install_synthetic_finalization_fixture(root)
    runs_root = fixture["runs_root"]
    manifest_path = runs_root / "campaign_manifests" / "synthetic.json"
    manifest = json.loads(manifest_path.read_text())
    prospective_sha = hashlib.sha256(fixture["prospective_path"].read_bytes()).hexdigest()
    manifest["analysis_manifest_sha256"] = prospective_sha
    manifest["config_dir"] = str(
        fixture["prospective_path"].parent / "01_decode_contrast_blocks_01_05"
    )
    first_stage = fixture["prospective"]["stage_manifests"][0]
    order = json.loads(
        (fixture["prospective_path"].parent / first_stage["manifest_path"]).read_text()
    )
    expected_ids = {
        row["run_id"] for row in order["executed_order"] if row["block_index"] == 1
    }
    manifest["members"] = [
        member for member in manifest["members"] if member["run_id"] in expected_ids
    ]
    for index, member in enumerate(manifest["members"]):
        member["role"] = (
            run_campaign_module.NEG8_REFERENCE_ROLE
            if index in {0, len(manifest["members"]) - 1}
            else None
        )
        member["sentinel_position"] = (
            "start"
            if index == 0
            else "end"
            if index == len(manifest["members"]) - 1
            else None
        )
        member["scientific_config_sha256"] = "8" * 64
        member["canonical_neg8_workload"] = member["role"] is not None
        if member["role"] is not None:
            gross = 8.0 if index == 0 else 8.001
            idle = 7.0 if index == 0 else 7.001
            summary_path = runs_root / member["run_id"] / "summary_metrics.json"
            summary = json.loads(summary_path.read_text())
            summary.update(
                gross_energy_j=gross,
                idle_subtracted_energy_j=idle,
                energy_anchor_shift_envelopes={
                    "/gross_energy_j": {
                        "point_j": gross,
                        "lower_j": gross - 0.001,
                        "upper_j": gross + 0.001,
                    }
                },
            )
            _write_json(summary_path, summary)
    manifest["session_id"] = "synthetic-science-session"
    manifest["first_physical_run_id"] = manifest["members"][0]["run_id"]
    cooldown_dir = manifest_path.parent / "cooldown"
    cooldown_dir.mkdir()
    for index, member in enumerate(manifest["members"]):
        run_id = member["run_id"]
        if index == 0:
            cooldown = {
                "result": "first_run_exempt",
                "session_id": manifest["session_id"],
                "following_run_id": run_id,
            }
        else:
            payload = b'{"release":true,"release_criteria_met_late":false}\n'
            raw_path = cooldown_dir / f"{run_id}.jsonl"
            raw_path.write_bytes(payload)
            cooldown = {
                "result": "recovered",
                "session_id": manifest["session_id"],
                "following_run_id": run_id,
                "raw_artifact": {
                    "path": f"cooldown/{run_id}.jsonl",
                    "sha256": hashlib.sha256(payload).hexdigest(),
                    "records": 1,
                },
            }
        member["preceding_campaign_cooldown"] = cooldown
    _write_json(manifest_path, manifest)

    policy_path = (
        Path(__file__).resolve().parents[1]
        / "configs"
        / "campaign_policies"
        / "quiet_mac_p2_production.json"
    )
    _produce_whole_window_verdict(fixture)

    in_runs_binding = runs_root / "bracket_binding.json"
    in_runs_binding.write_bytes(fixture["bracket_path"].read_bytes())
    fixture["bracket_path"] = in_runs_binding
    head_pin = fixture["root"] / "calibration_ledger_head.json"
    fixture["terminal_head_pin"] = json.loads(head_pin.read_text())
    boundary_record = fixture["root"] / "post-bracket-terminal-boundary.json"
    _write_json(
        boundary_record,
        {
            "status": "session_status",
            "session_id": "synthetic-session",
            "session_state": "finalized",
            "pin_relation": "physical_ahead",
            "refusal_code": "calibration_ledger_head_mismatch",
            "terminal_head_pin_candidate": fixture["terminal_head_pin"],
        },
    )
    fixture["terminal_boundary_record"] = boundary_record
    return fixture


def _produce_whole_window_verdict(fixture: dict, *, require_pass: bool = True) -> int:
    runs_root = fixture["runs_root"]
    policy_path = (
        Path(__file__).resolve().parents[1]
        / "configs"
        / "campaign_policies"
        / "quiet_mac_p2_production.json"
    )
    verdict_path = runs_root / "whole-window-verdict.json"
    verdict_path.unlink(missing_ok=True)
    (runs_root / "campaign_log.jsonl").write_text("")
    args = run_campaign_module.parse_args(
        [
            "--whole-window-verdict",
            "--runs-dir",
            str(runs_root),
            "--campaign-policy",
            str(policy_path),
            "--neg8-drift-bound",
            str(fixture["root"] / "neg8_drift_bound.json"),
            "--whole-window-verdict-output",
            str(verdict_path),
        ]
    )
    with (
        mock.patch.object(run_campaign_module, "validate_bundle", return_value=[]),
        mock.patch.object(
            run_campaign_module, "_final_idle_admission_attempt", return_value=1
        ),
        mock.patch.object(
            run_campaign_module, "_load_idle_rich_telemetry", return_value=[]
        ),
        mock.patch.object(
            run_campaign_module, "post_run_environment_refusals", return_value=()
        ),
        mock.patch.object(
            run_campaign_module,
            "evaluate_cpu_idle_admission",
            return_value={"decision": "admitted", "conditions": []},
        ),
        mock.patch.object(
            run_campaign_module, "_adapter_observations_for", return_value=[]
        ),
        mock.patch.object(
            run_campaign_module,
            "evaluate_adapter_wattage_continuity",
            return_value={
                "schema_version": ADAPTER_CONTINUITY_SCHEMA,
                "decision": "stable",
                "conditions": [],
            },
        ),
        mock.patch.object(
            run_campaign_module,
            "_neg8_reference_scientific_config_sha256",
            return_value="8" * 64,
        ),
        mock.patch.object(
            run_campaign_module,
            "calibration_bracket_for_bundles",
            return_value=(
                {
                    "schema_version": "joulewise.instrument_calibration_bracket.v1",
                    "status": "passed",
                    "b_fiducial_s": 0.025,
                },
                (),
            ),
        ),
        redirect_stdout(io.StringIO()),
    ):
        result = run_campaign_module.run_whole_window_verdict(args)
        if require_pass and result != 0:
            rows = read_all_jsonl(runs_root / "campaign_log.jsonl")
            raise AssertionError(
                "whole-window fixture regeneration refused: "
                f"{rows[-1] if rows else None}"
            )
    fixture["verdict_path"] = verdict_path
    return result


def _make_sliced_one_block_verdict(fixture: dict) -> None:
    verdict = json.loads(fixture["verdict_path"].read_text())
    keep = {
        bundle_id
        for bundle_id in verdict["bundle_ids"]
        if "-decode-contrast-b01-" in bundle_id
    }
    verdict["bundle_ids"] = sorted(keep)
    basis = verdict["evaluation_basis"]
    basis["member_occurrences"] = [
        row for row in basis["member_occurrences"] if row["bundle_id"] in keep
    ]
    basis["sha256"] = canonical_sha256(
        {key: value for key, value in basis.items() if key != "sha256"}
    )
    core = verdict["idle_admission_core"]
    if isinstance(core.get("members"), list):
        core["members"] = [
            row for row in core["members"] if row.get("bundle_id") in keep
        ]
    verdict["member_failures"] = [
        row for row in verdict.get("member_failures", []) if row.get("bundle_id") in keep
    ]
    verdict["row_provenance"] = build_row_provenance(
        policy_sha256=verdict["campaign_policy"]["sha256"],
        bundle_ids=verdict["bundle_ids"],
        source_manifests=verdict["source_campaign_manifests"],
    )
    raw = (json.dumps(verdict, sort_keys=True) + "\n").encode()
    fixture["verdict_path"].write_bytes(raw)
    (fixture["runs_root"] / "campaign_log.jsonl").write_bytes(raw)


def _mutate_real_membership(fixture: dict, *, operation: str) -> str:
    """Add/delete one member across every real checker membership surface."""

    runs_root = fixture["runs_root"]
    manifest_path = runs_root / "campaign_manifests" / "synthetic.json"
    manifest = json.loads(manifest_path.read_text())
    verdict = json.loads(fixture["verdict_path"].read_text())
    if operation == "delete":
        target = next(
            member["run_id"]
            for member in manifest["members"]
            if member.get("role") is None
        )
        manifest["members"] = [
            member for member in manifest["members"] if member["run_id"] != target
        ]
    elif operation == "add":
        stage = fixture["prospective"]["stage_manifests"][0]
        order = json.loads(
            (fixture["prospective_path"].parent / stage["manifest_path"]).read_text()
        )
        target = next(
            row["run_id"] for row in order["executed_order"] if row["block_index"] == 2
        )
        source = next(
            member for member in manifest["members"] if member.get("role") is None
        )
        member = copy.deepcopy(source)
        member.update(
            bundle_ids=[target],
            canonical_neg8_workload=False,
            config=f"{target}.json",
            role=None,
            run_id=target,
            sentinel_position=None,
        )
        payload = b'{"release":true,"release_criteria_met_late":false}\n'
        raw_path = runs_root / "campaign_manifests" / "cooldown" / f"{target}.jsonl"
        raw_path.write_bytes(payload)
        member["preceding_campaign_cooldown"] = {
            "following_run_id": target,
            "raw_artifact": {
                "path": f"cooldown/{target}.jsonl",
                "records": 1,
                "sha256": hashlib.sha256(payload).hexdigest(),
            },
            "result": "recovered",
            "session_id": manifest["session_id"],
        }
        manifest["members"].append(member)
    else:
        raise ValueError(f"unknown membership mutation {operation!r}")
    _write_json(manifest_path, manifest)

    if operation == "delete":
        verdict["bundle_ids"] = [
            bundle_id for bundle_id in verdict["bundle_ids"] if bundle_id != target
        ]
        verdict["evaluation_basis"]["member_occurrences"] = [
            row
            for row in verdict["evaluation_basis"]["member_occurrences"]
            if row["bundle_id"] != target
        ]
        verdict["idle_admission_core"]["members"] = [
            row
            for row in verdict["idle_admission_core"].get("members", [])
            if row["bundle_id"] != target
        ]
    else:
        verdict["bundle_ids"].append(target)
        bundle = runs_root / target
        verdict["evaluation_basis"]["member_occurrences"].append(
            {
                "bundle_id": target,
                "bundle_path": target,
                "config_sha256": hashlib.sha256(
                    (bundle / "config.json").read_bytes()
                ).hexdigest(),
                "metadata_sha256": hashlib.sha256(
                    (bundle / "metadata.json").read_bytes()
                ).hexdigest(),
                "summary_sha256": hashlib.sha256(
                    (bundle / "summary_metrics.json").read_bytes()
                ).hexdigest(),
            }
        )
        core_member = copy.deepcopy(verdict["idle_admission_core"]["members"][0])
        core_member["bundle_id"] = target
        verdict["idle_admission_core"]["members"].append(core_member)
    verdict["bundle_ids"] = sorted(verdict["bundle_ids"])
    basis = verdict["evaluation_basis"]
    basis["member_occurrences"] = sorted(
        basis["member_occurrences"], key=lambda row: row["bundle_id"]
    )
    basis["sha256"] = canonical_sha256(
        {key: value for key, value in basis.items() if key != "sha256"}
    )
    verdict["member_failures"] = [
        row
        for row in verdict.get("member_failures", [])
        if row.get("bundle_id") in verdict["bundle_ids"]
    ]
    verdict["row_provenance"] = build_row_provenance(
        policy_sha256=verdict["campaign_policy"]["sha256"],
        bundle_ids=verdict["bundle_ids"],
        source_manifests=verdict["source_campaign_manifests"],
    )
    raw = (json.dumps(verdict, sort_keys=True) + "\n").encode()
    fixture["verdict_path"].write_bytes(raw)
    (runs_root / "campaign_log.jsonl").write_bytes(raw)
    return target


def _mutate_d157_contract(fixture: dict) -> None:
    prospective = copy.deepcopy(fixture["prospective"])
    prospective["families"][0]["multiplicity"]["m"] = 1
    prospective["frozen_semantics_sha256"] = analysis_semantics_sha256_v1(prospective)
    prospective["manifest_id"] = calculate_manifest_id(prospective)
    raw = render_manifest(prospective)
    fixture["prospective_path"].write_bytes(raw)
    plan_tree = json.loads(fixture["plan_tree_path"].read_text())
    plan_tree["downstream_contract"]["analysis_manifest_sha256"] = hashlib.sha256(
        raw
    ).hexdigest()
    _write_json(fixture["plan_tree_path"], plan_tree)


class CheckWindowProvenanceTests(unittest.TestCase):
    @staticmethod
    def _fail_ids(output: str) -> list[str]:
        return [
            line.split()[1]
            for line in output.splitlines()
            if line.startswith("FAIL ")
        ]

    def test_clean_all_assertions_pass(self) -> None:
        with tempfile.TemporaryDirectory(dir=_REAL_TMP) as tmp:
            fixture = _install_s11_checker_fixture(Path(tmp))
            code, output = _run(_normal_argv(fixture))
            self.assertEqual(code, 0, output)
            for assertion_id in (
                "NR14-LAYOUT",
                "S11-A1",
                "S11-A2",
                "S11-A3",
                "S11-A5",
                "F5-1",
                "F5-2",
                "F5-3",
                "F5-4",
            ):
                self.assertIn(f"PASS {assertion_id} ", output)
            self.assertIn(
                "SKIP S11-A4 present_stages=0 assertion_not_exercised", output
            )
            self.assertNotIn("PASS S11-A4 ", output)
            self.assertNotIn("FAIL ", output)

    def test_import_does_not_load_run_campaign(self) -> None:
        completed = subprocess.run(
            [
                sys.executable,
                "-c",
                (
                    "import sys; import scripts.check_window_provenance; "
                    "raise SystemExit('scripts.run_campaign' in sys.modules)"
                ),
            ],
            cwd=Path(__file__).resolve().parents[1],
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(completed.returncode, 0, completed.stderr)

    def test_runsheet_stages_complete_custody_and_confirmation_pair(self) -> None:
        runsheet = (
            Path(__file__).resolve().parents[1]
            / "docs/process_traces/2026-08-28-live-smoke/SHAKEDOWN-G2-RUNSHEET.md"
        ).read_text()
        self.assertIn('/bin/cp -Rp "$PACK_ROOT/." "$CUSTODY_ROOT/prospective/"', runsheet)
        self.assertIn('/usr/bin/diff -r "$PACK_ROOT" "$CUSTODY_ROOT/prospective"', runsheet)
        self.assertIn(
            '"$CUSTODY_ROOT/calibration/calibration_ledger_head.json"', runsheet
        )
        self.assertIn("analysis_finalization_prospective_invalid", runsheet)
        self.assertEqual(
            runsheet.count(
                '--expected-confirmation-digest "$EXPECTED_CONFIRMATION_DIGEST"'
            ),
            7,
        )
        self.assertEqual(
            runsheet.count('--step6-confirmation-table "$STEP6_CONFIRMATION_TABLE"'),
            2,
        )
        for artifact in (
            "d117_family_publication_v4.json",
            "d117_family_publication_v4.json.sha256",
            "d117_step6_confirmation_table_v4.json",
            "d117_step6_confirmation_table_v4.json.sha256",
        ):
            self.assertIn(artifact, runsheet)

    def test_runsheet_phase_d_chain_is_mechanically_bound_to_runbook(self) -> None:
        repo = Path(__file__).resolve().parents[1]
        runbook = (repo / "docs/phase_2/window_runbook.md").read_text()
        runsheet = (
            repo
            / "docs/process_traces/2026-08-28-live-smoke/SHAKEDOWN-G2-RUNSHEET.md"
        ).read_text()
        validate_pinned_anchors(runbook)
        expected = render_generated_region(runbook)
        start = runsheet.index(PHASE_D_BEGIN_MARKER)
        end = runsheet.index(PHASE_D_END_MARKER, start) + len(PHASE_D_END_MARKER) + 1
        self.assertEqual(runsheet[start:end].encode(), expected.encode())

    def test_runsheet_g2a_bracket_is_mechanically_bound_to_runbook(self) -> None:
        repo = Path(__file__).resolve().parents[1]
        runbook = (repo / "docs/phase_2/window_runbook.md").read_text()
        runsheet = (
            repo
            / "docs/process_traces/2026-08-28-live-smoke/SHAKEDOWN-G2-RUNSHEET.md"
        ).read_text()
        expected = render_g2a_generated_region(runbook)
        start = runsheet.index(G2A_BEGIN_MARKER)
        end = runsheet.index(G2A_END_MARKER, start) + len(G2A_END_MARKER) + 1
        self.assertEqual(runsheet[start:end].encode(), expected.encode())
        g2a = runsheet[start:end]
        for token in (
            'generate_g2a_probe_inputs.py" check',
            'PYTHONPATH="$REPO"',
            'readiness \\\n  --phase pre-reserve',
            'reserve_calibration_window_bracket.py" \\',
            'G2A_PRE_CAL_CUSTODY="$(calibrate_slot pre',
            'screen_pre_calibration "$G2A_PRE_CAL_CUSTODY"',
            'G2A_POST_CAL_CUSTODY="$(calibrate_slot post',
            "g2a-post-bracket-terminal-boundary.json",
            '.terminal_head_pin_candidate != null',
        ):
            self.assertIn(token, g2a)
        self.assertLess(
            g2a.index('generate_g2a_probe_inputs.py" check'),
            g2a.index('recover_calibration_ledger.py" readiness'),
        )
        self.assertLess(
            g2a.index('generate_g2a_probe_inputs.py" check'),
            g2a.index('reserve_calibration_window_bracket.py"'),
        )

    def test_phase_d_generation_rejects_runbook_settle_mutation(self) -> None:
        repo = Path(__file__).resolve().parents[1]
        runbook = (repo / "docs/phase_2/window_runbook.md").read_text()
        mutated = runbook.replace(
            '  /bin/sleep "$SETTLE_S"', "  /bin/sleep 999", 1
        )
        with self.assertRaisesRegex(ValueError, "pinned anchor 1556 drifted"):
            render_generated_region(mutated)

    def test_phase_d_byte_comparison_rejects_runsheet_settle_mutation(self) -> None:
        repo = Path(__file__).resolve().parents[1]
        runbook = (repo / "docs/phase_2/window_runbook.md").read_text()
        runsheet = (
            repo
            / "docs/process_traces/2026-08-28-live-smoke/SHAKEDOWN-G2-RUNSHEET.md"
        ).read_text()
        start = runsheet.index(PHASE_D_BEGIN_MARKER)
        end = runsheet.index(PHASE_D_END_MARKER, start) + len(PHASE_D_END_MARKER) + 1
        actual = runsheet[start:end]
        mutated = actual.replace('  /bin/sleep "$SETTLE_S"', "  /bin/sleep 999", 1)
        self.assertNotEqual(mutated.encode(), render_generated_region(runbook).encode())

    def test_runsheet_pins_ruled_termination_and_governed_chain(self) -> None:
        runsheet = (
            Path(__file__).resolve().parents[1]
            / "docs/process_traces/2026-08-28-live-smoke/SHAKEDOWN-G2-RUNSHEET.md"
        ).read_text()
        ordered_tokens = (
            '--lifecycle-event start',
            '# Final settle is chain-owned',
            '--lifecycle-event settle',
            'screen_pre_calibration "$PRE_CAL_CUSTODY"',
            'run_stage "$BOUND_RUNS_ROOT"',
            '--derive-neg8-drift-bound "$BOUND_MANIFEST"',
            'run_stage "$RUNS_ROOT" "$CLAIM_LOG" "$REF_ROOT/start_triplet"',
            "# G2-b delta: stop the authentic first stage after block 1",
            'test "$SCIENCE_RC" = 130',
            'run_stage "$RUNS_ROOT" "$CLAIM_LOG" "$REF_ROOT/midpoint"',
            'run_stage "$RUNS_ROOT" "$CLAIM_LOG" "$REF_ROOT/end_triplet"',
            'POST_CAL_CUSTODY="$(calibrate_slot post "$POST_ATTEMPT_ID")"',
            'post-bracket-terminal-boundary.json',
        )
        start = runsheet.index(PHASE_D_BEGIN_MARKER)
        positions = [runsheet.index(token, start) for token in ordered_tokens]
        self.assertEqual(positions, sorted(positions))
        self.assertNotIn('SLOT="$SLOT"', runsheet)
        self.assertNotIn('ATTEMPT_ID="$ATTEMPT_ID"', runsheet)
        self.assertIn("TERMINATE HERE", runsheet)
        self.assertIn('/bin/kill -INT "$SCIENCE_PID"', runsheet)
        self.assertIn("four block-1 bundle", runsheet)
        self.assertIn("diagnostic and non-claim by construction", runsheet)
        self.assertIn("exact refusal-set equality", runsheet)
        self.assertNotIn('--lifecycle-event completion\n', runsheet[start:runsheet.index(PHASE_D_END_MARKER)])
        self.assertIn("tracked pin unchanged", runsheet)

    def test_runsheet_shakedown_gate_note_matches_cli_cardinality(self) -> None:
        runsheet = (
            Path(__file__).resolve().parents[1]
            / "docs/process_traces/2026-08-28-live-smoke/SHAKEDOWN-G2-RUNSHEET.md"
        ).read_text()
        self.assertIn("requires `--backup`", runsheet)
        self.assertIn("exactly one single-repetition config", runsheet)
        self.assertIn("constrains an invocation to one bundle", runsheet)
        self.assertIn("cannot select that bundle", runsheet)
        self.assertIn("from a larger frozen stage", runsheet)
        self.assertIn("`scripts/run_campaign.py:8108-8117`", runsheet)
        self.assertNotIn("It bounds bundle quality, never bundle count.", runsheet)

    def test_preflight_comment_names_custody_artifact_replay(self) -> None:
        preflight = (
            Path(__file__).resolve().parents[1]
            / "docs/process_traces/2026-08-28-live-smoke/preflight.sh"
        ).read_text()
        self.assertIn("custody-artifact replay", preflight)
        self.assertIn("observation artifacts re-hashed at their custody", preflight)
        self.assertIn("_custody_reasons", preflight)
        self.assertNotIn("custody-store replay", preflight)

    def test_preflight_requires_documented_measurement_checkout_argument(self) -> None:
        preflight = (
            Path(__file__).resolve().parents[1]
            / "docs/process_traces/2026-08-28-live-smoke/preflight.sh"
        ).read_text()
        self.assertIn('if [ "$#" -ne 1 ]', preflight)
        self.assertIn("/Users/edr/JouleWise-measurement-20260813", preflight)
        self.assertIn('SMOKE_CHECKOUT="$1"', preflight)
        self.assertNotIn("/Users/edr/JouleWise-smoke/checkout", preflight)

    def test_runsheet_records_d166_prefill_resolvability_measurement(self) -> None:
        runsheet = (
            Path(__file__).resolve().parents[1]
            / "docs/process_traces/2026-08-28-live-smoke/SHAKEDOWN-G2-RUNSHEET.md"
        ).read_text()
        self.assertIn("## G2-a — first machine evening", runsheet)
        self.assertIn("## Desk day — reviewed pin, pack generation, estate 12", runsheet)
        self.assertIn("## G2-b — evening before the transaction", runsheet)
        self.assertIn("for length in 512 1024 2048 4096", runsheet)
        self.assertIn("Qwen3", runsheet)
        self.assertIn("in_window_sample_count", runsheet)
        # The per-row margin-above-three column left the runsheet with the
        # inline jq; the ratified reading (count >= 5) is now the summarizer's
        # constant, bound here so the runsheet and its producer cannot drift.
        summarizer = (
            Path(__file__).resolve().parents[1]
            / "scripts/summarize_g2a_prefill_probe.py"
        ).read_text()
        self.assertIn("MIN_OVERLAPPING_POWER_INTERVAL_COUNT = 5", summarizer)
        self.assertNotIn("overlap_margin_above_three", runsheet)
        # Ratified selection (cold gate 2026-08-30): small-model count >= 5
        # gates; the discarded margin-≥-5 reading (count >= 8) must be gone.
        self.assertIn("all_small_count_ge_5", runsheet)
        self.assertIn("all(.small_members >= 5)", runsheet)
        self.assertNotIn("all_margin_ge_5", runsheet)
        self.assertIn("select_g2a_prefill_length.py", runsheet)
        self.assertIn(
            'PYTHONPATH="$REPO" "$PY" "$REPO/scripts/select_g2a_prefill_length.py"',
            runsheet,
        )
        self.assertIn(
            'PYTHONPATH="$REPO" "$PY" "$REPO/scripts/summarize_g2a_prefill_probe.py"',
            runsheet,
        )
        self.assertIn(
            "The panel thinking-off policy and the MLX greedy runtime are hash-bound",
            runsheet,
        )
        self.assertNotIn(
            "thinking disabled, greedy\ndecode, and the indicated prompt length",
            runsheet,
        )
        self.assertIn("G2A_SELECTION_RECORD_SHA256", runsheet)
        self.assertIn('> "$G2A_SELECTION_RECORD.sha256"', runsheet)
        self.assertIn('and .collection_prefill_tokens == 4096', runsheet)
        g2a = runsheet.split("## G2-a", 1)[1].split("## Desk day", 1)[0]
        self.assertNotIn('test -f "$PACK_ROOT', g2a)
        self.assertIn('G2A_PRE_CAL_CUSTODY="$(calibrate_slot pre', g2a)
        self.assertIn('G2A_POST_CAL_CUSTODY="$(calibrate_slot post', g2a)
        g2b = runsheet.split("## G2-b — evening before the transaction", 1)[1]
        self.assertIn('test -f "$PACK_ROOT/analysis_manifest_v3.json"', g2b)

    def test_null_id_and_missing_sha_science_record_isolated_to_s11_a1(self) -> None:
        with tempfile.TemporaryDirectory(dir=_REAL_TMP) as tmp:
            fixture = _install_s11_checker_fixture(Path(tmp))
            source_path = fixture["runs_root"] / "campaign_manifests" / "synthetic.json"
            shadow_path = fixture["runs_root"] / "campaign_manifests" / "shadow.json"
            shadow = json.loads(source_path.read_text())
            shadow["members"] = [
                {**member, "execution": "blocked_before_invoke"}
                for member in shadow["members"]
            ]
            shadow["analysis_manifest_id"] = None
            shadow.pop("analysis_manifest_sha256")
            _write_json(shadow_path, shadow)
            code, output = _run(_normal_argv(fixture))
            self.assertNotEqual(code, 0, output)
            self.assertIn("FAIL S11-A1 ", output)
            self.assertEqual(self._fail_ids(output), ["S11-A1"], output)

    def test_foreign_finalized_collection_id_isolated_to_s11_a2(self) -> None:
        with tempfile.TemporaryDirectory(dir=_REAL_TMP) as tmp:
            fixture = _install_s11_checker_fixture(Path(tmp))
            finalized_path = fixture["root"] / "foreign-finalized.json"
            _write_json(
                finalized_path,
                {
                    "schema_version": FINALIZED_SCHEMA_VERSION,
                    "lineage": {"collection_manifest_id": "am-" + "f" * 64},
                },
            )
            code, output = _run(
                _normal_argv(fixture)
                + ["--finalized-manifest", str(finalized_path)]
            )
            self.assertNotEqual(code, 0, output)
            self.assertEqual(self._fail_ids(output), ["S11-A2"], output)

    def test_real_add_delete_membership_reaches_s11_a2_and_all_f5_assertions(self) -> None:
        for operation, direction in (("add", "extra"), ("delete", "missing")):
            with self.subTest(operation=operation), tempfile.TemporaryDirectory(
                dir=_REAL_TMP
            ) as tmp:
                fixture = _install_s11_checker_fixture(Path(tmp))
                target = _mutate_real_membership(fixture, operation=operation)
                code, output = _run(_normal_argv(fixture))
                self.assertNotEqual(code, 0, output)
                self.assertEqual(
                    self._fail_ids(output),
                    ["S11-A2", "F5-1", "F5-2", "F5-3", "F5-4"],
                    output,
                )
                for assertion_id in ("S11-A2", "F5-1", "F5-2", "F5-3", "F5-4"):
                    self.assertIn(f"FAIL {assertion_id} ", output)
                self.assertIn(f"{direction}=['{target}']", output)
                self.assertNotIn("SKIP F5-", output)

    def test_deleted_frozen_roster_bundle_isolated_to_s11_a2(self) -> None:
        with tempfile.TemporaryDirectory(dir=_REAL_TMP) as tmp:
            fixture = _install_s11_checker_fixture(Path(tmp))
            stage = fixture["prospective"]["stage_manifests"][0]
            order = json.loads(
                (fixture["prospective_path"].parent / stage["manifest_path"]).read_text()
            )
            deleted = next(
                row["run_id"]
                for row in order["executed_order"]
                if row["block_index"] == 1
            )
            shutil.rmtree(fixture["runs_root"] / deleted)
            code, output = _run(_normal_argv(fixture))
            self.assertNotEqual(code, 0, output)
            self.assertEqual(self._fail_ids(output), ["S11-A2"], output)
            self.assertIn(f"frozen roster bundles missing=['{deleted}']", output)

    def test_missing_cooldown_evidence_isolated_to_s11_a3(self) -> None:
        with tempfile.TemporaryDirectory(dir=_REAL_TMP) as tmp:
            fixture = _install_s11_checker_fixture(Path(tmp))
            import scripts.check_window_provenance as checker

            baseline = checker.campaign_cooldown_evidence(
                fixture["runs_root"], fixture["prospective"]["manifest_id"]
            )
            manifest_path = fixture["runs_root"] / "campaign_manifests" / "synthetic.json"
            manifest = json.loads(manifest_path.read_text())
            manifest["members"][1].pop("preceding_campaign_cooldown")
            _write_json(manifest_path, manifest)
            _produce_whole_window_verdict(fixture)
            missing = checker.campaign_cooldown_evidence(
                fixture["runs_root"], fixture["prospective"]["manifest_id"]
            )
            with mock.patch.object(
                checker,
                "campaign_cooldown_evidence",
                side_effect=[missing, baseline],
            ):
                code, output = _run(_normal_argv(fixture))
            self.assertNotEqual(code, 0, output)
            self.assertEqual(self._fail_ids(output), ["S11-A3"], output)

    def test_empty_null_stage_roster_skips_s11_a4_without_failure(self) -> None:
        with tempfile.TemporaryDirectory(dir=_REAL_TMP) as tmp:
            fixture = _install_s11_checker_fixture(Path(tmp))
            code, output = _run(
                _normal_argv(fixture) + ["--null-bound-stage", "absent-stage"]
            )
            self.assertEqual(code, 0, output)
            self.assertIn(
                "SKIP S11-A4 present_stages=0 assertion_not_exercised", output
            )
            self.assertNotIn("PASS S11-A4 ", output)

    def test_present_null_stage_with_non_null_id_fails_s11_a4(self) -> None:
        with tempfile.TemporaryDirectory(dir=_REAL_TMP) as tmp:
            fixture = _install_s11_checker_fixture(Path(tmp))
            source = fixture["runs_root"] / "campaign_manifests" / "synthetic.json"
            null_stage = json.loads(source.read_text())
            null_stage["config_dir"] = "/repo/configs/campaigns/metrology_v1"
            null_stage["members"] = [
                {**member, "execution": "blocked_before_invoke"}
                for member in null_stage["members"]
            ]
            _write_json(
                fixture["runs_root"] / "campaign_manifests" / "metrology.json",
                null_stage,
            )
            code, output = _run(_normal_argv(fixture))
            self.assertNotEqual(code, 0, output)
            self.assertEqual(self._fail_ids(output), ["S11-A4"], output)

    def test_manifest_id_key_altered_isolated_to_s11_a5(self) -> None:
        with tempfile.TemporaryDirectory(dir=_REAL_TMP) as tmp:
            fixture = _install_s11_checker_fixture(Path(tmp))
            prospective = json.loads(fixture["prospective_path"].read_text())
            prospective["manifest_id"] = "am-" + "f" * 64
            fixture["prospective_path"].write_bytes(render_manifest(prospective))
            fixture["prospective"] = prospective
            manifest_path = fixture["runs_root"] / "campaign_manifests" / "synthetic.json"
            manifest = json.loads(manifest_path.read_text())
            manifest["analysis_manifest_id"] = prospective["manifest_id"]
            manifest["analysis_manifest_sha256"] = hashlib.sha256(
                fixture["prospective_path"].read_bytes()
            ).hexdigest()
            _write_json(manifest_path, manifest)
            _produce_whole_window_verdict(fixture)
            code, output = _run(_normal_argv(fixture))
            self.assertNotEqual(code, 0, output)
            self.assertEqual(self._fail_ids(output), ["S11-A5"], output)

    def test_recorded_disposition_altered_isolated_to_f5_1(self) -> None:
        with tempfile.TemporaryDirectory(dir=_REAL_TMP) as tmp:
            fixture = _install_s11_checker_fixture(Path(tmp))
            import scripts.check_window_provenance as checker

            baseline = checker.campaign_cooldown_evidence(
                fixture["runs_root"], fixture["prospective"]["manifest_id"]
            )
            altered = copy.deepcopy(baseline)
            altered[next(iter(altered))]["result"] = "unknown"
            with mock.patch.object(
                checker,
                "campaign_cooldown_evidence",
                side_effect=[baseline, altered],
            ):
                code, output = _run(_normal_argv(fixture))
            self.assertNotEqual(code, 0, output)
            self.assertEqual(self._fail_ids(output), ["F5-1"], output)

    def test_verdict_status_flipped_isolated_to_f5_2(self) -> None:
        with tempfile.TemporaryDirectory(dir=_REAL_TMP) as tmp:
            fixture = _install_s11_checker_fixture(Path(tmp))
            verdict = json.loads(fixture["verdict_path"].read_text())
            verdict["status"] = "failed"
            raw = (json.dumps(verdict, sort_keys=True) + "\n").encode()
            fixture["verdict_path"].write_bytes(raw)
            (fixture["runs_root"] / "campaign_log.jsonl").write_bytes(raw)
            code, output = _run(_normal_argv(fixture))
            self.assertNotEqual(code, 0, output)
            self.assertEqual(self._fail_ids(output), ["F5-2"], output)

    def test_premature_pin_advance_fails_f5_2_and_f5_3(self) -> None:
        with tempfile.TemporaryDirectory(dir=_REAL_TMP) as tmp:
            fixture = _install_s11_checker_fixture(Path(tmp))
            record = json.loads(fixture["terminal_boundary_record"].read_text())
            record["pin_relation"] = "exact"
            record["refusal_code"] = None
            _write_json(fixture["terminal_boundary_record"], record)
            code, output = _run(_normal_argv(fixture))
            self.assertNotEqual(code, 0, output)
            self.assertEqual(self._fail_ids(output), ["F5-2", "F5-3"], output)
            self.assertIn("not the expected mismatch shape", output)

    def test_missing_terminal_candidate_fails_f5_2_and_f5_3(self) -> None:
        with tempfile.TemporaryDirectory(dir=_REAL_TMP) as tmp:
            fixture = _install_s11_checker_fixture(Path(tmp))
            record = json.loads(fixture["terminal_boundary_record"].read_text())
            record["terminal_head_pin_candidate"] = None
            _write_json(fixture["terminal_boundary_record"], record)
            code, output = _run(_normal_argv(fixture))
            self.assertNotEqual(code, 0, output)
            self.assertEqual(self._fail_ids(output), ["F5-2", "F5-3"], output)
            self.assertIn("candidate=None", output)

    def test_binding_runs_root_alias_isolated_to_f5_3(self) -> None:
        with tempfile.TemporaryDirectory(dir=_REAL_TMP) as tmp:
            fixture = _install_s11_checker_fixture(Path(tmp))
            alias = fixture["root"] / "runs-alias"
            os.symlink(fixture["runs_root"], alias)
            binding = json.loads(fixture["bracket_path"].read_text())
            binding["runs_root"] = str(alias)
            binding["binding_digest"] = ledger_canonical_sha256(
                {key: value for key, value in binding.items() if key != "binding_digest"}
            )
            _write_json(fixture["bracket_path"], binding)
            code, output = _run(_normal_argv(fixture))
            self.assertNotEqual(code, 0, output)
            self.assertIn("FAIL F5-3 ", output)
            self.assertEqual(self._fail_ids(output), ["F5-3"], output)

    def test_conflicted_supersession_isolated_to_f5_4(self) -> None:
        with tempfile.TemporaryDirectory(dir=_REAL_TMP) as tmp:
            fixture = _install_s11_checker_fixture(Path(tmp))
            verdict = json.loads(fixture["verdict_path"].read_text())
            conflict = {
                "record_type": "campaign_occurrence_supersession",
                "bundle_id": verdict["bundle_ids"][0],
            }
            verdict_raw = (json.dumps(verdict, sort_keys=True) + "\n").encode()
            fixture["verdict_path"].write_bytes(verdict_raw)
            (fixture["runs_root"] / "campaign_log.jsonl").write_bytes(
                (json.dumps(conflict, sort_keys=True) + "\n").encode() + verdict_raw
            )
            import scripts.check_window_provenance as checker

            # The malformed supersession deliberately poisons the loader's
            # cooldown join too; pin that prerequisite to its pre-mutation
            # result so this regression exercises only F5-4's visibility scan.
            manifest_id = fixture["prospective"]["manifest_id"]
            log_path = fixture["runs_root"] / "campaign_log.jsonl"
            log_path.write_bytes(verdict_raw)
            clean_join = checker.campaign_cooldown_evidence(
                fixture["runs_root"], manifest_id
            )
            log_path.write_bytes(
                (json.dumps(conflict, sort_keys=True) + "\n").encode() + verdict_raw
            )
            with (
                mock.patch.object(
                    checker,
                    "campaign_cooldown_evidence",
                    side_effect=[clean_join, clean_join],
                ),
                mock.patch.object(
                    checker, "whole_window_refusal_reasons", return_value=()
                ),
            ):
                code, output = _run(_normal_argv(fixture))
            self.assertNotEqual(code, 0, output)
            self.assertEqual(self._fail_ids(output), ["F5-4"], output)

    def test_sliced_verdict_one_block_default_refusal_and_mismatches(self) -> None:
        self.assertEqual(
            DEFAULT_EXPECTED_REFUSALS,
            frozenset({"analysis_finalization_member_cover_mismatch"}),
        )
        with tempfile.TemporaryDirectory(dir=_REAL_TMP) as tmp:
            root = Path(tmp)
            fixture = install_synthetic_finalization_fixture(
                root / "fixture", shared_family=True
            )
            _make_sliced_one_block_verdict(fixture)
            scratch = root / "scratch"
            code, output = _run(_finalizer_argv(fixture, scratch))
            self.assertEqual(code, 0, output)
            self.assertIn(
                "observed={analysis_finalization_member_cover_mismatch}", output
            )

            code, output = _run(
                _finalizer_argv(fixture, scratch)
                + ["--expected-refusals", "analysis_finalization_verdict_not_passed"]
            )
            self.assertNotEqual(code, 0, output)
            self.assertIn("FAIL FINALIZE-REFUSAL", output)
            self.assertIn("expected={analysis_finalization_verdict_not_passed}", output)

            _mutate_d157_contract(fixture)
            code, output = _run(_finalizer_argv(fixture, scratch))
            self.assertNotEqual(code, 0, output)
            self.assertIn("observed={analysis_finalization_prospective_invalid}", output)
            self.assertIn("expected={analysis_finalization_member_cover_mismatch}", output)

    def test_stripped_stage_custody_refuses_as_prospective_invalid(self) -> None:
        with tempfile.TemporaryDirectory(dir=_REAL_TMP) as tmp:
            root = Path(tmp)
            fixture = install_synthetic_finalization_fixture(
                root / "fixture", shared_family=True
            )
            _make_sliced_one_block_verdict(fixture)
            stripped = root / "stripped"
            shutil.copytree(fixture["root"], stripped)
            for stage in (
                "01_decode_contrast_blocks_01_05",
                "02_decode_contrast_blocks_06_10",
                "03_prefill_p256_contrast_blocks_01_05",
                "04_prefill_p256_contrast_blocks_06_10",
            ):
                shutil.rmtree(stripped / "pack" / stage)
            stripped_fixture = {
                **fixture,
                "root": stripped,
                "prospective_path": stripped / fixture["prospective_path"].relative_to(fixture["root"]),
                "plan_tree_path": stripped / fixture["plan_tree_path"].relative_to(fixture["root"]),
                "runs_root": stripped / fixture["runs_root"].relative_to(fixture["root"]),
                "verdict_path": stripped / fixture["verdict_path"].relative_to(fixture["root"]),
                "bracket_path": stripped / fixture["bracket_path"].relative_to(fixture["root"]),
                "ledger_path": stripped / fixture["ledger_path"].relative_to(fixture["root"]),
                "floor_path": stripped / fixture["floor_path"].relative_to(fixture["root"]),
            }
            code, output = _run(_finalizer_argv(stripped_fixture, root / "scratch"))
            self.assertNotEqual(code, 0, output)
            self.assertIn("observed={analysis_finalization_prospective_invalid}", output)
            self.assertIn("expected={analysis_finalization_member_cover_mismatch}", output)

    def test_real_verdict_producer_refuses_one_block_without_governed_references(self) -> None:
        with tempfile.TemporaryDirectory(dir=_REAL_TMP) as tmp:
            fixture = install_synthetic_finalization_fixture(Path(tmp))
            bundle_ids = [
                member["run_id"]
                for contrast in fixture["prospective"]["contrasts"]
                for member in contrast["members"]
            ]
            for bundle_id in bundle_ids:
                if "-decode-contrast-b01-" not in bundle_id:
                    shutil.rmtree(fixture["runs_root"] / bundle_id)
            result = _produce_whole_window_verdict(fixture, require_pass=False)
            self.assertNotEqual(result, 0)
            verdict = json.loads(fixture["verdict_path"].read_text())
            self.assertEqual(verdict["status"], "failed")
            conditions = set(verdict["idle_admission_core"]["conditions"])
            self.assertIn("neg8_bracket_missing", conditions)
            self.assertIn("neg8_bracket_reference_invalid", conditions)

    def test_clean_run_does_not_write_runs_or_custody(self) -> None:
        with tempfile.TemporaryDirectory(dir=_REAL_TMP) as tmp:
            fixture = _install_s11_checker_fixture(Path(tmp) / "fixture")
            before = _tree_digest(fixture["root"])
            parent_before = _tree_digest(fixture["root"].parent)
            code, output = _run(_normal_argv(fixture))
            after = _tree_digest(fixture["root"])
            parent_after = _tree_digest(fixture["root"].parent)
            self.assertEqual(code, 0, output)
            self.assertEqual(after, before)
            self.assertEqual(parent_after, parent_before)

    def test_verdict_outside_runs_root_isolated_to_nr14_layout(self) -> None:
        with tempfile.TemporaryDirectory(dir=_REAL_TMP) as tmp:
            fixture = _install_s11_checker_fixture(Path(tmp))
            outside = fixture["root"] / "whole-window-verdict-outside-runs.json"
            outside.write_bytes(fixture["verdict_path"].read_bytes())
            argv = _normal_argv(fixture)
            argv[argv.index("--whole-window-verdict") + 1] = str(outside)
            code, output = _run(argv)
            self.assertNotEqual(code, 0, output)
            self.assertEqual(self._fail_ids(output), ["NR14-LAYOUT"], output)

    def test_object_equal_pretty_verdict_passes_nr14_layout(self) -> None:
        with tempfile.TemporaryDirectory(dir=_REAL_TMP) as tmp:
            fixture = _install_s11_checker_fixture(Path(tmp))
            verdict = json.loads(fixture["verdict_path"].read_text())
            fixture["verdict_path"].write_text(
                json.dumps(verdict, indent=4, sort_keys=True) + "\n"
            )
            code, output = _run(_normal_argv(fixture))
            self.assertEqual(code, 0, output)
            self.assertIn("PASS NR14-LAYOUT ", output)

    def test_runs_root_spelled_through_symlinked_parent_passes_nr14_layout(self) -> None:
        with tempfile.TemporaryDirectory(dir=_REAL_TMP) as tmp:
            root = Path(tmp)
            real_parent = root / "real-parent"
            real_parent.mkdir()
            alias_parent = root / "alias-parent"
            os.symlink(real_parent, alias_parent)
            fixture = _install_s11_checker_fixture(alias_parent / "fixture")
            _code, output = _run(_normal_argv(fixture))
            self.assertIn("PASS NR14-LAYOUT ", output)
            self.assertNotIn("FAIL NR14-LAYOUT ", output)

    def test_relative_runs_root_anchors_under_custody_not_cwd(self) -> None:
        """A relative --runs-root is custody-relative (finalizer semantics),
        so the checker's result must not depend on the process CWD."""
        with tempfile.TemporaryDirectory(dir=_REAL_TMP) as tmp, tempfile.TemporaryDirectory(
            dir=_REAL_TMP
        ) as elsewhere:
            fixture = _install_s11_checker_fixture(Path(tmp))
            argv = _normal_argv(fixture)
            index = argv.index("--runs-root")
            argv[index + 1] = str(fixture["runs_root"].relative_to(fixture["root"]))
            previous = os.getcwd()
            os.chdir(elsewhere)
            try:
                code, output = _run(argv)
            finally:
                os.chdir(previous)
            self.assertEqual(code, 0, output)
            self.assertIn("PASS NR14-LAYOUT ", output)
            self.assertNotIn("FAIL ", output)

        with tempfile.TemporaryDirectory(dir=_REAL_TMP) as tmp:
            fixture = _install_s11_checker_fixture(Path(tmp))
            verdict = json.loads(fixture["verdict_path"].read_text())
            raw = fixture["verdict_path"].read_text()
            duplicate = '"record_type":' + json.dumps(verdict["record_type"]) + ","
            fixture["verdict_path"].write_text("{" + duplicate + raw[1:])
            code, output = _run(_normal_argv(fixture))
            self.assertNotEqual(code, 0, output)
            self.assertEqual(self._fail_ids(output), ["NR14-LAYOUT"], output)

    def test_symlink_inside_custody_tree_isolated_to_nr14_layout(self) -> None:
        with tempfile.TemporaryDirectory(dir=_REAL_TMP) as tmp:
            fixture = _install_s11_checker_fixture(Path(tmp))
            alias = fixture["root"] / "runs-alias"
            os.symlink(fixture["runs_root"], alias)
            argv = _normal_argv(fixture)
            argv[argv.index("--runs-root") + 1] = str(alias)
            code, output = _run(argv)
            self.assertNotEqual(code, 0, output)
            self.assertEqual(self._fail_ids(output), ["NR14-LAYOUT"], output)


if __name__ == "__main__":
    unittest.main()
