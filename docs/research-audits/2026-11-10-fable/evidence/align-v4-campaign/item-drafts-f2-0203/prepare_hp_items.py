"""Render and evaluate the hp-02 successor items using operational records only."""
import argparse
from datetime import date, datetime, time as wall_time, timedelta
import hashlib
import json
import math
import os
from pathlib import Path
import re
import stat
import subprocess
import sys
from tempfile import NamedTemporaryFile
import time
from zoneinfo import ZoneInfo

HERE = Path(__file__).resolve().parent
HP = HERE / "hp-02"
ZONE = ZoneInfo("America/Los_Angeles")
HP01_RECORDED_DATES = frozenset({date(2026, 11, 15)})  # RUN_STATE 335–344, ITEM-GATES-SPEC
PIN = "dd206025abb30fd5c07515cd4b34b3e653174810"
KIT_PATH = "hp-02/cl-hp-02.json"
KIT_SHA = "7693b8293b42b8ba20cbd321e201974745b172dc53c4f1397d2c1494f38fbe66"
HP01_SHA = "7eaf2660312ce6b3af90e8a1d9da1e05a6c409366a88a7e5e558d3bebb9d2965"
DELTA_COMMIT = "e3eaa282f9d4cea3b579eeb7bde989ff897df45e"
MAIN_RECORD = "6640a66719a2ff1f8cc38dbce3e8231f419e79d8"
LINE2_SENTENCE = (
    f"Line 2 for `cl-hp-02` (`{KIT_SHA}`) is `cl-hp-01`'s record under RL-165 §5; "
    "no frozen byte differs (RL-190 2)."
)
ARGUMENTS = ("02:00-02:35", "13:14-13:15")
LAUNCH_MARGIN_S = 600
CLOCK_GUARD_S = 120
COPY_WAIT_S = 600
START_SCHEMA = "hp-02.start.v4"
RUN_OBSERVATIONS = ("look", "hp01_dates", "latest_close", "history", "safety",
                    "stops", "copy", "priority", "calendar", "timing")
RANK1_POOL = "f2-stab-01..14"
RANK1_KITS = frozenset(f"f2-stab-{n:02d}" for n in range(1, 15))
RANK1_LEGS = frozenset(f"L{n:03d}" for n in range(1, 13))
RANK1_PIN = "2d347f721552fe03bdd19f113e7bad7a7c24908e"
PASS = frozenset({"ELIGIBLE", "ELIGIBLE_WITH_COPY_DEBT"})
ROSTERS = {
    "hp-02-s01": ["L001", "L002", "L003"],
    "hp-02-s02": ["L004", "L005", "L006", "L007"],
    "hp-02-s03": ["L008", "L009", "L010", "L011", "L012"],
}
INSTRUMENTS = ("f2-inst-01", "f2-inst-02", "f2-inst-03")
HIGHER = ("ready-session", "counted", "first-stability", *INSTRUMENTS)
HP_LEGS = frozenset(leg for roster in ROSTERS.values() for leg in roster)
CLOSE_KEYS = ("record", "receipt_sha256", "ended_epoch_s")
RESTORE_STOPS = frozenset({"RESTORE_UNPROVEN", "UNOWNED_MARKER"})
RANK_DECISION = ("CEDE_READY", "CEDE_COUNTED", "CEDE_RANK_1", "CEDE_INST_01", "CEDE_INST_02", "CEDE_INST_03")
FEEDS = {"agents", "meter", "volumes"}
PREFLIGHT = {
    "veto_clear", "maintenance_clear", "host_health", "disk_floor", "meter_available",
    "collector_available", "clock_ok", "on_ac", "battery_float", "night_lock_free",
    "mode_rules", "measurement_mode", "network_time_off", "frequency_zero",
}
MARKER = Path("/Users/Shared/JouleWise/host-power/high-power.marker")


class Refusal(ValueError):
    def __init__(self, decision, detail, *, cause=None, failed_read=False):
        super().__init__(detail)
        self.decision = decision
        self.cause = cause
        self.failed_read = failed_read


class OpenHold(Refusal):
    """A previously recorded refusal is not a new observation."""


def require(condition, decision, detail, **classification):
    if not condition:
        raise Refusal(decision, detail, **classification)


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def is_sha(value):
    return isinstance(value, str) and re.fullmatch("[0-9a-f]{64}", value) is not None


def is_text(value):
    return isinstance(value, str) and bool(value.strip())


def number(value):
    return type(value) in (int, float) and math.isfinite(value)


def local_date(epoch):
    return datetime.fromtimestamp(epoch, ZONE).date()


def midnight(day):
    return datetime.combine(day, wall_time.min, ZONE).timestamp()


def record(obj):
    return isinstance(obj, dict) and is_text(obj.get("record")) and is_text(obj.get("by"))


def read_json(data):
    def unique(pairs):
        obj = dict(pairs)
        if len(obj) != len(pairs):
            raise ValueError("duplicate JSON field")
        return obj

    return json.loads(data, object_pairs_hook=unique)


def git(repo, *args):
    return subprocess.check_output(["git", "--no-optional-locks", "-C", str(repo), *args], timeout=60)


def queue_start(row):
    return midnight(date.fromisoformat(row["not_before"]))


def queue_entry(item, queue, now):
    expiry = datetime.fromisoformat(queue["expires_at"])
    require(queue["schema"] == "joulewise.cadence_queue.v1" and is_text(queue["queue_id"]),
            "WAIT_BINDING", "invalid queue header")
    require(queue["halt"] is None, "WAIT_BINDING", "queue halt is active")
    entry = None
    seq = 0
    for row in queue["spans"]:
        span = row["span_id"]
        require(span in ROSTERS and row["seq"] == list(ROSTERS).index(span) + 1
                and row["seq"] > seq and row["attempt"] == 1 and row["legs"] == ROSTERS[span]
                and row["kit"] == {"path": KIT_PATH, "sha256": KIT_SHA}
                and row["block_id"] == "hp-02" and row.get("rerun_of") is None,
                "WAIT_BINDING", "queue does not preserve the ordered same-pin rosters")
        seq = row["seq"]
        start = queue_start(row)
        require(expiry.tzinfo is not None and start < expiry.timestamp(),
                "WAIT_BINDING", "invalid queue interval")
        if span == item["span"]:
            entry = row
            require(now >= start, "NEED_FRESH_QUEUE", "before the finite queue interval",
                    cause="only before not_before")
            require(now < expiry.timestamp(), "NEED_FRESH_QUEUE", "outside the finite queue interval")
    require(entry is not None and entry["seq"] == item["piece"] and entry["attempt"] == item["attempt"]
            and entry["legs"] == item["legs"], "WAIT_BINDING", "queue entry does not match the issue binding")
    return entry


def authority():
    return {
        "spec_sha256": sha256((HP / "ITEM-GATES-SPEC.md").read_bytes()),
        "occupancy_sha256": sha256((HP / "FREEZE-ADDENDUM.md").read_bytes()),
        "line_2": {
            "main_commit": MAIN_RECORD, "run_state_item": 338, "hp01_kit_sha256": HP01_SHA,
            "delta_commit": DELTA_COMMIT, "delta_path": "hp-02/HP02-DELTA.md",
            "frozen_block_byte_equal": True, "sentence": LINE2_SENTENCE,
        },
        "inherited_smoke": {"main_commit": MAIN_RECORD, "smoke_check_item": 337, "acceptance_item": 338},
    }


def issue_binding(item):
    return {k: item[k] for k in ("span", "piece", "attempt", "legs", "pin", "kit_sha", "queue", "predecessor")}


def check_issue(item, issue, now, phase, *, binding_only=False):
    auth = item["authority"]
    line2_ok = "yes" if issue.get("line_2") == auth["line_2"] else "no"
    require(
        record(issue) and issue["schema"] == "hp-02.issue.v1"
        and issue["status"] == ("PROPOSED" if phase == "Issue" else "ISSUED")
        and issue["binding"] == issue_binding(item)
        and number(issue["issued_epoch_s"]) and (binding_only or issue["issued_epoch_s"] <= now)
        and number(issue["check_deadline_epoch_s"])
        and is_text(issue["check_target"]) and is_text(issue["latest_close_at_issue"])
        and issue["spec_sha256"] == auth["spec_sha256"]
        and issue["occupancy_sha256"] == auth["occupancy_sha256"]
        and issue["inherited_smoke"] == auth["inherited_smoke"]
        and line2_ok == "yes",
        "WAIT_BINDING", "issue identity, accepted spec, inherited smoke or LINE2_OK missing",
    )
    for expiry in (item["expires_epoch_s"], issue["expires_epoch_s"]):
        require(expiry is None or number(expiry) and (binding_only or expiry > now),
                "WAIT_BINDING", "item or issue expiry is invalid or reached")


def check_look_binding(look, now, sampled_at):
    require(
        record(look) and look["scope"] == "lm-hp-01" and look["kit_sha256"] == KIT_SHA
        and look["checked_through"] == sampled_at and look["checked_through"] <= now
        and look["execution_register_checked"] is True and look["both_custody_roots_checked"] is True
        and look["all_execution_routes_covered"] is True,
        "WAIT_EVIDENCE", "current scoped look evidence required",
    )

def check_look(look, now, sampled_at):
    check_look_binding(look, now, sampled_at)
    require(look["status"] != "ran", "NOT_ADMITTED", "lm-hp-01 already started")
    require(look["status"] == "not_run" and look["pending_conflict"] is False, "WAIT_EVIDENCE", "look unresolved",
            failed_read=look["status"] not in ("not_run", "reserved", "pending", "queued")
            and look["pending_conflict"] is not True)


def history_states(history):
    require(record(history) and history["complete"] is True and history["kit_sha256"] == KIT_SHA,
            "WAIT_EVIDENCE", "complete per-leg execution history required")
    states = history["legs"]
    require(isinstance(states, dict) and states.keys() == HP_LEGS
            and all(state in ("unrun", "spent", "ambiguous") for state in states.values()),
            "WAIT_EVIDENCE", "history must classify the entire fixed roster")
    return states


def check_close_identity_agreement(first, second):
    same_record = first["record"] == second["record"]
    same_receipt = first["receipt_sha256"] == second["receipt_sha256"]
    same_end = first["ended_epoch_s"] == second["ended_epoch_s"]
    if same_record or same_receipt or same_end:
        require(same_receipt and same_end, "WAIT_EVIDENCE", "close identity, receipt or chronology conflicts")


def check_history(item, obs, close):
    history = obs["history"]
    states = history_states(history)
    current = [states[leg] for leg in item["legs"]]
    require("spent" not in current, "SKIP_SPENT", "roster already started")
    require(all(state == "unrun" for state in current), "WAIT_EVIDENCE", "ambiguous unrun roster")
    require(all(states[leg] == "unrun" for span, roster in ROSTERS.items()
                if span > item["span"] for leg in roster),
            "WAIT_EVIDENCE", "later HP roster started or unresolved before this one")
    previous = item["predecessor"]
    if previous is not None:
        prior = history["prior_check"]
        require(record(prior) and prior["span"] == previous and prior["kit_sha256"] == KIT_SHA
                and type(prior["attempt"]) is int and prior["attempt"] == 1 and prior["legs"] == ROSTERS[previous]
                and prior["host"] == obs["host"] and number(prior["ended_epoch_s"])
                and prior["ended_epoch_s"] <= close["ended_epoch_s"],
                "WAIT_EVIDENCE", "exact prior HP Check required")
        require(prior["status"] != "dirty", "HOLD_KIT", "prior HP Check dirty")
        require(prior["status"] == "clean" and is_sha(prior["receipt_sha256"])
                and prior["fence_gone"] is True and prior["restore_proven"] is True
                and all(states.get(leg) == "spent" for span, roster in ROSTERS.items()
                        if span < item["span"] for leg in roster),
                "WAIT_EVIDENCE", "prior HP Check/roster unresolved")
        check_close_identity_agreement(prior, close)


def automatic(value):
    return type(value) is int and value == 0


def check_close_binding(close, obs):
    require(record(close) and close["identity"] == "latest-unambiguous" and close["host"] == obs["host"]
            and is_sha(close["receipt_sha256"])
            and number(close["ended_epoch_s"]) and close["ended_epoch_s"] <= obs["observed_epoch_s"],
            "WAIT_EVIDENCE", "latest identified Check at observation time required")


