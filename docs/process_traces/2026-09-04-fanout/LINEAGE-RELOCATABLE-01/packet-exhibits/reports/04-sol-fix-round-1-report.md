```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "clean",
  "completion": "complete",
  "summary": "Implemented the ruled non-authoritative post-hoc relocation carrier, proved a deleted-source lineage end to end, and pinned all six named refusal legs without adding a reason code.",
  "workspace": {
    "base_requested": "ec4b76e22bd3673958e557d85a7eeefdf31f09b5",
    "base_mode": "descendant",
    "head_start": "64df15d8cee8097791b8a690faafc6a572918205",
    "head_end": "64df15d8cee8097791b8a690faafc6a572918205",
    "upstream_end": "64df15d8cee8097791b8a690faafc6a572918205",
    "branch": "feat/2026-09-04-fan-LINEAGE-RELOCATABLE-01"
  },
  "pathspec": [
    "joulewise/arm_readiness.py",
    "scripts/launch_window.py",
    "tests/test_arm_readiness.py",
    "tests/test_launch_window.py",
    "docs/process_traces/2026-09-04-fanout/LINEAGE-RELOCATABLE-01/04-sol-fix-round-1-report.md"
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
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_arm_readiness",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Ran 56 tests in 12.262s",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 56 tests in [0-9.]+s[\\s\\S]*OK"
      }
    },
    {
      "id": "V2",
      "kind": "suite",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_arm_readiness tests.test_arm_readiness_lifecycle tests.test_arm_readiness_schemas tests.test_arm_readiness_evidence tests.test_launch_window tests.test_analysis_inputs",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Ran 214 tests in 287.145s",
          "OK (skipped=4)"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 214 tests in [0-9.]+s[\\s\\S]*OK \\(skipped=4\\)"
      }
    },
    {
      "id": "V3",
      "kind": "lint",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -m py_compile joulewise/arm_readiness.py scripts/launch_window.py tests/test_arm_readiness.py tests/test_launch_window.py && git diff --check",
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
      "id": "V4",
      "kind": "inspection",
      "cmd": "python3 - <<'PY'\nimport json\nfrom pathlib import Path\np=Path('docs/process_traces/2026-09-04-fanout/LINEAGE-RELOCATABLE-01/04-sol-fix-round-1-report.md')\ns=p.read_text(encoding='utf-8')\nassert s.startswith('```json\\n')\ne=s.index('\\n```', 8)\nraw=s[8:e]\nv=json.loads(raw)\nassert len(raw.encode('utf-8')) <= 8192\nassert v['schema']=='claude-codex-report/v1'\nassert v['genre']=='implementation'\nprint(f\"report envelope: {v['status']} {v['completion']}\")\nPY",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "report envelope: clean complete"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "^report envelope: clean complete$"
      }
    },
    {
      "id": "V5",
      "kind": "inspection",
      "cmd": "git status --short && git rev-parse HEAD && git rev-parse @{upstream}",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          " M joulewise/arm_readiness.py",
          " M scripts/launch_window.py",
          " M tests/test_arm_readiness.py",
          " M tests/test_launch_window.py",
          "?? docs/process_traces/2026-09-04-fanout/LINEAGE-RELOCATABLE-01/04-sol-fix-round-1-report.md",
          "64df15d8cee8097791b8a690faafc6a572918205",
          "64df15d8cee8097791b8a690faafc6a572918205"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "joulewise/arm_readiness\\.py[\\s\\S]*04-sol-fix-round-1-report\\.md[\\s\\S]*64df15d8cee8097791b8a690faafc6a572918205[\\s\\S]*64df15d8cee8097791b8a690faafc6a572918205$"
      }
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "residual_risk",
      "level": "nonblocking",
      "text": "The ruling requires an independent cold gate before merge; this implementation-seat proof packet is ready for that lead-owned gate.",
      "needs": "Lead reruns the cold gate and final diff review before merge."
    },
    {
      "id": "F2",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "An extra 32-module reverse-import attempt was interrupted at the unrelated subprocess-heavy receipt-histsem refresh test after extended silence; the mandated six touched/importing modules then passed completely.",
      "needs": ""
    }
  ]
}
```

## Change

The adopted ruling at
`docs/process_traces/2026-09-04-fanout/01-magistrate-rulings.md:33`
is installed as a canonical exact-key carrier whose four target directories
are relative to the carrier. The carrier is read once into a frozen context,
cannot name absolute/traversing/symlink targets, and is bound to the immutable
source locator digest. It selects read locations only: original reference
objects remain unchanged for every digest and predecessor comparison.

Post-hoc callers must pass `relocation_carrier` explicitly. Bundle admission
then reads only fixed custody, window-plan, lifecycle, and committed-pack
locations. The live campaign authenticator and both launcher modes explicitly
refuse that argument with the existing `launch_binding_mismatch` code.

### Finding → cure → file:line map

