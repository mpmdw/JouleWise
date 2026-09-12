```json
{
  "schema": "claude-codex-report/v1",
  "genre": "verification",
  "status": "findings",
  "completion": "complete",
  "summary": "BLOCKED. All 38 content-distinct candidates were recovered, hash-authenticated, epoch-checked, and replayed from raw physics: 32 VERIFIED-VALID and 6 VERIFIED-INVALID, with no missing raw evidence. Issuance is not ready because two verified-valid observations exceed the systematic-failure screen and therefore lack an unambiguous ledger disposition, and the repository does not specify a deterministic authenticated historical-import/bootstrap transaction from which one authoritative sequence/head digest can be computed.",
  "workspace": {
    "head_start": "8e68cde6bb67165b6576c331d9631aa353ad0e83",
    "head_end": "8e68cde6bb67165b6576c331d9631aa353ad0e83",
    "branch": "main",
    "pathspec": [],
    "unowned_dirty": [],
    "write_scope": "none",
    "edits": "none"
  },
  "verdict": {
    "overall": "BLOCKED",
    "prompt_vs_R2_divergence": false,
    "raw_member_results": {
      "VERIFIED-VALID": 32,
      "VERIFIED-INVALID": 6,
      "UNRESOLVED": 0
    },
    "blocking_items": [
      {
        "id": "B1",
        "type": "ledger_disposition_ruling",
        "members": [
          "20260726T000039-491995f3",
          "20260801T064830-c76f5d1c"
        ],
        "reason": "Both replay as physically valid, matching the candidate inventory, but their bounds 0.035435840879704805 and 0.0350400833260715 exceed the ratified 0.033558756679900 preflight screen. The production writer maps such a valid capture to systematic-invalid at scripts/validate_powermetrics_fiducial.py:664-671; D-102 explicitly calls the first member a systematic failure at docs/decision_log.md:6298-6301. The backfill candidate tool instead proposes valid solely from stored status at scripts/calibration_ledger_backfill.py:58-63. Selecting either disposition is lead-owned."
      },
      {
        "id": "B2",
        "type": "bootstrap_contract_gap",
        "members": "all 38",
        "reason": "No historical-import/bootstrap API, receipt ordering, duplicate-custody selection rule, or import-transaction schema exists. The candidate tool emits only an unauthoritative candidate set and never appends the ledger (scripts/calibration_ledger_backfill.py:2-7,90-117). Because receipt digests bind sequence, predecessor, disposition, artifact hashes and absolute custody locator (joulewise/calibration_ledger.py:590-622), more than one valid head digest is possible."
      }
    ]
  },
  "binding_clauses": [
    {
      "clause": "D-109 R1.4",
      "source": "docs/decision_log.md:7027-7039",
      "verbatim": "4. The acceptance artifact pins its baseline ledger head. Evaluation ALSO requires the independent current-head pin (clause below), verifies one complete non-forked chain extension from baseline to current, and threads ONE immutable ledger snapshot through every consumer path (session, direct runner path, secondary verifier) — repeated independent loads are a refusal-grade defect. Anti-rollback authority: a REPO-COMMITTED head-pin file `{sequence, head_digest, ledger_schema}` (existing checked-in byte-pin trust model; no second trusted latest-sequence store). Rotation is epoch-bounded — at most one lead-controlled quiet-machine collection session — and NO claim evaluation may occur between ledger advancement and pin commit; a physical head differing from the committed pin refuses.",
      "verification_plan": "After an authorized bootstrap, recompute every receipt digest, require one linear chain, require the artifact cutoff to equal an exact receipt, require the physical head to equal the separately committed pin, and trace one snapshot object through every consumer. This session verified the implemented digest/head machinery but could not select an authoritative bootstrap head because no import transaction is specified."
    },
    {
      "clause": "D-109 R2.1",
      "source": "docs/decision_log.md:7053",
      "verbatim": "1. The issuance cutoff is an exact ledger sequence + head digest.",
      "verification_plan": "Compute the final receipt count and digest only after disposition, ordering and custody-locator rules are fixed. Current fixture cutoff remains non-production genesis sequence 0/all-zero digest at configs/calibration/calibration_acceptance_d079_v2.json:14-18."
    },
    {
      "clause": "D-109 R2.2",
      "source": "docs/decision_log.md:7054-7055",
      "verbatim": "2. `derivation_corpus` remains exactly the n=19 threshold-producing observations.",
      "verification_plan": "Re-run the corpus verifier against all 19 pinned member manifest/evidence hashes and recompute the decimal statistics and artifact canonical hash. Result: PASS."
    },
    {
      "clause": "D-109 R2.3",
      "source": "docs/decision_log.md:7056-7060",
      "verbatim": "3. `prior_observation_set` = every content-distinct governed observation known at the cutoff — valid, systematic-invalid, ordinary-invalid, blind holdout, and unresolved — with epoch and disposition recorded separately. (The current artifact's two ID-only `blind_exclusions` are insufficient and are superseded.)",
      "verification_plan": "Enumerate every exact-epoch validation tree, collapse copies by canonical content ID, authenticate the raw bytes, and assign one epoch plus one ruled disposition per content ID. The 38 identities are complete for the located candidate, but two dispositions require a ruling."
    },
    {
      "clause": "D-109 R2.4",
      "source": "docs/decision_log.md:7061-7063",
      "verbatim": "4. Content identity is path-independent, derived from canonical primary-byte hashes; attempt identity is separate; copies do not create new observations.",
      "verification_plan": "Hash manifest.json and instrument_evidence.json bytes, canonical-JSON encode the two-name hash map, SHA-256 it, and collapse identical IDs. Implementation is joulewise/calibration_ledger.py:94-105,120-134. Result: 53 checkout copies collapse to 38 IDs."
    },
    {
      "clause": "D-109 R2.5",
      "source": "docs/decision_log.md:7064-7068",
      "verbatim": "5. \"New\" (trigger population) = current authentic content IDs − `prior_observation_set`, regardless of capture timestamp or source root; a previously unknown historical artifact IS new when discovered. Every new observation is judged under the PRIOR artifact (D-102's prospective rule).",
      "verification_plan": "After issuance, subtract the exact 38-ID prior set from the authenticated ledger snapshot, independent of path/time, before applying triggers. The implemented subtraction is at joulewise/calibration_bracketing.py:870-893."
    },
    {
      "clause": "D-109 R2.6",
      "source": "docs/decision_log.md:7069-7070",
      "verbatim": "6. New unresolved or unclassifiable attempts cause refusal; only after trigger disposition may a successor artifact absorb them.",
      "verification_plan": "Require every post-cutoff receipt to classify as valid, systematic-invalid or ordinary-invalid; unresolved/abandoned/null-content rows must refuse. Implemented refusal is at joulewise/calibration_bracketing.py:895-900."
    },
    {
      "clause": "D-109 R2.7",
      "source": "docs/decision_log.md:7071-7074",
      "verbatim": "7. The 32-valid/6-invalid same-epoch inventory is a backfill CANDIDATE, not a ratified classification: identities may seed the backfill, but dispositions require raw-physics + hash verification before issuance, and any unresolved member blocks issuance.",
      "verification_plan": "For all 38 members: verify manifest and evidence hashes, verify raw/event hashes, replay causal clock-anchor derivation and the strict 59-pulse detector, verify the six-field epoch, then compare with candidate labeling. Result: 32 VERIFIED-VALID, 6 VERIFIED-INVALID, zero raw-physics unresolved; two final ledger dispositions remain ambiguous."
    },
    {
      "clause": "D-109 R2.8",
      "source": "docs/decision_log.md:7075-7079",
      "verbatim": "8. Counting rule for the D-102 corpus-doubling trigger (19→38): 38 TOTAL authenticated, content-distinct, VALID same-epoch observations — including previously blind observations once unblinded — not 38 post-cutoff observations. Under the candidate inventory, six further valid observations trigger re-derivation.",
      "verification_plan": "Count content-distinct ledger observations whose disposition is exactly valid and whose epoch equals d079_epoch. The implementation does this at joulewise/calibration_bracketing.py:901-908. Result is six further only under the candidate-tool 32-valid disposition proposal; it is eight further under the production writer's systematic-screen mapping."
    }
  ],
  "inventory": {
    "where_it_lives": {
      "count_only_authority": [
        "docs/process_traces/2026-08-03-d111-backfill/calbracket_d079/F3-fix-investigation.md:296-308",
        "configs/calibration/calibration_acceptance_d079_v2.json:225-233"
      ],
      "candidate_emitter": "scripts/calibration_ledger_backfill.py:42-117",
      "concrete_membership": "Implicit in the 53 exact-epoch validation custody trees under runs*/instrument_validation; no standalone serialized 38-row candidate file exists in the checkout or .desk.",
      "raw_archive": "/Users/edr/Library/Mobile Documents/com~apple~CloudDocs/JouleWise-backup",
      "important_non_inventory": "docs/process_traces/2026-08-03-d111-backfill/MANIFEST.md is a manifest of 41 process artifacts, not the 38 calibration observations."
    },
    "identity_method": "sha256(canonical_json({\"instrument_evidence.json\": sha256(evidence bytes), \"manifest.json\": sha256(manifest bytes)}))",
    "identity_method_source": "joulewise/calibration_ledger.py:94-105,120-134",
    "checkout_copy_count": 53,
    "content_distinct_count": 38,
    "candidate_label_counts": {
      "valid": 32,
      "invalid": 6
    },
    "analysis_only_member_set_sha256": {
      "value": "7c0ae751e3be9d180c932b14da1cc9b50f85a73a0821de03c7a7911728a25e95",
      "definition": "canonical SHA-256 of the ordered 38 candidate rows containing attempt_id, content_id, all artifact hashes, epoch, full T1, capture lexeme and bound lexeme; custody locator deliberately excluded. This digest is verification evidence, not a contract-defined production identity."
    }
  },
  "epoch": {
    "epoch_id": "d079_epoch",
    "all_38_match": true,
    "fields": {
      "os_build": "25F84",
      "hardware_model": "Mac15,9",
      "power_policy": "ac_high_power",
      "sampling_interval_ms": 100,
      "estimator_revision": "joint_loss_sublevel_interval_branch_v2",
      "pulse_protocol_id": "powermetrics_pulse_fiducial_v3"
    },
    "source": "configs/calibration/calibration_acceptance_d079_v2.json:20-26,193-200"
  },
  "per_member": [
    {
      "n": 1,
      "attempt_id": "20260722T145535-e941c821",
      "content_id": "c2a4412ee77fd2c10a397c8c4072d06c31bf26ea6b6a9a2ad1764dced71de2e9",
      "manifest_sha256": "e34cdc199a479364dfdc539b3f924aefc997f7fecdeaa5d3d706028bf78e13a7",
      "evidence_sha256": "148a7b45fa5efe88c6d925c836cb9c11596ffc1412960f6248e6bd8114b3eb7a",
      "raw_sha256": "b55f3471c70c54e0174b09e67486759fc532742e9bd671e53ce8324fe23209ef",
      "events_sha256": "605e2330d27f874621edb698c233542d7eb31fb8b8d1def044852a77a223b1bc",
      "bound_s": "0.03018980442653224",
      "verdict": "VERIFIED-VALID",
      "disposition": "valid"
    },
    {
      "n": 2,
      "attempt_id": "20260722T194118-9dc0749d",
      "content_id": "029a412be038ce88428ff1e8d302d90f2020e5cb0179ef4a750613fffc51f8ee",
      "manifest_sha256": "0852da1adb0d0dd243b2142bd67da636f26c07eee4bbfbe1f79f78c771742041",
      "evidence_sha256": "b763e5d6703255d7ebb18113c56cccda8908bb9d8049ab4210935304f50faa3f",
      "raw_sha256": "aa36a9c1e8451e2a0de875a7ff45232c98bf0cce5cdcd5b827d176ea24aa85f7",
      "events_sha256": "0f543eb7f697d442a5c0ddce1fe6f3f69c268c96bdc7a5ffbb6e84f70e8f1d66",
      "bound_s": "0.026300679324099796",
      "verdict": "VERIFIED-VALID",
      "disposition": "valid"
    },
    {
      "n": 3,
      "attempt_id": "20260722T213749-563b9849",
      "content_id": "ec850ad5359df234cf091b452194753acbd609f8c5102443fca8cfb40b3c72aa",
      "manifest_sha256": "b7dd23cf8a9e30d81a01ba0b3c5c5e0c21b4c325e48e1d02e046fb61b77cb0ac",
      "evidence_sha256": "1cc789e9558667e188f1859ba591a584a73eb4d2309612c924eebfb4cf5ffe80",
      "raw_sha256": "3684b27080f6b4254d61e1c5b3f0f25e8401257078145331ef2122b2c1893fd1",
      "events_sha256": "b179d606c17148e754bba07bb61c3d7a5c094e5a0e701251e7674b45472f5a4b",
      "bound_s": "0.2079182387602739",
      "verdict": "VERIFIED-INVALID",
      "disposition": "ordinary-invalid",
      "raw_reason": "fresh causal anchor unknown: native_intersection_empty"
    },
    {
      "n": 4,
      "attempt_id": "20260722T214220-1acdbbc0",
      "content_id": "7232cfa1de9e6e19543d00c976e184ee23f8e4a17d2b05f7f4fa44fc6461f01f",
      "manifest_sha256": "ee78c1a87e5ab21f5c042e4dd2db38b9b7742be1ecaaa75fe0280f7c75a2f5b1",
      "evidence_sha256": "3ea8f946d3522de46b01a90d29b0462f138a7048aa96df33bac79509d46349ea",
      "raw_sha256": "7a4b62258d4d6afe251c4ed60a02835ac4d2b743f926260b2f621cb2301a72de",
      "events_sha256": "6f0c813bf5489f1fce820bddd1160d6936ec5dc6e89f1c3ca2aecdbedc2834af",
      "bound_s": "0.03312014638436772",
      "verdict": "VERIFIED-VALID",
      "disposition": "valid"
    },
    {
      "n": 5,
      "attempt_id": "20260722T215127-eeef661a",
      "content_id": "7d7e898178e7fac74d9733a6703319d3458785abb671a2d43907a1018549f554",
      "manifest_sha256": "9bf378fb924b96cf88015bd35f8733a2a31b2a965872a7781f7c3170fc55e0a5",
      "evidence_sha256": "0659f79270fca6fa1459c01cf7ba8163337b28c3224b3c751eaa2241ca728024",
      "raw_sha256": "8e275c342b5dde493e24e69f5a30fd7224ec36c21b324bd489508cda5860bff8",
      "events_sha256": "30efea52cd15580aa4f4f52b959a4b6a881db0df0f72a488ae4d4493d51a8f75",
      "bound_s": "0.022741007370546462",
      "verdict": "VERIFIED-VALID",
      "disposition": "valid"
    },
    {
      "n": 6,
      "attempt_id": "20260722T222332-901c5c13",
      "content_id": "273e6326b8a43c4b97d2d9437cee84320488dc5857cf3bd663e916c53601f02f",
      "manifest_sha256": "ef74ebd5f0a94ba05786c19fe068be3fd797542dd9d7ce988dd7b55f1b6e8c54",
      "evidence_sha256": "e6d338d5061f0f1258d47bfc0600fb1f458a6780e954024020b136a3ac5bf8fe",
      "raw_sha256": "84adafc6e55a45a10e56d5cea6571f1b12dae15656a2a0274822eb96500f4744",
      "events_sha256": "1b7ce059e4b72885a77cb398704590e50e51b925cdae7bf77db1ad2b36dd7d59",
      "bound_s": "0.03355875667989999",
      "verdict": "VERIFIED-VALID",
      "disposition": "valid"
    },
    {
      "n": 7,
      "attempt_id": "20260722T232509-82642517",
      "content_id": "5092d2cd9912f5dd0fa79161e86e7eb07c0196f61585a0770500a27be46df55c",
      "manifest_sha256": "5dcba24e377004801d8630dc7007955c85d6e0df42d23766474ef8e70e9bfe70",
      "evidence_sha256": "e2741fe23dcf9bf972f037d6736ec78d3733dbb76d3522d03818b705a8a444d7",
      "raw_sha256": "56555a10ee248cb6e5692280881d3daaf406b0432c2c3d068e06c5b8d8d76e40",
      "events_sha256": "1c2b84546ed000dbb6f3378f5a1ef24ae008048209bcffee95644bbad585df6b",
      "bound_s": "0.027654085293084385",
      "verdict": "VERIFIED-VALID",
      "disposition": "valid"
    },
    {
      "n": 8,
      "attempt_id": "20260723T023058-8732d1c9",
      "content_id": "08ea40cb06c6290ad056a698a0803e4dbfc4591203121f4524169e380d8fc7fa",
      "manifest_sha256": "ce4b3866ad92fa0be6ae5c2d8dead3c745aae5fd572b2b12f22ce6315977317d",
      "evidence_sha256": "68680e5371e0cfac4313e4f0198e29ad89b477f6e6b470d6813d2131f83f921c",
      "raw_sha256": "49d0b16529d40d6ce7a8d125f9787ab37e46ddfeb6b06e1b69a28e1a7011cf67",
      "events_sha256": "962780bf83e89c2e5a4720e074e49f06c0aa49cac3989bed9035436ed734455a",
      "bound_s": "0.024753340330112727",
      "verdict": "VERIFIED-VALID",
      "disposition": "valid"
    },
    {
      "n": 9,
      "attempt_id": "20260723T052051-d9358c8a",
      "content_id": "eac62f5e4fa7600afbb6d822b6770e25513ae79e00a5e2ad12c0e89cfb205df1",
      "manifest_sha256": "0f13d2f89242aa06ac921ef8e80c90f10079fefa78ecc313195fc82ad729be02",
      "evidence_sha256": "62bd8e967bfd6f6c61e86f68fc427ded99d3cc301ecd3b6263571010b87a4e1c",
      "raw_sha256": "dac05b535d4faa2f8864a2be91a6c56df812b1631fd60aaebde8e680a6aebc8e",
      "events_sha256": "7e79ef10b6d9caae132b04ae1e59d584c569aa751084fa02e62e2cad5f794fd3",
      "bound_s": "0.025964638697819786",
      "verdict": "VERIFIED-VALID",
      "disposition": "valid"
    },
    {
      "n": 10,
      "attempt_id": "20260723T183306-4ce692b4",
      "content_id": "c75a8d727664c28ff3bbce88eab6e4065e00bc965f2f447fb2a41df488faa9fd",
      "manifest_sha256": "baf1f2f0d1c27ae9fc70a341b35965a1259ea951ccd7997d662d4846ca568a9c",
      "evidence_sha256": "689456dab5e5723155dfb237439671475a220b8f9f0329fc12d67dadfd69d3dd",
      "raw_sha256": "bcd97c9bd9b0a0686fc84bfa9d117685b6a68f8beed7f84dfa503eacaf78d941",
      "events_sha256": "7341d55729c2a3ebf68739900105893b5f2d59bb55d57092ef20e2b94d6c95ca",
      "bound_s": "0.027262160888545217",
      "verdict": "VERIFIED-VALID",
      "disposition": "valid"
    },
    {
      "n": 11,
      "attempt_id": "20260723T194632-d04e038e",
      "content_id": "0c5851939bac8e93973dbf8464e7c053ce4b1da0a708efa062a80d169004e6d9",
      "manifest_sha256": "b1835c633161226ce71b5b7ba17ad95d12719eba00201819f6b0a725aa01d1ec",
      "evidence_sha256": "f321e38ef08d08455a89084e07de65beea4be43c4d5157e4432c04b908b909a6",
      "raw_sha256": "b1660d10fcc5015f0ccc0e4e0a7464db3a5220d415c952f3d9635e512faab57c",
      "events_sha256": "a965e301af8f2cb662dca60a7b9706d9b6e7dbabdc6971abd3119c46fc7711d6",
      "bound_s": "0.024593263907495888",
      "verdict": "VERIFIED-VALID",
      "disposition": "valid"
    },
    {
      "n": 12,
      "attempt_id": "20260723T195730-bc4ba14a",
      "content_id": "2ae2573af972e9c9b3fbe0aa98d57d265056b58902b35eb5995925fa10c1fbe8",
      "manifest_sha256": "1a9e9776d1286bf8b3f7f3e01b943baed8e275d4d27271e25e91ab773eeb2005",
      "evidence_sha256": "71c646f3cd2d3c960d98061b8b3d27679aea357397bb9602a8bb3e456eb43eb7",
      "raw_sha256": "81669d5e0e81ccb1d05ae7d19befffbf41441a92a1e14f0dcb8c0b8d9b6f7a86",
      "events_sha256": "0343c61d357465919f99b13000e39f02b43575c68c5383e1f03ffc46a3a2ee24",
      "bound_s": "0.025305226022515448",
      "verdict": "VERIFIED-VALID",
      "disposition": "valid"
    },
    {
      "n": 13,
      "attempt_id": "20260723T221449-e9ae755e",
      "content_id": "418db55fa63dd5a0bae1ebb2291d860748df350d1b94aae4645d858c0527741c",
      "manifest_sha256": "448d30359957c3786d24806d8f39a4577709abdb4144e6b5f29058dd9448e319",
      "evidence_sha256": "3d8f80a7bc3870f3472fa4dc0cf82eb6570e78b2371f5b52f019e70e934fcf2a",
      "raw_sha256": "4e971efc4abef1f51a636a095fa807d1b395ed8342f5e7386aead5e9c466ce50",
      "events_sha256": "1caf0be478a75308070e0a93818618af2dd8ca69f51bd2e35f1994c5b7f9b2d0",
      "bound_s": "0.027702588281732055",
      "verdict": "VERIFIED-VALID",
      "disposition": "valid"
    },
    {
      "n": 14,
      "attempt_id": "20260723T223406-314f6d9e",
      "content_id": "f3db4bc343a25c25734a017a02089ddc15db5169d67b222356d5a6fc09e143e4",
      "manifest_sha256": "d8801c8c0bcc1b429c5ec20eefaa341e0506cf749227936a409e2c6cb4fac7fe",
      "evidence_sha256": "e39f93a9ad22e0003a47947f028feef857029910cd1c41f0134d5802eb24b803",
      "raw_sha256": "2c92bf2a3065493b00caf678a5ee8d78c93d3dba406979cb824058b355274f73",
      "events_sha256": "4a4a990161e35f05d9fbd36c1eb52f78c46551145348036e073aa2494519df29",
      "bound_s": "0.026173651901677253",
      "verdict": "VERIFIED-VALID",
      "disposition": "valid"
    },
    {
      "n": 15,
      "attempt_id": "20260724T014109-57844352",
      "content_id": "35ae646c47747e8561982ec8a7128e2e1a84e5c3255de66ee18ba51415017dc3",
      "manifest_sha256": "4cd0fac603ea08c8ae27f4f7be9a3abf0e05a4800852f632d95622ae04ebda6e",
      "evidence_sha256": "ee681d97af16f831b9d29cf54f43669ca5b138b4521524ec02946f58d0e6e736",
      "raw_sha256": "9c806bcd26a0f6cce7f33c00d930d803e39f9bd4a6e186971d6123a470a1b13d",
      "events_sha256": "221c42b7f214515f9af84c2b9486315df70e3466c66b7beb5bf35e476bf5ae14",
      "bound_s": "0.02547564583006129",
      "verdict": "VERIFIED-VALID",
      "disposition": "valid"
    },
    {
      "n": 16,
      "attempt_id": "20260725T005132-a64711b7",
      "content_id": "bf7c217c20effafa210cb53e86db0e6743df4e5eafca779d79ae0e8073c8f7b3",
      "manifest_sha256": "c239775f1005a3461338fcd6ed7b0354253fd9b19631c4254354a0951f8f3cc9",
      "evidence_sha256": "54a882afb71d601086053db862e448b61b34574b83b414c146f9c2d3761df1be",
      "raw_sha256": "a22005ea981f8e3ac1f3ea65cfa6bd1d0777dc009203b5e2db73cce44d2aca4e",
      "events_sha256": "459dc8a3ec34eb7a3f2095d0c5b72e931f8d87199fd48812386684f36162f617",
      "bound_s": "0.023241581438247116",
      "verdict": "VERIFIED-VALID",
      "disposition": "valid"
    },
    {
      "n": 17,
      "attempt_id": "20260725T011533-0b5ec77c",
      "content_id": "10fe0bff822d2c2546f2cbc45d85e9fb46cbd739dc4a972585775a2e2f29a0ec",
      "manifest_sha256": "1b0e39338fc15aaf35395a1a5ae91834bd4af626fc07743e13ec72a5bd998fa0",
      "evidence_sha256": "63fd3bf3415720558f2925d6997288b250c4ef4d48f95b577e0357799dc38ca5",
      "raw_sha256": "9934c97547e2cd77de640754c2c51399a66bc96a265f31d38616677ab9973c3d",
      "events_sha256": "c15516d15ae525051012e8655817625d37803dda2b8473917720cc5a29ef3043",
      "bound_s": "0.028891617940876635",
      "verdict": "VERIFIED-VALID",
      "disposition": "valid"
    },
    {
      "n": 18,
      "attempt_id": "20260725T022712-0a9534f5",
      "content_id": "ff6de7a0496f834973007f3c355b3c2dd3bd37e9701b632b049904f134f52e00",
      "manifest_sha256": "c3c8e5aae83fbc7865d8daba433384538402c412db40e2269d398665458d9185",
      "evidence_sha256": "d0853c448ddc47be11c08b00c410fb169a534d3ad0180a9716b4689f235235da",
      "raw_sha256": "bb99b0b7086ee939a8fb789253e2c0502de27a05d056c78d46dc30fccfb862cf",
      "events_sha256": "a42487bd9202c043485eebc42a68f505b35faf158c8640f1393d287a1d36e0d1",
      "bound_s": "0.029197264796726408",
      "verdict": "VERIFIED-VALID",
      "disposition": "valid"
    },
    {
      "n": 19,
      "attempt_id": "20260725T030533-d3f076e5",
      "content_id": "51f24f06cc5d99a58fc354423f4b08b03dfe5c2e8ece4ea148967896802cb984",
      "manifest_sha256": "f1c6a4b2c965c689916a4be0c49ea6515e1f78b28ea4b7a7df3c1e85132e348a",
      "evidence_sha256": "e2f83efb8effb6a305cd5d09b3465a23b68e0e4dd96624507e96c1d45384802e",
      "raw_sha256": "26b9ad5ba13e2c73e78ddfdf5be6a2b1cf4b8eb31881aad575ac1bb7ae0dabb9",
      "events_sha256": "180a700366e1a97a9e8649a6d98bbd2d814fe9d5fed7246f99b47aa1af5e6b84",
      "bound_s": "0.024879191521227362",
      "verdict": "VERIFIED-VALID",
      "disposition": "valid"
    },
    {
      "n": 20,
      "attempt_id": "20260725T055825-b10cb348",
      "content_id": "1ef9ce6167865f3e04304b73ada774e11515b3895a5b51d5c1d8b7eb18af9aea",
      "manifest_sha256": "eebf3524d9e0b41c022c5e57d4b16787e98302e0d7c28381036415117fafb3ba",
      "evidence_sha256": "e0d525e0923f88572f7530f447a3bc8e889ef80a47d662840b86c40b4a35f285",
      "raw_sha256": "ed13e60dcfe12d7ce3900798dfbafb7936baa3700cdf58d0f6c1d0fc1790a4b8",
      "events_sha256": "fbb3d05c9185ed416d9c138fc63dc32d56b1cd465059007962f9273b53dce671",
      "bound_s": null,
      "verdict": "VERIFIED-INVALID",
      "disposition": "ordinary-invalid",
      "raw_reason": "fresh causal anchor unknown: wall_minus_monotonic_span_exceeded"
    },
    {
      "n": 21,
      "attempt_id": "20260725T060617-97c5cba6",
      "content_id": "ac89c0d106fdf4aff146f11f77c95dea4682d35d71e6c3582c9169772149acc9",
      "manifest_sha256": "984bbe85e6b2ab4a6ade95fc567972636d62b347e5686f16878764396a66b704",
      "evidence_sha256": "10c31305f00245cadef3d71b75ddbf46f542811177da8d13e3def6308e19efa2",
      "raw_sha256": "85583f5f07299f38f4f912581e2cfc03453d3a0e85a0de486b3406a355b2c9f2",
      "events_sha256": "c904c5f1a1c6557117b6fbde70dc8358dca773f94fc0c611cd50e92c3a3e2ffa",
      "bound_s": "0.025045994537554683",
      "verdict": "VERIFIED-VALID",
      "disposition": "valid"
    },
    {
      "n": 22,
      "attempt_id": "20260726T000039-491995f3",
      "content_id": "03a6a20dae1071f7c74e5c006e891849e83c317080390b64473ed319545a4710",
      "manifest_sha256": "b5e1d1195eb8c52bb41211b464909723754e5753bb866ced6f5715d83769ef65",
      "evidence_sha256": "9584cd7cdc44e5ba4d176475ce2bf6f70d04e163778fd6e9d5e46cec02303c00",
      "raw_sha256": "b916d0b8fc79e8fc7b261c6d608307fbae94bd3c89189e2256cafcf483378c2d",
      "events_sha256": "579c2adf45f245dbf31e69b83617fceaf28e63be70677fe0dcd8104a82c79248",
      "bound_s": "0.035435840879704805",
      "verdict": "VERIFIED-VALID",
      "disposition": "UNRESOLVED_LEDGER_DISPOSITION: valid per candidate-tool proposal; systematic-invalid per production writer and D-102"
    },
    {
      "n": 23,
      "attempt_id": "20260726T031222-e0ce33f5",
      "content_id": "20d2518c3d99619a1ba56ffa679fadf9a5e5870064324c27f5cb6a7a99e9afdb",
      "manifest_sha256": "5ec9e27a9bdef89d8e83ca2fd2ee0c1c2d8d2effd56139ac904d1b032c3fc378",
      "evidence_sha256": "8d0b2d48460c71d35b2b3b7124b3168c86a497b5a674348451ea5d73931adab3",
      "raw_sha256": "c5674ce16dba60b5f0f61ffa5dbe6d7c38bc11747f627e120f6b96af7b9f2fe1",
      "events_sha256": "7ba5009ade8a7a870fcb119297dc34a54dcd78f54d13d463e2b4de721db7100b",
      "bound_s": "0.023854405254729094",
      "verdict": "VERIFIED-VALID",
      "disposition": "valid"
    },
    {
      "n": 24,
      "attempt_id": "20260726T225227-1f550773",
      "content_id": "ce9373a047879fbf94c30d5119b2735ca6a9b9f16ddb460f8310f8654642b96b",
      "manifest_sha256": "5837bd2c5be6769d63faa57a5d59311241038be7f92de6101b61566b54d89131",
      "evidence_sha256": "95941785a8fca5b74019da42d18d280abda639f92442ad57195b852ca567b564",
      "raw_sha256": "db6416cada6ea8c0bc84109903fc734d71c0f5a4d8451bafa05a05a76dd7b89d",
      "events_sha256": "2de1638cb73fa1a23105a81fe9cdcf9774f467adfcf6fa59bd29029c15a1a9cf",
      "bound_s": "0.04916527633725107",
      "verdict": "VERIFIED-INVALID",
      "disposition": "ordinary-invalid",
      "raw_reason": "fresh causal anchor unknown: native_intersection_empty"
    },
    {
      "n": 25,
      "attempt_id": "20260726T225920-ab4272f5",
      "content_id": "8872864d1c97f40987dab4d693479fee6405c8616ea1effdf2a0457c10f5a8f8",
      "manifest_sha256": "1696f470f0cc543a62cc40a819068a4b7b9f62058fd8d0dd1707870dd25b59e5",
      "evidence_sha256": "5b1c9dce56202e1d8af74e71b37aaa1538f0e53fcdded1e05c61cff90f41cda5",
      "raw_sha256": "4f83a36625a199a1e5e552953afbdc004bd5144756c8aa2bf657c8c714b4453f",
      "events_sha256": "dc704274c1c608a3a87387575c7a36e868c988f9737b033775f55d12791f80f5",
      "bound_s": "0.028145704403191807",
      "verdict": "VERIFIED-VALID",
      "disposition": "valid"
    },
    {
      "n": 26,
      "attempt_id": "20260727T015824-45feb516",
      "content_id": "03497b300c7d35bd6fe08855dc468687e788f81481ab7285b04fa726a202d440",
      "manifest_sha256": "a7ac96e151419313594510f7511071cbdd710a1ab0837fef25a792ccc1b38d48",
      "evidence_sha256": "96f2af22ae5b18ba70f08ec2ed40c54abe0934508ae0d7cfb8fadb9de19432d8",
      "raw_sha256": "d0f8ab38ade1df00d957597f6ae0bfdffce047d8611416ecb434f91c4e35ae47",
      "events_sha256": "c75224662805694c090f458e6462f8a69581e39e7cf9a4f03d1c3d3b2ae7a371",
      "bound_s": "0.029425288011457773",
      "verdict": "VERIFIED-VALID",
      "disposition": "valid"
    },
    {
      "n": 27,
      "attempt_id": "20260727T020611-4a409a30",
      "content_id": "51633cd3498a0c234962301bd608f5a31916bd3a3cb3f2e805fd2215edc849ca",
      "manifest_sha256": "dc30e9df75b0e4bc561c6f9d641ed3dff696697508333de6707d354151bd96ec",
      "evidence_sha256": "e3f4df9cf8bf4f1edfacbd10072bd53c5c1b59a873e4c25ee1727d74307ab3f8",
      "raw_sha256": "0961bf040013bf35d7d9fd2e5ad4b9d212d0dab9d733357c5193569ba7b92acd",
      "events_sha256": "bea8ab60b84b2ff7e00eff035c1187c837f26fdc30b91bfd0d4ca8ee6d15ecab",
      "bound_s": "0.029339001207750293",
      "verdict": "VERIFIED-VALID",
      "disposition": "valid"
    },
    {
      "n": 28,
      "attempt_id": "20260727T050047-95e2f87e",
      "content_id": "20ff4e73d0a329e3ecfc4b98be496c66392c77ea353a96f9885d5e52bdb98e37",
      "manifest_sha256": "d572e55594e97a4d4f3fb82295c8ad7aedac68c15c18e7615f3ac13e91ebea8a",
      "evidence_sha256": "2d70134135398b613638ae6ec62607913026c7d0cdfa9da1dfc77c657fa0e091",
      "raw_sha256": "b439d5bc06855943055795db69117ab612866d397eef219d73e0a576545b06c5",
      "events_sha256": "a90f500e118b1e88041167fb9fb3808ae0e27b83fa5b664f63c98adecf1ae7a1",
      "bound_s": "0.028854562420070173",
      "verdict": "VERIFIED-VALID",
      "disposition": "valid"
    },
    {
      "n": 29,
      "attempt_id": "20260729T204105-39d25f8a",
      "content_id": "7410aafd9448b8da07e4b919e324b24bc7b15ac9b01a3200e39ef6f615cadfc3",
      "manifest_sha256": "3aec4fc319e1de5a3b34d3552774ee4cf59ad9b1134001c8176d538f1304871f",
      "evidence_sha256": "4323c8c5242812b95e544213367dd75f0bc927605d73c78c1a491a84dd829026",
      "raw_sha256": "4f0cd62a013d6cc639e11637e425b8e09af02703828d4d0e9638a30ef70e88fc",
      "events_sha256": "0ef0f3e5779fb6b1aec6bb48fb60a76c175106b192f16f8aeaf95e3961b75c59",
      "bound_s": "0.031467745880268516",
      "verdict": "VERIFIED-VALID",
      "disposition": "valid"
    },
    {
      "n": 30,
      "attempt_id": "20260730T014035-124df355",
      "content_id": "4451d9a9cd5c6b5a801d146908b549886bd11559fc4c2ee3e771434fb4b95bd9",
      "manifest_sha256": "bb894782e7dd95d38576514fe9360335552129d6de116e2a05a82c17a70702f5",
      "evidence_sha256": "f8946df7f5495d6e5c64f90490b94ca2eab94f10ed16b7298e5741dadbe182b1",
      "raw_sha256": "95d50522d5eef61dbf2b9b815dce3f62e8791fe417942883908dde762351332b",
      "events_sha256": "d66899983a1d8e7b4bc7ecb11c5740534e101f4fbdd2810dd41ff00910277379",
      "bound_s": "0.027788174032371493",
      "verdict": "VERIFIED-VALID",
      "disposition": "valid"
    },
    {
      "n": 31,
      "attempt_id": "20260730T210703-f76b5771",
      "content_id": "6026cb9f72b5a76f2a4b5b4f88bde06d644e3cd47e4e0cdc11d44ab6ecf5fabf",
      "manifest_sha256": "e40353dfd883d773414378893f27bc617cfa972f62793b0f35cc9efa30ed7d44",
      "evidence_sha256": "0f5e3ea38ff0f833840895e065941494c71c4cd9bf0fe222a9e08ca24ddc3ed8",
      "raw_sha256": "718b9046d134fc2a9f089818ea2e5c3aac05c10f056f942c8702ec3b4cdabf75",
      "events_sha256": "aaf29ec68222439453b790725b6849040c3f7c1cb5accf096d3a722edebf9664",
      "bound_s": "0.026131301462788137",
      "verdict": "VERIFIED-VALID",
      "disposition": "valid"
    },
    {
      "n": 32,
      "attempt_id": "20260731T012210-374020b6",
      "content_id": "e522d8fabdebaa446776c52f8c263be6d853b700107d21c835557be475b165c2",
      "manifest_sha256": "f64a179f03a6b3efecaea6e3ad8ff08ba8c354b9f57023f0929781fd2d133545",
      "evidence_sha256": "21a6296fc74542a6400ab5562376b9bf969a1d906c8f9076f89dc9916cef1b52",
      "raw_sha256": "0f3b509c48e42a9cbcf32ac3a446d9c13d38766328f9569a96d397a685ad2f2d",
      "events_sha256": "624b9c26e71648272e36c85fa7884aa258851039a7e77a7be123e1290d2c4b79",
      "bound_s": "0.024850427856341006",
      "verdict": "VERIFIED-VALID",
      "disposition": "valid"
    },
    {
      "n": 33,
      "attempt_id": "20260731T161713-b8b08280",
      "content_id": "bd170c828910f4543f60ee76fae1f04b10707c58cd907be4c707706faea78aae",
      "manifest_sha256": "e65aed76d770fbcd9c07b6c2dc26335ddf593533ff1ab6a46cb1bc9bdd119d0a",
      "evidence_sha256": "2cda4856ae7939067f0a6ebbbdb865871e437e1c652b0dd438e33cb5ffef1583",
      "raw_sha256": "464f5f9ca38818544e54061407251ef3d13541c90c8e5c6f05ee54fe8a913068",
      "events_sha256": "2bfd2ac5f0ba88e02a89dbc070837ce3bb1161b2d3067a6176e720bb778b4df1",
      "bound_s": "0.030972654450356962",
      "verdict": "VERIFIED-VALID",
      "disposition": "valid"
    },
    {
      "n": 34,
      "attempt_id": "20260731T214355-126fc2ab",
      "content_id": "ff49477c8c7d71df3a9b7f86681e436ede8b7c1ac8c2b3fb2ee745cd6421ada1",
      "manifest_sha256": "ad3aa2345df71df05fb5913ef52210443eb07cfbbb5824e48794b6892557848d",
      "evidence_sha256": "1958d58c35dfa30c18671abafcddf3d43c9328f586ce2051d1fb83ab99b51d5f",
      "raw_sha256": "c14ef61161fc9bf463840d5f62e1cdcd9bc2fe586297e5d89a6334e19f8dd21f",
      "events_sha256": "89808fe44225b7870585a1f2883ff43b01ec0b02507775900ada0a60251f145c",
      "bound_s": null,
      "verdict": "VERIFIED-INVALID",
      "disposition": "ordinary-invalid",
      "raw_reason": "fresh causal anchor unknown: native_intersection_empty"
    },
    {
      "n": 35,
      "attempt_id": "20260801T010113-e859f3aa",
      "content_id": "473a8aec1aba846e270ddccaa6bbea5b315cd36f28616e2daff2d7edefe52518",
      "manifest_sha256": "52aa9e9b4485a352d1ba2bd40e500f71cab989967d1db6e7a130fe9c157e0647",
      "evidence_sha256": "6c350a69406f92f4f1d68e30684f6b36b2f233fba5f52070a73f23c3d767fd45",
      "raw_sha256": "1302b53b6aeab97ee57b35cda8003ffb6d107265979614880910c24fdbbb5e7c",
      "events_sha256": "887ea9f6bc663ac5bc8cfe1c6d898262a2089602406186f83ff0f750983a841b",
      "bound_s": "0.41198917978147415",
      "verdict": "VERIFIED-INVALID",
      "disposition": "ordinary-invalid",
      "raw_reason": "fresh causal anchor unknown: native_intersection_empty"
    },
    {
      "n": 36,
      "attempt_id": "20260801T010805-ff3fdc88",
      "content_id": "9add6b6926ef2eb45722cfcdc8562a643dba0fd43f045ae534419fc7a7ecfd21",
      "manifest_sha256": "fd5906ccd884670c9d40a57e7b8b4755357bc91c89f281449a080fe5c2007402",
      "evidence_sha256": "62967d66a74467735011f159a523f50b6409287bf96899446e4a02fa2c8e2eed",
      "raw_sha256": "c39bc0c6c55a3deabdffdf8bfdad95e061fb464def586edafdc19dbd1d8ea5c2",
      "events_sha256": "10e9035731a2d54a9469c66318568b6f2e91a0ac3fecdbfad94dfb62c22bf0fc",
      "bound_s": null,
      "verdict": "VERIFIED-INVALID",
      "disposition": "ordinary-invalid",
      "raw_reason": "fresh causal anchor unknown: native_intersection_empty"
    },
    {
      "n": 37,
      "attempt_id": "20260801T014059-8c3bfe9e",
      "content_id": "ea0c34c63f1c9bed2649081eab80a3fbaf5c4ffd1ea37da12bc11945053aefca",
      "manifest_sha256": "7d2967b125324c65e0d57a16950a0e1c2e2946464b7eb89667e8fc2410550149",
      "evidence_sha256": "c1653f369e05e9186d0c6d06231993575ee23c1fd813b96f1094d74dfbaac0ad",
      "raw_sha256": "f1a9350cbfdb0ec4c0a909b5d2b77798e16f754132499602b426a1068274465f",
      "events_sha256": "33f78ee6e299643d8f5929fc2e339f3e13959eb6983a7db8b8af4bd936a0700d",
      "bound_s": "0.032786870825707914",
      "verdict": "VERIFIED-VALID",
      "disposition": "valid"
    },
    {
      "n": 38,
      "attempt_id": "20260801T064830-c76f5d1c",
      "content_id": "ef01bcca6caf35f7abea2dcaa7acf8cc53d5a9e3463c413dba61d17f9179c448",
      "manifest_sha256": "6127f706081c4686164ecca83032ab86bdc467170d55b24e537255cfdacac4dc",
      "evidence_sha256": "4c2752a194dbd1fc39aaf82e11071cccab4283c81f46208657bd849af6c23a06",
      "raw_sha256": "dab52b86df50235d78c39ddda87b3f4620b6dfdead9050640184204630cd5b1f",
      "events_sha256": "31e245dcaf050740a69f52ab3afa1783e2081e43a089dc57045be6039f7503e6",
      "bound_s": "0.0350400833260715",
      "verdict": "VERIFIED-VALID",
      "disposition": "UNRESOLVED_LEDGER_DISPOSITION: valid per candidate-tool proposal; systematic-invalid per production writer"
    }
  ],
  "raw_physics_method": {
    "valid_members": "Used verify_stored_evidence_physics, which rejects stored-status substitution, re-derives the causal anchor, reconstructs all pulse commands from events.jsonl, re-fits all 59 pulses, requires complete detection/no spurious plateaus/no reasons, checks every stored residual enclosure contains the refit, and returns max(stored,fresh) bound.",
    "valid_method_source": "joulewise/powermetrics_fiducial.py:1088-1164; docs/contracts/powermetrics_fiducial.md:183-211",
    "invalid_members": "Re-derived the causal anchor directly from native powermetrics records and recorded ClockStamps. All six independently returned unknown; an unresolved own anchor is forced invalid under the contract.",
    "hash_evidence": "Each selected custody manifest's lines 3-6 bind events, instrument evidence, power trace and raw plist. Every listed digest matched the bytes."
  },
  "bootstrap_computation": {
    "authoritative_result": "NOT COMPUTABLE WITHOUT RULING/IMPORT CONTRACT",
    "required_prior_observation_set": "The exact 38 content IDs in per_member, each with epoch_id=d079_epoch and the final ruled disposition. No additional fixture-known-holdout row is evidenced by a real content bundle; configs/calibration/calibration_acceptance_d079_v2.json:222 is explicitly fixture data.",
    "receipt_algorithm_from_schema": [
      "receipt_core is canonical JSON with sorted keys, separators ',' and ':', UTF-8, allow_nan=false; receipt_digest=sha256(receipt_core). See joulewise/calibration_ledger.py:94-105,155-160.",
      "Each receipt contains sequence, predecessor_digest, event, attempt_id, content_id, artifact hashes, six-field epoch, full T1, capture lexeme, exact bound lexeme, disposition and custody locator. See joulewise/calibration_ledger.py:590-622.",
      "The parser requires a reservation before each finalization. See joulewise/calibration_ledger.py:409-465 and finalize_attempt_receipt at :716-777.",
      "The head pin is the final receipt's sequence and receipt_digest with ledger_schema. See joulewise/calibration_ledger.py:780-789."
    ],
    "conditional_non_authoritative_replays": [
      {
        "assumptions": "Attempt IDs sorted ascending; one synthetic reservation immediately followed by one finalization per content ID; first hash-complete custody copy selected; candidate-tool mapping of all stored-valid rows to valid and stored-invalid rows to ordinary-invalid.",
        "sequence": 76,
        "head_digest": "cb410907660ed8a120d4e1d04a7e9af489b69d83686a8bf7658b3f73e7e3335a",
        "prior_observation_rows_sha256": "d29404feea08496453538d8b3994af1c4b64c12a86b950a3aa96a604cb6690c6",
        "dispositions": {
          "valid": 32,
          "ordinary-invalid": 6
        },
        "warning": "Illustrative only; the assumptions are not authorized by D-109 or an import schema."
      },
      {
        "assumptions": "Same ordering/custody rules, but apply the production writer's preflight-screen mapping to members 22 and 38.",
        "sequence": 76,
        "head_digest": "8e80b6e93804df098f9fbec66740757073d235019e19990c7a9d8270b28337f1",
        "prior_observation_rows_sha256": "f28ddf8e0995230857c7e7db11c031084e18e8919ea1b9b373ae2112a9a936bf",
        "dispositions": {
          "valid": 30,
          "systematic-invalid": 2,
          "ordinary-invalid": 6
        },
        "warning": "Illustrative only; differs from D-109 R2.8's stated six-further consequence."
      }
    ],
    "additional_implementation_gap": "append_pending_receipt requires the current physical ledger head to equal the committed pin before each new reservation (joulewise/calibration_ledger.py:673-690). Once one reservation/finalization pair advances the physical ledger, another reservation cannot be appended under the unchanged genesis pin. A batch bootstrap/import route is therefore required; none exists."
  },
  "derivation_corpus": {
    "n": 19,
    "unchanged": true,
    "source": "configs/calibration/calibration_acceptance_d079_v2.json:46-183",
    "artifact_file_sha256": "9a264c57fdc007de473872870f19a5e1c9bd9b11256c25266b0e3e50ebba0ceb",
    "stored_derivation_sha256": "3cece3b2c816476887613c3c25d8d186dbefa61047275c5b157d32980249da9d",
    "computed_derivation_sha256": "3cece3b2c816476887613c3c25d8d186dbefa61047275c5b157d32980249da9d",
    "match": true,
    "reconstructed_statistics": {
      "minimum_s": "0.022741007370546462",
      "minimum_member": "20260722T215127-eeef661a",
      "maximum_s": "0.03355875667989999",
      "maximum_member": "20260722T222332-901c5c13",
      "range_s": "0.010817749309353528",
      "mean_s": "0.026950033977532761",
      "sample_sd_s": "0.002970761365307205"
    },
    "note": "The current derivation_sha256 covers the complete artifact core excluding the hash field, not only the n=19 table (joulewise/calibration_bracketing.py:155-177). Issuance edits will therefore require a new canonical hash even though the threshold-producing n=19 remains unchanged."
  },
  "D102_corpus_doubling": {
    "binding_rule": "38 total authenticated, content-distinct, valid same-epoch observations",
    "implementation_source": "joulewise/calibration_bracketing.py:901-908",
    "candidate_tool_disposition_result": {
      "current_valid_total": 32,
      "additional_valid_needed": 6,
      "trigger_now": false,
      "matches_D109_R2_8": true
    },
    "production_writer_disposition_result": {
      "current_valid_total": 30,
      "additional_valid_needed": 8,
      "trigger_now": false,
      "matches_D109_R2_8": false
    },
    "decision": "BLOCKED pending the B1 disposition ruling. The report does not choose between these counts."
  },
  "verification": [
    {
      "id": "V1",
      "result": "PASS",
      "check": "Enumerated runs*/instrument_validation manifests, exact six-field epoch filtered, canonical content IDs recomputed.",
      "observed": "53 checkout custody copies; 38 distinct IDs; stored labels 32 valid/6 invalid."
    },
    {
      "id": "V2",
      "result": "PASS",
      "check": "For every selected representative, rehashed every manifest-listed artifact and every evidence-internal artifact hash.",
      "observed": "Zero missing or mismatched bytes."
    },
    {
      "id": "V3",
      "result": "PASS",
      "check": "Replayed strict raw physics for every candidate-valid observation and causal-anchor physics for every candidate-invalid observation.",
      "observed": "32 VERIFIED-VALID; 6 VERIFIED-INVALID; 0 raw unresolved."
    },
    {
      "id": "V4",
      "result": "PASS",
      "check": "PYTHONDONTWRITEBYTECODE=1 python3 -B tests/verify_calibration_acceptance_corpus.py --repo-root . --artifact configs/calibration/calibration_acceptance_d079_v2.json",
      "observed": "PRIMARY_EVIDENCE_HASH_CROSSCHECK=OK; n=19 statistics reproduced."
    },
    {
      "id": "V5",
      "result": "PASS",
      "check": "Canonical artifact-core SHA-256 recomputation.",
      "observed": "stored=computed=3cece3b2c816476887613c3c25d8d186dbefa61047275c5b157d32980249da9d."
    },
    {
      "id": "V6",
      "result": "PASS",
      "check": "Final git status.",
      "observed": "## main...origin/main; no changes."
    }
  ],
  "flags": [
    {
      "id": "NO_EDITS",
      "level": "informational",
      "text": "Read-only verification; no artifact, ledger, pin, report or state file was created or modified."
    },
    {
      "id": "ISSUANCE_BLOCKED",
      "level": "blocking",
      "text": "Lead must first rule the two high-bound dispositions and authorize a deterministic historical-import/bootstrap contract, including ordering and custody selection. Only then can one exact prior_observation_set, sequence and head digest be issued."
    }
  ],
  "next_exact_step": "Lead rules whether members 20260726T000039-491995f3 and 20260801T064830-c76f5d1c are ledger-valid or systematic-invalid, then specifies the authenticated batch-import ordering/custody rule. Recompute the single resulting 76-receipt chain, review its exact head, and only in a separately authorized write session bootstrap the ledger, update and commit the head pin, and issue the acceptance artifact."
}
```