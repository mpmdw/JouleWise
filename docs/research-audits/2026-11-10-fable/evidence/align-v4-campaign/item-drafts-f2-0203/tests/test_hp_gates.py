"""Translate the frozen synthetic observations into the successor record schema."""
from contextlib import contextmanager, redirect_stdout
from copy import deepcopy
import csv
import io
from datetime import datetime
from itertools import product
import json
from pathlib import Path
import sys
from tempfile import TemporaryDirectory
from types import SimpleNamespace
from unittest.mock import patch

DRAFTS = Path(__file__).resolve().parents[1]
HP = DRAFTS / "hp-02"
SEAT = Path(sys.argv[1]).resolve()
sys.path.insert(0, str(DRAFTS))
import prepare_hp_items as hp

sys.path.insert(0, str(SEAT / "tmp/pin"))
sys.path.insert(0, str(SEAT / "fixtures"))
import clocked_occupancy as freeze
import successor_regression as regression
from joulewise.cadence.legs import PlanError

DOC = json.loads((HP / "fixtures/item-cases.json").read_bytes())
BASE = DOC["base"]
ITEMS = {row["span"]: row for row in json.loads((HP / "items.json").read_bytes())}
QUEUE_A = (HP / "queue-a.json").read_bytes()


def evidence(reference, **fields):
    return {"record": reference, "by": "Synthetic issuing desk", **fields}


def unix(stamp):
    return int(datetime.fromisoformat(stamp).timestamp())


def timing(item, selector=1100):
    return evidence(
        "synthetic setup envelope", runner_start_max_s=60, selector_sample_max_s=selector,
        soak_dispatch_max_s=10, inner_soak_gate_max_s=100, pre_leg_max_s=12,
        leg_wait_overshoot_max_s=0, post_last_cap_max_s=100 - 10 - 12 * (len(item["legs"]) + 2),
        restore_and_close_max_s=180, outer_clear_max_s=190,
    )


def fixture_queue():
    queue = json.loads(QUEUE_A)
    fixture = DOC["fixture-Q2"]
    queue["queue_id"] = "cq-hp-02-q2"
    queue["expires_at"] = fixture["expires_at"]
    for row in queue["spans"]:
        row["not_before"] = fixture["not_before"]
    return json.dumps(queue).encode()


def first_stability_entry(over, day):
    stability = over.get("stability", BASE["stability"])
    if stability == "first-eligible":
        return evidence("rank-one eligible kit", rung="first-stability", status="eligible",
                        entry_id=over.get("stability_kit"), pool=over.get("first_eligible_stability_pool"))
    # The fixture's default states the first leg is done. When it names a
    # separate 15/16 filler, its explicit rank-one pool and completion facts
    # are the evidence for that day; rank four cannot supply those facts.
    separate_pool = over.get("stability_kit") in ("f2-stab-15", "f2-stab-16")
    pool = over.get("rank1_pool") if separate_pool else over.get("rank1_pool", hp.RANK1_POOL)
    done = over.get("rank1_already_done") if separate_pool else over.get("rank1_already_done", True)
    kit_id = "f2-stab-01"
    entry = evidence("rank-one daily disposition", rung="first-stability", status="unavailable",
                     entry_id=kit_id, basis="spent-for-date", pool=pool)
    if done is True:
        entry["completion"] = evidence("synthetic first leg completion", kit_id=kit_id,
                                       leg_id="L001", pin=hp.RANK1_PIN, t0_date=day.isoformat(), status="completed")
    return entry


