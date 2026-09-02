```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "findings",
  "completion": "complete",
  "summary": "Implemented the dictated round-7 typed-scalar fence, placement census, CLI regressions, and checklist disclosures within the three-file write scope.",
  "workspace": {
    "base_requested": "781c8d78",
    "base_mode": "exact",
    "head_start": "781c8d78c359ba41bb2b0940ef37592a4e99729f",
    "head_end": "781c8d78c359ba41bb2b0940ef37592a4e99729f",
    "upstream_end": "b36d1e8557c771600c78202d6050fdd3a2e8637e",
    "branch": "feat/2026-09-02-dx-registry"
  },
  "pathspec": [
    "scripts/check_paper_round7_artifacts.py",
    "tests/test_paper_round7_artifacts.py",
    "docs/paper/round7/fill-checklist.md"
  ],
  "unowned_dirty": [],
  "verdict": {
    "implementation": "implemented",
    "acceptance": "pending_verification"
  },
  "verification": [
    {
      "id": "V1",
      "kind": "suite",
      "cmd": "python3 -m unittest tests.test_paper_round7_artifacts.RegistryAndDigestTests tests.test_paper_round7_artifacts.RefusalTests tests.test_paper_round7_artifacts.TypedArtifactCliTests tests.test_paper_round7_artifacts.InvocationTests",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Ran 43 tests in 0.792s",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 4[0-9]+ tests.*\\n\\nOK"
      }
    },
    {
      "id": "V2",
      "kind": "smoke",
      "cmd": "python3 scripts/check_paper_round7_artifacts.py --literals-only; echo EXIT=$?",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "R7F PLACED 0/16",
          "R7F LITERALS-ONLY COMPARED 181 / MISMATCHES 0",
          "EXIT=0"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "R7F PLACED 0/16\\nR7F LITERALS-ONLY COMPARED 181 / MISMATCHES 0\\nEXIT=0"
      }
    },
    {
      "id": "V3",
      "kind": "lint",
      "cmd": "python3 -m py_compile scripts/check_paper_round7_artifacts.py tests/test_paper_round7_artifacts.py",
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
      "id": "V5",
      "kind": "suite",
      "cmd": "python3 -m py_compile scripts/check_paper_round7_artifacts.py tests/test_paper_round7_artifacts.py && python3 -m unittest tests.test_paper_round7_artifacts",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 130,
        "tail": [
          "36 pre-replay tests emitted passing dots",
          "retained replay was interrupted during the AQ producer",
          "KeyboardInterrupt"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 44 tests.*\\n\\nOK"
      }
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "The exact module command entered its corpus-gated retained replay because the corpus is present on this machine; it was interrupted during AQ production to preserve the magistrate-only replay gate. Outputs were TMPDIR-only and no repository or corpus file was written.",
      "needs": "Magistrate runs the exact 44-test module suite and full replay at the bench."
    }
  ]
}
```

## Change

The fence now loads JSON fractional tokens as `Decimal`, compares values only when their Python types match, and routes artifact scalars through the single `_typed` resolver. Gate booleans, figure pulse values, control failure IDs, schema text, count fields, and renderer numbers fail closed with source-qualified messages.

Figure tolerance arithmetic uses the sole `_geometry(Decimal) -> float` conversion. SVG attribute strings and `float("nan")` remain the only other float conversions.

Placement now derives the 16 non-identity IDs from the parsed registry, gates markers on the byte-pinned standing-sentence head, and prints `R7F PLACED n/16` immediately before either successful or mismatching `COMPARED` tail. Successful census comparisons remain represented by that separate line, preserving the established 181/184 comparison counts.

P3 uses `--literals-only`: that path still runs `digest_half → check_figure`, so it exercises figure refusal without entering replay. P4 changes DX-015’s JSON token from `4.0` to `4`; `_typed` maps it to `Decimal(4)` and the unchanged rendered string `4.0 ms` passes.

The strict-comparison call-site audit found no legitimate cross-type equivalences requiring normalization. Existing pin, size, schema, Boolean, count, and rendered-literal comparisons are already like-for-like; missing/refused branches intentionally differ.

### Mutation check

