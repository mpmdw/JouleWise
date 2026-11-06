# Window council, round 2 — Sol

2026-11-05. **Design advice, PROVISIONAL; no arm authorization.** I read all
three round-1 designs in full. Checks below use repository code and recorded
findings, not measurement files. No network was used; the other seats' web
claims remain attributed claims until the checks in §4 are supplied.

Citation convention: `O`, `F`, `S` mean `.council-out/r1-opus.md`,
`r1-fable.md`, `r1-sol.md`, respectively, with line numbers. Local code is at
`e328f0e72`. Additional sources:

| Key | Exact source |
|---|---|
| R7 | `origin/main:docs/process_traces/2026-11-04-magistrate-cf1baad2/RECORD.md` |
| R3 | `origin/main:docs/process_traces/2026-11-03-magistrate-af17111e/RECORD.md` |
| R9 | `origin/docs/2026-11-05-magistrate-c110a6c9:docs/process_traces/2026-11-05-magistrate-c110a6c9/RECORD.md` |
| CAL | `origin/lane/2026-11-04-align-desk-calibration:scripts/align_pilot_calibration.py`, frozen `7fbd95e31` |
| EXT | `origin/desk/2026-10-29-byext-slots:configs/campaigns/bytes_v1/extension/slots.json`; same ref's `.codex-report/BY-EXT-2.md` |

## 1. Errors and unsupported conclusions

### Opus

1. **The deciding experiment does not decide the stated alternatives.**
   O:164–172 has only one A/B difference for each of two different trajectories.
   Its order is ABBA in *treatment labels*, not a replicated ABBA for each
   trajectory. At W1 ordinals 5,9,15,18, a linear ordinal drift contributes
   `[(15−5)+(9−18)]/2 = 0.5` drift units to the mean B−A contrast; unequal
   member durations also defeat cancellation in wall time. There is no
   independent replication for the proposed per-turn trend CI: turns share
   an episode. A ≤6 J difference in two old 30B trajectories cannot reject
   thermal effects in dense 27B or justify dropping their gates. Identical
   tokens isolate a **schedule/state intervention**, not temperature alone.
   The existing ruling explicitly leaves the p5→p6 cause unattributed
   [R7:41–45]; O:161's claim that this proves mechanism T is too strong.

2. **The gates can ratchet and admit uncontrolled state.** O:237 changes the
   reference to the preceding turn when recovery fails; successive permitted
   rises can accumulate. O:205 proceeds after timeout, while O:243 keeps
   missing-sensor trajectories in fits after a timed wait. Neither establishes
   U1's measured-state condition. Refuse subsequent work on a failed gate;
   do not change the reference or replace a thermometer with elapsed time.
   The initial gate must also follow warmup: lifecycle is idle → warmup →
   measured run (`joulewise/controller.py:1655–1660`), and present warmup uses
   the condition's prompt (`joulewise/align/apple/workload.py:265–271`).

3. **Chunk holds change both the workload and the energy boundary.**
   O:208–214 excludes hold energy and says a token budget makes trajectories
   independent of machine speed. It removes a wall-based stopping mechanism;
   it does not prove replay identity. Cached and full-prefill paths already
   selected different tokens at bf16 ties [R3:15,34]. Pauses also change
   cache/state and latency. Present attribution keeps unowned gaps in the
   episode total but outside turn-owned energy
   (`joulewise/align/energy_residual.py:145–163`). Report **both active-turn
   energy and full elapsed/gross energy**, including holds and gate waits.
   A chunked cell needs a new attribution/version gate, not just a pause hook.

4. **The acceptance tests do not establish equivalence.** O:270 requires a
   correlation CI to include zero at m≥6; that is failure to reject, not
   evidence of a small confound. Restricted temperature range can suppress
   correlation. U4 is unevaluable in W1's 1–2 benign/model/pair [O:333], so
   O:334 cannot promise all U1–U4 checks pass. Use fixed-work effect bounds
   with intervals; “insufficient precision” must be a possible verdict.

