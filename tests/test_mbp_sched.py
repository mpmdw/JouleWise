"""Frozen decision invariants. Every ledger, receipt and host observation is synthetic."""

from copy import deepcopy
from datetime import datetime
import contextlib
import hashlib
import io
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch
from zoneinfo import ZoneInfo

from scripts import mbp_sched as sched


FIXTURES = Path(__file__).parent / "fixtures" / "mbp_sched"
ZONE = ZoneInfo("America/Los_Angeles")
READBACKS = ("power_mode", "network_time_off", "frequency_word_zero", "no_monitor",
             "no_high_power_marker", "feeds_stopped", "process_group_gone")


def epoch(day=18, hour=14, minute=0, second=0):
    return int(datetime(2026, 11, day, hour, minute, second, tzinfo=ZONE).timestamp())


def encoded(value):
    return json.dumps(value, ensure_ascii=True, sort_keys=True, separators=(",", ":")).encode()


def digest(value):
    return hashlib.sha256(encoded(value)).hexdigest()


def head_for(rows):
    return {"ledger_id": "fixture-ledger", "last_seq": len(rows),
            "digest": hashlib.sha256(b"".join(encoded(row) + b"\n" for row in rows)).hexdigest()}


def write(path, value):
    path.write_bytes(encoded(value) + b"\n")


def probe_child(argv, **kwargs):
    responses = {
        "pmset": "Now drawing from 'AC Power'\n - 100%; charged",
        "df": "Filesystem 1G-blocks Used Available Capacity Mounted on\nfixture 500 100 400 20% /",
        "launchctl": "PID\tStatus\tLabel\n-\t0\tfixture",
        "ps": "PID PPID COMM\n10 1 fixture-agent\n11 10 fixture-agent\n",
        "sysctl": "{ sec = 1794900000, usec = 0 }",
    }
    return subprocess.CompletedProcess(argv, 0, responses.get(Path(argv[0]).name, ""), "")


class History:
    """Build writer events without using the scheduler's fold."""

    def __init__(self):
        self.rows = []

    def add(self, event, legs=0, **fields):
        row = {"seq": len(self.rows) + 1, "event": event, "legs": legs, **fields}
        self.rows.append(row)
        return row

    def launch(self, entry_id, span_id, started, *, kind="product_filler", groups=(),
               legs=1, pin, boot_id="boot-a", kit_sha256=None, block=None, **fields):
        members = {"kind": kind, "groups": list(groups), "block": block, "legs": legs}
        return self.add("LAUNCH", legs, entry_id=entry_id, span_id=span_id,
                        t0_epoch=started, pin=pin, boot_id=boot_id, kit_sha256=kit_sha256,
                        kind=kind, groups=list(groups), block=block, queue_commit="fixture-commit",
                        registration=members, campaign="fixture-campaign", **fields)

    def bind(self, attempt):
        return {**{key: attempt[key] for key in ("entry_id", "span_id", "kit_sha256")},
                "open_seq": attempt["seq"]}

    def close(self, attempt, ended, *, clean=True, restore=True, redos=0, load_flag=False,
              copy=True, receipt=True):
        bound = self.bind(attempt)
        if receipt:
            self.add("RECEIPT", **bound, receipt_id="receipt-" + attempt["span_id"], receipt={
                "entry_id": attempt["entry_id"], "span_id": attempt["span_id"],
                "kit_sha256": attempt["kit_sha256"], "mock": False, "rc": 0,
                "started": {"epoch_s": attempt["t0_epoch"]}, "ended": {"epoch_s": ended},
            })
        readbacks = dict.fromkeys(READBACKS, True)
        readbacks["feeds_stopped"] = restore
        self.add("RESTORE", **bound, readbacks=readbacks)
        self.add("CLOSE", attempt["legs"], **bound, ended_epoch=ended,
                 clean=clean, load_redos=redos, load_flag=load_flag)
        if copy:
            self.add("COPY_VERIFIED", **bound)

    def ready(self, entry, effective, route_clear=True, expected_ready_by=None):
        self.add("READY", entry_id=entry, effective=effective, route_clear=route_clear,
                 expected_ready_by=expected_ready_by)


MIRRORS = {
    "launches": {"LAUNCH"}, "closes": {"CLOSE"}, "receipts": {"RECEIPT"},
    "restore_proofs": {"RESTORE"}, "stops": {"STOP"}, "gates": {"GATE"},
    "ready": {"READY"}, "refusals": {"REFUSAL"},
    "copy_events": {"COPY_VERIFIED", "UPLOAD_STOPPED", "COPY_STARTED"},
    "config_events": {"CONFIG"},
}


def scenario(name):
    queue = json.loads(sched.DEFAULT_QUEUE.read_text())
    rules = json.loads(sched.DEFAULT_RULES.read_text())
    f0 = queue["entries"][0]
    f0.update(worktree="/fixture/f0", argv=["fixture-f0"], worst_case_s=12180)
    now = epoch()
    pin = f0["pin"]
    counted = {**f0, "id": "dev-next", "kind": "counted", "repeat": False,
               "worktree": "/fixture/count", "argv": ["fixture-count", "--legs", "1"],
               "plan_argv": ["fixture-count-plan"],
               "requires": ["pin-admitted", "registered-window", "block-dependency", "launcher-admits"],
               "params": {"groups": ["dev-mixed", "dev-total"], "legs": 1,
                          "campaign": "fixture-campaign",
                          "date_caps": [{"group": "dev-mixed", "max": 12}],
                          "gates": ["freeze-2"], "window": {"earliest_epoch": epoch(hour=0),
                                                            "latest_epoch": epoch(hour=23, minute=59, second=59)}},
               "expected_s": 2400, "worst_case_s": 3200}
    short = {**f0, "id": "short", "kind": "product_filler", "repeat": False,
             "worktree": "/fixture/short", "argv": ["fixture-short"], "plan_argv": ["fixture-short-plan"],
             "requires": ["pin-admitted", "counted-fits", "launcher-admits", "not-refused"],
             "params": {}, "expected_s": 2900, "worst_case_s": 3800}
    queue["entries"] += [counted, short]
    if name != "counted":
        counted["expected_ready_by"] = now + 4000
    winning = {"counted": counted, "short": short}.get(name)
    if name == "v4":
        winning = {**f0, "id": "v4-ready", "kind": "v4_session", "repeat": False,
                   "worktree": "/fixture/v4", "argv": ["fixture-v4"], "plan_argv": ["fixture-v4-plan"],
                   "requires": ["pin-admitted", "launcher-admits", "session-route"], "params": {}}
        queue["entries"].append(winning)

    history = History()
    prior = history.launch("dev-prior", "dev-1", now - 500, kind="counted", pin=pin,
                           groups=("dev-mixed", "dev-total"), legs=11,
                           soak_end_epoch=now - 480, predicted_batch_epoch=now - 510)
    history.close(prior, now - 450, clean=False, redos=3, load_flag=True)
    history.add("STOP", **history.bind(prior), code="CONTAMINATED_REDOS", epoch=now - 449)
    for index, boot in enumerate(("boot-a", "boot-b")):
        attempt = history.launch("instrument", f"inst-{index}", now - 400 + index * 100, pin=pin,
                                 kind="product_filler", groups=("dev-mixed",), legs=12, boot_id=boot)
        history.close(attempt, attempt["t0_epoch"] + 10)
    history.add("GATE", id="freeze-2", passed=False)
    history.add("GATE", id="freeze-2", passed=True)
    history.add("GATE", id="r1-post-close-check", passed=False)
    history.ready("dev-next", False, expected_ready_by=counted.get("expected_ready_by"))
    if name == "counted":
        history.ready("dev-next", True)
    if name == "v4":
        history.ready("v4-ready", False)
        history.ready("v4-ready", True)
    history.add("REFUSAL", entry_id="other", kit_sha256=None, block=None,
                queue_commit="fixture-commit", epoch=now - 10, reason="fixture refusal")
    facts = json.loads((FIXTURES / "facts.json").read_text())
    history.add("CONFIG", queue_commit=facts["queue_commit"],
                queue_digest=digest(queue), rules_digest=digest(rules))
    facts.update(now_epoch=now, ledger_head=head_for(history.rows), queue_digest=digest(queue),
                 rules_digest=digest(rules), plans={})
    for mirror, kinds in MIRRORS.items():
        facts[mirror] = deepcopy([row for row in history.rows if row["event"] in kinds])
    facts["uncopied"] = []
    set_plans(queue, facts)
    return queue, rules, facts, history.rows, winning