| Finding | Cure | Production / biting regression |
|---|---|---|
| LR-01 blocker: authority absent | The adopted magistrate row at `01-magistrate-rulings.md:33` now supplies NR-1..NR-3 authority. | Carrier implementation `joulewise/arm_readiness.py:9171`; moved-source regression `tests/test_arm_readiness.py:1806`. |
| NR-1 non-authoritative carrier | Exact schema, frozen resolved context, source-locator digest, relative-only targets; issued lineage bytes are never rewritten. | `joulewise/arm_readiness.py:95`, `:727-751`, `:9171-9256`, `:10957-11047`; `tests/test_arm_readiness.py:1806`, `:1902`. |
| NR-2 post-hoc only | Relocation is opt-in at bundle/direct authentication; current-boot/campaign/launcher paths reject it. | `joulewise/arm_readiness.py:10279-10307`, `:10843-10855`; `scripts/launch_window.py:61`, `:244-250`, `:280-286`; `tests/test_arm_readiness.py:1822`; `tests/test_launch_window.py:82`. |
| NR-3 same-byte/same-pack | Target reads retain source digests, predecessor objects, fixed namespaces, committed-tree digest, and repository-relative pack location. | `joulewise/arm_readiness.py:9485-9618`, `:10329-10671`; `tests/test_arm_readiness.py:1806-1820`, `:1833-1906`. |
| Named tamper / committed-pack-change / repository-relative-move | Exact copied bytes, committed pack tree, and relative pack suffix remain binding. | `tests/test_arm_readiness.py:1833`, `:1838`, `:1854`. |
| Named swapped-chain / traversal / symbolic-link | Fixed lifecycle filenames and existing predecessor/kind checks remain binding; carrier traversal and every reachable target symlink refuse. | `tests/test_arm_readiness.py:1874`, `:1890`, `:1902`. |

### Clause map

| Ruling proposition (`01-magistrate-rulings.md:33`) | Production site | Biting assertion | Counterfactual |
|---|---|---|---|
| “explicit NON-authoritative relocation carrier over immutable issued bytes” | `joulewise/arm_readiness.py:9171-9256` and `:10957-11047` | `test_moved_source_authenticates_only_with_explicit_carrier`, `tests/test_arm_readiness.py:1806` | Ignore the carrier dispatch or rewrite an issued reference: the deleted-source positive fails or lineage equality fails. |
| “only for post-hoc analysis when explicitly supplied” | `joulewise/arm_readiness.py:10279-10307` | `test_moved_source_authenticates_only_with_explicit_carrier`, `tests/test_arm_readiness.py:1806` | Make the carrier implicit: the no-carrier refusal assertion fails. |
| “live launch and campaign replay remain absolute-path and refuse relocation” | `joulewise/arm_readiness.py:10843-10855`; `scripts/launch_window.py:244-250`, `:280-286` | `test_live_campaign_replay_refuses_relocation_carrier`, `tests/test_arm_readiness.py:1822`; `test_live_launcher_refuses_post_hoc_relocation_carrier_option`, `tests/test_launch_window.py:82` | Thread the carrier into either live path: its `launch_binding_mismatch` assertion fails. |
| “preserve every existing artifact-specific refusal code” | `joulewise/arm_readiness.py:9122-9126`, `:9485-9618`, `:10329-10671` | Six named refusal methods at `tests/test_arm_readiness.py:1833-1906` | Add a relocation reason or translate legacy failures: the exact-code assertions fail. |
| “same-byte/same-pack relocation” | `joulewise/arm_readiness.py:9012-9055`, `:9485-9618` | `test_moved_source_authenticates_only_with_explicit_carrier`, tamper, committed-pack-change, and repository-relative-move at `tests/test_arm_readiness.py:1806-1872` | Skip a digest or pack-location comparison: its corresponding negative assertion fails. |
| “proof goes before a cold gate before the landing merges” | `NOT PINNED: process gate, not production bytes; proof packet below.` | Report V1/V2 and the six-leg table below | Merge without the independent rerun: the lead-owned merge gate remains unsatisfied. |

### NR-3 cold-gate proof packet

The positive fixture issues a real consumption → start → settle chain, clones
the committed checkout and custody/window/run inputs, deletes the original
repository, custody tree, and arm-context roots, first proves the unchanged
absolute path refuses, then proves the explicit carrier accepts. It asserts
the returned lineage equals the issued lineage object, the consumption digest
equals its issued reference, and the returned pack digest equals a fresh
committed-tree digest of the clone. Removing the relocation dispatch makes the
second half repeat the first refusal, so the positive regression is biting.

| Named leg | Counterfactual input | Preserved code |
|---|---|---|
| tamper | Append one byte-bearing line to copied `window.env`. | `launch_binding_mismatch` |
| committed-pack-change | Commit different `calibration_plan.json` bytes in the selected clone. | `launch_binding_mismatch` |
| repository-relative-move | `git mv` the same pack to a different repository suffix and point the carrier there. | `launch_binding_mismatch` |
| swapped-chain | Swap copied start/settle primaries and regenerate only their filename sidecars. | `launch_consumption_invalid` |
| traversal | Set `custody_pack_root` to `../custody`. | `launch_binding_mismatch` |
| symbolic-link | Replace the selected window-plan target with a directory symlink. | `launch_binding_mismatch` |

No magistrate-owned state file was changed. No state-row mutation is needed to
cure the implementation; after the independent cold gate, the magistrate can
retire A126 under the kernel's house convention.

## Verification notes

The required focused gate is V2. No repository-wide discovery ran. An extra
reverse-import experiment named 32 direct importers and made broad clean
progress, but was interrupted at
`tests.test_receipt_histsem.ReceiptHistsemTests.test_refresh_lane_whole_candidate_requires_every_stale_row`,
an unrelated long-running subprocess test; this was not treated as evidence.

## Residual risk

Per NR-3, merge remains gated on the lead's independent cold review and replay
of this proof packet. No hardware or quiet-machine gate is involved.
