"""Whole-machine DC-input energy from a KM003C stream (``scripts/km003c_monitor.py``).

Standard library only.  A recorded, disclosed diagnostic: nothing here refuses
a window or produces a claim number.

What is measured.  The POWER-Z KM003C sits on the USB-C cable between the
wall adapter and the Mac and samples bus voltage (Vbus) and bus current (Ibus)
at 50 samples per second.  Vbus x Ibus is the power entering the machine from
the adapter.  When the battery helps (discharges) or charges, the machine's
own consumption differs from the adapter input by the battery's power, which
the SMC reports once a second as B0AC (battery current, mA, negative =
discharging) and B0AV (battery voltage, mV).  So

    machine power  =  meter power  +  battery power into the machine
    battery power into the machine  =  -B0AC [mA] x B0AV [mV] / 1e6   [W]

(positive while the battery discharges into the machine, negative while it
charges).

Device time.  Each 20-byte sample carries a 16-bit sequence number that counts
device milliseconds (1 kHz) and wraps every 65.536 s; at 50 samples per second
consecutive samples are 20 apart.  :func:`samples` unwraps it: the step
between consecutive samples is taken as the signed 16-bit difference (so a
small backward step, the meter re-sending samples it already sent, stays
backward and is dropped as a duplicate), except across a stall between polls
longer than 32 s, where the host receive times choose the number of wraps.
A gap of more than one step is counted as dropped samples.

Clock alignment.  Device milliseconds are mapped to the host clock
CLOCK_MONOTONIC_RAW by a straight line host_ns = a + b x dev_ms fitted on
"earliest-arrival" points: for a poll whose answer was not capped at 63
samples (so it drained the meter's queue and its newest sample is recent) and
whose request-to-answer round trip was under 3 ms (so the host was not
descheduled mid-transfer), the newest sample was digitised at most one sample
period plus the round trip before the answer arrived.  Fitting a line under
the lowest such points (minimum residual per ~10 s bin, then a line through
those minima) estimates the meter's clock rate and the minimum latency; each
point's height above that line is its extra latency, the alignment jitter.

Energy in a window.  :func:`integrate` takes the mean power of the samples
whose host time falls in [t0, t1) times the window's duration.  Samples are
evenly spaced in device time (drops are counted and flagged separately), so
the mean times the duration is the integral without needing interpolation at
the window edges; at 50 samples per second a trapezoid adds nothing.

Worked example (tests/fixtures/km003c/repo_live_50sps.jsonl, a 20 s desk
recording at 50 samples/s; pinned in test_worked_example_numbers).  Times are
seconds after the first sample.  Baseline [0, 10) s: 500 meter samples, mean
69.258 W.  Window [12, 17) s: 250 samples whose mean power x 5 s is
364.540 J.  dE_meter = 364.540 - 69.258 x 5 = 18.252 J.  B0AC read 0 mA at all
25 window polls and 50 baseline polls, so the battery term is 0 J and
dE_machine = 18.252 J.  If the rail (powermetrics CPU+GPU+ANE) energy above
its own baseline over the same window were 9.1 J, rho = 9.1 / 18.252 = 0.50.
"""

from __future__ import annotations

import bisect
import dataclasses
import json
import math
import struct
import sys
from collections.abc import Iterable, Mapping, Sequence
from pathlib import Path
from typing import Any

STEP_MS = {0: 500, 1: 100, 2: 20, 3: 1}
SAMPLE = struct.Struct("<HHiiHHHH")
RESPONSE_CAP = 63
WRAP = 65536
FIT_MAX_RTT_MS = 3.0
FIT_BIN_MS = 10_000
FIT_MIN_POINTS = 20

DROP_LIMIT = 0.005                  # meter.drops_excess above 0.5 %
PDTR_GAIN_BAND = (0.95, 1.02)       # meter.pdtr_gain_out_of_band outside this
PDTR_MIN_W = 1.0                    # bins with less meter power carry no gain
VBUS_BAND_V = (26.6, 29.4)          # 28 V EPR contract +/- 5 %
BATTERY_FLOOR_MA = 0                # meter.battery_activity when |B0AC| > this
FIT_RESIDUAL_PERIODS = 2            # meter.clock_fit_residual above this many sample periods