def candidate(over, now, phase, queue=None):
    item = deepcopy(ITEMS[over.get("span", BASE["span"])])
    if queue is None:
        queue = fixture_queue() if over.get("queue") == "fixture-Q2" else QUEUE_A
    item["queue"]["sha256"] = hp.sha256(queue)
    issue = evidence(
        BASE["typed_issue"], schema="hp-02.issue.v1", status="PROPOSED" if phase == "Issue" else "ISSUED",
        binding=hp.issue_binding(item), issued_epoch_s=now - over.get("item_age_s", 1200),
        expires_epoch_s=None, check_deadline_epoch_s=now + item["deadline_s"],
        latest_close_at_issue=BASE["close_reference"]["id"], check_target="synthetic check",
        **item["authority"],
    )
    original = BASE["close_reference"]
    close = evidence(
        original["id"], identity="latest-unambiguous", host=original["host"],
        ended_epoch_s=now - over.get("wait_s", over.get("close_age_s", original["ended_seconds_before_now"])),
        receipt_sha256="a" * 64, receipt_ok=original["receipt"] == "OK", restore_status="proven", fence_gone=original["fence_gone"],
        restores_read_back=original["restores_read_back"], feeds_proven_stopped=original["feeds_proven_stopped"],
        ac_powermode=original["hp_mode_after"], marker_present_or_link=original["marker_present_or_link"],
        host_lock_free=original["host_lock_free"], groups=[
            {
                "group_id": row["synthetic_group_id"], "start_identity": row["start_identity"],
                "receipt_stop": over.get("receipt_group", row["receipt_stop"]),
                "independent_census": over.get("pgid_census", row["independent_census"]),
            } for row in original["groups"]
        ],
    )
    if "last_close_identity" in over:
        close["identity"] = over["last_close_identity"]
    if "close_restore" in over:
        close["restore_status"] = over["close_restore"]
        close["recovery"] = evidence(
            "one synthetic pinned recovery",
            result={"fails": "failed", "proven": "proven"}[over["external_recovery"]],
            residual_refusal={"still-open": "open", "unknown": "unknown"}.get(over.get("other_refusal")),
            same_close=close["record"], safe_route_proven=True,
        )
    safety = evidence(
        "current host preflight", host=original["host"], close_record=original["id"], close_sha256="a" * 64,
        mode_verify=evidence("synthetic mode verify", rc=0, exceptions=[]),
        ac_powermode=0, marker_present_or_link=bool(over.get("host_marker")),
        foreign_agent_census_casefold=[x.casefold() for x in over.get("case_insensitive_census", [])],
        foreign_process_census=original["foreign_process_census"], preflight=dict.fromkeys(hp.PREFLIGHT, True),
    )
    if "typed_restore" in over:
        restore = over["typed_restore"]
        safety["close_record"] = restore["identity"] if isinstance(restore, dict) else None
    if "typed_safety" in over:
        safety = over["typed_safety"]
    look_ref = BASE["look_reference"]
    look = evidence(
        look_ref["kind"], scope=look_ref["scope"], kit_sha256=look_ref["kit"], checked_through=now,
        execution_register_checked=True, both_custody_roots_checked=True,
        all_execution_routes_covered=look_ref["all_execution_routes_covered"],
        pending_conflict=look_ref["pending_conflict"], status=over.get("look_attestation", look_ref["status"]),
    )
    copy_ref = BASE["copy_reference"]
    copy = evidence(
        copy_ref["kind"], predecessor=copy_ref["predecessor"], status="verified",
        plaintext_manifest_sha256=copy_ref["plaintext_manifest_sha256"], ciphertext_sha256=copy_ref["ciphertext_sha256"],
        ciphertext_size_bytes=copy_ref["ciphertext_size_bytes"],
        provider_verification=copy_ref["provider_completion_and_readback"], transfer_stopped=copy_ref["transfer_stopped"],
    )
    if "copy" in over:
        copy["status"] = over["copy"]
        copy["transfer_stopped"] = over.get("copy_process") == "stopped"
        if over.get("wait_s", 0) >= 600:
            copy["debt_record"] = "synthetic unresolved copy debt; preserve and page"
    ranks = {
        "ready-session": over.get("eligible_session", BASE["eligible_session"]),
        "counted": over.get("eligible_counted", BASE["eligible_counted"]),
        **{f"f2-inst-0{n}": f"inst-0{n}" in over.get("finite_ready", BASE["finite_ready"]) for n in (1, 2, 3)},
        "further-stability": over.get("stability") == "further-eligible",
    }
    day = hp.local_date(now)
    priority = evidence("synthetic complete ladder", date=day.isoformat(), complete=True, r1_post_close=True, entries=[
        evidence(f"entry {rung}", rung=rung, status="eligible" if eligible else "unavailable",
                 entry_id=over.get("stability_kit", rung) if rung == "further-stability" else rung)
        for rung, eligible in ranks.items()
    ] + [first_stability_entry(over, day)])
    spent = {}
    for row in over.get("hp_run_history", BASE["hp_run_history"]):
        span, status = row.split(":")
        spent.update(dict.fromkeys(hp.ROSTERS[f"hp-02-{span}"], "ambiguous" if status == "unknown" else "spent"))
    history = evidence(
        "synthetic per-leg census", complete=True, kit_sha256=item["kit_sha"],
        legs={**dict.fromkeys(sum(hp.ROSTERS.values(), []), "unrun"), **spent},
        prior_check=None,
    )
    if item["predecessor"] and over.get("hp_prior_check"):
        previous = item["predecessor"]
        history["prior_check"] = evidence(
            "synthetic prior HP Check", span=previous, kit_sha256=item["kit_sha"], attempt=1,
            legs=hp.ROSTERS[previous], host=BASE["host"], ended_epoch_s=now - 1200, status=over["hp_prior_check"],
        )
    starts = []
    for pair in over.get("dated_pending", BASE["dated_pending"]):
        floor = unix(pair["t0_floor"])
        last = int(hp.midnight(hp.date.fromisoformat(pair["date"]) + hp.timedelta(days=1))) - 1
        first, second = pair["spans"]
        for span, seconds in ((first, pair["first_to_second_s"]), (second, pair["last_span_bound_s"])):
            starts.append(evidence(f"synthetic counted {span}", span=span, pin="synthetic-counted-pin",
                                   date=pair["date"], windows=[[floor, last]], through_transition_s=seconds))
    if "hp_to_next_s" in over:
        assert over["hp_to_next_s"] == item["deadline_s"]
    obs = evidence(
        "fresh synthetic record", schema="hp-02.observation.v1", phase=phase, host=BASE["host"],
        binding=hp.issue_binding(item), issue_record=issue["record"], observed_epoch_s=now, valid_through_epoch_s=now,
        latest_close=close, safety=safety, look=look, priority=over.get("priority_census", priority),
        hp01_dates=evidence("synthetic hp-01 date census", kit_sha256=hp.HP01_SHA,
                            complete=BASE["date_inventory_complete"], t0_dates=over.get("hp01_t0_dates", BASE["hp01_t0_dates"])),
        history=history, copy=copy, timing=timing(item), fence_clear=over.get("fence_gone", True),
        calendar=evidence("synthetic dated inventory", complete=True, post_fence_transfer_s=0, starts=starts),
        stops=evidence("synthetic stop inventory", complete=True, open=BASE["named_stops"]),
    )
    if not over.get("queue_hash_admitted", BASE["queue_hash_admitted"]):
        # Mutate the fresh staged bytes while preserving the approved issue binding.
        queue += b"\n"
    return item, issue, obs, phase, now, HP / "cl-hp-02.json", queue


def pinned_refuses(kit, roster, argument, *, t0):
    raise PlanError(["span meets a batch blackout"])


def close_chain_for_timing(args):
    item, _, obs, *_ = args
    prior = item["predecessor"]
    if prior:
        obs["history"]["prior_check"] = evidence(
            "synthetic clean prior HP Check", status="clean", span=prior, attempt=1, kit_sha256=item["kit_sha"],
            legs=hp.ROSTERS[prior], host=obs["host"], ended_epoch_s=obs["observed_epoch_s"] - 1300,
            receipt_sha256="b" * 64, fence_gone=True, restore_proven=True,
        )
        for span, roster in hp.ROSTERS.items():
            if span < item["span"]:
                obs["history"]["legs"].update(dict.fromkeys(roster, "spent"))


def original_vectors():
    decisions = {}
    for row in DOC["cases"]:
        over = row["observations"]
        now = unix(row.get("clock", BASE["clock"]))
        planner = pinned_refuses if over.get("pin_plan") else None
        phases = ("Issue", "Start", "Run") if "phase" not in over else ("Run",)
        if phases == ("Run",):
            started = candidate({"stability": "first already done"}, unix(over["start_phase_clock"])
                                if "start_phase_clock" in over else now - 1, "Start")
            assert hp.decide(*started)["decision"] == "ELIGIBLE", row["id"]
        for phase in phases:
            decision = hp.decide(*candidate(over, now, phase), planner=planner)
            assert decision["decision"] == row["expected_successor"], (row["id"], phase, decision)
            decisions[row["id"]] = decision["decision"]
    return decisions


def timing_vectors():
    decisions = {}
    for key, span, label, now, want in regression.vectors():
        args = candidate({"span": span, "queue": "fixture-Q2"}, now, key.rsplit("/", 1)[1])
        close_chain_for_timing(args)
        item, _, obs, *_ = args
        obs["timing"] = None if label == "unknown-entry" else timing(item, 1351 if label == "old-band-late-entry" else 1100)
        decision = hp.decide(*args)
        assert decision["decision"] == want, (key, decision)
        decisions[key] = decision["decision"]
    return decisions


def clock_matrix():
    rows = 0
    with (SEAT / "fixtures/clock-matrix.csv").open() as stream:
        for row in csv.DictReader(stream):
            item = ITEMS[row["span"]]
            args = (item, HP / "cl-hp-02.json", unix(row["t0"]), timing(item))
            try:
                result = hp.occupancy(*args, arguments=(row["argument"],))
            except hp.Refusal as ex:
                actual = "REFUSE_PLAN" if ex.decision == "WAIT_PIN" else ex.decision
            else:
                actual = "ELIGIBLE"
                for key, field in (("work_s", "work_s"), ("soak_wait_s", "soak_wait_s"),
                                   ("leg_wait_s", "leg_wait_s"), ("through_clearance_s", "required_s"),
                                   ("close_s", "close_end_s")):
                    assert result[key] == int(row[field]), (row, result)
            assert actual == row["decision"], (row, actual)
            rows += 1
    return rows


