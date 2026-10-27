GPT-6 (the exact serving model ID is not exposed to this seat)

## Findings (file:line)

**M1 supports a post-load OS-pressure episode, not demonstrated decode throttling. It does not establish that tail pressure is irrelevant to the sentinel, or supply a SoC-to-OS publication-lag bound. Preserve s5-p1's unavailable registered cell. Print a narrowly defined, post hoc OS-window sensitivity beside it; prefer measured thermal headroom and recharge recovery for pass 2 over changing the primary exclusion.**

Council activation a46602ae, 2026-10-27. Scope: read the supplied brief and both round-1 reports, Sol at 512425faf and Opus at c400efdaf. All production-code references below are against **991358f73f6d509c8a1ace3e812ff4e81a3983b2**, inspected unchanged in an isolated worktree. The report branch is cut from origin/main at **f164bef49c98d4383a7e2ee0ea48e7bd9c1c1a69**. M1 and the session counts are supplied observations, not measurements repeated here. The s5-p1 bundle/journal archive was not present in this workspace; no s5-p1 energy values were read. No production code, registration, evidence or live-loop state was changed.

1. **Three different endpoints matter.** Harvest's member hull includes sampler pre-spawn/post-parse and idle-baseline/sentinel events (joulewise/b5/harvest.py:2006). Its “request” ends at the sampling_stopped paired stamp (:2033), which is the endpoint M1 uses. BYTES obtains its actual decode interval from decode phase events and consumes the reduced decode energy (joulewise/bytes_analysis.py:1003, :1009). Do not silently equate M1's request endpoint with decode phase_end; obtain their exact offset from each bundle before an interval comparison.

2. **The registered OS rule deliberately over-covers.** The production in_force function selects the last read at/before start, all inside, and the first at/after end (harvest.py:2477). thermal_member_flags applies level != 0 to those readings (:3062). Both OS and powermetrics thermal codes exclude members (docs/registrations/bytes_pack_v1.md:168). Whole quads are atomic, and both strata need five units (:170; bytes_analysis.py:1176). M1 gives no head/load hits: 10 affected members, 9 lost units, including both a1 and a2 of b05. Thus H = 0. A wait for an already-present episode to end cannot remove a preceding member's tail hit; a colder starting condition is a different intervention.

3. **Polling latency is not thermal-publication latency.** NotifyReader reads the current notify-bus state in process; it does not wait for a future notification (joulewise/hazards/thermal.py:45, :72). The monitor polls thermal every 5 s and SMC every 1 s (joulewise/hazards/monitor.py:100). Powermetrics parses its own thermal_pressure field (joulewise/adapters/powermetrics.py:1807). Neither reader provides a calibrated delay from a physical sensor or frequency clamp to that field. The claim in Opus round-1 F3 that either channel necessarily reports every throttle identically is stronger than the inspected evidence supports.

4. **The sentinel is outside the measured window and has a purpose.** The controller stops sampling before the sentinel (joulewise/controller.py:2605, :2615). The adapter takes a short new post-idle capture, compares it with the pre-idle records, and records contamination evidence (powermetrics.py:1021, :1061). The derivation uses the largest absolute departure from pre-idle mean, including departures downward; contaminated GPU-idle evidence makes the bound unknown (joulewise/uncertainty_evidence.py:1539). A post-load frequency clamp or changed leakage/fan behavior can therefore matter to what this endpoint comparison represents. The per-run sentinel is distinct from BYTES' session NEG-8 allowance: BYTES' cell bound uses the registered reference-based allowance and transfer scale (bytes_pack_v1.md:257, :259; bytes_analysis.py:1275), not a new correction inferred from the late OS integer.

5. **Cooling and charging evidence are different.** The existing cooldown releases on power recovery and the last powermetrics pressure, subject to its cap (controller.py:4038, :4062). Neither the cause of a cap hit nor a 300 s OS episode follows from a cap-hit flag. The pinned catalog makes member.cooldown_cap_hit DISCLOSE (configs/b6/flag_catalog_b6.json:1018); the round-1 Sol warning that the flag itself excludes is incorrect. M1's 10–35 s episodes supersede the round-1 inference of an OS episode lasting at least 300 s. Battery charging exclusions remain separately specified (harvest.py:2686, :2974).

**Executed checks, synthetic only.** Ran the unchanged production parse_monitor_line, member_spans, in_force, thermal_member_flags, _kept, derive_idle_drift_evidence and decode_rich_telemetry from the inspection pin. Scripts ran through Python stdin; no test or source file was added.

