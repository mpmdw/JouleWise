# 32k rung desk smoke — run plan, not executed

STATUS: DRAFT. This **loads both models** and is a desk feasibility smoke, not quiet-machine evidence. It may run while agents are active, but was **not run in this drafting seat**. Never use its watts as a claim or let it substitute for the 25G83/v4 acceptance. R-Q1(4) requires load, memory and duration before the registration is sealed; the admitted sources and context windows are in `configs/model_panels/qwen3_4bit.json:4-50`. Use scratch only under `/tmp/278ebc9e/`.

## Exact desk commands for the future operator

Run from this worktree at the same HEAD, Python environment and power policy planned for the night. The self-contained script below uses the local model path only; no download is allowed. It uses a deterministic **token-ID** prompt to avoid tokenizer-length ambiguity; its SHA-256 and full IDs must be replaced by the final pinned, thinking-off prompt array before sealing. The command is deliberately a provisional load/rate probe, not the final capture implementation.

```zsh
mkdir -p /tmp/278ebc9e/calnight-smoke
sysctl -n hw.memsize > /tmp/278ebc9e/calnight-smoke/physical-bytes.txt
sysctl vm.swapusage > /tmp/278ebc9e/calnight-smoke/swap-before.txt
sw_vers > /tmp/278ebc9e/calnight-smoke/os.txt
git rev-parse HEAD > /tmp/278ebc9e/calnight-smoke/head.txt
: > /tmp/278ebc9e/calnight-smoke/smoke.jsonl
for rep in 1 2 3; do
CALNIGHT_REP=$rep python3 - <<'PY' >> /tmp/278ebc9e/calnight-smoke/smoke.jsonl
import hashlib, json, os, resource, time
from pathlib import Path
import mlx.core as mx
import mlx_lm

panel = json.loads(Path('configs/model_panels/qwen3_4bit.json').read_text())
for entry in panel['entries']:
    model_id = entry['model_id']
    source = Path(entry['source'])
    assert source.is_dir(), ('local model absent', source)
    t0 = time.monotonic()
    model, tokenizer = mlx_lm.load(str(source))
    load_s = time.monotonic() - t0
    sampler = mlx_lm.make_sampler(temp=0.0)
    seed_id = tokenizer.encode('Calibration night pinned smoke.', add_special_tokens=False)
    assert seed_id
    for L in (512, 2048, 8192, 16384, 32768):
        prompt = (seed_id * ((L + len(seed_id) - 1)//len(seed_id)))[:L]
        assert len(prompt) == L
        prompt_sha = hashlib.sha256(json.dumps(prompt, separators=(',', ':')).encode()).hexdigest()
        original_eos = getattr(tokenizer, 'eos_token_ids', None)
        assert original_eos is not None
        tokenizer.eos_token_ids = set()
        try:
            started = time.monotonic()
            first_s = None
            emitted = 0
            for response in mlx_lm.stream_generate(model, tokenizer, prompt, max_tokens=512, sampler=sampler):
                emitted += 1
                if first_s is None: first_s = time.monotonic()
            ended = time.monotonic()
        finally:
            tokenizer.eos_token_ids = original_eos
        print(json.dumps({'rep':int(os.environ['CALNIGHT_REP']),'model':model_id,'L':L,'prompt_sha256':prompt_sha,
                          'load_s':load_s,'prefill_to_first_s':first_s-started if first_s else None,
                          'decode_512_s':ended-first_s if first_s else None,
                          'emitted':emitted,'max_rss_bytes':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
                          'metal_peak_bytes':mx.metal.get_peak_memory(),
                          'metal_active_bytes':mx.metal.get_active_memory()},sort_keys=True),flush=True)
        assert emitted == 512
    del model, tokenizer
PY
done
sysctl vm.swapusage > /tmp/278ebc9e/calnight-smoke/swap-after.txt
```

The MLX adapter's production path suppresses EOS around generation and pins greedy sampling (`joulewise/adapters/mlx_runtime.py:727-734,762-769,984-1029,1075-1093`). The operator must first confirm the installed MLX API exposes `make_sampler`, `metal.get_peak_memory`, and `metal.get_active_memory`; if an API differs, revise and cold-review the script **before running**, never silently remove memory measurement. The production prompt's 8192 sustained-preload repetition is separately timed by a second desk script built from the same pinned prompt and max_tokens=1; its active-prefill time, number of repeats and wall overhead go into the budget. Record process exit, stderr, OS build, HEAD, package versions, hashes and the raw JSONL. A failure is a no-go, not a missing row to interpolate.

## Go/no-go arithmetic

For each model use the observed rung prefill-to-first and decode-512 durations; the command performs **three repetitions** and records all rows, retaining the largest observed duration per rung and load. Require both peak Metal and peak resident memory individually to stay below **80% of physical RAM** and no MLX allocation error or swap growth; read `hw.memsize` and swap counters before/after without a quiet measurement. Require 32k+512 ≤40,960 context, exact 512 outputs, no tokenizer/EOS pin failure, and each model's measured total in `01-registration-draft.md` to fit **≤570 s** including 30 s initial idle, five ×30 s post-rung idle, ≥60 s active sustained prefill, 30 s final idle, the measured load and markers. The remaining ≥30 s is schedule margin. Require every 512 decode ≤50 s if the proposed ±0.10 W stopwatch band is kept.

If 570 s fails with five rungs, recompute after dropping **16384 first**. If still >570 s, drop **32768 next**. Publish the per-model arithmetic and physical memory reason; seal the same surviving rung set for all envelopes. If three rungs still fail, **NO-GO / NEEDS_RULING**. No 600 s envelope is stretched, no prompt is shortened in place, and no night is armed on a desk-only estimate. The desk check must also benchmark the logger's 0.5 s receipts and inspect whether the full payload can close within the driver's exclusive window (`scripts/run_night.py:684-710`).
