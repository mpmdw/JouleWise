from __future__ import annotations

import copy
import importlib.util
import json
import hashlib
import os
import shlex
import subprocess
import sys
import tempfile
import textwrap
import unittest
from dataclasses import replace as dataclass_replace
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "run_campaign.py"
BASE_CONFIG = ROOT / "configs" / "examples" / "mock_local.json"
SUITE_CONFIG = ROOT / "configs" / "examples" / "mock_suite_local.json"
COMMAND_TIMEOUT_S = 60
GENERATOR = ROOT / "scripts" / "generate_matrix.py"

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
) -> subprocess.CompletedProcess[str]:
    command = [sys.executable, str(SCRIPT), str(config_dir), "--runs-dir", str(runs_dir)]
    if log_path is not None:
        command.extend(["--log", str(log_path)])
    if dry_run:
        command.append("--dry-run")
    if backup is not None:
        command.extend(["--backup", str(backup)])
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
) -> Path:
    path = config_dir / filename
    payload = json.loads(SUITE_CONFIG.read_text(encoding="utf-8"))
    payload["run_id"] = run_id
    if suite_manifest is not None:
        payload["workload_profile"]["suite_manifest_ref"] = str(suite_manifest)
    if sidecar is not None:
        payload["workload_profile"]["generator_sidecar_ref"] = str(sidecar)
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
) -> None:
    _write_bundle(
        runs_dir,
        run_id,
        status,
        idle_window_suspect=idle_window_suspect,
        config_path=config_path,
        start_s=start_s,
    )


