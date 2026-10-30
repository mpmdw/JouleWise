"""RC-CMP-8: RC-CMP7-OPUS-REV findings 1-5 and RC-CMP7-FABLE-REV findings 1-2.

The round's rule: every printed word that asserts a claim, direction, status or relation and that the
recompute or the sealed registry can determine is compared exactly; an exemption states why its word is
not checkable. The regressions are Opus's probes C1, C3, C3b, C4, C6 and K5-K9 (review/2026-10-29-rc-cmp7-
opus-rev probe_cmp7.py) and Fable's F2.c-F2.e and F2.g (review/2026-10-29-rc-cmp7-fable-rev probes.py). At
c372211bf each of them exits 0 (claims.out, keys.out, probes.out there); each test here also shows, where the
check can be switched off in place, the case passing without it. F4 adds the producer-shaped sensitivity
fixture (computed reported, floor and contrast rows) on a widened and an unwidened window.
"""
import copy
from unittest import mock

from . import test_comparator
from .test_comparator import DECODE, SHA, cmp, item
from .test_input_gate import CODED, GateCase
from .test_rc_cmp7 import find, with_neg8, with_references
from .test_review_fixes import DISCLOSURE, FILL, VERDICTS

F = r"fill:gamma/contrasts/\*/"
# c372211bf's rules for the leaves this round compares (scripts/compare_b5_recompute.py:1727-1732, :1862-1865,
# :1892 there), prepended to the shipped rules for the in-place counterfactuals.
OLD_RULES = (
    (F + r"(claim_evaluation/claim_ready_for_l2_l3|loo/status|loo/rows/\*/influence_triggers/\*)", cmp.UNCOVERED + "old"),
    # c372211bf read an empty trigger list as an empty container (no printed value).
    (F + r"loo/rows/\*/influence_triggers", cmp.UNCOVERED + "empty container; no printed value"),
    (F + r"(claim_role|hypothesized_direction|sampling/confirmatory_status)", cmp.UNCOVERED + "old"),
    (r"fill:campaigns/(alpha|beta)/claim_usable", cmp.IDENTITY),
    (r"disclosure:(sensitivity/(reported_cells|contrasts)/\*|block_lines/sensitivity_(reported|contrast)/record)/"
     r"(mean_and_half_width_equal_primary|bound_independent_values_equal_primary)", cmp.UNCOVERED + "old"),
    (r"disclosure:(cells/reported_cell/status|cells/battery_assist_cell/primary/status|"
     r"contrasts/battery_assist_contrast/status)", cmp.UNCOVERED + "old"),
    (F + r"(conditions/(condition_a_id|condition_b_id|difference_orientation)|metric/(name|metric_tag|window_class)|"
     r"floor/(claim_floor_rule|aggregation)|floor/resolutions/\*/transport_rule_id)", cmp.UNCOVERED + "old"),
    (r"disclosure:(contrasts/primary_contrast/estimator/name|floors/floor_composition/source|"
     r"window_lines/[a-z]+/neg8_allowance/source)", cmp.UNCOVERED + "old"))
SENSITIVITY = "outputs/" + "1" * 64 + ".json"
PROJECTION = f"outputs/{SHA}-projection-alpha.json"
REPORTED = "d117-reported-mean-ph-decode-qwen3-1p7b"
FAMILY = "df-ph-decode-qwen3-1p7b"
FLOOR_CELLS = {"alpha": "d117-qwen3-1p7b-decode-floor-v5", "beta": "d117-qwen3-8b-decode-floor-v5"}
MODEL_CELLS = {"alpha": "Qwen3-1.7B-4bit/decode", "beta": "Qwen3-8B-4bit/decode"}


def contrast_rows(case, cid=DECODE):
    """The claim-verdict row and its fill copy for one contrast."""
    return [next(r for r in rows if r["contrast_id"] == cid)
            for rows in (case.files[VERDICTS]["contrasts"], case.files[FILL]["gamma"]["contrasts"])]


def loo_b03(contrast):
    """Block 3's leave-one-out row of a verdict or fill contrast (RC-CMP-9: the base prints one per kept block)."""
    return next(r for r in contrast["loo"]["rows"] if r["omitted_block_id"] == "d117-decode-contrast-b03")


class Round(GateCase):
    def outcome(self):
        try:
            return self.exit_code(CODED)[0]
        except cmp.Refusal:
            return 2

    def row(self, out, key, family="outcome_word"):
        return next(r for r in out["comparisons"] if r["key"] == key and r["family"] == family)


