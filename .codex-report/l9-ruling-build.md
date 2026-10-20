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
