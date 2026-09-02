# Paper seat D (DG-071 / DG-075 statistics) — magistrate notes for the PR gate

Lane: the DG-071 (sampler-record interval width) and DG-075 (record spacing)
statistics producer `scripts/issue_dg071_dg075_statistics.py`, its test
module, and the issued artifact `docs/paper/round7/dg071-dg075-statistics.{json,md}`
over the retained a10 bundle `p2015-df-ph-decode-abs-r03` (read-only, sha
pinned). Branch `feat/2026-09-02-paper-d`; PR #276. Files 01–28 in this
directory are the seat briefs, the sealed reports and the magistrate
dispositions, in gauntlet order; `14a-dg071-bench.py` and
`26a-golden-check.py` are the replayable bench scripts behind the executed
evidence in the addendum and in file 26.

## Gauntlet record

| Round | Seat | Files | Audited head | Outcome |
| --- | --- | --- | --- | --- |
| Landing | Sol high (167 → NEEDS-RULING; 169 landing under ruling R-167-1) | 01–04 | main at launch | producer v1: n = 1218 (every CSV row), six-decimal float64 renderings — later found defective |
| Refute, contract lens | luna (178) | 05, 06 | `1baf8c4c` | findings → fix round 1 |
| Fix round 1 | Sol (180) | 07, 08 | `1baf8c4c` | landed `681f30ce`; re-issue `a3dadadd` |
| Delta re-audit 1 | terra (185) | 09, 10 | `a3dadadd` (diff from `1baf8c4c`) | clean on the round-1 defects |
| Refute, execution + physics lens | Sol xhigh (245) | 11, 12 | `a3dadadd` | the population and precision defects (rows are per-rail; float64 at 1.78e9 s is coarser than the literals) |
| Refute, physics lens, second family | Opus 5 (246) | 13 | `a3dadadd` | converges on the same four defects independently |
| Blind fresh-Fable seat | Fable, packet-only (no loop context) | 14, 15 | packet | rules the defects real and the fix shape (dated addendum on the 2026-08-31 ratification withdrawing R-167-1 where they conflict) |
| Bench | magistrate | `14a-dg071-bench.py`, addendum | — | commit `b298ffe5` |
| Fix round 2 | Sol xhigh (247) | 16, 17 | `b298ffe5` | landed `29181d6c`: sampler-record population, exact Decimal, type-7 disclosure, tiling verification, 16 refusals bound through `main` |
| Bench re-issue | magistrate | 18 | `29181d6c` | `8096cb80`, twice byte-identical; values of record established (DG-071 120.9186 / 5.9508 ms; DG-075 120.9224 / 5.8949 ms) |
| Delta re-audit 2 | terra xhigh (248), execution lens | 19, 20 | `8096cb80` | values replicated independently; SHOULD-FIX 2 = two surviving value-changing mutants |
| Bench | magistrate | 21 | — | two fixtures, mutation proof; `7b9e2a5b` |
| Opus counter-review (gate item 6) | Opus 5 (249), contract lens | 22, 23 | `8ab397b5` | BLOCKER 0 / SHOULD-FIX 5 / NIT 5; C-1 = two MORE surviving mutants of the same class → escalation |
| Consult (rule 11 standing trigger) | Sol xhigh (250), read-only | 24, 25, 26 | `8ab397b5` | coverage SHAPE ruled: one hand-derived golden bundle with full-payload equality + Markdown/stdout projection, plus a fixed-seed differential against an independent reference; golden re-derived at the bench (`26a-golden-check.py`) |
| Fix round 3 | luna xhigh (251), third family | 27, 28 | `447a0f2b` | landed `6d30c105`; six mutants killed at the bench; Method glosses (Opus C-3/C-4/C-10) and prune (C-6); re-issue `6846363d` twice byte-identical, values of record unchanged |
| Delta re-audit 3 | terra xhigh (252), execution lens, detached worktree | 29, 30 | `6846363d` | (pending at the time of writing; recorded below when custodied) |

