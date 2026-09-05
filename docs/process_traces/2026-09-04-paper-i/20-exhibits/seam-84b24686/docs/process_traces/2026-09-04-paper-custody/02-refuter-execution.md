```json
{
  "verdict": {
    "gauntlet": "NOT LANDABLE",
    "findings": [
      {"id":"F1","severity":"blocker","file_line":"joulewise/paper_custody.py:88","text":"Callers choose paths, digests, inventory, receipt, and Git root; the opener never uses the ruled clean-tree _mint_git_anchor supply map.","counterfactual":"A dirty fresh fixture worktree still returned VerifiedReportedEnergyParents.","cure_shape":"Land addendum 5; accept only role+runs-root, resolve the repository supply map internally, and use _mint_git_anchor."},
      {"id":"F2","severity":"blocker","file_line":"joulewise/campaign_provenance.py:453","text":"Both ruled lower bypasses remain: caller raw_bytes and load_floor_artifact's mapping/digest downgrade at inputs.py:953.","counterfactual":"A disk source=disk log returned the injected source=caller row.","cure_shape":"Remove raw_bytes; preserve or require the seam capability at the floor API; add negative boundary tests."},
      {"id":"F3","severity":"blocker","file_line":"joulewise/paper_custody.py:373","text":"validator_source_sha256 hashes only _replay_family, excluding its dispatcher and owning validators.","counterfactual":"Replacing _validate_production_documents left the digest unchanged.","cure_shape":"Hash a closed per-family census of governed replay/adapter source bytes and mutation-test every member."},
      {"id":"F4","severity":"should_fix","file_line":"joulewise/paper_custody.py:172","text":"All five exported Verified* classes allow empty public construction.","counterfactual":"Each Verified*() succeeded without evidence or payload.","cure_shape":"Make normal construction raise; keep the private factory and add five refusal tests."},
      {"id":"F5","severity":"should_fix","file_line":"tests/test_d165_dominance_closeout.py:2068","text":"The D-165 test uses assertIn; it does not enforce enum↔registry-map equality.","counterfactual":"An extra d165_paper_future_unmapped code left the test green.","cure_shape":"Assert exact bidirectional equality and mutation-probe additions on both sides."}
    ]
  },
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "The prescribed tests and five-family attack census pass, but the seam misses the binding clean-tree supply-map design, leaves both ruled lower bypasses open, and has two forge/drift gaps.",
  "workspace": {"base_requested":"b700ac4e","base_mode":"exact","head_start":"b700ac4ef08ca29963991b8d5e29217effe25656","head_end":"b700ac4ef08ca29963991b8d5e29217effe25656","upstream_end":"b700ac4ef08ca29963991b8d5e29217effe25656","branch":"feat/2026-09-04-paper-custody-seam"},
  "pathspec": ["docs/process_traces/2026-09-04-paper-custody/02-refuter-execution.md"],
  "unowned_dirty": [],
  "verification": [
    {"id":"V1","kind":"inspection","cmd":"test \"$(git rev-parse HEAD)\" = b700ac4ef08ca29963991b8d5e29217effe25656 && test -z \"$(git status --porcelain --untracked-files=no)\" && git rev-parse --short=8 HEAD","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["b700ac4e"]},"expected":{"exit_code":0,"tail_regex":"^b700ac4e$"}},
    {"id":"V2","kind":"suite","cmd":"python3 -m unittest tests.test_paper_custody tests.test_authentication_io tests.test_d165_dominance_closeout tests.test_floor_extraction tests.test_whole_window","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["OK"]},"expected":{"exit_code":0,"tail_regex":"OK$"}},
    {"id":"V3","kind":"test","cmd":"python3 -m unittest -v tests.test_paper_custody.PaperCustodyCensusTests.test_every_family_actual_read_census_refuses_all_three_attack_arms","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["OK"]},"expected":{"exit_code":0,"tail_regex":"OK$"}},
    {"id":"V4","kind":"smoke","cmd":"python3 -c \"from joulewise import paper_custody as c; cs=(c.VerifiedReportedEnergyParents,c.VerifiedD165Closeout,c.VerifiedWholeWindowVerdict,c.VerifiedClaimEvidence,c.VerifiedTransferProjection); exec('def reject(x):\\n try: c.open_paper_input(x)\\n except c.PaperCustodyRefusal as e:\\n  assert e.code == \\\"paper_custody_request_invalid\\\" and e.rendered_output == (); return e.code\\n raise AssertionError(\\\"accepted\\\")'); rows=[reject(x) for cls in cs for x in ({},b'{}',object.__new__(cls))]; assert len(rows)==15; print('SUPPLIER_SHAPES_REFUSED',len(rows))\"","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["SUPPLIER_SHAPES_REFUSED 15"]},"expected":{"exit_code":0,"tail_regex":"^SUPPLIER_SHAPES_REFUSED 15$"}},
    {"id":"V5","kind":"smoke","cmd":"python3 -c \"from tests.test_paper_custody import _FamilyFixture; from joulewise import paper_custody as c; f=_FamilyFixture('reported_energy_parents'); (f.root/'untracked').write_text('dirty\\\\n'); o=c.open_paper_input(f.ref); assert type(o) is c.VerifiedReportedEnergyParents; print('DIRTY_TREE_ACCEPTED',type(o).__name__); f.close()\"","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["DIRTY_TREE_ACCEPTED VerifiedReportedEnergyParents"]},"expected":{"exit_code":0,"tail_regex":"^DIRTY_TREE_ACCEPTED VerifiedReportedEnergyParents$"}},
    {"id":"V6","kind":"inspection","cmd":"python3 -c \"import inspect,tempfile; from pathlib import Path; from joulewise.analysis_engine.inputs import load_floor_artifact as f; from joulewise.campaign_provenance import load_campaign_log_rows as c; d=tempfile.TemporaryDirectory(); p=Path(d.name)/'campaign_log.jsonl'; p.write_bytes(b'{\\\"source\\\":\\\"disk\\\"}\\\\n'); r=c(p,raw_bytes=b'{\\\"source\\\":\\\"caller\\\"}\\\\n'); assert r==[{'source':'caller'}]; print('LOWER_BYPASS',r[0]['source'],inspect.signature(f).return_annotation); d.cleanup()\"","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["LOWER_BYPASS caller tuple[Mapping[str, Any], str]"]},"expected":{"exit_code":0,"tail_regex":"^LOWER_BYPASS caller tuple\\[Mapping.*str\\]$"}},
    {"id":"V7","kind":"inspection","cmd":"for custody_rev in origin/main HEAD; do git ls-tree -r --name-only origin/main tests/fixtures | while IFS= read -r custody_path; do git show \"${custody_rev}:${custody_path}\" | shasum -a 256 | awk '{print $1}'; done | shasum -a 256 | awk -v rev=\"$custody_rev\" '{print rev,$1}'; done; git diff --name-status origin/main..HEAD -- tests/fixtures; shasum -a 256 tests/fixtures/paper_custody/family_catalog.json","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["origin/main 0b5d5b4a5be73b3546534547f1b6fb244317e67c0e17249eea2577b72f1744f0","HEAD 0b5d5b4a5be73b3546534547f1b6fb244317e67c0e17249eea2577b72f1744f0","A\ttests/fixtures/paper_custody/family_catalog.json","ed2301b2f7ef003ae14e5419eeabae1a9223f1d5f4a4055f561e3f853a519f04  tests/fixtures/paper_custody/family_catalog.json"]},"expected":{"exit_code":0,"tail_regex":"origin/main ([0-9a-f]{64})[\\s\\S]*HEAD \\1[\\s\\S]*family_catalog.json"}},
    {"id":"V8","kind":"lint","cmd":"python3 -m unittest -v tests.test_authentication_io.AuthenticationSurfaceGuardTests.test_marked_v2_surface_has_no_direct_readable_io tests.test_authentication_io.AuthenticationSurfaceGuardTests.test_guard_distinguishes_readable_and_output_only_open","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["OK"]},"expected":{"exit_code":0,"tail_regex":"OK$"}}
  ],
  "flags": [
    {"id":"FL1","kind":"baseline_drift","level":"blocking","text":"Required addendum 16 is absent from b700ac4e; reviewed from local 913bf3f7, not an ancestor of HEAD.","needs":"Rebase/merge the addendum and current origin/main before delta review."},
    {"id":"FL2","kind":"residual_risk","level":"nonblocking","text":"Execution used synthetic non-issuing fixtures; no production or live evidence ran.","needs":"Keep issuance blocked through producer final-head review."}
  ]
}
```

