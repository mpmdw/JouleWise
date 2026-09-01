```json
{
  "schema":"claude-codex-report/v1",
  "genre":"review",
  "status":"findings",
  "completion":"complete",
  "summary":"REFUTE: the chain can authorize a v5-accepted pin from synthetic/unbound probe evidence, its probe workload differs from v5, and it silently misses R1/R2 registration requirements.",
  "workspace":{"base_requested":"bc19bfb6","base_mode":"exact","head_start":"d26e0472b1bdceda3129f7fbb0a4e7beb9f603c3","head_end":"d26e0472b1bdceda3129f7fbb0a4e7beb9f603c3","upstream_end":"d26e0472b1bdceda3129f7fbb0a4e7beb9f603c3","branch":"feat/2026-09-01-g2a-probe"},
  "pathspec":[],
  "unowned_dirty":[],
  "verdict":{"overall":"REFUTE","findings":[
    {"id":"B1","severity":"blocker","title":"Probe workload name differs from v5 workload_for(prefill)."},
    {"id":"B2","severity":"blocker","title":"Summarizer and issuer accept synthetic, unbound probe evidence and can yield a v5-accepted pin."},
    {"id":"B3","severity":"blocker","title":"R2 does not hash-bind the MLX greedy runtime."},
    {"id":"B4","severity":"blocker","title":"Issuer omits closing_sentence although R1.4 requires verbatim selected-rung fields."},
    {"id":"B5","severity":"blocker","title":"The R1-R4 ruling is absent from HEAD and the R2 wording is not exact."},
    {"id":"B6","severity":"blocker","title":"The checked campaign policy is not bound to the policy used by the bracket."},
    {"id":"B7","severity":"blocker","title":"Authentication guards lack mutation-catching tests."},
    {"id":"S1","severity":"should_fix","title":"prompt-corpus is a dead, unrecorded required input."},
    {"id":"S2","severity":"should_fix","title":"Runsheet omits issuer invocation and leaves operational terms undefined."}
  ]},
  "verification":[
    {"id":"V1","kind":"inspection","cmd":"PYTHONDONTWRITEBYTECODE=1 python3 scripts/gen_g2_phase_d.py --check","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["PASS generated Phase D matches pinned runbook bytes"]},"expected":{"exit_code":0,"tail_regex":"^PASS generated Phase D matches pinned runbook bytes$"}},
    {"id":"V2","kind":"test","cmd":"TMPDIR=/tmp PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_generate_g2a_probe_inputs tests.test_check_window_provenance tests.test_summarize_g2a_prefill_probe tests.test_issue_g2a_prefill_prompt_pin","cwd":".","observed":{"result":"fail","exit_code":1,"tail":["FileNotFoundError: [Errno 2] No usable temporary directory found in ['/tmp', '/tmp', '/var/tmp', '/usr/tmp', '/Users/edr/code/JouleWise-wt-probe']"]},"expected":{"exit_code":0,"tail_regex":"^OK$"}},
    {"id":"V3","kind":"lint","cmd":"git diff --check bc19bfb6..HEAD","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["(no output)"]},"expected":{"exit_code":0,"tail_regex":"^$"}}
  ],
  "flags":[
    {"id":"F1","kind":"baseline_drift","level":"blocking","text":"Required 16b ruling and scout exist at commit 80912c8d but are absent from HEAD; 80912c8d is not an ancestor of d26e0472.","needs":"Restore the registered ruling/scout or issue a replacement before acceptance."},
    {"id":"F2","kind":"verification_gap","level":"nonblocking","text":"Focused unit tests could not create a temporary directory in the read-only sandbox.","needs":"Rerun V2 in a writable test environment."}
  ]
}
```

## Findings

