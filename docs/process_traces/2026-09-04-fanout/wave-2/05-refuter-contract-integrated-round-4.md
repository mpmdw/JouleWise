```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "NOT LANDABLE: tests, contracts, and cold-gate fencing fail.",
  "workspace": {
    "base_requested": "origin/int/2026-09-04-fan-wave-1",
    "base_mode": "exact",
    "head_start": "8222b114f1b20b600d6b1680a9f8773feca7069f",
    "head_end": "8222b114f1b20b600d6b1680a9f8773feca7069f",
    "upstream_end": "eb3e3d85dc9c3ee1b6e4e470fb67fac33a76d25c",
    "branch": "int/2026-09-04-fan-wave-2"
  },
  "pathspec": [
    "docs/process_traces/2026-09-04-fanout/wave-2/05-refuter-contract-integrated-round-4.md"
  ],
  "unowned_dirty": [
    "docs/process_traces/2026-09-04-fanout/wave-2/06-opus-counter-review.md"
  ],
  "verdict": {
    "gauntlet": "NOT LANDABLE",
    "round1": {"F1":"CURED","F2":"CURED","F3":"CURED","F4":"CURED","F5":"CURED","F6":"CURED"},
    "round2": {"R2-F1":"CURED","R2-F2":"CURED","R2-F3":"CURED","R2-F4":"CURED"},
    "round3": {"R3-F1":"CURED","R3-F2":"NOT_CURED_AND_EXPANDED_AS_R4-F1","R3-F3":"CURED","R3-F4":"CURED"},
    "landings": {"requested":19,"ancestor_count":19,"name_deviations":[]},
    "findings": [
      {
        "id": "R4-F1",
        "severity": "blocker",
        "location": "tests/test_git_fixture_maintenance.py:172 (failure map: seven calls in six modules)",
        "text": "R3-F2 remains and expanded: the estate guard finds seven direct git initializations in six modules."
      },
      {
        "id": "R4-F2",
        "severity": "blocker",
        "location": "docs/phase_2/floor_mint_contract.md:14; joulewise/detection_floor_registry.py:18-27",
        "text": "MODULARITY replaced FLOOR_METRIC_CATALOG with a frozen registry, but ratified W8 still requires the deleted symbol."
      },
      {
        "id": "R4-F3",
        "severity": "blocker",
        "location": "docs/process/state_kernel.json:58; docs/orchestration.md:335; docs/decision_log.md",
        "text": "aud-wo-rows adds a standalone bridge gate without its acceptance-required D-060 six-part decision; the breadth therefore waits for gates."
      },
      {
        "id": "R4-F4",
        "severity": "blocker",
        "location": "docs/process/state_kernel.json:1004; 01-magistrate-rulings.md:44",
        "text": "COLDGATE-HANDOFF is landed, but live state ends its operational fence on landing. The adopted re-scope keeps it until Ed ratifies the registry amendment and a lead-owned concrete-launcher check passes."
      },
      {
        "id": "R4-F5",
        "severity": "should_fix",
        "location": "TASK_QUEUE.md:103; docs/process_traces/2026-09-04-fanout/PHASE-SHARE-ESTIMAND-01/06-sol-fix-round-2-report.md:28",
        "text": "The queue says all ten phase-share ratios are 1.0, but corrected retained replay records 0.803853955423178-0.958277594709544; r01/r10 replay gives 0.914089967341564 and 0.803853955423178."
      }
    ]
  },
  "verification": [
    {
      "id":"V1","kind":"test","cmd":"git diff --name-only origin/int/2026-09-04-fan-wave-1..HEAD -- 'tests/test_*.py' | sed 's#/#.#g;s#\\.py$##' | xargs env PYTHONDONTWRITEBYTECODE=1 python3 -m unittest docs.paper.fill-rehearsal.test_select_outcome_branches","cwd":".",
      "observed":{"result":"fail","exit_code":1,"tail":["FAIL: test_every_test_module_routes_git_initialization_through_shared_helper","Ran 2115 tests in 4823.421s","FAILED (failures=1, skipped=45)"]},
      "expected":{"exit_code":0,"tail_regex":"Ran 2115 tests.*OK"}
    },
    {
      "id":"V2","kind":"inspection","cmd":"set -e; test -f docs/process_traces/2026-09-04-fanout/wave-1/04-delta-reaudit-round-1.md; test -f docs/process_traces/2026-09-04-fanout/wave-2/01-refuter-contract-integrated.md; test \"$(shasum -a 256 joulewise/reduce.py | cut -d' ' -f1)\" = 7b9c0d28869040229e113ea2d40ecc69966075fd34052fbb51cfaffbd9ff9fcc; test \"$(rg -c '^\\| D-172 \\|' docs/decision_log.md)\" = 1; test \"$(rg -c '^## D-172:' docs/decision_log.md)\" = 1; rg -q 'doc008 sign-off RECORDED' docs/process_traces/2026-09-04-fanout/01-magistrate-rulings.md; rg -q '# R-12: the governed family is the Qwen3 _v5 campaign packs' scripts/prewindow_check.sh; echo prior-recheck=pass","cwd":".",
      "observed":{"result":"pass","exit_code":0,"tail":["prior-recheck=pass"]},
      "expected":{"exit_code":0,"tail_regex":"prior-recheck=pass"}
    },
    {
      "id":"V3","kind":"inspection","cmd":"set -e; rg -n 'W8 — public FLOOR_METRIC_CATALOG' docs/phase_2/floor_mint_contract.md; ! rg -n '^FLOOR_METRIC_CATALOG\\s*=' joulewise/detection_floor.py; python3 -c 'from joulewise import detection_floor as f; from joulewise.detection_floor_registry import default_detection_floor_closed_sets as d; r=d(); assert not hasattr(f,\"FLOOR_METRIC_CATALOG\"); print(f\"contract_symbol=absent registry_sha256={r.sha256} metrics={len(r.floor_metrics)}\")'","cwd":".",
      "observed":{"result":"pass","exit_code":0,"tail":["contract_symbol=absent registry_sha256=fc91df6d14b02d17dba31d1018c31287b65bde2d94f2b608825411f98b2aed1d metrics=9"]},
      "expected":{"exit_code":0,"tail_regex":"fc91df6d.*metrics=9"}
    },
    {
      "id":"V4","kind":"inspection","cmd":"set -e; test -f scripts/check-bridge-docs.mjs; rg -q 'NAMED-FAILURE BAR FOR PROCESS INNOVATION' docs/orchestration.md; rg -q 'WO-020 has a recorded standalone bridge-checker decision' docs/process/state_kernel.json; ! rg -q 'check-bridge-docs|standalone bridge.checker|WO-020' docs/decision_log.md; node scripts/check-bridge-docs.mjs; echo standalone-checker=present d060-record=absent checker-selftest=pass","cwd":".",
      "observed":{"result":"pass","exit_code":0,"tail":["bridge docs check OK (5 consumers, 5 snippets)","standalone-checker=present d060-record=absent checker-selftest=pass"]},
      "expected":{"exit_code":0,"tail_regex":"d060-record=absent"}
    },
    {
      "id":"V5","kind":"inspection","cmd":"set -e; git merge-base --is-ancestor 9c158976 HEAD; rg -q 'Until this row lands, no validator PASS' docs/process/state_kernel.json; rg -q 'Keep the operational fence only until Ed ratifies the registry amendment and the concrete launcher passes lead-owned live verification' docs/process_traces/2026-09-04-fanout/01-magistrate-rulings.md; ! rg -q 'Ed ratifies the registry amendment.*concrete launcher.*live verification' docs/process/state_kernel.json TASK_QUEUE.md; echo handoff=landed live-state-fence=pre-landing-only post-landing-ruling=unprojected","cwd":".",
      "observed":{"result":"pass","exit_code":0,"tail":["handoff=landed live-state-fence=pre-landing-only post-landing-ruling=unprojected"]},
      "expected":{"exit_code":0,"tail_regex":"post-landing-ruling=unprojected"}
    },
    {
      "id":"V6","kind":"inspection","cmd":"set -e; for b in /Users/edr/code/JouleWise/runs_window_a10_20260725/p2015-df-ph-decode-abs-r01 /Users/edr/code/JouleWise/runs_window_a10_20260725/p2015-df-ph-decode-abs-r10; do PYTHONDONTWRITEBYTECODE=1 python3 scripts/analyze_phase_share.py \"$b\" | python3 -c 'import json,sys; p=json.load(sys.stdin); print(p[\"bundle_id\"],p[\"comparison\"][\"joint_to_box_prefill_share_width_ratio\"])'; done","cwd":".",
      "observed":{"result":"pass","exit_code":0,"tail":["p2015-df-ph-decode-abs-r01 0.914089967341564","p2015-df-ph-decode-abs-r10 0.803853955423178"]},
      "expected":{"exit_code":0,"tail_regex":"r10 0\\.803853955423178"}
    }
  ],
  "flags": [
    {"id":"G1","kind":"verification_gap","level":"nonblocking","text":"Only the 50 changed tests/test_*.py modules and changed paper branch-selector module ran, per preflight.","needs":"Magistrate runs the whole suite after the blockers are cured."},
    {"id":"G2","kind":"residual_risk","level":"nonblocking","text":"No live launcher, hardware, or quiet-machine measurement ran; COLDGATE remains operationally fenced.","needs":"Ed ratification and lead-owned real-entry verification."},
    {"id":"G3","kind":"baseline_drift","level":"nonblocking","text":"origin/main advanced during review from c74c7e6a to eb3e3d85; the requested target stayed exactly 8222b114 and was not rebased.","needs":"Merge/review later main movement separately if it is added to the candidate."}
  ]
}
```

