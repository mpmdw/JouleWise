"""Tiny in-memory contract vectors for lm-ctl-01. All observations are invented.

python3 -B synthetic_acceptance.py             # check the reference vectors
python3 -B synthetic_acceptance.py --builder   # future pure adapter, RED until built
No data-path argument, discovery, runner, sampler, or look entry point.
"""
import hashlib
import json
import sys
import unittest
from copy import deepcopy


def digest(value):
    raw = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(raw).hexdigest()


IDS = tuple(f"L{i:03}" for i in range(1, 13))
KINDS = ("extra-turn", "hidden", "cpu", "cpu", "hidden", "split",
         "plain", "hidden", "hidden", "cpu", "hidden", "hidden")
HIDDEN = (0, 512, 0, 0, 128, 0, 0, 256, 512, 0, 256, 128)
BURN = (0, 0, 30, 90, 0, 0, 0, 0, 0, 10, 0, 0)
CAPS = {"extra-turn": (1024, 1024), "cpu": (512, 512),
        "hidden": (1024,), "split": (342, 341, 341), "plain": (1024,)}
PAIR_LABEL = "equal counts, same prompt and seed, different context depth"
LAYOUT = [list(IDS[:3]), list(IDS[3:])]
CHANNELS = ("gpu_rail", "cpu_rail", "rail_sum", "dc_in")


def counts(call_counts):
    return {"prompt": 2000 * len(call_counts), "decoded": sum(call_counts)}


def steps(kind):
    visible = ["visible"] * len(CAPS[kind])
    if kind == "hidden":
        visible.insert(0, "hidden")
    elif kind == "cpu":
        visible.insert(1, "cpu")
    elif kind == "split":
        visible = ["visible", "gap", "visible", "gap", "visible"]
    return ["G0", *visible, "recovery", "sampling_stop"]


def example():
    # These commitments stand in for independently authenticated Git/receipt records.
    # The invented tick order is ledger order. Nothing here is a timestamp or a real pin.
    plan = dict(look="lm-ctl-01", kit="cl-ctl-01", kit_sha=digest("toy-issued-kit"),
                runner="a" * 40, master_seed=2026111601, layout=deepcopy(LAYOUT),
                freeze_seq=10, first_open_seq=12, pilot_pass_seq=4, remainder_seq=5,
                split_hand_pass=True, instrument=dict(look_id="lm-inst-01",
                    manifest_sha=digest("toy-instrument-manifest"), kit_id="f2-inst-02",
                    leg="L001", channel="gpu_rail", window_s=10, print_id="gain.floor_in_tokens"),
                manifest_sha=digest("toy-manifest"),
                code_sha=digest("toy-code"), schema_sha=digest("toy-schema"))
    public = dict(look_id=plan["look"], manifest_sha256=plan["manifest_sha"],
                  commit="b" * 40, stage1_sha256=digest("toy-census"), n_legs=12)
    anchors, rows = {}, []
    for i, (leg, kind) in enumerate(zip(IDS, KINDS)):
        span = 1 if i < 3 else 2
        capture = "L001" if span == 1 else "L004"
        anchor = digest(["toy-reference", span, capture, 1])
        calls = list(CAPS[kind])
        work = dict(kind=kind, steps=steps(kind), hidden_tokens=HIDDEN[i], visible=calls, cpu_s=BURN[i],
                    recovery_s=600, gap_s=10 if kind == "split" else 0,
                    start_ctx=[2000] * (len(calls) + bool(HIDDEN[i])),
                    seed=106 if kind in {"split", "plain"} else 101 + i,
                    prompt=digest("invented prompt identity"))
        identity = [plan["kit"], plan["kit_sha"], plan["runner"], span, leg, 1]
        anchors[leg] = dict(identity=identity, role="capture" if leg == capture else "consume",
                            reference=anchor, script_sha=digest(work))
        rows.append(dict(leg=leg, identity=identity.copy(), reference=anchor,
                         role=anchors[leg]["role"], work=work, logged=[counts(calls)]))
    # Synthetic *outputs*, already tabulated. No reader or energy integration.
    # 1 J = 1% of the toy total. Deliberately make 10/30/90 order differ from leg order.
    private = dict(pair_label=PAIR_LABEL, qualifier="yes",
                   phases={ch: [99] * 12 for ch in CHANNELS},
                   totals={ch: [100] * 12 for ch in CHANNELS},
                   cpu_other_by_seconds={10: 3, 30: 6, 90: 12})
    public["stage1_sha256"] = digest(anchors)
    committed = dict(plan=deepcopy(plan), legs=anchors, public=public, qualifier_ran=True)
    candidate = dict(plan=plan, legs=rows, private=private, public=deepcopy(public))
    return committed, candidate


