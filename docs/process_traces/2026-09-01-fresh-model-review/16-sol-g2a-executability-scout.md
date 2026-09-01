```json
{
  "schema": "claude-codex-report/v1",
  "genre": "scout",
  "status": "findings",
  "completion": "complete",
  "summary": "G2-a is not executable from repository-produced inputs: no code emits the eight probe directories, their manifests/configs, the frozen G2-a plan, calibration identity vectors, or the post-selection prompt pin (SHAKEDOWN-G2-RUNSHEET.md:235-267; feat/2026-09-01-flowmap:docs/process/v5-artifact-flow.md:19-24).",
  "workspace": {
    "base_requested": null,
    "base_mode": null,
    "head_start": "bc19bfb6501f5b0dc88f23091e3e3d48865678a5",
    "head_end": "bc19bfb6501f5b0dc88f23091e3e3d48865678a5",
    "upstream_end": null,
    "branch": "feat/2026-09-01-g2a-probe"
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "rows": [
      {
        "row": "G2-a evening",
        "action": "do_not_start",
        "wait_for": "Generated and checked probe inputs plus the magistrate rulings below",
        "reason": "The runsheet calls the inputs lead-prepared, but its generated bracket only tests for manifests and consumes them; it does not build them (SHAKEDOWN-G2-RUNSHEET.md:256-267,414-422; scripts/gen_g2_phase_d.py:50-60)."
      },
      {
        "row": "Producer implementation",
        "action": "needs_ruling",
        "wait_for": "Prompt construction/workload semantics and G2-a record-id authority",
        "reason": "The current prompt-pin validator accepts supplied text and token IDs but does not tokenize the text, and no issuer exists (generate_configs.py:812-950; estate-12-delta-template.md:52-55)."
      },
      {
        "row": "Calibration custody",
        "action": "wait_for",
        "wait_for": "Live operator-controlled bracket only",
        "reason": "Pre/post custody is deliberately created by the live calibration writer after reservation, not by a desk producer (validate_powermetrics_fiducial.py:1732-1816,2178-2202)."
      }
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "inspection",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 scripts/gen_g2_phase_d.py --check",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "PASS generated Phase D matches pinned runbook bytes"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "^PASS generated Phase D matches pinned runbook bytes$"
      }
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_select_g2a_prefill_length tests.test_d117_contrast_v5_pack",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": [
          "FileNotFoundError: [Errno 2] No usable temporary directory found",
          "Ran 24 tests in 0.222s",
          "FAILED (errors=30)"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "^OK$"
      }
    },
    {
      "id": "V3",
      "kind": "inspection",
      "cmd": "git diff --exit-code && git status --short --branch",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "## feat/2026-09-01-g2a-probe"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "^## feat/2026-09-01-g2a-probe$"
      }
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "lead_ruling",
      "level": "blocking",
      "text": "The prompt corpus, four-length cutting rule, and whether G2-a measures the same raw-text workload later consumed by _v5 are not settled by an executable artifact (generate_configs.py:774-775,1404-1419,1626-1662).",
      "needs": "Issue R1 below."
    },
    {
      "id": "F2",
      "kind": "lead_ruling",
      "level": "blocking",
      "text": "Thinking-off and greedy generation are not literal BenchmarkConfig fields: thinking-off is in the panel, while greedy is enforced by the MLX adapter (qwen3_4bit.json:23-26; mlx_runtime.py:975-1023).",
      "needs": "Issue R2 below."
    },
    {
      "id": "F3",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "The focused unit suites could not create temporary directories under the read-only sandbox; the errors occurred before their test bodies.",
      "needs": "Rerun the exact V2 command in a writable test environment."
    },
    {
      "id": "F4",
      "kind": "residual_risk",
      "level": "blocking",
      "text": "For ordinary configs, run_campaign validates manifest membership but ignores order-manifest schema_version and config_sha256; frozen launch authentication activates only for marker-bearing pack configs (run_campaign.py:1854-1879,2999-3100).",
      "needs": "Install the proposed G2-a input checker before opening the bracket."
    }
  ]
}
```

## Ledger

