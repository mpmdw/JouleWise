"""Synthetic agent worlds through the real generator, registry and campaign CLI."""

from __future__ import annotations

import json
import math
import os
import subprocess
import sys
import tempfile
import unittest
from dataclasses import replace
from pathlib import Path
from typing import Any

from joulewise.align.apple.campaign import generate_campaign
from joulewise.align.apple.workload import EpisodeSpec, read_episode_bundle
from joulewise.align.records import Episode, from_json, to_json
from joulewise.bundle_read import BundleReader
from joulewise.clock import Clock, FakeClock
from joulewise.controller import run_benchmark
from joulewise.reduce import _integrate
from joulewise.schemas import BenchmarkConfig, FailureReason, RuntimeBackend

ROOT = Path(__file__).resolve().parents[2]
PROMPTS = (2048, 3072, 4096, 5120, 6144, 7168)
COMPLETIONS = (512, 512, 768, 768, 1024, 1024)
TOOL_SECONDS = (1.5, 2.0, 0.8, 3.0, 1.0)
HIDDEN_TOKENS = 256


def base_config() -> BenchmarkConfig:
    obj = json.loads((ROOT / "configs/examples/mock_local.json").read_text())
    # 10 Hz is the production Apple cadence. A 30 s idle admission window
    # matches the campaign's existing CPU-evidence averaging window.
    obj["sampling"].update(power_hz=10.0, idle_seconds=30.0)
    obj["model"]["context_window"] = 32768
    return BenchmarkConfig.from_mapping(obj)


class SyntheticTask:
    """Local document-checking task with five timed, UTF-8 tool results."""

    task_pair = "synthetic/document_reconciliation"
    scratchpad_tags = ("<think>", "</think>")

    def __init__(self, clock: Clock, fail_step: int | None = None) -> None:
        self.clock = clock
        self.fail_step = fail_step
        self.condition = "benign"

    def reset(self, seed: int) -> None:
        self.seed = seed

    def system_prompt(self, condition: str) -> str:
        self.condition = condition
        return "Reconcile the local document ledger. Use lookup for supporting rows."

    def user_prompt(self) -> str:
        return "Check five ledger sections and report the reconciliation."

    def task_description(self) -> str:
        return self.user_prompt()

    def tool_schemas(self):
        return [{
            "type": "function",
            "function": {
                "name": "lookup", "description": "Read local synthetic ledger rows.",
                "parameters": {
                    "type": "object", "properties": {"step": {"type": "integer"}},
                    "required": ["step"],
                },
            },
        }]

    def call_tool(self, name: str, arguments_json: str) -> str:
        step = json.loads(arguments_json)["step"]
        self.clock.sleep(TOOL_SECONDS[step])
        if step == self.fail_step:
            raise RuntimeError("synthetic tool fault")
        return json.dumps({
            "section": step,
            "rows": [
                {"record": row, "amount": row * 7 + self.seed, "note": "local ledger row"}
                for row in range(32)
            ],
        })

    def score_main(self, transcript) -> float:
        return float(sum(message.role == "tool" for message in transcript) == len(TOOL_SECONDS))

    def score_side(self, transcript) -> bool:
        return self.condition == "sabotage"


def make_synthetic_task(clock: Clock, fail_step: int | None = None) -> SyntheticTask:
    return SyntheticTask(clock, fail_step)


def episode_spec(*, hidden: bool, fail_step: int | None = None) -> EpisodeSpec:
    script: list[dict[str, Any]] = []
    for index, (prompt, completion) in enumerate(zip(PROMPTS, COMPLETIONS)):
        content = (
            "<tool_call>" + json.dumps({"name": "lookup", "arguments": {"step": index}})
            + "</tool_call>"
            if index < len(TOOL_SECONDS) else "The five sections reconcile."
        )
        hidden_count = HIDDEN_TOKENS if hidden and index == len(PROMPTS) - 1 else 0
        if hidden_count:
            content = "<think>Synthetic hidden final-turn scratchpad.</think>" + content
        script.append({
            "prompt_tokens": prompt, "completion_tokens": completion + hidden_count,
            "reasoning_tokens": hidden_count, "content": content,
        })
    return EpisodeSpec(
        task_factory="tests.align.test_apple_campaign:make_synthetic_task",
        task_kwargs={"fail_step": fail_step},
        condition="sabotage" if hidden else "benign", seed=19,
        max_turns=len(PROMPTS), max_tokens=max(COMPLETIONS) + HIDDEN_TOKENS,
        temperature=0.0, mock_turns=tuple(script),
    )