- A production-shaped member with sampling stop at synthetic second 110 and hull end 133.4 was excluded for first nonzero reads at stop +10, +15, +20 and +25 s. Applying the same thermal function through sampling stop instead gave no OS code. A nonzero first bracketing read after that shorter endpoint still excluded; a nonzero head read still excluded. Thus the proposed alternative retains bracketing, not just inside samples.
- A 50-row fixture with M1's affected identities and b04–b06 battery exclusions failed the registered minimum. Narrowing only the OS window yielded 10 repeats/7 quads; flagged-inclusive yielded 10/10. These are fixture results and potential archive counts, not verified availability on either boundary.
- Synthetic pre-idle power 2 W and post-idle power 2, 1 or 3 W produced respective sentinel bounds 0, 1 and 1 W. These deliberately arbitrary fixture values are not proposed physical thresholds.
- A synthetic 0.1 s plist frame preserved GPU DVFM residency and CPU-cluster fields; GPU states at 500/1000 MHz with 0.25/0.75 residency decoded to 875 MHz active weighted frequency. This checks the structural diagnostic path, not hardware behavior.
- Focused existing tests passed: **22 tests, 0.311 s, OK**, using PYTHONDONTWRITEBYTECODE=1 and python3 -B -m unittest with tests.test_harvest_b5_p3harv.SmcBatteryRuleTests, .CleanCapturePairTests, .PairEndpointSignTests, and tests.test_uncertainty_evidence.IdleDriftEvidenceTests. An initial invocation also named a nonexistent test class; correcting that name produced this passing run. A full suite was unnecessary for this report-only change.

## Answers Q1–Q4

### Q1. Physics and the measurement that distinguishes mechanisms

**A pressure state that truly begins after decode cannot alter energy already consumed.** Rails integrate the decode trace; DC input integrates the mapped decode span and adds signed BAT-2 battery energy over that same span (bytes_analysis.py:508, :528, :534, :566). Neither includes the entire 23 s post-request hull in gross decode energy. BAT-2 separately bounds late battery reporting with tau = 2 × 1 s + the meter stream's largest poll interval (:491, :546). That derivation concerns the SMC battery channel, not thermal pressure.

Plausible links to decode are:

- Frequency/voltage limiting began during decode but the OS thermal-policy state was published later, because of sensor dynamics, policy averaging/hysteresis or a separate publication path. No SoC-to-notify lag bound is established here.
- A warmer machine changed leakage or operating frequencies during decode without crossing the OS pressure threshold. A later pressure episode can be a marker of that earlier thermal history.
- A later episode has no earlier limiting counterpart: heat reaches a slower sensor or thermal mass after load, or an OS policy threshold is crossed only during recovery. Ten–25 s after sampling stop is compatible with such a delayed thermal response, but does not identify the sensor or cause.

Even demonstrated throttling would primarily change the operating regime, duration and measured energy of the fixed workload; it would not automatically make integration of that actual energy erroneous. Nominal-regime comparability is nevertheless a legitimate reason for a registered exclusion.

**No flag is useful negative evidence, not proof of no throttle.** At the registered 10 Hz, sustained frequency/residency changes should be visible if those fields were captured; a sub-0.1 s transient can be averaged within a frame. The thermal flag tests only the pressure string, not the frequency distribution (joulewise/environment_admission.py:337, :424, :447). Nominal pressure can coexist with ordinary DVFS or a physical constraint below the policy threshold. Nor is a lower clock alone proof of thermal throttling: demand and memory stalls also alter residency.

**Measure first, from disk:** for all 50 members, use authenticated native powermetrics.plist and its recorded anchor, decode events, and the thermal journal. Reconstruct native averaging supports [endpoint − elapsed_ns, endpoint), not file-write times. Produce a structural table/time trace, with no joules or power columns:

- Decode GPU active-frequency/residency distributions, GPU idle ratio, requested versus actual software/DVFM states when present; CPU-cluster frequency, idle/down/online ratios; missing-field and support-coverage counts.
- Compare affected members with clean members adjacent in collection order and at corresponding within-decode positions. Also inspect all members across session order; “lost versus kept” is a diagnostic grouping, not a new selection rule.
- Record last nominal/first nonzero notify times relative to sampling stop and decode end, each pressure string in decode, and the exact sentinel start/end. Decode rich fields with the production decoder (powermetrics.py:1863, :2091, :2112); GPU freq_hz is observed in MHz while CPU cluster freq_hz is in Hz. Missing counters must remain missing.

