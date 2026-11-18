MERGE

I audited pushed head `134860d4a` with synthetic inputs and reproduced the prior findings on their reported revisions.

- **[HIGH] [REFUTED] Premature W1 deletion.** Both the retired and current clients retained all ten originals and the pack before pushed desk finality, on automatic and explicit release. Fresh and cached paths refused `archive/`, `PILOT.json`, and `desk.json`.
- **[MED] [VERIFIED] The quiet-start receipt includes the private timing span.** The documented `triage` command emitted both `raw_bytes` and `compressed_bytes`. Committing that receipt verbatim would publish both sizes. Keep the span out of the committed receipt. [Synthetic reproduction](/private/tmp/jw-desk-audit-r4.A8m1ut13/triage_receipt.py)
- **[MED] [VERIFIED] The runbook command fails in zsh.** Section 1d assigns to the read-only variable `status` and exits 1 before invoking offload. Renaming it `checkout_status` passed the same probe. [Runbook line 106](https://github.com/mpmdw/JouleWise/blob/134860d4a3a8d712e570a7bd00c5d2fa82c6d8d0/docs/align/v4/HARVEST-OFF-MAGISTRATE-RUNBOOK.md#L106)

All ten frozen blobs matched `b2e01464d` byte for byte. `2c0c766f9` isolates the U3 fix and its test. The head exporter matches `5a325b2ee`. The registered e01/e09 pair passed, and off-list e01–e04 were refused after a working-tree roster edit.

E2, Sol3, and Sol5 passed on head and PR base. With staged synthetic harvest output, E2 failed on `5e97809` at the exposed digest. On `7476ce4`, Sol3 failed at the printed count and Sol5 at the refusal message. The older rerun guard also stopped the second desk.