Bottom line: the flow map’s finding is confirmed. `gen_g2_phase_d.py` renders the eight-directory loop but creates none of its inputs; repository search finds no other producer. `feat/2026-09-01-flowmap:docs/process/v5-artifact-flow.md:19-24`; `scripts/gen_g2_phase_d.py:50-60,103-188,287-310`.

Contract shorthand used below:

- **R**: the runsheet requires eight ordinary config directories, at least five small members per rung, at least one large member per rung, hashes preserved before reservation, and all four lengths. `docs/process_traces/2026-08-28-live-smoke/SHAKEDOWN-G2-RUNSHEET.md:256-267,414-422`.
- **A4**: every qualifying small rung needs at least five independently collected members and every member’s overlapping count must be at least five; large observations never gate. `docs/process_traces/2026-08-30-prefill-margin-coldgate/03-MAGISTRATE-RATIFICATION.md:53-62`.
- **SEL**: the selector consumes exactly four rows, requires `small_members >= 5` plus `all_small_count_ge_5`, and pins reducer floor 3/count floor 5. `scripts/select_g2a_prefill_length.py:16-24,53-108`.
- **RUN**: a directory must exist, all top-level JSON other than recognized sidecars becomes a config, the manifest must cover exactly those configs with contiguous indices, every config must pass `BenchmarkConfig`/doctor validation, and run IDs must be unique. `scripts/run_campaign.py:1844-1851,2999-3100,8012-8050,8097-8107`.
- **HASH**: current ordinary-manifest loading does not inspect `schema_version`, `config_sha256`, or manifest `run_id` agreement. The `_v5` generator is the closest correct hash-bearing builder. `scripts/run_campaign.py:3020-3064`; `configs/campaigns/d117_contrast_v5/generate_configs.py:1984-2000,3084-3115`.

### Probe matrix objects

| Object | Schema and validation | Producer | Required closure |
|---|---|---|---|
| `$G2A_CONFIG_ROOT/small-p512/` | No schema; `RUN` directory check | **NONE** | Must contain one manifest and the five-or-more member files below; closest layout builder is the `_v5` stage loop. `scripts/run_campaign.py:1844-1851`; `generate_configs.py:3084-3115`. |
| `$G2A_CONFIG_ROOT/small-p1024/` | Same | **NONE** | Same, for 1024. `SHAKEDOWN-G2-RUNSHEET.md:256-267`. |
| `$G2A_CONFIG_ROOT/small-p2048/` | Same | **NONE** | Same, for 2048. `SHAKEDOWN-G2-RUNSHEET.md:256-267`. |
| `$G2A_CONFIG_ROOT/small-p4096/` | Same | **NONE** | Same, for 4096. `SHAKEDOWN-G2-RUNSHEET.md:256-267`. |
| `$G2A_CONFIG_ROOT/large-p512/` | No schema; `RUN` directory check | **NONE** | One or more large-model members; recorded but non-gating. `03-MAGISTRATE-RATIFICATION.md:58-62`. |
| `$G2A_CONFIG_ROOT/large-p1024/` | Same | **NONE** | Same, for 1024. `03-MAGISTRATE-RATIFICATION.md:58-62`. |
| `$G2A_CONFIG_ROOT/large-p2048/` | Same | **NONE** | Same, for 2048. `03-MAGISTRATE-RATIFICATION.md:58-62`. |
| `$G2A_CONFIG_ROOT/large-p4096/` | Same | **NONE** | Same, for 4096. `03-MAGISTRATE-RATIFICATION.md:58-62`. |
| `small-p512/order_manifest.json` | Must say `joulewise.order_manifest.v1`; current runner validates only JSON shape, contiguous indices and exact config cover | **NONE** | Entries need `index`, `config`, `config_sha256`, matching `run_id`, model role, rung and repetition; new checker must authenticate every hash. `generate_configs.py:174,1984-2000`; `run_campaign.py:2999-3100`. |
| `small-p1024/order_manifest.json` | Same | **NONE** | Same, bound to 1024. |
| `small-p2048/order_manifest.json` | Same | **NONE** | Same, bound to 2048. |
| `small-p4096/order_manifest.json` | Same | **NONE** | Same, bound to 4096. |
| `large-p512/order_manifest.json` | Same | **NONE** | Same, with `model_role=large`; it remains outside the selector predicate. `select_g2a_prefill_length.py:60-90,102-107`. |
| `large-p1024/order_manifest.json` | Same | **NONE** | Same, bound to 1024. |
| `large-p2048/order_manifest.json` | Same | **NONE** | Same, bound to 2048. |
| `large-p4096/order_manifest.json` | Same | **NONE** | Same, bound to 4096. |
| `small-p512/g2a-small-p0512-r{01..05}.json` | Benchmark config `0.1`; doctor/`BenchmarkConfig.from_mapping` | **NONE** | At least five distinct files and globally unique run IDs; exact Qwen3-1.7B model pins; selected prompt text/length; one repetition and warmup; no `launch_lineage_required` tag. `joulewise/schemas.py:128-188,962-1015`; `03-MAGISTRATE-RATIFICATION.md:53-62`. |
| `small-p1024/g2a-small-p1024-r{01..05}.json` | Same | **NONE** | Same, exact 1024-token prompt. |
| `small-p2048/g2a-small-p2048-r{01..05}.json` | Same | **NONE** | Same, exact 2048-token prompt. |
| `small-p4096/g2a-small-p4096-r{01..05}.json` | Same | **NONE** | Same, exact 4096-token prompt. |
| `large-p512/g2a-large-p0512-r01.json` | Benchmark config `0.1` | **NONE** | At least one Qwen3-8B member; same prompt construction and runtime policy; its count is recorded but cannot affect selection. `03-MAGISTRATE-RATIFICATION.md:58-62`; `select_g2a_prefill_length.py:102-107`. |
| `large-p1024/g2a-large-p1024-r01.json` | Same | **NONE** | Same, exact 1024-token prompt. |
| `large-p2048/g2a-large-p2048-r01.json` | Same | **NONE** | Same, exact 2048-token prompt. |
| `large-p4096/g2a-large-p4096-r01.json` | Same | **NONE** | Same, exact 4096-token prompt. |