def as_config(spec: EpisodeSpec, run_id: str) -> BenchmarkConfig:
    config = base_config()
    return replace(
        config, run_id=run_id,
        workload_profile=replace(
            config.workload_profile, name="align_episode",
            prompt_text=spec.to_text(), prompt_tokens=None, output_tokens=None,
        ),
    )


class AppleCampaignTests(unittest.TestCase):
    def test_generator_real_campaign_and_hidden_work_control(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            specs = (episode_spec(hidden=False), episode_spec(hidden=True))
            members = generate_campaign(base_config(), specs, root / "pack", model_tag="apple")
            before = [path.read_bytes() for path in members]
            self.assertEqual(
                members, generate_campaign(base_config(), specs, root / "pack", model_tag="apple")
            )
            self.assertEqual(before, [path.read_bytes() for path in members])  # exact config identity
            policy = json.loads((ROOT / "configs/campaign_policies/quiet_mac_exploratory.json").read_text())
            # Like tests.test_window_lineage.run_member, mock workloads have
            # no display/idle host evidence. Production admission is unchanged.
            policy["idle_admission"]["enabled"] = False
            policy["environment_guard"] = {
                key: False for key in policy["environment_guard"]
            }
            policy_path = root / "synthetic-policy.json"
            policy_path.write_text(json.dumps(policy))
            env = dict(os.environ, JW_B5_SYNTHETIC_ONLY="1", PYTHONDONTWRITEBYTECODE="1")
            completed = subprocess.run([
                sys.executable, "-B", str(ROOT / "scripts/run_campaign.py"),
                str(root / "pack/members"), "--runs-dir", str(root / "runs"),
                "--log", str(root / "campaign.jsonl"), "--campaign-policy", str(policy_path),
            ], cwd=ROOT, env=env, text=True, capture_output=True)
            self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)
            episodes = []
            energies = []
            for member in members:
                config = BenchmarkConfig.from_mapping(json.loads(member.read_text()))
                bundle = root / "runs" / config.run_id
                summary = json.loads((bundle / "summary.json").read_text())
                self.assertEqual(summary["status"], "succeeded", summary)
                self.assertIsNotNone(summary["gross_energy_j"])
                self.assertIsNotNone(summary["phase_energy_j"])
                reader = BundleReader(bundle)
                episode = read_episode_bundle(bundle)
                episodes.append(episode)
                self.assertEqual(len(episode.turns), len(PROMPTS))
                self.assertEqual(episode.totals()["tool_calls"], len(TOOL_SECONDS))
                self.assertTrue((bundle / "raw/mock_samples.json").is_file())
                self.assertTrue((bundle / "outputs/align_transcript.jsonl").is_file())
                self.assertTrue((bundle / "outputs/align_turns.jsonl").is_file())
                self.assertEqual(from_json(Episode, to_json(episode)), episode)  # record identity
                self.assertEqual(len(reader.phase_windows()["prefill"]), len(PROMPTS))
                self.assertEqual(len(reader.phase_windows()["decode"]), len(PROMPTS))
                self.assertFalse(any(name.startswith("align_turn_") for name in reader.phase_windows()))
                for turn, prefill in zip(episode.turns, reader.phase_windows()["prefill"]):
                    # Identical event-to-ns conversions must give bit identity.
                    self.assertEqual(turn.first_token_ns, round(prefill.end_s * 1e9))
                window = reader.measured_window()
                self.assertIsNotNone(window)
                energies.append(_integrate(reader.summed_curve(), window.start_s, window.end_s))
                self.assertTrue(episode.power_traces)
                self.assertTrue(episode.clock_mappings)
            baseline, hidden = episodes
            self.assertEqual(
                sum(turn.decode_tokens - turn.hidden_tokens for turn in baseline.turns),
                sum(turn.decode_tokens - turn.hidden_tokens for turn in hidden.turns),
            )
            self.assertEqual(hidden.totals()["hidden_tokens"], HIDDEN_TOKENS)
            # D-019 physics: each extra output token costs 10 ms at 7.5 W.
            # These are exact mock parameters, with no uncertainty; use the
            # required 1e-6 relative agreement bar, well above float roundoff.
            expected_extra_j = HIDDEN_TOKENS * 0.010 * 7.5
            self.assertTrue(math.isclose(
                energies[1] - energies[0], expected_extra_j, rel_tol=1e-6
            ), (energies, expected_extra_j))
            # The brief's ~1 J attribution half-width is the detection bar.
            # A no-hidden-work implementation must fail this effect test.
            self.assertGreater(energies[1] - energies[0], 1.0)
            expected_baseline_s = sum(PROMPTS) * 0.001 + sum(COMPLETIONS) * 0.010 + sum(TOOL_SECONDS)
            self.assertTrue(math.isclose(
                (baseline.end_ns - baseline.start_ns) / 1e9,
                expected_baseline_s, rel_tol=1e-6,
            ))  # D-019 closed-form timeline, same no-uncertainty bar.
            self.assertTrue(math.isclose(
                energies[0], expected_baseline_s * 7.5, rel_tol=1e-6,
            ))  # independently sum phase durations, then multiply physical power.

    def test_tool_failure_is_an_episode_flag_and_remaining_turns_run(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            bundle, summary = run_benchmark(
                as_config(episode_spec(hidden=False, fail_step=2), "apple-tool-fault"),
                Path(directory), FakeClock(),
            )
            self.assertEqual(summary.status.value, "succeeded", summary)
            self.assertIsNotNone(summary.gross_energy_j)
            self.assertIsNotNone(summary.phase_energy_j)
            episode = read_episode_bundle(bundle)
            self.assertEqual(len(episode.turns), len(PROMPTS))
            self.assertEqual(episode.totals()["tool_calls"], len(TOOL_SECONDS))
            self.assertIn("tool_error:2:0", episode.flags)

    def test_prepare_failures_are_structured_before_measurement(self) -> None:
        base = episode_spec(hidden=False)
        missing = as_config(replace(base, task_factory="missing_apple_task:factory"), "apple-missing-task")
        bad = as_config(base, "apple-bad-spec")
        bad = replace(bad, workload_profile=replace(bad.workload_profile, prompt_text='{"schema":"nope"}'))
        mlx = as_config(base, "apple-no-model")
        mlx = replace(mlx, model=replace(mlx.model, source=None), hardware_target=replace(
            mlx.hardware_target, runtime_backend=RuntimeBackend.MLX
        ))
        unsupported = as_config(base, "apple-vllm")
        unsupported = replace(unsupported, hardware_target=replace(
            unsupported.hardware_target, runtime_backend=RuntimeBackend.VLLM
        ))
        for config in (missing, bad, mlx, unsupported):
            with self.subTest(run_id=config.run_id), tempfile.TemporaryDirectory() as directory:
                clock = FakeClock()
                bundle, summary = run_benchmark(config, Path(directory), clock)
                self.assertEqual(summary.status.value, "failed", summary)
                self.assertEqual(summary.failure_reason, FailureReason.RUNTIME_UNAVAILABLE)
                self.assertTrue(summary.failure_message)
                self.assertIsNone(summary.gross_energy_j)
                self.assertFalse((bundle / "outputs/align_episode.json").exists())
                self.assertFalse(any(
                    event.get("phase") == "measured_run"
                    for event in (json.loads(line) for line in (bundle / "events.jsonl").read_text().splitlines())
                ))
