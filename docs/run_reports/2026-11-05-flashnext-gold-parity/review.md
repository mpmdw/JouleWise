# Independent read-only review

Native reviewer `/root/gold_review`, using the inherited caller model
(exact runtime model id not separately exposed). The reviewer reports no files
edited, tests run or numerical workers started. Lead retains verification and authority.

| Finding | Lead disposition |
|---|---|
| P1: coordinator can materialize whole head traces/fp64 copies outside worker guard | Fixed with `TraceFile` contiguous NPY streaming, chunked metrics, and random-input allocation preflight. No retained mmap pages. |
| P1: missing live `peak_mlx_bytes` treated as zero | Fixed; finite nonnegative metadata required for `GOLD_ADAPTER_KIND='mlx'`, or `MLX_ERROR`. |
| P2: persistent n-gram buffers regenerated instead of checkpoint-loaded | Fixed; exact I64 checkpoint buffers loaded natively with shape/dtype checks; missing buffers fail closed. |
| P2: layer aggregates appear only at full-run completion | Fixed; JSON/Markdown published after each case/block with explicit expected/completed counts. Incomplete coverage cannot earn PASS. |
| P2: canonical package-relative imports cannot load as standalone file | Documentation requires a standalone wrapper importing the port in its normal package context. Sibling imports from adapter directory work. |
| P2: full-48 flag did not check configured layer count | Fixed; config must also specify exactly 48 layers. |
| Delta advice: shard mutation can occur during hash or final read | Fixed; stat checked before/after hashing, before each access, and after worker execution; config/index digests checked in worker. |

Delta review found no new blocking issues in streaming comparisons, persistent
buffers, incremental coverage, full-48 checking or immutable case inputs.
The final shard-guard implementation follows the delta advice; lead checks it
with a targeted replacement test and final end-to-end runs. This review is
engineering evidence, not a hardware or model-parity certification.
