# 04 — THROUGHPUT-01: Fable synthesis of the three-seat consult (Fable 5.1, Opus 5.5, Astra high)

Ed, 2026-09-23 ~03:50–04:05 PDT, verbatim: "consult you, opus and astra high on how to remedy this and churn windows
asap"; "you guys solve that to get the whole process running efficiently so i can remove as many barriers to as much
science squeezed out of this machine now that it seems the instrument is fairly solid"; "get this cycle running as
efficiently as possible". Seats: Opus 5.5 (record 05), Astra high (record 06), Fable (this synthesis, one notch above
Opus on judgment per Ed 03:40; dissent recorded, never dropped). Every number is an estimate.

## Ruling on the framing (dissent recorded)

Opus: "windows are still the bottleneck: the limit is how many windows produce USABLE data" — verified that no
paper-bearing measurement has run (every night so far was instrument qualification), that `evidence_night.py` accepts
only the idle kind `quiet_predicate_evidence`, and that A212/A234 are READY, not landed. Astra: "review cadence is a
workflow choice, not a fixed cost". Fable adopts BOTH: this week the binding constraint is the gate chain plus the
missing model-run arm path; from week two it is usable windows per day. Ordering below follows that.

## The lane, in dependency order (magistrate executes; Opus loop, Sol 6.0 seats, Fable final pass)

1. **Finish the window machinery this week.** (a) v3 non-observer predicate (in flight, PR pending). (b) Land A234
   WATCHDOG-EARLY-REFUSAL-RELEASE-01 and A212 refusal fast-retry together, reconciled with NIGHT-GATE-QUIET-ADMISSION-01
   and the 40-minute arm lead (Astra: a 20-minute recovery is not credible until the lead is reconciled; target a
   10-minute lead for template re-arms). (c) A271: the corecaptured Wi-Fi toggle inside `check`. Files: `scripts/
   magistrate_watchdog.py`, `joulewise/arm_retry.py`, `docs/process/NIGHT_HANDBACK.md`, `docs/phase_2/
   derivation_night_runbook.md`, `docs/process/state_kernel.json` + generated regions. Release the hold only on
   positive terminal evidence plus delivery, never on a refusal file's existence.
2. **Build the headline's critical path in parallel, now (none of it exists):** a scored-campaign night kind in
   `joulewise/evidence_night.py`; a MATH importer cloned from the GSM8K pattern in `benchmark_import.py`; the D-166/AP-5
   amendment that lets MATH's author levels be the difficulty axis while keeping AP-5's bans ("difficulty causes
   energy", "intelligence per joule") and the contamination caveat (`benchmark_import.py:84,88`). Three independent
   packets, three seats in parallel, ONE integration adjudication.
3. **One registration packet for the whole headline campaign:** both thinking arms, both ladders (MATH levels +
   `affine_mod_ladder_v1`), the 16-item sizing pilot and what it may set (items per envelope, caps, never which levels are
   reported: D-062), merge order for sparse levels, the multiple-testing family (Holm), fixed n. One cold gate instead
   of three or four. Envelopes are sized by decode tokens, not by cell (Opus: 64 thinking-off items on the 8B ≈ 700 s >
   480 s; the thinking-on arm ≈ 8 h of 8B decode). Spend envelopes on more items, not repeats (greedy decoding replicates
   energy only); 128 items per level if the pilot shows it affordable; same items for both models.
4. **Window queue.** States: authored → dry-checked → reviewed → eligible → armed → harvested. The successor plan is
   authored and dry-checked BEFORE the agent exits for the current window (never during capture on this machine); the
   arm follows the harvest and proven cleanup with fresh check/notice/veto. Template re-arms (an already-ruled plan with a
   new start time) need only notice + veto, guarded by a template hash. Target 4–5 windows/day on the dedicated Max.
5. **Risk-tiered gates (process rule; adopted by Fable under Ed's "you guys solve that", Ed may object):** the full
   shape (Opus lens + Sol refuters + COLD Fable instance) is mandatory for a FIXED file list — reducers, admission
   predicates, plan writers, `docs/contracts/analysis_plans.md`, `benchmark_import.py`, registrations, anything
   claim-bearing — and for every arm. Routine changes (docs, tooling, pins, tests-only) get an Opus lens plus a Fable
   final pass that reads the lens and the diff (minutes, not a fresh investigation). Failure mode: a claim-bearing file
   missing from the list; the list is reviewed at each kernel touch. Expected: ~2 substantial gates/day.
6. **Fewer fix rounds via stronger briefs:** every brief carries a clause-to-acceptance map, an executable
   counterexample, the production call site that consumes the fix, and the unresolved rulings named; evidence
   mechanically assembled; delta audits and raw-evidence access preserved. Expected 0.5–2 days saved per gate.
7. **Desk work off the Mac during windows:** evaluate cloud Claude Code sessions against origin for bench-free seats
   (reviews, drafting, packet assembly) so gates proceed while windows run (+~1 gate/day). Bench-needing seats keep the
   Mac between windows. Never an agent on the Mac inside a window.
8. **Writing from day one:** living draft under `docs/paper/`; Opus drafts Paper B methods and limitations (the daemon-
   contamination episodes are what a metrology reader values), the headline's intro, related work, pre-registered plan,
   and BOTH the crossover and the null paragraphs; Sol builds figure and table code on `joulewise/paper_rendering.py`
   against watermarked pilot data, regenerated from authenticated harvests; Fable runs the first-use test and the final
   pass. The advisor sees the methods section and one pilot figure in week two. Ed gets a weekly decision packet.
   Expected 5–8 end-iteration days recovered.
9. **Result risk:** the pilot sizes runtime and caps only; report per level the accuracy ratio the 8B would need to
   break even plus the decomposition J/correct = J/token × tokens/attempt ÷ accuracy; an interval spanning 1 is
   inconclusive, not a null. Opus's prior: thinking-off never crosses (8B ≈ 3–4× per token vs ≤ 2× accuracy at level 5);
   a crossover, if any, lives in the thinking-on arm where the 1.7B's long traces hit the cap. Plan the thinking-on arm
   as primary for the crossover question and thinking-off as the decomposition baseline; register that ordering.

## Not to do (all three seats agree)

No agents or synchronization on the Mac during a window. No thinning of the full gate on claim-bearing changes. No
"intelligence per joule" or "difficulty causes energy" claims (AP-5). MATH accuracy is not capability (contamination).
Never divide idle-padded envelope energy by correctness. Keep attribution labels and denominator guards intact.

## Expected effect (estimates)

Headline campaign registered in week one instead of week two; usable windows 4–5/day from week two; data-complete for
the Apple-only characterization about mid-October; end iteration shortened by about a week. The NVIDIA leg is not
assumed. Same-packet score: Opus 5.5 supplied the verified facts (no model arm path, A212/A234 unlanded, envelope sizing)
that changed Fable's ordering; Astra supplied the workflow reframing and the queue-state model. Both PASS.
