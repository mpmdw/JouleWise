**Seat: Fable 5.1** (blind council seat, D-184 instrument acceptance, 25G83)

**Disclosure.** Auto-loaded before any action: `~/.claude/CLAUDE.md`, the worktree `CLAUDE.md`, the memory index `MEMORY.md` (truncated), and harness reminders. None used as authority; no `RUN_STATE.md`, `TASK_QUEUE.md`, council log, or `24-*`+ file read. Read-only throughout; nothing written.

## (a) Recommended path: C then B, amended — "protocol v4 + physically sized rev-4 registration + two quiet windows"

1. **Desk (now, no window):** land protocol v4 = pulse duration 2.0 s (currently 1.0 s, `joulewise/powermetrics_fiducial.py:63`), authenticated duration window 1.8–2.2 s (`:97-98`), inset 0.25 s unchanged (`:102`), protocol id v4. This is a D-138 pinned-file change, merge-staged into the successor re-freeze (`docs/decision_log.md:10361-10375`), which is exactly the transaction we are doing anyway.
2. **Desk:** write registration rev 4 (rules in (c)), sealed before the first v4 capture. Fixture replay of the 24 archived n1/n2 captures against the interior rule confirms the miss mechanism (already shown: all eight misses had intervals straddling the interior, `docs/process_traces/2026-09-19-activation-b165c535/03-diagnostic-invalid-captures-astra.md:2` `misses`).
3. **Quiet windows:** two 12-slot derivation windows, ≥ 6 h apart, any hour, any dates. Issue on retained n ≥ 12; a third window is pre-authorised only on n < 12 (stop on count, never on values).
4. **Desk + cold gate:** derive, issue, re-freeze pins, regenerate G2-a bindings.
5. **Parallel, non-blocking, needs Ed's `sudo -n` powermetrics only (already in sudoers for the chain):** the A243 35-min attribution matrix as a diagnostic window. Its result changes paper disclosure only, not the path, unless it shows native intervals > 0.75 s under load.
6. **Ed hardware:** none on the critical path.

## (b) The physics: cadence is a yield problem and a +0.4 J problem, not a claim threat

