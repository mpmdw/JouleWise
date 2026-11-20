"""Render and evaluate the hp-02 successor items using operational records only."""
import argparse
from datetime import date, datetime, time as wall_time, timedelta
import hashlib
import json
import math
import os
from pathlib import Path
import re
import subprocess
import sys
import time
from zoneinfo import ZoneInfo

HERE = Path(__file__).resolve().parent
HP = HERE / "hp-02"
ZONE = ZoneInfo("America/Los_Angeles")
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
PASS = frozenset({"ELIGIBLE", "ELIGIBLE_WITH_COPY_DEBT"})
ROSTERS = {
    "hp-02-s01": ["L001", "L002", "L003"],
    "hp-02-s02": ["L004", "L005", "L006", "L007"],
    "hp-02-s03": ["L008", "L009", "L010", "L011", "L012"],
}
HIGHER = ("ready-session", "counted", "first-stability", "f2-inst-01", "f2-inst-02", "f2-inst-03")
RANK_DECISION = ("CEDE_READY", "CEDE_COUNTED", "CEDE_RANK_1", "CEDE_INST_01", "CEDE_INST_02", "CEDE_INST_03")
FEEDS = {"agents", "meter", "volumes"}
PREFLIGHT = {
    "veto_clear", "maintenance_clear", "host_health", "disk_floor", "meter_available",
    "collector_available", "clock_ok", "on_ac", "battery_float", "night_lock_free",
    "mode_rules", "measurement_mode", "network_time_off", "frequency_zero",
}
MARKER = Path("/Users/Shared/JouleWise/host-power/high-power.marker")


class Refusal(ValueError):
    def __init__(self, decision, detail):
        super().__init__(detail)
        self.decision = decision


def require(condition, decision, detail):
    if not condition:
        raise Refusal(decision, detail)


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
    return subprocess.check_output(["git", "-C", str(repo), *args], timeout=60)


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
        start = midnight(date.fromisoformat(row["not_before"]))
        require(expiry.tzinfo is not None and start < expiry.timestamp(),
                "WAIT_BINDING", "invalid queue interval")
        if span == item["span"]:
            entry = row
            require(start <= now < expiry.timestamp(), "NEED_FRESH_QUEUE", "outside the finite queue interval")
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


def check_issue(item, issue, now, phase):
    auth = item["authority"]
    line2_ok = "yes" if issue.get("line_2") == auth["line_2"] else "no"
    require(
        record(issue) and issue["schema"] == "hp-02.issue.v1"
        and issue["status"] == ("PROPOSED" if phase == "Issue" else "ISSUED")
        and issue["binding"] == issue_binding(item) and issue["expires_epoch_s"] is None
        and number(issue["issued_epoch_s"]) and issue["issued_epoch_s"] <= now
        and number(issue["check_deadline_epoch_s"])
        and is_text(issue["check_target"]) and is_text(issue["latest_close_at_issue"])
        and issue["spec_sha256"] == auth["spec_sha256"]
        and issue["occupancy_sha256"] == auth["occupancy_sha256"]
        and issue["inherited_smoke"] == auth["inherited_smoke"]
        and line2_ok == "yes",
        "WAIT_BINDING", "issue identity, accepted spec, inherited smoke or LINE2_OK missing",
    )


def check_look(look, now, sampled_at):
    require(
        record(look) and look["scope"] == "lm-hp-01" and look["kit_sha256"] == KIT_SHA
        and look["checked_through"] == sampled_at and look["checked_through"] <= now
        and look["execution_register_checked"] is True and look["both_custody_roots_checked"] is True
        and look["all_execution_routes_covered"] is True,
        "WAIT_EVIDENCE", "current scoped look evidence required",
    )
    require(look["status"] != "ran", "NOT_ADMITTED", "lm-hp-01 already started")
    require(look["status"] == "not_run" and look["pending_conflict"] is False, "WAIT_EVIDENCE", "look unresolved")