5. **Calibration and series claims need correction.** O:248–251,287–291
   import CAL unchanged, then O:340 calls the result split calibration.
   CAL:70–112 refits each session, and seed filtering affects the pool,
   **not the fit** (explicitly CAL:76). Fresh trajectories under a frozen
   design are not automatically independent calibration under a fixed scoring
   function. Also m=19, not 20, is the first finite rank; m=20 still uses the
   maximum [CAL:45–57]. O:341's fastest-model promotion must precede fresh
   calibration; any earlier screen remains development permanently.

### Fable

1. **Held-out counts contradict the declared selection phase.** F:152–159
   counts M1/M2's six benign/pair toward m=16, while F:167 explicitly calls
   each first model window selection data. Under that declaration the later
   increment contributes **m=10/pair**, not 16. Even if all operating choices
   were irrevocably fixed before M1/M2, m=16 gives rank 17 and no finite
   threshold. Pilot 9 yields **20 held-out/pair**, not F:171's 21: old seed 1
   is selection data; the fresh increments are 17–26 and 27–36
   [R7:46–48; R9:20–24]. CAL unchanged also has the fixed-fit problem above.

2. **The window extension is not scientifically necessary.** F:157 says
   smaller rosters leave too few benign trajectories to *ever* obtain a finite
   threshold. More prespecified windows solve that problem. Its quoted maxima
   are 44,820 / 48,420 / 47,040 s, so **even M1 exceeds 44,640 s**.
   The formula adds 17,700 s, not merely active collection time
   (`joulewise/b6/plan_inputs.py:56–59`; `joulewise/b5/plan.py:59,66–67`).
   The 600 s/member extra gate wait is not reserved in F:152–154. At 20 target
   members it could add 12,000 s. Rehearsal must replace transfers with an
   inclusive bound; there is no free gate allowance.

3. **An idle gate does not control later turns.** F:99,103 gates before
   warmup and asserts resetting the *next* member is the needed property.
   Pilot 7's open problem is the later-turn accumulation within an episode
   [R7:41–45]. A post-warmup gate and a within-episode intervention/test are
   necessary. A start-state gate alone is insufficient for F:55's acknowledged
   300–430 s dense-model load. F:113 lets missing thermometry count under old
   rules; that cannot qualify the new thermal claim.

4. **Historical anchors cannot supply missing temperatures or causal beta_T.**
   F:122 proposes a temperature regression using old windows that recorded no
   die temperature [R7:24,41–42]. K counts windows, not temperature-observed
   windows. Identical work removes behavior variation, but cooling, fan mode,
   calendar state and temperature can still co-vary. Fit an intervention
   contrast on new randomized, temperature-observed replays; call an
   observational slope a diagnostic. Likewise PSTR minus SoC rails [F:83] is
   an unassigned power residual across different sensor boundaries, not a
   validated DRAM meter (`joulewise/hazards/smc.py:21–27`).
   F:131 also calls 6 J three times the replay noise: the difference SD is
   `sqrt(2)×2.1 = 2.97 J`, so 6 J is about **two** difference SDs. Neither
   that noise estimate nor a weak residual correlation establishes control
   for a new model.

5. **Memory, inventory and feasibility claims overreach.** The claimed default
   Metal limit “about 96 GB” [F:31] conflicts with the recorded **115.4 GB /
   107.5 GiB recommended working set**, default sysctl 0
   (`docs/design/bytes_pilot/SUMMARY.md:29–31`). Neither is a total-memory
   guarantee. Qwen3.8 was re-downloaded on October 28, contrary to F:29,196's
   outstanding-download claim [origin/main `RUN_STATE.md:349`; EXT:12–19].
   “397B does not fit at any quantization” [F:13] is not established: its ideal
   2-bit weight floor is 99.25 GB. That says nothing about an available,
   acceptable-quality runtime, but disproves a universal weight-size argument.
   For Flash-Next, pinned-runtime incompatibility is distinct from physical
   infeasibility at every quantization. Both seats must normalize GB/GiB and
   supply exact artifact/loader evidence before making the latter claim.

