# Charge — cold gate A281-DECISION-SPEC-01: the second fix round on the headline pure modules (rule 11 mandatory triggers: a second fix round on the same defect; two consecutive rounds failed with the same signature)

Assembled 2026-09-23 ~20:45 PDT by the resident magistrate (Opus 5.5, activation d8cc9c0a). Nothing is armed. The lead's dispositions below are ARGUMENT, not evidence. The exhibits are the seats' reports, verbatim or transcribed. Verify load-bearing claims against the code at `d2f9a273` (`git show d2f9a273:joulewise/energy_per_correct.py` and so on) or by your own probes.

## Terms in plain words

The headline experiment asks whether a larger language model (8B parameters) or a smaller one (1.7B) spends fewer joules per CORRECT answer on MATH problems at five difficulty levels. For each level L, R_L = (joules per correct answer, 8B) / (joules per correct answer, 1.7B). R below 1 means the 8B model is cheaper per correct answer. A *block* is a fixed slice of problems whose energy is measured as one unit. An *envelope* is one fixed-length power capture (600 s). *Holm* is the step-down multiple-test correction, here over a fixed family of m = 5 levels. *Sparse-level merging* pools a level whose correct-answer count is below 3 with its neighbour, in a fixed order (5 into 4 then 3; 1 into 2 then 3), decided on counts only. The *crossover level* L\* is the headline quantity: the difficulty level at which the bigger model becomes cheaper per correct answer. Three pure Python modules implement this: a packer (schedules blocks into envelopes), a reducer (per-cell accuracy and joules per correct), and an estimator (R_L intervals, Holm, merges, L\*). Nothing calls them yet; no data exists.

## History

Round 1 (exhibits 04, 07) failed both lenses. The magistrate ruled (exhibit 08), and fix round 1 (exhibits 09, 10) landed `d2f9a273`: 30 tests pass, and every file-level operand-collapse mutant is killed. The delta re-audit (exhibits 14, 17) failed both lenses again, with the SAME defect classes: (i) crossover and decision semantics, where non-monotone patterns still yield L\*, a false `boundary_in_merged_group` reason appears, and pooled levels are labelled "not estimable"; (iv) silent defaults, including retry provenance defaulted, sparse paths skipping validation, family not bound to arm, and incoherent timing accepted. There is also a new blocker: split-block bootstrap bounds are too narrow. An escalation consult ran with two blind seats (Sol, exhibit 19; Opus, exhibit 20).

## Lead disposition (argument)

D1 Diagnosis: both consults agree. The decision rule was INCOMPLETE: packet C, the synthesis and ruling 08 define only when L\* exists. Tests checked single points in a finite input space: Opus 20 enumerated the 676 reachable decision inputs and found 123 false crossovers, 91 wrong reasons, and every pooled row mislabelled at d2f9a273. Validation sat at the use site instead of the entry point.
D2 Decision specification: adopt Opus 20's closed vocabulary and pseudocode (group status E8/E1/NR/NE with an NE reason; level status `pooled` with `pooled_in`; a pattern vocabulary; typed L\* absent reasons). Monotonicity is judged over resolved groups only: NR and NE are gaps and are reported. The status rule is: Holm rejects, the direction by p, and the interval lies wholly on that side; otherwise NR with an `interval_disagrees` flag. An isolated sparse Level 3 is NE. Two splits between the seats, with the lead's picks:
  - LICENSING: Opus 20 says a merged lower 1.7B-cheaper group suffices (the claim is "8B cheaper at L\* on its own unmerged test, and 1.7B cheaper somewhere below"). Sol 19 and ruling 08 require at least one singleton licensing level, because a pooled R above 1 does not establish either constituent's R. **Lead: Opus.** The claim sentence makes a region statement about the lower levels, not a constituent statement.
  - REVERSE ORDER (88111): Opus says pattern `reverse_order`; Sol says `non_monotone`. **Lead: Opus.** More informative; no L\* either way.
  - CEILING VIOLATION (an item that overran even alone): both say the group is NE(`ceiling_violation`), never pairwise-excluded in the primary estimate. Opus lets the family's L\* proceed, treating the NE group as a gap. Sol withholds the headline L\* until a registered recapture resolves the item. **Lead: Sol** (reason `ceiling_violation_unresolved`). The violating item is by construction the hardest, and a gap there is selection.
