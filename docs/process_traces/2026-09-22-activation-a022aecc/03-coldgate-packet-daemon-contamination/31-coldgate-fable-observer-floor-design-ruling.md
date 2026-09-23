# Ruling 31 — cold gate QPE01-DAEMON-CONTAMINATION-01, round 3 (Q5, observer-floor design consult)

Cold Fable judge (claude-fable-5-1), single foreground session, 2026-09-23, worktree at `57c01b1c`. Disclosure: auto-loaded `~/.claude/CLAUDE.md`, project `CLAUDE.md`, memory index `MEMORY.md`; none used. Not opened: CLAUDE.local.md, RUN_STATE.md, TASK_QUEUE.md, memory files, council logs, run reports, other trace dirs. No subagents or background tasks.

## 0. Trust anchors (before the merits)

| item | expected | observed | method |
|---|---|---|---|
| charter | `099de884…a870ff…95d81` (out-of-packet) | `099de884b1d081ffa547dfd8ff5837e75813a870ff8c7285c749c1b440c95d81` | `shasum -a 256`; validator receipt |
| charge 30 | `d8672b37…1882` | `d8672b37e4ae516d10b92c73d2e387bda2c1dec824d604263be4a6e453881882` | same |

Run 1 (mistyped `…a880ff…`): `REFUSE`, `charter_trusted_observed_mismatch`, rc 2. Run 2 (true sha): `PASS`, rc 0, nine exhibits observed = expected.

## 1. Executed evidence (mine)

- Code at `57c01b1c` (identical to `69315e79` for campaign, evidence script, tests, protocol): `stop_branch` 936 is a bare `observer_floor > smallest_share`; `pilot_summary` 1067–1072 sums per-row `observer_cpu_s`; `whole_envelope_observer_cpu_s` is loaded at 1044 and never read. Evidence script `:713` = worker/census block; `:1164` = `cpu_total() - envelope_cpu_start`. G1 exact.
- Archives (sha `9121f080…`, `84bfcafb…`): Σ whole / round support = **0.17789** / **0.16135**; per-envelope over 600 s: mean 0.17512 / 0.16094, **sd 0.00229 / 0.00277**; over each session's monotonic span (597–607 s): mean 0.17572 / 0.15909, sd 0.00214 / 0.00267. Round-block sd 0.0002: the wander is in the recorder half. G2 reproduces.
- Rate: C8:398 +0.3194 W (medians), +1.0349 W (env 01). Corrected excess over 0.05: 19.61 / 17.07 J at 0.3194 W — ruling 21's rule stops every pilot (premise verified). Observed sd × 0.3194 × 480 = **0.35 / 0.42 J**; 0.01 cores = **1.53 J** (median), **4.97 J** (env-01).
- Charge's "recorder alone ≈ 0.11": (whole − round − recorder)/600 = 0.116 / 0.101 = collector + power recorder together; unexhibited.
- v2 protocol: `authored_after_pilot` true, `levels [0, 0.05]`, `summary[5]` says "including recorder"; no v3. Test 286 asserts `.051` → stop. Unittest 128 OK, 12.1 s.

## 2. Q5 — verdict

**AFFIRM the lead's disposition (b) in shape; REJECT its amendment (the instrument bound does not govern); rule (b) as corrected below, with the arm-symmetry check made a registered block-two field.**

Why (b). Energy per arm = machine + observer + (load arm) level. A constant observer is in both arms and cancels in the difference; its size shifts the baseline, a stated condition of the measurement, not an error in the contrast. What does not cancel: (1) envelope-to-envelope wander (spread), testable by the pilot; (2) a systematic arm difference (bias), testable only by block two. (a) stops on baseline size at any rate (§1): foregone, REJECT. (c) stops on a quantity that cancels, keyed to a placeholder of an unauthored block (`authored_after_pilot` true; "holdable" undefined in 10a/46b): REJECT. (d) deletes a guard with a physical target and 4× margin on real data: REJECT.

Which bound governs. The level bound (0.2 × 0.05 = 0.01 cores) governs, in cores: the confound is relative to the manipulated variable, and a 0.01-core wander is a 20 % perturbation of the level whatever the watts. The instrument bound is a floor no bar may go beneath: 1 J ÷ (0.3194 W × 480 s) = 0.0065 cores. Rule: `bar = max(0.2 × smallest level, 0.0065)` = 0.01; not microscopic (1.53 J median, 4.97 J env-01). Observed sd = 0.35–0.42 J, below the ≈ 1 J attribution limit: both nights pass for a physical reason. No rate constant enters the rule; rates live in basis text only.

