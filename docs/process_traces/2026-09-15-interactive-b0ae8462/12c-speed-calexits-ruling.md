# 12c — TEST-SPEED-01 calexits pool: DROPPED (magistrate b0ae8462, 2026-09-15 23:00 PDT)

The seat (12b) audited concurrency honestly: the expensive corrected-writer cases perform a machine-wide census and
`WitnessSandbox.close` asserts globally that no owned fake sampler survives, so 17 cases including every CPU-heavy
writer must stay serial; pooling the remaining 55 cheap cases cannot deliver the projected saving, and the receipts bind
random custody paths/PIDs so the literal byte-identity bar does not even hold serial-to-serial. Ruling: the pool lever is
dropped. The calibration-exits job stays the execution floor (~11–19 min) until the fitter lever lands with the next
acceptance re-issue (12a). Cheap remaining cuts (git-fixture template, lazy CLI imports for the crash matrix) are
optional and not worth a seat tonight. The CI wall clock now depends on queueing (PR #340's 6×2 shards; the
one-interpreter-on-PRs proposal awaiting Ed's ruling).
