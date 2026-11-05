# Block-5 release readiness — 2026-11-05

Branch: `lane/2026-11-05-b5-release-readiness`, created from local
`origin/main` at `92026c1849c0f053e56bdac6110c079211db2c31`.
No network, real study custody, measurement input, or external `/Users/edr`
path was accessed. Only repository-generated synthetic S10 data was executed.
No study release or unblinding occurred. This is a local, unpushed lane.

## Intake and scope

First command:

```sh
git show origin/lane/2026-11-05-b5-release-runbook:docs/process/b5_release_runbook.md
```

Mission M0: read repository instructions, the generated stop/restart region,
Current Project Status and Known Workspace State, the block-5 handoff and
recompute items, Current Queue and Do-Not-Do-Yet, the playbook, orchestration,
owning registration/plan, D-188–D-190, and the RC-CMP records. No active stop
card or global work-selection gate. Initial workspace clean and detached at
the base above. The user's explicit two-part brief overrides queue rank
(playbook M0); this is bounded `[AGENT]` preparation. The post-release
`FREEZE-BY-COMMIT-01` selection and all machine-state gates remain as before.
No agent was delegated and no scientific ruling was made.

## Part A — code and contract audit

Both original remote lanes are merged, rather than branch-only:

```sh
git merge-base --is-ancestor origin/lane/2026-10-14-independent-recompute origin/main
git merge-base --is-ancestor origin/lane/2026-10-27-recompute-comparator origin/main
git merge-base --is-ancestor d97e55d1f origin/main
```

All exit 0. The lane tips are `9ca87bcee5d810c14c105c3104b16a62109d1005`
and `ea17de53ddcf2fb843869fe64bae619549508e1c`; the last comparator code
change is RC-CMP-11, `d97e55d1f`. The programs live at
`scripts/independent_recompute_b5.py` and `scripts/compare_b5_recompute.py`;
block-5 bars at `configs/analysis/b5/recompute_bars.json`; tests at
`tests/independent_recompute/`. Their contents are identical between the
base and r2:

```sh
git diff b5/analysis-r2 HEAD -- scripts/compare_b5_recompute.py scripts/independent_recompute_b5.py
```

No diff. RC-CMP-1's two-bar experiment is historical. RUN_STATE item 83 and
RC-CMP-2 fix block 5's coded release bars; S-13 stays a block-6 test config.

The comparator still expects:

- A **dry-run custody root**, containing
  `dry-run/B5-BLIND-DRY-RUN-RECORD.json` and `dry-run/restricted/`. It does not
  auto-select `release/B5-RELEASE-RECORD.json`.
- Each output's record-listed name and SHA-256. Step-11 fill and disclosure
  records match `outputs/<64 hex>-results-fill-input.json` and
  `disclosures/<64 hex>.json`. Fill JSON is canonical plus newline;
  disclosure JSON is canonical without newline. Released/unreleased text
  views are not independently compared by this arithmetic comparator.
- The exact driver index passed via `--window-index`; its digest must match
  the record. The default tracked real index was never used for execution.
- Independent recompute JSON with `--member-detail`, the same synthetic
  archive/claim/bound roots, registered ids and selection. The loader checks
  duplicate keys, canonical step-11 bytes, routing/shape/required fields and
  content hashes; it is not a complete dry-run-record schema validator or a
  terminal-completion gate. Completion is checked separately in this run.
- Registry-driven expected checks and key-bound leaf coverage (RC-CMP-3
  through RC-CMP-11), not RC-CMP-1's earlier value-only coverage map. The
  historical 624 list was a per-run report, not a static allowlist. Its
  original valued report was not opened; a fresh synthetic census is below.

The r2 writers still identify the run record as
`joulewise.b5_blind_dry_run.v1` (mode distinguishes dry-run/release), the fill
as `joulewise.results_fill_input.v1`, the disclosures as
`joulewise.b5_disclosures.v1`, and sensitivity as
`joulewise.b5_bracket_sensitivity.v1`. Independent output is
`joulewise.independent_recompute_b5.v1`; comparison output is
`joulewise.b5_recompute_comparison.v1`. Equal version strings alone do not
prove conditional-shape compatibility.

