# Charge — cold gate PR0-ESC-01: escalation on PR-0 (claim-gate v1 replay golden) after two same-signature rounds

Assembled 2026-09-25 ≈06:15 PDT by the resident magistrate (Opus 5.5, activation 152c9255). Nothing is armed. This gate is a mandatory trigger: two consecutive review rounds failed with the same signature.

## Background in plain words

PR-0 (WR-7, `ex-cgw-wiring-rulings-v1-1.md` §4) freezes a snapshot, called a "golden", of every v1 claim-gate decision before the claim-gate v2 code changes, so the later change can be shown to move no historical decision.
- The first review lens (`ex-03-lens.md`) showed that 7 of 9 real code mutations survived the golden.
- Fix round 1 (`ex-04-fix1-brief.md`, `ex-05-fix1-report.md`, commit `7929a7ec` on `test/2026-09-25-claimgate-pr0-golden`) killed those nine.
- A fresh delta re-audit (`ex-06-delta-reaudit.md`) found three things. The kills were confounded by an unrelated digest assertion. With that neutralised, 7 of 10 new mutations survive, which is the same signature. And there are 2 new BLOCKERs: D-1, a mocked admit path that hides a production KeyError; and D-2, a deadlock between WR-6 and the golden's refresh isolation.

The magistrate's proposal is `ex-10-magistrate-proposal.md`: a structural cure S (mechanical branch-coverage and mutation-sweep acceptance), plus D-1 and D-2. The auditors and the proposal are arguments before you, not authorities.

## Questions

- **G1.** Is S the right structural cure? Consider:
  - whether 100 % branch coverage of the named functions from golden inputs is achievable without `joulewise/` changes;
  - whether the named function list is complete for what the CG-4 PR edits (WR-0 to WR-10);
  - whether the operand-collapse sweep with zero survivors is the right acceptance, or whether equivalent mutants make it unachievable, and if so what the ruled exception is.
  Verify against the code.
- **G2.** D-1: AFFIRM or amend, and rule the production defect's lane and interim status. Is a KeyError crash in `_claim_issuance_gate` acceptable as fail-closed until fixed?
- **G3.** D-2: rule option (a), (b), (c) or another. Verify the deadlock claim against WR-6 and `tests/test_claim_replay_golden.py` at `7929a7ec`.
- **G4.** Issue **"PR-0 rulings (final texts)"** for exactly one more implementation round, executable without choosing, with its acceptance criteria. Add a plain summary of at most 4 lines for Ed.

## Constraints on the judge

- Read-only.
- Never run `sudo`, `launchctl` or `powermetrics`.
- Never touch `/Users/edr/code/JouleWise` (the canonical root), `/Users/edr/night-custody`, `~/Library/LaunchAgents` or `/Users/edr/JouleWise-measurement-*`.
- Clone to `/tmp` for probes: `git clone` the repository at your worktree's HEAD and fetch the branch.
- Focused tests are allowed; the discovery suite is not.
- Write only the ruling file.
- Do not read RUN_STATE.md, TASK_QUEUE.md, council logs, run reports, memory, or any `docs/process_traces` file outside this packet directory.

## Charter pin

Charter (operative v2): `docs/process/coldgate_charter.md`
sha256
099de884b1d081ffa547dfd8ff5837e75813a870ff8c7285c749c1b440c95d81

## Exhibit manifest

```
944980325a648b630c375b6a7f5f13b8bbfbdcc65cf677717cf893b00bad3b5b  ex-03-lens.md
9320ec4fb6243faf69bfce53ecf3d53615608b6bcdabbb935b4cecdc65a9fc5d  ex-04-fix1-brief.md
af2406d3d787f3e9a054d89a7a0bd366abdb8ba37082e29d28ccdf2962e64798  ex-05-fix1-report.md
4cf339159dd2ab6425c9a3ca070ba31bd6a727333eb221e3481f5f4820425f39  ex-06-delta-reaudit.md
ea65e5871236533504c84530c2f47a69b43297e653636113c1bf741f3f1a81f4  ex-10-magistrate-proposal.md
84ef2c0ce15d49ea466a822a3fc406499d7f06adf88f59419fa19bf047701511  ex-cgw-wiring-rulings-v1-1.md
```
