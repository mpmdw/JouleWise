# Critical-path lookahead — sol1, 2026-11-08

Seat/branch: `perf/2026-11-08-critical-path-sol1`. Repository-only, blinded,
docs-only audit. **The next likely idle point is W1 registration, followed by
the absence of executable D/calibration/test kits.** R1's missing arm route is
already an acknowledged immediate blocker. A functioning W1 runtime does not
establish a functioning series.

The concrete catches are:

1. W1's `validate_u3()` **always raises**; supplying a signed JSON bar cannot
   clear it. A scientific ruling **and code** are needed.
2. The battery window desk always emits `bar_pass=None`; the session requires
   all those values to be true. Even an otherwise perfect W1 cannot pass its
   mandatory desk as currently implemented.
3. The R1 lane's output lacks fields the newer W1 kit requires. Export and
   backfill tools now exist on the v4 branch, but the operator handoff must
   actually run them, with source hashes, before kit admission.
4. R12 has a triage **consumer**, without a production packet-building command
   in the inspected ALIGN paths. Its thermal/eligibility entries still gate
   every arm; moving the full desk off the MBP does not remove those waits.
5. The series delivery consists of explicitly **non-executable** planning
   sheets, using an obsolete seven-plus-reserve/interleaved-v5 plan. The W1
   session remains hardwired to its W1 kit. There is no qualified complete
   D/C/T arm route in these sources.
6. Permanent SSD adoption is not a free operational shortcut: the current
   proposal requires about 10.3–13.3 h qualification **plus full R1-S**, and
   its hooks are standalone, unwired and based on earlier event semantics.
7. A v4 independent recompute/comparison/release route is missing in the
   inspected ALIGN implementation. The similarly named Block-5 programs do
   not implement this experiment.

Evidence for these statements is itemized below. None is a claim about live
results or about work that may exist outside the locally available Git refs.

## Source snapshot and meaning of readiness

All citations use `KEY:path:line` (inclusive ranges when useful); KEY expands
to the immutable local-ref snapshot below. These are Git-object citations,
not instructions to execute a cited command or follow an absolute data path.

| Key | Local ref | Commit |
|---|---|---|
| M | `origin/main` | `e7203f0ad11b479ad5b8ae945e01087a5c9518cf` |
| V | `origin/align/2026-11-08-v4-r11` | `05b6d04cba4868531cc03da187689a3dc187e0eb` |
| R | `origin/lane/2026-11-07-r1-kit-r0fill` | `d9d1098c6` |
| L | `origin/perf/2026-11-08-latency-synthesis` | `55029b860` |
| S | `origin/align/2026-11-08-v5-series-plan` | `b60c6b20e` |
| T | `origin/align/2026-11-08-v4-transcripts` | `a85c4b10d` |
| P | `origin/align/2026-11-08-ssd-permanent-agreement` | `3799eacae` |
| H | `origin/align/2026-11-08-ssd-hooks` | `a9261df4d` |
| F | `origin/align/2026-11-08-v5design-ruling` | `52e976dc9` |

**Exists** means source or a filled record is in that snapshot. **Partial**
means code exists but cannot clear all prerequisites. **Missing** means the
named artifact/route is absent in the inspected scope. **Native pending** means
this audit cannot certify the live receipt. These distinctions matter: V still
has `R0.reasoning_effort=null` and `sensors=PENDING_R0`, whereas R has the
mechanical R0 fills. Neither branch alone is a completed W1 delivery
(`V:configs/campaigns/align_v4/registration/inputs.json:100–106`;
`V:configs/align/v4/r1_runtime.json:14`;
`R:configs/align/v4/r1_runtime.json:14–18`; `M:RUN_STATE.md:1051–1079`).

The intake read M items 196–219, Mission M0, queue/do-not-do-yet, orchestration,
and relevant decision authority. This user brief overrides the normal
coordination-state updates and full-suite instructions. No state/kernel edits,
network, model downloads, hardware probes, real data, or measurement commands
were used. The two seats remain independent; this seat launched no other agent.

## Prerequisite inventory, from R1 through release

### Common prerequisites for every measurement launch

The following set is referenced as **A** in each measurement row below.

| Prerequisite | Exists now / executable end to end? | Owner and minimal completion |
|---|---|---|
| Exact runnable checkout, pinned interpreter, model/tokenizer identities, generated config/hash chain, complete plan with correct deadline, real prepare → install → launch → teardown | **Partial.** PREQUAL tests R0's launcher, kit and W1-plan logic, not an R1/D/T arm. `V:docs/align/v4/PREQUAL.md:117–132,173–176`; `V:joulewise/align/prequal.py:370–461,1002–1009`. Main item 219 adds arm-route existence as a requirement; its implementation is not in this PREQUAL runner. | Air desk supplies a stage-specific synthetic launch receipt at the exact final head, including rejection paths and terminal release. Magistrate re-executes it before installation. Preserve the venv interpreter path; the R0 regression was resolving its symlink (`M:scripts/launch_align_r0.py:335–340`). |
| Reviews and authority for that frozen code/protocol | **Partial.** R1's integration reviews exist, but R1-ARM-1 needs independent executing review and magistrate replay (`M:RUN_STATE.md:1045–1079`). W1 requires blind Fable + Opus protocol gates and lead verification (`V:docs/align/pilot_protocol_v4.md:1050–1058`). | Air performs reviews before the MBP becomes available; lead adjudicates. Do not make every unchanged window repeat code-change gates (`M:docs/orchestration.md:116–133`). |
| Agent-free host, no competing plan/loaded job, terminal release of predecessor, notice to Ed and opportunity for NO, STOP/fence, network time OFF, sleep prevention, physical setup | **Code/policy exists; native pending.** `M:docs/orchestration.md:116–133`; `M:RUN_STATE.md:38` (historical item 19, keep-awake instruction); `V:docs/align/pilot_protocol_v4.md:1033–1047`. Do not reuse historical checks as fresh native receipts. | Magistrate's short between-window activation; Ed for physical/OS/sudo setup. ≥5 cm clearance, ambient/thermostat recorded, direct 140 W MagSafe, OBC off, cooler fixed. Exit before capture. No agent activity or evidence transfer during measurement. |
| AC powermode and restore/host lock | **Implemented, native pending.** R1 A-B-A decides 0 or 2; W1 install declares, enters, reads back and restores it. `V:docs/align/r1_runtime_contract.md:118–137`; `V:scripts/align_v4_session.py:32–60,425–570`. | Ed's narrow sudo rule; magistrate validates marker/lock ownership. Known orphan/restore limitations remain explicit in contract lines 118,125,137; a new arm wrapper must not silently bypass them. |
| Battery top-up and fresh float, external-volume/disk admission | **Implemented predicates, native pending.** Required flags include `--obc-off-attested-by`, `--topup-completed-at`, `--topup-source`, `--w1-disk-config`; AC, ≥99%, not charging, ≤200 mA, observation ≤180 s, top-up ≤30 min. `V:scripts/align_v4_session.py:244–315,573–588`; `V:joulewise/align/apple/v4_registration.py:386–425`. | Magistrate obtains actual evidence, with Ed attestation where required. Keep default no-mounted-external/network/FUSE policy until prospectively changed. Current free disk must meet the actual reservation and floor, not just 80 GB (`V:docs/align/pilot_protocol_v4.md:1007–1012`). |
| Brackets, ledger pin/freshness, scaffold, meter capture and custody | **Shared machinery exists; stage binding/native proof pending.** R1 runtime `calibration-pre/post` only records host snapshots; the *outer plan* must supply real brackets (`V:joulewise/align/apple/r1_runtime.py:1580–1584`). W1/D requires the single supervisor-owned KM003C reader; no second reader (`V:joulewise/align/apple/km003c.py:21–40`; `M:RUN_STATE.md:1144–1160`). | Air pins all bindings in the complete stage kit. Magistrate checks actual samples, member coverage, clocks and battery flow, not merely a process exit. This is especially important for R1 if its new arm route is not HAZARD_PACK. |
| Full transcripts retained, sealed and unscored | **Separate implementation exists; integration/native qualification pending.** T captures raw completions, history and hashes after quiescence, before harvest. T does not provide a release/scoring API. `T:docs/align/squeeze/fanout/transcripts.md:13–61,109–121`; V lacks this module. | Air integrates T with registration dependency closure; magistrate verifies receipt presence/hashes after close. No reading/scoring transcript contents before the owning v5 registration. |

