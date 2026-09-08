"""S6 synthetic contract oracle: no paper renderer, evidence IO or capabilities.

These records exercise semantics only. They are deliberately not D-173 types.
The production D-168 census is eight ordinary/independent ratios plus four
comparative R_cm values; these synthetic fixtures preserve that full arity.
"""
from dataclasses import dataclass, replace
from decimal import Decimal as D
from itertools import product
import unittest


@dataclass(frozen=True)
class FloorCell:
    branch: str = 'exact'
    components_valid: tuple = (True, True)
    operative: D | None = D('3')
    reason: str | None = None
    point_diagnostic_published: bool = False


def floor_slot(cell):
    if cell.components_valid != (True, True) or cell.point_diagnostic_published:
        raise ValueError('unvalidated components or promoted diagnostic')
    if cell.branch == 'exact':
        if cell.operative is None or not cell.operative.is_finite() or cell.operative < 0:
            raise ValueError('missing exact floor')
        if cell.reason is not None:
            raise ValueError('conflicting floor branch')
        return ('exact', cell.operative)
    if cell.branch not in ('no_exact_floor', 'terminal_refusal') or not cell.reason:
        raise ValueError('unproven floor branch')
    if cell.operative is not None:
        raise ValueError('conflicting floor value')
    return (cell.branch, cell.reason)


@dataclass(frozen=True)
class Comparison:
    estimate: D = D('10')
    floor: D = D('3')
    measurement: tuple = (D('9'), D('11'))
    decision: tuple = (D('8'), D('12'))
    direction: int = 1
    holm_pass: bool = True


def model_outcome(value):
    numbers = (value.estimate, value.floor, *value.measurement, *value.decision)
    if (not all(x.is_finite() for x in numbers) or value.floor < 0
            or value.direction not in (-1, 1)
            or value.measurement[0] > value.measurement[1]
            or value.decision[0] > value.decision[1]):
        raise ValueError('invalid comparison')
    if abs(value.estimate) <= value.floor:
        return 'magnitude_failed'
    if not all(x * value.direction > 0
               for x in (*value.measurement, *value.decision)):
        return 'sign_failed'
    if not value.holm_pass:
        return 'holm_failed'
    return 'directional'


@dataclass(frozen=True)
class Stop:
    stage: str
    reason: str
    affected: str


@dataclass(frozen=True)
class Scenario:
    ratio: str = 'A'
    ratios: tuple = (D('2'),) * 8
    comparative_ratios: tuple = (D('3'),) * 4
    decode: Comparison = Comparison()
    prefill: Comparison = Comparison()
    stops: tuple = ()
    stage_order: tuple = ('before comparison', 'at close-out')
    evidence: str = 'verified'
    exhausted_count: int | None = None
    characterization: str = 'collected'
    abstract: str = 'synthetic'


@dataclass(frozen=True)
class Expected:
    ratio: str
    decode: str
    prefill: str
    stop: Stop | None = None
    evidence: str = 'verified'
    reducer: str | None = None
    prefix: str | None = None
    repeated_decode: tuple = ()
    repeated_prefill: tuple = ()
    holm_size: int = 2
    standing: str = 'SYNTHETIC_NON_ISSUING'
    s1: str = 'UNBOUND'
    s3: str = 'UNBOUND'
    paper_prose: str = ''


def expected(ratio='A', decode='directional', prefill='directional', **kwargs):
    # Two logical copies exercise equality; actual placement count is S1-unbound.
    return Expected(ratio, decode, prefill,
                    repeated_decode=(decode, decode),
                    repeated_prefill=(prefill, prefill), **kwargs)


