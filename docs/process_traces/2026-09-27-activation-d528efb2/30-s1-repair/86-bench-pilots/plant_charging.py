"""Plant: every bundle the test module produces (and every reference pair) carries a charging pair."""
import importlib, sys, unittest
sys.path.insert(0, ".")
import tests.bfgs_fixtures as f
T = sys.argv[1]
mod = importlib.import_module(T.rsplit(".", 2)[0])
orig = mod.produce_strict_bundle
def planted(*a, **k):
    b = orig(*a, **k)
    f.write_charging_pair(b)
    return b
mod.produce_strict_bundle = planted
if hasattr(mod, "write_passing_pair"):
    mod.write_passing_pair = f.write_charging_pair
unittest.main(module=None, argv=["unittest", T])
