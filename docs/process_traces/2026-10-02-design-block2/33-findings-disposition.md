# PR #458 findings disposition (lane G2A-NIGHT-25G83-01)

| Source | Finding | Severity | Disposition |
|---|---|---|---|
| Sol review [31](31-sol-review.md) | G2A-01: window runbook still states span 33556 / window 34456 | minor | **Fixed** in `4cacd72b` (runbook §14 and runsheet carry 17248 / 19980; authoring example takes `"$WINDOW_MAX_S"`) |
| Sol review | F1/F2: eight base-matched battery-fixture driver failures; one head-only watchdog timeout that passed on replay | environment | **Rejected as not a defect**: identical ids at base (lead compared by id); timeout is contention |
| Sol review | F3: harvest fixtures mock the ledger/bracket/raw seams | residual risk | **Accepted**: the real mock-capture campaign test proves the low-count path; live behaviour is the window's own (registration §7 RECOVER routes any surprise) |
| Sol review | F4: stray scratch process PID 76991 | cleanup | **Fixed**: process had exited when checked |
| Cold seal ruling [51](51-seal-ruling.md) | C1 (F1): clock-refused member counted | major | **Fixed** in `d5b28bb8`: member valid only when `metadata.json` `uncertainty_evidence.clock_anchor.status == "bounded"`; tests `test_c1_*` (five small non-bounded → RECOVER shortfall; missing record → invalid; one large non-bounded → SELECT 23/24; count 2 + bounded stays valid) |
| Cold seal ruling | C2 (F2): REFUSED instead of the §7 verdict when the chain's summary counted an invalid member | major | **Fixed** in `d5b28bb8`: equality required only when every member is valid; otherwise `chain_summary_copy` records the difference; tests `test_c2_*` |
| Cold seal ruling | F7: no-capture class not recorded | minor | **Fixed** in `d5b28bb8`: `capture_made` from `raw/powermetrics*.plist` in the archive copy; tests `test_t8_*` |
| Cold seal ruling | F8: author command accepts any window ≥ span + 900 | minor | **Fixed in the arm recipe** (step2 requires `WINDOW_MAX_S` to equal span + 2700 rounded up); code unchanged (tests use the minimum) |
| Cold seal ruling | F9: NULL only after the completion boundary | minor | **Rejected**: the next arm's discovery treats the plan span as active until the same boundary, so an earlier NULL saves no time |
| Cold seal ruling | F10/F11: summarizer zero-member rung `0` vs `null`; `windows[0]` | nit | **Deferred** to lane G2A-FOLLOWUPS-01 (unreachable through the harvest: the selector runs only on SELECT, configs fix one prefill window) |
| Cold seal ruling | F4, F5, F6, F12, F13, T1-T8 | text | **Applied** to the registration (T2a chosen: no chain change) |
| Seal refuter [51r](51r-seal-refuter.md) | D1: later windows other than recovery need a head rule | minor | **Applied** inside T6 |
| Seal refuter | D2: no real member bundle at H shown with a `bounded` anchor | risk | **Disclosed** in the seal record; the recipe routes a systematic non-bounded RECOVER to a consult, not to `w2`. A live member capture is outside this seat's authority (no powermetrics) |
| Seal refuter | D3, D5, D6 | nit | **Rejected**: no number depends on the chain's copy (D3); the driver checks the 600 s/same-boot conditions before the chain starts (D5); the D-166 wording governs the `_v5` arm's printed result, not this block (D6) |
| Lead | The seat's first span sizing (33,556 s) | design | **Fixed** in `8a8635a7` (17,248 s, design record item 7) |
| Lead | WindowDeadlineTests chain fixture lacked the span literal (5 regressions) | regression | **Fixed** in `8a8635a7` |
| Lead | NULL verdict for a window whose chain never started | design | **Added** in `8a8635a7` with a test |
| Lead | `--new-g2a-window` forced the plan into the night root (published before the arm notice) | design | **Fixed** in `4cacd72b`: plan may be staged; test `test_plan_may_be_staged_outside_the_night_root_for_later_publication` |
| Sol delta review [32](32-sol-delta-review.md) (MERGE) | G2AD-01: wrong-filename negative test masked by existing outputs (mutant survived) | should_fix | **Fixed** in `a7aa3029`: fresh coordinates and a filename-specific assertion; the lead re-ran the mutant (guard removed): the test fails |
| Fable final pass [36](36-fable-final-pass.md) (MERGE) | F1: eight harvester guards correct but unpinned (8 surviving mutants) | minor | **Fixed** in `2b49b041`: the judge's 16 probes lifted into `tests/test_harvest_g2a_window.py` as `test_guard_*` (46 tests OK) |
| Fable final pass | F2: real seams (input auth, ledger replay, strict validation, bracket decision) only exercised with fixtures | minor | **Accepted** (as Sol F3): any fault there yields REFUSED or RECOVER, never SELECT; the first real harvest exercises them |
| Fable final pass | F3: a derivation chain registered under D-166 now refuses before OFF (no span literal); the derivation generator's example plan still shows D-166 | minor | **Rejected as a defect, recorded**: fails closed; every Revision 6 window carries the Revision 6 registration (C1, C2 did); the example text is historical (pre-seal W2). Example refresh deferred to lane G2A-FOLLOWUPS-01 |
| Fable final pass | F4: allowlist line numbers stale | nit | **Fixed** in `2b49b041` (143, 174) |
| Fable final pass | F5: Revision 6 refusal text lists missing evidence in a different order | nit | **Rejected**: outcome and record keys identical |
| Fable final pass | F6: `exit_code` JSON `false` equals 0 | nit | **Rejected**: the driver writes integers; string `"0"` already gives RECOVER |
| Fable final pass | F7: a harvest failing after the pin advance cannot be re-run cleanly | nit | **Deferred** to lane G2A-FOLLOWUPS-01 (fail-closed; recipe §7 REFUSED → R3) |

Lane G2A-FOLLOWUPS-01 (named here; registered in RUN_STATE's block-2 handoff): seal F10/F11 (summarizer zero-member `null`, single prefill window assertion), Fable F3 example refresh, Fable F7 post-advance re-harvest.
