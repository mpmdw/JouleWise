# A346 Phase-1 rebind — 2026-11-05

Status: prepared for landing **after** the block-5 release. This is an
implementation record, not a new scientific ruling or a release declaration.

Authority: Ed's adopted F1/F2/F4/F7 model in
[freeze_by_commit.md](freeze_by_commit.md), RUN_STATE item 146, and the
2026-11-05 FREEZE-BY-COMMIT-01 Phase-1 brief. D-138 and RUN_STATE item 145
retain authority over the combined acceptance reissue. The frozen-component
repair authority is also quoted in D-190; no sealed registration is rewritten.

## Registered identities

[freeze_commits.json](../../configs/analysis/b5/freeze_commits.json) records
annotated tag object IDs, full peeled commit IDs and Git tree hashes for
`b5/collection`, `b5/analysis`, and the release tag `b5/analysis-r2`.
The analysis identity is **929fc65c9ce3ff82f0311d28acf76a682edd466f**, tree
**9e89d7ff48999416467129c03ea171fc3a1f3f83**. No tag is moved or created here.
The release executes its existing tag tree; these changes affect subsequent
main development. A same-commit tag replacement, lightweight tag, wrong tree,
unavailable object or unruled descendant refuses.

F2 enumerates every commit in `registered_analysis..HEAD`, including merged
side history. Every commit needs its tree plus a `docs/` ruling blob and
SHA-256 in `ruled_descendants`. That ledger is empty: this work does not
self-authorize its own branch as block-5 analysis code. Since a commit cannot
contain its own ID or tree hash, a ruled descendant's clean checkout uses
`JOULEWISE_B5_FREEZE_REGISTRATION_COMMIT=<full reviewed registration commit>`.
That later commit contains the ledger; the loader reads its exact Git blob
without checking out a new tree. Record this authority commit in the block's
invocation record. Branch names, filesystem overrides and missing commits
refuse. Without the explicit pin, the current checkout's registration is used.
The legacy
`require_origin_main` keyword is retained as a spelling of the new gate.
The mint's existing clean-tree check remains; its upstream-containment field
is still audit evidence, never admission authority.

## Rebind scope

- `joulewise/identity_pins.py`: F2 release identity replaces remote-main
  containment when a custody caller requests a release anchor.
- `joulewise/paper_custody.py`: requests that explicit registered-analysis
  anchor. Its inputs, validators, arithmetic and return formats stay intact.
- `scripts/digest_pin_census.py`, `scripts/repin.py`,
  `configs/pins/registry.json`: F7 replaces the Python tests' `#L<line>`
  locations with `#sha256/<literal>`. Kind-P target methods, families,
  refusal/reissue rules and literal multiplicity are preserved. Historical
  document line locations and JSON field pointers retain their meaning.
- `tests/b5_analysis/test_frozen_files.py`: F1 verifies the complete sealed
  collection inventory against collection Git blobs; each amended harvest
  against its own recorded commit; and the analysis tags' trees and seal
  documents. It never opens current collection/analysis source files.
- `tests/b5_analysis/joined_s10.py`: the synthetic harness supplies an
  annotated fixture tag and a fixture registration to the real F2 predicate;
  it no longer relies on a synthetic upstream-containment observation alone.
- `tests/test_digest_pin_census.py`, `tests/test_repin.py`: adapt to content
  locations and prove that line motion survives re-census and explicit repin.

The per-file old/new source digests below cover every changed existing code,
test and pin-registry file in the release tree. The collection seal's digests
are retained verbatim in its inventory and verified against `b5/collection`.
New modules, tests and registration metadata have no predecessor to rebind.