1. **B1 — BLOCKER:** The produced workload is not identical to `_v5`. The probe emits `name: "g2a_prefill_p{length}_diagnostic"` in [`generate_g2a_probe_inputs.py:480`](/Users/edr/code/JouleWise-wt-probe/scripts/generate_g2a_probe_inputs.py:480), while `_v5` emits `df_ph_prefill_p{PREFILL_LENGTH}_candidate` in [`generate_configs.py:1413`](/Users/edr/code/JouleWise-wt-probe/configs/campaigns/d117_contrast_v5/generate_configs.py:1413). All other workload fields agree. A default 512 member therefore violates R4 despite an otherwise valid prompt. Minimal fix: emit the exact `_v5` name.

2. **B2 — BLOCKER:** The evidence seam is not authenticated end-to-end. The summarizer accepts arbitrary self-hashed header files ([`summarize_g2a_prefill_probe.py:103`](/Users/edr/code/JouleWise-wt-probe/scripts/summarize_g2a_prefill_probe.py:103)), then extracts only `in_window_sample_count` from each unbound `summary_metrics.json` ([`...:248`](/Users/edr/code/JouleWise-wt-probe/scripts/summarize_g2a_prefill_probe.py:248), [`...:367`](/Users/edr/code/JouleWise-wt-probe/scripts/summarize_g2a_prefill_probe.py:367)). The issuer never accepts the inventory, config root, runs root, or an authenticated summary receipt; it takes only separately supplied selection, summary, and ladder paths ([`issue_g2a_prefill_prompt_pin.py:260`](/Users/edr/code/JouleWise-wt-probe/scripts/issue_g2a_prefill_prompt_pin.py:260)).

   Concrete failing input: five hand-written minimal `summary_metrics.json` files per small rung, each containing count `6`, plus a self-hashed synthetic inventory and a correctly tokenized alternate ladder. This produces a qualifying four-row summary and selection; the issuer accepts its self-consistent inputs, and `_v5` checks only pin-local fields ([`generate_configs.py:890`](/Users/edr/code/JouleWise-wt-probe/configs/campaigns/d117_contrast_v5/generate_configs.py:890)). Minimal fix: establish a bound run-result receipt, require the issuer to consume the inventory-bound ladder and receipt, and rederive/byte-compare the summary. This needs a registration ruling because the four-row selector input cannot itself carry provenance.

3. **B3 — BLOCKER:** R2’s greedy-runtime hash binding is absent. The ladder binds the panel hash, but the generated config contains only the literal tag `mlx-greedy-runtime` ([`generate_g2a_probe_inputs.py:497`](/Users/edr/code/JouleWise-wt-probe/scripts/generate_g2a_probe_inputs.py:497)). The T1 vector records `mlx_version` and a fiducial-protocol hash, not `mlx_runtime.py` or greedy sampler bytes ([`validate_powermetrics_fiducial.py:656`](/Users/edr/code/JouleWise-wt-probe/scripts/validate_powermetrics_fiducial.py:656)). Changing the adapter from temperature zero to non-greedy after build leaves `check`’s expected input bytes unchanged. Minimal fix: bind the adapter source hash in an existing config-bound field and have `check` regenerate it.

4. **B4 — BLOCKER:** R1.4 requires the pin to copy selected-rung fields including `closing_sentence` verbatim (16b-RULING, lines 53–58, absent from `HEAD`). The issuer returns text, hashes, IDs, repeat count, and generation method, but no closing sentence ([`issue_g2a_prefill_prompt_pin.py:318`](/Users/edr/code/JouleWise-wt-probe/scripts/issue_g2a_prefill_prompt_pin.py:318)). `_v5` accepts that omission because its closed schema lacks the field ([`generate_configs.py:833`](/Users/edr/code/JouleWise-wt-probe/configs/campaigns/d117_contrast_v5/generate_configs.py:833)). Minimal fix: obtain a ruling for a compatible loader/schema revision; silently adding the field would make `_v5` reject the pin.

