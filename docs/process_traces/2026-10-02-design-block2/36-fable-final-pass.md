FINAL PASS: MERGE

# Cold Fable 5.1 final pass: PR #458, G2-a night integration on 25G83 (lane G2A-NIGHT-25G83-01)

Head `d5b28bb859a5d9227b470c19029f7c1cfb8f1652`, base `b317866d04b4b2af1eaf4522df6563d87e8bafe3`.
One foreground session, no subagent, no background task. Interpreter
`/Users/edr/code/JouleWise/.venv/bin/python -B`. Scratch: `/tmp/g2a-fable-final/`.

## Contamination disclosure

- I did not open `RUN_STATE.md`, `TASK_QUEUE.md`, any `CLAUDE*.md`, `AGENTS.md`, or any memory or
  skill file.
- The session harness injected three things into my context before the charge, without my asking:
  the global `~/.claude/CLAUDE.md`, this worktree's `CLAUDE.md`, and the `MEMORY.md` index (one
  line per loop memory: checkpoint headlines, directive titles, model-routing notes). So this seat
  is not fully cold. I used none of it as evidence. Every finding below rests on the diff, the
  lane documents the charge named, files on disk, or a command I ran.
- Lane documents read: the block-2 registration, `31-sol-review.md`, `33-findings-disposition.md`.
  I did not read `03`, `04`, `12`, `21`, `22` (not needed to answer the question; time went to
  execution instead).
- I read (did not write) four real night plans under `/Users/edr/night-custody/` to learn which
  registration real Revision 6 windows carry. I ran no git command in the canonical repository.
- Scratch-only actions: two `git archive | tar -x` extracts of head and base into scratch (no
  `.git` inside), a stub `git` and a stub Python on a scratch `PATH`, and mutated copies of files
  in the scratch head extract. Nothing in this worktree changed except this file.

## Executed checks

| # | Command (abbreviated; cwd is this worktree unless stated) | Result |
|---|---|---|
| 1 | `git diff --name-only base head -- ` the four estimator files, `scripts/validate_powermetrics_fiducial.py`, `scripts/run_campaign.py`, `scripts/night_chains` | 0 paths. All untouched. |
| 2 | `-m unittest tests.test_gen_g2a_window` | 11 tests, OK |
| 3 | `-m unittest tests.test_harvest_g2a_window` | 30 tests, OK |
| 4 | `-m unittest tests.test_gen_g2_phase_d` | 10 tests, OK |
| 5 | `-m unittest tests.test_generate_g2a_probe_inputs` | 28 tests, OK |
| 6 | `-m unittest tests.test_summarize_g2a_prefill_probe`, `tests.test_select_g2a_prefill_length`, `tests.test_night_gate` | OK, 8 OK, 104 OK |
| 7 | `scripts/gen_g2_phase_d.py --check` | `PASS generated Phase D matches pinned runbook bytes`, exit 0 |
| 8 | `-m unittest tests.test_run_night` in the scratch head extract and the scratch base extract | 257 tests at head, 255 at base. 12 errors at each, the same 12 test ids (diff of ids is empty). All 12 are `git` calls failing because the extract has no `.git`. Every admission test (OFF receipt, clean dwell, start manifest, budget, generic) passed at both. |
| 9 | The same 12 ids re-run in this worktree (has git) | 4 pass, 8 fail. All 8 fail at one setup assertion, `test interpreter must load the battery fixture in child Pythons`, before any installer code runs. This is the environment condition the Sol review recorded as base-matched; I could not re-check base here (no checkout allowed). These 8 therefore gave no evidence either way. |
| 10 | `-m unittest tests.test_run_campaign.G2aLowCountCampaignTests` (real mock capture, reducer, strict validator, campaign with `max_failures=1`) | 1 test, OK |
| 11 | `-m unittest tests.test_custody_mode_inventory` | 7 tests, OK |
| 12 | `gen_g2_phase_d.py --emit-chain` into scratch, then `/bin/zsh -n`, then sidecar compare | exit 0; syntax OK; sidecar digest equals the chain's sha256 |
| 13 | Emitted chain run with `NIGHT_RESERVATION_ARGV_ONLY=1`, then with both flags, against a scratch tree, with a full inventory (path, size, mtime, mode, sha256) before and after | exit 0 both times; inventory identical; stub Python never invoked; the two outputs byte-identical; 36 NUL-terminated words ending `--verify-only`, no `--execute` |
| 14 | Emitted chain run with `NIGHT_VERIFY_ONLY=1` alone (reservation replaced by a recording stub) | exit 0; exactly one call, to the reservation script, with `--verify-only` and without `--execute`; inventory identical; no `runs/` directory created |
| 15 | Independent screen derivation: `_derive_preflight_systematic_screen_s()` versus the emitted chain's literals | acceptance file sha256 is `f949f511…b3660`; `acceptance_id` is `d079_calibration_acceptance_v2_n24_25g83_r2`; the chain has 2 `PRE_CAL_FIDUCIAL_MAX_S` literals and both equal the derived value exactly (string and decimal) |
| 16 | Scratch mutant: old literal put back in the runbook; `--check` | `FAIL acceptance-derived screen drift`, exit 1 |
| 17 | Scratch mutant: old literal put back in the runsheet (all 4 places); `--check` | `FAIL generated Phase D drift`, exit 1 |
| 18 | Emit a chain from that stale runsheet | The chain still carries the live value in both places and the old value nowhere. Restored; `--check` exit 0. |
| 19 | 22 harvester mutants in the scratch head extract, each run against `tests.test_harvest_g2a_window` (baseline there: 30 OK) | 14 went red, 8 stayed green. See finding F1. |
| 20 | 16 probes of the unmutated harvester for the guards behind the 8 green mutants and for the SELECT conditions (`/tmp/g2a-fable-final/probe_harvest.py`) | All pass. Details under question 5. |
| 21 | 9 driver mutants in the scratch head extract against 13 focused admission tests (baseline green) | All 9 went red. |
| 22 | `gen_g2_phase_d.py --new-g2a-window` end to end into scratch, window 19980 s, plan staged outside the night root | exit 0; v2 plan, `DIAGNOSTIC_NO_PACK`, D-166 registration path; schedule gives stand-down t0 − 480, latest chain start t0 + 2732, window end t0 + 19980, harvest open t0 + 20280; chain passes `zsh -n`; sidecar verifies. A 18147 s window refuses; existing outputs refuse. Nothing was created under `/Users/edr/night-custody/measurement/`. |
| 23 | Read `registration_path` and its sha256 from the real plans of Revision 6 windows C1 (two) and C2 | All three carry `configs/calibration/preregistration_d079_epoch_25g83_rev1.md`, sha256 `d0034003…7b78`, which is the driver's Revision 6 discriminant. The tracked file at head has the same sha256. |
| 24 | Static check: stdout `print` calls reachable from the harvester's in-process callees | selector: none to stdout; summarizer: none to stdout; `cli.validate_bundle` call graph: none; `calibration_bracketing`: none; `calibration_ledger`: all to stderr |

