# 2026-07-06: Autonomous Build-Out — Backup Protocol, Provisional D-016, Slice 2G, Related-Work Draft

User direction: "Build out as much of the project as possible, following
the process outlined so far" before the user supplies the remaining
external inputs; "set a cursory backup location in a separate directory
and point it there... I'll handle that later"; delegate implementation to
the local Codex CLI via the repo's new bridge, with Claude reviewing.
This report records that go-ahead as the gate evidence for the interim
P0-002 destination and the **provisional** D-016 pick (playbook M4 gate:
"explicit user go-ahead recorded in the run report").

## Environment (new machine)

- Machine: MacBook Pro, Apple M3 Max, 128 GB RAM, macOS (Darwin 24.6.0).
  Repo cloned fresh to `~/code/JouleWise` (the old canonical path
  `~/code/CapstoneRivoire/Capstone` belongs to the previous machine).
- Git author auto-selected as `Ed R <edr@Eds-MacBook-Pro.local>` (differs
  from the previous machine's `Edr <edr@Edrs-MacBook-Air.local>`; amend
  policy unchanged — flag, don't rewrite).
- Preflight (playbook M0): suite green on arrival (`Ran 226 tests, OK
  (skipped=10)`); mock e2e run → `validate-bundle` green.
- New tooling: repo-local Codex bridge (`scripts/codex-bridge`, `.mcp.json`,
  `CLAUDE.md`; commit `10a570d`). Codex CLI 0.142.5 (gpt-5.5, high
  reasoning, `workspace-write` sandbox = repo + /tmp, no network, no
  Metal device in-sandbox). Machine-local `.claude/` agent/command/skill
  files stay uncommitted per the existing `.gitignore`.

## 1. P0-002: backup protocol (commit `5b12332`)

Implemented by Codex, reviewed by Claude. `scripts/backup_runs.sh`
(rsync -a, never `--delete`, dated UTC audit line per invocation).
Codex verified in /tmp (its sandbox boundary); Claude ran the real-
destination pass: backup of a mock bundle to `~/JouleWise-backup`,
restore to a temp dir, `validate-bundle` green on the restored copy.
INTERIM caveat recorded in R-016; follow-up queued as P0-003 (user names
the external/cloud destination).

## 2. D-016 provisional pick (decision log updated)

Qwen2.5-1.5B-Instruct, MLX 4-bit (`mlx-community/Qwen2.5-1.5B-Instruct-4bit`,
revision `8b403126fc14f14cfc99bb4cfa72ecbc129ea677`), mirrored per R-014 to
`~/jw_models/mlx-community/Qwen2.5-1.5B-Instruct-4bit` (839 MB; HF repo
verified via API the same day). KV row verified against the mirrored
`config.json`: 28 layers × 2 kv_heads × 128 head_dim → 28,672 B/token
fp16, matching the Phase 3 table (verification note added there).
Opens the 2G gate only; full closure (mid model, CUDA load, GGUF paths,
P1-001 scope) remains open.

## 3. Slice 2G: MLX runtime adapter (commit `3eb0acd`)

Install evidence (Phase 1 checklist updated): repo-local `.venv`,
Python 3.13.1, `mlx` 0.31.2, `mlx_lm` 0.31.3, `transformers` 5.12.1.
**Compat finding:** `transformers` 5.13.0 breaks `mlx_lm` 0.31.3 at
import (`AutoTokenizer.register` signature change); the `[mac]` extra
now pins `mlx-lm>=0.31.3` + `transformers<5.13`.

Implemented by Codex per the pinned guide §2G (adapter, lazy registry
branch, CI-safe fake-based tests, config updates); suite 226 → 230,
green under both system python3 (CI-equivalent, no mlx) and the venv.
Codex confirmed the installed API surface (`mlx_lm.load(...,
return_config=True)`, `mlx_lm.stream_generate(model, tokenizer, prompt,
max_tokens=...)`; `_download` stays local for existing paths).

**Live smoke** (Claude, real Metal — Codex's sandbox has no Metal device;
its in-sandbox attempt correctly produced a structured `unsupported`
bundle, D-012 working as designed):

- First live run FAILED usefully: `unknown_error`, "fewer than 2 power
  samples inside the measured_run window (0 found)". Root cause (from
  the bundle's own evidence): `MockTelemetryAdapter` under `SystemClock`
  (bound per D-020 because the runtime is real) stamps its first sample
  at `start_sampling`'s clock read (microseconds BEFORE the
  `sampling_started` marker) and its last at `stop_sampling`'s (AFTER
  `sampling_stopped`) — both outside the D-026 window; at 2 Hz a ~0.32 s
  window has no interior samples either. Under FakeClock these coincide
  with the markers, which is why 169→230 tests never saw it. This is a
  mock-only composition edge (real samplers emit continuously inside the
  window). Fix: bring-up config sampling at 20 Hz + note (Codex,
  reviewed); hardening queued as P2-008.
