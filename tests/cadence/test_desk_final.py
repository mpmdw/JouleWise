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

from joulewise.cadence import desk, desk_final, desk_transport, kit as kitmod
from joulewise.cadence.stops import evaluate_named_stops
from scripts import cadence_legs_runner as runner
from scripts.air import cadence_desk as cli
from tests.cadence.test_kit_v11 import local
from tests.git_fixture import init_git_fixture
from tests.cadence.test_span_reference import span_kit

TMP = os.environ.get("TMPDIR")
KIT_PATH = "docs/process/cadence/kits/cl-test-11.json"
FIXTURES = Path(__file__).resolve().parent / "fixtures_desk_final"
KITS = Path(__file__).resolve().parents[2] / "docs/process/cadence/kits"


def codes(verdict):
    return sorted({s["code"] for s in verdict["named_stops"]} | {s["code"] for s in verdict["pending"]})


class Fixture:
    """One synthetic kit file, a queue of four six-leg spans (two re-runs pad the draw's block), and mock span
    outputs to pack. The queue id is the first whose seeded draw samples neither of the first two spans."""

    def __init__(self, root):
        self.root = Path(root)
        self.kit = span_kit(legs_per_span=6)
        self.kit_path = self.root / "kit.json"
        self.kit_path.write_text(json.dumps(self.kit, indent=1))
        _, self.sha = kitmod.load_kit(self.kit_path)
        self.ids = [leg["leg_id"] for leg in self.kit["legs"]]
        self.spans = {}
        self.queue_id = next(q for q in (f"cq-df-{i}" for i in range(1, 50))
                             if not any(desk_final.hand_sample(self.queue(queue_id=q), f"cq-df-s0{n}-a1", self.kit,
                                                               self.sha)["selected"] for n in (1, 2)))

    def queue(self, rosters=None, sha=None, queue_id=None):
        rosters = rosters or [self.ids[:6], self.ids[6:12]]
        spans = [{"seq": i + 1, "span_id": f"df-s{i + 1:02d}", "block_id": "df-dev",
                  "kit": {"path": KIT_PATH, "sha256": sha or self.sha}, "legs": roster, "attempt": 1,
                  "not_before": "2026-11-17"} for i, roster in enumerate(rosters)]
        if len(rosters) == 2:
            spans += [{**spans[i], "seq": 3 + i, "span_id": f"df-s{3 + i:02d}", "rerun_of": spans[i]["span_id"]}
                      for i in (0, 1)]
        return {"schema": "joulewise.cadence_queue.v1", "queue_id": queue_id or self.queue_id,
                "expires_at": "2026-12-31T00:00:00-08:00", "halt": None, "standing_notice": None, "spans": spans}

    def identity(self, **kw):
        return {"path": KIT_PATH, "sha256": self.sha, "campaign_id": self.kit["campaign_id"],
                "frozen_commit": self.kit["frozen"]["commit"], **kw}

    def span(self, name, legs, rc_ok=True, **kw):
        if name not in self.spans:
            out = self.root / "spans" / name
            rc, _, _, _ = runner.run_mock(kit=self.kit, kit_sha256=kw.pop("kit_sha256", self.sha), output=out,
                                          t0_epoch=local("2026-11-17T03:00"), windows=[], leg_ids=legs, **kw)
            assert (rc == 0) == rc_ok, (name, rc)
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

    def pack(self, span=None, *, seq=1, kit=None, roster=None, **kw):
        work = self.work()
        bundle = work / "bundle"
        roster = roster or (self.fx.ids[:6] if seq == 1 else self.fx.ids[6:12])
        anchor = desk_final.pack_bundle(span or self.clean, bundle, plan_id=f"cq-df-s{seq:02d}-a1",
                                        queue_id=self.fx.queue_id, span_id=f"df-s{seq:02d}", attempt=1,
                                        kit=kit or self.fx.identity(), roster=roster, **kw)
        return work, bundle, anchor

    def judge(self, work, bundle, anchor, *, seq=1, queue=None, history="default", allow_mock=True,
              allow_unsigned=True, **kw):
        qp = work / "QUEUE.json"
        qp.write_text(json.dumps(queue or self.fx.queue()))
        return desk_final.judge_span(plan_id=f"cq-df-s{seq:02d}-a1", bundle_dir=bundle, manifest_sha256=anchor,
                                     queue_path=qp, kit_path=kw.pop("kit_path", self.fx.kit_path),
                                     out_dir=work / "out", history=self.fx.history() if history == "default" else history,
                                     allow_mock=allow_mock, allow_unsigned=allow_unsigned, **kw)

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


