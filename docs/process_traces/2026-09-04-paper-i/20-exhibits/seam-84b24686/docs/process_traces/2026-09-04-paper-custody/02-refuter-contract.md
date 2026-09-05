```json
{
  "verdict": {
    "gauntlet": "NOT LANDABLE",
    "findings": [
      {"id":"F1","severity":"blocker","file":"joulewise/paper_custody.py","line":"456-485, 853-924","text":"The caller chooses the Git repository, HEAD, inventory path, and inventory whose generated-file digests become the authority; the required fixed clean-tree _mint_git_anchor and repository-selected supply map are absent.","counterfactual":"A caller creates and commits a private Git repository containing forged inputs, inventory, and receipt; the seam accepts that repository as its independent anchor and returns a typed fixture result. Removing the temporary production refusal would make the same caller-controlled root paper authority.","cure_shape":"Resolve the fixed repository and clean HEAD through identity_pins._mint_git_anchor, then resolve a repo-tracked supply map by closed role; never derive the trust root from the call."},
      {"id":"F2","severity":"blocker","file":"joulewise/paper_custody.py","line":"88-162, 488-504, 620-675, 847-879","text":"The public wire is a caller-authored graph of BoundFile paths/digests and ReceiptRef metadata, not the addendum's role name plus runs root only; the AST signature test misses this because the container is hidden behind _FamilyRef.","counterfactual":"A caller selects every path and pin, the inventory locator, and receipt metadata while the signature guard reports clean; with F1, complete resealing plus a caller-selected committed HEAD supplies the apparent authority.","cure_shape":"Replace the five object graphs with closed role-only refs containing only role and runs_root; look up paths, digests, schemas, validator identity, and receipt location internally, and make the guard assert the exact public signature/ref fields."},
      {"id":"F3","severity":"blocker","file":"joulewise/analysis_engine/inputs.py","line":"945-955","text":"Ruling 15 Q-C-8 and addendum 16 require both lower bypasses closed in this seam landing, but load_floor_artifact still degrades an authenticated artifact to Mapping+digest and campaign_provenance.load_campaign_log_rows still accepts caller raw_bytes at lines 453-469; the contract defers both at paper_supply_custody.md:171-175.","counterfactual":"A supplier can bypass the seam through either legacy API and regain caller-authored bytes or an authority-erasing mapping even though its nominal seam signature passes.","cure_shape":"Remove the raw/degrading forms or require a seam-issued internal capability now, cover both modules in authentication/signature guards, and add focused bypass regressions."},
      {"id":"F4","severity":"blocker","file":"joulewise/d165_dominance_closeout.py","line":"15-27, 38-71","text":"The new shim independently defines four adapter-category codes; it does not alias the closed D-165 producer reason enumeration in the real dominance_closeout module and no test cross-checks a registry map against that producer enumeration.","counterfactual":"dominance_closeout.py can add or emit a reason such as the comparative_common_mode_ratios malformed path at lines 1833/1952 while the four-code adapter set and registry remain green and collapse it to a generic owner code.","cure_shape":"Define and enforce the one exhaustive reason enumeration in joulewise/dominance_closeout.py. A shim is permitted only as a thin import alias of that exact object, never a duplicate; assert exact key equality with the registry map and exercise each producer reason."},
      {"id":"F5","severity":"blocker","file":"docs/decision_log.md","line":"218-220, EOF after 10899","text":"The diff deletes the provisional D-173 row and decision required by Q-C-9.","counterfactual":"Landing removes the authority the new contract claims governs it.","cure_shape":"Rebase, preserve D-173, and amend it to addendum 16."},
      {"id":"F6","severity":"should_fix","file":"joulewise/paper_custody.py","line":"400-405, 882","text":"The supposedly closed refusal boundary leaks raw exceptions: a non-string expected_sha256 reaches re.fullmatch and raises TypeError, and invocation inside an active V2AuthenticationReadSession raises RuntimeError.","counterfactual":"Malformed caller objects or a legitimate nested authentication call crash past PaperCustodyRefusal, so callers cannot exhaustively handle the closed paper_custody_* namespace.","cure_shape":"Validate primitive types before regex/path operations and translate session-state and all boundary failures to exact closed codes; add public-entry negative tests."},
      {"id":"F7","severity":"should_fix","file":"docs/contracts/paper_supply_custody.md","line":"3-5, 14-23, 39-66, 73-96, 104-131","text":"The normative text is not first-use complete or independently replicable: it uses D-173/D-123/D-165/D-117/G2-a/TR-01 without definitions or owning links, and omits the supply-map location/schema, role lookup, exact clean-tree anchor, and canonical inventory/receipt wire while prescribing the superseded caller-pin wire.","counterfactual":"Two clean-room implementers can choose different repositories, supply maps, clean-tree tests, receipt encodings, and validator-source digests and both claim conformance.","cure_shape":"Define or link every first-use term and specify the exact role-only call, repo map path/schema, _mint_git_anchor semantics, canonical wire/keysets, digest algorithms, and replay comparison from the text."}
    ]
  },
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "NOT LANDABLE: caller-selected Git authority, caller-pin API, open bypasses, duplicated D-165 reason ownership, and deleted D-173.",
  "workspace": {"base_requested":"b700ac4e","base_mode":"exact","head_start":"b700ac4ef08ca29963991b8d5e29217effe25656","head_end":"b700ac4ef08ca29963991b8d5e29217effe25656","upstream_end":"f61a7d06c4acd0e2abfa68fe5a30fa5b1e2e2b84","branch":null},
  "pathspec": ["docs/process_traces/2026-09-04-paper-custody/02-refuter-contract.md"],
  "unowned_dirty": [],
  "verification": [
    {"id":"V1","kind":"inspection","cmd":"test \"$(git rev-parse HEAD)\" = b700ac4ef08ca29963991b8d5e29217effe25656 && git diff --name-status origin/main..HEAD","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["M\\ttests/test_whole_window.py"]},"expected":{"exit_code":0,"tail_regex":"^M\\ttests/test_whole_window.py$"}},
    {"id":"V2","kind":"test","cmd":"python3 -m unittest tests.test_paper_custody tests.test_authentication_io.AuthenticationSurfaceGuardTests tests.test_authentication_io.V2AuthenticationReadSessionTests.test_pinned_nofollow_read_checks_digest_before_json_grammar tests.test_d165_dominance_closeout.D165PaperCustodyAdapterTests tests.test_floor_extraction.FloorCustodyReadTests tests.test_whole_window.PaperCustodyWholeWindowValidationTests","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["Ran 18 tests in 10.809s","OK"]},"expected":{"exit_code":0,"tail_regex":"^OK$"}},
    {"id":"V3","kind":"smoke","cmd":"python3 -c 'from tests.test_paper_custody import _FamilyFixture; from joulewise.paper_custody import open_paper_input; f=_FamilyFixture(\"claim_evidence\"); v=open_paper_input(f.ref); print(type(v).__name__, v.evidence.mode, v.evidence.issuance_authorized); f.close()'","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["VerifiedClaimEvidence test_fixture_non_issuing False"]},"expected":{"exit_code":0,"tail_regex":"False$"}}
  ],
  "flags": [
    {"id":"FL1","kind":"baseline_drift","level":"blocking","text":"The named addendum-5 file is absent from b700ac4e and origin/main, but is available in local Git at 913bf3f7 and was inspected there; b700ac4e also deletes origin/main's D-173.","needs":"Rebase the landing onto the ruling/addendum authority and preserve an addendum-conformant D-173."},
    {"id":"FL2","kind":"residual_risk","level":"nonblocking","text":"Production currently refuses issuance; no real supplier path was exercised.","needs":"Keep issuance blocked through F1-F4 and re-review the first supplier join."}
  ]
}
```

