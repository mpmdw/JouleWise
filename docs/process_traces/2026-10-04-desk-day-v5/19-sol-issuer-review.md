```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "REVIEW: FAIL — reproduced weak harvest provenance and rejection of a permitted SELECT with an excluded large-model member.",
  "workspace": {
    "base_requested": "8fa002f7",
    "base_mode": "descendant",
    "head_start": "a112600925b36beb41d3c55bae06342e10330921",
    "head_end": "a112600925b36beb41d3c55bae06342e10330921",
    "upstream_end": "8fa002f77db7af1e261a30e3787e38af2ab5e946",
    "branch": null
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "line": "REVIEW: FAIL",
    "findings": [
      {
        "id": "F1",
        "severity": "should_fix",
        "display_severity": "MAJOR",
        "file": "scripts/issue_g2a_prefill_prompt_pin.py",
        "line": 214,
        "summary": "Block-3 provenance rests on editable declarations; relabeled block-2 RECOVER archives issue an end-state pin despite their unchanged block-2 frozen plans and mismatching archive checksums."
      },
      {
        "id": "F2",
        "severity": "should_fix",
        "display_severity": "MAJOR",
        "file": "scripts/issue_g2a_prefill_prompt_pin.py",
        "line": 693,
        "summary": "The new validity-filtered harvest inputs reach validators that require a large-model member and the complete inventory roster, rejecting a permitted SELECT."
      }
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "suite",
      "cmd": "TMPDIR=/tmp/dd5-isreview PYTHONDONTWRITEBYTECODE=1 /Users/edr/code/JouleWise/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_issue_g2a_prefill_prompt_pin.py tests/test_summarize_g2a_prefill_probe.py tests/test_select_g2a_prefill_length.py tests/test_d117_contrast_v5_pack.py",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["93 passed, 189 subtests passed in 75.73s (0:01:15)"]
      },
      "expected": {"exit_code": 0, "tail_regex": "93 passed, 189 subtests passed"}
    },
    {
      "id": "V2",
      "kind": "suite",
      "cmd": "TMPDIR=/tmp/dd5-isreview PYTHONDONTWRITEBYTECODE=1 /Users/edr/code/JouleWise/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_generate_g2a_probe_inputs.py tests/test_d117_floor_qwen3_v5_generate.py",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["43 passed, 36 subtests passed in 77.28s (0:01:17)"]
      },
      "expected": {"exit_code": 0, "tail_regex": "43 passed, 36 subtests passed"}
    },
    {
      "id": "V3",
      "kind": "smoke",
      "cmd": "TMPDIR=/tmp/dd5-isreview PYTHONDONTWRITEBYTECODE=1 HF_HOME=/tmp/dd5-isreview/hf HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 /Users/edr/code/JouleWise/.venv/bin/python -B /tmp/dd5-isreview/verify_findings.py real_select",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["PASS: guarded real SELECT issue; exit=0; no live path opened"]
      },
      "expected": {"exit_code": 0, "tail_regex": "PASS: guarded real SELECT issue; exit=0; no live path opened"}
    },
    {
      "id": "V4",
      "kind": "test",
      "cmd": "TMPDIR=/tmp/dd5-isreview PYTHONDONTWRITEBYTECODE=1 HF_HOME=/tmp/dd5-isreview/hf HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 /Users/edr/code/JouleWise/.venv/bin/python -B /tmp/dd5-isreview/verify_findings.py relabeled_block2",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": ["AssertionError: block-2 records relabeled block 3 must refuse"]
      },
      "expected": {"exit_code": 0, "tail_regex": ""}
    },
    {
      "id": "V5",
      "kind": "test",
      "cmd": "TMPDIR=/tmp/dd5-isreview PYTHONDONTWRITEBYTECODE=1 HF_HOME=/tmp/dd5-isreview/hf HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 /Users/edr/code/JouleWise/.venv/bin/python -B /tmp/dd5-isreview/verify_findings.py reconstructed_select",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": ["AssertionError: selection newly constructed over a RECOVER archive must refuse"]
      },
      "expected": {"exit_code": 0, "tail_regex": ""}
    },
    {
      "id": "V6",
      "kind": "test",
      "cmd": "TMPDIR=/tmp/dd5-isreview PYTHONDONTWRITEBYTECODE=1 HF_HOME=/tmp/dd5-isreview/hf HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 /Users/edr/code/JouleWise/.venv/bin/python -B /tmp/dd5-isreview/verify_findings.py excluded_large",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": ["AssertionError: valid-member SELECT must issue; observed exit=2"]
      },
      "expected": {"exit_code": 0, "tail_regex": ""}
    }
  ],
  "flags": [
    {
      "id": "R1",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "Successful end-state cases used scratch mutations of supplied archives; no genuine completed end-state archive was supplied.",
      "needs": ""
    }
  ]
}
```

