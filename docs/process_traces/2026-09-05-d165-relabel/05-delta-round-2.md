```json
{"schema":"claude-codex-report/v1","genre":"review","status":"findings","completion":"complete","summary":"NOT LANDABLE: R1/R2 cured; active paper consumers leave R3 incomplete.","workspace":{"base_requested":"c43b7086","base_mode":"exact","head_start":"c43b7086","head_end":"c43b7086","upstream_end":"c43b7086","branch":"feat/2026-09-05-d165-relabel"},"pathspec":["docs/process_traces/2026-09-05-d165-relabel/05-delta-round-2.md"],"unowned_dirty":[],"verdict":{"result":"NOT LANDABLE","same_signature":"YES: missed mirror/consumer (R3), not arithmetic.","findings":[{"id":"D1","severity":"should_fix","summary":"Fill checklist requires v1 exclusively; structural insertion authority still names v1."},{"id":"D2","severity":"should_fix","summary":"Two active draft timing claims await the declared paper-K handoff."}]},"verification":[{"id":"V1","kind":"test","cmd":"PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_night_gate.NightGateTests.test_d166_registration_digest_is_the_ruled_literal tests.test_night_gate.NightGateTests.test_d166_registration_file_hashes_to_the_ruled_literal","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["OK"]},"expected":{"exit_code":0,"tail_regex":"OK"}},{"id":"V2","kind":"test","cmd":"PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_d165_dominance_closeout","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["OK"]},"expected":{"exit_code":0,"tail_regex":"OK"}},{"id":"V3","kind":"test","cmd":"PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_d117_contrast_v5_pack","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["OK"]},"expected":{"exit_code":0,"tail_regex":"OK"}},{"id":"V4","kind":"test","cmd":"PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_d117_floor_qwen3_v5_generate","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["OK"]},"expected":{"exit_code":0,"tail_regex":"OK"}},{"id":"V5","kind":"test","cmd":"PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_night_gate","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["OK"]},"expected":{"exit_code":0,"tail_regex":"OK"}},{"id":"V6","kind":"smoke","cmd":"PYTHONDONTWRITEBYTECODE=1 python3 - <<'PY'\nimport json,subprocess\nfrom pathlib import Path\nfor file,vid in [('03-refuter-physics.md','V3'),('04-fix-round-2-report.md','V6')]:\n r=json.loads((Path('docs/process_traces/2026-09-05-d165-relabel')/file).read_text().split('```json\\n',1)[1].split('\\n```',1)[0])\n cmd=next(v['cmd'] for v in r['verification'] if v['id']==vid)\n subprocess.run(cmd,shell=True,check=True)\nPY","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["paper-K draft bytes unchanged: PASS"]},"expected":{"exit_code":0,"tail_regex":"PASS"}}],"flags":[{"id":"F1","kind":"residual_risk","level":"nonblocking","text":"External custody artifacts are unavailable; prospective supersession remains a collection gate.","needs":"Lead inventories actual custody coordinates and completes the dependency census below before collection."}]}
```

## Findings

**D1 — should_fix, same signature as round 1 (R3: missed consumer).** `docs/paper/round7/fill-checklist.md:138` requires authenticated **v1** exclusively, excluding active v2. `round7/structural-edits.md:86` still cites v1 as insertion authority. The :82 note supersedes only the cancellation paragraph. Specify active v2/historical v1.

**D2 — should_fix, known paper-K handoff (R3).** `docs/paper/draft-v2-skeleton.md:29,1387` still claims physical timing motion preserves doubling. Paper-K's assigned cure is unlanded. **NOT LANDABLE** for full relabel closure at c43b7086; lead must close D1/D2. 

R1/R2 cured: both floor generators import the shared reason at :39, use it at :678 and inject registration at :720. V6 confirms mirrors, registration/pin, six supersessions and fixture digest. `git show c43b7086` changes no replay arithmetic.

