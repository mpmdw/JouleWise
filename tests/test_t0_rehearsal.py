from __future__ import annotations

import copy
import io
import tempfile
import time
from contextlib import contextmanager
import unittest
from pathlib import Path
from typing import Any, Mapping
from unittest import mock

from joulewise import arm_readiness as readiness
from joulewise import clock_reference
from joulewise import t0_rehearsal as rehearsal
from scripts import rehearse_t0_unattended as cli


REAL_G5_T0_AUTHENTICATOR = readiness._authenticate_go_t0_evidence

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


def fixture_inventory(root):
    return [{"deployment_id": "fixture", "measurement_root": str(root.parents[2] / "production"),
             "custody_root": None, "ledger_path": None, "notes": "synthetic"}]


def fixture_bundle(root):
    return cli.load_evidence_bundle(root, home=root.parents[1], inventory=fixture_inventory(root))


def install_t0_inventory(fixture):
    """Synthetic probe bytes; the production T0 inventory authenticator stays real."""
    from joulewise import arm_readiness_evidence_t0 as author
    from tests.test_arm_readiness_schemas import sample_evidence
    root = fixture.custody / fixture.pack.name
    recipe_path = root / fixture.arm["evidence"][0]["path"]
    recipe = readiness.parse_json_bytes(recipe_path.read_bytes())
    source_path = root / recipe["facts"][0]["source_path"]
    source = readiness.parse_json_bytes(source_path.read_bytes())
    now = time.monotonic_ns()
    paths = []
    for index, (step, name) in enumerate(author._CAPTURE_FILES.items()):
        path = root / author._INPUT_DIRECTORY / name
        value = _command_capture(step, ["/fixture/probe"], "",
                                 started=now - 100 + index * 2,
                                 finished=now - 99 + index * 2)
        value["boot_session_id"] = fixture.arm["boot_session_id"]
        _write_json(path, value)
        source["input_artifacts"].append(fixture._artifact(path))
        paths.append(path)
    _write_json(source_path, source)
    source_digest = fixture._artifact(source_path)["sha256"]
    fixture.arm["evidence"] = []
    for row in author._EXPECTED_ROWS:
        value = copy.deepcopy(recipe) if row == "t0.single_launch_capability" else sample_evidence()
        value.update(evidence_id=author._evidence_id(row), kind=author._ROW_KIND[row],
                     boot_session_id=fixture.arm["boot_session_id"],
                     pack_sha256=fixture.arm["pack"]["pack_sha256"],
                     head_commit=fixture.arm["reviewed_main"]["head_commit"],
                     valid_until_monotonic_ns=fixture.arm["valid_until_monotonic_ns"])
        for fact in value["facts"]:
            fact.update(source_kind="PROBE", source_path=str(source_path.relative_to(root)),
                        source_sha256=source_digest)
        path = root / author._EVIDENCE_DIRECTORY / author._receipt_name(row)
        _write_json(path, value)
        digest = fixture._artifact(path)["sha256"]
        path.with_name(path.name + ".sha256").write_bytes(readiness.gnu_sidecar(digest, path.name))
        fixture.arm["evidence"].append({"evidence_id": value["evidence_id"],
            "receipt_kind": value["kind"], "namespace": "WINDOW_CUSTODY",
            "path": str(path.relative_to(root)), "sha256": digest,
            "schema_version": value["schema_version"], "status": "PASS"})
        paths.append(path)
    fixture._rewrite_arm()
    return sorted((_reference(path, fixture.custody) for path in paths), key=lambda ref: ref["path"])


@contextmanager
def fixture_replay(root):
    """Only ARM semantics/pack metadata are synthetic; GO/T0/consumption replay is real."""
    arm_path, = root.glob("*/arm_readiness.receipts/arm-0001.json")
    arm = readiness.parse_json_bytes(arm_path.read_bytes())
    with mock.patch.object(readiness, "_pack_record", return_value=arm["pack"]), \
         mock.patch.object(readiness, "_derive_arm_semantics_for_verification",
                           return_value=(arm["rows"], arm["refusals"])), \
         mock.patch.object(readiness, "_authenticate_go_t0_evidence", REAL_G5_T0_AUTHENTICATOR):
        yield


