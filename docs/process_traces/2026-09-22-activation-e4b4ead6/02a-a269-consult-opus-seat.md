# A269 ENVELOPE-START-DRIFT-01 — independent design consult (Opus seat)

Read-only, 2026-09-22, worktree `JouleWise-wt-mag-e4b4ead6` at `ecbc0fac`; archive
`/Users/edr/night-archive/qpe01-pilot-n1-20260922-0217-harvest-20260922/night/`. Bench numbers executed this session
with an agent session live, so they are upper bounds on an idle night.

## Recommendation

**Adopt cure 2 — re-register the protocol with a slot pitch strictly larger than the capture (`slot_pitch_s: 620`,
`envelope_s: 600` unchanged) — and decline cures 1 and 3.** Cure 2 is the only candidate that provably reaches the
≤ 2 s bar, and the night holds its proof: envelope 01, the one slot with no predecessor to wait for, drifted
**0.159 s** (`evidence_envelopes.jsonl` line 1). A 20 s gap makes every slot an envelope-01. Cure 1 does **not** reach the bar: I decomposed the tail at the bench and its largest term is not the
plist parse the diagnosis names but `cleanup_groups`' **113 serial `pgrep` subprocesses** (~2.6 s), which cure 1
leaves untouched — cure 1 plus the new A267 attestation lands at ~4.2–4.8 s. Cure 1 also buys that failure by re-architecting the evidence output
contract (two-stage `session.json`, batch finalisation) on the night-critical path; cure 3 re-sizes a gate away while
leaving the harness overrunning its schedule. Alongside cure 2, batch the group census into one `pgrep -g <list>`
call (measured **0.012 s**) — not to reach the bar but to cut the tail's variance. **A correction that
matters more than the cure choice: on the 09-22 night `start_drift` excluded zero envelopes that were not already
excluded on other grounds. See Q6.**

## Q1 — Which cure, with the per-slot serial arithmetic

Today `scheduled = first + (i−1) × envelope_s` and the same `envelope_s` is passed as `--duration-s`, so pitch equals
capture and the chain blocks on `collector.wait()` before the next `Popen`
(`joulewise/quiet_predicate_campaign.py:477–500`). Serial tail, envelope 02 (`session.json` stamps):

| term | night (env 02) | bench re-measurement |
|---|---|---|
| `sampling_stopped − scheduled` | 0.15 s | — |
| recorder TERM→exit wait | ≲ 0.35 s (residual) | `power.cleanup` rc 0, `kill:false` |
| `parse_frames`, 132,917,113-byte plist | ~4.6 s | **5.18 / 5.21 / 5.46 s** (read 0.01 s warm) |
| `align_frames` → `derive_powermetrics_anchor_v3` | 2.12 s (0.01 when the fit refuses early) | **2.39 s**, `bounded` |
| reduce_interior + 19× integrate + sha256(133 MB) | ~0.27 s | **0.05 + 0.16 + 0.06 s** |
| collector exit + `cleanup_groups` + `Popen` | ~2.6 s | 113–116 pgids per envelope (`evidence_envelopes.jsonl` `cleanup.groups`), each a separate `/usr/bin/pgrep -lf -g <pgid> .` (`campaign.py:127–129` → `scripts/run_night.py:3413–3427`) |
| **total** | **10.08 s** → envelope 03 drift 10.11 s ✓ | |

New A267 cost: the R4 attestation `log show`, run twice this session — **1.454 s** and **0.874 s** (46 lines) — and
R4 forbids deferring it to harvest.

**Cure 1** removes parse + derive + reduction: 0.15 + 0.35 + 0.2 (bare exit) + 2.6 (census) + 0.05 (spawn) ≈
**3.35 s**, plus the serial attestation → **4.2–4.8 s**. Fails. With the batched census folded in: ~1.05 s + 0.87–1.45
= **1.9–2.5 s** — still over at the top of the observed `log show` range, with zero margin, after re-architecting the
output contract. I will not recommend a design whose pass depends on the faster of two samples.

**Cure 2** makes drift the `Popen` latency alone, **measured 0.159 s**. Worst observed tail 10.23 s + worst
attestation 1.45 s = 11.7 s inside a 20 s gap → 8.3 s headroom; with the batched census, ~7.6 s tail and ~12 s
headroom. Window: 600 settle + 11 × 620 + 600 + ~12 s = **8032 s < `window_max_s` 9000** (968 s spare). The drift
gate then becomes protective instead of firing by construction. Two call sites must learn pitch ≠ capture:
`execute`'s window check (`campaign.py:481`) and, unchanged and correct as written, `pilot_summary`'s covariate
filter (`monotonic_end <= scheduled + envelope_s`).

**Cure 3** is refused: it leaves an 8–10 s per-slot overrun in a harness whose pre-registration claims a 600 s
cadence, and blinds the only detector of a tail regression.

