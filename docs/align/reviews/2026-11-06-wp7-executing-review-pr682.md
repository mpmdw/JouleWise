# WP7 verdict: PR #682, review range 83e2dac59..cda5716a1

Reviewer: Opus 5.5 (lead WP7 agent, with three Opus sub-reviewers covering the R0 path, the #666 rebuild and the cloud-Sol WP15/16/17/21 code). Executing review at cda5716a1.

## Verdict: ADMIT_WITH_FIXES

- **Merge and R0 desk checks: admit.** No BLOCKER or HIGH affects R0 or the anchor path.
- **R1 arming:** one HIGH (fails closed) and several MEDIUMs must be fixed first (list below).
- **Fix branch:** none pushed. The only HIGH needs an owner decision on the digest semantics, so a blind patch could still be refused (see H1).

## Ruling on the end_state stop order

**Keep the order as coded:** deadman > fault (runner.error) > thermal.incomplete (gate/hold timeout or deadman interval) > decode_budget > end_task > time_guard > context_limit > turn-token cut > turn count. The plan's listed order (thermal before runner.error) is rejected.

- **A fault invalidates the execution.** Thermal censoring is a protocol outcome of a valid execution. If faults were labelled thermal.incomplete:
  - the X2 censoring rate would be inflated by software defects;
  - fault triage would be hidden;
  - a fault can itself cause a gate timeout (dead collector), so the fault is the root cause.
- **The label does not change the run's outcome.** workload.py raises AdapterFailure on deadman or any fault whichever label wins.
- **Deadman outranks fault** because it is the governed member-level abort, and an interrupt can cause secondary faults.

## Findings

| Sev | Where | Failure scenario |
|---|---|---|
| HIGH (R1 only, fails closed) | scripts/align_v4_kit.py:121-124 and :186-192 vs thermal_gates.py:79-111 | `require_ready` refuses any policy with `window_reference`; `validate_gate_policy` requires it. So no filled R1 input can ever pass `--check`/prepare, and every gated spec is refused. The kit never assigns capture (member 5) or consume roles, and test_v4_kit.py:178 asserts the stripped form. The fix needs `source_config_sha256` defined against the bundle's config.json bytes, which nothing pins yet. Owner: WP15/16. |
| MEDIUM | workload.py:114-124 (EpisodeSpec validation) | A gate cell (`thermal.sensors`) is accepted with `deadman_s=None`, and the kit's X-G/Y-G members set no deadman. With sensors unobserved (dead collector), every G1/H waits the full 300 s cap, which can reach hours per member with no wall bound. Require `deadman_s` for gate cells, or confirm an outer member cap. |
| MEDIUM | scripts/night_chains/align_r1_rehearsal.zsh:25 | `exec` of the Python driver discards the zsh restore trap. A SIGKILL (run_night escalation after 30 s, or jetsam) during or after segment B leaves the Mac in High Power. The INT/TERM trap also does not exit. |
| MEDIUM | joulewise/align/r0.py:165 | `generated_rewrites` uses `append_result(strict=True)`. One stochastic off-spec echo call by D (T=1.0, 12 turns) marks B7 `fail`, and fail-fast stops R0 with no checkpoint verdict. `load_coherence` treats the same event as diagnostic. WP13 should pre-declare this as inconclusive/retry, or make it non-strict. |
| MEDIUM (label drift) | stop_precedence.py:39-52, used at workload.py:644 | The workload `stop_condition` and `token_budget.stop_reason` changed against 83e2dac59: an earlier-turn `turn_token_budget_reached:N` now outranks `turn_budget_reached`, and `endpoint_error`/`episode_error` became `runner.error`. Nothing reads these labels today, and anchors stop by time_guard. Desk end_state was restored in f40dabe93. |
| LOW | r0.py:225 / r0_mlx.py:94 vs align_v4_kit.py:233 | R0's xhigh rung passes no kwarg, but the kit passes `{"reasoning_effort":"xhigh"}`. The rendered bytes are identical but the policy hash differs, so the runbook's "effort in hashed policy" claim is false for xhigh. |
| LOW | r0_host.py:315; r0_runner.py:166-170 | `smc_source_commit` 58525031a does not contain the WP15 classifier, and `implementation_sha256` hashes no SMC file. `checkout_head` still pins the code. |
| LOW | r0_host.py:331-332 | The diagnostic `rank_response` runs before the classifier and can set the receipt to inconclusive. Practically unreachable on real captures. |
| LOW | r0_runner.py:128 | `--timeout` is not checked against the 2400 s SMC budget. On a kill, the GPU worker is orphaned for about 900 s (bounded). |
| LOW | r0_host.py:92-99 | QuietGuard argv match refuses a forking wrapper (`caffeinate -i python …`). This matters for the WP10 LaunchAgent design; it fails closed. |
| LOW | thermal_gates.py:270-272 | `drain_decode` walks nn.Module (a dict subclass) and evaluates the weights. It costs milliseconds per chunk inside decode, with no effect on tokens or RNG. |
| LOW | endpoint.py:293-299 / thermal.py:102-145 | `persist_interval` on the decode hot path contends with the Sidecar RLock held across SMC reads and fsync. |
| LOW | workload.py:383-401 | A non-Refused exception in `capture_reference` skips warmup but returns ok=True, so the member is measured without warmup. |
| LOW | thermal_gates.py:410-516 | A dead collector thread is never checked in `wait()`, so it surfaces as X4 or deadman instead of a fault. |
| LOW | thermal_gates.py:177-188 | A resealed captured→unobserved downgrade of the custody file is accepted. |
| LOW | align_v4_kit.py:84-85 | `fan_keys: []` counts as pending although the policy accepts it. |
| LOW | align_r1_rehearsal.py:180-185, 205 | `--synthetic` writes `r1_slots.json` into the repo by default, and slots are unvalidated beyond finiteness. |
| LOW | docs/align/r0_desk_runbook.md:133-140 | Still describes the superseded fitted rule as deciding R0 (WP4c doc update not done). |
| LOW (tests) | tests/align/test_r0_checks.py:354 | `patch.object(MlxBackend.__new__)` breaks test_r0_mlx when run in the same process. Per-module CI hides it. |

## Checked and found correct

- **The six (seven) omit-if-None EpisodeSpec fields.**
  - Serialization: `to_text` drops them when None, and `from_text` defaults them to None.
  - Counterbalance key: `execution_policy_projection` groups episodes the same way as the old key; it only decides grouping, in insertion order.
  - Anchors: configs a-e01..e04 in the v3 and v4 kits are byte-identical to 83e2dac59.
- **add_generation_prompt.** It is passed through all three render paths (XML, reasoning_content, JSON).
  - `rendered_prompt_length` and the prior-hidden scrub use True, matching generation.
  - The only False render is checkpoint boundary planning, which is off for D (limit 0).
  - The D3 budget `_Template` override still works.
- **WP2.** The default is None and is omitted when None. `hybrid_checkpoint_policy` treats None and 0 the same (off).
- **WP3 (54b8a624d).**
  - `mlx_runtime.py` is unchanged against 83e2dac59.
  - The prefill hook now sits on the stream wrapper. The prompt is positional `args[2]`, and the hook still runs inside the prefill phase.
  - With checkpoints off, the anchor path is the same.
- **f3e0d9a01.** The owner of `_generate.__self__` is the same object the old bound dispatch used, so the budget view gets the real tokenizer.
- **f40dabe93 and a0de7ad85.** Both are correct.
- **#666 rebuild.**
  - Hold intervals are split out of decode timing.
  - The drain runs before the entry stamp, and `resume_hold` is stamped once on every path.
  - The deadman is enforced inside the waits, and no journal write happens under an armed SIGALRM.
  - G0 uses the window reference, and G1/H use the G0 exit values.
- **R0 path.**
  - The WP14(a) classifier matches the ruling.
  - Hub symlinks: all 9 cases checked, including escape, loop and blobs-dir symlink refusals.
  - The flock is released on all paths, and nothing on this path touches Spotlight.
- **WP14(b) custody reader.** It refuses on all 7 tampering cases tried.

## Tests run

All runs used `nice -n 19` and Homebrew python3.13/3.14 unittest, with `TMPDIR=jw-wt/ci-rootcause-b6-tmp`. No MLX venv was found, so MLX-native tests were skipped and not run.

- **Lead:**
  - stop_precedence, decode_budget, history_rendering, xml_tool_calls, cache_checkpoint, measurement_core_boundary, pilot2: 86 tests OK (3 skipped).
  - budget_apple, apple_campaign, thermal_gate: 64 OK.
- **R0 sub-review:** 12 r0/smc modules, 108 tests, 1 error. The error is the order-dependent test bug above; `test_r0_mlx` alone passes 5/5.
- **#666 sub-review:** thermal_gate/sidecar/mlx/coverage/legacy, decode_budget, thermal_desk, hazards.test_temperature: 101 tests OK (3 skipped).
- **Sol-code sub-review:** v4_kit, window_reference_custody, registry_select, cli_registry_selection, r1_rehearsal, stop_precedence, thermal_desk, measurement_core_boundary, thermal_gate, pilot3_cache, smc_classifier_v4: 120 tests OK.

Repro scripts are in the session scratchpad: repro_kit.py, repro_stop.py, repro_nodeadman.py, repro_drain.py, inv_repro.py, repro_refusals.py.
