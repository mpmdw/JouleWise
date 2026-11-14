"""Synthetic backend for the WP15 R1 runtime (tests only).

SYNTHETIC ONLY: the WP22 world (``tests.align.w1_synthetic``) supplies a fake
clock, SMC transport, PM status, a powermetrics-labelled GPU rail and a fake
native mlx_lm stream; ``ps``, ``pmset`` and ``sysctl`` are answered from the
world. The runtime's production orchestration, run_benchmark, the episode
adapter, ThermalSession gates, deadman and bundle custody all run unchanged.
No model, SHADE cache, sensor or host setting is touched.

Selected by an R1 runtime config with ``"backend": "synthetic"``; its
``synthetic`` block may set ``battery`` {start_pct, drain_pct_per_h,
resume_at_pct}, ``background_pcpu``, ``decline_after_s`` (a synthetic
GPU clock decline that far into decode), ``slow_gain`` and ``powermode_file``
(a file holding the host's AC powermode, kept by a test's fake sudo, so the
ruling 7 record follows the driver's A-B-A and series settings).
"""
from __future__ import annotations

from contextlib import nullcontext
from types import SimpleNamespace
from copy import deepcopy
import json
import math
import os
from pathlib import Path
import subprocess

from joulewise.align.apple import r1_runtime as rt
from tests.align import w1_synthetic as syn

NS = syn.NS
HEATER_W = 80.0
PMSET_CUSTOM = ("System-wide power settings:\nCurrently in use:\n lowpowermode         0\n"
                "AC Power:\n lowpowermode         0\n powermode            {mode}\n sleep                0\n")


class R1World(syn.World):
    """The WP22 world plus per-second hooks (the runtime's journals and heater)."""

    def __init__(self, **kwargs):
        self.hooks = []
        self._next_hook = None
        super().__init__(**kwargs)

    def advance(self, seconds):
        end = self.clock.now() + seconds
        while True:
            now = self.clock.now()
            if self._next_hook is None:
                self._next_hook = math.floor(now) + 1
            if self._next_hook > end:
                break
            super().advance(self._next_hook - now)
            self.clock._now = self._next_hook
            for hook in list(self.hooks):
                hook()
            self._next_hook += 1
        rest = end - self.clock.now()
        if rest > 0:
            super().advance(rest)


class SyntheticHeater:
    def __init__(self, world):
        self.world = world
        self.stopped = False

    def set_duty(self, duty):
        self.world.extra_heat_w = HEATER_W * min(1.0, max(0.0, duty))

    def stop(self):
        self.stopped = True
        self.world.extra_heat_w = 0.0


def completed(argv, stdout="", code=0):
    return subprocess.CompletedProcess(list(argv), code, stdout, "")


