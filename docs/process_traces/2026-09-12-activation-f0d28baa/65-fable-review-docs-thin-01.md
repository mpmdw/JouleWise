# 65 — Fable 5.1 read-only review: DOCS-THIN-01 (branch chore/2026-09-10-docs-thin)

HEAD 29dbc537 (origin/main 686e0ad8 is an ancestor). Worktree clean. Read-only throughout; nothing edited, no git writes.

**VERDICT: FIX-FIRST (four small mechanical fixes, then READY FOR DRAFT PR).** Nothing live, pinned, or code-bearing is broken; tests and the kernel check pass. The fixes are unrepaired links the note claims are done, plus two inaccurate claims in the note.

## 1. Nothing LIVE was moved — CONFIRMED

Method: extract every `docs/...`-shaped path from each group, `stat` it, count only misses whose target now exists under `docs/legacy/` (a "moved-target miss"); placeholders like `docs/phase_N` are not counted.

| Group | files | path refs | unique | moved-target misses |
|---|---:|---:|---:|---:|
| `docs/process/state_kernel.json` | 1 | 632 | 144 | **0** |
| `docs/contracts/**` | 31 | 101 | 48 | **0** |
| runbooks + NIGHT_HANDBACK + MAGISTRATE_* | 5 | 48 | 19 | **0** |
| README, AGENT_PLAN, PROJECT_STATUS, CLAIMS_STATUS | 4 | 78 | 47 | 2 (CLAIMS_STATUS.md L68, L161 — see §2) |
| RUN_STATE.md, TASK_QUEUE.md (edit-excluded) | 2 | 1295 | 350 | 40 |
| decision_log, council_log (edit-excluded) | 2 | 379 | 222 | 50 |

The 40 in RUN_STATE/TASK_QUEUE are all in superseded blocks: RUN_STATE's first is at L1827 (T7 checkpoint, "kept as record"); lines 1–1826 cite zero moved paths. TASK_QUEUE's six are at L182–203 under "Completed Queue Items"; its Current Queue and Active Gates sections cite only directories that still exist. The 50 log citations resolve by the `docs/X -> docs/legacy/X` rule, as the note intends. All 309 renames obey that rule (script-checked, 0 violations). The armed night's clone was not read.

## 2. Moved-file links in live documents — INCOMPLETE ("six repairs" is an undercount)

Existence-filtered scan of every tracked file outside `docs/legacy/`, history dirs (process_traces, run_reports, stream_logs, reviews, site, advisor_briefs), and code. Live documents still citing a moved path by its old name:

- `CLAIMS_STATUS.md` L68 (`2026-08-06-d110-remint-fork/`), L161 (`2026-08-03-winB-reeval-stop/`) — root live doc, NOT on the exclusion list. FIX.
- `docs/phase_2/three_night_freeze_manifest.md` L52 (`2026-08-07-d117-plan-freeze/DESIGN-MEMO.md`). FIX.
- `docs/strategy/2026-08-09-extension-axes-roadmap.md` L354, L546, L678; `2026-08-08-40h-plan.md` L24, L33; `2026-08-14-70h-plan.md` L20; `2026-08-07-three-night-operator-packet.md` L6. FIX (repair, or archive the three dated plans — §6a).
- `docs/project_critique_review.html` L880 (`docs/test_audit_2026-07-07.md`) — read by `pack_capsule.py`; optional.
- `docs/specs/axi/sb_static_batch_verdict.md` L6, L200; `sc_spec_decode_verdict.md` L7, L280 — frozen verdicts citing evidence-with-SHA-256; leave (record), lookup rule applies.
- `docs/paper/results-fill-registry.md` L132 and `docs/paper/draft-v1-review-round2-lensA.md` (8 lines) — `docs/paper/**` is edit-excluded; hand to the paper lane, not this branch.

Code (scripts/tests/configs/joulewise/.github): zero hits on moved paths.

## 3. Excluded paths — CONFIRMED