6. **Tool capability is not built far enough.** F:179–190 adds template
   kwargs but omits the XML parser Opus identifies. The current parser feeds
   `<tool_call>` contents to `json.loads` and cannot parse an XML function
   envelope (`joulewise/align/apple/endpoint.py:126–158`). If the model templates
   emit Opus's reported XML, D/122B cannot act. F:196's 7,102+2,048-token run
   also does **not** exercise a 40,960-position cache merely by setting the cap.

### Corrections to my own round 1

- **My five-window budget was wrong.** S:529–549 treated 42,355 / 43,835 s
  as window maxima. They are programmed spans; the actual maxima are
  **60,060 / 61,560 s**, after the existing planner allowances. Withdraw the
  five-window promise. The revised smaller allocations below retain the cap.
- **Pooling is already adjudicated in the later record.** S:496–504 left it
  open; R9:13 rejects the cross-pair proposal, deliberately keeping per-pair
  pools. R9:14 also accepts the disclosure that offset invariance is constant
  **per turn**, not arbitrary per episode. Preserve that ruling for pilots 8/9.

## 2. Best ideas adopted

- **Opus:** Thinking Next for a reasoning-omission study; a replicated
  identical-work state intervention before expensive calibration; typed XML
  parsing; a recurrent-state checkpoint if template rewrites really force
  rebuilds; separate production and legacy environments if a loader fix is
  necessary. These are hypotheses/build gates, not established live results.
- **Fable:** one production model per later window to reduce reloads;
  window-local measured reference state, supplemented by cross-window
  sentinels; ambient logging and fixed external airflow; explicit capability,
  memory and thermal admission criteria before choosing quantization.
- **Both:** a new prospective cell; old anchors never become new-model
  calibration; gates/holds have a real time cost; no primary clock term.

## 3. Contested decisions — my position

### (a) Models and quantizations

**Primary N: Next-80B-A3B-Thinking 4-bit**, conditional on verifying Opus's
artifact `mlx-community/Qwen3-Next-80B-A3B-Thinking-4bit`, revision
`9a2b46347bb170cb2924092175fa21554fe585a9`. Prefer useful reasoning and tool
behavior over raising Instruct to 8-bit: prior **greedy 4-bit Instruct** acted
only 0–2 times [R3:19,36], and 8-bit alone does not demonstrate capability.
This does not prove Thinking acts better. Test it. Pinned Instruct 4-bit
`d8a069bf…` is the operational fallback/contrast, not interchangeable hidden
reasoning evidence. Instruct 8-bit is a later quantization cell if Ed wants it.

**Primary D: Qwen3.8-27B 8-bit**, `mlx-community/Qwen3.8-27B-8bit`,
`815b83c0df8ffd1d1b5244cf75fd6ef14fca9ef9`. EXT's download is 29,531,521,322 B;
header census text residency is **28,579,478,528 B** [EXT report:9–16].
The recorded config implies 2,684,354,560 B attention KV at 40,960 BF16
positions, plus recurrent state/workspace. No peak is established by that
sum. Use a verified **same-model 4-bit** fallback if 8-bit fails; otherwise
report the cell unavailable. Freeze effort after checking the actual template,
not by silently treating truncated xhigh reasoning as completed behavior.

**122B: IN the qualification shortlist, OUT of the initial calibration
allocation.** Its pinned `mlx-community/Qwen3.5-122B-A10B-4bit`, `e9c67b08…`,
has 68,690,732,544 resident bytes; native small-context cache records exist
under 0.31.3 (`configs/bytes/records/RUN.md:127–140`). Promote it if Next fails
capability, or if Ed explicitly wants a third calibration cell. Its observed
71.5 GB MLX peak was at small context, not a tool-loop bound
(`docs/design/bytes_pilot/SUMMARY.md:26`). Screen it in the quiet rehearsal;
do not invent a third-model calibration from two-model counts.

