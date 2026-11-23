"""Fault combinations for the primary's optional export and reducer branches."""
from contextlib import contextmanager
import io
import json
from pathlib import Path
import plistlib
import tempfile
import unittest
from unittest.mock import patch

from joulewise import environment_admission
from tests.b6.support import document
from tests.test_bytes_availability import (
    AvailabilityFixture, CONTRACT, FAULTS, MODEL, PHASES, SESSION,
    agreement, bytes_twin, event_v2_inputs, file_fault,
)

MIRRORS = {"response_mirror": b"\0\0\0\0", "tokens_mirror": b"{}\n"}


@contextmanager
def synthetic_mirror_fault(path, fixture_bytes, fault):
    """Give the readers fabricated bytes while keeping mirror content off disk."""
    assert not path.exists()
    if fault == "absent":
        yield
        return
    data = {"zero": b"", "half": fixture_bytes[:len(fixture_bytes) // 2], "garbage": b"\xffbroken input\n"}[fault]
    original = Path.open

    def open_fixture(pathname, mode="r", *args, **kwargs):
        if pathname == path and mode.startswith("r"):
            return io.BytesIO(data) if "b" in mode else io.StringIO(data.decode("utf-8"))
        return original(pathname, mode, *args, **kwargs)

    path.touch()
    try:
        with patch.object(Path, "open", open_fixture):
            yield
    finally:
        path.unlink()


def environment_inputs(fixture):
    config_path, metadata_path = (fixture.bundle / name for name in ("config.json", "metadata.json"))
    config, metadata = agreement.load(config_path), agreement.load(metadata_path)
    config["hardware_target"]["telemetry_backend"] = "powermetrics"
    metadata.setdefault("adapters", {}).setdefault("telemetry", {})["name"] = "powermetrics"
    metadata.update(environment_admission={"attempts": [{"attempt": 1, "start_s": 0, "end_s": 1,
                                                         "baseline": {"duration_s": 1}}]},
                    campaign_policy={"sha256": "0" * 64})
    agreement._write(config_path, config)
    agreement._write(metadata_path, metadata)
    paths = {"rich_idle": fixture.bundle / "rich_telemetry_idle.jsonl",
             "raw_idle": fixture.bundle / "raw/powermetrics_idle.plist",
             "environment_policy": fixture.root / "configs/campaign_policies/policy.json"}
    paths["rich_idle"].write_bytes(b'{"timestamp_s":1,"elapsed_ns":1000000000}\n')
    paths["raw_idle"].parent.mkdir(exist_ok=True)
    processor = {name: 1000 for name in ("cpu_power", "gpu_power", "ane_power", "cpu_energy", "gpu_energy", "ane_energy")}
    paths["raw_idle"].write_bytes(plistlib.dumps({"timestamp": "2026-11-01T10:00:00Z", "elapsed_ns": 1_000_000_000,
                                                 "processor": processor, "thermal_pressure": "nominal"}))
    paths["environment_policy"].parent.mkdir(parents=True)
    paths["environment_policy"].write_bytes(b'{"schema_version":"synthetic availability fixture"}\n')
    return paths


def compare_member(fixture, export, keys, roster):
    """Evaluate the same planned member before the estimator's 50-run minimum."""
    plan = fixture.archive / "derived/roster.json"
    original = plan.read_bytes()
    agreement._write(plan, roster)
    try:
        session, = fixture.manifest["sessions"]
        primary, = agreement.ba.archive_records(fixture.archive, fixture.manifest, session, stage="fit",
                                                 export_path=export, key_dir=keys)
        manifest = bytes_twin.read_manifest(fixture.manifest_path)
        archive = bytes_twin.load_archive(fixture.archive)
        science = [row for row in bytes_twin.read_export(export) if row["run_id"] == fixture.member]
        result = bytes_twin.analyse(science, manifest, [archive], stage="1", key_dir=keys,
                                    listed={SESSION: session}, synthetic=True)
        block = result["cells"][bytes_twin.canon(MODEL)]["pass1"]
        twin_admitted = fixture.member in block["dc_join_status"]
        pairs = [(primary["status"] == "succeeded", twin_admitted)]
        pairs.extend((primary["flags"], block["boundaries"][boundary]["gross"]["flags"])
                     for boundary in bytes_twin.BOUNDARIES)
        return pairs
    finally:
        plan.write_bytes(original)


class ConditionalAvailabilityTests(unittest.TestCase):
    def check_matrix(self, timing):
        cases = comparisons = 0
        with tempfile.TemporaryDirectory(prefix=f"bytes-conditional-faults-{timing}-") as directory:
            root = Path(directory)
            fixture = AvailabilityFixture(root / "base", timing)
            # Conditions on these inputs are checked at the member gate. Keeping
            # the meter absent on both sides makes any derived flag observable.
            fixture.stream.unlink()
            roster = agreement.load(fixture.archive / "derived/roster.json")
            roster["members"] = [row for row in roster["members"] if row["run_id"] == fixture.member]
            acceptance = fixture.root / "registration/acceptance.json"
            acceptance.parent.mkdir(exist_ok=True)
            agreement._write(acceptance, document())
            suite = fixture.bundle / "suite_manifest.json"
            suite.write_bytes(b'{"schema_version":"suite_manifest.v2","items":[]}\n')
            config, metadata = (fixture.bundle / name for name in ("config.json", "metadata.json"))
            original_config, original_metadata = config.read_bytes(), metadata.read_bytes()

            def check(paths):
                nonlocal cases, comparisons
                for row_id, path in paths.items():
                    contract = CONTRACT[row_id]
                    self.assertEqual(tuple(contract["faults"]), FAULTS)
                    for fault in contract["faults"]:
                        for phase in PHASES:
                            with self.subTest(timing=timing, file=row_id, fault=fault, phase=phase):
                                scratch = root / f"{row_id}-{fault}-{phase}"
                                scratch.mkdir()
                                context = (synthetic_mirror_fault(path, MIRRORS[row_id], fault)
                                           if row_id in MIRRORS else file_fault(path, fault))
                                with context:
                                    if phase == "before_export":
                                        export, keys = fixture.export_again(scratch / "export", scratch / "private",
                                                                             read_evidence=row_id == "acceptance_registration")
                                    else:
                                        export, keys = fixture.export, fixture.keys
                                    checks = compare_member(fixture, export, keys, roster)
                                expected = not (fault == "garbage" and contract.get("synthetic_invalid_utf8_drops"))
                                self.assertEqual(checks[0], (expected, expected))
                                for primary, twin in checks[1:]:
                                    self.assertEqual(primary, twin)
                                cases += 1
                                comparisons += len(checks)

            initial = {"acceptance_registration": acceptance, "suite_manifest": suite}
            check(initial)
            suite.unlink()
            environment = environment_inputs(fixture)
            with patch.object(environment_admission, "REGISTERED_POLICY_DIR", environment["environment_policy"].parent):
                check(environment)
            config.write_bytes(original_config)
            metadata.write_bytes(original_metadata)
            v2 = event_v2_inputs(fixture)
            check(v2)
            self.assertEqual(set(initial) | set(environment) | set(v2), {
                key for key, row in CONTRACT.items() if row["scope"] == "observed_branch"
                and key not in {"compressed_member", "restore_bundle_inventory", "authenticated_plan_trees"}})
        print(f"\nBYTES {timing} conditional matrix: {cases} cases, {comparisons} exact comparisons, zero disagreements", flush=True)

    def test_mock_timing_conditional_file_faults(self):
        self.check_matrix("mock")

    def test_native_timing_conditional_file_faults(self):
        self.check_matrix("native")