**Registration v3 field text (exact):**
```
"observer_floor": {
  "statistic": "per envelope: session.whole_envelope_observer_cpu_s / (end_stamp.monotonic_before_s - start_stamp.monotonic_before_s); campaign value = sum of whole_envelope_observer_cpu_s over all readable envelopes / sum of their spans",
  "definition": "SELF + all reaped CHILDREN, including collector, power recorder, load recorder and census; never subtracted",
  "supersedes": "v2 observer_floor_cores summed per-round observer_cpu_s (worker/census block only) and omitted the power recorder; v2 reported 0.0531 (20260922-0217) and 0.0528 (20260922-2100); corrected whole-envelope values 0.178 and 0.161 cores",
  "role": "REPORTED in every pilot summary; input to block two's authoring as the baseline the level sits on; never a stop, never subtracted, never a retention input",
  "limitation_sentence": "Block two measures the marginal energy of the level on top of this observer, not on an idle machine."
},
"observer_variation": {
  "statistic": "sample SD over all readable envelopes of the per-envelope observer_floor share, df = n - 1, cores",
  "bar_cores": 0.01,
  "bar_basis": "max(0.2 * block_two.levels[1], 0.0065): 0.2 x 0.05 = 0.01 cores is one fifth of the smallest level; 0.0065 cores is the 1 J attribution limit / (0.3194 W x 480 s) at C8's median rate; 0.01 cores = 1.53 J at that rate, 4.97 J at C8's envelope-01 rate 1.0349 W; observed 0.0023 / 0.0028 cores on 20260922-0217 / -2100",
  "minimum_envelopes": 2,
  "absent": "an envelope session without whole_envelope_observer_cpu_s, or fewer than 2 readable envelopes, is a summary refusal, never a pass"
},
"block_two_required_fields": {
  "observer_arm_symmetry": "|mean per-envelope observer share, load arms - idle arms| <= observer_variation.bar_cores (same statistic); above -> 'no cutoff qualifies'; block two may not register without this field"
},
"stop_branches": {"observer_variation_above_level_tolerance": "no cutoff qualifies",
                  "block_two_upper_bound_above_1_J": "no cutoff qualifies",
                  "sized_pairs_above_24": "no cutoff qualifies"}
```
`observer_floor_above_smallest_holdable_share` leaves `stop_branches`; `smallest_holdable_share` stays as the level, no longer an operand.

**Replacement for `stop_branch` (exact; `observer_floor` leaves the signature):**
```python
def stop_branch(*, s_upper=None, observer_variation=None, block_two_upper_j=None, protocol=None):
    """Apply only ruled stop conditions; absent evidence is never a pass."""
    protocol = frozen_protocol() if protocol is None else protocol
    for value in (s_upper, observer_variation, block_two_upper_j):
        if value is not None and (type(value) not in (int, float) or not math.isfinite(value) or value < 0):
            raise ValueError("stop-branch evidence must be finite and nonnegative")
    causes = []
    pairs = None if s_upper is None else size_block_two(s_upper, protocol)
    if pairs is not None and pairs > protocol["sizing"]["maximum_pairs"]:
        causes.append("sized_pairs_above_24")
    if observer_variation is None:
        raise ValueError("observer variation absent: whole-envelope observer accounting missing; absent evidence is never a pass")
    if observer_variation > protocol["observer_variation"]["bar_cores"]:
        causes.append("observer_variation_above_level_tolerance")
    if block_two_upper_j is not None and block_two_upper_j > protocol["sizing"]["delta_j"]:
        causes.append("block_two_upper_bound_above_1_J")
    return {"outcome": protocol["stop_branches"][causes[0]] if causes else "no decision", "causes": causes, "pairs": pairs}
```
**Replacement for the derivation, 1065–1073 (exact):**
```python
    # Whole-envelope observer cost, all envelopes; REPORTED; never subtracted.
    shares = []
    for v in values:
        if v.get("error") is not None:
            continue  # unreadable session, already excluded
        span = v.get("envelope_span_s")
        if harness.number(v.get("whole_envelope_observer_cpu_s")) is None or harness.number(span) is None or span <= 0:
            raise ValueError(f"envelope {v['index']}: whole_envelope_observer_cpu_s or span missing; absent evidence is never a pass")
        shares.append(v["whole_envelope_observer_cpu_s"] / span)
    observer_support_s = sum(v["envelope_span_s"] for v in values if v.get("error") is None)
    observer_floor = sum(v["whole_envelope_observer_cpu_s"] for v in values if v.get("error") is None) / observer_support_s if observer_support_s else None
    observer_variation = statistics.stdev(shares) if len(shares) >= 2 else None
    stop = stop_branch(s_upper=s_upper, observer_variation=observer_variation, protocol=protocol)
```
plus at 1044 `"envelope_span_s": session["end_stamp"]["monotonic_before_s"] - session["start_stamp"]["monotonic_before_s"]`; the report gains `"observer_variation_cores"`, `"observer_floor_role": "reported; input to block two authoring"`, and the v3 `observer_definition` string. `observer_floor_cores` keeps its name (comparable under the supersession note).

