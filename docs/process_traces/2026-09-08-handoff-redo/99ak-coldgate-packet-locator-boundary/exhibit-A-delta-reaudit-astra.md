```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "Selected routing tests bite, but issuing-relevant snapshot consumers still inherit replay mapping and the contract census omits them.",
  "workspace": {
    "base_requested": "20cd559f",
    "base_mode": "exact",
    "head_start": "ae09cad7a0abe620ef965167d6f8c72257e668e3",
    "head_end": "ae09cad7a0abe620ef965167d6f8c72257e668e3",
    "upstream_end": null,
    "branch": "fix/2026-09-08-icloud-custody-locator"
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "findings": [
      {
        "id": "F1",
        "severity": "blocker",
        "summary": "Issuing-relevant consumers outside the selected lifecycle sites still authenticate through default read_replay snapshot resolution.",
        "locations": [
          "scripts/mint_floor_artifact.py:2036",
          "scripts/mint_floor_artifact_generalized.py:3454",
          "scripts/build_bracket_binding.py:492",
          "scripts/build_bracket_binding.py:509",
          "joulewise/analysis_manifest_v3.py:3637"
        ]
      },
      {
        "id": "F2",
        "severity": "should_fix",
        "summary": "The contract census is explicitly limited to two modules and omits issuing-relevant and shared consumers required to establish the stated boundary.",
        "locations": ["docs/contracts/calibration_ledger_append.md:431"]
      }
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "test",
      "cmd": "python3 -B -m unittest -v tests.test_authentication_io.AuthenticationSurfaceGuardTests.test_marked_v2_surface_has_no_direct_readable_io tests.test_calibration_ledger_custody.CustodyProbeTests.test_readiness_forwards_resolution_mode_to_snapshot_and_state tests.test_calibration_ledger_custody.CustodyProbeTests.test_head_pin_advancement_forwards_issuing_mode tests.test_calibration_ledger_custody.CustodyProbeTests.test_lifecycle_slot_validator_forwards_issuing_mode tests.test_calibration_ledger_custody.CustodyProbeTests.test_unknown_resolution_mode_refuses_before_probe",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["OK"]},
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V2",
      "kind": "inspection",
      "cmd": "rg -n '\\b(probe_custody|_custody_probe_paths|_custody_state|_custody_reasons|load_calibration_ledger_snapshot)\\b' joulewise scripts",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": []},
      "expected": {"exit_code": 0, "tail_regex": "load_calibration_ledger_snapshot"}
    },
    {
      "id": "V3",
      "kind": "test",
      "cmd": "python3 -B -c 'import ast, pathlib, unittest, io\nfrom joulewise import calibration_ledger as ledger\nfrom scripts import validate_powermetrics_fiducial as writer\nfrom tests.test_calibration_ledger_custody import CustodyProbeTests\ncases=[(ledger,\"calibration_readiness\",\"test_readiness_forwards_resolution_mode_to_snapshot_and_state\"),(ledger,\"advance_calibration_head_pin\",\"test_head_pin_advancement_forwards_issuing_mode\"),(writer,\"_validate_reserved_bracket_slot\",\"test_lifecycle_slot_validator_forwards_issuing_mode\")]\nfor module,name,test in cases:\n tree=ast.parse(pathlib.Path(module.__file__).read_text()); node=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name==name)\n for n in ast.walk(node):\n  if isinstance(n,ast.keyword) and n.arg==\"mode\": n.value=ast.Constant(value=\"read_replay\")\n old=getattr(module,name); exec(compile(ast.fix_missing_locations(ast.Module(body=[node],type_ignores=[])),module.__file__,\"exec\"),module.__dict__)\n result=unittest.TextTestRunner(stream=io.StringIO()).run(CustodyProbeTests(test)); setattr(module,name,old)\n print(name+\": \"+str(len(result.failures))+\" assertion failures, \"+str(len(result.errors))+\" errors\")\n assert result.failures and not result.errors\nprint(\"MUTATIONS_KILLED=3\")'",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["MUTATIONS_KILLED=3"]},
      "expected": {"exit_code": 0, "tail_regex": "MUTATIONS_KILLED=3"}
    }
  ],
  "flags": [
    {
      "id": "R1",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "Filesystem-fixture tests and the full suite were not executed under the read-only filesystem restriction; their relevant assertions were inspected. Three routing counterfactuals ran entirely in memory.",
      "needs": "Lead should execute the fixture regression and broader verification after correcting issuing routing."
    }
  ]
}
```

## Findings

**F1 — blocker: the issuing boundary remains incomplete.** Floor minting inherits replay resolution at `scripts/mint_floor_artifact.py:2036`; generalized minting reaches the same default through `scripts/mint_floor_artifact_generalized.py:3454,3630,4066`. Bracket-binding publication uses replay snapshots at `scripts/build_bracket_binding.py:492,509`, including the purported finalizer-compatibility check. Analysis finalization also uses replay at `joulewise/analysis_manifest_v3.py:3637`. Thus, a missing original plus valid replacement can satisfy custody validation on issuing-relevant paths. This violates the addendum’s explicit issuer requirement (`docs/contracts/calibration_ledger_append.md:426`). Shared mint/replay validators need caller-sensitive propagation; globally flipping them would damage replay.