class SoakRetry(DeskFinalCase):
    """RL-171's one soak retry (Mythos #794 F3): the receipt's soak_attempts, a refused stage then an accepted one."""

    def test_no_retry_prints_one_accepted_soak(self):
        work, bundle, anchor = self.pack()
        verdict = self.judge(work, bundle, anchor)
        self.assertTrue(verdict["desk_final"], verdict["reasons"])
        self.assertIn("- soak (RL-171 retry): accepted attempt 1", (work / "out/JOURNAL-TABLE.md").read_text())
        summary = json.loads((work / "out/desk_summary.json").read_text())
        self.assertEqual(summary["soak"]["accepted_attempt"], 1)

    def test_a_refused_soak_then_an_accepted_retry_is_not_a_stopped_span(self):
        retried = self.fx.span("soak-retry", self.fx.ids[:6], soak_refusals=1)
        receipt = json.loads((retried / runner.RECEIPT_NAME).read_text())
        stages = {s["name"]: s["rc"] for s in receipt["steps"] if s["name"].startswith("soak")}
        self.assertEqual(stages, {"soak": 2, "soak.a2": 0})
        self.assertEqual([a["output_dir"] for a in receipt["soak_attempts"]], ["soak.rejected1", "soak"])
        work, bundle, anchor = self.pack(retried)
        verdict = self.judge(work, bundle, anchor)
        # RL-172a: a retried soak puts the span on the hand table; the refusal kind is kept (Sol 8, Mythos F6).
        self.assertNotFinal(verdict, "HAND_TABLE_DUE")
        self.assertEqual(verdict["hand_table"]["triggers"], ["retried soak (settle_or_quiet; RL-172a)"])
        self.assertEqual((verdict["named_stops"], verdict["next_arm_hold"]), ([], False))
        summary = json.loads((work / "out/desk_summary.json").read_text())
        self.assertEqual(summary["soak"]["attempts"][0]["refusal_kind"], "settle_or_quiet")
        self.assertIn("settle or quiet check", summary["soak"]["attempts"][0]["refusal"])
        rows = HandTableAndGates.rows(self, bundle)
        hand = work / desk_final.HAND_TABLE_NAME
        hand.write_text(json.dumps({"schema": desk_final.HAND_TABLE_SCHEMA, "plan_id": "cq-df-s01-a1", "legs": rows,
                                    "named_stops": [], "soak_attempts": 2}))
        verdict = self.judge(work, bundle, anchor, hand_table_path=hand)
        self.assertTrue(verdict["desk_final"], verdict["reasons"])
        table = (work / "out/JOURNAL-TABLE.md").read_text()
        self.assertIn("- soak (RL-171 retry): accepted attempt 2 after 1 refused (settle_or_quiet; retry)", table)
        self.assertIn("non-zero: soak (refused soak, retried)", table)
        gate = next(g for g in verdict["hand_gates"] if g["gate"] == "class A smoke hand-read")
        self.assertEqual(gate["print"]["steps_nonzero"], ["soak (refused soak, retried)"])
        self.assertEqual(len(gate["print"]["soak_attempts"]), 2)
        q1 = next(g for g in verdict["hand_gates"] if g["gate"] == "RL-158 Q1 reference print")
        self.assertEqual(q1["print"]["soak_reference"], {"dir": "soak", "attempts": 2, "refusals": ["settle_or_quiet"]})
        # A receipt whose soak record disagrees with its stages is not final.
        for change in (lambda r: r["soak_attempts"][0].update(output_dir="soak"),
                       lambda r: next(s for s in r["steps"] if s["name"] == "soak").update(rc=0)):
            work, bundle, anchor = self.pack(retried)
            edit_json(bundle / desk_final.RECEIPT_NAME, change)
            self.assertNotFinal(self.judge(work, bundle, remanifest(bundle)), "DESK_ATTEMPTS")

    def test_a_second_soak_refusal_is_a_stop(self):
        refused = self.fx.span("soak-refused", self.fx.ids[:6], rc_ok=False, soak_refusals=2)
        work, bundle, anchor = self.pack(refused)
        verdict = self.judge(work, bundle, anchor)
        self.assertNotFinal(verdict, "DESK_NO_LEG_ROWS")
        self.assertTrue(verdict["next_arm_hold"])
        refusal = next(s for s in verdict["named_stops"] if s["code"] == "REFUSAL")
        self.assertIn("no soak accepted (2 refused: settle_or_quiet, settle_or_quiet)", refusal["detail"])
        self.assertIn("- soak (RL-171 retry): no soak accepted (2 refused", (work / "out/JOURNAL-TABLE.md").read_text())


class HandTableAndGates(DeskFinalCase):
    def hand_table(self, work, rows, **kw):
        path = work / desk_final.HAND_TABLE_NAME
        path.write_text(json.dumps({"schema": desk_final.HAND_TABLE_SCHEMA, "plan_id": "cq-df-s01-a1",
                                    "legs": rows, "named_stops": [], "soak_attempts": 1, **kw}))
        return path

    def rows(self, bundle):
        out = []
        for leg_id in self.fx.ids[:6]:
            d = json.loads((bundle / f"legs/{leg_id}/leg_summary.json").read_text())
            out.append({k: d[k] for k in ("leg_id", "attempts", "contaminated_redos", "g0_outcome", "admitted",
                                          "band_reached", "g0_role", "span_reference")}
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
        self.assertEqual(verdict["hand_table"]["triggers"], ["sampled (the lead's selection)"])
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
                "--lock", str(lock), "--allow-unsigned", "--allow-mock"]
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


