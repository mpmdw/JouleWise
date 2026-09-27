# BFGS S1 fix-round verbatim verification transcript

## Forward check A

Command: `python3 scripts/build_battery_float_historical_bundles.py --check`

Exit: 0

### stdout (verbatim)

```text
forward check: byte-identical entries=69
```

### stderr (verbatim)

```text
unparseable docs/legacy/process_traces/2026-08-06-d079-issuance-coldgate/ISSUANCE-execute-summary.json: JSONDecodeError
unparseable docs/process_traces/2026-09-16-activation-9853dd2b/77-arm-evidence-n1-20260917/arm-census-final.json: JSONDecodeError
unparseable docs/process_traces/2026-09-16-activation-9853dd2b/77-arm-evidence-n1-20260917/arm-census-staging.json: JSONDecodeError
unparseable docs/process_traces/2026-09-18-activation-d8ca3a36/08-adhoc-corecording-state-3seats-2claude.sampler.jsonl: JSONDecodeError
unparseable docs/process_traces/2026-09-18-activation-d8ca3a36/21-arm-evidence-n1-20260919/arm-census-1.json: JSONDecodeError
unparseable docs/process_traces/2026-09-18-activation-d8ca3a36/21-arm-evidence-n1-20260919/arm-census-2.json: JSONDecodeError
unparseable docs/process_traces/2026-09-18-activation-d8ca3a36/21-arm-evidence-n1-20260919/arm-census-final.json: JSONDecodeError
unparseable docs/process_traces/2026-09-19-activation-4ca26e9c/01-arm-evidence-n2-20260919/arm-census-1.json: JSONDecodeError
unparseable docs/process_traces/2026-09-19-activation-4ca26e9c/01-arm-evidence-n2-20260919/arm-census-2.json: JSONDecodeError
unparseable docs/process_traces/2026-09-19-activation-4ca26e9c/01-arm-evidence-n2-20260919/arm-census-final.json: JSONDecodeError
unparseable docs/process_traces/2026-09-19-activation-a743be05/03-arm-evidence-qpe01-pilot-n1-20260920/arm-census-1.json: JSONDecodeError
unparseable docs/process_traces/2026-09-19-activation-a743be05/03-arm-evidence-qpe01-pilot-n1-20260920/arm-census-2.json: JSONDecodeError
unparseable docs/process_traces/2026-09-19-activation-a743be05/03-arm-evidence-qpe01-pilot-n1-20260920/arm-census-final.json: JSONDecodeError
unparseable docs/process_traces/2026-09-24-activation-278ebc9e/104-forger-fable/adjudication.jsonl: JSONDecodeError
unparseable docs/process_traces/2026-09-24-activation-278ebc9e/104-forger-fable/replay-check.jsonl: JSONDecodeError
unparseable docs/process_traces/2026-09-24-activation-278ebc9e/105-coldgate-packet-a291-forger2/ex-104-fc-adjudication.jsonl: JSONDecodeError
unparseable docs/process_traces/2026-09-24-activation-278ebc9e/106-forger-fable-b/adjudication.jsonl: JSONDecodeError
unparseable docs/process_traces/2026-09-24-activation-278ebc9e/112-coldgate-packet-a291-premerge/ex-104-fc-adjudication.jsonl: JSONDecodeError
unparseable docs/process_traces/2026-09-24-activation-278ebc9e/112-coldgate-packet-a291-premerge/ex-106-fb-adjudication.jsonl: JSONDecodeError
unparseable docs/process_traces/2026-09-24-activation-278ebc9e/117-coldgate-packet-a291-finalpass/ex-104-fc-adjudication.jsonl: JSONDecodeError
unparseable docs/process_traces/2026-09-24-activation-278ebc9e/117-coldgate-packet-a291-finalpass/ex-104-fc-replay.jsonl: JSONDecodeError
unparseable docs/process_traces/2026-09-24-activation-278ebc9e/117-coldgate-packet-a291-finalpass/ex-106-fb-adjudication-and-replay.jsonl: JSONDecodeError
listed analysis/rpt001-v1/artifact_manifest.json bundle_tree_sha256 tree_legacy 1ffe1ec76e3022bac5bd651b261a044d0865a1d5877c165aa45f96018ff0e1ca: retired tree fold
listed analysis/rpt001-v1/artifact_manifest.json bundle_tree_sha256 tree_legacy 36d3b109ac3a2e88b27434361ccb5b85c84d653b4cb7fabf25b3e222506f57ef: retired tree fold
listed analysis/rpt001-v1/artifact_manifest.json bundle_tree_sha256 tree_legacy 9be1c5df4bb566fbe057735bac5377d6826828f0061f11fee2b48cd74f982ff4: retired tree fold
listed analysis/rpt001-v1/artifact_manifest.json bundle_tree_sha256 tree_legacy b029e14b53a085f74653857a62194ed50a47d63e4bc49d15238ec77ff94cc2b5: retired tree fold
listed analysis/rpt001-v1/artifact_manifest.json bundle_tree_sha256 tree_legacy ec05d3d2c2bd262cb3488c887e4a561ef6c70d6271058f3fb0c0e823e38699cc: retired tree fold
listed analysis/rpt001-v1/artifact_manifest.json bundle_tree_sha256 tree_legacy f9f5896c8edf8b8dc1fd56dee977f5a5b7b4d5a04cc76b1405c865d817f9e279: retired tree fold
listed analysis/rpt001-v1/input_manifest.json bundle_tree_sha256 tree_legacy 1ffe1ec76e3022bac5bd651b261a044d0865a1d5877c165aa45f96018ff0e1ca: retired tree fold
listed analysis/rpt001-v1/input_manifest.json bundle_tree_sha256 tree_legacy 36d3b109ac3a2e88b27434361ccb5b85c84d653b4cb7fabf25b3e222506f57ef: retired tree fold
listed analysis/rpt001-v1/input_manifest.json bundle_tree_sha256 tree_legacy 9be1c5df4bb566fbe057735bac5377d6826828f0061f11fee2b48cd74f982ff4: retired tree fold
listed analysis/rpt001-v1/input_manifest.json bundle_tree_sha256 tree_legacy b029e14b53a085f74653857a62194ed50a47d63e4bc49d15238ec77ff94cc2b5: retired tree fold
listed analysis/rpt001-v1/input_manifest.json bundle_tree_sha256 tree_legacy ec05d3d2c2bd262cb3488c887e4a561ef6c70d6271058f3fb0c0e823e38699cc: retired tree fold
listed analysis/rpt001-v1/input_manifest.json bundle_tree_sha256 tree_legacy f9f5896c8edf8b8dc1fd56dee977f5a5b7b4d5a04cc76b1405c865d817f9e279: retired tree fold
listed analysis/rpt001-v2/artifact_manifest.json bundle_tree_sha256 tree_nul_v1 2888c9d205df62e1136a376997ea8a6947683e4311eedaee20e3135bd559e213: source not named by amendment 40
listed analysis/rpt001-v2/artifact_manifest.json bundle_tree_sha256 tree_nul_v1 5ec71ed301ba9c0a48b137b5bdce00b8893c62d4f1397f55aac3c1943ccc9180: source not named by amendment 40
listed analysis/rpt001-v2/artifact_manifest.json bundle_tree_sha256 tree_nul_v1 8a99d7a851c55e53631df6f910d17ee097cbf8bd19f33d44bcef911a6502e82f: source not named by amendment 40
listed analysis/rpt001-v2/artifact_manifest.json bundle_tree_sha256 tree_nul_v1 9376dbc16848e03d3bd54e4fac5598b34e1391d376ef11db527ac1fe25f08773: source not named by amendment 40
listed analysis/rpt001-v2/artifact_manifest.json bundle_tree_sha256 tree_nul_v1 9f162f058bfceb949f34e0c24042c83e8d7f353f97d87b4cf6e0e6dff0912398: source not named by amendment 40
listed analysis/rpt001-v2/artifact_manifest.json bundle_tree_sha256 tree_nul_v1 c72cdc34ef3ce9ccfb0a015bed5ace8e4efa7d18f457ac5cd8a0c894acc21268: source not named by amendment 40
listed df-ph-decode-floor-mint1.json bundle_sha256s complete 0a22a02caa28f0c75bc460339dd420604638cf5f7aa17a0ca2e4fd1c8afbb9ae: duplicate of included citation
listed df-ph-decode-floor-mint1.json bundle_sha256s complete 0a76e5fbcffdccb44ebc22b8d9d86e259b49d2c529ec89bcc0a24c6f22994899: duplicate of included citation
listed df-ph-decode-floor-mint1.json bundle_sha256s complete 0eb6a006b4afc1cc031a3786a0cc1180686cdb78cb9375788370a3bfd86e8060: duplicate of included citation
listed df-ph-decode-floor-mint1.json bundle_sha256s complete 153af6c4d94ba5f9e67f23cf4151703b27d430717dc3d9b773258f7ffdd40593: duplicate of included citation
listed df-ph-decode-floor-mint1.json bundle_sha256s complete 1624fc548379c427d047187df164fa297bec2080062f28bb809a2dba80c94a00: duplicate of included citation
listed df-ph-decode-floor-mint1.json bundle_sha256s complete 195b495930c4cdd532cfdd4773260ba3de73e585c7a3a9e55bac179e3b984195: duplicate of included citation
listed df-ph-decode-floor-mint1.json bundle_sha256s complete 1a7a291dd1b789f95faf8c873a459fd4d8bb6b26257f8866726151f6c156cb96: duplicate of included citation
listed df-ph-decode-floor-mint1.json bundle_sha256s complete 2863fa61af00fb8e23c68bd6848c9eb7f630d21827aefa4ba9af9b09a05537c9: duplicate of included citation
listed df-ph-decode-floor-mint1.json bundle_sha256s complete 2d1c88636ad93b0727cb01d8d4c70253fc5318ce3033b9d11e2bc0e4d8a68733: duplicate of included citation
listed df-ph-decode-floor-mint1.json bundle_sha256s complete 2ecceeb9237077c2f3a6577c9d7bce24d3deeb926df1e15f1b389bad0db02147: duplicate of included citation
listed df-ph-decode-floor-mint1.json bundle_sha256s complete 32c53e61cdbb8f507eed269af1eeeef69f4105fba8c9d9d2f43f06f8ba9acaf9: duplicate of included citation
listed df-ph-decode-floor-mint1.json bundle_sha256s complete 377f6a786c341eef39d6836cb2d12921ab4a05d434c5a241f5c581d8f4d4a2ee: duplicate of included citation
listed df-ph-decode-floor-mint1.json bundle_sha256s complete 39054c62e30e8362a0ef473fb674aed5d1c87df7c630d0f4daadfd296874439e: duplicate of included citation
listed df-ph-decode-floor-mint1.json bundle_sha256s complete 48a8bb2a6f23c6531eae6f8d99c043e0500379aff9427956fee1b74de75694ff: duplicate of included citation
listed df-ph-decode-floor-mint1.json bundle_sha256s complete 5135406fa3ba08b4df498cfbe12a463607a829db546a13d273e7b97fdb1aab50: duplicate of included citation
listed df-ph-decode-floor-mint1.json bundle_sha256s complete 584b8d1b73e7f5a5d8fe4b1e6b0f5e3a6382bb84a57c5cd6015eda31a26c31e5: duplicate of included citation
listed df-ph-decode-floor-mint1.json bundle_sha256s complete 589b17f6a10c6275407367f7f90bea8ced63dabb70850798e0808626924168fe: duplicate of included citation
listed df-ph-decode-floor-mint1.json bundle_sha256s complete 59aade4961b9e59f1696f88f263204f3739cb7d81adc754cc3380a0133f92691: duplicate of included citation
listed df-ph-decode-floor-mint1.json bundle_sha256s complete 5c7a8a6ce946d88fdd5ea0124bafa1ffad8c289308d5e9b600d2f95e280bb025: duplicate of included citation
listed df-ph-decode-floor-mint1.json bundle_sha256s complete 6a090490fd08e646bc39c4eaa112fffcdf87e0d5f03599af10595512957997f4: duplicate of included citation
listed df-ph-decode-floor-mint1.json bundle_sha256s complete 6cdd0c795befd568798a4ef4538bf6db1ccd930f240de873a77ab36263927561: duplicate of included citation
listed df-ph-decode-floor-mint1.json bundle_sha256s complete 769d1d1378e3603fe40013fadeda35504eca0c235f773106233323fba5a61163: duplicate of included citation
listed df-ph-decode-floor-mint1.json bundle_sha256s complete 8a9216a68466a432fe65e7ff9d48664d1c1e8b297b9a011cbe4f462e291220b4: duplicate of included citation
listed df-ph-decode-floor-mint1.json bundle_sha256s complete 8bc66888f356e9e123d356db3dd1f538e71dada51037f953b8f3055e901447f4: duplicate of included citation
listed df-ph-decode-floor-mint1.json bundle_sha256s complete 8eaba1d3b0069dd913aafabff74f6d2b6dfab066a0b30e8f4f68322a84973903: duplicate of included citation
listed df-ph-decode-floor-mint1.json bundle_sha256s complete 9d67992e7cdd70a86bbbf82ca6a9b587d42779c14a28f72256900331d9f8fece: duplicate of included citation
listed df-ph-decode-floor-mint1.json bundle_sha256s complete a71d5519ecbf8a1659cbdca66d0d80b34e0350a9746ef5637e84e76771e5eea3: duplicate of included citation
listed df-ph-decode-floor-mint1.json bundle_sha256s complete acd77e1d5a8a5bc82493315b772fa616a3cf5c579fda5586e04902fdda388459: duplicate of included citation
listed df-ph-decode-floor-mint1.json bundle_sha256s complete b200324cffed9a1db87323a5961d28dbdc593e743d623423b6862e5f643f5273: duplicate of included citation
listed df-ph-decode-floor-mint1.json bundle_sha256s complete b25522da721b5a7deb6060fa1ed4ce22c174bcefa6d47617a76bfb90b23f4755: duplicate of included citation
listed df-ph-decode-floor-mint1.json bundle_sha256s complete b27c6af7109a5734079ad311df84f812680daa957e2b5121de46372fe6871bf3: duplicate of included citation
listed df-ph-decode-floor-mint1.json bundle_sha256s complete b2b10d7dc7c70820ffa7be4cd6e5c7d99bfb723c24ecc8aa143b92b28a18cca2: duplicate of included citation
listed df-ph-decode-floor-mint1.json bundle_sha256s complete b446e7a59d38287578918f273a1fa512f89f8da1ca4e8304f1f83d7af27dc568: duplicate of included citation
listed df-ph-decode-floor-mint1.json bundle_sha256s complete b65b79bb3f7d7a6c570d882abc6b75bef14c1c56223bfb062f6b40c708a4ad8e: duplicate of included citation
listed df-ph-decode-floor-mint1.json bundle_sha256s complete c285172881235ef1ed0e29731c412706604e8cd182182981a5ed44cc2df986bf: duplicate of included citation
listed df-ph-decode-floor-mint1.json bundle_sha256s complete cac899e4c3fa84eec27f5fc26e0c105f25abc6948190821552f3a89f317fd681: duplicate of included citation
listed df-ph-decode-floor-mint1.json bundle_sha256s complete d88ffadb420cf59aa20a7efc7615a1d7817f91814b0754756b0bc65e51cd57bf: duplicate of included citation
listed df-ph-decode-floor-mint1.json bundle_sha256s complete dc1e56aa1d27fc6ac0bb5d7a80b7881e635a5050e7ffc9536b62c75dd22cee5a: duplicate of included citation
listed df-ph-decode-floor-mint1.json bundle_sha256s complete e339de0c0f2e5b464e73e2423e94ad6a4fa72c2abca68cebeb2d97f3af893109: duplicate of included citation
listed df-ph-decode-floor-mint1.json bundle_sha256s complete e35798402f4af613c21e7bd5069875a4194b6672c3c3ab1c3073fff3ec05b17d: duplicate of included citation
listed df-ph-decode-floor-mint1.json bundle_sha256s complete e7ee36928bac0e65b8004f8f7b7fae0babe3ac706171b26b8dd92015a1f87058: duplicate of included citation
listed df-ph-decode-floor-mint1.json bundle_sha256s complete eb05f32d37b1c8e8969f097a0ff112ea95e7ca9c1110e03127b7538267414449: duplicate of included citation
listed df-ph-decode-floor-mint1.json bundle_sha256s complete ec172522b7ba17c83008f32994e0c727cad2bc857aee4b6a18b4c6ac4ed14446: duplicate of included citation
listed df-ph-decode-floor-mint1.json bundle_sha256s complete ec6fda56898612837eb76d658c9057ab0e08e26689e44b1dea1a296dd17674b2: duplicate of included citation
listed df-ph-decode-floor-mint1.json bundle_sha256s complete ed743899e603951287cce29814371c4949b452a36b65550992535a3e3ffeef3e: duplicate of included citation
listed df-ph-decode-floor-mint1.json bundle_sha256s complete edbaba1c823c33bbc51164f96947a590ab0f4d96569ca221669942500d4ff2cc: duplicate of included citation
listed df-ph-decode-floor-mint1.json bundle_sha256s complete f29039135ac92d31ea88c277682ff79aae0474ac741c2a18d2a1930f71be620b: duplicate of included citation
listed df-ph-decode-floor-mint1.json bundle_sha256s complete f39fcdfe56370dc2ed33f53c6901ebcfda3362193f5f0f865d8b366c0a3eb80d: duplicate of included citation
listed df-ph-decode-floor-mint1.json bundle_sha256s complete fb12d40f5a418462a268587fa9ad8e9bbbef5e32e47132f112e2f3f9d540c5e1: duplicate of included citation
listed df-ph-decode-floor-mint1.json bundle_sha256s complete ffacb0680cf37794804f7af1f5e0bd39fab26160bf134a0cf63525c293155f13: duplicate of included citation
listed docs/legacy/strategy/2026-08-07-paper-portfolio/proposals/prop-param-scaling-energy.md bundle_sha256 complete 0eb6a006b4afc1cc031a3786a0cc1180686cdb78cb9375788370a3bfd86e8060: source not named by amendment 40
listed docs/legacy/strategy/2026-08-07-paper-portfolio/proposals/prop-param-scaling-energy.md bundle_sha256 complete 153af6c4d94ba5f9e67f23cf4151703b27d430717dc3d9b773258f7ffdd40593: source not named by amendment 40
listed docs/legacy/strategy/2026-08-07-paper-portfolio/proposals/prop-param-scaling-energy.md bundle_sha256 complete 195b495930c4cdd532cfdd4773260ba3de73e585c7a3a9e55bac179e3b984195: source not named by amendment 40
listed docs/legacy/strategy/2026-08-07-paper-portfolio/proposals/prop-param-scaling-energy.md bundle_sha256 complete 2d1c88636ad93b0727cb01d8d4c70253fc5318ce3033b9d11e2bc0e4d8a68733: source not named by amendment 40
listed docs/legacy/strategy/2026-08-07-paper-portfolio/proposals/prop-param-scaling-energy.md bundle_sha256 complete 5135406fa3ba08b4df498cfbe12a463607a829db546a13d273e7b97fdb1aab50: source not named by amendment 40
listed docs/legacy/strategy/2026-08-07-paper-portfolio/proposals/prop-param-scaling-energy.md bundle_sha256 complete 8bc66888f356e9e123d356db3dd1f538e71dada51037f953b8f3055e901447f4: source not named by amendment 40
listed docs/legacy/strategy/2026-08-07-paper-portfolio/proposals/prop-param-scaling-energy.md bundle_sha256 complete 8eaba1d3b0069dd913aafabff74f6d2b6dfab066a0b30e8f4f68322a84973903: source not named by amendment 40
listed docs/legacy/strategy/2026-08-07-paper-portfolio/proposals/prop-param-scaling-energy.md bundle_sha256 complete b200324cffed9a1db87323a5961d28dbdc593e743d623423b6862e5f643f5273: source not named by amendment 40
listed docs/legacy/strategy/2026-08-07-paper-portfolio/proposals/prop-param-scaling-energy.md bundle_sha256 complete b2b10d7dc7c70820ffa7be4cd6e5c7d99bfb723c24ecc8aa143b92b28a18cca2: source not named by amendment 40
listed docs/legacy/strategy/2026-08-07-paper-portfolio/proposals/prop-param-scaling-energy.md bundle_sha256 complete b65b79bb3f7d7a6c570d882abc6b75bef14c1c56223bfb062f6b40c708a4ad8e: source not named by amendment 40
listed docs/legacy/strategy/2026-08-07-paper-portfolio/proposals/prop-param-scaling-energy.md bundle_sha256 complete d88ffadb420cf59aa20a7efc7615a1d7817f91814b0754756b0bc65e51cd57bf: source not named by amendment 40
listed docs/legacy/strategy/2026-08-07-paper-portfolio/proposals/prop-param-scaling-energy.md bundle_sha256 complete edbaba1c823c33bbc51164f96947a590ab0f4d96569ca221669942500d4ff2cc: source not named by amendment 40
listed docs/process_traces/2026-08-07-plan-factory/DRAFT-NEVERZERO.md bundle_sha256 complete 0a22a02caa28f0c75bc460339dd420604638cf5f7aa17a0ca2e4fd1c8afbb9ae: source not named by amendment 40
listed docs/process_traces/2026-08-07-plan-factory/DRAFT-NEVERZERO.md bundle_sha256 complete 0a22a02caa28f0c75bc460339dd420604638cf5f7aa17a0ca2e4fd1c8afbb9ae: source not named by amendment 40
listed docs/process_traces/2026-08-07-plan-factory/DRAFT-NEVERZERO.md bundle_sha256 complete 0eb6a006b4afc1cc031a3786a0cc1180686cdb78cb9375788370a3bfd86e8060: source not named by amendment 40
listed docs/process_traces/2026-08-07-plan-factory/DRAFT-NEVERZERO.md bundle_sha256 complete 153af6c4d94ba5f9e67f23cf4151703b27d430717dc3d9b773258f7ffdd40593: source not named by amendment 40
listed docs/process_traces/2026-08-07-plan-factory/DRAFT-NEVERZERO.md bundle_sha256 complete 153af6c4d94ba5f9e67f23cf4151703b27d430717dc3d9b773258f7ffdd40593: source not named by amendment 40
listed docs/process_traces/2026-08-07-plan-factory/DRAFT-NEVERZERO.md bundle_sha256 complete 1624fc548379c427d047187df164fa297bec2080062f28bb809a2dba80c94a00: source not named by amendment 40
listed docs/process_traces/2026-08-07-plan-factory/DRAFT-NEVERZERO.md bundle_sha256 complete 195b495930c4cdd532cfdd4773260ba3de73e585c7a3a9e55bac179e3b984195: source not named by amendment 40
listed docs/process_traces/2026-08-07-plan-factory/DRAFT-NEVERZERO.md bundle_sha256 complete 195b495930c4cdd532cfdd4773260ba3de73e585c7a3a9e55bac179e3b984195: source not named by amendment 40
listed docs/process_traces/2026-08-07-plan-factory/DRAFT-NEVERZERO.md bundle_sha256 complete 1a7a291dd1b789f95faf8c873a459fd4d8bb6b26257f8866726151f6c156cb96: source not named by amendment 40
listed docs/process_traces/2026-08-07-plan-factory/DRAFT-NEVERZERO.md bundle_sha256 complete 2863fa61af00fb8e23c68bd6848c9eb7f630d21827aefa4ba9af9b09a05537c9: source not named by amendment 40
listed docs/process_traces/2026-08-07-plan-factory/DRAFT-NEVERZERO.md bundle_sha256 complete 2d1c88636ad93b0727cb01d8d4c70253fc5318ce3033b9d11e2bc0e4d8a68733: source not named by amendment 40
listed docs/process_traces/2026-08-07-plan-factory/DRAFT-NEVERZERO.md bundle_sha256 complete 2d1c88636ad93b0727cb01d8d4c70253fc5318ce3033b9d11e2bc0e4d8a68733: source not named by amendment 40
listed docs/process_traces/2026-08-07-plan-factory/DRAFT-NEVERZERO.md bundle_sha256 complete 5135406fa3ba08b4df498cfbe12a463607a829db546a13d273e7b97fdb1aab50: source not named by amendment 40
listed docs/process_traces/2026-08-07-plan-factory/DRAFT-NEVERZERO.md bundle_sha256 complete 584b8d1b73e7f5a5d8fe4b1e6b0f5e3a6382bb84a57c5cd6015eda31a26c31e5: source not named by amendment 40
listed docs/process_traces/2026-08-07-plan-factory/DRAFT-NEVERZERO.md bundle_sha256 complete 8a9216a68466a432fe65e7ff9d48664d1c1e8b297b9a011cbe4f462e291220b4: source not named by amendment 40
listed docs/process_traces/2026-08-07-plan-factory/DRAFT-NEVERZERO.md bundle_sha256 complete 8bc66888f356e9e123d356db3dd1f538e71dada51037f953b8f3055e901447f4: source not named by amendment 40
listed docs/process_traces/2026-08-07-plan-factory/DRAFT-NEVERZERO.md bundle_sha256 complete 8eaba1d3b0069dd913aafabff74f6d2b6dfab066a0b30e8f4f68322a84973903: source not named by amendment 40
listed docs/process_traces/2026-08-07-plan-factory/DRAFT-NEVERZERO.md bundle_sha256 complete 9dd33c8f5bb5de530ccb0abff96435abc687d27db7286076415008eacd898c5f: source not named by amendment 40
listed docs/process_traces/2026-08-07-plan-factory/DRAFT-NEVERZERO.md bundle_sha256 complete a71d5519ecbf8a1659cbdca66d0d80b34e0350a9746ef5637e84e76771e5eea3: source not named by amendment 40
listed docs/process_traces/2026-08-07-plan-factory/DRAFT-NEVERZERO.md bundle_sha256 complete b200324cffed9a1db87323a5961d28dbdc593e743d623423b6862e5f643f5273: source not named by amendment 40
listed docs/process_traces/2026-08-07-plan-factory/DRAFT-NEVERZERO.md bundle_sha256 complete b200324cffed9a1db87323a5961d28dbdc593e743d623423b6862e5f643f5273: source not named by amendment 40
listed docs/process_traces/2026-08-07-plan-factory/DRAFT-NEVERZERO.md bundle_sha256 complete b25522da721b5a7deb6060fa1ed4ce22c174bcefa6d47617a76bfb90b23f4755: source not named by amendment 40
listed docs/process_traces/2026-08-07-plan-factory/DRAFT-NEVERZERO.md bundle_sha256 complete b27c6af7109a5734079ad311df84f812680daa957e2b5121de46372fe6871bf3: source not named by amendment 40
listed docs/process_traces/2026-08-07-plan-factory/DRAFT-NEVERZERO.md bundle_sha256 complete b2b10d7dc7c70820ffa7be4cd6e5c7d99bfb723c24ecc8aa143b92b28a18cca2: source not named by amendment 40
listed docs/process_traces/2026-08-07-plan-factory/DRAFT-NEVERZERO.md bundle_sha256 complete b2b10d7dc7c70820ffa7be4cd6e5c7d99bfb723c24ecc8aa143b92b28a18cca2: source not named by amendment 40
listed docs/process_traces/2026-08-07-plan-factory/DRAFT-NEVERZERO.md bundle_sha256 complete b65b79bb3f7d7a6c570d882abc6b75bef14c1c56223bfb062f6b40c708a4ad8e: source not named by amendment 40
listed docs/process_traces/2026-08-07-plan-factory/DRAFT-NEVERZERO.md bundle_sha256 complete c285172881235ef1ed0e29731c412706604e8cd182182981a5ed44cc2df986bf: source not named by amendment 40
listed docs/process_traces/2026-08-07-plan-factory/DRAFT-NEVERZERO.md bundle_sha256 complete d88ffadb420cf59aa20a7efc7615a1d7817f91814b0754756b0bc65e51cd57bf: source not named by amendment 40
listed docs/process_traces/2026-08-07-plan-factory/DRAFT-NEVERZERO.md bundle_sha256 complete e35798402f4af613c21e7bd5069875a4194b6672c3c3ab1c3073fff3ec05b17d: source not named by amendment 40
listed docs/process_traces/2026-08-07-plan-factory/DRAFT-NEVERZERO.md bundle_sha256 complete ec172522b7ba17c83008f32994e0c727cad2bc857aee4b6a18b4c6ac4ed14446: source not named by amendment 40
listed docs/process_traces/2026-08-07-plan-factory/DRAFT-NEVERZERO.md bundle_sha256 complete edbaba1c823c33bbc51164f96947a590ab0f4d96569ca221669942500d4ff2cc: source not named by amendment 40
listed docs/process_traces/2026-08-07-plan-factory/DRAFT-NEVERZERO.md bundle_sha256 complete f29039135ac92d31ea88c277682ff79aae0474ac741c2a18d2a1930f71be620b: source not named by amendment 40
listed docs/process_traces/2026-08-07-plan-factory/DRAFT-NEVERZERO.md bundle_sha256 complete f39fcdfe56370dc2ed33f53c6901ebcfda3362193f5f0f865d8b366c0a3eb80d: source not named by amendment 40
listed docs/process_traces/2026-08-08-attribution-debate/COMMONMODE-REPLAY.md complete_bundle_sha256 complete 708fced0676c05556749712ac3905f36e40ec22218e8d4e67e13938253639607: source not named by amendment 40
listed scripts/issue_dg071_dg075_statistics.py PINNED_BUNDLE_SHA256 file_digest 6945160964bc8667f4bfcc1ba7b500f81045fce8301ef7aadce45a188d3e06e9: file digest, not a bundle
listed tests/goldens/axi_strict_validation_evidence.json validated_bundle_sha256 not_a_bundle cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc: not a bundle
listed tests/goldens/output_identity_output_divergent.patch.json /spec_on_bundle/requests_artifact_sha256 file_digest bef5c2573c7d8c52651924817cecd64b89841b61110cde35c8413d8e475756e8: file digest, not a bundle
listed tests/goldens/output_identity_text_divergent.patch.json /spec_on_bundle/requests_artifact_sha256 file_digest ca6f3736d85f0c152f9f4f9b0a086aeb8ef03eefea659ca7e4a4505b93da93a6: file digest, not a bundle
listed tests/goldens/output_identity_unassessable.patch.json /spec_on_bundle/requests_artifact_sha256 file_digest 3eea19beae8c74a0cc3e6c0cf6c9a289cb51b813a18e8a882503fb913b6337e5: file digest, not a bundle
listed_count analysis/rpt001-v1/artifact_manifest.json bundle_tree_sha256 6
listed_count analysis/rpt001-v1/input_manifest.json bundle_tree_sha256 6
listed_count analysis/rpt001-v2/artifact_manifest.json bundle_tree_sha256 6
listed_count df-ph-decode-floor-mint1.json bundle_sha256s 50
listed_count docs/legacy/strategy/2026-08-07-paper-portfolio/proposals/prop-param-scaling-energy.md bundle_sha256 12
listed_count docs/process_traces/2026-08-07-plan-factory/DRAFT-NEVERZERO.md bundle_sha256 33
listed_count docs/process_traces/2026-08-08-attribution-debate/COMMONMODE-REPLAY.md complete_bundle_sha256 1
listed_count scripts/issue_dg071_dg075_statistics.py PINNED_BUNDLE_SHA256 1
listed_count tests/goldens/axi_strict_validation_evidence.json validated_bundle_sha256 1
listed_count tests/goldens/output_identity_output_divergent.patch.json /spec_on_bundle/requests_artifact_sha256 1
listed_count tests/goldens/output_identity_text_divergent.patch.json /spec_on_bundle/requests_artifact_sha256 1
listed_count tests/goldens/output_identity_unassessable.patch.json /spec_on_bundle/requests_artifact_sha256 1
listed_population paper_results_file_digest bundles=100
listed_population p2015-df-cmp-abba-ph-decode-b01-a1 /Users/edr/code/JouleWise/runs_window_c_20260726 file_digest
listed_population p2015-df-cmp-abba-ph-decode-b01-a2 /Users/edr/code/JouleWise/runs_window_c_20260726 file_digest
listed_population p2015-df-cmp-abba-ph-decode-b01-b1 /Users/edr/code/JouleWise/runs_window_c_20260726 file_digest
listed_population p2015-df-cmp-abba-ph-decode-b01-b2 /Users/edr/code/JouleWise/runs_window_c_20260726 file_digest
listed_population p2015-df-cmp-abba-ph-decode-b02-a1 /Users/edr/code/JouleWise/runs_window_c_20260726 file_digest
listed_population p2015-df-cmp-abba-ph-decode-b02-a2 /Users/edr/code/JouleWise/runs_window_c_20260726 file_digest
listed_population p2015-df-cmp-abba-ph-decode-b02-b1 /Users/edr/code/JouleWise/runs_window_c_20260726 file_digest
listed_population p2015-df-cmp-abba-ph-decode-b02-b2 /Users/edr/code/JouleWise/runs_window_c_20260726 file_digest
listed_population p2015-df-cmp-abba-ph-decode-b03-a1 /Users/edr/code/JouleWise/runs_window_c_20260726 file_digest
listed_population p2015-df-cmp-abba-ph-decode-b03-a2 /Users/edr/code/JouleWise/runs_window_c_20260726 file_digest
listed_population p2015-df-cmp-abba-ph-decode-b03-b1 /Users/edr/code/JouleWise/runs_window_c_20260726 file_digest
listed_population p2015-df-cmp-abba-ph-decode-b03-b2 /Users/edr/code/JouleWise/runs_window_c_20260726 file_digest
listed_population p2015-df-cmp-abba-ph-decode-b04-a1 /Users/edr/code/JouleWise/runs_window_c_20260726 file_digest
listed_population p2015-df-cmp-abba-ph-decode-b04-a2 /Users/edr/code/JouleWise/runs_window_c_20260726 file_digest
listed_population p2015-df-cmp-abba-ph-decode-b04-b1 /Users/edr/code/JouleWise/runs_window_c_20260726 file_digest
listed_population p2015-df-cmp-abba-ph-decode-b04-b2 /Users/edr/code/JouleWise/runs_window_c_20260726 file_digest
listed_population p2015-df-cmp-abba-ph-decode-b05-a1 /Users/edr/code/JouleWise/runs_window_c_20260726 file_digest
listed_population p2015-df-cmp-abba-ph-decode-b05-a2 /Users/edr/code/JouleWise/runs_window_c_20260726 file_digest
listed_population p2015-df-cmp-abba-ph-decode-b05-b1 /Users/edr/code/JouleWise/runs_window_c_20260726 file_digest
listed_population p2015-df-cmp-abba-ph-decode-b05-b2 /Users/edr/code/JouleWise/runs_window_c_20260726 file_digest
listed_population p2015-df-cmp-abba-ph-decode-b06-a1 /Users/edr/code/JouleWise/runs_window_c_20260726 file_digest
listed_population p2015-df-cmp-abba-ph-decode-b06-a2 /Users/edr/code/JouleWise/runs_window_c_20260726 file_digest
listed_population p2015-df-cmp-abba-ph-decode-b06-b1 /Users/edr/code/JouleWise/runs_window_c_20260726 file_digest
listed_population p2015-df-cmp-abba-ph-decode-b06-b2 /Users/edr/code/JouleWise/runs_window_c_20260726 file_digest
listed_population p2015-df-cmp-abba-ph-decode-b07-a1 /Users/edr/code/JouleWise/runs_window_c_20260726 file_digest
listed_population p2015-df-cmp-abba-ph-decode-b07-a2 /Users/edr/code/JouleWise/runs_window_c_20260726 file_digest
listed_population p2015-df-cmp-abba-ph-decode-b07-b1 /Users/edr/code/JouleWise/runs_window_c_20260726 file_digest
listed_population p2015-df-cmp-abba-ph-decode-b07-b2 /Users/edr/code/JouleWise/runs_window_c_20260726 file_digest
listed_population p2015-df-cmp-abba-ph-decode-b08-a1 /Users/edr/code/JouleWise/runs_window_c_20260726 file_digest
listed_population p2015-df-cmp-abba-ph-decode-b08-a2 /Users/edr/code/JouleWise/runs_window_c_20260726 file_digest
listed_population p2015-df-cmp-abba-ph-decode-b08-b1 /Users/edr/code/JouleWise/runs_window_c_20260726 file_digest
listed_population p2015-df-cmp-abba-ph-decode-b08-b2 /Users/edr/code/JouleWise/runs_window_c_20260726 file_digest
listed_population p2015-df-cmp-abba-ph-decode-b09-a1 /Users/edr/code/JouleWise/runs_window_c_20260726 file_digest
listed_population p2015-df-cmp-abba-ph-decode-b09-a2 /Users/edr/code/JouleWise/runs_window_c_20260726 file_digest
listed_population p2015-df-cmp-abba-ph-decode-b09-b1 /Users/edr/code/JouleWise/runs_window_c_20260726 file_digest
listed_population p2015-df-cmp-abba-ph-decode-b09-b2 /Users/edr/code/JouleWise/runs_window_c_20260726 file_digest
listed_population p2015-df-cmp-abba-ph-decode-b10-a1 /Users/edr/code/JouleWise/runs_window_c_20260726 file_digest
listed_population p2015-df-cmp-abba-ph-decode-b10-a2 /Users/edr/code/JouleWise/runs_window_c_20260726 file_digest
listed_population p2015-df-cmp-abba-ph-decode-b10-b1 /Users/edr/code/JouleWise/runs_window_c_20260726 file_digest
listed_population p2015-df-cmp-abba-ph-decode-b10-b2 /Users/edr/code/JouleWise/runs_window_c_20260726 file_digest
listed_population p2015-df-ph-decode-abs-r01 /Users/edr/code/JouleWise/runs_window_a10_20260725 file_digest
listed_population p2015-df-ph-decode-abs-r02 /Users/edr/code/JouleWise/runs_window_a10_20260725 file_digest
listed_population p2015-df-ph-decode-abs-r03 /Users/edr/code/JouleWise/runs_window_a10_20260725 file_digest
listed_population p2015-df-ph-decode-abs-r04 /Users/edr/code/JouleWise/runs_window_a10_20260725 file_digest
listed_population p2015-df-ph-decode-abs-r05 /Users/edr/code/JouleWise/runs_window_a10_20260725 file_digest
listed_population p2015-df-ph-decode-abs-r06 /Users/edr/code/JouleWise/runs_window_a10_20260725 file_digest
listed_population p2015-df-ph-decode-abs-r07 /Users/edr/code/JouleWise/runs_window_a10_20260725 file_digest
listed_population p2015-df-ph-decode-abs-r08 /Users/edr/code/JouleWise/runs_window_a10_20260725 file_digest
listed_population p2015-df-ph-decode-abs-r09 /Users/edr/code/JouleWise/runs_window_a10_20260725 file_digest
listed_population p2015-df-ph-decode-abs-r10 /Users/edr/code/JouleWise/runs_window_a10_20260725 file_digest
listed_population sw7bfloor-df-cmp-abba-ph-decode-b01-a1 /Users/edr/code/JouleWise/runs_window_7bfloor_20260729 file_digest
listed_population sw7bfloor-df-cmp-abba-ph-decode-b01-a2 /Users/edr/code/JouleWise/runs_window_7bfloor_20260729 file_digest
listed_population sw7bfloor-df-cmp-abba-ph-decode-b01-b1 /Users/edr/code/JouleWise/runs_window_7bfloor_20260729 file_digest
listed_population sw7bfloor-df-cmp-abba-ph-decode-b01-b2 /Users/edr/code/JouleWise/runs_window_7bfloor_20260729 file_digest
listed_population sw7bfloor-df-cmp-abba-ph-decode-b02-a1 /Users/edr/code/JouleWise/runs_window_7bfloor_20260729 file_digest
listed_population sw7bfloor-df-cmp-abba-ph-decode-b02-a2 /Users/edr/code/JouleWise/runs_window_7bfloor_20260729 file_digest
listed_population sw7bfloor-df-cmp-abba-ph-decode-b02-b1 /Users/edr/code/JouleWise/runs_window_7bfloor_20260729 file_digest
listed_population sw7bfloor-df-cmp-abba-ph-decode-b02-b2 /Users/edr/code/JouleWise/runs_window_7bfloor_20260729 file_digest
listed_population sw7bfloor-df-cmp-abba-ph-decode-b03-a1 /Users/edr/code/JouleWise/runs_window_7bfloor_20260729 file_digest
listed_population sw7bfloor-df-cmp-abba-ph-decode-b03-a2 /Users/edr/code/JouleWise/runs_window_7bfloor_20260729 file_digest
listed_population sw7bfloor-df-cmp-abba-ph-decode-b03-b1 /Users/edr/code/JouleWise/runs_window_7bfloor_20260729 file_digest
listed_population sw7bfloor-df-cmp-abba-ph-decode-b03-b2 /Users/edr/code/JouleWise/runs_window_7bfloor_20260729 file_digest
listed_population sw7bfloor-df-cmp-abba-ph-decode-b04-a1 /Users/edr/code/JouleWise/runs_window_7bfloor_20260729 file_digest
listed_population sw7bfloor-df-cmp-abba-ph-decode-b04-a2 /Users/edr/code/JouleWise/runs_window_7bfloor_20260729 file_digest
listed_population sw7bfloor-df-cmp-abba-ph-decode-b04-b1 /Users/edr/code/JouleWise/runs_window_7bfloor_20260729 file_digest
listed_population sw7bfloor-df-cmp-abba-ph-decode-b04-b2 /Users/edr/code/JouleWise/runs_window_7bfloor_20260729 file_digest
listed_population sw7bfloor-df-cmp-abba-ph-decode-b05-a1 /Users/edr/code/JouleWise/runs_window_7bfloor_20260729 file_digest
listed_population sw7bfloor-df-cmp-abba-ph-decode-b05-a2 /Users/edr/code/JouleWise/runs_window_7bfloor_20260729 file_digest
listed_population sw7bfloor-df-cmp-abba-ph-decode-b05-b1 /Users/edr/code/JouleWise/runs_window_7bfloor_20260729 file_digest
listed_population sw7bfloor-df-cmp-abba-ph-decode-b05-b2 /Users/edr/code/JouleWise/runs_window_7bfloor_20260729 file_digest
listed_population sw7bfloor-df-cmp-abba-ph-decode-b06-a1 /Users/edr/code/JouleWise/runs_window_7bfloor_20260729 file_digest
listed_population sw7bfloor-df-cmp-abba-ph-decode-b06-a2 /Users/edr/code/JouleWise/runs_window_7bfloor_20260729 file_digest
listed_population sw7bfloor-df-cmp-abba-ph-decode-b06-b1 /Users/edr/code/JouleWise/runs_window_7bfloor_20260729 file_digest
listed_population sw7bfloor-df-cmp-abba-ph-decode-b06-b2 /Users/edr/code/JouleWise/runs_window_7bfloor_20260729 file_digest
listed_population sw7bfloor-df-cmp-abba-ph-decode-b07-a1 /Users/edr/code/JouleWise/runs_window_7bfloor_20260729 file_digest
listed_population sw7bfloor-df-cmp-abba-ph-decode-b07-a2 /Users/edr/code/JouleWise/runs_window_7bfloor_20260729 file_digest
listed_population sw7bfloor-df-cmp-abba-ph-decode-b07-b1 /Users/edr/code/JouleWise/runs_window_7bfloor_20260729 file_digest
listed_population sw7bfloor-df-cmp-abba-ph-decode-b07-b2 /Users/edr/code/JouleWise/runs_window_7bfloor_20260729 file_digest
listed_population sw7bfloor-df-cmp-abba-ph-decode-b08-a1 /Users/edr/code/JouleWise/runs_window_7bfloor_20260729 file_digest
listed_population sw7bfloor-df-cmp-abba-ph-decode-b08-a2 /Users/edr/code/JouleWise/runs_window_7bfloor_20260729 file_digest
listed_population sw7bfloor-df-cmp-abba-ph-decode-b08-b1 /Users/edr/code/JouleWise/runs_window_7bfloor_20260729 file_digest
listed_population sw7bfloor-df-cmp-abba-ph-decode-b08-b2 /Users/edr/code/JouleWise/runs_window_7bfloor_20260729 file_digest
listed_population sw7bfloor-df-cmp-abba-ph-decode-b09-a1 /Users/edr/code/JouleWise/runs_window_7bfloor_20260729 file_digest
listed_population sw7bfloor-df-cmp-abba-ph-decode-b09-a2 /Users/edr/code/JouleWise/runs_window_7bfloor_20260729 file_digest
listed_population sw7bfloor-df-cmp-abba-ph-decode-b09-b1 /Users/edr/code/JouleWise/runs_window_7bfloor_20260729 file_digest
listed_population sw7bfloor-df-cmp-abba-ph-decode-b09-b2 /Users/edr/code/JouleWise/runs_window_7bfloor_20260729 file_digest
listed_population sw7bfloor-df-cmp-abba-ph-decode-b10-a1 /Users/edr/code/JouleWise/runs_window_7bfloor_20260729 file_digest
listed_population sw7bfloor-df-cmp-abba-ph-decode-b10-a2 /Users/edr/code/JouleWise/runs_window_7bfloor_20260729 file_digest
listed_population sw7bfloor-df-cmp-abba-ph-decode-b10-b1 /Users/edr/code/JouleWise/runs_window_7bfloor_20260729 file_digest
listed_population sw7bfloor-df-cmp-abba-ph-decode-b10-b2 /Users/edr/code/JouleWise/runs_window_7bfloor_20260729 file_digest
listed_population sw7bfloor-df-ph-decode-abs-r01 /Users/edr/code/JouleWise/runs_window_7bfloor_20260729 file_digest
listed_population sw7bfloor-df-ph-decode-abs-r02 /Users/edr/code/JouleWise/runs_window_7bfloor_20260729 file_digest
listed_population sw7bfloor-df-ph-decode-abs-r03 /Users/edr/code/JouleWise/runs_window_7bfloor_20260729 file_digest
listed_population sw7bfloor-df-ph-decode-abs-r04 /Users/edr/code/JouleWise/runs_window_7bfloor_20260729 file_digest
listed_population sw7bfloor-df-ph-decode-abs-r05 /Users/edr/code/JouleWise/runs_window_7bfloor_20260729 file_digest
listed_population sw7bfloor-df-ph-decode-abs-r06 /Users/edr/code/JouleWise/runs_window_7bfloor_20260729 file_digest
listed_population sw7bfloor-df-ph-decode-abs-r07 /Users/edr/code/JouleWise/runs_window_7bfloor_20260729 file_digest
listed_population sw7bfloor-df-ph-decode-abs-r08 /Users/edr/code/JouleWise/runs_window_7bfloor_20260729 file_digest
listed_population sw7bfloor-df-ph-decode-abs-r09 /Users/edr/code/JouleWise/runs_window_7bfloor_20260729 file_digest
listed_population sw7bfloor-df-ph-decode-abs-r10 /Users/edr/code/JouleWise/runs_window_7bfloor_20260729 file_digest
```

