"""RC-CMP-7: FIX-BRIEF-3 Amendment 1 (G7) and the RC-CMP6-OPUS-REV findings 2 and 3.

G7: each family's key universe comes from registered member roles, applied identically to both
sides, never from either side's output. run_phase_energy_j's universe is the science runs L9's
step 2 re-reduces (the kept units of L9's kept-units record); a member the window's sealed plan
tree registers as a NEG-8 reference is compared in its NEG-8 family and listed as excluded with
compared_in:<family>. The regressions are RC-CMP-4's two causes (report/2026-10-28-rc-cmp-4) on
the producer-shaped fixture and Opus's probes G7.1 and G7.2 (review/2026-10-29-rc-cmp6-opus-rev
probe_cmp6.py). At 1134bbf58 the RC-CMP-4 window and G7.1 exit 1 and G7.2 exits 0 (counterfactuals
in .codex-report/RC-CMP-7.md); each test here also shows, where the check can be switched off in
place, the case passing or failing without it.
"""
import copy
from unittest import mock

from . import test_comparator
from .test_comparator import SHA, cmp
from .test_input_gate import CODED, GateCase
from .test_review_fixes import DISCLOSURE

ALPHA_KEPT = f"kept-units/{SHA}-alpha.json"
BASE = "bracket.claim_families.gross_energy."
NEG8_VALUES = {"bound_envelope_j": 2.0, "bound_prediction_j": 1.5, "start.mean_j": 10.0, "midpoint.mean_j": 10.5,
               "end.mean_j": 11.0, "trajectory_excursion_max_j": 1.0, "drift_allowance_j": 1.0}
# RC-CMP-4 cause 1: the NEG-8 reference members the recompute marked selected in each window (12 corpus,
# 3 window-end, 2 of 3 window-start, the midpoint), with their registered roles in the sealed plan trees.
RC_CMP4_REFERENCES = ([f"neg8-refcorpus-r{i:02d}" for i in range(1, 13)] + [f"neg8-window-end-r{i}" for i in (1, 2, 3)]
                      + ["neg8-window-start-r2", "neg8-window-start-r3", "neg8-window-midpoint"])
ROLES = {"neg8-refcorpus": "corpus", "neg8-window-end": "end", "neg8-window-start": "start", "neg8-window-midpoint": "midpoint"}


def role_of(rid):
    """The fixture's expected role (a test-side table; the comparator reads the plan trees)."""
    return next(role for prefix, role in ROLES.items() if rid.startswith(prefix))


def with_neg8(case, packs=("alpha", "beta", "gamma"), start=2, deciding=12):
    """Both sides' NEG-8 lines (disclosures._reference_lines) for each window.

    RC-CMP-8: the base fixture now carries them (the producer prints them for every registered window), so
    this replaces each window's NEG-8 lines with the given counts instead of appending a second set.
    """
    for pack in packs:
        lines = case.files[DISCLOSURE]["window_lines"][pack]
        lines[:] = [row for row in lines if row["line"] not in test_comparator.NEG8_WORDS]
        lines += test_comparator.neg8_lines(pack, start, deciding)
        case.ours["windows"][cmp.PACKS[pack]]["neg8"] = test_comparator.neg8_recompute()


def with_references(case, packs=("alpha", "beta", "gamma")):
    """RC-CMP-4 cause 1: every NEG-8 reference member in the recompute's member detail, selected."""
    for pack in packs:
        members = case.ours["members"].setdefault(cmp.PACKS[pack], {})
        for rid in RC_CMP4_REFERENCES:
            members[rid] = {"role": role_of(rid), "selected": True, "E_j": {"prefill": 1.0, "decode": 1.0, "request": 2.0}}
        members["neg8-window-start-r1"] = {"role": "start", "selected": False,
                                           "E_j": {"prefill": 1.0, "decode": 1.0, "request": 2.0}}


