from __future__ import annotations

import copy
import io
import tempfile
import unittest
from pathlib import Path
from typing import Any, Mapping

from joulewise import arm_readiness as readiness
from joulewise import clock_reference
from joulewise import t0_rehearsal as rehearsal
from scripts import rehearse_t0_unattended as cli


BOOT_ID = "aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa"
HEAD = "a" * 40
TREE = "b" * 40
PACK_SHA = "c" * 64
OFFSET_NS = 2_000_000_000_000_000_000
R0_RAW_NS = 1_000_000_000_000
AUTHOR_RAW_NS = R0_RAW_NS + 600_000_000_000
R1_FINISHED_MONOTONIC_NS = 900_000_000_000


def _write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(readiness.render_json(value))


def _reference(path: Path, root: Path) -> dict[str, str]:
    raw = path.read_bytes()
    return {
        "path": path.relative_to(root).as_posix(),
        "sha256": readiness.sha256_bytes(raw),
    }


def _sntp_line(
    server: str,
    *,
    offset: str = "+0.010000",
    uncertainty: str = "0.020000",
) -> str:
    peers = {
        "time.apple.com": "17.253.4.45",
        "pool.ntp.org": "192.0.2.20",
        "time.nist.gov": "129.6.15.28",
    }
    return f"{offset} +/- {uncertainty} {server} {peers[server]}"


def _clock_reference_value() -> dict[str, object]:
    batch_started = R0_RAW_NS + 10
    cursor = batch_started + 10
    samples = []
    for server in clock_reference.SERVER_ROSTER:
        line = _sntp_line(server)
        parsed = clock_reference.parse_sntp_stdout(line, server=server)
        assert parsed is not None
        samples.append(
            {
                "server": server,
                "argv": clock_reference.build_sntp_argv(server),
                "exit_code": 0,
                "started_monotonic_raw_ns": cursor,
                "finished_monotonic_raw_ns": cursor + 1,
                "stdout": line,
                "stderr": "",
                "parsed": True,
                "offset_s": float(parsed.offset_s),
                "uncertainty_s": float(parsed.uncertainty_s),
                "peer_address": parsed.peer_address,
                "raw_line": parsed.raw_line,
            }
        )
        cursor += 2
    return {
        "schema_version": clock_reference.SCHEMA_VERSION,
        "sample_policy_id": clock_reference.SAMPLE_POLICY_ID,
        "boot_session_id": BOOT_ID,
        "anchor_realtime_ns": OFFSET_NS + R0_RAW_NS,
        "anchor_monotonic_raw_ns": R0_RAW_NS,
        "anchor_read_skew_ns": 1_000,
        "batch_started_monotonic_raw_ns": batch_started,
        "batch_finished_monotonic_raw_ns": cursor,
        "samples": samples,
    }


def _command_capture(
    step_id: str,
    argv: list[str],
    stdout: str,
    *,
    started: int,
    finished: int,
) -> dict[str, object]:
    return {
        "schema_version": "joulewise.arm_readiness_t0_command_capture.v1",
        "step_id": step_id,
        "argv": argv,
        "cwd": "/fixture/repository",
        "exit_code": 0,
        "stdout": stdout,
        "stderr": "",
        "started_monotonic_ns": started,
        "finished_monotonic_ns": finished,
        "boot_session_id": BOOT_ID,
    }


def _clock_value() -> dict[str, object]:
    return {
        "independent_clock_attestation": True,
        "reference_quorum_satisfied": True,
        "absolute_offset_within_ceiling": True,
        "unstepped_across_t0_sequence": True,
        "sample_policy_id": clock_reference.SAMPLE_POLICY_ID,
        "reference_server_count": 3,
        "reference_bound_seconds": 0.03,
        "comparison_delta_seconds": 0.01,
        "r0_anchor_realtime_ns": OFFSET_NS + R0_RAW_NS,
        "r0_anchor_monotonic_raw_ns": R0_RAW_NS,
        "r0_anchor_read_skew_ns": 1_000,
        "anchor_realtime_ns": OFFSET_NS + AUTHOR_RAW_NS,
        "anchor_monotonic_raw_ns": AUTHOR_RAW_NS,
        "anchor_read_skew_ns": 1_000,
        "anchor_delta_ns": 0,
        "t0_span_ns": 600_000_000_000,
        "r1_batch_started_monotonic_raw_ns": AUTHOR_RAW_NS - 1_000,
        "r1_batch_finished_monotonic_raw_ns": AUTHOR_RAW_NS,
        "r1_batch_duration_ns": 1_000,
        "r1_batch_finished_monotonic_ns": R1_FINISHED_MONOTONIC_NS,
    }


