# Flash-Next streamed MLX conversion

**2026-11-18 · Sol 6.2 xhigh · Tier 1 · PROVISIONAL for real weights**

Mission M0 found a clean branch at main `2bb70e143`, with no remote branch, PR or active stop card for this seat. The lead's direct engineering assignment selected this work. Authority is [RL-182 §2 at `7ec51b1d9`](https://github.com/mpmdw/JouleWise/blob/7ec51b1d9/docs/research-audits/2026-11-10-fable/RESEARCH-LEAD-DECISIONS.md), the Flash-Next page's capacity estimates and the [canonical converter and module at PR #683 head `97d780d59`](https://github.com/mpmdw/JouleWise/tree/97d780d59).

## Conversion

`python3 scripts/align_stream_qwen4_exp.py JOB --port-checkout PORT --execution off-mbp --plan-only` prints the exact byte budget for the pinned revision before staging any weight payload. `JOB` is a new or resumable private directory with an existing parent. `PORT` provides the two content-pinned files from `97d780d59`. Use the port's MLX 0.31.2 and mlx-lm 0.31.3 environment with `huggingface_hub` available. Planning reads Hub metadata and exact safetensors header ranges into memory. It checks the shard count against the authenticated index and requires LFS SHA-256 metadata for all 131 shards.

After owner authorization, replace `--plan-only` with `--allow-official-download`. Use `--execution engineering` only from the lead's engineering queue entry. The flag declares the execution context. Queue admission, scheduling and close proof belong to the launcher. `maxfit` is the default 6-bit/group-64 recipe. `maxfit5` is available separately after a ruled fit failure. `bf16` is available for reference conversion. Each recipe uses its own job directory. Output appears at `JOB/artifact`, and the final JSON prints the artifact's manifest SHA-256 for external pinning.

The converter authenticates one staged shard at a time. It writes each tensor piece into its canonical shard or PLE file offset, syncs the output files, compares the written range hashes, commits the journal and releases the source file before requesting the next one. Split experts and PLE rows keep canonical ordering across source shards. Restart with the same arguments and directory. Resume checks committed ranges, continues a partial download by HTTP range, and replays only the unfinished source shard. The published v2 manifest adds the pinned source identity and a plain SHA-256, shape, dtype and byte range for each MLX tensor and the assembled BF16 PLE table. Use the canonical verified loader against the printed pin before any later measurement.

## Disk budget

Peak job allocation is the block-rounded sum of all planned final output files and the manifest, the largest pinned source shard, two complete journal allocations and 64 MiB of filesystem housekeeping headroom. Direct offset writes avoid a second copy of an output file. Pending manifests are renamed into the final inventory on the same volume. File lengths are bounded by the plan, and the converter checks the job's allocated blocks while the source file is still present. The free-space admission line adds 70,000,000,000 bytes for the 40 GB floor and 30 GB allowance in RL-182 §2.3. Resume credits allocated job files after validating their type, size and volume, and free space is rechecked before each transfer. This budget covers the job's files. Concurrent volume use and filesystem snapshots affect volume availability and belong to engineering admission.

## Verification and handoff

- Bare Python 3.13 ran the focused module with nine passing tests and one optional native test skipped. Coverage includes the bound, a fresh refusal one byte below the requirement, refusal after available space falls between shards, partial download resume, journal-commit resume, source and output corruption, and exact HTTP range handling.
- On the engineering MacBook Air, all ten focused tests passed in the pinned MLX environment. The streamed `maxfit` fixture matched every canonical payload file digest and tensor SHA-256, including packed experts, scales, biases and split PLE. It loaded with the canonical verified loader. The synthetic peak allocation bound was 68,030,464 bytes.
- Hosted CI owns the canonical full suite under `CANONICAL.md`. The PR remains in draft for Tier 1 cross-family review. This run used synthetic weights and performed no measured-span work.
- The next lead step is to review CI and route the draft for one cross-family review. Before an authorized internal-disk run, bind the command to the launcher for an `engineering` entry with a stated worst case, obtain the owner's transfer approval and run the metadata plan to check the actual free-space requirement. Live conversion and release gates remain open.
