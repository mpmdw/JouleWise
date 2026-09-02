```json
{"schema":"claude-codex-report/v1","genre":"review","status":"findings","completion":"complete","summary":"REFUTE: F1/F4/F5 are cured, but V2 still accepts a forged rule-shaped prompt pin, the receipt does not freeze all normative dependencies, and the contract invokes two absent producer CLIs.","workspace":{"base_requested":"285aaefe","base_mode":"exact","head_start":"aa2a7d89","head_end":"aa2a7d89","upstream_end":"aa2a7d89","branch":"feat/transfer-fiducial-01"},"pathspec":[],"unowned_dirty":[],"verdict":{"decision":"REFUTE","findings":[{"id":"A1","severity":"blocker","summary":"F2 remains incomplete: a rule-shaped, runtime-tokenized but manually forged prompt pin is still admissible; neither issuer nor prompt-ladder provenance is authenticated."},{"id":"A2","severity":"blocker","summary":"F3 remains incomplete: the receipt omits normative dependencies used by the fitter, including uncertainty validation and BenchmarkConfig parsing."},{"id":"C1","severity":"blocker","summary":"F6 remains incomplete: the contract's required summarizer and prompt-pin issuer do not exist at HEAD, so its procedure is not runnable from this contract/worktree."},{"id":"B1","severity":"should_fix","summary":"The runtime token-ID mismatch regression asserts only exit status, not its named refusal reason."},{"id":"C2","severity":"should_fix","summary":"Receipt regressions repeatedly run the expensive production pulse detector; the ~355-second unit cost is an avoidable test-fixture accident."},{"id":"A3","severity":"nit","summary":"Report 28's stated HEAD~ V1 source audit is inaccurate: fit_run and _run_binding_reasons changed as well as build_capture, although the resulting V1 behavior is restored to the cb9371aa baseline."}]},"verification":[{"id":"V1","kind":"inspection","cmd":"git diff --check 285aaefe aa2a7d89","cwd":".","observed":{"result":"pass","exit_code":0,"tail":[]},"expected":{"exit_code":0,"tail_regex":"^$"}},{"id":"V2","kind":"inspection","cmd":"grep -n \"for _ in range\\|bootstrap\\|n_resamples\\|iterations\" tests/test_transfer_fiducial.py joulewise/transfer_fiducial.py || true","cwd":".","observed":{"result":"pass","exit_code":0,"tail":[]},"expected":{"exit_code":0,"tail_regex":"^$"}},{"id":"V3","kind":"test","cmd":"PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_transfer_fiducial tests.test_transfer_fiducial_v2_plan","cwd":".","observed":{"result":"not_run","exit_code":125,"tail":["Not run: the read-only sandbox cannot provide the temporary-directory writes these tests require; magistrate bench evidence was supplied."]},"expected":{"exit_code":0,"tail_regex":"^OK"}},{"id":"V4","kind":"inspection","cmd":"git show main:docs/process_traces/2026-09-01-fresh-model-review/28-sol-fix-13-fiducial.md","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["## Verification notes","Their capture objects were exactly equal."]},"expected":{"exit_code":0,"tail_regex":"^## Change"}}],"flags":[{"id":"F1","kind":"environment","level":"nonblocking","text":"No unit test was run locally: this read-only seat lacks a writable temporary directory, while both target modules use TemporaryDirectory().","needs":"Use the already-run bench suite for dynamic confirmation."},{"id":"F2","kind":"baseline_drift","level":"nonblocking","text":"main advanced to 832a5ce3 during the audit; report 28 was read from that final main revision. HEAD and its upstream remained aa2a7d89.","needs":""}]}
```

## Findings

### A. Contract