NOT EXECUTED:

- `tests.test_night_agent_install` (about 11 minutes; the Sol review ran it green at `8a8635a7`,
  and `joulewise/night_agent_install.py` did not change after that commit; I checked the later
  diff: 6 files, none of them the installer).
- `scripts/run_night.py preflight` on the authored plan (it runs machine probes; I did not audit
  which).
- The harvester's real seams on real data: `generate_g2a_probe_inputs.py check --at-reservation`
  on a real ledger, the real ledger replay, the real bracket decision, and strict validation of a
  real G2-a member. No G2-a window exists yet. The lane's tests and my probes replace these four
  with fixtures.
- Any live capture, model load, launchd install, or network-time command.
- The whole test suite.

## Answers to the seven questions

**1. Revision 6 admission and budget: unchanged.** The driver now asks one question first: is the
plan's registration file byte-identical (by sha256) to the sealed Revision 6 registration? When
yes, the span stays the fixed constant (600 + 11 × 600 + 480 = 7680 s), the prior-session manifest
is still read before the OFF command, both manifest evidence entries are still written, the
session id still comes from the chain's `SESSION_ID` literal, and the record keeps the Revision 6
schema. In scratch I mutated four of those one at a time (manifest read before OFF, manifest
entries, span, session id: R4, R5, R6, R9) and the discriminant itself in both directions (R1,
R2); every mutant went red (check 21). The real C1 and C2 plans carry that registration (check 23). The admission tests give the
same results at base and head (check 8).

**2. G2-a start conditions: enforced, and a clean window is not refused.** A non-Revision-6
calibration chain takes the same path as Revision 6 minus the manifest: OFF receipt, clean dwell
run during the settle, the 600 s test on both clocks and same boot, then the night gate, then the
start record. A chain with no admission record cannot be claimed (`run_night.py:3543`). A mutant
that skipped OFF and dwell for the generic case went red (R7). The start deadline comes from the
chain's `NIGHT_PROGRAMMED_SPAN_S` literal; a missing literal refuses before OFF. With the
registered window (19980 s) and span (17248 s) the runway is 2732 s, which covers the dwell's
2700 s cap (check 22).

**3. Screen in the G2-a chain: correct.** Checks 15 to 18. The generator refreshes the literal from
the live acceptance on every render, so even a stale source document cannot put an old screen in
an emitted chain, and `--check` fails on a stale literal in either source.

**4. Inspection is non-mutating.** Checks 13 and 14, plus the lane's installer render-only and
probe-binding tests (check 2). In the emitted chain the argv-only and verify-only branches sit at
lines 116 to 122; the first `mkdir` is line 123. The only commands before the branches are
variable exports, a read-only `git rev-parse`, and a `shasum` of the frozen plan.

**5. SELECT cannot be reached by an incomplete or unauthenticated window, or by count.** A member
is valid on three tests only: strict validation clean, status `succeeded`, clock anchor `bounded`.
None reads the count. Executed on the unmutated code (check 20): a nonzero exit, a missing exit
record, an open session, a missing session, a failed bracket with no reason codes, and a
non-succeeded small member each give RECOVER with no selection; an altered registration, a chain
that differs from its sidecar, a plan outside the night root, a ledger refusal reason, a session
bound to another plan, an inventory for another window, and a source file changed during the
harvest each give REFUSED, the last four with zero ledger commands issued. Harvest before
`window end + 300 s`, without delivery, or with the chain group alive refuses before any archive
(lane test, mutants H8 and H11 red).

