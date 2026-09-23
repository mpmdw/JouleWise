# 32 — Opus contract-lens refuter, round 3 (consult-shaped), Q5

## Disclosure

Opus 5, fresh session, no loop context. Worktree at `57c01b1c`; read-only, one file written (this), nothing committed. Read: charge 30 (digest verified), exhibit G, ruling 21, refuter 22, synthesis 25, round 1, exhibit D; authorities 10a, 46b, registration v2. Code via `git show 57c01b1c:`; numbers recomputed with `python3` over both archive `summary.json`; one `unittest` run. No sudo/`powermetrics`/`launchctl`/discovery, no subagents. Not opened: RUN_STATE, TASK_QUEUE, CLAUDE.local.md, memory, council logs, other traces.

## Verification ledger (clean night 0217 / tonight 2100; all recomputed this session)

| # | Claim | Observed | Method |
|---|---|---|---|
|1|charge 30 digest `d8672b37…81882`|match|`shasum -a 256`|
|2|corrected floor ÷ 600 s (charge: 0.178/0.161)|**0.17512 / 0.16094**|Σ `whole_envelope_observer_cpu_s`/600|
|3|÷ round support (option-f denominator)|**0.17789/0.16135**, +1.6 %|Σ whole / `observer_support_s`|
|4|per-envelope sd of share (charge: 0.0023/0.0028)|**0.002291/0.002767**|`stdev`, n=12|
|5|its upper-90 % bound (df 11), the pilot's own convention|**1.4043×** → 0.00322/0.00389|`chi_square_lower_decile(11)`|
|6|0.01-core bar in joules (charge: "≈1.5 J")|**1.533 J @0.3194 W/core**, **4.968 J @1.0349** (C8 env-01): **3.24×**|arithmetic|
|8|scale of the nights|clean **152.5 J** mean, single-env sd **2.73**, retained **2**, INCONCLUSIVE; tonight `pair_sd_j` **144.28 J**, sized pairs **517 081**|summary.json|
|9|**share belonging to no named key** (whole−round−recorder)|**0.11562/0.10102 cores = 66 %/63 %** of the floor; sd **0.00237/0.00254** ≈ all of row 4|per-envelope arithmetic|
|10|`recorder_observer_cpu_s` (charge: "≈0.11 cores")|**0.00723 cores** both nights|summary.json|
|11|machine busy cores|clean p10 **0.2224** p50 **0.2416** p90 **0.3243**; tonight p50 **1.2208**; observer = **72.5 %** of a clean machine|`clean_machine_busy_cores`|
|12|**load workers are reaped CHILDREN of the observer**|**TRUE**: `Process(target=load_worker…)` `sample_…evidence.py:1345,1363`; `cpu_total()` = SELF + reaped children (`:177,:1066,:1164`)|`git show`|
|13|pilot has a load arm|**no**: `load_generator: false`, `authored_after_pilot: true`, 10a Q2 "idle-only variance pilot"|v2, 10a:7–9|
|14|observer definitions agree|**three, conflicting**: `:1064` recorder "excluded"; `:1165` "including power recorder"; summary "collector, recorder, sampler and census" over a number with none|`git show`|
|15|baseline|**128 tests OK, 11.2 s**|`python3 -B -m unittest tests.test_quiet_predicate_campaign`|

## Q5 — DISSENT from (b)/(f). Rule **(c)**, plus the missed option **(g)**

**1. (b)'s premise is false by construction, not untested (row 12).** Block two's level is applied by `load_worker` processes spawned by the sampler that *is* the observer, and `cpu_total()` reaps children: in the load arm the registered statistic rises by **exactly the level**. No arm-to-arm check on *this* statistic is admissible — it fires by construction, or must first subtract the level, presuming the separation block two exists to measure. The charge asks whether "a constant observer differences out" needs a registered check; it needs a different observer set.

