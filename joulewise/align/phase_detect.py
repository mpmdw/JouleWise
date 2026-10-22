"""Noise-penalized binary segmentation of power, without access to agent logs.

Binary segmentation costs O(n log n) for balanced changes and uses O(n) storage;
it is practical for sub-ms traces without a quadratic dynamic-programming
table. Its greedy splits can miss short balanced troughs; sensitivity must be
reported by sensor/duration rather than presumed. Labels assume idle < decode
< prefill and shorter prefill bursts, as in the synthetic timeline model.
Read gaps widen boundary uncertainty. Held values are thinned by observed
cadence; robust multiscale variance retains within-decode token modulation.
"""

from __future__ import annotations

import math
import statistics
from dataclasses import dataclass, replace

from joulewise.align.records import Episode, PowerTrace, ToolCall


@dataclass(frozen=True)
class Segment:
    start_ns: int
    end_ns: int
    mean_w: float
    label: str
    clock_domain: str = ""
    sample_interval_ns: int = 0
    averaging_window_ns: int = 0
    flags: tuple[str, ...] = ()
    boundary_uncertainty_ns: int = 0


@dataclass(frozen=True)
class ToolCallMatch:
    recall: float
    precision: float
    unmatched_logged: tuple[ToolCall, ...]
    unlogged_candidates: tuple[Segment, ...]
    flags: tuple[str, ...] = ()
    matched_count: int = 0
    tolerance_ns: int = 0
    indeterminate_candidates: tuple[Segment, ...] = ()


def estimate_noise_sd(values: tuple[float, ...]) -> float:
    """MAD of first differences / (sqrt(2) * Phi^-1(0.75)).

    Gaussian independent read noise differences have sd sqrt(2)*sigma.
    The Gaussian MAD consistency factor is Phi^-1(0.75), computed by stdlib.
    Sparse phase boundaries are robust outliers; ripple/correlation can bias
    this estimator, which is a limitation, not a hardware noise calibration.
    """
    if len(values) < 2:
        return 0.0
    # Adjacent bit-identical repeats are held observations, not independent
    # noise measurements. Any sensor can be polled faster than it converts.
    distinct = [a for i, a in enumerate(values) if i == 0 or a != values[i - 1]]
    if len(distinct) < 2:
        return 0.0
    differences = [b - a for a, b in zip(distinct, distinct[1:])]
    center = statistics.median(differences)
    mad = statistics.median(abs(x - center) for x in differences)
    return mad / (math.sqrt(2) * statistics.NormalDist().inv_cdf(0.75))


