# PIPELINE-SMOKE-LIVE-01 command verification notes

Desk source verification began at repository head
`3cde678411c7bf24643dfc6d645495a8265769de`. The operator-selected
`REVIEWED_HEAD` must be the post-PR head containing `RUNSHEET.md`,
`preflight.sh`, and this file; preflight executes that reviewed copy from the
fresh smoke checkout.
No live, dry-run, freeze, arm, T-0, launch, campaign, sudo, powermetrics, or MLX
command was executed during this desk review. The only Python executions were
the four permitted `--help` invocations listed at the end.

`RUNSHEET.md` marks future flags or future authenticated inputs
**BLOCKED-UNTIL-CURE**. Such rows are proposals against a named smallest cure,
not claims that the current parser accepts them.

| Runsheet command | Flag set / operand set | Verification source |
|---|---|---|
| A1 `export …` | fresh checkout at `$SMOKE_ROOT/checkout`; generated pack below checkout under non-top-level-`configs/`; required post-PR `$REVIEWED_HEAD`; exact source interpreter `/Users/edr/code/JouleWise/.venv/bin/python`; `PYTHONPATH=$SMOKE_CHECKOUT` for every Python command; `_v9` candidate IDs | `.gitignore:6`; `arm_readiness.py:2723-2733,4202-4231`; task checkout ruling; generator identity enforcement at gamma `generate_configs.py:171-180` |
| A2 `preflight.sh` | reviewed absolute script path; consumes `REVIEWED_HEAD`, `SMOKE_CHECKOUT`, exact `PY`, and exact `PYTHONPATH`; `GIT_OPTIONAL_LOCKS=0` for Git probes and `PYTHONDONTWRITEBYTECODE=1` for Python probes; source-venv relock against smoke-checkout lock; smoke-checkout import origin; exact Git/branch/ps failure handling; governed `/usr/bin/powermetrics` and sudo argv | `preflight.sh`; `.gitignore:6`; `scripts/prewindow_check.sh:148-155` (private census is interim pending B5 shared-helper cure); `window_runbook.md:1705-1709`; `powermetrics.py:50`; `sampler-checklist.sh:69-75` |
| A3 `test/find`, `mkdir -p`, containment `case`, `git status`, `shasum` | before creation `$SMOKE_ROOT` contains exactly `checkout/`; checkout is clean at `$REVIEWED_HEAD` with exactly the checked-out local branch; all created destinations remain below `$SMOKE_ROOT` | Task checkout ruling and quarantine fence; Git status/branch forms from repository intake |
| A4 `cp` ledger/head | real canonical ledger and committed head pin copied into quarantine | `window_runbook.md:204-205,1360-1410` |
| A4 Python identity projection | last ledger row `identity_epoch` and `t1_bindings`; exact closed key sets; canonical JSON | `scripts/ed_session/build_rehearsal_env.sh:95-107`; `joulewise.calibration_ledger.IDENTITY_EPOCH_FIELDS`, `T1_FIELDS`, `canonical_json_bytes` |
| B1 gamma generator | current: `--output-root --pack-id --family-suffix --no-preserve-current-frozen-bytes`; future: `--n-blocks 1 --measurement-arm decode`; fixed_n derives from block count | current parser `configs/campaigns/d117_contrast_qwen25_1p5b_vs_7b_v3/generate_configs.py:2276-2306`; block-count serialization `:92-95,907`; future flags absent and therefore B2 |
| B1 1.5B floor generator | same current/future split | current parser `configs/campaigns/d117_floor_qwen25_1p5b_v3/generate_configs.py:2638-2655`; future flags absent and therefore B2 |
| B1 7B floor generator | same current/future split | current parser `configs/campaigns/d117_floor_qwen25_7b_v3/generate_configs.py:2860-2873`; future flags absent and therefore B2 |
| B2 Python family assertion | all three plans fixed_n=1; recursive generation_kind rejection; gamma single decode block has exact member `arm` order A/B/B/A and position order A1/B1/B2/A2; each authenticated floor plan/order/spec decode-only and exactly five members; adjacent spec SHA checked | D-158 R-3; D-160 R-2; gamma condition/member encoding `generate_configs.py:838-860,1478-1515`; floor plan/spec emitters at 1.5B `:2024-2027,2436-2440` and 7B `:2043-2047,2278-2281` |
| B2/C1/C2 local Git branch and commits | throwaway local branch based on `REVIEWED_HEAD`; generated/projected/frozen pack bytes committed under `$PACK_OUTPUT_RELATIVE`; never pushed | `arm_readiness.py:2723-2733,4202-4231`; lead checkout ruling; Git CLI |
| C1 `project_identity_pins.py freeze` ×3 | subcommand plus one positional `pack_root` | `scripts/project_identity_pins.py:23-38`; mutation and PASS boundary `:41-60` |
| C2 `generate_arm_readiness.py freeze` ×3 and mint-head capture | current: `--pack-root --measurement-checkout`; future authenticated diagnostic admission outside the byte-identical registry plus diagnostic GENESIS semantics (generation-1-equivalent, no predecessor); deliberately no publication-marker flags; after the last local commit capture exact `MINT_HEAD` and assert clean tree | `scripts/generate_arm_readiness.py:28-58`; proposed parser site `:36-73`; registry refusal `arm_readiness.py:4130-4133`; successor refusal `:7360-7363`; checkout-only gates `:2723-2733,4202-4231`; future admission/genesis cure absent and therefore B3/B8/B9 |
| D1 jq `plan_id` / SHA / `evidence_root_id` | derives values from generated bytes, not operator invention | `capture_t0_step.py:387-440` validates plan/environment identity; `:527-602` renders reservation from it |
| D1 `printf []` | one empty waiver array | `window_runbook.md:239-248`; run_campaign `--waivers` parser `run_campaign.py:681-684` |
| D1 `printf window.env` | exactly the 25 current keys and literal values; `wc -l == 25` | `scripts/capture_t0_step.py:84-112,236-245`; absence of `ARM_RECEIPT` and `LAUNCH_MANIFEST` is B6, not an omission |
| D1 stage-list production | before midpoint: exact two generated floor pack roots; after midpoint: exact gamma pack root | chain consumers `window_runbook.md:1684-1689`; `capture_t0_step.py:446-465` requires the reviewed chain before T-0 |
| D1 chain existence/SHA | complete reviewed `window-chain.zsh` must already exist; SHA recorded before D2 | `capture_t0_step.py:150-159,446-465`; chain source `window_runbook.md:1418-1709`; producer remains B6/T0-ENV-PARSER-UNIFY-01 |
| D2 `capture_t0_step.py` loop | step order `clock-reference`, `clock-disable`, `quiet-mac-prep`, `prewindow-check`, `ledger-readiness`, `ledger-reservation`; common `--pack-root --custody-root --window-plan-root` | choices/parser `scripts/capture_t0_step.py:41-49,905-923`; exact derived subprocess argv `:527-602`; ordering refusal `:608-666` |
| D3 arm | `arm --pack-root --arm-context <JSON object> --window-custody-root` | `scripts/generate_arm_readiness.py:65-73,91-103,141-147` |
| D3 verify | `verify --pack-root --arm-receipt` | `scripts/generate_arm_readiness.py:75-82,148-153` |
| E1 launch | `--pack-root --arm-receipt --arm-readiness-custody-root --launch-manifest`; no lifecycle event on physical launch | parser `scripts/launch_window.py:38-60`; execve path and FD handoff `:240-267`; `--help` excerpt confirms all four required flags |
| E2 lifecycle start/settle/completion | same four roots plus `--lifecycle-event {start,settle,completion}`; start additionally awaits B6/B9 supply | `scripts/launch_window.py:46-60,270-299`; `window_runbook.md:1486-1509,1650-1699` |
| E2 run stage | positional `config_dir`; `--runs-dir --log --campaign-policy --instrument-calibration-dir --instrument-power-policy --arm-quiet-mode --arm-countdown-s 20 --max-failures 1` | parser `scripts/run_campaign.py:660-719`; exact runbook function `window_runbook.md:1608-1630`; `run_campaign.py --help` excerpt |
| E2 protocol-v3 calibration | `--allow-live --arm-countdown-s 20 --sleep-display-before-capture --output-root --ledger --head-pin --session-id --slot --attempt-id --power-policy` | parser `scripts/validate_powermetrics_fiducial.py:1523-1603`; exact runbook `window_runbook.md:1548-1572` |
| E2 NEG-8 bound mint | `--derive-neg8-drift-bound --neg8-drift-bound-output --runs-dir` | `scripts/run_campaign.py:784-803`; `window_runbook.md:1670-1680` |
| F1 copy/cmp prospective bytes | copies exact plan/tree/manifest into distinct analysis custody and byte-compares | D-160 #217 addendum distinct-analysis-root ruling; finalizer containment `joulewise/analysis_manifest_v3.py:3276-3297` |
| F1 bracket builder | copies/cmp prospective inputs before invocation; binding output is `$RUNS_ROOT/bracket-binding.json`; all required current flags supplied | parser `scripts/build_bracket_binding.py:383-413`; pre-existing custody inputs `:420-440`; publication `:416-572` |
| F2 whole-window verdict | current verdict flags plus binding beneath exact `--runs-dir`; future `--calibration-ledger/--head-pin` route is shown and blocked | parser `scripts/run_campaign.py:734-760,784-803`; binding containment `:4884-4920`; default-ledger load `:4783-4812`; R-3′ order |
| F2 jq status | exact `.status == "passed"` | `window_runbook.md:1793-1816`; D-158 2026-08-28 PASS addendum |
| F3 spec derivation/SHA and extraction ×2 | each spec path and SHA comes from adjacent authenticated plan-tree fields; extraction supplies `--runs-root --spec --out --evaluation-basis-sha256 --consumption-semantics-id d078_minted_envelopes_v1 --hash-bundles` | floor generator plan-tree emitters at 1.5B `generate_configs.py:2436-2440` and 7B `:2043-2047`; parser `scripts/extract_detection_floors.py:48-114` |
| F4 aggregate floor mint | `--pinset --pinset-sha256 --v2-input-manifest --out --single-count-out --project-commit "$MINT_HEAD" --project-tree-state clean`; `MINT_HEAD` is captured after the final C2 local commit from a clean tree | actual-HEAD equality `scripts/mint_floor_artifact_generalized.py:3904-3910`; parser `:4031-4064`; missing tiny-family pinset/input producer is B7 |
| G1 finalizer | all nine required flags; binding is `$RUNS_ROOT/bracket-binding.json`; `--output-dir == --custody-root == $ANALYSIS_ROOT` | parser `scripts/finalize_analysis_manifest.py:23-39`; missing-input refusal `joulewise/analysis_manifest_v3.py:1329-1335`; H6 template `real-transaction-runbook.md:1366-1388` |
| G1 jq output | read finalizer stdout `.output` | finalizer success object `scripts/finalize_analysis_manifest.py:68-81` |
| G2 evidence-root derivation/analyze-claims | current exact two `--evidence-root ID=$RUNS_ROOT` mappings derived from plan trees; future `--calibration-ledger/--head-pin` route shown; no legacy mode | parser `joulewise/cli.py:2283-2319`; multi-root refusal `inputs.py:1230-1263,3001-3017`; default-ledger load `:3037`; H6 form `real-transaction-runbook.md:1393-1408` |
| S11 A1 Python | non-null science campaign manifests equal prospective `manifest_id` and exact-byte SHA | `estate11-assertions.md:11-25`; producer fields `run_campaign.py:3446-3470` |
| S11 A2 Python | `campaign_cooldown_evidence(runs_root, finalized.lineage.collection_manifest_id)` nonempty and covers selected bundle IDs | `estate11-assertions.md:27-39`; public helper `inputs.py:2043-2058`; exact ID filters `:2143,2191` |
| S11 A3 jq | no recursive `campaign_cooldown_evidence_missing` reason | `estate11-assertions.md:41-48`; reason append at `inputs.py:3461` |
| S11 A4 Python | exact NEG-8, start/midpoint/end reference, and both floor config identities each have a nonempty null-bound campaign manifest | `estate11-assertions.md:46-65`; producer `run_campaign.py:3446-3470` |
| S11 A5 Python | `^am-[0-9a-f]{64}$` and `calculate_manifest_id` equality | `estate11-assertions.md:69-75`; calculator `analysis_manifest_v3.py:374,622,702` |
| F5 cooldown Python | selected joined rows all have raw artifact descriptors | re-derivation `inputs.py:1982-2034`; D-160 F-5 |
| F5 whole-window Python | verdict passed; empty reasons; nonempty included bundle IDs from `contrasts[*].bundle_blocks` are a subset of evaluation basis | claim shape `artifact.py:44-53,175-200`; producer `analysis_engine/__init__.py:1804-1857`; passed basis requirement `window_runbook.md:1793-1816` |
| F5 runs-root jq | binding `.runs_root == $RUNS_ROOT` | builder equality inputs `build_bracket_binding.py:210-280,467-483`; D-160 F-5 |
| F5 supersession Python | `supersession_visibility_scan(...).status == clean` against whole-window basis | scan calls `inputs.py:3060-3102`; function at `inputs.py:1324` |
| DATA predicate Python | `assert_data_reason_only(artifact, expect_lock=None)` | exact helper name and non-smoke call shape `reason_kinds.py:71-131`; DATA set `:36-50` |
| no-marker `find` | no `d117_family_publication_v4.json` or family-marker name below quarantine; diagnostic admission must bypass, not traverse, the marker gate because the marker roster pins `pack_path == configs/campaigns/<pack_id>` | D-158 R-3; D-160 R-2; marker constant `arm_readiness.py:71`; marker roster path gate `:10735` |
| registry grep/hash | no `_v9` row and exact before digest still verifies | task quarantine fence; registry admission code `arm_readiness.py:4097-4145` |
| final Git status | no tracked or untracked checkout residue | task quarantine fence and preflight clean-tree requirement |

