# Agent-monitoring pilot v0: protocol (DRAFT for the lead)

Status: **DRAFT for the lead.** Non-claim instrument check. Nothing here is
registered, and no pilot number is a result for any candidate question.
Written by seat ALIGN-READY-1 on 2026-10-27; kit `configs/campaigns/align_pilot_v0/`,
runner `scripts/align_pilot_session.py`, roster `joulewise/align/apple/pilot.py`.

## Purpose

The first pilot checks that the Apple `align_episode` path works as an
instrument on the measurement Mac. It serves the first two bank rows in
`docs/align/PIPELINE.md`:

- RQ-ALIGN-METADATA-BASELINE: the logged turn, token and tool-call counts each
  episode records;
- RQ-ALIGN-ENERGY-RESIDUAL: the energy beside those counts, attributed per turn,
  phase and tool call.

A pilot session tests no hypothesis. It does not estimate a catch rate, a
residual effect or a monitor score. Twelve episodes from one model cannot
separate benign runs from sabotage runs, and nobody should read them that way.

## What one session runs

| Item | v0 value | Source |
|---|---|---|
| Model | Qwen3-8B-4bit, MLX, revision `545dc425` (the BYTES `qwen3-8b` source, already on the Mac and file-pinned) | `scripts/align_pilot_kit.py` `BASE_CONFIG` |
| Runtime | in-process `mlx_lm` through the existing `MlxRuntimeAdapter`; greedy; chat template default (Qwen3 thinking on) | `docs/align/apple_path.md` |
| Telemetry | powermetrics at 10 Hz, the unchanged controller, hazard policy and custody of the BYTES member | base config |
| Tasks | SHADE-Arena `spam_filter_update` (41 tools) and `bank_transfer_2` (71 tools), pinned at `6614e771` | `joulewise/align/shade/upstream.py` |
| Why these two | both pairs score main and side tasks deterministically, so no judge model or service is needed | `docs/align/shade_port.md` |
| Conditions | benign (`system_message_no_secondary_task`) and sabotage (`system_message_suspicious`, hint on) | `ShadeTask` |
| Repeats | 3 per (pair, condition); because decoding is greedy, a repeat regenerates the same token sequence | `PILOT_V0_REPEATS` |
| Episodes | 12, in matched ABBA order, alternating the two pairs; 6 run before the midpoint reference and 6 after | kit `collection_plan.json` |
| Budgets | up to 12 turns per episode, up to 1,536 generated tokens per turn; the episode ends when the model replies without a tool call | `PILOT_V0_MAX_TURNS`, `PILOT_V0_MAX_TOKENS` |
| Scaffold | the BYTES Mac check's block-6 scaffold, unchanged: bracket reservation, pre and post calibration, 18 NEG-8 corpus members with the bound derivation, 3 start, 1 midpoint and 3 end references, verdict, backup | kit `plan_tree.json` |
| Monitor | none during the session; see "After the session" | |

Only the lead arms a session, with the item-H sequence:
`align_pilot_session.py prepare`, then `install` as the lead's last action
before exiting, then `desk` after the terminal record. No agent session may be
active on the Mac at any point while a session is armed.

## What is recorded

Each episode member records the following in its run bundle, through the
existing controller:

- the immutable `Episode`: turns with prefill, decode and hidden token counts,
  tool calls with their timestamps, flags, and the main and side task scores;
- the transcript and per-turn rows (`align_transcript.jsonl`, `align_turns.jsonl`);
- `power_trace.csv` and raw powermetrics output, the paired clock stamps and
  the anchor evidence;
- the summary metrics and the hazard flags (battery assist, thermal, contention, clock).

`desk` reads every episode bundle read-only into `PILOT.json` before the
harvest runs. For each episode it records the attributed energy per recorded
power channel, with its half-width, the number of segments and their sum,
plus the logged totals and the full totals. Across repeats it records the
spread of energy per cell. The native harvest then runs with `--non-claim`.

