# Window B re-evaluation evidence — steps 1–5 only

Execution date: 2026-08-03. Repository head: `0e40111ca6f498d167a71b66b5069d988b9bb9bb`. The whole-window verdict (brief step 6) was not run. No file under the runs or custody roots was written.

## Governing inputs and boundary

- Campaign policy SHA-256: `b0d7b228b88bea717aa9269c103aca760cc36cf05239e0f86c235b4b29665efd`.
- Runs root: `/Users/edr/code/JouleWise/runs_window_metrologyB_20260801`.
- Quarantine root: `/Users/edr/JouleWise-window-custody/window_metrologyB_20260801/quarantine`.
- D-100 addendum custody universe recorded in the closure: `/Users/edr/code/JouleWise/runs_window_metrologyB_20260801` plus `/Users/edr/JouleWise-window-custody/window_metrologyB_20260801/quarantine`.
- Delivery deviation applied: artifacts were staged under `.desk/winb_reeval/`; the lead will install the unchanged bytes into real custody before the reserved verdict run.

## Step 1 — salvage closure

The fact sheet uses zero-based campaign-log indices. Primary log verification:

| Zero index | Physical line | Run ID | Status | Exit | Timestamp | Source manifest |
|---:|---:|---|---|---:|---|---|
| 39 | 40 | `mtnull-o0512-b04-b2` | `failed` | 3 | `2026-08-01T11:30:40.330873Z` | `campaign_manifests/campaign-20260801T104658893526Z-p56481.json` |
| 87 | 88 | `mtadd-p2048o0128-r08` | `failed` | 3 | `2026-08-01T13:14:34.990670Z` | `campaign_manifests/campaign-20260801T120835813415Z-p59214.json` |
| 112 | 113 | `mtadd-p2048o0128-r08` | `failed` | 3 | `2026-08-01T13:30:42.089400Z` | `campaign_manifests/campaign-20260801T132123643876Z-p61920.json` |

Occurrence 1 corroboration: zero-index 55 (physical line 56) is the successful `mtnull-o0512-b04-b2` continuation at `2026-08-01T11:46:38.354433Z`; zero-index 118 (physical line 119) is its valid `campaign_occurrence_supersession`, entry SHA-256 `3896c5ed92a0606751a8b9c5474aba1737429e8f893e6021258abdd22dcbd507`. It is therefore not the dangler. Occurrences 2 and 3 leave `mtadd-p2048o0128-r08` with zero surviving bundles and make it the single exclusion target.

Mechanical inspection of the three quarantine directories:

| Occurrence | Quarantine directory | Files | Descriptor-manifest SHA-256 | Failure timestamp (s) | Telemetry first/last (s) | Teardown (s) |
|---:|---|---:|---|---:|---|---:|
| 1 | `/Users/edr/JouleWise-window-custody/window_metrologyB_20260801/quarantine/mtnull-o0512-b04-b2__20260801T113258Z` | 22 | `1857ebb709713a0aa0ea640ee3c2598c5d13ca085333e8b435a5a7883db7ef0d` | 1785583837.520066 | 1785583760.0 / 1785583837.5868704 | 0.06680440902709961 |
| 2 | `/Users/edr/JouleWise-window-custody/window_metrologyB_20260801/quarantine/mtadd-p2048o0128-r08__20260801T131705Z` | 22 | `72fb6d92cceead16c6082c0fd2266727989bb94deffe9e0f2df91fa0c947c2e2` | 1785590072.201848 | 1785589995.0 / 1785590072.3728275 | 0.17097949981689453 |
| 3 | `/Users/edr/JouleWise-window-custody/window_metrologyB_20260801/quarantine/mtadd-p2048o0128-r08__20260801T133315Z` | 22 | `329bc9f88295eb6a7ab91a25f28ea2600483fca42bd3e3396629a1aee5df3039` | 1785591039.250626 | 1785590962.0 / 1785591039.38633 | 0.13570380210876465 |

For every occurrence, the exact event sequence is `run_started/run → stage_started/validate → stage_completed/validate → stage_started/prepare → stage_completed/prepare → stage_started/idle_baseline → failure/idle_baseline → run_finalized/run`. Metadata has `environment_admission.decision = "abort"`, `claim_reason = "environment_admission_failed"`, and two ordered attempts with `admitted = false`. Summary status is `failed`; all defined measurand fields are null. The byte-derived shared failure signature is `9ae545544eb92282a0d28b41eb103ef155e7233c346aae1aaa821157179236a1`, terminal stage `idle_baseline`, failure reason `unknown_error`.

