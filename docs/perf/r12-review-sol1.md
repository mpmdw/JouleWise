# R12 v4-lean adversarial review — Sol1

Review branch: `perf/2026-11-08-r12-review-sol1`; base/main
`3809bdd14da5882659f17dc292200d4afbbd1579` (item 214). Documentary review
only. No registration, measurement, code change, or scientific gate admission.

**Recommendation: retain the lean measurement design; amend B2 and B3 before
W1 registration.** The R1 scheduler correction is real and operationally
relevant. B1's arithmetic is right, but its runtime saving is unmeasured and
early completion already has implementation support. Counts-only stopping
can preserve alarm blinding; it does not establish score exchangeability or
finish R13/R14.

## Verdicts

| Item | Verdict | Severity / reason |
|---|---|---|
| R1 batch-bound correction | **KEEP** | **HIGH:** the 61,607 s figure understates one encounter, and existing instructions explicitly use it to size an enforced deadline. Call 67,371 s a corrected one-encounter subtotal, not an end-to-end bound. |
| B1 terminal-completion windows | **KEEP** | **MED:** 40,527 s programmed span and 59,520 s authorized ceiling are correct planning quantities. Preserve authenticated terminal release, custody, quiet admission and the ceiling. No observed five-hour runtime saving established. |
| B2 triage before the next arm; full desk on laptop | **CHANGE** | **HIGH:** preserve the placement improvement, but enumerate every next-window-dependent check. Existing thermal escalation and cohort rules cannot silently become non-gating. A five-minute complete triage has no timing evidence. |
| B3 count-based stop, minimum six / cap eight | **CHANGE** | **HIGH:** prospectively freeze order, roles, final eligibility, both-pair predicates, cap accounting and failure disposition. Qualify selection/exchangeability under that rule; do not call R13/R14 settled. |
| Retained anchors, contrasts, gates, idle, scaffold and physical setup | **KEEP** | No source establishes a valid faster replacement for this v4 cohort. The remaining timing targets are scenarios. |
| Other synthesis arithmetic / attribution | **CHANGE** | **MED/LOW:** correct the sabotage-inclusive expectation, R1 campaign subtotal, D-only idle saving, and treatment of fit-support costs and seat agreement below. |

Severity describes the consequence if the proposition is used to register or
arm; it is not evidence that an actual window failed.

## Source pins and citation convention

The v4 implementation is absent from this pruned main tree. Citations below
mean `git show <pin>:<path>`, with line numbers in that blob, rather than files
in an external checkout. All sources were local Git objects or this clone's
documents. Absolute measurement/model paths in source text were not followed.

| Key | Pin | Source |
|---|---|---|
| MAIN | `3809bdd14da5882659f17dc292200d4afbbd1579` | `RUN_STATE.md`, especially items 202, 204, 212–214 |
| SYN | `55029b860adc775fc2ef10a8f9aff19f30af05d2` | `docs/perf/2026-11-08-latency-synthesis.md` |
| L1 | `d9f443db67794a74b4e51c0535d2e1fd51f995ad` | `docs/perf/LATENCY-AUDIT-sol1.md` |
| L2 | `80ba796621ca369126f6a92b9b5f7034c9c65a1c` | `docs/perf/LATENCY-AUDIT-sol2.md` |
| W1 | `05aec5b13856f73e04d532fc25b5f79e79076517` | `docs/perf/WINDOW-EFFICIENCY-sol1.md` |
| W2 | `8dc931d1813714c134df6add4716e28c5bdb9d57` | `docs/perf/WINDOW-EFFICIENCY-sol2.md` |
| R1 | `e901eb2a480d51377a494be9d797733dfcd0220b` | Integrated R1 code specified by item 202 |
| KIT | `d600baba029f70592bb8e792098338e4cd6811d3` | W1 kit snapshot used by both window seats |
| REG | `6daa3d6573412b90ad3f8d5007dbf1eaa8177218` | Later v4 registration lane |
| R11 | `c3796bf49256cb9243976915234f05c529657132` | R11 integration lane; later authority reconciliation, still incomplete |
| AF | `4526de7d587a412073cf792c959090401e8d4797` | `docs/align/squeeze/AGREEMENT-FINAL.md`, Track 1 R13/R14 and A06 |