def write_experiment(
    runs_dir: Path,
    run_id: str,
    repetitions: int,
    *,
    statuses: list[str] | None = None,
    completed: int | None = None,
) -> None:
    if statuses is None:
        statuses = ["succeeded"] * repetitions
    if completed is None:
        completed = repetitions
    members: list[str] = []
    for rep in range(1, completed + 1):
        member_name = f"{run_id}__r{rep}"
        members.append(member_name)
        _write_bundle(runs_dir, member_name, statuses[rep - 1])
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
) -> None:
    from joulewise import reduce as reduce_module
    from joulewise.bundle import RunBundleWriter
    from joulewise.clock import FakeClock
    from joulewise.interfaces import PowerSample, RuntimeEvent
    from joulewise.provenance import output_policy, prompt_provenance
    from joulewise.schemas import BenchmarkConfig, FailureReason, RunStatus, SummaryMetrics

    source_config = config_path if config_path is not None else BASE_CONFIG
    config_data = json.loads(source_config.read_text(encoding="utf-8"))
    config_data["run_id"] = run_id
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
        writer.write_metadata(
            {
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
        )
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
            BASE_CONFIG = ROOT / "configs" / "examples" / "mock_local.json"
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
                config_data["workload_profile"]["repetitions"] = 1
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
                            "idle_baseline": {{
                                "power_w_mean": 5.0,
                                "power_w_stddev": 0.0,
                                "duration_s": 1.0,
                                "sample_count": 2,
                                "telemetry_backend": telemetry_backend,
                                "idle_window_suspect": False,
                            }},
                            "idle_drift_bound_w": 0.0,
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


def write_two_member_analysis_manifest(config_dir: Path) -> None:
    configs = [config_dir / "a.json", config_dir / "b.json"]
    order = {
        "executed_order": [
            {"index": index, "config": path.name, "run_id": path.stem}
            for index, path in enumerate(configs, start=1)
        ]
    }
    order_bytes = (json.dumps(order, indent=2) + "\n").encode("utf-8")
    (config_dir / "order_manifest.json").write_bytes(order_bytes)
    entries = []
    for path, cell_id in zip(configs, ("cell-a", "cell-b"), strict=True):
        payload = json.loads(path.read_text(encoding="utf-8"))
        entries.append(
            {
                "entry_id": f"entry-{path.stem}",
                "config": path.name,
                "config_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                "run_id": payload["run_id"],
                "cell_id": cell_id,
                "block_id": "block-1",
            }
        )
    manifest = {
        "schema_version": "joulewise.analysis_manifest.v1",
        "manifest_id": None,
        "freeze_status": "frozen",
        "design": {
            "sampling_plan": {"design": "fixed_n", "planned_n_blocks": 1}
        },
        "source": {
            "order_manifest": {"sha256": hashlib.sha256(order_bytes).hexdigest()}
        },
        "entries": entries,
        "contrasts": [
            {
                "contrast_id": "ctr-b-minus-a",
                "metric": {
                    "name": "gross_energy_j",
                    "window_class": "gross_request",
                },
                "cell_a_id": "cell-a",
                "cell_b_id": "cell-b",
                "block_ids": ["block-1"],
            }
        ],
    }
    identity_payload = dict(manifest)
    identity_payload.pop("manifest_id")
    canonical = json.dumps(
        identity_payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")
    manifest["manifest_id"] = "am-" + hashlib.sha256(canonical).hexdigest()
    (config_dir / "analysis_manifest.json").write_text(
        json.dumps(manifest, indent=2) + "\n", encoding="utf-8"
    )


def write_prior_campaign_provenance(
    runs_dir: Path,
    evidence_by_bundle: dict[str, str],
    analysis_manifest_id: str,
) -> None:
    manifest_dir = runs_dir / "campaign_manifests"
    manifest_dir.mkdir(parents=True, exist_ok=True)
    raw_dir = manifest_dir / "raw"
    raw_dir.mkdir(parents=True, exist_ok=True)
    raw_payload = json.dumps({"rolling_mean_power_w": 5.0}) + "\n"
    (raw_dir / "fixture.jsonl").write_text(raw_payload, encoding="utf-8")
    raw_sha = hashlib.sha256(raw_payload.encode("utf-8")).hexdigest()
    session_id = "campaign-fixture"
    members = []
    for bundle_id, result in evidence_by_bundle.items():
        cooldown = {
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
                "execution": "fixture",
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


def analysis_manifest_id(config_dir: Path) -> str:
    return json.loads(
        (config_dir / "analysis_manifest.json").read_text(encoding="utf-8")
    )["manifest_id"]


def write_strict_analysis_campaign(
    config_dir: Path,
    runs_dir: Path | None = None,
    *,
    telemetry_backend: str = "wall_meter",
) -> tuple[dict, dict[str, float]]:
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
    starts: dict[str, float] = {}
    if runs_dir is not None:
        for index, entry in enumerate(manifest["entries"]):
            run_id = entry["run_id"]
            start_s = float(index * 400)
            starts[run_id] = start_s
            write_single_bundle(
                runs_dir,
                run_id,
                config_path=config_dir / entry["config"],
                start_s=start_s,
            )
    return manifest, starts


def write_verifiable_campaign_provenance(
    runs_dir: Path,
    manifest: dict,
    starts: dict[str, float],
    *,
    result_overrides: dict[str, str] | None = None,
    fabricated_run_id: str | None = None,
    omit_raw_for: set[str] | None = None,
    all_first_run_exempt: bool = False,
) -> Path:
    result_overrides = result_overrides or {}
    omit_raw_for = omit_raw_for or set()
    manifest_dir = runs_dir / "campaign_manifests"
    raw_dir = manifest_dir / "raw"
    raw_dir.mkdir(parents=True, exist_ok=True)
    session_id = "campaign-verifiable-fixture"
    members: list[dict] = []
    cooldown_gates: list[dict] = []
    entries = manifest["entries"]
    for index, entry in enumerate(entries):
        run_id = entry["run_id"]
        bundle_ids = [run_id]
        if index == 0 or all_first_run_exempt:
            note = {
                "result": "first_run_exempt",
                "session_id": session_id,
                "following_run_id": run_id,
                "following_bundle_ids": bundle_ids,
                "recorded_at": "2026-07-10T00:00:00Z",
            }
        else:
            preceding_run_id = entries[index - 1]["run_id"]
            preceding_bundle_config = json.loads(
                (runs_dir / preceding_run_id / "config.json").read_text(
                    encoding="utf-8"
                )
            )
            trace_backend = preceding_bundle_config["hardware_target"][
                "telemetry_backend"
            ]
            result = result_overrides.get(run_id, "recovered")
            gate_started_at_s = starts[preceding_run_id] + 2.0
            waited_s = 300.0 if result == "cap_hit" else 5.0
            subwindow_power_w = 7.0 if result == "cap_hit" else 5.0
            cooldown_run_id = f"{session_id}-cooldown-before-{run_id}"
            note = {
                "result": result,
                "session_id": session_id,
                "preceding_run_id": preceding_run_id,
                "preceding_bundle_id": preceding_run_id,
                "following_run_id": run_id,
                "following_bundle_ids": bundle_ids,
                "recorded_at": "2026-07-10T00:00:00Z",
                "cooldown_run_id": cooldown_run_id,
                "waited_s": waited_s,
                "reference_power_w": 5.0,
                "tolerance_fraction": 0.1,
                "decision_rolling_mean_power_w": subwindow_power_w,
                "gate_started_at_s": gate_started_at_s,
            }
            if run_id not in omit_raw_for:
                if run_id == fabricated_run_id:
                    payload = json.dumps({"rolling_mean_power_w": 5.0}) + "\n"
                else:
                    trace_row = {
                        "schema_version": "joulewise.campaign_cooldown_trace.v2",
                        "session_id": session_id,
                        "cooldown_run_id": cooldown_run_id,
                        "sample_index": 0,
                        "preceding_run_id": preceding_run_id,
                        "preceding_bundle_id": preceding_run_id,
                        "following_run_id": run_id,
                        "following_bundle_ids": bundle_ids,
                        "gate_started_at_s": gate_started_at_s,
                        "timestamp_s": gate_started_at_s + waited_s,
                        "waited_s": waited_s,
                        "rolling_mean_power_w": subwindow_power_w,
                        "baseline": {
                            "power_w_mean": subwindow_power_w,
                            "power_w_stddev": 0.0,
                            "duration_s": 5.0,
                            "sample_count": 5,
                            "telemetry_backend": trace_backend,
                            "gpu_idle_ratio_mean": None,
                            "gpu_idle_ratio_min": None,
                            "gpu_freq_hz_mean": None,
                            "idle_window_suspect": None,
                        },
                    }
                    payload = json.dumps(trace_row, sort_keys=True) + "\n"
                raw_name = f"fixture-before-{run_id}.jsonl"
                (raw_dir / raw_name).write_text(payload, encoding="utf-8")
                note["raw_artifact"] = {
                    "path": f"raw/{raw_name}",
                    "sha256": hashlib.sha256(payload.encode("utf-8")).hexdigest(),
                    "records": 1,
                }
            cooldown_gates.append(note)
        members.append(
            {
                "config": entry["config"],
                "run_id": run_id,
                "bundle_ids": bundle_ids,
                "execution": "fixture",
                "preceding_campaign_cooldown": note,
            }
        )
    path = manifest_dir / "verifiable-fixture.json"
    path.write_text(
        json.dumps(
            {
                "schema_version": "joulewise.campaign_provenance.v1",
                "session_id": session_id,
                "created_at": "2026-07-10T00:00:00Z",
                "config_dir": "fixture",
                "analysis_manifest_id": manifest["manifest_id"],
                "first_physical_run_id": entries[0]["run_id"],
                "members": members,
                "cooldown_gates": cooldown_gates,
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    return path


def load_direct_readiness_fixture(
    config_dir: Path,
    runs_dir: Path,
) -> tuple[object, list, object]:
    state = run_campaign_module.load_analysis_manifest(config_dir)
    assert state is not None and state.valid, state.problems if state else None
    frozen = run_campaign_module.frozen_order_run_ids(state)
    cooldown = run_campaign_module.prior_campaign_cooldown_evidence(
        runs_dir, state.manifest_id, frozen
    )
    notes = {
        bundle_id: validation.effective_note()
        for bundle_id, validation in cooldown.by_bundle.items()
    }
    evaluations = []
    for entry in state.raw["entries"]:
        info = run_campaign_module.load_config_info(config_dir / entry["config"])
        evaluations.extend(
            run_campaign_module.evaluate_members(info, runs_dir, {}, notes)
        )
    return state, evaluations, cooldown


def contrast_evaluation(
    state: object,
    evaluations: list,
    metric_tag: str,
) -> tuple[dict, object]:
    contrast = next(
        row for row in state.raw["contrasts"] if row["metric"]["metric_tag"] == metric_tag
    )
    entry = next(
        row
        for row in state.raw["entries"]
        if row["block_id"] == contrast["block_ids"][0]
        and row["cell_id"] == contrast["cell_a_id"]
    )
    evaluation = next(row for row in evaluations if row.bundle_id == entry["run_id"])
    return contrast, evaluation


class RunCampaignTests(unittest.TestCase):
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
            write_config(config_dir, "complete.json", "complete-exp", repetitions=5)
            write_experiment(runs_dir, "complete-exp", 5)
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
            write_config(config_dir, "failed-member.json", "failed-member-exp", repetitions=5)
            write_experiment(
                runs_dir,
                "failed-member-exp",
                5,
                statuses=["succeeded", "succeeded", "failed", "succeeded", "succeeded"],
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

    def test_waiver_allows_invalid_existing_member_and_records_partial_verdict(self) -> None:
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
            self.assertIn("verdict: partial", result.stdout)
            rows = read_jsonl(runs_dir / "campaign_log.jsonl")
            self.assertEqual([row["status"] for row in rows], ["skipped", "waived"])
            all_rows = read_all_jsonl(runs_dir / "campaign_log.jsonl")
            verdict = all_rows[-1]
            self.assertEqual(verdict["record_type"], "campaign_verdict")
            self.assertEqual(verdict["collection"]["verdict"], "partial")
            self.assertEqual(verdict["collection"]["categories"]["usable"], ["good"])
            self.assertEqual(verdict["collection"]["categories"]["waived"], ["idle"])
            self.assertEqual(verdict["analysis_readiness"]["verdict"], "not_assessed")

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

    def test_waiver_scope_must_cover_failure_classes(self) -> None:
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

            self.assertEqual(result.returncode, 1)
            rows = read_jsonl(runs_dir / "campaign_log.jsonl")
            self.assertEqual(rows[0]["status"], "failed")
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
            write_single_bundle(runs_dir, "idle", idle_window_suspect=True)
            waivers.write_text(
                json.dumps(
                    [
                        {
                            "bundle_id": "idle",
                            "reason": "all waived is not claim evidence",
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

            self.assertEqual(result.returncode, 1)
            all_rows = read_all_jsonl(runs_dir / "campaign_log.jsonl")
            verdict = all_rows[-1]
            self.assertEqual(verdict["collection"]["verdict"], "invalid")
            self.assertEqual(verdict["collection"]["categories"]["waived"], ["idle"])

    def test_one_bundle_campaign_is_usable_and_analysis_readiness_not_assessed(self) -> None:
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
            self.assertIn("ANALYSIS READINESS:", result.stdout)
            self.assertNotIn("publish" + "able", result.stdout)
            all_rows = read_all_jsonl(runs_dir / "campaign_log.jsonl")
            self.assertEqual(all_rows[-1]["record_type"], "campaign_verdict")
            self.assertEqual(
                all_rows[-1]["schema_version"], "joulewise.campaign_verdict.v2"
            )
            self.assertEqual(all_rows[-1]["collection"]["verdict"], "usable")
            self.assertEqual(
                all_rows[-1]["analysis_readiness"]["verdict"], "not_assessed"
            )
            self.assertEqual(
                all_rows[-1]["collection"]["categories"]["usable"], ["one"]
            )
            self.assertEqual(
                all_rows[-1]["collection"]["categories"]["failed"], []
            )

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
            readiness = verdict["analysis_readiness"]
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
            manifest, starts = write_strict_analysis_campaign(config_dir, runs_dir)
            target = next(
                entry["run_id"]
                for entry in manifest["entries"]
                if entry["role"] == "condition"
            )
            write_verifiable_campaign_provenance(
                runs_dir, manifest, starts, result_overrides={target: "cap_hit"}
            )

            result = run_campaign(config_dir, runs_dir)

            self.assertEqual(result.returncode, 0, result.stderr)
            verdict = read_all_jsonl(runs_dir / "campaign_log.jsonl")[-1]
            self.assertEqual(verdict["collection"]["verdict"], "usable")
            self.assertEqual(
                verdict["analysis_readiness"]["verdict"], "not_ready_for_analysis"
            )
            self.assertIn("cooldown_cap_hit", verdict["analysis_readiness"]["reasons"])

    def test_verifiable_cooldown_reaches_direct_ready_path_before_scope_gate(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            config_dir = tmp_path / "configs"
            runs_dir = tmp_path / "runs"
            config_dir.mkdir()
            manifest, starts = write_strict_analysis_campaign(config_dir, runs_dir)
            write_verifiable_campaign_provenance(runs_dir, manifest, starts)
            state, evaluations, cooldown = load_direct_readiness_fixture(
                config_dir, runs_dir
            )

            readiness = run_campaign_module.analysis_readiness_for(
                state,
                "usable",
                evaluations,
                cooldown,
                {"reasons": []},
            )

            self.assertEqual(readiness["verdict"], "ready_for_analysis")
            self.assertEqual(
                readiness["ready_contrast_ids"],
                [row["contrast_id"] for row in manifest["contrasts"]],
            )

    def test_synthesized_one_line_cooldown_note_is_unverifiable_and_not_ready(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            config_dir = tmp_path / "configs"
            runs_dir = tmp_path / "runs"
            config_dir.mkdir()
            manifest, starts = write_strict_analysis_campaign(config_dir, runs_dir)
            target = next(
                entry["run_id"]
                for entry in manifest["entries"]
                if entry["role"] == "condition"
            )
            write_verifiable_campaign_provenance(
                runs_dir,
                manifest,
                starts,
                fabricated_run_id=target,
            )

            result = run_campaign(config_dir, runs_dir)

            self.assertEqual(result.returncode, 0, result.stderr)
            readiness = read_all_jsonl(runs_dir / "campaign_log.jsonl")[-1][
                "analysis_readiness"
            ]
            self.assertEqual(readiness["verdict"], "not_ready_for_analysis")
            self.assertIn("cooldown_evidence_unverifiable", readiness["reasons"])

    def test_cooldown_trace_record_count_mismatch_is_unverifiable(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            config_dir = tmp_path / "configs"
            runs_dir = tmp_path / "runs"
            config_dir.mkdir()
            manifest, starts = write_strict_analysis_campaign(config_dir, runs_dir)
            provenance_path = write_verifiable_campaign_provenance(
                runs_dir, manifest, starts
            )
            provenance = json.loads(provenance_path.read_text(encoding="utf-8"))
            provenance["members"][1]["preceding_campaign_cooldown"]["raw_artifact"][
                "records"
            ] = 2
            provenance_path.write_text(
                json.dumps(provenance, indent=2, sort_keys=True) + "\n",
                encoding="utf-8",
            )

            state, evaluations, cooldown = load_direct_readiness_fixture(
                config_dir, runs_dir
            )
            readiness = run_campaign_module.analysis_readiness_for(
                state, "usable", evaluations, cooldown, {"reasons": []}
            )

            self.assertEqual(readiness["verdict"], "not_ready_for_analysis")
            self.assertIn("cooldown_evidence_unverifiable", readiness["reasons"])

    def test_cooldown_trace_rejects_rehashed_spoofed_rolling_mean(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            config_dir = tmp_path / "configs"
            runs_dir = tmp_path / "runs"
            config_dir.mkdir()
            manifest, starts = write_strict_analysis_campaign(config_dir, runs_dir)
            provenance_path = write_verifiable_campaign_provenance(
                runs_dir, manifest, starts
            )
            provenance = json.loads(provenance_path.read_text(encoding="utf-8"))
            note = provenance["members"][1]["preceding_campaign_cooldown"]
            raw_path = provenance_path.parent / note["raw_artifact"]["path"]
            row = json.loads(raw_path.read_text(encoding="utf-8"))
            row["rolling_mean_power_w"] = 123.0
            payload = json.dumps(row, sort_keys=True) + "\n"
            raw_path.write_text(payload, encoding="utf-8")
            note["raw_artifact"]["sha256"] = hashlib.sha256(
                payload.encode("utf-8")
            ).hexdigest()
            provenance_path.write_text(
                json.dumps(provenance, indent=2, sort_keys=True) + "\n",
                encoding="utf-8",
            )

            state, evaluations, cooldown = load_direct_readiness_fixture(
                config_dir, runs_dir
            )
            readiness = run_campaign_module.analysis_readiness_for(
                state, "usable", evaluations, cooldown, {"reasons": []}
            )

            self.assertIn("cooldown_evidence_unverifiable", readiness["reasons"])

    def test_cooldown_trace_rederives_multirow_rolling_recovery_and_rejects_nonmonotonic(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            config_dir = tmp_path / "configs"
            runs_dir = tmp_path / "runs"
            config_dir.mkdir()
            manifest, starts = write_strict_analysis_campaign(config_dir, runs_dir)
            provenance_path = write_verifiable_campaign_provenance(
                runs_dir, manifest, starts
            )
            provenance = json.loads(provenance_path.read_text(encoding="utf-8"))
            note = provenance["members"][1]["preceding_campaign_cooldown"]
            raw_path = provenance_path.parent / note["raw_artifact"]["path"]
            template = json.loads(raw_path.read_text(encoding="utf-8"))
            first = copy.deepcopy(template)
            first["waited_s"] = 5.0
            first["timestamp_s"] = first["gate_started_at_s"] + 5.0
            first["rolling_mean_power_w"] = 7.0
            first["baseline"]["power_w_mean"] = 7.0
            second = copy.deepcopy(template)
            second["sample_index"] = 1
            second["waited_s"] = 10.0
            second["timestamp_s"] = second["gate_started_at_s"] + 10.0
            second["rolling_mean_power_w"] = 5.0
            second["baseline"]["power_w_mean"] = 3.0
            payload = "".join(
                json.dumps(row, sort_keys=True) + "\n" for row in (first, second)
            )
            raw_path.write_text(payload, encoding="utf-8")
            note["waited_s"] = 10.0
            note["decision_rolling_mean_power_w"] = 5.0
            note["raw_artifact"]["records"] = 2
            note["raw_artifact"]["sha256"] = hashlib.sha256(
                payload.encode("utf-8")
            ).hexdigest()
            provenance_path.write_text(
                json.dumps(provenance, indent=2, sort_keys=True) + "\n",
                encoding="utf-8",
            )

            state, evaluations, cooldown = load_direct_readiness_fixture(
                config_dir, runs_dir
            )
            ready = run_campaign_module.analysis_readiness_for(
                state, "usable", evaluations, cooldown, {"reasons": []}
            )
            self.assertEqual(ready["verdict"], "ready_for_analysis")
            self.assertEqual(second["baseline"]["power_w_mean"], 3.0)

            second["timestamp_s"] = first["timestamp_s"]
            bad_payload = "".join(
                json.dumps(row, sort_keys=True) + "\n" for row in (first, second)
            )
            raw_path.write_text(bad_payload, encoding="utf-8")
            provenance = json.loads(provenance_path.read_text(encoding="utf-8"))
            provenance["members"][1]["preceding_campaign_cooldown"]["raw_artifact"][
                "sha256"
            ] = hashlib.sha256(bad_payload.encode("utf-8")).hexdigest()
            provenance_path.write_text(
                json.dumps(provenance, indent=2, sort_keys=True) + "\n",
                encoding="utf-8",
            )
            _, evaluations, cooldown = load_direct_readiness_fixture(
                config_dir, runs_dir
            )
            not_ready = run_campaign_module.analysis_readiness_for(
                state, "usable", evaluations, cooldown, {"reasons": []}
            )
            self.assertEqual(not_ready["verdict"], "not_ready_for_analysis")
            self.assertIn("cooldown_evidence_unverifiable", not_ready["reasons"])

    def test_cooldown_trace_rejects_rehashed_wrong_member_binding(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            config_dir = tmp_path / "configs"
            runs_dir = tmp_path / "runs"
            config_dir.mkdir()
            manifest, starts = write_strict_analysis_campaign(config_dir, runs_dir)
            provenance_path = write_verifiable_campaign_provenance(
                runs_dir, manifest, starts
            )
            provenance = json.loads(provenance_path.read_text(encoding="utf-8"))
            note = provenance["members"][1]["preceding_campaign_cooldown"]
            raw_path = provenance_path.parent / note["raw_artifact"]["path"]
            row = json.loads(raw_path.read_text(encoding="utf-8"))
            row["preceding_bundle_id"] = "spoofed-member"
            payload = json.dumps(row, sort_keys=True) + "\n"
            raw_path.write_text(payload, encoding="utf-8")
            note["raw_artifact"]["sha256"] = hashlib.sha256(
                payload.encode("utf-8")
            ).hexdigest()
            provenance_path.write_text(
                json.dumps(provenance, indent=2, sort_keys=True) + "\n",
                encoding="utf-8",
            )

            state, evaluations, cooldown = load_direct_readiness_fixture(
                config_dir, runs_dir
            )
            readiness = run_campaign_module.analysis_readiness_for(
                state, "usable", evaluations, cooldown, {"reasons": []}
            )

            self.assertIn("cooldown_evidence_unverifiable", readiness["reasons"])

    def test_cooldown_trace_rejects_recorded_decision_mismatch(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            config_dir = tmp_path / "configs"
            runs_dir = tmp_path / "runs"
            config_dir.mkdir()
            manifest, starts = write_strict_analysis_campaign(config_dir, runs_dir)
            provenance_path = write_verifiable_campaign_provenance(
                runs_dir, manifest, starts
            )
            provenance = json.loads(provenance_path.read_text(encoding="utf-8"))
            provenance["members"][1]["preceding_campaign_cooldown"][
                "result"
            ] = "cap_hit"
            provenance_path.write_text(
                json.dumps(provenance, indent=2, sort_keys=True) + "\n",
                encoding="utf-8",
            )

            state, evaluations, cooldown = load_direct_readiness_fixture(
                config_dir, runs_dir
            )
            readiness = run_campaign_module.analysis_readiness_for(
                state, "usable", evaluations, cooldown, {"reasons": []}
            )

            self.assertIn("cooldown_evidence_unverifiable", readiness["reasons"])

    def test_cooldown_trace_rejects_invalid_baseline_semantics_and_zero_elapsed(self) -> None:
        mutations = (
            (
                "negative_duration",
                lambda row, note: row["baseline"].__setitem__("duration_s", -5.0),
            ),
            (
                "negative_stddev",
                lambda row, note: row["baseline"].__setitem__(
                    "power_w_stddev", -1.0
                ),
            ),
            (
                "fabricated_backend",
                lambda row, note: row["baseline"].__setitem__(
                    "telemetry_backend", "fabricated"
                ),
            ),
            (
                "ratio_out_of_range",
                lambda row, note: row["baseline"].__setitem__(
                    "gpu_idle_ratio_mean", 2.0
                ),
            ),
            (
                "negative_frequency",
                lambda row, note: row["baseline"].__setitem__(
                    "gpu_freq_hz_mean", -1.0
                ),
            ),
            (
                "null_gate_id",
                lambda row, note: (
                    row.__setitem__("cooldown_run_id", None),
                    note.__setitem__("cooldown_run_id", None),
                ),
            ),
            (
                "zero_elapsed_subwindow",
                lambda row, note: (
                    row.__setitem__("waited_s", 0.0),
                    row.__setitem__("gate_started_at_s", row["timestamp_s"]),
                    note.__setitem__("waited_s", 0.0),
                    note.__setitem__("gate_started_at_s", row["timestamp_s"]),
                ),
            ),
        )
        for name, mutate in mutations:
            with self.subTest(name=name), tempfile.TemporaryDirectory() as tmp:
                tmp_path = Path(tmp)
                config_dir = tmp_path / "configs"
                runs_dir = tmp_path / "runs"
                config_dir.mkdir()
                manifest, starts = write_strict_analysis_campaign(config_dir, runs_dir)
                provenance_path = write_verifiable_campaign_provenance(
                    runs_dir, manifest, starts
                )
                provenance = json.loads(provenance_path.read_text(encoding="utf-8"))
                note = provenance["members"][1]["preceding_campaign_cooldown"]
                raw_path = provenance_path.parent / note["raw_artifact"]["path"]
                row = json.loads(raw_path.read_text(encoding="utf-8"))
                mutate(row, note)
                payload = json.dumps(row, sort_keys=True) + "\n"
                raw_path.write_text(payload, encoding="utf-8")
                note["raw_artifact"]["sha256"] = hashlib.sha256(
                    payload.encode("utf-8")
                ).hexdigest()
                provenance_path.write_text(
                    json.dumps(provenance, indent=2, sort_keys=True) + "\n",
                    encoding="utf-8",
                )

                state, evaluations, cooldown = load_direct_readiness_fixture(
                    config_dir, runs_dir
                )
                readiness = run_campaign_module.analysis_readiness_for(
                    state, "usable", evaluations, cooldown, {"reasons": []}
                )

                self.assertEqual(readiness["verdict"], "not_ready_for_analysis")
                self.assertIn(
                    "cooldown_evidence_unverifiable", readiness["reasons"]
                )

    def test_fresh_readiness_rehashes_after_resume_validation(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            config_dir = tmp_path / "configs"
            runs_dir = tmp_path / "runs"
            config_dir.mkdir()
            manifest, starts = write_strict_analysis_campaign(config_dir, runs_dir)
            provenance_path = write_verifiable_campaign_provenance(
                runs_dir, manifest, starts
            )
            state = run_campaign_module.load_analysis_manifest(config_dir)
            assert state is not None and state.valid
            frozen = run_campaign_module.frozen_order_run_ids(state)
            resume_check = run_campaign_module.prior_campaign_cooldown_evidence(
                runs_dir, state.manifest_id, frozen
            )
            target = manifest["entries"][1]["run_id"]
            self.assertTrue(resume_check.by_bundle[target].verifiable)
            provenance = json.loads(provenance_path.read_text(encoding="utf-8"))
            raw_ref = provenance["members"][1]["preceding_campaign_cooldown"][
                "raw_artifact"
            ]
            raw_path = provenance_path.parent / raw_ref["path"]
            raw_path.write_bytes(raw_path.read_bytes() + b" ")

            _, evaluations, fresh_check = load_direct_readiness_fixture(
                config_dir, runs_dir
            )
            readiness = run_campaign_module.analysis_readiness_for(
                state, "usable", evaluations, fresh_check, {"reasons": []}
            )

            self.assertFalse(fresh_check.by_bundle[target].verifiable)
            self.assertIn("cooldown_evidence_unverifiable", readiness["reasons"])

    def test_invalid_utf8_cooldown_trace_fails_closed_without_crashing(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            config_dir = tmp_path / "configs"
            runs_dir = tmp_path / "runs"
            config_dir.mkdir()
            manifest, starts = write_strict_analysis_campaign(config_dir, runs_dir)
            provenance_path = write_verifiable_campaign_provenance(
                runs_dir, manifest, starts
            )
            provenance = json.loads(provenance_path.read_text(encoding="utf-8"))
            note = provenance["members"][1]["preceding_campaign_cooldown"]
            raw_path = provenance_path.parent / note["raw_artifact"]["path"]
            payload = b"\xff\n"
            raw_path.write_bytes(payload)
            note["raw_artifact"]["sha256"] = hashlib.sha256(payload).hexdigest()
            provenance_path.write_text(
                json.dumps(provenance, indent=2, sort_keys=True) + "\n",
                encoding="utf-8",
            )

            state, evaluations, cooldown = load_direct_readiness_fixture(
                config_dir, runs_dir
            )
            readiness = run_campaign_module.analysis_readiness_for(
                state, "usable", evaluations, cooldown, {"reasons": []}
            )

            self.assertEqual(readiness["verdict"], "not_ready_for_analysis")
            self.assertIn("cooldown_evidence_unverifiable", readiness["reasons"])

    def test_all_repetition_one_members_cannot_claim_first_run_exempt(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            config_dir = tmp_path / "configs"
            runs_dir = tmp_path / "runs"
            config_dir.mkdir()
            manifest, starts = write_strict_analysis_campaign(config_dir, runs_dir)
            write_verifiable_campaign_provenance(
                runs_dir,
                manifest,
                starts,
                all_first_run_exempt=True,
            )

            result = run_campaign(config_dir, runs_dir)

            self.assertEqual(result.returncode, 0, result.stderr)
            readiness = read_all_jsonl(runs_dir / "campaign_log.jsonl")[-1][
                "analysis_readiness"
            ]
            self.assertEqual(readiness["verdict"], "not_ready_for_analysis")
            self.assertIn("cooldown_evidence_unverifiable", readiness["reasons"])

    def test_one_first_run_exemption_cannot_fan_out_to_all_members(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            config_dir = tmp_path / "configs"
            runs_dir = tmp_path / "runs"
            config_dir.mkdir()
            manifest, starts = write_strict_analysis_campaign(config_dir, runs_dir)
            provenance_path = write_verifiable_campaign_provenance(
                runs_dir, manifest, starts
            )
            provenance = json.loads(provenance_path.read_text(encoding="utf-8"))
            all_run_ids = [entry["run_id"] for entry in manifest["entries"]]
            first = provenance["members"][0]
            first["bundle_ids"] = all_run_ids
            first["preceding_campaign_cooldown"]["following_bundle_ids"] = all_run_ids
            for member in provenance["members"][1:]:
                member["preceding_campaign_cooldown"] = None
            provenance_path.write_text(
                json.dumps(provenance, indent=2, sort_keys=True) + "\n",
                encoding="utf-8",
            )

            state, evaluations, cooldown = load_direct_readiness_fixture(
                config_dir, runs_dir
            )
            readiness = run_campaign_module.analysis_readiness_for(
                state, "usable", evaluations, cooldown, {"reasons": []}
            )

            self.assertEqual(readiness["verdict"], "not_ready_for_analysis")
            self.assertIn("cooldown_evidence_unverifiable", readiness["reasons"])

    def test_invalid_frozen_first_exemption_blocks_every_contrast_globally(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            config_dir = tmp_path / "configs"
            runs_dir = tmp_path / "runs"
            config_dir.mkdir()
            manifest, starts = write_strict_analysis_campaign(config_dir, runs_dir)
            provenance_path = write_verifiable_campaign_provenance(
                runs_dir, manifest, starts
            )
            provenance = json.loads(provenance_path.read_text(encoding="utf-8"))
            provenance["members"][0]["preceding_campaign_cooldown"][
                "raw_artifact"
            ] = provenance["members"][1]["preceding_campaign_cooldown"][
                "raw_artifact"
            ]
            provenance_path.write_text(
                json.dumps(provenance, indent=2, sort_keys=True) + "\n",
                encoding="utf-8",
            )

            state, evaluations, cooldown = load_direct_readiness_fixture(
                config_dir, runs_dir
            )
            readiness = run_campaign_module.analysis_readiness_for(
                state, "usable", evaluations, cooldown, {"reasons": []}
            )

            self.assertTrue(cooldown.problems)
            self.assertEqual(readiness["verdict"], "not_ready_for_analysis")
            self.assertIn("cooldown_evidence_unverifiable", readiness["reasons"])

    def test_crash_window_first_exemption_reservation_is_consumed_and_unverifiable(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            config_dir = tmp_path / "configs"
            runs_dir = tmp_path / "runs"
            config_dir.mkdir()
            manifest, _ = write_strict_analysis_campaign(config_dir, runs_dir)
            manifest_dir = runs_dir / "campaign_manifests"
            manifest_dir.mkdir(parents=True)
            reservation = manifest_dir / "crashed-before-member-record.json"
            reservation.write_text(
                json.dumps(
                    {
                        "schema_version": "joulewise.campaign_provenance.v1",
                        "session_id": "crashed-session",
                        "created_at": "2026-07-10T00:00:00Z",
                        "config_dir": str(config_dir),
                        "analysis_manifest_id": manifest["manifest_id"],
                        "first_physical_run_id": manifest["entries"][0]["run_id"],
                        "members": [],
                        "cooldown_gates": [],
                    }
                )
                + "\n",
                encoding="utf-8",
            )
            state = run_campaign_module.load_analysis_manifest(config_dir)
            assert state is not None and state.valid

            cooldown = run_campaign_module.prior_campaign_cooldown_evidence(
                runs_dir,
                state.manifest_id,
                run_campaign_module.frozen_order_run_ids(state),
            )

            self.assertEqual(cooldown.first_run_exemption_claims, 1)
            self.assertTrue(cooldown.problems)

    def test_mock_or_backend_mismatched_trace_cannot_authorize_recovery(self) -> None:
        for backend, mutate_trace in (("mock", False), ("wall_meter", True)):
            with self.subTest(backend=backend, mutate_trace=mutate_trace), tempfile.TemporaryDirectory() as tmp:
                tmp_path = Path(tmp)
                config_dir = tmp_path / "configs"
                runs_dir = tmp_path / "runs"
                config_dir.mkdir()
                manifest, starts = write_strict_analysis_campaign(
                    config_dir, runs_dir, telemetry_backend=backend
                )
                provenance_path = write_verifiable_campaign_provenance(
                    runs_dir, manifest, starts
                )
                if mutate_trace:
                    provenance = json.loads(
                        provenance_path.read_text(encoding="utf-8")
                    )
                    note = provenance["members"][1]["preceding_campaign_cooldown"]
                    raw_path = provenance_path.parent / note["raw_artifact"]["path"]
                    row = json.loads(raw_path.read_text(encoding="utf-8"))
                    row["baseline"]["telemetry_backend"] = "powermetrics"
                    payload = json.dumps(row, sort_keys=True) + "\n"
                    raw_path.write_text(payload, encoding="utf-8")
                    note["raw_artifact"]["sha256"] = hashlib.sha256(
                        payload.encode("utf-8")
                    ).hexdigest()
                    provenance_path.write_text(
                        json.dumps(provenance, indent=2, sort_keys=True) + "\n",
                        encoding="utf-8",
                    )
                state, evaluations, cooldown = load_direct_readiness_fixture(
                    config_dir, runs_dir
                )
                readiness = run_campaign_module.analysis_readiness_for(
                    state, "usable", evaluations, cooldown, {"reasons": []}
                )

                self.assertEqual(readiness["verdict"], "not_ready_for_analysis")
                self.assertIn(
                    "cooldown_evidence_unverifiable", readiness["reasons"]
                )

    def test_unregistered_matching_strict_valid_bundle_blocks_analysis_readiness(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            config_dir = tmp_path / "configs"
            runs_dir = tmp_path / "runs"
            extra_config = tmp_path / "top-up.json"
            config_dir.mkdir()
            manifest, starts = write_strict_analysis_campaign(config_dir, runs_dir)
            write_verifiable_campaign_provenance(runs_dir, manifest, starts)
            source = config_dir / manifest["entries"][1]["config"]
            payload = json.loads(source.read_text(encoding="utf-8"))
            payload["run_id"] = "unregistered-top-up"
            extra_config.write_text(json.dumps(payload) + "\n", encoding="utf-8")
            write_single_bundle(
                runs_dir,
                "unregistered-top-up",
                config_path=extra_config,
                start_s=99999.0,
            )

            result = run_campaign(config_dir, runs_dir)

            self.assertEqual(result.returncode, 0, result.stderr)
            verdict = read_all_jsonl(runs_dir / "campaign_log.jsonl")[-1]
            self.assertEqual(
                verdict["sampling_audit"]["unregistered_matching_bundle_ids"],
                ["unregistered-top-up"],
            )
            self.assertTrue(verdict["sampling_audit"]["top_up_suspected"])
            self.assertIn(
                "unregistered_matching_bundle",
                verdict["analysis_readiness"]["reasons"],
            )

    def test_wider_top_up_scope_is_named_and_fail_closed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            config_dir = tmp_path / "configs"
            runs_dir = tmp_path / "runs"
            config_dir.mkdir()
            manifest, starts = write_strict_analysis_campaign(config_dir, runs_dir)
            write_verifiable_campaign_provenance(runs_dir, manifest, starts)

            result = run_campaign(config_dir, runs_dir)

            self.assertEqual(result.returncode, 0, result.stderr)
            verdict = read_all_jsonl(runs_dir / "campaign_log.jsonl")[-1]
            self.assertEqual(
                verdict["sampling_audit"]["detection_scope"]["wider_scope_scan"],
                "out_of_reach",
            )
            self.assertIn(
                "top_up_detection_scope_incomplete",
                verdict["analysis_readiness"]["reasons"],
            )

    def test_gross_readiness_uses_gross_request_not_request_alias(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            config_dir = tmp_path / "configs"
            runs_dir = tmp_path / "runs"
            config_dir.mkdir()
            manifest, starts = write_strict_analysis_campaign(config_dir, runs_dir)
            write_verifiable_campaign_provenance(runs_dir, manifest, starts)
            state, evaluations, cooldown = load_direct_readiness_fixture(
                config_dir, runs_dir
            )
            contrast, evaluation = contrast_evaluation(
                state, evaluations, "gross_request"
            )
            summary = copy.deepcopy(evaluation.summary)
            summary["window_evidence_precheck"]["request"] = {
                "eligible": False,
                "reasons": ["deprecated_alias_must_not_be_consumed"],
            }
            summary["measurement_quality"]["idle_window_suspect"] = True
            mutated = dataclass_replace(evaluation, summary=summary)

            reasons = run_campaign_module._member_readiness_reasons(
                mutated, contrast, cooldown.by_bundle[evaluation.bundle_id]
            )

            self.assertNotIn("deprecated_alias_must_not_be_consumed", reasons)
            self.assertNotIn("idle_window_suspect", reasons)
            self.assertEqual(reasons, [])

    def test_idle_readiness_uses_idle_subtracted_request_precheck(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            config_dir = tmp_path / "configs"
            runs_dir = tmp_path / "runs"
            config_dir.mkdir()
            manifest, starts = write_strict_analysis_campaign(config_dir, runs_dir)
            write_verifiable_campaign_provenance(runs_dir, manifest, starts)
            state, evaluations, cooldown = load_direct_readiness_fixture(
                config_dir, runs_dir
            )
            contrast, evaluation = contrast_evaluation(state, evaluations, "idle_request")
            summary = copy.deepcopy(evaluation.summary)
            summary["window_evidence_precheck"]["request"] = {
                "eligible": True,
                "reasons": [],
            }
            summary["window_evidence_precheck"]["idle_subtracted_request"] = {
                "eligible": False,
                "reasons": ["drift_term_unknown"],
            }
            mutated = dataclass_replace(evaluation, summary=summary)

            reasons = run_campaign_module._member_readiness_reasons(
                mutated, contrast, cooldown.by_bundle[evaluation.bundle_id]
            )

            self.assertIn("drift_term_unknown", reasons)

    def test_current_era_claim_eligibility_only_never_becomes_ready(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            config_dir = tmp_path / "configs"
            runs_dir = tmp_path / "runs"
            config_dir.mkdir()
            manifest, starts = write_strict_analysis_campaign(config_dir, runs_dir)
            write_verifiable_campaign_provenance(runs_dir, manifest, starts)
            state, evaluations, cooldown = load_direct_readiness_fixture(
                config_dir, runs_dir
            )
            contrast, evaluation = contrast_evaluation(
                state, evaluations, "gross_request"
            )
            summary = copy.deepcopy(evaluation.summary)
            summary["claim_eligibility"] = summary.pop("window_evidence_precheck")
            mutated = dataclass_replace(evaluation, summary=summary)

            reasons = run_campaign_module._member_readiness_reasons(
                mutated, contrast, cooldown.by_bundle[evaluation.bundle_id]
            )

            self.assertIn("window_evidence_precheck_missing", reasons)

    def test_missing_null_nan_and_infinite_metric_emit_metric_missing_or_nonfinite(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            config_dir = tmp_path / "configs"
            runs_dir = tmp_path / "runs"
            config_dir.mkdir()
            manifest, starts = write_strict_analysis_campaign(config_dir, runs_dir)
            write_verifiable_campaign_provenance(runs_dir, manifest, starts)
            state, evaluations, cooldown = load_direct_readiness_fixture(
                config_dir, runs_dir
            )
            contrast, evaluation = contrast_evaluation(
                state, evaluations, "gross_request"
            )
            for value in ("missing", None, float("nan"), float("inf")):
                with self.subTest(value=value):
                    summary = copy.deepcopy(evaluation.summary)
                    if value == "missing":
                        del summary["gross_energy_j"]
                    else:
                        summary["gross_energy_j"] = value
                    mutated = dataclass_replace(evaluation, summary=summary)
                    reasons = run_campaign_module._member_readiness_reasons(
                        mutated,
                        contrast,
                        cooldown.by_bundle[evaluation.bundle_id],
                    )
                    self.assertIn("metric_missing_or_nonfinite", reasons)

    def test_verdict_binds_manifest_and_trace_hashes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            config_dir = tmp_path / "configs"
            runs_dir = tmp_path / "runs"
            config_dir.mkdir()
            manifest, starts = write_strict_analysis_campaign(config_dir, runs_dir)
            write_verifiable_campaign_provenance(runs_dir, manifest, starts)

            result = run_campaign(config_dir, runs_dir)

            self.assertEqual(result.returncode, 0, result.stderr)
            provenance = read_all_jsonl(runs_dir / "campaign_log.jsonl")[-1][
                "campaign_provenance"
            ]
            self.assertGreaterEqual(len(provenance["manifests"]), 2)
            for row in provenance["manifests"]:
                self.assertEqual(
                    row["sha256"],
                    hashlib.sha256(Path(row["path"]).read_bytes()).hexdigest(),
                )
            self.assertTrue(provenance["cooldown_artifacts"])
            for row in provenance["cooldown_artifacts"]:
                raw_path = Path(row["provenance_path"]).parent / row["path"]
                self.assertEqual(
                    row["sha256"], hashlib.sha256(raw_path.read_bytes()).hexdigest()
                )

    def test_analysis_manifest_config_hash_mismatch_refuses_execution(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            config_dir = tmp_path / "configs"
            runs_dir = tmp_path / "runs"
            sentinel = tmp_path / "invoked"
            config_dir.mkdir()
            manifest, _ = write_strict_analysis_campaign(config_dir)
            config_path = config_dir / manifest["entries"][1]["config"]
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
            self.assertIn("config_hash_mismatch", verdict["analysis_readiness"]["reasons"])

    def test_readiness_preflight_uses_real_validator_for_fixed_n_block_and_cell_mutations(self) -> None:
        from joulewise.analysis_manifest import calculate_manifest_id

        mutations = (
            (
                "fixed_n",
                lambda value: (
                    value["design"]["sampling_plan"].__setitem__(
                        "planned_n_blocks", 1
                    ),
                    [
                        contrast.__setitem__("block_ids", contrast["block_ids"][:1])
                        for contrast in value["contrasts"]
                    ],
                ),
                "requires fixed_n=5",
            ),
            (
                "duplicate_block",
                lambda value: value["contrasts"][0]["block_ids"].__setitem__(
                    1, value["contrasts"][0]["block_ids"][0]
                ),
                "invalid semantic block linkage",
            ),
            (
                "same_cell",
                lambda value: value["contrasts"][0].__setitem__(
                    "cell_b_id", value["contrasts"][0]["cell_a_id"]
                ),
                "differs from frozen registry enumeration",
            ),
        )
        for name, mutate, expected in mutations:
            with self.subTest(name=name), tempfile.TemporaryDirectory() as tmp:
                tmp_path = Path(tmp)
                config_dir = tmp_path / "configs"
                runs_dir = tmp_path / "runs"
                config_dir.mkdir()
                manifest, _ = write_strict_analysis_campaign(config_dir)
                mutate(manifest)
                manifest["manifest_id"] = calculate_manifest_id(manifest)
                (config_dir / "analysis_manifest.json").write_text(
                    json.dumps(manifest, indent=2, sort_keys=True) + "\n",
                    encoding="utf-8",
                )

                result = run_campaign(config_dir, runs_dir)

                self.assertEqual(result.returncode, 1)
                verdict = read_all_jsonl(runs_dir / "campaign_log.jsonl")[-1]
                self.assertIn(
                    expected,
                    "\n".join(verdict["analysis_manifest"]["problems"]),
                )
                self.assertIn(
                    "analysis_manifest_invalid",
                    verdict["analysis_readiness"]["reasons"],
                )

    def test_campaign_provenance_records_first_run_exemption_and_unknown_mock_gate(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            config_dir = tmp_path / "configs"
            runs_dir = tmp_path / "runs"
            config_dir.mkdir()
            manifest, _ = write_strict_analysis_campaign(config_dir)
            fake_cli = make_fake_cli(tmp_path)

            result = run_campaign(config_dir, runs_dir, cli_cmd=cli_cmd_for(fake_cli))

            self.assertEqual(result.returncode, 0, result.stderr)
            manifests = list((runs_dir / "campaign_manifests").glob("*.json"))
            self.assertEqual(len(manifests), 1)
            provenance = json.loads(manifests[0].read_text(encoding="utf-8"))
            first_run_id = manifest["entries"][0]["run_id"]
            self.assertEqual(provenance["first_physical_run_id"], first_run_id)
            self.assertEqual(
                provenance["members"][0]["preceding_campaign_cooldown"]["result"],
                "first_run_exempt",
            )
            second = provenance["members"][1]["preceding_campaign_cooldown"]
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

    def test_inferred_sidecar_with_annotations_marker_is_not_applicable(self) -> None:
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

            self.assertEqual(result.returncode, 0, result.stderr)
            rows = read_jsonl(runs_dir / "campaign_log.jsonl")
            check = rows[0]["members"][0]["prompt_hash_check"]
            self.assertEqual(check["status"], "not_applicable")
            self.assertEqual(check["sidecar_path"], str(sidecar))
            self.assertEqual(check["checked_items"], 0)

    def test_inferred_sidecar_with_known_non_prompt_schema_is_not_applicable(self) -> None:
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
                config_dir, "suite.json", "suite-inferred-schema", suite_manifest=manifest
            )

            result = run_campaign(config_dir, runs_dir)

            self.assertEqual(result.returncode, 0, result.stderr)
            rows = read_jsonl(runs_dir / "campaign_log.jsonl")
            check = rows[0]["members"][0]["prompt_hash_check"]
            self.assertEqual(check["status"], "not_applicable")
            self.assertEqual(check["sidecar_path"], str(sidecar))
            self.assertEqual(check["checked_items"], 0)

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

    def test_absent_inferred_prompt_hash_sidecar_is_not_applicable(self) -> None:
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

            self.assertEqual(result.returncode, 0, result.stderr)
            rows = read_jsonl(runs_dir / "campaign_log.jsonl")
            check = rows[0]["members"][0]["prompt_hash_check"]
            self.assertEqual(check, {"status": "not_applicable", "checked_items": 0})

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

            result = run_campaign(config_dir, runs_dir)

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

    def test_sidecarless_campaign_records_prompt_hash_check_not_applicable(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            config_dir = tmp_path / "configs"
            runs_dir = tmp_path / "runs"
            config_dir.mkdir()
            write_suite_config(config_dir, "suite.json", "suite-no-sidecar")

            result = run_campaign(config_dir, runs_dir)

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertNotIn("prompt_hash", result.stderr)
            rows = read_jsonl(runs_dir / "campaign_log.jsonl")
            check = rows[0]["members"][0]["prompt_hash_check"]
            self.assertEqual(check, {"status": "not_applicable", "checked_items": 0})

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
            write_suite_config(config_dir, "suite.json", "suite-posthoc")
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
            write_suite_config(config_dir, "suite.json", "suite-posthoc-nonzero")
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
            write_config(config_dir, "partial.json", "partial-exp", repetitions=5)
            write_experiment(runs_dir, "partial-exp", 5, completed=3)
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
            write_config(config_dir, "space.json", "Foo Bar")
            write_single_bundle(runs_dir, "foo-bar")
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
            write_config(config_dir, "01-complete.json", "complete", repetitions=5)
            write_config(config_dir, "02-partial.json", "partial", repetitions=5)
            write_config(config_dir, "03-fresh.json", "fresh", repetitions=5)
            write_experiment(runs_dir, "complete", 5)
            write_experiment(runs_dir, "partial", 5, completed=2)
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


if __name__ == "__main__":
    unittest.main()
