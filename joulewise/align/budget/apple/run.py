"""One model/seed per live invocation; an offline synthetic matrix for rehearsal."""

from __future__ import annotations

import hashlib
import json
import math
import os
import platform
import subprocess
from dataclasses import asdict, replace
from pathlib import Path
from uuid import uuid4

from joulewise.align.apple.endpoint import MlxEndpoint
from joulewise.align.apple.sampler import monotonic_ns
from joulewise.align.budget.apple.endpoint import BudgetMlxEndpoint
from joulewise.align.budget.apple.models import CachedModel, MODEL_SIZES
from joulewise.align.budget.apple.sampling import BudgetAppleSampler, apple_energy, normalize_result
from joulewise.align.budget.conditions import default_conditions
from joulewise.align.budget.items import ItemBatch
from joulewise.align.budget.run import ModelSpec, Settings, run_matrix, summarize, summary_table
from joulewise.align.budget.score import HintMonitor
from joulewise.align.budget.storage import write_episode_views, write_result
from joulewise.align.budget.synthetic import ScriptedModel, ScriptedMonitor, WordCodec, synthetic_items
from joulewise.align.interfaces import ChatMessage
from joulewise.align.records import to_json
from joulewise.clock import FakeClock, SystemClock
from joulewise.interfaces import AdapterResult, PowerSample, RunContext, TelemetryStopResult
from joulewise.schemas import BenchmarkConfig

DOMAIN = "d3.apple.monotonic_ns"
STATUS = "PROVISIONAL_UNREGISTERED"


class BudgetClock:
    def __init__(self, clock):
        self.clock = clock

    def __call__(self):
        return monotonic_ns(self.clock.stamp())

    def advance(self, ns):
        self.clock.sleep(ns / 1_000_000_000)


def _implementation() -> str:
    root = Path(__file__).resolve().parents[2]
    paths = sorted(Path(__file__).parent.glob("*.py")) + [root / "apple" / n for n in (
        "endpoint.py", "sampler.py")]
    paths += [root.parents[0] / "adapters" / n for n in ("mlx_runtime.py", "powermetrics.py")]
    return hashlib.sha256(b"".join(p.name.encode() + p.read_bytes() for p in paths)).hexdigest()


def _settings(settings: Settings):
    if (settings.temperature != 0.0 or settings.measurement_id == "unmeasured"
            or settings.calibration_repetitions < 1 or settings.max_tokens < 1
            or settings.answer_max_tokens < 1):
        raise ValueError("D3 needs greedy temperature=0, a measurement_id and positive ceilings/calibration count")


def _conditions(order):
    defaults = default_conditions()
    if order is None:
        return defaults
    by_name = {c.name: c for c in defaults}
    if len(order) != len(defaults) or set(order) != set(by_name):
        raise ValueError("condition_order must be a permutation of the complete default matrix")
    return tuple(by_name[name] for name in order)


def preflight(endpoint: BudgetMlxEndpoint, settings: Settings, seed: int):
    """Warm without power attribution and exercise the pilot's prefix shapes.

    Successful calls show API support, not semantic validation of controls.
    The lead must inspect reasoning-off and the answer continuations before
    setting controls_verified. Preflight is preserved separately from trials.
    """
    messages = (ChatMessage("user", "What is 2 + 2? Return ANSWER: A for 4, B for 5."),)
    results = []
    for enabled in (True, False):
        results.append(endpoint.configured({"chat_template_kwargs": {"enable_thinking": enabled}}).chat(
            messages, max_tokens=settings.max_tokens, temperature=0.0, seed=seed))
    for shape in ("A natural close.", "A cut mid", "A paragraph cut.\n", ""):
        prefix = settings.thinking_open + "\n" + shape.strip("\n") + settings.thinking_end
        results.append(endpoint.configured({"chat_template_kwargs": {"enable_thinking": True},
                       "continue_final_message": True, "add_generation_prompt": False}).chat(
                           (*messages, ChatMessage("assistant", prefix)),
                           max_tokens=settings.answer_max_tokens, temperature=0.0, seed=seed))
    return tuple(results)