def check_close_restore(close):
    restore_status = close.get("restore_status")
    require(restore_status in ("proven", "unproven"), "HOLD_HOST", "unknown initial restore status")
    recovery = close.get("recovery")
    if recovery is not None or restore_status == "unproven":
        require(record(recovery) and recovery.get("safe_route_proven") is True
                and recovery.get("same_close") == close["record"],
                "HOLD_HOST", "restore unproven; use the safe pinned recovery route")
        if recovery.get("result") == "failed":
            raise Refusal("HALT_AND_PAGE", "pinned recovery failed; halt host and page Ed and lead")
        require(recovery.get("result") == "proven", "HOLD_HOST", "restore unproven after deferred recovery")
        residual = recovery.get("residual_refusal")
        require(residual != "open", "HOLD_KIT", "restore proven; separate refusal open")
        require(residual == "clear", "WAIT_EVIDENCE", "post-recovery stop status unknown")


def check_close_proof(close):
    require(
        close["receipt_ok"] is True and close["restores_read_back"] is True
        and automatic(close["ac_powermode"])
        and close["marker_present_or_link"] is False and close["host_lock_free"] is True,
        "HOLD_HOST", "latest close restore/readbacks incomplete",
    )


def check_close_stops(close):
    feeds = close["feeds_proven_stopped"]
    groups = close["groups"]
    require(
        set(feeds) == FEEDS and all(feeds[feed] is True for feed in FEEDS)
        and isinstance(groups, list) and bool(groups)
        and all(is_text(group["group_id"]) and is_text(group["start_identity"])
                and group["receipt_stop"] == "proven" and group["independent_census"] == "empty"
                for group in groups),
        "HOLD_CLOSE", "receipt stop proof and independent group absence both required",
    )


def check_close(close, obs):
    check_close_binding(close, obs)
    check_close_restore(close)
    require(close["fence_gone"] is True, "WAIT_FENCE", "shared fence clearance unproven")
    check_close_proof(close)
    check_close_stops(close)


def open_stops(obs):
    stops = obs["stops"]
    require(record(stops) and stops["complete"] is True, "WAIT_EVIDENCE", "scoped stop register required")
    names = stops["open"]
    require(isinstance(names, list) and all(isinstance(stop, dict) and is_text(stop.get("code"))
                                            and is_text(stop.get("scope")) for stop in names),
            "WAIT_EVIDENCE", "invalid stop register")
    return names


def check_safety(obs, close, *, include_stops=True):
    safety = obs["safety"]
    require(
        record(safety) and safety["close_record"] == close["record"]
        and safety["close_sha256"] == close["receipt_sha256"] and safety["host"] == obs["host"]
        and automatic(safety["ac_powermode"])
        and safety["marker_present_or_link"] is False
        and safety["foreign_agent_census_casefold"] == [] and safety["foreign_process_census"] == []
        and all(safety["preflight"].get(line) is True for line in PREFLIGHT),
        "HOLD_HOST", "current scoped restore, census or preflight failed",
    )
    verify = safety["mode_verify"]
    require(record(verify) and type(verify["rc"]) is int
            and (verify["rc"] == 0 and verify["exceptions"] == []
                 or verify["rc"] == 1 and verify["exceptions"] == ["own-agent-tree-or-permitted-jobs"]),
            "HOLD_HOST", "measurement mode verify failed beyond the documented exception")
    if include_stops:
        check_scoped_stops(obs)


def check_scoped_stops(obs):
    for stop in open_stops(obs):
        code = stop["code"]
        require(code not in RESTORE_STOPS | {"DISK_FLOOR", "HOST_STATE"}
                and stop["scope"] != "host", "HOLD_HOST", f"host-wide stop {code}")
        require(stop["scope"] not in ("measured", "hp-02", obs["binding"]["span"]),
                "HOLD_KIT", f"applicable stop {code}")
        require(stop["scope"] in ("counted", "v4", "other-kit"), "WAIT_EVIDENCE", "unresolved stop scope")


def copy_verified(copy):
    return (
        copy.get("status") == "verified" and is_sha(copy.get("plaintext_manifest_sha256"))
        and is_sha(copy.get("ciphertext_sha256")) and type(copy.get("ciphertext_size_bytes")) is int
        and copy["ciphertext_size_bytes"] > 0 and is_text(copy.get("provider_verification"))
    )


def check_copy(copy, close, now):
    require(record(copy) and copy["predecessor"] == close["record"], "WAIT_COPY", "unbound copy evidence")
    stopped = copy["transfer_stopped"] is True
    if copy_verified(copy) and stopped:
        return False
    require(now - close["ended_epoch_s"] >= COPY_WAIT_S, "WAIT_COPY", "waiting within the copy interval")
    require(stopped, "HOLD_FOREIGN_LOAD", "transfer has not stopped")
    require(is_text(copy.get("debt_record")), "WAIT_COPY", "copy debt is unrecorded")
    return True


def hp01_dates(obs):
    census = obs["hp01_dates"]
    require(record(census) and census["complete"] is True and census["kit_sha256"] == HP01_SHA,
            "WAIT_EVIDENCE", "complete hp-01 date census required")
    rows = census["t0_dates"]
    require(isinstance(rows, list) and rows and all(isinstance(day, str) for day in rows),
            "WAIT_EVIDENCE", "hp-01 t0-dates must be a nonempty list of local dates")
    dates = {date.fromisoformat(day) for day in rows}
    require({day.isoformat() for day in dates} == set(rows),
            "WAIT_EVIDENCE", "hp-01 t0-dates must use YYYY-MM-DD")
    return dates


def check_rank1(entry, day):
    require(entry.get("pool") == RANK1_POOL, "WAIT_EVIDENCE", "rank 1 must adjudicate the 01–14 pool")
    if entry["status"] == "eligible":
        require(entry["entry_id"] in RANK1_KITS, "WAIT_EVIDENCE", "invalid first-stability kit")
        return
    if entry.get("basis") == "spent-for-date":
        complete = entry.get("completion")
        require(record(complete) and is_text(complete.get("leg_id")) and is_text(complete.get("t0_date")),
                "WAIT_EVIDENCE", "rank 1 completion evidence is missing", failed_read=True)
        require(record(complete) and complete.get("status") == "completed"
                and complete.get("kit_id") in RANK1_KITS
                and complete["kit_id"] == entry["entry_id"]
                and complete.get("pin") == RANK1_PIN and complete.get("t0_date") == day.isoformat()
                and complete.get("leg_id") in RANK1_LEGS,
                "WAIT_EVIDENCE", "rank 1 spent requires a completed 01–14 leg and this date's completion record")
        return
    census = entry.get("eligibility_census")
    require(entry.get("basis") == "no-eligible-kit" and entry["entry_id"] == RANK1_POOL
            and record(census) and census.get("date") == day.isoformat()
            and census.get("pool") == RANK1_POOL
            and census.get("complete") is True and census.get("eligible_kits") == [],
            "WAIT_EVIDENCE", "rank 1 unavailability requires a complete pool adjudication")


def check_rank(priority, day):
    require(record(priority) and priority["complete"] is True and priority["date"] == day.isoformat()
            and priority["r1_post_close"] is True, "WAIT_EVIDENCE", "current complete ladder required",
            failed_read=True)
    by_rung = {}
    for entry in priority["entries"]:
        require(record(entry) and is_text(entry.get("entry_id"))
                and entry["rung"] in (*HIGHER, "further-stability")
                and entry["status"] in ("eligible", "unavailable"),
                "WAIT_EVIDENCE", "unknown ladder entry eligibility")
        rung = entry["rung"]
        require(rung not in by_rung, "WAIT_EVIDENCE", "ambiguous ladder rung")
        by_rung[rung] = entry
    require(set(by_rung) == {*HIGHER, "further-stability"}, "WAIT_EVIDENCE", "incomplete ladder")
    check_rank1(by_rung["first-stability"], day)
    instruments = [by_rung[rung] for rung in INSTRUMENTS]
    require(all(entry["entry_id"] == entry["rung"] for entry in instruments)
            and len({entry["record"] for entry in instruments}) == len(instruments),
            "WAIT_EVIDENCE", "each finite instrument kit needs its own adjudication")
    for rung, decision in zip(HIGHER, RANK_DECISION):
        require(by_rung[rung]["status"] != "eligible", decision, by_rung[rung]["record"])
    return by_rung["further-stability"]["status"] == "eligible"


def dated_limits(calendar):
    require(record(calendar) and calendar["complete"] is True, "WAIT_EVIDENCE", "complete dated starts required")
    transfer = calendar["post_fence_transfer_s"]
    require(number(transfer) and 0 <= transfer <= 600, "WAIT_EVIDENCE", "unbounded post-fence transition")
    latest_start = math.inf
    starts = calendar["starts"]
    require(isinstance(starts, list) and len({row["span"] for row in starts}) == len(starts),
            "WAIT_EVIDENCE", "ambiguous outstanding counted starts")
    for row in reversed(starts):
        day = date.fromisoformat(row["date"])
        first, last = midnight(day), midnight(day + timedelta(days=1)) - 1
        transition = row["through_transition_s"]
        require(record(row) and is_text(row["pin"]) and number(transition) and transition >= 0
                and isinstance(row["windows"], list) and bool(row["windows"]),
                "WAIT_EVIDENCE", "counted pin/start/transition bounds missing")
        upper = min(last, math.floor(latest_start - transition)) if math.isfinite(latest_start) else last
        choices = []
        for lo, hi in row["windows"]:
            require(type(lo) is int and type(hi) is int and first <= lo <= hi <= last,
                    "WAIT_EVIDENCE", "invalid pin start window for counted date")
            if lo <= upper:
                choices.append(min(hi, upper))
        if not choices:
            yield row["span"], None
            return
        latest_start = max(choices)
        yield row["span"], latest_start


def check_dated(calendar, now, fence_s, boundaries=None):
    limits = list(dated_limits(calendar))
    transfer = calendar["post_fence_transfer_s"]
    if boundaries is not None:
        for span, latest in limits:
            if latest is not None:
                boundaries[latest - fence_s - transfer] = f"last HP start preserving {span}"
        check_guard_band(boundaries, now)
    earliest = math.ceil(now + fence_s + transfer)
    for span, latest in limits:
        require(latest is not None and latest >= earliest, "CEDE_DATED", f"would block counted start {span}")


def add_window_boundaries(boundaries, epoch, windows, label, *, offset=0, duration=0):
    from joulewise.cadence import legs

    for first, end in legs.window_epochs(epoch + offset, windows):
        edge = first - offset - duration
        boundaries[edge] = label
        if duration:
            # The half-open overlap test changes just AFTER this equality.
            boundaries[math.nextafter(edge, math.inf)] = label
        boundaries[end - offset] = label


