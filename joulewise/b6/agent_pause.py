"""Agent episodes pause future members and exclude overlapping whole units."""
from __future__ import annotations

from collections import defaultdict, deque
import json
import os
from pathlib import Path
import tempfile
import time

# Collection design 6.2: ten clean minutes to resume, two paused hours total.
PAUSE_RESUME_S = 600
PAUSE_LIMIT_S = 7200


def clock_stamp():
    return {"monotonic_ns": time.monotonic_ns(), "wall_s": time.time()}


def write_marker(path: Path, value: dict | None) -> None:
    if value is None:
        path.unlink(missing_ok=True)
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, name = tempfile.mkstemp(dir=path.parent, prefix=".pause-")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(value, handle, sort_keys=True)
        os.replace(name, path)
    finally:
        Path(name).unlink(missing_ok=True)


def _instant(row):
    return row.get("at", row.get("stamp", row))


class AgentPause:
    def __init__(self, *, clock=clock_stamp, marker_writer=lambda row: None,
                 journal_appender=lambda row: None, flag=lambda code, observed: None,
                 driver_pid=None):
        self.clock, self.marker_writer, self.journal_appender, self.flag = clock, marker_writer, journal_appender, flag
        self.driver_pid = os.getpid() if driver_pid is None else driver_pid
        self.since = self.last_sighting = None
        self.completed_pause_s = 0.0
        self.stopped_by_limit = False
        self.rows = []

    def _write(self, writer, value):
        try:
            writer(value)
        except Exception as error:
            self.flag("census.journal_write_failed", {"record": "agent_pause", "error": f"{type(error).__name__}: {error}"})

    def total_pause_s(self, at=None):
        at = self.clock() if at is None else at
        return self.completed_pause_s + (0 if self.since is None else
            (at["monotonic_ns"] - self.since["monotonic_ns"]) / 1e9)

    def observe(self, kind, stdout="") -> bool:
        at = self.clock()
        if kind == "positive":
            if self.since is None:
                self.since = at
            self.last_sighting = at
            names = []
            for line in stdout.splitlines():
                bits = line.split()
                if len(bits) >= 2 and bits[0].isdigit():
                    names.append([int(bits[0]), Path(bits[1]).name])
            row = {"event": "sighting", "at": at, "pids_names": names}
            self.rows.append(row)
            self._write(self.journal_appender, row)
            self._write(self.marker_writer, {"driver_pid": self.driver_pid,
                                             "since": self.since, "last_sighting": at})
        # Even an unmeasured pass can reach the cumulative physical pause limit.
        if self.total_pause_s(at) >= PAUSE_LIMIT_S:
            self.stopped_by_limit = True
            return True
        if (kind == "clean" and self.since is not None
                and at["monotonic_ns"] - self.last_sighting["monotonic_ns"] >= PAUSE_RESUME_S * 1e9):
            self.completed_pause_s = self.total_pause_s(at)
            row = {"event": "resume", "at": at}
            self.rows.append(row)
            self._write(self.journal_appender, row)
            self._write(self.marker_writer, None)
            self.since = self.last_sighting = None
        return False


class PausingCensus:
    def __init__(self, inner, pause):
        self.inner, self.pause = inner, pause
        self.last_positive = None
        self.rows = []

    def __call__(self):
        probe, refusal = self.inner()
        kind = self.inner.classify(probe)
        self.rows.append({"exit_code": probe.exit_code, "stdout": probe.stdout,
                          "monotonic_ns": probe.monotonic_ns})
        if kind == "positive":
            self.last_positive = (probe, refusal)
        if self.pause.observe(kind, probe.stdout):
            return probe, self.last_positive[1] if self.last_positive is not None else refusal
        return probe, None

    def append(self, *args):
        return self.inner.append(*args)

    def __getattr__(self, name):
        return getattr(self.inner, name)