`git diff origin/main...HEAD --stat -- joulewise scripts configs tests` → `tests/test_docs_freshness.py | 2 ++`, one file. The diff adds, inside `_decision_reference_documents`:
```
+        # DOCS-THIN-01: archived history stays outside the live reference scan.
+        and not path.relative_to(root).as_posix().startswith("docs/legacy/")
```
The note's own exclusion grep prints nothing. Census: 309 R, 7 A (legacy README + six thread files), 5 M (README, bridge_protocol, alpha_arm_readiness, window_runbook, the test).

## 4. Tests — PASS (venv python3, dotted names, this reviewer's run)

- `tests.test_docs_freshness`: `Ran 31 tests in 0.494s — OK`
- `tests.test_gen_state`: `Ran 44 tests in 1.705s — OK`
- `scripts/gen_state.py --check`: rc 0

## 5. Freshness scan set — NOT byte-identical; the note's claim is wrong in a harmless direction

Reproduced the glob rules against `git ls-tree` of origin/main and HEAD (HEAD tree = on-disk set, 402 = 402). Main scans **459** documents; the branch scans **402**. The 57 dropped are all archived `.md` files that were never under `process_traces/`: 52 in `docs/strategy/2026-08-07-paper-portfolio/`, plus `docs/advisor/2026-08-27-session-brief.md`, `docs/evidence/.../EVIDENCE.md`, `docs/instrument-v2-lessons.md`, `docs/research_question_coverage-2026-08-28.md`, `docs/test_audit_2026-07-07.md`. Nothing new entered (0). Without the fix, 282 legacy files would have been swept in (684 total) — the trap is real and the fix prevents it. Correct the note/PR text: "the scan shrinks by 57 archived documents; no live document leaves it."

## 6. Far enough / too far

(a) Live but archive-shaped, not archived:
1. `docs/process_traces/2026-08-07-plan-factory/` — 17.9 MB, nine raw Codex transcripts (DRAFT-QUANT_GATES 4.5 MB, -REASONCODE 3.9, -NEVERZERO 3.4, -U8 1.5, -MOE_GATES 1.1, -U4, -PROBES, -PAPER-REFUSAL-SECTION). Only `DRAFT-U5U7.md` (configs d117 plan_tree/generate_configs, `tests/test_d117_decode_contrast_plan.py:2158`) and `DRAFT-RESULTS_PROSE.md` (`configs/campaigns/metrology_v1/characterization_result_schema_v1.json`) are pinned. The other seven (~15.7 MB) are the nine largest live files under `docs/` and roughly a quarter of the 62.7 MB live surface. Moving them splits a directory — Ed's call.
2. `docs/strategy/2026-08-08-40h-plan.md`, `2026-08-14-70h-plan.md`, `2026-08-07-three-night-operator-packet.md` — finished/superseded dated plans, unpinned.
3. `WINDOW_STATUS.md` (2026-08-20 narrative) — script-owned (`window_status.sh`, `test_window_status_guard.py`); needs Ed, as the note says.
4. `docs/run_reports/` (106 files, 1.5 MB, 2026-06..08) and `docs/site/` (1.6 MB generated HTML of the retired D-136 lane, now carrying stale links) — need a script change; correctly deferred.

(b) Archived, but a fresh reader may want at the old spot:
1. `docs/advisor/2026-08-27-session-brief.md` — the newest advisor-facing brief; the older 2026-07-30 brief stays live in `docs/advisor_briefs/`. Consider `docs/advisor_briefs/` instead of legacy (Ed).
2. `docs/process_traces/2026-08-07-d117-plan-freeze/DESIGN-MEMO.md` — defines the freeze units; three live docs plus the paper registry cite it.
3. `docs/evidence/d117-v2-decisive-20260811/` — cited as evidence in decision_log L174; 5.5 KB of test logs, so lookup suffices.

## 7. Exact fixes before the draft PR
1. Repair links: CLAIMS_STATUS.md L68, L161; three_night_freeze_manifest.md L52; the four docs/strategy files (7 lines) or archive the three dated plans.
2. RESUME/README/PR text: "309 renames" (git), not 376; replace "byte-identical" with the §5 wording.
3. List the docs/paper dangling lines (§2) as a hand-off to the paper lane in the PR body.
4. Optional: project_critique_review.html L880.
