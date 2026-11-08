# v4 critical-path lookahead — Sol-2

2026-11-08. Seat: `perf/2026-11-08-critical-path-sol2`. Repository-only,
blinded, docs-only audit. **The next bottleneck is W1 admission, followed by
the missing D/calibration/test series implementation.** These are larger risks
than hashing speed. Have their synthetic launch-to-close paths ready while R1
measures; do not discover them at the next arm.

## Evidence boundary and version map

All references below are **local Git snapshots**, not claims about current remote
PR status or the live MBP. `V:path:line` means the named branch's file and line,
not the file at this report's main-based checkout. No network, weights, real
measurement directories, process census, hardware command, analysis pipeline or
test suite was used. Absolute data locators in configs were read as text only.
“Missing” means absent from the inspected repository route; an unpushed build or
an external operator record may exist but was not inspected.

| Prefix | Branch and inspected commit |
|---|---|
| M | `origin/main` @ `e7203f0ad11b479ad5b8ae945e01087a5c9518cf` |
| V | `origin/align/2026-11-08-v4-r11` @ `05b6d04cba4868531cc03da187689a3dc187e0eb` |
| L | `origin/perf/2026-11-08-latency-synthesis` @ `55029b860adc775fc2ef10a8f9aff19f30af05d2` |
| S | `origin/align/2026-11-08-ssd-permanent-agreement` @ `3799eacae61c9669d239ba0cca82fec5a91fcdf5` |
| H | `origin/align/2026-11-08-ssd-hooks` @ `a9261df4ddaa690a3ddd12785514b18bbfb8c05a` |
| E | `origin/perf/2026-11-08-eng-desk` @ `2fd82914cdea274c2662bc036d0be922608d3dde` |
| F | `origin/perf/2026-11-08-eng-finalize` @ `fdcc73d743d40d9b18ff1a56d81bb70302e3893c` |
| P | `origin/perf/2026-11-08-eng-prearm` @ `348c4a70bb213e63df9e0cabdcdd7ea38fa5f07f` |
| N | `origin/align/2026-11-08-v5design-ruling` @ `52e976dc928c30bb73bcb722ea5cca9dc37bae2c` |

Read intake: M `RUN_STATE.md` items 196–219, active stop card NONE, current
status/workspace/queue and do-not-do list; Mission M0; orchestration and D-181.
This task is the user's explicit off-Mac documentation priority. Coordination
state remains lead-owned. M `docs/decision_log.md:11918` permits back-to-back
quiet windows; it does not remove physical or evidence gates.

Two authority distinctions matter:

* The latency synthesis is a proposal. M `RUN_STATE.md` items 215–217 amend it:
  **eight fixed calibration windows**, not the synthesis's 6.87 expected or
  seven-window arithmetic; 67,371 s is the one-encounter R1 no-retry subtotal,
  and 96,427 s the retry floor, before brackets/close/harvest. Additional
  encounters/redos must be budgeted from the actual plan
  (`V:docs/align/r1_runtime_contract.md:95`).
* SSD-P1 and the v5 ruling remain **drafts**
  (`S:docs/align/v4/SSD-PERMANENT-AGREEMENT.md:3`,
  `N:docs/align/squeeze/v5-design/RULING-DRAFT.md:3`). Neither authorizes a
  hardware change. The installed v4 arm still forces external-volume status
  off (`V:scripts/align_v4_session.py:263`).

## Readiness inventory, from the next arm to release

**Status key:** EXISTS = a concrete implementation exists, not live-qualified;
PARTIAL = components exist but a gate, input or integration is missing;
MISSING = no complete owning route found. No row is certified runnable on the
live MBP by this audit.

Every collection row below inherits these prerequisites, designated **A**:
one reviewed executable checkout and exact-head passing PREQUAL; a concrete
plan/chain, sizing and ledger/identity pins; notice before install; fresh host
admission and clean agent census; display asleep and required dwell; sufficient
physical free disk; AC/battery/OBC evidence; correct frozen power mode and
restoration; meter samples/clock/custody; immutable terminal record and close.
The physical setup is Ed's: clearance ≥5 cm, ambient/thermostat recorded,
140 W MagSafe, top-up, OBC off, fixed cooler state and narrow powermode sudoers
rule. These are **unverified here**, not missing merely because private receipts
were deliberately not read (`V:docs/align/v4/PREQUAL.md:62`,
`V:docs/align/v4/PREQUAL.md:173`,
`V:docs/align/pilot_protocol_v4.md:1033`,
`V:docs/align/pilot_protocol_v4.md:1042`).

