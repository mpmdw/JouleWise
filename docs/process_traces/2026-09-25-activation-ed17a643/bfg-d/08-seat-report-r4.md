# BFG-D round 4: implementation seat report (Opus 5.5)

Seat: Claude Opus 5.5 (`claude-opus-5-5`), one foreground session, worktree `JouleWise-wt-ed17a643-bfgd`, branch `feat/2026-09-25-bfg-d`. Start `1bf0ef76` (the round-4 brief on top of `ab431280`). The code end is `e5af8e59`; the end of the round is the commit that adds this file. No subagents, background tasks, watchers, launchctl, powermetrics, sudo, installer runs or model inference. Nothing was pushed.

The source I implemented is `06-harvest-final-obligations-v1.1-source.md` §4 (§4.1–§4.11). Where §4 gives a name, I used it verbatim. `joulewise/authentication_io.py` is reused and was not edited.

**Status: complete.**
- §4.10 items 1–7, 9 and 11 are implemented. Every test named in §4.10 exists and passes at the production call site §4.10 names.
- Item 8 is implemented in `NIGHT_HANDBACK.md`. One runbook row it implies is outside my scope; see NEEDS_SCOPE N-1.
- Item 10 is PR-body text for the lead; its wording is below.
- Every module the brief requires passes at the final code, and so does every other module I touched or found coupled.

## Commits (this round)

| Commit | Content |
|---|---|
| `5620bf32` | `battery_float`: the §4.1 custody rule, `CustodyFailure`, `NoRecord`, `VERDICT_SCHEMA`, `verdict_record`, `load_committed_verdict`, `compare_verdict`, `predates_battery_float`, and the item 1 tests (a)–(h). |
| `ef3e5876` | Issuer: the `battery-verdict` subcommand, the reworked §4.4 block (`_battery_computed_set`), the §4.5 dry run, the §4.6 registry pin, the item 6 fixture builder, and the item 2, 3 and 5 tests. Also the custody-read allowlist rows. |
| `e70144da` | §4.5: `report_window` and `derive_record` now require the record; their fixtures and tests are updated. |
| `ad159745` | Docs: A-R5b-1 in the decision log, runbook §2.2a with its §2.1 row and §2.3 sentence, and the handback's verdict-line template. |
| `e5af8e59` | Keeps the module-level imports of `battery_float` to the standard library only (finding F-10). |

## §4.10 → implementation → tests

Line numbers are at `e5af8e59`.

