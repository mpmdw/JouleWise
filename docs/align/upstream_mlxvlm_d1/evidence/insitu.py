import sys
from pathlib import Path
kit = Path("/Users/edr/code/CapstoneProject/jw-wt/port-qwen4-exp/docs/align/upstream_mlxvlm_d1/test_qwen4_exp_ragged_qsa.py").read_text()
func = kit[kit.index("@pytest.mark.parametrize"):].replace("@pytest.mark.parametrize", "@parametrize", 1)
target = Path(sys.argv[1])
s = target.read_text()
anchor = "def test_hashes_and_dependencies():"
assert anchor in s and "test_qwen4_exp_ragged_batch_matches_single_requests" not in s
s = s.replace(anchor, func + "\n\n" + anchor, 1)
target.write_text(s)
