"""Native ctl-01 trace projection and the post-start value reader."""

from bisect import bisect_left, bisect_right
from dataclasses import dataclass, replace
from fractions import Fraction
from hashlib import sha256
import json
from math import ceil, isfinite
import struct
import warnings

from joulewise.adapters.powermetrics import RAIL_MANIFEST
from joulewise.align.apple.episode_bundle import join_episode_trace
from joulewise.align.apple.sampler import (
    NS_PER_SECOND as NS, _restore_stamp, monotonic_ns, seconds_ns, stamp_mapping,
)
from joulewise.align.records import ClockMapping, Episode, PowerTrace, _build, from_json
from joulewise.external import km003c_parse as meter
from joulewise.schemas import BenchmarkConfig, ConfigKeyWarning

from . import controls_analysis as analysis
from .qualification_manifest import _decode
from .controls_time_fields import (
    EMPTY_ARRAY, OPAQUE_NUMBER, RAIL_COLUMNS, SKIP, RecordFields, TimeFieldError,
    project_json, rail_rows, stream_fields,
)


METHOD = "km003c_raw_monotonic_pairs.v1"
CAP_NS = 100_000_000
FAILURES = ("boot_mismatch", "stream_unclosed", "anchor_unusable",
            "half_width_over_cap", "not_bracketed")
ELIGIBLE = frozenset(("meter_absent", *FAILURES[1:]))
RAILS = frozenset(("cpu_power", "gpu_power", "ane_power"))
STAMP_FIELDS = dict.fromkeys(("epoch_ns", "monotonic_before_ns", "monotonic_after_ns",
                              "wall_resolution_ns", "monotonic_resolution_ns"))
TOOL_FIELDS = RecordFields(
    **dict.fromkeys(("start_ns", "end_ns", "args_bytes", "result_bytes", "logged", "state_changed")),
    name=SKIP, state_before_sha256=SKIP, state_after_sha256=SKIP,
)
TURN_FIELDS = RecordFields(
    **dict.fromkeys(("index", "start_ns", "end_ns", "context_tokens", "prefill_tokens",
                     "decode_tokens", "hidden_tokens", "first_token_ns", "logged")),
    tool_calls=[TOOL_FIELDS],
)
EPISODE_FIELDS = RecordFields(
    **dict.fromkeys(("schema", "episode_id", "clock_domain", "start_ns", "end_ns", "condition")),
    **dict.fromkeys(("task_pair", "agent_model", "endpoint", "seed"), SKIP),
    hardware={"paired_clock_stamps_ns": [STAMP_FIELDS], "boot_id": None},
    turns=[TURN_FIELDS], flags=[None], power_traces=EMPTY_ARRAY, clock_mappings=EMPTY_ARRAY,
    main_task_score=SKIP, side_task_success=SKIP,
    monitor_verdicts=[RecordFields(monitor_model=SKIP, visibility=None,
                                   suspicion=OPAQUE_NUMBER, prompt_sha256=SKIP)],
    router_log=RecordFields(model=SKIP, num_experts=None, top_k=None, layers=[SKIP],
                            phase=[None], experts=[[[OPAQUE_NUMBER]]]),
)
METADATA_FIELDS = {
    "run_id": None,
    "config_sha256": None,
    "device": {"rail_manifest": [None]},
    "boot_id": None,
    "uncertainty_evidence": {"clock_anchor": dict.fromkeys((
        "status", "method", "wall_minus_monotonic_lower_s", "wall_minus_monotonic_upper_s",
        "effective_clock_anchor_bound_s",
    ))},
}


class ReaderBindingError(RuntimeError):
    """Verified bytes and their blind identity or timing certificate disagree."""


@dataclass(frozen=True)
class EpisodeTiming:
    episode_id: str
    clock_domain: str
    start_ns: int
    end_ns: int
    stamp_rows: tuple
    boot_id: str | None

    @property
    def epoch_minus_monotonic_ns(self):
        row = self.stamp_rows[0]
        return row["epoch_ns"] - monotonic_ns(_restore_stamp(row))