## Forward check B

Command: `python3 scripts/build_battery_float_historical_bundles.py --check`

Exit: 0

### stdout (verbatim)

```text
forward check: byte-identical entries=69
```

### stderr (verbatim)

```text
unparseable docs/legacy/process_traces/2026-08-06-d079-issuance-coldgate/ISSUANCE-execute-summary.json: JSONDecodeError
unparseable docs/process_traces/2026-09-16-activation-9853dd2b/77-arm-evidence-n1-20260917/arm-census-final.json: JSONDecodeError
unparseable docs/process_traces/2026-09-16-activation-9853dd2b/77-arm-evidence-n1-20260917/arm-census-staging.json: JSONDecodeError
unparseable docs/process_traces/2026-09-18-activation-d8ca3a36/08-adhoc-corecording-state-3seats-2claude.sampler.jsonl: JSONDecodeError
unparseable docs/process_traces/2026-09-18-activation-d8ca3a36/21-arm-evidence-n1-20260919/arm-census-1.json: JSONDecodeError
unparseable docs/process_traces/2026-09-18-activation-d8ca3a36/21-arm-evidence-n1-20260919/arm-census-2.json: JSONDecodeError
unparseable docs/process_traces/2026-09-18-activation-d8ca3a36/21-arm-evidence-n1-20260919/arm-census-final.json: JSONDecodeError
unparseable docs/process_traces/2026-09-19-activation-4ca26e9c/01-arm-evidence-n2-20260919/arm-census-1.json: JSONDecodeError
unparseable docs/process_traces/2026-09-19-activation-4ca26e9c/01-arm-evidence-n2-20260919/arm-census-2.json: JSONDecodeError
unparseable docs/process_traces/2026-09-19-activation-4ca26e9c/01-arm-evidence-n2-20260919/arm-census-final.json: JSONDecodeError
unparseable docs/process_traces/2026-09-19-activation-a743be05/03-arm-evidence-qpe01-pilot-n1-20260920/arm-census-1.json: JSONDecodeError
unparseable docs/process_traces/2026-09-19-activation-a743be05/03-arm-evidence-qpe01-pilot-n1-20260920/arm-census-2.json: JSONDecodeError
unparseable docs/process_traces/2026-09-19-activation-a743be05/03-arm-evidence-qpe01-pilot-n1-20260920/arm-census-final.json: JSONDecodeError
unparseable docs/process_traces/2026-09-24-activation-278ebc9e/104-forger-fable/adjudication.jsonl: JSONDecodeError
unparseable docs/process_traces/2026-09-24-activation-278ebc9e/104-forger-fable/replay-check.jsonl: JSONDecodeError
unparseable docs/process_traces/2026-09-24-activation-278ebc9e/105-coldgate-packet-a291-forger2/ex-104-fc-adjudication.jsonl: JSONDecodeError
unparseable docs/process_traces/2026-09-24-activation-278ebc9e/106-forger-fable-b/adjudication.jsonl: JSONDecodeError
unparseable docs/process_traces/2026-09-24-activation-278ebc9e/112-coldgate-packet-a291-premerge/ex-104-fc-adjudication.jsonl: JSONDecodeError
unparseable docs/process_traces/2026-09-24-activation-278ebc9e/112-coldgate-packet-a291-premerge/ex-106-fb-adjudication.jsonl: JSONDecodeError
unparseable docs/process_traces/2026-09-24-activation-278ebc9e/117-coldgate-packet-a291-finalpass/ex-104-fc-adjudication.jsonl: JSONDecodeError
unparseable docs/process_traces/2026-09-24-activation-278ebc9e/117-coldgate-packet-a291-finalpass/ex-104-fc-replay.jsonl: JSONDecodeError
unparseable docs/process_traces/2026-09-24-activation-278ebc9e/117-coldgate-packet-a291-finalpass/ex-106-fb-adjudication-and-replay.jsonl: JSONDecodeError
listed analysis/rpt001-v1/artifact_manifest.json bundle_tree_sha256 tree_legacy 1ffe1ec76e3022bac5bd651b261a044d0865a1d5877c165aa45f96018ff0e1ca: retired tree fold
listed analysis/rpt001-v1/artifact_manifest.json bundle_tree_sha256 tree_legacy 36d3b109ac3a2e88b27434361ccb5b85c84d653b4cb7fabf25b3e222506f57ef: retired tree fold
listed analysis/rpt001-v1/artifact_manifest.json bundle_tree_sha256 tree_legacy 9be1c5df4bb566fbe057735bac5377d6826828f0061f11fee2b48cd74f982ff4: retired tree fold
listed analysis/rpt001-v1/artifact_manifest.json bundle_tree_sha256 tree_legacy b029e14b53a085f74653857a62194ed50a47d63e4bc49d15238ec77ff94cc2b5: retired tree fold
listed analysis/rpt001-v1/artifact_manifest.json bundle_tree_sha256 tree_legacy ec05d3d2c2bd262cb3488c887e4a561ef6c70d6271058f3fb0c0e823e38699cc: retired tree fold
listed analysis/rpt001-v1/artifact_manifest.json bundle_tree_sha256 tree_legacy f9f5896c8edf8b8dc1fd56dee977f5a5b7b4d5a04cc76b1405c865d817f9e279: retired tree fold
listed analysis/rpt001-v1/input_manifest.json bundle_tree_sha256 tree_legacy 1ffe1ec76e3022bac5bd651b261a044d0865a1d5877c165aa45f96018ff0e1ca: retired tree fold
listed analysis/rpt001-v1/input_manifest.json bundle_tree_sha256 tree_legacy 36d3b109ac3a2e88b27434361ccb5b85c84d653b4cb7fabf25b3e222506f57ef: retired tree fold
listed analysis/rpt001-v1/input_manifest.json bundle_tree_sha256 tree_legacy 9be1c5df4bb566fbe057735bac5377d6826828f0061f11fee2b48cd74f982ff4: retired tree fold
listed analysis/rpt001-v1/input_manifest.json bundle_tree_sha256 tree_legacy b029e14b53a085f74653857a62194ed50a47d63e4bc49d15238ec77ff94cc2b5: retired tree fold
listed analysis/rpt001-v1/input_manifest.json bundle_tree_sha256 tree_legacy ec05d3d2c2bd262cb3488c887e4a561ef6c70d6271058f3fb0c0e823e38699cc: retired tree fold
listed analysis/rpt001-v1/input_manifest.json bundle_tree_sha256 tree_legacy f9f5896c8edf8b8dc1fd56dee977f5a5b7b4d5a04cc76b1405c865d817f9e279: retired tree fold
listed analysis/rpt001-v2/artifact_manifest.json bundle_tree_sha256 tree_nul_v1 2888c9d205df62e1136a376997ea8a6947683e4311eedaee20e3135bd559e213: source not named by amendment 40
listed analysis/rpt001-v2/artifact_manifest.json bundle_tree_sha256 tree_nul_v1 5ec71ed301ba9c0a48b137b5bdce00b8893c62d4f1397f55aac3c1943ccc9180: source not named by amendment 40
listed analysis/rpt001-v2/artifact_manifest.json bundle_tree_sha256 tree_nul_v1 8a99d7a851c55e53631df6f910d17ee097cbf8bd19f33d44bcef911a6502e82f: source not named by amendment 40
listed analysis/rpt001-v2/artifact_manifest.json bundle_tree_sha256 tree_nul_v1 9376dbc16848e03d3bd54e4fac5598b34e1391d376ef11db527ac1fe25f08773: source not named by amendment 40
listed analysis/rpt001-v2/artifact_manifest.json bundle_tree_sha256 tree_nul_v1 9f162f058bfceb949f34e0c24042c83e8d7f353f97d87b4cf6e0e6dff0912398: source not named by amendment 40
listed analysis/rpt001-v2/artifact_manifest.json bundle_tree_sha256 tree_nul_v1 c72cdc34ef3ce9ccfb0a015bed5ace8e4efa7d18f457ac5cd8a0c894acc21268: source not named by amendment 40
listed df-ph-decode-floor-mint1.json bundle_sha256s complete 0a22a02caa28f0c75bc460339dd420604638cf5f7aa17a0ca2e4fd1c8afbb9ae: duplicate of included citation
listed df-ph-decode-floor-mint1.json bundle_sha256s complete 0a76e5fbcffdccb44ebc22b8d9d86e259b49d2c529ec89bcc0a24c6f22994899: duplicate of included citation
listed df-ph-decode-floor-mint1.json bundle_sha256s complete 0eb6a006b4afc1cc031a3786a0cc1180686cdb78cb9375788370a3bfd86e8060: duplicate of included citation
listed df-ph-decode-floor-mint1.json bundle_sha256s complete 153af6c4d94ba5f9e67f23cf4151703b27d430717dc3d9b773258f7ffdd40593: duplicate of included citation
listed df-ph-decode-floor-mint1.json bundle_sha256s complete 1624fc548379c427d047187df164fa297bec2080062f28bb809a2dba80c94a00: duplicate of included citation
listed df-ph-decode-floor-mint1.json bundle_sha256s complete 195b495930c4cdd532cfdd4773260ba3de73e585c7a3a9e55bac179e3b984195: duplicate of included citation
listed df-ph-decode-floor-mint1.json bundle_sha256s complete 1a7a291dd1b789f95faf8c873a459fd4d8bb6b26257f8866726151f6c156cb96: duplicate of included citation
listed df-ph-decode-floor-mint1.json bundle_sha256s complete 2863fa61af00fb8e23c68bd6848c9eb7f630d21827aefa4ba9af9b09a05537c9: duplicate of included citation
listed df-ph-decode-floor-mint1.json bundle_sha256s complete 2d1c88636ad93b0727cb01d8d4c70253fc5318ce3033b9d11e2bc0e4d8a68733: duplicate of included citation
listed df-ph-decode-floor-mint1.json bundle_sha256s complete 2ecceeb9237077c2f3a6577c9d7bce24d3deeb926df1e15f1b389bad0db02147: duplicate of included citation
listed df-ph-decode-floor-mint1.json bundle_sha256s complete 32c53e61cdbb8f507eed269af1eeeef69f4105fba8c9d9d2f43f06f8ba9acaf9: duplicate of included citation
listed df-ph-decode-floor-mint1.json bundle_sha256s complete 377f6a786c341eef39d6836cb2d12921ab4a05d434c5a241f5c581d8f4d4a2ee: duplicate of included citation
listed df-ph-decode-floor-mint1.json bundle_sha256s complete 39054c62e30e8362a0ef473fb674aed5d1c87df7c630d0f4daadfd296874439e: duplicate of included citation
listed df-ph-decode-floor-mint1.json bundle_sha256s complete 48a8bb2a6f23c6531eae6f8d99c043e0500379aff9427956fee1b74de75694ff: duplicate of included citation
listed df-ph-decode-floor-mint1.json bundle_sha256s complete 5135406fa3ba08b4df498cfbe12a463607a829db546a13d273e7b97fdb1aab50: duplicate of included citation
listed df-ph-decode-floor-mint1.json bundle_sha256s complete 584b8d1b73e7f5a5d8fe4b1e6b0f5e3a6382bb84a57c5cd6015eda31a26c31e5: duplicate of included citation
listed df-ph-decode-floor-mint1.json bundle_sha256s complete 589b17f6a10c6275407367f7f90bea8ced63dabb70850798e0808626924168fe: duplicate of included citation
listed df-ph-decode-floor-mint1.json bundle_sha256s complete 59aade4961b9e59f1696f88f263204f3739cb7d81adc754cc3380a0133f92691: duplicate of included citation
listed df-ph-decode-floor-mint1.json bundle_sha256s complete 5c7a8a6ce946d88fdd5ea0124bafa1ffad8c289308d5e9b600d2f95e280bb025: duplicate of included citation
listed df-ph-decode-floor-mint1.json bundle_sha256s complete 6a090490fd08e646bc39c4eaa112fffcdf87e0d5f03599af10595512957997f4: duplicate of included citation
listed df-ph-decode-floor-mint1.json bundle_sha256s complete 6cdd0c795befd568798a4ef4538bf6db1ccd930f240de873a77ab36263927561: duplicate of included citation
listed df-ph-decode-floor-mint1.json bundle_sha256s complete 769d1d1378e3603fe40013fadeda35504eca0c235f773106233323fba5a61163: duplicate of included citation
listed df-ph-decode-floor-mint1.json bundle_sha256s complete 8a9216a68466a432fe65e7ff9d48664d1c1e8b297b9a011cbe4f462e291220b4: duplicate of included citation
listed df-ph-decode-floor-mint1.json bundle_sha256s complete 8bc66888f356e9e123d356db3dd1f538e71dada51037f953b8f3055e901447f4: duplicate of included citation
listed df-ph-decode-floor-mint1.json bundle_sha256s complete 8eaba1d3b0069dd913aafabff74f6d2b6dfab066a0b30e8f4f68322a84973903: duplicate of included citation
listed df-ph-decode-floor-mint1.json bundle_sha256s complete 9d67992e7cdd70a86bbbf82ca6a9b587d42779c14a28f72256900331d9f8fece: duplicate of included citation
listed df-ph-decode-floor-mint1.json bundle_sha256s complete a71d5519ecbf8a1659cbdca66d0d80b34e0350a9746ef5637e84e76771e5eea3: duplicate of included citation
listed df-ph-decode-floor-mint1.json bundle_sha256s complete acd77e1d5a8a5bc82493315b772fa616a3cf5c579fda5586e04902fdda388459: duplicate of included citation
listed df-ph-decode-floor-mint1.json bundle_sha256s complete b200324cffed9a1db87323a5961d28dbdc593e743d623423b6862e5f643f5273: duplicate of included citation
listed df-ph-decode-floor-mint1.json bundle_sha256s complete b25522da721b5a7deb6060fa1ed4ce22c174bcefa6d47617a76bfb90b23f4755: duplicate of included citation
listed df-ph-decode-floor-mint1.json bundle_sha256s complete b27c6af7109a5734079ad311df84f812680daa957e2b5121de46372fe6871bf3: duplicate of included citation
listed df-ph-decode-floor-mint1.json bundle_sha256s complete b2b10d7dc7c70820ffa7be4cd6e5c7d99bfb723c24ecc8aa143b92b28a18cca2: duplicate of included citation
listed df-ph-decode-floor-mint1.json bundle_sha256s complete b446e7a59d38287578918f273a1fa512f89f8da1ca4e8304f1f83d7af27dc568: duplicate of included citation
listed df-ph-decode-floor-mint1.json bundle_sha256s complete b65b79bb3f7d7a6c570d882abc6b75bef14c1c56223bfb062f6b40c708a4ad8e: duplicate of included citation
listed df-ph-decode-floor-mint1.json bundle_sha256s complete c285172881235ef1ed0e29731c412706604e8cd182182981a5ed44cc2df986bf: duplicate of included citation
listed df-ph-decode-floor-mint1.json bundle_sha256s complete cac899e4c3fa84eec27f5fc26e0c105f25abc6948190821552f3a89f317fd681: duplicate of included citation
listed df-ph-decode-floor-mint1.json bundle_sha256s complete d88ffadb420cf59aa20a7efc7615a1d7817f91814b0754756b0bc65e51cd57bf: duplicate of included citation
listed df-ph-decode-floor-mint1.json bundle_sha256s complete dc1e56aa1d27fc6ac0bb5d7a80b7881e635a5050e7ffc9536b62c75dd22cee5a: duplicate of included citation
listed df-ph-decode-floor-mint1.json bundle_sha256s complete e339de0c0f2e5b464e73e2423e94ad6a4fa72c2abca68cebeb2d97f3af893109: duplicate of included citation
listed df-ph-decode-floor-mint1.json bundle_sha256s complete e35798402f4af613c21e7bd5069875a4194b6672c3c3ab1c3073fff3ec05b17d: duplicate of included citation
listed df-ph-decode-floor-mint1.json bundle_sha256s complete e7ee36928bac0e65b8004f8f7b7fae0babe3ac706171b26b8dd92015a1f87058: duplicate of included citation
listed df-ph-decode-floor-mint1.json bundle_sha256s complete eb05f32d37b1c8e8969f097a0ff112ea95e7ca9c1110e03127b7538267414449: duplicate of included citation
listed df-ph-decode-floor-mint1.json bundle_sha256s complete ec172522b7ba17c83008f32994e0c727cad2bc857aee4b6a18b4c6ac4ed14446: duplicate of included citation
listed df-ph-decode-floor-mint1.json bundle_sha256s complete ec6fda56898612837eb76d658c9057ab0e08e26689e44b1dea1a296dd17674b2: duplicate of included citation
listed df-ph-decode-floor-mint1.json bundle_sha256s complete ed743899e603951287cce29814371c4949b452a36b65550992535a3e3ffeef3e: duplicate of included citation
listed df-ph-decode-floor-mint1.json bundle_sha256s complete edbaba1c823c33bbc51164f96947a590ab0f4d96569ca221669942500d4ff2cc: duplicate of included citation
listed df-ph-decode-floor-mint1.json bundle_sha256s complete f29039135ac92d31ea88c277682ff79aae0474ac741c2a18d2a1930f71be620b: duplicate of included citation
listed df-ph-decode-floor-mint1.json bundle_sha256s complete f39fcdfe56370dc2ed33f53c6901ebcfda3362193f5f0f865d8b366c0a3eb80d: duplicate of included citation
listed df-ph-decode-floor-mint1.json bundle_sha256s complete fb12d40f5a418462a268587fa9ad8e9bbbef5e32e47132f112e2f3f9d540c5e1: duplicate of included citation
listed df-ph-decode-floor-mint1.json bundle_sha256s complete ffacb0680cf37794804f7af1f5e0bd39fab26160bf134a0cf63525c293155f13: duplicate of included citation
listed docs/legacy/strategy/2026-08-07-paper-portfolio/proposals/prop-param-scaling-energy.md bundle_sha256 complete 0eb6a006b4afc1cc031a3786a0cc1180686cdb78cb9375788370a3bfd86e8060: source not named by amendment 40
listed docs/legacy/strategy/2026-08-07-paper-portfolio/proposals/prop-param-scaling-energy.md bundle_sha256 complete 153af6c4d94ba5f9e67f23cf4151703b27d430717dc3d9b773258f7ffdd40593: source not named by amendment 40
listed docs/legacy/strategy/2026-08-07-paper-portfolio/proposals/prop-param-scaling-energy.md bundle_sha256 complete 195b495930c4cdd532cfdd4773260ba3de73e585c7a3a9e55bac179e3b984195: source not named by amendment 40
listed docs/legacy/strategy/2026-08-07-paper-portfolio/proposals/prop-param-scaling-energy.md bundle_sha256 complete 2d1c88636ad93b0727cb01d8d4c70253fc5318ce3033b9d11e2bc0e4d8a68733: source not named by amendment 40
listed docs/legacy/strategy/2026-08-07-paper-portfolio/proposals/prop-param-scaling-energy.md bundle_sha256 complete 5135406fa3ba08b4df498cfbe12a463607a829db546a13d273e7b97fdb1aab50: source not named by amendment 40
listed docs/legacy/strategy/2026-08-07-paper-portfolio/proposals/prop-param-scaling-energy.md bundle_sha256 complete 8bc66888f356e9e123d356db3dd1f538e71dada51037f953b8f3055e901447f4: source not named by amendment 40
listed docs/legacy/strategy/2026-08-07-paper-portfolio/proposals/prop-param-scaling-energy.md bundle_sha256 complete 8eaba1d3b0069dd913aafabff74f6d2b6dfab066a0b30e8f4f68322a84973903: source not named by amendment 40
listed docs/legacy/strategy/2026-08-07-paper-portfolio/proposals/prop-param-scaling-energy.md bundle_sha256 complete b200324cffed9a1db87323a5961d28dbdc593e743d623423b6862e5f643f5273: source not named by amendment 40
listed docs/legacy/strategy/2026-08-07-paper-portfolio/proposals/prop-param-scaling-energy.md bundle_sha256 complete b2b10d7dc7c70820ffa7be4cd6e5c7d99bfb723c24ecc8aa143b92b28a18cca2: source not named by amendment 40
listed docs/legacy/strategy/2026-08-07-paper-portfolio/proposals/prop-param-scaling-energy.md bundle_sha256 complete b65b79bb3f7d7a6c570d882abc6b75bef14c1c56223bfb062f6b40c708a4ad8e: source not named by amendment 40
listed docs/legacy/strategy/2026-08-07-paper-portfolio/proposals/prop-param-scaling-energy.md bundle_sha256 complete d88ffadb420cf59aa20a7efc7615a1d7817f91814b0754756b0bc65e51cd57bf: source not named by amendment 40
listed docs/legacy/strategy/2026-08-07-paper-portfolio/proposals/prop-param-scaling-energy.md bundle_sha256 complete edbaba1c823c33bbc51164f96947a590ab0f4d96569ca221669942500d4ff2cc: source not named by amendment 40
listed docs/process_traces/2026-08-07-plan-factory/DRAFT-NEVERZERO.md bundle_sha256 complete 0a22a02caa28f0c75bc460339dd420604638cf5f7aa17a0ca2e4fd1c8afbb9ae: source not named by amendment 40
listed docs/process_traces/2026-08-07-plan-factory/DRAFT-NEVERZERO.md bundle_sha256 complete 0a22a02caa28f0c75bc460339dd420604638cf5f7aa17a0ca2e4fd1c8afbb9ae: source not named by amendment 40
listed docs/process_traces/2026-08-07-plan-factory/DRAFT-NEVERZERO.md bundle_sha256 complete 0eb6a006b4afc1cc031a3786a0cc1180686cdb78cb9375788370a3bfd86e8060: source not named by amendment 40
listed docs/process_traces/2026-08-07-plan-factory/DRAFT-NEVERZERO.md bundle_sha256 complete 153af6c4d94ba5f9e67f23cf4151703b27d430717dc3d9b773258f7ffdd40593: source not named by amendment 40
listed docs/process_traces/2026-08-07-plan-factory/DRAFT-NEVERZERO.md bundle_sha256 complete 153af6c4d94ba5f9e67f23cf4151703b27d430717dc3d9b773258f7ffdd40593: source not named by amendment 40
listed docs/process_traces/2026-08-07-plan-factory/DRAFT-NEVERZERO.md bundle_sha256 complete 1624fc548379c427d047187df164fa297bec2080062f28bb809a2dba80c94a00: source not named by amendment 40
listed docs/process_traces/2026-08-07-plan-factory/DRAFT-NEVERZERO.md bundle_sha256 complete 195b495930c4cdd532cfdd4773260ba3de73e585c7a3a9e55bac179e3b984195: source not named by amendment 40
listed docs/process_traces/2026-08-07-plan-factory/DRAFT-NEVERZERO.md bundle_sha256 complete 195b495930c4cdd532cfdd4773260ba3de73e585c7a3a9e55bac179e3b984195: source not named by amendment 40
listed docs/process_traces/2026-08-07-plan-factory/DRAFT-NEVERZERO.md bundle_sha256 complete 1a7a291dd1b789f95faf8c873a459fd4d8bb6b26257f8866726151f6c156cb96: source not named by amendment 40
listed docs/process_traces/2026-08-07-plan-factory/DRAFT-NEVERZERO.md bundle_sha256 complete 2863fa61af00fb8e23c68bd6848c9eb7f630d21827aefa4ba9af9b09a05537c9: source not named by amendment 40
listed docs/process_traces/2026-08-07-plan-factory/DRAFT-NEVERZERO.md bundle_sha256 complete 2d1c88636ad93b0727cb01d8d4c70253fc5318ce3033b9d11e2bc0e4d8a68733: source not named by amendment 40
listed docs/process_traces/2026-08-07-plan-factory/DRAFT-NEVERZERO.md bundle_sha256 complete 2d1c88636ad93b0727cb01d8d4c70253fc5318ce3033b9d11e2bc0e4d8a68733: source not named by amendment 40
listed docs/process_traces/2026-08-07-plan-factory/DRAFT-NEVERZERO.md bundle_sha256 complete 5135406fa3ba08b4df498cfbe12a463607a829db546a13d273e7b97fdb1aab50: source not named by amendment 40
listed docs/process_traces/2026-08-07-plan-factory/DRAFT-NEVERZERO.md bundle_sha256 complete 584b8d1b73e7f5a5d8fe4b1e6b0f5e3a6382bb84a57c5cd6015eda31a26c31e5: source not named by amendment 40
listed docs/process_traces/2026-08-07-plan-factory/DRAFT-NEVERZERO.md bundle_sha256 complete 8a9216a68466a432fe65e7ff9d48664d1c1e8b297b9a011cbe4f462e291220b4: source not named by amendment 40
listed docs/process_traces/2026-08-07-plan-factory/DRAFT-NEVERZERO.md bundle_sha256 complete 8bc66888f356e9e123d356db3dd1f538e71dada51037f953b8f3055e901447f4: source not named by amendment 40
listed docs/process_traces/2026-08-07-plan-factory/DRAFT-NEVERZERO.md bundle_sha256 complete 8eaba1d3b0069dd913aafabff74f6d2b6dfab066a0b30e8f4f68322a84973903: source not named by amendment 40
listed docs/process_traces/2026-08-07-plan-factory/DRAFT-NEVERZERO.md bundle_sha256 complete 9dd33c8f5bb5de530ccb0abff96435abc687d27db7286076415008eacd898c5f: source not named by amendment 40
listed docs/process_traces/2026-08-07-plan-factory/DRAFT-NEVERZERO.md bundle_sha256 complete a71d5519ecbf8a1659cbdca66d0d80b34e0350a9746ef5637e84e76771e5eea3: source not named by amendment 40
listed docs/process_traces/2026-08-07-plan-factory/DRAFT-NEVERZERO.md bundle_sha256 complete b200324cffed9a1db87323a5961d28dbdc593e743d623423b6862e5f643f5273: source not named by amendment 40
listed docs/process_traces/2026-08-07-plan-factory/DRAFT-NEVERZERO.md bundle_sha256 complete b200324cffed9a1db87323a5961d28dbdc593e743d623423b6862e5f643f5273: source not named by amendment 40
listed docs/process_traces/2026-08-07-plan-factory/DRAFT-NEVERZERO.md bundle_sha256 complete b25522da721b5a7deb6060fa1ed4ce22c174bcefa6d47617a76bfb90b23f4755: source not named by amendment 40
listed docs/process_traces/2026-08-07-plan-factory/DRAFT-NEVERZERO.md bundle_sha256 complete b27c6af7109a5734079ad311df84f812680daa957e2b5121de46372fe6871bf3: source not named by amendment 40
listed docs/process_traces/2026-08-07-plan-factory/DRAFT-NEVERZERO.md bundle_sha256 complete b2b10d7dc7c70820ffa7be4cd6e5c7d99bfb723c24ecc8aa143b92b28a18cca2: source not named by amendment 40
listed docs/process_traces/2026-08-07-plan-factory/DRAFT-NEVERZERO.md bundle_sha256 complete b2b10d7dc7c70820ffa7be4cd6e5c7d99bfb723c24ecc8aa143b92b28a18cca2: source not named by amendment 40
listed docs/process_traces/2026-08-07-plan-factory/DRAFT-NEVERZERO.md bundle_sha256 complete b65b79bb3f7d7a6c570d882abc6b75bef14c1c56223bfb062f6b40c708a4ad8e: source not named by amendment 40
listed docs/process_traces/2026-08-07-plan-factory/DRAFT-NEVERZERO.md bundle_sha256 complete c285172881235ef1ed0e29731c412706604e8cd182182981a5ed44cc2df986bf: source not named by amendment 40
listed docs/process_traces/2026-08-07-plan-factory/DRAFT-NEVERZERO.md bundle_sha256 complete d88ffadb420cf59aa20a7efc7615a1d7817f91814b0754756b0bc65e51cd57bf: source not named by amendment 40
listed docs/process_traces/2026-08-07-plan-factory/DRAFT-NEVERZERO.md bundle_sha256 complete e35798402f4af613c21e7bd5069875a4194b6672c3c3ab1c3073fff3ec05b17d: source not named by amendment 40
listed docs/process_traces/2026-08-07-plan-factory/DRAFT-NEVERZERO.md bundle_sha256 complete ec172522b7ba17c83008f32994e0c727cad2bc857aee4b6a18b4c6ac4ed14446: source not named by amendment 40
listed docs/process_traces/2026-08-07-plan-factory/DRAFT-NEVERZERO.md bundle_sha256 complete edbaba1c823c33bbc51164f96947a590ab0f4d96569ca221669942500d4ff2cc: source not named by amendment 40
listed docs/process_traces/2026-08-07-plan-factory/DRAFT-NEVERZERO.md bundle_sha256 complete f29039135ac92d31ea88c277682ff79aae0474ac741c2a18d2a1930f71be620b: source not named by amendment 40
listed docs/process_traces/2026-08-07-plan-factory/DRAFT-NEVERZERO.md bundle_sha256 complete f39fcdfe56370dc2ed33f53c6901ebcfda3362193f5f0f865d8b366c0a3eb80d: source not named by amendment 40
listed docs/process_traces/2026-08-08-attribution-debate/COMMONMODE-REPLAY.md complete_bundle_sha256 complete 708fced0676c05556749712ac3905f36e40ec22218e8d4e67e13938253639607: source not named by amendment 40
listed scripts/issue_dg071_dg075_statistics.py PINNED_BUNDLE_SHA256 file_digest 6945160964bc8667f4bfcc1ba7b500f81045fce8301ef7aadce45a188d3e06e9: file digest, not a bundle
listed tests/goldens/axi_strict_validation_evidence.json validated_bundle_sha256 not_a_bundle cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc: not a bundle
listed tests/goldens/output_identity_output_divergent.patch.json /spec_on_bundle/requests_artifact_sha256 file_digest bef5c2573c7d8c52651924817cecd64b89841b61110cde35c8413d8e475756e8: file digest, not a bundle
listed tests/goldens/output_identity_text_divergent.patch.json /spec_on_bundle/requests_artifact_sha256 file_digest ca6f3736d85f0c152f9f4f9b0a086aeb8ef03eefea659ca7e4a4505b93da93a6: file digest, not a bundle
listed tests/goldens/output_identity_unassessable.patch.json /spec_on_bundle/requests_artifact_sha256 file_digest 3eea19beae8c74a0cc3e6c0cf6c9a289cb51b813a18e8a882503fb913b6337e5: file digest, not a bundle
listed_count analysis/rpt001-v1/artifact_manifest.json bundle_tree_sha256 6
listed_count analysis/rpt001-v1/input_manifest.json bundle_tree_sha256 6
listed_count analysis/rpt001-v2/artifact_manifest.json bundle_tree_sha256 6
listed_count df-ph-decode-floor-mint1.json bundle_sha256s 50
listed_count docs/legacy/strategy/2026-08-07-paper-portfolio/proposals/prop-param-scaling-energy.md bundle_sha256 12
listed_count docs/process_traces/2026-08-07-plan-factory/DRAFT-NEVERZERO.md bundle_sha256 33
listed_count docs/process_traces/2026-08-08-attribution-debate/COMMONMODE-REPLAY.md complete_bundle_sha256 1
listed_count scripts/issue_dg071_dg075_statistics.py PINNED_BUNDLE_SHA256 1
listed_count tests/goldens/axi_strict_validation_evidence.json validated_bundle_sha256 1
listed_count tests/goldens/output_identity_output_divergent.patch.json /spec_on_bundle/requests_artifact_sha256 1
listed_count tests/goldens/output_identity_text_divergent.patch.json /spec_on_bundle/requests_artifact_sha256 1
listed_count tests/goldens/output_identity_unassessable.patch.json /spec_on_bundle/requests_artifact_sha256 1
listed_population paper_results_file_digest bundles=100
listed_population p2015-df-cmp-abba-ph-decode-b01-a1 /Users/edr/code/JouleWise/runs_window_c_20260726 file_digest
listed_population p2015-df-cmp-abba-ph-decode-b01-a2 /Users/edr/code/JouleWise/runs_window_c_20260726 file_digest
listed_population p2015-df-cmp-abba-ph-decode-b01-b1 /Users/edr/code/JouleWise/runs_window_c_20260726 file_digest
listed_population p2015-df-cmp-abba-ph-decode-b01-b2 /Users/edr/code/JouleWise/runs_window_c_20260726 file_digest
listed_population p2015-df-cmp-abba-ph-decode-b02-a1 /Users/edr/code/JouleWise/runs_window_c_20260726 file_digest
listed_population p2015-df-cmp-abba-ph-decode-b02-a2 /Users/edr/code/JouleWise/runs_window_c_20260726 file_digest
listed_population p2015-df-cmp-abba-ph-decode-b02-b1 /Users/edr/code/JouleWise/runs_window_c_20260726 file_digest
listed_population p2015-df-cmp-abba-ph-decode-b02-b2 /Users/edr/code/JouleWise/runs_window_c_20260726 file_digest
listed_population p2015-df-cmp-abba-ph-decode-b03-a1 /Users/edr/code/JouleWise/runs_window_c_20260726 file_digest
listed_population p2015-df-cmp-abba-ph-decode-b03-a2 /Users/edr/code/JouleWise/runs_window_c_20260726 file_digest
listed_population p2015-df-cmp-abba-ph-decode-b03-b1 /Users/edr/code/JouleWise/runs_window_c_20260726 file_digest
listed_population p2015-df-cmp-abba-ph-decode-b03-b2 /Users/edr/code/JouleWise/runs_window_c_20260726 file_digest
listed_population p2015-df-cmp-abba-ph-decode-b04-a1 /Users/edr/code/JouleWise/runs_window_c_20260726 file_digest
listed_population p2015-df-cmp-abba-ph-decode-b04-a2 /Users/edr/code/JouleWise/runs_window_c_20260726 file_digest
listed_population p2015-df-cmp-abba-ph-decode-b04-b1 /Users/edr/code/JouleWise/runs_window_c_20260726 file_digest
listed_population p2015-df-cmp-abba-ph-decode-b04-b2 /Users/edr/code/JouleWise/runs_window_c_20260726 file_digest
listed_population p2015-df-cmp-abba-ph-decode-b05-a1 /Users/edr/code/JouleWise/runs_window_c_20260726 file_digest
listed_population p2015-df-cmp-abba-ph-decode-b05-a2 /Users/edr/code/JouleWise/runs_window_c_20260726 file_digest
listed_population p2015-df-cmp-abba-ph-decode-b05-b1 /Users/edr/code/JouleWise/runs_window_c_20260726 file_digest
listed_population p2015-df-cmp-abba-ph-decode-b05-b2 /Users/edr/code/JouleWise/runs_window_c_20260726 file_digest
listed_population p2015-df-cmp-abba-ph-decode-b06-a1 /Users/edr/code/JouleWise/runs_window_c_20260726 file_digest
listed_population p2015-df-cmp-abba-ph-decode-b06-a2 /Users/edr/code/JouleWise/runs_window_c_20260726 file_digest
listed_population p2015-df-cmp-abba-ph-decode-b06-b1 /Users/edr/code/JouleWise/runs_window_c_20260726 file_digest
listed_population p2015-df-cmp-abba-ph-decode-b06-b2 /Users/edr/code/JouleWise/runs_window_c_20260726 file_digest
listed_population p2015-df-cmp-abba-ph-decode-b07-a1 /Users/edr/code/JouleWise/runs_window_c_20260726 file_digest
listed_population p2015-df-cmp-abba-ph-decode-b07-a2 /Users/edr/code/JouleWise/runs_window_c_20260726 file_digest
listed_population p2015-df-cmp-abba-ph-decode-b07-b1 /Users/edr/code/JouleWise/runs_window_c_20260726 file_digest
listed_population p2015-df-cmp-abba-ph-decode-b07-b2 /Users/edr/code/JouleWise/runs_window_c_20260726 file_digest
listed_population p2015-df-cmp-abba-ph-decode-b08-a1 /Users/edr/code/JouleWise/runs_window_c_20260726 file_digest
listed_population p2015-df-cmp-abba-ph-decode-b08-a2 /Users/edr/code/JouleWise/runs_window_c_20260726 file_digest
listed_population p2015-df-cmp-abba-ph-decode-b08-b1 /Users/edr/code/JouleWise/runs_window_c_20260726 file_digest
listed_population p2015-df-cmp-abba-ph-decode-b08-b2 /Users/edr/code/JouleWise/runs_window_c_20260726 file_digest
listed_population p2015-df-cmp-abba-ph-decode-b09-a1 /Users/edr/code/JouleWise/runs_window_c_20260726 file_digest
listed_population p2015-df-cmp-abba-ph-decode-b09-a2 /Users/edr/code/JouleWise/runs_window_c_20260726 file_digest
listed_population p2015-df-cmp-abba-ph-decode-b09-b1 /Users/edr/code/JouleWise/runs_window_c_20260726 file_digest
listed_population p2015-df-cmp-abba-ph-decode-b09-b2 /Users/edr/code/JouleWise/runs_window_c_20260726 file_digest
listed_population p2015-df-cmp-abba-ph-decode-b10-a1 /Users/edr/code/JouleWise/runs_window_c_20260726 file_digest
listed_population p2015-df-cmp-abba-ph-decode-b10-a2 /Users/edr/code/JouleWise/runs_window_c_20260726 file_digest
listed_population p2015-df-cmp-abba-ph-decode-b10-b1 /Users/edr/code/JouleWise/runs_window_c_20260726 file_digest
listed_population p2015-df-cmp-abba-ph-decode-b10-b2 /Users/edr/code/JouleWise/runs_window_c_20260726 file_digest
listed_population p2015-df-ph-decode-abs-r01 /Users/edr/code/JouleWise/runs_window_a10_20260725 file_digest
listed_population p2015-df-ph-decode-abs-r02 /Users/edr/code/JouleWise/runs_window_a10_20260725 file_digest
listed_population p2015-df-ph-decode-abs-r03 /Users/edr/code/JouleWise/runs_window_a10_20260725 file_digest
listed_population p2015-df-ph-decode-abs-r04 /Users/edr/code/JouleWise/runs_window_a10_20260725 file_digest
listed_population p2015-df-ph-decode-abs-r05 /Users/edr/code/JouleWise/runs_window_a10_20260725 file_digest
listed_population p2015-df-ph-decode-abs-r06 /Users/edr/code/JouleWise/runs_window_a10_20260725 file_digest
listed_population p2015-df-ph-decode-abs-r07 /Users/edr/code/JouleWise/runs_window_a10_20260725 file_digest
listed_population p2015-df-ph-decode-abs-r08 /Users/edr/code/JouleWise/runs_window_a10_20260725 file_digest
listed_population p2015-df-ph-decode-abs-r09 /Users/edr/code/JouleWise/runs_window_a10_20260725 file_digest
listed_population p2015-df-ph-decode-abs-r10 /Users/edr/code/JouleWise/runs_window_a10_20260725 file_digest
listed_population sw7bfloor-df-cmp-abba-ph-decode-b01-a1 /Users/edr/code/JouleWise/runs_window_7bfloor_20260729 file_digest
listed_population sw7bfloor-df-cmp-abba-ph-decode-b01-a2 /Users/edr/code/JouleWise/runs_window_7bfloor_20260729 file_digest
listed_population sw7bfloor-df-cmp-abba-ph-decode-b01-b1 /Users/edr/code/JouleWise/runs_window_7bfloor_20260729 file_digest
listed_population sw7bfloor-df-cmp-abba-ph-decode-b01-b2 /Users/edr/code/JouleWise/runs_window_7bfloor_20260729 file_digest
listed_population sw7bfloor-df-cmp-abba-ph-decode-b02-a1 /Users/edr/code/JouleWise/runs_window_7bfloor_20260729 file_digest
listed_population sw7bfloor-df-cmp-abba-ph-decode-b02-a2 /Users/edr/code/JouleWise/runs_window_7bfloor_20260729 file_digest
listed_population sw7bfloor-df-cmp-abba-ph-decode-b02-b1 /Users/edr/code/JouleWise/runs_window_7bfloor_20260729 file_digest
listed_population sw7bfloor-df-cmp-abba-ph-decode-b02-b2 /Users/edr/code/JouleWise/runs_window_7bfloor_20260729 file_digest
listed_population sw7bfloor-df-cmp-abba-ph-decode-b03-a1 /Users/edr/code/JouleWise/runs_window_7bfloor_20260729 file_digest
listed_population sw7bfloor-df-cmp-abba-ph-decode-b03-a2 /Users/edr/code/JouleWise/runs_window_7bfloor_20260729 file_digest
listed_population sw7bfloor-df-cmp-abba-ph-decode-b03-b1 /Users/edr/code/JouleWise/runs_window_7bfloor_20260729 file_digest
listed_population sw7bfloor-df-cmp-abba-ph-decode-b03-b2 /Users/edr/code/JouleWise/runs_window_7bfloor_20260729 file_digest
listed_population sw7bfloor-df-cmp-abba-ph-decode-b04-a1 /Users/edr/code/JouleWise/runs_window_7bfloor_20260729 file_digest
listed_population sw7bfloor-df-cmp-abba-ph-decode-b04-a2 /Users/edr/code/JouleWise/runs_window_7bfloor_20260729 file_digest
listed_population sw7bfloor-df-cmp-abba-ph-decode-b04-b1 /Users/edr/code/JouleWise/runs_window_7bfloor_20260729 file_digest
listed_population sw7bfloor-df-cmp-abba-ph-decode-b04-b2 /Users/edr/code/JouleWise/runs_window_7bfloor_20260729 file_digest
listed_population sw7bfloor-df-cmp-abba-ph-decode-b05-a1 /Users/edr/code/JouleWise/runs_window_7bfloor_20260729 file_digest
listed_population sw7bfloor-df-cmp-abba-ph-decode-b05-a2 /Users/edr/code/JouleWise/runs_window_7bfloor_20260729 file_digest
listed_population sw7bfloor-df-cmp-abba-ph-decode-b05-b1 /Users/edr/code/JouleWise/runs_window_7bfloor_20260729 file_digest
listed_population sw7bfloor-df-cmp-abba-ph-decode-b05-b2 /Users/edr/code/JouleWise/runs_window_7bfloor_20260729 file_digest
listed_population sw7bfloor-df-cmp-abba-ph-decode-b06-a1 /Users/edr/code/JouleWise/runs_window_7bfloor_20260729 file_digest
listed_population sw7bfloor-df-cmp-abba-ph-decode-b06-a2 /Users/edr/code/JouleWise/runs_window_7bfloor_20260729 file_digest
listed_population sw7bfloor-df-cmp-abba-ph-decode-b06-b1 /Users/edr/code/JouleWise/runs_window_7bfloor_20260729 file_digest
listed_population sw7bfloor-df-cmp-abba-ph-decode-b06-b2 /Users/edr/code/JouleWise/runs_window_7bfloor_20260729 file_digest
listed_population sw7bfloor-df-cmp-abba-ph-decode-b07-a1 /Users/edr/code/JouleWise/runs_window_7bfloor_20260729 file_digest
listed_population sw7bfloor-df-cmp-abba-ph-decode-b07-a2 /Users/edr/code/JouleWise/runs_window_7bfloor_20260729 file_digest
listed_population sw7bfloor-df-cmp-abba-ph-decode-b07-b1 /Users/edr/code/JouleWise/runs_window_7bfloor_20260729 file_digest
listed_population sw7bfloor-df-cmp-abba-ph-decode-b07-b2 /Users/edr/code/JouleWise/runs_window_7bfloor_20260729 file_digest
listed_population sw7bfloor-df-cmp-abba-ph-decode-b08-a1 /Users/edr/code/JouleWise/runs_window_7bfloor_20260729 file_digest
listed_population sw7bfloor-df-cmp-abba-ph-decode-b08-a2 /Users/edr/code/JouleWise/runs_window_7bfloor_20260729 file_digest
listed_population sw7bfloor-df-cmp-abba-ph-decode-b08-b1 /Users/edr/code/JouleWise/runs_window_7bfloor_20260729 file_digest
listed_population sw7bfloor-df-cmp-abba-ph-decode-b08-b2 /Users/edr/code/JouleWise/runs_window_7bfloor_20260729 file_digest
listed_population sw7bfloor-df-cmp-abba-ph-decode-b09-a1 /Users/edr/code/JouleWise/runs_window_7bfloor_20260729 file_digest
listed_population sw7bfloor-df-cmp-abba-ph-decode-b09-a2 /Users/edr/code/JouleWise/runs_window_7bfloor_20260729 file_digest
listed_population sw7bfloor-df-cmp-abba-ph-decode-b09-b1 /Users/edr/code/JouleWise/runs_window_7bfloor_20260729 file_digest
listed_population sw7bfloor-df-cmp-abba-ph-decode-b09-b2 /Users/edr/code/JouleWise/runs_window_7bfloor_20260729 file_digest
listed_population sw7bfloor-df-cmp-abba-ph-decode-b10-a1 /Users/edr/code/JouleWise/runs_window_7bfloor_20260729 file_digest
listed_population sw7bfloor-df-cmp-abba-ph-decode-b10-a2 /Users/edr/code/JouleWise/runs_window_7bfloor_20260729 file_digest
listed_population sw7bfloor-df-cmp-abba-ph-decode-b10-b1 /Users/edr/code/JouleWise/runs_window_7bfloor_20260729 file_digest
listed_population sw7bfloor-df-cmp-abba-ph-decode-b10-b2 /Users/edr/code/JouleWise/runs_window_7bfloor_20260729 file_digest
listed_population sw7bfloor-df-ph-decode-abs-r01 /Users/edr/code/JouleWise/runs_window_7bfloor_20260729 file_digest
listed_population sw7bfloor-df-ph-decode-abs-r02 /Users/edr/code/JouleWise/runs_window_7bfloor_20260729 file_digest
listed_population sw7bfloor-df-ph-decode-abs-r03 /Users/edr/code/JouleWise/runs_window_7bfloor_20260729 file_digest
listed_population sw7bfloor-df-ph-decode-abs-r04 /Users/edr/code/JouleWise/runs_window_7bfloor_20260729 file_digest
listed_population sw7bfloor-df-ph-decode-abs-r05 /Users/edr/code/JouleWise/runs_window_7bfloor_20260729 file_digest
listed_population sw7bfloor-df-ph-decode-abs-r06 /Users/edr/code/JouleWise/runs_window_7bfloor_20260729 file_digest
listed_population sw7bfloor-df-ph-decode-abs-r07 /Users/edr/code/JouleWise/runs_window_7bfloor_20260729 file_digest
listed_population sw7bfloor-df-ph-decode-abs-r08 /Users/edr/code/JouleWise/runs_window_7bfloor_20260729 file_digest
listed_population sw7bfloor-df-ph-decode-abs-r09 /Users/edr/code/JouleWise/runs_window_7bfloor_20260729 file_digest
listed_population sw7bfloor-df-ph-decode-abs-r10 /Users/edr/code/JouleWise/runs_window_7bfloor_20260729 file_digest
```

