# P2-041 Vetted Rebuild (2026-07-11)

## Outcome

P2-041 was rebuilt manually on `impl/p2041-vetted` from post-PR-#49 commit
`1b0f1f6578b60487cc6bb375cdc13008258740e5`, using
`docs/reviews/2026-07-11-p2041-red-tranche-triage.md` as the authoritative
per-file A/B/C recipe. The raw `impl/p2041` diff was not applied wholesale.
No commit, push, merge, site regeneration, live hardware command, or
`[QUIET-MAC]` measurement was performed.

The resulting implementation keeps the wire name `claim_readiness`, applies
the first-run exemption once per physical campaign session, retains the
adjudicated `joulewise.campaign_verdict.v2` sampling-audit shape, and advances
current reducer output to `0.4.0` with `window_evidence_precheck`. The reducer,
`MeasurementQuality`, JSON Schema, and strict comparison retain both
`runtime_cleanup_ok` and post-#49 `remote_cleanup_failed`. The strict raw-lineage
registry, mock exemption, powermetrics current/legacy arms, and NVIDIA
`nvidia_smi` verifier remain intact.

The historical tranche report
`docs/run_reports/2026-07-10-p2041-campaign-verdict-split.md` was copied exactly
as required. Its stale deviations are historical; this report is the current
rebuild authority.

## Intake And Planning Reflection

- Read the authoritative triage recipe first, then the active stop card,
  Current Project Status, Known Workspace State, What Is Next, current queue,
  Do-Not-Do-Yet list, Mission M0, orchestration process, source-of-truth map,
  planning-reflection protocol, Component C, D-030, D-050, and D-057.
- Confirmed the worktree was clean at the requested `1b0f1f6` branch point.
- Baseline canonical suite:

  ```text
  Ran 1041 tests in 67.995s

  OK (skipped=13)
  ```

- Goal: land only audited P2-041/C5 A behavior plus required post-#49 A+B
  unions, while preserving every unrelated P2-038/P2-040/P2-042/#49 behavior.
- Fences: no pure-B deletion hunk, no `docs/site/*`, no quiet-Mac work, no
  speculative version compatibility, and no commit.

## Composition By Category

### Clean A files copied exactly from `impl/p2041`

The working blobs match `impl/p2041:5135c1d` exactly:

- `docs/run_reports/2026-07-10-p2041-campaign-verdict-split.md`
- `docs/specs/c027/p2-040_reducer_gate_correctness.md`
- `tests/test_analysis_manifest.py`
- `tests/test_uncertainty_p2029.py`

### Mixed files composed from main

| File | Composition decision |
|---|---|
| `RUN_STATE.md` | Preserve post-#49 state; add only the rebuilt P2-041 handoff, verification, workspace, and report pointers. |
| `TASK_QUEUE.md` | Preserve main; update only P2-038's C5 request path and the P2-041 row. |
| `docs/contracts/run_bundle_layout.md` | Preserve config warnings, full P2-038 evidence, and cleanup fields; add 0.4.0/current-0.3.x dispatch, C5 precheck shape, and the original per-session campaign-provenance contract. |
| `docs/decision_log.md` | Preserve D-060 and the P2-038/P2-040 D-030 chain; union both cleanup fields, append 0.4.0, and append only the original closed-v1 P2-041 vocabulary. |
| `docs/phase_2/detection_floor.md` | Rename only the reducer field; preserve sentinel economics and landed-state tense. |
| `docs/specs/c027/analysis_engine_trio.md` | Resolve H3 to the landed campaign gate while retaining `claim_readiness`, per-physical-session exemption, and adjudicated v2/top-up shape. |
| `docs/specs/c027/p2-038_production_uncertainty_evidence.md` | Re-derive request paths to `window_evidence_precheck.idle_subtracted_request`; preserve the pending/null guard block. |
| `joulewise/cli.py` | Make 0.4.0 exact; reject current-era 0.3.0 and 0.3.1; retain frozen legacy arms, P2-038 uncertainty re-derivation, `RAW_TO_TRACE_VERIFIERS`, and NVIDIA verification. |
| `joulewise/reduce.py` | Rename helpers/output, remove the generic request alias, retain per-token evidence plus both cleanup fields. |
| `joulewise/schemas.py` | Set reducer 0.4.0 and rename the governed summary field while preserving ConfigKeyWarning and both cleanup fields/schema properties. |
| `scripts/run_campaign.py` | Apply the original audited verdict split; union P2-042's authoritative validator and both sidecar exclusions; preserve P2-038 shakedown and integer backup return; keep simple per-session cooldown provenance. |
| `tests/test_cli_run.py` | Re-derive exact 0.4.0 tests, explicit 0.3.0/0.3.1 rejection, old-field failure, and missing-either-cleanup-field exactness while retaining raw-lineage coverage. |
| `tests/test_p2038_production_path.py` | Preserve main's full production path and change only the three C5 request paths. |
| `tests/test_run_campaign.py` | Apply verdict/readiness mutations, all seven fixture repairs, real P2-042 validation, approved per-session provenance, sampling-audit shape, and P2-038 shakedown tests; omit rejected hardening tests. |
| `tests/test_schemas.py` | Expect 0.4.0 and assert both cleanup fields plus the renamed schema surface. |