class LegacyPins(unittest.TestCase):
    """Mythos F3, Sol 13: the development pins' runners write no ``soak_attempts``. Their own mocks' receipts
    (``fixtures_desk_final/``) are one accepted soak, never a REFUSAL."""
    CASES = {"b4b6aeb19": ("cl-dev-02.json", "dev-02-s01"), "2d347f721": ("cl-dev-04.v1.1.json", "dev-04-s01")}

    def setUp(self):
        tmp = tempfile.TemporaryDirectory(dir=TMP)
        self.addCleanup(tmp.cleanup)
        self.work = Path(tmp.name)

    def judge(self, pin, change=None):
        kit_name, span_id = self.CASES[pin]
        kit_path = KITS / kit_name
        kit, sha = kitmod.load_kit(kit_path)
        receipt = json.loads((FIXTURES / pin / runner.RECEIPT_NAME).read_text())
        roster = receipt["roster"]
        self.n = getattr(self, "n", 0) + 1
        base = self.work / f"{pin}-{self.n}"
        span_dir = base / "span"
        shutil.copytree(FIXTURES / pin, span_dir)
        plan_id = f"cq-{span_id}-a1"
        queue = {"schema": "joulewise.cadence_queue.v1", "queue_id": "cq-legacy-1",
                 "expires_at": "2026-12-31T00:00:00-08:00", "halt": None, "standing_notice": None,
                 "spans": [{"seq": 1, "span_id": span_id, "block_id": span_id[:6], "attempt": 1,
                            "kit": {"path": f"docs/process/cadence/kits/{kit_name}", "sha256": sha}, "legs": roster,
                            "not_before": "2026-11-17"}]}
        qp = base / "QUEUE.json"
        qp.write_text(json.dumps(queue))
        bundle = base / "bundle"
        anchor = desk_final.pack_bundle(span_dir, bundle, plan_id=plan_id, queue_id="cq-legacy-1", span_id=span_id,
                                        attempt=1, roster=roster,
                                        kit={"path": f"docs/process/cadence/kits/{kit_name}", "sha256": sha,
                                             "campaign_id": kit["campaign_id"], "frozen_commit": kit["frozen"]["commit"]})
        if change is not None:
            edit_json(bundle / desk_final.RECEIPT_NAME, change)
            anchor = remanifest(bundle)
        keys = sorted(json.loads((span_dir / "desk-bundle/legs" / roster[0] / "leg_summary.json").read_text()))
        return desk_final.judge_span(plan_id=plan_id, bundle_dir=bundle, manifest_sha256=anchor, queue_path=qp,
                                     kit_path=kit_path, out_dir=base / "out", allow_mock=True,
                                     allow_unsigned=True, history=[{"kit_schema": kit["schema"], "leg_keys": keys,
                                                                    "legs": []}])

    def test_a_clean_receipt_from_either_pin_is_one_accepted_soak(self):
        for pin in self.CASES:
            receipt = json.loads((FIXTURES / pin / runner.RECEIPT_NAME).read_text())
            self.assertNotIn("soak_attempts", receipt, pin)
            verdict = self.judge(pin)
            self.assertEqual(verdict["named_stops"], [], (pin, verdict["named_stops"]))
            self.assertFalse(verdict["next_arm_hold"], pin)
            self.assertLessEqual(set(codes(verdict)), {"HAND_TABLE_DUE"}, pin)   # a one-span stratum is always drawn
            summary = json.loads((self.work / f"{pin}-{self.n}" / "out/desk_summary.json").read_text())
            self.assertEqual(summary["soak"]["accepted_attempt"], 1, pin)
            self.assertFalse(summary["soak"]["field"], pin)
            self.assertIn("legacy receipt", summary["soak"]["note"], pin)
        gates = {g["gate"]: g for g in self.judge("2d347f721")["hand_gates"]}
        self.assertEqual(gates["L005 consumer gate"]["holds"], "kit:cl-dev-04")

    def test_a_refused_legacy_soak_is_a_refusal_and_an_invented_retry_is_refused(self):
        def refused(r):
            next(s for s in r["steps"] if s["name"] == "soak")["rc"] = 2
        verdict = self.judge("2d347f721", refused)
        self.assertIn("REFUSAL", codes(verdict))
        self.assertIn("legacy receipt: soak stage rc 2", next(s for s in verdict["named_stops"]
                                                              if s["code"] == "REFUSAL")["detail"])

        def retry(r):
            r["steps"].append({"name": "soak.a2", "rc": 0})
        self.assertIn("DESK_ATTEMPTS", codes(self.judge("2d347f721", retry)))

    def test_the_fixtures_are_the_pinned_runners_own_mocks(self):
        import subprocess
        import sys
        root = Path(__file__).resolve().parents[2]
        for pin, (kit_name, _) in self.CASES.items():
            if subprocess.run(["git", "-C", str(root), "cat-file", "-e", f"{pin}^{{commit}}"],
                              capture_output=True).returncode:
                self.skipTest(f"{pin} not in this clone")
            tree = self.work / f"tree-{pin}"
            tree.mkdir()
            archive = subprocess.run(["git", "-C", str(root), "archive", pin, "scripts", "joulewise", "configs"],
                                     capture_output=True, check=True).stdout
            subprocess.run(["tar", "-x", "-C", str(tree)], input=archive, check=True)
            out = self.work / f"regen-{pin}"
            gen = ("import sys, json; from pathlib import Path; from datetime import datetime; sys.path.insert(0, sys.argv[1]);"
                   "from scripts import cadence_legs_runner as r; from joulewise.cadence import kit as k, legs as l;"
                   "w=((2,0),(2,35)); kit, sha = k.load_kit(sys.argv[2], batch_window=w);"
                   "t0=datetime.fromisoformat('2026-11-17T13:20').replace(tzinfo=l.LOCAL_ZONE).timestamp();"
                   "r.run_mock(kit=kit, kit_sha256=sha, output=Path(sys.argv[3]), t0_epoch=t0, windows=[w],"
                   " leg_ids=['L001','L002','L003','L004','L005','L006'])")
            subprocess.run([sys.executable, "-B", "-c", gen, str(tree), str(KITS / kit_name), str(out)], check=True,
                           cwd=tree, capture_output=True, env={**os.environ, "TMPDIR": str(self.work)})
            fresh = json.loads((out / runner.RECEIPT_NAME).read_text())
            fixture = json.loads((FIXTURES / pin / runner.RECEIPT_NAME).read_text())
            self.assertNotIn("soak_attempts", fresh, pin)
            self.assertEqual([s["name"] for s in fresh["steps"]], [s["name"] for s in fixture["steps"]], pin)
            self.assertEqual([leg["summary"] for leg in fresh["legs"]], [leg["summary"] for leg in fixture["legs"]], pin)


