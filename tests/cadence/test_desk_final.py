"""Desk-final from the automatic table (RL-172 section (c), Sol's conditions): every condition refuses
finality with a named stop. Synthetic mock spans only (the runner's ``mock``); no real kit, custody, energy,
power or meter-sample file is opened."""
from __future__ import annotations

import io
import json
import os
from pathlib import Path
import shutil
import tempfile
import unittest
from contextlib import redirect_stdout
from unittest import mock

from joulewise.cadence import desk, desk_final, kit as kitmod
from joulewise.cadence.stops import evaluate_named_stops
from scripts import cadence_legs_runner as runner
from scripts.air import cadence_desk as cli
from tests.cadence.test_kit_v11 import local
from tests.cadence.test_span_reference import span_kit

TMP = os.environ.get("TMPDIR")
QUEUE_ID, KIT_PATH = "cq-df-1", "docs/process/cadence/kits/cl-test-11.json"


def codes(verdict):
    return sorted({s["code"] for s in verdict["named_stops"]} | {s["code"] for s in verdict["pending"]})


class Fixture:
    """One synthetic kit file, a queue of two six-leg spans, and mock span outputs to pack."""

    def __init__(self, root):
        self.root = Path(root)
        self.kit = span_kit(legs_per_span=6)
        self.kit_path = self.root / "kit.json"
        self.kit_path.write_text(json.dumps(self.kit, indent=1))
        _, self.sha = kitmod.load_kit(self.kit_path)
        self.ids = [leg["leg_id"] for leg in self.kit["legs"]]
        self.spans = {}

    def queue(self, rosters=None, sha=None):
        rosters = rosters or [self.ids[:6], self.ids[6:12]]
        return {"schema": "joulewise.cadence_queue.v1", "queue_id": QUEUE_ID,
                "expires_at": "2026-12-31T00:00:00-08:00", "halt": None, "standing_notice": None,
                "spans": [{"seq": i + 1, "span_id": f"df-s{i + 1:02d}", "block_id": "df-dev",
                           "kit": {"path": KIT_PATH, "sha256": sha or self.sha}, "legs": roster, "attempt": 1,
                           "not_before": "2026-11-17"} for i, roster in enumerate(rosters)]}

    def identity(self, **kw):
        return {"path": KIT_PATH, "sha256": self.sha, "campaign_id": self.kit["campaign_id"],
                "frozen_commit": self.kit["frozen"]["commit"], **kw}

    def span(self, name, legs, **kw):
        if name not in self.spans:
            out = self.root / "spans" / name
            rc, _, _, _ = runner.run_mock(kit=self.kit, kit_sha256=kw.pop("kit_sha256", self.sha), output=out,
                                          t0_epoch=local("2026-11-17T03:00"), windows=[], leg_ids=legs, **kw)
            assert rc == 0, name
            self.spans[name] = out
        return self.spans[name]

    def history(self):
        return [{"kit_schema": self.kit["schema"], "leg_keys": sorted(desk.LEG_SUMMARY_KEYS), "legs": []}]


def remanifest(bundle):
    """Re-hash every file into the manifest (an authenticated but wrong bundle). Returns the new anchor."""
    bundle = Path(bundle)
    manifest = json.loads((bundle / desk_final.MANIFEST_NAME).read_text())
    files = {}
    for path in sorted(bundle.rglob("*")):
        rel = path.relative_to(bundle).as_posix()
        if path.is_file() and rel != desk_final.MANIFEST_NAME:
            files[rel] = desk_final.sha256_bytes(path.read_bytes())
    manifest["files"] = files
    manifest["receipt"]["sha256"] = files.get(desk_final.RECEIPT_NAME)
    raw = (json.dumps(manifest, indent=1, sort_keys=True) + "\n").encode()
    (bundle / desk_final.MANIFEST_NAME).write_bytes(raw)
    return desk_final.sha256_bytes(raw)


def edit_json(path, change):
    doc = json.loads(Path(path).read_text())
    change(doc)
    Path(path).write_text(json.dumps(doc, indent=1, sort_keys=True) + "\n")


class DeskFinalCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory(dir=TMP)
        cls.fx = Fixture(cls.tmp.name)
        cls.clean = cls.fx.span("clean", cls.fx.ids[:6])

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def work(self):
        tmp = tempfile.TemporaryDirectory(dir=TMP)
        self.addCleanup(tmp.cleanup)
        return Path(tmp.name)

    def pack(self, span=None, *, seq=1, kit=None, **kw):
        work = self.work()
        bundle = work / "bundle"
        anchor = desk_final.pack_bundle(span or self.clean, bundle, plan_id=f"cq-df-s{seq:02d}-a1", queue_id=QUEUE_ID,
                                        span_id=f"df-s{seq:02d}", attempt=1, kit=kit or self.fx.identity(), **kw)
        return work, bundle, anchor

    def judge(self, work, bundle, anchor, *, seq=1, queue=None, history="default", allow_mock=True, **kw):
        qp = work / "QUEUE.json"
        qp.write_text(json.dumps(queue or self.fx.queue()))
        return desk_final.judge_span(plan_id=f"cq-df-s{seq:02d}-a1", bundle_dir=bundle, manifest_sha256=anchor,
                                     queue_path=qp, kit_path=kw.pop("kit_path", self.fx.kit_path),
                                     out_dir=work / "out", history=self.fx.history() if history == "default" else history,
                                     allow_mock=allow_mock, **kw)

    def assertNotFinal(self, verdict, code):
        self.assertFalse(verdict["desk_final"], verdict["reasons"])
        self.assertIn(code, codes(verdict))
        self.assertTrue(desk_final.verify_verdict(verdict))
        self.assertTrue(any(r.startswith(code) for r in verdict["reasons"]), verdict["reasons"])


class CleanSpan(DeskFinalCase):
    def test_a_clean_authenticated_span_is_desk_final(self):
        work, bundle, anchor = self.pack()
        verdict = self.judge(work, bundle, anchor)
        self.assertTrue(verdict["desk_final"], verdict["reasons"])
        self.assertEqual((verdict["named_stops"], verdict["pending"], verdict["next_arm_hold"]), ([], [], False))
        self.assertEqual(verdict["identities"]["manifest_sha256"], anchor)
        self.assertEqual(verdict["identities"]["kit_sha256"], self.fx.sha)
        self.assertEqual(verdict["identities"]["capture_leg"], "L001")
        on_disk = json.loads((work / "out" / desk_final.VERDICT_NAME).read_text())
        self.assertEqual(on_disk, verdict)
        self.assertTrue(desk_final.verify_verdict(on_disk))
        self.assertFalse(desk_final.verify_verdict({**on_disk, "desk_final": False}))
        for name in ("JOURNAL-TABLE.md", "desk_summary.json", "stops.json"):
            self.assertTrue((work / "out" / name).is_file(), name)
        summary = json.loads((work / "out/desk_summary.json").read_text())
        self.assertEqual([r["leg_id"] for r in summary["legs"]], self.fx.ids[:6])
        self.assertEqual(set(summary["feeds"]), set(desk_final.EXPECTED_FEEDS))
        self.assertTrue(set(verdict["opened"]) <= desk_final.ALLOWED_BASENAMES)
        self.assertIn("**desk_final: true**", (work / "out/JOURNAL-TABLE.md").read_text())

    def test_operational_stops_hold_the_arm_but_do_not_unmake_finality(self):
        # LEG_OVERTIME needs two legs over 1.5 x budget: an authenticated record of a slow span is final.
        work, bundle, anchor = self.pack()
        for leg_id in ("L002", "L003"):
            def slow(doc):
                doc["wall_s"] = doc["budget_s"] * 2
            edit_json(bundle / f"legs/{leg_id}/leg_summary.json", slow)
            edit_json(bundle / desk_final.RECEIPT_NAME,
                      lambda r, i=leg_id: [slow(leg["summary"]) for leg in r["legs"] if leg["leg_id"] == i])
        verdict = self.judge(work, bundle, remanifest(bundle))
        self.assertEqual(codes(verdict), ["LEG_OVERTIME"])
        self.assertTrue(verdict["desk_final"], verdict["reasons"])
        self.assertTrue(verdict["next_arm_hold"])
        self.assertEqual(verdict["named_stops"][0]["kind"], "operational")


