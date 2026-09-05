# Opus counter-review — WAVE-2 integration tree (gate ledger row 6)

Seat: Opus counter-review (row 6). Tree: `/Users/edr/code/JouleWise-wt-int-fan-wave2`,
branch `int/2026-09-04-fan-wave-2`, head `8222b114`. Scope reviewed:
`git diff origin/int/2026-09-04-fan-wave-1..HEAD` (322 files, +39912/-2547).
Read-only except this file. The Sol contract refuter's round 4 was running
concurrently and was not read.

Lens: claim-bearing surfaces; cross-landing seams; the D-161 re-scopes;
implementation-encoding tests; docs describing absent behaviour;
doctrine-shaped changes owing a cold gate. Execution/contract refuter rounds
1–3 (`wave-2/01`, `02`, `03`) and the wave-1 counter-review were treated as
already-covered ground; findings below are the delta this seat adds.

---

## VERDICT

**NOT LANDABLE.**

Three blockers. One is a red test in the delta (B1) with two independent
causes, one of which — a post-seam-fix merge from `origin/main` — was never
re-run. Two are advisor-facing claim-surface defects introduced by this
wave's own documentation landings (B2, B3), both of which contradict either
the evidence in the tree or another landing in the same wave.

None of the blockers touches physics, calibration, or a pre-registered
constant. The claim spine came through this wave clean, and that is verified
positively below, not assumed.

---

## Executed evidence (all run by this seat in this session unless labelled otherwise)

| # | Command | Result |
|---|---|---|
| E1 | `git diff --stat origin/main -- joulewise/reduce.py`; `git rev-parse origin/main:joulewise/reduce.py HEAD:joulewise/reduce.py` | empty diff; both blobs `82449d58209278e756050762a0de6cd958558f7e` |
| E2 | `shasum -a 256 configs/analysis_registry/detection_floor_closed_sets.v1.json` | `fc91df6d14b02d17dba31d1018c31287b65bde2d94f2b608825411f98b2aed1d` — equals the `.sha256` sidecar and `detection_floor_registry.py:FROZEN_REGISTRY_SHA256` |
| E3 | `python3 scripts/check_campaign_generator_core_parity.py --baseline-ref origin/main` | `PARITY_OK generators=3 files=352 excluded=[...] baseline=origin/main` |
| E4 | `python3 configs/campaigns/p2_015_floors/generate_configs.py --out-dir $T/new` then `diff -r $T/new configs/campaigns/p2_015_floors --exclude=generate_configs.py --exclude=campaign_spec.json` | `generated 282 runnable configs`; diff reports only `Only in configs/…/p2_015_floors: backup_icloud.sh` — every frozen config byte reproduced |
| E5 | `python3 -m unittest tests.test_git_fixture_maintenance` | **FAILED (failures=1)** — see B1 |
| E6 | `python3 -m unittest tests.test_detection_floor tests.test_floor_extraction tests.test_reduce` | `Ran 459 tests … OK (skipped=1)` |
| E7 | `python3 -m unittest tests.test_arm_readiness_integration tests.test_night_gate tests.test_run_night tests.test_campaign_generator_core tests.test_phase_share tests.test_modularity tests.test_build_site_parsers tests.test_s0_line_audit_guard` | `Ran 178 tests … OK (skipped=30)` |
| E8 | `python3 -m unittest tests.test_whole_window tests.test_whole_window_selection tests.test_check_window_provenance tests.test_run_campaign` | exit code 0 (summary line lost to the tail pipe; unittest exits nonzero on any failure) |
| E9 | `python3 -m unittest tests.test_paper_round7_artifacts` | exit code 0 |
| E10 | `python3 -c "import json;k=json.load(open('docs/process/state_kernel.json'));print('P1-008' in k['tasks'],'ED-DATES-01' in k['tasks'])"` | `False True` |
| E11 | `grep -c -i "fixed term\|rank devices\|advisor\|D-067" docs/contracts/measurement_methodology.md` | `0` |
| E12 | `grep -c "D-070\|stress" docs/research_question_registry.md` | `0` |
| E13 | `grep -rl "claim_family_bounds" --include="*.json" .` | no hits |
| E14 | `grep -rn "FLOOR_METRIC_CATALOG" --include="*.py" .` | no hits outside process traces |

Delegated read-only audit seats (launched and directed by this seat in this
session; their commands are quoted where cited): a docs-vs-code seat and a
D-161 re-scope seat. Findings taken from them are marked **[delegated]**.

---