class ClaimWordTests(Round):
    """Opus F1 (MEDIUM): claim_ready_for_l2_l3 and claim_usable compared."""
    def test_baseline_rows_agree(self):
        code, err, out = self.exit_code(CODED)
        self.assertEqual((code, err), (0, ""))
        for cid in (DECODE, test_comparator.PREFILL):
            self.assertEqual(self.row(out, f"{cid}/claim_ready")["recompute"], False)
        for pack in ("alpha", "beta"):
            row = self.row(out, f"campaigns/{pack}/claim_usable")
            self.assertEqual((row["l9"], row["recompute"], row["verdict"]), (True, True, "AGREE"))
        self.assertEqual(out["coverage"]["leaves"][F.replace("\\", "") + "claim_evaluation/claim_ready_for_l2_l3"],
                         "outcome_word")
        self.assertEqual(out["coverage"]["leaves"]["fill:campaigns/alpha/claim_usable"], "outcome_word")

    def test_opus_c1_ready_true_with_ceiling_l1_fails(self):
        contrast_rows(self)[1]["claim_evaluation"]["claim_ready_for_l2_l3"] = True
        self.assertEqual(self.outcome(), 2)
        with mock.patch.object(cmp, "COVERAGE", OLD_RULES + cmp.COVERAGE):
            self.assertEqual(self.outcome(), 0)
        # A wrong producer (verdict and fill both say ready on an L1 ceiling) DISAGREEs the row.
        self.setUp()
        for row in contrast_rows(self):
            row["claim_evaluation"]["claim_ready_for_l2_l3"] = True
        code, _, out = self.exit_code(CODED)
        self.assertNotEqual(code, 0)
        self.assertEqual(self.row(out, f"{DECODE}/claim_ready")["verdict"], "DISAGREE")

    def test_ready_follows_the_recompute_ceiling(self):
        # The recompute says L2: L9's False (and L1) both disagree; the ready word alone is enough.
        self.ours["contrasts"][DECODE]["ceiling"] = "L2"
        code, _, out = self.exit_code(CODED)
        self.assertNotEqual(code, 0)
        self.assertEqual((self.row(out, f"{DECODE}/claim_ready")["recompute"],
                          self.row(out, f"{DECODE}/claim_ready")["verdict"]), (True, "DISAGREE"))
        self.ours["contrasts"][DECODE].pop("ceiling")
        self.assertEqual(self.row(self.shipped(), f"{DECODE}/claim_ready")["reason"], "missing_or_null")

    def test_opus_c3_and_c3b_claim_usable_fails(self):
        self.files[FILL]["campaigns"]["alpha"]["claim_usable"] = False
        code, _, out = self.exit_code(CODED)
        self.assertEqual(code, 2)
        self.assertEqual(self.row(out, "campaigns/alpha/claim_usable")["verdict"], "DISAGREE")
        with mock.patch.object(cmp, "COVERAGE", OLD_RULES + cmp.COVERAGE), \
                mock.patch.object(cmp, "compare_campaigns", lambda c, custody, ours: None):
            self.assertEqual(self.outcome(), 0)
        self.setUp()
        self.ours["inputs"]["ALPHA"]["claim_usable"] = False
        self.ours.setdefault("flags", []).append({"code": "claim_usable_false", "pack": "ALPHA", "scope": "window"})
        self.assertNotEqual(self.outcome(), 0)
        with mock.patch.object(cmp, "COVERAGE", OLD_RULES + cmp.COVERAGE), \
                mock.patch.object(cmp, "compare_campaigns", lambda c, custody, ours: None):
            self.assertEqual(self.outcome(), 0)
        # The recompute holding no claim_usable word is DISAGREE too, never a pass.
        self.setUp()
        self.ours["inputs"]["BETA"].pop("claim_usable")
        self.assertEqual(self.row(self.shipped(), "campaigns/beta/claim_usable")["reason"], "missing_or_null")