**F2 — should-fix: incomplete contract census.** The table expressly covers only “two owning modules” (`docs/contracts/calibration_ledger_append.md:431`) and misses F1’s consumers. Expand it to the following complete call-site inventory.

**1. Census.** `I` means issuing/original; `R` means read_replay/mapped; `N` means custody verification disabled. Imports, definitions, and exports are excluded. Line numbers below identify every actual call found by grep and AST inspection.

Within **`joulewise/calibration_ledger.py`**:

| Called function | Call lines: effective mode and classification |
|---|---|
| `probe_custody` | `277,2329,2357,2379`: explicit I, correct issuance helpers. `1788`: forwards `_custody_reasons` mode, default R. `4811`: forwards `_custody_state` mode, default I. Both forwarding boundaries are correct. |
| `_custody_probe_paths` | `4713`: I, lexical disabled query; `4765`: forwarded mode, default I. Correct. |
| `_custody_reasons` | `2071`: snapshot mode, default R; correct shared forwarding, subject to caller errors below. |
| `_custody_state` | `4886`: R, status; `5023`: enforcing I/advisory R; `5269`: I, resume-finalize. Correct. |
| `load_calibration_ledger_snapshot` | `4853`: R/N, status; `4968`: enforcing I/verified, advisory R/N; `5152`: I, head advancement; `5242`: R/N, resume-finalize, followed by explicit I state check. Correct. |

The remaining direct probe is **`joulewise/calibration_bracketing.py:1101`**: explicit R, correct candidate replay.

Remaining **snapshot** calls:

| File | Lines: mode and classification |
|---|---|
| `joulewise/receipt_oracle.py` | `143`: R/N, correct receipt inspection. |
| `joulewise/analysis_engine/inputs.py` | `1630,3125`: R, evidence binding/loading; correct replay, shared issuance consumers require propagation. |
| `joulewise/whole_window.py` | `512`: R, evidence authentication; correct replay, same shared-consumer caveat. |
| `joulewise/analysis_manifest_v3.py` | `3637`: R, shared finalization authentication; incorrect issuing branch, F1. |
| `scripts/run_campaign.py` | `4829`: R through kwargs (`4817`), runner evaluation; correct replay. |
| `scripts/check_window_provenance.py` | `322,854`: R/N, correct provenance checks. |
| `scripts/validate_powermetrics_fiducial.py` | `1208`: I, correct lifecycle gate. |
| `scripts/mint_floor_artifact.py` | `969`: R, shared component authentication; `1745`: R, replay rebinding; `2036`: R, incorrect mint route. |
| `scripts/mint_floor_artifact_generalized.py` | `3454`: R, incorrect mint route when no custody store; supplied stores use separate authentication. |
| `scripts/recover_calibration_ledger.py` | `233,264`: R, correct audit commands. |
| `scripts/build_bracket_binding.py` | `492,509`: R, incorrect publication/compatibility routes; `492` bypasses mapping when a store is supplied. |
| `scripts/generate_g2a_probe_inputs.py` | `675`: R/N, no mapped custody access. |

No replay mapping loss found. Candidate replay remains explicit. The paper producers/fence retain independent override resolvers at `scripts/paper_anchor_correction_quantified.py:221`, `scripts/paper_excursion_decomposition.py:134`, and `scripts/check_paper_replay_fence.py:330`.

**2. Four regression rows.** All four bite their selected sites, not the omitted census:

- `test_issuing_helpers_ignore_planted_replacement`: assertions at `tests/test_calibration_ledger_custody.py:133,134` compare outcomes and require zero replacement touches. Counterfactual: change `calibration_ledger.py:277` to R with the mint guard mocked, or flip any enumerated no-follow helper to R. Replacement probing records a touch even when its exception becomes absence. Inspected, not executed.
- `test_readiness_forwards_resolution_mode_to_snapshot_and_state`: assertions at `:164–166` check both mode kwargs. Counterfactual: force R at ledger `4968` or `5023`; fails.
- `test_head_pin_advancement_forwards_issuing_mode`: assertion `:184`; force R at ledger `5152`; fails.
- `test_lifecycle_slot_validator_forwards_issuing_mode`: assertion `:199`; force R at validator `1208`; fails.

The latter three counterfactuals were killed by in-memory mutations.

**3. Empty override.** Under backup prefixes, `""` returns absence without probing (`calibration_ledger.py:4702`); local paths remain original. This already occurred at base `20cd559f:4698`, so **no part-4 behavior change**. Compared with an unset override, it can spuriously REFUSE available custody: resume-finalize rejects absent state (`:5269–5275`). The mint guard rejects only nonempty overrides (`:4681–4685`); empty is permitted. This shortcut supplies no replacement bytes and does not establish a spurious PASS.

**4. Authentication pins.** No hidden I/O drift found. The pin protects the exact census of classified direct-I/O exceptions, keyed by file/function/line/operation (`tests/test_authentication_io.py:58,400–430`), not unrelated signature formatting. The pinned operations remain unchanged; the inventory test passes.

## Residual risk

No live custody validation or full-suite execution. The fixture-heavy helper counterfactual remains an inspected prediction.