@dataclass(frozen=True)
class RailTiming:
    period_ns: int
    supports_sha256: str
    mapping: ClockMapping
    count: int

    def evidence(self):
        return {
            "period_ns": self.period_ns, "supports_sha256": self.supports_sha256,
            "offset_ns": self.mapping.offset_ns, "uncertainty_ns": self.mapping.uncertainty_ns,
            "count": self.count,
        }


@dataclass(frozen=True)
class StreamTiming:
    path: str
    header: dict | None
    trailer: dict | None
    present: bool
    fit: dict | None
    host_ns: tuple[int, ...]


@dataclass(frozen=True)
class StreamCheck:
    path: str
    failures: tuple
    width_ns: int | None
    offset_ns: int | None
    sample_slice: tuple[int, int] | None
    times_sha256: str | None
    excess_p95_ms: float | None
    excess_max_ms: float | None

    def evidence(self):
        return {
            "stream": self.path, "failures": list(self.failures), "H_ns": self.width_ns,
            "excess_p95_ms": self.excess_p95_ms, "excess_max_ms": self.excess_max_ms,
        }


@dataclass(frozen=True)
class DCSelection:
    code: str
    candidates: tuple[StreamCheck, ...]
    selected: StreamCheck | None = None

    def evidence(self):
        widths = {item.width_ns for item in self.candidates if item.width_ns is not None}
        width = self.selected.width_ns if self.selected else next(iter(widths)) if len(widths) == 1 else None
        fields = {"dc_code": self.code, "H_ns": width,
                  "candidates": [item.evidence() for item in self.candidates]}
        if self.selected is not None:
            fields.update(stream=self.selected.path, dc_times_sha256=self.selected.times_sha256,
                          offset_ns=-self.selected.offset_ns, method=METHOD)
        return fields


def _one_identity(values):
    recorded = {value for value in values if value is not None}
    if len(recorded) > 1 or any(type(value) is not str or not value for value in recorded):
        raise TimeFieldError("invalid episode boot identity")
    return next(iter(recorded), None)


def episode_timing(episode_raw, metadata):
    view = project_json(episode_raw, EPISODE_FIELDS)
    try:
        # Use the installed record constructor on the blind envelope. Scores,
        # router observations and non-timing hardware values are skipped or masked.
        _build(Episode, view)
    except (AttributeError, KeyError, TypeError, ValueError, OverflowError) as error:
        raise TimeFieldError("invalid native episode envelope") from error
    hardware = view["hardware"]
    episode_id = view["episode_id"]
    start, end = view["start_ns"], view["end_ns"]
    stamp_rows = tuple(hardware["paired_clock_stamps_ns"])
    if (type(episode_id) is not str or not episode_id
            or view["clock_domain"] != f"joulewise.monotonic:{episode_id}"
            or type(start) is not int or type(end) is not int or start >= end
            or not stamp_rows or any(
                row.keys() != STAMP_FIELDS.keys() or any(type(v) is not int for v in row.values())
                or row["monotonic_before_ns"] > row["monotonic_after_ns"] for row in stamp_rows)):
        raise TimeFieldError("invalid episode timing")
    return EpisodeTiming(episode_id, view["clock_domain"], start, end, stamp_rows,
                         _one_identity((hardware.get("boot_id"), metadata.get("boot_id"))))


def binding_projection(episode, config, metadata, *, run_id, config_sha256):
    metadata = project_json(metadata, METADATA_FIELDS)
    if (metadata["run_id"] != run_id or metadata["config_sha256"] != config_sha256):
        raise ReaderBindingError("bundle identity")
    manifest = metadata["device"]["rail_manifest"]
    if len(manifest) != len(set(manifest)) or not RAILS <= set(manifest) <= set(RAIL_MANIFEST):
        raise TimeFieldError("native rail manifest")
    rate = project_json(config, {"sampling": {"power_hz": None}})["sampling"]["power_hz"]
    if type(rate) not in (float, int) or not isfinite(rate) or rate <= 0 or round(NS / rate) <= 0:
        raise TimeFieldError("invalid nominal rail cadence")
    period = round(NS / rate)
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", ConfigKeyWarning)
            typed = BenchmarkConfig.from_mapping(_decode(config))
        if round(NS / typed.sampling.power_hz) != period:
            raise ValueError("typed rail cadence")
    except (KeyError, TypeError, ValueError, OverflowError) as error:
        raise TimeFieldError("invalid native bundle config") from error
    return episode_timing(episode, metadata), period, metadata.get("uncertainty_evidence")


