```json
{
  "verdict": {
    "gauntlet": "ACCEPT WITH ONE DOCUMENTATION FIX",
    "same_signature": "No original refuter or delta finding survives with the same signature; F1 is a new API-notation mismatch, not the former caller-authority defect.",
    "new_defects": ["F1"],
    "dispositions": [
      {"id":"execution/F1","status":"CURED","evidence":"V9-V10: authenticated fixed map; dirty anchor refused."},
      {"id":"execution/F2","status":"CURED","evidence":"V3-V4: both lower bypass regressions pass."},
      {"id":"execution/F3","status":"CURED","evidence":"V2: every dispatcher/owner mutation changes the digest."},
      {"id":"execution/F4","status":"CURED","evidence":"V2: five direct constructors refuse."},
      {"id":"execution/F5","status":"CURED","evidence":"V5-V6,V11: producer/enum/map guards pass."},
      {"id":"contract/F1","status":"CURED","evidence":"V9-V10: clean anchor passes; dirty anchor refuses."},
      {"id":"contract/F2","status":"CURED","evidence":"V3: five refs are exactly role+runs_root."},
      {"id":"contract/F3","status":"CURED","evidence":"V3-V4: raw_bytes and Mapping+digest are gone."},
      {"id":"contract/F4","status":"CURED","evidence":"V5-V6,V11: shim gone; enum/map closed."},
      {"id":"contract/F5","status":"CURED","evidence":"D-173 authority wording is restored; see new F1."},
      {"id":"contract/F6","status":"CURED","evidence":"V2: boundary failures are closed refusals."},
      {"id":"contract/F7","status":"CURED","evidence":"Manual first-use and required-term inspection pass."},
      {"id":"delta/F1","status":"CURED","evidence":"V4: authenticated floor capability preserved."},
      {"id":"delta/F2","status":"CURED","evidence":"V5-V6,V11: one exhaustive D-165 owner."},
      {"id":"delta/F3","status":"CURED","evidence":"D-173 now assigns paths/digests to the repository."}
    ],
    "findings": [
      {"id":"F1","severity":"should_fix","file_line":"docs/decision_log.md:10915","text":"The detailed D-173 body spells open_paper_input(role, runs_root), but ruling 15, the normative contract, and all six public signatures expose open_paper_input(ref), where the five closed ref types carry role and runs_root.","counterfactual":"The documented two-argument form raised raw TypeError before the custody boundary.","cure_shape":"Change only the call notation to open_paper_input(ref), retaining the next sentence that limits ref fields to role and runs_root."}
    ]
  },
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "All twelve original and three round-1 delta findings are cured; one new should-fix D-173 API-notation mismatch remains.",
  "workspace": {"base_requested":"2df32d5c","base_mode":"exact","head_start":"2e3349e1f412349638c578b56a9927824fc4713d","head_end":"2e3349e1f412349638c578b56a9927824fc4713d","upstream_end":"2e3349e1f412349638c578b56a9927824fc4713d","branch":"feat/2026-09-04-paper-custody-seam"},
  "pathspec": ["docs/process_traces/2026-09-04-paper-custody/07-delta-reaudit-round-2.md"],
  "unowned_dirty": [],
  "verification": [
    {"id":"V1","kind":"inspection","cmd":"test \"$(git rev-parse HEAD)\" = 2e3349e1f412349638c578b56a9927824fc4713d && test \"$(git merge-base 2df32d5c HEAD)\" = 2df32d5c1f28e3f75c93072fcd50b6a9c04b6544 && git diff --check 2df32d5c..HEAD && git rev-parse --short=8 HEAD","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["2e3349e1"]},"expected":{"exit_code":0,"tail_regex":"^2e3349e1$"}},
    {"id":"V2","kind":"test","cmd":"PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_paper_custody","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["Ran 10 tests in 17.343s","OK"]},"expected":{"exit_code":0,"tail_regex":"Ran 10 tests[\\s\\S]*OK$"}},
    {"id":"V3","kind":"test","cmd":"PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_authentication_io","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["Ran 21 tests in 0.985s","OK"]},"expected":{"exit_code":0,"tail_regex":"Ran 21 tests[\\s\\S]*OK$"}},
    {"id":"V4","kind":"test","cmd":"PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_analysis_inputs","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["Ran 19 tests in 60.835s","OK"]},"expected":{"exit_code":0,"tail_regex":"Ran 19 tests[\\s\\S]*OK$"}},
    {"id":"V5","kind":"test","cmd":"PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_dominance_closeout","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["Ran 3 tests in 1.749s","OK"]},"expected":{"exit_code":0,"tail_regex":"Ran 3 tests[\\s\\S]*OK$"}},
    {"id":"V6","kind":"test","cmd":"PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_d165_dominance_closeout","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["Ran 50 tests in 10.818s","OK"]},"expected":{"exit_code":0,"tail_regex":"Ran 50 tests[\\s\\S]*OK$"}},
    {"id":"V7","kind":"test","cmd":"PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_floor_extraction","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["Ran 169 tests in 4.024s","OK"]},"expected":{"exit_code":0,"tail_regex":"Ran 169 tests[\\s\\S]*OK$"}},
    {"id":"V8","kind":"test","cmd":"PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_whole_window","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["Ran 57 tests in 0.564s","OK"]},"expected":{"exit_code":0,"tail_regex":"Ran 57 tests[\\s\\S]*OK$"}},
    {"id":"V9","kind":"inspection","cmd":"PYTHONDONTWRITEBYTECODE=1 python3 -c \"from joulewise import paper_custody as c; from joulewise.authentication_io import V2AuthenticationReadSession; from joulewise.identity_pins import _mint_git_anchor; r,h=_mint_git_anchor(); s=V2AuthenticationReadSession(); s.__enter__(); c._load_supply_entry(s,r,h,'fixture.reported_energy_parents',c._FAMILY_SPECS[c.ReportedEnergyParentsRef]); key=f'git:{h}:{c._SUPPLY_MAP_PATH}'; assert key in s.records; s.__exit__(None,None,None); print('SUPPLY_MAP_AUTHENTICATED',h,key)\" && git ls-files --error-unmatch configs/paper_supply/supply_map.json","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["SUPPLY_MAP_AUTHENTICATED 2e3349e1f412349638c578b56a9927824fc4713d git:2e3349e1f412349638c578b56a9927824fc4713d:configs/paper_supply/supply_map.json","configs/paper_supply/supply_map.json"]},"expected":{"exit_code":0,"tail_regex":"SUPPLY_MAP_AUTHENTICATED 2e3349e1.*supply_map.json[\\s\\S]*configs/paper_supply/supply_map.json$"}},
    {"id":"V10","kind":"smoke","cmd":"probe_dir=$(mktemp -d /private/tmp/jw-paper-custody-dirty.XXXXXX)\ngit clone --quiet --no-hardlinks /Users/edr/code/JouleWise-wt-paper-custody \"$probe_dir/repo\"\ngit -C \"$probe_dir/repo\" update-index --force-remove README.md\nprobe_output=$(cd \"$probe_dir/repo\" && PYTHONDONTWRITEBYTECODE=1 python3 -c 'from joulewise.identity_pins import _mint_git_anchor; _mint_git_anchor()' 2>&1)\nprobe_status=$?\ntest \"$probe_status\" -ne 0\ncase \"$probe_output\" in *'requires a clean Git working tree'*) echo 'DIRTY_ANCHOR_REFUSED clean-tree' ;; *) echo \"$probe_output\"; exit 1 ;; esac","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["DIRTY_ANCHOR_REFUSED clean-tree"]},"expected":{"exit_code":0,"tail_regex":"^DIRTY_ANCHOR_REFUSED clean-tree$"}},
    {"id":"V11","kind":"inspection","cmd":"test -z \"$(git ls-files joulewise/d165_dominance_closeout.py)\" && ! rg -n 'from joulewise\\.d165_dominance_closeout|import joulewise\\.d165_dominance_closeout|from \\.d165_dominance_closeout' joulewise scripts tests --glob '*.py' && echo SHIM_DELETED_NO_IMPORTS","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["SHIM_DELETED_NO_IMPORTS"]},"expected":{"exit_code":0,"tail_regex":"^SHIM_DELETED_NO_IMPORTS$"}}
  ],
  "flags": [
    {"id":"FL1","kind":"residual_risk","level":"nonblocking","text":"Only synthetic non-issuing roles were exercised; production supplier issuance remains intentionally blocked.","needs":"Keep issuance blocked through each supplier's final-head review and the paper-supply cold gate."},
    {"id":"FL2","kind":"verification_gap","level":"nonblocking","text":"The repository-wide suite was not run because the preflight explicitly forbade it.","needs":""}
  ]
}
```