Inspect raw/powermetrics_idle_post.plist and its quality metadata separately. M1's category “tail” does not prove overlap with the actual sentinel capture; post-parse is also in that hull. A nominal final read before the first level-1 read, aligned against any earlier clamp, distinguishes late publication from genuinely later policy onset as far as the archive permits. Existing captures may not cover the whole inter-member gap. If needed, the lead can run an independently authorized quiet diagnostic with continuous frequency/residency, pressure and available die-temperature sampling through load and recovery.

This disk analysis can settle whether there is evidence of an in-decode clamp at the available resolution. It cannot prove the absence of hidden limiting or calibrate a universal publication delay. The latter needs a validated physical-state reference and the OS channel observed together over relevant cold and heat-soaked conditions.

For the sentinel, a later thermal episode may change post-idle leakage, clock residency and cooling behavior. An endpoint envelope may widen; a depressed post-idle state could also fail to represent a hotter unobserved interval during load. The current derivation does not infer that hidden history from OS level. Inspect overlap, raw post-idle quality and recorded bounded/unknown status; do not delete the sentinel or declare all late reads harmless. The roughly 1 J attribution scale supplies no allowable thermal level or temperature: converting a thermal/regime effect into a joule bound requires measured power sensitivity and duration. Structural frequency checks alone cannot prove an effect below 1 J.

### Q2. Exact labelled alternative for s5-p1

Keep the registered result **unavailable: 9 repeats, 2 complete quads**, alongside the already required flagged-inclusive description (bytes_pack_v1.md:172).

I recommend one additional, explicitly post hoc line:

**“Request-end OS-window sensitivity — post hoc; post-request OS pressure disclosed; not a registered result.”**

Its exact rule is:

1. For each science member, let S be the original member hull start and R the exact member_spans “request” end, not a rounded M1 lag and not decode phase_end.
2. Re-evaluate only thermal.os_level_nonzero using the production thermal_member_flags predicate with span [S, R]. Thus count the last successful numeric-level read at/before S, all reads strictly between S and R, and the first successful numeric-level read at/after R. Any level != 0 among these still excludes.
3. Preserve the complete original journal, flags and full-hull thermal coverage disclosures. Require usable endpoint/bracketing evidence; do not infer nominal state from an absent read. Preserve every other exclusion, invalid-record rule, whole-quad rule, five-unit minimum, boundary availability rule, arithmetic and uncertainty term. Keep sentinel evidence and the registered NEG-8 reference selection/allowance unchanged. Recompute selection-dependent means, transfer scales and bounds under the same formulas. In particular, do not restore charging members.
4. Print identities of restored and still-dropped units, both stratum counts and all usual estimates/bounds if computable; otherwise print the alternative's own unavailability reason. It has no deciding role, no replacement primary point and no automatic entry into the paper's registered pass mean/difference or H1/H2.

**Derivation:** R is an independently defined end of the measured window containing decode. Keeping its first bracketing read covers the uncertainty of observing the published OS state at that boundary. On M1's complete successful-read series this extends the observed-state check by at most the measured maximum poll gap, approximately 5.3 s. It does **not** claim that the SoC-to-OS lag is at most 5.3 s. Do not use R + 5.3 as the new endpoint and then add another bracketing poll; that silently doubles the intended extension. Do not transplant BAT-2's 2 × 1 s term into this channel.

Opus's M1 script rounds onset lags to the nearest 5 s. Even an onset printed as 10 s is at least about 7.5 s after R; the 5.3 s maximum gap leaves a nominal observation after R before that onset. This supports the shorter-window sensitivity, subject to checking exact unrounded stamps and successful bracketing reads. It is not a measured publication-lag bound. The 23.4 s median tail is likewise not a physical lag bound.

From the supplied exclusions, this could restore r07 and thermal-only quads b02, b03, b07, b09 and b10: **10 repeats and 7 quads potentially survive**, while b04–b06 remain out. Valid energy records, meter support and references must still be verified. No numerical energy estimate can be supplied from M1.

**Worth printing: yes.** It isolates the consequence of the OS-window endpoint while retaining battery protections, unlike flagged-inclusive, which restores catalog-excluded charging units too. It demonstrates sensitivity to an administrative span; it does not demonstrate that the registered threshold has been physically disproved. No finite thermal-publication bound can be derived from the supplied onsets, poll cadence or absence of a pressure flag. A future lag-protected variant would require an independently supported publication bound L and timestamp uncertainty, followed by an explicitly defined endpoint R + L and its sampling treatment; L is **measure first**.

### Q3. Prospective s5-p2

**Recommend (a), after a structural headroom/cooling diagnostic, with (c) as the fallback. Do not narrow pass-2's primary thermal window on M1 alone.** Its registration remains draft (configs/b6/packs/bytes-s5-p2/registration.json:353), so a fully disclosed procedure can still be fixed before collection; “draft” does not make it outcome-blind.