The closest reusable config builder is `_v5.config_for()`: it emits schema `0.1`, model, quantization, hardware, workload, interconnect, sampling and metadata, while `manifest_entry()` binds each member hash. `configs/campaigns/d117_contrast_v5/generate_configs.py:1916-2000`. The older P2-015 generator is the closest synthetic-prefill example: it puts `prompt_tokens=4096` directly in `workload_profile`. `configs/campaigns/p2_015_floors/generate_configs.py:92-100`; `configs/campaigns/p2_015_floors/02_phase_absolute/p2015-df-ph-prefill-abs-r01.json:24-51`.

### Common inputs and later objects

| Object or variable | Schema and validation | Producer | Executability finding |
|---|---|---|---|
| `$G2A_FROZEN_PLAN` | Current consumers require readable JSON, a string `.plan_id`, and exact byte hash; they do not require `joulewise.detection_floor_calibration_plan.v1`. `recover_calibration_ledger.py:383-402`; `calibration_ledger.py:4626-4647`. | **NONE** | Build a diagnostic `joulewise.g2a_probe_plan.v1` binding the ladder, models, prompt-ladder hash, eight manifests, policy, evidence-root ID, window/session IDs and non-claim status. |
| `$G2A_IDENTITY_EPOCH_JSON` | No schema ID; exact keys are `os_build`, `hardware_model`, `power_policy`, `sampling_interval_ms`, `estimator_revision`, `pulse_protocol_id`. `calibration_ledger.py:100-108,767-784`. | **NONE** | Closest code is the rehearsal/smoke extraction, but that merely copies a ledger row. `scripts/ed_session/build_rehearsal_env.sh:95-107`; `RUNSHEET.md:344-370`. A real producer should derive and validate the active acceptance epoch. |
| `$G2A_T1_BINDINGS_JSON` | No schema ID; exact `V2_BINDING_FIELDS`, including powermetrics hash, anchor method, MLX version and protocol hash. `powermetrics_fiducial.py:105-120`; `calibration_ledger.py:767-784`. | **NONE** | Reuse `_planned_t1_bindings`, which computes the exact vector used by the live writer. `validate_powermetrics_fiducial.py:656-667,1701-1709`. |
| `$G2A_WINDOW_PLAN_ROOT/prefill-prompt-ladder.json` | Proposed `joulewise.g2a_prefill_prompt_ladder.v1` | **NONE** | Latent required input if the probe and `_v5` are to use identical prompt text. It must hold four exact texts, token IDs, text/token hashes, tokenizer hash, corpus hash, construction method and prefix/cut evidence. |
| `$G2A_WINDOW_PLAN_ROOT/g2a-input-inventory.json` | Proposed `joulewise.g2a_input_inventory.v1` | **NONE** | Needed to implement the runsheet’s “hash and preserve every config” instruction because ordinary `run_campaign` does not check manifest member hashes. `SHAKEDOWN-G2-RUNSHEET.md:263-265`; `run_campaign.py:2999-3072`. |
| `configs/model_panels/qwen3_4bit.json` | `joulewise.model_panel.v1`; `load_model_panel` plus `_v5` pair checks | **NONE — tracked input** | Already supplies both model revisions, quantization, tokenizer/template hashes and thinking-off policy. `qwen3_4bit.json:1-68`; `generate_configs.py:991-1074`. |
| Small model source directory | External MLX mirror from panel line 8 | **NONE in repository** | Must contain a loadable local model plus `tokenizer.json` and `tokenizer_config.json`; the adapter verifies their pinned hashes before `mlx_lm.load`. `qwen3_4bit.json:5-25`; `mlx_runtime.py:85-125,230-307`. |
| Large model source directory | External MLX mirror from panel line 41 | **NONE in repository** | Same requirement for Qwen3-8B. `qwen3_4bit.json:38-58`; `mlx_runtime.py:85-125,230-307`. |
| `$POLICY` | `joulewise.campaign_policy.v1`; closed typed parser | **NONE — tracked input** | Existing `quiet_mac_p2_production.json` is sufficient; it requires production calibration bracketing. `quiet_mac_p2_production.json:1-52`; `joulewise/schemas.py:635-722`; `run_campaign.py:918-928`. |
| `$POWER_POLICY=ac_high_power` | No file and no schema; it is a string identity | **NONE required** | The runsheet passes the ID to calibration and collection. The calibration evidence/T1 vector binds it and reduction compares it with runtime observation. `SHAKEDOWN-G2-RUNSHEET.md:208,322,375`; `validate_powermetrics_fiducial.py:2130-2153`; `reduce.py:1651-1704`. |
| `$CALIBRATION_LEDGER` | `joulewise.calibration_observation_ledger.v1`; authenticated against head pin | Initial producer `scripts/calibration_ledger_bootstrap.py:515-531`; live append producer `scripts/validate_powermetrics_fiducial.py:1748-1762,2221-2245` | Must already exist at its reviewed head before reservation. `calibration_ledger.py:1973-2045`. |
| `$LEDGER_HEAD_PIN` | Exact keys `sequence`, `head_digest`, `ledger_schema` | Producer `scripts/recover_calibration_ledger.py:469-482`, writer in `calibration_ledger.py:4955-5042` | Must be the committed reviewed head; G2-a deliberately stops physical-ahead after post calibration. `SHAKEDOWN-G2-RUNSHEET.md:424-437,487-504`. |
| Active D-079 acceptance artifact | `joulewise.calibration_acceptance_bound.v2` | **NONE — issued tracked input** | The live writer requires the active r6 artifact, verifies its role, protocol/code hashes and identity epoch. `calibration_bracketing.py:163-176`; `validate_powermetrics_fiducial.py:364-434`; `calibration_acceptance_d079_v2_n17_r6.json:1-27`. |
| `configs/calibration/powermetrics_fiducial/protocol_v3.json` | `joulewise.pulse_fiducial_protocol.v3` | **NONE — tracked input** | The writer validates its fields against executable constants before capture. `validate_powermetrics_fiducial.py:124-129,936-943`; `protocol_v3.json:1-39`. |
| `$REPO`, `$PY`, harness scripts and host tools | No shared schema | **NONE — checkout/venv/OS supply** | Required scripts are `validate_powermetrics_fiducial.py`, `recover_calibration_ledger.py`, `reserve_calibration_window_bracket.py`, `run_campaign.py`, and later `select_g2a_prefill_length.py`; exact invocations are in the runsheet. `SHAKEDOWN-G2-RUNSHEET.md:309-328,359-404,496-504`. |
| `$G2A_EVIDENCE_ROOT_ID` | No file; nonempty scalar in reservation identity | **NONE** | Reservation validates it as a nonempty session-identity field and writes it into the bracket receipt. `calibration_ledger.py:751-764,4108-4131`. Bind it into the proposed frozen plan/inventory. |
| Pre custody path `$G2A_RUNS_ROOT/instrument_validation/$G2A_PRE_ATTEMPT_ID` | `instrument_evidence` v1 plus `instrument_validation_manifest.v1` and governed raw files | Live producer `validate_powermetrics_fiducial.py:1732-1816,2178-2202` | **Not a pre-open object.** Its exact path is reserved first and should not already contain custody; the writer creates it with `exist_ok=False`. `calibration_ledger.py:4133-4151`; `validate_powermetrics_fiducial.py:1815-1819`. |
| Post custody path `$G2A_RUNS_ROOT/instrument_validation/$G2A_POST_ATTEMPT_ID` | Same | Same live producer | **Not a pre-open object.** It is produced only after all eight stages. `SHAKEDOWN-G2-RUNSHEET.md:400-424`. |
| Each `$G2A_RUNS_ROOT/<run_id>/summary_metrics.json` | Summary schema `0.1` | `run_campaign` through bundle finalization; physical write at `joulewise/bundle.py:1167-1194` | The later jq requires `.window_evidence_precheck.phase.prefill.windows[0].in_window_sample_count`. `SHAKEDOWN-G2-RUNSHEET.md:449-459`; `reduce.py:956-1031`. |
| `d166-prefill-overlap-counts.jsonl` | No schema ID | **NONE as script; inline runsheet jq** | Contains rung, run ID, role, overlap count and count-minus-three. `SHAKEDOWN-G2-RUNSHEET.md:441-462`. A scripted reducer should authenticate manifests/config hashes before writing it. |
| `d166-prefill-resolvability-summary.json` | Four-row array, no schema ID | **NONE as script; inline runsheet jq** | Must contain `length`, `small_members`, `large_members`, `small_minimum_count`, `all_small_count_ge_5`. `SHAKEDOWN-G2-RUNSHEET.md:463-478`; `select_g2a_prefill_length.py:53-95`. |
| `d166-prefill-selection.json` | `joulewise.g2a_prefill_selection.v1` | `scripts/select_g2a_prefill_length.py:155-200` | Existing producer is sufficient. It selects the shortest qualifying rung or records collect-at-4096 refusal. `select_g2a_prefill_length.py:98-136`. |
| `d166-prefill-selection.json.sha256` | Plain SHA-256 sidecar | **NONE as script; inline runsheet command** | Produced on desk day after selection. `SHAKEDOWN-G2-RUNSHEET.md:496-504`. |
| `$PREFILL_PROMPT_PIN` | Closed `joulewise.prefill_prompt_pin.v2`; validated by `_load_prefill_prompt_pin` | **NONE** | This is post-evening, not a bracket precondition. It must bind the ladder, floors, selection expression, split refusal, G2 record hash/path/ruling, selected or collection length, tokenizer hash, exact prompt text/IDs/hashes, repeat count and method. `generate_configs.py:812-950`; `d117_contrast_v5.md:99-108`. |
| `$G2A_LOG` and terminal-boundary JSON | Campaign log has no single wrapper schema; terminal object comes from session-status | `run_campaign.py` and `recover_calibration_ledger.py` | Live outputs. Terminal jq requires finalized session, physical-ahead pin relation, head-mismatch refusal and a candidate. `SHAKEDOWN-G2-RUNSHEET.md:424-437`. |

