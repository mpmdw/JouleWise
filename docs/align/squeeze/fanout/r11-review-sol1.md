# R11 independent executing review — sol1

2026-11-07 PST; task/authority package dated 2026-11-08.

**Verdict: HOLD. Two HIGH findings and one MED finding, reproduced by five
failing-first synthetic tests. No product code was changed.** This is the
sol1 seat, not the second independent review or the agreement report. The
current U3/registration stops prevent W1 admission; the findings below do not
claim that this pending tree can currently arm.

## Reviewed candidate and authority

- Candidate: `origin/align/2026-11-08-v4-r11`,
  `c3796bf49256cb9243976915234f05c529657132`; local review branch
  `align/2026-11-08-v4-r11-review-sol1`, initially clean.
- Read `git log --oneline origin/main..HEAD`, the full changed-path/stat
  inventory for `git diff origin/main...HEAD`, and targeted source diffs.
  **Range limitation:** the literal comparison has **1,117 commits, 3,120
  files, 797,673 insertions and 18,420 deletions**. Its merge base is
  `d842f697f37a95a439dbb89927185b4b6e4fb1ea`. It contains substantial older
  Block/ALIGN development, not just this task's three pieces. I do not certify
  line-by-line review of all that historical material. Detailed review covers
  the named stack, `d600baba0..c3796bf49` (45 files), its runtime dependencies
  and the tests below. The lead must resolve this coverage gap before treating
  this seat as admission of the entire literal historical range.
- `origin/main` is `f48741f157685aa068465c7cb5e3c1f4af098e85`.
  **It does contain the requested authority.** My initial progress-message
  claim that the items were absent was a filtering error, corrected during
  the review. At this object: `RUN_STATE.md:1060` is item 212,
  `:1091` item 210, `:1098` item 209, `:1175` item 204 and `:1185` item 203.
- Adopted agreement: `4526de7d587a412073cf792c959090401e8d4797`, at
  **`docs/align/squeeze/AGREEMENT-FINAL.md`**, not under `fanout/`.
  Track 1 R01–R16 are lines 37–52 in that immutable object. R11-2's contrast,
  seed, U3, roster and rank choices are `origin/main:RUN_STATE.md:1063`–1067;
  D07/D09/D12 are lines 1068–1070; the meter ruling is lines 1071–1075.
- M0/workspace/stop-card/orchestration intake completed; the worktree's
  `RUN_STATE.md:6408` stop card is NONE. Explicit review and standing rules
  supersede ordinary queue selection, full-suite and coordination-write work.
  No network, external study paths, real measurement files, weights, MLX,
  Block-5 analysis, machine census or measurement campaign was used.

## Ranked findings and witnesses

### R11-S1-H1 — HIGH: the executable v4 U6 route still uses the superseded rules

**Authority:** AGREEMENT-FINAL R04 (`4526de7d5:docs/align/squeeze/AGREEMENT-FINAL.md:40`);
`docs/align/pilot_protocol_v4.md:455` requires ±0.5·s_r, trajectory-clustered
uncertainty, the imprecision label, and D position means with no turn-index
slope gate. The package calls chair 6 installed at protocol line 596.

**Execution evidence:** `scripts/align_v4_thermal_desk.py:113` obtains
`session_desk_evidence` and line 115 forwards its monitoring into
`window_report(..., v4=True)`. But
`joulewise/align/apple/thermal_desk.py:479` calls the legacy
`monitoring_stability`; lines 551–570 fit a turn-index slope, compute Welch
episode-half uncertainty, and decide using the slope plus
`.0037 * mean_episode_j`. `acceptance` line 645 and `window_report` line 807
accept that result unchanged in v4. The new clustered helper at
`joulewise/align/apple/v4_estimands.py:168` and position helper at line 205
are not wired to this route.

**Concrete failures:** twelve synthetic trajectories with the same
`[0,100,200]` residual pattern in both halves receive U6 FAIL solely from
the removed D slope veto. Conversely, an episode-half shift of 6 J passes
against 11.1 J (`.0037 * 3000`) without supplying the registered cell s_r at
all. That is neither the registered margin nor an unavailable/imprecise result.
The first case can wrongly bar a detection-rate claim; the second can label
unqualified stability PASS once D reporting becomes available.

