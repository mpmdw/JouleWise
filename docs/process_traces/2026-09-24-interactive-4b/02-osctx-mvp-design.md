# OSCTX-MVP-01: does the way macOS launches our jobs change what we measure?

Status: DRAFT design, written before any MVP data. Lane OS-LAUNCH-AUDIT-01, interactive seat 4b, Ed present, 2026-09-24 ≈18:15 PDT. Reviewers: Fable 5.1 (blind seat) and Astra 6. Builder: Sol 6.0.

## 1. The forcing problem

Every unattended JouleWise run (calibration captures, idle-floor pilots, model nights) starts from a **launchd job**. launchd is the macOS service manager: a small property-list file tells it which program to start and when. That file may carry a `ProcessType` key, which tells macOS how much to hold the job back. Our three templates in `configs/launchd/` set no `ProcessType`. launchd.plist(5) says a job with none set gets "light resource limits … throttling its CPU usage". Every process the job starts inherits that treatment: the shell script, the Python driver, `sudo powermetrics` and the MLX inference.

Two facts from today (record 01 and `pilot/`):

1. **Sampling cadence.** powermetrics is asked for one sample every 100 ms (`-i 100`). The gap it actually delivers between samples is the "cadence":

   | Launch context | Cadence |
   |---|---|
   | Interactive shell | ≈118 ms |
   | Default launchd job, user active | ≈175 ms |
   | Launch agent marked Interactive | ≈126 ms |
   | Archived unattended night captures | ≈248 ms |

2. **Workload speed.** A pilot with the user at the keyboard ran a fixed pure-Python loop, a fixed GPU matrix multiply, and a 200-token generation with Qwen2.5-0.5B-4bit:

   | Launch context | QoS class | Workload times |
   |---|---|---|
   | Shell | 0x21 | 0.38 s (loop), 0.48 s (generation) |
   | Default launchd | 0x11 | the same as the shell |
   | Launch agent marked Interactive | 0x15 | the same as the shell |
   | Background | 0x09 | loop 2.0–2.5 s, generation 1.7–1.9 s |

   The QoS class is the scheduling priority macOS assigns the thread: 0x21 user-interactive, 0x19 user-initiated, 0x15 default, 0x11 utility, 0x09 background. Low classes are steered onto the slower efficiency cores ("E-cores") and get coalesced timers, meaning wake-ups are batched and deferred.

The unexplained gap is 175 ms by day against 248 ms at night. So the **unattended state** tightens the throttling further. In the unattended state nobody touches the keyboard ("user idle"), and the display stays ON at brightness 0: Ed dims it by hand, `pmset displaysleep 0`, and the screensaver is off. If the tightening reaches the inference workload, the energy and latency from launchd nights are biased. A model placed on E-cores, or waiting on coalesced timers, uses a different number of joules per token than the same model run attended.

## 2. Questions the MVP must answer (pre-registered)

- **Q1 (compromise).** In the unattended state, does the production context (default launchd) change workload time or energy per unit of work relative to the Interactive context by more than the materiality bar in §5?
- **Q2 (cure).** In the unattended state, does `ProcessType=Interactive` give powermetrics cadence ≤ 130 ms median and workload metrics equal to the attended shell within the bar?
- **Q3 (state).** Which part of the unattended state does the tightening: user-idle alone, or idle plus maintenance daemons that macOS starts when the user is idle? Examples of such daemons: Spotlight `mds`/`mdworker`, `photoanalysisd`, `backupd`, `fseventsd`, XProtect. The census answers this.
- **Q4 (display).** Does display sleep (`pmset displaysleepnow`) behave differently from display-on at brightness 0? This is secondary, but future windows might sleep the display.

## 3. Design

**One cell** = one throwaway launchd gui job (label `com.joulewise.dummy.osctx.*`, booted out afterwards). It runs the whole measurement so every child inherits the context. The cell does, in order:

