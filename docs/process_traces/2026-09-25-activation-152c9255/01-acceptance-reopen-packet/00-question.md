# 01/00 — Reopened D-184 council ACCEPTANCE-25G83-02: the cadence cure is the launch context, not the pulse length

Assembled 2026-09-25 ≈04:30 PDT by the resident magistrate (Opus 5.5, activation 152c9255). Nothing is armed, and no night agent is loaded or on disk.

## 1. What changed since the last ruling

**The instrument.** Every science night needs a calibration acceptance under D-079, bound to the live macOS build. The machine runs 25G83, and the active acceptance, r7, is for 25F84. `powermetrics` is asked for one sample every 100 ms. Every one-shot capture carries 59 timing pulses: short, deliberate bursts of CPU load that the capture must detect so its clock can be anchored. Protocol v3 uses 1.0 s pulses and needs at least two whole samples inside each pulse's 0.5 s authenticated interior.

**The old premise.** On the 09-19 nights the samples arrived about every 0.245 s rather than r6's ~0.120 s. At that interval a 0.5 s interior often holds fewer than two samples, and 13 of 24 captures failed. The council and cold ruling ACCEPTANCE-25G83-01 (exhibit `docs/process_traces/2026-09-24-activation-278ebc9e/31-coldgate-packet-acceptance/20-coldgate-fable-acceptance-ruling.md` §3) treated 0.245 s as a property of the 25G83 build. Their cure was R-ACC-1..7:
- protocol v4 with 2.0 s pulses;
- a science-neutral r8 reissue;
- registration Revision 4: two 12-slot windows at least 6 h apart, retained n ≥ 12, the screen challenge dropped, the excursion rule, and the zero-headroom rule.

The work-in-progress PR for that plan sits at `origin/feat/2026-09-24-acc-25g83-v4-rev4` (head `ea10e3c8`). It is HELD and unmerged. The deterministic desk-replay gate passed (`.../38-coldgate-packet-acc-replay/20-coldgate-fable-replay-ruling.md`).

**The corrected premise.** An interactive seat, with Ed present on 09-24 evening, measured the cause. Records are on main under `docs/process_traces/2026-09-24-interactive-4b/`. Read 01, 21, 24, 26, 27, 28 and 29 first; 02–20 are its design and harness audits.
- From a login shell, the same binary and argv give a median interval of ≈118 ms.
- Under a launchd user agent with no `ProcessType` key, it gives ≈171–178 ms. That is what `joulewise/night_agent_install.py` renders from `configs/launchd/com.joulewise.night.plist.template`. The night is later, quieter and display-idle, and there it reaches 237–248 ms.
- With `ProcessType=Interactive` it gives ≈126–132 ms.
- The mechanism is launchd's default-ProcessType timer coalescing (utility QoS), not the 25G83 binary. The r6 corpus from July predates the launchd night agent, which landed on 09-15.
- **Session 2 (record 21):** the production `joulewise run` under the default launchd context FAILED CLOSED 3/3 on a quiet machine. Its idle baseline at 237–248 ms overran production's 55 s capture bound (`_capture_timeout_s`).
- **Session C (record 26)**, launchd Interactive (I) versus a login shell (SH), with 6 Williams blocks and one production run per cell:
  - E (J per output token): SH/I = 0.99991, 99.375 % interval [0.99548, 1.00435], EQUIVALENT nominally. The widened worst-case-attribution interval [0.861, 1.161] crosses δ = 3 %.
  - R (tokens/s): SH/I = 0.99471 [0.99192, 0.99751], EQUIVALENT.
  - I's median idle cadence was 131.8 ms, missing its own 130 ms criterion but meeting the purpose-based test: all I runs valid and median ≤ 150 ms.
  - A CPU probe under default launchd (D) ran 0.98× the Interactive time, so there is no compute throttling, while ProcessType=Background ran 7.4×.
- **The reviews:** Astra (27) and a fresh Fable (28) both recomputed the result identically and said STAND WITH LISTED CORRECTIONS.
- **The census:** the largest non-workload CPU users were the agent sessions themselves and Ed's Wispr Flow dictation app (≈5 % of a core).
- **Record 29:** every per-night measurement clone `~/JouleWise-measurement-*` is Spotlight-indexed, so indexing load falls inside the measurement period. The peer seat's PR #410 moves clones under an excluded parent. That PR is not this council's to decide, but its ordering is.

## 2. Questions (answer each; give executable text; tier concerns BLOCKER / MATERIAL / NIT)

- **Q1 — The cure.** Choose one, or write your own:
  - (A) `ProcessType=Interactive` on the night agents, keeping protocol v3 with 1.0 s pulses;
  - (B) Interactive plus protocol v4 with 2.0 s pulses, as belt and braces;
  - (C) v4 alone, as ruled, with the launch context unchanged;
  - (D) something else.
  Say which launchd labels get the key: `com.joulewise.night`, `com.joulewise.night.deadman`, and the probe template. Say whether it must also reach child processes. Record 24/26 speak to QoS ancestry; verify it from the harness and the plist, don't assume it. Quantify the v3 interior margin at 126–132 ms, and in the 237–248 ms tail if coalescing recurs, using `joulewise/powermetrics_fiducial.py` and the observed distributions.
- **Q2 — Sufficiency of the evidence.** Is session C (an interactive-seat harness, not the installed night agent) enough to adopt the cure? Or must a rehearsal under the real installed night agent (the D-183 mock-free rule) show the cadence first? Name the smallest executable check and its pass criterion, fixed now.
- **Q3 — Registration.** R-ACC-2 (Revision 4) was written for v4 at 0.245 s. Under your Q1 cure, keep / change / drop each element (a)–(l), with the physical reason. Also say:
  - whether the D-102 equivalence path against the r6 envelope (continue r6 on PASS) is available again for 25G83 once the cadence matches r6's regime;
  - which already-seen 25G83 captures (n1/n2 09-19, qpe01 09-23) may be used, and how, without breaking rules-before-data;
  - that the preregistration is `configs/calibration/preregistration_d079_epoch_25g83_rev1.md`.
- **Q4 — Fate of the v4 work.** Close the v4/rev4 PR, salvage parts of it (the stale-number audit, the r8 reissue mechanism, the excursion rule, the simulation), or keep it as the fallback path with a named trigger?
- **Q5 — Science risk and contaminants.** The 09-24 record 84 flagged "launchd-launched inference may be throttled". Session C's D ≈ I result speaks to it. Is anything measured under a launchd night agent (09-15 onward) now usable or unusable, and what must the paper disclose? Rule on the window-admission conditions:
  - should windows quit Wispr Flow;
  - display on or asleep, since record 26 left display-asleep untested;
  - the ordering of PR #410 (clone relocation) against the first window;
  - network time.
- **Q6 — Order of steps and authority.** Replace R-ACC-6 with the new sequence, from desk work through the first science night (the calibration night per COUNCIL-407-01). Say what in this path, if anything, is Ed's under the D-184 addendum (Ed owns only hardware, sudo, a notice NO and claim publication). Say whether R-ACC-5 (the macOS auto-update hold) stands.
- **Q7 — What would prove your path wrong**, and which step of it detects that.

## 3. Standards

Ed's words: the orchestration exists for "preventing bad science, not progress on the paper when models agree". On this exact question (09-19): "do whatever makes sense to get good science done towards the paper. make sure the barriers to acceptance aren't overly strict for no reason". Every barrier needs a physical or statistical reason (the sensible-gates directive). Tolerances are sized to the instrument, which is attribution-limited at ~1 J with a ~5 J claim bar.
