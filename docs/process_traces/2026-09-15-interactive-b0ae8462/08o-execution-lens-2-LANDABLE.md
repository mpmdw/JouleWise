```json
{"schema":"claude-codex-report/v1","genre":"review","status":"clean","completion":"complete","summary":"LANDABLE: 638/638 real-signal cells, 4/4 F1 shell cells and 50/50 module tests pass.","workspace":{"base_requested":"d5ec18bb88590e07d60ce0078237ce31dd1b0101","base_mode":"exact","head_start":"d5ec18bb88590e07d60ce0078237ce31dd1b0101","head_end":"d5ec18bb88590e07d60ce0078237ce31dd1b0101","upstream_end":null,"branch":null},"pathspec":[],"unowned_dirty":[],"verdict":{"decision":"LANDABLE","findings":[],"verification_root":"/private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/exec-lens2-copy","next_step":"Lead adjudication at the pinned head."},"verification":[{"id":"V1","kind":"test","cmd":"python3 -B execution_lens2_probe.py --all","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["EXECUTION LENS 3.14.7: 316/316 PASS"]},"expected":{"exit_code":0,"tail_regex":"PASS"}},{"id":"V2","kind":"test","cmd":"/usr/bin/python3 -B execution_lens2_probe.py --all","cwd":".","observed":{"result":"fail","exit_code":1,"tail":["EXECUTION LENS 3.9.6: 150/316 PASS"]},"expected":{"exit_code":0,"tail_regex":"316/316 PASS"}},{"id":"V3","kind":"test","cmd":"python3 -B execution_lens2_repair.py","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["EXECUTION LENS 3.9.6: 316/316 PASS"]},"expected":{"exit_code":0,"tail_regex":"PASS"}},{"id":"V4","kind":"test","cmd":"python3 -B execution_lens2_pins.py","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["PINS WRITE: 6/6 PASS"]},"expected":{"exit_code":0,"tail_regex":"PASS"}},{"id":"V5","kind":"test","cmd":"python3 -B execution_lens2_aux.py --shell && /usr/bin/python3 -B execution_lens2_aux.py --shell","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["F1 shell cells: 2/2 PASS","F1 shell cells: 2/2 PASS"]},"expected":{"exit_code":0,"tail_regex":"PASS"}},{"id":"V6","kind":"suite","cmd":"python3 -B execution_lens2_aux.py --suite > execution-lens2-results/suite.log 2>&1","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["Ran 50 tests in 753.426s","OK"]},"expected":{"exit_code":0,"tail_regex":"OK"}},{"id":"V7","kind":"inspection","cmd":"python3 -B execution_lens2_finalize.py","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["638/638 real-signal cells; 4/4 F1 shell cells; 50/50 module tests PASS","Production source and test hashes unchanged; LANDABLE"]},"expected":{"exit_code":0,"tail_regex":"PASS"}}],"flags":[{"id":"F1","kind":"environment","level":"nonblocking","text":"V2 initially had 166 fixture-import failures before engine execution: the plan producer requires Python >=3.11. Fixture production and fence evaluation were moved to 3.14; engine and fake launchctl stayed on 3.9. V3 replayed all 166 successfully. All original tracebacks are preserved in AUDIT.md.","needs":""}]}
```

## Findings

No engine findings. Each cell checks the documented code, one teardown (uninstall: one verified bootout), SIG_IGN ×3, unchanged masks, file/liveness/fence invariants, and no escape. All 42 CLI cells had nonnegative exit codes. Counts include INT/TERM/HUP and applicable outcome variants.

