# Close offload build, 2026-11-16

Owner: Sol 6.1 via Codex, branch `ops/2026-11-16-close-offload`, base
`8fd5c8cc549311537b65d64e68036e52beebc28b`. Public repository; no measurement
bytes or private artifacts are in the diff. No MBP contact, no iCloud call,
no live measurement, no analysis, no outcomes read. This is an [AGENT] task.

M0: read CANONICAL, RUN_STATE 375 and the relevant 346–375 close/copy/census
text, CURRENT and POINTER_RULE, M0, AGENT_PLAN and orchestration. No active
stop card; clean initial worktree. The explicit owner's 2026-11-16 safety
request selects this bounded build ahead of the historical backlog. RL-173 A,
RL-171 and RL-172 (g)(i) read from the audit branch. The two supplied scratch
scripts were inspected as implementation references, not live validation.

## Change and evidence

- `joulewise/close_offload.py`, `scripts/close_offload.py`: structural closed
  output selection, newest-of-kind retention, cloud-only copy policy,
  per-file byte manifest, stdlib zstd/tar stream verification, private
  receipts, resumable upload/eviction/deletion records, shared launcher lock,
  process/fence guards, hard deadline supervisor, SSD Air pull with independent
  receipt digest and filtered extraction.
- `tests/test_close_offload.py`: synthetic opaque receipt bytes; fake brctl,
  stat and pgrep on PATH. No native service or remote host is used.
- `.github/workflows/close-offload.yml`: Python 3.14 focused synthetic job;
  the canonical CI suite uses Python 3.13.
- `docs/ops/CLOSE-OFFLOAD.md`, CANONICAL row: command, custody record path,
  recovery, status semantics, installation boundary and open authority conflicts.
- State kernel and its generated RUN_STATE/TASK_QUEUE projections register
  the bounded work. No operational pointer is reissued and no arm is authorized.

## Exit checklist

| Gate | State | Evidence |
|---|---|---|
| Byte-only implementation / deterministic close command | built | source and runbook |
| Synthetic functional coverage on Python 3.14 | PASS, final 28 tests | scratch focused-final.log |
| Python 3.13 structural compatibility and state fidelity | PASS, 72 cases, 18 zstd skips | scratch structural-final.log |
| Canonical suite | hosted PASS on c2612f16d; local attempt interrupted (130) after sandbox failures | CI 43998129636; scratch full-suite.log |
| Quick tier | hosted PASS on c2612f16d; local diagnostic FAIL | CI 43998129636; scratch quick.log |
| State/current/pins/diff fences | PASS locally; hosted fences PASS | gen_state/gen_current/repin --check and diff --check |
| PR / final-head CI | draft PR #807; initial full CI green; final delta CI tracked in PR checks | https://github.com/mpmdw/JouleWise/pull/807 |
| Requested one Sol cold seat | REFUSE: 2 authority conflicts, 3 reproduced implementation defects; code fixes await same-seat delta | private fallback/REPORT.md; manifest below |
| Policy / production admission | BLOCKED | plaintext-vs-encryption and pending-upload-vs-next-soak conflicts |
| Live GUI/TCC/provider validation | PROVISIONAL, lead-owned | never attempted from this session |

Two owner questions were sent while independent implementation continued:
(1) the requested `.tar.zst` format versus RL-173 A.1–2's application encryption
and off-MBP key; (2) requested nonholding UPLOAD_PENDING versus A.3 and A.7.
The current code implements the explicit requested archive format and status
but is not represented as satisfying those conflicting clauses. The runbook
holds deployment/standing-item issuance pending their resolution. This session
cannot invent a research/owner ruling. iCloud's sync-folder daemon remains
RL-173 A.3's interim mechanism and belongs in the maintenance line.

## Verification details and finding dispositions

The first focused run found a test expectation error: a deliberately shortened
file fails tar construction before stream verification. The test now changes
same-length bytes and directly exercises the stream hash mismatch.
Subsecond pending tests were then made phase-deterministic (real fake-provider
poll, followed by a synthetic deadline at sleep), avoiding dependence on
packing speed while the full suite runs. Production deadline behavior has a
separate actual-process/hanging-provider test.

Lead review found and fixed interrupted deletion losing its discovery receipt:
`DELETING` is durable and resumable without that receipt, remaining entries must
match the original manifest subset, and newest receipts remain protected.
It also added an independent receipt digest requirement to Air pull.
These are implementation defects fixed locally, not hardware evidence.

The local quick runner hit existing `PermissionError: Operation not permitted`
when tests create directories named `restricted` under its synthetic temp tree;
this session's inherited OS sandbox protects those paths. No attempt was made
to bypass that sandbox. Hosted CI provides the unrestricted independent suite
result; do not label the local failures green.

