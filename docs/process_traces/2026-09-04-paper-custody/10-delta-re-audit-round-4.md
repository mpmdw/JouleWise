```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "LANDABLE: every round-4 gate cure is present and mutation-sensitive; two nonblocking same-signature contract/test weaknesses remain.",
  "workspace": {"base_requested":"f2d35b4f","base_mode":"exact","head_start":"f2d35b4f7fe58f059ed999e18754fa3a4f8ff9ba","head_end":"f2d35b4f7fe58f059ed999e18754fa3a4f8ff9ba","upstream_end":"f2d35b4f7fe58f059ed999e18754fa3a4f8ff9ba","branch":"feat/2026-09-04-paper-custody-seam"},
  "pathspec": ["docs/process_traces/2026-09-04-paper-custody/10-delta-re-audit-round-4.md"],
  "unowned_dirty": [],
  "verdict": {
    "landing": "LANDABLE",
    "gate_findings": {"G1/C-01":"cured","G2/C-05":"cured"},
    "other_dispositions": {"C-02":"cured","C-03":"cured for ordinary construction; F1 remains","C-04":"cured","C-06":"current registry cured; F2 remains","N-2":"cured"},
    "same_signature": "Yes. F1 is the deliberate-forgery/contract-overclaim class of execution F4/C-03; F2 is the static-literal-without-semantic-reach class of round-1 delta F2 and G1/C-01. Neither reopens an ordinary public caller-authority channel, and production issuance remains blanket-refused.",
    "peer_f4": {"status":"open_should_fix","reuse":"possible but not drop-in","cost":"about 0.5 day for arithmetic factoring; 1-2 engineer-days for a correct custodied seam, supply-map/input-contract changes, and regressions"},
    "findings": [
      {"id":"F1","severity":"should_fix","file_line":"joulewise/paper_custody.py:155-203; docs/contracts/paper_supply_custody.md:53-56,75-81","text":"The token is stored on every authentic capability, so object.__getattribute__ can extract a fixture token and the importable private constructors can mint an issuance_authorized forged result; the closure-only and never-valid object.__new__ contract claims are too strong."},
      {"id":"F2","severity":"should_fix","file_line":"tests/test_paper_custody.py:614-658","text":"The claimed raise-site reachability census is source.count(code)>1. A dead string can replace a real raise while this check stays green; use an AST/dataflow census or explicit per-condition executions."}
    ]
  },
  "verification": [
    {"id":"V1","kind":"inspection","cmd":"git rev-parse HEAD && git branch --show-current && git status --short --branch","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["f2d35b4f7fe58f059ed999e18754fa3a4f8ff9ba","feat/2026-09-04-paper-custody-seam","## feat/2026-09-04-paper-custody-seam...origin/feat/2026-09-04-paper-custody-seam"]},"expected":{"exit_code":0,"tail_regex":"origin/feat/2026-09-04-paper-custody-seam$"}},
    {"id":"V2","kind":"test","cmd":"PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_paper_custody","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["Ran 15 tests in 20.067s","OK"]},"expected":{"exit_code":0,"tail_regex":"Ran 15 tests[\\s\\S]*OK$"}},
    {"id":"V3","kind":"test","cmd":"PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_authentication_io","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["Ran 21 tests in 1.306s","OK"]},"expected":{"exit_code":0,"tail_regex":"Ran 21 tests[\\s\\S]*OK$"}},
    {"id":"V4","kind":"test","cmd":"PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_d165_dominance_closeout","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["Ran 51 tests in 11.622s","OK"]},"expected":{"exit_code":0,"tail_regex":"Ran 51 tests[\\s\\S]*OK$"}}
  ],
  "flags": [
    {"id":"FL1","kind":"baseline_drift","level":"nonblocking","text":"The requested peer-audit path is absent from f2d35b4f; F4 was read from the committed path at 5e416c47 on the named 2026-09-04 consult ref.","needs":"Lead should preserve that source identity when consuming this assessment."},
    {"id":"FL2","kind":"verification_gap","level":"nonblocking","text":"The discovery suite was not run because the preflight forbade it; only permitted single modules and counterfactuals ran.","needs":""},
    {"id":"FL3","kind":"residual_risk","level":"nonblocking","text":"All seam roles are synthetic/non-issuing; no production supplier, real v5 floor, hardware, or quiet-machine evidence was exercised.","needs":"Keep production issuance stopped through supplier final-head review."}
  ]
}
```

## Findings

Verdict: **LANDABLE**. G1 and G2, the two Opus gate conditions, are closed. The following nonblocking issues should travel with the supplier re-landing.

### F1 — should_fix — the capability token is recoverable

The ordinary-mistake cure is real: direct constructors refuse, tokenless `object.__new__` values refuse on guarded access, and the private mint is used at `paper_custody.py:1277-1311`. But the token is also written into every authentic object (`:174,:197`). From a legitimate non-issuing fixture result, `object.__getattribute__(opened, "_custody_token")` recovered it; `_construct_custody_evidence` and `_construct_verified` then produced a readable `VerifiedD165Closeout`: `EXTRACTED_TOKEN True`; `FORGED_AUTHORIZED True`; `FORGED_HEADLINE supplier-authored`. This requires deliberate private introspection, so it is outside D-161's ordinary-operator threat and does not block this fixture-only landing, but contract lines 53-56 and 75-81 must be narrowed or the token must not be resident on capabilities.

### F2 — should_fix — C-06's “reachability census” is a string count

