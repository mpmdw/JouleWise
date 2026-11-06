# ALIGN Stage 3 thermal gates — 2026-11-05

Branch: `lane/2026-11-05-align-thermal-gates`.
Base: `origin/lane/2026-11-05-align-smc-thermal` (`5202533f2`).
Merged `origin/lane/2026-11-05-align-token-budget` (`01b6cd2d8`) first,
with local merge commit `87cbe87d1`; Git resolved it without conflicts.
Implementation commit: `698a61082` —
`feat(align): add thermal gates, decode holds and exclusion desk`.
This report is a separate local documentation commit.
No push, registration or measurement launch.

## Intake, authority and boundaries

Selected the user's bounded [AGENT] implementation brief over the normal
queue head. Read the binding council design FIRST, at
`origin/lane/2026-11-05-align-window-council` (`219fb1515`), especially
§§1(c–e), 2.2 and 2.4–2.8. Read AGENTS/CLAUDE, Mission M0, stop card and
status/workspace/next-work pointers, current queue and do-not-do list,
authority map, orchestration, measurement methodology and targeted D-003,
D-009, D-050 and D-090 entries. No active stop card. The worktree began clean,
detached at the requested base.

The user's standing rules override coordination-state writes and the canonical
full-suite instruction. No changes to RUN_STATE, TASK_QUEUE, the state kernel
or test_gen_state; no kernel task registered. No network, external consult,
subagent, integration installation, actual SMC read, GPU workload, real model
load, quiet measurement, block-5 analysis pipeline or real measurement data
access. Absolute data/model references in configs were treated as text.
File reads stayed in this clone, synthetic temporary fixtures and Git's
explicitly allowed shared object store. No real restricted directory opened.

## Built (initial implementation; corrected by the Fix round below)

- Opt-in `EpisodeSpec.thermal` and `warmup_condition`, omitted when unset and
  included in new-cell policy identity/counterbalancing. All old cell bytes
  and legacy output paths remain unchanged.
- ALIGN-local prepare-to-cleanup 1 Hz sidecar using the existing SMC Reader,
  typed decoded values/errors, paired epoch/monotonic brackets and a
  bundle-local journal. An explicit per-run registry binds OS notify readings
  and the actual telemetry adapter's current complete PM frames. No second
  sampler or model is launched. The initial lane did not itself edit the core,
  but its merged #658 base changed the pinned monitor and SMC reader. The fix
  round below restores their exact pre-#658 pilot-9 bytes and relocates the
  extensions into ALIGN-local code. No pin rebind is claimed.
- Neutral benign warmup, first-member last-60-second idle medians, G0 after
  warmup/before the episode stamp, both temperature upper bands, 10 samples,
  60-second slow OLS slope ±0.2 °C/min, OS 0 / PM Nominal, 600-second cap.
  Timeout flags/proceeds; missing sensor state becomes a 300-second timed wait.
- Configurable G1 before turns >=1, always referenced to the episode's G0
  release; five qualifying samples and R1 cap <=300 seconds. No ratchet.
  Timeout or unobserved state stops before the next chat.
- Heavy-cell fixed-token holds, including lookahead array evaluation and
  explicit generation-stream synchronization before entry. Native generators
  whose stream cannot be identified refuse the hold path. Holds end at the
  next stream-dispatch stamp, including post-condition bookkeeping; final
  journal publication follows dispatch. Timeout retains partial IDs and stops
  before executing tools from the incomplete completion.
- Whole-turn token admission is unchanged. G0 precedes the episode deadman;
  G1/H consume **wall time**, as explicitly required by §2.2. Model-call alarms
  do not survive into a hold. A hold's own wall-deadline guard retains an exact
  partial exclusion and X7 when the actual deadline is exhausted. No deadline
  extension can silently defeat the outer member cap.
- Hold attribution splits decode into unowned `hold` segments; G1 occupies
  unowned gaps and G0 precedes the episode. Gross totals and I3 tiling remain
  intact. Turn-owned energy, including summed episode turn-owned energy,
  excludes gates/holds. Invalid interval custody refuses. Energy residual
  integration remains unchanged. Phase markers also split around holds so the
  pinned reducer sees disjoint phases.
