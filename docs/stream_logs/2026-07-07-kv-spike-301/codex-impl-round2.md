Built [scripts/spike_mlx_prompt_cache.py](/Users/edr/code/jw-spike301/scripts/spike_mlx_prompt_cache.py): one subprocess-orchestrated spike with `monolithic`, `prefill`, `decode`, and `run` subcommands, lazy MLX imports, deterministic prompt construction, persisted prompt IDs for resume, trim-by-1 boundary handling, offset assertions, token identity comparison, and cache-size prediction via the importable `joulewise.kv_size` helpers. I did not run MLX/model paths.

My judgment: the subprocess-per-stage design is genuinely airtight against accidental in-process state reuse because `run` invokes each stage with a fresh `sys.executable` process. Residual leak paths are OS page cache, model mmap/cache effects, filesystem cache, and possible MLX compiled-kernel caches; those can affect timings, but not the correctness claim, since the resume process reconstructs correctness only from `prompt_cache.safetensors` plus persisted prompt token IDs. I would not isolate this differently unless the goal were timing purity, in which case a reboot/container/cache-drop protocol would be relevant.

Smoke commands run:
- `python3 scripts/spike_mlx_prompt_cache.py --help` -> exit 0.
- `python3 scripts/spike_mlx_prompt_cache.py monolithic --help` -> exit 0.
- `python3 scripts/spike_mlx_prompt_cache.py prefill --help` -> exit 0.
- `python3 scripts/spike_mlx_prompt_cache.py decode --help` -> exit 0.
- `python3 scripts/spike_mlx_prompt_cache.py run --help` -> exit 0.
- `git status --short` -> exit 0; shows `?? scripts/spike_mlx_prompt_cache.py` plus existing untracked `docs/stream_logs/`, which I did not touch.