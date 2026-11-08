# R11 independent review — Sol-2

**Verdict: HOLD for W1 registration.** One HIGH and two MED findings below
have failing-first synthetic witnesses. The existing scientific/native holds
also remain real holds. This is one independent seat, not the two-seat
agreement report, and grants no arm, merge or measurement authority.

Launch series: 2026-11-08; executed 2026-11-07 PST. Seat is **sol2**, from
`align/2026-11-08-v4-r11-review-sol2`. Reviewed candidate:
`c3796bf49256cb9243976915234f05c529657132`, including safeguards
`7895b9e7ea0436c44685bb7599dccc7b2c5dd804`, registration `659cea924`,
KM003C `4c1041c78`, and merge `199006f16`.

## Authority and coverage

Authority was read from local Git objects, without fetching:

- `origin/main` = `f48741f157685aa068465c7cb5e3c1f4af098e85`:
  `RUN_STATE.md:1185` item 203, `:1175` item 204, `:1098` item 209,
  `:1091` item 210, and `:1060` item 212. In particular, item 212 lines
  1061–1075 adopt qualified HC/HR findings, preserve U items, choose the
  named R/D alternatives and retain the GPU residual/shared meter launcher.
- `4526de7d587a412073cf792c959090401e8d4797` on
  `origin/align/2026-11-07-squeeze-agreement-final`:
  **`docs/align/squeeze/AGREEMENT-FINAL.md`**, not a file under `fanout/`.
  Track 1 is at lines 37–58; the final action list is at lines 115–134.
- Repository M0, active-stop section (NONE), queue/do-not-do section,
  orchestration, targeted decision authority, chair/lead rulings, protocol,
  residual contract and implementation disposition map were consulted.
  The explicit review brief overrides stale queue pointers and full-suite/
  coordination-state instructions. No coordination state was changed.

**Material coverage limit:** the literal requested comparison is much larger
than the three named pieces. `git log --oneline origin/main..HEAD` contains
**1,117 commits**. `git diff origin/main...HEAD` uses merge base
`d842f697f37a95a439dbb89927185b4b6e4fb1ea` and spans **3,120 files,
797,673 insertions, 18,420 deletions** (37,677,253 diff bytes). Its inventory
includes 2,348 config files, 155 `joulewise` files, 65 scripts and 312 tests.
Both requested outputs were captured under `/private/tmp/r11-review-sol2-*`.
I inspected that inventory and the three-piece diff against the pre-stack
R10 baseline (`d600baba0`/`581560e5d`), then followed relevant live call paths.
I did **not** independently line-review all 1,117 inherited commits or every
unrelated Block-series/config/document addition. Accordingly this report
cannot certify the entire literal main-to-head stack. The lead should retain
its earlier gates or supply an isolated integration comparison; this review
must not be represented as blanket approval of that history.

## Ranked findings

### F01 — HIGH: the exact-candidate receipt omits executed cache code

`joulewise/align/apple/v4_registration.py:16` enumerates the exact allowed
artifact set. `:75` requires that set, and `:89` verifies only those paths
plus the two report files against current bytes and the named commit.
`joulewise/align/apple/prompt_cache.py` is absent. Yet
`joulewise/align/apple/endpoint.py:662` constructs `EpisodePromptCache`,
`:667` obtains the actual fed delta, and `:714` reconciles represented IDs.
These operations directly implement R09's work/accounting requirement.
The regeneration identity at `scripts/align_v4_kit.py:1524` binds the kit
generator; it supplies no hash for this cache implementation.

**Failure scenario:** after Stage A/B review, a normal later clean commit
changes cache prefix/rebuild behavior without changing a listed artifact.
The old receipt still validates. A plan can then pin the new code while the
gate receipt authenticates a different implementation of measured work.
This is ordinary implementation drift, not a forged-verdict threat. R01
requires exact-candidate admission; protocol `:731` promises relevant runtime
bindings. A code pin alone does not prove the gate reviewed that code.

