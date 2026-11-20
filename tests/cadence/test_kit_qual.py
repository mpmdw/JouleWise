"""The qualification law ``sha256-qual-v1`` (RL-165 section 8.1; RL-150 section 3.2) on kit schema v1.1, the
per-leg decode cap it carries to the leg spec, and the committed qualification kits. No model, sensor, host
or energy."""
from __future__ import annotations

import copy
import hashlib
from datetime import datetime
import io
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest
from contextlib import redirect_stdout

from joulewise.cadence import kit as kitmod, kit_v11, legs as legsmod
from scripts import cadence_legs_runner as runner, cadence_queue

from tests.cadence import test_kit_v11 as v11t
from tests.cadence.test_kit_v11 import NEW_WINDOW, v11_kit

TMP = os.environ.get("TMPDIR")
ZONE = legsmod.LOCAL_ZONE
KITS = runner.ROOT / "docs/process/cadence/kits"
ANCHOR = legsmod.ANCHOR_PREFILL_TOKENS
A_TOKENS = [2000, 10000, ANCHOR, ANCHOR]   # RL-165 section 8.1: per span one 2k, one 10k, two 19k type-A legs
PAIRS = [{"prefill_tokens": ANCHOR, "decode_tokens": [3724, 4096]},
         {"prefill_tokens": ANCHOR, "decode_tokens": [3151, 4096]}]
# Seeds (RL-165 section 8.1): the first unused numbers after the reserved 07-21. qual-03 takes the first seed from
# 2026111424 up with which the three blocks run each ratio in both orders and each pair in both spans (24-27 fail).
QUAL = {"cl-qual-01": 2026111422, "cl-qual-02": 2026111423, "cl-qual-03": 2026111428}


def local(text):
    return datetime.fromisoformat(text).replace(tzinfo=ZONE).timestamp()


def qlaw(**overrides):
    value = {"method": kit_v11.QUAL_LAW, "master_seed": 2026111499, "n_legs": 12, "bands": ["q0"], "spans": 2,
             "span_a_tokens": list(A_TOKENS), "pairs": copy.deepcopy(PAIRS), "g0_shapes": ["own", "span"]}
    value.update(overrides)
    return value


def qual_kit(seed_law=None, validate=True):
    return v11_kit(validate=validate, seed_law=seed_law or qlaw(), leg_budget_s=1660)   # the dev kits' ceiling


def spans_of(legs, per=6):
    return [legs[i:i + per] for i in range(0, len(legs), per)]