5. **B5 — BLOCKER:** The stipulated R1–R4 ruling and scout are not on this branch; `HEAD` instead retains the older 08-30 authority path ([`generate_configs.py:88`](/Users/edr/code/JouleWise-wt-probe/configs/campaigns/d117_contrast_v5/generate_configs.py:88)) and the issuer requires that old path ([`issue_g2a_prefill_prompt_pin.py:249`](/Users/edr/code/JouleWise-wt-probe/scripts/issue_g2a_prefill_prompt_pin.py:249)). Further, the runsheet says “hash-bound—fixed by exact file fingerprints” ([`SHAKEDOWN-G2-RUNSHEET.md:260`](/Users/edr/code/JouleWise-wt-probe/docs/process_traces/2026-08-28-live-smoke/SHAKEDOWN-G2-RUNSHEET.md:260)), not the ruled replacement sentence. Minimal fix: restore 16b and its scout, then use the exact ruled R2 text.

6. **B6 — BLOCKER:** `bind-window` hashes the supplied campaign policy into inventory ([`generate_g2a_probe_inputs.py:913`](/Users/edr/code/JouleWise-wt-probe/scripts/generate_g2a_probe_inputs.py:913)), but `check` has no policy argument and only reopens that stored path ([`...:1125`](/Users/edr/code/JouleWise-wt-probe/scripts/generate_g2a_probe_inputs.py:1125)). The bracket later runs `$POLICY` directly ([`SHAKEDOWN-G2-RUNSHEET.md:390`](/Users/edr/code/JouleWise-wt-probe/docs/process_traces/2026-08-28-live-smoke/SHAKEDOWN-G2-RUNSHEET.md:390)). Binding with policy A, checking, then setting `$POLICY` to policy B runs mismatched inputs. Minimal fix: pass `$POLICY` to `check` and require its resolved path and SHA to equal inventory.

7. **B7 — BLOCKER:** Authentication guards have no mutation-catching tests. The generator’s live-vector/ledger authentication is mocked in the only producer test ([`test_generate_g2a_probe_inputs.py:117`](/Users/edr/code/JouleWise-wt-probe/tests/test_generate_g2a_probe_inputs.py:117)); no summary test mutates a top-level bound-file reference ([`test_summarize_g2a_prefill_probe.py:130`](/Users/edr/code/JouleWise-wt-probe/tests/test_summarize_g2a_prefill_probe.py:130)); and issuer tests replace real tokenizer authentication entirely ([`test_issue_g2a_prefill_prompt_pin.py:100`](/Users/edr/code/JouleWise-wt-probe/tests/test_issue_g2a_prefill_prompt_pin.py:100)). Minimal fix: add direct mutations for ledger/vector, bound path/SHA confinement, runtime-tokenizer SHA, ruling-trace, and inventory-to-issuer linkage.

8. **S1 — SHOULD-FIX:** `--prompt-corpus` is dead and should be removed. It is only read/count-checked ([`generate_g2a_probe_inputs.py:382`](/Users/edr/code/JouleWise-wt-probe/scripts/generate_g2a_probe_inputs.py:382)); the actual ladder is constructed solely from constants ([`...:400`](/Users/edr/code/JouleWise-wt-probe/scripts/generate_g2a_probe_inputs.py:400)) and neither schema records corpus path nor hash ([`...:76`](/Users/edr/code/JouleWise-wt-probe/scripts/generate_g2a_probe_inputs.py:76)). The runsheet’s “lead supplies” placeholder therefore blocks an artifact that cannot affect registration ([`SHAKEDOWN-G2-RUNSHEET.md:248`](/Users/edr/code/JouleWise-wt-probe/docs/process_traces/2026-08-28-live-smoke/SHAKEDOWN-G2-RUNSHEET.md:248)).

9. **S2 — SHOULD-FIX:** The runsheet never invokes `issue_g2a_prefill_prompt_pin.py`; it stops after selection ([`SHAKEDOWN-G2-RUNSHEET.md:507`](/Users/edr/code/JouleWise-wt-probe/docs/process_traces/2026-08-28-live-smoke/SHAKEDOWN-G2-RUNSHEET.md:507)). It also invokes “G1 assertions,” “estate 11,” “W-11,” “D-157,” and “S11/F-5” without commands or paths ([`...:491`](/Users/edr/code/JouleWise-wt-probe/docs/process_traces/2026-08-28-live-smoke/SHAKEDOWN-G2-RUNSHEET.md:491)). Minimal fix: add the issuer command, output variable, ruling trace, and explicit links/commands for those prerequisites.