R11 is inspected as a candidate implementation, not asserted merged or
registered. R12 the lead ruling is distinct from AF's row also named R12.

## 1. R1: correction confirmed, deadline dependency found

**HIGH — KEEP the warning; correct its scope.** At R1
`scripts/align_r1_rehearsal.py:980–996`, `finish=t+expected_s`; any overlap
with today's/tomorrow's blackout makes the function sleep to its end.
For blackout `[s,e)` and segment bound b, an arrival just after `s−b`
waits almost `b+(e−s)`. This is a supremum, not necessarily an attained
maximum: exact finish at 11:45 is admitted by the strict `finish > s0` test.
`_segment` supplies the whole attempt bound at `:1064–1073`, and journals
the wait at `:1080–1082`.

For the default step-D bound:

```text
member = 1750 + 1.13544*1580 + 120 = 3663.9952 s
b_D = member + 1200 + 300 + 600 = 5763.9952 s
one encounter wait < b_D + 5400 = 11163.9952 s
phase subtotal + that allowance = 56206.9616 + 11163.9952
                              = 67370.9568 s, rounded up 67371 s
```

The actual pure scheduler, with an injected clock/sleeper, waits **9,900 s**
from 10:30 PST on November 8 to 13:15. A boundary probe approaches
11,163.9952 s. Neither probe slept or ran a runtime. The source formulas
are at R1 `scripts/align_r1_rehearsal.py:126–156,1314–1354`.

The helper's `batch_window_wait_max_s=5400` and
`with_one_batch_wait_s=61606.9616` are therefore mislabelled. However,
**67,371 s is not a replacement universal R1 bound**. Brackets and harvest
are explicitly excluded (`:1319–1321`); calibration retries add
29,055.9808 s, quiet-load redos add attempts/releases and can change the
admission bound, and multi-day execution may hit another blackout. The
unresolved four-member idle accounting caveat is also documented at R1
`docs/align/r1_runtime_contract.md:95`. No claim here proves all segment
caps themselves bound every runtime path.

**There is a real reliance path, even without a programmatic caller.** A
targeted search of R1 `scripts/` and `joulewise/` found the table helper and
its returned keys only in its definition. The R1 shell wrapper simply invokes
the rehearsal (`scripts/night_chains/align_r1_rehearsal.zsh:49–53`). But MAIN
`RUN_STATE.md:1222`, item 202(3), explicitly tells the operator to set
`window_max_s` from **56,207 / 61,607 / 90,663 s**. R1
`docs/align/r1_runtime_contract.md:95` repeats that sizing instruction.
R1 `scripts/run_night.py:1152–1171` computes and starts the enforced stop
from `t0 + window_max_s + WINDOW_SHUTDOWN_GRACE_S`; its `_WindowDeadline`
class at `:815–840` explains process-group termination after the shutdown allowance.
Thus a plan authored from the printed number can cut the rehearsal early.
The operator schedule also depends directly on that text. The internal member
deadman is a separate bound; no use of this table to derive it was found.

**Lead action:** inspect the exact prospective R1 plan and its t0/segment
schedule in a permitted lead-controlled session, including bracket/close and
retry policy, before arming. This review deliberately did not inspect an
external or installed plan, so cannot certify its actual deadline. Do not
modify any running job on the basis of this report.

## 2. B1: right quantities, existing early-release machinery