## Invocation and calibration ledger (D-050)

No implementation subagents. The owner explicitly requests one cold Sol seat
through `sol_seat.sh`; it must inspect the pinned head, source and RL-173 A only.
It may execute synthetic checks and is read-only with respect to this worktree.
The top-level builder remains responsible for final diff/verification and all
finding dispositions. Invocation manifest and raw artifact hashes will be
appended after execution. No measurement or claim number changed; process
gates caught implementation recovery and custody-proof gaps only.

Scratch root: `/Volumes/JW-EXT/scratch/sol-close-offload/` (private, never
committed). Logs: `focused.log`, `focused-313.log`, `full-suite.log`,
`quick.log`; PR body `pr-body.md`; cold review `review/`.

Next exact step: obtain the two owner rulings below; inspect the same-seat delta report and PR #807 final-head checks. Do not issue the standing item, merge or install on the MBP until the authority conflicts and live gate are closed.

Additional verification catch: the repository requires a timing-map entry for
new test modules. The quick tier identified `tests.test_close_offload` as
unweighed; added a 1.402 s scheduling hint from the local Python 3.13 final
24-case run (14 zstd cases skipped). Python 3.14 functional coverage is the
separate focused CI job, already PASS in run 43996700761. This is scheduling
metadata only and will yield to a hosted timing harvest.

Hosted CI quick on `68818a9a2` found a bookkeeping mismatch: registering the
new state-kernel task also requires updating `tests/test_gen_state.py`'s exact
live-id set and count. Both now include CLOSE-OFFLOAD-01 (284 rows); no state
semantics or generated pointer changed. The offload synthetic CI job passed
on both pushed heads. Local quick's final result was 282 modules, 14 failing
modules in 458.427 s: mostly OS-denied restricted paths, one existing Python
3.14 timestamp-parsing expectation, and the now-corrected timing-map entry.
The local Python 3.14 shard-discovery invariant replay passed 8 tests; the
Python 3.13 discovery replay instead meets the inherited sandbox's forbidden
optional real-corpus stat probes. Fixture census returns 2 (ps denied), not
an empty/clean census.

## Cold seat and dispositions

The requested `sol_seat.sh review` was invoked once after CI green at
2026-11-16 18:13 PST. The nested OS sandbox rejected `sandbox_apply: Operation
not permitted`; events.jsonl is empty and no final message exists. The wrapper
returned 0 anyway, so its shell return was not accepted as review success.
No Codex/model seat started through that wrapper. No bypass or permission
expansion was attempted. The built-in collaboration tool then launched the
ONE fresh `gpt-6.1-sol` xhigh seat with `fork_turns=none`, a bounded code/RL-173 A
read set and no repository writes. The same existing OS blinding applied.
The peer executed all 24 pinned tests and six synthetic probes.

| Finding | Lead disposition | Evidence / owner |
|---|---|---|
| P1 pending upload releases next arm contrary to A.3/A.7 | NEEDS_RULING; requested status remains, production blocked | owner decision CLOSE-OFFLOAD-PENDING-ARM, under CLOSE-OFFLOAD-01 |
| P1 plaintext archive contrary to A.1/A.2 | NEEDS_RULING; application_encryption=false remains explicit, production blocked | owner decision CLOSE-OFFLOAD-ARCHIVE-FORMAT, under CLOSE-OFFLOAD-01 |
| P1 provider grandchild survives normal worker pending exit | fixed; supervisor always clears worker group in finally | test_deadline_cleans_provider_grandchild_after_normal_worker_exit; same-seat delta requested |
| P2 cloud-only .ok later becomes Air proof | fixed; never create/overwrite legacy copy markers; per-source record alone is cloud marker; generic prior-copy provenance named accurately | test_cloud_only_completion_never_satisfies_air_opt_out_for_later_source; same-seat delta requested |
| P2 extraction filter normalizes accepted links after originals removed | fixed by refusing noncanonical, unresolved/cyclic or escaping source links before upload/removal | test_noncanonical_symlink_refuses_before_any_original_is_removed, test_symlink_cycle_refuses_before_delete; same-seat delta requested |

The marker fix also closes the builder's independently noticed risk that an
older directory's generic plan marker could satisfy a newer same-plan output's
legacy copy gate. No legacy marker is written by the new tool. Existing markers
are read structurally as the owner requested; their contents are never parsed.

### NEEDS_RULING

Question 1: readable `.tar.zst` as explicitly requested, or application-encrypted
archive with a verified off-MBP key record as RL-173 A.1–2 requires? Options
considered: owner exception for the requested archive format; implement encryption
and require the lead's off-MBP key evidence. Recommendation: follow A.1–2 unless
the owner explicitly amends it. Blocked: production admission and that custody
contract; no encryption/key action can be invented by this builder.

