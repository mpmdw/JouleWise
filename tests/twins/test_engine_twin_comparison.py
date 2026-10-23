"""Post-blind synthetic comparison; evidence adapters are explicitly stubbed.

The standalone twin was saved and hashed before production code was read.
These adapters compare real estimator, ABBA assembly, claim and LOO code.
No disk evidence, claim-window outcomes, authentication, or hardware is used.
"""

from contextlib import ExitStack
from dataclasses import replace
import math
import random
from statistics import mean
from types import SimpleNamespace
import unittest
from unittest.mock import patch

import joulewise.analysis_engine as engine
from joulewise.analysis_manifest_v3 import SCHEMA_VERSION as MANIFEST_SCHEMA
from joulewise.analysis_engine.claims import evaluate_claim
from joulewise.analysis_engine.distributions import two_sided_student_t_p_value
from joulewise.analysis_engine.estimators import (
    DeterministicBoundTerm, PairedObservation, StochasticVarianceTerm,
    _ci_t_critical, estimate_paired_blocks,
)
from joulewise.analysis_engine.multiplicity import holm_adjust, benjamini_hochberg_adjust
from joulewise.analysis_engine.inputs import FloorResolution
from joulewise.analysis_engine.sensitivity import influence_triggers
from joulewise.twins.engine_twin import (
    INTERPOLATION, Block, Run, adjust, estimate, family, outcome, t_critical, t_two_sided,
)


# B5-PLAN 7.2 prints the synthetic CI half-width as 0.1489 J: 1% is
# 0.001489 J. 1e-5 J lies below it and above 1e6 ulps of every member
# energy used below (all <4096 J, at most 4.55e-7 J). No tighter bar is used
# to call a discrepancy. Dimensionless p-values use the COMMON fallback
# of 1e-6 relative, with the 1e6-ulp roundoff floor.
ENERGY_BAR_J = 1e-5


def to_observations(blocks, *, gross_variance=0.0):
    """Independent wire adapter; does not call the engine's ABBA preparation."""
    observations = []
    for b in blocks:
        kinds = set(b.contrast_bounds)
        for run in (*b.a, *b.b):
            kinds.update(run.bounds)
        stochastic = (StochasticVarianceTerm(
            "governed_synthetic", sum(r.variance for r in b.a)/len(b.a)**2,
            sum(r.variance for r in b.b)/len(b.b)**2, b.covariance),)
        if gross_variance:
            stochastic += (StochasticVarianceTerm("E_gross_repetition_j2", gross_variance, gross_variance),)
        terms = []
        for kind in sorted(kinds):
            if kind in b.contrast_bounds:
                # Production ignores the arm fields when a contrast bound is given
                # (estimators._deterministic_bound_value). Pass the recorded arm
                # means so a rule that used them would show; an arm whose members
                # do not all record the kind gets 0.0 in this ignored field only.
                arms = [mean(r.bounds[kind] for r in side)
                        if all(kind in r.bounds for r in side) else 0.0
                        for side in (b.a, b.b)]
                terms.append(DeterministicBoundTerm(kind, *arms, b.contrast_bounds[kind]))
                continue
            try:
                terms.append(DeterministicBoundTerm(
                    kind, mean(r.bounds[kind] for r in b.a),
                    mean(r.bounds[kind] for r in b.b)))
            except KeyError:
                raise ValueError(f"member bound unrecorded: {kind}") from None
        observations.append(PairedObservation(b.key, mean(r.energy for r in b.a),
                                               mean(r.energy for r in b.b), stochastic, tuple(terms)))
    return tuple(observations)


def world(differences, *, drift=0.0, bound=0.0, variance=0.0, prefix="q"):
    rows = []
    for i, d in enumerate(differences):
        base = 100 + i*7*drift
        def run(x):
            return Run(x, variance, {"E_clock_anchor_shift_bound_j": bound,
                                     INTERPOLATION: 0.0})
        rows.append(Block(f"{prefix}{i}", (run(base), run(base+3*drift)),
                          (run(base+d+drift), run(base+d+2*drift))))
    return rows