| Step | Prerequisites, route, receipts and decisions | Exists now / end-to-end assessment |
|---|---|---|
| **R1 arm and launch** | A; passing R0 with selected effort and provisional sensors; WP18 fixtures; runtime entrypoint; R1 plan with actual retry/blackout budget; independent executing arm review; magistrate's own synthetic replay. Chain → `align_r1_rehearsal.py` → `align_r1_runtime.py` → production benchmark/thermal path. | **PARTIAL, presently blocked in M.** Item 218 says R0 passed and the R0-fill lane contains `medium`, TV0h/Tf08 and R0 digest; V still has null effort/R1 inputs (`V:configs/campaigns/align_v4/registration/inputs.json:104`). Driver/runtime exist (`V:docs/align/r1_runtime_contract.md:3`, `:143`). M item 218 explicitly establishes that no R1 arm route exists; item 219 assigns Air Opus review. The announced `lane/2026-11-08-r1-arm` ref is absent from this clone's available remote refs, so its completion cannot be credited. A driver invocation or a fake workload is not that missing arm path. |
| **R1 acquisition, retry and close** | Accepted soak; model/stack identity; per-second CPU journal; 30B/D steps, A-B-A, designed start states, three gated D runs, X-G; authenticated step-D slots; host lock; brackets and harvest in the actual plan. | **EXISTS below the missing launcher.** Phase order `V:scripts/align_r1_rehearsal.py:495`; runtime reads authenticated step-D bytes before gated members (`V:docs/align/r1_runtime_contract.md:27`). CPU >0.5 core for 60 samples causes bounded segment redos, then refusal; missing journal coverage also refuses (`V:scripts/align_r1_rehearsal.py:869`, `:878`, `:1064`). Pure G0 timeout gets a retry/inconclusive path, not fabricated usable slots (`V:docs/align/r1_runtime_contract.md:98`). Cannot establish actual meter/bracket capture until the new route is supplied and checked. |
| **R1 → W1 evidence chain, on Air** | Closed copy of `r1_result.json`, per-phase bundles and `registration/r1_slots.json`; count exporter → X-G backfill → turn-count backfill → contrast derivation → R10 decision; copy authenticated soak reference; fill B_D/I_D/T_dead/thermal policy, power mode/classification/bands/chunk/hold/G0 fields and regenerate. Lead signs selected 1(f) branch. | **EXISTS mechanically, pending data and decisions.** Exact commands `V:docs/align/R1-TO-W1-CHAIN.md:23`. R1 lane omits X-G and per-turn fields expected by newer kit; backfills are necessary, not optional (`:5`, `:55`). Synthetic integration evidence only (`:78`). The note's `--check` does not produce U3, WP19, registration signature, the lead's decisions or W1 readiness by itself (`:51`). Preserve original slots; commit the derived backfill and source digests separately. |
| **R10 decision/fallback** | Measured minimum decode rate, released G0 waits, all three runs' completed-turn counts at chosen B_D, duty bar and tails; contrast fit; signed `ruling_1f_receipt.json`; deviation and independent review. | **PARTIAL.** Budget procedure and below-600-s D/independent contrast caps now exist in V, unlike M item 203's older description (`V:docs/align/pilot_protocol_v4.md:387`, `:710`). If 8-bit branch (a) fails, a name for fallback (b) does not build a runnable **R1-4bit** kit: current kit refuses 450-s/4-bit fallback steps (`:710`). Prepare that alternative route off-Mac now; lead/Ed choose from actual timing evidence. No assumption that branch (a) will pass. |
| **SSD decision before W1** | Ed/lead choose continued drive-free v4 versus a prospectively adopted storage-equipped configuration; final device/config/port/cable/placement; qualified collectors, receipts and arm integration. | **OPEN, two different routes.** Installed baseline forbids mounted external volumes and requires daytime verified offloads (`V:scripts/align_v4_session.py:244`, `:348`). Original presence qualification exists: five blocks, 120-s segments, 60-s gaps, 600-s settling; operator starts continuous powermetrics and physically changes presence (`V:joulewise/align/apple/ssd_qualification.py:76`, `V:scripts/align_ssd_qualification.py:13`). Its 24,600-s plan is ~6.83 h, not a 30–45-min gap. Proposed SSD-P1 instead costs 10.3–13.3 h plus full R1-S, and needs Ed's explicit configuration sign-off (`S:docs/align/v4/SSD-PERMANENT-AGREEMENT.md:25`, `:88`). These are alternatives, not two cumulative mandatory qualifications. |
| **SSD-P1, if adopted** | Ed's ~45-min setup, enrolled device/volume identity, all-volume unmount/noauto/locked replug; counter/log positive controls, quiescence Q, G1–G4/G6 pass, DCS-1 label; exclusive lease across hooks and measuring launcher; complete `ssd-closed.json`; full R1-S output becomes W1 authority. | **PARTIAL, not production wired.** Standalone hooks exist but operator card explicitly leaves production wiring/qualification to lead (`H:docs/align/v4/SSD-B-UNMOUNT-OPERATOR.md:3`, `:69`). Its “lose whole window/repeat W1” event description (`:45`) needs alignment with newer SSD-P1 IO/STATE/UNVERIFIED/config-break and fixed-eight accounting (`S:docs/align/v4/SSD-PERMANENT-AGREEMENT.md:55`). A mount-only census cannot prove device continuity. R1-S re-derives rates, sensors, bands, thermal/power decisions and budgets (`S:docs/align/v4/SSD-PERMANENT-AGREEMENT.md:205`). If signed before R1 starts, draft permits one R1-S instead of two R1 runs (`:227`); never touch a running R1. |
| **W1 registration package** | A plus post-R1 sizing/plan/slots; U3 derivation and implementation; WP19 native identity, cache/rewrite qualification; battery B consequence; qualified mount-event audit; U5 admission decision/updated OC table; all nine chair rulings; exact-byte Stage A/B ADMIT reports, anti-hindsight delta and lead signature. | **BLOCKED by code as well as evidence.** `require_w1_ready` actually calls all readiness gates (`V:scripts/align_v4_kit.py:1267`). **`validate_u3` unconditionally raises** (`V:joulewise/align/apple/v4_registration.py:375`); filling JSON cannot fix it. Protocol specifies the missing predictive/small-sample/dependence/transfer derivation (`V:docs/align/pilot_protocol_v4.md:619`). Receipt is pending, with null commit/artifact hashes and PENDING gates (`V:configs/campaigns/align_v4/registration/registration_receipt.json:1`); validator requires current and committed bytes, both ADMITs and a signature (`V:joulewise/align/apple/v4_registration.py:284`). No qualified full-span mount-audit route found; arm only takes a census. M's “nine rulings missing” is partly stale: text installed, evidence still pending (`V:docs/align/pilot_protocol_v4.md:595`). |
| **W1 native smoke, ≤45 min** | Reviewed final code head; dedicated labelled nonregistrable smoke plan; existing local native stack; same prepare/install/launch/custody/close seams; safe injected refusals; no production ledger contamination; passing PREQUAL including next-arm route. | **MISSING in inspected refs.** Announced by M item 219 on `align/2026-11-08-w1-smoke`; that ref is unavailable here. Existing WP22 is explicitly fake clock/SMC/PM/native stream, not native smoke (`V:scripts/align_v4_w1_synthetic.py:2`). It also does not establish the real `run_night` arm path. Scaffold alone is 4,995 s (~83 min), so ≤45 min cannot mean the unchanged full W1 campaign. Build a separate smoke plan and certify exactly which seams it exercises; do not quietly shorten registered waits or call a tiny-model smoke D qualification. |
| **W1 long window** | All preceding W1 gates; final W1 plan/sizing; `prepare` → `install` → shared pilot/BYTES writer/installer → HAZARD_PACK `run_night` → chain/campaign → terminal/courier. Per-arm OBC/top-up/offload/triage packets. | **PARTIAL route, blocked.** `V:scripts/align_v4_session.py:41`, `:573` wire prepare/install; shared prepare consumes `sizing_b5.json` and model paths (`V:scripts/bytes_h_session.py:297`). W1 roster is concrete, including 5/17 replay and optional 18 (`V:scripts/align_v4_kit.py:63`). R1-filled `w1_plan.json`/`sizing_b5.json` absent now. A successful `prepare` exit is insufficient: state can be `INPUTS_ONLY` after plan-writer refusal (`V:scripts/bytes_h_session.py:364`). Require STAGED, a verified plan and successful synthetic install/launch/close. |
| **W1 full desk / D1 clearance** | Closed W1 raw record on Air; real portable paths/export; token comparison R1 ↔ W1 5/17; capability/sentinel admission; U1–U3, battery B, cohort identity; thermal escalation/slot freeze and any required delta review. | **PARTIAL, deterministic blocker beyond U3.** `desk_diagnostics` always writes `bar_pass: None` (`V:joulewise/align/apple/v4_registration.py:509`); session desk uses `all(w['bar_pass'] ...)` as `v4_B_bar` (`V:scripts/align_v4_session.py:207`). Thus even clean battery data cannot currently make that check pass. Lead must rule B then implement it. CLI desk uses absolute session/plan/runs locators (`V:scripts/align_pilot_session.py:269`); E supplies a portable authenticated replay interface, still requiring a complete export/descriptor, not just a pushed summary (`E:docs/perf/2026-11-08-eng-desk.md:29`, `:88`). Full desk must pass after W1 (`V:joulewise/align/apple/v4_cadence.py:63`). |
| **D1** | A; passed W1 desk; charge hold by Ed; final D slot/cohort freeze; held-out seed/role manifest; qualified identical scoring law for fit/calibration/test; generated 22-member plan, per-window reference producer and sentinels. | **MISSING complete D route.** Protocol describes 4 anchors + 2 sentinels + 14 benign + 2 sabotage (`V:docs/align/pilot_protocol_v4.md:151`), but V generator loops only fixed W1 `ROSTER`, labels every generated member `held_out=False` (`V:scripts/align_v4_kit.py:1391`, `:1464`); session CLI offers no window/role selector (`V:scripts/align_pilot_session.py:438`). Hand-changing W1 would trip regeneration/receipt checks. Scorer wiring/common-shift oracle are explicitly pre-D1 work (`V:docs/align/pilot_protocol_v4.md:577`). |
| **D2** | A and same prospective cohort/role plan as D1; final prior-window triage, counts and sentinel/escalation choice; fresh seeds, new reference and reservations. | **MISSING same series builder/arm integration**, not a second scientific design. Must prove the second window really changes IDs, seeds, reference-source bindings, hashes and roots while preserving slots. R12 triage consumer exists (`V:joulewise/align/apple/v4_cadence.py:23`), but no production packet producer found. |
| **D3** | D2 prerequisites plus cumulative sentinel/U4/U5/U6 evidence from W1 and D1–D3; alternate sentinel/E_ref recovery if 5 unusable. | **PARTIAL arithmetic, missing production bridge.** `u4_reference` computes W1-inclusive E_ref/window count (`V:joulewise/align/apple/v4_estimands.py:245`). K-session consumer requires `v4_desk_evidence` or external adapter; no producer found in V scripts/ALIGN modules (`V:joulewise/align/apple/thermal_desk.py:438`). Session addendum labels every member `window='W1'` (`V:scripts/align_v4_session.py:185`). Without explicit D window identity and cross-window extraction, more captures do not make the cumulative check evaluable. |
| **C1** | D1 prerequisites; **prospective role mapping** of D labels to calibration slots and separate F/test pools; first counted C receipt. | **MISSING series manifest/route.** Fixed-eight rule exists; actual fit/C/T roster remains lead-owned (`V:docs/align/pilot_protocol_v4.md:557`, `:817`). Do not assume D1–D3 are three extra development windows: older default D1–D3 was the initial held-out plan. Mapping D1=C1 etc. requires the signed manifest. |
| **C2** | A, C1 role map; final triage, no duplicated seeds or calibration-source leakage; same frozen scorer. | **MISSING concrete generated kit**, shares D2 gap. `calibration_stop` consumes supplied rows, does not discover or validate a frozen roster (`V:joulewise/align/apple/v4_cadence.py:164`). |
| **C3** | Same; cumulative sentinel/state checks; no silent replacement for failed window. | **MISSING concrete kit and multi-window evidence producer**, shares D3 gap. U4 includes W1; anchors are print-only for v4 acceptance (`V:docs/align/pilot_protocol_v4.md:454`). |
| **C4** | A; fourth frozen slot, final counts by pair, cohort/pool/escalation decisions and next-arm packet. | **MISSING concrete kit/packet producer**; pure fixed-eight consumer exists (`V:joulewise/align/apple/v4_cadence.py:164`). No count-based early stop even if counts suffice. |
| **C5** | Same, fifth frozen slot; maintain all eligible calibrators and exclusion accounting. | **MISSING concrete kit/packet producer**, same gap. Per-pair maximum is seven eligible benign/window, not seven pooled across both (`V:joulewise/align/apple/v4_cadence.py:158`). |
| **C6** | Same; prior final-eligibility lag must meet prospectively settled rule before next arm. | **PARTIAL rule, M/V discrepancy to settle.** M item 216 says pending eligibility blocks from window 6. V protocol now allows provisional scheduling through 7, helper returns continue below 8 (`V:docs/align/pilot_protocol_v4.md:830`, `V:joulewise/align/apple/v4_cadence.py:224`). Fixed-eight amendment may explain the change, but no explicit disposition of the earlier from-six fence was found. Resolve before signing; do not treat a hand-written “pass” as evidence. |
| **C7** | Same; seventh frozen slot; final eligibility and cumulative count packet must be available before C8 decision. | **MISSING concrete kit/producer**, same gap. Retain failed/in-flight counted windows; zero captures alone do not consume a slot. |
| **C8** | Same; eighth counted slot; finalize all eight eligibility rows; both pairs ≥39; every eligible calibrator used; thresholds frozen before any test; stop/escalation outcome receipt. | **PARTIAL predicate, missing integration.** `calibration_stop` implements exactly eight, two trailing zero-capture escalation, pending-final/insufficient outcomes (`V:joulewise/align/apple/v4_cadence.py:164`). At cap there is no ninth counted attempt or ad hoc D7/D8 extension. After eight default windows 56/pair is possible, not promised. Fit-support deductions change that arithmetic and need a ruling (`V:docs/align/pilot_protocol_v4.md:843`). |
| **T1** | A; calibration_complete; prelocked distinct test roster, scorer/threshold digest and labels/access policy; test acceptance/failure policy. | **MISSING v4 test kit/runner and frozen role manifest** in inspected V. Triage can allow role `test`, but that is not a test plan. Three two-pair versus six one-pair windows remains an open lead/scoring decision (M item 214; `L:docs/perf/2026-11-08-latency-synthesis.md:103`). |
| **T2 / T3** | A and unchanged T1 freeze; successive locked windows; no test feedback into scorer, policy, eligibility or extra data decisions; all attempted outcomes retained. | **MISSING concrete kits**, same series gap. Do not reuse C rows as test. If six-window shape is chosen, **T4/T5/T6 inherit these same gates**; their plans must also exist before W1 registration, not be invented after T3. |
| **Finalize / offload / next arm — every window, including R1** | Proven all writers gone, terminal result/chain closure/courier and watchdog empty-process latch; hash immutable raw record, commit permitted records; verified destination copy, reserve next physical disk allocation; restore mode, cool/quiet, fresh arm evidence; no hashing/copy while next window measures on MBP. | **EXISTS core; PARTIAL optimized/portable loop.** Watchdog already supports terminal release (`M:scripts/magistrate_watchdog.py:1035`, `:1268`); do not sleep to ceiling. F supplies bounded hashing and operation-local reuse while preserving destination reread (`F:docs/perf/2026-11-08-eng-finalize.md:10`). No production timing claimed. V offload tool verifies configured copies; it does not supply a signed freshness policy (`V:scripts/align_v4_offloads.py:15`, `V:scripts/align_v4_session.py:324`). For SSD-P1 the shared lease and complete closed-record manifest remain integration work (H operator card `:52`, `:69`). Summary Git push alone does not transport the raw evidence the Air desk needs. |
| **Independent v4 recompute** | Frozen estimator/selection/eligibility/threshold contract; authenticated raw export, clocks, tokens, source/config hashes, all attempt/exclusion/role records; independent arithmetic and predeclared agreement bars; synthetic oracle and failure comparisons before release. | **MISSING v4 integrated command/comparison receipt.** ALIGN requires a second independent implementation (`V:docs/align/PIPELINE.md:76`). Existing `M:scripts/independent_recompute_b5.py:2` is explicitly block-5, with ALPHA/BETA model/ABBA schema (`:42`), not a v4 implementation. It was only read as code, never run. `v4_estimands` contains useful independent-check targets, not a raw-to-release independent pipeline. Build on Air; do not occupy MBP after capture merely to recompute. |
| **v4 release** | Independent agreement or disclosed unresolved outcome, final U/OC/cohort/attrition and FPR scope, immutable registered manifests, complete test seal and access log, privacy-reviewed shareable outputs, lead release ruling/signature. | **MISSING owning v4 closeout/release route and explicit completion checklist** in inspected V. Generic `M:scripts/release_check.py:2` exercises publication packaging/mock seams, not v4 scientific clearance. Freeze the release contract before collection; Air can perform release while MBP starts authorized v5 development. Release here does not mean publishing v4 reasoning transcripts; retain their seal. |