## Reverse completeness witness

Command: `python3 scripts/build_battery_float_historical_bundles.py --check --witness /Users/edr/code/JouleWise/runs*`

Exit: 0

### stdout (verbatim)

```text
forward check: byte-identical entries=69
witness bundles=1402
witness listed tree /Users/edr/code/JouleWise/runs/example-mac-mlx-local__r1 9376dbc16848e03d3bd54e4fac5598b34e1391d376ef11db527ac1fe25f08773 analysis/rpt001-v2/artifact_manifest.json
witness included tree /Users/edr/code/JouleWise/runs/example-mac-mlx-local__r1 9376dbc16848e03d3bd54e4fac5598b34e1391d376ef11db527ac1fe25f08773 analysis/rpt001-v2/input_manifest.json
witness listed tree /Users/edr/code/JouleWise/runs/example-mac-mlx-local__r1 9376dbc16848e03d3bd54e4fac5598b34e1391d376ef11db527ac1fe25f08773 docs/legacy/strategy/2026-08-07-paper-portfolio/proposals/prop-param-scaling-energy.md
witness listed tree /Users/edr/code/JouleWise/runs/example-mac-mlx-local__r1 9376dbc16848e03d3bd54e4fac5598b34e1391d376ef11db527ac1fe25f08773 docs/process_traces/2026-08-07-plan-factory/DRAFT-QUANT_GATES.md
witness listed tree /Users/edr/code/JouleWise/runs/example-mac-mlx-local__r2 8a99d7a851c55e53631df6f910d17ee097cbf8bd19f33d44bcef911a6502e82f analysis/rpt001-v2/artifact_manifest.json
witness included tree /Users/edr/code/JouleWise/runs/example-mac-mlx-local__r2 8a99d7a851c55e53631df6f910d17ee097cbf8bd19f33d44bcef911a6502e82f analysis/rpt001-v2/input_manifest.json
witness listed tree /Users/edr/code/JouleWise/runs/example-mac-mlx-local__r2 8a99d7a851c55e53631df6f910d17ee097cbf8bd19f33d44bcef911a6502e82f docs/process_traces/2026-08-07-plan-factory/DRAFT-QUANT_GATES.md
witness listed tree /Users/edr/code/JouleWise/runs/example-mac-mlx-local__r3 5ec71ed301ba9c0a48b137b5bdce00b8893c62d4f1397f55aac3c1943ccc9180 analysis/rpt001-v2/artifact_manifest.json
witness included tree /Users/edr/code/JouleWise/runs/example-mac-mlx-local__r3 5ec71ed301ba9c0a48b137b5bdce00b8893c62d4f1397f55aac3c1943ccc9180 analysis/rpt001-v2/input_manifest.json
witness listed tree /Users/edr/code/JouleWise/runs/example-mac-mlx-local__r3 5ec71ed301ba9c0a48b137b5bdce00b8893c62d4f1397f55aac3c1943ccc9180 docs/legacy/strategy/2026-08-07-paper-portfolio/proposals/prop-param-scaling-energy.md
witness listed tree /Users/edr/code/JouleWise/runs/example-mac-mlx-local__r3 5ec71ed301ba9c0a48b137b5bdce00b8893c62d4f1397f55aac3c1943ccc9180 docs/process_traces/2026-08-07-plan-factory/DRAFT-QUANT_GATES.md
witness listed tree /Users/edr/code/JouleWise/runs/example-mac-mlx-qwen35-122b-512t__r1 9f162f058bfceb949f34e0c24042c83e8d7f353f97d87b4cf6e0e6dff0912398 analysis/rpt001-v2/artifact_manifest.json
witness included tree /Users/edr/code/JouleWise/runs/example-mac-mlx-qwen35-122b-512t__r1 9f162f058bfceb949f34e0c24042c83e8d7f353f97d87b4cf6e0e6dff0912398 analysis/rpt001-v2/input_manifest.json
witness listed tree /Users/edr/code/JouleWise/runs/example-mac-mlx-qwen35-122b-512t__r1 9f162f058bfceb949f34e0c24042c83e8d7f353f97d87b4cf6e0e6dff0912398 docs/legacy/strategy/2026-08-07-paper-portfolio/proposals/prop-moe-routing-energy.md
witness listed tree /Users/edr/code/JouleWise/runs/example-mac-mlx-qwen35-122b-512t__r1 9f162f058bfceb949f34e0c24042c83e8d7f353f97d87b4cf6e0e6dff0912398 docs/process_traces/2026-08-07-plan-factory/DRAFT-QUANT_GATES.md
witness listed tree /Users/edr/code/JouleWise/runs/example-mac-mlx-qwen35-122b-512t__r2 2888c9d205df62e1136a376997ea8a6947683e4311eedaee20e3135bd559e213 analysis/rpt001-v2/artifact_manifest.json
witness included tree /Users/edr/code/JouleWise/runs/example-mac-mlx-qwen35-122b-512t__r2 2888c9d205df62e1136a376997ea8a6947683e4311eedaee20e3135bd559e213 analysis/rpt001-v2/input_manifest.json
witness listed tree /Users/edr/code/JouleWise/runs/example-mac-mlx-qwen35-122b-512t__r2 2888c9d205df62e1136a376997ea8a6947683e4311eedaee20e3135bd559e213 docs/legacy/strategy/2026-08-07-paper-portfolio/proposals/prop-moe-routing-energy.md
witness listed tree /Users/edr/code/JouleWise/runs/example-mac-mlx-qwen35-122b-512t__r2 2888c9d205df62e1136a376997ea8a6947683e4311eedaee20e3135bd559e213 docs/legacy/strategy/2026-08-07-paper-portfolio/proposals/prop-param-scaling-energy.md
witness listed tree /Users/edr/code/JouleWise/runs/example-mac-mlx-qwen35-122b-512t__r2 2888c9d205df62e1136a376997ea8a6947683e4311eedaee20e3135bd559e213 docs/process_traces/2026-08-07-plan-factory/DRAFT-QUANT_GATES.md
witness listed tree /Users/edr/code/JouleWise/runs/example-mac-mlx-qwen35-122b-512t__r3 c72cdc34ef3ce9ccfb0a015bed5ace8e4efa7d18f457ac5cd8a0c894acc21268 analysis/rpt001-v2/artifact_manifest.json
witness included tree /Users/edr/code/JouleWise/runs/example-mac-mlx-qwen35-122b-512t__r3 c72cdc34ef3ce9ccfb0a015bed5ace8e4efa7d18f457ac5cd8a0c894acc21268 analysis/rpt001-v2/input_manifest.json
witness listed tree /Users/edr/code/JouleWise/runs/example-mac-mlx-qwen35-122b-512t__r3 c72cdc34ef3ce9ccfb0a015bed5ace8e4efa7d18f457ac5cd8a0c894acc21268 docs/legacy/strategy/2026-08-07-paper-portfolio/proposals/prop-moe-routing-energy.md
witness listed tree /Users/edr/code/JouleWise/runs/example-mac-mlx-qwen35-122b-512t__r3 c72cdc34ef3ce9ccfb0a015bed5ace8e4efa7d18f457ac5cd8a0c894acc21268 docs/process_traces/2026-08-07-plan-factory/DRAFT-QUANT_GATES.md
witness included complete /Users/edr/code/JouleWise/runs_window_a10_20260725/p2015-df-ph-decode-abs-r01 195b495930c4cdd532cfdd4773260ba3de73e585c7a3a9e55bac179e3b984195 df-ph-decode-floor-mint1.json
witness listed complete /Users/edr/code/JouleWise/runs_window_a10_20260725/p2015-df-ph-decode-abs-r01 195b495930c4cdd532cfdd4773260ba3de73e585c7a3a9e55bac179e3b984195 docs/legacy/strategy/2026-08-07-paper-portfolio/proposals/prop-param-scaling-energy.md
witness listed complete /Users/edr/code/JouleWise/runs_window_a10_20260725/p2015-df-ph-decode-abs-r01 195b495930c4cdd532cfdd4773260ba3de73e585c7a3a9e55bac179e3b984195 docs/process_traces/2026-08-07-plan-factory/DRAFT-NEVERZERO.md
witness included complete /Users/edr/code/JouleWise/runs_window_a10_20260725/p2015-df-ph-decode-abs-r02 a71d5519ecbf8a1659cbdca66d0d80b34e0350a9746ef5637e84e76771e5eea3 df-ph-decode-floor-mint1.json
witness listed complete /Users/edr/code/JouleWise/runs_window_a10_20260725/p2015-df-ph-decode-abs-r02 a71d5519ecbf8a1659cbdca66d0d80b34e0350a9746ef5637e84e76771e5eea3 docs/process_traces/2026-08-07-plan-factory/DRAFT-NEVERZERO.md
witness included complete /Users/edr/code/JouleWise/runs_window_a10_20260725/p2015-df-ph-decode-abs-r03 c285172881235ef1ed0e29731c412706604e8cd182182981a5ed44cc2df986bf df-ph-decode-floor-mint1.json
witness listed complete /Users/edr/code/JouleWise/runs_window_a10_20260725/p2015-df-ph-decode-abs-r03 c285172881235ef1ed0e29731c412706604e8cd182182981a5ed44cc2df986bf docs/process_traces/2026-08-07-plan-factory/DRAFT-NEVERZERO.md
witness included complete /Users/edr/code/JouleWise/runs_window_a10_20260725/p2015-df-ph-decode-abs-r04 e35798402f4af613c21e7bd5069875a4194b6672c3c3ab1c3073fff3ec05b17d df-ph-decode-floor-mint1.json
witness listed complete /Users/edr/code/JouleWise/runs_window_a10_20260725/p2015-df-ph-decode-abs-r04 e35798402f4af613c21e7bd5069875a4194b6672c3c3ab1c3073fff3ec05b17d docs/process_traces/2026-08-07-plan-factory/DRAFT-NEVERZERO.md
witness included complete /Users/edr/code/JouleWise/runs_window_a10_20260725/p2015-df-ph-decode-abs-r05 b2b10d7dc7c70820ffa7be4cd6e5c7d99bfb723c24ecc8aa143b92b28a18cca2 df-ph-decode-floor-mint1.json
witness listed complete /Users/edr/code/JouleWise/runs_window_a10_20260725/p2015-df-ph-decode-abs-r05 b2b10d7dc7c70820ffa7be4cd6e5c7d99bfb723c24ecc8aa143b92b28a18cca2 docs/legacy/strategy/2026-08-07-paper-portfolio/proposals/prop-param-scaling-energy.md
witness listed complete /Users/edr/code/JouleWise/runs_window_a10_20260725/p2015-df-ph-decode-abs-r05 b2b10d7dc7c70820ffa7be4cd6e5c7d99bfb723c24ecc8aa143b92b28a18cca2 docs/process_traces/2026-08-07-plan-factory/DRAFT-NEVERZERO.md
witness included complete /Users/edr/code/JouleWise/runs_window_a10_20260725/p2015-df-ph-decode-abs-r06 ec172522b7ba17c83008f32994e0c727cad2bc857aee4b6a18b4c6ac4ed14446 df-ph-decode-floor-mint1.json
witness listed complete /Users/edr/code/JouleWise/runs_window_a10_20260725/p2015-df-ph-decode-abs-r06 ec172522b7ba17c83008f32994e0c727cad2bc857aee4b6a18b4c6ac4ed14446 docs/process_traces/2026-08-07-plan-factory/DRAFT-NEVERZERO.md
witness included complete /Users/edr/code/JouleWise/runs_window_a10_20260725/p2015-df-ph-decode-abs-r07 2863fa61af00fb8e23c68bd6848c9eb7f630d21827aefa4ba9af9b09a05537c9 df-ph-decode-floor-mint1.json
witness listed complete /Users/edr/code/JouleWise/runs_window_a10_20260725/p2015-df-ph-decode-abs-r07 2863fa61af00fb8e23c68bd6848c9eb7f630d21827aefa4ba9af9b09a05537c9 docs/process_traces/2026-08-07-plan-factory/DRAFT-NEVERZERO.md
witness included complete /Users/edr/code/JouleWise/runs_window_a10_20260725/p2015-df-ph-decode-abs-r08 153af6c4d94ba5f9e67f23cf4151703b27d430717dc3d9b773258f7ffdd40593 df-ph-decode-floor-mint1.json
witness listed complete /Users/edr/code/JouleWise/runs_window_a10_20260725/p2015-df-ph-decode-abs-r08 153af6c4d94ba5f9e67f23cf4151703b27d430717dc3d9b773258f7ffdd40593 docs/legacy/strategy/2026-08-07-paper-portfolio/proposals/prop-param-scaling-energy.md
witness listed complete /Users/edr/code/JouleWise/runs_window_a10_20260725/p2015-df-ph-decode-abs-r08 153af6c4d94ba5f9e67f23cf4151703b27d430717dc3d9b773258f7ffdd40593 docs/process_traces/2026-08-07-plan-factory/DRAFT-NEVERZERO.md
witness included complete /Users/edr/code/JouleWise/runs_window_a10_20260725/p2015-df-ph-decode-abs-r09 1a7a291dd1b789f95faf8c873a459fd4d8bb6b26257f8866726151f6c156cb96 df-ph-decode-floor-mint1.json
witness listed complete /Users/edr/code/JouleWise/runs_window_a10_20260725/p2015-df-ph-decode-abs-r09 1a7a291dd1b789f95faf8c873a459fd4d8bb6b26257f8866726151f6c156cb96 docs/process_traces/2026-08-07-plan-factory/DRAFT-NEVERZERO.md
witness included complete /Users/edr/code/JouleWise/runs_window_a10_20260725/p2015-df-ph-decode-abs-r10 1624fc548379c427d047187df164fa297bec2080062f28bb809a2dba80c94a00 df-ph-decode-floor-mint1.json
witness listed complete /Users/edr/code/JouleWise/runs_window_a10_20260725/p2015-df-ph-decode-abs-r10 1624fc548379c427d047187df164fa297bec2080062f28bb809a2dba80c94a00 docs/process_traces/2026-08-07-plan-factory/DRAFT-NEVERZERO.md
witness listed complete /Users/edr/code/JouleWise/runs_window_a10_20260725/p2015-df-ph-prefill-abs-r01 9dd33c8f5bb5de530ccb0abff96435abc687d27db7286076415008eacd898c5f docs/process_traces/2026-08-07-plan-factory/DRAFT-NEVERZERO.md
witness listed complete /Users/edr/code/JouleWise/runs_window_a5_20260723/p2015-df-cmp-abba-ph-decode-b01-a1 ac6b87e6005d8d3737e1c02fe58571447ca0f2468a515f3a5630ba3ea3ecfe02 docs/process_traces/2026-08-08-attribution-debate/COMMONMODE-REPLAY.md
witness listed complete /Users/edr/code/JouleWise/runs_window_a5_20260723/p2015-df-cmp-abba-ph-decode-b01-a2 ea1291f6a32c05aa59a2dbbfd17cc9350a1a1a62da9e58d4bc6fb46b1efa4595 docs/process_traces/2026-08-08-attribution-debate/COMMONMODE-REPLAY.md
witness listed complete /Users/edr/code/JouleWise/runs_window_a5_20260723/p2015-df-cmp-abba-ph-decode-b01-b1 f1ac2a656d6514fa92e84065f7892683893caf92ac1cbf4ab979ca8bd32a6d15 docs/process_traces/2026-08-08-attribution-debate/COMMONMODE-REPLAY.md
witness listed complete /Users/edr/code/JouleWise/runs_window_a5_20260723/p2015-df-cmp-abba-ph-decode-b01-b2 e66e7f4ac7e39336b6d1e2ecb1d426996944783bfdd9ea993a8643df4c9ce06d docs/process_traces/2026-08-08-attribution-debate/COMMONMODE-REPLAY.md
witness listed complete /Users/edr/code/JouleWise/runs_window_a5_20260723/p2015-df-cmp-abba-ph-decode-b02-a1 ca5ef622abc4d4ec29c96f5432de659deea42ddb73a5ddc385355ebb0766d0e4 docs/process_traces/2026-08-08-attribution-debate/COMMONMODE-REPLAY.md
witness listed complete /Users/edr/code/JouleWise/runs_window_a5_20260723/p2015-df-cmp-abba-ph-decode-b02-a2 27e49d56cb67d487ff573f4edadb63847f9edb69d5e2d21d1d7e6eb460b5f4d4 docs/process_traces/2026-08-08-attribution-debate/COMMONMODE-REPLAY.md
witness listed complete /Users/edr/code/JouleWise/runs_window_a5_20260723/p2015-df-cmp-abba-ph-decode-b02-b1 142c12760c1cede038665b98249ba133382f272a09a8570d4c553bb0155441b5 docs/process_traces/2026-08-08-attribution-debate/COMMONMODE-REPLAY.md
witness listed complete /Users/edr/code/JouleWise/runs_window_a5_20260723/p2015-df-cmp-abba-ph-decode-b02-b2 7a5fc39c76b84248b3a2bdd2f7283898523c0f8a77cd5acba262155132f99e70 docs/process_traces/2026-08-08-attribution-debate/COMMONMODE-REPLAY.md
witness listed complete /Users/edr/code/JouleWise/runs_window_a5_20260723/p2015-df-cmp-abba-ph-decode-b03-a1 627d9f8510deb0687340e533009be2af6fbcc8fb1103d8f906ce60b9c75d738d docs/process_traces/2026-08-08-attribution-debate/COMMONMODE-REPLAY.md
witness listed complete /Users/edr/code/JouleWise/runs_window_a5_20260723/p2015-df-cmp-abba-ph-decode-b03-a2 d6486439e275a96e2f8ed3212e2ac7e537232df68f4a3f6c974b1e02d7e2d3ed docs/process_traces/2026-08-08-attribution-debate/COMMONMODE-REPLAY.md
witness listed complete /Users/edr/code/JouleWise/runs_window_a5_20260723/p2015-df-cmp-abba-ph-decode-b03-b1 16e43706e063d833c32614fb0a75ed0f4fc258a60eae0cdf7aff93d419ff4438 docs/process_traces/2026-08-08-attribution-debate/COMMONMODE-REPLAY.md
witness listed complete /Users/edr/code/JouleWise/runs_window_a5_20260723/p2015-df-cmp-abba-ph-decode-b03-b2 536bcf2bb15af7f325f3e3e5f67ac2da46a8b6b3f6ee0e37f6dd2df20389b223 docs/process_traces/2026-08-08-attribution-debate/COMMONMODE-REPLAY.md
witness listed complete /Users/edr/code/JouleWise/runs_window_a5_20260723/p2015-df-cmp-abba-ph-decode-b04-a1 27d2847d85306f5181c4831426a340bbdedf555a9491c6249740cd70af3adf39 docs/process_traces/2026-08-08-attribution-debate/COMMONMODE-REPLAY.md
witness listed complete /Users/edr/code/JouleWise/runs_window_a5_20260723/p2015-df-cmp-abba-ph-decode-b04-a2 c29db85c8980058951816baa18dac5b6322d50fed5be24392a57d1a44c2ef15a docs/process_traces/2026-08-08-attribution-debate/COMMONMODE-REPLAY.md
witness listed complete /Users/edr/code/JouleWise/runs_window_a5_20260723/p2015-df-cmp-abba-ph-decode-b04-b1 1b825caa961d579dbd4bec82b3943c498ab2799df8976adcab14660b39625cbf docs/process_traces/2026-08-08-attribution-debate/COMMONMODE-REPLAY.md
witness listed complete /Users/edr/code/JouleWise/runs_window_a5_20260723/p2015-df-cmp-abba-ph-decode-b04-b2 6f71f212143dab57c7bd8053dfec08f1f798b5c8cedf6dde623c179d772d90ea docs/process_traces/2026-08-08-attribution-debate/COMMONMODE-REPLAY.md
witness listed complete /Users/edr/code/JouleWise/runs_window_a5_20260723/p2015-df-cmp-abba-ph-decode-b05-a1 fca491eae21a421fca171eb1d4dee172ee9b09b52fcbddfb724a49e0e95e6808 docs/process_traces/2026-08-08-attribution-debate/COMMONMODE-REPLAY.md
witness listed complete /Users/edr/code/JouleWise/runs_window_a5_20260723/p2015-df-cmp-abba-ph-decode-b05-a2 23484dee9aafe083f1cffc22ea5542ccb841305b7f4c8531a225efbc914a1637 docs/process_traces/2026-08-08-attribution-debate/COMMONMODE-REPLAY.md
witness listed complete /Users/edr/code/JouleWise/runs_window_a5_20260723/p2015-df-cmp-abba-ph-decode-b05-b1 021be8c7a7ead2404f35c07f6cdfd52aff4f6f250e591aa30277101f226af6ac docs/process_traces/2026-08-08-attribution-debate/COMMONMODE-REPLAY.md
witness listed complete /Users/edr/code/JouleWise/runs_window_a5_20260723/p2015-df-cmp-abba-ph-decode-b05-b2 2c87974fb346c285567cc9172ea55d9c95a356021799484fcdf651162dc477c5 docs/process_traces/2026-08-08-attribution-debate/COMMONMODE-REPLAY.md
witness listed complete /Users/edr/code/JouleWise/runs_window_a5_20260723/p2015-df-cmp-abba-ph-decode-b06-a1 027d87f3a799df9951ce4311bec579a7b94951a6b25142508780a1e8e21aaea1 docs/process_traces/2026-08-08-attribution-debate/COMMONMODE-REPLAY.md
witness listed complete /Users/edr/code/JouleWise/runs_window_a5_20260723/p2015-df-cmp-abba-ph-decode-b06-a2 e71dfb547be58e13a0cfc7cdb17488a4d9d54ae6fe308b4362e58968a6afd4f9 docs/process_traces/2026-08-08-attribution-debate/COMMONMODE-REPLAY.md
witness listed complete /Users/edr/code/JouleWise/runs_window_a5_20260723/p2015-df-cmp-abba-ph-decode-b06-b1 2cf02ef3269518e919a72acfdf63b62828961de8678cfdef41241b190f894c60 docs/process_traces/2026-08-08-attribution-debate/COMMONMODE-REPLAY.md
witness listed complete /Users/edr/code/JouleWise/runs_window_a5_20260723/p2015-df-cmp-abba-ph-decode-b06-b2 618834e11ec3d94dff129fb157db0d4883dde082d05940ee7498f53d742daed4 docs/process_traces/2026-08-08-attribution-debate/COMMONMODE-REPLAY.md
witness listed complete /Users/edr/code/JouleWise/runs_window_a5_20260723/p2015-df-cmp-abba-ph-decode-b07-a1 bf95c37a75f61c1ddd082af9043cdf5f4daee47a8f557388f30ec73569ead98f docs/process_traces/2026-08-08-attribution-debate/COMMONMODE-REPLAY.md
witness listed complete /Users/edr/code/JouleWise/runs_window_a5_20260723/p2015-df-cmp-abba-ph-decode-b07-a2 b52295202a323aacc5f5046a507fc2a94c2c386578bc43f3df3adfe36805f7f1 docs/process_traces/2026-08-08-attribution-debate/COMMONMODE-REPLAY.md
witness listed complete /Users/edr/code/JouleWise/runs_window_a5_20260723/p2015-df-cmp-abba-ph-decode-b07-b1 3d80258d2dc3aa868bc7560bb1a72e31aef273b32575d9c3d37f8e5d7b185c2b docs/process_traces/2026-08-08-attribution-debate/COMMONMODE-REPLAY.md
witness listed complete /Users/edr/code/JouleWise/runs_window_a5_20260723/p2015-df-cmp-abba-ph-decode-b07-b2 b9b859aba669d0c118c0a026e3f8af816039f24781138ba561358165167239b7 docs/process_traces/2026-08-08-attribution-debate/COMMONMODE-REPLAY.md
witness listed complete /Users/edr/code/JouleWise/runs_window_a5_20260723/p2015-df-cmp-abba-ph-decode-b08-a1 75eaf5ae9cb0f3dc4ee3bc5afe74cf0344ecbabefd42c52b8df60a3584444b64 docs/process_traces/2026-08-08-attribution-debate/COMMONMODE-REPLAY.md
witness listed complete /Users/edr/code/JouleWise/runs_window_a5_20260723/p2015-df-cmp-abba-ph-decode-b08-a2 2b8827700b94c17483ffe1c252d115e6733e12132e7347d29a8531ac97397336 docs/process_traces/2026-08-08-attribution-debate/COMMONMODE-REPLAY.md
witness listed complete /Users/edr/code/JouleWise/runs_window_a5_20260723/p2015-df-cmp-abba-ph-decode-b08-b1 9ee040ca0e00dbb66665164d65191a10318121049f0cc2a962c30a3db50f0825 docs/process_traces/2026-08-08-attribution-debate/COMMONMODE-REPLAY.md
witness listed complete /Users/edr/code/JouleWise/runs_window_a5_20260723/p2015-df-cmp-abba-ph-decode-b08-b2 82f713219e2ba797ddff99c3d4b57c1d14d9f55a58932e47304c1a2f85cd01dd docs/process_traces/2026-08-08-attribution-debate/COMMONMODE-REPLAY.md
witness listed complete /Users/edr/code/JouleWise/runs_window_a5_20260723/p2015-df-cmp-abba-ph-decode-b09-a1 89770eb0bcde68fa3049591efe5a08f22cbf4e451d40ac2a95fecb68e54a798a docs/process_traces/2026-08-08-attribution-debate/COMMONMODE-REPLAY.md
witness listed complete /Users/edr/code/JouleWise/runs_window_a5_20260723/p2015-df-cmp-abba-ph-decode-b09-a2 faae7684c398587bb49bd1120e83a3c5c78cd0139e33cd22b5d1e08bd7ee6017 docs/process_traces/2026-08-08-attribution-debate/COMMONMODE-REPLAY.md
witness listed complete /Users/edr/code/JouleWise/runs_window_a5_20260723/p2015-df-cmp-abba-ph-decode-b09-b1 614f0c38f43932b92744d82e1a7bab2eb2940ac5f7355c54ad142c4b11cd3aab docs/process_traces/2026-08-08-attribution-debate/COMMONMODE-REPLAY.md
witness listed complete /Users/edr/code/JouleWise/runs_window_a5_20260723/p2015-df-cmp-abba-ph-decode-b09-b2 a5d39fff38d413ca4675b21656bdcad4dbcaeafb9839af4d076b5035121bbec0 docs/process_traces/2026-08-08-attribution-debate/COMMONMODE-REPLAY.md
witness listed complete /Users/edr/code/JouleWise/runs_window_a5_20260723/p2015-df-cmp-abba-ph-decode-b10-a1 efab1fc895a98d296e86491c1c22d7d5bb3948fcc8ae02deca4477f218e770a0 docs/process_traces/2026-08-08-attribution-debate/COMMONMODE-REPLAY.md
witness listed complete /Users/edr/code/JouleWise/runs_window_a5_20260723/p2015-df-cmp-abba-ph-decode-b10-a2 f0f8901691a3a57da68989cd02abea1c2f9ed9f41c37b59fdcd358a4a74abd2c docs/process_traces/2026-08-08-attribution-debate/COMMONMODE-REPLAY.md
witness listed complete /Users/edr/code/JouleWise/runs_window_a5_20260723/p2015-df-cmp-abba-ph-decode-b10-b1 6363a5a4021227adf3431dbfd89746b132484aedd2db0fabc75b11ee00024cf7 docs/process_traces/2026-08-08-attribution-debate/COMMONMODE-REPLAY.md
witness listed complete /Users/edr/code/JouleWise/runs_window_a5_20260723/p2015-df-cmp-abba-ph-decode-b10-b2 a7734f9176ba682da73e068dff6fcc359032f53d8c9448cd2ae010a20ad399f3 docs/process_traces/2026-08-08-attribution-debate/COMMONMODE-REPLAY.md
witness included complete /Users/edr/code/JouleWise/runs_window_c_20260726/p2015-df-cmp-abba-ph-decode-b01-a1 0a22a02caa28f0c75bc460339dd420604638cf5f7aa17a0ca2e4fd1c8afbb9ae df-ph-decode-floor-mint1.json
witness listed complete /Users/edr/code/JouleWise/runs_window_c_20260726/p2015-df-cmp-abba-ph-decode-b01-a1 0a22a02caa28f0c75bc460339dd420604638cf5f7aa17a0ca2e4fd1c8afbb9ae docs/process_traces/2026-08-07-plan-factory/DRAFT-NEVERZERO.md
witness included complete /Users/edr/code/JouleWise/runs_window_c_20260726/p2015-df-cmp-abba-ph-decode-b01-a2 2d1c88636ad93b0727cb01d8d4c70253fc5318ce3033b9d11e2bc0e4d8a68733 df-ph-decode-floor-mint1.json
witness listed complete /Users/edr/code/JouleWise/runs_window_c_20260726/p2015-df-cmp-abba-ph-decode-b01-a2 2d1c88636ad93b0727cb01d8d4c70253fc5318ce3033b9d11e2bc0e4d8a68733 docs/legacy/strategy/2026-08-07-paper-portfolio/proposals/prop-param-scaling-energy.md
witness listed complete /Users/edr/code/JouleWise/runs_window_c_20260726/p2015-df-cmp-abba-ph-decode-b01-a2 2d1c88636ad93b0727cb01d8d4c70253fc5318ce3033b9d11e2bc0e4d8a68733 docs/process_traces/2026-08-07-plan-factory/DRAFT-NEVERZERO.md
witness included complete /Users/edr/code/JouleWise/runs_window_c_20260726/p2015-df-cmp-abba-ph-decode-b01-b1 b25522da721b5a7deb6060fa1ed4ce22c174bcefa6d47617a76bfb90b23f4755 df-ph-decode-floor-mint1.json
witness listed complete /Users/edr/code/JouleWise/runs_window_c_20260726/p2015-df-cmp-abba-ph-decode-b01-b1 b25522da721b5a7deb6060fa1ed4ce22c174bcefa6d47617a76bfb90b23f4755 docs/process_traces/2026-08-07-plan-factory/DRAFT-NEVERZERO.md
witness included complete /Users/edr/code/JouleWise/runs_window_c_20260726/p2015-df-cmp-abba-ph-decode-b01-b2 584b8d1b73e7f5a5d8fe4b1e6b0f5e3a6382bb84a57c5cd6015eda31a26c31e5 df-ph-decode-floor-mint1.json
witness listed complete /Users/edr/code/JouleWise/runs_window_c_20260726/p2015-df-cmp-abba-ph-decode-b01-b2 584b8d1b73e7f5a5d8fe4b1e6b0f5e3a6382bb84a57c5cd6015eda31a26c31e5 docs/process_traces/2026-08-07-plan-factory/DRAFT-NEVERZERO.md
witness included complete /Users/edr/code/JouleWise/runs_window_c_20260726/p2015-df-cmp-abba-ph-decode-b02-a1 f39fcdfe56370dc2ed33f53c6901ebcfda3362193f5f0f865d8b366c0a3eb80d df-ph-decode-floor-mint1.json
witness listed complete /Users/edr/code/JouleWise/runs_window_c_20260726/p2015-df-cmp-abba-ph-decode-b02-a1 f39fcdfe56370dc2ed33f53c6901ebcfda3362193f5f0f865d8b366c0a3eb80d docs/process_traces/2026-08-07-plan-factory/DRAFT-NEVERZERO.md
witness included complete /Users/edr/code/JouleWise/runs_window_c_20260726/p2015-df-cmp-abba-ph-decode-b02-a2 8a9216a68466a432fe65e7ff9d48664d1c1e8b297b9a011cbe4f462e291220b4 df-ph-decode-floor-mint1.json
witness listed complete /Users/edr/code/JouleWise/runs_window_c_20260726/p2015-df-cmp-abba-ph-decode-b02-a2 8a9216a68466a432fe65e7ff9d48664d1c1e8b297b9a011cbe4f462e291220b4 docs/process_traces/2026-08-07-plan-factory/DRAFT-NEVERZERO.md
witness included complete /Users/edr/code/JouleWise/runs_window_c_20260726/p2015-df-cmp-abba-ph-decode-b02-b1 f29039135ac92d31ea88c277682ff79aae0474ac741c2a18d2a1930f71be620b df-ph-decode-floor-mint1.json
witness listed complete /Users/edr/code/JouleWise/runs_window_c_20260726/p2015-df-cmp-abba-ph-decode-b02-b1 f29039135ac92d31ea88c277682ff79aae0474ac741c2a18d2a1930f71be620b docs/process_traces/2026-08-07-plan-factory/DRAFT-NEVERZERO.md
witness included complete /Users/edr/code/JouleWise/runs_window_c_20260726/p2015-df-cmp-abba-ph-decode-b02-b2 b200324cffed9a1db87323a5961d28dbdc593e743d623423b6862e5f643f5273 df-ph-decode-floor-mint1.json
witness listed complete /Users/edr/code/JouleWise/runs_window_c_20260726/p2015-df-cmp-abba-ph-decode-b02-b2 b200324cffed9a1db87323a5961d28dbdc593e743d623423b6862e5f643f5273 docs/legacy/strategy/2026-08-07-paper-portfolio/proposals/prop-param-scaling-energy.md
witness listed complete /Users/edr/code/JouleWise/runs_window_c_20260726/p2015-df-cmp-abba-ph-decode-b02-b2 b200324cffed9a1db87323a5961d28dbdc593e743d623423b6862e5f643f5273 docs/process_traces/2026-08-07-plan-factory/DRAFT-NEVERZERO.md
witness included complete /Users/edr/code/JouleWise/runs_window_c_20260726/p2015-df-cmp-abba-ph-decode-b03-a1 b27c6af7109a5734079ad311df84f812680daa957e2b5121de46372fe6871bf3 df-ph-decode-floor-mint1.json
witness listed complete /Users/edr/code/JouleWise/runs_window_c_20260726/p2015-df-cmp-abba-ph-decode-b03-a1 b27c6af7109a5734079ad311df84f812680daa957e2b5121de46372fe6871bf3 docs/process_traces/2026-08-07-plan-factory/DRAFT-NEVERZERO.md
witness included complete /Users/edr/code/JouleWise/runs_window_c_20260726/p2015-df-cmp-abba-ph-decode-b03-a2 59aade4961b9e59f1696f88f263204f3739cb7d81adc754cc3380a0133f92691 df-ph-decode-floor-mint1.json
witness listed complete /Users/edr/code/JouleWise/runs_window_c_20260726/p2015-df-cmp-abba-ph-decode-b03-a2 59aade4961b9e59f1696f88f263204f3739cb7d81adc754cc3380a0133f92691 docs/process_traces/2026-08-07-plan-factory/DRAFT-NEVERZERO.md
witness included complete /Users/edr/code/JouleWise/runs_window_c_20260726/p2015-df-cmp-abba-ph-decode-b03-b1 ec6fda56898612837eb76d658c9057ab0e08e26689e44b1dea1a296dd17674b2 df-ph-decode-floor-mint1.json
witness listed complete /Users/edr/code/JouleWise/runs_window_c_20260726/p2015-df-cmp-abba-ph-decode-b03-b1 ec6fda56898612837eb76d658c9057ab0e08e26689e44b1dea1a296dd17674b2 docs/process_traces/2026-08-07-plan-factory/DRAFT-NEVERZERO.md
witness included complete /Users/edr/code/JouleWise/runs_window_c_20260726/p2015-df-cmp-abba-ph-decode-b03-b2 8eaba1d3b0069dd913aafabff74f6d2b6dfab066a0b30e8f4f68322a84973903 df-ph-decode-floor-mint1.json
witness listed complete /Users/edr/code/JouleWise/runs_window_c_20260726/p2015-df-cmp-abba-ph-decode-b03-b2 8eaba1d3b0069dd913aafabff74f6d2b6dfab066a0b30e8f4f68322a84973903 docs/legacy/strategy/2026-08-07-paper-portfolio/proposals/prop-param-scaling-energy.md
witness listed complete /Users/edr/code/JouleWise/runs_window_c_20260726/p2015-df-cmp-abba-ph-decode-b03-b2 8eaba1d3b0069dd913aafabff74f6d2b6dfab066a0b30e8f4f68322a84973903 docs/process_traces/2026-08-07-plan-factory/DRAFT-NEVERZERO.md
witness included complete /Users/edr/code/JouleWise/runs_window_c_20260726/p2015-df-cmp-abba-ph-decode-b04-a1 2ecceeb9237077c2f3a6577c9d7bce24d3deeb926df1e15f1b389bad0db02147 df-ph-decode-floor-mint1.json
witness listed complete /Users/edr/code/JouleWise/runs_window_c_20260726/p2015-df-cmp-abba-ph-decode-b04-a1 2ecceeb9237077c2f3a6577c9d7bce24d3deeb926df1e15f1b389bad0db02147 docs/process_traces/2026-08-07-plan-factory/DRAFT-NEVERZERO.md
witness included complete /Users/edr/code/JouleWise/runs_window_c_20260726/p2015-df-cmp-abba-ph-decode-b04-a2 769d1d1378e3603fe40013fadeda35504eca0c235f773106233323fba5a61163 df-ph-decode-floor-mint1.json
witness listed complete /Users/edr/code/JouleWise/runs_window_c_20260726/p2015-df-cmp-abba-ph-decode-b04-a2 769d1d1378e3603fe40013fadeda35504eca0c235f773106233323fba5a61163 docs/process_traces/2026-08-07-plan-factory/DRAFT-NEVERZERO.md
witness included complete /Users/edr/code/JouleWise/runs_window_c_20260726/p2015-df-cmp-abba-ph-decode-b04-b1 48a8bb2a6f23c6531eae6f8d99c043e0500379aff9427956fee1b74de75694ff df-ph-decode-floor-mint1.json
witness listed complete /Users/edr/code/JouleWise/runs_window_c_20260726/p2015-df-cmp-abba-ph-decode-b04-b1 48a8bb2a6f23c6531eae6f8d99c043e0500379aff9427956fee1b74de75694ff docs/process_traces/2026-08-07-plan-factory/DRAFT-NEVERZERO.md
witness included complete /Users/edr/code/JouleWise/runs_window_c_20260726/p2015-df-cmp-abba-ph-decode-b04-b2 eb05f32d37b1c8e8969f097a0ff112ea95e7ca9c1110e03127b7538267414449 df-ph-decode-floor-mint1.json
witness listed complete /Users/edr/code/JouleWise/runs_window_c_20260726/p2015-df-cmp-abba-ph-decode-b04-b2 eb05f32d37b1c8e8969f097a0ff112ea95e7ca9c1110e03127b7538267414449 docs/process_traces/2026-08-07-plan-factory/DRAFT-NEVERZERO.md
witness included complete /Users/edr/code/JouleWise/runs_window_c_20260726/p2015-df-cmp-abba-ph-decode-b05-a1 9d67992e7cdd70a86bbbf82ca6a9b587d42779c14a28f72256900331d9f8fece df-ph-decode-floor-mint1.json
witness listed complete /Users/edr/code/JouleWise/runs_window_c_20260726/p2015-df-cmp-abba-ph-decode-b05-a1 9d67992e7cdd70a86bbbf82ca6a9b587d42779c14a28f72256900331d9f8fece docs/process_traces/2026-08-07-plan-factory/DRAFT-NEVERZERO.md
witness included complete /Users/edr/code/JouleWise/runs_window_c_20260726/p2015-df-cmp-abba-ph-decode-b05-a2 0eb6a006b4afc1cc031a3786a0cc1180686cdb78cb9375788370a3bfd86e8060 df-ph-decode-floor-mint1.json
witness listed complete /Users/edr/code/JouleWise/runs_window_c_20260726/p2015-df-cmp-abba-ph-decode-b05-a2 0eb6a006b4afc1cc031a3786a0cc1180686cdb78cb9375788370a3bfd86e8060 docs/legacy/strategy/2026-08-07-paper-portfolio/proposals/prop-param-scaling-energy.md
witness listed complete /Users/edr/code/JouleWise/runs_window_c_20260726/p2015-df-cmp-abba-ph-decode-b05-a2 0eb6a006b4afc1cc031a3786a0cc1180686cdb78cb9375788370a3bfd86e8060 docs/process_traces/2026-08-07-plan-factory/DRAFT-NEVERZERO.md
witness included complete /Users/edr/code/JouleWise/runs_window_c_20260726/p2015-df-cmp-abba-ph-decode-b05-b1 5c7a8a6ce946d88fdd5ea0124bafa1ffad8c289308d5e9b600d2f95e280bb025 df-ph-decode-floor-mint1.json
witness listed complete /Users/edr/code/JouleWise/runs_window_c_20260726/p2015-df-cmp-abba-ph-decode-b05-b1 5c7a8a6ce946d88fdd5ea0124bafa1ffad8c289308d5e9b600d2f95e280bb025 docs/process_traces/2026-08-07-plan-factory/DRAFT-NEVERZERO.md
witness included complete /Users/edr/code/JouleWise/runs_window_c_20260726/p2015-df-cmp-abba-ph-decode-b05-b2 39054c62e30e8362a0ef473fb674aed5d1c87df7c630d0f4daadfd296874439e df-ph-decode-floor-mint1.json
witness listed complete /Users/edr/code/JouleWise/runs_window_c_20260726/p2015-df-cmp-abba-ph-decode-b05-b2 39054c62e30e8362a0ef473fb674aed5d1c87df7c630d0f4daadfd296874439e docs/process_traces/2026-08-07-plan-factory/DRAFT-NEVERZERO.md
witness included complete /Users/edr/code/JouleWise/runs_window_c_20260726/p2015-df-cmp-abba-ph-decode-b06-a1 5135406fa3ba08b4df498cfbe12a463607a829db546a13d273e7b97fdb1aab50 df-ph-decode-floor-mint1.json
witness listed complete /Users/edr/code/JouleWise/runs_window_c_20260726/p2015-df-cmp-abba-ph-decode-b06-a1 5135406fa3ba08b4df498cfbe12a463607a829db546a13d273e7b97fdb1aab50 docs/legacy/strategy/2026-08-07-paper-portfolio/proposals/prop-param-scaling-energy.md
witness listed complete /Users/edr/code/JouleWise/runs_window_c_20260726/p2015-df-cmp-abba-ph-decode-b06-a1 5135406fa3ba08b4df498cfbe12a463607a829db546a13d273e7b97fdb1aab50 docs/process_traces/2026-08-07-plan-factory/DRAFT-NEVERZERO.md
witness included complete /Users/edr/code/JouleWise/runs_window_c_20260726/p2015-df-cmp-abba-ph-decode-b06-a2 b65b79bb3f7d7a6c570d882abc6b75bef14c1c56223bfb062f6b40c708a4ad8e df-ph-decode-floor-mint1.json
witness listed complete /Users/edr/code/JouleWise/runs_window_c_20260726/p2015-df-cmp-abba-ph-decode-b06-a2 b65b79bb3f7d7a6c570d882abc6b75bef14c1c56223bfb062f6b40c708a4ad8e docs/legacy/strategy/2026-08-07-paper-portfolio/proposals/prop-param-scaling-energy.md
witness listed complete /Users/edr/code/JouleWise/runs_window_c_20260726/p2015-df-cmp-abba-ph-decode-b06-a2 b65b79bb3f7d7a6c570d882abc6b75bef14c1c56223bfb062f6b40c708a4ad8e docs/process_traces/2026-08-07-plan-factory/DRAFT-NEVERZERO.md
witness included complete /Users/edr/code/JouleWise/runs_window_c_20260726/p2015-df-cmp-abba-ph-decode-b06-b1 edbaba1c823c33bbc51164f96947a590ab0f4d96569ca221669942500d4ff2cc df-ph-decode-floor-mint1.json
witness listed complete /Users/edr/code/JouleWise/runs_window_c_20260726/p2015-df-cmp-abba-ph-decode-b06-b1 edbaba1c823c33bbc51164f96947a590ab0f4d96569ca221669942500d4ff2cc docs/legacy/strategy/2026-08-07-paper-portfolio/proposals/prop-param-scaling-energy.md
witness listed complete /Users/edr/code/JouleWise/runs_window_c_20260726/p2015-df-cmp-abba-ph-decode-b06-b1 edbaba1c823c33bbc51164f96947a590ab0f4d96569ca221669942500d4ff2cc docs/process_traces/2026-08-07-plan-factory/DRAFT-NEVERZERO.md
witness included complete /Users/edr/code/JouleWise/runs_window_c_20260726/p2015-df-cmp-abba-ph-decode-b06-b2 e7ee36928bac0e65b8004f8f7b7fae0babe3ac706171b26b8dd92015a1f87058 df-ph-decode-floor-mint1.json
witness listed complete /Users/edr/code/JouleWise/runs_window_c_20260726/p2015-df-cmp-abba-ph-decode-b06-b2 e7ee36928bac0e65b8004f8f7b7fae0babe3ac706171b26b8dd92015a1f87058 docs/process_traces/2026-08-07-plan-factory/DRAFT-NEVERZERO.md
witness included complete /Users/edr/code/JouleWise/runs_window_c_20260726/p2015-df-cmp-abba-ph-decode-b07-a1 32c53e61cdbb8f507eed269af1eeeef69f4105fba8c9d9d2f43f06f8ba9acaf9 df-ph-decode-floor-mint1.json
witness listed complete /Users/edr/code/JouleWise/runs_window_c_20260726/p2015-df-cmp-abba-ph-decode-b07-a1 32c53e61cdbb8f507eed269af1eeeef69f4105fba8c9d9d2f43f06f8ba9acaf9 docs/process_traces/2026-08-07-plan-factory/DRAFT-NEVERZERO.md
witness included complete /Users/edr/code/JouleWise/runs_window_c_20260726/p2015-df-cmp-abba-ph-decode-b07-a2 e339de0c0f2e5b464e73e2423e94ad6a4fa72c2abca68cebeb2d97f3af893109 df-ph-decode-floor-mint1.json
witness listed complete /Users/edr/code/JouleWise/runs_window_c_20260726/p2015-df-cmp-abba-ph-decode-b07-a2 e339de0c0f2e5b464e73e2423e94ad6a4fa72c2abca68cebeb2d97f3af893109 docs/process_traces/2026-08-07-plan-factory/DRAFT-NEVERZERO.md
witness included complete /Users/edr/code/JouleWise/runs_window_c_20260726/p2015-df-cmp-abba-ph-decode-b07-b1 cac899e4c3fa84eec27f5fc26e0c105f25abc6948190821552f3a89f317fd681 df-ph-decode-floor-mint1.json
witness listed complete /Users/edr/code/JouleWise/runs_window_c_20260726/p2015-df-cmp-abba-ph-decode-b07-b1 cac899e4c3fa84eec27f5fc26e0c105f25abc6948190821552f3a89f317fd681 docs/process_traces/2026-08-07-plan-factory/DRAFT-NEVERZERO.md
witness included complete /Users/edr/code/JouleWise/runs_window_c_20260726/p2015-df-cmp-abba-ph-decode-b07-b2 ed743899e603951287cce29814371c4949b452a36b65550992535a3e3ffeef3e df-ph-decode-floor-mint1.json
witness listed complete /Users/edr/code/JouleWise/runs_window_c_20260726/p2015-df-cmp-abba-ph-decode-b07-b2 ed743899e603951287cce29814371c4949b452a36b65550992535a3e3ffeef3e docs/process_traces/2026-08-07-plan-factory/DRAFT-NEVERZERO.md
witness included complete /Users/edr/code/JouleWise/runs_window_c_20260726/p2015-df-cmp-abba-ph-decode-b08-a1 0a76e5fbcffdccb44ebc22b8d9d86e259b49d2c529ec89bcc0a24c6f22994899 df-ph-decode-floor-mint1.json
witness listed complete /Users/edr/code/JouleWise/runs_window_c_20260726/p2015-df-cmp-abba-ph-decode-b08-a1 0a76e5fbcffdccb44ebc22b8d9d86e259b49d2c529ec89bcc0a24c6f22994899 docs/process_traces/2026-08-07-plan-factory/DRAFT-NEVERZERO.md
witness included complete /Users/edr/code/JouleWise/runs_window_c_20260726/p2015-df-cmp-abba-ph-decode-b08-a2 fb12d40f5a418462a268587fa9ad8e9bbbef5e32e47132f112e2f3f9d540c5e1 df-ph-decode-floor-mint1.json
witness listed complete /Users/edr/code/JouleWise/runs_window_c_20260726/p2015-df-cmp-abba-ph-decode-b08-a2 fb12d40f5a418462a268587fa9ad8e9bbbef5e32e47132f112e2f3f9d540c5e1 docs/process_traces/2026-08-07-plan-factory/DRAFT-NEVERZERO.md
witness included complete /Users/edr/code/JouleWise/runs_window_c_20260726/p2015-df-cmp-abba-ph-decode-b08-b1 589b17f6a10c6275407367f7f90bea8ced63dabb70850798e0808626924168fe df-ph-decode-floor-mint1.json
witness listed complete /Users/edr/code/JouleWise/runs_window_c_20260726/p2015-df-cmp-abba-ph-decode-b08-b1 589b17f6a10c6275407367f7f90bea8ced63dabb70850798e0808626924168fe docs/process_traces/2026-08-07-plan-factory/DRAFT-NEVERZERO.md
witness included complete /Users/edr/code/JouleWise/runs_window_c_20260726/p2015-df-cmp-abba-ph-decode-b08-b2 6a090490fd08e646bc39c4eaa112fffcdf87e0d5f03599af10595512957997f4 df-ph-decode-floor-mint1.json
witness listed complete /Users/edr/code/JouleWise/runs_window_c_20260726/p2015-df-cmp-abba-ph-decode-b08-b2 6a090490fd08e646bc39c4eaa112fffcdf87e0d5f03599af10595512957997f4 docs/process_traces/2026-08-07-plan-factory/DRAFT-NEVERZERO.md
witness included complete /Users/edr/code/JouleWise/runs_window_c_20260726/p2015-df-cmp-abba-ph-decode-b09-a1 377f6a786c341eef39d6836cb2d12921ab4a05d434c5a241f5c581d8f4d4a2ee df-ph-decode-floor-mint1.json
witness listed complete /Users/edr/code/JouleWise/runs_window_c_20260726/p2015-df-cmp-abba-ph-decode-b09-a1 377f6a786c341eef39d6836cb2d12921ab4a05d434c5a241f5c581d8f4d4a2ee docs/process_traces/2026-08-07-plan-factory/DRAFT-NEVERZERO.md
witness included complete /Users/edr/code/JouleWise/runs_window_c_20260726/p2015-df-cmp-abba-ph-decode-b09-a2 dc1e56aa1d27fc6ac0bb5d7a80b7881e635a5050e7ffc9536b62c75dd22cee5a df-ph-decode-floor-mint1.json
witness listed complete /Users/edr/code/JouleWise/runs_window_c_20260726/p2015-df-cmp-abba-ph-decode-b09-a2 dc1e56aa1d27fc6ac0bb5d7a80b7881e635a5050e7ffc9536b62c75dd22cee5a docs/process_traces/2026-08-07-plan-factory/DRAFT-NEVERZERO.md
witness included complete /Users/edr/code/JouleWise/runs_window_c_20260726/p2015-df-cmp-abba-ph-decode-b09-b1 acd77e1d5a8a5bc82493315b772fa616a3cf5c579fda5586e04902fdda388459 df-ph-decode-floor-mint1.json
witness listed complete /Users/edr/code/JouleWise/runs_window_c_20260726/p2015-df-cmp-abba-ph-decode-b09-b1 acd77e1d5a8a5bc82493315b772fa616a3cf5c579fda5586e04902fdda388459 docs/process_traces/2026-08-07-plan-factory/DRAFT-NEVERZERO.md
witness included complete /Users/edr/code/JouleWise/runs_window_c_20260726/p2015-df-cmp-abba-ph-decode-b09-b2 8bc66888f356e9e123d356db3dd1f538e71dada51037f953b8f3055e901447f4 df-ph-decode-floor-mint1.json
witness listed complete /Users/edr/code/JouleWise/runs_window_c_20260726/p2015-df-cmp-abba-ph-decode-b09-b2 8bc66888f356e9e123d356db3dd1f538e71dada51037f953b8f3055e901447f4 docs/legacy/strategy/2026-08-07-paper-portfolio/proposals/prop-param-scaling-energy.md
witness listed complete /Users/edr/code/JouleWise/runs_window_c_20260726/p2015-df-cmp-abba-ph-decode-b09-b2 8bc66888f356e9e123d356db3dd1f538e71dada51037f953b8f3055e901447f4 docs/process_traces/2026-08-07-plan-factory/DRAFT-NEVERZERO.md
witness included complete /Users/edr/code/JouleWise/runs_window_c_20260726/p2015-df-cmp-abba-ph-decode-b10-a1 6cdd0c795befd568798a4ef4538bf6db1ccd930f240de873a77ab36263927561 df-ph-decode-floor-mint1.json
witness listed complete /Users/edr/code/JouleWise/runs_window_c_20260726/p2015-df-cmp-abba-ph-decode-b10-a1 6cdd0c795befd568798a4ef4538bf6db1ccd930f240de873a77ab36263927561 docs/process_traces/2026-08-07-plan-factory/DRAFT-NEVERZERO.md
witness included complete /Users/edr/code/JouleWise/runs_window_c_20260726/p2015-df-cmp-abba-ph-decode-b10-a2 ffacb0680cf37794804f7af1f5e0bd39fab26160bf134a0cf63525c293155f13 df-ph-decode-floor-mint1.json
witness listed complete /Users/edr/code/JouleWise/runs_window_c_20260726/p2015-df-cmp-abba-ph-decode-b10-a2 ffacb0680cf37794804f7af1f5e0bd39fab26160bf134a0cf63525c293155f13 docs/process_traces/2026-08-07-plan-factory/DRAFT-NEVERZERO.md
witness included complete /Users/edr/code/JouleWise/runs_window_c_20260726/p2015-df-cmp-abba-ph-decode-b10-b1 b446e7a59d38287578918f273a1fa512f89f8da1ca4e8304f1f83d7af27dc568 df-ph-decode-floor-mint1.json
witness listed complete /Users/edr/code/JouleWise/runs_window_c_20260726/p2015-df-cmp-abba-ph-decode-b10-b1 b446e7a59d38287578918f273a1fa512f89f8da1ca4e8304f1f83d7af27dc568 docs/process_traces/2026-08-07-plan-factory/DRAFT-NEVERZERO.md
witness included complete /Users/edr/code/JouleWise/runs_window_c_20260726/p2015-df-cmp-abba-ph-decode-b10-b2 d88ffadb420cf59aa20a7efc7615a1d7817f91814b0754756b0bc65e51cd57bf df-ph-decode-floor-mint1.json
witness listed complete /Users/edr/code/JouleWise/runs_window_c_20260726/p2015-df-cmp-abba-ph-decode-b10-b2 d88ffadb420cf59aa20a7efc7615a1d7817f91814b0754756b0bc65e51cd57bf docs/legacy/strategy/2026-08-07-paper-portfolio/proposals/prop-param-scaling-energy.md
witness listed complete /Users/edr/code/JouleWise/runs_window_c_20260726/p2015-df-cmp-abba-ph-decode-b10-b2 d88ffadb420cf59aa20a7efc7615a1d7817f91814b0754756b0bc65e51cd57bf docs/process_traces/2026-08-07-plan-factory/DRAFT-NEVERZERO.md
witness_count included complete df-ph-decode-floor-mint1.json 50
witness_count listed complete docs/legacy/strategy/2026-08-07-paper-portfolio/proposals/prop-param-scaling-energy.md 12
witness_count listed complete docs/process_traces/2026-08-07-plan-factory/DRAFT-NEVERZERO.md 51
witness_count listed complete docs/process_traces/2026-08-08-attribution-debate/COMMONMODE-REPLAY.md 40
witness_count listed tree analysis/rpt001-v2/artifact_manifest.json 6
witness_count included tree analysis/rpt001-v2/input_manifest.json 6
witness_count listed tree docs/legacy/strategy/2026-08-07-paper-portfolio/proposals/prop-moe-routing-energy.md 3
witness_count listed tree docs/legacy/strategy/2026-08-07-paper-portfolio/proposals/prop-param-scaling-energy.md 3
witness_count listed tree docs/process_traces/2026-08-07-plan-factory/DRAFT-QUANT_GATES.md 6
```