| Seam | 3.14.7 | 3.9.6 |
|---|---:|---:|
| a_committed | 3/3 | 3/3 |
| a_last_mutation | 3/3 | 3/3 |
| after_ADMITTED | 3/3 | 3/3 |
| after_DEADMAN_LOADED | 3/3 | 3/3 |
| after_NIGHT_LOADED | 3/3 | 3/3 |
| after_PUBLISHED | 3/3 | 3/3 |
| after_STAGED | 3/3 | 3/3 |
| after_VALIDATED | 3/3 | 3/3 |
| after_VERIFIED | 3/3 | 3/3 |
| b_except | 3/3 | 3/3 |
| bootstrap_after_1 | 3/3 | 3/3 |
| bootstrap_before_1 | 3/3 | 3/3 |
| bootstrap_before_2 | 3/3 | 3/3 |
| c_unwind_entry | 6/6 | 6/6 |
| child_mask | 3/3 | 3/3 |
| cli_atexit | 6/6 | 6/6 |
| cli_main_return | 6/6 | 6/6 |
| cli_parse | 3/3 | 3/3 |
| cli_run_return | 6/6 | 6/6 |
| commit_clock | 3/3 | 3/3 |
| d_uninstall_entry | 3/3 | 3/3 |
| e_quiesce_1_after | 12/12 | 12/12 |
| e_quiesce_1_before | 12/12 | 12/12 |
| e_quiesce_2_after | 12/12 | 12/12 |
| e_quiesce_2_before | 12/12 | 12/12 |
| e_quiesce_3_after | 12/12 | 12/12 |
| e_quiesce_3_before | 12/12 | 12/12 |
| enter_ADMITTED | 3/3 | 3/3 |
| enter_DEADMAN_LOADED | 3/3 | 3/3 |
| enter_NIGHT_LOADED | 3/3 | 3/3 |
| enter_PUBLISHED | 3/3 | 3/3 |
| enter_STAGED | 3/3 | 3/3 |
| enter_VALIDATED | 3/3 | 3/3 |
| enter_VERIFIED | 3/3 | 3/3 |
| entry_protected | 3/3 | 3/3 |
| f_pair_entry | 2/2 | 2/2 |
| f_pair_pre_latch | 1/1 | 1/1 |
| f_pair_sequential | 1/1 | 1/1 |
| g_teardown | 6/6 | 6/6 |
| g_teardown_body | 6/6 | 6/6 |
| i_quiesce_entry | 9/9 | 9/9 |
| j_external_bootstrap_1 | 3/3 | 3/3 |
| j_external_bootstrap_2 | 3/3 | 3/3 |
| k_external_bootout | 3/3 | 3/3 |
| pep475 | 3/3 | 3/3 |
| pins | 3/3 | 3/3 |
| post_latch | 3/3 | 3/3 |
| post_quiesce | 9/9 | 9/9 |
| pre_latch | 3/3 | 3/3 |
| restore_prior_1 | 3/3 | 3/3 |
| restore_prior_2 | 3/3 | 3/3 |
| run_return | 6/6 | 6/6 |
| stage_after | 3/3 | 3/3 |
| teardown_bootout_1 | 3/3 | 3/3 |
| teardown_bootout_2 | 3/3 | 3/3 |
| teardown_print_1 | 3/3 | 3/3 |
| teardown_print_2 | 3/3 | 3/3 |
| u_bootout_after_1 | 3/3 | 3/3 |
| u_bootout_after_2 | 3/3 | 3/3 |
| u_bootout_before_1 | 3/3 | 3/3 |
| u_bootout_before_2 | 3/3 | 3/3 |
| u_print_after_1 | 3/3 | 3/3 |
| u_print_after_2 | 3/3 | 3/3 |
| u_print_before_1 | 3/3 | 3/3 |
| u_print_before_2 | 3/3 | 3/3 |
| u_remove_after_1 | 3/3 | 3/3 |
| u_remove_after_2 | 3/3 | 3/3 |
| u_remove_before_1 | 3/3 | 3/3 |
| u_remove_before_2 | 3/3 | 3/3 |
| validate | 3/3 | 3/3 |
| verify_after_1 | 3/3 | 3/3 |
| verify_after_2 | 3/3 | 3/3 |
| verify_before_1 | 3/3 | 3/3 |
| verify_before_2 | 3/3 | 3/3 |
| write_after_1 | 3/3 | 3/3 |
| write_after_2 | 3/3 | 3/3 |
| write_before_1 | 3/3 | 3/3 |
| write_before_2 | 3/3 | 3/3 |
| pins_write | 3/3 | 3/3 |
| F1 shell | 2/2 | 2/2 |

[Full audit: every seam and every superseded setup-failure traceback](/private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/exec-lens2-copy/execution-lens2-results/AUDIT.md).

## Residual risk

Fake launchctl only; no live launchd validation. Pre-handler startup and SIGKILL/SIGQUIT remain outside the protected transaction window.