### Exact small-model member pins

| Required pin | Existing expression | Finding |
|---|---|---|
| Qwen3-1.7B 4-bit revision | `model.name`, `model.source`, `model.revision`, `model.weight_format`; quantization is the config’s `quantization` object. The authoritative revision is `3b1b1768f8f8cf8351c712464f906e86c2b8269e`. `qwen3_4bit.json:5-17`; `generate_configs.py:782-805,1967-1981`. | Directly expressible and runtime-loadable. |
| Thinking disabled | Panel entry and rendering pinset carry `enable_thinking: "false"`; the panel validator enforces that pinset value. `qwen3_4bit.json:23-26,71-81`; `model_panel.py:405-423`. | **Not present in the member config schema.** `_model_config()` deliberately omits it. `generate_configs.py:782-805`. |
| Greedy decode | MLX adapter constructs a temperature-zero greedy sampler and fails if it cannot pin the sampler. `mlx_runtime.py:975-1023`. | **Not a member config field.** The config only selects the MLX runtime and output-token budget. |
| Prompt length | Synthetic configs can use `workload_profile.prompt_tokens`; `_v5` instead embeds `prompt_text` and adds a `prompt-tokens=N` metadata tag. `schemas.py:169-182,286-304`; `generate_configs.py:1404-1419,1916-1924`. | A raw-text config cannot also carry `prompt_tokens`; the sources are mutually exclusive. Exact length therefore needs producer-time tokenization plus a hash-bound ladder/checker. |
| Output budget | `_v5` prefill workload uses `output_tokens=512`, one repetition and one warmup. `generate_configs.py:1413-1419`. | Reusing this is a magistrate workload choice, not implied by the current G2-a runsheet. |
| Member hash/authentication | `_v5` manifests carry `config_sha256`. `generate_configs.py:1984-2000`. | G2-a needs a separate `check` gate because ordinary `run_campaign` does not consume that hash. `run_campaign.py:2999-3072`. |