class SyntheticBackend:
    name = "synthetic"

    def __init__(self, config):
        self.config = config
        self.options = config.get("synthetic") or {}
        # slow_gain (C/W): the heatsink pole's gain; the WP22 default gives the
        # D step a ~3 C rise, at the WP14(a) heatsink-class boundary.
        self.world = R1World(**({"slow_gain": float(self.options["slow_gain"])}
                                if "slow_gain" in self.options else {}))
        self.clock = self.world.clock
        self.stack, _ = syn.patches(self.world)
        self.stack.__enter__()
        self.powermode = int(self.options.get("powermode", 0))
        self.heaters = []

    # Host commands --------------------------------------------------------
    def battery_line(self):
        battery = {"start_pct": 100.0, "drain_pct_per_h": 0.0, "resume_at_pct": None,
                   **(self.options.get("battery") or {})}
        soc = battery["start_pct"] - battery["drain_pct_per_h"] * self.clock.now() / 3600.0
        resume = battery["resume_at_pct"]
        state = "charging" if resume is not None and soc <= resume else "discharging"
        return (f"Now drawing from 'AC Power'\n -InternalBattery-0 (id=1)\t{int(soc)}%; {state}; "
                f"0:00 remaining present: true\n")

    def run_cmd(self, argv):
        argv = tuple(argv)
        if argv == tuple(rt.contract.PS_ARGV):
            background = float(self.options.get("background_pcpu", 5.0))
            return completed(argv, f"    1     0   0.1 /sbin/launchd\n"
                                   f"{os.getpid():5d}     1  80.0 python3\n"
                                   f"  400     1 {background:5.1f} /usr/libexec/mds_stores\n")
        if argv == rt.PMSET_BATT:
            return completed(argv, self.battery_line())
        if argv[:3] == ("/usr/bin/pmset", "-g", "custom"):
            return completed(argv, PMSET_CUSTOM.format(mode=self.current_powermode()))
        if argv[:3] == ("/usr/bin/pmset", "-g", "therm"):
            return completed(argv, "No thermal warning level has been recorded\n")
        if argv[:2] == ("/usr/sbin/sysctl", "iogpu.wired_limit_mb"):
            return completed(argv, "iogpu.wired_limit_mb: 0\n")
        if argv[:3] == ("/usr/sbin/sysctl", "-n", "hw.memsize"):
            return completed(argv, str(128 * 1024 ** 3) + "\n")
        return completed(argv, "", code=127)

    def epoch(self):
        return self.clock.stamp().epoch_s

    def monotonic(self):
        return self.clock.now()

    def ticker(self, callback):
        self.world.hooks.append(callback)

        def stop():
            if callback in self.world.hooks:
                self.world.hooks.remove(callback)
        return stop

    # Collectors -------------------------------------------------------------
    def inventory_reader(self):
        world = self.world

        class Reader:
            # A one-quantum deterministic dither stands in for sensor noise, so a
            # settled synthetic key is not a "constant/stale idle series".
            reads = 0

            def enumerate_sensors(self):
                return {"keys": [{"key": key, "unit": "rpm" if key == syn.FAN else "degC",
                                  "data_type": "flt ", "data_size": 4}
                                 for key in sorted((syn.FAST, syn.SLOW, syn.FAN, "Ta0P"))],
                        "errors": {}, "unsupported_types": {}, "complete": True}

            def read(self, keys):
                self.reads += 1
                dither = ((self.reads % 3) - 1) / 256
                # RL-145 close: the gate pair is one thermometer under two names, so the classification
                # journal reads the slow key as the fast key's alias (the gates keep their own two series).
                values = {syn.FAST: world.t_fast + dither, syn.SLOW: world.t_fast + dither, syn.FAN: 1200.0,
                          "Ta0P": syn.AMBIENT_C + 0.001 * world.t_slow}
                return {"values": {key: round(values[key] * 256) / 256 for key in keys if key in values},
                        "errors": {key: "unknown synthetic sensor" for key in keys if key not in values}, "raw": {}}

        return Reader()

    def session(self, policy, outputs_dir, run_id, *, pm_status=False):
        from types import SimpleNamespace
        from joulewise.align.apple.smc_reader import Reader
        from joulewise.align.apple.thermal_gates import ThermalSession
        outputs_dir = Path(outputs_dir)
        outputs_dir.mkdir(parents=True, exist_ok=True)
        context = SimpleNamespace(outputs_dir=outputs_dir, bundle_path=outputs_dir, run_id=run_id)
        session = ThermalSession(policy, self.clock, context, reader=Reader(self.world.transport()),
                                 status_reader=self.world.status if pm_status else None)
        self.world.register(session)
        session.start()
        return rt.ManagedSession(session, on_close=lambda: self.world.unregister(session))

    def run_member(self, config_map, runs_root, hook):
        from joulewise.align.apple.thermal_gates import ThermalRegistry
        from joulewise.controller import run_benchmark
        from joulewise.schemas import BenchmarkConfig
        from scripts.align_v4_w1_synthetic import Delegate, mirror, thermal_factory
        config_map = deepcopy(config_map)
        family = config_map["model"]["family"]
        config_map["model"]["source"] = mirror(Path(runs_root).parent / "synthetic", family)
        spec = json.loads(config_map["workload_profile"]["prompt_text"])
        if spec["task_factory"] != rt.STEP_TASK_FACTORY:
            spec["task_factory"] = rt.SYNTHETIC_TASK_FACTORY
            spec["task_kwargs"] = {"task_pair": spec["task_kwargs"]["task_pair"]}
            config_map["workload_profile"]["prompt_text"] = rt.canonical(spec)
        base = thermal_factory(self.world)

        def factory(policy, clock, context, status_reader=None):
            session = base(policy, clock, context, status_reader)
            if hook is not None:
                hook(session)
            return session
        registry = ThermalRegistry(delegate=Delegate(self.world), thermal_factory=factory,
                                   status_factory=lambda telemetry, clock: self.world.status,
                                   powermode_reader=self.current_powermode)
        self.world.family, self.world.run_id, self.world.turn = family, config_map["run_id"], 0
        from joulewise.align.apple import thermal
        from joulewise.align.apple.smc_reader import Reader
        from joulewise.align.apple.thermal_gates import _EpisodeClocks
        from joulewise.hazards.base import Context
        from unittest.mock import patch
        native_sidecar = thermal.Sidecar
        sidecars = []
        def sidecar_factory(outputs, policy):
            obj = native_sidecar(outputs, policy, reader=Reader(self.world.transport()),
                ctx=Context(clocks=_EpisodeClocks(SimpleNamespace(clock=self.clock))))
            obj.sample = obj.tick
            original = obj.start
            def start():
                original(background=False)
                obj.tick()
            obj.start = start
            self.world.register(obj)
            sidecars.append(obj)
            return obj
        try:
            with patch.object(thermal, "Sidecar", side_effect=sidecar_factory) if "sensors" not in (spec.get("thermal") or {}) and spec.get("thermal") else nullcontext():
                bundle, summary = run_benchmark(BenchmarkConfig.from_mapping(config_map), Path(runs_root), self.clock,
                                                registry=registry)
            return Path(bundle), summary
        finally:
            for obj in sidecars:
                self.world.unregister(obj)

    def current_powermode(self):
        path = self.options.get("powermode_file")
        return int(Path(path).read_text()) if path else self.powermode

    def heater(self, workdir):
        heater = SyntheticHeater(self.world)
        self.heaters.append(heater)
        return heater

    def pm_samples(self, bundle, ep):
        rows = syn.pm_samples(self.world, ep.start_ns - NS, ep.end_ns + NS)
        after = self.options.get("decline_after_s")
        if after is not None and ep.turns and ep.turns[0].first_token_ns is not None:
            cut = ep.turns[0].first_token_ns + round(after * NS)
            for row in rows:
                if row["start_ns"] >= cut:
                    row["clock_mhz"] = 1300.0
        return rows

    def close(self):
        self.world.extra_heat_w = 0.0
        self.stack.close()


