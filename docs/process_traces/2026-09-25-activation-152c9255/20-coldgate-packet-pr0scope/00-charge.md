# Charge — cold gate PR0-SCOPE-01: PR-0's ruled mutation acceptance cannot pass as scoped; re-scope or hold

Assembled 2026-09-25 07:02 PDT (clock-read) by the resident magistrate (Opus 5.5, activation 152c9255). Nothing is armed. This is a mandatory trigger: it is the third same-signature round on PR-0, following escalation ruling PR0-ESC-01 (`ex-02-pr0esc-ruling.md`).

## Background in plain words

PR-0 freezes a snapshot of every v1 claim-gate decision, so the coming claim-gate v2 change can be shown to move none of them. The escalation ruling replaced hand-picked checks with mechanical acceptance:
- R-4, full branch coverage of named functions. It passes.
- R-6, an automated mutation sweep: every small code change to those functions must alter the snapshot, or be proven harmless. It fails: 840 of 1,112 code changes go unnoticed, 770 of them inside one 2,500-line input validator.

The implementing seat weakened nothing (`ex-03-round-seat-report.md`, output `ex-01-sweep-output.md`). The magistrate's re-scope proposal is `ex-04-magistrate-proposal.md`. It is an argument before you, not authority.

## Questions

- **Q1.** Verify the breakdown and the structural argument yourself. Check out `origin/test/2026-09-25-claimgate-pr0-golden` at `576f3989` in a /tmp clone and run `python3 -B scripts/claimgate_golden_sweep.py --mutate` if your budget allows; it takes roughly 10 minutes. Is zero survivors over `validate_claim_verdicts` achievable in one more round, and at what cost?
- **Q2.** Rule (A), (B) or another scope. If (A), fix the exact decision-function list, the corruption generator's specification (seed, operators, count), how the validator residual is reported, and which lane owns it.
- **Q3.** Issue **"PR-0 acceptance v2 (final text)"** for one round, executable without choosing. Add a plain summary of at most 3 lines for Ed.

## Constraints on the judge

- Read-only.
- Never run `sudo`, `launchctl` or `powermetrics`.
- Never touch `/Users/edr/code/JouleWise` (the canonical root), `/Users/edr/night-custody` or `~/Library/LaunchAgents`.
- Use /tmp clones only; the discovery suite is not allowed.
- Write only the ruling file.
- Do not read RUN_STATE.md, TASK_QUEUE.md, council logs or memory.

## Charter pin

Charter (operative v2): `docs/process/coldgate_charter.md`
sha256
099de884b1d081ffa547dfd8ff5837e75813a870ff8c7285c749c1b440c95d81

## Exhibit manifest

```
e19ba6bc5c9319c5f5a7a29aa99433dc372982a5033b3f3556670c40bc2576f3  ex-01-sweep-output.md
2cb1c3ea646fda78307f7f359bcc4773ba39d4db959a2c3ec81a2036de263191  ex-02-pr0esc-ruling.md
a0b77d204683fb7abd520c4f177be6c5a17f5a394bd246726598fefffd3b059c  ex-03-round-seat-report.md
7b391abc038e7152dd793e87ab69d90f786a081d2edc2a9253989f2372525efa  ex-04-magistrate-proposal.md
```