| Item | Implementation | Test (production call site) | Result |
|---|---|---|---|
| 1 `battery_float.py` | `CustodyFailure(RuntimeError)` `joulewise/battery_float.py:40` (`failures`, `detail`, `str` = `custody failure: <slot>/<artifact> expected <sha> observed <sha\|absent>; …`); `NoRecord(ValueError)` `:58`; `VERDICT_SCHEMA` `:32`; `validate_window` E0–E6 `:235-331` (raise at `:327`); `verdict_record` `:376`; `load_committed_verdict` `:408` (checks 1–4; `ingest_git_authentication_input` imported locally); `compare_verdict` `:478`. Supporting helpers: `verdict_relative_path` `:334`, `render_verdict` `:341`, `predates_battery_float` `:346`. | `tests/test_battery_float.py`: (a) `:260`; (b) `:273` and the re-asserted A10 at `:198`; (c) `:281`; (d) `:294`; (e) `:301`; (f) `:312`; (g) `:319`; (h) `CommittedVerdictTests` `:339` (honest `:391`, delete-and-re-add "3 commits, 2 adding" `:400`, modify-in-place "2 commits, 1 adding" `:409`, uncommitted edit `:416`, absent `:422`, wrong registration digest `:429`, altered evidence digest `:435`, `compare_verdict` `:442`, schema `:380`). | pass |
| 2 `battery-verdict` | `scripts/issue_calibration_acceptance_generation.py:1329` / `:1347`. Parser `:2177`; dispatch `:2311`. It takes exactly the six ruled flags, all required, and follows steps 1–8 in order. Every refusal prints `REFUSED: <reason>` and exits 3. On success it prints one line. It writes with `open(path, "xb")`. | `tests/test_issue_calibration_acceptance_generation.py` through `issuer.main`: (a)+(b) `:2393`; (c) `:2421`; (d)+(e) `:2430` (non-terminal, wrong digest, zero finalized slots, pre-A-R5b). | pass |
| 3 `_prepare_candidate` | Computed set `_battery_computed_set` `:1239` (registration ∪ A-7 owners ∪ S; exemption (i) is the pinned registry, exemption (ii) is `predates_battery_float`, never for registration sessions). Step 3 is at `:1529-1564`, with the three ruled refusal texts at `:1541`, `:1551`, `:1557`. The recorded status governs. The unchanged exact-set text and the bound follow (`:1589`). Notes: `battery_confounded_sessions[*].verdict_file_sha256/verdict_commit` and `battery_verdict_records` at `:1939`. | (a) M1 `:2456`; (b) E8 `:2479`; (c) P2-E1 `:2490`; (d) `:2499`; (e) `:2304` (now with a committed W1 record; still issues) and `:2514`; (f) N1 `:2529`; (g) `:2550`. | pass |
| 4 consumers | Dry run `:181-307`: prints `battery=<recomputed> recorded=<status\|absent>`, with the custody, missing-record and disagreement blockers. The epoch bound `_dry_run_epoch_bound` `:312` uses the same helper as the issuer. `report_window` `scripts/calibration_cadence_report.py:62-79`. `derive_record` `scripts/issue_epoch_continuation.py:86-107`, which raises `battery_float_custody_failure`, `_verdict_missing` or `_verdict_mismatch`. | Dry run `:2572`, `:2591`; the re-asserted tampered raw at `:2367`; `report_window` `:2598` (missing record, custody failure, `diagnostic_only` taken from the record); continuation `tests/test_epoch_continuation.py:274` (missing, custody failure) and `:254` (recorded non-pass). | pass |
| 5 registry pin | `DISPOSITION_REGISTRY_SHA256` `:469`. `_registered_dispositions` reads the file as bytes and refuses on its digest before parsing (`:1214`). | `tests/test_acc_25g83_rev5.py:343` (tracked sha256 equals the constant; 11 rows), `:348` (one appended row gives "digest mismatch"), `:359` (A4 route through `issuer.main`: appended registry → 3 `digest mismatch`; tracked registry → 3 on A-7 `W2-d01`). The same test adds a counterfactual: with the pin bypassed, a W2-only registry issues at exit 0 with n = 24, which is the ruling's A4 defect. | pass |
| 6 fixture builder | `tests/fixtures/epoch_bootstrap/build.py`: `verdict_records: bool = False` (`:163`), which writes and commits each session's record in the terminal-pin commit. Also `rerecord_verdict` `:278`, plus `add_session` `:225` and `write_verdict_record` `:246`. | used by items 2–5 | pass |
| 7 runbook | New §2.2a at `docs/phase_2/derivation_night_runbook.md:2519`: why the step exists, what a custody failure is, and steps (i)–(viii) as one command block. The §2.1 row is at `:2483`, the §2.3 sentence at `:2600`. The ARM-RETRY-POLICY block is unchanged. | `tests.test_docs_freshness` | pass |
| 8 notices | `docs/process/NIGHT_HANDBACK.md:179`, standing template text: the exact per-window line, which the harvest notice sends at the pin commit and the next arm notice and arm record repeat. The policy block is unchanged. The runbook §1.5 arm-record table is not updated (N-1). | — | done, apart from N-1 |
| 9 decision log | A-R5b-1 is appended verbatim from the §4.8 code block (extracted by program, byte-exact) at `docs/decision_log.md:12213`. A-R5b is not on this branch, so the entry goes at the end (F-8). | `tests.test_gen_state`, `tests.test_d078_reason_registry` | pass |
| 10 PR body | Text for the lead: the two BFG addendum §5.3 item 8 statements from round 3 (BFG-D does not close BATTERY-FLOAT-GATE-01; every transaction-pack campaign re-freezes `arm_readiness.sources` before any transaction-pack window arms), then: "A-R5b-1 is recorded in the decision log; the committed harvest verdict file is the window verdict; a custody failure refuses and never excludes; the disposition registry is digest-pinned." | — | for the lead |
| 11 pin regression | Unchanged from round 3. | `tests/test_validate_powermetrics_fiducial_derivation_only.py:242` (`SAMPLERS`, protocol v3, the `ESTIMATOR_CODE_PATHS` digests, chain digest) and `:324` (`manifest.artifacts` and `artifact_sha256` key sets) | pass |