- M1 — KILLED by `test_comparison_requires_identical_python_types` and the bool/int assertion in the P2 CLI test.
- M2 — KILLED by `test_decimal_loader_preserves_fixed_literal_across_float_roundtrip_edge`; exact Decimal rendering gives `1.000001`, while float/repr round-trip gives `1.000002`.
- M3 — KILLED by the resolver table and P1’s DX-026 string-number fixture.
- M4 — KILLED by P3’s `figure onset mark 0` string fixture.
- M5 — KILLED by `test_renamed_out_flag_in_pinned_command_is_refused`.
- M6 — KILLED by the current-skeleton `0/0` placement test; removing the standing gate produces 16 missing-placement mismatches.
- M7 — KILLED by the registry-substring test for `DX_STANDING_SENTENCE_HEAD`.

### Same-signature closure

This is rule-11’s second round on “scalar reads coerce instead of refuse.” A third round is structurally precluded by Decimal-at-load, the one `_typed` resolver, strict comparison, and elimination of free artifact-scalar `float`/`Decimal(str(...))` coercions.

```text
$ grep -n 'artifacts\[\|pulse\[\|resolve_field(' scripts/check_paper_round7_artifacts.py
348:            artifacts[code] = payload
352:            schema = _typed(artifacts["XD"].get("schema"), "str", "XD#schema")
359:def resolve_field(payload: Any, path: str) -> Any:
380:                resolve_field(artifacts[field.source], field.path)
429:    return [resolve_field(artifacts[ref.source], ref.path) for ref in row.field_refs]
459:        summary = artifacts["AQ"].get("summary")
548:                resolve_field(artifacts[source], path),
590:    pulses = artifacts["XD"].get("per_pulse")
627:                        f"REFUSED: per_pulse[{index}] is not a dict",
633:                    pulse[value_key],
635:                    f"XD#per_pulse[{index}].{value_key}",
```

Lines 348, 459, and 590 are dictionary/list navigation; 380 is an existence-only resolution whose result is discarded. Line 429 feeds renderer values into typed wrappers, with composite lists validated before their typed leaves are consumed. Lines 352, 548, and 633 are directly `_typed`-guarded; 627/635 are labels, not reads.

## Verification notes

The requested full module command encountered the retained replay because the corpus exists here. It was stopped during AQ production; the subsequent explicit non-replay selection ran all 43 non-replay tests successfully. The module contains 44 tests total, leaving only the magistrate-owned replay test for bench verification.

Acceptance greps:

```text
$ grep -n 'Decimal(str(' scripts/check_paper_round7_artifacts.py
(no output; exit 1)

$ grep -n 'float(' scripts/check_paper_round7_artifacts.py
570:    return float(value)
604:                    x = float(shape.attrib[x_key])
605:                    y = float(shape.attrib[y_key])
607:                    x = float(shape.attrib[x_key]) + float(shape.attrib["width"]) / 2.0
608:                    y = float(shape.attrib[y_key]) + float(shape.attrib["height"]) / 2.0
610:                positioned.append((float("nan"), float("nan")))
```

F-8 is confirmed: `git diff --exit-code b36d1e85 781c8d78 -- scripts/check_paper_round7_artifacts.py` was empty. Thus the pre-edit `781c8d78` checker retained Sol 216’s cited lines `625–648`, `725–778`, and `840/860/869/874`; the registry repin did not move them.

Final status contains only the three allowlisted paths. Diff stat: 3 files, 464 insertions, 73 deletions.

## Clause map