## Blockers

### B1 — the estate-wide Git-fixture guard is RED at HEAD (six modules), and the merge after the seam fix was never re-run

`tests/test_git_fixture_maintenance.py:172`
(`test_every_test_module_routes_git_initialization_through_shared_helper`).

Counterfactual (E5), verbatim:

```
AssertionError: {'test_install_magistrate_watchdog.py': (98, 117),
 'test_install_night_agent.py': (30,),
 'test_magistrate_watchdog.py': (1576,),
 'test_magistrate_watchdog_cli.py': (34,),
 'test_run_night.py': (66,),
 'test_s0_line_audit_guard.py': (103,)} != {}
```

Two independent causes, and each matters on its own:

1. **A named call site was left uncured.** The round-3 contract refuter
   (`wave-2/03`, R3-F2) named `tests/test_s0_line_audit_guard.py:103`
   explicitly. The seam fix that claims to cure it —
   `d5378e8e` "direct git-init calls routed through the shared helper" —
   touched only `tests/test_arm_readiness_integration.py`,
   `tests/test_issue_dg071_dg075_statistics.py`,
   `tests/test_paper_round7_artifacts.py` and its own trace file
   (`git show --stat d5378e8e`). `tests/test_s0_line_audit_guard.py` is not
   in that commit, and line 103 still reads
   `subprocess.run(["git", "init", "-q"], cwd=repository, check=True)`.
   A fix report asserting a cure for a site it never opened is the defect
   shape, not the line itself.

2. **The merge regrew it, five-fold, and nobody re-ran the guard.** `8222b114`
   merged `origin/main` — carrying PR #284 — *after* `d5378e8e`. That brought
   five watchdog/installer test modules that predate the guard and were never
   routed through `tests/git_fixture.init_git_fixture`. `git log -L` confirms
   the five lines originate in the watchdog series (`a15cc15e`, `12ec41d2`,
   `8b2e11c8`, `aeacba61`), not in any wave-2 landing.

This is the canonical cross-landing seam the counter-review lens exists for:
one landing adds an estate-wide guard, and an unrelated merge trips it. The
guard is doing its job; the integration tree is red.

Severity: blocker. The tree cannot land with a delta test failing.
Cure: route the six sites through `init_git_fixture`, then re-run E5 **after**
any further merge from `origin/main`, not before.

### B2 — `PROJECT_STATUS.md:104` introduces an uncorroborated count on the advisor-facing surface

New text: *"Five post-repair measurement windows passed the contamination
screening and uncertainty accounting, establishing that the mechanism can
pass."*

The wave-1 base said, at `PROJECT_STATUS.md:346`, *"Earlier post-repair
windows established that the path can pass"* — deliberately uncounted. The
doc008/docs-vs-truth compaction replaced an honest indefinite with a specific
integer.

Counterfactual: `grep -rn "post-repair" --include="*.md" docs/ PROJECT_STATUS.md README.md`
(traces excluded) returns three hits —
`docs/project_status_history.md:17` ("the first post-repair windows passed",
uncounted), `docs/run_reports/2026-07-28-floor-mint-implementation.md:76`
(a single rerun), and the new sentence itself. No ledger, run report,
artifact, or kernel row in the tree enumerates five such windows. The count
is unsupported by anything a reader could check.

Severity: blocker. This is the page the advisor reads. A number that cannot be
resolved to its evidence is precisely the defect class D-078's custody rules
exist to prevent, and the cure is one clause: restore the indefinite, or name
the five windows and their bundles.

### B3 — cross-landing seam: `milestones.md` and `risk_register.md` cite a task this same wave retired, and name it as a truth source

Nine lines ADDED by the wave-2 delta name task `P1-008` as the owner of the
evaluator/colloquium/report dates:

- `docs/milestones.md:15` — truth-source column reads
  `docs/process/state_kernel.json`, task `P1-008`
