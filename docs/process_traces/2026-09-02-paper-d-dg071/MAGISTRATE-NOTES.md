# Paper seat D (DG-071 / DG-075 statistics) — magistrate notes for the PR gate

Lane: the DG-071 (sampler-record interval width) and DG-075 (record spacing)
statistics producer `scripts/issue_dg071_dg075_statistics.py`, its test
module, and the issued artifact `docs/paper/round7/dg071-dg075-statistics.{json,md}`
over the retained a10 bundle `p2015-df-ph-decode-abs-r03` (read-only, sha
pinned). Branch `feat/2026-09-02-paper-d`; PR #276. Files 01–35 in this
directory are the seat briefs, the sealed reports, the cold-gate packet and
rulings, and the magistrate dispositions, in gauntlet order; `14a-dg071-bench.py` and
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
| Delta re-audit 3 | terra xhigh (252), execution lens, detached worktree | 29, 30 | `6846363d` | golden re-derived by hand (D1), eight values replicated from Method alone (D5); BLOCKER 2: B1 = `sorted(values[:400])` survives (no test at the paper's cardinality), B2 = brief D4's sha expectation fails; D6 states the same-signature recurrence → rule-11 cold gate |
| Cold gate (rule 11, mandatory) | cold Fable seat (packet-only) + Opus 5 contract-lens refuter, parallel, read-only | 31, 32, 33 | `5f105823` (= `6846363d` code) | both: B1 should-fix (residual / ruled-shape gap, not a recurrence), closure (a) both halves, no second consult; B2 a brief defect. Split on B2's remedy: cold seat prose-only, Opus redefine `git_commit` as the script's last commit; Opus adds M1 (the two-checkout test asserted a false property) |
| Fix round 4 (bench) + re-issue | magistrate | 34 | `70147173` → artifact `ebd947a0` | synthesis adopts Opus's remedy + the cold seat's gloss; 500-record differential bundle (CI) + retained-bundle value-of-record pin (bench, skipTest in CI); mutants `[:8]`/`[:400]`/`[:406]`/rev-parse all die; twice byte-identical AND byte-identical when replayed at the artifact's own commit; values of record unchanged |
| Fresh pass (op-loop §5) | Sol high (253), read-only, detached worktree | 35, 36 | `b6b4013b` | BLOCKER 0 / SHOULD-FIX 1 / NIT 1. SF1: the re-scoped provenance test still passed a `git rev-parse HEAD^` producer (fixture shape); N1: the provenance prose compared a SHA-256 with a commit id. Both cured at the bench (`6b6deb2f`, six fixture lines + one sentence), re-issued `2eea71fe`, byte-identical when replayed at its own commit; file 36 carries the escalation-trigger statement (a residual narrowed by the cure, not a recurrence — a third fixture-shape survivor fires the standing trigger) |
| Fresh pass 2 (op-loop §5, over `6b6deb2f`) | terra high (254), read-only, detached worktree | 37 | `dfe69194` | BLOCKER 0 / SHOULD-FIX 1 / NIT 1; replay byte-identical, hash comparison actionable, values of record unchanged. G1-SF1: the provenance fixture still passes a `scripts/` directory-pathspec lookup and a `--diff-filter=A` lookup; G1-N1: fixture-tuned `HEAD~2` survives. Third fixture-shape survivor → file 36's own trigger fires: no bench fix |
| Cold gate + consult (rule 11: standing trigger and second fix round on the same defect) | cold Fable seat (packet-only) + Opus 5 contract-lens refuter + Sol xhigh (255) consult, parallel, read-only | 38, 39, 40, 41, 42 | `73417fee` | Sol 255 (file 39): rejects the P1/P2′/P3 closure claim with five executed counterexamples on merge/rename/extra-ref histories (`--first-parent`, `--follow`, `--diff-filter=M`, `--no-merges`, `--all` all pass the proposed fixture and are wrong outside it); cure = pin the disclosed command (`subprocess.run` args) + one real-git smoke; merge now with a kernel row; Q5: the trigger should have fired at SF1. Cold seat (file 40): the packet's cure adds no discriminating power (all power is in the history), `--first-parent` proven WRONG on the real repository (PR merge commits), axis-derived F2 history pair offered with code. Opus (file 41): BLOCKER ×2 against the packet's cure (H1 regresses the `--diff-filter=M` kill; `--all` passes with P3 green and is reader-harmful), P1/P2′/P3 not a unique characterization on merge histories, generated-history differential built (30/30 base, every wrong implementation dies); Q3 frame rejected as a manufactured-harm question. UNANIMOUS: candidate cure withdrawn, #276 merges now, test-only cure on main under kernel row `DG071-PROVENANCE-TEST-01` (argv pin + F2 pair + add-only shape; fallback = the differential), severities affirmed, file 36 was wrong and the trigger should have fired at SF1. Synthesis file 42; two process proposals go to Ed, not installed |

The producer, test module and artifact are as at `6b6deb2f` / `2eea71fe`
after the gate: the gate changed no code. Post-review commits after the last
fresh pass (terra 254 over `6b6deb2f`) are custody, notes and the kernel row
only, so no further §5 pass is owed.

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
Delta 3 then found that the ruled shape's differential (2–8 records) never
reached the paper's own cardinality (406 records) and that the artifact's
`git_commit` line — the checkout HEAD at issue time — could never equal the
commit a reader checks out; reinterpreting a seat's "recurrence" verdict is
a rule-11 cold-gate trigger, so a cold Fable seat and an Opus refuter ruled
(both: should-fix, not blocker; close it, do not consult again). The fix is
one line in the differential, ten literals on the retained bundle, and one
function so the artifact names the commit that produced it rather than the
commit that happened to be checked out.

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
  next touch of the producer — which fix round 4 was; the clause was still
  not taken there (the round was bounded to the cold-gate remedies).
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
| `5f105823` | Delta 3 custody (29, 30) + cold-gate packet (31) + these notes |
| `70147173` | Fix round 4 (bench, per cold gate): provenance definition, widened differential, retained pin, M1, N1 |
| `ebd947a0` | Re-issue at 70147173 + cold-gate custody (32, 33) |
| `b6b4013b` | Cold-gate synthesis and fix-round-4 disposition (34) |
| `eba264f0` | These notes through fix round 4 |
| `6b6deb2f` | Sol 253 cures: provenance fixture history (SF1), `git show` comparison in the provenance prose (N1) |
| `2eea71fe` | Re-issue at 6b6deb2f + Sol 253 custody (35) |
| `dfe69194` | Sol 253 disposition with replay evidence (36) |
| `2610cd21` | These notes through fresh pass 2's launch |
| `e6687638` | terra 254 custody (37) |
| `73417fee` | Cold-gate packet on the fixture-shape class (38) |
| `d3119939` | Sol 255 custody (39) |
| `9ab5838a` | Merge main (t26 install wave, gate ledger, dx registry) |
| `e7425eef` | Cold seat + Opus custody (40, 41), synthesis (42), kernel row `DG071-PROVENANCE-TEST-01` + `test_gen_state` literal (bookkeeping, no producer or test-module change) |
| (this commit) | File 43: integration replay `f79d193b` (4847 OK skipped=125) + byte-identical reissue at `e7425eef`; ledger rows 9–12 (docs only) |

## Follow-ups outside this PR

- Registry rows DG-071/DG-075 and fill-checklist sentences: the prerequisite
  `feat/2026-09-02-dx-registry` branch has merged. The rows remain
  `VALUE_UNISSUED` / `STOP_FILL` in `docs/paper/results-fill-registry.md`, so
  artifact issuance is due rather than deferred behind that merge.
- Paper-wide rendered-digit disclosure (`scripts/paper_excursion_decomposition.py`
  and `scripts/paper_anchor_correction_quantified.py` also render six
  decimals on different, already-relative data): kernel row.
- Scratchpad-path redactions outside this lane (Opus C-9): post-merge batch
  on main.
