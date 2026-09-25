# Charge — cold gate JCORRECT-FLOOR-01: rule the four-model council on the J/correct noise floor, the cross-model floor, and a claim-side accuracy BLOCKER

Assembled 2026-09-25 ≈06:05 PDT by the resident magistrate (Opus 5.5, activation 152c9255). Nothing is armed.

## Background in plain words

The paper's headline asks how the energy per correct answer changes with MATH difficulty and model size. The draft analysis plan (AP-5M v5) registers a dimensionless log contrast Δ_L. The ruled claim gate (CG-1..CG-4) needs a matched noise floor for it, and the wiring ruling (WR-9) sent the choice of floor to this council.

Four blind seats answered (`ex-02-seat-{sol,astra,opus,fable}.md`). All four choose option (c), a floor in log units, matched to Δ_L's own shape. The comparison was drafted by an Opus subagent that verified every disputed fact, and the magistrate added proposals §P (`ex-30-synthesis.md`: Terms with a worked floor example; J1–J5; 9 splits; §P).

The Opus seat also found, and the subagent verified, a BLOCKER in the ruled CG-1 itself (S3 / P-0). CG-1 builds its standard error from envelope scatter only. The sampling error of the correctness fraction, shared by all envelopes, enters divided by k or not at all. Desk checks put the false-admission rate at about 0.39–0.81 per level at a true effect of zero.

The seats and the synthesis are arguments before you, not authorities.

Ed's standard: "preventing bad science, not progress on the paper when models agree". Under D-184 the four-model council decides experiment design, and a fixed ruled text changes only through an explicitly labelled cold-gate amendment.

## Questions

- **F1 (P-0).** Verify the S3 BLOCKER yourself. Read CG-1 in `docs/process_traces/2026-09-24-activation-278ebc9e/91-claimgate-final-texts-v2.md`, `joulewise/analysis_engine/estimators.py` ≈`:390-400` and the WIP helper via `git show origin/feat/2026-09-24-claimgate-v2:joulewise/analysis_engine/estimators.py`, and the AP-5M v5 draft's estimator section. Run your own desk simulation at the draft's planned n_acc and k. Then either AFFIRM the magistrate's amendment text, write a different labelled amendment of CG-1, or send a named question back to the council. If you amend, give the exact SE formula, the df rule, the V_acc estimator (the paired bootstrap over problems, or another), and the simulation acceptance criterion.
- **F2.** J1–J5 splits S1–S9 and the §P proposals: for each, AFFIRM or write a different ruling, with the deciding evidence. In particular: S2 (one transferred floor plus a verification pair, versus per-cell floors); S5 (null on the pilot set versus test problems, against the outcome-blind freeze); S9 (window class).
- **F3.** Anything the seats and the synthesis all missed.
- **F4.** Issue **"J/correct floor rulings (final texts)"**, executable without choosing:
  - the floor derivation rule, in its unit, with the null block definition;
  - k_cal and n_cal;
  - the transfer check;
  - the byte-identity refusal and its ceiling;
  - the problem set;
  - the registration fields;
  - the CG-1 amendment text if F1 amends;
  - the window count before the first claim-bearing number;
  - the prerequisites (lane A283's seeded sampler; the window class).
  Add a plain summary of at most 8 lines for Ed.

## Constraints on the judge

- Read-only.
- Never run `sudo`, `launchctl`, `powermetrics` or any model inference.
- Never touch `/Users/edr/code/JouleWise` (the canonical root), `/Users/edr/night-custody`, `~/Library/LaunchAgents` or `/Users/edr/JouleWise-measurement-*`.
- Desk Python and focused unit tests are allowed; the discovery suite is not.
- Write only the ruling file.
- Do not read RUN_STATE.md, TASK_QUEUE.md, council logs, run reports or memory. Do not read any `docs/process_traces` file outside this packet directory, except the files ex-30's header cites (AP, CG, CGW, ACC2, C407) and `docs/process_traces/2026-09-24-activation-278ebc9e/19-desk-simulations/`.

## Charter pin

Charter (operative v2): `docs/process/coldgate_charter.md`
sha256
099de884b1d081ffa547dfd8ff5837e75813a870ff8c7285c749c1b440c95d81

## Exhibit manifest

```
0fcb9f61b437a191afdd97242d655fd50ace5d38653b56d07c7f84d2ea2d3117  ex-00-question.md
24379c0dab2417227ae7fc038e269ab3d2a34ae20893545a6614916cda6884ad  ex-02-seat-astra.md
6eba1bdb32d4ebb2d69c3a8d73f0abc09cfb4dd6e2a302532e479714314ebe67  ex-02-seat-fable.md
2d7ff0ac5a011f481231b38f2d48b42ac2b1a36ba5383db8f7221eb5ad227d84  ex-02-seat-opus.md
70775187a7642ce3d7afc2761ed0be756a921b621a5632344c5dc7616a7022a4  ex-02-seat-sol.md
bcb9422c31b28c2a31b54b57ac6848f4503b3339a10fe4ef934b8b598658e580  ex-30-synthesis.md
```