def occupancy(item, kit_path, now, timing, arguments=ARGUMENTS, planner=None, resample=None,
              boundaries=None):
    """Compose the pinned stages through outer clearance; no native actions."""
    from joulewise.cadence import legs
    from scripts import align_r1_rehearsal as r1, cadence_legs_runner as runner
    from scripts import launch_align_r0 as base, launch_cadence_span as launcher

    planner = launcher.cadence_plan if planner is None else planner
    roster = ",".join(item["legs"])
    for arg in arguments:
        try:
            plan = planner(kit_path, roster, arg, t0=now)
        except legs.PlanError as err:
            if len(err.problems) == 1 and "meets a batch blackout" in err.problems[0]:
                if resample is not None and arg != arguments[-1]:
                    fresh = resample()
                    require(number(fresh) and fresh >= now, "WAIT_EVIDENCE", "clock changed during planning")
                    now = fresh
                continue
            raise Refusal("WAIT_PIN", str(err)) from err
        except ValueError as err:
            raise Refusal("WAIT_PIN", str(err)) from err
        break
    else:
        raise Refusal("WAIT_PIN", "both explicit plans meet a batch blackout")

    work = item["worst_case_s"]
    fence = item["deadline_s"]
    minimum = launcher.cadence_minimum_seconds(plan)
    require(plan["worst_case_s"] == work and plan["expected_s"] == item["expected_s"]
            and plan["blackout_clear"] is True and plan["batch_windows"] == [arg]
            and [leg["leg_id"] for leg in plan["legs"]] == item["legs"]
            and minimum <= fence,
            "WAIT_PIN", "pin plan, roster or deadline mismatch")
    require(record(timing), "WAIT_EVIDENCE", "no demonstrated timing bound")
    keys = ("runner_start_max_s", "selector_sample_max_s", "soak_dispatch_max_s", "inner_soak_gate_max_s",
            "pre_leg_max_s", "leg_wait_overshoot_max_s", "post_last_cap_max_s",
            "restore_and_close_max_s", "outer_clear_max_s")
    require(all(number(timing.get(k)) and timing[k] >= 0 for k in keys),
            "WAIT_EVIDENCE", "missing or unbounded timing component", failed_read=True)

    soak_s = base.r1_soak_cap_s()
    inner_s = next(seconds for name, _, seconds, _ in r1.phase_plan() if name == "idle_soak")
    arg_window = legs.parse_window(arg)
    runner_lag = timing["runner_start_max_s"]
    selector = timing["selector_sample_max_s"]
    dispatch = timing["soak_dispatch_max_s"]
    attempts = len(plan["legs"]) + plan["redo_quota"]
    cut = fence - runner.WORK_RESERVE_S
    close_cut = fence - base.R1_CLEANUP_GRACE_S - 10
    require(
        runner_lag + base.DISPLAY_SLEEP_DWELL_S <= selector
        and selector + soak_s + attempts * plan["leg_cap_s"] <= cut
        and dispatch + timing["inner_soak_gate_max_s"] <= soak_s - inner_s,
        "WAIT_EVIDENCE", "setup, child check or leg-delay timing cannot prove the capped path",
    )
    require(not legs.blackout_bound_s(now, work + runner_lag, [arg_window]),
            "WITHHOLD_REPLAN", "selected argument can refuse during runner handoff")

    after_setup = now + selector
    soak_windows = [arg_window, r1.OS_BATCH_WINDOW_LOCAL]
    if boundaries is not None:
        add_window_boundaries(boundaries, now, soak_windows, "soak wait",
                              offset=selector, duration=soak_s)
    soak_wait = legs.interval_delay(after_setup, soak_s, soak_windows)
    end = after_setup + soak_wait + dispatch + soak_s
    leg_wait = 0
    for _ in range(attempts):
        end += timing["pre_leg_max_s"]
        # A wait pins the downstream clock to a window end until an upstream
        # boundary changes. Otherwise every downstream selector moves with t0.
        if boundaries is not None and not (soak_wait or leg_wait):
            add_window_boundaries(boundaries, now, [arg_window], "leg start wait",
                                  offset=end - now)
        wait = legs.leg_start_delay(end, [arg_window])
        end += wait + timing["leg_wait_overshoot_max_s"] + plan["leg_cap_s"]
        leg_wait += wait
    work_end = end - now + timing["post_last_cap_max_s"]
    close_end = work_end + timing["restore_and_close_max_s"]
    through_clearance = close_end + timing["outer_clear_max_s"]
    if boundaries is not None:
        if soak_wait or leg_wait:
            boundaries[now + work_end - cut] = "work cutoff"
            boundaries[now + close_end - close_cut] = "close cutoff"
            boundaries[now + through_clearance - fence] = "outer clearance cutoff"
        check_guard_band(boundaries, now)
    require(work_end <= cut and close_end <= close_cut and through_clearance <= fence,
            "CEDE_FENCE", f"composed clearance at +{through_clearance:g}s; fence +{fence}s")
    return {
        "argument": arg, "t0": now, "deadline": now + fence, "work_s": work_end,
        "minimum_s": minimum,
        "soak_wait_s": soak_wait, "leg_wait_s": leg_wait, "close_s": close_end,
        "through_clearance_s": through_clearance, "fence_s": fence,
    }


def check_observation(item, issue, obs, phase, now, *, binding_only=False):
    require(record(obs) and obs["schema"] == "hp-02.observation.v1" and obs["phase"] == phase
            and is_text(obs["host"]) and obs["binding"] == issue_binding(item)
            and obs["issue_record"] == issue["record"]
            and number(obs["observed_epoch_s"]) and number(obs["valid_through_epoch_s"])
            and (binding_only or obs["observed_epoch_s"] <= now <= obs["valid_through_epoch_s"])
            and obs["observed_epoch_s"] >= issue["issued_epoch_s"],
            "WAIT_EVIDENCE", "fresh phase- and issue-bound operational observation required")


def check_fence(obs):
    require(obs.get("fence_clear") is True, "WAIT_FENCE", "shared fence still live or status unknown")


def check_issue_close(issue, obs, phase):
    check_close(obs["latest_close"], obs)
    if phase == "Issue":
        require(obs["latest_close"]["record"] == issue["latest_close_at_issue"],
                "WAIT_EVIDENCE", "issue close mismatch")


def check_look_priority(obs, now):
    try:
        check_look(obs["look"], now, obs["observed_epoch_s"])
    except Refusal as ex:
        if ex.decision == "NOT_ADMITTED" and any(
            entry.get("rung") == "further-stability" and entry.get("status") == "eligible"
            for entry in (obs.get("priority") or {}).get("entries", [])
        ):
            raise Refusal("SELECT_RANK_4", str(ex)) from ex
        raise


def check_dates(obs, now):
    dates = hp01_dates(obs)
    require(local_date(now) not in dates, "INELIGIBLE_DATE", "hp-01 leg on this t0-date")
    require(HP01_RECORDED_DATES <= dates, "WAIT_EVIDENCE", "hp-01 census omits a documented t0-date")


def phase_checks(item, issue, obs, phase, now):
    # These are the same validators used by the pure replay. Section names
    # supply provenance when more than one independent input refuses.
    yield "fence", lambda: check_fence(obs)
    yield "latest_close", lambda: check_issue_close(issue, obs, phase)
    yield "safety", lambda: check_safety(obs, obs["latest_close"], include_stops=False)
    yield "stops", lambda: check_scoped_stops(obs)
    yield "priority", lambda: check_rank(obs["priority"], local_date(now))
    yield "look", lambda: check_look_priority(obs, now)
    yield "hp01_dates", lambda: check_dates(obs, now)
    yield "history", lambda: check_history(item, obs, obs["latest_close"])
    yield "copy", lambda: check_copy(obs["copy"], obs["latest_close"], now)


def tagged(source, check, *args, **kwargs):
    try:
        return check(*args, **kwargs)
    except (Refusal, KeyError, ValueError, OSError, TypeError, AttributeError, OverflowError, RuntimeError,
            subprocess.SubprocessError) as ex:
        if not hasattr(ex, "source"):
            ex.source = source
        raise


def decide(item, issue, obs, phase, now, kit_path, queue_bytes, *, planner=None, resample=None,
           boundaries=None, raise_refusal=False):
    """Evaluate the phase snapshot; run_gate adds custody and dispatch preconditions."""
    from joulewise.cadence import kit as kitmod, queue as queuemod

    try:
        check_issue(item, issue, now, phase)
        require(sha256(queue_bytes) == item["queue"]["sha256"], "WAIT_BINDING", "staged queue bytes changed")
        kit, sha = kitmod.load_kit(kit_path)
        require(sha == item["kit_sha"] == KIT_SHA and kit["frozen"]["commit"] == item["pin"] == PIN,
                "WAIT_BINDING", "kit or runner pin mismatch")
        queue = read_json(queue_bytes)
        queuemod.validate_queue(queue, {KIT_PATH: (kit, sha)})
        queue_entry(item, queue, now)
        check_observation(item, issue, obs, phase, now)
        for source, check in phase_checks(item, issue, obs, phase, now):
            debt = tagged(source, check)
        timing = tagged("timing", occupancy, item, kit_path, now, obs.get("timing"), planner=planner,
                        resample=resample, boundaries=boundaries)
        t0 = timing["t0"]
        if t0 != now:
            queue_entry(item, queue, t0)
            require(t0 <= obs["valid_through_epoch_s"] and local_date(t0) == local_date(now),
                    "WAIT_EVIDENCE", "alternate plan needs a fresh dated observation")
        tagged("calendar", check_dated, obs["calendar"], t0, timing["fence_s"], boundaries)
        return {"decision": "ELIGIBLE_WITH_COPY_DEBT" if debt else "ELIGIBLE", **timing}
    except Refusal as ex:
        if raise_refusal:
            raise
        return {"decision": ex.decision, "detail": str(ex)}
    except (KeyError, ValueError, OSError, TypeError, AttributeError, OverflowError) as ex:
        if raise_refusal:
            raise
        return {"decision": "WAIT_EVIDENCE", "detail": f"incomplete or invalid input: {ex}"}
CHECK=r'''import json, sys
from pathlib import Path
out=Path(sys.argv[1]); roster=sys.argv[2].split(',')
r=json.loads((out/'runner_receipt.json').read_text())
assert r.get('mock') in (None,False), 'synthetic receipt is not live evidence'
assert r['runner_kind']=='cadence-legs-v1' and r['roster']==roster
assert r['batch_windows']==[sys.argv[3]]
assert r['kit']['campaign_id']=='cl-hp-02' and r['kit']['sha256']=='@SHA@'
assert r['kit']['frozen_commit']=='dd206025abb30fd5c07515cd4b34b3e653174810'
assert r['rc']==0 and not r.get('error') and r['legs_finished']==len(roster)==r['legs_planned']
assert r['span_result']['outcome']=='MEASURED_OK' and r['span_result']['chain_outcome']=='COMPLETE'
hp=r['high_power']; proof=hp['close_proof']
assert proof['proven'] is True and type(proof['ac_powermode']) is int and proof['ac_powermode']==0
assert proof['host_marker_present'] is False
assert not hp.get('revoked'), 'HP admission revoked: hold for the research lead'
assert set(r['feeds'])=={'agents','meter','volumes'}
assert all(f['stop']['proven_stopped'] is True for f in r['feeds'].values())
assert all(sum(s['name']==name for s in r['steps'])==1 for name in ('restore','stop-agents','stop-meter','stop-volumes','power_proof','host_lock_release'))
assert all(s['rc']==0 for s in r['steps'] if s['name']=='restore' or s['name'].startswith(('stop-','close-','power_','host_lock_release')))
span=json.loads((out/'desk-bundle/span/result.json').read_text()); assert span['restore_proven'] is True
print('operational receipt',r['rc'],r['legs_finished'],r['ended'],'power close',proof)
for leg in roster:
    rec=json.loads((out/'legs'/leg/'leg_record.json').read_text())
    result=rec.get('result') or {}
    summary=json.loads((out/'desk-bundle/legs'/leg/'leg_summary.json').read_text())
    print(leg,{k:result.get(k) for k in ('leg_status','g0_outcome','g0_wait_s','decode_tokens','decode_cap_reached','prefill_tokens','ac_powermode')},
          {k:summary.get(k) for k in ('admitted','wall_s','budget_s','contaminated_redos','g0_outcome')})
print('RECEIPT OK; this is operational verification, never an energy read')
'''


GATES = r'''# Call from the rendered item; each phase reads its own fresh record.
hp_gate() {
  phase=$1
  observation=$2
  "$PY" -I -B "$HP_DRAFTS/prepare_hp_items.py" gate "$SPAN" "$phase" \
    --repo "$REPO" --kit "$KIT" --queue "$QUEUE_FILE" \
    --issue "$HP_ISSUE" --issue-sha "$HP_ISSUE_SHA" --observation "$observation" \
    --custody "$CUSTODY" --output "$OUT" --magistrate-pid "$MAGISTRATE_PID"
}
'''