def export(output: Path, result):
    output.mkdir(parents=True, exist_ok=True)
    rows = summarize(result.trials, energy_reducer=apple_energy,
                     confidence=result.trials[0].settings.confidence)
    write_result(output / "result.json", result)
    (output / "summary.json").write_text(to_json(rows) + "\n", encoding="utf-8")
    (output / "summary.md").write_text(summary_table(rows), encoding="utf-8")
    write_episode_views(output / "episodes.jsonl", (t.episode for t in result.trials))
    write_episode_views(output / "paired_episodes.jsonl",
                        (t.paired.episode for t in result.trials if t.source_trial_id is None))
    write_episode_views(output / "calibration_episodes.jsonl",
                        (e for c in result.calibrations for e in c.episodes))
    return rows


class SyntheticAppleTelemetry:
    """Injected native-adapter boundary: 10 Hz interval averages on three rails.

    These designed values are not M3 measurements. Apple's representation
    adapter deliberately leaves sensor resolution unknown even in rehearsal.
    """
    def __init__(self, clock):
        self.clock = clock

    def start_sampling(self, config, context):
        self.start_s = self.clock.now()
        return AdapterResult(ok=True)

    def stop_sampling_with_evidence(self, config, context, **kwargs):
        step = 1 / config.sampling.power_hz
        count = math.floor((self.clock.now() - self.start_s) / step)
        samples = []
        for i in range(1, count + 1):
            t = self.start_s + i * step
            for rail, watts in (("cpu_power", 4.0), ("gpu_power", 28.0), ("ane_power", 0.3)):
                samples.append(PowerSample(t, watts, "powermetrics", rail, t - step, t))
        return TelemetryStopResult(samples, {"synthetic": True, "clock_anchor": {
            "status": "bounded", "method": "synthetic_identity_clock",
            "wall_minus_monotonic_lower_s": 0.0, "wall_minus_monotonic_upper_s": 0.0,
            "effective_clock_anchor_bound_s": 0.0}})


def run_dry(*, output: Path, config: BenchmarkConfig, count: int = 2, seed: int = 0):
    if count < 1:
        raise ValueError("count must be positive")
    clock = FakeClock(start=100.0)
    budget_clock = BudgetClock(clock)
    config = replace(config, sampling=replace(config.sampling, power_hz=10.0))
    items = synthetic_items(count)
    specs = []
    for repo_id, size in MODEL_SIZES.items():
        codec = WordCodec()
        endpoint = ScriptedModel(items.items, budget_clock, codec, base_reasoning_tokens=64)
        specs.append(ModelSpec(repo_id, size, "mock", endpoint.identity, codec,
                               endpoint.configured, "dense", DOMAIN, controls_verified=True))
    settings = Settings(128, 16, temperature=0.0, measurement_id="D3-SYNTHETIC-NOT-HARDWARE")
    result = run_matrix(items, specs, default_conditions(), seeds=(seed,), settings=settings,
                        monitor=HintMonitor(ScriptedMonitor(), model="synthetic-monitor", revision="script-v1"),
                        checkpoint=output / "checkpoint.jsonl", clock=budget_clock,
                        sampler_factory=lambda _: BudgetAppleSampler(
                            config, clock, episode_domain=DOMAIN, adapter=SyntheticAppleTelemetry(clock)),
                        run_metadata={"d3": {"status": STATUS, "synthetic": True,
                                              "implementation_sha256": _implementation(),
                                              "model_revisions": "synthetic; no weights loaded",
                                              "rail_scope": "gross CPU+GPU+ANE; not wall energy",
                                              "attribution_floor_j_approx": 1.0}})
    result = normalize_result(result)
    export(output, result)
    return result


