# D123 supplier — Sol fix round 1

Date: 2026-09-04

Base: `456f4e4fa47462b3d85696e8b1da9f00317ab7e6`

Authority: R1 in `docs/process_traces/2026-09-04-paper-i/06-magistrate-contract-rulings.md`; both `02-refuter-execution.md` and `02-refuter-contract.md`.

Evidence class: synthetic fixtures only. No measurement value is inferred or issued.

## Finding → cure → production/test site

| Finding | Cure | Production and biting regression |
|---|---|---|
| Execution B1 / contract F1 — incompatible invented extraction wire | Added content-addressed `joulewise.reported_phase_energy_source.v1` plus separately versioned `joulewise.reported_phase_energy_projection.v1`; the source producer now invokes the established `validate_d117_mint_consumption_report` before the report can parent a projection. | `joulewise/reported_phase_energy.py:349-440`; incompatible old-shaped report regression `tests/test_reported_phase_energy.py:606-625` |
| Contract F2 — proposed t95 rule could fill default-rule placements | Kept both ruled composition algorithms in the artifact validator, but issuance and projection enforce `composed_member_envelope_mean.v1` for the current decode/selected-prefill placements. | `joulewise/reported_phase_energy.py:1267-1316,1352-1424`; forged t95 issuance regression `tests/test_reported_phase_energy.py:426-463` |
| Contract F3 — 20 exact-token rows remained stale | Rebound all 20 exact tokens to artifact field paths, default rule, refusal scope, governed issuance, and `VALUE_UNISSUED`; removed the stale undefined-basis discrepancy/checklist text. | `docs/paper/results-fill-registry.md:329-364,936,988-990`; registry-sync regression `tests/test_reported_phase_energy.py:797-806` |
| Execution B2 / contract F4 — uniform denominator source required | The ratio-of-sums issues for any per-member mix of the two allowed sources and records the sorted authenticated `token_count_sources` set. | `joulewise/reported_phase_energy.py:760-778,1069-1092`; mixed-source regression `tests/test_reported_phase_energy.py:540-587` |
| Contract F5 — self-hash mistaken for issuance | Added `joulewise.reported_phase_energy_issuance.v1`; its producer rebuilds each artifact from exact source bytes, and the projector requires an externally expected SHA-256 of the role-to-artifact manifest. | `joulewise/reported_phase_energy.py:1232-1335,1352-1381`; resealed-number regression `tests/test_reported_phase_energy.py:689-727` |
| Execution B3 / contract F6 — duplicate role was last-wins | The projector censuses candidates before selection and requires exactly one candidate per role, refusing only the affected role. | `joulewise/reported_phase_energy.py:1383-1393`; both-order regression `tests/test_reported_phase_energy.py:665-687` |
| Execution S1 / contract F7 — zero-digest custody fabrication | Refused members preserve available custody and encode unavailable bundle/summary/metadata/basis hashes as `null`; issued members still require all hashes. | `joulewise/reported_phase_energy.py:443-492,966-1008`; missing-custody regression `tests/test_reported_phase_energy.py:627-650` |
| Execution S2 — stale-address mutation mask and missing boundary coverage | The mutation census now includes digest, status/outcome, census, member-energy, mean, interval, and per-token boundaries. Every artifact mutation is resealed before the source-derived issuer check; parent-digest mutations are rejected against exact source bytes. | `joulewise/reported_phase_energy.py:1267-1300`; exhaustive resealed mutation regression `tests/test_reported_phase_energy.py:729-795` |

Ruling precedence: F2 exposed implementation drift, not a ruling conflict. R1 explicitly keeps the t95 rule PROPOSED while binding current placements to the default; the cure follows R1. No refuter finding showed R1 contradicting a registered decision, registry row, or validator. F1 instead showed that the landing had reused an established schema tag for incompatible fixture bytes; the new projection is separately versioned and the existing validator remains authoritative.

## Clause map delta

| R1 proposition | Production site | Biting assertion / counterfactual |
|---|---|---|
| “one content-addressed artifact per `campaign_role`” | `joulewise/reported_phase_energy.py:1267-1335,1383-1393` | `tests/test_reported_phase_energy.py:665-687`; adding a second alpha candidate in either order refuses alpha |
| default rule now; t95 rule remains proposed behind its ID | `joulewise/reported_phase_energy.py:730-755,1301-1316,1414-1424` | `tests/test_reported_phase_energy.py:388-463`; changing the current placement to t95 cannot render even under a resealed caller manifest |
| three refusal levels | `joulewise/reported_phase_energy.py:443-492,537-796,1352-1429` | `tests/test_reported_phase_energy.py:477-538,540-587,627-650`; artifact, owning-cell, and denominator-only defects have distinct STOP_FILL scope |
| ratio of sums; both runtime sources; prompt equality; decode 512 | `joulewise/reported_phase_energy.py:495-535,760-778,1069-1092` | `tests/test_reported_phase_energy.py:540-587`; mixed allowed sources issue, fallback/count mismatch refuses only per-token |
| custody-rich wire, explicit role, renderer owns formatting | `joulewise/reported_phase_energy.py:799-934,1098-1205,1352-1429` | `tests/test_reported_phase_energy.py:288-806`; removing role/custody or changing a boundary fails validation/issuance, while numeric rendering occurs only after validation |
| registry corrects stale undefined-basis text and binds DS-09..24 | `docs/paper/results-fill-registry.md:329-364,867-882` | `tests/test_reported_phase_energy.py:797-806`; reverting any exact-token row to UNKNOWN/SUPPLIER_UNKNOWN fails synchronization |

## Red → green

Red after the refuter counterfactuals were installed, before the registry and mixed-source cures:

```text
ERROR ... (mutation='mixed_runtime_sources', refusal='per-token')
FAIL ... (token='[E_1p7B_prefill_p[PREFILL_LENGTH]_J_per_request]', check='registry-sync')
... 19 additional registry-sync failures ...
Ran 1 test in 50.692s
FAILED (failures=20, errors=1)
```

Green after the fixes:

```text
Ran 1 test in 51.033s
OK
```

## Verification

Pre-change authorized baseline:

```text
python3 -m unittest tests.test_reported_phase_energy tests.test_d117_floor_qwen3_v5_generate tests.test_floor_extraction tests.test_paper_first_use_ledger tests.test_paper_terms_lint
Ran 195 tests in 22.789s
OK
```

Final authorized checks:

```text
python3 -m unittest tests.test_reported_phase_energy
Ran 1 test in 51.033s
OK

python3 -m unittest tests.test_d117_floor_qwen3_v5_generate tests.test_floor_extraction
Ran 181 tests in 11.667s
OK

R7F_CORPUS_ROOT=/Users/edr/code/JouleWise python3 -m unittest tests.test_paper_first_use_ledger tests.test_paper_terms_lint
Ran 13 tests in 2.710s
OK
```

The prompt prohibits the canonical whole suite; it was not run. Final authorized-suite evidence follows in the runner envelope.