### stderr (verbatim)

```text
unparseable docs/legacy/process_traces/2026-08-06-d079-issuance-coldgate/ISSUANCE-execute-summary.json: JSONDecodeError
unparseable docs/process_traces/2026-09-16-activation-9853dd2b/77-arm-evidence-n1-20260917/arm-census-final.json: JSONDecodeError
unparseable docs/process_traces/2026-09-16-activation-9853dd2b/77-arm-evidence-n1-20260917/arm-census-staging.json: JSONDecodeError
unparseable docs/process_traces/2026-09-18-activation-d8ca3a36/08-adhoc-corecording-state-3seats-2claude.sampler.jsonl: JSONDecodeError
unparseable docs/process_traces/2026-09-18-activation-d8ca3a36/21-arm-evidence-n1-20260919/arm-census-1.json: JSONDecodeError
unparseable docs/process_traces/2026-09-18-activation-d8ca3a36/21-arm-evidence-n1-20260919/arm-census-2.json: JSONDecodeError
unparseable docs/process_traces/2026-09-18-activation-d8ca3a36/21-arm-evidence-n1-20260919/arm-census-final.json: JSONDecodeError
unparseable docs/process_traces/2026-09-19-activation-4ca26e9c/01-arm-evidence-n2-20260919/arm-census-1.json: JSONDecodeError
unparseable docs/process_traces/2026-09-19-activation-4ca26e9c/01-arm-evidence-n2-20260919/arm-census-2.json: JSONDecodeError
unparseable docs/process_traces/2026-09-19-activation-4ca26e9c/01-arm-evidence-n2-20260919/arm-census-final.json: JSONDecodeError
unparseable docs/process_traces/2026-09-19-activation-a743be05/03-arm-evidence-qpe01-pilot-n1-20260920/arm-census-1.json: JSONDecodeError
unparseable docs/process_traces/2026-09-19-activation-a743be05/03-arm-evidence-qpe01-pilot-n1-20260920/arm-census-2.json: JSONDecodeError
unparseable docs/process_traces/2026-09-19-activation-a743be05/03-arm-evidence-qpe01-pilot-n1-20260920/arm-census-final.json: JSONDecodeError
unparseable docs/process_traces/2026-09-24-activation-278ebc9e/104-forger-fable/adjudication.jsonl: JSONDecodeError
unparseable docs/process_traces/2026-09-24-activation-278ebc9e/104-forger-fable/replay-check.jsonl: JSONDecodeError
unparseable docs/process_traces/2026-09-24-activation-278ebc9e/105-coldgate-packet-a291-forger2/ex-104-fc-adjudication.jsonl: JSONDecodeError
unparseable docs/process_traces/2026-09-24-activation-278ebc9e/106-forger-fable-b/adjudication.jsonl: JSONDecodeError
unparseable docs/process_traces/2026-09-24-activation-278ebc9e/112-coldgate-packet-a291-premerge/ex-104-fc-adjudication.jsonl: JSONDecodeError
unparseable docs/process_traces/2026-09-24-activation-278ebc9e/112-coldgate-packet-a291-premerge/ex-106-fb-adjudication.jsonl: JSONDecodeError
unparseable docs/process_traces/2026-09-24-activation-278ebc9e/117-coldgate-packet-a291-finalpass/ex-104-fc-adjudication.jsonl: JSONDecodeError
unparseable docs/process_traces/2026-09-24-activation-278ebc9e/117-coldgate-packet-a291-finalpass/ex-104-fc-replay.jsonl: JSONDecodeError
unparseable docs/process_traces/2026-09-24-activation-278ebc9e/117-coldgate-packet-a291-finalpass/ex-106-fb-adjudication-and-replay.jsonl: JSONDecodeError
listed analysis/rpt001-v1/artifact_manifest.json bundle_tree_sha256 tree_legacy 1ffe1ec76e3022bac5bd651b261a044d0865a1d5877c165aa45f96018ff0e1ca: retired tree fold
listed analysis/rpt001-v1/artifact_manifest.json bundle_tree_sha256 tree_legacy 36d3b109ac3a2e88b27434361ccb5b85c84d653b4cb7fabf25b3e222506f57ef: retired tree fold
listed analysis/rpt001-v1/artifact_manifest.json bundle_tree_sha256 tree_legacy 9be1c5df4bb566fbe057735bac5377d6826828f0061f11fee2b48cd74f982ff4: retired tree fold
listed analysis/rpt001-v1/artifact_manifest.json bundle_tree_sha256 tree_legacy b029e14b53a085f74653857a62194ed50a47d63e4bc49d15238ec77ff94cc2b5: retired tree fold
listed analysis/rpt001-v1/artifact_manifest.json bundle_tree_sha256 tree_legacy ec05d3d2c2bd262cb3488c887e4a561ef6c70d6271058f3fb0c0e823e38699cc: retired tree fold
listed analysis/rpt001-v1/artifact_manifest.json bundle_tree_sha256 tree_legacy f9f5896c8edf8b8dc1fd56dee977f5a5b7b4d5a04cc76b1405c865d817f9e279: retired tree fold
listed analysis/rpt001-v1/input_manifest.json bundle_tree_sha256 tree_legacy 1ffe1ec76e3022bac5bd651b261a044d0865a1d5877c165aa45f96018ff0e1ca: retired tree fold
listed analysis/rpt001-v1/input_manifest.json bundle_tree_sha256 tree_legacy 36d3b109ac3a2e88b27434361ccb5b85c84d653b4cb7fabf25b3e222506f57ef: retired tree fold
listed analysis/rpt001-v1/input_manifest.json bundle_tree_sha256 tree_legacy 9be1c5df4bb566fbe057735bac5377d6826828f0061f11fee2b48cd74f982ff4: retired tree fold
listed analysis/rpt001-v1/input_manifest.json bundle_tree_sha256 tree_legacy b029e14b53a085f74653857a62194ed50a47d63e4bc49d15238ec77ff94cc2b5: retired tree fold
listed analysis/rpt001-v1/input_manifest.json bundle_tree_sha256 tree_legacy ec05d3d2c2bd262cb3488c887e4a561ef6c70d6271058f3fb0c0e823e38699cc: retired tree fold
listed analysis/rpt001-v1/input_manifest.json bundle_tree_sha256 tree_legacy f9f5896c8edf8b8dc1fd56dee977f5a5b7b4d5a04cc76b1405c865d817f9e279: retired tree fold
listed analysis/rpt001-v2/artifact_manifest.json bundle_tree_sha256 tree_nul_v1 2888c9d205df62e1136a376997ea8a6947683e4311eedaee20e3135bd559e213: source not named by amendment 40
listed analysis/rpt001-v2/artifact_manifest.json bundle_tree_sha256 tree_nul_v1 5ec71ed301ba9c0a48b137b5bdce00b8893c62d4f1397f55aac3c1943ccc9180: source not named by amendment 40
listed analysis/rpt001-v2/artifact_manifest.json bundle_tree_sha256 tree_nul_v1 8a99d7a851c55e53631df6f910d17ee097cbf8bd19f33d44bcef911a6502e82f: source not named by amendment 40
listed analysis/rpt001-v2/artifact_manifest.json bundle_tree_sha256 tree_nul_v1 9376dbc16848e03d3bd54e4fac5598b34e1391d376ef11db527ac1fe25f08773: source not named by amendment 40
listed analysis/rpt001-v2/artifact_manifest.json bundle_tree_sha256 tree_nul_v1 9f162f058bfceb949f34e0c24042c83e8d7f353f97d87b4cf6e0e6dff0912398: source not named by amendment 40
listed analysis/rpt001-v2/artifact_manifest.json bundle_tree_sha256 tree_nul_v1 c72cdc34ef3ce9ccfb0a015bed5ace8e4efa7d18f457ac5cd8a0c894acc21268: source not named by amendment 40
listed df-ph-decode-floor-mint1.json bundle_sha256s complete 0a22a02caa28f0c75bc460339dd420604638cf5f7aa17a0ca2e4fd1c8afbb9ae: duplicate of included citation
listed df-ph-decode-floor-mint1.json bundle_sha256s complete 0a76e5fbcffdccb44ebc22b8d9d86e259b49d2c529ec89bcc0a24c6f22994899: duplicate of included citation
listed df-ph-decode-floor-mint1.json bundle_sha256s complete 0eb6a006b4afc1cc031a3786a0cc1180686cdb78cb9375788370a3bfd86e8060: duplicate of included citation
listed df-ph-decode-floor-mint1.json bundle_sha256s complete 153af6c4d94ba5f9e67f23cf4151703b27d430717dc3d9b773258f7ffdd40593: duplicate of included citation
listed df-ph-decode-floor-mint1.json bundle_sha256s complete 1624fc548379c427d047187df164fa297bec2080062f28bb809a2dba80c94a00: duplicate of included citation
listed df-ph-decode-floor-mint1.json bundle_sha256s complete 195b495930c4cdd532cfdd4773260ba3de73e585c7a3a9e55bac179e3b984195: duplicate of included citation
listed df-ph-decode-floor-mint1.json bundle_sha256s complete 1a7a291dd1b789f95faf8c873a459fd4d8bb6b26257f8866726151f6c156cb96: duplicate of included citation
listed df-ph-decode-floor-mint1.json bundle_sha256s complete 2863fa61af00fb8e23c68bd6848c9eb7f630d21827aefa4ba9af9b09a05537c9: duplicate of included citation
listed df-ph-decode-floor-mint1.json bundle_sha256s complete 2d1c88636ad93b0727cb01d8d4c70253fc5318ce3033b9d11e2bc0e4d8a68733: duplicate of included citation
listed df-ph-decode-floor-mint1.json bundle_sha256s complete 2ecceeb9237077c2f3a6577c9d7bce24d3deeb926df1e15f1b389bad0db02147: duplicate of included citation
listed df-ph-decode-floor-mint1.json bundle_sha256s complete 32c53e61cdbb8f507eed269af1eeeef69f4105fba8c9d9d2f43f06f8ba9acaf9: duplicate of included citation
listed df-ph-decode-floor-mint1.json bundle_sha256s complete 377f6a786c341eef39d6836cb2d12921ab4a05d434c5a241f5c581d8f4d4a2ee: duplicate of included citation
listed df-ph-decode-floor-mint1.json bundle_sha256s complete 39054c62e30e8362a0ef473fb674aed5d1c87df7c630d0f4daadfd296874439e: duplicate of included citation
listed df-ph-decode-floor-mint1.json bundle_sha256s complete 48a8bb2a6f23c6531eae6f8d99c043e0500379aff9427956fee1b74de75694ff: duplicate of included citation
listed df-ph-decode-floor-mint1.json bundle_sha256s complete 5135406fa3ba08b4df498cfbe12a463607a829db546a13d273e7b97fdb1aab50: duplicate of included citation
listed df-ph-decode-floor-mint1.json bundle_sha256s complete 584b8d1b73e7f5a5d8fe4b1e6b0f5e3a6382bb84a57c5cd6015eda31a26c31e5: duplicate of included citation
listed df-ph-decode-floor-mint1.json bundle_sha256s complete 589b17f6a10c6275407367f7f90bea8ced63dabb70850798e0808626924168fe: duplicate of included citation
listed df-ph-decode-floor-mint1.json bundle_sha256s complete 59aade4961b9e59f1696f88f263204f3739cb7d81adc754cc3380a0133f92691: duplicate of included citation
listed df-ph-decode-floor-mint1.json bundle_sha256s complete 5c7a8a6ce946d88fdd5ea0124bafa1ffad8c289308d5e9b600d2f95e280bb025: duplicate of included citation
listed df-ph-decode-floor-mint1.json bundle_sha256s complete 6a090490fd08e646bc39c4eaa112fffcdf87e0d5f03599af10595512957997f4: duplicate of included citation
listed df-ph-decode-floor-mint1.json bundle_sha256s complete 6cdd0c795befd568798a4ef4538bf6db1ccd930f240de873a77ab36263927561: duplicate of included citation
listed df-ph-decode-floor-mint1.json bundle_sha256s complete 769d1d1378e3603fe40013fadeda35504eca0c235f773106233323fba5a61163: duplicate of included citation
listed df-ph-decode-floor-mint1.json bundle_sha256s complete 8a9216a68466a432fe65e7ff9d48664d1c1e8b297b9a011cbe4f462e291220b4: duplicate of included citation
listed df-ph-decode-floor-mint1.json bundle_sha256s complete 8bc66888f356e9e123d356db3dd1f538e71dada51037f953b8f3055e901447f4: duplicate of included citation
listed df-ph-decode-floor-mint1.json bundle_sha256s complete 8eaba1d3b0069dd913aafabff74f6d2b6dfab066a0b30e8f4f68322a84973903: duplicate of included citation
listed df-ph-decode-floor-mint1.json bundle_sha256s complete 9d67992e7cdd70a86bbbf82ca6a9b587d42779c14a28f72256900331d9f8fece: duplicate of included citation
listed df-ph-decode-floor-mint1.json bundle_sha256s complete a71d5519ecbf8a1659cbdca66d0d80b34e0350a9746ef5637e84e76771e5eea3: duplicate of included citation
listed df-ph-decode-floor-mint1.json bundle_sha256s complete acd77e1d5a8a5bc82493315b772fa616a3cf5c579fda5586e04902fdda388459: duplicate of included citation
listed df-ph-decode-floor-mint1.json bundle_sha256s complete b200324cffed9a1db87323a5961d28dbdc593e743d623423b6862e5f643f5273: duplicate of included citation
listed df-ph-decode-floor-mint1.json bundle_sha256s complete b25522da721b5a7deb6060fa1ed4ce22c174bcefa6d47617a76bfb90b23f4755: duplicate of included citation
listed df-ph-decode-floor-mint1.json bundle_sha256s complete b27c6af7109a5734079ad311df84f812680daa957e2b5121de46372fe6871bf3: duplicate of included citation
listed df-ph-decode-floor-mint1.json bundle_sha256s complete b2b10d7dc7c70820ffa7be4cd6e5c7d99bfb723c24ecc8aa143b92b28a18cca2: duplicate of included citation
listed df-ph-decode-floor-mint1.json bundle_sha256s complete b446e7a59d38287578918f273a1fa512f89f8da1ca4e8304f1f83d7af27dc568: duplicate of included citation
listed df-ph-decode-floor-mint1.json bundle_sha256s complete b65b79bb3f7d7a6c570d882abc6b75bef14c1c56223bfb062f6b40c708a4ad8e: duplicate of included citation
listed df-ph-decode-floor-mint1.json bundle_sha256s complete c285172881235ef1ed0e29731c412706604e8cd182182981a5ed44cc2df986bf: duplicate of included citation
listed df-ph-decode-floor-mint1.json bundle_sha256s complete cac899e4c3fa84eec27f5fc26e0c105f25abc6948190821552f3a89f317fd681: duplicate of included citation
listed df-ph-decode-floor-mint1.json bundle_sha256s complete d88ffadb420cf59aa20a7efc7615a1d7817f91814b0754756b0bc65e51cd57bf: duplicate of included citation
listed df-ph-decode-floor-mint1.json bundle_sha256s complete dc1e56aa1d27fc6ac0bb5d7a80b7881e635a5050e7ffc9536b62c75dd22cee5a: duplicate of included citation
listed df-ph-decode-floor-mint1.json bundle_sha256s complete e339de0c0f2e5b464e73e2423e94ad6a4fa72c2abca68cebeb2d97f3af893109: duplicate of included citation
listed df-ph-decode-floor-mint1.json bundle_sha256s complete e35798402f4af613c21e7bd5069875a4194b6672c3c3ab1c3073fff3ec05b17d: duplicate of included citation
listed df-ph-decode-floor-mint1.json bundle_sha256s complete e7ee36928bac0e65b8004f8f7b7fae0babe3ac706171b26b8dd92015a1f87058: duplicate of included citation
listed df-ph-decode-floor-mint1.json bundle_sha256s complete eb05f32d37b1c8e8969f097a0ff112ea95e7ca9c1110e03127b7538267414449: duplicate of included citation
listed df-ph-decode-floor-mint1.json bundle_sha256s complete ec172522b7ba17c83008f32994e0c727cad2bc857aee4b6a18b4c6ac4ed14446: duplicate of included citation
listed df-ph-decode-floor-mint1.json bundle_sha256s complete ec6fda56898612837eb76d658c9057ab0e08e26689e44b1dea1a296dd17674b2: duplicate of included citation
listed df-ph-decode-floor-mint1.json bundle_sha256s complete ed743899e603951287cce29814371c4949b452a36b65550992535a3e3ffeef3e: duplicate of included citation
listed df-ph-decode-floor-mint1.json bundle_sha256s complete edbaba1c823c33bbc51164f96947a590ab0f4d96569ca221669942500d4ff2cc: duplicate of included citation
listed df-ph-decode-floor-mint1.json bundle_sha256s complete f29039135ac92d31ea88c277682ff79aae0474ac741c2a18d2a1930f71be620b: duplicate of included citation
listed df-ph-decode-floor-mint1.json bundle_sha256s complete f39fcdfe56370dc2ed33f53c6901ebcfda3362193f5f0f865d8b366c0a3eb80d: duplicate of included citation
listed df-ph-decode-floor-mint1.json bundle_sha256s complete fb12d40f5a418462a268587fa9ad8e9bbbef5e32e47132f112e2f3f9d540c5e1: duplicate of included citation
listed df-ph-decode-floor-mint1.json bundle_sha256s complete ffacb0680cf37794804f7af1f5e0bd39fab26160bf134a0cf63525c293155f13: duplicate of included citation
listed docs/legacy/strategy/2026-08-07-paper-portfolio/proposals/prop-param-scaling-energy.md bundle_sha256 complete 0eb6a006b4afc1cc031a3786a0cc1180686cdb78cb9375788370a3bfd86e8060: source not named by amendment 40
listed docs/legacy/strategy/2026-08-07-paper-portfolio/proposals/prop-param-scaling-energy.md bundle_sha256 complete 153af6c4d94ba5f9e67f23cf4151703b27d430717dc3d9b773258f7ffdd40593: source not named by amendment 40
listed docs/legacy/strategy/2026-08-07-paper-portfolio/proposals/prop-param-scaling-energy.md bundle_sha256 complete 195b495930c4cdd532cfdd4773260ba3de73e585c7a3a9e55bac179e3b984195: source not named by amendment 40
listed docs/legacy/strategy/2026-08-07-paper-portfolio/proposals/prop-param-scaling-energy.md bundle_sha256 complete 2d1c88636ad93b0727cb01d8d4c70253fc5318ce3033b9d11e2bc0e4d8a68733: source not named by amendment 40
listed docs/legacy/strategy/2026-08-07-paper-portfolio/proposals/prop-param-scaling-energy.md bundle_sha256 complete 5135406fa3ba08b4df498cfbe12a463607a829db546a13d273e7b97fdb1aab50: source not named by amendment 40
listed docs/legacy/strategy/2026-08-07-paper-portfolio/proposals/prop-param-scaling-energy.md bundle_sha256 complete 8bc66888f356e9e123d356db3dd1f538e71dada51037f953b8f3055e901447f4: source not named by amendment 40
listed docs/legacy/strategy/2026-08-07-paper-portfolio/proposals/prop-param-scaling-energy.md bundle_sha256 complete 8eaba1d3b0069dd913aafabff74f6d2b6dfab066a0b30e8f4f68322a84973903: source not named by amendment 40
listed docs/legacy/strategy/2026-08-07-paper-portfolio/proposals/prop-param-scaling-energy.md bundle_sha256 complete b200324cffed9a1db87323a5961d28dbdc593e743d623423b6862e5f643f5273: source not named by amendment 40
listed docs/legacy/strategy/2026-08-07-paper-portfolio/proposals/prop-param-scaling-energy.md bundle_sha256 complete b2b10d7dc7c70820ffa7be4cd6e5c7d99bfb723c24ecc8aa143b92b28a18cca2: source not named by amendment 40
listed docs/legacy/strategy/2026-08-07-paper-portfolio/proposals/prop-param-scaling-energy.md bundle_sha256 complete b65b79bb3f7d7a6c570d882abc6b75bef14c1c56223bfb062f6b40c708a4ad8e: source not named by amendment 40
listed docs/legacy/strategy/2026-08-07-paper-portfolio/proposals/prop-param-scaling-energy.md bundle_sha256 complete d88ffadb420cf59aa20a7efc7615a1d7817f91814b0754756b0bc65e51cd57bf: source not named by amendment 40
listed docs/legacy/strategy/2026-08-07-paper-portfolio/proposals/prop-param-scaling-energy.md bundle_sha256 complete edbaba1c823c33bbc51164f96947a590ab0f4d96569ca221669942500d4ff2cc: source not named by amendment 40
listed docs/process_traces/2026-08-07-plan-factory/DRAFT-NEVERZERO.md bundle_sha256 complete 0a22a02caa28f0c75bc460339dd420604638cf5f7aa17a0ca2e4fd1c8afbb9ae: source not named by amendment 40
listed docs/process_traces/2026-08-07-plan-factory/DRAFT-NEVERZERO.md bundle_sha256 complete 0a22a02caa28f0c75bc460339dd420604638cf5f7aa17a0ca2e4fd1c8afbb9ae: source not named by amendment 40
listed docs/process_traces/2026-08-07-plan-factory/DRAFT-NEVERZERO.md bundle_sha256 complete 0eb6a006b4afc1cc031a3786a0cc1180686cdb78cb9375788370a3bfd86e8060: source not named by amendment 40
listed docs/process_traces/2026-08-07-plan-factory/DRAFT-NEVERZERO.md bundle_sha256 complete 153af6c4d94ba5f9e67f23cf4151703b27d430717dc3d9b773258f7ffdd40593: source not named by amendment 40
listed docs/process_traces/2026-08-07-plan-factory/DRAFT-NEVERZERO.md bundle_sha256 complete 153af6c4d94ba5f9e67f23cf4151703b27d430717dc3d9b773258f7ffdd40593: source not named by amendment 40
listed docs/process_traces/2026-08-07-plan-factory/DRAFT-NEVERZERO.md bundle_sha256 complete 1624fc548379c427d047187df164fa297bec2080062f28bb809a2dba80c94a00: source not named by amendment 40
listed docs/process_traces/2026-08-07-plan-factory/DRAFT-NEVERZERO.md bundle_sha256 complete 195b495930c4cdd532cfdd4773260ba3de73e585c7a3a9e55bac179e3b984195: source not named by amendment 40
listed docs/process_traces/2026-08-07-plan-factory/DRAFT-NEVERZERO.md bundle_sha256 complete 195b495930c4cdd532cfdd4773260ba3de73e585c7a3a9e55bac179e3b984195: source not named by amendment 40
listed docs/process_traces/2026-08-07-plan-factory/DRAFT-NEVERZERO.md bundle_sha256 complete 1a7a291dd1b789f95faf8c873a459fd4d8bb6b26257f8866726151f6c156cb96: source not named by amendment 40
listed docs/process_traces/2026-08-07-plan-factory/DRAFT-NEVERZERO.md bundle_sha256 complete 2863fa61af00fb8e23c68bd6848c9eb7f630d21827aefa4ba9af9b09a05537c9: source not named by amendment 40
listed docs/process_traces/2026-08-07-plan-factory/DRAFT-NEVERZERO.md bundle_sha256 complete 2d1c88636ad93b0727cb01d8d4c70253fc5318ce3033b9d11e2bc0e4d8a68733: source not named by amendment 40
listed docs/process_traces/2026-08-07-plan-factory/DRAFT-NEVERZERO.md bundle_sha256 complete 2d1c88636ad93b0727cb01d8d4c70253fc5318ce3033b9d11e2bc0e4d8a68733: source not named by amendment 40
listed docs/process_traces/2026-08-07-plan-factory/DRAFT-NEVERZERO.md bundle_sha256 complete 5135406fa3ba08b4df498cfbe12a463607a829db546a13d273e7b97fdb1aab50: source not named by amendment 40
listed docs/process_traces/2026-08-07-plan-factory/DRAFT-NEVERZERO.md bundle_sha256 complete 584b8d1b73e7f5a5d8fe4b1e6b0f5e3a6382bb84a57c5cd6015eda31a26c31e5: source not named by amendment 40
listed docs/process_traces/2026-08-07-plan-factory/DRAFT-NEVERZERO.md bundle_sha256 complete 8a9216a68466a432fe65e7ff9d48664d1c1e8b297b9a011cbe4f462e291220b4: source not named by amendment 40
listed docs/process_traces/2026-08-07-plan-factory/DRAFT-NEVERZERO.md bundle_sha256 complete 8bc66888f356e9e123d356db3dd1f538e71dada51037f953b8f3055e901447f4: source not named by amendment 40
listed docs/process_traces/2026-08-07-plan-factory/DRAFT-NEVERZERO.md bundle_sha256 complete 8eaba1d3b0069dd913aafabff74f6d2b6dfab066a0b30e8f4f68322a84973903: source not named by amendment 40
listed docs/process_traces/2026-08-07-plan-factory/DRAFT-NEVERZERO.md bundle_sha256 complete 9dd33c8f5bb5de530ccb0abff96435abc687d27db7286076415008eacd898c5f: source not named by amendment 40
listed docs/process_traces/2026-08-07-plan-factory/DRAFT-NEVERZERO.md bundle_sha256 complete a71d5519ecbf8a1659cbdca66d0d80b34e0350a9746ef5637e84e76771e5eea3: source not named by amendment 40
listed docs/process_traces/2026-08-07-plan-factory/DRAFT-NEVERZERO.md bundle_sha256 complete b200324cffed9a1db87323a5961d28dbdc593e743d623423b6862e5f643f5273: source not named by amendment 40
listed docs/process_traces/2026-08-07-plan-factory/DRAFT-NEVERZERO.md bundle_sha256 complete b200324cffed9a1db87323a5961d28dbdc593e743d623423b6862e5f643f5273: source not named by amendment 40
listed docs/process_traces/2026-08-07-plan-factory/DRAFT-NEVERZERO.md bundle_sha256 complete b25522da721b5a7deb6060fa1ed4ce22c174bcefa6d47617a76bfb90b23f4755: source not named by amendment 40
listed docs/process_traces/2026-08-07-plan-factory/DRAFT-NEVERZERO.md bundle_sha256 complete b27c6af7109a5734079ad311df84f812680daa957e2b5121de46372fe6871bf3: source not named by amendment 40
listed docs/process_traces/2026-08-07-plan-factory/DRAFT-NEVERZERO.md bundle_sha256 complete b2b10d7dc7c70820ffa7be4cd6e5c7d99bfb723c24ecc8aa143b92b28a18cca2: source not named by amendment 40
listed docs/process_traces/2026-08-07-plan-factory/DRAFT-NEVERZERO.md bundle_sha256 complete b2b10d7dc7c70820ffa7be4cd6e5c7d99bfb723c24ecc8aa143b92b28a18cca2: source not named by amendment 40
listed docs/process_traces/2026-08-07-plan-factory/DRAFT-NEVERZERO.md bundle_sha256 complete b65b79bb3f7d7a6c570d882abc6b75bef14c1c56223bfb062f6b40c708a4ad8e: source not named by amendment 40
listed docs/process_traces/2026-08-07-plan-factory/DRAFT-NEVERZERO.md bundle_sha256 complete c285172881235ef1ed0e29731c412706604e8cd182182981a5ed44cc2df986bf: source not named by amendment 40
listed docs/process_traces/2026-08-07-plan-factory/DRAFT-NEVERZERO.md bundle_sha256 complete d88ffadb420cf59aa20a7efc7615a1d7817f91814b0754756b0bc65e51cd57bf: source not named by amendment 40
listed docs/process_traces/2026-08-07-plan-factory/DRAFT-NEVERZERO.md bundle_sha256 complete e35798402f4af613c21e7bd5069875a4194b6672c3c3ab1c3073fff3ec05b17d: source not named by amendment 40
listed docs/process_traces/2026-08-07-plan-factory/DRAFT-NEVERZERO.md bundle_sha256 complete ec172522b7ba17c83008f32994e0c727cad2bc857aee4b6a18b4c6ac4ed14446: source not named by amendment 40
listed docs/process_traces/2026-08-07-plan-factory/DRAFT-NEVERZERO.md bundle_sha256 complete edbaba1c823c33bbc51164f96947a590ab0f4d96569ca221669942500d4ff2cc: source not named by amendment 40
listed docs/process_traces/2026-08-07-plan-factory/DRAFT-NEVERZERO.md bundle_sha256 complete f29039135ac92d31ea88c277682ff79aae0474ac741c2a18d2a1930f71be620b: source not named by amendment 40
listed docs/process_traces/2026-08-07-plan-factory/DRAFT-NEVERZERO.md bundle_sha256 complete f39fcdfe56370dc2ed33f53c6901ebcfda3362193f5f0f865d8b366c0a3eb80d: source not named by amendment 40
listed docs/process_traces/2026-08-08-attribution-debate/COMMONMODE-REPLAY.md complete_bundle_sha256 complete 708fced0676c05556749712ac3905f36e40ec22218e8d4e67e13938253639607: source not named by amendment 40
listed scripts/issue_dg071_dg075_statistics.py PINNED_BUNDLE_SHA256 file_digest 6945160964bc8667f4bfcc1ba7b500f81045fce8301ef7aadce45a188d3e06e9: file digest, not a bundle
listed tests/goldens/axi_strict_validation_evidence.json validated_bundle_sha256 not_a_bundle cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc: not a bundle
listed tests/goldens/output_identity_output_divergent.patch.json /spec_on_bundle/requests_artifact_sha256 file_digest bef5c2573c7d8c52651924817cecd64b89841b61110cde35c8413d8e475756e8: file digest, not a bundle
listed tests/goldens/output_identity_text_divergent.patch.json /spec_on_bundle/requests_artifact_sha256 file_digest ca6f3736d85f0c152f9f4f9b0a086aeb8ef03eefea659ca7e4a4505b93da93a6: file digest, not a bundle
listed tests/goldens/output_identity_unassessable.patch.json /spec_on_bundle/requests_artifact_sha256 file_digest 3eea19beae8c74a0cc3e6c0cf6c9a289cb51b813a18e8a882503fb913b6337e5: file digest, not a bundle
listed_count analysis/rpt001-v1/artifact_manifest.json bundle_tree_sha256 6
listed_count analysis/rpt001-v1/input_manifest.json bundle_tree_sha256 6
listed_count analysis/rpt001-v2/artifact_manifest.json bundle_tree_sha256 6
listed_count df-ph-decode-floor-mint1.json bundle_sha256s 50
listed_count docs/legacy/strategy/2026-08-07-paper-portfolio/proposals/prop-param-scaling-energy.md bundle_sha256 12
listed_count docs/process_traces/2026-08-07-plan-factory/DRAFT-NEVERZERO.md bundle_sha256 33
listed_count docs/process_traces/2026-08-08-attribution-debate/COMMONMODE-REPLAY.md complete_bundle_sha256 1
listed_count scripts/issue_dg071_dg075_statistics.py PINNED_BUNDLE_SHA256 1
listed_count tests/goldens/axi_strict_validation_evidence.json validated_bundle_sha256 1
listed_count tests/goldens/output_identity_output_divergent.patch.json /spec_on_bundle/requests_artifact_sha256 1
listed_count tests/goldens/output_identity_text_divergent.patch.json /spec_on_bundle/requests_artifact_sha256 1
listed_count tests/goldens/output_identity_unassessable.patch.json /spec_on_bundle/requests_artifact_sha256 1
listed_population paper_results_file_digest bundles=100
listed_population p2015-df-cmp-abba-ph-decode-b01-a1 /Users/edr/code/JouleWise/runs_window_c_20260726 file_digest
listed_population p2015-df-cmp-abba-ph-decode-b01-a2 /Users/edr/code/JouleWise/runs_window_c_20260726 file_digest
listed_population p2015-df-cmp-abba-ph-decode-b01-b1 /Users/edr/code/JouleWise/runs_window_c_20260726 file_digest
listed_population p2015-df-cmp-abba-ph-decode-b01-b2 /Users/edr/code/JouleWise/runs_window_c_20260726 file_digest
listed_population p2015-df-cmp-abba-ph-decode-b02-a1 /Users/edr/code/JouleWise/runs_window_c_20260726 file_digest
listed_population p2015-df-cmp-abba-ph-decode-b02-a2 /Users/edr/code/JouleWise/runs_window_c_20260726 file_digest
listed_population p2015-df-cmp-abba-ph-decode-b02-b1 /Users/edr/code/JouleWise/runs_window_c_20260726 file_digest
listed_population p2015-df-cmp-abba-ph-decode-b02-b2 /Users/edr/code/JouleWise/runs_window_c_20260726 file_digest
listed_population p2015-df-cmp-abba-ph-decode-b03-a1 /Users/edr/code/JouleWise/runs_window_c_20260726 file_digest
listed_population p2015-df-cmp-abba-ph-decode-b03-a2 /Users/edr/code/JouleWise/runs_window_c_20260726 file_digest
listed_population p2015-df-cmp-abba-ph-decode-b03-b1 /Users/edr/code/JouleWise/runs_window_c_20260726 file_digest
listed_population p2015-df-cmp-abba-ph-decode-b03-b2 /Users/edr/code/JouleWise/runs_window_c_20260726 file_digest
listed_population p2015-df-cmp-abba-ph-decode-b04-a1 /Users/edr/code/JouleWise/runs_window_c_20260726 file_digest
listed_population p2015-df-cmp-abba-ph-decode-b04-a2 /Users/edr/code/JouleWise/runs_window_c_20260726 file_digest
listed_population p2015-df-cmp-abba-ph-decode-b04-b1 /Users/edr/code/JouleWise/runs_window_c_20260726 file_digest
listed_population p2015-df-cmp-abba-ph-decode-b04-b2 /Users/edr/code/JouleWise/runs_window_c_20260726 file_digest
listed_population p2015-df-cmp-abba-ph-decode-b05-a1 /Users/edr/code/JouleWise/runs_window_c_20260726 file_digest
listed_population p2015-df-cmp-abba-ph-decode-b05-a2 /Users/edr/code/JouleWise/runs_window_c_20260726 file_digest
listed_population p2015-df-cmp-abba-ph-decode-b05-b1 /Users/edr/code/JouleWise/runs_window_c_20260726 file_digest
listed_population p2015-df-cmp-abba-ph-decode-b05-b2 /Users/edr/code/JouleWise/runs_window_c_20260726 file_digest
listed_population p2015-df-cmp-abba-ph-decode-b06-a1 /Users/edr/code/JouleWise/runs_window_c_20260726 file_digest
listed_population p2015-df-cmp-abba-ph-decode-b06-a2 /Users/edr/code/JouleWise/runs_window_c_20260726 file_digest
listed_population p2015-df-cmp-abba-ph-decode-b06-b1 /Users/edr/code/JouleWise/runs_window_c_20260726 file_digest
listed_population p2015-df-cmp-abba-ph-decode-b06-b2 /Users/edr/code/JouleWise/runs_window_c_20260726 file_digest
listed_population p2015-df-cmp-abba-ph-decode-b07-a1 /Users/edr/code/JouleWise/runs_window_c_20260726 file_digest
listed_population p2015-df-cmp-abba-ph-decode-b07-a2 /Users/edr/code/JouleWise/runs_window_c_20260726 file_digest
listed_population p2015-df-cmp-abba-ph-decode-b07-b1 /Users/edr/code/JouleWise/runs_window_c_20260726 file_digest
listed_population p2015-df-cmp-abba-ph-decode-b07-b2 /Users/edr/code/JouleWise/runs_window_c_20260726 file_digest
listed_population p2015-df-cmp-abba-ph-decode-b08-a1 /Users/edr/code/JouleWise/runs_window_c_20260726 file_digest
listed_population p2015-df-cmp-abba-ph-decode-b08-a2 /Users/edr/code/JouleWise/runs_window_c_20260726 file_digest
listed_population p2015-df-cmp-abba-ph-decode-b08-b1 /Users/edr/code/JouleWise/runs_window_c_20260726 file_digest
listed_population p2015-df-cmp-abba-ph-decode-b08-b2 /Users/edr/code/JouleWise/runs_window_c_20260726 file_digest
listed_population p2015-df-cmp-abba-ph-decode-b09-a1 /Users/edr/code/JouleWise/runs_window_c_20260726 file_digest
listed_population p2015-df-cmp-abba-ph-decode-b09-a2 /Users/edr/code/JouleWise/runs_window_c_20260726 file_digest
listed_population p2015-df-cmp-abba-ph-decode-b09-b1 /Users/edr/code/JouleWise/runs_window_c_20260726 file_digest
listed_population p2015-df-cmp-abba-ph-decode-b09-b2 /Users/edr/code/JouleWise/runs_window_c_20260726 file_digest
listed_population p2015-df-cmp-abba-ph-decode-b10-a1 /Users/edr/code/JouleWise/runs_window_c_20260726 file_digest
listed_population p2015-df-cmp-abba-ph-decode-b10-a2 /Users/edr/code/JouleWise/runs_window_c_20260726 file_digest
listed_population p2015-df-cmp-abba-ph-decode-b10-b1 /Users/edr/code/JouleWise/runs_window_c_20260726 file_digest
listed_population p2015-df-cmp-abba-ph-decode-b10-b2 /Users/edr/code/JouleWise/runs_window_c_20260726 file_digest
listed_population p2015-df-ph-decode-abs-r01 /Users/edr/code/JouleWise/runs_window_a10_20260725 file_digest
listed_population p2015-df-ph-decode-abs-r02 /Users/edr/code/JouleWise/runs_window_a10_20260725 file_digest
listed_population p2015-df-ph-decode-abs-r03 /Users/edr/code/JouleWise/runs_window_a10_20260725 file_digest
listed_population p2015-df-ph-decode-abs-r04 /Users/edr/code/JouleWise/runs_window_a10_20260725 file_digest
listed_population p2015-df-ph-decode-abs-r05 /Users/edr/code/JouleWise/runs_window_a10_20260725 file_digest
listed_population p2015-df-ph-decode-abs-r06 /Users/edr/code/JouleWise/runs_window_a10_20260725 file_digest
listed_population p2015-df-ph-decode-abs-r07 /Users/edr/code/JouleWise/runs_window_a10_20260725 file_digest
listed_population p2015-df-ph-decode-abs-r08 /Users/edr/code/JouleWise/runs_window_a10_20260725 file_digest
listed_population p2015-df-ph-decode-abs-r09 /Users/edr/code/JouleWise/runs_window_a10_20260725 file_digest
listed_population p2015-df-ph-decode-abs-r10 /Users/edr/code/JouleWise/runs_window_a10_20260725 file_digest
listed_population sw7bfloor-df-cmp-abba-ph-decode-b01-a1 /Users/edr/code/JouleWise/runs_window_7bfloor_20260729 file_digest
listed_population sw7bfloor-df-cmp-abba-ph-decode-b01-a2 /Users/edr/code/JouleWise/runs_window_7bfloor_20260729 file_digest
listed_population sw7bfloor-df-cmp-abba-ph-decode-b01-b1 /Users/edr/code/JouleWise/runs_window_7bfloor_20260729 file_digest
listed_population sw7bfloor-df-cmp-abba-ph-decode-b01-b2 /Users/edr/code/JouleWise/runs_window_7bfloor_20260729 file_digest
listed_population sw7bfloor-df-cmp-abba-ph-decode-b02-a1 /Users/edr/code/JouleWise/runs_window_7bfloor_20260729 file_digest
listed_population sw7bfloor-df-cmp-abba-ph-decode-b02-a2 /Users/edr/code/JouleWise/runs_window_7bfloor_20260729 file_digest
listed_population sw7bfloor-df-cmp-abba-ph-decode-b02-b1 /Users/edr/code/JouleWise/runs_window_7bfloor_20260729 file_digest
listed_population sw7bfloor-df-cmp-abba-ph-decode-b02-b2 /Users/edr/code/JouleWise/runs_window_7bfloor_20260729 file_digest
listed_population sw7bfloor-df-cmp-abba-ph-decode-b03-a1 /Users/edr/code/JouleWise/runs_window_7bfloor_20260729 file_digest
listed_population sw7bfloor-df-cmp-abba-ph-decode-b03-a2 /Users/edr/code/JouleWise/runs_window_7bfloor_20260729 file_digest
listed_population sw7bfloor-df-cmp-abba-ph-decode-b03-b1 /Users/edr/code/JouleWise/runs_window_7bfloor_20260729 file_digest
listed_population sw7bfloor-df-cmp-abba-ph-decode-b03-b2 /Users/edr/code/JouleWise/runs_window_7bfloor_20260729 file_digest
listed_population sw7bfloor-df-cmp-abba-ph-decode-b04-a1 /Users/edr/code/JouleWise/runs_window_7bfloor_20260729 file_digest
listed_population sw7bfloor-df-cmp-abba-ph-decode-b04-a2 /Users/edr/code/JouleWise/runs_window_7bfloor_20260729 file_digest
listed_population sw7bfloor-df-cmp-abba-ph-decode-b04-b1 /Users/edr/code/JouleWise/runs_window_7bfloor_20260729 file_digest
listed_population sw7bfloor-df-cmp-abba-ph-decode-b04-b2 /Users/edr/code/JouleWise/runs_window_7bfloor_20260729 file_digest
listed_population sw7bfloor-df-cmp-abba-ph-decode-b05-a1 /Users/edr/code/JouleWise/runs_window_7bfloor_20260729 file_digest
listed_population sw7bfloor-df-cmp-abba-ph-decode-b05-a2 /Users/edr/code/JouleWise/runs_window_7bfloor_20260729 file_digest
listed_population sw7bfloor-df-cmp-abba-ph-decode-b05-b1 /Users/edr/code/JouleWise/runs_window_7bfloor_20260729 file_digest
listed_population sw7bfloor-df-cmp-abba-ph-decode-b05-b2 /Users/edr/code/JouleWise/runs_window_7bfloor_20260729 file_digest
listed_population sw7bfloor-df-cmp-abba-ph-decode-b06-a1 /Users/edr/code/JouleWise/runs_window_7bfloor_20260729 file_digest
listed_population sw7bfloor-df-cmp-abba-ph-decode-b06-a2 /Users/edr/code/JouleWise/runs_window_7bfloor_20260729 file_digest
listed_population sw7bfloor-df-cmp-abba-ph-decode-b06-b1 /Users/edr/code/JouleWise/runs_window_7bfloor_20260729 file_digest
listed_population sw7bfloor-df-cmp-abba-ph-decode-b06-b2 /Users/edr/code/JouleWise/runs_window_7bfloor_20260729 file_digest
listed_population sw7bfloor-df-cmp-abba-ph-decode-b07-a1 /Users/edr/code/JouleWise/runs_window_7bfloor_20260729 file_digest
listed_population sw7bfloor-df-cmp-abba-ph-decode-b07-a2 /Users/edr/code/JouleWise/runs_window_7bfloor_20260729 file_digest
listed_population sw7bfloor-df-cmp-abba-ph-decode-b07-b1 /Users/edr/code/JouleWise/runs_window_7bfloor_20260729 file_digest
listed_population sw7bfloor-df-cmp-abba-ph-decode-b07-b2 /Users/edr/code/JouleWise/runs_window_7bfloor_20260729 file_digest
listed_population sw7bfloor-df-cmp-abba-ph-decode-b08-a1 /Users/edr/code/JouleWise/runs_window_7bfloor_20260729 file_digest
listed_population sw7bfloor-df-cmp-abba-ph-decode-b08-a2 /Users/edr/code/JouleWise/runs_window_7bfloor_20260729 file_digest
listed_population sw7bfloor-df-cmp-abba-ph-decode-b08-b1 /Users/edr/code/JouleWise/runs_window_7bfloor_20260729 file_digest
listed_population sw7bfloor-df-cmp-abba-ph-decode-b08-b2 /Users/edr/code/JouleWise/runs_window_7bfloor_20260729 file_digest
listed_population sw7bfloor-df-cmp-abba-ph-decode-b09-a1 /Users/edr/code/JouleWise/runs_window_7bfloor_20260729 file_digest
listed_population sw7bfloor-df-cmp-abba-ph-decode-b09-a2 /Users/edr/code/JouleWise/runs_window_7bfloor_20260729 file_digest
listed_population sw7bfloor-df-cmp-abba-ph-decode-b09-b1 /Users/edr/code/JouleWise/runs_window_7bfloor_20260729 file_digest
listed_population sw7bfloor-df-cmp-abba-ph-decode-b09-b2 /Users/edr/code/JouleWise/runs_window_7bfloor_20260729 file_digest
listed_population sw7bfloor-df-cmp-abba-ph-decode-b10-a1 /Users/edr/code/JouleWise/runs_window_7bfloor_20260729 file_digest
listed_population sw7bfloor-df-cmp-abba-ph-decode-b10-a2 /Users/edr/code/JouleWise/runs_window_7bfloor_20260729 file_digest
listed_population sw7bfloor-df-cmp-abba-ph-decode-b10-b1 /Users/edr/code/JouleWise/runs_window_7bfloor_20260729 file_digest
listed_population sw7bfloor-df-cmp-abba-ph-decode-b10-b2 /Users/edr/code/JouleWise/runs_window_7bfloor_20260729 file_digest
listed_population sw7bfloor-df-ph-decode-abs-r01 /Users/edr/code/JouleWise/runs_window_7bfloor_20260729 file_digest
listed_population sw7bfloor-df-ph-decode-abs-r02 /Users/edr/code/JouleWise/runs_window_7bfloor_20260729 file_digest
listed_population sw7bfloor-df-ph-decode-abs-r03 /Users/edr/code/JouleWise/runs_window_7bfloor_20260729 file_digest
listed_population sw7bfloor-df-ph-decode-abs-r04 /Users/edr/code/JouleWise/runs_window_7bfloor_20260729 file_digest
listed_population sw7bfloor-df-ph-decode-abs-r05 /Users/edr/code/JouleWise/runs_window_7bfloor_20260729 file_digest
listed_population sw7bfloor-df-ph-decode-abs-r06 /Users/edr/code/JouleWise/runs_window_7bfloor_20260729 file_digest
listed_population sw7bfloor-df-ph-decode-abs-r07 /Users/edr/code/JouleWise/runs_window_7bfloor_20260729 file_digest
listed_population sw7bfloor-df-ph-decode-abs-r08 /Users/edr/code/JouleWise/runs_window_7bfloor_20260729 file_digest
listed_population sw7bfloor-df-ph-decode-abs-r09 /Users/edr/code/JouleWise/runs_window_7bfloor_20260729 file_digest
listed_population sw7bfloor-df-ph-decode-abs-r10 /Users/edr/code/JouleWise/runs_window_7bfloor_20260729 file_digest
```

