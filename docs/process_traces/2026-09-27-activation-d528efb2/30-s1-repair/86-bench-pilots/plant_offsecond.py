"""Plant: the test's ID is taken off the second list; print the loader's reasons on failure."""
import sys, unittest
sys.path.insert(0, ".")
import tests.bfgs_fixtures as f
from joulewise.analysis_engine import inputs
f.PARITY_SECOND_FORM_TEST_IDS = frozenset()
orig = inputs.load_analysis_inputs if hasattr(inputs, "load_analysis_inputs") else None
unittest.main(module=None, argv=["unittest", sys.argv[1]])
