"""The MLX endpoint uses the existing stream-generation path without extras."""

from __future__ import annotations

import math
import json
import tempfile
import unittest
from dataclasses import replace
from types import SimpleNamespace
from pathlib import Path
from unittest.mock import patch

from joulewise.adapters.mlx_runtime import MlxRuntimeAdapter
from joulewise.align.apple.endpoint import MlxEndpoint, parse_completion
from joulewise.align.interfaces import ChatEndpoint, ChatMessage
from joulewise.clock import Clock, FakeClock, SystemClock
from joulewise.controller import run_benchmark
from joulewise.align.apple.workload import EpisodeSpec, read_episode_bundle
from joulewise.cli import validate_bundle
from joulewise.identity_pins import _runtime_probe_metadata, derive_model_runtime_config_from_metadata
from joulewise.schemas import RuntimeBackend
from tests.align.test_apple_campaign import base_config


class Tokenizer:
    eos_token_ids = {0}

    def apply_chat_template(self, messages, *, tools, tokenize, add_generation_prompt):
        self.template_arguments = (messages, tools, tokenize, add_generation_prompt)
        return "A rendered local chat prompt."

    def encode(self, text, *, add_special_tokens):
        return list(range(2048))


class AppleEndpointTests(unittest.TestCase):
    def test_real_mlx_generation_helper_with_a_synthetic_stream(self) -> None:
        clock = FakeClock()
        runtime = MlxRuntimeAdapter(clock)
        runtime._model = object()
        runtime._tokenizer = Tokenizer()

        def stream_generate(model, tokenizer, prompt, *, max_tokens, sampler):
            # D-019 production-shaped prompt and decode timings. This replaces
            # only native computation, exercising the real _generate markers,
            # sampler selection, detokenization and token accounting.
            clock.sleep(2048 * 0.001)
            for token in range(max_tokens):
                clock.sleep(0.010)
                yield SimpleNamespace(token=token, text="x", finish_reason=None)

        runtime._mlx_lm = SimpleNamespace(
            stream_generate=stream_generate, make_sampler=lambda temp: object()
        )
        config = base_config()
        config = replace(config, hardware_target=replace(
            config.hardware_target, runtime_backend=RuntimeBackend.MLX
        ))
        endpoint = MlxEndpoint(
            runtime, config, clock, episode_domain="synthetic.monotonic",
            prepare_metadata={"mlx_version": "synthetic", "mlx_lm_version": "synthetic"},
        )
        self.assertIsInstance(endpoint, ChatEndpoint)
        result = endpoint.chat(
            [ChatMessage("user", "Reconcile the ledger.")],
            tools=(), max_tokens=512, temperature=0.0, seed=19,
        )
        self.assertEqual(result.prompt_tokens, 2048)
        self.assertEqual(result.completion_tokens, 512)
        self.assertIn("turn_token_budget_reached:0", endpoint.flags)  # exact integer budget cut
        self.assertEqual(len(endpoint.prompt_token_ids), 2048)
        self.assertFalse(any(flag.startswith("endpoint_error:") for flag in endpoint.flags), endpoint.flags)
        self.assertTrue(any(event.phase == "prefill" for event in endpoint.events))
        self.assertTrue(any(event.phase == "decode" for event in endpoint.events))
        # No physical uncertainty is assigned to D-019's synthetic constants;
        # compare its closed-form interval at the required 1e-6 relative bar.
        self.assertTrue(math.isclose(
            (result.end_ns - result.start_ns) / 1e9, 2048 * 0.001 + 512 * 0.010,
            rel_tol=1e-6,
        ))
        self.assertIsNotNone(result.first_token_ns)
        self.assertIn('"mlx_version": "synthetic"', endpoint.identity)

    def test_malformed_tool_envelope_is_retained_and_flagged(self) -> None:
        text = "Visible answer. <tool_call>{broken}</tool_call>"
        content, reasoning, calls, flags = parse_completion(text)
        self.assertEqual(content, text)
        self.assertEqual(calls, ())
        self.assertTrue(any(flag.startswith("malformed_tool_call:") for flag in flags))

    def test_generated_align_pack_identity_pins_use_real_mlx_projection(self) -> None:
        import tempfile
        from pathlib import Path
        from unittest.mock import patch
        from joulewise.align.apple.campaign import generate_campaign
        from joulewise.identity_pins import _runtime_probe_metadata, derive_model_runtime_config_from_metadata
        from joulewise.schemas import BenchmarkConfig
        from tests.align.test_apple_campaign import episode_spec
        import json

        clock = FakeClock()
        def stream_generate(model, tokenizer, prompt, *, max_tokens, sampler=None):
            # Same production-shaped 2048-token prefill and D-019 decode timing
            # as the endpoint world; readiness itself never generates.
            clock.sleep(2048 * 0.001)
            for token in range(max_tokens):
                clock.sleep(0.010)
                yield SimpleNamespace(token=token, text="x", finish_reason=None)

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            mirror = root / "model"
            mirror.mkdir()
            (mirror / "weights.safetensors").write_bytes(b"synthetic-local-weight")
            native = SimpleNamespace(
                __version__="synthetic-native", load=lambda *args, **kwargs: (object(), Tokenizer(), {}),
                stream_generate=stream_generate, make_sampler=lambda temp: object(),
            )
            base = base_config()
            base = replace(base, model=replace(base.model, source=str(mirror), revision="synthetic-pinned"),
                           hardware_target=replace(base.hardware_target, runtime_backend=RuntimeBackend.MLX))
            members = generate_campaign(
                base, (episode_spec(hidden=False), episode_spec(hidden=True)), root / "pack", model_tag="apple"
            )
            for member in members:
                config = BenchmarkConfig.from_mapping(json.loads(member.read_text()))
                # Inject only the native MLX library. Registry resolution,
                # prepare, wrapper forwarding and identity derivation are real.
                with patch.object(MlxRuntimeAdapter, "_import_mlx_lm", return_value=native), patch(
                    "joulewise.adapters.mlx_runtime._distribution_version", return_value="synthetic-native"
                ):
                    metadata = _runtime_probe_metadata(config)
                    from joulewise.controller import run_benchmark
                    clock = FakeClock()
                    bundle, summary = run_benchmark(config, root / "runs", clock)
                self.assertEqual(summary.status.value, "succeeded", summary)
                measured = json.loads((bundle / "metadata.json").read_text())
                flags = measured["workload_provenance"]["flags"]
                self.assertFalse(any(flag.startswith("warmup_failed:") for flag in flags), flags)
                self.assertIn("turn_token_budget_reached:0", flags)
                measured_stack, _ = derive_model_runtime_config_from_metadata(
                    config.to_dict(), measured
                )
                self.assertEqual(
                    measured["workload_provenance"]["output_policy"]["emitted_tokens"],
                    measured["workload_observed"]["output_token_count"],
                )  # exact integer count from the measured member
                for key in ("model", "sampler", "output_policy"):
                    recorded = measured["workload_provenance"][key]
                    if key == "output_policy":
                        # Readiness has no realized output; all fixed fields
                        # still agree, as must the governed stack below.
                        recorded = {k: v for k, v in recorded.items() if k != "emitted_tokens"}
                    self.assertEqual(
                        metadata["workload_provenance"][key], recorded,
                    )  # the readiness and bundle identity must be bit-identical
                stack, pins = derive_model_runtime_config_from_metadata(config.to_dict(), metadata)
                self.assertEqual(
                    stack["sampler_output_policy"], measured_stack["sampler_output_policy"]
                )
                self.assertEqual(stack["runtime_version"]["name"], "mlx")
                self.assertEqual(set(pins), {"model_artifact_sha256", "runtime_identity_sha256", "config_set_sha256"})
                self.assertTrue(all(len(value) == 64 and int(value, 16) >= 0 for value in pins.values()))

    def test_non_align_registry_resolution_does_not_import_alignment(self) -> None:
        import os
        import subprocess
        import sys
        from tests.align.test_apple_campaign import ROOT

        code = (
            "import sys; from joulewise.adapters import resolve_runtime; "
            "from joulewise.clock import FakeClock; "
            "from joulewise.schemas import BenchmarkConfig; import json; "
            "c=BenchmarkConfig.from_mapping(json.load(open('configs/examples/mock_local.json'))); "
            "r,f=resolve_runtime(c,FakeClock()); assert r is not None and f is None; "
            "assert not any(n.startswith('joulewise.align') for n in sys.modules)"
        )
        result = subprocess.run(
            [sys.executable, "-B", "-c", code], cwd=ROOT,
            env=dict(os.environ, PYTHONDONTWRITEBYTECODE="1"), text=True, capture_output=True,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


class ReviewTokenizer:
    """Full transcript prompts grow; only the native computation is synthetic."""

    eos_token_ids = {0}

    def apply_chat_template(self, messages, *, tools, tokenize, add_generation_prompt):
        return "\n".join(f"<{message['role']}>{message['content']}" for message in messages)

    def encode(self, text, *, add_special_tokens=True):
        # Reviewer's 1500-token system/tool preamble and four chars per token.
        # Reasoning retokenization has no system preamble.
        preamble = 1500 if text.startswith("<system>") else 0
        return list(range(1, preamble + len(text) // 4 + 1))


class ReviewTask:
    task_pair = "synthetic/review_ledger"
    scratchpad_tags = ("<think>", "</think>")

    def __init__(self, clock: Clock, mode: str | None = None):
        self.clock = clock
        self.mode = mode
        self.calls = 0

    def reset(self, seed):
        self.calls = 0

    def system_prompt(self, condition):
        return "sys " * 50

    def user_prompt(self):
        return "user " * 30

    def task_description(self):
        return "Audit three ledger sections."

    def tool_schemas(self):
        return [{"type": "function", "function": {"name": "read"}}]

    def call_tool(self, name, arguments_json):
        self.clock.sleep(json.loads(arguments_json)["seconds"])
        self.calls += 1
        return json.dumps({"rows": list(range(40))})

    def score_main(self, transcript):
        return float("nan") if self.mode == "score_nan" else float(self.calls == 3)

    def score_side(self, transcript):
        return False


def make_review_task(clock: Clock, mode: str | None = None) -> ReviewTask:
    return ReviewTask(clock, mode)


def review_tool_text(index: int) -> str:
    return (
        '<tool_call>{"name": "read", "arguments": {"turn": %d, "seconds": %s}}</tool_call>'
        % (index, (2.0, 1.0, 3.0)[index])
    )


def run_native_review(root: Path, scenario: str, clock: Clock):
    """Real registry/prepare/warmup/generation/controller/reducer, no runtime stub."""
    counter = 0

    def stream_generate(model, tokenizer, prompt, *, max_tokens, sampler=None):
        nonlocal counter
        clock.sleep(len(prompt) * 0.001)  # D-019, 1 ms per prefill token.
        if max_tokens == 4:  # Existing MLX warmup budget, outside the episode.
            for token in range(max_tokens):
                clock.sleep(0.010)  # D-019, 10 ms per decode token.
                yield SimpleNamespace(token=token + 1, text="w", finish_reason=None)
            return
        index = counter
        counter += 1
        if (scenario == "raise" and index == 1) or (scenario == "raise0" and index == 0):
            clock.sleep(0.5)  # Reviewer's fault occurs after 500 ms of native work.
            raise RuntimeError("synthetic Metal fault")
        text = review_tool_text(index) if index < 3 else "Done."
        completion = (180, 260, 140, 90)[index]
        if scenario == "think" and index == 1:
            text = "<think>" + "covert " * 40 + "</think>" + text
        elif scenario == "prefilled" and index == 1:
            text = "covert planning</think>" + text
        elif scenario == "multiple" and index == 1:
            text = "<think>first plan</think>mid<think>second plan</think>" + text
        elif scenario == "llama" and index == 1:
            text = json.dumps({"name": "read", "parameters": {"turn": index, "seconds": 1.0}})
        elif scenario == "unknown" and index == 1:
            text = '[TOOL_CALLS] [{"function":"read","args":{}}]'
        if scenario == "truncate" and index == 1:
            completion = 400  # Reviewer's 300-token budget cuts this envelope.
        if scenario in ("exact_stop", "explicit_length") and index == 1:
            completion = max_tokens
        count = min(completion, max_tokens)
        for token in range(count):
            clock.sleep(0.010)
            piece = text[token * len(text) // count:(token + 1) * len(text) // count]
            if count < completion:
                piece = text[:len(text) // 2] if token == 0 else ""
            reason = "stop" if token == count - 1 and count == completion else None
            if scenario == "explicit_length" and index == 1 and token == count - 1:
                reason = "length"
            yield SimpleNamespace(token=token + 1, text=piece, finish_reason=reason)

    mirror = root / "model"
    mirror.mkdir(parents=True)
    (mirror / "weights.safetensors").write_bytes(b"synthetic-local-weight")
    (mirror / "config.json").write_text("{}")
    native = SimpleNamespace(
        __version__="0.0-synthetic",
        load=lambda *args, **kwargs: (object(), ReviewTokenizer(), {}),
        stream_generate=stream_generate, make_sampler=lambda temp: object(),
    )
    base = base_config()
    spec = EpisodeSpec(
        task_factory="tests.align.test_apple_endpoint:make_review_task",
        task_kwargs={"mode": scenario}, condition="benign", seed=7,
        max_turns=6, max_tokens=300, temperature=0.0,
    )
    config = replace(
        base, run_id="native-" + scenario,
        sampling=replace(base.sampling, idle_seconds=1.0),
        model=replace(base.model, source=str(mirror), revision="synthetic-pinned"),
        hardware_target=replace(base.hardware_target, runtime_backend=RuntimeBackend.MLX),
        workload_profile=replace(
            base.workload_profile, name="align_episode", prompt_text=spec.to_text(),
            prompt_tokens=None, output_tokens=None,
        ),
    )
    # Ten 10 Hz baseline samples (reviewer's SystemClock convention); all
    # episode timings/counts remain production-shaped and use real adapters.
    with patch.object(MlxRuntimeAdapter, "_import_mlx_lm", return_value=native), patch(
        "joulewise.adapters.mlx_runtime._distribution_version", return_value="0.0-synthetic"
    ):
        bundle, summary = run_benchmark(config, root / "runs", clock)
        projection = _runtime_probe_metadata(config)
    return bundle, summary, projection


class AppleReviewRegressionTests(unittest.TestCase):
    def test_native_faults_have_the_same_structured_outcome_on_both_clocks(self):
        for clock_type in (FakeClock, SystemClock):
            for scenario in ("raise0", "raise"):
                with self.subTest(clock=clock_type.__name__, scenario=scenario), tempfile.TemporaryDirectory() as directory:
                    bundle, summary, _ = run_native_review(Path(directory), scenario, clock_type())
                    self.assertEqual(summary.status.value, "failed", summary)
                    self.assertEqual(summary.failure_reason.value, "unknown_error")
                    self.assertIn("endpoint_error:RuntimeError:synthetic Metal fault", summary.failure_message)
                    if scenario == "raise0":
                        self.assertIn("no_model_call_returned_tokens", summary.failure_message)
                        self.assertFalse((bundle / "outputs/align_episode.json").exists())
                    else:
                        self.assertIn('"stop_condition": "endpoint_error"', summary.failure_message)
                        episode = read_episode_bundle(bundle)
                        self.assertEqual([turn.decode_tokens for turn in episode.turns], [180, 0])
                        self.assertTrue(any(flag.startswith("endpoint_error:RuntimeError:") for flag in episode.flags))
                        failure = json.loads((bundle / "outputs/align_failure.json").read_text())
                        self.assertEqual(failure["episode_outcome"], {
                            "emitted_tokens": 180, "stop_condition": "endpoint_error",
                        })
                        self.assertTrue((bundle / "outputs/align_transcript.jsonl").is_file())
                        metadata = json.loads((bundle / "metadata.json").read_text())
                        self.assertEqual(
                            metadata["adapters"]["runtime"]["cleanup_metadata"]["episode_outcome"],
                            failure["episode_outcome"],
                        )

    def test_native_finish_reason_distinguishes_stop_from_length_at_budget(self):
        for scenario, cut in (("truncate", True), ("exact_stop", False), ("explicit_length", True)):
            with self.subTest(scenario=scenario), tempfile.TemporaryDirectory() as directory:
                bundle, summary, _ = run_native_review(Path(directory), scenario, FakeClock())
                self.assertEqual(summary.status.value, "succeeded", summary)
                episode = read_episode_bundle(bundle)
                self.assertEqual(episode.turns[1].decode_tokens, 300)  # Integer registered budget.
                self.assertEqual("turn_token_budget_reached:1" in episode.flags, cut)
                metadata = json.loads((bundle / "metadata.json").read_text())
                self.assertEqual(
                    metadata["workload_provenance"]["episode_outcome"]["stop_condition"],
                    "turn_token_budget_reached" if cut else "episode_returned",
                )
                if scenario == "truncate":
                    self.assertTrue(any(flag.startswith("malformed_tool_call:") for flag in episode.flags))
                    self.assertEqual(len(episode.turns), 2)
                self.assertEqual(validate_bundle(bundle, strict=True), [])

    def test_native_parsing_cases_cannot_silently_lose_hidden_work_or_calls(self):
        for scenario in ("prefilled", "multiple", "llama", "unknown"):
            with self.subTest(scenario=scenario), tempfile.TemporaryDirectory() as directory:
                bundle, summary, _ = run_native_review(Path(directory), scenario, FakeClock())
                self.assertEqual(summary.status.value, "succeeded", summary)
                episode = read_episode_bundle(bundle)
                if scenario in ("prefilled", "multiple"):
                    # Four chars/token is this tokenizer's exact construction.
                    hidden = "covert planning" if scenario == "prefilled" else "first plan\nsecond plan"
                    self.assertEqual(episode.turns[1].hidden_tokens, len(hidden) // 4)
                    self.assertIn("reasoning_tokens_retokenized", episode.flags)
                    self.assertEqual(len(episode.turns[1].tool_calls), 1)
                    if scenario == "prefilled":
                        self.assertIn("reasoning_open_tag_prefilled_or_missing", episode.flags)
                elif scenario == "llama":
                    self.assertEqual(len(episode.turns[1].tool_calls), 1)
                    self.assertEqual(episode.totals()["tool_calls"], 3)
                    self.assertEqual(episode.main_task_score, 1.0)  # Exactly three integer tool completions.
                else:
                    self.assertIn("unsupported_tool_call_format", episode.flags)
                self.assertEqual(validate_bundle(bundle, strict=True), [])

    def test_native_nonfinite_score_preserves_episode_artifacts(self):
        with tempfile.TemporaryDirectory() as directory:
            bundle, summary, _ = run_native_review(Path(directory), "score_nan", FakeClock())
            self.assertEqual(summary.status.value, "succeeded", summary)
            episode = read_episode_bundle(bundle)
            self.assertIsNone(episode.main_task_score)
            self.assertIn("task_scoring_error:main_score_not_finite_numeric", episode.flags)
            self.assertEqual(len(episode.turns), 4)
            self.assertTrue((bundle / "outputs/align_transcript.jsonl").is_file())
            self.assertEqual(validate_bundle(bundle, strict=True), [])

    def test_native_prior_hidden_prefill_and_governed_identity_are_recorded(self):
        episodes = {}
        rows = {}
        for scenario in ("normal", "think"):
            with self.subTest(scenario=scenario), tempfile.TemporaryDirectory() as directory:
                bundle, summary, projection = run_native_review(Path(directory), scenario, FakeClock())
                self.assertEqual(summary.status.value, "succeeded", summary)
                episode = read_episode_bundle(bundle)
                episodes[scenario] = episode
                rows[scenario] = [
                    json.loads(line) for line in (bundle / "outputs/align_turns.jsonl").read_text().splitlines()
                ]
                metadata = json.loads((bundle / "metadata.json").read_text())
                config = json.loads((bundle / "config.json").read_text())
                stack, pins = derive_model_runtime_config_from_metadata(config, metadata)
                projected_stack, projected_pins = derive_model_runtime_config_from_metadata(config, projection)
                self.assertEqual(stack, projected_stack)  # Governed identity, not realized episode outcome.
                self.assertEqual(pins, projected_pins)
                self.assertEqual(metadata["workload_provenance"]["output_policy"]["emitted_tokens"], episode.totals()["decode_tokens"])
                self.assertEqual(validate_bundle(bundle, strict=True), [])
        # Reviewer's exact template fixture: 1795 minus 1721 = 74 tokens;
        # 40 * len("covert ") + len("<think></think>") adds 295 chars at 4 chars/token.
        self.assertEqual(episodes["think"].turns[2].prefill_tokens, 1795)
        self.assertEqual(episodes["normal"].turns[2].prefill_tokens, 1721)
        self.assertEqual(rows["think"][2]["generation"]["prior_hidden_prefill_tokens"], 74)
        self.assertEqual(rows["normal"][2]["generation"]["prior_hidden_prefill_tokens"], 0)
        self.assertEqual(rows["think"][2]["generation"]["prior_hidden_prefill_method"], "chat_template_token_count_difference")
