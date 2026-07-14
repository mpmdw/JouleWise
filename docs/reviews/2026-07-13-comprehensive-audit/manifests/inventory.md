# Batch 0 inventory — §7 coverage-table draft

Census: `git ls-tree -r --name-only e3fc14a01ca047e779fa7924fdf128b25762d063` = 443 tracked
files (audit object is the pinned tree; current HEAD `bd36dff` differs only by the audit
charter itself, which belongs to no scan manifest). LOC via `wc -l` at the pinned working
tree — routing context only, never evidence.

## Invariant

census 443 = domains 275 (D1..D7) + excluded 168. Verified mechanically (assignment
script covered every path; zero unrouted). Walk invariants verified: no file in more than
one walk; every walk file is domain-assigned (non-excluded).

## Domain manifests

| Domain | Files | LOC | Notes |
|---|---|---|---|
| D1 run lifecycle / evidence kernel | 30 | 9,485 | joulewise kernel modules, configs/examples, pyproject, CI, env/*, backup_runs.sh, 3 contracts |
| D2 platform boundaries | 16 | 9,322 | interfaces.py + 11 adapters, mlx spike script, 2 contracts, nv-gate-2 spec |
| D3 campaign / workload orchestration | 32 | 19,196 | suite/workloads/gensuite, campaign scripts, suite+campaign configs, campaign_packs, suite_next specs |
| D4 reduction / analysis / claims | 33 | 22,976 | reduce+aggregate, analysis_engine (9), gates, floors, claims_lint, 4 contracts, c027 analysis specs |
| D5 reporting / packaging / site | 36 | 9,388 | report.py, privacy, site/pack scripts, site_capsule (8), report_src (18), rpt-001 spec |
| D6 test portfolio | 72 | 48,302 | all tests/** incl. 6 fixture files |
| D7 governance / process stack | 56 | 23,058 | top-level process docs, bridge+codex tooling (7 scripts), state kernel, phase plans (13), registries, decision/council logs (current operating surfaces) |
| **Total** | **275** | **141,727** | |

## Seam-walk manifests (subset of domain-assigned files; ≤1 walk per file)

| Walk | Files | LOC |
|---|---|---|
| W1 one-run lifecycle | 30 | 17,439 |
| W2 campaign-to-claim | 40 | 33,968 |
| W3 local-to-remote / future-split | 14 | 8,507 |
| W4 clean-clone-to-publication | 34 | 9,792 |
| W5 authority-to-enforcement-to-test | 18 | 16,244 |

## Exclusions (168 files, 29,748 LOC)

| Reason | Files | Main groups |
|---|---|---|
| historical | 126 | docs/run_reports (62), docs/stream_logs (32), docs/reviews pre-audit (20), docs/process_traces (8), hardening proposal, critique pair, test_audit_2026-07-07 |
| generated | 41 | docs/site (30), analysis/rpt001-v1 (9), figures (1), report_src/generated (1) |
| legal | 1 | LICENSE |

Flag for lead ratification: `analysis/rpt001-v1/**` (9) and `figures/**` (1) are excluded
as generated (machine-produced, regenerable, checked-against-generator per the charter's
mirror rule) — but they are also pinned claim-evidence artifacts; if the lead wants them
line-audited they belong to D4/D5 with W2.

## Shape of the repo (10 lines)

1. Tests are the single largest body of code: 48.3k LOC across 72 files vs 34.6k LOC in joulewise/ — test-to-source ratio ~1.4:1 (~0.98:1 if scripts/ counts as source).
2. Largest tracked file is a test: tests/test_run_campaign.py at 3,675 LOC, paired with the largest script, scripts/run_campaign.py at 2,917 LOC.
3. docs/ dominates the file census (247/443, 56%); more than half of docs is excluded historical/generated record (run_reports 62, stream_logs 32, site 30).
4. The governance/process stack (D7) is 23.1k LOC of CURRENT surface — comparable in size to the entire analysis domain (D4, 23.0k) — with docs/decision_log.md alone at 3,377 lines.
5. Analysis (D4) is the largest production-code domain; analysis_engine/artifact.py (2,335) and scripts/claims_lint.py (2,118) are the biggest modules.
6. Suite-manifest configs are heavy JSON: two suite manifests approach 2.8-2.9k lines each; configs/ totals 9.7k LOC.
7. Adapter layer (D2) is compact: 11 adapters + interfaces in 9.3k LOC, largest being node_worker.py (1,882).
8. Bridge/orchestration tooling is nontrivial code: scripts/bridge is 2,262 LOC of tracked process infrastructure.
9. Reporting/publication (D5) is broad but thin: 36 files, 9.4k LOC, spread across report_src chapters and the live site_capsule.
10. W2 (campaign-to-claim) is the fattest seam at 40 files / 34k LOC; W3 (remote/future-split) the thinnest at 14 files / 8.5k.
