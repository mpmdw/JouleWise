# Charge 20 — bounded round 2 of cold gate QPE01-DAEMON-CONTAMINATION-01: the registered observer-floor stop branch fires on every pilot by construction (rule 11 trigger: a registered stop rule whose amendment is a process rule; raised by refuter 11 B2, verified by the magistrate in exhibit D)

Assembled 2026-09-23 00:15 PDT by the resident magistrate (activation a022aecc). Round 1 (packet `00-PACKET.md`, ruling 10, refuter 11, synthesis 15) is sealed and is NOT reopened; this round decides one new question. Exhibit D is executed evidence generated at the bench over the read-only archives; the magistrate's disposition is labelled argument.

Terms in plain words. The *observer floor* is the night's own CPU cost during an envelope — the collector process plus every child it reaped (the power sampler, the 30 s load recorder, the census) — expressed as a share of one core over the round; it is computed from the collector's own accounting, not from `top`. The *smallest holdable share* (0.05 cores) is the lowest load level block two is designed to hold as its contrast. The registered *stop branch* `observer_floor_above_smallest_holdable_share` says: if the observer itself costs more than the smallest level block two would apply, block two cannot resolve that level, so "no cutoff qualifies".

## What the evidence shows (exhibit D)

- D3: the clean 02:17 night's floor was 0.05310 cores and its ONLY stop cause was the observer floor; tonight's floor is 0.05282 (with the sizing cause on top). The floor is ≈ 31.6 s of observer CPU per 600 s round on both nights, independent of the daemon.
- D3: the excess over 0.05 is 0.0028–0.0031 cores. At the measured 0.3125 W per busy core (exhibit C8, an efficiency-core rate) that is 0.42–0.47 J per 480 s interior, below the ≈ 1 J attribution limit (B2 sensible gates: tolerances sized to the instrument, ≈ 1 J / ≈ 5 J) and below block two's own 1 J contrast δ.
- D4: the 30 s load recorder itself costs 0.0076 cores; the rest of the floor is the collector and the power sampler at 100 ms, both registered instrument settings.
- D2: `stop_branches` and `block_two.smallest_holdable_share` are byte-pinned registration text; `stop_branch` (D1) compares with a strict `>` and no tolerance.

Consequence: under registration v2 — and under v3 as ruled in round 1 — a perfectly clean pilot returns "no cutoff qualifies" on this cause alone. The round-1 plan "re-run once under v3" would stop on it.

## Q4 — What does registration v3 do about the observer-floor stop branch?

Options. (a) Materiality form: keep the rule and add the instrument tolerance the sensible-gates rule requires — the branch fires only when (floor − share) × W_per_core × interior_s exceeds the ≈ 1 J attribution limit, with W_per_core the night's own measured rate (the pilot records it) or, absent a measurement, the registered constant 0.3125 W from night 20260922-2100; the field carries the arithmetic. (b) Raise `smallest_holdable_share` to 0.10 (block two's lowest level doubles; the pilot's purpose narrows). (c) Reduce the observer's cost below 0.05 by changing a registered instrument setting (power sampling 100 → 200 ms, or the load recorder 30 → 60 s; D4 shows the recorder is 0.0076 of the 0.053, so only the sampler change could reach 0.05, and it halves the power time resolution). (d) Delete the stop branch (block two's holdability is then unguarded). (e) Keep as is (every pilot stops on it).

Lead's disposition: (a). Reasons (argument): the branch's purpose is real — an observer that costs more than the smallest level would confound block two — but its bar is a bare share comparison with no tolerance, which at 0.003 cores is a gate on ≈ 0.45 J, four times finer than the instrument can attribute; (a) keeps the guard and sizes it to the instrument, which is the rule Ed set for every tolerance on the claim path. (b) sacrifices the science to the accounting; (c) changes the instrument to satisfy a threshold; (d) removes a real guard; (e) is a foregone conclusion.

Deliver: the ruled option; if (a), the exact registration v3 field text (name, formula, the source of W_per_core, the tolerance value and its citation) and the exact replacement for `stop_branch`'s comparison; the defect-shaped regressions (each must FAIL at `258c90ed`): (i) both archived summaries re-derived under v3 → the observer-floor cause ABSENT on the clean night and on tonight (excess 0.42–0.47 J < 1 J), (ii) a synthetic floor of 0.10 cores → the cause PRESENT (≈ 7.5 J), (iii) a missing W_per_core with no registered constant → refusal, never a pass; and whether this amendment may land in the same v3 registration as round 1's fields (the lead says yes: one re-registration, one ruled digest).

## Constraints on the judge

Read-only; nothing armed. Do NOT run `systemsetup`, `sudo`, `powermetrics` or `launchctl`. At most one run of `tests.test_quiet_predicate_campaign`. Probes: `git show 258c90ed:<path>`, `sed -n`, `python3` over the two archive roots named in exhibit D (read-only), `/usr/bin/log`. Read round 1's sealed files in this directory for context; do not re-rule them. Ruling file: `21-coldgate-fable-observer-floor-ruling.md` in this directory. Under 10 KB.

## Charter pin

Charter (operative v2): `docs/process/coldgate_charter.md`
sha256
099de884b1d081ffa547dfd8ff5837e75813a870ff8c7285c749c1b440c95d81

## Exhibit manifest

```
7083c815f103e2361aaa8ec51ef1b421fc7428bf2e7aa95ff7b5d8382c6725fa  00-PACKET.md
d87ffcea92f876e87daad3c8319519dfcde3391b34eb51842e88ec6f2ea2d123  10-coldgate-fable-ruling.md
a69fa595cab9686c9c74a0e34503e68020e740f2c280b02e0c474a66bacc0463  11-opus-contract-refuter.md
153ad80b55d4668c3d567d8aaf8789d64e8a6bb1d7185cc3163fea9a40e7989b  15-magistrate-synthesis.md
cea03093dd7b5f5f27d0beb131af132e988757486e07cfd96d73cb7fd7d41c00  exhibit-A-code-at-main.md
96456f3959b3a152b5cbbf8bbcc1ca21d4d4a0295439143b518f05d8f5b81d27  exhibit-B-authorities.md
a3f70f6542385cf037f912312b0b8c00f2d5787289042357a4616bfccf0bc0e6  exhibit-C-executed-evidence.md
d8109170ba4e876c488bd8ce815ddf3eddc814f4b3ae7eb482e4da492d10dd81  exhibit-D-observer-floor.md
```
