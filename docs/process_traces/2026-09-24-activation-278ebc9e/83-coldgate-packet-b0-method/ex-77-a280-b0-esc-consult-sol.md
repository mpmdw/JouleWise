```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "B0 needs a differential idle-parity gate and a single authenticated dispatch boundary before another fix round.",
  "workspace": {
    "base_requested": "2ea6a7ec",
    "base_mode": "descendant",
    "head_start": "bee658c5acc4dd860a382317c40ec4421587a13a",
    "head_end": "bee658c5acc4dd860a382317c40ec4421587a13a",
    "upstream_end": null,
    "branch": null
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "findings": [
      {
        "id": "F1",
        "severity": "blocker",
        "location": "joulewise/evidence_night.py:249,689; scripts/run_night.py:1009,1390",
        "text": "New kind checks and a second receipt read change the order and outcome of established idle refusals and cleanup."
      },
      {
        "id": "F2",
        "severity": "blocker",
        "location": "scripts/run_night.py:1019-1027",
        "text": "_custody_row accepts an unbound wrapper as dispatch authority when no validated C5 receipt exists."
      },
      {
        "id": "F3",
        "severity": "should_fix",
        "location": "joulewise/evidence_night.py:639",
        "text": "A list-valued preparation kind raises TypeError before the historical typed refusal."
      }
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "inspection",
      "cmd": "git rev-parse HEAD 2ea6a7ec",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "bee658c5acc4dd860a382317c40ec4421587a13a",
          "2ea6a7ec3d199908ad85d79e0f6a2a511bb25b4b"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "2ea6a7ec3d199908ad85d79e0f6a2a511bb25b4b"
      }
    },
    {
      "id": "V2",
      "kind": "smoke",
      "cmd": "python3 -B - <<'PY'\nfrom pathlib import Path\nfrom types import SimpleNamespace\nfrom unittest.mock import patch\nfrom joulewise import evidence_night\nfrom scripts import run_night\nwith patch.object(evidence_night, 'safe_path', side_effect=lambda value: value), patch.object(evidence_night, 'read_state', return_value={'kind': []}):\n    try:\n        evidence_night.candidate_state(Path('/tmp/278ebc9e/b0esc-sol/candidate'))\n    except Exception as exc:\n        print('malformed_kind:', type(exc).__name__, str(exc))\nwrapper = 'export NIGHT_PAYLOAD_KIND=quiet_predicate_evidence\\n'\ndef read_text(path, *args, **kwargs):\n    if path.name == 'receipt.json':\n        raise FileNotFoundError\n    return wrapper\nplan = SimpleNamespace(custody_root='/tmp/278ebc9e/b0esc-sol/custody', chain_path='/tmp/278ebc9e/b0esc-sol/bare_wrapper', plan_id='test')\nwith patch.object(Path, 'read_text', read_text):\n    print('bare_wrapper_row:', run_night._custody_row(plan).kind)\nPY",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "malformed_kind: TypeError cannot use 'list' as a dict key (unhashable type: 'list')",
          "bare_wrapper_row: quiet_predicate_evidence"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "bare_wrapper_row: quiet_predicate_evidence"
      }
    },
    {
      "id": "V3",
      "kind": "smoke",
      "cmd": "python3 -B - <<'PY'\nimport json\nfor label, raw in [('utf8_bom', b'\\xef\\xbb\\xbf{\"plan_id\":\"p\"}'), ('utf16', '{\"plan_id\":\"p\"}'.encode('utf-16'))]:\n    print(label, 'bytes_json=', json.loads(raw), end='; ')\n    try:\n        print('utf8_text_json=', json.loads(raw.decode('utf-8')))\n    except Exception as exc:\n        print('utf8_text_json=', type(exc).__name__)\nPY",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "utf8_bom bytes_json= {'plan_id': 'p'}; utf8_text_json= JSONDecodeError",
          "utf16 bytes_json= {'plan_id': 'p'}; utf8_text_json= UnicodeDecodeError"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "utf16 bytes_json=.*UnicodeDecodeError"
      }
    }
  ],
  "flags": [
    {
      "id": "R1",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "This structural consult did not rerun the 603-test module suite or the full discovery suite.",
      "needs": "Run both on the final implementation head after the parity harness passes."
    }
  ]
}
```

## Sol 6.0 — Findings

**F1 — blocker.** The root cause is a validation-order change repeated across surfaces. The base sealer checked sealed bytes, clone state and plan through its established path; head selects a kind at [evidence_night.py:249](/Users/edr/code/wt-278ebc9e-b0esc-sol/joulewise/evidence_night.py:249) and checks wrapper/source binding at [evidence_night.py:689](/Users/edr/code/wt-278ebc9e-b0esc-sol/joulewise/evidence_night.py:689). Thus a malformed wrapper or moved source can receive a new kind or binding refusal before the base’s refusal. Cleanup validates a receipt from bytes at [run_night.py:1379](/Users/edr/code/wt-278ebc9e-b0esc-sol/scripts/run_night.py:1379), then `_custody_row` rereads it as text at [run_night.py:1009](/Users/edr/code/wt-278ebc9e-b0esc-sol/scripts/run_night.py:1009). V3 demonstrates why BOM and UTF-16 receipts can pass the first parse and fail the second. The 72b audit executed the resulting base/head cleanup and sealing counterexamples.

