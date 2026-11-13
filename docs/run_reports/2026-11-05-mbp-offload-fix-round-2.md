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

N5b patch 2: second applyable diff in the same patch document records pilot
measurement/ view symlinks (including dangling links) as path/type/target text.
It uses scandir metadata with follow_symlinks=False rather than os.walk, which
can stat link targets while classifying them. Regular file reads use O_NOFOLLOW
and inode/change checks. CLI --inventory and pilot-copy comparisons opt in;
model inventories stay strict. Blinded entries refuse before stat/descent.
Runbook pilot copies preserve links with cp -pRP. Exact delivered two-patch
series applies sequentially in the test's synthetic checkout.
`python3.13 -B -m unittest tests.test_align_offload_r0_patch`: PASS, 4 tests.
No R0 branch, model data, real pilot or measurement view target was accessed.

N5c: reconciled the whole runbook: current source reclaim is only class (a),
all pilot/capture trees stay until after block-5 release, conditional pilot-8
reclaim credit is withdrawn, and the earlier empty-model-tier/flat-80-GB claims
are superseded. Step 8 now exposes only the public-weights operator command;
backup work remains copy-only for retained evidence. No candidate or internal
free-space estimate is invented. Budget zero reclaim until the full census
and specific approval pass; report regular bytes and actual available delta.
External gold remains the current storage plan, with actual measured admission
still required. The public receipt contract is now step 8, not an appendix.
`python3.13 -B -m unittest tests.test_align_offload_runbook`: PASS, 3 tests;
retention/reclaim contract and all shell/Python documentation syntax checked
without executing any documented command.

## Final findings and clause map

The Git-only BYTES roster inspection at full commit
c58282f87369c73c5b0a25d8a5a217555758c6d8 names
Qwen3-Next-80B-A3B-Instruct-4bit and Qwen3.5-122B-A10B-4bit. Under the explicit
all-plans/pins ruling these identities remain KEEP, even after ALIGN drops
them. A regression test now pins that disposition. Other Next variants are
not classified here: amendment/v4 objects and a complete census are missing.
No real candidate path, model file or measurement was inspected.

Final N1 review also covers abnormal child-supervisor exit: the guard stops
surviving group members even if the group leader is already dead. This and
its regression test were folded into the single N1 commit. Unit heartbeat
writes are mocked so the low-space/unmount tests reach their intended gates.
The native synthetic guard-death tests run real isolated Python processes.

| Ruling clause | Production site | Biting assertion | Counterfactual |
| --- | --- | --- | --- |
| N5a(1), every plan/pin | model_keep.derive + delete_root.replay_census/unreferenced | disjoint Git histories, modified receipt refusal, referenced alias/path refusal | model dropped from ALIGN still present in BYTES remains KEEP |
| N5a(2), exact repo/revision and every blob | public_evidence + tree + check_hf_downloadable | full-SHA, manifest, mapping and link tests | revision=main, changed blob or snapshot link refuses |
| N5a(3), fresh HEAD | check_hf_downloadable at final deletion gate | API and per-file HEAD URL/method/no-auth checks | missing/gated revision or file refuses before rmtree |
| N5a(4), specific Ed list | public_evidence | exact JSON claim equality | changed source/revision/list or another approver refuses |
| N5a, relax only exact model containment | check_keep(public_path=src) | mandatory root, other KEEP and another-path tests | approved source's root/sibling/descendant KEEP cannot be removed |
| N5b, W1 two copies + floor | R0 patch 1 required_free_bytes/disk_census | exact boundary +/-1 byte; malformed/null citation/budget tests | old flat threshold and missing amendment budget cannot pass |
| N5b, record view link text | R0 patch 2 inventory/CLI | dangling/view target text, only regular local file opened | no target descent; default model inventory still refuses links |
| N5c, pilots/capture trees stay | delete_root common retention + runbook step 8/9b | all-pilot and instrument_validation refusal, public-only operator command | conditional pilot-8 reclaim credit removed |

## Final verification

Each unittest command ran sequentially, one module at a time; no full suite.
All use Python 3.13 and synthetic filesystem fixtures. Latest results:

