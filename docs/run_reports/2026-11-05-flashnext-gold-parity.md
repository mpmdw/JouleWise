# 2026-11-05 — Qwen4 real-weight gold parity harness

LOCAL_ONLY — local commits requested; no push, PR, deployment or merge authorized.
Branch: `lane/2026-11-05-align-flashnext-gold-parity`.
Base: `origin/port/qwen4-exp-mlx`, `1643e9aac`.

## Scope and authority

Implemented GOAL items 5/11 tooling and the explicit task brief. Mission M0
found no active stop card. This is `[AGENT]` correctness tooling, not a quiet
measurement or a Block-5 analysis. The brief supersedes ordinary queue/kernel
bookkeeping and full-suite instructions: `RUN_STATE.md`, `TASK_QUEUE.md`,
`docs/process/state_kernel.json`, and `tests/test_gen_state.py` are untouched.
No study data, real `restricted/` directory, outside-repo `/Users/edr` path,
network, community PR #1788 code, or Block-5 pipeline was accessed. Git's
approved shared object alternates were used normally. No packages installed.

## Implementation

- Offline indexed safetensors slicing, meta-constructed single reference units,
  paged official expert storage, unique embedding rows, 1024-row head chunks,
  and sharded n-gram row gathers. Original checkpoint files remain untouched.
- Serial Torch/MLX subprocesses with identical immutable inputs, two compute
  threads, a 12 GiB aggregate budget, child RSS watchdogs, allocation preflights,
  bounded streamed coordinator comparisons, and required live MLX peak metadata.
- Both fp32/bf16, seeded random inputs with real-activation RMS when available,
  actual reference activations carried from embeddings through each layer,
  intermediate norms/streams/attention/router/MoE/PLE traces, exact expert-set,
  PLE-id and QSA-mask gates, and provisional fixed numerical tolerances.
- Durable per-case traces and incrementally published JSON/Markdown per unit,
  artifact hashes, immutable retry attempts, checkpoint/runtime/source identity,
  stat-guarded shard reads, and resume. Stub results cannot earn parity PASS.
- Standalone `--mlx-module` adapter contract, plus documentation for package
  wrappers, missing predecessor weights, QSA budget coverage and MBP execution.
- Tiny random bf16 checkpoint through official `save_pretrained`, and a separate
  bounded tiny full-model oracle to validate the streaming reference path.

Changed code: `joulewise/align/__init__.py`,
`joulewise/align/qwen4_gold/{__init__,core,reference,runner,worker,stub_adapter,tiny_oracle}.py`,
`scripts/run_qwen4_gold_parity.py`, `tests/test_qwen4_gold_parity.py`.
Changed docs: [gold_parity.md](../align/qwen4_exp_port/gold_parity.md), this report,
and [review/evidence records](2026-11-05-flashnext-gold-parity/).

## Verification

All numerical workers ran serially, with two compute threads. The full suite
was deliberately not run because the user forbade it while a seven-worker
analysis job was active. No pytest was used. Python 3.11 was not executed; new code targets 3.11/3.13, with only 3.13
verified in this session.

Commands below use `PYTHONNOUSERSITE=1 OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2
VECLIB_MAXIMUM_THREADS=2`; oracle execution also used offline HF flags.

```bash
/private/tmp/jwsol/venv-ref/bin/python -B -m unittest tests.test_qwen4_gold_parity
python3.13 -B -m unittest tests.test_qwen4_gold_parity
python3.13 -B -m compileall -q joulewise/align scripts/run_qwen4_gold_parity.py tests/test_qwen4_gold_parity.py
git diff --check

/private/tmp/jwsol/venv-ref/bin/python -B scripts/run_qwen4_gold_parity.py \
  --checkpoint /private/tmp/jwflash-gold-tiny-final \
  --output /private/tmp/jwflash-gold-selftest-final --make-tiny \
  --layers all --dtypes fp32,bf16 --input-modes random,real

/private/tmp/jwsol/venv-ref/bin/python -B -m joulewise.align.qwen4_gold.tiny_oracle \
  --checkpoint /private/tmp/jwflash-gold-tiny-final \
  --output /private/tmp/jwflash-gold-selftest-final

/private/tmp/jwsol/venv-ref/bin/python -B scripts/run_qwen4_gold_parity.py \
  --checkpoint /private/tmp/jwflash-weights \
  --output /private/tmp/jwflash-gold-real-final \
  --layers 2,3 --dtypes fp32,bf16 --input-modes random,real
```

The final real command includes endpoint probes; the incomplete real predecessor
chain is expected to block, and missing final mixer weights are expected to
produce reference errors for that endpoint. These failures do not suppress
available random layer/head or embedding cases. Exit 2 is required while using
an incomplete stub. Numerical output is never described as MLX parity.

Results:

