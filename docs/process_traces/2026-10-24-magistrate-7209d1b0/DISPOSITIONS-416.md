# #416 pre-arm triple audit at c84bb34c2: lead dispositions (activation 7209d1b0, 2026-10-24)

Reports: Astra 6 xhigh `~/night-archive/seats-786c/audit416/astra-report.md` (ids A*); Fable 5.1 `~/night-archive/seats-7209/fable-report.md` (final, 09:37; same findings as the draft) (ids F-B*, F-S*, F-N*); Opus 5.5 `~/night-archive/seats-7209/opus-report.md` (ids O-B*, O-S*). Auditor probes copied to `~/night-archive/seats-7209/probes/<seat>/`. All three verdicts: ARM AFTER LISTED BLOCKERS. All three reproduced the six sizing rows exactly, and showed native parser = analysis = twin on the real H and BY-H2 streams.

Seat A is `fix/2026-10-24-416-analysis` (worktree `jw-wt/fix416-analysis`). Seat B is `fix/2026-10-24-416-gates` (worktree `jw-wt/fix416-gates`). Both are cut from c84bb34c2 and run Sol 6.1 xhigh.

## Fixed before the registration gate

| finding | lead check | ruling | seat |
|---|---|---|---|
| NEG-8 reference span is the `measured_run` stage, not the request (F-B4, O-B1) | Re-executed. BY-H2 refcorpus r01: stage 8.943 s vs request (tokenize start to decode end) 1.306 s; r02: 8.651 vs 1.327 s. | The span is the whole request, as the registration says. Duration and every boundary's reference energy use that one span. The twin and the blinded stage already do this. B was too small: O-B1 measured the DC drift term 52 % low. | A |
| Synthetic campaigns put no time between stage markers and phases, and use a 10 Hz stream (F-B4, F-N/F6) | Fixture source read by both seats. | Fixtures get production-shaped gaps (sampler spawn, 1 s dwell, wind-down) and a 50 SPS (20 ms) stream. The span rule must show above the bar. | A |
| `test7_passed` manifest boolean is unvalidated (F-S1) | Probe in the Fable report: scale 13.546 drops to 1.0. | `validate_manifest` refuses `test7_passed: true` for pass 1 (P0 ruling 3: no regime passed). | A |
| Numeric predictors are not bound to the registered manifest (A3) | Astra V3: doubled W gives BW 266 → 475 GB/s, no flag. | Both readers refuse a manifest whose model block differs from the registered §4 manifest digest. | A |
| Twin's invalid-record set is wider than the analysis's registered seven (F-S2, O-S11) | Sets read from source. | The twin uses §6's seven, written independently from the text. | A |
| Meter edge power uses only the two adjacent samples, valid only while r_max ≤ Δt (F-S5) | Real margin 11-14 %. | The edge power is the largest sample power within ±(r_max + Δt) of the edge. This equals the registered rule whenever r_max ≤ Δt, so nothing changes on real data. §7 text updated. | A |
| Meter integration bridges dropped samples silently (O-S7: 28 s dropout gives −185 J, no flag) | Not yet re-executed; seat A must reproduce it first. | A decode or reference span with a dropped device sample (from the device's sample counter, an exact integer count) gives no DC-input value for that run, flagged `bytes.meter_gap`. H and BY-H2 had 0 drops. | A |
| Agreement bars looser than §12 (A4) | Astra V4 mutations pass under the bar. | Bars exactly as §12 states: energies 1 % of (h + B); P̄ 1 % of (h + B)/T; H2 coefficients 1 % of HC3 half-width; durations 1 ms; VIF 2 significant figures; any quantity without a half-width at most half a unit in the last place §14 prints. No propagated or relative substitute. | A |
| `cell.below_minimum` excludes the whole session (F-B2, O-S2) | Code `flags/exclusions.py:350-370`, BYTES pack `flag_effects` EXCLUDE_WINDOW; §6 says the cell becomes unavailable and "this never stops a stage". | Code is brought to the text. In the six BYTES packs the condition is cell-level: the cell prints unavailable with its reason, and the session counts. Block 6 is closed and unchanged. | B |
| Arm clock hold judges the kernel frequency word, not the measured rate r (A1, F-S6, O-S1) | 22 block-6 arm records, 44 gate reads: word 0 ppm, PASS every time. Over-strict, never fail-open; it has never changed a number. | Implement P0 ruling 4 and the physics doctrine (measure the quantity, not the setting). The dwell estimates r from its anchor series and applies the precheck's own r bound; steps are residuals from the fitted line; the word, and a change in it, is a recorded diagnostic. Existing registered limits only. Old-vs-new replay over every real arm record on disk. | B |
| C4 runtime stack identity unbound (A2, F-B3, O-B3) | `identity_pins.json`: the ten BYTES units have `stack_identity: {}`; block-6 units have eight keys. The projection half of A2 is not a defect: block-6 claim trees also carry `unprojected` with `derive_never_operator_enter`. | Fill the ten units in the block-6 eight-key shape from the observed runtime and each model's files. A tokenizer, quantization or runtime change must now produce a stack difference (O-A3 probe), and real H/BY-H2 runs must stop carrying a spurious `model.identity_mismatch`. Seat B checks that the BYTES arm path derives the projection the way block 6 did. | B |
| Blinding fail-open: unresolved pack registration exports held-out rows visibly; a missing group key is silently redrawn (F-S9, F-S10) | Fable probes. | Export stops with the cause when the registration does not resolve. A group key is never redrawn once any session of the pack has a sidecar. Both are desk-side, not collection refusals. | B |
| Blinding and catalog untested (F-S11, O-S5 mutants: `PACK_RANGE=(1,1)`, key `O_TRUNC`/0644, `_w` columns) | Mutants survive per Opus A5. | Tests pin the registered ranges, the key-file mode and O_EXCL, and the blinded columns. Acceptance records a flag when the running catalog digest is not the registered one. | B |
| Catalog lacks `bytes.meter_decode_unavailable` and the new `bytes.meter_gap` (F-N1) | grep → 0. | Both added as DISCLOSE in the catalog and the six pass-1 packs' `flag_effects`. | B |
| No test ties the sizing rows to `derivation.json` (O-S11) | Opus A3 probe. | Test added. | B |
| Registration text stale: estimator versions "null"; §7 "100 ms at 10 Hz"; BAT-RULING.md absent; §5 clock wording; C4 slot (A5, F-S13, O-S10) | Verified by all three. | Text corrected; BAT-RULING.md brought into the tree from 1531dfbac. Seat A reports its text changes; the lead applies them at integration. | B + lead |
| Nine number-bearing modules outside both pinned sets (F-S3: bundle_read, whole_window, aggregate, b6/calibration, export_runs, b5/harvest, km003c_parse, analysis_engine/distributions, desk_restore) | `git diff --stat 3bb305d7a..HEAD` per Fable. | Deferred (revised at integration). That file is block 6's registered acceptance (registered_commit 3bb305d7a), shared by BYTES; block 6 is closed. Pass 1 collects from one frozen measurement pin, and the analysis is bound by SHA, so a later edit cannot move a pass-1 number unseen. A BYTES-own number-bearing list goes with the pass-2 registration. | lead |
| Number-bearing `joulewise/b5/driver.py` (a8e871293) and `joulewise/bundle.py` (fcc063249) have no executing-review rows, so every session would be EXCLUDE (F-B1, O-B2) | Expected (record 786c0858 item 26). | The three #416 reports are executing reviews of the whole head. Rows are added for the final integrated head after the delta cold passes, before the registration gate. | lead |

## Kept, deferred or rejected

- **O-S3: disk P is inflated by idle-admission retry files outside the stream span** (s4 116.4 vs 85.1 GB). Kept as P0 ruling 6 has it. The rows err toward more space, and freeing disk is operator work. Changing them now would reopen six re-derived rows that all three auditors reproduced. Opus's dissent is recorded. If disk cannot be freed to the largest P plus smoke share, this is the first thing revisited (consult).
- **F-S4: pro-rating at a phase edge, declared bound 0** (worst case 0.915 J per run, actual 0.043 J). It is inside the ratified ~1 J per-run attribution limit (D-078 clause 11) and pre-registered since block 5. The §7 text names it, and the registration cold gate sees it. No estimator change.
- **O-S4 / F-N4: the blinded stage and the twin use the whole-request anchor column.** These are pre-commit blinded tables only; the fit stage is correct. Seat A fixes it if the export carries the decode-envelope anchor, and otherwise reports.
- **O-S5: the export is not bound to the archive by digest.** Deferred (D-161 threat-model prune: no operator-adversary refusals). SHA256SUMS verification at the desk goes on the pruning-list review.
- **O-S6: precheck UNMEASURED waits forever; the loop's refusal cycle never alerts.** Deferred, named LOOP-REFUSAL-ALERT. The magistrate watches every pass-1 session.
- **O-S7, other items: `thresholds_for` falls back to 335 s; one corrupt meter line drops the session's DC; an evicted bundle or ENOSPC during re-reduction.** Deferred. The fallback errs long, not short. 0 corrupt lines and 0 evictions occurred in H and BY-H2. The StorageStop rule covers restores.
- **O-S8 / F-S12: refit cache schema string.** Numbers are identical; the time cost is already inside S. Deferred.
- **O-S9: the 5 ms anchor cap removed 2 of 168 runs.** This is a registered block-5 rule, and the flagged-inclusive line prints them. Deferred to the pruning list.
- **O-S12: DST repeated hour 2026-11-01 01:00-02:00 PDT.** Scheduling removes it: no pass-1 session spans that hour. Gate rule 5: one setting rather than enforcement code.
- **F-S7, F-S8, remaining NITs.** Deferred to the registration gate charge as named items. F-S8's disk case is backstopped by the precheck's WAIT and the in-window `disk.low`.

## Cold delta passes on 24718b166 (Fable 5.1 REFUSE, Opus 5.5 ADMIT-WITH-CORRECTIONS)

Reports: `/private/tmp/cold416-{fable,opus}/REPORT.md` (copied to `~/night-archive/seats-7209/cold416/`). Both seats were stopped by the lead's 2 h background limit after writing their reports, Fable before its Executed section was final.

| finding | lead check | disposition |
|---|---|---|
| Merged tree's agreement/analysis suites red: fixture cannot export under fail-closed registration (Fable 1, Opus 1) | Same failure in the lead's own shard run | Fixed 2ed536739 (explicit registration for ungrouped synthetic packs). Lead rerun: agreement 48 tests OK, 0 above the bar. The SubsetReleaseChain test wrapper is still red → FIX-416-C item 1 |
| `_reference_request_fields` drops a reference silently on a read/storage failure (Fable 2, BLOCKER) | Re-executed (Fable's blinding_probe2 P on the merged code): a corrupt or unreadable trace exports `succeeded`, empty columns, no flag | FIX-416-C item 2: read/parse failure stops the export with its cause; unreadable request → `bytes.reference_request_unavailable` (DISCLOSE) and no usable record; both readers print dropped references; a missing column on an unflagged reference is an error. Refusal reported to Ed (Gmail 1a16fa8f5681d1f3) |
| bytes-mac-check exports refused (Opus 2, Fable 8) | Opus re-export probe | FIX-416-C item 3 |
| Blinding: whole-document comparison falsely refuses a changed member set; non-atomic sidecar; harvest hides the cause (Fable 3, Opus 6) | Probes in the reports | FIX-416-C item 4 |
| Arm judge passes mid-dwell steps up to 2 ms (old 1 ms); missing f skips the rate gate; G10 control cannot discharge (Opus 3, 4, 5; Fable (a)) | Both seats measured 1.8-2.0 ms on real dwells. No number reads the dwell (Fable (a)). | FIX-416-C item 5: add the precheck's registered consecutive-step test; judge the anchors when f is absent; fix G10 |
| C4 compare omits sampler, output policy, telemetry, OS, hardware; qwen3-8b-8bit tokenizer revision null; issuer roots not recorded (Opus 7, 8; Fable 5) | Opus probes | FIX-416-C item 6 |
| §9 stale 377/400 sentence; §7 edge counts and span ratio (Fable 4, 6; Opus 9, 10) | Lead's text edit left the old sentence | Lead text fix with FIX-416-C's sentences |
| Harvest uses the global catalog, so a below-minimum BYTES session carries `records.claim_usable_counting_disagreement` (Fable 7) | Code read by Fable; disclosure only, acceptance governs | Deferred: HARVEST-PACK-EFFECTS (before stage-1 analysis); §6 gets one sentence |

## Round-2 cold delta passes on 2ed536739..fcc0ac921 (Fable 5.1 and Opus 5.5 both ADMIT-WITH-CORRECTIONS)

Reports in `~/night-archive/seats-7209/cold416b/`. Round 1's blockers are closed. Opus's BLOCKER 1 is the same defect class as Fable's round-1 refusal: a storage fault in a reference bundle still drops the reference from NEG-8. The new cases are a missing, truncated or unreadable raw plist, a missing calibration directory, and a missing bundle directory, now flagged `bytes.reference_request_unavailable`. Real BY-H2 effect of one such drop: rails E_ref 37.12101 → 37.08911 J.

**Lead ruling, structural (FIX-416-D), instead of a consult.** The rule says that the same class failing twice goes to a consult. That rule exists to stop a search that is not converging, and here the cause is identified: the code listed the failure classes that stop, and each pass found more. So the rule is inverted. For a reference the harvest recorded as collected, the export returns:
- the three columns; or
- the disclosed flag, only for the two registered absences (no request markers in a complete, SHA256SUMS-verified `events.jsonl`; no idle baseline in a verified, well-typed summary); or
- a `StorageStop` with its cause, for everything else (any exception, an unresolved anchor, uncovered curve support, a missing bundle, garbled JSON, a digest mismatch).

It is replayed over every real archive before adoption. The precedent is #574 round e: a recurring class with an identified cause was ruled directly.

| finding | disposition |
|---|---|
| Opus 1 (BLOCKER), Fable 1, 2, 4; Opus 2, 6 | FIX-416-D items 1-2 (default-stop, SHA256SUMS verification, every cause printed) |
| Opus 3: a skew-rejected anchor sample voids the dwell and hides a measured rate hazard | FIX-416-D item 3 |
| Opus 7: blinding key first draw can leave 0 bytes | FIX-416-D item 4 |
| Fable 5: whole-dict sampler comparison can exclude a good session after an adapter change | FIX-416-D item 5 (registered keys only) |
| Fable 3: the qwen3-8b-8bit tokenizer revision cannot be compared at harvest (runs do not record it) | Text: the revision is a pin-side record; for this model the tokenizer is bound by its pinned file hashes and the artifact digest |
| Opus 4, 5; Fable 6: step figure about 1.010 ms; span ratios (BY-H2 window 6.5-6.8, corpus 6.3-6.8; H window 6.6-6.9) | Lead text |
| Opus 8: the G10 control no longer exercises the clock module | Deferred (G10 is dormant in block 6/BYTES; diagnostic; pruning list) |

## Round-3 cold delta passes on fcc0ac921..81782d6a3 (Fable 5.1 and Opus 5.5 both ADMIT-WITH-CORRECTIONS)

Reports in `~/night-archive/seats-7209/cold416c/`. Neither found over-refusal on real archives (Fable replayed 6, Opus several; 0 stops). The sources/ side of the default-stop is closed.

| finding | disposition (FIX-416-F) |
|---|---|
| Fable 2 HIGH: derived/roster.json is unauthenticated; removing a collected reference silently drops it (BY-H2 clone: allowance 0.8726 → 1.0123 J, nothing printed) | Same class via another input. The structural rule extends: every input that decides reference membership or status is authenticated against harvest.json's digests or cross-checked against SHA256SUMS both ways; a mismatch stops |
| Opus 1 medium: an unlisted stray directory can shadow the listed bundle (not a regression) | The bundle is the directory the inventory lists; a stray, duplicate or unlisted candidate stops; every bundle-internal input requires a digest |
| Opus 2 medium: the schema's canonical `idle_baseline: null` stops the session export | It is the registered absence (flag); §6 text adds "or null" |
| Opus 3 low: harvested failed vs verified succeeded is not cross-checked | Stop on disagreement in both directions |
| Fable 1 medium / Opus 4 low: "≥ 2 anchors" has no derivation; few anchors weaken the step test | Rate judged with ≥ 2; step test only with N ≥ 150 (derivation: absorption 1.5/N ≤ 1 % of step_ns); below that a disclosed `clock.step_unmeasured`, never a refusal |
| Opus 5 low: exact gap comparison on the non-powermetrics path | Bar 4 × ulp(t) of the edge epoch (the representation limit, 2.4e-7 s near 1.79e9 s, far below the 1 ms printed duration precision) |
| Fable 3 low: scripts/b6_export_runs.py hides messages and exits 1 on StorageStop | Print class and message; exit 5 |
| Fable 4 note: bytes-mac-check resolves only via the registration dir | Recorded (production passes that dir) |