### The series-role ambiguity must be settled prospectively

Do not schedule **D1–D3 + eight C + three T** as if that were already adopted.
The old D1–D3 roster was 21 benign/pair total; Q6 and R12 replace that
insufficient calibration basis with fixed C1–C8 and distinct test units.
Conversely, do not silently spend three extra development windows and then count
their seeds as calibration. The signed series manifest must name each F/C/T
role, D alias, seed and reference source before W1. If separate D development or
fit-support windows are required to cure scorer asymmetry, budget them explicitly.
Three extra default cycles cost **35.27–36.02 MBP-calendar hours** before other
delays. The fit-support example in V leaves only 40/pair before a whole-window
loss and 35 afterward; the default 56/pair arithmetic cannot fund it
(`V:docs/align/pilot_protocol_v4.md:151`, `:569`, `:846`).

## Critical-path calendar and readiness deadlines

**Illustrative scenario, not a promised finish:** R1 starts **Nov 8, 08:00 PST**,
returns in the user's expected 16–19 h; W1 programmed span 26,927 s = 7.480 h;
each default C/T window 40,527 s = 11.2575 h; ordinary turnaround 0.50–0.75 h;
native smoke budgeted at 0.75 h after R1; first full W1 desk 98–103 min, overlapped
with ordinary cooldown/turnaround rather than added twice. R1→W1 derivation and
reviews are assumed ready to finish within that handover; **any excess is an
additional delay, Δ**, carried through every date below. Source durations and
desk estimate: `L:docs/perf/2026-11-08-latency-synthesis.md:57`, `:88`, `:113`.
These are programmed spans/targets, not measured D-series throughput.

