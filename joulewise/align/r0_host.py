"""Read-only R0 host probes. No model imports or downloads.

R0's only authority is its final verdict over the complete sample series.
A sampler stall, a judged window longer than the limit, a census fault or a
contention flag, latched at any time from the first admission to the end of
the run, gives exit 2 and withheld publication (QuietGuard.finish, then
QuietGuard.verify_publication).

The verdict's windows come only from that series: the startup and daemon
samples, then the read each publication census takes at run end. It judges
every window the sliding rule defines over the series, including the one
ending at the final read. At every sample it also runs the exact check: for
each earlier sample at most INTERVAL_S before it, a contaminant whose
counter grew by at least the limit times INTERVAL_S is flagged. Each sample
is judged once, when it first ends a window, and a flag is never withdrawn,
so adding samples cannot remove a flag. Each sample also gets the proven
check (lead P1). Against each earlier point of the same process's life,
whether a reading or its birth bound with a zero counter, it takes the
growth less one centisecond over the largest span the reads allow. It splits
that span into k windows of at most 30 s, and flags if growth / k reaches
the limit times 30 s: one of those windows held at least that much. Scope
is sticky (lead Q1). A (pid, start) that any read identified is in scope for
its whole retained history. At the final verdict, every such process is
judged over all pairs of its points, whichever read ends a pair. Readings
of a process are kept whether or not the read identified it. They come from
every read R0 takes, admission reads included (lead R1). That evidence can
only add a withhold. Admission reads still never open or extend a window. Admission windows reproduce the
admitted L3 guard's flags; they can add a flag, never supply an opening to
the verdict.

Adding a reading of a process, from any read, can only add withhold
evidence (lead S1). Every judgement uses every pair (lead S2). Each daemon
or admission read that closes a window is also paired with every earlier
opening less than 30 s before the window's own, under the same rule. With
the window, those are the pairs no read splits into two parts of at least
30 s. A longer pair holds such a read, and a rate above the limit over the
pair puts one part above it. So an added reading keeps every judged pair or
splits it into two judged ones. P1 runs over every pair of each process's
history at each admission as well as at the final verdict.

The final verdict is authoritative (lead T1). It judges every pair of each
in-scope process's readings, with no bound on the span, under the admitted
rate rule (``QuietGuard._pair_history``). Runs of unchanged readings are
kept as their first and last, and every read between them is restored from
the read index. A newcomer is also judged from its birth bound to each
reading. A read added between two readings therefore never removes their
pair, and a read that splits a window no longer splits these judgements.
The birth bound only narrows (lead T2). Its zero is the latest instant every
reading allows as the earliest birth, so an added sighting cannot move it
earlier. The stall rule stays coverage, not evidence: a daemon read inside
a gap lifts it.

Foreground admission is advisory. It saves work that the final verdict
would discard; it cannot make a run pass. Its last act before it returns
clear re-reads the sampler's latch, the age of the newest sample (at most
QuietGuard.MAX_WINDOW_S) and any windows completed while its own probes ran.
The sampler runs concurrently, so a fault can still latch after that read
and before or during the work it admits. That race is accepted: the work
runs, and the final verdict withholds the run.

Window and interval arithmetic uses the monotonic clock. Wall time labels
samples. Darwin's printed process start (lstart) is a wall-clock label and
the only evidence of a birth time; it is converted with the wall offset
measured by the read that listed it. A window in which the wall and
monotonic clocks move apart by more than WALL_DIVERGENCE_LIMIT_NS is
flagged, which withholds publication, so no unflagged window relies on a
conversion across a wall step.

A process the series first lists after its first read has one birth bound,
fixed by that first sighting and never recomputed. It was born after the
last series read that did not list it and before the first that did. Its
printed start second can only narrow that bracket. That second is converted
once, with the largest wall offset either bracket read measured, so a clock
change between the reads cannot date the birth later than it was. A zero
counter is inferred only at the bound's earliest instant, so contention is
claimed only if it holds for every birth time inside it. The exact check
and the lifetime check use the same bound. Every counter reading stays a
lower bound for everything inferred after it: an absence after a reading,
or a later reading of the same start second, proves nothing.

KNOWN LIMITATION R0-CLOCK. R0 assumes a stable wall clock: if wall - mono
varies by more than 1 ms over the series, it withholds (clock_unstable).
Within a stable clock, verdicts within one centisecond of 1.50 CPU-s, and
workloads whose sampled observations are identical, are not
distinguishable; R0 refuses, never publishes, in the ambiguous case. The
precondition sees only the offsets its reads measure, so a wall excursion
that returns between two reads is indistinguishable from a stable clock.
"""
from __future__ import annotations

import bisect
from dataclasses import asdict, dataclass, replace
from datetime import datetime, timedelta, timezone
from fnmatch import fnmatchcase
import hashlib
import json
import math
import os
from pathlib import Path
import re
import shutil
import subprocess
import threading
import time

from joulewise import measurement_liveness
from joulewise.agent_identity import AGENT_PREFIXES, identify as identify_agent
from joulewise.measurement_liveness import census, custody_parent, Refused, ADDITIONAL_PARENTS_ENV
from joulewise.night_gate import AGENT_CENSUS_PATTERN, ProbeResult, decide_census
from joulewise.prewindow import PS_ARGV
from joulewise import prewindow
from joulewise.hazards import contention
from joulewise.hazards.base import Stamp
from joulewise.align.r0_step import (ProfileRefused, profile_config as fixed_profile,
                                     rank_response, step_budget as fixed_budget)
from joulewise.align.apple.smc_enumeration import rank as classify_smc


# The literal pattern must not match a simultaneous census's command line.
_AGENT_APP_PATTERN = r"/([c]laude|[c]odex)[.]app/Contents/MacOS/"
R0_AGENT_CENSUS_ARGV = ("/usr/bin/pgrep", "-a", "-lf", "-i", _AGENT_APP_PATTERN + "|" + AGENT_CENSUS_PATTERN)
_AGENT_CANDIDATE = re.compile(R0_AGENT_CENSUS_ARGV[-1], re.I)
_AGENT_APP = re.compile(_AGENT_APP_PATTERN, re.I)
_CHAIN_NAMES = tuple(stem + suffix
                     for stem in ("run_campaign", "run_night", "window-chain", "window_chain",
                                  "align_r1_rehearsal", "align_r0_checks", "run_b5_analysis", "chain", "powermetrics")
                     for suffix in ("", ".py", ".sh", ".zsh"))
_CONTAMINANT_NAMES = tuple(name.casefold() for name in prewindow.CONTAMINANTS.split("|"))
_ADMITTED_CONTAMINANTS = re.compile(prewindow.CONTAMINANTS, re.I)
_CPU_LIMIT_NUM, _CPU_LIMIT_DEN = prewindow.CPU_LIMIT_PERCENT.as_integer_ratio()


def profile_config(value=None):
    """D3 adaptive profile; keep the retired fixed-profile fit diagnostic intact."""
    if value is not None and not isinstance(value, dict):
        return fixed_profile(value)  # existing typed refusal
    supplied = dict(value or {})
    # D3: measured post-step settle median ~930 s, maximum 1,038 s => 1,200 s cap.
    maximum = supplied.pop("idle_max_seconds", 1200)
    profile = fixed_profile(supplied)
    if type(maximum) is not int or maximum < profile["idle_seconds"]:
        raise ProfileRefused("smc_step.invalid_duration", "idle_max_seconds must be an integer >= idle_seconds")
    return {**profile, "idle_max_seconds": maximum}


def step_budget(value=None):
    profile = profile_config(value)
    # Budget the maximum capture; fixed_budget retains the existing +600 s
    # execution margin. Erratum 2: measured journal 95,467,641 bytes /1,800
    # one-Hz slots =53,037.58 bytes/slot; ceil to a whole byte for planning.
    maximum = {k: v for k, v in profile.items() if k != "idle_max_seconds"}
    maximum["idle_seconds"] = profile["idle_max_seconds"]
    budget = fixed_budget(maximum)
    per_slot = math.ceil(95_467_641 / 1800)
    return {**budget, "profile": profile, "journal_bytes_per_slot_estimate": per_slot,
            "journal_bytes_estimate": budget["capture_seconds"] * per_slot,
            "journal_estimate_note": "Measured 95,467,641 bytes /1,800 slots, rounded up; verify after enumeration."}


def _tool_env():
    return {**os.environ, "LC_ALL": "C", "TZ": "UTC"}


def command(argv):
    result = subprocess.run(argv, capture_output=True, text=True, timeout=30,
                            env=_tool_env())
    if result.returncode:
        raise RuntimeError(f"{argv[0]} exit {result.returncode}: {result.stderr.strip()}")
    return result.stdout


def _installed_night_agents():
    fs = measurement_liveness.census_fs
    directory = fs(Path("~"), "home")
    entries = measurement_liveness.census_entries
    for name in ("library", "launchagents"):
        directory = entries(directory).get(name)
        if directory is None:
            return []
    return sorted(str(entry) for key, entry in entries(directory).items()
                  if fnmatchcase(key, "com.joulewise.night*.plist"))


def _with_peak_counters(snapshot):
    corrected = {key: {**row, "cumulative_cpu_seconds": row["peak_cpu_seconds"]}
                 for key, row in snapshot.rows.items() if "peak_cpu_seconds" in row}
    return replace(snapshot, rows={**snapshot.rows, **corrected}) if corrected else snapshot


def _normalize_process_name(value):
    value = value.strip()
    if value.startswith("(") and value.endswith(")"):
        value = value[1:-1]
    return value.rsplit("/", 1)[-1].casefold()


def _matches_process_name(name, patterns, *, prefixes=False):
    return (name in patterns or (prefixes and name.startswith(patterns))
            or (len(name.encode("utf-8", "surrogateescape")) == 16
                and any(pattern.startswith(name) for pattern in patterns)))


def _require_clear_sighting(pid, command, receipt, *, argv=None, line=None):
    """Classify all names on one captured row before any follow-up query."""
    executable = _normalize_process_name(command)
    tokens = tuple(argv.split()) if argv else ()
    names = (executable, *map(_normalize_process_name, tokens[1:]))
    agent = (_matches_process_name(executable, AGENT_PREFIXES, prefixes=True) or _AGENT_APP.search(command)
             or (argv and _AGENT_CANDIDATE.search(argv) and identify_agent(command, tokens) == "agent"))
    chain = (any(_matches_process_name(name, _CHAIN_NAMES) for name in names) and pid != os.getpid())
    for field, matched in (("named_agents", agent), ("chains", chain)):
        if matched:
            receipt.setdefault(field, []).append(line or f"{pid} {command}")
            raise Refused(f"machine occupied or census indeterminate: {field}, pid {pid} process {argv or command}")
    # The admitted census also matches within executable names and argv
    # paths. Inspect the original spelling to retain directory components.
    return (any(_matches_process_name(name, _CONTAMINANT_NAMES, prefixes=True) for name in names)
            or _ADMITTED_CONTAMINANTS.search(argv or command) is not None)


@dataclass(frozen=True)
class _ArgumentsRead:
    started_ns: int
    finished_ns: int
    pids: frozenset[int]
    contenders: frozenset[int]


@dataclass(frozen=True, kw_only=True)
class _AccountingRead(contention.Snapshot):
    admitted_start_ns: int
    admitted_finish: Stamp

    @property
    def admitted_midpoint_ns(self):
        return (self.admitted_start_ns + self.admitted_finish.monotonic_ns) // 2

    def admitted_endpoint(self):
        start = Stamp(self.started.wall_ns, self.admitted_start_ns, self.admitted_start_ns)
        return replace(self, started=start, finished=self.admitted_finish)


def _read_finished_ns(read):
    return read.finished_ns if isinstance(read, _ArgumentsRead) else read.finished.monotonic_ns


# Darwin prints lstart in whole seconds: the floor of the start time.
_START_RESOLUTION_NS = 1_000_000_000


def _wall_offset_ns(read):
    return read.started.wall_ns - read.started.monotonic_ns


def _birth_floor_ns(row, read):
    """Monotonic time of ``row``'s printed start second, on the clock of the read that listed it."""
    return int(row["start_epoch_s"]) * 1_000_000_000 - _wall_offset_ns(read)


def _born_after(row, read, monotonic_ns, reference):
    """Whether ``row``'s printed start second proves a birth after ``monotonic_ns``.

    ``read`` listed the row. ``reference`` is an accounting read taken no
    later than ``monotonic_ns``. Any wall step between the two shows as a
    difference of their offsets, and the start must clear the instant by
    that much. Nothing is proven without a reference or by a start dated
    after its own listing.
    """
    if reference is None:
        return False
    shift = abs(_wall_offset_ns(read) - _wall_offset_ns(reference))
    return monotonic_ns + shift < _birth_floor_ns(row, read) <= read.finished.monotonic_ns


