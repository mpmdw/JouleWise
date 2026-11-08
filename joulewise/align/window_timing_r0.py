"""Timing/identity projection of R0 receipts; no capture or backend imports.

R0 v1 records durations, not check boundary pairs. Keep its duration budget
separate from the epoch partition. Never backdate checks or CPU observations.
The archival NOTE reader accepts the specific committed summary grammar only.
"""
from datetime import datetime, timedelta, timezone
from decimal import Decimal, InvalidOperation
import re

NS = 1_000_000_000
EPOCH = datetime(1970, 1, 1, tzinfo=timezone.utc)


def epoch_ns(value):
    moment = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if moment.tzinfo is None:
        raise ValueError("timezone_unavailable")
    delta = moment - EPOCH
    return (delta.days * 86400 + delta.seconds) * NS + delta.microseconds * 1000


class R0Timing:
    def __init__(self, source, to_ns, warn):
        self.source, self.ns, self.warn = source, to_ns, warn
        self.data = dict(source=source, format=None, start_ns=None, end_ns=None,
                         wall_ns=None, wall_basis=None, epoch_wall_ns=None,
                         checks=[], checks_ns=0, unattributed_ns=None,
                         rounding_bound_ns=0, rungs=[], calls=[], cpu_observations=[],
                         cpu_observation_union_ns=0, milestones={}, dwell=None,
                         post_finish_to_agent_ns=None,
                         unavailable=["arm", "quiet_guard_wait", "finalize", "push",
                                      "check_placement", "rung_wall"])
        self.budget_valid = True

    def duration(self, value, source):
        if value is None:
            self.warn(source, "duration_unavailable")
            return None
        try:
            duration = self.ns(value)
            if duration < 0:
                raise ValueError("negative_duration")
            return duration
        except (ValueError, TypeError, InvalidOperation):
            self.warn(source, "invalid_duration")
            return None

    def bounds(self, a, b):
        if b < a:
            raise ValueError("reversed_R0_epoch_interval")
        self.data.update(start_ns=a, end_ns=b, epoch_wall_ns=b-a)

    def check(self, name, model, duration, source):
        if (not isinstance(name, str) or not re.fullmatch(r"[a-z][a-z-]*", name)
                or (model is not None and (not isinstance(model, str) or not re.fullmatch(r"[A-Z]", model)))):
            self.warn(source, "check_identity_unavailable")
            self.budget_valid = False
            return
        if any(r["check"] == name and r["model"] == model for r in self.data["checks"]):
            self.warn(source, "duplicate_R0_check")
            self.budget_valid = False
        self.data["checks"].append(dict(check=name, model=model, duration_ns=duration, source=source))

    def call(self, row, source, check):
        # Deliberate scalar allowlist. Never walk arbitrary nested payloads.
        duration = self.duration(row.get("seconds"), source)
        self.data["calls"].append(dict(check=check, source=source, duration_ns=duration))
        return duration

    def objects(self, parent, key, source):
        rows = parent.get(key, [])
        if not isinstance(rows, list):
            self.warn(source+"."+key, "expected_list")
            return
        for i, row in enumerate(rows):
            loc = f"{source}.{key}[{i}]"
            if not isinstance(row, dict):
                self.warn(loc, "expected_object")
                continue
            yield row, loc

    def native(self, doc):
        if not isinstance(doc, dict) or doc.get("schema") != "joulewise.align.r0.report.v1":
            raise ValueError("unsupported R0 report schema")
        self.data["format"] = "native_report"
        try:
            self.bounds(epoch_ns(doc["created_utc"]), epoch_ns(doc["finished_utc"]))
        except (KeyError, TypeError, AttributeError, ValueError):
            self.warn(self.source, "R0_epoch_boundaries_unavailable")
        self.data["wall_ns"] = self.duration(doc.get("total_seconds"), self.source+"#total_seconds")
        self.data["wall_basis"] = "recorded_monotonic_total_seconds"
        checks = doc.get("checks", [])
        if not isinstance(checks, list):
            self.warn(self.source+"#checks", "expected_list")
            self.budget_valid = False
            checks = []
        for i, row in enumerate(checks):
            source = f"{self.source}#checks[{i}]"
            if not isinstance(row, dict):
                self.warn(source, "expected_check_object")
                self.budget_valid = False
                continue
            name = row.get("check")
            self.check(name, row.get("model"), self.duration(row.get("check_seconds"), source), source)
            if name == "ladder":
                for rung, loc in self.objects(row, "rungs", source):
                    if not isinstance(rung.get("rung"), str):
                        self.warn(loc, "rung_identity_unavailable")
                        continue
                    count = missing = total = 0
                    for episode, ep_loc in self.objects(rung, "episodes", loc):
                        for turn, turn_loc in self.objects(episode, "turns", ep_loc):
                            duration = self.call(turn, turn_loc, name)
                            count += 1
                            missing += duration is None
                            total += duration or 0
                    self.data["rungs"].append(dict(rung=rung.get("rung"), source=loc,
                        wall_ns=None, call_ns=total if count else None,
                        recorded_calls=count, missing_call_times=missing,
                        not_run=rung.get("status") == "not_run"))
            elif name == "long-decode":
                for attempt, loc in self.objects(row, "attempts", source):
                    self.call(attempt, loc, name)
            elif name == "generated":
                for turn, loc in self.objects(row, "turns", source):
                    self.call(turn, loc, name)
        for row, loc in self.objects(doc, "census", self.source+"#"):
            source = loc+".cpu_interval"
            interval = row.get("cpu_interval", {})
            if not interval:
                continue
            if not isinstance(interval, dict):
                self.warn(source, "expected_object")
                continue
            try:
                a, b = self.ns(interval["start_monotonic_s"]), self.ns(interval["end_monotonic_s"])
                if b < a:
                    raise ValueError("reversed")
                self.data["cpu_observations"].append(dict(start_monotonic_ns=a, end_monotonic_ns=b, source=source))
            except (KeyError, TypeError, ValueError, InvalidOperation):
                self.warn(source, "invalid_cpu_observation_interval")
        # These windows overlap and include work. Union is diagnostic only;
        # their lengths are neither census execution time nor time sleeping.
        end = None
        for row in sorted(self.data["cpu_observations"], key=lambda r: r["start_monotonic_ns"]):
            a, b = row["start_monotonic_ns"], row["end_monotonic_ns"]
            self.data["cpu_observation_union_ns"] += max(0, b-max(a, end if end is not None else a))
            end = max(b, end if end is not None else b)
        return self.finish()

    def note(self, text):
        self.data["format"] = "committed_note"
        # Select only timing captures. Prose/status columns and embedded paths
        # are never copied, followed, interpreted as JSON, or used as inputs.
        heading = re.search(r"^# ALIGN v4 R0 re-run \d+ \((\d{4}-\d\d-\d\d) (\d\d:\d\d)(?:-\d\d:\d\d)? (PST|PDT)\)", text, re.M)
        timing = re.search(r"^\- Record: .*?\(created (\d\d:\d\d:\d\d)Z, finished (\d\d:\d\d:\d\d)Z; ([\d,]+\.\d+) s wall\)", text, re.M)
        if not heading or not timing:
            raise ValueError("unsupported R0 NOTE timing grammar")
        local_zone = timezone(timedelta(hours=-8 if heading[3] == "PST" else -7))
        local_start = datetime.fromisoformat(heading[1]+"T"+heading[2]).replace(tzinfo=local_zone)
        utc_start = local_start.astimezone(timezone.utc)
        a = datetime.fromisoformat(utc_start.date().isoformat()+"T"+timing[1]+"+00:00")
        if abs((a-utc_start).total_seconds()) >= 60:
            raise ValueError("R0 NOTE heading_and_start_disagree")
        b = datetime.combine(a.date(), datetime.strptime(timing[2], "%H:%M:%S").time(), timezone.utc)
        if b < a:
            b += timedelta(days=1)
        self.bounds(epoch_ns(a.isoformat()), epoch_ns(b.isoformat()))
        total = Decimal(timing[3].replace(",", ""))
        self.data.update(wall_ns=self.ns(total), wall_basis="rounded_NOTE_wall_seconds",
                         rounding_bound_ns=self.ns(Decimal(1).scaleb(total.as_tuple().exponent)/2))
        in_table = False
        for number, line in enumerate(text.splitlines(), 1):
            if line.strip() == "| Check | Status | Wall s |":
                in_table = True
                continue
            if not in_table:
                continue
            if not line.startswith("|"):
                in_table = False
                continue
            columns = [v.strip() for v in line.split("|")[1:-1]]
            if len(columns) != 3 or columns[0].startswith("---"):
                continue
            source = f"{self.source}:{number}"
            identity = re.fullmatch(r"([a-z][a-z-]*)(?: \(([A-Z])\))?", columns[0])
            if not identity:
                self.warn(source, "check_identity_unavailable")
                self.budget_valid = False
                continue
            try:
                value = Decimal(columns[2].replace(",", ""))
            except InvalidOperation:
                value = None
            self.check(identity[1], identity[2], self.duration(value, source), source)
            if value is not None and value.is_finite():
                self.data["rounding_bound_ns"] += self.ns(Decimal(1).scaleb(value.as_tuple().exponent)/2)
        # These exact recorded milestones establish the observed dwell. A
        # configured "dwell 300 s" alone cannot create an observed interval.
        agents = re.search(r"^\- Agents: .*? exited (\d\d:\d\d:\d\d) "+heading[3]+r".*?; desk fence (\d\d:\d\d:\d\d).*?; the run's dwell ended (\d\d:\d\d:\d\d); .*? spawned (\d\d:\d\d:\d\d)", text, re.M)
        if agents:
            start_local = a.astimezone(local_zone)
            def moment(clock, before):
                dt = datetime.combine(start_local.date(), datetime.strptime(clock, "%H:%M:%S").time(), local_zone)
                anchor = a if before else b
                if before and dt > anchor:
                    dt -= timedelta(days=1)
                elif not before and dt < anchor:
                    dt += timedelta(days=1)
                return epoch_ns(dt.isoformat())
            exit_ns, fence_ns, dwell_end, resumed = (moment(agents[i], i < 4) for i in range(1, 5))
            self.data["milestones"] = dict(agent_exit_ns=exit_ns, desk_fence_ns=fence_ns,
                                            dwell_end_ns=dwell_end, agent_resumed_ns=resumed)
            if exit_ns <= fence_ns <= dwell_end == self.data["start_ns"]:
                self.data["dwell"] = dict(start_ns=exit_ns, end_ns=dwell_end)
            else:
                self.warn(self.source, "R0_NOTE_dwell_milestones_inconsistent")
            self.data["post_finish_to_agent_ns"] = resumed-self.data["end_ns"]
        return self.finish()

    def finish(self):
        data = self.data
        data["checks_ns"] = sum(r["duration_ns"] or 0 for r in data["checks"])
        if not data["checks"]:
            self.budget_valid = False
            self.warn(self.source, "R0_checks_unavailable")
        if data["wall_ns"] is not None and self.budget_valid:
            remainder = data["wall_ns"]-data["checks_ns"]
            if remainder >= 0:
                data["unattributed_ns"] = remainder
            else:
                self.warn(self.source, "r0_check_budget_exceeds_wall")
        if data["wall_ns"] is not None and data["epoch_wall_ns"] is not None:
            data["epoch_minus_wall_ns"] = data["epoch_wall_ns"]-data["wall_ns"]
            tolerance = NS + data["rounding_bound_ns"] if data["format"] == "committed_note" else 1_000_000
            if abs(data["epoch_minus_wall_ns"]) > tolerance:
                self.warn(self.source, "R0_epoch_total_elapsed_disagreement")
        if data["dwell"] is None:
            data["unavailable"].append("dwell")
        if not data["cpu_observations"]:
            data["cpu_observation_union_ns"] = None
            data["unavailable"].append("cpu_observations")
        if data["format"] == "committed_note":
            data["unavailable"].append("nested_call_timing")
        return data