def evaluate_fixture(root):
    with fixture_replay(root):
        return rehearsal.evaluate_rehearsal(fixture_bundle(root))


class FixtureBuilder:
    """Current pack GO and retained consumption, plus synthetic ten-gate evidence."""

    def __init__(
        self,
        base: Path,
        *,
        broken_gate: str | None = None,
        hid_case: str = "pass",
        g10_case: str = "pass",
    ) -> None:
        self.base = base.resolve()
        self.root = self.base / "home/night-custody/rehearsal-t0-unattended-fixture-001"
        self.root.mkdir(parents=True)
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
        self._build_pack_go()
        if self.broken_gate == "G5":
            self._build_d149()
        self._build_rehearsal_receipt()
        self._build_process_lineage()
        self._build_lifecycle()
        self._build_falsifiers()
        self._build_g7()
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

    def _build_pack_go(self):
        from tests.test_arm_readiness import LaunchConsumptionV2Tests
        fixture = LaunchConsumptionV2Tests()
        fixture._fixture_root = self.base
        fixture._custody_window = self.root.name
        try:
            fixture.setUp()
            evidence = install_t0_inventory(fixture)
            inputs = fixture._consumer_inputs()
            go = inputs["authenticated_go_receipt"]
            go["t0_evidence"] = evidence
            go["t0_evidence_set_sha256"] = readiness.sha256_bytes(readiness.render_json(evidence))
            go["conditions"][1]["evidence"].extend(evidence)
            go["conditions"][3]["evidence"] = copy.deepcopy(go["conditions"][1]["evidence"])
            _write_json(inputs["go_receipt"], go)
            inputs["go_receipt_sha256"] = readiness.sha256_bytes(inputs["go_receipt"].read_bytes())
            with mock.patch.object(readiness, "_authenticate_go_t0_evidence", REAL_G5_T0_AUTHENTICATOR):
                fixture._invoke_consumer(inputs)
        finally:
            fixture.doCleanups()

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
            self.root / "night/go_receipt.json",
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
                "window_id": rehearsal.REHEARSAL_WINDOW_PREFIX + "fixture-001" + (
                    "-wrong-sibling" if self.broken_gate == "G6" else ""),
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

    def _build_g7(self):
        control = self.root.with_name(self.root.name + "-g7-control")
        self.g7_path = control / "night/g7_refusal.json"
        _write_json(self.g7_path, {
            "schema_version": rehearsal.G7_CONTROL_SCHEMA,
            "control_custody_root": str(control), "rehearsal_window_id": self.root.name,
            "control_plan_sha256": "a" * 64,
            "presented": [{"kind": kind, "path": str(control / "night" / filename),
                "sha256": readiness.sha256_bytes((self.root / "night/go_receipt.json" if kind == "rehearsal_go"
                    else self.records / "rehearsal-receipt.json").read_bytes()),
                "refusal": {"reason": "launch_go_receipt_invalid", "detail": detail},
                "first_refusal": True, "presented_monotonic_ns": at}
                for kind, filename, detail, at in (
                    ("rehearsal_receipt", "presented_rehearsal_receipt.json", "go_receipt.receipt_class", 10),
                    ("rehearsal_go", "presented_go_receipt.json", "rehearsal_purpose_on_production_id", 20))],
            "absence": {"consumption_absent": True, "chain_started_absent": True, "checked_monotonic_ns": 30},
            "verdict": "PASS"})

    def _build_manifest(self) -> None:
        production = self.base / "production"
        production.mkdir()
        inventory = fixture_inventory(self.root)
        _write_json(
            self.root / cli.MANIFEST_NAME,
            {
                "schema_version": cli.MANIFEST_SCHEMA,
                "t0_namespace": self.namespace.relative_to(self.root).as_posix(),
                "records": {
                    "execution": "records/execution.json",
                    "hid_idle": "records/hid-idle.txt",
                    "d149_go": "night/go_receipt.json",
                    "g7_control": {"path": str(self.g7_path), "sha256": readiness.sha256_bytes(self.g7_path.read_bytes())},
                    "rehearsal_receipt": "records/rehearsal-receipt.json",
                    "process_lineage": "records/process-lineage.json",
                    "lifecycle": "records/lifecycle.json",
                    "falsifier_controls": "records/falsifier-controls.json",
                    "positive_control": "records/positive-control.json",
                },
                "production_roots": [
                    {"role": item.role, "path": str(item.path)}
                    for item in readiness.production_custody_roots(
                        home=self.base / "home", inventory=inventory)
                ],
            },
        )


