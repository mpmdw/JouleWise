# Block 6 release record

Released under its registration on 2026-11-13 17:38 PST. The commit of this record on `main` is the release event (RL-134 item 10); before it no person or agent opened the restricted outputs.

## Identity

| Item | Value |
|---|---|
| Registration (`docs/registrations/block6_replication_DRAFT.md` at `main` 76a6eba99b3a08137c8608d92c4fcc36581fa4a4) | `7243a2bc1e43207d756ba9eacc6c93622968edd73a6ebe0648afaba563324ead` |
| Flag catalog (S-3) | `b5bce6c64bbc1d079ecf6fed02bf4c214b76a8f7d279d44eea5984e4a389a42b` |
| S-14 commit | `6e6d1b18a9dffbba675c3abd28db2e4c6a484fde` |
| Tag | `b6/analysis-r2` |
| Custody manifest | `b2901d51990812f6c2dadce1a763d90502d85b58a9d5b5b358d4cbb2ba9a9d6b` |
| Verify receipt (custody copy) | `57df8a76361ba9d299383c2248e3ba6497dd33fd92dd74be33ec5d89a4830c91` |
| Verify receipt (release census) | `57df8a76361ba9d299383c2248e3ba6497dd33fd92dd74be33ec5d89a4830c91` |
| Run-input document, dry run (`D_block`) | `0a1a149cc9403e956121eec2daaf7c852eae1a83ea1c079562c80c4e4cc66a8e` |
| Run-input document, gate run (`D_gate`) | `ace8bfb4f8ceb0b007d0641933ad78f2d469f73af3f159feb63b617bdebf7b9a` |
| Block 5 released output | `c06ee7c8cbf85a68dcebc24a73e0372fd6f8d825fc3acf30ec352304dd93cacc` |
| Python | 3.13.18 |
| zstd | *** Zstandard CLI (64-bit) v1.5.7, by Yann Collet *** |
| L9 audit | not run |

## The 24 pinned files

| Path | SHA-256 |
|---|---|
| `configs/b6/flag_catalog_b6.json` | `b5bce6c64bbc1d079ecf6fed02bf4c214b76a8f7d279d44eea5984e4a389a42b` |
| `configs/b6/recompute/hazard_sizing.json` | `bf399bec4195b9237f53c747c6fc9cd24066610eba933a0fad767534d970d29b` |
| `configs/b6/recompute/precision.json` | `e242cab6bb311a9c23d5c6dc06374ed3094a351e36d6954c3589e2b535cc63b0` |
| `configs/b6/recompute/production_comparison_keys.json` | `62dbfaef9ebc5cfbbe5a00734f5eb8ad3d82389f54f28473ed63db6135b9174d` |
| `configs/b6/registration/acceptance.json` | `ea130c87ece4e8b557a6357f1f75df045b5a0a738db18fe5ee990a7b539ce2a8` |
| `configs/b6/registration/identity_pins.json` | `513d7d4a98f464c7236b34c53f51cd523a9f45b4d9f05f2282a4a22424b4841d` |
| `joulewise/__init__.py` | `df98d6ea46fd21ec24bb8fc4c208e4e01f5167e6c7f2af36490781779d5710cc` |
| `joulewise/axi_decode_config.py` | `fab53ea66a636458bb8c36f0c5f5f3f014478db8351e246746c9b6bc7c62dd93` |
| `joulewise/b6_analysis_check.py` | `634c991c527106d32a93197dc00af113636ce30789b1080431cfa1750d056b30` |
| `joulewise/b6_analysis_hazards.py` | `9a907a3671dbe210df4d417428c9108f0fdee1c16531bd0bef2fd39b0f27bb2b` |
| `joulewise/b6_analysis_inputs.py` | `283dfc78341742768dc210b9fd46da19cc0b1f883f316db8106e3db79f89219e` |
| `joulewise/desk_compress.py` | `ac770c9407dad936cc742957b6f5673a1b69523156aa2be9baf7de8eb2b56777` |
| `joulewise/flags/__init__.py` | `2ea17e7b30b4101d2149be0a216c82e223b903121f50bda8f0d5665b33378ba2` |
| `joulewise/flags/catalog.py` | `006840601a37009d685db458186492963b15fa7cb9be05a3ae066b9e9ae82ef0` |
| `joulewise/flags/exclusions.py` | `ebe1678c0fdd60b1ddd20d432cf07412bd321a8629589f4ce4c6b334378f0ad6` |
| `joulewise/flags/schema.py` | `cd7ce3c00dec53068db4e5c6a41115e264399dbbcc741b96dc8133b67fa1fad8` |
| `joulewise/idle_admission.py` | `9dc6b5d45c1dc138a13195b64cd1ca23eac0427c864063f26e274775b5a5a79e` |
| `joulewise/schemas.py` | `f47fbf68c2c4a931854995d1258425b476c4bc8a686dfccf011d9caef092cc3b` |
| `joulewise/twins/__init__.py` | `e717dc7f4b7c3b6006f06763873a70c79d95d9ad7cb3183c21eb5251daffaeb0` |
| `joulewise/twins/engine_twin.py` | `5cd6977d79b2951a6e4351a9e8f95b4f91bc38af50eeb4c5bf2d5115ffedbff8` |
| `joulewise/twins/harvest_twin.py` | `df39036b24eab0d015c198686e3ed03ae0add341e487636d34ed622fa0695af0` |
| `joulewise/validation.py` | `82bb03f3aed626446298d186e845b7fe75b3371ca6cbabd7160946bd8e7bfcfd` |
| `scripts/independent_recompute_b5.py` | `d49103e884ccae47242b8efb91ea1f5764e4505a4ad5e54558cc42a399a2e4e0` |
| `scripts/independent_recompute_b6.py` | `4a9f594471652581737b6cd02bd2922592f2e7cf9d575a164adb10162a5211ea` |

