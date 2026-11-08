W1 smoke delta5 — independent Sol review, 2026-11-08.

**Verdict: ADMIT.** No new plausible operator, host or functional failure found.
Reviewed `80bbfa2cd..0ad6f29f3`, excluding v4-r11 merge content: the substantive
smoke change is `c551fe9d2`, plus the final runbook pointer. Integration checks
ran at `0ad6f29f3`. Authority: the brief's CLI-only child-process ruling and
`W1-SMOKE-AGREEMENT.md` §10. M0/intake and orchestration were read; no active
stop card exists. The requested branch already existed, clean, at the candidate.
This explicit [AGENT] review supersedes queue selection; coordination is lead-owned.

The production child uses the clone's interpreter/script/cwd, smoke environment
and remaining budget. `pass_fds` preserves the anchor through exec alongside
the wrapper's separate pid-report mechanism. Temporary anchors close in
`finally`; normal runner ownership ends at teardown. The real CLI control
observes no parent fd leak. The child creates its numbered result exclusively
beneath the anchor. The parent's descriptor-based `safe_read` refuses links and
nonregular/multiple-link files, and closes its read handle.

`grouped_run` kills remaining group members and proves absence on success,
failure or timeout; unproven exit raises `TeardownFailure`, rather than claiming
a clean `BudgetExpired`. Real-process witnesses cover timeout descendants and
successful/nonzero leaders. TMPDIR is checked before and after the child.
Nonzero exit produces `PREPARE_CHILD_FAILED` and failed child/prepare rows;
`_sequence` returns 1 before any arm.

No runner patch of `subprocess.run`, defaults, TMPDIR or `tempfile.tempdir`
remains. The `h.measurement_view` reduction seam runs in the dedicated child
or synthetic seams. In-process production prepare refuses; unsupported
in-process `run()` warns and logs its entry.

All seven adaptations retain the original safety property under the ruling:

- Delta4-sol1 body exits: run/defaults/temp state survive every exit, including
  interrupts and SystemExit; run/defaults are unchanged inside prepare too.
- Delta4-sol1 options: exact remaining timeout, env/TMPDIR, cwd and inherited
  fd are asserted; expiry prevents launch. The child boundary replaces deleted
  wrapper cases; binary/exception controls remain.
- Delta4-sol2 body exits: the same restoration property, including loaded
  prepare/install defaults, with unchanged assertions after each exit.
- Delta4-sol2 setup interrupt: no abandoned mutation and the child-owned
  temporary anchor closes when launch is interrupted.
- Delta4-sol2 thread: an unrelated real command remains independent while
  prepare exhausts its own budget.
- Delta4-sol2 direct/default commands: real child commands outlive 1.5 seconds,
  but their whole group is gone promptly; both TMPDIR boundary checks occur.
- Delta3-sol2 capacity: real production `important_capacity` retains its own
  30-second probe timeout, while the outer child is bounded and proven gone.

Comparison with the original delta4 remote review branches and delta3-sol2 at
`80bbfa2cd` finds exactly those seven changed tests, none removed or added.
Executable ASTs outside those bodies/module docstrings are identical. No
skips/expected failures were introduced. The accepted production-write/TMPDIR
pathname residual is unchanged.

Verification used Python 3.13, sequentially, one module per process. The first
four commands were `TMPDIR=/private/tmp python3.13 -B -m unittest -v MODULE`:

| MODULE | Result | Seconds |
|---|---|---:|
| `tests.align.test_smoke_delta4_sol1` | 12 OK | 1.709 |
| `tests.align.test_smoke_delta4_sol2` | 11 OK | 3.462 |
| `tests.align.test_smoke_delta3_sol1` | 16 OK | 6.780 |
| `tests.align.test_smoke_delta3_sol2` | 15 OK | 178.185 |
| `tests.align.test_w1_smoke` (bootstrap below) | 26 OK | 21.345 |

Total: 80 tests, 211.481 seconds; no failures/errors/skips. Expected CLI-only
warnings appeared. The last module used
`TMPDIR=/private/tmp python3.13 -B -` with this bootstrap, so its older fixtures
never resolve configured external custody paths or inspect the real home:

```python
import os, tempfile, unittest
from pathlib import Path
from unittest import mock
from joulewise.align import w1_smoke as smoke
with tempfile.TemporaryDirectory(prefix='smoke-delta5-safe-') as temporary:
    root = Path(temporary)
    home = root / 'home'
    (home / 'Library/LaunchAgents').mkdir(parents=True)
    (root / 'host').mkdir()
    original = smoke.load_config
    def config(*args, **kwargs):
        return {**original(*args, **kwargs), 'production_roots': [str(root / 'custody')]}
    with mock.patch.object(smoke, 'load_config', side_effect=config), \
         mock.patch.object(Path, 'home', return_value=home), \
         mock.patch.dict(os.environ, {'JOULEWISE_HOST_STATE_DIR': str(root / 'host')}):
        unittest.main(module='tests.align.test_w1_smoke', argv=['unittest', '-v'])
```

`PYTHONPYCACHEPREFIX=/private/tmp/jw-smoke-delta5-sol-pycache python3.13 -B -m compileall -q joulewise tests`
and `git diff --check` passed. The full suite was omitted under the machine-load
restriction. All executable probes were offline and synthetic; no measurement
pipeline, model weights, live launchd operation or real restricted data was used.

Changed: this report only, one local documentation commit on
`align/2026-11-08-smoke-delta5-sol`; no fixes, coordination edits or push.
No peer/subagent used. Open questions: none requiring a ruling.
Unverified: Python 3.11, the live production prepare body (the CLI control
substitutes a synthetic body), native wall time, launchd teardown, real meter
restart and contender overlap. This admission does not satisfy those live gates.
No MLX code changed or ran; this delta adds no MLX-native test requirement.
Next exact step: the lead consumes this report, then performs the existing
native CLI smoke and parser qualification in `W1-SMOKE.md` from a clean,
agent-free MBP gap. Do not run that measurement while the analysis job is active.