**No in-harness cure reaches 2 s; re-registration is unavoidable — and is not the expensive option.** A267 already
forces one: R4 adds two exclusion reasons (`network_time_slew_attested`, `network_time_unattested`) to the retention
rule, and `exclusions` is pre-registration text (`pilot_protocol_v1.json:19–29`). Under rules-before-data it must be
re-registered regardless; adding `slot_pitch_s` in the same registration costs ~nothing.

## Q2 — Observer load

Under cure 2 nothing moves: parse, derive, integration, hashing and `log show` all run in the 20 s gap, with the
per-envelope `powermetrics` recorder stopped and the next not yet started. No burst is ever concurrent with a
capture — strictly better than today, where the parse and derive finish 0–3 s before the next capture begins. The
covariate recorder samples the gap, but `pilot_summary` admits only rows inside `[scheduled, scheduled + envelope_s]`,
so gap rows drop out of the busy-core covariate. Relaxation before the interior: ~13 s of gap + 60 s
`interior_offset_s`, with a per-round `CPU_Speed_Limit` probe still gating.

**Do not run the attestation concurrently with a capture**, despite its trivial client cost (0.04 s user,
0.11–0.17 s sys). `log show`'s real work is done by **`logd`, a system daemon** — not a child of the chain — so its
CPU is invisible to `observer_cpu_s`, defined as "SELF + reaped CHILDREN". Concurrent execution would inject
unattributed observer energy into a measured window. That independently forbids hiding the attestation under the
next capture, and is a second argument for a real gap.

## Q3 — Output contract under cure 2

Unchanged — the point, and the largest engineering saving. The collector still writes `rounds.jsonl` and the final
`session.json` in one pass at exit; `pilot_summary` still reads those two files plus `evidence_busy_cores.jsonl`. No
staged write, no provisional-stamps sidecar, no harvest-time deriver.

The one addition is A267's attestation, written by the **chain** after `cleanup_groups` and before the next sleep:
`evidence/envelope-NN/timed-log.txt` plus a sibling `attestation.json` carrying
`{state, method, window_epoch_s, log_sha256, matched_lines}` — a sibling, never an edit to `session.json`, whose
owning collector has exited. **Window stamps come straight from the completed `session.json`**:
`power.stamps.sampling_started.epoch_s` and `sampling_stopped.epoch_s` are final at collector exit (archive envelope
02: 1790069829.861781, 1790070421.015672), so `--start`/`--end` need no staging. Missing stamps (collector crash) →
`asserted` → `network_time_unattested`. Under cure 1 this breaks: the stamps would not exist until batch
finalisation, so the ten-minute attestation would need a provisional stamps file.

## Q4 — Shaping the R6 live dry check

Drift comes from the serial tail, dominated by parsing a real 133 MB plist, which needs a real 600 s `powermetrics`
capture under sudo. Any faithful check is therefore a `[QUIET-MAC]` measurement, forbidden while an agent session is
alive. **No daytime shape is both real and admissible. Say so and arm it.**

1. **Daytime, real code, not a measurement (engineering evidence only).** Run the real chain and collector with
   `powermetrics` replaced at the existing `recorder_factory` seam by a fixture emitting an archived 133 MB plist and
   exiting on TERM: real `parse_frames`, `align_frames`, `cleanup_groups`, attestation and `Popen`, measuring the tail
   against the gap. It does **not** satisfy R6 (fake recorder; fake launchctl is `rehearsal_ready`, never `armable` —
   `docs/contracts/evidence_night_entry.md:160–166`). Do not label it as such.
2. **Night, live installer (the R6 evidence).** Arm a ~41-minute cadence night under its own registered identity
   (600 settle + 3 × 620), `DIAGNOSTIC_NO_PACK`, sole output per-envelope `start_drift_s`. Three envelopes suffice:
   the drift is a per-slot constant reproducing from envelope 02 onward (7.63–10.23 s across all eleven successors,
   zero accumulation).

**Better: make R6 cheap rather than ceremonial.** Amend R6 to accept an **in-chain early drift abort** — after
envelope 02, `start_drift_s > 2` raises, writes the refusal, ends the night at ~t0+21 min instead of ~t0+2.5 h,
turning the precondition from "spend a window to prove it" into "spend 21 minutes to disprove it" (the economics Ed
already ruled for zero-capture t0 refusals). If R6 stands as written, tier 2 is the shape; tier 1 is worth running
either way as the only thing iterable in daylight.

## Q5 — Regressions that kill the defect

Counterfactual throughout: the harness at `ecbc0fac` with a **stub collector that sleeps the capture then burns 5–7 s
before exiting** must FAIL each test; cured it must pass.

1. **Pitch/capture separation (the defect test).** Drive `execute` with the burn stub and a scaled protocol
   (`envelope_s` 6, `slot_pitch_s` 12, 4 envelopes); assert every `evidence_envelopes.jsonl` `start_drift_s` ≤
   0.02 × scale. At main (pitch ≡ capture) the stub yields 5–7 s drift → FAILS. Call site: the slot loop,
   `campaign.py:477–486`.
