# PRUNE P2 preparation — 2026-11-05

Task: A346 / FREEZE-BY-COMMIT-01 Phase 2. Requested branch:
`lane/2026-11-05-repo-prune-p2`. Starting checkout was clean, detached at
`92026c1849c0f053e56bdac6110c079211db2c31`.

## Outcome

Prepared [the eight-stage plan](../process/repo_prune_plan_2026-11.md) and
[measured inventory](../process/repo_prune_inventory_2026-11.json). Stage 1
identifies five orphan diagnostic scripts, 2,534 lines / 91,728 bytes. Their
current hashes match the collection sealed inventory; no code/test or named
CI/infra consumers were found. They are still present and unchanged.

**Implementation, branch creation and local commits are blocked. No deletions,
commits, push, tags, history rewrite or external integration occurred.**
RUN_STATE item 167 and the owning freeze-by-commit plan require the release and
Phase 1 first; this checkout contains no verified completion evidence. The
environment also makes `.git` read-only and this clone's history is borrowed
from an external directory forbidden by the user's blinding boundary.

The current tracked tree is 13,009 files / 375,553,491 bytes, including 725,536
physical source lines in 913 eligible files. Thirty largest current tracked
blobs and per-directory measurements are in the plan. Sizes of records/data
come from metadata; their content was not opened for counting. Code LOC excludes
records, fixtures, analysis outputs, JSON, Markdown and HTML. It is not directly
comparable to TRIM_REPORT's historical all-blob newline count.

Larger prospective cuts remain decisions/migrations: 33,256 lines of arm/T-0
source plus 151,201 lines of test referrers; the latter cannot be deleted as a
group. Four of five provisional remote modules remain reachable in the current
conservative graph. `spike_mlx_prompt_cache`, `gen_gsm8k_scored` and
`gen_jw_mixed` have surviving test consumers. Mint v1 is loaded by generalized
mint. These observations prevent treating the historical inventory as a
literal deletion manifest.

Retain 83,144,895 bytes of legacy records, 157,013,233 bytes of process traces,
and 728,362 bytes of `.codex-report` material pending per-path authority. The
trim report §7 / D-111 / RUN_STATE evidence policy protect them. No tracked
`.codex-bridge` files were found. Generated site output is 1,566,398 bytes,
but has builder/test consumers and needs the owning lane's decision.

## Boundary incident and Git limitation

Initial `git log`, tag and revision queries were issued before noticing
`.git/objects/info/alternates`. They used
`/Users/edr/jw-b5-analysis/.git/objects`, crossing the user's allowed filesystem
boundary through Git. This was a session error. No measurement-file content
was requested, and no data/analysis pipeline was run. The external path was
subsequently treated only as text and never deliberately followed.

After discovery, Git calls used `GIT_OBJECT_DIRECTORY` pointing to
`/private/tmp/jwsol/prune-p2/tmp/local-objects`, copied only from the clone's
local two-hex-digit object directories, and empty
`GIT_ALTERNATE_OBJECT_DIRECTORIES`. The isolated store cannot resolve HEAD,
its tree or `b5/analysis-r2`. Branch creation there returned
`fatal: You are on a branch yet to be born`; that reflects missing objects,
not a claim that the original repository has no HEAD. Isolated `git status`
likewise reports `fatal: bad object HEAD`.

Attempting to create a local object-store directory inside `.git` returned
`Operation not permitted`; the environment declares `.git` read-only. No
permission/sandbox bypass or network repair was attempted. Initial
`git count-objects -vH` reports 27 local objects / 308 KiB, zero packs, plus
the alternate; total historical storage cannot be inferred from that figure.
The initial tag commit queries are recorded in the plan, but annotated objects
and tree hashes could not subsequently be verified within the boundary.

## Files changed

- Added `docs/process/repo_prune_plan_2026-11.md`: paths, measured context,
  preservation tags, risk, keep lists, NEEDS-ED decisions and projections.
- Added `docs/process/repo_prune_inventory_2026-11.json`: compact measurements,
  blob IDs, candidate manifests, source references and conservative closures.
