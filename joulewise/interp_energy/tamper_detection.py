"""Synthetic tamper sensitivity; no acquisition, model loading or data inputs.

Expected effects are explicit counterfactual assumptions, not fitted hardware
facts. The count/context baseline is reused from behaviour_channel; correlated
stress noise is generated with lockin's randomized ABBA and window simulation.
NumPy is lazy and MLX is never needed by this module.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
import math

from . import behaviour_channel as behaviour
from ._common import require_numpy
from .lockin import NoiseModel, abba_differences, make_schedule, simulate_trace
from .power import plan_power

CHANNELS = ("gpu_j", "dc_j", "time_s")
STATUS = "SYNTHETIC_UNCALIBRATED_NOT_HARDWARE_EVIDENCE"


@dataclass(frozen=True)
class Edit:
    name: str
    adversary: str = "non_adaptive"
    rate_fraction: float = 0.0
    time_fraction: float = 0.0
    gpu_dose_j: float = 0.0
    cpu_dose_j: float = 0.0
    accounted_gpu_j: float = 0.0
    hidden_seconds: float = 0.0
    accounted_seconds: float = 0.0
    decode_ratio: float = 1.0
    padding: str = "none"

    def __post_init__(self):
        if not isinstance(self.name, str) or not self.name.strip():
            raise ValueError("edit name must be nonempty")
        if self.adversary not in ("non_adaptive", "timing_masked", "adaptive"):
            raise ValueError("invalid adversary")
        if self.padding not in ("none", "idle", "adaptive"):
            raise ValueError("invalid padding")
        for name in ("rate_fraction", "time_fraction", "gpu_dose_j", "cpu_dose_j",
                     "accounted_gpu_j", "hidden_seconds", "accounted_seconds", "decode_ratio"):
            if not math.isfinite(getattr(self, name)):
                raise ValueError(f"nonfinite {name}")
        if (min(self.gpu_dose_j, self.cpu_dose_j, self.accounted_gpu_j,
                self.hidden_seconds, self.accounted_seconds) < 0 or self.decode_ratio <= 0
                or self.rate_fraction <= -1 or self.time_fraction <= -1
                or self.accounted_gpu_j > self.gpu_dose_j
                or self.accounted_seconds > self.hidden_seconds):
            raise ValueError("invalid dose, ratio or physical cost")
        if self.padding != "none" and (self.time_fraction >= 0 or self.rate_fraction > 0):
            raise ValueError("padding requires a faster, cheaper substitute")


def edit_catalogue() -> tuple[Edit, ...]:
    """Dose points are scenarios. Dense zero/outlier effects are UNKNOWN on Mac.

    Precision reductions are illustrative time-at-flat-power changes, not a
    claim of monotonic quantization savings or a transferred KB J/GB slope.
    Adaptive masking assumes enough budget to match BOTH observed boundaries.
    """
    return (
        Edit("sham"),
        Edit("surgical_astra", rate_fraction=1e-5),
        Edit("rank_one", rate_fraction=3.5e-5),
        Edit("merged_lora", rate_fraction=1e-5),
        Edit("dense_zero_hypothesis", rate_fraction=-.001),
        Edit("outlier_hypothesis", rate_fraction=.001),
        Edit("fixed_k_expert_identity"),
        Edit("structured_prune", rate_fraction=-.1, time_fraction=-.1),
        Edit("precision_swap", rate_fraction=-.35, time_fraction=-.35),
        Edit("precision_idle_mask", "timing_masked", rate_fraction=-.35,
             time_fraction=-.35, padding="idle"),
        Edit("precision_adaptive", "adaptive", rate_fraction=-.35,
             time_fraction=-.35, padding="adaptive"),
        Edit("unmerged_lora", rate_fraction=.03, time_fraction=.03),
        Edit("hidden_gpu_edit", gpu_dose_j=200, hidden_seconds=8),
        Edit("hidden_gpu_tool_wait", "timing_masked", gpu_dose_j=200),
        Edit("hidden_cpu_edit", cpu_dose_j=40),
        Edit("logged_gpu_edit", gpu_dose_j=200, accounted_gpu_j=200,
             hidden_seconds=8, accounted_seconds=8),
        Edit("precomputed_delta", cpu_dose_j=.1),
        Edit("behaviour_shortening", decode_ratio=.5),
    )


def reference_model() -> behaviour.EnergyModel:
    return behaviour.EnergyModel(.02, .3, context_j_per_token_squared=1e-6,
                                 fixed_j=200, coefficient_basis="gross",
                                 source="synthetic ~2.7 kJ GPU unit; NOT calibrated")


def expected_signal(edit: Edit, *, model=None, prefill_tokens=256,
                    decode_tokens=8192, duration_s=100.0,
                    dc_to_gpu=1.8, idle_gpu_w=2.0, idle_dc_w=12.0) -> dict:
    """Gross changes and residuals versus a frozen count/context prediction.

    DC coefficients here are simply dc_to_gpu times GPU coefficients, an
    explicit simulation assumption. CPU editing contributes only to DC;
    CPU-rail/total-rail detectors could close part of that gap on a real rig.
    Timing is compared with a count-conditioned baseline, not raw length.
    """
    model = reference_model() if model is None else model
    if model.coefficient_basis != "gross":
        raise ValueError("simulation requires explicit gross coefficients")
    for value in (duration_s, dc_to_gpu):
        if not math.isfinite(value) or value <= 0:
            raise ValueError("duration and boundary ratio must be positive")
    for value in (idle_gpu_w, idle_dc_w):
        if not math.isfinite(value) or value < 0:
            raise ValueError("idle powers must be nonnegative")
    base = behaviour.Answer("synthetic", prefill_tokens, decode_tokens, False)
    edited = behaviour.Answer("synthetic", prefill_tokens,
                              round(decode_tokens * edit.decode_ratio), False)
    base_j = behaviour.answer_energy(base, model)["gross_j"]
    edited_j = behaviour.answer_energy(edited, model)["gross_j"]
    behaviour_j = edited_j - base_j
    gpu = edited_j * edit.rate_fraction + edit.gpu_dose_j
    dc = dc_to_gpu * gpu + edit.cpu_dose_j
    time = duration_s * edit.time_fraction + edit.hidden_seconds - edit.accounted_seconds
    if edit.padding == "idle":
        gpu += -duration_s * edit.time_fraction * idle_gpu_w
        dc += -duration_s * edit.time_fraction * idle_dc_w
        time -= duration_s * edit.time_fraction
    elif edit.padding == "adaptive":
        # Observational-equivalence counterexample, NOT a demonstrated attack.
        gpu, dc, time = 0.0, 0.0, 0.0
    return {"status": STATUS, "baseline_gpu_j": base_j,
            "behaviour_delta_gpu_j": behaviour_j,
            "gpu_gross_delta_j": behaviour_j + gpu,
            "dc_gross_delta_j": dc_to_gpu * behaviour_j + dc,
            "gpu_j": gpu - edit.accounted_gpu_j,
            "dc_j": dc - dc_to_gpu * edit.accounted_gpu_j,
            "time_s": time}


@dataclass(frozen=True)
class StressNoise:
    """Absolute SD anchors, with additional colored noise/bursts/offsets.

    replay: 2.97 J is the study's paired GPU anchor; fresh episodes need 19-58 J
    residual noise (default 35 J). DC and timing SDs are assumptions. The white
    ABBA component alone has these SDs; stress terms increase the realized SD.
    """
    gpu_sd_j: float = 2.97
    dc_sd_j: float = 12.0
    time_sd_s: float = .12
    session_sd_j: float = 4.7
    pink_fraction: float = .25
    burst_rate_hz: float = .02

    def __post_init__(self):
        for name, value in asdict(self).items():
            if not math.isfinite(value) or value < 0:
                raise ValueError(f"invalid noise {name}")
        if min(self.gpu_sd_j, self.dc_sd_j, self.time_sd_s) <= 0:
            raise ValueError("noise SDs must be positive")


def synthetic_noise(count: int, *, seed: int, noise=None, session_offset_j=None):
    """Chronological paired-contrast surrogates using the shared lockin model.

    Eight-second ABBA blocks generate NOISE only, not 100-second replay work.
    W-to-J scaling is chosen to match the white component's absolute pair SD.
    This avoids claiming short chips earned the long-replay instrument floor.
    All boundaries use an 8 Hz surrogate; it is not a KM003C cadence model.
    """
    np = require_numpy()
    if isinstance(count, bool) or not isinstance(count, int) or count < 1:
        raise ValueError("count must be a positive integer")
    noise = StressNoise() if noise is None else noise
    if session_offset_j is not None and not math.isfinite(session_offset_j):
        raise ValueError("session offset must be finite")
    rng = np.random.default_rng(seed)
    def series(sd, trace_seed):
        white_w = sd / 100 * 4  # sqrt(2 seconds * 8 Hz)
        segments = []
        # Bound the shared simulator's per-burst window operations and memory.
        # Each segment has its own finite 1/f spectrum / warm-up / step; only
        # the session offset below spans the entire requested realization.
        for start in range(0, count, 256):
            schedule = make_schedule(min(256, count - start), chip_seconds=2,
                                     seed=seed + start)
            stress = NoiseModel(white_sd_w=white_w,
                                pink_sd_w=white_w * noise.pink_fraction,
                                thermal_amplitude_w=white_w / 2,
                                steps=((schedule.duration_seconds / 2, white_w),),
                                burst_rate_hz=noise.burst_rate_hz,
                                burst_mean_seconds=.7, burst_amplitude_w=4 * white_w)
            trace = simulate_trace(schedule, baseline_w=27, effect_fraction=0,
                                   noise=stress, seed=trace_seed + start)
            segments.append(abba_differences(trace) * 100)
        return np.concatenate(segments)

    gpu = series(noise.gpu_sd_j, seed + 1)
    independent_dc = series(noise.dc_sd_j, seed + 2)
    # One shared session offset remains even after averaging copies/replays.
    drawn_offset = rng.normal(0, noise.session_sd_j)
    gpu += drawn_offset if session_offset_j is None else session_offset_j
    dc = .6 * noise.dc_sd_j / noise.gpu_sd_j * gpu + .8 * independent_dc
    timing = (.5 * noise.time_sd_s / noise.gpu_sd_j * gpu
              + math.sqrt(.75) * rng.normal(0, noise.time_sd_s, count))
    return np.column_stack((gpu, dc, timing))


def _observations(values):
    np = require_numpy()
    result = np.asarray(values, dtype=float)
    if result.ndim != 2 or result.shape[1] != 3 or not len(result) or not np.isfinite(result).all():
        raise ValueError("expected nonempty finite N x 3 residuals in J, J, seconds")
    return result


@dataclass(frozen=True)
class Detector:
    thresholds: tuple[float, float, float]
    family_alpha: float
    calibration_units: int

    def __post_init__(self):
        if (len(self.thresholds) != 3
                or any(not math.isfinite(x) or x <= 0 for x in self.thresholds)
                or not 0 < self.family_alpha < 1
                or isinstance(self.calibration_units, bool)
                or not isinstance(self.calibration_units, int) or self.calibration_units < 1):
            raise ValueError("invalid detector calibration")

    def scores(self, observations):
        return abs(_observations(observations)) / require_numpy().asarray(self.thresholds)

    def flags(self, observations):
        return self.scores(observations) > 1


def calibrate(benign, *, family_alpha=.05) -> Detector:
    """Freeze empirical two-sided thresholds from HELD-OUT benign residuals.

    Each channel gets alpha/3 and the corrected (m+1) order statistic. A union
    bound applies under exchangeability with continuous benign scores. Shared
    session shifts/colored noise can break that assumption; the stress demo
    reports empirical sham errors and makes NO guaranteed false-alarm claim.
    No timing term is fitted into the energy prediction: padding stays visible.
    """
    np = require_numpy()
    benign = _observations(benign)
    if not 0 < family_alpha < 1:
        raise ValueError("family_alpha must be between zero and one")
    rank = math.ceil((len(benign) + 1) * (1 - family_alpha / 3))
    if rank > len(benign):
        raise ValueError("insufficient benign calibration units for finite thresholds")
    thresholds = np.sort(abs(benign), axis=0)[rank - 1]
    if (thresholds <= 0).any():
        raise ValueError("degenerate calibration; positive thresholds required")
    return Detector(tuple(float(x) for x in thresholds), family_alpha, len(benign))


def simulate_detector(*, copies_per_class=256, seed=17, noise=None,
                      edits=None, calibration_units=512) -> dict:
    """One stress realization; class order is interleaved before noise is added.

    Forced choice compares max normalized anomaly scores for each independent
    simulated tamper and its separately simulated matched sham in the SAME
    session offset. Calibration, test noise and pairing noise use separate RNG
    streams. Ties are fair coins.
    Rates below are descriptive for this realization, not binomial claims:
    chronological noise and common session shifts induce dependence.
    """
    np = require_numpy()
    if (isinstance(copies_per_class, bool) or not isinstance(copies_per_class, int)
            or copies_per_class < 1):
        raise ValueError("copies_per_class must be a positive integer")
    edits = edit_catalogue() if edits is None else tuple(edits)
    if not edits or len({e.name for e in edits}) != len(edits):
        raise ValueError("edits must have distinct names")
    noise = StressNoise() if noise is None else noise
    detector = calibrate(synthetic_noise(calibration_units, seed=seed, noise=noise))
    count = len(edits) * copies_per_class
    rng = np.random.default_rng(seed + 10)
    labels = rng.permutation(np.repeat(np.arange(len(edits)), copies_per_class))
    session_offset = rng.normal(0, noise.session_sd_j)
    observed = synthetic_noise(count, seed=seed + 20, noise=noise,
                               session_offset_j=session_offset)
    matched = synthetic_noise(count, seed=seed + 30, noise=noise,
                              session_offset_j=session_offset)
    results = []
    for index, edit in enumerate(edits):
        signal = expected_signal(edit)
        select = labels == index
        values = observed[select] + [signal[c] for c in CHANNELS]
        scores = detector.scores(values)
        flags = scores > 1
        max_scores = scores.max(axis=1)
        matched_scores = detector.scores(matched[select]).max(axis=1)
        wins = (max_scores > matched_scores).astype(float)
        ties = max_scores == matched_scores
        wins[ties] = rng.integers(0, 2, int(ties.sum()))
        gpu_effect = signal["gpu_j"]
        planning = (asdict(plan_power(effect_fraction=gpu_effect / signal["baseline_gpu_j"],
                                     unit_sd_fraction=noise.gpu_sd_j / signal["baseline_gpu_j"],
                                     unit_seconds=200, budget_hours=copies_per_class * 200 / 3600,
                                     systematic_bound_fraction=.5 / signal["baseline_gpu_j"]))
                    if gpu_effect else None)
        results.append({"edit": asdict(edit), "expected": signal,
                        "any_flag_rate": float(flags.any(axis=1).mean()),
                        "channel_flag_rates": dict(zip(CHANNELS, map(float, flags.mean(axis=0)))),
                        "forced_choice_rate": float(wins.mean()),
                        "gpu_independent_pair_white_noise_plan": planning})
    return {"status": STATUS, "seed": seed, "copies_per_class": copies_per_class,
            "noise": asdict(noise), "detector": asdict(detector), "classes": results,
            "limits": ["Effect sizes, DC ratio, timing SD and padding powers are assumptions.",
                       "One correlated stress realization; rates have no confirmatory CI.",
                       "Pair-white-noise plans exclude colored noise and session offsets.",
                       "Independent synthetic copies do not prove independent real artifacts.",
                       "No model edits, physical instruments or Block 5 data were executed."]}
