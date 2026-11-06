# Canonical entry points (draft)

**Status:** inventory draft, 2026-11-06. This file does not change any seal,
registration, release gate, or measurement instruction. “Canonical” below means
the one present-tree entry point a new operator should start from for the named
job. Historical records remain evidence, not alternate instructions.

## Selection method

I used, in descending order: (1) an explicit current pointer in `RUN_STATE.md`,
(2) the newest governing design or executable in Git history, and (3) actual
imports/calls. Dates below are commit dates from `git log -1 -- <path>`; import
claims are from the named source. A branch-only object is not promoted to a
checkout entry point. This matters for Flash-Next: `RUN_STATE.md:1195-1202`
names branch `port/qwen4-exp-mlx` and its `GOAL.md`, but neither object is in
this checkout.

## One current entry point per job

| Job | ONE current tool or document | Evidence and what it replaced |
|---|---|---|
| ALIGN v4 **R0 measurement window** | `scripts/launch_align_r0.py` | Newest R0 executable (last changed by `38ebcf4`, 2026-11-06); its module docstring says it hands R0 to a one-shot LaunchAgent rather than measuring in the agent tree (`scripts/launch_align_r0.py:1-2`). It consumes the committed R0 configuration, whose authoritative 300/900/600-second profile and refusal floor are recorded in `docs/align/council-2026-11-05/FINAL-DESIGN-AMENDMENT-2.md:5-10`. **Replaced:** direct/session-owned R0 launch and the 60-second load step described by the base design and Amendment 1 (replacement is explicit at Amendment 2 lines 7-10). |
| ALIGN v4 **R1 measurement window** | `docs/align/council-2026-11-05/FINAL-DESIGN.md` **as amended, in order, by** `FINAL-DESIGN-AMENDMENT-1.md` and `FINAL-DESIGN-AMENDMENT-2.md` | This is one composite design record, not three competing protocols: Amendment 2 says it changes no window design and records facts cited by the R0 directive (`FINAL-DESIGN-AMENDMENT-2.md:1-3`), while its thermal rule forbids R1 policy from naming keys R0 did not classify (`:21-25`). `RUN_STATE.md:1195-1202` says v4 R0 checks and R1 rehearsal are next and folds earlier follow-ups into this v4 plan. **Replaced:** the ALIGN v3 pilot protocol/alternative desk for production planning, and the unamended v4 text wherever an amendment expressly changes it. |
| ALIGN v4 **W1 measurement window** | `docs/align/council-2026-11-05/FINAL-DESIGN.md` **plus Amendments 1 then 2** | Same governing composite as R1. Amendment 1 fixes W1’s D-only capability fallback and bars spending a held-out seed on capability failure (`FINAL-DESIGN-AMENDMENT-1.md:150-157`); Amendment 2 makes the R0-classified thermal keys a prerequisite (`FINAL-DESIGN-AMENDMENT-2.md:21-25`). **Replaced:** v3 pilot window instructions and the base v4 model roster before Amendment 1 made Qwen3.8-27B the only present production model. |
| **Block 5 analysis** | `scripts/run_b5_analysis.py` | The executable calls `joulewise.b5_analysis.dry_run.run` (`scripts/run_b5_analysis.py:75-80`) and documents both governed modes, blind dry run and release, over the same custody root (`:1-35`). Last substantive path change shown by Git is `bfa0103` (2026-11-03). **Replaced:** staged L9/S0-S11 lane scripts and manual per-step execution; those remain in process traces and `.codex-report/` as build/review evidence. |
| **Release** (publication/package release) | `docs/publication_release_checklist.md` | It calls itself the “single ordered publication command/checklist” (`docs/publication_release_checklist.md:1-7`) and makes `python3 scripts/release_check.py --dry-run` the non-secret clean-clone gate (`:21-42`). **Replaced:** treating `scripts/release_check.py` alone, a green smoke, historical six-bundle regeneration, site deployment, or CI as the whole release; credentialed publication remains explicitly manual (`:84-94`). |
| **Independent recompute** | `scripts/independent_recompute_b5.py` | Its header defines an independent, non-issuing, standard-library-only recomputation from archived raw records (`scripts/independent_recompute_b5.py:1-14`); Git history begins at `ab14e02` and most recently changes it at `048085b` (2026-10-28). `RUN_STATE.md:37` (paragraph beginning at line 394) names the independent recompute as the no-shared-code release cross-check. **Replaced:** hand calculations, stored-number copying, and the pre-round-3 recompute branch snapshots described in historical handoffs. |
| **Comparator** (independent recompute versus L9) | `scripts/compare_b5_recompute.py` | Its header says it compares L9 restricted outputs with the independent recompute, imports no repository analysis code, and takes the release bar set (`scripts/compare_b5_recompute.py:1-13`). The latest comparator commit is `d97e55d` (RC-CMP-11, 2026-10-30). **Replaced:** `tools/normalized_compare.py`, `docs/process_traces/2026-11-01-l9-speedup-r1/normalized_compare.py`, and manual/CROSS-CHECK round comparisons. Do not confuse it with `tools/b5_equivalence/compare_b5_results.py`, which is the D-188 *same-analysis result-equivalence* comparator, not the independent-recompute comparator. |
| **Seal and custody verification** | `scripts/digest_pin_census.py` | This is the maintained verifier/registry writer for era-bound seal pins: the seal landing review records its exit 0 and unchanged pin registry (`docs/process_traces/2026-10-07-block5-seal/gates/10-seal-landing-review.md:297`), and the post-seal runbook runs `tests.test_digest_pin_census` together with the seal-landing test (`docs/process_traces/2026-10-07-block5-seal/30-post-seal-runbook.md:686-698`). **Replaced:** one-off seal verification scripts such as `docs/process_traces/2026-09-29-interactive-ff50b201/154-rev6-seal-verification.py`, and manual digest checking. It does **not** replace the governing `SEAL_RECORD.md`; it verifies pinned/era claims about tracked bytes. |
| **Flash-Next `qwen4_exp` MLX port** | `docs/align/council-2026-11-05/FINAL-DESIGN-AMENDMENT-1.md`, §A4 “Slot for adding Flash-Next later” | This is the only current, present-tree port contract. It fixes the separate stack-B identity and full-model parity, memory, template, cache, long-decode, thermal, and window admissions (`FINAL-DESIGN-AMENDMENT-1.md:159-183`). `RUN_STATE.md:1195-1202` says the implementation lives on branch `port/qwen4-exp-mlx` under `GOAL.md`, but that branch/file is absent here; therefore this draft does not pretend a branch-only tool is runnable. **Replaced:** the base design’s “not admitted on the pinned stack” disposition and the earlier “physically infeasible” shorthand; it does not yet replace an upstream runtime implementation. |
| **CI** | `.github/workflows/ci.yml` | This is the sole workflow in `.github/workflows`. It runs on main pushes and PRs (`.github/workflows/ci.yml:1-7`), uses a base-commit docs-only classifier that fails closed (`:60-87`), and owns fences plus the sharded test matrix (`:89-107`, `:127-144`). Last changed by `b876680` (2026-11-01). **Replaced:** deleted `site.yml`, the older multi-version PR matrix, and the six-shard CI described in historical `RUN_STATE.md`/process records. `scripts/ci_docs_only.sh` and `scripts/quick_suite.py` are components, not alternate CI entry points. |
| **Paper** | `docs/paper/draft-v2-skeleton.md` | Its banner identifies it as the selected methods/diagnostic submission draft and points source rows to the results-fill registry (`docs/paper/draft-v2-skeleton.md:1-5`); its title and abstract define the current paper (`:7-31`). **Replaced:** `docs/paper/draft-v1.md` and review-round drafts, the July outline, and staging/rendered fill rehearsals. The registry and artifact guide support this manuscript; neither is a second paper. |
| **RUN_STATE** | `RUN_STATE.md` | It explicitly calls itself the single running pointer and says not to create another dated restart document (`RUN_STATE.md:1-11`). **Replaced:** the three dated `docs/legacy/process_traces/RESUME-2026-07-{26,27,28}.md` restart documents, plus later checkpoint prose as a restart authority. Current entries win over older material within the same file; generated kernel sections remain generated, not hand-edited (`RUN_STATE.md:7447-7454`). |

