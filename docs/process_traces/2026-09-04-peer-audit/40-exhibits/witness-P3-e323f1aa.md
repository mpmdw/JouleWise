# P3 witness replay at e323f1aa5b9d1579f4a93b13b2665388cdeaa643

Source command: `docs/process_traces/2026-09-04-peer-audit/02-claim-spine.md:201-214`.
Re-executed from repository root on 2026-09-04 with exit status 0.

```sh
PYTHONDONTWRITEBYTECODE=1 python3 - <<'PY'
import os, subprocess, sys
cmd=[sys.executable,'scripts/render_results_fills.py','tests/fixtures/results_prose_render/synthetic_d_and_0_manifest.json']
r=subprocess.run(cmd,capture_output=True,text=True,env=os.environ)
print('renderer_exit_code=%d' % r.returncode)
print(r.stdout.splitlines()[0])
print('contains_fixture_label=%s' % ('synthetic' in r.stdout.lower() or 'fixture' in r.stdout.lower()))
print('contains_old_models=%s' % ('1.5B' in r.stdout and '7B' in r.stdout))
print('published_language=%s' % ('operative floor is published' in r.stdout))
PY
```

Complete tail:

```text
renderer_exit_code=0
## §7 Variant D — a token-generation cell publishes no floor
contains_fixture_label=False
contains_old_models=True
published_language=True
```