**Abort count:** unchanged (round 1's two consecutive exclusions). Variation is a harvest-time campaign statistic: no in-night abort, no t0 predicate.

**Regressions (each must FAIL at `57c01b1c`; site `pilot_summary` → `stop_branch`):**
- (i) Both archives re-derived → `observer_floor_cores` 0.1757 ± 0.002 / 0.1591 ± 0.002, `observer_variation_cores` 0.0021 ± 0.0005 / 0.0027 ± 0.0005, observer causes ABSENT. Fails today: 0.0531 / 0.0528, cause present. Counterfactual: the twelve `whole_envelope_observer_cpu_s` values (totals 1260.87 / 1158.76 s).
- (ii) Twelve synthetic sessions, shares 0.16 ± alternating 0.02 (sd 0.0209) → `observer_variation_above_level_tolerance` PRESENT. Fails today (cause unknown). Counterfactual: sd 0.009 → ABSENT.
- (iii) One readable session lacking `whole_envelope_observer_cpu_s` → `ValueError` (text above); `stop_branch(observer_variation=None)` → `ValueError`. Fails today (silent; None → "no decision").
- (iv) `stop_branch(observer_floor=0.9)` → `TypeError`. Fails today.
- (v) `joules`, `pair_sd_j`, `s_upper` byte-equal to the archives. Passes today; a guard, labelled not defect-shaped.
- (vi) Test 285 `stop_branch()` → `assertRaises(ValueError)`; 286 `{"observer_floor": .051}` → `{"observer_variation": .011}`, add `.01` → "no decision"; 113–115, 263–265 moved to the variation key.
- Arm symmetry: no regression writable at `57c01b1c` (block two has no code); binds at block two's registration gate. NOT EXECUTED by design.

**Archived summaries:** AFFIRM — dated addendum only, never rewritten. Text: "Addendum (2026-09-23, cold gate round 3, ruling 31): `observer_floor_cores` 0.0531 [0.0528] used the v2 statistic (per-round worker block) and omits the power recorder; under v3 (whole envelope over span) the floor is 0.176 [0.159] cores, envelope sd 0.0021 [0.0027]. The v2 stop cause stands as issued; superseded, not reversed."

## 3. Findings

- **MATERIAL** — the lead's amendment inverts the governing bound: an instrument-sized bar ties the rule to a daemon-derived rate (round 2's defect again); cured by `max(level bound, instrument floor)`, rates in basis text only.
- **MATERIAL** — arm symmetry is real and untestable by the pilot; implicit, block two could register without it. Cured as a required field.
- **MATERIAL** — refuter 22 divides by round support (≈ 590 s), G by 600 s nominal; neither is the accounting window of `whole_envelope_observer_cpu_s`. Ruled: the session's monotonic span.
- **NIT** — "≈ 0.11 cores, recorder alone" is collector + recorder (0.10–0.12), unexhibited.
- **NIT** — "3.2–3.6 ×" in the charge is 3.05–3.35 × on the same-support floors.

## 4. Packet hygiene

Neutral in substance: four options, the refuter's contrary finding carried as verified evidence, both seats unedited, numbers reproducible. Defects: Q5 compound (option + bound + assumption), separately ruled; one unlabelled derived figure (0.11); two unlabelled denominators (G2). Effect: none on the option, material on the statistic's exact text, cured.

## 5. Probes

No `systemsetup`/`sudo`/`powermetrics`/`launchctl`; `/usr/bin/log` not needed; reads: packet dir, harvest record, two archive roots, `git show`; one unittest run; one file written.