**Flash-Next: not admitted on the present stack; not proved physically
impossible.** Resolve which artifact, units, loader and quantization before
excluding it from the 128 GB frontier. Keep 0.31.3 initially. A necessary
upgrade gets its own pinned production environment and calibration identity;
the old anchor environment remains available. For every candidate require
actual full-context/rebuild peak below `min(96 GiB, .75 × physical_bytes)`,
no new swap, and verified tools/reasoning. This is a proposed headroom policy,
not a claim about Apple's default limit or a universal feasibility result.

### (b) Qualification, experiment and calibration counts

Combine them: the **next new-protocol window is a 16-member qualification**,
including the corrected state experiment; no held-out calibration yet.
Do not cancel or alter pilots 8/9: the lead decides pilot 9 from the existing
pointer/read [R9:19–24]. Four old seed-1 originals retain ordinals 1–4; this
is a smaller bridge, **not the full eight-anchor K-session design**.

For the deciding experiment use the two pilot-7 spam templates identified by
Opus, frozen token IDs/tool I/O/cache ledger: **four runs per template**, A-B-B-A
and B-A-A-B. A = post-warmup start gate only; B = same start gate plus
per-turn recovery. Use equal-duration reserved slots, pad outside measured
episodes, and record actual episode starts/active-energy time centroids;
predeclare a linear elapsed-time term for the contrast rather than claiming
ABBA cancels arbitrary drift. Both arms record temperature. These eight runs
are a mechanism screen on 30B, not a
thermal verdict on the new models. Require exact consumed-token/cache-work
identity; seed-only replay divergence makes the contrast unavailable.

The other four members are N/D × both pairs, benign. Full both-condition
capability, 122B and long-context tests belong to the preceding quiet rehearsal.
If the reserved contrast slots cannot fit, split qualification rather than
call two differences decisive. A small/uncertain contrast never licenses
dropping the gates; qualify each new model on its own sentinels.

After qualification, allocate **four 18-member windows per promoted model**:

| Window | Training benign | Calibration benign | Sabotage | Exact-work sentinel members |
|---|---:|---:|---:|---:|
| T | 12 = 6/pair | 0 | 2 development = 1/pair | 4 |
| C1 | 0 | 14 = 7/pair | 0 | 4 |
| C2 | 0 | 14 = 7/pair | 0 | 4 |
| C3 | 0 | 12 = 6/pair | 2 fresh = 1/pair | 4 |

Fit/freeze after T, before C1; development includes qualification/rehearsal.
Thus **m=20 fresh calibration/pair**, one fresh sabotage/pair, and six matched
sentinel pairs over three calibration windows. The sabotage sample is purely
descriptive. CAL's exact rank arithmetic can be reused; its session refitting
cannot implement this split. No mixing task pairs, models, quantizations,
stack/control policies, training rows or duplicate seeds. Window dependence
still limits exchangeability; no exact distribution-free coverage claim.
For a registration intended to move beyond a maximum threshold, plan
**m≥39/pair** and a separate locked FPR/power test cohort prospectively.

**Budget, including the planner's allowances:**

| Window | Inclusive programmed span, conditional rehearsal ceilings | Window maximum |
|---|---|---:|
| Qualification | `4×800 + 8×1200 + 4×1300 + 4995 + 2000 = 24995 s` | **42,720 s** |
| Each T/C window | `18×1100 + 4995 + 1500 = 26295 s` | **44,040 s** |

The 4,995 s scaffold is a transfer (`docs/align/pilot_protocol_v3.md:168–180`);
extra conditioning and all waits must fit these ceilings. This plan costs
**five windows for the first calibrated model; nine for both**, about 109.7 h
of maximum reservations for nine, plus rehearsal and desks. It is not an
optimality claim. Split further if rehearsal fails; never silently add time.
The old disk law gives approximately **35 GB/two copies** for an 18×1100 s
window before extra telemetry, residual margin and partials; reserve ≥80 GB
free *after* weights, then replace the transfer with verified receipts.

### (c) Gate variable, form and work budget

