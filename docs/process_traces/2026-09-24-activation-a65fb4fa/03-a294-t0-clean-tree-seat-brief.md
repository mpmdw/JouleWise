ROLE: implementation seat for JouleWise lane A294 (T0-CLEAN-TREE-CHECK-01). Execution seat and design peer; the magistrate reviews. Do not call Claude or any other agent (bridge depth is one hop).

WRITE_SCOPE: ["joulewise/night_gate.py", "tests/test_night_gate.py"]

0. CONTEXT. Linked worktree /Users/edr/code/wt-a65fb4fa-a294, branch feat/2026-09-24-a294-t0-clean-tree at origin/main bd80d169. Do not commit. Fences: never launchctl, sudo, networksetup; never touch /Users/edr/night-custody or /Users/edr/JouleWise-measurement-*; never import or execute from /Users/edr/code/JouleWise (the canonical checkout). Authority: docs/process_traces/2026-09-23-activation-d8cc9c0a/29-a280-pra-opus-lens.md §R3 (read it first) and TASK_QUEUE.md row A294.

1. PROBLEM. The arm check (`evidence_night.checkout_ok`, evidence_night.py:148-155) refuses a measurement clone with tracked edits or untracked files. At t0 the gate in night_gate.py (about :1241-1261, check row C5) compares only `rev-parse HEAD` against `plan.measurement_head`, and the per-file byte comparison covers only the manifested files. A working-tree edit to an executing but unmanifested file (for example `corecaptured_loop.py`), or a shadowing untracked module, made between arm and t0 would go undetected.

2. CLAUSES (magistrate rulings; do not choose differently without an explicit dissent in your report):
   C1. Immediately after the existing HEAD comparison in the C5 block (only when HEAD matches), run through `probes.run` the argv `("/usr/bin/git", "-C", plan.measurement_root, "--no-optional-locks", "status", "--porcelain=v1", "--untracked-files=all")` (match the git path convention night_gate already uses for its other git probes; if it uses a different git path constant, use that constant and say so). Append the ProbeResult to `evidence` the way neighbouring probes do.
   C2. Non-empty stdout → refuse with the EXISTING code `night_plan_stale` (no new refusal code) and a detail that names the measurement root and says it has tracked edits or untracked files, including at most the first 5 porcelain lines. Record the porcelain result in `rows["C5"].measured` under a new key `measurement_checkout_porcelain` (list of lines, empty when clean).
   C3. Non-zero exit code, or the probe raising → the tree is uncheckable → refuse through the existing `_probe_refusal` / `night_probe_error` path (raise into it or construct identically; do not invent a new code).
   C4. Do NOT extend any manifest list (MANIFEST_PATHS or similar). Do not change evidence_night, the arm check, the Probes dataclass fields, or any refusal text other than the new detail.
   C5. Every existing test fake `run` in tests/test_night_gate.py that must now answer the new argv answers it with a clean result (exit 0, empty stdout) unless the test is about this check; keep existing assertions unchanged.

3. REGRESSIONS (named; each must fail at bd80d169 or when the new guard is deleted):
   T1 dirty tracked file (porcelain ` M joulewise/corecaptured_loop.py`) → `night_plan_stale`, detail names the root and the file, C5 measured carries the line.
   T2 untracked shadowing module (`?? joulewise/shadow.py`) → `night_plan_stale`.
   T3 clean tree → the gate proceeds exactly as before (same receipt fields as at bd80d169 apart from the new measured key).
   T4 git status exit 128 → `night_probe_error`.
   T5 ordering: a HEAD mismatch still refuses with the HEAD-mismatch detail, and the status probe is not run.
   T6 one test drives a REAL temporary git repository (use `tests.git_fixture.init_git_fixture`, never a bare `git init`; see tests/test_git_fixture_maintenance.py) through the production probe runner night_gate uses in production (find it: the default/production Probes constructor), edits an unmanifested tracked file after commit, and proves the refusal; then restores and proves a pass of this check.

4. ACCEPTANCE: named modules ONLY: `python3 -B -m unittest tests.test_night_gate tests.test_evidence_night tests.test_night_kinds tests.test_run_night tests.test_arm_retry tests.test_magistrate_watchdog tests.test_git_fixture_maintenance`. NEVER `unittest discover` or scripts/shard_tests.py. If a test fails only because this sandbox denies `ps` or another process list, say so by name; the magistrate re-runs it at the bench. `git diff bd80d169 --stat` lists only WRITE_SCOPE paths. End your turn only after the named acceptance has run; do not stop mid-flight.

5. EVIDENCE DEMANDED (markdown body): C1-C5 mapped to file:line; T1-T6 mapped to test names; the guard-deletion check (delete the new refusal, show which tests fail, restore); the test command and its result tail; "what the magistrate should double-check". Implementation-genre verdict keys only; JSON header under 8 KB.