No SSD qualification, R1-S, 4-bit qualification, extra F/development windows,
batch blackout during C/T, retry, charge recovery or new-code CI cycle is hidden
in this table. Those costs are stated separately below. Minutes are rounded down;
use earlier times as readiness deadlines, not the latest end of the band.

| Event | Earliest–later scenario (PST), plus Δ | Latest readiness to avoid idle |
|---|---|---|
| R1 start | Nov 8 08:00 | Arm route, reviewed synthetic end-to-end replay, exact-head PREQUAL and correctly sized plan **before this**; if not supplied, MBP is blocked now. |
| R1 terminal | Nov 9 00:00–03:00 | Air Stage A, U3/B implementations and decisions, mount/meter qualification plan, smoke/series-route builds **by Nov 9 00:00**. Target Nov 8 20:00 leaves four hours for repairs; that margin is a recommendation. |
| W1 arm | Nov 9 01:15–04:30 | R1-dependent slots, R10 receipt, WP19, soak copy, Stage B/lead signature and smoke pass **by earliest arm**. Static F/C/T roster/OC/test-shape decisions must already be frozen. Any new qualification or review overrun delays W1. |
| W1 terminal | Nov 9 08:43–11:58 | Export and portable full-desk route ready before close; D1 generated and synthetically launch-proven before this. |
| D1 / C1 arm, if manifest maps them | Nov 9 10:21–13:41 | Passed W1 full desk, charge hold, final slots/scorer/oracle and C1 packet. Every day these are missing leaves up to 24 h of MBP capacity unused. |
| D2 / C2 arm | Nov 9 22:07–Nov 10 01:42 | C1 triage and C2 immutable kit ready at its earlier terminal + 30 min. |
| D3 / C3 arm | Nov 10 09:52–13:42 | C2 triage; cumulative sentinel/window evidence producer operational. |
| C4 arm | Nov 10 21:38–Nov 11 01:43 | C3 triage and any registered sentinel escalation; C4 kit. |
| C5 arm | Nov 11 09:23–13:43 | C4 triage; C5 kit. |
| C6 arm | Nov 11 21:09–Nov 12 01:44 | Resolve from-six versus from-eight pending-eligibility rule **before W1**, not here. C5 evidence/C6 kit ready. |
| C7 arm | Nov 12 08:54–13:44 | C6 finality/cap accounting and C7 kit. |
| C8 arm | Nov 12 20:39–Nov 13 01:44 | C7 evidence; last fixed slot. Do not wait to build final-pool adjudication now. |
| C8 terminal | Nov 13 07:55–13:00 | Final C1–C8 eligibility/scorer/threshold procedure rehearsed; final data-dependent calculation begins now. |
| T1 arm | Nov 13 08:25–13:45 | calibration_complete and threshold/test seals. Any slow final adjudication/export adds Δ; no speculative T1 arm. |
| T2 arm | Nov 13 20:10–Nov 14 01:45 | T1 mechanical triage, locked T2 kit. |
| T3 arm / terminal | arm Nov 14 07:56–13:46; terminal Nov 14 19:11–Nov 15 01:01 | Locked T3 kit; independent recompute and release tooling tested **before T1**. Final release data only exist after this close. |
| Optional T4–T6 | T6 terminal Nov 16 06:28–13:03 | Adopt six-window shape before registration. Adds 35.27–36.02 h, not an after-T3 choice. |
| First v5 native development | after final v4 close/turnaround, subject to its own authority | G0–G2 software/decision package and native launch card ready **before Nov 14 19:11** in three-test scenario; it need not wait for off-MBP v4 arithmetic/publication. |