def production_outcome(value, floor, adjusted, *, reasons=(), confirmatory=True,
                       current=True, sensitivity=False):
    return evaluate_claim(
        estimate=value.estimate if value else None,
        metrology_aware_ci95=vars(value.metrology_aware_ci95) if value else None,
        decision_interval=vars(value.decision_interval) if value else None,
        floor_gate_j=floor, adjusted_rejected=adjusted is not None and adjusted <= 0.05,
        base_reason_codes=reasons, hypothesized_direction="positive",
        confirmatory_status="confirmatory" if confirmatory else "demoted_exploratory",
        evidence_class="current" if current else "legacy_l1", sensitivity_blocking=sensitivity)


def synthetic_prepared(blocks, *, missing=()):
    """Exercise production ABBA assembly while stubbing evidence admission.

    A missing index stands for a whole quad removed by sealed exclusions.
    Its manifest slot remains frozen. Exclusion authentication itself is not
    modeled: its absence in production is one of the registered L9 gaps.
    """
    entries, manifest_blocks, effective = [], [], {}
    for i, b in enumerate(blocks):
        positions = {}
        for pos, run in zip(("A1", "B1", "B2", "A2"), (b.a[0], b.b[0], b.b[1], b.a[1])):
            eid = f"{b.key}-{pos}"
            entry = {"entry_id": eid, "block_id": b.key,
                     "condition_id": "a" if pos.startswith("A") else "b"}
            entries.append(entry)
            positions[pos] = eid
            if i not in missing:
                effective[eid] = SimpleNamespace(
                    entry=entry, bundle_id=eid, base_reason_codes=(), included=True,
                    summary={"phase_energy_j": {"decode": run.energy},
                             "energy_variance_terms_j2": {"E_idle_mean_j2": 10000},
                             "synthetic_bounds": run.bounds, "synthetic_variance": run.variance})
        manifest_blocks.append({"block_id": b.key, "position_entry_ids": positions})
    contrast = {"contrast_id": "decode", "metric": {
        "name": "phase_energy_j.decode", "unit": "J", "window_class": "phase",
        "ratio_estimand": None}, "condition_a_id": "a", "condition_b_id": "b",
        "block_ids": [b.key for b in blocks], "claim_role": "primary",
        "equivalence": None, "hypothesized_direction": "positive"}
    inputs = SimpleNamespace(manifest={
        "entries": entries, "blocks": manifest_blocks,
        "schema_version": MANIFEST_SCHEMA,
        "design": {"sampling_plan": {"planned_n_blocks": len(blocks)}}},
        effective=effective, top_up_entry_ids=frozenset())
    floor = {"active_floor_j": 1.2}
    with ExitStack() as stack:
        stack.enter_context(patch.object(engine, "window_evidence_precheck", return_value={"reasons": []}))
        stack.enter_context(patch.object(engine, "deterministic_bounds",
                                         side_effect=lambda e, m: (e.summary["synthetic_bounds"], [])))
        stack.enter_context(patch.object(engine, "_resolve_contrast_floor", return_value=()))
        stack.enter_context(patch.object(engine, "_combined_floor", return_value=floor))
        stack.enter_context(patch.object(engine, "_decorate_v3_floor", side_effect=lambda m,c,f,r: f))
        prepared = engine._prepare_contrast_v3(inputs, contrast, None, None, evidence_class="current")
    return inputs, prepared


def production_loo(blocks, *, missing=()):
    """Dispatch the same valid LOO call for complete and excluded-quad worlds."""
    inputs, prepared = synthetic_prepared(blocks, missing=missing)
    family_spec = {"family_instance_id": "synthetic", "contrast_ids": ["decode"],
                   "multiplicity": {"method": "holm", "m": 1, "alpha": 0.05, "q": None}}
    point = prepared["estimate"]
    full_adjusted = {"decode": {"rejected": point.raw_p <= 0.05}}
    full_evaluations = {"decode": production_outcome(
        point, 1.2, point.raw_p, reasons=prepared["global_reason_codes"])}
    with patch.object(engine, "frozen_family_block_strata",
                      return_value=[(i, {"decode": b.key}) for i, b in enumerate(blocks)]), \
         patch.object(engine, "_subset_floor", return_value=({"active_floor_j": 1.2}, ())):
        return engine._loo_family(inputs, family_spec, {"decode": prepared},
                                  full_adjusted, full_evaluations, None)["decode"]


