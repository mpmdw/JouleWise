I could not build `scripts/spike_mlx_prompt_cache.py` because the workspace is mounted read-only and `apply_patch` was rejected by the sandbox. I did verify that `joulewise/kv_size.py` exposes clean importable helpers, so the script should prefer that path over CLI parsing. My judgment: the requested subprocess-per-stage design is genuinely airtight against accidental Python/MLX in-process state reuse because `prefill` and `decode` run in different OS processes via `sys.executable`; residual leak paths like filesystem cache, mmap cache, or OS page cache can affect timings, but not the correctness claim of token identity from serialized cache state.

Commands run:
- `pwd && rg --files ...` failed because `rg` is not installed.
- `git status --short` could not produce useful status because read-only temp restrictions blocked Xcode cache writes.
- `find scripts -maxdepth 2 -type f`, `find joulewise -maxdepth 2 -type f`, `ls` succeeded.
- `sed -n ... joulewise/kv_size.py`, `scripts/generate_matrix.py`, `joulewise/cli.py`, `pyproject.toml`, `scripts/run_campaign.py` succeeded.
- `apply_patch` to add `scripts/spike_mlx_prompt_cache.py` failed: `writing is blocked by read-only sandbox`.
- I could not run `python3 scripts/spike_mlx_prompt_cache.py --help` or subcommand help checks because the script file was not created.