| Source finding | Cure hunk and regression | Would fail on 285aaefe? | Delta disposition |
|---|---|---|---|
| F1 | `generate_plan.py:99-148` adds `--summary` and raw-byte digest comparison; `test_selection_summary_exact_bytes_are_authenticated` at `tests/test_transfer_fiducial_v2_plan.py:185`. | Yes: parent has neither argument nor comparison. | Cured exactly. |
| F2 | `generate_plan.py:205-235` adds record ID/path, method-form, and runtime-token checks; tests at lines 162, 334, 400. | Yes: parent admits the self-hashed synthetic pin. | Partial; see A1. |
| F3 | `transfer_fiducial.py:883-1059` hashes raw configs, receipt bytes, sidecar, wrapper/core/estimator; tests at `tests/test_transfer_fiducial.py:534,571,623`. | Yes: parent normalizes config bytes and lacks module/sidecar checks. | Partial; see A2. |
| F4 | `scripts/fit_transfer_fiducial.py:25-63,96-115` uses `O_CREAT|O_EXCL`; regression at `tests/test_transfer_fiducial.py:669`. | Yes: parent overwrites. | Cured exactly. |
| F5 | V2 dispatch at `transfer_fiducial.py:690-734,1185-1429`; CLI dispatch at `scripts/fit_transfer_fiducial.py:66-124`; V1/V2 regressions at `tests/test_transfer_fiducial.py:438,484,513`. | Yes: parent requires a receipt for V1. | Behavior cured. Relative to pre-round V1 baseline `cb9371aa`, V1 remains equivalent. |
| F6 | Contract changes at `docs/contracts/transfer_fiducial.md:3-75,231-381`; text-only regression at `tests/test_transfer_fiducial_v2_plan.py:226`. | Yes: expected new text is absent. | Partial; see C1. |
| F7 | Attack tests added throughout both target test modules. | Yes: the attacks are absent or accepted. | Partial; see B1 and the mutation table. |

| ID | Severity | File:line | What fails | Cure |
|---|---|---|---|---|
| A1 | blocker | `generate_plan.py:231-235` | The regex accepts any quoted strings and any count; it never verifies the R1 repeated-sentence construction or binds the pin to an authenticated prompt-ladder/issuer output. The positive fixture at `tests/test_transfer_fiducial_v2_plan.py:33-95` is manually constructed, not issued. | Authenticate the selected prompt-ladder entry and its inventory binding, then verify copied text, IDs, count, and method fields. |
| A2 | blocker | `transfer_fiducial.py:29-33,1237-1243,1001-1051` | Receipt hashing tracks only wrapper, core, and estimator. Changing `joulewise/uncertainty_evidence.py` or `joulewise/schemas.py` can alter fit admissibility after data without a receipt source-drift reason. | Freeze a closed source-dependency inventory for all verdict-relevant modules and test mutations of each. |
| A3 | nit | `transfer_fiducial.py:96,284,1090,1185`; `scripts/fit_transfer_fiducial.py:66,79` | Report 28 says only `build_capture` changed from `HEAD~`; `TransferFiducialRunFit`, `fit_run`, and `_run_binding_reasons` also changed. | Correct the audit note. The V1 branch itself restores `cb9371aa` behavior. |

V1 path changes from parent are `TransferFiducialRunFit`, `fit_run`, `_run_binding_reasons`, and `build_capture`; CLI definitions `_parser` and `main` also changed. The new V1 branch uses the original schema validator, normalized-config check, binding checks, no receipt, no dwell/calibration-order gates, and the original CLI requirements. That is behaviorally equivalent to `cb9371aa`, not source-identical to parent.

### B. Execution

| ID | Severity | File:line | What fails | Cure |
|---|---|---|---|---|
| B1 | should-fix | `tests/test_transfer_fiducial_v2_plan.py:377-398` | Runtime ID mismatch checks only `main(...) == 2`; it does not assert `prefill_prompt_pin_runtime_token_ids_mismatch`. | Assert the named stderr reason. |

## Mutation table