| Command | Result |
| --- | --- |
| `python3.13 -B -m unittest tests.test_align_offload_disk_guard` | PASS, 7 tests, 0.905 s |
| `python3.13 -B -m unittest tests.test_align_offload_delete_root` | PASS, 49 tests, 0.351 s |
| `python3.13 -B -m unittest tests.test_align_offload_model_keep` | PASS, 4 tests, 2.740 s |
| `python3.13 -B -m unittest tests.test_align_offload_public_weights` | PASS, 13 tests, 0.131 s after final BYTES-reference regression |
| `python3.13 -B -m unittest tests.test_align_offload_r0_patch` | PASS, 4 tests, 0.092 s |
| `python3.13 -B -m unittest tests.test_align_offload_runbook` | PASS, 3 tests, 0.649 s; all current zsh fences and Python heredocs parse |
| `python3.13 -B -m unittest tests.test_docs_freshness` | PASS, 31 tests, 1.360 s after final documentation changes |

Total: 111 targeted tests, all passing; cumulative iterations far below
20 minutes. Compilation command also PASS (exit 0):
`PYTHONPYCACHEPREFIX=/private/tmp/jwsol/mbp-offload-4/tmp/compile-cache python3.13 -m compileall -q joulewise tests scripts/align_offload_delete_root.py scripts/align_offload_disk_guard.py scripts/align_offload_model_keep.py`.
`git diff --check 43ce366556423eb2ff8be273af9caa83ec3d4138` PASS.
Protected-path diff against base is empty for RUN_STATE.md, TASK_QUEUE.md,
docs/process/state_kernel.json and tests/test_gen_state.py. No tasks registered.

## Changed files and local commits

Changed: scripts/align_offload_disk_guard.py, align_offload_delete_root.py,
align_offload_model_keep.py; their three existing test modules; new
tests/test_align_offload_public_weights.py, test_align_offload_r0_patch.py,
test_align_offload_runbook.py; docs/align/mbp_offload_and_gold_setup.md,
r0_disk_gate_patch.md; this report. No R0-branch file changed.

Local commits are one per review item, with N5 split into its requested
public-policy, two R0 patch-series, and retention/documentation pieces.
Local commit inventory (the N5c commit containing this final report is HEAD):

- 2e44820d1 — N1 guard lifetime and signal safety.
- 9b4fc4b7c — N2 validated journal.
- 77caa147a — N3 closed upload parser.
- d6c338f40 — N4 protected flags.
- e9fa8920e — N7 executable census.
- e2f1c1b78 — N6 multi-ref Git census.
- 923c8ae04 — N5a public-weights deletion policy/tests.
- 740003268 — N5b patch 1, disk gate.
- 6863e8e5f — N5b patch 2, symlink inventory.
- HEAD — N5c current reclaim/retention reconciliation and final handoff.

No push.

## Limits, open questions and exact next step

No network, real data/model inventory, source deletion, offload, release,
harvest, analysis pipeline, hardware measurement or native MLX execution.
No paths under /Users/edr outside this clone were intentionally accessed;
Git object reads through the expressly allowed shared alternate supplied only
repository code/plan/registration text. Synthetic restricted directories in
TMPDIR contained no study data. No raw evidence/run bundle was modified.

Remaining operational gates, not silently completed:

- Lead supplies locally available full SHAs for amendment 1, ALIGN v4 kit and
  v4 R0 config. Current cached refs lack them. Full census must pass from Git
  objects; no merged checkout or inferred model path substitutes. The two
  BYTES-listed expected candidates above remain KEEP under the given rule.
- Lead records the actual amendment W1 per-copy bundle bytes and full citation
  in a reviewed v4 R0 config. Delivered patches verify the formula/types and
  citation shape, not semantic extraction of a number from unavailable prose.
- Ed captures the real step-5 successful fileproviderctl sample and tool/macOS
  version; lead reviews and commits its exact grammar/sample digest. Until
  then all operational cloud upload checks deliberately refuse.
- Ed's exact public-model list/manifest/revision approval and successful
  deletion-time unauthenticated HF HEAD checks are still required. Live API
  HEAD/redirect behavior is unverified; any unsupported response refuses.
  Freed here: 0 bytes; no eligible model list or real capacity is claimed.
- R0 lead rebases/applies the two delivered patches to #661's reviewed v4
  source, runs its native config/disk/inventory tests and then the approved
  operator inventories. Guard native process-state T checks for SIGHUP,
  SIGKILL and worker groups should run on the target Mac: /bin/ps was denied
  here, so these tests establish live-but-nonexecuting synthetic writers.
  Model/R0/MLX and real iCloud/hardware validation remain outside this sandbox.

Next exact step: lead reviews these local commits, resolves the missing Git
pins/plan budget and coordinates the two documented patches with #661.
Preserve the pause and pilot roots; follow the existing Ed-only handoff only
after the recorded parser, census, disk and specific-approval gates pass.
No new independent SAFE verdict is claimed by this implementation run.
