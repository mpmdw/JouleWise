# 22 — Opus contract-lens refuter, bounded round 2 (Q4, observer-floor stop branch)

## Disclosure

Opus 5, fresh session, no loop context. Read-only except this file; nothing committed. Read: charge 20 (sha256 verified `fbf4b9b9…1210cb`), exhibit D, exhibit C §C8/C9, round 1 (`10`,`11`,`15`) for context only; authorities `…d0b83820/10a`, `46b`. Code via `git show 258c90ed:`. No sudo/`powermetrics`/`launchctl`/discovery; one unittest run; no subagents.

## Verification ledger

| # | Claim | Expected | Observed | Method |
|---|---|---|---|---|
|1–2|Charge digest; D3 floors|`fbf4b9b9…1210cb`; 0.053098 / 0.052823|both match|`shasum`; `summary.json`|
|4|`0.3125 W` is "exhibit C8"|present|**ABSENT.** C8 has 0.3194, 0.3110, **1.0349** (env 01); 0.3125 = ruling 10's 150 J/480 s rounding|grep; C8:396–400|
|5|Same excess at C8's env-01 rate (1.0349 W)|—|**1.539 / 1.402 J — above 1 J**|python|
|6|Floor includes the power sampler, per registered `observer_definition`|yes|**NO.** Floor sums round `observer_cpu_s` (`sample_…evidence.py:713`, worker/census block only); the sampler sits in `whole_envelope_observer_cpu_s` (`:1164`), unread|`campaign.py:1067-72`|
|7|Floor under the registered definition|—|**0.177885 / 0.161350 cores (3.35× / 3.05×)**|Σ over both archives|
|8|(a)'s excess on the corrected floor|< 1 J|**19.18 / 16.70 J** at 0.3125 W; 63.5 / 55.3 J at 1.0349 W|python|
|9|"W_per_core … the pilot records it"|a field|**FALSE.** No watt/per-core key among 37 summary keys|key scan|
|10|Observer stability, corrected floor|—|per-envelope sd **0.002328 / 0.002774** cores; range 0.1746–0.1812 / 0.1578–0.1689|python|
|11|`smallest_holdable_share` defined in authorities|a definition|**none.** 10a says only "the observer floor's own busy cores exceed the smallest holdable share"; 46b: no match|grep|
|12|`block_two.authored_after_pilot`|—|`true`; `levels [0, 0.05]`|protocol v2|
|13|Baseline at 258c90ed|green|128 tests OK, 11.2 s|`python3 -B -m unittest`|

## Q4 — DISSENT from (a)

**1. The quantity (a) would excuse is wrong by 3.05–3.35× (ledger 6–8).** `observer_floor` sums per-round `observer_cpu_s`, measured only across the round's worker/census block. The 100 ms power sampler runs for the whole envelope and lands in `whole_envelope_observer_cpu_s`, which the floor never reads — yet the summary's own `observer_definition` claims "including collector, recorder, sampler and census", as does exhibit D's D4. The true floor is 0.178 / 0.161 cores and the excess is worth **19.2 / 16.7 J** at (a)'s own rate, so **(a)'s regression (i) pins a wrong answer**: "cause ABSENT" needs the undercount.

**2. A floor rate used to prove smallness (ledger 4–5).** 0.3125 W/core is not in C8; it is ruling 10's rounding of C8's whole-machine night-to-night delta, labelled there "an efficiency-core rate, **so a floor**". (a) reverses that direction, using a deliberate under-estimate to argue immateriality. At C8's env-01 rate the excess is 1.40–1.54 J, **above** 1 J: (a) flips on a rate choice inside one exhibit.

**3. The joule shape is off-contract.** 10a registers a busy-core comparison — "the observer floor's own busy cores exceed the smallest holdable share". (a) turns a level predicate into an energy one and borrows δ from two different quantities: block two's 1 J is a tolerance on a *paired contrast between two measured states*, and the ≈ 1 J attribution limit governs attributing *measured* energy to a workload. The observer excess is neither — cores × an assumed rate — and a measurement tolerance around a modelled number is a second defect, not a cure. A night-measured `W_per_core` could only come from regressing rail energy on `busy_cores`, which 10a fences as "a recorded covariate only — **no exclusion threshold reads it**" (both seats, after cold gate 70 refused a post-hoc cutoff). And "the pilot records it" is false (ledger 9): every night falls back to the constant, so regression (iii) can never fire.

**4. What the floor confounds, and the missed option.** Block two is a *paired* idle-load-idle bracket: a constant observer sits in both arms and differences out, raising the baseline, not the contrast. What can defeat the contrast is whether the generator can hold a +0.05-core increment on top of that baseline, and the observer's **arm-to-arm variation** relative to the level. Neither is a joule. Further, `authored_after_pilot = true` (ledger 12) and "holdable" is undefined in both authorities (ledger 11): `smallest_holdable_share = 0.05` is a placeholder in a block that does not exist yet, so **the pilot is refused by an unauthored block's placeholder** — the by-construction stop. The repair: make the floor an *input to authoring block two*, and gate only on what the pilot can invalidate — whether the observer is stable enough to difference out. It is (ledger 10): sd 0.0023 / 0.0028 cores, 4.7–5.5 % of the level, passing on both nights *even with the corrected, 3× larger floor*, for a physical reason rather than a tolerance.

