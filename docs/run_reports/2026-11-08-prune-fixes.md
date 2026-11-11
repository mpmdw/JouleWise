# Prune-plan cold-review remediation

Task branch: `ops/2026-11-08-prune-fixes`, created from
`ops/2026-11-08-prune-plan` at `7cce18c15`. Date follows the assigned brief.
Cold review: `b7151f058a49eccae6633f9f6d4cfb0457a01076`,
`docs/ops/prune-plan-opus-review.md` on the locally recorded review ref.
Verdict applied: **ADMIT_WITH_FIXES**. This is planning/tooling work, not cleanup.

## Authority and scope

Read AGENTS/CLAUDE, Mission M0, generated stop-card/restart and current queue,
manual Do-Not-Do-Yet, project/workspace/next pointers, orchestration,
freeze-by-commit and D-188–D-190. No active stop card. The direct PI assignment
is bounded `[AGENT]` remediation; no kernel task was registered. The explicit
brief overrides the usual coordination-state writes and full local suite.
RUN_STATE, TASK_QUEUE, state kernel, tests/test_gen_state and advisor-visible
status were left unchanged. Intake tree was clean; no unrelated work existed.
No subagents or cross-model consult were launched; the supplied Opus review
is the external review input, not a new final-head review or merge approval.

## Review dispositions

| Finding | Change supplied | Remaining execution evidence |
|---|---|---|
| HIGH-1 alternates | Air checklist maps owners/borrowers, unpushed commits, auto-GC hold, repack without --local and isolated fsck. Corrected handoff to self-contained; analysis store still backs ~14 clones and must survive until borrowers are repacked | Ed's fresh authorized metadata graph; no machine inventory here |
| HIGH-2 sync deletion | Exact source path and proof it is outside every synced tree; cloud re-download/checksum check from another device/session | Owner receipts |
| HIGH-3 borrowed SSD | Explicitly never an independent retention copy; two durable independent destinations required | Owned/Air/independent-cloud copy verification |
| HIGH-4 tag publication | One Ed-created tag ruleset, admin-only creation, update/deletion protection, explicit tag push, ls-remote comparisons of tag-object and peeled IDs, ruleset JSON | Ed installs/exports ruleset and verifies server objects |
| HIGH-5 branch consumers | Separate real test commit requires immutable 9b reference and fails when missing; committed candidate-name grep covers main/HOLD code, tools, tests, configs, CI and registrations | Land test fix; refresh and disposition each hit before deletion |
| HIGH-6 ephemeral scripts | Four committed offline scripts under scripts/ops, with synthetic unittest coverage and one-command refresh | Release-day refresh after fetch |
| MED-1 missed pins/scope | Main + every HOLD source tip; deeper docs and tools; listed ALIGN/port/BYTES/#704/audit-burn pins; receipt analysis/oracle/comparator/recompute/release checkout roles; 498ad1d0 marked server-existing/unfetched; history-reader inventory expanded | Actual receipt roles, PR-head fetch, missing-history dispositions |
| MED-2 archive row | Corrected to recorded main c07b388e9; refresh takes explicit archive SHA/date and verifier refuses stale main/row | Fresh release-day main before creation; never move an existing tag |
| MED-3 review provenance | Per-tag evidence table; exact-SHA PR/check results, tag-object ID, ruling allowlist/evidence digest and optional signer authentication in future contract | PR/check JSON is PENDING, not invented offline |
| MED-4 weights | Shared Air/MBP model-cache KEEP inventory covering upstream revision, local path/digests, conversions and live working sets; verified durable second copy required | Owner-populated cache/copy receipt; no weights accessed/downloaded |
| MED-5 ledger | Named magistrate gate to recover 4cb222a19 to records/b5-ledger-final plus pin/b5-ledger-final, verify server and restore both bundles before any MBP cleanup | Magistrate/lead recovery outside this task |
| LOW-1 rollback | Header-only PRUNE-ROLLBACK.tsv; committed INTENT before deletion, outcome after, exact restoration command | No deletion rows because nothing was deleted |
| LOW-2 freshness | Fetch --prune immediately before tip checks, with exact lease deletes; verify rejects new/removed/moved local remote refs | Later connected owner session |
| LOW-3 removable worktrees | Lock SSD worktrees; no worktree prune with detached volumes | Owner inventory |

Adopted proportionality: **33 named anchors**, reusing existing scientific tags;
no per-citation tag factory; fresh GitHub mirror including explicit PR-head
fetch, complete `git bundle create --all`, two independent durable copies,
merged-only batch 1, protected whole-tip archive tag for later unmerged retirement.
This retains more than per-citation tags: uncited HOLD-tip work is in the complete
backup and must be tagged before that tip is retired. Prior archive branch/tag
promise remains intact. No frozen B5 computation or registered digest changed.