2. **Window arithmetic and registration binding.** `envelopes × slot_pitch_s + settle_s > window_max_s` refuses
   *before* the first spawn (counterfactual `slot_pitch_s: 750` → refusal, no collector launched; `campaign.py:481`),
   and `validate_protocol` rejects `slot_pitch_s < envelope_s` and any CLI override (`campaign.py:50–53`, already the
   fail-closed seam).
3. **Batched group census.** Journal 120 pgids with a counting subprocess runner: assert ≤ 2 `pgrep` invocations
   **and** that a genuinely live group is still reported present, so the test cannot be passed by not censusing. At
   main, 120 invocations → FAILS. Call sites `campaign.py:127–129` → `run_night.py:3413`.
4. **Attestation placement.** Assert `timed-log.txt` and `attestation.json` for envelope NN exist before envelope
   NN+1's `pre_spawn`, and that `window_epoch_s` equals `[sampling_started − 1, sampling_stopped + 1]` read from that
   envelope's `session.json`. Counterfactual: moving the call after the loop fails. Call site: `execute`, immediately
   after `cleanup_groups`.
5. **Attestation argv and failure modes.** Assert absolute `/usr/bin/log` plus both `--info` and `--debug` in the
   argv. Exhibit-D fixture → 10 matches → `slew_attested` + `network_time_slew_attested`; exit≠0 → `asserted` +
   `network_time_unattested`; both must reach `pilot_summary`'s excluded list. Counterfactual: dropping `--debug`
   gives 0 matches on the same fixture and the envelope wrongly retains.
## Q6 — What the magistrate missed

**(a) `start_drift` excluded zero envelopes on the 09-22 night.** In `evidence/summary.json` all three
drift-excluded envelopes also carry `incomplete_interior_support` (03 and 09 additionally
`clock_anchor_unresolved`) — **every one was already excluded on independent grounds.** Deleting the rule entirely
leaves retained at 2/12, pairs at 0. The refuter's BLOCKER 3 premise as written — "the exclusion removed envelopes
03, 06 and 09" (record 02 line 3) — is false as an as-observed causal claim, and record 02 and the A269 registration
repeat it. Correct it before it is cited again.

**(b) The conclusion survives with a far stronger argument — use this one instead.** The night's real losses were 7
envelopes to `clock_anchor_unresolved` (01, 03, 04, 07, 08, 09, 10) and 3 to `incomplete_interior_support` with a
*bounded* anchor and **full 480.000 s coverage on every rail**: envelopes 05, 06 and 11 failed on `span_mismatch:
true` alone — the `> 1e-6` float comparator in `integrate()` that A267's Q3(a)/R5 replaces with exact integer
equality. **All ten are A267's targets; none is A269's.** But run it forward: with A267 landed, `start_drift` becomes
the *sole surviving* exclusion class and removes 03, 06 and 09, killing pairs (3,4), (5,6) and (9,10) — 9 retained
but only **3 disjoint pairs against `minimum_adjacent_pairs: 4`**. A269 uncured turns a 12-retained/6-pair PASS into
a 9-retained/3-pair INCONCLUSIVE. That is the real justification for the p1 promotion.

**(c) The tail's second-largest term is mis-attributed.** Record 02 line 26 reads the ~2.8 s bucket as "collector
exit, `cleanup_groups` census loop over the process journal, `Popen`" without noticing the census is **113–116
separate `pgrep` spawns per envelope** and dominates it (~2.6 s) — larger than the anchor derivation. That is why
cure 1 cannot reach 2 s: line 32's "removes ~7 s per slot" is right about what it removes, silent about the ~3.3 s
it leaves.

**(d) Record 02 line 36 is right on fact, misleading on economics.** Cure 1 indeed does not touch the pre-registered
JSON (`chain_source_sha256` pins `scripts/night_chains/quiet_predicate_evidence.zsh`, verified `568a2771…`, not the
Python) — but R4 forces a re-registration anyway, so cure 2's registration cost is sunk while cure 1's engineering
cost is not.

**(e) A risk in R4 for the A267 seat.** The attestation window is derived from *epoch* stamps, yet the attestation
exists to detect a wall-clock step. If `timed` stepped the clock inside the envelope, `log show --start/--end` —
which interprets wall time — may not cover the true capture, and ±1 s is arbitrary against an unbounded step. Widen
to the union of the monotonic span mapped through both `sampling_started` and `sampling_stopped`.

**(f) Sizing note.** `start_drift_max_s: 10` nominally protects interior containment, but containment is already
proven per envelope by `interior.complete_support` (`sample_quiet_predicate_evidence.py:296–310`), and the physical
bound on drift is `interior_offset_s` = 60 s. Keep 10 s rather than re-sizing it: under cure 2 it stops firing by
construction and starts catching tail regressions. A gate that never fires because the mechanism is fixed is the
right end state; a gate widened until the broken mechanism fits under it is not.
