# Charge 30 — round 3 of cold gate QPE01-DAEMON-CONTAMINATION-01, consult-shaped: what the observer-floor stop branch is FOR, what it must measure, and what rule follows (rule 11 triggers: a registered stop rule; two consecutive rounds failed on the same signature, so this round is a design consult, not a third fix)

Assembled 2026-09-23 00:40 PDT by the resident magistrate (activation a022aecc). Rounds 1 and 2 are sealed (synthesis 15, synthesis 25). Exhibit G is executed evidence; ruling 21 and refuter 22 are the two seats' arguments and are exhibits here, not authorities.

Terms in plain words. *Block two* is the experiment the pilot serves: a paired "idle-load-idle bracket" that applies a small, held CPU load (a *level*, the smallest registered being 0.05 cores) between idle envelopes and measures the energy difference. The *observer* is the night's own machinery — collector, the 100 ms power recorder, the 30 s load recorder, census — whose CPU is present in every envelope and is never subtracted. The *observer floor* is that cost as a share of one core. The registered *stop branch* says: if the observer's own busy cores exceed the smallest holdable share, "no cutoff qualifies".

## What is now established (exhibit G, verified at the bench)

- The number the stop branch reads (`observer_floor_cores` 0.053) counts only the round's worker block. The whole-envelope accounting, which the registration's own `observer_definition` describes, is 0.178 (clean night) and 0.161 (tonight) cores: the observer is 3.2–3.6 × the 0.05 level.
- Across envelopes the whole-envelope observer share varies by sd 0.0023 (clean) / 0.0028 (tonight) cores — 4.7–5.5 % of the 0.05 level.
- "Holdable" is named in 10a and the registration but defined in neither; `block_two.authored_after_pilot` is true.
- Round 2's tolerance rule (ruling 21) was computed on the under-reported floor; on the corrected floor its excess is 16.7–19.2 J at the median rate, so it stops every pilot too.

## Q5 — What is the observer-floor guard protecting, and what rule should registration v3 carry?

Options. (a) Ruling 21's joule tolerance, recomputed on the corrected floor — fires on every pilot (exhibit G); adopting it means the pilot cannot proceed until the observer is made lighter than 0.05 cores, which the 100 ms power recorder alone (≈ 0.11 cores) forbids. (b) Refuter 22's option (f): correct the statistic to whole-envelope accounting; REPORT the floor as an input to authoring block two; GATE only on the observer's arm-to-arm variation — sd over envelopes of the per-envelope whole-envelope share — against the level's own tolerance (0.2 × smallest_holdable_share = 0.01 cores); rationale: a constant observer sits in both arms of a paired bracket and differences out, only its variation confounds. (c) Correct the statistic and keep the level comparison as registered (floor > 0.05 → stop): the honest registered conclusion is then that block two at a 0.05-core level is not holdable above this observer, and block two is re-designed (larger levels, or a lighter observer) before any pilot re-run. (d) Defer the whole stop branch: delete it from v3, report the corrected floor and its variation, and let block two's authoring (which is after the pilot by registration) decide holdability with the pilot's numbers in hand.

Lead's disposition: (b), with one amendment — the variation gate's tolerance must be sized to the instrument, not to the level alone: 0.01 cores × 0.3194 W × 480 s ≈ 1.5 J, i.e. just above the ≈ 1 J attribution limit, so the level's 20 % tolerance and the instrument's limit agree to within 50 % and the gate is not microscopic; the judge should say which of the two bounds governs and why. Reasons (argument): (a) is a foregone stop; (c) reaches a real conclusion but from a placeholder level that block two has not authored; (d) removes a guard that the refuter shows can be made meaningful; (b) keeps a guard that measures the thing that actually confounds a paired contrast. Against (b): whether a constant observer truly differences out depends on the load arm not changing the observer's work (the power recorder parses the same stream; the census and load recorder run the same commands) — the judge should rule whether that assumption needs a registered check (for example, the observer share in the load arm within the same tolerance of the idle arms).

Deliver: the ruled option; exact registration v3 field text (statistic, tolerance, its basis, the supersession note naming the v2 statistic and both corrected floors 0.178/0.161); the exact replacement for `stop_branch` and for the `observer_floor` derivation in `pilot_summary` (lines 1064–1073 at 69315e79), including what happens when `whole_envelope_observer_cpu_s` is missing (refuse, never pass); defect-shaped regressions that FAIL at 69315e79, each with its counterfactual input — at least: both archives re-derived → corrected floor 0.178/0.161 reported and the cause ABSENT under the ruled rule; a synthetic per-envelope observer series with sd 0.02 → PRESENT; a missing whole-envelope key → refusal; and whether the two archived summaries' reported floors are corrected by dated addendum only (the lead says yes).

## Constraints on the judge

Read-only; nothing armed. Do NOT run `systemsetup`, `sudo`, `powermetrics` or `launchctl`. At most one run of `tests.test_quiet_predicate_campaign`. Probes: `git show 69315e79:<path>`, `sed -n`, `python3` over the two archive roots named in exhibit G (read-only). Read the sealed rounds 1–2 files in this directory for context; do not re-rule Q1–Q4. Ruling file: `31-coldgate-fable-observer-floor-design-ruling.md` in this directory. Under 12 KB.

## Charter pin

Charter (operative v2): `docs/process/coldgate_charter.md`
sha256
099de884b1d081ffa547dfd8ff5837e75813a870ff8c7285c749c1b440c95d81

## Exhibit manifest

```
fbf4b9b90f0662dc898d501aaca23be2854e8dd0fba23b3374c9ea54631210cb  20-charge-observer-floor.md
8ab780e71f11f9d4da369d832e8ba539daedc404c3122b29116480e3579f06a9  21-coldgate-fable-observer-floor-ruling.md
ce93ecc41a03cb211573a2098ad2dba40f09fa50bbcddd631a4fc408ba8341e9  22-opus-contract-refuter-observer-floor.md
1016dfad5a545dfcdf9c563ecde5fec93077ad6a12549c4b2871aeb389338fb2  25-magistrate-synthesis-round-2.md
d8109170ba4e876c488bd8ce815ddf3eddc814f4b3ae7eb482e4da492d10dd81  exhibit-D-observer-floor.md
07a33fcc406fce479ecb6c9b6e6b4cf67d0ad46489bceecf0a0024cd5fbe67c6  exhibit-G-observer-accounting.md
d87ffcea92f876e87daad3c8319519dfcde3391b34eb51842e88ec6f2ea2d123  10-coldgate-fable-ruling.md
a69fa595cab9686c9c74a0e34503e68020e740f2c280b02e0c474a66bacc0463  11-opus-contract-refuter.md
153ad80b55d4668c3d567d8aaf8789d64e8a6bb1d7185cc3163fea9a40e7989b  15-magistrate-synthesis.md
```