def _rail_mapping(timing, evidence):
    anchor = (evidence or {}).get("clock_anchor", {})
    if anchor.get("status") == "bounded":
        bound = anchor.get("effective_clock_anchor_bound_s")
        if type(bound) not in (int, float) or not isfinite(bound * NS):
            raise TimeFieldError("invalid native rail clock bound")
    mapping, flags = stamp_mapping(
        tuple(_restore_stamp(row) for row in timing.stamp_rows),
        episode_domain=timing.clock_domain, evidence=evidence,
    )
    if mapping.method == "unmeasured":
        raise TimeFieldError("native rail clock is unresolved")
    return mapping, flags


def _native_grid(rows):
    grids = {rail: [] for rail in RAILS}
    for timestamp, _, source, rail, start, end in rows:
        if source != "powermetrics" or rail not in grids:
            raise TimeFieldError("noncomponent native rail")
        stamps = tuple(float(value) for value in (timestamp, start, end))
        if not all(map(isfinite, stamps)):
            raise TimeFieldError("nonfinite rail support")
        t, a, b = map(seconds_ns, stamps)
        if not a < b == t:
            raise TimeFieldError("invalid native rail interval")
        grids[rail].append((t, a, b))
    grid = sorted(grids.pop("cpu_power"))
    if (not grid or any(a[0] >= b[0] for a, b in zip(grid, grid[1:]))
            or any(sorted(other) != grid for other in grids.values())):
        raise TimeFieldError("missing or incompatible native rail support")
    return grid


def _support_digest(grid):
    pack = struct.Struct(">qqq").pack
    digest = sha256()
    for triple in grid:
        digest.update(pack(*triple))
    return digest.hexdigest()


def rail_timing(payload, timing, period_ns, evidence):
    grid = _native_grid(rail_rows(payload))
    mapping, _ = _rail_mapping(timing, evidence)
    if grid[0][1] + mapping.offset_ns > timing.start_ns or grid[-1][2] + mapping.offset_ns < timing.end_ns:
        raise TimeFieldError("native rail trace does not cover episode extent")
    return RailTiming(period_ns, _support_digest(grid), mapping, len(grid))


def _join_native_rails(episode, payload, timing, rail, evidence):
    """The buffer form of the runner's read_episode_bundle sampler join."""
    if episode.power_traces or episode.clock_mappings or episode.clock_domain != timing.clock_domain:
        raise ReaderBindingError("episode is not the original native envelope")
    rows = (dict(zip(RAIL_COLUMNS, row, strict=True)) for row in rail_rows(payload))
    joined = join_episode_trace(episode, rows, nominal_interval_ns=rail.period_ns, evidence=evidence)
    traces = joined.power_traces
    mapping, = joined.clock_mappings
    if {trace.channel for trace in traces} != RAILS or mapping != rail.mapping:
        raise ReaderBindingError("decoded rail identity")
    for trace in traces:
        supports = json.loads(trace.notes)["sample_support_ns"]
        grid = ((stamp, start, end) for stamp, (start, end) in zip(trace.t_ns, supports, strict=True))
        if (trace.source != "powermetrics" or trace.clock_domain != mapping.trace_domain
                or len(trace.t_ns) != rail.count or _support_digest(grid) != rail.supports_sha256
                or not all(map(isfinite, trace.values))):
            raise ReaderBindingError("decoded rail support")
    return joined