CODES = ("meter.absent", "meter.drops_excess", "meter.duplicates", "meter.clock_fit_residual",
         "meter.pdtr_gain_out_of_band", "meter.battery_activity", "meter.vbus_out_of_contract")


# --------------------------------------------------------------------------
# Loading and decoding


def load(path: str | Path) -> tuple[dict | None, dict | None, list[dict], list[dict]]:
    """(header, trailer, batches, errors) of one stream file.

    A truncated last line (a writer killed mid-line) is ignored.  Any other
    line that is not a JSON object is kept in ``errors`` as
    ``{"k": "e", "parse_error": ..., "line": number}``, so it counts as a
    protocol error; the samples it carried show up as dropped samples.
    """

    header = trailer = None
    batches: list[dict] = []
    errors: list[dict] = []
    with open(path) as handle:
        lines = handle.read().split("\n")
    for number, line in enumerate(lines, 1):
        if not line.strip():
            continue
        try:
            item = json.loads(line)
            if not isinstance(item, dict):
                raise ValueError(f"a JSON {type(item).__name__}, not an object")
        except ValueError as exc:
            if number == len(lines):
                continue  # no newline after it: the truncated final line
            errors.append({"k": "e", "parse_error": str(exc)[:200], "line": number})
            continue
        kind = item.get("k")
        if kind == "h":
            header = item
        elif kind == "t":
            trailer = item
        elif kind == "e":
            errors.append(item)
        elif kind == "b":
            batches.append(item)
    return header, trailer, batches, errors


@dataclasses.dataclass
class Samples:
    dev_ms: list[int]          # unwrapped device time of each kept sample
    vbus_v: list[float]
    ibus_a: list[float]
    batch: list[int]           # index into the batch list of each kept sample
    duplicates: int            # samples dropped because they did not advance device time
    step_ms: int

    @property
    def watts(self) -> list[float]:
        return [v * i for v, i in zip(self.vbus_v, self.ibus_a)]