def counted_pairs():
    rows = 0
    with (SEAT / "fixtures/counted-pairs.csv").open() as stream:
        for row in csv.DictReader(stream):
            now = unix(row["t0"])
            day = hp.local_date(now).isoformat()
            for phase in ("Issue", "Start", "Run"):
                args = candidate({"span": row["span"], "queue": "fixture-Q2"}, now, phase)
                close_chain_for_timing(args)
                obs = args[2]
                first = now + 900 if day == "2026-11-20" else unix(day + "T14:00:00-08:00")
                obs["calendar"].update(
                    post_fence_transfer_s=int(row["transfer_s"]),
                    starts=[evidence(f"dated {name}", span=name, pin="synthetic pin", date=day,
                                     windows=[[first, unix(row["latest"])]], through_transition_s=transition)
                            for name, transition in (("A", int(row["first_to_second_s"])), ("B", 0))],
                )
                decision = hp.decide(*args)
                assert decision["decision"] == row["decision"], (row, phase, decision)
            rows += 1
    return rows


def additional_checks():
    now = unix(BASE["clock"])
    args = candidate({}, now, "Issue")
    args[1]["line_2"] = {**args[1]["line_2"], "sentence": "unbound"}
    assert hp.decide(*args)["decision"] == "WAIT_BINDING"
    for minute, want in [(0, "CEDE_FENCE"), (45, "ELIGIBLE")]:
        t = unix(f"2026-11-20T12:{minute:02d}:00-08:00")
        for phase in ("Issue", "Start", "Run"):
            assert hp.decide(*candidate({}, t, phase, queue=fixture_queue()))["decision"] == want
    queue_b = (HP / "queue-b.json").read_bytes()
    for stamp, want in (("2026-11-20T23:59:59-08:00", "NEED_FRESH_QUEUE"), ("2026-11-21T00:00:00-08:00", "ELIGIBLE"),
                        ("2026-11-29T23:59:59-08:00", "ELIGIBLE"), ("2026-11-30T00:00:00-08:00", "NEED_FRESH_QUEUE")):
        assert hp.decide(*candidate({}, unix(stamp), "Run", queue=queue_b))["decision"] == want
    # The alternate must carry the clock sampled after the default refuses.
    night = unix("2026-11-21T23:30:00-08:00")
    args = candidate({}, night, "Run", queue=queue_b)
    args[2]["valid_through_epoch_s"] = night + 1
    actual = hp.decide(*args, resample=lambda: night + 1)
    assert actual["decision"] == "ELIGIBLE" and actual["argument"] == "13:14-13:15"
    assert actual["t0"] == night + 1
    # A fresh alternate sample also observes the exclusive expiry.
    last = unix("2026-11-29T23:59:59-08:00")
    args = candidate({}, last, "Run", queue=queue_b)
    args[2]["valid_through_epoch_s"] = last + 1
    assert hp.decide(*args, resample=lambda: last + 1)["decision"] == "NEED_FRESH_QUEUE"
    # A half-complete counted block contributes its outstanding half. The
    # later interval is disjoint from the one at which HP can actually clear.
    args = candidate({}, now, "Run")
    fence_end = now + args[0]["deadline_s"]
    args[2]["calendar"]["starts"] = [
        evidence("counted B", pin="synthetic", date=BASE["clock"][:10], span="B",
                 windows=[[now + 1, fence_end - 1], [fence_end, fence_end]], through_transition_s=99999),
    ]
    assert hp.decide(*args)["decision"] == "ELIGIBLE"
    args[2]["calendar"]["post_fence_transfer_s"] = 1
    assert hp.decide(*args)["decision"] == "CEDE_DATED"


def transition_record(span, phase, sampled, queue, **over):
    vector = candidate({"span": span, **over}, sampled, phase, queue=queue)
    close_chain_for_timing(vector)
    return vector[2]


@contextmanager
def transition_runtime(root, span, now, *, queue=None):
    """Drive the real Start and Run entry with a mutable fake clock and no native calls."""
    from joulewise.align.apple import powermode

    root.mkdir()
    if queue is None:
        queue = (HP / "queue-b.json").read_bytes()
    _, issue, *_ = candidate({"span": span}, now, "Start", queue=queue)
    args = SimpleNamespace(
        repo=SEAT / "tmp/pin", kit=HP / "cl-hp-02.json", span=span, phase="Start",
        queue=root / "queue.json", issue=root / "issue.json", observation=root / "obs.json",
        output=root / "new-output", custody=root / "custody", magistrate_pid=1000,
    )
    args.issue.write_text(json.dumps(issue))
    args.issue_sha = hp.sha256(args.issue.read_bytes())
    args.queue.write_bytes(queue)
    clock = [now]
    def record(phase, sampled, **over):
        obs = transition_record(span, phase, sampled, queue, **over)
        # Each retry observes the same immutable close receipts unless the
        # scenario explicitly supplies a different close.
        obs["latest_close"]["ended_epoch_s"] -= sampled - now
        if obs["history"]["prior_check"]:
            obs["history"]["prior_check"]["ended_epoch_s"] -= sampled - now
        if phase == "Run":
            obs["valid_through_epoch_s"] = sampled + 1200
            for field in hp.RUN_OBSERVATIONS:
                if isinstance(obs.get(field), dict):
                    obs[field]["sampled_at"] = sampled
            first = int(hp.midnight(hp.local_date(sampled)))
            last = int(hp.midnight(hp.local_date(sampled) + hp.timedelta(days=1))) - 1
            for entry in obs["priority"]["entries"]:
                entry.setdefault("start_windows", [[first, last]] if entry["status"] == "eligible" else [])
        return obs

    def invoke(observation, at, want):
        clock[0] = at
        args.phase = observation["phase"]
        args.observation.write_text(json.dumps(observation))
        captured = io.StringIO()
        with redirect_stdout(captured):
            assert hp.run_gate(args) == int(want not in hp.PASS), (root.name, want, captured.getvalue())
        decision = json.loads(captured.getvalue())
        assert decision["decision"] == want, (root.name, want, decision)
        return decision

    with (
        patch.object(hp, "assert_source_bindings", return_value=queue), patch.object(hp, "runtime_files"),
        patch.object(hp, "check_agent_census"), patch.object(powermode, "observe_ac_powermode", return_value=0),
        patch.object(hp.time, "time", side_effect=lambda: clock[0]),
        patch.object(hp.subprocess, "call", return_value=0) as launch,
    ):
        yield args, record, invoke, launch, clock


