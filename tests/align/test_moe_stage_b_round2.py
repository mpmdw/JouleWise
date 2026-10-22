"""Round-2 reviewer worlds through the real traffic/sensor/analysis chain.

The no-shell fallback consolidates identical worlds, but preserves every probe
parameter, patched experiment global and numerical comparison. Evidence is
printed before assertions and contains the command-equivalent case names.
"""
from __future__ import annotations

import hashlib
import json
import math
import os
import random
import statistics
import unittest
from dataclasses import replace
from unittest.mock import patch

import joulewise.align.moe_stage_b.experiment as ex
from joulewise.align.moe_stage_b.analysis import (
    recover_power_increment, fisher_interval_95, pearson,
)

DESIGN = dict(stage_a_effect_sd=1.0, n_per_condition=50, alpha=.05, power=.8, comparisons=3)


def emit(tag, value):
    print("STAGEB_R2 " + tag + " " + json.dumps(value, sort_keys=True), flush=True)


def summary(result):
    inc = result["power_increment_over_timing"]
    return dict(r=inc["held_out_correlation"], ci=inc["held_out_interval_95"],
        verdict=result["stage_b_verdict"], flags=inc["flags"],
        recovery={k: (v["within_condition_held_out_correlation"],
                      v["within_condition_held_out_interval_95"], v["verdict"])
                  for k, v in result["recovery"].items()},
        required=result["requirement"]["minimum_absolute_correlation"],
        decode_s=result["decode_duration_s_range"], episodes=result["episodes"])


def within_fit(obs):
    """Reviewer's q6 sketch, retained independently of the shipped oracle."""
    truth, pred, labels = [], [], []
    for target in obs:
        train = [o for o in obs if o.group != target.group]
        rows = {c: [o for o in train if o.episode_id.endswith("-sabotage") == c]
                for c in (False, True)}
        means = {c: (statistics.fmean(o.features.decode_seconds_per_token for o in v),
                     statistics.fmean(o.features.energy_per_decode_token_j for o in v),
                     statistics.fmean(o.routing_statistic for o in v)) for c, v in rows.items()}
        cond = lambda o: o.episode_id.endswith("-sabotage")
        T = [o.features.decode_seconds_per_token-means[cond(o)][0] for o in train]
        E = [o.features.energy_per_decode_token_j-means[cond(o)][1] for o in train]
        R = [o.routing_statistic-means[cond(o)][2] for o in train]
        tt = math.fsum(t*t for t in T)
        se = math.fsum(t*e for t, e in zip(T, E))/tt
        sr = math.fsum(t*r for t, r in zip(T, R))/tt
        er, rr = [e-se*t for e, t in zip(E, T)], [r-sr*t for r, t in zip(R, T)]
        slope = math.fsum(e*r for e, r in zip(er, rr))/math.fsum(e*e for e in er)
        c = cond(target); mt, me, mr = means[c]
        dt = target.features.decode_seconds_per_token-mt
        truth.append(target.routing_statistic-mr-sr*dt)
        pred.append(slope*(target.features.energy_per_decode_token_j-me-se*dt))
        labels.append(c)
    tx, py = [], []
    for c in (False, True):
        pairs = [(a, b) for a, b, label in zip(truth, pred, labels) if label == c]
        ma, mb = statistics.fmean(a for a, _ in pairs), statistics.fmean(b for _, b in pairs)
        tx += [a-ma for a, _ in pairs]; py += [b-mb for _, b in pairs]
    r = pearson(tx, py)
    return r, fisher_interval_95(r, len(tx), fitted_means=3)