def old_key_set(c, custody, ours):
    """1134bbf58's compare_runs: L9's re-reduced runs against every selected member (the outputs' union)."""
    members = ours["members"]
    for (pack, rid), name, _ in c.pairs("run/", cmp.rereduced_names(custody), cmp.selected_runs(members)):
        l9 = custody.read(name) if name else {}
        mine = cmp.get(members, cmp.PACKS[pack], rid, "E_j", default={})
        for phase in ("prefill", "decode"):
            c.numeric("run_phase_energy_j", f"{pack}/{rid}/{phase}", cmp.get(l9, "phase_energy_j", phase), cmp.get(mine, phase))
        c.numeric("run_phase_energy_j", f"{pack}/{rid}/request", cmp.get(l9, "gross_energy_j"), cmp.get(mine, "request"))


class StepTwoUniverseTests(GateCase):
    """G7 on run_phase_energy_j."""
    def code(self):
        code, err, out = self.exit_code(CODED)
        return code, err, out

    def test_role_table_from_the_sealed_plan_trees(self):
        registry = cmp.load_registry()
        for pack in ("alpha", "beta", "gamma"):
            roles = registry.roles[pack]
            self.assertEqual(sum(r == "corpus" for r in roles.values()), 18)
            self.assertEqual({rid for rid, r in roles.items() if r == "start"},
                             {f"neg8-window-start-r{i}" for i in (1, 2, 3)} | {f"neg8-window-start-spare-{i}" for i in (1, 2, 3)})
            self.assertEqual(roles["neg8-window-midpoint"], "midpoint")
            self.assertEqual(roles["neg8-window-midpoint-spare-1"], "midpoint")
        self.assertEqual(sum(r == "science" for r in registry.roles["alpha"].values()), 100)
        self.assertEqual(sum(r == "science" for r in registry.roles["gamma"].values()), 80)
        self.assertEqual(registry.roles["gamma"]["gamma-interior-reference-decode-midpoint"], "diagnostic")
        self.assertEqual(registry.role("alpha", "d117fq31p7-df-ph-decode-abs-r01"), "science")
        self.assertIsNone(registry.role("alpha", "run-a"))

    def test_rc_cmp4_window_passes_and_lists_each_reference_member(self):
        # RC-CMP-4's two causes together: the registered cmp-abba floor spelling is in the base fixture's
        # floor_composition lines, and every window's reference members are selected by the recompute.
        self.assertIn("d117-df-cmp-abba-ph-decode-qwen3-1p7b",
                      {row.get("cell_id") for row in self.files[DISCLOSURE]["floors"]})
        with_neg8(self)
        with_references(self)
        code, err, out = self.code()
        self.assertEqual((code, err), (0, ""))
        excluded = {(row["pack"], row["run_id"]): row for row in out["excluded_members"]}
        self.assertEqual(len(excluded), 3 * 19)
        for (pack, rid), row in excluded.items():
            family = "corpus_counts" if role_of(rid) == "corpus" else "reference_counts"
            self.assertEqual((row["family"], row["role"], row["reason"]),
                             ("run_phase_energy_j", role_of(rid), "compared_in:" + family))
        self.assertFalse(excluded[("alpha", "neg8-window-start-r1")]["selected"])
        keys = {row["key"] for row in out["comparisons"] if row["family"] == "run_phase_energy_j"}
        self.assertEqual(keys, {"alpha/run-a/" + phase for phase in ("prefill", "decode", "request")})
        # Counterfactual: 1134bbf58's key set (the union of the outputs) fails the same sound window.
        with mock.patch.object(cmp, "compare_runs", old_key_set):
            code, _, out = self.code()
        self.assertEqual(code, 1)
        self.assertEqual(out["counts"]["run_phase_energy_j"]["fail"], 3 * 3 * 18)

    def test_opus_g7_1_refcorpus_member_selected_passes(self):
        self.ours["members"]["ALPHA"]["run-a"]["role"] = "science"
        self.ours["members"]["ALPHA"]["neg8-refcorpus-r01"] = {"role": "reference", "selected": True,
                                                               "E_j": {"prefill": 1.0, "decode": 1.0, "request": 1.0}}
        code, err, out = self.code()
        self.assertEqual((code, err), (0, ""))
        self.assertEqual(out["excluded_members"], [{"family": "run_phase_energy_j", "pack": "alpha",
                                                    "run_id": "neg8-refcorpus-r01", "role": "corpus", "selected": True,
                                                    "reason": "compared_in:corpus_counts"}])
        with mock.patch.object(cmp, "compare_runs", old_key_set):
            self.assertEqual(self.code()[0], 1)

    def test_opus_g7_2_science_run_both_sides_omit_disagrees(self):
        self.files.pop("rereduced/alpha/run-a.rereduced.json")
        self.ours["members"]["ALPHA"]["run-a"]["selected"] = False
        code, _, out = self.code()
        self.assertEqual(code, 1)
        self.assertEqual(self.fails(out), {"run_phase_energy_j": 3, "routing_id": 1})
        route = next(r for r in out["comparisons"] if r["key"] == "run/alpha/run-a")
        self.assertEqual((route["l9"], route["recompute"], route["reason"]), (None, None, "missing_or_null"))
        # Counterfactual: a universe taken from the outputs (no kept-units runs) compares the run nowhere.
        with mock.patch.object(cmp, "step_2_universe", lambda custody: ({}, {p: {"exclusions_sha256": "e" * 64, "pack": p}
                                                                              for p in cmp.PACKS})):
            code, _, out = self.code()
        self.assertEqual(code, 0)
        self.assertEqual(out["counts"]["run_phase_energy_j"], {"pass": 0, "fail": 0})

    def test_universe_run_either_side_lacks_disagrees(self):
        for side in ("l9", "recompute"):
            with self.subTest(side):
                self.setUp()
                if side == "l9":
                    self.files.pop("rereduced/alpha/run-a.rereduced.json")
                else:
                    self.ours["members"]["ALPHA"]["run-a"]["selected"] = False
                code, _, out = self.code()
                self.assertEqual(code, 1)
                # The run's routing_id row; its energies too where L9's are absent (the recompute's
                # unselected member detail still carries its values, which then agree).
                self.assertEqual(self.fails(out), {"run_phase_energy_j": 3, "routing_id": 1} if side == "l9"
                                 else {"routing_id": 1})
                route = next(r for r in out["comparisons"] if r["key"] == "run/alpha/run-a")
                self.assertEqual(route["verdict"], "DISAGREE")

    def test_run_both_sides_hold_outside_the_universe_disagrees(self):
        # L9 re-reduced it and the recompute selected it, but L9's step-2 selection does not keep it.
        self.files[ALPHA_KEPT] = test_comparator.kept_units_record("alpha", [])
        code, _, out = self.code()
        self.assertEqual(code, 1)
        route = next(r for r in out["comparisons"] if r["key"] == "run/alpha/run-a")
        self.assertEqual((route["l9"], route["verdict"]), (None, "DISAGREE"))

    def test_kept_reference_member_refuses(self):
        self.files[ALPHA_KEPT] = test_comparator.kept_units_record("alpha", ["run-a", "neg8-refcorpus-r01"])
        self.refused("kept_units_member_not_science:alpha")
        self.files[ALPHA_KEPT] = test_comparator.kept_units_record("alpha", ["run-a", "gamma-interior-reference-decode-midpoint"])
        self.files[f"kept-units/{SHA}-gamma.json"] = test_comparator.kept_units_record(
            "gamma", ["gamma-interior-reference-decode-midpoint"])
        self.files[ALPHA_KEPT] = test_comparator.kept_units_record("alpha", ["run-a"])
        self.refused("kept_units_member_not_science:gamma")

    def test_missing_record_or_other_exclusions_disagree(self):
        for label, edit in (("record absent", lambda: self.files.pop(ALPHA_KEPT)),
                            ("other exclusions", lambda: self.files[ALPHA_KEPT].update(exclusions_sha256="9" * 64))):
            with self.subTest(label):
                self.setUp()
                edit()
                code, _, out = self.code()
                self.assertEqual(code, 1)
                self.assertIn("routing_id", self.fails(out))
                row = next(r for r in out["comparisons"] if r["key"] == "run/alpha/kept_units/exclusions_sha256")
                self.assertEqual(row["verdict"], "DISAGREE")

    def test_reference_member_l9_rereduced_disagrees(self):
        # A reference member is in no run universe: a re-reduced file for one is DISAGREE.
        self.files["rereduced/alpha/neg8-refcorpus-r01.rereduced.json"] = {
            "phase_energy_j": {"prefill": 1.0, "decode": 1.0}, "gross_energy_j": 1.0}
        self.ours["members"]["ALPHA"]["neg8-refcorpus-r01"] = {"selected": True,
                                                               "E_j": {"prefill": 1.0, "decode": 1.0, "request": 1.0}}
        code, _, out = self.code()
        self.assertEqual(code, 1)
        self.assertEqual(self.fails(out), {"routing_id": 1})
        route = next(r for r in out["comparisons"] if r["key"] == "run/alpha/neg8-refcorpus-r01")
        self.assertEqual((route["l9"], route["recompute"]), (None, None))

    def test_selected_diagnostic_or_unregistered_member_disagrees(self):
        # Only registered NEG-8 reference roles leave the run universe; any other selected member is a key.
        for rid in ("gamma-interior-reference-decode-midpoint", "extra-run"):
            with self.subTest(rid):
                self.setUp()
                self.ours["members"]["ALPHA"][rid] = {"selected": True, "E_j": {"prefill": 1.0, "decode": 1.0, "request": 1.0}}
                code, _, out = self.code()
                self.assertEqual(code, 1)
                self.assertEqual(self.fails(out), {"routing_id": 1, "run_phase_energy_j": 3})

    def test_reference_member_dropped_from_a_neg8_line_still_disagrees(self):
        # Opus NEG8.1 and NEG8.2 with the reference members excluded from run_phase_energy_j.
        for label, start, deciding, path in (("start reference", 1, 12, "reference_counts/counts/start"),
                                             ("corpus member", 2, 11, "corpus_counts/deciding")):
            with self.subTest(label):
                self.setUp()
                with_references(self, ("alpha",))
                with_neg8(self, ("alpha",), start=start, deciding=deciding)
                code, err, out = self.code()
                self.assertEqual((code, err), (2, "refused=step11_unmapped_fill\n"))
                self.assertEqual(self.fails(out), {"count": 1})
                self.assertIn((f"disclosure:window_lines/alpha/{path}", "row_disagrees"), self.unbound(out))
                self.assertTrue(any(r["run_id"] == "neg8-window-start-r2" for r in out["excluded_members"]))

    def test_neg8_line_dropped_by_one_side_disagrees(self):
        with_references(self, ("alpha",))
        with_neg8(self, ("alpha",))
        self.files[DISCLOSURE]["window_lines"]["alpha"] = [
            row for row in self.files[DISCLOSURE]["window_lines"]["alpha"] if row["line"] != "corpus_counts"]
        code, _, out = self.code()
        self.assertEqual(code, 1)
        row = next(r for r in out["comparisons"] if r["key"] == "disclosure/window_lines/alpha/corpus_counts")
        self.assertEqual((row["l9"], row["verdict"]), (None, "DISAGREE"))
        # RC-CMP-9: the registry-driven table expects the line too (expected/disclosure/window_lines/alpha/corpus_counts).
        self.assertEqual(copy.deepcopy(self.fails(out)), {"routing_id": 2, "count": 1})


