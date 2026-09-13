```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "No blocker found. One should-fix first-use audit regression and one README nit; requested checks pass, while opt-in site tests expose pre-existing failures.",
  "workspace": {
    "base_requested": "76a2f2a73be3f5337155730fb88ce5ff555d19d0",
    "base_mode": "exact",
    "head_start": "76a2f2a73be3f5337155730fb88ce5ff555d19d0",
    "head_end": "76a2f2a73be3f5337155730fb88ce5ff555d19d0",
    "upstream_end": "76a2f2a73be3f5337155730fb88ce5ff555d19d0",
    "branch": null
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "findings": [
      {
        "id": "F1",
        "severity": "should_fix",
        "site": "docs/paper/protocol/first-use-audit-ledger.md:141",
        "summary": "New audience-vocabulary dispositions bypass the ledger's explicit category definition and leave binary64 used before its moved definition.",
        "related_sites": [
          "docs/paper/protocol/first-use-audit-ledger.md:5",
          "docs/paper/protocol/first-use-audit-ledger.md:149",
          "docs/paper/draft-v2-skeleton.md:740",
          "tests/test_paper_first_use_ledger.py:399",
          "tests/test_paper_first_use_ledger.py:510"
        ],
        "minimal_cure": "Gloss binary64 at line 740, split its grouped ledger row, classify resolution bound as glossed at its existing protocol definition, and enforce audience-category membership in the audit test."
      },
      {
        "id": "F2",
        "severity": "nit",
        "site": "README.md:12",
        "summary": "The current Next sentence still directs merging the paper pass after PR #331 has merged.",
        "minimal_cure": "Remove the completed merge step from the Next sentence."
      }
    ],
    "same_signature": {
      "answer": "yes",
      "site": "docs/paper/draft-v2-skeleton.md:740; docs/paper/protocol/first-use-audit-ledger.md:141",
      "reason": "F1 repeats term-before-build and an audit disposition certifying more than its consumer verifies. No new runtime or numeric-replay integration defect was found."
    }
  },
  "verification": [
    {
      "id": "V1",
      "kind": "suite",
      "cmd": "R7F_CORPUS_ROOT=/Users/edr/code/JouleWise PYTHONDONTWRITEBYTECODE=1 JOULEWISE_BACKUP_ROOTS= python3 -B -m unittest tests.test_paper_first_use_ledger tests.test_paper_terms_lint tests.test_paper_replay_fence tests.test_check_paper_replay_fence tests.test_paper_round7_artifacts tests.test_docs_freshness tests.test_d165_rationale_census tests.test_gen_state tests.test_paper_successor_migration tests.test_build_site_parsers",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "----------------------------------------------------------------------",
          "Ran 244 tests in 499.318s",
          "",
          "OK (skipped=30)"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "OK \\(skipped=30\\)"
      }
    },
    {
      "id": "V2",
      "kind": "lint",
      "cmd": "python3 -B scripts/gen_state.py --check",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": []
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "^$"
      }
    },
    {
      "id": "V3",
      "kind": "test",
      "cmd": "python3 -B scripts/check_paper_replay_fence.py --literals-only --draft docs/paper/draft-v1.md",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "LITERALS 22 extracted from docs/paper/draft-v1.md",
          "INTERNAL MISMATCHES 0"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "INTERNAL MISMATCHES 0"
      }
    },
    {
      "id": "V4",
      "kind": "test",
      "cmd": "python3 -B scripts/check_paper_replay_fence.py --literals-only --draft docs/paper/draft-v2-skeleton.md",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "LITERALS 22 extracted from docs/paper/draft-v2-skeleton.md",
          "INTERNAL MISMATCHES 0"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "INTERNAL MISMATCHES 0"
      }
    },
    {
      "id": "V5",
      "kind": "suite",
      "cmd": "JOULEWISE_SITE_CONTENT_TESTS=1 PYTHONDONTWRITEBYTECODE=1 JOULEWISE_BACKUP_ROOTS= python3 -B -m unittest tests.test_build_site_parsers tests.test_pack_capsule tests.test_claims_lint tests.test_select_outcome_branches",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": [
          "scripts.build_site.SiteBuildError: project status split: PROJECT_STATUS.md: expected exactly one <!-- ADVISOR-PAGE-END --> marker",
          "",
          "----------------------------------------------------------------------",
          "Ran 108 tests in 8.316s",
          "",
          "FAILED (errors=3, skipped=3)"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "OK"
      }
    },
    {
      "id": "V6",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest tests.test_paper_excursion_decomposition.BackupHelperIdentityTests tests.test_arm_readiness_schemas.ProductionCustodyResolverTests.test_backup_override_cannot_shrink_census_and_three_script_literals_stay_pinned",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "----------------------------------------------------------------------",
          "Ran 2 tests in 0.075s",
          "",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "OK"
      }
    }
  ],
  "flags": [
    {
      "id": "R1",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "V1 skips all 30 site tests. Explicitly enabling them in V5 exposes three pre-existing PROJECT_STATUS parser errors: missing Status At A Glance heading and missing ADVISOR-PAGE-END marker. PROJECT_STATUS.md, both site/pack scripts, and the site parser test module are byte-identical to c53d4227; both underlying errors reproduce against that base. Changed README/RUN_STATE/TASK_QUEUE content renders successfully in memory.",
      "needs": "Keep the existing site incompatibility separate from PR #331; do not report the complete site build as passing."
    },
    {
      "id": "R2",
      "kind": "environment",
      "level": "nonblocking",
      "text": "Opt-in site verification skips pinned Marked, Lakebed, and esbuild integration because their local dependencies are absent. No dependencies were installed, no paper build was run, and no repository files were modified.",
      "needs": ""
    }
  ]
}
```

