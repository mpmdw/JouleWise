```json
{
  "schema":"claude-codex-report/v1",
  "genre":"review",
  "status":"findings",
  "completion":"complete",
  "summary":"Concede registry-sourced resolution and rename-only fixture digest; amend tooling to preserve frozen v2 generator bytes and bind the new v3 family directly to r5.",
  "workspace":{"base_requested":"9f7f091","base_mode":"exact","head_start":"9f7f0917751cd7cdbdd61351c98d2fac6132b9e4","head_end":"9f7f0917751cd7cdbdd61351c98d2fac6132b9e4","upstream_end":null,"branch":null},
  "pathspec":[],
  "unowned_dirty":[],
  "verdict":{"findings":[{"id":"F1","severity":"blocker","title":"Retargeting a v2 generator mutates a frozen pack","detail":"Each v2 generate_configs.py is a generated pack path and a recorded evidence source; a new v3-specific generator/builder is required for the r5 retarget."}]},
  "verification":[
    {"id":"V1","kind":"inspection","cmd":"git status --short --branch && git rev-parse HEAD","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["## HEAD (no branch)","9f7f0917751cd7cdbdd61351c98d2fac6132b9e4"]},"expected":{"exit_code":0,"tail_regex":"9f7f091[0-9a-f]+"}},
    {"id":"V2","kind":"inspection","cmd":"shasum -a 256 configs/campaigns/d117_floor_qwen25_1p5b_v2/generate_configs.py","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["f55955c51b04fb80647935d16527e7de7927079ef807dea1cefa2a173eeaf5b7  configs/campaigns/d117_floor_qwen25_1p5b_v2/generate_configs.py"]},"expected":{"exit_code":0,"tail_regex":"f55955c51b04fb80647935d16527e7de7927079ef807dea1cefa2a173eeaf5b7"}},
    {"id":"V3","kind":"inspection","cmd":"PYTHONDONTWRITEBYTECODE=1 python3 -c 'from pathlib import Path; import hashlib; from joulewise import calibration_bracketing as cb; r4=Path(\"configs/calibration/calibration_acceptance_d079_v2_n17_r4.json\").read_bytes(); print(\"r4-registry-digest-match\", hashlib.sha256(r4).hexdigest()==cb.ISSUED_ACCEPTANCE_REGISTRY[cb.ANCHOR_V3_R4_ACCEPTANCE_ID][\"file_sha256\"]); print(\"r4-d102-screen\", cb._D102_GENERATION_DERIVATIONS[cb.ANCHOR_V3_R4_ACCEPTANCE_ID][\"operatives\"][\"bracket_screen_s\"]); print(\"fixture-digest-role\", cb.DEFAULT_ACCEPTANCE_BOUND_SHA256==\"9a264c57fdc007de473872870f19a5e1c9bd9b11256c25266b0e3e50ebba0ceb\")'","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["r4-registry-digest-match True","r4-d102-screen 0.009724","fixture-digest-role True"]},"expected":{"exit_code":0,"tail_regex":"r4-registry-digest-match True"}},
    {"id":"V4","kind":"test","cmd":"PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp python3 -m unittest tests.test_floor_mint_estimator","cwd":".","observed":{"result":"fail","exit_code":1,"tail":["Ran 37 tests in 0.044s","FAILED (errors=23)"]},"expected":{"exit_code":0,"tail_regex":"OK"}}
  ],
  "flags":[{"id":"F2","kind":"environment","level":"nonblocking","text":"The read-only sandbox cannot create temporary directories even with TMPDIR=/tmp; V4 errors are FileNotFoundError for no usable temporary directory, not assertion failures.","needs":"Replay estimator and generator checks in the writable transaction checkout."}]
}
```

## Findings

### 1. RESOLVER SOURCING — CONCEDE

The estimator replay fixture supplies only `acceptance_id`, `derivation_sha256`, and `schema_version`—no `decimal_derivation` (`tests/test_floor_mint_estimator.py:38-42`). Artifact-sourcing at that boundary would break replay.

Adopt registry-sourced, fail-closed policy resolution by `acceptance_id`, with the ID required to match the independently authenticated issued-acceptance context. The registry remains artifact-authenticated: `_valid_acceptance_bound` checks the artifact’s operatives against its generation derivation (`calibration_bracketing.py:545-559`). Unknown IDs refuse.

### 2. TOOLING — AMEND

Withdraw the bespoke mint-policy derivation command and standalone family verifier. Retain the existing emission/check mechanics and a no-copied-scalar guard.

F1: do not retarget the three `_v2/generate_configs.py` files. Each is an expected pack output (`:2470-2474`) and the alpha source is recorded at its current hash in `arm_readiness.sources/multicell-mint.json:327-328`. Preserve mode copies the current repository bytes (`:1940-1944`), so after an edit it copies the altered—not historical—generator. D-134 hashes every committed pack blob (`arm_readiness.py:2553-2564`).

Amended clause: “Create deterministic `_v3` generator/builder bytes, seeded from the audited `_v2` mechanics but living only in the new `_v3` packs, and bind them directly to r5 through the resolver. Keep all `_v2` generator bytes untouched. The new generator’s `--check`, frozen `_v2` byte/replay checks, and successor lifecycle authentication are sufficient; do not add a tracked golden-regeneration tool.”

### 3. DEFAULT_ACCEPTANCE_BOUND_SHA256 — CONCEDE

Rename only, preserving `9a264c57…` as `GENESIS_FIXTURE_ACCEPTANCE_SHA256` (or equivalent). It authenticates `schema_fixture_unissued` at `calibration_bracketing.py:627-635` and is returned for non-issued artifacts at `:719-722`; changing it to r4 or r5 would break that fixture role.

### 4. ACCEPTANCE BINDING UNDER R1 — AMEND

(a) Rebind the new output to r5: create/authenticate the r5 artifact; add its issued-registry and arm-readiness routing rows; make r5 live; map r5 to `_D102_N17_DERIVATION`; point the new `_v3` generators, specs, evidence, and receipts to r5’s ID/path/artifact/derivation hashes. Add r5 to the fixture copy-list alongside r3/r4. Update issuance-dependent goldens once. Schema conditionals gain r5 for the existing n17 screen/rule pair; the scalar enum values do not change.

Leave `_v1`/`_v2`, r3/r4 bytes and registry entries, `freeze-0002`, `_ACCEPTANCE_SELECTION`, n19 mappings, and the renamed genesis-fixture digest untouched.

(b) Cheapest safe sequence:

1. Finish R1’s flip and all four D-079-pinned estimator-source edits.
2. Derive/build and authenticate r5 at that final R1 state; install its registry/live pointers.
3. Implement R2 resolver/schema/validator and new `_v3` generator directly against r5; derive goldens once.
4. Emit `_v3` once, then author evidence and mint `freeze-0003` at the final measurement-checkout head.

(c) R2 does not make r5 harder: its planned files are absent from r4’s pinned `ESTIMATOR_CODE_PATHS` (`calibration_bracketing.py:142-147`). No r6 is needed unless implementation expands into one of those four files.