- Final live run: `bundle ... status=succeeded`;
  `validate-bundle --strict` green; post-hoc `reduce` green.
  Numbers (bundle `example-mac-mlx-mock-telemetry`, /tmp runs dir):
  TTFT **81.5 ms** (>0, < total ✓), decode **265.8 tok/s** (64/64 tokens,
  EOS suppressed-and-recorded), token timeline monotonic ✓, model load
  0.26–0.85 s, `token_count_source=runtime_observed` (2N.3 exercised),
  `observed_sampling_hz` 20.00002 vs 20.0 requested, phase energy split
  prefill/decode present (synthetic power × real timeline). First real
  generation traces of the project.

## 4. P3-001: related-work draft (commit `c31ffac`)

Produced by a 23-agent research workflow (11 sources researched in
parallel, each independently re-fetched and adversarially verified;
corrections applied — e.g. Bench360's raw-artifact flag flipped to
false, MLPerf Power's boundary wording tightened). Positioning audit
per playbook M3 step 3, honestly adjusted:

- Claim 1 (boundary-honest cross-device) — partially covered by
  JouleSort and MLPerf Power; narrowed to rail-manifest granularity on
  device classes both exclude.
- Claim 2 (auditable raw bundles) — partially covered by MLPerf Power
  logs / Splitwise+Mooncake workload traces; narrowed to self-contained
  re-reducible per-run bundles.
- Claim 3 (split-inference energy on local interconnects) — stands
  against all 11 sources.

Claude's review caught the synthesis dropping Bench360 from the
citations table (restored; author list verified directly against arXiv).

## Verification (end of session)

```
python3 -m unittest discover -s tests        → Ran 230 tests, OK (skipped=10)
.venv/bin/python -m unittest discover -s tests → Ran 230 tests, OK (skipped=10)
```

Plus: mock e2e green; 2G live bundle succeeded + `--strict` + `reduce`;
backup restore test green. Commits (local, NOT pushed — awaiting user):
`10a570d` bridge, `5b12332` backup, `c31ffac` related work, `3eb0acd` 2G,
plus this bookkeeping commit.

## Delegation notes (user-requested meta-observation)

Codex (gpt-5.5) interactions: 1 smoke, 2 implementation, 1 review-fix
round trip. What worked: pinned-spec pointers instead of restated specs;
environment facts it cannot discover (sandbox limits, verified versions,
mirror paths, which interpreter is CI-equivalent); an explicit
bookkeeping fence; demanding evidence + a deviations section. Both its
deviations were sound judgment calls (no `set -e` so `$?` capture works;
broadened import-failure catch justified by in-sandbox Metal errors).
What cannot be delegated: anything outside its sandbox (real-Metal
smoke, $HOME writes, network) and anything needing cross-session project
context (bookkeeping, gate decisions). The live-smoke failure was found
only because the parent re-verified on real hardware — sub-agent "tests
green" is necessary, never sufficient, for hardware-adjacent slices.

## Next

1. P1-002 (user): privileged powermetrics sample + D-004 sudoers — the
   only blocker for 2H, then 2I (first real ENERGY numbers).
2. P1-001 (user): supervisor scope → full D-016 closure.
3. P0-003 (user): real backup destination.
4. Implementable without user: P2-008 mock-telemetry hardening; Stage
   3.0.0 kv-size helper; Stage 3.0.1 mlx-lm prompt-cache spike (2G +
   chosen small model now satisfied its inputs).
