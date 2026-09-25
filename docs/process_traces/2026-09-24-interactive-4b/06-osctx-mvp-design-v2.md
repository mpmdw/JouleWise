# OSCTX-MVP-01 design v2 (supersedes 02), after the Fable and Astra reviews

Written 2026-09-24 ≈18:45 PDT, before any MVP data. The reviews are in 04 (Astra, REDESIGN) and 05 (Fable, RUN WITH CHANGES). Each change below cites the finding that forced it. Where the reviewers disagreed, the lead's call and its reason are stated.

## 1. The forcing problem, restated

A launchd job with no `ProcessType` runs at **utility** priority. The QoS class is the scheduling priority macOS gives a thread. Every child of the job inherits it, including the inference workload.

The pilot showed no workload penalty at utility priority on a **busy** machine. Fable's reading: on a busy machine the efficiency cores ("E-cores", the slow low-power cores) are already occupied, so a utility thread spills onto a performance core ("P-core"). On a **quiet** machine the scheduler may keep it on E-cores. That would change both joules per token and tokens per second. Unattended windows run on a quiet machine, so this is the threat to test (Fable 1b).

The 248 ms night cadence has a simpler explanation than "extra throttling at night". It is **timer coalescing**: the kernel may delay a low-priority thread's wake-up by a "leeway", up to 75–100 ms on this machine (`sysctl kern.timer`), so that sleeping cores stay asleep. On a quiet machine nothing else wakes the core, so the full leeway is used every sample. Fable re-parsed the archive, and the evidence fits:
- the archived gaps are capped near 275 ms;
- the rare short gaps coincide with power spikes, when something else woke a core.

Cadence alone does not bias integrated energy, because every sample carries its own energy counter. Its cost is coarser time boundaries (Fable 1a).

## 2. Questions, pre-registered