| Path | SHA-256 at analysis-r2 | SHA-256 after Phase 1 |
| --- | --- | --- |
| `configs/pins/registry.json` | `2482eee5eb846d597cf9d1e69893b41c2851bb8cb6acc4234345f79510eb190c` | `bfc1cef5724d1ec87e7816b48df83480ab52a5ecf33daa76021cdbdb1a5dd92c` |
| `joulewise/identity_pins.py` | `a102a7712559d62294db46836da9f900ee5281701ae366bf08c69287cc99e109` | `0f679b5e2609cc4f8e12acf38f8527fbbadaf1df4be6b51bfb3df50c56edc480` |
| `joulewise/paper_custody.py` | `f2d3273e71b30f7a55e8eafcf4ebf7eb0afce64946ae9c7cbc224e8748ea2966` | `eab2452bd5bd5092e3bf9a5c6ec4cb9de5dbbd1e51dbaa529fe10213318ecede` |
| `scripts/digest_pin_census.py` | `59be516f789a994d82d47a8ca3a79b45307265e43384b1f4ec3c55b089a604e0` | `4edac808870cc09ef798c02e749ee58efb7b3d9a4bfe7caca6a0c998e1d44c36` |
| `scripts/repin.py` | `ff4f2bbe9be92a0b7b6f7641a951fd361633516991ba63d99a141de027af4398` | `4ce661de4d7439d06c45b6822ab46a7a17c433c5423370373650bda46a1909ee` |
| `tests/b5_analysis/joined_s10.py` | `296abb2746977db1ca9733d5b1b87457d792728aa8e6695611b0821ec48df11c` | `bb2abe80acf1f3cc536a87cd30f98fbb80e5e76190c07c89e8e742d3ce9232b0` |
| `tests/b5_analysis/test_frozen_files.py` | `523f4ee386efc143fee98843104f60b2a9137d58083c17bcb0d5e7b325a4e19d` | `21d5664ec208281c85f43a7ef5d91f81e780115fd954798942a23d1a998d806b` |
| `tests/test_digest_pin_census.py` | `5c83e04bc139f0b0d9b854e5d33394f98a95c0fb3557554be490d4ff8f9972ab` | `bdf8e98a552fda692c558e6d558060320c256df1629d7b83e3c4455681e7e0a4` |
| `tests/test_repin.py` | `b15f3fb7498b00b4f880fe1b081a93ecd4db1ebaf9fa6c83830c4ac5ef75f3ad` | `7373df8cd28e63258fc36aae3135e53c91f2235d43f3916429346f4caf6a93ca` |

| `tests/test_whole_window_inverted_corner_clamp.py` | `ab154bb78045669bce32b55177bb2101aa602ffc19a613650db069565ba25dfa` | `e648a0b1b7df84de10b494c895580c17f39b0a38440e974dd73952cd8596c9b0` |

B1 (PR #649 fix round 1): retire the test module's worktree-byte pin on
`tests/b5_analysis/test_frozen_files.py`. F1's registered Git trees preserve
the original freeze independently of this test's evolving implementation.
The estimator-byte and live-acceptance checks in the clamp module remain.
The final fix-round report records the tree-wide old-digest audit, including
historical occurrences outside the Kind-P census.

## Calibration dependency: deliberately unissued

A178 is still `STAGED, not landed` in the kernel. `_anchor_coverage_ok` still
uses its original endpoint comparisons in `reduce.py`; no combined reissue
carrying A178 and L9-ENV-2 was found in the repository authorities inspected.
F4 therefore has an explicit `STUB_REISSUE_REQUIRED` record, null acceptance,
and `require_commit_scoped_calibration()` always refuses with
`calibration_commit_scope_reissue_pending`. No production call is redirected
to that stub. The issued acceptance, estimator files and current live-byte
staleness invariant are unchanged, as D-138 requires.

The owning D-138 transaction must issue `{commit, path: sha256}` acceptance,
verify in that commit's clean checkout, install the loader/trigger route,
and test clamp × one-ULP coverage together (including an inverted corner with
an endpoint within one ULP). It must not simply remove the live-byte check.
F4 activation and the tag/locked-environment reproduction rehearsal remain
open gates; this preparation is not a claim that either passed. Phase-2
pruning, L9-ENV-3 mirror removal and block-6/BYTES addenda are outside this
Phase-1 brief.
