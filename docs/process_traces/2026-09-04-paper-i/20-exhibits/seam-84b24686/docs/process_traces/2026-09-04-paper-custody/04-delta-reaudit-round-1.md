```json
{
  "verdict": {
    "gauntlet": "NOT LANDABLE",
    "same_signature": "Survivors continue execution F2 / contract F3-F5; no new signature.",
    "new_defects": [],
    "dispositions": [
      {"id":"execution/F1","status":"CURED","evidence":"Five refs are role+runs_root; clean anchor/map exercised."},
      {"id":"execution/F2","status":"NOT CURED","evidence":"Campaign raw_bytes is gone, but load_floor_artifact still returns Mapping+digest."},
      {"id":"execution/F3","status":"CURED","evidence":"Dispatcher/owner census killed 24 member mutations."},
      {"id":"execution/F4","status":"CURED","evidence":"All five public Verified* constructors refuse with paper_custody_request_invalid."},
      {"id":"execution/F5","status":"CURED","evidence":"The core enum/map equality test detects additions to either side and passes."},
      {"id":"contract/F1","status":"CURED","evidence":"Clean-tree opening passed; dirty-tree anchoring refused."},
      {"id":"contract/F2","status":"CURED","evidence":"Every public reference contains only role and runs_root."},
      {"id":"contract/F3","status":"NOT CURED","evidence":"The floor capability is still erased to dict+digest although the campaign-log byte channel is closed."},
      {"id":"contract/F4","status":"NOT CURED","evidence":"Old shim remains; core enum misses an emitted reason."},
      {"id":"contract/F5","status":"NOT CURED","evidence":"D-173 exists, but its paths+pins+receipts input rule was not amended to addendum 16's role+runs_root rule."},
      {"id":"contract/F6","status":"CURED","evidence":"Malformed map primitives, nested sessions, and forbidden construction all returned closed paper_custody_* refusals."},
      {"id":"contract/F7","status":"CURED","evidence":"Terms and all requested map/anchor algorithms are specified."}
    ],
    "findings": [
      {"id":"F1","severity":"blocker","file_line":"joulewise/analysis_engine/inputs.py:953-955","text":"The required lower floor bypass remains: load_floor_artifact erases AuthenticatedFloorArtifact to Mapping+digest; the file is absent from the fix diff while the contract falsely says the capability is preserved.","cure_shape":"Return AuthenticatedFloorArtifact and add the authentication/signature regression required by ruling 15 clause 6 and addendum 16 clause 5."},
      {"id":"F2","severity":"blocker","file_line":"joulewise/d165_dominance_closeout.py:21-71; joulewise/dominance_closeout.py:178-269; tests/test_d165_dominance_closeout.py:2070-2095","text":"The duplicate shim still exists, and the core enum/map test compares two static collections without constraining producer emissions; a real built close-out emitted an unenumerated reason.","cure_shape":"Delete the shim; make the real producer emit only the canonical enumeration; cross-check its actual registry map both ways and exercise each emitted reason."},
      {"id":"F3","severity":"blocker","file_line":"docs/decision_log.md:219,10914-10920","text":"D-173 was restored but still declares paths, expected-digest pins, and receipts as caller inputs, contradicting binding addendum 16 and the normative contract's role+runs_root wire.","cure_shape":"Amend both D-173 locations to the addendum-16 role+runs_root contract before landing."}
    ]
  },
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "NOT LANDABLE: the floor downgrade, duplicate/non-exhaustive D-165 reason ownership, and stale D-173 wire remain.",
  "workspace": {"base_requested":"2df32d5c","base_mode":"exact","head_start":"2df32d5c1f28e3f75c93072fcd50b6a9c04b6544","head_end":"2df32d5c1f28e3f75c93072fcd50b6a9c04b6544","upstream_end":"2df32d5c1f28e3f75c93072fcd50b6a9c04b6544","branch":"feat/2026-09-04-paper-custody-seam"},
  "pathspec": ["docs/process_traces/2026-09-04-paper-custody/04-delta-reaudit-round-1.md"],
  "unowned_dirty": [],
  "verification": [
    {"id":"V1","kind":"inspection","cmd":"git status --short --branch && git rev-parse HEAD && git branch --show-current","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["2df32d5c1f28e3f75c93072fcd50b6a9c04b6544","feat/2026-09-04-paper-custody-seam"]},"expected":{"exit_code":0,"tail_regex":"2df32d5c1f28e3f75c93072fcd50b6a9c04b6544[\\s\\S]*feat/2026-09-04-paper-custody-seam$"}},
    {"id":"V2","kind":"test","cmd":"PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_paper_custody","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["Ran 10 tests in 16.349s","OK"]},"expected":{"exit_code":0,"tail_regex":"Ran 10 tests[\\s\\S]*OK$"}},
    {"id":"V3","kind":"test","cmd":"PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_authentication_io","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["Ran 21 tests in 0.770s","OK"]},"expected":{"exit_code":0,"tail_regex":"Ran 21 tests[\\s\\S]*OK$"}},
    {"id":"V4","kind":"test","cmd":"PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_d165_dominance_closeout","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["Ran 50 tests in 9.677s","OK"]},"expected":{"exit_code":0,"tail_regex":"Ran 50 tests[\\s\\S]*OK$"}},
    {"id":"V5","kind":"test","cmd":"PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v tests.test_analysis_inputs","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["Ran 18 tests in 59.258s","OK"]},"expected":{"exit_code":0,"tail_regex":"Ran 18 tests[\\s\\S]*OK$"}},
    {"id":"V6","kind":"test","cmd":"PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_floor_extraction","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["Ran 169 tests in 3.914s","OK"]},"expected":{"exit_code":0,"tail_regex":"Ran 169 tests[\\s\\S]*OK$"}},
    {"id":"V7","kind":"test","cmd":"PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_whole_window","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["Ran 57 tests in 0.574s","OK"]},"expected":{"exit_code":0,"tail_regex":"Ran 57 tests[\\s\\S]*OK$"}},
    {"id":"V8","kind":"test","cmd":"PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_run_campaign","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["Ran 270 tests in 202.323s","OK"]},"expected":{"exit_code":0,"tail_regex":"Ran 270 tests[\\s\\S]*OK"}},
    {"id":"V9","kind":"smoke","cmd":"python3 -c 'from joulewise.identity_pins import _mint_git_anchor; repo, head = _mint_git_anchor(); print(repo); print(head)'","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["/Users/edr/code/JouleWise-wt-paper-custody","2df32d5c1f28e3f75c93072fcd50b6a9c04b6544"]},"expected":{"exit_code":0,"tail_regex":"2df32d5c1f28e3f75c93072fcd50b6a9c04b6544$"}},
    {"id":"V10","kind":"inspection","cmd":"python3 -c 'import inspect; from joulewise.analysis_engine import inputs; from joulewise.campaign_provenance import load_campaign_log_rows; print(inspect.signature(inputs.load_floor_artifact)); print(inspect.signature(load_campaign_log_rows))'","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["(path: 'Path') -> 'tuple[Mapping[str, Any], str]'","(log_path: 'Path') -> 'list[Mapping[str, Any]] | None'"]},"expected":{"exit_code":0,"tail_regex":"tuple\\[Mapping.*str\\][\\s\\S]*\\(log_path: 'Path'\\)"}},
    {"id":"V11","kind":"smoke","cmd":"python3 -c 'from joulewise.identity_pins import IdentityPinProjectionError, _mint_git_anchor; exec(\"try:\\n _mint_git_anchor()\\nexcept IdentityPinProjectionError as exc:\\n print(exc.reason_code)\\nelse:\\n raise AssertionError(\\\"dirty tree accepted\\\")\")'","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["readiness_identity_environment_dirty"]},"expected":{"exit_code":0,"tail_regex":"^readiness_identity_environment_dirty$"}}
  ],
  "flags": [
    {"id":"FL1","kind":"residual_risk","level":"nonblocking","text":"Only synthetic non-issuing roles exist; no production supplier or live evidence was exercised.","needs":"Keep production issuance blocked through supplier final-head reviews."},
    {"id":"FL2","kind":"verification_gap","level":"nonblocking","text":"The whole suite was not run because the preflight expressly forbade it.","needs":""}
  ]
}
```