## Findings

### F1 — blocker — caller-selected authority and no clean-tree gate

File: `joulewise/paper_custody.py:88`. Text: all family refs expose `BoundFile` paths and expected digests, while `open_paper_input` accepts a caller-selected Git root and `_git_blob` uses `git show`; it never invokes the addendum-5-mandated `identity_pins._mint_git_anchor`. The normative contract repeats the superseded caller-pin wire at `docs/contracts/paper_supply_custody.md:20-22,51-58`.

Counterfactual: a fresh fixture worktree with an untracked dirty file returned `VerifiedReportedEnergyParents`. Cure shape: callers provide only a closed role and runs root; the seam resolves the supply map internally from the fixed, clean `_mint_git_anchor` checkout. Land the missing addendum and reconcile the contract.

### F2 — blocker — the two expressly ruled lower bypasses remain open

File: `joulewise/campaign_provenance.py:453`. Text: `load_campaign_log_rows(..., raw_bytes=...)` still accepts caller-substituted bytes, and `joulewise/analysis_engine/inputs.py:953` still converts authenticated floor evidence to `(Mapping, digest)`. This directly contradicts ruling 15 line 10 and addendum 5 line 9; the landing report itself records the miss at lines 46-54.

Counterfactual: disk said `source=disk`, but the loader returned the injected `source=caller` row. Cure shape: remove the byte channel and require/preserve a seam-issued typed floor capability, with negative boundary tests.

