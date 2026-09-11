# COLD-GATE ADJUDICATION PACKET — FCM-01 disposition after round-6 delta REJECT (FCM6-01)

Assembled mechanically 2026-08-11 from primary artifacts (verbatim below). The adjudicator has NO loop context by design.

## THE QUESTION

The round-6 fresh delta REJECTED on FCM6-01 (full report below). The pre-committed decision rule ('delta clean -> land FCM-01; any exact understatement on the extraction path -> merge the re-spec fallback') matched NEITHER branch: exact_understatement_found=false, but the 'closes by construction' claim is broken at the JSON admission boundary. A round 7 would be the next round on the fabricated-record-admission defect class (round 5 stopped on this class; round 6 claimed to close it by construction). Rule this binary + design question:

(i) AUTHORIZE ROUND 7 under a custody-closure design: accept that construction-closure at a serialization boundary is impossible in principle under repo-trust (any bytes a validator accepts can be produced by a forger running the same repo code — no in-repo secret exists); re-state the registered-identity claim as CUSTODY-closed (registered floors are trustworthy only through the governed extraction run's committed sha pin, the same custody model every other JouleWise artifact uses per D-120); wire validators/consumers so registered identity in admitted JSON is refused unless the artifact sha matches the committed governed-extraction record; complete the delta's unexecuted arithmetic lenses in the next audit.
(ii) MERGE THE FALLBACK NOW (respec/d124-withdrawn, 681ab49, green, ready): packs re-spec to the worst-case default estimator; wider floors; freeze lane unblocks immediately; the tighter-floor contrast margin is lost to the paper.
(iii) Any hybrid you judge superior (state it precisely, including its effect on the pack freeze).

Constraints binding the adjudicator: D-119 soundness-above-all; D-132 (verbatim below); the freeze lane and paper timeline gate on this disposition; Ed's standing FCM ruling (verbatim): 'Is there no long term benefit to repair of the contract? if it doesn't buy the paper or future ambitions for the research anything, absolutely dropping it is ok. So is repairing if it's a desk thread non-major blocker, your work is cheap.'

---
## EXHIBIT A — D-132 (docs/decision_log.md on main, index row verbatim)

| D-132 | STOPPING RULES TARGET DOOM LOOPS, NOT CONVERGING INSTRUMENTS (Ed, in-thread 2026-08-11): meta-process stop rules exist to kill non-converging loops — same defect recurring, no durable progress. They must NEVER terminate work on an instrument or component that is demonstrably converging (each round permanently closing its defect against a rising audit bar) when that work serves the paper: PROGRESS TOWARD A PUBLISHABLE PAPER IS THE HIGHEST-ORDER GOAL and all process rules rank below it (composing with D-119 soundness-above-all: soundness bounds WHAT may be claimed; this principle bounds when work may be STOPPED). Applied same-day: the FCM-01 stopping-rule execution is REVISED — the six-round record shows convergence, not doom-looping (arithmetic proven exact; production path sound from round 2; successive defects 0.25 J → 5e-10 J in ever-more-exotic classes) — and the estimator is REVIVED under the class-closing-by-construction design: the public registered surface is DELETED; the estimator becomes internal to the governed extraction path (the only path that may mint claims per the custody model), so no admitted-input class exists. The re-spec-to-default branch stays unmerged as the ready fallback until the revival round's delta verdict. Rust is affirmed as the H2/H3 next-generation core answer (unforgeable capability tokens), now justified by executed demonstration rather than conjecture | adopted (Ed, in-thread; transcribed by the magistrate) |

---
## EXHIBIT B — round-5 stopping record (STOPPED-FCM01.md on impl/floor-commonmode-01, verbatim)

# FLOOR-COMMONMODE-01 — STOPPED (Ed's pre-committed rule executed, 2026-08-11)

**Terminal state.** The D-124 relicense (decision log, ea3f325) carried a
BINDING pre-committed stopping rule: any exact-arithmetic understatement at
an admitted input found by the round-5 delta re-audit drops the unit to the
worst-case default with no further rounds. **The rule fired**: FCM-R5-01 —
the frozen dataclass's generated constructor plus a type()-only admission
check admit records fabricated by direct construction, dataclasses.replace,
object.__new__ + __setattr__, copy, and pickle; each admitted fabrication
carried a false zero index and understated by 4.999917146975008e-10 J in
exact arithmetic while passing registration validation. This is the
residual risk the relicense contract stated in advance (Python privacy is
conventional); Ed licensed with it stated; the rule executes as written.

**Disposition (executed):** the D-124 two-shared-edge estimator candidate
is WITHDRAWN from the freeze path per D-124's own fallback clause
("contrasts fall back to the worst-case default and the paper says so").
Freeze-plan Q7 is REVERSED; the packs' comparative cells re-spec to the
default worst-case estimator on main. This branch is the permanent record
of the six-round gauntlet (five understatement mechanisms + the provenance
class), three cold-gate sittings, two paired refuter reports, five delta
audits, and the adversary-authored oracle — all custodied. No further work
on this branch under any authority but Ed's explicit new decision.

**What the six rounds proved and bank for any future revival:** the
extremum enumeration is exact in rational arithmetic (three independent
proofs); the member-envelope enclosure is analytically derived; the real
a5 fixtures and the oracle are reusable; the terminal lesson is that a
sound registered surface in Python needs the arithmetic BEHIND a process
boundary or capability token, not a convention — the Rust-rewrite memory's
point, now with an executed demonstration.

---
## EXHIBIT C — round-6 implementation report (Sol xhigh, verbatim)

```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "findings",
  "completion": "complete",
  "summary": "Implemented D-132 by deleting public registered FloorEstimate construction and confining registration to governed extraction CellReports; all required tests pass.",
  "workspace": {
    "base_requested": "0b5fce8",
    "base_mode": "exact",
    "head_start": "0b5fce8f642500b03752be3b3da6e7d4843bb661",
    "head_end": "0b5fce8f642500b03752be3b3da6e7d4843bb661",
    "upstream_end": "0b5fce8f642500b03752be3b3da6e7d4843bb661",
    "branch": "impl/floor-commonmode-01"
  },
  "pathspec": [
    "docs/decision_log.md",
    "joulewise/detection_floor.py",
    "joulewise/floor_extraction.py",
    "tests/test_detection_floor.py",
    "tests/test_floor_extraction.py",
    "tests/test_r4_acceptance_oracle.py"
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
      "cmd": "python3 -m py_compile joulewise/detection_floor.py joulewise/floor_extraction.py tests/test_detection_floor.py tests/test_floor_extraction.py tests/test_r4_acceptance_oracle.py && python3 -m unittest tests.test_detection_floor tests.test_floor_extraction tests.test_d117_decode_contrast_plan tests.test_d117_floor_qwen25_1p5b_plan tests.test_d117_floor_qwen25_7b_plan tests.test_r4_acceptance_oracle",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Ran 287 tests in 8.082s",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 287 tests in [0-9.]+s\\n\\nOK"
      }
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "python3.11 -m py_compile joulewise/detection_floor.py joulewise/floor_extraction.py tests/test_detection_floor.py tests/test_floor_extraction.py tests/test_r4_acceptance_oracle.py && python3.11 -m unittest tests.test_detection_floor tests.test_floor_extraction tests.test_d117_decode_contrast_plan tests.test_d117_floor_qwen25_1p5b_plan tests.test_d117_floor_qwen25_7b_plan tests.test_r4_acceptance_oracle",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Ran 287 tests in 8.990s",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 287 tests in [0-9.]+s\\n\\nOK"
      }
    },
    {
      "id": "V3",
      "kind": "test",
      "cmd": "python3 -m unittest tests.test_floor_extraction.RegisteredCommonModeRealBlockTests.test_promoted_a5_fixture_replay_flows_through_extraction tests.test_detection_floor.AdversarialZeroDesignationProbes.test_internal_extraction_seam_has_zero_understatements_for_adversarial_z && python3.11 -m unittest tests.test_floor_extraction.RegisteredCommonModeRealBlockTests.test_promoted_a5_fixture_replay_flows_through_extraction tests.test_detection_floor.AdversarialZeroDesignationProbes.test_internal_extraction_seam_has_zero_understatements_for_adversarial_z",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Ran 2 tests in 0.362s",
          "OK",
          "Ran 2 tests in 0.371s",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 2 tests in [0-9.]+s\\n\\nOK.*Ran 2 tests in [0-9.]+s\\n\\nOK"
      }
    },
    {
      "id": "V4",
      "kind": "test",
      "cmd": "python3 -m unittest tests.test_r4_acceptance_oracle && python3.11 -m unittest tests.test_r4_acceptance_oracle",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Ran 9 tests in 1.682s",
          "OK",
          "Ran 9 tests in 1.909s",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 9 tests in [0-9.]+s\\n\\nOK.*Ran 9 tests in [0-9.]+s\\n\\nOK"
      }
    },
    {
      "id": "V5",
      "kind": "test",
      "cmd": "python3 -m unittest tests.test_floor_extraction.RegisteredCommonModeRealBlockTests.test_real_block_width_satisfies_both_exact_bars && python3.11 -m unittest tests.test_floor_extraction.RegisteredCommonModeRealBlockTests.test_real_block_width_satisfies_both_exact_bars",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Ran 1 test in 0.005s",
          "OK",
          "Ran 1 test in 0.005s",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 1 test in [0-9.]+s\\n\\nOK.*Ran 1 test in [0-9.]+s\\n\\nOK"
      }
    },
    {
      "id": "V6",
      "kind": "inspection",
      "cmd": "python3 -c 'import json; from pathlib import Path; from joulewise.floor_extraction import validate_extraction_spec; paths=[Path(\"configs/floor_mint/d117_qwen25_1p5b_extraction_spec.json\"),Path(\"configs/floor_mint/d117_qwen25_7b_extraction_spec.json\")]; assert all(not validate_extraction_spec(json.loads(p.read_text())) for p in paths); print(\"2 shipped specs valid\")' && python3.11 -c 'import json; from pathlib import Path; from joulewise.floor_extraction import validate_extraction_spec; paths=[Path(\"configs/floor_mint/d117_qwen25_1p5b_extraction_spec.json\"),Path(\"configs/floor_mint/d117_qwen25_7b_extraction_spec.json\")]; assert all(not validate_extraction_spec(json.loads(p.read_text())) for p in paths); print(\"2 shipped specs valid\")'",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "2 shipped specs valid",
          "2 shipped specs valid"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "2 shipped specs valid\\n2 shipped specs valid"
      }
    },
    {
      "id": "V7",
      "kind": "suite",
      "cmd": "python3 -m unittest discover -s tests",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Ran 3012 tests in 1560.043s",
          "OK (skipped=93)"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 3012 tests in [0-9.]+s\\n\\nOK \\(skipped=93\\)"
      }
    },
    {
      "id": "V8",
      "kind": "inspection",
      "cmd": "git diff --check",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "(no output)"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "^$"
      }
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "environment",
      "level": "nonblocking",
      "text": "The canonical suite skipped 93 environment- or retained-corpus-gated tests; both requested focused matrices, the oracle, exact bars, and specification validation ran under Python 3 and 3.11.",
      "needs": ""
    },
    {
      "id": "F2",
      "kind": "residual_risk",
      "level": "nonblocking",
      "text": "An exploratory direct reintegration of the machine-local source corpus produced 1.8695016260131678, 5.1e-15 above the frozen promoted A5 replay pin. The committed promoted replay vectors produce the required exact 1.8695016260131627 through extract_comparative_cell, and the trimmed real-byte b01/b02 exact-bar checks pass.",
      "needs": "Lead may confirm the frozen promoted A5 replay vectors remain the intended full-precision replay authority."
    }
  ]
}
```

## Change

Deleted the importable registered block type, its builder, and the `registered_block_inputs` overload. The legacy raw estimator remains public and always unregistered. Registered identity now appears only on the private extraction-produced `CellReport` form; its contained `FloorEstimate` remains unregistered and cannot receive registration through its constructor or public record builder.

The registered parameter dictionary gained `registered_results_exist_only_as_governed_extraction_artifacts`; the sole rotation is `dea20dc0d43760ebfd17cb6a130ab2c2e85fb7a9a06c224cbf584804ee2f9bdf`. The superseded-SHA regression now rejects five hashes.

Deleted obsolete round-5 surface tests:

- `test_builder_records_positive_zero_and_preserves_evaluation_order`
- `test_registered_surface_accepts_only_records_and_is_mutually_exclusive`
- `test_one_core_serves_both_surfaces_and_construction_is_single_site`
- `test_registered_cell_refuses_an_unregistered_raw_estimate`

The replacement tests prove public-surface absence, prevent forged registration serialization, and inventory the extraction-only production call graph.

Every oracle retargeting line is:

- Line 19: signature heading changed to the internal extraction seam.
- Line 21: declared callable changed to `_common_mode_floor_from_extracted_inputs`.
- Line 42: added the `floor_extraction` module import.
- Line 169: updated only the harness docstring.
- Lines 183–185: redirected the harness invocation to the internal seam.

No oracle bar, case generator, constant, or assertion changed.

The D-124 chain now contains the D-132 revival, deleted-surface design, rotated hash, and revised registered-artifact claim. Changes remain uncommitted.

## Verification notes

The 2,048-case exact-arithmetic campaign reported zero understatements. The promoted A5 replay produced exactly `1.8695016260131627` through `extract_comparative_cell`; real trimmed b01/b02 fixtures satisfy both exact bars.

Two preliminary diagnostic commands had invocation mistakes—an obsolete test method name and an incorrect registration-map lookup—and were corrected before the recorded verification runs. No product assertion failed.

## Residual risk

The frozen promoted replay and a fresh machine-local source-corpus reintegration differ by approximately `5.1e-15`; see flag F2.
---
## EXHIBIT D — round-6 fresh delta audit (Sol xhigh, verbatim) — the REJECT under adjudication

```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "partial",
  "summary": "REJECT: committed artifact validators admit forged registered identity that never passed through extract_comparative_cell.",
  "workspace": {
    "base_requested": "3390cb7",
    "base_mode": "exact",
    "head_start": "3390cb76132c20e8aed9f47605c2937dde864841",
    "head_end": "3390cb76132c20e8aed9f47605c2937dde864841",
    "upstream_end": "3390cb76132c20e8aed9f47605c2937dde864841",
    "branch": "impl/floor-commonmode-01"
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "overall": "REJECT",
    "findings": [
      {
        "id": "FCM6-01",
        "severity": "blocker",
        "lens": "surface-closure",
        "title": "Forged registered identity is admitted through JSON artifact validators",
        "evidence": [
          "Adding the current registration dictionary to a genuine extraction-report floor produced validate_d117_mint_consumption_report(...) == [].",
          "Adding the same identity to the comparative record in df-ph-decode-floor-mint1.json produced validate_floor_artifact(...) == [].",
          "authenticate_floor_artifact_bytes(...) then returned an AuthenticatedFloorArtifact carrying parameter sha dea20dc0d43760ebfd17cb6a130ab2c2e85fb7a9a06c224cbf584804ee2f9bdf.",
          "The forged artifact SHA was 8afdcb5133ff853f27a065e7eb06cd6c35e5626f432f6a6323398075299ddaaa."
        ],
        "impact": "Registered identity is not confined by construction to CellReports produced by extract_comparative_cell. A JSON producer can attach the exact registration mapping to an unrelated valid floor artifact, and a committed downstream consumer authenticates it.",
        "cause": "validate_d117_mint_consumption_report permits estimator_registration as an optional floor key without validating provenance. detection_floor._validate_comparative verifies only equality with the current registration dictionary; it does not establish that the record came from governed extraction.",
        "test_gap": "The new forgery regression checks only that build_comparative_record strips an object.__setattr__ mutation. It does not exercise direct JSON admission or authenticate_floor_artifact_bytes."
      }
    ],
    "exact_understatement_found": false
  },
  "verification": [
    {
      "id": "V1",
      "kind": "inspection",
      "cmd": "git status --short --branch && git rev-parse HEAD && git branch --show-current",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "## impl/floor-commonmode-01...origin/impl/floor-commonmode-01",
          "3390cb76132c20e8aed9f47605c2937dde864841",
          "impl/floor-commonmode-01"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "3390cb76132c20e8aed9f47605c2937dde864841"
      }
    },
    {
      "id": "V2",
      "kind": "smoke",
      "cmd": "python3 -c 'import json; from pathlib import Path; from joulewise.detection_floor import two_shared_edge_common_mode_registration,validate_floor_artifact; from joulewise.floor_extraction import validate_d117_mint_consumption_report; reg=two_shared_edge_common_mode_registration(); report=json.loads(Path(\"tests/fixtures/d117_postcollection_trust/extraction_report.json\").read_text()); report[\"cells\"][0][\"floor\"][\"estimator_registration\"]=reg; print(\"d117_profile_errors=\",validate_d117_mint_consumption_report(report)); artifact=json.loads(Path(\"df-ph-decode-floor-mint1.json\").read_text()); comps=[]; [(cell[\"comparative\"].update({\"estimator_registration\":reg}),comps.append(cell.get(\"cell_id\"))) for cell in artifact[\"cells\"] if isinstance(cell.get(\"comparative\"),dict)]; errors=validate_floor_artifact(artifact); print(\"mutated_comparative_cells=\",comps); print(\"floor_artifact_error_count=\",len(errors)); print(\"floor_artifact_errors=\",errors[:10])'",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 0,
        "tail": [
          "d117_profile_errors= []",
          "mutated_comparative_cells= ['df-ph-decode-floor']",
          "floor_artifact_error_count= 0",
          "floor_artifact_errors= []"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "one or both validators reject the injected identity"
      }
    },
    {
      "id": "V3",
      "kind": "smoke",
      "cmd": "python3 -c 'import json; from pathlib import Path; from joulewise.detection_floor import two_shared_edge_common_mode_registration; from joulewise.analysis_engine.inputs import authenticate_floor_artifact_bytes; a=json.loads(Path(\"df-ph-decode-floor-mint1.json\").read_text()); a[\"cells\"][0][\"comparative\"][\"estimator_registration\"]=two_shared_edge_common_mode_registration(); raw=json.dumps(a,sort_keys=True,separators=(\",\",\":\"),allow_nan=False).encode(); accepted=authenticate_floor_artifact_bytes(raw); print(\"accepted_artifact_id=\",accepted.value[\"artifact_id\"]); print(\"accepted_registration_sha=\",accepted.value[\"cells\"][0][\"comparative\"][\"estimator_registration\"][\"parameter_sha256\"]); print(\"authenticated_sha256=\",accepted.file_sha256)'",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 0,
        "tail": [
          "accepted_artifact_id= df-ph-decode-floor-mint1",
          "accepted_registration_sha= dea20dc0d43760ebfd17cb6a130ab2c2e85fb7a9a06c224cbf584804ee2f9bdf",
          "authenticated_sha256= 8afdcb5133ff853f27a065e7eb06cd6c35e5626f432f6a6323398075299ddaaa"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "injected registered identity is rejected"
      }
    },
    {
      "id": "V4",
      "kind": "inspection",
      "cmd": "python3 --version; python3.11 --version; git status --short --branch",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Python 3.13.1",
          "Python 3.11.15",
          "## impl/floor-commonmode-01...origin/impl/floor-commonmode-01"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "impl/floor-commonmode-01"
      }
    }
  ],
  "flags": [
    {
      "id": "G1",
      "kind": "verification_gap",
      "level": "blocking",
      "text": "The interrupted audit did not complete the A5 replay, independent >=500-case rational campaign, oracle pass/mutation proof, pre-round-6 replacement-test execution, parameter/spec cross-interpreter checks, or canonical suite.",
      "needs": "Do not treat the unexecuted lenses as clean; the demonstrated surface-closure blocker already selects REJECT."
    }
  ]
}
```

## Findings

FCM6-01 — blocker: the construction-only claim is false at a committed admission boundary.

A genuine extraction-report JSON can be mutated to add `estimator_registration`, and `validate_d117_mint_consumption_report` returns no errors. More decisively, the same identity can be injected into a genuine floor artifact; both `validate_floor_artifact` and the analysis engine’s `authenticate_floor_artifact_bytes` accept it as authenticated.

The validator checks that the supplied mapping equals the current registration dictionary, but never proves that the registered result was emitted by `extract_comparative_cell`. This is exactly the forbidden artifact class: registered identity without governed extraction.

The replacement forgery test does not close this path. It proves only that `build_comparative_record` omits a mutated `FloorEstimate.estimator_registration`; direct JSON admission bypasses that builder.

Overall verdict: **REJECT**.

## Residual risk

No exact arithmetic understatement was established in the completed evidence. The remaining mandatory arithmetic, oracle, historical-baseline, parameter/spec, and suite executions were not completed before the audit turn was interrupted. The worktree remained clean and no files were modified.