class DefinitionAndStatusWordTests(Round):
    """Opus F2: the registered definition words, the status words the producer fixes, the influence triggers."""
    def test_registry_reads_the_manifest_words(self):
        entry = cmp.load_registry().entry(DECODE, "contrast")
        self.assertEqual((entry["role"], entry["direction"], entry["confirmatory"]), ("primary", "positive", "confirmatory"))

    def test_opus_c4_and_each_definition_word_fails(self):
        cases = {"hypothesized_direction": lambda row: row.update(hypothesized_direction="negative"),
                 "claim_role": lambda row: row.update(claim_role="secondary"),
                 "confirmatory_status": lambda row: row["sampling"].update(confirmatory_status="demoted_exploratory")}
        for word, edit in cases.items():
            with self.subTest(word):
                self.setUp()
                edit(contrast_rows(self)[1])
                self.assertEqual(self.outcome(), 2)
                with mock.patch.object(cmp, "COVERAGE", OLD_RULES + cmp.COVERAGE):
                    self.assertEqual(self.outcome(), 0)
                self.setUp()
                for row in contrast_rows(self):
                    edit(row)
                code, _, out = self.exit_code(CODED)
                self.assertNotEqual(code, 0)
                self.assertEqual(self.row(out, f"{DECODE}/{word}")["verdict"], "DISAGREE")

    def test_opus_c6_loo_status_fails(self):
        contrast_rows(self)[1]["loo"]["status"] = "computed"
        self.assertEqual(self.outcome(), 2)
        with mock.patch.object(cmp, "COVERAGE", OLD_RULES + cmp.COVERAGE):
            self.assertEqual(self.outcome(), 0)
        # RC-CMP-9: the producer-complete base keeps nine blocks, so the engine's word is complete.
        for word in ("not_run", "not_required"):
            with self.subTest(word):
                self.setUp()
                for row in contrast_rows(self):
                    row["loo"]["status"] = word
                code, _, out = self.exit_code(CODED)
                self.assertNotEqual(code, 0)
                self.assertEqual(self.row(out, f"{DECODE}/loo_status")["recompute"], "complete")

    def test_loo_status_word_rule(self):
        # RC-CMP-9 A2: the word follows the kept n (one row per kept block), never the rows either side printed.
        self.assertEqual(cmp.loo_status(0, tuple(range(10))), "not_run")
        self.assertEqual(cmp.loo_status(1, tuple(range(10))), "complete")
        self.assertEqual(cmp.loo_status(9, tuple(range(10))), "complete")
        # More registered blocks than the engine's limit leave the word undetermined (refuse, never pass).
        self.assertIsNone(cmp.loo_status(9, tuple(range(11))))
        self.assertIsNone(cmp.loo_status(None, tuple(range(10))))
        self.assertIsNone(cmp.loo_status(True, tuple(range(10))))

    def with_loo(self, triggers, estimate=-1.0):
        """Block 3's leave-one-out row on both sides (as test_rc_cmp7.RegisteredLabelTests.with_loo). RC-CMP-9: the
        producer-complete base prints a row for every kept block; block 3's is rewritten in place."""
        row = {"omitted_block_id": "d117-decode-contrast-b03", "estimate": estimate, "raw_p": 0.9, "adjusted_p": 1.0,
               "outcome": "not_resolvable", "floor_status": "not_above_floor",
               "metrology_aware_ci95": {"lower": -13.0, "upper": 11.0}, "decision_interval": {"lower": -16.0, "upper": 14.0},
               "n_blocks": 8, "df": 7, "influence_triggers": triggers}
        for contrast in contrast_rows(self):
            rows = contrast["loo"]["rows"]
            rows[next(i for i, r in enumerate(rows) if r["omitted_block_id"] == row["omitted_block_id"])] = copy.deepcopy(row)
        own = self.ours["contrasts"][DECODE]["loo"]
        own[next(i for i, r in enumerate(own) if r["block_number"] == 3)] = {
            "block_number": 3, "dbar_j": estimate, "p": 0.9, "holm_p": 1.0, "holm_reject": False,
            "outcome": "not_resolvable", "metrology_interval_j": [-13.0, 11.0], "decision_interval_j": [-16.0, 14.0],
            "n": 8, "above_floor": False}

    def test_influence_triggers_compared(self):
        self.with_loo([])
        code, err, out = self.exit_code(CODED)
        self.assertEqual((code, err), (0, ""))
        self.assertEqual(self.row(out, f"{DECODE}/loo/b03/influence_triggers")["recompute"], [])
        # A sign flip (the recompute's -1.25 full estimate against +1.0) is the estimate_sign trigger.
        self.setUp()
        self.with_loo(["estimate_sign"], estimate=1.0)
        self.assertEqual(self.exit_code(CODED)[:2], (0, ""))
        for triggers in ([], ["estimate_sign", "outcome"], ["outcome"]):
            with self.subTest(triggers):
                self.setUp()
                self.with_loo(["estimate_sign"], estimate=1.0)
                for contrast in contrast_rows(self):
                    loo_b03(contrast)["influence_triggers"] = list(triggers)
                self.assertNotEqual(self.outcome(), 0)
        # Counterfactual: c372211bf's vocabulary exemption and no row.
        self.setUp()
        self.with_loo(["estimate_sign"], estimate=1.0)
        loo_b03(contrast_rows(self)[1])["influence_triggers"] = []
        self.assertEqual(self.outcome(), 2)
        with mock.patch.object(cmp, "COVERAGE", OLD_RULES + cmp.COVERAGE):
            self.assertEqual(self.outcome(), 0)

    def test_loo_triggers_follow_the_engine_order(self):
        full = {"dbar_j": 200.0, "floor_gate_j": 100.0, "holm_reject": True, "outcome": "direction_supported"}
        row = {"dbar_j": -10.0, "holm_reject": False, "outcome": "not_resolvable", "above_floor": False}
        self.assertEqual(cmp.loo_triggers(full, row),
                         ["estimate_sign", "floor_status", "adjusted_rejection", "outcome", "estimate_magnitude"])
        self.assertIsNone(cmp.loo_triggers(full, dict(row, holm_reject=None)))

    def with_assist_contrast(self, status="computed", n=9):
        # RC-CMP-9: the producer-complete base prints DECODE's line; it is replaced in place.
        lines, index = find(self, "battery_assist_contrast")
        lines[index] = item("battery_assist_contrast", True, DECODE + ": without assisted quads", contrast_id=DECODE,
                            status=status, n=n, mean_j=-1.25, s_d=16.0, se=5.25, t_star=2.306, lower_j=-13.5,
                            upper_j=11.0, assist_quads=0, assist_members={})
        self.ours["disclosures"]["battery_assist"][DECODE] = {
            "n": 9, "dbar_j": -1.25, "s_d_j": 16.0, "se_j": 5.25, "t_star": 2.306, "metrology_interval_j": [-13.5, 11.0],
            "status": "computed", "assist_quads": 0, "assist_members_by_stratum": {}}

    def test_battery_assist_contrast_status_fails(self):
        self.with_assist_contrast()
        self.assertEqual(self.exit_code(CODED)[:2], (0, ""))
        for word in ("one_quad", "not_computable", "refused"):
            with self.subTest(word):
                self.setUp()
                self.with_assist_contrast(word)
                self.assertNotEqual(self.outcome(), 0)
                # c372211bf: the old rules and no status row (RC-CMP-8 report: "old rules + no row").
                with mock.patch.object(cmp, "COVERAGE", OLD_RULES + cmp.COVERAGE), \
                        mock.patch.object(cmp.Comparison, "exact", rows_off(cmp.Comparison.exact,
                                                                            "/battery_assist_contrast/status")):
                    self.assertEqual(self.outcome(), 0)
        self.assertEqual([cmp.paired_status(n) for n in (0, 1, 2, 9, None, 2.0)],
                         ["not_computable", "one_quad", "computed", "computed", None, None])

    def test_restricted_is_a_listed_disclosure_control(self):
        leaves = self.shipped()["coverage"]["leaves"]
        self.assertEqual(leaves["disclosure:block_lines/dominance_branch/restricted"], cmp.DISCLOSURE_CONTROL)
        self.assertFalse(any(reason == cmp.TEXT for path, reason in leaves.items() if path.endswith("/restricted")))


