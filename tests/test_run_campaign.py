from __future__ import annotations

import importlib.util
import hashlib
import io
import json
import math
import os
import shutil
import shlex
import subprocess
import sys
import tempfile
import textwrap
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from unittest.mock import patch

from scripts.run_campaign import (
    ShakedownGateError,
    append_log,
    execute_production_uncertainty_gate,
    failed_shakedown_record,
)


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "run_campaign.py"
BASE_CONFIG = ROOT / "configs" / "examples" / "mock_local.json"
SUITE_CONFIG = ROOT / "configs" / "examples" / "mock_suite_local.json"
COMMAND_TIMEOUT_S = 60
GENERATOR = ROOT / "scripts" / "generate_matrix.py"
TEST_CAMPAIGN_POLICY = ROOT / "tests" / "fixtures" / "campaign_policy_test.json"

spec = importlib.util.spec_from_file_location("run_campaign_module", SCRIPT)
run_campaign_module = importlib.util.module_from_spec(spec)
assert spec.loader is not None
sys.modules["run_campaign_module"] = run_campaign_module
spec.loader.exec_module(run_campaign_module)


def run_campaign(
    config_dir: Path,
    runs_dir: Path,
    *,
    cli_cmd: str | None = None,
    dry_run: bool = False,
    max_failures: int | None = None,
    log_path: Path | None = None,
    backup: Path | None = None,
    waivers: Path | None = None,
    shakedown_gate: bool = False,
    ack_config_warnings: bool = False,
    campaign_policy: Path | None = TEST_CAMPAIGN_POLICY,
    environment_override: Path | None = None,
) -> subprocess.CompletedProcess[str]:
    command = [sys.executable, str(SCRIPT), str(config_dir), "--runs-dir", str(runs_dir)]
    if log_path is not None:
        command.extend(["--log", str(log_path)])
    if dry_run:
        command.append("--dry-run")
    if backup is not None:
        command.extend(["--backup", str(backup)])
    if shakedown_gate:
        command.extend(["--shakedown-gate", "production_uncertainty_v1"])
    if ack_config_warnings:
        command.append("--ack-config-warnings")
    if campaign_policy is not None:
        command.extend(["--campaign-policy", str(campaign_policy)])
    if environment_override is not None:
        command.extend(["--environment-override", str(environment_override)])
    if waivers is not None:
        command.extend(["--waivers", str(waivers)])
    if cli_cmd is not None:
        command.extend(["--cli-cmd", cli_cmd])
    if max_failures is not None:
        command.extend(["--max-failures", str(max_failures)])
    return subprocess.run(
        command,
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
        timeout=COMMAND_TIMEOUT_S,
    )


def cli_cmd_for(fake_cli: Path) -> str:
    return shlex.join([sys.executable, str(fake_cli)])


def rendered_cli_command(cli_cmd: str, config_path: Path, runs_dir: Path) -> str:
    return shlex.join(shlex.split(cli_cmd) + ["run", str(config_path), "--runs-dir", str(runs_dir)])


def write_config(config_dir: Path, filename: str, run_id: str, repetitions: int = 1) -> Path:
    path = config_dir / filename
    payload = json.loads(BASE_CONFIG.read_text(encoding="utf-8"))
    payload["run_id"] = run_id
    payload["workload_profile"]["repetitions"] = repetitions
    path.write_text(json.dumps(payload) + "\n", encoding="utf-8")
    return path


def write_suite_config(
    config_dir: Path,
    filename: str,
    run_id: str,
    *,
    sidecar: str | Path | None = None,
    suite_manifest: str | Path | None = None,
    prompt_token_evidence_policy: str | None = None,
) -> Path:
    path = config_dir / filename
    payload = json.loads(SUITE_CONFIG.read_text(encoding="utf-8"))
    payload["run_id"] = run_id
    if suite_manifest is not None:
        payload["workload_profile"]["suite_manifest_ref"] = str(suite_manifest)
    if sidecar is not None:
        payload["workload_profile"]["generator_sidecar_ref"] = str(sidecar)
    if prompt_token_evidence_policy is not None:
        payload["workload_profile"]["prompt_token_evidence_policy"] = (
            prompt_token_evidence_policy
        )
    path.write_text(json.dumps(payload) + "\n", encoding="utf-8")
    return path


def write_prompt_sidecar(
    path: Path,
    *,
    item_003_hash: str,
    subset_sha256: str = "mock-subset",
    include_item_003: bool = True,
) -> None:
    items: dict[str, dict[str, str]] = {
        "mock_item_002": {
            "prompt_source": "token_ids",
            "token_ids_sha256": "5d7c51bfa697d3e72c8b79b97ba7396ffd399406ccb332b028bd38f44557a284",
        },
    }
    if include_item_003:
        items["mock_item_003"] = {"token_ids_sha256": item_003_hash}
    path.write_text(
        json.dumps(
            {
                "suite": "jw_mixed_v1",
                "source_manifest": {
                    "source_id": "mock_suite_source",
                    "subset_sha256": subset_sha256,
                },
                "tokenizer": {"tokenizer_id": "mock"},
                "items": items,
            }
        )
        + "\n",
        encoding="utf-8",
    )


def write_single_bundle(
    runs_dir: Path,
    run_id: str,
    status: str = "succeeded",
    *,
    idle_window_suspect: bool | None = None,
    config_path: Path | None = None,
    start_s: float = 0.0,
    runtime_cleanup_ok: bool | None = None,
    remote_cleanup_failed: list[str] | None = None,
) -> None:
    _write_bundle(
        runs_dir,
        run_id,
        status,
        idle_window_suspect=idle_window_suspect,
        config_path=config_path,
        start_s=start_s,
        runtime_cleanup_ok=runtime_cleanup_ok,
        remote_cleanup_failed=remote_cleanup_failed,
    )


def write_experiment(
    runs_dir: Path,
    run_id: str,
    repetitions: int,
    *,
    statuses: list[str] | None = None,
    completed: int | None = None,
    config_path: Path | None = None,
) -> None:
    if statuses is None:
        statuses = ["succeeded"] * repetitions
    if completed is None:
        completed = repetitions
    members: list[str] = []
    for rep in range(1, completed + 1):
        member_name = f"{run_id}__r{rep}"
        members.append(member_name)
        _write_bundle(
            runs_dir,
            member_name,
            statuses[rep - 1],
            config_path=config_path,
        )
    experiments = runs_dir / "experiments"
    experiments.mkdir(parents=True, exist_ok=True)
    (experiments / f"{run_id}.json").write_text(
        json.dumps(
            {
                "experiment_id": run_id,
                "config_sha256": "fake",
                "members": members,
                "condition_order": ["test"] * len(members),
                "cooldown": [],
                "created_at_s": 0.0,
            }
        )
        + "\n",
        encoding="utf-8",
    )


def _write_bundle(
    runs_dir: Path,
    run_id: str,
    status: str,
    *,
    idle_window_suspect: bool | None = None,
    config_path: Path | None = None,
    start_s: float = 0.0,
    runtime_cleanup_ok: bool | None = None,
    remote_cleanup_failed: list[str] | None = None,
) -> None:
    from joulewise import reduce as reduce_module
    from joulewise.bundle import RunBundleWriter, sanitize_id_component
    from joulewise.clock import FakeClock
    from joulewise.interfaces import PowerSample, RuntimeEvent
    from joulewise.provenance import output_policy, prompt_provenance
    from joulewise.schemas import BenchmarkConfig, FailureReason, RunStatus, SummaryMetrics

    source_config = config_path if config_path is not None else BASE_CONFIG
    config_data = json.loads(source_config.read_text(encoding="utf-8"))
    if sanitize_id_component(config_data["run_id"]) != run_id:
        config_data["run_id"] = run_id
    if config_path is None:
        config_data["workload_profile"]["repetitions"] = 1
    config = BenchmarkConfig.from_mapping(config_data)
    telemetry_backend = config.hardware_target.telemetry_backend.value
    writer = RunBundleWriter.create(runs_dir, config, FakeClock(start=start_s + 1.1))

    def event(timestamp_s: float, event_type: str, phase: str, message: str = "") -> None:
        writer.append_event(
            RuntimeEvent(
                timestamp_s=start_s + timestamp_s,
                event_type=event_type,
                phase=phase,
                message=message or f"{event_type} {phase}",
                metadata={},
            )
        )

    if status == "succeeded":
        event(0.0, "stage_started", "measured_run")
        event(0.0, "sampling_started", "measured_run")
        event(0.0, "phase_start", "prefill")
        event(0.5, "phase_end", "prefill")
        event(0.5, "phase_start", "decode")
        event(0.6, "token", "decode")
        event(0.7, "token", "decode")
        event(0.8, "phase_end", "decode")
        event(1.0, "sampling_stopped", "measured_run")
        event(1.0, "stage_completed", "measured_run")
        if runtime_cleanup_ok is not None:
            writer.append_event(
                RuntimeEvent(
                    timestamp_s=start_s + 1.05,
                    event_type="stage_completed",
                    phase="cleanup",
                    message="stage_completed cleanup",
                    metadata={"cleanup_ok": runtime_cleanup_ok},
                )
            )
        writer.write_power_trace(
            [
                PowerSample(
                    timestamp_s=start_s + step / 10.0,
                    power_w=7.5,
                    source=telemetry_backend,
                    rail="mock",
                )
                for step in range(11)
            ]
        )
        idle = {
            "power_w_mean": 5.0,
            "power_w_stddev": 0.0,
            "duration_s": 1.0,
            "sample_count": 2,
            "telemetry_backend": telemetry_backend,
            "idle_window_suspect": False,
        }
        if idle_window_suspect is not None:
            idle["idle_window_suspect"] = idle_window_suspect
        metadata = {
                "device": {"telemetry": telemetry_backend, "rail_manifest": ["mock"]},
                "adapters": {"telemetry": {"name": telemetry_backend}},
                "clock_anchor_bound_s": 0.0,
                "idle_drift_bound_w": 0.0,
                "idle_baseline": idle,
                "workload_observed": {"token_count": 34, "output_token_count": 2},
                "workload_provenance": {
                    "prompt": prompt_provenance([1, 2, 3], text="test"),
                    "generator": {"name": "fake_cli", "version": "test"},
                    "tokenizer": {
                        "backend": "mock",
                        "identifier": "fake",
                        "revision": "test",
                        "class": "FakeTokenizer",
                        "vocab_size": None,
                    },
                    "model": {"source": config.model.source, "revision": config.model.revision},
                    "output_policy": output_policy(
                        "fixed_budget_exact",
                        requested_tokens=2,
                        emitted_tokens=2,
                        stop_condition="requested_tokens_emitted",
                    ),
                },
            }
        if remote_cleanup_failed:
            metadata["extra"] = {
                "node_cleanup": [
                    {"path": path, "removed": False}
                    for path in remote_cleanup_failed
                ]
            }
        writer.write_metadata(metadata)
        summary = reduce_module.reduce_bundle(writer.path)
    else:
        writer.write_metadata(
            {
                "device": {"telemetry": "mock", "rail_manifest": ["mock"]},
                "adapters": {"telemetry": {"name": "mock"}},
            }
        )
        summary = SummaryMetrics(
            status=RunStatus.FAILED,
            failure_reason=FailureReason.UNKNOWN_ERROR,
            failure_message="fake failure",
        )
    writer.write_summary(summary)
    writer.finalize()


def make_fake_cli(tmp: Path, sentinel: Path | None = None) -> Path:
    sentinel_line = f"Path({str(sentinel)!r}).write_text('invoked\\n', encoding='utf-8')" if sentinel else "pass"
    script = tmp / "fake_cli.py"
    script.write_text(
        textwrap.dedent(
            f"""
            import json
            import sys
            from pathlib import Path

            ROOT = Path({str(ROOT)!r})
            if str(ROOT) not in sys.path:
                sys.path.insert(0, str(ROOT))
            from joulewise import reduce as reduce_module
            from joulewise.bundle import sanitize_id_component
            from joulewise.bundle import RunBundleWriter
            from joulewise.clock import FakeClock
            from joulewise.interfaces import PowerSample, RuntimeEvent
            from joulewise.provenance import output_policy, prompt_provenance
            from joulewise.schemas import BenchmarkConfig, FailureReason, RunStatus, SummaryMetrics

            {sentinel_line}
            if len(sys.argv) < 5 or sys.argv[1] != "run":
                raise SystemExit(64)

            config_path = Path(sys.argv[2])
            runs_dir = Path(sys.argv[sys.argv.index("--runs-dir") + 1])
            config = json.loads(config_path.read_text(encoding="utf-8"))
            run_id = sanitize_id_component(config["run_id"])
            repetitions = config.get("workload_profile", {{}}).get("repetitions", 1)
            runs_dir.mkdir(parents=True, exist_ok=True)
            with (runs_dir / "order.log").open("a", encoding="utf-8") as handle:
                handle.write(run_id + "\\n")

            def emit_bundle(bundle, status):
                print(f"bundle: {{bundle}} status={{status}}")

            def write_bundle(bundle_run_id, status):
                config_data = json.loads(config_path.read_text(encoding="utf-8"))
                config_data["run_id"] = bundle_run_id
                config = BenchmarkConfig.from_mapping(config_data)
                telemetry_backend = config.hardware_target.telemetry_backend.value
                writer = RunBundleWriter.create(runs_dir, config, FakeClock(start=3.0))

                def event(timestamp_s, event_type, phase):
                    writer.append_event(
                        RuntimeEvent(
                            timestamp_s=timestamp_s,
                            event_type=event_type,
                            phase=phase,
                            message=f"{{event_type}} {{phase}}",
                            metadata={{}},
                        )
                    )

                if status == "succeeded":
                    event(0.0, "stage_started", "measured_run")
                    event(0.0, "sampling_started", "measured_run")
                    event(0.0, "phase_start", "prefill")
                    event(0.5, "phase_end", "prefill")
                    event(0.5, "phase_start", "decode")
                    event(0.6, "token", "decode")
                    event(0.7, "token", "decode")
                    event(0.8, "phase_end", "decode")
                    event(1.0, "sampling_stopped", "measured_run")
                    event(1.0, "stage_completed", "measured_run")
                    writer.write_power_trace(
                        [
                            PowerSample(timestamp_s=0.0, power_w=7.5, source=telemetry_backend, rail="mock"),
                            PowerSample(timestamp_s=0.25, power_w=7.5, source=telemetry_backend, rail="mock"),
                            PowerSample(timestamp_s=0.5, power_w=7.5, source=telemetry_backend, rail="mock"),
                            PowerSample(timestamp_s=0.75, power_w=7.5, source=telemetry_backend, rail="mock"),
                            PowerSample(timestamp_s=1.0, power_w=7.5, source=telemetry_backend, rail="mock"),
                        ]
                    )
                    writer.write_metadata(
                        {{
                            "device": {{"telemetry": telemetry_backend, "rail_manifest": ["mock"]}},
                            "adapters": {{"telemetry": {{"name": telemetry_backend}}}},
                            "clock_anchor_bound_s": 0.0,
                            "idle_drift_bound_w": 0.0,
                            "idle_baseline": {{
                                "power_w_mean": 5.0,
                                "power_w_stddev": 0.0,
                                "duration_s": 1.0,
                                "sample_count": 2,
                                "telemetry_backend": telemetry_backend,
                                "idle_window_suspect": False,
                            }},
                            "workload_observed": {{"token_count": 34, "output_token_count": 2}},
                            "workload_provenance": {{
                                "prompt": prompt_provenance([1, 2, 3], text="test"),
                                "generator": {{"name": "fake_cli", "version": "test"}},
                                "tokenizer": {{
                                    "backend": "mock",
                                    "identifier": "fake",
                                    "revision": "test",
                                    "class": "FakeTokenizer",
                                    "vocab_size": None,
                                }},
                                "model": {{"source": config.model.source, "revision": config.model.revision}},
                                "output_policy": output_policy(
                                    "fixed_budget_exact",
                                    requested_tokens=2,
                                    emitted_tokens=2,
                                    stop_condition="requested_tokens_emitted",
                                ),
                            }},
                        }}
                    )
                    summary = reduce_module.reduce_bundle(writer.path)
                else:
                    writer.write_metadata(
                        {{
                            "device": {{"telemetry": "mock", "rail_manifest": ["mock"]}},
                            "adapters": {{"telemetry": {{"name": "mock"}}}},
                        }}
                    )
                    summary = SummaryMetrics(
                        status=RunStatus.FAILED,
                        failure_reason=FailureReason.UNKNOWN_ERROR,
                        failure_message="fake failure",
                    )
                writer.write_summary(summary)
                bundle = writer.finalize()
                emit_bundle(bundle, status)

            def write_single(status):
                write_bundle(run_id, status)

            def write_manifest(members):
                experiments = runs_dir / "experiments"
                experiments.mkdir(parents=True, exist_ok=True)
                manifest = experiments / f"{{run_id}}.json"
                manifest.write_text(
                    json.dumps(
                        {{
                            "experiment_id": run_id,
                            "config_sha256": "fake",
                            "members": members,
                            "condition_order": ["test"] * len(members),
                            "cooldown": [],
                            "created_at_s": 0.0,
                        }}
                    )
                    + "\\n",
                    encoding="utf-8",
                )
                return manifest

            def write_experiment(statuses, completed=None):
                if completed is None:
                    completed = repetitions
                members = []
                for rep in range(1, completed + 1):
                    member_name = f"{{run_id}}__r{{rep}}"
                    members.append(member_name)
                    write_bundle(member_name, statuses[rep - 1])
                manifest = write_manifest(members)
                print(f"experiment: {{manifest}} members={{len(members)}}")

            if "fail" in run_id:
                if repetitions > 1:
                    statuses = ["succeeded"] * repetitions
                    statuses[-1] = "failed"
                    write_experiment(statuses)
                else:
                    write_single("failed")
                raise SystemExit(3)

            if "exit2" in run_id:
                raise SystemExit(2)

            if "crash2" in run_id:
                if repetitions > 1:
                    write_experiment(["succeeded"] * repetitions, completed=min(2, repetitions))
                else:
                    (runs_dir / run_id).mkdir(parents=True, exist_ok=True)
                raise SystemExit(3)

            if "partial" in run_id:
                if repetitions > 1:
                    write_experiment(["succeeded"] * repetitions, completed=max(1, repetitions - 2))
                else:
                    (runs_dir / run_id).mkdir(parents=True, exist_ok=True)
                raise SystemExit(3)

            if repetitions > 1:
                write_experiment(["succeeded"] * repetitions)
            else:
                write_single("succeeded")
            raise SystemExit(0)
            """
        ).lstrip(),
        encoding="utf-8",
    )
    return script


def read_jsonl(path: Path) -> list[dict]:
    return [
        row
        for row in read_all_jsonl(path)
        if row.get("record_type") != "campaign_verdict"
    ]


