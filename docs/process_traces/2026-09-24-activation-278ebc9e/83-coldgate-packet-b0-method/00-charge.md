# Charge — cold gate B0-ESC-01: rule the next round of A280 PR B0 after the same-signature recurrence, using the executed parity harness as evidence

Assembled 2026-09-24 ≈17:15 PDT by the resident magistrate (Opus 5.5, activation 278ebc9e). Nothing is armed. The gate is MANDATORY because round 2 would be the second fix round on the same defect.

## Background in plain words

B0 (`ex-10-b0-brief.md`) makes every idle-only site of the night machinery dispatch on the immutable NightKind table, with the idle night byte-identical and no second, unauthenticated kind authority. The history:
- Round 0 lenses (`ex-29a`, `ex-29b`) found 3 BLOCKERs. Cures C1–C6 (`ex-32`) were applied (`ex-47b`).
- The delta re-audit (`ex-72b`) found the same signature again: 2 BLOCKERs and 2 should_fix.
- Three blind consults (`ex-77` Sol, `ex-78` Astra, `ex-79` Opus) converged on a root cause: constant `KIND` lookups, which cannot fail, were replaced by disk reads that can. They also converged on a cure: first a differential parity harness, then a fix seat whose acceptance test is that harness passing.

The harness is now built as TESTS ONLY (report `ex-80b`; summaries `ex-80c-*`; inventory groups `ex-80d`; branch `test/2026-09-24-b0-idle-parity` at `eb8d745f`). It runs base `2ea6a7ec` against a candidate in isolated subprocesses over 11,346 corpus cases and 20 entry points, with 99,443 observations per side.

| Comparison | Parity mismatches | Outcome mismatches |
|---|---|---|
| Base vs base | 0 | 0 |
| Base vs round 0 `7647bb2e` | 56,131 | 35,351 |
| Base vs round 1 `bee658c5` | 31,378 | 19,615 |

Round 1 also has 1,688 new-private-API diagnostics. The magistrate takes no position.

## Questions (AFFIRM / write a different ruling; exact final text; BLOCKER / MATERIAL / NIT)

- **P1 (design).** Choose the next round's design:
  - (a) keep the current approach and drive the harness GREEN;
  - (b) "validate exactly as base, then route": every malformed-input path stays on base code, and dispatch on kind happens only after base validation has succeeded;
  - (c) split B0 into per-surface PRs, each with its own parity slice;
  - or another design.
  Weigh this against the counts: are ~19.6k outcome mismatches mostly one mechanism (for example extra reads or changed refusal order), or many?
- **P2 (the harness as acceptance test).** Is "zero outcome mismatches on the idle row, and zero parity mismatches except named new-private-API diagnostics" the right gate? Are call-order and extra-read differences parity violations or allowed? Which additions are needed?
- **P3 (seats, scope, independence, and the gate before merge).**
- **P4.** Whether B0 should proceed at all now. The scored night kind it prepares for waits on A291 and on the headline redesign, and B0 is refused standing at COUNCIL-407-01 R-A280. Is parking B0 until the scored-night design settles the better science-and-schedule choice?
- **P5.** Anything else.

Finish with **"Final texts B0-R2 (paste verbatim into the fix brief)"**, or a PARK ruling with its unpark condition.

## Constraints on the judge

- Read-only; nothing is armed.
- Never run `sudo`, `launchctl`, `powermetrics` or `systemsetup`.
- Never touch `/Users/edr/code/JouleWise`, `/Users/edr/night-custody`, `/Users/edr/JouleWise-measurement-*` or `~/Library/LaunchAgents`.
- Code evidence comes from `git show <rev>:<path>` for `2ea6a7ec`, `7647bb2e`, `bee658c5` or `eb8d745f`. You may run the harness on `/tmp` archives, within about 5 minutes per full comparison.
- Write only the ruling file.
- Do not read RUN_STATE.md, TASK_QUEUE.md, council logs, memory, or `docs/process_traces` files outside this packet directory.

## Charter pin

Charter (operative v2): `docs/process/coldgate_charter.md`
sha256
099de884b1d081ffa547dfd8ff5837e75813a870ff8c7285c749c1b440c95d81

## Exhibit manifest

```
2acefba1eeaf3a37dbd55415f716c0f9eb9869adbd0189a1c4382a13817d3929  ex-10-b0-brief.md
bc37428abb3e62b533a8d4573fe4fa97d0452e37a0246983d28dd629bf6bd2fb  ex-29a-a280-b0-sol-execution-lens.md
caac1cf7ef071161fa92f221b4c537ef5a7c2a63d810a1712811523244994f90  ex-29b-a280-b0-opus-contract-lens.md
77dfe80fbb05e8b5d49a47a2e2bda56f46e9f771e9e6e996668c57a7dc83e1be  ex-32-a280-b0-fix1-brief.md
f1aa5f725c8297e8f9b1468cf62734fa072402727c2c83df830617a69770616d  ex-47b-a280-b0-fix1-report.md
3fd1687ef62718991aacf777ad483fed5256b3aaaa1d03574a6508e52636631c  ex-72b-a280-b0-delta-reaudit.md
56d01208773f12639d2355467dc4757f1b3cdb1e3b3a71eb39730f0ea54438b4  ex-77-a280-b0-esc-consult-sol.md
f5b9875353f26cf3b407ca214e7b811c9a18b05d9172d4fd01ccd62097eec77c  ex-78-a280-b0-esc-consult-astra.md
8e01630a685959f98bb4347063a2c0dcb542ec3ad5b0ab19b16e3809172a5f58  ex-79-a280-b0-esc-consult-opus.md
75b4be3ef9adb4bbf42e1c6328afd3776fb6beabc52312471500da2d00a75758  ex-80b-a280-b0-parity-harness-report.md
f14e44e25334eb84f80d33a9d13c4a1533527baa1e132accb1b340df61c054f4  ex-80c-parity-summary-v1.json
baea6fa3aef7d2572596e36709b2a806326d0287f15ecf25c66f3c002674b3b7  ex-80c-parity-summary-v2.json
0b9a6b23d541a79d91680740977d1f7160e4c010c59a6fe6ee4dd298d2f9f4be  ex-80c-parity-summary-v3.json
77885662134cfe2bd56694569c5c64bb94cad5fe023c8b0fb582428f8ef46fc2  ex-80d-v3-inventory-groups.md
```