def check_history(item, obs):
    history = obs["history"]
    require(record(history) and history["complete"] is True and history["kit_sha256"] == KIT_SHA,
            "WAIT_EVIDENCE", "complete per-leg execution history required")
    states = history["legs"]
    current = [states.get(leg) for leg in item["legs"]]
    require(not any(state == "spent" for state in current), "SKIP_SPENT", "roster already started")
    require(all(state == "unrun" for state in current), "WAIT_EVIDENCE", "ambiguous unrun roster")
    previous = item["predecessor"]
    if previous is not None:
        prior = history["prior_check"]
        require(record(prior) and prior["span"] == previous and prior["kit_sha256"] == KIT_SHA
                and prior["attempt"] == 1 and prior["legs"] == ROSTERS[previous]
                and number(prior["ended_epoch_s"]) and prior["ended_epoch_s"] <= obs["observed_epoch_s"],
                "WAIT_EVIDENCE", "exact prior HP Check required")
        require(prior["status"] != "dirty", "HOLD_KIT", "prior HP Check dirty")
        require(prior["status"] == "clean" and is_sha(prior["receipt_sha256"])
                and prior["fence_gone"] is True and prior["restore_proven"] is True
                and all(states.get(leg) == "spent" for span, roster in ROSTERS.items()
                        if span < item["span"] for leg in roster),
                "WAIT_EVIDENCE", "prior HP Check/roster unresolved")


def check_close(close, obs, now):
    require(record(close) and close["identity"] == "latest-unambiguous" and close["host"] == obs["host"]
            and is_sha(close["receipt_sha256"])
            and number(close["ended_epoch_s"]) and close["ended_epoch_s"] <= now,
            "WAIT_EVIDENCE", "latest identified Check required")
    recovery = close.get("recovery")
    if close.get("restore_status") == "unproven":
        require(record(recovery) and recovery.get("safe_route_proven") is True
                and recovery.get("same_close") == close["record"],
                "HOLD_HOST", "restore unproven; use the safe pinned recovery route")
        if recovery.get("result") == "failed":
            raise Refusal("HALT_AND_PAGE", "pinned recovery failed; halt host and page Ed and lead")
        require(recovery.get("result") == "proven", "HOLD_HOST", "restore unproven after deferred recovery")
        residual = recovery.get("residual_refusal")
        require(residual != "open", "HOLD_KIT", "restore proven; separate refusal open")
        require(residual == "clear", "WAIT_EVIDENCE", "post-recovery stop status unknown")
    require(close["fence_gone"] is True, "WAIT_FENCE", "shared fence clearance unproven")
    require(
        close["receipt_ok"] is True and close["restores_read_back"] is True
        and close["restore_status"] in ("proven", "unproven") and close["ac_powermode"] == 0
        and close["marker_present_or_link"] is False and close["host_lock_free"] is True,
        "HOLD_HOST", "latest close restore/readbacks incomplete",
    )
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


def check_safety(obs, close):
    safety = obs["safety"]
    require(
        record(safety) and safety["close_record"] == close["record"]
        and safety["close_sha256"] == close["receipt_sha256"] and safety["host"] == obs["host"] and safety["ac_powermode"] == 0
        and safety["marker_present_or_link"] is False
        and safety["foreign_agent_census_casefold"] == [] and safety["foreign_process_census"] == []
        and all(safety["preflight"].get(line) is True for line in PREFLIGHT),
        "HOLD_HOST", "current scoped restore, census or preflight failed",
    )
    verify = safety["mode_verify"]
    require(record(verify) and (verify["rc"] == 0 and verify["exceptions"] == []
            or verify["rc"] == 1 and verify["exceptions"] == ["own-agent-tree-or-permitted-jobs"]),
            "HOLD_HOST", "measurement mode verify failed beyond the documented exception")
    stops = obs["stops"]
    require(record(stops) and stops["complete"] is True, "WAIT_EVIDENCE", "scoped stop register required")
    names = stops["open"]
    require(isinstance(names, list), "WAIT_EVIDENCE", "invalid stop register")
    for stop in names:
        code = stop["code"]
        require(code not in {"RESTORE_UNPROVEN", "UNOWNED_MARKER", "DISK_FLOOR", "HOST_STATE"}
                and stop["scope"] != "host", "HOLD_HOST", f"host-wide stop {code}")
        require(stop["scope"] not in ("measured", "hp-02", obs["binding"]["span"]),
                "HOLD_KIT", f"applicable stop {code}")
        require(stop["scope"] in ("counted", "v4", "other-kit"), "WAIT_EVIDENCE", "unresolved stop scope")


