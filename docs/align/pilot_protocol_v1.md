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

Each tool call hashes a canonical serialization of the public SHADE environment
before and after execution. The turn record retains both SHA-256 digests and
`state_changed`. The desk counts observed changes, prints counted and read-only
names separately, and excludes `end_task` from action counts even if a fixture
changes state there. After all calls in an `end_task` turn run, the episode ends
with flag `episode.end_task:<turn>`. Legacy pilot-1 calls lack observations and
retain their prefix rule (`list_`, `view_`, `search_`, `get_`) labelled
`classification: name_rule_v0`.

`desk` prints powermetrics pressure seconds clipped to the episode and OS thermal
readings inside the longer spawn-to-exit member interval. The chain check uses
the harvest roster's `target_precheck_path` values, skipping null paths exactly
as the harvest does; ALIGN's fallback cells have null paths. Request and phase
window eligibility/reasons remain separate diagnostics. Missing precheck rows
are never eligible. After harvesting, `archive/derived/exclusions.json` supplies
the member exclusion codes. Instrument checks and exclusions are both printed;
excluded members cannot produce `instrument_ok` or harvest `ok`. Missing harvest
exclusion evidence is disclosed as `exclusions_unavailable`. `desk --no-harvest`
uses an existing exclusions record and extracts without archive stages.

A context guard at turn 0 retains the prompt-check window and a succeeded,
flagged zero-generation bundle. If rendering takes less than two requested
sampler periods, `align_context_stop_observation` retains the remaining time:
`max(0, 2/power_hz - elapsed)`. The reducer requires two in-window samples.
This is an explicitly labelled observation interval with no generation. A missing or invalid
native position limit adds `model.position_limit_unread` and uses the spec cap.
Unset thinking/context controls are omitted from spec text and identity to
preserve pilot-1 bytes. Hidden tokens count emitted IDs between reasoning
delimiters, excluding trailing EOS, without retokenizing generated text.

The lead reads action counts and task evaluation diagnostics first, then end
states and token tuples, thermal onset and GPU clocks, eligibility reasons,
and energy with its uncertainty and per-turn work. Compare both arms' actual
progress before interpreting a difference in energy. One repeat per cell
estimates neither within-cell sigma nor between-window sigma.

Sizing inputs and arithmetic live in `registration/sizing_evidence.json` and
`sizing_b5.json`. Every generated turn's prompt is at most cap minus its output
budget. B/C retain decoded tokens, so episode decode is at most
`min(turns*budget, 40960-6347)`; 6,347 is pilot 1's smallest first prompt. If A
retains reasoning, the same aggregate limit holds; its planning bound keeps
the more conservative `turns*budget` allowance even if a template drops it.

The member fit is pilot-1 spawn-to-exit seconds versus episode seconds, plus
`300-57.6 = 242.4 s` for the new idle. It is compared with the unchanged runner
cap: `1800 + min(1500, remaining of 7200 session idle-wait seconds)`. All blocks
fit 3,300 s with the wait budget unspent. The cap can fall toward 1,800 s only
after repeated failed idle admissions on a nonquiet Mac; the chain already
physics-flags that condition, and the lead accepts this corner. No turn-count
reduction is needed under the guard-derived bounds.

Local-tool allowance is pilot 1's maximum summed `phase/align_tool_*` duration
per turn plus the measured hash-pair cost for the largest observed call count.
Disk bytes are fitted from complete uncompressed pilot-1 bundles against member
duration, with the largest positive fit residual added to each projected block
member. Measured scaffold bundle bytes are added once; capture plus backup gives
two peak copies. These transferred rates, context factors, overhead, tool and
disk laws retain `sizing.planning_bound_unmeasured`. Prepare stages the real
chain; the lead owns hardware rehearsal and final verification.
