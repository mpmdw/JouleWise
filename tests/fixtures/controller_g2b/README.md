# Controller G2-b archived capture

`block3-pre/` preserves all seven files of the REAL Revision-5 pre capture at
`/Users/edr/night-archive/harvest-d117-g2a-prefill-probe-20261004T1305Z-r2/g2a-root/runs/instrument_validation/d117-g2a-prefill-probe-20261004T1305Z-cal-pre/`.
The files were copied into `/tmp/dd5-ctl/` before compression. The archive
was read only. Gzip compression is lossless (mtime zero); `provenance.json`
records each original SHA-256 and byte length, including the full 82 MB
powermetrics stream and both raw ioreg observations. No timestamps, binding
markers, pulse values, or recorded battery predicates were edited.

The tests decompress into temporary scratch. They build a synthetic launch
chain and calibration ledger around the original capture identity and use a
mock workload. Existing launch-fixture ARM/T-0 issuance, pack inspection and
boot boundaries are stubbed; lineage/session authentication, manifest and
receipt hash checks, battery authentication and stored-physics replay execute.
The forbidden finalized-post control explicitly changes only the identity
in a separate synthetic copy. These tests are desk regressions, not live
G2-b qualification or hardware evidence.
