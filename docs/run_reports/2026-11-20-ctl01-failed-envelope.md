# ctl-01 failed-envelope audit follow-up, 2026-11-20

Mission M0 found no active stop card or global work-selection gate. The
requested audit follow-up selected a synthetic-only agent task. The clean
worktree matched the remote head of PR #808 at `1f8541e4b`. Draft PR #900
targets that runner branch. [Draft PR](https://github.com/mpmdw/JouleWise/pull/900)

## Finding and change

Audit 6 reproduced a failed L001 with two 1,024-token physical turns. The
second turn returned an unexpected tool request. Its row held the delivered
counts before the runtime raised, so the old aggregate of returned results
reported only 1,024. The runtime exited 3 with no result.

RL-186 §2.3 defines one envelope that sums visible calls. In `c70609e92`,
the exception branch sums recorded visible physical rows for decode, cached
context, and fresh prefill. Fresh prefill is the full prompt count less the
cached prefix. The failed first/last clock boundaries still come from started
visible calls. [RL-186 §2.3](https://github.com/mpmdw/JouleWise/blob/71a83f666024c26e89cdce09dfb7a7e80d299794/docs/research-audits/2026-11-10-fable/RESEARCH-LEAD-DECISIONS.md#L21364-L21371)

## Verification

- `test_failed_envelope_counts_l001_second_call_with_tool_request` failed
  on the base with `1024 != 2048` and passed on the change with 2,048,
  exit 3, and no result file. The ruling update gives the returned visible
  call two reasoning tokens and the rejected call one. The envelope's
  `hidden_tokens` is two.
- `test_failed_envelope_counts_and_boundaries_at_every_failure_position`
  passed 40 cases across one to four visible calls. The cases cover a
  returned tool request and exceptions before the clock stamp, before the
  first stream yield, and after it. The existing finalize-exception test
  passed and still checks the end stamp recorded before the exception.
  All three focused tests passed on Python 3.13 after the ruling update.
- Replayed the existing synthetic roster against the base module loaded
  from Git and against the changed module. Both used the same fixture
  config, soak, and absolute replay paths with fresh output trees. Raw
  audit and runtime result files matched byte for byte for all 12 admitted
  legs, covering extra-turn, hidden, CPU, split, and plain, including capture
  and consumer references.
- The draft kit has 40 zero SHA-256 path placeholders and a zero commit
  placeholder. The production preflight and the pre-fence launch refusal
  tests passed.
- `python3.13 -B -m unittest discover -s tests/cadence` ran 239 tests.
  Of those, 226 passed and one skipped. Twelve launch-fixture tests recorded
  13 errors because the session was denied access to `/bin/ps`. Hosted CI ran
  the full suite on isolated Ubuntu runners. All 21 jobs passed on
  `c70609e92`, including the ctl shard and the launch-fixture shard.
  [Hosted CI](https://github.com/mpmdw/JouleWise/actions/runs/44714650958)
- `git diff --check` passed. The tested production diff is confined to
  the failed-envelope aggregation.

## Resolved rulings

- A rejected visible tool call contributes its recorded decode, cached
  context, and fresh prefill counts. Its row carries no reasoning count.
  `failed_envelope.hidden_tokens` sums `reasoning_tokens` from the visible
  calls that `physical_call` returned to the script. All envelope totals
  exclude hidden physical calls.
- If the endpoint raises before returning a result, the row's `actual_tokens`
  stays null, including after a stream yield. The envelope sums visible rows
  with recorded counts. An empty sum is zero and the failed row's count stays
  unknown. The runner omits the envelope if no visible call started.
  Otherwise it uses the first started visible row's `started_ns` and the last
  started visible row's `ended_ns`, falling back to that row's `started_ns`.

The existing runner satisfies both rulings. NEEDS_SPEC is closed.
[Exact-head hosted checks](https://github.com/mpmdw/JouleWise/pull/900/checks)

The next step is lead review of PR #900 before selecting the ctl runner pin.