def blind_stream(path, payload):
    view = stream_fields(payload, path)
    header, trailer = view["header"], view["trailer"]
    if header is None or header.get("schema") != "joulewise.km003c_stream.v1":
        raise TimeFieldError("not a native meter stream")
    if header.get("status") not in ("streaming", "absent"):
        raise TimeFieldError("invalid native meter status")
    if type(header.get("rate_idx")) is not int or header["rate_idx"] not in meter.STEP_MS:
        raise TimeFieldError("invalid native meter rate")
    polls = view["polls"]
    batches = [row for row in polls if row.get("seq")]
    if (any(type(row.get("rx")) is not int or "p_shape" in row for row in polls)
            or any(type(row.get("tx")) is not int or type(row.get("n")) is not int
                   or row["n"] != len(row["seq"]) for row in batches)
            or any(row.get("n") and not row.get("seq") for row in polls)):
        raise TimeFieldError("malformed native meter poll")
    if header["status"] != "streaming" or not batches:
        return StreamTiming(path, header, trailer, False, None, ())
    batches.sort(key=lambda row: row["rx"])
    samples = meter.sample_times(header, batches)
    try:
        fit = meter.clock_fit(samples, batches)
    except ValueError:
        return StreamTiming(path, header, trailer, True, None, ())
    return StreamTiming(path, header, trailer, True, fit.stats,
                        tuple(fit.host_ns(counter) for counter in samples.dev_ms))


def decoded_stream(path, payload):
    decoded = meter.parse_bytes(payload)
    view = StreamTiming(path, decoded.header, decoded.trailer, decoded.present,
                        decoded.fit.stats if decoded.fit is not None else None, tuple(decoded.host_ns))
    return view, decoded


def _integer_field(document, field):
    value = (document or {}).get(field)
    return value if type(value) is int else None


def _stream_anchors(stream):
    return (_integer_field(stream.header, "start_raw_ns"),
            _integer_field(stream.header, "start_mono_ns"),
            _integer_field(stream.header, "start_real_ns"),
            _integer_field(stream.trailer, "end_raw_ns"),
            _integer_field(stream.trailer, "end_mono_ns"))


def _times_digest(times, offset):
    pack = struct.Struct(">q").pack
    return sha256(b"".join(pack(stamp - offset) for stamp in times)).hexdigest()


def _candidate(stream, timing):
    start_raw, start_mono, start_real, end_raw, end_mono = _stream_anchors(stream)
    complete_anchors = None not in (start_raw, start_mono, start_real, end_raw, end_mono)
    if complete_anchors and (end_mono < timing.start_ns or start_mono > timing.end_ns):
        return None

    failures = set()
    if stream.trailer is None:
        failures.add("stream_unclosed")
    boot_id = stream.header.get("boot_id")
    identity_bad = (
        (start_real is not None and start_mono is not None
         and abs(start_real - start_mono - timing.epoch_minus_monotonic_ns) > 5 * NS)
        or (boot_id is not None and timing.boot_id is not None and boot_id != timing.boot_id)
    )
    if identity_bad:
        failures.add("boot_mismatch")

    width = sample_range = times_sha256 = offset = None
    fit = stream.fit or {}
    if not complete_anchors or not fit:
        failures.add("anchor_unusable")
    if None not in (start_raw, start_mono, end_raw, end_mono):
        offset = meter.raw_anchor_offset_ns(stream.header, stream.trailer, allow_unclosed=False)
        if offset is None:
            failures.add("anchor_unusable")
        if fit and offset is not None:
            rtt = meter.FIT_MAX_RTT_MS if fit["filtered"] else fit["request_rtt_ms_max"]
            step_ns = meter.STEP_MS[stream.header["rate_idx"]] * 1_000_000
            spread = abs((end_raw - end_mono) - (start_raw - start_mono))
            excess = max(0, -Fraction(fit["excess_latency_ms_min"]))
            width = spread + 1_000_000 + step_ns + ceil(1_000_000 * (excess + Fraction(rtt)))
            if width > CAP_NS:
                failures.add("half_width_over_cap")
    if ((start_mono is not None and start_mono > timing.start_ns)
            or (end_mono is not None and end_mono < timing.end_ns)):
        failures.add("not_bracketed")
    if offset is not None and fit:
        raw = stream.host_ns
        lo = bisect_right(raw, timing.start_ns + offset) - 1
        hi = bisect_left(raw, timing.end_ns + offset)
        if lo < 0 or hi >= len(raw):
            failures.add("not_bracketed")
        else:
            window = raw[lo:hi + 1]
            if any(a >= b for a, b in zip(window, window[1:])):
                failures.add("anchor_unusable")
            else:
                sample_range = (lo, hi + 1)
                times_sha256 = _times_digest(window, offset)

    return StreamCheck(stream.path, tuple(code for code in FAILURES if code in failures), width, offset,
                       sample_range, times_sha256, fit.get("excess_latency_ms_p95"),
                       fit.get("excess_latency_ms_max"))