## V3 fresh failure index (verbatim)

```text
[B] ERROR: test_calibration_attachment_refuses_runtime_executable_digest_mismatch (tests.test_p2038_production_path.P2038ProductionPathTests.test_calibration_attachment_refuses_runtime_executable_digest_mismatch)
ValueError: instrument calibration battery_float_evidence_missing: pre evidence missing: phase not recorded; post evidence missing: phase not recorded

[B] ERROR: test_extreme_post_idle_sentinel_cannot_leak_into_measured_trace_or_energy (tests.test_p2038_production_path.P2038ProductionPathTests.test_extreme_post_idle_sentinel_cannot_leak_into_measured_trace_or_energy)
ValueError: instrument calibration battery_float_evidence_missing: pre evidence missing: phase not recorded; post evidence missing: phase not recorded

[B] ERROR: test_rail_only_sentinels_withhold_drift_but_leave_gross_eligible (tests.test_p2038_production_path.P2038ProductionPathTests.test_rail_only_sentinels_withhold_drift_but_leave_gross_eligible)
ValueError: instrument calibration battery_float_evidence_missing: pre evidence missing: phase not recorded; post evidence missing: phase not recorded

[B] ERROR: test_real_path_exercises_fail_closed_gate_reasons_without_scalar_edits (tests.test_p2038_production_path.P2038ProductionPathTests.test_real_path_exercises_fail_closed_gate_reasons_without_scalar_edits) (mode='inconsistent')
ValueError: instrument calibration battery_float_evidence_missing: pre evidence missing: phase not recorded; post evidence missing: phase not recorded

[B] ERROR: test_real_path_exercises_fail_closed_gate_reasons_without_scalar_edits (tests.test_p2038_production_path.P2038ProductionPathTests.test_real_path_exercises_fail_closed_gate_reasons_without_scalar_edits) (mode='contaminated_post')
ValueError: instrument calibration battery_float_evidence_missing: pre evidence missing: phase not recorded; post evidence missing: phase not recorded

[B] ERROR: test_real_path_exercises_fail_closed_gate_reasons_without_scalar_edits (tests.test_p2038_production_path.P2038ProductionPathTests.test_real_path_exercises_fail_closed_gate_reasons_without_scalar_edits) (mode='wide')
ValueError: instrument calibration battery_float_evidence_missing: pre evidence missing: phase not recorded; post evidence missing: phase not recorded

[B] ERROR: test_real_powermetrics_evidence_path_passes_p2029_p2040_gates (tests.test_p2038_production_path.P2038ProductionPathTests.test_real_powermetrics_evidence_path_passes_p2029_p2040_gates)
ValueError: instrument calibration battery_float_evidence_missing: pre evidence missing: phase not recorded; post evidence missing: phase not recorded

[B] ERROR: test_strict_rederivation_rejects_evidence_raw_and_marker_tampering (tests.test_p2038_production_path.P2038ProductionPathTests.test_strict_rederivation_rejects_evidence_raw_and_marker_tampering)
ValueError: instrument calibration battery_float_evidence_missing: pre evidence missing: phase not recorded; post evidence missing: phase not recorded

[B] ERROR: test_bundle_producer_seals_sources_and_reports_fixture_comparison (tests.test_phase_share.PhaseBoundaryEnvelopeTests.test_bundle_producer_seals_sources_and_reports_fixture_comparison)
joulewise.bundle_read.BatteryStatusRefusal: battery_float_evidence_missing: prospective bundle (config.json cannot be read: [Errno 2] No such file or directory: '/var/folders/p3/fpwjrcg55vb0zsn3knm7xk2m0000gn/T/tmp1e2m758y/bundle-1/config.json')

[B] ERROR: test_changed_source_bytes_change_a_pinned_sha256_digest (tests.test_phase_share.PhaseBoundaryEnvelopeTests.test_changed_source_bytes_change_a_pinned_sha256_digest)
joulewise.bundle_read.BatteryStatusRefusal: battery_float_evidence_missing: prospective bundle (config.json cannot be read: [Errno 2] No such file or directory: '/var/folders/p3/fpwjrcg55vb0zsn3knm7xk2m0000gn/T/tmpqn28zj5j/bundle-1/config.json')

[B] ERROR: test_retained_r01_current_wire_marginals_define_the_box (tests.test_phase_share.PhaseBoundaryEnvelopeTests.test_retained_r01_current_wire_marginals_define_the_box)
joulewise.bundle_read.BatteryStatusRefusal: battery_float_evidence_missing: prospective bundle (config.json cannot be read: [Errno 2] No such file or directory: '/var/folders/p3/fpwjrcg55vb0zsn3knm7xk2m0000gn/T/tmp5oz0u10t/bundle-1/config.json')

[B] ERROR: test_d079_real_selector_to_real_reducer_embeds_allowance_once (tests.test_whole_window_selection.MaxBracketConsumptionTests.test_d079_real_selector_to_real_reducer_embeds_allowance_once)
ValueError: instrument calibration battery_float_evidence_missing: pre evidence missing: phase not recorded; post evidence missing: phase not recorded

[A] ERROR: test_reducer_0_6_2_uses_the_same_authenticated_override_path (tests.test_whole_window_selection.MaxBracketConsumptionTests.test_reducer_0_6_2_uses_the_same_authenticated_override_path)
KeyError: 'energy_anchor_shift_envelopes'

[B] ERROR: test_authoritative_input_invalid_refuses_without_output (tests.test_window_duration_margins.WindowDurationMarginsTests.test_authoritative_input_invalid_refuses_without_output)
joulewise.bundle_read.BatteryStatusRefusal: battery_float_evidence_missing: prospective bundle (config.json digest does not match metadata.config_sha256)

[B] ERROR: test_closed_schema_rejects_unknown_keys (tests.test_window_duration_margins.WindowDurationMarginsTests.test_closed_schema_rejects_unknown_keys)
joulewise.bundle_read.BatteryStatusRefusal: battery_float_evidence_missing: prospective bundle (config.json digest does not match metadata.config_sha256)

[B] ERROR: test_duplicate_present_member_refuses_without_output (tests.test_window_duration_margins.WindowDurationMarginsTests.test_duplicate_present_member_refuses_without_output)
joulewise.bundle_read.BatteryStatusRefusal: battery_float_evidence_missing: prospective bundle (config.json digest does not match metadata.config_sha256)

[B] ERROR: test_duplicate_registered_member_refuses_without_output (tests.test_window_duration_margins.WindowDurationMarginsTests.test_duplicate_registered_member_refuses_without_output)
joulewise.bundle_read.BatteryStatusRefusal: battery_float_evidence_missing: prospective bundle (config.json digest does not match metadata.config_sha256)

[B] ERROR: test_hand_computed_numeric_oracle (tests.test_window_duration_margins.WindowDurationMarginsTests.test_hand_computed_numeric_oracle)
joulewise.bundle_read.BatteryStatusRefusal: battery_float_evidence_missing: prospective bundle (config.json digest does not match metadata.config_sha256)

[B] ERROR: test_member_config_mismatch_refuses_without_output (tests.test_window_duration_margins.WindowDurationMarginsTests.test_member_config_mismatch_refuses_without_output)
joulewise.bundle_read.BatteryStatusRefusal: battery_float_evidence_missing: prospective bundle (config.json digest does not match metadata.config_sha256)

[B] ERROR: test_missing_member_refuses_without_output (tests.test_window_duration_margins.WindowDurationMarginsTests.test_missing_member_refuses_without_output)
joulewise.bundle_read.BatteryStatusRefusal: battery_float_evidence_missing: prospective bundle (config.json digest does not match metadata.config_sha256)

[B] ERROR: test_negative_margin_is_still_pass (tests.test_window_duration_margins.WindowDurationMarginsTests.test_negative_margin_is_still_pass)
joulewise.bundle_read.BatteryStatusRefusal: battery_float_evidence_missing: prospective bundle (config.json digest does not match metadata.config_sha256)

[B] ERROR: test_non_unique_phase_boundaries_refuse_without_output (tests.test_window_duration_margins.WindowDurationMarginsTests.test_non_unique_phase_boundaries_refuse_without_output)
joulewise.bundle_read.BatteryStatusRefusal: battery_float_evidence_missing: prospective bundle (config.json digest does not match metadata.config_sha256)

[B] ERROR: test_nonfinite_arithmetic_refuses_without_output (tests.test_window_duration_margins.WindowDurationMarginsTests.test_nonfinite_arithmetic_refuses_without_output)
joulewise.bundle_read.BatteryStatusRefusal: battery_float_evidence_missing: prospective bundle (config.json digest does not match metadata.config_sha256)

[B] ERROR: test_pack_identity_invalid_refuses_without_output (tests.test_window_duration_margins.WindowDurationMarginsTests.test_pack_identity_invalid_refuses_without_output)
joulewise.bundle_read.BatteryStatusRefusal: battery_float_evidence_missing: prospective bundle (config.json digest does not match metadata.config_sha256)

[B] ERROR: test_pack_pin_invalid_refuses_without_output (tests.test_window_duration_margins.WindowDurationMarginsTests.test_pack_pin_invalid_refuses_without_output)
joulewise.bundle_read.BatteryStatusRefusal: battery_float_evidence_missing: prospective bundle (config.json digest does not match metadata.config_sha256)

[B] ERROR: test_recorder_cli_is_deterministic_across_independent_processes (tests.test_window_duration_margins.WindowDurationMarginsTests.test_recorder_cli_is_deterministic_across_independent_processes)
joulewise.bundle_read.BatteryStatusRefusal: battery_float_evidence_missing: prospective bundle (config.json digest does not match metadata.config_sha256)

[B] ERROR: test_recorder_cli_refuses_republication_in_same_namespace (tests.test_window_duration_margins.WindowDurationMarginsTests.test_recorder_cli_refuses_republication_in_same_namespace)
joulewise.bundle_read.BatteryStatusRefusal: battery_float_evidence_missing: prospective bundle (config.json digest does not match metadata.config_sha256)

[B] ERROR: test_registered_membership_invalid_refuses_without_output (tests.test_window_duration_margins.WindowDurationMarginsTests.test_registered_membership_invalid_refuses_without_output)
joulewise.bundle_read.BatteryStatusRefusal: battery_float_evidence_missing: prospective bundle (config.json digest does not match metadata.config_sha256)

[B] ERROR: test_second_record_call_refuses_and_preserves_first_receipt_bytes (tests.test_window_duration_margins.WindowDurationMarginsTests.test_second_record_call_refuses_and_preserves_first_receipt_bytes)
joulewise.bundle_read.BatteryStatusRefusal: battery_float_evidence_missing: prospective bundle (config.json digest does not match metadata.config_sha256)

[B] ERROR: test_summary_precheck_is_cross_check_not_copy_source (tests.test_window_duration_margins.WindowDurationMarginsTests.test_summary_precheck_is_cross_check_not_copy_source)
joulewise.bundle_read.BatteryStatusRefusal: battery_float_evidence_missing: prospective bundle (config.json digest does not match metadata.config_sha256)

[B] ERROR: test_synthetic_arithmetic_fixture_derives_three_cells (tests.test_window_duration_margins.WindowDurationMarginsTests.test_synthetic_arithmetic_fixture_derives_three_cells)
joulewise.bundle_read.BatteryStatusRefusal: battery_float_evidence_missing: prospective bundle (config.json digest does not match metadata.config_sha256)

[B] ERROR: test_tampered_events_refuses_without_output (tests.test_window_duration_margins.WindowDurationMarginsTests.test_tampered_events_refuses_without_output)
joulewise.bundle_read.BatteryStatusRefusal: battery_float_evidence_missing: prospective bundle (config.json digest does not match metadata.config_sha256)

[B] ERROR: test_tampered_power_trace_refuses_without_output (tests.test_window_duration_margins.WindowDurationMarginsTests.test_tampered_power_trace_refuses_without_output)
joulewise.bundle_read.BatteryStatusRefusal: battery_float_evidence_missing: prospective bundle (config.json digest does not match metadata.config_sha256)

[B] ERROR: test_two_derivations_are_byte_identical (tests.test_window_duration_margins.WindowDurationMarginsTests.test_two_derivations_are_byte_identical)
joulewise.bundle_read.BatteryStatusRefusal: battery_float_evidence_missing: prospective bundle (config.json digest does not match metadata.config_sha256)

[B] ERROR: test_unavailable_b_operative_refuses_without_output (tests.test_window_duration_margins.WindowDurationMarginsTests.test_unavailable_b_operative_refuses_without_output)
joulewise.bundle_read.BatteryStatusRefusal: battery_float_evidence_missing: prospective bundle (config.json digest does not match metadata.config_sha256)

[B] ERROR: test_unknown_b_operative_refuses_without_output (tests.test_window_duration_margins.WindowDurationMarginsTests.test_unknown_b_operative_refuses_without_output)
joulewise.bundle_read.BatteryStatusRefusal: battery_float_evidence_missing: prospective bundle (config.json digest does not match metadata.config_sha256)

[B] ERROR: test_unrecordable_minimum_refuses_without_output (tests.test_window_duration_margins.WindowDurationMarginsTests.test_unrecordable_minimum_refuses_without_output)
joulewise.bundle_read.BatteryStatusRefusal: battery_float_evidence_missing: prospective bundle (config.json digest does not match metadata.config_sha256)

[A] FAIL: test_b4_salvage_floor_binder_accepts_correct_pair_after_real_row_validation (tests.test_analysis_integration.AnalysisIntegrationTests.test_b4_salvage_floor_binder_accepts_correct_pair_after_real_row_validation)
AssertionError: True is not false

[B] FAIL: test_allowlisted_legacy_identity_allows_missing_workload_provenance (tests.test_audit_amplification.StrictGateInteractionAmplification.test_allowlisted_legacy_identity_allows_missing_workload_provenance)
-  '(config.json digest does not match metadata.config_sha256)']

[B] FAIL: test_legacy_summary_tolerance_does_not_hide_raw_to_trace_order_drift (tests.test_audit_amplification.StrictGateInteractionAmplification.test_legacy_summary_tolerance_does_not_hide_raw_to_trace_order_drift)
AssertionError: <RunStatus.FAILED: 'failed'> != <RunStatus.SUCCEEDED: 'succeeded'>

[B] FAIL: test_raw_to_trace_rejects_interval_support_drift (tests.test_audit_amplification.StrictGateInteractionAmplification.test_raw_to_trace_rejects_interval_support_drift)
AssertionError: <RunStatus.FAILED: 'failed'> != <RunStatus.SUCCEEDED: 'succeeded'>

[B] FAIL: test_raw_to_trace_rejects_sub_epsilon_numeric_drift (tests.test_audit_amplification.StrictGateInteractionAmplification.test_raw_to_trace_rejects_sub_epsilon_numeric_drift)
AssertionError: <RunStatus.FAILED: 'failed'> != <RunStatus.SUCCEEDED: 'succeeded'>

[D] FAIL: test_campaign_prebundle_process_failure_retains_identity_receipt_and_row (tests.test_axi_controller_events.AxiControllerEventTests.test_campaign_prebundle_process_failure_retains_identity_receipt_and_row)
AssertionError: 2 != 1

[D] FAIL: test_campaign_zero_exit_without_finalized_bundle_is_dispatch_failure (tests.test_axi_controller_events.AxiControllerEventTests.test_campaign_zero_exit_without_finalized_bundle_is_dispatch_failure)
AssertionError: 2 != 1

[D] FAIL: test_v2_campaign_refuses_eligible_receipt_after_bundle_store_deletion (tests.test_axi_mock_spec.AxiMockSpecTests.test_v2_campaign_refuses_eligible_receipt_after_bundle_store_deletion)
AssertionError: 2 != 0

[D] FAIL: test_v2_campaign_writes_complete_immutable_ledger_and_pair_reports (tests.test_axi_mock_spec.AxiMockSpecTests.test_v2_campaign_writes_complete_immutable_ledger_and_pair_reports)
AssertionError: 2 != 0

[A] FAIL: test_reduce_default_replays_recorded_060_and_051_versions (tests.test_cli.CliTests.test_reduce_default_replays_recorded_060_and_051_versions) (expected_version='0.5.1')
AssertionError: 3 != 0

[B] FAIL: test_settled_marker_reduce_before_completion_carries_full_lineage (tests.test_cli_run.ReduceVerbTests.test_settled_marker_reduce_before_completion_carries_full_lineage)
AssertionError: 3 != 0 : 

[B] FAIL: test_all_six_allowlisted_legacy_bundles_keep_dispatch_semantics (tests.test_cli_run.StrictValidateTests.test_all_six_allowlisted_legacy_bundles_keep_dispatch_semantics) (identity=('example-mac-mlx-local__r1', 'ee80585a2f6cee6aa7e12eb83c318fd88a934be02d5fa2fb2eb7509630640fd5'))
-  '(config.json digest does not match metadata.config_sha256)']

[B] FAIL: test_all_six_allowlisted_legacy_bundles_keep_dispatch_semantics (tests.test_cli_run.StrictValidateTests.test_all_six_allowlisted_legacy_bundles_keep_dispatch_semantics) (identity=('example-mac-mlx-local__r2', '08144a7be4a10d887babbd5fcd1a93f391c1db2d11c63d3131afad80b59cb373'))
-  '(config.json digest does not match metadata.config_sha256)']

[B] FAIL: test_all_six_allowlisted_legacy_bundles_keep_dispatch_semantics (tests.test_cli_run.StrictValidateTests.test_all_six_allowlisted_legacy_bundles_keep_dispatch_semantics) (identity=('example-mac-mlx-local__r3', 'fe75fc3bafe0af7485fdf98b70ac3d07ccc1db502230bf1b180b94689ab54652'))
-  '(config.json digest does not match metadata.config_sha256)']

[B] FAIL: test_all_six_allowlisted_legacy_bundles_keep_dispatch_semantics (tests.test_cli_run.StrictValidateTests.test_all_six_allowlisted_legacy_bundles_keep_dispatch_semantics) (identity=('example-mac-mlx-qwen35-122b-512t__r1', '74761e420520e0d6d979be7d3d08aa6ff7e0f5f8ac8e48109d3dedc08d8d0b7a'))
-  '(config.json digest does not match metadata.config_sha256)']

[B] FAIL: test_all_six_allowlisted_legacy_bundles_keep_dispatch_semantics (tests.test_cli_run.StrictValidateTests.test_all_six_allowlisted_legacy_bundles_keep_dispatch_semantics) (identity=('example-mac-mlx-qwen35-122b-512t__r2', '8808632f0235b412d30563747283c397ad534edb711e4cec784712182cbe3b60'))
-  '(config.json digest does not match metadata.config_sha256)']

[B] FAIL: test_all_six_allowlisted_legacy_bundles_keep_dispatch_semantics (tests.test_cli_run.StrictValidateTests.test_all_six_allowlisted_legacy_bundles_keep_dispatch_semantics) (identity=('example-mac-mlx-qwen35-122b-512t__r3', '8be8dd955219a8631c8e37a1b3467f368f37624d07acebd2d52924137dff69f4'))
-  '(config.json digest does not match metadata.config_sha256)']

[B] FAIL: test_allowlisted_legacy_fresh_idle_metadata_mismatch_fails_strict (tests.test_cli_run.StrictValidateTests.test_allowlisted_legacy_fresh_idle_metadata_mismatch_fails_strict)
+  '(idle_metadata_mismatch)']

[B] FAIL: test_allowlisted_legacy_present_non_object_provenance_fails_strict (tests.test_cli_run.StrictValidateTests.test_allowlisted_legacy_present_non_object_provenance_fails_strict) (value='legacy')
AssertionError: False is not true : ['summary provenance is not null or an object', 'strict: battery_float_evidence_missing: not_applicable not bound (config.json digest does not match metadata.config_sha256)']

[B] FAIL: test_allowlisted_legacy_present_non_object_provenance_fails_strict (tests.test_cli_run.StrictValidateTests.test_allowlisted_legacy_present_non_object_provenance_fails_strict) (value=['legacy'])
AssertionError: False is not true : ['summary provenance is not null or an object', 'strict: battery_float_evidence_missing: not_applicable not bound (config.json digest does not match metadata.config_sha256)']

[B] FAIL: test_allowlisted_legacy_present_null_provenance_fails_strict (tests.test_cli_run.StrictValidateTests.test_allowlisted_legacy_present_null_provenance_fails_strict)
AssertionError: False is not true : ['strict: battery_float_evidence_missing: not_applicable not bound (config.json digest does not match metadata.config_sha256)']

[B] FAIL: test_allowlisted_legacy_recorded_value_mutations_fail_strict (tests.test_cli_run.StrictValidateTests.test_allowlisted_legacy_recorded_value_mutations_fail_strict) (field='energy_token_j')
AssertionError: False is not true : ['strict: battery_float_evidence_missing: not_applicable not bound (config.json digest does not match metadata.config_sha256)']

[B] FAIL: test_allowlisted_legacy_recorded_value_mutations_fail_strict (tests.test_cli_run.StrictValidateTests.test_allowlisted_legacy_recorded_value_mutations_fail_strict) (field='measurement_quality.token_count_source')
AssertionError: False is not true : ['strict: battery_float_evidence_missing: not_applicable not bound (config.json digest does not match metadata.config_sha256)']

[B] FAIL: test_allowlisted_legacy_recorded_value_mutations_fail_strict (tests.test_cli_run.StrictValidateTests.test_allowlisted_legacy_recorded_value_mutations_fail_strict) (field='gross_energy_j')
AssertionError: False is not true : ['strict: battery_float_evidence_missing: not_applicable not bound (config.json digest does not match metadata.config_sha256)']

[B] FAIL: test_config_powermetrics_missing_raw_plist_fails_strict (tests.test_cli_run.StrictValidateTests.test_config_powermetrics_missing_raw_plist_fails_strict)
AssertionError: <RunStatus.FAILED: 'failed'> != <RunStatus.SUCCEEDED: 'succeeded'>

[B] FAIL: test_current_bundle_spoofed_as_legacy_with_absent_provenance_passes (tests.test_cli_run.StrictValidateTests.test_current_bundle_spoofed_as_legacy_with_absent_provenance_passes)
-  '(config.json digest does not match metadata.config_sha256)']

[B] FAIL: test_legacy_dispatch_tolerates_governed_additive_absence (tests.test_cli_run.StrictValidateTests.test_legacy_dispatch_tolerates_governed_additive_absence)
-  '(config.json digest does not match metadata.config_sha256)']

[B] FAIL: test_legacy_summary_missing_additive_null_keys_passes_strict (tests.test_cli_run.StrictValidateTests.test_legacy_summary_missing_additive_null_keys_passes_strict)
-  '(config.json digest does not match metadata.config_sha256)']

[B] FAIL: test_legacy_summary_missing_honesty_fields_keeps_strict_tolerance (tests.test_cli_run.StrictValidateTests.test_legacy_summary_missing_honesty_fields_keeps_strict_tolerance)
-  '(config.json digest does not match metadata.config_sha256)']

[B] FAIL: test_powermetrics_raw_to_trace_formatting_only_variant_passes_strict (tests.test_cli_run.StrictValidateTests.test_powermetrics_raw_to_trace_formatting_only_variant_passes_strict)
AssertionError: <RunStatus.FAILED: 'failed'> != <RunStatus.SUCCEEDED: 'succeeded'>

[B] FAIL: test_powermetrics_raw_to_trace_matching_bundle_passes_strict (tests.test_cli_run.StrictValidateTests.test_powermetrics_raw_to_trace_matching_bundle_passes_strict)
AssertionError: <RunStatus.FAILED: 'failed'> != <RunStatus.SUCCEEDED: 'succeeded'>

[B] FAIL: test_powermetrics_raw_to_trace_value_tamper_fails_with_row_and_rail (tests.test_cli_run.StrictValidateTests.test_powermetrics_raw_to_trace_value_tamper_fails_with_row_and_rail)
AssertionError: <RunStatus.FAILED: 'failed'> != <RunStatus.SUCCEEDED: 'succeeded'>

[B] FAIL: test_raw_to_trace_ignores_tampered_metadata_adapter_name (tests.test_cli_run.StrictValidateTests.test_raw_to_trace_ignores_tampered_metadata_adapter_name)
AssertionError: <RunStatus.FAILED: 'failed'> != <RunStatus.SUCCEEDED: 'succeeded'>

[B] FAIL: test_raw_to_trace_runs_without_metadata_adapters_block (tests.test_cli_run.StrictValidateTests.test_raw_to_trace_runs_without_metadata_adapters_block)
AssertionError: <RunStatus.FAILED: 'failed'> != <RunStatus.SUCCEEDED: 'succeeded'>

[B] FAIL: test_raw_to_trace_unregistered_production_backend_hard_fails_strict (tests.test_cli_run.StrictValidateTests.test_raw_to_trace_unregistered_production_backend_hard_fails_strict)
AssertionError: False is not true : ["metadata.config_sha256 mismatch: metadata has 'c055d1ee4b759c6cbda83085214e1923bf506d344c81b7deea89537cf71ea384', config.json bytes hash to 'fca4a3bc68d3596cab9fcbb1851a49d9e22516de8ec6fabdadd3ea06a04df505'", 'strict: battery_float_evidence_missing: not_applicable not bound (config.json digest does not match metadata.config_sha256)']

[A] FAIL: test_bracket_max_exceeding_minted_member_bound_refuses (tests.test_floor_extraction.CpuAndWholeWindowClaimBarrierTests.test_bracket_max_exceeding_minted_member_bound_refuses)
AssertionError: 'calibration_bracket_exceeds_minted_bound' not found in {'environment_admission_missing'}

[A] FAIL: test_current_neg8_summary_disagreement_maps_to_whole_window_conflict (tests.test_floor_extraction.CpuAndWholeWindowClaimBarrierTests.test_current_neg8_summary_disagreement_maps_to_whole_window_conflict)
-  'whole_window_verdict_provenance_invalid')

[A] FAIL: test_current_whole_window_rederives_cpu_and_adapter_labels (tests.test_floor_extraction.CpuAndWholeWindowClaimBarrierTests.test_current_whole_window_rederives_cpu_and_adapter_labels)
'environment_admission_missing'

[A] FAIL: test_floor_cpu_ledger_rejects_duplicates_reordering_mismatch_and_absence (tests.test_floor_extraction.CpuAndWholeWindowClaimBarrierTests.test_floor_cpu_ledger_rejects_duplicates_reordering_mismatch_and_absence)
+ ()

[A] FAIL: test_inflated_metadata_effective_bound_is_provenance_invalid (tests.test_floor_extraction.CpuAndWholeWindowClaimBarrierTests.test_inflated_metadata_effective_bound_is_provenance_invalid)
AssertionError: 'whole_window_verdict_provenance_invalid' not found in {'environment_admission_missing'}

[B] FAIL: test_calibration_attachment_refuses_config_only_power_policy (tests.test_p2038_production_path.P2038ProductionPathTests.test_calibration_attachment_refuses_config_only_power_policy)
AssertionError: "runtime-observed power policy" does not match "instrument calibration battery_float_evidence_missing: pre evidence missing: phase not recorded; post evidence missing: phase not recorded"

[B] FAIL: test_powermetrics_raw_plist_is_omitted_but_source_hash_is_recorded (tests.test_package_bundle_pack.BundlePackTests.test_powermetrics_raw_plist_is_omitted_but_source_hash_is_recorded)
AssertionError: <RunStatus.FAILED: 'failed'> != <RunStatus.SUCCEEDED: 'succeeded'>

[D] FAIL: test_d173_is_only_evidence_entry_and_fixture_cannot_render (tests.test_paper_reported_energy.ReportedEnergyTests.test_d173_is_only_evidence_entry_and_fixture_cannot_render)
AssertionError: stale supply-map receipt digest: reported_energy_parents

[A] FAIL: test_strict_validation_tamper_refuses_without_enclosure (tests.test_partial_record_enclosure.PartialRecordEnclosureTests.test_strict_validation_tamper_refuses_without_enclosure)
+ bundle_strict_validation_failed

[B] FAIL: test_run_bundle_metadata_records_dropped_powermetrics_tail_diagnostic (tests.test_powermetrics.PowermetricsAdapterTests.test_run_bundle_metadata_records_dropped_powermetrics_tail_diagnostic)
AssertionError: <RunStatus.FAILED: 'failed'> != <RunStatus.SUCCEEDED: 'succeeded'>

[A] FAIL: test_b1_r1_explicit_minted_fresh_valid_session_is_prepared_and_accepted (tests.test_whole_window_selection.MaxBracketConsumptionTests.test_b1_r1_explicit_minted_fresh_valid_session_is_prepared_and_accepted)
+ ()

[A] FAIL: test_b1_r4_implicit_minted_fresh_valid_session_matches_explicit (tests.test_whole_window_selection.MaxBracketConsumptionTests.test_b1_r4_implicit_minted_fresh_valid_session_matches_explicit)
+ ()

[A] FAIL: test_minted_semantics_loads_and_refuses_pending_ledger_snapshot (tests.test_whole_window_selection.MaxBracketConsumptionTests.test_minted_semantics_loads_and_refuses_pending_ledger_snapshot)
AssertionError: False is not true

[A] FAIL: test_explicit_salvage_dispatch_selects_only_salvage (tests.test_whole_window_selection.SalvageSemanticsDispatchTests.test_explicit_salvage_dispatch_selects_only_salvage)
KILLED 3 renderer AST mutations: wrapper deletion, widened annotation, unregistered renderer

```

