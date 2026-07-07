# 2026-07-06: Slice 2I — First Real Energy Measurements (Mac Vertical Slice Complete)

Continuation of `2026-07-06-slice-2h-powermetrics.md`, same session. The
user installed the D-004 sudoers line
(`<local_user> ALL=(root) NOPASSWD: /usr/bin/powermetrics` (installed locally with the real username), via
`sudo tee /etc/sudoers.d/joulewise-powermetrics` + `visudo -c`); parent
verified `sudo -n` works.

## First flagship attempt: instructive failure (commit context)

Before the run, `mac_mlx_local.json` sampling was raised 1 → 10 Hz
(known-in-advance: a ~0.4 s window at 1 Hz cannot contain 2 samples).
The run: **idle baselines worked** — the project's first real power
measurement (300 samples / 35.4 s, mean 0.366 W) — but all 3 reps failed
at reduce: 0 samples in the measured window, `raw/powermetrics.plist`
**0 bytes**. Root cause (parent-diagnosed from bundle evidence):
powermetrics has ~1 s startup latency before its first document;
`start_sampling` returned at `Popen`, so a 0.32 s window (64 tokens at
~260 tok/s) SIGTERMed the sampler before it ever wrote. The
`sampling_started` marker was asserting an active sampler that wasn't.

## Fixes (commit `b4d4173`, Codex implemented, parent reviewed)

1. **Readiness wait**: `start_sampling` blocks (15 s bound, 50 ms
   `time.monotonic` polls — operational time, deliberately outside the
   benchmark clock) until the first plist document parses; timeout/early
   exit are structured failures; process terminated on failure. Codex
   also found `-b 0` (unbuffered output) in `powermetrics --help` and
   added it to all invocations, and argued correctly for anchoring
   timestamps at post-readiness `clock.now()` rather than Popen time.
2. **Measurable flagship workload**: decode 64 → 512 tokens (~2 s
   window; profile renamed `smoke_short_prompt_medium_decode`), 10 Hz
   sampling; pinned hash updated (D-029, deliberate).
3. Suite 251 → 254, green both interpreters.

## THE RESULT — 3/3 reps succeeded, all `validate-bundle --strict` green

M3 Max, Qwen2.5-1.5B-Instruct-4bit (provisional D-016), 512 output
tokens, real MLX runtime × real powermetrics telemetry, real cooldown
gate between reps:

| rep | gross J | idle-sub J | mJ/out-token | prefill J | decode J | TTFT ms | tok/s | obs Hz | idle W |
|---|---|---|---|---|---|---|---|---|---|
| 1 | 47.986 | 40.651 | 76.99 | 0.028 | 47.94 | 94.6 | 257.4 | 8.82 | 3.507 |
| 2 | 47.037 | 46.317 | 87.72 | 0.029 | 46.99 | 94.9 | 257.6 | 8.90 | 0.344 |
| 3 | 46.638 | 46.309 | 87.71 | 0.034 | 46.58 | 92.8 | 257.2 | 8.91 | 0.157 |

- Gross energy CV across reps: **1.4%** (idle-subtracted CV 7.4%, driven
  entirely by rep 1's idle baseline).
- Observed sampling 8.82-8.91 Hz vs 10 requested — inside 2H's ±20%
  acceptance band (real powermetrics intervals overrun ~12-13%).
- Implied package power during decode ≈ 23-24 W; prefill/decode energy
  asymmetry visible live (0.03 J vs ~47 J).
- **Methodological finding for D-014 / Stage 4.0:** rep 1's idle
  baseline (3.51 W vs 0.16-0.34 W for reps 2-3) was measured right
  after model load and is contaminated by post-load system settling —
  idle-subtracted energy inherits it. Idle-window placement/settling
  needs a protocol note when Stage 4.0 ratifies the statistical
  protocol.
- Corpus (3 bundles + experiment manifest) backed up to
  `~/JouleWise-backup` per the R-016 protocol immediately after the
  session.

## Acceptance

- 2H real-machine smoke: real idle baseline + measured window recorded ✓
  (this report); observed Hz within 20% ✓; permission-denied path
  documented earlier same day ✓ → **Slice 2H COMPLETE**.
- 2I: one-command real bundle ✓; `repetitions: 3` with real
  idle-recovery cooldown ✓; 3-rep variance recorded ✓; sanity checks
  (TTFT plausible, monotonic timelines, strict re-reduction) ✓ →
  **Slice 2I COMPLETE — the Phase 2 flagship demo exists.**
- P1-002 → complete (sample + sudoers verified via `sudo -n`).

## Next

- 2M homogeneous baselines (Mac-only floor allowed) is now unblocked —
  workload matrix over the Mac target.
- Phase 3 Stage 3.0.0 (kv-size helper) and 3.0.1 (mlx-lm prompt-cache
  spike) are unblocked desk/Mac work.
- P2-008 (mock telemetry × SystemClock hardening) still queued.
- Deferred (user): P1-001 scope (meta), P0-003 real backup destination
  (meta), P1-008 calendar.