class QualLaw(unittest.TestCase):
    def check_design(self, legs, shapes=("own", "span")):
        self.assertEqual(len(legs), 12)
        a = [leg for leg in legs if leg["leg_type"] == "A"]
        pairs = [leg for leg in legs if leg["leg_type"] == "L"]
        # Six type A, two per size, plus two type A at 19,458 (the type-M slots); every type A at the kit's cap.
        self.assertEqual(sorted(leg["prefill_tokens"] for leg in a), sorted(A_TOKENS * 2))
        self.assertEqual({leg["decode_tokens"] for leg in a}, {4096})
        self.assertEqual({leg["pair"] for leg in a}, {None})
        # Two type-L pairs at 19,458: 3,724 with 4,096 and 3,151 with 4,096.
        self.assertEqual({leg["prefill_tokens"] for leg in pairs}, {ANCHOR})
        by_pair = {}
        for leg in pairs:
            by_pair.setdefault(leg["pair"], []).append(leg)
        self.assertEqual({k: sorted(x["decode_tokens"] for x in v) for k, v in by_pair.items()},
                         {"p1": [3724, 4096], "p2": [3151, 4096]})
        for span in spans_of(legs):
            # A span's first leg is type A and not part of a pair; it judges its G0 against its own capture.
            self.assertEqual((span[0]["leg_type"], span[0]["pair"], span[0]["g0_shape"]), ("A", None, "own"))
            # One pair per span, its two legs adjacent.
            idx = [i for i, leg in enumerate(span) if leg["leg_type"] == "L"]
            self.assertEqual(len(idx), 2)
            self.assertEqual(idx[1], idx[0] + 1)
            self.assertEqual(span[idx[0]]["pair"], span[idx[1]]["pair"])
            # Each span: one 2k, one 10k and two 19k type A.
            self.assertEqual(sorted(leg["prefill_tokens"] for leg in span if leg["leg_type"] == "A"), sorted(A_TOKENS))
            expected = "span" if "span" in shapes else "own"
            self.assertEqual({leg["g0_shape"] for leg in span[1:]}, {expected})

    def test_design_holds_over_many_seeds(self):
        firsts, positions = set(), set()
        for seed in range(40):
            legs = kit_v11.generate_legs("cl-qual-xx", qlaw(master_seed=seed), {"decode_tokens": 4096})
            self.check_design(legs)
            for span in spans_of(legs):
                idx = [i for i, leg in enumerate(span) if leg["leg_type"] == "L"]
                positions.add(idx[0])
                firsts.add((span[idx[0]]["pair"], span[idx[0]]["decode_tokens"]))
        # Positions and the pair's first leg are drawn, not fixed.
        self.assertEqual(positions, {1, 2, 3, 4})
        self.assertEqual(firsts, {("p1", 3724), ("p1", 4096), ("p2", 3151), ("p2", 4096)})

    def test_seeds_and_bands_are_v1s(self):
        legs = kit_v11.generate_legs("cl-qual-01", qlaw(master_seed=2026111422), {"decode_tokens": 4096})
        v1_legs = kitmod.generate_legs("cl-qual-01", {"method": "sha256-v1", "master_seed": 2026111422,
                                                      "n_legs": 12, "bands": ["q0"]})
        self.assertEqual([(x["leg_id"], x["seed"], x["start_band"]) for x in legs],
                         [(x["leg_id"], x["seed"], x["start_band"]) for x in v1_legs])

    def test_the_law_is_pinned(self):
        legs = kit_v11.generate_legs("cl-qual-01", qlaw(master_seed=2026111422), {"decode_tokens": 4096})
        self.assertEqual([(leg["leg_type"], leg["prefill_tokens"], leg["decode_tokens"]) for leg in legs],
                         [("A", ANCHOR, 4096), ("A", 10000, 4096), ("A", ANCHOR, 4096), ("L", ANCHOR, 3151),
                          ("L", ANCHOR, 4096), ("A", 2000, 4096), ("A", 10000, 4096), ("A", ANCHOR, 4096),
                          ("L", ANCHOR, 4096), ("L", ANCHOR, 3724), ("A", ANCHOR, 4096), ("A", 2000, 4096)])

    def test_own_shaped_variant_differs_in_shape_only(self):
        span = kit_v11.generate_legs("cl-qual-01", qlaw(), {"decode_tokens": 4096})
        own = kit_v11.generate_legs("cl-qual-01", qlaw(g0_shapes=["own"]), {"decode_tokens": 4096})
        self.check_design(own, shapes=("own",))
        self.assertEqual([{k: v for k, v in leg.items() if k != "g0_shape"} for leg in span],
                         [{k: v for k, v in leg.items() if k != "g0_shape"} for leg in own])

    def test_the_cell_law_is_unchanged(self):
        # sha256-cells-v1 keeps its legs and its leg keys (dev-03, dev-04 and dev-05 still validate).
        legs = kit_v11.generate_legs("cl-dev-03", {"method": kit_v11.LAW, "master_seed": 2026111403, "n_legs": 12,
                                                   "bands": ["q0"], "prompt_tokens": [2000, 10000, ANCHOR],
                                                   "g0_shapes": ["own", "span"]}, {"decode_tokens": 4096})
        self.assertEqual(set(legs[0]), kit_v11.LEG_KEYS)

    def test_law_refusals(self):
        bad = (qlaw(n_legs=10), qlaw(spans=3), qlaw(pairs=PAIRS[:1]), qlaw(g0_shapes=["span"]),
               qlaw(span_a_tokens=[]), qlaw(pairs=[{**PAIRS[0], "decode_tokens": [4096, 4096]}, PAIRS[1]]),
               qlaw(pairs=[{**PAIRS[0], "decode_tokens": [4097, 4096]}, PAIRS[1]]),
               qlaw(pairs=[{**PAIRS[0], "decode_tokens": [3724]}, PAIRS[1]]),
               qlaw(pairs=[{**PAIRS[0], "extra": 1}, PAIRS[1]]), qlaw(prompt_tokens=[2000]))
        for law in bad:
            with self.subTest(law=law):
                with self.assertRaises(kitmod.KitError):
                    kit_v11.validate_kit(qual_kit(law, validate=False), batch_window=NEW_WINDOW)

    def test_decode_range_is_the_leg_specs(self):
        self.assertEqual(kit_v11.DECODE_TOKENS_RANGE, legsmod.DECODE_TOKENS_RANGE)