**KEEP.** The correct default frame is four anchors plus eighteen D members
(two sentinels, fourteen fresh benign, two fresh sabotage): 22 executions,
16 fresh, seven prospective benign calibrators per pair. REG
`docs/align/pilot_protocol_v4.md:140–147,798–805` and KIT's sizing preview
support the planning inputs. At REG `scripts/align_v4_kit.py:1487–1491`,
the preview is explicitly `PROVISIONAL_NOT_ARM_SIZING`; actual W1 sizing
uses validated R1-filled member seconds at `:1105–1147`.

```text
D span  = ceil(3131.27 + 18*1800 + 4995) = 40527 s
D computed maximum = 60*ceil((40527+3300+7200+7200)/60) = 58260 s
Q4 authorized ceiling = 59520 s; additional headroom = 1260 s
W1 span = ceil(3131.27 + 4*1150 + 4*850 + 6*1800 + 4995) = 26927 s
W1 computed maximum = 44640 s
```

The validator actually checks the formula, rather than imposing a sleep:
REG `scripts/validate_align_v4_w1_plan.py:201–223`. With a 30–45 minute
turnaround the D planning cycle is **11.7575–12.0075 h**, about
**44.91–43.97 members/day**. These reproduce SYN's rounded numbers.
They are conditional occupied-Mac forecasts, not demonstrated elapsed times
or independent eligible observations/day. The 1,800 s member cost and 4,995 s
transferred scaffold are themselves allowances/estimates.

Static code resolves SYN D10 more directly than an R1 timing record:
R1 `scripts/run_night.py:1234,1409–1436` exits its supervision loop on
process completion, proves group closure on the applicable path, and returns.
The W1 template is `HAZARD_PACK` (R11
`configs/campaigns/align_v4/night_plan.template.json:190`). R1
`joulewise/arm_retry.py:259–286` and
`scripts/magistrate_watchdog.py:936–952,1034–1051` already support early
terminal release for that class, requiring terminal result, chain closure,
courier delivery and the watchdog's empty-process/census latch. Thus an
arbitrary terminal-looking file or direct-child exit is insufficient. Retain
these facts plus record commitment, quiet recovery and fresh arm checks.
Do not lower deadlines or claim the unused 18,993 s was previously consumed.

Changing the time-of-day distribution by running continuously changes the
sampling schedule even if each trajectory's protocol is unchanged. Freeze
the C/T schedule, blacklist/admission treatment and window order; address
window/time dependence under R14. B1 alone neither breaks score blinding nor
establishes exchangeability.

## 3. B2: off-host desk is sound; next-arm dependencies need a contract

**HIGH — CHANGE the blanket “desk output is non-gating” interpretation.**
Moving full computation to the laptop is supported by all four seats. A
98–103 minute historical desk/harvest interval is not a measurement of
100 minutes of removable pure analysis; L1 M23 says those activities overlap.
SYN B2's five-minute triage and the 30–45 minute total turnaround remain
targets. The latter includes finalize/hash/transfer, cooling, pre-arm and
quiet dwell, not just the triage script.

The retained rules have genuine dependencies on previous-window results:
R11 `docs/align/pilot_protocol_v4.md:487–505` retains X1–X8; U1–U3 failure
bars pool entry and applies an escalation **before the next window**;
U4/U5 can change remaining sentinel requirements. Any revised configuration
must be recorded before use and cannot be pooled across cohorts (`:543`).
These are broader than meter, battery and a committed record. R11
`scripts/align_v4_session.py:203–211` currently obtains U1–U3, battery-bar and
cohort checks from the desk. Its disposition map also explicitly leaves the
D-series desk gate unfinished (`docs/align/squeeze/fanout/apply-r11.md:40`).

Preserve B2's full-desk gates after W1 and after every code/configuration
change. For unchanged later windows, the lead must enumerate which results
are needed before the **next arm**, which only gate **pool entry/claims**,
and how a late fault is handled. Either move all next-arm predicates into
the mechanical/off-host pre-arm receipt, wait for those results, or write
an explicit prospective supersession permitting speculative collection under
the old frozen configuration. A fault must not trigger retrospective roster,
policy or eligibility changes. The accepted risk of losing the next window
does not by itself specify that contract.