def worksheet_r0(data):
    def seconds(value):
        return "unavailable" if value is None else f"{value/NS:.6f}"
    lines = ["", "R0 DURATION BUDGET (unplaced sequential check totals; separate from epoch ledger)",
             "format: "+data["format"],
             "run wall: "+seconds(data["wall_ns"])+" s ("+data["wall_basis"]+")",
             "epoch envelope: "+seconds(data["epoch_wall_ns"])+" s",
             "check\tmodel\tseconds"]
    for row in data["checks"]:
        lines.append("\t".join((row["check"], row["model"] or "-", seconds(row["duration_ns"]))))
    lines += ["checks total: "+seconds(data["checks_ns"])+" s",
              "outside timed checks / missing check timing: "+seconds(data["unattributed_ns"])+" s",
              "budget rounding allowance (nearest decimal assumed): +/-"+seconds(data["rounding_bound_ns"])+" s",
              "R0 RUNGS (nested recorded call sums; rung wall is unavailable)"]
    for row in data["rungs"]:
        lines.append(f"{row['rung']}: calls="+seconds(row["call_ns"])+
                     f" s; count={row['recorded_calls']}; missing={row['missing_call_times']}; not_run={row['not_run']}")
    lines += ["R0 CALLS (nested diagnostics; do not add to check totals)"]
    for row in data["calls"]:
        lines.append(row["source"]+": "+seconds(row["duration_ns"])+" s")
    lines += ["CPU observation windows: "+str(len(data["cpu_observations"]))+
              "; union="+seconds(data["cpu_observation_union_ns"])+" s (NOT wait or guard execution time)"]
    dwell = data["dwell"]
    lines.append("observed pre-run dwell: "+seconds(dwell["end_ns"]-dwell["start_ns"] if dwell else None)+" s")
    for name, at in data["milestones"].items():
        stamp = (EPOCH+timedelta(seconds=at//NS)).isoformat()
        lines.append(name+": "+stamp)
    lines += ["finish-to-agent-resume gap: "+seconds(data["post_finish_to_agent_ns"])+" s (unattributed; outside run)",
              "R0 unavailable: "+", ".join(data["unavailable"])]
    return lines