def set_plans(queue, facts):
    facts["plans"] = {}
    for entry in queue["entries"]:
        if "plan_argv" in entry:
            # This is the writer's attestation, independently encoded for the control.
            values = [entry, facts["ledger_head"], facts["queue_commit"], facts["queue_digest"],
                      facts["rules_digest"], facts["now_epoch"], facts["now_epoch"], entry["argv"]]
            facts["plans"][entry["id"]] = {"rc": 0, "signature": digest(values)}


def reseal(queue, rules, facts, rows, mirrors=True):
    revision = {"queue_commit": facts["queue_commit"],
                "queue_digest": digest(queue), "rules_digest": digest(rules)}
    existing = next((row for row in reversed(rows) if row["event"] == "CONFIG"), {})
    if any(existing.get(key) != value for key, value in revision.items()):
        rows.append({"seq": len(rows) + 1, "event": "CONFIG", "legs": 0, **revision})
    facts.update(ledger_head=head_for(rows), queue_digest=digest(queue), rules_digest=digest(rules))
    for key, events in MIRRORS.items():
        if mirrors:
            facts[key] = deepcopy([row for row in rows if row["event"] in events])
        else:
            facts.pop(key, None)
    facts.pop("uncopied", None)
    set_plans(queue, facts)
    return facts


def decide(queue, rules, facts, rows, *, head=None, now=None, recheck=None):
    if head is None:
        head = facts.get("ledger_head") if isinstance(facts, dict) else None
    return sched.authorize_next(queue, rules, facts, rows, head, now=now,
                                recheck_head=recheck or (lambda: deepcopy(head)))["decision"]


def paths(value, prefix=()):
    if isinstance(value, dict):
        for key, element in value.items():
            subpath = (*prefix, key)
            yield subpath, element
            yield from paths(element, subpath)
    elif isinstance(value, list):
        for index, element in enumerate(value):
            subpath = (*prefix, index)
            yield subpath, element
            yield from paths(element, subpath)


def replace(tree, path, operation, value=None):
    root = deepcopy(tree)
    parent = root
    for key in path[:-1]:
        parent = parent[key]
    key = path[-1]
    if operation == "delete":
        del parent[key]
    else:
        parent[key] = value
    return root


def collection_mutations(value):
    for path, items in [((), value), *paths(value)]:
        if not isinstance(items, list):
            continue
        # Only row collections have positional identity. Groups, argv and rule
        # references are covered by the required-field operator below.
        if not any(isinstance(item, dict) for item in items):
            continue
        for index, item in enumerate(items):
            for operation in ("delete", "null", "duplicate", "move"):
                targets = range(len(items)) if operation == "move" else (index,)
                for target in targets:
                    if operation == "move" and index == target:
                        continue
                    edited = list(items)
                    if operation == "delete":
                        del edited[index]
                    elif operation == "null":
                        edited[index] = None
                    elif operation == "duplicate":
                        edited.insert(index, deepcopy(item))
                    else:
                        edited.insert(target, edited.pop(index))
                    if edited != items:
                        yield (operation, path, index, target), (
                            replace(value, path, "set", edited) if path else edited)


def field_mutations(value):
    for path, item in paths(value):
        if isinstance(path[-1], int) and isinstance(item, dict):
            continue
        wrong = [] if not isinstance(item, (dict, list)) else False
        for operation, substitution in (("delete", None), ("null", None), ("type", wrong),
                                        ("unparseable", "not a structured value")):
            edited = replace(value, path, "delete" if operation == "delete" else "set", substitution)
            if encoded(edited) != encoded(value):
                yield (operation, path), edited