class TestMoeStageBRound2(unittest.TestCase):
    def test_all_reviewer_worlds(self):
        with patch.dict(os.environ, {"JW_B5_SYNTHETIC_ONLY": "1"}):
            self.run_probes()

    def run_probes(self):
        cache = {}
        ina, nvml = ex.default_sensors()
        real_obs, real_sim, real_extract, real_synthetic = (
            ex.RoutingObservation, ex.simulate_episode, ex.extract_features, ex.synthetic_episode)
        def run(mode="e2e_nostall", sensor_i=0, *, seed=20261021, jitter=2_000_000,
                variant="real", offset=0.0):
            key = (mode, sensor_i, seed, jitter, variant, offset)
            if key in cache:
                return cache[key]
            world = (ex.WorldConfig(seed=seed, decode_step_jitter_ns=jitter) if mode == "default"
                     else ex.WorldConfig(groups=48, turns=3, decode_miss_stalls=mode == "e2e",
                                         seed=seed, decode_step_jitter_ns=jitter))
            sensor = (ina, nvml)[sensor_i]
            cap = []
            def capture(*a, **kw):
                o = real_obs(*a, **kw); cap.append(o); return o
            def sim(episode, config, sensor, **kw):
                out = real_sim(episode, config, sensor, **kw)
                if variant not in ("const_off", "noise_only", "condition"):
                    return out
                tr = out.episode.power_traces[-1]
                level = kw["baseline_w"]+kw["decode_load_w"]
                rng = random.Random(f"probe-{kw['seed']}")
                if variant == "const_off":
                    values = tuple(level+.5 for _ in tr.values)
                else:
                    level += offset if episode.condition == "sabotage" else 0.0
                    q = sensor.quantum_w
                    values = tuple(round((level+rng.gauss(0, sensor.noise_std_w))/q)*q
                                   for _ in tr.values)
                tr = replace(tr, values=values)
                return replace(out, episode=replace(out.episode,
                    power_traces=out.episode.power_traces[:-1]+(tr,)))
            def extract(episode, trace, **kw):
                if variant == "b_plus1":
                    kw["baseline_w"] += 1
                return real_extract(episode, trace, **kw)
            def synthetic(config, **kw):
                ep = real_synthetic(config, **kw)
                return (replace(ep, episode_id=hashlib.sha256(ep.episode_id.encode()).hexdigest())
                        if variant == "hash" else ep)
            try:
                with patch.object(ex, "RoutingObservation", capture), \
                     patch.object(ex, "simulate_episode", sim), \
                     patch.object(ex, "extract_features", extract), \
                     patch.object(ex, "synthetic_episode", synthetic):
                    result = ex.run_world(world, sensor, all_resident=False, **DESIGN)
                out = (summary(result), cap)
            except Exception as error:
                out = (dict(error=type(error).__name__, message=str(error)), cap)
            cache[key] = out
            return out
        checks = []
        # q1: only the opaque Episode ID changes, through the actual runner seam.
        for mode, sensor_i in (("default", 0), ("default", 1), ("e2e_nostall", 0), ("e2e_nostall", 1)):
            a, _ = run(mode, sensor_i); b, _ = run(mode, sensor_i, variant="hash")
            emit(f"q1_ids {mode} {sensor_i}", dict(suffix_ids=a, hash_ids=b))
            checks.append(("opaque IDs complete and preserve verdict", "error" not in b and
                           b.get("verdict") == a.get("verdict")))
            if "ci" in a and "r" in b and a["ci"]:
                # 1% of the suffix run's printed 95% half-width, rule 3.
                checks.append(("opaque IDs preserve increment", abs(a["r"]-b["r"]) <
                               .01*(a["ci"][1]-a["ci"][0])/2))
        # q1b: identical observations apart from ID strings require bit identity.
        for mode, sensor_i in (("e2e_nostall", 0), ("e2e", 0), ("default", 1), ("e2e_nostall", 1)):
            result, cap = run(mode, sensor_i)
            a = recover_power_increment(cap)
            b = recover_power_increment([replace(o, episode_id=hashlib.sha256(
                o.episode_id.encode()).hexdigest()) for o in cap])
            aa, bb = (a.held_out_correlation, a.held_out_interval_95), (b.held_out_correlation, b.held_out_interval_95)
            emit(f"q1b_increment_ids {mode} {sensor_i}", dict(suffix_ids=aa, hash_ids=bb, flags=b.flags))
            checks.append(("ID-only replacement is bit-identical", aa == bb))
        # q2: real, stuck off-level, blind noise, analyst baseline shift.
        blind = {}
        for variant in ("real", "const_off", "noise_only", "b_plus1"):
            result, _ = run("e2e", variant=variant); blind[variant] = result
            emit("q2_blind "+variant, result)
        for variant in ("const_off", "noise_only"):
            checks.append(("blind sensor gives no yes", blind[variant]["verdict"] != "yes"))
        checks.append(("noise-only verdict", blind["noise_only"]["verdict"] == "no"))
        checks.append(("baseline shift preserves verdict", blind["real"]["verdict"] == blind["b_plus1"]["verdict"]))
        for row in ("increment", "mean_decode_power_w"):
            r = blind["real"]; b = blind["b_plus1"]
            rv, bv = (r["r"], b["r"]) if row == "increment" else (
                r["recovery"][row][0], b["recovery"][row][0])
            ci = r["ci"] if row == "increment" else r["recovery"][row][1]
            # Agreement is 1% of this row's printed 95% half-width (rule 3).
            checks.append(("baseline shift preserves "+row, abs(rv-bv) < .01*(ci[1]-ci[0])/2))
        for jitter in (2_000_000, 10_000_000, 25_000_000):
            result, _ = run("e2e", jitter=jitter); emit(f"q3_jitter {jitter}", result)
        for sensor_i, seeds in ((0, range(1, 7)), (1, range(1, 4))):
            for seed in seeds:
                result, _ = run(sensor_i=sensor_i, seed=seed)
                emit(f"q4_seeds {seed} nostall {sensor_i}", result)
        # q5 + l1: constant timing flags, random covariates cannot create a
        # measured change larger than the constant result's 95% half-width.
        for mode, sensor_i in (("e2e_nostall", 0), ("e2e_nostall", 1), ("e2e", 0)):
            result, cap = run(mode, sensor_i)
            def timing(values):
                return [replace(o, features=replace(o.features, decode_seconds_per_token=v))
                        for o, v in zip(cap, values)]
            const = recover_power_increment(timing([.05]*len(cap)))
            ts = [o.features.decode_seconds_per_token for o in cap]
            mt, sd = statistics.fmean(ts), statistics.pstdev(ts)
            vals = []
            for k in range(10):
                rng = random.Random(1000+k)
                vals.append(recover_power_increment(timing([rng.gauss(mt, sd) for _ in cap])).held_out_correlation)
            half = (const.held_out_interval_95[1]-const.held_out_interval_95[0])/2 if const.held_out_interval_95 else None
            worst = max(abs(v-const.held_out_correlation) for v in vals) if all(v is not None for v in vals) and half else None
            passed = worst is not None and worst < half
            emit(f"l1_random_covariate {mode} {sensor_i}", dict(real=(result["r"], result["ci"]),
                const=(const.held_out_correlation, const.held_out_interval_95, const.flags),
                random_covariate=vals, worst_abs_change=worst, bar_half_width=half,
                result="PASS" if passed else "FAIL"))
            checks.append(("independent random covariate stays below printed uncertainty", passed))
            checks.append(("constant timing is flagged", "constant_within_condition_training_timing" in const.flags))
            if mode == "e2e_nostall":
                emit(f"q5_procedure {sensor_i}", dict(a_increment=result["r"],
                    b_increment_no_timing=const.held_out_correlation,
                    c_energy_only_within=result["recovery"]["energy_per_decode_token_j"][0]))
        # q6: all five cases, independently rederived within-condition sketch.
        for mode, sensor_i, jitter in (("e2e_nostall", 0, 2_000_000), ("e2e_nostall", 1, 2_000_000),
                ("e2e", 0, 2_000_000), ("e2e", 0, 10_000_000), ("e2e", 0, 25_000_000)):
            result, cap = run(mode, sensor_i, jitter=jitter)
            expected, ci = within_fit(cap)
            tsd = statistics.fmean(statistics.pstdev([
                o.features.decode_seconds_per_token for o in cap
                if o.episode_id.endswith("-sabotage") == c]) for c in (False, True))
            emit(f"q6_leak {mode} {sensor_i} {jitter}", dict(shipped=(result["r"], result["ci"], result["verdict"]),
                 within_condition_nuisance_fit=(expected, ci), within_sd_timing_ms=tsd*1000))
            # Rule 3: 1% of the sketch's printed 95% half-width.
            checks.append(("within-condition sketch agrees", abs(expected-result["r"]) < .01*(ci[1]-ci[0])/2))
        # q7 + q8: within each condition this sensor observes noise only.
        for mode, offset in (("e2e_nostall", 0.0), ("e2e_nostall", .1),
                            ("e2e_nostall", .3), ("e2e_nostall", 1.0), ("e2e", .3)):
            result, cap = run(mode, variant="condition", offset=offset)
            emit(f"q7_condition_sensor {mode} {offset}", result)
            checks.append(("condition-offset sensor gives no yes", result["verdict"] != "yes"))
            if mode == "e2e_nostall" and offset == .3:
                emit("q8_fixcheck", dict(shipped=result["r"], within_condition_fit=within_fit(cap)))
        emit("checks", checks)
