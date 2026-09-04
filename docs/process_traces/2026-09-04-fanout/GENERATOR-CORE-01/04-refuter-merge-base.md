```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "NOT LANDABLE: the mission delta exceeds the retarget scope and the shared-core counterfactual can be spoofed by a differently named local validator.",
  "workspace": {
    "base_requested": "merge-base(origin/main,HEAD)=7da20e28e795ac9aac41f774e4f5f7fa0ef29f5c",
    "base_mode": "exact",
    "head_start": "ddfdbc91d4a9d98cd2af9ef9a6a88cd8dddf0770",
    "head_end": "ddfdbc91d4a9d98cd2af9ef9a6a88cd8dddf0770",
    "upstream_end": "7da20e28e795ac9aac41f774e4f5f7fa0ef29f5c",
    "branch": "feat/2026-09-04-fan-GENERATOR-CORE-01"
  },
  "pathspec": [
    "docs/process_traces/2026-09-04-fanout/GENERATOR-CORE-01/04-refuter-merge-base.md"
  ],
  "unowned_dirty": [],
  "verdict": {
    "gauntlet": "NOT LANDABLE",
    "findings": [
      {
        "id": "F1",
        "severity": "blocker",
        "location": "tests/test_campaign_generator_core.py:75",
        "text": "The claimed local-core counterfactual checks only exact imported object names and exact top-level function-definition names. ALPHA can retain those checked imports, redirect its production call to a differently named local validator, and keep this test green; a temporary mutation using a local no-op validator then followed a configs symlink and wrote outside the output root.",
        "counterfactual": "In a temporary HEAD archive, add _local_validate_generation_write_boundary, redirect ALPHA's line-2475 call to it, and leave the imported validate_generation_write_boundary untouched: the named counterfactual test passes while generation escapes through an output-root symlink."
      },
      {
        "id": "F2",
        "severity": "blocker",
        "location": "docs/process_traces/2026-09-04-fanout/GENERATOR-CORE-01/{01-sol-report.md,02-supersession-scout.md,03-sol-retarget-report.md}",
        "text": "The merge-base delta has ten paths, but the retarget launch scope of record contains only the three generators, shared core, core test, parity checker, and generator-core spec. These three process-trace files are therefore outside the declared landing WRITE_SCOPE. RUN_STATE.md, TASK_QUEUE.md, docs/process/state_kernel.json, and docs/decision_log.md correctly have no delta.",
        "counterfactual": "Removing the three trace records from the mission delta, or explicitly adding them to the landing scope of record, makes the ten-path versus seven-path set difference empty; the four magistrate-owned state paths are already clean."
      }
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "inspection",
      "cmd": "BASE=$(git merge-base origin/main HEAD); git diff --name-status \"$BASE\"..HEAD; git diff --quiet \"$BASE\"..HEAD -- RUN_STATE.md TASK_QUEUE.md docs/process/state_kernel.json docs/decision_log.md; printf 'STATE_DOC_DELTA_EXIT=%s\\n' \"$?\"",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "A\ttests/test_campaign_generator_core.py",
          "STATE_DOC_DELTA_EXIT=0"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "STATE_DOC_DELTA_EXIT=0"
      }
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "set -o pipefail; PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_campaign_generator_core tests.test_d117_contrast_v5_pack tests.test_d117_floor_qwen3_v5_generate tests.test_issue_g2a_prefill_prompt_pin 2>&1 | tee /tmp/generator-core-01-focused-tests.log | tail -n 8",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Ran 69 tests in 24.533s",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 69 tests in .*s[\\s\\S]*OK"
      }
    },
    {
      "id": "V3",
      "kind": "inspection",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 scripts/check_campaign_generator_core_parity.py --baseline-ref origin/main",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "PARITY_DIFF_EMPTY generator=ALPHA files=120",
          "PARITY_DIFF_EMPTY generator=BETA files=120",
          "PARITY_DIFF_EMPTY generator=GAMMA files=112",
          "PARITY_OK generators=3 files=352 excluded=['generate_configs.py', 'plan_tree.json', 'plan_tree.sha256'] baseline=origin/main"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "PARITY_OK generators=3 files=352 .* baseline=origin/main"
      }
    },
    {
      "id": "V4",
      "kind": "inspection",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 - <<'PY'\nimport subprocess,tempfile\nfrom pathlib import Path\nfrom scripts.check_campaign_generator_core_parity import GENERATOR_CASES,configure_generator,generate,load_source\nfrom tests.test_d117_floor_qwen3_v5_generate import fixture_prefill_pin\nwith tempfile.TemporaryDirectory(prefix='generator-core-direct-diff-') as td:\n t=Path(td);f=t/'fixture';f.mkdir();pin=fixture_prefill_pin(f)\n for ref,side in (('origin/main','base'),('HEAD','head')):\n  for label,rel,_ in GENERATOR_CASES:\n   src=subprocess.check_output(['git','show',f'{ref}:{rel.as_posix()}']);m=load_source(f'direct_{side}_{label}',src,Path.cwd()/rel);m.embedded_generator_bytes=lambda src=src:src;configure_generator(label,m,pin);generate(m,label,t/side/label)\n full=subprocess.run(['diff','-qr',str(t/'base'),str(t/'head')],text=True,capture_output=True);lines=full.stdout.splitlines();assert full.returncode==1 and len(lines)==9;assert all(any(n in x for n in ('generate_configs.py','plan_tree.json','plan_tree.sha256')) for x in lines)\n clean=subprocess.run(['diff','-qr','--exclude=generate_configs.py','--exclude=plan_tree.json','--exclude=plan_tree.sha256',str(t/'base'),str(t/'head')],text=True,capture_output=True);assert clean.returncode==0,(clean.stdout,clean.stderr);print('DIRECT_TWO_ROOT_DIFF_OK self_bound=9 non_self_bound=0')\nPY",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "DIRECT_TWO_ROOT_DIFF_OK self_bound=9 non_self_bound=0"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "DIRECT_TWO_ROOT_DIFF_OK self_bound=9 non_self_bound=0"
      }
    },
    {
      "id": "V5",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 - <<'PY'\nimport os,shutil,subprocess,sys,tempfile\nfrom pathlib import Path\nwith tempfile.TemporaryDirectory() as td:\n d=Path(td)/'r';shutil.copytree(Path.cwd(),d,ignore=shutil.ignore_patterns('.git','__pycache__'));p=d/'configs/campaigns/d117_floor_qwen3-1p7b_v5/generate_configs.py';s=p.read_text();n='render_json = make_render_json(thread_generation_identity)\\n';p.write_text(s.replace(n,n+'\\n\\n_local_validate_generation_write_boundary = lambda output_root, outputs: None\\n',1).replace('    validate_generation_write_boundary(output_root, outputs)','    _local_validate_generation_write_boundary(output_root, outputs)',1));e=os.environ.copy();e.update(PYTHONPATH=str(d),PYTHONDONTWRITEBYTECODE='1');t='tests.test_campaign_generator_core.CampaignGeneratorCoreTests.test_counterfactual_local_write_boundary_cannot_bypass_shared_core';r=subprocess.run([sys.executable,'-m','unittest',t],cwd=d,env=e,capture_output=True,text=True);assert r.returncode==0,r.stderr\nprint('ALIAS_BYPASS_UNDETECTED test=pass')\nPY",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "ALIAS_BYPASS_UNDETECTED test=pass"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "ALIAS_BYPASS_UNDETECTED test=pass"
      }
    }
  ],
  "flags": [
    {
      "id": "G1",
      "kind": "scope_deviation",
      "level": "blocking",
      "text": "The reviewed landing, not this review session, contains three paths outside its seven-path retarget scope of record.",
      "needs": "Remove/re-home those paths from the mission delta or issue an explicit landing-scope ruling before merge."
    }
  ]
}
```