### Ordered steps and their additional prerequisites

Each measurement row requires A above. Off-box rows are included because their
output can block the next MBP arm; they do not require the MBP for computation.

| Step | Additional prerequisites, current status and end-to-end finding |
|---|---|
| **1. R1 arm and rehearsal** | **Immediate missing route in available refs.** R contains medium effort, TV0h/Tf08, fans and R0 journal digest; WP18 X/Y fixtures and WP15 argv exist. M item 218 records R0 PASS/complete_r0 and that DIAGNOSTIC registration, dry-arm and pilot session routes do not arm R1. `V:scripts/night_chains/align_r1_rehearsal.zsh:20–53` reaches driver/runtime **only once an outer arm actually launches it**. The announced `origin/lane/2026-11-08-r1-arm` ref is absent locally. Need its installed plan, bracket/harvest path, independent executing verdict, magistrate replay, PREQUAL and physical receipts. Use installed retry policy to size ≥67,371 s no-redo or ≥96,427 s retry floor **plus** bracket/close/harvest and applicable extra encounters; neither is a universal all-redos bound (`V:docs/align/r1_runtime_contract.md:92–98`; `M:RUN_STATE.md:1045–1079,1093–1114`). Expected 16–19 h is a planning estimate, not a kill deadline. |
| **2. R1 terminal → Air handoff → W1 budget decision** | **Tools exist; native outputs and integrated runbook missing.** Preserve immutable `r1_result`, slots, soak reference, classification/alias groups, per-segment load/battery/volume journals, three gated D runs, replay pair and X-G; verify host restored. The R lane omits X-G budget fields and per-turn completion/count evidence (`V:docs/align/r1_runtime_contract.md:96`). V provides `align_r1_turn_counts_export.py --run-dir RUN --out EXPORT`, including plain/.zst and missing-bundle-key discovery (`:1–24,68–134`), then `align_w1_budget_procedure.py backfill-x-g`, `backfill-turn-counts`, `decide`, `derive-contrast`, and lead `sign` (`:205–275,281–302`). Freeze S1–S9, I_D, B_D, L1 T_dead/tail, bands, G_turn/N_chunk, final sensor picks, powermode, duty verdict, whole-turn opportunity at the **chosen** B_D and digest-bound 1(f) receipt. No energy input to the timing decision. Kit checks these at `V:scripts/align_v4_kit.py:183–312,577–613,727–789`. Prebuild this entire handoff on R-shaped synthetic output during R1. |
| **2a. Conditional R1 remedy / R1-4bit** | **Incomplete fallback route.** Step-D/start-state INCONCLUSIVE refuses W1; remedy is R1 rerun under the existing ruling (`V:docs/align/r1_runtime_contract.md:98`). R10(b) requires a separate **gated** R1-4bit night and lead/Ed decision. An optional single `d-4bit` segment is not that night; `R:configs/align/v4/r1_runtime.json:12` is null, and the frozen 8-bit/300-s kit refuses fallback steps 2/3 (`V:docs/align/pilot_protocol_v4.md:710–723`; `M:RUN_STATE.md:1269–1280`). Missing: separate filled config/identity, gated roster, sizing, arm route, evidence contract and review. Air can prepare the synthetic route now; no model acquisition is authorized by this audit. |
| **3. SSD decision and optional native qualification** | **Decision needed; default can proceed without adoption if capacity/offload is solved.** V has `align_ssd_qualification.py plan/run/extract/evaluate`, fixed-work decode command and a five-block design, but live unit, operator steps and acceptance are pending (`V:scripts/align_ssd_qualification.py:13–19,68–103,149–180`; `V:joulewise/align/apple/ssd_qualification.py:76–124,423–454`). It is ~6.83 h programmed, longer for real decode/operator transitions. Its output allows B or C; it is not council/Ed adoption. Alternative **P is advisory until signed**: one-line Ed scope confirmation, lead supersession, enrollment/native G1–G6, counter/log positive controls, Q and full R1-S required (`P:docs/align/v4/SSD-PERMANENT-AGREEMENT.md:4,75–105,123–171,225–248`). H's CLI exists but requires a shared lease retained by the launcher, a finalizer-supplied complete `ssd-closed.json`, qualified collectors and production wiring; none is delivered by the standalone CLI (`H:docs/align/v4/SSD-B-UNMOUNT-OPERATOR.md:43–77`). H's “repeat W1/second event” prose at 45–51 predates P revision 2's fixed-8 event classes at 250–257: reconcile before use. |
| **4. W1 native smoke** | **Missing available delivery.** M item 219 announces ≤45 min, non-registrable native smoke before the first long window after code changes. The named `origin/align/2026-11-08-w1-smoke` ref is absent locally. WP22 exists but uses fake clock/SMC/PM/MLX and task; it does not prove native prepare/install/launch/close (`V:scripts/align_v4_w1_synthetic.py:1–10`). Need a labelled smoke plan/arm path, tiny/local synthetic model, registered expected outcomes for safe collector/gate faults, exact-head receipt and cleanup. Air builds/reviews; magistrate runs outside agent load after final integration. Any code fix after smoke requires the relevant rerun. |
| **5. W1 registration + launch** | **Blocked in code and artifacts.** Route exists in parts: `align_v4_kit` → filled `w1_plan`/derived `sizing_b5` → `align_v4_session prepare/install` → shared installer/HAZARD_PACK → launch_window/campaign → runtime → terminal → desk. Admission calls `require_w1_ready` → `require_registration` (`V:scripts/align_v4_kit.py:1267–1283`; `V:scripts/align_v4_session.py:41–60,538–588`). Missing at V: `w1_plan.json`, `sizing_b5.json`, `ruling_1f_receipt.json`, `u3_bar.json`, `wp19_receipt.json`, `r1_soak_reference.json`; slots/inputs are pending. Receipt has null commit/artifact digests, pending A/B gates and signature (`V:configs/campaigns/align_v4/registration/registration_receipt.json:225–252`). Required: Stage A R1-independent gate now; Stage B native delta + anti-hindsight commit list after R1; blind protocol gates; U3 derivation/OC/source bytes/independent gate; battery B window ruling; qualified daytime mount/unmount audit; U5 consequence ruling; all native setup/capture evidence. Rulings 4/5/6/9/11/15/17/18/20 are **installed in text**, not all scientifically/operationally closed (`V:docs/align/pilot_protocol_v4.md:595–751`). |
| **5a. W1 unconditional U3 stop** | **Missing implementation, not just a missing receipt.** `require_registration` calls `validate_u3`; `validate_u3` unconditionally raises, and `u3_margin` implements no margin (`V:joulewise/align/apple/v4_registration.py:331–383`). Scientific owner must admit predictive/small-sample/dependence/transfer treatment and series false-failure OC; Air then builds that exact validator/margin and oracle tests. No old k=3/2.576 default. This must be finished before W1 registration and smoke. |
| **5b. WP19 and warm-reference bridge** | **Source exists; receipts await R1.** WP19 renders all X/Y fixture turns with local tokenizer, verifies live X-G seed/turn IDs, binds tokenizer/config/input hashes (`V:scripts/align_v4_wp19.py:55–102`). Copy authenticated soak reference under registration. Partial/zero/divergent X-G must produce the ruled non-veto INCONCLUSIVE receipt, not certify unseen turns (`V:docs/align/pilot_protocol_v4.md:675–708`; `V:joulewise/align/apple/v4_registration.py:451–469`). Qualify raw/plain/.zst handoff: WP19 CLI reads an explicit plain turns file at line 90, unlike the counts exporter. Desk must materialize an authenticated logical copy if source is compressed. Lead owns native identity judgment and signature. |
| **6. W1 desk, final cohort and D1 clearance** | **Currently cannot pass battery check.** `desk_diagnostics` always sets `battery_windows[*].bar_pass=None`; `powermode_desk_check` sets `checks['v4_B_bar']=all(...)` (`V:joulewise/align/apple/v4_registration.py:509–515`; `V:scripts/align_v4_session.py:203–219`). Need the B numeric window bar/consequence ruling plus implementation before W1, because full desk must pass before D1. Also require W1 capability per pair, U1–U3, U5 disposition/tightening, admissible completed ≥3-turn sentinel, final-policy comparison, R1 pair + W1 5/17 E_ref, contrast report, frozen cohort. Only G0 cap, δ_slow, G_turn, N_chunk may change within D-17a; quantization/B_D/T_dead/4096/12 are already frozen. Changed configuration forfeits W1 reference use and needs an explicit recovery path (`V:docs/align/pilot_protocol_v4.md:206–210,498–506,656–673,725–729`). Alternate ordinal 18 is **not** a qualified substitute; matched reference/recovery missing until prospectively supplied. |
| **7. D1** | **No executable D kit/launcher delivery found.** Needs A, W1 clearance, exact frozen fit/C/T manifest, distinct ordinal/seed/config hashes, sentinel/reference and thermal slots, scaffold/ledger/meter/transcript bindings, D sizing and triage. S explicitly says its custom schemas have `execution_enabled:false`, runtime does not consume capture fields, and W1 validator does not validate D/T (`S:configs/campaigns/align_v4/series/README.md:3–6,18–33`). V's session still defaults to `kit.KIT`/`kit.PACK_ID`, not a selected series window (`V:scripts/align_v4_session.py:50–54,573–576`). Air needs a role-aware materializer/validator plus the real shared arm path, not renamed W1 files. |
| **8. D2** | **Same missing route**, plus finalized D1 record, final eligibility/escalation/cohort/sentinel decisions and next-arm packet. Must consume the next frozen seed allocation, never repeat W1 or replace lost fresh members. Full desk can be deferred only if unchanged code/config; its gating subset must already be ready (`V:docs/align/pilot_protocol_v4.md:777–815`). |
| **9. D3 and cross-window acceptance** | **Same missing route**, plus D1/D2 reports and R1/W1 reference for U4 at W=4 (W1+D1–D3), U5/sentinel action and U6 diagnostics (`V:docs/align/pilot_protocol_v4.md:449–506`). Old `v4_desk.md` is stale: it adds a ≤6 J anchor veto, different U5/U6 rules and an off-repo `k_sessions.py` adapter (`V:docs/align/v4_desk.md:31–64`). Current implementation/ruling supersedes it (`V:docs/align/squeeze/fanout/r11-dispositions.md:12–18,36`). Need one pinned multi-window CLI/manifest and independently checked current U4/U6 formulas; final-roster U6 OC is explicitly still owed. |
| **10. C1–C8: all eight calibration windows** | **Predicate exists; full schedule/kits do not.** Exactly eight counted windows, 7 fresh benign/pair/window, final m≥39 for both pairs; zero capture does not consume a slot, two consecutive zero captures escalate; insufficient after eight means stop, no ninth/top-up (`V:joulewise/align/apple/v4_cadence.py:155–230`; `V:docs/align/pilot_protocol_v4.md:817–862`). Require role/seed order, eligibility semantics, frozen scorer/fit-support allocation and capture routes before D1. D1–D3 are calibration in S's older plan (`S:docs/align/squeeze/SERIES-PLAN.md:44–56`); **do not add three windows to eight automatically**. Lead must name their mapping to C1–C3 or fund separate fit windows. S's seven+conditional-D8 and interleaved adaptive T plan is superseded/incompatible with V's fixed-8-before-test consumer. No scorer is qualified by count alone (`V:docs/align/pilot_protocol_v4.md:569–593`; `V:docs/align/squeeze/fanout/r11-dispositions.md:56–58`). |
| **11. Locked v4 test windows** | **Missing frozen roster/scorer/armable kits.** Need both-pair C8 final eligibility, thresholds frozen before test use, disjoint F/C/T roles/seeds, exact scorer for benign and sabotage, exchangeability/dependence qualification, missing/tie/strict-`>` rules and 3-versus-6-window ruling (`V:docs/align/pilot_protocol_v4.md:557–593`; `M:RUN_STATE.md:1115–1128`; `L:docs/perf/2026-11-08-latency-synthesis.md:101–104`). The old S T templates include adaptive attacks/real-compute controls belonging to **v5**, not an admitted v4 held-out test (`S:docs/align/squeeze/SERIES-PLAN.md:18–23,105–110`). Do not let a v5 injector/monitor become an accidental dependency of v4. Each test still requires A, the correct role-specific plan and terminal triage. |
| **12. Every window: terminal → finalize/hash/custody → offload → next arm** | **Generic terminal release exists; short end-to-end turnaround not delivered/proven.** Watchdog requires terminal shape, courier and empty-process latch, not only child exit (`M:scripts/magistrate_watchdog.py:937–952,1035–1058,2056–2057`; `V:docs/align/pilot_protocol_v4.md:764–785`). Harvest/desk route invokes the measurement view's `.venv` and absolute paths, archives/compresses before final checks (`V:scripts/align_pilot_session.py:269–337`). No one-command relocatable Air handoff/triage builder found in the inspected ALIGN scripts. Need immutable complete manifest (raw + scaffold + backups + transcripts), destination re-read/hash, recovery/idempotence, compact record commit, then any offload while no window measures. `align_v4_offloads.py` verifies a supplied offload config; it does not perform copies or generate `ssd-closed.json` (`V:scripts/align_v4_offloads.py:15–26`). W1 two-copy planning 37.4 GB, D 52.9 GB; actual whole-session reservation governs (`V:docs/align/pilot_protocol_v4.md:993–1012`). Without pruning/offload, eight D reservations alone total 423.2 GB; no disk sufficiency claim is possible from this audit. |
| **12a. Every arm: R12 packet and receipts** | **Consumer exists; producer/integration missing in inspected ALIGN scope.** Required list: `record_committed`, `terminal_completion`, `quiet_start_state`, `series_powermode`, `external_volume`, `charging_battery`, `meter_samples_clock`, `capture_faults`, `thermal_escalation`, `cohort_pool_rules`, `sentinel_roster`, `member_eligibility`, `calibration_stop`, `full_desk_gate` (`V:joulewise/align/apple/v4_cadence.py:23–152`). First three and meter/fault checks cannot be waived even before W1; only specified prior-v4 checks may be N/A for previous R1. W1 and any changed code/config force a completed passing full desk. Build a digest-bound gate-only Air extractor and packet writer from committed records; magistrate supplies live power/volume/battery checks. Current consumer trusts status+basis assertions; it does not itself authenticate their source records. Add that binding in the producer/review, rather than hand-type PASS. |
| **13. Independent v4 recompute** | **Missing ALIGN end-to-end program/contract in inspected refs.** Need source manifests, independent raw GPU integration/attribution, seeds/token identity, exclusions/eligible pools, frozen fit/scoring/thresholds/U checks/H grid and uncertainty, missingness/refusal behavior, comparison tolerances and machine-readable agree/hold. Build on synthetic raw bundles now, freeze before opening results, then run on an authorized Air copy after final custody. `M:scripts/independent_recompute_b5.py:1–17,42–46` is explicitly Block-5 with ALPHA/BETA/ABBA roles; it is not v4 support. Independence cannot mean calling the production estimator twice. No MBP arithmetic needed once authenticated copies exist. |
| **14. Release, publication and v5 handoff** | **Missing v4 release manifest/check/approval route.** Needs all admissibility records, final fixed-8 and test disposition, registered analysis at pinned code, independent comparison, deviation/attrition report, transcript embargo handling and explicit release authority. `M:scripts/release_b5.py:1–38` is a Block-5-specific sealed-digest/recompute/comparator path; `M:scripts/release_check.py:1–9` is a source/publication smoke. Neither releases ALIGN results. Lead should define a structure-only v4 gate that consumes the actual comparison and signs an immutable release record; Ed owns any reserved unsealing/publication action. Dec 10 is a planning deadline for using v4 in the capstone paper, not a completed release rule (`M:docs/research/research-strategy.md:5–8`). Keep v5 development independent of v4 release unless its source data genuinely require release. |