### Pure-B preservation

All recipe-listed pure-B configs, production code, tests, contracts, plans,
reviews, reports, and generated `docs/site/*` files remain unchanged from the
branch base, with one disclosed post-#49 union exception below. In particular,
P2-038 clock/adapter/controller/uncertainty code, P2-040 warning/warmup/cleanup
code, the production shakedown configs, and their tests were not replaced by
tranche content. No site file was regenerated.

The recipe predates #49. Keeping post-#49 tests byte-untouched makes the
canonical suite fail after the required object/API rename, while adding a
`claim_eligibility` compatibility property would violate C5. The bounded A+B
union exception changes two assertions in `tests/test_reduce.py` and one in
`tests/test_nvidia_node_integration.py` only to
`summary.window_evidence_precheck`. No test behavior or production semantics
changed, and no production compatibility alias was added.

## Lead Rulings And Reverted Hardenings

1. **Wire name:** all tranche `analysis_readiness` changes were rejected.
   Current JSON, console output, helpers, specs, and tests use
   `claim_readiness` / `CLAIM-INPUT READINESS`.
2. **First-run identity:** the landing exempts the first physical invocation
   once per physical campaign session. A final review found a fail-open where
   persisted provenance could fan one session's exemption out to every member.
   The bounded v1 fix accepts at most one exemption-bearing physical member per
   provenance session, tied to `session_id`, `first_physical_run_id`,
   `following_run_id`, and that member's bundle IDs. Malformed/fanned-out notes
   normalize to `unknown`; counting does not cross sessions or manifests.
   Only `execution: invoked` rows may originate evidence, and resumed
   `execution: existing` bookkeeping rows carry no copied cooldown note, so a
   later resume cannot shadow the valid physical origin.
3. **Cooldown/top-up hardening:** the landing keeps raw cooldown JSONL
   path/hash/record-count provenance and the adjudicated sampling-audit keys.
   It does not add trace-v2 adjacency/timestamp/re-derivation fields, scoped
   runs-directory scanning, `detection_scope`, new hardening reasons, or an
   `analysis_readiness` wire.

Queue candidates are recorded here, not added as live queue rows:

- **Resume-spanning first-run identity.** Candidate: separately adjudicate an
  across-resumes, once-per-analysis-manifest exemption. Dissent: that rejected
  form is more fail-closed because repeated resumes cannot each gain an
  exemption. The lead's per-physical-session ruling governs this landing.
- **Cooldown trace hardening.** Candidate: version and review stronger
  adjacency/timestamp binding, row-shape checks, line-count validation, and
  independent rolling-decision re-derivation. Dissent: stronger binding would
  better detect stale or self-attested evidence. It is not silently folded
  into the adjudicated trace contract here.
- **Scoped top-up detection.** Candidate: define a complete search scope before
  adding scanning and fail-closed vocabulary. Dissent:
  `top_up_suspected: false` cannot prove absence outside an inspected scope.
  The landing keeps the adjudicated v2 shape exactly.

## Flagged Uncertainties And Follow-Ups

1. **Frozen stored-field mapper gap.** Component C5 describes an internal
   mapping for a frozen legacy summary that actually contains
   `claim_eligibility`, including `source_field` and
   `legacy_precheck_not_claim_evaluator`. Neither main nor the tranche defines
   that mapper or stable reason. The six real frozen summaries apparently
   predate the field; current code preserves their provenance-less absence
   tolerance. No hypothetical mapper was invented. Lead/spec adjudication is
   required before claiming the broader mapping behavior.