class Condition1Roster(DeskFinalCase):
    def test_sol_probe_zero_leg_rows_is_a_stop(self):
        # Sol's probe: clean status and meter metadata with zero leg rows raise no named stop in the frozen desk.
        rules = self.fx.kit["stop_rules"]
        base = {"result": {"chain_exit_code": 0, "chain_outcome": "COMPLETE", "fault": False, "outcome": "MEASURED_OK"},
                "meter": {"present": True, "proven_stopped": True, "bad_polls": 0, "usb_errors": 0},
                "feeds_proven_stopped": True, "legs": []}
        self.assertEqual(evaluate_named_stops(rules, base), [])
        work, bundle, anchor = self.pack()
        shutil.rmtree(bundle / "legs")
        _, stops = desk.build_desk(plan_id="probe", input_dir=bundle, out_dir=work / "frozen",
                                   adapter="leg-summary-v1", stop_rules=rules)
        self.assertEqual(stops, [])     # the frozen desk builds a zero-row table with no stop
        verdict = self.judge(work, bundle, remanifest(bundle))
        self.assertNotFinal(verdict, "DESK_NO_LEG_ROWS")
        self.assertTrue(verdict["next_arm_hold"])
        # Zero rows with the receipt's legs emptied too (a consistent but empty record) is still a stop.
        edit_json(bundle / desk_final.RECEIPT_NAME, lambda r: r.update(legs=[]))
        verdict = self.judge(work, bundle, remanifest(bundle))
        self.assertNotFinal(verdict, "DESK_NO_LEG_ROWS")
        self.assertNotFinal(verdict, "DESK_ROSTER")

    def test_a_missing_summary_is_a_stop(self):
        work, bundle, anchor = self.pack()
        (bundle / "legs/L003/leg_summary.json").unlink()
        self.assertEqual(len(desk.leg_summary_rows(bundle)), 5)   # the frozen loader skips it silently
        verdict = self.judge(work, bundle, remanifest(bundle))
        self.assertNotFinal(verdict, "DESK_ROSTER")
        self.assertIn("missing leg records ['L003']", " ".join(verdict["reasons"]))

    def test_a_duplicate_leg_record_is_a_stop(self):
        work, bundle, anchor = self.pack()
        shutil.copytree(bundle / "legs/L002", bundle / "legs/L007")
        verdict = self.judge(work, bundle, remanifest(bundle))
        self.assertNotFinal(verdict, "DESK_DUPLICATE")
        self.assertIn("leg L002 has 2 records", " ".join(verdict["reasons"]))
        # The receipt recording a leg twice.
        work, bundle, anchor = self.pack()
        edit_json(bundle / desk_final.RECEIPT_NAME, lambda r: r["legs"].append(r["legs"][1]))
        self.assertNotFinal(self.judge(work, bundle, remanifest(bundle)), "DESK_DUPLICATE")

    def test_order_and_count_must_equal_the_queue_entry(self):
        ids = self.fx.ids
        for roster in ([ids[0], ids[2], ids[1], *ids[3:6]], ids[:5], ids[:7]):
            work, bundle, anchor = self.pack()
            verdict = self.judge(work, bundle, anchor, queue=self.fx.queue([roster, ids[7:12]]))
            self.assertNotFinal(verdict, "DESK_ROSTER")
        # The receipt's leg records out of roster order (its roster field and the rows are right).
        work, bundle, anchor = self.pack()
        edit_json(bundle / desk_final.RECEIPT_NAME,
                  lambda r: r.update(legs=[r["legs"][0], r["legs"][2], r["legs"][1], *r["legs"][3:]]))
        verdict = self.judge(work, bundle, remanifest(bundle))
        self.assertNotFinal(verdict, "DESK_ROSTER")
        self.assertIn("receipt legs", " ".join(verdict["reasons"]))

    def test_attempts_and_redo_names(self):
        redo = self.fx.span("redo", self.fx.ids[:6], contaminate=["L002"])
        work, bundle, anchor = self.pack(redo)
        receipt = json.loads((bundle / desk_final.RECEIPT_NAME).read_text())
        l002 = next(leg for leg in receipt["legs"] if leg["leg_id"] == "L002")
        self.assertEqual([a["output_dir"] for a in l002["attempts"]], ["legs/L002/runtime.rejected1", "legs/L002/runtime"])
        verdict = self.judge(work, bundle, anchor)
        self.assertEqual(codes(verdict), ["HAND_TABLE_DUE"])    # a redo always takes the hand table
        for name, change in (
                ("renamed redo", lambda r: r["legs"][1]["attempts"][0].update(output_dir="legs/L002/runtime.rejected2")),
                ("renumbered", lambda r: r["legs"][1]["attempts"][1].update(attempt=3)),
                ("hidden redo", lambda r: r["legs"][1].update(attempts=r["legs"][1]["attempts"][1:])),
                ("redo count", lambda r: r.update(load_redos_used=0))):
            work, bundle, anchor = self.pack(redo)
            edit_json(bundle / desk_final.RECEIPT_NAME, change)
            self.assertNotFinal(self.judge(work, bundle, remanifest(bundle)), "DESK_ATTEMPTS")


