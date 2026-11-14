# Block 6 release record

Released under its registration on 2026-11-13 18:23 PST. The commit of this record on `main` is the release event (RL-134 item 10); before it no person or agent opened the restricted outputs.

## Identity

| Item | Value |
|---|---|
| Registration (`docs/registrations/block6_replication_DRAFT.md` at `main` a5dc2a1b56d1f55126324fc8c0b73f5f10d8d88d) | `7243a2bc1e43207d756ba9eacc6c93622968edd73a6ebe0648afaba563324ead` |
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

Signed: Laptop lead (Claude Opus 5.5) under Ed's OK of 2026-11-13 (RUN_STATE items 309 and 311), 2026-11-13 18:23 PST. The eleven conditions held at the release check of 2026-11-14T00:54:46+00:00 (UTC); the numbers that print are the dry run's outputs, verified by digest.

## Additions and corrections (RL-142, the RL-144 addendum, RL-146)

Written by hand by the lead under RL-146, 2026-11-13 18:23 PST. Everything above this heading is the output of `b6_release_record.py record` (tools commit `f19f3608120adce25bb3ace62dab1ddd9b54f6e4`) from the release-check draft (SHA-256 `bab20d7ad58ba0aead7f121d2ff633e6fbcd066f75d3e8e8eeb0ab19a5271581`), unchanged. The JSON record is the tool's output and does not carry this section.

### Release time

The time in the first line and in the signature is when this record was rendered and signed. The release time is the commit time of this record's merge on `main`. It is entered in `RUN_STATE.md` with the RL-6 (d) line, before any restricted output is opened.

### Correction to condition 9

Condition 9 cites the S-16 line at `236c8f708`. That commit is on `docs/2026-11-13-b6-s17-fill-staged` and is not an ancestor of `main`. The line is on `main` as `255ab96cc781a1ff7b4c56b231ba6f1831d6807d`, inside PR #748's merge `35b94bca5113704f80c9c6d4cf587c8c4ff4577d`. Its text is the same at both commits. The condition holds; the pointer is corrected.

### Condition 11, in Ed's words

Ed, 2026-11-13 18:13:29 PST, verbatim: "OK, today or tomorrow"; the option's text, which he chose: "Release on the same r2 outputs once fixes, CI and Fable's admit are in, even if the merge lands after midnight. I'll quote this answer verbatim and re-date the record and the RL-6 (d) line if it does." (`RUN_STATE.md` item 311, main `a5dc2a1b5`). Item 309 reported his OK of 08:45 PST and its renewal of 14:30 PST in the lead's words.

### Comparisons (a) and (b) (RL-142 §2 items 5 and 6: release conditions on r2)

Names-only comparisons. Each prints differing key paths and no value.

| | Directories | Verdict | Differing paths | Unowned | Result file SHA-256 |
|---|---|---|---|---|---|
| (a) | `gate-2` against `gate-r2` | PASS | 27 | 0 | `b3717ec3001da7f2c1db44af21e5c900dab10a03c630d77b8877c90710c05f9b` |
| (b) | `dry` against `dry-r2` | PASS | 176 | 0 | `8b805e8e910e1dfe3b801a137c9f137a0a4c75b4eb67d695923ac1ba66ade6eb` |

Comparer `compare_rl142.py` v2, SHA-256 `eb82b6e25a9dc9a3cffcb4d2e859a19c2f2151a42ce3b4a98f2ea188887e02c1`; its predeclared differences, `rl142-expected-diff.md`, SHA-256 `6101e980ecfe0e37f7bd4da86bc17fea1498cc1b6e48ef0adf79f9f9e40816e4`. The three files are committed to the audit branch after the release. The comparer's own tests (18 of 18) are the lead's account; no log was kept.

### The suite at the release (RL-144 addendum §2)

**Item 1, the named set, green on macOS before the gate run.** Log `evidence/pr762/premerge-macos.log` on `audit/2026-11-10-fable` at `301b632736d61dc5b97bc32a2512555600a4773f`, SHA-256 `8472facb929bbdfbb31b3d6dada210288da0a85515dd8923832c30f7589e4e43`; finished 15:55:45 PST; the gate run at r2 started 15:58:11.

| Modules | Commit | Result |
|---|---|---|
| `tests.independent_recompute.test_block6`, `tests.independent_recompute.test_b6_production` (the tests of RC-B6-1 and of `b6_analysis_check`) | `aaa2f3086` (the same tree as `b6/analysis-r2`) | Ran 62, OK |
| `tests.test_b6_release_record`, `tests.test_b6_structure_probe` | `f19f36081` | Ran 40, OK |
| Custody kit end to end (`tests.test_b6_custody_kit.EndToEnd`, `EndToEndPinned`; kit `e1f4f805288ede026980852814af2512a58b4c74` against the r2 tree) | | 8 OK by the lead's account; **no log was kept**. The gate run and the dry run at r2 then read the kit's real documents and exited 0 |

