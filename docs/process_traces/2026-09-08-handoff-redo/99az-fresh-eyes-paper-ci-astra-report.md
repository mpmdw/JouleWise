```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "clean",
  "completion": "complete",
  "summary": "Restoration is byte-identical; census is exact; no new defect found.",
  "workspace": {
    "base_requested": "83f61672",
    "base_mode": "exact",
    "head_start": "ff417462738153000ead16742c326701dbee07b4",
    "head_end": "ff417462738153000ead16742c326701dbee07b4",
    "upstream_end": "ff417462738153000ead16742c326701dbee07b4",
    "branch": "int/2026-09-08-paper-s1-s6-s7"
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {"findings": []},
  "verification": [
    {
      "id": "V1",
      "kind": "test",
      "cmd": "python3 -B -m unittest tests.test_d165_rationale_census",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["Ran 10 tests in 8.102s", "OK"]},
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "python3 -B -m unittest tests.test_paper_round7_artifacts.TypedArtifactCliTests.test_prose_fixture_uses_checklist_sentence_and_real_skeleton_prose",
      "cwd": ".",
      "observed": {"result": "fail", "exit_code": 1, "tail": ["FileNotFoundError: No usable temporary directory"]},
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "V2 could not import because the read-only sandbox provides no writable temporary directory; parser inspected directly.",
      "needs": "Lead may rerun V2 in its normal test environment."
    }
  ]
}
```

## Findings

None.

1. Checklist lines 59–67 equal `main` lines 35–43 byte-for-byte, **including indentation**. `_checklist_standing_sentence` at `tests/test_paper_round7_artifacts.py:1291` selects marker `"  The mandatory standing sentence is:\n\n"`, strips `"  > "`, and joins the four quoted lines. It parses exactly the restored sentence. Its assertion at 1298 is `self.assertTrue(sentence.startswith(FENCE.DX_STANDING_SENTENCE_HEAD))`: prefix validation, not full-sentence equality.

2. All **36** allowlist keys exactly match census occurrences. Changed retained targets, quoting relevant text:
   - `docs/paper/results-fill-registry.md:270`: “common-time replay is implemented; absolute R_cm is not_applicable because the” (preceding line supplies the negation).
   - Same file, **279, 287, 295, 303**, each: “no absolute common-time replay is implemented; absolute R_cm is not_applicable because the registered replay is comparative-only”.
   - `docs/paper/round7/successor-migration-inventory.md:66`, both added entries: “R_cm uses shared-energy-sign/local-corner numerator, not physical common-time replay.”
   
   Six deleted checklist entries have no retained occurrence.

3. No S7 contradiction. “Future batch gates — pending,” “Preserved historical replay fences,” and “When the DX rows are placed” already supply framing. The adjacent paragraph explicitly rejects importing historical placement counts. Additional framing is optional.

4. No new defect found; no edits made.