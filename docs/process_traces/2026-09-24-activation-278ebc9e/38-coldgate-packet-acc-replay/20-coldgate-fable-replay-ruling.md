# 20 — Cold Fable gate ruling: addendum to ACCEPTANCE-25G83-01, R-ACC-1(b) desk replay (packet 38)

Judge: Fable 5.1, fresh non-interactive session, worktree `JouleWise-wt-coldgate-278ebc9e-accr` at `1dbdd726`, 2026-09-24 06:17–06:5x PDT. Read-only except this file. No sudo, launchctl, powermetrics, systemsetup, subagents or background tasks. Nothing armed.

## 0. Disclosure and trust anchors

**Auto-loaded by the harness before any action:** `~/.claude/CLAUDE.md`, the worktree `CLAUDE.md`, the memory index `MEMORY.md` (partial). None used as authority or evidence. Not read: `CLAUDE.local.md`, `RUN_STATE.md`, `TASK_QUEUE.md`, council logs, run reports, memory files, any `docs/process_traces` file outside packet 38, ex-26 (not in the packet). Read under the charge's explicit allowance: the 24 archived captures under `/Users/edr/night-archive/…-n1-…` and `…-n2-…` (`events.jsonl`, `power_trace.csv`, `instrument_evidence.json`, `manifest.json`), and the replay re-run from a `/tmp` copy of this worktree.

**Validator record (method: `python3 scripts/validate_gate_packet.py`, then independent `shasum -a 256`):**

| Run | Expected charter sha | Observed | Result |
|---|---|---|---|
| 1 | `…d95d82` (deliberate typo) | `…d95d81` | REFUSE, `charter_trusted_observed_mismatch`, rc=2 |
| 2 | `099de884b1d081ffa547dfd8ff5837e75813a870ff8c7285c749c1b440c95d81` | same | PASS, rc=0; packet `c64ead37…9cfb7a55b` matches; all 5 exhibits expected == observed |

`shasum` reproduced both digests. `judge_handoff_bound: false` is the validator's label for a non-runner invocation, not a defect.

## 1. Verdicts

| Q | Verdict on the ruling text | Deciding evidence |
|---|---|---|
| J1 | **Different text.** The literal criterion is under-specified for captures the detector never fitted; corrected criterion in §3.1; applied: **PASS** (v3 22/22 defined comparisons exact; v4 0/1,416). The seat's literal FAIL stands on the record as issued. | `fiducial.py:948-976` (bypass before any `_fit_pulse`); `validate_powermetrics_fiducial.py:2472-2486` (unresolved run writes the CSV from native records); archive probes §2 M1 |
| J2 | **AFFIRM R-ACC-2 counts; add one disclosure sentence** (§3.2). Anchor failure is a separate, pulse-length-independent yield factor, observed 2/24; futility 8/12 and two windows survive it at both the point rate and the 95 % pessimistic rate. | `instrument_evidence.json` d07 `clock_anchor.detail = wall_minus_monotonic_span_exceeded`, d10 `= affine_clock_fit_empty`; all 18 recorded pulse failures across 24 captures carry exactly one reason, `no_plateau_interior_intervals` |
| J3 | **AFFIRM ruling 1(b) as written:** the jittered r6 diagnostic is still run, diagnostic only, not a merge precondition (§3.3). | ex-20 `:63` sentence 3 |
| J4 | Four additional findings (§2 M2–M4, N1). No REFUSE. | — |

Packet hygiene: complete and neutral for the questions asked. One omission the charge could not have known: it does not disclose that the two disputed captures' trace timeline is a fallback, which is the deciding fact for J1 (§2 M1). This is not a cherry-pick; the exhibits contain the data that reveals it.

## 2. Findings, tiered

**MATERIAL M1 — The four "extra" v3 misses are computed on a fallback timeline that is not the command clock, so they are not "misses at the actual commanded pulse times". Verified against primary evidence:**