The 16–19 h R1 expectation **cannot size its kill deadline**. One-encounter
retry floor 96,427 s is 26.79 h, 7.79–10.79 h beyond that expected range, plus
brackets/close/harvest; per-segment load redos or further encounters can add more.
Keep the long reservation and release on authenticated completion. The watchdog
already supports this; a reservation is not a sleep instruction
(`V:docs/align/r1_runtime_contract.md:95`,
`M:scripts/magistrate_watchdog.py:1268`).

If SSD-P1 is chosen after drive-free R1: add its **10.3–13.3 h qualification +
R1-S**, at least 18.71 h for the specified no-redo/one-encounter subtotal plus
brackets/close/harvest. That is a **29.0–32.0 h one-encounter scenario addition**, with
retry reservation larger; no default Sunday-night W1 promise survives it. Ed's
availability also gates setup. Existing 6.83 h qualification is a different
presence-equivalence proposal, not a shortcut to SSD-P1. If the drive-free path
has enough verified physical space, unadopted permanent storage is not itself a
reason to hold W1. Decide its configuration before collecting cohort data.

## Ranked gaps, smallest correct build, and owners

“Hours at risk” is **exposure, not a probabilistic expected loss**. No build-time
estimate or live duration was measured. Overlapping blockers are not additive.
One missing next-arm prerequisite can idle the MBP 24 h per day indefinitely;
ranking then follows first encounter and recoverability. Captured time lost to
a late scientific defect is shown separately from idle time.

| Rank | Gap / first encounter | MBP hours exposed | Smallest correct build and owner |
|---:|---|---|---|
| 1 | R1 arm route / now | Entire 16–19 h expected capture cannot start; every unresolved day = up to 24 idle h | Finish existing R1-ARM-1, not a second framework. **Air desk** independently executes real synthetic arm→gate→chain→close, including refusal and deadline; **magistrate** repeats final route and installs; **Ed** supplies physical/sudo actions. |
| 2 | W1 scientific and executable admission / R1 close | Unbounded idle after Nov 9 00:00; filling receipts alone still fails | **Air desk/statistics + lead** derive/adopt U3 and B consequence, implement validators/desk consistently, settle U5 and full-span mount audit, finish WP19 and Stage A/B exact-byte signatures; rebase #694 per M item 209; combine final head once, then PREQUAL and native smoke. **Magistrate** verifies/install. No fabricated bar or waiver. |
| 3 | Series roles, scorer and D/C/T route / W1 close; choices due before W1 | At least one 11.76–12.01 h cycle missed per slot delay; invalid score/role design can strand **90.06 captured calibration h**, plus W1/test work | **Lead** settles F/C/T, D aliases, 3 vs 6 tests and same frozen scoring law/exchangeability limits. **Air desk** extends existing generator/session/desk with window identity, distinct seeds/roots/reference bindings, role manifests, cap ledger, U4–U6 producer, calibrated scorer and independent common-shift oracle. Rehearse W1→C1→C2→C8→T1 and zero/partial-capture failures before W1. **Magistrate** only executes frozen cards. |
| 4 | Storage configuration and physical offload loop / first capacity-bound handover | Original plan ~6.83 h occupied; proposed permanent setup ≥29–32 h addition after R1, plus any Ed wait. A late configuration change can invalidate an entire cohort | **Ed/lead** sign which path and device. **Air desk** adapts hooks to final SSD-P1, shared launch lease, event classes, closed manifest, qualified counters/logs and Q. **Magistrate/Ed** perform qualification and R1-S only if adopted. Otherwise automate authenticated copies/unmount and reserve space under existing rule. Setup is scheduled measurement/engineering time, not counted as “idle saved.” |
| 5 | Fast triage and portable evidence transport / every close | If 98–103-min desk remained serial instead of 30–45-min gap, extra **53–73 min/ordinary handover**; not all desk work is deferrable | **Air desk** land/adapt E portable replay, build source-digest-bound 14-check triage producer; export only needed closed evidence first, then bulk data, all MBP I/O before next measurement. Time the required eligibility/U1–U3/sentinel checks. Consumer currently accepts status+basis strings; a manual “pass” packet is no substitute for replay. **Magistrate** publishes terminal/export receipt and fresh physical checks. Full desk still gates after W1/code/config changes. |
| 6 | Battery completion, freshness, disk and mount-audit mechanics / each arm | Repeated refusals can consume the entire target 30–45-min gap or force a top-up; no measured frequency | **Air desk** build source/time-bound charge-completion journal and signed offload-freshness recipe; **Ed** OBC/charge hold and physical setup; **magistrate** fresh observations after expensive preparation. Lead must settle continuously floated battery semantics; do not relabel ioreg UpdateTime as top-up completion. |
| 7 | Finalize/hash and terminal wake / each close | Poll improvement ≤5 min/close; hashing saving unknown until native timing. Cannot claim 20–30 min saved from tiny fixtures | **Air desk** integrate F/P, keep independent destination read and default conservative workers; **magistrate** times closed synthetic/local nonstudy files in a gap, then selected worker count. Existing terminal release is retained; event marker is advisory. F native process-group verification remains owed (`F:docs/perf/2026-11-08-eng-finalize.md:95`). |
| 8 | Independent recompute/release / last test | **Zero necessary MBP idle** if Air has evidence and v5 is ready; otherwise administrative hold is unbounded | **Air desk** build independent v4 raw arithmetic/comparison and explicit release manifest now; **lead** owns final verification, privacy and release decision. Do not reuse B5 results or run its pipeline. |
| 9 | v5 first-native route / v4 end | Up to 24 idle h/day after v4 if development is still prose | **Air desk/lead/Ed** finish G0–G2 and decisions while v4 runs; **magistrate** receives a native G3/G4 launch card, actual kit and rollback/teardown test. Treat draft capacity/resource numbers as unqualified. |

