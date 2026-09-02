# Supersession cross-consumer truth table — phase 1 exhibition

Status: **observed pre-cure behavior plus a proposal; no ruling and no cure**.

Notation: `o1`, `o2`, and `o3` are authenticated occurrences of bundle X.
`S1` selects `o2` over `[o1]`; `S2` selects `o3` over `[o1,o2]`;
`S2′` selects `o3` over `[o1]` and therefore does not chain across `o2`.
“Cooldown” is `campaign_cooldown_evidence`; “whole-window” is
`run_campaign._valid_supersession_entries` followed by
`_matching_supersession`; “binding” is `_basis_source_manifests`, including
its validator and exact-log-membership checks. For binding, the verdict row
supplies the named governing candidate once; the campaign-log bytes are the
same bytes seen by the other consumers.

| Same-bundle log shape | Cooldown join: observed | Whole-window membership: observed | Membership binding: observed | Test evidence | Proposed shared disposition (for magistrate ruling) |
|---|---|---|---|---|---|
| Single valid `S1`; ledger `[o1,o2]` | Selects `o2` (`verified=true`, manifest `02.json`) | Keeps `S1`; selects `o2` | With `S1` supplied, selects `o2` | `test_single_valid_row_all_three_consumers_agree` | **Select `o2`**: exactly one recognizable row, valid and exact for the full ledger. |
| Two valid chained rows, log order `S1,S2`; ledger `[o1,o2,o3]` | Refuses via complete payload: `result=unknown`, `verified=false`, `manifest=null` | Keeps both; exact matcher selects `S2` / `o3` | With `S2` supplied, selects `o3`; `S1` remains present in the same log | `test_legacy_log_selects_in_whole_window_while_cooldown_join_refuses`; `test_membership_binding_disposition_on_the_same_fixture` | **Refuse: multiple recognizable rows for X.** A predecessor-bound chain is separately unruled; choosing `S2` today is latest-wins conflict laundering. |
| Two valid rows `S1,S2′`, where `S2′` does not cover `o2`; ledger `[o1,o2,o3]` | Refuses via the complete unknown payload | Keeps both; exact matcher returns `None` | With `S2′` supplied, returns `None` | `test_truth_table_additional_multiple_row_shapes` (`valid_nonchain`) | **Refuse: multiple recognizable rows for X.** The rows also fail full-ledger coverage. |
| Valid `S1` plus invalid same-bundle clone; ledger `[o1,o2]` | Refuses via the complete unknown payload | Silently drops invalid clone; selects `S1` / `o2` | With `S1` supplied, selects `o2`; invalid competing log row is not scanned | `test_truth_table_additional_multiple_row_shapes` (`valid_plus_invalid`) | **Refuse: multiple recognizable rows for X.** Invalid evidence must remain visible as a competing disposition. |
| Duplicate identical valid bytes `S1,S1`; ledger `[o1,o2]` | Refuses via the complete unknown payload | Keeps both; exactly-one matcher returns `None` | With one `S1` supplied, selects `o2`; log membership is existence-only | `test_truth_table_additional_multiple_row_shapes` (`duplicate_identical`) | **Refuse: multiple recognizable rows for X.** Byte identity does not erase the second recorded disposition. |
| Same chained rows in reverse log order `S2,S1`; ledger `[o1,o2,o3]` | Refuses via the complete unknown payload | Keeps both; selects `S2` / `o3` | With `S2` supplied, selects `o3` | `test_truth_table_additional_multiple_row_shapes` (`chained_reverse_order`) | **Refuse: multiple recognizable rows for X.** Disposition must be order-independent. |

## D-093 observation

`test_d093_totals_audit_reports_clean_for_two_valid_same_bundle_rows` observes
`raw_count=2`, `validated_count=2`, `status=clean` for the chained `S1,S2`
fixture. The totals equality detects invalid-row filtering but not the
per-bundle multiplicity that causes the cross-consumer split.

## Proposal rationale — magistrate owns the ruling

The proposed common rule is: count every recognizable supersession row for a
bundle before filtering; select only when the count is exactly one and that
row validates and exactly covers the occurrence ledger; otherwise preserve
all bytes and refuse. This is the smallest order-independent rule consistent
with the cooldown join, D-156's preserve-and-refuse fence, and the rejection
of unbound latest-wins semantics. A future predecessor-bound chain, if ruled
under `SUPERSESSION-CHAINED-RECOVERY-01`, can define a new admissible shape;
phase 1 neither assumes nor implements it. The D-093 audit should also expose
per-bundle recognizable-row multiplicity so equal global totals cannot report
clean while consumers disagree.