**Negative-evidence scope.** At V, `git cat-file -e V:<path>` failed for the
six named W1 artifacts, `series/series_plan.json`, and the candidate filenames
`scripts/independent_recompute_align_v4.py`/`release_align_v4.py`. The wider
readiness finding also uses `git ls-tree` of the ALIGN configs/scripts and
`git grep` for recompute/release/triage in `docs/align`, `scripts/align_v4*`,
`joulewise/align/apple/v4*`: no equivalent complete routes/producers found.
This is not proof that no differently named/private work exists. The announced
R1-arm and smoke refs were tested with local `git show-ref --verify`; both
were unavailable. No fetch was attempted.

## Critical-path calendar and latest-ready times

All times below are **PST**, anchored to a hypothetical R1 t0 of **Nov 8,
08:00**; move them by the actual t0 delta. This is a readiness deadline model,
not a launch authorization. The frozen source does not establish that R1
actually started. Use the earliest plausible finish to set delivery deadlines,
and the installed plan's conservative bound to protect a running measurement.

Planning arithmetic: R1 16–19 h; W1 26,927 s = 7.480 h; D/C/T default span
40,527 s = 11.258 h; ordinary turnaround 0.5–0.75 h, hence cycle
11.758–12.008 h. These spans are programmed allowances, not measured duration
or worst-case guarantees (`L:docs/perf/2026-11-08-latency-synthesis.md:9–12,70–80,113`).
The synthesis's adaptive stop is superseded by M item 217. Full desk after W1
is still gating and was historically ~98–103 min; it is charged separately
below. Bracket/harvest excess, retries and blackout waits add time.

