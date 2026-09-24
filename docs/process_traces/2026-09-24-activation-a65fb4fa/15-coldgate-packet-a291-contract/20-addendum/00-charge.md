# Charge — addendum to cold gate A291-CONTRACT-01: rule the paired refuter's objections to the ruling's cure texts

Assembled 2026-09-24 by the resident magistrate (Opus 5.5, activation a65fb4fa). Nothing is armed. Round 1 of this gate: charge `ex-00-charge.md`, ruling `ex-10-coldgate-fable-ruling.md` (a cold Fable judge), and the paired Opus contract refuter `ex-11-opus-contract-refuter.md`, which attacked the ruling's exact cure texts as a checker seat and an implementer would have to build them. The refuter reports 1 BLOCKER, 8 MATERIAL and 3 NIT, with executed counter-examples. It AGREES with Q1, Q2, Q3, Q5, Q11, Q14, Q17, Q18 and Q19 as ruled. The magistrate takes no position on any item. This addendum decides the text the checker seat and the implementer will be briefed from, verbatim, so every cure must be exact and must leave the seat no choice.

## Terms in plain words

The terms are as built in `ex-00-charge.md` §1: envelope, block, parent, single, stage, observation, culprit, placement, event, seal, replay, checker. The refuter's R1 defines a *culprit* as a block whose observed elapsed time exceeds its own bound: `predicted_s` at the initial and whole-block stages (45/21 §7 (W)), the derived worst case for singles ((N)). A *witness* is an executed test input that violates an invariant on a named path and must be caught.

## Questions (for each: AFFIRM the ruling's text / ACCEPT the refuter's replacement / write a better text; give the final exact text)

- **A1 (refuter R1, BLOCKER).** Culprit scope across stages when one envelope holds blocks of different stages (Q7, Q8, Q9, INV-35(a)). Verify the refuter's two executed cases.
- **A2 (R2).** Rule (N)'s numeric bound "2 × (number of singles)" against the refuter's counter-example: the bound's arithmetic, the per-item culprit-event limit, and whether factor 2 is a constant.
- **A3 (R3).** Placement of split-created singles; placement order within one event; execution order inside an envelope.
- **A4 (R4).** How Q15's "no `n/a`" applies to cells whose ruled consequence is a recorded value or a root-only refusal (Q12, Q13, Q16), and the meaning of Q13's "(root roster)".
- **A5 (R5).** The level status consequence of an `unattributed_overrun` refusal, and its place in the (P) precedence as Q12 extends it.
- **A6 (R6).** Q4(iii)'s `roster.models` against (S)'s "no roster copies of registered values".
- **A7 (R7).** Key names and types: `planned_drift_lever_slots` against `drift_lever_slots`, and the `planned_spread_shortfall` key format, type and absent-versus-false rule.
- **A8 (R8).** Does replay re-derive decisions and placements from the observations, or apply the recorded ones? Give the text and its interaction with "`_seal` is the sole caller of `_digest`".
- **A9 (R9).** Runner sequencing: may envelope r+1 start before `requeue_overrun(r)` returns? Rule whether a runner-lane CARRIED row is added, with its exact text.
- **A10 (R10, NIT).** Executed lever with zero counted parents for a model at a level.
- **A11 (R11, NIT).** The field that holds Q6's voided attempt.
- **A12 (R12, NIT, the refuter marks it unruled).** Should an event whose Σ `elapsed_s` exceeds `interior_s` be refused as physically impossible? Rule yes (with text) or no.
- **A13.** Anything else in the ruling's texts that the refuter's reading exposes and that a checker seat would otherwise resolve silently.

Finish with a single consolidated list, **"Final texts (paste verbatim into the checker and implementer briefs)"**, that supersedes each amended ruling-10 text, so the briefs quote one place. Tier findings BLOCKER / MATERIAL / NIT.

## Constraints on the judge

Read-only; nothing armed. Never run `sudo`, `launchctl`, `powermetrics` or `systemsetup`. Never touch `/Users/edr/code/JouleWise` (canonical root), `/Users/edr/night-custody`, any `/Users/edr/JouleWise-measurement-*`, or `~/Library/LaunchAgents`. Probes only in a `git archive c0998fdb` copy under `/tmp`. Write only the ruling file. Do not read any `docs/process_traces` file outside this packet directory, or RUN_STATE.md, TASK_QUEUE.md, council logs, run reports or memory.

## Charter pin

Charter (operative v2): `docs/process/coldgate_charter.md`
sha256
099de884b1d081ffa547dfd8ff5837e75813a870ff8c7285c749c1b440c95d81

## Exhibit manifest

```
075efe00891499e8218dfdaa68d0f1ac4041620dfa380d03ea4d3d9aa9c7b00c  ex-00-charge.md
76fa67a1f93d5f05306f55657c9b790b1676e8a5ffbf70289abb27e52afb9611  ex-02b-contract-v2.md
715952a0e7a0c51be1cff131b4868b2e6873a4aaf17a1a673a99e7469bbf5b6b  ex-08-round1-rulings.md
c7c18b90a4e7f1c4553daabb3caee663d4c177a324fd33639792456228e9c52c  ex-10-coldgate-fable-ruling.md
2bc8d6c874b51d0a2ed7af98a1d6678f0df5f7708086e757cd1ff5033b9c6a29  ex-11-opus-contract-refuter.md
9fc61ee0765f37516580c1c8972b85638d61e1333a420691f9b30dd214d38b7a  ex-45-10-coldgate-ruling.md
005c0c96ffe54885fbb0e4f37a6b2b25bea76f245d5e39dfae87ac9667ebfc84  ex-45-21-addendum-ruling.md
```