Use validated **fast die and slower thermal-state sensors**, plus fan RPM;
clock is a fixed-work validation channel, not the gate's sole thermometer.
After neutral warmup, require the final 60 s within model reference ±1.5 °C,
absolute slope ≤0.2 °C/min, observed OS level 0 and Nominal pressure. Reference
comes from three recovered conditioning plateaus spanning ≤2 °C, before
behavior outcomes are used. Then require each turn's two sensor values within
±1.5 °C of that episode's own start for 10 consecutive 1 Hz samples.
Never move the reference to the previous turn. Total extra recovery cap:
**600 s/member**, further bounded by its inclusive reserved slot. Failure
refuses subsequent work and is reported; no automatic replacement seed.

Per-turn recovery cannot prevent heating inside one dense decode. Test the
longest full turn. **Chunking is a contingency cell**, adopted before fresh
calibration only if unchunked D fails. Choose a fixed positive token interval
whose measured worst chunk is ≤60% of fixed-work decline time; requalify its
prefill, resume transients, full energy and token identity. A token interval
alone does not bound seconds if throughput falls. If the qualified chunk
policy cannot fit, use verified D-4bit or stop D.

Prefer fixed decoded-token episode caps over the 120 s wall admission guard:
initial proposals N **8192 total / 4096 per turn**, D **4096 / 2048**, both
12 turns and 40,960 *total* context positions. Rehearsal may select a smaller,
separately named cell before qualification. Retain an independent operational
deadman/slot timeout: hitting it is incomplete, not normal task completion.
Publish task scores, actions, closed reasoning spans and all cap hits. No
claim that these budgeted agents reproduce unconstrained production service.

### (d) One merged “under control” gate

All thresholds below are **proposals**, fixed before qualification; failure
means fail/inconclusive, never a conveniently loosened cutoff.

1. **Observed state:** ≥99% die/clock interval coverage; die gaps ≤2 s,
   powermetrics gaps ≤1 s; OS observations meet existing coverage rules.
   All included turns have observed level 0/Nominal and passed gates;
   gate timeout/refusal rate ≤2% of attempted turn admissions. Report the
   attempted population and original registered thermal scopes beside it.
2. **Matched clocks:** identical consumed work, separately in prefill/decode:
   early/late active-weighted clock difference ≤0.5%; reference-state active
   residency difference ≤2 percentage points. Require cross-window agreement
   for the same templates too. Natural-trajectory clock correlations are
   diagnostics, not acceptance evidence or scoring terms.
3. **Matched energy:** ≥6 exact-work pairs over ≥3 windows/model, spanning
   decode, prefill and cache rewrite. Normalized difference absolute mean
   ≤0.25%, SD ≤0.25%, and a 90% equivalence interval wholly within ±0.5%.
   Use fixed template weights and window-cluster uncertainty (three window
   means give 2 df, not six independent windows). Also require the 90% bound
   on the induced episode-energy shift ≤**0.1×s_r,development**, using the
   smaller per-pair development SD. Express this shift as the normalized
   matched difference times the fixed development typical episode energy;
   freeze all scales after T, before C1.
   Six pairs may be too few for that precision: print **inconclusive**, not
   “no thermal effect.” Do not transfer the old 2.1 J noise to new models.
4. **Monitoring stability:** with the fixed predictor, the 90% interval for
   benign early-to-late episode-residual change must fit ±0.37% of the fixed
   development typical episode energy (≈±10 J at 2.7 kJ), per pair. A failure
   blocks the monitoring-readiness claim; it does not authorize deleting
   calibration scores, retuning, or calling a CI containing zero equivalent.
5. **Population integrity:** every refusal, incomplete attempt and thermal
   failure is printed by arm; no top-ups until clean. Only prospectively
   defined physical/identity rules determine eligibility. Sentinel failure
   marks its prespecified block; residual size never selects rows. Publish
   active-turn and gross episode energy/latency separately. Hardware control,
   score stability and threshold adequacy receive separate verdicts.

### (e) Must-build list, in order