class CommandResults(DeskFinalCase):
    """Sol 9: an error receipt, a failed or missing restore, or a soak claim with no stage never certifies."""

    def refusal(self, change):
        work, bundle, anchor = self.pack()
        edit_json(bundle / desk_final.RECEIPT_NAME, change)
        verdict = self.judge(work, bundle, remanifest(bundle))
        self.assertTrue(verdict["next_arm_hold"])
        return verdict, next((s["detail"] for s in verdict["named_stops"] if s["code"] == "REFUSAL"), "")

    def test_an_error_receipt_is_a_refusal(self):
        verdict, detail = self.refusal(lambda r: r.update(rc=17, error="RuntimeError: synthetic"))
        self.assertIn("receipt rc 17 (RuntimeError)", detail)
        self.assertIn("DESK_SCHEMA", codes(verdict))   # the clean span result contradicts rc 17

    def test_a_failed_or_missing_restore_is_a_refusal(self):
        _, detail = self.refusal(lambda r: next(s for s in r["steps"] if s["name"] == "restore").update(rc=17))
        self.assertIn("restore unproven (rc 17)", detail)
        verdict, detail = self.refusal(lambda r: r.update(steps=[s for s in r["steps"] if s["name"] != "restore"]))
        self.assertIn("restore unproven (no restore step)", detail)
        self.assertNotFinal(verdict, "DESK_SCHEMA")

    def test_a_failed_stage_and_a_soak_claim_without_its_stage(self):
        _, detail = self.refusal(lambda r: next(s for s in r["steps"] if s["name"] == "close-meter" or
                                                s["name"] == "condition13").update(rc=3))
        self.assertIn("rc 3", detail)
        verdict, detail = self.refusal(lambda r: r.update(steps=[s for s in r["steps"] if s["name"] != "soak"]))
        self.assertNotFinal(verdict, "DESK_ATTEMPTS")
        self.assertIn("no soak accepted", detail)

    def test_a_non_ok_controller_close_is_a_refusal(self):
        work, bundle, anchor = self.pack(controller={"status": "CLOSE_UNPROVEN"})
        verdict = self.judge(work, bundle, anchor)
        self.assertIn("controller close status CLOSE_UNPROVEN",
                      next(s["detail"] for s in verdict["named_stops"] if s["code"] == "REFUSAL"))


class PlanReferenceAndReuse(DeskFinalCase):
    def test_the_span_plan_binds_the_plan(self):
        work, bundle, anchor = self.pack()
        edit_json(bundle / desk_final.PLAN_NAME, lambda p: p.update(legs=p["legs"][:5]))
        self.assertNotFinal(self.judge(work, bundle, remanifest(bundle)), "DESK_ROSTER")
        work, bundle, anchor = self.pack()
        edit_json(bundle / desk_final.PLAN_NAME, lambda p: p.update(redo_quota=9))
        self.assertNotFinal(self.judge(work, bundle, remanifest(bundle)), "DESK_IDENTITY")
        work, bundle, anchor = self.pack()
        (bundle / desk_final.PLAN_NAME).unlink()
        self.assertNotFinal(self.judge(work, bundle, remanifest(bundle)), "DESK_IDENTITY")

    def test_consumers_are_bound_to_the_capture_not_only_to_each_other(self):
        work, bundle, anchor = self.pack(reference_record_sha256="e" * 64)
        self.assertTrue(self.judge(work, bundle, anchor)["desk_final"])

        def all_replaced(r):   # Sol 1: every consumer's hash changed to the same unrelated value
            for step in r["steps"]:
                if (step.get("result") or {}).get("g0_role") == "consume":
                    step["result"]["g0_reference_record_sha256"] = "d" * 64
        edit_json(bundle / desk_final.RECEIPT_NAME, all_replaced)
        verdict = self.judge(work, bundle, remanifest(bundle))
        self.assertNotFinal(verdict, "DESK_IDENTITY")
        self.assertIn("not the capture's record in the manifest", " ".join(verdict["reasons"]))
        work, bundle, anchor = self.pack()

        def other_source(r):
            for step in r["steps"]:
                if (step.get("result") or {}).get("g0_role") == "consume":
                    step["result"]["g0_reference_source"] = "mock-L999"
        edit_json(bundle / desk_final.RECEIPT_NAME, other_source)
        verdict = self.judge(work, bundle, remanifest(bundle))
        self.assertNotFinal(verdict, "DESK_IDENTITY")
        self.assertIn("capture's accepted run 'mock-L001'", " ".join(verdict["reasons"]))
        work, bundle, anchor = self.pack()
        edit_json(bundle / desk_final.MANIFEST_NAME, lambda m: m.update(reference=None))
        manifest_sha = desk_final.sha256_bytes((bundle / desk_final.MANIFEST_NAME).read_bytes())
        self.assertNotFinal(self.judge(work, bundle, manifest_sha), "DESK_IDENTITY")

    def test_a_receipt_judged_under_another_plan_id_is_refused(self):
        work, bundle, anchor = self.pack()
        receipt_sha = desk_final.sha256_bytes((bundle / desk_final.RECEIPT_NAME).read_bytes())
        history = [*self.fx.history(), {**self.fx.history()[0], "plan_id": "cq-df-s03-a1", "receipt_sha256": receipt_sha}]
        verdict = self.judge(work, bundle, anchor, history=history)
        self.assertNotFinal(verdict, "DESK_IDENTITY")
        self.assertIn("already judged under cq-df-s03-a1", " ".join(verdict["reasons"]))