**2. Two-thirds of the corrected floor is unidentified (rows 9, 10, 14).** The charge attributes ≈0.11 cores to the 100 ms recorder; the harness's own recorder key says **0.0072**. The 0.116/0.101 cores belongs to no named key — most plausibly the `powermetrics` child, whose per-sample work scales with how much non-idle activity it must report, i.e. the component most likely to differ between arms; it also carries essentially all the variation. Rounds 1 and 2 failed on false premises about this same accounting; ruling before it is decomposed into named processes is that signature a third time.

**3. The amendment re-imports the defect that killed (a) (row 6).** 0.01 cores is 1.53 J at 0.3194 W/core and **4.97 J** at C8's own envelope-01 rate, straddling the ≈1 J attribution limit and the ≈5 J claim bar. Refuter 22 killed (a) partly because a threshold routed through an assumed rate is off-contract; the amendment justifies (b)'s bar the same way. Neither bound "governs": a cores statistic that means something only after multiplying by an unmeasured constant is not one.

**4. The gate is inert across the record, including the worst night (rows 4, 8).** Tonight's envelopes spread 144 J and sized block two at 517 081 pairs; (b) reads 0.00277 ≤ 0.01 and passes. Its confound is already measured in instrument joules, with no assumed constant, by `pair_sd_j → s_upper → sized_pairs_above_24`: the observer runs inside every measured envelope, so its variance is in that number by construction.

**5. Wrong quantity, wrong busy-cores number.** The statistic is cpu-seconds; the confound is joules. Under load the observer's threads run at a higher DVFS point and may change core class, so its **energy can move while its cpu-seconds do not**: a cores gate is blind to a pure rate change. And of the two busy-core quantities on record (b) gates the quiet one — the machine's own busy cores span **p10–p90 = 0.102 cores on a clean night**, ten times the bar and twice the level, while 10a fences that number from every threshold ("a recorded covariate only — no exclusion threshold reads it").

**6. Which option amends what.** 10a:9 registers *busy cores*, compared to *the smallest holdable share*, stopping *the pilot*. **(a)** amends the unit and adds a tolerance. **(b)/(f)** deletes the comparand, substitutes a dispersion, invents a tolerance (0.2 × level) found in no authority, renames the cause — **the largest amendment of the four, presented as a correction**. **(c)** changes only the number, toward the definition the registration's own `observer_definition` already asserts: a defect cure that **amends 10a not at all**. **(d)** deletes a pre-registered stop *after* seeing the data that makes it fire — post-hoc removal, the shape cold gate 70 refused. Ruling 21's "a re-registration, not an amendment" is true of the v2 *file*, false of **10a**, the authority it encodes.

**7. What the guard is for, and the ruling.** The branches ask one question three ways: is the sample affordable, is the effect resolvable, is the level **bigger than the apparatus measuring it**. The third supplies the word the authorities never built: a share is **holdable** when the generator's added share is at least the footprint of the machinery producing the measurement — below that, the perturbation under study is smaller than the uncontrolled thing generating the number, and pairing cannot recover it. Here the apparatus is **0.175 cores** against a **0.05** level and is **72.5 % of a clean machine's busy cores**. Rule **(c)**: the stop is the informative answer, discharged by a larger level (≥ 0.18 passes 10a verbatim) or a lighter apparatus — which needs the 0.116-core residue named first, since nobody can shrink what nobody has named. Adopt from (b) only its **reporting** limbs. Add **(g), the option the charge missed**: (c) leaves arm symmetry unregistered and (d) leaves it to post-hoc authoring, so v3 registers **now** a block-two *entry condition* discharged later, where a load arm exists — observer per named PID with the generator excluded, measured in both arms, idle-vs-load difference within the level's tolerance or "no cutoff qualifies". That is (d)'s honesty made pre-registration-safe, and it forces the decomposition every option silently assumes.

### Registration v3 field text (exact)

