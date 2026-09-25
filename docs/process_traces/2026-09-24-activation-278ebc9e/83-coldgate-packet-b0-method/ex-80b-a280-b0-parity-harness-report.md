```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "findings",
  "completion": "complete",
  "summary": "Implemented the tests-only B0 IDLE differential harness; self-parity passes and both negative controls expose the required witnesses.",
  "workspace": {
    "base_requested": "bee658c5",
    "base_mode": "exact",
    "head_start": "bee658c5acc4dd860a382317c40ec4421587a13a",
    "head_end": "bee658c5acc4dd860a382317c40ec4421587a13a",
    "upstream_end": null,
    "branch": "test/2026-09-24-b0-idle-parity"
  },
  "pathspec": [
    "tests/parity/__init__.py",
    "tests/parity/b0_corpus.py",
    "tests/parity/b0_runner.py",
    "tests/test_b0_idle_parity.py"
  ],
  "unowned_dirty": [],
  "verdict": {
    "implementation": "implemented",
    "acceptance": "ready"
  },
  "verification": [
    {
      "id": "V1",
      "kind": "suite",
      "cmd": "python3 -B tests/parity/b0_runner.py --self --output /tmp/278ebc9e/b0par-final-v1",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "seed=278097879 observations=99443 mismatches=0",
          "outcome_mismatches=0 new_private_api=0",
          "shared_surface_mismatches=0",
          "authority_failures=0",
          "inventory=/tmp/278ebc9e/b0par-final-v1/inventory.md",
          "runtime_seconds=263.205",
          "PARITY PASS"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "PARITY PASS"
      }
    },
    {
      "id": "V2",
      "kind": "suite",
      "cmd": "python3 -B tests/parity/b0_runner.py --candidate-ref 7647bb2e --output /tmp/278ebc9e/b0par-final-v2",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": [
          "seed=278097879 observations=99443 mismatches=57819",
          "outcome_mismatches=35351 new_private_api=1688",
          "shared_surface_mismatches=56131",
          "authority_failures=2",
          "inventory=/tmp/278ebc9e/b0par-final-v2/inventory.md",
          "runtime_seconds=270.092",
          "PARITY FAIL"
        ]
      },
      "expected": {
        "exit_code": 1,
        "tail_regex": "PARITY FAIL"
      }
    },
    {
      "id": "V3",
      "kind": "suite",
      "cmd": "python3 -B tests/parity/b0_runner.py --candidate . --output /tmp/278ebc9e/b0par-final-v3",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": [
          "seed=278097879 observations=99443 mismatches=33066",
          "outcome_mismatches=19615 new_private_api=1688",
          "shared_surface_mismatches=31378",
          "authority_failures=2",
          "inventory=/tmp/278ebc9e/b0par-final-v3/inventory.md",
          "runtime_seconds=267.354",
          "PARITY FAIL"
        ]
      },
      "expected": {
        "exit_code": 1,
        "tail_regex": "PARITY FAIL"
      }
    },
    {
      "id": "V4",
      "kind": "other",
      "cmd": "python3 -B - <<'PY'\nimport json\nfrom pathlib import Path\nfor name in ('v1','v2','v3'):\n s=json.loads((Path('/tmp/278ebc9e')/('b0par-final-'+name)/'summary.json').read_text())\n assert s['observations']==99443\n assert s['runtime_seconds']<600\n print(name+' runtime_seconds='+str(s['runtime_seconds']))\nprint('V4 PASS: each full comparison finished within 600 seconds')\nPY",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "v1 runtime_seconds=263.205",
          "v2 runtime_seconds=270.092",
          "v3 runtime_seconds=267.354",
          "V4 PASS: each full comparison finished within 600 seconds"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "V4 PASS"
      }
    },
    {
      "id": "UNIT",
      "kind": "test",
      "cmd": "python3 -B -m unittest tests.test_b0_idle_parity",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": [
          "Ran 10 tests in 11.168s",
          "",
          "FAILED (failures=1)"
        ]
      },
      "expected": {
        "exit_code": 1,
        "tail_regex": "FAILED \\(failures=1\\)"
      }
    },
    {
      "id": "SHRINK",
      "kind": "test",
      "cmd": "python3 -B tests/parity/b0_runner.py --candidate . --case 72b.F1.bom --operation driver.cleanup --shrink --output /tmp/278ebc9e/b0par-final-shrink",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": [
          "shared_surface_mismatches=1",
          "authority_failures=0",
          "inventory=/tmp/278ebc9e/b0par-final-shrink/inventory.md",
          "runtime_seconds=5.122",
          "PARITY FAIL"
        ]
      },
      "expected": {
        "exit_code": 1,
        "tail_regex": "PARITY FAIL"
      }
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "The canonical repository suite was not run. Verification covered the standalone test tooling, full differential corpus, focused unittest module, shrinking, syntax, whitespace, and write-scope checks.",
      "needs": "Lead owns final repository verification."
    },
    {
      "id": "F2",
      "kind": "residual_risk",
      "level": "nonblocking",
      "text": "External process and hardware effects are fixture-controlled; results are offline compatibility evidence, not live hardware validation.",
      "needs": ""
    }
  ]
}
```

