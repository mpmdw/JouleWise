"""R0 step-profile ruling and offline first-order fits; no hardware imports.

The laptop lead's 2026-11-05 ruling supersedes Amendment 1 A5.3's 60 s
load. Quality/coverage bars retain #658's diagnostic rules. Slow tau is
estimated from load alone; recovery confirms that estimate without refitting.
"""
from __future__ import annotations

import math
import statistics

DEFAULT_PROFILE = {"idle_seconds": 300, "load_seconds": 900, "recovery_seconds": 600}
SLOW_TAU_UPPER_SECONDS = 900
FAST_FIT_SECONDS = 120


class ProfileRefused(ValueError):
    def __init__(self, code, detail):
        self.code = code
        super().__init__(f"{code}: {detail}")


def profile_config(value=None):
    if value is None:
        value = {}
    if not isinstance(value, dict) or set(value) - set(DEFAULT_PROFILE):
        raise ProfileRefused("smc_step.invalid_profile", "expected idle_seconds, load_seconds, recovery_seconds")
    profile = {**DEFAULT_PROFILE, **value}
    if any(type(v) is not int or v <= 0 for v in profile.values()):
        raise ProfileRefused("smc_step.invalid_duration", "phase durations must be positive integer seconds")
    if profile["load_seconds"] < SLOW_TAU_UPPER_SECONDS:
        raise ProfileRefused("smc_step.load_below_tau_upper_bound",
                             f"load_seconds={profile['load_seconds']} must be >= slow tau upper bound "
                             f"{SLOW_TAU_UPPER_SECONDS} s (slow tau must be strictly below that bound)")
    return profile


def step_budget(value=None):
    profile = profile_config(value)
    total = sum(profile.values())
    # Planning allowance, not a measured row size or a hard journal size cap.
    return {"profile": profile, "capture_seconds": total,
            "timeout_seconds": total + 600, "sample_period_seconds": 1,
            "journal_bytes_per_slot_estimate": 16_384,
            "journal_bytes_estimate": total * 16_384,
            "journal_estimate_note": "16 KiB per 1 Hz slot; verify actual size after enumeration."}


def _finite(value):
    return type(value) in (int, float) and math.isfinite(value)


def _r2(observed, predicted):
    mean = statistics.mean(observed)
    total = sum((v - mean) ** 2 for v in observed)
    return 1 - sum((v - p) ** 2 for v, p in zip(observed, predicted)) / total if total > 0 else 0.0


def _load_fit(observations, noise, duration):
    def fit(tau):
        response = [-math.expm1(-t / tau) for t, _ in observations]
        denom = sum(x * x for x in response)
        amplitude = sum(x * v for x, (_, v) in zip(response, observations)) / denom
        return sum((v - amplitude * x) ** 2 for x, (_, v) in zip(response, observations)), tau, amplitude

    width = math.log(2 * max(duration, SLOW_TAU_UPPER_SECONDS) / .25) / 100
    best = min(fit(.25 * math.exp(width * i)) for i in range(101))
    best = min(fit(best[1] * math.exp(width * i / 20)) for i in range(-20, 21))
    _, tau, amplitude = best
    r2 = _r2([v for _, v in observations],
             [amplitude * -math.expm1(-t / tau) for t, _ in observations])
    return {"status": "pass" if amplitude > 3 * noise and r2 >= .8 and .3 < tau < duration else "inconclusive",
            "tau_s": tau, "amplitude": amplitude, "amplitude_to_noise": amplitude / noise,
            "fit_r2": r2, "fit_seconds": duration}


