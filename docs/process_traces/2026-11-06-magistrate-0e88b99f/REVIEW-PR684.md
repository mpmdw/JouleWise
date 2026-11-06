# Executing review of PR #684 (R0 launcher keeps --python-bin unresolved)

Reviewer: Sonnet 5.5 subagent, independent of the author (magistrate 0e88b99f, Opus 5.5), read-only,
on commit 38ebcf4c6. Verdict: **ADMIT**, no blocker, major or minor findings.

What it ran:
- `python3.14 -B -m unittest tests.test_magistrate_desk_fence` (fresh TMPDIR): `Ran 35 tests in 26.575s` / `OK`.
- A real python3.13 venv: `v/bin/python` has `sys.prefix` = the venv; the `Path.resolve()` form is the
  Cellar `python3.13` with the base framework prefix (reproduces the R0 mlx failure); the patched
  `Path(os.path.abspath(p.expanduser()))` keeps `v/bin/python`. Relative input becomes absolute against
  cwd; `~` expands.
- Checked that nothing re-resolves the interpreter: `os.access` at `scripts/launch_align_r0.py:188`
  follows the link itself; `runner.json` and the plist carry the path verbatim (lines 201, 206, both
  asserted by the new test); `scripts/run_align_r0_launchagent.sh` uses `"$python_bin"` verbatim with no
  realpath/readlink; the watchdog never references the interpreter path.

Nit, rejected with reason: `os.path.abspath` collapses `..` lexically, so `link-dir/../python` could differ
from the OS's walk. No operator passes such a path for `--python-bin`; not worth a change.

Lead's own checks: counterfactual (launcher change reverted) makes the new test FAIL on its assertion;
the runner's QuietGuard (`joulewise/align/r0_host.py:94` in the measurement checkout) matches the
`align_r0_checks` script name in argv, not the interpreter path, so the unresolved path cannot defeat it.