**Witness:**
`tests/align/test_r11_review_sol2.py:17`,
`RegistrationCandidateWitness.test_receipt_refuses_changed_live_cache_implementation`.
It creates every required artifact and both reports in a temporary repository,
validates the original receipt, commits a changed cache function, proves the
worktree is clean, and expects refusal. Actual: **ValueError not raised**.

**Lead disposition needed:** complete the measurement/accounting dependency
binding (at least the executed cache helper; audit the MLX adapter, sampler,
attribution and meter-parser dependencies as well), or adopt a suitable
candidate-tree binding. Preserve the lightweight lead-manifest threat model.
The current pending receipt/U3 stop prevents a present-day arm; this is a
latent gate defect once the scientific stops are resolved, not proof of an
arm that already occurred.

### F02 — MED: zero-turn X-G turns non-veto identity failure into refusal

`v4_registration.py:173` emits a failed WP19 receipt for no native X turns,
with `live_x_turns_compared=0`, `live_x_complete=False` and the explicit
`INCONCLUSIVE: identity broken` predeclaration. But `:199` rejects a compared
count below one even for a failed receipt. `require_registration` at `:113`
and the thermal desk at `scripts/align_v4_thermal_desk.py:21` invoke that
validator. The WP19 writer accepts an empty JSONL input at
`scripts/align_v4_wp19.py:90` and emits this rejected record.

**Failure scenario:** R1 X-G times out at G0 and produces no turns. D's timing
evidence can otherwise be valid; R07 explicitly allows a non-veto
INCONCLUSIVE contrast for incomplete/failed proof. The cap code handles
missing evidence (`align_v4_kit.py:644`), but its WP19 receipt cannot pass
schema validation. After other gates are supplied, W1 still refuses rather
than retaining the known-unavailable contrast. This conflicts with protocol
`:702` and the R11 supersession at `LEAD-RULINGS-2.md:919`.

**Witness:** `ContrastIdentityWitness.test_zero_turn_x_retains_nonveto_failed_identity_receipt`
in `tests/align/test_r11_review_sol2.py:69`. All-turn synthetic X/Y renders
pass; the empty native source has a valid SHA-256; the failed receipt is
rejected with **`wp19_receipt.json pending or malformed`**.

**Recommendation/uncertainty:** permit an explicit failed/unavailable zero-turn
receipt while prohibiting a PASS/T claim, or have the lead expressly rule a
minimum-native-evidence exception to non-veto R07. My reading includes the
zero-turn case in failed/incomplete identity. If the lead intended otherwise,
that exception needs an explicit disposition. This witness does not claim
that original native X/Y execution has been attested by rendering.

### F03 — MED: H* still manufactures exact crossings from invalid/incomplete inputs

`v4_estimands.py:21` labels its result `registered_secondary`, coerces dose
keys with `int`, and selects the first *present* above-threshold grid entry.
It neither rejects fractional doses nor marks a missing earlier grid point
unresolved. This is distinct from the repaired carrier curve's integer-dose
and missing-grid checks at `:85` and `:119`.

**Failure scenarios:** `(128.5, score=2)` at threshold 1 is reported as exact
`H*=128`; with 128 below threshold, 256 absent and 384 above threshold, it
reports `H*=384` although the first registered-grid crossing could be 256.
The latter can arise from an incomplete score export and overstates the
resolved hidden-work dose. R15 requires actual doses and undefined crossings
to remain explicit; protocol `:587` retains those requirements.

**Witnesses:** `ExactDoseWitness` at
`tests/align/test_r11_review_sol2.py:87`. Expected fractional-dose refusal is
absent; expected unresolved crossing instead equals **384**. Strict `>`
itself is correctly repaired. This helper remains unwired to the production D
desk, so these are pre-integration defects, not observed errors in a v4 result.
The coercion/missing-grid behavior predates R11 and survives its R15 repair.

## Q1 — fidelity to the rulings