- Additive thermal desk support derives U1–U3 from member records/journals,
  exposes U4 window-cluster t intervals and crossed-anchor moments, U5 light
  contrast/heavy paired-temperature bounds, and U6 frozen-fit residual checks.
  Inconclusive is distinct; W1 leaves U4–U6 unevaluable. Hardware and monitoring
  verdicts are separate. Registered OS spans must be explicitly bound and
  clipped; missing binding cannot pass U1.
- The deciding experiment fits the eight energies to template + arm S + actual
  start-hour drift, reports the arm effect and a 90% t interval with 4 df,
  implements the exact 10 J / 6 J rule, and prints same-arm repeat and per-turn
  tables. Missing/divergent identity cannot become a contrast pass.
- `scripts/align_v4_thermal_desk.py` reads an explicit immutable-bundle manifest
  and creates PILOT.json and THERMAL.md in a new directory. It ignores attempts
  to override measured quantities with roster tags. This is a thermal component
  for B9, not the full frozen-calibration v4 desk.

Details and the config/launch contract: `docs/align/thermal_gates.md`.

## Files touched by this lane after the merge

- `joulewise/align/apple/thermal.py`, `thermal_desk.py` (new).
- `joulewise/align/apple/workload.py`, `endpoint.py`, `campaign.py`,
  `diagnostics.py`, `pilot_analysis.py`.
- `joulewise/align/attribution.py`.
- `scripts/align_v4_thermal_desk.py` (new thin CLI).
- `tests/align/test_thermal_gate.py`, `test_attribution_holds.py`,
  `test_thermal_desk.py`, `test_thermal_legacy.py` (new).
- `docs/align/thermal_gates.md` and this report.

## Verification

Only targeted unittest modules were run. For every row below the exact command
was `python3.13 -B -m unittest <module>`; final outcomes:

| Module | Result |
|---|---|
| `tests.align.test_thermal_gate` | 19 PASS |
| `tests.align.test_attribution_holds` | 5 PASS |
| `tests.align.test_thermal_desk` | 12 PASS |
| `tests.align.test_thermal_legacy` | 1 PASS |
| `tests.align.test_decode_budget` | 15 PASS |
| `tests.align.test_attribution` | 36 PASS |
| `tests.align.test_apple_campaign` | 12 PASS (~108 s) |
| `tests.align.test_apple_endpoint` | 9 PASS (~26 s) |
| `tests.align.test_pilot3_cache` | 12 PASS |
| `tests.align.test_pilot4` | 18 OK, 1 skip (~28 s) |
| `tests.align.test_energy_residual` | 13 OK, 1 skip |

152 tests in the final module set, including 2 skips. All runtime, SMC and meter
work was synthetic. Cumulative reported unittest runtimes, including retries,
were under 6 minutes; no full suite or pytest. **Sequencing deviation:** one
short thermal-gate run (~1.4 s) inadvertently overlapped the still-running
campaign module. This was disclosed during work; subsequent module runs were
strictly serial. Do not read this as perfect compliance with the one-at-a-time
standing rule.

Additional checks:

- `python3.13 -B -m compileall -q joulewise tests scripts/align_v4_thermal_desk.py`: PASS.
- `python3.13 -B scripts/align_v4_thermal_desk.py --help`: PASS; opens no backend.
- `git diff --check` and staged equivalent: PASS.
- Protected/pinned-path diff against the pre-implementation merge: empty.
- v0–v3 legacy stage config tree diff against `c9a0a3943`: empty. Regression
  freezes all 84 stage JSON bytes and round-trips every episode spec; aggregate
  SHA-256 `dd19c9b4d065d1e2129aea096cce2b581cc546aaa8e0b4284dceed9124c4762f`.
- The merged decode-budget tests retain the four explicit Qwen3-30B anchor
  hashes and frozen legacy episode/transcript/turn/desk/policy output hashes.

Meaningful integration catches: nested hold/decode phase markers initially
failed the unchanged reducer; decode markers now split. Reconstructing event
floats from rounded ns stamps created tiny overlaps; original binary64 event
boundaries are retained. A synthetic CLI bundle without a GPU meter cannot
pass hardware checks. Final tests exercise these cases, non-ratcheting gates,
partial timeout custody, lookahead drain-before-entry, hold exit at dispatch,
full token budget overshoot under holds, unchanged tokens/transcript, meter
clock mapping and exact energy/time tiling.

