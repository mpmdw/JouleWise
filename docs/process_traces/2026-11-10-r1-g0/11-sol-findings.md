```json
{
  "schema": "claude-codex-report/v1",
  "genre": "root_cause",
  "status": "findings",
  "completion": "complete",
  "summary": "Reference mismatch is real, but changing the reference alone still times out; no recorded candidate demonstrates a safe R1 release.",
  "workspace": {
    "base_requested": null,
    "base_mode": null,
    "head_start": null,
    "head_end": null,
    "upstream_end": null,
    "branch": null
  },
  "pathspec": [
    "docs/process_traces/2026-11-10-r1-g0/11-sol-findings.md"
  ],
  "unowned_dirty": [],
  "verdict": {
    "cause": "confirmed",
    "remediation": "proposed"
  },
  "verification": [
    {
      "id": "V1",
      "kind": "other",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -u -B -c 'from pathlib import Path; s=Path(\"docs/process_traces/2026-11-10-r1-g0/11-sol-findings.md\").read_text(); exec(s.split(\"# REPLAY_SOURCE_BEGIN\\n\",1)[1].split(\"\\n# REPLAY_SOURCE_END\",1)[0])'",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "REPLAY_DONE"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "REPLAY_DONE\\s*$"
      }
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "lead_ruling",
      "level": "blocking",
      "text": "NEEDS_RULING before implementation: changing R1's reference population or step-30b cap changes registered semantics and printed fields.",
      "needs": "Choose a matched resident-runtime/capture reference for R1 and rule on extending step-30b to the existing 1200 s ceiling; preserve W1's single shared reference."
    },
    {
      "id": "F2",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "R1 is censored at its original G0 exit; R0 has no bound OS/PM source and pilots have no SMC temperatures. No temperature-to-electrical-energy transfer coefficient is available within the permitted inputs.",
      "needs": "Lead-controlled quiet thermal continuation and permitted energy/temperature characterization before claiming release safety at 1 J."
    },
    {
      "id": "F3",
      "kind": "environment",
      "level": "nonblocking",
      "text": "No Git or network operation was performed. Workspace identity and dirty paths were not inspected; null fields and an empty unowned_dirty array are not a clean-tree assertion.",
      "needs": ""
    },
    {
      "id": "F4",
      "kind": "residual_risk",
      "level": "nonblocking",
      "text": "Full-inventory journals do not reproduce the two-key sidecar's coverage geometry; sensor-swap results are explicitly temperature-only diagnostics.",
      "needs": ""
    }
  ]
}
```

## Causal chain

**Finding:** the reference is mismatched, but the claim that this is only a reference problem is disproved by execution. Replacing it with the member's own idle median still gives **zero releases and one 600 s timeout**. At that exit, the host remains warmer than its own idle state. None of the defensible candidates establishes a safe R1 release on the available trace.

**Authority and read boundary.** I read the common brief, diagnosis, RUN_STATE items 251–253 and targeted intake/status regions, queue/do-not-do pointers, M0, orchestration and bridge protocol. The stop card is NONE; item 253 says the measuring chain exited and the lead restored the machine. This is offline [AGENT] analysis. No Git command, network operation, measurement, calibration value, workload output, commit, or write outside this report was used. Only structural phase times and the timestamp column were projected from events and idle telemetry; their power/workload values were not inspected. The other finder seat was not consulted.

Absolute read-only roots:

- M = /Users/edr/night-custody/measurement/JouleWise-measurement-20261102-align-pilot2 (head supplied by brief, not Git-verified).
- B = /Users/edr/night-align.
- R1 member = B/r1-20261111T014106Z/night/align-r1/step_30b.

M/docs/align/pilot_protocol_v4.md WP14(b) requires W1's **one first-member pre-warmup 60 s median**, carried unchanged to consumers. M/docs/align/r1_runtime_contract.md instead requires R1 model members to override self-capture with the **last 1,200 s mean of the no-runtime soak**. Current code follows that R1 contract; it has not accidentally omitted an existing required capture. Step-30b expressly retains the 600 s default; the existing 1,200 s exception applies to specified later R1 kinds.

The thermal/structural evidence gives this chain:

1. Soak reference TV0h = 34.011297 °C, Tf08 = 25.489065 °C. Registered bands are max(1 °C, 3 × detrended soak SD). The measured three-SD values are 0.023169 °C fast and 0.234162 °C slow, hence both bands are **1 °C** and the slow ceiling is **26.489065 °C**.
2. The final 60 s of actual idle capture, delimited by its timestamp column ending at epoch 1794365606.4337342, have Tf08 median **26.548594 °C**, mean **26.550057 °C**, detrended SD **0.075141 °C**, range **26.340000–26.706562 °C**, and slope **−0.049952 °C/min**. Its mean is **1.060992 °C above the soak**, already **0.060992 °C above the ceiling**. This independently confirms the operating-state mismatch.
3. The exact pre-warmup 60 s convention gives medians TV0h **34.106462 °C**, Tf08 **26.571250 °C**: slow offset **1.082185 °C**, corrected ceiling **27.571250 °C** with unchanged band. Both baseline definitions are reported; no quiet plateau was manually trimmed.
4. G0 starts with Tf08 **55.535938 °C** and exits after **600.049135 s**. Its final decision sample is at **599.666557 s**, with TV0h **34.292130 °C**, Tf08 **28.406876 °C**. Slow temperature is **1.917811 °C above the soak ceiling**, **1.835626 °C above its own pre-warmup idle median**, and still **0.835626 °C above the corrected ceiling**. The recorded slow slope is **−0.038629 °C/min** and status is nominal. Slow absolute temperature remains a real blocker after reference correction.
5. Frozen ThermalSession.wait times out. Only a released G0 creates an episode reference; episode.g0_unreleased:0 prevents turn 0. R1's completeness check rejects the zero-turn member and refuses the chain.