- **Q1 (compromise).** On a quiet, unattended machine, does the production context D change 7B decode joules per output token, or tokens per second, relative to the Interactive context I?
- **Q2 (cure, and link to the paper's data).** On a quiet, unattended machine, does I match the shell context SH, which is how every July/August claim corpus was launched (scout 03), on the same endpoints? Is I's powermetrics cadence ≤ 130 ms median?
- **Q4 (display).** Does display asleep (S) differ from display on at brightness 0 (U) for context I? It is secondary. It matters only if future windows change Ed's brightness-0 habit.
- **Dropped: Q3 (which daemon causes what).** Observation cannot establish cause, and DAS activity names are `<private>` in the log (Fable 2; Astra F2). The census is still recorded and reported as association.
- **Deferred: state A (attended).** Every production window runs unattended. Comparing to an attended state answers no decision. The shell arm SH, run in the same unattended state, is the right reference because it is the July launch path (Astra F2, the missing shell arm).

## 3. Arms, blocks and order

| Arm | How launched | Role |
|---|---|---|
| D | throwaway launchd gui job, no ProcessType | production today |
| I | same job with `ProcessType Interactive` | proposed cure |
| SH | subprocess of the lead's terminal-descended session (QoS 0x21 in the pilot) | July/August claim-corpus launch path |
| B | job with `ProcessType Background` | control that the harness can see throttling. It is not a decision input and does not validate small-effect sensitivity (Astra F6). |

- **One block** = D, I and SH once each, in an order drawn from a pre-generated balanced Latin-square sequence (fixed seed in the config, Astra F7). Each cell is measured independently. Repeats within a cell are not independent cells (Astra F1).
- **Stage 1, state U:** a discarded warm-up cell (I), then **6 blocks**, then B ×2 (Fable 2). That is 21 cells.
- **Stage 2, state U, only if stage 1 is INCONCLUSIVE on a primary endpoint:** 6 more blocks, and the final verdict is taken at n = 12. There is no third extension. The two looks split α: 0.0294 each, Pocock.
- **State S, context I only:** a U–S–U sandwich of 3 cells each, with every display transition verified in `pmset -g log` and 120 s of settling after it (Astra F2). It runs after stage 1, or after stage 2 if stage 2 happens.
- **State U gate:** HIDIdleTime ≥ 600 s before the first cell, re-checked before every cell. If the user returns, the runner pauses and logs it. Brightness is recorded (via `corebrightnessdiag`) or declared unreadable.
- **No agents:** the magistrate launches nothing and its seats finish before the gate opens. The lead's own seats are idle. The watchdog's 300 s tick is logged, and cells that overlap it are flagged (Fable 5).

## 4. What one cell measures

1. **Model page cache:** the model files are pre-read (`cat > /dev/null`) before each cell, so the default role's I/O throttling cannot enter through model load (Fable 1c). Load time is still recorded as its own segment.
2. **powermetrics:** production argv, started as a child of the cell (inherits the context).
3. **Segments:** each timed segment has ≥ 2 s idle guard bands on both sides (Fable 4). The segments are:
   - idle 30 s (floor and cadence);
   - LM: Qwen2.5-7B-Instruct-4bit, a pinned revision from the local cache, a fixed prompt, greedy, **256 output tokens**, 1 in-cell warm-up and then 3 timed requests. Prefill and decode are recorded separately. The output token count and a hash of the output text are recorded, so identical work is proved across arms (Astra F6);
   - a CPU-loop mechanism probe, lengthened to ≥ 5 s per repeat. It is not a decision input (Fable 2).
4. **Mechanism record:**
   - `ps -Ao pid,ppid,pcpu,comm` every 5 s and `pmset -g assertions` every 30 s for the whole cell, OS processes included (Fable 5 BLOCKER; Astra F4);
   - per-cluster E/P active residency and frequency from powermetrics;
   - thermal pressure per sample;
   - QoS of the workload's threads after MLX import;
   - `launchctl procinfo` for the workload and powermetrics if it works without root, otherwise recorded as unavailable;
   - the powermetrics CPU time at the end of the cell (Fable 1f).
5. **Energy:** production's own path, `joulewise/adapters/powermetrics.py` clock-evidence and anchoring, then `joulewise/reduce.py` interval integration (Σ power × overlap). Gross CPU+GPU+ANE rail energy and idle-subtracted energy are both reported, as production does. A second integral sums the plist energy counters over the same overlap. Any disagreement > 0.1 J flags the cell as a harness defect (Astra F3; Fable 4). If production anchoring cannot be reused as-is, the build stops and asks.

## 5. Decision rules (fixed now)

- **Primary endpoints** (per LM request, cell median of 3):
  - E = idle-subtracted decode joules per output token;
  - R = decode tokens per second.
- **Contrasts:** log(D/I) and log(SH/I), paired within blocks.
- **Margin:** δ = min(3 %, 5 J ÷ median gross decode energy of one request). The 3 % is sized to the claim-side bar of ≈5 J; the min() closes Astra's 2.5 % gap.

For each endpoint × contrast, compute the paired-t interval on the mean log-ratio:

| Verdict | Condition |
|---|---|
| **DIFFERENT** | the 95 % interval (Holm-adjusted across the 4 endpoint×contrast tests) excludes 0 **and** the point estimate is outside ±δ |
| **EQUIVALENT** | the 90 % interval (TOST, the standard two one-sided tests at α = 0.05) lies entirely inside ±δ |
| **INCONCLUSIVE** | otherwise. This goes to stage 2; after stage 2 it is reported as INCONCLUSIVE, never rounded to a verdict |

- **The minimum detectable effect** at 80 % power, from the observed paired spread, is reported next to every verdict.

| Outcome | Meaning |
|---|---|
| D vs I DIFFERENT on E or R | Launchd-default measurement is compromised for inference. No launchd-default inference data exist (scout 03), so this constrains future windows only. |
| I vs SH EQUIVALENT on E and R, and I's cadence ≤ 130 ms | **CURE SUPPORTED**: I reproduces the July launch path. This is a recommendation to the council, not an installation. The template change goes through the normal gated PR, scoped to the night job only. The dead-man and magistrate jobs are judged separately (Astra F7). |
| B not slower than I by ≥ 1.5× on the CPU probe | Control investigation. The run is not voided automatically (Astra F6). |
| Any other combination | Reported as is to the council. |

A null result on inference does not certify the September fiducial or idle nights. Those remain judged by their own evidence (Astra F7).

## 6. Budget

At ≈4 min per cell, stage 1 in U is ≈1.5 h, S is ≈40 min, and stage 2 if needed is ≈1.2 h. The runner has one deadline per cell, cleanup of only its own labels (trap on every exit path), and labels `com.joulewise.dummy.osctx.*`, outside every night-check pattern.

## 7. Reviewer disagreements and the lead's calls

| Point | Astra | Fable | Call and reason |
|---|---|---|---|
| Overall | redesign | run with changes | v2 keeps the shape and adopts both BLOCKER sets |
| Variance pilot before sizing | separate pilot | 6 pairs plus an extension | a two-stage design with α split gives the same protection without a separate run |
| Display sleep | defer; U–S–U if run | promote to primary | secondary, as a U–S–U sandwich on I only. Ed's windows use brightness 0, so S decides nothing unless the habit changes |
| Sampler-off controls | add limited | not raised | deferred. They are triggered only if D and I differ, to separate sampler from workload |
