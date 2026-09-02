```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "findings",
  "completion": "complete",
  "summary": "Created the executable identity-pin projection receipt contract with full derivation, lifecycle, schema, example, diagram, and test mapping.",
  "workspace": {
    "base_requested": "a37b0b9f",
    "base_mode": "exact",
    "head_start": "a37b0b9f72928e345739c8ef88a28b4198dd1133",
    "head_end": "a37b0b9f72928e345739c8ef88a28b4198dd1133",
    "upstream_end": "a37b0b9f72928e345739c8ef88a28b4198dd1133",
    "branch": null
  },
  "pathspec": [
    "docs/contracts/identity_pin_projection.md"
  ],
  "unowned_dirty": [],
  "verdict": {
    "implementation": "implemented",
    "acceptance": "ready"
  },
  "verification": [
    {
      "id": "V1",
      "kind": "other",
      "cmd": "TMPDIR=/private/tmp/claude-501/-Users-edr-code-JouleWise/540125d5-d8ee-49d1-8e6e-17050e77212d/scratchpad/ /Users/edr/code/JouleWise/.venv/bin/python -c 'import hashlib,json; domain=\"joulewise.prompt_token_ids.v1\"; h=lambda ids: hashlib.sha256((domain+\"\\0\"+json.dumps(ids,separators=(\",\",\":\"),sort_keys=True)).encode()).hexdigest(); assert h([11,22,33,44])==\"10e6c1854858d7cdd278400c11706ebd2a43fe79ffa241bd5c1d0f6fe665a9fe\"; assert h([11,22,33,45])==\"62a91911d641748e89ca36775d31747c0e83ce6ea0e9ba6c794b52ef65933b35\"; assert hashlib.sha256(b\"TOY\\n\").hexdigest()==\"6361d8e661d28948e82e68ed04a7d5becdc39bc6a94176bd805003b90991fdfb\"; print(\"worked hashes OK\")'",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "worked hashes OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "worked hashes OK"
      }
    },
    {
      "id": "V2",
      "kind": "other",
      "cmd": "TMPDIR=/private/tmp/claude-501/-Users-edr-code-JouleWise/540125d5-d8ee-49d1-8e6e-17050e77212d/scratchpad/ /Users/edr/code/JouleWise/.venv/bin/python -c 'from pathlib import Path; import hashlib; lines=Path(\"docs/contracts/identity_pin_projection.md\").read_text(encoding=\"utf-8\").splitlines(); values=[x for x in lines if x.startswith(\"[{\\\"config_inventory\\\"\")]; assert len(values)==1; actual=hashlib.sha256(values[0].encode()).hexdigest(); assert actual==\"6d3a16628cdda16cfd1b0bc3fba680b600e5e25e15f606986aa9ed92967fd1cd\"; print(\"projection input hash OK\", actual)'",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "projection input hash OK 6d3a16628cdda16cfd1b0bc3fba680b600e5e25e15f606986aa9ed92967fd1cd"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "projection input hash OK 6d3a1662"
      }
    },
    {
      "id": "V3",
      "kind": "inspection",
      "cmd": "git status --short --branch",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "## HEAD (no branch)",
          "?? docs/contracts/identity_pin_projection.md"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "\\?\\? docs/contracts/identity_pin_projection.md"
      }
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "baseline_drift",
      "level": "nonblocking",
      "text": "D-131 clause 2 specifies fixed alpha/beta/gamma identity-unit rosters, but the generic code validates only nonempty unique IDs and preserves pack order; the contract records executable behavior explicitly.",
      "needs": "Keep the pack-specific roster cure separate from this contract-only scope."
    },
    {
      "id": "F2",
      "kind": "environment",
      "level": "nonblocking",
      "text": "The prompt-named 141a ruling file is absent from checkout a37b0b9f; its committed Git object at 4141ff47 was inspected read-only.",
      "needs": ""
    },
    {
      "id": "F3",
      "kind": "residual_risk",
      "level": "nonblocking",
      "text": "Launch authenticates and replays the arm receipt but does not re-derive prompt realization; the contract names V5-LAUNCH-REALIZATION-RECHECK-01 and the later bundle-reader catch.",
      "needs": "Track the named follow-up independently."
    }
  ]
}
```

## Change

Created [identity_pin_projection.md](/Users/edr/code/JouleWise-wt-proj02-c/docs/contracts/identity_pin_projection.md:1), the ONE home for this receipt.

| Section | Lines |
|---|---:|
| Purpose and forcing problem | 7–25 |
| Vocabulary | 26–90 |
| Projection input and exclusions | 91–187 |
| Prompt realization | 188–225 |
| Freeze, arm, and launch lifecycle | 226–312 |
| Receipt schema and refusal codes | 313–378 |
| Worked two-config example | 379–463 |
| Named timeline diagram | 464–500 |
| Clause-to-test map | 501–523 |

Code contradicted one decision-log sentence: D-131’s fixed alpha/beta/gamma roster is not enforced by the generic validator. P-1–P-10 and the `transformers_version` exclusion otherwise match the checked-out implementation.

Glossed terms include projection, identity pin/unit, freeze, arm, re-derive, replay, drift, dirty, unreadable, custody, realization, expectation-bearing configuration, canonical JSON, shared-mint projection, receipt, sidecar, and idempotence.

## Verification notes

No tests were run, as requested. The worked token, drift, model-byte, and complete canonical projection-input SHA-256 values were independently recomputed with the specified virtualenv. Workspace inspection confirms only the authorized file was created.

## Residual risk

The documented arm-to-launch realization interval remains open under `V5-LAUNCH-REALIZATION-RECHECK-01`; current bundle validation catches it only after physical work.