## Producer design

### 1. `scripts/generate_g2a_probe_inputs.py`

One non-measurement producer with three subcommands:

- `build-probes --root "$G2A_ROOT" --panel configs/model_panels/qwen3_4bit.json --prompt-corpus PATH --small-members 5 --large-members 1`
- `bind-window --root "$G2A_ROOT" --ledger "$CALIBRATION_LEDGER" --head-pin "$LEDGER_HEAD_PIN" --campaign-policy "$POLICY" --power-policy ac_high_power --window-id ... --session-id ... --evidence-root-id ...`
- `check --root "$G2A_ROOT" --panel ... --ledger ... --head-pin ...`

`build-probes` should:

1. Validate the panel and require the exact small/large IDs, revisions, shared tokenizer hash, int4 quantization and thinking-off panel policy. The reusable checks already exist in `configure_model_pair()`. `generate_configs.py:991-1074`.
2. Tokenize the ruled source with the same raw-text mode used at runtime, including `add_special_tokens=True`. `mlx_runtime.py:931-940`.
3. Produce four exact text slices for 512/1024/2048/4096, re-tokenize every slice, require the exact count and token-ID prefix relation, and refuse when the corpus cannot supply the requested length.
4. Emit `prefill-prompt-ladder.json`.
5. Emit five small and one large config per rung, with globally unique run IDs, exact model pins, raw prompt text, output budget, sampling and diagnostic/non-claim tags.
6. Emit all eight `joulewise.order_manifest.v1` files with exact config cover and `config_sha256`.
7. Never add `launch_lineage_required`: G2-a is explicitly an ordinary diagnostic config family, while that marker requires a pack-root locator and authenticated pack inventory. `SHAKEDOWN-G2-RUNSHEET.md:256-264`; `arm_readiness.py:10478-10567,10576-10583`.
8. Refuse unknown JSON files inside a stage because `discover_configs()` would otherwise treat them as configs. `run_campaign.py:1844-1851`.

