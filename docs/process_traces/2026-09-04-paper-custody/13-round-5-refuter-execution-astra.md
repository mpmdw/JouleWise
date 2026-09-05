```json
{"schema":"claude-codex-report/v1","genre":"review","status":"clean","completion":"complete","summary":"NOT REFUTED under D-161: 53 tests passed, 35 named mutations killed, public synthetic probes fail closed.","workspace":{"base_requested":"01d00591","base_mode":"exact","head_start":"01d005919b62712853ee884bd452d6c491a4169b","head_end":"01d005919b62712853ee884bd452d6c491a4169b","upstream_end":"01d005919b62712853ee884bd452d6c491a4169b","branch":"feat/2026-09-04-paper-custody-seam"},"pathspec":["docs/process_traces/2026-09-04-paper-custody/13-round-5-refuter-execution-astra.md"],"unowned_dirty":["docs/process_traces/2026-09-04-paper-custody/14-round-5-refuter-contract-opus.md"],"verdict":{"result":"NOT REFUTED","findings":[]},"verification":[{"id":"V1","kind":"suite","cmd":"PYTHONDONTWRITEBYTECODE=1 python3 - <<'PY'\nimport pathlib, types, sys, unittest\np=pathlib.Path(\"tests/test_paper_custody.py\")\ns=p.read_text().replace('/ \"tests/fixtures/paper_custody\"\\n            / \".untracked-nongoverned-anchor-probe\"', '/ \"docs/process_traces/2026-09-04-paper-custody\"\\n            / \"13-round-5-refuter-execution-astra.md\"')\nassert s != p.read_text()\nm=types.ModuleType(\"tests.test_paper_custody\"); m.__file__=str(p.resolve())\nsys.modules[m.__name__]=m\nexec(compile(s,m.__file__,\"exec\"),m.__dict__)\nr=unittest.TextTestRunner().run(unittest.defaultTestLoader.loadTestsFromModule(m))\nraise SystemExit(not r.wasSuccessful())\nPY","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["Ran 28 tests in 31.528s","","OK"]},"expected":{"exit_code":0,"tail_regex":"OK"}},{"id":"V2","kind":"suite","cmd":"PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_paper_rendering","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["Ran 3 tests in 0.990s","","OK"]},"expected":{"exit_code":0,"tail_regex":"OK$"}},{"id":"V3","kind":"suite","cmd":"PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_authentication_io","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["Ran 22 tests in 1.362s","","OK"]},"expected":{"exit_code":0,"tail_regex":"OK"}},{"id":"V4","kind":"test","cmd":"PYTHONDONTWRITEBYTECODE=1 python3 - <<'PY'\nimport os,sys,subprocess,runpy,json\nchild=\"import sys,json,runpy,linecache,importlib.abc,importlib.util,unittest\\nfrom pathlib import Path\\nident,rel,old,new,test=json.loads(sys.argv[1])\\nroot=Path.cwd(); path=root/rel; src=path.read_text()\\nassert src.count(old)==1,(ident,src.count(old))\\noverlay={str(path):src.replace(old,new,1).encode()}\\nrb,rt,wb,wt=Path.read_bytes,Path.read_text,Path.write_bytes,Path.write_text\\nPath.read_bytes=lambda p:overlay.get(str(p),rb(p))\\nPath.read_text=lambda p,*a,**k:overlay[str(p)].decode() if str(p) in overlay else rt(p,*a,**k)\\nif rel.endswith(\\\".py\\\"):\\n class Loader(importlib.abc.Loader):\\n  def create_module(self,spec): return None\\n  def exec_module(self,module):\\n   module.__file__=str(path)\\n   s=overlay[str(path)].decode()\\n   linecache.cache[str(path)]=(len(s),None,s.splitlines(True),str(path))\\n   exec(compile(s,str(path),\\\"exec\\\"),module.__dict__)\\n class Finder(importlib.abc.MetaPathFinder):\\n  def find_spec(self,fullname,path=None,target=None):\\n   if fullname==rel[:-3].replace(\\\"/\\\",\\\".\\\"): return importlib.util.spec_from_loader(fullname,Loader())\\n sys.meta_path.insert(0,Finder())\\nif rel!=\\\"configs/paper_supply/supply_map.json\\\":\\n allowed={str(root/\\\"configs/paper_supply/supply_map.json\\\"),str(root/\\\"tests/fixtures/paper_custody/extraction_spec.json\\\")}\\n def write(p,data):\\n  assert str(p) in allowed,str(p)\\n  overlay[str(p)]=data\\n  return len(data)\\n Path.write_bytes=lambda p,data:write(p,data)\\n Path.write_text=lambda p,data,*a,**k:write(p,data.encode())\\n runpy.run_path(\\\"tests/fixtures/paper_custody/repin.py\\\")[\\\"repin\\\"]()\\n Path.write_bytes,Path.write_text=wb,wt\\nr=unittest.TextTestRunner().run(unittest.defaultTestLoader.loadTestsFromName(test))\\nraise SystemExit(not r.wasSuccessful())\\n\"\nrows=runpy.run_path(\"tests/fixtures/paper_custody/run_kills.py\")[\"MUTATIONS\"]\ngood=0\nfor row in rows:\n p=subprocess.run([sys.executable,\"-c\",child,json.dumps(row)],env=dict(os.environ,PYTHONDONTWRITEBYTECODE=\"1\"),stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True)\n lines=p.stdout.strip().splitlines()\n killed=p.returncode==1 and \"FAILED (\" in p.stdout and \"Ran 1 test\" in p.stdout\n good+=killed\n print(json.dumps({\"id\":row[0],\"test\":row[4],\"exit\":p.returncode,\"killed\":killed,\"tail\":lines[-9:]}),flush=True)\nprint(f\"IN-MEMORY KILLS: {good}/{len(rows)}\")\nraise SystemExit(good!=len(rows))\nPY","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["IN-MEMORY KILLS: 35/35"]},"expected":{"exit_code":0,"tail_regex":"IN-MEMORY KILLS: 35/35"}}],"flags":[{"id":"R1","kind":"residual_risk","level":"nonblocking","text":"Authentic production issuance remains unproved; current roles are fixtures.","needs":"Verify real production registration, census and acceptance."}]}
```
## Findings