The source of the offset is not established. Resident runtime/model, capture, inventory sampling and preparation differ from the soak. A storage-adjacent Tf08 and heating from capture writes remain hypotheses, not demonstrated sensor location or an isolated causal power source.

**Execution method.** The program embedded below reads absolute paths and was executed. R1 was checked sample by sample with the frozen slow_slope/coverage helpers and by calling the **actual frozen ThermalSession.wait**, using recorded snapshots, a virtual clock and an in-memory event sink. No collector constructor, thread, hardware reader or filesystem journal sink is invoked. Virtual polling uses the production 1 s interval. Release times below are recorded decision-sample times; the synthetic polling time is also given. Historical scheduler overhead is not synthesized.

Every R1 counterfactual stops at the **original G0 exit**. Sidecar data after the refusal occurred during capture teardown, so it cannot prove what a continuing otherwise unchanged G0 would have done. A 1,200 s candidate is **right-censored**, not an observed release or timeout.

| R1 candidate | Derivation / change | Releases / timeouts / censored | Release time; fast / slow excess above own pre-warmup median |
|---|---|---|---|
| A: registered | Soak reference; both δ = 1 °C; cap 600 s | 0 / 1 / 0 | None |
| B: own idle | Both pre-warmup last-60-s medians; same bands/cap | 0 / 1 / 0 | None |
| C: measured idle spread | Soak; max(1, 3 × last-60-s actual-capture residual SD) = 1 °C for both | 0 / 1 / 0 | None |
| D: compensate slow offset in δ | Soak retained; δ_slow = 26.571249962 − 25.489065073 + 1 = **2.082184888 °C**; fast unchanged | 0 / 1 / 0 | None |
| E: cap only | A with existing allowed maximum 1,200 s | 0 / 0 / 1 | No release through 599.667 s of unchanged-state samples |
| F: own idle + longer cap | B with existing allowed maximum 1,200 s | 0 / 0 / 1 | Same censoring |
| I: inflate pre-warmup SD (rejected diagnostic) | B with slow band 3 × pre-warmup detrended SD = **3.019823565 °C**; fast remains 1 °C | 1 / 0 / 0 | **591.666558 s**, virtual poll **592 s**; **+0.171724 / +1.863437 °C** |
| Matched resident-runtime/capture soak | Recompute reference under matched background, preserve δ | Not observable | No matched soak exists; B is offset evidence, not a replay of an unrecorded soak |

I exposes a contamination trap: the last pre-warmup minute rises to **31.001875 °C**, with slope **+2.859895 °C/min** and detrended SD **1.006608 °C**. Treating preparation heating as idle noise manufactures a large allowance. The structurally delimited final minute of actual idle capture instead gives **3σ = 0.225423 °C**, below the inherited 1 °C floor.

Minimizing the slow allowance over observed ten-sample runs that already satisfy fast/slope/status conditions requires at least **3.031871893 °C above the soak**, or **1.949687004 °C above own idle**, with release sample **592.666573 s**. Derivation: maximum Tf08 in each qualifying consecutive run, minus its reference, then minimum across runs. These are **post-hoc diagnostic bounds**, not proposed tolerances. Choosing them would fit admission to this refusal.

**Every earlier root and thermal record.** Archive mirrors and checked-in fixture journals inside source clones are not independent hardware records. Replay uses primary custody copies, not both copies. Earlier nights have no matching no-runtime soak that can legitimately be replaced by this night's absolute soak temperature.

| Root under B | Thermal samples: idle / load / recovery | Strict frozen G0 evidence | Temperature-only post-load replay, all reference/band candidates |
|---|---:|---|---|
| r0-v4-20261106T1605Z | No SMC journal | No inputs | Not replayable |
| r0-v4-20261106T1705Z | No SMC journal | No inputs | Not replayable |
| r0-v4-20261106T2235Z | No SMC journal | No inputs | Not replayable |
| r0-v4-20261107T0132Z | No SMC journal | No inputs | Not replayable |
| r0-v4-20261107T0149Z | No SMC journal | SMC attempt refused before a journal exists | Not replayable |
| r0-v4-20261107T0631Z | 300 / 900 / 78 | No bound OS/PM source → immediate thermal.status_source_missing | 0 releases; censored at **77.069435 s** |
| r0-v4-20261107T0720Z | 300 / 900 / 288 | Same missing-source fault | 0 releases; censored at **287.009917 s** |
| r0-v4-20261107T0810Z | 300 / 900 / 600 | Same missing-source fault | 0 releases; last sample **599.038334 s** |
| r0-v4-20261108T0115Z | 300 / 522 / 0 | Same missing-source fault | No recovery to replay |
| r0-v4-20261108T0140Z | 30 / 0 / 0 | Same missing-source fault; insufficient baseline | No recovery |
| r0-v4-20261108T0224Z | 338 / 587 / 0 | Same missing-source fault | No recovery |
| r0-v4-20261108T0550Z | 357 / 900 / 600 | Same missing-source fault | 0 releases; last sample **599.107711 s** |
| pilot-v7-20261105T015948Z | **4,629 OS-status readings**, no SMC samples | 4,625 level 0; 4 level 1; no G0 temperatures/fresh PM source | No temperature release inferable |
| pilot-v8-20261105T102850Z | **4,619 OS-status readings**, no SMC samples | All level 0; same missing inputs | Same |
| pilot-v9-20261105T231016Z | **4,645 OS-status readings**, no SMC samples | 4,640 level 0; 5 level 1; same missing inputs | Same |
| R1 idle_soak/sensors | **1,801 readings**, about 1,800 s | No bound status source → immediate missing-source fault | Thermal baseline, not a measured G0 release |

The soak's first-minute-reference temperature-only challenge releases at **91.010047 s** after its 60 s entry, with TV0h **34.033657 °C** and Tf08 **25.645624 °C**. These are **+0.022360 / +0.156559 °C** above the accepted last-1,200-s soak means, respectively. The actual frozen G0 still faults immediately because status is unbound; this is not a full-rule release.