`bind-window` should:

1. Authenticate ledger/head and the active acceptance artifact.
2. Derive the current identity epoch and T1 vector using the same constants/helper as the writer.
3. Emit `identity-epoch.json`, `t1-bindings.json`, a diagnostic `calibration_plan.json`, and `g2a-input-inventory.json`.
4. Bind hashes of the panel, campaign policy, prompt ladder, all eight manifests and every config.
5. Write by create-new/atomic publication and refuse pre-existing mismatched outputs.

`check` should be read-only and run before reservation. It should re-read every byte, run `BenchmarkConfig.from_mapping`/doctor, verify no warnings, exact manifest schema and membership, hashes, run-ID agreement, global uniqueness, counts, roles, lengths, models and absence of the launch-lineage marker. The generated bracket should call this before the ledger readiness/reservation commands.

### 2. `scripts/summarize_g2a_prefill_probe.py`

CLI:

`--config-root "$G2A_CONFIG_ROOT" --input-inventory "$G2A_WINDOW_PLAN_ROOT/g2a-input-inventory.json" --runs-root "$G2A_RUNS_ROOT" --counts-output ... --summary-output ...`

It should replace the inline jq producer while preserving the selector’s existing four-row array shape:

- Authenticate the inventory, every manifest and member config.
- Require all four lengths and at least five small members per rung.
- Require at least one large member per rung, but never include large counts in qualification.
- Read exactly `.window_evidence_precheck.phase.prefill.windows[0].in_window_sample_count`.
- Emit every member count to JSONL.
- Set `small_minimum_count` and `all_small_count_ge_5` from the individual small members.
- A member with count 3–4 makes that rung non-qualifying; a count below 3 preserves the reducer-refusal distinction; fewer than five members is malformed input and exits nonzero. `03-MAGISTRATE-RATIFICATION.md:29-38,53-62`; `select_g2a_prefill_length.py:98-135`.