class IncompleteHandTable(DeskFinalCase):
    """Sol 7: a hand table without its measurements cannot agree."""

    def test_rows_without_measurements_are_invalid_and_hold(self):
        work, bundle, anchor = self.pack()
        path = work / desk_final.HAND_TABLE_NAME
        for doc in ({"schema": desk_final.HAND_TABLE_SCHEMA, "plan_id": "cq-df-s01-a1",
                     "legs": [{"leg_id": x} for x in self.fx.ids[:6]], "named_stops": [], "soak_attempts": 1},
                    {"schema": desk_final.HAND_TABLE_SCHEMA, "plan_id": "cq-df-s01-a1",
                     "legs": HandTableAndGates.rows(self, bundle)}):
            path.write_text(json.dumps(doc))
            verdict = self.judge(work, bundle, anchor, hand_sample=True, hand_table_path=path)
            self.assertNotFinal(verdict, "HAND_TABLE_INVALID")
            self.assertTrue(verdict["next_arm_hold"])
            self.assertIsNone(verdict["hand_table"]["agrees"])

    def test_duplicate_and_non_finite_rows_are_invalid(self):
        work, bundle, anchor = self.pack()
        path = work / desk_final.HAND_TABLE_NAME
        rows = HandTableAndGates.rows(self, bundle)
        for bad in ([*rows, rows[0]], [{**rows[0], "g0_s": float("nan")}, *rows[1:]],
                    [{**rows[0], "attempts": "1"}, *rows[1:]]):
            path.write_text(json.dumps({"schema": desk_final.HAND_TABLE_SCHEMA, "plan_id": "cq-df-s01-a1",
                                        "legs": bad, "named_stops": [], "soak_attempts": 1}))
            self.assertNotFinal(self.judge(work, bundle, anchor, hand_table_path=path), "HAND_TABLE_INVALID")


class SeededDraw(unittest.TestCase):
    """The seeded stratified hand-sample draw (sha256-hand-sample-v1): one span per block of four per stratum."""

    def queue(self, kit, sha, n, queue_id="cq-draw-1", other=0):
        ids = [leg["leg_id"] for leg in kit["legs"]]
        spans = [{"seq": i + 1, "span_id": f"dr-s{i + 1:02d}", "kit": {"path": "k", "sha256": sha},
                  "legs": ids[:6], "attempt": 1} for i in range(n)]
        spans += [{"seq": n + i + 1, "span_id": f"dr-o{i + 1:02d}", "kit": {"path": "o", "sha256": "0" * 64},
                   "legs": ids[:6], "attempt": 1} for i in range(other)]
        return {"queue_id": queue_id, "spans": spans}

    def test_one_per_block_deterministic_and_prospective(self):
        kit = span_kit(legs_per_span=6)
        sha = "a" * 64
        q = self.queue(kit, sha, 9, other=3)
        draws = [desk_final.hand_sample(q, f"cq-dr-s{i + 1:02d}-a1", kit, sha) for i in range(9)]
        for block in (range(0, 4), range(4, 8), range(8, 9)):
            self.assertEqual(sum(draws[i]["selected"] for i in block), 1, list(block))
        self.assertEqual(draws, [desk_final.hand_sample(q, f"cq-dr-s{i + 1:02d}-a1", kit, sha) for i in range(9)])
        self.assertEqual(draws[0]["stratum"], {"kit_sha256": sha, "shape": "span"})
        self.assertIsNone(desk_final.hand_sample(q, "cq-dr-o01-a1", kit, sha))   # another kit: another stratum
        moved = [[desk_final.hand_sample(self.queue(kit, sha, 9, queue_id=f"cq-draw-{k}"), f"cq-dr-s{i + 1:02d}-a1",
                                         kit, sha)["position"] for i in range(9)] for k in range(2, 8)]
        self.assertGreater(len({tuple(m) for m in moved}), 1)   # the queue id is in the draw

    def test_own_shaped_spans_are_their_own_stratum(self):
        kit = span_kit(legs_per_span=6)
        own = [leg["leg_id"] for leg in kit["legs"] if leg["g0_shape"] == "own"]
        self.assertEqual(desk_final.span_shape(kit, own), "own")
        self.assertEqual(desk_final.span_shape(kit, [leg["leg_id"] for leg in kit["legs"]][:6]), "span")

    def test_sample_plan_cli(self):
        with tempfile.TemporaryDirectory(dir=TMP) as tmp:
            fx = Fixture(tmp)
            qp = Path(tmp) / "QUEUE.json"
            qp.write_text(json.dumps(fx.queue()))
            with redirect_stdout(io.StringIO()) as out:
                self.assertEqual(cli.main(["sample-plan", "--queue", str(qp), "--kit", str(fx.kit_path)]), 0)
            doc = json.loads(out.getvalue())
            self.assertEqual(doc["law"], desk_final.HAND_SAMPLE_LAW)
            self.assertEqual(sum(r["selected"] for r in doc["spans"]), 1)
            self.assertFalse(any(r["selected"] for r in doc["spans"] if r["plan_id"] in ("cq-df-s01-a1", "cq-df-s02-a1")))