class Condition2Identity(DeskFinalCase):
    def test_a_wrong_kit_hash_is_a_stop(self):
        work, bundle, anchor = self.pack()
        verdict = self.judge(work, bundle, anchor, queue=self.fx.queue(sha="0" * 64))
        self.assertNotFinal(verdict, "DESK_IDENTITY")
        self.assertIn("is not the queue's pin", " ".join(verdict["reasons"]))
        work, bundle, anchor = self.pack(kit=self.fx.identity(sha256="1" * 64))
        self.assertNotFinal(self.judge(work, bundle, anchor), "DESK_IDENTITY")
        # The span ran on another kit sha (receipt), though the bundle is packed with the queue's.
        other = self.fx.span("other-kit", self.fx.ids[:6], kit_sha256="2" * 64)
        work, bundle, anchor = self.pack(other)
        verdict = self.judge(work, bundle, anchor)
        self.assertNotFinal(verdict, "DESK_IDENTITY")
        self.assertIn("receipt kit.sha256", " ".join(verdict["reasons"]))

    def test_frozen_commit_plan_and_kit_leg_identities(self):
        work, bundle, anchor = self.pack(kit=self.fx.identity(frozen_commit="b" * 40))
        self.assertNotFinal(self.judge(work, bundle, anchor), "DESK_IDENTITY")
        work, bundle, anchor = self.pack(seq=2)    # packed as span 2's plan id
        self.assertNotFinal(self.judge(work, bundle, anchor), "DESK_IDENTITY")
        work, bundle, anchor = self.pack()
        verdict = self.judge(work, bundle, anchor, seq=9)
        self.assertNotFinal(verdict, "DESK_IDENTITY")
        self.assertIn("not in queue", " ".join(verdict["reasons"]))
        work, bundle, anchor = self.pack()
        for path in (bundle / "legs/L004/leg_summary.json",):
            edit_json(path, lambda d: d.update(seed=1))
        edit_json(bundle / desk_final.RECEIPT_NAME, lambda r: r["legs"][3]["summary"].update(seed=1))
        self.assertNotFinal(self.judge(work, bundle, remanifest(bundle)), "DESK_IDENTITY")

    def test_the_span_reference_is_the_capture_legs_accepted_attempt(self):
        work, bundle, anchor = self.pack()
        consumer = next(r["leg_id"] for r in json.loads((self.clean / "runner_receipt.json").read_text())["legs"]
                        if r.get("span_reference"))
        index = self.fx.ids.index(consumer)

        def wrong(doc):
            doc["span_reference"] = {**doc["span_reference"], "attempt": 2, "redone": True}
        edit_json(bundle / f"legs/{consumer}/leg_summary.json", wrong)
        edit_json(bundle / desk_final.RECEIPT_NAME, lambda r: wrong(r["legs"][index]["summary"]))
        verdict = self.judge(work, bundle, remanifest(bundle))
        self.assertNotFinal(verdict, "DESK_IDENTITY")
        self.assertIn("capture leg's accepted attempt", " ".join(verdict["reasons"]))
        # Consumers that verified different reference records.
        work, bundle, anchor = self.pack()

        def split(r):
            step = next(s for s in r["steps"] if s["name"] == f"{consumer}.a1")
            step["result"]["g0_reference_record_sha256"] = "d" * 64
        edit_json(bundle / desk_final.RECEIPT_NAME, split)
        self.assertNotFinal(self.judge(work, bundle, remanifest(bundle)), "DESK_IDENTITY")

    def test_a_mock_receipt_is_never_final_in_production(self):
        work, bundle, anchor = self.pack()
        verdict = self.judge(work, bundle, anchor, allow_mock=False)
        self.assertNotFinal(verdict, "DESK_IDENTITY")
        self.assertTrue(verdict["mock"])


