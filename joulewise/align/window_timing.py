"""Offline, timing-only worksheet for explicitly named committed window records.

No capture imports, filesystem discovery, path following, or measurement reads.
All intervals are half-open integer nanoseconds on the recorded epoch axis.
This is an accounting diagnostic, never a hardware/eligibility qualification.
See docs/perf/2026-11-08-eng-timing.md for supported sources and limitations.
R0 duration budgets and archival NOTE limits: docs/perf/2026-11-08-r0-timing.md.
"""
from __future__ import annotations

import argparse
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal, InvalidOperation
import hashlib
import json
import os
import subprocess

NS = 1_000_000_000
# Reader diagnostics only: 20 ppm allows the review's ~9.2 ppm ordinary drift.
# The 1 ms floor covers short records. Neither is a capture acceptance rule.
CLOCK_DRIFT_PPM = 20
CLOCK_FLOOR_NS = 1_000_000
PHASES = ("arm", "dwell", "idle", "scaffold", "decode", "gates", "holds",
          "references", "finalize", "offload", "unattributed")


def ns(seconds):
    if isinstance(seconds, bool) or not isinstance(seconds, (int, float, Decimal)):
        raise ValueError("timestamp/duration must be numeric")
    value = Decimal(str(seconds))
    if not value.is_finite():
        raise ValueError("timestamp/duration must be finite")
    return int((value * NS).to_integral_value())


def integer(value):
    if type(value) is not int:
        raise ValueError("nanosecond timestamp must be an integer")
    return value


