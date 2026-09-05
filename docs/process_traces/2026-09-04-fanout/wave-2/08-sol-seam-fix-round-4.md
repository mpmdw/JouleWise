```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "blocked",
  "completion": "partial",
  "summary": "Applied every unambiguous allowlisted wave-2 seam cure; W8 needs the actual contract path added to scope and PHASE-SHARE needs a ruling because its kernel row was already retired.",
  "workspace": {"base_requested":"19e7aa8e2e74a7b6fb872d0ebc4b524376802dd5","base_mode":"exact","head_start":"19e7aa8e2e74a7b6fb872d0ebc4b524376802dd5","head_end":"19e7aa8e2e74a7b6fb872d0ebc4b524376802dd5","upstream_end":"19e7aa8e2e74a7b6fb872d0ebc4b524376802dd5","branch":"int/2026-09-04-fan-wave-2"},
  "pathspec": ["PROJECT_STATUS.md","README.md","TASK_QUEUE.md","docs/milestones.md","docs/process/state_kernel.json","docs/process_traces/2026-09-04-fanout/wave-2/08-sol-seam-fix-round-4.md","docs/risk_register.md","scripts/check-bridge-docs.mjs","tests/test_bridge.py","tests/test_install_magistrate_watchdog.py","tests/test_install_night_agent.py","tests/test_issue_dg071_dg075_statistics.py","tests/test_magistrate_watchdog.py","tests/test_magistrate_watchdog_cli.py","tests/test_run_night.py","tests/test_s0_line_audit_guard.py"],
  "unowned_dirty": [],
  "verdict": {"implementation":"partial","acceptance":"needs_ruling"},
  "verification": [
    {"id":"V0","kind":"test","cmd":"PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_git_fixture_maintenance","cwd":".","observed":{"result":"fail","exit_code":1,"tail":["'test_run_night.py': (66,),","'test_s0_line_audit_guard.py': (103,)}","Ran 5 tests in 3.744s","FAILED (failures=1)"]},"expected":{"exit_code":0,"tail_regex":"Ran 5 tests.*OK"}},
    {"id":"V1","kind":"test","cmd":"PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_git_fixture_maintenance","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["Ran 5 tests in 3.869s","OK"]},"expected":{"exit_code":0,"tail_regex":"Ran 5 tests.*OK"}},
    {"id":"V2","kind":"test","cmd":"PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_issue_dg071_dg075_statistics","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["Ran 32 tests in 2.763s","OK"]},"expected":{"exit_code":0,"tail_regex":"Ran 32 tests.*OK"}},
    {"id":"V3","kind":"test","cmd":"PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_install_night_agent","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["Ran 11 tests in 6.317s","OK"]},"expected":{"exit_code":0,"tail_regex":"Ran 11 tests.*OK"}},
    {"id":"V4","kind":"test","cmd":"PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_magistrate_watchdog_cli","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["Ran 3 tests in 11.363s","OK"]},"expected":{"exit_code":0,"tail_regex":"Ran 3 tests.*OK"}},
    {"id":"V5","kind":"test","cmd":"PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_bridge","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["Ran 62 tests in 64.370s","OK"]},"expected":{"exit_code":0,"tail_regex":"Ran 62 tests.*OK"}},
    {"id":"V6","kind":"test","cmd":"PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_install_magistrate_watchdog","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["Ran 8 tests in 5.395s","OK"]},"expected":{"exit_code":0,"tail_regex":"Ran 8 tests.*OK"}},
    {"id":"V7","kind":"test","cmd":"PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_magistrate_watchdog","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["Ran 63 tests in 1.792s","OK"]},"expected":{"exit_code":0,"tail_regex":"Ran 63 tests.*OK"}},
    {"id":"V8","kind":"test","cmd":"PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_run_night","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["Ran 56 tests in 8.606s","OK"]},"expected":{"exit_code":0,"tail_regex":"Ran 56 tests.*OK"}},
    {"id":"V9","kind":"test","cmd":"PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_s0_line_audit_guard","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["Ran 5 tests in 1.786s","OK"]},"expected":{"exit_code":0,"tail_regex":"Ran 5 tests.*OK"}},
    {"id":"V10","kind":"test","cmd":"PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_docs_freshness","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["Ran 31 tests in 0.881s","OK"]},"expected":{"exit_code":0,"tail_regex":"Ran 31 tests.*OK"}},
    {"id":"V11","kind":"inspection","cmd":"PYTHONDONTWRITEBYTECODE=1 python3 scripts/gen_state.py --check","cwd":".","observed":{"result":"pass","exit_code":0,"tail":[]},"expected":{"exit_code":0,"tail_regex":"^$"}}
  ],
  "flags": [
    {"id":"F1","kind":"scope_deviation","level":"blocking","text":"R4-F2 names the governed file docs/phase_2/floor_mint_contract.md, but WRITE_SCOPE instead lists the nonexistent docs/contracts/floor_mint_contract.md.","needs":"Add docs/phase_2/floor_mint_contract.md to WRITE_SCOPE so W8 can name the frozen detection-floor registry."},
    {"id":"F2","kind":"lead_ruling","level":"blocking","text":"PHASE-SHARE-ESTIMAND-01 was retired from docs/process/state_kernel.json by 350bbd72; the stale 1.0 sentence is in TASK_QUEUE.md's hand-authored completed table, outside both generator regions.","needs":"Rule whether to correct that completed-table row directly (recommended) or introduce a supported completed-task kernel source; do not re-add the completed task as live or shelved."},
    {"id":"F3","kind":"residual_risk","level":"nonblocking","text":"No live launcher, hardware, whole-suite, or quiet-machine work ran, per the brief and machine-state fence.","needs":""}
  ],
  "scope_expansion": {"requested_paths":["docs/phase_2/floor_mint_contract.md"],"reason":"This is the only governed floor-mint contract in the tree and contains W8; the allowlisted docs/contracts path does not exist.","blocked_work":"Amend W8 to name the frozen detection-floor registry.","minimal_change":"One W8 contract-text replacement; no code or closed-set change."}
}
```

