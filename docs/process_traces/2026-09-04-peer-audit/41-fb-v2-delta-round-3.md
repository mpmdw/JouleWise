```json
{"schema":"claude-codex-report/v1","genre":"review","status":"findings","completion":"complete","summary":"NOT LANDABLE: R3 closed; malformed rule_id crashes the floor version census.","workspace":{"base_requested":"fd054a48","base_mode":"exact","head_start":"fd054a48adce6939e1361abfeb4c579827ad3811","head_end":"fd054a48adce6939e1361abfeb4c579827ad3811","upstream_end":"5b978884b743fa3f71504f2bcf17555983ab2ed1","branch":"feat/2026-09-04-fb-metadata"},"pathspec":["docs/process_traces/2026-09-04-peer-audit/41-fb-v2-delta-round-3.md"],"unowned_dirty":[],"verdict":{"decision":"NOT LANDABLE","findings":[{"id":"R4","severity":"blocker","path":"joulewise/detection_floor.py","line":4316,"title":"Malformed rule_id escapes named refusal"}]},"verification":[{"id":"V1","kind":"test","cmd":"PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_detection_floor","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["OK (skipped=1)"]},"expected":{"exit_code":0,"tail_regex":"OK \\(skipped=1\\)$"}},{"id":"V2","kind":"test","cmd":"PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_analysis_claims","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["OK"]},"expected":{"exit_code":0,"tail_regex":"OK$"}},{"id":"V3","kind":"test","cmd":"PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_floor_extraction","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["OK"]},"expected":{"exit_code":0,"tail_regex":"OK$"}},{"id":"V4","kind":"test","cmd":"PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_mint_floor_artifact","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["OK"]},"expected":{"exit_code":0,"tail_regex":"OK$"}},{"id":"V5","kind":"test","cmd":"PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_d165_dominance_closeout","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["OK"]},"expected":{"exit_code":0,"tail_regex":"OK$"}},{"id":"V6","kind":"test","cmd":"PYTHONDONTWRITEBYTECODE=1 python3 - <<'PY'\nimport json,subprocess\nfrom pathlib import Path\nr=json.loads(Path('docs/process_traces/2026-09-04-peer-audit/40-fb-v2-round-4-report.md').read_text().split('```')[1][5:])\nsubprocess.run(next(v['cmd'] for v in r['verification'] if v['id']=='V6'),shell=True,check=True)\nPY","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["Mutation ran in memory; repository source unchanged"]},"expected":{"exit_code":0,"tail_regex":"source unchanged$"}},{"id":"V7","kind":"smoke","cmd":"PYTHONDONTWRITEBYTECODE=1 python3 - <<'PY'\nimport json\nfrom tests.test_mint_floor_artifact import make_artifact\nfrom joulewise.analysis_engine.inputs import authenticate_floor_artifact_bytes\na=make_artifact();a['cells'][0]['single_count_discipline']['rule_id']=[]\nauthenticate_floor_artifact_bytes(json.dumps(a).encode())\nPY","cwd":".","observed":{"result":"fail","exit_code":1,"tail":["TypeError: cannot use 'list' as a set element (unhashable type: 'list')"]},"expected":{"exit_code":1,"tail_regex":"AnalysisInputError: invalid floor artifact:"}}],"flags":[]}
```

## Findings

**R4 (blocker):** detection_floor.py:4316 hashes unchecked rule_id values. A valid artifact with cell discipline ID [] or {} raises TypeError; V7 shows byte admission loses AnalysisInputError. Introduced by 23f19012; no acceptance bypass. Census validated IDs, retain errors; regress both shapes at all carriers/admission.

**R3 CLOSED:** V4 covers v1/v2 localized refusal and absent outputs. Named MintErrors: `artifact single-count discipline is not canonical`; `artifact mixes single-count discipline rule versions`. V6 restores the parent renderer: localized-corruption test: 52 MintError-not-raised failures, zero errors; source untouched.

Fresh rg census of discipline keys, formulas and renderer across joulewise/, scripts/, docs/site, then callers: eight Python files + HTML. df=detection_floor.py, ae=analysis_engine/, m=scripts/mint_floor_artifact.py, g=scripts/mint_floor_artifact_generalized.py; other paths under joulewise/. “Preserve” means exact frozen v1 / planning v2.

| Reader | v1 / v2 | Mixture / malformed |
|---|---|---|
| df:400 predicate | accept / accept | one object / false |
| df:3396 component,3886 cell,4164 group | validate / validate | parent-child errors / errors |
| df:4328 version census | retain / retain | mixed-ID error / R4; non-Mapping omission retains earlier errors |
| ae/inputs.py:895 admission;4341,4380 exact;4474,4519 transport | preserve / preserve | admission rejects mixtures, inherits R4; pure resolver checks selected metadata only, malformed → artifact_schema_invalid |
| ae/__init__.py:234,263 admission;287,298,335 copies;1287 forwarding | preserve / preserve | AnalysisInputError before copies; malformed: floor_resolution_single_count_discipline_invalid |
| ae/claims.py:303,316 | preserve / preserve | mixture upstream / floor_artifact_invalid, not_estimable, readiness false |
| ae/artifact.py:490,2281 metadata;2513 versions;2612 copies | validate / validate | errors for both; finalize/write:3584,3599 raise ClaimArtifactError |
| floor_extraction.py:1431,3120;1470,1495,1598 vocabulary | emits v2, no version selection | keys only; no body validation |
| m:1914,1950,1957,2016 | legacy / planning prose | named MintError before writes; validation inherits R4 |
| g:1716,3948,4188,4197 | delegates both | writers refuse before output; validation inherits R4 |
| scripts/build_site.py:2060 → docs/site/adapter_contracts.html | renders v1 / v2 text | no JSON discipline admission |

Rounds 2, 3 and 4 each found one missed consumer. **Class NOT CLOSED:** another malformed shape fails. No persistent discipline-consumer census test exists. Structural cure: enumerate direct/indirect readers with v1/v2, mixed and localized-malformed probes; predicate counts miss R4.

## Residual risk

480 tests, one skip; sequential, no discovery/agent launch/hardware. Site build not rerun. V4 pins historical bytes/prose. Next: lead fixes R4, adds census coverage, reruns delta.