def synthetic_config(root, *, templates=None, d_n_chunk=None, **synthetic):
    """Write a synthetic R1 runtime config plus filled kit-template copies under ``root``."""
    root = Path(root)
    root.mkdir(parents=True, exist_ok=True)
    production = json.loads((rt.ROOT / "configs/align/v4/r1_runtime.json").read_text())
    # RL-145 addendum row 2: the production config carries d_n_chunk (candidate, 4,096). The
    # synthetic runs keep the registered formula (key absent) unless a test passes a value.
    production.pop("d_n_chunk", None)
    production.pop("d_n_chunk_status", None)
    if d_n_chunk is not None:
        production["d_n_chunk"] = d_n_chunk
    out_templates = {}
    for key, path in production["templates"].items():
        config, spec = rt.read_template(path)
        if config["model"]["family"] == "qwen3_5":
            spec["chat_template_kwargs"] = {"reasoning_effort": "xhigh"}
        if key == "x_g":
            spec["max_turns"] = 3
        config["workload_profile"]["prompt_text"] = rt.canonical(spec)
        target = root / f"template-{key}.json"
        target.write_text(json.dumps(config, indent=2, sort_keys=True) + "\n")
        out_templates[key] = str(target)
    out_templates.update(templates or {})
    config = dict(production, backend="synthetic", templates=out_templates,
                  sensors={"s_fast": syn.FAST, "s_slow": syn.SLOW, "fan_keys": [syn.FAN],
                           "record_keys": ["Tf08"], "r0_sha256": "a" * 64},
                  r0_classified_keys=[syn.FAST, syn.SLOW],
                  # RL-145 section 3: the non-alias branch of night_confirmation needs a die second key.
                  r0_classes={syn.FAST: "die", syn.SLOW: "die"},
                  step={**production["step"], "prefill_chars": 4000},
                  battery_poll_s=30, synthetic={"battery": {"drain_pct_per_h": 9.0}, **synthetic})
    path = root / "r1_runtime_synthetic.json"
    path.write_text(json.dumps(config, indent=2, sort_keys=True) + "\n")
    return path
