# ALIGN pilot 2

Pilot 2 is a non-claim capability screen: can the local models act on both
SHADE tasks? It runs now; prompt caching belongs to pilot 3. Raw pilot-1
bundles remain immutable. Thermal energy is screening evidence and never
supplies a sigma estimate by itself.

| Block | Model | Thinking | Tokens per turn | Turns |
|---|---|---|---:|---:|
| A | Qwen3-30B-A3B MLX 4-bit | on | 4,096 | 12 |
| B | Qwen3-30B-A3B MLX 4-bit | off | 2,048 | 20 |
| C | Qwen3-Next-80B-A3B-Instruct MLX 4-bit | template default (no thinking mode) | 2,048 | 20 |

Each block has `spam_filter_update` and `bank_transfer_2`, benign and
sabotage, hint on: 3 × 2 × 2 = 12 episodes, one repeat. The shared cap is
40,960 tokens, even for Next. Before each turn, rendered prompt tokens plus
the output budget must fit the smaller of that cap and the model config's
`max_position_embeddings`. Exceeding it ends the episode with a flag.

Pairs stay adjacent. Spam/bank condition orders are BS/SB, SB/BS, BS/SB in
blocks A/B/C. Models are contiguous. The existing campaign uses a fresh
process and MLX load per member; a persistent load per block is a separate
runtime change, not provided by ordering. The pilot-1 scaffold stays:
calibration bracket, 18 NEG-8 bound members and derivation, three start,
one midpoint and three end references, closing calibration, harvest.
The midpoint follows A to keep configuration blocks intact.

Align members idle for 300 seconds, the cooldown policy's own `cap_s`.
Scaffold idle is unchanged. The longer idle standardizes the start; it does
not prevent thermal pressure during a long episode.

`desk` prints every member's thermal-pressure seconds clipped to the episode,
the reducer's window eligibility and reasons, time-weighted active GPU MHz,
end state, tool names by turn and state-changing call count. Read-only calls
are the `list_`, `view_`, `search_`, `get_` families of the recorded SHADE tool
schemas (or pinned definitions for old bundles). Unknown tools are printed.
It keeps instrument checks alongside chain eligibility; an ineligible member
cannot produce an overall `instrument_ok`. Repeat spreads include per-turn
energies and a thermal-ineligibility marker. Blocks are distinct work, not
repeats. `desk --no-harvest` extracts without running archive stages.

The lead reads action counts and task evaluation diagnostics first, then end
states and token tuples, thermal onset and GPU clocks, eligibility reasons,
and energy with its uncertainty and per-turn work. Compare both arms' actual
progress before interpreting a difference in energy. One repeat per cell
estimates neither within-cell sigma nor between-window sigma.

Sizing inputs and arithmetic live in `registration/sizing_evidence.json` and
`sizing_b5.json`. Member overhead and scaffold are measured from pilot 1;
BYTES short-context rates are measured. Their long-context transfer, the
one-second local-tool allowance, new-model overhead transfer and disk budget
retain `sizing.planning_bound_unmeasured`. Prepare stages the real chain;
the lead owns the hardware rehearsal and final verification.
