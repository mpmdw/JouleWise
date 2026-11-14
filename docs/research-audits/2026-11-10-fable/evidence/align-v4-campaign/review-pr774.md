# Independent review of PR #774 (v4 desk release guard), head a5364a01d

Reviewer: Sonnet 5.5, non-author, executing lens. Read-only on the PR (no push, comment or merge). Mutants ran in a throwaway worktree, now removed.

## Verdict: ADMIT WITH FIXES

The leak closure holds. My own sentinel test found no sentinel in stdout, PILOT.json, desk.json or the harvest-off record for C and T windows, and the control (unsealed PILOT.full.json) lit the detector 176 times. The release gate fails closed. Nothing outside the desk path changes for v3: test_pilot4 passes, and the hook default is the identity.

Four fixes are needed before the re-sign. None reopens the leak seen in the synthetic window, but F1 is a real small-pool leak and F2-F4 are coverage holes that three mutants slipped through.

## Findings

1. MEDIUM. The "pooled" G1-timeout figures reveal the G1 timeout of a single D member when the pool is one member.
   - Evidence: `_seal_x2` (v4_desk_seal.py ~L510-520) keeps `x2_count`, `x2_rate` and `g0_timeout_x2_count` through `X2_KEEP`, and adds `gate_timeout_x2_count`. `d_member_x2_report` (align_v4_session.py L845-875) builds `x2 = g0_timeout or gate_timeout` over role 'D' members only.
   - I ran `_seal_x2` on a one-D-member report with `gate_timeout_x2=True`, G0 ok. The sealed output reads `x2_count=1, x2_rate=1.0, gate_timeout_x2_count=1, g0_timeout_x2_count=0`. The per-row column is dropped, but the member's G1 timeout (a carved, heat-ended code) is fully readable.
   - It is also redundant: `x2_count` minus `g0_timeout_x2_count` already equals the G1 count.
   - RL-149 §3 says carved codes print "as a window count over all members". The X2 pool is D members only, and DEVIATIONS says C and T windows hold "D 1 each". If that is the real composition, the pool is one.
   - Fix: in C/T, drop `x2_count`, `x2_rate` and `gate_timeout_x2_count`, and keep `g0_timeout_x2_count`. Or print them only when D members number at least 2 and pool them into `carve_out_flag_counts` over all members. At minimum, confirm the real C/T D-member count and have the lead rule on it.

2. MEDIUM, test gap. Mutant (f) survived.
   - Evidence: moving `PILOT.full.json` to `archive/PILOT.full.json` passes all 12 guard tests plus test_v4_dc_sealing. The tests read the path through `seal.WITHHELD_PILOT`, so no test pins the literal `archive/withheld/` location.
   - Fix: assert the literal relative path and that `PILOT.full.json` is not at the session or inspection root.

3. MEDIUM, test gap. Mutant (g) survived the PR's guard tests.
   - Evidence: with the harvest-off triage sealing disabled (`if False:`), or limited to W1 (h4), `tests.align.test_v4_desk_release_guard` passes. Nothing in that file calls `cmd_triage`.
   - My detector kills both mutants: 6 to 12 sentinel numbers per window appear in the triage record.
   - I could not get test_harvest_off to finish under a mutant (the module exceeds 7 min), so I do not know whether it catches (g).
   - Fix: add a triage case to the guard test. Run `cmd_triage` on the synthetic C and T sessions and run the leak detector over the `--out` record, stdout and stderr.

4. LOW-MEDIUM, test gap. Mutant h3 survived: keeping the `gate_timeout_x2` column per row in `X2_ROW_KEEP` passes.
   - Evidence: the fixture has no G1-timeout data, and the W1 test only checks that non-benign rows are a subset of `X2_ROW_KEEP`.
   - Fix: plant a G1 timeout in a fixture member's episode flags and assert that no per-row `gate_timeout_x2` or `x2` appears in C/T or W1.

5. LOW. The per-member allowlist is wider than any consumer needs.
   - Evidence: grep across scripts/ and joulewise/ shows nothing outside the desk reads PILOT member `chain_eligible`, `chain_reasons`, `target_precheck_eligible`, `window_evidence_precheck`, `harvest_flag_codes` or `readable`.
   - `final_adjudication_error` reads `plan_id`, `status` and `members_excluded` (plus `members_disclosure_only`). `member_eligibility` and `thermal_escalation` read `extra_checks.thermal` members.
   - These fields are for the human desk readout. `chain_reasons` can carry `thermal_pressure_elevated_in_window`, which the PR itself calls heat-bearing, and `window_evidence_precheck` reasons are filtered only for carved codes, not for embedded values.
   - Suggestion: keep them only if the lead wants them on the desk readout, or fold them into the withheld digest.

6. LOW. `release_error` accepts any string of the form `lead: <x> <YYYY-MM-DD>` as the lead signature (`valid_lead_signature`, align_v4_kit.py L817). It binds the sha256 of `series_complete`, but anyone with write access to the measurement root can forge release. This matches existing registration practice, so I flag it for the cold review only.

7. INFO. `W1_EXCEPTIONS` matches its citations.
   - ROSTER (align_v4_kit.py L63-82) gives non-benign ordinals 2, 3, 6, 9, 11, 13, 14, 16. These are anchors 2 and 3, X-G 6 and 16, X-S 9 and 13, and D 11 and 14. The PR says the same.
   - U4 reads ordinals 5 and 17, both benign D (protocol :454, :686).
   - Spot-checked protocol lines in docs/align/pilot_protocol_v4.md: :444-447 (U1-U6), :452-456 (U table), :480 (tool flags), :518 (contrast), :536 (residual), :660 (ruling 5), :686-688 (ruling 6), :693 (ruling 9), :724-728 (ruling 18), :1099-1101 (B0). All fit. I did not re-verify :889 or :493 in context.
   - The non-benign set comes from plan `condition` at run time, not an ordinal list, so there is no hard-coded list to forget.