## Files supplied

- `tests/b5_analysis/test_result_equivalence.py` — immutable D-189 reference,
  required before the optional r1 skip can run.
- `scripts/ops/prune_inventory.py`, `prune_verify.py`, `prune_branch_names.py`,
  `prune_refresh.py` — offline Git/source census, freshness/topology validation,
  fixed-string name grep, and one-command output refresh.
- `tests/test_prune_ops.py` — tiny synthetic Git histories; off-main pins,
  doc/tools scope, excluded payloads, numeric false positives, whole-tip
  retention, stale archive/tips newly added remote-ref refusal, shared-prefix literal matching, and the
  one-command CLI.
- `docs/ops/PRUNE-PLAN.md`, `PIN-INVENTORY.md`, `TAG-PINNING.md` — revised
  procedure, scope/source map and future review-preserving identity contract.
- Ops TSV/JSON snapshots and evidence/rollback templates — see inventory for
  exact roles and the census result appended below.

## Verification and limits

| Command/check | Result |
|---|---|
| `python3.13 -B -m unittest tests.b5_analysis.test_result_equivalence` | PASS, 98 tests in 47.076 s, 2 skips |
| Missing-reference probe using unittest.mock on `_git_show` for R1_FIX_TAG only | PASS: exactly one assertion failure, no error/skip; missing tag cannot silently weaken the guard |
| `python3.13 -B -m unittest tests.test_prune_ops` | PASS, 11 tests in 9.843 s |
| `python3.13 -B -m unittest tests.b5_analysis.test_frozen_files` | PASS, 4 tests in 0.363 s |
| `python3.13 -B -m unittest tests.test_b5_seal_landing` | PASS, 9 tests in 3.208 s |
| Python 3.11 grammar parsing of new scripts/tests; shell-block bash -n; local Markdown links | PASS |

The equivalence skips require explicit synthetic S10 input environments
`JW_B5_EQ_SYNTHETIC_PAIRS` and `JW_B5_EQ_REMINT_SOURCE`; neither is a missing-tag
skip. The D-189 reference test ran successfully. Test modules ran one at a time;
combined test time, including development reruns, stayed far below 20 minutes.
No full suite, pytest, analysis pipeline, quiet-window capture or hardware
validation ran. Full CI is still required before merge, off this busy machine.
No MLX code changed; no new native Metal test is required for this remediation.
Later runtime/file-retirement PRs still owe their own native gates outside this
sandbox. Python 3.11 was grammar-checked, not runtime-tested here.

Development checks caught a missing archive tag in the tiny test setup and a
numeric fixture token that coincidentally resolved to a real commit. The setup
was fixed; numeric-only citations now require explicit context, fixture data
payloads are excluded before reads, and every remaining source blob is indexed
once. Several exploratory census/grep runs were interrupted while improving
performance; only the final completed snapshot is delivery evidence. Those
intermediate outputs are not authoritative inventories; task-generated files
from the two superseded scratch censuses were removed after final verification.
The early broad Git scan included tracked legacy fixture traces. Their
synthetic-versus-live provenance was not established; this is an explicit
uncertainty and the reason for excluding fixture data from the final tool. No
external raw data,
real restricted directory, sealed checkout or live analysis output was opened.
No numeric trace values are included in the handoff.

The source census scans eligible tracked text at main and every HOLD tip;
unchanged blobs inherit main's scan. It excludes sealed path components,
symlinks/submodules, binary/non-UTF8 content and fixture data payloads (only
fixture source/docs are scanned; raw/custody subtrees are excluded).
Code/config/docs/registrations remain in scope. These exclusions preserve the
blinding boundary and do not lose Git protection: merged history remains on
main and every HOLD tip stays in the complete mirror/bundle and gets a whole-tip
tag before retirement. A resolved hex string is still a citation candidate,
not automatically a scientific pin; unresolved strings need owner triage.

## Execution gates and uncertainty

No retention tags/refs in this clone, production bundles, rulesets, server
branches or disk copies were created/changed by this task. Temporary synthetic
test repositories did create their own fixture commits/tags. No network, push, cleanup, model download or external integration
ran. Only this clone and task-owned temporary files were read/written, plus
Git's allowed shared handoff object store. No other /Users/edr path was listed,
statted, searched or opened. Forbidden absolute paths in docs/configs were text
only. The existing long-running job was not inspected or controlled.

