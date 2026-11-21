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
| Synthetic functional coverage on Python 3.14 | PASS, final 31 tests | scratch focused-final.log |
| Python 3.13 structural compatibility and state fidelity | PASS, 75 cases, 21 zstd skips | scratch structural-final.log |
| Canonical suite | hosted PASS on c2612f16d; local attempt interrupted (130) after sandbox failures | CI 43998129636; scratch full-suite.log |
| Quick tier | hosted PASS on c2612f16d; local diagnostic FAIL | CI 43998129636; scratch quick.log |
| State/current/pins/diff fences | PASS locally; hosted fences PASS | gen_state/gen_current/repin --check and diff --check |
| PR / final-head CI | draft PR #807; initial full CI green; final delta CI tracked in PR checks | https://github.com/mpmdw/JouleWise/pull/807 |
| Requested one Sol cold seat and same-seat deltas | REFUSE solely for 2 authority conflicts; all 4 reproduced implementation findings closed | private fallback/DELTA2-REPORT.md; final manifest below |
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

## Same-seat delta 1 and second fix

The same Sol seat reviewed `3e638800cb7301b4a626cd82c5f419db9ac5e3eb`:
all three original implementation probes closed, 28 supplied tests passed.
Its verdict remained REFUSE for the two authority conflicts and one newly
reproduced P2: strict symlink resolution also rejected a legitimate partial
DELETING tree after rmtree had removed a link target before its link.

Lead disposition: fixed by checking exact link text (and every remaining entry)
against the already verified manifest during DELETING, without resolving a
link whose target may already be removed. Fresh-source manifests still require
resolvable canonical internal links. Regression tests cover both partial-delete
resumption and fresh dangling-link refusal. No new files or changed entries
can pass the subset comparison, and removal never follows links.

The builder also tightened the current invocation's copy flag for pending
transactions: an earlier cloud-only transaction no longer bypasses a later
`--no-cloud-only-allowed`. Its new regression proves the stricter run preserves
the original/archive and a later explicitly allowed run can resume. The final
record reflects the current invocation's copy policy and observed prior marker.

Final local checks: Python 3.14, 31 focused tests PASS in 22.884 s; Python 3.13,
75 focused/state cases PASS (21 zstd-dependent skips) in 4.574 s. State/kernel,
CURRENT and diff checks are repeated before this fix commit. No MBP contact.

| run_id | role/model/wrapper/session | prompt sha256 | output sha256 | disposition |
|---|---|---|---|---|
| close-offload-sol-delta-1 completed | same gpt-6.1-sol xhigh / collaboration.followup_task / /root/sol_cold_review | e4560b268a2d52a34e42716f5e6f6fda3814778d39df173aeb5b56d09e72ac09 (`review/fallback/DELTA-PROMPT.md`) | c25e09f75015f65487a6aab9bbdc625d60076730d0b64a284ccd21d3bcf26ebc (`review/fallback/DELTA-REPORT.md`) | original three code findings closed; new partial-delete defect fixed above; two authority conflicts still blocked |
| close-offload-sol-delta-2 | same seat / same wrapper / /root/sol_cold_review delta-2 | saved as `review/fallback/DELTA2-PROMPT.md` | `review/fallback/DELTA2-REPORT.md`, same stable invocation; exact hash/result read into PR #807 body | requested after this fix commit; no new cold seat |

Initial and delta-1 raw artifacts remain immutable. The final-head CI and
same-seat delta-2 result are read back into the PR body; neither an absent
review output nor a wrapper's zero exit is an admission. Production remains
blocked until both owner questions and the separate live gate are resolved.

## Final same-seat result and handoff

Delta-2 reviewed `603eae71bb1a444d464e43d4fc7285a3dab03986`. All 31 supplied
tests passed, zero skipped; 12 synthetic probes passed. The peer confirmed
partial deletion resumes when a verified target has already been unlinked,
fresh-source dangling links still refuse, current copy restrictions apply to
pending and DELETING resumptions, and completion provenance reflects the
invocation. No new material implementation defect was reproduced. The four
reproduced implementation findings across the initial review and first delta
are closed. The top-level builder independently ran the 31-case focused suite,
75-case structural/state suite, reviewed the diffs and retained final authority.

**Actual verdict: REFUSE solely for the two P1 authority conflicts.** No owner
answer arrived. This is a concrete, reviewable draft PR, not an ADMIT and not
production authority. The two pending hard start decisions keep CLOSE-OFFLOAD-01
blocked; no global stop card or operational pointer was changed. The next exact
step is the owner's answers to the two NEEDS_RULING questions above. The lead
may then revise the code or record prospective exceptions and resume this SAME
Sol seat. No new cold seat is needed or authorized by this handoff. Never merge
or contact/install on the MBP from this build session.

| run_id | parent_report / role / model / wrapper / session | prompt_path / sha256 | output_path / sha256 | status / consumed_by / disposition / commit_or_pr |
|---|---|---|---|---|
| close-offload-sol-delta-2 completed | this report / delta executing review / gpt-6.1-sol xhigh / collaboration.followup_task / /root/sol_cold_review | review/fallback/DELTA2-PROMPT.md / 3a3bbe9be6f80464f547be3fe0fe308f4afd4fa7d104a4675e17f1887ff99835 | review/fallback/DELTA2-REPORT.md / 705a548ca7227031ea98887067df996436c8aa981a5cfcdacdcaec3a1607be48 | REFUSE / top-level builder / code findings closed, authority questions to owner / 603eae71b, PR #807 |

