```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "clean",
  "completion": "complete",
  "summary": "D1 cured: active v2 is accepted, while v1 is historical and limited to pre-relabel artifacts.",
  "workspace": {
    "base_requested": "28fd95b4e9410b3ab524c3665b0aa5faa9853be9",
    "base_mode": "exact",
    "head_start": "28fd95b4e9410b3ab524c3665b0aa5faa9853be9",
    "head_end": "28fd95b4e9410b3ab524c3665b0aa5faa9853be9",
    "upstream_end": "28fd95b4e9410b3ab524c3665b0aa5faa9853be9",
    "branch": "feat/2026-09-05-d165-relabel"
  },
  "pathspec": [
    "docs/paper/round7/fill-checklist.md",
    "docs/paper/round7/structural-edits.md",
    "docs/process_traces/2026-09-05-d165-relabel/06-fix-round-3-report.md"
  ],
  "unowned_dirty": [],
  "verdict": {
    "implementation": "implemented",
    "acceptance": "ready"
  },
  "verification": [
    {
      "id": "V1",
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
    },
    {
      "id": "V2",
      "kind": "inspection",
      "cmd": "git diff --name-only -- docs/paper/round7/fill-checklist.md docs/paper/round7/structural-edits.md",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "docs/paper/round7/fill-checklist.md",
          "docs/paper/round7/structural-edits.md"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "docs/paper/round7/structural-edits\\.md$"
      }
    }
  ],
  "flags": []
}
```

## Change

Updated the authenticated replay acceptance to allow active v2 and historical v1 only for pre-relabel artifacts. Updated the S03 insertion-authority citation to identify v2 as active and v1 as historical, and added the requested dated supersession note. No commit was made.

Quoted old and new lines:

- `docs/paper/round7/fill-checklist.md:138`
  - Old:
    > unavailable unless the registered `d165_shared_sign_local_corner_replay.v1`
    > result can be authenticated against the same custodied block inputs.
  - New:
    > unavailable unless the registered `d165_shared_sign_local_corner_replay.v2`
    > (active) or `d165_shared_sign_local_corner_replay.v1` (historical, pre-relabel
    > artifacts only) result can be authenticated against the same custodied block
    > inputs.
- `docs/paper/round7/structural-edits.md:86`
  - Old:
    > **Authority:** `docs/decision_log.md` D-165 R-5 completion; D-165-as-amended index row; `06-COLD-GATE-RULING.md` R-2; the registered replay in `configs/campaigns/d117_contrast_v5/generate_configs.py` (`_common_mode_split`, `replay_common_mode_dominance`, and the `d165_shared_sign_local_corner_replay.v1` registration); `docs/paper/results-fill-registry.md` comparative and absolute R_cm rows.
  - New:
    > **Authority:** `docs/decision_log.md` D-165 R-5 completion; D-165-as-amended index row; `06-COLD-GATE-RULING.md` R-2; the registered replay in `configs/campaigns/d117_contrast_v5/generate_configs.py` (`_common_mode_split`, `replay_common_mode_dominance`, and the `d165_shared_sign_local_corner_replay.v2` registration (active); the `d165_shared_sign_local_corner_replay.v1` registration is historical and accepted only for pre-relabel artifacts); `docs/paper/results-fill-registry.md` comparative and absolute R_cm rows.
  - Added:
    > **SUPERSEDED 2026-09-05 — D-165 ratified addendum:** The prior v1-only insertion-authority citation is retained for custody and must not be used as active paper authority. Active replay rule: `d165_shared_sign_local_corner_replay.v2`; `d165_shared_sign_local_corner_replay.v1` is historical and accepted only for pre-relabel artifacts.

## Verification notes

Docs-only preflight applied; no tests were run. `git diff --check` passed, and the requested consumer diff is confined to the two named paper files. The report itself is the only additional modified path. No model launcher was started.