- **Why captures fail.** The detector needs one whole sample inside `[on+0.25, off−0.25]` (`powermetrics_fiducial.py:751-761`). With 1 s pulses that window is 0.5 s; a whole interval of length h fits at every phase only if h ≤ 0.25 s. 25G83 medians are 0.244–0.254 s, p95 0.274, max 0.419 (packet `01-cadence-facts.md:20-27`; `06-consult-instrument-cadence-astra.md:15`). One miss in 59 pulses invalidates the capture, hence 11/24. With 2 s pulses the window is 1.5 s, guaranteeing a whole interval for any h ≤ 0.75 s, 1.8× the worst interval seen. Yield returns to the anchor-limited rate (2/24 anchor failures on n1+n2; 11/12 anchors bounded on the 09-23 pilot, packet `03:12`), so ~20 retained from 24 slots.
- **B does not contain the cadence.** B = worst residual endpoint + anchor bound (`powermetrics_fiducial.py:1041-1043`). The nine ordinary retained 25G83 values sit at 0.028–0.043 s versus r6's 0.023–0.033 s (`01-n2-20260919-harvest-record.md:59-69`; `03-diagnostic…:2` `valid_fields_s`; `configs/calibration/calibration_acceptance_d079_v2_n17_r6.json` `source_statistics`). At the 33 W historical phase step (`docs/decision_log.md:4758-4769`) that is ~1.4 J versus ~1.0 J: the attribution limit moves by about 0.4 J. The anchor term widened from ~0.3 ms to 1–3 ms, i.e. ≤ 0.1 J.
- **The two outliers are not cadence.** 0.173 s (n1 d05) and 0.133 s (n2 d11) are single fitted onsets of +169 ms with 5 ms residual width: the GPU started late or the model says so (`03-diagnostic…:2` `decomposition`). They are 2 events in ~650 pulses. They, not the sampler, are what could put ~5 J on a bracket.
- **Paper quantities.** Segment energies of 10–600 s at 20–40 W are 200 J to 18 kJ. Timing error is ΔP at each boundary × operative bound (`joulewise/calibration_bracketing.py:2572-2579`). Idle-bracketed segments (R-Q1's design, council ruling `:18`) have ΔP ≈ 0 at the boundary, so the term is ~0. Phase-split boundaries at 33 W with a bulk operative bound ≈ 0.04 + 0.015 = 0.055 s give ~1.8 J per boundary: 1.8 % of a 10 s segment, 0.02 % of 600 s. Even an outlier-inflated bound of 0.18 s gives 6 J per boundary, under 5 % of the shortest planned segment. No planned claim (R-Q1 P̄(L), R-Q2 ratios, R-Q3 J/attempt, `_v5` 1.7B-vs-8B prefill at tens of J) sits near the 5 J bar.
- **Where the outliers do bite:** if they enter the successor statistics, SD of the eleven seen values ≈ 0.048 s, Q99 ≈ 0.2 s, S ≈ 0.145 s, so every later claim carries a ≥ 0.145 s allowance (~4.8 J) regardless of its own endpoints. Without them SD ≈ 0.005 s, S ≈ 0.015 s, allowance ≈ 0.5 J. That is the one place the acceptance design, not the physics, decides the paper's bar.

## (c) Barriers: keep / change / drop

| Barrier | Verdict | Reason |
|---|---|---|
| Plateau interior, SNR ≥ 10, 59-pulse detection, edge coverage, anchor feasibility, hash authentication | **keep** | evidence-bound; the interior inset 0.25 s is the measured ramp width (`03-diagnostic…:2` "ramps through 6.41, 33.88, 40.65 W") |
| Screen challenge: halt if ≥ 2 members exceed r6's max 0.0329 s (`preregistration_d079_epoch_25g83_rev1.md:188-190`) | **replace** with an absolute ceiling: any member B > 0.25 s (one sample interval; ~8 J) refuses issuance and names the mechanism | r6's maximum is a 25F84 statistic, not physics; on 25G83 it fires with certainty (10/11 seen above it), so option B as written cannot issue without an Ed ruling. Any sub-sample estimate beyond one interval means the localisation failed, which is a mechanism |
| Distinct calendar days ×3 (`:143`) | **change** to ≥ 2 windows ≥ 6 h apart, any dates | the population S must cover includes across-hours drift (r6 spans 07-22 to 07-25, member ids); the calendar date is not the mechanism, elapsed hours and thermal state are; Ed's quiet-any-hour rule stands |
| Retained n ≥ 19 (`:173-177`, from D-126 yield arithmetic `decision_log.md:6631-6640`) | **change** to n ≥ 12 | the level screen is an order statistic covering n/(n+1) of the population: 92 % at 12 vs 95 % at 19, a ~3 % difference in later bracket refusals, an operating cost, not a soundness term; t(0.995,11) = 3.106 vs 2.878 widens Q99 by 8 % in the conservative direction; the 19 guarded the df = 1 tail, which n = 12 also clears |
| 12 slots/window at 600 s cadence | **keep** the slot cadence (thermal return to idle), drop the "night" framing; 4–5 windows/day allowed | |
| No B-based exclusion (`:158`) | **keep**, plus one registered diagnostic | excluding high-B members would lie about the instrument; instead register: count members with B > 0.075 s (half the 5 J bar), report, and if ≥ 2 the artifact is labelled "excursion-limited" and the estimator lane in (f) opens. No halt: the numbers stay honest, only the bar widens |
| Equivalence shortcut (rev 2, `:428-435`) | **drop** | 0.48 pass rate on an unchanged instrument (`02-fresh-opus-review-verified.md:12`); v4 is a new protocol anyway; M1's TOST replacement is moot for acceptance |
| Blindness fence (`:179-186`) | **keep** as built | harmless; Ed's rules-before-data clarification governs |

**Rules-before-data.** The 11 seen values and 24 captures are protocol v3 and may never be members of a v4 corpus. They may, and should, set the rules: pulse length, the 0.25 s ceiling, the 0.075 s excursion threshold, and the n floor, all fixed in rev 4 before any v4 capture. That is exactly Ed's definition of blindness (`:490-497`). The qpe01 pilots supply the cadence distribution (h_max) for the same purpose.

## (d) What would show this wrong, and how it shows

- v4 window 1 yields < 60 % valid: the interior rule was not the whole miss mechanism. Detected at harvest by reason counts; then the A243 matrix becomes blocking.
- ≥ 3 of 12 members with B > 0.075 s, or any B > 0.25 s: excursions are frequent, not rare; issuance refuses or labels; estimator lane (f) before G2-a claims.
- Median delta_on on v4 differs from r6's 10–13.5 ms by > 10 ms: the longer pulse changed the fit; registered diagnostic, compared before issuance.
- After issuance, > 1 in 3 G2-a brackets refuse on the level screen: n too small or excursions; pre-authorised third window widens the corpus.

## (e) Calendar

| Milestone | Earliest |
|---|---|
| Protocol v4 + rev 4 registration + issuer changes landed | 09-25 evening |
| Derivation windows 1 and 2 (≥ 6 h apart) | 09-26 (e.g. 03:00 and 13:00) |
| Acceptance issued, re-freeze, G2-a bindings regenerated | 09-26/27 |
| G2-a armed | 09-27 (09-28 with rehearsal slack) |
| Calibration night (R-Q1/R-Q2) armed | 09-28/29, registration and meter payload prepared in parallel from now |

Two months of margin to end of November remain.

## (f) What the question misses

- **B conflates clock offset with GPU launch latency.** A common shift across 59 pulses is the clock; a single +169 ms pulse is the GPU. An estimator that bounds the common shift and reports per-pulse jitter separately would cut B ~4× on excursion captures. Not for this week; it is the right v3-estimator lane, and launch latency is a paper-worthy measured quantity in its own right.
- **Cadence changes the G2-a rung, not its truth.** D-166 selects the prefill length by ≥ 5 overlapping power records (`decision_log.md:212`); at 0.245 s that needs ≥ 1.2 s of prefill, so the selected rung will be longer. The ladder to 4096 handles it; nobody has said so.
- **Option B is a guaranteed halt** via the screen challenge; the packet's n-projection is moot.
- **The 1 J and 5 J figures are Window-A phase-contrast legacies.** The current science works in hundreds of joules per unit; the acceptance's urgency is unblocking refusals, not protecting a number.
- **The KM003C meter at ~0.5 s needs the same interior arithmetic** for any pulse-based alignment.
- **Restoring 120 ms is not free:** an argv change is also a pinned change and the cause is unproven; 2 s pulses are robust to any future OS cadence up to 0.75 s.
