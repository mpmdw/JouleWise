# RL-184 freeze-2 item handoff

**2026-11-18 · Tier 2 [AGENT] · DRAFT / HOLD_FOR_FIT_FREEZE**

RL-184 §2 at audit `61e8c9c2ccfd023c82e0da048dd89f4ed854a5bc` resolves
the naming representation. The qualification draft tree there is identical
to the tree at this branch's merge base `6c1076f25f22b4b1a0a3038244e4498b62292746`.
The branch retains the tests-only red at
`b9af98ad5ca2447306ec719d370752b3df1f0ab9` and the public adapter at
`0d1b5c9f11fc9d2a39fa15668500e169ee51d1ab`.

All six items use the same public CLI contract. Both Start and Run fetch
main and audit. The receipt identifies the current main commit, public
report and coefficient digests, reviewed verifier revision and either
ordinary `yes` or the verified ruling ID. The adapter remains fail-closed
until the shared verifier is pinned. RL-184 §2.4 assigns authentication
to the shared public verifier. The observed PR #795 head
`2f67206528f46d227815355ce701bd738233f647` has the older
`freeze2_commitment` and lacks the public `authorize-freeze2` CLI and
RL-184 resolver. PR #828's observed head
`e13d100b9c47c3c5b8c1b0072ed0b28d8a1665f6` remains an upstream
dependency for mixed-ledger acceptance.

## Verification

| Finding | Regression and result |
|---|---|
| The arm must accept the two public decision routes. | The synthetic CLI accepts ordinary `yes` without looking up the naming file. It accepts a canonical naming record on main bound to the report and an exact stanza at an ancestor of current audit. Bash and zsh exercise the named path through Start and Run for all six items. |
| A mismatched or stale naming attestation must refuse. | The fixture varies ruling ID, look ID, coefficient digest, public digest, designation, stanza bytes, path, canonical encoding, key set, log heading, uniqueness and audit ancestry. An audit-only record and a main record lacking an exact audit stanza both refuse. Run also refuses when audit loses the decision or the refresh fails after a successful Start. |
| Generation and arm behavior must retain their existing inputs. | Real regeneration twice reproduced six checked-in items, all three kits and queues and all three 38-path closures. The comparison covers every non-freeze gate and the existing date, close and t0 text. Bash/zsh lint and Python compilation passed. |

Seat evidence is under `rl184.WJLCVZ/`. The standalone matrix is in
`arm.log`, the final naming delta in `naming-final.log`, the real
regeneration comparison in `regen.log` and syntax results in `lint.log`.
The draft's hosted checks are tracked on its exact GitHub head. The
focused Air checks use committed synthetic histories. The required
production-pin check and the independent final candidate review follow
owner delivery.

## Next handoff

Bind the reviewed PR #795 public CLI revision and exact Python closure after
the owner validates the PR #828 mixed ledger on current main and the
execution commit. Rerun the ordinary and committed naming paths against
that exact implementation, followed by the integrated suite. The
qualification drafts remain at `HOLD_FOR_FIT_FREEZE` pending that work
and separate issuance authority.