The actual release receipt and its five roles remain unspecified. 498ad1d0's
server existence is Opus's evidence, not independently reverified here.
4cb222a19 recovery, the other three historical missing citations, per-tag PR and
check results, current GitHub rules, disk/alternates state and both durable copy
receipts all remain lead/Ed execution gates. The per-tag template marks them
PENDING. The corrected handoff/14-borrower status comes from the task brief,
not a filesystem inspection. These are limits of an offline plan, not claims
that retention has already been established.

Next exact step: lead reviews these local commits and lands the separate test
fix; after receipt acceptance and the job boundary, the magistrate recovers the
final ledger and Ed starts PRUNE-PLAN step 1 with a fresh branch/PR-head fetch.
Nothing in this handoff authorizes cleanup before those gates.

## Completed source-census evidence

Final source snapshot: `origin/main` c07b388e90d9f085e6428a1e0d96b0361ff417f0,
1,507 origin refs (687 merged candidates, 820 HOLD), 819 main/HOLD scope tips,
24,646 distinct eligible blobs, 6,536 resolved citation candidates: 4,366 MAIN,
236 existing-TAG, 1,934 HOLD-BUNDLE-ONLY, zero UNRETAINED. The 17,745 unresolved
text strings remain review aids, not 17,745 proven missing commits. The source
literal supplement has 824 digest occurrences across retained source versions.
The scope JSON records exclusions, numeric-context policy and network_verified=false.

The six highlighted objects (`8ce450ad55`, `9271df94f0`, `62bc719f7`, `28d153449`,
`ad56248a5`, `bea480f29`) all occur at full SHA in the expanded census. The first
two also have named anchor rows; the HOLD lanes require whole-tip tags at later
retirement. The anchor manifest has 12 existing names and 21 proposed names.

`python3.13 -B scripts/ops/prune_refresh.py --output /private/tmp/prune-fixes-final-census --archive-commit c07b388e90d9f085e6428a1e0d96b0361ff417f0 --archive-date 2026-11-08`
completed the final inventory phase; its initial grep phase was interrupted for
performance work. The final grep and verifier were then run as separate phases
against that same saved scope. The one-command CLI is also exercised end to end
by a tiny synthetic Git test, without network or production inputs.

`python3.13 -B scripts/ops/prune_verify.py --census docs/ops --archive-commit c07b388e90d9f085e6428a1e0d96b0361ff417f0`
PASS: 9,044 proposed anchor/main ancestors, 1,440 remaining HOLD-only candidates.
This is proposal topology, not proof that those 21 new tags exist or that server
rules/PR checks/copies are established. No complete scientific provenance claim
is made while the explicitly named missing/unfetched identities are unresolved.

`python3.13 -B scripts/ops/prune_branch_names.py --census docs/ops --output /private/tmp/prune-fixes-final-census/BRANCH-NAME-CONSUMERS.tsv`
completed with **exit 1, expected because matches require review**: 11,253
eligible distinct code/config/registration blobs, 207 positive blobs, 17,016
ref/path/line hits across 40 candidate names and 787 source refs. All rows remain
REVIEW; no hit was silently declared narrative or safe. Main has 66 hits across
26 names (the scope includes registration documents beyond the review's six
code roots). The old D-189 branch read on origin/main was detected; the local
test fix must land before that branch can be retired.

The final matcher shares literal prefixes, screens each distinct eligible blob
once, and gives Git grep only patterns actually present in each blob group.
Git grep -F remains the line/match authority, runs with one worker, and expands
hits to every affected ref/path. Overlapping and regex-special literal names
are tested, as is the one-command CLI. This avoids repeated matching of hundreds
of irrelevant patterns while preserving the exact fixed-string match set.

The broader scope necessarily enlarges the **audit** snapshots (including
repeated hits on HOLD refs), while the retention mechanism shrinks from 203
proposed tags to 33 named anchors. Audit rows never become tag-creation rows.
No name-consumer disposition or review-evidence PASS is invented from a hash
match. The actual release-day refresh still follows a fresh fetch and owner
review; today's output uses locally recorded refs only.

Commits: `dcaf2ca2c` contains only the real B5 equivalence-test fix. The second
local commit (`ops: apply cold-review fixes to prune plan and census tooling`)
contains the ops plan, scripts, synthetic regression tests, snapshots and this
report; its resulting SHA is provided in the final handoff. Nothing is pushed.

Final staged diff/scope, Python 3.11 grammar, local links and all seven shell
blocks passed. The final ops regression rerun passed after canonical digest
ordering and snippet whitespace normalization. Coordination files remain
unchanged; CI and all real execution gates remain pending as described above.