Witnesses: `tests/align/test_r11_review_sol1_witnesses.py:42` and `:49` follow
the portable evidence → v4 report path. Both fail. The first allows
INCONCLUSIVE if the new inputs are unavailable; it does not demand PASS or
invent an s_r. The second requires INCONCLUSIVE when the registered scale
is absent. **Lead action:** implement/version the v4 route and missing-input
contract, preserve historical behavior separately, then re-run the actual
final-roster U6 OC. A passing isolated helper is insufficient.

### R11-S1-H2 — HIGH: fresh battery state is accepted without completed-top-up timing

**Authority:** adopted R02 requires completed-top-up timing as well as
InstantAmperage/SoC/OBC evidence (agreement line 38).
`docs/align/pilot_protocol_v4.md:602` says arm within about 30 minutes of a
completed top-up. No new numerical tolerance is proposed here.

**Execution evidence:** `joulewise/align/apple/v4_registration.py:158`–170
checks the current observation's `update_age_s`, SoC, current and OBC attestor.
It never accepts or validates a completion time/source. The caller at
`scripts/align_v4_session.py:255`–273 records current ioreg/pmset evidence;
the CLI at line 530 exposes an OBC attestor, but no top-up completion
evidence/attestation. UpdateTime freshness is not time since charging ended.

**Concrete failure:** a valid, one-second-old observation at 99%, on AC,
not charging and 0 mA returns `admitted=True` even when there is no record of
a completed top-up. An older/unknown charging history can therefore satisfy
this arm predicate and defeat the intended contrast-block top-up precaution
after the independent registration holds are resolved. The arm record cannot
establish that the timing rule was followed.

Witness: `tests/align/test_r11_review_sol1_witnesses.py:16` fails on that
missing-evidence case. **Lead action:** retain a source/time-bound completion
receipt or explicit operator attestation and refuse missing/stale evidence;
the lead owns its exact timing convention. This finding does not reopen the
unruled numeric B-window consequence.

### R11-S1-M1 — MED: H* silently changes actual dose identity and drops duplicates

**Authority:** adopted R15 (agreement line 51), protocol
`docs/align/pilot_protocol_v4.md:583` and R11 implementation record
`docs/align/council-2026-11-06-v4-review/LEAD-RULINGS-2.md:996` require actual
integer doses, strict exceedance and explicit undefined cases.

**Execution evidence:** `joulewise/align/apple/v4_estimands.py:23` builds
`{int(h): float(score) ...}` with no validation. This truncates doses and
silently retains only the last row for a duplicate. The carrier helper at
lines 83–90 correctly rejects these inputs; H* does not.

**Concrete failures:** `[(128.9, 2)]` at threshold 1 reports registered
H*=128 although that actual dose was not measured. Duplicate rows
`[(128,2),(128,0)]` erase a detected crossing and report no crossing, with
no conflict flag. This can corrupt the registered secondary estimand at an
import/join boundary; native integer token counting alone does not repair it.

Witnesses: `tests/align/test_r11_review_sol1_witnesses.py:58` and `:62` both
fail. **Lead action:** validate actual integer/nonnegative/unique dose rows
and grid identity before constructing H*. Reject or explicitly mark invalid
input; do not coerce/overwrite it.

## Q1 — fidelity to the R11 adjudications

**Not every adjudication is implemented correctly:** H1, H2 and M1 are the
specific reproduced gaps. The following separates implemented safeguards
from deliberately unresolved scientific/native work; pending does not mean
admitted.