def detect_phases(trace: PowerTrace, *, noise_sd_w: float | None = None) -> list[Segment]:
    """Split on SSE reduction > 2 sigma^2 log(n), then label level/duration.

    Each split adds a mean and a boundary-location parameter. BIC contributes
    log(n) for each, giving 2*sigma^2*log(n) in SSE units. This is a model
    selection convention, not a fitted detection threshold. Quantization
    contributes variance q^2/12 for a uniform rounding bin.
    """
    n = len(trace.values)
    flags = []
    interval = trace.nominal_interval_ns
    window = trace.averaging_window_ns or 0
    if trace.unit != "W":
        flags.append("unsupported_cumulative_energy")
    if interval <= 0 or window < 0:
        flags.append("invalid_sensor_timing")
    if not all(math.isfinite(x) for x in trace.values):
        flags.append("nonfinite_power")
    if noise_sd_w is not None and (noise_sd_w < 0 or not math.isfinite(noise_sd_w)):
        flags.append("invalid_noise_sd")
    if n == 0:
        flags.append("empty_trace")
    if flags:
        return [Segment(trace.t_ns[0] if n else 0, trace.t_ns[-1] if n else 0,
                        0.0, "unknown", trace.clock_domain, interval, window, tuple(flags))]
    if trace.averaging_window_ns is None:
        flags.append("averaging_window_unknown")
    # A missing acquisition needs one whole extra nominal bin; ordinary
    # sub-period scheduler jitter is not a lost sample.
    gaps = [(a, b) for a, b in zip(trace.t_ns, trace.t_ns[1:]) if b - a >= 2 * interval]
    if gaps:
        flags.append("sample_gaps")
    # Infer held-register cadence only when changes are numerous enough to
    # distinguish a conversion stream from a few real phase plateaus. The
    # sqrt(n) count is the same local scale used for nuisance estimation;
    # sparse step traces must retain their duration/sample likelihood weight.
    changes = [i for i, value in enumerate(trace.values)
               if i and value != trace.values[i - 1]]
    change_times = [trace.t_ns[i] for i in changes]
    observed_periods = [b - a for a, b in zip(change_times, change_times[1:])]
    repeated = n - 1 - len(changes)
    effective_interval = interval
    if len(changes) >= math.isqrt(n) and observed_periods and repeated * 2 >= n - 1:
        effective_interval = max(interval, round(statistics.median(observed_periods)))
        flags.append("held_values_cadence_inferred")
    # Thin by the observed cadence rather than removing entire constant
    # plateaus. A 500 ms truly idle span still has 500/dt observations.
    indices = list(range(n))
    if effective_interval > interval:
        indices = [0]
        for i in range(1, n):
            if trace.t_ns[i] - trace.t_ns[indices[-1]] >= effective_interval:
                indices.append(i)
    times = [trace.t_ns[i] for i in indices]
    xs = tuple(trace.values[i] for i in indices)
    n = len(xs)
    sigma = estimate_noise_sd(xs) if noise_sd_w is None else noise_sd_w
    if noise_sd_w is None:
        flags.append("noise_estimated_from_differences")
    quantum = trace.resolution or 0.0
    if quantum < 0 or not math.isfinite(quantum):
        flags.append("invalid_resolution")
        quantum = 0.0
    variance = max(sigma * sigma, quantum * quantum / 12)
    # Token ripple is correlated work within decode, not a new phase. The
    # robust difference scale over lags through one exposure plus one sample
    # estimates its local envelope without assuming amplitude or TPS. Going
    # out to seconds on a slow sensor would confuse real phase changes with
    # nuisance noise. Supplied sd is read noise, not a zero-ripple assertion.
    lag = 1
    modulation_variance = 0.0
    normal_mad = math.sqrt(2) * statistics.NormalDist().inv_cdf(0.75)
    max_lag = max(1, min(math.isqrt(n), math.ceil(window / effective_interval) + 1))
    while lag <= max_lag:
        ds = [xs[i + lag] - xs[i] for i in range(n - lag)]
        if ds:
            median = statistics.median(ds)
            scale = statistics.median(abs(d - median) for d in ds) / normal_mad
            modulation_variance = max(modulation_variance, scale * scale)
            variance = max(variance, modulation_variance)
        lag *= 2
    center = statistics.fmean(xs)
    values = [x - center for x in xs]
    sums, squares = [0.0], [0.0]
    for value in values:
        sums.append(sums[-1] + value)
        squares.append(squares[-1] + value * value)

    def cost(left, right):
        size = right - left
        return max(0.0, squares[right] - squares[left] -
                   (sums[right] - sums[left]) ** 2 / size)

    penalty = 2 * variance * math.log(max(2, n))
    # One rounding ulp per observation bounds accumulation error, at the
    # accumulated squared signal itself; no arbitrary 1 W^2 floor.
    penalty = max(penalty, n * math.ulp(squares[-1]))
    pending, leaves = [(0, n)], []
    while pending:
        left, right = pending.pop()
        whole = cost(left, right)
        best_gain, best = penalty, None
        for split in range(left + 1, right):
            gain = whole - cost(left, split) - cost(split, right)
            if gain > best_gain:
                best_gain, best = gain, split
        if best is None:
            leaves.append((left, right))
        else:
            pending.extend(((left, best), (best, right)))
    leaves.sort()
    means = [(sums[b] - sums[a]) / (b - a) + center for a, b in leaves]
    # At a step, mixed exposure can occupy ceil(window/dt) observations.
    # These leaves cannot establish a sustained level; assign them using
    # temporal neighbors, retaining every sample in the final means.
    exposure_bins = max(1, math.ceil(window / effective_interval))
    stable = [i for i, (a, b) in enumerate(leaves) if b - a > exposure_bins]
    if not stable:
        stable = list(range(len(leaves)))
    order = sorted(stable, key=lambda i: means[i])
    groups = []
    # Complete-span grouping never chains idle through intermediate mixed
    # samples. The individual envelope includes correlated token modulation;
    # SE(mean) alone would split a decode ripple as read noise tends to zero.
    modulation_envelope = math.sqrt(2 * math.log(max(2, n)) * 2 * modulation_variance)
    for index in order:
        separation = modulation_envelope
        if groups:
            a, b = leaves[index]
            c, d = leaves[groups[-1][0]]
            separation = max(separation, math.sqrt(
                2 * math.log(max(2, n)) * variance * (1 / (b - a) + 1 / (d - c))))
        if not groups or means[index] - means[groups[-1][0]] > separation:
            groups.append([index])
        else:
            groups[-1].append(index)
    labels = ["unknown"] * len(leaves)
    if len(groups) >= 2:
        # Timeline ordering: idle < decode < prefill. Growing context can
        # create several sustained prefill levels.
        for i in groups[0]:
            labels[i] = "low"
        for i in groups[1]:
            labels[i] = "decode"
        for group in groups[2:]:
            for i in group:
                labels[i] = "prefill"
        decode_weight = sum(leaves[i][1] - leaves[i][0] for i in groups[1])
        decode_level = sum(means[i] * (leaves[i][1] - leaves[i][0]) for i in groups[1]) / decode_weight
        for i in range(len(leaves)):
            if i in stable:
                continue
            a, b = leaves[i]
            burst_separation = max(modulation_envelope, math.sqrt(
                2 * math.log(max(2, n)) * variance * (1 / (b - a) + 1 / decode_weight)))
            # A short prefill can have only one pure slow-sensor exposure.
            # It need not establish a new level, but a sample significantly
            # ABOVE sustained decode is a burst, never a low-power wait.
            if means[i] - decode_level > burst_separation:
                labels[i] = "prefill"
                continue
            left = next((j for j in reversed(stable) if j < i), None)
            right = next((j for j in stable if j > i), None)
            neighbors = [j for j in (left, right) if j is not None]
            # Nearest adjacent mean is the least-squares equal-variance choice.
            closest = min(neighbors or stable, key=lambda j: abs(means[j] - means[i]))
            labels[i] = labels[closest]
    else:
        flags.append("unidentified_single_level")
    result = []
    for (left, right), mean, label in zip(leaves, means, labels):
        start = times[left] - effective_interval
        end = times[right] - effective_interval if right < n else trace.t_ns[-1]
        local_flags = list(flags)
        boundary_uncertainty = 0
        for a, b in gaps:
            if a - effective_interval <= start <= b or a - effective_interval <= end <= b:
                boundary_uncertainty = max(boundary_uncertainty, b - a)
                local_flags.append("boundary_indeterminate_read_gap")
        segment = Segment(start, end, mean, label, trace.clock_domain,
                          effective_interval, window, tuple(sorted(set(local_flags))),
                          boundary_uncertainty)
        if result and result[-1].label == label:
            previous = result.pop()
            duration = max(0, previous.end_ns - previous.start_ns)
            added = max(0, end - start)
            mean = ((previous.mean_w * duration + mean * added) / (duration + added)
                    if duration + added else mean)
            segment = replace(
                segment, start_ns=previous.start_ns, mean_w=mean,
                flags=tuple(sorted(set(previous.flags) | set(segment.flags))),
                boundary_uncertainty_ns=max(previous.boundary_uncertainty_ns, boundary_uncertainty))
        result.append(segment)
    # Compare phase-run durations after consolidation; comparing individual
    # ripple leaves with a whole prefill would manufacture a model mismatch.
    decode_durations = [s.end_ns - s.start_ns for s in result if s.label == "decode"]
    prefill_durations = [s.end_ns - s.start_ns for s in result if s.label == "prefill"]
    if (decode_durations and prefill_durations and
            statistics.median(prefill_durations) > statistics.median(decode_durations)):
        result = [replace(s, flags=tuple(sorted(set(s.flags) |
                                               {"level_duration_model_mismatch"}))) for s in result]
    return [replace(s, label=("idle" if i in (0, len(result) - 1) else "tool_wait"))
            if s.label == "low" else s for i, s in enumerate(result)]