**B2/B3 interaction:** a quick eligible count cannot finalize the calibration
stop while a later U3/identity/thermal desk can invalidate members or an
entire window. Allow provisional counts for scheduling, but finalize the
stopping decision only from the complete frozen eligibility evaluation.
Keep score/alarm outputs sealed from the scheduling decision maker. Record
all first outcomes and missingness; never silently replace a failed window.
No desk computation, hashing or evidence traffic may run on the measuring
MBP during acquisition or its qualifying quiet dwell.

## 4. B3: count-only is necessary for blinding, insufficient for validity

**HIGH — CHANGE; do not revert to an unqualified fixed count as a purported
statistical cure.** Nominal benign totals per pair are 42 / 49 / 56 after
6 / 7 / 8 windows. Six gives only three individual losses of slack; lose a
whole window and it gives 35. Seven leaves 42 after one lost window; eight
leaves 49, or `floor(49*.8)=39` after the stated additional 20% attrition.
These counts are right conditional on **all seven fresh benign/pair being
calibration**, not fitting or development. They justify capacity, not an
eligibility/exchangeability theorem.

### A prospective complete rule is required

Before W1, freeze a manifest of C1–C8 in a fixed order (or a frozen randomized
order), pair/condition/seed roles, eligible-member predicates and configuration.
Check only after each complete window and final eligibility adjudication.
At the first n in {6,7,8} satisfying **all** adopted per-pair conditions,
stop; if none does, return insufficient calibration/unresolved at eight.
Specify that lost/failed attempted windows consume capacity, and define the
treatment of zero-capture refusal before use rather than inferring unlimited
retries. Use every eligible calibrator from the retained prefix under a fixed
rule; do not pick the quietest 39. No reordering, discretionary skipping,
score-based extension, retrospective eligibility edits or re-promotion of F/T.
Freeze a distinct test roster; do not consume unused calibration reserve as
an improvised test or fit cohort. If interleaving is used, predeclare it and
keep test outcomes inaccessible until the allowed release.

R12 authorizes the 6–8 capacity choice, but cannot substitute for this manifest
and its scorer/eligibility implementation. AF R13/A06 requires both pairs,
all stop conditions, separate fit/C/T units and shortfall at the cap. R11
`docs/align/squeeze/fanout/apply-r11.md:49–50` correctly marks R13 OPEN and
R14 PARTIAL. The R11 registration artifact list
(`joulewise/align/apple/v4_registration.py:16–34`) binds W1 inputs/roster,
not a complete ordered C1–C8/T series manifest; its signature is not evidence
that an unspecified series rule ran.

### Eligible counts can select score populations

Eligibility depends on thermal timeouts, OS/PM state, missingness, identity,
deadman and window-level acceptance; these can share causes with energy
residuals and trajectory length. See R11
`joulewise/align/apple/thermal_desk.py:585–645` and the protocol at
`:487–505`. U3 also uses replay-energy comparisons. A scheduler can see
only a pass/count and still select on a variable correlated with scores.
Gating on “counts” is not the same as gating on an ancillary variable.

A synthetic counterexample illustrates the missing assumption. Independently
for each window, let a low-score state yield seven eligible benign/pair and
a high-score state yield six, each state having probability 1/2. At six
windows the 39 target is met iff at most three were high-state windows.
Conditional on stopping at six, the first window is high-state with
probability **8/21 = .381**, while a fresh test window is high-state with
probability **.5**. Thus even fixed order and no score reads can make the
stopped cohort's state composition informative. This is a constructed
dependence example, not evidence of bias in actual D data or a measured FPR.

Correlation alone is not an automatic invalidity theorem: under a stationary
iid candidate process, taking the first fixed number of eligible observations
can validly sample the common conditional law `score | eligible`, even if
eligibility and score correlate. One must establish that calibration and
test use that same law and compatible stopping/scoring. The current design
has clustered windows, possible time drift, adaptive admission and session
refits; the iid rejection-sampling argument does not establish it. A fixed
eight-window fallback removes one adaptive selection mechanism but does not
repair those other dependencies or outcome-dependent exclusions.