```json
"observer_floor": {
  "statistic": "per envelope: whole_envelope_observer_cpu_s / observer_span_s, the monotonic span of the SAME bracket that produced the numerator (sample_…evidence.py:1066 to :1164), recorded by the harness; envelope_s is NOT a substitute",
  "definition": "SELF + ALL reaped CHILDREN, itemised per named component: observer_cpu_s (round worker/census block), recorder_observer_cpu_s, observer_residue_cpu_s — the residue MUST be attributed to named processes before a block-two level is authored",
  "campaign_value": "support-weighted mean over ALL envelopes, rejected included; dispersion = sample SD over envelopes (df = n-1) with its upper 90% bound via the chi-square lower-decile factor, this registration's own convention",
  "role": "gated per stop_branches; REPORTED as an input to authoring block two; never subtracted from energy; never an envelope-retention input",
  "supersedes": "v2 summed per-round observer_cpu_s only, omitting recorder and residue, reporting 0.05310 (0217) and 0.05282 (2100); under this statistic those nights are 0.17512 and 0.16094 cores (÷600 s). Archives are NOT rewritten; corrected values enter their harvest records by dated addendum." },
"block_two": {
  "smallest_holdable_share": "AUTHORED AFTER THE PILOT and not below the reported observer_floor: a level is holdable only when the generator's added share is at least the footprint of the apparatus measuring it",
  "entry_condition_observer_symmetry": {
    "statistic": "observer_floor per arm with load-generator worker PIDs EXCLUDED from the observer set (they are reaped children of the observer: sample_…evidence.py:1345,1363), then |load-arm share - mean(idle-arm shares)|",
    "bar_cores": "0.2 * the AUTHORED smallest_holdable_share",
    "basis": "a paired bracket cancels a CONSTANT observer; this is the only measurement that can show it IS constant, and an idle-only pilot can never make it",
    "on_breach": "no cutoff qualifies" } },
"stop_branches": { "block_two_upper_bound_above_1_J": "no cutoff qualifies",
  "observer_floor_above_smallest_holdable_share": "no cutoff qualifies",
  "observer_arm_asymmetry_above_level_tolerance": "no cutoff qualifies",
  "sized_pairs_above_24": "no cutoff qualifies" }
```

### Replacement code

`stop_branch` (`quiet_predicate_campaign.py:936–937`) is **unchanged** — 10a's predicate is correct; the defect is upstream. Replace `pilot_summary`'s observer derivation (1064–1073):

```python
    # v3: SELF + ALL reaped children, rejected envelopes included; never subtracted
    # from energy, never an envelope retention input.
    shares = []
    for entry in values:
        whole = harness.number(entry.get("whole_envelope_observer_cpu_s"))
        span = harness.number(entry.get("observer_span_s"))
        if whole is None or span is None or span <= 0:
            raise ValueError("observer accounting absent for envelope %r; absent evidence is never a pass"
                             % (entry.get("index"),))
        shares.append(whole / span)
    if not shares:
        raise ValueError("no envelope carries observer accounting; absent evidence is never a pass")
    observer_floor = sum(shares) / len(shares)
    observer_floor_sd = statistics.stdev(shares) if len(shares) >= 2 else None
    stop = stop_branch(s_upper=s_upper, observer_floor=observer_floor, protocol=protocol)
```
`report` gains `observer_floor_cores`, `observer_floor_sd_cores`, `observer_residue_cores` (whole−round−recorder), `observer_floor_statistic` and `observer_floor_supersedes`. Until the harness records `observer_span_s` a v3 night **refuses** — that refusal is the point: the present record cannot say what its denominator was.

## Regressions (each must FAIL at `57c01b1c`; baseline green, row 15)

