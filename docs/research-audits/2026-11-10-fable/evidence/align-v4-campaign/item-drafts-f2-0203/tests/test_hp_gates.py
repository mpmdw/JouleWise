"""Translate the frozen synthetic observations into the successor record schema."""
from contextlib import redirect_stdout
from copy import deepcopy
import csv
import io
from datetime import datetime
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
        "first-stability": over.get("stability") == "first-eligible",
        **{f"f2-inst-0{n}": f"inst-0{n}" in over.get("finite_ready", BASE["finite_ready"]) for n in (1, 2, 3)},
        "further-stability": over.get("stability") == "further-eligible",
    }
    day = hp.local_date(now)
    priority = evidence("synthetic complete ladder", date=day.isoformat(), complete=True, r1_post_close=True, entries=[
        evidence(f"entry {rung}", rung=rung, status="eligible" if eligible else "unavailable",
                 entry_id=over.get("stability_kit") if rung == "first-stability" else rung)
        for rung, eligible in ranks.items()
    ])
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
            legs=hp.ROSTERS[previous], ended_epoch_s=now - 1200, status=over["hp_prior_check"],
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
            legs=hp.ROSTERS[prior], ended_epoch_s=obs["observed_epoch_s"] - 1300,
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


def run_transition(output):
    """Exercise the launcher boundary with fake readbacks and zero native calls."""
    now = unix(BASE["clock"])
    queue = (HP / "queue-b.json").read_bytes()
    span = BASE["span"]
    _, issue, start, *_ = candidate({}, now, "Start", queue=queue)
    _, _, run, *_ = candidate({}, now + 1, "Run", queue=queue)
    _, _, higher, *_ = candidate({"finite_ready": ["inst-03"]}, now + 1, "Run", queue=queue)
    root = output / "transition"
    root.mkdir(exist_ok=True)
    args = SimpleNamespace(
        repo=SEAT / "tmp/pin", kit=HP / "cl-hp-02.json", span=span, phase="Start",
        queue=root / "queue.json", issue=root / "issue.json", observation=root / "obs.json",
        output=root / "new-output", custody=root / "custody", magistrate_pid=1000,
    )
    args.issue.write_text(json.dumps(issue))
    args.issue_sha = hp.sha256(args.issue.read_bytes())
    args.queue.write_bytes(queue)
    from joulewise.align.apple import powermode

    def invoke(record, want, status):
        args.observation.write_text(json.dumps(record))
        captured = io.StringIO()
        with patch.object(hp.time, "time", return_value=record["observed_epoch_s"]), redirect_stdout(captured):
            assert hp.run_gate(args) == status, captured.getvalue()
        assert json.loads(captured.getvalue())["decision"] == want

    with (
        patch.object(hp, "assert_source_bindings", return_value=queue), patch.object(hp, "runtime_files"),
        patch.object(hp, "check_agent_census"), patch.object(powermode, "observe_ac_powermode", return_value=0),
        patch.object(hp.subprocess, "call", return_value=0) as launch,
    ):
        invoke(start, "ELIGIBLE", 0)
        args.phase = "Run"
        args.queue.write_bytes(queue + b"\n")
        invoke(run, "WAIT_BINDING", 1)
        args.queue.write_bytes(queue)
        invoke(higher, "CEDE_INST_03", 1)
        launch.assert_not_called()
        invoke(run, "ELIGIBLE", 0)
        launch.assert_called_once()
        assert launch.call_args.args[0][-6:] == [
            "--deadline", str(now + 1 + ITEMS[span]["deadline_s"]),
            "--exit-wait-seconds", "180", "--start-wait-seconds", "30",
        ]
        invoke(run, "SKIP_SPENT", 1)
        launch.assert_called_once()


if __name__ == "__main__":
    output = Path(sys.argv[2])
    original = original_vectors()
    timing_decisions = timing_vectors()
    matrix = clock_matrix()
    pairs = counted_pairs()
    additional_checks()
    with TemporaryDirectory(dir=output) as run_session:
        run_transition(Path(run_session))
    (output / "item-decisions.json").write_text(json.dumps(original, indent=2))
    (output / "timing-decisions.json").write_text(json.dumps(timing_decisions, indent=2))
    assert not freeze.NATIVE
    print(f"PASS successor: {len(original)} original decisions, {len(timing_decisions)} timing decisions, "
          f"{matrix} clock cases, {pairs} dated pairs, {len(freeze.NATIVE)} native command attempts")
