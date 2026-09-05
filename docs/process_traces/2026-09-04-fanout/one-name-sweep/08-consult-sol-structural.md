```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "R2 is a history-shape false blocker: preserve the historical evidence anchor, downgrade current-last-touch equality, and replay by content identity.",
  "workspace": {
    "base_requested": "8b9113a75325e87f3d36cb4b669bc37c14d2026f",
    "base_mode": "exact",
    "head_start": "8b9113a75325e87f3d36cb4b669bc37c14d2026f",
    "head_end": "8b9113a75325e87f3d36cb4b669bc37c14d2026f",
    "upstream_end": "a6e9edde082f460fbe335d2eac8021f77258b8e6",
    "branch": "feat/2026-09-04-fan-one-name-sweep"
  },
  "pathspec": [
    "docs/process_traces/2026-09-04-fanout/one-name-sweep/08-consult-sol-structural.md"
  ],
  "unowned_dirty": [],
  "verdict": {
    "findings": [
      {
        "id": "S1",
        "severity": "should_fix",
        "location": "scripts/issue_dg071_dg075_statistics.py:398-410,590-594,623-626; tests/test_issue_dg071_dg075_statistics.py:653-771",
        "text": "The replay gate mistakes the checkout's latest producer-path commit for producer identity. A same-byte restoration changes that history-derived value while leaving the input, producer bytes, computation, and issued evidence unchanged, so every attempted producer-path fix recreates R2.",
        "counterfactual": "If producer identity is the script content hash and the stored commit is checked only as a historical locator for those bytes, the present branch passes the evidence check and merely records that its current last-touch commit differs."
      }
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "inspection",
      "cmd": "git rev-parse HEAD && git branch --show-current && git status --short --branch",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "8b9113a75325e87f3d36cb4b669bc37c14d2026f",
          "feat/2026-09-04-fan-one-name-sweep",
          "## feat/2026-09-04-fan-one-name-sweep...origin/feat/2026-09-04-fan-one-name-sweep"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "^8b9113a75325e87f3d36cb4b669bc37c14d2026f\\nfeat/2026-09-04-fan-one-name-sweep\\n## feat/2026-09-04-fan-one-name-sweep\\.\\.\\.origin/feat/2026-09-04-fan-one-name-sweep$"
      }
    },
    {
      "id": "V2",
      "kind": "inspection",
      "cmd": "artifact_commit=$(python3 -c 'import json; print(json.load(open(\"docs/paper/round7/dg071-dg075-statistics.json\"))[\"producer\"][\"git_commit\"])')\nartifact_sha=$(python3 -c 'import json; print(json.load(open(\"docs/paper/round7/dg071-dg075-statistics.json\"))[\"producer\"][\"script_sha256\"])')\ncurrent_last=$(git log -1 --format=%H -- scripts/issue_dg071_dg075_statistics.py)\ncurrent_sha=$(shasum -a 256 scripts/issue_dg071_dg075_statistics.py | cut -d' ' -f1)\nhistorical_sha=$(git show \"$artifact_commit\":scripts/issue_dg071_dg075_statistics.py | shasum -a 256 | cut -d' ' -f1)\nprintf 'artifact_commit=%s\\ncurrent_last=%s\\nartifact_sha=%s\\ncurrent_sha=%s\\nhistorical_sha=%s\\n' \"$artifact_commit\" \"$current_last\" \"$artifact_sha\" \"$current_sha\" \"$historical_sha\"\ntest \"$artifact_sha\" = \"$current_sha\"\ntest \"$artifact_sha\" = \"$historical_sha\"\ntest \"$artifact_commit\" != \"$current_last\"\nprintf 'CONTENT_IDENTITY_WITH_HISTORY_DIVERGENCE\\n'",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "artifact_commit=6b6deb2f8f9bbe88b604b18d544856d6ae4e0013",
          "current_last=94af46458aab6bb8597f2c4564f9b6d1e0d6975e",
          "artifact_sha=d657d75fc4bfa36dbfc12249b791a73541ae6e043eb861e4050c297e537f46d9",
          "current_sha=d657d75fc4bfa36dbfc12249b791a73541ae6e043eb861e4050c297e537f46d9",
          "historical_sha=d657d75fc4bfa36dbfc12249b791a73541ae6e043eb861e4050c297e537f46d9",
          "CONTENT_IDENTITY_WITH_HISTORY_DIVERGENCE"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "artifact_commit=6b6deb2f.*\\ncurrent_last=94af4645.*\\nartifact_sha=([0-9a-f]{64})\\ncurrent_sha=\\1\\nhistorical_sha=\\1\\nCONTENT_IDENTITY_WITH_HISTORY_DIVERGENCE"
      }
    },
    {
      "id": "V3",
      "kind": "inspection",
      "cmd": "report=docs/process_traces/2026-09-04-fanout/one-name-sweep/08-consult-sol-structural.md\nsed -n '2,/^```$/p' \"$report\" | sed '$d' | python3 -m json.tool >/dev/null\njson_bytes=$(sed -n '2,/^```$/p' \"$report\" | sed '$d' | wc -c | tr -d ' ')\ntest \"$json_bytes\" -le 8192\nprintf 'JSON_VALID bytes=%s\\n' \"$json_bytes\"\ngit diff --no-index --check /dev/null \"$report\"\ndiff_exit=$?\ntest \"$diff_exit\" -eq 1\nprintf 'DIFF_CHECK_CLEAN\\n'\ngit rev-parse HEAD\ngit status --short",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "JSON_VALID bytes=5747",
          "DIFF_CHECK_CLEAN",
          "8b9113a75325e87f3d36cb4b669bc37c14d2026f",
          "?? docs/process_traces/2026-09-04-fanout/one-name-sweep/08-consult-sol-structural.md"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "^JSON_VALID bytes=[0-9]+\\nDIFF_CHECK_CLEAN\\n8b9113a75325e87f3d36cb4b669bc37c14d2026f\\n\\?\\? docs/process_traces/2026-09-04-fanout/one-name-sweep/08-consult-sol-structural.md$"
      }
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "This is a design consult; the restore-history regression that proves the cure does not exist and was not run.",
      "needs": "After the magistrate adopts the ruling, implement the asymmetric verifier and run the single regression specified in Q3."
    }
  ]
}
```