R0 A uses the whole idle median as a proxy reference; B uses its final-60-s median. These are **conditional physical diagnostics**, not actual original-rule G0 counts. C and I reduce to 1 °C because every R0 final-60-s detrended SD is below 1/3 °C. D gives B's slow ceiling and A's fast ceiling; E/F change only the cap. All seven candidates produce zero two-sensor temperature releases on all four available post-load curves. For A/B/C/D/I there are two short censored traces and two traces ending at about 599 s without release; E/F are censored in all four. No sample after 600 s exists to evaluate a 1,200 s cap.

Strict R0 totals are **zero releases, zero adjudicable full-rule timeouts, seven missing-status-source faults**. The four post-load curves are finite observations, not seven completed G0 attempts. Applying the rule to pilots' absent temperature samples cannot release; missing inputs must not be counted as cold admission. Projected empty thermal histories take the frozen unobserved path (300 s) rather than inventing a temperature.

Direct substitution of full-inventory journals also fails narrow-sidecar rolling coverage: multi-key read brackets and the 100 ms grid tolerance have different geometry from a two-key collector. The physical-only diagnostics therefore use real preceding-60-s OLS observations with at least **54 = 0.9 × 60** valid slow-sensor readings, ten consecutive passes and sample gaps ≤2 s, and omit unavailable OS/PM and strict-grid latches. They do not fill missing temperatures, change custody, or certify production releases.

An additional challenge scans every sufficient R0 idle stream from its first 60 s, referencing that initial minute rather than a future warmed baseline:

| R0 suffix | Conditional thermal release after that entry | Tf08 excess above final-60-s idle median |
|---|---:|---:|
| 1107T0631Z | None through 239.118 s | — |
| 1107T0720Z | None through 239.150 s | — |
| 1107T0810Z | None through 239.028 s | — |
| 1108T0115Z | **9.128899 s** | **−0.352812 °C** |
| 1108T0140Z | Insufficient baseline | — |
| 1108T0224Z | **9.159195 s** | **−0.057188 °C** |
| 1108T0550Z | **55.189658 s** | **−0.183750 °C** |

These are 3 conditional temperature releases and 3 censored idle scans, not full-rule passes. The first three final idle medians are **34.623436, 34.405937, 34.747501 °C**, with slopes **−0.758626, −0.728847, −0.592000 °C/min**. Their own idle is still cooling. Being process-idle does not establish thermal equilibrium.

**Sensor census.** The replay tests **all 44 heatsink candidates** from accepted R0's response.heatsink_candidates plus diagnostic TVFh and intentionally invalid s_slow = s_fast = TV0h: **46 × 5 = 230** physical-only candidate/trace combinations across four R0 recoveries and R1 inventory. The candidate set comes from classification, not favorable outcomes. Each of the 44 heatsink keys and TVFh gives **zero releases on each curve**: 225 censored combinations. The TV0h negative control gives one censoring on the short 77.069 s trace and these four releases:

| Curve | Release sample s | TV0h excess above own baseline | Tf08 excess above own baseline |
|---|---:|---:|---:|
| R0 1107T0720Z | 210.125501 | +0.185516 °C | **+1.718750 °C** |
| R0 1107T0810Z | 217.101972 | +0.151958 °C | **+2.039997 °C** |
| R0 1108T0550Z | 222.042354 | +0.962254 °C | **+9.981562 °C** |
| R1 inventory | 193.416682 | +0.487331 °C | **+5.338438 °C** |

WP14 forbids one key or aliases for both roles and manual substitution of the ruled slow pick. Dropping the slow observable buys a hot start, not evidence of recovery. All sensor medians, outcomes and release values print in the replay.

## Remediation

**Recommendation, PROVISIONAL:** correct R1's reference operating-state population, retain both selected sensors and the existing absolute-temperature/slope/status tests, and investigate the remaining cooling duration. Do not widen a band just to admit the recorded tail.

An authenticated resident-runtime/capture idle reference removes the measured approximately 1.06–1.08 °C background offset. Existing pre-warmup median custody supplies a concrete implementation candidate. A soak with the same resident runtime/model, sampling and capture background preserves a single stated soak population more directly. Neither option has demonstrated a corrected 600 s release: B actually times out.

The already-allowed **1,200 s ceiling** is a bounded next candidate for step-30b's wait, not a new physical guarantee. It was registered for later R1 kinds after long-load recoveries reported at roughly 840–1,040 s, and validate_gate_policy enforces it. Here F is censored. Keep fail-closed timeout behavior if the matched-state reference/band is not reached. This data does not derive a sufficient new cap or justify increasing the current ceiling.

**Decisions I made.**

- Apply the frozen ten samples, one-sided bands, 60 s OLS, ±0.2 °C/min, 90% coverage, fresh ≤2 s PM status and 600 s default; each variation changes only its named term.
- B uses the protocol's exact pre-warmup median; independent noise/offset diagnosis uses the structural idle-capture endpoint. No hand-picked plateau or cross-night absolute temperature borrowing.
- Distinguish missing inputs, faults and finite-horizon censoring from timeouts and releases.
- Preserve W1's single shared reference. Giving every later member its own reference is not authorized by WP14(b) and risks normalizing prior heat. R0's unsettled idle slopes show why this matters.
- Retain selected Tf08; no alternative slow key offers an observed release.
- Preserve PROVISIONAL remedy status. This is replay of historical live thermal records, not a new hardware validation.

**NEEDS_RULING before implementation.** Question: should R1's planning-step reference population change to authenticated resident-member idle or to a matched runtime/capture soak, and should step-30b join the already-registered 1,200 s kinds? Options: median capture reuses custody and removes the offset; a matched soak preserves one population but needs a controlled thermal observation; band widening admits more heat. Recommendation: match the reference population, retain the band, and test the existing longer cap with explicit censoring. Blocked work: choosing/applying changed reference semantics/cap and claiming a safe successful re-arm. Those choices change which samples count or a printed number. No code change or measurement was attempted.

