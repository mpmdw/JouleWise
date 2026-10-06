"""Clock hazard: the wall clock stepped, or drifts beyond the 5 ms budget.

Measured directly, never parsed from a settings string:

- the **anchor** = CLOCK_REALTIME minus CLOCK_MONOTONIC_RAW, read in process
  (``clock_reference.sample_anchor``: RAW, REALTIME, RAW; the read skew is the
  RAW interval around the REALTIME read).  A wall-clock step moves it;
- the kernel **frequency word** f, read without privileges by
  ``ntp_adjtime(modes=0)`` (``kernel_clock.read_kernel_frequency``).  With
  network time OFF the anchor drifts linearly at f;
- the **residual**: the anchor's movement after removing f x elapsed RAW time.
  The sign was checked live on 10-05 (f = -207591, -3.1676 ppm): over 90 s
  the anchor moved -285.71 us against -285.23 us predicted, and every 10 s
  residual stayed under 1 us;
- the boot session (``kern.bootsessionuuid``): a reboot makes anchors
  incomparable.

Arm (plan §2.3; thresholds from the window plan, defaults below):

(i)   frequency gate: h + (|f| + 0.25 ppm) x T_stream_max <= 5 ms with
      h = 3.7 ms and T_stream_max = 335 s, i.e. |f| <= 3.6306 ppm.  The live
      word on 10-05 (-207591 = -3.1676 ppm) gives 4.8449 ms;
(ii)  over the dwell, sampled at 1 Hz, the signed residual stays within
      +-1 ms of its start value;
(iii) every anchor read pair has skew <= 1 ms;
(iv)  f is identical at dwell start, dwell end and GO; the boot session is
      unchanged.

In the window (flag only): ``clock.step`` when the residual moves more than
1 ms between consecutive 1 Hz samples, ``clock.frequency_changed`` when f
changes, and the member join ``clock.step_overlap``.  The per-member 5 ms
anchor bound computed by ``uncertainty_evidence`` stays authoritative and is
not touched here.

The form of the T-0 author check (``arm_readiness_evidence_t0.py:1213-1269``)
is ported here, not imported.
"""

from __future__ import annotations

import ctypes
import sys
import uuid
from collections.abc import Callable, Mapping, Sequence
from fractions import Fraction
from typing import Any

from joulewise import clock_reference, kernel_clock
from joulewise.hazards.base import (
    PASS, REFUSE, UNMEASURED, Context, Measurement, RawRef, Stamp, Verdict, finding,
    canonical_json, require_thresholds, sha256_hex, row,
)
from joulewise.hazards.base import coverage_gap as base_coverage_gap

MODULE = "clock"
BOOT_ARGV = ("/usr/sbin/sysctl", "-n", "kern.bootsessionuuid")
FREQUENCY_SCALE = kernel_clock.FREQUENCY_SCALE  # raw word units per ppm

DEFAULT_THRESHOLDS: dict[str, Any] = {
    "t_stream_max_s": 335,          # X10 sizing: the longest sampler stream
    "h_ms": 3.7,                    # 3.60 ms h_max + 0.10 ms placement margin
    "frequency_margin_ppm": 0.25,
    "limit_ms": 5.0,
    "skew_max_ns": 1_000_000,
    "residual_max_ns": 1_000_000,   # dwell linearity, +-1 ms of the start value
    "step_ns": 1_000_000,           # in-window step between consecutive samples
}
THRESHOLD_KEYS = tuple(DEFAULT_THRESHOLDS)

FrequencyReader = Callable[[], Mapping[str, Any]]
BootReader = Callable[[Context], str]


# --------------------------------------------------------------------------
# Probes


def read_frequency() -> dict[str, Any]:
    """``ntp_adjtime(modes=0)``: read-only; raises OSError off 64-bit macOS."""

    return kernel_clock.read_kernel_frequency()


def read_boot_session(ctx: Context) -> str:
    """kern.bootsessionuuid through the context's probe runner."""

    completed = ctx.run(BOOT_ARGV, ctx.probe_timeout_s)
    if not completed.ok:
        detail = completed.error or ("timeout" if completed.timed_out else
                                     f"exit {completed.returncode}")
        raise OSError(f"kern.bootsessionuuid probe failed: {detail}")
    text = completed.stdout.decode("ascii", errors="replace").strip().lower()
    canonical = str(uuid.UUID(text))
    if canonical != text:
        raise ValueError("kern.bootsessionuuid is not a canonical UUID")
    return canonical


def read_boot_session_inprocess() -> str:
    """The same value through ``sysctlbyname`` (no child process; macOS only)."""

    if sys.platform != "darwin":
        raise OSError("kern.bootsessionuuid requires macOS")
    libc = ctypes.CDLL("/usr/lib/libSystem.B.dylib", use_errno=True)
    size = ctypes.c_size_t(64)
    buffer = ctypes.create_string_buffer(size.value)
    if libc.sysctlbyname(b"kern.bootsessionuuid", buffer, ctypes.byref(size), None, 0) != 0:
        raise OSError(ctypes.get_errno(), "sysctlbyname kern.bootsessionuuid failed")
    text = buffer.value.decode("ascii").strip().lower()
    return str(uuid.UUID(text))


