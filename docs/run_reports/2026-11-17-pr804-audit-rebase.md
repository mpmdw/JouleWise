# PR #804 rebase on the Tier 2 audit repair

PR #804 started at `f4195f98d` and was rebased onto PR #811
`c40e953d2`. The two conflicts were in the shared child hook. The rebase
took #811's implementation, which includes the original #804 binding and its
test-discovery path resolution.

- I-01 drives CloudDocs upload polling to its deadline on the real offload
  seam. It observes exit 5 and an empty marker directory.
- I-02 drives a readback verification failure after CloudDocs reports idle.
  It observes exit 8 and the unconfirmed marker. I-07 will exercise the
  controller's downstream handling at its own gate.
- E-02 injects a pre-publication ENOSPC and an ENOSPC after the marker
  becomes visible. The retry reuses the same bytes and syncs before
  success. A focused test requires exit-class failure when both writes fail.

Python 3.13 cluster discovery ran 77 scenarios with 9 passes and 68
expected failures. Six additional collector and boundary checks passed.
The eight selected publication, SSD copy and pull tests passed under a
signal tripwire. The repeated-late-error regression also passed. Whole-suite
verification is the hosted CI run. Native qualification remains PROVISIONAL.

The I-01 NEEDS_SPEC in the earlier round 11 report is resolved. The next
observable is hosted CI at the rebased head, followed by lead delta
admission and the #811-first merge order.
