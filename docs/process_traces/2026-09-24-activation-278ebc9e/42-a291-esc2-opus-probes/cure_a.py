import inspect, runpy, sys
from joulewise import scored_packer as sp
src=inspect.getsource(sp._structure)
old='live_count = sum(not b["superseded"] and not any(t["model"] == model and t["item_id"] == item and t["block_id"] == b["block_id"] for t in terminal) and live_counts[b["block_id"]] == 1 for b in live_blocks)'
assert old in src
new='live_count = sum(not b["superseded"] and not all(any(t["model"] == model and t["item_id"] == x for t in terminal) for x in b["items"]) and live_counts[b["block_id"]] == 1 for b in live_blocks)'
exec(compile(src.replace(old,new),'cure_a','exec'), sp.__dict__)
sys.argv=['x',sys.argv[1]]
runpy.run_path('/tmp/278ebc9e/esc2-opus/seal_gap.py', run_name='__main__')
