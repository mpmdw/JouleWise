# Fable 5.1 blind seat — ACCEPTANCE-25G83-02

Worktree `wt-152c9255-acc-fable` at 032e9661, read-only; scratch none. Every number below was re-derived from the cited file or re-computed from the raw data named.

## Q1 — The cure: (A), Interactive launch context, protocol v3 unchanged

**Geometry (from code).** Pulse 1.0 s (`joulewise/powermetrics_fiducial.py:63`), inset 0.25 s (`:102`), so the authenticated interior is 0.5 s. The rule at `:751-761` needs **one** frame wholly inside the interior (two frame boundaries = the question's "two samples"). A frame of length h fits at every phase iff 0.5 ≥ 2h, i.e. h ≤ 0.250 s; two whole frames are guaranteed iff h ≤ 0.167 s.

**Observed distributions.**
- Interactive, session C, all 6 I cells, 3172 cpu-rail frames (`/Users/edr/osctx-mvp-01/sessionC1/C1/C1-0*.I.a1/runs/*/power_trace.csv`, my recomputation): median 131.6 ms, p95 134.7, p99 135.9, **max 140.8 ms**; zero frames > 167 ms. Shell: median 121.0, max 131.2. r6 reference: per-run medians 119.6–121.1 ms, overall max 144.252 ms (`31-coldgate-packet-acceptance/ex-22-packet-01-cadence-facts.md`, table row 1). Interactive's worst frame is inside r6's own maximum.
- Night tail, n1 raw plists re-parsed (`~/night-archive/d079-epoch-25g83-derivation-n1-20260919-harvest-20260919/runs/instrument_validation/*-d01..d12/raw/powermetrics.plist`): medians 244.3–249.8 ms, p95 273.0–274.8, max 280.1–353.3 ms; **44–50 % of frames exceed 250 ms**, 86–90 % exceed 167 ms.

**Margin.** At 131.6 ms every interior holds ≥ 2 whole frames at every phase (0.5/0.1316 = 3.8); the single-frame guarantee survives a 1.78× degradation of the observed max (250/140.8). At the 245 ms regime the guarantee fails for nearly half of all frames, which is why 11 of the 13 invalid captures were `no_plateau_interior_intervals` (`ex-22-packet-03-evidence-inventory.md`, n1/n2 rows). Production's idle baseline: 300 × 0.1316 = 39.5 s against the 55 s bound (`joulewise/adapters/powermetrics.py:1468-1470`); at 245 ms it needs 73.5 s and times out (record 21). v4's 1.5 s interior tolerates h ≤ 0.75 s; that headroom is only needed if the clamp recurs, and Q7 gives the detector.

**Labels.** `LABELS = ("com.joulewise.night", "com.joulewise.night.deadman")` (`joulewise/night_agent_install.py:39`) are both rendered from `configs/launchd/com.joulewise.night.plist.template` (`:608-629`), which has no `ProcessType`; the probe is rendered from `com.joulewise.night-probe.plist.template` (`:965-978`), also without. Add `<key>ProcessType</key><string>Interactive</string>` to both templates, so all three labels get it (the dead-man does not measure, but one template keeps one truth). `launchd.plist(5)`: unspecified ⇒ "light resource limits … throttling its CPU usage and I/O bandwidth"; Standard is equivalent to unspecified; Interactive has "the same resource limitations as apps, that is to say, none". Leave the magistrate plist alone; it never runs inside a window.

**Children.** The clamp is a task policy inherited through `posix_spawn`; nothing in the harness re-sets QoS (grep of `joulewise/*.py`, `scripts/run_night.py` for qos/taskpolicy/setpriority: empty). powermetrics is spawned by `subprocess.run` inside the same tree (`powermetrics.py:1201-1208`). Session C read QoS inside the child itself (`pilot/wl.py:5-8`, `pthread_get_qos_class_np`): 0x11 UTILITY under default, 0x15 under Interactive (record 26); and the production child's own cadence was the endpoint (I 131.6 ms vs D timeout). So the key reaches grandchildren without further work; confirm once in the Q2 check by recording the child QoS class.

**Executable text.** Add `ProcessType Interactive` to both plist templates. In `night_agent_install.py`, beside the KeepAlive refusals (`:975-976`, `:1091-1092`), refuse any template that lacks exactly `ProcessType = Interactive` (BLOCKER if omitted: a template regression would silently reproduce 09-19). Keep `PULSE_DURATION_S = 1.0`, protocol v3, `SUPPORTED_PROTOCOL_IDS` unchanged, r7 active; no r8.

Concerns: **BLOCKER** enforce-the-key refusal above. **NIT** record `ProcessType` in the arm evidence and the plan receipt.

## Q2 — Evidence sufficiency: one real-installer smoke under display sleep, then adopt

Session C is the right mechanism (a launchd job with the key, production `joulewise run` as child) but a different plist, a different parent driver, and **display on**. The 175 → 248 ms night gap under default was attributed to display-idle coalescing (record 01, conclusion) and Interactive-with-display-asleep is untested (record 26 §3). One check closes both gaps, mock-free, without a window:

**Smallest check (fixed now).** Ed away (HIDIdleTime > 600 s), no agent seats, display put to sleep (`pmset displaysleepnow`, no sudo), then the real installer's `--render-only` output of the amended night template bootstrapped on a throwaway label (standing approval for dummy-label live smoke), whose program is `run_night.py probe` extended to record one 300-frame `sudo -n /usr/bin/powermetrics -i 100 -b 0 -n 300 --format plist` capture through `_run_bounded_capture` plus the child's QoS class. **PASS** iff median frame ≤ 150 ms, max frame ≤ 200 ms, QoS ≠ 0x11, and the capture completes inside the 55 s bound. Two runs ≥ 30 min apart. FAIL ⇒ Q7 branch. Session C's SH/I result (E 0.99991 [0.99548, 1.00435]; R 0.99471 [0.99192, 0.99751], record 26) is not repeated; it answered bias, not cadence.

**Executable text.** Land the probe extension in the Q1 PR; run the smoke twice under display sleep before the equivalence night is armed; store both receipts in the arm record. **MATERIAL:** the criterion is written here before the data.

## Q3 — Registration under (A): Revision 5, not Revision 4

Equivalence path first. The D-102 addendum (`docs/decision_log.md:6704-6800`) is available again: its question ("did the OS release move the anchor bound?") is well-posed only when the sampler is in r6's regime, which Interactive restores (max 140.8 vs r6 max 144.3 ms). The 09-19 FAIL (m=7, max B 0.133, range 0.105) was measured in the clamped regime and does not bind; Ed's (c) ruling ordered exactly "restore the cadence" before more nights. The code exists: `joulewise/calibration_epoch_continuation.py` (MINIMUM_RETAINED 6, DECLARED_SLOT_COUNT 12, PASS ⇒ judged epoch added, read by `validate_powermetrics_fiducial.py:411-424`). The PASS test is not arbitrary: any B above r6's level screen would refuse ordinary preflights anyway (packet 02, bracket bullet), so PASS means "r7 will accept this instrument's captures"; FAIL means a successor is genuinely needed. On FAIL the night counts as W1 (Ed, 09-10 ruling, `:6784`).

Elements (a)–(l) for the FAIL branch:
- (a) epoch: **change** back to rev 1's six fields with `powermetrics_pulse_fiducial_v3`; add the launch context (`ProcessType Interactive`, recorded QoS) to known conditions. No r8.
- (b) two 12-slot windows ≥ 6 h apart: **keep** (different thermal/daemon state; calendar days were yield arithmetic).
- (c) n ≥ 12: **keep** (order-statistic coverage n/(n+1); t(0.995,11) widens Q99 7.9 % conservatively); salvage the D-126 addendum + issuer constant from the v4 branch.
- (d) futility 8/12, count-only W3: **keep**; expected valid rate now ≈ 22/24 (only the 2/24 anchor failures remain, rev 4 text), so it rarely fires.
- (e) blindness: **keep**.
- (f) disclosed inputs: **change**. Under v3 the 11 valid n1/n2 captures are *same-epoch*, and rev 1 refuses issuance on any valid same-epoch observation outside the registration (`preregistration…rev1.md:164-165`). Rev 5 must exclude sessions n1/n2 by a named, outcome-independent mechanism, "captured under default-ProcessType launch context (utility QoS)", disclosed as authored after their values were seen, and the issuer must honour an explicit excluded-session list. **MATERIAL**, small code change; never a workaround.
- (g) screen challenge: **drop** (diagnostic only). Under an identical instrument, P(≥ 2 of 12 new draws exceed the max of 17) ≈ 1 − (17/18)^12 − 12·(1/18)(17/18)^11 ≈ 0.14: a 14 % false refusal.
- (h) excursion rule: **keep** (one late onset sets S for every claim, ≈ 4.8 J at 0.145 s).
- (i) C = max(pred C, Q99, S), zero_headroom: **keep** (refusing a tighter instrument has no physical basis).
- (j) stale-number audit: **keep** verbatim (its dispositions do not depend on pulse length).
- (k) simulation: **keep** the n = 12 zero-admission result; label it as run under v4 geometry, which the admission gates do not use.
- (l) barrier basis: **keep**, replace "v4" with "v3 under Interactive launch context"; add launch context and per-window cadence flag to the physical list.

Already-seen captures: n1/n2 B values and the qpe01 pilots remain disclosed diagnostics only; none is a member or an equivalence value. Preregistration file: `configs/calibration/preregistration_d079_epoch_25g83_rev1.md`, appended as Revision 5 with the seal (digests of rev 5 and `protocol_v3.json` quoted in the arm notice).

**Executable text.** Append Revision 5 as above; keep the D-102 rule verbatim as the PASS test; state that a FAIL night is W1; desk-check that `authenticate_epoch_continuation` (`calibration_epoch_continuation.py:176-310`) does not refuse on the older finalized n1/n2 sessions, and if it does, land the smallest PR.

## Q4 — v4 work: close the PR, salvage five parts, keep v4 as a named fallback

Salvage into the Q1/Q3 PR: record 37 stale-number audit; D-126 and D-125 addenda with the issuer changes (n ≥ 12, zero_headroom); the excursion rule; `_native_frame_cadence_flag` in `reduce.py` (the only detector for a recurring clamp); the tests that do not pin v4. Drop: `protocol_v4.json`, `PULSE_DURATION_S = 2.0`, contract text "v3 or v4", the r8 reissue and its 70-test re-pin list. Fallback trigger: the Q2 smoke fails twice, or any window's recorded max native frame > 0.200 s under Interactive ⇒ reopen v4 (option B), re-using the passed desk replay. **NIT:** keep the branch, do not delete it.

## Q5 — Science risk, contaminants, admission

Nothing launched under the default agent (09-15 onward) is claim-bearing (scout 03, record 21 F-A), and D's compute was not slowed (0.98× I, record 26). Usable as descriptive/diagnostic only: n1/n2, all qpe01 pilots. Disclose in the paper: windows run as launchd user-agent jobs with `ProcessType Interactive`; the sampler's native cadence per window (median/max flag); that a utility-QoS clamp lengthened frames 2× on the abandoned September nights, whose data carry no claim.
- **Wispr Flow:** quit before admission. 5.3–5.8 % of a core continuously across all 13 cells (record 26 census) is the largest non-agent load; killing a user app is not hardware or sudo, so the agent does it and records it (no owner stop).
- **Display:** admit only the state in which the Q2 smoke passed; target display asleep (lower idle floor, Ed away). If asleep fails and on passes, register "display on" as a known condition.
- **PR #410 before the first window** (record 29: ~2,300 files indexed inside the period; a path change with no science content).
- **Network time:** keep the existing pause; the anchor bound (≤ 4 ms in session C) is the detector, and `Error:-99` with rc 0 must be logged as such.

**Executable text.** Add Wispr Flow to the census refusal list; record display state and cadence flag in every window's evidence; merge #410 first.

## Q6 — Order and authority (replaces R-ACC-6)

1. Desk PR (full tier, cold gate): templates + enforce-key refusal + probe cadence record + Revision 5 + salvaged v4 parts + issuer excluded-session list. 2. Merge #410. 3. Q2 smoke ×2 under display sleep. 4. Equivalence night (12 slots, Interactive, agent-free, Wispr quit) with the arm notice quoting the seal digests. 5. PASS ⇒ continuation addendum PR ⇒ calibration night on r7 ⇒ G2-a. FAIL ⇒ the night is W1 ⇒ W2 ≥ 6 h later ⇒ count-only W3 ⇒ cold science gate ⇒ successor issued ⇒ calibration night. m < 6 ⇒ one more equivalence night. Ed's items: none beyond the notice NO; sudo rules already cover `powermetrics` passwordless; **R-ACC-5 stands** (auto-update off until 2026-11-30, settings, not sudo; a build change voids rev 5 by its epoch clause).

## Q7 — What proves this wrong, and where it is caught

- Interactive still coalesces under display sleep ⇒ Q2 smoke (median > 150 or max > 200 ms) ⇒ option B.
- The clamp recurs mid-night ⇒ per-window cadence flag and the 55 s fail-closed ⇒ v4 fallback.
- B values under Interactive still exceed r6's level ⇒ equivalence FAIL ⇒ derivation branch, no data lost.
- A stable launch-context bias in E (widened interval [0.861, 1.161] crosses 3 %) ⇒ common to every arm of every window, so it cancels in contrasts; absolute numbers carry the disclosure line.
- The continuation module refuses on old sessions ⇒ Q3 desk check, PR, never a hand edit.

## Where I expect the other seats to be wrong

- Choosing (B) "belt and braces": v4 forces an r8 reissue, 70 re-pinned tests and closes the equivalence path (protocol id changes the epoch); the detector plus a named fallback buys the same safety.
- Treating session C as sufficient without a display-asleep smoke: that is the one untested cell, and it is where the default job was worst.
- Missing that under v3 the n1/n2 captures are same-epoch and the issuer refuses on them (rev 1 `:164-165`).
- Keeping or silently reviving the screen challenge: 14 % false refusal on an identical instrument.

## Plain summary for Ed

The sampler was never broken. macOS quietly throttles background jobs that are started by the scheduler without an "interactive" tag, and our night job had no tag, so it sampled every quarter-second instead of every eighth. Adding one line to the two job templates fixes it; last night's test under that tag ran at 132 ms with a worst frame of 141 ms, inside the July instrument's own range. The longer-pulse redesign is not needed; it stays on the shelf with a trigger. Before trusting the fix we run one two-minute smoke under the real installer with the display asleep, the only case not yet measured. Then one quiet night compares the new build against the existing calibration; if it agrees, we continue that calibration and go straight to the first real science night. If it disagrees, that night counts as the first of two toward a fresh calibration. Nothing here needs you except the standing "reply NO" on the arm notice and keeping automatic macOS updates off.