class Condition3Authenticated(DeskFinalCase):
    def test_a_tampered_receipt_is_a_stop(self):
        work, bundle, anchor = self.pack()
        edit_json(bundle / desk_final.RECEIPT_NAME, lambda r: r.update(load_redos_used=0))
        verdict = self.judge(work, bundle, anchor)
        self.assertNotFinal(verdict, "DESK_UNAUTHENTICATED")
        self.assertIn("runner_receipt.json: sha256", " ".join(verdict["reasons"]))

    def test_the_anchor_the_manifest_and_every_file(self):
        work, bundle, anchor = self.pack()
        self.assertNotFinal(self.judge(work, bundle, None), "DESK_UNAUTHENTICATED")       # no anchor
        self.assertNotFinal(self.judge(work, bundle, "0" * 64), "DESK_UNAUTHENTICATED")   # wrong anchor
        # A re-manifested bundle is self-consistent but no longer matches the published anchor.
        edit_json(bundle / "legs/L002/leg_summary.json", lambda d: d.update(admitted=False))
        remanifest(bundle)
        self.assertNotFinal(self.judge(work, bundle, anchor), "DESK_UNAUTHENTICATED")
        # A tampered leg summary under the original manifest.
        work, bundle, anchor = self.pack()
        edit_json(bundle / "legs/L005/leg_summary.json", lambda d: d.update(attempts=1))
        (bundle / "legs/L005/leg_summary.json").write_text((bundle / "legs/L005/leg_summary.json").read_text() + " ")
        self.assertNotFinal(self.judge(work, bundle, anchor), "DESK_UNAUTHENTICATED")
        # The manifest's receipt entry must be the receipt's own hash.
        work, bundle, anchor = self.pack()
        manifest = json.loads((bundle / desk_final.MANIFEST_NAME).read_text())
        manifest["receipt"]["sha256"] = "3" * 64
        raw = (json.dumps(manifest, indent=1, sort_keys=True) + "\n").encode()
        (bundle / desk_final.MANIFEST_NAME).write_bytes(raw)
        self.assertNotFinal(self.judge(work, bundle, desk_final.sha256_bytes(raw)), "DESK_UNAUTHENTICATED")

    def test_files_outside_the_manifest_or_the_layout_are_refused_unread(self):
        work, bundle, anchor = self.pack()
        planted = bundle / "hazards/meter/stream-0001.jsonl"
        planted.parent.mkdir(parents=True)
        planted.write_text('{"k": "s", "power_w": 1}\n')
        reads = []
        original = desk_final._Reader.read

        def spy(reader, path):
            reads.append(Path(path))
            return original(reader, path)
        with mock.patch.object(desk_final._Reader, "read", spy):
            verdict = self.judge(work, bundle, anchor)
        self.assertNotFinal(verdict, "DESK_UNAUTHENTICATED")
        self.assertIn("not in the bundle layout (not opened)", " ".join(verdict["reasons"]))
        self.assertNotIn(planted, reads)
        self.assertTrue(all(p.name in desk_final.ALLOWED_BASENAMES for p in reads))
        # A file inside the layout but not in the manifest.
        work2, bundle2, anchor2 = self.pack()
        shutil.copytree(bundle2 / "legs/L002", bundle2 / "legs/L007")
        verdict = self.judge(work2, bundle2, anchor2)
        self.assertNotFinal(verdict, "DESK_UNAUTHENTICATED")
        self.assertIn("legs/L007/leg_summary.json: in the bundle, not in the manifest", " ".join(verdict["reasons"]))
        # Listed in a re-manifest, it is still outside the layout and still unread.
        reads.clear()
        with mock.patch.object(desk_final._Reader, "read", spy):
            verdict = self.judge(work, bundle, remanifest(bundle))
        self.assertNotFinal(verdict, "DESK_UNAUTHENTICATED")
        self.assertNotIn(planted, reads)