## Findings

### F1 — blocker — spoofable shared-core counterfactual

The production branch currently calls the shared validator, but the regression
at `tests/test_campaign_generator_core.py:75-101` does not prove that production
calls stay attached to it. It checks that the expected imported names still
resolve to the core objects and rejects top-level functions only when their
names are exactly one of the six listed helper names.

Executed against a temporary archive of HEAD: ALPHA retained the imported
`validate_generation_write_boundary`, gained a differently named local no-op
validator, and redirected the call at
`configs/campaigns/d117_floor_qwen3-1p7b_v5/generate_configs.py:2475` to that
local name. The named counterfactual test still passed. With `output/configs`
symlinked outside the output root, the mutated generator wrote a
`calibration_plan.json` outside. Normal generation into empty roots remains
byte-identical under this mutation, so the parity check does not close the
bypass.

The narrower claimed counterfactual is real: temporary exact-name local
definitions for `actual_pack_paths`, `make_render_json`, `render_json`,
`sha256_bytes`, `sidecar_bytes`, and `validate_generation_write_boundary` each
made the named test red. The blocker is that equivalent local production logic
under a different name is not rejected. The fix needs to bind the relevant
production call sites to the shared objects, not merely prove that unused
imports exist and exact old names are absent.

### F2 — blocker — mission delta exceeds the retarget scope of record

`git diff $(git merge-base origin/main HEAD)..HEAD` contains ten paths. The
seven implementation/spec paths are within the scope supplied for this round;
`01-sol-report.md`, `02-supersession-scout.md`, and
`03-sol-retarget-report.md` are not. This is a landing-scope defect even though
the files are process evidence. The four named magistrate-owned state files
have no delta.

Executed evidence beyond V1-V5: one-line temporary mutations made the new
census test red for an unclassified thirteenth D-117 generator, the custody
test red for a historical generator importing the core, the symlink test red
when the shared core accepted a linked ancestor, and the absent-tree test red
when the shared core refused a missing pack ancestor. No repository-wide suite
was run.

## Residual risk

No previous refuter verdict was present in this mission directory, so there was
no inherited non-staleness blocker to carry forward. The prior base-staleness
issue was not re-reported. The refreshed range was reviewed only from its exact
`origin/main` merge base, and direct two-root regeneration confirmed that the
only nine byte differences are the three expected self-bound files per live
generator; all 352 non-self-bound files are byte-identical.