def check_copy(copy, close, now):
    require(record(copy) and copy["predecessor"] == close["record"], "WAIT_COPY", "unbound copy evidence")
    stopped = copy["transfer_stopped"] is True
    verified = (
        copy.get("status") == "verified" and is_sha(copy.get("plaintext_manifest_sha256"))
        and is_sha(copy.get("ciphertext_sha256")) and type(copy.get("ciphertext_size_bytes")) is int
        and copy["ciphertext_size_bytes"] > 0 and is_text(copy.get("provider_verification"))
    )
    if verified and stopped:
        return False
    require(now - close["ended_epoch_s"] >= 600, "WAIT_COPY", "waiting within the copy interval")
    require(stopped, "HOLD_FOREIGN_LOAD", "transfer has not stopped")
    require(is_text(copy.get("debt_record")), "WAIT_COPY", "copy debt is unrecorded")
    return True


def check_rank(priority, day):
    require(record(priority) and priority["complete"] is True and priority["date"] == day.isoformat()
            and priority["r1_post_close"] is True, "WAIT_EVIDENCE", "current complete ladder required")
    by_rung = {}
    for entry in priority["entries"]:
        require(entry["rung"] in (*HIGHER, "further-stability") and record(entry)
                and entry["status"] in ("eligible", "unavailable"),
                "WAIT_EVIDENCE", "unknown ladder entry eligibility")
        rung = entry["rung"]
        require(rung not in by_rung, "WAIT_EVIDENCE", "ambiguous ladder rung")
        by_rung[rung] = entry
        if rung == "first-stability" and entry["status"] == "eligible":
            require(re.fullmatch(r"f2-stab-(0[1-9]|1[0-4])", entry["entry_id"]) is not None,
                    "WAIT_EVIDENCE", "invalid first-stability kit")
    require(set(by_rung) == {*HIGHER, "further-stability"}, "WAIT_EVIDENCE", "incomplete ladder")
    for rung, decision in zip(HIGHER, RANK_DECISION):
        require(by_rung[rung]["status"] != "eligible", decision, by_rung[rung]["record"])
    return by_rung["further-stability"]["status"] == "eligible"


def check_dated(calendar, now, fence_s):
    require(record(calendar) and calendar["complete"] is True, "WAIT_EVIDENCE", "complete dated starts required")
    transfer = calendar["post_fence_transfer_s"]
    require(number(transfer) and 0 <= transfer <= 600, "WAIT_EVIDENCE", "unbounded post-fence transition")
    earliest = math.ceil(now + fence_s + transfer)
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
        require(choices and max(choices) >= earliest, "CEDE_DATED", f"would block counted start {row['span']}")
        latest_start = max(choices)


def occupancy(item, kit_path, now, timing, arguments=ARGUMENTS, planner=None):
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
                continue
            raise Refusal("WAIT_PIN", str(err)) from err
        except ValueError as err:
            raise Refusal("WAIT_PIN", str(err)) from err
        break
    else:
        raise Refusal("WAIT_PIN", "both explicit plans meet a batch blackout")

    work = item["worst_case_s"]
    fence = item["deadline_s"]
    require(plan["worst_case_s"] == work and plan["expected_s"] == item["expected_s"]
            and plan["blackout_clear"] is True and plan["batch_windows"] == [arg]
            and [leg["leg_id"] for leg in plan["legs"]] == item["legs"]
            and launcher.cadence_minimum_seconds(plan) <= fence,
            "WAIT_PIN", "pin plan, roster or deadline mismatch")
    require(record(timing), "WAIT_EVIDENCE", "no demonstrated timing bound")
    keys = ("runner_start_max_s", "selector_sample_max_s", "soak_dispatch_max_s", "inner_soak_gate_max_s",
            "pre_leg_max_s", "leg_wait_overshoot_max_s", "post_last_cap_max_s",
            "restore_and_close_max_s", "outer_clear_max_s")
    require(all(number(timing.get(k)) and timing[k] >= 0 for k in keys),
            "WAIT_EVIDENCE", "missing or unbounded timing component")

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
    soak_wait = legs.interval_delay(after_setup, soak_s, [arg_window, r1.OS_BATCH_WINDOW_LOCAL])
    end = after_setup + soak_wait + dispatch + soak_s
    leg_wait = 0
    for _ in range(attempts):
        end += timing["pre_leg_max_s"]
        wait = legs.leg_start_delay(end, [arg_window])
        end += wait + timing["leg_wait_overshoot_max_s"] + plan["leg_cap_s"]
        leg_wait += wait
    work_end = end - now + timing["post_last_cap_max_s"]
    close_end = work_end + timing["restore_and_close_max_s"]
    through_clearance = close_end + timing["outer_clear_max_s"]
    require(work_end <= cut and close_end <= close_cut and through_clearance <= fence,
            "CEDE_FENCE", f"composed clearance at +{through_clearance:g}s; fence +{fence}s")
    return {
        "argument": arg, "t0": now, "deadline": now + fence, "work_s": work_end,
        "soak_wait_s": soak_wait, "leg_wait_s": leg_wait, "close_s": close_end,
        "through_clearance_s": through_clearance, "fence_s": fence,
    }


