# 21 — A294 / A295 contract lens (Opus 5.5, independent, read-only)

Candidate: branch `feat/2026-09-24-a294-t0-clean-tree`, head `5ef72338`, base
`bd80d169`; commits `b79174e7` (A294) and `5ef72338` (A295). Diff: 4 files,
+193/−10 (`joulewise/night_gate.py`, `tests/test_night_gate.py`,
`tests/test_run_night.py`, `tests/test_night_kinds.py`). Authorities read:
briefs 03 and 04; record 29 §R3; record 43 §Q2 F1; TASK_QUEUE rows A294/A295
and their kernel acceptance; NIGHT_HANDBACK; `joulewise/arm_retry.py`;
`docs/phase_2/derivation_night_runbook.md`; every non-trace use of
`night_plan_stale`.

**Verdict: no BLOCKER. Two SHOULD-FIX (both documentation that is now false or
incomplete), six NITs.** Line numbers are at `5ef72338`.

## Executed evidence (this lens, scratch `git archive 5ef72338` under /tmp)

- The seven new A294 tests (named): `Ran 7 tests … OK`.
- Mutation probes on the scratch `night_gate.py`, each restored (`cmp` clean
  afterwards):

| Mutant | Tests that fail |
|---|---|
| M1 delete the exit-code raise (:1278-1282) | exit_128 (the gate goes on to GO, so `refusal` is None) |
| M2 delete the dirty refusal (:1285-1296) | dirty_tracked, untracked_shadow, real_git |
| M3 refusal evidence `()` instead of `tuple(evidence)` | dirty_tracked |
| M4 detail omits the porcelain lines | dirty_tracked, untracked_shadow, real_git |
| M5 detail omits the measurement root | dirty_tracked |
| M6 do not record `measurement_checkout_porcelain` | dirty_tracked, clean, real_git |
| M7 run the status probe BEFORE the HEAD comparison | head_mismatch_skips (+3 others) |

- Modules outside the named acceptance that drive the gate with fakes:
  `tests.test_arm_census` (20 OK), `tests.test_night_plan_writer` (10 OK),
  `tests.test_quiet_admission` (12 OK). `test_launch_window` borrows
  `tests.test_run_night.ProbeSource`, which now answers the status argv.
  Scratch results for the remaining three modules:
  - `tests.test_quiet_predicate_campaign`: 157 OK.
  - `tests.test_launch_window`: 38 tests, 2 subtest failures in
    `test_evidence_author_cli_requires_absolute_existing_checkout`.
  - `tests.test_gen_evidence_night`: 10 tests, 1 error in
    `test_staged_installer_render_publication_probe_bindings_and_published_render`
    (`git rev-parse HEAD` exit 128).
  Those three failures reproduce IDENTICALLY in a `git archive bd80d169`
  scratch copy. The cause is the scratch copy having no `.git`, not this
  change, so no regression outside the named acceptance was found. The real
  confirmation is CI's full shards.

## (1) Brief clauses

**A294 (brief 03).**
- C1 met. The argv is exact, and `/usr/bin/git` matches the gate's other git
  probe (`night_gate.py:1388`). The probe runs only after the HEAD match
  (:1269, after the :1256 return). The result is appended to `evidence`
  (:1275).
- C2 met. The existing code is used, the detail names the root plus at most 5
  lines (:1292-1293), and the measured key holds a list of lines (:1277).
- C3 met. A non-zero exit raises `ProbeError`, and the raise and any exception
  both go to `_probe_refusal`, which gives `night_probe_error` (:1278-1284).
- C4 met. No manifest, `evidence_night`, arm check or `Probes` field changed.
- C5 met, with an approved scope addition. `tests/test_run_night.py:236-240`
  lies outside brief 03's WRITE_SCOPE. The magistrate approved it after the
  NEEDS_SCOPE round (05a; activation record 00 items 9 and 12), limited to fake
  answers. Only a fake answer was added.
- T1–T6 are present (`test_night_gate.py:833, 847, 856, 866, 884, 892`), plus
  one extra test for a raised exception (:875). T6 uses `init_git_fixture` and
  the production `scripts.run_night.make_probes` runner.