| Report-23 mutation | Fixed-head result / covering test |
|---|---|
| Recompute `summary_sha256` | Covered: `test_selection_summary_exact_bytes_are_authenticated`. |
| Reject synthetic/unruled provenance and retokenize | Still uncovered: no test rejects a forged but rule-shaped pin whose text is unrelated to its claimed construction. |
| Enforce ruled `record_id` | Covered: `test_prompt_pin_authority_and_runtime_mismatches_refuse`. |
| Refuse a collect-at-4096 record | Covered: `test_collect_at_4096_refusal_record_cli_is_refused`. |
| Pin-length guard | Covered with named reason: `test_prompt_pin_rung_and_tokenizer_mismatches_refuse`. |
| Tokenizer guard | Covered with named reason: `test_prompt_pin_rung_and_tokenizer_mismatches_refuse`. |
| Selection-record/pin digest join | Covered: `test_prompt_pin_authority_and_runtime_mismatches_refuse`. |
| Raw-byte `--check` comparison | Still uncovered: positive `check()` uses identical output only. |
| Replace exact config bytes with normalization | Covered: `test_receipt_binds_exact_config_and_receipt_bytes`. |
| Omit fitter-module digest | Covered: `test_receipt_binds_actual_wrapper_core_and_estimator_bytes`. |
| Omit exclusive receipt publication | Covered: `test_duplicate_and_concurrent_receipt_issuance_refuse`. |
| Delete dwell check | Covered: `test_v2_dwell_and_calibration_time_are_enforced`. |
| Delete plan SHA check | Covered: `test_receipt_binds_plan_calibration_and_rule_bytes`. |
| Delete calibration identity check | Covered: `test_receipt_binds_plan_calibration_and_rule_bytes`. |
| Delete calibration-before-run check | Covered: `test_v2_dwell_and_calibration_time_are_enforced`. |
| Delete missing-receipt guard | Covered: `test_v2_requires_receipt_while_v1_remains_receipt_free`. |

Three added mutations of new guards:

| Mutation | Guard / named reason | Named reason asserted? |
|---|---|---|
| Append one byte to the supplied summary | `selection_record_summary_sha256_mismatch` | Yes. |
| Forge `selection_authority.g2a_record.record_id` | `prefill_prompt_pin_record_id_mismatch` | Yes. |
| Return a different runtime token-ID vector | `prefill_prompt_pin_runtime_token_ids_mismatch` | No; only exit status is asserted. |

### C. Regression, pedagogy, cost

| ID | Severity | File:line | What fails | Cure |
|---|---|---|---|---|
| C1 | blocker | `docs/contracts/transfer_fiducial.md:37-43,248-296` | `scripts/summarize_g2a_prefill_probe.py` and `scripts/issue_g2a_prefill_prompt_pin.py` are absent at HEAD, so their parser/flag claim cannot be true and the contract cannot run from this worktree. D-167 is also absent from this branch’s `docs/decision_log.md`. | Merge the producer stream before claiming an executable procedure, or explicitly park these steps as unavailable dependencies. |
| C2 | should-fix | `tests/test_transfer_fiducial.py:571-667`; `powermetrics_fiducial.py:88,910-991` | Receipt tests run about 15 full ten-bundle captures, including six captures in the two three-mutation tests. That invokes roughly 300 pulse projections under the 165,000-cell production budget. | Keep one end-to-end detector test; mock or fixture `fit_run` for receipt-only source/hash mutations. |

No changed hunk is unrelated to F1–F7; the failed contract references are within the F6 cure itself.

First-use check: `[QUIET-MAC]`, receipt, sidecar, digest, V2, prompt pin, rung, and transfer are built or glossed adequately. `D-167`/`V5-NIGHTLY-G3-01` are not locally built, and “bracket-calibration variant” remains an unglossed pre-existing term. Existing generator, selector, fitter, validator, CLI-run, and backup flags match their parsers; the two missing producer scripts have no parser to match.

The requested bootstrap/resampling grep is empty in both target files. The cost is therefore not a necessary bootstrap count: it is repeated use of the governed production detector in receipt tests.

## Residual risk

Dynamic regression execution was not repeated in this read-only sandbox because the target tests require temporary-directory writes.

VERDICT: **REFUTE** — the fix round closes several concrete defects but leaves provenance, full program-version freezing, and contract runnability materially incomplete.