| Item | Evidence and assessment |
|---|---|
| R01 | Receipt schema, exact artifact set, installed-ruling map, lead signature, both ADMIT gate reports, and committed/current digest checks: `v4_registration.py:58`–114. `align_v4_kit.py:1267`–1283 requires it. Pending receipt cannot admit. Gate content/actual execution remains the lead's responsibility. |
| R02 | Correct InstantAmperage, ≥99%, finite/missing checks and OBC attestor: `v4_registration.py:158`; numeric B bar withdrawn, `bar_pass=None` at line 252. **H2: completion timing absent.** |
| R03 | Descriptive PENDING export at `v4_registration.py:117`; unconditional refusal at line 147. No k=3/2.576 or operational energy floor. `thermal_desk.py:636` prevents a v4 fallback to v3's U3 margin. |
| R04 | U4 anchor demotion at `thermal_desk.py:643`, W1 U4–U6 unevaluable at line 810. **H1: actual U6 route contradicts the new rule.** OC and the U5 consequence remain pending (`pilot_protocol_v4.md:633`, `:721`). |
| R05 | 5/17 enforced by `v4_estimands.py:219`; alternate 18 remains unresolved in `v4_registration.py:235`–242. Final-policy comparison and qualified alternate recovery are still owed, not proved by these diagnostics. |
| R06 | Per-template delivery, eligible eight-row stage-adjusted fit, 3 df, positive d_X/d_Y and the existing rejection band: `thermal_desk.py:329`–377. Tests cover failure of one template's delivery. |
| R07 | Explicit supersession in `LEAD-RULINGS-2.md:919`; caps/negative-or-missing timing and predecessor disclosure in `align_v4_kit.py:644`; exact proof on both paths at line 940. WP19 partial X fails (`v4_registration.py:183`–189); both desks combine identity/cap predeclarations (`align_v4_thermal_desk.py:32`, `align_v4_session.py:203`). |
| R08 | Bare fallback rejected at `align_v4_kit.py:301`; passing duty labels require explicit no-X7 at line 401. Tuned S6 evidence bindings remain at line 968. No new 450-s/4-bit or budget-X7 waiver. |
| R09 | Checkpoint-off/all-transition accounting retained; `pilot_protocol_v4.md:645`, `v4_registration.py:258` rebuild prints. Cache and custody targeted tests pass; no native cache qualification claimed. |
| R10 | R0 record digest bound at `align_v4_kit.py:1029`; source/revision/runtime/policy identity at `v4_registration.py:211` and `v4_estimands.py:255`. Seed/tag deviation is explicit in `DEVIATIONS.md:14`. Actual stack/reference transfer and access chronology remain open. |
| R11 | Source/config/time-bound daytime receipt and explicit signed freshness at `align_v4_session.py:284`–353; no invented 24-hour default. Continuous mount-event qualification is expressly still missing (`pilot_protocol_v4.md:685`, `apply-r11.md:47`). An arm census alone does not close it. |
| R12 | Authenticated unobserved reference refuses before preparation (`thermal_gates.py:252`); observer SystemExit absorption with KeyboardInterrupt propagation (`scripts/run_night.py:2589`) retained. Targeted observer/custody checks pass. #694-on-#699 delta remains a pre-W1 lead gate (`origin/main:RUN_STATE.md:1100`–1105), not supplied here. |
| R13 | m≥39 **per pair** plus separate locked test, 42/35 loss arithmetic, prospective margin and all-condition cap/roster hold: `pilot_protocol_v4.md:556`–574 and `:836`. No D7/D8, ≥6-sabotage, or extra-window authorization installed. Exact fit/C/test roster and stopping OC remain unresolved. |
| R14 | Rank/strictness/FPR helper at `v4_estimands.py:49`; prospective maximum and legacy separation at `energy_residual.md:430`; public conditional wording at `energy-tripwire.html:154`. GPU legacy LOTO/full-fit scoring remains unqualified for the final D registration; it is not silently fixed by the new rank helper. |
| R15 | Untouched H=0, other-source exclusion, ≥40 for 39 remaining at .025, strict >, missing/nonmonotone crossings and fixed-threshold window bootstrap: `v4_estimands.py:70`–151. **M1: the separate H* path misses dose/duplicate validation.** |
| R16 | Chosen-B_D turn/count/digest admission and unresolved routing: `align_v4_kit.py:411`, `align_w1_budget_procedure.py:145`–171. No claim that the benign opportunity proves capability or an earlier blindness deadline. |

D07's .05 directly calibrated max, D09's assigned-attempt success-and-no-alarm
endpoint, and D12's time+monitor comparator are adopted **v5 design authority**
(`origin/main:RUN_STATE.md:1068`–1070). This Track 1 stack does not implement
or qualify those endpoints; v5 remains separately registered
(`LEAD-RULINGS-2.md:1007`–1011). I found no v4 monitor, joint endpoint,
threshold-budget change or extra exclusion implementing them prematurely.
The GPU residual's executable channel remains `powermetrics:gpu_power` in
`pilot_analysis.py:193`, `:213`–224.

## Q2 — blinding and release

No new transcript-monitor invocation, API scoring, sealed-outcome reader or
publication path was found in the reviewed three-piece stack. Protocol
`pilot_protocol_v4.md:743`–747 requires sealed, unscored full transcripts and
no v4 transcript monitor before v5 registration. The budget procedure's
explicit whitelist (`align_w1_budget_procedure.py:46`–80) reads timing/counts,
not energy, scores or semantic outcomes. It preserves the R10 blind selection
boundary.