- Literal deviation, T3. Brief T3 says the receipt fields match bd80d169 "apart
  from the new measured key". Under C1, however, the status ProbeResult also
  joins `evidence`, so every LATER refusal (census, chain, registration, quiet)
  now carries one more evidence entry. The parity test hides this through
  `legacy_projection` (`test_night_gate.py:1484-1493`). The magistrate's own C1
  requires this, and it is harmless, but the seat report does not name it. See
  NIT-1.

**A295 (brief 04).**
- C1 met. The test at `test_night_kinds.py:396-403` commits a mutant with
  `window_max_s=8999` in a clone. It checks that `"window_max_s=9000,"` occurs
  exactly once; that string is the `quiet_predicate_evidence` row,
  `night_kinds.py:56`, and the calibration row is `None`. The test then does
  `update-ref main` in the bare remote and calls the real
  `evidence_night.prepare`. It asserts the exact record-43 string `python failed
  (2): REFUSED: window_max_s must equal the frozen protocol's 9000 s`. The
  refusal runs in a subprocess inside the prepared root
  (`evidence_night.py:59-66`), so it exercises the COMMITTED guard at
  `quiet_predicate_campaign.py:162`. The test reuses the module helpers:
  `_census_clean_tempdir`, the setUp courier stub, and `commit_fixture`, which
  is factored out of `ensure_base_source` with unchanged behaviour.
- C2: partial deviation (NIT-5). The companion (`:402`) runs the 9000-second
  row through `source = ROOT` directly. It does NOT go through the same
  clone-and-commit path as the mutant, so it is "the same helper", not "the
  same fixture". The exact-message assertion on the mutant already rules out a
  different cause, so vacuity is not a live risk.
- C3: seat evidence only (report 06: "Refused not raised" with the guard
  removed in a disposable clone). This lens did not re-execute it.

## (2) Reusing `night_plan_stale` for a dirty tree

Consumers found:
- `NIGHT_GATE_REASON_CODES` and `ORDER` (`night_gate.py:207,246`).
- `arm_retry.COLD_GATE_CODES` (`arm_retry.py:42`), which gives disposition
  `cold_gate`.
- The generated handback block (`docs/process/NIGHT_HANDBACK.md:92`) and the
  runbook copy (`derivation_night_runbook.md:1890`).
- `night_agent_install.py:1101` (plan age at install).
- `RUN_STATE.md:316` (history).

No consumer re-arms automatically. The code is not in
`ZERO_CAPTURE_MACHINE_REFUSALS` (`arm_retry.py:20-24`), so the watchdog grants
no early release and builds no successor. It keeps the full plan-span hold and
routes to cold-gate review. Mechanically, that is the right remedy class for a
tampered or dirty clone. Its precedence position (second, before the census)
also fits a checkout-identity fault.