A longer pre-member cooldown can prevent a future episode by lowering the machine's initial thermal state and average duty. This differs from round-1 options 1–5 merely waiting for a previous episode to clear. M1 establishes that the latter do not directly rescue these hits; it does not establish that colder starts cannot prevent them.

**Measure first:** inspect recorded pre-member battery temperatures (scripts/run_campaign.py:4595) against collection order and episode incidence, then obtain the cooling trajectory and within-member temperature rise under the unchanged workload. A battery thermistor is a slow proxy, not a die-temperature sensor; 0.01 °C storage resolution is not sensor accuracy or a known relation to throttling. Prefer a validated relevant die-temperature/headroom signal if available. Determine cooling rate/time constants, ambient conditions, hysteresis and whether an isolated recovered member itself produces the tail episode.

Do not adopt “the highest temperature preceding a clean tail” as T_safe: one clean observation supplies neither a safety margin nor separation from affected observations. A threshold would need demonstrated room for the entire subsequent warm-up/request and delayed rise, including sensor uncertainty/lag. Check every member, including stage-first members; a hold only before quad a1 cannot protect the observed a2/b1/b2 onsets. The present data yield no justified temperature cutoff or fixed cooling duration.

| Prospective procedure | Additional wall-time arithmetic | What is and is not established |
|---|---|---|
| Measured headroom hold before each member | Sum of additional non-overlapping waits w_i / 60 min. A uniform measured wait w costs 50w/60 min for science, or 75w/60 if needed before all planned science/reference members. | May prevent internally generated episodes; success and w require measurement. |
| Lower duty by an added cooldown w | For measured hot-load duration L and actual cycle C, duty changes from L/C to L/(C + w). The adopted Llama member-wall mean is 266.313 s, excluding any separately added wait (derivation.json:3508). Use actual cycle and warm-up/request markers for L and C. | M1 gives no cooling slope or safe duty. Clean smaller models do not establish a safe duty for this model. |
| Hold until recharge and thermal recovery both complete | Additional wait is governed by the later satisfied condition, not the sum of simultaneous cooling and recharge waits. | Prevents carryover contamination; a new within-member episode can still occur. |

The 10–35 s episodes and 10–25 s onsets do not justify a 35 s cooldown, a 25 + 35 s cooldown, or a temperature margin. They describe pressure-state timing after the preceding load, not removal of stored heat before the next one. The measurement may show a much longer thermal time constant.

For scale, the existing 3,300 s kill-deadline margin (docs/registrations/block6_replication_DRAFT.md:524) corresponds to 55 min total, or 66 s per 50 science members / 44 s per 75 members **if all of it were genuinely available**. These are budget divisions, not recommended waits or a claim that the margin is unspent. Account for actual overhead, revised sizing, disk/custody streams and deadlines before choosing a procedure. Do not spend the separately purposed idle-wait allowance twice or release a known-unrecovered member merely because an arbitrary cap expired.

**Comparability and outcome-informed design:** thermal headroom changes acquisition conditions and may change decode operating points even with unchanged exclusions. Disclose that pass-2 minus pass-1 would mix procedure and session effects; do not interpret it as pure replication drift. With s5-p1's registered cell unavailable, a surviving registered s5-p2 point uses the existing one_pass fallback, and there is no numeric two-pass primary mean/difference to invent (bytes_pack_v1.md:271). If both refuse, there is no Llama point. Do not pair a request-window p1 sensitivity with an ordinary p2 primary as though they were matched passes.

Option (b) directly changes which observations count and is outcome-informed even if adopted before p2 runs. It would need a physical justification addressing publication lag and the sentinel, an explicit registration amendment and matched labelled reporting under both windows where evaluable. M1 supplies none of the missing lag calibration. Prefer retaining the full window and improving acquisition. If a justified preventive procedure cannot be established and budgeted before p2, run under the unchanged authorized design and accept fallback/unavailability; no top-up or selective replacement.

### Q4. Battery and recharge

**M1 changes no battery conclusion.** It locates thermal reads, not charging onset, charge-state publications, accumulator intervals or battery-pair failures. A hold that waits while charging protects later, non-onset members; it does not repair the member in which charging first begins. Because every affected b04–b06 quad also has a tail thermal hit, removing carryover charging alone does not restore any of those quads under the registered thermal rule. Exact battery-only rescue counts still require the battery journal. A colder/lower-duty schedule might also prevent recharge onset by changing the accumulated battery deficit, but that is a different, unmeasured counterfactual.

