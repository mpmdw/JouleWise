```json
{"schema":"claude-codex-report/v1","genre":"review","status":"clean","completion":"complete","summary":"LANDABLE: missed-consumer class structurally closed by census and typed admission; R1-R4/S1-S3 closed.","workspace":{"base_requested":"a76d30ed","base_mode":"exact","head_start":"a76d30edf987d838312086881468866c8999a7a7","head_end":"a76d30edf987d838312086881468866c8999a7a7","upstream_end":"46d925c2baf310fb5a69042a6246bb194d271405","branch":"feat/2026-09-04-fb-metadata"},"pathspec":["docs/process_traces/2026-09-04-peer-audit/44-fb-v2-structural-delta.md"],"unowned_dirty":[],"verdict":{"decision":"LANDABLE","same_signature":"STRUCTURALLY CLOSED within the explicit static-reader and JSON-carrier boundary","findings":[],"closures":{"R1-R4":"closed","S1-S3":"closed"}},"verification":[{"id":"V1","kind":"test","cmd":"PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_single_count_discipline_census","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["Ran 4 tests in 8.449s","OK"]},"expected":{"exit_code":0,"tail_regex":"OK$"}},{"id":"V2","kind":"test","cmd":"PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_single_count_discipline_matrix","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["Ran 11 tests in 1.691s","OK"]},"expected":{"exit_code":0,"tail_regex":"OK$"}},{"id":"V3","kind":"test","cmd":"PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_detection_floor","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["Ran 161 tests in 2.582s","OK (skipped=1)"]},"expected":{"exit_code":0,"tail_regex":"OK \\(skipped=1\\)$"}},{"id":"V4","kind":"test","cmd":"PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_analysis_claims","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["Ran 64 tests in 0.310s","OK"]},"expected":{"exit_code":0,"tail_regex":"OK$"}},{"id":"V5","kind":"test","cmd":"PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_floor_extraction","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["Ran 168 tests in 3.989s","OK"]},"expected":{"exit_code":0,"tail_regex":"OK$"}},{"id":"V6","kind":"test","cmd":"PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_mint_floor_artifact","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["Ran 40 tests in 1.055s","OK"]},"expected":{"exit_code":0,"tail_regex":"OK$"}},{"id":"V7","kind":"test","cmd":"PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_d165_dominance_closeout","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["Ran 47 tests in 10.987s","OK"]},"expected":{"exit_code":0,"tail_regex":"OK$"}},{"id":"V8","kind":"test","cmd":"PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=. python3 /private/tmp/jw-fb44-jnj22g/audit.py census","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["PASS: 4 scratch census mutations killed by intended assertion; repository unchanged"]},"expected":{"exit_code":0,"tail_regex":"PASS:.*$"}},{"id":"V9","kind":"smoke","cmd":"PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=. python3 /private/tmp/jw-fb44-jnj22g/audit.py stress","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["PASS unhashable IDs: aggregation=96, bytes=32, generalized_extraction=32, generalized_writer=64, mint_prose=48, resolver=16","PASS: all 288 cases used named refusal/null floors; no TypeError/KeyError/AttributeError; no writes"]},"expected":{"exit_code":0,"tail_regex":"PASS:.*$"}},{"id":"V10","kind":"smoke","cmd":"PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=. python3 /private/tmp/jw-fb44-jnj22g/audit.py compat","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["PASS: 5 byte-identical carriers; 18 frozen v1 wires accepted by migrated consumers; root mint validates","PASS: v2 emission pins unchanged; v1/v2 6/5/4 remains direction_supported"]},"expected":{"exit_code":0,"tail_regex":"PASS:.*$"}},{"id":"V11","kind":"smoke","cmd":"PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=. python3 /private/tmp/jw-fb44-jnj22g/audit.py baseline","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["PASS: synthetic-carrier full-validation limitations are inherited"]},"expected":{"exit_code":0,"tail_regex":"PASS:.*$"}},{"id":"V12","kind":"inspection","cmd":"PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=. python3 /private/tmp/jw-fb44-jnj22g/audit.py deletions","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["PASS: ten local canonical calls removed; emitter AST unchanged; replacement boundaries inspected"]},"expected":{"exit_code":0,"tail_regex":"PASS:.*$"}},{"id":"V13","kind":"inspection","cmd":"git diff --check","cwd":".","observed":{"result":"pass","exit_code":0,"tail":[]},"expected":{"exit_code":0,"tail_regex":"^$"}}],"flags":[]}
```

## Findings

No findings. **LANDABLE; same-signature STRUCTURALLY CLOSED by census plus accessor** within 42's ordinary-Python boundary.

Independent grep across joulewise/ and scripts/ of outer keys, formulas, inner keys and version literals: 67 hits. Following profile/cohort/adapter/renderer/writer and vocabulary callers recovers the indirect paths. Manifest comparison: **271 entries, 19 required edges, zero unclassified raw readers**. Raw discipline reads occur only in accessor/adapter; formula reads use validated copies.

