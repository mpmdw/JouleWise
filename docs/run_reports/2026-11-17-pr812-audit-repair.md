# PR #812 qualification start audit repair

The Tier 2 [AGENT] assignment repaired the five findings from the Astra
audit of `0576ed76d`. The PR branch now ends at
`57ed7334ea7dbc24ed47dfbf70c29c41197c9f01`. This patch targets the
audit branch at `aeadb9122f9b95055408f87556cd7390058e1153`, whose six
item drafts match the audited `c84a47674` drafts. The lead owns the
audit-branch commit and qualification admission.

| Finding | Change | Regression |
| --- | --- | --- |
| C.4 hold bypass after rollback | `c3802e69d`, `57ed7334e` and the draft patch carry the inclusive lower bound and a wall sample bracketed by monotonic timestamps. The runner checks both bounds and the authorized date for the full projected start interval and the child's wall sample before creating output. | `test_handoff_refuses_a_rollback_into_the_batch_hold`, `test_handoff_refuses_if_clock_sampling_delay_can_cross_cutoff` and the Run handoff gate test |
| Watcher expiry during handoff | The draft patch adds watcher expiry to the minimum cutoff. `c3802e69d` and `57ed7334e` enforce that cutoff at the child. | Bash and Zsh watcher handoff and exact-expiry cases in `test_qual_gates.py`, plus `test_handoff_refuses_when_anchored_t0_crosses_exclusive_cutoff` |
| Fractional-second date rounding | `c3802e69d`, `57ed7334e` and the draft patch use whole seconds for Los Angeles date lookup. C.3 floors legacy decimal seconds and reads exact nanoseconds on new receipts. | `test_submicrosecond_t0_stays_on_its_exact_los_angeles_date` and the legacy and nanosecond C.3 receipt cases |
| Omitted qualification authority | `c3802e69d` requires the date and both bounds in both CLIs for a qualification kit. | `test_qualification_requires_authority_in_both_clis` |
| Child receipt authority | `c3802e69d` records the authorized date, inclusive earliest start and exclusive cutoff in `t0_authority`. | `test_child_receipt_includes_all_three_authority_values` |

## Re-pinned kits

| Kit | SHA-256 | Frozen paths |
| --- | --- | --- |
| cl-qual-01 | `d77768e391f5ea9f3d8cd92a3bc97f846cf05c09cf66494579481b75b2932236` | 38/38 |
| cl-qual-02 | `8fcda25963ea6a21fd26c81d8979e5ad27bec226f9ca46562d06861007f45666` | 38/38 |
| cl-qual-03 | `36a573d8533783edd8d1904f45aba98f6d36572798da6994ccc1e5d155859621` | 38/38 |

An independent rehash read all 114 frozen blobs at the new pin. Each
kit retained the same 38 paths and changed the hashes of the two entry
scripts. The generator re-bound all six items, their queues and their
plans to the new kits. GitHub's test-merge tree matches the pin's tree
`26fa7f97cde46bb47895c840a92d392b25c78a26`.

## Verification and handoff

- 105 focused tests passed with Python 3.13. The 91 pinned draft checks
  passed, including six synthetic six-leg spans.
- The pinned child CLI scenarios passed on all three kits. Tests used
  synthetic clocks and stubbed the launcher and host dependencies.
- The final draft wrapper passed 1,384 arm gate checks and 246 close/copy
  checks across Bash and Zsh, 74 shell syntax checks, 68 Python compile
  checks, 21 standing checks, nine Round 10 tests and 13 generator checks.
- The local canonical suite includes tests that send process signals,
  so verification used focused local tests and hosted CI. The fixture
  orphan census returned exit 2 because the environment denied `ps`.
- Qualification remains `HOLD_FOR_FIT_FREEZE`. The lead must complete the
  final-head test comparison, fresh independent review and outstanding
  per-kit and issue gates. [PR #812](https://github.com/mpmdw/JouleWise/pull/812) · [Final-head CI](https://github.com/mpmdw/JouleWise/actions/runs/44243301044)