def _anchor_record(ctx: Context) -> dict[str, int]:
    anchor = clock_reference.sample_anchor(ctx.clocks.clock_gettime_ns)
    return {"realtime_ns": anchor.realtime_ns, "monotonic_raw_ns": anchor.monotonic_raw_ns,
            "read_skew_ns": anchor.read_skew_ns,
            "anchor_ns": anchor.realtime_ns - anchor.monotonic_raw_ns}


def sample(ctx: Context, *, frequency_reader: FrequencyReader | None = read_frequency,
           ) -> dict[str, Any]:
    """One light reading: the anchor, plus f unless ``frequency_reader`` is None.

    Returns a JSON-able sample with its own three-clock stamps and an
    ``error`` (None when every requested read succeeded).
    """

    started = ctx.stamp()
    error = None
    anchor = frequency = None
    try:
        anchor = _anchor_record(ctx)
        if frequency_reader is not None:
            frequency = dict(kernel_clock.validate_probe(dict(frequency_reader())))
    except Exception as exc:  # any probe failure is UNMEASURED, never a pass
        error = f"{type(exc).__name__}: {exc}"
    finished = ctx.stamp()
    return {"started": started.to_json(), "finished": finished.to_json(), "anchor": anchor,
            "frequency": frequency, "error": error}


def measure(ctx: Context, *, frequency_reader: FrequencyReader = read_frequency,
            boot_reader: BootReader = read_boot_session) -> Measurement:
    """Instant reading: anchor, frequency word and boot session."""

    started = ctx.stamp()
    values: dict[str, Any] = {"anchor": None, "frequency": None, "boot_session_uuid": None}
    raw: list[RawRef] = []
    error = None
    try:
        values["boot_session_uuid"] = boot_reader(ctx)
        values["anchor"] = _anchor_record(ctx)
        frequency = dict(kernel_clock.validate_probe(dict(frequency_reader())))
        values["frequency"] = frequency
        raw.append(ctx.keep_raw("timex.bin", bytes.fromhex(frequency["raw_hex"])))
    except Exception as exc:
        error = f"{type(exc).__name__}: {exc}"
    finished = ctx.stamp()
    return Measurement(MODULE, "instant", values, tuple(raw), started, finished, error)


def series(samples: Sequence[Mapping[str, Any]], *, boot_start: str | None,
           boot_end: str | None, started: Stamp, finished: Stamp) -> Measurement:
    """A dwell series (1 Hz samples, f at least at start and end) as one Measurement."""

    errors = [item["error"] for item in samples if item.get("error")]
    error = None
    if errors:
        error = f"{len(errors)} sample(s) failed; first: {errors[0]}"
    elif boot_start is None or boot_end is None:
        error = "boot session unread at dwell start or end"
    values = {"samples": [dict(item) for item in samples], "boot_session_uuid_start": boot_start,
              "boot_session_uuid_end": boot_end}
    encoded = canonical_json(values)
    return Measurement(MODULE, "series", values,
                       (RawRef("series.json", sha256_hex(encoded), len(encoded), None),),
                       started, finished, error)


# --------------------------------------------------------------------------
# Arithmetic (exact)


def frequency_bound(raw_word: int, thresholds: Mapping[str, Any]) -> dict[str, Any]:
    """h + (|f| + margin) x T_stream_max against the limit, in exact arithmetic."""

    rate_ppm = Fraction(abs(int(raw_word)), FREQUENCY_SCALE)
    span_s = Fraction(str(thresholds["t_stream_max_s"]))
    h_s = Fraction(str(thresholds["h_ms"])) / 1000
    margin = Fraction(str(thresholds["frequency_margin_ppm"]))
    limit_s = Fraction(str(thresholds["limit_ms"])) / 1000
    bound_s = h_s + (rate_ppm + margin) * span_s / 1_000_000
    max_ppm = (limit_s - h_s) * 1_000_000 / span_s - margin
    return {"frequency_ppm": float(Fraction(int(raw_word), FREQUENCY_SCALE)),
            "bound_ms": float(bound_s * 1000), "limit_ms": float(limit_s * 1000),
            "max_abs_frequency_ppm": float(max_ppm), "passes": bound_s <= limit_s}


def expected_anchor_movement_ns(raw_word: int, elapsed_raw_ns: int) -> Fraction:
    """Anchor drift at frequency word f over an elapsed RAW interval, in ns."""

    return Fraction(int(raw_word) * int(elapsed_raw_ns), FREQUENCY_SCALE * 1_000_000)


def residual_ns(first: Mapping[str, int], later: Mapping[str, int], raw_word: int) -> Fraction:
    """Signed residual of ``later`` against ``first``: anchor movement minus f x elapsed."""

    movement = int(later["anchor_ns"]) - int(first["anchor_ns"])
    elapsed = int(later["monotonic_raw_ns"]) - int(first["monotonic_raw_ns"])
    return Fraction(movement) - expected_anchor_movement_ns(raw_word, elapsed)


# --------------------------------------------------------------------------
# Judge


def judge(measurement: Measurement, thresholds: Mapping[str, Any]) -> Verdict:
    limits = require_thresholds(MODULE, thresholds, THRESHOLD_KEYS)
    if measurement.module != MODULE:
        raise ValueError("clock.judge received another module's measurement")
    if measurement.error:
        return Verdict(MODULE, UNMEASURED, (measurement.error,), limits)
    if measurement.kind == "instant":
        return _judge_instant(measurement.values, limits)
    if measurement.kind == "series":
        return _judge_series(measurement.values, limits)
    raise ValueError(f"unknown clock measurement kind {measurement.kind!r}")