The quarantine-root closure manifest contains 66 files and has canonical descriptor-list SHA-256 `11bbf56c385a418d98f0baaaad3474211aac81d5d6147eb0b158a7979fdb070a`. Occurrence 3 alone records: “D-099 clause 5: the operating session streamed its own post-arm status output during the member idle gate.” Loader output flags are `[false, false, true]`.

- `salvage-closure.json`: SHA-256 `385bc45181df3af3a7e36e8bb44789b5864d32c189670bea9b05a4b7edff2024`, 27970 bytes; `load_salvage_closure` accepted all three occurrences and terminal index 2.

## Step 2 — null-identity membership binding

`load_authenticated_campaign_catalog` returned exactly eight records; all eight have `analysis_manifest_id: null` and the exact campaign-policy SHA above. The merged loader authenticated these descriptors exhaustively:

| Manifest path (runs-root relative) | SHA-256 | Bytes |
|---|---|---:|
| `campaign_manifests/campaign-20260801T092509091193Z-p53702.json` | `159e9e7d820773ef86b5ac2d53d3d25ab7c41052ab0f8fa45c81033f57472a60` | 35995 |
| `campaign_manifests/campaign-20260801T093528169564Z-p54042.json` | `1c32890879582bb926dd54b301f77e412666e45934027a95092de472f16e598f` | 248619 |
| `campaign_manifests/campaign-20260801T104658893526Z-p56481.json` | `2d3963b94f554c540e93f14771bc9b683caf8f1ebfc9c2b7e04f758e35da3ff3` | 185943 |
| `campaign_manifests/campaign-20260801T113950593531Z-p58396.json` | `f00cfc87fea531513bc1ba4cb582eff80c60e71280582111b91cf4a00e383e79` | 85931 |
| `campaign_manifests/campaign-20260801T120323605152Z-p59069.json` | `765eefcccb2ff87462998174a247d8e65645a66288040e1b6dba252caf9ac170` | 11057 |
| `campaign_manifests/campaign-20260801T120835813415Z-p59214.json` | `7c2daa8a2bee20f01d04670217e5c01b583a4c7ed09767746d5b75c612b2bcb6` | 298345 |
| `campaign_manifests/campaign-20260801T132123643876Z-p61920.json` | `d64ce771c146daf3ef0a6418a6b629bd5060c88eacc297c3afce055730dcd45d` | 30393 |
| `campaign_manifests/campaign-20260801T133709453934Z-p62245.json` | `4698a34edfebfb17d583dbd4207cb088d46c564f7cba3d5f20bd8520e72389ea` | 35862 |

- Derived `membership_id` (canonical SHA-256 of the sorted descriptor array): `c5f5c793a4188b79926fc3b73e2cd5a229fea2785a866b815f8028b87d9638af`.
- `membership-binding.json`: SHA-256 `349d5d260800662976cf38317c6af2a59b6000a55de13d5cf12a9d05484e76c5`, 1870 bytes; `load_window_membership_binding` accepted it as exhaustive/authenticated.

## Step 3 — repaired-tool license verification

Lead bank compared: `/Users/edr/code/JouleWise/.desk/coldgate_d100_bii/d108-clause-d-rerecord.json` (file SHA-256 `4eb06ee9507077d9791f1f85371bc1192f6f73b6e475bd0d141451cc92dbf5e5`, recorded tool head `32d72fda092be9a40b51af96737143b12d9b1a08`). Current tool head is `0e40111ca6f498d167a71b66b5069d988b9bb9bb`.

| Subject | Licensed | Bank-format manifest SHA-256 | Inspect result exact | Per-file SHA map exact | Count exact |
|---|---|---|---|---|---|
| `mtnull-o0512-b04-b2__20260801T113258Z` | `true` | `105ca58322ef332c7bf54280b90ba486c5f83767bfe90b5d6b1e9f0368dff43d` | `true` | `true` | `true` |
| `mtadd-p2048o0128-r08__20260801T131705Z` | `true` | `5291b590b0202d1e4828831dd42978ccd299a5e8df49bf52341c28f5139e06bb` | `true` | `true` | `true` |
| `mtadd-p2048o0128-r08__20260801T133315Z` | `true` | `ee61bafa6421dfccd2e4b3dd2cead4cf79575b2b12b27ceb0bb1f51fcc65fcca` | `true` | `true` | `true` |

