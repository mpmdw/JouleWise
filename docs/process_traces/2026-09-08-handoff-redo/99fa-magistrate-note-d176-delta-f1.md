# Magistrate note — D-176 integration delta F1 (2026-09-08 ~16:40 PDT)

The Astra execution delta (99ez) killed every seam mutation (a–h) on the integrated head 4d72e524 and reported one
blocker: pack refusal receipts written for GO-production refusals (pack-tree digest mismatch at GO; a higher-numbered
unconsumed ARM) carry `refusal.reason = launch_go_receipt_invalid`, which the receipt validator MODULE loaded from
main 99a42edb rejects ("is not registered"), while the integrated validator accepts it.

Disposition (magistrate, with rationale; forwarded to the second cold gate as context): the two GO codes
`launch_go_receipt_missing` / `launch_go_receipt_invalid` are D-176 §1's own ruled R-8 registry additions ("registered
before emission"); the frozen seams are `validate_receipt` and `_RECEIPT_KEYS` (byte-identical to main, confirmed by
Opus 99ew §5 and the delta's own byte comparison), and both registries differ from main by EXACTLY those two ruled
entries. A receipt carrying a ruled code is valid under the head that will run the night; "valid under main's
registry" is not a contract obligation. NOT a defect. The seat-2 ruling stands: driver-side causes use the registered
`night_probe_error` with the true cause in `refusal.detail`; GO-production refusals use `launch_go_receipt_invalid`
per §3. The second cold gate (99ey) may overrule.