2. **Recipe-vintage pure-B conflict.** The three post-#49 assertion-only edits
   described above are necessary for C5 plus a green canonical suite. They are
   intentionally flagged for lead authorization because the older recipe says
   every pure-B file remains byte-untouched.
3. **Exact-clean P2-040 note.** The copied P2-040 spec's supersession note names
   current-era 0.3.0 but predates #49's 0.3.1. It remains blob-exact by the
   clean-file instruction. Current D-030, the run-bundle contract, code, and
   explicit tests reject both 0.3.0 and 0.3.1.
4. **Status-authority gap.** The Phase-2 plan/checklist contain no P2-041 matrix
   row. D-023 would normally call for a closure row, but both files are pure-B
   under the recipe. They remain untouched; lead/DOC-009 should reconcile the
   missing status authority.
5. **Top-up contract tension.** Component C still describes eventual top-up
   detection, while the binding ruling excludes this tranche's scoped
   detector. The current log therefore reports the adjudicated empty arrays and
   `top_up_suspected: false`; it does not claim a complete absence proof.
6. **Moving remote.** `origin/main` advanced after this worktree was created.
   The rebuild intentionally remains anchored at the user-specified post-#49
   commit `1b0f1f6`; no later bookkeeping commits were merged into the
   reconstruction. Consequently the anchored active stop card retains item
   1's pre-merge #49 narrative even though HEAD is the #49 merge; the P2-041
   handoff labels that inherited text superseded rather than importing later
   main state wholesale.

## Review Fixes

- B1 narrowed-confirmed → fixed: verdict-time cooldown raw provenance now fail-closes through one shared fresh/resume verifier for path, existence, current-byte SHA-256, JSONL parsing, and declared positive record count.
- S1 confirmed → fixed: every physically present expected member in the incomplete-existing branch is evaluated, while only absent paths enter the missing category.
- S2/R1 refuted empirically → queue candidate `frozen-legacy claim_eligibility mapper`.
- Semantic cooldown-row verification → queue candidate; row-field consistency and finite-value checks remain explicitly out of scope for this fix.
- N1 fixed: the current-reality critique cell now uses collection usable/partial/blocked/invalid plus `claim_readiness`.

## Verification

Required recipe commands were run without piping suite exit status. Final
tails:

### Focused modules

```text
----------------------------------------------------------------------
Ran 398 tests in 54.964s

OK (skipped=1)
```

### Canonical suite

The canonical command writes to
`/private/tmp/p2041-vetted-canonical-final.log`.

```text
----------------------------------------------------------------------
Ran 1062 tests in 76.436s

OK (skipped=13)
```

The canonical run emitted the existing loud skips for the absent retained
six-bundle corpus and sandbox-denied localhost socket gate. The
`make_figures` hash-mismatch line is expected output from its negative fixture;
the suite exit status was zero.

### Other gates

```text
git diff --check
(no output; exit 0)

rg -n '_window_claim_eligibility|_windows_claim_eligibility' joulewise scripts tests
(no matches; exit 1 as required)
```

The focused pre-final iteration passed `Ran 392 tests in 51.128s`,
`OK (skipped=1)`. The strengthened campaign module passed `Ran 72 tests in
18.229s`, `OK` after the exemption-fan-out and resume-shadow fixes and added
ruling locks.

## Recipe Steps Not Completed

Recipe step 6 (regenerate `docs/site/*`) was intentionally not run because the
user's post-recipe instruction explicitly reserves source-settled site
generation for the lead. No other recipe step was omitted. No commit was made,
also by explicit instruction; lead review, pathspec commit, and integrated-head
review remain handoff work rather than incomplete reconstruction work.

## Process Trace

- Active stop card at start: `RUN_STATE.md#ACTIVE_STOP_CARD`.
- Skills/playbooks used: Mission M0, planning-reflection protocol,
  `docs/orchestration.md`, authoritative P2-041 triage recipe. No installed
  artifact skill was applicable.
- Worktree / branch: `/Users/edr/code/JouleWise-wt/p2041-vetted`,
  `impl/p2041-vetted`; no PR or commit created.
- Invocation manifest path: none. Native collaboration sessions expose stable
  task paths but not file-backed prompt/output hashes; D-064 promotion remains
  pending in the active stop card. Unavailable fields are not fabricated.