**Not every adopted requirement is complete.** The three witnessed gaps above
remain, and several requirements correctly remain pending instead of receiving
invented constants, capacity or approval. I found no additional change in the
three-piece product diff to the registered GPU residual, model, seed law,
exclusion law or ≥39/pair plus separate-test requirement.

| Item | Candidate evidence and assessment |
|---|---|
| R01 | Receipt/gates/digest checks `v4_registration.py:58`; F01 prevents full exact-candidate fidelity. Template stays pending (`registration/registration_receipt.json:49`). Native inputs/access chronology and actual independent gates remain owed. |
| R02 | Required InstantAmperage/≥99%/missing-field refusal `v4_registration.py:158`; arm/OBC/raw evidence `align_v4_session.py:254`; no invented B bar (`v4_registration.py:252`). Completed-top-up timing, actual battery flow and the numeric window consequence remain lead/native obligations (`pilot_protocol_v4.md:602`). |
| R03 | `validate_u3` at `v4_registration.py:147` unconditionally refuses with R11/R03; derivation emits only a descriptive PENDING block (`:118`). No k=3/2.576 or v3-margin fallback is installed for v4 (`thermal_desk.py:636`). |
| R04 | U4 anchor veto demoted only for v4 (`thermal_desk.py:643`); U5 consequence remains pending (`pilot_protocol_v4.md:721`). Final-Q6 U6 OC and D-series wiring are not supplied. Failed/imprecise checks are not promoted to pass. |
| R05 | Explicit 5/17 E_ref (`v4_estimands.py:219`); completed/clean/≥3-turn admission (`:316`); alternate reference remains unresolved (`v4_registration.py:237`). Final-policy transfer/recovery is still required. |
| R06 | Per-template delivery, stage-adjusted eight-row fit, df=3 and positive direction (`thermal_desk.py:322`, `:361`, `:371`); targeted registration/R11 tests pass. |
| R07 | Separate bound contrast on both paths (`align_v4_kit.py:941`), zero/missing cap handling (`:644`), runtime binding (`thermal_gates.py:110`), and combined desk predeclaration (`align_v4_thermal_desk.py:32`). F02 is the remaining zero-native-turn veto. |
| R08 | A bare fallback cannot admit (`align_v4_kit.py:301`); chosen-budget actual turns checked (`:411`); no X7 budget waiver added. Qualified remeasurement remains necessary. |
| R09 | Checkpoints-off/accounting policy retained (`pilot_protocol_v4.md:645`, `prompt_cache.py:16`, `endpoint.py:667`). Cache module passes 13 tests. Receipt coverage remains incomplete (F01). |
| R10 | Seed tag unchanged and quantization labelled (`pilot_protocol_v4.md:173`); R0 digest binding (`align_v4_kit.py:1029`); observed runtime/effective-policy identity (`v4_registration.py:211`, `v4_estimands.py:255`). Full final-policy transfer and actual access history are still pending. |
| R11 | Daytime config/digest/time receipt without an invented freshness duration (`align_v4_session.py:284`, `:292`, `:308`). Qualified continuous mount-event audit and missing-evidence consequences remain owed (`pilot_protocol_v4.md:678`). |
| R12 | Authenticated unobserved reference refuses before runtime preparation (`thermal_gates.py:255`); observer KeyboardInterrupt escapes while SystemExit is absorbed (`run_night.py:2589`), consistent with recorded Ruling-76 scope correction, not a newly invented signal policy. Whole-chain loss text corrected. #694-on-#699 delta evidence remains owed under main item 209. |
| R13 | Q4 maximum 59,520 s (`pilot_protocol_v4.md:155`), m≥39/pair plus separate locked test (`:556`), 42→35 loss arithmetic, pre-W1 margin ruling and capped unresolved outcome (`:568`, `:836`). No D7/D8 or ≥6-sabotage authority was invented. Actual F/C/test roster, both-pair/all-stop OC and cap are absent, so this is not registration-ready. |
| R14 | Correct rank-38/.05 versus rank-39/.025 wording (`v4_estimands.py:49`, `:274`; protocol `:576`; `energy_residual.md:430`; public HTML `:154`). Frozen legacy scorer is explicitly unqualified for registration D. The new helpers do not repair its LOTO/full-fit asymmetry or window dependence. |
| R15 | Other-carrier untouched H=0 reference, ≥40 total for ≥39 donors, strict ties, no grid interpolation and conditional window bootstrap (`v4_estimands.py:70`). F03 remains in H*, and final scorer wiring/uncertainty admission is pending. |
| R16 | Count-only opportunity at chosen B_D (`align_v4_kit.py:411`, `align_w1_budget_procedure.py:146`); known two-turn case routes to (b), missing counts to unresolved/rerun. This is opportunity, not a sabotage-capability finding or proof of an earlier blind deadline. |

