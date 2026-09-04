```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "NOT LANDABLE: round 1 catches the refuter's exact same-signature ALPHA redirect, but its guard misses a correct core call followed by a write outside the validated root.",
  "workspace": {
    "base_requested": "c855dac7f540a68f8f16408d98deb6c6c3639019",
    "base_mode": "exact",
    "head_start": "c855dac7f540a68f8f16408d98deb6c6c3639019",
    "head_end": "c855dac7f540a68f8f16408d98deb6c6c3639019",
    "upstream_end": "a6e9edde082f460fbe335d2eac8021f77258b8e6",
    "branch": "feat/2026-09-04-fan-GENERATOR-CORE-01"
  },
  "pathspec": [
    "docs/process_traces/2026-09-04-fanout/GENERATOR-CORE-01/06-delta-reaudit-round-1.md"
  ],
  "unowned_dirty": [],
  "verdict": {
    "gauntlet": "NOT LANDABLE",
    "same_signature_evasion": "CAUGHT",
    "second_evasion": "MISSED",
    "findings": [
      {
        "id": "F1",
        "severity": "blocker",
        "location": "tests/test_campaign_generator_core.py:126",
        "text": "The behavioral guard inventories only files beneath output_root. ALPHA can call the real shared validator exactly once with the complete ordinary inventory, then write one file outside output_root; the guard passes because that file is absent from output_root.rglob('*').",
        "counterfactual": "Retain ALPHA's genuine validate_generation_write_boundary(output_root, outputs) call and immediately write /private/tmp/generator-core-outside-boundary-proof.txt. The guard passed and the outside file existed."
      }
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_campaign_generator_core.CampaignGeneratorCoreTests.test_exact_alpha_local_validator_evasion_is_detected",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Ran 1 test in 0.977s",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 1 test in .*s[\\s\\S]*OK"
      }
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 - <<'PY'\nfrom pathlib import Path\nfrom tests.test_campaign_generator_core import CampaignGeneratorCoreTests, GENERATOR_CASES, ROOT\nalpha = GENERATOR_CASES[0]\nlabel, generator_rel, _ = alpha\nsource = (ROOT / generator_rel).read_text(encoding='utf-8')\nneedle = '    validate_generation_write_boundary(output_root, outputs)\\n'\nproof = Path('/private/tmp/generator-core-outside-boundary-proof.txt')\nproof.unlink(missing_ok=True)\nassert label == 'ALPHA' and source.count(needle) == 1\nmutated = source.replace(needle, needle + \"    Path('/private/tmp/generator-core-outside-boundary-proof.txt').write_text('outside\\\\n', encoding='utf-8')\\n\", 1).encode('utf-8')\nCampaignGeneratorCoreTests().assert_generation_uses_shared_write_boundary((alpha,), source_overrides={generator_rel: mutated})\nassert proof.read_text(encoding='utf-8') == 'outside\\n'\nproof.unlink()\nprint('OUTSIDE_BOUNDARY_EVASION_UNDETECTED guard=pass proof=/private/tmp/generator-core-outside-boundary-proof.txt')\nPY",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "OUTSIDE_BOUNDARY_EVASION_UNDETECTED guard=pass proof=/private/tmp/generator-core-outside-boundary-proof.txt"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "OUTSIDE_BOUNDARY_EVASION_UNDETECTED guard=pass proof=/private/tmp/generator-core-outside-boundary-proof.txt"
      }
    },
    {
      "id": "V3",
      "kind": "suite",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_campaign_generator_core tests.test_d117_contrast_v5_pack tests.test_microdelta_generate_configs",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Ran 51 tests in 17.504s",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 51 tests in .*s[\\s\\S]*OK"
      }
    },
    {
      "id": "V4",
      "kind": "test",
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
    }
  ],
  "flags": []
}
```

## Findings

### F1 — blocker — outside-root writes are invisible to the guard

The refuter's exact evasion is now caught. The mutation at
`tests/test_campaign_generator_core.py:150-188` adds a same-signature local
validator (`output_root: Path, outputs: Iterable[Path] -> None`), leaves the
shared import untouched, redirects ALPHA's production call, and makes the
inner behavioral guard fail. The unittest passes only because it requires that
failure.

The replacement proof remains incomplete. Its emitted-file census at
`tests/test_campaign_generator_core.py:126-133` is rooted at `output_root`, so
it cannot observe a write beyond that root. In a separate source-override
probe, ALPHA retained the genuine shared-core call exactly once and then wrote
`/private/tmp/generator-core-outside-boundary-proof.txt`. The guard passed and
the file existed. This recreates the boundary-escape consequence of the
original F1 by a new route. Bind all producer writes to the validated
root/inventory, and add this counterfactual, before landing.

## Residual risk

The permitted checks cover the three named focused modules and byte parity;
no broader suite was run. The observer proves call occurrence and an in-root
post-generation inventory, but does not prove validation precedes every write.
