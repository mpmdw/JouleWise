# Run report — 2026-07-07: five-stream parallel batch (P2-008/009/011, 2M tooling, kv-size)

One session, six parallel worktree streams (five implementation + one
repo-wide test audit), an ideation council (C-005), and a process
meta-review (C-006). Product outcomes below; the full orchestration
trace — catch attribution, deliberations, interventions, layer yields —
lives in `docs/council_log.md` C-005/C-006 (not restated here).

## Landed (all merged to main, suite 369 OK skipped=10)

| PR | Stream | What |
|---|---|---|
| #2 | kv-size helper | `joulewise/kv_size.py` + `kv-size` CLI verb (Stage 3.0.0): KV-cache bytes/token from HF config or flags; nested `text_config`, head_dim fallback with divisibility guard; verified against both mirrored models (Qwen2.5-1.5B 28 KiB/tok; Qwen3.5-122B 96 KiB/tok) |
| #3 | 2M campaign tooling | `scripts/generate_matrix.py` (deterministic, byte-identical reruns; 4 profiles × any base config) + `scripts/run_campaign.py` (strictly sequential, resume-by-skip, JSONL log, lock, `--dry-run`, `--backup`, `--max-failures`) |
| #4 | P2-009 rich telemetry | `rich_telemetry(.idle).jsonl` bundle artifacts (per-sample GPU/cluster DVFS, regenerable from raw), idle-quality gate (`idle_window_suspect`, flag-only), `joulewise/environment.py` per-bundle snapshot |
| #5 | P2-008 mock hardening | MockTelemetryAdapter strictly-interior stamping (centered grid + thirds fallback); 20 Hz workaround retired; verified live at 1 Hz real-MLX (the original 2G failure regime) |
| #6 | P2-011 / D-014 uncertainty | `joulewise/aggregate.py` + experiment-manifest enrichment: per-metric Student-t 95% CIs as serialized `UncertaintyInterval`s, MAD outlier records, explicit below-protocol flags at every n |
| — | Integration fixes | INT-001 stale-config refusal in the campaign flow (`a05e54d`); INT-002 per-experiment shared env snapshot + deterministic FakeClock skip (`8856c04`) |

## Live verification highlights (lead-side, real hardware)

- **D-014 acceptance:** real n=3 MLX experiment → 10 metrics aggregated;
  energy/output-token **99.19 ± 1.36 mJ** (Student-t 95%, CV 0.55%);
  `below_headline_protocol: true` correctly flagged at n=3; aggregate
  **re-derives byte-identically from the bundles alone**.
- **Idle-gate first true positive:** the gate flagged the lead's own
  verification run as contaminated (agent-fleet display compositing held
  the GPU ~75% busy during the idle window) — the run still SUCCEEDED
  (flag-only guarantee held). The instrument outperformed the operator's
  prediction.
- **P2-008 regression proof:** 1 Hz real-MLX + mock telemetry (formerly
  0 interior samples → structural reducer failure) now yields 2 interior
  samples via the thirds fallback and a strict-valid bundle.

## Council outputs

- **C-005** (ideation): hardware-tiered research agenda appended to
  `docs/research_question_bank.md` — 16 Tier-1 questions on current
  hardware, 10 Tier-2 behind named gates, 5 Tier-3 acquisition classes;
  `jw_mixed_v1` starter workload suite specified (→ P2-012).
- **C-006** (meta-review): trace format v2 adopted; session trace
  committed; Opus refuter tier dropped (zero unique catches, per the
  council's own evidence rule); skills deduplicated to one-fact-one-home;
  `operation-loop` conductor-score skill installed globally.

## Open threads at session close

- **Stream F (repo test audit)** in flight: 7 bug-hunt lens outputs +
  gap map complete; findings re-check against merged main, test writing,
  and its PR remain. Final integration review over the complete
  composite follows F's landing.
- Follow-ups queued from stream reports: `aggregate` CLI verb (~15
  lines), methodology-doc amendment (aggregate lives in the experiment
  manifest; t-table floor policy), idle-gate 0.40 threshold needs an
  empirical contaminated-window corpus, `dvfm_states` slimming option
  for hour-long captures.

## Next best task

**P2-006: run the 2M two-model baseline campaign** — top of queue, fully
tooled, command sequence in PR #3. Requires a QUIET machine (no agent
fleet, no Codex load — the idle gate will now prove it) and the
`.venv` interpreter. Everything the campaign produces flows through
uncertainty aggregation and rich-telemetry forensics automatically.
