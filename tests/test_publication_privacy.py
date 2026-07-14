import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from joulewise import publication_privacy


SECRET_VALUES = (
    "PRIVATE_PROMPT_7f6c",
    "PRIVATE_RESPONSE_4a21",
    "/Users/example/private/model",
    "/srv/private/worker/state",
    "private-user-91",
    "private-host-28",
    "API_TOKEN_PRIVATE_83",
    "cleanup failed at /srv/private/worker/state",
)


IDLE_MEAN_UNCERTAINTY = {
    "status": "estimated",
    "method": "newey_west_bartlett_10s_iid_floor_v1",
    "source_artifact": "raw/powermetrics_idle.plist",
    "source_sha256": "2" * 64,
    "raw_sample_count": 100,
    "median_sample_interval_s": 0.1,
    "cadence_p95_p05_ratio": 1.02,
    "bandwidth_s": 10.0,
    "lag_count": 100,
    "sample_variance_w2": 0.4,
    "iid_variance_of_mean_w2": 0.004,
    "hac_variance_of_mean_w2": 0.006,
    "governed_variance_of_mean_w2": 0.006,
    "effective_sample_size": 66.66666666666667,
    "correlation_scope": "independent_run",
    "reason_codes": [],
}


def _write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _file_hashes(root: Path) -> dict[str, str]:
    return {
        path.relative_to(root).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in root.rglob("*")
        if path.is_file() and not path.is_symlink()
    }