def _judge_instant(values: Mapping[str, Any], limits: Mapping[str, Any]) -> Verdict:
    anchor, frequency = values.get("anchor"), values.get("frequency")
    if not anchor or not frequency or not values.get("boot_session_uuid"):
        return Verdict(MODULE, UNMEASURED, ("anchor, frequency word or boot session absent",),
                       limits)
    reasons = []
    gate = frequency_bound(frequency["raw_word"], limits)
    if not gate["passes"]:
        reasons.append(
            f"frequency gate: {gate['bound_ms']:.4f} ms > {gate['limit_ms']} ms "
            f"(|f| {abs(gate['frequency_ppm']):.4f} ppm > {gate['max_abs_frequency_ppm']:.4f} ppm)")
    if anchor["read_skew_ns"] < 0 or anchor["read_skew_ns"] > limits["skew_max_ns"]:
        reasons.append(f"anchor read skew {anchor['read_skew_ns']} ns exceeds "
                       f"{limits['skew_max_ns']} ns")
    observed = {"frequency_gate": gate, "read_skew_ns": anchor["read_skew_ns"],
                "raw_word": frequency["raw_word"]}
    return Verdict(MODULE, REFUSE if reasons else PASS, tuple(reasons), limits, observed)


def _judge_series(values: Mapping[str, Any], limits: Mapping[str, Any]) -> Verdict:
    samples = list(values.get("samples") or [])
    if len(samples) < 2 or samples[0].get("frequency") is None:
        return Verdict(MODULE, UNMEASURED,
                       ("dwell series needs >= 2 samples and f at its start",), limits)
    if samples[-1].get("frequency") is None:
        return Verdict(MODULE, UNMEASURED, ("dwell series has no f at its end",), limits)
    reasons = []
    if values.get("boot_session_uuid_start") != values.get("boot_session_uuid_end"):
        reasons.append("boot session changed during the dwell")
    words = [item["frequency"]["raw_word"] for item in samples if item.get("frequency")]
    f0 = words[0]
    if any(word != f0 for word in words):
        reasons.append(f"frequency word changed during the dwell: {sorted(set(words))}")
    gate = frequency_bound(f0, limits)
    if not gate["passes"]:
        reasons.append(f"frequency gate: {gate['bound_ms']:.4f} ms > {gate['limit_ms']} ms")
    skews = [item["anchor"]["read_skew_ns"] for item in samples]
    worst_skew = max(skews)
    if min(skews) < 0 or worst_skew > limits["skew_max_ns"]:
        reasons.append(f"anchor read skew {worst_skew} ns exceeds {limits['skew_max_ns']} ns")
    first = samples[0]["anchor"]
    residuals = [residual_ns(first, item["anchor"], f0) for item in samples]
    worst = max(residuals, key=abs)
    if abs(worst) > limits["residual_max_ns"]:
        reasons.append(f"dwell residual {float(worst) / 1e6:+.4f} ms exceeds "
                       f"+-{limits['residual_max_ns'] / 1e6} ms of its start value")
    raw_span = samples[-1]["anchor"]["monotonic_raw_ns"] - first["monotonic_raw_ns"]
    observed = {"frequency_gate": gate, "samples": len(samples), "raw_span_ns": raw_span,
                "max_abs_residual_ns": float(abs(worst)), "max_read_skew_ns": worst_skew,
                "anchor_movement_ns": samples[-1]["anchor"]["anchor_ns"] - first["anchor_ns"]}
    return Verdict(MODULE, REFUSE if reasons else PASS, tuple(reasons), limits, observed)


# --------------------------------------------------------------------------
# In-window events and the member join


def window_events(samples: Sequence[Mapping[str, Any]], *, step_ns: int = 1_000_000,
                  ) -> list[dict[str, Any]]:
    """``clock.step`` and ``clock.frequency_changed`` events from 1 Hz journal samples.

    A step is a residual movement above ``step_ns`` between consecutive
    samples that read an anchor, computed with the f in force (the latest f
    read at or before the earlier sample).  A sample whose anchor read failed
    is skipped without resetting the comparison: the next good anchor is
    compared with the last one across the gap, and the residual removes f x
    the elapsed RAW time, so a step that falls across a failed sample is still
    seen.  A sample that read its anchor but failed only its f read keeps its
    anchor.  Samples before the first f read cannot be judged.
    """

    events: list[dict[str, Any]] = []
    word = None       # the f in force at ``previous``
    previous = None   # the last sample that read an anchor
    for item in samples:
        if not item.get("anchor"):
            continue
        if previous is not None and word is not None:
            moved = residual_ns(previous["anchor"], item["anchor"], word)
            if abs(moved) > step_ns:
                events.append({"code": "clock.step", "interval": _interval(previous, item),
                               "observed": float(moved), "expected": step_ns})
        frequency = item.get("frequency")
        if frequency is not None:
            if word is not None and frequency["raw_word"] != word:
                events.append({"code": "clock.frequency_changed",
                               "interval": _interval(previous or item, item),
                               "observed": frequency["raw_word"], "expected": word})
            word = frequency["raw_word"]
        previous = item
    return events