### F3 — blocker — receipt validator-source digest omits validator implementations

File: `joulewise/paper_custody.py:373`. Text: the digest covers only the small `_replay_family` wrapper. It excludes `_validate_production_documents` and every owning validator it dispatches to.

Counterfactual: replacing the production replay implementation left the digest unchanged. Cure shape: hash a closed, per-family census of governed validator and adapter source bytes, and mutation-test every member.

### F4 — should_fix — verified tokens have public empty constructors

File: `joulewise/paper_custody.py:172`. Text: every exported `Verified*` dataclass has `init=False` but no refusing initializer, so ordinary `VerifiedClaimEvidence()`-style construction succeeds without evidence or payload.

Counterfactual: all five empty instances were created. Cure shape: make normal construction raise and retain only the private factory, with one constructor-refusal test per type.

### F5 — should_fix — D-165 total-map guard is one-directional

File: `tests/test_d165_dominance_closeout.py:2068`. Text: four expected codes are checked with `assertIn`; no registry map is compared and an extra enum code is invisible.

Counterfactual: `d165_paper_future_unmapped` was added under a patch and the named test stayed green. Cure shape: assert exact enum↔registry-key equality and mutation-probe additions on both sides.

## Residual risk

The five-family census used fresh synthetic Git fixtures and proved, for every actual census record, raw flip → `paper_custody_digest_mismatch`, full caller reseal → `paper_custody_anchor_mismatch`, and replay/reopen replacement → `paper_custody_input_changed`, always with zero output. Dict, bytes, and prevalidated shapes were refused for all five family types. The 184 pre-existing fixture files had identical aggregate SHA-256 at `origin/main` and HEAD; only the new catalog exists. Production issuance remains deliberately blocked and was not exercised. The repository-wide suite was not run because the preflight expressly limited this seat to the five named modules.