def check_fixture(case, output):
    """Reject an inconsistent proposed symbolic output; never issue paper text."""
    if len(case.abstract.split()) > 250:
        raise ValueError('abstract exceeds 250')
    # Knowing chronological order supplies no multi-stage precedence policy.
    if case.stage_order != ('before comparison', 'at close-out'):
        raise ValueError('stage order UNBOUND')
    if len(case.stops) > 1:
        raise ValueError('stage precedence UNBOUND or conflicting stages')
    for stop in case.stops:
        if (stop.stage not in ('before comparison', 'at close-out')
                or not stop.reason or not stop.affected):
            raise ValueError('invalid stop')
    if case.evidence not in ('verified', 'unavailable', 'invalid'):
        raise ValueError('invalid evidence state')
    if case.evidence != 'verified' and case.stops:
        raise ValueError('absence is not issued refusal')
    if case.characterization not in ('collected', 'not_collected', 'unavailable', 'invalid'):
        raise ValueError('invalid characterization')
    if case.stops:
        ratio = 'REFUSAL'
    elif case.evidence != 'verified':
        ratio = 'FALLBACK'
    else:
        if (len(case.ratios) != 8 or len(case.comparative_ratios) != 4
                or any(not x.is_finite() or x < 0
                       for x in (*case.ratios, *case.comparative_ratios))):
            raise ValueError('incomplete synthetic ratio census')
        ratio = 'A' if all(x >= 2 for x in (*case.ratios, *case.comparative_ratios)) else 'B'
    if case.ratio != ratio:
        raise ValueError('ratio disposition mismatch')
    decode, prefill = model_outcome(case.decode), model_outcome(case.prefill)
    for stop in case.stops:
        if stop.stage == 'before comparison':
            if stop.affected == 'prefill:model-small:window-beta':
                prefill = 'not_evaluated'
            elif stop.affected == 'decode:model-small:window-alpha':
                decode = 'not_evaluated'
            else:
                raise ValueError('unbound affected comparison')
    reducer = None
    if case.exhausted_count is not None:
        if type(case.exhausted_count) is not int or case.exhausted_count < 0:
            raise ValueError('invalid count')
        if case.exhausted_count < 3:
            prefill = reducer = 'not_resolvable_sample_count'
        elif case.exhausted_count < 5:
            prefill = 'below the pre-registered count floor of 5'
            reducer = 'resolvable'
        else:
            raise ValueError('exhausted ladder cannot clear count five')
    canonical = expected(
        ratio, decode, prefill, stop=case.stops[0] if case.stops else None,
        evidence=case.evidence, reducer=reducer,
        prefix='NOT_COLLECTED_PREFIX_UNBOUND' if case.characterization == 'not_collected' else None)
    if case.evidence != 'verified' and (output.ratio == 'REFUSAL' or output.stop):
        raise ValueError('absence is not issued refusal')
    if output.stop != canonical.stop:
        raise ValueError('contradictory stop reason or identity')
    for phase in ('decode', 'prefill'):
        proposed, governed = getattr(output, phase), getattr(canonical, phase)
        if proposed != governed:
            if proposed == 'directional':
                raise ValueError('directional claim forbidden by comparison gates')
            if phase == 'decode' and governed == 'directional':
                raise ValueError('unaffected decode must survive')
            raise ValueError('contradictory comparison outcome')
    if (output.repeated_decode != canonical.repeated_decode
            or output.repeated_prefill != canonical.repeated_prefill):
        raise ValueError('repeated verdicts must match byte-for-byte')
    if output != canonical:
        raise ValueError('inconsistent symbolic output')


def transact(case, output, sink, late_failure=False):
    """In-memory publication model only; sink never contains paper prose."""
    check_fixture(case, output)
    staged = (output,)
    if late_failure:
        raise RuntimeError('synthetic late failure')
    sink.extend(staged)


OUTCOMES = (
    (Comparison(), 'directional'),
    (Comparison(estimate=D('3')), 'magnitude_failed'),
    (Comparison(decision=(D('-1'), D('12'))), 'sign_failed'),
    (Comparison(holm_pass=False), 'holm_failed'),
)