The new DC values print only from the authorized session **desk**
(`align_v4_session.py:141`–162), not the structure-only night result or
courier; this is the expressly adopted print-only secondary analysis, not a
monitor score. The generic pilot desk remains a non-claim W1 diagnostic and
can render residuals (`align_pilot_session.py:353`–387). **This review does
not establish a qualified locked-D/v5 release mechanism or actual sealed
transcript capture**: those fan-out/native gates are not supplied by this
stack. Nor does a prose blindness declaration establish other sessions'
prior access (`DEVIATIONS.md:6`–8). No live/sealed input was opened to test it.

## Q3 — meter failures, custody and secondary scope

The reviewed failure paths pass. `km003c.py:88`–163 requires one aligned,
covering stream, matching RAW/monotonic offsets, no missing device counter
inside the member and no in-span/unknown-time protocol error. Missing spans,
baseline, samples, clock fit or coverage yield null DC values plus a per-member
flag. Stream hashes are checked against closing custody at lines 185–202;
bundle/parser errors stay in the member roster at lines 207–218. Unexpected
whole-desk exceptions become `meter.desk_failed:<type>` rows at
`align_v4_session.py:156`. No meter result is added as a rail instrument
gate; existing GPU exclusions remain independent. Synthetic gap/hash/parser,
unexpected-desk and shared-launch tests all pass.

There is one reader path: `joulewise/b5/driver.py:740` builds the production
reader command; lines 2442–2464 supervise it under the existing HAZARD_PACK
route. No second launch was added to the v4 session. The synthetic chain test
observes start before its first idle marker, stop after the last member,
one start/stop journal pair, closing trailer and stream hash
(`tests/align/test_km003c.py:247`). This is acquisition-path evidence only.

DC output explicitly says `SECONDARY / not yet registered`, `print_only=True`,
has no standardized score/decision, and uses a separate exploratory DC fit
(`km003c.py:21`, `:43`, `:224`–245). It neither calibrates nor substitutes for
the registered GPU residual. **Editorial ambiguity for the lead:** protocol
line 742 calls the DC integral “authority for small effects” within the v4
capture paragraph. Read that only with the later, explicit R11-3 restriction
(`LEAD-RULINGS-2.md:1004` and `origin/main:RUN_STATE.md:1074`): a qualified DC
claim endpoint belongs to v5. I did not treat that sentence as executable
permission to promote this diagnostic.

Actual meter samples, clock coverage, custody and battery flow remain native
gates. A synthetic launcher test or the device's physical inline position
does not establish those facts.

## Q4 — W1 readiness refusal

Missing/unreadable/disabled/changed meter declarations refuse before other
inputs (`align_v4_kit.py:1269`, `km003c.py:32`); messages explicitly cite
RUN_STATE 210 / squeeze. R11-3 adopts that meter lane; this older ruling
reference is traceable, not a second-reader design.

Pending inputs, R0/sensor identity, R1 budget/duty/turn evidence, sizing,
WP18 and committed exact-candidate Stage A/B registration remain required
(`align_v4_kit.py:1275`–1283). `generate(check=True)` invokes all readiness
gates at line 1650; install calls it before host operations
(`align_v4_session.py:392`). U3 is an unconditional R11/R03 refusal
(`v4_registration.py:147`). The committed receipt has pending status, empty
digests and PENDING gate verdicts (`registration/registration_receipt.json:38`).

Thus **the current tree refuses as intended**; there is no reported arm
bypass. Scientific/native items such as the margin/series roster, mount audit,
B-window consequence and #694 delta must also be reviewed in the real
Stage A/B gate content. They are not all independent automated predicates.
H1/H2 must be resolved before treating future signatures/native evidence as
proof that every adopted rule is executable.

## Q5 — execution record

Every unittest invocation was a separate process and ran sequentially. No
full suite, pytest, weights, native MLX execution or hardware probe ran.
All normal invocations returned 0. Times below are unittest's reported times.
Commands use the prefix `python3.13 -B -m unittest` unless specified.