The explicit R11 choices R07/R10/R03/R13/R14 are therefore preserved as above,
subject to F02/F03. **D07/D09/D12 are v5 obligations**, not implemented endpoints
in this Track-1 candidate: directly calibrated max(g_E,g_M) at .05 with .05
solos and a Bonferroni sensitivity; assigned side-task success AND no joint
alarm with utility; trusted-time-plus-monitor primary comparator. Their
authority is main item 212 lines 1068–1070. The candidate explicitly sends v5
to its own registration (`pilot_protocol_v4.md:744`, `LEAD-RULINGS-2.md:1008`)
and supplies no runnable joint detector/addendum claiming to satisfy them.
Track-2/3 HC/HR actions remain future obligations, including independent
F/C/test, unknown-channel accounting, actual capable attacks, physical shams,
fair solo/time comparisons, provenance and bounded claims. They must not be
marked DONE because this Track-1 lane exists. No new joint budget, semantic
margin, dose, reserve or test sample size is adopted here.

## Q2 — blinding and release

I found **no demonstrated new pre-release outcome or monitor-score leak in
the reviewed three-piece changes**. This is a code-review conclusion, not an
audit of any session's actual access history or a complete release rehearsal.

- R10's procedure takes a timing/count whitelist (`align_w1_budget_procedure.py:46`,
  `:68`). No new energy/U5/residual predictor drives its branch. Count exports
  and an opaque source digest do not require reading their energy fields.
- New DC values are explicitly permitted **print-only secondary diagnostics**
  (`km003c.py:21`, `:44`, `:244`; session print `align_v4_session.py:161`).
  They are not standardized monitor scores or a new GPU alarm. No change was
  made to `pilot_analysis.py` or `joulewise/align/energy_residual.py` by these
  three pieces; their legacy outputs remain development diagnostics, not a
  qualified locked-test scorer (protocol `:581`).
- Full-reasoning transcripts must remain sealed/unscored until v5 registration
  (`pilot_protocol_v4.md:743`). This stack does **not** implement or qualify
  the separate transcript-sealing fan-out, monitor export or release gate.
  No monitor was run here. Do not infer end-to-end sealing from that sentence.
- W1 is development, not a held-out calibration/test pool (`pilot_protocol_v4.md:563`,
  `:669`). Actual R0/R1/threshold/monitor access chronology is still unfilled
  (`DEVIATIONS.md:5`). No retrospective blindness or re-promotion of exposed
  cohorts is established. F01 could allow later unreviewed release/accounting
  code drift; it is not evidence that such a leak has occurred.

## Q3 — KM003C

The reviewed wiring reuses the shared launcher and keeps DC secondary.
`align_v4_session.py:54` delegates to the pilot preparation;
`align_pilot_session.prepare:40` uses the Block plan path;
`run_night.py:4554` selects `_hazard_seams`;
`joulewise/b5/driver.py:740` supplies the existing reader argv and `:2464`
starts the supervised meter. The new KM module contains no child launch.