**Fix recharge carryover prospectively regardless of thermal.** Before the earliest member span and pre-capture battery endpoint, require the existing AC/charging/current admission conditions with fresh evidence, including first members of stages. Continue monitoring throughout each member. A single low-current endpoint, or holding for BAT-2's tau, does not prove recharge or accumulator recovery.

Use the production battery join to inspect the first member's prospective in-force publications: the selected accumulator interval must no longer bridge excluded recharge, and endpoint-pair requirements must be met. With nominal 60 s publications, obtaining an entirely post-recharge pair can require nearly two publication periods, about 120 s after charging physically ends; this is a phase-of-publication cost component, not a hard sleep or a complete wait bound. Check actual publication stamps, state freshness and pair verdicts. At 50 holds that component alone could approach 100 min if needed every time; do not assume it is needed every member or add it twice to overlapping cooling.

BAT-2 remains essential and unchanged. Negative battery current on AC discloses assist and adds signed energy; it does not itself prove adapter output exceeded 140 W. Recharge remains excluded. At the round-1 19–27 W recharge rates, 1 J corresponds to only 1/19–1/27 s, about 53–37 ms, far shorter than a 1 s SMC refresh. Thus an arbitrary brief “looks clean” hold cannot establish sub-joule safety. Check SMC/accumulator consistency on matched publication intervals as a diagnostic, recognizing shared gauge provenance; do not treat agreement as independent metrological validation or replace the registered edge bound.

## Recommendation

Preserve s5-p1's registered unavailable result and existing flagged-inclusive line. Admit the precisely labelled request-end OS-window sensitivity for description only, retaining battery and valid-record protections.

Before fixing s5-p2's procedure, perform the structural decode-frequency/sentinel check and measure cooling/headroom and recharge recovery. Prefer a preventive pre-member procedure with unchanged workload, census, arithmetic and full thermal window, with its actual resource cost registered and disclosed. If no physically justified, affordable prevention is established, retain the current design and accept the registered one-pass/no-point outcome. M1 is insufficient grounds to change the pass-2 primary window.

## Decisions I made

- The registered s5-p1 cell is unavailable; neither M1 nor a prospective procedure changes that. Five complete quads remain mandatory, so at least three additional clean quads would have been needed.
- H = 0 rules out direct rescue by clearing a preceding episode. It does not rule out prevention by lower starting temperature/duty.
- Sampling stop, decode end, sentinel end and member-hull end are different endpoints; preserve their recorded definitions.
- A measured poll gap bounds observation of published state, not the physical-state-to-publication delay. No new thermal lag, wait, temperature or energy-negligibility cutoff is derived here.
- The exact descriptive alternative is [original member start, sampling stop] with the production bracketing rule, changing only the science-member OS-pressure exclusion. Its potential 10/7 census is conditional on valid records and other boundary requirements.
- Preserve signed BAT-2 correction, edge terms, recharge exclusions, complete-quad selection, registered reference selection and NEG-8 transfer scale. Do not substitute the sentinel envelope for that allowance.
- Correct the round-1 overclaims about identical thermal channels, cap-hit causation/duration and cap-hit exclusion effect using the pinned code.
- No source edits, hardware captures, live controls, additional peer-seat consultation, selective reruns or replacement observations were authorized or performed. This report is the sole delivered change on [codex/by-thermal70-r2-sol](https://github.com/mpmdw/JouleWise/blob/codex/by-thermal70-r2-sol/.codex-report/BY-THERMAL70-R2-sol.md).

## NEEDS_RULING

1. **Print the additional descriptive selection?** Options: existing registered/flagged-inclusive lines only; add the exact Q2 OS-window sensitivity; substitute a new primary. Recommend adding Q2 beside the unchanged registered result. It changes a printed number and which units enter that description, so adoption is a ruling. Blocked work: implementing and computing that additional line on authenticated archive data, outside this report's write scope.

2. **Which prospective acquisition conditions may define s5-p2?** Options: unchanged collection; a measured headroom/lower-duty and recharge barrier with the full thermal window; a new primary exclusion window. Recommend the measured preventive procedure if the required structural evidence and resource budget support it; otherwise unchanged collection with the existing fallback. This changes which future observations can enter printed results and needs an explicit prospective registration decision. Record its dependence on p1 structural outcomes. Blocked work: procedure implementation, registration/pin/sizing changes and quiet-machine collection, all outside this consult.

No ruling is needed to apply the existing exclusions/minimum, inspect structural data, keep the registered fallback or decline to invent a lag/cooling bound.
