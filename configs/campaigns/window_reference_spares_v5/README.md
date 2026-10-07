# Spare NEG-8 window references (spare-slot retry)

NEG-8 ruling of 2026-10-07 (decision 5; block-5 registration 0.12, "One retry,
by spare slot"). Each window reference stage lists spare members: copies of the
stage's first reference config, byte for byte except `run_id`, with the
stage's role and sentinel position. Three for each triplet, one for the
midpoint.

`<stage>_spares_<k>/` holds spares 1..k and an order manifest listing exactly
them. When a reference stage ends with k fewer succeeded members than it
planned, the block-5 chain (`joulewise/b5/chain.py`) runs `<stage>_spares_<k>`
once, immediately, into the same runs root, under the collection deadline. The
failed attempt's bundle is never touched; each spare measured is flagged
`member.retried`. The pack plan trees pin every file here through each
reference stage's `spare_retry` record.

Generated and verified by `python -m joulewise.b5.reference_spares --write`
and `--check`; never edit these files by hand.
