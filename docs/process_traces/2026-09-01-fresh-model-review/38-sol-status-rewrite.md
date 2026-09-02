```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "findings",
  "completion": "complete",
  "summary": "Reconciled the standalone advisor status to the 2026-09-01 Qwen3 campaign state, reducing it from 995 to 584 lines with all required checks passing.",
  "workspace": {
    "base_requested": null,
    "base_mode": null,
    "head_start": "c401bf91f59885ab55802f3c466612ab5d512c8a",
    "head_end": "c401bf91f59885ab55802f3c466612ab5d512c8a",
    "upstream_end": null,
    "branch": "feat/2026-09-01-status-rewrite"
  },
  "pathspec": [
    "PROJECT_STATUS.md"
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
      "cmd": "python3 -m unittest tests.test_paper_terms_lint tests.test_gen_state",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "...........................................",
          "----------------------------------------------------------------------",
          "Ran 43 tests in 1.996s",
          "",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 43 tests in .*s\\n\\nOK"
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
      "kind": "inspection",
      "cmd": "missing_count=0\nwhile IFS= read -r path; do\n  if [[ ! -e \"$path\" ]]; then\n    print -r -- \"missing: $path\"\n    missing_count=$((missing_count + 1))\n  fi\ndone < <(rg -o '`[^`]+`' PROJECT_STATUS.md | tr -d '`' | rg '^[A-Za-z0-9_.-]+/' | rg -v '^github[.]com/')\nif (( missing_count == 0 )); then\n  print 'all PROJECT_STATUS repository pointers resolve'\nelse\n  exit 1\nfi",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "all PROJECT_STATUS repository pointers resolve"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "all PROJECT_STATUS repository pointers resolve"
      }
    },
    {
      "id": "V4",
      "kind": "inspection",
      "cmd": "git diff --stat",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          " PROJECT_STATUS.md | 1409 +++++++++++++++++++----------------------------------",
          " 1 file changed, 499 insertions(+), 910 deletions(-)"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "1 file changed, 499 insertions\\(\\+\\), 910 deletions\\(-\\)"
      }
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "baseline_drift",
      "level": "nonblocking",
      "text": "The requested artifact-flow source path does not exist; the landed equivalent is docs/process/v5-artifact-flow.md.",
      "needs": ""
    },
    {
      "id": "F2",
      "kind": "baseline_drift",
      "level": "nonblocking",
      "text": "The task wording associates throwaway-clone re-proof with transaction night, while README and the live state kernel place it on the preceding desk day.",
      "needs": "Confirm only if the task wording was intended to override the live repository authorities."
    },
    {
      "id": "F3",
      "kind": "residual_risk",
      "level": "nonblocking",
      "text": "The current state kernel contains V5-prefixed rows but no D165-prefixed rows; D-168 assigns those rows to a follow-up.",
      "needs": "Register the D-165 close-out rows in the authorized follow-up."
    }
  ]
}
```

## Change

Rewrote the advisor document around the live Qwen3 campaign, the strengthened dominance rule, the prompt-selection mechanism, and the sequenced machine-to-paper path. Historical update prose was collapsed into one ledger, voided evidence was shortened to physical cause and replacement, and internal terminology was either explained at first use or removed.

The document is now 584 lines, down from 995. The frozen paper draft was untouched, no measurement ran, and no commit was created.

## Facts table

| fact | source | disposition |
|---|---|---|
| Qwen3-1.7B-4bit and Qwen3-8B-4bit form the `_v5` frozen-design regeneration | [decision_log.md:10365](/Users/edr/code/JouleWise-wt-status/docs/decision_log.md:10365), [README.md:67](/Users/edr/code/JouleWise-wt-status/README.md:67) | Carried, with MLX and M3 Max explained plainly |
| Plan semantics use SHA-256; a separate golden readback pins literal registration bytes | [decision_log.md:192](/Users/edr/code/JouleWise-wt-status/docs/decision_log.md:192), [REFUTER-ROUND-1-DISPOSITION.md:10](/Users/edr/code/JouleWise-wt-status/docs/process_traces/2026-08-30-t28-v5-prep/REFUTER-ROUND-1-DISPOSITION.md:10), [test_d117_contrast_v5_pack.py:518](/Users/edr/code/JouleWise-wt-status/tests/test_d117_contrast_v5_pack.py:518) | Carried with the two controls distinguished precisely |
| Dominance requires timing-aware floor ÷ naive floor ≥ 2 per component and cell | [README.md:27](/Users/edr/code/JouleWise-wt-status/README.md:27), [decision_log.md:10375](/Users/edr/code/JouleWise-wt-status/docs/decision_log.md:10375) | Carried |
| Missing, unauthenticated, or zero-denominator close-out inputs select neither wording | [06b-RULING-d165-artifact-ownership.md:29](/Users/edr/code/JouleWise-wt-status/docs/process_traces/2026-09-01-fresh-model-review/06b-RULING-d165-artifact-ownership.md:29) | Carried |
| Four-rung probe, at least five small-model runs per rung, large model non-gating, checked shortest-rung selection | [state_kernel.json:4590](/Users/edr/code/JouleWise-wt-status/docs/process/state_kernel.json:4590), [v5-artifact-flow.md:7](/Users/edr/code/JouleWise-wt-status/docs/process/v5-artifact-flow.md:7) | Carried |
| Probe evening → desk pin/generation/clone proof → real-pack shakedown/transaction → collection/fill | [README.md:59](/Users/edr/code/JouleWise-wt-status/README.md:59), [state_kernel.json:4581](/Users/edr/code/JouleWise-wt-status/docs/process/state_kernel.json:4581), [state_kernel.json:4717](/Users/edr/code/JouleWise-wt-status/docs/process/state_kernel.json:4717) | Carried using repository order; supplied clone-proof placement flagged |
| Fresh review used reviewers from three model families and launched paper/dependence follow-ups | [00-MAGISTRATE-SYNTHESIS.md:3](/Users/edr/code/JouleWise-wt-status/docs/process_traces/2026-09-01-fresh-model-review/00-MAGISTRATE-SYNTHESIS.md:3), [00-MAGISTRATE-SYNTHESIS.md:72](/Users/edr/code/JouleWise-wt-status/docs/process_traces/2026-09-01-fresh-model-review/00-MAGISTRATE-SYNTHESIS.md:72) | Carried as in-flight branch work, not landed |
| Transfer marker remains necessary for unconditional wording | [00-MAGISTRATE-SYNTHESIS.md:48](/Users/edr/code/JouleWise-wt-status/docs/process_traces/2026-09-01-fresh-model-review/00-MAGISTRATE-SYNTHESIS.md:48) | Carried |
| Instrument is attribution-limited at about 1 J | [decision_log.md:4713](/Users/edr/code/JouleWise-wt-status/docs/decision_log.md:4713) | Carried |
| Pre-repair energy is void and retained bundles are immutable | [README.md:74](/Users/edr/code/JouleWise-wt-status/README.md:74), [README.md:138](/Users/edr/code/JouleWise-wt-status/README.md:138), [README.md:240](/Users/edr/code/JouleWise-wt-status/README.md:240) | Carried |
| Requested artifact-flow path | [v5-artifact-flow.md:1](/Users/edr/code/JouleWise-wt-status/docs/process/v5-artifact-flow.md:1) | Flagged: source exists at a different landed path |
| D-165-prefixed state rows | [06b-RULING-d165-artifact-ownership.md:45](/Users/edr/code/JouleWise-wt-status/docs/process_traces/2026-09-01-fresh-model-review/06b-RULING-d165-artifact-ownership.md:45) | Flagged: none currently exist; follow-up registration is owed |

## Sections

| section | action taken |
|---|---|
| Current Repository View | Replaced stale July/August campaign status with the 2026-09-01 Qwen3 state and next machine gate |
| Voided sections | Reduced each to what was voided, the physical timing defect, and the repaired replacement |
| Update Ledger | Collapsed all five Previous Update sections and the older ledger into one dated, one-line table |
| Summary and advisor map | Re-centered the capstone on the governed instrument and updated artifact readiness |
| Status At A Glance | Reconciled Phases 2 and 4 to the `_v5` probe, collection, close-out, and fill chain |
| Architecture | Preserved the controller/adapter/bundle design while expanding terms at first use |
| Methodology | Preserved reporting and uncertainty rules; added the two-times dominance mechanism and close-out authority |
| Experiment Plan | Replaced stale baseline planning with the probe-to-results operator chain |
| Timeline | Removed promised dates and made dependencies the schedule |
| Risks and deliverables | Added prompt refusal, dependence, transfer-marker, and close-out risks; updated completion artifacts |
| Repository and process maps | Pointed to the landed flow map and distinguished active branches from landed work |

## Verification notes

```text
$ python3 -m unittest tests.test_paper_terms_lint tests.test_gen_state
...........................................
----------------------------------------------------------------------
Ran 43 tests in 1.996s

OK
```

```text
$ git diff --check
(no output; exit 0)
```

```text
$ git diff --stat
 PROJECT_STATUS.md | 1409 +++++++++++++++++++----------------------------------
 1 file changed, 499 insertions(+), 910 deletions(-)
```

The repository-pointer inspection also passed with:

```text
all PROJECT_STATUS repository pointers resolve
```

## Unresolved

- `docs/paper/round7/v5-artifact-flow-map.md` is absent. The rewrite uses the landed equivalent, `docs/process/v5-artifact-flow.md`.
- The supplied description places throwaway-clone re-proof on transaction night; both README and the live state kernel place it on the desk day before the real-pack shakedown. The rewrite follows those authorities.
- No `D165-` rows exist in the current state kernel. The close-out ruling explicitly assigns their registration to a follow-up, so the document labels the close-out implementation as branch-only/in-flight.

## Residual risk

Several post-collection producers remain active branches or ruled follow-ups rather than landed code. The rewrite identifies those gaps and does not present them as completed evidence.