class Condition4Feeds(DeskFinalCase):
    def test_every_feed_needs_its_own_stop_proof(self):
        work, bundle, anchor = self.pack()
        edit_json(bundle / desk_final.RECEIPT_NAME, lambda r: r["feeds"]["agents"].pop("stop"))
        verdict = self.judge(work, bundle, remanifest(bundle))
        self.assertNotFinal(verdict, "DESK_FEED_PROOF")
        self.assertIn("INSTRUMENT_FAULT", codes(verdict))

    def test_a_feed_not_proven_stopped_is_an_instrument_fault_the_frozen_desk_misses(self):
        work, bundle, anchor = self.pack()
        edit_json(bundle / desk_final.RECEIPT_NAME, lambda r: r["feeds"]["volumes"]["stop"].update(proven_stopped=False))
        verdict = self.judge(work, bundle, remanifest(bundle))
        self.assertIn("INSTRUMENT_FAULT", codes(verdict))
        self.assertTrue(verdict["next_arm_hold"])
        summary = json.loads((work / "out/desk_summary.json").read_text())
        self.assertFalse(summary["feeds_proven_stopped"])
        self.assertFalse(summary["feeds"]["volumes"]["proven_stopped"])
        # The frozen desk takes feeds_proven_stopped from the meter alone and pages nobody.
        _, stops = desk.build_desk(plan_id="frozen", input_dir=bundle, out_dir=work / "frozen",
                                   adapter="leg-summary-v1", stop_rules=self.fx.kit["stop_rules"])
        self.assertEqual(stops, [])
        # A meter.json whose proof disagrees with the meter feed's own proof.
        work, bundle, anchor = self.pack()
        edit_json(bundle / "span/meter.json", lambda m: m.update(proven_stopped=False))
        self.assertNotFinal(self.judge(work, bundle, remanifest(bundle)), "DESK_SCHEMA")