def require(ok, reason):
    if not ok:
        raise ValueError(reason)


def check(committed, candidate):
    """Fixture oracle on toy projections. Reasons and keys here are test API only."""
    p = candidate["plan"]
    require(set(p) == set(committed["plan"]), "plan shape")
    for field in ("look", "kit", "kit_sha", "runner"):
        require(p[field] == committed["plan"][field], "identity")
    require(p["master_seed"] == 2026111601 and p["layout"] == LAYOUT, "layout")
    require(type(p["pilot_pass_seq"]) is int and 0 < p["pilot_pass_seq"] < p["remainder_seq"], "pilot hand-read")
    require(p["split_hand_pass"] is True, "split hand-read")
    require(0 < p["freeze_seq"] < p["first_open_seq"], "pre-read freeze")
    require(p == committed["plan"], "freeze or evidence binding")
    rows = candidate["legs"]
    require([r["leg"] for r in rows] == list(IDS), "roster")
    for i, r in enumerate(rows):
        a = committed["legs"][r["leg"]]
        require(r["identity"] == a["identity"], "identity")
        require((r["role"], r["reference"]) == (a["role"], a["reference"]), "reference")
        w = r["work"]
        require(digest(w) == a["script_sha"], "script digest")
        require(w["kind"] == KINDS[i], "script kind")
        require(w["steps"] == steps(KINDS[i]), "physical order")
        require(len(r["logged"]) == 1 and r["logged"][0] == counts(w["visible"]), "envelope")
    split, plain = (r["work"] for r in rows[5:7])
    require(sum(split["visible"]) == sum(plain["visible"]), "pair count")
    require((split["seed"], split["prompt"]) == (plain["seed"], plain["prompt"]), "pair identity")
    require(split["start_ctx"] == [2000, 2000, 2000] and plain["start_ctx"] == [2000], "context")
    # Largest simultaneous context, not the last call in a concatenated transcript.
    split_depth = max(c + n for c, n in zip(split["start_ctx"], split["visible"]))
    plain_depth = plain["start_ctx"][0] + plain["visible"][0]
    require(plain_depth - split_depth == 682, "context")
    for i, r in enumerate(rows):
        w = r["work"]
        require(w["visible"] == list(CAPS[KINDS[i]]) and w["hidden_tokens"] == HIDDEN[i]
                and w["cpu_s"] == BURN[i] and w["gap_s"] == (10 if i == 5 else 0)
                and w["recovery_s"] == 600, "toy script")
    private = candidate["private"]
    require(set(private) == {"pair_label", "qualifier", "phases", "totals",
                             "cpu_other_by_seconds"}, "private disclosure")
    require(private["pair_label"] == PAIR_LABEL, "private disclosure")
    for field in ("phases", "totals"):
        grid = private[field]
        require(set(grid) == set(CHANNELS) and all(
            type(col) is list and len(col) == 12 and all(type(x) is int for x in col)
            for col in grid.values()), "private disclosure")
    cpu = private["cpu_other_by_seconds"]
    require(set(cpu) == {10, 30, 90} and all(type(x) is int for x in cpu.values()),
            "private disclosure")
    closes = all(abs(s - t) * 100 <= t for ch in CHANNELS
                 for s, t in zip(private["phases"][ch], private["totals"][ch]))
    word = "yes" if closes and cpu[10] < cpu[30] < cpu[90] else "no"
    if not committed["qualifier_ran"]:
        word = "not_run"
    require(private["qualifier"] == word, "qualifier")
    # Compare exact toy public bytes (True, 1.0 and integers have distinct encodings).
    require(digest(candidate["public"]) == digest(committed["public"]), "public disclosure")


VALIDATE = check


