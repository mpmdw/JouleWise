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
from joulewise.clock import Clock, FakeClock, SystemClock
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


class StartupFaultTask(SyntheticTask):
    """Exercise task startup failures at the real prepare boundary."""

    def __init__(self, clock: Clock, fault: str) -> None:
        super().__init__(clock)
        self.fault = fault

    def reset(self, seed: int) -> None:
        if self.fault == "reset":
            raise RuntimeError("reset fault")
        super().reset(seed)

    def system_prompt(self, condition: str) -> str:
        if self.fault == "system_prompt":
            raise RuntimeError("system prompt fault")
        return super().system_prompt(condition)

    def user_prompt(self) -> str:
        if self.fault == "user_prompt":
            raise RuntimeError("user prompt fault")
        return super().user_prompt()


def make_startup_fault_task(clock: Clock, fault: str) -> StartupFaultTask:
    return StartupFaultTask(clock, fault)


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
                summary = json.loads((bundle / "summary_metrics.json").read_text())
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
        unsupported = []
        for backend in RuntimeBackend:
            if backend in (RuntimeBackend.MOCK, RuntimeBackend.MLX):
                continue
            config = as_config(base, f"apple-{backend.value}")
            unsupported.append(replace(config, hardware_target=replace(
                config.hardware_target, runtime_backend=backend
            )))
        startup_faults = [
            as_config(replace(
                base, task_factory="tests.align.test_apple_campaign:make_startup_fault_task",
                task_kwargs={"fault": fault},
            ), f"apple-{fault}-fault")
            for fault in ("reset", "system_prompt", "user_prompt")
        ]
        for config in (missing, bad, mlx, *unsupported, *startup_faults):
            with self.subTest(run_id=config.run_id), tempfile.TemporaryDirectory() as directory:
                clock = FakeClock()
                bundle, summary = run_benchmark(config, Path(directory), clock)
                # D-012 maps RUNTIME_UNAVAILABLE to unsupported.
                self.assertEqual(summary.status.value, "unsupported", summary)
                self.assertEqual(summary.failure_reason, FailureReason.RUNTIME_UNAVAILABLE)
                self.assertTrue(summary.failure_message)
                self.assertIsNone(summary.gross_energy_j)
                self.assertFalse((bundle / "outputs/align_episode.json").exists())
                self.assertFalse(any(
                    event.get("phase") in ("idle_baseline", "warmup", "measured_run")
                    for event in (json.loads(line) for line in (bundle / "events.jsonl").read_text().splitlines())
                ))

    def test_system_clock_reset_fault_stops_before_idle_or_warmup(self) -> None:
        spec = replace(
            episode_spec(hidden=False),
            task_factory="tests.align.test_apple_campaign:make_startup_fault_task",
            task_kwargs={"fault": "reset"},
        )
        with tempfile.TemporaryDirectory() as directory:
            bundle, summary = run_benchmark(
                as_config(spec, "apple-system-reset-fault"), Path(directory), SystemClock()
            )
            self.assertEqual(summary.status.value, "unsupported", summary)
            self.assertEqual(summary.failure_reason, FailureReason.RUNTIME_UNAVAILABLE)
            self.assertIn("task_unavailable:RuntimeError:reset fault", summary.failure_message)
            self.assertFalse((bundle / "outputs/align_episode.json").exists())
            events = [json.loads(line) for line in (bundle / "events.jsonl").read_text().splitlines()]
            self.assertFalse(any(
                event.get("phase") in ("idle_baseline", "warmup", "measured_run")
                for event in events
            ))

    def test_zero_token_model_failure_is_failed_on_both_clocks(self) -> None:
        base = episode_spec(hidden=False)
        turns = ({**base.mock_turns[0], "prompt_tokens": "not-an-int"},)
        spec = replace(base, mock_turns=turns)
        for clock in (FakeClock(), SystemClock()):
            with self.subTest(clock=type(clock).__name__), tempfile.TemporaryDirectory() as directory:
                config = as_config(spec, "apple-zero-token-fault")
                # H4's 1 s idle covers ten 10 Hz samples and keeps this live-clock
                # error regression short; generation itself fails before sleeping.
                config = replace(config, sampling=replace(config.sampling, idle_seconds=1.0))
                bundle, summary = run_benchmark(config, Path(directory), clock)
                self.assertEqual(summary.status.value, "failed", summary)
                self.assertEqual(summary.failure_reason, FailureReason.UNKNOWN_ERROR)
                self.assertIn("no_model_call_returned_tokens", summary.failure_message)
                self.assertIn("endpoint_error:ValueError:", summary.failure_message)
                self.assertFalse((bundle / "outputs/align_episode.json").exists())

    def test_later_model_failure_keeps_partial_episode_as_flag(self) -> None:
        base = episode_spec(hidden=False)
        turns = list(base.mock_turns)
        turns[1] = {**turns[1], "prompt_tokens": "not-an-int"}
        with tempfile.TemporaryDirectory() as directory:
            bundle, summary = run_benchmark(
                as_config(replace(base, mock_turns=tuple(turns)), "apple-partial"),
                Path(directory), FakeClock(),
            )
            self.assertEqual(summary.status.value, "succeeded", summary)
            self.assertIsNotNone(summary.gross_energy_j)
            episode = read_episode_bundle(bundle)
            self.assertEqual(episode.turns[0].decode_tokens, COMPLETIONS[0])
            self.assertEqual(episode.turns[1].decode_tokens, 0)
            self.assertTrue(any(flag.startswith("endpoint_error:ValueError:") for flag in episode.flags))

    def test_flag_paths_succeed_with_measured_energy(self) -> None:
        base = episode_spec(hidden=False)
        malformed = list(base.mock_turns)
        malformed[0] = {**malformed[0], "content": "<tool_call>{broken}</tool_call>"}
        reasoning = list(base.mock_turns)
        reasoning[-1] = {**reasoning[-1], "reasoning_tokens": 99999}
        # 99,999 is a deliberately impossible usage fixture, above this
        # world's largest completion count (1,024), not an acceptance bar.
        at_budget = list(base.mock_turns)
        at_budget[-1] = {**at_budget[-1], "completion_tokens": base.max_tokens}
        cases = (
            (replace(base, mock_turns=tuple(at_budget)), "turn_token_budget_reached:5", 6),
            (replace(base, max_turns=3), "turn_budget_reached", 3),
            (replace(base, mock_turns=tuple(malformed)), "malformed_tool_call:", 1),
            (replace(base, mock_turns=tuple(reasoning)), "mock_reasoning_count_outside_completion", 6),
        )
        for index, (spec, flag, turn_count) in enumerate(cases):
            with self.subTest(flag=flag), tempfile.TemporaryDirectory() as directory:
                bundle, summary = run_benchmark(
                    as_config(spec, f"apple-flag-{index}"), Path(directory), FakeClock()
                )
                self.assertEqual(summary.status.value, "succeeded", summary)
                self.assertIsNotNone(summary.gross_energy_j)
                self.assertIsNotNone(summary.phase_energy_j)
                episode = read_episode_bundle(bundle)
                self.assertEqual(len(episode.turns), turn_count)
                self.assertTrue(any(value.startswith(flag) for value in episode.flags), episode.flags)
                summary_flag = "single_request_summary_fields_not_episode_metrics:ttft_s,decode_latency_s,energy_token_j"
                self.assertIn(summary_flag, episode.flags)
                raw = json.loads((bundle / "outputs/align_episode.json").read_text())
                self.assertIn(summary_flag, raw["flags"])

    def test_order_manifest_counterbalances_cells_and_pack_ids_do_not_collide(self) -> None:
        from scripts.run_campaign import apply_order_manifest, load_order_entries

        benign = episode_spec(hidden=False)
        sabotage = episode_spec(hidden=True)
        specs = (benign, replace(benign, seed=20), sabotage, replace(sabotage, seed=20))
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            members = generate_campaign(base_config(), specs, root / "one", model_tag="apple")
            entries, warning = load_order_entries(root / "one/members")
            self.assertIsNone(warning)
            ordered = apply_order_manifest(list(reversed(members)), entries)
            self.assertEqual(tuple(ordered), members)  # explicit order, not sorted fallback
            configs = [BenchmarkConfig.from_mapping(json.loads(path.read_text())) for path in ordered]
            self.assertEqual([
                EpisodeSpec.from_text(config.workload_profile.prompt_text).condition for config in configs
            ], ["benign", "sabotage", "sabotage", "benign"])
            for ordinal, config in enumerate(configs, 1):
                tags = config.to_dict()["run_metadata"]["tags"]
                self.assertIn(f"episode{ordinal}", tags)
                self.assertNotIn(f"rep{ordinal}", tags)
                self.assertNotIn("2m", tags)
            other = generate_campaign(base_config(), specs, root / "two", model_tag="apple")
            other_ids = {json.loads(path.read_text())["run_id"] for path in other}
            self.assertTrue({config.run_id for config in configs}.isdisjoint(other_ids))
            self.assertEqual(members, generate_campaign(base_config(), specs, root / "one", model_tag="apple"))

    def test_real_hazard_bundle_battery_assist_covers_late_tool_wait(self) -> None:
        from unittest.mock import patch
        from joulewise.hazards import battery
        from tests.hazards.test_battery import SpanRig
        import tests.test_window_lineage as lineage

        original = lineage._member_config
        def align_member(run_id, *, tagged):
            config = original(run_id, tagged=tagged)
            return replace(config, workload_profile=replace(
                config.workload_profile, name="align_episode",
                prompt_text=episode_spec(hidden=True).to_text(),
                prompt_tokens=None, output_tokens=None, prompt_token_expectation=None,
            ))

        with tempfile.TemporaryDirectory() as directory, patch.object(
            lineage, "_member_config", side_effect=align_member
        ), patch.object(lineage.window_lineage, "current_boot_session_id", return_value=lineage.STAND_IN_BOOT):
            window = lineage.build_window(Path(directory))
            bundle, summary = lineage.run_member(window, window.member_path)
            self.assertEqual(summary.status.value, "succeeded", summary)
            self.assertIsNotNone(summary.gross_energy_j)
            self.assertIsNotNone(summary.phase_energy_j)
            episode = read_episode_bundle(bundle)
            measured = BundleReader(bundle).measured_window()
            # The fixture uses FakeClock: its epoch and monotonic domains
            # are identical. These are the real bundle's sampling markers.
            span = {"monotonic_ns": [round(measured.start_s * 1e9), round(measured.end_s * 1e9)]}
            self.assertLessEqual(span["monotonic_ns"][0], episode.start_ns)
            self.assertGreaterEqual(span["monotonic_ns"][1], episode.end_ns)
            for turn in episode.turns:
                self.assertLessEqual(span["monotonic_ns"][0], turn.start_ns)
                self.assertGreaterEqual(span["monotonic_ns"][1], turn.end_ns)
                for tool in turn.tool_calls:
                    self.assertLessEqual(span["monotonic_ns"][0], tool.start_ns)
                    self.assertGreaterEqual(span["monotonic_ns"][1], tool.end_ns)
            rig = SpanRig()
            rig.setUp()
            rig.mono0 = (span["monotonic_ns"][0] // 10**9 - 2) * 10**9
            stop_s = math.ceil((span["monotonic_ns"][1] - rig.mono0) / 1e9)
            publications = rig.series(stop_s // 60 + 2)  # real 60 s gauge, with both end brackets
            clean = publications + rig.smc_lines(stop_s + 1)
            self.assertEqual(battery.span_findings(clean, span, request=span), [])
            tool = episode.turns[-2].tool_calls[0]
            late = math.ceil((tool.start_ns - rig.mono0) / 1e9)
            self.assertLess(rig.mono0 + late * 10**9, tool.end_ns)  # burst is inside the late wait
            # The ruling's 200 mA limit is crossed by the observed -865 mA
            # inference burst (665 mA beyond it); positive +865 tests charging.
            assisted = publications + rig.smc_lines(stop_s + 1, current={late: -865})
            found = battery.span_findings(assisted, span, request=span)
            self.assertEqual([item["code"] for item in found], ["battery.assist"])
            self.assertTrue(found[0]["observed"]["request_assist"])
            turn = episode.turns[-1]
            charging = math.ceil((turn.start_ns - rig.mono0) / 1e9)
            self.assertLess(rig.mono0 + charging * 10**9, turn.end_ns)
            charged = publications + rig.smc_lines(stop_s + 1, current={charging: 865})
            found = battery.span_findings(charged, span, request=span)
            self.assertIn("battery.member_span", [item["code"] for item in found])
            self.assertNotIn("battery.assist", [item["code"] for item in found])