## Sessions (`harvest_sha256` from the manifest)

| Copy path | `harvest_sha256` |
|---|---|
| `r1-alpha/archive` | `c0b5a53140da8d9cb72309eeda251a0c7794655726f030eb6dc0b01a20b0630f` |
| `r1-beta/archive` | `da7fcdebf734c7ca2585f757482e468b374204d14d041a6b797ad5081178b751` |
| `r1-gamma/archive` | `98b1be5d28237415b409a4ab861408a51be7010f1c4f529fea5e6ea23bb88898` |
| `r2-beta/archive` | `d6cf192f2dd308e02ce743992d253baab7979db10331173e90f00d31d7e3efba` |
| `r2-gamma/archive` | `94029bcef2971b87c9f5da32eb742a2e0aa94d4cc29feead58cef6253db45626` |
| `r3-alpha/archive` | `cea99d370c080144b9d956931bc7fe3212719d87037094910382fa64d016f48a` |
| `r3-beta/archive` | `0c5bfea7b7ad9d4c7f69d3b627a0dc2dfc3b73b5018546c4b4f9ab492a6ef512` |
| `r3-gamma/archive` | `d0b1a560b319625b5fed8ba36cd6f708db89575bef935330e839c7b8227d89e4` |
| `r4-alpha/archive` | `53ed3483341b7e56479a94ec37879235438ea75c299c0f69accbba57ebcdc069` |

## Output digests

| Run | File | SHA-256 |
|---|---|---|
| gate | public | `c926565b384259f4519069be225c4638bb4d8fa3ba48ae5f4fc09aff68da4f69` |
| gate | restricted | `4e620ed55cfe4e164e98c79e0d7b42523755a50b7176cbf2e3081f157f58a918` |
| gate | stderr | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |
| gate | stdout | `2a5cbd0676f7b7f64d187f1b907b1e8e451cfcf6b4a58d3bfc49b3e4a36a424b` |
| dry | public | `c2b5c4098f70dd3a5be19edb3016bf682588d5529f21c41abf05d125fe8107f8` |
| dry | restricted | `92e67c389bb71813d1e57b962e98eb6dcacf65d2bc3957332a36881c821c14bb` |
| dry | stderr | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |
| dry | stdout | `f718e0ac719f9e11165750beb844882e6bc7a559a95f31d27ffe8bb398c153d6` |