class Contract(unittest.TestCase):
    def setUp(self):
        self.c, self.x = example()

    def refuses(self, reason):
        with self.assertRaisesRegex(ValueError, reason):
            VALIDATE(self.c, self.x)

    def attest_work(self, i):
        # Model an authentic but scientifically mismatched script, not merely a bad hash.
        row = self.x["legs"][i]
        self.c["legs"][row["leg"]]["script_sha"] = digest(row["work"])

    def test_counted_layout_and_private_qualifier(self):
        VALIDATE(self.c, self.x)

    def test_wrong_identity(self):
        for field in ("look", "kit", "kit_sha", "runner"):
            with self.subTest(field=field):
                self.c, self.x = example()
                self.x["plan"][field] = "wrong"
                self.refuses("identity")
        for index in range(6):
            with self.subTest(identity_component=index):
                self.c, self.x = example()
                self.x["legs"][5]["identity"][index] = "foreign"
                self.refuses("identity")

    def test_layout_and_consumers(self):
        for field, value in (("master_seed", 1), ("layout", [list(IDS[:4]), list(IDS[4:])])):
            self.c, self.x = example()
            self.x["plan"][field] = value
            self.refuses("layout")
        self.c, self.x = example()
        self.x["legs"][6]["reference"] = self.x["legs"][0]["reference"]
        self.refuses("reference")
        self.c, self.x = example()
        self.x["legs"][3]["role"] = "consume"
        self.refuses("reference")

    def test_script_digest_and_visible_envelope(self):
        self.x["legs"][1]["work"]["hidden_tokens"] += 1
        self.refuses("script digest")
        self.c, self.x = example()
        self.x["legs"][1]["logged"][0]["decoded"] += HIDDEN[1]
        self.refuses("envelope")
        self.c, self.x = example()
        self.x["legs"][5]["logged"] = [counts([n]) for n in CAPS["split"]]
        self.refuses("envelope")

    def test_physical_order_and_sampled_recovery(self):
        for i, sequence in ((1, ["G0", "visible", "hidden", "recovery", "sampling_stop"]),
                            (0, ["G0", "visible", "visible", "sampling_stop", "recovery"])):
            self.c, self.x = example()
            self.x["legs"][i]["work"]["steps"] = sequence
            self.attest_work(i)
            self.refuses("physical order")

    def test_pair_count_seed_prompt_and_depth(self):
        for field, value, reason in (("visible", [342, 341, 340], "pair count"),
                                     ("seed", 999, "pair identity"), ("prompt", digest("other"), "pair identity"),
                                     ("start_ctx", [2000, 2342, 2683], "context")):
            with self.subTest(field=field):
                self.c, self.x = example()
                split = self.x["legs"][5]
                split["work"][field] = value
                split["logged"] = [counts(split["work"]["visible"])]
                self.attest_work(5)
                self.refuses(reason)

    def test_hand_read_and_freeze_order(self):
        for field, value, reason in (("pilot_pass_seq", None, "pilot hand-read"),
                                     ("pilot_pass_seq", 6, "pilot hand-read"),
                                     ("split_hand_pass", False, "split hand-read"),
                                     ("freeze_seq", 12, "pre-read freeze"),
                                     ("code_sha", digest("substitution"), "binding"),
                                     ("schema_sha", digest("substitution"), "binding"),
                                     ("manifest_sha", digest("substitution"), "binding")):
            self.c, self.x = example()
            self.x["plan"][field] = value
            # Authentic omission, late pass or late freeze still refuses.
            if field.endswith(("_seq", "_pass")):
                self.c["plan"][field] = value
            self.refuses(reason)

    def test_instrument_input_binding(self):
        for key, value in (("look_id", "lm-stab-01"), ("channel", "cpu_rail"),
                           ("manifest_sha", digest("foreign instrument")), ("window_s", 128)):
            self.c, self.x = example()
            self.x["plan"]["instrument"][key] = value
            self.refuses("binding")

    def test_exact_disclosure(self):
        for field in ("K_threshold", "S_score", "K_outcome", "S_word", "token_ids", "series_member"):
            self.c, self.x = example()
            self.x["private"]["phases"][field] = [0] * 12
            self.refuses("private disclosure")
        self.c, self.x = example()
        self.x["private"]["pair_label"] = "invented generated text"
        self.refuses("private disclosure")
        self.c, self.x = example()
        self.x["private"]["qualifier"] = "detected"
        self.refuses("qualifier")
        for field, value in (("generated_text", "invented"), ("qualifier", "yes"), ("n_legs", 12.0)):
            self.c, self.x = example()
            self.x["public"][field] = value
            self.refuses("public disclosure")

    def test_unrun_qualifier_has_no_public_word(self):
        self.c["qualifier_ran"] = False
        self.refuses("qualifier")
        self.x["private"]["qualifier"] = "not_run"
        VALIDATE(self.c, self.x)

    def test_closure_and_burn_order(self):
        for fault in ("closure", "burn"):
            self.c, self.x = example()
            if fault == "closure":
                self.x["private"]["phases"]["dc_in"][-1] = 98
            else:
                self.x["private"]["cpu_other_by_seconds"][30] = 3
            self.refuses("qualifier")
            self.x["private"]["qualifier"] = "no"
            VALIDATE(self.c, self.x)  # Shows the result privately even on a negative.


if __name__ == "__main__":
    if "--builder" in sys.argv:
        sys.argv.remove("--builder")
        try:
            from tests.contracts.cadence_looks.ctl_print_adapter import check_fixture as VALIDATE
        except ModuleNotFoundError as err:
            if err.name not in {"tests", "tests.contracts", "tests.contracts.cadence_looks",
                                "tests.contracts.cadence_looks.ctl_print_adapter"}:
                raise
            sys.exit("RED: future controls test adapter unavailable")
    unittest.main(verbosity=2)
