# PR #813 audit round 4 repair, 2026-11-18

[AGENT], Tier 2. Audited head `5765be043`. W1 base `b2e01464d`.
[RL-182a check 1](https://github.com/mpmdw/JouleWise/blob/45b2d57/docs/research-audits/2026-11-10-fable/RESEARCH-LEAD-DECISIONS.md#L19946)

The round 4 replay reproduced both findings. The previous trace accepted
a prompt hash between the stamps, and the clean adapter failed the prior
zero-gap assertion on a clock that advanced once per read.

The cached first-yield arm of `MlxRuntimeAdapter._generate` now takes the
prefill-end and token-0 clock reads in two consecutive assignments. It
constructs the two phase events after both reads. Decode start shares the
prefill-end timestamp. The round 3 marker override in the generation view
is superseded, and that file returns to its W1-base bytes. The legacy pin
check verifies the Pilot-10 digest after removing only the cached boundary
arm and restoring the original token-stamp selection.

The static check parses the live adapter source, locates the two assignments,
requires each to be a direct clock read, and checks common block identity and
consecutive statement indices. The runtime check runs a cached synthetic
endpoint turn and asserts a gap of exactly one tick. Its read step is the
exact binary fraction 1/1024 s.

All 139 focused tests passed. The clean adapter passes both checks. The AST regression rejects an extra
model call, the 35 ms encode and delay, moving the token-ID extraction,
and inserted `prompt_provenance(prompt)`. It also rejects an extra stream
request or clock read. Executing the extra-read mutant independently fails
the one-tick runtime assertion.

The scorer and registration files still match the audited head, and the
accepted synthetic scorer comparison passes with Q words enabled and
disabled. Neither state file appears in the PR diff.

## Runtime hashes for the handoff

| Artifact | SHA-256 |
|---|---|
| `joulewise/adapters/mlx_runtime.py` | `f496662de3621ad1b0621e91b9cbe9145827190c9198053d8a00be67ffc308ad` |
| `joulewise/align/apple/generation.py` | `853a3d0a651e90a8a6dd89a5e0905fe5cb5047345d8760ba8d95b0c276e52c04` |

CI and the final-head readback are recorded on draft PR #813. The lead's
independent disposition and receipt binding remain W1 signing steps.