`km003c.capture_member:110` refuses unresolved clocks, insufficient coverage,
dropped samples and protocol errors; restarts are not spliced. `km003c.py:197`
checks stream hashes; per-member exceptions and supervisor faults become flags
at `:214` and `:218`. The session catches whole diagnostic failures and emits
one flagged missing row per member (`align_v4_session.py:156`), while the GPU
checks have no DC admission predicate. The separate DC fit is in-sample and
issues no z score/threshold (`km003c.py:226`, `:241`). The 16 ALIGN meter tests
and the three parser/monitor modules corroborate synthetic behavior only.

No observed native samples, battery correction, coverage/custody or stop proof
was claimed. No second physical reader or USB probe was started by this review.
The explicit real-meter smoke was skipped. The new declaration has no toggle
that disables the existing shared reader. Future D kit/custody/desk routing
still needs its own qualification.

## Q4 — refusal behavior

Missing/disabled/wrong reader declarations refuse before later readiness fields
(`align_v4_kit.py:1267`, `km003c.py:32`), with **RUN_STATE 210 / squeeze ruling**
in the message. `tests.align.test_km003c` exercises these cases and passes.
The pending exact-candidate receipt refuses (`v4_registration.py:58`), and
even an apparently filled historical U3 artifact cannot bypass **R11/R03**
(`:147`). `generate(check=True)` rechecks generated bytes and readiness
(`align_v4_kit.py:1640`); install invokes it before its host operations
(`align_v4_session.py:392`). Registration and meter checks survive integration.

These are sound existing stops; no current arm bypass was demonstrated.
They do not close F01, and F02 is an additional unintended refusal under my
reading of R07. A generic “WP19 malformed” message conceals that policy conflict.
The unresolved B window consequence, U3 science, series margin and qualified
mount/identity/capture evidence remain blocks on signing, not green results.

Direct read-only probes on this checkout also refused as expected:
`require_registration(Path.cwd())` reported **registration_receipt is pending
or malformed**; `kit.generate(Path.cwd(), check=True, source_root=Path.cwd())`
reported **v4 kit BLOCKED by placeholders** for R0 reasoning effort and R1
B_D/I_D/T_dead/thermal policy. It did not report generated-byte drift. These
probes neither called prepare/install nor performed host operations.

## Q5 — execution evidence

Every module/selection ran in its **own process, sequentially**, using
`python3.13 -B -m unittest <selection>`. Environment was
`JW_B5_SYNTHETIC_ONLY=1 JW_WP22_FULL=0`; additional meter checks also used
`JW_REAL_METER_SMOKE=0`. No full suite or Block-5 analysis ran. Module
subprocess wall time total was **76.669 s**, plus the 0.962 s witness run.

| Selection | Exact unittest summary | Exit |
|---|---|---:|
| `tests.align.test_v4_r11` | Ran 27 tests in 0.268s; OK | 0 |
| `tests.align.test_v4_registration` | Ran 19 tests in 7.201s; OK | 0 |
| `tests.align.test_v4_kit` | Ran 116 tests in 6.182s; OK | 0 |
| `tests.align.test_w1_kit_r10` | Ran 30 tests in 6.211s; OK | 0 |
| `tests.align.test_v4_estimands` | Ran 14 tests in 0.002s; OK | 0 |
| `tests.align.test_thermal_desk` | Ran 24 tests in 1.123s; OK | 0 |
| `tests.align.test_v4_w1_synthetic` | Ran 18 tests in 1.512s; OK (skipped=14) | 0 |
| `tests.align.test_km003c` | Ran 16 tests in 2.245s; OK | 0 |
| `tests.align.test_protocol_v4_doc` | Ran 6 tests in 0.245s; OK | 0 |
| `tests.align.test_v4_w1_plan` | Ran 12 tests in 0.628s; OK | 0 |
| `tests.align.test_window_reference_custody` | Ran 5 tests in 0.721s; OK | 0 |
| `tests.align.test_pilot3_cache` | Ran 13 tests in 0.625s; OK | 0 |
| `tests.align.test_thermal_gate` | Ran 44 tests in 9.076s; OK | 0 |
| `tests.align.test_r1_round8_exec_review` | Ran 7 tests in 33.726s; FAILED (failures=3) | 1 |
| `tests.test_run_night.Ruling76DriverTests.test_observer_faults_do_not_change_success_or_failure_chain_rc` | Ran 1 test in 0.259s; OK | 0 |
| `tests.external.test_km003c_parse` | Ran 43 tests in 0.126s; OK | 0 |
| `tests.external.test_km003c_monitor` | Ran 13 tests in 0.232s; OK (skipped=1) | 0 |
| `tests.test_km003c_parse` | Ran 3 tests in 0.000s; OK | 0 |
| **New** `tests.align.test_r11_review_sol2` | Ran 4 tests in 0.962s; FAILED (failures=3, errors=1), deliberately red | 1 |

