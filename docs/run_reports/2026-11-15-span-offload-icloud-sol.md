# PR #804 cold executing software review

Completed 2026-11-15 19:46 PST (2026-11-16 03:46 UTC).

Candidate: `da02b7fdeca60bbbd933e7f3b5d679a6418464b6`, matching fetched
`origin/ops/2026-11-15-air-independence`. Comparison points:
`b9d688207` for the iCloud delta and fetched `origin/main`
`06841229cde15a890c3362c3fdaac361729938bd` for the full PR.

This was an independent cold executing seat. I did not build the candidate and made no
tracked-file changes. The detached checkout is
`/Volumes/JW-EXT/scratch/sol-offload-icloud/review/tree`; all authored probes, logs and
temporary fixtures are under the adjacent `tmp/`. No commit, push or merge of the
candidate occurred. No MBP contact, SSH, real brctl/iCloud operation, custody file,
energy file, journal or CloudDocs database access occurred. Git fetch and detached
worktree creation used the expressly authorized accessible metadata in
`/Volumes/JW-EXT/jw-wt/mythos-repo`.

The requested shell launcher was reported to have failed before this seat started because
nested sandbox-exec was prohibited. This authorized fallback inherited the existing OS
blinding. I did not retry a nested sandbox, change permissions, weaken the sandbox, or
use sandbox/approval bypass flags.

## Read set and scope

Read the complete 1,569-line library, 128-line CLI, 1,406-line offload test module,
250-line runbook and CANONICAL entry. Reviewed the full tool and the code delta from
`b9d688207`; inspected the builder's RUN_STATE, TASK_QUEUE, report and test-timing
bookkeeping. Intake included CANONICAL, current highest RUN_STATE item, CURRENT.json,
POINTER_RULE, Mission M0 and orchestration; the state kernel had no active stop card.

Read RL-173 section A verbatim from
`f35483d41:docs/research-audits/2026-11-10-fable/RESEARCH-LEAD-DECISIONS.md`, and
RUN_STATE items 347 and 350 from fetched origin/main, including item 347's full commands.
Those are authority text, not live-data validation. No policy was re-decided.

## Execution and evidence

Environment: `/opt/homebrew/bin/python3.13` 3.13.18, macOS 15.8.3 arm64,
real LibreSSL 3.3.6. Python ran with `-B` and `PYTHONDONTWRITEBYTECODE=1`.
`TMPDIR=/Volumes/JW-EXT/scratch/sol-offload-icloud/review/tmp` throughout execution.

Setup commands:

```sh
git -C /Volumes/JW-EXT/jw-wt/mythos-repo fetch origin
git -C /Volumes/JW-EXT/jw-wt/mythos-repo worktree add --detach \
  /Volumes/JW-EXT/scratch/sol-offload-icloud/review/tree \
  da02b7fdeca60bbbd933e7f3b5d679a6418464b6
```

From the detached checkout:

```sh
env TMPDIR=/Volumes/JW-EXT/scratch/sol-offload-icloud/review/tmp \
  PYTHONDONTWRITEBYTECODE=1 /opt/homebrew/bin/python3.13 -B -m unittest \
  tests.test_span_offload tests.test_docs_freshness tests.test_git_fixture_maintenance
```

Result: **104 tests passed in 35.317 s**. Raw output: `tmp/focused-tests.log`.
The supplied fake brctl executable ran on PATH; rclone calls used the supplied fake.
All span inputs were synthetic bytes. All dataless observations were explicit fakes.

Independent probe command:

```sh
env TMPDIR=/Volumes/JW-EXT/scratch/sol-offload-icloud/review/tmp \
  PYTHONDONTWRITEBYTECODE=1 /opt/homebrew/bin/python3.13 -B \
  /Volumes/JW-EXT/scratch/sol-offload-icloud/review/tmp/independent_probes.py
```

Result: **21 independent probes passed**, recorded in `tmp/independent-probes.log`
and `tmp/independent-results.json`; executable source is retained in
`tmp/independent_probes.py`. These probes do not import the supplied test helpers.
Their fake brctl preserves placeholder file length and tracks synthetic dataless
state by inode in scratch files, so eviction observation does not depend on a
zero-length-file assumption. `_is_dataless` is explicitly replaced in both the main
probe process and the signal-test CLI child. No actual file flags are set.

| Probe | Observed consequence |
|---|---|
| Success; pending status followed by idle/caught-up | Exit 0, four matched hash/size confirmations, byte-identical Air pull |
| Status stays pending | Exit 5 DEADLINE; neither marker |
| Evict exits 0 without a dataless observation | Exit 8; only `.ok.unconfirmed` |
| Download exits 0 but leaves the placeholder dataless | Exit 8; only `.ok.unconfirmed` |
| Download fails | Exit 8; only `.ok.unconfirmed` |
| Download truncates or corrupts bytes | Exit 5 READBACK_HASH; neither marker |
| One of four confirmations unavailable | Exit 8; no `.ok` |
| Retry after upload/status timeout | Reuses identical staged ciphertext; then exit 0 |
| Retry after another unconfirmed attempt | Exit 3; no `.ok` (finding 1) |
| Existing foreign remote bytes | Exit 5 REMOTE_CONFLICT; foreign bytes unchanged |
| Linked iCloud ancestor; linked plan; hardlinked or symlinked object | Exit 5 BACKEND_PATH; zero provider calls; source unchanged |
| Staged ciphertext changes during provider readback | Exit 5 STAGE_CHANGED; neither marker |
| Another writer creates the final marker | Exit 3; first writer's bytes preserved |
| SIGTERM during status, SIGHUP during eviction, SIGINT during download | Exit 5; fake brctl child reaped; no `.ok`; no private build/key temp directory |