# F2: the compared categorical lines (each prints a claim word the recompute re-derives) and every section
# and line word the exemptions cover (the producer's harvest, history and window structure words).
# RC-CMP-8 (Fable F1): neg8_screen too, now that every window prints it.
COMPARED_LINES = ("dominance_branch", "dominance_ratio", "sensitivity_reported", "sensitivity_window", "below_screen_bound",
                  "neg8_screen")
EXEMPT_BLOCK_WORDS = ("superseded_history", "attempt_count", "attempt_history", "g10", "harvest_once", "reharvest_account",
                      "sensitivity_boundary")


def find(case, word, keep=lambda row: True):
    """(section list, index) of the first line with this word in the case's disclosure record (and, given keep,
    the first such line keep accepts)."""
    record = case.files[DISCLOSURE]
    for lines in [record[s] for s in ("cells", "floors", "contrasts", "block_lines", "fixed_sentences")] + list(
            record["window_lines"].values()):
        for index, row in enumerate(lines):
            if row["line"] == word and keep(row):
                return lines, index
    raise KeyError(word)


def p42_line(row):
    """RC-CMP-9: the producer-complete base prints computed sensitivity_reported lines before the refused p42 ones."""
    return row["line"] != "sensitivity_reported" or row["record"]["status"] == "refused"