- Added this report.
- Updated A346's status note in `docs/process/state_kernel.json` and regenerated
  `TASK_QUEUE.md` with `scripts/gen_state.py`. The task remains queued.
- Added one side-lane preparation note to `RUN_STATE.md`; its existing
  operational/measurement handoff was preserved.

No advisor-visible scientific state changed, so `PROJECT_STATUS.md` was not
updated. No delegation or peer consult occurred: offline scope and the read-only
planning work did not need one. Independent executing review remains a landing
gate for a later deletion PR; it is not claimed here.

## Verification

Tests used system Python, `PYTHONNOUSERSITE=1`,
`PYTHONDONTWRITEBYTECODE=1`, `PYTHONPATH=.`, task-local `TMPDIR`, and isolated
Git storage. No full suite or discovery ran. Only one targeted test file ran;
its serial generator subprocesses stayed within the two-process test ceiling.
The two successful test runs took 6.958 seconds total.

| Command/check | Result |
|---|---|
| `python3 -m pytest tests/test_gen_state.py -q -x` | Exit 1: `No module named pytest`. No pytest collection/execution. Also unavailable in system 3.13 and `/usr/bin/python3`; no venv present, no installation attempted. |
| `python3 -m unittest tests.test_gen_state -q` (before notes) | 44 passed, 3.575 s. Targeted stdlib fallback. |
| Same command after regenerated notes | 44 passed, 3.383 s. |
| `python3 -I -B scripts/gen_state.py --check` | Exit 0 before and after regeneration. |
| `python3 -I -S -B /private/tmp/jwsol/prune-p2/tmp/import_smoke.py` | 171/171 non-CLI package modules imported. All 172 package sources compiled; `joulewise.__main__` was excluded from import because it executes the CLI. |
| Source/AST inventory | 845 Python source files parsed; no tests collected through full discovery. |
| Final Git blob identity check against index | All 913 eligible tracked source files match their original index blob IDs; 725,536 source lines unchanged. All five Stage-1 SHA-256s still match. |
| Inventory arithmetic | Directory file/byte/LOC totals and Stage-1 counts cross-checked. |
| Final coordination diff | Reconstructed originals of the three changed tracked files hash exactly to the index OIDs; reviewed their diffs without historical Git-object access. |

The import harness used isolated Python startup, a fixed safe temp directory,
source-only opens, explicit out-of-root/restricted boundary guards (including
stat/lstat/access/readlink), and subprocess/network denial. It permits normal
system native-library loads. Preliminary attempts rejected ctypes initialization
and tempfile's default-directory write probe; correcting the harness gave the
successful result above. These were guard restrictions, not code defects.
Nested OS `sandbox-exec` could not be applied (`sandbox_apply: Operation not
permitted`); Python guards are bounded import evidence, not an OS security proof.
No import invoked a CLI, analysis pipeline, hardware probe or measurement.

The one-off inventory, import and diff-review scripts are under the task-local
temporary directory. The durable JSON records their method and results; static
closures are from this worktree, not verified historical tag trees. Current
source evidence does not prove absence of reflective/external CLI consumers.

## NEEDS-ED / next exact step

The plan enumerates NEEDS-ED-01 through NEEDS-ED-11. The immediate blockers are:

1. Cite the completed block-5 release/recompute and Phase 1 landing gates.
2. Provide a writable, self-contained clone whose objects are within its allowed
   root; then create the requested branch and verify tag commit/tree/blob facts.
3. Confirm Stage 1's five tools have no owning-lane/personal CLI consumer.

An asynchronous question offered preparing Stage 1 as an unapplied patch; no
answer arrived during this work. No pending answer was treated as permission.
No patch or deletion was produced. With those questions resolved, the lead
creates the annotated preservation tag, applies exactly the five Stage-1
deletions, repeats focused checks on the resulting tree, and commits locally.
Proposed commit: `prune: retire isolated AXI and diagnostic one-shot scripts`.

Uncertainty: later net savings, test retirement subsets, actual tagged release
closure, owner adoption of the GPU stack, stored-format requirements and total
history size remain unverified. All projections in the plan distinguish those
uncertainties from measured facts. No hardware/scientific validation is claimed.