`git diff --check origin/main...HEAD` passed. Final `git status --porcelain=v1` was
empty. The requested broad quick tier and full suite were deliberately not run:
the brief assigns those to GitHub Actions because this seat's OS blinding denies
canonical custody paths, including `/restricted/` synthetic fixtures in legacy tests.
This report makes no claim about final GitHub CI completion.

## Numbered findings

1. **SHOULD-FIX — repeated unconfirmed attempts share the confirmed-marker exit code.**
   `joulewise/span_offload.py:1217` maps any marker collision to `marker_exists`;
   `:1335` also uses that writer for `.ok.unconfirmed`. A no-op eviction therefore
   gives exit 8 first and exit 3 on the second identical attempt, while `<plan>.ok`
   remains absent. Independent probe `repeat_unconfirmed` records
   `OFFLOAD_MARKER_EXISTS MARKER_EXISTS another writer created the marker first`.
   The supplied `test_cli_exit_codes_and_one_line_output` also expects this behavior
   for the local backend. It is inherited behavior that now reaches the production
   iCloud path. The close-step text at `docs/ops/SPAN-OFFLOAD.md:238` treats exit 3
   separately from failures and does not explicitly require that the existing
   marker be `.ok`, so a controller implementing that prose could misclassify it.
   **Consequence in the reviewed tool:** misleading retry classification only;
   the return code is nonzero and no false-success `.ok` appears. This is not a
   standing software blocker under the brief's consequence rule.
   **Suggested fix:** preserve the existing unconfirmed record without clobbering
   it, return exit 8 for an unconfirmed-record collision, and explicitly require
   an existing `<plan>.ok` before treating exit 3 as a satisfied copy gate.

2. **NOTE — provider evidence and failure behavior satisfy the software contract in
   the permitted synthetic model.** The four artifacts use exclusive temporary
   names, fsync and rename; iCloud directory components use openat/O_NOFOLLOW;
   artifacts reject non-regular files and multiple hardlinks. Status polling has
   subprocess and overall deadlines. A successful command exit alone cannot
   confirm eviction. Downloaded sha256 and byte count must equal the staged
   snapshot, and a single unavailable readback permanently downgrades the run.
   Marker publication is atomic and does not clobber the first writer. The per-plan
   lock, immutable stage reuse, public-key snapshot/pin, bytes-only archival and
   OPENSSL_CONF isolation remain intact. Source manifests were unchanged in the
   independent success and refusal probes. The trusted-control-root assumption in
   the brief remains necessary: comprehensive component-by-component link checks
   are on the iCloud destination; this is not an assertion of universal hostile
   ancestor-swap resistance across every control path.
   **Suggested action:** retain those checks and the install-time root provisioning;
   no change is required by this finding.

3. **NOTE — bookkeeping and documentation preserve the external gates.** CANONICAL
   names iCloud as the default production route and explicitly retains pending
   macOS 26 qualification. The runbook needs no new Google/rclone provisioning,
   names bird/cloudd/fileproviderd, and directly asks the research lead whether
   iCloud with evict+redownload readback is permanent under A.3. RUN_STATE's builder
   note and TASK_QUEUE's historical checkpoint report pending review/CI without
   replacing the measurement pointer or selecting a generated queue task. The
   timing entry records unknown hosted timing rather than fabricating a CI weight.
   **Suggested action:** after consuming this report, the lead should disposition
   finding 1 and update the pending-review/CI records at the actual final head.

There are **no standing BLOCKING software findings**.

## Policy and live limitations; next exact step

This software seat does not decide A.3's permanent-tool classification. CloudDocs
daemons remain asynchronous; the maintenance line remains required pending the
research lead's ruling. No live macOS 26 brctl syntax, status format, eviction,
SF_DATALESS transition, provider durability or production-key round trip was
qualified. A.1's actual off-MBP key custody, including the interim offload.key
second-copy duty, was not inspected or discharged. Source originals must remain
until the owning second-location gate is met.

The lead's next exact step is to consume and disposition this report, verify final
GitHub Actions results on `da02b7fdeca60bbbd933e7f3b5d679a6418464b6`, and record the
software review outcome. Any later software change needs the applicable delta
verification. Live qualification remains the runbook's separately authorized synthetic
MBP-to-iCloud-to-Air round trip on macOS 26 with production keys and four observed
readbacks. The research lead owns the separate A.3 permanence question. This admission
is not merge, installation, measurement, key-custody or policy authority.

VERDICT: ADMIT