## Superseded-but-present inventory

These files are useful history, fixtures, or narrower tools, but are **not** the
entry point for the jobs above:

- ALIGN: council briefs and seat reports under
  `docs/align/council-2026-11-05/{00-brief-*,r1-*,r2-*}.md`,
  and the unamended statements in `FINAL-DESIGN.md` that Amendments 1 or 2
  expressly replace.
- Block 5: `scripts/harvest_b5_window.py`, `scripts/produce_b5_disclosures.py`,
  `scripts/b5_phase_report.py`, the `docs/process_traces/2026-10-block5/l9-rulings/`
  stage briefs, and `.codex-report/L9-*.md`. They are inputs, subordinate
  producers, or evidence—not the full analysis runner.
- Recompute/comparison: `tools/normalized_compare.py`,
  `docs/process_traces/2026-11-01-l9-speedup-r1/normalized_compare.py`,
  `tools/b5_equivalence/compare_b5_results.py`, and the RC-CMP reports in
  `.codex-report/`.
- Seal/custody: `docs/process_traces/2026-09-29-interactive-ff50b201/154-rev6-seal-verification.py`,
  `scripts/check_sealed_bundle_compatibility.py`, and historical seal gate
  scripts. The compatibility checker answers a narrower bundle-schema question.
- Release: `scripts/release_check.py` by itself, historical capstone build
  instructions, and generated/deployment notes under `docs/site/`.
- Paper: `docs/paper/draft-v1*.md`, `docs/run_reports/2026-07-30-paper-outline-v1.md`,
  `docs/paper/fill-rehearsal/`, and `docs/paper/round7/` intermediate artifacts.
- Restart state: all dated `RESUME-*` files and historical checkpoint/resume
  sections inside `RUN_STATE.md`; they remain audit history only.

## Known gap

The requested Flash-Next implementation cannot be named as a current checkout
tool without inventing evidence: the current tree has no `GOAL.md`, no
`qwen4_exp` implementation, and no local or remote branch named
`port/qwen4-exp-mlx`. Until that branch is merged, §A4 is the canonical
present-tree contract and `RUN_STATE.md:1195-1202` is the branch pointer.