def run_live(*, output: Path, config: BenchmarkConfig, model: CachedModel,
             items: ItemBatch, monitor: HintMonitor, settings: Settings,
             seed: int, controls_verified: bool = False, condition_order=None):
    """Explicit hardware entry point. The build seat never calls this function."""
    _settings(settings)
    conditions = _conditions(condition_order)
    if not items.items:
        raise ValueError("freeze a nonempty roster first")
    if platform.system() != "Darwin" or platform.machine() != "arm64":
        raise ValueError("D3 live capture requires Apple Silicon")
    chip = subprocess.check_output(["/usr/sbin/sysctl", "-n", "machdep.cpu.brand_string"], text=True).strip()
    if "Apple M3 Max" not in chip:
        raise ValueError(f"D3 target is M3 Max, observed {chip}")
    if config.hardware_target.runtime_backend.value != "mlx" or config.hardware_target.telemetry_backend.value != "powermetrics":
        raise ValueError("base benchmark must select MLX and powermetrics")
    # Local snapshot paths are used below; these also prevent library fallbacks.
    os.environ["HF_HUB_OFFLINE"] = "1"
    os.environ["TRANSFORMERS_OFFLINE"] = "1"
    from joulewise.adapters.mlx_runtime import MlxRuntimeAdapter

    clock = SystemClock()
    budget_clock = BudgetClock(clock)
    config = replace(config, model=replace(config.model, name=model.repo_id, family="qwen3",
                     source=model.snapshot, revision=model.revision, weight_format="mlx"),
                     quantization=replace(config.quantization, name="int4", bits=4))
    output.mkdir(parents=True, exist_ok=True)
    roster_json = to_json(items) + "\n"
    roster_sha256 = hashlib.sha256(roster_json.encode()).hexdigest()
    roster_path = output / "rosters" / f"{roster_sha256}.json"
    roster_path.parent.mkdir(exist_ok=True)
    if not roster_path.exists():
        with roster_path.open("x", encoding="utf-8") as handle:
            handle.write(roster_json)
    runtime = MlxRuntimeAdapter(clock)
    try:
        prepared = runtime.prepare(config)
        if not prepared.ok:
            raise RuntimeError(prepared.message)
        endpoint = BudgetMlxEndpoint(MlxEndpoint(runtime, config, clock, episode_domain=DOMAIN,
                                                 prepare_metadata=prepared.metadata))
        warmed = preflight(endpoint, settings, seed)
        (output / "preflight").mkdir(exist_ok=True)
        (output / "preflight" / f"{uuid4().hex}.json").write_text(to_json(warmed) + "\n", encoding="utf-8")
        stable_prepare = {k: v for k, v in prepared.metadata.items()
                          if k not in ("load_wall_time_s", "memory_snapshots")}
        spec = ModelSpec(model.repo_id, model.size_b, "mlx", endpoint.identity, endpoint.codec,
                         endpoint.configured, "dense", DOMAIN, controls_verified=controls_verified,
                         supports_budget_continuation=True)

        def sampler_factory(_):
            capture = output / "captures" / uuid4().hex
            for name in ("raw", "logs", "outputs"):
                (capture / name).mkdir(parents=True, exist_ok=False)
            context = RunContext(config, clock, capture.name, capture,
                                 capture / "raw", capture / "logs", capture / "outputs")
            return BudgetAppleSampler(config, clock, episode_domain=DOMAIN, context=context)

        result = run_matrix(items, (spec,), conditions, seeds=(seed,), settings=settings,
                            monitor=monitor, checkpoint=output / "checkpoint.jsonl", clock=budget_clock,
                            sampler_factory=sampler_factory, run_metadata={"d3": {
                                "status": STATUS, "synthetic": False, "model": asdict(model),
                                "implementation_sha256": _implementation(), "prepare": stable_prepare,
                                "benchmark": config.to_dict(),
                                "roster_sha256": roster_sha256,
                                "monitor_transport": {k: getattr(monitor.endpoint, k) for k in (
                                    "base_url", "backend", "model", "timeout_s", "options")
                                    if hasattr(monitor.endpoint, k)},
                                "hardware": chip, "rail_scope": "gross CPU+GPU+ANE; not wall energy",
                                "attribution_floor_j_approx": 1.0,
                                "order": [c.name for c in sorted(conditions, key=lambda c: c.mode == "deletion")]}})
        result = normalize_result(result)
        export(output, result)
        return result
    finally:
        runtime.cleanup(config)
