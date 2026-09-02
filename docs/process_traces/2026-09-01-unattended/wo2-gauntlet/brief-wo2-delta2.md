ORIGIN: claude-code lead (magistrate)
HOP: 1 (do not call Claude by any route — never run `claude -p` yourself)
GENRE: review
WRITE_SCOPE: []

# Delta re-audit — night driver fix round 2 (`cdf58895` over `8510e6dc`)

Checkout: `/Users/edr/code/JouleWise-wt-night-driver` (branch
`feat/2026-09-01-night-driver`, head `cdf58895`). The fix is ONE commit:
`git show cdf58895 --stat` (8 files, +1465/-329). Write NOTHING in the tree;
`TMPDIR` = a subdirectory you create under
`/private/tmp/claude-501/-Users-edr-code-JouleWise/540125d5-d8ee-49d1-8e6e-17050e77212d/scratchpad/`.
Run only `python3 -m unittest tests.test_run_night tests.test_gen_g2_phase_d
tests.test_night_gate` (in the worktree and against TMPDIR copies). NEVER
spawn a real chain, a real `claude`, `launchctl`, or `git push`. Avoid the
substring `t3` in anything you create.

Authority: `docs/process_traces/2026-09-01-unattended/MAGISTRATE-RULING-UNATTENDED-STAGE1.md`
(R-2..R-8, §8). The fix brief (every ruled cure, B-A..B-F, S-a..S-f) is at
`.../scratchpad/run-wo2-fix2.md`; the seat's report at
`.../scratchpad/out/127-sol-wo2-fix2.md`. Fix rounds introduce defects —
audit the DELTA. The seat admits its "fails pre-fix" column was REASONED, not
executed. You execute it.

1. **Pre-fix kill check (mandatory, mechanical).** Build a TMPDIR copy of the
   pre-fix tree: `git archive 8510e6dc | tar -x -C $TMPDIR/prefix`. Then
   copy ONLY the three NEW test files from `cdf58895` over it and run the
   suite there. Every regression test the seat names in its table (24 names)
   must FAIL or ERROR on the pre-fix tree and PASS on `cdf58895`. Table:
   test name → pre-fix result → post-fix result. A named test that passes
   pre-fix is a blocker (the cure is unproven); note that some tests will
   error on import of names that do not exist pre-fix — that counts as a
   kill only if the test body would also fail on the old behaviour (say
   which kind each is).
2. **Cure-vs-brief match.** For each of B-A..B-F and S-a..S-f: does the code
   at the seat's cited file:line implement the brief's words? Specifically
   verify by reading + a TMPDIR probe where cheap:
   - B-A: `sys.path.insert(0, REPO_ROOT)` precedes the `joulewise` import;
     subprocess `--help` with `env={"PATH": "/usr/bin:/bin:/usr/sbin:/sbin"}`,
     `cwd="/"` exits 0; installer refuses exit 2 when `command -v claude` is
     empty (run the installer with `PATH` lacking claude in TMPDIR); courier
     `Popen` has `cwd=REPO_ROOT`; `courier.json` shape; second push;
     `EXIT_COURIER_FAILED` distinct from every other exit code.
   - B-B: every record opened `O_CREAT|O_EXCL|O_WRONLY`; the rerun path
     writes only `rerun-<epoch>.refusal.json`, spawns nothing (assert no
     `Popen`/`subprocess.run` call in the test), and exits non-zero.
   - B-C: `validate_refusal` exact key set; every refusal path validates;
     documents FAIL `night_gate.validate_receipt`.
   - B-D: unproven termination → `chain.unkilled`, `night_chain_alive`, no
     courier; dead-man reap via `os.killpg(pgid, 0)` → `chain.exited` with
     `reaped_by: dead-man`; `chain.started` has pid/pgid/epoch_s.
   - B-E: `{}` / non-JSON / missing → `night_plan_malformed`, courier
     attempted, non-zero.
   - B-F: REHEARSAL_STUB under `run`: census hits recorded, stub NOT killed,
     verdict `REHEARSAL_ONLY`, courier attempted; gate doc → `receipt.json`.
     DIAGNOSTIC with a hit still aborts.
   - S-a: constant 300 and the test computes it from `cold_start.json`.
   - S-b: predicate literally `t0 + window_max_s + COURIER_DEADLINE_S <
     dead-man epoch`; four `Popen`, sleeps exactly (60, 180, 600);
     `courier.lock` O_EXCL, removed on exit; dead-man `night_courier_running`
     only with a live pid; run-path hands off at the dead-man epoch.
   - S-c: equality against the FULL reconstruction; an appended line fails.
   - S-d: `start_new_session=True` asserted; `chain.exited` before push
     (call order); `CENSUS_INTERVAL_S == 30`; clone/push argv exact;
     `killpg(pgid, SIGTERM)`.
   - S-e: installer exit 3 on `chain.started` without `chain.exited`;
     bootstrap both or roll back the first.
   - S-f: `_night_date` local time; `_CODES` raises on a non-`night_`
     member; dead-man durable record before courier; fsync on the markers;
     distinct log stems.
3. **New defects in the delta.** Read `scripts/run_night.py` end to end
   (it is the file that runs unattended at 02:00 with nobody watching). For
   each of: an exception path that can skip the courier AND skip the durable
   record; a code path that can leave `courier.lock` behind after a crash so
   the dead-man refuses forever; a `Popen` whose stdout/stderr pipe can fill
   and block; a `time.sleep` inside the overrun-guarded loop that sleeps past
   the dead-man epoch; a refusal document whose `reason` is not in the
   registry — state FOUND (file:line, input) or NOT FOUND.
4. **Mutation probes (TMPDIR copies of `cdf58895`, never the tree):**
   (a) change `O_EXCL` to plain `O_CREAT` on `result.json`; (b) make
   `_terminate_process_group` return `True` unconditionally; (c) change the
   overrun predicate `<` to `<=`; (d) drop the second push; (e) set
   `COURIER_DEADLINE_S = 600`. Report the failing test name per mutant or
   SURVIVED.
5. Suite counts in the worktree: expected `Ran 84 tests … OK`.

## Report

Envelope first (fenced ```json, `claude-codex-report/v1`, genre `review`).
Verdict MERGE-READY / FIX-ROUND. Then the 24-row kill table, the cure-match
table (item → match / MISMATCH with file:line), §3 findings, the five mutant
results, exact commands. Under 120 lines after the envelope.