class T0RehearsalTests(unittest.TestCase):
    maxDiff = None

    def _run_rehearsal_arm_liveness_boundary(
        self, age_ns: int
    ) -> tuple[str, str | None]:
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        root = FixtureBuilder(Path(temporary.name)).build()
        bundle = fixture_bundle(root)
        _artifact, receipt, fact = rehearsal._clock_receipt(bundle)
        value = fact["value"]
        receipt["valid_until_monotonic_ns"] = (
            value["r1_batch_finished_monotonic_ns"]
            + 21_600_000_000_000
            + age_ns
        )
        return rehearsal._run_real_arm_boundary(receipt, 4_999_999)

    def test_rehearsal_t0_liveness_bound_refuses_at_600s_plus_1ns(self) -> None:
        self.assertEqual(
            self._run_rehearsal_arm_liveness_boundary(600_000_000_001),
            ("REFUSE", "readiness_clock_preflight_refused"),
        )

    def test_rehearsal_t0_liveness_bound_passes_at_600s_minus_1ns(self) -> None:
        self.assertEqual(
            self._run_rehearsal_arm_liveness_boundary(599_999_999_999),
            ("PASS", None),
        )

    def test_rehearsal_t0_liveness_bound_passes_at_exactly_600s(self) -> None:
        self.assertEqual(
            self._run_rehearsal_arm_liveness_boundary(600_000_000_000),
            ("PASS", None),
        )

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
        return temporary, root, evaluate_fixture(root)

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
        failed = [gate for gate in failed if gate["gate_id"] == gate_id]
        self.assertIn(message, failed[0]["message"])
        for gate in verdict["gates"]:
            if gate["gate_id"] != gate_id:
                self.assertEqual(gate["status"], "PASS", gate)
        return verdict

    def test_current_pack_bundle_composes_all_ten_gates_pass_through_loader(self):
        _temporary, _root, verdict = self._evaluate()
        self.assertEqual(verdict["overall_verdict"], "PASS", verdict)
        self.assertEqual(verdict["gate_counts"], {"PASS": 10, "FAIL": 0, "UNRULED": 0})
        self.assertEqual([gate["gate_id"] for gate in verdict["gates"]],
                         [f"G{i}" for i in range(1, 11)])

    def test_completed_bundle_loads_before_post_night_g7_control(self):
        _temporary, root, _verdict = self._evaluate()
        path = root / cli.MANIFEST_NAME
        manifest = readiness.parse_json_bytes(path.read_bytes())
        locator = manifest["records"].pop("g7_control")
        Path(locator["path"]).unlink()
        _write_json(path, manifest)
        verdict = evaluate_fixture(root)
        self.assertEqual(verdict["load_issues"], [])
        self.assertEqual(verdict["gate_counts"], {"PASS": 9, "FAIL": 1, "UNRULED": 0})
        self.assertEqual(verdict["gates"][6]["message"], "g7_control_pending")

    def test_g5_c2_real_t0_file_mutation_omission_and_substitution_fail(self):
        _temporary, root, verdict = self._evaluate()
        self.assertEqual(verdict["gates"][4]["status"], "PASS")
        go_path = root / "night/go_receipt.json"
        go_bytes = go_path.read_bytes()
        go = readiness.parse_json_bytes(go_bytes)
        capture, substitute = [root / ref["path"] for ref in go["t0_evidence"]
                               if "arm_readiness.t0.inputs/" in ref["path"]][:2]
        original = capture.read_bytes()
        for action in ("mutate", "omit", "substitute"):
            with self.subTest(action=action):
                if action == "omit":
                    capture.unlink()
                else:
                    capture.write_bytes(original + b" " if action == "mutate" else substitute.read_bytes())
                with fixture_replay(root):
                    result = rehearsal.evaluate_g5(fixture_bundle(root))
                self.assertEqual(result.status, rehearsal.GateStatus.FAIL, result.message)
                self.assertIn("t0_evidence", result.message)
                self.assertEqual(go_path.read_bytes(), go_bytes)  # C2 still advertises PASS.
                capture.write_bytes(original)
                with fixture_replay(root):
                    self.assertEqual(rehearsal.evaluate_g5(fixture_bundle(root)).status,
                                     rehearsal.GateStatus.PASS)

    def test_legacy_bundle_fails_g5_even_with_passing_g7_control(self) -> None:
        _temporary, _root, verdict = self._evaluate(broken_gate="G5")
        self.assertEqual(verdict["overall_verdict"], "FAIL")
        self.assertEqual(verdict["gate_counts"], {"PASS": 9, "FAIL": 1, "UNRULED": 0})
        self.assertEqual(verdict["gates"][6]["status"], "PASS")

    def test_g1_wrong_stdin_binding_fails_only_noninteractive_gate(self) -> None:
        self._assert_single_failure(
            "G1",
            broken_gate="G1",
            message="stdin was not bound to /dev/null",
        )

    def test_g1_missing_new_execution_record_is_unruled_not_pass(self) -> None:
        _temporary, root, _verdict = self._evaluate()
        (root / "records/execution.json").unlink()
        verdict = evaluate_fixture(root)
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

    def test_g5_refuses_legacy_receipt_even_with_condition_failure(self) -> None:
        self._assert_single_failure(
            "G5",
            broken_gate="G5",
            message="go_receipt",
        )

    def test_g6_real_path_containment_rejects_production_overlap(self) -> None:
        self._assert_single_failure(
            "G6",
            broken_gate="G6",
            message="rehearsal_roots_not_disjoint",
        )

    def test_g7_revalidates_bytes_schema_and_every_pass_condition(self):
        _temporary, root, _verdict = self._evaluate()
        bundle = fixture_bundle(root)
        artifact = bundle.record("g7_control")
        original = copy.deepcopy(artifact.value)
        mutations = [lambda v: v.update(extra=True), lambda v: v.update(schema_version="legacy"),
            lambda v: v.update(presented=v["presented"][:1]),
            lambda v: v["presented"][0]["refusal"].update(detail="ARM missing"),
            lambda v: v["presented"][0]["refusal"].update(detail="receipt_class"),
            lambda v: v["presented"][0]["refusal"].update(detail="night_plan.receipt_class"),
            lambda v: v["presented"][1].update(first_refusal=False),
            lambda v: v["absence"].update(consumption_absent=False),
            lambda v: v["absence"].update(chain_started_absent=False),
            lambda v: v["absence"].update(checked_monotonic_ns=0),
            lambda v: v.update(verdict="FAIL")]
        for mutate in mutations:
            value = copy.deepcopy(original)
            mutate(value)
            with self.subTest(value=value), self.assertRaises(ValueError):
                rehearsal.validate_g7_control(value)
        artifact.path.write_bytes(artifact.raw + b" ")
        self.assertEqual(rehearsal.evaluate_g7(bundle).status, rehearsal.GateStatus.FAIL)

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
        verdict = evaluate_fixture(root)
        failures = [gate for gate in verdict["gates"] if gate["status"] == "FAIL"]
        self.assertEqual([gate["gate_id"] for gate in failures], ["G9"])
        self.assertIn("human intervention occurred", failures[-1]["message"])

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

    def test_fixture_cli_reads_bytes_and_exits_success_for_pass(self) -> None:
        _temporary, root, _verdict = self._evaluate()
        output = io.BytesIO()
        with fixture_replay(root):
            code = cli.main(["--fixture-root", str(root)], stdout=output, home=root.parents[1], inventory=fixture_inventory(root))
        parsed = readiness.parse_json_bytes(output.getvalue(), require_canonical=True)
        self.assertEqual(code, 0)
        self.assertEqual(parsed["overall_verdict"], "PASS")
        self.assertEqual(output.getvalue(), readiness.render_json(parsed))

    def test_real_custody_cli_mode_uses_the_same_evidence_only_loader(self) -> None:
        _temporary, root, _verdict = self._evaluate()
        output = io.BytesIO()
        with fixture_replay(root):
            code = cli.main(["--custody-root", str(root)], stdout=output, home=root.parents[1], inventory=fixture_inventory(root))
        parsed = readiness.parse_json_bytes(output.getvalue(), require_canonical=True)
        self.assertEqual(code, 0)
        self.assertEqual(parsed["gate_counts"], {"PASS": 10, "FAIL": 0, "UNRULED": 0})