## Ruling on the prompt-corpus observation

Remove it. It has no registration purpose: it affects only refusal, is absent from the ladder and inventory, and cannot be reconstructed from any later artifact. The producer’s actual R1 prompt is exclusively constant repeats plus the selected closing sentence.

## Mutation table

| Guard family | Catching test | Result |
|---|---|---|
| Length/member floors; output mismatch; config hash/cover | `test_fewer_than_five_small_members_refuses`, `test_zero_large_members_refuses`, `test_mutated_member_hash_refuses`, `test_unknown_stage_json_refuses` | Covered |
| Real panel admission, source-tokenizer hash, ledger snapshot, current identity/T1 | None; tests mock the latter two | **BLOCKER gap** |
| Summary member floor, run-ID/hash, extra config, missing summary | `test_fewer_than_five_small_members_is_hard_malformed_input_refusal`, `test_wrong_run_id_refuses_even_when_the_mutated_config_hash_is_rebound`, `test_altered_config_hash_refuses`, `test_extra_config_refuses` | Covered |
| Summary inventory header file binding, path confinement, schema/policy/plan authentication, raw-result provenance | None | **BLOCKER gap** |
| Issuer selection/summary consistency, rung ID retokenization, selected/no-clear branches | `test_bad_selection_and_summary_hashes_refuse`, `test_text_that_does_not_retokenize_to_stored_ids_refuses`, `test_unknown_length_malformed_branch_and_inconsistent_floor_refuse` | Covered |
| Issuer tokenizer-file SHA, ruling-trace, panel hash, inventory linkage, closing verbatim copy | None; tokenizer is mocked | **BLOCKER gap** |
| Selector row count/types, internal contradiction, reducer drift | `test_malformed_summary_emits_refusal_and_nonzero`, `test_internally_contradictory_summary_refuses`, `test_reducer_floor_drift_refuses` | Covered |
| Selector duplicate-key and exact `large_members` enforcement | None; selector ignores `large_members` | SHOULD-FIX |
| Generated bracket check-before-readiness/reservation | `test_runsheet_g2a_bracket_is_mechanically_bound_to_runbook` | Covered |
| Exact R2 sentence and issuer-runbook integration | None | SHOULD-FIX |

## Seam check

| Seam | Result |
|---|---|
| Binder → inventory | Schema names, eight-stage small-first order, relative member paths, and byte hashes align. `check` rebuilds expected configs and plans. |
| Inventory → summarizer | Key names and config-root-relative stage paths align, including SHA checks. Authentication of the inventory’s origin and run summaries does not. |
| Summarizer → selector | Emits the required four rows in ascending ladder order. Selector correctly chooses the shortest qualifying rung, but the rows carry no provenance. |
| Selector → issuer | Issuer recomputes the selection from the supplied summary and writes R3 `record_id = sha256:<selection-byte-hash>` ([`issue_g2a_prefill_prompt_pin.py:286`](/Users/edr/code/JouleWise-wt-probe/scripts/issue_g2a_prefill_prompt_pin.py:286)). It does not bind either input to the G2-a inventory. |
| Issuer → `_v5` loader | All emitted loader-required fields are satisfiable. `_v5` independently verifies text and token-ID hashes, but only requires a nonempty record ID/path and does not validate their relationship ([`generate_configs.py:890`](/Users/edr/code/JouleWise-wt-probe/configs/campaigns/d117_contrast_v5/generate_configs.py:890)). |
| R1 selected-rung copy | Fails: `closing_sentence` is absent from the pin. |

## Residual risk

`gen_g2_phase_d.py --check` passes; the generated bracket runs `check` before readiness/reservation; `$PYTHONPATH` is present for summarizer and selector; generated-bracket variables are defined. Focused tests were not executable in this read-only sandbox because no writable temporary directory is available.