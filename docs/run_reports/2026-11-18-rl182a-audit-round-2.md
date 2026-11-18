# PR #813 audit round 2 repair, 2026-11-18

[AGENT], Tier 2. Audited head `f90e017e8`. W1 base `b2e01464d`.
[RL-182a check 1](https://github.com/mpmdw/JouleWise/blob/45b2d57/docs/research-audits/2026-11-10-fable/RESEARCH-LEAD-DECISIONS.md#L19946)

The audit replay passed the old check after the cached turn executed a
second native model call and after work was inserted before the token-0
stamp. The repaired check runs a synthetic `MlxEndpoint.chat` with
`episode_prefix`. Each stamp records the underlying model-call count, the
stream-request count and the clock-read sequence. Between the prefill-end
and token-0 stamps, both counts and simulated time must advance by zero.
The read sequence separately requires the existing two reads.

The first mutation consumes a second stream on the cache-accounting path.
It fails the model-call assertion. The second mutation adds 10 ms of stub
tokenizer work and 25 ms of delay. It fails the clock assertion. The
mutations are regression tests in `tests/test_mlx_runtime.py` and run
against in-memory copies of the adapter method.

`RUN_STATE.md` and `TASK_QUEUE.md` match the PR base byte for byte under
#829. The repair changes only tests and this report in the effective diff.
All 99 focused tests passed. The S/Q serialized-output regression passes on accepted synthetic inputs.
The registration and strict artifact hashes carry forward from the
[round 1 repair report](2026-11-18-rl182a-audit-fix.md).

Handoff for the W1 candidate assembly. The final independent disposition
is still a W1 signing gate. Before C1 arms, W1 supplies its first-token
exception count and its maximum prefill-end-to-token-0 gap, with RL-182a's
10 ms limit. The named release caller, #787, boundary test and signed
four-file binding remain C1 gates. Full-suite status is recorded on the PR.
