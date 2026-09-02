# 86 — Ruling: shared disposition for multiple same-bundle supersession rows (SUPERSESSION-CROSS-CONSUMER-DIVERGENCE-01, phase 2)

Date: 2026-09-01. Input: the phase-1 exhibition (PR #260,
`tests/test_supersession_cross_consumer.py`) and its truth table
(`78-sol-supersession-truth-table.md`), which proposed "refuse: multiple
recognizable rows for X" for every multi-row shape and asked for a ruling.

## Why this is a parameter alignment, not a reinterpretation

The WRITER already carries the disposition. `require_occurrence_supersession_recordable`
(`joulewise/whole_window.py:2779-2785`) is documented as "Refuse a second
disposition for one bundle in one campaign log" and refuses to append a
second recognizable row for a bundle. The three READERS diverge from it:
the cooldown join refuses (`analysis_engine/inputs.py:2338-2358`, via the
complete-unknown payload), while whole-window membership
(`scripts/run_campaign.py` `_matching_supersession`) and membership binding
(`joulewise/whole_window.py:4703 _supersession_is_logged`) select a row, and
the D-093 `supersession_visibility_scan` reports clean. A reader that
tolerates what the writer refuses is the defect; the writer's rule is the
ruled shape, so aligning the readers installs it rather than changing it.

Counterfactual check against retained evidence (bench, 2026-09-01): across
all 33 `runs*/campaign_log.jsonl` files, 7 supersession rows exist and NO
bundle carries more than one — the refusal disposition voids no retained
evidence.

## Ruling

R-1. **Disposition:** for any bundle with MORE THAN ONE recognizable
`campaign_occurrence_supersession` row in one campaign log, every consumer
refuses — the cooldown join (already), whole-window membership, membership
binding, and the D-093 scan (which must REPORT the shape, not "clean").
Order-independent; byte-identical duplicates count as two rows; a valid
row plus an invalid same-bundle row is two recognizable rows (invalid
evidence stays visible as a competing disposition — truth-table row 4).
R-2. **Exactly one valid row** is the only selecting shape (truth-table row
1). No consumer may pick "latest" among several.
R-3. **Reason code:** one shared constant, `campaign_occurrence_supersession_multiple_rows`,
exported from `joulewise/whole_window.py` beside the existing
`REASON_CAMPAIGN_OCCURRENCE_SUPERSESSION_*` names and imported by the other
consumers (not re-typed).
R-4. **D-156 fences hold:** the cure is reader-side only; no historical log
bytes are rewritten, deleted, or reordered.
R-5. **Regressions:** the phase-1 exhibition tests are re-pointed from
"exhibits divergence" to "all four consumers refuse with R-3's code", one
test per truth-table row, plus the positive coherent row (single valid row
selects). Mutation table for the cure round: (m1) restore latest-wins in
`_matching_supersession`; (m2) restore `_supersession_is_logged` existence-only
membership; (m3) D-093 scan drops the multi-row report; (m4) reason code
retyped as a different string in one consumer — each must be killed by a
named test.

## Addendum (2026-09-01 19:10) — R-6: the D-093 persisted finding wire

Sol's phase-2 cure (`87-sol-supersession-cure`, rc=79 NEEDS_RULING, landed
uncommitted then committed at the bench as `6633dd94` on
`feat/2026-09-01-supersession-exhibit`) refuses a multi-row bundle in
`supersession_visibility_scan` by setting `status: "refused"` and attaching
`findings: [{reason_code, bundle_ids}]`. Two facts force a ruling:

1. D-093's audit row has no reason wire: `_SUPERSESSION_AUDIT_KEYS`
   (`joulewise/analysis_engine/artifact.py:55-62`) is an exact six-key set,
   so `findings` is rejected as an unrecognized key.
2. Without a finding, the refusal itself is inadmissible: the persisted
   validator rejects "authenticated equal counts cannot be refused"
   (`artifact.py:1159-1161`) — a multi-row bundle has `raw_count ==
   validated_count` (every row is individually valid) on an authenticated
   basis. So the reader-side cure cannot be expressed in the persisted
   artifact at all without a schema change. The wire is load-bearing.

**R-6 (ruled).** Admit `findings` as an OPTIONAL key of the audit row via
`_exact_keys_with_optional_group` (required = the six keys, optional =
`{"findings"}`). When present: a nonempty list; each element exactly
`{"reason_code", "bundle_ids"}`; `reason_code` ∈ the closed set
`{REASON_CAMPAIGN_OCCURRENCE_SUPERSESSION_MULTIPLE_ROWS}` (extension by
ruling only — record the set as a module constant next to
`_SUPERSESSION_AUDIT_KEYS`); `bundle_ids` a nonempty, sorted, duplicate-free
list of nonempty strings. `findings` present ⇒ `status == "refused"`;
`status == "clean"` ⇒ `findings` absent. The "authenticated equal counts
cannot be refused" check is relaxed ONLY when a nonempty `findings` list is
present. Retained corpora carry no persisted `supersession_audit` block
(`grep -rl supersession_audit runs*` → nothing), so no historical artifact
changes validity. Scope expands to `joulewise/analysis_engine/artifact.py`
and its pinning tests (`tests/test_analysis_claims.py`,
`tests/test_analysis_integration.py`); regressions required: (a) persisted
row with a valid finding validates; (b) finding with an unknown key /
unknown reason / empty or duplicated `bundle_ids` refuses; (c) `clean` +
`findings` refuses; (d) `refused` with equal authenticated counts and NO
findings still refuses (the existing rule survives). This is the FIRST fix
round on this defect (the prior round was a partial landing, not a failed
one), so no cold gate is triggered; the delta re-audit runs on a different
model (terra).