def _interval(first: Mapping[str, Any], second: Mapping[str, Any]) -> dict[str, list[int]]:
    a, b = first["started"], second["finished"]
    return {"monotonic_ns": [a["monotonic_ns"], b["monotonic_ns"]],
            "monotonic_raw_ns": [a["monotonic_raw_ns"], b["monotonic_raw_ns"]],
            "wall_ns": [a["wall_ns"], b["wall_ns"]]}


def span_findings(samples: Sequence[Mapping[str, Any]], span: Mapping[str, Any], *,
                  step_ns: int = 1_000_000, max_gap_ns: int = 3_000_000_000,
                  ) -> list[dict[str, Any]]:
    """Member join (plan §3.4): ``clock.step_overlap`` and ``clock.unmeasured``.

    ``span`` is ``{"monotonic_ns": [start, stop]}`` in the controller's
    ``time.monotonic_ns`` domain (the member's sampler stream).
    """

    start, stop = span["monotonic_ns"]
    found = []
    for event in window_events(samples, step_ns=step_ns):
        a, b = event["interval"]["monotonic_ns"]
        if a <= stop and b >= start and event["code"] == "clock.step":
            found.append(finding("clock.step_overlap", span=span, observed=event["observed"],
                                 expected=step_ns, interval=event["interval"],
                                 detail="the wall clock stepped inside the member's stream"))
    gap = coverage_gap(samples, start, stop, max_gap_ns)
    if gap is not None:
        found.append(finding("clock.unmeasured", span=span, observed=gap, expected=max_gap_ns,
                             detail="the 1 Hz clock journal has a gap overlapping the stream"))
    return found


def coverage_gap(samples: Sequence[Mapping[str, Any]], start: int, stop: int,
                 max_gap_ns: int) -> list[int] | None:
    """The first [a, b] monotonic gap longer than ``max_gap_ns`` that overlaps [start, stop].

    Readings that read an anchor are the points (a failed f read does not
    blind the step check); the span is covered when a good reading lies
    within ``max_gap_ns`` before its start and after its stop and no two
    consecutive good readings inside it are further apart than ``max_gap_ns``.
    """

    return base_coverage_gap(
        [item["finished"]["monotonic_ns"] for item in samples if item.get("anchor")],
        start, stop, max_gap_ns)


