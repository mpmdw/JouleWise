# Charge — cold gate A292-ESC-01: second same-signature round on the A292 harness, plus the extreme-value ruling gap

Assembled 2026-09-25 09:17 PDT (clock-read) by the resident magistrate (Opus 5.5, activation 152c9255). Nothing is armed. These are mandatory triggers: a second fix round on the same defect class, and a ruled-text amendment.

## Background in plain words

The scored reducer (A292) is gated by the ruling E2 (`ex-e2-rulings-v1-1.md`), which requires zero non-equivalent surviving mutants in an automated mutation sweep.
- The first sweep (`ex-04-first-sweep.md`) left 23 survivors.
- A fix round added hand-written witnesses. The re-sweep (`ex-08-delta-sweep.md`) leaves three survivors (M033, M045, M050) of the same class, plus an unruled crash on astronomically large energy values.

The magistrate's proposal is `ex-10-magistrate-proposal.md`. It is argument before you, not authority.

## Questions

- **Z1.** Verify the three survivors and the crash inputs on `origin/feat/2026-09-25-a292-scored-reduce` at `660b32d7` (clone to /tmp). Rule P1: generated one-fault witnesses with mechanical acceptance. Give the exact generator specification (record types, predicates, container shapes, expected-code derivation) and the acceptance text.
- **Z2.** Rule P2: the 1e12 J domain bound. AFFIRM it, write a different bound or disposition, or REJECT it, with the physical reasoning. Give the exact amendment text for E2's domain clause.
- **Z3.** Issue **"A292 fix round 2 (final texts)"** for one harness round followed by one implementation round, executable without choosing. Add a plain summary of at most 3 lines for Ed.

## Constraints on the judge

- Read-only.
- Never run `sudo`, `launchctl` or `powermetrics`.
- Never touch `/Users/edr/code/JouleWise` (the canonical root) or `/Users/edr/night-custody`.
- Use /tmp clones only; the discovery suite and background tasks are not allowed.
- Write only the ruling file.
- Do not read RUN_STATE.md, TASK_QUEUE.md, council logs or memory.

## Charter pin

Charter (operative v2): `docs/process/coldgate_charter.md`
sha256
099de884b1d081ffa547dfd8ff5837e75813a870ff8c7285c749c1b440c95d81

## Exhibit manifest

```
b8c4bc21e16fa448ea8664c83754cbbef79d639cbaf344f32b809cdf143aae12  ex-04-first-sweep.md
daa126162cf6d300ba5305ca066681939ef28b0e11d70df98dd70fe770f718eb  ex-08-delta-sweep.md
5e1b229cc138ef194080909cc86fe8141db1076fc1f33ac6aec3c12a2e1e3626  ex-10-magistrate-proposal.md
81feba19b70cf71cc44d15444f5b274dbb52f5ea5686810274dbdea2f819e28e  ex-e2-rulings-v1-1.md
```
