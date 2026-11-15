# Cold review: `ops/2026-11-11-w1-p1-reviews` @ `54648b43a` (P1, executing-review rows)

Independent Opus subagent, read-only, 2026-11-11. **Verdict: ADMIT.** All seven rows hold under the exact-byte rule
(same blob at the commit and at the reviewed head; commit an ancestor of the head; no change to the path between).

| Commit | Cited review (paper @ sha) | Executed | Exact bytes | Quote |
|---|---|---|---|---|
| 19a862dc8 | Fable original W1 reliability review, cc946a5cd, head 297629a0d | 5 modules + 3 probes | yes | accurate |
| 2127e00bd | Fable pre-signing review, 82c14c9ea (head inferred; inference sound, see below) | repin, g2_phase_d, modules | yes | accurate |
| 454d78142 | Fable delta review D1, via c6d25d963, head ec0465fd1 | 13 modules + 4 probes | yes | accurate |
| 5dc2d4b48 | Fable RL-37 review M1/M2, b192d5712, head 248fd161e | trace regeneration + modules | yes | accurate |
| b4a6c217f | Opus pre-signing review, 4d2792f10, head 82c14c9ea | closure and boundary runs; full driver-diff read | yes (one-line docstring change) | accurate |
| c6d25d963 | Fable round-5 review R1, 734fc4433, head fe6912519 | modules + 4 probes | yes | accurate |
| ebe3d56a7 | Fable pre-signing review, 82c14c9ea | includes `test_adapters_powermetrics` | yes | accurate |

- Head-SHA inference: the review names f41ee4e7c as the last integrated piece; its Sol test head (cb67f5d4e) has the
  same powermetrics and harvest blobs, and the paper's estimator hash `70f47086…` equals `ebe3d56a7`'s file.
- Schema, append-only diff, citation-paper SHA-256 values all verified. The citation paper asserts no review that did
  not happen.
- `tests.b6.test_audit_record_fixes`: 8 tests, 1 failure, listing only `5bb152acc`.
- `5bb152acc`: no exact-byte executing review exists (only author/handoff reports). Observation for the lead: all 11
  lines it added to the driver survive verbatim at 297629a0d, which Fable's original review executed and affirmed; the
  ledger's first row already accepts a cumulative review of a later head. Whether to cite it is a lead decision; an
  independent A-01 executing review has been commissioned instead.