# Inventory rows (configs/gates/physics_rows.json) whose physical check this
# module performs.  tests/hazards/test_physics_coverage.py keeps the two in step.
PROTECTS: tuple[tuple[str, str, str, int], ...] = (
    # base line 6827: The live clock anchor cannot be sampled (clock_gettime REALTIME/MONOTONIC_RAW, or...
    row("joulewise/arm_readiness.py", "_sample_live_clock_anchor",
        "readiness_clock_preflight_refused (via None anchor -> predicate False at 6950)", 1),
    # base line 6911: Residual form: the kernel frequency word is the same at R0 and at the author anch...
    row("joulewise/arm_readiness.py", "_clock_probe_predicate_passes",
        "readiness_clock_preflight_refused", 3),
    # base line 6920: kernel_clock.frequency_gate: the stored drift rate (plus 0.25 ppm margin) over th...
    row("joulewise/arm_readiness.py", "_clock_probe_predicate_passes",
        "readiness_clock_preflight_refused", 4),
    # base line 6923: Legacy, no anchor_check_version: |REALTIME minus MONOTONIC_RAW change| from R0 to...
    row("joulewise/arm_readiness.py", "_clock_probe_predicate_passes",
        "readiness_clock_preflight_refused", 5),
    # base line 6947: Two read skews (R0 and anchor) are at most 1 ms each.
    row("joulewise/arm_readiness.py", "_clock_probe_predicate_passes",
        "readiness_clock_preflight_refused", 6),
    # base line 6965: The live boot session equals the receipt's boot session (no reboot since T-0). Th...
    row("joulewise/arm_readiness.py", "_clock_probe_predicate_passes",
        "readiness_clock_preflight_refused", 7),
    # base line 6981: Live at arm: the kernel frequency is unchanged since R0, and REALTIME minus MONOT...
    row("joulewise/arm_readiness.py", "_clock_probe_predicate_passes",
        "readiness_clock_preflight_refused", 8),
    # base line 10049: the kernel frequency word captured at R0 (ntp_adjtime) gives a drift bound h_max...
    row("joulewise/arm_readiness.py", "_authenticate_go_t0_evidence",
        "launch_go_receipt_invalid:t0_evidence kernel frequency", 1),
    # base line 771: The recorded R0 CLOCK_REALTIME/CLOCK_MONOTONIC_RAW pair was read more than 1 ms a...
    row("joulewise/arm_readiness_evidence_t0.py", "_captured_clock_reference",
        "evidence_author_t0_clock_attestation_underivable", 1),
    # base line 776: The R0 kernel frequency probe (ntp_adjtime modes=0 record and raw timex bytes) is...
    row("joulewise/arm_readiness_evidence_t0.py", "_captured_clock_reference",
        "evidence_author_t0_clock_attestation_underivable", 2),
    # base line 1147: The live anchor values are non-integer, or the read skew is negative.
    row("joulewise/arm_readiness_evidence_t0.py", "_sample_anchor",
        "evidence_author_t0_clock_attestation_underivable", 1),
    # base line 1258: Frequency gate: the R0 kernel drift rate |f| × the longest sampler stream + h exc...
    row("joulewise/arm_readiness_evidence_t0.py", "_derive_clock_attestation",
        "evidence_author_t0_clock_attestation_underivable", 3),
    # base line 1260: The R0 or live kernel frequency probe is invalid or unreadable, or the residual c...
    row("joulewise/arm_readiness_evidence_t0.py", "_derive_clock_attestation",
        "evidence_author_t0_clock_attestation_underivable", 4),
    # base line 1264: Clock step: the drift-corrected residual of (REALTIME−MONOTONIC_RAW) movement bet...
    row("joulewise/arm_readiness_evidence_t0.py", "_derive_clock_attestation",
        "evidence_author_t0_clock_attestation_underivable", 5),
    # base line 1266: The kernel frequency-correction word read live differs from R0's. That means time...
    row("joulewise/arm_readiness_evidence_t0.py", "_derive_clock_attestation",
        "evidence_author_t0_kernel_frequency_changed", 1),
    # base line 1269: The live author anchor pair was read more than 1 ms apart.
    row("joulewise/arm_readiness_evidence_t0.py", "_derive_clock_attestation",
        "evidence_author_t0_clock_attestation_underivable", 6),
    # base line 49: wall clock after the log read >= wall clock before it
    row("joulewise/corecaptured_loop.py", "count_spawns",
        "ValueError clock moved backward during the corecaptured log read", 1),
    # base line 70: ntp_adjtime returned status 0..5 with errno 0 and modes 0.
    row("joulewise/kernel_clock.py", "validate_probe",
        "ValueError kernel frequency read failed or was not read-only", 1),
    # base line 970: REALTIME/RAW pair read within 1 ms
    row("joulewise/t0_rehearsal.py", "evaluate_g4",
        "G4 R0 anchor read skew exceeds 1 ms", 1),
    # base line 1002: both RAW anchors present as ints
    row("joulewise/t0_rehearsal.py", "evaluate_g4",
        "G4 published clock endpoint is not an integer", 1),
    # base line 1038: REALTIME-RAW movement net of the applied slew <= 5 ms
    row("joulewise/t0_rehearsal.py", "evaluate_g4",
        "G4 RAW anchor residual exceeds 5 ms or differs", 1),
    # base line 1043: REALTIME-RAW movement <= 5 ms
    row("joulewise/t0_rehearsal.py", "evaluate_g4",
        "G4 RAW anchor delta exceeds 5 ms (legacy)", 1),
    # base line 1049: both anchor reads within 1 ms
    row("joulewise/t0_rehearsal.py", "evaluate_g4",
        "G4 RAW anchor read skew exceeds 1 ms", 1),
    # base line 758: ntp_adjtime frequency word is identical before and after the SNTP batch.
    row("scripts/capture_t0_step.py", "_arm_reference",
        "ValueError kernel frequency changed during R0 batch (retried, then L763)", 1),
    # base line 798: kern.bootsessionuuid is unchanged since context load.
    row("scripts/capture_t0_step.py", "_capture_step_with_dependencies",
        "evidence_author_t0_capture_boot_probe_failed (boot changed before command)", 1),
    # base line 809: Frequency word after OFF equals the word read with R0.
    row("scripts/capture_t0_step.py", "_capture_step_with_dependencies",
        "ValueError kernel frequency changed during R0; fresh R0 required", 1),
    # base line 818: 3.7 ms + (|f| + 0.25 ppm) x longest sampler stream <= 5 ms, with f read by ntp_ad...
    row("scripts/capture_t0_step.py", "_capture_step_with_dependencies",
        "ValueError R0 kernel frequency exceeds the stream clock budget", 1),
    # base line 840: Boot session is unchanged across the step.
    row("scripts/capture_t0_step.py", "_capture_step_with_dependencies",
        "evidence_author_t0_capture_boot_probe_failed (boot changed during command)", 1),
    # base line 215: Boot unchanged across preflight.
    row("scripts/ed_session/capture_t0_anchor_positive_control.py", "run_control",
        "NotDischarged g10_preflight_boot_changed", 1),
    # base line 227: Boot unchanged at the before stamp.
    row("scripts/ed_session/capture_t0_anchor_positive_control.py", "run_control",
        "NotDischarged g10_preflight_boot_changed (before)", 1),
    # base line 233: Kernel frequency word now equals R0's.
    row("scripts/ed_session/capture_t0_anchor_positive_control.py", "run_control",
        "NotDischarged pre_on_kernel_frequency_changed", 1),
    # base line 236: R0 kernel frequency is within the stream clock budget.
    row("scripts/ed_session/capture_t0_anchor_positive_control.py", "run_control",
        "NotDischarged pre_on_kernel_frequency_gate_failed", 1),
    # base line 240: R0 boot equals the current boot (anchor comparable).
    row("scripts/ed_session/capture_t0_anchor_positive_control.py", "run_control",
        "NotDischarged r0_boot_mismatch", 1),
    # base line 245: Drift-corrected anchor residual R0 to now is <=5 ms before ON.
    row("scripts/ed_session/capture_t0_anchor_positive_control.py", "run_control",
        "NotDischarged author_sequence_already_above_anchor_bound", 1),
    # base line 272: Boot unchanged during polling.
    row("scripts/ed_session/capture_t0_anchor_positive_control.py", "run_control",
        "NotDischarged boot_changed (poll)", 1),
    # base line 287: After ON, the drift-corrected anchor moved >5 ms within the timeout.
    row("scripts/ed_session/capture_t0_anchor_positive_control.py", "run_control",
        "NotDischarged anchor_movement_at_or_below_5ms", 1),
    # base line 289: R0-to-after residual is >5 ms, so the author should refuse.
    row("scripts/ed_session/capture_t0_anchor_positive_control.py", "run_control",
        "NotDischarged changed_author_sequence_not_above_bound", 1),
    # base line 314: Boot unchanged across the author run.
    row("scripts/ed_session/capture_t0_anchor_positive_control.py", "run_control",
        "NotDischarged author_boot_changed", 1),
    # base line 107: G4 clock mechanics recomputed from raw R0/R1 reference and RAW-clock endpoints
    row("scripts/harvest_v5_qualification.py", "harvest",
        "g4_not_passed", 1),
    # base line 3049: kern.bootsessionuuid read by the C4 probe is unchanged between hard checks.
    row("scripts/run_night.py", "bind_until_quiet.hard_done",
        "night_refused_boot_clock 'boot identity changed during binding'", 1),
    # base line 3051: The wall clock read by C4 never goes backwards between hard checks.
    row("scripts/run_night.py", "bind_until_quiet.hard_done",
        "night_refused_boot_clock 'wall clock rolled back during binding'", 1),
    # base line 3148: The boot identity is the same before and after a CPU sample.
    row("scripts/run_night.py", "bind_until_quiet",
        "night_refused_boot_clock 'sample boot identity changed'", 1),
    # base line 3180: At GO the wall clock is not behind the last C4 reading and not past the bind dead...
    row("scripts/run_night.py", "bind_until_quiet",
        "night_refused_boot_clock 'wall clock moved outside final-check/bind bounds'", 1),
    # base line 556: 3.60 ms + 0.10 ms + (|kernel frequency word| + 0.25 ppm) x longest planned stream...
    row("scripts/write_v5_qualification_plan.py", "write_qualification",
        "kernel_frequency_gate_exceeded", 1),
)