| MBP milestone | Conditional timing | Prerequisites must be ready by / latest time without new software idle |
|---|---|---|
| R1 arm | Nov 8 morning | **Before t0**: real R1 outer route, actual plan deadline, exact-head PREQUAL/review/replay, setup, notice, agent exit. Missing this loses every elapsed hour immediately. |
| R1 close | Nov 9 00:00–03:00 nominal | Air code for the complete R1→W1 transformation, U3/B/scorer design decisions, Stage A review, smoke kit, Air-copy/finalizer and storage decision **by Nov 8 evening**, before earliest close. Native slots/Stage B can only finish after close; prepare everything else now. |
| SSD branch point | Immediately after R1, or before it if still unarmed | Ed's availability/choice and the selected path's code/reviews **before R1 close**. Default disconnected-drive path can avoid qualification if disk/offload is ready. P adds ~10.3–13.3 h + 16–19 h R1-S (retry bounds longer); if signed before R1 arms, P permits first R1 as R1-S (`P:docs/align/v4/SSD-PERMANENT-AGREEMENT.md:25–32,225–228`). Never interrupt R1. |
| Smoke, registration delta, W1 | Earliest model: W1 starts ~Nov 9 01:30–04:30, finishes ~09:00–12:00 | Allow 0.75 h smoke + 0.75 h handoff/arm as an **optimistic target**. U3 code, B rule, WP19/soak, filled sizing/receipt/gates and capture integration must already be complete; unmeasured Stage B time is extra. No claim these fit 90 min. |
| D1/C1 | Planning anchor **Nov 9 12:00–15:00** | Role/seed/scorer ruling, all series kits, synthetic arm replays, fast triage and Air desk path **before W1 closes**. W1's full desk + cohort/sentinel freeze must then pass. If W1 fails, use its registered remedy, not the calendar. |
| D2/C2 | ~Nov 10 00:00–03:00 | D1 gate-only result and packet within its 30–45 min turnover. No software development should begin here. |
| D3/C3 | ~Nov 10 12:00–15:00; closes ~23:15–Nov 11 02:15 | Multi-window U4/U6 reader, current-rule OC and any sentinel-roster resizing **before D3 close**. Prefer delivery before D1. |
| C4 | ~Nov 11 00:00–03:00 | Same frozen pipeline; next-arm decisions from D3 must be available before arm. |
| C5 | ~Nov 11 12:00–15:00 | Same; no repeated lead/build round trip for unchanged state. |
| C6 | ~Nov 12 00:00–03:00 | Same. M item 216 used a window-6 eligibility fence for the earlier adaptive design; V's fixed-8 consumer waits on provisional counts at eight. Reconcile runbook wording before C1, not at C6. |
| C7 | ~Nov 12 12:00–15:00 | Same; prepare final count/freeze package and test kits off-box. |
| C8 | ~Nov 13 00:00–03:00; closes ~11:15–14:15 | Final eligibility for **all eight**, role/scorer qualification, threshold-freeze producer, test manifest/arm path **before this close**. Eight shortfall is a terminal outcome; no improvised top-up. |
| v4 test T1 | If three default-length windows: ~Nov 13 12:00–15:00 | Exact 3-versus-6 cohort and F/C/T law must be ruled **before W1**, not now. Test role launcher, blind analysis and independent comparison should be rehearsed by C8 close. Final eligibility, threshold freeze and disjoint test seeds are required before this arm. |
| v4 test T2 | ~Nov 14 00:00–03:00 | T1 terminal/record/triage, unchanged frozen scorer/cohort, next disjoint test roster; no threshold/attack redesign from T1 outcomes. |
| v4 test T3 | ~Nov 14 12:00–15:00; final close ~23:15–Nov 15 02:15 | Same gates from T2; final test disposition and immutable analysis inventory ready at close. If six tests are chosen prospectively, T4–T6 repeat these prerequisites and add ~35.3–36.0 h. |
| Independent recompute/release | Air while MBP begins approved v5 development; wall time unmeasured | Programs, source inventory, comparison coverage/tolerances and release checklist frozen/rehearsed **before first test closes**, preferably before C1. Compute/review latency need not leave the MBP idle. |
| First v5 native development | First authorized gap after v4 collection, ~Nov 15 in the three-test scenario | Air G0–G2 and a reviewed short G3/G4 operator kit ready **before final v4 close**. No requirement to await v4 unsealing to develop synthetic harnesses. |

