# W1 executing-review citations

2026-11-11. Citation record for `configs/b6/executing_reviews.json`.
This records existing executing reviews; it performs no new review and makes
no admission ruling. Original reports remain unchanged. Absolute custody
locators inside historical citations are text only.

The ledger's local-paper convention requires a file in `docs/align/reviews`
and its SHA-256 in `covered`. This citation record supplies that local paper;
each row also names the original report and the commit adding its relevant
review section. Full execution quotations and the omitted commit are in
`docs/run_reports/2026-11-11-w1-p1-reviews.md`.

## Original papers

**R — Fable 5.2 reliability reviews:**
`docs/run_reports/2026-11-10-w1-reliability-fable-review.md`.
The cumulative paper at `b192d57129dcba238ca81adaf0f37277693945a4` has SHA-256
`2d0854112f1617a83f6ea4d1f2cc8bee878339b26d90ecae2be81499e0f42da9`.
The following commits first add the sections used here:

| Section | Added by | Reviewed tree | Reported result |
|---|---|---|---|
| Original cold review, section 1 | `cc946a5cde243cc2e1ae4d8cc930091c922e0284` | `297629a0dc4a66797363d1dac23956f55536a061` | ADMIT-WITH-FIXES; synthetic modules and three review probes |
| Delta review, D1 | `c6d25d9636c0c4e7a9b19d86ad9c7f0d3c1c0573` | `ec0465fd1fd8227f9587d877d8762e6a9f2bd052` | ADMIT for branch 1; modules and review probes |
| Round-5 check, R1 | `734fc4433e2270c82e0a7d290aa10593deddb2d0` | `fe6912519ccc71715112fd9f98b10f1bfac38e1a` | ADMIT-WITH-FIXES; R5-1 remains before registration |
| RL-37 delta review, M2 | `b192d57129dcba238ca81adaf0f37277693945a4` | `248fd161eec67f81acf790337603a0607e738f49` | ADMIT; trace and listed modules |

**P — Fable 5.2 pre-signing review:**
`docs/run_reports/2026-11-11-w1-presign-fable-review.md`, first added at
`82c14c9eaa647089dce78ad9a45716ce45ce18c6`, SHA-256
`1645c7f2af94ffcc7c05fd1baea071bca3135fff7c38f720235e877e1559c103`.
The estimator-restore section says ADMIT and reports tests on the Sol branch;
the integrated-head confirmations include the adapter and harvest-off tests.
The paper does not print an integrated-head SHA. Its adding commit changes
only the paper; its code parent is `f41ee4e7c33784183ff5d69b2fdf0da6b5b224a9`.
Both that parent and the adding commit have the exact estimator and harvest
blobs listed below. This is an explicit provenance inference, not an assertion
that the reviewer printed that SHA.

**O — Opus 5.5 pre-signing second read:**
`docs/run_reports/2026-11-11-w1-presign-opus-review.md`, first added at
`4d2792f10306b3b197eb77e84e86d808feb868eb`, SHA-256 at that commit
`8f49ea4e1d4543772d86066fcd1c283189d4bc001776e1ec088b7afefe7f0bbd`.
It explicitly names reviewed head `82c14c9eaa647089dce78ad9a45716ce45ce18c6`.
The DRIVER-P9-W1 row reports reading the whole driver diff through
`b4a6c217f`; Checks row 6 reports executing closure and supporting modules.
The verdict is ADMIT for the integration commits, with signing gates retained.
The ledger citation here is limited to the unchanged driver blob, not those
other integration changes or any claim that signing gates passed.

## Exact number-bearing blob matches

Each pair was checked with `git rev-parse <commit>:<path>`. Only the path in
this table is registered for that commit; no row claims all changed files.

| Commit | Path | Matching review tree | Identical Git blob | Paper |
|---|---|---|---|---|
| `19a862dc8` | `joulewise/b5/driver.py` | `297629a0d` | `e83ff06b8d2b7c32e0347a95e6e80d6dd19dab81` | R, original |
| `2127e00bd` | `joulewise/b5/harvest.py` | `f41ee4e7c` / `82c14c9ea` | `0a733962780f0ce9b8ec002a0190ce7b11e8142e` | P |
| `454d78142` | `joulewise/b5/driver.py` | `ec0465fd1` | `da35ddc9372927d2f3ae4567f6cb132ece7c9add` | R, delta |
| `5dc2d4b48` | `joulewise/b5/driver.py` | `248fd161e` | `dbf8a5f0efc717f47478726abf753fd33c9efb98` | R, RL-37 |
| `b4a6c217f` | `joulewise/b5/driver.py` | `82c14c9ea` | `ff4fd76a6011b5790143f270d3d58fcd0e75750b` | O |
| `c6d25d963` | `joulewise/b5/driver.py` | `fe6912519` | `4e3cd6075ccdf5bfb75fa95e582829584be3bdd8` | R, round 5 |
| `ebe3d56a7` | `joulewise/adapters/powermetrics.py` | `f41ee4e7c` / `82c14c9ea` | `8fa6db3c444f6d27939728fc477c5e763a6306d3` | P |

`5bb152acc` is deliberately absent: its driver blob is
`d58ca9e4c7b648a2ce42c52ee0df08dbae574a8a`, different from the first
Fable-reviewed driver above. The later paper affirming A-01 is not an
exact-byte review of that earlier driver. No new review was commissioned.
