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
| Synthetic functional coverage on Python 3.14 | PASS, 24 tests | scratch focused.log |
| Python 3.13 structural compatibility | PASS on initial 21 cases, 11 zstd skips; final replay pending | scratch focused-313.log |
| Canonical suite | running | scratch full-suite.log |
| Quick tier | running; existing sandbox-restricted failures | scratch quick.log |
| State/current/pins/diff fences | initial checks running | will record exact results below |
| PR / final-head CI | pending | will record URL/head below |
| Requested one Sol cold seat | pending | scratch review/BRIEF.md and final message, hashes to be recorded |
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

Next exact step: finish synthetic/CI checks and the authorized cold review,
resolve the two policy questions with the owner, then hand the admitted PR
and proposed standing item to the lead. Do not merge or install on the MBP.

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
