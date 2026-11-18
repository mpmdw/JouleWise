# Qualification drafts at the PR #812 merge pin

**2026-11-18 · Tier 0 [AGENT] · DRAFT / HOLD_FOR_FIT_FREEZE**

The worktree matched the remote audit head `fa9e4c24e` before branching.
The PR #812 merge commit `6e9d42f1dd3d308bc9239143d0d634ab965e50e1`
has the reviewed head `0d03cb7833bb8b15bc391127a7fe5519b7d98602` as
its second parent. All 38 frozen tree entries match for each qualification
kit, and all 38 digests in each prior draft match the corresponding
merge blob. The three qualification kit documents change only
`frozen.commit` on this re-pin.

The qualification dates are Fri 20, Sat 21 and Sun 22 Nov PST. The three
finite qualification queues retain the Nov 23 00:00 PST expiry. The
filler builder used the existing Nov 24 12:43:05 PST expiry so the two
filler queues changed only their kit binding. The two filler kits derive
from `a8dc8b23c` and change only the frozen block.

## Corrections and regression evidence

All line numbers are in the resulting files unless marked old.
Qualification commit `696d72b04` and filler commit `32c745be0`
carry the draft changes.

| Fable finding | Diff lines | Regression |
|---|---|---|
| 1. First-arm registration and s02 hand-read | `ITEM-qual01-s01.md:11`, `ITEM-qual01-s02.md:11`, `gates.sh:260–265` | Registration line appears in s01. s02 requires both records, accepts a lead record of a prior passing same-pin q0 pilot read, and names C.3 re-dating. |
| 2. RL-179 retired gates | `gates.sh` old 4–16 and 268–292 removed, new 221–247, 272–297 and 346–349 | Old item/watcher/debt inputs impose no arm bound. A valid finite queue with more than seven days between commit and expiry passes. |
| 3. Stricter batch rule | `gates.sh:328–334` retained byte for byte, `tools/item-template.md:18` | A batch during soak holds the arm. Exact batch +27 min releases it. |
| 4. Day law and line 2 pin | `gates.sh:214–218`, `tools/item-template.md:15`, `evidence/record-shapes.md:11` | One-block and same-date refusal cases, and a line-2 pin mismatch refusal. |
| 5. First-arm ledger and refusal recovery | `ITEM-qual01-s01.md:21` and `:468`, `evidence/record-shapes.md:33–66` | Pinned sequence append, older receipt without span id refused, identity-bound Check accepted and a no-receipt rc 3 attempt recovered without a recorded t0. |

## SHA-256

| Artifact | SHA-256 |
|---|---|
| ITEM-qual01-s01.md | `1a5117272b63ad05a9e9aaa079ff5deac352f532762517f748fa5098a79b6346` |
| ITEM-qual01-s02.md | `9690500b6af1e5cd55fe99bcf315c9ab1b15259de645f63dd69441b458cf33a1` |
| ITEM-qual02-s01.md | `1a19d11f960e7a853af1775a85fa429a1b1f26b15e9f80266758622a00ddbf28` |
| ITEM-qual02-s02.md | `1114911b17ea4b04a37a83bae8add7e50bb7e4702f90c3922f7bfb88128dcd86` |
| ITEM-qual03-s01.md | `e8c37d40b4fa2ee62f09b8a9d1f9826dc8c4fc1d6bd271857476c2c5dec78117` |
| ITEM-qual03-s02.md | `e72b4d0e36d9d766244bd9d1dbbf5b8c68c94f68092e131dfaa4eb1f21218b52` |
| f2-stab-15.v1.1.json | `8dceffc2e1a10a03d25c6c06487756fe37f8f5a1c57d52e242a64faabcbc36a1` |
| f2-stab-16.v1.1.json | `0fc1139dfb4b92ab18e5fb4c0b66e0d211a02e218e841a4cf94fde1fb19f2b96` |

## Verification

- The exact embedded qualification gates passed 1,480 synthetic cases
  under bash and zsh.
- The pinned qualification check ran 91 cases across the three kits,
  three queues and six spans. All six synthetic qualification spans
  completed with one capture and five consumers and passed their
  embedded operational Check against synthetic records.
- The pinned filler builder validated both kits and queues and all 24
  one-leg plans. Each kit matches all 12 positional cells of
  `f2-inst-01` field for field except the allowed leg seed differences.
  Both synthetic filler mocks and all six filler tooling tests passed.
  [Filler verification](../research-audits/2026-11-10-fable/evidence/align-v4-campaign/f2-stab/qual-pin/VERIFICATION.json)
- The qualification test set also passed 74 shell syntax checks, 56
  Python compilations, 21 standing-F0 checks, nine Round 10 tests and
  13 generator checks. `scripts/gen_state.py --check` and
  `git diff --check` passed.
- The work was limited to Tier 0 draft data, generators and synthetic
  regressions. The canonical production suite was outside this run.
  Exact reviewed-head CI passed at `0d03cb783`. Line 2 remains
  lead-owned. [CI](https://github.com/mpmdw/JouleWise/actions/runs/44270871439)

## Before issue

The lead stages the revised queues under their authenticated audit
commit and supplies freeze 2 and the exact-pin admission records.
Draft PR #821 at `0b09bee24` still lists the previous three qualification
kit hashes. Update its registered manifest and ledger binding to the new
kit hashes and land the registration on main before qual-01-s01 arms.
The lead also completes the RL-179 F-11 first native run, seeds the
attempt ledger, and supplies the latest older-pin Check if needed.
A prior q0 leg-type hand-read remains unconfirmed. Use the s01 close
interval for it if no passing prior same-pin evidence is available.
[Registration PR #821](https://github.com/mpmdw/JouleWise/pull/821)