- `docs/milestones.md:41`, `:45`
- `docs/risk_register.md:42` (new risk R-022: "open; `P1-008` owns the missing
  inputs"), `:53`, `:55`, `:141`, `:223`, `:438`, `:441`

The magistrate's own fan-out ruling (`01-magistrate-rulings.md`, p1-rows row)
reads: *"Retire P1-008; open a narrow external-input row for the final-report
and colloquium dates."* The p1-rows landing did exactly that, in this same
wave — `TASK_QUEUE.md:109` records P1-008 RETIRED and `ED-DATES-01` as the
survivor.

Counterfactual (E10): `'P1-008' in kernel['tasks']` → `False`;
`'ED-DATES-01' in kernel['tasks']` → `True`. `docs/milestones.md:15` therefore
points a reader at a kernel task that does not exist, and calls it the truth
source. Confirmed as ADDED lines:
`git diff origin/int/2026-09-04-fan-wave-1..HEAD -- docs/milestones.md docs/risk_register.md | grep "^+.*P1-008"`
returns all nine. **[partly delegated]** — surfaced by the docs seat,
re-executed here.

Severity: blocker. Two landings in one delta contradict each other on a
professor-facing page, and the losing side cites a nonexistent authority.

---

## Should-fix

### S1 — `README.md:79-81` retargets to a document that does not contain the content

The advisor-review rationale and basis/boundary rule were retargeted from the
deleted `PROJECT_STATUS.md#measurement-methodology-highlights` to
`docs/contracts/measurement_methodology.md`. Counterfactual (E11): that file
contains zero occurrences of "fixed term", "rank devices", "advisor", or
"D-067". The text survived in `origin/int/2026-09-04-fan-wave-1:PROJECT_STATUS.md`
and now survives nowhere. **[delegated, re-executed here]**

### S2 — `README.md:90` retargets the D-070 stress-test agenda to a registry that lacks it

Counterfactual (E12): `grep -c "D-070\|stress" docs/research_question_registry.md`
→ `0`. The same wave's registry addition marks Q4 `cut`. The README paragraph
above the link states the five axes as live commitments; the link goes
somewhere that neither states nor supports them. **[delegated, re-executed here]**

### S3 — a ratified contract still specifies a public symbol MODULARITY-01 removed

`docs/phase_2/floor_mint_contract.md:14`, Implementation ORDER item W8
(marked "ratified; do not resequence"), specifies *"public
FLOOR_METRIC_CATALOG in detection_floor.py, imported by floor_extraction.py;
NINE entries…"*. MODULARITY-01 deleted the tuple, dropped it from `__all__`,
and removed the `floor_extraction.py` import.

Counterfactual (E14): `grep -rn "FLOOR_METRIC_CATALOG" --include="*.py" .` →
no hits outside process traces.

Mitigating, and verified: the semantics did not move. The registry declares
exactly the same nine metric/window pairs and the same four calibration
scopes the retired `_CALIBRATION_SCOPES` tuple held, and its bytes are pinned
three ways (E2). This is a stale ratified-contract text, not a widened closed
set. But a ratified contract naming a symbol that no longer exists is the
"ruled-not-installed" shape in reverse, and a future reader will trust it.

### S4 — the wave contradicts itself on whether site drift is recorded, and creates drift while doing so

`PROJECT_STATUS.md:135` ("repository is authoritative; drift is recorded and
Ed deploys manually") and `:192-193` ("Front-facing drift:
`docs/site/DRIFT.md`") assert an ongoing obligation. `README.md:264-266` and
`docs/publication_release_checklist.md:86-92`, edited in the same delta,
state that under D-136 agents "do not refresh, regenerate, or deploy the
site" and that DRIFT.md "is a retained reference only". D-136
(`decision_log.md:180`) retires the lane.

Compounding it: this delta changes `docs/site_src/{index,research,results}.html`
(+159/-142) while `docs/site` is untouched
(`git diff --name-only … -- docs/site` → empty), so the wave *creates*
source/built drift under the reading that says drift is no longer tracked.

The site edits themselves are in the safe direction and I record that: the
results page **removes** the ≈47.2 J/request, ≈44.4 J/request and 86.8
mJ/token readouts rather than restating them. **[partly delegated]**

### S5 — the NEG-8 contract narrowing rests on a repository-scoped absence argument

`docs/contracts/adapter_contracts.md:411-425` replaces *"A v1 artifact with an
authentic pre-addendum seal but no freshness block is replay-readable only to
produce that stale refusal"* with *"an artifact without the freshness block is
therefore malformed"*, on the stated premise that *"the dual-family shape and
freshness block were introduced together and no pre-freshness dual-family
artifact was issued."* The code follows:
`joulewise/whole_window.py:1647-1652` drops `frozenset(base_keys)` and
`frozenset(base_keys | {"launch_lineage"})` from the accepted wire shapes, and
`:1684` now returns `False` when `freshness` is absent.

Counterfactual (E13): `grep -rl "claim_family_bounds" --include="*.json" .`
returns no hits — the premise holds *for the repository*. It is untested for
artifacts held in external run-bundle or transaction custody. If one exists,
`load_neg8_drift_bound_artifact` (`whole_window.py:1737`) returns `None` and
`_validate_row_uncached` (`:5438`) emits
`whole_window_verdict_provenance_invalid` instead of the registered
`neg8_drift_bound_stale` — a refusal with the wrong diagnosis, which is worse
than the refusal itself.

Cure: state the scope of the search that established the premise, in the
contract text, so a future reader knows what was and was not checked.

### S6 — the fence one-name-sweep kept has no mutation kill **[delegated]**

The three fail-closed legs the D-161 re-scope preserved are present and
correctly ordered — every `raise` precedes the `warnings.warn` at
`tests/test_issue_dg071_dg075_statistics.py:125`, so the warn downgrade does
not swallow them (`:76` current script bytes vs stored `script_sha256`; `:89`
`git show <stored_commit>:<script_path>` vs the same digest; `:111`
regenerated-payload byte equality). Module green: `Ran 30 tests … OK`.

The defect is that `_verify_asymmetric_replay` is called from exactly one
happy-path site (`:1060`). Counterfactual executed by the delegated seat in a
`/tmp` copy: replacing all three conditions with `if False:` still yields
`Ran 1 test in 0.322s / OK`. The fence is present today and undetectable if
deleted tomorrow. Cure: a tampered-blob and a mutated-payload negative case.

### S7 — MODULARITY-01 landed in wave 2 although its ruling assigned it to the P3 lane, after the paper

`01-magistrate-rulings.md`, MODULARITY-01 row: *"Runtime-owned prompt
realization with runtime-neutral provenance; authenticated sibling estimator
(both recommendations adopted); **P3 lane, after the paper**."* The rulings
file carries no amendment, yet the landing is in this tree
(`joulewise/detection_floor_registry.py`,
`configs/analysis_registry/detection_floor_closed_sets.v1.{json,sha256}`,
`configs/campaigns/p2_015_floors/*`, `tests/test_modularity.py`,
`docs/design/modularity_01.md`).

This is a magistrate question, not a defect I can adjudicate: either the
ordering was re-ruled somewhere I did not find, or a P3-lane row jumped the
paper. I record it because sequencing rulings are exactly what a counter-review
should not let pass silently. The work itself is clean (E2, E4).

---

## Nits

- **N1 (implementation-encoding test)** — `tests/test_git_fixture_maintenance.py:78-86,110-114`.
  The guard matches on *spelling*, not on the contract. It fires on
  `function in {"subprocess.run", "_run", "_run_fixture_command"}` and on any
  list or tuple whose first string literal is `"init"`, and its exemptions are
  a hardcoded `path → scope-name` map (`:23-30`). A helper renamed from `_run`
  evades it; `sh -c "git init"` evades it; a file rename silently voids an
  exemption. The contract it should encode is "every disposable repository
  carries the four maintenance controls" — which is observable from the
  repository the fixture produced, not from how the call was written. It found
  six real sites (B1), so it earns its place; it will decay.
- **N2** — `joulewise/identity_pins.py:2009`: a purely cosmetic re-wrap of one
  call in a D-131-bearing module. No behaviour change; needless diff surface on
  a governed file.
- **N3 [delegated]** — `joulewise/workload_sizing.py:1`: no production importer
  anywhere in `joulewise/`, `scripts/`, or `configs/`; exercised only by its own
  test. Inert today, and exactly the shape later mistaken for authority. Give it
  a caller or move it out of the production package.
- **N4 [delegated]** — `configs/campaigns/d117_contrast_v5/generate_configs.py:2787`:
  `observed` is built under `if isinstance(unit, Mapping)`, so a non-Mapping
  element appended to `identity_units` is dropped and the exact-set comparison
  still passes. Not an evidence fence under D-161; recorded only.
- **N5** — asymmetric handling of a registry failure:
  `joulewise/analysis_manifest_v3.py:3732-3739` wraps `validate_floor_artifact`
  in `except Exception` and raises a registered
  `analysis_finalization_floor_dependency_unsatisfied`, while
  `joulewise/analysis_engine/inputs.py:895` does not — a
  `DetectionFloorRegistryError` there propagates as a bare `ValueError`
  subclass. Fail-closed either way (it crashes rather than admits), but only
  one path produces a named refusal.

---

## Verified — claim-bearing surfaces that came through clean

Recorded positively, because "no finding" on a claim surface is a result:

1. **`joulewise/reduce.py` is byte-identical to `origin/main`** (E1). Both
   blobs are `82449d5820…`, and the file is untouched by the wave-2 delta.
   The CUSTODY-HARDEN-01 remand condition is satisfied. The compensating
   contract text added at `docs/contracts/adapter_contracts.md:691-697`
   correctly states that reducer-local eligibility is not claim authority and
   that the campaign/whole-window and analysis-input boundaries reopen the
   custody-bound config independently.
2. **The new detection-floor registry does not widen any closed set** (E2).
   `configs/analysis_registry/detection_floor_closed_sets.v1.json` declares
   exactly the nine metric/window pairs of the retired `FLOOR_METRIC_CATALOG`
   and exactly the four scopes of the retired `_CALIBRATION_SCOPES`. Its
   loader is fail-closed three ways: unreadable file, sidecar mismatch, and a
   source-pinned trust anchor (`FROZEN_REGISTRY_SHA256`) that stops an editor
   from re-blessing changed declarations by also editing the sidecar
   (`detection_floor_registry.py:119-127`). Exact-key checks and
   prefix/window-class agreement are enforced per row.
3. **Pre-registered campaign bytes are unchanged.** The three d117 generators
   reproduce 352 files byte-for-byte against `origin/main` (E3), and the
   MODULARITY-01 rewrite of `configs/campaigns/p2_015_floors/generate_configs.py`
   — a 568-line change to a *pre-registered* generator — regenerates all 282
   frozen configs byte-identically (E4). This was the largest single risk in
   the delta and it is clean. Note for the record: the parity *script* covers
   only the three d117 generators; the p2_015 check above is this seat's, not
   an automated gate.
4. **No pinned floor, threshold, or paper-facing constant moved.** The
   `PROJECT_STATUS.md` numbers (0.7–1.0 J boundary, 0.29–0.49 J repeatability,
   ~50 J points, ~5 J clearable) match D-078 clause 11; the site results page
   removes numbers rather than adding them; `results-fill-registry.md` hash
   updates match the scripts they name and no status word moved off
   `STOP_FILL`. **[delegated, spot-checked here]**
5. **The D-161 re-scopes landed as ruled** (mine + **[delegated]**):
   COLDGATE-HANDOFF-01's single metamorphic test
   (`tests/test_validate_gate_packet.py:279`) asserts all four required legs
   per encoding, with three genuinely distinct encoders, and no residual code
   treats JSON spelling as a safety condition; the p1-rows bespoke
   row-disposition module is absent from HEAD; the generic runtime D-131
   dispatch is gone while the generator-owned unconditional roster check
   survives at `configs/campaigns/d117_contrast_v5/generate_configs.py:2759`,
   called at `:3166` before `plan_tree.json` is written, with the ruled
   C/D-rename + A/B-producer-swap mutation asserting the tree was never
   published (`tests/test_gamma_unit_roster_guard.py`, OK);
   FLOOR-WORKLOAD-SIZING-01's residue is genuinely archival.
6. **GENERATOR-CORE-01's ruling is honoured in both directions.** Parity holds
   (E3), and `docs/specs/generator_core.md:90-91` states the seam regressions
   "guard against accidental divergence by a maintainer; they are not an
   adversarial guard" — the exact softening the ruling required.
7. **The doctrine-shaped change in the delta went through a cold gate.** D-172
   (`docs/decision_log.md` §D-172) was adopted on a cold Fable gate's amended
   text with Ed notified and holding a veto — rule 11 satisfied. The
   `docs/orchestration.md` rule-11 topology section and the retirement of
   `docs/planning_reflection_protocol.md` to a D-063 compatibility pointer are
   descriptions of already-adopted decisions, not new policy.
8. **Delta test modules run this session are green** except the one in B1:
   459 + 178 tests OK, plus `test_whole_window`/`test_whole_window_selection`/
   `test_check_window_provenance`/`test_run_campaign` and
   `test_paper_round7_artifacts` at exit 0, and `test_docs_freshness`
   31 tests OK **[delegated]**. Round-3 refuter findings R3-F1 (doc008
   sign-off), R3-F3 (R7F path), R3-F4 (ARM clock) are cured; R3-F2 is not (B1).

---

## What this seat could not test

- Whether a pre-freshness dual-family NEG-8 artifact exists outside the
  repository (S5). Repository-scoped absence is all that was checkable here.
- The full-suite replay. The magistrate's replay runs separately; only
  claim-touching modules were run here, per brief.
- The Sol contract refuter's round 4, running concurrently and deliberately
  not read.
