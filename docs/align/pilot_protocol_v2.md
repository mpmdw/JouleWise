# ALIGN pilot 3

This is a non-claim cache and instrument pilot. The lead's pilot-3 ruling in
`docs/process_traces/2026-11-02-magistrate-e1308804/RECORD.md` (authority checkout
`rec-e1308804`) governs. Pilot 2's `pilot_protocol_v1.md` continues to govern
everything this document does not change. Hardware rehearsal precedes freezing
the collection span; fixture evidence is PROVISIONAL for native execution.

| Block | Model, MLX 4-bit | Thinking | Turns | Output budget per turn |
|---|---|---|---:|---:|
| A | Qwen3-30B-A3B | on | 12 | 4,096 |
| C | Qwen3-Next-80B-A3B-Instruct | template default | 20 | 2,048 |

Each block runs `spam_filter_update` and `bank_transfer_2`, benign and sabotage,
hint on, three repeats: 2 × 2 × 2 × 3 = 24 members. The cap remains 40,960,
limited further by the native model position limit. Before each turn, the full
rendered prompt plus output budget must fit. Every measured member uses
`prompt_cache="episode_prefix"`. Apart from this added field, every A/C episode
spec equals the matching pilot-2 spec, including seed 1. Repeat ordinals live in
the collection plan and tags, independently of the seed. Token IDs are discrete;
comparisons use exact equality, with no numerical tolerance.

A is contiguous, then C. Within each block, pair order is spam/bank, bank/spam,
spam/bank for repeats 1/2/3. Spam condition order is BS/SB/BS; bank is SB/BS/SB,
preserving matched opposite orders. There is one midpoint reference between
blocks. The 25 scaffold members and calibration bracket are unchanged. Each
align member idles 300 seconds, the existing cooldown cap. Processes and model
loads remain per member; ordering does not create a persistent model process.

The cache is owned by one measured episode, independently of warmup and other
members. Let P be the full rendered prompt IDs and K the IDs actually represented
in the native cache. Reuse C = LCP(K,P), leaving at least one fed token. A
trimmable cache is trimmed to C; both the library's returned trim count and all
available attention offsets must agree. For a non-trimmable cache, including
Next's ArraysCache/KVCache mix, only an exact represented prefix can be reused.
A rewrite discards the whole cache and rebuilds from the full prompt, recording
`untrimmable_rewrite` and `cache.rebuilt_untrimmable:<turn>`. Recurrent state is
never retained beside trimmed attention state. After generation, native offsets
witness how much of P plus emitted output IDs was consumed, including EOS.
Unknown or inconsistent accounting fails the member and invalidates the cache.

Per turn, logical `prompt_tokens=len(P)`, `cached_prompt_tokens=C`,
`Turn.context_tokens=C`, and `Turn.prefill_tokens=len(P)-C`. Full prompt/output
IDs, fed delta IDs and digest, cache classes, offsets, trims, rebuilds and fallback
reasons remain in custody. Prefill event metadata reports full, cached and fed
counts separately; setup events disclose reconciliation. The first-token phase
boundary retains its existing interpretation, including native asynchronous
lookahead. Logical throughput denominators are unchanged. The legacy
`prior_hidden_prefill_tokens` remains the rendered hidden-free counterfactual
token-count difference. Separate `cached_hidden_context_tokens` and
`fresh_hidden_prefill_tokens` annotate ID-delimited reasoning content. These
actual-work annotations must not become hidden-work predictors: energy-model
predictors continue to come from the specified visible log only.

The sampler's hashed `execution_policy` includes cache policy, whole-cache
fallback, effective context cap, accounting version and observe-only repetition
policy. Unset cache controls are omitted from spec text and policy identity,
preserving pilot-1/2 defaults. Actual hit counts are observations, not identity.

Repetition is observe only, with no stopping threshold. Each completed turn is
compared with the preceding turn using tool names, canonical arguments JSON and
byte-identical UTF-8 output. An identical call/output run emits
`repetition.identical_call_and_output:<run_length>`; equal output with changed
arguments emits `repetition.identical_output:<run_length>`. Runs start at two
observations, the minimum for an equality comparison. Distinct successful contact
additions are not loops. Multi-call turns compare the ordered complete call list.
Existing context, turn, output and end_task stopping rules remain.