class PublicationPrivacyTests(unittest.TestCase):
    def setUp(self) -> None:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.tmp = Path(tmp.name)

    def test_canonical_tree_identity_algorithm_is_versioned_and_stable(self) -> None:
        entries = [
            {
                "path": "a.txt",
                "sha256": "b6a98d9ce9a2d9149288fa3df42d377c3e42737afdcdaf714e33c0a100b51060",
                "size_bytes": 6,
            },
            {
                "path": "nested/b.bin",
                "sha256": "06eb7d6a69ee19e5fbdf749018d3d2abfa04bcbd1365db312eb86dc7169389b8",
                "size_bytes": 2,
            },
        ]
        self.assertEqual(
            publication_privacy.tree_identity_descriptor(),
            {
                "algorithm": "sha256",
                "version": "joulewise.bundle-tree.nul-v1",
            },
        )
        self.assertEqual(
            publication_privacy.tree_sha256(entries),
            "001e3ed0f152ef0dd6443cf3b6f5fce7fb1029582fc588afaee242de78824317",
        )

    def make_secret_bundle(self, name: str = "private-bundle") -> Path:
        bundle = self.tmp / name
        bundle.mkdir()
        _write_json(
            bundle / "config.json",
            {
                "schema_version": "0.1",
                "run_id": "private-user-91__private-host-28",
                "model": {
                    "name": "synthetic-model",
                    "family": "synthetic",
                    "source": "/Users/example/private/model",
                    "revision": "fixture-only",
                    "weight_format": "synthetic",
                    "context_window": 128,
                },
                "quantization": {"name": "none", "bits": None, "group_size": None},
                "hardware_target": {
                    "id": "private-host-28",
                    "transport": "ssh",
                    "runtime_backend": "mock",
                    "telemetry_backend": "mock",
                    "host": "private-host-28",
                    "device_kind": "synthetic",
                    "notes": "private-user-91 owns this fixture-only target",
                },
                "workload_profile": {
                    "name": "privacy-fixture",
                    "prompt_tokens": 4,
                    "output_tokens": 2,
                    "prompt_text": "PRIVATE_PROMPT_7f6c",
                    "dataset_ref": "/Users/example/private/dataset.json",
                    "suite_manifest_ref": None,
                    "suite_manifest_sha256": None,
                    "generator_sidecar_ref": "/Users/example/private/generator.json",
                    "repetitions": 1,
                    "warmup_runs": 0,
                },
                "interconnect": {
                    "name": "synthetic-link",
                    "link_speed_mbps": 1000,
                    "notes": "private lab path",
                },
                "sampling": {"power_hz": 2.0, "idle_seconds": 1.0, "warmup_seconds": 0.0},
                "run_metadata": {
                    "project": "private project",
                    "operator": "private-user-91",
                    "ambient_temp_c": 22.0,
                    "notes": "private-host-28",
                    "tags": ["API_TOKEN_PRIVATE_83"],
                },
            },
        )
        _write_json(
            bundle / "metadata.json",
            {
                "platform": "private-host-28.local",
                "machine": "private-machine-id",
                "python_version": "3.13.1",
                "joulewise_version": "fixture-only",
                "schema_version": "0.1",
                "config_sha256": "0" * 64,
                "run_id": "private-user-91__private-host-28",
                "git_commit": "1" * 40,
                "clock": {"kind": "synthetic"},
                "config_warnings": [],
                "model": {"source": "/Users/example/private/model"},
                "quantization": {"name": "none"},
                "device": {"path": "/dev/private-device"},
                "connection": {"transport": "ssh", "host": "private-host-28", "user": "private-user-91"},
                "environment": {
                    "HOME": "/Users/example",
                    "API_TOKEN": "API_TOKEN_PRIVATE_83",
                    "hostname": "private-host-28",
                },
                "adapters": {
                    "runtime": {
                        "name": "remote-worker",
                        "worker_metadata": {
                            "worker_environment": {"API_TOKEN": "API_TOKEN_PRIVATE_83"},
                            "state_dir": "/srv/private/worker/state",
                            "server_log_tail": "PRIVATE_RESPONSE_4a21",
                        },
                        "cleanup_metadata": {
                            "message": "cleanup failed at /srv/private/worker/state"
                        },
                    }
                },
                "idle_baseline": {"power_w_mean": 1.0},
                "thermal_pre": {"temperature_c": 40.0},
                "thermal_post": {"temperature_c": 41.0},
                "uncertainty_evidence": {"raw_path": "/srv/private/raw.plist"},
                "clock_anchor_bound_s": 0.1,
                "marker_to_first_sample_phase_bound_s": 0.2,
                "marker_to_last_sample_phase_bound_s": 0.2,
                "idle_drift_bound_w": 0.3,
                "workload_observed": {"token_count": 6},
                "workload_provenance": {
                    "prompt": "PRIVATE_PROMPT_7f6c",
                    "response": "PRIVATE_RESPONSE_4a21",
                },
                "suite": {"source": "/Users/example/private/suite.json"},
                "extra": {
                    "node_cleanup": [
                        {
                            "path": "/srv/private/worker/state",
                            "ok": False,
                            "message": "cleanup failed at /srv/private/worker/state",
                        }
                    ]
                },
            },
        )
        event = {
            "timestamp_s": 1.0,
            "event_type": "failure",
            "phase": "cleanup",
            "message": "cleanup failed at /srv/private/worker/state",
            "metadata": {
                "prompt": "PRIVATE_PROMPT_7f6c",
                "response": "PRIVATE_RESPONSE_4a21",
                "user": "private-user-91",
                "host": "private-host-28",
                "environment": {"API_TOKEN": "API_TOKEN_PRIVATE_83"},
                "worker_path": "/srv/private/worker/state",
            },
        }
        (bundle / "events.jsonl").write_text(json.dumps(event) + "\n", encoding="utf-8")
        (bundle / "power_trace.csv").write_text(
            "timestamp_s,power_w,source,rail\n1.0,10.0,mock,mock\n",
            encoding="utf-8",
        )
        _write_json(
            bundle / "summary_metrics.json",
            {
                "status": "succeeded",
                "energy_request_j": 10.0,
                "inter_token_throughput_tokens_s": 20.0,
                "idle_mean_uncertainty": IDLE_MEAN_UNCERTAINTY,
                "window_evidence_precheck": {
                    "private_path": "/srv/private/worker/state",
                    "reason_codes": ["fixture-only-open-subtree"],
                },
                "measurement_quality": {
                    "requested_sampling_hz": 2.0,
                    "remote_cleanup_failed": ["/srv/private/worker/state"],
                    "runtime_cleanup_ok": False,
                },
                "suite_metrics": None,
                "failure_reason": None,
                "failure_message": "cleanup failed at /srv/private/worker/state",
            },
        )
        (bundle / "outputs").mkdir()
        (bundle / "outputs" / "response.txt").write_text("PRIVATE_RESPONSE_4a21\n")
        (bundle / "outputs" / "tokens.jsonl").write_text(
            json.dumps({"token_id": 99, "response": "PRIVATE_RESPONSE_4a21"}) + "\n"
        )
        (bundle / "logs").mkdir()
        (bundle / "logs" / "controller.log").write_text("API_TOKEN_PRIVATE_83\n")
        (bundle / "logs" / "runtime.log").write_text("PRIVATE_PROMPT_7f6c\n")
        (bundle / "logs" / "telemetry.log").write_text("private-host-28\n")
        (bundle / "logs" / "task-runtime-cleanup-004_worker.log").write_text(
            "cleanup failed at /srv/private/worker/state\n"
        )
        (bundle / "raw").mkdir()
        _write_json(bundle / "raw" / "mock_samples.json", [{"source": "private-host-28"}])
        return bundle

    def test_secret_bearing_bundle_is_transformed_without_mutating_source(self) -> None:
        source = self.make_secret_bundle()
        source_hashes = _file_hashes(source)
        destination = self.tmp / "public"

        audit = publication_privacy.audit_private_bundle(source)
        transformation = publication_privacy.transform_public_bundle(source, destination)

        self.assertEqual(source_hashes, _file_hashes(source))
        self.assertEqual(transformation["source_bundle_sha256"], audit.source_bundle_sha256)
        self.assertEqual(
            transformation["bundle_tree_identity"],
            publication_privacy.tree_identity_descriptor(),
        )
        self.assertNotEqual(
            transformation["source_bundle_sha256"], transformation["output_bundle_sha256"]
        )
        self.assertIs(transformation["byte_identical_to_private_source"], False)
        self.assertEqual(
            publication_privacy.verify_public_bundle(
                destination, transformation["public_bundle_id"]
            ),
            [],
        )
        public_bytes = b"\n".join(
            path.read_bytes() for path in destination.rglob("*") if path.is_file()
        )
        for secret in SECRET_VALUES:
            self.assertNotIn(secret.encode(), public_bytes)
        self.assertFalse((destination / "outputs").exists())
        self.assertFalse((destination / "logs").exists())
        self.assertFalse((destination / "raw").exists())
        summary = json.loads((destination / "summary_metrics.json").read_text())
        quality = summary["measurement_quality"]
        self.assertEqual(
            quality["remote_cleanup_failed"],
            [publication_privacy.REDACTED_CLEANUP_PATH],
        )
        self.assertIs(quality["runtime_cleanup_ok"], False)
        self.assertEqual(summary["inter_token_throughput_tokens_s"], 20.0)
        self.assertEqual(summary["idle_mean_uncertainty"], IDLE_MEAN_UNCERTAINTY)
        self.assertIsNone(summary["window_evidence_precheck"])

    def test_unknown_fields_and_paths_fail_closed(self) -> None:
        mutations = {
            "config field": lambda bundle: self._add_json_field(
                bundle / "config.json", "unreviewed_top_level"
            ),
            "metadata field": lambda bundle: self._add_json_field(
                bundle / "metadata.json", "unreviewed_top_level"
            ),
            "summary field": lambda bundle: self._add_json_field(
                bundle / "summary_metrics.json", "unreviewed_top_level"
            ),
            "idle uncertainty field": self._add_idle_uncertainty_field,
            "idle uncertainty reason": self._add_idle_uncertainty_reason,
            "measurement quality field": self._add_quality_field,
            "event field": self._add_event_field,
            "power source value": self._set_unreviewed_power_source,
            "artifact path": lambda bundle: (bundle / "private-extra.txt").write_text(
                "fixture-only", encoding="utf-8"
            ),
        }
        for index, (label, mutate) in enumerate(mutations.items()):
            with self.subTest(label=label):
                bundle = self.make_secret_bundle(f"mutation-{index}")
                mutate(bundle)
                with self.assertRaisesRegex(
                    publication_privacy.PrivacyAuditError,
                    "unclassified",
                ):
                    publication_privacy.audit_private_bundle(bundle)

    def test_source_mutation_during_transform_refuses_and_removes_output(self) -> None:
        source = self.make_secret_bundle("concurrent-mutation")
        destination = self.tmp / "refused-public"
        original = publication_privacy._write_transformed_file
        mutated = False

        def mutate_source_once(*args, **kwargs):
            nonlocal mutated
            if not mutated:
                mutated = True
                with (source / "logs" / "controller.log").open("a") as handle:
                    handle.write("late fixture-only mutation\n")
            return original(*args, **kwargs)

        with patch.object(
            publication_privacy,
            "_write_transformed_file",
            side_effect=mutate_source_once,
        ):
            with self.assertRaisesRegex(
                publication_privacy.PrivacyAuditError,
                "changed during transformation",
            ):
                publication_privacy.transform_public_bundle(source, destination)
        self.assertFalse(destination.exists())

    @staticmethod
    def _add_json_field(path: Path, key: str) -> None:
        value = json.loads(path.read_text())
        value[key] = "fixture-only"
        _write_json(path, value)

    @staticmethod
    def _add_quality_field(bundle: Path) -> None:
        path = bundle / "summary_metrics.json"
        value = json.loads(path.read_text())
        value["measurement_quality"]["unreviewed_quality"] = 1
        _write_json(path, value)

    @staticmethod
    def _add_idle_uncertainty_field(bundle: Path) -> None:
        path = bundle / "summary_metrics.json"
        value = json.loads(path.read_text())
        value["idle_mean_uncertainty"]["unreviewed_nested"] = "fixture-only"
        _write_json(path, value)

    @staticmethod
    def _add_idle_uncertainty_reason(bundle: Path) -> None:
        path = bundle / "summary_metrics.json"
        value = json.loads(path.read_text())
        value["idle_mean_uncertainty"]["reason_codes"] = ["unreviewed_reason"]
        _write_json(path, value)

    @staticmethod
    def _add_event_field(bundle: Path) -> None:
        path = bundle / "events.jsonl"
        value = json.loads(path.read_text())
        value["unreviewed_event"] = "fixture-only"
        path.write_text(json.dumps(value) + "\n", encoding="utf-8")

    @staticmethod
    def _set_unreviewed_power_source(bundle: Path) -> None:
        path = bundle / "power_trace.csv"
        path.write_text(
            path.read_text(encoding="utf-8").replace(",mock,mock", ",private-host-28,mock"),
            encoding="utf-8",
        )


if __name__ == "__main__":
    unittest.main()