This calendar counts D1–D3 **inside** eight calibration windows, as in the
older allocation's role definition; the final mapping is a lead decision.
Three separate fit windows would add ~35.3–36.0 h, not disappear into the
eight-window bill. Six rather than three tests adds another ~35.3–36.0 h.
Both choices together shift completion about three days. A 26.79 h R1 retry
floor shifts the nominal calendar ~8–11 h plus brackets/close and additional
encounters. W1 at its 44,640 s ceiling rather than programmed span adds ~4.92 h;
each D at its 59,520 s ceiling adds ~5.28 h. **Do not reserve idle time to a
ceiling when the authenticated terminal release already occurred.**

## Gap priority: protect ready MBP hours first

Risk figures are opportunity-cost scenarios, not measured expected losses.
An unbuilt hard gate can idle the MBP indefinitely; rank uses proximity,
repeat exposure and rerun cost. Overlapping risks are not additive.

| Rank | Gap / MBP hours exposed | Smallest correct build / ruling | Who |
|---|---|---|---|
| 1 | R1 outer arm + deadline: **every hour now**; bad sizing can waste ~16–27+ h | Finish R1-ARM-1, complete plan including actual brackets/harvest, exact retry-bound calculation, synthetic real-launch replay, independent review, then native arm. Do not edit armed R1 measurement code. | Air builds/reviews; magistrate verifies/arms; Ed physical/sudo. |
| 2 | W1 U3 + B consequence + signed registration: first idle Nov 9; **one 12 h slot/day-scale stall**, potentially full R1 repeat | Admit the science now; implement U3 validation/margin and B verdict; Stage A before R1 closes; Stage B only native deltas; create/sign actual bound receipt. A JSON fill alone cannot fix either hard stop. | Air statistics/build; lead/cold gate rules; magistrate consumes. |
| 3 | R1→W1 exporter/backfill/budget fallback and native smoke: **hours of avoidable desk debugging**, ~16–27+ h if R1 must repeat | One tested transformation pipeline consuming lane-shaped and compressed records; count/completion hashes; R10 draft/sign/contrast; WP19 and soak; ≤45 min real-launch smoke at final head. Prebuild separate R1-4bit gated route if fallback is needed. | Air desk; lead/Ed on fallback; magistrate smoke. |
| 4 | D/C/T route, final roles and scorer: first idle after W1; **next ~12 h slot**, entire remaining ~129–132 h collection plan exposed | Materialize all eight C kits and separate tests, full seeds/ordinals/identities, role-aware validator/launcher, cohort/sentinel recovery, common-shift scorer oracle and prospective F/C/T ruling. Use existing shared launch machinery. | Air desk; lead/statistics/cold gate. |
| 5 | Disk/offload/SSD choice: **per-window wait for Ed** or lost arm on disk; P incurs **~26–32 h** extra after drive-free R1, before retries | Decide default disconnected vs fully adopted storage-equipped configuration before R1 close. Default: capacity and verified offload/operator schedule. P: sign/supersede, update H semantics, wire shared lease + finalizer manifest + ARM-SSD, qualify, run R1-S. | Lead + Ed decide/setup; Air builds; magistrate qualifies. |
| 6 | R12 fast triage / Air relocation / finalization: **~1.6–1.7 h per desk** if still serialized; for 11 default post-W1 windows ~18 h total | Portable immutable export manifest and rewritten session locators; gate-only extraction with equal verdicts; packet producer; bounded hashing/compression with destination verification. Keep the mandatory W1/change full desk. | Air builds/runs desk; magistrate finalize/export/arm only. |
| 7 | U4/U5 extra-sentinel/recovery path: possible **whole-window loss/reselection** and next-arm dead end | Prebuild both base and +2-sentinel sizing. At 1,800 s each, +2 takes planning maximum 58,260→61,860 s, exceeding 59,520 by 2,340 s. Lead must prospectively resolve roster/cap action; never silently drop fresh calibration units (`S:docs/align/squeeze/fanout/series-plan.md:24–27`; V protocol 498–506). | Air sizing; lead ruling; magistrate applies. |
| 8 | Recompute/release/v5 kit missing: **no intrinsic MBP idle if off-box**, but can become days of serial waiting | Build raw synthetic independent oracle, coverage comparator, digest-bound release manifest and v5 short native kit while v4 measures. No dependency on Block-5 analysis. | Air desk; lead release; Ed reserved actions. |