The current 16-code registry, contract table, and inspected current conditions agree (`paper_custody.py:41-60`; contract `:269-292`). The regression at `tests/test_paper_custody.py:655-658` does not prove that: replacing the production `paper_custody_receipt_unissued` raise with `paper_custody_request_invalid` plus a dead same-code assignment produced `COUNT_GUARD_SURVIVES True` and `RECEIPT_UNISSUED_RAISE_PRESENT False`. This is test debt, not a current registry mismatch.

### Named-finding delta matrix

Each counterfactual used a clean local clone of `f2d35b4f`, restored it between rows, and ran only the named single test module.

| Item | Cure at production call site | Revert and exact failing tail | New defect |
|---|---|---|---|
| G1 / C-01 | Operand classification and closed funnel at `dominance_closeout.py:354-383,1005-1030`; membership at `:1084-1089,1492-1495`; neutral record fallback at `:1959-1966`. | Parent `dominance_closeout.py`; `tests.test_d165_dominance_closeout...test_real_closeout_refusal_paths_stay_closed_when_message_is_reworded`: `AssertionError: 'the denominator wording changed' != 'dominance_ratio_zero_denominator'`; `Ran 1`; `FAILED (failures=1)`. | None found. |
| C-02 | Routed readers at `analysis_engine/inputs.py:115-120` and `analysis_manifest_v3.py:71-76`; enforced modules/exemptions at `test_authentication_io.py:29-65`. | Parent both production modules; `...AuthenticationSurfaceGuardTests.test_marked_v2_surface_has_no_direct_readable_io`: `First list contains 37 additional elements`; `Ran 1`; `FAILED (failures=1)`. | None found. |
| C-03 | Slotted guarded types and closure mint at `paper_custody.py:155-287`, consumed at `:1277-1311`. | Parent `paper_custody.py`; `...test_evidence_and_verified_outputs_require_the_private_seam_token`: `AssertionError: PaperCustodyRefusal not raised`; `Ran 1`; `FAILED (failures=1)`. | F1. |
| C-04 | Strict release containment at `identity_pins.py:819-852` and `paper_custody.py:1171`; anchor/map evidence at `paper_custody.py:1277-1289`. | Parent production files; evidence test: `AttributeError: 'CustodyEvidence' object has no attribute 'anchor_head'`; containment test: `TypeError: _mint_git_anchor() got an unexpected keyword argument 'require_origin_main'`; `Ran 2`; `FAILED (errors=2)`. | None found. |
| G2 / C-05 | Inventory-vs-map gate is `paper_custody.py:909-918`; the redundant later comparison is absent; coherent reseal reaches it via `test_paper_custody.py:228-281,354-366`. `09:52-63` explicitly corrects the historical `01/02` execution claim. | Parent `paper_custody.py`; `...test_no_post_pin_inventory_digest_comparison_remains_unreachable`: `AttributeError ... has no attribute '_open_paper_input_impl'`; `Ran 1`; `FAILED (errors=1)`. | None found; `01/02` are usable only with the `09` erratum. |
| C-06 | 16 declarations at `paper_custody.py:41-60`, normative conditions at contract `:269-292`, current test at `test_paper_custody.py:614-658`. | Parent `paper_custody.py`; `...test_refusal_namespace_is_closed_and_nonrendering`: `AssertionError ... != expected`; `Ran 1`; `FAILED (failures=1)`. | F2. |
| N-2 | Real whole-tree dirty gate at `scripts/mint_floor_artifact_generalized.py:1317-1354`, release wrapper `identity_pins.py:819-852`, real-path regression `test_paper_custody.py:509-525`, operational rule contract `:35-45`. | Monkeypatch `_actual_v2_git_state` to bypass the dirty check; `...test_real_anchor_refuses_untracked_nongoverned_file_without_mocking`: `AssertionError: IdentityPinProjectionError not raised`; `Ran 1`; `FAILED (failures=1)`. | None found. |

Same-signature statement: **yes**—F1 repeats the forgeability/overclaim class of round-1 execution F4 and C-03; F2 repeats the “two literals agree while the producer/call site escapes” test class of round-1 delta F2 and G1/C-01. Neither survivor is a G1/G2 gate failure.

## Residual risk

Peer-audit F4 is correct at this head. `analysis_engine.inputs.bind_floor_artifact_evidence` reopens bundles and checks bundle/config hashes, identities, order, and point metrics (`:1862-1999`) but not stored member/block widths. The mint's stronger path recomputes authenticated comparative inputs and exact widths (`floor_mint_estimator.py:468-576,598-718`; mint caller `scripts/mint_floor_artifact_generalized.py:4127-4151`).

The seam can reuse that logic, but floor bytes alone are insufficient. The current floor-bearing D-165 and claim roles (`paper_custody.py:351-379`) carry no v2 mint input manifest/pinset, component reports/specs/order manifests, evidence-root locator, calibration acceptance, ledger/head pin, or bracket binding required by the mint helper. The safe shape is to factor the mint's authenticated component reconstruction and exact-width comparison into a production module, add one Git-map-authorized recomputation descriptor plus its complete source census to each floor-bearing production family, and include the factored functions in the validator-source digest. Do not independently rewrite the estimator inside custody. Arithmetic factoring is about half a day; the full custodied seam, supply-map contract, fixtures, and counterfactual wrong-width regression are realistically **1–2 engineer-days**, assuming the final v5 inputs exist. Until then, retain F4's disclosed limitation and the blanket production stop.
