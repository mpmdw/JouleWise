# Cold-gate packet — D-166's prefill rule under the measured projection (mechanically assembled, 2026-08-30)

Assembled by the T28 magistrate for a COLD instance. Trigger: the questions
below interpret and possibly amend a ruled verdict (D-166 R-2), which is a
mandatory cold-gate matter; the loop-immersed magistrate does not rule them.

## 1. The ruled text (verbatim, `docs/decision_log.md` D-166 index row)

> `_v5` prefill length fixed from the G2 shakedown record (shortest of
> 512/1024/2048 with ≥3 overlapping records, margin ≥5, in every small-model
> member), pre-registered before the mint.

Source ruling: `docs/process_traces/2026-08-28-workload-consult/04-MAGISTRATE-RULING.md`
(three blind seats; read its R-2 section and each seat's prefill discussion).

## 2. The code fact

`joulewise/window_duration_margins.py:801-803` defines the repo's only field
named "margin" for this quantity:
`sample_count_margin = overlapping_power_interval_count − MIN_PHASE_SAMPLES`,
with `MIN_PHASE_SAMPLES = 3` (`joulewise/reduce.py:116`). Under that
convention "margin ≥ 5" means overlapping-record count ≥ 8. The plain-English
parse of the ruled sentence makes it count ≥ 5. Note both readings make the
sentence's "≥3 overlapping records" clause redundant (count ≥ 8 or ≥ 5 both
imply ≥ 3), so redundancy does not discriminate.

## 3. The measured projection (PR #245; `docs/paper/round7/prefill-resolvability-projection.{md,json}` on branch `paper/prefill-resolvability-projection`)

From 1,127 retained bundles, all three lengths DIRECTLY measured for the
small model (Qwen2.5-1.5B), records tile gapless (count = floor(D/S)+1,
validated on all 7 measured groups; 1127/1127 label agreement with the
production reducer). At the named 1.133× Qwen3-slowdown assumption:

| tokens | guaranteed / typical / best count | count ≥ 8 (A) | count ≥ 5 (B) |
|---|---|---|---|
| 512 | 2 / 3 / 4 | fails | fails |
| 1024 | 3 / 4 / 5 | fails | fails |
| 2048 | 5 / 6 / 8 | fails on guaranteed; typical 6 | clears |

Measured Qwen2.5 minima: 512 → 3 (2 in suite items), 1024 → 3, 2048 → 6.
4096 (outside the ladder, measured): counts 10–11, clears both readings; it
costs ~21 s added generation across 40 members. Sensitivity runs one way: a
FASTER Qwen3 (plausible for a newer architecture) lowers every count.
Relevant anomalies from the same analysis: no retained 256-token evidence
exists (every 256 figure in the consult was extrapolation), and one consult
seat's "4.39× prefill ratio" is an energy ratio misused as a duration ratio
(measured duration ratio at 128 tokens: 2.15×).

## 4. Context the seats had

Reviewer-panel finding D1 (`docs/process_traces/2026-08-28-reviewer-panel/04-SYNTHESIS.md`):
the old p256 arm was "designed to land ON the resolvability threshold," and
the paper must state projected overlap counts and the contingency. D-166's
ladder was ruled without the measured projection now available.

## 5. Questions for the cold instance

Q1. Which reading of "margin ≥ 5" binds — the repo field convention
(count ≥ 8) or the plain-English floor (count ≥ 5)? The pre-registration must
be numerically unambiguous before the mint.

Q2. Given the projection, does the ladder stand as ruled (with the
exhausted-ladder refusal branch live and stated in the paper), extend to
4096, or otherwise amend? Constraints: the G2 shakedown MEASURES the real
Qwen3 counts before any selection executes (the projection is expectation,
not outcome); pre-registration must fix the selection RULE, not the answer;
D-122's sizing rationale (prefill delta must clear the ~5 J practical bar
with margin — 256-token projection ~11.6 J) bears on whether longer prefill
harms or helps the science; adding 4096 costs ~21 s of generation per the
projection.

Q3. If the ladder is amended, state the exact replacement sentence for the
D-166 index row and what the `_v5` generator's pre-registration object must
encode (the generator currently refuses to finalize on an unresolved prefill
length; see PR #241).

## 6. Custody

The cold instance's ruling lands as `01-COLD-RULING.md` in this directory; an
Opus contract-lens refuter reviews it (`02-refuter-opus.md`) before the
magistrate ratifies. The magistrate may overrule only with written dissent Ed
sees (rule 11).