class HandTableAndGates(DeskFinalCase):
    def hand_table(self, work, rows, **kw):
        path = work / desk_final.HAND_TABLE_NAME
        path.write_text(json.dumps({"schema": desk_final.HAND_TABLE_SCHEMA, "plan_id": "cq-df-s01-a1",
                                    "legs": rows, **kw}))
        return path

    def rows(self, bundle):
        out = []
        for leg_id in self.fx.ids[:6]:
            d = json.loads((bundle / f"legs/{leg_id}/leg_summary.json").read_text())
            out.append({k: d[k] for k in ("leg_id", "attempts", "contaminated_redos", "g0_outcome", "admitted")}
                       | {"g0_s": round(d["g0_s"] + 0.4, 3), "wall_s": round(d["wall_s"] - 0.3, 3)})
        return out

    def test_a_mandatory_hand_table_that_agrees_makes_the_span_final(self):
        redo = self.fx.span("redo", self.fx.ids[:6], contaminate=["L002"])
        work, bundle, anchor = self.pack(redo)
        verdict = self.judge(work, bundle, anchor, hand_table_path=self.hand_table(work, self.rows(bundle),
                                                                                    named_stops=[]))
        self.assertTrue(verdict["desk_final"], verdict["reasons"])
        self.assertEqual(verdict["hand_table"]["triggers"], ["redo (L002)"])
        self.assertTrue(verdict["hand_table"]["agrees"])

    def test_a_disagreeing_hand_table_holds_the_next_arm(self):
        work, bundle, anchor = self.pack()
        rows = self.rows(bundle)
        rows[3]["admitted"] = False
        verdict = self.judge(work, bundle, anchor, hand_table_path=self.hand_table(work, rows))
        self.assertNotFinal(verdict, "HAND_TABLE_DISAGREES")
        self.assertTrue(verdict["next_arm_hold"])
        self.assertIn({"code": "HAND_TABLE_DISAGREES", "scope": "queue", "cleared_by": "the lead (named stop)"},
                      verdict["holds"])
        verdict = self.judge(work, bundle, anchor, hand_table_path=self.hand_table(work, self.rows(bundle),
                                                                                    named_stops=["REFUSAL"]))
        self.assertNotFinal(verdict, "HAND_TABLE_DISAGREES")

    def test_triggers_exclusion_schema_change_and_the_seeded_draw(self):
        timeout = self.fx.span("timeout", self.fx.ids[:6], g0_timeout=["L004"])
        work, bundle, anchor = self.pack(timeout)
        verdict = self.judge(work, bundle, anchor)
        self.assertNotFinal(verdict, "HAND_TABLE_DUE")
        self.assertEqual(verdict["hand_table"]["triggers"], ["exclusion (L004)"])
        work, bundle, anchor = self.pack()
        verdict = self.judge(work, bundle, anchor, history=[])
        self.assertNotFinal(verdict, "HAND_TABLE_DUE")
        self.assertIn("schema change", verdict["hand_table"]["triggers"][0])
        verdict = self.judge(work, bundle, anchor, history=[{"kit_schema": "joulewise.cadence_campaign_kit.v1",
                                                              "leg_keys": [], "legs": []}])
        self.assertNotFinal(verdict, "HAND_TABLE_DUE")
        verdict = self.judge(work, bundle, anchor, hand_sample=True)
        self.assertEqual(verdict["hand_table"]["triggers"], ["sampled (the lead's seeded draw)"])
        self.assertNotFinal(verdict, "HAND_TABLE_DUE")
        self.assertFalse(verdict["next_arm_hold"])   # a due hand table blocks finality, not the next arm

    def test_hand_gates_are_printed_and_never_cleared(self):
        work, bundle, anchor = self.pack()
        verdict = self.judge(work, bundle, anchor)
        gates = {g["gate"]: g for g in verdict["hand_gates"]}
        self.assertEqual(set(gates), {"class A smoke hand-read", "RL-158 Q1 reference print"})
        self.assertTrue(all(g["status"] == desk_final.GATE_REQUIRED for g in gates.values()))
        self.assertEqual(gates["class A smoke hand-read"]["holds"], "kit:cl-test-11")
        self.assertIsNone(gates["RL-158 Q1 reference print"]["holds"])
        q1 = gates["RL-158 Q1 reference print"]["print"]
        self.assertEqual(q1["capture"]["dir"], "legs/L001/runtime")
        self.assertEqual({c["leg_id"] for c in q1["consumers"]},
                         {r["leg_id"] for r in json.loads((work / "out/desk_summary.json").read_text())["legs"]
                          if r["g0_role"] == "consume"})
        table = (work / "out/JOURNAL-TABLE.md").read_text()
        self.assertIn("**HAND GATE REQUIRED: class A smoke hand-read**", table)
        self.assertIn("**HAND GATE REQUIRED: RL-158 Q1 reference print**", table)
        # The kit's second span is not its first: no class A gate; Q1's print stays.
        second = self.fx.span("second", self.fx.ids[6:12])
        work, bundle, anchor = self.pack(second, seq=2)
        verdict = self.judge(work, bundle, anchor, seq=2)
        self.assertTrue(verdict["desk_final"], verdict["reasons"])
        self.assertEqual([g["gate"] for g in verdict["hand_gates"]], ["RL-158 Q1 reference print"])
        self.assertEqual(verdict["hand_gates"][0]["print"]["capture"]["leg_id"], "L007")

    def test_the_l002_and_l005_consumer_gates(self):
        receipt = {"steps": [], "soak_attempts": [], "feeds": {}, "span_result": None,
                   "legs": [{"leg_id": "L001", "attempts": [{}]}]}
        for campaign, gated, shape in (("cl-dev-03", "L002", "span"), ("cl-dev-04", "L005", "span"),
                                       ("cl-dev-03", "L002", "own")):
            roster = ["L001", gated]
            expected = {"kit": {"campaign_id": campaign}, "roster": roster, "kit_first_leg": "L001",
                        "kit_schema": desk_final.V11_SCHEMA,
                        "kit_legs": {"L001": {"g0_shape": "own"}, gated: {"g0_shape": shape}}}
            rows = [{"leg_id": "L001", "g0_role": "capture"},
                    {"leg_id": gated, "g0_role": "consume" if shape == "span" else "capture",
                     "g0_outcome": "timeout", "g0_s": 1200.0, "admitted": False}]
            gates = {g["gate"]: g for g in desk_final.hand_gates(rows, receipt, expected, None)}
            name = f"{gated} consumer gate"
            if shape == "own":   # the v1.1a draft: L002 is own-shaped and no consumer gate applies
                self.assertNotIn(name, gates)
                continue
            self.assertEqual(gates[name]["holds"], f"kit:{campaign}")
            self.assertEqual(gates[name]["print"]["g0_outcome"], "timeout")
            self.assertEqual(gates[name]["status"], desk_final.GATE_REQUIRED)