## Findings

REVIEW: FAIL

**F1 — MAJOR: block-3 proof establishes internal consistency, without establishing producer provenance.** [scripts/issue_g2a_prefill_prompt_pin.py:214](/Users/edr/code/JouleWise-wt-dd5-isreview/scripts/issue_g2a_prefill_prompt_pin.py:214), also lines 199–237 and 679–691.

The proof uses the inventory’s policy path/hash, the plan’s `b3w1`/`b3w2` suffix, and the chain’s POLICY literal/hash sidecar. Coordinated scratch rewrites of those fields let both real **block-2** RECOVER archives issue an end-state pin accepted by the v5 loader. Their frozen calibration plans still name the block-2 policy, and four files per archive disagree with the preserved `SHA256SUMS`.

Additional accepted counterexamples:

- A newly constructed selection over the real block-3 RECOVER archive, after rewriting verdict, causes, and selection/output bindings.
- A one-byte whitespace edit to selection.json after updating both declared hashes.
- The real NULL archive rewritten as RECOVER with `capture_made=true` and five failed anchors, despite **zero capture files**.

Thus an unproduced selection can yield a pin. The proof is weaker than the harvester’s own source-copy and policy-byte authentication ([harvest_g2a_window.py:78](/Users/edr/code/JouleWise-wt-dd5-isreview/scripts/harvest_g2a_window.py:78), lines 137–143). V4/V5 reproduce the failures. These require coordinated metadata mutations; unchanged block-2 archives refuse.

**F2 — MAJOR: the new harvest path rejects permitted validity-filtered SELECT inputs.** [scripts/issue_g2a_prefill_prompt_pin.py:693](/Users/edr/code/JouleWise-wt-dd5-isreview/scripts/issue_g2a_prefill_prompt_pin.py:693), with rejection sites at lines 372 and 643.

Excluding one invalid, non-gating large-model member produces `large_members=0` and removes that member from the derived receipt. The actual summarizer reproduced both mutated outputs exactly. Issuance refused with `summary_large_members_invalid`; directly checking the receipt also refused with `counts_receipt_selected_rung_run_set_mismatch`.

Registration [§7:247](/Users/edr/code/JouleWise-wt-dd5-isreview/configs/campaigns/g2a_prefill_probe_25g83/registration_block3.md:247) gates SELECT on the small-model rungs; §8 lines 300–306 requires valid-member regeneration. These validators still expect the complete roster. V6 reproduces both rejection sites.

The other requested counterexamples behaved as follows:

| Counterexample | Exit | Refusal |
|---|---:|---|
| One-byte semantic selection edit | 2 | `harvest_selection_sha256_mismatch` |
| Update `selection.sha256` only | 2 | `harvest_output_sha256_mismatch` |
| Update both hashes | 2 | `selection_record_does_not_match_summary_and_rule` |
| RECOVER / NULL verdict | 2 | `harvest_verdict_not_select` |
| Block-2 policy, after satisfying verdict prerequisite | 2 | `harvest_block3_binding_mismatch` |
| `archive_root` elsewhere | 2 | `harvest_archive_root_mismatch` |
| Wrong plan hash | 2 | `harvest_plan_sha256_mismatch` |
| Wrong registration bytes | 2 | `registration_sha256_mismatch` |

The guarded real SELECT issue returned **0**, with no open attempts under either live root:

- Pin sha256: `d1209f6d5998e4a48ac0dae7ed04a8f6a2c5ec9950d768f0df9ef8839a32dccb`
- G2-a record sha256: `c694c4884ff7f31b677b5ade1ab9710a4797c4529eaad61fba85fea080a88222`

On internally consistent records, the §7 arithmetic matches [registration lines 277–280](/Users/edr/code/JouleWise-wt-dd5-isreview/configs/campaigns/g2a_prefill_probe_25g83/registration_block3.md:277): minimum five recorded anchors, exclude `not recorded`, and strictly more than half non-`bounded`. One all-bounded RECOVER refused; two captured RECOVERs and one systematic RECOVER issued **4096** and loaded successfully. `capture_made=false` refused. Both end-state records had the closed authority keys and no refusal or “no rung” wording; the static declaration remained intact.

Required tests: **93 passed, 189 subtests**. Additional importer modules: **43 passed, 36 subtests**. Worktree unchanged and clean at `a1126009`. Lead disposition of F1/F2 is the next step before merge.

## Residual risk

End-state successes were synthetic archive-copy cases, not live hardware validation. Scratch evidence and replay scripts are under [/tmp/dd5-isreview](/tmp/dd5-isreview/).