## Findings

### F1 — blocker — caller-selected Git is not an independent anchor

`open_paper_input` accepts `ref.root`, proves only that it is *some* Git root, and reads `HEAD:<caller inventory path>` (`joulewise/paper_custody.py:456-485,853-899`). The anchored inventory then supplies every generated-file digest and even each file's authority class (`:540-617,904-924`). The required fixed repository/clean-tree gate, `identity_pins._mint_git_anchor`, is never called. `tests/test_paper_custody.py:94-202` constructs a fresh caller-owned repository; V3 confirms the seam accepts it. The blanket production refusal limits today's result to non-issuing, but it does not make this contract landable.

Counterfactual: commit forged values, map, and receipt in a private repository, pass that root, and satisfy every current anchor check. Cure: obtain the fixed clean repository and HEAD from `_mint_git_anchor`; select the Git-tracked supply map internally by role.

### F2 — blocker — the public wire is the superseded caller-pin design

All five refs publicly carry a root, inventory `BoundFile`, every source `BoundFile(path, expected_sha256, role)`, and `ReceiptRef` metadata (`joulewise/paper_custody.py:88-162`). Those values drive the pinned reads and receipt comparison (`:488-504,620-675,847-879`). Addendum 16 permits only role name plus runs root. The signature guard at `tests/test_authentication_io.py:415-438` sees only `_FamilyRef`, so it blesses the hidden object graph.

