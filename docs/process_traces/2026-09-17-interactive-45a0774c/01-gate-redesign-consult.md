**Amend all three asks.** Bounded waiting is justified; replacing load average is justified; a scientifically defensible replacement threshold is not yet established. I would approve the mechanism design now and withhold activation of the new CPU admission rule pending the cold gate’s evidence review.

1. **Verdicts**

**(a) Amend.** Poll within a declared budget, but keep the acquisition end fixed. Start the chain after GO without moving the window, courier boundary, or dead-man. Require sustained quiet rather than one lucky passing snapshot. Waiting must happen before reservation or `chain.started`.

**(b) Amend substantially.** Drop load average as an admission condition; retain it as diagnostic evidence. The September 17 observations demonstrate its poor discrimination: high load at refusal, followed by sustained daemon activity at loads that would pass. They do not establish a safe CPU threshold. [Harvest record:19–25](/Users/edr/code/JouleWise/docs/process_traces/2026-09-17-activation-8789ee70/01-n1-20260917-harvest-record.md:19)

Reject daemon name exemptions and daemon-presence bans. Every listed daemon—`fseventsd`, Spotlight workers, media analysis, deletion, cloud sync, updates, backups—counts toward aggregate activity. Sleeping daemons are permissible; active daemons receive no exemption because macOS owns them.