class MutationProperties(unittest.TestCase):
    def test_every_operator_on_every_control(self):
        totals = {}
        for control in ("counted", "v4", "short"):
            queue, rules, facts, rows, expected = scenario(control)
            head = head_for(rows)
            launch = decide(queue, rules, facts, rows)
            self.assertEqual((launch["decision"], launch["entry"], launch["worktree"], launch["argv"]),
                             ("LAUNCH", expected["id"], expected["worktree"], expected["argv"]))
            count = 0

            def check(label, edited, *, irrelevant=False):
                nonlocal count
                count += 1
                decision = decide(*edited, head=head)
                if decision["decision"] == "LAUNCH":
                    self.assertEqual((irrelevant, decision), (True, launch), (control, label))

            inputs = (queue, rules, facts, rows)
            for index, source in enumerate(inputs):
                operators = (field_mutations(source), collection_mutations(source))
                for mutations in operators:
                    for label, edited in mutations:
                        args = list(inputs)
                        args[index] = edited
                        # Exact exemptions: mirrors and optional informational
                        # observations aren't used when the committed event
                        # stream already provides complete evidence.
                        mirror = (len(label) == 2 and label[0] == "delete" and len(label[1]) == 1
                                  and label[1][0] in set(MIRRORS) | {"uncopied"})
                        informational = (len(label) == 2 and label[0] == "delete"
                                         and label[1] == ("labels_loaded",))
                        check((index, label), args, irrelevant=index == 2 and (mirror or informational))
            for changed in (None, [], *[rows[:i] for i in range(1, len(rows))]):
                check(("ledger prefix", None if changed is None else len(changed)),
                      (queue, rules, facts, changed))
            for key in ("receipts", "restore_proofs", "stops", "gates", "ready", "launches",
                        "closes", "config_events"):
                for i, row in enumerate(facts[key]):
                    if key == "receipts":
                        substitutions = [(("receipt", "span_id"), "wrong-span")]
                    elif key == "restore_proofs":
                        substitutions = [(("readbacks", name), False) for name in READBACKS]
                    elif key == "stops":
                        substitutions = [(("code",), "LEG_OVERTIME")]
                    elif key == "gates":
                        substitutions = [(("passed",), not row["passed"])]
                    elif key == "ready":
                        substitutions = [(("effective",), not row["effective"]),
                                         (("route_clear",), not row["route_clear"]),
                                         (("expected_ready_by",), None if row["expected_ready_by"] is not None
                                           else facts["now_epoch"] + 1)]
                    elif key == "config_events":
                        substitutions = [(("queue_commit",), "wrong-commit")]
                    else:
                        substitutions = [(("legs",), row["legs"] + 1)]
                        if key == "launches":
                            substitutions.append((("groups",), ["wrong-group"]))
                    for path, alternate in substitutions:
                        edited_fact = replace(facts, (key, i, *path), "set", alternate)
                        check(("conflicting mirror", key, i, path), (queue, rules, edited_fact, rows))
                        edited_row = replace(rows, (row["seq"] - 1, *path), "set", alternate)
                        check(("conflicting event", key, i, path), (queue, rules, facts, edited_row))
            for label, changed_head in field_mutations(head):
                count += 1
                self.assertNotEqual(decide(queue, rules, facts, rows, head=changed_head)["decision"],
                                    "LAUNCH", (control, label))
            for when in (facts["now_epoch"] - 1, epoch(17, 23, 59), rows[0]["t0_epoch"] - 1):
                count += 1
                self.assertNotEqual(decide(queue, rules, facts, rows, head=head, now=when)["decision"], "LAUNCH")
            for path, stamp in paths(rows):
                if path[-1] in ("epoch", "t0_epoch", "ended_epoch", "epoch_s",
                                "soak_end_epoch", "predicted_batch_epoch"):
                    for earlier in (stamp - 1, epoch(17, 23, 59), rows[0]["t0_epoch"] - 1):
                        check(("rolled event", path, earlier),
                              (queue, rules, facts, replace(rows, path, "set", earlier)))
            totals[control] = count
        print(f"MUTATION_PASSES scenarios={len(totals)} mutations={sum(totals.values())} per_scenario={totals}")
        self.assertEqual(len(totals), 3)
        self.assertTrue(all(count > 1000 for count in totals.values()))