## Open kit v4 / protocol v4 work and uncertainty

1. **Kit/launcher wiring.** Select `ThermalRegistry` in the v4 member launcher;
   the ordinary v3 runner does not select it automatically. Persist one
   window-local R in custody and propagate it across fresh member processes.
   Bind actual registered sampler-stream spans and the external OS/temperature
   journals, assign replay/contrast groups and pilot-7 reference IDs, fill/freeze
   R0/R1 slots and safe sizing. New-cell configs are not generated here.
2. **Inherited R0 selection mismatch.** The base tool proposes by tau <30 /
   >120 seconds and amplitude/noise. The council instead uses die t63 <=5 s,
   largest ΔT, and slow ΔT >=3 °C / tau <=300 s with longest tau. No pin was
   altered to reconcile that discrepancy. Its proposals are not automatically
   qualified council sensor slots.
3. **Protocol estimator details need a freeze.** U6's early/late unit and CI
   convention, the four-anchor moment formula, and the exact heavy-cell β_T fit
   are not fully specified by the council text. Implemented conventions are
   explicit: chronological episode halves within pair, equal pair weighting
   with Welch uncertainty; balanced crossed-anchor moments; paired differences
   through the origin. U6 is inconclusive unless its split rule is explicitly
   selected. These conventions are not a new registered scientific ruling.
   Protocol v4 must explicitly carry the fix-round included-member rule:
   omit X1–X4 from U1(a)/U2 values while retaining exclusion and timeout counts.
4. **Full B9/protocol integration.** The library consumes frozen-fit residuals;
   the CLI intentionally leaves U4–U6 inconclusive. The full desk must import
   unchanged frozen alternative/calibration commits `4d54cb47b` / `7fbd95e31`,
   join historical/R1 references, and apply the kit's frozen fields. B8, B10,
   B11, the amended D-only W1 production-shaped review, cold passes and CI
   remain lead work. No protocol v4 registration or acceptance certificate is
   claimed by this lane.
5. **R1 hardware qualification.** Sensor identity/coverage, real generation-
   stream draining on mlx-lm 0.31.3, token identity under holds, resume
   transients, sidecar overhead/cleanup, and real meter exclusions remain
   unverified. The fallback is refusal, never a thermal-control claim.
6. **Member-cap sizing — implementation gap resolved in fix round F5.**
   Thermal members share the R1-derived deadline from G0 entry, reserving
   zero extra G0 allowance. R1 must still measure the actual intercept and
   verify teardown slack; synthetic tests cannot certify an uninterruptible
   device call or live bundle completion below the outer kill.
7. **Other lanes.** XML/history rendering fixes B1/B2 are not in these two base
   branches and were not reimplemented. Merge the reviewed Stage-1 work before
   D runs. B7 hybrid checkpoints remain conditional on R0, not silently assumed.

Next exact step: the lead reviews this diff and integrates the launch registry,
reference/span custody and thermal library into kit v4 and the full frozen v4
desk; settle/freeze the protocol conventions, then carry B5/B6 through the
specified executing/cold reviews. R0/R1 and all live gates require a separate
clean operator session with agents gone. All evidence here is PROVISIONAL.


## Fix round

2026-11-05; branch `fix/666-review-round`, starting at PR head `4ae984e7f`.
Read `/private/tmp/jwsol/rev-666.json` first: one HIGH, five MEDIUM and five
LOW findings, no BLOCKER and no refuted notes. All eleven are fixed below.
Each finding group has its own commit and a defect-shaped regression observed
failing before its fix. This is implementation verification, not a fresh
independent review or a live thermal-control verdict.

Authority: read `FINAL-DESIGN.md` with `git show` from the named council ref.
`FINAL-DESIGN-AMENDMENT-1.md` is absent from that local ref and from local
history for that path; no network fetch was attempted. Followed the user's
explicit amendment instruction: W1 is Qwen3.8-27B only; Next is dropped and
Flash-Next is later. These fixes are model-independent and create no roster,
new model cell, registration, or measurement. The lead must reconcile the
actual amendment text when integrating the amended kit/protocol.

### Finding-to-commit map

Finding numbers below are the review array order, making the mapping stable
without inventing review IDs.