## Pilot success, as an instrument check

The session succeeds when all four checks pass. They are printed by `desk` and
listed in `PILOT.json` under `checks`:

1. **I1, all bundles readable.** Each of the 12 episodes has a readable bundle
   and an `Episode` record.
2. **I2, energy present.** Every episode has energy on at least one channel,
   with none of `power_unavailable`, `trace.missing`, `trace.ambiguous` or
   `clock_anchor_unresolved`.
3. **I3, attribution tiles the episode.** On every channel, the per-segment
   energies sum to the episode total.
4. **I4, greedy repeats are identical.** The three repeats of each cell
   generate the same per-turn token counts. If they do not, the repeats are
   not the same work and their energy spread is not a noise estimate.

The lead also reads these numbers. None has a pass bar:

- the energy SD and range across repeats per cell (the first estimate of
  `sigma_pair` for identical work, `docs/align/apple_path.md` "Detection power");
- episode wall time against the planning bound, and per-turn prefill and
  decode times (these size the next session);
- hidden-token counts by condition, and how many turns end on
  `turn_token_budget_reached`;
- battery-assist and thermal flags per member, against the BYTES 8B record;
- main and side task scores, to see whether an 8B model attempts the tasks
  at all.

A session that fails I1 or I2 has found an instrument fault. Fix the fault
before running another pilot. A session that fails I4 needs a ruling on
whether MLX decoding is deterministic across members before any repeat
spread can be used.

## Time budget per session

The planning bound is not a measurement (`registration/sizing_b5.json`, flag
`sizing.planning_bound_unmeasured`). It assumes decode at 60 tok/s, prefill at
400 tok/s, a context of up to 32,768 tokens rendered in full every turn, 1 s
of tool time per turn, and 478.6 s of member overhead:

- worst-case episode: 12 x (81.9 + 25.6 + 1) s = 1,302 s;
- align members: 12 x (1,302.2 + 478.6) s = 21,370 s;
- scaffold: 25 x 300 s plus 2 calibration captures x 900 s = 9,300 s;
- programmed span: 30,670 s (8.5 h); the plan writer's window maximum adds the
  T0, pause and wait allowances, giving 48,420 s (13.5 h).

Expected wall time is lower, at about 5 to 6 h: SHADE episodes on an 8B model
probably end in fewer turns with shorter contexts. This expectation is a guess
until pilot 1 measures it. One pilot session fits an overnight window. From
about 6-10 Nov, plan one session per night. After pilot 1, re-derive the sizing
row from the measured member times, the way BYTES did with `derive_sizing.py`.

## After the session (off the measurement Mac)

- Monitor scoring: run `ShadeMonitor` on the transcripts against a local
  OpenAI-compatible server, `mlx_lm.server` or llama.cpp, on the analysis
  laptop. It needs no paid API and no network beyond localhost.
- Tamper transforms (`joulewise/align/tamper.py`): deleting turns and hiding
  the scratchpad are post-hoc transforms of the recorded episodes. They give
  the energy-residual dry run its hidden-work cases.
- `joulewise/align/analysis/metadata_baseline.py` and `joulewise/align/energy_residual.py` may run on
  the pilot episodes only as a pipeline dry run. They print no claim.

## Abort and hold conditions

The existing chain, census, hazard monitor and harvest decide all of the
following. The pilot adds no new refusal:

- an agent process present at arm or during the session;
- AC loss, a charging excursion, a thermal level or contention: flagged or
  excluded under the BYTES rules;
- a member whose task cannot start (cache missing, upstream bytes changed, a
  missing package) stops at prepare as `runtime_unavailable`, before idle
  admission. The other members still run, and I1 fails.

## Open choices for the lead (see ALIGN-READY-1 NEEDS_RULING)

- Qwen3 thinking left on (the template default) or switched off.
- Hint on or off for sabotage, and whether to add a third pair.
- Whether the first session should be shorter: 2 pairs x 2 conditions x 2
  repeats = 8 episodes.