class Regressions(unittest.TestCase):
    def setUp(self):
        self.queue, self.rules, self.facts, self.rows, self.entry = scenario("counted")

    def decision(self, *, resealed=False, now=None):
        if resealed:
            reseal(self.queue, self.rules, self.facts, self.rows)
        return decide(self.queue, self.rules, self.facts, self.rows, now=now)

    def test_audit_clock_rollback_and_latest_failed_attempt(self):
        history = History()
        history.rows = self.rows
        when = self.rows[0]["t0_epoch"] - 10
        last = history.launch("instrument", "inst-last", when, pin=self.entry["pin"], boot_id="new-boot")
        decision = self.decision(resealed=True)
        self.assertEqual(decision, {"decision": "CLOSE_OWED", "entry": "inst-last"})
        history.close(last, when + 1, restore=False)
        self.assertEqual(self.decision(resealed=True)["rule"], "RESTORE_UNPROVEN")
        del self.rows[last["seq"] - 1]
        self.assertEqual(self.decision(resealed=True)["decision"], "HALT")
        # Resequence to reach semantic validation rather than failing on a gap.
        for i, row in enumerate(self.rows, 1):
            row["seq"] = i
        self.assertEqual(self.decision(resealed=True)["rule"], "LEDGER_ORPHAN")

    def test_audit_no_receipt_or_wrong_span_cannot_prove_close(self):
        last_receipt = next(row for row in reversed(self.rows) if row["event"] == "RECEIPT")
        last_receipt["receipt"]["span_id"] = "wrong-span"
        self.assertEqual(self.decision(resealed=True)["rule"], "RECEIPT_CONFLICT")
        self.rows.remove(last_receipt)
        for i, row in enumerate(self.rows, 1):
            row["seq"] = i
        self.assertEqual(self.decision(resealed=True)["rule"], "RECEIPT_MISSING")

    def test_audit_truncated_ledger_and_mirrors_cannot_erase_stops_gates_or_ready(self):
        for partial in (None, [], self.rows[:6]):
            with self.subTest(partial=partial):
                self.assertEqual(decide(self.queue, self.rules, self.facts, partial)["decision"], "HALT")
        for field in ("closes", "stops", "gates", "ready", "receipts"):
            with self.subTest(field=field):
                changed = {**self.facts, field: []}
                self.assertEqual(decide(self.queue, self.rules, changed, self.rows)["rule"],
                                 "LEDGER_FACT_CONFLICT")
        changed = deepcopy(self.facts)
        changed["ready"].reverse()
        self.assertEqual(decide(self.queue, self.rules, changed, self.rows)["rule"], "LEDGER_FACT_CONFLICT")
        self.assertEqual(decide(self.queue, self.rules, self.facts, self.rows, recheck=lambda: {
            **self.facts["ledger_head"], "last_seq": 900,
        })["rule"], "LEDGER_HEAD_CHANGED")

    def test_audit_rollback_dated_contamination_is_active_until_later_clean_attempt(self):
        history = History()
        history.rows = self.rows
        history.add("STOP", **history.bind(self.rows[0]), code="CONTAMINATED_REDOS",
                    epoch=self.rows[0]["t0_epoch"] - 100)
        self.assertEqual(self.decision(resealed=True).get("entry"), "short")
        clock = self.facts["now_epoch"]
        later = history.launch("instrument", "cleanup", clock - 50, pin=self.entry["pin"])
        history.close(later, clock - 40)
        self.assertEqual(self.decision(resealed=True).get("entry"), "dev-next")

    def test_audit_caps_use_launch_legs_once_and_ignore_product_filler(self):
        self.assertEqual(self.decision()["entry"], "dev-next")
        self.entry["params"]["legs"] = 6
        self.entry["argv"][-1] = "6"
        self.assertNotEqual(self.decision(resealed=True).get("entry"), "dev-next")
        del self.entry["params"]["legs"]
        self.assertEqual(self.decision(resealed=True)["decision"], "HALT")
        self.entry["params"]["legs"] = 1
        del self.rows[0]["legs"]
        self.assertEqual(self.decision(resealed=True)["decision"], "HALT")

    def test_audit_qualification_batch_and_window_cannot_be_omitted_by_requires(self):
        self.entry["id"] = "qual-next"
        self.entry["params"].update(qualification=True, soak_end_s=1950, groups=["qualification"])
        self.entry["requires"].remove("registered-window")
        self.facts["boot_epoch"] = self.facts["now_epoch"] + 2400 - 43248
        # Qualification's date has no development charge so the batch itself binds.
        self.rows[0]["groups"] = ["registered-other"]
        self.rows[0]["registration"]["groups"] = ["registered-other"]
        self.rows[0]["entry_id"] = "prior-other"
        for row in self.rows[1:6]:
            row["entry_id"] = "prior-other"
            if row["event"] == "RECEIPT":
                row["receipt"]["entry_id"] = "prior-other"
        for row in self.rows:
            if row["event"] == "READY":
                row["entry_id"] = "qual-next"
        result = self.decision(resealed=True)
        self.assertEqual(result.get("entry"), "short", result)
        report = sched.authorize_next(self.queue, self.rules, self.facts, self.rows, head_for(self.rows),
                                      recheck_head=lambda: head_for(self.rows))
        self.assertEqual(next(row["rule"] for row in report["entries"] if row["id"] == "qual-next"),
                         "qualification-batch")
        self.entry["id"] = "dev-next"
        for row in self.rows:
            if row["event"] == "READY":
                row["entry_id"] = "dev-next"
        self.entry["params"].pop("qualification")
        self.entry["params"]["groups"] = ["dev-mixed", "dev-total"]
        self.entry["params"]["window"] = {"earliest_epoch": epoch(19, hour=0),
                                           "latest_epoch": epoch(19, hour=23, minute=59, second=59)}
        self.assertNotEqual(self.decision(resealed=True).get("entry"), "dev-next")

    def test_two_counted_batch_stops_extend_clearance_after_a_clean_filler(self):
        history = History()
        history.rows = self.rows
        now = self.facts["now_epoch"]
        self.entry["params"]["soak_end_s"] = 1950
        self.facts["boot_epoch"] = now + 2400 - 43248
        for index, t0 in enumerate((now - 180, now - 120)):
            launch = history.launch("study-prior", f"batch-{index}", t0, pin=self.entry["pin"],
                                    kind="counted", groups=("study",), soak_end_epoch=t0 + 5,
                                    predicted_batch_epoch=t0 + 10)
            history.close(launch, t0 + 20, clean=False, redos=3, load_flag=True)
            history.add("STOP", **history.bind(launch), code="CONTAMINATED_REDOS", epoch=t0 + 21)
        latest = history.launch("instrument", "after-batches", now - 50, pin=self.entry["pin"])
        history.close(latest, now - 40)
        self.assertEqual(self.decision(resealed=True)["entry"], "short")
        report = sched.authorize_next(self.queue, self.rules, self.facts, self.rows, head_for(self.rows),
                                      recheck_head=lambda: head_for(self.rows))
        self.assertEqual(next(row["rule"] for row in report["entries"] if row["id"] == "dev-next"),
                         "qualification-batch")

        launch["soak_end_epoch"] = launch["t0_epoch"] + 21  # one second after the close
        self.assertEqual(self.decision(resealed=True)["entry"], "short")
        launch["soak_end_epoch"] = launch["t0_epoch"] - 1
        self.assertEqual(self.decision(resealed=True)["entry"], "short")

    def test_three_redos_in_a_close_hold_counted_even_without_a_stop_row(self):
        history = History()
        history.rows = self.rows
        now = self.facts["now_epoch"]
        attempt = history.launch("other-filler", "loaded", now - 30, pin=self.entry["pin"])
        history.close(attempt, now - 20, clean=False, redos=3, load_flag=True)
        self.assertEqual(self.decision(resealed=True)["entry"], "short")
        for kind, start in (("maintenance", now - 19), ("product_filler", now - 15)):
            no_measurement = history.launch("housekeeping", kind, start, pin=self.entry["pin"],
                                            kind=kind, legs=0)
            history.close(no_measurement, start + 2)
            self.assertEqual(self.decision(resealed=True)["entry"], "short")
        later = history.launch("instrument", "recovered", now - 10, pin=self.entry["pin"])
        history.close(later, now - 5)
        self.assertEqual(self.decision(resealed=True)["entry"], self.entry["id"])

    def test_wait_can_name_an_opening_twelve_days_away(self):
        self.queue["entries"] = self.queue["entries"][:2]
        start = epoch(30, hour=0)
        self.entry["params"]["window"] = {"earliest_epoch": start,
                                           "latest_epoch": epoch(30, hour=23, minute=59, second=59)}
        history = History()
        history.rows = self.rows
        history.add("REFUSAL", entry_id="f0-part-c", kit_sha256=None, block=None,
                    queue_commit=self.facts["queue_commit"], epoch=self.facts["now_epoch"],
                    reason="fixture refusal")
        result = self.decision(resealed=True)
        self.assertEqual((result["decision"], result["until_epoch"]), ("WAIT", start))

    def test_dated_block_cutoff_protects_all_remaining_starts(self):
        now = self.facts["now_epoch"]
        for row in self.rows:
            if row["event"] in ("LAUNCH", "CLOSE") and row["entry_id"] == "dev-prior":
                row["legs"] = 9
                if "registration" in row:
                    row["registration"]["legs"] = 9
        self.entry.update(block="fixture-pair", worst_case_s=3200)
        self.entry["params"]["window"]["latest_epoch"] = now + 5400
        second = deepcopy(self.entry)
        second.update(id="dev-second", plan_argv=["second-plan"], argv=["second"])
        self.queue["entries"].append(second)
        history = History()
        history.rows = self.rows
        history.ready("dev-next", False)
        history.ready("dev-second", False)
        reseal(self.queue, self.rules, self.facts, self.rows)
        report = sched.authorize_next(self.queue, self.rules, self.facts, self.rows, head_for(self.rows),
                                      recheck_head=lambda: head_for(self.rows))
        self.assertNotEqual(report["decision"]["decision"], "LAUNCH")
        self.assertEqual(next(row["rule"] for row in report["entries"] if row["id"] == "short"),
                         "counted-fits")

    def test_semantic_overlap_reuse_and_no_predecessor_halt(self):
        history = History()
        history.add("GATE", id="freeze-2", passed=True)
        self.rows[:] = history.rows
        self.assertEqual(self.decision(resealed=True)["rule"], "PREDECESSOR_MISSING")
        history.rows = self.rows
        now = self.facts["now_epoch"]
        launch = history.launch("instrument", "one", now - 60, pin=self.entry["pin"])
        second = history.launch("instrument", "two", now - 30, pin=self.entry["pin"])
        self.assertEqual(self.decision(resealed=True)["rule"], "LEDGER_OVERLAP")
        self.rows.remove(second)
        history.close(launch, now - 50)
        history.launch("instrument", "one", now - 30, pin=self.entry["pin"])
        self.assertEqual(self.decision(resealed=True)["rule"], "LEDGER_DUPLICATE")

    def test_audit_ready_counted_and_v4_precede_fillers_and_latest_ready_wins(self):
        for name in ("counted", "v4"):
            with self.subTest(name=name):
                queue, rules, facts, rows, ready = scenario(name)
                history = History()
                history.rows = rows
                now = facts["now_epoch"]
                filler = dict(queue["entries"][2])
                filler.pop("plan_argv")
                queue["entries"] += [
                    dict(filler, id=entry, block="filler-pair") for entry in ("fill-first", "fill-second")
                ]
                first = history.launch("fill-first", "filler-1", now - 50,
                                       pin=filler["pin"], block="filler-pair")
                history.close(first, now - 40)
                reseal(queue, rules, facts, rows)
                self.assertEqual(decide(queue, rules, facts, rows)["entry"], ready["id"])
                history.ready(ready["id"], False)
                reseal(queue, rules, facts, rows)
                self.assertNotEqual(decide(queue, rules, facts, rows).get("entry"), ready["id"])

    def test_audit_partial_boot_metadata_cannot_hide_latest_failed_restore(self):
        history = History()
        history.rows = self.rows
        now = self.facts["now_epoch"]
        latest = history.launch("instrument", "inst-last", now - 10, pin=self.entry["pin"], boot_id="other-boot")
        history.close(latest, now - 9, restore=False)
        self.assertEqual(self.decision(resealed=True)["rule"], "RESTORE_UNPROVEN")
        latest.pop("boot_id")
        self.assertEqual(self.decision(resealed=True)["rule"], "LEDGER_INVALID")

    def test_resealed_receipt_identity_cannot_be_reused(self):
        receipts = [row for row in self.rows if row["event"] == "RECEIPT"]
        receipts[-1]["receipt_id"] = receipts[0]["receipt_id"]
        self.assertEqual(self.decision(resealed=True)["rule"], "LEDGER_DUPLICATE")

    def test_counted_t0_cannot_move_charged_legs_across_midnight(self):
        midnight = epoch(hour=0)
        history = History()
        self.rows = history.rows
        smoke = history.launch("instrument", "smoke", midnight - 100, pin=self.entry["pin"])
        history.close(smoke, midnight - 90)
        for entry in self.queue["entries"]:
            if entry["kind"].endswith("_filler"):
                history.add("REFUSAL", entry_id=entry["id"], kit_sha256=entry["kit_sha256"],
                            block=None, queue_commit="fixture-commit", epoch=midnight + 1,
                            reason="fixture refusal")
        charged = history.launch("dev-prior", "charged", midnight + 5, kind="counted",
                                 pin=self.entry["pin"], groups=("dev-mixed", "dev-total"), legs=12)
        history.close(charged, midnight + 60)
        history.add("GATE", id="freeze-2", passed=True)
        history.ready(self.entry["id"], True)
        self.assertEqual(self.decision(resealed=True)["decision"], "WAIT")
        for rolled in (midnight + 4, midnight - 1):
            with self.subTest(rolled=rolled):
                charged["t0_epoch"] = rolled
                result = self.decision(resealed=True)
                self.assertEqual((result["decision"], result["rule"]), ("HALT", "CLOCK_ROLLBACK"))

    def test_ready_split_qualification_moves_to_next_lawful_date(self):
        first, second = deepcopy(self.entry), deepcopy(self.entry)
        for entry, name in ((first, "qual-s01"), (second, "qual-s02")):
            entry.update(id=name, block="qual-01", argv=["fixture-count", name])
            entry["params"].update(qualification=True, groups=["qualification"], soak_end_s=900,
                                   date_caps=[], window={"earliest_epoch": epoch(17, hour=0),
                                                        "latest_epoch": epoch(17, 23, 59, 59)})
        first.pop("plan_argv")
        self.queue["entries"] = [self.queue["entries"][0], first, second]
        history = History()
        self.rows = history.rows
        smoke = history.launch("instrument", "native-smoke", epoch(17, hour=10), pin=first["pin"])
        history.close(smoke, epoch(17, hour=11))
        launch = history.launch(first["id"], "completed-half", epoch(17, hour=12), kind="counted",
                                pin=first["pin"], groups=("qualification",), block="qual-01")
        history.close(launch, epoch(17, hour=13))
        history.add("GATE", id="freeze-2", passed=True)
        history.add("GATE", id="r1-post-close-check", passed=False)
        history.ready(second["id"], True)
        self.facts["boot_epoch"] = epoch(16, hour=8)
        for day in (17, 18):
            with self.subTest(day=day):
                self.facts["now_epoch"] = epoch(day, hour=14)
                self.assertEqual(self.decision(resealed=True).get("entry"), second["id"])
                self.assertEqual(launch["t0_epoch"], epoch(17, hour=12))
        other = history.launch("qual-other", "occupied-date", epoch(18, hour=12), kind="counted",
                               pin=second["pin"], groups=("qualification",), block="qual-other")
        history.close(other, epoch(18, hour=13))
        self.assertEqual(self.decision(resealed=True)["entry"], "f0-part-c")
        self.facts["now_epoch"] = epoch(19, hour=14)
        self.assertEqual(self.decision(resealed=True)["entry"], second["id"])
        self.assertEqual(launch["t0_epoch"], epoch(17, hour=12))

    def test_only_measured_smoke_roles_qualify_the_pin(self):
        now = self.facts["now_epoch"]
        for kind, name, legs, pilot, qualifies in [
            ("maintenance", "housekeeping", 0, False, False),
            ("product_filler", "no-legs", 0, False, False),
            ("product_filler", "instrument", 1, False, True),
            ("diagnostic_filler", "unknown-diagnostic", 0, False, False),
            ("diagnostic_filler", "f0-part-c", 0, False, True),
            ("counted", "prior-pilot", 1, True, True),
            ("counted", "prior-ordinary", 1, False, False),
        ]:
            with self.subTest(kind=kind, name=name):
                history = History()
                self.rows = history.rows
                attempt = history.launch(name, "native", now - 30, kind=kind, legs=legs,
                                         groups=["study"] if kind == "counted" else [], pin=self.entry["pin"])
                if pilot:
                    attempt["registration"]["pilot"] = True
                history.close(attempt, now - 20)
                history.add("GATE", id="freeze-2", passed=True)
                history.add("GATE", id="r1-post-close-check", passed=False)
                history.ready(self.entry["id"], True)
                self.assertEqual(self.decision(resealed=True).get("entry") == self.entry["id"], qualifies)

    def test_nonclean_close_holds_same_kit_without_redundant_stop(self):
        history = History()
        history.rows = self.rows
        now = self.facts["now_epoch"]
        for entry in self.queue["entries"]:
            if entry["kind"].endswith("_filler"):
                history.add("REFUSAL", entry_id=entry["id"], kit_sha256=entry["kit_sha256"],
                            block=None, queue_commit="fixture-commit", epoch=now - 100,
                            reason="fixture refusal")
        failed = history.launch(self.entry["id"], "failed", now - 60, kind="counted",
                                pin=self.entry["pin"], groups=self.entry["params"]["groups"])
        history.close(failed, now - 10, clean=False)
        receipt = next(row for row in self.rows if row["event"] == "RECEIPT" and row["span_id"] == "failed")
        receipt["receipt"]["rc"] = 1
        history.add("STOP", **history.bind(failed), code="NON_CLEAN_CLOSE", epoch=now - 9)
        self.assertEqual(self.decision(resealed=True)["decision"], "QUEUE_EMPTY")
        failed["queue_commit"] = "unregistered-revision"
        self.assertEqual(self.decision(resealed=True)["decision"], "QUEUE_EMPTY")
        self.rows[:] = [row for row in self.rows if not (
            row["event"] == "STOP" and row["span_id"] == "failed")]
        for i, row in enumerate(self.rows, 1):
            row["seq"] = i
        self.assertEqual(self.decision(resealed=True)["decision"], "QUEUE_EMPTY")

        # A matching historical close still holds the kit when the attempt
        # precedes the first CONFIG and no governing change can be verified.
        self.rows[:] = [row for row in self.rows if row["event"] != "CONFIG"]
        openings = {row["span_id"]: i for i, row in enumerate(self.rows, 1) if row["event"] == "LAUNCH"}
        for i, row in enumerate(self.rows, 1):
            row["seq"] = i
            if "open_seq" in row:
                row["open_seq"] = openings[row["span_id"]]
        self.assertEqual(self.decision(resealed=True)["decision"], "QUEUE_EMPTY")

    def test_missing_predecessor_registration_does_not_treat_filler_as_complete(self):
        self.entry["params"]["after"] = ["instrument"]
        result = self.decision(resealed=True)
        self.assertEqual((result["decision"], result["rule"]), ("HALT", "DEPENDENCY_UNKNOWN"))

    def test_v4_pilot_flag_does_not_waive_a_qualified_smoke(self):
        queue, rules, facts, _, v4 = scenario("v4")
        history = History()
        now = facts["now_epoch"]
        maintenance = history.launch("housekeeping", "no-smoke", now - 30, pin=v4["pin"],
                                     kind="maintenance", legs=0)
        history.close(maintenance, now - 20)
        history.add("GATE", id="freeze-2", passed=True)
        history.add("GATE", id="r1-post-close-check", passed=False)
        history.ready("dev-next", False, expected_ready_by=queue["entries"][1]["expected_ready_by"])
        history.ready(v4["id"], True)
        v4["params"]["pilot"] = True
        result = decide(queue, rules, reseal(queue, rules, facts, history.rows), history.rows)
        self.assertNotEqual(result.get("entry"), v4["id"])

    def test_only_a_committed_revision_can_clear_a_refusal(self):
        without_config = self.rows[:-1]
        unchanged_facts = {**self.facts, "ledger_head": head_for(without_config), "config_events": []}
        self.assertEqual(decide(self.queue, self.rules, unchanged_facts, without_config)["rule"],
                         "CONFIG_REVISION")
        f0 = self.queue["entries"][0]
        self.queue["entries"] = [f0]
        history = History()
        history.rows = self.rows
        history.add("GATE", id="r1-post-close-check", passed=False)
        refusal = history.add("REFUSAL", entry_id=f0["id"], kit_sha256=f0["kit_sha256"], block=None,
                              queue_commit=self.facts["queue_commit"], epoch=self.facts["now_epoch"],
                              reason="fixture refusal")
        self.assertEqual(self.decision(resealed=True)["decision"], "QUEUE_EMPTY")
        refusal["queue_commit"] = "unregistered-revision"
        self.assertEqual(self.decision(resealed=True)["decision"], "QUEUE_EMPTY")
        self.facts["queue_commit"] = "fixture-next-commit"
        result = self.decision()
        self.assertEqual((result["decision"], result["rule"]), ("HALT", "CONFIG_REVISION"))
        self.assertEqual(self.decision(resealed=True)["entry"], f0["id"])

    def test_refusal_recorded_before_its_config_still_holds_target_revision(self):
        f0 = self.queue["entries"][0]
        self.queue["entries"] = [f0]
        history = History()
        history.rows = self.rows
        history.add("REFUSAL", entry_id=f0["id"], kit_sha256=f0["kit_sha256"], block=None,
                    queue_commit="next-revision", epoch=self.facts["now_epoch"],
                    reason="fixture refusal")
        self.facts["queue_commit"] = "next-revision"
        self.assertEqual(self.decision(resealed=True)["decision"], "QUEUE_EMPTY")

    def test_f0_requires_positive_evidence_of_retirement_gate_state(self):
        self.queue["entries"] = self.queue["entries"][:1]
        history = History()
        history.rows = self.rows
        history.add("GATE", id="r1-post-close-check", passed=True)
        self.assertEqual(self.decision(resealed=True)["decision"], "QUEUE_EMPTY")
        history.add("GATE", id="r1-post-close-check", passed=False)
        self.assertEqual(self.decision(resealed=True)["decision"], "QUEUE_EMPTY")
        self.rows[:] = [row for row in self.rows if not (
            row["event"] == "GATE" and row["id"] == "r1-post-close-check")]
        for i, row in enumerate(self.rows, 1):
            row["seq"] = i
        result = self.decision(resealed=True)
        self.assertEqual((result["decision"], result["rule"]), ("HALT", "GATE_UNKNOWN"))
        history.add("GATE", id="r1-post-close-check", passed=False)
        self.assertEqual(self.decision(resealed=True)["entry"], "f0-part-c")

    def test_removing_pending_ready_deadline_cannot_make_filler_fit(self):
        queue, rules, facts, rows, short = scenario("short")
        short["worst_case_s"] = 4000
        self.assertEqual(decide(queue, rules, reseal(queue, rules, facts, rows), rows)["rule"], "READY_FIT")
        del queue["entries"][1]["expected_ready_by"]
        result = decide(queue, rules, reseal(queue, rules, facts, rows), rows)
        self.assertEqual((result["decision"], result["rule"]), ("HALT", "READY_DEADLINE_CONFLICT"))
        history = History()
        history.rows = rows
        history.ready("dev-next", False, expected_ready_by=None)
        self.assertEqual(decide(queue, rules, reseal(queue, rules, facts, rows), rows)["entry"], "short")

    def test_copy_stop_must_follow_latest_start_even_with_prior_verification(self):
        history = History()
        self.rows = history.rows
        now = self.facts["now_epoch"]
        smoke = history.launch("instrument", "smoke", now - 1200, pin=self.entry["pin"])
        history.close(smoke, now - 1100)
        history.add("GATE", id="freeze-2", passed=True)
        history.add("GATE", id="r1-post-close-check", passed=False)
        history.ready(self.entry["id"], True)
        self.assertEqual(self.decision(resealed=True)["entry"], self.entry["id"])
        history.add("COPY_STARTED", **history.bind(smoke))
        result = self.decision(resealed=True)
        self.assertEqual((result["decision"], result["rule"]), ("HALT", "UPLOAD_ACTIVE"))
        history.add("UPLOAD_STOPPED", **history.bind(smoke))
        self.assertEqual(self.decision(resealed=True)["entry"], self.entry["id"])
        history.add("COPY_STARTED", **history.bind(smoke))
        self.assertEqual(self.decision(resealed=True)["rule"], "UPLOAD_ACTIVE")
        later = history.launch("instrument", "later-smoke", now - 1000, pin=self.entry["pin"])
        history.close(later, now - 900)
        self.assertEqual(self.decision(resealed=True)["rule"], "UPLOAD_ACTIVE")
        history.add("COPY_VERIFIED", **history.bind(smoke))
        self.assertEqual(self.decision(resealed=True)["entry"], self.entry["id"])

    def test_time_only_mixed_group_omission_still_requires_pinned_item_cap_gate(self):
        self.queue["entries"] = self.queue["entries"][:2]
        self.entry["params"]["legs"] = 6
        self.entry["argv"] = ["fixture-count", "--kit", "dev-04-mixed", "--legs", "6"]
        history = History()
        history.rows = self.rows
        history.add("GATE", id="r1-post-close-check", passed=True)
        self.facts["queue_commit"] = "next-queue-revision"
        self.assertEqual(self.decision(resealed=True)["decision"], "WAIT")
        # The pinned mixed-development item charges its actual six-leg roster.
        self.entry["params"]["groups"].remove("dev-mixed")
        self.assertEqual(self.decision(resealed=True)["entry"], self.entry["id"])

    def test_filler_worst_case_equal_to_ready_deadline_fails(self):
        queue, rules, facts, rows, short = scenario("short")
        self.assertEqual(decide(queue, rules, facts, rows)["entry"], short["id"])
        short["worst_case_s"] = 4000
        reseal(queue, rules, facts, rows)
        result = decide(queue, rules, facts, rows)
        self.assertEqual(result["rule"], "READY_FIT")

    def test_audit_host_facts_and_maintenance_are_fail_closed(self):
        for key, value in (("maintenance_active", True), ("maintenance_active", None),
                           ("disk_free_gib", 59), ("meter_ready", False), ("collector_ready", None),
                           ("power", {"ac": False, "charging": False}), ("power", None),
                           ("owner_stop", None), ("maintenance_marker", "/fixture/alternate")):
            with self.subTest(key=key, value=value):
                self.assertNotEqual(decide(self.queue, self.rules, {**self.facts, key: value}, self.rows)["decision"],
                                    "LAUNCH")
        changed = dict(self.facts)
        changed.pop("maintenance_active")
        self.assertEqual(decide(self.queue, self.rules, changed, self.rows)["rule"], "OWNER_FACT")

    def test_subsecond_close_and_no_retired_gap(self):
        now = self.facts["now_epoch"]
        history = History()
        history.rows = self.rows
        last = history.launch("instrument", "inst-last", now - 10, pin=self.entry["pin"])
        history.close(last, now - 0.125)
        self.assertEqual(self.decision(resealed=True)["entry"], "dev-next")
        self.assertEqual(self.decision(now=now - 0.250)["rule"], "CLOCK_ROLLBACK")