def run_transition(output):
    now = unix(BASE["clock"])
    span = BASE["span"]
    with transition_runtime(output / "usual-transition", span, now) as (args, record, invoke, launch, _):
        invoke(record("Start", now), now, "ELIGIBLE")
        queue = args.queue.read_bytes()
        run = record("Run", now + 1)
        args.queue.write_bytes(queue + b"\n")
        invoke(run, now + 1, "WAIT_BINDING")
        args.queue.write_bytes(queue)
        invoke(record("Run", now + 1, finite_ready=["inst-03"]), now + 1, "CEDE_INST_03")
        launch.assert_not_called()
        invoke(run, now + 1, "ELIGIBLE")
        launch.assert_called_once()
        assert launch.call_args.args[0][-6:] == [
            "--deadline", str(now + 1 + ITEMS[span]["deadline_s"]),
            "--exit-wait-seconds", "180", "--start-wait-seconds", "30",
        ]
        invoke(run, now + 1, "SKIP_SPENT")
        launch.assert_called_once()


def audit_transition_regressions(output):
    now = unix("2026-11-21T13:15:00-08:00")
    with transition_runtime(output / "start-high-water", BASE["span"], now) as (_, record, invoke, launch, _):
        start = record("Start", now - 60)
        start["valid_through_epoch_s"] = now + 1
        invoke(start, now, "ELIGIBLE")
        # An observation can be newer than Start's observation while still
        # predating the successful verdict. Equality also lacks a fresh read.
        for sampled in (now - 30, now):
            run = record("Run", sampled)
            run["valid_through_epoch_s"] = now + 1
            invoke(run, now + 1, "WAIT_EVIDENCE")
        invoke(record("Run", now + 1, look_attestation="ran"), now + 1, "NOT_ADMITTED")
        launch.assert_not_called()
        invoke(record("Run", now + 2), now + 2, "NOT_ADMITTED")
        launch.assert_not_called()

    with transition_runtime(output / "same-host", BASE["span"], now) as (_, record, invoke, launch, _):
        invoke(record("Start", now), now, "ELIGIBLE")
        run = record("Run", now + 1)
        for section in (run, run["latest_close"], run["safety"]):
            section["host"] = "another-synthetic-host"
        invoke(run, now + 1, "WAIT_EVIDENCE")
        launch.assert_not_called()

    expiry = unix("2026-11-30T00:00:00-08:00")
    handoff_cases = (
        ("expires-in-claim", expiry - 601, expiry + 5, "NEED_FRESH_QUEUE"),
        ("handoff-validity", now, now + 601, "WAIT_EVIDENCE"),
    )
    for name, started, valid_through, want in handoff_cases:
        with transition_runtime(output / name, BASE["span"], started) as (args, record, invoke, launch, clock):
            invoke(record("Start", started), started, "ELIGIBLE")
            run = record("Run", started + 1)
            run["valid_through_epoch_s"] = valid_through
            original = hp.write_exclusive

            def slow_claim(path, data):
                original(path, data)
                clock[0] += 1

            with patch.object(hp, "write_exclusive", side_effect=slow_claim):
                invoke(run, started + 1, want)
            launch.assert_not_called()
            assert not list((args.custody / "hp-02-arms").glob("*-a1.json"))
            if want == "WAIT_EVIDENCE":
                # Fresh evidence can proceed after a refusal before dispatch.
                invoke(record("Run", started + 2), started + 2, "ELIGIBLE")
                launch.assert_called_once()


def audit_evidence_regressions(output):
    def inverted_close(obs):
        obs["history"]["prior_check"]["ended_epoch_s"] = obs["latest_close"]["ended_epoch_s"] + 1

    def different_prior_host(obs):
        obs["history"]["prior_check"]["host"] = "another-synthetic-host"

    def failed_recovery(obs):
        close = obs["latest_close"]
        close["recovery"] = evidence("pinned restore retry", safe_route_proven=True, same_close=close["record"],
                                     result="failed", residual_refusal="open")

    def bool_mode(obs):
        for row in (obs["latest_close"], obs["safety"]):
            row["ac_powermode"] = False

    def missing_instrument(obs):
        for row in obs["priority"]["entries"]:
            if row["rung"] == "f2-inst-03":
                del row["entry_id"]

    now = unix(BASE["clock"])
    cases = (
        ("inverted-close", "hp-02-s02", inverted_close, "WAIT_EVIDENCE"),
        ("different-prior-host", "hp-02-s02", different_prior_host, "WAIT_EVIDENCE"),
        ("contradictory-recovery", BASE["span"], failed_recovery, "HALT_AND_PAGE"),
        ("boolean-mode", BASE["span"], bool_mode, "HOLD_HOST"),
        ("blank-date-text", BASE["span"], lambda obs: obs["hp01_dates"].update(t0_dates=""), "WAIT_EVIDENCE"),
        ("empty-date-list", BASE["span"], lambda obs: obs["hp01_dates"].update(t0_dates=[]), "WAIT_EVIDENCE"),
        ("omitted-historical-date", BASE["span"],
         lambda obs: obs["hp01_dates"].update(t0_dates=["2026-11-14"]), "WAIT_EVIDENCE"),
        ("missing-unavailable-instrument", BASE["span"], missing_instrument, "WAIT_EVIDENCE"),
    )
    for name, span, modify, want in cases:
        with transition_runtime(output / (name + "-start"), span, now) as (_, record, invoke, launch, _):
            start = record("Start", now)
            modify(start)
            invoke(start, now, want)
            launch.assert_not_called()
        with transition_runtime(output / (name + "-run"), span, now) as (_, record, invoke, launch, _):
            invoke(record("Start", now), now, "ELIGIBLE")
            run = record("Run", now + 1)
            modify(run)
            invoke(run, now + 1, want)
            launch.assert_not_called()

    with transition_runtime(output / "same-close-receipt", "hp-02-s02", now) as (_, record, invoke, launch, _):
        for phase, at in (("Start", now), ("Run", now + 1)):
            obs = record(phase, at)
            prior = obs["history"]["prior_check"]
            obs["latest_close"].update(ended_epoch_s=prior["ended_epoch_s"], receipt_sha256=prior["receipt_sha256"])
            obs["safety"]["close_sha256"] = prior["receipt_sha256"]
            invoke(obs, at, "ELIGIBLE")
        launch.assert_called_once()


def replace_close(obs, identity, ended, digit):
    sha = digit * 64
    obs["latest_close"].update(record=identity, ended_epoch_s=ended, receipt_sha256=sha)
    obs["safety"].update(close_record=identity, close_sha256=sha)
    obs["copy"]["predecessor"] = identity
    return obs["latest_close"]