## Expected-value and setup edits to existing tests

No pre-existing assertion was deleted or loosened. Each edit either moves an assertion to what §4 rules, or changes setup so that an unchanged assertion still reaches its code path.

1. **`tests/test_battery_float.py:198` (A10, ruled).**
   - Before: after `write_bytes(b"tampered")` on the pre raw file, `assertEqual(status, "battery_float_evidence_missing")`.
   - After: `assertRaisesRegex(CustodyFailure, r"s01/pre expected [0-9a-f]{64} observed")`.
   - The `post=None` assertion above it is unchanged (`evidence_missing`).
2. **`tests/test_issue_calibration_acceptance_generation.py:2367` (item 4, ruled).**
   - Before: `assertIn("W1: battery=confounded", lines)`.
   - After: `assertIn("W1: battery=confounded recorded=confounded", lines)`.
   - The tampered-raw half changes from `assertEqual(verdict["status"], "battery_float_evidence_missing")` to `assertRaisesRegex(CustodyFailure, r"d01/pre expected ")`.
3. **`tests/test_issue_calibration_acceptance_generation.py:1898` (template).**
   - Before: `lines[2] == f"{SESSION}: battery=pass"`.
   - After: `lines[2] == f"{SESSION}: battery=pass recorded=pass"`.
   - The fixture gains `verdict_records=True`. Every other index and pattern is unchanged.
4. **`tests/test_acc_25g83_rev5.py:84` (registry row grammar).** Both `invalid or duplicate` assertions are unchanged. They now run with `DISPOSITION_REGISTRY_SHA256` patched to the temporary copy's own digest, so the row grammar behind the pin is still exercised.
5. **`tests/test_acc_25g83_rev5.py`, unsealed/disposes test.**
   - The empty registry `[]` now also asserts `registry digest mismatch` (new).
   - The original `valid same-epoch observations outside` assertion is unchanged; it now runs under a patch pinning `[]`'s digest.
6. **`tests/test_epoch_continuation.py:876` (unanimity).**
   - The `identity_epoch_not_unanimous` assertion is unchanged, but it now runs on a non-Revision-5 epoch (`os_build` 25G99). On a 25G83/v3 session, no record can authenticate for mixed-epoch rows (§4.3 check 3), so the battery gate refuses first.
   - That case is added as a third subtest: `battery_float_verdict_missing: identity mismatch: identity_epoch`.
   - The `content_id` case is unchanged.
