# D-156 blind refuter verdict — custody record

- Date: 2026-08-26
- Seat: blind Fable refuter (no stream context), commissioned by the magistrate
  after the S6 ruling packet and before implementation landed.
- Lenses: two, both returned **SOUND**.
- Subject: the five premises D-156 rests on.
- Custody note: this file is a lieutenant-authored summary of the verdict as
  relayed by the magistrate, with every cited line **re-read and confirmed by
  the lieutenant against `origin/main`** before it was written down. It is not
  a verbatim transcript of the refuter's prose.

## Premise table (every cite re-verified at the bench)

| # | Premise | Cites | Confirmed |
|---|---|---|---|
| P1 | A recorder re-run cannot be byte-identical: `utc_timestamp()` is stamped into every row, and `entry_sha256` covers every field but itself. | `scripts/run_campaign.py:5455`, `:971` (`utc_timestamp`), `:5463`; `joulewise/whole_window.py:2269-2272` | yes |
| P2 | Whole-window membership refuses on two same-bundle rows: `_matching_supersession` returns a row only when exactly one entry matches on `(bundle_id, campaign_policy_sha256, selected_occurrence, superseded_occurrences)`. | `scripts/run_campaign.py:4766-4784`, `:4837-4848` | yes |
| P3 | The cooldown join refuses independently, requiring `len(bundle_supersessions) == 1` before it will consult the selector; the selector's own guard is a second line of defence. | `joulewise/analysis_engine/inputs.py:2354-2369`; `joulewise/whole_window.py:2840-2842` | yes |
| P4 | The existing D-093 supersession audit compares **totals** (`raw_count == validated_count`) and is therefore blind to two *valid* same-bundle rows, which it reports as clean. | `joulewise/analysis_engine/inputs.py:1349-1373` | yes |
| P5 | The raw reader fails closed globally — returning `None`, not a filtered list — when a recognizable supersession row has no usable `bundle_id`, or when the log is unreadable or not object-only JSONL. | `joulewise/whole_window.py:2782-2786` | yes |

Supporting cites the refuter used and the lieutenant confirmed:

- `scripts/run_campaign.py:2757` — the campaign lock is `O_EXCL`-created, so the
  write-time guard genuinely runs under mutual exclusion; a concurrent second
  recorder cannot slip between the check and the append.
- `joulewise/whole_window.py:4609` (`_supersession_is_logged`) and `:4700-4714`
  — a **third** consumer, on the membership-binding path, with the same
  `len(matches) != 1 → None` shape. The divergence story therefore involves
  three consumers, not two; recorded here so the Q4 draft row cites all three.
- `joulewise/arm_readiness.py:205-215` (`LAUNCH_LINEAGE_REASON_CODES`, plus the
  sibling `R1_CUSTODY_REASON_CODES` / `R1_GIT_REASON_CODES` sets unioned into
  `READINESS_REASON_CODES`) and `:1083` (`LaunchLineageError.__init__`
  rejecting an unregistered code) — the house pattern is *sibling registries on
  one class shape*, which is exactly what D-156's refusal surface must follow.
- `scripts/run_campaign.py:8139-8141` — the single `error: {reason_code}: {msg}`
  printing path, exit 2.

## The three residuals the verdict attaches (magistrate-relayed, should-fix, each owed a regression)

**R-1 — the guard must be built on the fail-closed reader, not on a
`bundle_id` lookup.** If `supersession_entry_validation_results` returns `None`
for the target log — a recognizable supersession row with a missing or
non-string `bundle_id`, or an unreadable / non-object-only log — the recorder
must **refuse**, not proceed. A guard that merely scans parsed rows for a
matching `bundle_id` would step straight past a recognizable row the reader
itself cannot assign, which is the one case where "no match found" and "this
log cannot be reasoned about" look identical from the inside.
Cite: `joulewise/whole_window.py:2782-2786`.

**R-2 — do not widen `LAUNCH_LINEAGE_REASON_CODES`.** That frozenset is
documented as D-078's launch-consumption lineage vocabulary
(`joulewise/arm_readiness.py:1080`). `campaign_occurrence_supersession_already_recorded`
belongs in a **sibling registry on the same class pattern**, so that the
paper's disjoint-vocabulary claim — "the characterization vocabulary is kept
disjoint from the others, so that no coincidental refusal raised elsewhere in
the pipeline can stand in for a required characterization refusal"
(`docs/paper/draft-v1.md:742`) — stays true. A shared registry would make one
class emit two unrelated vocabularies.

**R-3 — regressions must cover two distinct rerun shapes**, not one: (a) the
identical-arguments rerun, and (b) a rerun **after a third occurrence**, whose
row carries a *different* `selected_occurrence` and a widened
`superseded_occurrences`. Shape (b) is the dangerous one: whole-window
membership would otherwise **accept** it (only the new row matches the expanded
declared set) while the cooldown join refuses — the cross-consumer divergence.
Proving refusal on (a) alone leaves the divergence-creating write untested.

## Disposition

All three residuals were folded into the S6 implementation contract as
should-fix items with named regressions. The verdict changed no ruled
semantics of D-156; it hardened the guard's input source (R-1), its vocabulary
placement (R-2), and its proof obligation (R-3).