Do not land optional throughput code on the measuring host mid-window. It can
turn a later arm into a code-change gate (new full desk/PREQUAL/smoke/review),
costing more than it saves. Batch compatible changes in the next already-needed
head, and keep all scientific choices prospective.

## Refusal risks worth fixing before they cost another window

These are code-based risks, not claims that the live Mac currently fails.
Correct physics refusals are not “spurious” merely because they lose throughput.

| Guard / concrete logic | Likely operational failure | Proportionate response |
|---|---|---|
| Old R0 0.05 core per-process rule / #694 integration | Normal macOS UI/dasd/softwareupdated bursts caused refusals already documented in M items 205–209. M item 209 warns a merge can silently resurrect contention refusal or skip the later long-window judgment. | Preserve R0-L3 flag/one scoped redo and actual sampler/stall/census checks; apply that exact rebase disposition. Replay recorded-shape CPU intervals synthetically. Do not impose an overnight clean-gap schedule again. |
| R1 blackout checks **whole segment bound** (`V:scripts/align_r1_rehearsal.py:980`) | A start well before 11:45 can wait all the way to 13:15; step-D bound + blackout is 11,164 s, not 5,400. This is predictable idle, not evidence of contention. | Correct sizing immediately. Collect phase wait receipts; lead may prospectively authorize narrower member admission after R1 evidence. No blanket scheduler policy for D windows was found here; do not assume R1's implementation applies to them or silently remove it. |
| R1 journal validity and sustained-load redo (`V:scripts/align_r1_rehearsal.py:878`) | >5-s sampling gaps or <0.9 Hz over the invocation can refuse even after a quiet decode; macOS command stalls/journal start timing must be exercised. | Test real-shaped delayed `ps`/child startup, bracket journal span precisely, distinguish unobserved from loaded. Keep fail-closed missing evidence; bounded retries apply to permitted segment load, not every malformed runtime result. Do not widen limits without a sensitivity/ruling. |
| G0 status/coverage and consecutive samples (`V:joulewise/align/apple/thermal_gates.py:529`, `:549`) | G0 requires 10 good samples, slow slope ≤0.2 °C/min, fresh PM Nominal/OS 0. A collector gap sets unobserved; a subsequent quiet sample does not erase missing evidence. Short budget-derived G0 caps can yield many clean X2s. | Native smoke must include delayed collector/status, no-status and recovery cases; start taps before admission and bind correct clocks. Print which predicate failed. Preserve X2/unobserved classification; only adopt the evidence-derived R10 cap, never a “just pass” timeout increase. |
| Top-up bound: 99–100%, not charging, absolute current ≤200 mA, update ≤180 s, completed top-up ≤1,800 s (`V:joulewise/align/apple/v4_registration.py:391`) | Back-to-back 12-h operation may remain floated without a new completion event. A 100-min post-W1 desk also makes an earlier completion stale. Fresh ioreg is not a fresh top-up. | Build a completion-edge/source receipt and do paper/static work first. If maintained float is to count, lead must prospectively define its dwell/flow evidence and amend the rule. OBC is explicit Ed attestation, not a parser guess. |
| launchd absent-service string (`V:scripts/align_v4_session.py:406`) | Requires rc 113 and one exact English stderr line. macOS version/domain/localization or transient launchctl failure can look like unknown state. | Capture supported-host examples off-window; test absent/present/wrong-domain/timeout. Add only observed equivalent absence forms plus bounded retry, keeping unknown state refused. Never convert all nonzero exits into “absent.” |
| PREQUAL exact head and model inventories (`V:docs/align/v4/PREQUAL.md:173`, `:233`) | Final integration/config changes invalidate old pass; venv path resolution can select bare Python; harmless top-level HF cache bookkeeping once broke pins. | Generate at the final clean measuring head with the unresolved venv interpreter; check execution closure and actual versions. Keep existing top-level cache exception, not broad ignore patterns. Snapshot tests should assert readiness invariants, not forever-pending literals (M item 218). No weight download is needed for this audit. |
| No-external-volume census (`V:joulewise/align/apple/external_volume.py:182`) and optional SSD hooks | Network/FUSE/disk images are external by design; transient diskutil already gets one retry (`:73`). Proposed hook flags *any* matching storage log row (`H:docs/align/v4/SSD-B-UNMOUNT-OPERATOR.md:45`), including benign rows, potentially losing a fixed-eight slot. | Remove irrelevant mounts/settings through Ed's setup; qualify parser/collectors on actual host. Reconcile hooks with signed event taxonomy and positive controls; UNAVAILABLE must stay unavailable, not “no event.” Do not adopt the old blanket whole-window loss as an accidental scientific policy. |
| B/U3 pending gates, INPUTS_ONLY, triage status strings | These can look like another finicky arm guard, but the missing code/science/plan is real. A superficially successful CLI or typed pass can conceal it. | Fix owning derivation and implementation; require STAGED + actual plan hash and real launch/close proof. No relaxation of registration/eligibility guards. |