def republish_issue(args):
    issue = json.loads(args.issue.read_bytes())
    issue["check_target"] = "new synthetic issue publication"
    args.issue.write_text(json.dumps(issue))
    args.issue_sha = hp.sha256(args.issue.read_bytes())


def audit_close_history_regressions(output, now):
    span = BASE["span"]
    with transition_runtime(output / "older-close", span, now) as (_, record, invoke, launch, _):
        invoke(record("Start", now), now, "ELIGIBLE")
        run = record("Run", now + 1)
        replace_close(run, "fixture-close-16", now - 1800, "c")
        invoke(run, now + 1, "WAIT_EVIDENCE")
        launch.assert_not_called()
        run = record("Run", now + 2)
        replace_close(run, "fixture-close-18", now, "e")
        invoke(run, now + 2, "ELIGIBLE")
        launch.assert_called_once()

    with transition_runtime(output / "after-failed-restore", span, now) as (args, record, invoke, launch, _):
        invoke(record("Start", now), now, "ELIGIBLE")
        run = record("Run", now + 1)
        close = replace_close(run, "fixture-close-18", now, "e")
        close.update(restore_status="unproven", recovery=evidence(
            "pinned recovery on close 18", same_close=close["record"], safe_route_proven=True,
            result="failed", residual_refusal="open",
        ))
        invoke(run, now + 1, "HALT_AND_PAGE")
        invoke(record("Run", now + 2), now + 2, "HALT_AND_PAGE")
        run = record("Run", now + 3)
        replace_close(run, "fixture-close-19", now + 2, "f")
        invoke(run, now + 3, "HALT_AND_PAGE")
        republish_issue(args)
        invoke(record("Start", now + 4), now + 4, "HALT_AND_PAGE")
        launch.assert_not_called()

    with transition_runtime(output / "restore-disposition", span, now) as (_, record, invoke, launch, _):
        invoke(record("Start", now), now, "ELIGIBLE")
        run = record("Run", now + 1)
        close = replace_close(run, "fixture-close-18", now, "e")
        close["restore_status"] = "unproven"
        invoke(run, now + 1, "HOLD_HOST")
        run = record("Run", now + 2)
        replace_close(run, "fixture-close-18", now, "e")
        invoke(run, now + 2, "HOLD_HOST")
        launch.assert_not_called()
        run = record("Run", now + 3)
        close = replace_close(run, "fixture-close-18", now, "e")
        close.update(restore_status="unproven", recovery=evidence(
            "pinned successful recovery", same_close=close["record"], safe_route_proven=True,
            result="proven", residual_refusal="clear",
        ))
        invoke(run, now + 3, "ELIGIBLE")
        launch.assert_called_once()

    with transition_runtime(output / "scoped-restore-stop", span, now) as (_, record, invoke, launch, _):
        invoke(record("Start", now), now, "ELIGIBLE")
        run = record("Run", now + 1)
        run["stops"]["open"] = [{"code": "RESTORE_UNPROVEN", "scope": "host"}]
        invoke(run, now + 1, "HOLD_HOST")
        invoke(record("Run", now + 2), now + 2, "HOLD_HOST")
        launch.assert_not_called()


def audit_round_two_regressions(output):
    now = unix("2026-11-21T13:15:00-08:00")
    audit_close_history_regressions(output, now)
    with transition_runtime(output / "positive-look", BASE["span"], now) as (args, record, invoke, launch, _):
        invoke(record("Start", now), now, "ELIGIBLE")
        invoke(record("Run", now + 1, look_attestation="ran"), now + 1, "NOT_ADMITTED")
        invoke(record("Run", now + 2), now + 2, "NOT_ADMITTED")
        republish_issue(args)
        invoke(record("Start", now + 3), now + 3, "NOT_ADMITTED")
        launch.assert_not_called()

    with transition_runtime(output / "look-while-ceding", BASE["span"], now) as (_, record, invoke, launch, _):
        invoke(record("Start", now), now, "ELIGIBLE")
        invoke(record("Run", now + 1, look_attestation="ran", finite_ready=["inst-03"]), now + 1, "CEDE_INST_03")
        invoke(record("Run", now + 2), now + 2, "NOT_ADMITTED")
        launch.assert_not_called()

    def same_check_two_receipts(obs):
        obs["history"]["prior_check"]["record"] = obs["latest_close"]["record"]

    def later_roster_spent(obs):
        obs["history"]["legs"].update(dict.fromkeys(hp.ROSTERS["hp-02-s02"], "spent"))

    def copied_instrument(obs):
        rows = {entry["rung"]: entry for entry in obs["priority"]["entries"]}
        rows["f2-inst-03"].update(entry_id=rows["f2-inst-02"]["entry_id"], record=rows["f2-inst-02"]["record"])

    def copied_instrument_proof(obs):
        rows = {entry["rung"]: entry for entry in obs["priority"]["entries"]}
        rows["f2-inst-03"]["record"] = rows["f2-inst-02"]["record"]

    cases = (
        ("two-receipts-one-check", "hp-02-s02", same_check_two_receipts),
        ("fixed-roster-order", BASE["span"], later_roster_spent),
        ("unidentified-inst-03", BASE["span"], copied_instrument),
        ("duplicate-instrument-proof", BASE["span"], copied_instrument_proof),
    )
    for name, span, modify in cases:
        with transition_runtime(output / (name + "-start"), span, now) as (_, record, invoke, launch, _):
            start = record("Start", now)
            modify(start)
            invoke(start, now, "WAIT_EVIDENCE")
            launch.assert_not_called()
        with transition_runtime(output / (name + "-run"), span, now) as (_, record, invoke, launch, _):
            invoke(record("Start", now), now, "ELIGIBLE")
            run = record("Run", now + 1)
            modify(run)
            invoke(run, now + 1, "WAIT_EVIDENCE")
            if name == "fixed-roster-order":
                invoke(record("Run", now + 2), now + 2, "WAIT_EVIDENCE")
            launch.assert_not_called()

    with transition_runtime(output / "later-roster-claim", BASE["span"], now) as (args, record, invoke, launch, _):
        invoke(record("Start", now), now, "ELIGIBLE")
        claim = args.custody / "hp-02-arms" / f"{hp.KIT_SHA}-hp-02-s02-a1.json"
        hp.write_exclusive(claim, {"synthetic_only": True})
        invoke(record("Run", now + 1), now + 1, "WAIT_EVIDENCE")
        launch.assert_not_called()


