# Record 31 — fix-forward after PR #372: the hosted Linux 3.11 shard has no `python3.13` (2026-09-20 09:50–10:00 PDT)

## §1 Defect (executed evidence)
Post-merge run 35522762217 on main `2b6cb947`: `test (3.11, 5)` FAILURE, fail-fast cancelled eight shards; 3.13 shards 3/4 and 3.11 shards 3/6 passed. Job 106109917369 log (`/tmp/magistrate-21752427/pm372-shard5.log` lines 1430–1660): 14 ERROR entries over 12 `tests.test_evidence_night.PrepareTests` methods (three are subTests of one method), every one `FileNotFoundError: [Errno 2] No such file or directory: 'python3.13'` raised from `joulewise/evidence_night.py:379 run(["python3.13", "--version"])` on the pre-clone path — round 2's C9 added the bench step-1 probe unconditionally; the hosted 3.13 runners have `python3.13`, the 3.11 runners do not; the PR matrix runs only 3.13, so the PR head was green and the post-merge matrix caught it (Ed's 09-16 ruling: fix forward).

## §2 Fix (branch `fix/2026-09-20-evidence-night-py311`, `8963dcf0` + `ab95e377`, diff gate by the magistrate)
The probe moves INTO `build_venv` (the real recipe: `python3.13 --version` → `python3.13 -m venv .venv` → the two constrained installs → exact-lock freeze) — offline tests inject a builder, so the prepare path never needs `python3.13` on the host; the recipe test asserts the probe as the builder's first call, and the prepare test asserts it ABSENT from the prepare path. First push (`8963dcf0`) broke those two assertions at the bench (the lead pushed before re-running the module — corrected within four minutes by `ab95e377`; lesson: run the module before every push, even for a three-line move).
Bench (both interpreters, module alone):
```
/opt/homebrew/bin/python3.11 -B -m unittest -q tests.test_evidence_night → Ran 23 tests in 66.559s (first attempt: FAILED 1+1) → after ab95e377: OK
/Users/edr/code/JouleWise/.venv/bin/python -B -m unittest -q tests.test_evidence_night → OK
```
Replay for row 9: the delta is one module + its test; the round-1 full replay (record 26 §2, 6,637 tests) covers the surrounding suite; module re-run alone on both interpreters above; hosted matrix on the PR head + post-merge.

## §3 Counter-review (rows 1/2/6/10) — Opus 5 subagent, read-only; verbatim
VERDICT: FIX-FIRST — one doc line; code and tests are correct.
R1. The fix is minimal and correctly placed. `joulewise/evidence_night.py:103` probes before `:104` creates the venv, so the real bench recipe's order (probe → venv → two installs → lock verify) is preserved; `absent(root/".venv")` at `:99` still precedes it. Only host binaries left on the prepare path are `git`, `/bin/zsh` (installer shebang `scripts/install_night_agent.sh:1`, plus `subprocess.run(['/bin/zsh','-n',…])` inside the `sealed_candidate` payload, `evidence_night.py:222`, executed by the CLONE's `.venv/bin/python` = the test interpreter) and that python itself. The installer's `/usr/bin/env python3` fallback (`install_night_agent.sh:47`) never fires — prepare always passes `--python` (`:449`); its MIN_PYTHON gate is (3,11), so 3.11 shards pass. zsh -n DOES execute on Linux CI (CI installs zsh and asserts `test -x /bin/zsh`, `ci.yml:161-168`); proof is pre-merge run 35521486599 `test (3.13, 5)`, which ran `MODULE START tests.test_evidence_night` and all 23 green on ubuntu-latest — that run also exercised the installer and sealed-candidate paths. (Post-merge `test (3.13, 5)` was CANCELLED by fail-fast, so cite the pre-merge run, not it.)
BLOCKER-lite: `docs/contracts/evidence_night_entry.md:44` still says step 1 is "Run `python3.13 --version`, clone the remote…". The probe is now in step 2 (build_venv). The contract is the ONE home for this recipe; update that sentence in the same push. Consequence worth one clause there: a missing python3.13 now surfaces after the clone, with the "clone" checkpoint recorded (resume-safe).
R2. Preserved. Builder literals still asserted, now indices 0–3 (`tests/test_evidence_night.py:101-104`); `fetch < ancestry` kept at `:340`. Both mutants killed under 3.11 (in-memory source mutation, worktree untouched): re-adding the probe before the clone → FAIL at `:337` `assertNotIn`; deleting it from build_venv → FAIL at `:101`. Nit: the test is still named `test_preclone_recipe_…` though no pre-clone recipe assertion remains.
Executed: `/opt/homebrew/bin/python3.11 -B -m unittest tests.test_evidence_night -v` → `Ran 23 tests in 64.410s` / `OK` (exit 0).
R3. Accurate except one number: commit 8963dcf0 says "errored 13 tests"; the failing shard log shows 14 ERROR entries over 12 distinct methods (3 are subTests of `test_sealed_candidate_checks_before_checkpoint`). Everything else — cause, run id 35522762217, shard, mechanism — checks out; ab95e377's message matches its diff exactly.

Disposition: the contract sentence and the test name corrected in the third commit; the count corrected in §1 above (the commit message of 8963dcf0 keeps its "13", noted here).

## §4 Terminal review (row 12) and hosted result (row 11)
(appended before merge)