## Findings

R4-F1 — blocker. The Git-fixture estate guard is red on seven calls in six modules. This is R3-F2 left open at `test_s0_line_audit_guard.py:103`, plus watchdog/night-plan regrowth. The full touched-module command ran 2,115 tests and found no other failure.

R4-F2 — blocker. Ratified W8 still names the deleted `FLOOR_METRIC_CATALOG`; production now authenticates `detection_floor_closed_sets_v1` at `fc91df6d…`. Reconcile the contract to the replacement registry without changing its nine governed pairs.

R4-F3 — blocker. The standalone bridge checker is technically discriminating and green, but it is a new process layer with neither its acceptance-required decision nor D-060's six-part record/cold-gate disposition.

R4-F4 — blocker. The handoff implementation matches the adopted evidence mechanics, but the live operational fence does not: it currently expires on landing instead of after Ed ratification plus concrete-launcher verification.

R4-F5 — should fix. Preserve the ruled measured-null label, but update the queue's false `1.0` evidence sentence to the corrected diagnostic ratios and limitation.

All 19 named landing tips are ancestors; no name deviation was found. Prior F1-F6, R2-F1-F4, and R3-F1/F3/F4 are cured; R3-F2 is R4-F1.

Claim-bearing inventory: all four D-138 inputs remain byte-unchanged (`reduce.py` stays `7b9c0d…`); the prewindow baseline pair and all active D-166 generated JSON/SHA files are unchanged; the three D117 generator refactors reproduce 352 non-self-bound files. MODULARITY adds the nine-pair frozen registry (`fc91df6d…`) and moves historical P2-015 literals into `campaign_spec.json` without changing an issued floor/calibration artifact. R7 repins only the reviewed producer to `12d0293b…`; issued values/status stay unchanged. Results-fill amendments keep DS-32/PG-08 and new OB-01/TR-01/OR-01 stopped and value-unissued. The research-question addition is explicitly a planning join; canonical status and claim ceilings do not change. DOC-008 compacts advisor status with the recorded sign-off and still says no claim-bearing `_v5` data exist.

## Residual risk

No whole-suite, live launcher, hardware, or `[QUIET-MAC]` evidence was attempted. `origin/main` advanced after the exact target was fixed. The concurrent untracked `06-opus-counter-review.md` was preserved and not modified.
