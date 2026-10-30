import json, sys, os
root = sys.argv[1]; sys.path.insert(0, root); os.chdir(root)
import tests.test_bytes_stream_test as t
t.ReaderTests.setUpClass()
res = t.ReaderTests.result
rows = t.ReaderTests.records[0]['harvest']['idle']['pre']['rails']
out = {b: [res['boundaries'][b][k] for k in ('delta', 'halfwidth', 'alpha', 'gamma_c', 'gamma_d', 'r')] for b in ('rails', 'gpu', 'dc', 'rest')}
out['share'] = res['share']; out['printed'] = res['printed']['contrasts']
out['rails_min_power'] = min(r['power_w'] for r in rows)
out['rails_pre_mean_se'] = [res['calls'][0]['idle']['rails'][k] for k in ('pre_w', 'post_w', 'se_w')]
print(json.dumps(out))