def launch_margin_properties(output):
    """Check the real Run entry against both runway and exclusive expiry."""
    from scripts import launch_cadence_span as launcher

    expiry_text = "2026-11-29T16:00:00-08:00"
    expiry = unix(expiry_text)
    queue = json.loads((HP / "queue-b.json").read_bytes())
    queue["expires_at"] = expiry_text
    short_queue = json.dumps(queue).encode()
    latencies = (0, 1, 599, 600, 601)
    runway = (0, 1, 599, 600, 601, 602, 1200)
    failures = {"queue": "NEED_FRESH_QUEUE", "admission": "WAIT_EVIDENCE", "watcher": "WAIT_EVIDENCE",
                "item": "WAIT_BINDING", "issue": "WAIT_BINDING"}
    checked = 0
    for field, remaining, latency in product(failures, runway, latencies):
        now = expiry - remaining if field == "queue" else unix(BASE["clock"])
        limit = now + remaining
        case = output / f"margin-{field}-{remaining}-{latency}"
        span = BASE["span"]
        queue_override = short_queue if field == "queue" else None
        with transition_runtime(case, span, now - 2, queue=queue_override) as (args, record, invoke, launch, clock):
            rendered = case / "items"
            rendered.mkdir()
            items = deepcopy(ITEMS)
            if queue_override is not None:
                items[span]["queue"]["sha256"] = hp.sha256(queue_override)
            if field == "item":
                items[span]["expires_epoch_s"] = limit
            (rendered / "items.json").write_text(json.dumps(list(items.values())))
            if field == "issue":
                issue = json.loads(args.issue.read_bytes())
                issue["expires_epoch_s"] = limit
                args.issue.write_text(json.dumps(issue))
                args.issue_sha = hp.sha256(args.issue.read_bytes())
            run = record("Run", now)
            if field == "admission":
                run["valid_through_epoch_s"] = limit
            if field == "watcher":
                run["watcher"] = evidence("synthetic watcher relied on at Run", sampled_at=now, expires_epoch_s=limit)
            run["timing"]["runner_start_max_s"] = latency
            launched_at = []

            def launch_after_delay(argv, **kwargs):
                clock[0] += latency
                plan = launcher.cadence_plan(args.kit, argv[argv.index("--legs") + 1],
                                             argv[argv.index("--batch-window") + 1])
                launched_at.append(plan["t0_epoch_s"])
                assert launched_at[-1] < limit
                return 0

            launch.side_effect = launch_after_delay
            with patch.object(hp, "HP", rendered):
                invoke(record("Start", now - 2), now - 2, "ELIGIBLE")
                allowed = remaining >= 600 and remaining > latency
                failure = "WAIT_EVIDENCE" if remaining == 1 else failures[field]
                invoke(run, now, "ELIGIBLE" if allowed else failure)
            assert launch.call_count == int(allowed)
            assert launched_at == ([now + latency] if allowed else [])
            checked += 1

    queue_bytes = (HP / "queue-b.json").read_bytes()
    opens = unix("2026-11-21T00:00:00-08:00")
    item, issue, obs, *_ = candidate({}, opens, "Run", queue=queue_bytes)
    obs["valid_through_epoch_s"] = opens + 1200
    for offset in (-1, 0, 1):
        try:
            hp.check_run_expiries(item, issue, json.loads(queue_bytes), obs, opens + offset)
        except hp.Refusal as exc:
            assert offset == -1 and exc.decision == "NEED_FRESH_QUEUE"
        else:
            assert offset >= 0
    return checked


def publication_properties(output):
    """Sweep every ordering and tie of the four events on a one-second grid."""
    epoch = unix(BASE["clock"])
    for offsets in product(range(4), repeat=4):
        sampled_start, published, sampled_run, read_run = (epoch + offset for offset in offsets)
        root = output / ("publication-" + "-".join(map(str, offsets)))
        with transition_runtime(root, BASE["span"], epoch) as (args, record, invoke, launch, clock):
            events = []
            original_read = Path.read_bytes
            verify = hp.read_published_start
            link = hp.os.link

            def observed_verify(path, current_args):
                read = verify(path, current_args)
                if current_args.phase == "Run":
                    events.append("verified-start")
                return read

            def observed_read(path):
                if args.phase == "Run" and path == args.observation:
                    events.append("read-observation")
                return original_read(path)

            def link_at_publication(source, destination, *args, **kwargs):
                if Path(destination).name.endswith(".v4.json"):
                    # The sample at the Start gate cannot stand in for a
                    # receipt that is still absent during staged write I/O.
                    assert not Path(destination).exists()
                    clock[0] = published
                return link(source, destination, *args, **kwargs)

            def attempt_start():
                start = record("Start", sampled_start)
                start["valid_through_epoch_s"] = epoch + 1200
                if sampled_start > published:
                    invoke(start, published, "WAIT_EVIDENCE")
                else:
                    with patch.object(hp.os, "link", side_effect=link_at_publication):
                        invoke(start, sampled_start, "ELIGIBLE")

            allowed = sampled_start <= published < sampled_run <= read_run
            with patch.object(hp, "read_published_start", side_effect=observed_verify), \
                 patch.object(Path, "read_bytes", observed_read):
                if published <= read_run:
                    attempt_start()
                invoke(record("Run", sampled_run), read_run, "ELIGIBLE" if allowed else "WAIT_EVIDENCE")
                expected = ["verified-start", "read-observation"] if sampled_start <= published <= read_run else []
                if allowed:
                    expected.extend(["verified-start", "read-observation"])  # Final read-only pass.
                assert events == expected, offsets
                if published > read_run:
                    attempt_start()
            assert launch.call_count == int(allowed), offsets
    return 4 ** 4


def receipt_integrity_regressions(output):
    now = unix(BASE["clock"])
    with transition_runtime(output / "receipt-integrity", BASE["span"], now) as (args, record, invoke, launch, _):
        invoke(record("Start", now), now, "ELIGIBLE")
        receipt, = (args.custody / "hp-02-arms").glob("start-*.v4.json")
        original = receipt.read_bytes()
        seal = hp.start_seal_path(receipt)
        original_seal = seal.read_bytes()
        read_bytes = Path.read_bytes

        def require_no_observation(path):
            assert path != args.observation, "Run read observations before verifying Start"
            return read_bytes(path)

        for corruption in ("digest", "unpublished"):
            envelope = json.loads(original)
            if corruption == "digest":
                envelope["receipt"]["observation"] = "modified receipt"
            else:
                envelope["receipt"]["state"] = "PREPARED"
                envelope["sha256"] = hp.sha256(hp.receipt_bytes(envelope["receipt"]))
            receipt.write_text(json.dumps(envelope))
            with patch.object(Path, "read_bytes", require_no_observation):
                invoke(record("Run", now + 1), now + 1, "WAIT_EVIDENCE")
        receipt.write_bytes(original)
        seal.unlink()
        with patch.object(Path, "read_bytes", require_no_observation):
            invoke(record("Run", now + 1), now + 1, "WAIT_EVIDENCE")
        old_seal = json.loads(original_seal)
        old_seal["publication"]["published_at"] -= 1
        seal.write_text(json.dumps(old_seal))
        with patch.object(Path, "read_bytes", require_no_observation):
            invoke(record("Run", now + 1), now + 1, "WAIT_EVIDENCE")
        seal.write_bytes(original_seal)
        for field in hp.RUN_OBSERVATIONS + ("watcher",):
            run = record("Run", now + 1)
            if field == "watcher":
                run["watcher"] = evidence("synthetic watcher", expires_epoch_s=now + 1200)
            else:
                run[field].pop("sampled_at")
            invoke(run, now + 1, "WAIT_EVIDENCE")
            run[field]["sampled_at"] = now  # No stale section can hide inside a fresh envelope.
            invoke(run, now + 1, "WAIT_EVIDENCE")
        launch.assert_not_called()
        invoke(record("Run", now + 2), now + 2, "ELIGIBLE")
        launch.assert_called_once()