## Change

| Finding | Ruling | Cure | File:line |
|---|---|---|---|
| R4-F1 | Round-4 R4-F1 plus the implementation brief: all seven initializations use the shared helper. | Routed the seven sites through `init_git_fixture`; the estate guard moved red to green. | `tests/test_install_magistrate_watchdog.py:100,117`; `tests/test_install_night_agent.py:31`; `tests/test_magistrate_watchdog.py:1578`; `tests/test_magistrate_watchdog_cli.py:35`; `tests/test_run_night.py:67`; `tests/test_s0_line_audit_guard.py:105` |
| R4-F2 | Magistrate row `R4-F2 W8 / FLOOR_METRIC_CATALOG`: name the frozen registry. | Blocked without touching or shadowing the governed contract; minimal scope expansion is above. | `docs/phase_2/floor_mint_contract.md:14` |
| R4-F3 | Magistrate row `R4-F3 aud-wo-rows bridge gate`: remove only the standalone gate and its test. | Deleted the executable and its two dedicated tests; removed WO-020 standalone-gate acceptance text while retaining the other audit follow-ups and bridge drift coverage. | `scripts/check-bridge-docs.mjs` (deleted); `tests/test_bridge.py:1659`; `docs/process/state_kernel.json:52` |
| R4-F4 | Magistrate row `R4-F4 COLDGATE-HANDOFF-01 fence`: fence stays on after landing. | Release now requires Ed's registry ratification and a lead-owned concrete-launcher pass; regenerated queue projections carry it. | `docs/process/state_kernel.json:997`; `TASK_QUEUE.md:626,771` |
| R4-F5 | Magistrate row `R4-F5 phase-share ratios in the queue`: retain 0.803853955423178–0.958277594709544 and cite its artifact. | Blocked on the retired-row source-of-truth mismatch described in F2; generated regions were not hand-edited. | `TASK_QUEUE.md:103`; `docs/process/traces/2026-09-04-fanout/PHASE-SHARE-ESTIMAND-01/06-sol-fix-round-2-report.md:28` |
| Opus B2 | Magistrate row `Opus B2 PROJECT_STATUS "five windows"`: restore the base's uncounted phrasing. | Restored “Earlier post-repair windows established that the path can pass.” | `PROJECT_STATUS.md:106` |
| Opus B3 | Magistrate row `Opus B3 P1-008 references`: point all date ownership to `ED-DATES-01`. | Replaced every stale owner/truth-source reference. | `docs/milestones.md:15`; `docs/risk_register.md:42` |
| Opus S1/S2 | Magistrate row `Opus should-fixes`: README targets must contain the promised material. | Restored the D-067 rationale and D-070 agenda to the compact advisor page, then targeted that page without forbidden post-compaction anchors. | `PROJECT_STATUS.md:77`; `README.md:81,90` |
| Opus S6 | Magistrate row `Opus should-fixes`: the one-name-sweep fence gets a mutation kill. | Added tampered-producer-blob and mutated-issued-payload negative cases. | `tests/test_issue_dg071_dg075_statistics.py:1122,1140` |

`scripts/gen_state.py` regenerated `TASK_QUEUE.md`; `RUN_STATE.md` was also rendered but its generated bytes did not change.

## Verification notes

V0 is the required red baseline. V1 is the matching green run. The first V10 attempt exposed the DOC-008 no-anchor and 1,400-word constraints; the final V10 tail above is the green rerun after the README/PROJECT_STATUS cure was compacted.

## Residual risk

NEEDS_SCOPE: add only `docs/phase_2/floor_mint_contract.md` for R4-F2. NEEDS_RULING for R4-F5: direct correction of the hand-authored completed row is recommended because reintroducing the retired task would falsely make it live or shelved; a new completed-task kernel mechanism would be a larger state-contract change.
