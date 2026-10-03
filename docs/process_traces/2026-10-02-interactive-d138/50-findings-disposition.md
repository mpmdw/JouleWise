# PR #457 findings disposition (ledger row 5)

Every finding from the gates of the D-138 Revision 6 block 1 issuance, with its disposition. The
issued bytes (`f949f511…3660`) did not change in the fix round (`promote_calibration_candidate.py
--check` passes on the final head).

| Source | Id | Severity | Finding | Disposition |
|---|---|---|---|---|
| Fable final pass ([31](31-fable-final-pass.md)) | F1 | major | The rev6 text validator required only D1..Dn with n ≥ 1, so a text missing D10 would promote | **Fixed**: the rev6 entry pins the ids exactly `D1`..`D10` and the network-time disclosure to `D1`; two new RED-then-restored clauses (`disclosure_last_missing`, `disclosure_extra`), each RED with the pin removed |
| Fable final pass | F2 | minor | `tests/verify_registered_calibration_snapshot.py` defaulted `--reference-ref HEAD`, so it fails at or after this merge | **Fixed**: default is the pre-issuance main commit `384696d2` (P8 default); run on the branch: `REGISTERED_GENERATIONS=PASS count=9 retained=8` |
| Fable final pass | F3 | minor | The issuer's `--predecessor-acceptance` defaults to the live default (now r2), while a Revision 6 prepare requires P8; a default invocation refuses (fail-closed) | **Deferred** to the block-2 design seat (RUN_STATE item 7; already recorded on main as a block-2 design input, `f08b58cc`): any further Revision 6 or successor registration names its predecessor explicitly. Nothing silent |
| Fable final pass | F4 | nit | Pin-classification census predates two later test changes (87 hits, not 77) | **Fixed**: addendum and final census in [06](06-pin-classification.md) |
| Fable final pass | F5 | nit | A cited path inside the repo but not the intended record would pass the citation check | **Rejected**: every cited digest is verified against the bytes and the ruling ids are fixed and ordered; a substitute file cannot carry the cited digest |
| Sol review ([10](10-sol-review.md)) | R1 | nit | Classification omits ten final-head test hits; its NEEDS_SCOPE line is obsolete | **Fixed** in [06](06-pin-classification.md) (final census 87: 46 moves, 41 stays; NEEDS_SCOPE line marked resolved) |
| Sol review | F1 (flag) | environment | Live epoch-probe test fails only in the sandbox (`os_build=None`), identically at base | **Rejected as not a defect**: lead reran it outside the sandbox on the branch: `Ran 1 test … OK` |
| Sol review | F2 (flag) | baseline drift | origin/main moved after the review base | **No action**: the fix round changed no number-bearing code (promotion text validation, tests, records); main's new commits were RUN_STATE only |
| Sol review | F3 (flag) | verification gap | No canonical discovery or live capture by the reviewer; A335 deferred | Whole suite run by the lead on the final head ([40](40-suite-tail.txt)); live capture is the next block's; A335 is disclosure D10 |
| Whole suite, first run (head `fa77d7b0`) | S1 | regression | `tests.test_issue_p8_pin_delta`: 2 tests asserted P8 as the live default through the no-argument loader (the pin grep does not match that call) | **Fixed**: P8 named by path; the default derivation basis is asserted to be the live 25G83 generation, P8 by path still a valid basis, R7 stale. Module 5/5 OK |
| Whole suite | S2 | environment | 52 known local-only failures (46 battery fixture in child Pythons, 3 `UpdateTime` stale, 3 load-worker startup contention; the last passes serially, 96/96) | **Deferred** to lane TEST-LOCAL-ENV-ISOLATION-01 (pre-existing; same classes as #456) |
| Seat (Sol implementation, [05](05-sol-implementation-report.md)) | NEEDS_SCOPE | — | `tests/test_calibration_live_three_window.py` loaded the live default into an import-only synthetic issuance | **Fixed** by the lead (explicit P8 load; 47 tests OK with `test_arm_readiness_evidence_author`) |
| Erratum refuter ([41r](../2026-10-02-interactive/41r-erratum-nt1-refuter.md)) | 1–5 | — | Text-versus-code precision on the receipt wording and stderr; attribution of the 0137Z re-arm; disclosure nits | Dispositioned in [42-erratum-nt1.md](../2026-10-02-interactive/42-erratum-nt1.md); stderr narrowing deferred to lane NT-STDERR-NARROW-01 |
| Cold science gate ruling §6 ([RULING-judge](../rev6-derivation-block1/packet/RULING-judge.md)) | 1–6 | non-blocking | Six observations for the D-138 gate | Item 1 and 3: erratum E-NT1. Items 2, 4, 5, 6: disclosed as D2, D4, D5, D6 in the issued file |
| Cold science gate refuter | 1–3 | — | ICC transcription slip; quantile-route independence; voiding sentence | Items 1, 2 disclosed as D7, D8; item 3 answered in erratum E-NT1 |
| Scope (E1 §4 step 15) | — | — | The explicit old-epoch R7/P8 re-evaluation route is not in this PR | **Deferred** to lane A335 (OLD-EPOCH-EXPLICIT-R7-ROUTE-01); disclosed as D10; Fable confirmed no judging path silently evaluates a 25F84 result against the 25G83 file (each refuses by name) |

## Closing-merge custody precondition (E1 §3.3, step 18)

E1 §3.3 requires, before the closing merge, a second copy of R7's 17 members' `raw/powermetrics.plist`
outside iCloud. Session ff50b201 item 42 recorded it done (the three archive-only plists restored to
the local corpus root and hash-verified: `a22005ea…`, `9934c975…`, `bb99b0b7…`; all 17 local plus
iCloud). Re-verified by the D-138 seat on 2026-10-02: for each of R7's 17 members,
`/Users/edr/code/JouleWise/<source_directory>/raw/powermetrics.plist` exists and its sha256 equals
`artifact_sha256["raw/powermetrics.plist"]` in the member's `instrument_evidence.json`, whose own
sha256 equals R7's `instrument_evidence_sha256`: 17 of 17. (The state kernel's lane row
CALIBRATION-RAW-SECOND-COPY-01 still reads `queued`; it is stale.)
