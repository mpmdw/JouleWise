# Block-5 r2-on result

- Host capacity: `nproc = 3`; run used `--workers 2`.
- Driver result: exit code `2` after `1180.602 s`; the wrapper itself exited `1` because the synthetic driver reported its bounded stop.
- Per-step wall time/status: `0` — `15.272 s`, ok; `1` — `317.060 s`, ok; `2` — `16.301 s`, ok; `3` — `0.750 s`, ok; `3b` — `552.745 s`, ok; `4` — `276.730 s`, alpha ok and beta ok; `5` — `0.034 s`, `unclassified_refusal`.
- Steps `8`, `6`, `9`, `9b`, `10`, and `11` were not run, as requested by `--stop-after 4`.
- No step before step 4 refused. The only driver refusal was the expected post-step-4 stop marker: raw code `synthetic_stop_after` at `step-codes.jsonl:8`.
- Step 4's two expected fail-closed cell lists are preserved verbatim in `failure-logs/0529-4-alpha.stderr.log:1` and `failure-logs/0530-4-beta.stderr.log:1`; both step-level statuses remained `ok`.