### 3. `scripts/issue_g2a_prefill_prompt_pin.py`

CLI:

`--selection-record PATH --summary PATH --prompt-ladder PATH --ruling-trace docs/process_traces/2026-08-30-prefill-margin-coldgate/03-MAGISTRATE-RATIFICATION.md --output PATH`

It should:

- Recompute and bind the selection-record and summary hashes.
- Use `.collection_prefill_tokens`, including the ruled 4096 no-clear branch. `SHAKEDOWN-G2-RUNSHEET.md:505-518`.
- Select the exact matching ladder entry.
- Re-tokenize `prompt_text` and compare the real IDs with the stored IDs; the current `_v5` loader does not perform this check because it deliberately does not consult a tokenizer. `generate_configs.py:812-815,916-942`.
- Emit the exact closed v2 field set accepted by `_load_prefill_prompt_pin`.
- Refuse a missing/short corpus, text-token mismatch, bad G2 hash, unknown length, malformed selection, inconsistent floor constants or an existing output.

### Tests

Proposed fixture-backed `unittest.TestCase` modules:

- `tests/test_generate_g2a_probe_inputs.py`
  - exact 5/1 × four-rung inventory;
  - fewer than five small members refuses;
  - zero large members refuses;
  - a length outside `{512,1024,2048,4096}` refuses;
  - prompt source shorter than requested length refuses;
  - panel revision/thinking/tokenizer mismatch refuses;
  - duplicate run IDs and mutated member hashes refuse;
  - generated configs pass doctor with no warning;
  - marker-bearing configs refuse.

- `tests/test_summarize_g2a_prefill_probe.py`
  - five passing small members qualify a rung;
  - one small member below five makes the rung non-qualifying;
  - fewer than five small members is a hard malformed-input refusal;
  - a large member below five does not gate;
  - missing summary, wrong run ID, altered config hash and extra config refuse;
  - exact four-row output is accepted by `select_g2a_prefill_length.py`.

- `tests/test_issue_g2a_prefill_prompt_pin.py`
  - all selected rungs and the 4096 no-clear branch;
  - prompt shorter than requested length refuses;
  - text that does not re-tokenize to stored IDs refuses;
  - bad selection/summary hashes refuse;
  - emitted object is accepted by `_load_prefill_prompt_pin`;
  - deterministic bytes and create-new refusal.