Question 2: nonholding pending older uploads as explicitly requested, or hold
every next arm until confirmation as A.3/A.7 requires? Options considered: explicit
owner exception; holding rc 20 until provider confirmation. Recommendation:
hold until confirmed under the governing rule. Blocked: ADMIT and standing-item
issuance. A sync-folder daemon can continue after our process group has exited;
this is not resolved by fixing descendant cleanup.

Both questions were asked asynchronously while independent work continued.
No answer has arrived. AGENTS.md's contract-conflict early-return rule applies:
finish independent work, preserve the result, and return the question/options/
recommendation/blocked-work shape rather than inventing an authority decision.

### Invocation manifest and private artifact pointers

| run_id | role/model/wrapper/session | prompt / sha256 | output / sha256 or stable id | status / disposition |
|---|---|---|---|---|
| close-offload-wrapper-1 | cold / model not started / supplied sol_seat.sh / no session | review/BRIEF.md / 32e0425146c12dbac461bd3b1fde9fcf9e5924a46869fe200e1e40c5334d6109 | review/stderr.log / d34a4e4359a4dc36526cf5b363da32f7b7594a3a09eea17cbdfd6425b052d93e | BLOCKED by inherited OS sandbox; empty events, no final envelope; not counted as a seat |
| close-offload-sol-1 | executing cold / gpt-6.1-sol xhigh / collaboration.spawn_agent, fork none / /root/sol_cold_review | review/fallback/PROMPT.md / 6dbb7d66a7462d15ae52a283c76bcd6b72d1a51f27e4b4fcf617a6d88d740694 | review/fallback/REPORT.md / a0e19e4b44384abe9d34ac62ff519c80b27ba37c6f5c0c5c681466a8efcdf762 | REFUSE; five findings dispositioned above; consumed by top-level builder; PR #807, source c2612f16d |
| close-offload-sol-delta-1 | same seat / gpt-6.1-sol xhigh / collaboration.followup_task / /root/sol_cold_review | delta request to same stable task id; final source head named there | review/fallback/DELTA-REPORT.md; stable invocation /root/sol_cold_review delta-1 | requested after final fix commit; result/hash and final-head CI are read back into PR #807 body |

All paths in this table are relative to private scratch
`/Volumes/JW-EXT/scratch/sol-close-offload/`, not repository artifacts. Raw logs
remain private because they are execution traces, not source material or
measurement evidence; this committed table is their audit pointer. No private
measurement data was read or promoted. The wrapper and blinding-profile hashes
are 1c1720a38e7634417ae9492eebc85358156316cb4f70e383ec1f68738a6243ae
and aef3a5ac67b77001d672fcab9b3868260c6740975e6573dbafa75ebc9b4d0994.

Delegation calibration: judgment-call read-only code review; lead outcome useful:
three reproduced implementation defects, two prompt/specification conflicts;
roughly ten minutes of lead code/test rework before delta. No final verification
or authority was delegated. Fresh-seat isolation prevented builder findings
from being supplied to the peer. No further cold model was launched.

### Exact hosted suite tails (initial green source head)

CI run 43998129636, source c2612f16d04b21785e7e684bd526920a8bc598ee:

```text
SHARD SUMMARY index=1/6 modules=84 tests=2581 failures=0 errors=0 skipped=48 result=PASS
SHARD SUMMARY index=2/6 modules=88 tests=2013 failures=0 errors=0 skipped=82 result=PASS
SHARD SUMMARY index=3/6 modules=87 tests=1875 failures=0 errors=0 skipped=8 result=PASS
SHARD SUMMARY index=4/6 modules=87 tests=2082 failures=0 errors=0 skipped=24 result=PASS
SHARD SUMMARY index=5/6 modules=88 tests=1914 failures=0 errors=0 skipped=26 result=PASS
SHARD SUMMARY index=6/6 modules=87 tests=2533 failures=0 errors=0 skipped=17 result=PASS
SHARD SUMMARY index=1/2 modules=1 tests=1 failures=0 errors=0 skipped=0 result=PASS
SHARD SUMMARY index=2/2 modules=1 tests=19 failures=0 errors=0 skipped=0 result=PASS
Ran 48 tests in 821.385s
OK
```

The final code/test delta requires its own CI on PR #807; its final exact head
and check readback are in the PR body, updated after push (not a self-referential
commit digest here). The local canonical attempt ran the prescribed command,
then was interrupted with SIGINT (exit 130) at 18:02 after inherited blinding
made it unsuitable as a final green gate; no local whole-suite PASS is claimed.
The fixture census was attempted and returned 2, `ps` denied, not a clean zero.
PROJECT_STATUS is unchanged: no advisor-visible scientific state changed.