7. **Fixture setup only; no assertion changed.** These now pass `verdict_records=True` (with the sealed registration's digest where the test seals one):
   - the four `BatteryFloatRevisionFiveTests` class fixtures, `cls.wide`, and the aborted and template fixtures;
   - in `test_acc_25g83_rev5`: full-seal (the sealed text is now computed before the fixture), unsealed, futility/inset, and W3 (which also gets a record for its synthetic `derivation-night-3`, copied from night 2's record under its own id);
   - the cadence `setUpClass`;
   - the continuation `build()` default and its battery-gating test;
   - `tests/fixtures/epoch_continuation/build.py`.
   - The open-session case of item 2(d) asserts the reachable refusal (F-6).
8. **`tests/fixtures/custody_read_replay_allowlist.json`.** Insert-only: two rows, `_battery_verdict` (new) and `report_window` (a round-3 omission, F-9).

## Test tails (final code `e5af8e59`, foreground, each run to completion)

```
tests.test_battery_float                                  Ran 29 tests in 0.774s    OK
tests.test_issue_calibration_acceptance_generation        Ran 132 tests in 106.166s OK
tests.test_calibration_cadence_report                     Ran 6 tests in 0.629s     OK
tests.test_epoch_continuation                             Ran 66 tests in 52.759s   OK
tests.test_acc_25g83_rev5                                 Ran 12 tests in 15.092s   OK
tests.test_preregistration_chain_digest                   Ran 8 tests in 0.005s     OK
tests.test_validate_powermetrics_fiducial_derivation_only Ran 26 tests in 198.528s  OK
tests.test_night_gate                                     Ran 104 tests in 0.915s   OK
tests.test_evidence_night                                 Ran 159 tests in 257.400s OK
tests.test_docs_freshness                                 Ran 31 tests in 0.488s    OK
tests.test_gen_state                                      Ran 44 tests in 1.894s    OK
tests.test_custody_mode_inventory                         Ran 7 tests in 39.671s    OK
tests.test_validate_powermetrics_fiducial                 Ran 12 tests in 8.318s    OK
tests.test_write_derivation_night_inputs                  Ran 16 tests in 0.733s    OK
tests.test_epoch_equivalence_check                        Ran 26 tests in 10.146s   OK
```

- `tests.test_evidence_night` ran at `e5af8e59`. Every other module in the table ran at `e5af8e59` too. The last change was the import move, and I re-ran all of them after it.
- These modules read the decision log and also ran green, with the final docs text in place and before the import move: `tests.test_d078_reason_registry` (14), `tests.test_whole_window_selection` (57), `tests.test_schemas` (40, 1 skipped), `tests.test_claims_lint` (30) and `tests.test_quiet_guard` (87).
- Not run, left to the lead's discovery: `test_night_agent_install`, `test_install_night_agent`, `test_arm_readiness_evidence_t0`, `test_arm_retry`, `test_gen_evidence_night` and `test_evidence_arm_sequence`. Round 4 changed none of their code. The module-level imports of `battery_float` are standard-library only again (the only addition is `math`), which is the property F-10 shows those import paths need.
- No full discovery was run.

## Pin proof

```
$ git diff --stat c6814dd8 -- joulewise/calibration_bracketing.py
$ git diff --stat c6814dd8 -- joulewise/adapters/powermetrics.py
$ git diff --stat c6814dd8 -- joulewise/powermetrics_fiducial.py
$ git diff --stat c6814dd8 -- joulewise/uncertainty_evidence.py
$ git diff --stat c6814dd8 -- joulewise/reduce.py
$ git diff --stat c6814dd8 -- configs/calibration/powermetrics_fiducial/protocol_v3.json
$ git diff --stat c6814dd8 -- scripts/night_chains
$ git diff --stat c6814dd8 -- configs
$ git diff --stat c6814dd8 -- joulewise/authentication_io.py
```

All nine are empty. The registry was only read, to compute its digest: `ba1ba3fc596c9ef7f4014131e5cbc2012559f72bab41cafb89e004056790a63c`, equal to §4.6. The round-4 diff (`1bf0ef76..e5af8e59`) touches only paths inside WRITE_SCOPE: the four code files, `tests/**`, and the three granted docs.

## NEEDS_SCOPE

**N-1. The runbook §1.5 arm-record item table (`docs/phase_2/derivation_night_runbook.md`, "What the arm record must carry, every night", about `:2382-2410`).**
- Item 8 says the arm record carries the per-window line. My runbook scope is §2.2a, the §2.1 row, the §2.3 sentence and the policy block.
- `NIGHT_HANDBACK.md:179` now states that the arm record repeats every line, but the runbook's own list of arm-record items does not include it.
- Requested: one table row, "6. Battery-float verdict lines (Revision 5 epochs after W1): every earlier harvested window's `<session_id>: battery=… verdict_sha256=… verdict_commit=…` line, copied from its harvest notice."
- Without it: check 2 of §4.3 still makes the verdict files self-authenticating (§4.7 calls the lines disclosure), but the arm-record checklist is incomplete.

## Findings (all implemented as ruled unless stated)

- **F-1. Three consumers hold no pinned registration digest.** §4.5 applies `load_committed_verdict` to the dry run, `report_window` and `derive_record`. None of them takes a registration argument (`check` has only an optional `--preregistration`; the continuation and the cadence report have none).
  - `preregistration_sha256=None` skips that one identity field for these three consumers only.
  - `battery-verdict` and `_prepare_candidate`, the issuance gate, always pass the pinned digest.
  - If the lead wants those three consumers checked too, each needs a new flag.
- **F-2. Where the dry run looks for records.** The dry run reads records from the ledger's `runs/` parent, the same convention as the round-3 cadence report. In production this equals the tool's repository root, because §2.2a runs `check` from `$MEASUREMENT_ROOT` with the default ledger. No new flag was added.
- **F-3. Dry-run lines §4.5 does not state.**
  - On a custody failure: the blocker only, with no battery line and no mechanism count.
  - On a disagreement: the `battery=<recomputed> recorded=<recorded>` line as well as the ruled blocker.
  - The epoch bound counts recorded non-pass sessions over the issuer's own computed set, which includes the A-7 owners. This differs from "named ∪ S" only for a foreign owner that S exempts.
- **F-4. "It never runs `git`" (§4.2) against `tool_commit` = git HEAD.** I read `tool_commit` with the read-only `git rev-parse HEAD`. The ledger load's pin check already runs `git show`. The tool never adds or commits anything.
- **F-5. Refusals `battery-verdict` adds beyond §4.2.** All exit 3 and write nothing:
  - finalized rows that disagree on the epoch: such a record could never authenticate under §4.3 check 3;
  - a session id that cannot be a file name (path safety);
  - `joulewise/battery_float.py` unreadable under `--repo-root`: the digest is a record field;
  - no readable Git HEAD.
  - To make the fixtures honest, the builder copies `joulewise/battery_float.py` into every fixture root at genesis.
- **F-6. The non-terminal branch of step 3 is unreachable.** For an open session, step 2 (the ledger load) refuses first with `ledger: calibration_ledger_bracket_session_open`, so step 3's non-terminal check is defence in depth. Test 2(d) asserts the reachable refusal.
- **F-7. E2 "numeric" includes finiteness.** `wall_time_s` must be finite. JSON accepts `NaN`, and a NaN age makes `age > 180` false, so a NaN wall time would otherwise pass the staleness check.
- **F-8. Decision-log placement.** A-R5b is on PR #423, not on this branch. A-R5b-1 is therefore appended at the end, where it currently follows A-R5a-1. When the two branches meet, it should sit directly below A-R5b.
- **F-9. Round-3 omission.** `scripts/calibration_cadence_report.py::report_window` (round 3's R2 replay site) was never added to `tests/fixtures/custody_read_replay_allowlist.json`. `tests.test_custody_mode_inventory` already failed at `1bf0ef76`; I checked this by stashing round 4 under a tagged, SHA-applied stash and running it. It is fixed with an insert-only row.
- **F-10. Import-surface regression, caught and fixed.**
  - A module-level `from joulewise.authentication_io import …` in `battery_float` broke 99 `tests.test_evidence_night` lifecycle cases. `night_gate` imports `battery_float`, and the lifecycle clone (`tests/test_evidence_night.py:879`) copies only eight modules.
  - The import is now inside `load_committed_verdict` (`e5af8e59`).
  - Lesson: `battery_float` is on every arm and t0 import path, so its module-level imports must stay standard-library only.
- **F-11. How the provenance travels.** `load_committed_verdict` returns a `CommittedVerdict`, a `dict` subclass that carries `.file_sha256` and `.commit`. The issuer's notes read those two attributes, and nothing re-runs Git to get them.
- **F-12. §4 appears correct as ruled.** Every executed route (A3 counts 1/1, 3/2, 2/1; A4; M1; E8; N1) reproduced exactly at the production call sites above. The one text I could not satisfy from inside scope is N-1.