## What waits are fixed, what already releases on conditions

| Wait | Code behavior / authority | How to accelerate without silently changing the estimand |
|---|---|---|
| End of window | **Condition-based already**: authenticated terminal result, chain closed, courier delivered, empty-process latch releases span; open chain always holds (`M:scripts/magistrate_watchdog.py:1035`, `:1268`). | Schedule successor on this event. Never wait for 59,520-s ceiling. P's terminal wake retains 300-s fallback and the same gates (`P:docs/perf/2026-11-08-eng-prearm.md:21`). This changes dispatch latency only. |
| Between-window “15–25-min cooldown” | M item 213 is an estimate of return to quiet state, not proof of a universal fixed sleep. Existing controller cooldown is sustained recovered power + nominal thermal + coverage with cap (`M:joulewise/controller.py:3805`, `:3893`). It is a per-repetition mechanism, not automatically an installed whole-window coordinator. | Compose the actual next-arm state predicate from existing evidence/physical gates. Use measured recovery, not an added mandatory 25-min timer. Prove predicate/coverage equivalence and no measuring I/O overlap; do not claim the generic helper already controls every inter-window wait. |
| R1 precool/post-D cooldown | **Condition-based with caps**: `idle-until-soak`, max 1,500 s; R+0 then gated block has only W1's configured inter-member idle (`V:scripts/align_r1_rehearsal.py:56`, `:495`). | It already returns on recovery. Ensure wrapper does not sleep unused cap. Shortening cap changes censoring, not necessarily wall time saved. Retain band/slope/coverage and report cap hits. |
| R1 soak | **Fixed 1,800 s**, last 1,200 s detrended slope/SD qualifies bands (`V:scripts/align_r1_rehearsal.py:518`, `:915`). Step response also observes a fixed 600-s recovery (`V:docs/align/r1_runtime_contract.md:162`). | Fixed information windows, not scheduler slack. Smaller windows need SD/slope/tail precision and coverage qualification prospectively; no present evidence supports shortening v4. |
| Per-member idle/warmup | **Fixed 300-s idle, 5-s warmup** in D config (`V:configs/campaigns/align_v4/stages/episodes-a/align-v4-episodes-a-e05.json:49`). Reference R uses last 60 s before warmup (`V:joulewise/align/apple/thermal_gates.py:468`). | 300→120 s would nominally save 3,960 s per 22-member D window, less extra G0 time. M item 214 explicitly keeps v4 default and moves paired 30B 8-pair/2–4-h comparison to v5. Needed evidence: randomized/matched predecessor heat, baseline R/power, G0/H durations, token/clock identity, replay mean/variance and eligibility/score law across durations and D qualification. Redefine no logged-compute/energy boundary silently. |
| G0 / G1 / H | **Condition-based**, not mandatory cap sleeps. G0 10 good samples; G1/H 5; band checks, G0 slow slope/Nominal/fresh status, finite caps/deadman (`V:joulewise/align/apple/thermal_gates.py:529`, `:566`). | Use S6's authorized band tuning with δ_slow≤2 °C and new passing gated evidence; preserve reference-state conditions. Do not subtract caps from calendar as though they were spent. Measure actual G0/G1/H and censoring first. Removing them changes reference-state energy toward continuous serving. |
| Display dwell | R0 launcher executes display sleep then **fixed 300 s**, with production admissibility tied to that dwell (M item 209; `M:scripts/launch_align_r0.py:184`). A future W1 smoke does not prove this is W1's installed launcher policy. | Turn display off before the last mandatory clean dwell where allowed, so overlapping evidence intervals can satisfy both requirements; do not double-count overlapping waits. A shorter rule needs native display-wake/WindowServer/ControlCenter and thermal/load settling evidence, recorded prospectively. Test-only override is not production authority. |
| Clean quiet dwell | `prewindow_check.sh --wait`: **fixed minimum 600 continuous clean s**, 30-s checks, any fail resets; comments explicitly say it does not substitute for T0's independent rule (`M:scripts/prewindow_check.sh:34`, `:185`). Packless interval admission instead has plan-supplied parameters; not a universal v4 shortcut (`M:joulewise/quiet_admission.py:21`). | Establish exactly which path the new arm route uses. Avoid sequential duplicate waits only when the same clean interval is actually accepted by both consumers. Shorter minimum/looser macOS daemon rule requires prospective justification and registered amendment where relevant. |
| Launch lead and watchdog | Shared prepare uses 420-s default lead, at least 300 s, rounded to minute (`V:scripts/bytes_h_session.py:45`, `:314`); watchdog poll ≤300 s, not physics. | Build packet off-host before preparing t0; remove avoidable activation work; adopt P event wake after native launchd test. Do not count this lead again if already inside the 30–45-min turnover. |
| Thermal/statistical/custody tails | Controller post-window sampling default **1 s**, with validation and closure role (`M:joulewise/controller.py:176`, `:2375`); calibration scaffold 4,995 s is aggregate, not one arbitrary wait (`V:scripts/align_v4_kit.py:57`). | Retain sampling support and disjoint timestamps. Phase receipts can find duplicated work outside measurement; scaffold reuse needs drift/acceptance qualification and prospective authority. M item 214 keeps scaffold for v4. |
| SSD waits | Original plan fixed 600-s/block settle, 120-s segments/60-s gaps; permanent proposal unmount + stable counters then frozen **Q**, calibrated/validated over cycles (`H:docs/align/v4/SSD-B-UNMOUNT-OPERATOR.md:60`, `S:docs/align/v4/SSD-PERMANENT-AGREEMENT.md:140`). | Permanent drive with automated offload removes recurring Ed plug/eject actions only after adoption/qualification. Use qualified state/counters and frozen Q; “unmounted” or silent logs do not prove constant watts. No assumed macOS disksleep/APST timing; no 3-block shortcut with zero residual df. |

Practical non-software actions: reserve Ed's next actual setup/charge/SSD window
now; keep ambient/stand/cable/port/cooler configuration fixed; leave the display
asleep and agent apps closed; disable the already-authorized indexing/Photos
sources through the operator setup rather than waiting repeatedly for them;
top-up while off-window copying/preparation occurs, finishing close enough to
arm to satisfy the actual completion rule. Prepare enough **physically free**
internal space for both raw and backup allocations. macOS purgeable capacity is
reported separately from statvfs free (`V:scripts/bytes_h_session.py:284`);
do not substitute it for a reservation. Full off-MBP desk, reviews and ordinary
compute can run while MBP measures; USB copying, hashing and magistrate activity
on MBP cannot.