class RegisteredDefinitionTests(Round):
    """The round's rule beyond Opus's list: the manifest's direction and relation words and the allowance source."""
    def test_each_registered_word_flipped_fails(self):
        cases = {
            "difference_orientation": (lambda row: row["conditions"].update(difference_orientation="condition_a_minus_condition_b"),
                                       f"{DECODE}/definition/difference_orientation"),
            "condition ids swapped": (lambda row: row["conditions"].update(condition_a_id="sw-decode-b-qwen3-8b",
                                                                           condition_b_id="sw-decode-a-qwen3-1p7b"),
                                      f"{DECODE}/definition/condition_a_id"),
            "metric name": (lambda row: row["metric"].update(name="phase_energy_j.prefill"), f"{DECODE}/definition/name"),
            "metric tag": (lambda row: row["metric"].update(metric_tag="phase_prefill_p2048_energy"),
                           f"{DECODE}/definition/metric_tag"),
            "window class": (lambda row: row["metric"].update(window_class="request"), f"{DECODE}/definition/window_class"),
            "claim floor rule": (lambda row: row["floor"].update(claim_floor_rule="cross_stack_armwise_sum.v1"),
                                 f"{DECODE}/floor/claim_floor_rule"),
            "aggregation": (lambda row: row["floor"].update(aggregation="sum"), f"{DECODE}/floor/aggregation"),
            "transport rule": (lambda row: row["floor"]["resolutions"][1].update(transport_rule_id="nearest_stack.v1"),
                               f"contrast/{DECODE}/resolution/1/transport_rule_id")}
        for label, (edit, key) in cases.items():
            with self.subTest(label):
                self.setUp()
                edit(contrast_rows(self)[1])
                self.assertEqual(self.outcome(), 2)
                with mock.patch.object(cmp, "COVERAGE", OLD_RULES + cmp.COVERAGE):
                    self.assertEqual(self.outcome(), 0)
                self.setUp()
                for row in contrast_rows(self):
                    edit(row)
                code, _, out = self.exit_code(CODED)
                self.assertNotEqual(code, 0)
                self.assertEqual(self.row(out, key, "routing_id")["verdict"], "DISAGREE")

    def test_estimator_name_and_sources_fail(self):
        def estimator(case):
            for line in case.files[DISCLOSURE]["contrasts"]:
                if line["line"] == "primary_contrast" and line["contrast_id"] == DECODE:
                    line["estimator"]["name"] = "paired_block_mean"
        def composition(case):
            next(r for r in case.files[DISCLOSURE]["floors"] if r["line"] == "floor_composition")["source"] = "stored_bound"
        def allowance(case):
            lines, index = find(case, "neg8_allowance")
            lines[index]["source"] = "stored_bound"
        for label, edit in (("estimator name", estimator), ("floor_composition source", composition),
                            ("neg8_allowance source", allowance)):
            with self.subTest(label):
                self.setUp()
                edit(self)
                self.assertEqual(self.outcome(), 2)
                # c372211bf had neither these rules nor the source rows (read from the disclosure line itself).
                with mock.patch.object(cmp, "COVERAGE", OLD_RULES + cmp.COVERAGE), \
                        mock.patch.object(cmp.Comparison, "exact", rows_off(cmp.Comparison.exact, "/source")):
                    self.assertEqual(self.outcome(), 0)
        # A recompute on the other source DISAGREEs every source row of that window.
        self.setUp()
        self.ours["windows"]["BETA"]["neg8"]["source"] = "stored_bound"
        code, _, out = self.exit_code(CODED)
        self.assertNotEqual(code, 0)
        failing = {r["key"] for r in out["comparisons"] if r["verdict"] != "AGREE"}
        self.assertEqual(failing, {"disclosure/beta/neg8_allowance/source",
                                   "disclosure/Qwen3-8B-4bit/decode/absolute/floor_composition/source",
                                   "disclosure/Qwen3-8B-4bit/decode/comparative/floor_composition/source",
                                   "disclosure/Qwen3-8B-4bit/prefill/absolute/floor_composition/source",
                                   "disclosure/Qwen3-8B-4bit/prefill/comparative/floor_composition/source"})