## Likely refusal traps and proportionate fixes

These are code-based risks; only the R0 history is an observed refusal record.
A real agent, failed sensor, charging event or live writer is not a spurious
refusal. Numerical/admissibility changes need prospective authority.

| Guard / logic and macOS interaction | Risk and proportionate action |
|---|---|
| R0 instant daemon-CPU threshold, display redraws, dasd waves | M items 205–209 document frauddefensed, WindowServer/ControlCenter and routined refusals, including 0.052 CPU-s/s. **R0-L3 is already adopted**, not a new proposal. Preserve the actual amended classifier/guard on integration; do not revive a fork's old blanket 0.05 abort. Keep display asleep, routine load as disclosed where ruled, sustained-load logic for R1. R0 passed; do not spend another R0 to optimize history (`M:RUN_STATE.md:1182–1258`; R1 load handling `V:scripts/align_r1_rehearsal.py:869–909,1050–1107`). |
| SMC one-second-grid tolerance | R0's old 100 ms tolerance lost real coverage (M item 195). V still defaults `Coverage.tolerance_ns=100 ms`; gate rolling coverage and desk instantiate that default, while full-inventory classifier received a separate repair (`V:joulewise/align/apple/thermal.py:195–260`; `V:joulewise/align/apple/thermal_gates.py:271–285`; `V:joulewise/align/apple/thermal_desk.py:130`). Selected-key sidecar uses an absolute grid, so this is **not proof of the same live failure**. Replay delayed-read/native-jitter fixtures across *all* consumers, retaining measured read brackets and the 2 s gap bar; if a repair is needed, qualify half-cell assignment as a scientific change rather than faking samples. |
| Exact launchd absent-service stderr + exit 113 | V only admits one English line (`V:scripts/align_v4_session.py:406–422`), without the locale pin used by R's CPU census (`R:joulewise/align/r0_host.py:95–104`). Different/localized output could look indeterminate even when no job exists. Capture the target OS output during smoke; pin `LC_ALL=C`, use absolute executable path and a shared tested parser for documented observed forms. Never treat arbitrary nonzero/timeout as absence. Also test stale plist vs loaded service cleanup; live jobs still refuse. |
| Top-up ≤30 min vs finalize/cool/notice/dwell | Current source-time rule can expire while an already full battery remains in float. Repeated fresh ioreg reads **do not** renew a completed-top-up timestamp (`V:joulewise/align/apple/v4_registration.py:391–422`). Build a real completion/continuous-float history; schedule long work before the valid arm interval. If native evidence shows a stable long float, ask lead for a prospective continuous-float admission rule; do not invent a new completion time or widen the bound silently. |
| R1 CPU journal ≥0.9 Hz, no gap >5 s; thermal coverage ≥99% / gaps ≤2 s | Background probes/serialization can manufacture measurement gaps and a whole R1 refusal even without sustained external compute. Keep census/logging outside read brackets; native smoke must include load/jitter and collector failure. R1 already allows isolated CPU bursts and redoes quiet segments only on sustained load; do not turn every flagged member into a night veto (`V:scripts/align_r1_rehearsal.py:878–909,1085–1107`; `V:docs/align/pilot_protocol_v4.md:449–495`). Preserve missingness semantics; first optimize collector overhead, not thresholds. |
| Empty unified log / missing counter treated as clean, or every log row treated as SSD loss | First is a false pass; second creates routine-event false refusals. H currently flags any matching row, even benign, while P revision 2 has distinct IO/STATE/UNVERIFIED/config-break outcomes. Qualify target-host log predicates with induced mount/unmount/reconnect/read and counter resets; map events to the adopted classes. Preserve UNAVAILABLE on unqualified evidence. No continuous heavyweight in-window log scanner (`H:docs/align/v4/SSD-B-UNMOUNT-OPERATOR.md:45–77`; `P:docs/align/v4/SSD-PERMANENT-AGREEMENT.md:109–121,250–257`). |
| R1 phase bound copied into outer night deadline | A pre-blackout segment may wait until 13:15, adding its bound +5,400 s; a 61,607 s plan can kill a valid R1. Corrected V helper exists; R lane remains frozen. Generate deadline from *installed* segments/retries, not stale test/display text; include outer scaffold and shutdown/harvest. This is a deadline bug, not a reason to cut a running job (`V:scripts/align_r1_rehearsal.py:980–996,1314–1368`; `M:RUN_STATE.md:1093–1114`). |
| Exact-head PREQUAL and receipt digests | Necessary provenance, but unrelated late edits can invalidate a previously passing packet and force a fresh cycle. Freeze code once, complete all branch integration before smoke/reviews, then produce same-head evidence. PREQUAL `--offline` deliberately yields incomplete for the network pin check, never pass (`V:docs/align/v4/PREQUAL.md:162–184`). In this no-network task it cannot be a live admission receipt. An offline cached-pin equivalence mechanism would need its own authorized design/review; do not relabel incomplete. |
| Missing U3/B/triage/registration | These refusals are **real missing prerequisites**, not over-strict guards. Implement/qualify the admitted rule and producer. Do not waive them to hit a calendar target. |

