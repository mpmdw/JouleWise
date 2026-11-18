# Interim fit twin census, 2026-11-18

Tier 2 custody draft, PR #816. The independent twin follows the 16 twin fixes in the lead's synthetic divergence census. The tests regenerate the pertinent synthetic input cases and assert the primary outcomes recorded by Astra. The isolated-child fixture also uses a hand-derived coefficient reference. This run used the rulings, the handoffs and the census evidence without opening PR #795 implementation code.

Manifest pin candidate `scripts/cadence_interim_twin.py` has SHA-256 `ea9ce611f6f7df351aa21a6bbfd1523bdc7e36f1ef9b227baa93647999f0b90b`.

## Regression results

| Census item | Regression or control | Result |
| --- | --- | --- |
| T01 | A reduced roster passes B-4 after the main design drops delta. Both reduced channel designs and their folds omit delta. | PASS |
| T02 | Both sensitivity channels are null when required reduced onset fails. A successful reduced onset can still lose delta in an individual fold. | PASS |
| T03 | The one-second unsupported prefix contributes zero. Connected three-second gaps refuse. The bound child also accepts a prefix-only piece with zero GPU support. | PASS |
| T04 | Added zero-width and reversed GPU rows leave the Step 3 cell eligible. | PASS |
| T05 | Omitted and null turn indices, nonzero markers, missing token event types, phase rows and multiple turns. The bound child also processes omitted turn indices. | PASS |
| T06 | Numeric-string indices and stamps, tied stamps, a first token before turn start, and an early reported turn end. | PASS |
| T07 | Missing and null journal maps and scalars, missing or null reading kinds, and an all-error journal. | PASS |
| T08 | Future PM observations, fresh Unknown states, a stale final Nominal guard and a zero-valued floating-point level. | PASS |
| T09 | Absent and null TV0h and sensor maps result in the recorded cell-level disposition. | PASS |
| T10 | Empty PM evidence, zero elapsed, optional rich GPU fields and the different outcomes for absent and null used_ns. | PASS |
| T11 | Short, one-extra and two-extra native streams, an unreadable out-of-window frame and numeric-string elapsed. | PASS |
| T12 | Non-string pressure is missing. A single unregistered state fails the cell even when its other legs can be analysed. | PASS |
| T13 | A later-ending rich row contributes to an earlier overlapping clock window. | PASS |
| T14 | A short turn lacks the reference blocks. A zero-energy full block after the cut fails the leg. | PASS |
| T15 | The Step 3-only trace integrates partial block support across a three-second gap. | PASS |
| T16 | Nonpositive per-leg total, per-leg hot total and measured P-3 offset block each refuse. The P-3 controls exclude prefill and legs without an observed onset. | PASS |
| F01–F05 | Lexical path identities and receipt validation/provenance reproduce the observed defaults, including staged-span resolution. | PASS |
| F06–F08 | Separate energy and censored-fit relative metrics and unrounded inclusive 2% verdict. | PASS |
| RL-181 and RL-183a | Actual `python -I -B` child with the registered KM003C decoder and initializer. Match gives `yes`, perturbation gives `no`, and missing inputs or one-byte pin changes give `not_evaluable`. Unauthorized import, t helper call and out-of-scope read refuse. Neither real helper loads. The outer stream digit scan and read-only check pass. | PASS |

35 focused tests passed with NumPy and the exact registered decoder and initializer supplied by the local synthetic harness. `git diff --check` passed.

## NEEDS_SPEC

F01–F08 await RL-184. The named switches in the twin preserve the current primary behavior documented in the census. P01–P03 are tracked for the primary. CI and draft state are recorded on PR #816.