def rank_response(capture, samples, value=None):
    """Re-rank #658's authenticated journal with the lead's load-only fit rule.

    A 60 s sensor can have a passing resolved fit while belonging to neither
    role. Only a tau <30 s from the first 120 s can become S_fast. Recovery
    confirmation keeps #658's R2 >=0.8 quality bar but imposes no tau <600 s
    restriction on the slow class.
    """
    profile = profile_config(value)
    records = capture["phases"]
    if [p["phase"] for p in records] != ["idle", "load", "recovery"]:
        raise ValueError("SMC step phases must be idle, load, recovery")
    phases = {p["phase"]: p for p in records}
    previous = 0.0
    for name, bounds in phases.items():
        start, end = bounds["start_s"], bounds["end_s"]
        if (not _finite(start) or not _finite(end) or start < previous
                or not math.isclose(end - start, profile[name + "_seconds"], abs_tol=1e-6, rel_tol=0)):
            raise ValueError("SMC observed phase durations do not match configured profile")
        previous = end
    origin = capture["started"]["monotonic_ns"]
    rows = []
    for sensor in capture["inventory"]["keys"]:
        key = sensor["key"]
        row = {"key": key, "unit": sensor["unit"], "fast_eligible": False, "slow_eligible": False,
               "reason": "insufficient phase coverage", "phase_coverage": {}}
        rows.append(row)
        if sensor["unit"] != "degC":
            row["reason"] = "non-temperature sensor; excluded"
            continue
        good = {name: {} for name in phases}
        for sample in samples:
            name = sample.get("phase")
            if name not in phases or sample.get("kind") != "reading":
                continue
            bounds = phases[name]
            t = sample["elapsed_s"]
            finished = (sample["finished"]["monotonic_ns"] - origin) / 1e9
            v = sample["values"]["sensors"].get(key)
            if (_finite(t) and _finite(v) and -40 <= v <= 150
                    and key not in sample["values"]["errors"]
                    and bounds["start_s"] <= t <= finished < bounds["end_s"]
                    and int(t - bounds["start_s"]) == int(finished - bounds["start_s"])):
                good[name].setdefault(int(t - bounds["start_s"]), (t, v))
        row["phase_coverage"] = {name: len(good[name]) / profile[name + "_seconds"] for name in phases}
        if any(len(good[name]) < 5 or row["phase_coverage"][name] < .9 for name in phases):
            continue
        idle = [v for _, v in good["idle"].values()]
        baseline = statistics.mean(idle)
        noise = max(statistics.pstdev(idle), 1e-6)
        onset = phases["load"]["start_s"]
        load = [(t - onset, v - baseline) for t, v in good["load"].values()]
        fast = [(t, v) for t, v in load if t < FAST_FIT_SECONDS]
        slow_fit = _load_fit(load, noise, profile["load_seconds"])
        row.update(noise=noise, load_fit=slow_fit)
        if len(fast) >= .9 * FAST_FIT_SECONDS:
            fast_fit = _load_fit(fast, noise, FAST_FIT_SECONDS)
            row["fast_load_fit"] = fast_fit
            row["fast_eligible"] = fast_fit["status"] == "pass" and fast_fit["tau_s"] < 30
        recovery_onset = phases["recovery"]["start_s"]
        recovery = [(t - recovery_onset, v - baseline) for t, v in good["recovery"].values()]
        tau, amplitude = slow_fit["tau_s"], slow_fit["amplitude"]
        # Retain actual transition latency, as in #658. Never fit recovery back
        # into tau/amplitude or require tau to be below recovery duration.
        peak = amplitude * -math.expm1(-(recovery_onset - onset) / tau)
        recovery_r2 = _r2([v for _, v in recovery], [peak * math.exp(-t / tau) for t, _ in recovery])
        row["recovery_r2"] = recovery_r2
        row["slow_eligible"] = (slow_fit["status"] == "pass" and 120 < tau < SLOW_TAU_UPPER_SECONDS
                                and recovery_r2 >= .8)
        row["reason"] = "resolved load response" if slow_fit["status"] == "pass" else "weak, poor-fit or unresolved load response"

    def choose(role, fit):
        eligible = [r for r in rows if r[role + "_eligible"]]
        return min(eligible, key=lambda r: (-r[fit]["amplitude_to_noise"], r["key"]))["key"] if eligible else None

    fast, slow = choose("fast", "fast_load_fit"), choose("slow", "load_fit")
    return {"status": "pass" if fast and slow and fast != slow else "inconclusive",
            "s_fast": fast, "s_slow": slow, "ranking": rows,
            "rule": "S_fast: tau <30 s from first 120 s load; S_slow: 120 <tau <900 s from load, confirmed on recovery; locations PROVISIONAL."}