## Physics waits versus fixed program waits

| Wait | What the code actually does | Evidence needed for faster operation without changing the reference-state estimand |
|---|---|---|
| R1 initial soak | Fixed **1,800 s**; evaluates last **1,200 s** slope ≤0.2 °C/min, ≥0.9 valid reads/s; can redo. `V:scripts/align_r1_rehearsal.py:159–161,495–538,912–958,1090–1094`. | Do not shorten this armed R1. Development evidence of stationarity/variance and matched soak-derived R/bands across shorter starts, with a prospectively frozen stopping rule, could support a successor. A cool reading alone is insufficient. |
| R1 step quiet + recovery | After step G0 release, **300 s fixed quiet**, plus **600 s fixed post-step recovery observation**. These provide baseline and response evidence, not just cooling (`V:docs/align/r1_runtime_contract.md:148–162`; `V:scripts/align_r1_rehearsal.py:104–116`). | Separate warmup/load/idle/recovery timestamps first. Shortening observation can censor τ/S7 and change selected keys; needs matched response/band evidence and prospective qualification, not a sleep deletion. |
| R1 cooldown / precool | **Condition-based already**: stop when S_slow ≤ soak R+δ_slow, capped at 1,500 s. It is one-sided; already cooler is acceptable (`V:joulewise/align/apple/r1_runtime.py:1613–1635`). | Record time-to-band and any subsequent rebound. Avoid adding a second fixed 25 min timer after a passing condition. A temperature-only release is not the full G0 gate. |
| G0 / G1 / H | **Condition-based already**, not mandatory cap-length sleeps. G0 needs 10 consecutive good samples, both temperature bands, slow slope ≤0.2 °C/min, OS 0/Nominal recent PM; G1/H need 5 good samples. G0 cap normally 600–1,200 s or signed R10 D cap; G1/H use G_turn≤300 s. Unobserved/deadman paths retain flags (`V:joulewise/align/apple/thermal_gates.py:503–599`). | Most safe gain is reaching the existing state sooner and avoiding duplicate waits. Retain sidecar status/coverage/release evidence. Fewer consecutive samples, shorter slope horizon or wider bands are protocol changes requiring prospective operating-characteristic and repeatability evidence. R1 S6 tuning is the authorized evidence-based route; no opportunistic gate deletion. |
| W1/D member idle | Fixed **300 s**, also the R1 matched predecessor schedule (`V:docs/align/r1_runtime_contract.md:97`; `V:docs/align/pilot_protocol_v4.md:710–713`). | R12 explicitly keeps it for v4. V5 development paired 30B 300-vs-120 s check, 8 pairs, ~2–4 h; compare baseline R, repeat identity/energy, total idle+G0, battery and tails across predecessor heat. Saving ceiling is 22×180=3,960 s/window; actual gain smaller if G0 grows (`L:docs/perf/2026-11-08-latency-synthesis.md:63–68,104`; `M:RUN_STATE.md:1115–1128`). This supports the same reference-state target only if qualified; it still changes the prospective protocol. |
| Quiet admission / display dwell / launch lead | Cumulative CPU admission waits for a real observation interval (`R:joulewise/align/r0_host.py:66–74,149–158`). R0 display wait is fixed **300 s** (`M:scripts/launch_align_r0.py:31–37,184–204`). Shared session prepare uses **420 s default lead**, rounds to a minute, minimum 300 s (`V:scripts/bytes_h_session.py:43–47,312–318`). These are distinct mechanisms; do not double-count or assume R0 display logic is automatically in W1. | Parallelize only compatible post-close physics waits: finalize/offload finish before the uncontaminated CPU interval begins. Need native sleep/readback/wake receipts and quiet-state convergence to replace a fixed display dwell with a condition-based one. Prepare launch time after the packet is ready, leaving installer lead. No speculative shortening of agent stand-down. |
| R1 OS blackout | Fixed calendar **11:45–13:15 Pacific**, segment admission waits to its end if the *whole bound* intersects it. Up to **11,164 s** per step-D encounter (`V:scripts/align_r1_rehearsal.py:962–996`). Other scheduled bursts are recorded/retried under load logic, not all avoided. | R1 `os_batch_wait_s` and load/thermal journals show actual cost. Prospective member-level vs segment-level ruling could retain the same workload/thermal target; it changes scheduling/time-of-day selection and requires that disclosure. Do not apply a blanket 90 min/window tax to all W1/D code without finding its actual wait path. |
| Window ceiling | **No fixed wait** once authenticated terminal closure/release is achieved (`V:docs/align/pilot_protocol_v4.md:764–775`). | Trigger next preparation on the existing terminal release latch. Event wake can remove up to 300 s polling delay, not 5.28 h of computation. The larger saving comes from scheduling on actual close rather than reserving the ceiling (`L:docs/perf/2026-11-08-latency-synthesis.md:20–22,89–92`). |
| SSD old qualification | Fixed five blocks ×600 s settles +120 idle/decode segments ×120 s +120×60 s gaps = **24,600 s** planning; decode is fixed-work, not fixed-time (`V:joulewise/align/apple/ssd_qualification.py:76–124`). | Existing design needs block-level residual df; three blocks yield none. Shorter gaps/settles require recovery/carryover evidence, prospective design and native qualification. R12 rejected shortcuts; no saving credited. |
| Permanent SSD proposed Q | P G3 derives L from a measured power plateau; **Q=max(30 min,2×max(L1,L2))**, rounded to 5 min, frozen before third-cycle validation; Q≤90 min. Still a fixed minimum after each verified unmount/quiescence (`P:docs/align/v4/SSD-PERMANENT-AGREEMENT.md:135–162,230–248`). | Qualify once with induced I/O/counter/log controls and fixed hardware. Q alone can consume the old 30–45 min turnover before launch lead; forecast a longer cycle if adopted. Counters prove host block I/O, not constant device power. No zero-wake inference from silence. |