## Findings

### F1 — blocker — floor authentication is still downgraded

`joulewise/analysis_engine/inputs.py:953-955` still returns `(authenticated.value, authenticated.file_sha256)`. The executed probe reported `FLOOR_RESULT_TYPES ('dict', 'str')`; `git diff-tree` confirms that file is absent from `git show HEAD`. `campaign_provenance.load_campaign_log_rows` is cured: its only parameter is `log_path` and `tests.test_run_campaign` passed 270 tests.

### F2 — blocker — D-165 ownership is neither single nor exhaustive

`joulewise/d165_dominance_closeout.py` remains Git-tracked and independently defines the four adapter codes and validator. The new core equality test passes and mutation-probes additions to either `D165_CLOSEOUT_REFUSAL_CODES` or `D165_OR01_REASON_SENTENCES`, but it never proves producer→enum containment. Executed with resealed production-shaped fixtures, `build_d165_dominance_closeout` emitted `replay_sidecar.cells: cell census does not match floor artifact`; membership in the alleged closed enum was `False`. Contract F4 is therefore not cured. Execution F5's narrower one-way-test defect is cured.

### F3 — blocker — D-173 still states the superseded caller wire

D-173 exists at `docs/decision_log.md:219,10903-10930`, but lines 10914-10920 still say `In: paths plus expected-digest PINS and receipts`. Addendum 16 permits only a role name and runs root. Restoring the decision without amending those two locations leaves contract F5 incomplete.

## Residual risk

Every reference class was introspected as exactly `('role', 'runs_root')`; no non-test caller constructs one yet. The tracked supply map was ingested inside `V2AuthenticationReadSession` from `git:2df32d5c…:configs/paper_supply/supply_map.json`; an end-to-end clean-tree fixture opened non-issuing. All 24 validator-census members changed the digest under mutation, and malformed-map, nested-session, and all five constructor failures returned closed `paper_custody_*` codes. The contract rewrite cures F7. New defects: none. Same-signature statement: F1-F3 above continue the original bypass, D-165 ownership, and D-173/addendum findings.