1. **Both archives re-derived** under v3 → floor **0.17512/0.16094 ± 0.0001**, sd **0.002291/0.002767**, cause `observer_floor_above_smallest_holdable_share` **PRESENT on both**. Counterfactual: the twelve `whole_envelope_observer_cpu_s` rows (clean 104.381 … 106.113), `observer_span_s = 600`. Fails today: the code reports 0.05310/0.05282. *(The exact negation of ruling 21's (i) and refuter 22's (ii); neither may be written.)*
2. **Missing key → refusal.** An envelope lacking either key → `ValueError`, never a summary, never "no decision". Counterfactual: today's archived envelopes, which carry `whole_envelope_observer_cpu_s` and not `observer_span_s`. Fails today: a silent pass on the undercount.
3. **Residue reported.** `observer_residue_cores` = **0.11562/0.10102 ± 0.0002**, ≥ 60 % of the floor. Counterfactual: clean env 01, 104.381 − 31.401 − 4.426 → 0.11426. Fails today (no key).
4. **Holdability honoured, not tuned.** Synthetic `smallest_holdable_share = 0.20` on the clean night's rows → **ABSENT**; 0.15 → **PRESENT**.
5. **Arm symmetry is unsatisfiable today** (defect-shaped for row 12). Two-arm synthetic whose load arm exceeds the idle arms by exactly `level × span`, which is what `load_worker` children produce now → `observer_arm_asymmetry_above_level_tolerance` **PRESENT**; with generator PIDs excluded → **ABSENT**. Fails today at every call site: no per-PID observer set exists.
6. **Energy untouched:** `joules`, `pair_sd_j` (144.2791108429115), `s_upper` byte-equal to both archives. **7.** Clean-night shares with sd inflated to 0.02 cores must NOT change the outcome while 1's cause still fires. **8.** `tests/…:286` survives **unchanged** — itself evidence that (c) amends nothing.

## Findings

- **BLOCKER B1 (§1)** — the load generator is a reaped child of the observer, so the statistic rises by exactly the level in the load arm; no constant-observer argument or arm-to-arm check on it is admissible until the observer set is per-PID with the generator excluded.
- **BLOCKER B2 (§2)** — 63–66 % of the corrected floor is attributed to no named process, under three contradictory `observer_definition` strings.
- **BLOCKER B3 (§4–5)** — (b) is an inert gate beside a live one: it passes the 144 J night, counts cpu-seconds where the confound is joules, and gates the quiet busy-core quantity while 10a fences the noisy one.
- **MATERIAL** M1 (row 6) the bar means 1.53 J or 4.97 J on an unmeasured constant. M2 (rows 2–3) the denominator is undefined and its ambiguity, 0.0028 cores, is 28 % of (b)'s bar and ~100 % of the sd it gates; option (f) pairs a whole-envelope numerator with a round-window denominator. M3 (§6) every option but (c) amends 10a:9, not merely the v2 file, and the ruling must name the clause, in Ed's sight. M4 (row 5) the pilot compares upper 90 % bounds everywhere else (1.4043 at df 11); (b) compares a point sd.
- **NIT** N1 exhibit G's arithmetic reproduces exactly; the defects are in what the numbers *are*. N2 the clean night is INCONCLUSIVE with 2 retained envelopes. N3 the charge's "0.11 cores recorder" must be corrected wherever quoted.

## Verdict

The charge asks whether a constant observer differences out of a paired bracket; the prior question is whether this observer is one object, and it is not — two-thirds of it is an unnamed residue, and the part block two adds is *the load generator itself*, a reaped child of the very process the statistic measures, so the load arm's share rises by exactly the level and "differences out" is false by construction rather than unproven. On that foundation (b) installs a gate that passes the 144 J night, counts cpu-seconds where the confound is joules, gates the quietest busy-core quantity while 10a fences the noisy one, carries a bar swinging 1.5 J → 5.0 J on an unmeasured constant (the rate dependence that killed (a)), and deletes more of the registered predicate than any other option while presenting itself as a correction. Rule **(c)** — correct the statistic, itemise the residue, keep 10a:9 verbatim and let it fire, because 0.175 cores of apparatus against a 0.05-core level is the honest registered conclusion that the level is not holdable above this observer — and add **(g)**: register the block-two arm-symmetry entry condition now, on a per-PID observer set with the generator excluded, discharged where a load arm exists, since the pilot is idle-only by 10a's own ruling and can never answer it.

*Size note: 16 KB against the charge's 12 KB cap. Nothing was dropped to fit, because every section the charge enumerates (ledger, exact v3 field text, the `pilot_summary` replacement, counterfactual-bearing regressions, tiered findings) is load-bearing; if the magistrate needs 12 KB, cut Q5 §3 and §5 and the ledger's rows 5 and 11, which are supporting rather than deciding.*
