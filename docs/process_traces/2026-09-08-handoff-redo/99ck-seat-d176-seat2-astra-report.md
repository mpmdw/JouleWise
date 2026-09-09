```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "blocked",
  "completion": "partial",
  "summary": "Implemented and verified v3 plan validation, serialization and installation; GO orchestration and frozen production roots require lead rulings.",
  "workspace": {
    "base_requested": "main + seat-1 contract",
    "base_mode": "descendant",
    "head_start": "0a7c5858360f5d34f14e49984ea317755e059665",
    "head_end": "0a7c5858360f5d34f14e49984ea317755e059665",
    "upstream_end": "ac092ccd507c2e369ac4642dfce31352769ee698",
    "branch": "feat/2026-09-08-d176-seat2-producer"
  },
  "pathspec": [
    "docs/contracts/pack_night_go_receipt.md",
    "joulewise/night_gate.py",
    "joulewise/night_plan_writer.py",
    "scripts/install_night_agent.sh",
    "tests/test_install_night_agent.py",
    "tests/test_night_plan_writer.py"
  ],
  "unowned_dirty": [],
  "verdict": {
    "implementation": "partial",
    "acceptance": "needs_ruling"
  },
  "verification": [
    {
      "id": "V1",
      "kind": "suite",
      "cmd": "python3 -B -m unittest tests.test_night_gate tests.test_install_night_agent tests.test_run_night tests.test_t0_rehearsal tests.test_night_plan_writer tests.test_docs_freshness > /tmp/d176-seat2-acceptance.log 2>&1\nrc=$?\ntail -n 5 /tmp/d176-seat2-acceptance.log\nexit \"$rc\"",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 179 tests in 11.980s", "", "OK"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 179 tests in .*\\n\\nOK"
      }
    },
    {
      "id": "V2",
      "kind": "lint",
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
    },
    {
      "id": "V3",
      "kind": "test",
      "cmd": "python3 -B - <<'PY' > /tmp/d176-seat2-mutation.log 2>&1\nimport contextlib\nimport io\nimport unittest\nfrom pathlib import Path\nfrom joulewise import night_gate\n\nsource = Path(night_gate.__file__).read_text()\nold = 'if type(ordinal) is not int or ordinal < 1:'\nnew = 'if not isinstance(ordinal, int) or ordinal < 1:'\nassert source.count(old) == 1\nexec(compile(source.replace(old, new), night_gate.__file__, 'exec'), night_gate.__dict__)\nsuite = unittest.defaultTestLoader.loadTestsFromName(\n    'tests.test_night_plan_writer.NightPlanWriterTests.test_pack_nested_keys_types_and_digests_fail_closed')\nstream = io.StringIO()\nresult = unittest.TextTestRunner(stream=stream).run(suite)\nassert len(result.failures) == 1 and not result.errors, stream.getvalue()\nassert \"key='attempt_ordinal', value=True\" in stream.getvalue(), stream.getvalue()\nprint('PASS: boolean-ordinal validator mutation killed by the nested-type regression')\nPY\nrc=$?\ntail -n 3 /tmp/d176-seat2-mutation.log\nexit \"$rc\"",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["PASS: boolean-ordinal validator mutation killed by the nested-type regression"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "^PASS: boolean-ordinal validator mutation killed by the nested-type regression$"
      }
    },
    {
      "id": "V4",
      "kind": "inspection",
      "cmd": "git diff --exit-code HEAD -- scripts/run_night.py joulewise/arm_readiness.py joulewise/t0_rehearsal.py scripts/magistrate_watchdog.py",
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
  "flags": [
    {
      "id": "F1",
      "kind": "lead_ruling",
      "level": "blocking",
      "text": "NEEDS_RULING: What exact production roots constitute PRODUCTION_CUSTODY_ROOTS? Sections 6/10 S4 require a frozen census but do not enumerate it. The existing bundle.production_roots comes from caller-supplied manifest entries in scripts/rehearse_t0_unattended.py:149-175. Options considered: freeze a lead-approved complete census, or retain caller-selected roots. Recommendation: freeze the lead-approved census; caller selection cannot establish completeness.",
      "needs": "Provide the complete authoritative root list or its governing source. Blocks the shared constant and G6 migration."
    },
    {
      "id": "F2",
      "kind": "lead_ruling",
      "level": "blocking",
      "text": "NEEDS_RULING: What governed lookup supplies the driver's pack_root, selected ARM receipt, launch_manifest and preparation entry point? The exact v3 plan contains pack identity and record bindings but no locators for these inputs. Existing run_night executes chain_path directly; the launcher requires explicit pack/ARM/manifest paths. Options considered: a ruled deterministic lookup with ambiguity refusal, or an explicit bound locator/transport amendment. Recommendation: pin deterministic lookup rules and preparation ownership without silently expanding the exact plan schema.",
      "needs": "Rule input discovery and preparation/ARM sequencing, then resume seat 2. Blocks ARM-before-GO orchestration, runtime C1-C5 authentication, GO issuance and launcher argv integration."
    }
  ]
}
```

## Change

Completed the independent plan/installer work. No commit was made. Contract §9 records partial implementation pins without claiming producer completion.

| Clause | Production site | Regression | Counterfactual |
|---|---|---|---|
| B1: exact v3 plan | `night_gate.py:208,291` | `test_night_plan_writer.py:74,101` | Accept v2 pack plans, missing bindings or malformed ordinals |
| B1: persisted attempt | `night_plan_writer.py:18,45` | `test_night_plan_writer.py:47,156` | Recompute the ordinal or replace armed bytes with an invalid plan |
| B1: absolute installation pin | `install_night_agent.sh:39,73,80` | `test_install_night_agent.py:152,165` | Install an unresolved path or invalid v3 plan |
| B5 / §8.3: locator structure | `night_gate.py:311` | `test_night_plan_writer.py:101,134,149` | Accept malformed, aliased or custody-escaping bindings |
| F11: watchdog compatibility | `night_gate.py:208`; unchanged watchdog `:686` | `test_night_plan_writer.py:165` | Watchdog rejects or mutates a serialized v3 plan |

## Verification notes

Added the previously nonexistent `tests.test_night_plan_writer`; no requested module was dropped. All 179 acceptance tests passed. Testing followed the requested bounded suite.

Source comparison confirmed `_RECEIPT_KEYS`, the receipt validator, the pack refusal fence and `chain.started` implementation remain unchanged.

## Residual risk

GO production, runtime record authentication, C1–C5, T-0 inventory/digest, launcher transport and shared-root G6 remain unimplemented. The existing pack refusal fence remains active.

Next step: the lead supplies F1/F2 rulings and resumes seat 2; integration review and live qualification remain pending.