D3 Acceptance: split `decide` into pure layers (merge → ratio_interval → holm → status → classify). Enumerate exhaustively against an independent, table-driven reference that the magistrate writes into the fix brief from THIS gate's ruled table, never the implementer: merge over capped counts 4^10; status 18 cases; a Holm grid around each cutoff; classify over 676 × 2 family inputs; composition through a mocked ratio_interval. Mutation counts are no longer acceptance evidence for the decision layer.
D4 Silent defaults: one frozen `Registration`, built only through `from_mapping`, with no defaults and unknown or missing keys refused. Opus 20's Q4 field list plus Sol 19's identity fields. Its digest is bound into roster, reducer output and decision output. Every public entry point takes it and checks it on every path. Structural tests: no public parameter defaults; no `.get(` / `setdefault` on input records.
D5 (a) Bootstrap bounds: Opus 20's share-scaled per-window bound u = k·(floor + anchor)·s per drawn block and model. (b) Drift balance: refuse at pack time above a registered `max_drift_lever_slots`; null is allowed only in `mode = pilot`; the formula max_gap = budget_j / (δ_upper · blocks_per_cell) is registered now and δ_upper comes from the pilot; recompute after every requeue. (c) As D2.
D6 Scope: split the lane. **A281a** (Registration + packer + reducer, including `terminal_refusals` and `parent_block_id` in the cell interface) gets fix round 2 NOW, with a narrow brief. **A281b** (estimator): THIS gate rules the decision table, and the table goes into the AP-5M registration text (lane A282, which Ed owns for adoption). Implementation then follows against the D3 enumeration.
Standing sub-rulings from round 1 that you may overturn: F1 (the ordering invariant is equal mean envelope index per cell, and empty slots are captured as `idle_slot`); F2 (append-only retry tails are accepted with conditions); the M12 amendment (after a second overrun, single-problem blocks are packed several per envelope by worst-case duration; Sol dissent recorded in exhibit 08).

## Questions

- **Q1** Rule the decision specification. AFFIRM / REJECT / AMEND D2, including the three splits. Deliver the AUTHORITATIVE worked-pattern table: at least the 19 patterns in exhibit 20 plus Sol 19's `[1–3]e|4:1|5:8`, `1:1|2:n|[3–5]8` and `1:1|2:n|3:8|[4–5]8`. Give pattern, per-level statuses, and L\* or its reason. Probe the current code at d2f9a273 on any row you doubt.
- **Q2** Rule D3–D5: acceptance shape, the Registration cure and its field list, bootstrap bounds, drift refusal, ceiling handling.
- **Q3** Rule D6. Is a second fix round warranted now on A281a with the narrow brief, and the estimator deferred behind the table? Or should the lane change shape in another way?
- **Q4** AFFIRM / REJECT the round-1 standing sub-rulings F1, F2 and the M12 amendment.
Tier findings BLOCKER / MATERIAL / NIT. Give exact text wherever a cure is ruled.

## Constraints on the judge

Read-only; nothing is armed. Never run `sudo`, `launchctl`, `powermetrics` or `systemsetup`. Never touch `/Users/edr/code/JouleWise` (the canonical root), `/Users/edr/night-custody`, any `/Users/edr/JouleWise-measurement-*`, or `~/Library/LaunchAgents`. Probes: `git show d2f9a273:<path>`, a `git archive d2f9a273` copy under `/tmp` for executed probes, and `python3 -B -m unittest tests.test_scored_packer tests.test_scored_reduce tests.test_energy_per_correct` run inside that copy. Never run the discovery suite. Read only this packet directory and the code at d2f9a273. Ruling file: `10-coldgate-fable-ruling.md` in this directory. Under 14 KB.

## Charter pin

Charter (operative v2): `docs/process/coldgate_charter.md`
sha256
099de884b1d081ffa547dfd8ff5837e75813a870ff8c7285c749c1b440c95d81

## Exhibit manifest

```
b26da402a8965a1c8804358afe48076b0f5768f59daf72717b873cb0244a8401  ex-04-a281-sol-execution-lens.md
1e6ff9a5b19cfb05673e8d55771a1ea7835ca7acefab3d05ff01ed9a6d03abfd  ex-07-a281-opus-contract-lens.md
715952a0e7a0c51be1cff131b4868b2e6873a4aaf17a1a673a99e7469bbf5b6b  ex-08-a281-round1-synthesis-and-rulings.md
3f49dea2e1cbbcae74dcf6b5b2b542d638f3d9f16ff76869a12f9d2a691f7a3a  ex-09-a281-fix1-seat-brief.md
7c8d53ee62f2bceb561f1cc33705d773b00800b5653fd1d9930a433583770372  ex-10-a281-fix1-seat-report.md
42307bd1edea5bbf13f69ae6ee573df4828737efd97ef81a302010ba3acfe628  ex-14-a281-sol-delta-reaudit.md
f14e116b2f273f162b4f2d3fd987cd231f08ab06ead67c970aa81912e0f9ba0e  ex-17-a281-opus-delta-reaudit.md
9da4bda66c210dea7b6a07f537470dd4769493a9b18923dbc1591b60c43b0215  ex-19-a281-sol-consult.md
685730701d04829e1f50097d135388561778ee1c8aa8e88345208015334a943e  ex-20-a281-opus-consult.md
e017892827e524d5a346436cec82ebd195e826186f79864db481d0ce54f08649  ex-45-original-seat-brief.md
5134d0d89cc239c1c4972967e0a2c620cb55c387b521e222e5c70eb43d966104  ex-headline-integration-synthesis.md
0d1430bae90e55e65bcc9397e741f3a1cd6cde6cc9f34606488685bd8eff6f0d  ex-packet-c-ap5-amendment.md
```