def presence_intervals(journal_rows, census_rows, chain_start, chain_end):
    episodes = []
    active = None
    for row in journal_rows:
        at = _instant(row)
        if row.get("event") == "sighting":
            if active is None:
                before = [r for r in census_rows if r.get("exit_code") == 1 and not r.get("stdout", "").strip()
                          and chain_start["monotonic_ns"] <= _instant(r)["monotonic_ns"] < at["monotonic_ns"]]
                start = max((_instant(r) for r in before), key=lambda r: r["monotonic_ns"], default=chain_start)
                # Census journal has no wall stamp: project from this episode's clock pair.
                start = {**start, "wall_s": start.get("wall_s", at["wall_s"] - (at["monotonic_ns"] - start["monotonic_ns"]) / 1e9)}
                active = {"start": start, "last_sighting": at, "since": at, "basenames": []}
            active["last_sighting"] = at
            active["basenames"] = sorted(set(active["basenames"]) | {name for _, name in row.get("pids_names", [])})
        elif row.get("event") == "resume" and active is not None:
            active["pause_end"] = at
            episodes.append(active)
            active = None
    if active is not None:
        active["pause_end"] = chain_end
        episodes.append(active)
    for episode in episodes:
        last = episode["last_sighting"]
        clean = [r for r in census_rows if r.get("exit_code") == 1 and not r.get("stdout", "").strip()
                 and last["monotonic_ns"] < _instant(r)["monotonic_ns"] <= episode["pause_end"]["monotonic_ns"]]
        end = min((_instant(r) for r in clean), key=lambda r: r["monotonic_ns"], default=chain_end)
        end = {**end, "wall_s": end.get("wall_s", last["wall_s"] + (end["monotonic_ns"] - last["monotonic_ns"]) / 1e9)}
        episode.update(end=end, pause_s=(episode["pause_end"]["monotonic_ns"] - episode["since"]["monotonic_ns"]) / 1e9)
    return episodes


def paired_run_clocks(run_clock_rows):
    """Pair each start with the next unused end for that run id in file order."""
    pending = defaultdict(deque)
    pairs = []
    for row in run_clock_rows:
        if row.get("event") == "start":
            pending[row["run_id"]].append(len(pairs))
            pairs.append((row, None))
        elif row.get("event") == "end" and pending[row["run_id"]]:
            index = pending[row["run_id"]].popleft()
            pairs[index] = (pairs[index][0], row)
    return pairs


def overlap_flags(intervals, run_clock_rows):
    pairs = paired_run_clocks(run_clock_rows)
    flags = []
    for number, episode in enumerate(intervals, 1):
        units = {}
        for row, end in pairs:
            end_ns = end["clock"]["monotonic_ns"] if end is not None else float("inf")
            if row["clock"]["monotonic_ns"] <= episode["end"]["monotonic_ns"] and end_ns >= episode["start"]["monotonic_ns"]:
                unit = units.setdefault(row.get("unit_key", row["run_id"]), {"members": set(), "overlaps": set()})
                unit["members"].update(row.get("unit_run_ids") or [row["run_id"]])
                unit["overlaps"].add(row["run_id"])
        for key, unit in units.items():
            for run_id in sorted(unit["members"]):
                flags.append({"run_id": run_id, "observed": {"unit_key": key, "overlapping_run_ids": sorted(unit["overlaps"]), "episode": number}})
    return flags


def capture_overlaps(intervals, stage_rows):
    return [{"episode": i, "stage_id": row.get("stage_id")} for i, episode in enumerate(intervals, 1)
            for row in stage_rows if row.get("kind") == "calibration_capture"
            and isinstance(row.get("started_epoch_s"), (int, float))
            and isinstance(row.get("ended_epoch_s"), (int, float))
            and row["started_epoch_s"] <= episode["end"]["wall_s"]
            and row["ended_epoch_s"] >= episode["start"]["wall_s"]]


def _pid_alive(pid):
    try:
        os.kill(pid, 0)
        return True
    except ProcessLookupError:
        return False
    except PermissionError:
        return True


def wait_while_paused(custody_root, *, sleep=time.sleep, now=time.monotonic, pid_alive=_pid_alive):
    path = Path(custody_root) / "collection/pause.json"
    start = now()
    if not path.exists():
        return None
    stale = False
    while path.exists():
        try:
            marker = json.loads(path.read_text(encoding="utf-8"))
            stale = not pid_alive(int(marker["driver_pid"]))
        except FileNotFoundError:
            break
        except (OSError, ValueError, KeyError, TypeError):
            stale = True
        if stale or now() - start > PAUSE_LIMIT_S + PAUSE_RESUME_S:
            stale = True
            break
        sleep(5)
    end = now()
    return {"start": start, "end": end, "waited_s": end - start, "stale": stale}
