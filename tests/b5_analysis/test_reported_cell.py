"""Synthetic, independently calculated S8 reported-cell controls."""
from copy import deepcopy
from dataclasses import replace
import math
import statistics
import unittest
from joulewise import paper_reported_energy as e
from joulewise.b5_analysis.kept_units import CellKeptUnits, ReportedCellKept, Unit, DroppedUnit
from joulewise.analysis_engine.distributions import student_t_quantile
from tests.test_paper_reported_energy import synthetic_input

R = [10.0, 10.2, 9.9, 10.1, 10.0, 10.3, 9.8, 10.1, 10.0, 9.6]
B = [10.4, 10.1, 10.3, 10.2, 10.5, 10.0, 10.2, 10.3, 10.1, 9.9]


def case(remove_r=(), remove_b=()):
    data = synthetic_input(prefill_length=2048)
    cell, source = data['spec']['reported_energy_cells'][0], data['cells'][0]
    rows, binding = source['rows'], source['binding']
    for i, row in enumerate(rows):
        row['energy_j'] = R[i] if i < 10 else B[(i-10)//4] + (-0.3, -0.1, 0.1, 0.3)[(i-10)%4]
        row['bounds_j'] = dict(zip(e.BOUND_KINDS, (0.01, 0.0, 0.05)))
        row['tokens']['output'] = 512
    binding['attribution_floor_j'] = 0.01
    kept, dropped = {'repeat': [], 'quad': []}, []
    for stratum, ords in [('repeat', [(i,) for i in range(1,11)]),
                           ('quad', [tuple(range(i,i+4)) for i in range(11,51,4)])]:
        for i, ordinals in enumerate(ords,1):
            u = Unit('synthetic', stratum, f'{stratum}-{i}', tuple(rows[n-1]['member']['bundle_id'] for n in ordinals), ordinals, (None,)*len(ordinals))
            if i in (remove_r if stratum == 'repeat' else remove_b):
                dropped.append(DroppedUnit(**u.__dict__, codes=('synthetic',), families=('synthetic',)))
            else:
                kept[stratum].append(u)
    c = CellKeptUnits('synthetic', True, {'repeat':10,'quad':10}, {'repeat':5,'quad':5},
                     {s:tuple(us) for s,us in kept.items()}, tuple(dropped), len(kept['repeat']),len(kept['quad']))
    k = ReportedCellKept(c, tuple(i for i in range(1,11) if i not in remove_r), tuple(sorted(remove_r)),
                         tuple(tuple(range(11+4*(i-1),15+4*(i-1))) for i in range(1,11) if i not in remove_b),
                         tuple(tuple(range(11+4*(i-1),15+4*(i-1))) for i in sorted(remove_b)))
    allowed = e._kept_ordinals(k)
    return cell, [row for row in rows if row['member']['ordinal'] in allowed], binding, k


def project(c):
    cell, rows, binding, kept = c
    return e._project_cell(cell, rows, binding, kept=kept, exclusions_sha256='f'*64)


class ReportedCellTests(unittest.TestCase):
    def test_S8F1_ten_repeats_eight_quads_remain_stratified(self):
        c = case((), (5, 9))
        for row in c[1]:
            ordinal = row['member']['ordinal']
            row['bounds_j'] = {kind: (ordinal + 3*j)/100
                               for j, kind in enumerate(e.BOUND_KINDS)}
            row['tokens']['output'] = 100 + 7*ordinal
        c[2]['attribution_floor_j'] = max(row['bounds_j'][e.BOUND_KINDS[0]] for row in c[1])
        rows = c[1]
        repeats, quads = rows[:10], rows[10:]
        r = [row['energy_j'] for row in repeats]
        b = [statistics.fmean(row['energy_j'] for row in quads[i:i+4])
             for i in range(0, len(quads), 4)]
        mean = .2*statistics.fmean(r) + .8*statistics.fmean(b)
        variance = .2**2*statistics.variance(r)/10 + .8**2*statistics.variance(b)/8
        kinds = {kind: .2*statistics.fmean(row['bounds_j'][kind] for row in repeats)
                 + .8*statistics.fmean(row['bounds_j'][kind] for row in quads)
                 for kind in e.BOUND_KINDS}
        token_ratio = (.2*math.fsum(r)/sum(row['tokens']['output'] for row in repeats)
                       + .8*math.fsum(row['energy_j'] for row in quads)
                       / sum(row['tokens']['output'] for row in quads))
        for value, pooled in [(mean, statistics.fmean(row['energy_j'] for row in rows)),
                              (token_ratio, math.fsum(row['energy_j'] for row in rows)
                               / sum(row['tokens']['output'] for row in rows)),
                              *((kinds[kind], statistics.fmean(row['bounds_j'][kind] for row in rows))
                                for kind in e.BOUND_KINDS)]:
            self.assertGreater(abs(value-pooled), 1e-6)
        estimate = e.estimate_reported_cell(rows, c[3])
        value = project(c)
        self.assertAlmostEqual(estimate.mean_j, mean, delta=1e-12)
        self.assertAlmostEqual(value['mean_j'], mean, delta=1e-12)
        self.assertEqual(estimate.df, 7)
        self.assertEqual(value['interval']['df'], 7)
        for half in (estimate.h_j, value['interval']['h_j']):
            self.assertAlmostEqual(half, e.T975[7]*math.sqrt(variance), delta=1e-12)
        for kind in e.BOUND_KINDS:
            self.assertAlmostEqual(estimate.kind_averages_j[kind], kinds[kind], delta=1e-12)
            self.assertAlmostEqual(value['interval']['kind_averages_j'][kind], kinds[kind], delta=1e-12)
        self.assertAlmostEqual(estimate.per_token['j_per_token'], token_ratio, delta=1e-12)
        self.assertAlmostEqual(value['per_token']['j_per_token'], token_ratio, delta=1e-12)

    def assert_code(self, code, fn):
        with self.assertRaises(e.PaperReportedEnergyRefusal) as cm: fn()
        self.assertEqual(cm.exception.code, 'paper_reported_energy_'+code)

    def check_formula(self, c):
        value = project(c)
        rows, k = c[1], c[3]
        nr, nb = len(k.kept_repeat_ordinals), len(k.kept_quad_ordinals)
        r = [R[n-1] for n in k.kept_repeat_ordinals]
        b = [B[(q[0]-11)//4] for q in k.kept_quad_ordinals]
        variance = .2**2*statistics.stdev(r)**2/nr + .8**2*statistics.stdev(b)**2/nb
        self.assertAlmostEqual(value['mean_j'], .2*statistics.fmean(r)+.8*statistics.fmean(b), places=13)
        self.assertEqual(value['interval']['df'], min(nr,nb)-1)
        self.assertAlmostEqual(value['interval']['h_j'], e.T975[min(nr,nb)-1]*math.sqrt(variance), places=13)
        return value

    def test_T1_full_and_removed_examples(self):
        for c, m, h, lo, hi in [(case(),10.16,.108332,9.991668,10.328332),
            (case((6,),(5,9)),10.133333,.115189,9.958144,10.308523)]:
            v=self.check_formula(c)
            for actual,expected in [(v['mean_j'],m),(v['interval']['h_j'],h),(v['lower_j'],lo),(v['upper_j'],hi)]:
                self.assertAlmostEqual(actual,expected,places=6)
            self.assertAlmostEqual(v['per_token']['j_per_token'],v['mean_j']/512,places=14)

    def test_T2_named_removed_repeat(self):
        v=self.check_formula(case((6,)))
        self.assertAlmostEqual(v['mean_j'],10.153333,places=6)
        self.assertGreater(abs(v['mean_j']-10.157143),.003)
        self.assertAlmostEqual(v['interval']['h_j'],.110057,places=6)

    def test_T3_smaller_df_and_not_plain_41_mean(self):
        v=self.check_formula(case((6,),(5,9)))
        self.assertAlmostEqual(v['mean_j'],10.133333,places=6)
        self.assertGreater(abs(v['mean_j']-10.129268),.004)
        self.assertGreater(abs(v['interval']['h_j']-.112334),.002)

    def test_T4_five_repeats(self):
        v=self.check_formula(case((6,7,8,9,10)))
        self.assertAlmostEqual(v['interval']['h_j'],.131327,places=6)

    def test_T5_unequal_bounds(self):
        c=case((6,8,9),(4,5,7,8,9)); rows=c[1]
        for row in rows:
            i=row['member']['ordinal']
            row['bounds_j']={kind:(i+j)/100 for j,kind in enumerate(e.BOUND_KINDS)}
        c[2]['attribution_floor_j']=max(r['bounds_j'][e.BOUND_KINDS[0]] for r in rows)
        v=self.check_formula(c)
        self.assertAlmostEqual(v['mean_j'],10.100571,places=6)
        self.assertAlmostEqual(v['interval']['h_j'],.210165,places=6)
        for kind in e.BOUND_KINDS:
            values=[r['bounds_j'][kind] for r in rows]
            self.assertEqual(v['interval']['kind_averages_j'][kind], .2*statistics.fmean(values[:7])+.8*statistics.fmean(values[7:]))
            self.assertNotEqual(v['interval']['kind_averages_j'][kind],statistics.fmean(values))

    def test_T6_quantile_literals(self):
        nine={9:2.262157163,8:2.306004135,7:2.364624252,6:2.446911851,5:2.570581836,4:2.776445105}
        three={9:2.262,8:2.306,7:2.365,6:2.447,5:2.571,4:2.776,3:3.182,2:4.303,1:12.706}
        self.assertEqual(set(e.T975),set(range(1,10)))
        for df,t in e.T975.items():
            if df in nine:self.assertEqual(round(t,9),nine[df])
            self.assertEqual(round(t,3),three[df])
            self.assertTrue(math.isclose(t,student_t_quantile(.975,df),rel_tol=1e-12))

    def test_T7_attribution_is_not_composed(self):
        c=case((6,)); rows=c[1]
        for i,r in enumerate(rows):r['bounds_j'][e.BOUND_KINDS[0]]=1.95+.41*i/(len(rows)-1)
        c[2]['attribution_floor_j']=.046*50+.002*30
        v=project(c)
        self.assertFalse(v['attribution_floor_composed'])
        self.assertEqual(v['attribution_floor'],{'value_j':2.36,'minimum_j':1.95,'attained_by':rows[-1]['member']['bundle_id']})
        self.assertAlmostEqual(v['upper_j']-v['mean_j']-v['interval']['h_j'],v['interval']['B_j'])
        rows[-2]['bounds_j'][e.BOUND_KINDS[0]]=2.36
        tied=project(c)
        self.assertEqual(tied['attribution_floor']['attained_by'],rows[-2]['member']['bundle_id'])

    def test_T8_full_shared_values_equal(self):
        c=case(); old=e._project_cell(*c[:3]); new=project(c)
        def shared(a,b):
            for key,value in a.items():
                if isinstance(value,dict):shared(value,b[key])
                else:self.assertEqual(value,b[key],key)
        shared(old,new)

    def test_T9_stratified_ratios_of_totals(self):
        c=case((6,),(5,9)); rows=c[1]
        for r in rows:r['tokens']['output']=100+r['member']['ordinal']*7
        v=project(c); es=[r['energy_j'] for r in rows]; ts=[r['tokens']['output'] for r in rows]
        expected=.2*(math.fsum(es[:9])/sum(ts[:9]))+.8*(math.fsum(es[9:])/sum(ts[9:]))
        self.assertEqual(v['per_token']['j_per_token'],expected)
        self.assertNotEqual(expected,math.fsum(es)/sum(ts))
        self.assertNotEqual(expected,statistics.fmean(x/y for x,y in zip(es,ts)))
        self.assertEqual(v['per_token']['strata']['repeat']['observed_token_sum'],sum(ts[:9]))

    def test_R1_wrong_attribution_binding(self):
        c=case((6,));c[2]['attribution_floor_j']+=.001
        self.assert_code('binding_mismatch',lambda:project(c))

    def test_R2_minimum_and_sensitivity(self):
        c=case((),(5,6,7,8,9,10))
        self.assert_code('kept_units_below_minimum',lambda:e.estimate_reported_cell(c[1],c[3]))
        v=e.estimate_reported_cell(c[1],c[3],minimum=None)
        self.assertTrue(v.below_minimum);self.assertEqual(v.df,3)
        self.assertEqual(v.h_j,e.T975[3]*math.sqrt(v.variance))
        c=case((),tuple(range(2,11)))
        self.assert_code('kept_units_below_minimum',lambda:e.estimate_reported_cell(c[1],c[3],minimum=None))
        self.assert_code('request_invalid',lambda:e.estimate_reported_cell(case()[1],case()[3],minimum=4))

    def test_R3_exact_member_census(self):
        for changed in ('quad_three','removed_repeat','missing_repeat','duplicate'):
            c=case((6,)); rows=c[1]
            if changed=='removed_repeat':rows.insert(5,case()[1][5])
            elif changed=='duplicate':rows[1]=deepcopy(rows[0])
            else:rows.pop(10 if changed=='quad_three' else 0)
            with self.subTest(changed=changed):
                self.assert_code('member_count_invalid',lambda:e.estimate_reported_cell(rows,c[3]))
        c=case();bad=replace(c[3],removed_repeat_ordinals=(1,))
        self.assert_code('request_invalid',lambda:e.estimate_reported_cell(c[1],bad))

    def test_R4_bound_missing_only_on_kept_member(self):
        c=case((6,)); clean=project(c)
        removed=case()[1][5];del removed['bounds_j'][e.BOUND_KINDS[1]]
        self.assertEqual(clean,project(c))
        del c[1][0]['bounds_j'][e.BOUND_KINDS[1]]
        self.assert_code('schema_invalid',lambda:project(c))

    def test_R5_denominator_refuses_only_sibling(self):
        c=case((6,));clean=project(c);c[1][0]['tokens']['output']=0;v=project(c)
        self.assertEqual(v['mean_j'],clean['mean_j']);self.assertIsNone(v['per_token']['j_per_token'])
        self.assertEqual(v['per_token']['status'],'refused')


class KeptRowSchemaTests(unittest.TestCase):
    def test_missing_row_key_and_wrong_member_use_historical_codes(self):
        for defect,code in (("missing_key","schema_invalid"),("wrong_member","record_identity_mismatch")):
            c=case((6,))
            if defect=="missing_key":del c[1][0]["model"]
            else:c[1][0]["member"]["bundle_id"]="counterfactual-other-bundle"
            with self.subTest(defect=defect),self.assertRaises(e.PaperReportedEnergyRefusal) as cm:project(c)
            self.assertEqual(cm.exception.code,"paper_reported_energy_"+code)
