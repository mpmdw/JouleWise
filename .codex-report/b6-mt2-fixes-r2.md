```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "clean",
  "completion": "complete",
  "summary": "Implemented R1-R4; 704 focused/legacy test methods and the real-archive replay pass.",
  "workspace": {
    "base_requested": "0276a3327cbe11627d905ed3f728423b6280f129",
    "base_mode": "exact",
    "head_start": "0276a3327cbe11627d905ed3f728423b6280f129",
    "head_end": "0276a3327cbe11627d905ed3f728423b6280f129",
    "upstream_end": "0276a3327cbe11627d905ed3f728423b6280f129",
    "branch": "fix/2026-10-17-b6-mt2-fixes"
  },
  "pathspec": [
    ".codex-report/b6-mt2-fixes-r2.md",
    "joulewise/b6/acceptance.py",
    "joulewise/b6/smoke.py",
    "scripts/run_campaign.py",
    "tests/b6/test_acceptance.py",
    "tests/b6/test_smoke.py",
    "tests/test_b6_busy_fraction_desk.py",
    "tests/test_run_campaign.py"
  ],
  "unowned_dirty": [],
  "verdict": {
    "implementation": "implemented",
    "acceptance": "ready"
  },
  "verification": [
    {
      "id": "V1",
      "kind": "test",
      "cmd": "TMPDIR=/Users/edr/night-archive/b6-mt2-fix/tmp/r2.W18u PYTHONPATH=/Users/edr/code/JouleWise-wt-b6-mt2fix JW_B5_SYNTHETIC_ONLY=1 /opt/homebrew/bin/python3.13 -B -m unittest tests.test_b6_busy_fraction_desk tests.test_environment_admission tests.test_whole_window tests.test_hazard_whole_window_verdict tests.test_harvest_b5_p3harv tests.hazards.test_refusal_allowlist tests.b6.test_acceptance tests.b6.test_smoke tests.test_run_campaign.IdleAdmissionCoreVerdictTests > /Users/edr/night-archive/b6-mt2-fix/tmp/r2.W18u/required-tests.log 2>&1",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Ran 271 tests in 213.881s",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "OK"
      }
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "TMPDIR=/Users/edr/night-archive/b6-mt2-fix/tmp/r2.W18u PYTHONPATH=/Users/edr/code/JouleWise-wt-b6-mt2fix JW_B5_SYNTHETIC_ONLY=1 /opt/homebrew/bin/python3.13 -B -m unittest tests.test_controller tests.test_controller_retry_backoff tests.test_controller_hazard_flags tests.test_run_campaign_max_blocks tests.test_floor_extraction tests.test_reduce > /Users/edr/night-archive/b6-mt2-fix/tmp/r2.W18u/additional-tests.log 2>&1",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Ran 433 tests in 531.255s",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "OK"
      }
    },
    {
      "id": "V3",
      "kind": "test",
      "cmd": "TMPDIR=/Users/edr/night-archive/b6-mt2-fix/tmp/r2.W18u PYTHONPATH=/Users/edr/code/JouleWise-wt-b6-mt2fix JW_B5_SYNTHETIC_ONLY=1 /opt/homebrew/bin/python3.13 -B -m unittest tests.test_run_campaign.IdleAdmissionCoreVerdictTests > /Users/edr/night-archive/b6-mt2-fix/tmp/r2.W18u/final-writer-class.log 2>&1",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Ran 78 tests in 109.496s",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "OK"
      }
    },
    {
      "id": "V4",
      "kind": "smoke",
      "cmd": "TMPDIR=/Users/edr/night-archive/b6-mt2-fix/tmp/r2.W18u PYTHONPATH=/Users/edr/code/JouleWise-wt-b6-mt2fix JW_B5_SYNTHETIC_ONLY=1 /opt/homebrew/bin/python3.13 -B - <<'PY'\nfrom pathlib import Path\nfrom dataclasses import replace, asdict\nimport json\nfrom joulewise.b6.acceptance import ACCEPTANCE, evidence_from_archive\nfrom joulewise.b6.archive import plan_tree, executed_porcelain\nfrom joulewise.b6.smoke import classify, stages_succeeded\nfrom joulewise.environment_admission import environment_admission_refusals\nfrom joulewise.whole_window import validate_whole_window_verdict_row\np = Path('/Users/edr/code/JouleWise-wt-b6-mt2fix')\ns = Path('/Users/edr/night-b6/machine-test/MT-20261017T1735Z/smoke/d117_floor_qwen3-1p7b_v5-20261017T1735Z')\na = s / 'archive'\npp = s / 'custody/night_plan.json'\nplan = json.loads(pp.read_text())\nreg = s.parents[1] / 'registration'\nfor rid in ('d117fq31p7-df-ph-prefill-p2048-abs-r01', 'neg8-window-end-r1'):\n    admission = json.loads((a / 'sources/claim-runs' / rid / 'metadata.json').read_text())['environment_admission']\n    reasons = environment_admission_refusals(admission)\n    print('ENVIRONMENT', rid, reasons, flush=True)\n    assert reasons == ()\ne = evidence_from_archive(a, plan, reg)\ne = replace(e, runtime={**e.runtime, '_b6': {**e.runtime['_b6'], 'smoke': True}})\nt, pr = plan_tree(a, plan, e.pack_id)\ncode = json.loads((a / 'derived/code-identity.json').read_text())\ncode.update(repo_root=str(p), status_porcelain=executed_porcelain(a, plan, pp))\nf = ACCEPTANCE.prepare(ledger_path=s / 'measurement/runs/calibration_observation_ledger.jsonl', plan_tree=t,\n                       registration_dir=reg, code_identity=code, pack_root=pr)\nr = ACCEPTANCE.evaluate(f, e)\nprint('ACCEPTANCE', json.dumps({'structural': r.structural, 'reasons': r.reasons,\n                               'structural_failures': r.record['structural_failures']}), flush=True)\nassert not r.structural\nz = json.loads((s / 'smoke-result.json').read_text())\nok = stages_succeeded(z['stages'], tree=t, repo_root=a / 'sources/repo', evidence=e)\nstatus = classify(stages_ok=ok, driver_exit=z['driver_exit'], harvest_exit=z['harvest_exit'],\n                  acceptance_result=r, flags=z['flags'])\nprint('STAGES_OK', ok, flush=True)\nprint('CLASSIFY', status, flush=True)\nassert ok and status == 'physics'\nrow = json.loads((a / 'sources/claim-runs/whole-window-verdict.json').read_text())\nv = validate_whole_window_verdict_row(row, a / 'sources/claim-runs', set(row['bundle_ids']))\nprint('ARCHIVED_VERDICT_VALIDATOR', json.dumps(asdict(v), sort_keys=True), flush=True)\nprint('ARCHIVE_REPLAY_OK', flush=True)\nPY",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "CLASSIFY physics",
          "ARCHIVED_VERDICT_VALIDATOR {\"admitted\": false, \"authentic\": false, \"reasons\": [\"calibration_ledger_snapshot_required\", \"whole_window_neg8_verdict_failed\", \"whole_window_verdict_conflict\", \"whole_window_verdict_provenance_invalid\"], \"status\": \"failed\"}",
          "ARCHIVE_REPLAY_OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "ARCHIVE_REPLAY_OK"
      }
    },
    {
      "id": "V5",
      "kind": "inspection",
      "cmd": "git diff --check",
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
    }
  ],
  "flags": []
}
```

