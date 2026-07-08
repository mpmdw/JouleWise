from __future__ import annotations

import json
import os
import shlex
import subprocess
import sys
import tempfile
import textwrap
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "run_campaign.py"
BASE_CONFIG = ROOT / "configs" / "examples" / "mock_local.json"
COMMAND_TIMEOUT_S = 60


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


def write_single_bundle(
    runs_dir: Path,
    run_id: str,
    status: str = "succeeded",
    *,
    idle_window_suspect: bool | None = None,
) -> None:
    _write_bundle(runs_dir, run_id, status, idle_window_suspect=idle_window_suspect)


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
) -> None:
    from joulewise import reduce as reduce_module
    from joulewise.bundle import RunBundleWriter
    from joulewise.clock import FakeClock
    from joulewise.interfaces import PowerSample, RuntimeEvent
    from joulewise.provenance import output_policy, prompt_provenance
    from joulewise.schemas import BenchmarkConfig, FailureReason, RunStatus, SummaryMetrics

    config_data = json.loads(BASE_CONFIG.read_text(encoding="utf-8"))
    config_data["run_id"] = run_id
    config_data["workload_profile"]["repetitions"] = 1
    config = BenchmarkConfig.from_mapping(config_data)
    writer = RunBundleWriter.create(runs_dir, config, FakeClock(start=3.0))

    def event(timestamp_s: float, event_type: str, phase: str, message: str = "") -> None:
        writer.append_event(
            RuntimeEvent(
                timestamp_s=timestamp_s,
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
                PowerSample(timestamp_s=0.0, power_w=7.5, source="mock", rail="mock"),
                PowerSample(timestamp_s=0.5, power_w=7.5, source="mock", rail="mock"),
                PowerSample(timestamp_s=1.0, power_w=7.5, source="mock", rail="mock"),
            ]
        )
        idle = {
            "power_w_mean": 5.0,
            "power_w_stddev": 0.0,
            "duration_s": 1.0,
            "sample_count": 2,
            "telemetry_backend": "mock",
        }
        if idle_window_suspect is not None:
            idle["idle_window_suspect"] = idle_window_suspect
        writer.write_metadata(
            {
                "device": {"telemetry": "mock", "rail_manifest": ["mock"]},
                "adapters": {"telemetry": {"name": "mock"}},
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
                config_data = json.loads(BASE_CONFIG.read_text(encoding="utf-8"))
                config_data["run_id"] = bundle_run_id
                config_data["workload_profile"]["repetitions"] = 1
                config = BenchmarkConfig.from_mapping(config_data)
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
                            PowerSample(timestamp_s=0.0, power_w=7.5, source="mock", rail="mock"),
                            PowerSample(timestamp_s=0.5, power_w=7.5, source="mock", rail="mock"),
                            PowerSample(timestamp_s=1.0, power_w=7.5, source="mock", rail="mock"),
                        ]
                    )
                    writer.write_metadata(
                        {{
                            "device": {{"telemetry": "mock", "rail_manifest": ["mock"]}},
                            "adapters": {{"telemetry": {{"name": "mock"}}}},
                            "idle_baseline": {{
                                "power_w_mean": 5.0,
                                "power_w_stddev": 0.0,
                                "duration_s": 1.0,
                                "sample_count": 2,
                                "telemetry_backend": "mock",
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


class RunCampaignTests(unittest.TestCase):
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
            self.assertIn("VERDICT:", result.stdout)
            self.assertIn("verdict: partial", result.stdout)
            rows = read_jsonl(runs_dir / "campaign_log.jsonl")
            self.assertEqual([row["status"] for row in rows], ["skipped", "waived"])
            all_rows = read_all_jsonl(runs_dir / "campaign_log.jsonl")
            verdict = all_rows[-1]
            self.assertEqual(verdict["record_type"], "campaign_verdict")
            self.assertEqual(verdict["verdict"], "partial")
            self.assertEqual(verdict["usable"], ["good"])
            self.assertEqual(verdict["waived"], ["idle"])
            self.assertIn("all-waived is invalid", verdict["taxonomy"]["partial"])

    def test_waiver_target_namespace_is_exact_and_typed(self) -> None:
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

            self.assertEqual(result.returncode, 1)
            self.assertIn("not skippable", result.stderr)
            rows = read_jsonl(runs_dir / "campaign_log.jsonl")
            self.assertEqual(rows[0]["status"], "failed")
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
            self.assertEqual(rows[0]["members"][0]["quality_flags"], ["idle_window_suspect"])

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

    def test_idle_suspect_existing_member_requires_waiver(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            config_dir = tmp_path / "configs"
            runs_dir = tmp_path / "runs"
            config_dir.mkdir()
            write_config(config_dir, "idle.json", "idle")
            write_single_bundle(runs_dir, "idle", idle_window_suspect=True)
            fake_cli = make_fake_cli(tmp_path)

            result = run_campaign(config_dir, runs_dir, cli_cmd=cli_cmd_for(fake_cli))

            self.assertEqual(result.returncode, 1)
            self.assertIn("idle_window_suspect", result.stderr)
            rows = read_jsonl(runs_dir / "campaign_log.jsonl")
            self.assertEqual(rows[0]["status"], "failed")
            self.assertEqual(rows[0]["members"][0]["quality_flags"], ["idle_window_suspect"])

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
                            "reason": "all waived is not publishable evidence",
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
            self.assertEqual(verdict["verdict"], "invalid")
            self.assertEqual(verdict["waived"], ["idle"])
            self.assertIn("all-waived is invalid", verdict["taxonomy"]["partial"])

    def test_verdict_block_content_for_publishable_campaign(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            config_dir = tmp_path / "configs"
            runs_dir = tmp_path / "runs"
            config_dir.mkdir()
            write_config(config_dir, "one.json", "one")
            fake_cli = make_fake_cli(tmp_path)

            result = run_campaign(config_dir, runs_dir, cli_cmd=cli_cmd_for(fake_cli))

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("VERDICT:", result.stdout)
            self.assertIn("verdict: publishable", result.stdout)
            all_rows = read_all_jsonl(runs_dir / "campaign_log.jsonl")
            self.assertEqual(all_rows[-1]["record_type"], "campaign_verdict")
            self.assertEqual(all_rows[-1]["verdict"], "publishable")
            self.assertEqual(all_rows[-1]["usable"], ["one"])
            self.assertEqual(all_rows[-1]["failed"], [])

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
