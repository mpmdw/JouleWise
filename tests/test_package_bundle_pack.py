import contextlib
import hashlib
import io
import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from joulewise.adapters.powermetrics import RAW_SAMPLES_NAME
from joulewise.clock import FakeClock
from joulewise.cli import main as joulewise_main
from joulewise.cli import validate_bundle
from joulewise.controller import run_benchmark
from joulewise.publication_privacy import verify_public_bundle
from joulewise.schemas import BenchmarkConfig, RunStatus
from joulewise.suite import suite_manifest_sha256
from scripts import package_bundle_pack


ROOT = Path(__file__).resolve().parent.parent
EXAMPLE_CONFIG = ROOT / "configs" / "examples" / "mock_local.json"
EXAMPLE_SUITE_CONFIG = ROOT / "configs" / "examples" / "mock_suite_local.json"
MOCK_SUITE_MANIFEST = ROOT / "configs" / "suite_manifests" / "mock_suite_manifest.json"
POWERMETRICS_FIXTURE = ROOT / "tests" / "fixtures" / "powermetrics_sample.plist"


def _run_joulewise(argv: list[str]) -> tuple[int, str, str]:
    stdout = io.StringIO()
    stderr = io.StringIO()
    with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
        code = joulewise_main(argv)
    return code, stdout.getvalue(), stderr.getvalue()


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _run_packager(argv: list[str]) -> tuple[int, str, str]:
    stdout = io.StringIO()
    stderr = io.StringIO()
    with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
        code = package_bundle_pack.main(argv)
    return code, stdout.getvalue(), stderr.getvalue()


def _completed(command: list[str]) -> subprocess.CompletedProcess:
    return subprocess.CompletedProcess(command, 0, stdout=b"", stderr=b"")