**6. Low-count members stay valid and do not stop the campaign.** Check 10 runs the real campaign
code: two members with a prefill overlap below 3 both end `succeeded`, strict-valid, campaign log
`ok, ok`, exit 0 with `max_failures=1`. In the harvester a count of 2 with a bounded anchor stays
valid (lane test; mutant H21, which made validity depend on the count, went red). The clock
anchor status is computed from the capture's clock stamps and power records only
(`joulewise/uncertainty_evidence.py:1415`), so it cannot vary with the prefill count. The strict
validator has no count rule.

**7. No measured value on stdout.** The harvester prints the verdict, the number of valid members
out of the roster, and paths with sha256 digests. My probe matched every stdout line of a SELECT
run against that shape; the lane's own stdout test caught a mutant that printed the summary (H16);
the in-process callees print nothing to stdout (check 24). Exception text, which could carry
measured data, goes only into `harvest.json`.

## Findings

No blocker and no major finding.

| # | Severity | File:line | Claim | Evidence |
|---|---|---|---|---|
| F1 | minor | `tests/test_harvest_g2a_window.py` (whole file); guards at `scripts/harvest_g2a_window.py:100, 108, 137, 146, 152, 166, 223, 239` | Eight harvester guards are correct at head but no lane test pins them: member status `succeeded`; nonzero or missing chain exit gives RECOVER; registration digest; chain-versus-sidecar digest; ledger refusal reasons; session bound to this plan and runs root; inventory window identity; source unchanged before the pin advance. A later edit could remove any of them with the suite still green. The chain-exit one is a registered SELECT condition (registration §7). | Check 19: mutants H3, H4, H9, H10, H14, H15, H18, H22 left 30/30 green. Check 20: probes show each guard works on the unmutated code. The probe file can be lifted into the test module as is. |
| F2 | minor | `tests/test_harvest_g2a_window.py:77-85` | The harvest tests replace frozen-input authentication, the ledger replay, strict validation and the bracket decision with fixtures, so the real call signatures and real-data behaviour of those four seams are first exercised by the first real harvest. A fault there produces REFUSED or RECOVER, never SELECT, because SELECT needs every one of them to return a pass. Already accepted in the disposition (Sol F3); restated because it is the largest untested surface. | Read of the fixture; NOT EXECUTED on real data (none exists). |
| F3 | minor | `scripts/run_night.py:3078-3093`; `scripts/gen_derivation_night.py:703` | A derivation-chain window registered under D-166 went through the Revision 6 path at base (admitted when it had a start manifest); at head it refuses before OFF because its chain has no `NIGHT_PROGRAMMED_SPAN_S`. This fails closed and does not touch real Revision 6 windows, but the derivation generator's example plan still shows the D-166 registration with the derivation chain, so that documented example now describes a plan the driver refuses. | Check 23: the pre-seal plan `d079-epoch-25g83-derivation-w2-20260927` carries D-166 and its chain has no span literal; C1 and C2 carry the Revision 6 registration. Lane test `test_generic_missing_span_refuses_before_OFF` passes (check 8). |
| F4 | nit | `tests/fixtures/custody_read_replay_allowlist.json:76, 83` | The two new allowlist rows record lines 127 and 153; the replay calls are at lines 144 and 175 after the last commit. The test keys on call ordinal, so it passes. | Check 11; `grep -n read_replay scripts/harvest_g2a_window.py`. |
| F5 | nit | `scripts/run_night.py:3136-3145` | For Revision 6 the manifest evidence entries are now hashed after the other five instead of before, so when several evidence files are missing the joined refusal text lists them in a different order than at base. The admit-or-refuse outcome and the record's keys (sorted on write) are the same. | Read of the diff; the Revision 6 record tests pass at head (check 8). |
| F6 | nit | `scripts/harvest_g2a_window.py:223` | `exit_code != 0` treats JSON `false` as zero. The driver writes integers. | By reading only; the string `"0"` case was executed and gives RECOVER (check 20). |
| F7 | nit | `scripts/harvest_g2a_window.py:241-252` | If the harvest fails after the pin advance has executed, a re-run likely cannot authenticate the frozen ledger prefix against the moved pin and stays REFUSED until handled by hand. Fail-closed. | By reading only; NOT EXECUTED. |

## Summary

No defect of kinds (1) to (7) was found: the Revision 6 path is unchanged, the G2-a window keeps all physical start conditions, the screen equals the live 25G83 acceptance derivation, inspection writes nothing, and the harvest cannot SELECT an incomplete or unauthenticated window or judge members by count.
The one thing worth fixing soon is test coverage: eight harvest guards work but are unpinned (F1), and the harvest's four real seams have only ever run against fixtures (F2).
Not run here: the long installer suite, driver preflight, and anything live; eight installer tests in the driver module could not run in this environment.