def render(source_repo, queue_commit):
    queue_commit = git(source_repo, "rev-parse", queue_commit + "^{commit}").decode().strip()
    prefix = HP.relative_to(source_repo).as_posix()
    path = f"{prefix}/queue-b.json"
    queue_data = git(source_repo, "show", f"{queue_commit}:{path}")
    if queue_data != (HP / "queue-b.json").read_bytes():
        raise ValueError("queue-b is not the committed byte stream")
    queue = read_json(queue_data)
    old = read_json((HP / "queue-a.json").read_bytes())
    if (queue["spans"] != old["spans"] or queue["expires_at"] != "2026-11-30T00:00:00-08:00"
            or any(row["not_before"] != "2026-11-21" for row in queue["spans"])):
        raise ValueError("queue-b differs from the ruled successor")
    if sha256((HP / "cl-hp-02.json").read_bytes()) != KIT_SHA:
        raise ValueError("kit digest differs")
    build = read_json((HERE / "evidence/kit-build.json").read_bytes())
    hp_build = next(row for row in build["kits"] if row["name"] == "cl-hp-02")
    items = []
    previous = None
    for row in queue["spans"]:
        span, piece, roster = row["span_id"], row["seq"], row["legs"]
        if roster != ROSTERS[span]:
            raise ValueError("queue roster differs from the same-pin roster")
        plan = next(p["plan"] for p in hp_build["plans"]
                    if p["piece"] == piece and p["argument"] == ARGUMENTS[0])
        item = {
            "item": span, "span": span, "piece": piece, "rank": 3, "attempt": row["attempt"],
            "legs": roster, "predecessor": previous, "pin": PIN, "kit_sha": KIT_SHA,
            "queue": {"commit": queue_commit, "path": path, "sha256": sha256(queue_data)},
            "not_before": "2026-11-21T00:00:00-08:00", "expires_at": queue["expires_at"],
            "expires_epoch_s": None, "authority": authority(),
            "expected_s": plan["expected_s"], "worst_case_s": plan["worst_case_s"],
            "deadline_s": plan["worst_case_s"] + 1460,
        }
        (HP / f"ITEM-{span}.md").write_text(render_item(item), encoding="utf-8")
        items.append(item)
        previous = span
    (HP / "items.json").write_text(json.dumps(items, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    (HP / "gates.sh").write_text(GATES, encoding="utf-8")


def render_item(item):
    span = item["span"]
    legs = ",".join(item["legs"])
    prior = f"the clean Check for `{item['predecessor']}` and the latest host Check" if item["predecessor"] else (
        "the latest unambiguous clean host Check, named in the issue record and refreshed at arm"
    )
    queue = item["queue"]
    check = CHECK.replace("@SHA@", KIT_SHA)
    return f"""TBD. **Successor ready for the issuing desk under RL-190 §2 and ITEM-GATES-SPEC. Lead issues one attempt for `{span}` on `{PIN}`, ordered roster `{legs}`. Require {prior}. Exit the magistrate immediately when the launcher claims the shared fence.**

```pointer
owner: magistrate
wait: none
deadline: from the lead's typed issue Check deadline
on_early_or_refused: record the decision and re-rank on current eligible entries. Stop the host on unproven restore; follow the recovery procedure below. A started or ambiguously consumed leg stays held. Never skip a predecessor or replace a leg.
next_observable: the first activation after fence clearance runs Check and sends the operational verdict and close record to the lead
```

**Issue.** Bind the accepted spec and occupancy addendum, exact kit `cl-hp-02` SHA-256 `{KIT_SHA}`, rank 3, attempt 1, sequence {item['piece']}, ordered unrun leg IDs, prior Check, current close, named magistrate Check target and Check deadline. Name the admitted `queue-b.json` at `{queue['commit']}`, path `{queue['path']}`, SHA-256 `{queue['sha256']}`. Its local interval opens at `{item['not_before']}` and expires exclusively at `{item['expires_at']}`. The kit master seed is 2026111601 versus hp-01's 2026111404.

For `LINE2_OK=yes`, record all three:

1. RUN_STATE item 338 at `{MAIN_RECORD}`, hp-01 kit digest `{HP01_SHA}`, and its four-part line-2 record. CI 43673985768 at `2a8deb7b9` carries the twelve reds of 43600776368 at `fe907d0d3`, test for test. All twelve passed at PR #777's head in 43601158271. Preserve the historical record.
2. The independent [HP02-DELTA.md](HP02-DELTA.md) at `{DELTA_COMMIT}` and its finding that hp-02's `frozen` block is byte-equal to hp-01's.
3. {LINE2_SENTENCE}

Use the inherited Class A smoke accepted in RUN_STATE 337–338. The issuing desk confirms that `lm-hp-01` has neither started nor been reserved across the execution register and both custody roots, and records the census of hp-01 local t0-dates. This descriptive block is outside the 132 cap, day count, line 9, and every fit, and carries zero reserve. The future manifest lists both HP blocks by kit and receipt, roster and as-run position before any HP read. This supersedes the inherited kit prose about the interim look and reserve.

**Issue, Start and Run.** Invoke the same gate with a separate current observation for each phase. See [README.md](README.md) for the record fields and staging. The eligible ladder is effective READY, counted work, first stability leg of that local date from the lowest eligible kit 01–14, the finite instrument kits 01 → 02 → 03, this HP roster, then further stability. Re-rank at every clean close and at arm. The dated calendar contains every remaining counted start, including outstanding halves, on its actual allowed pin windows. A last counted start may be 23:59:59 and finish the next day.

The gate selects the explicit argument on the actual clock. It tries `02:00-02:35` first and uses `13:14-13:15` only after a window-only refusal. Expected work {item['expected_s']:,} s, plan worst {item['worst_case_s']:,} s, shared fence {item['deadline_s']:,} s. Fit the composed timing through outer clearance inside that fence, and reserve the entire fence plus any transfer outside it against dated starts. Supply demonstrable setup, wait, close, restore and clearance bounds with each phase. HP may run at any hour the pin admits. The runner soaks in Automatic on AC, applies G0 and load checks, sets the marker before changing to mode 2, verifies mode 2 across every included leg and keeps leg children from changing mode.

Before each phase, record current mode rules and measurement mode verification, the four RL-174 C lines, AC and floating battery, network time off, frequency zero, no lock, no maintenance or veto, disk floor, collector and meter, latest operational receipt, proven stop of every feed and group, and current independent group and case-insensitive agent census. Only the documented own-tree and jobs exceptions apply. A contradictory receipt cannot be overwritten with an empty census. Verify the latest copy by typed manifest and ciphertext digests, size and provider readback. At 600 s carry unresolved debt only after proving the transfer stopped. Preserve originals, page at 2 h and daily thereafter, and retain the original until two verified off-host copies and the off-host key exist.

**Start and check** (authorized desk only). Use a reviewed successor audit checkout and the detached measurement checkout below. Fill `HP_ISSUE` and its approved SHA, the staged `QUEUE_FILE`, the pinned `PY`, the desk PID and fresh phase record paths. Choose a new `OUT` under the HP campaign root. At Issue use `hp_gate Issue "$HP_ISSUE_OBSERVATION"` in place of the Start invocation, then have the lead record the passed decision and issue the item. At Start, the issue record must be ISSUED.

```sh
set -eu
set -o pipefail
SPAN={span}
LEGS={legs}
REPO=/Users/edr/code/jw-wt/cadence-{span}
KIT=/Users/edr/campaign-out/kits/cl-hp-02-RL174B.json
CUSTODY=/Users/edr/night-custody/magistrate
: "${{HP_DRAFTS:?absolute path to the reviewed item-drafts-f2-0203 directory}}"
: "${{OUT:?fresh HP output path}}"
. "$HP_DRAFTS/hp-02/gates.sh"
hp_gate Start "$HP_START_OBSERVATION" || exit 1
```

**Run.** Refresh the records, native census, marker, fence and clock after Start. Invoke the same gate with the Run observation immediately before launch. Run first verifies the atomically published Start receipt. It reads the operational observation afterward and requires its sample time to follow publication on the same host. The shared admission record retains observed close, restore, look-execution and spent-leg facts across issues and retries. Run returns WAIT in the 120 seconds before a derived clock boundary, including local midnight, pin and argument edges, finite queue endpoints and a higher rung's next eligible start. The guard includes the runway cutoff 600 seconds before each applicable expiry and the latest startup bound. The gate writes admission custody and the roster claim first, then re-reads the bound records, current rank, fence, census and AC mode before invoking the pinned launcher. The claim records the exact argument, decision t0 and deadline. The write-free interval ends at invocation. The frozen launcher then writes its runner specification, plist and fence. A state change after the final read remains the residual risk. The MBP is quiet under the magistrate, and host mode changes only through `measurement_mode`. On bootstrap refusal hold this attempt for the lead. Exit the session as soon as the launcher reports a claimed fence.

**Issue holds.** Issue, Start and Run use the frozen gate-machine table. Pure clock waits are transient. The sequenced ledger retains fact-dependent refusals, including blocks first seen on Run's final read. Unreadable issue identity or custody holds the admitted queue position separately. Later Start and Run require verified dispositions and current evidence. An observation may carry `hold_dispositions` with an exact cited lead or magistrate RUN_STATE item from published main. A later clean observation leaves holds open. An observed lm-hp-01 execution requires a separate lead attestation correction. A changed receipt projection under the same digest records a separate hold. See [README.md](README.md) for the ledger and disposition schema.

```sh
hp_gate Run "$HP_RUN_OBSERVATION" || exit 1
```

**Check.** Wait for shared fence clearance, including a dangling link check. Use the recorded output and `ARG` from the Run claim. Verify the operational receipt and run the pinned automatic desk against the operational projection only. Record the desk verdict, mode-to-first-G0 delay, per-leg wall/budget, revocation and all named stops. Report `LEG_OVERTIME` or fewer than nine included HP legs to the research lead as applicable. Check mode 0, no marker or host lock, network time off, frequency zero, independent group absence and measurement-mode verification. Record actual close and fence-gone times. A failed child stays unadmitted.

```sh
test ! -e "$CUSTODY/desk_fence.json" && test ! -L "$CUSTODY/desk_fence.json" || exit 1
"$PY" -I -B - "$OUT" "$LEGS" "$ARG" <<'PY'
{check}PY
```

**Restore owed.** If the close leaves restoration unproven, or a marker has no owner, hold the host. Once the measuring job and shared fence are clear, invoke the pinned `scripts/cadence_legs_runner.py restore-owed` once from the detached checkout and independently read back every restore line. The pin defers under the host lock and refuses W1 markers. Never delete a marker or recover during arm. If restoration still cannot be proven halt the host and page Ed and the lead. A proven recovery clears only its restore stop. Keep any receipt refusal, revocation or unresolved group open until positively dispositioned. Give the lead the Check before any successor arms.
"""


def runtime_files(args, item, *, binding_only=False):
    require(args.custody == Path("/Users/edr/night-custody/magistrate"),
            "HOLD_HOST", "use the shared host fence and roster ledger")
    if binding_only:
        return
    require(not os.path.lexists(args.custody / "desk_fence.json"), "WAIT_FENCE", "shared fence exists or is a link")
    require(not os.environ.get("JOULEWISE_HOST_STATE_DIR") and not os.path.lexists(MARKER),
            "HOLD_HOST", "host-state override or High Power marker")
    root = Path("/Users/edr/campaign-out/cl-hp-02")
    require(args.output.parent.resolve() == root and not os.path.lexists(args.output)
            and re.fullmatch(f"cq-{item['span']}-a1-[0-9]{{8}}T[0-9]{{6}}Z", args.output.name),
            "WAIT_BINDING", "output must be a new attempt directory under the HP campaign")


def assert_source_bindings(args, item):
    ref = item["queue"]
    require(git(args.repo, "rev-parse", "HEAD").decode().strip() == item["pin"]
            and subprocess.run(["git", "-C", str(args.repo), "symbolic-ref", "-q", "HEAD"],
                               capture_output=True, timeout=60).returncode == 1
            and not git(args.repo, "status", "--porcelain", "--untracked-files=all"),
            "WAIT_BINDING", "measurement checkout must be clean and detached at the pin")
    queue = args.queue.read_bytes()
    blob = git(args.repo, "show", f"{ref['commit']}:{ref['path']}")
    require(sha256(queue) == ref["sha256"] and queue == blob,
            "WAIT_BINDING", "queue commit, path or staged bytes differ")
    qtime = int(git(args.repo, "show", "-s", "--format=%ct", ref["commit"]))
    require(qtime <= time.time(), "WAIT_BINDING", "queue commit is in the future")
    delta_blob = git(args.repo, "show", f"{DELTA_COMMIT}:{Path(ref['path']).with_name('HP02-DELTA.md')}")
    require(delta_blob == (HP / "HP02-DELTA.md").read_bytes() and authority() == item["authority"],
            "WAIT_BINDING", "reviewed spec or delta record differs")
    kit = read_json(args.kit.read_bytes())
    require(sha256(args.kit.read_bytes()) == KIT_SHA and kit["frozen"]["commit"] == item["pin"],
            "WAIT_BINDING", "staged kit differs from the reviewed bytes")
    for path, expected in kit["frozen"]["paths"].items():
        require(sha256((args.repo / path).read_bytes()) == expected,
                "WAIT_BINDING", f"frozen path differs: {path}")
    return queue


def check_agent_census(obs, parent_pid):
    # Use the case-insensitive item 443 census. A permitted job needs its
    # exact separately attested command. Derive the magistrate tree by PPID.
    agents = subprocess.run(["pgrep", "-ilf", "claude|codex|cursor|copilot|chatgpt"],
                            text=True, capture_output=True, timeout=10)
    require(agents.returncode in (0, 1), "HOLD_HOST", "agent census failed")
    ps = subprocess.check_output(["ps", "-axo", "pid=,ppid="], text=True, timeout=10)
    tree = {int(pid): int(ppid) for pid, ppid in (line.split() for line in ps.splitlines())}
    require(parent_pid > 1 and parent_pid in tree, "HOLD_HOST", "magistrate tree not present")
    jobs = obs["safety"]["agent_job_exceptions"]
    for row in agents.stdout.splitlines():
        raw_pid, cmd = row.split(maxsplit=1)
        pid = int(raw_pid)
        job = jobs.get(raw_pid)
        if (job and job["command"] == cmd and job["label"].startswith(("com.joulewise.", "local.jwbench."))
                and record(job)):
            continue
        while pid in tree and pid != parent_pid and tree[pid] != pid:
            pid = tree[pid]
        require(pid == parent_pid, "HOLD_HOST", f"foreign agent PID {raw_pid}")


def write_exclusive(path, data):
    publish_new_file(path, (json.dumps(data) + "\n").encode())


def sync_directory(path):
    directory = os.open(path, os.O_RDONLY)
    try:
        os.fsync(directory)
    finally:
        os.close(directory)


def write_admission_state(path, data):
    # The arm lock serializes readers and writers. Keep the prior version on
    # write failure, and sync the new file and directory before returning.
    with NamedTemporaryFile(dir=path.parent, prefix=".admission-", delete=False) as stream:
        temporary = Path(stream.name)
        try:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
            os.replace(temporary, path)
            sync_directory(path.parent)
        finally:
            temporary.unlink(missing_ok=True)


def remember_admission(path, obs, now, *, read_only=False, holds=None):
    """Record scoped positive and adverse facts before evaluating arm eligibility."""
    schema = "hp-02.admission.v1"
    if os.path.lexists(path):
        state = read_json(path.read_bytes())
        require(state["schema"] == schema and state["host"] == obs["host"],
                "WAIT_EVIDENCE", "observation conflicts with shared admission custody")
    else:
        require(not read_only, "WAIT_EVIDENCE", "durable admission state disappeared")
        state = {"schema": schema, "host": obs["host"], "latest_close": None, "closes": {},
                 "restore_stop": None, "look_execution": None, "spent": []}
    before = json.dumps(state, sort_keys=True)
    current_look_ran = False
    states = None
    try:
        try:
            look = obs["look"]
            check_look_binding(look, now, obs["observed_epoch_s"])
        except (Refusal, KeyError, TypeError):
            pass  # The normal decision still requires a valid, current look attestation.
        else:
            current_look_ran = look.get("status") == "ran"
            if current_look_ran and state["look_execution"] is None:
                state["look_execution"] = look
                originals = [h["ledger_sequence"] for h in holds.open.values()
                             if h["decision"] in ("NOT_ADMITTED", "SELECT_RANK_4")
                             and h["source_digest"] == source_digest(look)]
                state["execution_ledger_sequence"] = min(originals, default=1)

        try:
            states = history_states(obs["history"])
        except (Refusal, KeyError, TypeError):
            pass  # Malformed history cannot supply new facts or grant eligibility.
        else:
            state["spent"] = sorted(set(state["spent"]) | {leg for leg, status in states.items() if status == "spent"})

        stop = state["restore_stop"]
        if stop and stop["decision"] == "HALT_AND_PAGE":
            raise Refusal("HALT_AND_PAGE", f"failed recovery on {stop['close']['record']} remains an active host halt")

        close = obs["latest_close"]
        check_close_binding(close, obs)
        identity = {key: close[key] for key in CLOSE_KEYS}
        seen = state["closes"]
        for earlier in seen.values():
            check_close_identity_agreement(identity, earlier)
        latest = state["latest_close"]
        require(latest is None or close["ended_epoch_s"] >= seen[latest]["ended_epoch_s"],
                "WAIT_EVIDENCE", "latest close is older than one already observed")
        if stop:
            check_close_identity_agreement(identity, stop["close"])
            require(identity == stop["close"] and isinstance(close.get("recovery"), dict),
                    stop["decision"], f"restore disposition still owed for {stop['close']['record']}")

        seen[identity["record"]] = identity
        state["latest_close"] = identity["record"]
        try:
            stops = open_stops(obs)
        except (Refusal, KeyError, TypeError):
            stops = None
        restore_owed = stops is not None and any(entry["code"] in RESTORE_STOPS for entry in stops)
        try:
            check_close(close, obs)
            require(not restore_owed, "HOLD_HOST", "restore stop is open in the scoped register")
        except Refusal as exc:
            if restore_owed or close.get("restore_status") != "proven" or close.get("recovery") is not None:
                state["restore_stop"] = {
                    "close": identity, "decision": exc.decision,
                    "observation": obs["record"], "recovery": close.get("recovery"),
                }
            raise
        if stops is not None:
            state["restore_stop"] = None

        prior = obs["history"].get("prior_check") if states is not None else None
        if record(prior) and is_sha(prior.get("receipt_sha256")) and number(prior.get("ended_epoch_s")):
            for known in seen.values():
                check_close_identity_agreement(prior, known)

        if state["look_execution"] is not None and not current_look_ran:
            raise Refusal("NOT_ADMITTED", f"lm-hp-01 execution recorded by {state['look_execution']['record']}")
        if states is not None:
            require(all(states[leg] == "spent" for leg in state["spent"]),
                    "WAIT_EVIDENCE", "history reverses a previously observed spent leg")
    finally:
        serialized = json.dumps(state, sort_keys=True)
        if serialized != before:
            require(not read_only, "WAIT_EVIDENCE", "final observation needs a new admission write")
            write_admission_state(path, (serialized + "\n").encode())


def receipt_bytes(record):
    return json.dumps(record, sort_keys=True, separators=(",", ":")).encode()


def source_digest(source):
    declared = source.get("receipt_sha256")
    if is_sha(declared):
        return declared
    content = {key: value for key, value in source.items() if key not in ("sampled_at", "checked_through")}
    return sha256(receipt_bytes(content))


def immutable_receipts(obs):
    close = obs.get("latest_close")
    prior = obs.get("history", {}).get("prior_check") if isinstance(obs.get("history"), dict) else None
    sources = [(section, obs.get(section)) for section in RUN_OBSERVATIONS + ("watcher",)]
    sources.extend((("prior_check", prior), ("recovery", close.get("recovery") if isinstance(close, dict) else None)))
    for section, source in sources:
        if not record(source) or not is_sha(source.get("receipt_sha256")):
            continue
        # Sampling metadata, independent census and subsequent recovery have
        # their own evidence. The original receipt projection is immutable.
        content = {key: value for key, value in source.items() if key not in
                   ("record", "by", "sampled_at", "checked_through", "receipt_sha256", "recovery")}
        if isinstance(content.get("groups"), list) and all(isinstance(group, dict) for group in content["groups"]):
            content["groups"] = [
                {key: value for key, value in group.items() if key != "independent_census"}
                for group in content["groups"]
            ]
        yield section, source["receipt_sha256"], sha256(receipt_bytes(content))


MACHINE_PATH = HERE.parents[5] / "tests/hp02_gate_machine/GATE-MACHINE.json"
MACHINE = read_json(MACHINE_PATH.read_bytes())
OUTCOMES = MACHINE["outcomes"]
TRANSITIONS = {(row["from"], row["event"]): row for row in MACHINE["transitions"]}
QUEUE_HOLD_ROOT = Path("/Users/Shared/JouleWise/hp02-holds")
ENTRY_STATE = {"Issue": "proposed", "Start": "start_pending", "Run": "run_assessed", "FinalRun": "final_read"}
HOLD_DISPOSITION_SCHEMA = "hp-02.hold-disposition.v1"
HOLD_EVENT_SCHEMA = "hp-02.hold-event.v1"
HOLD_ROLE_OWNERS = {"lead": {"lead", "research-lead"}, "magistrate": {"magistrate"}}
READ_ERRORS = (OSError, ValueError, TypeError, KeyError, AttributeError, OverflowError, RuntimeError,
               StopIteration, subprocess.SubprocessError)


def transition(state, event=None, *, outcome=None, cause=None, verified=()):
    """Apply an event or classified outcome from the frozen machine."""
    if outcome is not None:
        rule = OUTCOMES[outcome]
        wire = rule.get("normalize", outcome)
        if event is None:
            policy = rule["policy"]
            if policy == "BY_CAUSE":
                policy = "TRANSIENT" if cause in rule["transient"] else rule["otherwise"]
            if policy == "ADVANCE" or "state" in rule:
                raise ValueError(f"{outcome} needs a phase event")
            event = ("clock_only" if policy == "TRANSIENT" else
                     "observe_execution" if rule.get("execution_recovery") else "bound_block_or_unknown")
    else:
        wire = None
    row = TRANSITIONS[state, event]
    if not set(row["requires"]) <= set(verified):
        raise ValueError(f"unproved gate transition {state} / {event}")
    return row["to"], wire


def trusted_run_state(repo, commit):
    require(isinstance(commit, str) and re.fullmatch("[0-9a-f]{40}", commit) is not None,
            "WAIT_EVIDENCE", "disposition needs a full authority commit")
    result = subprocess.run(["git", "--no-optional-locks", "-C", str(repo), "merge-base", "--is-ancestor",
                             commit, "refs/remotes/origin/main"], capture_output=True, timeout=60)
    require(result.returncode == 0, "WAIT_EVIDENCE", "disposition authority is outside published main")
    return git(repo, "show", f"{commit}:RUN_STATE.md").decode()


def verify_authority(repo, payload, fence, now):
    authority = payload.get("authority")
    require(isinstance(authority, dict) and set(authority) == {"role", "run_state_item", "commit"}
            and authority["role"] in HOLD_ROLE_OWNERS and type(authority["run_state_item"]) is int
            and authority["run_state_item"] > 0,
            "WAIT_EVIDENCE", "invalid hold disposition authority")
    item_number = authority["run_state_item"]
    markdown = trusted_run_state(repo, authority["commit"])
    sections = re.split(r"(?m)^(\d+)\. \*\*", markdown)
    matches = [body for n, body in zip(sections[1::2], sections[2::2]) if int(n) == item_number]
    require(len(matches) == 1, "WAIT_EVIDENCE", "authority RUN_STATE item is missing or ambiguous")
    items = re.findall(r"(?ms)^\x60\x60\x60item\n(.+?)^\x60\x60\x60[ \t]*$", matches[0])
    require(len(items) == 1, "WAIT_EVIDENCE", "authority item lacks a typed item record")
    item = read_json(items[0])
    require(item.get("schema") == "joulewise.run_state_item.v1" and type(item.get("number")) is int
            and item["number"] == item_number and item.get("status") == "ISSUED" and item.get("owner") in HOLD_ROLE_OWNERS[authority["role"]]
            and number(item.get("issued_epoch_s")) and item["issued_epoch_s"] <= now,
            "WAIT_EVIDENCE", "RUN_STATE authority or publication time does not match")
    exact = {**payload, "authority": {k: authority[k] for k in ("role", "run_state_item")}}
    blocks = re.findall(rf"(?ms)^\x60\x60\x60{re.escape(fence)}\n(.+?)^\x60\x60\x60[ \t]*$", matches[0])
    require(any(receipt_bytes(read_json(block)) == receipt_bytes(exact) for block in blocks),
            "WAIT_EVIDENCE", "RUN_STATE item does not publish the exact disposition")


def verify_disposition(repo, disposition, hold, issue_id, now):
    scope = {k: hold[k] for k in ("queue_sha", "queue_seq") if k in hold}
    if not scope:
        scope["issue_id"] = issue_id
    require(isinstance(disposition, dict) and disposition.get("schema") == HOLD_DISPOSITION_SCHEMA
            and disposition.get("action") == "clear"
            and all(type(disposition.get(key)) is type(value) and disposition[key] == value
                    for key, value in scope.items())
            and set(disposition).intersection(("issue_id", "queue_sha", "queue_seq")) == set(scope)
            and disposition.get("hold_id") == hold["id"] and disposition.get("source_digest") == hold["source_digest"]
            and type(disposition.get("ledger_sequence")) is int
            and disposition["ledger_sequence"] > hold["ledger_sequence"],
            "WAIT_EVIDENCE", "disposition does not match the scope, hold, source digest and later ledger sequence")
    verify_authority(repo, disposition, "hp-02-hold-disposition", now)


class HoldCustodyError(RuntimeError):
    def __init__(self, source, error, *, marker=None):
        super().__init__(f"{source}: {error}")
        self.source = source
        self.error = error
        self.marker = marker


class HoldJournal:
    """One sequenced, append-only record format for issue and queue custody."""

    def __init__(self, ledger, item, issue=None, *, queue_root=None):
        self.root = ledger
        self.queue_scope = issue is None
        if self.queue_scope:
            self.scope = {"queue_sha": item["queue"]["sha256"], "queue_seq": item["piece"]}
            key = f"{self.scope['queue_sha']}-{self.scope['queue_seq']}"
            self.path = queue_root / f"{key}.records"
            self.seed = queue_root / f"{key}.json"
            self.inflight = None
        else:
            self.issue_id = sha256(receipt_bytes({"span": item["span"], "issue_record": issue["record"]}))
            self.scope = {"issue_id": self.issue_id}
            self.path = ledger / f"holds-{self.issue_id}"
            self.inflight = ledger / f"reading-{self.issue_id}.json"
            self.seed = None
        self.tail = None
        self.sequence = 0
        self.fingerprints = {}
        self.open = {}
        self.closed = {}
        try:
            if self.seed is not None and os.path.lexists(self.seed):
                data = read_receipt_file(self.seed)
                self.apply(read_json(data), sha256(data))
            if os.path.lexists(self.path):
                require(self.path.is_dir() and not self.path.is_symlink(),
                        "WAIT_EVIDENCE", "invalid hold ledger directory")
                for path in sorted(self.path.iterdir()):
                    data = read_receipt_file(path)
                    digest = sha256(data)
                    event = read_json(data)
                    require(path.name == f"{self.sequence + 1:08d}-{digest}.json"
                            and event["schema"] == HOLD_EVENT_SCHEMA and event["previous"] == self.tail,
                            "WAIT_EVIDENCE", "invalid hold ledger sequence or digest")
                    self.apply(event, digest)
        except READ_ERRORS as ex:
            raise HoldCustodyError("issue ledger read" if issue is not None else "queue ledger read", ex) from ex

    def begin_read(self):
        try:
            publish_new_file(self.inflight, receipt_bytes(self.scope) + b"\n")
        except OSError as ex:
            raise HoldCustodyError("issue ledger in-flight marker", ex) from ex

    def finish_read(self):
        try:
            self.inflight.unlink()
            sync_directory(self.root)
        except OSError as ex:
            raise HoldCustodyError("issue ledger write", ex, marker=self.inflight) from ex

    def apply(self, event, digest):
        require(all(event.get(k) == v for k, v in self.scope.items()),
                "WAIT_EVIDENCE", "hold ledger scope differs")
        self.sequence += 1
        require(self.fingerprints.keys().isdisjoint(event.get("sources", {})),
                "WAIT_EVIDENCE", "hold ledger rewrites an existing source")
        self.fingerprints.update(event.get("sources", {}))
        for hold in event["holds"]:
            require(hold["id"] not in self.open and hold["id"] not in self.closed
                    and hold.get("ledger_sequence", self.sequence) == self.sequence,
                    "WAIT_EVIDENCE", "duplicate hold identity or invalid sequence")
            self.open[hold["id"]] = {**hold, **self.scope, "ledger_sequence": self.sequence}
        for clearance in event["clears"]:
            hold_id = clearance["hold_id"]
            hold = self.open.pop(hold_id)
            require(all(clearance.get(k) == v for k, v in self.scope.items())
                    and clearance["source_digest"] == hold["source_digest"]
                    and clearance.get("ledger_sequence", self.sequence) > hold["ledger_sequence"],
                    "WAIT_EVIDENCE", "hold ledger disposition does not bind the open hold")
            self.closed[hold_id] = (hold, clearance)
        self.tail = digest

    def append(self, now, *, sources=None, holds=(), clears=(), corrections=(), initialize=False):
        if not (sources or holds or clears or corrections or initialize):
            return False
        event = {"schema": HOLD_EVENT_SCHEMA, **self.scope, "previous": self.tail,
                 "recorded_at": now, "sources": sources or {}, "holds": holds, "clears": clears}
        if corrections:
            event["attestation_corrections"] = corrections
        data = receipt_bytes(event) + b"\n"
        digest = sha256(data)
        try:
            if not self.path.exists():
                self.path.mkdir(parents=True)
                sync_directory(self.path.parent)
            publish_new_file(self.path / f"{self.sequence + 1:08d}-{digest}.json", data)
        except OSError as ex:
            raise HoldCustodyError("queue ledger write" if self.queue_scope else "issue ledger write",
                                   ex, marker=self.inflight) from ex
        self.apply(event, digest)
        return True

    def observe(self, now, failures, *, obs=None, initialize=False):
        sources = {}
        failures = list(failures)
        if obs is not None:
            for section, digest, fingerprint in immutable_receipts(obs):
                key = f"{section}:{digest}"
                previous = self.fingerprints.get(key)
                if previous is None:
                    sources[key] = fingerprint
                elif previous != fingerprint:
                    ex = Refusal("WAIT_EVIDENCE", f"{section} content changed under receipt digest {digest}")
                    failures.append((f"receipt-content-changed:{section}:{fingerprint}", ex,
                                     {"receipt_sha256": digest}, None))
        sequence = self.sequence + 1
        new = []
        existing = {(hold["fact"], hold["source_digest"]) for hold in self.open.values()}
        failed_sources = {(h["failed_read"]["source"], h["failed_read"]["error_class"])
                          for h in self.open.values() if "failed_read" in h}
        for source, ex, proof, marker in failures:
            read_error = not isinstance(ex, Refusal) or ex.failed_read or self.queue_scope
            outcome = ("CUSTODY_ERROR" if self.queue_scope else "READ_ERROR") if read_error else ex.decision
            event = "identity_or_issue_custody_failure" if self.queue_scope else None
            state, decision = transition(
                ENTRY_STATE[self.phase], event, outcome=outcome, cause=getattr(ex, "cause", None),
                verified=("append all newly observed blocking facts",
                          "retain original execution attestation digest across issues",
                          "durably identify failure independently by admitted queue SHA and sequence",
                          "open_holds empty", "preserve return phase"),
            )
            if state == "clock_wait":
                continue
            if read_error:
                error_class = type(ex).__name__
                if (source, error_class) in failed_sources:
                    continue
                failed_sources.add((source, error_class))
                failed = {"source": source, "error_class": error_class,
                          "attempt_time": now, "ledger_sequence": sequence}
                digest = sha256(receipt_bytes(failed))
                fact = "failed-read"
            else:
                failed = None
                digest = source_digest(proof)
                fact = f"{source}:{decision}"
            identity = (fact, digest)
            if identity in existing:
                continue
            hold_id = sha256(receipt_bytes([self.scope, sequence, fact, digest]))
            hold = {"id": hold_id, "fact": fact, "decision": decision, "detail": str(ex),
                    "source_digest": digest, "observed_at": now, "ledger_sequence": sequence}
            if failed:
                hold["failed_read"] = failed
            if marker is not None:
                hold["inflight"] = marker.name
            new.append(hold)
            existing.add(identity)
        return self.append(now, sources=sources, holds=new, initialize=initialize and not self.sequence)

    def verified_clearance(self, repo, row, now):
        hold_id = row.get("hold_id")
        if hold_id in self.closed:
            require(row == self.closed[hold_id][1], "WAIT_EVIDENCE", "conflicting hold disposition")
            return None
        require(hold_id in self.open, "WAIT_EVIDENCE", "disposition must name an open hold")
        hold = self.open[hold_id]
        verify_disposition(repo, row, hold, self.scope.get("issue_id"), now)
        return hold

    def require_clear(self):
        if self.open:
            hold = min(self.open.values(), key=lambda row: row["decision"] != "HALT_AND_PAGE")
            raise OpenHold(hold["decision"], f"open hold {hold['id']} ({hold['source_digest']}): {hold['detail']}")


def publish_new_file(path, data):
    linked = False
    try:
        with NamedTemporaryFile(dir=path.parent, prefix=".gate-", delete=False) as stream:
            temporary = Path(stream.name)
            try:
                stream.write(data)
                stream.flush()
                os.fsync(stream.fileno())
                os.link(temporary, path)
                linked = True
            finally:
                temporary.unlink()
        sync_directory(path.parent)
    except OSError:
        if linked:
            path.unlink()
        raise


def start_seal_path(path):
    return path.with_suffix(".published.json")


def publish_start(path, result):
    receipt = {**result, "schema": START_SCHEMA, "state": "PUBLISHED"}
    envelope = {"receipt": receipt, "sha256": sha256(receipt_bytes(receipt))}
    data = receipt_bytes(envelope) + b"\n"
    publish_new_file(path, data)
    # The complete, digest-verifiable receipt is visible and durable now.
    # Timestamp after that event, and bind the timestamp to those exact bytes.
    published = {"published_at": time.time(), "receipt_sha256": sha256(data)}
    try:
        seal = {"publication": published, "sha256": sha256(receipt_bytes(published))}
        publish_new_file(start_seal_path(path), receipt_bytes(seal) + b"\n")
    except OSError:
        path.unlink()
        sync_directory(path.parent)
        raise


def read_receipt_file(path):
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
    with os.fdopen(fd, "rb") as stream:
        require(stat.S_ISREG(os.fstat(stream.fileno()).st_mode),
                "WAIT_EVIDENCE", "Start receipt and publication seal must be regular files")
        return stream.read()


def read_published_start(path, args):
    data = read_receipt_file(path)
    envelope = read_json(data)
    seal = read_json(read_receipt_file(start_seal_path(path)))
    publication = seal["publication"]
    published_at = publication["published_at"]
    start = envelope["receipt"]
    require(seal["sha256"] == sha256(receipt_bytes(publication))
            and publication["receipt_sha256"] == sha256(data)
            and envelope["sha256"] == sha256(receipt_bytes(start))
            and start["schema"] == START_SCHEMA and start["state"] == "PUBLISHED"
            and start["decision"] in PASS and start["span"] == args.span
            and start["output"] == str(args.output) and start["issue_sha"] == args.issue_sha
            and number(published_at) and number(start["t0"]) and published_at >= start["t0"],
            "WAIT_EVIDENCE", "missing or unverifiable published Start receipt")
    return start, published_at


def check_run_observation_times(obs, start, published_at, read_at):
    sampled = obs["observed_epoch_s"]
    require(start["host"] == obs["host"] and number(sampled) and published_at < sampled <= read_at,
            "WAIT_EVIDENCE", "Run evidence must be sampled after published Start and before being read")
    fields = RUN_OBSERVATIONS + (("watcher",) if obs.get("watcher") is not None else ())
    for field in fields:
        observation = obs.get(field)
        require(isinstance(observation, dict) and number(observation.get("sampled_at")),
                "WAIT_EVIDENCE", f"{field} is missing its Run sample", failed_read=True)
        require(sampled <= observation["sampled_at"] <= read_at,
                "WAIT_EVIDENCE", f"{field} must have a sample after published Start and before being read")


def run_expiries(item, issue, queue, obs):
    yield "queue", datetime.fromisoformat(queue["expires_at"]).timestamp(), "NEED_FRESH_QUEUE"
    yield "admission", obs["valid_through_epoch_s"], "WAIT_EVIDENCE"
    for label, obj in (("item", item), ("issue", issue)):
        if obj["expires_epoch_s"] is not None:
            yield label, obj["expires_epoch_s"], "WAIT_BINDING"
    watcher = obs.get("watcher")
    if watcher is not None:
        require(record(watcher), "WAIT_EVIDENCE", "unverified watcher admission evidence")
        yield "watcher", watcher["expires_epoch_s"], "WAIT_EVIDENCE"


def check_run_expiries(item, issue, queue, obs, now, latest_start=None):
    queue_entry(item, queue, now)
    for label, expiry, status in run_expiries(item, issue, queue, obs):
        require(number(expiry) and expiry - now >= LAUNCH_MARGIN_S
                and (latest_start is None or latest_start < expiry),
                status, f"{label} expiry leaves insufficient launch margin")


def check_guard_band(boundaries, now, *, since=None, through=None):
    first = now if since is None else since
    last = now + CLOCK_GUARD_S if through is None else max(now + CLOCK_GUARD_S, through)
    upcoming = min((edge for edge in boundaries if first < edge <= last), default=None)
    if upcoming is not None:
        boundary = datetime.fromtimestamp(upcoming, ZONE).isoformat()
        raise Refusal("WAIT_EVIDENCE", f"launch guard at {boundary}: {boundaries[upcoming]}", cause="clock guard")


def add_start_windows(boundaries, windows, first, last, label):
    require(isinstance(windows, list), "WAIT_EVIDENCE", f"missing start windows for {label}")
    for lo, hi in windows:
        require(type(lo) is int and type(hi) is int and first <= lo <= hi <= last,
                "WAIT_EVIDENCE", f"invalid dated start window for {label}")
        boundaries.update({lo - 1: label, lo: label, hi: label, hi + 1: label})


def run_boundaries(item, issue, queue, obs, now):
    from joulewise.cadence import legs
    from scripts import align_r1_rehearsal as r1

    day = local_date(now)
    first, end = midnight(day), midnight(day + timedelta(days=1))
    boundaries = {first: "local midnight", end: "local midnight"}
    for row in queue["spans"]:
        if row["span_id"] == item["span"]:
            boundaries[queue_start(row)] = "queue opening"
    lag = obs["timing"]["runner_start_max_s"]
    require(number(lag) and lag >= 0, "WAIT_EVIDENCE", "invalid startup bound")
    for label, expiry, status in run_expiries(item, issue, queue, obs):
        require(number(expiry), status, f"invalid {label} expiry")
        boundaries[expiry] = f"{label} expiry"
        runway = expiry - LAUNCH_MARGIN_S
        boundaries[runway] = f"{label} launch runway"
        if lag:
            boundaries[math.nextafter(runway, math.inf)] = f"{label} launch runway"
            boundaries[expiry - lag] = f"{label} latest startup anchor"
    for label, epoch in (("issue time", issue["issued_epoch_s"]),
                         ("observation time", obs["observed_epoch_s"])):
        require(number(epoch), "WAIT_EVIDENCE", f"invalid {label}")
        boundaries[epoch] = label
    if not (copy_verified(obs["copy"]) and obs["copy"]["transfer_stopped"] is True):
        boundaries[obs["latest_close"]["ended_epoch_s"] + COPY_WAIT_S] = "copy debt threshold"
    arguments = [legs.parse_window(arg) for arg in ARGUMENTS]
    add_window_boundaries(boundaries, now, [*arguments, r1.OS_BATCH_WINDOW_LOCAL], "batch window")
    work = item["worst_case_s"]
    add_window_boundaries(boundaries, now, arguments, "pin plan", duration=work)
    add_window_boundaries(boundaries, now, arguments, "runner handoff", duration=work + lag)

    for entry in obs["priority"]["entries"]:
        if entry["rung"] in HIGHER:
            windows = entry["start_windows"]
            add_start_windows(boundaries, windows, first, end - 1, entry["rung"])
            require(entry.get("basis") != "spent-for-date" or windows == [],
                    "WAIT_EVIDENCE", "spent rank 1 cannot have another eligible start")
    calendar = obs["calendar"]
    for row in calendar["starts"]:
        start_day = date.fromisoformat(row["date"])
        add_start_windows(boundaries, row["windows"], midnight(start_day),
                          midnight(start_day + timedelta(days=1)) - 1, row["span"])
    for span, latest in dated_limits(calendar):
        if latest is not None:
            cutoff = latest - item["deadline_s"] - calendar["post_fence_transfer_s"]
            boundaries[cutoff] = f"last HP start preserving {span}"
            boundaries[cutoff - lag] = f"last HP startup preserving {span}"
    return boundaries


def check_run_rank_clock(priority, now):
    require(priority["date"] == local_date(now).isoformat() == local_date(priority["sampled_at"]).isoformat(),
            "WAIT_EVIDENCE", "rank clock needs this date's census")
    for entry in priority["entries"]:
        if entry["rung"] in HIGHER:
            windows = entry["start_windows"]
            sampled = priority["sampled_at"]
            current = any(lo <= now < hi + 1 for lo, hi in windows)
            original = any(lo <= sampled < hi + 1 for lo, hi in windows)
            require(current == original == (entry["status"] == "eligible"), "WAIT_EVIDENCE",
                    f"{entry['rung']} eligibility changed; refresh the census")


def run_decision(args, item, issue, obs, queue_bytes, now):
    queue = read_json(queue_bytes)
    boundaries = run_boundaries(item, issue, queue, obs, now)
    check_guard_band(boundaries, now)
    tagged("expiry", check_run_expiries, item, issue, queue, obs, now)
    tagged("priority", check_run_rank_clock, obs["priority"], now)
    result = decide(item, issue, obs, "Run", now, args.kit, queue_bytes, boundaries=boundaries, raise_refusal=True)
    tagged("calendar", check_dated, obs["calendar"], now + obs["timing"]["runner_start_max_s"], result["fence_s"])
    return result, queue, boundaries


def check_claims(item, claim, *, owned=False):
    if not owned:
        require(not os.path.lexists(claim), "SKIP_SPENT", "roster already has a launch claim")
    require(not any(os.path.lexists(claim.with_name(f"{KIT_SHA}-{span}-a1.json"))
                    for span in ROSTERS if span > item["span"]),
            "WAIT_EVIDENCE", "a later HP roster has a launch claim")


def result_record(args, decision, obs):
    return {**decision, "span": args.span, "output": str(args.output), "issue_sha": args.issue_sha,
            "host": obs["host"], "observed_epoch_s": obs["observed_epoch_s"], "observation": obs["record"]}


def check_automatic(mode):
    require(automatic(mode), "HOLD_HOST", f"AC powermode is not Automatic (observed {mode!r})")


def check_observation_sections(obs):
    for field in RUN_OBSERVATIONS:
        require(isinstance(obs.get(field), dict), "WAIT_EVIDENCE",
                f"{field} operational evidence is absent", failed_read=True)


def failure(source, ex, obs):
    proof = obs.get(source) if isinstance(obs, dict) else None
    if source == "history" and isinstance(proof, dict) and isinstance(ex, Refusal) and ex.decision == "HOLD_KIT":
        proof = proof.get("prior_check")
    if not isinstance(proof, dict):
        proof = {"source": source, "detail": str(ex)}
    return source, ex, proof, None


class GateInvocation:
    """Bind the current phase and apply machine events to the two custody scopes."""

    def __init__(self, args, item, ledger):
        self.args, self.item, self.ledger = args, item, ledger
        self.phase = args.phase
        self.claim = ledger / f"{KIT_SHA}-{item['span']}-a1.json"
        self.started = ledger / f"start-{args.issue_sha}.v4.json"
        self.admission = ledger / "admission-state.json"
        self.issue_holds = None
        self.queue_root = getattr(args, "queue_hold_root", QUEUE_HOLD_ROOT)
        self.queue_holds = HoldJournal(ledger, item, queue_root=self.queue_root)
        self.queue_holds.phase = self.phase
        self.owns_claim = False
        self.invoked = False
        self.state = {"Issue": MACHINE["initial_state"], "Start": "issued", "Run": "start_published"}[self.phase]

    def stage(self, event, *, outcome=None):
        # These phase edges are reached only after the named predicates,
        # custody and once-only roster checks have succeeded.
        self.state, _ = transition(
            self.state, event, outcome=outcome,
            verified=("all current phase predicates pass", "open_holds empty", "roster unconsumed",
                      "phase prerequisites verified again"),
        )

    def bound_issue(self):
        try:
            data = self.args.issue.read_bytes()
            require(is_sha(self.args.issue_sha) and sha256(data) == self.args.issue_sha,
                    "WAIT_BINDING", "issue identity digest differs")
            issue = read_json(data)
            check_issue(self.item, issue, time.time(), self.args.phase, binding_only=True)
            return issue
        except READ_ERRORS as ex:
            raise HoldCustodyError("issue identity", ex) from ex

    def current_journal(self, issue):
        journal = HoldJournal(self.ledger, self.item, issue)
        journal.phase = self.phase
        pending = os.path.lexists(journal.inflight)
        if pending and not any(h.get("inflight") == journal.inflight.name for h in self.queue_holds.open.values()):
            raise HoldCustodyError("in-flight issue ledger read", RuntimeError("unfinished issue observation"),
                                   marker=journal.inflight)
        return journal

    def apply_dispositions(self, obs, now):
        rows = obs.get("hold_dispositions", [])
        require(isinstance(rows, list), "WAIT_EVIDENCE", "hold dispositions must be a list")
        # Verify the entire submission before appending any clearance.
        proposed = {self.issue_holds: [], self.queue_holds: []}
        seen = set()
        for row in rows:
            require(isinstance(row, dict) and is_sha(row.get("hold_id")) and row["hold_id"] not in seen,
                    "WAIT_EVIDENCE", "invalid or duplicate disposition hold id")
            seen.add(row["hold_id"])
            journal = self.queue_holds if "queue_sha" in row or "queue_seq" in row else self.issue_holds
            hold = journal.verified_clearance(self.args.repo, row, now)
            if hold:
                proposed[journal].append((row, hold))
        for journal, events in proposed.items():
            if not events:
                continue
            if journal.queue_scope:
                for _, hold in events:
                    marker = hold.get("inflight")
                    if isinstance(marker, str) and re.fullmatch(r"reading-[0-9a-f]{64}\.json", marker):
                        # Q2 refers to this exact interrupted observation.
                        # Keep its marker until authenticated recovery.
                        (self.ledger / marker).unlink(missing_ok=True)
                        sync_directory(self.ledger)
                transition("queue_position_held", "typed_disposition", verified=(
                    "name queue-position hold ID and canonical source digest", "verified later ledger sequence",
                    "reevaluate all ordinary predicates"))
            else:
                event = "typed_clear_all" if len(events) == len(journal.open) else "typed_partial_clear"
                transition("held", event, verified=("valid dispositions for exact issue, IDs and source digests",
                                                    "independent blockers still apply", "one or more unresolved hold IDs"))
            journal.append(now, clears=[row for row, _ in events])
        return any(proposed.values())

    def apply_corrections(self, obs, now):
        rows = obs.get("attestation_corrections", [])
        require(isinstance(rows, list), "WAIT_EVIDENCE", "attestation corrections must be a list")
        if not rows:
            return False
        state = read_json(self.admission.read_bytes())
        attestation = state["look_execution"]
        require(attestation is not None and len(rows) == 1, "WAIT_EVIDENCE", "no unique execution to correct")
        row = rows[0]
        require(isinstance(row, dict) and row.get("schema") == "hp-02.attestation-correction.v1"
                and row.get("action") == "ATTESTATION-CORRECTION" and row.get("look_id") == "lm-hp-01"
                and row.get("original_source_digest") == source_digest(attestation)
                and isinstance(row.get("authority"), dict) and row["authority"].get("role") == "lead"
                and type(row.get("ledger_sequence")) is int
                and row["ledger_sequence"] > state.get("execution_ledger_sequence", 1)
                and isinstance(row.get("evidence"), dict) and is_text(row["evidence"].get("record"))
                and is_sha(row["evidence"].get("sha256")),
                "WAIT_EVIDENCE", "attestation correction does not bind the original execution and evidence")
        verify_authority(self.args.repo, row, "hp-02-attestation-correction", now)
        transition("execution_attested", "verified_attestation_correction", verified=(
            "published lead RUN_STATE with evidence of mistake and original digest",
            "other holds, claim and current evidence still bind"))
        self.issue_holds.append(now, corrections=[row])
        state["look_execution"] = None
        write_admission_state(self.admission, receipt_bytes(state) + b"\n")
        return True

    def require_clear(self):
        if self.queue_holds.open:
            transition("queue_position_held", "retry", verified=("same admitted queue SHA and sequence",))
            self.queue_holds.require_clear()
        if self.issue_holds.open:
            transition("held", "retry", verified=("one or more unresolved hold IDs",))
            self.issue_holds.require_clear()

    def read_records(self, issue):
        args = self.args
        queue = tagged("bound sources", assert_source_bindings, args, self.item)
        require(args.queue.read_bytes() == queue, "WAIT_BINDING", "staged queue changed during the arm check")
        if args.phase == "Run":
            try:
                start, published_at = tagged("Start receipt", read_published_start, self.started, args)
            except READ_ERRORS as ex:
                # A held Start that never published cannot create a second
                # failure solely because Run correctly refused its absence.
                if not os.path.lexists(self.started):
                    self.require_clear()
                if isinstance(ex, Refusal):
                    ex.failed_read = True
                raise
        read_at = time.time()
        data = tagged("observation", args.observation.read_bytes)
        obs = tagged("observation", read_json, data)
        if args.phase == "Run":
            try:
                tagged("observation", check_run_observation_times, obs, start, published_at, read_at)
            except Refusal as ex:
                # A replay outside the Start publication interval is not new
                # evidence for an already-held phase. Missing data remains a
                # failed read and is recorded independently.
                if not ex.failed_read:
                    self.require_clear()
                raise
        require(issue.get("synthetic_only") is not True and obs.get("synthetic_only") is not True,
                "WAIT_EVIDENCE", "synthetic records cannot issue or arm")
        tagged("observation", check_observation, self.item, issue, obs, args.phase, read_at, binding_only=True)
        return obs, queue, data

    def collect(self, issue, obs, now):
        for source, check in phase_checks(self.item, issue, obs, self.args.phase, now):
            try:
                check()
            except READ_ERRORS as ex:
                yield failure(source, ex, obs)

    def remember(self, obs, now, *, read_only=False):
        try:
            remember_admission(self.admission, obs, now, read_only=read_only, holds=self.issue_holds)
        except Refusal:
            raise
        except (OSError, RuntimeError, ValueError) as ex:
            raise HoldCustodyError("issue ledger admission custody", ex) from ex

    def evaluate(self, issue, obs, queue, now):
        args, item = self.args, self.item
        tagged("observation", check_observation_sections, obs)
        if args.phase == "Run":
            return run_decision(args, item, issue, obs, queue, now)
        decision = decide(item, issue, obs, args.phase, now, args.kit, queue,
                          resample=time.time, raise_refusal=True)
        return decision, read_json(queue), None

    def assess(self, *, final=False):
        args, item = self.args, self.item
        issue = self.bound_issue()
        approved_journal = self.issue_holds
        journal = self.current_journal(issue)
        if final and (journal.scope != approved_journal.scope or journal.tail != approved_journal.tail):
            raise HoldCustodyError("issue ledger final read", RuntimeError("issue custody changed after claim"))
        self.issue_holds = journal
        previously_held = bool(journal.open or self.queue_holds.open)
        marker = not final and not os.path.lexists(journal.inflight)
        if marker:
            journal.begin_read()
        obs = None
        error = None
        additional = []
        try:
            obs, queue, data = self.read_records(issue)
            now = time.time()
            try:
                decision, bound_queue, boundaries = self.evaluate(issue, obs, queue, now)
            except READ_ERRORS as ex:
                error = ex
                additional = list(self.collect(issue, obs, now))
            if error is None:
                tagged("roster claim", check_claims, item, self.claim, owned=final)
        except READ_ERRORS as ex:
            error = ex
        now = time.time()
        if error is not None and not isinstance(error, OpenHold):
            source = getattr(error, "source", "phase evidence")
            # The assessment may fail before the separate evidence checks,
            # or report the same fault. Preserve independently sourced facts.
            if not any(type(ex) is type(error) and str(ex) == str(error) for _, ex, _, _ in additional):
                additional.insert(0, failure(source, error, obs))
        recorded = journal.observe(now, additional, obs=obs, initialize=not final)
        if marker:
            journal.finish_read()
        sticky = any(isinstance(ex, Refusal) and (
            OUTCOMES[ex.decision].get("execution_recovery") or ex.decision == "HALT_AND_PAGE"
            or ex.decision == "SKIP_SPENT" and source == "history")
            for source, ex, _, _ in additional)
        if obs is not None and not final:
            try:
                reassess = self.apply_dispositions(obs, now)
                reassess = self.apply_corrections(obs, now) or reassess
            except HoldCustodyError:
                raise
            except READ_ERRORS as ex:
                if sticky:
                    try:
                        self.remember(obs, now)
                    except Refusal:
                        pass
                if self.queue_holds.open:
                    transition("queue_position_held", "invalid_disposition",
                               verified=("same admitted queue SHA and sequence",))
                elif self.issue_holds.open:
                    transition("held", "wrong_authority", verified=("one or more unresolved hold IDs",))
                ex.assessed = True
                raise
            if reassess and error is None and not (journal.open or self.queue_holds.open):
                self.state, _ = transition("reassess", f"{args.phase}.retry",
                                           verified=("phase prerequisites verified again",))
                try:
                    decision, bound_queue, boundaries = self.evaluate(issue, obs, queue, time.time())
                    tagged("roster claim", check_claims, item, self.claim)
                except READ_ERRORS as ex:
                    raise self.record_refusal(getattr(ex, "source", "phase evidence"), ex, obs)

        still_held = bool(journal.open or self.queue_holds.open)
        remember_read = not previously_held or not still_held or sticky
        if obs is not None and remember_read and (not final or error is not None or recorded):
            try:
                self.remember(obs, now)
            except Refusal as ex:
                # The historical execution, spent and halt bars survive
                # an otherwise clean observation and ordinary disposition.
                if error is None:
                    error = ex
            except (KeyError, TypeError, AttributeError):
                if error is None:
                    raise
        if error is not None:
            raise self.assessed_error(error)
        self.require_clear()
        if final and recorded:
            raise self.record_refusal("final evidence", Refusal("WAIT_EVIDENCE", "final read added custody facts"), obs)
        return decision, bound_queue, boundaries, obs, data

    def assessed_error(self, error):
        if not isinstance(error, Refusal) or error.failed_read:
            error = Refusal(OUTCOMES["READ_ERROR"]["normalize"], str(error))
        error.assessed = True
        return error

    def record_refusal(self, source, error, obs=None):
        self.issue_holds.observe(time.time(), [failure(source, error, obs)])
        return self.assessed_error(error)

    def live(self, obs):
        from joulewise.align.apple.powermode import observe_ac_powermode

        for source, check in (
            ("agent census", lambda: check_agent_census(obs, self.args.magistrate_pid)),
            ("host fence", lambda: runtime_files(self.args, self.item)),
            ("AC powermode", lambda: check_automatic(observe_ac_powermode())),
        ):
            try:
                check()
            except READ_ERRORS as ex:
                raise self.record_refusal(source, ex, obs)

    def dispatch(self, initial, approved):
        args, item = self.args, self.item
        self.phase = "FinalRun"
        approved_queue_tail = self.queue_holds.tail
        self.queue_holds = HoldJournal(self.ledger, item, queue_root=self.queue_root)
        self.queue_holds.phase = self.phase
        if self.queue_holds.tail != approved_queue_tail:
            self.queue_holds.require_clear()
            raise HoldCustodyError("queue ledger final read", RuntimeError("queue custody changed after claim"))
        require(item in read_json((HP / "items.json").read_bytes()),
                "WAIT_BINDING", "item changed during the claim write")
        fresh, queue, boundaries, obs, actual = self.assess(final=True)
        require(actual == approved, "WAIT_EVIDENCE", "Run observation changed during the claim write")
        require(read_json(self.claim.read_bytes()) == result_record(args, initial, obs),
                "WAIT_EVIDENCE", "durable claim changed before dispatch")
        require(fresh["argument"] == initial["argument"], "WAIT_EVIDENCE", "claim argument needs a fresh decision")
        read_at = time.time()
        self.remember(obs, read_at, read_only=True)
        argv = [
            sys.executable, "-B", "scripts/launch_cadence_span.py", "launch",
            "--repo", str(args.repo), "--python-bin", sys.executable, "--kit", str(args.kit),
            "--legs", ",".join(item["legs"]), "--batch-window", initial["argument"],
            "--output", str(args.output), "--disk-path", str(args.repo), "--custody-root", str(args.custody),
            "--magistrate-pid", str(args.magistrate_pid), "--deadline", str(initial["deadline"]),
            "--exit-wait-seconds", "180", "--start-wait-seconds", "30",
        ]
        self.live(obs)
        dispatch = time.time()
        latest_start = initial["t0"] + obs["timing"]["runner_start_max_s"]
        boundaries[initial["deadline"] - fresh["minimum_s"]] = "launcher deadline fit"
        try:
            check_guard_band(boundaries, dispatch, since=initial["t0"])
            issue = self.issue
            check_run_expiries(item, issue, queue, obs, dispatch, latest_start)
            check_guard_band(boundaries, dispatch, since=initial["t0"], through=latest_start)
            require(initial["t0"] <= read_at <= dispatch <= latest_start
                    and local_date(dispatch) == local_date(initial["t0"]),
                    "WAIT_EVIDENCE", "handoff window or date elapsed; make a fresh Run decision")
            check_dated(obs["calendar"], latest_start, fresh["fence_s"])
            require(latest_start + fresh["minimum_s"] <= initial["deadline"],
                    "WAIT_PIN", "deadline no longer fits at the launcher handoff")
        except Refusal as ex:
            raise self.record_refusal("handoff", ex, obs)
        self.stage("Run.final_reread", outcome=fresh["decision"])
        self.stage("Run.invoke", outcome=fresh["decision"])
        self.invoked = True
        try:
            rc = subprocess.call(argv, cwd=args.repo)
        except READ_ERRORS as ex:
            transition(self.state, "spent_or_uncertain_invocation", outcome="LAUNCHER_EXCEPTION")
            raise Refusal("LAUNCHER_EXCEPTION", str(ex)) from ex
        if rc:
            _, wire = transition(self.state, "spent_or_uncertain_invocation", outcome="LAUNCHER_NONZERO")
            print(json.dumps({"decision": wire, "launcher_rc": rc}), flush=True)
        else:
            print(json.dumps(initial), flush=True)
        return rc

    def execute(self):
        args, item = self.args, self.item
        if self.phase == "Issue":
            self.stage("bind_proposal")
        decision, queue, _, obs, obs_bytes = self.assess()
        if self.phase == "Run":
            self.stage("Run.verify_and_read", outcome=decision["decision"])
            self.issue = self.bound_issue()
            write_exclusive(self.claim, result_record(args, decision, obs))
            self.owns_claim = True
            self.stage("Run.pass_and_claim", outcome=decision["decision"])
            return self.dispatch(decision, obs_bytes)

        self.live(obs)
        if self.phase == "Start":
            self.stage("Start.read", outcome=decision["decision"])
            issue = self.bound_issue()
            passed = time.time()
            require(decision["t0"] <= passed <= obs["valid_through_epoch_s"]
                    and local_date(passed) == local_date(decision["t0"]),
                    "WAIT_EVIDENCE", "Start evidence expired before the verdict")
            queue_entry(item, queue, passed)
            publish_start(self.started, result_record(args, decision, obs))
            try:
                _, published_at = read_published_start(self.started, args)
                check_observation(item, issue, obs, self.phase, published_at)
                check_issue(item, issue, published_at, self.phase)
                queue_entry(item, queue, published_at)
                require(local_date(published_at) == local_date(decision["t0"]),
                        "WAIT_EVIDENCE", "Start date changed before publication")
            except READ_ERRORS:
                start_seal_path(self.started).unlink()
                self.started.unlink()
                sync_directory(self.ledger)
                raise
            self.stage("Start.pass_and_publish", outcome=decision["decision"])
        else:
            self.stage("Issue.pass", outcome=decision["decision"])
        print(json.dumps(decision), flush=True)
        return 0

    def queue_failure(self, error):
        self.queue_holds.phase = self.phase
        self.queue_holds.observe(time.time(), [(error.source, error.error, {}, error.marker)])
        self.release_unused_claim()
        raise Refusal(OUTCOMES["CUSTODY_ERROR"]["normalize"], str(error)) from error

    def release_unused_claim(self):
        if self.owns_claim and not self.invoked:
            self.claim.unlink()


def run_gate(args):
    import fcntl

    try:
        items = read_json((HP / "items.json").read_bytes())
        item = next(row for row in items if row["span"] == args.span)
        runtime_files(args, item, binding_only=True)
        require(is_sha(item["queue"]["sha256"]) and type(item["piece"]) is int and item["piece"] > 0,
                "WAIT_BINDING", "invalid admitted queue position")
        ledger = args.custody / "hp-02-arms"
        queue_root = getattr(args, "queue_hold_root", QUEUE_HOLD_ROOT)
        queue_root.mkdir(parents=True, exist_ok=True)
        # The queue lock remains available even when issue custody fails.
        lock_path = queue_root / f"{item['queue']['sha256']}-{item['piece']}.lock"
        with lock_path.open("a") as queue_lock:
            fcntl.flock(queue_lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
            gate = GateInvocation(args, item, ledger)
            try:
                ledger.mkdir(parents=True, exist_ok=True)
                lock = (ledger / "arm.lock").open("a")
            except OSError as ex:
                gate.queue_failure(HoldCustodyError("issue ledger lock", ex))
            with lock:
                fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
                sys.path.insert(0, str(args.repo))
                try:
                    try:
                        return gate.execute()
                    except HoldCustodyError:
                        raise
                    except READ_ERRORS as ex:
                        if (gate.issue_holds is not None and not gate.invoked and not isinstance(ex, OpenHold)
                                and not getattr(ex, "assessed", False)):
                            ex = gate.record_refusal(getattr(ex, "source", "phase custody"), ex)
                        gate.release_unused_claim()
                        raise ex
                except HoldCustodyError as ex:
                    gate.queue_failure(ex)
    except Refusal as ex:
        print(json.dumps({"decision": ex.decision, "detail": str(ex)}))
    except READ_ERRORS as ex:
        print(json.dumps({"decision": OUTCOMES["READ_ERROR"]["normalize"], "detail": str(ex)}))
    return 1


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    generator = sub.add_parser("render")
    generator.add_argument("--source-repo", type=Path, required=True)
    generator.add_argument("--queue-commit", required=True)
    gate = sub.add_parser("gate")
    gate.add_argument("span", choices=ROSTERS)
    gate.add_argument("phase", choices=("Issue", "Start", "Run"))
    for name in ("repo", "kit", "queue", "issue", "observation", "custody", "output"):
        gate.add_argument("--" + name, type=Path, required=True)
    gate.add_argument("--issue-sha", required=True)
    gate.add_argument("--magistrate-pid", type=int, required=True)
    args = parser.parse_args()
    if args.command == "render":
        render(args.source_repo.resolve(), args.queue_commit)
        return 0
    return run_gate(args)


if __name__ == "__main__":
    raise SystemExit(main())