def samples(header: Mapping[str, Any], batches: Sequence[Mapping[str, Any]]) -> Samples:
    step = STEP_MS[header["rate_idx"]]
    dev_ms: list[int] = []
    vbus: list[float] = []
    ibus: list[float] = []
    index: list[int] = []
    duplicates = 0
    previous_seq = None
    current = 0
    running_max = None
    previous_rx = None
    for j, batch in enumerate(batches):
        raw = bytes.fromhex(batch["p"]) if batch.get("p") else b""
        for k, (seq, _marker, v_uv, i_ua, *_aux) in enumerate(SAMPLE.iter_unpack(raw)):
            if previous_seq is None:
                current = 0
            else:
                d = ((seq - previous_seq + WRAP // 2) % WRAP) - WRAP // 2
                if k == 0 and previous_rx is not None:
                    host_ms = (batch["rx"] - previous_rx) / 1e6
                    if host_ms > WRAP // 2:
                        # A stall longer than half a wrap: let host time pick the wraps.
                        d += round((host_ms - d) / WRAP) * WRAP
                current += d
            previous_seq = seq
            if running_max is not None and current <= running_max:
                duplicates += 1
                continue
            running_max = current
            dev_ms.append(current)
            vbus.append(v_uv / 1e6)
            ibus.append(i_ua / 1e6)
            index.append(j)
        if raw:
            previous_rx = batch["rx"]
    return Samples(dev_ms, vbus, ibus, index, duplicates, step)


def drops(s: Samples) -> dict[str, Any]:
    dropped = irregular = 0
    for a, b in zip(s.dev_ms, s.dev_ms[1:]):
        gap = b - a
        if gap > s.step_ms:
            dropped += gap // s.step_ms - 1
        if gap % s.step_ms:
            irregular += 1
    total = len(s.dev_ms) + dropped
    return {"kept": len(s.dev_ms), "dropped": dropped, "irregular_gaps": irregular,
            "drop_fraction": dropped / total if total else None}


# --------------------------------------------------------------------------
# Clock fit


def _linear_fit(xs: Sequence[float], ys: Sequence[float]) -> tuple[float, float]:
    """Least-squares (intercept, slope), computed on centred values for precision."""

    n = len(xs)
    if n < 2:
        raise ValueError("a line needs two points")
    mx = sum(xs) / n
    my = sum(ys) / n
    sxx = sum((x - mx) ** 2 for x in xs)
    if sxx == 0:
        raise ValueError("all points at one x")
    sxy = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    slope = sxy / sxx
    return my - slope * mx, slope


def percentile(values: Sequence[float], q: float) -> float:
    """Linear-interpolation percentile (numpy's default)."""

    ordered = sorted(values)
    if not ordered:
        raise ValueError("no values")
    position = (len(ordered) - 1) * q / 100.0
    low = math.floor(position)
    high = min(low + 1, len(ordered) - 1)
    return ordered[low] + (ordered[high] - ordered[low]) * (position - low)


@dataclasses.dataclass
class Fit:
    a_ns: float               # host CLOCK_MONOTONIC_RAW ns at device ms 0
    b_ns_per_ms: float        # host ns per device ms
    stats: dict[str, Any]

    def host_ns(self, dev_ms: float) -> int:
        return int(round(self.a_ns + self.b_ns_per_ms * dev_ms))


def clock_fit(s: Samples, batches: Sequence[Mapping[str, Any]]) -> Fit:
    newest: dict[int, int] = {}
    for dev, j in zip(s.dev_ms, s.batch):
        newest[j] = dev  # the last kept sample of each batch
    points = []
    for j, dev in newest.items():
        b = batches[j]
        points.append((dev, b["rx"], (b["rx"] - b["tx"]) / 1e6, b["n"]))
    if len(points) < 2:
        raise ValueError("fewer than two batches with samples")
    good = [p for p in points if p[3] < RESPONSE_CAP and p[2] < FIT_MAX_RTT_MS]
    used = good if len(good) >= FIT_MIN_POINTS else points
    # Work relative to the first point so the sums stay well inside float precision.
    x0, y0 = used[0][0], used[0][1]
    xs = [p[0] - x0 for p in used]
    ys = [p[1] - y0 for p in used]
    a0, b0 = _linear_fit(xs, ys)
    residual = [y - (a0 + b0 * x) for x, y in zip(xs, ys)]
    span = xs[-1] - xs[0]
    bins = max(4, int(span / FIT_BIN_MS))
    width = (span + 1) / bins
    lowest: dict[int, int] = {}
    for idx, x in enumerate(xs):
        k = min(int((x - xs[0]) / width), bins - 1)
        if k not in lowest or residual[idx] < residual[lowest[k]]:
            lowest[k] = idx
    env_x = [xs[i] for i in lowest.values()]
    env_y = [ys[i] for i in lowest.values()]
    try:
        a1, b1 = _linear_fit(env_x, env_y)
    except ValueError:
        a1, b1 = a0, b0
    above = [(y - (a1 + b1 * x)) / 1e6 for x, y in zip(xs, ys)]  # ms above the envelope
    rtts = [p[2] for p in points]
    stats = {"points": len(points), "points_used": len(used),
             "fraction_used": len(used) / len(points), "filtered": len(good) >= FIT_MIN_POINTS,
             "clock_rate_ppm": (b1 / 1e6 - 1) * 1e6,
             "excess_latency_ms_p50": percentile(above, 50),
             "excess_latency_ms_p95": percentile(above, 95),
             "excess_latency_ms_max": max(above), "excess_latency_ms_min": min(above),
             "request_rtt_ms_p50": percentile(rtts, 50), "request_rtt_ms_max": max(rtts)}
    # Back from relative to absolute: host = y0 + a1 + b1 (dev - x0).
    return Fit(a_ns=y0 + a1 - b1 * x0, b_ns_per_ms=b1, stats=stats)


# --------------------------------------------------------------------------
# The parsed stream


@dataclasses.dataclass
class Stream:
    header: dict | None
    trailer: dict | None
    batches: list[dict]
    errors: list[dict]
    samples: Samples | None
    fit: Fit | None
    host_ns: list[int]                  # per kept sample, CLOCK_MONOTONIC_RAW
    watts: list[float]                  # per kept sample, Vbus x Ibus
    poll_ns: list[int]                  # per poll line (rx), CLOCK_MONOTONIC_RAW
    smc: list[dict]                     # per poll line, the SMC values (None where missing)
    fit_error: str | None = None

    @property
    def present(self) -> bool:
        """The meter streamed samples (whether or not they could be put on host time)."""

        return bool(self.header and self.header.get("status") == "streaming" and self.samples is not None
                    and self.samples.dev_ms)

    @property
    def aligned(self) -> bool:
        """The samples carry host times (the clock fit succeeded)."""

        return bool(self.host_ns)

    def battery_watts(self) -> tuple[list[int], list[float]]:
        """(poll times, battery power into the machine W) where B0AC and B0AV were read."""

        times, watts = [], []
        for t, values in zip(self.poll_ns, self.smc):
            current, voltage = values.get("B0AC"), values.get("B0AV")
            if current is not None and voltage is not None:
                times.append(t)
                watts.append(-current * voltage / 1e6)
        return times, watts


def parse(path: str | Path) -> Stream:
    header, trailer, batches, errors = load(path)
    if header is not None and "status" not in header:
        header = {**header, "status": "streaming"}  # the probe's streams predate the field
    if header is None or header.get("status") != "streaming":
        return Stream(header, trailer, batches, errors, None, None, [], [], [], [])
    polls = sorted(batches, key=lambda b: b["rx"])
    with_samples = [b for b in polls if b.get("n")]
    s = samples(header, with_samples)
    fit, fit_error, host = None, None, []
    try:
        fit = clock_fit(s, with_samples)
        host = [fit.host_ns(d) for d in s.dev_ms]
    except ValueError as exc:
        fit_error = str(exc)
    return Stream(header, trailer, polls, errors, s, fit, host, s.watts if host else [],
                  [b["rx"] for b in polls], [dict(b.get("smc") or {}) for b in polls], fit_error)


def raw_offset_ns(stream: Stream) -> int | None:
    """CLOCK_MONOTONIC_RAW minus ``time.monotonic_ns`` for this stream, or None.

    Member spans are stamped in the controller's ``time.monotonic_ns``; the
    stream and its clock fit are in CLOCK_MONOTONIC_RAW.  On macOS the two
    differ by a constant except across a system sleep, so the offset read at
    the stream's start must equal the one at its end (within 1 ms); otherwise
    (a sleep, or a stream without the pairs) None, and the caller takes the
    offset from the hazard monitor's journal lines, which carry both clocks.
    raw_ns = monotonic_ns + offset.
    """

    header, trailer = stream.header or {}, stream.trailer or {}
    try:
        start = header["start_raw_ns"] - header["start_mono_ns"]
        end = trailer["end_raw_ns"] - trailer["end_mono_ns"]
    except (KeyError, TypeError):
        return None
    return start if abs(end - start) <= 1_000_000 else None


# --------------------------------------------------------------------------
# Energy


def integrate(times_ns: Sequence[int], watts: Sequence[float], t0: int, t1: int
              ) -> tuple[float | None, int]:
    """(energy J, samples used): mean power of samples in [t0, t1) x (t1 - t0).

    ``times_ns`` must be sorted.  None when no sample falls in the window.
    """

    if t1 <= t0:
        raise ValueError("window end must follow its start")
    lo = bisect.bisect_left(times_ns, t0)
    hi = bisect.bisect_left(times_ns, t1)
    n = hi - lo
    if n == 0:
        return None, 0
    return sum(watts[lo:hi]) / n * (t1 - t0) / 1e9, n


def _delta(times: Sequence[int], watts: Sequence[float], window: Sequence[int],
           baseline: Sequence[int]) -> dict[str, Any]:
    energy, n = integrate(times, watts, window[0], window[1])
    base_energy, n_base = integrate(times, watts, baseline[0], baseline[1])
    duration_s = (window[1] - window[0]) / 1e9
    if energy is None or base_energy is None:
        return {"energy_J": energy, "baseline_W": None, "delta_J": None, "n": n, "n_baseline": n_base}
    base_w = base_energy / ((baseline[1] - baseline[0]) / 1e9)
    return {"energy_J": energy, "baseline_W": base_w, "delta_J": energy - base_w * duration_s,
            "n": n, "n_baseline": n_base}


def delta_machine_energy(stream: Stream, window: Sequence[int], baseline: Sequence[int]
                         ) -> dict[str, Any]:
    """Whole-machine energy above baseline in ``window``.

    ``window`` and ``baseline`` are (start_ns, stop_ns) in CLOCK_MONOTONIC_RAW,
    the clock of the stream's ``tx``/``rx`` and of the clock fit.

        dE_meter   = E_meter(window) - P_meter(baseline) x duration(window)
        dE_battery = same, on battery power into the machine
                     (-B0AC x B0AV / 1e6 W at each poll; the SMC refreshes 1 Hz)
        dE_machine = dE_meter + dE_battery

    Returns the parts, sample counts, and ``delta_J`` (dE_machine).  When the
    stream holds no B0AC/B0AV reads in the window or baseline the battery term
    is unavailable: ``battery_term_available`` is False and ``delta_J`` is the
    meter term alone.  ``delta_J`` is None when the meter has no sample in the
    window or baseline.
    """

    meter = _delta(stream.host_ns, stream.watts, window, baseline)
    times, watts = stream.battery_watts()
    battery = _delta(times, watts, window, baseline)
    available = battery["delta_J"] is not None
    delta = None
    if meter["delta_J"] is not None:
        delta = meter["delta_J"] + (battery["delta_J"] if available else 0.0)
    return {"window_ns": list(window), "baseline_ns": list(baseline),
            "duration_s": (window[1] - window[0]) / 1e9, "meter": meter, "battery": battery,
            "battery_term_available": available, "delta_J": delta}


def rho(rail_delta: float | None, machine_delta: float | None) -> float | None:
    """Rail energy above baseline as a share of whole-machine energy above baseline.

    None when either is missing or the machine delta is not positive (no share
    of nothing).
    """

    if rail_delta is None or machine_delta is None or machine_delta <= 0:
        return None
    return rail_delta / machine_delta


# --------------------------------------------------------------------------
# Flags (all DISCLOSE)


def _flag(code: str, observed: Any, expected: Any, detail: str) -> dict[str, Any]:
    return {"code": code, "effect": "DISCLOSE", "observed": observed, "expected": expected,
            "detail": detail}


def pdtr_gain(stream: Stream, bin_ns: int = 1_000_000_000) -> dict[str, Any]:
    """Median over 1 s host-time bins of mean PDTR / mean meter power.

    PDTR is the SMC's DC-input power (refreshed once a second); a gain near 1
    says the meter and the Mac's own input sensor agree.  Bins with meter
    power under 1 W or no PDTR read are skipped.
    """

    if not stream.host_ns:
        return {"bins": 0, "median": None}
    start = stream.host_ns[0]
    meter_bins: dict[int, list[float]] = {}
    for t, w in zip(stream.host_ns, stream.watts):
        meter_bins.setdefault((t - start) // bin_ns, []).append(w)
    pdtr_bins: dict[int, list[float]] = {}
    for t, values in zip(stream.poll_ns, stream.smc):
        if values.get("PDTR") is not None:
            pdtr_bins.setdefault((t - start) // bin_ns, []).append(values["PDTR"])
    gains = []
    for k, ws in meter_bins.items():
        mean_w = sum(ws) / len(ws)
        if k in pdtr_bins and mean_w >= PDTR_MIN_W:
            gains.append(sum(pdtr_bins[k]) / len(pdtr_bins[k]) / mean_w)
    return {"bins": len(gains), "median": percentile(gains, 50) if gains else None}


def flags(stream: Stream, windows: Iterable[Sequence[int]] = ()) -> list[dict[str, Any]]:
    """The meter.* disclosure flags.

    Stream-level: meter.absent, meter.drops_excess, meter.duplicates,
    meter.clock_fit_residual (also when no fit could be made),
    meter.pdtr_gain_out_of_band (also when no gain could be computed: the
    agreement with the Mac's own input sensor is then unconfirmed) and
    meter.vbus_out_of_contract (Vbus outside the 28 V EPR contract +/- 5 %:
    26.6-29.4 V; the probe saw 27.36-27.53 V).  Per window
    (CLOCK_MONOTONIC_RAW (start, stop)): meter.battery_activity when any B0AC
    read in the window is nonzero (the gauge reads exactly 0 at float; the
    probe saw bursts to -865 mA during inference).
    """

    if not stream.present:
        reason = (stream.header or {}).get("reason") or "no samples in the stream"
        return [_flag("meter.absent", {"status": (stream.header or {}).get("status"),
                                       "reason": reason}, "streaming", f"meter absent: {reason}")]
    out = []
    d = drops(stream.samples)
    if d["drop_fraction"] is not None and d["drop_fraction"] > DROP_LIMIT:
        out.append(_flag("meter.drops_excess", d, DROP_LIMIT,
                         f"{d['dropped']} samples dropped ({100 * d['drop_fraction']:.2f} %)"))
    if stream.samples.duplicates:
        out.append(_flag("meter.duplicates", stream.samples.duplicates, 0,
                         f"{stream.samples.duplicates} re-delivered samples dropped"))
    limit_ms = FIT_RESIDUAL_PERIODS * stream.samples.step_ms
    if stream.fit is None:
        out.append(_flag("meter.clock_fit_residual", stream.fit_error, limit_ms,
                         f"no clock fit: {stream.fit_error}"))
    elif stream.fit.stats["excess_latency_ms_max"] > limit_ms:
        out.append(_flag("meter.clock_fit_residual", stream.fit.stats, limit_ms,
                         f"fit residual {stream.fit.stats['excess_latency_ms_max']:.1f} ms above "
                         f"{limit_ms} ms (two sample periods)"))
    gain = pdtr_gain(stream)
    if gain["median"] is None or not PDTR_GAIN_BAND[0] <= gain["median"] <= PDTR_GAIN_BAND[1]:
        out.append(_flag("meter.pdtr_gain_out_of_band", gain, list(PDTR_GAIN_BAND),
                         f"median PDTR/meter gain {gain['median']} outside {PDTR_GAIN_BAND}"))
    outside = [v for v in stream.samples.vbus_v if not VBUS_BAND_V[0] <= v <= VBUS_BAND_V[1]]
    if outside:
        out.append(_flag("meter.vbus_out_of_contract",
                         {"samples_outside": len(outside), "min_V": min(outside), "max_V": max(outside)},
                         list(VBUS_BAND_V), f"{len(outside)} samples with Vbus outside {VBUS_BAND_V} V"))
    for window in windows:
        reads = [values.get("B0AC") for t, values in zip(stream.poll_ns, stream.smc)
                 if window[0] <= t < window[1] and values.get("B0AC") is not None]
        active = [c for c in reads if abs(c) > BATTERY_FLOOR_MA]
        if active:
            out.append(_flag("meter.battery_activity",
                             {"window_ns": list(window), "reads": len(reads), "nonzero": len(active),
                              "min_mA": min(active), "max_mA": max(active)},
                             BATTERY_FLOOR_MA, f"B0AC nonzero at {len(active)} of {len(reads)} reads"))
    return out


def characterise(stream: Stream) -> dict[str, Any]:
    out: dict[str, Any] = {"status": (stream.header or {}).get("status"), "polls": len(stream.batches),
                           "protocol_errors": len(stream.errors)}
    if stream.present and not stream.aligned:
        out.update(samples=len(stream.samples.dev_ms), fit=stream.fit_error)
    if stream.aligned:
        span_s = (stream.host_ns[-1] - stream.host_ns[0]) / 1e9
        out.update(samples=len(stream.host_ns), host_span_s=span_s,
                   achieved_sps=len(stream.host_ns) / span_s if span_s else None,
                   duplicates=stream.samples.duplicates, **drops(stream.samples),
                   meter_mean_W=sum(stream.watts) / len(stream.watts),
                   vbus_min_V=min(stream.samples.vbus_v), vbus_max_V=max(stream.samples.vbus_v),
                   fit=stream.fit.stats if stream.fit else stream.fit_error, pdtr_gain=pdtr_gain(stream))
        pdtr = [v["PDTR"] for v in stream.smc if v.get("PDTR") is not None]
        out["pdtr_mean_W"] = sum(pdtr) / len(pdtr) if pdtr else None
    if stream.trailer:
        cpu = stream.trailer["utime_s"] + stream.trailer["stime_s"]
        elapsed = stream.trailer["elapsed_s"]
        out.update(reader_cpu_s=cpu, reader_elapsed_s=elapsed,
                   reader_cpu_pct_of_core=100 * cpu / elapsed if elapsed else None,
                   reader_cpu_s_per_hour=3600 * cpu / elapsed if elapsed else None)
    out["flags"] = [f["code"] for f in flags(stream)]
    return out


if __name__ == "__main__":
    for path in sys.argv[1:]:
        print(json.dumps(characterise(parse(path)), indent=1))
