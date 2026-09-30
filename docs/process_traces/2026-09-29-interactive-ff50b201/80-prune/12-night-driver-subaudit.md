# Night-driver mechanisms sub-audit (read-only, main 32ff9013)

A sub-audit spawned by the Opus 5.5 code-side prune investigator (file 11), delivered separately on 2026-09-30. Filed by the orchestrator; wording condensed, facts and verdicts unchanged.

**What production ran.** Every armed production night used plan v2 `DIAGNOSTIC_NO_PACK` (derivation nights 09-13/15/16/17/19, W1, W2; QPE01 pilots 09-20/22/23). No v3 (TRANSACTION_PACK) or v4 (quiet-admission) plan exists anywhere; `released_zero_capture_refusals` is empty; no `successor-claims/`. On W1/W2 (the source of S/C) the machinery only attested (gate GO, 248 censuses on W1, no hits, no refusals).

| # | Mechanism | Where (approx.) | Protects | Real catches / costs | Verdict (est. removable prod lines) |
|---|---|---|---|---|---|
| M1 | t0 machine-quiet gate (agents, HID/screensaver, AC + battery float, load ≤ 2.0, thermal, non-observer busy share, corecaptured loop) | `night_gate.py` 686–716, 812–880, 1468–1702; `corecaptured_loop.py` | every capture's idle baseline and cadence | 09-13 agents present; 09-15/09-17 load > 2.0; one miss (09-22 fseventsd) led to the non-observer predicate | **KEEP** |
| M2 | driver custody basics (chain sha256 vs sidecar, once-only `chain.started`, write-once records, plan staleness, boot/clock) | `run_night.py` ~3140–3175, 559–606, 1780–1810; `night_gate.py` 1703–1752 | that the pinned chain ran once into one custody root | no production firing; write-once crashed the driver 09-16 (a mechanism defect) | **KEEP** (cheap, provenance) |
| M3 | in-window supervision (30 s agent census, wall-clock deadline, group termination + absence census) | `run_night.py` 463–558, 694–1009, 3461–3617 | an agent entering mid-capture; hangs; orphan samplers | 09-16 real but moot; 09-20 false positive (self-match) lost a night | **KEEP** census + deadline; **THIN** group-census batching (~120) |
| M4 | TRANSACTION_PACK (plan v3) path | `run_night.py` 1968–2267; `night_gate.py` 899–1200; `receipt_oracle.py` | only the future `_v5` campaign | never ran | **DELETE/park** (~800) |
| M5 | v4 quiet admission / `bind_until_quiet` | `run_night.py` 2268–2976; `night_gate.py` 1814–1849, 1930–2011; `gen_derivation_night.py` 901–952; `quiet_admission.py` | nothing yet | never ran; heavy cost (fix rounds 1–4, refuters, cold gates 70, 71) | **DELETE** (~870 + 343); "refuse and re-arm" suffices |
| M6 | zero-capture refusal release / successor retry (A212/A234) | `zero_capture_facts.py`; `evidence_night.py` 868–1039; `magistrate_watchdog.py` 800–905, 1531–1554 | scheduling convenience | never exercised; two same-signature BLOCKER rounds | **DELETE** (~450) |
| M7 | arm pipeline `evidence_night.py` | 1,947 lines | hygiene; arm-time census duplicates M1 | first live uses refused on the mechanism's own defects (3 cold gates) | **THIN** (~700) |
| M8 | LaunchAgent installer + launchd probe | `night_agent_install.py`; `install_night_agent.sh`; `run_night.py` 3618–3939, 1669–1780 | **probe load-bearing**: ProcessType=Interactive gives ≈126–132 ms cadence vs ≈175–248 ms default (OSCTX) | install windows: 3 cold gates, 6 rounds, then collapsed to all-day | **THIN** spans (~90) + Transaction/Shield (~400); **keep the probe** |
| M9 | dead-man + `claude -p` Gmail courier | `run_night.py` 1161–1630, 1811–1870, 3353–3460 | reporting only | 29 courier commits (11 fix rounds); one Claude session per night | **THIN** (~400) |
| M10 | registration pin C1 | `night_gate.py` 43–136, 1753–1812 | QPE01 chain binding; ceremony for derivation nights | — | **THIN** (~60) |
| M11 | magistrate watchdog | `scripts/magistrate_watchdog.py` 2,615 | only the plan-span hold matters for measurement | — | **THIN** (keep ≈150; ≈1,500 is orchestration, owner's call) |
| M12 | plan generation and pinning | `gen_derivation_night.py`, `gen_evidence_night.py`, `night_plan_writer.py`, `night_kinds.py`, `night_chains/` | W1/W2 provenance | — | **KEEP** |
| M13 | off-path modules | `salvage_dangler.py` 1,449 (Window B, retired); `window_duration_margins.py` 1,268 + script (no receipt ever written); `coldgate_receipt.py` 211 (no importer, unreviewed); `sampler_teardown.py` 561; `measurement_liveness.py` 276 | — | — | DELETE/park the first three; **KEEP** the last two |

**Totals (estimates):** ≈6,900 removable production lines outside the watchdog (+≈1,500 by owner decision); tests shrink by ≈8–10k lines.

**Load-bearing:** M1 t0 quiet predicates; M2 chain digest, once-only start, write-once records; M3 in-window census and deadline; M8 ProcessType=Interactive and the cadence probe; M12 plan and wrapper pinning.

**Pattern:** the largest costs went into mechanisms that never ran in production (M4, M5, M6) or mainly caught their own defects (retained roots, install windows, census self-match, write-once vs dead-man) — the network-time shape.
