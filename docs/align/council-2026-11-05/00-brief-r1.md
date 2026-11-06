# Window design council: the next ALIGN (SHADE-Arena agent-monitoring) window on the measurement Mac. ROUND 1, independent design

You are one of three independent designers: Opus 5.5, Sol 6.1 and Fable 5.1. You will see the others' designs only in round 2. An Opus 5.5 chair rules at the end. Work alone and be concrete.

## Ed's goal (verbatim, 2026-11-05)
"use that new council to design the next window for the next shade arena window - see if you can get that thermal shit under control so i can see on real models that are used in prod, whatever the top qwen models i think qwen next and qwen 3.8 something - just the top models runnable w 128 gb"

So the next window should:
- measure energy and monitoring signals on production-grade open models: the strongest Qwen models that fit and run on the 128 GB measurement Mac (Ed names Qwen3-Next and "Qwen 3.8 something");
- get thermal and clock confounds under control, so that energy-based sabotage and monitoring signals reflect behaviour, not machine state.

## Workspace (all paths relative to the council workspace root, the current directory for Sol; /Users/edr/code/CapstoneProject/jw-wt/council-align9 for Claude seats)
- The checkout is the live ALIGN pilot-8 kit, `lane/2026-11-04-align-pilot8-benign` @ e328f0e72. Read `scripts/align_pilot_session.py` and the related joulewise modules and configs.
- History and decisions are on origin/main. Use `git show origin/main:RUN_STATE.md` (search "ALIGN pilot", items ~150-168 and the "Next activation" blocks), `git show origin/main:docs/process_traces/<dir>/RECORD.md` for the magistrate records from 2026-10-30 to 11-04 (find them with `git ls-tree -r --name-only origin/main docs/process_traces | grep magistrate`), and the design docs and registrations they cite.
- Other ALIGN lanes are `git branch -r | grep -i align`. Earlier pilot kits and consult records are referenced from RUN_STATE.
- `.council-data/` is the private data repo. Its branches hold desk outputs and reviews, for example `origin/claude/align-desk-cal-review-cf1`.
- BYTES extension: `docs/registrations/bytes_extension_models_2026-10-27.md` on origin/main (Qwen3.8-27B 8-bit; MLX feasibility under the pinned mlx-lm 0.31.3; Nemotron 3.5 Super infeasible). Thermal work: BY-THERM-LINES (`origin/codex/2026-10-28-by-therm-lines`) and RUN_STATE's thermal notes.
- Key known facts:
  - Pilot 3 used Qwen3-30B (thinking on) and Qwen3-Next.
  - Pilot 7: OS thermal level 0, yet the untampered sabotage alarms "accumulated over later turns, shared by benign trajectories, tracking the GPU clock".
  - A level step between pilots 5 and 6 is not attributable.
  - Pilot 8 froze the sequence design `[1, P, D, (C+P)D + D^2/2, CP + P^2/2]` and runs anchors plus 20 fresh benign trajectories as a held-out calibration increment.

## Hard constraints
- The measurement Mac's quiet-machine rules hold: no agent processes during collection, a launchd chain only, and a window maximum of about 44,640 s unless you justify more. Read the RUN_STATE rules.
- The scientific integrity of earlier pilots holds: never edit a frozen script after seeing data under it, and keep held-out calibration honest. Say how the new models relate to the frozen pilot-8 design. Is it a new calibration cell, a fresh pre-registration, or something else?
- Do not touch block-5 paths (/Users/edr/jw-b5-*, night-custody, night-archive, restricted/). This is unrelated work and block 5 is blinded.
- Claude seats may use WebSearch and WebFetch to verify which Qwen models currently exist, their sizes, MLX conversions, and memory needs at the chosen quantization including KV cache at the needed context length. Sol has no network: list what must be verified.

## Deliverable: write `.council-out/r1-<seat>.md` (seat = opus | fable | sol)
1. **Model set**: exact models and repos, quantization, weight footprint, peak memory at the needed context, MLX and mlx-lm feasibility (pin bump?), tokens/s and energy-per-trajectory estimates, and why these count as the "top runnable in 128 GB". Include a fallback for each.
2. **Thermal and clock control protocol**:
   - diagnosis of the pilot-7 GPU-clock tracking from the records;
   - controls: preconditioning and soak to steady state, cooldown or stability gates on measured SoC temperature or GPU clock rather than wall time, duty-cycle limits, ambient and fan or physical setup Ed can do, interleaving or counterbalancing (ABBA, Latin square) so drift cancels, telemetry to record (powermetrics GPU frequency and residency, thermal pressure, die temperatures), and rejection and exclusion rules fixed in advance;
   - how the analysis adjusts or stratifies for clock state, and how you will know it is "under control" (a quantitative acceptance criterion).
3. **Window structure**: sessions, ordering, allocation (models × task pairs × benign/sabotage × seeds), duration budget against the window maximum, anchors that link to pilots 4-8, and whether one window or a short series is needed.
4. **What must be built or changed** in the kit, with file pointers, the rehearsal and dry-run plan, and the review gates.
5. **Risks, open questions, and what Ed must do physically**.
Be quantitative and cite file:line or record ids for every factual claim. Mark guesses as guesses.