class ProductionComparisonTests(unittest.TestCase):
    max_energy_delta = 0.0
    compared_worlds = 0

    def compare(self, blocks):
        twin = estimate(blocks)
        actual = estimate_paired_blocks(to_observations(blocks, gross_variance=1000))
        self.assertEqual((twin.n, twin.n-1), (actual.n, actual.df))
        for a,b in ((twin.point,actual.estimate), (twin.sd,actual.sample_stddev),
                    (twin.se_repeat,actual.se_repeat), (twin.se_metrology,actual.se_metrology),
                    (twin.se_total,actual.se_total), *zip(twin.ci, vars(actual.metrology_aware_ci95).values()),
                    *zip(twin.repeat_ci, vars(actual.repeat_point_ci95).values()),
                    *zip(twin.decision, vars(actual.decision_interval).values()),
                    (sum(twin.bounds.values()),actual.deterministic_bound_total)):
            delta = abs(a-b)
            type(self).max_energy_delta = max(self.max_energy_delta, delta)
            self.assertLessEqual(delta, ENERGY_BAR_J)
        bar_p = max(abs(twin.p)*1e-6, math.ulp(twin.p)*1e6)
        self.assertLessEqual(abs(twin.p-actual.raw_p), bar_p)
        self.assertEqual(set(twin.bounds), {t.name for t in actual.deterministic_bounds})
        for term in actual.deterministic_bounds:
            self.assertLessEqual(abs(twin.bounds[term.name]-term.bound), ENERGY_BAR_J)
        type(self).compared_worlds += 1
        return twin, actual

    def test_seeded_worlds_every_registered_n_and_variance_layer(self):
        rng = random.Random(20261022)
        for n in range(5,11):
            for index in range(20):
                differences = [rng.gauss((index-10)*0.3, 0.5) for _ in range(n)]
                with self.subTest(n=n, index=index):
                    self.compare(world(differences, drift=0.75, bound=index*0.002,
                                       variance=0 if index%2 else 0.25))

    def test_covariance_and_explicit_bound_override(self):
        blocks = [replace(b, covariance=0.25,
                          contrast_bounds={"E_clock_anchor_shift_bound_j": 0.01})
                  for b in world([1,2,3,4,5], bound=2, variance=1)]
        self.compare(blocks)
        # A replaced kind need not be recorded on the members whose bounds are unused.
        first = blocks[0]
        blocks[0] = replace(first, a=(replace(first.a[0], bounds={INTERPOLATION: 0.0}), first.a[1]))
        self.compare(blocks)

    def test_probability_and_frozen_multiplicity(self):
        for df in range(3,10):
            for x in (0, 0.001, 0.1, 1, 2, 3, 10, 46.5, 100):
                twin, actual = t_two_sided(x,df), two_sided_student_t_p_value(x,df)
                self.assertLessEqual(abs(twin-actual), max(twin*1e-6, math.ulp(twin)*1e6))
        for pvalues in ({"a":0.01,"b":None}, {"a":0.04,"b":0.01},
                        {"a":0.025,"b":0.05}, {"a":1.0,"b":1.0}):
            self.assertEqual(adjust(pvalues,2), holm_adjust(pvalues,m=2))
            self.assertEqual(adjust(pvalues,2,"bh"), benjamini_hochberg_adjust(pvalues,m=2))

    def test_ci_critical_matches_production_rounding(self):
        # Both round the quantile to the registered three places, so bit identity
        # is the property. Minimum distance to k/1000 + 0.0005 over df 1..30:
        # 2.9438642875e-5 (df 26), above its 1e6-ulp noise bar 4.4408920985e-10;
        # no df needs excluding from the exact comparison.
        for df in range(1, 31):
            with self.subTest(df=df):
                self.assertEqual(t_critical(df), _ci_t_critical(df))

    def test_unrecorded_interpolation_matches_production(self):
        control = world([3]*10, bound=0.025)
        unrecorded = [replace(b, a=tuple(replace(r, bounds={
            k: v for k, v in r.bounds.items() if k != INTERPOLATION}) for r in b.a),
            b=tuple(replace(r, bounds={k: v for k, v in r.bounds.items()
                                      if k != INTERPOLATION}) for r in b.b)) for b in control]
        for label, blocks in (("unrecorded", unrecorded), ("recorded zero", control)):
            with self.subTest(interpolation=label):
                _, prepared = synthetic_prepared(blocks)
                reasons = engine._analysis_reasons(
                    prepared, prepared["estimate"], prepared["floor"],
                    prepared["floor_resolutions"], prepared["randomization_check"])
                expected = "not_resolvable" if label == "unrecorded" else "direction_supported"
                if label == "unrecorded":
                    self.assertIn("interpolation_bound_unrecorded", reasons)
                else:
                    self.assertEqual(reasons, [])
                self.assertEqual(production_outcome(prepared["estimate"], 1.2, 0,
                                                    reasons=reasons)["outcome"], expected)
                self.assertEqual(outcome(estimate(blocks), 1.2, 0), expected)

    def test_partial_kind_in_every_quad_matches_production(self):
        anchor = "E_clock_anchor_shift_bound_j"
        blocks = [replace(b, a=(replace(b.a[0], bounds={INTERPOLATION: 0.0}), b.a[1]))
                  for b in world([3]*10, bound=0.025)]
        _, prepared = synthetic_prepared(blocks)
        reasons = engine._analysis_reasons(
            prepared, prepared["estimate"], prepared["floor"],
            prepared["floor_resolutions"], prepared["randomization_check"])
        self.assertIn("required_error_term_unknown", reasons)
        self.assertEqual(prepared["estimate"].deterministic_bounds, ())
        self.assertEqual(production_outcome(prepared["estimate"], 1.2, 0,
                                            reasons=reasons)["outcome"], "not_resolvable")
        value = estimate(blocks)
        self.assertIn(anchor, value.unknown_bounds)
        self.assertEqual(outcome(value, 1.2, 0), "not_resolvable")
        with self.assertRaisesRegex(ValueError, anchor):
            to_observations(blocks)

    def test_single_mismatched_quad_production_raises_pending_fix(self):
        """Pin today's production defect pending a fix: mismatched kinds abort.

        Production should record not_resolvable with the member's reason,
        which deterministic_bounds already records. When fixed, this test
        fails and is rewritten as an outcome equality with the twin.
        """
        anchor = "E_clock_anchor_shift_bound_j"
        control = world([3]*10, bound=0.025)
        partial = list(control)
        partial[0] = replace(control[0], a=(replace(control[0].a[0],
                             bounds={INTERPOLATION: 0.0}), control[0].a[1]))
        absent_quad = list(control)
        absent_quad[0] = replace(control[0],
            a=tuple(replace(r, bounds={INTERPOLATION: 0.0}) for r in control[0].a),
            b=tuple(replace(r, bounds={INTERPOLATION: 0.0}) for r in control[0].b))
        for label, blocks in (("one member", partial), ("whole quad", absent_quad)):
            with self.subTest(missing=label):
                with self.assertRaisesRegex(
                        ValueError, "every paired block must carry the same deterministic term names"):
                    synthetic_prepared(blocks)
                value = estimate(blocks)
                self.assertIn(anchor, value.unknown_bounds)
                self.assertEqual(outcome(value, 1.2, 0), "not_resolvable")

    def test_claim_boundaries_and_registered_direction(self):
        cases = ([3]*5, [-3]*5, [0]*5, [-2,-1,1,2,3], [0.2]*4+[10])
        for differences in cases:
            for bound in (0,0.025,2):
                twin, actual = self.compare(world(differences,bound=bound))
                for floor in (None,0,0.1,1.2,abs(twin.point)):
                    for adjusted in (0,0.05,0.051,1):
                        reasons = engine._interpolation_reasons(actual, {"active_floor_j": floor})
                        expected = outcome(twin,floor,adjusted)
                        observed = production_outcome(actual,floor,adjusted,reasons=reasons)
                        self.assertEqual(expected,observed["outcome"])
        for reason in ("metric_missing_or_nonfinite", "required_covariance_unknown", "floor_cmp_missing"):
            twin,actual = self.compare(world([3]*5))
            self.assertEqual(outcome(twin,1,0,reasons=[reason]),
                             production_outcome(actual,1,0,reasons=[reason])["outcome"])

    def test_family_wide_loo_matches_kernels_and_influence_rules(self):
        contrasts = {"decode":world([0.2]*4+[10]), "prefill":world([2,2.1,1.9,2.2,1.8])}
        floors = {"decode":1.2,"prefill":1.2}
        twins = family(contrasts,floors)
        actual = {k:estimate_paired_blocks(to_observations(v)) for k,v in contrasts.items()}
        adjusted = holm_adjust({k:v.raw_p for k,v in actual.items()},m=2)
        mapping = {"sign":"estimate_sign","floor":"floor_status", "magnitude":"estimate_magnitude",
                   "adjusted_verdict":"adjusted_rejection","outcome":"outcome"}
        for cid, result in twins.items():
            full_eval = production_outcome(actual[cid],floors[cid],adjusted[cid])
            for row in result["loo"]:
                estimates = {k:estimate_paired_blocks(to_observations([b for b in bs if b.key!=row["omitted"]]))
                             for k,bs in contrasts.items()}
                adj = holm_adjust({k:v.raw_p for k,v in estimates.items()},m=2)
                evaluation = production_outcome(estimates[cid],floors[cid],adj[cid])
                self.assertEqual(row["outcome"], evaluation["outcome"])
                def state(v,p,e):
                    return {"estimate":v.estimate,"floor_status":abs(v.estimate)>floors[cid],
                            "adjusted_rejection":p<=0.05,"outcome":e["outcome"]}
                triggers = influence_triggers(state(actual[cid],adjusted[cid],full_eval),
                                              state(estimates[cid],adj[cid],evaluation),active_threshold=floors[cid])
                self.assertEqual({mapping[t] for t in row["triggers"]},set(triggers))
            influential = any(set(r["triggers"])-{"magnitude"} for r in result["loo"])
            for confirmatory,current in ((True,True),(False,True),(True,False)):
                evaluated = production_outcome(actual[cid],floors[cid],adjusted[cid],
                                              sensitivity=influential,confirmatory=confirmatory,current=current)
                expected = family(contrasts,floors,confirmatory=confirmatory,current=current)[cid]["ceiling"]
                self.assertEqual(expected,evaluated["claim_level_ceiling"])

    def test_real_production_abba_assembly_complete(self):
        blocks = world([3.1,2.9,3.3,3,2.8,3.2,3.1,2.9,3,2.7],drift=0.7,bound=0.025)
        _,prepared = synthetic_prepared(blocks)
        self.assertEqual(prepared["global_reason_codes"],[])
        self.assertLessEqual(abs(estimate(blocks).point-prepared["estimate"].estimate),ENERGY_BAR_J)
        self.assertLessEqual(abs(estimate(blocks).decision[0]-prepared["estimate"].decision_interval.lower),ENERGY_BAR_J)
        self.assertEqual(prepared["estimate"].se_metrology,0)
        self.assertEqual(prepared["randomization_check"]["status"],"not_required")

    def test_floor_gate_retains_both_forms_and_sides(self):
        for values in ((1,2,3,4),(4,3,2,1),(1,4,3,2)):
            a_abs,a_cmp,b_abs,b_cmp = values
            resolutions = tuple(FloorResolution(
                status="exact",source_cell_ids=(side,),floor_abs_j=a,
                floor_cmp_j=b,floor_gate_j=max(a,b),artifact_id="synthetic",
                artifact_sha256="0"*64,transport_group_id=None,
                transport_rule_id=None,reason_codes=())
                for side,a,b in (("a",a_abs,a_cmp),("b",b_abs,b_cmp)))
            self.assertEqual(engine._combined_floor(resolutions)["active_floor_j"], max(values))

    def test_complete_production_loo_dispatch(self):
        blocks = world([3.1,2.9,3.3,3,2.8,3.2,3.1,2.9,3,2.7],bound=0.025)
        actual = production_loo(blocks)
        twin = family({"decode":blocks},{"decode":1.2})["decode"]["loo"]
        self.assertEqual(len(actual),len(twin))
        for a,b in zip(actual,twin):
            self.assertEqual(a["omitted_block_id"],b["omitted"])
            self.assertEqual(a["outcome"],b["outcome"])
            self.assertLessEqual(abs(a["estimate"]-b["estimate"].point),ENERGY_BAR_J)

    def test_kept_quads_production_refuses_pending_l9_exclusion_consumer(self):
        """Pin a known production gap fixed by the L9 exclusion consumer.

        The consumer authenticates removed units, keeps the frozen planned
        slots, and tells an allowed exclusion apart from unplanned
        incompleteness. When L9 lands this fails and is rewritten as equality
        of production outcome, ceiling and LOO row count with the twin's.
        """
        blocks = world([3.1,2.9,3.3,3,2.8,3.2,3.1,2.9,3,2.7],bound=0.025)
        _,prepared = synthetic_prepared(blocks,missing=(3,))
        # Production withholds this contrast's p from the frozen family today.
        self.assertIsNone(engine._claim_raw_p(prepared, prepared["estimate"]))
        kept = [b for i,b in enumerate(blocks) if i != 3]
        expected = family({"decode":kept,"prefill":kept},{"decode":1.2,"prefill":1.2})["decode"]
        point = prepared["estimate"]
        self.assertAlmostEqual(point.estimate, estimate(kept).point, delta=ENERGY_BAR_J)
        self.assertAlmostEqual(point.estimate, 3.0, delta=ENERGY_BAR_J)
        self.assertTrue({"fixed_n_plan_incomplete", "paired_block_incomplete"}
                        <= set(prepared["global_reason_codes"]))
        p = point.raw_p
        adjusted = holm_adjust({"decode": p, "prefill": p}, m=2)
        observed = production_outcome(point,1.2,adjusted["decode"],
                                      reasons=prepared["global_reason_codes"])
        self.assertEqual(observed["outcome"], "not_resolvable")
        self.assertNotEqual(observed["claim_level_ceiling"], "L2")
        self.assertEqual(expected["outcome"], "direction_supported")
        self.assertEqual(expected["ceiling"], "L2")

    def test_kept_quads_production_loo_pending_l9_exclusion_consumer(self):
        """Pin a known production gap fixed by the L9 exclusion consumer.

        When L9 lands this fails and is rewritten as equality of production
        outcome, ceiling and LOO row count with the twin's.
        """
        blocks = world([3.1,2.9,3.3,3,2.8,3.2,3.1,2.9,3,2.7],bound=0.025)
        self.assertEqual(len(production_loo(blocks, missing=())), 10)
        self.assertEqual(len(production_loo(blocks, missing=(3,))), 0)
        kept = [b for i, b in enumerate(blocks) if i != 3]
        self.assertEqual(len(family({"decode": kept}, {"decode": 1.2})["decode"]["loo"]), 9)

    @classmethod
    def tearDownClass(cls):
        print(f"Twin comparison: {cls.compared_worlds} numeric worlds; max energy delta {cls.max_energy_delta:.9g} J; bar {ENERGY_BAR_J:g} J")


if __name__ == "__main__":
    unittest.main()