class FixtureBuilder:
    """Test-only builder for one complete or exactly-one-gate-broken tree."""

    def __init__(
        self,
        base: Path,
        *,
        broken_gate: str | None = None,
        hid_case: str = "pass",
        g10_case: str = "pass",
    ) -> None:
        self.base = base
        self.root = base / "fixture"
        self.root.mkdir()
        self.namespace = self.root / "t0-namespace"
        self.inputs = self.namespace / "arm_readiness.t0.inputs"
        self.sources = self.namespace / "arm_readiness.t0.sources"
        self.receipts = self.namespace / "arm_readiness.evidence"
        self.records = self.root / "records"
        self.broken_gate = broken_gate
        self.hid_case = hid_case
        self.g10_case = g10_case

    def build(self) -> Path:
        self._build_clock_namespace()
        self._build_execution()
        self._build_hid()
        self._build_d149()
        self._build_rehearsal_receipt()
        self._build_process_lineage()
        self._build_lifecycle()
        self._build_falsifiers()
        self._build_manifest()
        return self.root

    def _build_clock_namespace(self) -> None:
        r0 = _clock_reference_value()
        r0_capture = _command_capture(
            "clock-reference",
            ["/fixture/repository/.venv/bin/python", "/fixture/repository/scripts/collect_clock_reference.py"],
            readiness.render_json(r0).decode("utf-8"),
            started=10,
            finished=20,
        )
        r0_path = self.inputs / "clock-reference.json"
        _write_json(r0_path, r0_capture)
        off_capture = _command_capture(
            "clock-disable",
            ["/usr/bin/sudo", "-n", "/usr/sbin/systemsetup", "-setusingnetworktime", "off"],
            readiness.EXPECTED_NETWORK_TIME_OFF_STDOUT,
            started=30,
            finished=40,
        )
        off_path = self.inputs / "clock-disable.json"
        _write_json(off_path, off_capture)

        probes = []
        for index, server in enumerate(clock_reference.SERVER_ROSTER):
            offset = "+0.010000"
            if self.broken_gate == "G4" and index == 2:
                offset = "+1.000000"
            probes.append(
                {
                    "argv": clock_reference.build_sntp_argv(server),
                    "cwd": "/fixture/repository",
                    "exit_code": 0,
                    "stdout": _sntp_line(server, offset=offset),
                    "stderr": "",
                }
            )
        source_value = _clock_value()
        clock_source = {
            "schema_version": "joulewise.arm_readiness_t0_source.v1",
            "row_id": "clock.correct_and_prior_state",
            "kind": "CLOCK_ATTESTATION",
            "head_commit": HEAD,
            "head_tree_oid": TREE,
            "pack_sha256": PACK_SHA,
            "boot_session_id": BOOT_ID,
            "primary_artifacts": [],
            "input_artifacts": [
                {"path": str(r0_path.resolve()), "sha256": readiness.sha256_bytes(r0_path.read_bytes())},
                {"path": str(off_path.resolve()), "sha256": readiness.sha256_bytes(off_path.read_bytes())},
            ],
            "probes": probes,
            "facts": [{"fact_id": "clock.correct_and_prior_state.v1", "value": source_value}],
            "derivation": {"sample_policy_id": clock_reference.SAMPLE_POLICY_ID},
        }
        source_path = self.sources / "clock-correct-and-prior-state.json"
        _write_json(source_path, clock_source)
        source_sha = readiness.sha256_bytes(source_path.read_bytes())
        clock_receipt = {
            "schema_version": readiness.EVIDENCE_RECEIPT_SCHEMA,
            "evidence_id": "arm-t0-clock-correct-and-prior-state-v1",
            "kind": "CLOCK_ATTESTATION",
            "status": "PASS",
            "issued_at_utc": "2026-08-26T00:00:00Z",
            "boot_session_id": BOOT_ID,
            "valid_until_monotonic_ns": R1_FINISHED_MONOTONIC_NS + 21_600_000_000_000,
            "pack_sha256": PACK_SHA,
            "head_commit": HEAD,
            "facts": [
                {
                    "fact_id": "clock.correct_and_prior_state.v1",
                    "value_type": "OBJECT",
                    "value": copy.deepcopy(source_value),
                    "source_kind": "PROBE",
                    "source_path": "arm_readiness.t0.sources/clock-correct-and-prior-state.json",
                    "source_sha256": source_sha,
                }
            ],
            "checks": [{"check_id": "derive-clock", "status": "PASS"}],
            "reason_codes": [],
            "assurance": copy.deepcopy(readiness.ASSURANCE),
        }
        _write_json(
            self.receipts / "evidence-t0-clock-correct-and-prior-state.json",
            clock_receipt,
        )

        second_off_source = {
            "schema_version": "joulewise.arm_readiness_t0_source.v1",
            "row_id": "clock.network_time_off",
            "kind": "CLOCK_PROBE",
            "head_commit": HEAD,
            "head_tree_oid": TREE,
            "pack_sha256": PACK_SHA,
            "boot_session_id": BOOT_ID,
            "primary_artifacts": [],
            "input_artifacts": [],
            "probes": [
                {
                    "argv": ["/usr/bin/sudo", "-n", "/usr/sbin/systemsetup", "-setusingnetworktime", "off"],
                    "cwd": "/fixture/repository",
                    "exit_code": 0,
                    "stdout": readiness.EXPECTED_NETWORK_TIME_OFF_STDOUT,
                    "stderr": "",
                }
            ],
            "facts": [
                {
                    "fact_id": "clock.network_time_off.v1",
                    "value": {"fresh_probe": True, "network_time": "off"},
                }
            ],
            "derivation": {},
        }
        _write_json(self.sources / "clock-network-time-off.json", second_off_source)

        other_source_kind = (
            "OPERATOR_ATTESTATION" if self.broken_gate == "G2" else "PROBE"
        )
        other_receipt = {
            "schema_version": readiness.EVIDENCE_RECEIPT_SCHEMA,
            "evidence_id": "arm-t0-other-v1",
            "kind": "MACHINE_PREFLIGHT",
            "status": "PASS",
            "facts": [
                {
                    "fact_id": "t0.other.v1",
                    "value_type": "OBJECT",
                    "value": {"green": True},
                    "source_kind": other_source_kind,
                    "source_path": "arm_readiness.t0.sources/other.json",
                    "source_sha256": "d" * 64,
                }
            ],
            "reason_codes": [],
        }
        _write_json(self.receipts / "evidence-t0-other.json", other_receipt)

    def _build_execution(self) -> None:
        stdin = "pipe:[123]" if self.broken_gate == "G1" else "/dev/null"
        value = {
            "schema_version": rehearsal.EXECUTION_SCHEMA,
            "sequence_completed": True,
            "processes": [
                {
                    "role": "top_level",
                    "pid": 700,
                    "argv": ["python", "author_arm_evidence_t0.py"],
                    "stdin_fd0_target": stdin,
                    "state": "EXITED",
                    "exit_code": 0,
                    "prompt_count": 0,
                    "eof_refusal": False,
                    "timed_out": False,
                },
                {
                    "role": "governed_subprocess",
                    "pid": 701,
                    "argv": ["/usr/bin/sntp", "-t", "2", "time.apple.com"],
                    "stdin_fd0_target": "/dev/null",
                    "state": "EXITED",
                    "exit_code": 0,
                    "prompt_count": 0,
                    "eof_refusal": False,
                    "timed_out": False,
                },
            ],
        }
        _write_json(self.records / "execution.json", value)

    def _build_hid(self) -> None:
        path = self.records / "hid-idle.txt"
        path.parent.mkdir(parents=True, exist_ok=True)
        if self.hid_case == "absent":
            return
        values = {
            "pass": '    "HIDIdleTime" = 600000000000\n',
            "ambiguous": '"HIDIdleTime" = 600000000000\n"HIDIdleTime" = 600000000001\n',
            "unparsable": '"HIDIdleTime" = 0x8bb2c97000\n',
            "below": '"HIDIdleTime" = 599999999999\n',
        }
        path.write_text(values[self.hid_case], encoding="utf-8")

    def _build_d149(self) -> None:
        conditions = []
        for index in range(1, 6):
            evidence_path = self.records / "d149-evidence" / f"C{index}.json"
            _write_json(evidence_path, {"condition_id": f"C{index}", "mechanical": True})
            conditions.append(
                {
                    "condition_id": f"C{index}",
                    "status": (
                        "FAIL"
                        if self.broken_gate == "G5" and index == 3
                        else "PASS"
                    ),
                    "evidence": [_reference(evidence_path, self.root)],
                }
            )
        _write_json(
            self.records / "d149-go.json",
            {
                "schema_version": rehearsal.D149_SCHEMA,
                "verdict": "GO",
                "conditions": conditions,
            },
        )

    def _build_rehearsal_receipt(self) -> None:
        _write_json(
            self.records / "rehearsal-receipt.json",
            {
                "schema_version": rehearsal.REHEARSAL_RECEIPT_SCHEMA,
                "receipt_class": rehearsal.REHEARSAL_RECEIPT_CLASS,
                "claim_eligible": False,
                "window_id": rehearsal.REHEARSAL_WINDOW_PREFIX + "fixture-001",
                "custody_root": str(self.root.resolve()),
                "acceptance_target": "T0-UNATTENDED-01",
            },
        )

    def _build_process_lineage(self) -> None:
        capture_processes = [{"pid": 900, "argv": ["/usr/bin/powermetrics"]}]
        if self.broken_gate == "G8":
            capture_processes.append(
                {"pid": 777, "argv": ["/usr/local/bin/codex", "exec"]}
            )
        _write_json(
            self.records / "process-lineage.json",
            {
                "schema_version": rehearsal.PROCESS_LINEAGE_SCHEMA,
                "agent_pid": 777,
                "agent_exit_monotonic_ns": 1_000,
                "capture_started_monotonic_ns": 1_001,
                "capture_finished_monotonic_ns": 2_000,
                "pre_launch_census": {
                    "processes": [
                        {"pid": 777, "argv": ["/usr/local/bin/codex", "exec"]}
                    ]
                },
                "capture_censuses": [{"processes": capture_processes}],
            },
        )

    def _build_lifecycle(self) -> None:
        stages = []
        for stage_id in (
            "launch",
            "capability_consumption",
            "capture",
            "claim_backup",
            "bound_backup",
            "close_out",
            "restore",
        ):
            evidence_path = self.records / "lifecycle-evidence" / f"{stage_id}.json"
            _write_json(evidence_path, {"stage_id": stage_id, "complete": True})
            stages.append(
                {
                    "stage_id": stage_id,
                    "status": (
                        "INCOMPLETE"
                        if self.broken_gate == "G9" and stage_id == "capture"
                        else "COMPLETE"
                    ),
                    "evidence": _reference(evidence_path, self.root),
                }
            )
        _write_json(
            self.records / "lifecycle.json",
            {
                "schema_version": rehearsal.LIFECYCLE_SCHEMA,
                "stages": stages,
                "operator_actions_at_t0": 0,
                "human_interventions": [],
            },
        )

    @staticmethod
    def _cases(reason_code: str) -> list[dict[str, object]]:
        return [
            {
                "delta_ns": 4_999_999,
                "expected_status": "PASS",
                "expected_reason_code": None,
                "pass_namespace_published": True,
            },
            {
                "delta_ns": 5_000_001,
                "expected_status": "REFUSE",
                "expected_reason_code": reason_code,
                "pass_namespace_published": False,
            },
        ]

    def _build_falsifiers(self) -> None:
        author_cases = self._cases(
            "evidence_author_t0_clock_attestation_underivable"
        )
        arm_cases = self._cases("readiness_clock_preflight_refused")
        if self.g10_case == "author_broken":
            author_cases[1]["delta_ns"] = 5_000_000
        if self.g10_case == "arm_broken":
            arm_cases[1]["delta_ns"] = 5_000_000
        _write_json(
            self.records / "falsifier-controls.json",
            {
                "schema_version": rehearsal.FALSIFIER_SCHEMA,
                "author_inputs": {
                    "reference_server_count": 3,
                    "reference_midpoint_seconds": 0.01,
                    "reference_bound_seconds": 0.03,
                    "r0_anchor_realtime_ns": OFFSET_NS + R0_RAW_NS,
                    "r0_anchor_monotonic_raw_ns": R0_RAW_NS,
                    "r0_anchor_read_skew_ns": 1_000,
                    "r0_batch_finished_monotonic_raw_ns": R0_RAW_NS + 100,
                    "clock_reference_capture_finished_monotonic_ns": 100,
                    "clock_disable_started_monotonic_ns": 200,
                    "clock_disable_finished_monotonic_ns": 300,
                    "r1_batch_started_monotonic_ns": 400,
                    "r1_batch_started_monotonic_raw_ns": AUTHOR_RAW_NS - 1_000,
                    "author_anchor_realtime_ns": OFFSET_NS + AUTHOR_RAW_NS,
                    "author_anchor_monotonic_raw_ns": AUTHOR_RAW_NS,
                    "author_anchor_read_skew_ns": 1_000,
                    "r1_batch_finished_monotonic_ns": 500,
                },
                "author_cases": author_cases,
                "arm_cases": arm_cases,
            },
        )
        if self.broken_gate != "G10":
            _write_json(
                self.records / "positive-control.json",
                {
                    "schema_version": rehearsal.POSITIVE_CONTROL_SCHEMA,
                    "performed_by": "Ed",
                    "outside_t0_sequence": True,
                    "network_time_reenabled": True,
                    "forced_resync": True,
                    "anchor_before_ns": OFFSET_NS,
                    "anchor_after_ns": OFFSET_NS + 5_000_001,
                    "author_refusal_reason_code": "evidence_author_t0_clock_attestation_underivable",
                },
            )

    def _build_manifest(self) -> None:
        production = self.base / "production"
        production.mkdir()
        if self.broken_gate == "G6":
            production = self.base
        _write_json(
            self.root / cli.MANIFEST_NAME,
            {
                "schema_version": cli.MANIFEST_SCHEMA,
                "t0_namespace": self.namespace.relative_to(self.root).as_posix(),
                "records": {
                    "execution": "records/execution.json",
                    "hid_idle": "records/hid-idle.txt",
                    "d149_go": "records/d149-go.json",
                    "rehearsal_receipt": "records/rehearsal-receipt.json",
                    "process_lineage": "records/process-lineage.json",
                    "lifecycle": "records/lifecycle.json",
                    "falsifier_controls": "records/falsifier-controls.json",
                    "positive_control": "records/positive-control.json",
                },
                "production_roots": [
                    {"role": "production_custody_root", "path": str(production.resolve())}
                ],
            },
        )


