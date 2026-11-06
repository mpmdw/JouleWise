import importlib.util, pathlib, unittest

P=pathlib.Path(__file__).parents[2]/"scripts"/"align_v4_oc_sim.py"
S=importlib.util.spec_from_file_location("align_v4_oc_sim",P); M=importlib.util.module_from_spec(S); S.loader.exec_module(M)

class OCTests(unittest.TestCase):
 def test_seeded_report_is_deterministic(self):
  self.assertEqual(M.simulate(2000,17),M.simulate(2000,17))
 def test_binomial_closed_form(self):
  self.assertAlmostEqual(M.binomial_tail(2,.5,1),.75)
  self.assertAlmostEqual(M.extension_prob(.10,1,21),M.binomial_tail(22,.9,21))
 def test_conformal_rank_closed_form(self):
  self.assertEqual(M.conformal_rank_coverage(19,.05),.95)
  self.assertEqual(M.conformal_rank_coverage(9,.05),1.0)
 def test_proposal_meets_series_false_fail_cap(self):
  self.assertLessEqual(M.simulate(100,1)["series"]["fail"],.15)

if __name__ == "__main__": unittest.main()