Do not substitute `ps %CPU` directly: Apple documents it as a decaying average. Use interval CPU-time differences; Apple’s `top` documentation likewise requires discarding its first, invalid CPU sample. [Apple ps source](https://raw.githubusercontent.com/apple-oss-distributions/adv_cmds/main/ps/ps.1), [Apple top source](https://raw.githubusercontent.com/apple-oss-distributions/top/main/top.1)

**(c) Amend.** Adopt Ed-side attribution and targeted Spotlight exclusions as preparation, without claiming exclusions cure `fseventsd`. Apple supports folder exclusions; their documented purpose does not establish the cause of this churn. Count actual directory entries under root access; do not infer the count from saturated link metadata. Preserve diagnostic output; do not delete `.fseventsd`. [Apple guidance](https://support.apple.com/en-ie/guide/mac-help/mchl1bb43b84/mac), [record:25](/Users/edr/code/JouleWise/docs/process_traces/2026-09-17-activation-8789ee70/01-n1-20260917-harvest-record.md:25)

**Opinion:** favor fully resident, nonsynced primary custody with a separately maintained backup. Do not make migration a prerequisite to this gate repair: 3.575 seconds is encouraging, but one successful access probe is not an availability guarantee. Migration must preserve bytes, hashes, original evidence and authenticated locator history; a path substitution alone is insufficient. The existing override is replay-specific and cannot authorize issuance using replacement bytes. [Probe:19](/Users/edr/code/JouleWise/docs/process_traces/2026-09-16-activation-9853dd2b/77-arm-evidence-n1-20260917/night_probe_receipt.json:19), [joulewise/calibration_ledger.py:5354](/Users/edr/code/JouleWise/joulewise/calibration_ledger.py:5354)

2. **Smallest sound combined design**

Use an explicit **new packless plan v4**, leaving v2 behavior intact and transaction-pack v3 unchanged. V3 is already occupied; current validation requires exact keys. [joulewise/night_gate.py:22](/Users/edr/code/JouleWise/joulewise/night_gate.py:22), [joulewise/night_gate.py:213](/Users/edr/code/JouleWise/joulewise/night_gate.py:213)

Add:

```json
"quiet_admission": {
  "policy_id": "cpu_interval_v1",
  "bind_max_s": 600,
  "post_bind_budget_s": 9000
}
```

The policy ID binds approved sampling and threshold semantics. No environment override. Old plans without this field must still validate **and retain their original admission semantics**, not receive polling through a default.

Proposed constants and allocations:

| Item | Proposal | Rationale |
|---|---:|---|
| Bind allocation | 600 s | Operational opportunity to outlast bursts; not a physical settling constant or inter-window cadence rule. |
| Sampling interval | 30 s | Resolves the reported burst scale while limiting observer activity. |
| Consecutive quiet intervals | 2 | Requires 60 seconds of observed quiet; reset after any busy interval. |
| Census interval | ≤30 s, plus final check | Preserves existing cadence through waiting. |
| CPU candidate | **0.01 busy-core equivalent aggregate** | **PROVISIONAL**, discussed below. |
| Attribution summary | Top 10 processes | Presentation limit only; admission uses all activity. |
| New derivation window | 9600 s | Adds 600 seconds before the existing 9000-second allocation. |

The **0.01-core candidate is not an established safe threshold**. Assuming 5 W/core, it corresponds to 3 J over 60 seconds. That arithmetic explains the candidate; it does not validate the power model, allocate a new 3 J error budget, or justify treating the approximately 5 J claim-clearance bar as spare contamination allowance. Ordinary kernel activity and the observer may also make it impractical.

Measure both aggregate process CPU and host busy time, normalized to cores:

`busy_core_equivalents = logical_cpu_count × (1 − idle_fraction)`.

Apply the same aggregate ceiling; an independent “95% idle” rule would conceal substantial activity on a many-core machine. Preserve kernel/unattributed activity and observer cost. PID identity must include process start identity; exited processes must not disappear from aggregate accounting.

**Science blocker:** establish the candidate’s discrimination against accepted clean evidence and known contamination, including observer overhead and GPU/I/O activity. Prefer existing evidence; if insufficient, use a bounded Ed-controlled validation. Do not install an invented percentage merely because it catches today’s daemon.

Only excess CPU activity becomes **WAIT**. Census hits, AC failure, screensaver-configuration failure, thermal restriction, boot/clock failure, malformed required observations, registration and digest failures remain terminal. Recheck dynamic hard conditions throughout binding and immediately before GO. Load-probe failure is diagnostic once load ceases to authorize admission.

Two corrections to the brief matter: the “HID” probe reads screensaver configuration, not live inactivity; thermal output without a speed-limit line currently passes. Preserve those semantics unless separately ruled. [joulewise/night_gate.py:1140](/Users/edr/code/JouleWise/joulewise/night_gate.py:1140), [joulewise/night_gate.py:1235](/Users/edr/code/JouleWise/joulewise/night_gate.py:1235)

**Timing.** Let `E=t0+window_max_s`, `B=bind_max_s`, `R=post_bind_budget_s`. Validate `window_max_s ≥ B+R`. Binding ends at `min(t0+B,E−R)`; all qualifying observations and final checks must finish by that instant. Late driver startup consumes B—it never restarts the allowance.

For a new 9600-second plan and GO at `t0+600`, 9000 seconds remain. Reservation then precedes the unchanged 600-second settle. The existing derivation schedule is 7680 seconds with a 300-second minimum pre-settle allowance. [scripts/gen_derivation_night.py:86](/Users/edr/code/JouleWise/scripts/gen_derivation_night.py:86), [scripts/gen_derivation_night.py:124](/Users/edr/code/JouleWise/scripts/gen_derivation_night.py:124), [scripts/gen_derivation_night.py:511](/Users/edr/code/JouleWise/scripts/gen_derivation_night.py:511)

Keep:

- Acquisition end: `E`.
- Nominal completion: `E+300`.
- Forced shutdown trigger: `E+300`, with bounded termination afterward.
- Dead-man: `60×ceil((E+300+3600)/60)`.

These are current derivations, independent of GO. Importantly, **forced termination does not begin at E**. [scripts/run_night.py:841](/Users/edr/code/JouleWise/scripts/run_night.py:841), [scripts/run_night.py:1399](/Users/edr/code/JouleWise/scripts/run_night.py:1399), [scripts/run_night.py:1506](/Users/edr/code/JouleWise/scripts/run_night.py:1506)

Convert absolute deadlines to monotonic deadlines once; never extend them after a clock change. Census and deadline supervision must remain responsive while probes run.

**Change sites:**

- [joulewise/night_gate.py:197](/Users/edr/code/JouleWise/joulewise/night_gate.py:197): `NightPlan.from_mapping`; explicit schema/policy dispatch.
- [joulewise/night_gate.py:947](/Users/edr/code/JouleWise/joulewise/night_gate.py:947): split `evaluate_night` into static checks, dynamic hard checks and interval admission; retain the legacy branch.
- [joulewise/night_gate.py:180](/Users/edr/code/JouleWise/joulewise/night_gate.py:180): extend injected observations for interval samples and fake-clock testing.
- [joulewise/night_plan_writer.py:18](/Users/edr/code/JouleWise/joulewise/night_plan_writer.py:18): version-aware `night_plan_mapping`, without migrating old plans.
- [scripts/run_night.py:316](/Users/edr/code/JouleWise/scripts/run_night.py:316), [scripts/run_night.py:1961](/Users/edr/code/JouleWise/scripts/run_night.py:1961): bounded sampler supervision and bind orchestration. The existing 30-second subprocess timeout cannot simply wrap a 60-second sampler.
- [scripts/gen_derivation_night.py:462](/Users/edr/code/JouleWise/scripts/gen_derivation_night.py:462): `build_spec` validates reserved post-bind runway.
- [scripts/run_night.py:945](/Users/edr/code/JouleWise/scripts/run_night.py:945): `_artifact_list` includes the complete sample journal.
- [joulewise/night_gate.py:1373](/Users/edr/code/JouleWise/joulewise/night_gate.py:1373): versioned receipt validation.

Use **receipt v3** for new admission semantics, with legacy v2 validation retained. Record an append-only `quiet_samples.jsonl`: every interval, timestamps, duration, boot identity, raw observations, CPU totals, top consumers, hard predicates, and WAIT/pass/error decision. The final receipt binds its digest/count, policy, threshold values, bind deadline, qualifying samples and GO time. Do not emit a terminal refusal for intermediate WAITs.

Every GO and refusal should carry attribution or an explicit unavailable/error reason. An immediate census refusal must not wait a minute merely to manufacture attribution.

**Retry reconciliation.** Implement A212 alongside this work. Current classification still assigns the four machine-state refusals to the cold-gate path; the watchdog still holds through nominal completion even after early refusal. [joulewise/arm_retry.py:29](/Users/edr/code/JouleWise/joulewise/arm_retry.py:29), [scripts/magistrate_watchdog.py:775](/Users/edr/code/JouleWise/scripts/magistrate_watchdog.py:775)

Change `classify_abort` through a separately evidenced zero-capture successor route, `retry_allowed`, and `render_policy`; do not globally whitelist refusal strings. The existing retry history requires the same plan digest, so a new-plan successor cannot masquerade as another same-candidate attempt. [joulewise/arm_retry.py:88](/Users/edr/code/JouleWise/joulewise/arm_retry.py:88), [joulewise/arm_retry.py:164](/Users/edr/code/JouleWise/joulewise/arm_retry.py:164), [joulewise/arm_retry.py:195](/Users/edr/code/JouleWise/joulewise/arm_retry.py:195)

R1 should say: binding observations are not retries; terminal zero-capture machine-state refusal permits a **new plan**, fresh notice, ≥60-second spacing, fresh install cutoff and every observed NO preserved. Require positive terminal evidence, no start claim/reservation/capture, and completed delivery handoff. A refusal receipt’s existence does not prove capture occurred—or that the driver has finished.

Update both generated policy copies and stale surrounding timing prose. The handbook still says 85 minutes at [NIGHT_HANDBACK.md:59](/Users/edr/code/JouleWise/docs/process/NIGHT_HANDBACK.md:59), whereas current code derives ten minutes from eight plus two. [scripts/magistrate_watchdog.py:86](/Users/edr/code/JouleWise/scripts/magistrate_watchdog.py:86), [scripts/run_night.py:1410](/Users/edr/code/JouleWise/scripts/run_night.py:1410)

3. **Regression tests and mutants**

These are proposed tests, not executed verification:

| Test | Mutants it must kill |
|---|---|
| `test_bind_go_on_second_consecutive_pass_at_k` | First-pass GO; nonconsecutive passes; continued polling after GO. |
| `test_bind_expiry_preserves_every_sample` | Last-sample-only receipt; deadline reset; intermediate `refusal.json`; late GO. |
| `test_low_load_busy_daemon_never_admits` | Load controls admission; daemon exemption; CPU normalized by machine capacity incorrectly. |
| `test_finished_burst_admits_despite_high_load` | Retained load veto; stale `%CPU`; stale failed sample. |
| `test_census_hit_during_bind_is_terminal_agent_present` | Cached initial census reused; wait until agent disappears; watchdog relaunch during binding. |
| `test_cpu_aggregate_identity_and_observer_accounting` | Many small workers evade per-process cap; PID reuse; exited-worker loss; observer silently excluded. |
| `test_v2_bytes_and_semantics_remain_legacy` | Implicit field insertion, schema rewrite, old plans silently use new thresholds; transaction v3 regression. |
| `test_late_go_preserves_absolute_deadlines` | GO shifts E/dead-man; late invocation gets fresh B; clock rollback extends waiting; insufficient runway accepted. |
| `test_zero_capture_successor_waits_for_delivery` | Bare refusal releases fence; started/reserved night retries; old digest reused; NO forgotten. |
| `test_probe_hang_cannot_block_census_or_expiry` | Sequential blocking sampler defeats supervisor; malformed evidence becomes quiet. |

Place these in the existing night-gate, driver, plan-writer, generator, retry and watchdog test modules; add installer compatibility coverage. Run focused checks and the canonical suite after implementation.

4. **Atomic cold-gate propositions**

Each requires its own AFFIRM/REJECT/REFUSE:

1. Pre-reservation admission may wait within a sealed bind allocation.
2. Admission requires two consecutive 30-second quiet intervals.
3. Load average may cease to veto admission.
4. The proposed aggregate CPU cutoff is scientifically adequate for the intended measurement class.
5. The sampler’s observer effect is acceptable.
6. The enumerated non-CPU predicates remain terminal during binding.
7. The proposed 9600-second allocation preserves the registered acquisition schedule.
8. Explicit v4 activation preserves sealed v2/v3 semantics.
9. Zero-capture bind-expiry refusal falls within the authorized successor-retry remedy.

For proposition 4, my present recommendation is **REFUSE pending evidence**, not approval by plausible wattage arithmetic. The charter places the burden on the proponent and requires atomic verdicts. [coldgate_charter.md:108](/Users/edr/code/JouleWise/docs/process/coldgate_charter.md:108), [coldgate_charter.md:116](/Users/edr/code/JouleWise/docs/process/coldgate_charter.md:116)

The magistrate may choose factoring, journal representation, diagnostic presentation and implementation sequencing within those rulings. It may not independently change thresholds, reinterpret preregistration or introduce new recovery policy.

5. **Missed blockers**

- **GO is not whole-window cleanliness.** Reservation reads occur after admission; then a 600-second settle precedes capture. Daemons can restart afterward. Admission evidence must not become a retrospective clean-window certificate or an unregistered exclusion rule. [scripts/night_chains/calibration_derivation_only.zsh:187](/Users/edr/code/JouleWise/scripts/night_chains/calibration_derivation_only.zsh:187), [scripts/night_chains/calibration_derivation_only.zsh:215](/Users/edr/code/JouleWise/scripts/night_chains/calibration_derivation_only.zsh:215)
- **Courier completion is not guaranteed at E+300.** That instant also triggers forced shutdown; reporting then precedes courier launch. Faster recovery must preserve delivery ownership and avoid overlapping magistrate/courier activity. [scripts/run_night.py:1549](/Users/edr/code/JouleWise/scripts/run_night.py:1549)
- **Revision 3 licenses a digest refill, not new science semantics.** Append a prospective ruling for admission changes; preserve prior text and rejected-night evidence. [Pre-registration:520](/Users/edr/code/JouleWise/configs/calibration/preregistration_d079_epoch_25g83_rev1.md:520)

No files changed, tests run, or live measurements attempted. The next step is a cold-gate packet containing the explicit v4 design and evidence needed to judge the CPU predicate.