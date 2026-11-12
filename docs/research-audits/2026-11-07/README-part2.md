# Research 2026-11-07, part 2: index

These are model-written research documents for Ed and the lead to triage. They are not decisions. Each document lists its own numbered decisions for Ed.

| Track | Document | Source branch |
|---|---|---|
| Our methodology against the literature: new experiments for the measurement Mac | [methodology-vs-literature.md](methodology-vs-literature.md) | `research/2026-11-07-methodology-vs-literature` (036c7402d) |
| Qwen-Next (qwen4_exp, Qwen3.8-Flash-Next) MLX port: what is achievable, and the upstream path | [qwen-next-port-upstream.md](qwen-next-port-upstream.md), with scripts in [qwen-next-port-upstream-scripts/](qwen-next-port-upstream-scripts/) | `research/2026-11-07-qwen-next-port-upstream` (617d366eb) |

## 1. Methodology against the literature

1. Our evidence discipline is ahead of the field. Our weak points are the measurement boundary and gain, and we are less weak there than the review seats said. BYTES already has a rest boundary, and the public known-bytes test puts about 76% of memory-traffic energy outside the rails.
2. Ideas are ranked by novelty times value, divided by cost. Ideas 2 and 3 come first. Both are desk-only, with registration deadlines of 12 Nov and D unblinding. The Mac nights follow in the order 1, 4, 6, 8, 7, 5, 9, 10. Idea 5 drops down the order because its bound of at most 0.05 %/°C is probably falsified and it costs about twice as much. Idea 7 drops because half of it can be answered from sealed BYTES data.
3. Verdicts: no idea is wholly refuted. Idea 10's κ-band headline is refuted by Dutta et al., who found κ from -0.1 to 1.2, and our proposed Qwen3-8B/0.6B pair raised energy. Ideas 5, 6, 8 and 9 and idea 1 parts (c) and (d) are partly anticipated. Ideas 2, 3 and 4 and idea 1 parts (a), (b) and (e) survive.
4. The checks force these changes:
   - Idea 3's time channel depends on the P_prefill/P_decode ratio, and a two-knob mixed attack must be registered.
   - Pilots 4-10 ran Qwen3-30B-A3B, so any 27B claim needs W1.
   - Idea 4 needs a resident arm, a concurrent pread arm and a page-cache purge.
   - Idea 8 needs an M3 Max Low Power GPU-frequency pilot first.
   - macOS 27 may block IOReport counters.
5. Upstream order: first the mlx-vlm D1 fix (f1e0f6673), then a verification package for mlx-lm #1788, then a PR for #1924. Ed writes all posts. Qwen3-Next is already in mlx-lm main. Three things are missing upstream, and each is several weeks of work:
   - an MTP head with recurrent-state rollback (#990 has stalled, and #1109 blocks ArraysCache);
   - a chunked gated-delta prefill kernel;
   - a fused hd256 SDPA.
6. Citation fixes: Kyung (arXiv:2508.06978) must be added to the bibliography. Kimpson is a MATS page, not a peer-reviewed paper. The PDTR fit is confirmed at registration_block5.md:3546. Section 2 of the document lists seven numbered decisions for Ed.

## 2. Qwen-Next MLX port and upstream path

1. The port passes every check the laptop can run: module f4ec75d1, plus gold and real-weight layer parity. The 128 GB Mac has measured nothing yet. Full 48-layer MLX parity and any real-weight test of sparse attention are still open.
2. New finding: the quant-quality POLICY classes the exact fp32 model as `reject` against the bf16 reference (mean projected KL 0.0208, p99 0.380). The lead re-registers it against the precision floor, blind, before Sunday (decision 10, FYI). The two read-only scripts behind this finding are committed so it can be reproduced.
3. Disk is the binding limit. Serial prefill n-gram I/O comes next (fixed in module v2), then memory: maxfit has 2.7 GB of margin, so maxfit5 is likely. Decode is expected at about 16-25 tok/s, because the module syncs to the host every token.
4. Plan: on Sunday, plug the SSD into the M4 Air and run download and conversion there overnight. The MBP then needs only 4-8 daytime hours of probes, and the SSD stays off it during R1.
5. Upstream: the mlx-vlm D1 fix goes first. It is still on main, unreported, and its kit is ready. A coordination comment on mlx-lm #1788 follows. The mlx-lm and llama.cpp AI rules require Ed to write every post and do every push.
6. The document has 10 numbered decisions for Ed and six research ideas for the Mac: the fidelity-energy frontier, SSD-paged parameter energy, software-overhead joules, J per byte, flat sparse-attention decode energy, and MTP. Both seat reports are in the appendix verbatim; only their heading levels are shifted.

## Overlap between the tracks

Both documents put the same upstream step first: report the mlx-vlm D1 fix, then coordinate on mlx-lm #1788. Ed writes every post. Triage the two upstream sections together.