1. Record the state: `HIDIdleTime`, `pmset -g assertions`, display brightness if readable, a `ps` top-15 by CPU, thermal pressure (`pmset -g therm`), QoS class and nice of the workload process, and the cluster of the core it runs on (via powermetrics per-cluster residency).
2. Start `sudo -n /usr/bin/powermetrics -b 0 -i 100 --samplers cpu_power,gpu_power,ane_power,thermal --format plist -o …` **as a child of the cell**. This is production argv.
3. Idle segment: 30 s of nothing. It gives the floor power and the cadence at rest.
4. CPU segment: a fixed pure-Python loop, 5 repeats.
5. GPU segment: a fixed MLX fp16 4096² matmul ×40, 5 repeats.
6. LM segment: Qwen2.5-7B-Instruct-4bit (a production model, cached locally) generates 128 tokens from a fixed prompt with greedy decoding, 1 warm-up and then 3 timed repeats. Record the prefill and decode token rates and the output-token count.
7. Stop powermetrics. Write one JSON with monotonic and wall timestamps for every segment boundary.

**Contexts.** Each cell runs in one of three contexts:

| Code | Context | Role |
|---|---|---|
| D | launchd, no ProcessType | production today |
| I | launchd, `ProcessType=Interactive` | proposed cure |
| B | launchd, `ProcessType=Background` | positive control, known to throttle; proves the harness can see throttling |

**States.**

| Code | State | Trigger | Order |
|---|---|---|---|
| A | attended | Ed or agents active | run now |
| U | unattended | `HIDIdleTime` ≥ 600 s continuously, brightness as Ed leaves it (0 by his habit) | the harness waits for it |
| S | display asleep | the agent issues `pmset displaysleepnow` after U | then `caffeinate -u -t 1` to wake |

**Order within a state:** D, I, B, then I, D, B, repeated, so 3 cells per context per state. The order is interleaved to cancel drift. A cell takes ≈3 min, so a state takes ≈30 min.

**Load control.** Agent seats are paused during U and S. The magistrate is asked, and this seat launches nothing. The census records what else ran. Any cell whose census shows a non-OS process above 20 % CPU is flagged, never silently dropped.

## 4. Derived quantities (computed identically for every cell)

- **Cadence:** median and p95 of the `elapsed_ns` gaps in the idle segment and in the LM segment.
- **Workload time:** the median of the repeats per segment.
- **Energy per segment:** Σ over samples of (cpu + gpu + ane power) × sample interval, with sample boundaries clipped to the segment boundaries. For the LM segment, also joules per output token.
- **Core placement:** the P-cluster versus E-cluster active residency during the CPU and LM segments.

## 5. Decision rules (fixed now, before data)

The **materiality bar** is a ratio outside [0.97, 1.03] between the median of D and the median of I in the same state. It applies to workload time or energy per token, and it counts only when the three D–I cell pairs all point the same way. It is sized to the project's ≈5 J claim-side bar: a 3 % change on a ≈100–200 J LM run is 3–6 J.

| Result | Verdict |
|---|---|
| B shows no throttling vs I (ratio < 1.5 on the CPU loop) | **HARNESS FAILURE**. The MVP is void and the harness is fixed. |
| Q1: D vs I breaches the bar in state U | **COMPROMISED**. Every launchd-night number needs re-collection or a correction argument before claim use. The scout's corpus inventory says which. |
| Q1: D vs I within the bar in U and S | Workload data are not compromised by the context. Cadence alone is the issue. |
| Q2: I in state U gives cadence median ≤ 130 ms **and** workload/energy within the bar of attended-state I | **CURE CONFIRMED**. Install `ProcessType=Interactive` in all three templates, through the normal gated PR. |

Any other outcome goes to council with the data, and no verdict is claimed.

## 6. What this MVP is not

It is a diagnostic. None of its numbers enter the paper. It decides:

1. whether past launchd data are usable;
2. which launch context future windows use;
3. whether the ACCEPTANCE-25G83-01 premise changes. Record 01 already says it does.
