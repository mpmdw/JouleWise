# Charge — cold addendum PR0-SCOPE-01-ADD: the refuter's BLOCKER against PR-0 acceptance v2

Assembled 2026-09-25 07:31 PDT (clock-read) by the resident magistrate (Opus 5.5, activation 152c9255). Nothing is armed. The implementation round under the ruling was STOPPED on the refuter's BLOCKER. Its partial work is stashed in the PR-0 worktree.

## Background in plain words

PR-0 freezes a "golden" snapshot of every v1 claim-gate decision, so the coming CG-4 PR (wiring rulings WR-0..WR-10, `ex-cgw-wiring-rulings.md`) can be shown to move no historical decision. The re-scope ruling (`ex-20-ruling.md`, on the magistrate's proposal `ex-04-proposal.md`) set PR-0 acceptance v2:
- a mutation sweep with zero survivors over a decision-function target map;
- a validator corruption corpus with a residual ratchet;
- branch coverage.

A paired Opus refuter (`ex-21-refuter.md`) reports:
- **B-1:** the sweep, coverage and ratchet tests are standing unit tests that will fail by design at the CG-4 PR (live transitions, new v2 code inside gated targets, line-number exception keys), and CG-4's write scope cannot fix them;
- **M-1:** the target map misses v1-path functions that CG-4 edits (`estimate_paired_blocks`, `_ci_t_critical`, `analyze_claims`, `claim_side_bound`);
- further MATERIAL findings and NITs.

You are the cold judge. The ruling and the refuter are both arguments before you, not authorities.

## Questions

- **Y1.** For each refuter finding: AFFIRM its corrected text, write a different text, or REJECT, with the deciding evidence from the code. The code is `origin/test/2026-09-25-claimgate-pr0-golden` at `576f3989`; clone it to /tmp.
- **Y2.** Step back and rule proportionality. After four review rounds on a test-only PR, is PR-0's certification design sound as amended? Or should the golden's job be narrowed, for example to the `invariant` plus `transitions` byte-comparison as the live guard, with sensitivity certified once at PR-0 and recorded as evidence rather than enforced by standing tests? Say which option best prevents an unnoticed v1 decision change at CG-4, at the least ongoing cost.
- **Y3.** Issue **"PR-0 acceptance v3 (final text)"**, complete and self-contained, for exactly one implementation round. State explicitly which tests stand after PR-0 and which are certification evidence only. Add a plain summary of at most 3 lines for Ed.

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
7b391abc038e7152dd793e87ab69d90f786a081d2edc2a9253989f2372525efa  ex-04-proposal.md
588c6efb134865cfdca2e0a328e47b23d275672204c25d3d0e5dfaa2c7521be7  ex-20-ruling.md
b46f85fb74cfbb5275f1bdd905c05e0f22f1504f8b6206afb9bdc03b5c5a6743  ex-21-refuter.md
84ef2c0ce15d49ea466a822a3fc406499d7f06adf88f59419fa19bf047701511  ex-cgw-wiring-rulings.md
```