class RequiredKeyTests(Round):
    """Opus F3 and Fable F1: a compared line, or a claim key, its producer always prints cannot be left out."""
    def strip(self, word, key):
        lines, index = find(self, word)
        lines[index].pop(key)

    def test_opus_k5_to_k8_refuse(self):
        cases = {"K5": ("dominance_branch", "branch"), "K6": ("dominance_branch", "dominance_sentence_licensed"),
                 "K7": ("below_screen_bound", "below"), "K8": ("sensitivity_window", "widened")}
        for label, (word, key) in cases.items():
            with self.subTest(label):
                self.setUp()
                self.strip(word, key)
                section = "window_lines" if word == "below_screen_bound" else "block_lines"
                self.refused(f"required_key_absent:disclosure:{section}/{word}/{key}")
                if label != "K7":
                    # Counterfactual: without the required-key gate (and RC-CMP-9's expected-check table, which
                    # c372211bf did not have either) the word survives only in text (exit 0).
                    with mock.patch.object(cmp, "require", lambda value, keys, where: None), \
                            mock.patch.object(cmp, "compare_expected", test_comparator.no_table):
                        self.assertEqual(self.outcome(), 0)

    def test_opus_k9_and_fable_f2d_f2e_a_dropped_window_claim_line_disagrees(self):
        for word in ("neg8_screen", "below_screen_bound"):
            with self.subTest(word):
                self.setUp()
                lines = self.files[DISCLOSURE]["window_lines"]["alpha"]
                lines[:] = [row for row in lines if row["line"] != word]
                code, _, out = self.exit_code(CODED)
                self.assertEqual(code, 1)
                route = self.row(out, f"disclosure/window_lines/{word}/alpha", "routing_id")
                self.assertEqual((route["l9"], route["verdict"]), (None, "DISAGREE"))

    def test_fable_f2c_neg8_word_relabelled_adapter_continuity_disagrees(self):
        lines, index = find(self, "neg8_screen")
        lines[index].update(decision="failed", line="adapter_continuity", label="adapter_continuity")
        code, _, out = self.exit_code(CODED)
        self.assertEqual(code, 1)
        # RC-CMP-9: the table also expects alpha's neg8_screen line and one adapter_continuity line (now two), and
        # both relabelled-into items are outside it (four more routing rows).
        self.assertEqual(self.fails(out), {"outcome_word": 1, "routing_id": 5})

    def test_fill_claim_keys_are_required(self):
        cases = {"claim_evaluation/claim_ready_for_l2_l3": lambda row: row["claim_evaluation"].pop("claim_ready_for_l2_l3"),
                 "claim_evaluation/direction": lambda row: row["claim_evaluation"].pop("direction"),
                 "hypothesized_direction": lambda row: row.pop("hypothesized_direction"),
                 "sampling/confirmatory_status": lambda row: row["sampling"].pop("confirmatory_status"),
                 "loo/status": lambda row: row["loo"].pop("status")}
        for path, edit in cases.items():
            with self.subTest(path):
                self.setUp()
                edit(contrast_rows(self)[1])
                where = path.rsplit("/", 1)
                self.refused("required_key_absent:fill:gamma/contrasts/*" + ("/" + where[0] if len(where) == 2 else "")
                             + "/" + where[-1])
                with mock.patch.object(cmp, "require", lambda value, keys, where: None), \
                        mock.patch.object(cmp, "compare_expected", test_comparator.no_table):
                    self.assertEqual(self.outcome(), 0)
        self.setUp()
        self.files[FILL]["campaigns"]["beta"].pop("claim_usable")
        self.refused("required_key_absent:fill:campaigns/beta/claim_usable")

    def test_sensitivity_record_keys_are_required(self):
        self.files[DISCLOSURE]["sensitivity"]["windows"]["gamma"].pop("widened")
        self.refused("required_key_absent:disclosure:sensitivity/windows/gamma/widened")
        self.setUp()
        next(r for r in self.files[DISCLOSURE]["sensitivity"]["reported_cells"] if r["status"] == "refused").pop("code")
        self.refused("required_key_absent:disclosure:sensitivity/reported_cells/code")

    def test_producer_lines_with_conditional_keys_absent_pass_the_gate(self):
        # disclosures.py: a refused ratio, a one-quad and an empty assist contrast, a ratio that is not
        # computable, a machine summary with no finite rho; and a refused reported sensitivity record.
        record = {
            "contrasts": [
                item("battery_assist_contrast", True, "x", contrast_id=DECODE, status="one_quad", n=1, mean_j=-1.0,
                     assist_quads=8, assist_members={"quad": 8}),
                item("battery_assist_contrast", True, "x", contrast_id=DECODE, status="not_computable", n=0,
                     assist_quads=9, assist_members={"quad": 9}),
                item("magnitude_ratio", True, "x: ratio not computable", contrast_id=DECODE)],
            "block_lines": [
                item("dominance_ratio", True, "x absolute: R refused", cell_id=FLOOR_CELLS["alpha"], component="absolute",
                     n=9, status="refused"),
                item("sensitivity_reported", True, "x", record={"pack": "alpha", "cell_id": REPORTED,
                                                               "status": "refused", "code": "p42_expected_unresolvable"})],
            "window_lines": {"alpha": [item("machine_summary", True, "x: no clean window", model="qwen3-1p7b")]}}
        cmp.gate_lines(record)
        # Control: each line refuses once an unconditional key goes.
        for section, index, key in (("contrasts", 0, "status"), ("contrasts", 2, "contrast_id"),
                                    ("block_lines", 0, "n"), ("block_lines", 1, "record")):
            with self.subTest(key=key, section=section):
                broken = copy.deepcopy(record)
                broken[section][index].pop(key)
                with self.assertRaises(cmp.Refusal):
                    cmp.gate_lines(broken)


