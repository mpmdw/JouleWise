"""Every E1-E19 and S1-S11 worked arithmetic acceptance case."""
import math
from types import SimpleNamespace
import unittest
from .support import recompute as r, R, B, D, CONTRAST, CORPUS, KINDS


class WorkedExamples(unittest.TestCase):
    def close(self, actual, expected, digits):
        self.assertAlmostEqual(actual, expected, delta=.5 * 10 ** -digits)

    def test_E1_overlap(self):
        self.assertAlmostEqual(r.overlap([(9.90,10.03,20.),(10.03,10.16,30.),(10.16,10.29,30.)],10.,10.25)[0],7.2,delta=1e-9)

    def example_envelope(self, off):
        records = [(9.95+i*.13, 9.95+(i+1)*.13, p) for i,p in enumerate([2]+[30]*7+[20,4])]
        return r.shift_envelope(records,10.015,off,.0457,.0003,.002)

    def test_E2_envelope(self):
        e = self.example_envelope(11.055)
        for key,value in (("point_j",28.730),("max_abs_delta_j",1.048),("lower_j",27.682),("upper_j",29.778)):
            self.assertAlmostEqual(e[key],value,delta=1e-9)

    def test_E3_crossing(self):
        e = self.example_envelope(11.)
        self.assertAlmostEqual(e["point_j"],27.630,delta=1e-9)
        self.assertAlmostEqual(e["max_abs_delta_j"],1.428,delta=1e-9)

    def test_E4_full_reported(self):
        e = r.reported_estimate(R,B,KINDS,R+[x for b in B for x in [b]*4])
        for actual, expected, digits in ((e["mean_j"],10.16,2),(e["interval"]["variance"],.0022933,7),
            (e["interval"]["h_j"],.10833,5),(e["lower_j"],9.9917,4),(e["upper_j"],10.3283,4),
            (e["mean_j"]/512,.019844,6)):
            self.close(actual,expected,digits)

    def test_E5_units_removed(self):
        e = r.reported_estimate(R[:5]+R[6:],[x for i,x in enumerate(B) if i not in (4,8)],KINDS)
        for actual,expected,digits in ((e["mean_j"],10.13333,5),(e["interval"]["s_r"],.18028,5),
            (e["interval"]["s_b"],.16690,5),(e["interval"]["variance"],.0023730,7),
            (e["interval"]["h_j"],.11519,5),(e["lower_j"],9.9581,4),(e["upper_j"],10.3085,4),
            (e["mean_j"]/512,.019792,6)):
            self.close(actual,expected,digits)
        self.assertEqual(e["interval"]["df"],7)

    def test_E6_repeat_only_removed(self):
        e = r.reported_estimate(R[:5]+R[6:],B,KINDS)
        self.assertEqual(e["interval"]["df"],8)
        for actual,expected in ((e["mean_j"],10.153333),(e["interval"]["h_j"],.110057),
                               (e["lower_j"],9.983277),(e["upper_j"],10.323390)):
            self.close(actual,expected,6)

    def test_E7_absolute_floor(self):
        f = r.floor_estimate(R,[.05]*10,"absolute")
        self.close(f["prediction_j"],.4745,4)
        self.close(f["operative_unguarded_floor_j"],.5730,4)
        self.assertEqual(f["guard"],1)

    def test_E8_reduced_absolute(self):
        f = r.floor_estimate(R[:5]+R[6:],[.05]*9,"absolute")
        for key,val in (("prediction_j",.4382),("operative_unguarded_floor_j",.5435),("guarded_floor_j",.5765)):
            self.close(f[key],val,4)

    def test_E9_comparative(self):
        f = r.floor_estimate(D,[.3]*10,"comparative")
        self.close(f["prediction_j"],.2692,4)
        self.close(f["operative_unguarded_floor_j"],1.0349,4)

    def test_E10_reduced_comparative(self):
        f = r.floor_estimate([v for i,v in enumerate(D) if i not in (4,8)],[.3]*8,"comparative")
        for key,val,digits in (("s_j",.09258,5),("prediction_j",.2822,4),
            ("operative_unguarded_floor_j",1.0896,4),("guarded_floor_j",1.2354,4)):
            self.close(f[key],val,digits)

    def test_E11_dominance(self):
        a = r.floor_estimate(R,[.05]*10,"absolute")["R"]
        c = r.floor_estimate(D,[.3]*10,"comparative")["R"]
        self.close(a,1.21,2); self.close(c,3.84,2)
        self.assertLess(a,2); self.assertGreaterEqual(c,2)

    def test_E12_contrast(self):
        d = CONTRAST[:3]+CONTRAST[4:]
        e = r.finish_contrast(r.contrast_stats(d,.05),.01,1.2)
        self.assertEqual(e["n"],9); self.assertEqual(e["t_star"],2.306)
        for key,val,digits in (("dbar_j",3.,9),("s_d_j",.19365,5),("se_j",.064550,6),("t_stat",46.4758,4)):
            self.close(e[key],val,digits)
        for pair,expected in ((e["metrology_interval_j"],[2.8511,3.1489]),(e["decision_interval_j"],[2.8011,3.1989])):
            for actual,val in zip(pair,expected): self.close(actual,val,4)
        self.assertAlmostEqual(e["p"],5.077e-11,delta=.0005e-11)
        self.assertAlmostEqual(max(abs(x["dbar_j"]-3.) for x in e["loo"]),.0375,delta=1e-9)
        self.assertEqual(e["outcome"],"direction_supported"); self.assertEqual(e["ceiling"],"L2")

    def test_E13_load_sensitivity(self):
        e = r.reported_estimate(R,[v for i,v in enumerate(B) if i not in (4,8)],KINDS)
        self.assertEqual((e["n_r"],e["n_b"]),(10,8))
        self.close(e["mean_j"],10.14,2); self.close(e["interval"]["h_j"],.11557,5)

    def test_E14_assist_cell(self):
        e = r.reported_estimate(R[:2]+R[3:],B[:6]+B[7:],KINDS)
        self.assertEqual((e["n_r"],e["n_b"]),(9,9)); self.close(e["mean_j"],10.16222,5)

    def test_E15_assist_contrast(self):
        e = r.contrast_stats([v for i,v in enumerate(CONTRAST) if i not in (2,3)])
        self.assertEqual(e["n"],8); self.assertEqual(e["t_star"],2.365)
        for key,val,digits in (("dbar_j",2.9625,4),("s_d_j",.16850,5),("se_j",.059574,6)):
            self.close(e[key],val,digits)
        for actual,val in zip(e["metrology_interval_j"],[2.8216,3.1034]): self.close(actual,val,4)

    def test_E16_neg8(self):
        for ns,ne,val in ((3,3,.5933),(3,2,.6383),(2,2,.6800)):
            e = r.neg8_bound(CORPUS,ns,ne)
            self.close(e["bound_j"],val,4); self.close(e["s_j"],.2353,4)
            self.assertEqual(e["t"],2.201)
        start = sum([100.02,99.91,99.95])/3
        spread,allowance = r.drift_allowance(start,100.20,sum([100.26,100.19])/2,r.neg8_bound(CORPUS,3,2)["bound_j"])
        self.close(allowance,.6383,4); self.close(allowance/2,.3192,4)

    def test_E17_neg8_spread(self):
        spread,allowance = r.drift_allowance(20.10,19.90,20.35,.40)
        self.assertAlmostEqual(spread,.45,delta=1e-9); self.assertAlmostEqual(allowance/2,.225,delta=1e-9)

    def test_E18_attribution(self):
        # Exercise the reporting layer, including ordinal first-on-tie attribution.
        bounds = [1.95,2.36,2.36,2.0,1.98]
        members = [SimpleNamespace(run_id=f"fixture-r{i:02}",energies={"decode":10.},
                   tokens={"decode":512},op={"decode":{"max_abs_delta_j":v}}) for i,v in enumerate(bounds,1)]
        repeats = [(m.run_id,[m]) for m in members]
        quads = [(f"fixture-b{i:02}",[SimpleNamespace(run_id=f"fixture-b{i:02}-{p}",energies={"decode":10.},
                  tokens={"decode":512},op={"decode":{"max_abs_delta_j":1.95}}) for p in r.POSITIONS]) for i in range(1,6)]
        w = SimpleNamespace(pack="ALPHA",exclusion_cells={},neg8={"allowance_j":.1})
        e = r.make_reported(w,"df-ph-decode-qwen3-1p7b",repeats,quads)
        self.assertEqual(e["attribution_floor"],{"value_j":2.36,"attained_by":"fixture-r02","minimum_j":1.95})

    def test_E19_quantiles(self):
        literals = [12.706204736174705,4.302652729749464,3.1824463052837095,2.7764451051977943,
                    2.5705818356363155,2.44691185114497,2.364624251592785,2.306004135204166,2.262157162798205]
        for df,expected in enumerate(literals,1):
            with self.subTest(df=df): self.assertAlmostEqual(r.student_quantile(df),expected,delta=1e-12)

    def test_S1_overlap(self):
        e,n = r.overlap([(0,.1,10),(.1,.2,50),(.2,.3,10)],.05,.25)
        self.assertAlmostEqual(e,6.,delta=1e-9); self.assertEqual(n,3)

    def test_S2_inside_record(self):
        e = r.shift_envelope([(-10,10,40)],0,1,.046,0,.002)
        for key,val in (("max_abs_delta_j",3.68),("lower_j",36.32),("upper_j",43.68)):
            self.assertAlmostEqual(e[key],val,delta=1e-9)

    def test_S3_minimum_reported(self):
        e = r.reported_estimate([1,2,3,4,5],[2,2.1,1.9,2,2],(.1,0,.2))
        for actual,expected in ((e["mean_j"],2.2),(e["interval"]["variance"],.02064),
                               (e["interval"]["h_j"],.3988815),(e["lower_j"],1.5011185),(e["upper_j"],2.8988815)):
            self.assertAlmostEqual(actual,expected,delta=5e-8)

    def test_S4_minimum_absolute(self):
        f = r.floor_estimate([1,2,3,4,5],[.5]*5,"absolute")
        for key,val in (("prediction_j",4.808173),("corner_widened_unguarded_floor_j",6.305860),
                        ("guarded_floor_j",9.458790),("R",1.311488)):
            self.close(f[key],val,6)
        self.assertEqual(f["guard"],1.5)

    def test_S5_minimum_comparative(self):
        f = r.floor_estimate([.1,-.1,.2,0,.3],[.2]*5,"comparative")
        for key,val in (("prediction_j",.580817),("corner_widened_unguarded_floor_j",1.249011),
                        ("guarded_floor_j",1.873517),("R",2.150437)):
            self.close(f[key],val,6)

    def test_S6_common_mode(self):
        f = r.floor_estimate([.1,-.1,.2,0,.3],[.2]*5,"comparative",[.15]*5,[.05]*5)
        self.close(f["common_mode_numerator_j"],.890586,6); self.close(f["R_cm"],1.533332,6)
        self.assertLess(f["R_cm"],f["R"])

    def test_S7_shared_width(self):
        members=[]
        for position in r.POSITIONS:
            power=10 if position.startswith("a") else 20
            records=[(-1,2,power)]
            members.append(SimpleNamespace(run_id="fixture-b01-"+position,records=records,
                edges={"prefill":(0,.5)},energies={"prefill":power*.5},
                residual={"prefill":r.shift_envelope(records,0,.5,0,.0003,.001)}))
        split=r.common_width(members,"prefill",.045)
        for key,val in (("shared_j",.9),("local_j",.018),("width_j",.918)):
            self.assertAlmostEqual(split[key],val,delta=1e-9)

    def test_S8_pvalue(self):
        e=r.contrast_stats([1,2,3,4,5])
        self.close(e["p"],.0132356,7); self.close(e["t_stat"],4.2426407,7)
        for actual,val in zip(e["metrology_interval_j"],[1.037072,4.962928]): self.close(actual,val,6)

    def test_S9_holm(self):
        for p,expected in (([.01,.04],[.02,.04]),([.03,.2],[.06,.2]),([.001,None],[.002,1.])):
            with self.subTest(p=p): self.assertEqual(r.holm(p),expected)

    def test_S10_outcome(self):
        cases=[(1.,[.4,1.6],0.,1.,"not_resolvable"),(3.,[.4,5.6],.5,1.,"not_resolvable"),
               (3.,[-.1,6.1],0.,1.,"unresolved")]
        for mean,met,D,floor,expected in cases:
            row={"n":5,"dbar_j":mean,"metrology_interval_j":met,"decision_interval_j":[met[0]-D,met[1]+D],"D_j":D}
            self.assertEqual(r.evaluate_outcome(row,floor,True),expected)
        e=r.finish_contrast(r.contrast_stats([-3,-3.1,-3.2,-2.9,-2.8],.05),.01,1.)
        self.assertEqual(e["outcome"],"direction_supported"); self.assertEqual(e["ceiling"],"L1")
        self.assertEqual(r.evaluate_outcome(r.contrast_stats([1,2,3,4]),1.,True),"not_estimable")

    def test_S11_magnitudes(self):
        pairs=[(10,10,20,22),(10,12,21,20),(11,10,22,23),(10,10,20,21),(12,11,24,22)]
        a=[(x+y)/2 for x,y,_,_ in pairs]; b=[(x+y)/2 for _,_,x,y in pairs]
        contrast=r.contrast_stats([y-x for x,y in zip(a,b)])
        e=r.descriptive_estimate(a,b,contrast,"decode")
        self.close(e["ratio"],2.028951,6)
        for actual,val in zip(e["ratio_interval"],[1.897151,2.169907]): self.close(actual,val,6)
        self.close(e["per_token_difference_j"],.021289,6)
        g=r.cross_window(a,{"mean_j":10.,"interval":{"h_j":.1}})
        self.close(g["G_j"],10.6,1); self.close(g["h_G_j"],.809466,6)
