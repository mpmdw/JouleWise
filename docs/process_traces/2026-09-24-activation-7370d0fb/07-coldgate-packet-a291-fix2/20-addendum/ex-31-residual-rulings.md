# 31 — A291: magistrate rulings on 02d §10 residual details X-1..X-10 (representation)

- **X-1** ACCEPT the proposal. At `pack`, `blocks` are ordered by level ascending, then role order ("8B" first), then `k`. Singles are appended at a split in `j` order. `voided_block_ids` is appended in `block_ids` order. `terminal_refusals` is appended in `block_ids` order, then item order.
- **X-2** ACCEPT. A split parent keeps `retry_stage: whole_block` and is marked `superseded`.
- **X-3** ACCEPT. A single's `predicted_item_s` is `[parent.predicted_item_s[j]]`.
- **X-4** ACCEPT the specified float evaluation order: sums in item order; a planned position is `sum(indices in item order) / count`; a per-model mean is taken over parents in `roster.blocks` order. Digests must be reconstructible bit-exactly, and the `isclose` alternative is rejected.
- **X-5** CONFIRM the cell keys. `spread_exceeded` is a CELL property (45/10 §Q4, FT-10); record 25's word "per-level" was the magistrate's error. FT-10's "not set" is `false`. Both texts are installed literally, as §4.1 does.
- **X-6** ACCEPT INV-51 and INV-52, with `inv_id` strings as written in the headings.
- **X-7** CONFIRM `reschedule_without_culprit` (INV-35(a)) and `culprit_limit` (INV-35(b)), the ruled FT-1/FT-2 names, and `inv_35c` for (c).
- **X-8** ACCEPT. The constants come from 45/10 §Q3 and c0998fdb until AP-5M is adopted. The Q1 equality test binds to the adopted AP-5M text when it lands (lane A282).
- **X-9** ACCEPT. INV-40, INV-44 and INV-50's permutation clause are not checker-evaluable (they are implementation-source properties); the implementer's tests own them.
- **X-10** Brief 28 is repointed to 02d plus this record.
