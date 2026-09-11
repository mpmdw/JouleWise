# Gate ledger row 10 — third FINAL-HEAD FRESH-EYES pass
Lane: ACCEPTANCE-EPOCH-25G83-01
Worktree: /Users/edr/code/JouleWise-wt-epoch-integration (branch feat/2026-09-10-epoch-integration)
HEAD verified: fa7dd55dd57b2be6d4cd4aa3cb117e0d5686c619 (working tree clean, `git status --porcelain` empty)
Mode: strictly read-only — no edits, no cuts, no git state changes; canonical /Users/edr/code/JouleWise untouched.

## VERDICT: CLEAN

---

## (1) Test-only and confined to the one file? YES

```
$ git diff f2a027c1..HEAD --stat
 tests/test_gen_derivation_night.py | 7 ++++++-
 1 file changed, 6 insertions(+), 1 deletion(-)
```

Full diff (the whole delta, nothing elided):

```diff
diff --git a/tests/test_gen_derivation_night.py b/tests/test_gen_derivation_night.py
index 25ff4b3b..ee1903d2 100644
--- a/tests/test_gen_derivation_night.py
+++ b/tests/test_gen_derivation_night.py
@@ -19,6 +19,8 @@ import shutil
 import subprocess
 import sys
 import tempfile
+
+from tests.git_fixture import init_git_fixture
 import unittest
 
 
@@ -116,7 +118,10 @@ class WrapperFixture:
         self.fake_python.write_text(FAKE_PYTHON)
         self.fake_python.chmod(0o755)
         self.calls_path = venv / "calls.jsonl"
-        _git(self.measurement_root, "init", "-q")
+        # The shared helper disables Git's detached maintenance writers, which
+        # a temp-dir cleanup would otherwise race; the maintenance guard in
+        # tests/test_git_fixture_maintenance.py refuses a direct `git init`.
+        init_git_fixture(self.measurement_root, "-q")
         _git(self.measurement_root, "add", "-A")
         _git(
             self.measurement_root,
```

One file, under `tests/`, one import + one call-site swap + three comment lines. No
production path, no fixture data, no config, no docs touched.

## (2) Behaviour reproduction and commit compatibility? YES

`tests/git_fixture.py` (read at HEAD):

- `GIT_MAINTENANCE_CONTROLS = (("maintenance.auto","false"), ("gc.auto","0"),
  ("maintenance.autoDetach","false"), ("gc.autoDetach","false"))`
- `init_git_fixture(repository, *init_arguments)` runs
  `git -C <repository> init <init_arguments...>` with `check=True`, then four
  `git -C <repository> config --local <key> <value>` calls, each `check=True`.

Equivalence: the previous line was `_git(self.measurement_root, "init", "-q")`, i.e.
`git -C <measurement_root> init -q`. The new call `init_git_fixture(self.measurement_root, "-q")`
issues exactly `git -C <measurement_root> init -q` — same binary, same `-C` target,
same `-q` argument, same fail-loud semantics — and then adds only the four
maintenance-control `--local` config writes. Strict superset: prior behaviour plus
the detached-writer suppression. Nothing about refs, default branch, worktree layout,
or the returned repository shape changes; `-q` still suppresses the init hint.

Commit compatibility: the helper writes ONLY the four maintenance keys. It sets no
`user.email`/`user.name`, so it cannot collide with identity. The subsequent
`_git(self.measurement_root, "-c", "user.email=seat@example.invalid", "-c",
"user.name=seat", "commit", "-q", "-m", "fixture")` supplies identity as one-shot
`-c` overrides on the command line, which take precedence over any repo config in
any case. `self.head = _git(..., "rev-parse", "HEAD")` on the next line would raise
(via `check=True`) if the commit had not landed; it does not. The later
`_git(clone, ... "commit" ...)` / `reset --hard self.fixture.head` path at lines
859–862 exercises the same repository again and also passes.

Executed proof — `tests.test_git_fixture_maintenance` (includes a live
`init_git_fixture` + `git config --local --get` readback of all four keys):

```
$ python3 -m unittest tests.test_git_fixture_maintenance -v   # tail
test_established_local_helpers_retain_the_exact_tuple ... ok
test_every_test_module_routes_git_initialization_through_shared_helper ... ok
test_guard_flags_direct_init_in_nested_support_module ... ok
test_nested_git_fixture_does_not_inherit_top_level_exemption ... ok
test_shared_helper_installs_the_exact_four_key_tuple ... ok

----------------------------------------------------------------------
Ran 5 tests in 7.771s

OK
RC=0
```