class T0RehearsalTests(unittest.TestCase):
    maxDiff = None

    def _evaluate(
        self,
        *,
        broken_gate: str | None = None,
        hid_case: str = "pass",
        g10_case: str = "pass",
    ) -> tuple[tempfile.TemporaryDirectory[str], Path, Mapping[str, Any]]:
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        root = FixtureBuilder(
            Path(temporary.name),
            broken_gate=broken_gate,
            hid_case=hid_case,
            g10_case=g10_case,
        ).build()
        bundle = cli.load_evidence_bundle(root)
        return temporary, root, rehearsal.evaluate_rehearsal(bundle)

    def _assert_single_failure(
        self,
        gate_id: str,
        *,
        broken_gate: str | None = None,
        hid_case: str = "pass",
        g10_case: str = "pass",
        message: str,
    ) -> Mapping[str, Any]:
        _temporary, _root, verdict = self._evaluate(
            broken_gate=broken_gate,
            hid_case=hid_case,
            g10_case=g10_case,
        )
        self.assertEqual(verdict["overall_verdict"], "FAIL")
        failed = [gate for gate in verdict["gates"] if gate["status"] == "FAIL"]
        self.assertEqual([gate["gate_id"] for gate in failed], [gate_id])
        self.assertIn(message, failed[0]["message"])
        for gate in verdict["gates"]:
            if gate["gate_id"] not in {gate_id, "G7"}:
                self.assertEqual(gate["status"], "PASS", gate)
        return verdict

    def test_passing_bundle_is_incomplete_for_exact_g7_reason(self) -> None:
        _temporary, _root, verdict = self._evaluate()
        self.assertEqual(verdict["overall_verdict"], "INCOMPLETE")
        self.assertEqual(verdict["gate_counts"], {"PASS": 9, "FAIL": 0, "UNRULED": 1})
        g7 = verdict["gates"][6]
        self.assertEqual(g7["gate_id"], "G7")
        self.assertEqual(g7["status"], "UNRULED")
        self.assertEqual(g7["message"], rehearsal.G7_UNRULED_REASON)

    def test_g1_wrong_stdin_binding_fails_only_noninteractive_gate(self) -> None:
        self._assert_single_failure(
            "G1",
            broken_gate="G1",
            message="stdin was not bound to /dev/null",
        )

    def test_g1_missing_new_execution_record_is_unruled_not_pass(self) -> None:
        _temporary, root, _verdict = self._evaluate()
        (root / "records/execution.json").unlink()
        verdict = rehearsal.evaluate_rehearsal(cli.load_evidence_bundle(root))
        self.assertEqual(verdict["gates"][0]["status"], "UNRULED")
        self.assertIn("current command captures do not record", verdict["gates"][0]["message"])
        self.assertEqual(verdict["overall_verdict"], "INCOMPLETE")

    def test_g2_other_receipt_operator_attestation_fails_broad_census(self) -> None:
        verdict = self._assert_single_failure(
            "G2",
            broken_gate="G2",
            message="OPERATOR_ATTESTATION fact",
        )
        clock_gate = verdict["gates"][1]
        self.assertIn("evidence-t0-other.json", clock_gate["message"])

    def test_g3_absent_ambiguous_unparsable_and_one_ns_below_all_fail(self) -> None:
        for case, message in (
            ("absent", "HIDIdleTime output is absent"),
            ("ambiguous", "HIDIdleTime output is ambiguous"),
            ("unparsable", "HIDIdleTime output is unparsable"),
            ("below", "is below measured T-0 span"),
        ):
            with self.subTest(case=case):
                self._assert_single_failure("G3", hid_case=case, message=message)

    def test_g4_empty_r1_intersection_fails_only_clock_mechanics(self) -> None:
        self._assert_single_failure(
            "G4",
            broken_gate="G4",
            message="R1 reference agreement intervals have empty intersection",
        )

    def test_g5_non_green_c3_fails_only_d149(self) -> None:
        self._assert_single_failure(
            "G5",
            broken_gate="G5",
            message="D-149 C3 is not mechanically green",
        )

    def test_g6_real_path_containment_rejects_production_overlap(self) -> None:
        self._assert_single_failure(
            "G6",
            broken_gate="G6",
            message="rehearsal custody overlaps production root",
        )

    def test_g7_is_first_class_unruled_and_never_faked_as_failure_or_pass(self) -> None:
        _temporary, _root, verdict = self._evaluate()
        gate = verdict["gates"][6]
        self.assertEqual(gate["status"], "UNRULED")
        self.assertIn("RF-32", gate["message"])
        self.assertNotEqual(verdict["overall_verdict"], "PASS")

    def test_g8_capture_census_agent_fails_only_zero_agent_gate(self) -> None:
        self._assert_single_failure(
            "G8",
            broken_gate="G8",
            message="agent process existed during capture",
        )

    def test_g9_incomplete_capture_fails_only_full_lifecycle(self) -> None:
        self._assert_single_failure(
            "G9",
            broken_gate="G9",
            message="lifecycle stage capture is not complete",
        )

    def test_g9_any_human_intervention_fails_even_if_stages_complete(self) -> None:
        _temporary, root, _verdict = self._evaluate()
        path = root / "records/lifecycle.json"
        value = readiness.parse_json_bytes(path.read_bytes(), require_canonical=True)
        value["human_interventions"] = [{"action": "made run succeed"}]
        _write_json(path, value)
        verdict = rehearsal.evaluate_rehearsal(cli.load_evidence_bundle(root))
        failures = [gate for gate in verdict["gates"] if gate["status"] == "FAIL"]
        self.assertEqual([gate["gate_id"] for gate in failures], ["G9"])
        self.assertIn("human intervention occurred", failures[0]["message"])

    def test_g10_real_author_and_real_arm_paths_observe_both_boundaries(self) -> None:
        _temporary, _root, verdict = self._evaluate()
        gate = verdict["gates"][9]
        self.assertEqual(gate["status"], "PASS")
        author = next(
            item["author_boundary_observations"]
            for item in gate["mechanical_evidence"]
            if "author_boundary_observations" in item
        )
        arm = next(
            item["arm_boundary_observations"]
            for item in gate["mechanical_evidence"]
            if "arm_boundary_observations" in item
        )
        self.assertEqual(
            [(item["delta_ns"], item["status"], item["reason_code"]) for item in author],
            [
                (4_999_999, "PASS", None),
                (5_000_001, "REFUSE", "evidence_author_t0_clock_attestation_underivable"),
            ],
        )
        self.assertEqual(
            [(item["delta_ns"], item["status"], item["reason_code"]) for item in arm],
            [
                (4_999_999, "PASS", None),
                (5_000_001, "REFUSE", "readiness_clock_preflight_refused"),
            ],
        )

    def test_g10_author_and_arm_control_descriptions_each_fail_closed(self) -> None:
        for case, message in (
            ("author_broken", "author_cases must contain exactly"),
            ("arm_broken", "arm_cases must contain exactly"),
        ):
            with self.subTest(case=case):
                self._assert_single_failure("G10", g10_case=case, message=message)

    def test_g10_missing_physical_control_fails_and_names_ed_hands(self) -> None:
        self._assert_single_failure(
            "G10",
            broken_gate="G10",
            message="outstanding Ed-hands privileged anchor positive-control record is absent",
        )

    def test_verdict_composition_distinguishes_all_status_combinations(self) -> None:
        cases = (
            (("PASS",), "PASS"),
            (("PASS", "PASS"), "PASS"),
            (("UNRULED",), "INCOMPLETE"),
            (("PASS", "UNRULED"), "INCOMPLETE"),
            (("FAIL",), "FAIL"),
            (("PASS", "FAIL"), "FAIL"),
            (("FAIL", "UNRULED"), "FAIL"),
            (("PASS", "FAIL", "UNRULED"), "FAIL"),
        )
        for statuses, expected in cases:
            with self.subTest(statuses=statuses):
                self.assertEqual(
                    rehearsal.compose_overall_verdict(statuses).value,
                    expected,
                )
        with self.assertRaises(ValueError):
            rehearsal.compose_overall_verdict(())

    def test_fixture_cli_reads_bytes_and_exits_non_success_for_incomplete(self) -> None:
        _temporary, root, _verdict = self._evaluate()
        output = io.BytesIO()
        code = cli.main(["--fixture-root", str(root)], stdout=output)
        parsed = readiness.parse_json_bytes(output.getvalue(), require_canonical=True)
        self.assertEqual(code, 3)
        self.assertEqual(parsed["overall_verdict"], "INCOMPLETE")
        self.assertEqual(output.getvalue(), readiness.render_json(parsed))

    def test_real_custody_cli_mode_uses_the_same_evidence_only_loader(self) -> None:
        _temporary, root, _verdict = self._evaluate()
        output = io.BytesIO()
        code = cli.main(["--custody-root", str(root)], stdout=output)
        parsed = readiness.parse_json_bytes(output.getvalue(), require_canonical=True)
        self.assertEqual(code, 3)
        self.assertEqual(parsed["gate_counts"]["UNRULED"], 1)


if __name__ == "__main__":
    unittest.main()