def rank1_properties():
    observations = next(row["observations"] for row in DOC["cases"] if row["id"] == "rank1-spent-for-date")
    now = unix(BASE["clock"])
    for phase in ("Issue", "Start", "Run"):
        def fixture(over=observations):
            return candidate(over, now, phase, queue=(HP / "queue-b.json").read_bytes())

        def rank_one(args):
            return next(entry for entry in args[2]["priority"]["entries"] if entry["rung"] == "first-stability")

        assert hp.decide(*fixture())["decision"] == "ELIGIBLE"
        for fact in ("rank1_pool", "rank1_already_done"):
            without_fact = {key: value for key, value in observations.items() if key != fact}
            assert hp.decide(*fixture(without_fact))["decision"] == "WAIT_EVIDENCE", (phase, fact)
        for fact in rank_one(fixture())["completion"]:
            args = fixture()
            del rank_one(args)["completion"][fact]
            assert hp.decide(*args)["decision"] == "WAIT_EVIDENCE", (phase, fact)
        for kit in range(1, 17):
            args = fixture()
            row = rank_one(args)
            row["completion"]["kit_id"] = row["entry_id"] = f"f2-stab-{kit:02d}"
            assert hp.decide(*args)["decision"] == ("ELIGIBLE" if kit <= 14 else "WAIT_EVIDENCE"), (phase, kit)
        for field, incorrect in (("t0_date", hp.local_date(now - 86400).isoformat()),
                                 ("leg_id", "L013"), ("pin", hp.PIN), ("status", "running")):
            args = fixture()
            rank_one(args)["completion"][field] = incorrect
            assert hp.decide(*args)["decision"] == "WAIT_EVIDENCE", (phase, field)
        args = fixture()
        row = rank_one(args)
        row.pop("completion")
        row.update(entry_id=hp.RANK1_POOL, basis="no-eligible-kit", eligibility_census=evidence(
            "complete synthetic eligibility census", date=hp.local_date(now).isoformat(), pool=hp.RANK1_POOL,
            complete=True, eligible_kits=[],
        ))
        assert hp.decide(*args)["decision"] == "ELIGIBLE", phase



def guard_sweep():
    from joulewise.cadence import legs
    from scripts import align_r1_rehearsal as r1

    queue_bytes = (HP / "queue-b.json").read_bytes()
    queue = json.loads(queue_bytes)
    now = unix("2026-11-21T13:30:00-08:00")
    day = "2026-11-21"
    # The instrument schedule is an input to HP. Use RS463's one-leg
    # windows, including alternate-argument and closed-band edges.
    def local(hms):
        return unix(f"{day}T{hms}-08:00")

    instrument_edges = (
        ("00:00:00", "02:34:59"), ("02:35:00", "10:50:00"),
        ("13:15:00", "23:48:10"), ("23:48:11", "23:59:59"),
    )
    count = 0
    for span in ITEMS:
        item, issue, obs, _, _, kit, _ = candidate({"span": span}, now, "Run", queue=queue_bytes)
        item["expires_epoch_s"] = now + 12345
        issue["expires_epoch_s"] = now + 17968
        obs["valid_through_epoch_s"] = now + 2555
        obs["copy"]["status"] = "pending"
        obs["watcher"] = evidence("watcher", expires_epoch_s=now + 4142)
        for entry in obs["priority"]["entries"]:
            entry["start_windows"] = []
            if entry["rung"] == "f2-inst-03":
                entry["start_windows"] = [[local(lo), local(hi)] for lo, hi in instrument_edges]
        obs["calendar"]["starts"] = [evidence("pending counted start", span="A", date=day,
                                                pin="synthetic", windows=[[local("18:10:00"), local("22:00:00")]],
                                                through_transition_s=1800)]
        edges = hp.run_boundaries(item, issue, queue, obs, now)
        assert hp.occupancy(item, kit, now, obs["timing"], boundaries=edges)["argument"] == hp.ARGUMENTS[0]
        assert hp.occupancy(item, kit, local("23:40:00"), obs["timing"], boundaries=edges)["argument"] == hp.ARGUMENTS[1]
        hp.check_dated(obs["calendar"], now, item["deadline_s"], edges)
        required = {
            local("00:00:00"), local("02:00:00"), local("02:35:00"), local("10:50:01"),
            local("13:14:59"), local("13:15:00"), local("23:48:10"), local("23:48:11"),
            hp.midnight(hp.local_date(now) + hp.timedelta(days=1)),
            hp.queue_start(queue["spans"][0]), unix(queue["expires_at"]),
            local("18:10:00"), local("22:00:00") - item["deadline_s"],
            item["expires_epoch_s"], issue["expires_epoch_s"], obs["valid_through_epoch_s"],
            obs["watcher"]["expires_epoch_s"], obs["latest_close"]["ended_epoch_s"] + hp.COPY_WAIT_S,
        }
        assert required <= set(edges), (span, required - set(edges))
        assert "soak wait" in edges.values() and "leg start wait" in edges.values()
        for edge in edges:
            for offset in range(-121, 2):
                point = edge + offset
                guarded = any(point < candidate <= point + 120 for candidate in edges)
                for table, expected in (({edge: edges[edge]}, -120 <= offset < 0), (edges, guarded)):
                    try:
                        hp.check_guard_band(table, point)
                    except hp.Refusal as ex:
                        assert expected and ex.decision == "WAIT_EVIDENCE", (span, edge, offset, ex)
                    else:
                        assert not expected, (span, edge, offset, table)
                count += 1

        # Independently evaluate each pinned argument at every accepted
        # second around raw and shifted blackout boundaries and at +60.
        for arg in hp.ARGUMENTS:
            window = legs.parse_window(arg)
            for first, end in legs.window_epochs(now, [window, r1.OS_BATCH_WINDOW_LOCAL]):
                for edge in (first, end, first - item["worst_case_s"]):
                    for offset in range(-121, 2):
                        point = edge + offset
                        if any(point < candidate <= point + 120 for candidate in edges):
                            continue
                        def blocked(epoch):
                            return bool(legs.blackout_bound_s(epoch, item["worst_case_s"], [window]))
                        assert blocked(point) == blocked(point + 60), (span, arg, edge, offset)
    return count