def reported_values(widened):
    primary = {"mean_j": 50.0, "h_j": 2.0, "B_j": 1.0, "lower_j": 47.0, "upper_j": 53.0, "attribution_floor_j": 3.0}
    return primary, (dict(primary, B_j=1.5, lower_j=46.5, upper_j=53.5, attribution_floor_j=3.5) if widened
                     else dict(primary))


def with_sensitivity(case, widened=True):
    """F4: a producer-shaped computed sensitivity (sensitivity.build_sensitivity_record): ALPHA's decode reported
    cell (its projection cell and the disclosure's reported_cell, battery_assist_cell and attribution_floor lines),
    both decode aggregate floor cells and the decode contrast, in the record, the disclosure's copy and the
    block-line copies; the recompute's primary and sensitivity values beside them. Unwidened, B_max sits below
    every window's b_op, so b_sens equals b_op and the sensitivity values equal the primary ones.

    RC-CMP-9: the base fixture is producer-complete (every registered reported cell, floor cell and contrast has its
    sensitivity row, line and recompute value), so this sets the widened values of those three items in place and,
    unwidened, every sensitivity value to its primary value."""
    files, ours = case.files, case.ours
    primary, after = reported_values(widened)
    floor_before = {"floor_abs_j": 43.0, "floor_cmp_j": 103.5, "floor_gate_j": 103.5}
    floor_after = dict(floor_before, floor_abs_j=45.0, floor_cmp_j=105.0, floor_gate_j=105.0) if widened else dict(floor_before)
    contrast_after = dict(floor_after, D_j=3.0 if widened else 2.75, outcome="not_resolvable")
    bound = 0.0625 if widened else 0.0375
    record = files[SENSITIVITY]
    record["b_max"]["value_s"] = 0.0625 if widened else 0.03
    for window in record["windows"].values():
        window.update(b_sens_s=bound, widened=widened)
    for row in record["reported_cells"]:
        if row["status"] == "computed":
            row["sensitivity"] = dict(after if row["cell_id"] == REPORTED else row["primary"])
            row["equals_primary"] = row["sensitivity"] == row["primary"]
    for row in record["floor_cells"]:
        decode = row["cell_id"] in FLOOR_CELLS.values()
        row["sensitivity"] = dict(floor_after, allowance_j=1.0) if decode else dict(row["primary"])
        row["equals_primary"] = row["sensitivity"] == row["primary"]
    for row in record["contrasts"]:
        row["sensitivity"] = dict(contrast_after) if row["contrast_id"] == DECODE else (
            dict(row["sensitivity"]) if widened else dict(row["primary"]))
    files[DISCLOSURE]["sensitivity"] = copy.deepcopy(record)
    rows = {(line, row.get("contrast_id") or row["cell_id"]): row for line, section in
            (("sensitivity_reported", "reported_cells"), ("sensitivity_floor", "floor_cells"),
             ("sensitivity_contrast", "contrasts")) for row in record[section]}
    for line in files[DISCLOSURE]["block_lines"]:
        if line["line"] in ("sensitivity_reported", "sensitivity_floor", "sensitivity_contrast"):
            line["record"] = copy.deepcopy(rows[(line["line"], line["record"].get("contrast_id") or line["record"]["cell_id"])])
        if line["line"] == "sensitivity_bmax":
            line["value_s"] = 0.0625 if widened else 0.03
        if line["line"] == "sensitivity_window":
            line.update(b_sens_s=bound, widened=widened)
    files[f"brackets/{SHA}-block.json"]["value_s"] = 0.0625 if widened else 0.03
    for pack in ("alpha", "beta", "gamma"):
        files[f"brackets/{SHA}-{pack}.json"]["b_sens"] = bound
    line = ours["disclosures"]["sensitivity_bound"]
    line["B_max_s"] = 0.0625 if widened else 0.03
    for window in line["windows"].values():
        window["b_sens_s"] = bound
    line["reported_cells"][FAMILY] = {"status": "computed", "mean_j": after["mean_j"], "lower_j": after["lower_j"],
                                      "upper_j": after["upper_j"], "interval": {"h_j": after["h_j"], "B_j": after["B_j"]},
                                      "attribution_floor": {"value_j": after["attribution_floor_j"]}}
    for pack in FLOOR_CELLS:
        line["floor_cells"][MODEL_CELLS[pack]] = dict(floor_after)
    line["contrasts"][DECODE].update(floor_gate_j=contrast_after["floor_gate_j"], D_j=contrast_after["D_j"])
    if not widened:
        line["contrasts"][test_comparator.PREFILL]["D_j"] = 2.75