class SignedTransport(DeskFinalCase):
    """Mythos F1, Sol 1: the bundle arrives as a commit signed by the controller's key and is verified on the
    Air in code; the verdict goes back as a commit signed by the desk's key, read by ``read_verdict``.
    Local repositories and throwaway keys only."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        import subprocess
        if shutil.which("ssh-keygen") is None:
            raise unittest.SkipTest("ssh-keygen not available")
        cls.sp = subprocess
        root = Path(cls.tmp.name) / "signing"
        root.mkdir()
        cls.keys = {}
        for name in ("cadence-controller", "cadence-desk", "rogue"):
            subprocess.run(["ssh-keygen", "-q", "-t", "ed25519", "-N", "", "-C", name, "-f", str(root / name)],
                           check=True)
            cls.keys[name] = root / name
        cls.signers = root / "allowed_signers"
        cls.signers.write_text("".join(f'{n} namespaces="git" {(root / (n + ".pub")).read_text().strip()}\n'
                                       for n in ("cadence-controller", "cadence-desk")))
        cls.origin = root / "origin.git"
        cls.origin.mkdir()
        init_git_fixture(cls.origin, "-q", "--bare")
        for name in ("mbp", "air"):
            (root / name).mkdir()
            init_git_fixture(root / name, "-q")
            subprocess.run(["git", "-C", str(root / name), "remote", "add", "origin", str(cls.origin)], check=True)
        cls.mbp, cls.air = root / "mbp", root / "air"

    def git(self, repo, *args):
        return self.sp.run(["git", "-C", str(repo), *args], capture_output=True, text=True)

    def audit_commit(self, queue_doc):
        """The queue committed on a synthetic audit branch (the controller's transition record names it)."""
        raw = json.dumps(queue_doc, indent=1).encode()
        tree = desk_transport.tree_of(self.mbp, {"docs/QUEUE.json": raw})
        commit = self.sp.run(["git", "-C", str(self.mbp), "commit-tree", tree], input=b"queue\n", capture_output=True,
                             env={**os.environ, "GIT_AUTHOR_NAME": "l", "GIT_AUTHOR_EMAIL": "l@l",
                                  "GIT_COMMITTER_NAME": "l", "GIT_COMMITTER_EMAIL": "l@l"}).stdout.decode().strip()
        self.git(self.mbp, "push", "-q", "-f", "origin", f"{commit}:refs/heads/audit")
        self.git(self.air, "fetch", "-q", "origin", "+refs/heads/audit:refs/remotes/origin/audit")
        return {"path": "docs/QUEUE.json", "sha256": desk_final.sha256_bytes(raw), "commit": commit}

    def transition(self, bundle, queue_doc=None, **kw):
        span = (queue_doc or self.fx.queue())["spans"][0]
        doc = {"schema": desk_transport.TRANSITION_SCHEMA, "plan_id": "cq-df-s01-a1", "queue_id": self.fx.queue_id,
               "span_id": span["span_id"], "attempt": 1, "queue": self.audit_commit(queue_doc or self.fx.queue()),
               "kit": {"path": KIT_PATH, "sha256": self.fx.sha},
               "plan_sha256": desk_final.sha256_bytes((bundle / desk_final.PLAN_NAME).read_bytes()),
               "arm_proof_sha256": "1" * 64, "arm_command_sha256": "2" * 64, "close_proof_sha256": "3" * 64,
               "status": "CLOSED_OK", "manifest_sha256": None, "t0_epoch": 0, "receipt_epoch": 0}
        doc.update(kw)
        return doc

    def ship(self, bundle, plan_id="cq-df-s01-a1", key="cadence-controller", **kw):
        sha, anchor = desk_transport.sign_bundle(self.mbp, bundle, self.transition(bundle, **kw), plan_id=plan_id,
                                                 signing_key=self.keys[key])
        ref = f"{desk_transport.BUNDLE_REF_PREFIX}{plan_id}"
        self.assertEqual(self.git(self.mbp, "push", "-q", "-f", "origin", f"{sha}:{ref}").returncode, 0)
        self.git(self.air, "fetch", "-q", "origin", "+refs/heads/desk-bundles/*:refs/remotes/origin/desk-bundles/*")
        return f"refs/remotes/origin/desk-bundles/{plan_id}", anchor

    def final(self, work, ref, *extra):
        qp = work / "QUEUE.json"
        qp.write_text(json.dumps(self.fx.queue()))
        hist = work / "history.json"
        hist.write_text(json.dumps(self.fx.history()))
        argv = ["final", "--plan-id", "cq-df-s01-a1", "--repo", str(self.air), "--bundle-ref", ref,
                "--allowed-signers", str(self.signers), "--kit", str(self.fx.kit_path),
                "--out", str(work / "out"), "--history", str(hist), "--lock", str(work / "lock"), "--allow-mock",
                *extra]
        with redirect_stdout(io.StringIO()):
            rc = cli.main(argv)
        return rc, json.loads((work / "out" / desk_final.VERDICT_NAME).read_text())

    def test_signed_bundle_to_verdict_and_back(self):
        work, bundle, anchor = self.pack()
        ref, signed_anchor = self.ship(bundle)
        self.assertEqual(signed_anchor, anchor)
        rc, verdict = self.final(work, ref)
        self.assertEqual(rc, 0, verdict["reasons"])
        self.assertEqual(verdict["transport"]["signed"], True)
        self.assertEqual(verdict["transport"]["signer"], "cadence-controller")
        self.assertFalse(list((work / "out").glob(".bundle-*")))      # the extracted copy is removed
        with redirect_stdout(io.StringIO()):
            self.assertEqual(cli.main(["publish", "--plan-id", "cq-df-s01-a1", "--out", str(work / "out"), "--repo",
                                       str(self.air), "--signing-key", str(self.keys["cadence-desk"])]), 0)
        self.git(self.mbp, "fetch", "-q", "origin", "+refs/heads/cadence-desk-final/*:refs/remotes/origin/cadence-desk-final/*")
        vref = "refs/remotes/origin/cadence-desk-final/cq-df-s01-a1"
        doc, summary = desk_transport.read_verdict(self.mbp, vref, allowed_signers=self.signers, plan_id="cq-df-s01-a1")
        self.assertEqual(doc, verdict)
        span = self.fx.queue()["spans"][0]
        ident = dict(plan_id="cq-df-s01-a1", queue_id=self.fx.queue_id, span_id=span["span_id"], attempt=1,
                     manifest_sha256=anchor)
        self.assertFalse(desk_final.counts_as_final(doc, **ident))          # a mock receipt never counts
        self.assertTrue(desk_final.counts_as_final({**doc, "mock": False} | {"verdict_sha256": desk_final.canonical_sha256(
            {k: v for k, v in {**doc, "mock": False}.items() if k != "verdict_sha256"})}, **ident))
        self.assertFalse(desk_final.counts_as_final(doc, **{**ident, "manifest_sha256": "0" * 64}))
        # A second judgment is a child commit on the same ref; the history comes back from the signed records.
        with redirect_stdout(io.StringIO()):
            self.assertEqual(cli.main(["publish", "--plan-id", "cq-df-s01-a1", "--out", str(work / "out"), "--repo",
                                       str(self.air), "--signing-key", str(self.keys["cadence-desk"])]), 0)
        self.git(self.mbp, "fetch", "-q", "origin", "+refs/heads/cadence-desk-final/*:refs/remotes/origin/cadence-desk-final/*")
        self.assertEqual(self.git(self.mbp, "rev-list", "--count", vref).stdout.strip(), "2")
        hist = desk_transport.history_from_records(self.mbp, "refs/remotes/origin/cadence-desk-final/",
                                                   allowed_signers=self.signers, campaign_id=self.fx.kit["campaign_id"])
        self.assertEqual([h["plan_id"] for h in hist], ["cq-df-s01-a1"])

    def test_a_bundle_signed_by_another_key_or_unsigned_is_refused(self):
        work, bundle, anchor = self.pack()
        ref, _ = self.ship(bundle, key="rogue")
        rc, verdict = self.final(work, ref)
        self.assertEqual(rc, 3)
        self.assertNotFinal(verdict, "DESK_UNAUTHENTICATED")
        self.assertEqual(verdict["opened"], [])      # nothing in the bundle was read
        self.git(self.mbp, "fetch", "-q", "origin", "+refs/heads/desk-bundles/*:refs/remotes/origin/desk-bundles/*")
        tree = self.git(self.mbp, "rev-parse", "refs/remotes/origin/desk-bundles/cq-df-s01-a1^{tree}")
        unsigned = self.sp.run(["git", "-C", str(self.mbp), "commit-tree", tree.stdout.strip()], input=(
            "cadence close bundle cq-df-s01-a1\n"), capture_output=True, text=True,
            env={**os.environ, "GIT_AUTHOR_NAME": "x", "GIT_AUTHOR_EMAIL": "x@x", "GIT_COMMITTER_NAME": "x",
                 "GIT_COMMITTER_EMAIL": "x@x"}).stdout.strip()
        self.git(self.mbp, "push", "-q", "-f", "origin", f"{unsigned}:refs/heads/desk-bundles/cq-df-s01-a1")
        self.git(self.air, "fetch", "-q", "origin", "+refs/heads/desk-bundles/*:refs/remotes/origin/desk-bundles/*")
        work2 = self.work()
        rc, verdict = self.final(work2, "refs/remotes/origin/desk-bundles/cq-df-s01-a1")
        self.assertNotFinal(verdict, "DESK_UNAUTHENTICATED")

    def signed(self, files, subject="cadence close bundle cq-df-s01-a1"):
        tree = desk_transport.tree_of(self.mbp, files)
        return self.sp.run(["git", "-C", str(self.mbp), "-c", "gpg.format=ssh", "-c",
                            f"user.signingkey={self.keys['cadence-controller']}", "commit-tree", "-S", tree],
                           input=subject + "\n", capture_output=True, text=True,
                           env={**os.environ, "GIT_AUTHOR_NAME": "c", "GIT_AUTHOR_EMAIL": "c@c",
                                "GIT_COMMITTER_NAME": "c", "GIT_COMMITTER_EMAIL": "c@c"}).stdout.strip()

    def test_a_signed_tree_outside_the_layout_or_a_wrong_anchor_is_refused_unread(self):
        work, bundle, anchor = self.pack()
        transition = {**self.transition(bundle), "manifest_sha256": anchor}
        good = {"transition.json": json.dumps(transition).encode(),
                **{f"bundle/{p.relative_to(bundle).as_posix()}": p.read_bytes() for p in bundle.rglob("*") if p.is_file()}}
        planted = bundle / "hazards/meter/stream-0001.jsonl"
        planted.parent.mkdir(parents=True)
        planted.write_text("{}\n")
        with self.assertRaises(desk_transport.TransportRefusal):     # the packer side refuses it too
            desk_transport.sign_bundle(self.mbp, bundle, transition, plan_id="cq-df-s01-a1",
                                       signing_key=self.keys["cadence-controller"])
        reads = []
        original = desk_transport._git

        def spy(repo, *args, **kw):
            if args[:2] == ("cat-file", "blob"):
                reads.append(args[2])
            return original(repo, *args, **kw)
        for files, pattern in (({**good, "bundle/hazards/meter/stream-0001.jsonl": b"{}\n"}, "outside the bundle layout"),
                               ({**good, "notes.txt": b"x"}, "outside the bundle layout"),
                               ({k: v for k, v in good.items() if k != "transition.json"}, "no transition.json"),
                               ({**good, "transition.json": json.dumps({**transition, "manifest_sha256": "0" * 64}).encode()},
                                "manifest_sha256"),
                               ({**good, "transition.json": json.dumps({**transition, "plan_id": "cq-df-s02-a1"}).encode()},
                                "is for"),
                               ({**good, "transition.json": json.dumps({k: v for k, v in transition.items()
                                                                        if k != "queue"}).encode()}, "missing")):
            commit = self.signed(files)
            reads.clear()
            with mock.patch.object(desk_transport, "_git", spy), \
                    self.assertRaisesRegex(desk_transport.TransportRefusal, pattern):
                desk_transport.extract_bundle(self.mbp, commit, work / "x", allowed_signers=self.signers,
                                              plan_id="cq-df-s01-a1")
            self.assertFalse((work / "x").exists())
            if pattern == "outside the bundle layout":
                self.assertEqual(reads, [])          # refused before any blob is read
        with self.assertRaisesRegex(desk_transport.TransportRefusal, "subject"):
            desk_transport.extract_bundle(self.mbp, self.signed(good), work / "z", allowed_signers=self.signers,
                                          plan_id="cq-df-s02-a1")

    def test_the_transition_record_binds_queue_plan_and_close(self):
        work, bundle, anchor = self.pack()
        ref, _ = self.ship(bundle, status="STOPPED")
        rc, verdict = self.final(work, ref)
        self.assertIn("controller close status STOPPED",
                      next(s["detail"] for s in verdict["named_stops"] if s["code"] == "REFUSAL"))
        self.assertTrue(verdict["next_arm_hold"])
        work, bundle, anchor = self.pack()
        ref, _ = self.ship(bundle, plan_sha256="4" * 64)
        rc, verdict = self.final(work, ref)
        self.assertNotFinal(verdict, "DESK_IDENTITY")
        self.assertIn("span_plan.json is not the plan the transition record names", " ".join(verdict["reasons"]))
        work, bundle, anchor = self.pack()
        ref, _ = self.ship(bundle)
        qp = work / "other-QUEUE.json"
        qp.write_text(json.dumps({**self.fx.queue(), "expires_at": "2026-12-30T00:00:00-08:00"}))
        rc, verdict = self.final(work, ref, "--queue", str(qp))
        self.assertNotFinal(verdict, "DESK_IDENTITY")
        self.assertIn("not the one the transition record armed from", " ".join(verdict["reasons"]))


    def test_the_wrong_principal_and_a_mismatched_verdict_trailer_are_refused(self):
        work, bundle, anchor = self.pack()
        ref, _ = self.ship(bundle, key="cadence-desk")    # a good signature, by the desk's principal
        rc, verdict = self.final(work, ref)
        self.assertNotFinal(verdict, "DESK_UNAUTHENTICATED")
        self.assertIn("signed by cadence-desk, not cadence-controller", " ".join(verdict["reasons"]))
        work, bundle, anchor = self.pack()
        ref, _ = self.ship(bundle)
        rc, verdict = self.final(work, ref)
        raw = (work / "out" / desk_final.VERDICT_NAME).read_bytes()
        files = {desk_final.VERDICT_NAME: raw,
                 desk_final.SUMMARY_NAME: (work / "out" / desk_final.SUMMARY_NAME).read_bytes()}
        for trailer in (f"Verdict-SHA256: {'0' * 64}\nDesk-Final: true", f"Verdict-SHA256: {verdict['verdict_sha256']}\n"
                                                                         "Desk-Final: false"):
            commit = desk_transport._signed_commit(self.air, files, message=f"cadence desk verdict cq-df-s01-a1\n\n{trailer}",
                                                   signing_key=self.keys["cadence-desk"], principal="cadence-desk")
            with self.assertRaisesRegex(desk_transport.TransportRefusal, "does not verify against its commit"):
                desk_transport.read_verdict(self.air, commit, allowed_signers=self.signers, plan_id="cq-df-s01-a1")
        good = desk_transport._signed_commit(
            self.air, files, message=f"cadence desk verdict cq-df-s01-a1\n\nVerdict-SHA256: {verdict['verdict_sha256']}\n"
                                     f"Desk-Final: {str(verdict['desk_final']).lower()}",
            signing_key=self.keys["cadence-desk"], principal="cadence-desk")
        self.assertEqual(desk_transport.read_verdict(self.air, good, allowed_signers=self.signers,
                                                     plan_id="cq-df-s01-a1")[0], verdict)
        with self.assertRaisesRegex(desk_transport.TransportRefusal, "not cadence-desk"):
            desk_transport.read_verdict(self.air, desk_transport._signed_commit(
                self.air, files, message=f"cadence desk verdict cq-df-s01-a1\n\nVerdict-SHA256: {verdict['verdict_sha256']}",
                signing_key=self.keys["cadence-controller"], principal="x"), allowed_signers=self.signers,
                plan_id="cq-df-s01-a1")

    def test_an_unsigned_bundle_is_never_final_outside_synthetic_runs(self):
        work, bundle, anchor = self.pack()
        verdict = self.judge(work, bundle, anchor, allow_unsigned=False)
        self.assertNotFinal(verdict, "DESK_UNAUTHENTICATED")
        self.assertFalse(verdict["transport"]["signed"])
        qp = work / "Q.json"
        qp.write_text(json.dumps(self.fx.queue()))
        with redirect_stdout(io.StringIO()):
            self.assertEqual(cli.main(["final", "--plan-id", "cq-df-s01-a1", "--bundle", str(bundle), "--manifest-sha256",
                                       anchor, "--queue", str(qp), "--kit", str(self.fx.kit_path), "--out",
                                       str(work / "o"), "--lock", str(work / "lock")]), 2)


if __name__ == "__main__":
    unittest.main()