## Findings

**Q1 / S1 — structural cause.** R2 is caused by coupling deterministic evidence bytes to mutable Git graph shape. `_git_commit()` asks `git log -1 -- <producer path>` at runtime (`scripts/issue_dg071_dg075_statistics.py:398-410`), then injects that answer into JSON and Markdown (`:590-594`, `:623-626`). The implementation's stability claim is conditional on later commits leaving the path untouched (`:401-404`), but the fix process changed and then restored that path: the restored script, the script at stored commit `6b6deb2f`, and artifact `script_sha256` are byte-identical, while `git log` now returns restore commit `94af4645`. The current regression models only unrelated and empty later commits (`tests/test_issue_dg071_dg075_statistics.py:697-704`), so it misses the same-byte restore case; the re-audit therefore reports the inevitable result—tree identity passes while only `producer.git_commit` differs (`06-delta-reaudit-round-1.md:62-73,113-119`). Squashing happens to erase this instance of the graph edge but does not cure the class.

**Q2 — threat model under D-161.** Split the present check asymmetrically. The immutable artifact's historical tuple is an evidence fence and stays fail-closed: its stored commit must resolve, and `git show <stored-commit>:<script-path>` must hash to stored `script_sha256`; input digest and computed statistics must also agree. Equality between that stored commit and the current checkout's latest path-touch commit is only an operator/history-shape guard, because it rejects identical producer bytes without detecting any change in physics, evidence, or pre-registration; downgrade it to WARN-AND-RECORD, not a blocker. That is D-161's exact boundary: historical-side equality remains blocking, current-side equality becomes warning (`docs/decision_log.md:10363-10368`), while operator-only custody machinery is over-engineering (`docs/decision_log.md:207`).

**Q3 — cure and proof.** Use a content-addressed, asymmetric replay mechanism, not history-excluding landing surgery: preserve the issued v2 bytes; regenerate the input-bound/statistical payload from the current script; require current script SHA = stored script SHA; independently authenticate the stored commit-to-script-SHA link; treat current last-touch divergence as recorded metadata only. Re-scope this one-name mission to mutable authored terminology surfaces, excluding immutable issued artifacts and their producer, and land it normally. One regression proves the class closed: in a temporary repository, issue from producer commit P, commit a producer edit, commit an exact-byte restoration R, assert `last_touch(R) != P`, and require historical-anchor validation plus byte-exact semantic replay to pass while emitting the nonblocking divergence warning.

**Q4 — magistrate ruling row, verbatim.** `one-name-sweep is remanded for a threat-model correction, not a third fix round: R2's current-head git-log equality is an operator/history-shape check and is downgraded to WARN-AND-RECORD under D-161. The evidence fence remains fail-closed: the immutable artifact's stored producer commit must resolve to script bytes matching its stored script SHA-256, and the input digest and regenerated statistical payload must match. Re-scope the mission to mutable authored terminology surfaces, preserve the issued DG-071/DG-075 bytes, and land by ordinary ancestry-preserving merge rather than squash surgery. Acceptance is the change-then-exact-restore regression: current last-touch differs, the historical anchor passes, and replay passes while recording the warning.`

## Residual risk

The proposed verifier boundary and regression are not implemented in this design-only scope. Until they are, the existing full-file replay command will continue to report the known provenance-only mismatch; it must not be silently treated as the new asymmetric verdict.