Non-software throughput measures: keep the MBP dedicated and display asleep;
batch Ed's one-time cable/clearance/OBC/sudo/accessory/storage setup; arrange
operator availability before the SSD gap; move record review, statistical work,
kit generation, native Air tiny-model qualification and all hashing of *remote
closed copies* to the Air; run back-to-back on actual terminal release. Keep
the physical configuration fixed throughout a cohort. Do not overlap MBP
copy/compression/hash work with capture, change cooler/powermode between members,
or thin reference scaffolding without qualification. R12 explicitly retained
anchors, contrasts, idle and scaffold (`M:RUN_STATE.md:1115–1143`).

## First v5 development steps: prepare before v4 ends

F is a **draft**, not adopted authority (`F:docs/align/squeeze/v5-design/RULING-DRAFT.md:1–3`).
Its ground-up behavioral design supersedes neither v4 nor the older add-on by
itself. The concrete earliest work and missing prerequisites are:

| Step | Current existence / prerequisites / owner |
|---|---|
| G0–G2, Air during v4 | Threat/evidence contract, exact macOS receipts, permitted helper/log-edit surfaces, matched honest carriers, reduced-tool tasks, supervisor/truth ledger, submitted projection, declared-work twin and operator-record rerun. Existing v4 bundles/seeds/parser/gates are reusable components; **a qualified complete v5 harness is not delivered in the inspected draft/series sheets**. Air implements/reviews synthetic fixtures; lead rules the contract. API monitor immutable pin/view/parser/canaries and cap need Ed, under future network authority. No v4 transcript scoring (`F:docs/align/squeeze/v5-design/RULING-DRAFT.md:131–183,399–405`). |
| G3, first short MBP slot | Native sandbox/child escape/teardown/no-daemon qualification after Air fixture tests, with its own tiny synthetic native arm route and smoke receipt. Missing as a delivered kit here. Magistrate executes; Air builds. This is the first small hardware task that can consume a gap without a long campaign (`F:docs/align/squeeze/v5-design/RULING-DRAFT.md:406`). |
| G4, daytime model qualification | Final model ladder decision, existing port gold + real-weight parity, qualified storage, frozen context/cache/helper resource maxima; native no-swap/memory-pressure, tok/s and paging-I/O evidence. Flash-Next deadline **Dec 6** is draft. Ed must be present for physical/storage changes; never overlap v4. Candidate availability is unverified; this audit downloads nothing (`F:docs/align/squeeze/v5-design/RULING-DRAFT.md:77,407`; `M:RUN_STATE.md:1338–1355`, item 198's operator-only constraint). |
| G5–G7, capability/replay/timing | Per-pair capability bars, token-exact seeded operator rerun and declared twin, measured rerun multiplier, member timing under qualified thermal policy. Need admitted task/model/roster, complete launch route and isolated truth/custody. V4's medium-effort rung and successful energy capture do not satisfy these gates (`F:docs/align/squeeze/v5-design/RULING-DRAFT.md:408–410`). |
| G8–G9 + idle experiment | DC-in closure/clock/gaps/battery/tail/repeatability, randomized replay/sham and resolution for side-generation/CPU under serial/concurrent load; independently qualify g_E and any lighter thermal policy. A SECONDARY v4 KM003C fit supplies no primary-endpoint qualification (`F:docs/align/squeeze/v5-design/RULING-DRAFT.md:411–412`; `V:joulewise/align/apple/km003c.py:170–176`). The 2–4 h idle paired check belongs here, per R12. |
| G10–G12 | Only after earlier gates: capped adaptive nonredundancy search, actual API budget, power/size/regression tests, capped fresh calibration plan, release-cost ledger, cold reviews and seal. Draft v5 gives **no v4 calibration credit**; do not let a reuse assumption hide fresh MBP cost (`F:docs/align/squeeze/v5-design/RULING-DRAFT.md:25–32,413–425`). Lead/Ed own adoption and spending. |

## Verification and handoff

Performed only source inspection (`git show`, `git ls-tree`, `git grep`,
`git cat-file -e`), arithmetic and six tiny synthetic/AST checks under
`python3.13 -B` (one process): **6 passed, 0.001 s**. Checks established the
unconditional U3 refusal, constant pending B bar, seven-window continue,
eight-window completion, eight-window shortfall, and missing-packet refusal.
No production runtime/arm/PREQUAL command or repository test suite was run.
This is a docs-only audit; full suite is forbidden by the brief and unnecessary
for the change. The native lead must run the integrated exact-head PREQUAL,
real-launch synthetic replay and labelled smoke, individually, outside agent
load; this report supplies no live hardware acceptance.

Final document checks: 118 branch/file/line citations resolved across 45 source
files; all line numbers were in bounds. Markdown table columns and the local
handoff link passed a small checker. Calendar/cycle and +2-sentinel arithmetic
were recomputed from source constants. `git diff --check` passed. These checks
validate references and arithmetic, not hardware behavior. For native MLX
stream qualification, the lead's existing no-download test command is
`JW_ALIGN_MLX_NATIVE_TESTS=1 python3.13 -B -m unittest tests.align.test_thermal_mlx`
on the appropriate integrated lane (`S:docs/align/squeeze/fanout/series-plan.md:58–65`);
it still does not replace the real stage arm/smoke gates.

Changed files: this report and
`docs/run_reports/2026-11-08-critical-path-sol1.md`. Coordination state is
untouched. The local commit ID is supplied in the session final handoff; no push.

**Next exact step:** Air/lead triage rows 1–5 now: obtain R1-ARM-1 and smoke
delivery; assign U3 and B rulings/implementations; freeze the D1–D3/C1–C8/test
role/scorer contract; choose the SSD path with Ed. Deliver runnable synthetic
handoff packets before R1 closes. The magistrate should receive a prepared
kit and short execution list, not discover missing routes at the keyboard.