class CLITests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.dir = Path(temporary.name)
        self.queue, self.rules, self.facts, self.rows, self.entry = scenario("counted")
        self.ledger = self.dir / "attempts.jsonl"
        self.head = self.dir / "attempts.jsonl.head.json"

    def call(self, *args, status=0):
        output, errors = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(output), contextlib.redirect_stderr(errors):
            observed = sched.main(list(map(str, args)))
        self.assertEqual(observed, status, errors.getvalue())
        return output.getvalue(), errors.getvalue()

    def inputs(self):
        for name in ("queue", "rules", "facts"):
            write(self.dir / f"{name}.json", getattr(self, name))
        write(self.head, head_for(self.rows))
        self.ledger.write_bytes(b"".join(encoded(row) + b"\n" for row in self.rows))
        return ("--queue", self.dir / "queue.json", "--rules", self.dir / "rules.json",
                "--facts", self.dir / "facts.json", "--ledger", self.ledger)

    def test_next_explain_and_report_share_committed_decision(self):
        args = self.inputs()
        observed, _ = self.call("next", *args, "--record", self.dir / "decisions.jsonl")
        self.assertEqual(json.loads(observed)["entry"], "dev-next")
        self.assertEqual(json.loads(self.call("explain", *args, "--json")[0])["decision"], json.loads(observed))
        self.assertEqual(self.call("next", *args)[0], observed)
        self.assertEqual(json.loads(self.call("next", *args[:-2])[0])["rule"], "LEDGER_MISSING")
        self.head.unlink()
        self.assertEqual(json.loads(self.call("next", *args)[0])["rule"], "LEDGER_HEAD_INVALID")
        output, _ = self.call("report", "--ledger", self.dir / "decisions.jsonl",
                              "--since", "2026-11-18T00:00:00-08:00")
        self.assertIn("Hours by decision", output)

    def test_cli_rejects_duplicate_keys_nonfinite_numbers_and_numeric_booleans(self):
        args = self.inputs()
        for payload in ('{"now_epoch":0,"now_epoch":1}', '{"now_epoch":NaN}', '{"now_epoch":true}'):
            (self.dir / "facts.json").write_text(payload, encoding="utf-8")
            self.assertEqual(json.loads(self.call("next", *args)[0])["decision"], "HALT")

    def test_validate_rejects_missing_standing_filler_including_implicit_block_dependency(self):
        for extra in ({"done": True}, {"kind": "maintenance"}, {"block": "pair"},
                      {"params": {"window": {"earliest_epoch": epoch(19),
                                             "latest_epoch": epoch(19, 23, 59, 59)}}},
                      {"requires": ["registered-window"]}):
            with self.subTest(extra=extra):
                self.queue["entries"] = [
                    {**self.entry, "block": "pair"}, {**self.queue["entries"][0], **extra},
                ]
                args = self.inputs()
                _, errors = self.call("validate", *args[:4], status=2)
                self.assertIn("NO_STANDING_FILLER", errors)

    def fixture_probe(self, args, out):
        real_lstat = Path.lstat
        marker = self.dir / "missing-marker"

        def lstat(path):
            return real_lstat(marker if str(path) == sched.MAINTENANCE_PATH else path)

        with patch.object(sched.subprocess, "run", side_effect=probe_child), patch.object(
                sched.time, "time", return_value=self.facts["now_epoch"]), patch.object(Path, "lstat", lstat):
            self.call("probe", *args[:4], "--ledger", self.ledger, "--host-facts", self.dir / "facts.json",
                      "--out", out, "--caller-pid", 10, "--run-plans")
        return json.loads(out.read_text())

    def test_prior_filler_with_same_id_and_kit_does_not_complete_ready_counted_work(self):
        entry = self.entry
        entry["kit_sha256"] = "c" * 64
        self.queue["admitted"].append({"pin": entry["pin"], "kit_sha256": entry["kit_sha256"]})
        older_queue = deepcopy(self.queue)
        old_entry = older_queue["entries"][1]
        old_entry.update(kind="product_filler", params={"groups": entry["params"]["groups"], "legs": 1},
                         requires=["pin-admitted", "launcher-admits"])
        history = History()
        self.rows = history.rows
        history.add("CONFIG", queue_commit="older", queue_digest=digest(older_queue),
                    rules_digest=digest(self.rules))
        now = self.facts["now_epoch"]
        prior = history.launch(entry["id"], "old-filler", now - 200, pin=entry["pin"],
                               kind="product_filler", groups=entry["params"]["groups"],
                               kit_sha256=entry["kit_sha256"])
        prior["queue_commit"] = "older"
        history.close(prior, now - 130, clean=False)
        smoke = history.launch("instrument", "pin-smoke", now - 120, pin=entry["pin"])
        smoke["queue_commit"] = "older"
        history.close(smoke, now - 80)
        history.add("GATE", id="freeze-2", passed=True)
        history.add("GATE", id="r1-post-close-check", passed=False)
        history.ready(entry["id"], True)
        close = next(row for row in self.rows if row["event"] == "CLOSE" and row["span_id"] == "old-filler")
        for clean in (False, True):
            with self.subTest(clean=clean):
                close["clean"] = clean
                reseal(self.queue, self.rules, self.facts, self.rows)
                args = self.inputs()
                out = self.dir / "priority-probe.json"
                observed = self.fixture_probe(args, out)
                self.assertEqual(observed["plans"][entry["id"]]["rc"], 0)
                command = (*args[:4], "--ledger", self.ledger, "--facts", out)
                result = json.loads(self.call("next", *command)[0])
                self.assertEqual(result["entry"], entry["id"])
                self.assertEqual(json.loads(self.call("explain", "--json", *command)[0])["decision"], result)

        completed = history.launch(entry["id"], "actual-counted", now - 40, kind="counted",
                                   pin=entry["pin"], kit_sha256=entry["kit_sha256"],
                                   groups=entry["params"]["groups"])
        history.close(completed, now - 20)
        entry["pin"] = entry["pin"].upper()
        entry["kit_sha256"] = entry["kit_sha256"].upper()
        reseal(self.queue, self.rules, self.facts, self.rows)
        args = self.inputs()
        out = self.dir / "completion-probe.json"
        self.assertNotIn(entry["id"], self.fixture_probe(args, out)["plans"])
        report = json.loads(self.call("explain", "--json", *args[:4], "--ledger", self.ledger,
                                      "--facts", out)[0])
        self.assertEqual(next(row["status"] for row in report["entries"] if row["id"] == entry["id"]), "DONE")

    def test_time_only_cached_meter_observation_remains_subject_to_pinned_poll(self):
        self.facts["errors"] = {"meter_ready": "fixture polling error behind cached success"}
        args = self.inputs()
        self.assertEqual(json.loads(self.call("next", *args)[0])["rule"], "PROBE_FAILED")
        for ready in (False, True):
            with self.subTest(ready=ready):
                self.facts["meter_ready"] = ready
                args = self.inputs()
                out = self.dir / "meter-probe.json"
                observed = self.fixture_probe(args, out)
                self.assertEqual(observed["errors"], {})
                result = json.loads(self.call("next", *args[:4], "--ledger", self.ledger, "--facts", out)[0])
                if ready:
                    self.assertEqual(result["entry"], self.entry["id"])
                else:
                    self.assertEqual(result["rule"], "host-meter")

    def test_probe_binds_writer_revision_and_dry_run_to_committed_head(self):
        args = self.inputs()
        out = self.dir / "probe.json"
        real_lstat = Path.lstat
        missing_marker = self.dir / "missing-marker"

        def lstat(path):
            return real_lstat(missing_marker if str(path) == sched.MAINTENANCE_PATH else path)

        with patch.object(sched.subprocess, "run", side_effect=probe_child) as commands, patch.object(
                sched.time, "time", return_value=self.facts["now_epoch"]), patch.object(Path, "lstat", lstat):
            probe_opts = (*args[:4], "--ledger", self.ledger, "--host-facts", self.dir / "facts.json",
                          "--out", out, "--caller-pid", 10, "--run-plans")
            self.call("probe", *probe_opts)
            observed = json.loads(out.read_text())
            self.assertEqual(observed["queue_commit"], self.facts["queue_commit"])
            self.assertEqual(observed["ledger_head"], head_for(self.rows))
            self.assertEqual(len(commands.call_args_list), 7)
            result, _ = self.call("next", *args[:4], "--ledger", self.ledger, "--facts", out)
            self.assertEqual(json.loads(result)["entry"], "dev-next")
            self.call("probe", *probe_opts, "--queue-commit", "wrong-revision", status=3)
            self.assertIsNone(json.loads(out.read_text())["ledger_head"])

    def test_probe_keeps_allowlisted_receipt_fields_and_reads_registered_marker(self):
        args = self.inputs()
        out = self.dir / "probe.json"
        root = self.dir / "receipts"
        root.mkdir()
        rec = json.loads((FIXTURES / "runner_receipt.json").read_text())
        write(root / "runner_receipt.json", rec)
        marker = self.dir / "active"
        marker.touch()
        real_lstat = Path.lstat
        with patch.object(sched.subprocess, "run", side_effect=probe_child) as commands, patch.object(
                sched.time, "time", return_value=epoch()), patch.object(
                    Path, "lstat", lambda p: real_lstat(marker if str(p) == sched.MAINTENANCE_PATH else p)):
            self.call("probe", *args[:4], "--host-facts", self.dir / "facts.json",
                      "--out", out, "--caller-pid", 10, "--receipt-root", root,
                      "--maintenance-marker", self.dir / "alternate")
            calls = [call.args[0] for call in commands.call_args_list]
            first = out.read_bytes()
            self.assertTrue(json.loads(first)["maintenance_active"])
            self.assertNotIn(b"SENTINEL", first)
            for section in (rec, rec["started"], rec["ended"], rec["span_result"],
                            rec["span_result"]["steps"][0]):
                section["unread"] += 1000
            write(root / "runner_receipt.json", rec)
            self.call("probe", *args[:4], "--host-facts", self.dir / "facts.json",
                      "--out", out, "--caller-pid", 10, "--receipt-root", root,
                      "--maintenance-marker", self.dir / "alternate")
            self.assertEqual(out.read_bytes(), first)
        self.assertEqual(calls, [
            ["/usr/bin/pmset", "-g", "batt"], ["/bin/df", "-g", "/"], ["/bin/launchctl", "list"],
            ["/bin/ps", "-axo", "pid,ppid,comm"], ["/usr/sbin/sysctl", "-n", "kern.boottime"],
        ])


if __name__ == "__main__":
    unittest.main()