## V1 final five lines

```text
.............................................................................................................................................................................................................................................................................................................................................
----------------------------------------------------------------------
Ran 333 tests in 434.908s

OK
```

## V2 final five lines

```text
...........................................................................................................................................................................................................................................................................................................................
----------------------------------------------------------------------
Ran 315 tests in 534.259s

OK
```

## V3 final five lines

```text
----------------------------------------------------------------------
Ran 1052 tests in 437.842s

FAILED (failures=49, errors=37, skipped=16)
KILLED 3 renderer AST mutations: wrapper deletion, widened annotation, unregistered renderer
```

## red-36-git (verbatim)

```text
FF
======================================================================
FAIL: test_no_consumer_references_a_verdict_primitive (tests.test_battery_float_consumers.ConsumerGuardTests.test_no_consumer_references_a_verdict_primitive)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/private/tmp/bfgs-s1-head/tests/test_battery_float_consumers.py", line 282, in test_no_consumer_references_a_verdict_primitive
    self.assertEqual(found, [])
    ~~~~~~~~~~~~~~~~^^^^^^^^^^^
AssertionError: Lists differ: [('joulewise/controller.py', 1983, 'datacl[185 chars]ce')] != []

First list contains 4 additional elements.
First extra element 0:
('joulewise/controller.py', 1983, 'dataclasses.replace')

+ []
- [('joulewise/controller.py', 1983, 'dataclasses.replace'),
-  ('joulewise/controller.py', 2566, 'dataclasses.replace'),
-  ('joulewise/controller.py', 2569, 'dataclasses.replace'),
-  ('joulewise/controller.py', 2966, 'dataclasses.replace')]

======================================================================
FAIL: test_replace_call_allowlist_is_exact_and_only_covers_older_types (tests.test_battery_float_consumers.ConsumerGuardTests.test_replace_call_allowlist_is_exact_and_only_covers_older_types)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/private/tmp/bfgs-s1-head/tests/test_battery_float_consumers.py", line 336, in test_replace_call_allowlist_is_exact_and_only_covers_older_types
    self.assertEqual(Counter(sites), Counter(REPLACE_CALL_ALLOWLIST.keys()))
    ~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
AssertionError: Count[125 chars]wise/controller.py', '_Execution._axi_request_[1898 chars]: 1}) != Count[125 chars]wise/night_gate.py', '_check_machine.battery_r[1385 chars]: 1})

----------------------------------------------------------------------
Ran 2 tests in 8.752s

FAILED (failures=2)
```