Executed proof — `tests.test_gen_derivation_night` (the changed module; its
`WrapperFixture.__init__` init+add+commit path runs in every test):

```
$ python3 -m unittest tests.test_gen_derivation_night   # tail
........................................
----------------------------------------------------------------------
Ran 40 tests in 17.169s

OK
RC=0
```

40/40 pass, no errors, no ResourceWarnings, no stray output.

## (3) Any other lane test module that would trip the same guard? NO

Lane test surface:

```
$ git diff origin/main...HEAD --name-only -- tests
tests/fixtures/custody_read_replay_allowlist.json
tests/fixtures/epoch_bootstrap/__init__.py
tests/fixtures/epoch_bootstrap/build.py
tests/test_arm_readiness_evidence_author.py
tests/test_authentication_io.py
tests/test_calibration_bracketing.py
tests/test_calibration_exits.py
tests/test_calibration_ledger.py
tests/test_calibration_ledger_custody.py
tests/test_calibration_writer_crash_matrix.py
tests/test_gen_derivation_night.py
tests/test_issue_calibration_acceptance_generation.py
tests/test_validate_powermetrics_fiducial_derivation_only.py
```

Grep for `"init"` / `git init` / `init_git` across exactly those files:

- Already routed through the shared helper: `test_calibration_bracketing.py:970`,
  `test_calibration_ledger.py:146`, `test_calibration_writer_crash_matrix.py:354`,
  `test_validate_powermetrics_fiducial_derivation_only.py:255`,
  `tests/fixtures/epoch_bootstrap/build.py:137` — each `init_git_fixture(<repo>, "-q")`
  with the matching `from tests.git_fixture import init_git_fixture`.
- `tests/fixtures/epoch_bootstrap/__init__.py`, `test_arm_readiness_evidence_author.py`,
  `test_authentication_io.py`, `test_calibration_ledger_custody.py`,
  `test_issue_calibration_acceptance_generation.py`: zero `git init` sites.
- Two direct sites remain, both in `tests/test_calibration_exits.py`, and both are
  covered by the guard's `ESTABLISHED_LOCAL_HELPERS` exemption, which is not a
  blanket pass: the exemption only applies when the enclosing scope matches, the
  scope contains exactly one init call, and the same function iterates
  `GIT_MAINTENANCE_CONTROLS` with `config` + `--local` (`_uses_local_hygiene`).
  Verified at HEAD:
  - `2146: self._git(sandbox.repo, "init", "-q")` in
    `CalibrationExitReliabilityTests._configure_fixture_repo`, followed at 2149 by
    `for key, value in GIT_MAINTENANCE_CONTROLS: self._git(sandbox.repo, "config", "--local", key, value)`.
  - `3650: subprocess.run(["git", "init", "-q"], cwd=self.repo, check=True)` in
    `PublicGovernedExitWitnessTests.setUp`, followed at 3661 by the same
    `GIT_MAINTENANCE_CONTROLS` / `config --local` loop.
  The module's own `GIT_MAINTENANCE_CONTROLS` at line 86 is pinned to the canonical
  four-key tuple by `test_established_local_helpers_retain_the_exact_tuple`, which
  passes.

Guard coverage confirmed at HEAD: `_git_init_violations` walks `TESTS_ROOT.rglob("*.py")`
— all of `tests/`, not just the lane diff — and
`test_every_test_module_routes_git_initialization_through_shared_helper` asserts the
violation set is empty. It passes at fa7dd55d (see the run above), so no module
anywhere in `tests/` trips the guard, lane or otherwise.

## Notes (nits, not findings)

- The new import sits between `import tempfile` and `import unittest`, splitting the
  stdlib block with a first-party import. Cosmetic only: the repository has no
  `[tool.ruff]` section in `pyproject.toml` and no ruff/flake8/isort step in
  `.github/workflows/`, so nothing enforces import ordering and nothing can fail on it.

## Read-only attestation

Commands executed were `git rev-parse`, `git status --porcelain`, `git branch --show-current`,
`git diff` (×3), `cat`/`sed`/`grep`/`ls` reads, and two `python3 -m unittest` module runs.
No writes to the worktree, no `git` state-changing command, no other worktree touched.
Only this report under /tmp was written.