The problem is the text, which is what an operator reads. **SHOULD-FIX-1:**
`arm_retry.py:42` and its two generated copies say "Plan age or pinned head
failed; not a stale notice." A reader who meets a dirty-clone refusal is sent
toward "author a fresh plan / re-pin the head". The right remedy is different:
find what wrote into the clone, then re-cut it (runbook §0.8: "stand the night
down and re-cut the clone (§0.2)"). The wrong remedy fails closed, because the
arm check's `checkout_ok` (`evidence_night.py:148-155`) refuses "dirty clone"
on the same clone. So this costs a wasted cycle and a misdirected diagnosis,
and it is not a safety hole. Suggested text: "Plan age, pinned head, or a
dirty/untracked measurement clone at t0 failed; for a dirty clone, find the
writer and re-cut the clone; not a stale notice." Brief C4 barred the seat from
editing refusal text, so this is a magistrate or bookkeeping edit. Make it in
`arm_retry.py` and regenerate both blocks; `tests/test_arm_retry.py:128-129`
pins the doc block to the dict.

## (3) Documents that must change in this PR

**SHOULD-FIX-2:** `docs/phase_2/derivation_night_runbook.md:770-781` states
that "the night gate binds the clone by its committed `HEAD` only … and nothing
more … Nothing anywhere excludes uncommitted edits … **This check is procedure,
not code**: no tool enforces it". After A294 that is false. The night gate now
refuses a dirty or untracked clone at t0 for every plan class, and the
evidence-night arm check already refused one at arm. The paragraph should keep
the manual §0.8 check, which still binds at arm time for the derivation path,
and should say that the t0 gate now enforces cleanliness as well. This is the
only place where the runbook explains the check. SHOULD-FIX-1 above is the
second doc edit. No other t0 description needs to change: NIGHT_HANDBACK has
no C5 prose, and the kernel and TASK_QUEUE rows are status bookkeeping for the
magistrate.

Integration note, no finding: the calibration and derivation paths keep their
ledger in `runs/`, and `*.egg-info/` is ignored (`.gitignore:48`), as are
`__pycache__/`, `.venv/` and `runs/`. So the known writers inside a clone
cannot trip the new check. The magistrate's check of five clean clones covered
QPE evidence nights only. No calibration or derivation clone has yet been
observed after a night under this check.

## (4) Test strength

Every new test can fail for its intended reason (see the mutation table). Two
exceptions:
- T5 (`:884`) passes at bd80d169 by construction, because the status probe
  never runs there. It guards ordering (M7), not presence. That is correct for
  its purpose.
- No test pins the at-most-5-lines cap. Changing `porcelain[:5]` to
  `porcelain` survives every test. See NIT-2.

None of the tests is tautological. `FakeProbeSource.run` sends the status argv
into `status_calls` instead of `run_calls` (`test_night_gate.py:149-153`). That
keeps the existing sequence assertions unchanged, as C5 required, but it also
means no existing `run_calls` assertion can see the new probe. T5 and T3 check
`status_calls` directly, which covers this.

## (5) A295 hermeticity and Linux CI

- The test is gated on `/bin/zsh`, like its two siblings (`:382, 386, 396`).
  Both ordinary CI jobs install zsh and assert `test -x /bin/zsh`
  (`.github/workflows/ci.yml:25-31, 161-168`), so the test RUNS on Linux CI.
  It is not silently skipped there.
- It needs ROOT to be a git repository: it clones `ROOT` (HEAD), so it tests
  committed code, as the pre-existing sibling already did. A scratch `git
  archive` copy cannot run it.
- The mutant commit is hermetic: fixed identity and dates,
  `commit.gpgsign=false`, `core.hooksPath=/dev/null`.
- The non-bare `git clone` (:415) and the `git add` inherit the user's global
  config (templates, autocrlf). This is minor, and the sibling's bare clone is
  already the precedent (NIT-4).
- Cost: roughly three full-repository copies per run (a 317 MB `.git`) with
  `--no-hardlinks`. The magistrate's bench replay still ran within budget
  (seat report: 19 tests in 85 s).
- Cleanup: `addCleanup(head_dir.cleanup)` runs after `tearDown` has already
  removed FIXTURE. `ignore_cleanup_errors=True` absorbs that, so it is
  harmless.

## (6) Overbuild

None of substance. The additions are:
- the exception test (:875), 9 lines;
- `legacy_projection`, which parity needs;
- the `commit_fixture` extraction, which is reuse.

The `test_run_night` fake matches the status argv for ANY root (NIT-3). That
is broader than needed, but the magistrate licensed it.

## NITs

- NIT-1 `night_gate.py:1275`: the status probe now appears in the refusal
  evidence of every later refusal. This is intended by C1 but was not reported
  as a T3 deviation. Record it in the PR body.
- NIT-2 `test_night_gate.py:833`: no test pins the 5-line cap. Add six
  porcelain lines and assert that the sixth is absent from the detail.
- NIT-3 `test_run_night.py:236-240`: the fake answers "clean" for any
  measurement root. Matching the plan's root would keep a future dirty-root
  test possible.
- NIT-4 `test_night_gate.py:903-906` (T6 commit) and `test_night_kinds.py:415`:
  both lack `commit.gpgsign=false` / `core.hooksPath=/dev/null` or rely on
  global config. On a machine with global signing, T6 would error. The
  module's own `commit_fixture` pattern is the cure.
- NIT-5 `test_night_kinds.py:402`: the C2 companion is not "the same fixture"
  (see above). Consider `window_max_s=9000` through the clone path with
  `--allow-empty`, or accept the difference with a note.
- NIT-6 `night_gate.py:1277, 1293`:
  - On a non-zero exit, the measured key records `[]`, which reads as "clean",
    even though the refusal is `night_probe_error`.
  - The detail renders a Python list repr.
  - The measured list is uncapped, so a massively dirty clone bloats the
    receipt. The census stdout is the precedent.
  All cosmetic.