## red-36-forgery-mutant (verbatim)

```text
F
======================================================================
FAIL: test_controller_replace_forgery_self_test (tests.test_battery_float_consumers.ConsumerGuardTests.test_controller_replace_forgery_self_test)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/private/tmp/bfgs-s1-head/tests/test_battery_float_consumers.py", line 355, in test_controller_replace_forgery_self_test
    self.assertEqual(violations("joulewise/controller.py", forged), [
    ~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
        ("joulewise/controller.py", source[:source.index(line)].count("\n") + 2,
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
         "dataclasses.replace")])
         ^^^^^^^^^^^^^^^^^^^^^^^^
AssertionError: Lists differ: [] != [('joulewise/controller.py', 449, 'dataclasses.replace')]

Second list contains 1 additional elements.
First extra element 0:
('joulewise/controller.py', 449, 'dataclasses.replace')

- []
+ [('joulewise/controller.py', 449, 'dataclasses.replace')]

----------------------------------------------------------------------
Ran 1 test in 0.079s

FAILED (failures=1)
```

## red-head (verbatim)

```text
FFFFEEE.
======================================================================
ERROR: test_two_prospective_members_are_both_named (tests.test_bfgs_window_consumers.WindowMembersTests.test_two_prospective_members_are_both_named)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/private/tmp/bfgs-s1-head/joulewise/bundle_read.py", line 252, in authenticate_window_members
    verdict = reader._battery_verdict(metadata)
  File "/private/tmp/bfgs-s1-head/joulewise/bundle_read.py", line 414, in _battery_verdict
    raise BundleReadError("battery_float_evidence_missing: prospective bundle")
joulewise.bundle_read.BundleReadError: battery_float_evidence_missing: prospective bundle

The above exception was the direct cause of the following exception:

Traceback (most recent call last):
  File "/private/tmp/bfgs-s1-head/tests/test_bfgs_window_consumers.py", line 100, in test_two_prospective_members_are_both_named
    authenticate_window_members(members)
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^
  File "/private/tmp/bfgs-s1-head/joulewise/bundle_read.py", line 254, in authenticate_window_members
    raise battery_float.CustodyUnreadable(f"{label}: {exc}") from exc
joulewise.battery_float.CustodyUnreadable: a: battery_float_evidence_missing: prospective bundle

======================================================================
ERROR: test_confounded_then_prospective_names_both (tests.test_bfgs_window_consumers.WindowMembersTests.test_confounded_then_prospective_names_both)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/private/tmp/bfgs-s1-head/joulewise/bundle_read.py", line 252, in authenticate_window_members
    verdict = reader._battery_verdict(metadata)
  File "/private/tmp/bfgs-s1-head/joulewise/bundle_read.py", line 414, in _battery_verdict
    raise BundleReadError("battery_float_evidence_missing: prospective bundle")
joulewise.bundle_read.BundleReadError: battery_float_evidence_missing: prospective bundle

The above exception was the direct cause of the following exception:

Traceback (most recent call last):
  File "/private/tmp/bfgs-s1-head/tests/test_bfgs_window_consumers.py", line 121, in test_confounded_then_prospective_names_both
    authenticate_window_members((("charging", charging), ("prospective", prospective)))
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/private/tmp/bfgs-s1-head/joulewise/bundle_read.py", line 254, in authenticate_window_members
    raise battery_float.CustodyUnreadable(f"{label}: {exc}") from exc
joulewise.battery_float.CustodyUnreadable: prospective: battery_float_evidence_missing: prospective bundle

======================================================================
ERROR: test_custody_second_member_has_label_note_and_original_failures (tests.test_bfgs_window_consumers.WindowMembersTests.test_custody_second_member_has_label_note_and_original_failures)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/private/tmp/bfgs-s1-head/tests/test_bfgs_window_consumers.py", line 138, in test_custody_second_member_has_label_note_and_original_failures
    self.assertEqual(exc.window_member, "member-7")
                     ^^^^^^^^^^^^^^^^^
AttributeError: 'CustodyFailure' object has no attribute 'window_member'

======================================================================
FAIL: test_nonmock_missing_key_config_binding_details (tests.test_bundle_read.StrictAccessorTests.test_nonmock_missing_key_config_binding_details) (mode='altered')
----------------------------------------------------------------------
joulewise.bundle_read.BundleReadError: config.json digest does not match metadata.config_sha256

During handling of the above exception, another exception occurred:

Traceback (most recent call last):
  File "/private/tmp/bfgs-s1-head/tests/test_bundle_read.py", line 262, in test_nonmock_missing_key_config_binding_details
    with self.assertRaisesRegex(BatteryStatusRefusal,
         ~~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^
                                r"^battery_float_evidence_missing: prospective bundle \("):
                                ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
AssertionError: "^battery_float_evidence_missing: prospective bundle \(" does not match "config.json digest does not match metadata.config_sha256"

======================================================================
FAIL: test_nonmock_missing_key_config_binding_details (tests.test_bundle_read.StrictAccessorTests.test_nonmock_missing_key_config_binding_details) (mode='deleted')
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/private/tmp/bfgs-s1-head/joulewise/bundle_read.py", line 419, in _digest_bound_mock_config
    raw = read_authentication_input(
        self._path / "config.json", grammar="raw",
        label=f"bundle {self._path.name} config.json",
    )
  File "/private/tmp/bfgs-s1-head/joulewise/authentication_io.py", line 555, in read_authentication_input
    return Path(path).read_bytes()
           ~~~~~~~~~~~~~~~~~~~~~^^
  File "/opt/homebrew/Cellar/python@3.14/3.14.7/Frameworks/Python.framework/Versions/3.14/lib/python3.14/pathlib/__init__.py", line 777, in read_bytes
    with self.open(mode='rb', buffering=0) as f:
         ~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^
  File "/opt/homebrew/Cellar/python@3.14/3.14.7/Frameworks/Python.framework/Versions/3.14/lib/python3.14/pathlib/__init__.py", line 771, in open
    return io.open(self, mode, buffering, encoding, errors, newline)
           ~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
FileNotFoundError: [Errno 2] No such file or directory: '/var/folders/p3/fpwjrcg55vb0zsn3knm7xk2m0000gn/T/tmp596sfzx1/runs/missing-key-deleted/config.json'

The above exception was the direct cause of the following exception:

joulewise.bundle_read.BundleReadError: config.json cannot be read: [Errno 2] No such file or directory: '/var/folders/p3/fpwjrcg55vb0zsn3knm7xk2m0000gn/T/tmp596sfzx1/runs/missing-key-deleted/config.json'

During handling of the above exception, another exception occurred:

Traceback (most recent call last):
  File "/private/tmp/bfgs-s1-head/tests/test_bundle_read.py", line 262, in test_nonmock_missing_key_config_binding_details
    with self.assertRaisesRegex(BatteryStatusRefusal,
         ~~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^
                                r"^battery_float_evidence_missing: prospective bundle \("):
                                ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
AssertionError: "^battery_float_evidence_missing: prospective bundle \(" does not match "config.json cannot be read: [Errno 2] No such file or directory: '/var/folders/p3/fpwjrcg55vb0zsn3knm7xk2m0000gn/T/tmp596sfzx1/runs/missing-key-deleted/config.json'"

======================================================================
FAIL: test_marker_config_digest_mismatch_has_not_bound_prefix (tests.test_bundle_read.StrictAccessorTests.test_marker_config_digest_mismatch_has_not_bound_prefix)
----------------------------------------------------------------------
joulewise.bundle_read.BundleReadError: config.json digest does not match metadata.config_sha256

During handling of the above exception, another exception occurred:

Traceback (most recent call last):
  File "/private/tmp/bfgs-s1-head/tests/test_bundle_read.py", line 274, in test_marker_config_digest_mismatch_has_not_bound_prefix
    with self.assertRaisesRegex(BatteryStatusRefusal,
         ~~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^
                                r"^battery_float_evidence_missing: not_applicable not bound \("):
                                ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
AssertionError: "^battery_float_evidence_missing: not_applicable not bound \(" does not match "config.json digest does not match metadata.config_sha256"

======================================================================
FAIL: test_explicit_mock_not_applicable_refuses_nonmock_config (tests.test_bundle_read.StrictAccessorTests.test_explicit_mock_not_applicable_refuses_nonmock_config)
----------------------------------------------------------------------
joulewise.bundle_read.BundleReadError: battery_float_evidence_missing: invalid record

During handling of the above exception, another exception occurred:

Traceback (most recent call last):
  File "/private/tmp/bfgs-s1-head/tests/test_bundle_read.py", line 366, in test_explicit_mock_not_applicable_refuses_nonmock_config
    with self.assertRaisesRegex(BundleReadError, "^battery_float_evidence_missing: not_applicable not bound$"):
         ~~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
AssertionError: "^battery_float_evidence_missing: not_applicable not bound$" does not match "battery_float_evidence_missing: invalid record"

----------------------------------------------------------------------
Ran 7 tests in 0.473s

FAILED (failures=4, errors=3)
```

## red-39 (verbatim)

```text
HEAD RED BundleReadError battery_float_evidence_missing: prospective bundle
```

## red-43-stage (verbatim)

```text
base_status RunStatus.SUCCEEDED sentinel_events 0 expected 2
Traceback (most recent call last):
  File "<stdin>", line 13, in <module>
AssertionError
```

## green-36 (verbatim)

```text
.....
----------------------------------------------------------------------
Ran 5 tests in 8.625s

OK
```

## focused-final (verbatim)

```text
...............................................................
----------------------------------------------------------------------
Ran 63 tests in 46.994s

OK
```

## rpt001-focused (verbatim)

```text
.
----------------------------------------------------------------------
Ran 1 test in 9.640s

OK
```