def last_read_properties(output):
    from joulewise.align.apple import powermode
    from scripts import launch_cadence_span as launcher

    now = unix(BASE["clock"])
    count = 0
    for target, delay in product(("control", "mode", "fence", "census", "rank", "after-read"), (0, 1, 15, 60)):
        with transition_runtime(output / f"read-last-{target}-{delay}", BASE["span"], now) as (
                args, record, invoke, launch, clock):
            invoke(record("Start", now), now, "ELIGIBLE")
            run = record("Run", now + 1)
            events = []
            state = {"changed": False}
            claim_write = hp.write_exclusive
            sync = hp.sync_directory
            verify_start = hp.read_published_start
            read_bytes = Path.read_bytes
            remember = hp.remember_admission

            def mutate_after_claim_io(path, data):
                events.append("write-claim")
                claim_write(path, data)
                clock[0] += delay
                if target in ("mode", "fence", "census"):
                    state["changed"] = True
                if target == "rank":
                    changed = deepcopy(run)
                    changed["priority"]["entries"][1].update(status="eligible")
                    args.observation.write_text(json.dumps(changed))

            def sync_custody(path):
                events.append("sync")
                sync(path)

            def read_start(*args):
                events.append("start")
                return verify_start(*args)

            def read_input(path):
                names = {hp.HP / "items.json": "item", args.queue: "queue", args.issue: "issue",
                         args.observation: "evidence", args.kit: "kit"}
                if path in names:
                    events.append(names[path])
                return read_bytes(path)

            def read_admission(*args, read_only=False):
                events.append("admission-read" if read_only else "admission-preflight")
                return remember(*args, read_only=read_only)

            def read_census(*args):
                events.append("census")
                if target == "census" and state["changed"]:
                    raise hp.Refusal("HOLD_HOST", "foreign agent appeared during write")

            def read_fence(*args, binding_only=False):
                if not binding_only:
                    events.append("fence")
                    if target == "fence" and state["changed"]:
                        raise hp.Refusal("WAIT_FENCE", "fence appeared during write")

            def read_mode():
                events.append("mode")
                return 2 if state["changed"] else 0

            def receive(argv, **kwargs):
                events.append("launch")
                if target == "after-read":
                    state["changed"] = True
                plan = launcher.cadence_plan(args.kit, argv[argv.index("--legs") + 1],
                                             argv[argv.index("--batch-window") + 1])
                assert now + 1 <= plan["t0_epoch_s"] <= now + 61
                return 0

            launch.side_effect = receive
            with (patch.object(hp, "write_exclusive", side_effect=mutate_after_claim_io),
                  patch.object(hp, "sync_directory", side_effect=sync_custody),
                  patch.object(hp, "read_published_start", side_effect=read_start),
                  patch.object(Path, "read_bytes", read_input),
                  patch.object(hp, "remember_admission", side_effect=read_admission),
                  patch.object(hp, "check_agent_census", side_effect=read_census),
                  patch.object(hp, "runtime_files", side_effect=read_fence),
                  patch.object(powermode, "observe_ac_powermode", side_effect=read_mode)):
                want = {"mode": "HOLD_HOST", "census": "HOLD_HOST", "fence": "WAIT_FENCE",
                        "rank": "WAIT_EVIDENCE"}.get(target, "ELIGIBLE")
                invoke(run, now + 1, want)
            disk = args.custody / "hp-02-arms"
            assert bool(list(disk.glob("*-a1.json"))) == (want == "ELIGIBLE")
            assert launch.call_count == int(want == "ELIGIBLE")
            after_sync = events[events.index("sync") + 1:]
            assert after_sync[:5] == ["item", "start", "issue", "evidence", "queue"], events
            if want == "ELIGIBLE":
                assert {"admission-read", "kit", "census", "fence", "mode"} <= set(after_sync)
                assert after_sync.index("census") < after_sync.index("fence") < after_sync.index("mode")
                assert after_sync[after_sync.index("mode"):][:2] == ["mode", "launch"], events
                assert not {"write-claim", "sync", "admission-preflight"} & set(after_sync)
            count += 1
    return count


def launch_edge_regressions(output):
    # Exact audit reproductions and permitted controls around both edges.
    cases = (
        ("midnight", unix("2026-11-22T00:00:00-08:00")),
        ("instrument", unix(BASE["clock"])),
    )
    count = 0
    for (name, boundary), offset, delay in product(cases, (-121, -120, -119, -1), (0, 1, 59, 60)):
        now = boundary + offset
        with transition_runtime(output / f"{name}-{offset}-{delay}", BASE["span"], now - 1) as (
                _, record, invoke, launch, clock):
            invoke(record("Start", now - 1), now - 1, "ELIGIBLE")
            run = record("Run", now)
            if name == "instrument":
                row = next(e for e in run["priority"]["entries"] if e["rung"] == "f2-inst-03")
                row["start_windows"] = [[boundary, int(hp.midnight(hp.local_date(now) + hp.timedelta(days=1))) - 1]]

            def receive(*args, **kwargs):
                clock[0] += delay
                assert clock[0] < boundary
                return 0

            launch.side_effect = receive
            # A preceding clock boundary can overlap the sparse control;
            # the midnight control has no adjacent pin edge in this case.
            allowed = offset == -121 and name == "midnight"
            invoke(run, now, "ELIGIBLE" if allowed else "WAIT_EVIDENCE")
            assert launch.call_count == int(allowed)
            count += 1
    return count


if __name__ == "__main__":
    output = Path(sys.argv[2])
    original = original_vectors()
    timing_decisions = timing_vectors()
    matrix = clock_matrix()
    pairs = counted_pairs()
    additional_checks()
    with TemporaryDirectory(dir=output) as run_session:
        session = Path(run_session)
        run_transition(session)
        audit_transition_regressions(session)
        audit_evidence_regressions(session)
        audit_round_two_regressions(session)
        margin_cases = launch_margin_properties(session)
        ordering_cases = publication_properties(session)
        receipt_integrity_regressions(session)
        read_last_cases = last_read_properties(session)
        launch_edge_cases = launch_edge_regressions(session)
    rank1_properties()
    guard_cases = guard_sweep()
    print(f"PASS handoff rules: {guard_cases} guard offsets, {launch_edge_cases} launcher races "
          f"and {read_last_cases} read-last cases")
    print(f"PASS lead rules: {margin_cases} scope/runway/latency cases and {ordering_cases} publication interleavings")
    (output / "item-decisions.json").write_text(json.dumps(original, indent=2))
    (output / "timing-decisions.json").write_text(json.dumps(timing_decisions, indent=2))
    assert not freeze.NATIVE
    print(f"PASS successor: {len(original)} original decisions, {len(timing_decisions)} timing decisions, "
          f"{matrix} clock cases, {pairs} dated pairs, {len(freeze.NATIVE)} native command attempts")
