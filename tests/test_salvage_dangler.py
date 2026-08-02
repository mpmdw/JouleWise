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


class SalvageDanglerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def copy_attempt(self, name: str = "attempt") -> Path:
        destination = self.root / name
        shutil.copytree(FIXTURE, destination)
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

    def write_closure(self) -> tuple[Path, Path]:
        attempts = [self.copy_attempt(f"attempt-{index}") for index in range(3)]
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
        inspected = [inspect_salvage_attempt(path) for path in attempts]
        binding = self.write_binding()
        binding_sha = hashlib.sha256(binding.read_bytes()).hexdigest()
        closure = {
            "schema_version": SALVAGE_CLOSURE_SCHEMA,
            "campaign_policy_sha256": POLICY_SHA,
            "membership_binding_sha256": binding_sha,
            "opened_at": "2026-08-01T10:00:00Z",
            "closed_at": "2026-08-01T12:00:00Z",
            "custody_roots": [str(self.root)],
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

    def test_unknown_nonnull_summary_fields_fail_closed(self) -> None:
        attempt = self.copy_attempt()
        summary = json.loads((attempt / "summary_metrics.json").read_text())
        summary["future_measurement"] = {"value": 0.0}
        (attempt / "summary_metrics.json").write_text(json.dumps(summary) + "\n")
        with self.assertRaisesRegex(SalvageAuthorizationError, "unknown non-null"):
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
        custody = self.root / "custody"
        custody.mkdir()
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
            refusal_path = custody / f"refusal-{index}.json"
            refusal_path.write_text(json.dumps(refusal) + "\n")
            occurrences.append(
                {
                    "timestamp": core["timestamp"],
                    "license_branch": "launcher_refusal_zero_bytes",
                    "launcher_refusal_path": str(refusal_path),
                    "failure_signature_sha256": inspect_launcher_refusal(
                        refusal, [custody]
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
        closure_path = self.root / "launcher-closure.json"
        closure_path.write_text(
            json.dumps(
                {
                    "schema_version": SALVAGE_CLOSURE_SCHEMA,
                    "campaign_policy_sha256": POLICY_SHA,
                    "membership_binding_sha256": hashlib.sha256(
                        binding.read_bytes()
                    ).hexdigest(),
                    "opened_at": "2026-08-01T10:00:00Z",
                    "closed_at": "2026-08-01T10:03:00Z",
                    "custody_roots": [str(custody)],
                    "terminal_occurrence_index": 2,
                    "occurrences": occurrences,
                }
            )
            + "\n"
        )
        closure = load_salvage_closure(closure_path)
        payload = build_salvage_exclusion_payload(closure, binding)
        self.assertTrue(validate_salvage_exclusion_payload(payload))


if __name__ == "__main__":
    unittest.main()