## Exact `--help` invocations executed

All ran from `/Users/edr/code/JouleWise-wt-live` with the task-owned temporary
directory:

```sh
TMPDIR=/Users/edr/code/JouleWise-wt-live/docs/process_traces/2026-08-28-live-smoke/.tmp /Users/edr/code/JouleWise/.venv/bin/python -m joulewise --help
```

Key lines: subcommand list includes `analyze-claims`; description is “derive
paired contrast and claim verdicts from frozen evidence.”

```sh
TMPDIR=/Users/edr/code/JouleWise-wt-live/docs/process_traces/2026-08-28-live-smoke/.tmp /Users/edr/code/JouleWise/.venv/bin/python -m joulewise analyze-claims --help
```

Key usage: `--analysis-manifest ANALYSIS_MANIFEST --runs-root RUNS_ROOT
[--evidence-root ID=PATH] --floor-artifact FLOOR_ARTIFACT --output OUTPUT
[--legacy-l1-mechanics]`.

```sh
TMPDIR=/Users/edr/code/JouleWise-wt-live/docs/process_traces/2026-08-28-live-smoke/.tmp /Users/edr/code/JouleWise/.venv/bin/python scripts/run_campaign.py --help
```

Key lines: collection accepts positional `config_dir`, `--runs-dir`, `--log`,
`--campaign-policy`, `--instrument-calibration-dir`,
`--instrument-power-policy`, `--arm-quiet-mode`, `--arm-countdown-s`, and
`--max-failures`; verdict mode accepts `--whole-window-verdict`,
`--whole-window-verdict-output`, `--bracket-binding`, and
`--neg8-drift-bound`. `--dry-run` was displayed but never invoked.

```sh
TMPDIR=/Users/edr/code/JouleWise-wt-live/docs/process_traces/2026-08-28-live-smoke/.tmp /Users/edr/code/JouleWise/.venv/bin/python scripts/launch_window.py --help
```

Key usage: `--pack-root --arm-receipt --arm-readiness-custody-root
--launch-manifest`, optional private `--lifecycle-event
{start,settle,completion}`, and optional confirmation path/digest pair.