class PaperComparisonContractTests(unittest.TestCase):
    def test_floor_branches_require_explicit_validated_evidence(self):
        self.assertEqual(floor_slot(FloorCell()), ('exact', D('3')))
        for branch in ('no_exact_floor', 'terminal_refusal'):
            self.assertEqual(floor_slot(FloorCell(branch=branch, operative=None,
                             reason='synthetic_governed_reason')),
                             (branch, 'synthetic_governed_reason'))
        for bad in (FloorCell(operative=None), FloorCell(components_valid=(True, False)),
                    FloorCell(point_diagnostic_published=True),
                    FloorCell(branch='no_exact_floor', operative=None),
                    FloorCell(branch='unknown', operative=None, reason='unknown')):
            with self.assertRaises(ValueError):
                floor_slot(bad)

    def test_ratio_crosses_independent_model_outcomes(self):
        for ratio, (decode, dtext), (prefill, ptext) in product(('A', 'B'), OUTCOMES, OUTCOMES):
            with self.subTest(ratio=ratio, decode=dtext, prefill=ptext):
                case = Scenario(ratio=ratio, ratios=(D('2'),) * 8 if ratio == 'A'
                                else (D('1.9'),) + (D('2'),) * 7, decode=decode, prefill=prefill)
                check_fixture(case, expected(ratio, dtext, ptext))

    def test_two_stop_stages_and_unaffected_decode(self):
        before = Stop('before comparison', 'synthetic_window_non_admission',
                      'prefill:model-small:window-beta')
        close = Stop('at close-out', 'synthetic_zero_denominator', 'ratio:cell-beta')
        for stop, prefill in ((before, 'not_evaluated'), (close, 'directional')):
            with self.subTest(stage=stop.stage):
                case = Scenario(ratio='REFUSAL', stops=(stop,))
                good = expected('REFUSAL', prefill=prefill, stop=stop)
                check_fixture(case, good)
                with self.assertRaisesRegex(ValueError, 'unaffected decode must survive'):
                    check_fixture(case, replace(good, decode='not_evaluated',
                                                repeated_decode=('not_evaluated',) * 2))

    def test_unavailable_and_invalid_are_not_issued_refusals(self):
        for state in ('unavailable', 'invalid'):
            case = Scenario(ratio='FALLBACK', evidence=state)
            good = expected('FALLBACK', evidence=state)
            check_fixture(case, good)
            forged = replace(good, ratio='REFUSAL', stop=Stop(
                'at close-out', 'invented_missing_ratio', 'ratio:cell-beta'))
            with self.assertRaisesRegex(ValueError, 'absence is not issued refusal'):
                check_fixture(case, forged)
            with self.assertRaisesRegex(ValueError, 'absence is not issued refusal'):
                check_fixture(replace(case, ratio='REFUSAL', stops=(forged.stop,)), forged)

    def test_d166_split_retains_decode_and_two_test_family(self):
        for count in (0, 2, 3, 4):
            with self.subTest(count=count):
                case = Scenario(exhausted_count=count)
                text = ('not_resolvable_sample_count' if count < 3
                        else 'below the pre-registered count floor of 5')
                good = expected(prefill=text, reducer='not_resolvable_sample_count'
                                if count < 3 else 'resolvable')
                check_fixture(case, good)
                for bad in (replace(good, holm_size=1), replace(good, decode=''),
                            replace(good, reducer='resolvable' if count < 3
                                    else 'not_resolvable_sample_count')):
                    with self.assertRaises(ValueError):
                        check_fixture(case, bad)

    def test_conflicting_stages_have_no_inferred_precedence(self):
        stops = (Stop('before comparison', 'non_admission', 'prefill:model-small:window-beta'),
                 Stop('at close-out', 'zero_denominator', 'ratio:cell-beta'))
        for pair in (stops, stops[::-1], (stops[0], replace(stops[0], reason='conflict'))):
            with self.assertRaises(ValueError):
                check_fixture(Scenario(ratio='REFUSAL', stops=pair), expected('REFUSAL'))

    def test_known_stage_order_does_not_license_contradictions(self):
        stop = Stop('before comparison', 'synthetic_window_non_admission',
                    'prefill:model-small:window-beta')
        case = Scenario(ratio='REFUSAL', stops=(stop,))
        self.assertEqual(case.stage_order, ('before comparison', 'at close-out'))
        self.assertEqual(len(case.stops), 1)  # Passes the independent arity guard.
        good = expected('REFUSAL', prefill='not_evaluated', stop=stop)
        check_fixture(case, good)
        with self.assertRaisesRegex(ValueError, 'contradictory stop reason or identity'):
            check_fixture(case, replace(good, stop=replace(stop, reason='conflict')))
        with self.assertRaisesRegex(ValueError, 'contradictory comparison outcome'):
            check_fixture(case, replace(good, prefill='magnitude_failed',
                                       repeated_prefill=('magnitude_failed',) * 2))

    def test_full_d168_census_and_each_ratio_component(self):
        case = Scenario()
        check_fixture(case, expected())
        for field, size in (('ratios', 8), ('comparative_ratios', 4)):
            for arity in (size - 1, size + 1):
                with self.subTest(field=field, arity=arity):
                    with self.assertRaisesRegex(ValueError, 'incomplete synthetic ratio census'):
                        check_fixture(replace(case, **{field: (D('2'),) * arity}), expected())
            for index in range(size):
                values = list(getattr(case, field))
                values[index] = D('1.9')
                check_fixture(replace(case, ratio='B', **{field: tuple(values)}), expected('B'))

    def test_characterization_prefix_is_independent(self):
        for ratio in ('A', 'B'):
            for state in ('collected', 'not_collected', 'unavailable', 'invalid'):
                case = Scenario(ratio=ratio, ratios=(D('2'),) * 8 if ratio == 'A'
                                else (D('1'),) + (D('2'),) * 7, characterization=state)
                check_fixture(case, expected(ratio, prefix='NOT_COLLECTED_PREFIX_UNBOUND'
                                            if state == 'not_collected' else None))

    def test_magnitude_equality_sign_and_holm_counterfactuals(self):
        for comparison, outcome in OUTCOMES[1:]:
            case = Scenario(decode=comparison)
            check_fixture(case, expected(decode=outcome))
            # Ratio A cannot force a directional claim in either repeated slot.
            with self.assertRaisesRegex(ValueError, 'directional claim forbidden by comparison gates'):
                check_fixture(case, expected(decode='directional'))
        self.assertEqual(model_outcome(Comparison(estimate=D('-3'))), 'magnitude_failed')
        self.assertEqual(model_outcome(Comparison(decision=(D('0'), D('12')))), 'sign_failed')
        self.assertEqual(model_outcome(Comparison(measurement=(D('-11'), D('-9')))), 'sign_failed')
        self.assertEqual(model_outcome(Comparison(estimate=D('-10'), direction=-1,
                         measurement=(D('-11'), D('-9')), decision=(D('-12'), D('-8')))), 'directional')

    def test_exact_repeated_verdict_consistency(self):
        good = expected()
        for bad in (replace(good, repeated_decode=('directional', 'Directional')),
                    replace(good, repeated_prefill=('directional', 'directional ')),
                    replace(good, repeated_decode=('directional',))):
            with self.assertRaisesRegex(ValueError, 'repeated verdicts must match byte-for-byte'):
                check_fixture(Scenario(), bad)

    def test_abstract_after_substitution_boundary(self):
        check_fixture(Scenario(abstract=' '.join(['word'] * 250)), expected())
        with self.assertRaisesRegex(ValueError, 'abstract exceeds 250'):
            check_fixture(Scenario(abstract=' '.join(['word'] * 251)), expected())

    def test_transaction_no_partial_emission_on_late_failure(self):
        existing = ['existing synthetic artifact']
        with self.assertRaisesRegex(RuntimeError, 'synthetic late failure'):
            transact(Scenario(), expected(), existing, late_failure=True)
        self.assertEqual(existing, ['existing synthetic artifact'])
        empty = []
        with self.assertRaisesRegex(RuntimeError, 'synthetic late failure'):
            transact(Scenario(), expected(), empty, late_failure=True)
        self.assertEqual(empty, [])  # Fails if staging leaks before late failure.
        with self.assertRaisesRegex(ValueError, 'abstract exceeds 250'):
            transact(Scenario(abstract='word ' * 251), expected(), empty)
        self.assertEqual(empty, [])
        transact(Scenario(), expected(), empty)
        self.assertEqual(empty, [expected()])

    def test_fixtures_cannot_claim_issuance_or_bind_dependencies(self):
        for bad in (replace(expected(), standing='ISSUED'),
                    replace(expected(), paper_prose='A directional model claim.'),
                    replace(expected(), s1='bound'), replace(expected(), s3='joules')):
            with self.assertRaises(ValueError):
                check_fixture(Scenario(), bad)
        self.assertFalse(hasattr(expected(), '_custody_token'))


if __name__ == '__main__':
    unittest.main()