def decide(item, issue, obs, phase, now, kit_path, queue_bytes, *, planner=None):
    """One fail-closed decision shared by Issue, Start and Run."""
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
        require(record(obs) and obs["schema"] == "hp-02.observation.v1" and obs["phase"] == phase
                and is_text(obs["host"]) and obs["binding"] == issue_binding(item)
                and obs["issue_record"] == issue["record"]
                and number(obs["observed_epoch_s"]) and number(obs["valid_through_epoch_s"])
                and obs["observed_epoch_s"] <= now <= obs["valid_through_epoch_s"]
                and obs["observed_epoch_s"] >= issue["issued_epoch_s"],
                "WAIT_EVIDENCE", "fresh phase- and issue-bound operational observation required")
        if obs.get("fence_clear") is not True:
            raise Refusal("WAIT_FENCE", "shared fence still live or status unknown")
        close = obs["latest_close"]
        check_close(close, obs, now)
        if phase == "Issue":
            require(close["record"] == issue["latest_close_at_issue"], "WAIT_EVIDENCE", "issue close mismatch")
        check_safety(obs, close)
        further = check_rank(obs["priority"], local_date(now))
        try:
            check_look(obs["look"], now, obs["observed_epoch_s"])
        except Refusal as ex:
            if ex.decision == "NOT_ADMITTED" and further:
                return {"decision": "SELECT_RANK_4", "detail": str(ex)}
            raise
        census = obs["hp01_dates"]
        require(record(census) and census["complete"] is True and census["kit_sha256"] == HP01_SHA,
                "WAIT_EVIDENCE", "complete hp-01 date census required")
        dates = {date.fromisoformat(day) for day in census["t0_dates"]}
        require(local_date(now) not in dates, "INELIGIBLE_DATE", "hp-01 leg on this t0-date")
        check_history(item, obs)
        debt = check_copy(obs["copy"], close, now)
        timing = occupancy(item, kit_path, now, obs.get("timing"), planner=planner)
        check_dated(obs["calendar"], now, timing["fence_s"])
        return {"decision": "ELIGIBLE_WITH_COPY_DEBT" if debt else "ELIGIBLE", **timing}
    except Refusal as ex:
        return {"decision": ex.decision, "detail": str(ex)}
    except (KeyError, ValueError, OSError, TypeError, AttributeError, OverflowError) as ex:
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
assert proof['proven'] is True and proof['ac_powermode']==0 and proof['host_marker_present'] is False
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

**Run.** Refresh the records, native census, marker, fence and clock after Start. Invoke the same gate with the Run observation immediately before launch. The gate verifies the successful Start and atomically claims the roster once. The claim records the exact argument, t0 and deadline. On bootstrap refusal hold this attempt for the lead. Exit the session as soon as the launcher reports a claimed fence.

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