## Findings

**No blocker found.**

**F1 — should-fix: the audit accepts newly exempted terms without enforcing its exemption rule.** At `docs/paper/draft-v2-skeleton.md:740`:

> “The event-duration statistic subtracts binary64 epoch values before rounding”

Before this PR, “binary64, the usual 64-bit floating-point format” preceded that use at base line 425. Its first remaining definition is now at line 979.

The changed ledger row at `docs/paper/protocol/first-use-audit-ledger.md:141` instead assigns:

> “binary64 / member-envelope integral sum … audience-vocabulary”

Neither term belongs to the header’s “that class here is exactly” list at line 5. Newly reclassified “resolution bound” at line 149 also falls outside that list, although its protocol first use already supplies a definition.

The consumer at `tests/test_paper_first_use_ledger.py:510` checks only that the **status name** belongs to `STATUSES`; the glossary checker at line 399 iterates predefined requirements, which omit the binary64 group. Consequently, the requested tests pass despite this discrepancy.

Minimal cure: add the short binary64 gloss at line 740, separate the two ledger terms into their actual homes, restore `glossed-at-first-use` for the already-defined resolution bound, and check audience-category membership.

**Same signature: YES.** F1 repeats the term-before-build mechanism identified in records 16/21 and the over-certifying audit disposition discussed in records 21/28. Record 28’s round-3 edited-site check did not establish correctness at line 740. Escalation disposition remains the lead’s decision.

**F2 — nit: stale post-merge next action.** `README.md:12` says:

> “Next: merge the paper pass under the twelve-row gate”

At the requested two-parent merge, that action is complete. Delete that step. The renderer preserves this stale text; it does not choke on it.

The consumers census follows. “OK” means agreement with this PR’s changes, not blanket certification of an entire subsystem.