## Attempts ledger (RL-134 item 6)

| Stem | Exit | Status | Class | Code | Wall (s) | argv SHA-256 |
|---|---|---|---|---|---|---|
| gate | 4 | refused | A | compression_relocation_ambiguous | 0.331 | `e8efd54fa133a891a78e17ac63f48fce141a0dac9bfa6f6536c7f2b27b48df85` |
| gate | 0 | complete | None | None | 322.427 | `511b860757f1d2776c52b5b04902516bf533eeabbc58ea9656e6af3344a6cd33` |
| dry | 3 | hold | None | comparison_stopped | 2820.609 | `8b507892a4a368a6e6deeeed2427ffe2cc9d19cec78a3ade9ab1cb6a2241f845` |
| gate | 0 | complete | None | None | 319.346 | `9b79ce010d435b6c6200e8e0e47822cab9bfcfa60ae63af5ec090a73a5b667bf` |
| dry | 0 | complete | None | None | 2805.143 | `f04c97aac9ee828336fa790aa74fffc84c23a5b47a0a730648bf0ae45a01eef4` |

## The eleven conditions (runbook step 11)

| # | Condition | Result | Evidence |
|---|---|---|---|
| 1 | Block 6 closed: nine counting sessions (§5.3 close record, RUN_STATE item 59) | pass | Block 6 closed, nine counting sessions: §5.3 close record, RUN_STATE item 59 (loop wake 000002, 2026-10-21) |
| 10 | the RL-6 (d) line is in RUN_STATE.md | pass | RL-6 (d) line: RUN_STATE item 309, main a5c698e51 (2026-11-13) |
| 11 | Ed's OK is on record | pass | Ed's OK in session 2026-11-13 08:45 PST, renewed 14:30 PST for r2 (RL-142); RUN_STATE item 309 |
| 2 | Block 5 released (RUN_STATE item 231) | pass | Block 5 released: RUN_STATE item 231 (Ed's unseal OK 2026-11-08 11:17 PST) and the Block 5 release record |
| 3 | the dry run completed over every session, exit 0, no refusal; every earlier attempt is in the ledger | pass | {"exit_code": 0, "gate_exit_code": 0, "ledger_rows": 5, "sessions": 9, "unledgered_attempts": []} |
| 4 | option_c.pass true, comparison_stopped false, every compared class failed 0 and unmatched 0 | pass | {"block5_count": {"expected": 48, "observed": 48}, "classes_not_clean": [], "probe_ran_on_these_bytes": true, "probes": {"dry": {"bound": true, "departs": [], "not_checked": [], "stage_ok": true}, "gate": {"bound": true, "departs": [], "not_checked": [], "stage_ok": true}}} |
| 5 | term 7: pass | pass | {"term7": "pass"} |
| 6 | output digests equal the launcher's record; public restricted_sha256 equals the restricted file's | pass | {"public_binds_restricted": true, "public_equal": true, "restricted_equal": true} |
| 7 | input census: a second kit verify, same sessions, files and bytes; run inputs, Block 5 and loop files re-hash to the values the run used | pass | {"kit_exit": 0, "receipt_existed": false, "receipts_agree": true, "rehash": {"block5": true, "loop_attempts": true, "loop_state": true, "run_inputs": true}} |
| 8 | run checkout clean at the S-14 commit with 24 of 24 hashes, before the gate run and after the dry run | pass | {"gate_and_dry_records": true, "now": {"clean": true, "hashes_equal": true, "hashes_equal_count": 24, "head_is_commit": true}} |
| 9 | PR #748 merged; S-16 line entered or RL-134 item 17 applied | pass | PR #748 merged 35b94bca5 (S-14 fill); S-16 line 236c8f708 (RL-134 item 17) |

## Signature

Signed: Laptop lead (Claude Opus 5.5) under Ed's OK of 2026-11-13 (RUN_STATE item 309), 2026-11-13 17:38 PST. The eleven conditions held at the release check of 2026-11-14T00:54:46+00:00 (UTC); the numbers that print are the dry run's outputs, verified by digest.