# Wall and monotonic time may drift apart by slew within a window, not more.
WALL_DIVERGENCE_LIMIT_NS = 500_000_000
# The series' clock-stability precondition (lead K1): every series read's
# wall - monotonic offset within 1 ms of every other, or R0 withholds as
# clock_unstable. Network time is off on a measurement host.
CLOCK_STABILITY_LIMIT_NS = 1_000_000


def _wall_divergence_ns(reads):
    """How far the wall clock moved against the monotonic clock across a window's accounting reads."""
    offsets = [stamp.wall_ns - stamp.monotonic_ns for read in reads if isinstance(read, contention.Snapshot)
               for stamp in (read.started, read.finished, getattr(read, "admitted_finish", read.finished))]
    return max(offsets) - min(offsets) if offsets else 0


def _exact_cpu_evidence(identity, row, baseline, basis):
    """Charge proven counter growth to a full 30 s, including ties at the limit."""
    interval_ns = prewindow.INTERVAL_S * 1_000_000_000
    growth_cs = round(row["cumulative_cpu_seconds"] * 100) - round(baseline * 100)
    if growth_cs * 1_000_000_000 * _CPU_LIMIT_DEN >= _CPU_LIMIT_NUM * interval_ns:
        return {"pid": identity[0], "command": row["command"], "start": identity[1],
                "cpu_s_per_s": growth_cs * 10_000_000 / interval_ns, "basis": basis}


def _exact_window_evidence(earlier, later):
    """Growth between two readings of the same identity, charged to 30 s.

    An identity missing from ``earlier`` gets no zero here: its only zero
    is its birth bound's (``_BirthBound``), never an absence read after a
    reading of it.
    """
    measured = []
    for identity, row in later.rows.items():
        before = earlier.rows.get(identity)
        if (before is not None and "peak_cpu_seconds" not in before
                and (row["contaminant"] or before["contaminant"])):
            evidence = _exact_cpu_evidence(identity, row, before["cumulative_cpu_seconds"],
                                           "CPU between two samples at most 30 s apart, charged to 30 s")
            if evidence:
                measured.append(evidence)
    return measured


def _stamp_offsets_ns(read):
    return [stamp.wall_ns - stamp.monotonic_ns
            for stamp in (read.started, read.finished, getattr(read, "admitted_finish", read.finished))]


@dataclass(frozen=True)
class _BirthBound:
    """Where a process the series first saw at ``sighted`` was born, in monotonic ns.

    It was born after the last series sample that did not list it and
    before the first accounting read that did (``sighted``). That sample's
    absence is its accounting table (at the read's midpoint, as E1 places
    samples) or, later, the arguments table read with it, when that lists
    no process with the PID (from the table's start). The absence is an
    independent zero. The printed start second can only narrow the bracket
    from inside it. It is converted once, when the process is first seen,
    with the largest wall offset measured from the absence sample to the end
    of the sighting's accounting read; no offset measured after that read
    enters. No later read converts it again. ``printed_ns`` is that
    conversion. The series' clock-stability precondition bounds only the
    offsets its reads measure; R0 assumes the offset at birth lies within
    them (KNOWN LIMITATION R0-CLOCK).
    """
    absent_ns: int
    absent_started_ns: int
    sighted_midpoint_ns: int
    sighted_finished_ns: int
    printed_ns: int

    @property
    def zero_ns(self):
        """The exact check's zero: the latest instant every reading allows as the earliest birth.

        Lead T2: the process was born after the absence and no earlier than
        its printed start second, which counts whenever the sighting read
        ended no earlier than it. An added reading can only narrow this:
        a later absence moves the zero later, an earlier sighting leaves it.
        """
        if self.printed_ns <= self.sighted_finished_ns:
            return max(self.absent_ns, self.printed_ns)
        return self.absent_ns

    @property
    def lifetime_floor_ns(self):
        """The lifetime check's earliest birth, on its read-bracket convention."""
        if self.printed_ns <= self.sighted_finished_ns:
            return max(self.absent_started_ns, self.printed_ns)
        return self.absent_started_ns


def _birth_bound(row, absent, absent_args, sighted):
    absent_ns, absent_started_ns = absent.midpoint_ns, absent.started.monotonic_ns
    if absent_args is not None and row["pid"] not in absent_args.pids:
        absent_ns = max(absent_ns, absent_args.started_ns)
        absent_started_ns = max(absent_started_ns, absent_args.started_ns)
    offsets = _stamp_offsets_ns(absent) + [stamp.wall_ns - stamp.monotonic_ns
                                           for stamp in (sighted.started, sighted.finished)]
    return _BirthBound(absent_ns, absent_started_ns, sighted.midpoint_ns, sighted.finished.monotonic_ns,
                       int(row["start_epoch_s"]) * 1_000_000_000 - max(offsets))


def _birth_window_evidence(current, births, dwell_ns):
    """A zero counter at each newcomer's birth bound, charged to 30 s.

    ``births`` holds the bound fixed when the series first saw each identity
    absent from its first read. A later read's offset never moves it, so a
    later wall step, gain or loss, cannot change this evidence.
    """
    windows = {}
    closing_ns = current.midpoint_ns
    for identity, row in current.rows.items():
        bound = births.get(identity)
        if bound is None or not row["contaminant"]:
            continue
        zero_ns = bound.zero_ns
        if 0 <= closing_ns - zero_ns <= dwell_ns:
            basis = ("CPU since a complete process table proved absence" if zero_ns == bound.absent_ns
                     else "CPU since the printed start second")
            evidence = _exact_cpu_evidence(identity, row, 0, basis)
            if evidence:
                windows.setdefault(zero_ns, []).append(evidence)
    return windows.items()


