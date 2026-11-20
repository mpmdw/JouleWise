"""RL-193 §§4–5. Invented records, device observations and Git books only."""
import json
from pathlib import Path
import re
import subprocess
import tempfile
import unittest

import test_desc_looks_acceptance as f
import test_desc_looks_rl190 as r


def git(world, *args):
    return subprocess.check_output(["git", "-C", world.repo, *args])


def committed(world, commit, path):
    return git(world, "show", f"{commit}:{path}")


class TwoWitnesses(r.AsRun):
    """One typed decision with independently committed queue and ended-span evidence."""
    def drop(self, key, row):
        super().drop(key, row)
        target = self.repo / row["drop"]
        declaration = f.read(target)
        reason = declaration["reason"]
        kit, leg = key.split("/")
        alternate = kit + "/L012"
        evidence = {
            "queue": {"queue_id": "invented-Q", "final": True, "unrun": [key]},
            "receipt": {"span_id": r.LOCATION[key][0], "closed": True, "kit_id": kit,
                        "kit_sha256": f.sha((self.repo / "kits" / (kit + ".json")).read_bytes()),
                        "member_legs": [], "unrun": [key]},
        }
        if self.conflict:
            evidence[self.conflict]["unrun"] = [alternate]
        statements = []
        for role, record in evidence.items():
            name = f"ops/drop-evidence/{role}.json"
            declaration[role] = name
            f.put(self.repo / name, record)
            statement = r.typed_item(key, reason, name, f.sha(f.wire(record)))
            statements.append(statement if role == "queue" else statement.splitlines(keepends=True)[-1])
        f.put(self.repo / "RUN_STATE.md", b"".join(statements))
        f.put(target, declaration)


