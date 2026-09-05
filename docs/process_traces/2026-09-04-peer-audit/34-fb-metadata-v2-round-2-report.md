```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "clean",
  "completion": "complete",
  "summary": "Implemented the ratified single-count discipline v2, preserved and accepted frozen v1 bytes, migrated all ten consumers, refused mixtures, and regenerated the contract HTML.",
  "workspace": {"base_requested":"ed0b93b4","base_mode":"exact","head_start":"ed0b93b49ae8aacbd295989f940d24c5a23a6564","head_end":"ed0b93b49ae8aacbd295989f940d24c5a23a6564","upstream_end":"82636d67f4ceb9563548a5e417bd92712ded533d","branch":"feat/2026-09-04-fb-metadata"},
  "pathspec": ["docs/contracts/adapter_contracts.md","docs/phase_2/detection_floor.md","docs/site/adapter_contracts.html","joulewise/analysis_engine/__init__.py","joulewise/analysis_engine/artifact.py","joulewise/analysis_engine/claims.py","joulewise/analysis_engine/inputs.py","joulewise/detection_floor.py","scripts/mint_floor_artifact.py","tests/test_analysis_claims.py","tests/test_detection_floor.py","tests/test_floor_extraction.py","tests/test_mint_floor_artifact.py","docs/process_traces/2026-09-04-peer-audit/34-fb-metadata-v2-round-2-report.md"],
  "unowned_dirty": [],
  "verdict": {"implementation":"implemented","acceptance":"ready"},
  "verification": [
    {"id":"V1","kind":"inspection","cmd":"git fetch origin main","cwd":".","observed":{"result":"fail","exit_code":255,"tail":["error: cannot open '/Users/edr/code/JouleWise/.git/worktrees/JouleWise-wt-fb-metadata/FETCH_HEAD': Operation not permitted"]},"expected":{"exit_code":0,"tail_regex":"^$"}},
    {"id":"V2","kind":"inspection","cmd":"git show ff82e0dd:docs/process_traces/2026-09-04-peer-audit/43-magistrate-synthesis-gate-17.md | sed -n '7,11p'","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["| Q-17-3 | AFFIRM | D-083 addendum ratifiable verbatim; max(F, h+B) exact with strict inequalities at both boundaries (41 §1). Census corrected per 42: TEN exact-equality object sites (not seven); the key appears in 4 of the 17 fill-rehearsal JSONs; df-ph-decode-floor-mint1.json and docs/site/adapter_contracts.html are consumers too. |","| Q-17-4 | AMEND | Prompt-0 contrast AFFIRMED as better-defensible. D-166 sentence substituted: \"Regenerate every artifact whose identity, digest or custody pin derives from the decode prompt selection — at minimum contrast configs, suite manifests, identities, projections and custody pins, including expected_pack_paths() pack-level objects and the D-138 successor-generation requirement — as enumerated by a dependency census recorded in the supersession record before collection, and rerun the required clone proof.\" |"]},"expected":{"exit_code":0,"tail_regex":"Q-17-4 .* AMEND"}},
    {"id":"V3","kind":"test","cmd":"PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_detection_floor","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["----------------------------------------------------------------------","Ran 161 tests in 2.691s","","OK (skipped=1)"]},"expected":{"exit_code":0,"tail_regex":"OK \\(skipped=1\\)"}},
    {"id":"V4","kind":"test","cmd":"PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_analysis_claims","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["----------------------------------------------------------------------","Ran 62 tests in 0.314s","","OK"]},"expected":{"exit_code":0,"tail_regex":"OK"}},
    {"id":"V5","kind":"test","cmd":"PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_floor_extraction","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["----------------------------------------------------------------------","Ran 168 tests in 3.995s","","OK"]},"expected":{"exit_code":0,"tail_regex":"OK"}},
    {"id":"V6","kind":"test","cmd":"PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_mint_floor_artifact","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["----------------------------------------------------------------------","Ran 39 tests in 0.987s","","OK"]},"expected":{"exit_code":0,"tail_regex":"OK"}},
    {"id":"V7","kind":"test","cmd":"PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_d165_dominance_closeout","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["----------------------------------------------------------------------","Ran 47 tests in 10.850s","","OK"]},"expected":{"exit_code":0,"tail_regex":"OK"}},
    {"id":"V8","kind":"test","cmd":"temporary apply_patch claims.py:336 from floor to floor + derived B; PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_analysis_claims; apply_patch restore","cwd":".","observed":{"result":"pass","exit_code":1,"tail":["----------------------------------------------------------------------","Ran 62 tests in 0.317s","","FAILED (failures=2)"]},"expected":{"exit_code":1,"tail_regex":"FAILED \\(failures=2\\)"}},
    {"id":"V9","kind":"build","cmd":"PYTHONDONTWRITEBYTECODE=1 python3 - <<'PY'\nfrom scripts import build_site\ndoc = next(item for item in build_site.BASE_DOC_PAGES if item.source == 'docs/contracts/adapter_contracts.md')\nbuild_site.write(build_site.OUT / doc.out_name, build_site.render_doc_page(doc, False, build_site.git_source_stamp(doc.source)))\nprint(f'built {doc.source} -> docs/site/{doc.out_name}')\nPY","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["build_site.py: WARNING: pinned Marked is unavailable; using offline fallback markdown renderer.","built adapter_contracts.html","built docs/contracts/adapter_contracts.md -> docs/site/adapter_contracts.html"]},"expected":{"exit_code":0,"tail_regex":"built docs/contracts/adapter_contracts.md -> docs/site/adapter_contracts.html"}},
    {"id":"V10","kind":"inspection","cmd":"git diff --check","cwd":".","observed":{"result":"pass","exit_code":0,"tail":[]},"expected":{"exit_code":0,"tail_regex":"^$"}}
  ],
  "flags": [
    {"id":"F1","kind":"environment","level":"nonblocking","text":"The requested fetch could not update FETCH_HEAD because linked-worktree Git metadata is outside the writable sandbox; the locally available gate records were read at commits 60c6b558 and ff82e0dd, and origin/main resolved to 82636d67.","needs":"Lead may confirm remote freshness outside this sandbox."}
  ]
}
```

