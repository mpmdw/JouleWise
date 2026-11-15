"""The qualification law ``sha256-qual-v1`` (RL-165 section 8.1; RL-150 section 3.2) on kit schema v1.1, the
per-leg decode cap it carries to the leg spec, and the committed qualification kits. No model, sensor, host
or energy."""
from __future__ import annotations

import copy
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
from scripts import align_r1_rehearsal as r1, cadence_legs_runner as runner, cadence_queue

from tests.cadence import test_kit_v11 as v11t
from tests.cadence.test_kit_v11 import NEW_WINDOW, v11_kit

TMP = os.environ.get("TMPDIR")
ZONE = legsmod.LOCAL_ZONE
KITS = runner.ROOT / "docs/process/cadence/kits"
ANCHOR = legsmod.ANCHOR_PREFILL_TOKENS
A_TOKENS = [2000, 10000, ANCHOR, ANCHOR]   # RL-165 section 8.1: per span one 2k, one 10k, two 19k type-A legs
PAIRS = [{"prefill_tokens": ANCHOR, "decode_tokens": [3724, 4096]},
         {"prefill_tokens": ANCHOR, "decode_tokens": [3151, 4096]}]
QUAL = {"cl-qual-01": 2026111422, "cl-qual-02": 2026111423, "cl-qual-03": 2026111424}


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


class ChecklistSoakWindowIsTheDrivers(unittest.TestCase):
    """At a pin whose R1 driver soaks outside 02:00-02:35 only, the arm checklist has no 10:50-13:15 refusal."""

    def test_checklist_follows_the_driver_constant(self):
        self.assertEqual(cadence_queue.soak_window(), r1.OS_BATCH_WINDOW_LOCAL)
        with tempfile.TemporaryDirectory(dir=TMP) as td:
            kit_path, obs_path = Path(td) / "kit.json", Path(td) / "obs.json"
            kit_path.write_text(json.dumps(qual_kit(), indent=1))
            t0 = local("2026-11-19T11:00")
            obs_path.write_text(json.dumps({**v11t.FreeT0Checklist.GOOD, "t0_epoch_s": t0, "end_by_epoch_s": t0 + 26210}))
            buffer = io.StringIO()
            with redirect_stdout(buffer):
                code = cadence_queue.main(["checklist", "--kit", str(kit_path), "--kit-sha256", "f" * 64,
                                           "--observations", str(obs_path), "--batch-window", "02:00-02:35"])
        late = r1.OS_BATCH_WINDOW_LOCAL[0][0] < 10
        self.assertEqual(code, 0 if late else 1, buffer.getvalue())


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
            for key in ("runner", "model", "leg_defaults", "stop_rules", "span_template", "checklist", "looks", "desk",
                        "ruling"):
                self.assertEqual(kit[key], dev03[key], key)

    def test_each_ratio_runs_both_orders_across_the_three_blocks(self):
        orders = {}
        for kit in self.kits().values():
            for span in spans_of(kit["legs"]):
                pair = [leg for leg in span if leg["leg_type"] == "L"]
                orders.setdefault(pair[0]["pair"], set()).add(pair[0]["decode_tokens"] == 4096)
        self.assertEqual(orders, {"p1": {True, False}, "p2": {True, False}})

    def test_frozen_paths_hash_at_the_frozen_commit(self):
        for kit in self.kits().values():
            have = subprocess.run(["git", "-C", str(runner.ROOT), "cat-file", "-e",
                                   kit["frozen"]["commit"] + "^{commit}"], capture_output=True)
            if have.returncode:
                self.skipTest("frozen commit not in this clone")
            self.assertEqual(kitmod.verify_frozen(kit, runner.ROOT), [])


if __name__ == "__main__":
    unittest.main()