def _proven_pair(points, closing_finished_ns, closing_cs):
    """Lead P1 for one reading: the earlier point proving the largest share, or None.

    ``points`` are (start ns, midpoint ns, lower-bound cs) of earlier
    readings, or of the birth bound with 0 cs. The span runs from a point's
    start to the end of the closing read; the growth is the closing counter
    less the point's, less one centisecond. Over k = ceil(span / 30 s)
    windows (k = 1 up to 30 s) one holds at least growth / k. Returns
    (start ns, midpoint ns, growth cs, k, span ns) when that reaches the
    limit times 30 s.
    """
    window_ns = prewindow.INTERVAL_S * 1_000_000_000
    best = None
    for started_ns, midpoint_ns, lower_cs in points:
        span_ns = closing_finished_ns - started_ns
        growth_cs = closing_cs - lower_cs - 1
        if span_ns <= 0 or growth_cs <= 0:
            continue
        windows = max(1, -(-span_ns // window_ns))
        if (growth_cs * 1_000_000_000 * _CPU_LIMIT_DEN >= _CPU_LIMIT_NUM * window_ns * windows
                and (best is None or growth_cs * best[3] > best[2] * windows)):
            best = (started_ns, midpoint_ns, growth_cs, windows, span_ns)
    return best


def _expand_readings(history, stamps, starts):
    """Every reading of one process, restoring the reads a run of unchanged ones folded away.

    ``history`` keeps only the first and last of a run of unchanged
    readings (``QuietGuard._readings``). Each accounting read is a complete
    process table, so every read between them listed the process with the
    same counters. ``stamps`` and ``starts`` index every accounting read.
    """
    readings = []
    for previous, entry in zip((None, *history), history):
        if previous is not None and previous[3:] == entry[3:]:
            low, high = bisect.bisect_right(starts, previous[0]), bisect.bisect_left(starts, entry[0])
            readings.extend((stamp[0], stamp[1], stamp[2], entry[3], entry[4]) for stamp in stamps[low:high])
        readings.append(entry)
    return readings


def _rate_pair(readings):
    """Lead T1: the admitted rate rule over every pair of one process's readings.

    For readings a before b whose midpoints are at least INTERVAL_S apart,
    the pair is above the limit when b's counter less a's, over the
    midpoints' span, exceeds it, with the lower-bound or the printed
    counters. Returns (a, b, growth cs, span ns) for the pair furthest
    above the limit, or None.
    """
    window_ns = prewindow.INTERVAL_S * 1_000_000_000
    scale = 1_000_000_000 * _CPU_LIMIT_DEN
    lowest = [None, None]
    best = None
    opened = 0
    for index, (_, _, midpoint_ns, lower_cs, printed_cs) in enumerate(readings):
        while opened < index and readings[opened][2] <= midpoint_ns - window_ns:
            for k in (0, 1):
                value = readings[opened][3 + k] * scale - _CPU_LIMIT_NUM * readings[opened][2]
                if lowest[k] is None or value < lowest[k][0]:
                    lowest[k] = (value, opened)
            opened += 1
        for k, cs in enumerate((lower_cs, printed_cs)):
            if lowest[k] is not None:
                excess = cs * scale - _CPU_LIMIT_NUM * midpoint_ns - lowest[k][0]
                if excess > 0 and (best is None or excess > best[0]):
                    best = (excess, lowest[k][1], index, k)
    if best is None:
        return None
    _, a, b, k = best
    return readings[a], readings[b], readings[b][3 + k] - readings[a][3 + k], readings[b][2] - readings[a][2]


def _window_reads(reads, opening, current):
    start = next(i for i, read in enumerate(reads) if read is opening)
    end = next(i for i in range(start + 1, len(reads)) if reads[i] is current)
    return reads[start:end + 1]


def _overlap_cpu_evidence(opening, current, reads, *, endpoint_elapsed_ns, births=None, initial=frozenset()):
    """Compare observed TIME growth against the largest supported overlap.

    ``births`` and ``initial`` are the series' birth bounds and the
    identities its first read listed. A newcomer's overlap starts at its
    birth bound. An identity already read before this window gets no
    inferred zero, even if a table in between omitted it.
    """
    births = births or {}
    accounting = [(i, read) for i, read in enumerate(reads) if isinstance(read, contention.Snapshot)]
    named = {pid for read in reads if isinstance(read, _ArgumentsRead) for pid in read.contenders}
    identities = {key for _, read in accounting for key, row in read.rows.items()
                  if row["contaminant"] or key[0] in named}
    # The arguments table prints a PID and no start time. Every other join
    # below is on (pid, start), so a PID's later holder is a distinct process.
    watched = {pid for pid, _ in identities}
    holders = {}
    for index, read in accounting:
        for key, row in read.rows.items():
            if key[0] in watched:
                holders.setdefault(key[0], []).append((index, read, key, row))
    window_start = opening.started.monotonic_ns
    opening_offset = _wall_offset_ns(opening)
    evidence = []
    contenders = []
    for identity in identities:
        pid, start = identity
        observed = [(i, read, read.rows[identity]) for i, read in accounting if identity in read.rows]
        first_index, first, first_row = observed[0]
        last_index, last, last_row = observed[-1]
        last_possible = current.finished.monotonic_ns
        # Absence bounds the lifetime only after its final positive accounting read.
        lifetime_end = len(reads)
        for index, read in enumerate(reads[last_index + 1:], last_index + 1):
            present = pid in read.pids if isinstance(read, _ArgumentsRead) else identity in read.rows
            if not present:
                last_possible = _read_finished_ns(read)
                lifetime_end = index
                break
        # A reused PID keeps the arguments table's row. This identity had
        # released it before the next holder's printed start second ended,
        # and before the read that listed that holder. A forward wall step
        # since this identity's last row can only have dated the start early.
        # Each later holder is judged at the read that first listed it; a
        # later read of the same start second supplies no new bound.
        released = None
        bounded = set()
        for index, read, other, row in holders[pid]:
            if other == identity or index <= last_index or other in bounded:
                continue
            bounded.add(other)
            step = max(0, _wall_offset_ns(read) - _wall_offset_ns(last))
            bound = min(read.finished.monotonic_ns,
                        _birth_floor_ns(row, read) + _START_RESOLUTION_NS + step)
            if last.started.monotonic_ns <= bound < last_possible:
                released = bound if released is None else min(released, bound)

        # Darwin prints lstart at whole-second precision. The largest
        # possible overlap starts at the later of the opening read's
        # beginning and the birth bound fixed at the series' first sighting.
        # A process only admission reads listed gets the same conversion
        # over its bracket in this window.
        birth = births.get(identity)
        seen_before = identity in initial or (birth is not None and birth.sighted_midpoint_ns < opening.midpoint_ns)
        if birth is not None:
            start_bound = max(window_start, birth.lifetime_floor_ns)
        else:
            previous = next((read for i, read in reversed(accounting) if i < first_index), None)
            offsets = [stamp.wall_ns - stamp.monotonic_ns for stamp in (first.started, first.finished)]
            offsets += _stamp_offsets_ns(previous) if previous is not None else []
            floor = int(first_row["start_epoch_s"]) * 1_000_000_000 - max(offsets)
            reliable_start = (abs(_wall_offset_ns(first) - opening_offset) <= 1_000_000_000
                              and floor <= first.finished.monotonic_ns)
            start_bound = max(window_start, floor) if reliable_start else window_start

        # An arguments sighting of the PID counts until this identity's
        # confirmed absence. One that precedes its first accounting row
        # counts too, unless the printed start proves a later birth: an
        # earlier holder of the PID cannot hide it.
        def sighted(until=None):
            for index, read in enumerate(reads[:lifetime_end]):
                if not isinstance(read, _ArgumentsRead) or pid not in read.contenders:
                    continue
                if index < first_index:
                    reference = next(earlier for earlier in reversed(reads[:index])
                                     if isinstance(earlier, contention.Snapshot))
                    if _born_after(first_row, first, read.finished_ns, reference):
                        continue
                elif index > last_index and until is not None and read.started_ns > until:
                    continue  # it began after the later holder had the PID
                return True
            return False

        # The later holder's bound applies when this identity is named by
        # its own rows or by a sighting from inside the bounded lifetime.
        # Otherwise the lifetime stays as long as the PID was listed, so
        # that the bound only ever adds evidence.
        matches = {match for _, _, row in observed for match in row["contaminant_matches"]}
        if released is not None and (matches or sighted(released)):
            last_possible = released
            if sighted(released):
                matches.add("args")
        elif sighted():
            matches.add("args")
        if not matches:
            continue
        resident = first is opening and identity in current.rows
        if resident:
            overlap_ns = endpoint_elapsed_ns
        else:
            overlap_ns = min(last_possible, current.finished.monotonic_ns) - start_bound
        if overlap_ns <= 0:
            continue
        if first is not opening and not seen_before:
            # This complete table proves a zero counter for the identity,
            # including when it lists another holder of the same PID.
            baseline = 0.0
            basis = "CPU lower bound from absence at the opening and a sample inside this window"
        elif first is not opening:
            # Read before this window: a table that omits it proves no zero.
            # Its first reading here is a lower bound on the opening counter.
            baseline = first_row.get("peak_cpu_seconds", first_row["cumulative_cpu_seconds"])
            basis = "CPU lower bound between samples in this window"
        else:
            baseline = first_row.get("peak_cpu_seconds", first_row["cumulative_cpu_seconds"])
            basis = "CPU lower bound from the opening counter and a later sample in this window"
        peak = max(row["cumulative_cpu_seconds"] for _, _, row in observed)
        # Darwin TIME is in centiseconds. One quantum ties the limit at
        # 200 ms. Compare integers so a floating point tie stays quiet.
        growth_cs = round(peak * 100) - round(baseline * 100)
        rate = growth_cs * 10_000_000 / overlap_ns
        if rate > contention.REPORT_FLOOR_CPU_S_PER_S:
            contenders.append({"pid": pid, "lstart": start, "name": last_row["command"],
                               "matched_on": sorted(matches), "cpu_s": growth_cs / 100, "cpu_s_per_s": rate})
        # The endpoint decision owns the ordinary resident comparison,
        # including ties. A larger interior peak can prove growth after a reset.
        endpoint_growth = (resident and peak == current.rows[identity]["cumulative_cpu_seconds"]
                           and (first_row["contaminant"] or current.rows[identity]["contaminant"]))
        if not endpoint_growth and growth_cs * 1_000_000_000 * _CPU_LIMIT_DEN > _CPU_LIMIT_NUM * overlap_ns:
            evidence.append({"pid": pid, "command": last_row["command"], "start": start,
                             "cpu_s_per_s": rate, "basis": basis})
    evidence.sort(key=lambda row: (-row["cpu_s_per_s"], row["pid"], row["start"]))
    contenders.sort(key=lambda row: (-row["cpu_s_per_s"], row["pid"], row["lstart"]))
    return evidence, contenders


class QuietGuard:
    """Reuse the agent identity and custody census, with no ancestor exemption.

    Additional argv matching covers hand-run measurement chains. Custody parents
    include shared defaults and configured extras; missing roots fail closed.
    A refusal is latched even if an endpoint catches the raised exception.
    CPU windows span at least prewindow.INTERVAL_S. The admitted endpoint
    comparison uses paired-read midpoints. Background windows use the
    accounting-read midpoints. Interior readings also bound CPU across a
    transient worker's observed lifetime. The first admission waits for the
    baseline. Its midpoint sample lets the daemon close its first window
    after one more cadence.

    After that admission a daemon thread repeats the census and takes a CPU
    snapshot every SNAPSHOT_CADENCE_S; it only stores what it saw (or the
    first failure). Each admission repeats the full census and uses the
    admitted guard's caller snapshots alongside the background windows. Active-work
    polling keeps the existing throttle. The caller judges, for every
    snapshot stored since the last judged one, the window
    from the newest snapshot at least INTERVAL_S earlier (sliding windows,
    so a burst shorter than one cadence always falls wholly inside one 30 s
    window and no stretch of time escapes judgement), and the pair from
    each earlier snapshot less than INTERVAL_S before that one (lead S2,
    ``_judge_pairs``); admission windows get the same pairs. A stored failure, a
    stalled sampler or a window longer than MAX_WINDOW_S refuses. Every
    clear verdict re-reads the stored failure as its last act, so a census
    that fails while an admission's own probes run refuses that admission.
    Contention in a judged window is recorded and blocks publication.
    A process is its (pid, start) pair. The arguments table prints no start,
    so its rows are joined by the printed start second and the confirmed
    lifetime; an earlier or later holder of a PID is a different process.
    A later holder that only an arguments table lists cannot be told from
    the earlier process and extends its supported lifetime.
    finish() stops sampling and judges the final state before success can
    be published. An unfinished census at the join bound is indeterminate.
    """

    # The daemon's cadence, the only place it is set.
    SNAPSHOT_CADENCE_S = 15.0
    JOIN_TIMEOUT_S = 1.0
    # A steady window spans two cycles: INTERVAL_S plus two cycles' probe
    # time. The margin absorbs that and moderate
    # slips; beyond INTERVAL_S + one cadence + margin (50 s) the sampler has
    # stalled and the window would dilute a contender, so it refuses as
    # indeterminate, and a check finding no snapshot that recent refuses too.
    WINDOW_MARGIN_S = 5.0
    MAX_WINDOW_S = prewindow.INTERVAL_S + SNAPSHOT_CADENCE_S + WINDOW_MARGIN_S

    def __init__(self, parents, *, run=subprocess.run, inspect_custody=census,
                 clock=time.monotonic, sleep=time.sleep, wall_clock_ns=None,
                 host_reader=contention.read_host_cpu):
        self.parents = [Path(p) for p in parents]
        self.run, self.inspect_custody, self.clock = run, inspect_custody, clock
        self.sleep = sleep
        self.wall_clock_ns = wall_clock_ns or (lambda: time.time_ns())
        self.host_reader = host_reader
        self.last = float("-inf")
        self._clock_last = float("-inf")
        self._clock_lock = threading.Lock()
        self._cpu_probe_lock = threading.Lock()
        self._snapshots = []
        self._initial_identities = frozenset()
        # (pid, start) -> _BirthBound, fixed by the series read that first
        # listed an identity its first read did not. Never recomputed.
        self._birth_bounds = {}
        # The arguments table read with the newest series sample, and the
        # lowest and highest wall - monotonic offset of every series read.
        self._series_args = None
        self._wall_offsets = None
        # (pid, start) -> every reading of it R0 took, series or admission
        # (lead R1), oldest first, as
        # (started ns, finished ns, midpoint ns, lower-bound cs, printed cs).
        # Of a run of unchanged readings only the first and last are kept:
        # no other can give a larger proven bound (lead P1), and the final
        # verdict restores the rest from the read index (lead T1).
        self._readings = {}
        self._commands = {}
        # Every accounting read, oldest first, as (started ns, finished ns,
        # midpoint ns, largest wall - monotonic offset of its accounting
        # table, the same including its arguments table), and each
        # (pid, start)'s first reading: (index into it, printed start
        # second). Lead T1 judges every pair of readings from these.
        self._read_stamps = []
        self._first_listings = {}
        self._admission_snapshots = []
        self._admission_previous_over = {}
        self._process_observations = []
        # pid -> start -> (highest CPU, contaminant matches). One entry per
        # process seen; a PID's next holder never reads or replaces it.
        self._process_history = {}
        # Index into _snapshots of the snapshot that closed the last judged
        # window (or the first snapshot before admission).
        self._judged_end = 0
        # Per-snapshot disclosures and daemon cycle times, receipted by the
        # next check() on the caller's thread (the daemon never writes receipts).
        self._pending = self._empty_pending()
        self._snapshot_lock = threading.Lock()
        self._stop_sampler = threading.Event()
        self._sampler = None
        self._background_failure = None
        self.failure = None
        self.receipts = []
        self.contention_flags = []
        self._flagged_windows = set()

    @staticmethod
    def _empty_pending():
        return {"regressed_counters": [], "wall_clock_backwards": False, "census": []}

    def _now(self):
        with self._clock_lock:
            now = self.clock()
            if not math.isfinite(now) or now < self._clock_last:
                raise Refused("census indeterminate: monotonic clock went backwards or is invalid")
            self._clock_last = now
            return now

    def _read_cpu_snapshot(self, *, include_host):
        host = host_error = None
        if include_host and self.host_reader is not None:
            try:
                host = [list(cpu) for cpu in self.host_reader()]
            except Exception as exc:
                host_error = f"{type(exc).__name__}: {exc}"
        # The optional host tick read precedes the process tables. Start the
        # process clock at the first table, as the admitted guard does.
        started = self._now()
        wall = self.wall_clock_ns()
        try:
            result = self.run(contention.PS_ARGV, capture_output=True, text=True,
                              timeout=contention.PROBE_TIMEOUT_S,
                              env=_tool_env())
            # Keep the accounting bracket for lifetime evidence and record
            # the full paired read below for the admitted midpoint.
            finished = self._now()
            finished_wall = self.wall_clock_ns()
        except Exception as exc:
            raise Refused(f"census indeterminate: cumulative CPU snapshot: {exc}") from exc
        if result.returncode:
            raise Refused(f"census indeterminate: cumulative CPU snapshot exit {result.returncode}")
        try:
            rows = contention.parse(result.stdout.encode("utf-8"), tz=timezone.utc)
        except (ValueError, OverflowError) as exc:
            raise Refused(f"census indeterminate: cumulative CPU snapshot: {exc}") from exc
        sightings = {}
        for row in rows.values():
            is_worker = _require_clear_sighting(row["pid"], row["command"], sightings)
            row["contaminant_matches"] = ["ucomm"] if is_worker else []
        try:
            table = self.run(PS_ARGV, capture_output=True, text=True,
                             timeout=contention.PROBE_TIMEOUT_S,
                             env=_tool_env())
        except Exception as exc:
            raise Refused(f"census indeterminate: process args table: {exc}") from exc
        if table.returncode:
            raise Refused("census indeterminate: process args table unavailable")
        admitted_finished = self._now()
        admitted_wall = self.wall_clock_ns() if admitted_finished != finished else finished_wall
        admitted_finish_ns = int(admitted_finished * 1e9)
        args = self._process_table(table.stdout, {}, started_ns=round(finished * 1e9),
                                   finished_ns=round(admitted_finished * 1e9))
        for row in rows.values():
            if row["pid"] in args.contenders:
                row["contaminant_matches"].append("args")
            row["contaminant"] = bool(row["contaminant_matches"])
        return _AccountingRead(
            Stamp(wall, round(started * 1e9), round(started * 1e9)),
            Stamp(finished_wall, round(finished * 1e9), round(finished * 1e9)), rows, None,
            host=host, host_error=host_error, admitted_start_ns=int(started * 1e9),
            admitted_finish=Stamp(admitted_wall, admitted_finish_ns, admitted_finish_ns)), args

    def _cpu_snapshot(self, *, census_summary=None, admission=False):
        with self._cpu_probe_lock:
            snapshot, args = self._read_cpu_snapshot(include_host=not admission)
            with self._snapshot_lock:
                self._remember_cpu_snapshot(snapshot, census_summary=census_summary, admission=admission, args=args)
                self._process_observations.extend((snapshot, args))
        return snapshot

    def _remember_cpu_snapshot(self, snapshot, *, census_summary, admission, args=None):
        rows = snapshot.rows
        previous_read = self._process_observations[-1] if self._process_observations else None
        sighted = previous_read.contenders if isinstance(previous_read, _ArgumentsRead) else frozenset()
        reference = next((read for read in reversed(self._process_observations)
                          if isinstance(read, contention.Snapshot)), None)
        for (pid, start), row in rows.items():
            cpu = row["cumulative_cpu_seconds"]
            matches = set(row["contaminant_matches"])
            holders = self._process_history.setdefault(pid, {})
            known = holders.get(start)
            # The arguments table prints no start time. Its sighting of this
            # PID stays with this row unless accounting has another holder
            # of the PID on record and this row's start proves a birth after
            # the sighting. An earlier holder alone decides nothing.
            if pid in sighted and (known is not None or not holders or not _born_after(
                    row, snapshot, previous_read.finished_ns, reference)):
                matches.add("args")
            if known is not None:
                prior_cpu, prior_matches = known
                matches.update(prior_matches)
                if prior_cpu > cpu:
                    row["peak_cpu_seconds"] = prior_cpu
                    cpu = prior_cpu
            row["contaminant_matches"] = sorted(matches)
            row["contaminant"] = bool(matches)
            holders[start] = (cpu, matches)
        # Lead R1: every reading R0 takes of a process, by the daemon, a
        # foreground admission, an inventory tick or the final read, is P1
        # evidence for that (pid, start). It can only add a withhold:
        # admission reads still never open or extend a judged window.
        started_ns, finished_ns = snapshot.started.monotonic_ns, snapshot.finished.monotonic_ns
        offsets = _stamp_offsets_ns(snapshot)
        read_index = len(self._read_stamps)
        self._read_stamps.append((started_ns, finished_ns, (started_ns + finished_ns) // 2,
                                  max(offsets[:2]), max(offsets)))
        for identity, row in rows.items():
            entry = (started_ns, finished_ns, (started_ns + finished_ns) // 2,
                     round(row.get("peak_cpu_seconds", row["cumulative_cpu_seconds"]) * 100),
                     round(row["cumulative_cpu_seconds"] * 100))
            history = self._readings.get(identity)
            if history is None:
                history = self._readings[identity] = []
                self._first_listings[identity] = (read_index, int(row["start_epoch_s"]))
            if len(history) >= 2 and history[-2][3:] == history[-1][3:] == entry[3:]:
                history[-1] = entry
            else:
                history.append(entry)
            self._commands[identity] = row["command"]
        if not admission:
            backwards = snapshot.finished.wall_ns < snapshot.started.wall_ns
            if self._snapshots:
                previous = self._snapshots[-1]
                backwards = backwards or snapshot.started.wall_ns < previous.finished.wall_ns
                for identity in previous.rows.keys() & rows.keys():
                    if rows[identity]["cumulative_cpu_seconds"] < previous.rows[identity]["cumulative_cpu_seconds"]:
                        self._pending["regressed_counters"].append({
                            "pid": identity[0], "start": identity[1],
                            "command": rows[identity]["command"], "reason": "counter regressed",
                            "contaminant": rows[identity]["contaminant"] or previous.rows[identity]["contaminant"]})
                # A newcomer was born between the previous series sample, which
                # did not list it, and this read. Fix its bound now, once.
                for identity, row in rows.items():
                    if identity not in self._initial_identities and identity not in self._birth_bounds:
                        self._birth_bounds[identity] = _birth_bound(row, previous, self._series_args, snapshot)
            else:
                self._initial_identities = frozenset(rows)
            self._series_args = args
            offsets = _stamp_offsets_ns(snapshot)
            if self._wall_offsets is not None:
                offsets += self._wall_offsets
            self._wall_offsets = (min(offsets), max(offsets))
            self._pending["wall_clock_backwards"] |= backwards
            self._snapshots.append(snapshot)
            if census_summary is not None:
                # A consumer sees the snapshot and its census together.
                self._pending["census"].append({
                    "monotonic_s": snapshot.midpoint_ns / 1e9, **census_summary})

    def _probe(self, argv):
        result = self.run(argv, capture_output=True, text=True, timeout=15, env=_tool_env())
        return ProbeResult(argv, result.returncode, result.stdout, result.stderr, time.monotonic_ns())

    @staticmethod
    def _require_clear_agent_result(agent, receipt, field):
        if type(agent.exit_code) is not int or not isinstance(agent.stdout, str) or not isinstance(agent.stderr, str):
            raise Refused("agent census returned malformed probe result")
        for line in agent.stdout.splitlines():
            fields = line.split(None, 1)
            if len(fields) == 2 and fields[0].isdecimal():
                pid, argv = fields
                _require_clear_sighting(int(pid), argv.split(None, 1)[0], receipt, argv=argv, line=line)
        # Resolve incidental argv matches using the admitted identity filter.
        agent = decide_census(agent)
        receipt[field] = asdict(agent)
        if agent.exit_code != 1 or agent.stdout.strip():
            raise Refused(f"agent census refused: {receipt[field]}")

    def _process_table(self, stdout, receipt, *, started_ns, finished_ns):
        if not stdout.strip():
            raise ValueError("empty process census")
        receipt["pcpu_diagnostic"] = []
        receipt["chains"] = []
        pids = set()
        contenders = set()
        candidates = []
        for line in stdout.splitlines():
            if not line.strip():
                continue
            fields = line.split(None, 2)
            if len(fields) != 3 or not fields[0].isdigit():
                raise ValueError("invalid process census row")
            pid, pcpu, argv = int(fields[0]), float(fields[1]), fields[2]
            if not math.isfinite(pcpu) or pcpu < 0:
                raise ValueError("invalid process CPU")
            if _require_clear_sighting(pid, argv.split(None, 1)[0], receipt, argv=argv, line=line):
                contenders.add(pid)
                if pcpu > prewindow.CPU_LIMIT_PERCENT:
                    receipt["pcpu_diagnostic"].append((pid, pcpu, argv))
            pids.add(pid)
            if _AGENT_CANDIDATE.search(argv):
                candidates.append(f"{pid} {argv}\n")
        if candidates:
            self._require_clear_agent_result(
                ProbeResult(PS_ARGV, 0, "".join(candidates), "", time.monotonic_ns()), receipt, "process_table_agent")
        return _ArgumentsRead(started_ns, finished_ns, frozenset(pids), frozenset(contenders))

    def _census(self, receipt):
        fs = measurement_liveness.census_fs
        extra = json.loads(os.environ.get(ADDITIONAL_PARENTS_ENV, "[]"))
        if not isinstance(extra, list) or any(not isinstance(p, str) or not p for p in extra):
            raise Refused("additional custody parents must be a JSON array of paths")
        parents = [custody_parent(), *(fs(Path(p), "expanduser") for p in extra), *self.parents]
        for parent in parents:
            if not parent.is_absolute() or {part.casefold() for part in parent.parts} & {"..", "restricted"}:
                raise Refused(f"invalid custody parent: {parent}")
        installed = _installed_night_agents()
        receipt["installed_night_agents"] = installed
        if installed:
            raise Refused(f"measurement window armed: {installed}")
        launched = self.run(("/bin/launchctl", "print", f"gui/{os.getuid()}/com.joulewise.night"),
                            capture_output=True, text=True, timeout=15, env=_tool_env())
        receipt["launchctl"] = {"exit_code": launched.returncode, "stdout": launched.stdout,
                                "stderr": launched.stderr}
        if launched.returncode == 0:
            raise Refused("measurement night LaunchAgent is loaded")
        if launched.returncode != 113 or "could not find service" not in launched.stderr.lower():
            raise Refused("LaunchAgent census indeterminate")
        self._require_clear_agent_result(self._probe(R0_AGENT_CENSUS_ARGV), receipt, "agent")
        custody = self.inspect_custody(parents=parents, strict=True)
        receipt["resolved_custody_parents"] = custody.resolved_parents
        receipt["custody"] = {"refusals": custody.refusals, "warnings": custody.warnings}
        with self._cpu_probe_lock:
            started = self._now()
            table = self._probe(PS_ARGV)
            if table.exit_code != 0:
                raise Refused("process table unavailable")
            args = self._process_table(table.stdout, receipt, started_ns=round(started * 1e9),
                                       finished_ns=round(self._now() * 1e9))
            with self._snapshot_lock:
                self._process_observations.append(args)
        if not custody.clear:
            raise Refused(f"machine occupied or census indeterminate: {receipt}")

    def _background_snapshot(self):
        """One daemon cycle: the census, then a CPU snapshot. Stores, never judges."""
        try:
            seen = {"resolved_custody_parents": []}
            self._census(seen)
            # What this cycle's census saw, compactly (#691 receipted it per
            # check); every verdict here passed, or the cycle would have failed.
            summary = {
                "resolved_custody_parents": seen["resolved_custody_parents"],
                "installed_night_agents": seen["installed_night_agents"],
                "launchctl_exit_code": seen["launchctl"]["exit_code"],
                "agent_exit_code": seen["agent"]["exit_code"],
                "agent_hits": len(seen["agent"]["stdout"].strip().splitlines()),
                "custody_clear": not seen["custody"]["refusals"],
                "custody_warnings": seen["custody"]["warnings"],
                "chains": seen["chains"],
                "pcpu_diagnostic": seen["pcpu_diagnostic"]}
            self._cpu_snapshot(census_summary=summary)
        except Exception as exc:
            # Fail closed: the next check() refuses with this reason.
            with self._snapshot_lock:
                self._background_failure = f"{type(exc).__name__}: {exc}"
            self._stop_sampler.set()

    def _latched_background_failure(self):
        with self._snapshot_lock:
            return self._background_failure

    def _sampler_state(self):
        """The newest sample, whether completed windows await judgment, and the latch."""
        with self._snapshot_lock:
            latest = self._snapshots[-1] if self._snapshots else None
            queued = len(self._snapshots) - 1 > self._judged_end
            return latest, queued, self._background_failure

    def _close_admission(self, receipt):
        """Admission's last act before it returns clear. Advisory (module docstring)."""
        _, queued, _ = self._sampler_state()
        if queued:
            # Windows completed while this admission's own probes ran.
            self._cpu_interval(receipt)
        latest, _, _ = self._sampler_state()
        self._require_fresh_background(self._now(), latest)
        self._require_background_clear()

    def _require_background_clear(self):
        """The last act of every clear verdict.

        The sampler can latch a failed census while an admission's own
        probes are running. That admission refuses; it does not hand the
        failure to the next one.
        """
        failure = self._latched_background_failure()
        if failure:
            raise Refused(f"census refused or indeterminate in the background sampler: {failure}")

    def _sampler_main(self):
        while not self._stop_sampler.wait(self.SNAPSHOT_CADENCE_S):
            self._background_snapshot()
            if self._background_failure:
                return

    def _start_sampler(self):
        if self._sampler is None:
            self._sampler = threading.Thread(target=self._sampler_main,
                                             name="joulewise-quiet-snapshots", daemon=True)
            self._sampler.start()

    def close(self):
        self._stop_sampler.set()
        sampler = self._sampler
        if sampler is not None and sampler is not threading.current_thread():
            sampler.join(self.JOIN_TIMEOUT_S)

    def finish(self):
        """Stop and drain the sampler before an entry point publishes success."""
        if self.failure is not None:
            raise Refused(self.failure)
        receipt = {"resolved_custody_parents": []}
        try:
            self.close()
            if self._sampler is None:
                raise Refused("census indeterminate: background sampler never started")
            # Establish whether the join succeeded before reading the final
            # state. A later exit cannot validate an earlier copy of it.
            stopped = not self._sampler.is_alive()
            if stopped:
                receipt["monotonic_s"] = self._now()
            self.receipts.append(receipt)
            self._cpu_interval(receipt)
            self._proven_history(receipt)
            self._pair_history(receipt)
            if not stopped:
                raise Refused("census indeterminate: background sampler did not stop within the join bound")
            self._require_background_clear()
            self._require_stable_clock(receipt)
        except Exception as exc:
            raise self._record_refusal(receipt, exc) from exc

    def verify_publication(self):
        """Take a fresh census at the point that a pass can be published."""
        if self.failure is not None:
            raise Refused(self.failure)
        receipt = {}
        try:
            receipt["monotonic_s"] = self._now()
            with self._snapshot_lock:
                latest = self._snapshots[-1] if self._snapshots else None
            self._require_fresh_background(receipt["monotonic_s"], latest)
            self._census(receipt)
            # The read at run end joins the sample series. The admission
            # window keeps parity with the admitted guard; the verdict's
            # windows below use only the series.
            current = self._cpu_snapshot()
            self._admission_interval(receipt, current)
            self._cpu_interval(receipt)
            self._proven_history(receipt)
            self._pair_history(receipt)
            self._require_fresh_background(self._now(), latest)
            self._require_background_clear()
            self._require_stable_clock(receipt)
        except Exception as exc:
            raise self._record_refusal(receipt, exc) from exc
        if self.receipts:
            self.receipts[-1]["publication_census"] = receipt
        else:
            self.receipts.append(receipt)

    def _require_stable_clock(self, receipt):
        """Withhold unless every series read saw the same wall - monotonic offset, within 1 ms.

        A birth's printed start second converts to monotonic time only as
        well as the offset at birth is known. R0 assumes it lies within the
        range the series' reads measured. An excursion that returns between
        two reads leaves no trace in them and is not detected (KNOWN
        LIMITATION R0-CLOCK in the module docstring).
        """
        with self._snapshot_lock:
            offsets = self._wall_offsets
        if offsets is None:
            return
        spread_ns = offsets[1] - offsets[0]
        receipt["wall_offset_range_us"] = spread_ns / 1000
        if spread_ns > CLOCK_STABILITY_LIMIT_NS:
            raise Refused(f"clock_unstable: wall - monotonic offset varied by {spread_ns / 1000:.3f} µs "
                          f"over the series' reads (limit {CLOCK_STABILITY_LIMIT_NS / 1000:g} µs)")

    def _require_fresh_background(self, now, latest):
        if latest is None:
            raise Refused("census indeterminate: background snapshots unavailable")
        lag = now - latest.finished.monotonic_ns / 1e9
        if lag > self.MAX_WINDOW_S:
            raise Refused(f"census indeterminate: background snapshots stalled ({lag:.1f} s since the last)")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, traceback):
        self.close()

    def _record_cpu_flags(self, receipt, details, busy, *, kind=None, proof_interval=None, note=None):
        if not busy:
            return
        interval = {key: details[key] for key in ("start_monotonic_s", "end_monotonic_s", "elapsed_s")}
        fresh = []
        for row in busy:
            key = (interval["start_monotonic_s"], interval["end_monotonic_s"], row["pid"], row["start"])
            if key not in self._flagged_windows:
                self._flagged_windows.add(key)
                fresh.append(row)
        if fresh:
            names = ", ".join(f"{row['pid']} {row['command']} {row['cpu_s_per_s']:.6g} CPU-s/s" for row in fresh)
            flag = f"contaminating CPU contention: {names}" + (f" ({note})" if note else "")
            details["contention_flag"] = flag
            receipt.setdefault("contention_flag", flag)
            entry = {"monotonic_s": receipt.get("monotonic_s", interval["end_monotonic_s"]),
                     "flag": flag, "interval": interval, "busy": fresh}
            if kind is not None:
                entry["kind"] = kind
            if proof_interval is not None:
                entry["proof_interval"] = proof_interval
            self.contention_flags.append(entry)

    def _record_clock_flag(self, receipt, details):
        if not details.get("wall_clock_diverged"):
            return
        interval = {key: details[key] for key in ("start_monotonic_s", "end_monotonic_s", "elapsed_s")}
        key = (interval["start_monotonic_s"], interval["end_monotonic_s"], "wall_clock")
        if key in self._flagged_windows:
            return
        self._flagged_windows.add(key)
        flag = (f"wall clock moved {details['wall_clock_divergence_s']:.6g} s against the monotonic clock "
                f"within this window (limit {WALL_DIVERGENCE_LIMIT_NS / 1e9:g} s)")
        details["clock_flag"] = flag
        receipt.setdefault("clock_flag", flag)
        self.contention_flags.append({"monotonic_s": receipt.get("monotonic_s", interval["end_monotonic_s"]),
                                      "flag": flag, "interval": interval, "busy": [], "kind": "wall_clock"})

    def _record_interval_flags(self, receipt, details, endpoint, endpoint_busy, lifetime_busy):
        self._record_clock_flag(receipt, details)
        if (endpoint["start_monotonic_s"], endpoint["end_monotonic_s"]) == (
                details["start_monotonic_s"], details["end_monotonic_s"]):
            self._record_cpu_flags(receipt, details, endpoint_busy + lifetime_busy)
        else:
            self._record_cpu_flags(receipt, endpoint, endpoint_busy)
            self._record_cpu_flags(receipt, details, lifetime_busy)

    def _judge_pairs(self, receipt, sequence, samples, start, current, observations, births, *,
                     previous_over=None):
        """Lead S1-S2: judge every pair that ``current`` closes, not only the newest window.

        ``samples[start]`` is the newest opening at least INTERVAL_S before
        ``current``, the admitted L3 window the caller has judged. Each
        earlier opening less than INTERVAL_S before it is judged by the same
        rule here. With the L3 window, those are the pairs no read splits
        into two parts of at least INTERVAL_S. A longer pair holds a read
        that does, and a rate above the limit over it puts one part above
        it. So a reading added anywhere keeps every judged pair, or splits
        it into two judged ones. Flags only: these pairs never refuse as
        stalled and never move the L3 window.
        """
        admitted = previous_over is not None
        midpoint = (lambda read: read.admitted_midpoint_ns) if admitted else (lambda read: read.midpoint_ns)
        newest = midpoint(samples[start])
        dwell_ns = prewindow.INTERVAL_S * 1_000_000_000
        busy = []
        for index in range(start - 1, -1, -1):
            opening = samples[index]
            if midpoint(opening) <= newest - dwell_ns:
                break
            reads = _window_reads(observations, opening, current)
            entry = {"sequence": sequence, "start_monotonic_s": opening.midpoint_ns / 1e9,
                     "end_monotonic_s": current.midpoint_ns / 1e9,
                     "elapsed_s": (current.midpoint_ns - opening.midpoint_ns) / 1e9}
            details = {"regressed_counters": [], "regressed_noncontaminant": []}
            endpoint, endpoint_busy, lifetime_busy = self._judge_cpu_interval(
                opening, current, details, reads=reads, births=births,
                previous_over=None if previous_over is None else dict(previous_over))
            self._record_interval_flags(receipt, details, endpoint, endpoint_busy, lifetime_busy)
            busy.extend(endpoint_busy + lifetime_busy)
            for key in ("contention_flag", "clock_flag"):
                if key in details:
                    entry[key] = details[key]
            receipt.setdefault("pair_windows", []).append(entry)
        return busy

    def _admission_interval(self, receipt, current=None):
        if current is None:
            current = self._cpu_snapshot(admission=True)
        # L3 chooses the newest eligible earlier admission. The daemon's
        # samples provide evidence inside that window without moving it.
        samples = self._admission_snapshots
        dwell_ns = prewindow.INTERVAL_S * 1_000_000_000
        start = next((i for i in range(len(samples) - 1, -1, -1)
                      if current.admitted_midpoint_ns - samples[i].admitted_midpoint_ns >= dwell_ns), None)
        if start is not None:
            details = {"regressed_counters": [], "regressed_noncontaminant": []}
            opening = samples[start]
            with self._snapshot_lock:
                observations = list(self._process_observations)
                births = dict(self._birth_bounds)
            reads = _window_reads(observations, opening, current)
            previous_over = dict(self._admission_previous_over)
            endpoint, endpoint_busy, lifetime_busy = self._judge_cpu_interval(
                opening, current, details, reads=reads, births=births,
                previous_over=self._admission_previous_over)
            self._record_interval_flags(receipt, details, endpoint, endpoint_busy, lifetime_busy)
            receipt.setdefault("admission_cpu_intervals", []).append(details)
            self._judge_pairs(receipt, "admission", samples, start, current, observations, births,
                              previous_over=previous_over)
            # Keep every opening a later pair can need (lead S2).
            keep = next(i for i in range(start + 1)
                        if samples[i].admitted_midpoint_ns > opening.admitted_midpoint_ns - dwell_ns)
            del samples[:keep]
        if not samples or samples[-1].admitted_midpoint_ns != current.admitted_midpoint_ns:
            samples.append(current)
        else:
            samples[-1] = current
        with self._snapshot_lock:
            # Retain observations until neither sequence can use them inside
            # a future window. Each sequence keeps its own opening endpoint.
            cutoff = min(self._snapshots[0].started.monotonic_ns, samples[0].started.monotonic_ns)
            self._process_observations = [read for read in self._process_observations if _read_finished_ns(read) >= cutoff]

    def _exact_windows(self, receipt, snapshots, births, end, dwell_ns, flagged):
        current = snapshots[end]
        closing_ns = current.midpoint_ns
        zero_windows = []

        def interval(opening_ns):
            return {"start_monotonic_s": opening_ns / 1e9, "end_monotonic_s": closing_ns / 1e9,
                    "elapsed_s": (closing_ns - opening_ns) / 1e9}

        def record(opening_ns, evidence, fresh, *, sampled_ns=None):
            details = {**interval(opening_ns), "charged_s": prewindow.INTERVAL_S, "busy": evidence}
            receipt.setdefault("exact_windows", []).append(details)
            if sampled_ns is None or sampled_ns == opening_ns:
                self._record_cpu_flags(receipt, details, fresh, kind="exact_30s")
            else:
                # The flag's interval locates the proof between actual
                # reads. Keep the unsampled start second as the exact proof.
                self._record_cpu_flags(receipt, interval(sampled_ns), fresh, kind="exact_30s",
                                       proof_interval=interval(opening_ns))
            flagged.update((row["pid"], row["start"]) for row in evidence)

        busy = []
        for earlier in range(end - 1, -1, -1):
            opening = snapshots[earlier]
            if closing_ns - opening.midpoint_ns > dwell_ns:
                break
            measured = _exact_window_evidence(opening, current)
            if measured:
                record(opening.midpoint_ns, measured, measured)
                busy.extend(measured)
        for opening_ns, evidence in _birth_window_evidence(current, births, dwell_ns):
            sampled_ns = next((sample.midpoint_ns for sample in reversed(snapshots[:end])
                               if sample.midpoint_ns <= opening_ns), snapshots[0].midpoint_ns)
            zero_windows.append((opening_ns, evidence, sampled_ns))

        # Keep every qualifying exact window in the receipt. A zero opening
        # can corroborate another flag for this process at the same read.
        for opening_ns, evidence, sampled_ns in zero_windows:
            fresh = [row for row in evidence if (row["pid"], row["start"]) not in flagged]
            record(opening_ns, evidence, fresh, sampled_ns=sampled_ns)
            busy.extend(fresh)
        return busy

    def _proven_windows(self, receipt, current, births, readings, flagged):
        """Lead P1: contention any two points of one process's life prove.

        A point is a series reading of the process (its lower-bound
        counter) or its birth bound's earliest instant (counter 0). For an
        earlier point a and the reading b at ``current``, the span L runs
        from the start of a's read (or the bound) to the end of b's read,
        the largest the reads allow. The growth is b's printed counter less
        a's, less one centisecond for Darwin's rounding. Split [a, b] into
        k = ceil(L / 30 s) windows (k = 1 up to 30 s): one holds at least
        growth / k. Contention is proven if that reaches the limit times
        30 s. Identities another check flagged at this read are skipped.
        """
        busy = []
        for identity, row in current.rows.items():
            if not row["contaminant"] or identity in flagged:
                continue
            points = [(started, midpoint, lower) for started, _, midpoint, lower, _ in readings.get(identity, ())
                      if midpoint < current.midpoint_ns]
            bound = births.get(identity)
            if bound is not None:
                points.append((bound.lifetime_floor_ns, bound.lifetime_floor_ns, 0))
            best = _proven_pair(points, current.finished.monotonic_ns, round(row["cumulative_cpu_seconds"] * 100))
            if best is None:
                continue
            busy.append(self._record_proven(receipt, identity, row["command"], best,
                                            current.midpoint_ns, current.finished.monotonic_ns))
            flagged.add(identity)
        return busy

    def _proven_history(self, receipt):
        """Lead Q1: P1 over the complete history of every process in scope at any read.

        Scope is sticky: a (pid, start) that any read identified as a
        contaminant is judged over every retained reading of it, earlier
        and later, and its birth bound, whatever later or earlier reads
        made of it. Every pair is checked, whichever read ends it. This
        runs at the final verdict, so a change of scope at any read is
        covered; processes already flagged are skipped.
        """
        with self._snapshot_lock:
            readings = {identity: tuple(history) for identity, history in self._readings.items()}
            births = dict(self._birth_bounds)
            commands = dict(self._commands)
            scope = {(pid, start) for pid, holders in self._process_history.items()
                     for start, (_, matches) in holders.items() if matches}
        flagged = {(row["pid"], row["start"]) for flag in self.contention_flags for row in flag["busy"]}
        busy = []
        for identity in sorted(scope - flagged):
            history = readings.get(identity, ())
            bound = births.get(identity)
            best = None
            for index, (_, finished_ns, midpoint_ns, _, printed_cs) in enumerate(history):
                points = [(started, midpoint, lower) for started, _, midpoint, lower, _ in history[:index]
                          if midpoint < midpoint_ns]
                if bound is not None:
                    points.append((bound.lifetime_floor_ns, bound.lifetime_floor_ns, 0))
                proof = _proven_pair(points, finished_ns, printed_cs)
                if proof is not None and (best is None or proof[2] * best[0][3] > best[0][2] * proof[3]):
                    best = (proof, midpoint_ns, finished_ns)
            if best is not None:
                busy.append(self._record_proven(receipt, identity, commands.get(identity, "?"), *best))
        return busy

    def _record_proven(self, receipt, identity, command, proof, closing_midpoint_ns, closing_finished_ns):
        started_ns, midpoint_ns, growth_cs, windows, span_ns = proof
        evidence = {"pid": identity[0], "command": command, "start": identity[1],
                    "cpu_s_per_s": growth_cs / windows / 100 / prewindow.INTERVAL_S,
                    "basis": "CPU between two points of one process's life, split into windows of at most 30 s"}
        details = {"start_monotonic_s": midpoint_ns / 1e9, "end_monotonic_s": closing_midpoint_ns / 1e9,
                   "elapsed_s": (closing_midpoint_ns - midpoint_ns) / 1e9, "span_s": span_ns / 1e9,
                   "cpu_s": growth_cs / 100, "windows": windows, "bound_cpu_s": growth_cs / windows / 100,
                   "busy": [evidence]}
        receipt.setdefault("proven_windows", []).append(details)
        note = (f"{growth_cs / 100:.2f} CPU-s after rounding from {started_ns / 1e9:.3f} s to "
                f"{closing_finished_ns / 1e9:.3f} s: at least {growth_cs / windows / 100:.3f} CPU-s in one of "
                f"{windows} window{'s' if windows > 1 else ''} of at most {prewindow.INTERVAL_S:g} s")
        self._record_cpu_flags(receipt, details, [evidence], kind="proven_30s", note=note)
        return evidence

    def _pair_history(self, receipt):
        """Lead T1: the admitted rate rule over every pair of each in-scope process's readings.

        Runs at the final verdict, after P1, over every process any read
        identified (lead Q1) and not yet flagged. Every reading of it is
        judged against every earlier one at least INTERVAL_S before it,
        with no bound on the span (``_rate_pair``), so a read added between
        two readings never removes their pair. A process first listed after
        the first read is also judged from its birth bound: its counter at
        each reading over the span from the latest instant every reading
        allows as its birth (lead T2) to the end of that read, the admitted
        rule's lifetime convention, once a read at least INTERVAL_S before
        it exists. Flags only.
        """
        window_ns = prewindow.INTERVAL_S * 1_000_000_000
        with self._snapshot_lock:
            readings = {identity: tuple(history) for identity, history in self._readings.items()}
            stamps = list(self._read_stamps)
            firsts = dict(self._first_listings)
            births = dict(self._birth_bounds)
            commands = dict(self._commands)
            scope = {(pid, start) for pid, holders in self._process_history.items()
                     for start, (_, matches) in holders.items() if matches}
        if not stamps:
            return []
        starts = [stamp[0] for stamp in stamps]
        flagged = {(row["pid"], row["start"]) for flag in self.contention_flags for row in flag["busy"]}
        busy = []
        for identity in sorted(scope - flagged):
            history = readings.get(identity, ())
            if not history:
                continue
            expanded = _expand_readings(history, stamps, starts)
            pair = _rate_pair(expanded)
            basis = "CPU between two readings of one process at least 30 s apart"
            if pair is None:
                pair = self._birth_pair(identity, expanded, stamps, firsts, births, window_ns)
                basis = "CPU since its birth bound, to the end of a later read"
            if pair is None:
                continue
            opening, closing, growth_cs, span_ns = pair
            evidence = {"pid": identity[0], "command": commands.get(identity, "?"), "start": identity[1],
                        "cpu_s_per_s": growth_cs / 100 / (span_ns / 1e9), "basis": basis}
            details = {"start_monotonic_s": opening[2] / 1e9, "end_monotonic_s": closing[2] / 1e9,
                       "elapsed_s": (closing[2] - opening[2]) / 1e9, "span_s": span_ns / 1e9,
                       "cpu_s": growth_cs / 100, "busy": [evidence]}
            receipt.setdefault("pair_history", []).append(details)
            note = (f"{growth_cs / 100:.2f} CPU-s over {span_ns / 1e9:.3f} s, above "
                    f"{prewindow.CPU_LIMIT_PERCENT / 100:g} CPU-s/s, from the reading at {opening[2] / 1e9:.3f} s "
                    f"to {closing[2] / 1e9:.3f} s")
            self._record_cpu_flags(receipt, details, [evidence], kind="pair_rate", note=note)
            busy.append(evidence)
        return busy

    @staticmethod
    def _birth_pair(identity, readings, stamps, firsts, births, window_ns):
        """The admitted lifetime rule from a newcomer's birth bound to each of its readings (lead T1-T2)."""
        index, printed_s = firsts.get(identity, (0, None))
        if index == 0:
            return None  # listed by the first read: no absence bounds its birth
        absent, sighted = stamps[index - 1], stamps[index]
        printed_ns = printed_s * 1_000_000_000 - max(absent[4], sighted[3])
        floor_ns = max(absent[0], printed_ns) if printed_ns <= sighted[1] else absent[0]
        bound = births.get(identity)
        if bound is not None:
            floor_ns = max(floor_ns, bound.lifetime_floor_ns)
        scale = 1_000_000_000 * _CPU_LIMIT_DEN
        best = None
        for reading in readings:
            span_ns = reading[1] - floor_ns
            if span_ns <= 0 or reading[2] - stamps[0][2] < window_ns:
                continue
            excess = reading[3] * scale - _CPU_LIMIT_NUM * span_ns
            if excess > 0 and (best is None or excess * best[1] > best[0] * span_ns):
                best = (excess, span_ns, reading)
        if best is None:
            return None
        _, span_ns, reading = best
        return (absent[0], absent[1], absent[2]), reading, reading[3], span_ns

    def _cpu_interval(self, receipt):
        # Admission's closing read can judge a second batch into its receipt.
        details = receipt.get("cpu_interval") or {"regressed_counters": [], "regressed_noncontaminant": []}
        judged = receipt.setdefault("cpu_intervals", [])
        dwell_ns = prewindow.INTERVAL_S * 1_000_000_000
        busy = []
        with self._snapshot_lock:
            snapshots = list(self._snapshots)
            observations = list(self._process_observations)
            births = dict(self._birth_bounds)
            readings = {identity: tuple(history) for identity, history in self._readings.items()}
            pending, self._pending = self._pending, self._empty_pending()
            background_failure = self._background_failure
        if pending["census"]:
            receipt.setdefault("background_snapshots_monotonic_s", []).extend(
                row["monotonic_s"] for row in pending["census"])
            receipt.setdefault("background_census", []).extend(pending["census"])
        if pending["wall_clock_backwards"]:
            receipt["wall_clock_backwards"] = True
        opening = None
        try:
            for end in range(self._judged_end + 1, len(snapshots)):
                # The newest opening at least INTERVAL_S before this end: the
                # window slides by one snapshot, so its opening never passes
                # the previous end and every stretch is judged.
                start = next((i for i in range(end - 1, -1, -1)
                              if snapshots[end].midpoint_ns - snapshots[i].midpoint_ns >= dwell_ns), None)
                long_interval = None
                flagged = set()
                if start is not None:  # None only at the admission's mid-baseline snapshot
                    interval_details = {"regressed_counters": [], "regressed_noncontaminant": []}
                    reads = _window_reads(observations, snapshots[start], snapshots[end])
                    endpoint, endpoint_busy, lifetime_busy = self._judge_cpu_interval(
                        snapshots[start], snapshots[end], interval_details, reads=reads, births=births)
                    judged.append(interval_details)
                    details = interval_details
                    self._judged_end, opening = end, start
                    busy.extend(endpoint_busy + lifetime_busy)
                    if interval_details["long_interval"]:
                        long_interval = interval_details["elapsed_s"]
                    else:
                        self._record_interval_flags(receipt, interval_details, endpoint, endpoint_busy, lifetime_busy)
                        flagged.update((row["pid"], row["start"]) for row in endpoint_busy + lifetime_busy)
                    # Lead S2: every pair this sample closes, not only the newest window.
                    paired = self._judge_pairs(receipt, "series", snapshots, start, snapshots[end],
                                               observations, births)
                    busy.extend(paired)
                    flagged.update((row["pid"], row["start"]) for row in paired)
                # The exact check at this sample, against every earlier sample
                # at most INTERVAL_S before it and each newcomer's birth bound.
                busy.extend(self._exact_windows(receipt, snapshots, births, end, dwell_ns, flagged))
                # Lead P1, over each process's whole sampled life.
                busy.extend(self._proven_windows(receipt, snapshots[end], births, readings, flagged))
                if long_interval is not None:
                    receipt["long_interval"] = True
                    raise Refused(
                        f"census indeterminate: judged CPU window of {long_interval:.1f} s "
                        f"exceeds {self.MAX_WINDOW_S:g} s (background snapshots stalled)")
        finally:
            for row in pending["regressed_counters"]:
                for key in ("regressed_counters", "regressed_noncontaminant"):
                    if key == "regressed_noncontaminant" and row["contaminant"]:
                        continue
                    if all((entry["pid"], entry["start"]) != (row["pid"], row["start"])
                           for entry in details[key]):
                        details[key].append(row)
            receipt["cpu_interval"] = details
            receipt["host_aggregate_cpu"] = [
                {key: interval[key] for key in
                 ("outside_aggregate_cpu_s_per_s", "aggregate_above_0_05")}
                for interval in judged]
            receipt["busy"] = receipt.get("busy", []) + busy
        if opening:
            # Keep the newest opening, every sample less than INTERVAL_S
            # before it (later pairs open there, lead S2) and everything
            # after it; the next window's opening can only be later.
            keep = next(i for i in range(opening + 1)
                        if snapshots[i].midpoint_ns > snapshots[opening].midpoint_ns - dwell_ns)
            if keep:
                with self._snapshot_lock:
                    del self._snapshots[:keep]
                self._judged_end -= keep
        # Completed windows precede a later failed census or stale tail.
        if background_failure:
            # This copy belongs to the snapshots judged above. A later latch
            # is caught where the verdict ends.
            raise Refused(f"census refused or indeterminate in the background sampler: {background_failure}")
        if "monotonic_s" in receipt:
            self._require_fresh_background(receipt["monotonic_s"], snapshots[-1] if snapshots else None)
        return busy

    def _judge_cpu_interval(self, opening, current, details, *, reads, births, previous_over=None):
        limit = prewindow.CPU_LIMIT_PERCENT / 100

        def measure(before, after, prior=None):
            return contention.interval(before, after, tree_roots=(), include_kernel_task=True,
                                       limit=limit, previous_over=prior)

        # Only the caller's admitted sequence uses the paired args read as
        # part of its timestamp. Daemon selection and rates both use the
        # accounting clock, even when the subsequent args query runs long.
        admitted = previous_over is not None
        before, after = opening, current
        if admitted:
            before, after = opening.admitted_endpoint(), current.admitted_endpoint()
        endpoint_elapsed_ns = after.midpoint_ns - before.midpoint_ns
        raw = measure(before, after, previous_over)
        # Endpoint counters provide the existing regression and host aggregate
        # diagnostics. The admitted verdict uses the raw endpoint counters.
        peak_opening, peak_current = _with_peak_counters(before), _with_peak_counters(after)
        measured = raw if peak_opening is before and peak_current is after else measure(peak_opening, peak_current)
        sampled_elapsed = (current.midpoint_ns - opening.midpoint_ns) / 1e9
        details.update({
            "start_monotonic_s": opening.midpoint_ns / 1e9,
            "end_monotonic_s": current.midpoint_ns / 1e9,
            "elapsed_s": sampled_elapsed, "contaminants": [],
            "unaccounted": raw["unaccounted"],
            "long_interval": sampled_elapsed > self.MAX_WINDOW_S})
        divergence_ns = _wall_divergence_ns(reads)
        details["wall_clock_divergence_s"] = divergence_ns / 1e9
        details["wall_clock_diverged"] = divergence_ns > WALL_DIVERGENCE_LIMIT_NS
        # Journaled like CpuQuietProbe's aggregate: flagged, never judged.
        aggregate = measured["outside_aggregate_cpu_s_per_s"]
        details["outside_aggregate_cpu_s_per_s"] = aggregate
        details["aggregate_above_0_05"] = aggregate is not None and aggregate > limit
        matches = {}
        for snapshot in (opening, current):
            for identity, row in snapshot.rows.items():
                if row["contaminant"]:
                    matches.setdefault(identity, set()).update(row["contaminant_matches"])
        def contaminant(row):
            return (row["pid"], row["start"]) in matches
        regressions = [row for row in raw["unaccounted"] if row["reason"] == "counter regressed"]
        for row in regressions:
            entry = {**row, "contaminant": contaminant(row)}
            for key in ("regressed_counters", "regressed_noncontaminant"):
                if key == "regressed_noncontaminant" and entry["contaminant"]:
                    continue
                recorded = details[key]
                recorded[:] = [entry for entry in recorded
                               if (entry["pid"], entry["start"]) != (row["pid"], row["start"])]
                recorded.append(entry)
        # An unproven regression alone is disclosure.
        if measured["error"] and measured["error"] != contention.REGRESSED_COUNTER_ERROR:
            raise Refused(f"census indeterminate: {measured['error']}")
        endpoint = {"start_monotonic_s": before.midpoint_ns / 1e9, "end_monotonic_s": after.midpoint_ns / 1e9,
                    "elapsed_s": raw["elapsed_s"]}
        details["endpoint_interval"] = endpoint
        endpoint_evidence = raw if admitted else measured
        endpoint_busy = {(row["pid"], row["start"]): row for row in endpoint_evidence["outside_over_limit"] if contaminant(row)}
        if previous_over is not None:
            previous_over.clear()
            previous_over.update((key, rate) for key, rate in contention.over_limit(raw).items() if key in matches)
        evidence, details["contaminants"] = _overlap_cpu_evidence(
            opening, current, reads, endpoint_elapsed_ns=endpoint_elapsed_ns,
            births=births, initial=self._initial_identities)
        same_window = before.midpoint_ns == opening.midpoint_ns and after.midpoint_ns == current.midpoint_ns
        lifetime_busy = []
        for row in evidence:
            key = row["pid"], row["start"]
            if key in opening.rows and key in current.rows:
                endpoint_busy.setdefault(key, row)
            elif key not in endpoint_busy or not same_window:
                lifetime_busy.append(row)
        details["exited_over_limit"] = [row for row in lifetime_busy if (row["pid"], row["start"]) not in current.rows]
        return endpoint, list(endpoint_busy.values()), lifetime_busy

    def _record_refusal(self, receipt, error):
        if not any(item is receipt for item in self.receipts):
            self.receipts.append(receipt)
        # An exception without a message still latches.
        self.failure = str(error) or type(error).__name__
        receipt["refusal"] = self.failure
        return Refused(self.failure)

    def check(self, *, force=False):
        if self.failure is not None:
            raise Refused(self.failure)
        receipt = {"resolved_custody_parents": []}
        try:
            now = self._now()
            # The throttle skips repeated probes. It never skips a latched
            # failure, a completed window awaiting judgment or a stale sample.
            if not force and now - self.last < 15 and not self._stop_sampler.is_set():
                latest, queued, failure = self._sampler_state()
                if (not failure and not queued and latest is not None
                        and now - latest.finished.monotonic_ns / 1e9 <= self.MAX_WINDOW_S):
                    return
            receipt["monotonic_s"] = now
            self.receipts.append(receipt)
            current = None
            if self._sampler is None:
                self._census(receipt)
                if not self._snapshots:
                    first = self._cpu_snapshot()
                    self._admission_snapshots.append(first)
                    # A mid-baseline snapshot: the daemon's first window
                    # (ending one cadence after admission) opens here, so it
                    # is 30 s, not 45 s (cold MEDIUM-1).
                    self.sleep(prewindow.INTERVAL_S / 2)
                    self._cpu_snapshot()
                    self.sleep(prewindow.INTERVAL_S / 2)
                    current = self._cpu_snapshot()
                    # Preserve the first forced call's full baseline wait.
                    if current.midpoint_ns - first.midpoint_ns < prewindow.INTERVAL_S * 1e9:
                        raise Refused("census indeterminate: initial CPU baseline shorter than 30 s")
            self._cpu_interval(receipt)
            self._census(receipt)
            self._admission_interval(receipt, current)
            # Lead S2: P1 over every pair of each process's history at
            # admission too, not only at the final verdict.
            self._proven_history(receipt)
            self.last = self._now()
            self._start_sampler()
            self._close_admission(receipt)
        except Exception as exc:
            refusal = self._record_refusal(receipt, exc)
            self.close()
            raise refusal from exc


# Keep the install log read bounded (cold LOW-4).
INSTALL_LOG_TAIL_BYTES = 8 * 1024 * 1024


def _log_tail(path, limit):
    with open(path, "rb") as handle:
        size = handle.seek(0, os.SEEK_END)
        handle.seek(max(0, size - limit))
        data = handle.read(limit)
    if size > limit:
        data = data.split(b"\n", 1)[1] if b"\n" in data else b""  # drop a partial first line
    return data.decode("utf-8", errors="replace")


def softwareupdate_scan_forecast(start, deadline, *, log_path=Path("/var/log/install.log"),
                                 tail_bytes=INSTALL_LOG_TAIL_BYTES):
    """Predict six-hour softwareupdated scans; advisory only, never a gate.

    Use the latest AutoBackgroundScanFinished line in the last ``tail_bytes``
    of install.log to project six-hour scans in [start, deadline] in UTC.
    Unzoned inputs and log lines are interpreted as UTC. A read or parse
    problem gives status "unknown".
    """
    def utc(value):
        if isinstance(value, datetime):
            return value.replace(tzinfo=timezone.utc) if value.tzinfo is None else value.astimezone(timezone.utc)
        return datetime.fromtimestamp(value, timezone.utc)

    try:
        start, deadline = utc(start), utc(deadline)
        if deadline < start:
            raise ValueError("deadline precedes start")
        latest = None
        # An explicit offset may follow the seconds directly or after spaces.
        pattern = re.compile(
            r"(?:(?P<iso>\d{4}-\d\d-\d\d[ T]\d\d:\d\d:\d\d)(?:\s*(?P<zone>Z|[+-]\d\d(?::?\d\d)?))?"
            r"|(?P<syslog>[A-Z][a-z]{2}\s+\d{1,2}\s+\d\d:\d\d:\d\d)).*AutoBackgroundScanFinished")
        for line in _log_tail(log_path, tail_bytes).splitlines():
            match = pattern.search(line)
            if not match:
                continue
            parsed = utc(datetime.fromisoformat(match["iso"] + (match["zone"] or ""))
                         if match["iso"] else
                         datetime.strptime(f"{start.year} {match['syslog']}", "%Y %b %d %H:%M:%S"))
            if latest is None or parsed > latest:
                latest = parsed
        window = [start.isoformat(), deadline.isoformat()]
        if latest is None:
            return {"status": "unknown", "predicted": [], "window": window}
        predicted = []
        next_scan = latest + timedelta(hours=6)
        while next_scan < start:
            next_scan += timedelta(hours=6)
        while next_scan <= deadline:
            predicted.append(next_scan.isoformat())
            next_scan += timedelta(hours=6)
        return {"status": "forecast", "last_finished": latest.isoformat(),
                "cadence_hours": 6, "predicted": predicted, "window": window}
    except (OSError, ValueError, TypeError, OverflowError):
        return {"status": "unknown", "predicted": []}


def _hub_blob(path, hub_root):
    """Resolve each link inside the hub before inspecting its target."""
    pending = list(path.relative_to(hub_root).parts)
    resolved, links = hub_root, 0
    while pending:
        part, *pending = pending
        if part == "restricted":
            raise ValueError(f"refusing restricted target: {path}")
        if part == "..":
            if resolved == hub_root:
                raise ValueError(f"symlink escapes hub root: {path}")
            resolved = resolved.parent
            continue
        candidate = resolved / part
        if candidate.is_symlink():
            links += 1
            if links > 40:
                raise ValueError(f"symlink loop: {path}")
            target = Path(os.readlink(candidate))
            if target.is_absolute():
                if not target.is_relative_to(hub_root):
                    raise ValueError(f"symlink escapes hub root: {path}")
                resolved = hub_root
                target = target.relative_to(hub_root)
            pending = list(target.parts) + pending
        else:
            resolved = candidate
    relative = resolved.relative_to(hub_root)
    if (len(relative.parts) != 3 or not relative.parts[0].startswith("models--")
            or relative.parts[1] != "blobs" or not resolved.is_file()):
        raise ValueError(f"not a regular HF hub blob: {path}")
    return resolved


def inventory(root, tick=lambda: None):
    """Hash local files, including confined HF snapshot-to-blob links.

    Only a models--*/snapshots/<revision> root enables file links. Each must
    resolve to a regular models--*/blobs/<file> within that same hub directory.
    Directory links, escaping links and restricted components always refuse.
    """
    root = Path(root)
    if "restricted" in root.parts or root.is_symlink() or not root.is_dir():
        raise ValueError(f"not a materialized unrestricted directory: {root}")
    root = root.resolve()
    if "restricted" in root.parts:
        raise ValueError(f"refusing restricted directory: {root}")
    hub_root = (root.parent.parent.parent if root.parent.name == "snapshots"
                and root.parent.parent.name.startswith("models--") else None)
    rows = []
    def walk(directory):
        # os.walk classifies links with a target stat before yielding them.
        # Inspect links first so escapes refuse before any target access.
        with os.scandir(directory) as stream:
            entries = sorted(stream, key=lambda entry: entry.name)
        for entry in entries:
            tick()
            path = Path(entry.path)
            if entry.name == "restricted":
                raise ValueError(f"refusing restricted path: {path}")
            if entry.is_symlink():
                if hub_root is None:
                    raise ValueError(f"not an HF snapshot link: {path}")
                yield path, _hub_blob(path, hub_root)
            elif entry.is_dir(follow_symlinks=False):
                yield from walk(path)
            elif entry.is_file(follow_symlinks=False):
                yield path, path
            else:
                raise ValueError(f"not a regular materialized file: {path}")
    for path, target in walk(root):
        digest = hashlib.sha256()
        size = 0
        with target.open("rb") as handle:
            for chunk in iter(lambda: handle.read(8 * 1024 * 1024), b""):
                tick()
                digest.update(chunk)
                size += len(chunk)
        rows.append({"path": path.relative_to(root).as_posix(),
                     "bytes": size, "sha256": digest.hexdigest()})
    if not rows:
        raise ValueError(f"empty inventory: {root}")
    return sorted(rows, key=lambda row: row["path"])


def disk_census(config, pins, tick=lambda: None):
    """Report R0 storage and local model hashes; no W1 arm gates or offloads."""
    budget = step_budget(config.get("smc_step"))
    free = shutil.disk_usage(config["disk_path"]).free
    anchor_files = inventory(config["anchor_source"], tick)
    models = {}
    for tag, entry in config["models"].items():
        rows = inventory(entry["source"], tick)
        total = sum(row["bytes"] for row in rows)
        models[tag] = {"files": rows, "bytes": total,
                       "design_download_bytes": pins[tag]["bytes"],
                       "difference_bytes": total - pins[tag]["bytes"],
                       "revision": pins[tag]["revision"],
                       "identity_note": "Local hashes; revision is configured, not independently authenticated."}
    return {"status": "diagnostic", "purpose": "r0_report_only",
            "free_bytes_after_present_weights": free, "smc_step_budget": budget,
            "w1_required_free_bytes_after_r0": 80_000_000_000,
            "design": {"W1_bytes_per_copy": 18_710_000_000, "W1_two_copies_bytes": 37_400_000_000,
                       "D_two_copies_bytes": 52_900_000_000, "disk_figures_are_rounded_planning_estimates": True},
            "anchor": {"files": anchor_files, "bytes": sum(r["bytes"] for r in anchor_files),
                       "revision": "d388dead1515f5e085ef7a0431dd8fadf0886c57",
                       "identity_note": "Local hashes; remote revision not independently authenticated."},
            "models": models, "offloads": [],
            "configured_w1_offload_labels": [item["label"] for item in config.get("offloads", [])],
            "note": "R0 disk check is report-only. Free space and configured offload hashes gate W1 via w1_disk_gate."}


def w1_disk_gate(config, tick=lambda: None):
    """Require 80 decimal GB after R0 and verify every configured offload.

    Call at W1 arm time, after R0's journal has been written. This read-only
    check neither performs offloads nor grants an arm authorization.
    """
    free = shutil.disk_usage(config["disk_path"]).free
    offloads = []
    for item in config.get("offloads", []):
        tick()
        row = {"label": item["label"], "pass": False,
               "inventory": item["inventory"], "destination": item["destination"]}
        offloads.append(row)
        try:
            # Saved BEFORE offload; the source need not remain on local disk.
            expected = json.loads(Path(item["inventory"]).read_text())
            actual = inventory(item["destination"], tick)
            row.update(observed=actual, **{"pass": isinstance(expected, list) and bool(expected) and expected == actual})
        except (OSError, ValueError) as exc:
            row["error"] = f"{type(exc).__name__}: {exc}"
    return {"status": "pass" if free >= 80_000_000_000 and all(row["pass"] for row in offloads) else "fail",
            "purpose": "w1_arm_gate", "free_bytes_after_present_weights": free,
            "required_free_bytes_after_r0": 80_000_000_000, "offloads": offloads,
            "required_offload_labels": [row["label"] for row in offloads]}


def swap_bytes(run=command):
    text = run(("/usr/sbin/sysctl", "-n", "vm.swapusage"))
    match = re.search(r"used\s*=\s*([0-9.]+)([KMG])", text)
    if not match:
        raise ValueError("vm.swapusage used value unavailable")
    return int(float(match[1]) * {"K": 1024, "M": 1024**2, "G": 1024**3}[match[2]])


def host_identity(expected_model, run=command):
    """Always gate native model work, including CLI subsets, on host capacity."""
    try:
        memory = int(run(("/usr/sbin/sysctl", "-n", "hw.memsize")).strip())
        model = run(("/usr/sbin/sysctl", "-n", "hw.model")).strip()
    except Exception as exc:
        return {"status": "fail", "error": str(exc)}
    return {"status": "pass" if memory >= 128 * 1024**3 and model == expected_model else "fail",
            "hw_memsize": memory, "hw_model": model, "expected_hw_model": expected_model,
            "minimum_memory_bytes": 128 * 1024**3}


def host_snapshot(run=command):
    probes = {"pmset_custom": ("/usr/bin/pmset", "-g", "custom"),
              "pmset_battery": ("/usr/bin/pmset", "-g", "batt"),
              "pmset_thermal": ("/usr/bin/pmset", "-g", "therm"),
              "wired_limit": ("/usr/sbin/sysctl", "iogpu.wired_limit_mb"),
              "physical_memory": ("/usr/sbin/sysctl", "-n", "hw.memsize")}
    out = {}
    for name, argv in probes.items():
        try:
            out[name] = {"status": "pass", "stdout": run(argv)}
        except Exception as exc:
            out[name] = {"status": "fail", "error": str(exc)}
    batt = out["pmset_battery"].get("stdout", "")
    custom = out["pmset_custom"].get("stdout", "")
    settings = custom.split("AC Power:")[-1] if "AC Power:" in custom else ""
    mode = re.search(r"(?m)^\s*powermode\s+(\d+)\s*$", settings)
    low = re.search(r"(?m)^\s*lowpowermode\s+(\d+)\s*$", settings)
    powered = "AC Power" in batt
    # macOS 26 spells this powermode, older versions lowpowermode. Both
    # Automatic (0) and explicitly observed High Power (2) are recorded.
    power_ok = bool((mode and mode[1] in {"0", "2"}) or (not mode and low and low[1] == "0"))
    readiness = {"on_ac": powered, "power_mode_ok": power_ok,
                 "observed_power_mode": mode[1] if mode else None,
                 "observed_lowpowermode": low[1] if low else None}
    return {"status": "pass" if powered and power_ok and all(r["status"] == "pass" for r in out.values()) else "fail",
            "probes": out, "readiness": readiness,
            "note": "Read-only desk readiness; R1 lever adoption and arm readiness require their own gates."}


DISPLAY_TRANSITION = re.compile(
    r"^(\d{4}-\d\d-\d\d \d\d:\d\d:\d\d [+-]\d{4})\s.*?\bDisplay is turned (on|off)\b", re.M)


def display_census(started_epoch, finished_epoch, run=subprocess.run):
    """R0-L3 display ruling (RUN_STATE 206): record, never refuse.

    Records `pmset -g`'s displaysleep value, the display state at the run's
    start (the last transition before it) and every `pmset -g log` display
    transition inside [started_epoch, finished_epoch].
    """
    record = {"displaysleep_minutes": None, "display_at_start": None, "transitions": [],
              "display_woke_during_run": None}
    env = _tool_env()
    try:
        settings = run(("/usr/bin/pmset", "-g"), capture_output=True, text=True, timeout=15, env=env)
        match = re.search(r"(?m)^\s*displaysleep\s+(\d+)", settings.stdout)
        record["displaysleep_minutes"] = int(match[1]) if match else None
    except Exception as exc:
        record["pmset_g_error"] = f"{type(exc).__name__}: {exc}"
    try:
        log = run(("/usr/bin/pmset", "-g", "log"), capture_output=True, text=True, timeout=60, env=env)
        for match in DISPLAY_TRANSITION.finditer(log.stdout):
            when = datetime.strptime(match[1], "%Y-%m-%d %H:%M:%S %z").timestamp()
            if when < started_epoch:
                record["display_at_start"] = match[2]
            elif when <= finished_epoch:
                record["transitions"].append({"state": match[2], "epoch_s": when, "line": match[0].strip()})
        record["display_woke_during_run"] = any(t["state"] == "on" for t in record["transitions"])
    except Exception as exc:
        record["pmset_log_error"] = f"{type(exc).__name__}: {exc}"
    return record


def smc_enumeration(repo, output, step=None):
    try:
        profile = profile_config(step)
    except ProfileRefused as exc:
        return {"status": "refused", "refusal_code": exc.code, "reason": str(exc)}
    budget = step_budget(profile)
    script = Path(repo) / "scripts/align_smc_enumerate.py"
    if not script.is_file():
        return {"status": "unavailable", "reason": "SMC lane not integrated"}
    import sys
    from joulewise.align.apple.smc_enumeration import CONTENTION_REDO_EXIT
    output = Path(output)
    redone = []
    # R0-L3: ruling 8 in R0. A sustained episode (largest single process,
    # kernel_task excluded, >=0.5 cores for 60 s)
    # abandons the first capture for ONE redo; the redo records any further
    # episode as `contended` rather than abandoning or refusing.
    for policy in ("redo", "flag"):
        argv = [sys.executable, "-B", str(script), "--output", str(output), "--gpu-step",
                "--idle-seconds", str(profile["idle_seconds"]), "--idle-max-seconds", str(profile["idle_max_seconds"]),
                "--load-seconds", str(profile["load_seconds"]),
                "--recovery-seconds", str(profile["recovery_seconds"]), "--contention-policy", policy]
        result = subprocess.run(argv, capture_output=True, text=True, timeout=budget["timeout_seconds"],
                                env=_tool_env())
        if policy == "flag" or result.returncode != CONTENTION_REDO_EXIT:
            break
        attempt = {"argv": argv, "exit_code": result.returncode, "stderr": result.stderr,
                   "reason": "sustained background CPU contention (R0-L3 redo)"}
        rejected = output.with_name(f"{output.name}.rejected{len(redone) + 1}")
        if output.is_dir():
            try:
                attempt["contention"] = json.loads((output / "contention.json").read_text())
            except (OSError, ValueError) as exc:
                attempt["contention_error"] = f"{type(exc).__name__}: {exc}"
            output.rename(rejected)
            attempt["output_dir"] = str(rejected)
        redone.append(attempt)
    receipt = {"status": "fail" if result.returncode else "inconclusive",
               "contention_redo": redone, "contended": False,
               "argv": argv, "exit_code": result.returncode, "smc_step_budget": budget,
               "timeout_seconds": budget["timeout_seconds"],
               "stdout": result.stdout, "stderr": result.stderr,
               "smc_source_commit": "58525031a",
               "selection_status": "PROVISIONAL",
               "step_ruling": "docs/align/r0_step_test_ruling.md",
               "note": "Idle plus load-step selection; R1 still owns thermal-control qualification."}
    if result.returncode:
        return receipt
    try:
        payload = json.loads((Path(output) / "r0.json").read_text())
        if payload["schema"] != "joulewise.align_smc_r0.v1" or payload["gpu_step"] is not True:
            raise ValueError("not a #658 GPU-step receipt")
        if payload["samples_journal"] != "samples.jsonl":
            raise ValueError("unexpected SMC journal name")
        raw = (Path(output) / "samples.jsonl").read_bytes()
        if hashlib.sha256(raw).hexdigest() != payload["samples_sha256"]:
            raise ValueError("SMC journal SHA-256 mismatch")
        samples = [json.loads(line) for line in raw.splitlines() if line.strip()]
        # Authenticate observed adaptive phase lengths before either analysis.
        phases = payload["phases"]
        if [p["phase"] for p in phases] != ["idle", "load", "recovery"]:
            raise ValueError("SMC step phases must be idle, load, recovery")
        previous = 0
        duration_flags = []
        for phase in phases:
            begin, end = phase["start_s"], phase["end_s"]
            if (type(begin) not in (int, float) or type(end) not in (int, float)
                    or not math.isfinite(begin) or not math.isfinite(end) or begin < previous or end <= begin):
                raise ValueError("invalid SMC phase bounds")
            duration = end-begin
            # Erratum 2: deviation >one 1 Hz period is a bookkeeping flag,
            # never a refusal; quiet probes can overrun a phase deadline.
            # Adaptive idle is compared to its configured [minimum, cap].
            if phase["phase"] == "idle":
                deviation = duration - min(max(duration, profile["idle_seconds"]), profile["idle_max_seconds"])
            else:
                deviation = duration-profile[phase["phase"]+"_seconds"]
            if abs(deviation) > 1:
                duration_flags.append({"phase": phase["phase"], "actual_seconds": duration,
                                       "deviation_seconds": deviation})
            previous = end
        receipt["phase_duration_flags"] = duration_flags
        # The old load-fit block is diagnostic only. It expects exact fixed
        # lengths; use this capture's actual phase lengths, never the idle cap.
        diagnostic_profile = {p["phase"]+"_seconds": p["end_s"]-p["start_s"] for p in phases}
        try:
            diagnostic = rank_response(payload, samples, {
                k: round(v) for k, v in diagnostic_profile.items()})
        except ValueError as exc:
            diagnostic = {"status": "unavailable", "reason": str(exc)}
        # Erratum 4: a legacy journal has only actual ends. Reconstruct fixed
        # deadlines from the invoked profile, and adaptive idle from its
        # deciding evaluation (recorded by new collectors), bounded by its cap.
        grid_phases = []
        for phase in phases:
            name, begin = phase["phase"], phase["start_s"]
            deadline = (min(phase.get("deadline_s", phase["end_s"]), begin+profile["idle_max_seconds"])
                        if name == "idle" else begin+profile[name+"_seconds"])
            grid_phases.append({**phase, "deadline_s": deadline})
        classification = classify_smc({**payload, "phases": grid_phases, "samples": samples}, stage="r0")
        selection = {name: classification[name] for name in ("s_fast", "s_slow")}
        resolved = all(isinstance(v, str) and re.fullmatch(r"T[!-~]{3}", v) for v in selection.values())
        resolved = resolved and selection["s_fast"] != selection["s_slow"]
        receipt.update(selection=selection, response=classification,
                       **{field: classification[field] for field in (
                           "heat_ordering_reference", "heat_ordering_reference_rise", "heat_ordering_excluded",
                           "recovery_onset_gap_s", "heat_ordering_indeterminate",
                           "heat_ordering_exclusion_count", "heat_ordering_wide_exclusion")},
                       selected_key_aliases=classification["selected_key_aliases"],
                       exponential_fit_diagnostic=diagnostic, source_response=payload["response"])
        receipt["capture_coverage_diagnostic"] = payload["coverage"]
        # R0-L3: the capture's contention receipts and flag, read beside the
        # picks; recorded, never a refusal. A legacy payload has none.
        receipt["contention"] = classification["contention"]
        receipt["contention_by_phase"] = classification["contention_by_phase"]
        receipt["contended"] = bool((payload.get("contention") or {}).get("contended"))
        by_key = {row["key"]: row for row in classification["ranking"]}
        selected_rows = {key: by_key[key] for key in selection.values() if key in by_key}
        receipt["selected_key_readability"] = {key: {field: row[field] for field in (
            "phase_coverage", "phase_read_error_fraction", "phase_seconds", "phase_valid_samples",
            "phase_max_empty_cells", "period_ns", "max_interval_ns", "baseline_unsettled", "baseline_slope_c_min")}
            for key, row in selected_rows.items()}
        # Keep the capture's nominal one-Hz period assertion; the capture-wide
        # occupancy fraction itself is diagnostic and never refuses a pick.
        readable = (resolved and classification["readability_bar_met"]
                    and payload["coverage"]["period_ns"] == 1_000_000_000)
        for row in selected_rows.values():
            # Erratum 2 D6: per-phase one-second-cell occupancy >=99%, <1%
            # read errors, no two adjacent empty cells (U1(c)'s 2 s window).
            # The old total >=600 s bar was vacuous under this step profile.
            readable = (readable and row["period_ns"] == 1_000_000_000
                        and all(v >= .99 for v in row["phase_coverage"].values())
                        and all(v < .01 for v in row["phase_read_error_fraction"].values())
                        and all(v < 2 for v in row["phase_max_empty_cells"].values()))
        receipt["readability_bar_met"] = bool(readable)
        if not resolved:
            receipt["reason"] = "SMC die/heatsink selection unresolved"
        elif not readable:
            receipt["reason"] = "SMC selected-key coverage does not meet 1 Hz / >=99% per phase / <1% errors / no consecutive empty cells"
        else:
            receipt["status"] = "pass"
            receipt["reason"] = "WP14(a) model-free classifier and readability bars met; picks PROVISIONAL"
    except (OSError, ValueError, KeyError, TypeError) as exc:
        receipt["reason"] = f"SMC r0.json selection unavailable: {exc}"
    return receipt