class BundlePackTests(unittest.TestCase):
    def setUp(self) -> None:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.tmp = Path(tmp.name)
        self.runs_dir = self.tmp / "runs"

    def write_config(self, run_id: str) -> Path:
        data = json.loads(EXAMPLE_CONFIG.read_text(encoding="utf-8"))
        data["run_id"] = run_id
        path = self.tmp / f"{run_id}.json"
        path.write_text(json.dumps(data), encoding="utf-8")
        return path

    def write_suite_config(self, run_id: str) -> Path:
        data = json.loads(EXAMPLE_SUITE_CONFIG.read_text(encoding="utf-8"))
        data["run_id"] = run_id
        data["workload_profile"]["suite_manifest_ref"] = str(MOCK_SUITE_MANIFEST)
        path = self.tmp / f"{run_id}.json"
        path.write_text(json.dumps(data), encoding="utf-8")
        return path

    def make_bundle(self, run_id: str) -> Path:
        code, stdout, stderr = _run_joulewise(
            ["run", str(self.write_config(run_id)), "--runs-dir", str(self.runs_dir)]
        )
        self.assertEqual(code, 0, stderr)
        line = stdout.strip()
        self.assertTrue(line.startswith("bundle: "), line)
        return Path(line[len("bundle: ") :].split(" ", 1)[0])

    def make_suite_bundle(self, run_id: str) -> Path:
        code, stdout, stderr = _run_joulewise(
            ["run", str(self.write_suite_config(run_id)), "--runs-dir", str(self.runs_dir)]
        )
        self.assertEqual(code, 0, stderr)
        line = stdout.strip()
        self.assertTrue(line.startswith("bundle: "), line)
        return Path(line[len("bundle: ") :].split(" ", 1)[0])

    def make_powermetrics_bundle(self, run_id: str) -> Path:
        fixture = POWERMETRICS_FIXTURE.read_bytes()
        config_data = json.loads(EXAMPLE_CONFIG.read_text(encoding="utf-8"))
        config_data["run_id"] = run_id
        config_data["hardware_target"]["telemetry_backend"] = "powermetrics"
        config_data["workload_profile"]["output_tokens"] = 300
        config_data["sampling"] = {"power_hz": 2.0, "idle_seconds": 5.0}
        config = BenchmarkConfig.from_mapping(config_data)

        def fake_run(command, **kwargs):
            if "-o" in command:
                Path(command[command.index("-o") + 1]).write_bytes(fixture)
            return _completed(command)

        class FakePopen:
            def __init__(self, command, **kwargs):
                self.path = Path(command[command.index("-o") + 1])
                self.path.write_bytes(fixture)
                self.returncode = None

            def poll(self):
                return self.returncode

            def terminate(self):
                self.returncode = 0

            def kill(self):
                self.returncode = -9

            def communicate(self, timeout=None):
                self.returncode = 0
                return b"", b""

        with (
            patch("joulewise.adapters.powermetrics.subprocess.run", side_effect=fake_run),
            patch("joulewise.adapters.powermetrics.subprocess.Popen", FakePopen),
        ):
            bundle, summary = run_benchmark(
                config,
                self.runs_dir,
                FakeClock(start=1_783_394_100.0),
            )
        self.assertEqual(summary.status, RunStatus.SUCCEEDED)
        self.assertEqual(validate_bundle(bundle, strict=True), [])
        return bundle

    def test_pack_mock_bundle_manifest_hashes_privacy_and_source_immutability(self) -> None:
        source_bundle = self.make_bundle("pack-mock")
        pack_dir = self.tmp / "pack"
        source_hashes_before = {
            path.relative_to(source_bundle).as_posix(): _sha256(path)
            for path in source_bundle.rglob("*")
            if path.is_file() and not path.is_symlink()
        }

        manifest = package_bundle_pack.package_bundles([source_bundle], pack_dir)

        self.assertEqual(manifest["schema"], package_bundle_pack.PACK_SCHEMA)
        self.assertEqual(manifest["bundle_count"], 1)
        entry = manifest["bundles"][0]
        self.assertTrue(entry["bundle_id"].startswith("public-"))
        self.assertNotIn("pack-mock", json.dumps(manifest))
        self.assertEqual(manifest["schema"], "joulewise.public_bundle_pack.v2")
        self.assertIs(manifest["byte_identical_to_private_sources"], False)
        self.assertNotEqual(manifest["project_commit"], "unknown")
        self.assertIn(
            manifest["project_tree_state"],
            {
                package_bundle_pack.TREE_STATE_CLEAN,
                package_bundle_pack.TREE_STATE_DIRTY,
                package_bundle_pack.TREE_STATE_UNKNOWN,
            },
        )
        self.assertEqual(
            entry["source_config_sha256"], _sha256(source_bundle / "config.json")
        )
        self.assertNotEqual(entry["config_sha256"], entry["source_config_sha256"])
        self.assertIsNone(entry["effective_manifest_sha256"])
        self.assertEqual(entry["summary_status"], "succeeded")

        packed_bundle = pack_dir / "bundles" / entry["bundle_id"]
        self.assertEqual(verify_public_bundle(packed_bundle, entry["bundle_id"]), [])
        by_path = {item["path"]: item for item in entry["files"]}
        self.assertIn("config.json", by_path)
        self.assertIn("summary_metrics.json", by_path)
        self.assertIn("power_trace.csv", by_path)
        self.assertNotIn("outputs/response.txt", by_path)
        self.assertNotIn("outputs/tokens.jsonl", by_path)
        self.assertNotIn("logs/controller.log", by_path)
        self.assertNotIn("raw/mock_samples.json", by_path)
        for rel, item in by_path.items():
            self.assertEqual(item["sha256"], _sha256(packed_bundle / rel), rel)
            self.assertEqual(item["size_bytes"], (packed_bundle / rel).stat().st_size)
        for rel, digest in source_hashes_before.items():
            self.assertEqual(digest, _sha256(source_bundle / rel), rel)

        disk_manifest = json.loads((pack_dir / "MANIFEST.json").read_text(encoding="utf-8"))
        self.assertEqual(disk_manifest, manifest)
        transformation = json.loads(
            (pack_dir / package_bundle_pack.TRANSFORMATION_MANIFEST_NAME).read_text(
                encoding="utf-8"
            )
        )
        transform_entry = transformation["bundles"][0]
        self.assertEqual(transform_entry["source_bundle_sha256"], entry["source_bundle_sha256"])
        self.assertEqual(transform_entry["output_bundle_sha256"], entry["public_bundle_sha256"])
        self.assertIs(transform_entry["byte_identical_to_private_source"], False)
        self.assertTrue(
            all("source_path" not in item for item in transform_entry["files"])
        )
        self.assertEqual(manifest["readme_sha256"], _sha256(pack_dir / "README.md"))
        readme = (pack_dir / "README.md").read_text(encoding="utf-8")
        self.assertIn("privacy-transformed", readme)
        self.assertIn("TRANSFORMATION_MANIFEST.json", readme)
        self.assertIn("not strict-valid", readme)
        self.assertIn("MIT License", readme)
        if manifest["project_tree_state"] == package_bundle_pack.TREE_STATE_CLEAN:
            self.assertIn(f"git checkout {manifest['project_commit']}", readme)
        else:
            self.assertIn("exact source tree", readme)
            self.assertNotIn("git checkout unknown", readme)
        self.assertEqual(package_bundle_pack.verify_pack(pack_dir), [])

    def test_non_strict_bundle_is_refused_before_copying(self) -> None:
        source_bundle = self.make_bundle("pack-refuse")
        summary_path = source_bundle / "summary_metrics.json"
        summary = json.loads(summary_path.read_text(encoding="utf-8"))
        summary["energy_request_j"] = summary["energy_request_j"] + 1.0
        summary_path.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")

        self.assertNotEqual(validate_bundle(source_bundle, strict=True), [])
        pack_dir = self.tmp / "pack-refused"
        with self.assertRaises(package_bundle_pack.BundlePackError):
            package_bundle_pack.package_bundles([source_bundle], pack_dir)
        self.assertFalse(pack_dir.exists())

    def test_verify_pack_catches_tampered_packed_file(self) -> None:
        source_bundle = self.make_bundle("pack-tamper")
        pack_dir = self.tmp / "pack"
        manifest = package_bundle_pack.package_bundles([source_bundle], pack_dir)
        public_id = manifest["bundles"][0]["bundle_id"]

        config_path = pack_dir / "bundles" / public_id / "config.json"
        config = json.loads(config_path.read_text(encoding="utf-8"))
        config["run_id"] = "pack-tampered"
        config_path.write_text(json.dumps(config, indent=2, sort_keys=True) + "\n")

        problems = package_bundle_pack.verify_pack(pack_dir)

        self.assertTrue(
            any("hash mismatch for config.json" in problem for problem in problems),
            problems,
        )

    def test_verify_pack_catches_tamper_even_if_pack_manifest_is_rehashed(self) -> None:
        source_bundle = self.make_bundle("pack-transform-tamper")
        pack_dir = self.tmp / "transform-tamper-pack"
        built = package_bundle_pack.package_bundles([source_bundle], pack_dir)
        public_id = built["bundles"][0]["bundle_id"]
        trace_path = pack_dir / "bundles" / public_id / "power_trace.csv"
        trace_path.write_text(
            trace_path.read_text(encoding="utf-8").replace(",7.5,", ",99.0,", 1),
            encoding="utf-8",
        )

        manifest_path = pack_dir / package_bundle_pack.MANIFEST_NAME
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        entry = manifest["bundles"][0]
        trace_entry = next(item for item in entry["files"] if item["path"] == "power_trace.csv")
        trace_entry["sha256"] = _sha256(trace_path)
        trace_entry["size_bytes"] = trace_path.stat().st_size
        entry["public_bundle_sha256"] = package_bundle_pack.tree_sha256(entry["files"])
        readme = package_bundle_pack._readme(package_bundle_pack._readme_manifest(manifest))
        (pack_dir / package_bundle_pack.README_NAME).write_text(readme, encoding="utf-8")
        manifest["readme_sha256"] = _sha256(pack_dir / package_bundle_pack.README_NAME)
        manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")

        problems = package_bundle_pack.verify_pack(pack_dir)

        self.assertTrue(
            any(
                "transformation output hash mismatch for power_trace.csv" in problem
                or "public bundle hash differs across manifests" in problem
                for problem in problems
            ),
            problems,
        )

    def test_verify_pack_catches_readme_that_does_not_match_manifest(self) -> None:
        first = self.make_bundle("pack-readme-a")
        second = self.make_bundle("pack-readme-b")
        pack_dir = self.tmp / "pack-readme"
        built = package_bundle_pack.package_bundles([first, second], pack_dir)

        manifest_path = pack_dir / "MANIFEST.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["bundles"] = manifest["bundles"][:1]
        manifest["bundle_count"] = 1
        manifest["readme_sha256"] = _sha256(pack_dir / "README.md")
        manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
        shutil.rmtree(pack_dir / "bundles" / built["bundles"][1]["bundle_id"])

        problems = package_bundle_pack.verify_pack(pack_dir)

        self.assertTrue(
            any("README.md does not match manifest-derived contents" in problem for problem in problems),
            problems,
        )

    def test_verify_pack_accepts_readme_with_non_default_bundles_dir(self) -> None:
        source_bundle = self.make_bundle("pack-custom-bundles-dir")
        pack_dir = self.tmp / "pack-custom-bundles-dir"
        built = package_bundle_pack.package_bundles([source_bundle], pack_dir)
        public_id = built["bundles"][0]["bundle_id"]

        custom_bundles_dir = "published-bundles"
        shutil.move(str(pack_dir / "bundles"), str(pack_dir / custom_bundles_dir))
        manifest_path = pack_dir / "MANIFEST.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["bundles_dir"] = custom_bundles_dir
        readme = package_bundle_pack._readme(package_bundle_pack._readme_manifest(manifest))
        (pack_dir / "README.md").write_text(readme, encoding="utf-8")
        manifest["readme_sha256"] = _sha256(pack_dir / "README.md")
        manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")

        self.assertIn(f"published-bundles/{public_id}", readme)
        self.assertNotIn(f"`bundles/{public_id}`", readme)
        self.assertEqual(package_bundle_pack.verify_pack(pack_dir), [])

    def test_existing_output_dir_is_refused_and_preserved(self) -> None:
        source_bundle = self.make_bundle("pack-existing-output")
        pack_dir = self.tmp / "preexisting"
        pack_dir.mkdir()
        sentinel = pack_dir / "sentinel.txt"
        sentinel.write_text("keep me", encoding="utf-8")

        with self.assertRaises(package_bundle_pack.BundlePackError):
            package_bundle_pack.package_bundles([source_bundle], pack_dir)

        self.assertEqual(sentinel.read_text(encoding="utf-8"), "keep me")
        code, stdout, stderr = _run_packager(
            ["--output", str(pack_dir), str(source_bundle)]
        )
        self.assertEqual(code, 2)
        self.assertEqual(stdout, "")
        self.assertIn("error:", stderr)
        self.assertEqual(sentinel.read_text(encoding="utf-8"), "keep me")

    def test_output_dir_claim_race_is_refused_and_preserved(self) -> None:
        source_bundle = self.make_bundle("pack-output-race")
        pack_dir = self.tmp / "race-pack"
        sentinel = pack_dir / "sentinel.txt"

        def create_competing_output_dir() -> dict[str, str]:
            pack_dir.mkdir()
            sentinel.write_text("raced claim", encoding="utf-8")
            return {
                "project_commit": "race-test",
                "project_tree_state": package_bundle_pack.TREE_STATE_CLEAN,
            }

        with patch.object(
            package_bundle_pack,
            "_git_provenance",
            side_effect=create_competing_output_dir,
        ):
            with self.assertRaisesRegex(
                package_bundle_pack.BundlePackError,
                "output directory already exists",
            ):
                package_bundle_pack.package_bundles([source_bundle], pack_dir)

        self.assertEqual(sentinel.read_text(encoding="utf-8"), "raced claim")

    def test_suite_bundle_records_effective_manifest_sha256(self) -> None:
        source_bundle = self.make_suite_bundle("pack-suite")
        pack_dir = self.tmp / "suite-pack"

        manifest = package_bundle_pack.package_bundles([source_bundle], pack_dir)

        raw_suite_manifest = json.loads(
            (source_bundle / "suite_manifest.json").read_text(encoding="utf-8")
        )
        self.assertEqual(
            manifest["bundles"][0]["effective_manifest_sha256"],
            suite_manifest_sha256(raw_suite_manifest),
        )
        self.assertEqual(package_bundle_pack.verify_pack(pack_dir), [])

    def test_powermetrics_raw_plist_is_omitted_but_source_hash_is_recorded(self) -> None:
        source_bundle = self.make_powermetrics_bundle("pack-powermetrics")
        pack_dir = self.tmp / "powermetrics-pack"

        manifest = package_bundle_pack.package_bundles([source_bundle], pack_dir)

        rel = f"raw/{RAW_SAMPLES_NAME}"
        by_path = {item["path"]: item for item in manifest["bundles"][0]["files"]}
        self.assertNotIn(rel, by_path)
        transformation = json.loads(
            (pack_dir / package_bundle_pack.TRANSFORMATION_MANIFEST_NAME).read_text()
        )
        by_source_path = {
            item["path"]: item for item in transformation["bundles"][0]["files"]
        }
        self.assertEqual(by_source_path[rel]["operation"], "omit")
        self.assertEqual(by_source_path[rel]["source_sha256"], _sha256(source_bundle / rel))
        self.assertIsNone(by_source_path[rel]["output_sha256"])
        self.assertEqual(package_bundle_pack.verify_pack(pack_dir), [])

    def test_multi_bundle_duplicate_and_later_invalid_refusals(self) -> None:
        first = self.make_bundle("pack-multi-a")
        second = self.make_bundle("pack-multi-b")
        pack_dir = self.tmp / "multi-pack"

        manifest = package_bundle_pack.package_bundles([first, second], pack_dir)

        self.assertEqual(manifest["bundle_count"], 2)
        public_ids = [entry["bundle_id"] for entry in manifest["bundles"]]
        self.assertEqual(len(set(public_ids)), 2)
        self.assertTrue(all(value.startswith("public-") for value in public_ids))
        readme = (pack_dir / "README.md").read_text(encoding="utf-8")
        self.assertTrue(all(f"bundles/{value}" in readme for value in public_ids))
        self.assertNotIn("pack-multi-a", readme)
        self.assertNotIn("pack-multi-b", readme)
        self.assertEqual(package_bundle_pack.verify_pack(pack_dir), [])

        duplicate = self.tmp / "duplicate-source"
        shutil.copytree(second, duplicate)
        metadata_path = duplicate / "metadata.json"
        metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
        metadata["run_id"] = "pack-multi-a"
        metadata_path.write_text(json.dumps(metadata, indent=2, sort_keys=True) + "\n")
        duplicate_out = self.tmp / "duplicate-out"
        with self.assertRaisesRegex(package_bundle_pack.BundlePackError, "duplicate bundle id"):
            package_bundle_pack.package_bundles([first, duplicate], duplicate_out)
        self.assertFalse(duplicate_out.exists())

        invalid = self.tmp / "invalid-later"
        shutil.copytree(second, invalid)
        summary_path = invalid / "summary_metrics.json"
        summary = json.loads(summary_path.read_text(encoding="utf-8"))
        summary["energy_request_j"] = summary["energy_request_j"] + 1.0
        summary_path.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
        invalid_out = self.tmp / "invalid-out"
        with self.assertRaises(package_bundle_pack.BundlePackError):
            package_bundle_pack.package_bundles([first, invalid], invalid_out)
        self.assertFalse(invalid_out.exists())

    def test_post_preflight_transformation_failure_is_cleaned_up(self) -> None:
        source_bundle = self.make_bundle("pack-transform-failure")
        pack_dir = self.tmp / "divergent-pack"
        with patch.object(
            package_bundle_pack,
            "transform_public_bundle",
            side_effect=package_bundle_pack.PrivacyAuditError("injected refusal"),
        ):
            with self.assertRaisesRegex(
                package_bundle_pack.BundlePackError, "privacy transformation failed"
            ):
                package_bundle_pack.package_bundles([source_bundle], pack_dir)

        self.assertFalse(pack_dir.exists())

    def test_non_succeeded_bundle_is_refused_even_when_strict_valid(self) -> None:
        source_bundle = self.make_bundle("pack-failed-status")
        summary_path = source_bundle / "summary_metrics.json"
        summary = json.loads(summary_path.read_text(encoding="utf-8"))
        summary["status"] = "failed"
        summary["failure_reason"] = "unknown_error"
        summary["failure_message"] = "synthetic failure"
        summary_path.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
        self.assertEqual(validate_bundle(source_bundle, strict=True), [])

        with self.assertRaisesRegex(package_bundle_pack.BundlePackError, "must be succeeded"):
            package_bundle_pack.package_bundles([source_bundle], self.tmp / "failed-pack")

    def test_path_like_bundle_id_is_refused_before_copying(self) -> None:
        source_bundle = self.make_bundle("pack-traversal")
        metadata_path = source_bundle / "metadata.json"
        metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
        metadata["run_id"] = "../../PWNED_ESCAPE"
        metadata_path.write_text(json.dumps(metadata, indent=2, sort_keys=True) + "\n")
        self.assertEqual(validate_bundle(source_bundle, strict=True), [])

        escaped = self.tmp / "PWNED_ESCAPE"
        with self.assertRaisesRegex(package_bundle_pack.BundlePackError, "plain path component"):
            package_bundle_pack.package_bundles([source_bundle], self.tmp / "traversal-pack")
        self.assertFalse(escaped.exists())

    def test_verify_pack_catches_missing_extra_count_readme_and_cli_statuses(self) -> None:
        source_bundle = self.make_bundle("pack-negative")
        pack_dir = self.tmp / "negative-pack"
        built = package_bundle_pack.package_bundles([source_bundle], pack_dir)
        public_id = built["bundles"][0]["bundle_id"]

        code, stdout, stderr = _run_packager(["--verify", str(pack_dir)])
        self.assertEqual(code, 0, stderr)
        self.assertIn("valid bundle pack", stdout)

        missing_path = pack_dir / "bundles" / public_id / "events.jsonl"
        missing_path.unlink()
        problems = package_bundle_pack.verify_pack(pack_dir)
        self.assertTrue(
            any("missing file listed in manifest: events.jsonl" in problem for problem in problems),
            problems,
        )
        missing_path.write_text("", encoding="utf-8")

        extra_path = pack_dir / "bundles" / public_id / "extra.txt"
        extra_path.write_text("extra", encoding="utf-8")
        problems = package_bundle_pack.verify_pack(pack_dir)
        self.assertTrue(
            any("extra file not listed in manifest: extra.txt" in problem for problem in problems),
            problems,
        )
        extra_path.unlink()

        manifest_path = pack_dir / "MANIFEST.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["bundle_count"] = 99
        manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
        problems = package_bundle_pack.verify_pack(pack_dir)
        self.assertTrue(any("bundle_count" in problem for problem in problems), problems)
        manifest["bundle_count"] = 1
        manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")

        (pack_dir / "bundles" / "fabricated").mkdir()
        problems = package_bundle_pack.verify_pack(pack_dir)
        self.assertTrue(
            any("unexpected bundle directory not listed in manifest: fabricated" in problem for problem in problems),
            problems,
        )
        (pack_dir / "bundles" / "fabricated").rmdir()

        readme_path = pack_dir / "README.md"
        readme_path.write_text(readme_path.read_text(encoding="utf-8") + "\ntampered\n", encoding="utf-8")
        problems = package_bundle_pack.verify_pack(pack_dir)
        self.assertTrue(any("README.md hash mismatch" in problem for problem in problems), problems)

        code, stdout, stderr = _run_packager(["--verify", str(pack_dir)])
        self.assertEqual(code, 2)
        self.assertIn("invalid pack:", stdout)
        self.assertEqual(stderr, "")

    def test_verify_pack_rejects_duplicate_bundle_ids_and_file_paths(self) -> None:
        source_bundle = self.make_bundle("pack-duplicate-manifest")
        pack_dir = self.tmp / "duplicate-manifest-pack"
        built = package_bundle_pack.package_bundles([source_bundle], pack_dir)
        public_id = built["bundles"][0]["bundle_id"]

        manifest_path = pack_dir / "MANIFEST.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["bundles"].append(json.loads(json.dumps(manifest["bundles"][0])))
        manifest["bundle_count"] = 2
        readme = package_bundle_pack._readme(package_bundle_pack._readme_manifest(manifest))
        (pack_dir / "README.md").write_text(readme, encoding="utf-8")
        manifest["readme_sha256"] = _sha256(pack_dir / "README.md")
        manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")

        problems = package_bundle_pack.verify_pack(pack_dir)

        self.assertTrue(
            any(f"duplicate manifest bundle_id: {public_id}" in problem for problem in problems),
            problems,
        )

        manifest["bundles"] = manifest["bundles"][:1]
        manifest["bundle_count"] = 1
        manifest["bundles"][0]["files"].append(json.loads(json.dumps(manifest["bundles"][0]["files"][0])))
        readme = package_bundle_pack._readme(package_bundle_pack._readme_manifest(manifest))
        (pack_dir / "README.md").write_text(readme, encoding="utf-8")
        manifest["readme_sha256"] = _sha256(pack_dir / "README.md")
        manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")

        problems = package_bundle_pack.verify_pack(pack_dir)

        self.assertTrue(
            any("duplicate manifest file path" in problem for problem in problems),
            problems,
        )

    def test_verify_pack_catches_pack_root_extras_and_injected_symlinks(self) -> None:
        source_bundle = self.make_bundle("pack-root-extra")
        pack_dir = self.tmp / "root-extra-pack"
        built = package_bundle_pack.package_bundles([source_bundle], pack_dir)
        public_id = built["bundles"][0]["bundle_id"]

        (pack_dir / "EXTRA.txt").write_text("extra", encoding="utf-8")
        problems = package_bundle_pack.verify_pack(pack_dir)
        self.assertTrue(any("unexpected file at pack root: EXTRA.txt" in problem for problem in problems), problems)
        (pack_dir / "EXTRA.txt").unlink()

        symlink_path = pack_dir / "bundles" / public_id / "link-to-config"
        try:
            symlink_path.symlink_to("config.json")
        except OSError as exc:
            self.skipTest(f"symlink creation unavailable: {exc}")
        problems = package_bundle_pack.verify_pack(pack_dir)
        self.assertTrue(
            any("symlink not allowed in packed bundle: link-to-config" in problem for problem in problems),
            problems,
        )


if __name__ == "__main__":
    unittest.main()