The additional round-8 module's failures are:

1. `NightRepeatedSignalTests.test_signals_during_the_termination_do_not_cut_it_short`
   expects `"proven": true`; the log instead records `census_exit_3`,
   `sysmond service not found` / `pgrep: Cannot get process list` and defers restore.
2. `NightLockHoldingEscapeeTests.test_an_escapee_that_holds_the_lock_sees_no_restore`
   expects the later “could not be retaken” branch; the same failed group
   census defers earlier. The observation is consistent with safe refusal.
3. `R1RepeatedSignalTests.test_signals_during_the_runtime_kill_do_not_cut_the_close_short`
   gets `census_failed=True`, `proven=False`, `pipes_held_open=True`.

These are sandbox process-census limitations, **not established product
regressions**; the module cannot establish native termination/tree proof here.
Its other four cases passed. The scoped Ruling-76 selection passed separately.
Only test-owned synthetic children were signalled; no production job was
inspected or controlled manually. Logs and JSON command summaries are in
`/private/tmp/r11-review-sol2-tests/` (temporary, not committed evidence).

`PYTHONPYCACHEPREFIX=/private/tmp/r11-review-sol2-pycache python3.13 -m compileall -q joulewise tests`
passed, exit 0. No source fix was applied. No weights/downloads, network,
real restricted directory, external study root or measurement data were used.
Synthetic tests do not validate live USB/Metal, battery flow or a scientific FPR.
`git diff --check` also passed; the final staged whitespace check is recorded
with the local commit handoff.

## Handoff and outstanding judgments

Changed files are this review, the four intentionally failing witnesses and
`docs/run_reports/2026-11-07-r11-review-sol2.md`. Product, generated kit,
coordination state and raw evidence are unchanged. The local commit containing
these files is the review handoff; it is not pushed.

**Next exact step:** lead dispositions F01–F03, reconciles this independent
seat with Sol-1, records an agreement report and fixes/tests only under its
own authority. Preserve the scientific holds while obtaining the actual
series-plan margin/F/C/test roster and cap, U3 predictive/OC derivation, B
consequence, native WP19/transfer, mount audit, #694-on-#699 delta and sealed
transcript capture evidence. Then review/sign one exact integrated candidate.

Outside this sandbox the lead must rerun the three round-8 process/tree
checks with process enumeration available; run tiny synthetic
`tests.align.test_cache_checkpoint_native` and `tests.align.test_thermal_mlx`
with importability-gated MLX/Metal; and run the opt-in full WP22 integration.
Actual meter samples/clock coverage/custody/battery and WP19 tokenizer/history/
RNG/cache qualification require the owning clean, lead-controlled gate. They
are not completed by these green fixtures. Do not interfere with the ongoing
blinded job to obtain them.

Open judgments are F02's explicit zero-turn identity interpretation and the
intended treatment of the unexpectedly broad inherited review stack. No
claim is made about literature/venue freshness, actual attack capability,
outcomes, prior sessions' blindness or remote ref freshness.