The artifact paths remain relative to the private scratch root identified
above. They are not promoted to the public repository because raw execution
traces are private; the committed path/hash rows are the audit record. The
original failed-wrapper artifacts, initial report and both deltas are preserved.
Final-head CI, exact SHA and review hashes are copied into the PR body from
readbacks after the final records commit. That CI remains a separate required
check; green implementation tests never substitute for the missing rulings.
The PR stays draft and no merge is attempted.

## Latest intake: main advanced and RL-174 was published

Before the final handoff, the live remote main was re-read. It advanced from
`8fd5c8cc5` to `6fc02b1925b726585e66ff32885964f4207d7d09`, adding the lead's
item 376 (offload window closed) and magistrate item 377 (F0 launch). Those
operational records and their process trace were integrated into the feature
branch; only RUN_STATE's insert location conflicted. The build note is now
**376b**, below 377 and above 376, so future operational integer items cannot
collide with it. Both upstream records are preserved. No PR was merged, no host
instruction changed and no MBP was contacted. The current pointer still comes
from item 372. The code/scripts/tests/workflow tree is identical to reviewed
code head `603eae71b`; integration and subsequent records are documentation only.

Main item 376 pointed to a newly requested RL-174 D. The audit ref was refreshed
and the ruling was found at `4f4934df65e290e6bc9b744138b6a1c33222cbeb`, issued
2026-11-16 18:04 PST while this build was in progress. Its storage clauses are
now known, not absent. No claim of admission under that new contract is made.
The Sol seat's initial review/deltas were against the originally supplied
RL-173 A read set, as the owner explicitly requested.

| New clause | Required integration gap in this prototype |
|---|---|
| A.16: one backend and marker; lead picks which side changes | integrate automatic selection/newest retention with PR #804's existing `joulewise/span_offload.py` and `joulewise.span_offload_marker.v1`; do not fork another backend |
| D.1: observed evict/re-download/hash of encrypted custody | this prototype's plaintext tar.zst and evict/dataless/size confirmation are insufficient; reuse #804's ciphertext round trip |
| D.1: every arm reads no transfer pending | use #804's `pending` command in the lead's arm item; not issued here |
| D.2: packed raw may be removed, materialized archive retained | split raw deletion from final local archive eviction |
| D.2: cloud plus equal SSD receipt before archive eviction | retain compressed MBP bytes while Air/SSD away; add typed SSD receipt validation; current cloud-only eviction is not compliant |
| D.2: low-disk mail, native qualification and scheduling | lead-owned mail/key/GUI setup and live record remain separate; no native attempt made |

Read-only engineering inspection of PR #804 at
`ccfe442b628d840405a6ecac1f1805a947dabb52` found that it already implements
encryption, the supervised iCloud backend, typed marker, SSD receipt and close
shim. Its archive format, artifact layout and command arguments differ from
the explicit original build request. Its sources were inspected, not copied,
merged into this implementation or run against any live provider.

### Current NEEDS_RULING (supersedes the two older unanswered questions)

**Question:** should this task be retargeted to RL-174 D and the shared #804
backend contract, or does the owner explicitly authorize the originally
requested plaintext/nonholding/cloud-only-eviction behavior as exceptions?

**Options considered:** (1) adapt this selection/newest-kept frontend to #804,
letting the lead settle format/path/CLI compatibility; (2) preserve this reviewed
prototype only under explicit prospective owner exceptions. **Recommendation:**
option 1. The source-of-truth ruling exists, but the task's requested wire
behavior conflicts and A.16 leaves the shared-side choice to the lead.
**Blocked work:** changing the shared storage/marker contract, ADMIT, and issuance
of a standing item. AGENTS.md's contract/naming/authority early-return rule
requires this question rather than guessing. A new asynchronous question was
sent once the ruling was found; no answer has arrived.

The prior two decision dependency names are superseded by the single
CLOSE-OFFLOAD-RL174-INTEGRATION dependency; their full reasoning and review
findings remain above. This is a reviewable draft, not completion of the newly
published storage contract. Independent authorized work (implementation, focused
checks, one cold seat with deltas, current-main reconciliation and final-head CI)
is preserved. The PR body carries final SHA/check readback and this blocking choice.

## Final test-fixture hygiene

The deadline regression's fake provider grandchild now carries the unique argv
marker `jw-close-offload-fixture-provider-child-v1`. Registered it in
`tests/fixture_signatures.json` as required by orchestration's session-end fixture
census rule, with positive orphan, active-parent and non-fixture negative cases
in `tests/test_fixture_orphan_census.py`. The child code ignores this extra argv
and its heartbeat/cleanup assertion is unchanged. The focused child+signature
checks passed on 3.14 and the static signature check passed on 3.13. There is no
production offload-code delta from reviewed code head 603eae71b; only test
fixture identification and records followed. Live global observation still
returns 2 because ps is denied; no clean census is claimed. Final-head CI in the
PR body includes this fixture-registration change.