class BlindingAndCli(DeskFinalCase):
    def test_a_planted_denied_key_refuses_with_a_verdict_and_no_table(self):
        work, bundle, anchor = self.pack()
        self.assertTrue(self.judge(work, bundle, anchor)["desk_final"])     # a table now sits in out/
        edit_json(bundle / "legs/L002/leg_summary.json", lambda d: d.update(energy_j=12.5))
        verdict = self.judge(work, bundle, remanifest(bundle))
        self.assertNotFinal(verdict, "DESK_REFUSAL")
        self.assertFalse((work / "out/JOURNAL-TABLE.md").exists())
        text = (work / "out" / desk_final.VERDICT_NAME).read_text()
        self.assertNotIn("energy_j", text)
        self.assertNotRegex(text, r"(?i)\b(\w*energy\w*|joules?|watts?|\w*power_w\w*|slots?|\w*transcripts?)\b")
        self.assertTrue(desk_final.verify_verdict(json.loads(text)))

    def test_cli_final_exit_codes_lock_and_the_legacy_build(self):
        work, bundle, anchor = self.pack()
        qp = work / "QUEUE.json"
        qp.write_text(json.dumps(self.fx.queue()))
        hist = work / "history.json"
        hist.write_text(json.dumps(self.fx.history()))
        lock = work / "AIR-QUIET.lock"
        argv = ["final", "--plan-id", "cq-df-s01-a1", "--bundle", str(bundle), "--manifest-sha256", anchor,
                "--queue", str(qp), "--kit", str(self.fx.kit_path), "--out", str(work / "o1"), "--history", str(hist),
                "--lock", str(lock), "--allow-mock"]
        with redirect_stdout(io.StringIO()) as out:
            self.assertEqual(cli.main(argv), 0)
        self.assertIn("desk_final true", out.getvalue())
        self.assertIn("HAND GATE REQUIRED class A smoke hand-read", out.getvalue())
        with redirect_stdout(io.StringIO()):
            self.assertEqual(cli.main([*argv[:-1]]), 3)                       # a mock receipt without --allow-mock
            self.assertEqual(cli.main([*argv[:6], "0" * 64, *argv[7:]]), 3)   # wrong anchor
        lock.write_text(f"label=other pid={os.getpid()} start=now\n")
        with redirect_stdout(io.StringIO()) as out:
            self.assertEqual(cli.main([*argv[:12], str(work / "o2"), *argv[13:]]), 4)
        self.assertFalse((work / "o2" / desk_final.VERDICT_NAME).exists())
        lock.unlink()
        with redirect_stdout(io.StringIO()) as out:
            rc = cli.main(["build", "--plan-id", "legacy", "--input", str(self.clean / runner.DESK_BUNDLE),
                           "--out", str(work / "legacy"), "--kit", str(self.fx.kit_path), "--lock", str(lock)])
        self.assertEqual(rc, 0)
        legacy = json.loads((work / "legacy" / desk_final.VERDICT_NAME).read_text())
        self.assertFalse(legacy["desk_final"])
        self.assertTrue(desk_final.verify_verdict(legacy))


if __name__ == "__main__":
    unittest.main()