1. **Artifact/stack and template audit, then typed tool parsing.** Verify exact
   revisions, real reasoning-effort kwargs, EOS/reasoning counts and schemas.
   Extend `joulewise/align/apple/endpoint.py:95–161,240–250` with XML parsing
   only for verified formats; test malformed/nested/typed values and action
   round trips. This also corrects my round-1 parser omission.
2. **Cache correctness and ledger.** Instrument template rewrites and
   `joulewise/align/apple/prompt_cache.py:42–94` rebuild frequency. Build Opus's
   recurrent checkpoint only if needed; preserve represented IDs, attention
   offsets and recurrent arrays. Compare logits/state with fresh prefill;
   record numerical token divergence rather than asserting seed identity.
3. **Replay and telemetry, then gates.** Forced-token/tool replay with honest
   cache accounting; validated temperature types/keys, 1 Hz sidecar, paired
   clocks, RPM and phase-specific DVFM summaries. Existing SMC decoder only
   handles its listed numeric types (`joulewise/hazards/smc.py:101–117`), so
   enumeration alone is not a working temperature reader. Measure overhead
   and prove timeout/process cleanup. Prefer ALIGN-local changes; shared
   controller/monitor edits require pin/freeze impact review.
4. **Work cap and conditional hold attribution.** Version spec/policy identity,
   neutral warmup, final/per-turn gates, spent wait budgets and stop reasons.
   Holds require tiling and full-energy accounting before use.
5. **New kit/registration and fixed-fit scorer.** New files/config tree;
   explicit role/seed/order/control identities and full sizing/disk receipts.
   Preserve old frozen kits/CAL; do not rewrite them under new semantics.
   Synthetic production-shaped desk, focused serial unittest modules and
   non-author executing/science review precede the quiet live rehearsal.
   No current design constitutes a live gate pass.

### (f) Ed's physical work and questions only he can settle

Ed fixes stand/vent clearance, lid/display geometry, AC adapter and power mode;
logs ambient near intake at ≥1/min, targeting 20–23 °C and ≤1 °C window range;
starts any external fan at one fixed setting before conditioning and leaves it.
Use the existing qualified fan/power policy initially. A High Power or internal
fan-control change is a separate qualified physical regime, not a forced
prerequisite. Require stable battery float, not a blanket inference that
`battery.assist` means charger failure: R3:36 explicitly rejects that inference.
No unsupported fan writes or new utility installation are authorized here.

Only Ed can identify **which “Qwen 3.8”/actual production deployment he meant**,
whether paused/cooldown operation answers his use case, acceptable fan noise,
and how much quiet-Mac time he will provide. The chair can decide the scientific
roster once that intent is known. Downloads/offloads are lead-prepared and
verified during a desk; existing inventory is checked before any re-download.
For collection Ed closes all local agents/apps **and the seven-worker analysis
job if it is on the measurement Mac**. Collection/rehearsal uses launchd only,
with no live agent watching. This council session performs none of that work.

## 4. Web facts still needing independent verification

Sol cannot certify the other seats' November 5 web checks. The chair/network
seat should provide immutable receipts, then the Mac should verify locally:

- Official release identities/rankings/licences for Qwen3.8-27B, Flash-Next,
  Next Thinking and 122B; comparable tool benchmarks rather than unlike
  benchmark versions. Repository October 27 ranking is dated evidence only
  (`origin/main:docs/registrations/bytes_extension_models_2026-10-27.md:19`).
- Exact HF revisions, tensor inventories and **byte counts** of Thinking-4bit,
  Instruct-8bit, D-4bit and each Flash candidate. Resolve 97.6 **GiB** versus
  111.5 **GB**, embedding/MTP inclusion and KV/recurrent dtypes. Check the
  actual model `config.json`, template and conversion commit, not its name.
- Pinned mlx-lm loader support, alleged PRs **#1623/#1632/#1788**, the claimed
  0.32.2 release/fixes, mlx-vlm alternatives and any requirement for a separate
  runtime. Does absence of `mtp.` keys actually establish immunity to #1623?
  Source inspection and a fixed-prompt output check must agree.