| Reader and quoted dependency | Assessment |
|---|---|
| `scripts/check_paper_replay_fence.py:174`: `(?:Subtracting the two printed bounds gives\|largest pulse residual before the anchor term is)` | **OK:** both prose forms extract; V3/V4 pass. |
| `tests/test_paper_replay_fence.py:139`: `self.assertEqual(v1_literals, self.literals)`; line 143: `"the retained largest pulse residual is not this subtraction result"` | **OK:** equal numeric dictionaries and corrected v2 wording are pinned. Record 28’s SF-28-2 is cured. |
| `scripts/check_paper_round7_artifacts.py:47`: `Path("docs/paper/draft-v2-skeleton.md")`; line 1047: `skeleton_path.read_text(...)` | **OK:** placement, registry and retained-producer replay pass in V1. |
| `tests/test_paper_round7_artifacts.py:40`: `"draft-v2-skeleton.md"`; line 1516: `415` | **OK:** moved prose retains the registered artifact contract. |
| `tests/test_paper_terms_lint.py:18`: `"draft-v2-skeleton.md"`; line 42: `"## 3. How the method quantifies assigned-energy sensitivity"` | **OK:** moved enclosure example and revised figure order are consumed at their new locations. |
| `tests/test_paper_first_use_ledger.py:12,19,23`: `"draft-v2-skeleton.md"`, `"built-terms-lexicon.md"`, `"first-use-audit-ledger.md"` | **F1:** semantic exemption gap. Otherwise the header parses, 262 rows load, and all nine protected tuple strings remain present. |
| `tests/test_paper_first_use_ledger.py:458`: `lines.index(TABLE_HEADER, ledger_line + 1)` | **OK:** searches for the table header, so the inserted rule paragraph does not shift a fixed-offset parser. Ledger preamble is excluded from audited body text. |
| `tests/test_paper_successor_migration.py:50`: `_parse_ledger(article + "\n" + protocol + "\n" + ledger)`; `tests/test_select_outcome_branches.py:12`: `"docs/paper/draft-v2-skeleton.md"` | **OK:** assembled audit, selector, abstract and copying checks pass. |
| `scripts/paper_terms_lint.py:25–26`: `"resolution bound"`, `"detection floor"`; line 545: `not cells[1].isdigit()` | **OK:** deliberately retained lint vocabulary; loader consumes the numeric-line historical base, not successor home labels. Loaded 430 historical entries. |
| `tests/test_d165_rationale_census.py:34`: `"tests/fixtures/d165_rationale_allowlist.json"`; line 167: `(entry["path"], entry["line"], entry["phrase"])` | **OK:** updated line 1525 contains the Figure A2 `"common-time line"` caption. Exact census passes. |
| `tests/test_paper_excursion_decomposition.py:24`: `"check_paper_replay_fence.py"`; `tests/test_check_paper_replay_fence.py:6`: `shared.SCRIPT.with_name(...)` | **OK:** shared backup-helper bytes and backup-discovery behavior remain compatible; V1/V6 pass. |
| `tests/test_arm_readiness_schemas.py:1768`: `"check_paper_replay_fence.py"`; line 1769: `self.assertIn(spec.value, ...)` | **OK:** external custody-root literal remains present; focused V6 passes. |
| `scripts/build_site.py:159,163–164`: `DocPage("README.md"...)`, `DocPage("RUN_STATE.md"...)`, `DocPage("TASK_QUEUE.md"...)`; line 2071: `path.read_text(...)` | **OK parser / F2 content:** all three changed documents render in memory. No paper or ledger page is selected by this generator. Full build has the separate baseline failure described below. |
| `scripts/gen_state.py:835–836`: `_read(path)` and `replace_region(...)`; `tests/test_gen_state.py:807,876`: `"TASK_QUEUE.md"`, `"RUN_STATE.md"` | **OK:** generated marker regions remain synchronized; V2 succeeds silently. |
| `tests/test_docs_freshness.py:22`: `("README.md", "PROJECT_STATUS.md", "docs/orchestration.md")`; lines 295–297 include the three changed state surfaces | **OK:** freshness and reader-facing literal rules pass. They do not detect F2’s completed action. |
| `scripts/claims_lint.py:836`: `("README.md", "PROJECT_STATUS.md")`; `tests/test_claims_lint.py` | **OK:** README is a real non-paper consumer; its tests pass in V5. Pack-local `README.md` references elsewhere name different files. |
| `scripts/pack_capsule.py:483`: `sorted(SITE.glob("*.html"))`; `tests/test_pack_capsule.py:66`: `"TASK_QUEUE.md · commit ..."` | **OK dependency:** consumes rendered HTML and provenance, not paper wording or ledger layout. Integration limitations remain below. |
| `.github/workflows/site.yml:34`: `tests.test_build_site_parsers tests.test_pack_capsule`; `ci.yml:66`: `shard_tests.discover_test_modules()` | **OK:** changed tests remain discoverable. Site tests require their explicit opt-in flag. |
| `joulewise/powermetrics_fiducial.py:994`: `"never a truncated accepted region"`; `tests/test_calibration_bracketing.py:2815`: `"complete accepted region"` | **OK:** independent detector vocabulary; neither reads the paper or depends on the former “allowed region” label. |
| `scripts/mint_floor_artifact_generalized.py:2544`: `"report cell floor differs"`; line 4061: `"multi-cell floor mint requires..."`; `scripts/render_results_fills.py:611`: `"Because no operative cell floor exists"`; corresponding mint tests | **OK:** artifact terminology is unchanged; no paper-text dependency. |
| `tests/fixtures/paper_first_use_pre_cure.md:195`: `"largest pulse residual before the anchor term is"`; lines 644–646: `"resolution bound"` / `"cell floor"` | **OK:** intentionally historical negative fixture. Frozen-v1 readers, including `scripts/dependence_sensitivity.py:72`, still target `"draft-v1.md"`. |
| `docs/site/index.html:17`: `"below the detection floor"`; `claims_ladder.html:1`, `council_log.html:1`, `record.html:1`, `advisor_brief.html:753` | **OK relative to PR:** independent or historical detection-floor wording; these files are byte-identical to the base. No searched `Table 4/A4`, `P_rest`, subtraction-anchor, paper-path or ledger-path consumer occurs there. |

The paper-local pinned SVG still says “eight rows in Table 4” (`docs/paper/figures/figA4_shared_signs.svg:15`), as does its README row 16. The new article caption at line 515 explicitly maps that label to Table A4. This is the already-recorded pinned-figure residue, not a newly missed external consumer.

## Residual risk

The full site build **does fail on main**, but before reaching the new README content: `scripts/build_site.py:802` expects `"Status At A Glance"`, and line 380 requires `"exactly one <!-- ADVISOR-PAGE-END --> marker"`. Both errors reproduce against `c53d4227`; the relevant source and consumer files are unchanged. The opt-in run’s three errors are entirely these baseline incompatibilities.

In-memory checks produced:

```text
IN_MEMORY_RENDER_OK README.md
IN_MEMORY_RENDER_OK RUN_STATE.md
IN_MEMORY_RENDER_OK TASK_QUEUE.md
LEDGER_OK rows=262 header_excluded=True protected_tuple=9
LEXICON_HISTORICAL_LOADER_OK entries=430
```

Pinned Marked, Lakebed and esbuild integration remained unavailable. No paper build, hardware collection or repository edit occurred. No runner output path was supplied; this response is the report. Next exact step: lead disposition of F1/F2, preserving the separate retired-site failure boundary.