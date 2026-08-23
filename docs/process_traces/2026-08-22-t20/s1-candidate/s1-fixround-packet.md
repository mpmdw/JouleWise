# S-1 COMBINED FIX ROUND — LEAD PACKET

Worktree `/Users/edr/code/JouleWise-wt-s1`, branch `impl/s1-candidate`, base `c1b87f6`.
Stream B harvested from `/Users/edr/code/JouleWise-wt-s1b` (branch `tmp/s1-fixtures`).

## Magistrate rulings applied (2026-08-23)

**R1 — S-0 acceptance re-founded.** The 21-test flip addendum is STRUCK from S-0's
acceptance: it encoded the disproven S0-BLOCKED theory, and the measured set is empty,
so it gated nothing. S-0's acceptance reverts to its primary, always-authoritative
form — the runsheet r2 §5 proving-obligations checklist (r4-2/V-2 obligations + the
full probe battery + the D-151/marker additions), which never depended on fixtures.
The runsheet r2 §5.1 amendment striking the addendum is a PENDING LEAD EDIT, applied
by the magistrate at the pre-execution read of the runsheet. This packet references it;
this round does not touch the runsheet.

**R2 — historical-pairing test.** Neither retired nor reconstructed now. The property
is real; reconstruction needs real `_v4`→`_v3` receipt chains that exist only post-S-0.
Sol's reconstruction design is recorded below and assigned to FIXTURE-MODERNIZATION-01
as its post-mint item. The honest structural skip stands, with a pointer to that row
applied at `tests/test_arm_readiness_lifecycle.py`.

## Recorded design (R2 post-mint item)

Replace the static `_PROFILE_BY_PACK` map-membership assertion with an authenticated
runtime `_v4`→`_v3` predecessor proof, supplying a valid synthetic family-publication
marker. Rationale: predecessor-chain authentication remains safety-relevant, so the
test should be reconstructed rather than retired — but the false map-membership
assertion must not be preserved in any form.

## Measured partition (independently re-verified by the lead)

| Class | Count | Meaning |
|---|---|---|
| `S0-BLOCKED:` | **0** | No test is unblocked by S-0's byte mint. |
| `STRUCTURAL-BLOCKED:` | 17 | 14 fixture-schema + 3 named singletons. |
| `CRASH-BLOCKED:` | 4 | ACID T-0 tests riding the pre-existing SIGABRT. |

Zero `@unittest.expectedFailure` decorators remain anywhere in `tests/`.
Enumeration is mechanical and enforced by `tests/test_s0_blocked_enumeration.py`.

The 14 fixture-schema tests stop at `joulewise/arm_readiness.py:5330`
(`legacy generic freeze evidence may not enter the R1 lifecycle`) because
`make_go_fixture` authors legacy generic evidence while R1 requires content/execution
receipt schemas. Minting `_v4` pack bytes changes neither conjunct — independently
reproduced by two seats.

## Paste-ready kernel rows (register in the next kernel wave)

| A84 | FIXTURE-MODERNIZATION-01 | P3 Backlog | READY [AGENT] | Modernize the arm-readiness test fixtures so `make_go_fixture` authors R1 content/execution receipt schemas instead of legacy generic freeze evidence, unblocking the 14 STRUCTURAL-BLOCKED tests that stop at `joulewise/arm_readiness.py:5330`, and reconstruct the historical-predecessor test on real post-mint `_v4`->`_v3` receipt chains. | The fixture-schema blocked class is cured and the historical-pairing property is proven on real chains, non-gating for S-0. Evidence: `make_go_fixture` authors R1 content/execution receipt schemas and the 14 tests carrying `STRUCTURAL-BLOCKED: synthetic fixture authors legacy generic evidence` flip green with their skip decorators removed; `tests/test_s0_blocked_enumeration.py` asserts the reduced partition and still finds zero `expectedFailure` decorators; POST-MINT ITEM: `test_historical_predecessor_resolves_and_still_anchors_the_chain` is reconstructed as an authenticated runtime `_v4`->`_v3` predecessor proof with a valid synthetic family-publication marker, replacing (never preserving) the false `_PROFILE_BY_PACK` map-membership assertion. Authority: [S-1 combined fix round magistrate rulings 2026-08-23](docs/process_traces/2026-08-22-t20/s1-candidate/MANIFEST.md). Fence: The four r6-pinned estimator sources stay byte-identical; every WRITE_SCOPE authorization checks that list first (Standing frozen-surface hazard). Note: NON-GATING for S-0 — S-0 proves the transaction on REAL R1 artifacts in its clone, not on fixtures. Created when the S0-BLOCKED theory was disproven by measurement (partition measured 0/17/4); the 21-test flip addendum was struck from S-0 acceptance at the same ruling. The post-mint item unblocks only after S-0 mints the `_v4` generation. |

| A85 | MLX-ACID-SIGABRT-01 (necessary but NOT sufficient for the four CRASH-BLOCKED tests — they also need A84 FIXTURE-MODERNIZATION-01; delta re-audit S1D-3) | P3 Backlog | READY [AGENT] | Cure the pre-existing process-level `SIGABRT` (exit 134) at `joulewise/adapters/mlx_runtime.py:1159`, reached under pytest via the four ACID tests in `tests/test_arm_readiness_evidence_t0.py`, which aborts the interpreter at ~9% of a full-suite run and makes those tests uncollectable rather than merely red. | The full repository suite runs to completion under pytest with no process-level abort and no deselection of the four ACID tests. Evidence: The abort at `joulewise/adapters/mlx_runtime.py:1159` no longer fires under a full pytest run; the four tests carrying `CRASH-BLOCKED:` have their skip decorators removed and are collectable; `tests/test_s0_blocked_enumeration.py` asserts the reduced partition. Authority: [S-1 seat verdict item 15 + S-1 combined fix round 2026-08-23](docs/process_traces/2026-08-22-t20/s1-candidate/MANIFEST.md). Fence: NOT a branch regression — reproduces at merge-base `5523003`, verified by extracting the base tree with `git archive`; any cure is adapter-side and must not touch the four r6-pinned estimator sources. Note: An `expectedFailure` marker cannot contain a process-level abort — a test that kills the interpreter does not make the suite green, it makes it uncollectable. That is why these four are `skip`, not xfail. With the four deselected the suite completes: 6 failed, 3763 passed, 95 skipped, 4 deselected, 17 xfailed, 19674 subtests passed in 2904.34s (independent seat, base-parity). |

## Suite-radius truth for MANIFEST §9

Independent seat, full pytest at base parity, four aborting tests deselected:
`6 failed, 3763 passed, 95 skipped, 4 deselected, 17 xfailed, 19674 subtests passed in 2904.34s`.
Two of the six failures are a pre-existing non-deterministic flake in
`tests/test_calibration_exits.py` — unmodified on this branch, failing at base `5523003`
with a different byte diff each run (it captures an ambient process command line).
Not a branch defect.

The prior `MANIFEST.md:617-620` figures (`failures=2, errors=2, expected failures=21`)
were a `unittest` run over a narrower radius (1,368 tests, 13 min) and do not
characterise the repository.
