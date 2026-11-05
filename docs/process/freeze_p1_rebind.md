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

H1 (PR #649 fix round 1) chooses strict F3: only HEAD equal to the
checkout's registered analysis tag is admitted. An untagged descendant,
including one with a local ruling blob, refuses. A ruled scientific fix must
cite the owner's decision in `docs/decision_log.md`, record old/new trees,
and receive a new reviewed `b5/analysis-r<k>` tag and registration before use.
There is no runtime descendant-ruling authority: `ruled_descendants` is
removed and nonempty legacy ledgers refuse. Thus a runtime ruling cannot
name an unresolved decision or manufacture authority from its own blob.

`JOULEWISE_B5_FREEZE_REGISTRATION_COMMIT` is retired and explicitly refuses
when exported. A local annotated r3 tag plus any arbitrary registration
commit cannot replace `tags` or `active_analysis` in the checkout. This is
simpler than adding a second registration-tag trust chain, and follows F3's
existing re-tag/review procedure. Regression tests replay both forgery paths.
The mint's clean-tree check remains.

M1: after Phase 1 lands, **post-release paper and fill runs must execute
from a clean `b5/analysis-r2` checkout**, not main. This applies to
`build_results_fill_input.py`, `issue_reported_energy.py`,
`produce_b5_disclosures.py`, `compare_b5_recompute.py`, and `open_paper_input`
for every currently supported custody family. Main and unregistered block
branches refuse `analysis_descendant_unruled`. The F3 successor procedure
above is required for any later analysis checkout.

TODO A346: select the registration by block or supply role before extending
this custody seam to block 6/BYTES. Those role contracts are not yet wired;
this fix does not invent mappings. `require_origin_main=True` now honors its
name by requiring positive containment; it is independent of the registered
analysis gate, which paper custody requests instead (F2).

M2: the registration is independently pinned by full literal triples in
`RegistrationAuthorityTests`, cross-checked against the clerical identity
table in RUN_STATE item 146 and against all three annotated Git objects.
The prior record printed only abbreviated collection and r2 identities;
the original-analysis tag's existing message names its full commit/tree.
Full tag-object literals were not previously present in the cited ruled
records, so item 146 now records their explicit expansion. These reviewed
local objects are the source; this is not a new scientific release ruling.

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
| `joulewise/identity_pins.py` | `a102a7712559d62294db46836da9f900ee5281701ae366bf08c69287cc99e109` | `ad67633fbef04122ed3af9c034c6f8688015add31c89f300f1e3b38c61cba8fe` |
| `joulewise/paper_custody.py` | `f2d3273e71b30f7a55e8eafcf4ebf7eb0afce64946ae9c7cbc224e8748ea2966` | `067dcc7029c6452e053a7a2cc56e7db7ed1c05baa1bc33bb8381314f18a72a40` |
| `scripts/digest_pin_census.py` | `59be516f789a994d82d47a8ca3a79b45307265e43384b1f4ec3c55b089a604e0` | `4edac808870cc09ef798c02e749ee58efb7b3d9a4bfe7caca6a0c998e1d44c36` |
| `scripts/repin.py` | `ff4f2bbe9be92a0b7b6f7641a951fd361633516991ba63d99a141de027af4398` | `4d8deb934909208d8df5522d152be47f8871c157951f5147418848ff7ec19eb0` |
| `tests/b5_analysis/joined_s10.py` | `296abb2746977db1ca9733d5b1b87457d792728aa8e6695611b0821ec48df11c` | `bb2abe80acf1f3cc536a87cd30f98fbb80e5e76190c07c89e8e742d3ce9232b0` |
| `tests/b5_analysis/test_frozen_files.py` | `523f4ee386efc143fee98843104f60b2a9137d58083c17bcb0d5e7b325a4e19d` | `f114a7830ed1119756aadcae17cf5bd2563454a72627aa9ba027820232b30016` |
| `tests/test_digest_pin_census.py` | `5c83e04bc139f0b0d9b854e5d33394f98a95c0fb3557554be490d4ff8f9972ab` | `bdf8e98a552fda692c558e6d558060320c256df1629d7b83e3c4455681e7e0a4` |
| `tests/test_repin.py` | `b15f3fb7498b00b4f880fe1b081a93ecd4db1ebaf9fa6c83830c4ac5ef75f3ad` | `5e478dc8da10564d35c8eba77b784dadf8c76a2242006e40129d5f8befd091cb` |
| `tests/test_whole_window_inverted_corner_clamp.py` | `ab154bb78045669bce32b55177bb2101aa602ffc19a613650db069565ba25dfa` | `e648a0b1b7df84de10b494c895580c17f39b0a38440e974dd73952cd8596c9b0` |
| `tests/test_paper_custody.py` | `359b0930d78242f298c547f435d30535088493bf98d0c43d4665b709c69758b5` | `61b9a5cf247c96598c71c5ddc4a72b6fa7e3745c027b4f04420b5ba0251edd98` |

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

## Fix-round audit and small findings

The final before/after table includes the clamp and custody tests (B1/M1).
L2 checks collection imports at both the collection and active-analysis tags;
L5 clears/restores the exported registration override in test setup. L3
closes AttributeError from malformed registration at the anchor boundary.
L1 warns when a `#sha256/` pointer is absent and prints the registry-refresh
command after a family rewrite. It does not run a broad census automatically.

The B1 old-digest search and exact hit dispositions are recorded in
`docs/run_reports/2026-11-05-freeze-p1-old-digest-audit.json`. It checks all
predecessor file digests for PR-changed paths at the pre-PR base, r2 and the
initial implementation, over allowed source/config/Markdown files, beyond
Kind-P pins. Remaining occurrences are historical seal provenance, this
rebind table, and the retained informational Kind-B census row for the retired
test pin. That row is not admission authority (`is_checked` is false for
`source_digest`); L1 reports its absent pointer. Regenerating the whole census
would index forbidden measurement artifacts, so it is not done in this lane.
No other live old-digest constraint was found in the inspected tree.