def match_tool_calls(segments: list[Segment], episode: Episode) -> ToolCallMatch:
    """Match detected troughs to idle runs implied by the visible log.

    A run includes contiguous calls and the client/serving gap up to the next
    logged generation activity. Every logged call in a matched run contributes
    to recall; power supplies no individual boundary inside that run. Precision
    counts matched troughs, not calls. A hidden call sharing a matched run is
    unidentifiable by this measurement and is not claimed as detected.
    """
    logged = [call for turn in episode.turns if turn.logged
              for call in turn.tool_calls if call.logged]
    flags = set(flag for segment in segments for flag in segment.flags)
    # Visible generation envelopes, subtracting visible in-turn tool waits.
    # No access to unlogged turn/call timing is used to construct idle runs.
    active = []
    for turn in episode.logged_turns():
        cursor = turn.start_ns
        for call in sorted(logged, key=lambda c: c.start_ns):
            left, right = max(turn.start_ns, call.start_ns), min(turn.end_ns, call.end_ns)
            if right <= left:
                continue
            if left > cursor:
                active.append((cursor, left))
            cursor = max(cursor, right)
        if cursor < turn.end_ns:
            active.append((cursor, turn.end_ns))
    active.sort()
    runs = {}
    for index, call in enumerate(logged):
        left = max([episode.start_ns] + [b for a, b in active if b <= call.start_ns])
        right = min([episode.end_ns] + [a for a, b in active if a >= call.end_ns])
        if any(a < call.end_ns and b > call.start_ns for a, b in active):
            flags.add("tool_call_overlaps_logged_generation")
            left, right = call.start_ns, call.end_ns
        runs.setdefault((left, right), []).append(index)
    run_items = sorted(runs.items())
    if any(len(indices) > 1 for _, indices in run_items):
        flags.add("back_to_back_calls_temporally_unresolved")
    candidates = [s for s in segments if s.label == "tool_wait"]
    # A final call can merge with the idle tail. Include such an edge only
    # when a visible call overlaps it; generic head/tail idle is not a tool.
    for s in segments:
        if s.label != "idle":
            continue
        if s.clock_domain in ("", episode.clock_domain) and any(
                s.start_ns < c.end_ns and s.end_ns > c.start_ns for c in logged):
            candidates.append(s)
    transformed, indeterminate = [], []
    tolerance = 0
    for segment in candidates:
        domain = segment.clock_domain or episode.clock_domain
        offset, uncertainty = 0, 0
        if domain != episode.clock_domain:
            mappings = [m for m in episode.clock_mappings if
                        m.trace_domain == domain and m.episode_domain == episode.clock_domain]
            if len(mappings) != 1:
                flags.add("clock_mapping_unavailable_or_ambiguous")
                indeterminate.append(segment)
                continue
            offset, uncertainty = mappings[0].offset_ns, mappings[0].uncertainty_ns
            if uncertainty < 0:
                flags.add("invalid_clock_uncertainty")
                indeterminate.append(segment)
                continue
        bound = (segment.sample_interval_ns + segment.averaging_window_ns +
                 uncertainty + segment.boundary_uncertainty_ns)
        tolerance = max(tolerance, bound)
        transformed.append((replace(segment, start_ns=segment.start_ns + offset,
                                    end_ns=segment.end_ns + offset,
                                    clock_domain=episode.clock_domain), bound))
    edges = [[j for j, ((left, right), _) in enumerate(run_items)
              if abs(segment.start_ns - left) <= bound and
              abs(segment.end_ns - right) <= bound]
             for segment, bound in transformed]
    owner = {}

    def augment(i, visited):
        for j in edges[i]:
            if j in visited:
                continue
            visited.add(j)
            if j not in owner or augment(owner[j], visited):
                owner[j] = i
                return True
        return False

    for i in range(len(transformed)):
        augment(i, set())
    matched_segments = set(owner.values())
    matched_calls = {index for j in owner for index in run_items[j][1]}
    unlogged = []
    for i, (segment, _) in enumerate(transformed):
        if i in matched_segments:
            continue
        if segment.boundary_uncertainty_ns:
            indeterminate.append(segment)
            flags.add("tool_wait_indeterminate_read_gap")
        else:
            unlogged.append(segment)
    if not logged:
        flags.add("recall_undefined_no_logged_calls")
    usable_candidates = len(candidates) - len(indeterminate)
    if not usable_candidates:
        flags.add("precision_undefined_no_candidates")
    count = len(matched_calls)
    recall = count / len(logged) if logged else 1.0
    precision = len(matched_segments) / usable_candidates if usable_candidates else 1.0
    return ToolCallMatch(
        recall, precision, tuple(c for j, c in enumerate(logged) if j not in matched_calls),
        tuple(unlogged), tuple(sorted(flags)), count, tolerance, tuple(indeterminate))