Qualify the actual scorer and selection rule using prospective assumptions,
window-level dependence/missingness sensitivities and synthetic null checks.
Retain availability and all-assigned denominators. A count-only scheduling
interface can preserve score blinding; it must not expose alarms, residuals,
threshold stability or energy-conditioned optional eligibility choices.

### R14 and fit/test costs remain blocking

R11 `docs/align/pilot_protocol_v4.md:576–592` explicitly leaves LOTO/full-fit
asymmetry, window dependence and final scorer wiring unresolved. The pure
rank helper (`joulewise/align/apple/v4_estimands.py:49–67`) states the same
assumption. At m=39, strict rank 38 gives ≤5%; maximum rank 39 gives ≤2.5%
under valid exchangeability. For m=39–56 the .025 helper remains the
maximum. Having enough observations does not make the assumed ranks valid.
If using leave-one-source-carrier diagnostics, ≥40 source carriers are needed
to leave ≥39 calibration scores (`pilot_protocol_v4.md:585–586`); this is
distinct from m≥39 for a new held-out test point.

SYN D4 overstates what choosing test-window fit supports could settle. W1
`WINDOW-EFFICIENCY-sol1.md:395–415` explicitly says matching training
cardinality alone does not prove exchangeability. W2 §4 likewise says that
if two of seven benign slots/pair become independent fit support, only five
remain calibration: cap eight gives 40 before losses, 35 after a whole-window
loss; **nine** would be needed for 40 after that loss. R12's cap must not
silently expand. Resolve the common scorer and actual roles first, then
recompute feasibility or return insufficient calibration under the adopted
cap. Three versus six test windows also purchases different honest/sabotage
sample sizes, not merely identical science at different overhead.

### Count-yield arithmetic

Under SYN's illustrative **independent 90% eligibility for every member and
pair**, with seven benign and one sabotage per pair/window:

| Windows n | Both benign counts ≥39 | Also both sabotage counts ≥6 |
|---|---:|---:|
| 6 | .147184 | .041569 |
| 7 | .984054 | .711490 |
| 8 | .999990 | .925258 |

These are cumulative completion probabilities, not probabilities of first
stopping at n. With compulsory cap-eight execution for cases unfinished at
seven, `E[N]=8−P(complete by 6)−P(complete by 7)`: **6.868762** for benign
only, **7.246940** including the sabotage target. Cap shortfall is respectively
about **0.00099%** and **7.474%**. No measured yield or iid evidence supports
either forecast. At an 11.7575 h cycle, expected savings versus eight are
about **13.30 h** and **8.85 h** respectively. Do not average these rules or
install the ≥6 sabotage target by citing its probability calculation. R12
does not resolve whether that target is adopted.

## 5. Other synthesis corrections and retained warnings

1. **MED — campaign bill carries the stale R1 number.** SYN §3 explicitly
   charges R1 at 17.11 h despite its corrected scheduler finding. For its
   seven-C/three-T scenario, replacing only that one-encounter subtotal raises
   **143.17–146.17 h to 144.77–147.77 h** for 30–45 minute turnaround,
   before the same omitted brackets/harvest, retries and fit qualification.
   The advertised roughly six days is a conditional scenario, not a deadline.
2. **MED — sample count is not the full bill.** Preserve W2 §4's explicit
   fit-support sensitivity, W1 §4's separate paid test supports and both
   seats' score-law caveat in the headline lean proposal. They are more than
   an unresolved choice costing exactly three extra windows. R13/R14 can
   change calibration yield as well as test shape. Do not claim an arbitrary
   scorer remedy fits the eight-window cap.
