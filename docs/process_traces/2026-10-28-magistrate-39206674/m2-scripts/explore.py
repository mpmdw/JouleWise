import sys, json, subprocess
D=sys.argv[1]
rec=[json.loads(l) for l in subprocess.run(['zstd','-dc',D+'/rich_telemetry.jsonl.zst'],capture_output=True).stdout.decode().splitlines()]
ev=[json.loads(l) for l in open(D+'/events.jsonl')]
m=json.load(open(D+'/metadata.json'))
ca=m['uncertainty_evidence']['clock_anchor']
print('first_sample_end', ca['first_sample_end_point_epoch_s'], 'samp_start', ca['clock_stamps']['sampling_started'])
for e in ev:
    if e['phase'] in ('decode','idle_baseline','prefill','tokenize') or 'monotonic_ns' in e['metadata']:
        print(e['phase'], e['event_type'], e['timestamp_s'], e['metadata'].get('monotonic_ns'))
print([ (r['index'], r['timestamp_s'], r['elapsed_ns']) for r in rec[:3]], rec[-1]['timestamp_s'], rec[-1]['index'])
import collections
print(collections.Counter(round(r['elapsed_ns']/1e6) for r in rec).most_common(5))
r=rec[800]
print('gpu freq', r['gpu']['freq_hz'], [ (s['freq'],round(s['used_ratio'],3)) for s in r['gpu']['dvfm_states']], r['gpu']['active_freq_mhz_weighted'], r['gpu']['idle_ratio'])
for c in r['clusters']:
    print(c['name'], c['freq_hz'], c['idle_ratio'], [(s['freq'],round(s['used_ratio'],3)) for s in c['dvfm_states']])