Three model families reviewed the producer (Sol, terra/luna, Opus) plus the
blind Fable seat; the physics refutation was found independently by two
families before the blind seat ruled.

## Why the gauntlet ran this long (for the reader of the PR)

The first defect was the magistrate's own: ruling R-167-1 glossed "every
retained record" as every CSV row without opening the bundle, so v1 counted
every width three times and rendered six float64 decimals that the file's
seven-decimal literals cannot support. Two refuters of different families
found it; the blind seat ruled; the addendum withdrew the ruling. The second
defect class — reported fields with no test pinning their value on an input
where a wrong computation differs — surfaced in two consecutive rounds
(delta 2, counter-review), which is rule 11's standing escalation trigger;
the spend went to a consult (Sol 250) for the coverage shape, not a third
pair of hand-added fixtures, and round 3 implemented the ruled shape.

## Overbuild / merge-ability prune (gate item 8)

Adopting Opus 249 §6 (file 22) with the magistrate's reading:

- **Earns its place:** the 16 refusals, each the named failure mode of an
  evidence artifact bound through `main` with a stated counterfactual;
  `--repository-root` (makes `git_commit` reproducible from a detached
  worktree); `SamplerRecord` as a frozen dataclass (field names are the
  contract vocabulary); the golden full-payload test and the fixed-seed
  differential (the ruled answer to the two-round coverage signature —
  the alternatives, a per-field census test, Hypothesis, a mutation
  framework, were rejected in file 26 as indirect or overbuild).
- **Pruned in round 3 (C-6):** `_ParsedRow.row_number` and
  `SamplerRecord.interval_start_literal`, both write-only.
- **Recorded, not taken:** Opus's below-nit clause for the `--bundle`
  `help=` string ("must equal the pinned path; exists so the mismatch
  refusal is testable"). Any edit to the producer changes
  `producer.script_sha256` and forces an artifact re-issue plus a fresh
  pass; a help-string clause does not justify that cycle. Carried to the
  next touch of the producer.
- **Not overbuilt, checked:** the artifact's Method section is long because
  the replication bar demands it (terra 248 D9 replicated the digits from
  it in 24 lines; delta 3 D5 repeats the exercise on the round-3 prose).

## Bench commits on this branch (from `git log 403998e1..HEAD`)

| Commit | What |
| --- | --- |
| `3fca7d6b` | Seat D landing (Sol 169) — producer v1 + 7 refusal tests |
| `1baf8c4c` | v1 artifact issued (later withdrawn) |
| `681f30ce` | Fix round 1 (Sol 180) |
| `a3dadadd` | Re-issue at 681f30ce |
| `a46000da` | Custody of files 01–14 |
| `b298ffe5` | Dated addendum + blind-seat ruling (15) + `14a` + fix-round-2 brief (16) |
| `29181d6c` | Fix round 2 (Sol 247) |
| `8096cb80` | Re-issue at 29181d6c + custody 17–18 |
| `7b9e2a5b` | Delta 2 cures (two mutation-kill fixtures) + custody 19–21 |
| `8ab397b5` | Merge main |
| `f0befff4` | Opus 249 custody + disposition (23), addendum correction, redactions, consult brief (24) |
| `447a0f2b` | Sol 250 custody (25) + ruling (26, 26a) |
| `6d30c105` | Fix round 3 (luna 251) |
| `6846363d` | Re-issue at 6d30c105 + custody 27–28 |

## Follow-ups outside this PR

- Registry rows DG-071/DG-075 and fill-checklist sentences: issued on the
  bench-only registry after `feat/2026-09-02-dx-registry` merges.
- Paper-wide rendered-digit disclosure (`scripts/paper_excursion_decomposition.py`
  and `scripts/paper_anchor_correction_quantified.py` also render six
  decimals on different, already-relative data): kernel row.
- Scratchpad-path redactions outside this lane (Opus C-9): post-merge batch
  on main.