Subject set, all inspection fields, every per-file SHA-256, and all artifact counts exactly match the banked re-record. No divergence was found. The two r08 teardown tails are 0.17097949981689453 s and 0.13570380210876465 s; occurrence 1 is 0.06680440902709961 s. All are within the 0.250 s bound.

A read-only dry authorization using `authorize_salvage_dangler_exclusion` accepted one absent ID, `mtadd-p2048o0128-r08`, and returned:

- schema `joulewise.salvage_dangler_exclusion.v1`; disposition `whole_window_member_terminally_absent_salvage`; attempt count 3; membership ID `c5f5c793a4188b79926fc3b73e2cd5a229fea2785a866b815f8028b87d9638af`; `operator_deviations_flagged: true`.
- Staging-only payload SHA-256 `4107953947e9c9755c26d4864ccd6e4856ba9f831500666e03edb9e2cb8f215d`. This digest is path-bound to artifact descriptors and must be re-derived after the lead installs the unchanged artifacts in custody; it is not a custody-run payload pin.

## Step 4 — D-093 clause 4 supersession visibility

- Scan scope: `window_b_re_evaluation_preflight`; authenticated basis: current campaign-log SHA-256 `b0dd1c20f224b3428f7364514174c76b76c2e443830a27935b7e0275e6ce8cf8`.
- Raw recognizable supersession records: **1**. Validated supersession records: **1**. Status: **clean**.
- The counts do not diverge; the void/stop condition did not fire.

## Step 5 — frozen corpus

- `campaign_log.jsonl`: SHA-256 `b0dd1c20f224b3428f7364514174c76b76c2e443830a27935b7e0275e6ce8cf8`, 1253770 bytes, 120 lines. Re-read after steps 1–4 produced the same SHA-256.
- Manifest set: the eight SHA-256/size descriptors in Step 2; canonical descriptor-set SHA-256 `c5f5c793a4188b79926fc3b73e2cd5a229fea2785a866b815f8028b87d9638af`.
- Original failed whole-window row: zero-index 119 / physical line 120; stored evaluation-basis SHA-256 `b00f8f7cc5bd0f210d5cc445137f3aa2b712aa3409abf54ac1b78a3a8a54be19`.
- Byte-identity replay against that original basis: 70 member occurrences, 210 config/metadata/summary files checked, plus 4 pre/post calibration evidence files; mismatch count **0**.
- No hand edits or writes were made to the corpus. These hashes are the pre-step-6 freeze pins; the lead-reserved verdict will append to the campaign log, so its post-run file hash is expected to differ while the recorded prefix/input hash remains this value.

## Commands and code surfaces

- Schema/loaders: `joulewise.salvage_dangler.load_salvage_closure`, `scripts.run_campaign.load_window_membership_binding`.
- Attempt checks: `joulewise.salvage_dangler.inspect_salvage_attempt` on all three quarantine paths.
- Dry authorization: `joulewise.salvage_dangler.authorize_salvage_dangler_exclusion` with the exact policy SHA, runs root, and one absent ID.
- D-093 scan: `joulewise.analysis_engine.inputs.supersession_visibility_scan` over the runs root with the campaign-log SHA-256 as authenticated basis.
- Step 6 was deliberately not invoked; no `--whole-window-verdict` command was run.

## Post-authoring verification

- `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_salvage_dangler`: **PASS**, 24 tests.
- `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests`: **FAIL**, 2443 tests, 1 failure, 85 skips. The sole failure is `test_gen_state.TestRefreshedStateFidelity.test_exact_live_id_set_59`: its tracked expected-ID set still includes retired `D100-BII-BINDING-01`, while the current state kernel does not.
- `PYTHONDONTWRITEBYTECODE=1 python3 scripts/gen_state.py --check`: **PASS**. A single-test replay reproduces the same expectation drift. `git diff --exit-code` is clean for tracked files, so this failure is a pre-existing exact-head baseline issue outside the three-file write scope and unrelated to the re-evaluation artifacts.