**D-190 boundary:** normal issued numeric shapes and registered null outcomes
are different contracts. `Comparison.numeric` still rejects a null on either
side under RC-CMP-1 A2; numeric coverage requires an agreeing row. Thus this
comparator cannot certify every newly traversable D-190 null branch merely
because the r2 driver completes. A not-estimable recompute row also retains
its supplied D and uses p=1 as its arithmetic placeholder, whereas the engine
and step-11 presentation can carry nulls. No generic null-equals-null waiver,
new exemption, relaxed bar, or analysis-code change was introduced. The
synthetic issued-shape result must not be generalized to an unseen study
outcome. A separately specified state mapping is needed before claiming
recompute coverage of those branches.

**NEEDS_RULING (null-state certification only).** Question: does the lead
retain the original RC-CMP-1 A2 rule ("a value missing or null on either
side is DISAGREE"), or install an explicit D-190 state-aware comparison
contract? Options considered: preserve fail-closed behavior; compare only
independently established registered non-issuance states, with exact shape,
count and outcome checks and no general null-equality rule. Recommendation:
preserve A2 until that contract is specified and reviewed. Blocked work:
certifying all D-190 null branches as independent-recompute agreement. This
does not describe any observed study outcome. The question was presented
while the independent synthetic work continued.

## Synthetic execution

**PASS for the full S10 issued-output case.** Fresh r2 driver exit **0**;
every registered step through 11 is `ok`, including 9b and both step-10
windows; `completed_without_tooling_refusal=true`. Step 11 retains
`results_rendering_not_run_no_block5_template`. Independent recompute exit
**0**; current comparator exit **0**, **2,514 comparisons, 0 disagreements**.
There are no disagreements to classify. No comparator adaptation was needed
for this full-size case. This does not certify the D-190 null branches above.

| Comparison | Comparisons | Disagreements | Normalized leaf paths | Compared | Uncovered | Unmapped |
|---|---:|---:|---:|---:|---:|---:|
| Archived RC-CMP-1 report (L9 `6af08b780`) | 1,454 | 0 | 841 | 217 | 624 | 0 |
| Original RC-CMP-1 code replayed on **r2**, coded bars | 1,454 | 0 | 841 | 217 | 624 | 0 |
| Original RC-CMP-1 code replayed on **r2**, S-13 test bars | 1,454 | 0 | 841 | 217 | 624 | 0 |
| Current RC-CMP-11 code on **r2**, block-5 release bars | 2,514 | 0 | 1,384 | 328 | 1,056 | 0 |

All three fresh comparator invocations exit 0. The original script is
`234fbb12708c6b318173d7227319aaaa377d1b76:scripts/compare_b5_recompute.py`,
SHA-256 `263b74fa345a92563526fe55deb8f8b047195499000fb72981ebbc53e7ac4495`,
matching RC-CMP-1's recorded hash. S-13 is used only to reproduce that
historical experiment, not to select or relax block 5's release bars.

The current map uses named disclosure-line scopes where the original used
generic list stars, and later RC-CMP revisions add expected, routing and
categorical checks. Consequently its normalized path count is different;
1,056 versus 624 is not a count of additional physical outputs or a regression
caused by the rewrite. The fresh original-code replay reproduces the old
841/217/624 census exactly on r2. The original untracked per-leaf report was
not available here, so equal counts are not claimed as a byte comparison to
that historical list. The new per-path maps and reasons are preserved at
[`synthetic-coverage.json`](../process_traces/2026-11-05-b5-release-readiness/synthetic-coverage.json).
The current map explicitly lists **340 numeric/null exemption paths**;
there are **0 nonfinite paths**, **0 absent step-11 sources**, and **0
unmapped paths**. Listed exemptions still require the registered post-release
reader's hand check for anything the paper prints.

Current per-family pass/fail counts:

| Family | Pass | Fail |
|---|---:|---:|
| run_phase_energy_j | 786 | 0 |
| floor_j | 149 | 0 |
| floor_gate_j | 70 | 0 |
| dominance_ratio | 12 | 0 |
| reported_cell_j | 144 | 0 |
| contrast_j | 122 | 0 |
| contrast_p | 44 | 0 |
| descriptive_ratio | 6 | 0 |
| per_token_j | 10 | 0 |
| b_op_s | 14 | 0 |
| count | 133 | 0 |
| outcome_word | 188 | 0 |
| dominance_branch | 2 | 0 |
| p42_status | 6 | 0 |
| holm_order | 1 | 0 |
| kept_units | 26 | 0 |
| exclusions_rederivation | 3 | 0 |
| routing_id | 798 | 0 |
| meter_j, meter_w, machine_j, rho, window_edge_s, battery_term (each) | 0 | 0 |

The full-size fixture has no meter stream, so the last six families are
**unexercised**, not six passes. The targeted meter module below covers its
synthetic meter cases separately. Recompute flags are the same intentional
fixture features documented in RC-CMP-1: `archive_file_missing=19`,
`trace_plist_missing=3`, `member_pre_bound_missing=3`, and `meter_absent=3`.
They concern planted aborted/truncated or excluded members and missing meter
streams; they are not disagreements on compared selected members.

Exact invocation from the detached r2 worktree:

```sh
TMPDIR="$PWD/.scratch-s10f/tmp/readiness-on" JW_B5_S10_REAL_PROGRAMS=1 JW_B5_S10_CHAIN_CACHE="$PWD/.scratch-s10f/tmp/readiness-on/fixtures" JOULEWISE_B5_VDL=on python3.13 -B ../synthetic_run.py
```

The saved script calls r2's real `dry_run.run(...)` through the existing
joined harness, not a bare CLI with invented study inputs. It then launches:

```text
python3.13 -B <CLONE>/scripts/independent_recompute_b5.py --member-detail --out <TMPDIR>/recompute.json --alpha <TMPDIR>/fixtures/alpha/archive --claim-runs-alpha <TMPDIR>/fixtures/alpha/custody/runs_claim --bound-runs-alpha <TMPDIR>/fixtures/alpha/custody/runs_bound --beta <TMPDIR>/fixtures/beta/archive --claim-runs-beta <TMPDIR>/fixtures/beta/custody/runs_claim --bound-runs-beta <TMPDIR>/fixtures/beta/custody/runs_bound --gamma <TMPDIR>/fixtures/gamma/archive --claim-runs-gamma <TMPDIR>/fixtures/gamma/custody/runs_claim --bound-runs-gamma <TMPDIR>/fixtures/gamma/custody/runs_bound
python3.13 -B <CLONE>/scripts/compare_b5_recompute.py --l9-custody <TMPDIR>/synthetic-custody --recompute <TMPDIR>/recompute.json --window-index <TMPDIR>/index.json --restricted-out <TMPDIR>/comparison-initial.json
```

These readable vectors abbreviate the clone/TMPDIR prefixes and interpreter path;
`<CLONE>` is this clone root and `<TMPDIR>` is the final invocation's TMPDIR. The exact
absolute OS argument vectors, interpreter, exit codes, program/config/output
hashes and driver record are in
[`synthetic-summary.json`](../process_traces/2026-11-05-b5-release-readiness/synthetic-summary.json).
The original comparator was extracted with
`git show 234fbb127:scripts/compare_b5_recompute.py` and run by:

```sh
python3.13 -B .scratch-b5-release-readiness/summarize.py
```

That saved summarizer invokes the extracted script twice, with
`--l9-custody`, `--recompute`, `--bars` (the original coded and S-13 files)
and new `--restricted-out` paths. Its exact vectors and exits are also in the
summary. A subsequent metadata-only summarizer pass added the public record
identity and deduplicated identical coverage maps; it reused the recorded
legacy invocations rather than rerunning them.

Runtime: CPython **3.13.18**. Restore + harness setup + driver took **2446.88 s**
(the trace field `driver_wall_s` includes restore/setup); recompute took about
20.71 s and comparison about 1 s. Complete record SHA-256:
`34ec2896354148e129254f9a3796879134a306f9c6a3c8709aaf399fdd7a788f`.
Comparator checkout at execution:
`ef8d2c20dd28698dfd4e80245b42597e77842915` (docs/bookkeeping edits only;
comparator and config bytes unchanged).
Current comparator SHA-256:
`28d504c2ab6a67090e3cd1a1b4d11d4e4002e03d99c94196298215d311ce6207`;
release-bar SHA-256:
`2f65bba22c0afd23a637cabb5079e1c5dc6a367d53d956f77c20ead416813892`.

The exact acceptance script and launch are preserved in
`docs/process_traces/2026-11-05-b5-release-readiness/`. The r2 code is
unchanged; the existing joined harness supplies synthetic Git observations.
Its synthetic record's `analysis_commit` is that harness's Git anchor
(`c98628b20ed0ac84ce2924ab135f96dbf2dae6a1`), not the actual executing r2
source identity, which is recorded separately. This is the same synthetic
method used by RC-CMP-1, not a real release checkout/record attestation.
The final fresh run explicitly uses `JOULEWISE_B5_VDL=on`. One driver worker;
no reported timing is a live performance claim. Fixture cache and analysis
custody are both under its TMPDIR inside the detached worktree.

An earlier default-VDL (`shadow:1000`) attempt was interrupted via Control-C
to its owned tool session during step 5. Its record is exit 2 after 1598.95 s,
step 5 `unclassified_refusal`, later steps `not_run`; it cannot establish
acceptance or an r2 defect. The underlying exception was not separately
adjudicated after the deliberate interrupt request. Its independent recompute
exited 0 and its
comparison exited 2 (`step11_outputs_absent`). This interrupted attempt and
its inputs remain at `.scratch-b5-release-readiness/tmp/` and
`.scratch-b5-release-readiness/r2/.scratch-s10f/tmp/readiness/`, respectively.
Record SHA-256:
`eef0aec005e5b3a9afc6577b3982155c559f0fc000ca94a0937a7ca8c4471f85`.
An initial bad-path launch failed before fixture restore; the sandbox also
refused `nice`. The exact launches and failure disposition are in the trace
README. No signal was sent to the existing seven-worker job.

The full-size S10 fixture archives themselves are unchanged from RC-CMP-1's
L9 tree: `git diff --stat 6af08b780 b5/analysis-r2 --
tests/fixtures/b5_analysis/s10` prints nothing. The restore helper is also
unchanged from `2ea99f51f`: `git diff --stat 2ea99f51f b5/analysis-r2 --
tests/b5_analysis/fixtures_s10.py` prints nothing. They contain 125 ALPHA,
125 BETA and 107 GAMMA generated members, including intentional
aborted/truncated/retired members. This is the full existing S10 case,
not a reduced or hand-authored comparator-only mock.

## Part B — draft seal addendum

Created `docs/process/b5_r2_analysis_addendum_DRAFT.md`, without editing
`SEAL_RECORD.md` or sealed registration/plan. It records the date, this
seat's own blinding statement, pin-before-event authority and append
convention, exact annotated-tag/commit/tree identities for the first
analysis tag, r1, r2 and the patched reference, D-188–D-190 changes, the
validated-fill-input renderer deviation, and explicit `LEAD-FILL` evidence
and adoption fields. It makes no retrospective pin or release assertion.

The companion `docs/process/b5_r2_analysis_program_files_DRAFT.json` names
315 source/config/environment files and their SHA-256s, all read from r2 Git
objects. It is intentionally overinclusive, not a runtime import census.
Its SHA-256 is
`fe7268c7012214d23360b50e6ca0fd1b81bacd752fd7377c6659fed7567a7c4e`.
The full r2 tree binds remaining tracked material. Actual environment use,
study-run ids/verdicts, final harvest bindings, reviews and adoption remain
`LEAD-FILL`.

Identity commands:

```sh
git rev-parse 'b5/analysis-r2^{commit}' 'b5/analysis-r2^{tree}'
git rev-parse 'b5/analysis-r1-9bfix-ref^{commit}' 'b5/analysis-r1-9bfix-ref^{tree}'
git cat-file -t b5/analysis-r2
git cat-file -t b5/analysis-r1-9bfix-ref
```

Results: r2 commit `929fc65c9ce3ff82f0311d28acf76a682edd466f`, tree
`9e89d7ff48999416467129c03ea171fc3a1f3f83`; reference commit
`e7eb872d232ab58efe3ff861ae2c33dbfd8c0a33`, tree
`de2e980edecf9047efd5c86dd4f31488a6d5a739`; both types `tag`.

## Verification and remaining authority

Targeted modules ran **sequentially**, with
`JW_B5_SYNTHETIC_ONLY=1 TMPDIR="$PWD/.scratch-b5-release-readiness/tmp"`
and `python3.13 -B -m unittest <module>`:

| Module | Result |
|---|---|
| `tests.independent_recompute.test_comparator` | 28 tests, 11.977 s, OK |
| `tests.independent_recompute.test_rc_cmp11` | 13 tests, 19.734 s, OK |
| `tests.independent_recompute.test_hygiene` | 6 tests, 0.851 s, OK |
| `tests.b5_analysis.test_step11_null_outcomes` | 9 tests, 1.346 s, OK |
| `tests.independent_recompute.test_comparator_meter` | 13 tests, 3.339 s, OK |
| `tests.test_gen_state` | 44 tests, 3.833 s, OK |

`python3.13 -B -m compileall -q joulewise tests`: exit 0.
`python3.13 -B scripts/gen_state.py --check`: baseline and regenerated views exit 0.
The Git-object pin verification re-read all 315 source/config file objects
and all four tag/commit/tree identity sets, and matched the companion
inventory digest: exit 0. Final `git diff --cached --check`: exit 0.
No full suite was run, per the user's load/blinding restriction; test-module
time is 41.080 s (113 tests). The separate full-size driver is acceptance
execution under the task's synthetic-only exception, not a test-suite run.

The old RC-CMP brief explicitly says the real recompute comparison happens
at release under registration §8; it motivates the pre-event synthetic run.
This helps explain the runbook's ordering gap, but the actual lead's ordering
disposition remains `LEAD-FILL`. No real-data agreement is supplied here.

Next exact step: the lead reviews this lane's synthetic evidence and draft,
resolves any unsupported-state mapping and recompute-ordering disposition,
fills the real evidence fields, and adopts the analysis pin in the seal
record before the event. The actual release remains lead-owned.

## Changed files, commits and workspace

- Draft addendum and companion pin inventory under `docs/process/`.
- This report and the trace directory's README, exact runner, summarizer,
  value-free run summary and per-leaf coverage map.
- `docs/process/state_kernel.json`: latest report/date and the existing
  freeze task's preparation note only. Regenerated `RUN_STATE.md` and
  `TASK_QUEUE.md`, with a compact lane handoff and completed-preparation
  history outside the generated regions. Live task count, ranks, statuses,
  dependencies and gates did not change. Explicit user direction authorized
  immediate preparation; no new live task remains for this finished fixture
  run, and the null-state decision is recorded above rather than silently
  installed.

No analysis, recompute/comparator, fixture or test source was edited.
`PROJECT_STATUS.md` was not changed because no advisor-visible study state
advanced. No new scientific decision was installed in the decision log.
The draft/pin commit is **`ef8d2c20d`**; the final evidence/handoff commit is
identified by this branch's subsequent `git log` and the final task reply.
No push or merge was performed.

`git diff --exit-code origin/main --
docs/process_traces/2026-10-07-block5-seal/SEAL_RECORD.md
configs/campaigns/v5_claim_25g83/registration_block5.md
configs/campaigns/v5_claim_25g83/analysis_plan_block5.md`: exit 0, unchanged.
The detached r2 worktree remains at `929fc65c9` with no tracked changes.
Task-owned ignored scratch retains both synthetic attempts and their inputs;
no raw bundles or custody were pruned. The local-only `.git/info/exclude`
additions are `/.scratch-b5-release-readiness/` and `/.scratch-s10f/`.

Remaining uncertainty is bounded: this fixture exercises issued numeric
shapes and no full-size meter stream; it does not settle D-190 null-state
certification, any actual study verdict, the real run environment, the
unavailable historical per-leaf artifact, or the lead's release/adoption
ordering. The draft leaves those evidence/authority fields `LEAD-FILL`.
