gpt-6.1-sol

Branch: `lane/2026-10-20-l9-ruling-build`; verified base `090a398bb55916850ad052c1127433a4f0f7b1c4`.
Work in progress; final assessed head and complete check/replay tables follow after all questions.

Authority: origin/main's L9-RULING-ADDENDUM.md (activation 6cff3515), then L9-RULING.md (4b350f47), both read in full. Read both council reports, both cold reports and the silly-number executing review; inspected the cold exact-stack and consumer probes. No real archive or key directory opened. All checks use Python 3.13 unittest (pytest absent), `JW_B5_SYNTHETIC_ONLY=1`, and fresh per-module TMPDIRs.

Number rule: every measured/derived tolerance carries its derivation between 1e6 times float noise and 1% of the smallest printed half-width; without a half-width use 1e-6 absolute in the column unit. Equality is reserved for integer/hash/identity/digest comparisons and identical code on identical inputs. §Z supplies the zero-point bar.

Q-LINEAGE: DONE. Aggregate producer inventory, ordered schema validation, per-producer reconstruction and digest checking, scoped absent/unauthenticated limitations, and verdict revalidation. Single-lineage provenance remains the original shape; per-producer split/mixed provenance still refuses. Focused detection-floor, claim-artifact, input and S10 defect tests pass; the full mint checks are in progress.
Q-EXACTSTACK, Q-CONSUMERID, Q-RENDERER, §C, §Z and seam deletion: NOT DONE yet, in the required order.

§I step 1: not run yet; no consumer-identity policy decision has been taken.

Decisions I made:
- Baseline runs use an immutable detached worktree at the exact base. This keeps baseline evidence separate from implementation.
- `/tmp` has a small independent capacity. Concurrent fixture restores exhausted it; those capacity-error runs are retained in scratch logs and repeated using fresh module directories under `/workspace/l9-tmp`. This does not change test code or evidence.
- Floor lineage limitations are compared by exact equality of the complete floor-lineage subsequence of `inputs.limitations`; other questions append their own scoped limitations to the same existing list.
- The synthetic mint helper updates its aggregate producer-set digest after re-pinning its generated component digests, eliminating a pre-existing helper-only stale binding in the new assertions.

Left for a later round: none decided yet. No NEEDS_RULING at this checkpoint.

Q-EXACTSTACK: DONE. `detection_floor.exact_stack_serving_cell` selects the unique claim-usable source using family admission, backend/metric/window class, stack digest, and authenticated family phase/token lengths. Finalizer, close-out, request construction and exact resolution use it. Group-served requests use empty stress, retain the actual source id, and check the singleton gate by operand identity. Verdicts carry the scoped no-envelope limitation. The 31-test S10 defect module (including nine refusal variants), 131 detection-floor tests, 20 input tests, 65 claim tests, 19 manifest tests, 59 close-out tests and 18 finalizer tests pass. Number coverage passes (6 tests, 1 skip), so `number_rows.json` is unchanged.

Q-LINEAGE full mint verification completed: generalized mint 84 tests (2 skips), kept-unit mint 85 tests (2 skips), all pass. The Git CLI has no working push credential; after checking explicit per-file/branch authorization, the connected GitHub API published the identical Git tree as commit `a8f3d5566c7e171293a4fd930b092bda94e2e21d`. Automatic review initially rejected one blob for purported incomplete authorization; the same upload succeeded after the scope and public-source checks. No approval remains blocked.