Counterfactual: every locator, digest, and receipt selector remains caller-authored while the guard reports no channel. Cure: role-only refs; repository lookup owns all remaining fields; guard the exact signature and dataclass field set.

### F3 — blocker — Q-C-8 bypass closure was deferred, not landed

`joulewise/analysis_engine/inputs.py:945-955` still returns a mapping/digest pair, and `joulewise/campaign_provenance.py:453-469` still accepts `raw_bytes`. The seat report admits the omission at `docs/process_traces/2026-09-04-paper-custody/01-seat-landing-report.md:46-54`; the normative contract improperly postpones it at `docs/contracts/paper_supply_custody.md:171-175`. Ruling 15 clause 6 and addendum 16 clause 5 require both closures in this landing.

Counterfactual: a supplier routes through either legacy API and reacquires caller-authored or authority-erased evidence. Cure: close both APIs now and add focused negative tests plus guard coverage.

### F4 — blocker — the D-165 shim duplicates the wrong abstraction

`joulewise/d165_dominance_closeout.py:15-27` imports only validator functions, then independently defines four paper adapter categories. It neither aliases nor exhausts the producer's reason vocabulary in the real `joulewise/dominance_closeout.py`, which owns reason constants at `:40-49` and can emit the comparative malformed path at `:1833,1952`. `tests/test_d165_dominance_closeout.py:1990-2068` checks only that four adapter outcomes belong to the adapter's own set; it has no registry-map equality test.

Ruling: the duplicate enumeration is not permitted. A shim may remain only if it imports/aliases the exact canonical enumeration object from `dominance_closeout.py`; the producer must be constrained to that enum and the registry map must have exactly the same keys.

### F5 — blocker — D-173 is deleted by the landing diff

The current decision table ends at D-172 (`docs/decision_log.md:218-220`) and the file ends after the D-172 body (`:10895-10899`). `git diff origin/main..HEAD` shows deletion of both D-173 entries, contrary to Q-C-9 and ruling 15 clause 7.

Counterfactual: landing erases the authority that the new normative contract claims governs it. Cure: rebase, preserve D-173, and amend its old paths-plus-pins language to addendum 16.

### F6 — should_fix — raw exceptions escape the closed namespace

`_relative_path` applies the SHA regex without first requiring a string (`joulewise/paper_custody.py:400-405`); a malformed public ref raises raw `TypeError`. Entering the new session at `:882` inside an already active session raises raw `RuntimeError`. Both were reproduced directly.

Counterfactual: malformed input or nested legitimate use escapes the promised `paper_custody_*` handling contract. Cure: primitive validation first and exhaustive translation at the public boundary, with exact-code tests.

### F7 — should_fix — the normative text is not reproducible from itself

The contract uses D-173, D-123, D-165, D-117, G2-a, and TR-01 before defining or linking them (`docs/contracts/paper_supply_custody.md:3-5,39-66,104-131`). Its inventory definition and algorithm (`:14-23,73-96`) omit the repository supply-map path/schema, role lookup, exact clean-tree anchor, receipt/inventory canonical keysets, and validator-source digest algorithm; `:51-58` instead specifies the superseded caller-pin wire.

Counterfactual: independent implementers choose different anchors and wires while claiming conformance. Cure: define/link each first-use term and specify the exact role-only resolution and canonical algorithms in the normative text.

## Residual risk

The focused 18-test contract set is green, and the landing does correctly keep whole-window issuance blocked, keep receipt evidence corroborative, wrap reads in a fresh `V2AuthenticationReadSession`, join `paper_custody.py` to the authentication lint list, and expose closed top-level refusal codes. Those positives do not exercise a real producer or supplier. The repository-wide suite was not run, per the explicit preflight rule.
