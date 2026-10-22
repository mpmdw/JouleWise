"""Noise-penalized binary segmentation of power, without access to agent logs.

Binary segmentation costs O(n log n) for balanced changes and uses O(n) storage;
it is practical for sub-ms traces without a quadratic dynamic-programming
table. Its greedy splits can miss short balanced troughs; sensitivity must be
reported by sensor/duration rather than presumed. Labels use local prefill peaks
followed by lower decode, with near-idle troughs; decode may rise with context.
Read gaps widen boundary uncertainty. Held values are thinned by observed
cadence; robust multiscale variance retains within-decode token modulation.
"""

from __future__ import annotations

import math
import statistics
from dataclasses import dataclass, replace

from joulewise.align.records import Episode, PowerTrace, ToolCall
from joulewise.align.sensor_sim import _held_change_indices, _mean_period_ns


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
    low_observation_windows: tuple[tuple[int, int, float], ...] = ()
    observation_uncertainty_ns: int = 0
    idle_floor_w: float | None = None
    active_floor_w: float | None = None
    power_uncertainty_w: float = 0.0


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
    Remove repeats only with evidence of a multi-poll conversion stream.
    Otherwise, constant quantized plateaus carry real low-variance evidence.
    """
    if len(values) < 2:
        return 0.0
    changes = _held_change_indices(values)
    observed = [values[0]] + [values[i] for i in changes] if changes else values
    differences = [b - a for a, b in zip(observed, observed[1:])]
    center = statistics.median(differences)
    mad = statistics.median(abs(x - center) for x in differences)
    scale = mad / (math.sqrt(2) * statistics.NormalDist().inv_cdf(0.75))
    if scale == 0.0:
        # Quantized independent noise can occupy one bin for >half the
        # differences. Exact out-and-back excursions identify an observed
        # small step without mistaking a one-way phase transition for noise.
        # Uniform rounding in that bin has sd q/sqrt(12). This is an
        # observable resolution floor, not a calibrated analog-noise estimate.
        excursions = [abs(b - a) for a, b, c in zip(observed, observed[1:], observed[2:])
                      if a == c and b != a]
        if excursions:
            scale = min(excursions) / math.sqrt(12)
    return scale


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
    # Infer cadence only from conversion-like multi-poll runs, not from
    # constant quantized phases. The same evidence rule governs noise MAD.
    changes = _held_change_indices(trace.values)
    effective_interval = interval
    if changes:
        change_times = [trace.t_ns[i] for i in changes]
        observed_periods = [b - a for a, b in zip(change_times, change_times[1:])]
        effective_interval = max(interval, math.ceil(_mean_period_ns(observed_periods)))
        flags.append("held_values_cadence_inferred")
        # Held conversion latency also supplies an inferred exposure when
        # the trace has no narrower physical characterization.
        window = max(window, effective_interval)
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
    # A lag needs two observations; the exposure duration supplies the other
    # cap. No sample-count square-root cap is physically justified.
    max_lag = max(1, min(n - 1, math.ceil(window / effective_interval) + 1))
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
    # For Gaussian level errors with difference variance v, the tail bound
    # exp(-d^2/(2v)) <= 1/n gives d=sqrt(2*v*log(n)). For independent
    # means v=variance*(1/n1+1/n2); for local modulation use two readings.
    # Two rounded values each have +/-q/2 ambiguity, so their separation
    # must also exceed one whole quantum. Add that bounded rounding error
    # to the statistical mean-error term by the triangle inequality; it
    # cannot average away without demonstrated dithering. This survives zero ripple.
    modulation_envelope = max(quantum, math.sqrt(
        2 * math.log(max(2, n)) * 2 * modulation_variance))
    for index in order:
        separation = modulation_envelope
        if groups:
            a, b = leaves[index]
            c, d = leaves[groups[-1][0]]
            separation = max(separation, quantum + math.sqrt(
                2 * math.log(max(2, n)) * variance * (1 / (b - a) + 1 / (d - c))))
        if not groups or means[index] - means[groups[-1][0]] > (
                separation + math.ulp(means[index]) + math.ulp(means[groups[-1][0]])):
            groups.append([index])
        else:
            groups[-1].append(index)
    low = []
    labels = ["unknown"] * len(leaves)
    if len(groups) >= 2:
        rank = {i: k for k, group in enumerate(groups) for i in group}
        # Consolidate sustained equal levels temporally. Global rank does
        # not identify decode: waits can sit above idle and KV growth can
        # give each decode its own level. A prefill is a local high burst;
        # the sustained level immediately after its fall is decode.
        anchors = []
        for i in stable:
            if anchors and rank[anchors[-1][-1]] == rank[i]:
                anchors[-1].append(i)
            else:
                anchors.append([i])

        def separation(i, j):
            a, b = leaves[i]
            c, d = leaves[j]
            return max(modulation_envelope, quantum + math.sqrt(
                2 * math.log(max(2, n)) * variance * (1 / (b - a) + 1 / (d - c))))

        peaks, following_bursts = set(), set()
        for k, anchor in enumerate(anchors):
            i = anchor[0]
            before = anchors[k - 1][-1] if k else None
            after = anchors[k + 1][0] if k + 1 < len(anchors) else None
            # A prefill shorter than one exposure can be an unstable leaf
            # before a sustained decode. It must not turn that decode into
            # the highest sustained level of the cycle.
            previous_end = before + 1 if before is not None else 0
            short_burst = any(means[j] - means[i] > separation(j, i) and
                              (before is None or means[j] - means[before] > separation(j, before))
                              for j in range(previous_end, i))
            if short_burst:
                following_bursts.add(k)
            if (not short_burst and after is not None and
                    rank[i] > rank[after] and
                    (before is None or rank[i] > rank[before])):
                peaks.add(k)
        # A decode following one observed burst can be a local maximum
        # when another prefill falls entirely between sensor slices. Do not
        # let that one unresolved burst promote its following wait to the
        # episode-wide decode level. Established peak/fall roles outrank
        # local height alone.
        post_peak_ranks = {rank[anchors[k + 1][0]] for k in peaks}
        peaks = {k for k in peaks if rank[anchors[k][0]] not in post_peak_ranks}
        # Equal low head/tail levels establish the timeline's idle floor.
        # A single short edge excursion cannot promote that known floor to
        # decode across the episode. Cropped active-only traces have unlike
        # edge levels and therefore do not acquire this idle constraint.
        edge_idle_ranks = ({rank[anchors[0][0]]} if
                           rank[anchors[0][0]] == rank[anchors[-1][0]] and
                           0 not in peaks else set())
        decode_anchors = {k for k in following_bursts
                          if rank[anchors[k][0]] not in edge_idle_ranks}
        for k in peaks:
            following = k + 1
            # A low head and equal-level tail establish idle. In a trace
            # cropped to active work, the last post-prefill level is decode.
            edge_idle = (following == len(anchors) - 1 and
                         rank[anchors[0][0]] == rank[anchors[following][0]] and
                         0 not in peaks)
            if not edge_idle and rank[anchors[following][0]] not in edge_idle_ranks:
                decode_anchors.add(following)
        if not decode_anchors:
            # Too little temporal structure for peak/fall identification:
            # retain the original ordered-level hypothesis and flag its
            # duration check below (including deliberately inverted worlds).
            for i in groups[0]:
                labels[i] = "low"
            for i in groups[1]:
                labels[i] = "decode"
            for group in groups[2:]:
                for i in group:
                    labels[i] = "prefill"
        else:
            decode_ranks = {rank[i] for k in decode_anchors for i in anchors[k]}
            for k, anchor in enumerate(anchors):
                i = anchor[0]
                nearest_decode = min((anchors[j][0] for j in decode_anchors),
                                     key=lambda j: abs(means[i] - means[j]))
                above_decode = means[i] - means[nearest_decode] > separation(i, nearest_decode)
                label = ("decode" if k in decode_anchors or rank[i] in decode_ranks else
                         "prefill" if k in peaks or above_decode else "low")
                for i in anchor:
                    labels[i] = label
        low = [i for i in stable if labels[i] == "low"]
        decode = [i for i in stable if labels[i] == "decode"]
        for i in range(len(leaves)):
            if i in rank:
                continue
            # Nearest established low/decode level is the equal-variance
            # least-squares decision. Only established lows can create a
            # short trough; an active-only two-level trace has none.
            low_distance = min((abs(means[i] - means[j]) for j in low), default=math.inf)
            decode_distance = min((abs(means[i] - means[j]) for j in decode), default=math.inf)
            if low_distance < decode_distance:
                labels[i] = "low"
                continue
            if decode:
                j = min(decode, key=lambda j: abs(means[j] - means[i]))
                if means[i] - means[j] > separation(i, j):
                    labels[i] = "prefill"
                    continue
            left = next((j for j in reversed(stable) if j < i), None)
            right = next((j for j in stable if j > i), None)
            neighbors = [j for j in (left, right) if j is not None]
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
        # Retain low-segment exposures to test whether an empty visible gap
        # can explain their convolution. Even a partial-window trough can
        # refute a short client gap; it need not be a pure-idle observation.
        # Two independent level errors have variance <=2*variance; the
        # Gaussian tail <=1/n and bounded rounding derive the power bar.
        low_bar = quantum + math.sqrt(4 * variance * math.log(max(2, n)))
        observations = tuple((times[k] - window, times[k], xs[k]) for k in range(left, right)
                             if low and label == "low")
        observation_uncertainty = boundary_uncertainty + (effective_interval if changes else 0)
        idle_floor = min((means[j] for j in low), default=None)
        active_floor = min((means[j] for j in decode), default=None) if len(groups) >= 2 else None
        segment = Segment(start, end, mean, label, trace.clock_domain,
                          effective_interval, window, tuple(sorted(set(local_flags))),
                          boundary_uncertainty, observations, observation_uncertainty,
                          idle_floor, active_floor, low_bar)
        if result and result[-1].label == label:
            previous = result.pop()
            duration = max(0, previous.end_ns - previous.start_ns)
            added = max(0, end - start)
            mean = ((previous.mean_w * duration + mean * added) / (duration + added)
                    if duration + added else mean)
            segment = replace(
                segment, start_ns=previous.start_ns, mean_w=mean,
                flags=tuple(sorted(set(previous.flags) | set(segment.flags))),
                boundary_uncertainty_ns=max(previous.boundary_uncertainty_ns, boundary_uncertainty),
                low_observation_windows=previous.low_observation_windows + observations,
                observation_uncertainty_ns=max(previous.observation_uncertainty_ns,
                                               observation_uncertainty))
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
    # Every complement of the visible generation union is explained idle,
    # including ordinary client latency after a turn with no tool calls.
    # A trough in such a gap supplies no evidence beyond the log's timestamps.
    merged = []
    for left, right in active:
        if merged and left <= merged[-1][1]:
            merged[-1] = (merged[-1][0], max(right, merged[-1][1]))
        else:
            merged.append((left, right))
    runs = {}
    cursor = episode.start_ns
    for left, right in merged:
        if cursor < left:
            runs[(cursor, left)] = []
        cursor = max(cursor, right)
    if cursor < episode.end_ns:
        runs[(cursor, episode.end_ns)] = []
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
        offset = 0
        if s.clock_domain not in ("", episode.clock_domain):
            mappings = [m for m in episode.clock_mappings if
                        m.trace_domain == s.clock_domain and m.episode_domain == episode.clock_domain]
            if len(mappings) != 1 or mappings[0].uncertainty_ns < 0:
                continue
            offset = mappings[0].offset_ns
        if any(s.start_ns + offset < c.end_ns and s.end_ns + offset > c.start_ns for c in logged):
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
                                    clock_domain=episode.clock_domain,
                                    low_observation_windows=tuple((a + offset, b + offset, value)
                                        for a, b, value in segment.low_observation_windows),
                                    observation_uncertainty_ns=segment.observation_uncertainty_ns +
                                        uncertainty), bound))
    def gap_explains_observations(segment, left, right):
        if segment.idle_floor_w is None or segment.active_floor_w is None:
            return True  # No amplitude evidence; retain timing uncertainty.
        uncertainty = segment.observation_uncertainty_ns
        left, right = left - uncertainty, right + uncertainty
        # Partial edge exposures do not determine instantaneous decode power:
        # token ripple can vanish in full windows and survive partial ones.
        # Use only exposures compatible with the established idle level.
        # Their whole averaging window must fit an explained empty gap.
        # Disjoint level-error intervals are needed to identify a pure low.
        if segment.active_floor_w - segment.idle_floor_w <= 2 * segment.power_uncertainty_w:
            return True
        for a, b, value in segment.low_observation_windows:
            if (abs(value - segment.idle_floor_w) <= segment.power_uncertainty_w and
                    (a < left or b > right)):
                return False
        return True

    edges = [[j for j, ((left, right), calls) in enumerate(run_items)
              if abs(segment.start_ns - left) <= bound and
              abs(segment.end_ns - right) <= bound and
              (calls or gap_explains_observations(segment, left, right))]
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
    # An unmatched visible call whose envelope remains at the sustained
    # decode level has no separable trough. Name the observational failure
    # specifically; level alone cannot distinguish a wait equal to decode.
    for j, call in enumerate(logged):
        if j not in matched_calls and any(
                s.label == "decode" and
                s.start_ns + next((m.offset_ns for m in episode.clock_mappings
                                  if m.trace_domain == s.clock_domain and
                                  m.episode_domain == episode.clock_domain), 0) < call.end_ns and
                s.end_ns + next((m.offset_ns for m in episode.clock_mappings
                                if m.trace_domain == s.clock_domain and
                                m.episode_domain == episode.clock_domain), 0) > call.start_ns
                for s in segments):
            flags.add("tool_wait_not_separated_from_decode_level")
    unlogged = []
    for i, (segment, _) in enumerate(transformed):
        if i in matched_segments:
            continue
        if segment.boundary_uncertainty_ns:
            indeterminate.append(segment)
            flags.add("tool_wait_indeterminate_read_gap")
        elif segment.label == "idle":
            # Edge-low runs were admitted only because a visible call overlaps
            # them. A trace cut inside that run has an unobserved endpoint;
            # failing its full-run timing test is not evidence of a hidden call.
            indeterminate.append(replace(
                segment, flags=tuple(sorted(set(segment.flags) |
                                            {"boundary_indeterminate_trace_edge"}))))
            flags.add("tool_wait_indeterminate_trace_edge")
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