def select_dc(timing, streams):
    present = tuple(stream for stream in streams if stream.present)
    if not present:
        return DCSelection("meter_absent", ())
    candidates = tuple(check for stream in present if (check := _candidate(stream, timing)) is not None)
    passing = tuple(check for check in candidates if not check.failures)
    if len(passing) == 1:
        return DCSelection("ok", candidates, passing[0])
    if passing:
        return DCSelection("ambiguous_overlap", candidates)
    failures = {failure for check in candidates for failure in check.failures}
    return DCSelection(next((code for code in FAILURES if code in failures), "not_bracketed"), candidates)


def _attach_dc(episode, selected, decoded):
    source = decoded[selected.path]
    lo, stop = selected.sample_slice
    domain = "joulewise.km003c.raw:" + selected.path
    samples = tuple(source.watts[lo:stop])
    if len(samples) != stop - lo or not all(map(isfinite, samples)):
        raise ReaderBindingError("decoded meter values")
    period = meter.STEP_MS[source.header["rate_idx"]] * 1_000_000
    trace = PowerTrace("wall_meter", "dc_in", domain, tuple(source.host_ns[lo:stop]), samples,
                       "W", period)
    mapping = ClockMapping(domain, episode.clock_domain, -selected.offset_ns, selected.width_ns, METHOD)
    return replace(episode, power_traces=(*episode.power_traces, trace),
                   clock_mappings=(*episode.clock_mappings, mapping))


def first_read(inputs, stage1):
    """Rebind each dispatched leg and join the authenticated inputs in memory."""
    inputs.verify_stage1(stage1)
    cache = {}
    positions = []
    for leg in stage1.legs:
        leg_id = leg.binding.leg_id
        position = inputs.positions[leg_id]
        if not leg.g0_released:
            positions.append(analysis.LegInput(leg_id, leg.kind, leg.admitted, False))
            continue

        pin = position["files"]
        files = {role: inputs.read_entry(position["span_id"], pin[role])
                 for role in ("episode", "config", "metadata", "rails", "script")}
        timing, period, evidence = binding_projection(
            files["episode"], files["config"], files["metadata"], run_id=position["run_id"],
            config_sha256=pin["config"]["sha256"],
        )
        rail = rail_timing(files["rails"], timing, period, evidence)
        certificate = inputs.certificate(leg_id)
        if timing.episode_id != leg.episode_id or rail.evidence() != certificate["rails"]:
            raise ReaderBindingError("certificate rail or episode identity")
        span_id = position["span_id"]
        if span_id not in cache:
            decoded = {}
            projected = []
            for entry in inputs.spans[span_id]["streams"]:
                path = entry["path"]
                view, decoded[path] = decoded_stream(path, inputs.read_entry(span_id, entry))
                projected.append(view)
            cache[span_id] = (projected, decoded)
        projected, decoded = cache[span_id]
        dc = select_dc(timing, projected)
        if any(certificate.get(key) != value for key, value in dc.evidence().items()):
            raise ReaderBindingError("certificate meter timing")

        work = _decode(files["script"])
        if (work["leg_id"] != leg_id or work["leg_spec_sha256"] != position["spec_sha256"]
                or work["script"]["kind"] != leg.kind):
            raise ReaderBindingError("script identity")
        try:
            episode = from_json(Episode, files["episode"])
        except ValueError:
            positions.append(analysis.LegInput(leg_id, leg.kind, leg.admitted, True, analysis.INVALID_LEG_RECORD))
            continue
        if (episode.episode_id, episode.clock_domain, episode.start_ns, episode.end_ns) != (
                timing.episode_id, timing.clock_domain, timing.start_ns, timing.end_ns):
            raise ReaderBindingError("decoded episode identity")
        episode = _join_native_rails(episode, files["rails"], timing, rail, evidence)
        if dc.selected is not None:
            episode = _attach_dc(episode, dc.selected, decoded)
        positions.append(analysis.LegInput(leg_id, leg.kind, leg.admitted, True, episode, files["script"],
                                           pin["script"]["sha256"]))
    return tuple(positions)