def read_all_jsonl(path: Path) -> list[dict]:
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def write_strict_analysis_campaign(
    config_dir: Path,
    runs_dir: Path | None = None,
    *,
    telemetry_backend: str = "mock",
) -> dict:
    base_payload = json.loads(BASE_CONFIG.read_text(encoding="utf-8"))
    base_payload["hardware_target"]["telemetry_backend"] = telemetry_backend
    base_path = config_dir.parent / "analysis-base.json"
    base_path.write_text(json.dumps(base_payload) + "\n", encoding="utf-8")
    result = subprocess.run(
        [
            sys.executable,
            str(GENERATOR),
            "--base",
            str(base_path),
            "--model-tag",
            "mock",
            "--out-dir",
            str(config_dir),
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
        timeout=COMMAND_TIMEOUT_S,
    )
    if result.returncode != 0:
        raise AssertionError(result.stderr)
    manifest = json.loads(
        (config_dir / "analysis_manifest.json").read_text(encoding="utf-8")
    )
    if runs_dir is not None:
        for index, entry in enumerate(manifest["entries"]):
            write_single_bundle(
                runs_dir,
                entry["run_id"],
                config_path=config_dir / entry["config"],
                start_s=float(index * 2),
            )
    return manifest


def write_prior_campaign_provenance(
    runs_dir: Path,
    evidence_by_bundle: dict[str, str],
    analysis_manifest_id: str,
) -> None:
    manifest_dir = runs_dir / "campaign_manifests"
    raw_dir = manifest_dir / "raw"
    raw_dir.mkdir(parents=True, exist_ok=True)
    raw_payload = json.dumps({"rolling_mean_power_w": 5.0}) + "\n"
    (raw_dir / "fixture.jsonl").write_text(raw_payload, encoding="utf-8")
    raw_sha = hashlib.sha256(raw_payload.encode("utf-8")).hexdigest()
    session_id = "campaign-fixture"
    members = []
    for bundle_id, result in evidence_by_bundle.items():
        cooldown: dict[str, object] = {
            "result": result,
            "session_id": session_id,
            "following_run_id": bundle_id,
        }
        if result in {"recovered", "cap_hit"}:
            cooldown["raw_artifact"] = {
                "path": "raw/fixture.jsonl",
                "sha256": raw_sha,
                "records": 1,
            }
        members.append(
            {
                "config": f"{bundle_id}.json",
                "run_id": bundle_id,
                "bundle_ids": [bundle_id],
                "execution": "invoked",
                "preceding_campaign_cooldown": cooldown,
            }
        )
    (manifest_dir / "fixture.json").write_text(
        json.dumps(
            {
                "schema_version": "joulewise.campaign_provenance.v1",
                "session_id": session_id,
                "created_at": "2026-07-10T00:00:00Z",
                "config_dir": "fixture",
                "analysis_manifest_id": analysis_manifest_id,
                "first_physical_run_id": next(iter(evidence_by_bundle), None),
                "members": members,
                "cooldown_gates": [],
            }
        )
        + "\n",
        encoding="utf-8",
    )


def write_malformed_first_exemption_provenance(
    runs_dir: Path,
    manifest: dict,
    *,
    fan_out_one_note: bool,
) -> None:
    manifest_dir = runs_dir / "campaign_manifests"
    manifest_dir.mkdir(parents=True, exist_ok=True)
    session_id = "campaign-malformed-first-exemptions"
    run_ids = [entry["run_id"] for entry in manifest["entries"]]
    first_run_id = run_ids[0]
    if fan_out_one_note:
        members = [
            {
                "config": manifest["entries"][0]["config"],
                "run_id": first_run_id,
                "bundle_ids": run_ids,
                "execution": "invoked",
                "preceding_campaign_cooldown": {
                    "result": "first_run_exempt",
                    "session_id": session_id,
                    "following_run_id": first_run_id,
                },
            }
        ]
    else:
        members = [
            {
                "config": entry["config"],
                "run_id": entry["run_id"],
                "bundle_ids": [entry["run_id"]],
                "execution": "invoked",
                "preceding_campaign_cooldown": {
                    "result": "first_run_exempt",
                    "session_id": session_id,
                    "following_run_id": entry["run_id"],
                },
            }
            for entry in manifest["entries"]
        ]
    (manifest_dir / "malformed-first-exemptions.json").write_text(
        json.dumps(
            {
                "schema_version": "joulewise.campaign_provenance.v1",
                "session_id": session_id,
                "created_at": "2026-07-10T00:00:00Z",
                "config_dir": "fixture",
                "analysis_manifest_id": manifest["manifest_id"],
                "first_physical_run_id": first_run_id,
                "members": members,
                "cooldown_gates": [],
            }
        )
        + "\n",
        encoding="utf-8",
    )


def analysis_manifest_id(config_dir: Path) -> str:
    return json.loads(
        (config_dir / "analysis_manifest.json").read_text(encoding="utf-8")
    )["manifest_id"]


class RunCampaignTests(unittest.TestCase):
    def test_campaign_policy_defaults_to_production_sidecar(self) -> None:
        args = run_campaign_module.parse_args(["configs"])
        binding = run_campaign_module.load_campaign_policy(args.campaign_policy)
        self.assertEqual(binding.policy.policy_id, "quiet-mac-p2-production")
        self.assertEqual(binding.policy.profile.value, "production")
        self.assertEqual(binding.policy.idle_admission.on_fail.value, "abort")

    def test_frozen_campaign_anchor_is_explicit_child_experiment_argument(self) -> None:
        from joulewise import cli as cli_module
        from joulewise.clock import FakeClock

        anchor = {
            "schema_version": "joulewise.cooldown_anchor.v1",
            "source_kind": "neg8_reference_start",
            "bundle_id": "neg8-anchor",
            "policy_sha256": "a" * 64,
            "environment_snapshot_sha256": "b" * 64,
            "immutable_after_freeze": True,
            "eligibility": {
                "eligible": True,
                "provenance_present": True,
            },
            "baseline": {
                "power_w_mean": 5.0,
                "power_w_stddev": 0.0,
                "duration_s": 30.0,
                "sample_count": 30,
                "telemetry_backend": "powermetrics",
                "idle_window_suspect": False,
            },
        }
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            config_dir = root / "configs"
            runs_dir = root / "runs"
            config_dir.mkdir()
            config_path = write_config(
                config_dir, "multi.json", "multi", repetitions=2
            )
            with (
                patch(
                    "run_campaign_module.prior_campaign_cooldown_anchor",
                    return_value=anchor,
                ),
                patch(
                    "run_campaign_module.command_for",
                    wraps=run_campaign_module.command_for,
                ) as parent_command,
                redirect_stdout(io.StringIO()),
                redirect_stderr(io.StringIO()),
            ):
                parent_code = run_campaign_module.main(
                    [
                        str(config_dir),
                        "--runs-dir",
                        str(runs_dir),
                        "--dry-run",
                        "--campaign-policy",
                        str(TEST_CAMPAIGN_POLICY),
                    ]
                )

            self.assertEqual(parent_code, 0)
            self.assertEqual(
                parent_command.call_args.kwargs["frozen_cooldown_anchor"], anchor
            )
            command = run_campaign_module.command_for(
                config_path,
                runs_dir,
                None,
                frozen_cooldown_anchor=anchor,
            )
            self.assertIn("--frozen-cooldown-anchor-json", command)
            anchor_index = command.index("--frozen-cooldown-anchor-json") + 1
            self.assertEqual(json.loads(command[anchor_index]), anchor)

            with (
                patch("joulewise.cli._select_clock", return_value=FakeClock()),
                patch(
                    "joulewise.cli.run_experiment",
                    return_value=(runs_dir / "experiments" / "multi.json", []),
                ) as child_experiment,
                redirect_stdout(io.StringIO()),
                redirect_stderr(io.StringIO()),
            ):
                child_code = cli_module.main(command[3:])

            self.assertEqual(child_code, 0)
            self.assertEqual(
                child_experiment.call_args.kwargs["frozen_cooldown_anchor"], anchor
            )

    def test_parent_anchor_validator_has_canonical_child_parity(self) -> None:
        from joulewise.cooldown_anchor import cooldown_anchor_eligibility

        policy_sha256 = "a" * 64
        anchor = {
            "schema_version": "joulewise.cooldown_anchor.v1",
            "source_kind": "neg8_reference_start",
            "bundle_id": "neg8-anchor",
            "policy_sha256": policy_sha256,
            "environment_snapshot_sha256": "b" * 64,
            "immutable_after_freeze": True,
            "eligibility": {
                "eligible": True,
                "provenance_present": True,
            },
            "baseline": {
                "power_w_mean": 5.0,
                "power_w_stddev": 0.0,
                "duration_s": 30.0,
                "sample_count": 30,
                "telemetry_backend": "powermetrics",
                "idle_window_suspect": False,
            },
        }
        malformed = json.loads(json.dumps(anchor))
        malformed["policy_sha256"] = "c" * 64
        malformed["eligibility"].pop("provenance_present")
        malformed["baseline"]["idle_window_suspect"] = True

        for candidate in (anchor, malformed):
            with self.subTest(eligible=candidate is anchor):
                self.assertEqual(
                    run_campaign_module._cooldown_anchor_eligibility(
                        candidate, policy_sha256
                    ),
                    cooldown_anchor_eligibility(candidate, policy_sha256),
                )

    def test_environment_preflight_fails_closed_and_override_binds_exact_snapshot(self) -> None:
        binding = run_campaign_module.load_campaign_policy(
            str(ROOT / "configs" / "campaign_policies" / "quiet_mac_p2_production.json")
        )
        snapshot = {
            "power_source": "AC Power",
            "power": {"external_connected": True},
            "low_power_mode": False,
            "display_power_state": "any_awake",
            "screensaver_engaged": False,
            "thermal_pressure": "nominal",
            "load_average_1m": 0.0,
        }
        with tempfile.TemporaryDirectory() as tmp:
            with patch(
                "run_campaign_module.collect_environment_snapshot",
                return_value=snapshot,
            ):
                blocked = run_campaign_module.campaign_environment_preflight(
                    binding,
                    arm_quiet_mode=False,
                    arm_countdown_s=0,
                    override_path=None,
                )
            self.assertFalse(blocked["admitted"])
            evaluation = blocked["evaluation"]
            override_path = Path(tmp) / "override.json"
            override_path.write_text(
                json.dumps(
                    {
                        "schema_version": "joulewise.environment_override.v1",
                        "snapshot_sha256": evaluation["snapshot_sha256"],
                        "findings_sha256": evaluation["findings_sha256"],
                        "reason": "bounded exploratory collection",
                        "approver": "campaign-owner",
                        "timestamp": "2026-07-17T00:00:00Z",
                    }
                )
                + "\n",
                encoding="utf-8",
            )
            with patch(
                "run_campaign_module.collect_environment_snapshot",
                return_value=snapshot,
            ):
                overridden = run_campaign_module.campaign_environment_preflight(
                    binding,
                    arm_quiet_mode=False,
                    arm_countdown_s=0,
                    override_path=str(override_path),
                )

        self.assertTrue(overridden["admitted"])
        self.assertEqual(overridden["override"]["classification"], "override")
        self.assertFalse(overridden["override"]["claim_eligible"])

    def test_rejected_environment_preflight_appends_terminal_verdict(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            config_dir = root / "configs"
            runs_dir = root / "runs"
            config_dir.mkdir()
            write_config(config_dir, "one.json", "one")
            args = run_campaign_module.parse_args(
                [
                    str(config_dir),
                    "--runs-dir",
                    str(runs_dir),
                    "--campaign-policy",
                    str(
                        ROOT
                        / "configs"
                        / "campaign_policies"
                        / "quiet_mac_p2_production.json"
                    ),
                ]
            )
            rejected = {
                "power_source": "AC Power",
                "power": {"external_connected": True},
                "low_power_mode": False,
                "display_power_state": "any_awake",
                "screensaver_engaged": False,
                "thermal_pressure": "nominal",
            }
            with patch(
                "run_campaign_module.collect_environment_snapshot",
                return_value=rejected,
            ):
                result = run_campaign_module.run_campaign(args)

            self.assertEqual(result, 1)
            rows = read_all_jsonl(runs_dir / "campaign_log.jsonl")
            self.assertEqual(rows[-1]["schema_version"], "joulewise.campaign_verdict.v2")
            self.assertEqual(rows[-1]["record_type"], "campaign_verdict")
            self.assertEqual(rows[-1]["collection"]["verdict"], "invalid")
            self.assertIn(
                "environment preflight rejected",
                rows[-1]["collection"]["reasons"][0],
            )

    def test_malformed_environment_override_appends_terminal_verdict(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            config_dir = root / "configs"
            runs_dir = root / "runs"
            config_dir.mkdir()
            write_config(config_dir, "one.json", "one")
            override = root / "override.json"
            override.write_text("{not-json\n", encoding="utf-8")
            args = run_campaign_module.parse_args(
                [
                    str(config_dir),
                    "--runs-dir",
                    str(runs_dir),
                    "--campaign-policy",
                    str(
                        ROOT
                        / "configs"
                        / "campaign_policies"
                        / "quiet_mac_p2_production.json"
                    ),
                    "--environment-override",
                    str(override),
                ]
            )
            clean = {
                "power_source": "AC Power",
                "power": {"external_connected": True},
                "low_power_mode": False,
                "display_power_state": "all_asleep",
                "screensaver_engaged": False,
                "thermal_pressure": "nominal",
            }
            with patch(
                "run_campaign_module.collect_environment_snapshot",
                return_value=clean,
            ):
                result = run_campaign_module.run_campaign(args)

            self.assertEqual(result, 2)
            verdict = read_all_jsonl(runs_dir / "campaign_log.jsonl")[-1]
            self.assertEqual(verdict["record_type"], "campaign_verdict")
            self.assertEqual(verdict["collection"]["verdict"], "invalid")

    def test_arm_quiet_mode_counts_down_sleeps_display_and_reprobes(self) -> None:
        binding = run_campaign_module.load_campaign_policy(
            str(ROOT / "configs" / "campaign_policies" / "quiet_mac_p2_production.json")
        )
        base = {
            "power_source": "AC Power",
            "power": {"external_connected": True},
            "low_power_mode": False,
            "screensaver_engaged": False,
            "thermal_pressure": "nominal",
            "load_average_1m": 0.0,
        }
        awake = {**base, "display_power_state": "any_awake"}
        asleep = {**base, "display_power_state": "all_asleep"}
        completed = subprocess.CompletedProcess(
            ["pmset", "displaysleepnow"], 0, "", ""
        )
        with (
            patch(
                "run_campaign_module.collect_environment_snapshot",
                side_effect=[awake, asleep],
            ) as collect,
            patch("run_campaign_module.subprocess.run", return_value=completed) as run,
        ):
            result = run_campaign_module.campaign_environment_preflight(
                binding,
                arm_quiet_mode=True,
                arm_countdown_s=0,
                override_path=None,
            )

        self.assertEqual(collect.call_count, 2)
        self.assertEqual(run.call_args.args[0], ["pmset", "displaysleepnow"])
        self.assertTrue(result["admitted"])
        self.assertTrue(result["arm_quiet_mode"]["verified_by_reprobe"])

    def test_cooldown_v2_contaminated_reference_falls_back_to_frozen_anchor(self) -> None:
        from joulewise.clock import FakeClock
        from joulewise.interfaces import ThermalState
        from joulewise.schemas import IdleBaseline, TelemetryBackend

        class CooldownTelemetry:
            name = "cooldown-fixture"

            def __init__(self, clock):
                self.clock = clock

            def measure_idle(self, config, context=None):
                self.clock.sleep(config.sampling.idle_seconds)
                return IdleBaseline(
                    power_w_mean=0.15,
                    power_w_stddev=0.0,
                    duration_s=config.sampling.idle_seconds,
                    sample_count=5,
                    telemetry_backend=TelemetryBackend.POWERMETRICS,
                    idle_window_suspect=False,
                )

            def thermal_state(self, config, context=None):
                return ThermalState(
                    timestamp_s=self.clock.now(), thermal_pressure="Nominal"
                )

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            config_path = root / "previous.json"
            payload = json.loads(BASE_CONFIG.read_text(encoding="utf-8"))
            payload["run_id"] = "previous"
            payload["hardware_target"]["telemetry_backend"] = "powermetrics"
            config_path.write_text(json.dumps(payload) + "\n", encoding="utf-8")
            previous_info = run_campaign_module.ConfigInfo(
                path=config_path,
                run_id="previous",
                raw_run_id="previous",
                repetitions=1,
            )
            following_info = run_campaign_module.ConfigInfo(
                path=config_path,
                run_id="following",
                raw_run_id="following",
                repetitions=1,
            )
            contaminated = {
                "power_w_mean": 0.8,
                "power_w_stddev": 0.1,
                "duration_s": 30.0,
                "sample_count": 30,
                "telemetry_backend": "powermetrics",
                "idle_window_suspect": True,
            }
            previous = run_campaign_module.MemberEvaluation(
                bundle_id="previous",
                bundle_path=root / "previous",
                config_name=config_path.name,
                status="succeeded",
                strict_valid=True,
                summary={"idle_baseline": contaminated},
                metadata={
                    "campaign_policy": {"sha256": "b" * 64},
                    "environment_admission": {
                        "critical_environment_passed": False,
                        "decision": "flagged",
                        "reference_provenance_present": True,
                    },
                },
            )
            binding = run_campaign_module.load_campaign_policy(
                str(
                    ROOT
                    / "configs"
                    / "campaign_policies"
                    / "quiet_mac_p2_production.json"
                )
            )
            anchor = {
                "schema_version": "joulewise.cooldown_anchor.v1",
                "source_kind": "neg8_reference_start",
                "bundle_id": "p2015-neg8-reference-start",
                "policy_sha256": binding.sha256,
                "baseline": {
                    **contaminated,
                    "power_w_mean": 0.2,
                    "idle_window_suspect": False,
                },
                "eligibility": {
                    "eligible": True,
                    "provenance_present": True,
                },
                "environment_snapshot_sha256": "a" * 64,
                "immutable_after_freeze": True,
            }
            provenance_path = root / "campaign_manifests" / "session.json"
            provenance_path.parent.mkdir()
            clock = FakeClock()
            telemetry = CooldownTelemetry(clock)
            with (
                patch("joulewise.clock.SystemClock", return_value=clock),
                patch(
                    "joulewise.adapters.resolve_telemetry",
                    return_value=(telemetry, None),
                ),
            ):
                note = run_campaign_module.campaign_cooldown_before_member(
                    previous_info=previous_info,
                    previous_evaluation=previous,
                    following_info=following_info,
                    provenance_path=provenance_path,
                    session_id="session",
                    policy_binding=binding,
                    frozen_anchor=anchor,
                )

        self.assertEqual(note["result"], "recovered")
        self.assertEqual(note["reference_selection"], "frozen_clean_anchor")
        self.assertFalse(note["reference_eligibility"]["eligible"])
        self.assertEqual(note["reference_power_w"], 0.2)
        self.assertGreaterEqual(note["window_coverage_s"], 30.0)
        self.assertTrue(note["thermal_nominal"])
        self.assertEqual(
            note["anchor_provenance"]["bundle_id"],
            "p2015-neg8-reference-start",
        )

    def test_physical_repetitions_receive_distinct_cooldown_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            config_dir = root / "configs"
            runs_dir = root / "runs"
            config_dir.mkdir()
            config_path = write_config(
                config_dir, "three.json", "three", repetitions=3
            )
            write_experiment(
                runs_dir, "three", 3, config_path=config_path
            )
            manifest_path = runs_dir / "experiments" / "three.json"
            manifest = json.loads(manifest_path.read_text())
            manifest["cooldown"] = [
                {"after_member": "three__r1", "result": "recovered"},
                {"after_member": "three__r2", "result": "cap_hit"},
            ]
            manifest_path.write_text(json.dumps(manifest) + "\n")
            info = run_campaign_module.load_config_info(config_path)
            self.assertIsInstance(info, run_campaign_module.ConfigInfo)
            binding = run_campaign_module.load_campaign_policy(
                str(TEST_CAMPAIGN_POLICY)
            )
            provenance_path, _provenance = run_campaign_module.new_campaign_provenance(
                config_dir, runs_dir, None, binding
            )
            first = {
                **run_campaign_module._cooldown_policy_decision_surface(
                    binding.policy.cooldown
                ),
                "result": "first_run_exempt",
                "session_id": "session",
                "following_run_id": "three__r1",
            }
            evidence = run_campaign_module._physical_cooldown_evidence_for_config(
                info,
                runs_dir,
                first,
                provenance_path,
                binding.policy.cooldown,
            )

        self.assertEqual(evidence["three__r1"]["result"], "first_run_exempt")
        self.assertEqual(evidence["three__r2"]["result"], "recovered")
        self.assertEqual(evidence["three__r3"]["result"], "cap_hit")
        self.assertNotEqual(evidence["three__r2"], evidence["three__r1"])
        self.assertNotEqual(evidence["three__r3"], evidence["three__r1"])

    def test_axi_multi_entry_campaign_records_gate_before_entry_two(self) -> None:
        state = run_campaign_module.load_analysis_manifest(
            ROOT / "tests" / "fixtures" / "axi_ap_spec"
        )
        self.assertIsNotNone(state)
        binding = run_campaign_module.load_campaign_policy(
            str(TEST_CAMPAIGN_POLICY)
        )
        with tempfile.TemporaryDirectory() as tmp:
            runs_dir = Path(tmp) / "runs"
            result = run_campaign_module.run_axi_spec_campaign(
                run_campaign_module.argparse.Namespace(
                    dry_run=False,
                    cli_cmd=None,
                    arm_quiet_mode=False,
                    arm_countdown_s=0,
                    environment_override=None,
                ),
                state,
                runs_dir=runs_dir,
                policy_binding=binding,
            )
            manifests = list((runs_dir / "campaign_manifests").glob("*.json"))
            self.assertEqual(len(manifests), 1)
            provenance = json.loads(manifests[0].read_text())

        self.assertEqual(result, 0)
        self.assertGreaterEqual(len(provenance["members"]), 2)
        first = provenance["members"][0]["physical_members"][0]
        second = provenance["members"][1]["physical_members"][0]
        self.assertEqual(
            first["preceding_campaign_cooldown"]["result"],
            "first_run_exempt",
        )
        self.assertNotEqual(
            second["preceding_campaign_cooldown"]["result"],
            "first_run_exempt",
        )
        self.assertEqual(len(provenance["cooldown_gates"]), 3)

    def test_anchor_freezes_first_eligible_repetition_in_execution_order(self) -> None:
        binding = run_campaign_module.load_campaign_policy(
            str(
                ROOT
                / "configs"
                / "campaign_policies"
                / "quiet_mac_p2_production.json"
            )
        )
        info = run_campaign_module.ConfigInfo(
            path=BASE_CONFIG,
            run_id="multi",
            raw_run_id="multi",
            repetitions=3,
        )
        clean_baseline = {
            "power_w_mean": 5.0,
            "power_w_stddev": 0.0,
            "duration_s": 30.0,
            "sample_count": 30,
            "telemetry_backend": "powermetrics",
            "idle_window_suspect": False,
        }
        clean_metadata = {
            "campaign_policy": {"sha256": binding.sha256},
            "environment_admission": {
                "critical_environment_passed": True,
                "decision": "admitted",
                "reference_provenance_present": True,
                "per_run_environment_evaluation": {
                    "snapshot_sha256": "a" * 64
                },
            },
        }
        r1 = run_campaign_module.MemberEvaluation(
            bundle_id="multi__r1",
            bundle_path=Path("multi__r1"),
            config_name="multi.json",
            status="succeeded",
            strict_valid=True,
            summary={"idle_baseline": clean_baseline},
            metadata=clean_metadata,
        )
        r3 = run_campaign_module.MemberEvaluation(
            bundle_id="multi__r3",
            bundle_path=Path("multi__r3"),
            config_name="multi.json",
            status="succeeded",
            strict_valid=True,
            summary={
                "idle_baseline": {
                    **clean_baseline,
                    "idle_window_suspect": True,
                }
            },
            metadata={
                **clean_metadata,
                "environment_admission": {
                    **clean_metadata["environment_admission"],
                    "decision": "flagged",
                },
            },
        )
        anchor = run_campaign_module._first_eligible_cooldown_anchor(
            [r1, r3],
            info,
            binding,
            source_kind="first_admission_passing_baseline",
        )
        self.assertIsNotNone(anchor)
        self.assertEqual(anchor["bundle_id"], "multi__r1")

    def test_environment_admission_claim_reason_is_not_cleared_by_waiver(self) -> None:
        summary = {
            "window_evidence_precheck": {
                "gross_request": {
                    "eligible": False,
                    "reasons": ["environment_admission_failed"],
                },
                "idle_subtracted_request": {
                    "eligible": False,
                    "reasons": ["environment_admission_failed"],
                },
                "throughput": {
                    "eligible": False,
                    "reasons": ["environment_admission_failed"],
                },
            }
        }
        waiver = run_campaign_module.Waiver(
            target_kind="bundle_id",
            target="flagged",
            reason="collection-only review",
            approver="owner",
            timestamp="2026-07-17T00:00:00Z",
            scope="any",
        )
        evaluation = run_campaign_module.MemberEvaluation(
            bundle_id="flagged",
            bundle_path=Path("flagged"),
            config_name="flagged.json",
            status="succeeded",
            strict_valid=True,
            claim_evidence_flags=run_campaign_module.claim_evidence_flags(summary),
            waiver=waiver,
            summary=summary,
        )
        self.assertIn(
            "environment_admission_failed",
            evaluation.unwaived_claim_evidence_flags(),
        )

    def test_doctor_config_warning_gate_blocks_unacknowledged_campaign(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            config_dir = tmp_path / "configs"
            runs_dir = tmp_path / "runs"
            config_dir.mkdir()
            config_path = write_config(config_dir, "warn.json", "warn")
            payload = json.loads(config_path.read_text(encoding="utf-8"))
            payload["workload_profile"]["output_tokenz"] = 64
            config_path.write_text(json.dumps(payload) + "\n", encoding="utf-8")
            sentinel = tmp_path / "sentinel"
            fake_cli = make_fake_cli(tmp_path, sentinel)

            result = run_campaign(
                config_dir,
                runs_dir,
                cli_cmd=cli_cmd_for(fake_cli),
            )

            self.assertEqual(result.returncode, 1, result.stderr)
            self.assertFalse(sentinel.exists())
            self.assertIn("DOCTOR CONFIG PREFLIGHT: 1 warning(s), unacknowledged", result.stdout)
            verdict = read_all_jsonl(runs_dir / "campaign_log.jsonl")[-1]
            self.assertEqual(verdict["collection"]["verdict"], "invalid")
            self.assertEqual(verdict["claim_readiness"]["verdict"], "not_assessed")
            preflight = verdict["preflight"]
            self.assertEqual(preflight["schema_version"], "joulewise.doctor.v1")
            acknowledgement = preflight["config_warning_acknowledgement"]
            self.assertTrue(acknowledgement["required"])
            self.assertFalse(acknowledgement["acknowledged"])
            self.assertEqual(acknowledgement["warnings"][0]["path"], "workload_profile.output_tokenz")

    def test_doctor_config_warning_acknowledgement_is_logged_and_allows_campaign(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            config_dir = tmp_path / "configs"
            runs_dir = tmp_path / "runs"
            config_dir.mkdir()
            config_path = write_config(config_dir, "warn.json", "warn")
            payload = json.loads(config_path.read_text(encoding="utf-8"))
            payload["sampling"]["power_hzz"] = 10.0
            config_path.write_text(json.dumps(payload) + "\n", encoding="utf-8")
            fake_cli = make_fake_cli(tmp_path)

            result = run_campaign(
                config_dir,
                runs_dir,
                cli_cmd=cli_cmd_for(fake_cli),
                ack_config_warnings=True,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("DOCTOR CONFIG PREFLIGHT: 1 warning(s), acknowledged", result.stdout)
            verdict = read_all_jsonl(runs_dir / "campaign_log.jsonl")[-1]
            self.assertEqual(verdict["collection"]["verdict"], "usable")
            acknowledgement = verdict["preflight"]["config_warning_acknowledgement"]
            self.assertTrue(acknowledgement["acknowledged"])
            self.assertEqual(acknowledgement["mechanism"], "--ack-config-warnings")

    def test_discover_configs_excludes_order_and_analysis_manifest_sidecars(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            config_dir = Path(tmp)
            config = write_config(config_dir, "cell.json", "cell")
            (config_dir / "order_manifest.json").write_text("{}\n", encoding="utf-8")
            (config_dir / "analysis_manifest.json").write_text("{}\n", encoding="utf-8")

            self.assertEqual(run_campaign_module.discover_configs(config_dir), [config])

    def test_dry_run_executes_nothing_and_reports_plan(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            config_dir = tmp_path / "configs"
            runs_dir = tmp_path / "runs"
            config_dir.mkdir()
            config_path = write_config(config_dir, "one.json", "one", repetitions=5)
            sentinel = tmp_path / "sentinel"
            fake_cli = make_fake_cli(tmp_path, sentinel)
            cli_cmd = cli_cmd_for(fake_cli)

            result = run_campaign(
                config_dir,
                runs_dir,
                cli_cmd=cli_cmd,
                dry_run=True,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertFalse(sentinel.exists())
            self.assertIn("Config files to execute:", result.stdout)
            self.assertIn(str(config_path), result.stdout)
            self.assertIn("Dry run", result.stdout)
            self.assertIn("dry_run one: would run", result.stdout)
            self.assertIn(str(fake_cli), result.stdout)
            self.assertIn(rendered_cli_command(cli_cmd, config_path, runs_dir), result.stdout)
            self.assertFalse((runs_dir / "campaign_log.jsonl").exists())

    def test_resume_skip_complete_experiment_records_member_counts(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            config_dir = tmp_path / "configs"
            runs_dir = tmp_path / "runs"
            config_dir.mkdir()
            config_path = write_config(
                config_dir, "complete.json", "complete-exp", repetitions=5
            )
            write_experiment(
                runs_dir, "complete-exp", 5, config_path=config_path
            )
            sentinel = tmp_path / "sentinel"
            fake_cli = make_fake_cli(tmp_path, sentinel)

            result = run_campaign(
                config_dir,
                runs_dir,
                cli_cmd=cli_cmd_for(fake_cli),
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertFalse(sentinel.exists())
            self.assertIn("skipped complete-exp", result.stdout)
            rows = read_jsonl(runs_dir / "campaign_log.jsonl")
            self.assertEqual([row["status"] for row in rows], ["skipped"])
            self.assertEqual(rows[0]["members_succeeded"], 5)
            self.assertEqual(rows[0]["members_total"], 5)

    def test_unvalidated_existing_summary_is_not_skippable(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            config_dir = tmp_path / "configs"
            runs_dir = tmp_path / "runs"
            config_dir.mkdir()
            write_config(config_dir, "complete.json", "complete")
            write_single_bundle(runs_dir, "complete")
            summary_path = runs_dir / "complete" / "summary_metrics.json"
            summary = json.loads(summary_path.read_text(encoding="utf-8"))
            summary["gross_energy_j"] = summary["gross_energy_j"] + 1.0
            summary_path.write_text(json.dumps(summary) + "\n", encoding="utf-8")
            fake_cli = make_fake_cli(tmp_path)

            result = run_campaign(config_dir, runs_dir, cli_cmd=cli_cmd_for(fake_cli))

            self.assertEqual(result.returncode, 1)
            self.assertIn("not skippable", result.stderr)
            self.assertIn("fresh re-reduction", result.stderr)
            self.assertFalse((runs_dir / "order.log").exists())
            rows = read_jsonl(runs_dir / "campaign_log.jsonl")
            self.assertEqual(rows[0]["status"], "failed")
            self.assertFalse(rows[0]["members"][0]["strict_valid"])

    def test_skipped_experiment_with_failed_member_fails_campaign(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            config_dir = tmp_path / "configs"
            runs_dir = tmp_path / "runs"
            config_dir.mkdir()
            config_path = write_config(
                config_dir,
                "failed-member.json",
                "failed-member-exp",
                repetitions=5,
            )
            write_experiment(
                runs_dir,
                "failed-member-exp",
                5,
                statuses=["succeeded", "succeeded", "failed", "succeeded", "succeeded"],
                config_path=config_path,
            )
            sentinel = tmp_path / "sentinel"
            fake_cli = make_fake_cli(tmp_path, sentinel)

            result = run_campaign(
                config_dir,
                runs_dir,
                cli_cmd=cli_cmd_for(fake_cli),
            )

            self.assertEqual(result.returncode, 1)
            self.assertFalse(sentinel.exists())
            self.assertIn("not skippable", result.stderr)
            self.assertIn("failed-member-exp__r3", result.stderr)
            rows = read_jsonl(runs_dir / "campaign_log.jsonl")
            self.assertEqual(rows[0]["status"], "failed")
            self.assertEqual(rows[0]["members_succeeded"], 4)
            self.assertEqual(rows[0]["members_total"], 5)

    def test_claim_waiver_is_visible_without_changing_usable_collection(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            config_dir = tmp_path / "configs"
            runs_dir = tmp_path / "runs"
            waivers = tmp_path / "waivers.json"
            config_dir.mkdir()
            write_config(config_dir, "01-good.json", "good")
            write_config(config_dir, "02-idle.json", "idle")
            write_single_bundle(runs_dir, "good")
            write_single_bundle(runs_dir, "idle", idle_window_suspect=True)
            waivers.write_text(
                json.dumps(
                    [
                        {
                            "bundle_id": "idle",
                            "reason": "manual idle-window review accepted",
                            "approver": "council",
                            "timestamp": "2026-07-08T00:00:00Z",
                            "scope": "idle_window_suspect",
                        }
                    ]
                )
                + "\n",
                encoding="utf-8",
            )
            fake_cli = make_fake_cli(tmp_path)

            result = run_campaign(
                config_dir,
                runs_dir,
                cli_cmd=cli_cmd_for(fake_cli),
                waivers=waivers,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("COLLECTION VERDICT:", result.stdout)
            self.assertIn("verdict: usable", result.stdout)
            rows = read_jsonl(runs_dir / "campaign_log.jsonl")
            self.assertEqual([row["status"] for row in rows], ["skipped", "skipped"])
            self.assertEqual(rows[1]["members"][0]["collection_classification"], "usable")
            self.assertEqual(rows[1]["members"][0]["claim_evidence_classification"], "flagged")
            self.assertEqual(rows[1]["members"][0]["waiver"]["scope"], "idle_window_suspect")
            all_rows = read_all_jsonl(runs_dir / "campaign_log.jsonl")
            verdict = all_rows[-1]
            self.assertEqual(verdict["record_type"], "campaign_verdict")
            self.assertEqual(verdict["collection"]["verdict"], "usable")
            self.assertEqual(
                verdict["collection"]["categories"]["usable"], ["good", "idle"]
            )
            self.assertEqual(verdict["collection"]["categories"]["waived"], [])
            self.assertEqual(verdict["claim_readiness"]["verdict"], "not_assessed")

    def test_waiver_target_namespace_is_exact_and_does_not_poison_collection(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            config_dir = tmp_path / "configs"
            runs_dir = tmp_path / "runs"
            waivers = tmp_path / "waivers.json"
            config_dir.mkdir()
            write_config(config_dir, "good.json", "bad")
            write_single_bundle(runs_dir, "bad", idle_window_suspect=True)
            waivers.write_text(
                json.dumps(
                    [
                        {
                            "bundle_id": "good",
                            "reason": "wrong namespace must not match run_id or config",
                            "approver": "council",
                            "timestamp": "2026-07-08T00:00:00Z",
                            "scope": "any",
                        }
                    ]
                )
                + "\n",
                encoding="utf-8",
            )
            fake_cli = make_fake_cli(tmp_path)

            result = run_campaign(
                config_dir,
                runs_dir,
                cli_cmd=cli_cmd_for(fake_cli),
                waivers=waivers,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            rows = read_jsonl(runs_dir / "campaign_log.jsonl")
            self.assertEqual(rows[0]["status"], "skipped")
            self.assertIsNone(rows[0]["members"][0].get("waiver"))

    def test_waiver_unknown_scope_class_fails_at_load(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            config_dir = tmp_path / "configs"
            runs_dir = tmp_path / "runs"
            waivers = tmp_path / "waivers.json"
            config_dir.mkdir()
            write_config(config_dir, "idle.json", "idle")
            write_single_bundle(runs_dir, "idle", idle_window_suspect=True)
            waivers.write_text(
                json.dumps(
                    [
                        {
                            "bundle_id": "idle",
                            "reason": "typo scope must fail closed",
                            "approver": "council",
                            "timestamp": "2026-07-08T00:00:00Z",
                            "scope": "idle_window_suspect,not_a_real_class",
                        }
                    ]
                )
            )
            fake_cli = make_fake_cli(tmp_path)
            result = run_campaign(
                config_dir,
                runs_dir,
                cli_cmd=cli_cmd_for(fake_cli),
                waivers=waivers,
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("unknown scope class", result.stdout + result.stderr)

    def test_unmatched_claim_waiver_scope_does_not_change_collection(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            config_dir = tmp_path / "configs"
            runs_dir = tmp_path / "runs"
            waivers = tmp_path / "waivers.json"
            config_dir.mkdir()
            write_config(config_dir, "idle.json", "idle")
            write_single_bundle(runs_dir, "idle", idle_window_suspect=True)
            waivers.write_text(
                json.dumps(
                    [
                        {
                            "bundle_id": "idle",
                            "reason": "wrong failure class",
                            "approver": "council",
                            "timestamp": "2026-07-08T00:00:00Z",
                            "scope": "status_failed",
                        }
                    ]
                )
                + "\n",
                encoding="utf-8",
            )
            fake_cli = make_fake_cli(tmp_path)

            result = run_campaign(
                config_dir,
                runs_dir,
                cli_cmd=cli_cmd_for(fake_cli),
                waivers=waivers,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            rows = read_jsonl(runs_dir / "campaign_log.jsonl")
            self.assertEqual(rows[0]["status"], "skipped")
            self.assertEqual(
                rows[0]["members"][0]["collection_classification"], "usable"
            )
            self.assertEqual(
                rows[0]["members"][0]["claim_evidence_classification"], "flagged"
            )
            self.assertIn(
                "idle_window_suspect",
                rows[0]["members"][0]["claim_evidence_flags"],
            )

    def test_duplicate_waiver_targets_fail_closed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            config_dir = tmp_path / "configs"
            runs_dir = tmp_path / "runs"
            waivers = tmp_path / "waivers.json"
            config_dir.mkdir()
            write_config(config_dir, "good.json", "good")
            entry = {
                "config": "good.json",
                "reason": "duplicate",
                "approver": "council",
                "timestamp": "2026-07-08T00:00:00Z",
                "scope": "any",
            }
            duplicate = {**entry, "config": "good"}
            waivers.write_text(json.dumps([entry, duplicate]) + "\n", encoding="utf-8")

            result = run_campaign(config_dir, runs_dir, waivers=waivers)

            self.assertEqual(result.returncode, 2)
            self.assertIn("duplicate waiver target", result.stderr)

    def test_idle_suspect_member_is_collection_usable_but_claim_evidence_flagged(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            config_dir = tmp_path / "configs"
            runs_dir = tmp_path / "runs"
            config_dir.mkdir()
            write_config(config_dir, "idle.json", "idle")
            write_single_bundle(runs_dir, "idle", idle_window_suspect=True)
            fake_cli = make_fake_cli(tmp_path)

            result = run_campaign(config_dir, runs_dir, cli_cmd=cli_cmd_for(fake_cli))

            self.assertEqual(result.returncode, 0, result.stderr)
            rows = read_jsonl(runs_dir / "campaign_log.jsonl")
            self.assertEqual(rows[0]["status"], "skipped")
            member = rows[0]["members"][0]
            self.assertEqual(member["collection_classification"], "usable")
            self.assertEqual(member["claim_evidence_classification"], "flagged")
            self.assertEqual(member["collection_integrity_flags"], [])
            self.assertIn("idle_window_suspect", member["claim_evidence_flags"])

    def test_all_waived_campaign_is_invalid_not_partial(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            config_dir = tmp_path / "configs"
            runs_dir = tmp_path / "runs"
            waivers = tmp_path / "waivers.json"
            config_dir.mkdir()
            write_config(config_dir, "idle.json", "idle")
            write_single_bundle(runs_dir, "idle")
            summary_path = runs_dir / "idle" / "summary_metrics.json"
            summary = json.loads(summary_path.read_text(encoding="utf-8"))
            summary["gross_energy_j"] += 1.0
            summary_path.write_text(json.dumps(summary) + "\n", encoding="utf-8")
            waivers.write_text(
                json.dumps(
                    [
                        {
                            "bundle_id": "idle",
                            "reason": "strict-invalid member retained for collection audit",
                            "approver": "council",
                            "timestamp": "2026-07-08T00:00:00Z",
                            "scope": "strict_invalid",
                        }
                    ]
                )
                + "\n",
                encoding="utf-8",
            )
            fake_cli = make_fake_cli(tmp_path)

            result = run_campaign(
                config_dir,
                runs_dir,
                cli_cmd=cli_cmd_for(fake_cli),
                waivers=waivers,
            )

            self.assertEqual(result.returncode, 1)
            all_rows = read_all_jsonl(runs_dir / "campaign_log.jsonl")
            verdict = all_rows[-1]
            self.assertEqual(verdict["collection"]["verdict"], "invalid")
            self.assertEqual(verdict["collection"]["categories"]["waived"], ["idle"])

    def test_one_bundle_campaign_is_usable_and_claim_readiness_not_assessed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            config_dir = tmp_path / "configs"
            runs_dir = tmp_path / "runs"
            config_dir.mkdir()
            write_config(config_dir, "one.json", "one")
            fake_cli = make_fake_cli(tmp_path)

            result = run_campaign(config_dir, runs_dir, cli_cmd=cli_cmd_for(fake_cli))

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("COLLECTION VERDICT:", result.stdout)
            self.assertIn("CLAIM-INPUT READINESS:", result.stdout)
            self.assertNotIn("publish" + "able", result.stdout)
            all_rows = read_all_jsonl(runs_dir / "campaign_log.jsonl")
            self.assertEqual(all_rows[-1]["record_type"], "campaign_verdict")
            self.assertEqual(
                all_rows[-1]["schema_version"], "joulewise.campaign_verdict.v2"
            )
            self.assertEqual(all_rows[-1]["collection"]["verdict"], "usable")
            self.assertEqual(
                all_rows[-1]["claim_readiness"]["verdict"], "not_assessed"
            )
            self.assertEqual(
                all_rows[-1]["collection"]["categories"]["usable"], ["one"]
            )
            self.assertEqual(
                all_rows[-1]["collection"]["categories"]["failed"], []
            )

    def test_current_era_claim_eligibility_only_never_becomes_ready(self) -> None:
        contrast = {
            "contrast_id": "ctr-b-minus-a",
            "metric": {"name": "gross_energy_j", "metric_tag": "gross_request"},
            "cell_a_id": "cell-a",
            "cell_b_id": "cell-b",
            "block_ids": ["block-1"],
        }
        state = run_campaign_module.AnalysisManifestState(
            path=Path("analysis_manifest.json"),
            raw={
                "design": {"sampling_plan": {"planned_n_blocks": 1}},
                "entries": [
                    {"run_id": "a", "block_id": "block-1", "cell_id": "cell-a"},
                    {"run_id": "b", "block_id": "block-1", "cell_id": "cell-b"},
                ],
                "contrasts": [contrast],
            },
            manifest_id="am-fixture",
            file_sha256="fixture",
        )
        legacy_named_summary = {
            "gross_energy_j": 1.0,
            "claim_eligibility": {
                "gross_request": {"eligible": True, "reasons": []}
            },
            "measurement_quality": {"idle_window_suspect": False},
        }
        evaluations = [
            run_campaign_module.MemberEvaluation(
                bundle_id=bundle_id,
                bundle_path=Path(bundle_id),
                config_name=f"{bundle_id}.json",
                status="succeeded",
                strict_valid=True,
                summary=legacy_named_summary,
                preceding_campaign_cooldown=cooldown,
            )
            for bundle_id, cooldown in (
                ("a", {"result": "first_run_exempt"}),
                (
                    "b",
                    {
                        "result": "recovered",
                        "raw_artifact": {
                            "path": "raw/fixture.jsonl",
                            "sha256": "fixture",
                            "records": 1,
                        },
                    },
                ),
            )
        ]

        readiness = run_campaign_module.claim_readiness_for(
            state, "usable", evaluations
        )

        self.assertEqual(readiness["verdict"], "not_ready_for_analysis")
        self.assertIn("window_evidence_precheck_missing", readiness["reasons"])

    def test_metric_specific_precheck_routing_has_no_generic_request_alias(self) -> None:
        gross = {"eligible": True, "reasons": []}
        idle = {"eligible": False, "reasons": ["drift_term_unknown"]}
        summary = {
            "window_evidence_precheck": {
                "gross_request": gross,
                "idle_subtracted_request": idle,
            }
        }

        self.assertIs(
            run_campaign_module._precheck_for_contrast(
                summary,
                {"metric": {"name": "gross_energy_j", "metric_tag": "gross_request"}},
            ),
            gross,
        )
        self.assertIs(
            run_campaign_module._precheck_for_contrast(
                summary,
                {
                    "metric": {
                        "name": "idle_subtracted_energy_j",
                        "metric_tag": "idle_request",
                    }
                },
            ),
            idle,
        )
        self.assertNotIn("request", summary["window_evidence_precheck"])

        mutated_summary = {
            "gross_energy_j": 1.0,
            "idle_subtracted_energy_j": 1.0,
            "window_evidence_precheck": {
                "request": {"eligible": False, "reasons": ["drift_term_unknown"]},
                "gross_request": gross,
                "idle_subtracted_request": idle,
            },
            "measurement_quality": {"idle_window_suspect": True},
        }
        evaluation = run_campaign_module.MemberEvaluation(
            bundle_id="member",
            bundle_path=Path("member"),
            config_name="member.json",
            status="succeeded",
            strict_valid=True,
            summary=mutated_summary,
            preceding_campaign_cooldown={"result": "first_run_exempt"},
        )
        gross_reasons = run_campaign_module._member_readiness_reasons(
            evaluation,
            {"metric": {"name": "gross_energy_j", "metric_tag": "gross_request"}},
        )
        idle_reasons = run_campaign_module._member_readiness_reasons(
            evaluation,
            {
                "metric": {
                    "name": "idle_subtracted_energy_j",
                    "metric_tag": "idle_request",
                }
            },
        )
        self.assertNotIn("idle_window_suspect", gross_reasons)
        self.assertNotIn("drift_term_unknown", gross_reasons)
        self.assertIn("idle_window_suspect", idle_reasons)
        self.assertIn("drift_term_unknown", idle_reasons)

    def test_missing_nan_and_infinite_metric_fail_readiness(self) -> None:
        contrast = {
            "metric": {"name": "gross_energy_j", "metric_tag": "gross_request"}
        }
        for label, value in (
            ("missing", None),
            ("null", None),
            ("nan", float("nan")),
            ("inf", float("inf")),
        ):
            with self.subTest(value=label):
                summary = {
                    "window_evidence_precheck": {
                        "gross_request": {"eligible": True, "reasons": []}
                    },
                    "measurement_quality": {"idle_window_suspect": False},
                }
                if label != "missing":
                    summary["gross_energy_j"] = value
                evaluation = run_campaign_module.MemberEvaluation(
                    bundle_id="member",
                    bundle_path=Path("member"),
                    config_name="member.json",
                    status="succeeded",
                    strict_valid=True,
                    summary=summary,
                    preceding_campaign_cooldown={"result": "first_run_exempt"},
                )

                reasons = run_campaign_module._member_readiness_reasons(
                    evaluation, contrast
                )

                self.assertIn("metric_missing_or_nonfinite", reasons)

    def test_missing_campaign_cooldown_evidence_fails_closed_with_named_reason(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            config_dir = tmp_path / "configs"
            runs_dir = tmp_path / "runs"
            config_dir.mkdir()
            write_strict_analysis_campaign(config_dir, runs_dir)

            result = run_campaign(config_dir, runs_dir)

            self.assertEqual(result.returncode, 0, result.stderr)
            verdict = read_all_jsonl(runs_dir / "campaign_log.jsonl")[-1]
            self.assertEqual(verdict["collection"]["verdict"], "usable")
            readiness = verdict["claim_readiness"]
            self.assertEqual(readiness["verdict"], "not_ready_for_analysis")
            self.assertIn("campaign_cooldown_evidence_missing", readiness["reasons"])
            self.assertNotIn("idle_window_suspect", readiness["reasons"])
            self.assertEqual(readiness["ready_contrast_ids"], [])

    def test_cooldown_cap_hit_propagates_without_poisoning_collection(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            config_dir = tmp_path / "configs"
            runs_dir = tmp_path / "runs"
            config_dir.mkdir()
            manifest = write_strict_analysis_campaign(config_dir, runs_dir)
            evidence = {
                entry["run_id"]: "recovered" for entry in manifest["entries"]
            }
            evidence[manifest["entries"][0]["run_id"]] = "first_run_exempt"
            evidence[manifest["entries"][1]["run_id"]] = "cap_hit"
            write_prior_campaign_provenance(
                runs_dir,
                evidence,
                analysis_manifest_id(config_dir),
            )

            result = run_campaign(config_dir, runs_dir)

            self.assertEqual(result.returncode, 0, result.stderr)
            verdict = read_all_jsonl(runs_dir / "campaign_log.jsonl")[-1]
            self.assertEqual(verdict["collection"]["verdict"], "usable")
            self.assertEqual(
                verdict["claim_readiness"]["verdict"], "not_ready_for_analysis"
            )
            self.assertIn("cooldown_cap_hit", verdict["claim_readiness"]["reasons"])

    def test_explicit_campaign_cooldown_evidence_allows_ready_for_analysis(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            config_dir = tmp_path / "configs"
            runs_dir = tmp_path / "runs"
            config_dir.mkdir()
            manifest = write_strict_analysis_campaign(config_dir, runs_dir)
            evidence = {
                entry["run_id"]: "recovered" for entry in manifest["entries"]
            }
            evidence[manifest["entries"][0]["run_id"]] = "first_run_exempt"
            write_prior_campaign_provenance(
                runs_dir,
                evidence,
                analysis_manifest_id(config_dir),
            )

            result = run_campaign(config_dir, runs_dir)

            self.assertEqual(result.returncode, 0, result.stderr)
            verdict = read_all_jsonl(runs_dir / "campaign_log.jsonl")[-1]
            self.assertEqual(
                verdict["claim_readiness"]["verdict"], "ready_for_analysis"
            )
            self.assertEqual(
                set(verdict["claim_readiness"]["ready_contrast_ids"]),
                {contrast["contrast_id"] for contrast in manifest["contrasts"]},
            )
            sampling_audit = verdict["sampling_audit"]
            self.assertEqual(
                set(sampling_audit),
                {
                    "design",
                    "planned_n_blocks",
                    "registered_bundle_ids",
                    "unregistered_matching_bundle_ids",
                    "valid_replacements",
                    "top_up_suspected",
                },
            )
            self.assertEqual(sampling_audit["unregistered_matching_bundle_ids"], [])
            self.assertEqual(sampling_audit["valid_replacements"], [])
            self.assertIs(sampling_audit["top_up_suspected"], False)
            self.assertNotIn("detection_scope", sampling_audit)
            self.assertNotIn("reasons", sampling_audit)

    def test_cleanup_suspect_waiver_is_visible_but_never_clears_readiness(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            config_dir = tmp_path / "configs"
            runs_dir = tmp_path / "runs"
            waivers = tmp_path / "waivers.json"
            config_dir.mkdir()
            manifest = write_strict_analysis_campaign(config_dir, runs_dir)
            target = next(entry for entry in manifest["entries"] if entry["role"] == "condition")
            target_bundle = runs_dir / target["run_id"]
            shutil.rmtree(target_bundle)
            write_single_bundle(
                runs_dir,
                target["run_id"],
                config_path=config_dir / target["config"],
                runtime_cleanup_ok=False,
                remote_cleanup_failed=["/remote/tmp/joulewise-task"],
            )
            suspect_summary = json.loads(
                (target_bundle / "summary_metrics.json").read_text(encoding="utf-8")
            )
            self.assertEqual(suspect_summary["status"], "succeeded")
            self.assertGreater(suspect_summary["energy_request_j"], 0.0)
            evidence = {entry["run_id"]: "recovered" for entry in manifest["entries"]}
            evidence[manifest["entries"][0]["run_id"]] = "first_run_exempt"
            write_prior_campaign_provenance(
                runs_dir, evidence, analysis_manifest_id(config_dir)
            )

            unwaived = run_campaign(config_dir, runs_dir)

            self.assertEqual(unwaived.returncode, 0, unwaived.stderr)
            first_verdict = read_all_jsonl(runs_dir / "campaign_log.jsonl")[-1]
            self.assertEqual(first_verdict["collection"]["verdict"], "usable")
            self.assertEqual(
                first_verdict["claim_readiness"]["verdict"],
                "not_ready_for_analysis",
            )
            self.assertIn(
                "required_error_term_unknown",
                first_verdict["claim_readiness"]["reasons"],
            )
            first_member = next(
                member
                for member in first_verdict["members"]
                if member["bundle_id"] == target["run_id"]
            )
            self.assertEqual(first_member["status"], "succeeded")
            self.assertIs(first_member["runtime_cleanup_ok"], False)
            self.assertEqual(
                first_member["remote_cleanup_failed"],
                ["/remote/tmp/joulewise-task"],
            )
            self.assertEqual(
                first_member["claim_evidence_flags"],
                ["remote_cleanup_failed", "runtime_cleanup_ok"],
            )

            waivers.write_text(
                json.dumps(
                    [
                        {
                            "bundle_id": target["run_id"],
                            "reason": "cleanup residue reviewed and bounded",
                            "approver": "campaign-owner",
                            "timestamp": "2026-07-11T00:00:00Z",
                            "scope": "runtime_cleanup_ok,remote_cleanup_failed",
                        }
                    ]
                )
                + "\n",
                encoding="utf-8",
            )

            waived = run_campaign(config_dir, runs_dir, waivers=waivers)

            self.assertEqual(waived.returncode, 0, waived.stderr)
            second_verdict = read_all_jsonl(runs_dir / "campaign_log.jsonl")[-1]
            self.assertEqual(second_verdict["collection"]["verdict"], "usable")
            self.assertEqual(
                second_verdict["claim_readiness"]["verdict"],
                "not_ready_for_analysis",
            )
            self.assertIn(
                "required_error_term_unknown",
                second_verdict["claim_readiness"]["reasons"],
            )
            second_member = next(
                member
                for member in second_verdict["members"]
                if member["bundle_id"] == target["run_id"]
            )
            self.assertEqual(second_member["claim_evidence_classification"], "flagged")
            self.assertEqual(
                second_member["waiver"]["scope"],
                "runtime_cleanup_ok,remote_cleanup_failed",
            )
            provenance_rows = [
                json.loads(path.read_text(encoding="utf-8"))
                for path in (runs_dir / "campaign_manifests").glob("*.json")
            ]
            provenance_row = next(
                row
                for row in provenance_rows
                if any(
                    item.get("waiver") is not None
                    for member in row["members"]
                    for item in member.get("claim_evidence", [])
                )
            )
            recorded = next(
                item
                for member in provenance_row["members"]
                for item in member["claim_evidence"]
                if item["bundle_id"] == target["run_id"]
            )
            self.assertEqual(recorded["waiver"], second_member["waiver"])

    def test_cleanup_claim_waiver_does_not_skip_shakedown_or_backup(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            config_dir = tmp_path / "configs"
            runs_dir = tmp_path / "runs"
            waivers = tmp_path / "waivers.json"
            backup = tmp_path / "backup.sh"
            config_dir.mkdir()
            config_path = write_config(config_dir, "cleanup.json", "cleanup")
            write_single_bundle(
                runs_dir,
                "cleanup",
                config_path=config_path,
                runtime_cleanup_ok=False,
                remote_cleanup_failed=["/remote/tmp/joulewise-task"],
            )
            waivers.write_text(
                json.dumps(
                    [
                        {
                            "bundle_id": "cleanup",
                            "reason": "collection may continue after visible review",
                            "approver": "campaign-owner",
                            "timestamp": "2026-07-11T00:00:00Z",
                            "scope": "runtime_cleanup_ok,remote_cleanup_failed",
                        }
                    ]
                )
                + "\n",
                encoding="utf-8",
            )
            completed = subprocess.CompletedProcess([], 0)
            argv = [
                str(config_dir),
                "--runs-dir",
                str(runs_dir),
                "--backup",
                str(backup),
                "--shakedown-gate",
                "production_uncertainty_v1",
                "--waivers",
                str(waivers),
                "--campaign-policy",
                str(TEST_CAMPAIGN_POLICY),
            ]
            with (
                patch("run_campaign_module.validate_bundle", return_value=[]),
                patch("run_campaign_module.subprocess.run", return_value=completed),
                patch(
                    "run_campaign_module.assert_production_uncertainty",
                    return_value={"bundle_id": "cleanup", "request_eligible": True},
                ),
                patch("run_campaign_module.backup_runs", return_value=0) as backup_runs,
                redirect_stdout(io.StringIO()),
                redirect_stderr(io.StringIO()),
            ):
                result = run_campaign_module.main(argv)

            self.assertEqual(result, 0)
            backup_runs.assert_called_once_with(runs_dir, backup)
            rows = read_all_jsonl(runs_dir / "campaign_log.jsonl")
            gate = next(row for row in rows if row.get("record_type") == "shakedown_gate")
            campaign = next(row for row in rows if row.get("run_id") == "cleanup")
            self.assertEqual(gate["status"], "passed")
            self.assertEqual(campaign["status"], "skipped")
            self.assertEqual(
                campaign["members"][0]["collection_classification"], "usable"
            )
            self.assertEqual(
                campaign["members"][0]["claim_evidence_classification"], "flagged"
            )

    def test_ratio_readiness_reuses_engine_token_denominator_gate(self) -> None:
        ratio = {
            "form": "mean_of_request_ratios",
            "numerator_metric": "energy_request_j",
            "denominator": "runtime_observed_output_tokens",
            "denominator_unit": "token",
            "tokenizer_scope": "same_identity_required",
            "output_policy_scope": "same_policy_required",
        }
        contrast = {
            "contrast_id": "ratio-contrast",
            "metric": {
                "name": "energy_output_token_j",
                "metric_tag": "energy_output_token",
                "window_class": "idle_subtracted_request",
                "unit": "J/token",
                "ratio_estimand": ratio,
            },
            "cell_a_id": "cell-a",
            "cell_b_id": "cell-b",
            "block_ids": ["block-1"],
        }
        state = run_campaign_module.AnalysisManifestState(
            path=Path("analysis_manifest.json"),
            raw={
                "design": {"sampling_plan": {"planned_n_blocks": 1}},
                "entries": [
                    {"run_id": "a", "block_id": "block-1", "cell_id": "cell-a"},
                    {"run_id": "b", "block_id": "block-1", "cell_id": "cell-b"},
                ],
                "contrasts": [contrast],
            },
            manifest_id="ratio-fixture",
            file_sha256="fixture",
        )
        summary = {
            "energy_request_j": 2.0,
            "window_evidence_precheck": {
                "idle_subtracted_request": {"eligible": True, "reasons": []}
            },
            "measurement_quality": {"idle_window_suspect": False},
        }
        valid_provenance = {
            "output_tokens": 2,
            "token_count_source": "runtime_observed",
            "stop_reason": "requested_tokens_emitted",
            "output_policy": {
                "name": "fixed_budget_exact",
                "requested_tokens": 2,
                "sampler": None,
            },
            "tokenizer_identity": {"backend": "mock", "identifier": "tok"},
        }
        evaluations = [
            run_campaign_module.MemberEvaluation(
                bundle_id=bundle_id,
                bundle_path=Path(bundle_id),
                config_name=f"{bundle_id}.json",
                status="succeeded",
                strict_valid=True,
                summary=summary,
                ratio_token_provenance={
                    **valid_provenance,
                    **({"token_count_source": "config_fallback"} if bundle_id == "b" else {}),
                },
                preceding_campaign_cooldown={"result": "first_run_exempt"},
            )
            for bundle_id in ("a", "b")
        ]

        readiness = run_campaign_module.claim_readiness_for(
            state, "usable", evaluations
        )

        self.assertEqual(readiness["verdict"], "not_ready_for_analysis")
        self.assertIn("runtime_token_denominator_required", readiness["reasons"])
        self.assertNotIn("metric_missing_or_nonfinite", readiness["reasons"])
        self.assertNotIn("window_evidence_precheck_missing", readiness["reasons"])

    def test_existing_resume_provenance_does_not_shadow_invoked_cooldown_evidence(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            config_dir = tmp_path / "configs"
            runs_dir = tmp_path / "runs"
            config_dir.mkdir()
            manifest = write_strict_analysis_campaign(config_dir, runs_dir)
            first_contrast = manifest["contrasts"][0]
            first_inferential_entry = next(
                entry
                for entry in manifest["entries"]
                if entry["cell_id"] == first_contrast["cell_a_id"]
                and entry["block_id"] == first_contrast["block_ids"][0]
            )
            evidence = {first_inferential_entry["run_id"]: "first_run_exempt"}
            evidence.update(
                {
                    entry["run_id"]: "recovered"
                    for entry in manifest["entries"]
                    if entry["run_id"] != first_inferential_entry["run_id"]
                }
            )
            write_prior_campaign_provenance(
                runs_dir,
                evidence,
                analysis_manifest_id(config_dir),
            )
            manifest_dir = runs_dir / "campaign_manifests"
            (manifest_dir / "fixture.json").rename(
                manifest_dir / "campaign-00000000T000000000000Z-p0.json"
            )

            first_resume = run_campaign(config_dir, runs_dir)
            second_resume = run_campaign(config_dir, runs_dir)

            self.assertEqual(first_resume.returncode, 0, first_resume.stderr)
            self.assertEqual(second_resume.returncode, 0, second_resume.stderr)
            verdicts = [
                row
                for row in read_all_jsonl(runs_dir / "campaign_log.jsonl")
                if "claim_readiness" in row
            ]
            self.assertEqual(
                [row["claim_readiness"]["verdict"] for row in verdicts[-2:]],
                ["ready_for_analysis", "ready_for_analysis"],
            )
            resumed_provenance = [
                json.loads(path.read_text(encoding="utf-8"))
                for path in sorted(manifest_dir.glob("campaign-202*.json"))
            ]
            self.assertEqual(len(resumed_provenance), 2)
            for provenance in resumed_provenance:
                self.assertTrue(provenance["members"])
                self.assertTrue(
                    all(
                        member["execution"] == "existing"
                        and member["preceding_campaign_cooldown"] is None
                        for member in provenance["members"]
                    )
                )

    def test_non_invoked_provenance_cannot_originate_cooldown_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            config_dir = tmp_path / "configs"
            runs_dir = tmp_path / "runs"
            config_dir.mkdir()
            manifest = write_strict_analysis_campaign(config_dir)
            evidence = {
                entry["run_id"]: "recovered" for entry in manifest["entries"]
            }
            evidence[manifest["entries"][0]["run_id"]] = "first_run_exempt"
            write_prior_campaign_provenance(
                runs_dir,
                evidence,
                analysis_manifest_id(config_dir),
            )
            provenance_path = runs_dir / "campaign_manifests" / "fixture.json"
            provenance = json.loads(provenance_path.read_text(encoding="utf-8"))
            for member in provenance["members"]:
                member["execution"] = "existing"
            provenance_path.write_text(
                json.dumps(provenance) + "\n",
                encoding="utf-8",
            )

            self.assertEqual(
                run_campaign_module.prior_campaign_cooldown_evidence(
                    runs_dir, manifest["manifest_id"]
                ),
                {},
            )

    def test_recovered_cooldown_without_raw_provenance_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            config_dir = tmp_path / "configs"
            runs_dir = tmp_path / "runs"
            config_dir.mkdir()
            manifest = write_strict_analysis_campaign(config_dir, runs_dir)
            evidence = {
                entry["run_id"]: "recovered" for entry in manifest["entries"]
            }
            evidence[manifest["entries"][0]["run_id"]] = "first_run_exempt"
            write_prior_campaign_provenance(
                runs_dir,
                evidence,
                analysis_manifest_id(config_dir),
            )
            (runs_dir / "campaign_manifests" / "raw" / "fixture.jsonl").unlink()

            result = run_campaign(config_dir, runs_dir)

            self.assertEqual(result.returncode, 0, result.stderr)
            readiness = read_all_jsonl(runs_dir / "campaign_log.jsonl")[-1][
                "claim_readiness"
            ]
            self.assertEqual(readiness["verdict"], "not_ready_for_analysis")
            self.assertIn("campaign_cooldown_evidence_missing", readiness["reasons"])

    def test_nonexistent_nonhex_cooldown_descriptor_has_readiness_objection(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            runs_dir = Path(tmp) / "runs"
            evaluation = run_campaign_module.MemberEvaluation(
                bundle_id="member",
                bundle_path=runs_dir / "member",
                config_name="member.json",
                status="succeeded",
                strict_valid=True,
                summary={
                    "gross_energy_j": 1.0,
                    "window_evidence_precheck": {
                        "gross_request": {"eligible": True, "reasons": []}
                    },
                    "measurement_quality": {"idle_window_suspect": False},
                },
                preceding_campaign_cooldown={
                    "result": "recovered",
                    "raw_artifact": {
                        "path": "raw/nonexistent.jsonl",
                        "sha256": "not-a-hex-digest",
                        "records": 1,
                    },
                },
            )

            reasons = run_campaign_module._member_readiness_reasons(
                evaluation,
                {"metric": {"name": "gross_energy_j", "metric_tag": "gross_request"}},
            )

            self.assertNotEqual(reasons, [])
            self.assertIn("campaign_cooldown_evidence_missing", reasons)

    def test_fresh_cooldown_raw_provenance_is_reverified_at_verdict_time(self) -> None:
        for mutation in (
            "valid",
            "hash_mismatch",
            "count_mismatch",
            "malformed_jsonl",
        ):
            with self.subTest(mutation=mutation), tempfile.TemporaryDirectory() as tmp:
                runs_dir = Path(tmp) / "runs"
                provenance_path = runs_dir / "campaign_manifests" / "fresh.json"
                raw_artifact = run_campaign_module._write_campaign_cooldown_trace(
                    provenance_path,
                    "member",
                    [{"rolling_mean_power_w": 5.0}],
                )
                raw_path = provenance_path.parent / raw_artifact["path"]
                if mutation == "hash_mismatch":
                    raw_path.write_text('{"rolling_mean_power_w": 6.0}\n', encoding="utf-8")
                elif mutation == "count_mismatch":
                    raw_artifact["records"] = 2
                elif mutation == "malformed_jsonl":
                    payload = b'{"rolling_mean_power_w":\n'
                    raw_path.write_bytes(payload)
                    raw_artifact["sha256"] = hashlib.sha256(payload).hexdigest()
                evaluation = run_campaign_module.MemberEvaluation(
                    bundle_id="member",
                    bundle_path=runs_dir / "member",
                    config_name="member.json",
                    status="succeeded",
                    strict_valid=True,
                    summary={
                        "gross_energy_j": 1.0,
                        "window_evidence_precheck": {
                            "gross_request": {"eligible": True, "reasons": []}
                        },
                        "measurement_quality": {"idle_window_suspect": False},
                    },
                    preceding_campaign_cooldown={
                        "result": "recovered",
                        "raw_artifact": raw_artifact,
                    },
                )

                reasons = run_campaign_module._member_readiness_reasons(
                    evaluation,
                    {
                        "metric": {
                            "name": "gross_energy_j",
                            "metric_tag": "gross_request",
                        }
                    },
                )

                if mutation == "valid":
                    self.assertNotIn("campaign_cooldown_evidence_missing", reasons)
                else:
                    self.assertIn("campaign_cooldown_evidence_missing", reasons)

    def test_cooldown_provenance_symlink_loop_fails_closed(self) -> None:
        # Path.resolve() may raise (RuntimeError, or OSError ELOOP depending
        # on Python version) for a symlink loop; the verifier must return a
        # fail-closed False, never abort verdict construction.
        with tempfile.TemporaryDirectory() as tmp:
            manifest_dir = Path(tmp) / "campaign_manifests"
            raw_dir = manifest_dir / "raw"
            raw_dir.mkdir(parents=True)
            loop = raw_dir / "loop.jsonl"
            loop.symlink_to(loop)

            self.assertFalse(
                run_campaign_module.verify_cooldown_raw_provenance(
                    {
                        "result": "recovered",
                        "raw_artifact": {
                            "path": "raw/loop.jsonl",
                            "sha256": "0" * 64,
                            "records": 1,
                        },
                    },
                    manifest_dir,
                )
            )

    def test_resumed_cooldown_hash_and_count_mismatches_block_readiness(self) -> None:
        for mutation in ("hash_mismatch", "count_mismatch"):
            with self.subTest(mutation=mutation), tempfile.TemporaryDirectory() as tmp:
                tmp_path = Path(tmp)
                config_dir = tmp_path / "configs"
                runs_dir = tmp_path / "runs"
                config_dir.mkdir()
                manifest = write_strict_analysis_campaign(config_dir, runs_dir)
                evidence = {
                    entry["run_id"]: "recovered" for entry in manifest["entries"]
                }
                evidence[manifest["entries"][0]["run_id"]] = "first_run_exempt"
                write_prior_campaign_provenance(
                    runs_dir,
                    evidence,
                    analysis_manifest_id(config_dir),
                )
                provenance_path = runs_dir / "campaign_manifests" / "fixture.json"
                if mutation == "hash_mismatch":
                    (provenance_path.parent / "raw" / "fixture.jsonl").write_text(
                        '{"rolling_mean_power_w": 6.0}\n', encoding="utf-8"
                    )
                else:
                    provenance = json.loads(
                        provenance_path.read_text(encoding="utf-8")
                    )
                    for member in provenance["members"]:
                        raw_artifact = member["preceding_campaign_cooldown"].get(
                            "raw_artifact"
                        )
                        if raw_artifact is not None:
                            raw_artifact["records"] = 2
                    provenance_path.write_text(
                        json.dumps(provenance) + "\n", encoding="utf-8"
                    )

                result = run_campaign(config_dir, runs_dir)

                self.assertEqual(result.returncode, 0, result.stderr)
                readiness = read_all_jsonl(runs_dir / "campaign_log.jsonl")[-1][
                    "claim_readiness"
                ]
                self.assertEqual(readiness["verdict"], "not_ready_for_analysis")
                self.assertIn(
                    "campaign_cooldown_evidence_missing", readiness["reasons"]
                )

    def test_all_members_cannot_claim_one_session_first_run_exemption(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            config_dir = tmp_path / "configs"
            runs_dir = tmp_path / "runs"
            config_dir.mkdir()
            manifest = write_strict_analysis_campaign(config_dir, runs_dir)
            write_malformed_first_exemption_provenance(
                runs_dir, manifest, fan_out_one_note=False
            )

            result = run_campaign(config_dir, runs_dir)

            self.assertEqual(result.returncode, 0, result.stderr)
            readiness = read_all_jsonl(runs_dir / "campaign_log.jsonl")[-1][
                "claim_readiness"
            ]
            self.assertEqual(readiness["verdict"], "not_ready_for_analysis")
            self.assertIn("campaign_cooldown_evidence_missing", readiness["reasons"])

    def test_first_run_exemption_note_cannot_fan_out_to_unrelated_members(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            config_dir = tmp_path / "configs"
            runs_dir = tmp_path / "runs"
            config_dir.mkdir()
            manifest = write_strict_analysis_campaign(config_dir)
            write_malformed_first_exemption_provenance(
                runs_dir, manifest, fan_out_one_note=True
            )

            evidence = run_campaign_module.prior_campaign_cooldown_evidence(
                runs_dir, manifest["manifest_id"]
            )

            self.assertEqual(
                set(evidence),
                {entry["run_id"] for entry in manifest["entries"]},
            )
            self.assertTrue(
                all(note["result"] == "unknown" for note in evidence.values())
            )
            self.assertTrue(
                all("physical-session" in note["reason"] for note in evidence.values())
            )

    def test_analysis_manifest_config_hash_mismatch_refuses_execution(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            config_dir = tmp_path / "configs"
            runs_dir = tmp_path / "runs"
            sentinel = tmp_path / "invoked"
            config_dir.mkdir()
            manifest = write_strict_analysis_campaign(config_dir)
            config_path = config_dir / manifest["entries"][0]["config"]
            payload = json.loads(config_path.read_text(encoding="utf-8"))
            payload["run_metadata"]["notes"] = "tampered after freeze"
            config_path.write_text(json.dumps(payload) + "\n", encoding="utf-8")
            fake_cli = make_fake_cli(tmp_path, sentinel=sentinel)

            result = run_campaign(
                config_dir, runs_dir, cli_cmd=cli_cmd_for(fake_cli)
            )

            self.assertEqual(result.returncode, 1)
            self.assertFalse(sentinel.exists())
            verdict = read_all_jsonl(runs_dir / "campaign_log.jsonl")[-1]
            self.assertEqual(verdict["collection"]["verdict"], "invalid")
            self.assertIn("config_hash_mismatch", verdict["claim_readiness"]["reasons"])

    def test_readiness_preflight_uses_real_validator_for_fixed_n_mutation(self) -> None:
        from joulewise.analysis_manifest import calculate_manifest_id

        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            config_dir = tmp_path / "configs"
            runs_dir = tmp_path / "runs"
            sentinel = tmp_path / "invoked"
            config_dir.mkdir()
            manifest = write_strict_analysis_campaign(config_dir)
            manifest["design"]["sampling_plan"]["planned_n_blocks"] = 1
            for contrast in manifest["contrasts"]:
                contrast["block_ids"] = contrast["block_ids"][:1]
            manifest["manifest_id"] = calculate_manifest_id(manifest)
            (config_dir / "analysis_manifest.json").write_text(
                json.dumps(manifest, indent=2) + "\n", encoding="utf-8"
            )
            fake_cli = make_fake_cli(tmp_path, sentinel=sentinel)

            result = run_campaign(
                config_dir, runs_dir, cli_cmd=cli_cmd_for(fake_cli)
            )

            self.assertEqual(result.returncode, 1)
            self.assertFalse(sentinel.exists())
            verdict = read_all_jsonl(runs_dir / "campaign_log.jsonl")[-1]
            self.assertEqual(verdict["collection"]["verdict"], "invalid")
            self.assertEqual(
                verdict["claim_readiness"]["verdict"],
                "not_ready_for_analysis",
            )
            self.assertIn(
                "analysis_manifest_invalid",
                verdict["claim_readiness"]["reasons"],
            )

    def test_malformed_analysis_manifest_is_not_assessed_as_ready(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            config_dir = tmp_path / "configs"
            runs_dir = tmp_path / "runs"
            config_dir.mkdir()
            (config_dir / "analysis_manifest.json").write_text("{}\n", encoding="utf-8")

            result = run_campaign(config_dir, runs_dir)

            self.assertEqual(result.returncode, 1, result.stderr)
            verdict = read_all_jsonl(runs_dir / "campaign_log.jsonl")[-1]
            self.assertEqual(verdict["collection"]["verdict"], "invalid")
            self.assertEqual(
                verdict["claim_readiness"]["verdict"],
                "not_ready_for_analysis",
            )
            self.assertIn(
                "analysis_manifest_invalid",
                verdict["claim_readiness"]["reasons"],
            )

    def test_campaign_provenance_records_first_run_exemption_and_unknown_mock_gate(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            config_dir = tmp_path / "configs"
            runs_dir = tmp_path / "runs"
            config_dir.mkdir()
            manifest = write_strict_analysis_campaign(
                config_dir, telemetry_backend="mock"
            )
            fake_cli = make_fake_cli(tmp_path)

            result = run_campaign(config_dir, runs_dir, cli_cmd=cli_cmd_for(fake_cli))

            self.assertEqual(result.returncode, 0, result.stderr)
            manifests = list((runs_dir / "campaign_manifests").glob("*.json"))
            self.assertEqual(len(manifests), 1)
            provenance = json.loads(manifests[0].read_text(encoding="utf-8"))
            first_run_id = manifest["entries"][0]["run_id"]
            second_run_id = manifest["entries"][1]["run_id"]
            self.assertEqual(provenance["first_physical_run_id"], first_run_id)
            members = {
                member["run_id"]: member for member in provenance["members"]
            }
            self.assertEqual(
                members[first_run_id]["preceding_campaign_cooldown"]["result"],
                "first_run_exempt",
            )
            first_cooldown = members[first_run_id]["preceding_campaign_cooldown"]
            self.assertEqual(first_cooldown["policy_version"], "cooldown-v2")
            self.assertEqual(first_cooldown["thresholds"]["sustained_window_s"], 2.0)
            self.assertEqual(first_cooldown["window_coverage_s"], 0.0)
            self.assertIsNone(first_cooldown["thermal_nominal"])
            self.assertEqual(
                first_cooldown["release_criterion"]["window"],
                "complete_sustained_span_and_minimum_coverage",
            )
            second = members[second_run_id]["preceding_campaign_cooldown"]
            self.assertEqual(second["result"], "unknown")
            self.assertIn("mock telemetry", second["reason"])

    def test_prompt_hash_sidecar_match_records_matches(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            config_dir = tmp_path / "configs"
            runs_dir = tmp_path / "runs"
            sidecar = tmp_path / "mixed.annotations.json"
            config_dir.mkdir()
            write_prompt_sidecar(
                sidecar,
                item_003_hash="059b92ad883522ede0ed6466c53233117801ea5d28c3af1ff6d0777487b37e10",
            )
            write_suite_config(config_dir, "suite.json", "suite-match", sidecar=sidecar)

            result = run_campaign(config_dir, runs_dir)

            self.assertEqual(result.returncode, 0, result.stderr)
            rows = read_jsonl(runs_dir / "campaign_log.jsonl")
            self.assertEqual(rows[0]["status"], "ok")
            check = rows[0]["members"][0]["prompt_hash_check"]
            self.assertEqual(check["status"], "matched")
            self.assertEqual(check["checked_items"], 1)
            self.assertEqual(
                [match["item_id"] for match in check["matches"]],
                ["mock_item_003"],
            )

    def test_prompt_hash_sidecar_can_be_inferred_next_to_suite_manifest(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            config_dir = tmp_path / "configs"
            runs_dir = tmp_path / "runs"
            manifest = tmp_path / "mock_suite_manifest.json"
            sidecar = tmp_path / "mock_suite_manifest_annotations.json"
            config_dir.mkdir()
            manifest.write_text(
                (ROOT / "configs" / "suite_manifests" / "mock_suite_manifest.json").read_text(
                    encoding="utf-8"
                ),
                encoding="utf-8",
            )
            write_prompt_sidecar(
                sidecar,
                item_003_hash="059b92ad883522ede0ed6466c53233117801ea5d28c3af1ff6d0777487b37e10",
            )
            write_suite_config(config_dir, "suite.json", "suite-inferred", suite_manifest=manifest)

            result = run_campaign(config_dir, runs_dir)

            self.assertEqual(result.returncode, 0, result.stderr)
            rows = read_jsonl(runs_dir / "campaign_log.jsonl")
            check = rows[0]["members"][0]["prompt_hash_check"]
            self.assertEqual(check["status"], "matched")
            self.assertEqual(check["sidecar_path"], str(sidecar))
            self.assertEqual(check["checked_items"], 1)

    def test_malformed_inferred_prompt_hash_sidecar_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            config_dir = tmp_path / "configs"
            runs_dir = tmp_path / "runs"
            manifest = tmp_path / "mock_suite_manifest.json"
            sidecar = tmp_path / "mock_suite_manifest_annotations.json"
            config_dir.mkdir()
            manifest.write_text(
                (ROOT / "configs" / "suite_manifests" / "mock_suite_manifest.json").read_text(
                    encoding="utf-8"
                ),
                encoding="utf-8",
            )
            sidecar.write_text("{not-json\n", encoding="utf-8")
            write_suite_config(
                config_dir, "suite.json", "suite-inferred-malformed", suite_manifest=manifest
            )

            result = run_campaign(config_dir, runs_dir)

            self.assertEqual(result.returncode, 1)
            self.assertIn("prompt_hash_check_error", result.stderr)
            self.assertIn(str(sidecar), result.stderr)
            self.assertIn("not valid JSON", result.stderr)
            rows = read_jsonl(runs_dir / "campaign_log.jsonl")
            check = rows[0]["members"][0]["prompt_hash_check"]
            self.assertEqual(check["status"], "error")
            self.assertEqual(check["sidecar_path"], str(sidecar))
            self.assertIn("not valid JSON", check["problems"][0])

    def test_neighboring_non_prompt_annotations_sidecar_is_missing_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            config_dir = tmp_path / "configs"
            runs_dir = tmp_path / "runs"
            manifest = tmp_path / "mock_suite_manifest.json"
            sidecar = tmp_path / "mock_suite_manifest_annotations.json"
            config_dir.mkdir()
            manifest.write_text(
                (ROOT / "configs" / "suite_manifests" / "mock_suite_manifest.json").read_text(
                    encoding="utf-8"
                ),
                encoding="utf-8",
            )
            sidecar.write_text(
                json.dumps(
                    {
                        "annotations": [
                            {
                                "item_id": "affine_v1_L01_i00",
                                "scorer_id": "affine_mod_ladder_v1/score_v1",
                            }
                        ],
                    }
                )
                + "\n",
                encoding="utf-8",
            )
            write_suite_config(
                config_dir, "suite.json", "suite-inferred-annotations", suite_manifest=manifest
            )

            result = run_campaign(config_dir, runs_dir)

            self.assertEqual(result.returncode, 1, result.stderr)
            rows = read_jsonl(runs_dir / "campaign_log.jsonl")
            member = rows[0]["members"][0]
            check = member["prompt_hash_check"]
            self.assertEqual(check["status"], "missing_evidence")
            self.assertEqual(check["sidecar_path"], str(sidecar))
            self.assertEqual(check["checked_items"], 0)
            self.assertEqual(
                member["collection_integrity_flags"],
                ["prompt_token_evidence_missing"],
            )
            self.assertEqual(member["collection_classification"], "failed")

    def test_explicit_affine_text_evidence_exemption_is_honored(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            config_dir = tmp_path / "configs"
            runs_dir = tmp_path / "runs"
            manifest = tmp_path / "affine_smoke_v1.json"
            sidecar = tmp_path / "affine_smoke_v1_annotations.json"
            config_dir.mkdir()
            manifest.write_text(
                (ROOT / "configs" / "suite_manifests" / "mock_suite_manifest.json").read_text(
                    encoding="utf-8"
                ),
                encoding="utf-8",
            )
            sidecar.write_text(
                json.dumps({"schema_version": "affine_smoke_annotations.v1"}) + "\n",
                encoding="utf-8",
            )
            write_suite_config(
                config_dir,
                "suite.json",
                "suite-inferred-schema",
                suite_manifest=manifest,
                prompt_token_evidence_policy="exempt_affine_generated_text",
            )

            result = run_campaign(config_dir, runs_dir)

            self.assertEqual(result.returncode, 0, result.stderr)
            rows = read_jsonl(runs_dir / "campaign_log.jsonl")
            member = rows[0]["members"][0]
            check = member["prompt_hash_check"]
            self.assertEqual(check["status"], "policy_exempt")
            self.assertEqual(check["sidecar_path"], str(sidecar))
            self.assertEqual(check["checked_items"], 0)
            self.assertEqual(member["collection_integrity_flags"], [])
            self.assertEqual(member["collection_classification"], "usable")

    def test_unknown_schema_inferred_prompt_hash_sidecar_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            config_dir = tmp_path / "configs"
            runs_dir = tmp_path / "runs"
            manifest = tmp_path / "mock_suite_manifest.json"
            sidecar = tmp_path / "mock_suite_manifest_annotations.json"
            config_dir.mkdir()
            manifest.write_text(
                (ROOT / "configs" / "suite_manifests" / "mock_suite_manifest.json").read_text(
                    encoding="utf-8"
                ),
                encoding="utf-8",
            )
            sidecar.write_text(
                json.dumps({"schema_version": "joulewise.prompt_hash_sidecar.v2"}) + "\n",
                encoding="utf-8",
            )
            write_suite_config(
                config_dir, "suite.json", "suite-inferred-unknown-schema", suite_manifest=manifest
            )

            result = run_campaign(config_dir, runs_dir)

            self.assertEqual(result.returncode, 1)
            self.assertIn("prompt_hash_check_error", result.stderr)
            self.assertIn(str(sidecar), result.stderr)
            self.assertIn("ambiguous", result.stderr)
            rows = read_jsonl(runs_dir / "campaign_log.jsonl")
            check = rows[0]["members"][0]["prompt_hash_check"]
            self.assertEqual(check["status"], "error")
            self.assertEqual(check["sidecar_path"], str(sidecar))
            self.assertEqual(
                check["problems"],
                [
                    "inferred generator sidecar is ambiguous: "
                    "missing prompt-hash items and no recognized other-type marker"
                ],
            )

    def test_non_object_items_inferred_prompt_hash_sidecar_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            config_dir = tmp_path / "configs"
            runs_dir = tmp_path / "runs"
            manifest = tmp_path / "mock_suite_manifest.json"
            sidecar = tmp_path / "mock_suite_manifest_annotations.json"
            config_dir.mkdir()
            manifest.write_text(
                (ROOT / "configs" / "suite_manifests" / "mock_suite_manifest.json").read_text(
                    encoding="utf-8"
                ),
                encoding="utf-8",
            )
            sidecar.write_text(json.dumps({"items": []}) + "\n", encoding="utf-8")
            write_suite_config(
                config_dir, "suite.json", "suite-inferred-non-object-items", suite_manifest=manifest
            )

            result = run_campaign(config_dir, runs_dir)

            self.assertEqual(result.returncode, 1)
            self.assertIn("prompt_hash_check_error", result.stderr)
            self.assertIn(str(sidecar), result.stderr)
            self.assertIn("inferred generator sidecar items is not an object", result.stderr)
            rows = read_jsonl(runs_dir / "campaign_log.jsonl")
            check = rows[0]["members"][0]["prompt_hash_check"]
            self.assertEqual(check["status"], "error")
            self.assertEqual(check["sidecar_path"], str(sidecar))
            self.assertEqual(
                check["problems"], ["inferred generator sidecar items is not an object"]
            )

    def test_empty_object_inferred_prompt_hash_sidecar_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            config_dir = tmp_path / "configs"
            runs_dir = tmp_path / "runs"
            manifest = tmp_path / "mock_suite_manifest.json"
            sidecar = tmp_path / "mock_suite_manifest_annotations.json"
            config_dir.mkdir()
            manifest.write_text(
                (ROOT / "configs" / "suite_manifests" / "mock_suite_manifest.json").read_text(
                    encoding="utf-8"
                ),
                encoding="utf-8",
            )
            sidecar.write_text("{}\n", encoding="utf-8")
            write_suite_config(
                config_dir, "suite.json", "suite-inferred-empty", suite_manifest=manifest
            )

            result = run_campaign(config_dir, runs_dir)

            self.assertEqual(result.returncode, 1)
            self.assertIn("prompt_hash_check_error", result.stderr)
            self.assertIn(str(sidecar), result.stderr)
            self.assertIn("ambiguous", result.stderr)
            rows = read_jsonl(runs_dir / "campaign_log.jsonl")
            check = rows[0]["members"][0]["prompt_hash_check"]
            self.assertEqual(check["status"], "error")
            self.assertEqual(check["sidecar_path"], str(sidecar))
            self.assertEqual(
                check["problems"],
                [
                    "inferred generator sidecar is ambiguous: "
                    "missing prompt-hash items and no recognized other-type marker"
                ],
            )

    def test_required_text_evidence_missing_flags_member_unusable(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            config_dir = tmp_path / "configs"
            runs_dir = tmp_path / "runs"
            manifest = tmp_path / "mock_suite_manifest.json"
            config_dir.mkdir()
            manifest.write_text(
                (ROOT / "configs" / "suite_manifests" / "mock_suite_manifest.json").read_text(
                    encoding="utf-8"
                ),
                encoding="utf-8",
            )
            write_suite_config(
                config_dir, "suite.json", "suite-inferred-absent", suite_manifest=manifest
            )

            result = run_campaign(config_dir, runs_dir)

            self.assertEqual(result.returncode, 1, result.stderr)
            rows = read_jsonl(runs_dir / "campaign_log.jsonl")
            member = rows[0]["members"][0]
            check = member["prompt_hash_check"]
            self.assertEqual(check["status"], "missing_evidence")
            self.assertIn("missing prompt-token evidence", check["problems"][0])
            self.assertEqual(
                member["collection_integrity_flags"],
                ["prompt_token_evidence_missing"],
            )
            self.assertEqual(member["collection_classification"], "failed")

    def test_ids_prompt_label_does_not_bypass_text_evidence_requirement(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            config_dir = tmp_path / "configs"
            runs_dir = tmp_path / "runs"
            manifest = tmp_path / "mislabeled_text_suite.json"
            config_dir.mkdir()
            manifest_data = json.loads(
                (
                    ROOT
                    / "configs"
                    / "suite_manifests"
                    / "mock_suite_manifest.json"
                ).read_text(encoding="utf-8")
            )
            text_item = next(
                item
                for item in manifest_data["items"]
                if item["source"].get("prompt_text") is not None
            )
            text_item["item_type"] = "ids_prompt"
            manifest.write_text(json.dumps(manifest_data) + "\n", encoding="utf-8")
            config = write_suite_config(
                config_dir,
                "suite.json",
                "suite-mislabeled-text",
                suite_manifest=manifest,
            )
            from joulewise.suite import suite_manifest_sha256

            config_data = json.loads(config.read_text(encoding="utf-8"))
            config_data["workload_profile"]["suite_manifest_sha256"] = (
                suite_manifest_sha256(manifest_data)
            )
            config.write_text(json.dumps(config_data) + "\n", encoding="utf-8")

            result = run_campaign(config_dir, runs_dir)

            self.assertEqual(result.returncode, 1, result.stderr)
            rows = read_jsonl(runs_dir / "campaign_log.jsonl")
            member = rows[0]["members"][0]
            self.assertEqual(
                member["prompt_hash_check"]["status"],
                "missing_evidence",
            )
            self.assertEqual(
                member["collection_integrity_flags"],
                ["prompt_token_evidence_missing"],
            )
            self.assertEqual(member["collection_classification"], "failed")

    def test_prompt_hash_sidecar_top_level_alias_resolves_relative_to_config(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            config_dir = tmp_path / "configs"
            runs_dir = tmp_path / "runs"
            sidecar_dir = config_dir / "sidecars"
            sidecar = sidecar_dir / "mixed.annotations.json"
            config_dir.mkdir()
            sidecar_dir.mkdir()
            write_prompt_sidecar(
                sidecar,
                item_003_hash="059b92ad883522ede0ed6466c53233117801ea5d28c3af1ff6d0777487b37e10",
            )
            config = write_suite_config(config_dir, "suite.json", "suite-relative-sidecar")
            payload = json.loads(config.read_text(encoding="utf-8"))
            payload["suite_sidecar_ref"] = str(Path("sidecars") / sidecar.name)
            config.write_text(json.dumps(payload) + "\n", encoding="utf-8")

            result = run_campaign(
                config_dir, runs_dir, ack_config_warnings=True
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            rows = read_jsonl(runs_dir / "campaign_log.jsonl")
            check = rows[0]["members"][0]["prompt_hash_check"]
            self.assertEqual(check["status"], "matched")
            self.assertEqual(check["sidecar_path"], str(sidecar))

    def test_prompt_hash_sidecar_single_item_mismatch_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            config_dir = tmp_path / "configs"
            runs_dir = tmp_path / "runs"
            sidecar = tmp_path / "mixed.annotations.json"
            config_dir.mkdir()
            write_prompt_sidecar(sidecar, item_003_hash="0" * 64)
            write_suite_config(config_dir, "suite.json", "suite-mismatch", sidecar=sidecar)

            result = run_campaign(config_dir, runs_dir)

            self.assertEqual(result.returncode, 1)
            self.assertIn("prompt_hash_mismatch", result.stderr)
            self.assertIn("mock_item_003", result.stderr)
            self.assertIn("expected", result.stderr)
            self.assertIn("realized", result.stderr)
            rows = read_jsonl(runs_dir / "campaign_log.jsonl")
            self.assertEqual(rows[0]["status"], "failed")
            member = rows[0]["members"][0]
            self.assertTrue(member["strict_valid"])
            self.assertEqual(member["collection_integrity_flags"], ["prompt_hash_mismatch"])
            check = member["prompt_hash_check"]
            self.assertEqual(check["status"], "mismatch")
            self.assertEqual(check["checked_items"], 1)
            self.assertIn("mock_item_003", check["problems"][0])

    def test_prompt_hash_sidecar_error_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            config_dir = tmp_path / "configs"
            runs_dir = tmp_path / "runs"
            sidecar = tmp_path / "mixed.annotations.json"
            config_dir.mkdir()
            write_prompt_sidecar(
                sidecar,
                item_003_hash="059b92ad883522ede0ed6466c53233117801ea5d28c3af1ff6d0777487b37e10",
                include_item_003=False,
            )
            write_suite_config(config_dir, "suite.json", "suite-sidecar-error", sidecar=sidecar)

            result = run_campaign(config_dir, runs_dir)

            self.assertEqual(result.returncode, 1)
            self.assertIn("prompt_hash_check_error", result.stderr)
            self.assertIn("missing from generator sidecar", result.stderr)
            rows = read_jsonl(runs_dir / "campaign_log.jsonl")
            self.assertEqual(rows[0]["status"], "failed")
            member = rows[0]["members"][0]
            self.assertEqual(member["collection_integrity_flags"], ["prompt_hash_check_error"])
            check = member["prompt_hash_check"]
            self.assertEqual(check["status"], "error")
            self.assertEqual(check["checked_items"], 0)

    def test_explicit_scorer_shaped_sidecar_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            config_dir = tmp_path / "configs"
            runs_dir = tmp_path / "runs"
            sidecar = tmp_path / "affine_smoke_v1_annotations.json"
            config_dir.mkdir()
            sidecar.write_text(
                json.dumps(
                    {
                        "annotations": [
                            {
                                "item_id": "affine_v1_L01_i00",
                                "scorer_id": "affine_mod_ladder_v1/score_v1",
                            }
                        ],
                        "schema_version": "affine_smoke_annotations.v1",
                    }
                )
                + "\n",
                encoding="utf-8",
            )
            write_suite_config(
                config_dir, "suite.json", "suite-explicit-affine-sidecar", sidecar=sidecar
            )

            result = run_campaign(config_dir, runs_dir)

            self.assertEqual(result.returncode, 1)
            self.assertIn("prompt_hash_check_error", result.stderr)
            self.assertIn("generator sidecar items is not an object", result.stderr)
            rows = read_jsonl(runs_dir / "campaign_log.jsonl")
            check = rows[0]["members"][0]["prompt_hash_check"]
            self.assertEqual(check["status"], "error")
            self.assertEqual(check["sidecar_path"], str(sidecar))
            self.assertEqual(check["problems"], ["generator sidecar items is not an object"])

    def test_prompt_hash_sidecar_pairing_mismatch_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            config_dir = tmp_path / "configs"
            runs_dir = tmp_path / "runs"
            sidecar = tmp_path / "mixed.annotations.json"
            config_dir.mkdir()
            write_prompt_sidecar(
                sidecar,
                item_003_hash="059b92ad883522ede0ed6466c53233117801ea5d28c3af1ff6d0777487b37e10",
                subset_sha256="wrong-subset",
            )
            write_suite_config(config_dir, "suite.json", "suite-pairing-error", sidecar=sidecar)

            result = run_campaign(config_dir, runs_dir)

            self.assertEqual(result.returncode, 1)
            self.assertIn("prompt_hash_check_error", result.stderr)
            self.assertIn("source_manifest.subset_sha256 mismatch", result.stderr)
            rows = read_jsonl(runs_dir / "campaign_log.jsonl")
            check = rows[0]["members"][0]["prompt_hash_check"]
            self.assertEqual(check["status"], "error")
            self.assertEqual(check["checked_items"], 1)

    def test_prompt_hash_sidecar_missing_source_manifest_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            config_dir = tmp_path / "configs"
            runs_dir = tmp_path / "runs"
            sidecar = tmp_path / "mixed.annotations.json"
            config_dir.mkdir()
            write_prompt_sidecar(
                sidecar,
                item_003_hash="059b92ad883522ede0ed6466c53233117801ea5d28c3af1ff6d0777487b37e10",
            )
            payload = json.loads(sidecar.read_text(encoding="utf-8"))
            del payload["source_manifest"]
            sidecar.write_text(json.dumps(payload) + "\n", encoding="utf-8")
            write_suite_config(
                config_dir, "suite.json", "suite-missing-source-manifest", sidecar=sidecar
            )

            result = run_campaign(config_dir, runs_dir)

            self.assertEqual(result.returncode, 1)
            self.assertIn("prompt_hash_check_error", result.stderr)
            self.assertIn("source_manifest is missing", result.stderr)
            rows = read_jsonl(runs_dir / "campaign_log.jsonl")
            check = rows[0]["members"][0]["prompt_hash_check"]
            self.assertEqual(check["status"], "error")
            self.assertEqual(check["checked_items"], 1)
            self.assertIn("generator sidecar source_manifest is missing", check["problems"])

    def test_prompt_hash_error_can_be_waived_to_partial(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            config_dir = tmp_path / "configs"
            runs_dir = tmp_path / "runs"
            sidecar = tmp_path / "mixed.annotations.json"
            waivers = tmp_path / "waivers.json"
            config_dir.mkdir()
            write_config(config_dir, "01-good.json", "good")
            write_prompt_sidecar(
                sidecar,
                item_003_hash="059b92ad883522ede0ed6466c53233117801ea5d28c3af1ff6d0777487b37e10",
                include_item_003=False,
            )
            write_suite_config(config_dir, "02-suite.json", "suite-waived-error", sidecar=sidecar)
            waivers.write_text(
                json.dumps(
                    [
                        {
                            "run_id": "suite-waived-error",
                            "reason": "manual prompt-sidecar audit accepted",
                            "approver": "council",
                            "timestamp": "2026-07-08T00:00:00Z",
                            "scope": "prompt_hash_check_error",
                        }
                    ]
                )
                + "\n",
                encoding="utf-8",
            )

            result = run_campaign(config_dir, runs_dir, waivers=waivers)

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("verdict: partial", result.stdout)
            rows = read_jsonl(runs_dir / "campaign_log.jsonl")
            self.assertEqual([row["status"] for row in rows], ["ok", "waived"])
            member = rows[1]["members"][0]
            self.assertEqual(member["collection_classification"], "waived")
            self.assertEqual(member["waiver"]["scope"], "prompt_hash_check_error")

    def test_id_native_suite_without_sidecar_remains_not_applicable(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            config_dir = tmp_path / "configs"
            runs_dir = tmp_path / "runs"
            manifest = tmp_path / "id_native_suite.json"
            config_dir.mkdir()
            manifest_data = json.loads(
                (
                    ROOT
                    / "configs"
                    / "suite_manifests"
                    / "mock_suite_manifest.json"
                ).read_text(encoding="utf-8")
            )
            for item in manifest_data["items"]:
                if item["item_type"] != "text_prompt":
                    continue
                count = item["shape"]["planned_prompt_tokens"]
                item["item_type"] = "ids_prompt"
                item["source"]["prompt_text"] = None
                item["source"]["prompt_token_ids"] = list(range(1, count + 1))
            manifest.write_text(json.dumps(manifest_data) + "\n", encoding="utf-8")
            config = write_suite_config(
                config_dir,
                "suite.json",
                "suite-no-sidecar",
                suite_manifest=manifest,
            )
            from joulewise.suite import suite_manifest_sha256

            config_data = json.loads(config.read_text(encoding="utf-8"))
            config_data["workload_profile"]["suite_manifest_sha256"] = (
                suite_manifest_sha256(manifest_data)
            )
            config.write_text(json.dumps(config_data) + "\n", encoding="utf-8")

            result = run_campaign(config_dir, runs_dir)

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertNotIn("prompt_hash", result.stderr)
            rows = read_jsonl(runs_dir / "campaign_log.jsonl")
            check = rows[0]["members"][0]["prompt_hash_check"]
            self.assertEqual(check, {"status": "not_applicable", "checked_items": 0})

    def test_unknown_prompt_token_evidence_policy_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            config_dir = tmp_path / "configs"
            runs_dir = tmp_path / "runs"
            config_dir.mkdir()
            write_suite_config(
                config_dir,
                "suite.json",
                "suite-unknown-policy",
                prompt_token_evidence_policy="trust_neighboring_annotations",
            )

            result = run_campaign(config_dir, runs_dir)

            self.assertEqual(result.returncode, 2)
            self.assertIn("prompt_token_evidence_policy must be one of", result.stderr)
            self.assertFalse(runs_dir.exists())

    def test_post_hoc_prompt_hash_check_flag_on_fixture_pair(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            config_dir = tmp_path / "configs"
            runs_dir = tmp_path / "runs"
            sidecar = tmp_path / "mixed.annotations.json"
            config_dir.mkdir()
            write_prompt_sidecar(
                sidecar,
                item_003_hash="059b92ad883522ede0ed6466c53233117801ea5d28c3af1ff6d0777487b37e10",
            )
            write_suite_config(
                config_dir,
                "suite.json",
                "suite-posthoc",
                prompt_token_evidence_policy="exempt_affine_generated_text",
            )
            campaign = run_campaign(config_dir, runs_dir)
            self.assertEqual(campaign.returncode, 0, campaign.stderr)

            result = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--check-prompt-hashes",
                    str(runs_dir / "suite-posthoc"),
                    str(sidecar),
                ],
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=False,
                timeout=COMMAND_TIMEOUT_S,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            check = json.loads(result.stdout)
            self.assertEqual(check["status"], "matched")
            self.assertEqual(check["checked_items"], 1)

    def test_post_hoc_prompt_hash_check_nonzero_statuses(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            config_dir = tmp_path / "configs"
            runs_dir = tmp_path / "runs"
            sidecar = tmp_path / "mixed.annotations.json"
            config_dir.mkdir()
            write_prompt_sidecar(sidecar, item_003_hash="0" * 64)
            write_suite_config(
                config_dir,
                "suite.json",
                "suite-posthoc-nonzero",
                prompt_token_evidence_policy="exempt_affine_generated_text",
            )
            campaign = run_campaign(config_dir, runs_dir)
            self.assertEqual(campaign.returncode, 0, campaign.stderr)

            mismatch = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--check-prompt-hashes",
                    str(runs_dir / "suite-posthoc-nonzero"),
                    str(sidecar),
                ],
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=False,
                timeout=COMMAND_TIMEOUT_S,
            )
            error = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--check-prompt-hashes",
                    str(runs_dir / "suite-posthoc-nonzero"),
                    str(tmp_path / "missing-sidecar.json"),
                ],
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=False,
                timeout=COMMAND_TIMEOUT_S,
            )

            self.assertEqual(mismatch.returncode, 1, mismatch.stderr)
            self.assertEqual(json.loads(mismatch.stdout)["status"], "mismatch")
            self.assertEqual(error.returncode, 2, error.stderr)
            self.assertEqual(json.loads(error.stdout)["status"], "error")

    def test_partial_experiment_is_incomplete_and_does_not_invoke_cli(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            config_dir = tmp_path / "configs"
            runs_dir = tmp_path / "runs"
            config_dir.mkdir()
            config_path = write_config(
                config_dir, "partial.json", "partial-exp", repetitions=5
            )
            write_experiment(
                runs_dir,
                "partial-exp",
                5,
                completed=3,
                config_path=config_path,
            )
            sentinel = tmp_path / "sentinel"
            fake_cli = make_fake_cli(tmp_path, sentinel)

            result = run_campaign(
                config_dir,
                runs_dir,
                cli_cmd=cli_cmd_for(fake_cli),
            )

            self.assertEqual(result.returncode, 1)
            self.assertFalse(sentinel.exists())
            self.assertIn("incomplete_existing partial-exp", result.stderr)
            self.assertIn("partial-exp__r1", result.stderr)
            self.assertIn("partial-exp__r3", result.stderr)
            rows = read_jsonl(runs_dir / "campaign_log.jsonl")
            self.assertEqual([row["status"] for row in rows], ["incomplete_existing"])
            self.assertNotIn("members_succeeded", rows[0])
            verdict = read_all_jsonl(runs_dir / "campaign_log.jsonl")[-1]
            self.assertEqual(verdict["collection"]["verdict"], "blocked")
            self.assertEqual(
                verdict["collection"]["categories"]["usable"],
                ["partial-exp__r1", "partial-exp__r2", "partial-exp__r3"],
            )
            self.assertEqual(
                verdict["collection"]["categories"]["missing"],
                ["partial-exp__r4", "partial-exp__r5"],
            )

    def test_existing_incomplete_member_prevents_usable_collection_verdict(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            config_dir = tmp_path / "configs"
            runs_dir = tmp_path / "runs"
            config_dir.mkdir()
            write_config(config_dir, "01-usable.json", "usable")
            write_config(config_dir, "02-incomplete.json", "incomplete")
            write_single_bundle(runs_dir, "usable")
            (runs_dir / "incomplete").mkdir()

            result = run_campaign(config_dir, runs_dir)

            self.assertEqual(result.returncode, 1)
            verdict = read_all_jsonl(runs_dir / "campaign_log.jsonl")[-1]
            self.assertNotEqual(verdict["collection"]["verdict"], "usable")
            self.assertEqual(verdict["collection"]["verdict"], "invalid")
            self.assertEqual(
                verdict["collection"]["categories"]["usable"], ["usable"]
            )
            self.assertEqual(
                verdict["collection"]["categories"]["failed"], ["incomplete"]
            )
            self.assertEqual(verdict["collection"]["categories"]["missing"], [])

    def test_mixed_complete_incomplete_and_absent_members_are_classified_exactly(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            config_dir = tmp_path / "configs"
            runs_dir = tmp_path / "runs"
            config_dir.mkdir()
            config_path = write_config(
                config_dir, "mixed.json", "mixed", repetitions=3
            )
            write_single_bundle(
                runs_dir,
                "mixed__r1",
                config_path=config_path,
            )
            (runs_dir / "mixed__r2").mkdir()

            result = run_campaign(config_dir, runs_dir)

            self.assertEqual(result.returncode, 1)
            verdict = read_all_jsonl(runs_dir / "campaign_log.jsonl")[-1]
            self.assertEqual(verdict["collection"]["verdict"], "blocked")
            self.assertEqual(
                verdict["collection"]["categories"],
                {
                    "usable": ["mixed__r1"],
                    "waived": [],
                    "failed": ["mixed__r2"],
                    "missing": ["mixed__r3"],
                },
            )

    def test_reps_one_resume_uses_single_bundle_path(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            config_dir = tmp_path / "configs"
            runs_dir = tmp_path / "runs"
            config_dir.mkdir()
            write_config(config_dir, "01-complete.json", "complete", repetitions=1)
            write_config(config_dir, "02-incomplete.json", "incomplete", repetitions=1)
            write_single_bundle(runs_dir, "complete")
            (runs_dir / "incomplete").mkdir()
            sentinel = tmp_path / "sentinel"
            fake_cli = make_fake_cli(tmp_path, sentinel)

            result = run_campaign(
                config_dir,
                runs_dir,
                cli_cmd=cli_cmd_for(fake_cli),
            )

            self.assertEqual(result.returncode, 1)
            self.assertFalse(sentinel.exists())
            self.assertIn("skipped complete", result.stdout)
            self.assertIn("incomplete_existing incomplete", result.stderr)
            rows = read_jsonl(runs_dir / "campaign_log.jsonl")
            self.assertEqual([row["status"] for row in rows], ["skipped", "incomplete_existing"])
            self.assertEqual([row["exit_code"] for row in rows], [None, None])

    def test_fake_cli_execution_logs_statuses_and_sequential_order(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            config_dir = tmp_path / "configs"
            runs_dir = tmp_path / "runs"
            config_dir.mkdir()
            write_config(config_dir, "01-alpha.json", "alpha", repetitions=5)
            write_config(config_dir, "02-beta.json", "beta-fail", repetitions=5)
            write_config(config_dir, "03-gamma.json", "gamma", repetitions=5)
            fake_cli = make_fake_cli(tmp_path)

            result = run_campaign(
                config_dir,
                runs_dir,
                cli_cmd=cli_cmd_for(fake_cli),
                max_failures=2,
            )

            self.assertEqual(result.returncode, 1)
            self.assertEqual((runs_dir / "order.log").read_text(encoding="utf-8").splitlines(), ["alpha", "beta-fail", "gamma"])
            self.assertIn(f"bundle: {runs_dir / 'alpha__r1'} status=succeeded", result.stdout)
            self.assertIn(f"bundle: {runs_dir / 'beta-fail__r5'} status=failed", result.stdout)
            self.assertIn(f"experiment: {runs_dir / 'experiments' / 'alpha.json'} members=5", result.stdout)
            rows = read_jsonl(runs_dir / "campaign_log.jsonl")
            self.assertEqual([row["run_id"] for row in rows], ["alpha", "beta-fail", "gamma"])
            self.assertEqual([row["status"] for row in rows], ["ok", "failed", "ok"])
            self.assertEqual([row["exit_code"] for row in rows], [0, 3, 0])
            self.assertIsInstance(rows[0]["duration_s"], float)
            self.assertTrue((runs_dir / "alpha__r1" / "summary_metrics.json").is_file())
            self.assertTrue((runs_dir / "alpha__r5" / "summary_metrics.json").is_file())
            self.assertTrue((runs_dir / "beta-fail__r5" / "summary_metrics.json").is_file())
            self.assertTrue((runs_dir / "gamma__r5" / "summary_metrics.json").is_file())

    def test_order_manifest_controls_execution_order_and_log_metadata(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            config_dir = tmp_path / "configs"
            runs_dir = tmp_path / "runs"
            config_dir.mkdir()
            alpha = write_config(config_dir, "01-alpha.json", "alpha")
            beta = write_config(config_dir, "02-beta.json", "beta")
            (config_dir / "order_manifest.json").write_text(
                json.dumps(
                    {
                        "schema_version": "joulewise.order_manifest.v1",
                        "seed": 2000005,
                        "rotation_scheme": {},
                        "imbalance_note": "test",
                        "executed_order": [
                            {
                                "index": 1,
                                "config": beta.name,
                                "run_id": "beta",
                                "model_tag": "b",
                                "rep": 1,
                                "workload": "short_short",
                            },
                            {
                                "index": 2,
                                "config": alpha.name,
                                "run_id": "alpha",
                                "model_tag": "a",
                                "rep": 1,
                                "workload": "short_short",
                            },
                        ],
                    }
                )
                + "\n",
                encoding="utf-8",
            )
            fake_cli = make_fake_cli(tmp_path)

            result = run_campaign(config_dir, runs_dir, cli_cmd=cli_cmd_for(fake_cli))

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual((runs_dir / "order.log").read_text(encoding="utf-8").splitlines(), ["beta", "alpha"])
            rows = read_jsonl(runs_dir / "campaign_log.jsonl")
            self.assertEqual([row["run_id"] for row in rows], ["beta", "alpha"])
            self.assertEqual([row["run_index"] for row in rows], [1, 2])
            self.assertEqual(rows[0]["executed_order"]["model_tag"], "b")
            self.assertIs(rows[0]["model_load_boundary"], True)
            self.assertIs(rows[1]["model_load_boundary"], True)

    def test_order_manifest_log_echo_carries_drift_covariates_when_present(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            fake_cli = make_fake_cli(tmp_path)

            config_dir = tmp_path / "configs-with-covariates"
            runs_dir = tmp_path / "runs-with-covariates"
            config_dir.mkdir()
            sentinel = write_config(config_dir, "sentinel.json", "alpha-r1-short_short_sentinel-start")
            (config_dir / "order_manifest.json").write_text(
                json.dumps(
                    {
                        "schema_version": "joulewise.order_manifest.v1",
                        "executed_order": [
                            {
                                "index": 1,
                                "config": sentinel.name,
                                "run_id": "alpha-r1-short_short_sentinel-start",
                                "model_tag": "alpha",
                                "rep": 1,
                                "workload": "short_short_sentinel",
                                "role": "drift_sentinel",
                                "block_index": 7,
                                "position_in_block": 1,
                                "sentinel_position": "start",
                            }
                        ],
                    }
                )
                + "\n",
                encoding="utf-8",
            )

            result = run_campaign(config_dir, runs_dir, cli_cmd=cli_cmd_for(fake_cli))

            self.assertEqual(result.returncode, 0, result.stderr)
            rows = read_jsonl(runs_dir / "campaign_log.jsonl")
            echoed = rows[0]["executed_order"]
            self.assertEqual(echoed["run_id"], "alpha-r1-short_short_sentinel-start")
            self.assertEqual(echoed["role"], "drift_sentinel")
            self.assertEqual(echoed["block_index"], 7)
            self.assertEqual(echoed["position_in_block"], 1)
            self.assertEqual(echoed["sentinel_position"], "start")

            old_config_dir = tmp_path / "configs-old-manifest"
            old_runs_dir = tmp_path / "runs-old-manifest"
            old_config_dir.mkdir()
            old_config = write_config(old_config_dir, "baseline.json", "alpha-r1-short_short")
            (old_config_dir / "order_manifest.json").write_text(
                json.dumps(
                    {
                        "schema_version": "joulewise.order_manifest.v1",
                        "executed_order": [
                            {
                                "index": 1,
                                "config": old_config.name,
                                "run_id": "alpha-r1-short_short",
                                "model_tag": "alpha",
                                "rep": 1,
                                "workload": "short_short",
                            }
                        ],
                    }
                )
                + "\n",
                encoding="utf-8",
            )

            old_result = run_campaign(old_config_dir, old_runs_dir, cli_cmd=cli_cmd_for(fake_cli))

            self.assertEqual(old_result.returncode, 0, old_result.stderr)
            old_rows = read_jsonl(old_runs_dir / "campaign_log.jsonl")
            old_echoed = old_rows[0]["executed_order"]
            self.assertEqual(old_echoed["run_id"], "alpha-r1-short_short")
            self.assertNotIn("role", old_echoed)
            self.assertNotIn("block_index", old_echoed)
            self.assertNotIn("position_in_block", old_echoed)
            self.assertNotIn("sentinel_position", old_echoed)

    def test_order_manifest_rejects_duplicate_and_non_contiguous_entries(self) -> None:
        cases = [
            (
                "duplicate-config",
                [
                    {"index": 1, "config": "01-alpha.json"},
                    {"index": 2, "config": "01-alpha.json"},
                ],
                "duplicate config",
            ),
            (
                "duplicate-index",
                [
                    {"index": 1, "config": "01-alpha.json"},
                    {"index": 1, "config": "02-beta.json"},
                ],
                "duplicate index",
            ),
            (
                "gap-index",
                [
                    {"index": 1, "config": "01-alpha.json"},
                    {"index": 3, "config": "02-beta.json"},
                ],
                "contiguous",
            ),
        ]
        for label, executed_order, expected in cases:
            with self.subTest(label=label), tempfile.TemporaryDirectory() as tmp:
                tmp_path = Path(tmp)
                config_dir = tmp_path / "configs"
                runs_dir = tmp_path / "runs"
                config_dir.mkdir()
                write_config(config_dir, "01-alpha.json", "alpha")
                write_config(config_dir, "02-beta.json", "beta")
                (config_dir / "order_manifest.json").write_text(
                    json.dumps(
                        {
                            "schema_version": "joulewise.order_manifest.v1",
                            "executed_order": executed_order,
                        }
                    )
                    + "\n",
                    encoding="utf-8",
                )

                result = run_campaign(config_dir, runs_dir)

                self.assertEqual(result.returncode, 2)
                self.assertIn(expected, result.stderr)

    def test_missing_order_manifest_records_loud_warning(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            config_dir = tmp_path / "configs"
            runs_dir = tmp_path / "runs"
            config_dir.mkdir()
            write_config(config_dir, "one.json", "one")
            fake_cli = make_fake_cli(tmp_path)

            result = run_campaign(config_dir, runs_dir, cli_cmd=cli_cmd_for(fake_cli))

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("no order_manifest.json found", result.stderr)
            all_rows = read_all_jsonl(runs_dir / "campaign_log.jsonl")
            self.assertIn("block_order_warning", all_rows[0])
            self.assertIn("block_order_warning", all_rows[-1])

    def test_fresh_experiment_run_then_second_invocation_skips(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            config_dir = tmp_path / "configs"
            runs_dir = tmp_path / "runs"
            config_dir.mkdir()
            write_config(config_dir, "matrix.json", "matrix-exp", repetitions=5)
            fake_cli = make_fake_cli(tmp_path)

            first = run_campaign(
                config_dir,
                runs_dir,
                cli_cmd=cli_cmd_for(fake_cli),
            )
            second = run_campaign(
                config_dir,
                runs_dir,
                cli_cmd=cli_cmd_for(fake_cli),
            )

            self.assertEqual(first.returncode, 0, first.stderr)
            self.assertEqual(second.returncode, 0, second.stderr)
            self.assertEqual((runs_dir / "order.log").read_text(encoding="utf-8").splitlines(), ["matrix-exp"])
            self.assertTrue((runs_dir / "matrix-exp__r1" / "summary_metrics.json").is_file())
            self.assertTrue((runs_dir / "experiments" / "matrix-exp.json").is_file())
            rows = read_jsonl(runs_dir / "campaign_log.jsonl")
            self.assertEqual([row["status"] for row in rows], ["ok", "skipped"])
            self.assertEqual(rows[1]["members_succeeded"], 5)
            self.assertEqual(rows[1]["members_total"], 5)

    def test_max_failures_stops_after_n_failures(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            config_dir = tmp_path / "configs"
            runs_dir = tmp_path / "runs"
            config_dir.mkdir()
            write_config(config_dir, "01-one.json", "one-fail")
            write_config(config_dir, "02-two.json", "two-fail")
            write_config(config_dir, "03-three.json", "three")
            fake_cli = make_fake_cli(tmp_path)

            result = run_campaign(
                config_dir,
                runs_dir,
                cli_cmd=cli_cmd_for(fake_cli),
                max_failures=1,
            )

            self.assertEqual(result.returncode, 1)
            self.assertEqual((runs_dir / "order.log").read_text(encoding="utf-8").splitlines(), ["one-fail"])
            rows = read_jsonl(runs_dir / "campaign_log.jsonl")
            self.assertEqual([row["run_id"] for row in rows], ["one-fail"])
            self.assertEqual([row["status"] for row in rows], ["failed"])

    def test_resume_after_partial_failure_sequence_skips_partial_on_second_run(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            config_dir = tmp_path / "configs"
            runs_dir = tmp_path / "runs"
            log_path = tmp_path / "campaign.jsonl"
            config_dir.mkdir()
            write_config(config_dir, "01-alpha.json", "alpha", repetitions=5)
            write_config(config_dir, "02-beta.json", "beta-crash2", repetitions=5)
            fake_cli = make_fake_cli(tmp_path)

            first = run_campaign(
                config_dir,
                runs_dir,
                cli_cmd=cli_cmd_for(fake_cli),
                max_failures=2,
                log_path=log_path,
            )
            second = run_campaign(
                config_dir,
                runs_dir,
                cli_cmd=cli_cmd_for(fake_cli),
                max_failures=2,
                log_path=log_path,
            )

            self.assertEqual(first.returncode, 1)
            self.assertEqual(second.returncode, 1)
            self.assertEqual((runs_dir / "order.log").read_text(encoding="utf-8").splitlines(), ["alpha", "beta-crash2"])
            self.assertTrue((runs_dir / "beta-crash2__r1" / "summary_metrics.json").is_file())
            self.assertTrue((runs_dir / "beta-crash2__r2" / "summary_metrics.json").is_file())
            self.assertFalse((runs_dir / "beta-crash2__r3").exists())
            rows = read_jsonl(log_path)
            self.assertEqual([row["run_id"] for row in rows], ["alpha", "beta-crash2", "alpha", "beta-crash2"])
            self.assertEqual([row["status"] for row in rows], ["ok", "failed", "skipped", "incomplete_existing"])
            verdicts = [
                row
                for row in read_all_jsonl(log_path)
                if row.get("record_type") == "campaign_verdict"
            ]
            self.assertEqual(
                [verdict["collection"]["verdict"] for verdict in verdicts],
                ["blocked", "blocked"],
            )

    def test_malformed_member_summary_is_incomplete_existing_without_invocation(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            config_dir = tmp_path / "configs"
            runs_dir = tmp_path / "runs"
            config_dir.mkdir()
            write_config(config_dir, "matrix.json", "matrix", repetitions=5)
            member = runs_dir / "matrix__r1"
            member.mkdir(parents=True)
            (member / "summary_metrics.json").write_text('{"status": ', encoding="utf-8")
            fake_cli = make_fake_cli(tmp_path)

            result = run_campaign(
                config_dir,
                runs_dir,
                cli_cmd=cli_cmd_for(fake_cli),
            )

            self.assertEqual(result.returncode, 1)
            self.assertFalse((runs_dir / "order.log").exists())
            self.assertIn("malformed summary_metrics.json", result.stderr)
            self.assertIn("matrix__r1", result.stderr)
            rows = read_jsonl(runs_dir / "campaign_log.jsonl")
            self.assertEqual([row["status"] for row in rows], ["incomplete_existing"])
            verdict = read_all_jsonl(runs_dir / "campaign_log.jsonl")[-1]
            self.assertEqual(verdict["collection"]["verdict"], "blocked")
            self.assertEqual(
                verdict["collection"]["categories"]["failed"], ["matrix__r1"]
            )
            self.assertEqual(
                verdict["collection"]["categories"]["missing"],
                [
                    "matrix__r2",
                    "matrix__r3",
                    "matrix__r4",
                    "matrix__r5",
                ],
            )

    def test_config_error_aborts_before_invocation_or_log_writes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            config_dir = tmp_path / "configs"
            runs_dir = tmp_path / "runs"
            config_dir.mkdir()
            good = write_config(config_dir, "01-good.json", "good")
            bad = config_dir / "02-bad.json"
            bad.write_text('{"run_id": ', encoding="utf-8")
            later = write_config(config_dir, "03-later.json", "later")
            fake_cli = make_fake_cli(tmp_path)

            result = run_campaign(
                config_dir,
                runs_dir,
                cli_cmd=cli_cmd_for(fake_cli),
                max_failures=2,
            )

            self.assertEqual(result.returncode, 2)
            self.assertIn("Config files to execute:", result.stdout)
            self.assertIn(str(good), result.stdout)
            self.assertIn(str(bad), result.stdout)
            self.assertIn(str(later), result.stdout)
            self.assertIn("config is not valid JSON", result.stderr)
            self.assertIn(str(bad), result.stderr)
            self.assertFalse((runs_dir / "order.log").exists())
            self.assertFalse((runs_dir / "campaign_log.jsonl").exists())

    def test_duplicate_sanitized_run_ids_abort_before_invocation(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            config_dir = tmp_path / "configs"
            runs_dir = tmp_path / "runs"
            config_dir.mkdir()
            write_config(config_dir, "01-space.json", "Foo Bar")
            write_config(config_dir, "02-dash.json", "foo-bar")
            fake_cli = make_fake_cli(tmp_path)

            result = run_campaign(
                config_dir,
                runs_dir,
                cli_cmd=cli_cmd_for(fake_cli),
            )

            self.assertEqual(result.returncode, 2)
            self.assertIn("duplicate sanitized run_id", result.stderr)
            self.assertIn("01-space.json", result.stderr)
            self.assertIn("02-dash.json", result.stderr)
            self.assertFalse((runs_dir / "order.log").exists())
            self.assertFalse((runs_dir / "campaign_log.jsonl").exists())

    def test_sanitized_run_id_is_used_for_path_checks(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            config_dir = tmp_path / "configs"
            runs_dir = tmp_path / "runs"
            config_dir.mkdir()
            config_path = write_config(config_dir, "space.json", "Foo Bar")
            write_single_bundle(runs_dir, "foo-bar", config_path=config_path)
            fake_cli = make_fake_cli(tmp_path)

            result = run_campaign(
                config_dir,
                runs_dir,
                cli_cmd=cli_cmd_for(fake_cli),
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("sanitized run_id", result.stderr)
            self.assertIn("skipped foo-bar", result.stdout)
            self.assertFalse((runs_dir / "order.log").exists())
            rows = read_jsonl(runs_dir / "campaign_log.jsonl")
            self.assertEqual(rows[0]["run_id"], "foo-bar")
            self.assertEqual(rows[0]["status"], "skipped")

    def test_cli_exit_2_is_failed_log_row_without_bundle(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            config_dir = tmp_path / "configs"
            runs_dir = tmp_path / "runs"
            config_dir.mkdir()
            write_config(config_dir, "exit2.json", "exit2")
            fake_cli = make_fake_cli(tmp_path)

            result = run_campaign(
                config_dir,
                runs_dir,
                cli_cmd=cli_cmd_for(fake_cli),
            )

            self.assertEqual(result.returncode, 1)
            self.assertFalse((runs_dir / "exit2").exists())
            rows = read_jsonl(runs_dir / "campaign_log.jsonl")
            self.assertEqual(rows[0]["status"], "failed")
            self.assertEqual(rows[0]["exit_code"], 2)

    def test_cli_cmd_with_spaces_executes_and_dry_run_quotes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            config_dir = tmp_path / "configs"
            runs_dir = tmp_path / "runs"
            spaced_dir = tmp_path / "tool dir"
            config_dir.mkdir()
            spaced_dir.mkdir()
            write_config(config_dir, "one.json", "one")
            fake_cli = make_fake_cli(spaced_dir)
            cli_cmd = cli_cmd_for(fake_cli)

            dry = run_campaign(config_dir, runs_dir, cli_cmd=cli_cmd, dry_run=True)
            real = run_campaign(config_dir, runs_dir, cli_cmd=cli_cmd)

            self.assertEqual(dry.returncode, 0, dry.stderr)
            self.assertIn(shlex.quote(str(fake_cli)), dry.stdout)
            self.assertEqual(real.returncode, 0, real.stderr)
            self.assertEqual((runs_dir / "order.log").read_text(encoding="utf-8").splitlines(), ["one"])

    def test_max_failures_skips_do_not_consume_incomplete_does(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            config_dir = tmp_path / "configs"
            runs_dir = tmp_path / "runs"
            config_dir.mkdir()
            write_config(config_dir, "01-skip.json", "skip")
            write_config(config_dir, "02-partial.json", "partial", repetitions=5)
            write_config(config_dir, "03-fresh.json", "fresh")
            write_single_bundle(runs_dir, "skip")
            (runs_dir / "partial__r1").mkdir(parents=True)
            fake_cli = make_fake_cli(tmp_path)

            result = run_campaign(
                config_dir,
                runs_dir,
                cli_cmd=cli_cmd_for(fake_cli),
                max_failures=1,
            )

            self.assertEqual(result.returncode, 1)
            self.assertFalse((runs_dir / "order.log").exists())
            rows = read_jsonl(runs_dir / "campaign_log.jsonl")
            self.assertEqual([row["run_id"] for row in rows], ["skip", "partial"])
            self.assertEqual([row["status"] for row in rows], ["skipped", "incomplete_existing"])

    def test_backup_shim_runs_once_per_success_and_failure_is_nonfatal(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            config_dir = tmp_path / "configs"
            runs_dir = tmp_path / "runs"
            backup_log = tmp_path / "backup.log"
            backup = tmp_path / "backup shim.sh"
            config_dir.mkdir()
            write_config(config_dir, "01-alpha.json", "alpha")
            write_config(config_dir, "02-beta.json", "beta")
            fake_cli = make_fake_cli(tmp_path)
            backup.write_text(
                f"#!/bin/sh\nprintf '%s\\n' \"$1\" >> {shlex.quote(str(backup_log))}\nexit 1\n",
                encoding="utf-8",
            )
            os.chmod(backup, 0o755)

            result = run_campaign(
                config_dir,
                runs_dir,
                cli_cmd=cli_cmd_for(fake_cli),
                backup=backup,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(backup_log.read_text(encoding="utf-8").splitlines(), [str(runs_dir), str(runs_dir)])
            self.assertIn("warning: backup command failed", result.stderr)
            rows = read_jsonl(runs_dir / "campaign_log.jsonl")
            self.assertEqual([row["status"] for row in rows], ["ok", "ok"])

    def test_torn_log_gets_newline_before_new_json_rows(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            config_dir = tmp_path / "configs"
            runs_dir = tmp_path / "runs"
            log_path = tmp_path / "campaign.jsonl"
            config_dir.mkdir()
            write_config(config_dir, "one.json", "one")
            log_path.write_text("dead partial", encoding="utf-8")
            fake_cli = make_fake_cli(tmp_path)

            result = run_campaign(
                config_dir,
                runs_dir,
                cli_cmd=cli_cmd_for(fake_cli),
                log_path=log_path,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            lines = log_path.read_text(encoding="utf-8").splitlines()
            self.assertEqual(lines[0], "dead partial")
            parsed = [
                json.loads(line)
                for line in lines[1:]
                if json.loads(line).get("record_type") != "campaign_verdict"
            ]
            self.assertEqual([row["status"] for row in parsed], ["ok"])

    def test_lock_blocks_real_run_is_removed_after_success_and_dry_run_ignores_it(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            config_dir = tmp_path / "configs"
            runs_dir = tmp_path / "runs"
            config_dir.mkdir()
            runs_dir.mkdir()
            write_config(config_dir, "one.json", "one")
            fake_cli = make_fake_cli(tmp_path)
            lock = runs_dir / "campaign.lock"
            lock.write_text("pid=123 created_at=manual\n", encoding="utf-8")

            dry = run_campaign(config_dir, runs_dir, cli_cmd=cli_cmd_for(fake_cli), dry_run=True)
            blocked = run_campaign(config_dir, runs_dir, cli_cmd=cli_cmd_for(fake_cli))
            self.assertFalse((runs_dir / "campaign_log.jsonl").exists())
            self.assertFalse((runs_dir / "order.log").exists())
            lock.unlink()
            real = run_campaign(config_dir, runs_dir, cli_cmd=cli_cmd_for(fake_cli))

            self.assertEqual(dry.returncode, 0, dry.stderr)
            self.assertEqual(blocked.returncode, 2)
            self.assertIn("another campaign appears to be running", blocked.stderr)
            self.assertEqual(real.returncode, 0, real.stderr)
            self.assertFalse(lock.exists())
            self.assertEqual((runs_dir / "order.log").read_text(encoding="utf-8").splitlines(), ["one"])

    def test_dry_run_plan_matches_real_mixed_state_actions(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            config_dir = tmp_path / "configs"
            runs_dir = tmp_path / "runs"
            config_dir.mkdir()
            complete_config = write_config(
                config_dir, "01-complete.json", "complete", repetitions=5
            )
            partial_config = write_config(
                config_dir, "02-partial.json", "partial", repetitions=5
            )
            write_config(config_dir, "03-fresh.json", "fresh", repetitions=5)
            write_experiment(
                runs_dir, "complete", 5, config_path=complete_config
            )
            write_experiment(
                runs_dir,
                "partial",
                5,
                completed=2,
                config_path=partial_config,
            )
            fake_cli = make_fake_cli(tmp_path)

            dry = run_campaign(
                config_dir,
                runs_dir,
                cli_cmd=cli_cmd_for(fake_cli),
                dry_run=True,
            )
            real = run_campaign(
                config_dir,
                runs_dir,
                cli_cmd=cli_cmd_for(fake_cli),
                max_failures=2,
            )

            self.assertEqual(dry.returncode, 0, dry.stderr)
            self.assertIn("dry_run complete: skip complete", dry.stdout)
            self.assertIn("dry_run partial: incomplete existing", dry.stdout)
            self.assertIn("dry_run fresh: would run", dry.stdout)
            self.assertEqual(real.returncode, 1)
            self.assertEqual((runs_dir / "order.log").read_text(encoding="utf-8").splitlines(), ["fresh"])
            rows = read_jsonl(runs_dir / "campaign_log.jsonl")
            self.assertEqual([row["run_id"] for row in rows], ["complete", "partial", "fresh"])
            self.assertEqual([row["status"] for row in rows], ["skipped", "incomplete_existing", "ok"])
            manifests = list((runs_dir / "campaign_manifests").glob("*.json"))
            self.assertEqual(len(manifests), 1)
            provenance = json.loads(manifests[0].read_text(encoding="utf-8"))
            self.assertEqual(provenance["first_physical_run_id"], "fresh__r1")
            fresh = next(
                member
                for member in provenance["members"]
                if member["run_id"] == "fresh"
            )
            self.assertEqual(
                fresh["preceding_campaign_cooldown"]["result"],
                "first_run_exempt",
            )

    def test_first_run_exemption_resets_for_each_physical_campaign_session(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            config_dir = tmp_path / "configs"
            runs_dir = tmp_path / "runs"
            config_dir.mkdir()
            write_config(config_dir, "01-a.json", "a")
            fake_cli = make_fake_cli(tmp_path)

            first = run_campaign(config_dir, runs_dir, cli_cmd=cli_cmd_for(fake_cli))
            write_config(config_dir, "02-b.json", "b")
            second = run_campaign(config_dir, runs_dir, cli_cmd=cli_cmd_for(fake_cli))

            self.assertEqual(first.returncode, 0, first.stderr)
            self.assertEqual(second.returncode, 0, second.stderr)
            manifests = sorted((runs_dir / "campaign_manifests").glob("*.json"))
            self.assertEqual(len(manifests), 2)
            sessions = [json.loads(path.read_text(encoding="utf-8")) for path in manifests]
            self.assertEqual(
                {session["first_physical_run_id"] for session in sessions},
                {"a", "b"},
            )
            for session in sessions:
                first_member = next(
                    member
                    for member in session["members"]
                    if member["run_id"] == session["first_physical_run_id"]
                )
                self.assertEqual(
                    first_member["preceding_campaign_cooldown"]["result"],
                    "first_run_exempt",
                )

    def test_p2038_shakedown_requires_backup_and_exactly_one_config(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            config_dir = tmp_path / "configs"
            runs_dir = tmp_path / "runs"
            config_dir.mkdir()
            write_config(config_dir, "one.json", "one")
            missing_backup = run_campaign(
                config_dir, runs_dir, shakedown_gate=True
            )
            self.assertEqual(missing_backup.returncode, 2)
            self.assertIn("requires --backup", missing_backup.stderr)

            write_config(config_dir, "two.json", "two")
            backup = tmp_path / "backup.sh"
            backup.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
            os.chmod(backup, 0o755)
            too_many = run_campaign(
                config_dir,
                runs_dir,
                backup=backup,
                shakedown_gate=True,
            )
            self.assertEqual(too_many.returncode, 2)
            self.assertIn("exactly one", too_many.stderr)

    def test_p2038_shakedown_rejects_mock_backend_with_named_gate_row(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            config_dir = tmp_path / "configs"
            runs_dir = tmp_path / "runs"
            config_dir.mkdir()
            write_config(config_dir, "one.json", "one")
            fake_cli = make_fake_cli(tmp_path)
            backup = tmp_path / "backup.sh"
            backup.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
            os.chmod(backup, 0o755)

            result = run_campaign(
                config_dir,
                runs_dir,
                cli_cmd=cli_cmd_for(fake_cli),
                backup=backup,
                shakedown_gate=True,
            )

            self.assertEqual(result.returncode, 1)
            self.assertIn(
                "SHAKEDOWN_GATE_FAILED[not_production_backend]", result.stderr
            )
            rows = read_all_jsonl(runs_dir / "campaign_log.jsonl")
            gate = next(row for row in rows if row.get("record_type") == "shakedown_gate")
            self.assertEqual(gate["status"], "failed")
            self.assertEqual(gate["code"], "not_production_backend")

    def test_p2038_shakedown_backup_launch_failure_has_named_failed_gate_row(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            bundle = root / "bundle"
            bundle.mkdir()
            log_path = root / "campaign_log.jsonl"
            completed = subprocess.CompletedProcess([], 0)
            with (
                patch("scripts.run_campaign.validate_bundle", return_value=[]),
                patch("scripts.run_campaign.subprocess.run", return_value=completed),
                patch(
                    "scripts.run_campaign.assert_production_uncertainty",
                    return_value={"bundle_id": bundle.name},
                ),
                patch(
                    "scripts.run_campaign.backup_runs",
                    side_effect=FileNotFoundError("backup executable missing"),
                ),
            ):
                with self.assertRaises(ShakedownGateError) as raised:
                    execute_production_uncertainty_gate(
                        bundle, root, str(root / "missing-backup")
                    )
            error = raised.exception
            self.assertEqual(error.code, "backup_failed")
            rendered = (
                f"SHAKEDOWN_GATE_FAILED[{error.code}] bundle={error.bundle_id} "
                f"detail={error.detail}"
            )
            self.assertIn("SHAKEDOWN_GATE_FAILED[backup_failed]", rendered)
            append_log(
                log_path,
                failed_shakedown_record("production_uncertainty_v1", error),
            )
            gate = read_all_jsonl(log_path)[0]
            self.assertEqual(gate["status"], "failed")
            self.assertEqual(gate["code"], "backup_failed")


def _idle_admission_extension_mapping(profile: str) -> dict:
    mapping = {
        "schema_version": "joulewise.idle_admission_extension.v1",
        "policy_version": "idle-admission-core-v1",
        "claim_bearing": True,
        "cpu_criteria": {
            "cpu_busy_ratio_p95_max": 0.5,
            "processor_combined_power_w_p95_max": 1.0,
            "min_samples": 3,
            "on_missing_telemetry": "fail",
        },
        "adapter_wattage": {"require_known_wattage": True},
        "neg8_bracket": {
            "require_bracket": True,
            "max_abs_delta_j": 0.5,
            "max_rel_delta": 0.0625,
        },
    }
    if profile == "exploratory":
        mapping["claim_bearing"] = False
        mapping["cpu_criteria"]["on_missing_telemetry"] = "flag"
        mapping["adapter_wattage"]["require_known_wattage"] = False
        mapping["neg8_bracket"]["require_bracket"] = False
    return mapping


def _clean_idle_records(count: int = 5) -> list[dict]:
    return [
        {
            "processor_combined_power_w": 0.15,
            "clusters": [
                {
                    "cpus": [
                        {"idle_ratio": 0.95, "down_ratio": 0.0},
                        {"idle_ratio": 0.99, "down_ratio": 0.0},
                    ]
                }
            ],
        }
        for _ in range(count)
    ]


class IdleAdmissionCoreVerdictTests(unittest.TestCase):
    """T0.5 idle-admission core: sidecar binding + campaign-verdict surface."""

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.root = Path(self._tmp.name)

    def _write_extended_sidecar(
        self, profile: str = "production", mutate=None
    ) -> Path:
        source = (
            ROOT
            / "configs"
            / "campaign_policies"
            / (
                "quiet_mac_p2_production.json"
                if profile == "production"
                else "quiet_mac_exploratory.json"
            )
        )
        payload = json.loads(source.read_text(encoding="utf-8"))
        payload["idle_admission_extension"] = _idle_admission_extension_mapping(
            profile
        )
        if mutate is not None:
            mutate(payload)
        path = self.root / f"policy_{profile}.json"
        path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
        return path

    def _binding(self, *, profile: str = "production"):
        return run_campaign_module.load_campaign_policy(
            str(self._write_extended_sidecar(profile))
        )

    def _member(
        self,
        bundle_id: str,
        *,
        records: list[dict] | None,
        adapter_watts=140,
        adapter_description="140W USB-C Power Adapter",
        gross_energy_j: float | None = None,
        admission_decision: str | None = "admitted",
    ):
        bundle_path = self.root / bundle_id
        bundle_path.mkdir(parents=True, exist_ok=True)
        if records is not None:
            (bundle_path / "rich_telemetry_idle.jsonl").write_text(
                "".join(json.dumps(record) + "\n" for record in records)
            )
        metadata: dict = {
            "environment": {
                "power_source": "AC Power",
                "power": {
                    "adapter_watts": adapter_watts,
                    "adapter_description": adapter_description,
                },
            }
        }
        if admission_decision is not None:
            metadata["environment_admission"] = {"decision": admission_decision}
        summary = (
            {"gross_energy_j": gross_energy_j} if gross_energy_j is not None else {}
        )
        return run_campaign_module.MemberEvaluation(
            bundle_id=bundle_id,
            bundle_path=bundle_path,
            config_name=f"{bundle_id}.json",
            status="succeeded",
            strict_valid=True,
            summary=summary,
            metadata=metadata,
        )

    def test_load_campaign_policy_parses_and_hash_binds_extension(self) -> None:
        path = self._write_extended_sidecar("production")
        binding = run_campaign_module.load_campaign_policy(str(path))
        self.assertIsNotNone(binding.idle_admission_extension)
        self.assertTrue(binding.idle_admission_extension.claim_bearing)
        self.assertEqual(
            binding.sha256, hashlib.sha256(path.read_bytes()).hexdigest()
        )
        metadata = binding.to_metadata()
        self.assertEqual(
            metadata["idle_admission_extension"]["schema_version"],
            "joulewise.idle_admission_extension.v1",
        )
        # Byte-hash enforcement: changing one new field changes the campaign
        # policy identity (binding hash) and the extension hash.
        changed = self._write_extended_sidecar(
            "production",
            mutate=lambda payload: payload["idle_admission_extension"][
                "cpu_criteria"
            ].update(cpu_busy_ratio_p95_max=0.6),
        )
        rebound = run_campaign_module.load_campaign_policy(str(changed))
        self.assertNotEqual(binding.sha256, rebound.sha256)
        self.assertNotEqual(
            metadata["idle_admission_extension"]["sha256"],
            rebound.to_metadata()["idle_admission_extension"]["sha256"],
        )

    def test_extension_version_and_profile_constraints_fail_closed(self) -> None:
        from joulewise.idle_admission import IdleAdmissionPolicyError

        tampered = self._write_extended_sidecar(
            "production",
            mutate=lambda payload: payload["idle_admission_extension"].update(
                schema_version="joulewise.idle_admission_extension.v0"
            ),
        )
        with self.assertRaises(IdleAdmissionPolicyError):
            run_campaign_module.load_campaign_policy(str(tampered))
        loosened = self._write_extended_sidecar(
            "production",
            mutate=lambda payload: payload["idle_admission_extension"][
                "cpu_criteria"
            ].update(on_missing_telemetry="flag"),
        )
        with self.assertRaises(IdleAdmissionPolicyError):
            run_campaign_module.load_campaign_policy(str(loosened))

    def test_sidecar_without_extension_yields_named_condition(self) -> None:
        binding = run_campaign_module.load_campaign_policy(
            str(ROOT / "tests" / "fixtures" / "campaign_policy_test.json")
        )
        self.assertIsNone(binding.idle_admission_extension)
        section = run_campaign_module.idle_admission_core_verdict([], binding)
        self.assertEqual(
            section["conditions"], ["idle_admission_extension_unconfigured"]
        )
        self.assertIsNone(section["extension"])

    def test_clean_members_pass_with_stable_wattage_and_neg8_bracket(self) -> None:
        binding = self._binding()
        evaluations = [
            self._member(
                "p2-neg8-reference-start__r1",
                records=_clean_idle_records(),
                gross_energy_j=8.0,
            ),
            self._member("p2-work-a__r1", records=_clean_idle_records()),
            self._member(
                "p2-neg8-reference-end__r1",
                records=_clean_idle_records(),
                gross_energy_j=8.5,
            ),
        ]
        section = run_campaign_module.idle_admission_core_verdict(
            evaluations, binding
        )
        self.assertEqual(section["conditions"], [])
        self.assertTrue(
            all(row["cpu_admission"]["admitted"] for row in section["members"])
        )
        self.assertEqual(
            section["adapter_wattage_continuity"]["decision"], "stable"
        )
        self.assertEqual(section["neg8_bracket"]["decision"], "passed")
        self.assertEqual(section["neg8_bracket"]["abs_delta_j"], 0.5)

    def test_missing_idle_telemetry_fails_closed_under_production(self) -> None:
        binding = self._binding()
        evaluations = [self._member("p2-work-a__r1", records=None)]
        section = run_campaign_module.idle_admission_core_verdict(
            evaluations, binding
        )
        member = section["members"][0]["cpu_admission"]
        self.assertEqual(member["decision"], "failed")
        self.assertIn("cpu_baseline_telemetry_missing", section["conditions"])

    def test_cpu_active_member_fails_and_is_named(self) -> None:
        binding = self._binding()
        active = [
            {
                "processor_combined_power_w": 0.2,
                "clusters": [{"cpus": [{"idle_ratio": 0.05, "down_ratio": 0.0}]}],
            }
            for _ in range(5)
        ]
        section = run_campaign_module.idle_admission_core_verdict(
            [self._member("p2-work-a__r1", records=active)], binding
        )
        self.assertIn("cpu_busy_ratio_p95_exceeded", section["conditions"])
        self.assertEqual(
            section["members"][0]["cpu_admission"]["decision"], "failed"
        )

    def test_wattage_discontinuity_and_description_change_are_named(self) -> None:
        binding = self._binding()
        evaluations = [
            self._member("m1__r1", records=_clean_idle_records(), adapter_watts=140),
            self._member("m2__r1", records=_clean_idle_records(), adapter_watts=70),
            self._member("m3__r1", records=_clean_idle_records(), adapter_watts=140),
            self._member(
                "m4__r1",
                records=_clean_idle_records(),
                adapter_watts=140,
                adapter_description="96W USB-C Power Adapter",
            ),
        ]
        section = run_campaign_module.idle_admission_core_verdict(
            evaluations, binding
        )
        continuity = section["adapter_wattage_continuity"]
        self.assertEqual(continuity["decision"], "flagged")
        self.assertIn("adapter_wattage_discontinuity", section["conditions"])
        self.assertIn("adapter_description_changed", section["conditions"])
        self.assertEqual(
            [
                (row["from_watts"], row["to_watts"])
                for row in continuity["wattage_transitions"]
            ],
            [(140.0, 70.0), (70.0, 140.0)],
        )

    def test_unknown_adapter_wattage_fails_closed_under_production(self) -> None:
        binding = self._binding()
        section = run_campaign_module.idle_admission_core_verdict(
            [
                self._member(
                    "m1__r1",
                    records=_clean_idle_records(),
                    adapter_watts=None,
                    adapter_description=None,
                )
            ],
            binding,
        )
        self.assertEqual(
            section["adapter_wattage_continuity"]["decision"], "failed"
        )
        self.assertIn("adapter_wattage_unknown", section["conditions"])

    def test_neg8_bracket_edge_cases_in_verdict(self) -> None:
        binding = self._binding()

        def section_for(end_gross: float | None) -> dict:
            evaluations = [
                self._member(
                    "p2-neg8-reference-start__r1",
                    records=_clean_idle_records(),
                    gross_energy_j=8.0,
                )
            ]
            if end_gross is not None:
                evaluations.append(
                    self._member(
                        "p2-neg8-reference-end__r1",
                        records=_clean_idle_records(),
                        gross_energy_j=end_gross,
                    )
                )
            return run_campaign_module.idle_admission_core_verdict(
                evaluations, binding
            )

        exactly_on = section_for(8.5)
        self.assertEqual(exactly_on["neg8_bracket"]["decision"], "passed")
        one_ulp_over = section_for(math.nextafter(8.5, math.inf))
        self.assertEqual(one_ulp_over["neg8_bracket"]["decision"], "failed")
        missing = section_for(None)
        self.assertEqual(missing["neg8_bracket"]["decision"], "failed")
        self.assertIn("neg8_bracket_missing", missing["conditions"])


if __name__ == "__main__":
    unittest.main()
