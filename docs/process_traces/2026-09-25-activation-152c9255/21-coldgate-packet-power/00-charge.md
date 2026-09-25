# Charge — Fable final pass HEADLINE-POWER-01: the magistrate's n-per-level decision (Ed's O-18/E4 delegation)

Assembled 2026-09-25 07:07 PDT (clock-read) by the resident magistrate (Opus 5.5, activation 152c9255). Ed delegated O-18/E4 ("n per level") as follows: the magistrate decides toward best practice, with Opus 5.5 and Astra 6 each ruling and a Fable 5.1 final pass. You are that final pass, cold.

## Background in plain words

The headline tests, per MATH level, whether a longer thinking budget changes the relative energy per correct answer of two models. A cold ruling today (`ex-jc-rulings-v1-1.md`, §A = amendment A-JC-1 v1.1) made the claim gate account for the sampling error of the correctness fraction. At the drafted 128 problems per level, power at the stated effect size became 0.20–0.37.
- The Opus ruling (`ex-01-ruling-opus.md`) proposes a census of the eligible pool.
- The Astra ruling (`ex-02-ruling-astra.md`) proposes min(600, available).
- The magistrate decided on the census with a floor of 128 (`ex-10-magistrate-decision.md`), and routed two A-JC-1 changes to you.

## Questions

- **W1.** AFFIRM or REFUSE the decision, with evidence. Verify the expected per-level counts against the importer or registration data in the repo, and recompute power at the census counts under A-JC-1 v1.1 with your own desk simulation.
- **W2.** Opus's df rule ν = min(ν̂_Welch, ν_proj,L): adopt it as an addendum to A-JC-1 v1.1 (give the exact text) or reject it.
- **W3.** A finite-population correction on V_acc under the ruled population (the level-L eligible pool): adopt it as an addendum (exact formula, and when it applies) or reject it. Say what it does to the false-admission rate at the census counts.
- **W4.** The final text for the registration's n_acc, SESOI and null-wording clauses, plus a plain summary of at most 5 lines for Ed.

A REFUSE is a stop. Say what would have to change.

## Constraints on the judge

- Read-only.
- Never run `sudo`, `launchctl`, `powermetrics` or model inference.
- Never touch `/Users/edr/code/JouleWise` (the canonical root) or `/Users/edr/night-custody`.
- Desk Python is allowed; the discovery suite is not.
- Write only the ruling file.
- Do not read RUN_STATE.md, TASK_QUEUE.md, council logs or memory.

## Charter pin

Charter (operative v2): `docs/process/coldgate_charter.md`
sha256
099de884b1d081ffa547dfd8ff5837e75813a870ff8c7285c749c1b440c95d81

## Exhibit manifest

```
9db57e6b2eabc9bcc750e5e3b834559fbe58118c64a423cd38f9a6d7752559a8  ex-00-question.md
21ceca7110d6ab1b6130181a36e13d4e1ee3d4388e68de9e68c650c56c043705  ex-01-ruling-opus.md
57689b1db543477ce2f12ef490a1bf1dc924412f20434bb9a0502a1dc4febc78  ex-02-ruling-astra.md
5f5735e63a2b8b46985da96e0d3b5f68b43411809bc08e3c015a4f6b75bcd9f3  ex-10-magistrate-decision.md
aca98625678fb5c4ddc18912d70ca798ca0f1932b2249b351633b37644a25d62  ex-jc-rulings-v1-1.md
```