class LineWordTests(GateCase):
    """F2: a line word read from the checked document no longer moves compared leaves under an exemption."""
    def outcome(self):
        try:
            return self.exit_code(CODED)[0]
        except cmp.Refusal:
            return 2

    def test_opus_relabel_sweep_never_exits_0(self):
        # probe_cmp6.py relabel(): every floors, contrasts and block_lines line relabelled to every other word of
        # the fixture. At 1134bbf58 58 of them exit 0 (probe_cmp6.out); here none does.
        record = self.files[DISCLOSURE]
        words = sorted({row["line"] for sec in ("cells", "floors", "contrasts", "block_lines", "fixed_sentences")
                        for row in record[sec]} | {row["line"] for rows in record["window_lines"].values() for row in rows})
        exits = []
        for section in ("floors", "contrasts", "block_lines"):
            for index, row in enumerate(copy.deepcopy(record[section])):
                for word in words:
                    if word == row["line"]:
                        continue
                    self.setUp()
                    item = self.files[DISCLOSURE][section][index]
                    item["line"] = item["label"] = word
                    if self.outcome() == 0:
                        exits.append((section, row["line"], word))
        self.assertEqual(exits, [])
        # Counterfactual: without the line gate the gate-free relabels of the block lines' claim words exit 0
        # again only where an exemption still names the leaf; the enumerated exemptions name none of them.
        with mock.patch.object(cmp, "gate_lines", lambda record: None):
            self.setUp()
            line = self.files[DISCLOSURE]["block_lines"][find(self, "dominance_branch")[1]]
            line.update(branch="A", line="harvest_once", label="harvest_once")
            self.assertNotEqual(self.outcome(), 0)

    def test_each_compared_line_relabelled_into_every_exempt_section_refuses(self):
        targets = [("block_lines", word) for word in EXEMPT_BLOCK_WORDS]
        targets += [("window_lines", word) for word in sorted(cmp.LINE_KEYS["window_lines"])]
        targets += [(section, word) for section in ("cells", "floors", "contrasts", "fixed_sentences")
                    for word in sorted(cmp.LINE_KEYS[section])]
        exits = []
        for source in COMPARED_LINES:
            for section, word in targets:
                if word == source:
                    continue
                self.setUp()
                lines, index = find(self, source)
                item = lines.pop(index)
                item["line"] = item["label"] = word
                record = self.files[DISCLOSURE]
                (record["window_lines"]["alpha"] if section == "window_lines" else record[section]).append(item)
                if self.outcome() == 0:
                    exits.append((source, section, word))
        self.assertEqual(exits, [])

    def test_wrong_categorical_word_in_its_own_line_disagrees(self):
        cases = {
            "branch A": ("dominance_branch", lambda row: row.update(branch="A")),
            "licensed True": ("dominance_branch", lambda row: row.update(dominance_sentence_licensed=True)),
            "ratio status refused": ("dominance_ratio", lambda row: row.update(status="refused")),
            "below True": ("below_screen_bound", lambda row: row.update(below=True)),
            "widened False": ("sensitivity_window", lambda row: row.update(widened=False)),
            # RC-CMP-8 F3: a computed record without its values now refuses at the gate (required keys).
            "p42 status computed": ("sensitivity_reported", lambda row: row["record"].update(status="computed")),
            "p42 code other": ("sensitivity_reported", lambda row: row["record"].update(code="p42_other")),
        }
        for label, (word, edit) in cases.items():
            with self.subTest(label):
                self.setUp()
                lines, index = find(self, word, p42_line)
                edit(lines[index])
                code, err, out = self.exit_code(CODED)
                if label == "p42 status computed":
                    self.assertEqual((code, err), (2, "refused=required_key_absent:disclosure:block_lines/"
                                                      "sensitivity_reported/record/primary\n"))
                    continue
                self.assertEqual((code, err), (2, "refused=step11_unmapped_fill\n"))
                self.assertTrue(any(u["reason"] in ("value_differs", "row_disagrees") for u in out["coverage"]["unbound"]))

    def test_licensed_and_p42_words_were_exempt_at_1134bbf58(self):
        # Counterfactual in place: the 1134bbf58 rules for these two leaves (uncovered:) let the wrong word pass.
        old = ((r"disclosure:block_lines/dominance_branch/dominance_sentence_licensed", cmp.UNCOVERED + "x"),
               (r"disclosure:(block_lines/[a-z_]+/record|sensitivity/[a-z_]+/\*)/(status|code)", cmp.UNCOVERED + "x"))
        for word, edit in (("dominance_branch", lambda row: row.update(dominance_sentence_licensed=True)),
                           ("sensitivity_reported", lambda row: row["record"].update(status="computed"))):
            with self.subTest(word):
                self.setUp()
                lines, index = find(self, word, p42_line)
                edit(lines[index])
                self.assertEqual(self.outcome(), 2)
                # RC-CMP-8 F3's required-key gate is switched off too: it refuses a computed record without values.
                with mock.patch.object(cmp, "COVERAGE", old + cmp.COVERAGE), \
                        mock.patch.object(cmp, "sensitivity_row", lambda row, name, where: None):
                    self.assertEqual(self.exit_code(CODED)[0], 0)

    def test_line_gate_refuses_an_unregistered_word_or_key(self):
        self.files[DISCLOSURE]["block_lines"].append(test_comparator.item("made_up", False, "x"))
        self.refused("line_word_unregistered:disclosure:block_lines")
        self.setUp()
        self.files[DISCLOSURE]["window_lines"]["alpha"].append(test_comparator.item("harvest_once", False, "x"))
        self.refused("line_word_unregistered:disclosure:window_lines")
        self.setUp()
        lines, index = find(self, "harvest_once")
        lines[index]["branch"] = "B"
        self.refused("line_key_unregistered:disclosure:block_lines/harvest_once/branch")
        self.setUp()
        lines, index = find(self, "sensitivity_boundary")
        lines[index]["line"] = "dominance_branch"
        self.refused("line_keys_absent:disclosure:block_lines/dominance_branch")
        self.setUp()
        self.files[DISCLOSURE]["window_lines"]["delta"] = []
        self.refused("routing_id_unregistered:disclosure:window_lines/delta")

    def test_no_exemption_takes_a_window_or_history_subtree(self):
        for rule in cmp.COVERAGE:
            if len(rule) == 2:
                self.assertNotIn("window_lines/.*", rule[0])
                self.assertNotRegex(rule[0], r"(attempt_history|harvest_once|reharvest_account|g10)\)?/\.\*")