## Change

Implemented R1–R4. The campaign core carries the final admission attempt for marked block-6 members, and its claim barrier uses the existing busy-only predicate against both the recorded and recomputed CPU results. The standalone whole-window producer now uses that same barrier instead of repeating the raw-CPU veto. Raw CPU evidence is preserved, and ordinary block-5 core rows retain their existing shape.

Acceptance restores the base absence predicate exactly: bundle absent OR member.bytes_missing. Only a complete stage of recorded idle skips receives the exemption. The renamed recorded_idle_skip helper recognizes the exact cap and budget flag/reason pairs, and the smoke desk uses it for exact dispatched members. Count minima, unexplained missing records, crashes and unrelated failures retain their outcomes.

Regressions cover both actual producer paths (standalone and AXI), a clean core with one busy-only member, the unmarked control, inconsistent CPU results, summary loss after clean capture, budget skips, mixed cap/budget skips, missing or mismatched explanations, and the corrected extra-marker expectation.

### Decisions I made

- Applied threshold-design council Q3 as written: final admitted=True and busy_fraction_admitted=True must accompany busy-only recorded and recomputed CPU results. Power, GPU, environment, enforcement and missing-evidence checks remain in force.
- Treated the standalone writer's duplicate raw-CPU veto as the same R1 defect. Sharing the barrier keeps both producers consistent without changing which data count.
- Followed R2 and the authorities by restoring the base predicate and adding only the recorded-skip exemption. Opus F2's suggestion of a new structural/flag code was not adopted; the existing structural code already covers unexplained whole-stage summary loss.
- Applied collection-design §13.1 and its per-session wait-budget rule: both (idle.wait_cap_skip, wait_cap_reached) and (idle.wait_budget_skip, wait_budget_exhausted) explain a physical pre-measurement loss. A flag or reason alone, a crossed pair, an absent bundle or incomplete stage does not suffice.
- Kept cell.below_minimum and all thresholds, tolerances and estimators unchanged.
- Left R5's reviewer metadata and Opus F3's unreachable shape untouched.
- Used this bounded brief as the M0 work-selection override; no stop card is active. Preserved lead-owned state, queue and other reports outside WRITE_SCOPE.