Each fix round preserved its **named inputs** because the tests pinned particular states, not the partitions formed by wrapper encoding, sidecar state, receipt encoding, source state and entry point together. A lens can find counterexamples and review validation order. Neither a lens nor a finite corpus proves byte identity for *every* possible input. A generated corpus makes parity an executable, bounded acceptance condition; structural sequencing and authority review address the states it cannot enumerate.

**F2 — blocker.** `_custody_row` returns the row parsed from wrapper text at [run_night.py:1019–1027](/Users/edr/code/wt-278ebc9e-b0esc-sol/scripts/run_night.py:1019) even without a sidecar, source binding or validated C5. V2 reproduced idle selection from such a bare wrapper. A declaration in a file is not, by itself, the authenticated identity required by brief 10.

**F3 — should_fix.** [evidence_night.py:639](/Users/edr/code/wt-278ebc9e-b0esc-sol/joulewise/evidence_night.py:639) looks up `state.get("kind")` before checking its type. V2 reproduced `TypeError` for `[]`, where the base’s candidate check gives the owned-preparation refusal.

| Structural cure | Cost | What it guarantees |
|---|---|---|
| **(a) Differential parity harness** against exact `2ea6a7ec` and head | Medium to high fixture work; cheap repeat runs | Exact equality for every generated idle case, including ordered calls and written bytes. It does **not** prove equality outside the corpus. Make it B0’s acceptance test. |
| **(b) Validate as base, then route** | Medium refactor | Preserves base handling of malformed idle inputs if no kind lookup or new side effect runs before the base outcome. Select a non-idle row only from an authenticated result after shared validation. Keep reporting independent of kind. Review the sequencing at every entry point. |
| **(c) Per-surface PRs** for candidate/sealing, generation/notice, gate/installer/probe, and reporting/cleanup | More review and integration time | Localizes regressions. Each PR must pass the **entire accumulated** parity corpus, since surfaces share custody state. Splitting alone gives no parity guarantee. |
| **(d) Single authenticated dispatch result** | Medium design change | Have validated sealed-candidate or C5 code produce one immutable kind-and-binding result consumed by dispatch. No helper may reconstruct authority from plan hints or wrapper text. This narrows the authority audit; it still needs the harness. |

**Recommended next round, executable brief:**

> **Seat H — independent harness writer.** `WRITE_SCOPE: ["tests/test_night_kind_differential.py"]`. In isolated scratch under `/tmp/278ebc9e/b0esc-<seat>/`, run the same generated case and frozen clock/path/dependency responses against archive `2ea6a7ec` and `bee658c5`. Enumerate plan shape and kind types; valid, missing, malformed, wrong-class and changed plans; wrapper missing, non-UTF-8, BOM, ambiguous, unknown, declaration-stripped and intact; sidecar missing, malformed and mismatched; C5 missing, invalid, conflicting, UTF-8, UTF-8 BOM and UTF-16; clone/source intact, moved, absent and changed; and pre/post seal, notice, reporting, courier, cleanup, uninstall, veto and verify entry points. Include single faults and relevant pairs, especially wrapper × receipt × source. Compare return values, exception types/messages, refusal codes/texts, exit/stdout/stderr, ordered mocked calls/argv, and created/changed/deleted file paths **and bytes**. Record case IDs and seed. First prove base-versus-base passes and a deliberate refusal-text or dispatch mutation fails.
>
> **Seat I — B0 implementation, after H’s corpus is reviewed.** `WRITE_SCOPE: ["joulewise/night_kinds.py", "joulewise/evidence_night.py", "scripts/gen_evidence_night.py", "joulewise/night_gate.py", "joulewise/night_agent_install.py", "scripts/run_night.py", "joulewise/zero_capture_facts.py", "tests/test_night_kinds.py", "tests/test_evidence_night.py", "tests/test_gen_evidence_night.py", "tests/test_night_gate.py", "tests/test_night_agent_install.py", "tests/test_run_night.py", "tests/test_zero_capture_facts.py", "tests/test_kind_dispatch_literals.py"]`. Preserve H’s test unchanged. Apply base-first validation and the single authenticated dispatch result; retain the historical row-neutral reporting inventory. **Gate:** zero unexplained idle differences across the corpus, typed refusal for every unhandled row, no bare-wrapper or plan-hint authority, existing byte goldens and focused suite green, then the canonical discovery suite and final fresh review. If an idle difference appears necessary, return `NEEDS_RULING` with its case ID rather than accepting it.

## Residual risk

The corpus will cover specified input partitions and combinations, not all possible filesystem races or malformed bytes. The final reviewer should trace every kind source and validation order in code alongside the executable gate.