class RegisteredLabelTests(GateCase):
    """F3 (Opus finding 3, Fable F2): leave-one-out keys and ratio labels from registered ids and fields."""
    DECODE = test_comparator.DECODE

    def with_loo(self, block_id):
        """Block 3's leave-one-out row on both sides: L9's verdict and fill copy (by block id), the recompute's (b03).

        RC-CMP-9: the producer-complete base prints a row for every kept block (status complete); this case
        rewrites block 3's row in place, with its omitted block id printed as block_id."""
        verdict = next(r for r in self.files[f"outputs/{SHA}-claim-verdicts.json"]["contrasts"] if r["contrast_id"] == self.DECODE)
        fill = next(r for r in self.files[f"outputs/{SHA}-results-fill-input.json"]["gamma"]["contrasts"]
                    if r["contrast_id"] == self.DECODE)
        for contrast in (verdict, fill):
            row = next(r for r in contrast["loo"]["rows"] if r["omitted_block_id"] == "d117-decode-contrast-b03")
            row.update({"omitted_block_id": block_id, "estimate": -1.0, "raw_p": 0.9, "adjusted_p": 1.0,
                        "outcome": "not_resolvable", "floor_status": "not_above_floor",
                        "metrology_aware_ci95": {"lower": -13.0, "upper": 11.0},
                        "decision_interval": {"lower": -16.0, "upper": 14.0}, "n_blocks": 8, "df": 7,
                        "influence_triggers": []})
        own = next(r for r in self.ours["contrasts"][self.DECODE]["loo"] if r["block_number"] == 3)
        own.update({"block_number": 3, "dbar_j": -1.0, "p": 0.9, "holm_p": 1.0, "holm_reject": False,
                    "outcome": "not_resolvable", "metrology_interval_j": [-13.0, 11.0],
                    "decision_interval_j": [-16.0, 14.0], "n": 8, "above_floor": False})

    def test_registered_block_id_binds(self):
        self.with_loo("d117-decode-contrast-b03")
        code, err, out = self.exit_code(CODED)
        self.assertEqual((code, err), (0, ""))
        self.assertTrue(any(r["key"] == f"{self.DECODE}/loo/b03/dbar_j" and r["verdict"] == "AGREE" for r in out["comparisons"]))

    def test_unregistered_or_other_contrast_block_id_does_not_route_fable_p3b_p3c(self):
        for block_id in ("TYPO-b03", "b03", "d117-prefill-p2048-contrast-b03", "plan-gamma-b03"):
            with self.subTest(block_id):
                self.setUp()
                self.with_loo(block_id)
                self.assertNotEqual(self.exit_code(CODED)[0], 0)
                # Counterfactual: 1134bbf58's parse (a trailing bNN) routes every one of them to b03 (and 1134bbf58
                # had no expected-check table, which now expects block 3's registered id).
                def parse(registry, cid, bid):
                    return "b%02d" % int(bid.rsplit("b", 1)[1]) if isinstance(bid, str) else None
                with mock.patch.object(cmp, "loo_key", parse), \
                        mock.patch.object(cmp, "compare_expected", test_comparator.no_table):
                    self.assertEqual(self.exit_code(CODED)[0], 0)

    def test_ratio_label_takes_the_registered_numerator_field(self):
        ratio = self.files["finalized/outputs/closeout.ratio-table.json"]["ratios"][0]
        for field in ("common_mode_x", "corner_widened_unguarded_floor_j_v2"):
            with self.subTest(field):
                ratio["numerator_field"] = field
                code, _, out = self.exit_code(CODED)
                self.assertEqual(code, 2)
                # The row keys on no recompute ratio: its routing_id row (and the recompute's own ratio) DISAGREE.
                self.assertGreaterEqual(out["counts"]["routing_id"]["fail"], 2)
        ratio["numerator_field"] = "corner_widened_unguarded_floor_j"
        self.assertEqual(self.exit_code(CODED)[0], 0)
