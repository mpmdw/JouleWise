# MBP offload fix round 2 — 2026-11-05

Base 43ce366556423eb2ff8be273af9caa83ec3d4138, branch
`lane/2026-11-05-mbp-offload-runbook`, initially clean. Explicit task authority
overrides coordination closeout: no RUN_STATE, TASK_QUEUE, state-kernel or
test_gen_state edits, task registration, network, real measurement reads,
analysis execution, full suite or push. All filesystem tests are synthetic.

N1: termination handlers stop the writer group; a child supervisor detects
guard death through private-pipe EOF (including SIGKILL), or a stale heartbeat
after 15 seconds, and self-SIGSTOPs the group. The actual writer is its child.
Runbook requires tmux, caffeinate and keeping Terminal open. Targeted command
`python3.13 -B -m unittest tests.test_align_offload_disk_guard`: PASS, 6 tests,
1.346 s. Real synthetic subprocess tests kill guards with SIGHUP and SIGKILL;
the writer remains alive and its 20 ms execution counter stops advancing.
Sandbox denies /bin/ps, so the test uses that observable stopped execution,
not a native process-state query. Lead should repeat on the Mac and confirm
state T for supervisor, writer and workers. Initial test iteration exposed
the ps sandbox restriction and mocked-pipe BrokenPipe; both tests corrected.
No stopped production group or real writer was involved.

N2: journal validation precedes all audit paths: exact item.parent and
`deletions.tsv`, regular non-symlink, nlink 1; open uses O_NOFOLLOW, O_APPEND,
O_CREAT, and fstat/lstat identity is rechecked before each write. Invalid
journals receive no refusal row. Tests preserve exact KEEP bytes for symlink,
hardlink and a link substituted during open, and reject wrong parent/name.
`python3.13 -B -m unittest tests.test_align_offload_delete_root`: PASS,
45 tests, 0.721 s.

N3: all upload decisions now use one exact-output parser, including shell
jw_uploaded. No real step-5 fileproviderctl sample is available here, so its
sample/digest pins are unset and every operational check refuses. Step 5 now
captures stdout/stderr/digest and requires a reviewed parser commit before
continuing. Synthetic-only parser tests cover pending uploads, any error,
conflicts, unknown keys/format, duplicate keys and misleading uploaded values.
`python3.13 -B -m unittest tests.test_align_offload_delete_root`: PASS,
46 tests. Operational cloud deletion remains BLOCKED until the lead records
and pins the real sample; no synthetic fixture is represented as live output.

N4: LOCK_FLAGS additionally rejects SF_NOUNLINK (0x100000), SF_RESTRICTED
(0x80000), UF_DATAVAULT (0x80). Synthetic stat tests exercise every protected
bit independently and assert refusal before ACL execution.
`python3.13 -B -m unittest tests.test_align_offload_delete_root`: PASS, 47 tests.
Native privileged flags are not set by these tests.

N7: deletion and pause bootstrap share `census`, using ps pid/comm only and
full executable basename matching (plus the Claude versioned executable
spelling). No argv is requested, matched or exported; `--item harvest...`
cannot trigger a false positive. Synthetic tests cover named executables,
benign executable paths containing harvest/tar directory tokens, and the exact
ps field request. Interpreted scripts whose comm is only Python require the
external no-writer/launcher gates too; comm is not an argv script census.
`python3.13 -B -m unittest tests.test_align_offload_delete_root`: PASS, 48 tests.

N6: replaced working-tree reads with six independently reviewed Git-ref roles:
main, BYTES c58282f87, B6 dda456f98, ALIGN v4, amendment 1 and v4 R0 config.
All identity pins/rosters plus explicit B6 §1.4, kit and plan/config blobs use
git show at resolved full commits. Receipts carry role/ref/commit/path/digest,
source paths and conservative model aliases. Real model paths stay inert.
Synthetic disjoint orphan histories prove no merged checkout is required;
working-copy poison/symlinks have no effect, Git symlinks and missing inputs
refuse. `python3.13 -B -m unittest tests.test_align_offload_model_keep`: PASS,
4 tests. Cached council 219fb1515 lacks amendment 1; kit 8d1ab6e2c has only
v0–v3; R0 49e78e178 still names Next-80B. Asked for locally available reviewed
v4/amendment SHAs; no source revision, candidate list or plan value fabricated.

N5a: added delete_root --model-class public-weights. Exact per-item Ed approval
binds path, every-file blob manifest, repo id/full revision, replayable six-ref
census and file-to-HF mapping. It skips only the containing mandatory model
root's overlap; every other KEEP overlap and common deletion guard remains.
Cloud-copy proof is replaced by public reproducibility proof: unauthenticated
operator-time HEAD of the exact API revision and every mapped file. No call
was made here. Independent review, retention, ACLs/flags, pause/census/floor,
source recheck, validated journal, pointer and partial-failure behavior remain.
All pilot roots now refuse pending block-5 release, including pilot 8. Test
fixtures for archived-class success now use an explicitly approved non-pilot
source. New tests cover exact approval, reference aliases/paths, missing census,
root/other KEEP protections, blob-only files, source mutation, HF failures and
HEAD URL/method/no-auth. Deletion reports regular bytes and measured available
space delta separately. Actual source deletions/freed bytes here: NONE / 0.

`python3.13 -B -m unittest tests.test_align_offload_delete_root`: PASS, 49 tests.
`python3.13 -B -m unittest tests.test_align_offload_public_weights`: PASS, 12 tests.
These are synthetic tests, not HF availability or model eligibility validation.

N5b patch 1: docs/align/r0_disk_gate_patch.md carries a reviewable diff against
R0 49e78e178, not edits to that branch. Gate = reviewed amendment-1 W1 bytes
per copy * 2 + 30,000,000,000. Config requires two copies and full amendment
SHA:path citation; old/missing/null budgets refuse. The numeric plan value is
not available here and remains an explicit R0-lead review gate. The example
intentionally refuses rather than inventing a value. Runbook formula updated.
`python3.13 -B -m unittest tests.test_align_offload_r0_patch`: PASS, 2 tests;
exact shipped patch applies to cached code, synthetic boundary +/-1 byte and
missing/malformed inputs tested. No R0 or model/hardware probe executed.