class PackGoReplayTests(unittest.TestCase):
    """Real GO/consumption replay; synthetic ARM semantics and T0 prerequisites."""

    def setUp(self):
        from tests.test_arm_readiness import PackNightConsumerTests
        self.case = PackNightConsumerTests()
        self.case.setUp()
        self.addCleanup(self.case.doCleanups)
        self.fixture = self.case.fixture
        self.case.rewrite_go(lambda go: go["conditions"][3].update(
            evidence=copy.deepcopy(go["conditions"][1]["evidence"])))
        self.case.consume()

    def bundle(self):
        artifacts, issues = cli._crawl(self.fixture.custody)
        go = next(item for item in artifacts if item.relative_path == "night/go_receipt.json")
        return rehearsal.EvidenceBundle(self.fixture.custody, self.fixture.custody,
            go, artifacts, {"d149_go": go.relative_path}, (), issues)

    def evaluate(self):
        with mock.patch.object(readiness, "_derive_arm_semantics_for_verification",
                return_value=(self.fixture.arm["rows"], self.fixture.arm["refusals"])):
            return rehearsal.evaluate_g5(self.bundle())

    def rebind(self):
        def references(go):
            for condition in go["conditions"]:
                for ref in condition["evidence"]:
                    ref["sha256"] = readiness.sha256_bytes((self.fixture.custody / ref["path"]).read_bytes())
        self.case.rewrite_go(references)
        record = readiness.parse_json_bytes(self.case.consumption.read_bytes())
        record["go_receipt"]["sha256"] = self.case.inputs["go_receipt_sha256"]
        self.case.rewrite_consumption(record)

    def test_g5_pack_go_replays_c1_through_c5_and_refuses_d149(self):
        result = self.evaluate()
        self.assertEqual(result.status, rehearsal.GateStatus.PASS, result.message)
        path = self.case.inputs["go_receipt"]
        _write_json(path, {"schema_version": rehearsal.D149_SCHEMA, "verdict": "GO",
                          "conditions": [{"condition_id": f"C{i}", "status": "PASS", "evidence": []} for i in range(1, 6)]})
        self.assertEqual(self.evaluate().status, rehearsal.GateStatus.FAIL)

    def test_g5_recomputes_authorization_despite_pass_labels_and_rebound_hashes(self):
        path = Path(self.case.inputs["authenticated_go_receipt"]["authorization"]["path"])
        value = readiness.parse_json_bytes(path.read_bytes())
        value["permitted_blocks"] = 2
        _write_json(path, value)
        digest = readiness.sha256_bytes(path.read_bytes())
        plan_path = self.case.inputs["night_plan"]
        plan = readiness.parse_json_bytes(plan_path.read_bytes())
        plan["pack_night"]["authorization_record"]["sha256"] = digest
        _write_json(plan_path, plan)
        plan_digest = readiness.sha256_bytes(plan_path.read_bytes())
        self.case.rewrite_go(lambda go: (go["authorization"].update(sha256=digest), go.update(plan_sha256=plan_digest)))
        self.rebind()
        record = readiness.parse_json_bytes(self.case.consumption.read_bytes())
        record["night_plan"]["sha256"] = plan_digest
        record["go_receipt"]["plan_sha256"] = plan_digest
        self.case.rewrite_consumption(record)
        result = self.evaluate()
        self.assertEqual(result.status, rehearsal.GateStatus.FAIL)
        self.assertIn("G2B_SHAKEDOWN", result.message)

    def test_g5_requires_arm_semantic_replay_and_real_t0_inventory(self):
        with mock.patch.object(readiness, "_derive_arm_semantics_for_verification",
                return_value=([], [{"reason": "refused"}])):
            result = rehearsal.evaluate_g5(self.bundle())
        self.assertEqual(result.status, rehearsal.GateStatus.FAIL)
        self.assertIn("PASS/GO", result.message)
        with mock.patch.object(readiness, "_authenticate_go_t0_evidence", REAL_G5_T0_AUTHENTICATOR):
            result = self.evaluate()
        self.assertEqual(result.status, rehearsal.GateStatus.FAIL)
        self.assertIn("t0_evidence", result.message)

    def test_g5_recomputes_census_instead_of_accepting_c3_pass(self):
        self.case.rewrite_go(lambda go: go["census"].update(exit_code=0))
        self.rebind()
        result = self.evaluate()
        self.assertEqual(result.status, rehearsal.GateStatus.FAIL)
        self.assertIn("census", result.message)

    def test_g5_recomputes_clock_bounds_instead_of_accepting_c4_pass(self):
        consumed = readiness.parse_json_bytes(self.case.consumption.read_bytes())["consumed_at_monotonic_ns"]
        self.case.rewrite_go(lambda go: go.update(valid_until_monotonic_ns=consumed))
        self.rebind()
        result = self.evaluate()
        self.assertEqual(result.status, rehearsal.GateStatus.FAIL)
        self.assertIn("monotonic", result.message)

    def test_g5_requires_one_consumption_instead_of_accepting_c5_pass(self):
        self.case.consumption.unlink()
        result = self.evaluate()
        self.assertEqual(result.status, rehearsal.GateStatus.FAIL)
        self.assertIn("exactly one consumption", result.message)

    def test_g5_numeric_types_condition_order_and_vocabulary_are_exact(self):
        original = copy.deepcopy(self.case.inputs["authenticated_go_receipt"])
        mutations = [lambda go: go.update(issued_epoch_s=1),
            lambda go: go.update(issued_monotonic_ns=True),
            lambda go: go.update(valid_until_monotonic_ns=1.5),
            lambda go: go["conditions"].reverse(),
            lambda go: go["conditions"][1].update(condition_id="C1"),
            lambda go: go["conditions"][0].update(status="NOT_APPLICABLE"),
            lambda go: go["conditions"][0].update(status="GO"),
            lambda go: go["conditions"][0].update(basis="no_pack_by_design")]
        for mutate in mutations:
            value = copy.deepcopy(original)
            mutate(value)
            _write_json(self.case.inputs["go_receipt"], value)
            self.rebind()
            with self.subTest(value=value):
                self.assertEqual(self.evaluate().status, rehearsal.GateStatus.FAIL)

    def test_g5_refuses_higher_arm_on_same_boot(self):
        value = copy.deepcopy(self.fixture.arm)
        value["receipt_id"] = "arm-0002"
        value["supersedes"] = {"receipt_id": self.fixture.arm["receipt_id"],
            "receipt_path": "arm_readiness.receipts/arm-0001.json",
            "receipt_sha256": readiness.sha256_bytes(self.fixture.arm_path.read_bytes()),
            "pack_id": value["pack"]["pack_id"], "pack_sha256": value["pack"]["pack_sha256"]}
        path = self.fixture.arm_path.with_name("arm-0002.json")
        _write_json(path, value)
        path.with_name(path.name + ".sha256").write_bytes(
            readiness.gnu_sidecar(readiness.sha256_bytes(path.read_bytes()), path.name))
        result = self.evaluate()
        self.assertEqual(result.status, rehearsal.GateStatus.FAIL)
        self.assertIn("superseded", result.message)


if __name__ == "__main__":
    unittest.main()