## Disproved alternatives

- **Own idle alone fixes it:** B still times out at 600 s in the actual frozen wait.
- **Ordinary idle spread needs a larger band:** genuine final-minute capture noise gives 3σ = 0.225423 °C, below 1 °C. The 3.019824 °C allowance mixes preparation heating into noise.
- **The short exponential fit proves it can never cool to the ceiling:** refitting the same tail over consecutive 60 s start boundaries gives incompatible asymptotes at essentially the measured noise scale:

| Fit window, s after G0 entry | Asymptote °C | τ s | RMSE °C | Extrapolated own-idle +1 °C crossing |
|---|---:|---:|---:|---|
| 240–599.667 | 27.664461 | 253.397541 | 0.079911 | None |
| 300–599.667 | 27.221278 | 335.888438 | 0.078380 | 1,007.759292 s |
| 360–599.667 | 26.099090 | 561.545191 | 0.077407 | 845.177857 s |

These diagnostic fits minimize squared residuals for T∞ + A exp(−t/τ), positive τ. Each start moves one existing 60 s window. The last fit even crosses the original soak ceiling at about 1,591.136 s. They refute certainty about “never”; they do not establish that any extrapolation is correct. Multiple thermal time constants, background changes or noise can explain their sensitivity.

- **Swap to a fast observable:** none of the slow alternatives releases in the supported interval. The invalid fast-only control admits up to 9.98 °C extra Tf08 heat in R0 and 5.34 °C in R1.
- **Nominal status proves cold:** R1 is nominal while Tf08 remains 1.84 °C above own idle. Pilots' OS levels cannot reconstruct missing temperatures or PM freshness.

## Residual risk

**Physical effect size and the approximately 1 J attribution limit.** For the rejected fast-only R1 release at **193.416682 s**, Tf08 is **31.895000 °C**, **5.338438 °C** above its inventory baseline. It subsequently drops **3.488125 °C** during **405.999982 s** of remaining unchanged-state observations. Trapezoidal integration of measured excess above that baseline gives **1,226.649432 °C·s**.

For I's frozen-wait release, Tf08 is **1.863437 °C above its sidecar baseline**. Only **8 s** of same-state samples remain. The observed drop is **0.027811 °C** and excess area **15.112345 °C·s**. That short observation cannot bound its complete remaining tail. A small slope is not a stored-heat bound.

A legitimate conversion to the smallest printed energy quantity is conditional:

- Thermal excess Q = C_eff × ΔT. Q ≤1 J would require C_eff ≤ **1/5.338438 = 0.187321 J/K** for fast-only, or **1/1.863437 = 0.536643 J/K** for I. No effective heat capacity was measured; thermal Q is also not automatically electrical energy charged to a run.
- If electrical error follows ΔP = κ × ΔT, the supported fast-only tail gives ΔE = κ × 1226.649432 J. Keeping even that finite tail below 1 J requires |κ| ≤ **0.000815229 W/K**, derived as 1/1226.649432. I's finite 8 s slice requires |κ| ≤ **0.0661711 W/K**, from 1/15.112345; the unknown later tail prevents a run-level bound.
- More generally, measured run sensitivity ΔE = β × ΔT_start would require |β| ≤ **0.187321 J/K** or **0.536643 J/K**, respectively. No β is inferable from temperature alone.

Thus **the permitted records cannot establish whether this heat costs less than, equals, or exceeds 1 J on a printed run energy**. The measured tail and the coefficient bounds needed for that claim are given above. Degrees or degree-seconds cannot be converted directly into joules, and stored heat must not be presented as electrical work. The inherited 1 °C floor is an existing setting, not a newly established 1 J equivalence. No calibration or workload result was read to supply the missing coefficient.

The lead's remaining evidence gate requires a clean [QUIET-MAC] session: retain matched background conditions through the cooling continuation, observe whether the corrected reference/band is reached, then obtain permitted temperature-to-electrical sensitivity before pricing the heat against the approximately 1 J attribution limit. This agent started no measurement.

**Reproducibility and verification.** Only this report was written. No canonical test suite was needed for a thermal analysis with no product-code edits. The embedded program uses Python's standard library and the frozen read-only gate module, prints per-record/per-sensor results and input SHA-256 digests, and ends with REPLAY_DONE. Its virtual clock does not sleep on the host. Numerical fit search bounds are optimizer bounds, not proposed thermal tolerances; fitted optima lie inside them. The program keeps full-inventory physical projections distinct from production gates.

**Observed input digests (SHA-256).** These bind the primary thermal files used in the replay; the complete source prints them again.

