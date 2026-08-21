# Errata — 2026-08-20 go-session custody

Corrections to custodied verbatim reports. The originals are records of what
the tool emitted and are not edited; this file is the correction channel.

## E-1: `rh-impl-report.md` workspace branch field is wrong

`rh-impl-report.md:14` records `"branch": "impl/d144-followups-prewindow"`
with `head_start = head_end = 42bd318`. The RECEIPT-HISTSEM-01 implementation
that report describes lives on branch **`impl/receipt-histsem` @ `60ba2e9`**
(pushed, labelled do-not-merge). The report's pathspec and verification
records are internally consistent; only the branch metadata is stale (the
session inherited the field from the prior lane). Anyone harvesting by branch
name must use `impl/receipt-histsem`.

Filed 2026-08-20 by the T19 successor session (lead), caught by the T18/T19
run-report drafter's evidence pass; verified against the custodied file
before filing.