def runtime_files(args, item):
    require(args.custody == Path("/Users/edr/night-custody/magistrate"),
            "HOLD_HOST", "use the shared host fence and roster ledger")
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
    with path.open("x", encoding="utf-8") as stream:
        json.dump(data, stream)
        stream.write("\n")
        stream.flush()
        os.fsync(stream.fileno())


def run_gate(args):
    # The pure fixture entry is decide(); this command is reserved for the
    # authorized desk. Do not invoke it as a builder or with synthetic data.
    import fcntl

    try:
        items = read_json((HP / "items.json").read_bytes())
        item = next(row for row in items if row["span"] == args.span)
        queue = assert_source_bindings(args, item)
        sys.path.insert(0, str(args.repo))
        runtime_files(args, item)
        issue_bytes = args.issue.read_bytes()
        require(sha256(issue_bytes) == args.issue_sha, "WAIT_BINDING", "issue bytes differ")
        issue = read_json(issue_bytes)
        obs = read_json(args.observation.read_bytes())
        require(issue.get("synthetic_only") is not True and obs.get("synthetic_only") is not True,
                "WAIT_EVIDENCE", "synthetic records cannot issue or arm")
        from joulewise.align.apple.powermode import observe_ac_powermode
        require(observe_ac_powermode() == 0, "HOLD_HOST", "AC powermode is not Automatic")
        check_agent_census(obs, args.magistrate_pid)
        args.custody.mkdir(parents=True, exist_ok=True)
        ledger = args.custody / "hp-02-arms"
        ledger.mkdir(exist_ok=True)
        # Use stable identities independent of queue renewal or output naming.
        claim = ledger / f"{KIT_SHA}-{item['span']}-a1.json"
        started = ledger / f"start-{args.issue_sha}.json"
        with (ledger / "arm.lock").open("a") as lock:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
            runtime_files(args, item)
            require(not os.path.lexists(claim), "SKIP_SPENT", "roster already has a launch claim")
            if args.phase == "Run":
                start = read_json(started.read_bytes())
                require(start["output"] == str(args.output) and start["issue_sha"] == args.issue_sha
                        and obs["observed_epoch_s"] > start["observed_epoch_s"],
                        "WAIT_EVIDENCE", "Run requires a successful Start and a fresh observation")
            current_queue = args.queue.read_bytes()
            require(current_queue == queue, "WAIT_BINDING", "staged queue changed during the arm check")
            decision = decide(item, issue, obs, args.phase, time.time(), args.kit, current_queue)
            print(json.dumps(decision), flush=True)
            if decision["decision"] not in PASS:
                return 1
            result = {**decision, "span": item["span"], "output": str(args.output), "issue_sha": args.issue_sha,
                      "observed_epoch_s": obs["observed_epoch_s"], "observation": obs["record"]}
            if args.phase == "Start":
                write_exclusive(started, result)
            if args.phase == "Run":
                runtime_files(args, item)
                require(args.queue.read_bytes() == queue and sha256(args.kit.read_bytes()) == KIT_SHA,
                        "WAIT_BINDING", "staged queue or kit changed after Run decision")
                require(time.time() <= decision["t0"] + obs["timing"]["runner_start_max_s"],
                        "WAIT_EVIDENCE", "handoff window elapsed; make a fresh Run decision")
                write_exclusive(claim, result)
                return subprocess.call([
                    sys.executable, "-B", "scripts/launch_cadence_span.py", "launch",
                    "--repo", str(args.repo), "--python-bin", sys.executable, "--kit", str(args.kit),
                    "--legs", ",".join(item["legs"]), "--batch-window", decision["argument"],
                    "--output", str(args.output), "--disk-path", str(args.repo), "--custody-root", str(args.custody),
                    "--magistrate-pid", str(args.magistrate_pid), "--deadline", str(decision["deadline"]),
                    "--exit-wait-seconds", "180", "--start-wait-seconds", "30",
                ], cwd=args.repo)
        return 0
    except Refusal as ex:
        print(json.dumps({"decision": ex.decision, "detail": str(ex)}))
    except (OSError, ValueError, TypeError, KeyError, StopIteration, subprocess.SubprocessError) as ex:
        print(json.dumps({"decision": "WAIT_EVIDENCE", "detail": str(ex)}))
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
