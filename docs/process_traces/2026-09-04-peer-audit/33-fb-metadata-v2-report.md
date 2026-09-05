```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "blocked",
  "completion": "partial",
  "summary": "The required ten-site v1/v2 migration is blocked because four exact-equality consumers live in three paths omitted from WRITE_SCOPE; no code was changed.",
  "workspace": {"base_requested":"d4aa000a","base_mode":"exact","head_start":"d4aa000ab6182296d5b839f2aed1cf8805a2d6e2","head_end":"d4aa000ab6182296d5b839f2aed1cf8805a2d6e2","upstream_end":"92350cadb4d7cfe0429175d95386ce4c322b83cf","branch":"feat/2026-09-04-fb-metadata"},
  "pathspec": ["docs/process_traces/2026-09-04-peer-audit/33-fb-metadata-v2-report.md"],
  "unowned_dirty": [],
  "verdict": {"implementation":"no_change","acceptance":"needs_ruling"},
  "verification": [
    {"id":"V1","kind":"inspection","cmd":"git status --short --branch && git rev-parse HEAD && git branch --show-current && git rev-parse --verify origin/main","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["## feat/2026-09-04-fb-metadata","d4aa000ab6182296d5b839f2aed1cf8805a2d6e2","feat/2026-09-04-fb-metadata","92350cadb4d7cfe0429175d95386ce4c322b83cf"]},"expected":{"exit_code":0,"tail_regex":"92350cadb4d7cfe0429175d95386ce4c322b83cf$"}},
    {"id":"V2","kind":"inspection","cmd":"git fetch origin main","cwd":".","observed":{"result":"fail","exit_code":255,"tail":["error: cannot open '/Users/edr/code/JouleWise/.git/worktrees/JouleWise-wt-fb-metadata/FETCH_HEAD': Operation not permitted"]},"expected":{"exit_code":0,"tail_regex":"^$"}},
    {"id":"V3","kind":"inspection","cmd":"rg -n \"attribution_single_count_discipline\\(\\)\" joulewise/detection_floor.py joulewise/analysis_engine/artifact.py joulewise/analysis_engine/__init__.py joulewise/analysis_engine/inputs.py joulewise/analysis_engine/claims.py scripts/mint_floor_artifact.py","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["joulewise/detection_floor.py:3353:        attribution_single_count_discipline()","joulewise/detection_floor.py:3842:                attribution_single_count_discipline()","joulewise/detection_floor.py:4112:                attribution_single_count_discipline()"]},"expected":{"exit_code":0,"tail_regex":"joulewise/detection_floor.py:4112:.*attribution_single_count_discipline\\(\\)$"}}
  ],
  "flags": [
    {"id":"F1","kind":"scope_deviation","level":"blocking","text":"The ratified migration requires edits to four exact-equality consumers in three unlisted paths. Leaving them unchanged makes v1 or v2 artifacts fail and cannot satisfy the refusal-of-mixtures rule.","needs":"Resume with the three requested paths added to WRITE_SCOPE."},
    {"id":"F2","kind":"environment","level":"nonblocking","text":"The requested fetch could not update FETCH_HEAD because the linked worktree Git metadata is outside the writable sandbox; gate records 41/42/43 were read from locally available commits 60c6b558/ff82e0dd.","needs":"Lead may confirm remote freshness outside this sandbox."},
    {"id":"F3","kind":"verification_gap","level":"nonblocking","text":"No test module was run because the atomic implementation is scope-blocked; the discovery suite was not run as instructed.","needs":"After scope expansion, run only the five named modules, one at a time."}
  ],
  "scope_expansion": {"requested_paths":["joulewise/analysis_engine/inputs.py","joulewise/analysis_engine/claims.py","scripts/mint_floor_artifact.py"],"reason":"Gate 42 identifies these as four of the ten whole-object equality consumers that must dispatch by embedded rule_id and preserve the matched canonical object.","blocked_work":"Atomic v1/v2 implementation, mixture refusal, producer rendering, and the five focused module runs.","minimal_change":"Replace the four equality checks with the shared version-aware canonical validator and preserve the validated object when propagating/rendering it."}
}
```

## Change

No implementation file was changed. The exact consumer census is:

| Site | Role | Scope |
|---|---|---|
| `joulewise/detection_floor.py:3352-3353` | component-record validation | authorized |
| `joulewise/detection_floor.py:3841-3842` | cell validation | authorized |
| `joulewise/detection_floor.py:4111-4112` | transport-group validation | authorized |
| `joulewise/analysis_engine/artifact.py:490-491` | claim-artifact metadata validation | authorized |
| `joulewise/analysis_engine/__init__.py:257-258` | per-resolution propagation | authorized |
| `joulewise/analysis_engine/__init__.py:294-295` | aggregate propagation | authorized |
| `joulewise/analysis_engine/inputs.py:4336` | exact floor resolution | **not authorized** |
| `joulewise/analysis_engine/inputs.py:4467-4468` | transported floor resolution | **not authorized** |
| `joulewise/analysis_engine/claims.py:303-304` | claim evaluation | **not authorized** |
| `scripts/mint_floor_artifact.py:1914-1928` | mint prose consumer | **not authorized** |

`joulewise/floor_extraction.py:1432-1433,3121` are v2 producer/propagation sites, not additional equality consumers.

Carrier census: 4 of 17 fill-rehearsal JSONs contain the key. They were introduced as synthetic fixtures in `e3f28da9` with no repository producer, so their v1 bytes must remain frozen. Root `df-ph-decode-floor-mint1.json` is a frozen v1 mint produced by `scripts/mint_floor_artifact.py`; `docs/site/adapter_contracts.html` is produced by `scripts/build_site.py`.

## Verification notes

Tests intentionally did not start because the migration cannot be made atomic inside the current allowlist.

## Residual risk

Editing only the authorized six consumers would leave four consumers rejecting one valid version or silently rewriting v1 metadata as v2, contrary to Q-17-3.