| Selection | Exact result |
|---|---|
| `tests.align.test_v4_r11` | 27 tests, 0.249 s, OK |
| `tests.align.test_v4_registration` | 19 tests, 6.370 s, OK |
| `tests.align.test_v4_kit` | 116 tests, 5.807 s, OK |
| `tests.align.test_w1_kit_r10` | 30 tests, 6.709 s, OK |
| `tests.align.test_v4_estimands` | 14 tests, 0.002 s, OK |
| `tests.align.test_thermal_desk` | 24 tests, 1.151 s, OK |
| `tests.align.test_v4_w1_synthetic` | 18 tests, 1.459 s, OK, 14 full-WP22 opt-in skips |
| `tests.align.test_km003c` | 16 tests, 2.183 s, OK |
| `tests.test_km003c_parse` | 3 tests, 0.000 s, OK; `JW_B5_SYNTHETIC_ONLY=1` |
| `tests.external.test_km003c_parse.{UnwrapAndDropTests,ClockFitTests,EnergyTests,OffsetTests,FlagTests,ReviewRegressionTests}` | The six fully qualified selections in one process, 24 tests, 0.075 s, OK; `JW_B5_SYNTHETIC_ONLY=1` |
| `tests.external.test_km003c_monitor` | 13 tests, 0.256 s, OK, 1 real-meter skip; `JW_B5_SYNTHETIC_ONLY=1` |
| `tests.align.test_protocol_v4_doc` | 6 tests, 0.253 s, OK |
| `tests.align.test_window_reference_custody` | 5 tests, 0.572 s, OK |
| `tests.align.test_pilot3_cache` | 13 tests, 0.622 s, OK |
| `tests.align.test_thermal_gate` | 44 tests, 9.266 s, OK |
| `tests.align.test_r1_round8_exec_review.SwallowedSignalLatchTests` | 2 tests, 0.033 s, OK; `JW_B5_SYNTHETIC_ONLY=1` |
| `tests.test_run_night.Ruling76DriverTests.test_observer_faults_do_not_change_success_or_failure_chain_rc` | 1 test, 0.191 s, OK; `JW_B5_SYNTHETIC_ONLY=1` |
| `tests.align.test_r11_review_sol1_witnesses` | **5 tests, 0.006 s, FAILED (failures=5), exit 1** on final witness text; no product fix applied |

The parser class selection above expands to this exact command:

```sh
JW_B5_SYNTHETIC_ONLY=1 python3.13 -B -m unittest tests.external.test_km003c_parse.UnwrapAndDropTests tests.external.test_km003c_parse.ClockFitTests tests.external.test_km003c_parse.EnergyTests tests.external.test_km003c_parse.OffsetTests tests.external.test_km003c_parse.FlagTests tests.external.test_km003c_parse.ReviewRegressionTests
```

Normal checks total **360 passed, 15 skipped** (375 enumerated). The five
new failures are intentional review evidence, not counted as passes. An
earlier witness run also failed all five (0.005 s); two U6 assertions were
narrowed before the final run to avoid demanding an invented scale/PASS.
Total test time stayed below a minute, far below the 20-minute budget.
Recorded-fixture parser tests were **not run**, because they open real probe
recordings; only synthetic parser classes were selected. Real meter smoke
was forced off before device discovery. Full WP22 was not opted into.

`python3.13 -m compileall -q joulewise tests` and `git diff --check` passed.
No claim is made that green synthetic tests are MLX/Metal or live measurement
qualification. After the concurrent blinded job and under the lead's clean
machine gate, run tiny native `tests.align.test_cache_checkpoint_native`,
`tests.align.test_thermal_mlx`, all-turn WP19 tokenizer/history/RNG checks and
the qualified battery/meter clock/coverage/custody/mount experiments. Do not
load production weights or read sealed Block-5 data for these witnesses.

## Handoff

Changed only this report, its dated run-report pointer and
`tests/align/test_r11_review_sol1_witnesses.py`. No coordination state or
product files changed. Local commit only; no push. The commit containing
this report carries the review/witnesses together.

Next exact step: lead obtains sol2's independent report, dispositions H1/H2/M1
and the historical-range coverage limitation, then writes the agreement
report before issuing any scoped implementation work. Keep U3, actual
fit/C/test rosters and margin/OC, final scorer exchangeability/dependence,
B-window consequences, full-span mount audit, transcript capture and native
identity/acquisition gates pending. The exact s_r unit/cluster convention,
top-up completion evidence convention and final release design are lead-owned;
this review does not choose them or relax the holds.

**NEEDS_RULING — comparison coverage.** Question: should admission cover the
literal 1,117-commit historical range, or the 45-file three-piece stack over
`d600baba0`, with earlier work covered by named prior gates? Options considered:
complete the literal historical re-review; explicitly scope this round to the
three pieces; supply a corrected shared baseline. Recommendation: the lead
names the intended baseline and prior-gate evidence, and commissions any
remaining review under that explicit scope. Blocked work: certification of
the entire `origin/main...c3796bf49` range. The five witnesses and bounded
review are complete and do not depend on that ruling.