- Production never ran the interior rule on d07 or d10. `detect_pulses` returns at `powermetrics_fiducial.py:948-976` with `fits=()` when `projection_bypass_reason == CLOCK_ANCHOR_UNRESOLVED`, before the `_fit_pulse` loop at `:977-990`. Their `recorded_fit_count` is 0 for that reason (`ex-34-replay-results.json` captures n1-d07, n1-d10). Equality "replay == recorded" is therefore undefined for them, not false.
- Their `power_trace.csv` is not anchored. `scripts/validate_powermetrics_fiducial.py:2472-2486`: when `point_anchor_s is None` the runner sets `anchored = native_records` and writes the CSV from those; the adapter's comment at `joulewise/adapters/powermetrics.py:575-579` calls this the "fail-closed timeline … never re-enters any claim math". The 22 resolved captures use `parse_powermetrics_records(data, first_record_endpoint_s=point_anchor_s)`, the same construction production re-derivation uses at `fiducial.py:1250-1258`, which is why they match exactly.
- Measured consequence (my probe, first frame above 20 W minus commanded on, all 59 pulses): n1-d01 median −0.005 s, n2-d05 +0.019 s (aligned); **n1-d07 median −0.403 s (range −0.565…−0.177); n1-d10 median −0.621 s (range −0.788…−0.447)**. The plateau sits about half a second before the commanded window on those two timelines.
- Frame structure differs too: resolved captures have contiguous frames (max overlap 0.0000 s, max gap 0.0000 s, n1-d01 871 frames); d07/d10 have 427/422 overlapping pairs (max 0.15 s) and 427/433 gaps (max 0.15 s). Interval geometry there is native-stamp arithmetic, not the anchored frame sequence.
- Illustration, n1-d07 pulse 13: commanded interior [467.4271, 467.9378]; frames [467.4234, 467.6836] (starts 3.7 ms early) and [467.8019, 467.9439] (ends 6 ms late). A geometric near-miss on a timeline offset by ≈0.4 s from the one production would have used. The indices 13, 52, 24, 56 carry no information about which pulses would have missed under a resolved anchor.

Effect on J1: the v3 half of the criterion cannot be evaluated on d07/d10 by any replay, because no reference exists and the timeline is not the command clock. The v4 half **can**: with max frame length 0.309 s (d07) / 0.282 s (d10), max gap 0.15 s, any 1.5 s interior contains a whole frame regardless of time offset. The v4 zero-miss result holds on all 24 captures and is time-base invariant on the two fallback ones. This is the only correct reading; the exclusion below is mechanism-defined and outcome-independent (it would exclude d07/d10 whether the replay found 0 or 59 misses there).

**MATERIAL M2 — The replay script will refuse to run on the very PR it gates.** `ex-34-replay.py:89` raises unless `evidence["protocol_id"] == detector.PROTOCOL_ID`. Ruling 1(a) sets `PROTOCOL_ID` to v4 in the same PR that ruling 1(b) makes the replay a pre-merge gate of. On that tree every archived v3 capture trips `unexpected recorded protocol`. Likewise `:100` hard-codes `+ 1.0` s rather than `PULSE_DURATION_S − 1.0`. Cure §3.4(a).

**MATERIAL M3 — README and seat report describe the four indices as physical misses.** `ex-34-replay-README.md` last paragraph: "Their archived frames still show four empty interiors at the actual command times"; ex-33b F1: "their frames yield four v3 interior misses". Both are wrong per M1 and would mislead a later reader. Cure §3.4(b).

**MATERIAL M4 — Anchor failures are a distinct yield mechanism the plan must name with its observed rate.** Verified: across all 24 captures, every undetected pulse (18) has exactly one reason, `no_plateau_interior_intervals`; the 11 valid / 13 invalid split is 11 interior-failed + 2 anchor-failed. The two anchor details are `wall_minus_monotonic_span_exceeded` (d07, span 0.0062 s: the wall clock slewed against monotonic during the capture) and `affine_clock_fit_empty` (d10). Neither takes pulse duration as an input; the anchor is built from native whole-second rollovers (`native_rollover_count: 198` in d01; adapter `:1585-1600`). v4 fixes none of it. Arithmetic (binomial, my computation):

| Per-slot valid rate | P(W1 < 8 of 12) | P(< 12 valid in 24) | E[valid of 24] |
|---|---|---|---|
| point 22/24 = 0.917 | 0.0019 | < 1e-5 | 22.0 |
| Clopper–Pearson 95 % pessimistic, 0.760 | 0.137 | 0.0014 | 18.2 |

Two windows and futility 8/12 survive both rows. No count changes. Cure §3.2 (disclosure only).

**NIT N1 — Charge background says the replay "finds v3 misses 13, 52 (d07) and 24, 56 (d10) there".** True of the script's output, false as a physical statement (M1). Record in the synthesis; no cure beyond §3.4(b).

**Not a defect, recorded because verified:** re-running `ex-34-replay.py` from a `/tmp` copy of this worktree at `1dbdd726` reproduced `ex-34-replay-results.json` byte-for-byte (24 captures, `verdict: FAIL`, rc=1, 0.38 s). Source digests in the results file equal the `artifact_sha256` entries inside each capture's own `instrument_evidence.json` (checked d01, d07, d10). Observed v3 pulse durations: min 1.0004 s, median 1.0053 s, max 1.0111 s over 1,416 pulses, so the +1.0 s counterfactual yields 2.000–2.011 s, inside the 1.8–2.2 s authenticated window of ruling 1(a).

