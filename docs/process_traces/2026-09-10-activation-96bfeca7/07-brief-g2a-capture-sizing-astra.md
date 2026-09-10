SESSION_MODE: delegated
WRITE_SCOPE: []
BRIDGE_ORIGIN: claude
BRIDGE_HOPS_REMAINING: 0

# G2-a capture sizing versus the two evidence gates seat B flagged (gpt-6-astra, high, genre scout, read-only; return the report as your FINAL MESSAGE)

Seat B of GATE-SENSIBILITY-SWEEP-01 (`docs/process_traces/2026-09-10-activation-96bfeca7/02b-gate-inventory-analysis-side-astra-report.md` §D items 2–3, §E R2) raised two capture-sizing questions that could refuse a correctly configured first G2-a night. Answer them from code, the G2-a probe configuration, and historical bundles.

The G2-a probe configuration (`scripts/generate_g2a_probe_inputs.py:467–498` at this head): one repetition, one warmup run, 512 output tokens, 10 Hz power sampling (nominal 100 ms; the fiducial contract reports ~115 ms observed cadence), 30-second idle sampling, 5-second warmup sampling. The chain is emitted by `scripts/gen_g2_phase_d.py` from `docs/process_traces/2026-08-28-live-smoke/SHAKEDOWN-G2-RUNSHEET.md` (G2-a block from ~line 316); each stage runs `run_campaign.py` with `configs/campaign_policies/quiet_mac_p2_production.json`.

Q1. `joulewise/uncertainty_evidence.py:977` requires ≥60 s of accumulated raw sampler intervals (excluding record zero) for the rate-model fit. Trace which capture that lifetime is measured over for a G2-a member (per-member sampler process? per stage? idle + warmup + run?), what the sampler lifetime of one G2-a member actually is (derive from the controller's capture lifecycle in `joulewise/controller.py` and `joulewise/adapters/powermetrics.py`, and confirm against a historical bundle's raw sample count under `runs/` or `/Users/edr/JouleWise-shakedown-g2/` if present — read-only), and give the verdict: passes with margin / at risk / fails. If at risk, the physically motivated remedy (which knob, which file, what it does to the emitted chain bytes and inventory pins) and whether it must land before the first window.

Q2. `joulewise/idle_dependence.py:267` requires n ≥ 3(L+1) idle samples where L is derived from cadence (read how). At exactly 100 ms, L=100 → 303 needed, so 300 perfect samples fail; at 115 ms, L=86 → 261 needed. Determine from the controller/adapter how many idle samples a 30 s idle capture actually yields (nominal vs observed cadence; is the 30 s wall-clock or sample-count bounded? does record zero count?), read a historical bundle's idle sample count if any exists, and give the same verdict / remedy / must-it-land-first answer. State explicitly whether the exact-100 ms case is physically reachable (does powermetrics ever deliver exactly 100 ms intervals over 30 s?).

Q3. Any OTHER count/duration gate on the G2-a member path that a 30 s idle / 5 s warmup / 512-token single-repetition capture sits within 20 % of (sample minimums, coverage fractions, settle requirements, the 600 s clean dwell, the fiducial's 59-pulse census). One line each with margin.

Read-only; no edits; `python3 -c` arithmetic only. Report claude-codex-report/v1, genre scout, header < 8192 bytes; verdict rows Q1/Q2/Q3 each `start_now` (safe) / `needs_ruling` (at risk, remedy stated) / `do_not_start` (fails).