## Verification notes

The final writer-class rerun includes the strengthened test through both actual producers. AXI receives the member-derived core at its evaluation boundary and launches synthetic fixture children; its status selection, row writing and exit decision execute normally. These are desk tests, not live hardware validation.

The whole-tests-tree refusal-code search found no additional stale assertion for a marked busy-only admission. Extra coverage exercises legacy busy abort/retry, HAZARD controller, campaign barrier, floor replay and reducer paths. Other grep matches were refusal vocabularies, post-run display failures or explicit unrelated member failures.

V4 repeats round 1's deciding-function replay on the real MT-20261017T1735Z archive. It uses the archived executed-code identity with the corrected worktree functions; no archived bytes or judgments were rewritten. Full output:

```text
ENVIRONMENT d117fq31p7-df-ph-prefill-p2048-abs-r01 ()
ENVIRONMENT neg8-window-end-r1 ()
ACCEPTANCE {"structural": false, "reasons": [], "structural_failures": []}
STAGES_OK True
CLASSIFY physics
ARCHIVED_VERDICT_VALIDATOR {"admitted": false, "authentic": false, "reasons": ["calibration_ledger_snapshot_required", "whole_window_neg8_verdict_failed", "whole_window_verdict_conflict", "whole_window_verdict_provenance_invalid"], "status": "failed"}
ARCHIVE_REPLAY_OK
```

The historical verdict remains failed for the displayed provenance/NEG-8 reasons. Neither environment_admission_failed nor cpu_admission_core_failed appears in its validator reasons. This replay does not issue a new claim-window verdict or certify a new collection pin.

TMPDIR was created with mktemp -d /Users/edr/night-archive/b6-mt2-fix/tmp/r2.XXXX and resolved to /Users/edr/night-archive/b6-mt2-fix/tmp/r2.W18u. Commands and logs are recorded in the envelope; test tails show the unittest summaries from those redirected logs. The full repository suite and remaining block-6 modules were not rerun under this round's targeted test list; CI and the lead own broader and live gates. No collection, commit, staging, push or merge ran.

### SUMMARY

R1–R4 implemented within scope. All 704 required/additional test methods pass; the final 78-method writer class also passes. Both producers agree on busy-only admission, and the real archive replay classifies physics.

Exact files changed:

- `.codex-report/b6-mt2-fixes-r2.md`
- `joulewise/b6/acceptance.py`
- `joulewise/b6/smoke.py`
- `scripts/run_campaign.py`
- `tests/b6/test_acceptance.py`
- `tests/b6/test_smoke.py`
- `tests/test_b6_busy_fraction_desk.py`
- `tests/test_run_campaign.py`