## 3. Rulings (final texts, executable without choice)

**3.1 J1 — replace ruling 1(b)'s PASS sentence with this text:**

> (b) Desk replay gate, before the PR merges: run the interior rule (`_fit_pulse`, inset 0.25 s) at the commanded pulse times from `events.jsonl` over the 24 archived n1/n2 captures. A capture is *fitted* iff its `instrument_evidence.json` has `clock_anchor_resolved: true` and 59 pulse rows; otherwise it is *unfitted* (its `power_trace.csv` is the native fallback timeline, not the anchored one). PASS iff (i) for every fitted capture the v3-geometry miss indices equal the recorded `no_plateau_interior_intervals` indices exactly, and (ii) for every one of the 24 captures the v4 geometry (observed on-stamp, observed duration + 1.0 s, 1.5 s interior) produces zero misses. Unfitted captures are reported with their v3 indices labelled `v3_comparison_undefined_unfitted`, and count toward neither (i) nor a mismatch. If either (i) or (ii) fails, stop and return to the council.

Applied to the exhibits: fitted = 22 captures, all `v3_exact_match: true`; unfitted = n1-d07, n1-d10; v4 misses = 0 of 1,416. **R-ACC-1(b): PASS.** The seat's recorded "FAIL" under the superseded literal text remains in the historical record as issued (charter §9); it is not converted, it is succeeded by this criterion.

**3.2 J2 — append to ruling 2(f) (disclosed design inputs) this sentence:**

> Anchor-failure rate: 2 of 24 n1/n2 captures were `clock_anchor_unresolved` (n1-d07 `wall_minus_monotonic_span_exceeded`, n1-d10 `affine_clock_fit_empty`); pulse duration is not an input to the anchor, so v4 leaves this rate unchanged. Expected per-slot valid rate under v4 ≈ 0.92 (point), ≥ 0.76 (95 % pessimistic); at both rates P(W1 futility) ≤ 0.14 and P(fewer than 12 valid in 24) ≤ 0.002. The futility threshold 8/12, two windows and the count-only W3 are unchanged.

No change to 2(b), 2(c), 2(d) or 2(l); "anchor feasibility" already appears in 2(l)'s physical list.

**3.3 J3 — AFFIRM ruling 1(b) sentence 3 unchanged:** "ex-26's jittered resampling of r6 is run and committed as a diagnostic trace only; it is not a gate." Execution text: the seat runs it now, commits the trace under the 34 replay directory alongside `results.json`, and the PR does not wait on it; if it is not landed when the PR is otherwise ready, the PR merges and the trace lands in the next commit of this activation. Its output changes no rule and no count.

**3.4 J4 — two cures, same PR as the replay:**

(a) In `replay.py`: replace `detector.PROTOCOL_ID` at line 89 with the literal `"powermetrics_pulse_fiducial_v3"`; replace `+ 1.0` at line 100 with `+ (detector.PULSE_DURATION_S - 1.0)` guarded by `assert detector.PULSE_DURATION_S == 2.0`; add the fitted/unfitted label of 3.1 to each capture record and make `verdict` follow 3.1. Re-run; commit the new `results.json`; expected `verdict: PASS`, rc=0.

(b) In the replay README and in the synthesis's quotation of ex-33b F1: replace "four empty interiors at the actual command times" and "their frames yield four v3 interior misses" with: "their `power_trace.csv` is the unanchored native fallback timeline (plateaus sit ≈0.40 s and ≈0.62 s before the commanded windows; frames overlap and gap by up to 0.15 s), so no per-index v3 comparison exists for them; the v4 zero-miss result is time-base invariant and holds."

## 4. Plain-language summary for Ed

1. The longer 2-second pulse is confirmed: on every one of the 24 archived recordings, the new pulse length always contains at least one whole power sample, with margin. The 1-second pulse's failures are reproduced exactly wherever the instrument had actually scored them.
2. The two recordings that looked like a mismatch were never scored by the instrument at all, because their clock could not be pinned to the power trace. Their timeline is a placeholder that sits about half a second off. Comparing the replay against nothing on a shifted clock is meaningless, so the rule now says so explicitly. With that fix the gate passes.
3. Those two clock failures are a separate, small loss mechanism (about 1 in 12 recordings) that the longer pulse does not touch. The two-window plan absorbs it comfortably; nothing in the plan's counts changes, it is simply written down.
4. The replay script has to be adjusted so it still runs after the code switches to the new pulse length, and two sentences in its write-up that call the shifted-clock frames "real misses" are corrected.

Final: no REFUSE; no BLOCKER; four MATERIAL (M1–M4) cured by the exact texts in §3; R-ACC-1(b) PASSES under the corrected criterion 3.1, and the plan proceeds to ruling 1(c).