| Closure | Production | Biting test | Counterfactual |
|---|---|---|---|
| F-1 | [checker:344](/Users/edr/code/JouleWise-wt-dx/scripts/check_paper_round7_artifacts.py:344), [checker:790](/Users/edr/code/JouleWise-wt-dx/scripts/check_paper_round7_artifacts.py:790) | [tests:693](/Users/edr/code/JouleWise-wt-dx/tests/test_paper_round7_artifacts.py:693) | Long decimal token crosses a fixed-six-place boundary after float/repr round-trip. |
| F-2 | [checker:171](/Users/edr/code/JouleWise-wt-dx/scripts/check_paper_round7_artifacts.py:171) | [tests:213](/Users/edr/code/JouleWise-wt-dx/tests/test_paper_round7_artifacts.py:213) | `True == 1`, `True == 1.0`, and `1 == 1.0` would pass; no legitimate call-site normalization was required. |
| F-3 | [checker:392](/Users/edr/code/JouleWise-wt-dx/scripts/check_paper_round7_artifacts.py:392), [checker:543](/Users/edr/code/JouleWise-wt-dx/scripts/check_paper_round7_artifacts.py:543), [checker:633](/Users/edr/code/JouleWise-wt-dx/scripts/check_paper_round7_artifacts.py:633) | [tests:221](/Users/edr/code/JouleWise-wt-dx/tests/test_paper_round7_artifacts.py:221), [tests:597](/Users/edr/code/JouleWise-wt-dx/tests/test_paper_round7_artifacts.py:597), [tests:621](/Users/edr/code/JouleWise-wt-dx/tests/test_paper_round7_artifacts.py:621) | Strings as numbers, integers as booleans, fractional counts, or non-string failure IDs are refused with exact field-qualified messages. |
| F-4 | [checker:568](/Users/edr/code/JouleWise-wt-dx/scripts/check_paper_round7_artifacts.py:568), [checker:573](/Users/edr/code/JouleWise-wt-dx/scripts/check_paper_round7_artifacts.py:573) | [tests:646](/Users/edr/code/JouleWise-wt-dx/tests/test_paper_round7_artifacts.py:646) | Per-pulse `"16.0"` would be accepted by `float(...)`; SVG strings remain valid geometry input. |
| F-5 | [checker:429](/Users/edr/code/JouleWise-wt-dx/scripts/check_paper_round7_artifacts.py:429), [checker:543](/Users/edr/code/JouleWise-wt-dx/scripts/check_paper_round7_artifacts.py:543), [checker:573](/Users/edr/code/JouleWise-wt-dx/scripts/check_paper_round7_artifacts.py:573) | [P1:597](/Users/edr/code/JouleWise-wt-dx/tests/test_paper_round7_artifacts.py:597), [P2:621](/Users/edr/code/JouleWise-wt-dx/tests/test_paper_round7_artifacts.py:621), [P3:646](/Users/edr/code/JouleWise-wt-dx/tests/test_paper_round7_artifacts.py:646), [P4:670](/Users/edr/code/JouleWise-wt-dx/tests/test_paper_round7_artifacts.py:670) | AQ string number, XD integer Boolean, and XD pulse string fail; JSON integer `4` remains accepted as a number. |
| F-6 | [checker:111](/Users/edr/code/JouleWise-wt-dx/scripts/check_paper_round7_artifacts.py:111), [checker:712](/Users/edr/code/JouleWise-wt-dx/scripts/check_paper_round7_artifacts.py:712), [checker:936](/Users/edr/code/JouleWise-wt-dx/scripts/check_paper_round7_artifacts.py:936), [checklist:29](/Users/edr/code/JouleWise-wt-dx/docs/paper/round7/fill-checklist.md:29) | [tests:252](/Users/edr/code/JouleWise-wt-dx/tests/test_paper_round7_artifacts.py:252), [tests:736](/Users/edr/code/JouleWise-wt-dx/tests/test_paper_round7_artifacts.py:736), [tests:759](/Users/edr/code/JouleWise-wt-dx/tests/test_paper_round7_artifacts.py:759), [tests:777](/Users/edr/code/JouleWise-wt-dx/tests/test_paper_round7_artifacts.py:777) | Standing sentence plus 15 markers, marker without standing sentence, altered sentence head, and current 0/0 skeleton. |
| F-7 | [checker:832](/Users/edr/code/JouleWise-wt-dx/scripts/check_paper_round7_artifacts.py:832), [checker:878](/Users/edr/code/JouleWise-wt-dx/scripts/check_paper_round7_artifacts.py:878) | [tests:467](/Users/edr/code/JouleWise-wt-dx/tests/test_paper_round7_artifacts.py:467) | Renaming `--out` to `--outt` yields exactly `pinned F4 command must contain exactly one --out`. |
| F-8 | Pre-edit `781c8d78`: `:625–648`, `:725–778`, `:840`, `:860`, `:869`, `:874`; final [literal block:662](/Users/edr/code/JouleWise-wt-dx/scripts/check_paper_round7_artifacts.py:662), [replay block:832](/Users/edr/code/JouleWise-wt-dx/scripts/check_paper_round7_artifacts.py:832), [main:954](/Users/edr/code/JouleWise-wt-dx/scripts/check_paper_round7_artifacts.py:954) | [tests:317](/Users/edr/code/JouleWise-wt-dx/tests/test_paper_round7_artifacts.py:317), [tests:442](/Users/edr/code/JouleWise-wt-dx/tests/test_paper_round7_artifacts.py:442), [tests:777](/Users/edr/code/JouleWise-wt-dx/tests/test_paper_round7_artifacts.py:777) | A stale clause map could audit the wrong literal, replay-command, or tail site after edits. |

## Residual risk

The retained full replay and exact 44-test module completion remain for the magistrate’s bench run.