## First v5 development steps to have waiting

N is a reviewed **draft**, not collection authority. It explicitly orders G0–G12
before v5 calibration (`N:docs/align/squeeze/v5-design/RULING-DRAFT.md:399`).
Other named v5 design branches are design inputs; their names do not establish
an integrated native launch route. “v5” in older D117/calibration paths also does
not establish implementation of this new squeeze experiment.

| First work | Prerequisites / current existence | Owner and deadline |
|---|---|---|
| **G0 threat/view contract** | Exact editable surfaces, helper permissions, receipts/A0–A13 crosswalk, matched carriers. **Draft exists; executable contract/registration not proved.** | Air/lead finish while v4 runs; before G2/native arm. `N:docs/align/squeeze/v5-design/RULING-DRAFT.md:403`. |
| **G1 API monitor pin + G11 spend** | Provider/version/prompt/view/parser/canaries, measured call/token price, Ed's cap; no v4 transcript scoring. **Decisions/qualification pending**, not authorized by this audit. | Air designs under existing authority; Ed cap before any paid calls. Draft open choices at `N:docs/align/squeeze/v5-design/RULING-DRAFT.md:429`. |
| **G2 synthetic harness → G3 native sandbox smoke** | Reduced-tool tasks, sandbox supervisor/escape and child teardown, edit/truth surfaces, forced twin, S collectors, consistent rerun view, synthetic leak/fault tests; native plan/arm/close card. **No integrated G0→G3 route demonstrated in inspected snapshots.** | Air builds/reviews during v4; magistrate runs one short native check only under new approved card. Ready before final v4 close, not after release paperwork (`N:docs/align/squeeze/v5-design/RULING-DRAFT.md:405`). |
| **G4 realistic-load/model route** | Gold/real-weight parity; model ladder choice; qualified final external volume; context/tools/cache/concurrent helper limits; no-swap/pressure, paging and tok/s receipts. Flash-Next gold reference existence is reported by M item 197, not native capacity validation. **Native gate pending.** | Port/Air lane prepares; magistrate + Ed execute, no overlap with v4. Draft deadline Dec 6 (`N:docs/align/squeeze/v5-design/RULING-DRAFT.md:407`). This audit downloads no weights. |
| **G5 capability; G6 replay; G7 timing** | Chosen model/thermal policy, per-pair capability attempts, exact honest/native twin replays, measured rerun multiplier/timing and launch kits. **Rules exist in draft; qualified measurements unavailable here.** | Magistrate captures, Air scores/reduces; lead adjudicates. Freeze package before spending native development time (`N:docs/align/squeeze/v5-design/RULING-DRAFT.md:408`). |
| **G8 DC-in closure; G9 resolution; G10 nonredundancy** | Final hardware, whole-member clocks/gaps/battery/tail/repeatability, sham and randomized replay placement; side-generation/CPU serial+concurrent doses; capped attack search and independent graders. **Open hard native gates.** v4 GPU fit and SSD idle-stable label do not qualify primary v5 DC-in. | Magistrate + Ed physical work; Air independent arithmetic/red team; lead decisions. Ordered before calibration (`N:docs/align/squeeze/v5-design/RULING-DRAFT.md:411`, `S:docs/align/v4/SSD-PERMANENT-AGREEMENT.md:95`). |
| **Capacity/registration before v5 series** | CAP-1 ≥10 consecutive v4 windows spanning ≥7 calendar days; CAP-1b ≥5 v5 development windows spanning ≥7 days; CAP-2 actual timing, yield, complete fit/C/test/release resource ledger; cold reviews/lead seal. **No live capacity verified here.** | Magistrate exports timestamps/status only, Air checks and lead rules. Do not delay fast v4 solely to make its calendar span seven days or assume six-day v4 proves this gate; missing qualifying evidence means HOLD for the dependent v5 schedule (`N:docs/align/squeeze/v5-design/RULING-DRAFT.md:367`, `:415`). |

## Handoff and verification

Only this report and its dated run report were added. No implementation,
measurement evidence or coordination state changed. No test was necessary for
this docs-only audit; no MLX/native behavior is claimed. Validation consisted of
Git snapshot/source-line checks, static code witnesses, independent schedule
arithmetic and `git diff --check` (results in the run report).

Native verification remains outside this sandbox and outside measurement windows.
On a checkout containing V and the final reviewed integration, the lead should run
these individually with the pinned native venv:

```sh
JW_ALIGN_MLX_NATIVE_TESTS=1 .venv/bin/python -B -m unittest tests.align.test_thermal_mlx
PYTHONPATH=. .venv/bin/python -B scripts/align_cache_checkpoint_native.py
.venv/bin/python -B -m unittest tests.test_run_night.HazardPackPrimitiveTests
```

The first two use tiny synthetic arrays/models and no weights/data; neither
qualifies D's real model generator, timing or memory. The first is opt-in and
skips without importable MLX (`V:tests/align/test_thermal_mlx.py:1`, `:18`);
the checkpoint script explicitly requires native Metal and the pinned stack
(`V:scripts/align_cache_checkpoint_native.py:1`). The process-group tests address
the native uncertainty recorded by F. In addition, execute the new R1 arm
runbook's synthetic route, W1 native smoke, and the physical gates above under
lead control; this audit supplies no launch authorization or made-up smoke command.

**Lead's next exact step:** turn ranks 1–3 into concrete delivery/check cards
before R1 closes: obtain R1-ARM-1 plus executing review; get the U3/B and SSD
decisions with named builders; require a synthetically exercised final W1→C→T
route and prospective series manifest. Schedule Ed's physical card explicitly.
This report proposes work and deadlines; it installs no scientific ruling.

Uncertainty to resolve: actual R1 start/phase times and retry policy; final arm
route and meter/brackets; U3/B/U5 rulings; SSD adoption and Ed availability;
scorer/F/C/T/test-shape authority; D1–D3 aliases; eligibility-lag rule; mount/log
collector native fidelity; actual export/finalize/triage latency and native
quiet/display behavior. Final verification and all live gates remain the lead's.
