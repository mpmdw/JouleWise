"""D-100 attempt, closure, launcher-refusal, and payload regressions."""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import tempfile
import unittest
from pathlib import Path

from joulewise.salvage_dangler import (
    LAUNCHER_REFUSAL_SCHEMA,
    MEMBERSHIP_BINDING_SCHEMA,
    SALVAGE_CLOSURE_SCHEMA,
    SalvageAuthorizationError,
    authorize_salvage_dangler_exclusion,
    build_salvage_exclusion_payload,
    inspect_launcher_refusal,
    inspect_preworkload_abort,
    inspect_salvage_attempt,
    load_salvage_closure,
    validate_salvage_exclusion_payload,
)


FIXTURE = Path("tests/fixtures/salvage_dangler/r5a_idle_abort")
REAL_QUARANTINE = (
    Path.home()
    / "JouleWise-window-custody"
    / "window_metrologyB_20260801"
    / "quarantine"
)
# Canonical SHA-256 of each subject's complete {path, sha256, size} manifest.
# These pins make the external, byte-faithful 22-file fixtures reviewable
# without copying roughly 154 MiB per subject into the repository.
BYTE_FAITHFUL_FIXTURE_SHA256 = {
    "mtadd-p2048o0128-r08__20260801T131705Z": (
        "72fb6d92cceead16c6082c0fd2266727989bb94deffe9e0f2df91fa0c947c2e2"
    ),
    "mtadd-p2048o0128-r08__20260801T133315Z": (
        "329bc9f88295eb6a7ab91a25f28ea2600483fca42bd3e3396629a1aee5df3039"
    ),
    "mtnull-o0512-b04-b2__20260801T113258Z": (
        "1857ebb709713a0aa0ea640ee3c2598c5d13ca085333e8b435a5a7883db7ef0d"
    ),
}
POLICY_SHA = "a" * 64


def canonical_sha256(value: object) -> str:
    return hashlib.sha256(
        json.dumps(
            value,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
            allow_nan=False,
        ).encode("utf-8")
    ).hexdigest()


def digest_manifest(root: Path) -> list[dict[str, object]]:
    return [
        {
            "path": path.relative_to(root).as_posix(),
            "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
            "size": path.stat().st_size,
        }
        for path in sorted(
            candidate for candidate in root.rglob("*") if candidate.is_file()
        )
    ]


class SalvageDanglerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def copy_attempt(self, name: str = "attempt") -> Path:
        destination = self.root / name
        shutil.copytree(FIXTURE, destination)
        idle_rows = [
            {"index": 1, "processor_combined_power_w": 0.19, "timestamp_s": 99.81},
            {"index": 2, "processor_combined_power_w": 0.21, "timestamp_s": 99.91},
        ]
        retry_rows = [
            {"index": 1, "processor_combined_power_w": 0.22, "timestamp_s": 99.92},
            {"index": 2, "processor_combined_power_w": 0.24, "timestamp_s": 100.05},
        ]
        for telemetry_name, rows in (
            ("rich_telemetry_idle.jsonl", idle_rows),
            ("rich_telemetry_idle_attempt_2.jsonl", retry_rows),
        ):
            (destination / telemetry_name).write_text(
                "".join(json.dumps(row) + "\n" for row in rows), encoding="utf-8"
            )
        return destination

    def write_binding(self) -> Path:
        path = self.root / "membership.json"
        descriptors = [
            {"path": "campaign_manifests/window.json", "sha256": "b" * 64, "size": 12}
        ]
        path.write_text(
            json.dumps(
                {
                    "schema_version": MEMBERSHIP_BINDING_SCHEMA,
                    "campaign_policy_sha256": POLICY_SHA,
                    "source_campaign_manifests": descriptors,
                    "membership_id": canonical_sha256(descriptors),
                },
                sort_keys=True,
            )
            + "\n",
            encoding="utf-8",
        )
        return path

    def write_closure(self, *, with_siblings: bool = False) -> tuple[Path, Path]:
        quarantine = self.root / "quarantine"
        quarantine.mkdir()
        attempts = [
            self.copy_attempt(f"quarantine/attempt-{index}") for index in range(3)
        ]
        for path, bundle_id in zip(
            attempts,
            ("prior-failure-a", "prior-failure-b", "d100-dangler-r5a"),
            strict=True,
        ):
            config = json.loads((path / "config.json").read_text())
            config["run_id"] = bundle_id
            (path / "config.json").write_text(json.dumps(config) + "\n")
            metadata = json.loads((path / "metadata.json").read_text())
            metadata["run_id"] = bundle_id
            (path / "metadata.json").write_text(json.dumps(metadata) + "\n")
        if with_siblings:
            self.copy_attempt("quarantine/sibling-a")
            sibling_b = self.copy_attempt("quarantine/sibling-b")
            sibling_config = json.loads((sibling_b / "config.json").read_text())
            sibling_config["run_id"] = "different-sibling"
            (sibling_b / "config.json").write_text(json.dumps(sibling_config) + "\n")
        inspected = [inspect_salvage_attempt(path) for path in attempts]
        binding = self.write_binding()
        binding_sha = hashlib.sha256(binding.read_bytes()).hexdigest()
        closure = {
            "schema_version": SALVAGE_CLOSURE_SCHEMA,
            "campaign_policy_sha256": POLICY_SHA,
            "membership_binding_sha256": binding_sha,
            "opened_at": "2026-08-01T10:00:00Z",
            "closed_at": "2026-08-01T12:00:00Z",
            "custody_roots": [str(quarantine)],
            "quarantine_root": str(quarantine),
            "quarantine_manifest": digest_manifest(quarantine),
            "terminal_occurrence_index": 2,
            "occurrences": [
                {
                    "timestamp": f"2026-08-01T10:0{index}:00Z",
                    "quarantine_path": str(path),
                    "license_branch": observation["license_branch"],
                    "failure_signature_sha256": observation[
                        "failure_signature_sha256"
                    ],
                    "evidence_paths": observation["artifact_manifest"],
                    "operator_deviations": [],
                }
                for index, (path, observation) in enumerate(
                    zip(attempts, inspected, strict=True)
                )
            ],
        }
        path = self.root / "closure.json"
        path.write_text(json.dumps(closure, sort_keys=True) + "\n", encoding="utf-8")
        return path, binding

    def test_r5a_real_idle_abort_shape_accepts_171ms_teardown(self) -> None:
        observation = inspect_salvage_attempt(self.copy_attempt())
        self.assertTrue(observation["licensed"])
        self.assertEqual(observation["terminal_stage"], "idle_baseline")
        self.assertAlmostEqual(observation["teardown_s"], 0.171)
        self.assertEqual(
            {row["path"] for row in observation["artifact_manifest"]},
            {
                "config.json",
                "metadata.json",
                "summary_metrics.json",
                "events.jsonl",
                "power_trace.csv",
                "rich_telemetry.jsonl",
                "rich_telemetry_idle.jsonl",
                "rich_telemetry_idle_attempt_2.jsonl",
            },
        )
        second = self.copy_attempt("r5a-136ms")
        (second / "power_trace.csv").write_text(
            "timestamp_s,power_w,source,rail,interval_start_s,interval_end_s\n"
            "99.9,0.2,powermetrics,cpu_power,99.8,99.9\n"
            "100.136,0.3,powermetrics,cpu_power,100.05,100.136\n",
            encoding="utf-8",
        )
        self.assertAlmostEqual(inspect_salvage_attempt(second)["teardown_s"], 0.136)

    def test_r5_workload_stage_or_measurand_bytes_refuse(self) -> None:
        attempt = self.copy_attempt()
        events = [
            json.loads(line)
            for line in (attempt / "events.jsonl").read_text().splitlines()
        ]
        events.insert(
            -1,
            {
                "event_type": "stage_started",
                "phase": "workload",
                "timestamp_s": 101.0,
            },
        )
        (attempt / "events.jsonl").write_text(
            "".join(json.dumps(row) + "\n" for row in events)
        )
        with self.assertRaisesRegex(SalvageAuthorizationError, "stage_started"):
            inspect_preworkload_abort(attempt)

        attempt = self.copy_attempt("measurand")
        summary = json.loads((attempt / "summary_metrics.json").read_text())
        summary["gross_energy_j"] = 0.001
        (attempt / "summary_metrics.json").write_text(json.dumps(summary) + "\n")
        with self.assertRaisesRegex(SalvageAuthorizationError, "measurand"):
            inspect_salvage_attempt(attempt)

    def test_r5b_missing_or_truncated_events_and_late_telemetry_refuse(self) -> None:
        attempt = self.copy_attempt()
        (attempt / "events.jsonl").write_text('{"event_type":', encoding="utf-8")
        with self.assertRaisesRegex(SalvageAuthorizationError, "truncated"):
            inspect_salvage_attempt(attempt)

        attempt = self.copy_attempt("late")
        with (attempt / "power_trace.csv").open("a", encoding="utf-8") as handle:
            handle.write("100.251,0.1,powermetrics,cpu_power,100.2,100.251\n")
        with self.assertRaisesRegex(SalvageAuthorizationError, "teardown bound"):
            inspect_salvage_attempt(attempt)

    def test_d106_early_telemetry_substitution_refuses(self) -> None:
        attempt = self.copy_attempt()
        telemetry_path = attempt / "rich_telemetry.jsonl"
        rows = [json.loads(line) for line in telemetry_path.read_text().splitlines()]
        for index, row in enumerate(rows, start=1):
            row["timestamp_s"] = float(index)
        telemetry_path.write_text(
            "".join(json.dumps(row) + "\n" for row in rows), encoding="utf-8"
        )
        with self.assertRaisesRegex(SalvageAuthorizationError, "telemetry interval"):
            inspect_salvage_attempt(attempt)

    def test_d108_nested_content_does_not_void_license(self) -> None:
        attempt = self.copy_attempt()
        metadata_path = attempt / "metadata.json"
        events_path = attempt / "events.jsonl"
        summary_path = attempt / "summary_metrics.json"
        metadata = json.loads(metadata_path.read_text())
        metadata["environment_admission"]["future_nested"] = {
            "model_output": {"tokens": ["content grammar is non-load-bearing"]}
        }
        metadata_path.write_text(json.dumps(metadata) + "\n", encoding="utf-8")
        events = [json.loads(line) for line in events_path.read_text().splitlines()]
        failure = next(row for row in events if row["event_type"] == "failure")
        failure["metadata"]["future_nested"] = {
            "generated_text": ["diagnostic-only content"]
        }
        events_path.write_text(
            "".join(json.dumps(row) + "\n" for row in events), encoding="utf-8"
        )
        summary = json.loads(summary_path.read_text())
        summary["future_nested"] = {"runtime_result": {"value": "hygiene-only"}}
        summary_path.write_text(json.dumps(summary) + "\n", encoding="utf-8")

        self.assertTrue(inspect_salvage_attempt(attempt)["licensed"])

    def test_d107_false_refusal_domains_license(self) -> None:
        attempt = self.copy_attempt()
        metadata_path = attempt / "metadata.json"
        metadata = json.loads(metadata_path.read_text())
        metadata["environment_admission"]["guard_observations"] = [
            {"phase": "before_attempt_1"},
            {"phase": "after_attempt_1"},
            {"phase": "before_attempt_2"},
            {"phase": "after_attempt_2"},
        ]
        metadata["extra"] = {
            "preceding_member_end_s": None,
            "idle_start_s": 99.0,
            "preceding_gap_s": None,
            "clock_step_suspect": True,
            "cooldown_cap_hit": True,
            "environment_admission_failed": True,
            "node_cleanup": [
                {"path": "remote-a", "removed": False},
                {
                    "task_id": "node-task-1",
                    "scope": "remote",
                    "path": "/tmp/node-task-1",
                    "removed": True,
                    "error": None,
                    "after_durable_custody": True,
                },
            ],
        }
        metadata_path.write_text(json.dumps(metadata) + "\n", encoding="utf-8")

        self.assertTrue(inspect_salvage_attempt(attempt)["licensed"])

    def test_d107_hash_pinned_real_quarantine_shapes_all_license(self) -> None:
        if not REAL_QUARANTINE.is_dir():
            self.skipTest("window-B quarantine custody path is absent")
        subjects = {
            path.name: path for path in REAL_QUARANTINE.iterdir() if path.is_dir()
        }
        self.assertEqual(set(subjects), set(BYTE_FAITHFUL_FIXTURE_SHA256))
        for name, expected_sha256 in BYTE_FAITHFUL_FIXTURE_SHA256.items():
            with self.subTest(subject=name):
                manifest = digest_manifest(subjects[name])
                self.assertEqual(len(manifest), 22)
                self.assertEqual(canonical_sha256(manifest), expected_sha256)
                self.assertTrue(inspect_salvage_attempt(subjects[name])["licensed"])

    def test_b3_closed_idle_inventory_rejects_extra_artifact(self) -> None:
        attempt = self.copy_attempt()
        (attempt / "workload_result.json").write_text(
            json.dumps({"status": "succeeded", "phase": "workload"}) + "\n",
            encoding="utf-8",
        )
        with self.assertRaisesRegex(
            SalvageAuthorizationError, "unexpected salvage artifact"
        ):
            inspect_salvage_attempt(attempt)

    def test_b3_closed_event_sequence_rejects_non_stage_workload_event(self) -> None:
        attempt = self.copy_attempt()
        events = [
            json.loads(line)
            for line in (attempt / "events.jsonl").read_text().splitlines()
        ]
        events.insert(
            -1,
            {
                "event_type": "measurement_result",
                "phase": "workload",
                "timestamp_s": 101.0,
            },
        )
        (attempt / "events.jsonl").write_text(
            "".join(json.dumps(row) + "\n" for row in events),
            encoding="utf-8",
        )
        with self.assertRaisesRegex(SalvageAuthorizationError, "unexpected event"):
            inspect_preworkload_abort(attempt)

    def test_b3_closed_inventory_rejects_copied_idle_telemetry(self) -> None:
        attempt = self.copy_attempt()
        metadata_path = attempt / "metadata.json"
        metadata = json.loads(metadata_path.read_text())
        metadata["environment_admission"]["attempts"] = [
            {"admitted": False, "attempt": 1}
        ]
        metadata_path.write_text(json.dumps(metadata) + "\n", encoding="utf-8")
        (attempt / "rich_telemetry_idle_attempt_2.jsonl").unlink()
        shutil.copyfile(
            attempt / "rich_telemetry.jsonl",
            attempt / "rich_telemetry_idle.jsonl",
        )
        with self.assertRaisesRegex(
            SalvageAuthorizationError, "duplicate telemetry content"
        ):
            inspect_salvage_attempt(attempt)

    def test_b3_telemetry_rejects_workload_fields_inside_teardown_bound(self) -> None:
        attempt = self.copy_attempt()
        telemetry_path = attempt / "rich_telemetry.jsonl"
        rows = [json.loads(line) for line in telemetry_path.read_text().splitlines()]
        rows[-1].update(
            {
                "phase": "measured_run",
                "workload_result": {"gross_energy_j": 0.0},
                "output_token_count": 0,
            }
        )
        telemetry_path.write_text(
            "".join(json.dumps(row) + "\n" for row in rows), encoding="utf-8"
        )
        with self.assertRaisesRegex(
            SalvageAuthorizationError, "admission-phase telemetry"
        ):
            inspect_salvage_attempt(attempt)

    def test_full_file_enumeration_rejects_symlinks_and_duplicate_inodes(self) -> None:
        attempt = self.copy_attempt()
        os.symlink(attempt / "config.json", attempt / "alias.json")
        with self.assertRaisesRegex(SalvageAuthorizationError, "non-regular"):
            inspect_salvage_attempt(attempt)

        attempt = self.copy_attempt("hardlink")
        os.link(attempt / "config.json", attempt / "duplicate.json")
        with self.assertRaisesRegex(SalvageAuthorizationError, "duplicate artifact"):
            inspect_salvage_attempt(attempt)

        attempt = self.copy_attempt("root-target")
        root_alias = self.root / "root-alias"
        os.symlink(attempt, root_alias)
        with self.assertRaisesRegex(SalvageAuthorizationError, "attempt path.*symlink"):
            inspect_salvage_attempt(root_alias)

    def test_d087_closure_and_exclusion_payload_reauthenticate_all_bytes(self) -> None:
        closure_path, binding_path = self.write_closure()
        closure = load_salvage_closure(
            closure_path,
            expected_policy_sha256=POLICY_SHA,
            expected_membership_binding_sha256=hashlib.sha256(
                binding_path.read_bytes()
            ).hexdigest(),
        )
        payload = build_salvage_exclusion_payload(closure, binding_path)
        self.assertTrue(validate_salvage_exclusion_payload(payload))
        authorized = authorize_salvage_dangler_exclusion(
            closure_path,
            binding_path,
            campaign_policy_sha256=POLICY_SHA,
            terminal_absent_bundle_ids=["d100-dangler-r5a"],
        )
        self.assertEqual(authorized, payload)

        tampered = dict(payload)
        tampered.pop("payload_sha256")
        self.assertFalse(validate_salvage_exclusion_payload(tampered))

    def test_d106_quarantine_digest_freeze_rejects_sibling_copy(self) -> None:
        closure_path, binding_path = self.write_closure(with_siblings=True)
        sibling_a = self.root / "quarantine" / "sibling-a" / "config.json"
        sibling_b = self.root / "quarantine" / "sibling-b" / "config.json"
        shutil.copyfile(sibling_a, sibling_b)

        with self.assertRaisesRegex(SalvageAuthorizationError, "quarantine manifest"):
            authorize_salvage_dangler_exclusion(
                closure_path,
                binding_path,
                campaign_policy_sha256=POLICY_SHA,
                terminal_absent_bundle_ids=["d100-dangler-r5a"],
            )

    def test_preworkload_closure_without_quarantine_manifest_refuses(self) -> None:
        closure_path, _binding_path = self.write_closure()
        closure = json.loads(closure_path.read_text(encoding="utf-8"))
        closure.pop("quarantine_manifest")
        closure_path.write_text(
            json.dumps(closure, sort_keys=True) + "\n", encoding="utf-8"
        )

        with self.assertRaisesRegex(SalvageAuthorizationError, "quarantine manifest"):
            load_salvage_closure(closure_path)

    def test_r6_cap_one_and_waivers_refuse(self) -> None:
        closure_path, binding_path = self.write_closure()
        for absent in ([], ["d100-dangler-r5a", "other"]):
            with self.subTest(absent=absent), self.assertRaisesRegex(
                SalvageAuthorizationError, "cap is exactly one"
            ):
                authorize_salvage_dangler_exclusion(
                    closure_path,
                    binding_path,
                    campaign_policy_sha256=POLICY_SHA,
                    terminal_absent_bundle_ids=absent,
                )
        with self.assertRaisesRegex(SalvageAuthorizationError, "waivers"):
            authorize_salvage_dangler_exclusion(
                closure_path,
                binding_path,
                campaign_policy_sha256=POLICY_SHA,
                terminal_absent_bundle_ids=["d100-dangler-r5a"],
                waivers=[{"scope": "status_failed"}],
            )

    def test_b_i_hash_bound_launcher_refusal_requires_zero_occurrence_bytes(self) -> None:
        custody = self.root / "custody"
        custody.mkdir()
        core = {
            "schema_version": LAUNCHER_REFUSAL_SCHEMA,
            "bundle_id": "never-launched",
            "timestamp": "2026-08-01T10:00:00Z",
            "reason": "launcher refused before bundle creation",
            "refusal_code": "launcher_precondition_refused",
        }
        refusal = {**core, "record_sha256": canonical_sha256(core)}
        observation = inspect_launcher_refusal(refusal, [custody])
        self.assertEqual(observation["license_branch"], "launcher_refusal_zero_bytes")

        (custody / "never-launched").mkdir()
        with self.assertRaisesRegex(SalvageAuthorizationError, "bytes exist"):
            inspect_launcher_refusal(refusal, [custody])

    def test_b2_launcher_refusal_sweep_finds_renamed_partial_bundle_content(self) -> None:
        custody = self.root / "custody"
        partial = custody / "x"
        partial.mkdir(parents=True)
        core = {
            "schema_version": LAUNCHER_REFUSAL_SCHEMA,
            "bundle_id": "never-launched",
            "timestamp": "2026-08-01T10:00:00Z",
            "reason": "launcher refused before bundle creation",
            "refusal_code": "launcher_precondition_refused",
        }
        refusal = {**core, "record_sha256": canonical_sha256(core)}
        (partial / "metadata.json").write_text(
            json.dumps({"run_id": "never-launched"}) + "\n", encoding="utf-8"
        )
        (partial / "events.jsonl").write_text(
            json.dumps(
                {
                    "event_type": "run_started",
                    "bundle_id": "never-launched",
                    "timestamp_s": 1.0,
                }
            )
            + "\n",
            encoding="utf-8",
        )
        with self.assertRaisesRegex(SalvageAuthorizationError, "bytes exist"):
            inspect_launcher_refusal(refusal, [custody])

    def _assert_b2_raw_occurrence_bytes_refuse(self, relative_path: str) -> None:
        custody = self.root / "custody"
        candidate = custody / "nested" / relative_path
        candidate.parent.mkdir(parents=True)
        core = {
            "schema_version": LAUNCHER_REFUSAL_SCHEMA,
            "bundle_id": "never-launched",
            "timestamp": "2026-08-01T10:00:00Z",
            "reason": "launcher refused before bundle creation",
            "refusal_code": "launcher_precondition_refused",
        }
        refusal = {**core, "record_sha256": canonical_sha256(core)}
        candidate.write_bytes(
            b'\x00unparsed:{"bundle_id":"never-launched"}:bytes\xff'
        )
        with self.assertRaisesRegex(SalvageAuthorizationError, "bytes exist"):
            inspect_launcher_refusal(refusal, [custody])

    def test_b2_total_sweep_finds_raw_bytes_in_summary_metrics(self) -> None:
        self._assert_b2_raw_occurrence_bytes_refuse("summary_metrics.json")

    def test_b2_total_sweep_finds_raw_bytes_in_rich_telemetry(self) -> None:
        self._assert_b2_raw_occurrence_bytes_refuse("rich_telemetry.jsonl")

    def test_b2_total_sweep_finds_raw_bytes_in_renamed_json(self) -> None:
        self._assert_b2_raw_occurrence_bytes_refuse("renamed.json")

    def test_launcher_refusal_hash_and_custody_universe_fail_closed(self) -> None:
        custody = self.root / "custody"
        custody.mkdir()
        core = {
            "schema_version": LAUNCHER_REFUSAL_SCHEMA,
            "bundle_id": "never-launched",
            "timestamp": "2026-08-01T10:00:00Z",
            "reason": "launcher refused before bundle creation",
            "refusal_code": "launcher_precondition_refused",
        }
        with self.assertRaisesRegex(SalvageAuthorizationError, "malformed"):
            inspect_launcher_refusal({**core, "record_sha256": "0" * 64}, [custody])
        with self.assertRaisesRegex(SalvageAuthorizationError, "universe is empty"):
            inspect_launcher_refusal(
                {**core, "record_sha256": canonical_sha256(core)}, []
            )

    def test_b_i_closure_binds_refusal_files_and_zero_byte_universe(self) -> None:
        runs_root = self.root / "runs"
        quarantine = self.root / "quarantine"
        refusal_root = self.root / "refusals"
        runs_root.mkdir()
        quarantine.mkdir()
        refusal_root.mkdir()
        binding = self.write_binding()
        occurrences = []
        for index in range(3):
            core = {
                "schema_version": LAUNCHER_REFUSAL_SCHEMA,
                "bundle_id": "never-launched",
                "timestamp": f"2026-08-01T10:0{index}:00Z",
                "reason": "launcher refused before bundle creation",
                "refusal_code": "launcher_precondition_refused",
            }
            refusal = {**core, "record_sha256": canonical_sha256(core)}
            refusal_path = refusal_root / f"refusal-{index}.json"
            refusal_path.write_text(json.dumps(refusal) + "\n")
            occurrences.append(
                {
                    "timestamp": core["timestamp"],
                    "license_branch": "launcher_refusal_zero_bytes",
                    "launcher_refusal_path": str(refusal_path),
                    "failure_signature_sha256": inspect_launcher_refusal(
                        refusal, [runs_root, quarantine]
                    )["failure_signature_sha256"],
                    "evidence_paths": [
                        {
                            "path": str(refusal_path.resolve()),
                            "sha256": hashlib.sha256(
                                refusal_path.read_bytes()
                            ).hexdigest(),
                            "size": refusal_path.stat().st_size,
                        }
                    ],
                    "operator_deviations": [],
                }
            )
        closure_value = {
            "schema_version": SALVAGE_CLOSURE_SCHEMA,
            "campaign_policy_sha256": POLICY_SHA,
            "membership_binding_sha256": hashlib.sha256(
                binding.read_bytes()
            ).hexdigest(),
            "opened_at": "2026-08-01T10:00:00Z",
            "closed_at": "2026-08-01T10:03:00Z",
            "runs_root": str(runs_root),
            "quarantine_roots": [str(quarantine)],
            "custody_roots": [str(quarantine)],
            "terminal_occurrence_index": 2,
            "occurrences": occurrences,
        }
        closure_path = self.root / "launcher-closure.json"
        closure_path.write_text(json.dumps(closure_value) + "\n")
        with self.assertRaisesRegex(SalvageAuthorizationError, "runs root"):
            load_salvage_closure(
                closure_path,
                expected_runs_root=runs_root,
            )

        extra = self.root / "undeclared-custody"
        extra.mkdir()
        closure_value["custody_roots"] = [
            str(runs_root),
            str(quarantine),
            str(extra),
        ]
        closure_path.write_text(json.dumps(closure_value) + "\n")
        with self.assertRaisesRegex(SalvageAuthorizationError, "must equal"):
            load_salvage_closure(
                closure_path,
                expected_runs_root=runs_root,
            )

        missing = self.root / "missing-quarantine"
        closure_value["quarantine_roots"] = [str(missing)]
        closure_value["custody_roots"] = [str(runs_root), str(missing)]
        closure_path.write_text(json.dumps(closure_value) + "\n")
        with self.assertRaisesRegex(SalvageAuthorizationError, "cannot be resolved"):
            load_salvage_closure(
                closure_path,
                expected_runs_root=runs_root,
            )

        closure_value["quarantine_roots"] = [str(quarantine)]
        closure_value["custody_roots"] = [str(runs_root), str(quarantine)]
        closure_path.write_text(json.dumps(closure_value) + "\n")
        closure = load_salvage_closure(
            closure_path,
            expected_runs_root=runs_root,
        )
        payload = build_salvage_exclusion_payload(closure, binding)
        self.assertTrue(validate_salvage_exclusion_payload(payload))


if __name__ == "__main__":
    unittest.main()