- Exact template support for effort levels, preserved thinking, JSON versus
  XML calls, recommended sampler and any unsupported presence penalty.
- High Power availability/behavior on this exact Mac; sensor access/types.
  Third-party throughput tables are planning hints only: measure the pinned
  runner at 40,960 positions including a real rewind/rebuild and longest turn.

## 5. Revised recommendation — one-page decision sheet

**Run a qualification window before buying a calibration series.** Keep the
old pilot-8/9 population and scripts frozen. New quantization, stack, effort,
cooling, gates and chunking are explicitly new cells. Prefer Next Thinking
4-bit plus Qwen3.8-27B 8-bit; screen pinned 122B as a real challenger/fallback.
Next Instruct 8-bit is not the default reasoning-omission instrument.
Flash-Next is currently unadmitted, not proved impossible on 128 GB.

**Build first:** exact model/template receipts → usable tool parser → cache
correctness/checkpoint if needed → exact-work replay and validated thermometry
→ post-warmup/per-turn gates and work cap → new kit and genuinely fixed-fit
calibration driver. Run synthetic desk and focused checks, independent review,
then a launchd-only quiet rehearsal including full context, rewrites, both
conditions, longest turns, peak memory and slot timing. No hardware claim
comes from synthetic success.

**Next window:** 16 members: four unchanged 30B originals, eight fixed-work
state-control contrasts (two templates, replicated ABBA/BAAB), four benign
model×pair screens. Freeze equal-duration contrast slots. Planned span
24,995 s; planner maximum **42,720 s**, conditional on inclusive rehearsal
ceilings. A two-template result screens an intervention; it neither attributes
all drift to heat nor licenses removing new-model gates.

**Control:** fixed physical setup/ambient, neutral warmup, measured initial
reference, per-turn recovery to the episode's own initial state; never ratchet
the reference. Missing sensors/timeout mean refusal/incomplete. Token work
caps replace the behavioral wall guard, while a separate deadman remains.
Chunk dense decode only as a newly qualified fallback; print holds, full
energy and latency. Use no in-episode clock/temperature predictor.

**Acceptance:** ≥99% telemetry; admitted turns level 0/Nominal and gate-passed;
≤2% gate failures; matched clock ≤0.5%, residency ≤2 pp; ≥6 matched energy
pairs across three windows, |mean|/SD ≤0.25%, 90% interval inside ±0.5%, and
state-shift bound ≤0.1 development residual SD. Fixed-fit benign residual
drift interval must fit ±0.37% typical energy. Low precision is inconclusive.
Retain every attempted result and never remove rows because their score is bad.

**Calibration cost:** per promoted model, one 18-member training window,
then three 18-member calibration windows; each maximum **44,040 s**.
This buys 20 fresh benign/pair (rank 20, the maximum), six sentinel pairs,
and only one held-out sabotage/pair. Five windows including qualification for
one model, nine for both; more if timing fails. It does not buy a precise
5% FPR or power claim. Predeclare m≥39/pair and a separate test cohort if
those claims are wanted. Prioritize one model's complete cell before funding
the second. Ed supplies intended model/deployment, cooling/noise preference,
and quiet time; the chair rules and issues the bounded build brief.

## Handoff / run report

Only `.council-out/r2-sol.md` was written; no commit, branch/ref change, push,
coordination-state edit, measurement read, inference or collection. This
explicit council deliverable takes priority over generic queue/report writes.
Verification: all three designs read in full; cited code/records inspected;
`python3.13 -B -` stdlib checks of ranks, cache bytes, window maxima, document
whitespace/content and original-design SHA-256 hashes passed; `git diff --check`
passed. No unittest/full
suite was needed or run for this prose-only change. Unresolved facts are
listed in §4; all new timing/control thresholds remain proposals. Next exact
step: chair adjudicates the model/control/effort choices and authorizes a
bounded build, with live qualification still reserved for a clean Mac.