class QualValidator(unittest.TestCase):
    def refused(self, kit, fragment):
        with self.assertRaises(kitmod.KitError) as ctx:
            kit_v11.validate_kit(kit, batch_window=NEW_WINDOW)
        self.assertTrue(any(fragment in p for p in ctx.exception.problems), ctx.exception.problems)

    def test_valid_and_regenerated(self):
        kit = qual_kit()
        self.assertEqual(kitmod.deny_scan(kit), [])
        i = next(i for i, leg in enumerate(kit["legs"]) if leg["decode_tokens"] == 3724)
        kit["legs"][i]["decode_tokens"] = 4096
        self.refused(kit, "not the cell law's list")
        kit = qual_kit()
        kit["legs"][0]["leg_type"] = "L"
        self.refused(kit, "not the cell law's list (first difference at index 0")
        kit = qual_kit()
        del kit["legs"][2]["pair"]
        self.refused(kit, "legs[2]: missing key 'pair'")

    def test_cell_law_kits_take_no_qual_keys(self):
        kit = v11_kit()
        kit["legs"][0]["leg_type"] = "A"
        self.refused(kit, "legs[0]: unknown key 'leg_type'")


class QualLegsReachTheRuntime(unittest.TestCase):
    def test_each_legs_own_cap_is_its_spec_and_the_labels_stay_in_the_kit(self):
        kit = qual_kit()
        specs = legsmod.leg_specs(kit)
        self.assertEqual([s["decode_tokens"] for s in specs], [leg["decode_tokens"] for leg in kit["legs"]])
        for spec in specs:
            self.assertNotIn("leg_type", spec)
            self.assertNotIn("pair", spec)
        # On 6 + 6, each span's first leg is own (its capture is the reference); the ten others consume.
        roles = []
        for ids in (["L%03d" % i for i in range(1, 7)], ["L%03d" % i for i in range(7, 13)]):
            roles += [s.get("g0_role") for s in legsmod.leg_specs(kit, ids)]
        self.assertEqual(roles, [None] + ["consume"] * 5 + [None] + ["consume"] * 5)

    def test_plan_budgets_follow_each_legs_cap(self):
        kit = qual_kit()
        ids = ["L%03d" % i for i in range(1, 7)]
        plan = legsmod.plan_span(kit, t0_epoch=local("2026-11-19T02:40"), windows=[NEW_WINDOW], leg_ids=ids)
        budgets = {(spec["decode_tokens"], spec.get("g0_role")): leg["budget_s"]
                   for leg, spec in zip(plan["legs"], legsmod.leg_specs(kit, ids)) if spec["prefill_tokens"] == ANCHOR}
        short = next(cap for cap, role in budgets if cap < 4096)
        self.assertLess(budgets[(short, "consume")], budgets[(4096, "consume")])
        self.assertEqual(plan["worst_case_s"], 24750)

    def test_mock_span_records_each_cap(self):
        kit = qual_kit()
        ids = ["L%03d" % i for i in range(1, 7)]
        with tempfile.TemporaryDirectory(dir=TMP) as td:
            out = Path(td) / "span"
            rc, summary, stops, _ = runner.run_mock(kit=kit, kit_sha256="f" * 64, output=out,
                                                    t0_epoch=local("2026-11-19T02:40"), windows=[NEW_WINDOW],
                                                    leg_ids=ids)
            self.assertEqual((rc, stops), (0, []))
            self.assertTrue(all(leg["admitted"] for leg in summary["legs"]))
            for leg in kit["legs"][:6]:
                record = json.loads((out / "legs" / leg["leg_id"] / "leg_record.json").read_text())
                self.assertEqual((record["spec"]["decode_tokens"], record["result"]["decode_cap"]),
                                 (leg["decode_tokens"], leg["decode_tokens"]))

    def test_gen_legs_cli_is_the_law(self):
        buffer = io.StringIO()
        with redirect_stdout(buffer):
            code = cadence_queue.main(["gen-legs", "--law", kit_v11.QUAL_LAW, "--campaign-id", "cl-test-11",
                                       "--master-seed", "2026111499", "--n-legs", "12", "--bands", "q0",
                                       "--spans", "2", "--span-a-tokens", "2000,10000,19458,19458",
                                       "--pairs", "19458:3724:4096,19458:3151:4096", "--g0-shapes", "own,span",
                                       "--decode-tokens", "4096"])
        self.assertEqual(code, 0)
        out = json.loads(buffer.getvalue())
        self.assertEqual((out["seed_law"], out["legs"]), (qlaw(), qual_kit()["legs"]))
        with redirect_stdout(io.StringIO()):
            self.assertEqual(cadence_queue.main(["gen-legs", "--law", kit_v11.QUAL_LAW, "--campaign-id", "c-id",
                                                 "--master-seed", "1", "--n-legs", "12", "--bands", "q0",
                                                 "--decode-tokens", "4096"]), 2)