8. INFO. v3 identity.
   - With `print_policy=None`, `member_lines()` runs once in the print loop with the same keys and order as the old inline prints. test_pilot4 (18 tests, 1 skipped) and test_v4_disclosure_only_desk (13) pass.
   - v4 `desk()` sets the policy only when `print_policy` is not in kwargs, so an explicit caller still wins.
   - The `released()` path returns `None`, which restores the identity.

9. INFO. A pooled count over a small member set is the same class as F1 for `carve_out_flag_counts`. That one is over all members, as ruled, so it is fine as long as the window has at least 2 members.

## Mutant kill table

Run on guard test module plus test_v4_dc_sealing (each one executes the desk on the synthetic six-member fixture).

| Mutant | Result | Killed by |
|---|---|---|
| a. add `episode_seconds` to `MEMBER_ALLOWLIST` | KILLED | C and T no-planted-value tests, W1 test |
| b. `released()` true on `series_complete.json` only (no receipt) | KILLED | `test_a_registered_release_event_opens_the_fields` |
| c. skip the policy for T windows | KILLED | T-window no-planted-value test |
| d. carve-out codes printed per member | KILLED | C and T tests plus a third |
| e. W1 forgets one non-benign member (ordinal 6, analog of 14 in the fixture) | KILLED | W1 switch test plus one |
| f. `PILOT.full.json` outside `archive/withheld` | SURVIVED | none (F2) |
| g. harvest-off triage writes unsealed thermal and km003c | SURVIVED the PR's tests; KILLED by my sentinel detector | none (F3) |
| h1. policy not passed from v4 `desk()` | KILLED | 4 failures |
| h2. R22-3 balance unsealed in C/T | KILLED | 3 failures |
| h3. per-row G1-timeout column kept in X2 rows | SURVIVED | none (F4) |
| h4. triage sealing limited to W1 | SURVIVED the PR's tests; KILLED by my detector | none (F3) |
| h5. thermal member `tokens` printed raw | KILLED | 3 failures |
| h6. C/T DC seal not applied in `powermode_desk_check` | KILLED | 2 failures |

The harvest-off module was not run to completion for g or h4 (see below). Mutant (b) first appeared to hang only because I had test_harvest_off in the batch.

## Independent leak re-check

Script: /private/tmp/claude-501/mine/sentinel_check.py. It reuses the PR's fixture class (`Fixture`, six synthetic members, existing pattern) but replaces `plant()` with my own sentinels: unique 7-digit-plus floats and ints in every numeric and outcome field (GPU and CPU joules, turn joules, scores, seconds, battery, DC, owned, gross, latency, waits, tool counts) and unique strings (tool names, bank stage, side-task text).

My detector is separate from the PR's: it scans every number token for a rel-1e-9 match with each sentinel (and its int form), checks a 9-significant-digit substring signature, and checks string sentinels. It does not use the PR's key blacklist.

Results on the PR head, C3 (calibration) and T2 (test) windows:
- stdout, PILOT.json, desk.json: 0 hits.
- harvest-off `cmd_triage` record (`--out`), JSON stdout, stdout and stderr: 0 hits.
- Control (the unsealed `archive/withheld/PILOT.full.json`): 176 hits, so the detector works.
- With the triage seal removed (mutant g), the triage record leaks sentinels (turn joules, tokens, call counts).

## Test tails (taskpolicy -b python3.13 -B -m unittest, PYTHONPATH=.:tests)

- tests.align.test_v4_desk_release_guard: `Ran 12 tests in 17.511s  OK`
- tests.align.test_v4_dc_sealing: `Ran 2 tests in 0.097s  OK`
- tests.align.test_v4_disclosure_only_desk: `Ran 13 tests in 45.017s  OK`
- tests.align.test_pilot4: `Ran 18 tests in 123.697s  OK (skipped=1)`

## Diff checks

- Allowlist: see F5. It is the intended set plus six desk-readout fields no consumer reads. Everything that `final_adjudication_error`, `member_eligibility`, `thermal_escalation` and `cmd_final` read is kept.
- `W1_EXCEPTIONS`: matches the roster and spot-checked protocol lines (F7). The `in_class` markings (U1/U2 placed in the class by the builder) are for the cold review.
- v3 behaviour: only `scripts/align_pilot_session.py` touches common code. The hook is a default-None parameter, member lines are built by the same code, and the shown values come from the same objects. v4_registration.py only adds the new module to `EXECUTED_CLOSURE` (which is the re-sign trigger, as the PR says).
- `cmd_triage` now seals through `v4_desk_seal.seal_extra` with the rows as plan members. That path is exercised only by my detector (F3).

## What I could not check

- test_harvest_off against mutants g and h4 (module too slow, over 7 min per run). Whether it already covers triage sealing is unknown.
- Real C/T window composition (number of D members), which F1 turns on. I used the DEVIATIONS text, not a real roster.
- Real bundles, real harvest catalogs and real `thermal_desk` output. All inputs are the PR's synthetic fixture with patched `window_report`, `desk_diagnostics`, `km003c` and `enrich_record`, so a real field outside the patched shapes could print unnoticed (for example a real `window_evidence_precheck` reason carrying an embedded value).
- The CI run, the cold-review items for the `in_class: False` W1 rows, and the pre-C1 seal-list ledger step.
- Mutants of the guard on the W1 non-benign ordinals 14 and 16 specifically: the fixture has six members, so I used ordinal 6.
- No full suite, no SSH, no `~/night-*`, no real measurement content.