```text
SHA256 /Users/edr/night-custody/measurement/JouleWise-measurement-20261102-align-pilot2/joulewise/align/apple/thermal_gates.py 2d4917b7e499630a653fcf8a0d0dbec4e7db87193b16df92e29e82faa04eda37
SHA256 /Users/edr/night-custody/measurement/JouleWise-measurement-20261102-align-pilot2/joulewise/align/apple/r1_runtime.py 4bcd8b70f94f98de63b444290b172f14982c7206872745b2130065952ee53fa5
SHA256 /Users/edr/night-align/r1-20261111T014106Z/night/align-r1/step_30b/runs/align-v4-r1-step-30b/outputs/align_thermal.jsonl ebc7a978637090713fa4525acea15523ccfccc552ef8ee0e227b6e639b433ef6
SHA256 /Users/edr/night-align/r1-20261111T014106Z/night/align-r1/step_30b/inventory/inventory_journal.jsonl 5852d01eeadf0d8c89209f002d973e206160f78c5130267ae9c85c103c9e9e20
SHA256 /Users/edr/night-align/r1-20261111T014106Z/night/align-r1/idle_soak/sensors/align_thermal.jsonl 9537751c31358acc506e6e1cd863ed44b382f80ee4e2c6c767006d4c994df0b6
SHA256 /Users/edr/night-align/r0-v4-20261107T0631Z/smc/samples.jsonl 022c868185f9d19d406d3c3c88de8dca21acaec4c838477502a1b8dfa881a68b
SHA256 /Users/edr/night-align/r0-v4-20261107T0720Z/smc/samples.jsonl 6d8eded0069ec313e76ddef7873a2a456eb2e3ad2784f7ac5ea68bee6fe79c5a
SHA256 /Users/edr/night-align/r0-v4-20261107T0810Z/smc/samples.jsonl 16aa5307ffc24f55bc20d66823e8c9375d84da6ac723fa77b23d024f66244984
SHA256 /Users/edr/night-align/r0-v4-20261108T0115Z/smc/samples.jsonl 1ee178271f16d60b0329a13090bfa788eaca0b1a69d25c94c7b4c1e9ae149c82
SHA256 /Users/edr/night-align/r0-v4-20261108T0140Z/smc/samples.jsonl db6fe9fe3eddb2ea6ef34b849da85461b61679f4093b11188b0774a32971cc5f
SHA256 /Users/edr/night-align/r0-v4-20261108T0224Z/smc/samples.jsonl 77410460b8d9570b98a1abed31eaf784549c472d3e573cc872b18e033ef22879
SHA256 /Users/edr/night-align/r0-v4-20261108T0550Z/smc/samples.jsonl 79998635cc29caa2810389584a895810413ff1cbd550a0182dae7bed32804b94
SHA256 /Users/edr/night-align/pilot-v7-20261105T015948Z/custody/hazards/monitor/thermal.jsonl 3ced529e9c2134abf8b3c0c23ce0da9384d7a800ac02367a9c7088804134a2b3
SHA256 /Users/edr/night-align/pilot-v8-20261105T102850Z/custody/hazards/monitor/thermal.jsonl a570a3ae154c2bc39346006206e69b8b8f42fab825bca7b1463bc3b094793180
SHA256 /Users/edr/night-align/pilot-v9-20261105T231016Z/custody/hazards/monitor/thermal.jsonl 111212df547e3b70866b0faf0a83db40f43e89bbcdf5c2919c8b68854f2e1c8f
```