class ChecklistHasNoClockWindow(unittest.TestCase):
    """RL-171: the qualification arm checklist has no 10:50-13:15 refusal and no 01:50 fence; no window by default."""

    def test_checklist_admits_1100_and_a_span_through_0200(self):
        self.assertFalse(hasattr(cadence_queue, "soak_window"))
        with tempfile.TemporaryDirectory(dir=TMP) as td:
            kit_path, obs_path = Path(td) / "kit.json", Path(td) / "obs.json"
            kit_path.write_text(json.dumps(qual_kit(), indent=1))
            for when in ("2026-11-19T11:00", "2026-11-19T00:30"):
                t0 = local(when)
                obs_path.write_text(json.dumps({**v11t.FreeT0Checklist.GOOD, "t0_epoch_s": t0,
                                                "end_by_epoch_s": t0 + 26210 + 1950}))
                buffer = io.StringIO()
                with redirect_stdout(buffer):
                    code = cadence_queue.main(["checklist", "--kit", str(kit_path), "--kit-sha256", "f" * 64,
                                               "--observations", str(obs_path)])
                self.assertEqual(code, 0, (when, buffer.getvalue()))

    def test_qual_span_plans_at_0030_and_1100_with_no_window(self):
        kit = qual_kit()
        ids = ["L%03d" % i for i in range(1, 7)]
        for when in ("2026-11-19T00:30", "2026-11-19T11:00"):
            plan = legsmod.plan_span(kit, t0_epoch=local(when), windows=runner.default_windows(), leg_ids=ids)
            self.assertEqual((plan["worst_case_s"], plan["batch_windows"]), (24750, []))


class CommittedQualKits(unittest.TestCase):
    """cl-qual-01 to cl-qual-03 (RL-165 section 8.1), pinned at the qualification merge pin."""

    def kits(self):
        out = {}
        for cid in QUAL:
            path = KITS / f"{cid}.v1.1.json"
            if not path.exists():
                self.skipTest(f"{path.name} not on this branch")
            out[cid] = kitmod.load_kit(path, batch_window=NEW_WINDOW)[0]
        return out

    def test_shape_seeds_and_frozen_set(self):
        dev03, _ = kitmod.load_kit(KITS / "cl-dev-03.v1.1.json", batch_window=NEW_WINDOW)
        for cid, kit in self.kits().items():
            self.assertEqual((kit["campaign_id"], kit["seed_law"]["master_seed"]), (cid, QUAL[cid]))
            self.assertEqual(kit["seed_law"], qlaw(master_seed=QUAL[cid]))
            QualLaw.check_design(self, kit["legs"])
            self.assertEqual(set(kit["frozen"]["paths"]), set(dev03["frozen"]["paths"]))
            self.assertEqual(kitmod.deny_scan(kit), [])
            for key in ("runner", "model", "leg_defaults", "checklist", "looks", "desk", "ruling"):
                self.assertEqual(kit[key], dev03[key], key)
            # dev-03's template with spans of at most six legs (#794 cold seat F2).
            self.assertEqual(kit["span_template"], {**dev03["span_template"], "legs_per_span": 6})
            self.assertIn("2026111424 to 2026111427 are retired", kit["title"])    # RL-167 Part B Q3
            # The stop rules are dev-03's; the notes add the type-L budgets only.
            self.assertEqual({k: v for k, v in kit["stop_rules"].items() if k != "notes"},
                             {k: v for k, v in dev03["stop_rules"].items() if k != "notes"})
            self.assertIn("1,611 s at 3,724 and 1,563 s at 3,151", kit["stop_rules"]["notes"])
            self.assertEqual(kit["stop_rules"]["notes"].replace(
                "A type-L leg (19,458 tokens, a span-reference leg in this kit) is modeled at its own decode cap: "
                "1,611 s at 3,724 and 1,563 s at 3,151. ", ""), dev03["stop_rules"]["notes"])
            rules = {r["id"] for r in kit["inclusion_rules"]}
            self.assertEqual(rules, {r["id"] for r in dev03["inclusion_rules"]} - {"pilot_counted"})

    def test_each_ratio_runs_both_orders_and_both_spans_across_the_three_blocks(self):
        orders, spans = {}, {}
        for kit in self.kits().values():
            for index, span in enumerate(spans_of(kit["legs"])):
                pair = [leg for leg in span if leg["leg_type"] == "L"]
                orders.setdefault(pair[0]["pair"], set()).add(pair[0]["decode_tokens"] == 4096)
                spans.setdefault(pair[0]["pair"], set()).add(index)
        self.assertEqual(orders, {"p1": {True, False}, "p2": {True, False}})
        self.assertEqual(spans, {"p1": {0, 1}, "p2": {0, 1}})

    def test_the_seed_rule(self):
        def features(cid, seed):
            legs = kit_v11.generate_legs(cid, qlaw(master_seed=seed), {"decode_tokens": 4096})
            out = []
            for index, span in enumerate(spans_of(legs)):
                pair = [leg for leg in span if leg["leg_type"] == "L"]
                out.append((pair[0]["pair"], index, pair[0]["decode_tokens"] == 4096))
            return out
        first_two = features("cl-qual-01", QUAL["cl-qual-01"]) + features("cl-qual-02", QUAL["cl-qual-02"])
        def balanced(seed):
            rows = first_two + features("cl-qual-03", seed)
            return all({o for q, _, o in rows if q == p} == {True, False} and {i for q, i, _ in rows if q == p} == {0, 1}
                       for p in ("p1", "p2"))
        self.assertEqual(next(s for s in range(2026111424, 2026111499) if balanced(s)), QUAL["cl-qual-03"])

    def test_frozen_paths_hash_at_the_frozen_commit(self):
        for kit in self.kits().values():
            have = subprocess.run(["git", "-C", str(runner.ROOT), "cat-file", "-e",
                                   kit["frozen"]["commit"] + "^{commit}"], capture_output=True)
            if have.returncode:
                self.skipTest("frozen commit not in this clone")
            self.assertEqual(kitmod.verify_frozen(kit, runner.ROOT), [])