3. **LOW — B4 contradicts its own “anchors stay 300 s” condition.** SYN
   `:65` credits `22*180=3960 s`. Only eighteen D members change in that
   proposal: **3240 s**, giving D span **37,287 s = 10.3575 h**, before
   compensating G0 waits. Downstream B4/B5 rows must be recalculated. R12
   correctly did not adopt these changes, so no current design reversal.
4. **LOW — correct seat attribution and agreement strength.** SYN table #23
   attributes a code finding to L2, but L2's inventory also says at most
   5,400 s. W2 §2.4 supplies the adversarial code finding; L1 M16 and W1
   §2.5 carry the stale total too. Off-host placement has broad support;
   a blanket non-gating desk does not. L2 F1 explicitly says never arm across
   an unresolved desk-dependent gate. SYN openly identifies adaptive B3 as
   its own synthesis; retain that distinction from independently reviewed
   fixed-eight versus seven-plus-reserve proposals.
5. **MED — freeze the stopping rule before looking at early yield.** SYN D3's
   “settle: exclusion rate in the first two calibration windows” must mean
   evaluating feasibility under an already frozen rule, not choosing a new
   cap, extra stop condition, order, or cohort after inspecting those windows.
   A different rule requires prospective authority and an access-history
   disposition; those windows are not automatically reusable as untouched C.
6. **LOW — full token debit is not a universal realized runtime floor.** W2
   §2.2 explicitly qualifies 10,240/11.9 = 860.5 s as the protected full-use
   debit; early task completion can be shorter. Preserve that qualification
   in SYN's opening. It is appropriate for a worst-work admission proof,
   not proof each realized member must decode for fourteen minutes.
7. **KEEP — uncertainty and controls.** Preserve all four seats' separation
   of measured historical wall, provisional transferred law, caps and targets;
   W1/W2's unknown G0/G1/H and scaffold decomposition; immutable evidence,
   destination re-read, no overlapping MBP offload, no shortened final turns,
   native identity/thermal qualification and no pooling across configurations.
   Synthesis's engineering savings are overlapping resource-specific scenarios,
   not additive demonstrated MBP time. B1/B2 move critical-path work; B3 can
   reduce actually collected windows and therefore needs the stronger design
   argument above. No recommendation here invokes D-188 to waive v4 science.

## Verification, uncertainty and exact handoff

Ran `python3.13 -B /private/tmp/r12-review-sol1/check.py`: **PASS**, subsecond.
It AST-isolated the actual R1 scheduler/table functions and R11 rank helper,
injected literal default config dependencies and a fake clock/sleeper, and
checked scheduler boundary behavior, phase/sizing arithmetic, binomial count
OC, ranks and the synthetic count/score example. It imported no repo runtime,
model, test harness, study reader or hardware backend. The temporary script
is session-local; the formulas and pins above are the durable reproduction
specification. `git diff --check` passed. No unittest module or full suite
was needed for two documentation files; no network or measurement pipeline ran.

These checks establish code/arithmetic behavior only. They do not validate
the actual R1 installed plan, elapsed D timing, five-minute triage, eligibility
yield, exchangeability or native thermal/token behavior. No new MLX code was
written; no native test gate was closed. If the lead changes kit/runtime code,
the relevant outside-sandbox gates include
`tests.align.test_r0_mlx_native`, `tests.align.test_thermal_mlx` and
`tests.align.test_cache_checkpoint_native` on its exact pinned Metal stack,
plus the actual controlled R1/W1 protocol gates. They must not run in this
session or compete with the blinded job.

**Next exact step:** lead adjudicates this seat alongside the second
independent Sol review; revises the prospective B2 dependency/late-fault
contract and B3 ordered manifest/eligibility/scorer/OC; checks the R1 deadline
under permitted conditions; then presents the exact integrated registration
candidate for its required independent gates. Open choices are the adopted
sabotage count predicate, fit/C/T score architecture and capacity, handling
of pending desk eligibility, and the actual installed-plan deadline. This
report recommends changes; it does not exercise the lead's ruling authority.