```python
# REPLAY_SOURCE_BEGIN
import sys,json,math,statistics as st,hashlib,bisect,collections
from pathlib import Path
M=Path('/Users/edr/night-custody/measurement/JouleWise-measurement-20261102-align-pilot2')
B=Path('/Users/edr/night-align')
sys.path.insert(0,str(M))
from joulewise.align.apple.thermal_gates import sample_rows,slow_slope,_window_coverage
NS=10**9
def load(p): return [json.loads(l) for l in p.open() if l.strip()]
def norm_inv(raw):
 return [dict(kind='sample',monotonic_ns=r['started']['monotonic_ns'],
  epoch_ns=0,started={'monotonic_before_ns':r['started']['monotonic_ns']},
  finished={'monotonic_after_ns':r['finished']['monotonic_ns']},status={},**r['values']) for r in raw]
def stats(rows,key):
 a=[(r['monotonic_ns']/NS,r['sensors'][key]) for r in rows if key in r['sensors'] and key not in r.get('errors',{})]
 if len(a)<2:return None
 x0=a[0][0];x=[t-x0 for t,y in a];y=[y for t,y in a];xm=st.mean(x);ym=st.mean(y)
 beta=sum((t-xm)*(v-ym) for t,v in zip(x,y))/sum((t-xm)**2 for t in x)
 sd=math.sqrt(sum((v-ym-beta*(t-xm))**2 for t,v in zip(x,y))/(len(y)-2))
 return dict(n=len(y),mean=ym,median=st.median(y),min=min(y),max=max(y),sd=st.stdev(y),resid_sd=sd,slope=beta*60)
def window(rows,end,seconds=60):
 return [r for r in rows if end-seconds*NS<=r['monotonic_ns']<end]
def evaluations(rows,fast,slow):
 times=[r['monotonic_ns'] for r in rows];out=[]
 for i,r in enumerate(rows):
  t=times[i];j=bisect.bisect_left(times,t-61*NS)
  hist=rows[j:i+1]
  # Preserve the original collector grid even when using a rolling history.
  if j:hist=[rows[0]]+hist
  now=max(r['finished']['monotonic_after_ns'],r.get('status',{}).get('monotonic_ns',t))
  cov=_window_coverage(hist,now,(fast,slow))['sample_fraction']
  slope=slow_slope(hist,t,slow)
  s=r.get('status',{});pm=s.get('pm_observed_ns')
  status=(s.get('os_level')==0 and s.get('pm_state')=='Nominal' and type(pm)is int and 0<=now-pm<=2*NS)
  out.append(dict(row=r,t=t,now=now,cov=cov,slope=slope,status=status))
 return out
def replay(ev,entry,refs,bands,cap,full_status=True,horizon=None):
 n=0;prev=None;latch=False;last=None
 for z in ev:
  if z['t']<entry:continue
  if z['now']>entry+cap*NS:break
  r=z['row'];t=z['t'];last=z
  if z['cov'] is None or z['cov']<.9:latch=True
  good=(not latch and (prev is None or 0<t-prev<=2*NS) and z['slope'] is not None and abs(z['slope'])<=.2)
  for k,ref in refs.items():
   v=r['sensors'].get(k)
   good=good and isinstance(v,(int,float)) and math.isfinite(v) and k not in r.get('errors',{}) and v<=ref+bands[k]
  if full_status:good=good and z['status']
  n=n+1 if good else 0;prev=t
  if n>=10:
   return dict(outcome='release',t_s=(t-entry)/NS,temps={k:r['sensors'][k] for k in refs},slope=z['slope'],above_idle=None)
 observed=(ev[-1]['t']-entry)/NS if ev else 0
 return dict(outcome=('unobserved' if latch and observed>=300 else 'censored') if horizon is None else ('timeout' if horizon-entry>=cap*NS else 'censored'),observed_s=max(0,observed),last_t_s=(last['t']-entry)/NS if last else None,latched=latch)
R=B/'r1-20261111T014106Z/night/align-r1/step_30b'
raw=load(R/'runs/align-v4-r1-step-30b/outputs/align_thermal.jsonl');r1=sample_rows(raw)
gate=next(r['values']['gate'] for r in raw if r.get('values',{}).get('gate',{}).get('kind')=='G0')
events=load(R/'runs/align-v4-r1-step-30b/events.jsonl')
warm=next(r['timestamp_s'] for r in events if r.get('phase')=='warmup' and r.get('event_type')=='stage_started')
idle_times=[json.loads(l)['timestamp_s'] for l in (R/'runs/align-v4-r1-step-30b/rich_telemetry_idle.jsonl').open()]
# Epoch conversion uses the nearest sidecar's paired epoch and monotonic stamps.
anchor=min(r1,key=lambda r:abs(r['epoch_ns']/NS-warm))
to_mono=lambda epoch:anchor['monotonic_ns']+round(epoch*NS-anchor['epoch_ns'])
warm_ns=to_mono(warm);idle_end=to_mono(idle_times[-1]);idle_start=to_mono(idle_times[0])
soak=json.loads((B/'r1-20261111T014106Z/night/align-r1/soak_reference.json').read_text())
keys=('TV0h','Tf08');refs={k:soak['sensors_c'][k] for k in keys}
own={k:stats(window(r1,warm_ns),k)['median'] for k in keys}
idle={k:stats(window(r1,idle_end),k) for k in keys}
print('R1_IDLE',json.dumps(dict(capture_span_epoch=[idle_times[0],idle_times[-1]],capture_stats={k:stats([r for r in r1 if idle_start<=r['monotonic_ns']<=idle_end],k) for k in keys},last60_capture=idle,last60_prewarm={k:stats(window(r1,warm_ns),k) for k in keys}),sort_keys=True))
r1_live=[r for r in r1 if r['monotonic_ns']<=gate['end_ns']]
ev=evaluations(r1_live,*keys)
print('R1_RECORDED',json.dumps(gate,sort_keys=True))
candidates={
 'A_soak_600':(refs,{k:1. for k in keys},600),
 'B_own_600':(own,{k:1. for k in keys},600),
 'C_spread_600':(refs,{k:max(1.,3*idle[k]['resid_sd']) for k in keys},600),
 'D_shift_slow_600':(refs,{'TV0h':1.,'Tf08':own['Tf08']-refs['Tf08']+1},600),
 'E_soak_1200':(refs,{k:1. for k in keys},1200),
 'F_own_1200':(own,{k:1. for k in keys},1200),
 'I_prewarm_sd_600':(own,{k:max(1.,3*stats(window(r1,warm_ns),k)['resid_sd']) for k in keys},600)}
r1_results={}
for label,(ref,band,cap) in candidates.items():
 res=replay(ev,gate['start_ns'],ref,band,cap,horizon=gate['end_ns'])
 if res['outcome']=='release':res['above_idle']={k:res['temps'][k]-own[k] for k in keys}
 r1_results[label]=res
 print('R1_REPLAY',label,json.dumps(dict(ref=ref,band=band,result=res),sort_keys=True))

def temp_evaluations(rows,fast,slow):
 times=[r['monotonic_ns'] for r in rows];out=[]
 for i,r in enumerate(rows):
  t=times[i];j=bisect.bisect_left(times,t-60*NS);hist=rows[j:i]
  good=[p for p in hist if 0<=p['finished']['monotonic_after_ns']-p['monotonic_ns']<=NS and slow in p['sensors'] and slow not in p.get('errors',{})]
  slope=None
  if len(good)>=54:
   x=[(p['monotonic_ns']-t)/NS for p in good];y=[p['sensors'][slow] for p in good];xm=st.mean(x);ym=st.mean(y);den=sum((a-xm)**2 for a in x)
   if den:slope=60*sum((a-xm)*(b-ym) for a,b in zip(x,y))/den
  out.append(dict(row=r,t=t,now=t,cov=1. if len(good)>=54 else None,slope=slope,status=True))
 return out
def physical_replay(rows,en,refs,cap=600):
 fk='TV0h';sk=next((k for k in refs if k!=fk),fk)
 ee=temp_evaluations(rows,fk,sk)
 # Coverage is a point predicate in this diagnostic only; do not latch missing
 # prehistory at an idle challenge's entry.
 rr=replay(ee,en,refs,{k:1. for k in refs},cap,False)
 if rr['outcome']=='release':
  at=min(rows,key=lambda r:abs(r['monotonic_ns']-en-rr['t_s']*NS))
  rr['Tf08_at_release']=at['sensors'].get('Tf08')
 return rr
datasets=[]
for root in sorted(B.glob('r0-v4-*')):
 p=root/'smc/samples.jsonl'
 if not p.exists():print('R0_NO_JOURNAL',root.name,flush=True);continue
 raw0=load(p);rows=[]
 for r in raw0:
  rr=sample_rows([r])
  if rr:rr[0]['phase']=r.get('phase');rows.extend(rr)
 idles=[r for r in rows if r.get('phase')=='idle'];rec=[r for r in rows if r.get('phase')=='recovery']
 boundary=next((r['monotonic_ns'] for r in rows if r.get('phase')=='load'),idles[-1]['monotonic_ns']+NS)
 datasets.append((root.name,rows,boundary,idles,rec))
 print('R0_PHASES',root.name,json.dumps(dict(collections.Counter(r['phase'] for r in rows))),flush=True)
 print('R0_BASELINE',root.name,json.dumps({k:stats(window(idles,boundary),k) for k in keys},sort_keys=True),flush=True)
 if rec:
  own0={k:stats(window(idles,boundary),k)['median'] for k in keys}
  all0={k:stats(idles,k)['median'] for k in keys}
  for name,ref in [('A_idleall',all0),('B_own',own0),('C_spread',all0),('D_shift_slow',{'TV0h':all0['TV0h'],'Tf08':own0['Tf08']}),('E_idleall_1200',all0),('F_own_1200',own0),('I_prewarm_sd',own0)]:
   rr=physical_replay(rows,rec[0]['monotonic_ns'],ref,1200 if '1200' in name else 600)
   if rr['outcome']=='release':rr['above_idle']={k:rr['temps'][k]-own0[k] for k in keys}
   print('R0_PHYSICAL',root.name,name,json.dumps(rr,sort_keys=True),flush=True)
 # Inspect every idle stream too, with the reference from its FIRST valid 60 s.
 # This tests hot-reference laundering without pretending it is post-warmup.
 if idles[-1]['monotonic_ns']-idles[0]['monotonic_ns']>=60*NS:
  en=idles[0]['monotonic_ns']+60*NS
  first={k:stats(window(idles,en),k)['median'] for k in keys}
  rr=physical_replay(idles,en,first)
  if rr['outcome']=='release':
   rr['above_last60_idle']={k:rr['temps'][k]-stats(window(idles,boundary),k)['median'] for k in keys}
  print('R0_IDLE_CHALLENGE',root.name,json.dumps(rr,sort_keys=True),flush=True)
inv=norm_inv(load(R/'inventory/inventory_journal.jsonl'))
inv=[r for r in inv if r['monotonic_ns']<=gate['end_ns']]
accepted=json.loads((B/'r0-v4-20261108T0550Z/smc/r0.json').read_text())['response']
slowkeys=sorted(set(accepted['heatsink_candidates']+['TVFh','TV0h']))
datasets.append(('R1_INVENTORY',inv,warm_ns,window(inv,warm_ns,300),[r for r in inv if r['monotonic_ns']>=gate['start_ns']]))
for root,rows,boundary,idles,rec in datasets:
 if not rec:continue
 en=gate['start_ns'] if root=='R1_INVENTORY' else rec[0]['monotonic_ns']
 results=[]
 for sk in slowkeys:
  fk='TV0h';bas=window(idles,boundary);fs=stats(bas,fk);ss=stats(bas,sk)
  if not fs or not ss:continue
  ref={fk:fs['median'],sk:ss['median']}
  rr=physical_replay(rows,en,ref)
  if rr['outcome']=='release':
   rr['above_idle']={k:rr['temps'][k]-ref[k] for k in ref}
   rr['Tf08_above_own']=rr['Tf08_at_release']-stats(bas,'Tf08')['median']
   rr['Tf08_own_ref']=stats(bas,'Tf08')['median']
  results.append([sk,rr])
 print('PHYSICAL_SWAP',root,json.dumps(results,sort_keys=True),flush=True)
for root in sorted(B.glob('pilot-v[789]-*')):
 p=root/'custody/hazards/monitor/thermal.jsonl';a=load(p)
 counts=collections.Counter(r.get('values',{}).get('level') for r in a if r.get('kind')=='reading')
 print('PILOT',root.name,'readings',sum(counts.values()),'levels',dict(counts),'temperature_samples',len(sample_rows(a)),flush=True)



from types import SimpleNamespace
from joulewise.align.apple.thermal_gates import ThermalSession
from joulewise.clock import ClockStamp
class ReplayClock:
 def __init__(self,start):self.n=start
 def stamp(self):return ClockStamp(epoch_s=self.n/NS,monotonic_before_s=self.n/NS,monotonic_after_s=self.n/NS,wall_resolution_s=1e-6,monotonic_resolution_s=1e-9)
 def sleep(self,seconds):self.n+=round(seconds*NS)
class ReplaySession(ThermalSession):
 @property
 def rows(self):
  return [r for r in self.replay_rows if max(r['finished']['monotonic_after_ns'],r.get('status',{}).get('monotonic_ns',r['monotonic_ns']))<=self.clock.n]
 def _collector_fault(self):return None
 def persist_interval(self,row):pass
def native_wait(ref,band,cap,rows,entry):
 session=object.__new__(ReplaySession)
 session.clock=ReplayClock(entry);session.replay_rows=rows
 session.reference={'fast_c':ref['TV0h'],'slow_c':ref['Tf08']}
 session.episode_reference=None
 session.policy={'sensors':{'s_fast':'TV0h','s_slow':'Tf08'},'delta_fast_c':band['TV0h'],'delta_slow_c':band['Tf08'],'g0_cap_s':cap}
 session.flags=[];session.intervals=[];session.events=[]
 session.sidecar=SimpleNamespace(event=lambda *args:None,_thread=True,_seq=0)
 return session.wait('G0')
for label,(ref,band,cap) in candidates.items():
 if cap>600:continue
 v=native_wait(ref,band,cap,r1_live,gate['start_ns'])
 print('NATIVE_WAIT',label,json.dumps({k:v[k] for k in ('outcome','duration_s','release','exit_sample_ns')},sort_keys=True),flush=True)
 assert v['outcome']==('released' if r1_results[label]['outcome']=='release' else r1_results[label]['outcome']),label
 

print('NATIVE_WAIT_OK',flush=True)

def tail_effect(rows,entry,release_s,base):
 start=entry+round(release_s*NS)
 a=[((r['monotonic_ns']-entry)/NS,r['sensors']['Tf08']) for r in rows if start<=r['monotonic_ns']<=gate['end_ns']]
 area=sum((v1+v2-2*base)/2*(t2-t1) for (t1,v1),(t2,v2) in zip(a,a[1:]))
 if a:
  print('EFFECT',json.dumps(dict(release_s=release_s,supported_span_s=a[-1][0]-a[0][0],slow_at_start=a[0][1],slow_at_end=a[-1][1],drop_c=a[0][1]-a[-1][1],above_idle_c=a[0][1]-base,degree_seconds=area,max_heat_capacity_J_per_K_for_1J=1/(a[0][1]-base),max_kappa_W_per_K_for_1J=1/area if area else None),sort_keys=True))
tail_effect(r1_live,gate['start_ns'],r1_results['I_prewarm_sd_600']['t_s'],own['Tf08'])
inv_effect=norm_inv(load(R/'inventory/inventory_journal.jsonl'))
tail_effect(inv_effect,gate['start_ns'],193.416682041,26.556562423706055)
# Minimum slow allowance that can release in the recorded G0; no proposed bar.
runs=[];best=None
for z in ev:
 if z['t']<gate['start_ns']:continue
 r=z['row'];good=(z['cov'] is not None and z['cov']>=.9 and z['status'] and z['slope'] is not None and abs(z['slope'])<=.2 and r['sensors']['TV0h']<=refs['TV0h']+1)
 runs=(runs+[z])[-10:] if good else []
 if len(runs)==10:
  need=max(zz['row']['sensors']['Tf08'] for zz in runs)-refs['Tf08']
  if best is None or need<best[0]:best=(need,(z['t']-gate['start_ns'])/NS)
print('MIN_SLOW_BAND',json.dumps(dict(soak_delta=best[0],own_delta=best[0]+refs['Tf08']-own['Tf08'],release_sample_s=best[1])))
def fit_tail(start):
 v=[((r['monotonic_ns']-gate['start_ns'])/NS,r['sensors']['Tf08']) for r in r1_live if r['monotonic_ns']>=gate['start_ns']+start*NS]
 t0=v[0][0];tt=[t-t0 for t,y in v];yy=[y for t,y in v]
 def f(logtau):
  tau=math.exp(logtau);x=[math.exp(-t/tau) for t in tt];xm=st.mean(x);ym=st.mean(yy);den=sum((a-xm)**2 for a in x)
  if not den:return float('inf'),0,0,tau
  b=sum((a-xm)*(y-ym) for a,y in zip(x,yy))/den;c=ym-b*xm
  return sum((y-c-b*a)**2 for a,y in zip(x,yy)),c,b,tau
 grid=[math.log(.1)+i*(math.log(1e6)-math.log(.1))/200 for i in range(201)]
 j=min(range(1,200),key=lambda j:f(grid[j])[0]);lo,hi=grid[j-1],grid[j+1]
 for _ in range(80):
  aa=lo+(hi-lo)/3;bb=hi-(hi-lo)/3
  if f(aa)[0]<f(bb)[0]:hi=bb
  else:lo=aa
 err,c,b,tau=f((lo+hi)/2)
 crosses={k:(None if c>=ref else t0+tau*math.log(b/(ref-c))) for k,ref in [('soak',refs['Tf08']+1),('own',own['Tf08']+1)]}
 print('TAIL_FIT',json.dumps(dict(start_s=start,n=len(v),asymptote_c=c,tau_s=tau,rmse_c=math.sqrt(err/len(v)),crossing_s=crosses),sort_keys=True))
for t in (240,300,360):fit_tail(t)

# Strict status admission of each available R0 temperature journal.
from joulewise.align.apple.thermal_gates import ThermalFault
for root,rows,boundary,idles,rec in datasets:
 if root=='R1_INVENTORY':continue
 entry=rec[0]['monotonic_ns'] if rec else idles[-1]['monotonic_ns']
 ref={k:stats(idles,k)['median'] for k in keys}
 try:
  native_wait(ref,{k:1. for k in keys},600,rows,entry)
  raise AssertionError('R0 unexpectedly had a G0 status source')
 except ThermalFault as error:
  assert error.code=='thermal.status_source_missing'
  print('R0_STRICT',root,error.code,flush=True)
soakpath=B/'r1-20261111T014106Z/night/align-r1/idle_soak/sensors/align_thermal.jsonl'
soakrows=sample_rows(load(soakpath))
se=soakrows[0]['monotonic_ns']+60*NS
sref={k:stats(window(soakrows,se),k)['median'] for k in keys}
try:
 sr=native_wait(sref,{k:1. for k in keys},600,soakrows,se)
 print('SOAK_STRICT',json.dumps({k:sr[k] for k in ('outcome','duration_s')},sort_keys=True),flush=True)
except ThermalFault as error:
 print('SOAK_STRICT',error.code,flush=True)
sp=physical_replay(soakrows,se,sref)
print('SOAK_PHYSICAL',json.dumps(sp,sort_keys=True),flush=True)
# Unchanged source provenance, not Git state.
paths=[M/'joulewise/align/apple/thermal_gates.py',M/'joulewise/align/apple/r1_runtime.py',
 R/'runs/align-v4-r1-step-30b/outputs/align_thermal.jsonl',
 R/'inventory/inventory_journal.jsonl',soakpath]
paths += sorted(B.glob('r0-v4-*/smc/samples.jsonl'))
paths += sorted(B.glob('pilot-v[789]-*/custody/hazards/monitor/thermal.jsonl'))
for p in paths:
 h=hashlib.sha256()
 with p.open('rb') as fh:
  for block in iter(lambda:fh.read(1024*1024),b''):h.update(block)
 print('SHA256',str(p),h.hexdigest(),flush=True)
assert r1_results['A_soak_600']['outcome']=='timeout'
assert r1_results['B_own_600']['outcome']=='timeout'
assert r1_results['F_own_1200']['outcome']=='censored'
print('REPLAY_DONE',flush=True)

# REPLAY_SOURCE_END
```

