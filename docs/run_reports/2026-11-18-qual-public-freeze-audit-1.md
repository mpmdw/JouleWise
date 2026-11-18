# Qualification public freeze gate audit round 1

**2026-11-18 · Tier 2 [AGENT] · Draft PR #835 · HOLD_FOR_FIT_FREEZE**

Round 1 audited `286ee878d0a7764d7fdf043d3a893d339ef7b459`. The
independent audit result was BLOCK. Both findings were reproduced against
the audited test or shipped gate.

| Finding | Disposition | Regression |
|---|---|---|
| HIGH. The shipped gate holds even with a bound public `yes` because the reviewed production pin is unset. | **BLOCKED on owner delivery.** PR #795 still lacks `authorize-freeze2` at `2f67206528f46d227815355ce701bd738233f647`. The reviewed immutable revision, exact dependency files and proof of the registered sibling in both ledgers are required before binding the provider. | The unpinned-provider regression exercises the actual emitted gate for all six items in bash and zsh. Start and Run each fetch the fixture refs and refuse before consulting the public ledger or materializing provider code. PASS for safe hold. Production authorization remains unverified. |
| MED. The synthetic verifier rejected the real public path of the registered qualification sibling. | **Repaired.** Both ledgers validate the sibling's status, digest syntax and repository-relative JSON path. Each sibling path is metadata for this look. The verifier reads the pinned interim manifest and its own allowlisted public evidence. | The control accepted in both shells before the fix. The real registration path alone on current, execution or both ledgers produced six expected red results. After the fix all six passed with the exact observed Git lookup set. Absolute, parent-traversal and non-JSON sibling paths refused on each ledger. |

The default synthetic history uses the public manifest path from the
`registered` row on main at `e6d30561ae77a2d66e324603c5094db57c3075cd`.
The other fixture values are invented. The synthetic pass on both decision
paths establishes item behavior only for the fixture CLI. It carries no
production mixed-ledger validation or issuance evidence.

## Verification

- The standalone public-arm matrix passed in bash and zsh, including ordinary
  `yes`, committed RL-184 naming and the two audit regressions. The observer
  reported zero prohibited lookups.
- Real regeneration repeated all six renders and matched the three kits,
  three queues and each 38-path closure. Lint passed 74 shell syntax
  checks and 57 Python compilations. The work is limited to the synthetic
  fixture and this report. The integrated local suite follows the owner
  delivery and exact production-pin test.
- The earlier head had hosted quick and shard 4 failures in
  `tests.test_agent_identity`. Shard 4's same matcher case is also tracked
  in issue #834. The test and matcher are unchanged from the audit base.
  [Earlier exact-head CI](https://github.com/mpmdw/JouleWise/actions/runs/44310512985)

Seat evidence is under `audit-1-repair.24kNv5/`. See `red.log`,
`green.log`, `regen.log` and `prior-ci-shard4.log`. The previous round's
audit report and probe output remain in their original locations.

## Next handoff

The lead obtains the reviewed PR #795 CLI, dependency files and mixed-ledger
result from the provider owners. The item builder binds that revision
separately from the PR #812 runner, then reruns both decision paths and
refusals at Start and Run in all six items with the real pin and the read
observer. PR #835 stays draft and qualification stays held.
