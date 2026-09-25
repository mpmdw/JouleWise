# OSCTX-MVP-01 v2.1: amendments to v2 after the delta reviews (Fable 05 lower half, Astra 07)

Written before any MVP data. Both reviewers returned RUN AFTER LISTED FIXES. Each amendment names the finding it cures. v2 (06) stands except where amended here.

## A1. Statistics (Astra N1, Fable 2a, 2f)

- **Stage design.** Each stage is one **Williams design**: all 6 orders of (D, I, SH) once, in a seeded random sequence (Fable 2f).
  - Stage 1 is 6 blocks.
  - Stage 2 runs only if stage 1 leaves any primary test INCONCLUSIVE. It adds 6 more blocks, and the analysis uses all 12.
- **Intervals.** At both looks, every test uses **99.375 % paired-t intervals** on the mean log-ratio. That is α = 0.05 Bonferroni-split over 4 contrasts (2 endpoints × 2 contrasts) and 2 looks. It is exact and conservative (Astra's text, adopted verbatim; it replaces the Pocock/Holm/TOST mix that Fable 2a showed was inconsistent).

| Verdict | Condition |
|---|---|
| DIFFERENT | the whole interval lies beyond a materiality boundary |
| EQUIVALENT | the whole interval lies inside both boundaries |
| INCONCLUSIVE | otherwise |

- **Power before capture (Astra N1).** Stage 0 below measures the paired spread. Before stage 1 starts, the lead publishes a table of 80 % power to reach EQUIVALENT when the truth is ratio = 1, at n = 6 and n = 12, over the stage-0 SD and 1.5× it.
  - If n = 12 cannot give ≥ 80 % power at 1.5× the stage-0 SD, the stage sizes are raised **before** stage 1, not after.
  - The minimum detectable effect reported with the results is descriptive only.

## A2. Endpoints and margins (Fable 2b, Astra N2)

- **The endpoints change.** v2's decode-only split has an internal prefill/decode boundary that guard bands cannot isolate (Astra N2). The primary endpoints avoid it.

| Endpoint | Definition |
|---|---|
| E | net rail energy of the **whole request** (fixed prompt plus exactly 256 output tokens) ÷ output tokens, in J/token. Net = gross CPU+GPU+ANE minus the cell's idle-segment mean power × request duration, the production idle subtraction. |
| R | decode tokens per second from mlx_lm's own statistics |

- **The margins.** δE = δR = 3 %, and the log bounds are log(0.97) and log(1.03).
  - **Lead's ruling on the disagreement:** Fable 2b holds against Astra's min(3 %, 5 J/E₀). The ≈5 J claim bar applies to a whole claim window, not to one arbitrary 256-token request. Tying the margin to request length makes it depend on a free choice. The absolute J/token contrast and its interval are reported beside every verdict so the council can scale them to real run lengths.
  - **Dissent (Astra) is recorded here.**
- **Validity.** If net energy is ≤ 0 in any cell, that cell's log analysis is invalid. Such a cell is reported and the block is flagged.
- **Boundary uncertainty (Astra N2).** For every request, the bound on misattributed boundary energy is (the power of the samples straddling the guard-band edges × their unclipped part). Any request where the bound exceeds 0.5 % of its net energy is flagged. The two-integral agreement check stays, as an arithmetic check only (Astra: shared anchoring can make both wrong together).

## A3. Stage 0: variance and harness smoke (Astra F7/N1, "validate offline, then size")

- **Stage 0 runs now, attended, before the unattended leg.** It is 3 blocks of (I, SH) in alternating order, 6 cells in total, with a full cell protocol.
- **Its purposes:**
  1. prove the harness end to end on real hardware, including the production-anchored reduction and the two-integral check;
  2. estimate the paired spread of E and R for A1's power table.
- **Its limits.**
  - Stage 0 runs with agents active, so its spread is an **upper-side** estimate.
  - Its numbers decide only the sizing. They never enter a verdict.

## A4. Launch chain and SH arm (Fable 2e, Astra N3, Astra N4)

- **D, I and B** start `ProgramArguments = /bin/zsh -c 'exec <python> cell.py …'`, mirroring the production chain's zsh → Python exec. The template also keeps production's environment keys (PATH, WorkingDirectory).
- **SH** is started as `caffeinate -is /bin/zsh -c 'exec <python> cell.py …'`, detached with `nohup`, from the lead's terminal-descended session. That is July's `quiet_window_clock.sh` wrapping. The cell records its ancestry (the ppid chain up to launchd), its effective QoS and the assertions.
- **SH is a contemporary shell reference, not a validated reconstruction of July** (Astra N3). An EQUIVALENT result supports this tested configuration only.

## A5. Census and state verification (Fable 2c, 2d; Astra N4, F4)

- **Every 5 s during a cell, record** per-process cumulative CPU time (`ps -Ao pid,ppid,time,comm`; flags use CPU-time **deltas**, not `%cpu`, which is a decaying average), HIDIdleTime, and the display power state.
- **Every 30 s, record** `pmset -g assertions`.
- **The flag rule:** any process other than the workload, its powermetrics and the census itself that consumes ≥ 5 % of one core in CPU-time delta over a segment flags the cell. OS processes count. The lead's session tree is allowlisted **by pid** and reported.
- **The magistrate's watchdog label.** Its owner (the magistrate) boots it out for the duration of U and S and re-bootstraps it afterwards (Fable 2c). If it cannot be parked, every cell carries the overlap record and the CPU rule decides.
- **Interruptions.** If HIDIdleTime falls below 600 s during a U cell, or the display state changes unexpectedly, the cell is **interrupted**. It is discarded and logged, the whole block re-runs in the same order after the gate re-opens, and no data are cherry-picked.

## A6. Workload integrity (Astra F6/N4)

- **Pinned everything.**
  - Model directory: `/Users/edr/jw_models/mlx-community/Qwen2.5-7B-Instruct-4bit`, the production path, with the sha256 of model.safetensors recorded.
  - mlx 0.31.2 and mlx_lm 0.31.3.
  - A fixed prompt with the chat template applied, greedy decoding, max_tokens 256, and the EOS token suppressed or verified absent, so that exactly 256 tokens come out.
- **Cache.** Each request starts from a fresh prompt cache (no reuse), and GPU completion is synchronized (`mx.eval` before stopping the clock).
- **Output identity.** The hash of the output token ids is recorded. A request whose hash differs from the stage reference is flagged, and nondeterminism is reported, never hidden.

## A7. Pre-registered follow-ups (Fable §7, Astra F5)

- **If D vs I is DIFFERENT on E or R:** a crossed follow-up of sampler context × workload context (2 × 2, 6 Williams-balanced blocks) separates sampler perturbation from workload throttling. It is designed now and run only on that trigger.
- **The U–S–U display sandwich** (I only, 3 cells each) is exploratory. It reports intervals and no verdict (Fable 2g; Astra).

## A8. Unchanged claims discipline

- **Timer coalescing and E-core placement are hypotheses.** The mechanism record may support them, but the verdicts are about the endpoints only (Astra N4).
- **No MVP number enters the paper.**
- **Installation of any ProcessType change** goes through the normal gated PR, scoped per job.
