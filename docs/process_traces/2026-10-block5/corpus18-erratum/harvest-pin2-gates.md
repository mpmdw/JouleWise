# The harvest program of the second seal: gate record

Magistrate activation 1aed44f9 (Opus 5.5, headless), 2026-10-09. Structure only. The seats' full reports
are in `/Users/edr/night-archive/b5-consults/corpus18-build/` on the measurement Mac.

The change is the desk side of the block 5 corpus erratum (cold ruling `RULING.md` in this directory,
section B): `joulewise/b5/harvest.py`, one method and the two places that read its result, and tests.
`joulewise/whole_window.py` and `scripts/harvest_b5_window.py` are unchanged from the first harvest pin.
Pinned commit: `224a264c5faaae90cdf56118df37e773a932700b`.

## Who did what

| Step | Seat | Result |
|---|---|---|
| Build (`05897b24c`) | Sol 6.1, effort xhigh (`sol-desk-side.md`) | the capped clean bound, 13 new tests; it disclosed that the always-on clean bound let a stored NEG-8 condition clear |
| Correction and executing review (`49265927d`) | a second Sol 6.1 seat, effort xhigh, which did not write the first commit (`sol-desk-fix1.md`) | the re-screen guard restored against the sealed text; a second gap found and closed (an unavailable clean bound fell back to the uncapped one); the cap made a named constant; review of the rest of the diff: no path for a capped member's energy into the bound, the order comes only from the pinned order manifest |
| Cold pass 1 at `49265927d` | Fable 5.1, new session (`FABLE-desk-pass.md`) | `PASS-WITH-FINDINGS`: one major (a failure disclosure lost when the re-screen does not run), one minor (a wrong count in a record after an order-check failure), six recording-only |
| Fixes (`273fc48db`) | Sol 6.1, effort xhigh (`sol-desk-fix2.md`) | both fixed; two parent assertions restored byte for byte; every assertion changed since the first pin dispositioned (two restored, two equivalent, seven superseded by the rule that the re-screen always runs) |
| Merge of the second seal commit (`d58913476`) and test alignment (`224a264c5`) | the lead (merge), Sol 6.1 xhigh (`sol-desk-merge.md`) | tests use the committed 18-member corpus; the 12-member case is built explicitly; no production change |
| Cold pass 2 at `224a264c5` | Fable 5.1, new session (`FABLE-desk-pass2.md`) | `PASS-WITH-FINDINGS`: no blocker, major or minor; six recording-only |

## Findings of the last cold pass and their dispositions (all recording-only; no fix round)

| # | Finding | Disposition |
|---|---|---|
| 1 | The sealed text does not say what happens when the order manifest is unreadable, unpinned or changed; the code refuses the bound | Flag: the code fails closed |
| 2 | A physics flag on a member beyond the cap counts as "a corpus member dropped for physics" and so lets the re-screen decide over another stored condition, although the deciding twelve are unchanged | Flag: it matches the sealed sentence literally; a tightening would be a text change and goes to the erratum lane if it is ever wanted |
| 3 | The clean bound keeps the in-window bound's derivation time, which can be later than the last kept member's end by the span of members 13 to 18 | Flag: minutes against a 24-hour horizon; unchanged behaviour |
| 4 | Route 2 checks order against `settled_corpus.json`, the cap orders by `order_manifest.json`; they agree and a test asserts it | Flag |
| 5 | The allowance consumer accepts a collected-subset bound on arithmetic alone | Flag, older than this change and unreachable from this harvest |
| 6 | Two keys of the record both hold the bound's member count | Flag: naming |

## Whole suite

`harvest-pin2-suite-summary.txt` beside this file: head `224a264c5`, six shards and the two exclusive
modules. Two wall-clock tests failed inside the parallel run and pass alone. One test fails on the lane by
construction and is not a defect: `tests.test_repin` compares `joulewise/whole_window.py` with the digest
the sealed inventory holds for it, and the lane's copy is the harvest lane's own (unchanged since the first
harvest pin), not the sealed one. For that reason the lane is not merged into main, exactly as the first
harvest lane was not: main keeps the sealed bytes, and the desk root is a separate checkout at the pinned
commit. Every other module passed.

## What this pull request changes

Documents only: Addendum 2 of the seal record, with the line a program reads (`B5-HARVEST-PIN:` and the
pinned commit), this record and the suite summary. The pinned commit is on the remote branch
`lane/2026-10-09-harvest-corpus-cap`.