def drift_allowance(elapsed_ns):
    return max(CLOCK_FLOOR_NS, (abs(elapsed_ns)*CLOCK_DRIFT_PPM+999_999)//1_000_000)


def drift_detail(delta, elapsed):
    ppm = delta*1_000_000/elapsed if elapsed else None
    return f"wall_minus_monotonic_ns={delta} drift_ppm={ppm}"


def safe_path(path):
    """Validate text before asking Git anything about a source path."""
    if not isinstance(path, str) or not path or path.startswith(("/", "-")):
        raise ValueError("source must be a repository-relative path")
    parts = path.split("/")
    if any(p in ("", ".", "..", ".git", "restricted", "night-custody", "night-archive")
           or p.startswith(("jw-b5-", "night-")) for p in parts):
        raise ValueError("forbidden source path")
    if any(c in path for c in ("\\", ":", "\x00", "\n", "\r")):
        raise ValueError("invalid source path")
    return path


class GitRecords:
    """Read regular blobs at one pinned local commit; never open record paths.

    Git may use the clone's configured shared object store. No fetch, working
    tree reads, symlink resolution, hooks, or Git LFS/smudge filters are run.
    """
    def __init__(self, repo, ref):
        self.repo = os.fspath(repo)
        self.env = {**os.environ, "GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": os.devnull,
                    "GIT_OPTIONAL_LOCKS": "0", "GIT_NO_LAZY_FETCH": "1"}
        self.commit = self._git("rev-parse", "--verify", "--end-of-options", ref+"^{commit}").decode().strip()

    def _git(self, *args):
        result = subprocess.run(["git", "--no-replace-objects", "-C", self.repo, *args],
                                capture_output=True, env=self.env)
        if result.returncode:
            raise ValueError("local Git read failed: " + result.stderr.decode(errors="replace").strip())
        return result.stdout

    def read(self, path):
        path = safe_path(path)
        row = self._git("ls-tree", "-z", self.commit, "--", ":(literal)"+path)
        if not row:
            raise FileNotFoundError(path)
        mode_type_oid, name = row.rstrip(b"\0").split(b"\t", 1)
        mode, kind, oid = mode_type_oid.split()
        if name.decode() != path or mode not in (b"100644", b"100755") or kind != b"blob":
            raise ValueError("source must be one committed regular file: " + path)
        return self._git("cat-file", "blob", oid.decode())


@dataclass(frozen=True)
class Interval:
    start_ns: int
    end_ns: int
    phase: str
    source: str
    priority: int
    member: str | None = None
    activity: str | None = None

    def __post_init__(self):
        if integer(self.end_ns) < integer(self.start_ns):
            raise ValueError("reversed interval: " + self.source)
        if self.phase not in PHASES:
            raise ValueError("unknown phase: " + self.phase)


def partition(start_ns, end_ns, intervals):
    """Sweep intervals; refine parent contexts without counting them twice.

    Equal-priority contradictory labels remain unattributed (with all source
    locators). Reference context changes the window phase while preserving
    the inner member activity. No duration-only sum becomes an interval.
    """
    if end_ns < start_ns:
        raise ValueError("reversed ledger bounds")
    edges = defaultdict(list)
    edges[start_ns]
    edges[end_ns]
    for i, span in enumerate(intervals):
        a, b = max(start_ns, span.start_ns), min(end_ns, span.end_ns)
        if a < b:
            edges[a].append((i, span))
            edges[b].append((i, None))
    active = {}
    result = []
    points = sorted(edges)
    for a, b in zip(points, points[1:]):
        for i, span in edges[a]:
            if span is None:
                active.pop(i, None)
            else:
                active[i] = span
        if a == b:
            continue
        priority = max((i.priority for i in active.values()), default=-1)
        top = [i for i in active.values() if i.priority == priority]
        labels = {(i.phase, i.member, i.activity or i.phase) for i in top}
        ambiguous = len(labels) > 1
        phase, member, activity = next(iter(labels)) if len(labels) == 1 else ("unattributed", None, "unattributed")
        if not ambiguous and any(i.phase == "references" for i in active.values()):
            phase = "references"
        row = dict(start_ns=a, end_ns=b, phase=phase, member=member, activity=activity,
                   ambiguous=ambiguous, sources=sorted({i.source for i in active.values()}))
        if result and all(result[-1][k] == row[k] for k in row if k not in ("start_ns", "end_ns")):
            result[-1]["end_ns"] = b
        else:
            result.append(row)
    return result


def totals(rows, key):
    result = {p: 0 for p in PHASES} if key == "phase" else {}
    for row in rows:
        label = row[key]
        result[label] = result.get(label, 0) + row["end_ns"] - row["start_ns"]
    return result


class _Reader:
    def __init__(self, read_blob):
        self.read_blob = read_blob
        self.sources = {}
        self.raw = {}
        self.warnings = []
        self.intervals = []
        self.bounds = []
        self.members = {}
        self.attempts = []
        self.stages = []

    def warn(self, source, reason):
        self.warnings.append(source+": "+reason)

    def blob(self, path):
        safe_path(path)
        if path not in self.sources:
            try:
                raw = self.read_blob(path)
            except (KeyError, FileNotFoundError):
                self.warn(path, "source_unavailable")
                return None
            self.sources[path] = {"sha256": hashlib.sha256(raw).hexdigest(), "bytes": len(raw)}
            self.raw[path] = raw
        return self.raw[path]

    def load(self, path, lines=False):
        raw = self.blob(path)
        if raw is None:
            return [] if lines else None
        if lines:
            result = []
            for number, line in enumerate(raw.splitlines(), 1):
                if not line.strip():
                    continue
                try:
                    result.append((f"{path}:{number}", json.loads(line, parse_float=Decimal)))
                except (ValueError, UnicodeError):
                    self.warn(f"{path}:{number}", "malformed_json_line")
            return result
        try:
            return json.loads(raw, parse_float=Decimal)
        except (ValueError, UnicodeError):
            self.warn(path, "malformed_json")
            return None

    def add(self, a, b, phase, source, priority, member=None, activity=None):
        try:
            span = Interval(a, b, phase, source, priority, member, activity)
        except (ValueError, TypeError) as error:
            self.warn(source, str(error))
            return
        self.intervals.append(span)

    def timed(self, row, source):
        if not isinstance(row, dict):
            self.warn(source, "expected_object")
            return None
        try:
            if "started_epoch_s" in row and "ended_epoch_s" in row:
                a, b = ns(row["started_epoch_s"]), ns(row["ended_epoch_s"])
            elif "started_ns" in row and "ended_ns" in row:
                # R1 DRIVER fields are time.time_ns(), unlike episode fields.
                a, b = integer(row["started_ns"]), integer(row["ended_ns"])
            else:
                self.warn(source, "timing_boundaries_unavailable")
                return None
            if b < a:
                raise ValueError("reversed_epoch_interval")
            if "started_monotonic_ns" in row and "ended_monotonic_ns" in row:
                elapsed = integer(row["ended_monotonic_ns"]) - integer(row["started_monotonic_ns"])
                # Diagnostic only; no clock correction or measurement tolerance changes.
                if elapsed < 0 or abs((b-a)-elapsed) > drift_allowance(elapsed):
                    self.warn(source, "clock_elapsed_disagreement "+drift_detail(b-a-elapsed, elapsed))
            return a, b
        except (ValueError, TypeError) as error:
            self.warn(source, str(error))
            return None

    def journal(self, path, stage_phases):
        known = {"bracket_reservation": "scaffold", "calibration_capture": "scaffold",
                 "bound_derivation": "scaffold", "pre_calibration_screen": "scaffold",
                 "window_calibration_verdict": "scaffold", "whole_window_verdict": "finalize",
                 "backup": "offload", "session_status_record": "finalize"}
        seen = set()
        for source, row in self.load(path, lines=True):
            times = self.timed(row, source)
            if not times:
                continue
            stage = row.get("stage_id")
            if not isinstance(stage, str) or not isinstance(row.get("kind"), str):
                self.warn(source, "stage_identity_unavailable")
                continue
            if stage in seen:
                self.warn(source, "duplicate_stage_id")
            seen.add(stage)
            phase = stage_phases.get(stage, known.get(row.get("kind"), "unattributed"))
            self.add(*times, phase, source, 5, activity=str(stage))
            self.stages.append(dict(stage_id=stage, kind=row.get("kind"), rc=row.get("rc"),
                                    start_ns=times[0], end_ns=times[1], phase=phase, source=source))
            self.bounds.append(times)
        for stage in set(stage_phases)-seen:
            self.warn(path, "stage_phase_override_not_found="+stage)

    def r1(self, path):
        doc = self.load(path)
        if not isinstance(doc, dict):
            return

        def duration(value, source):
            if value is None:
                return None
            try:
                result = ns(value)
                if result < 0:
                    raise ValueError("negative_wait_duration")
                return result
            except ValueError as error:
                self.warn(source, str(error))
                return None

        def boundaries(row, source):
            if not isinstance(row, dict):
                return None
            if "entry_epoch_s" in row and "exit_epoch_s" in row:
                return self.timed(dict(started_epoch_s=row["entry_epoch_s"],
                                       ended_epoch_s=row["exit_epoch_s"]), source)
            if any(k in row for k in ("started_ns", "started_epoch_s", "ended_ns", "ended_epoch_s")):
                return self.timed(row, source)
            # In particular, bare g0.start_ns/end_ns are episode monotonic,
            # NOT epoch. Do not place them without a clock bridge.
            return None

        def attempt(row, source):
            if not isinstance(row, dict):
                self.warn(source, "expected_attempt_object")
                return
            for i, prior in enumerate(row.get("superseded_attempts", [])):
                attempt(prior, f"{source}.superseded_attempts[{i}]")
            times = self.timed(row, source)
            name = row.get("name", "unknown")
            if times:
                # Only whole non-model R1 segments have a known phase here.
                phase = ("dwell" if name == "idle_soak" else "scaffold"
                         if name in ("pre_calibration_bracket", "post_calibration_bracket") else "unattributed")
                self.add(*times, phase, source, 3, activity=name)
                self.bounds.append(times)
            wait_ns = duration(row.get("os_batch_wait_s"), source+".os_batch_wait_s")
            wait_times = boundaries(row.get("os_batch_wait"), source+".os_batch_wait")
            release = row.get("g0_release")
            if release is not None and not isinstance(release, dict):
                self.warn(source, "expected_g0_release_object")
            gate = release.get("g0") if isinstance(release, dict) else None
            if gate is not None and not isinstance(gate, dict):
                self.warn(source, "expected_g0_object")
                gate = None
            release_times = boundaries(release, source+".g0_release")
            gate_times = boundaries(gate, source+".g0_release.g0")
            gate_wait = duration(release.get("g0_wait_s", (gate or {}).get("duration_s")),
                                 source+".g0_release.g0_wait_s") if isinstance(release, dict) else None
            self.attempts.append(dict(name=name, attempt=row.get("attempt"), source=source,
                                     start_ns=times[0] if times else None, end_ns=times[1] if times else None,
                                     os_batch_wait_ns=wait_ns, wait_placement="unplaced",
                                     os_batch_wait_basis="requested, unmeasured",
                                     os_batch_wait_interval=None, gap_before_ns=None,
                                     g0_release=dict(interval=None, gate_interval=None, wait_ns=gate_wait,
                                                     placement="unplaced") if release is not None else None,
                                     _wait_times=wait_times, _release_times=release_times, _gate_times=gate_times,
                                     aggregate_phases_s=_plain((row.get("result") or {}).get("phases_s"))))
        for i, row in enumerate(doc.get("phases", [])):
            attempt(row, f"{path}#phases[{i}]")
        # Chronology includes superseded attempts; JSON nesting is not order.
        previous_end = None
        self.attempts.sort(key=lambda r: (r["start_ns"] is None, r["start_ns"] or 0))
        for row in self.attempts:
            start, end, source = row["start_ns"], row["end_ns"], row["source"]
            if start is not None and previous_end is not None:
                row["gap_before_ns"] = start-previous_end

            def place(times, activity, priority, upper):
                if times is None or start is None:
                    return None
                a, b = times
                if b > upper or (previous_end is not None and a < previous_end):
                    self.warn(source, activity+"_outside_pre_attempt_gap")
                    return None
                self.add(a, b, "gates", source+"."+activity, priority, activity=activity)
                self.bounds.append(times)
                return dict(start_ns=a, end_ns=b, duration_ns=b-a, basis="measured boundaries")

            release_times, gate_times = row.pop("_release_times"), row.pop("_gate_times")
            release = row["g0_release"]
            if release is not None:
                release["interval"] = place(release_times, "g0_release", 6, start)
                if gate_times and release_times and not (release_times[0] <= gate_times[0] <= gate_times[1] <= release_times[1]):
                    self.warn(source, "g0_release_gate_outside_release")
                else:
                    release["gate_interval"] = place(gate_times, "g0_release_wait", 7, start)
                if release["interval"] or release["gate_interval"]:
                    release["placement"] = "measured boundaries"
                else:
                    self.warn(source, "g0_release_unplaced")
            release_start = min((i[0] for i in (release_times, gate_times) if i), default=start)
            wait_times = row.pop("_wait_times")
            row["os_batch_wait_interval"] = place(wait_times, "os_batch_wait", 6, release_start)
            if row["os_batch_wait_interval"] is not None:
                row["wait_placement"] = "measured boundaries"
                row["os_batch_wait_basis"] = "requested sleep total; interval separately measured"
            elif row["os_batch_wait_ns"]:
                # An optional requested position is a table annotation ONLY:
                # no measured ledger interval, and no observed bound extension.
                if release is None and start is not None:
                    row["os_batch_wait_interval"] = dict(start_ns=start-row["os_batch_wait_ns"],
                        end_ns=start, duration_ns=row["os_batch_wait_ns"], basis="requested, unmeasured")
                    row["wait_placement"] = "inferred before attempt; excluded from ledger"
                else:
                    self.warn(source, "os_batch_wait_unplaced; requested, unmeasured")
            if end is not None:
                previous_end = max(previous_end, end) if previous_end is not None else end

    def bundle(self, path):
        meta_path = path+"/metadata.json"
        meta = self.load(meta_path)
        member = meta.get("run_id", path) if isinstance(meta, dict) else path
        if not isinstance(member, str) or not member:
            raise ValueError("metadata run_id must be a nonempty string")
        if member in self.members:
            raise ValueError("duplicate member run_id: "+member)
        state = dict(unavailable=["eligibility"], gate_waits=[], decode_tokens=None,
                     turns=None, deadline_tail_ns=None, path=path, bounds=None)
        self.members[member] = state
        event_path = path+"/events.jsonl"
        events = self.load(event_path, lines=True)
        opened = {}
        run_start = run_end = None
        event_times = []
        stage_map = {"validate": "scaffold", "prepare": "scaffold", "warmup": "scaffold",
                     "idle_baseline": "idle", "idle_drift_sentinel": "idle",
                     "measured_run": "unattributed", "cleanup": "scaffold", "reduce": "scaffold"}
        for source, row in events:
            if not isinstance(row, dict):
                self.warn(source, "expected_event_object")
                continue
            try:
                at = ns(row["timestamp_s"])
            except (KeyError, ValueError, TypeError) as error:
                self.warn(source, "invalid_event_timestamp "+str(error))
                continue
            event_times.append(at)
            kind, phase = row.get("event_type"), row.get("phase")
            if kind == "run_started":
                if run_start is not None:
                    self.warn(source, "duplicate_run_start")
                run_start = at
            if kind == "run_finalized":
                if run_end is not None:
                    self.warn(source, "duplicate_run_end")
                run_end = at
            if kind == "stage_started":
                if phase in opened:
                    self.warn(source, "duplicate_event_start="+str(phase))
                opened[phase] = (at, source)
            if kind == "stage_completed":
                if phase not in opened:
                    self.warn(source, "unmatched_event_end="+str(phase))
                    continue
                a, origin = opened.pop(phase)
                self.add(a, at, stage_map.get(phase, "unattributed"), origin+".."+source, 20,
                         member, activity=str(phase))
        for phase, (_, source) in opened.items():
            self.warn(source, "unclosed_event="+str(phase))
        if run_start is not None and run_end is not None and run_end >= run_start:
            state["bounds"] = (run_start, run_end)
            state["bounds_basis"] = "run_started_to_run_finalized"
        else:
            state["unavailable"].append("member_wall")
            self.warn(event_path, "member_boundaries_unavailable")
            state["bounds_basis"] = "event_envelope_incomplete_run" if event_times else "unavailable"
            if event_times:
                state["bounds"] = (min(event_times), max(event_times))
                self.warn(event_path, "incomplete_run_bounded_by_event_envelope")
        if state["bounds"] is not None:
            self.add(*state["bounds"], "unattributed", event_path+"#run", 10, member)
            self.bounds.append(state["bounds"])
        self.episode(path+"/outputs/align_episode.json", member, state)

    def episode(self, path, member, state):
        ep = self.load(path)
        if not isinstance(ep, dict):
            state["unavailable"].append("episode")
            return
        hardware = ep.get("hardware") or {}
        mappings = [m for m in ep.get("clock_mappings", [])
                    if m.get("trace_domain") == "joulewise.controller.epoch_ns"
                    and m.get("episode_domain") == ep.get("clock_domain")]
        try:
            pairs = hardware.get("paired_clock_stamps_ns") or []
            drift = 0
            mono_elapsed = integer(ep["end_ns"])-integer(ep["start_ns"])
            if len(pairs) >= 2:
                epoch_elapsed = integer(pairs[-1]["epoch_ns"])-integer(pairs[0]["epoch_ns"])
                mono_elapsed = ((integer(pairs[-1]["monotonic_before_ns"])+integer(pairs[-1]["monotonic_after_ns"]))//2
                                - (integer(pairs[0]["monotonic_before_ns"])+integer(pairs[0]["monotonic_after_ns"]))//2)
                if epoch_elapsed < 0 or mono_elapsed < 0:
                    raise ValueError("reversed_paired_clock_interval")
                drift = epoch_elapsed-mono_elapsed
                state["clock_elapsed_drift_ns"] = drift
                state["clock_elapsed_drift_ppm"] = drift*1_000_000/mono_elapsed if mono_elapsed else None
            if len(mappings) > 1:
                raise ValueError("conflicting_clock_mappings")
            if len(mappings) == 1:
                offset = -integer(mappings[0]["offset_ns"])
                uncertainty = integer(mappings[0]["uncertainty_ns"])
                if uncertainty < 0:
                    raise ValueError("negative_clock_uncertainty")
                # The native mapping already includes its anchor span. Keep it
                # usable; conservatively expose an additional observed-drift
                # allowance, rather than treating 1 ms as a placement veto.
                state["recorded_clock_mapping_uncertainty_ns"] = uncertainty
                uncertainty += abs(drift)
            else:
                # Early episodes can carry paired stamps but no trace mapping.
                if not pairs:
                    raise ValueError("clock_mapping_unavailable")
                lower = min(integer(p["epoch_ns"])-integer(p["monotonic_after_ns"]) for p in pairs)
                upper = max(integer(p["epoch_ns"])-integer(p["monotonic_before_ns"]) for p in pairs)
                resolution = max(integer(p.get("wall_resolution_ns", 0)) +
                                 integer(p.get("monotonic_resolution_ns", 0)) for p in pairs)
                if resolution < 0 or any(integer(p["monotonic_after_ns"]) < integer(p["monotonic_before_ns"])
                                         for p in pairs):
                    raise ValueError("invalid_paired_clock_bracket")
                offset, uncertainty = (lower+upper)//2, (upper-lower+1)//2+resolution
                if abs(drift) > uncertainty+drift_allowance(mono_elapsed):
                    raise ValueError("episode_clock_elapsed_disagreement; placement_unavailable; "+
                                     drift_detail(drift, mono_elapsed))
                self.warn(path, "paired_clock_bracket_only")
            if abs(drift) > drift_allowance(mono_elapsed):
                self.warn(path, "episode_clock_elapsed_disagreement; mapping_retained; "+
                          drift_detail(drift, mono_elapsed))
            state["clock_mapping_uncertainty_ns"] = uncertainty
            a, b = integer(ep["start_ns"])+offset, integer(ep["end_ns"])+offset
            if b < a:
                raise ValueError("reversed_episode_interval")
        except (KeyError, ValueError, TypeError) as error:
            self.warn(path, str(error))
            state["unavailable"].append("episode_clock")
            return
        if state["bounds"] is not None:
            lo, hi = state["bounds"]
            if a < lo or b > hi:
                self.warn(path, "episode_outside_member_bounds")
                state["unavailable"].append("episode_placement")
                return
        else:
            self.warn(path, "episode_member_bounds_unavailable")
            state["unavailable"].append("episode_placement")
            return
        self.add(a, b, "unattributed", path, 25, member)
        self.bounds.append((a, b))
        state["turns"] = len(ep.get("turns", []))
        counts = [t.get("decode_tokens") for t in ep.get("turns", [])]
        if all(type(n) is int and n >= 0 for n in counts):
            state["decode_tokens"] = sum(counts)
        deadline = hardware.get("token_budget", {}).get("deadline_ns")
        if type(deadline) is int:
            state["deadline_tail_ns"] = max(0, ep["end_ns"]-max(ep["start_ns"], deadline))
        def inner(row, source, phase, priority, activity=None):
            try:
                start, end = integer(row["start_ns"])+offset, integer(row["end_ns"])+offset
                if start < a or end > b or end < start:
                    raise ValueError("interval_outside_episode")
                self.add(start, end, phase, source, priority, member, activity)
                return end-start
            except (KeyError, ValueError, TypeError) as error:
                self.warn(source, str(error))
                return None
        for i, turn in enumerate(ep.get("turns", [])):
            source = f"{path}#turns[{i}]"
            first = turn.get("first_token_ns")
            if type(first) is int and type(turn.get("start_ns")) is int and type(turn.get("end_ns")) is int and turn["start_ns"] <= first <= turn["end_ns"]:
                inner(dict(start_ns=turn["start_ns"], end_ns=first), source+".prefill", "scaffold", 30, "prefill")
                inner(dict(start_ns=first, end_ns=turn["end_ns"]), source+".decode", "decode", 30, "decode")
            else:
                self.warn(source, "first_token_unavailable_or_invalid")
                if "prefill_decode_split" not in state["unavailable"]:
                    state["unavailable"].append("prefill_decode_split")
            for j, call in enumerate(turn.get("tool_calls", [])):
                inner(call, f"{source}.tool_calls[{j}]", "scaffold", 40, "tool")
        thermal = hardware.get("thermal") or {}
        if "intervals" not in thermal:
            state["unavailable"].append("gate_intervals")
        for i, gate in enumerate(thermal.get("intervals", [])):
            kind = gate.get("kind")
            if kind not in ("G0", "G1", "H"):
                self.warn(path, "unknown_gate_kind="+str(kind))
                continue
            duration = inner(gate, f"{path}#thermal.intervals[{i}]", "holds" if kind == "H" else "gates", 50, kind)
            state["gate_waits"].append(dict(kind=kind, duration_ns=duration, outcome=gate.get("outcome")))


def _plain(value):
    """JSON-compatible informational aggregates; never used for wall sums."""
    if isinstance(value, Decimal):
        return str(value)
    if isinstance(value, dict):
        return {k: _plain(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_plain(v) for v in value]
    return value


def read_window(read_blob, *, night_result=None, chain_journal=None, chain_started=None,
                chain_exited=None, night_log=None, r1_result=None, plan=None, bundles=(),
                spans=(), stage_phases=None, r0_result=None, r0_note=None):
    """Build an observed-envelope ledger. read_blob reads only named sources.

    Spans are (phase, path) pairs pointing at EXISTING timed JSON documents;
    the phase assignment is an explicit operator annotation in the output.
    Plan t0/window_max_s define a reservation only, never observed time.
    """
    reader = _Reader(read_blob)
    if r0_result and r0_note:
        raise ValueError("supply only one R0 source: --r0-result or --r0-note")
    r0 = None
    if r0_result or r0_note:
        from joulewise.align.window_timing_r0 import R0Timing
        path = r0_result or r0_note
        parser = R0Timing(path, ns, reader.warn)
        raw = reader.blob(path)
        if raw is not None:
            r0 = parser.native(reader.load(path)) if r0_result else parser.note(raw.decode())
            if r0["start_ns"] is not None and r0["end_ns"] is not None:
                reader.bounds.append((r0["start_ns"], r0["end_ns"]))
            if r0["dwell"]:
                dwell = r0["dwell"]
                reader.add(dwell["start_ns"], dwell["end_ns"], "dwell", path+"#observed_dwell", 15)
                reader.bounds.append((dwell["start_ns"], dwell["end_ns"]))
    stage_phases = stage_phases or {}
    if any(p not in PHASES for p in stage_phases.values()):
        raise ValueError("unknown stage phase")
    driver = reader.load(night_result) if night_result else None
    driver_times = reader.timed(driver, night_result) if driver is not None else None
    if driver_times:
        reader.bounds.append(driver_times)
    start_doc = reader.load(chain_started) if chain_started else None
    end_doc = reader.load(chain_exited) if chain_exited else None
    start = ns(start_doc["epoch_s"]) if isinstance(start_doc, dict) and "epoch_s" in start_doc else None
    end = ns(end_doc["epoch_s"]) if isinstance(end_doc, dict) and "epoch_s" in end_doc else None
    if start is not None and end is not None:
        if end < start:
            raise ValueError("chain exit precedes start")
        if "monotonic_ns" in start_doc and "monotonic_ns" in end_doc:
            elapsed = integer(end_doc["monotonic_ns"])-integer(start_doc["monotonic_ns"])
            delta = (end-start)-elapsed
            if elapsed < 0 or abs(delta) > drift_allowance(elapsed):
                reader.warn(chain_exited, "clock_elapsed_disagreement "+drift_detail(delta, elapsed))
    # A lone terminal is still observed evidence, including the unknown tail.
    for boundary in (start, end):
        if boundary is not None:
            reader.bounds.append((boundary, boundary))
    if chain_journal:
        reader.journal(chain_journal, stage_phases)
    if r1_result:
        reader.r1(r1_result)
    annotations = []
    for phase, path in spans:
        if phase not in PHASES:
            raise ValueError("unknown span phase: "+phase)
        row = reader.load(path)
        times = reader.timed(row, path) if row is not None else None
        annotations.append(dict(path=path, phase=phase))
        if times:
            reader.add(*times, phase, path, 15)
            reader.bounds.append(times)
    if night_log:
        # run_night's native ISO-stamped night.log. Only the bounded admission
        # aggregate is known; no arbitrary text line is interpreted as a phase.
        safe_path(night_log)
        try:
            raw = read_blob(night_log)
            reader.sources[night_log] = {"sha256": hashlib.sha256(raw).hexdigest(), "bytes": len(raw)}
            launched = None
            for i, line in enumerate(raw.decode().splitlines(), 1):
                stamp, _, message = line.partition(" ")
                if message == "night driver started" or message.startswith("night gate verdict="):
                    moment = datetime.fromisoformat(stamp.replace("Z", "+00:00"))
                    if moment.tzinfo is None:
                        raise ValueError("night_log_timezone_unavailable")
                    at = ns(moment.timestamp())
                    if driver_times and not driver_times[0] <= at <= driver_times[1]:
                        reader.warn(f"{night_log}:{i}", "log_event_outside_driver_bounds")
                        continue
                    if message == "night driver started":
                        if launched is not None:
                            reader.warn(night_log, "multiple_driver_starts")
                        launched = at
                    elif launched is not None:
                        reader.add(launched, at, "gates", f"{night_log}:{i}#admission", 2,
                                   activity="admission_aggregate")
                        reader.bounds.append((launched, at))
                        launched = None
        except (KeyError, FileNotFoundError, ValueError, UnicodeError) as error:
            reader.warn(night_log, "log_unavailable_or_invalid "+str(error))
    for bundle in bundles:
        reader.bundle(safe_path(bundle))
    if not reader.bounds:
        raise ValueError("no observed timing boundaries in named records")
    a, b = min(t[0] for t in reader.bounds), max(t[1] for t in reader.bounds)
    window_intervals = list(reader.intervals)
    member_bounds = [(name, state["bounds"]) for name, state in reader.members.items() if state["bounds"]]
    for i, (name, bounds) in enumerate(member_bounds):
        for other, other_bounds in member_bounds[i+1:]:
            lo, hi = max(bounds[0], other_bounds[0]), min(bounds[1], other_bounds[1])
            if lo < hi:
                reader.warn("ledger", "overlapping_member_envelopes="+name+","+other)
                # A more detailed activity from one member cannot win ownership
                # over another member's overlapping lifecycle. Keep each member
                # ledger intact, but leave the shared wall ambiguous.
                for owner in (name, other):
                    window_intervals.append(Interval(lo, hi, "unattributed",
                        reader.members[owner]["path"]+"/events.jsonl#overlap", 100, owner))
    rows = partition(a, b, window_intervals)
    if any(r["ambiguous"] for r in rows):
        reader.warn("ledger", "conflicting_overlapping_intervals")
    unknown = totals(rows, "phase")["unattributed"]
    if unknown:
        reader.warn("ledger", "unattributed_wall_ns="+str(unknown))
    for member, state in reader.members.items():
        bounds = state.pop("bounds")
        state["wall_ns"] = bounds[1]-bounds[0] if bounds else None
        # Each member has an independently reconciled envelope. Other members
        # are excluded here; the window ledger still exposes ownership conflicts.
        own = [i for i in reader.intervals if i.member in (member, None)]
        member_rows = partition(*bounds, own) if bounds else []
        state["ledger"] = member_rows
        state["phase_ns"] = totals(member_rows, "phase") if bounds else None
        state["activity_ns"] = totals(member_rows, "activity") if bounds else None
    plan_doc = reader.load(plan) if plan else None
    origin = ns(plan_doc["t0_epoch_s"]) if isinstance(plan_doc, dict) and "t0_epoch_s" in plan_doc else None
    cap = ns(plan_doc["window_max_s"]) if isinstance(plan_doc, dict) and "window_max_s" in plan_doc else None
    last_stage = max((s["end_ns"] for s in reader.stages), default=None)
    ceiling = dict(origin_ns=origin, cap_ns=cap, terminal_ns=end,
                   terminal_minus_origin_ns=end-origin if end is not None and origin is not None else None,
                   headroom_ns=origin+cap-end if None not in (origin, cap, end) else None,
                   post_last_stage_ns=end-last_stage if end is not None and last_stage is not None else None,
                   status="unavailable", idle_to_ceiling="unproven")
    if None not in (origin, cap, end):
        if cap <= 0:
            raise ValueError("window_max_s must be positive")
        ceiling["status"] = "closed_before_ceiling" if end < origin+cap else "at_or_after_ceiling_cause_unproven"
        if ceiling["status"] == "closed_before_ceiling":
            ceiling["idle_to_ceiling"] = "not_in_this_record"
    missing = [phase for phase in PHASES[:-1] if not any(i.phase == phase for i in reader.intervals)]
    report = dict(schema="joulewise.align.window_timing.v1", start_ns=a, end_ns=b, wall_ns=b-a,
                bounds_basis="observed_envelope_of_named_sources", ledger=rows,
                phase_ns=totals(rows, "phase"), activity_ns=totals(rows, "activity"),
                members=reader.members, stages=reader.stages, attempts=reader.attempts,
                ceiling=ceiling, unavailable_phases=missing, warnings=sorted(set(reader.warnings)),
                sources=reader.sources, phase_annotations=annotations, stage_phase_annotations=stage_phases)
    if r0 is not None:
        report["r0"] = r0
    return report


def worksheet(report):
    wall = report["wall_ns"]
    lines = ["TIMING ONLY — observed records; unavailable fields are not zero",
             "Zero phase totals mean no interval attributed, not proof of absent work.", "",
             f"Observed envelope: {wall/NS:.6f} s ({report['bounds_basis']})",
             "phase             seconds      fraction"]
    for phase, duration in report["phase_ns"].items():
        lines.append(f"{phase:15} {duration/NS:12.6f} {duration/wall if wall else 0:12.6%}")
    if "r0" in report:
        from joulewise.align.window_timing_r0 import worksheet_r0
        lines += worksheet_r0(report["r0"])
    lines += ["", "MEMBERS (seconds; phase shares use the member's observed wall)",
              "decode excludes tool-call time and gates/holds; tool is a separate disjoint activity.",
              "Native R1 phases_s.decode includes tool-call time (subtracts holds only); its totals may overlap tool.",
              "member\twall\tidle\tscaffold\tprefill\tdecode_excluding_tools\ttool\tG0\tG1\tH\tunknown\ttail\tturns\ttokens\tunavailable"]
    def seconds(value):
        return "unavailable" if value is None else f"{value/NS:.6f}"
    for member, state in report["members"].items():
        activities, phases = state["activity_ns"] or {}, state["phase_ns"] or {}
        gates = {k: (None if "gate_intervals" in state["unavailable"] else activities.get(k, 0))
                 for k in ("G0", "G1", "H")}
        values = [state["wall_ns"], phases.get("idle"), phases.get("scaffold"), activities.get("prefill"),
                  activities.get("decode"), activities.get("tool"), *gates.values(),
                  phases.get("unattributed"), state["deadline_tail_ns"]]
        lines.append("\t".join([member, *map(seconds, values), str(state["turns"]),
                                str(state["decode_tokens"]), ",".join(state["unavailable"])]))
        if state["wall_ns"]:
            lines.append("  phase fractions: "+", ".join(f"{p}={v/state['wall_ns']:.6%}" for p, v in phases.items() if v))
        lines.append("  activities (disjoint seconds): "+", ".join(f"{p}={v/NS:.6f}" for p, v in activities.items()))
        lines.append("  member bounds: "+state["bounds_basis"])
        for gate in state["gate_waits"]:
            lines.append(f"  {gate['kind']} {gate['outcome']}: {seconds(gate['duration_ns'])} s")
    lines += ["", "STAGES (inclusive envelopes; do not add these to the disjoint ledger)"]
    for stage in report["stages"]:
        lines.append(f"{stage['stage_id']} {stage['kind']} rc={stage['rc']}: "+seconds(stage["end_ns"]-stage["start_ns"])+" s")
    lines += ["", "R1 ATTEMPTS (inclusive; only measured boundaries enter the disjoint ledger)",
              "Requested sleep totals are requested, unmeasured; inferred positions never extend observed wall."]
    for attempt in report["attempts"]:
        duration = attempt["end_ns"]-attempt["start_ns"] if attempt["start_ns"] is not None else None
        lines.append(f"{attempt['name']} attempt={attempt['attempt']} wall="+seconds(duration)+" s; os_batch_wait="+
                     seconds(attempt["os_batch_wait_ns"])+" s ("+attempt["os_batch_wait_basis"]+"); "+
                     attempt["wait_placement"]+"; gap_before="+seconds(attempt["gap_before_ns"])+" s")
        def show_interval(label, interval):
            if interval is not None:
                lines.append(f"  {label}: [{interval['start_ns']}, {interval['end_ns']}) epoch ns; "+
                             seconds(interval["duration_ns"])+" s ("+interval["basis"]+")")
        show_interval("os_batch_wait", attempt["os_batch_wait_interval"])
        if attempt["g0_release"] is not None:
            release = attempt["g0_release"]
            lines.append("  g0_release: "+release["placement"]+"; recorded G0 wait="+seconds(release["wait_ns"])+" s")
            show_interval("g0_release envelope", release["interval"])
            show_interval("g0_release gate", release["gate_interval"])
        if attempt["aggregate_phases_s"] is not None:
            lines.append("  recorded phase totals (unplaced, may overlap; decode includes tools): "+json.dumps(attempt["aggregate_phases_s"], sort_keys=True))
    ceiling = report["ceiling"]
    lines += ["", "CEILING: "+ceiling["status"],
              "  origin-to-terminal="+seconds(ceiling["terminal_minus_origin_ns"])+" s; cap="+seconds(ceiling["cap_ns"])+" s",
              "  unused headroom="+seconds(ceiling["headroom_ns"])+" s; after last stage="+seconds(ceiling["post_last_stage_ns"])+" s",
              "  idle-to-ceiling cause: "+ceiling["idle_to_ceiling"],
              "Unavailable phase boundaries: "+", ".join(report["unavailable_phases"]), "", "WARNINGS"]
    lines += report["warnings"] or ["none"]
    lines += ["", "SOURCES (committed bytes; SHA-256)", "commit: "+report.get("source_commit", "provided by caller")]
    lines += [path+" "+source["sha256"] for path, source in sorted(report["sources"].items())]
    lines += ["phase annotations: "+json.dumps(report["phase_annotations"], sort_keys=True),
              "stage annotations: "+json.dumps(report["stage_phase_annotations"], sort_keys=True)]
    return "\n".join(lines)+"\n"


def _assignment(value):
    key, sep, path = value.partition("=")
    if not sep or not key or not path:
        raise argparse.ArgumentTypeError("expected NAME=VALUE")
    return key, path


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", default=".")
    parser.add_argument("--ref", required=True, help="local committed export ref; never fetched")
    for option in ("night-result", "chain-journal", "chain-started", "chain-exited", "night-log", "r1-result", "plan"):
        parser.add_argument("--"+option)
    r0_options = parser.add_mutually_exclusive_group()
    r0_options.add_argument("--r0-result", help="native R0 report.json; timing/identity fields only")
    r0_options.add_argument("--r0-note", help="committed R0 summary NOTE when report is not committed")
    parser.add_argument("--bundle", action="append", default=[], help="committed bundle directory; repeat for each member")
    parser.add_argument("--span", action="append", default=[], type=_assignment,
                        help="PHASE=PATH to an existing timed JSON document (operator phase annotation)")
    parser.add_argument("--stage-phase", action="append", default=[], type=_assignment,
                        help="STAGE_ID=PHASE (e.g. references); no stage-name guessing")
    parser.add_argument("--format", choices=("worksheet", "json"), default="worksheet")
    args = parser.parse_args(argv)
    try:
        source = GitRecords(args.repo, args.ref)
        report = read_window(source.read, **{name: getattr(args, name) for name in
                             ("night_result", "chain_journal", "chain_started", "chain_exited", "night_log", "r1_result", "plan", "r0_result", "r0_note")},
                             bundles=args.bundle, spans=args.span, stage_phases=dict(args.stage_phase))
        report["source_commit"] = source.commit
    except (ValueError, OSError, InvalidOperation) as error:
        parser.error(str(error))
    print(json.dumps(report, sort_keys=True, indent=2, allow_nan=False) if args.format == "json" else worksheet(report), end="\n" if args.format == "json" else "")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