## Change

`SINGLE_COUNT_DISCIPLINE_ID` now emits `.v2` with the ratified planning expression, two-role flag, non-gating role, explicit non-acceptance flag, and one-sentence two-gate note. The exact historical v1 object remains available through version dispatch. Consumers preserve the validated carried object instead of normalizing v1 to v2; floor-artifact, claim-artifact, aggregation, and prose paths refuse mixed rule versions.

The carrier census is 17 fill-rehearsal JSONs, 4 containing the key. The four are frozen synthetic fixtures with no repository producer and were not edited. Their SHA-256 values remain `5bd4d748…9575755`, `ecea77fc…28c9`, `06f9b63d…77a066`, and `da611926…b90c1`. Root `df-ph-decode-floor-mint1.json`, produced by `scripts/mint_floor_artifact.py`, remains frozen v1 at `559ab5ed…1188a8`; it validates with zero errors and renders through the v1 prose branch. `docs/site/adapter_contracts.html` was regenerated only for its source page through `scripts/build_site.py` and contains both exact versioned objects.

The v2 producer/propagation census is `joulewise/detection_floor.py:900,1713,1800` and `joulewise/floor_extraction.py:1433,3121`. These five are emitters, not additional equality consumers.

## Clause map

| Exact consumer site | Role | Biting assertion | Counterfactual |
|---|---|---|---|
| `joulewise/detection_floor.py:3388` | component record | `tests/test_detection_floor.py:2169` | hard-code current v2 equality; frozen v1 artifact fails |
| `joulewise/detection_floor.py:3878` | cell | `tests/test_detection_floor.py:2169` | accept canonical objects independently without matching component version; mixture passes |
| `joulewise/detection_floor.py:4156` | transport group | `tests/test_detection_floor.py:2169` | accept canonical objects independently without matching source-cell version; mixture passes |
| `joulewise/analysis_engine/artifact.py:490` | claim artifact metadata | `tests/test_analysis_claims.py:504` | compare only with default v2; converted v1 verdict fails validation |
| `joulewise/analysis_engine/__init__.py:247` | per-resolution propagation | `tests/test_analysis_claims.py:1278` | re-emit default v2; v1 resolution changes version |
| `joulewise/analysis_engine/__init__.py:276` | aggregate propagation | `tests/test_analysis_claims.py:1278` | aggregate unlike ids; mixed resolutions do not refuse |
| `joulewise/analysis_engine/inputs.py:4336` | exact resolution | `tests/test_analysis_claims.py:2065` | compare only with default v2; exact v1 resolution refuses |
| `joulewise/analysis_engine/inputs.py:4467` | transported resolution | `tests/test_analysis_claims.py:2065` | compare only with default v2; transported v1 resolution refuses |
| `joulewise/analysis_engine/claims.py:303` | claim evaluation | `tests/test_analysis_claims.py:425` | re-emit default v2; accepted v1 claim metadata changes version |
| `scripts/mint_floor_artifact.py:1929` | prose rendering | `tests/test_mint_floor_artifact.py:1497,1529` | compare only with v2 or omit cross-carrier id check; frozen carriers fail or mixtures render |

The v2 shape itself is pinned at `joulewise/detection_floor.py:116,377-391` by `tests/test_detection_floor.py:2144`; the v1 object and five byte hashes are pinned by `tests/test_detection_floor.py:2169` and `tests/test_mint_floor_artifact.py:1497`. The unchanged two-gate implementation at `joulewise/analysis_engine/claims.py:336,362-375` is pinned by the 6/5/4 witness at `tests/test_analysis_claims.py:408`; the temporary summed-gate mutation made that witness `not_resolvable` and failed V8.

## Verification notes

The first V3/V4 attempts each found a test-fixture setup error: the new legacy checks had initially used a non-attribution-limited artifact, whose correct discipline is absent. The fixtures were changed to explicit attribution-limited artifacts; the complete modules then passed with the exact tails above. Per preflight, no discovery suite and no sixth test module were run; both `inputs.py` branches are exercised in V4. The site producer used its deterministic offline renderer because pinned Marked is unavailable.
