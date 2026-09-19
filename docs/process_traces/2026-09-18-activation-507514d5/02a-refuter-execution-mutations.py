import importlib.util, pathlib, sys, unittest
root = pathlib.Path(__file__).parent
repo = pathlib.Path.cwd()
sys.path.insert(0, str(repo))
import scripts
name = sys.argv[1]
spec = importlib.util.spec_from_file_location("scripts.sample_quiet_predicate_evidence", root/(name+".py"))
module = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = module
setattr(scripts,"sample_quiet_predicate_evidence",module)
spec.loader.exec_module(module)
suite=unittest.defaultTestLoader.loadTestsFromName("tests.test_sample_quiet_predicate_evidence")
result=unittest.TextTestRunner(verbosity=2).run(suite)
print("MUTATION",name,"run",result.testsRun,"failures",len(result.failures),"errors",len(result.errors))
sys.exit(not result.wasSuccessful())