**Option (f) — correct the statistic, report the level, gate the variation. v3 field text:**

```
"observer_floor": {
  "statistic": "per envelope: whole_envelope_observer_cpu_s / (sum over that envelope's rows of round_mono_end_s - round_mono_start_s)",
  "definition": "SELF + ALL reaped CHILDREN, including the power recorder; supersedes the v2 statistic, which summed per-round observer_cpu_s and omitted the sampler",
  "campaign_value": "support-weighted mean over envelopes",
  "role": "REPORTED with every pilot summary and carried into the authoring of block two; never subtracted from energy, never an envelope-retention input", "gate": false },
"observer_variation": {
  "statistic": "sample SD over envelopes of observer_floor (cores), df = n - 1",
  "bar_cores_value": 0.01,
  "bar_basis": "0.2 * block_two.smallest_holdable_share — the level's OWN tolerance: a paired bracket differences out a constant observer, so the confound is envelope-to-envelope variation, not the absolute share; cores, never joules" },
"stop_branches": { "observer_variation_above_level_tolerance": "no cutoff qualifies",
                   "block_two_upper_bound_above_1_J": "no cutoff qualifies",
                   "sized_pairs_above_24": "no cutoff qualifies" }
```

Replacement for `stop_branch` 936–937 (`observer_floor` leaves the signature; `observer_variation` takes its place):

```python
    if observer_variation is None:
        raise ValueError("observer variation absent; absent evidence is never a pass")
    if observer_variation > protocol["observer_variation"]["bar_cores_value"]:
        causes.append("observer_variation_above_level_tolerance")
```

**Regressions (each must FAIL at `258c90ed`; baseline green):** (i) Re-derive both archives: `observer_floor_cores` = **0.177885** / **0.161350**, not 0.0531/0.0528 — lands first; (a)'s regression (i) is its exact negation and must not be written. (ii) `observer_variation` = 0.002328 / 0.002774 ≤ 0.01 → cause ABSENT on both nights. (iii) Synthetic series with floor sd 0.02 cores → cause PRESENT. (iv) `observer_variation=None` → `ValueError`, never "no decision". (v) The corrected floor appears while `joules` and `pair_sd_j` stay byte-equal to the archives. (vi) `stop_branch(observer_floor=0.9)` raises `TypeError`.

**One registration or two.** One v3 re-registration, but not one undifferentiated digest: correcting `observer_floor` changes a number already published in two archived summaries, so v3 carries a supersession note naming the v2 statistic and both corrected values, and both archives are re-derived as a dated addendum (archives not rewritten). Round 1's Q2 arithmetic survives — it uses the floor rate conservatively.

## Findings

*If (a) is ruled anyway:* fix the floor statistic regardless (nothing can be ruled on a 3× wrong input); record `0.3125 W` as a floor rate, forbidding its use to show immateriality; make regression (iii) reachable. (c) is separately refuted by ledger 6 — changing the sampler interval cannot move a floor that never counted the sampler.

**BLOCKER B1.** `observer_floor` omits the power recorder the registered definition names; true floor 0.178 / 0.161 cores (3.05–3.35×). Every size-dependent conclusion in the charge is void.
**BLOCKER B2.** (a)'s regression (i) pins "cause ABSENT" from that undercount; on the corrected floor the excess is 16.7–19.2 J at (a)'s own rate, so (a) hides a miscount rather than relieving it.
**BLOCKER B3.** Shape: 10a registers a busy-core comparison, the paired-bracket confound is variation not level or joules, and (a)'s rate routes a stop threshold through the covariate 10a fenced from thresholds.
**MATERIAL M1.** `0.3125 W per busy core` is mis-cited to C8 and knowingly a floor rate; at C8's env-01 rate (a) fails its own test (1.40–1.54 J).
**MATERIAL M2.** "the pilot records it" (W_per_core) is false: no field, no mechanism.
**MATERIAL M3.** `smallest_holdable_share` is undefined in both authorities and `authored_after_pilot = true`: the pilot is gated on an unauthored block's placeholder.
**NIT N1.** The charge's multiplications reproduce exactly — the error is in the inputs and the direction of use; ruling 10's `bar_basis` should carry the floor-rate caveat so the constant is not re-borrowed dismissively.

## Verdict

The charge asks whether a 0.45 J gate is too fine for a ≈ 1 J instrument; the prior question is whether the 0.003-core excess is real, and it is not — the registered floor omits the power sampler its own definition string claims to include, so the honest floor is 0.16–0.19 cores, three times the smallest level and worth 17–19 J at the charge's own rate. (a) would write a tolerance around a miscount and byte-pin the wrong answer. Beneath that the shape is wrong: a constant observer differences out of a paired bracket, so what defeats the contrast is its envelope-to-envelope variation against the level — 0.0023 / 0.0028 cores, inside one fifth of the level even after the floor is corrected. Rule (f): fix the statistic, report the floor as an input to authoring block two rather than a gate upon it, and stop only on variation, in cores.