Exact refuter search rerun:
`rg -n -i 'cancels exactly|common-time|moved together|shared fiducial shift' joulewise configs docs/contracts docs/paper`
All **20 survivors**:
- Legacy (1): `joulewise/dominance_closeout.py:58`.
- Corrected denial/rationale (9): core :63,602; contract :42,46; registry :229,244,260; structural-edits :82; contrast registration JSON :1.
- Superseded history (6): structural-edits :84; retensing-plan :127,131,411,559,563.
- Unrelated ABBA drift diagrams (2): draft-v1 :61; draft-v2-skeleton :221.
- Active stale claims (2): draft-v2-skeleton :29,1387 (D2).
D1 is outside this search; same missed-consumer signature.

Custody consequences — **before collection; none performed**:

Floor-generator digests changed.

`git ls-files 'configs/campaigns/d117_floor_qwen3-*_v5/*'` lists only two sources. No local trees/projections/receipts or tracked old-digest pins exist. Per external pack:
1. Direct pin: `plan_tree.json.generator.sha256` (:2852–2854), sealed by `plan_tree.sha256`. Hash final `embedded_generator_bytes()`, including successor rewriting.
2. Registration-bearing `calibration_plan.json`+sidecar; `producer_contract.json.plan` pins both. Tree pins plan, producer and `extraction_spec.json`. Recompute changed bytes and dependent references together.
3. Frozen projection mirrors in tree `arm_attachments.identity_pin_projection` and producer `identity_pin_projection`; `identity_pin_projection.receipts/projection-NNNN.json`+`projection-NNNN.sha256`. Receipts bind identity/config inputs and reviewed commit, **not generator SHA directly** (`identity_pins.py:2083–2108`).
4. `arm_readiness.sources/pack-authentication.json` includes generator primary SHA; `arm_readiness.evidence/evidence-pack-authentication.json`+sidecar binds it. All evidence shares pack digest/HEAD; renew it and clone proof (`arm_readiness.py:3509`).
5. `arm_readiness.freeze.receipts/freeze-NNNN.json`+`.json.sha256`, tree attachment/evidence closure; external `<custody>/<pack>/receipts/<bracket>/identity-pin-arm-verify.json`+sidecar. Freeze pins plan bytes; new custody must bind successor identity/evidence.
6. `expected_pack_paths()` (:3037–3105) is inventory, not a pin: README, generator, calibration plan+sidecar, root+six stage order manifests, tree+sidecar, producer, extraction spec, decode prompt manifest/candidate, prefill pin+ladder+selection sources, three family definitions, 100 configs. Audit every member and external reference; update successor paths/IDs consistently. `check_current()` (:3134–3180) adds freeze/projection/evidence/source closure.

Before collection, lead must inventory external coordinates, map old→new artifacts/receipts, use D-138 successors for frozen identities (first custody for drafts), rederive projections and reissue readiness/freeze/arm evidence plus clone proof. Preserve history/supersedes lineage. No submission-time scientific rebuild.

Night retarget: active SHA `dfe55f8d96cd21e07cd1c7fe230fef34f485f027f3920ce96b8a9ebacc1ac265`. Executed:
`rg -n '1c0a4a119fa06984ff38082781e06bc9bd90f07eae7165359718dfb063783a2b' scripts joulewise tests configs`
Only `night_gate.py:29`'s historical comment survives. No old digest in quiet_window_clock.sh (no registration pin), night_plan_writer.py or night_plan_v1_retired.json (path only), or rehearsal tests (synthetic bytes/constant patched). New diagnostic/stub plans must resolve to v2 registration bytes; C1 :908–935 rejects old copies. Preserve historical copies. Night gate has no floor-generator pin.

Compatibility executed (V2/V6): original v1 sidecar SHA `69ac25694cb5d8f8cf7645c844b2eab3c769ba82748802a3291fcae950440735` remains exact and validates through legacy result/reason acceptance; v1-backed closeout validates. P2: **1.500000 / False** in both; all other fields equal. Night-plan v1 is separately retired: V5 executes its expected rejection.

## Residual risk

152 tests passed: pins first (2), sequential modules (50/40/13/47). No discovery, agents or hardware work. External custody/live gates unverified. Only report written; clean exact HEAD/upstream.