Recommended exact implementation `WRITE_SCOPE`:

- `scripts/generate_g2a_probe_inputs.py`
- `scripts/summarize_g2a_prefill_probe.py`
- `scripts/issue_g2a_prefill_prompt_pin.py`
- `scripts/gen_g2_phase_d.py`
- `docs/process_traces/2026-08-28-live-smoke/SHAKEDOWN-G2-RUNSHEET.md`
- `tests/test_generate_g2a_probe_inputs.py`
- `tests/test_summarize_g2a_prefill_probe.py`
- `tests/test_issue_g2a_prefill_prompt_pin.py`
- `tests/test_select_g2a_prefill_length.py`
- `tests/test_d117_contrast_v5_pack.py`
- `tests/test_check_window_provenance.py`
- `tests/fixtures/g2a/**`

If ruling R2 requires literal member-config fields rather than the recommended raw-prefill interpretation, also add:

- `joulewise/schemas.py`
- `joulewise/adapters/mlx_runtime.py`
- `tests/test_schemas.py`
- `tests/test_mlx_runtime.py`
- `tests/goldens/config_schema.json`

## Rulings needed

1. **NEEDS_RULING — prompt source, cuts and workload equivalence.**

   - Option A: use the `_v5` repeated-sentence construction already named by `PROMPT_SENTENCE`/`PROMPT_FINAL_SENTENCE`; create one 4096-token master and four exact re-tokenizable text prefixes; use those same texts in G2-a and the eventual pin.
   - Option B: concatenate/repeat the eight `real_prompts_v1` texts and cut exact prefixes.
   - Option C: use `workload_profile.prompt_tokens`, letting the adapter synthesize token IDs; issue an unrelated real-text prompt only after selection.
   - Recommendation: **A**. It is the only option aligned with `_v5`’s existing raw `prompt_text`, `repeat_count`, and generation-method contract. `generate_configs.py:774-775,1404-1419,1626-1662`. Option C is simpler but measures a different workload. `mlx_runtime.py:1187-1196`.

2. **NEEDS_RULING — what “thinking disabled and greedy pinned in each config” means.**

   - Option A: treat raw prefill text as bypassing chat-template thinking entirely; bind the admitted panel’s thinking-off policy in the prompt ladder/inventory, and rely on the MLX adapter’s fail-closed greedy sampler.
   - Option B: extend `BenchmarkConfig` with literal thinking/rendering/sampler fields and make the adapter validate them.
   - Option C: move G2-a to chat-rendered suite inputs; this changes the summary/evidence surface and is not recommended.
   - Recommendation: **A**, with runsheet wording corrected to “panel thinking-off policy plus MLX greedy runtime are hash-bound.” Current configs have no literal fields for either claim. `schemas.py:128-188`; `generate_configs.py:782-805`; `mlx_runtime.py:975-1023`.

3. **NEEDS_RULING — G2-a `record_id` used by the prompt pin.**

   - Option A: define it as `sha256:<selection-record-sha256>`.
   - Option B: require a lead-issued human-readable ID.
   - Recommendation: **A** because the selection artifact currently has no `record_id`, while the prompt-pin contract requires one. `select_g2a_prefill_length.py:109-136`; `generate_configs.py:890-915`.

The number of probe members is otherwise an engineering default: exactly five small and one large per rung is the smallest set satisfying A4. More members are allowed but increase live cost. `03-MAGISTRATE-RATIFICATION.md:53-62`.

## Estimate

Engineering estimate, excluding the live evening:

| Producer | Sol-hours |
|---|---:|
| `generate_g2a_probe_inputs.py` including prompt ladder, configs, manifests, plan, calibration vectors, inventory and checker | 9–13 |
| `summarize_g2a_prefill_probe.py` plus authenticated fixture reducer | 4–6 |
| `issue_g2a_prefill_prompt_pin.py` plus `_v5` integration tests | 4–6 |
| Generated-runsheet integration and provenance tests | 2–3 |
| Total | **19–28** |

No repository files were modified.