**Items 2 and 3, the full hosted run on r2's tree.** Run 43521257617 at `aaa2f3086` finished (failure). Its complete failing list is 75 lines, 41 distinct test ids. All 41 also fail on Linux at the base `3551e1a7d4f3bb455b8bfb810d2f406b0fb4b93b` (run 43525694693), with no id on one side only. Class of every id: base-inherent and reproduced on `3551e1a7d`. Unexplained: none. In the named set: none.

| Module | Lines | Distinct ids | On macOS at r2 |
|---|---|---|---|
| `b5_analysis.test_frozen_files` | 2 | 1 | fails the same at head and base (M2 below) |
| `test_mint_policy_resolver_guard` | 4 | 1 | fails the same at head and base (M1 below) |
| `test_b6_r12_session_fixture` | 8 | 4 | passes (86 OK, 14 skipped) |
| `test_git_fixture_maintenance` | 1 | 1 | fails the same at head and base |
| `test_install_night_agent` | 52 | 26 | passes (Ran 67, OK) |
| `test_run_night` | 8 | 8 | none of the 8 fails |

The ids: `evidence/pr762/ci-43521257617-failing-ids.txt` (SHA-256 `fa2389f0f983401f55c94ba8784efc5342342e032f5c6617fdeee96d8932cf9a`) and `ci-43525694693-base-failing-ids.txt` (`0b985eed08d7f9924401acb49f14b043a93ee6e9a242a05c7a3ca902cae1d0ed`), same branch and commit. Also seen on macOS at background priority only: 7 failures in `test_run_night`, the same at head and base, none of them a hosted id.

**Item 4, the two base reds (RL-144 addendum §3).**

- **M1, base-inherent.** `joulewise/b6_analysis_check.py` and `scripts/independent_recompute_b6.py` each carry the literal 0.010818 s. It equals the registered s_bracket (registration §3.3: 10.818 ms). The mint-lane guard forbids copies of that constant; an independent recompute carries its own copy from the registration by design. Not a correctness matter. After the release the guard exempts these two files by name and asserts each literal equals the registry constant. No pinned byte changes.
- **M2, base-inherent.** `joulewise/flags/exclusions.py` (SHA-256 `ebe1678c0fdd60b1ddd20d432cf07412bd321a8629589f4ce4c6b334378f0ad6`, a row of the 24 above) differs from its Block 5 frozen hash: commit `4e3446e6c` added a keyword-only `pack_scoped: bool = True` to `compute`. With the default the expression reduces to Block 5's. **A frozen Block 5 file was edited without a cited rebind.** Owed after the release and before the S-14 line merges to `main`: a row in `docs/analysis/b5/DEVIATION-LOG.md`, entries in `EVOLVED_ON_MAIN` and `REBOUND_WORKING_TREE`, and one test that `compute` with the default gives the Block 5 commit's result on a fixture.

### Disclosures

- **S-14 is at revision 2.** Registration §14 row S-14 names the first pin (`3551e1a7d`, tag `b6/analysis`). §17-R13 and the freeze addendum's `b6/analysis-r2` row are the revision of record, and this release ran at `6e6d1b18a9dffbba675c3abd28db2e4c6a484fde`. That commit is reachable from the tag `b6/analysis-r2` and from `analysis/2026-11-13-b6-s14-merge`; it is not yet on `main` (RL-134 item 18).
- **Order of the r2 predeclaration.** Its amendment (`0dbfd105f17d11ca4e9cf352c50c51fe5310fe6f`, on `docs/2026-11-13-b6-s17-fill-staged`) was committed at 15:58:57 PST, 46 s after the gate run at r2 started and before the dry run at r2 was launched. Runbook step 6 puts it before any program run. The predeclared count of 48 was fixed earlier by RL-142 (14:30), by the tool's `--predeclared` check (`f19f36081`, 14:50) and by `b5-probe` at r2 before the gate run.
- **Programs that opened the restricted outputs before the release,** each by ruling: the pinned program; the launcher and the release check (hash only); the structure probe (RL-134 item 4); and the RL-142 comparer, on `gate-2`, `gate-r2`, `dry` and `dry-r2`. The Mythos audit hashed them and opened none.
- **Mode.** The gate run and the dry run at r2 ran serial (`--workers 1`).
- **Audits of this record.** Claude Mythos 5.2, cold, 2026-11-13 (report SHA-256 `9ba5c89d59ceea82e39ab7e4928bbc279a4a26d8efce69a654fb794bd71a6862`): admit with fixes. Research lead RL-146: this section.
