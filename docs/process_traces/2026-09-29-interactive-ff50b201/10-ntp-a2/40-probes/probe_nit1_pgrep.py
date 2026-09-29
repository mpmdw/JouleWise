import sys, json, os, subprocess, tempfile, time
import os as _os
CAND = _os.environ['CAND']
sys.path.insert(0, CAND)
from pathlib import Path
from scripts import run_night as d
SCR = Path('/private/tmp/claude-501/-Users-edr-code-JouleWise/ff50b201-b458-48cc-8d86-bb1b4bb19e19/scratchpad/n1delta3/tmp')
me = os.getpgid(0)
print('== real pgrep (no mocks) ==')
for argv in (['/usr/bin/pgrep','-lf','-g','999999','.'], ['/usr/bin/pgrep','-lf','-g','999998,999999','.'],
             ['/usr/bin/pgrep','-lf','-g',f'999999,{me}','.'], ['/usr/bin/pgrep','-lf','-g',str(me),'.']):
    r = subprocess.run(argv, capture_output=True, text=True)
    print(' '.join(argv[1:]), '-> exit', r.returncode, 'lines', len([l for l in r.stdout.splitlines() if l.strip()]), 'stderr', r.stderr.strip()[:60])
print('_group_census(999999) ->', d._group_census(999999, 1))
print('_group_census_batch([999998,999999]) ->', d._group_census_batch([999998, 999999], 1))
print('_group_census_batch([999999, me]) ->', {k: v[0] for k, v in d._group_census_batch([999999, me], 1).items()})

print('\n== NIT-1 real proof, real census + sweep ==')
with tempfile.TemporaryDirectory(dir=SCR) as td:
    root = Path(td); mroot = root/'mroot'; mroot.mkdir(); night = root/'night'; night.mkdir()
    sleeper = mroot/'cg_sleeper.py'
    for life, n_groups in ((2.0, 2), (0.5, 2), (2.0, 1), (2.0, 0), (3.5, 0), (0.0, 2)):
        sleeper.write_text(f'import time\ntime.sleep({life})\n')
        (night/'evidence_processes.jsonl').write_text(''.join(json.dumps({'pgid': g})+'\n' for g in range(999000, 999000+n_groups)))
        marker = {'measurement_root': str(mroot), 'custody_root': str(root), 'chain_path': str(root/'chain.zsh'),
                  'measurement_root_resolved': str(mroot.resolve()), 'custody_root_resolved': str(root.resolve()),
                  'chain_path_resolved': str((root/'chain.zsh').resolve())}
        child = subprocess.Popen([sys.executable, '-B', str(sleeper)], start_new_session=True,
                                 stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        if life == 0.0:
            child.wait()
        t0 = time.monotonic()
        proved, ev = d._prove_capture_absent(marker, 999999, night)
        dt = time.monotonic() - t0
        alive = child.poll() is None
        m = ev.get('matches')
        print(f'life={life}s groups={n_groups} -> proved={proved} check={ev.get("check")} passes={ev.get("passes")} '
              f'took={dt:.2f}s child_alive_at_return={alive} match_pid_is_child={bool(m) and m[0]["pid"]==child.pid}')
        try: child.kill()
        except ProcessLookupError: pass
        child.wait()
print('leftover sleepers:', subprocess.run(['/usr/bin/pgrep','-f','cg_sleeper.py'], capture_output=True, text=True).stdout.strip() or 'none')
print('PROBE2_COMPLETE')