class QualQueues(unittest.TestCase):
    """#794 cold seat F1 and F2: a held queue does not arm; validate-queue binds rosters to the law's spans."""

    def queue(self, rosters, halt=None):
        kit_path = "docs/process/cadence/kits/cl-qual-01.v1.1.json"
        sha = hashlib.sha256((runner.ROOT / kit_path).read_bytes()).hexdigest()
        return {"schema": "joulewise.cadence_queue.v1", "queue_id": "cq-cl-qual-01", "expires_at": "2026-11-22T23:59:00-08:00",
                "halt": halt, "standing_notice": None,
                "spans": [{"seq": i, "span_id": f"qual-01-s{i:02d}", "block_id": "qual-01",
                           "kit": {"path": kit_path, "sha256": sha}, "legs": legs, "attempt": 1,
                           "not_before": "2026-11-19", "rerun_of": None} for i, legs in enumerate(rosters, 1)]}

    def validate(self, doc):
        if not (KITS / "cl-qual-01.v1.1.json").exists():
            self.skipTest("cl-qual-01 not on this branch")
        with tempfile.TemporaryDirectory(dir=TMP) as td:
            path = Path(td) / "queue.json"
            path.write_text(json.dumps(doc))
            out = io.StringIO()
            with redirect_stdout(out):
                code = cadence_queue.main(["validate-queue", str(path), "--kits-root", str(runner.ROOT)])
            return code, out.getvalue()

    def test_law_spans_validate_and_cuts_refuse(self):
        ids = ["L%03d" % i for i in range(1, 13)]
        code, out = self.validate(self.queue([ids[:6], ids[6:]]))
        self.assertEqual(code, 0, out)
        for rosters, fragment in (([ids[:4], ids[4:6]], "splits type-L pair p2"),
                                  ([ids[:3], ids[3:6]], "starts on L004"),
                                  ([ids[3:9]], "crosses the law's spans"),
                                  ([ids], "12 > span_template.legs_per_span")):   # legs_per_span 6 (frozen queue.py)
            with self.subTest(rosters=rosters):
                code, out = self.validate(self.queue(rosters))
                self.assertEqual(code, 1)
                self.assertIn(fragment, out)

    def test_a_held_queue_does_not_arm(self):
        from joulewise.cadence import queue as q
        ids = ["L%03d" % i for i in range(1, 13)]
        held = self.queue([ids[:6], ids[6:]], halt={"reason": "HOLD_FOR_FIT_FREEZE", "by": "builder",
                                                   "at": "2026-11-14T21:40:00-08:00"})
        self.assertEqual(self.validate(held)[0], 0)
        decision = q.next_action(q.validate_queue(held), {}, (), local("2026-11-19T02:40"))
        self.assertEqual(decision.action, "halt")
        held["halt"] = None
        self.assertEqual(q.next_action(q.validate_queue(held), {}, (), local("2026-11-19T02:40")).action, "arm")


if __name__ == "__main__":
    unittest.main()