| Check | Result |
|---|---|
| Reference-venv unittest module | 20 passed, about 1 second |
| Bare Python 3.13 unittest module | 20 discovered, 15 optional-dependency skips, 5 passed |
| Targeted compileall / Git whitespace | Passed |
| Tiny save_pretrained harness | 52/52 reference cases valid; all 52 candidate cases `STUB_NOT_VALIDATED`; expected exit 2 |
| Tiny full-model oracle | 24/24 passed; maximum fp32 absolute difference `5.960464477539063e-08`; all 12 bf16 comparisons bitwise equal |
| Resume | 52/52 cases reused, no numerical worker launched; expected exit 2 with stub |
| Real layer 2/3 random inputs | 8/8 reference probes succeeded (2 layers × 2 dtypes × 2 prompts); stub candidate withheld parity |
| Real embeddings / head | 4 embedding and 4 random-input head probes succeeded in reference; stub withheld parity |
| Missing-weight handling | 4 layer-0 attempts and 4 final-mixer random attempts failed explicitly; 16 requested real-input cases recorded as blocked in layer/endpoint reports |
| Worker RSS | Tiny peak `0.3273 GiB`; real peak `0.9344 GiB`; maximum coordinator peak `0.1064 GiB` |
| Live watchdog smoke | `execute(..., max_gb=.34)` terminated a fresh tiny-creation worker with exit 86 / `memory_guard`, as intended |
| Real n-gram row loader | Rows 0, 3, 17 of table part 0 (shape 3×160) decoded identically through Torch and NumPy BF16 slicing; max difference 0. This is a loader test, not full PLE or MLX parity. |

All nine present official shard files matched their supplied local sha256.txt
entries by the final run. The remaining 122 shards were absent. This checks
local file integrity, not independently authenticated download origin.
The final numerical runs used code commit `c9ca4edbb`. The subsequent commit
corrects explanatory tolerance prose and Markdown layout only: each bf16 allowance is four ULPs
near one, while the combined absolute-plus-relative bound is eight ULPs at
magnitude one (sixteen unit roundoffs). Numerical thresholds/calculations did
not change. Promoted Markdown includes that correction; JSON evidence remains
byte-identical to the original runs, with both source and promoted hashes.
Blocked-case reasons were moved below tables so report rows render consistently.
No numerical rerun was needed for these presentation corrections. The 1,519
committed ephemeral-artifact pointers and promoted-file hashes were verified.

Final machine-readable results and ephemeral artifact hashes are recorded in
[evidence.json](2026-11-05-flashnext-gold-parity/evidence.json).
Initial exploratory runs (`jwflash-gold-selftest`, `-v2`, and
`jwflash-gold-real`) remain in `/private/tmp`; they exposed HF unpacked expert
serialization and the sandbox's denied `ps`/Metal access. Final numerical evidence uses
the frozen `c9ca4edbb` sources and fresh output directories; the later prose-only
tolerance/layout correction is identified above.

## Review and check yield

The independent read-only native reviewer found six engineering issues; lead
fixed/dispositioned all of them. A delta review found no new blocking issue.
See [the disposition table](2026-11-05-flashnext-gold-parity/review.md) and
[invocation manifest](2026-11-05-flashnext-gold-parity/invocation_manifest.jsonl).
Task altitude: design-freedom implementation, judgment-call review. Outcome:
useful; the review caught parent memory exposure, absent Metal accounting,
checkpoint-buffer drift and false/incomplete coverage risks. Prompt defects:
none identified. Lead rework: approximately 25 minutes (estimate, not measured).
Final verification remained with the lead. No scientific number or study result
was touched; these checks protect engineering correctness and resource bounds.

## Local commits

- `c9ca4edbb` — `feat(align): add streamed real-weight qwen4 gold parity harness`.
- Follow-up commit — tolerance/layout correction plus verification, per-layer
  JSON/Markdown, artifact pointers, review dispositions and this report.

## Limits and next exact step

Neither Sol nor twin port ref was present in this clone at runtime; only the
base port branch and this lane were visible. Both harness runs used the
explicit NumPy stub. This sandbox cannot initialize Metal, even after selecting
MLX CPU. Real layer-2/3 **reference** execution is established; MLX parity is not.
The supplied download covers selected shards, not the layer-0/1 chain or all
48 layers. The final norm/mixer weights are on unavailable shard 00001.
The default fixtures are fixed numeric token sequences; before the MBP gold
run supply documented tokenization of the chosen fixed natural-language prompts.
Short real prompts do not exercise the 2048-token QSA budget; tiny prompts do
exercise truncation of their budget 4. BF16 bounds remain provisional until a
real adapter has been assessed; no observed failure was used to widen them.
Sampled RSS/Metal guards cannot replace an OS hard allocation limit or careful
adapter allocation behavior. Artifact files under `/private/tmp` are ephemeral;
committed hashes preserve their identity, not their long-term availability.

Next: each port implements the documented adapter, then an environment with
Metal reruns tiny gold and the available real layers. On the MBP, use all 131
bf16 shards plus fixed tokenized prompts and `--layers all --resume` for all 48
layers and endpoints. Stop/restart keeps the same output directory and arguments.
No coordination-state or kernel registration was made in this lane.