| Finding | Severity | Commit | Change and regression |
|---|---|---|---|
| F1: sidecar drift, PM parse cost, reference/window coverage | HIGH | `7fdc3d03f` | Absolute one-second deadlines; bracket only SMC; parse the latest complete PM frame once; true 60-slot windows with 54/60 observation floor. Nonzero SMC cost, 110 ms PM cost, phase jitter, reference capture and G0 release tested; all three new regressions failed before the fix. |
| F2: excluded members fail U1(a)/U2 | MEDIUM | `a637b30d6` | Only X1–X4-free members supply U1(a)/U2 values. Exclusions still count in U1(b); timeouts/admissions still count in U1(d). Tests cover one tolerated OS/PM exclusion and a hot G0 timeout, plus two-exclusion failure. Protocol handoff stated explicitly. |
| F3: X5 incorrectly fails U3 | MEDIUM | `f3bc85a38` | Divergent pairs report `excluded` with X5 in PILOT.json. U3 combines eligible pairs only and is inconclusive if none remain. Regression covers one excluded plus one valid pair and all-excluded input. |
| F4: monitor phase cannot verify gate release stamps | MEDIUM | `f8a13ba6f` | Coverage can use external monitor rows; release custody always uses the member's own sidecar journal. Nearby monitor temperatures are an independent cross-check. Missing decision samples are null/inconclusive; observed mismatches remain failures. Regression uses a shifted monitor journal and missing sidecar samples. |
| F5: G0 sits outside member deadman slack | MEDIUM | `b86ec3124` | Thermal deadline starts at G0 entry with zero extra planned allowance, conservatively bounding both G0 and episode by the same R1-derived slack. Budget custody prints deadline/origin. A 600-second G0 timeout followed by a long call yields X2/X7 and retained evidence instead of receiving a second full budget. |
| F6: inherited changes violate pinned measurement-core boundary | MEDIUM | `54bd1ea9f` | Restore `hazards/smc.py` and `hazards/monitor.py` exactly to pre-#658/pilot-9 bytes. Put extra decoding/enumeration and the opt-in monitor subclass/launcher in ALIGN-local files; preserve ordinary launch selection. Correct unchanged-source claims. Byte-hash regression failed for both files before restoration; fake enumeration, policy wiring and monitor-loop tests pass. No pin rebind. |
| F7: temporary-path alias breaks anchor byte regression | LOW | `072213d09` | Normalize both resolved and unresolved roots. The original anchor regression now always exercises a synthetic symlink, fails before normalization, and retains its original expected hashes. |
| F8: deadman during lookahead drain loses partial turn | LOW | `436bcd73c` | Drain catches `DeadmanExpired` through the same cancellation path as stream advancement. Regression retains all 256 returned tokens, closes the stream, and checks partial endpoint bundle IDs/events. Two opt-in real-MLX array tests are added, skipped here. |
| F9: unmapped/unbounded energy reaches thermal decisions | LOW | `8d5aba296` | Gate U3/contrast on actual `clock.*`, trace and uncovered-duty flags and finite energy uncertainties. Export unavailable bounds as null with flags. Regressions cover missing/ambiguous/mismatched mappings, missing uncertainty, duty gaps, infinity/NaN/null bounds and derived attribution flags. |
| F10: unobserved stops, lost capability, skipped rows, stale PM | LOW | `f80932399` | Follow the binding design: unobserved G1/H waits then proceeds with X4; actual timeouts stop but retain capability scores; X7 stays incomplete/unscored. Check all queued samples and require PM observation age <=2 s at G0. Six pre-fix failures cover each behavior and endpoint scoring. |
| F11: U4 checks only one of two required conditions | LOW | `b3176b9ca` | Return both sentinel equivalence and anchor moments and combine them. Acceptance rejects a lone pass status. Regression shows passing anchors cannot hide failing sentinels; either missing part is inconclusive. |

No findings were deferred or rejected. The final documentation/whitespace
commit records this handoff and removes one trailing blank line found by
`git diff --check`; it changes no runtime behavior.

### Files touched

- Runtime/desk: `joulewise/align/apple/{thermal,thermal_desk,workload,endpoint}.py`.
- ALIGN-local core boundary: `joulewise/align/apple/{smc,temperature_monitor}.py`,
  `scripts/align_temperature_monitor.py`, `scripts/align_smc_enumerate.py`,
  `joulewise/b5/driver.py`, plus restoration of `joulewise/hazards/{smc,monitor}.py`.
