```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "clean",
  "completion": "complete",
  "summary": "Control passed; all five ruled mutants were killed with the reference pairwise escape counts.",
  "workspace": {
    "base_requested": "6e2504b1",
    "base_mode": "exact",
    "head_start": "6e2504b166a6c9b5be85b4b916adfd2d4dae814a",
    "head_end": "6e2504b166a6c9b5be85b4b916adfd2d4dae814a",
    "upstream_end": null,
    "branch": "fix/2026-09-24-a291-r3-packer"
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "findings": [],
    "control": {
      "pairwise_escape_count": 0,
      "named_seal": "NAMED_SEAL {\"AUD-1\": \"refused:inv_11\", \"B1\": \"refused:inv_11\", \"B1-singles-voided\": \"refused:inv_11\", \"B2\": \"refused:inv_11\", \"cross-model-reorder\": \"refused:inv_10\", \"legal-contrast\": \"accepted\", \"probe-D\": \"refused:inv_11\"}",
      "tests_passed": true
    },
    "mutants": [
      {
        "id": "m1",
        "source": "joulewise/scored_packer.py:96,98",
        "diff": "-            held = counts == (1, 0) and not view[\"blocks\"][live[0][0]][\"superseded\"] and not any(\n+            held = bool(live) and not view[\"blocks\"][live[0][0]][\"superseded\"] and not any(\n-            _need(held or counts == (0, 1), \"inv_11\", \"item conservation\")\n+            _need((len(live) <= 1 and len(term) <= 1) and (not live or held), \"inv_11\", \"item conservation\")",
        "pairwise_escape_count": 45,
        "named_seal": "NAMED_SEAL {\"AUD-1\": \"refused:inv_11\", \"B1\": \"refused:inv_11\", \"B1-singles-voided\": \"refused:inv_11\", \"B2\": \"refused:inv_11\", \"cross-model-reorder\": \"refused:inv_10\", \"legal-contrast\": \"accepted\", \"probe-D\": \"refused:inv_11\"}",
        "killed": true
      },
      {
        "id": "m2",
        "source": "joulewise/scored_packer.py:96",
        "diff": "-            held = counts == (1, 0) and not view[\"blocks\"][live[0][0]][\"superseded\"] and not any(\n+            held = counts == (1, 0) and not any(",
        "pairwise_escape_count": 2,
        "named_seal": "NAMED_SEAL {\"AUD-1\": \"refused:inv_11\", \"B1\": \"refused:inv_11\", \"B1-singles-voided\": \"refused:stale_derived\", \"B2\": \"refused:inv_11\", \"cross-model-reorder\": \"refused:inv_10\", \"legal-contrast\": \"accepted\", \"probe-D\": \"refused:inv_11\"}",
        "killed": true
      },
      {
        "id": "m3",
        "source": "joulewise/scored_packer.py:86",
        "diff": "-        term.setdefault((entry[\"model\"], entry[\"item_id\"]), []).append(entry)\n+        term[(entry[\"model\"], entry[\"item_id\"])] = [entry]",
        "pairwise_escape_count": 276,
        "named_seal": "NAMED_SEAL {\"AUD-1\": \"refused:inv_11\", \"B1\": \"refused:inv_11\", \"B1-singles-voided\": \"refused:inv_11\", \"B2\": \"refused:inv_11\", \"cross-model-reorder\": \"refused:inv_10\", \"legal-contrast\": \"accepted\", \"probe-D\": \"refused:inv_11\"}",
        "killed": true
      },
      {
        "id": "m4",
        "source": "joulewise/scored_packer.py:83",
        "diff": "-                live.setdefault((block[\"model\"], item), []).append((bid, envelope[\"index\"]))\n+                live[(block[\"model\"], item)] = [(bid, envelope[\"index\"])]",
        "pairwise_escape_count": 355,
        "named_seal": "NAMED_SEAL {\"AUD-1\": \"refused:inv_11\", \"B1\": \"accepted\", \"B1-singles-voided\": \"refused:inv_11\", \"B2\": \"refused:inv_11\", \"cross-model-reorder\": \"refused:inv_10\", \"legal-contrast\": \"accepted\", \"probe-D\": \"refused:inv_11\"}",
        "killed": true
      },
      {
        "id": "m5",
        "source": "joulewise/scored_packer.py:81",
        "diff": "+            if block[\"superseded\"]:\n+                continue",
        "pairwise_escape_count": 184,
        "named_seal": "NAMED_SEAL {\"AUD-1\": \"refused:inv_11\", \"B1\": \"accepted\", \"B1-singles-voided\": \"refused:inv_11\", \"B2\": \"accepted\", \"cross-model-reorder\": \"refused:inv_10\", \"legal-contrast\": \"accepted\", \"probe-D\": \"refused:inv_11\"}",
        "killed": true
      }
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "test",
      "cmd": "cd /tmp/278ebc9e/mk/control && python3 -B -m unittest tests.test_scored_ownership_forgery.OwnershipForgeryTests.test_pairwise_seal_property tests.test_scored_ownership_forgery.OwnershipForgeryTests.test_named_seal_regressions",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["Ran 2 tests in 18.379s", "OK"]},
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "cd /tmp/278ebc9e/mk/m1 && python3 -B -m unittest tests.test_scored_ownership_forgery.OwnershipForgeryTests.test_pairwise_seal_property tests.test_scored_ownership_forgery.OwnershipForgeryTests.test_named_seal_regressions",
      "cwd": ".",
      "observed": {"result": "fail", "exit_code": 1, "tail": ["FAILED (failures=1)"]},
      "expected": {"exit_code": 1, "tail_regex": "FAILED \\(failures=1\\)"}
    },
    {
      "id": "V3",
      "kind": "test",
      "cmd": "cd /tmp/278ebc9e/mk/m2 && python3 -B -m unittest tests.test_scored_ownership_forgery.OwnershipForgeryTests.test_pairwise_seal_property tests.test_scored_ownership_forgery.OwnershipForgeryTests.test_named_seal_regressions",
      "cwd": ".",
      "observed": {"result": "fail", "exit_code": 1, "tail": ["FAILED (failures=2)"]},
      "expected": {"exit_code": 1, "tail_regex": "FAILED \\(failures=2\\)"}
    },
    {
      "id": "V4",
      "kind": "test",
      "cmd": "cd /tmp/278ebc9e/mk/m3 && python3 -B -m unittest tests.test_scored_ownership_forgery.OwnershipForgeryTests.test_pairwise_seal_property tests.test_scored_ownership_forgery.OwnershipForgeryTests.test_named_seal_regressions",
      "cwd": ".",
      "observed": {"result": "fail", "exit_code": 1, "tail": ["FAILED (failures=1)"]},
      "expected": {"exit_code": 1, "tail_regex": "FAILED \\(failures=1\\)"}
    },
    {
      "id": "V5",
      "kind": "test",
      "cmd": "cd /tmp/278ebc9e/mk/m4 && python3 -B -m unittest tests.test_scored_ownership_forgery.OwnershipForgeryTests.test_pairwise_seal_property tests.test_scored_ownership_forgery.OwnershipForgeryTests.test_named_seal_regressions",
      "cwd": ".",
      "observed": {"result": "fail", "exit_code": 1, "tail": ["FAILED (failures=2)"]},
      "expected": {"exit_code": 1, "tail_regex": "FAILED \\(failures=2\\)"}
    },
    {
      "id": "V6",
      "kind": "test",
      "cmd": "cd /tmp/278ebc9e/mk/m5 && python3 -B -m unittest tests.test_scored_ownership_forgery.OwnershipForgeryTests.test_pairwise_seal_property tests.test_scored_ownership_forgery.OwnershipForgeryTests.test_named_seal_regressions",
      "cwd": ".",
      "observed": {"result": "fail", "exit_code": 1, "tail": ["FAILED (failures=2)"]},
      "expected": {"exit_code": 1, "tail_regex": "FAILED \\(failures=2\\)"}
    }
  ],
  "flags": []
}
```