All rows in 42 accounted for (df=detection_floor; ae=analysis_engine):

| Reader set | Route/consequence |
|---|---|
| df predicate, component/cell/group, old ID census | Wrapper or floor profile → accessor/cohort before deeper validation. |
| ae/inputs bytes, exact/transport, resolution adapter | Validator delegate; selected metadata parses before copying; invalid resolution gives artifact_schema_invalid/null floors. Adapter handles default None. |
| ae aggregation/evaluation | Admit every resolution before filtering; typed cohort and copies; claim forwarding parses active floor. |
| ae/claims | Required accessor; invalid → floor_artifact_invalid/not_estimable/false readiness. |
| ae/artifact metadata, relationships, generic forwarding, finalize/write | Accessor/cohort; copied views; retained validation delegates and ClaimArtifactError before writes. |
| floor_extraction outputs/D117 keys | Canonical emitters and exact vocabulary/schema exceptions. |
| Original mint selection/construction/prose/writers | Extraction profile before selection/reconstruction; profile/cohort before output; MintError. |
| Generalized validation, both ingress routes, both writers/wrappers | Validator/renderer/writer edges; pre-reconstruction profile; public core-error translation. |
| build_site/HTML; five historical files | Markdown consumer, no JSON admission. HTML/Markdown object parity and v1-byte tests pass. |

V8 executes the census test on four scratch source copies. First three: `unclassified raw readers`; removed writer/renderer edge: `deleted delegate edges`. Each: one assertion failure, zero errors. Exact tails:

```text
new_raw_get:
Ran 1 test in 0.010s

FAILED (failures=1)
same_function_bypass:
Ran 1 test in 0.009s

FAILED (failures=1)
alias:
Ran 1 test in 0.009s

FAILED (failures=1)
deleted_delegate:
Ran 1 test in 0.062s

FAILED (failures=1)
```

Matrix: all 15 v1/16 v2 shapes cover missing/null/list/object/string, non-string/unknown/unhashable IDs, ID/body swaps, extra fields, bool/int confusion and mixed canonical versions both ways. Cell/absolute/comparative/group cross bytes/pre-projection chains, original prose/writer and both generalized writers. Extraction root/cell cross pre-reconstruction ingress, original selection/authenticated construction and prose/writers. Resolution injections cover exact/transported/refused, both orders and absent diagnostics. Claims/finalize/write, parent absence, detached views, valid controls and twelve runtime mutation kills passed.

V9 independently expands rule IDs to `[]`, `{}`, `[[]]`, `{"nested":[]}`: **288 named-refusal/null-floor checks, no TypeError/KeyError/AttributeError, no negative-case writes**. Pure resolver coverage is selected cell/group; component chains correctly stop at byte admission. Extraction bytes is a wrong-schema control; resolver/aggregation are N/A. Pure resolvers do not own cross-carrier mixtures.

V10: four `dominance-reproduced-{alpha,beta}-{extraction,floor}.json` files plus `df-ph-decode-floor-mint1.json` match origin/main byte-for-byte. All 18 objects take the exact frozen v1 branch and pass migrated component/cell/group, bytes, exact/transport, aggregation, claim/finalization and prose consumers in valid fixture contexts. Root mint fully validates. V2 emission and emitter AST are unchanged: planning_sizing_expression, both_terms_required=true, gating=false, role=prospective_sizing_diagnostic, not_an_acceptance_gate=true. Both versions retain the direction_supported, claim-ready 6/5/4 witness.

Deletion audit of `git show a76d30ed`: ten local canonical calls are gone (AST 10→0); wrapper remains. Also removed: R1 guard/copy filter/raw-ID set/raw copies; R3 collect/traversal/validation/ID set/emitter re-selection; R4 unchecked comprehension/Mapping guard; raw parent-child/claim comparisons and generic projection. Owning helper callers remain behind profile admission. Domain checks, error adapters, mixed-version invariants and validation-before-write remain. No dependent regression found.

## Residual risk

495 tests, one existing skip; modules sequentially, no discovery/launchers/hardware. Generalized probes stub custody/recomputation, retaining real admission/output. V11 confirms inherited synthetic-carrier full-validator errors: 18 per extraction, 169 per floor, identical to origin/main. These are compatibility fixtures.

Static census excludes arbitrary reflection/dynamic code. HTML object parity passed; full-site build/live custody were not reverified. Replay helper: `/private/tmp/jw-fb44-jnj22g/audit.py`, SHA-256 `e3c986b10d87429c0bbbb1b33daba293f35a378c21e89db2047a718248cf30fa`.

M0: clean/exact base; no stop card; A151 [AGENT]/D-174. Only authorized report written. Next: lead adjudicates and verifies integration before landing.