- Tests: `tests/align/{test_thermal_gate,test_thermal_desk,test_decode_budget,
  test_measurement_core_boundary,test_thermal_mlx}.py` and
  `tests/hazards/{test_smc_enumeration,test_temperature}.py`.
- Documentation: `docs/align/{thermal_gates,smc_temperature}.md` and this report.

### Verification

All unittest commands ran serially, one module at a time. The command for each
module row is `python3.13 -B -m unittest <module>`. This table records final
module results, not pre-fix red runs. Repeated targeted runs plus these checks
remain well below the user's approximately 20-minute test-time limit. No full
suite, pytest, network, pipeline, real measurement data, real restricted path,
or native SMC/MLX workload was run. Coordination files were left untouched.

| Module | Final result |
|---|---|
| `tests.align.test_thermal_gate` | 29 OK |
| `tests.align.test_thermal_desk` | 18 OK |
| `tests.align.test_measurement_core_boundary` | 1 OK |
| `tests.hazards.test_smc_enumeration` | 18 OK |
| `tests.hazards.test_temperature` | 13 OK |
| `tests.align.test_thermal_mlx` | 2 skipped (native Metal opt-in) |
| `tests.align.test_decode_budget` | 15 OK, including aliased-path anchor bytes |
| `tests.align.test_attribution_holds` | 5 OK |
| `tests.align.test_attribution` | 36 OK |
| `tests.align.test_thermal_legacy` | 1 OK |
| `tests.align.test_apple_endpoint` | 9 OK |
| `tests.hazards.test_monitor` | 36 OK, 1 skipped |
| `tests.align.test_apple_campaign` | 12 OK (~65 s) |

Also ran `python3.13 -B -m unittest tests.hazards.test_smc.EncodingTests tests.hazards.test_smc.ReaderTests`: 12 OK, 1 skipped; no live SMC class ran.

The distinct final verification set totals 207 tests: 203 passed and 4 skipped.
All touched test modules were rerun after their fixes. The full suite remains
intentionally unrun under the standing machine-load restriction.

Additional checks:

- `python3.13 -B -m compileall -q joulewise tests scripts/align_smc_enumerate.py scripts/align_temperature_monitor.py`: PASS.
- `python3.13 -B scripts/align_temperature_monitor.py --help` and
  `python3.13 -B scripts/align_v4_thermal_desk.py --help`: PASS; no backend opened.
- `git diff --check 4ae984e7f`: PASS after whitespace cleanup.
- `git diff c9a0a3943 -- joulewise/hazards/smc.py joulewise/hazards/monitor.py`:
  empty (exact pilot-9 core restoration).
- Diff against starting PR head for `RUN_STATE.md`, `TASK_QUEUE.md`,
  `docs/process/state_kernel.json`, `tests/test_gen_state.py`: empty.

### Lead handoff and uncertainty

Next exact step: review the eleven local fixes and handoff commit, reconcile
Amendment 1 from the lead's copy, then run native tests outside this sandbox:

```sh
JW_ALIGN_MLX_NATIVE_TESTS=1 python3.13 -B -m unittest tests.align.test_thermal_mlx
```

Those two tests use real MLX arrays in a small synthetic lookahead stream;
they do not load weights or qualify the actual pinned mlx-lm generator.
The quiet R1 gate still owes pinned mlx-lm 0.31.3 token identity, pending-work
draining, hold resume transients, SMC identity/refresh/coverage, actual sidecar
cost and cleanup, measured member intercept/teardown slack and live meter
attribution. Agents must be absent for quiet measurements. An uninterruptible
native/OS call remains bounded only by the external runner; this round does
not claim to make it interruptible.

The v4 kit/launcher, window-reference custody and frozen protocol conventions
remain the lead integrations already listed above. Protocol v4 must state
included-member U1/U2 values, X5 pair exclusion, conjunctive U4, timed X4 waits,
and capability scoring for thermal timeouts before registration. No frozen
calibration, estimator constants, model roster or live result was changed.
All hardware evidence remains PROVISIONAL. No push or external write occurred.
