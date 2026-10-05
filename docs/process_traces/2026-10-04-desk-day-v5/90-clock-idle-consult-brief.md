# Consult (blind, one round): the `s1` clock and idle-admission budget

You are one of two independent consult seats (the other is a different model). Explicit license to disagree, including with the framing. Read-only: write nothing in the repository; write only your answer. At most 1,000 words, file:line evidence for factual claims. One session, foreground only; finish in this turn.

## Situation
JouleWise measures LLM inference energy on a dedicated M3 Max. Power samples are timestamped by the wall clock; network time stays OFF across windows, so the wall clock drifts relative to the raw monotonic counter at the kernel's stored frequency correction. Two admissions use the difference between them (the "anchor"):
1. **T-0 author** (`joulewise/arm_readiness_evidence_t0.py:1176-1187`): refuses when |Δanchor| > 5 ms between the T-0 sequence's first reference sample (R0) and the author's own anchor; span R0→author is 600–3600 s.
2. **Per member** (`joulewise/uncertainty_evidence.py`, pinned estimator file; do not propose edits to it): the effective clock-anchor bound must be ≤ 5 ms; a stream shorter than 60 s yields `clock_fit_span_insufficient` → status `unknown`.

An Opus pre-mortem (`/Users/edr/night-archive/ia-0a40/MEMO.md`, read §1.1, §1.8, §1.14, §1.21 and "C. Decisions", item 2) found:
- The kernel's current correction is −3.17 ppm (read-only `ntp_adjtime(modes=0)`), so a T-0 span over about 1579 s refuses. Each network-time ON lets `timed` draw a new rate; observed draws ran from −8.7 to +12.3 ppm; about 15% exceed 8.33 ppm, at which even a 600 s span refuses.
- All 99 configs `s1` runs have `idle_seconds` 30 → streams of about 52–59 s → `unknown` → RECOVER classified as physics → END STATE. G2-a fixed the same hazard on 09-10 (idle 30→75): block 3's 50 anchors were all bounded, the largest 4.02 ms.
- Idle admission retries once with no backoff inside the same sampler stream; P(at least one admission abort in s1's 23 gated members) ≈ 0.46 by a Jeffreys simulation; one abort ends `s1` as physics. A 300 s backoff inside one stream pushes it beyond the 5 ms budget.
- Options on the table: (a) drift-aware T-0 author bound 5 ms + RATE_CAP × span (RATE_CAP ≈ 12 ppm fixed at seal), mirrored in the G10 helper; (b) read the kernel frequency after G10's OFF and at every R0, arm only if |f| × span and h_max + |f| × longest stream fit 5 ms, with one allowed extra ON/OFF redraw before `a1`; (c) idle seconds 75 (block-3 precedent) or 55 (claim draft); (d) make an admission retry start a NEW sampler stream (a controller change), which also permits a 300 s backoff; (e) keep zero backoff and add a registration clause that one guard-attested admission abort re-arms a fresh `s1` without END STATE.

The registration draft is `/Users/edr/code/JouleWise-wt-dd5-block4/configs/campaigns/v5_qualification_25g83/registration_block4_draft.md` (§3.5, §4, §5, §7); sizing record 44 beside it.

## Questions
1. Which combination protects the numbers best for the least change? Name the exact values (idle seconds, backoff, RATE_CAP or frequency gate thresholds) and why, from the physics: what error does each guard keep out of an energy window?
2. Is a drift-aware T-0 bound sound — does it still catch a real resync step — and what bound would you register?
3. Is a retry-as-new-stream change worth it now, or is option (e) the better bet for one qualification night?
4. Anything the pre-mortem got wrong here.

Write your answer as the report body.

WRITE_SCOPE: []