## Change

Implemented 11,346 cases: every single-axis variation, 8,527 isolated pairs, the exhaustive 2,560-case cleanup cross, seeded multifaults, scheduled read changes, and named historical witnesses. Each full comparison evaluates 99,443 observations per side.

The runner preserves exact outputs, exceptions, refusal codes, file bytes/modes, and ordered dependency calls. Both sides use separate subprocesses with independently restored fixtures and frozen environment inputs. Files remain uncommitted; no production changes or other agents were used.

## Verification notes

V2 reproduces the round-0 witnesses, including `29a.F2`, `29b.B1`, `29b.B2`, and `29b.N1`, at their relevant entry points. [Complete V2 inventory](/tmp/278ebc9e/b0par-final-v2/inventory.md).

V3 confirms:

- **F1:** BOM/UTF-16 receipts with unreadable wrappers change cleanup return values and file effects.
- **F2:** sealing refusal text changes; source drift changes `dirty clone` to `candidate chain source differs from sealed binding`.
- **F3:** list/object kinds change `Refused` into `TypeError`.
- **F4:** both bare-wrapper witnesses select a row without the required authority.

The private helper did not exist at the oracle. Its availability differences are retained separately; F4 has an explicit authority assertion. They are not presented as proof of a public cleanup bypass.

The focused unittest’s sole failure is the intended current-candidate parity gate. Shrinking F1 retains both faults: removing either eliminates the file/return difference.

V3 inventory below counts differing case/entry-point observations. **Every case is listed in the [grouped inventory](/tmp/278ebc9e/b0par-final-v3/inventory.md); every exact field difference is retained in [diffs.jsonl.gz](/tmp/278ebc9e/b0par-final-v3/diffs.jsonl.gz).**

| Entry point | Differences |
|---|---:|
| diagnostic.custody_row | 1,688 |
| driver.cleanup | 1,941 |
| driver.courier_cleanup | 1,941 |
| evidence.candidate_payload_kind | 3,207 |
| evidence.candidate_state | 150 |
| evidence.clone_census | 3,372 |
| evidence.notice_subject | 3,372 |
| evidence.notice_unused | 3,297 |
| evidence.prepare | 384 |
| evidence.prepare_fresh | 60 |
| evidence.render_notice | 4,476 |
| evidence.sealed_candidate | 2,958 |
| evidence.sealed_state | 1,299 |
| evidence.sealed_state_published | 1,299 |
| generator.render_only | 179 |
| installer.receipt_validation | 2,395 |
| installer.render | 192 |
| installer.uninstall | 176 |
| installer.verify | 530 |
| installer.veto | 150 |
| **Total** | **33,066** |

Zero differences: driver artifact listing, courier argv, durable recording, probe dispatch, refusal reporting, gate C3/C5, and `zero_capture_facts`.

Of the total, 19,615 affect outcomes, 11,763 affect dependency calls only, and 1,688 concern the new private API, including two F4 authority failures. Runtime excludes waiting for the fixture serialization lock.

## Residual risk

Coverage is finite and external effects are simulated. Next step: independent lead review of the harness and witnesses, followed by the separate production-fix seat.