# Proxy rows on paths block 5 no longer runs that this module's direct
# measurement replaces (configs/gates/physics_rows.json, "retired_proxy").
SUPERSEDES: tuple[tuple[str, str, str, int], ...] = (
    # base line 108: Re-exports the exact systemsetup 'Network Time: Off' stdout wording that comparat...
    row("joulewise/arm_readiness.py", "<module>",
        "EXPECTED_NETWORK_TIME_OFF_STDOUT / network_time_off_stdout_admitted", 1),
    # base line 968: The clock row requires independent_clock_attestation true, from an operator attes...
    row("joulewise/arm_readiness.py", "<module>",
        "predicate clock.correct_and_prior_state.v1", 1),
    # base line 971: Requires a fresh probe reporting network_time == 'off', a settings string.
    row("joulewise/arm_readiness.py", "<module>",
        "predicate clock.network_time_off.v1", 1),
    # base line 5893: requires_t0_frequency_gate decides from registry row text (CLOCK_ATTESTATION in t...
    row("joulewise/arm_readiness.py", "requires_t0_frequency_gate",
        "(no raise; registry lookup errors propagate: readiness_row_registry_mismatch)", 1),
    # base line 6433: CLOCK_ATTESTATION probe's t_stream_max_s (longest sampler stream allowed by the c...
    row("joulewise/arm_readiness.py", "_authenticate_generic_evidence_item",
        "readiness_evidence_digest_mismatch", 1),
    # base line 6868: Four receipt booleans must be true: independent_clock_attestation, reference_quor...
    row("joulewise/arm_readiness.py", "_clock_probe_predicate_passes",
        "readiness_clock_preflight_refused", 1),
    # base line 6883: The NTP reference bound is at most 0.5 s and the |comparison delta| to the networ...
    row("joulewise/arm_readiness.py", "_clock_probe_predicate_passes",
        "readiness_clock_preflight_refused", 2),
    # base line 7036: On the OPERATOR_ATTESTATION route, the clock row passes when the receipt says pri...
    row("joulewise/arm_readiness.py", "_predicate_passes",
        "readiness_clock_preflight_refused", 1),
    # base line 7168: The CLOCK_PROBE receipt says network_time == 'off' and fresh_probe is true.
    row("joulewise/arm_readiness.py", "_evaluate_rows",
        "readiness_clock_preflight_refused (row clock.network_time_off)", 1),
    # base line 932: refuses if the launch recipe or stage graph JSON contains the byte strings setusi...
    row("joulewise/arm_readiness_evidence.py", "_derive_doctrine_pin",
        "evidence_author_doctrine_pin_underivable", 1),
    # base line 952: runbook §5A does not contain ten exact normalized sentences stating that network...
    row("joulewise/arm_readiness_evidence.py", "_derive_doctrine_pin",
        "evidence_author_doctrine_pin_underivable", 2),
    # base line 965: any sentence in runbook sections 5-12 that the regexes read as enabling network t...
    row("joulewise/arm_readiness_evidence.py", "_derive_doctrine_pin",
        "evidence_author_doctrine_pin_underivable", 3),
    # base line 733: Fewer than two sntp servers answered, for R0 (via 772) or R1 (via 1185). Absolute...
    row("joulewise/arm_readiness_evidence_t0.py", "_reference_agreement",
        "evidence_author_t0_clock_attestation_underivable", 1),
    # base line 737: The sntp offset±uncertainty intervals do not intersect (the servers disagree).
    row("joulewise/arm_readiness_evidence_t0.py", "_reference_agreement",
        "evidence_author_t0_clock_attestation_underivable", 2),
    # base line 742: The absolute wall-clock offset bound from sntp exceeds 0.5 s.
    row("joulewise/arm_readiness_evidence_t0.py", "_reference_agreement",
        "evidence_author_t0_clock_attestation_underivable", 3),
    # base line 779: The pack requires the frequency gate, but the R0 capture carries no t_stream_max_s.
    row("joulewise/arm_readiness_evidence_t0.py", "_captured_clock_reference",
        "evidence_author_t0_clock_attestation_underivable", 3),
    # base line 1185: R1 live sntp quorum, interval intersection and 0.5 s bound (raised inside _refere...
    row("joulewise/arm_readiness_evidence_t0.py", "_fresh_clock_reference_batch",
        "evidence_author_t0_clock_attestation_underivable", 1),
    # base line 1219: The network-time-OFF (systemsetup) capture exited nonzero. This proxies 'network...
    row("joulewise/arm_readiness_evidence_t0.py", "_derive_clock_attestation",
        "evidence_author_t0_clock_attestation_underivable", 1),
    # base line 1221: The OFF capture argv is not exactly `sudo … systemsetup -setusingnetworktime off`...
    row("joulewise/arm_readiness_evidence_t0.py", "_derive_clock_attestation",
        "evidence_author_t0_clock_attestation_underivable", 2),
    # base line 1320: CLOCK_PROBE row: the OFF capture exited nonzero.
    row("joulewise/arm_readiness_evidence_t0.py", "_derive_clock_probe",
        "evidence_author_t0_clock_probe_underivable", 1),
    # base line 1336: The OFF receipt is unreadable or a symlink, has a window/plan mismatch or another...
    row("joulewise/arm_readiness_evidence_t0.py", "_derive_clock_probe",
        "evidence_author_t0_clock_probe_underivable", 2),
    # base line 71: The SNTP argv carries no -s/-S/-a, so the observer cannot step the clock.
    row("joulewise/clock_reference.py", "assert_report_only_argv",
        "ValueError sntp clock-setting flag is forbidden", 1),
    # base line 68: Receipt schema, OFF argv, exit 0, stdout in the admitted Off statements, stderr i...
    row("joulewise/network_time_off.py", "admit",
        "ValueError network time OFF receipt not admitted", 1),
    # base line 111: The OFF setter succeeded with admitted wording.
    row("joulewise/network_time_off.py", "set_network_time_off",
        "admit(receipt) after running OFF (setter failed, sudo refused, timeout, or wording)", 1),
    # base line 121: Receipt boot_id equals the current boot.
    row("joulewise/network_time_off.py", "seconds_since_receipt",
        "ValueError OFF receipt belongs to a different boot", 1),
    # base line 129: Both epoch and monotonic elapsed time since the receipt are >= 600 s.
    row("joulewise/network_time_off.py", "seconds_since_receipt",
        "ValueError OFF receipt has not settled for 600 seconds on both clocks", 1),
    # base line 1035: kernel slew rate constant across T-0
    row("joulewise/t0_rehearsal.py", "evaluate_g4",
        "G4 R0-to-author kernel frequency word changed", 1),
    # base line 1041: 3.7 ms + (ppm+0.25)*T_stream <= 5 ms
    row("joulewise/t0_rehearsal.py", "evaluate_g4",
        "G4 R0 kernel frequency exceeds the stream clock budget", 1),
    # base line 1074: systemsetup Off exit 0, exact argv, admitted stdout string
    row("joulewise/t0_rehearsal.py", "evaluate_g4",
        "G4 first exact-Off not mechanically green", 1),
    # base line 1084: OFF receipt same boot and at least 600 s old on both clocks
    row("joulewise/t0_rehearsal.py", "evaluate_g4",
        "seconds_since_receipt: different boot / not settled 600 s", 1),
    # base line 1100: Off exit 0, argv, stdout string
    row("joulewise/t0_rehearsal.py", "evaluate_g4",
        "G4 second exact-Off not mechanically green", 1),
    # base line 1602: restore stage records network_time OFF and stand_down true
    row("joulewise/t0_rehearsal.py", "evaluate_g9",
        "G9 restore-ON is forbidden", 1),
    # base line 1605: setter stdout reads 'network time is already off'
    row("joulewise/t0_rehearsal.py", "evaluate_g9",
        "G9 restore lacks already-OFF setter witness", 1),
    # base line 648: systemsetup setter stdout normalises to 'setusingnetworktime: off' or 'network ti...
    row("scripts/capture_t0_step.py", "_validate_result",
        "evidence_author_t0_capture_result_invalid (E-5 stdout not the Off postcondition)", 1),
    # base line 763: Within 25 tries/120 s, collect_clock_reference exits 0 and the SNTP legs pass sch...
    row("scripts/capture_t0_step.py", "_arm_reference",
        "evidence_author_t0_capture_result_invalid (arm reference did not converge within 120 s)", 1),
    # base line 771: The OFF setter ran, exited 0 with admitted wording, and the receipt was newly cre...
    row("scripts/capture_t0_step.py", "_arm_reference",
        "set_network_time_off in finally: FileExistsError or admit() ValueError becomes result_invalid at L837", 1),
    # base line 822: clock-disable step re-reads the OFF receipt.
    row("scripts/capture_t0_step.py", "_capture_step_with_dependencies",
        "network_time_off.read_receipt (symlink/absent/not admitted/plan-window mismatch) becomes result_invalid", 1),
    # base line 832: OFF receipt is admitted, from the same boot, and >=600 s old on both epoch and mo...
    row("scripts/capture_t0_step.py", "_capture_step_with_dependencies",
        "read_receipt + seconds_since_receipt before ledger steps becomes result_invalid", 1),
    # base line 191: OFF receipt plan/window identity
    row("scripts/check_v5_arm_abort.py", "observe",
        "network_time_off.read_receipt", 1),
    # base line 192: OFF receipt boot equals ARM boot
    row("scripts/check_v5_arm_abort.py", "observe",
        "off_boot", 1),
    # base line 199: ledger-readiness start is between first boundary and now, same boot
    row("scripts/check_v5_arm_abort.py", "observe",
        "off_settle_boundary", 1),
    # base line 201: 600 s between OFF receipt and settled ledger use on both clocks
    row("scripts/check_v5_arm_abort.py", "observe",
        "off_settle", 1),
    # base line 263: ON setter stdout normalises to 'setusingnetworktime: on' or 'network time is alre...
    row("scripts/ed_session/capture_t0_anchor_positive_control.py", "run_control",
        "NotDischarged network_time_on_not_observed", 1),
    # base line 349: OFF setter succeeded with admitted wording, receipt re-read, kernel probe after O...
    row("scripts/ed_session/capture_t0_anchor_positive_control.py", "run_control",
        "off_receipt_missing_or_invalid (OFF in finally not admitted, or after-OFF probe invalid)", 1),
    # base line 457: All stamps same boot with skew <=1 ms, monotonic order, OFF after the control and...
    row("scripts/ed_session/capture_t0_anchor_positive_control.py", "verify_g10_custody",
        "NotDischarged g10_boot_or_order", 1),
    # base line 696: An OFF receipt exists under the pack plan id and window id
    row("scripts/harvest_v5_g2b_window.py", "harvest",
        "network_time_off.read_receipt (raise)", 1),
    # base line 712: Each capture's battery 'pre' wall and monotonic stamps fall after the OFF receipt...
    row("scripts/harvest_v5_g2b_window.py", "harvest",
        "network_time_off_not_settled (RECOVER)", 1),
    # base line 272: re-runs sudo -n systemsetup -setusingnetworktime off and requires stdout 'network...
    row("scripts/produce_t0_rehearsal_bundle.py", "observe_network_time_off",
        "OFF observation unavailable", 1),
    # base line 377: OFF receipt exists with matching plan/window id
    row("scripts/produce_t0_rehearsal_bundle.py", "lifecycle",
        "network_time_off.read_receipt", 1),
    # base line 378: 600 s elapsed since the OFF receipt on both clocks, same boot
    row("scripts/produce_t0_rehearsal_bundle.py", "lifecycle",
        "OFF receipt has not settled for 600 seconds / different boot", 1),
    # base line 565: restore stage record says network_time OFF and stand_down true
    row("scripts/produce_t0_rehearsal_bundle.py", "assemble",
        "restore-ON is forbidden", 1),
    # base line 3354: The pre-staged OFF receipt under <pack_id>/arm_readiness.t0.inputs/ has the exact...
    row("scripts/run_night.py", "_admit_network_time_off",
        "ValueError from network_time_off.read_receipt/admit on TRANSACTION_PACK: 'OFF receipt is a symlink', 'network time OFF receipt not admitted', 'invalid OFF receipt clock', 'OFF receipt window/plan mismatch'", 1),
    # base line 3356: Runs sudo -n systemsetup -setusingnetworktime off, then requires exit 0 and stdou...
    row("scripts/run_night.py", "_admit_network_time_off",
        "ValueError 'network time OFF receipt not admitted' (network_time_off.set_network_time_off -> admit), non-pack path", 1),
    # base line 3368: The current boot matches the receipt's boot, and at least 600 s have passed since...
    row("scripts/run_night.py", "_admit_network_time_off",
        "ValueError 'OFF receipt belongs to a different boot' / 'OFF receipt has not settled for 600 seconds on both clocks' / 'invalid admission clock' (network_time_off.seconds_since_receipt)", 1),
    # base line 4053: The OFF receipt is admitted and has settled 600 s on both clocks on the same boot...
    row("scripts/run_night.py", "run_night",
        "night_probe_error from _admit_network_time_off at launch (every non-DIAGNOSTIC, non-evidence plan, including TRANSACTION_PACK)", 1),
    # base line 173: OFF receipt plan/window identity
    row("scripts/v5_s1_desk_closeout.py", "closeout",
        "network_time_off.read_receipt", 1),
    # base line 175: OFF receipt boot id equals GO boot
    row("scripts/v5_s1_desk_closeout.py", "closeout",
        "OFF receipt boot mismatch", 1),
    # base line 184: desk-time setter stdout 'already off'
    row("scripts/v5_s1_desk_closeout.py", "closeout",
        "OFF observation unavailable (producer.observe_network_time_off)", 1),
    # base line 211: the observed_max_effective_bound allowance, a historical block-3 number read from...
    row("scripts/write_v5_qualification_plan.py", "size_window",
        "clock_bound_exceeded", 1),
)