## Findings

### F1 — should_fix — D-173 names a nonexistent two-argument API

`docs/decision_log.md:10915` says
`open_paper_input(role, runs_root)`. The binding ruling, normative contract, and
implementation instead expose `open_paper_input(ref)`; each of the five closed
reference types contains exactly `role` and `runs_root`. Direct inspection
covered every public signature; executing the D-173 spelling raised `TypeError`
before custody exception translation could run. Change only the call notation
to `open_paper_input(ref)`; the role-plus-runs-root authority rule is correct.

All original findings are cured. V9 authenticated the tracked supply map via
`V2AuthenticationReadSession` at `2e3349e1`; V10 dirtied a temporary clone and
proved `_mint_git_anchor` refused it. V3/V4 plus the direct signatures at
`campaign_provenance.py:453` and `analysis_engine/inputs.py:945` close both
lower bypasses: no `raw_bytes` channel remains, and the floor loader returns the
authenticated object rather than a mapping/digest projection. V5/V6/V11 prove
the bench deletion has no Python importer and the real D-165 producer's 25-code
enumeration equals the registry map in both directions. V2 mutation-checks all
dispatcher-plus-owner members in every validator-source census and exercises
closed `paper_custody_*` exception translation. Manual first-use and required-term
review confirms the normative contract defines its terms and states the exact
map location/schema, role lookup, authentication session, and clean-tree
anchor.

Same-signature statement: no prior finding survives or regressed. F1 is new
and limited to an incorrect interface spelling in the D-173 mirror; it does not
reopen caller-selected paths, digests, bytes, mappings, or receipts.

## Residual risk

The five roles remain synthetic and non-issuing. No production paper value,
live run, hardware evidence, or quiet-machine measurement was exercised. The
whole suite was intentionally not run under the supplied preflight rule; every
permitted relevant module was run separately.