None under D-161: **NOT REFUTED** for fixture landing. Exact clean starting HEAD; no stop card. V1 relocates its dirty-anchor probe to this allowed report path in memory. Sequential permitted modules: 53 passes, including 109 source/5 grant-policy mutations. V4 repins and mutates only in memory; one truncated F2 tail was recaptured. No discovery, launcher or measurement checkout.

C = tests.test_paper_custody.RoundFiveTests; A = tests.test_authentication_io.PaperRendererBoundaryTests; R = tests.test_paper_rendering.PaperRenderingTests.

1. C.test_issuing_fixture_type_matrix
2. A.test_registered_renderers_require_issuing_boundary
3. R.test_d165_issued_control_and_subject_grants
4. C.test_contract_threat_model_matches_capability_wire
5. C.test_closed_gate_registry
6. C.test_d165_gate_branches_and_floor_acceptance
7. C.test_claim_gate_per_contrast
8. C.test_gate_sources_change_receipt_digest
9. C.test_git_blob_dispatch_checks_blob_before_parse_and_worktree
10. C.test_production_git_blob_coverage
11. C.test_refusal_constructor_ast_census

Every mutation below ran its named test (child exit 1). Exact terminal lines, grouped only where identical; V4 exit 0:

| Mutation(s) | Test | Exact tail |
|---|---:|---|
| F1-wrong-class | 1 | FAILED (errors=1) |
| F1-fixture-inherits-verified | 1 | FAILED (failures=1) |
| F1-wrapper-deleted, F1-annotation-widened, F1-unregistered-renderer | 2 | FAILED (failures=1) |
| F1-grant-check-deleted | 3 | FAILED (failures=1) |
| F2-closure-only-overclaim, F2-tokenless-omitted | 4 | FAILED (failures=1) |
| F3-empty-replay-issues, F3-receipt-issues-fixture, F3-unknown-gate-default | 5 | FAILED (failures=1) |
| F3-fixture-dispatches-gate | 5 | FAILED (errors=1) |
| F3-d165-B-collapsed, F3-d165-null-issues, F3-d165-A-grants-lost, F3-d165-owner-skipped, F3-acceptance-skipped, F3-wrong-floor-accepted | 6 | FAILED (failures=1) |
| F3-claim-ready-flag-trusted, F3-claim-owner-skipped, F3-sidecar-skipped, F3-sidecar-wrong-digest, F3-sidecar-wrong-cell, F3-sidecar-wrong-lineage | 7 | FAILED (failures=1) |
| F3-embedded-floor-skipped, F3-sidecar-wrong-bound | 7 | FAILED (errors=1) |
| F3-source-owner-omitted | 8 | FAILED (failures=1) |
| F4-authority-ignored, F4-blob-comparison-skipped | 9 | FAILED (failures=1) |
| F4-wrong-root | 9 | FAILED (errors=1) |
| F4-fixture-substitute | 10 | FAILED (failures=1) |
| F5-dead-literal, F5-declared-only, F5-undeclared-call, F5-variable-argument | 11 | FAILED (failures=1) |

Public probes used unmodified archived code in temporary synthetic Git repositories, real anchors, no function/registry monkeypatch: 25 Fixture/renderer refusals, five non-null fixture gates refused, five replay→reopen changes refused. Exact selected stdout:

```text
production gate=None/inventory=production => paper_custody_issuance_gate_unregistered
production gate=unknown.v1/inventory=production => paper_custody_issuance_gate_unregistered
production gate=None/inventory=None => paper_custody_receipt_invalid
PUBLIC registered gate raises => paper_custody_validator_refused; validator_codes=('ValueError',); output=()
wrong grant subject => paper_custody_binding_mismatch
missing outcome grant => paper_custody_not_issuable
wrong floor => paper_custody_issuance_prerequisite_missing
stale anchor => paper_custody_issuance_prerequisite_missing
missing acceptance => paper_custody_issuance_prerequisite_missing
PUBLIC copy/pickle/replace/constructor routes: 90 refusals; zero output
```

Acceptance control passed; stale anchor was an unrelated real commit. AST scratch kills produced `refusal constructor/registry/contract census mismatch` (constructor replaced by dead literal) and `refusal constructor requires a literal first argument` (variable argument).

Requested `git diff origin/main -- tests/fixtures/paper_custody configs/paper_supply`: five additions. supply_map.json supplies five fixture rows/v2 gates/census/pending role; extraction_spec.json is synthetic Git-blob input; family_catalog.json lists families; repin.py refreshes envelopes; run_kills.py defines mutations. Round 5 vs 55d3bbbe leaves catalog unchanged, upgrades map v1→v2, repins receipt/inventory hashes, relocates extraction input with unchanged digest, adds the other three files. No existing v1 fixture or frozen evidence bytes changed.

## Residual risk

Production replay→mint on authentic evidence remains unproved; owner-policy controls mock authentication. Claim/F6 gates stay absent. Lead must verify production registration.

Explicit `inspect.unwrap(renderer)` returns `'admitted'` / `'diagnostic projection'` from whole-window/transfer bodies for all five fixtures. Deliberate decorator bypass is outside D-161; verdict does not promise tamper-proof Python.