# Each relation word of the fixture: (record section, row index, word).
RELATION_WORDS = (("reported_cells", 0, "equals_primary"), ("reported_cells", 0, "not_below_primary"),
                  ("reported_cells", 0, "mean_and_half_width_equal_primary"),
                  ("floor_cells", 0, "equals_primary"), ("floor_cells", 1, "not_below_primary"),
                  ("contrasts", 0, "not_below_primary"), ("contrasts", 0, "outcome_equals_primary"),
                  ("contrasts", 0, "bound_independent_values_equal_primary"))
BLOCK_LINES = {"reported_cells": "sensitivity_reported", "floor_cells": "sensitivity_floor",
               "contrasts": "sensitivity_contrast"}


class SensitivityFixtureTests(Round):
    """Opus F4: the sensitivity comparisons on a producer-shaped computed record (sound, then each word flipped)."""
    def flip(self, section, index, word, copies=("record", "disclosure", "block")):
        """The word negated in the chosen printed copies: L9's record, the disclosure's copy, its block line."""
        targets = []
        if "record" in copies:
            targets.append(self.files[SENSITIVITY][section][index])
        if "disclosure" in copies:
            targets.append(self.files[DISCLOSURE]["sensitivity"][section][index])
        if "block" in copies:
            name = BLOCK_LINES[section]
            lines = [r for r in self.files[DISCLOSURE]["block_lines"] if r["line"] == name]
            targets.append(lines[index]["record"])
        for target in targets:
            target[word] = not target[word]

    def test_sound_window_passes_widened_and_not(self):
        for widened in (True, False):
            with self.subTest(widened=widened):
                self.setUp()
                with_sensitivity(self, widened)
                code, err, out = self.exit_code(CODED)
                self.assertEqual((code, err), (0, ""))
                rows = {r["key"]: r for r in out["comparisons"] if r["key"].startswith("sensitivity/")}
                for key, value in ((f"sensitivity/alpha/{FAMILY}/equals_primary", not widened),
                                   (f"sensitivity/alpha/{FAMILY}/not_below_primary", True),
                                   (f"sensitivity/alpha/{FAMILY}/mean_and_half_width_equal_primary", True),
                                   (f"sensitivity/{MODEL_CELLS['alpha']}/equals_primary", not widened),
                                   (f"sensitivity/{MODEL_CELLS['beta']}/not_below_primary", True),
                                   (f"sensitivity/{DECODE}/not_below_primary", True),
                                   (f"sensitivity/{DECODE}/outcome_equals_primary", True),
                                   (f"sensitivity/{DECODE}/bound_independent_values_equal_primary", True),
                                   ("sensitivity/windows/alpha/widened", widened)):
                    self.assertEqual((rows[key]["l9"], rows[key]["recompute"], rows[key]["verdict"]),
                                     (value, value, "AGREE"), key)
                leaves = out["coverage"]["leaves"]
                for path in ("disclosure:sensitivity/reported_cells/*/equals_primary",
                             "disclosure:block_lines/sensitivity_floor/record/not_below_primary",
                             "disclosure:block_lines/sensitivity_contrast/record/outcome_equals_primary",
                             "disclosure:sensitivity/contrasts/*/bound_independent_values_equal_primary",
                             "disclosure:cells/reported_cell/status", "disclosure:cells/battery_assist_cell/primary/status"):
                    self.assertEqual(leaves[path], "outcome_word", path)

    def test_each_relation_word_flipped_fails(self):
        for widened in (True, False):
            for section, index, word in RELATION_WORDS:
                for copies in (("record", "disclosure", "block"), ("disclosure",), ("block",)):
                    with self.subTest(widened=widened, word=word, section=section, copies=copies):
                        self.setUp()
                        with_sensitivity(self, widened)
                        self.flip(section, index, word, copies)
                        self.assertNotEqual(self.outcome(), 0)
        # Counterfactual: c372211bf exempted the two by-construction words, so a printed False passed.
        for section, word in (("reported_cells", "mean_and_half_width_equal_primary"),
                              ("contrasts", "bound_independent_values_equal_primary")):
            with self.subTest(counterfactual=word):
                self.setUp()
                with_sensitivity(self)
                self.flip(section, 0, word)
                with mock.patch.object(cmp, "COVERAGE", OLD_RULES + cmp.COVERAGE), \
                        mock.patch.object(cmp.Comparison, "exact", rows_off(
                            cmp.Comparison.exact, "/mean_and_half_width_equal_primary",
                            "/bound_independent_values_equal_primary")):
                    self.assertEqual(self.outcome(), 0)

    def test_widened_flipped_fails(self):
        for widened in (True, False):
            with self.subTest(widened=widened):
                self.setUp()
                with_sensitivity(self, widened)
                for record in (self.files[SENSITIVITY], self.files[DISCLOSURE]["sensitivity"]):
                    record["windows"]["beta"]["widened"] = not widened
                next(r for r in self.files[DISCLOSURE]["block_lines"]
                     if r["line"] == "sensitivity_window" and r["pack"] == "beta")["widened"] = not widened
                code, _, out = self.exit_code(CODED)
                self.assertNotEqual(code, 0)
                self.assertEqual(self.row(out, "sensitivity/windows/beta/widened")["verdict"], "DISAGREE")

    def test_reported_cell_status_words_fail(self):
        for word, path in (("reported_cell", ("status",)), ("battery_assist_cell", ("primary", "status"))):
            for value in ("one_unit", "not_computable", "refused"):
                with self.subTest(word=word, value=value):
                    self.setUp()
                    with_sensitivity(self)
                    lines, index = find(self, word)
                    target = lines[index]
                    for key in path[:-1]:
                        target = target[key]
                    target[path[-1]] = value
                    self.assertNotEqual(self.outcome(), 0)
                    with mock.patch.object(cmp, "COVERAGE", OLD_RULES + cmp.COVERAGE), \
                            mock.patch.object(cmp.Comparison, "exact", rows_off(
                                cmp.Comparison.exact, "/reported_cell/status", "/battery_assist_cell/primary/status")):
                        self.assertEqual(self.outcome(), 0)

    def test_a_dropped_reported_cell_line_disagrees(self):
        with_sensitivity(self)
        self.files[DISCLOSURE]["cells"] = [r for r in self.files[DISCLOSURE]["cells"] if r["line"] != "reported_cell"]
        code, _, out = self.exit_code(CODED)
        self.assertEqual(code, 1)
        self.assertEqual(self.row(out, f"disclosure/cells/reported_cell/alpha/{FAMILY}", "routing_id")["l9"], None)

    def test_with_references_and_neg8_lines_still_pass(self):
        with_sensitivity(self)
        with_neg8(self)
        with_references(self)
        self.assertEqual(self.exit_code(CODED)[:2], (0, ""))


def rows_off(exact, *suffixes):
    """No row for keys ending in these suffixes (a check c372211bf did not have)."""
    def patched(self, family, key, l9, ours, raw=cmp.MISSING):
        if key.endswith(suffixes):
            return None
        return exact(self, family, key, l9, ours, raw)
    return patched


class CommentTests(GateCase):
    """Opus F5: the exclusions_sha256 comment names the stored file and the re-derivation binding."""
    def test_comment_names_the_stored_file(self):
        source = cmp.Path(cmp.__file__).read_text()
        self.assertNotIn("the one built from the exclusions the recompute re-derived", source)
        self.assertIn("hash the stored derived/exclusions.json", source)
        self.assertIn("exclusions_rederivation == agrees", source)