class RL193(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.base = Path(temp.name).resolve()
        self.serial = 0

    def folder(self):
        self.serial += 1
        return self.base / str(self.serial)

    def world(self, **kwargs):
        return r.AsRun(self.folder(), **kwargs)

    def test_sq2_never_issued_key_has_no_artifact_or_reservation(self):
        w = self.world(scenario="pending")
        kit, leg = r.SOLO.split("/")
        for path in (w.repo / "ops").glob("*/issue.json"):
            issue = json.loads(committed(w, w.receipts, path.relative_to(w.repo)))
            self.assertFalse(issue["kit_id"] == kit and leg in issue["legs"])
        self.assertFalse(any(row.get("receipt") for row in w.rows if row["key"] == r.SOLO))
        self.assertFalse((w.repo / "drops" / (r.SOLO + ".json")).exists())
        self.assertEqual(r.stage(self, self.world())["counts"]["n_legs"], 35)
        r.pending_refuses(self, w)

    def dual_drop(self, conflict):
        class Evidence(TwoWitnesses):
            pass
        Evidence.conflict = conflict
        w = Evidence(self.folder(), scenario="drop", defect="queue")
        declaration = f.read(w.repo / ("drops/" + r.SOLO + ".json"))
        for role in ("queue", "receipt"):
            payload = committed(w, w.receipts, declaration[role])
            self.assertIn(f.sha(payload).encode(), committed(w, w.receipts, "RUN_STATE.md"))
            self.assertEqual(r.SOLO in json.loads(payload)["unrun"], role != conflict)
        return w

    def test_sq3_queue_and_receipt_agree(self):
        doc = r.stage(self, self.dual_drop(None))
        self.assertEqual(doc["positions"][r.SOLO]["disposition"], "dropped:queue_retired")
        self.assertEqual(doc["counts"]["n_legs"], 34)

    def conflicting_drop(self, conflict):
        # A blanket refusal of every two-witness record fails the positive control.
        with self.subTest(control="agree"):
            r.stage(self, self.dual_drop(None))
        with self.subTest(conflict=conflict):
            r.stage(self, self.dual_drop(conflict), allowed=False)

    def test_sq3_queue_disagrees_with_receipt(self):
        self.conflicting_drop("queue")

    def test_sq3_receipt_disagrees_with_queue(self):
        self.conflicting_drop("receipt")

    def test_legacy_undocumented_drop_authority_refuses(self):
        class Bare(r.AsRun):
            def drop(self, key, row):
                super().drop(key, row)
                f.put(self.repo / row["drop"], {"key": key, "status": "dropped",
                                                "authority": "fixture desk decision"})
                (self.repo / "RUN_STATE.md").unlink()
                (self.repo / "ops/drop-evidence/queue.json").unlink()
        r.stage(self, self.world(scenario="drop", defect="queue"))
        r.stage(self, Bare(self.folder(), scenario="drop", defect="queue"), allowed=False)

    def test_legacy_bare_drop_invalid_in_committed_schema(self):
        from jsonschema.validators import validator_for
        w = self.world(scenario="drop", defect="queue")
        row = r.stage(self, w)["positions"][r.SOLO]
        schema = f.read(w.targets["pin_stage1_schema"])
        validator = validator_for(schema)(dict(schema["properties"]["positions"], **{"$defs": schema["$defs"]}))
        self.assertTrue(validator.is_valid({r.SOLO: row}))
        self.assertFalse(validator.is_valid({r.SOLO: dict(row, disposition="dropped")}))

    def test_sq4_index_matches_its_documented_basis_for_every_span(self):
        w = self.world()
        doc = r.stage(self, w)
        schema = f.read(w.targets["pin_stage1_schema"])
        # Read the documentation of the observed integer, allowing either origin and any name.
        def definitions(obj, field):
            if isinstance(obj, dict):
                prop = obj.get("properties", {}).get(field)
                if isinstance(prop, dict):
                    yield prop
                for child in obj.values():
                    yield from definitions(child, field)
            if isinstance(obj, list):
                for child in obj:
                    yield from definitions(child, field)
        r.check_span_ids(self, doc)
        for path, origin in r.numeric_paths(doc["positions"][r.KEYS[0]]):
            if not all(dict(r.numeric_paths(doc["positions"][k])).get(path) == origin + i
                       for k, (span, i) in r.LOCATION.items()):
                continue
            for prop in definitions(schema, path[-1]):
                words = (prop.get("description", "") + " " + prop.get("title", "")).lower()
                labels = ("zero", "0") if origin == 0 else ("one", "1") if origin == 1 else (str(origin),)
                if (prop.get("minimum") == origin or
                        any(re.search(rf"\b{label}[- ]based\b|\bstarts? (?:at|from) {label}\b", words)
                            for label in labels)):
                    return
        self.fail("no schema-documented basis agrees with the receipt-local positions")

    def test_sq4_own_reference_for_recut_first(self):
        r.own_reference(self, r.SOLO)

    def test_sq4_borrowed_reference_for_second(self):
        r.own_reference(self, r.KEYS[1])

    def binding_graph(self, placement, binding="valid"):
        # Obtain genuine census bytes, then build two identical cuts differing in Git timing.
        # The new first parent has the authentic receipt collection and has no final manifest.
        w = self.world(late=True)
        doc = r.stage(self, w)
        stage_name = w.stage.relative_to(w.repo).as_posix()
        manifest_name = w.man.relative_to(w.repo).as_posix()
        payload = w.stage.read_bytes()
        w.stage.unlink()
        w.ledger.unlink()
        w.book.head = w.receipts
        self.assertFalse(f.git_ok(w.repo, "cat-file", "-e", f"{w.receipts}:{manifest_name}"))
        if placement == "proper":
            registration = w.book.seal("final manifest precedes first stage-one artifact")
            self.assertFalse(f.git_ok(w.repo, "cat-file", "-e", f"{registration}:{stage_name}"))
        f.put(w.stage, payload if binding != "wrong_bytes" else b'{}\n')
        artifact = w.book.seal("introduce stage-one artifact")
        if placement == "same":
            registration = artifact
        self.assertEqual(committed(w, registration, manifest_name), w.man.read_bytes())
        self.assertEqual(f.git_ok(w.repo, "merge-base", "--is-ancestor", registration, artifact), True)
        self.assertEqual(registration == artifact, placement == "same")
        named = artifact
        if binding == "sibling":
            w.book.head = registration
            named = w.book.seal("identical stage-one artifact on a sibling")
            w.book.head = artifact
            self.assertFalse(f.git_ok(w.repo, "merge-base", "--is-ancestor", named, artifact))
        if binding == "no_artifact":
            named = registration
        f.put(w.stage, payload)
        w.manifest_registration = registration
        w.row.update(status="stage1_committed", stage1_path=stage_name, stage1_sha256=f.sha(payload),
                     stage1_commit=named)
        if binding == "omitted":
            del w.row["stage1_commit"]
        w.save_row()
        ledger_commit = w.book.seal("introduce stage1_committed row after its artifact")
        row = json.loads(committed(w, ledger_commit, "LOOKS.json"))["looks"][0]
        self.assertFalse(f.git_ok(w.repo, "cat-file", "-e", f"{artifact}:LOOKS.json"))
        self.assertEqual(row["execution_host"], r.HOST)
        self.assertNotEqual(ledger_commit, artifact)
        w.book.seal("unrelated later public note")
        return w, doc, ledger_commit, artifact

    def test_sq5_proper_manifest_ancestor(self):
        w, _, _, _ = self.binding_graph("proper")
        r.at_reservation(self, w, reached=True)

    def test_sq5_manifest_and_stage1_artifact_same_commit_refuses(self):
        with self.subTest(control="proper"):
            w, _, _, _ = self.binding_graph("proper")
            r.at_reservation(self, w, reached=True)
        with self.subTest(placement="same"):
            w, _, _, _ = self.binding_graph("same")
            r.at_reservation(self, w, reached=False)

    def test_sq7_artifact_named_and_ledger_commit_resolved_from_history(self):
        w, doc, ledger_commit, artifact = self.binding_graph("proper")
        self.assertEqual(w.row["stage1_commit"], artifact)
        self.assertTrue(f.git_ok(w.repo, "merge-base", "--is-ancestor", artifact, ledger_commit))
        candidate = self.base / "candidate.json"
        for oid in (ledger_commit, artifact, w.book.head):
            with self.subTest(commit=oid), r.device(boundary=True):
                f.put(candidate, dict(look_id=w.look, manifest_sha256=w.row["sha256"], commit=oid,
                                      stage1_sha256=w.row["stage1_sha256"], **doc["counts"]))
                rc, _, _, events = f.invoke(w, "validate-public", "--candidate", str(candidate))
                self.assertEqual(rc, 0 if oid == ledger_commit else 2)
                self.assertFalse([e for e in events if e[0] in ("open", "reservation_attempt")])

    def invalid_artifact(self, mode):
        with self.subTest(control="valid"):
            w, _, _, _ = self.binding_graph("proper")
            r.at_reservation(self, w, reached=True)
        with self.subTest(binding=mode):
            w, _, _, _ = self.binding_graph("proper", mode)
            r.at_reservation(self, w, reached=False)

    def test_sq8_per_kit_totals_and_reason_subcounts(self):
        w = self.world(scenario="drop", defect="queue")
        doc = r.stage(self, w)
        for kit, summary in doc["by_kit"].items():
            with self.subTest(kit=kit, check="exact_disposition_categories"):
                buckets = summary.get("counts", summary)
                names = set(buckets)
                if buckets is summary:
                    names.discard("reasons")  # Permitted sibling table of reason subcounts.
                self.assertEqual(names, {"qualified", "not_qualified", "dropped"})
        qualified = {"qualified": 12}
        # Independent of the emitted positions and the machine's totals.
        f.check_category_counts(self, doc, {"f2-inst-01": {"qualified": 11, "dropped:queue_retired": 1},
                                            "f2-inst-02": {"qualified": 11, "not_qualified:loaded": 1},
                                            "f2-inst-03": qualified})

    def wall_case(self, stopped, limit):
        class Timed(r.AsRun):
            def group_members(world):
                super().group_members()
                target = next(row for row in world.rows if row["key"] == r.SOLO)
                path = world.repo / target["leg_record"]
                op = f.read(path)
                kit = f.read(world.repo / "kits/f2-inst-01.json")["span_template"]
                allowance, stop = kit["leg_budget_s"], kit["leg_worst_case_s"]
                wall = {"budget": allowance, "below_stop": stop-1, "at_stop": stop, "above_stop": stop+1}[limit]
                op.update(leg_status="stopped" if stopped else "complete", wall_s=wall, over_time_budget=wall>allowance)
                f.put(path, op)
                world.planted = op
        w = Timed(self.folder(), scenario="wall", defect="status" if stopped else "none")
        doc = r.stage(self, w)
        row = doc["positions"][r.SOLO]
        self.assertEqual(row["reasons"], ["incomplete"] if stopped else [])
        self.assertEqual(row["disposition"], "not_qualified:incomplete" if stopped else "qualified")
        self.assertIs(row["over_time_budget"], w.planted["over_time_budget"])
        self.assertEqual(doc["counts"]["n_legs"], 34 if stopped else 35)

    def test_b1_coverage_and_wall_excluded_from_stage1(self):
        class NoCoverage(f.World):
            def leg(world, *args):
                refs = super().leg(*args)
                if args[4] == 1:
                    path = world.repo / refs["leg_record"]
                    op = f.read(path)
                    op.update(wall_s=10 * op["leg_budget_s"], over_time_budget=True)
                    f.put(path, op)
                    world.target = refs["key"]
                    for filename in ("power_trace.csv", "dc_points.csv"):
                        trace = world.copy / world.target / filename
                        f.put(trace, trace.read_bytes().splitlines(keepends=True)[0])
                return refs
        w = NoCoverage(self.folder(), f.IDS[0])
        doc = r.stage(self, w)
        self.assertEqual(doc["counts"]["n_legs"], 2)
        row = doc["positions"][w.target]
        self.assertEqual((row["disposition"], row["reasons"]), ("qualified", []))
        self.assertIs(row["over_time_budget"], True)


def case(function, *args):
    def method(self):
        function(self, *args)
    return method


for mode in ("omitted", "no_artifact", "wrong_bytes", "sibling"):
    setattr(RL193, "test_sq7_refuse_" + mode, case(RL193.invalid_artifact, mode))
for stopped in (False, True):
    for limit in ("budget", "below_stop", "at_stop", "above_stop"):
        setattr(RL193, "test_sq9_" + ("stopped_" if stopped else "complete_") + limit,
                case(RL193.wall_case, stopped, limit))


def projection_record(test, omitted):
    """SQ6 normalized record contract. The lead owns the producer and public wire mapping."""
    w = test.world(late=True)
    proof = f.read(w.targets["cold"])
    evidence = proof["bindings"]["host_rehearsal"]
    rehearsal = json.loads(committed(w, w.book.head, evidence["path"]))
    expected_spans = {}
    for span, keys in r.GROUPS.items():
        receipt = next(row["receipt"] for row in w.rows if row["key"] == keys[0])
        close = json.loads(committed(w, w.receipts, receipt))["close_epoch_s"]
        check = json.loads(committed(w, w.receipts, f"checks/{span}.json"))
        expected_spans[span] = dict(close_epoch_s=close, registration_commit=w.reg,
                                    projection_commit=w.receipts, offload_manifest_sha256=check["offload_manifest_sha256"])
    book = f.Book(test.folder() / "projection-book")
    # Only normalized, typed facts cross the synthetic producer/consumer boundary.
    # No public CLI, private-read permission, or production row spelling is assumed here.
    rows = {"spans": w.row["spans"], "cold": {key:proof[key] for key in
             ("ruling", "bindings", "dropped", "not_qualified")}, "rehearsal": rehearsal}
    if omitted == "one_span":
        rows["spans"] = dict(rows["spans"])
        del rows["spans"][next(iter(expected_spans))]
    elif omitted:
        del rows[omitted]
    f.put(book.path / "observations.json", rows)
    book.seal("publish invented verified typed observations")
    observed = r.main_record(book, "observations.json")
    test.assertEqual(subprocess.check_output(["git", "-C", book.path, "ls-tree", "--name-only", "HEAD"]),
                     b"observations.json\n")
    pins = f.read(w.man)["code_pins"]
    artifacts = {pin["path"]: f.sha(committed(w, w.reg, pin["path"]))
                 for pin in pins.values() if pin["path"].endswith(".py")}
    accepted = (r.ledger_agrees(observed.get("spans", {}), expected_spans)
                and r.cold_record_agrees(observed.get("cold", {}), "RL-900002", proof["bindings"],
                                         {}, {r.LOADED: "loaded"})
                and r.rehearsal_covers(observed.get("rehearsal", {}), r.HOST, f.sha(f.wire(artifacts))))
    test.assertEqual(accepted, omitted is None)


for missing in (None, "spans", "one_span", "cold", "rehearsal"):
    setattr(RL193, "test_sq6_typed_projection_" + ("complete" if missing is None else "absent_"+missing),
            case(projection_record, missing))


def consume_projection_without_ruling(test):
    class Projected(r.AsRun):
        def cold_evidence(world):
            attested = super().cold_evidence()
            # The producer saw the original. The executor receives the verified projection only.
            raw_ruling = world.repo / attested["ruling_path"]
            test.assertEqual(f.sha(raw_ruling.read_bytes()), attested["ruling_sha256"])
            raw_ruling.unlink()
            return attested
    w = Projected(test.folder())
    original = f.read(w.targets["cold"])["ruling_path"]
    test.assertFalse(f.git_ok(w.repo, "cat-file", "-e", "HEAD:"+original))
    test.assertEqual(r.stage(test, w)["counts"]["n_legs"], 35)
RL193.test_sq6_consume_verified_cold_projection_without_ruling_prose = consume_projection_without_ruling


def identical_hardware(test):
    r.host_id(test, (r.UUID, r.UUID), True)
RL193.test_hardware_identical_lines_one_value = identical_hardware


def rehearsal_change(test, role):
    w = test.world()
    pins = f.read(w.man)["code_pins"]
    paths = {pin["path"] for pin in pins.values() if pin["path"].endswith(".py")}
    proof = f.read(w.targets["cold"])["bindings"]["host_rehearsal"]
    evidence = json.loads(committed(w, w.book.head, proof["path"]))
    def at(commit):
        return f.sha(f.wire({path:f.sha(committed(w, commit, path)) for path in paths}))
    before = w.book.head
    test.assertTrue(r.rehearsal_covers(evidence, r.HOST, at(before)))
    if role == "documentation":
        f.put(w.repo / "desk/record.md", b"Lead: pinned executor code unchanged; same host and rehearsal.\n")
    else:
        path = w.repo / pins[role]["path"]
        f.put(path, path.read_bytes() + b"\n# invented revision of a pinned code path\n")
    after = w.book.seal("record a later revision")
    test.assertNotEqual(before, after)
    test.assertEqual(r.rehearsal_covers(evidence, r.HOST, at(after)), role == "documentation")


for changed in ("documentation", "reader", "validator", "schema_validator"):
    setattr(RL193, "test_rehearsal_content_" + changed, case(rehearsal_change, changed))


if __name__ == "__main__":
    unittest.main()