- Council/debate: none; three pinned-spec read-only review roles plus final
  re-audits.

### Delegated invocation ledger

| Run | Parent report | Role/lens | Model/wrapper | Session ID | Prompt hash/path | Output path | Status | Consumed by | Disposition | Commit/PR |
|---|---|---|---|---|---|---|---|---|---|---|
| p2041-core-1 | this report | core reducer/CLI union audit | Codex subagent / native collaboration | `/root/core_union_audit` | unavailable (native) | conversation result | complete | root | accepted; drove dispatch union and flagged post-#49 test conflict | none |
| p2041-campaign-1 | this report | campaign runner/test composition audit | Codex subagent / native collaboration | `/root/campaign_audit` | unavailable (native) | conversation result | complete | root | accepted; defined approved/rejected campaign surface | none |
| p2041-docs-1 | this report | docs/contracts composition audit | Codex subagent / native collaboration | `/root/docs_audit` | unavailable (native) | conversation result | complete | root | accepted; drove D-030/D-057 and dissent wording | none |
| p2041-core-2 | this report | final core diff audit | Codex subagent / native collaboration | `/root/core_union_audit` | unavailable (native) | conversation result | complete | root | clean verification; two documentation flags consumed | none |
| p2041-docs-2 | this report | final docs diff audit | Codex subagent / native collaboration | `/root/docs_audit` | unavailable (native) | conversation result | complete | root | clean verification; wording/status gaps consumed | none |
| p2041-campaign-2 | this report | final campaign diff audit | Codex subagent / native collaboration | `/root/campaign_audit` | unavailable (native) | conversation result | complete | root | found exemption fan-out blocker plus coverage gaps; fixed | none |
| p2041-campaign-3 | this report | exemption/resume-fix final audit | Codex subagent / native collaboration | `/root/campaign_audit` | unavailable (native) | conversation result | complete | root | clean; adversarial inferential-member double resume and non-originating existing rows verified | none |

### Review yield and delegation calibration

| Role | Altitude | Lead-assigned outcome | Unique useful findings | Lead rework | Prompt vs model defect |
|---|---|---|---|---|---|
| Core audit | pinned-spec / post-merge union | accepted | post-#49 pure-B conflict; frozen mapper gap; missing remote-cleanup contract prose | not instrumented | recipe-vintage gap, not model defect |
| Campaign audit | pinned-spec with composition judgment | accepted after fixes | first-exemption fan-out fail-open; copied-existing resume shadow; exact valid/rejected test split; session-local identity nuance | not instrumented | implementation defects caught by reviewer |
| Docs audit | pinned-spec | accepted | D-030 two-field union; D-057 wording; status-authority gap; dissent language | not instrumented | no prompt/model defect assigned |

The campaign audit found the two accepted production defects in the final
review rounds: exemption fan-out and copied-existing resume shadow. Other
findings were contract/documentation drift or clean verification. No
false-positive finding was applied.

### Ephemeral artifacts

| Path | SHA-256 / stable ID | Promoted to | Not promoted reason |
|---|---|---|---|
| `/private/tmp/p2041-vetted-baseline.log` | `91105c89f2b5fc20f99881a13c36628a891957559a99fd146932f4218350e867` | baseline tail in this report | raw dot stream is disposable |
| `/private/tmp/p2041-vetted-focused-final.log` | `f7a962361ddc09ad679c195afb29cc38afa5d90778e5b23fffc7239921809e49` | final tail in this report | raw dot stream is disposable |
| `/private/tmp/p2041-vetted-canonical-final.log` | `17eff0ec5fa4a029d64659bb9a7ff4b2b9adf70ba05a25884ac3283996a372c7` | final tail in this report | raw dot stream is disposable |

- Stop state at end: implementation and local verification complete, dirty
  only with the intended uncommitted rebuild; lead owns final diff review,
  pathspec commit, review stack, and integration/merge decisions.

## Next Exact Step

Lead-review this diff against the triage recipe, explicitly adjudicate the
three assertion-only post-#49 pure-B exceptions and the frozen-mapper gap, run
the canonical suite unpiped in the lead environment, then commit only the
reviewed P2-041 rebuild pathspecs. Do not regenerate `docs/site/*` until source
composition is accepted.