The desk's I4 compares actual emitted ID sequences within cells. Fewer than two
comparable repeats prints `not_evaluated`, never pass. Energy spreads additionally
require equal full prompt IDs and token-accounting tuples. `desk --compare-session
<pilot2 root>` reads prior bundles without changing them and reports identical or
the first divergent turn per cell and member, comparing full prompt and output
IDs. Native greedy equality across cache shapes is an empirical hardware check,
not guaranteed by the fake-cache tests.

Thermal and contention retain their existing eligibility rules; the desk only
prints them. In particular, `thermal.os_level_nonzero` remains an exclusion.
The first observed nonzero OS sample is printed relative to both episode start
and episode end. The last recorded level at each turn start includes its sample
time and age, without interpolation or an invented freshness bar. Every harvest
flag is printed on one line per member, including contention, busy idle,
identity and battery. Battery discharged energy is read from the existing
withheld receipt. `model.identity_mismatch` is explained under non-claim null
runtime pins; it is not silently cleared. Phase-window reason counts are grouped
by phase kind. Short tool phases are never padded. Missing evidence stays missing.

State hashes still classify state-changing calls. The desk also prints
`acted_beyond_read_marking`, removing `get_unread_emails` from that action count
without changing its state-change classification. Bank progress prints observed
contact additions, attempted payment calls and observed email sends. Contact and
email counts require observed state changes; they are progress diagnostics, not
task scores. Bank score zero is accepted at these budgets: completing roughly
ten contacts, payments and emails needs about 30–35 one-call turns. These cells
remain because A/bank/sabotage is the costliest cached onset probe.

Sizing receipts are regenerated from pilot-2 session files with their SHA-256
digests by `registration/derive_sizing.py --pilot-session <root>`. Pilot-2 member
seconds follow OLS `519.235 + 1.151110 × episode_s`; the 300-second idle is already
included, so it is not added again. Disk bytes follow pilot-2 OLS
`212148182 + 470679 × member_s`; the planning upper disk law adds its largest
positive residual. The measured scaffold is 5,019 seconds and about 4.03 GB.
The tool allowance remains pilot 1's measured phase/hash allowance, about 0.083
seconds per turn, with its source digest retained.

The conditional cache planning envelope uses prefill ≤ cap + turns × budget
(90,112 A; 81,920 C), and decode ≤ min(turns × budget, cap − 6,347), with 6,347
the smallest recorded initial prompt. The prefill envelope assumes each rewind
is bounded by one output budget; unexpected whole-cache rebuilds can exceed it.
Rates are the slowest observed pilot-2 phase rates per retained block, including
throttled turns: A prefill/decode about 562/39.1 tokens/s, C about 754/57.6.
This is a transferred planning bound, not a physical worst-case guarantee;
`sizing.planning_bound_unmeasured` remains. Rehearsal must validate reconciliation,
timing and disk before the lead seals a span. Runner caps remain
`1800 + min(1500, remaining of 7200 session wait seconds)`, independently of this
arithmetic. No new waits or power thresholds are introduced.

Keeping pilot-2 trajectories and replacing their prefill time by cache-delta
time gives about 5.51 hours including scaffold; no cache savings gives 8.73 hours.
The conditional planning bound is about 11.60 hours. Expected capture is about
15.0 GiB; capture plus backup is about 30.0 GiB, with a planning bound about
49.4 GiB. `sizing_b5.json` carries the precise arithmetic. Reconciliation changes,
different trajectories and full-ID artifacts can change those transfers.
Generation preserves Mac-derived file identity pins and package observations;
inherited pilot-2 receipts are labelled as inherited, without asserting a new
local hash or sealed runtime identity. A fresh Mac derivation is also preserved.

The night can estimate pooled within-cell energy spread for identical work
(16 residual degrees of freedom across eight cells), per-configuration spread
(8 degrees of freedom), the five-term benign energy fit with nonzero cached
context terms, sabotage residuals beside it, thermal onset under cached duty,
and token identity across pilots. Interpret these with all eligibility flags.
Energy differences from pilot 2 describe cache savings only for identical work
and with both pilots' thermal/contamination status printed. The night cannot
estimate between-window sigma_w, a hidden-token causal effect size, or bank task
completion at these budgets. Thermal-safe episode length, dwell and duty cycle
are measured in rehearsal; they are not selected from fixture outcomes.
