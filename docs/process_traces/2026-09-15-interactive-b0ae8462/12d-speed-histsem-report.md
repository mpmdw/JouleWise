```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "blocked",
  "completion": "partial",
  "summary": "H1 implemented and verified; H2 requires a ruling because pack-only sparse checkout refuses valid historical generators.",
  "workspace": {
    "base_requested": "e991ef89ef2d713e228792319c063adb4c60ca42",
    "base_mode": "exact",
    "head_start": "e991ef89ef2d713e228792319c063adb4c60ca42",
    "head_end": "e991ef89ef2d713e228792319c063adb4c60ca42",
    "upstream_end": "46bce53b9d80afd4db373ea01985b70bed366567",
    "branch": "perf/2026-09-15-histsem-batch"
  },
  "pathspec": [
    "joulewise/arm_readiness.py",
    "tests/test_receipt_histsem.py"
  ],
  "unowned_dirty": [],
  "verdict": {
    "implementation": "partial",
    "acceptance": "needs_ruling"
  },
  "verification": [
    {
      "id": "V1",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 /usr/bin/time -p python3 -m unittest -v tests.test_receipt_histsem.HistoricalBlobBatchTests > /private/tmp/histsem-focused.log 2>&1",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Ran 5 tests in 19.135s",
          "OK",
          "real 19.92",
          "user 10.01",
          "sys 8.60"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "OK"
      }
    },
    {
      "id": "V2",
      "kind": "smoke",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 /usr/bin/time -p python3 - <<'PY' > /private/tmp/histsem-cli-before.json 2> /private/tmp/histsem-cli-before.log\nimport runpy\nimport sys\nentry = runpy.run_path('scripts/verify_receipt_histsem.py')\nprint('BASELINE_CLI_IMPORTED', file=sys.stderr, flush=True)\nraise SystemExit(entry['main'](['--repository-root', '.', '--require-published']))\nPY",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "BASELINE_CLI_IMPORTED",
          "real 73.54",
          "user 36.35",
          "sys 32.73"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "BASELINE_CLI_IMPORTED"
      }
    },
    {
      "id": "V3",
      "kind": "smoke",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 /usr/bin/time -p python3 scripts/verify_receipt_histsem.py --repository-root . --require-published > /private/tmp/histsem-cli-after.json 2> /private/tmp/histsem-cli-after.log",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "real 59.71",
          "user 29.71",
          "sys 26.56"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "real [0-9.]+"
      }
    },
    {
      "id": "V4",
      "kind": "test",
      "cmd": "python3 -B - <<'PY'\nimport hashlib\nfrom pathlib import Path\nbefore=Path('/private/tmp/histsem-cli-before.json').read_bytes()\nafter=Path('/private/tmp/histsem-cli-after.json').read_bytes()\nassert before == after\nprint('CLI outputs byte-identical:', hashlib.sha256(after).hexdigest())\nPY",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "CLI outputs byte-identical: a9b969cc9914d4de49683d2bfeb5f667bc22b2be81490701364d48f1ccc7f0b6"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "CLI outputs byte-identical: a9b969cc9914d4de49683d2bfeb5f667bc22b2be81490701364d48f1ccc7f0b6"
      }
    },
    {
      "id": "V5",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 /usr/bin/time -p python3 -m unittest tests.test_receipt_histsem > /private/tmp/histsem-after.log 2>&1\nhistsem_test_exit=$?\nprintf '%s\\n' \"$histsem_test_exit\" > /private/tmp/histsem-after.exit\nexit \"$histsem_test_exit\"",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Ran 73 tests in 1373.340s",
          "OK (skipped=1)",
          "real 1374.10",
          "user 643.22",
          "sys 663.45"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "OK \\(skipped=1\\)"
      }
    },
    {
      "id": "V6",
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
  "flags": [
    {
      "id": "F1",
      "kind": "lead_ruling",
      "level": "blocking",
      "text": "NEEDS_RULING: H2's pack-only sparse set conflicts with unchanged published-corpus PASS. A real sparse probe of d117_contrast_qwen25_1p5b_vs_7b_v1 at c3d805ee94629a0588f44b0ccb8430fd52ec07b3 refused histsem_historical_digest_mismatch because its generator imports joulewise outside the pack: ModuleNotFoundError. Production checkout behavior remains unchanged. The new outside-reference regression confirms a missing external artifact refuses loudly.",
      "needs": "Rule whether H2 may include a reviewed closure of historical generator libraries and external inputs, or defer H2. Recommend reviewing and authorizing that dependency closure. Production H2 is blocked pending this ruling."
    },
    {
      "id": "F2",
      "kind": "verification_gap",
      "level": "blocking",
      "text": "The timed before-module run lost its execution handle on resumption. Its log ends after 55 results, including one skip, with no failures or completion/time tail. Last observed elapsed time was 1347.7 seconds. No completed before-module timing or full-module speedup is claimed. Partial evidence remains in /private/tmp/histsem-before.log.",
      "needs": "Obtain an uninterrupted timed tests.test_receipt_histsem baseline at BASE_HEAD before accepting the module performance comparison."
    },
    {
      "id": "F3",
      "kind": "environment",
      "level": "nonblocking",
      "text": "Measurements used Python 3.14.7 and Apple Git 2.50.1 on the shared machine; they are not CI estimates. origin/main advanced independently during execution, while the requested HEAD remained unchanged. No commits or out-of-scope repository edits were made.",
      "needs": ""
    }
  ]
}
```

## Change

H1 adds the batch decoder at [line 3394](/Users/edr/code/JouleWise-wt-speed-histsem/joulewise/arm_readiness.py:3394) and integrates it into the digest loop at [line 3547](/Users/edr/code/JouleWise-wt-speed-histsem/joulewise/arm_readiness.py:3547).

The [new tests](/Users/edr/code/JouleWise-wt-speed-histsem/tests/test_receipt_histsem.py:2770) compare **2,325 blob payloads across 18 coordinates** using byte equality against legacy reads. All pinned digests match. Sorted paths, modes, lengths, hashes, and digest framing remain unchanged; all pre-existing test source bytes are preserved.

## Verification notes

CLI wall time was **73.54 → 59.71 seconds**, with identical PASS output for 9 packs and 99 receipts. The incomplete baseline prevents a complete module timing comparison.

H2 remains unapplied pending the dependency-set ruling above.

## Residual risk

Batching buffers a whole pack’s blobs rather than one blob at a time; the largest tested coordinate contained 900,226 bytes. The existing 20-second Git timeout now covers the complete batch.