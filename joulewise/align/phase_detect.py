"""Noise-penalized binary segmentation of power, without access to agent logs.

Binary segmentation costs O(n log n) for balanced changes and uses O(n) storage;
it is practical for sub-ms traces without a quadratic dynamic-programming
table. Its greedy splits can miss short balanced troughs; sensitivity must be
reported by sensor/duration rather than presumed. Labels assume idle < decode
< prefill and shorter prefill bursts, as in the synthetic timeline model.
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


@dataclass(frozen=True)
class ToolCallMatch:
    recall: float
    precision: float
    unmatched_logged: tuple[ToolCall, ...]
    unlogged_candidates: tuple[Segment, ...]
    flags: tuple[str, ...] = ()
    matched_count: int = 0
    tolerance_ns: int = 0


def estimate_noise_sd(values: tuple[float, ...]) -> float:
    """MAD of first differences / (sqrt(2) * Phi^-1(0.75)).

    Gaussian independent read noise differences have sd sqrt(2)*sigma.
    The Gaussian MAD consistency factor is Phi^-1(0.75), computed by stdlib.
    Sparse phase boundaries are robust outliers; ripple/correlation can bias
    this estimator, which is a limitation, not a hardware noise calibration.
    """
    if len(values) < 2:
        return 0.0
    differences = [b - a for a, b in zip(values, values[1:])]
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
    if any(b - a > interval for a, b in zip(trace.t_ns, trace.t_ns[1:])):
        flags.append("sample_gaps")
    sigma = estimate_noise_sd(trace.values) if noise_sd_w is None else noise_sd_w
    if noise_sd_w is None:
        flags.append("noise_estimated_from_differences")
    quantum = trace.resolution or 0.0
    if quantum < 0 or not math.isfinite(quantum):
        flags.append("invalid_resolution")
        quantum = 0.0
    variance = max(sigma * sigma, quantum * quantum / 12)
    # Center before prefix sums to reduce cancellation of a large idle floor.
    center = statistics.mean(trace.values)
    values = [x - center for x in trace.values]
    sums, squares = [0.0], [0.0]
    for value in values:
        sums.append(sums[-1] + value)
        squares.append(squares[-1] + value * value)

    def cost(left, right):
        size = right - left
        return max(0.0, squares[right] - squares[left] -
                   (sums[right] - sums[left]) ** 2 / size)

    penalty = 2 * variance * math.log(max(2, n))
    # With truly noiseless input, SSE cancellation is bounded by accumulated
    # squared-value ulps. This numerical floor prevents fictitious changes.
    penalty = max(penalty, n * math.ulp(max(squares[-1], 1.0)))
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
    # Distinct levels must clear the universal Gaussian noise excursion bound,
    # sqrt(2 log n), applied to the standard error of two segment means.
    order = sorted(range(len(leaves)), key=lambda i: means[i])
    groups = []
    for index in order:
        if not groups:
            groups.append([index])
            continue
        previous = groups[-1][-1]
        a, b = leaves[index]
        c, d = leaves[previous]
        separation = math.sqrt(2 * math.log(max(2, n)) * variance *
                               (1 / (b - a) + 1 / (d - c)))
        if means[index] - means[previous] > separation:
            groups.append([index])
        else:
            groups[-1].append(index)
    labels = ["unknown"] * len(leaves)
    if len(groups) >= 2:
        for i in groups[0]:
            labels[i] = "idle" if i in (0, len(leaves) - 1) else "tool_wait"
        for group in groups[1:]:
            for i in group:
                labels[i] = "decode"
        if len(groups) >= 3:
            def duration(group):
                return statistics.median(leaves[i][1] - leaves[i][0] for i in group)

            # Decode is the longest sustained nonidle level in the timeline.
            # Growing context can create several distinct prefill levels;
            # classify every higher/shorter group, not only the highest one.
            decode_group = max(groups[1:], key=duration)
            decode_level = statistics.mean(means[i] for i in decode_group)
            for group in groups[1:]:
                if statistics.mean(means[i] for i in group) > decode_level:
                    if duration(group) < duration(decode_group):
                        for i in group:
                            labels[i] = "prefill"
                    else:
                        flags.append("level_duration_model_mismatch")
            if "prefill" not in labels:
                flags.append("level_duration_model_mismatch")
    else:
        flags.append("unidentified_single_level")
    if len(groups) > 3:
        flags.append("more_than_three_power_levels")
    result = []
    for (left, right), mean, label in zip(leaves, means, labels):
        # Each end-stamped reading represents the preceding sampling bin.
        start = trace.t_ns[left] - interval
        end = trace.t_ns[right] - interval if right < n else trace.t_ns[-1]
        result.append(Segment(start, end, mean, label, trace.clock_domain,
                              interval, window, tuple(flags)))
    return result


def match_tool_calls(segments: list[Segment], episode: Episode) -> ToolCallMatch:
    """One-to-one maximum-cardinality boundary matching after clock mapping.

    Tolerance is dt + averaging window + clock-offset half-width. Both start
    and end must match, so a broad trough cannot absorb several logged calls.
    Unmatched candidates can be idle for reasons other than a tool call.
    """
    candidates = [s for s in segments if s.label == "tool_wait"]
    logged = [call for turn in episode.turns if turn.logged
              for call in turn.tool_calls if call.logged]
    flags = set(flag for segment in segments for flag in segment.flags)
    transformed = []
    tolerance = 0
    unmappable = []
    for segment in candidates:
        domain = segment.clock_domain or episode.clock_domain
        offset, uncertainty = 0, 0
        if domain != episode.clock_domain:
            mappings = [m for m in episode.clock_mappings if
                        m.trace_domain == domain and m.episode_domain == episode.clock_domain]
            if len(mappings) != 1:
                flags.add("clock_mapping_unavailable_or_ambiguous")
                unmappable.append(segment)
                continue
            offset, uncertainty = mappings[0].offset_ns, mappings[0].uncertainty_ns
            if uncertainty < 0:
                flags.add("invalid_clock_uncertainty")
                unmappable.append(segment)
                continue
        bound = segment.sample_interval_ns + segment.averaging_window_ns + uncertainty
        tolerance = max(tolerance, bound)
        transformed.append((replace(segment, start_ns=segment.start_ns + offset,
                                    end_ns=segment.end_ns + offset,
                                    clock_domain=episode.clock_domain), bound))
    edges = [[j for j, call in enumerate(logged)
              if abs(segment.start_ns - call.start_ns) <= bound and
              abs(segment.end_ns - call.end_ns) <= bound]
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
    matched = set(owner.values())
    count = len(owner)
    if not logged:
        flags.add("recall_undefined_no_logged_calls")
    if not candidates:
        flags.add("precision_undefined_no_candidates")
    # Vacuous empty-set rates are 1, always accompanied by explicit flags.
    recall = count / len(logged) if logged else 1.0
    precision = count / len(candidates) if candidates else 1.0
    return ToolCallMatch(
        recall, precision, tuple(c for j, c in enumerate(logged) if j not in owner),
        tuple(s for i, (s, _) in enumerate(transformed) if i not in matched) + tuple(unmappable),
        tuple(sorted(flags)), count, tolerance)
