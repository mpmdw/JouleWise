# PR #799: gate 4 dispositions, Sol round 5 (2026-11-15)

User-directed priority: finish the paired #799/#800 review findings before ordinary queue work. No phase exit-checklist matrix row exists for this PR fix round. This is [AGENT] work only. No MBP contact, measurement, custody, energy or power files were opened. No merge.

The supplied worktrees' .git pointers lead to a path denied by the environment; reads were retried and remained denied. Builds use clean detached worktrees at the exact handoff heads in /Volumes/JW-EXT/scratch/sol-ctl-r5/, backed by the accessible mythos-repo clone. Original worktrees remain untouched.

## Findings

Gate-4 reports: /Volumes/JW-EXT/scratch/mythos-gate4-800-799/REPORT.md and /Volumes/JW-EXT/scratch/opus-gate4-800-799/REPORT.md. Authorities: RL-172(c)(g)(i), RL-173; design 15.13-15.14.

| Finding | Disposition |
|---|---|
| Mythos F10 / Opus 6 (T11 residue) | NEEDS RESEARCH-LEAD RULING. A valid rerun_of uses a new span id; the current draw remains unchanged. Does a disposed first attempt consume the always-drawn place? Options: count the executed attempt; or resolve rerun chains to preserve its first place. Recommend the latter; no implementation before ruling. FORMAT now states the actual behavior. |
| Mythos F11 / Opus 12 (history assertion) | FIXED auditability and invocation: verdict records history_empty_asserted under its hash; history refusal preserves the verified bundle transport; FORMAT gives first-record flag and host-local lock setup. Missing lock parent returns rc 4. Remote emptiness remains an explicit operator assertion; a stronger fetched-prefix proof requires an owner contract. |
| Mythos F12 (same refusal) | FIXED: replace declared desk-local roots with stable roles in diagnostic details, preserving relative paths, codes, hashes and counts. Different semantic failures still disagree. |
| Mythos F12 / Opus 11 (code closure) | FIXED: desk_code covers all 14 repository files in the desk import closure, including kit_v11 and the top-level package imports. #800 separately checks the whole checkout at arm and close. |
| Opus 7 (latent campaign-scope history) | DEFERRED, not claimed supported. All nine current kits use span scope. Campaign-scoped stops need a full authenticated shared history contract before a kit uses them; the research lead owns that policy. No change to agreement semantics silently suppresses those stops. |

## Verification and process

Delegated desk implementation used a disjoint worktree and exhaustive four-file WRITE_SCOPE. The lead read the full final diff and owns commits and final verification. Worker verified 71 desk tests (32.6 s) and diff whitespace; the only scope deviation was its log placed in the parent scratch directory (no repository scope violation). Regression tests cover missing lock parents, matching versus differing refusal details, import identity changes, and signed history assertions. No signal/reap test was added or unstubbed.

The paired controller's local cadence suite, synthetic run, final-head CI and pending gates are reported in the controller run report and PR findings tables. Gate 4 was REFUSE / ADMIT WITH FIXES at the old heads; these fixes do not constitute fresh seat admission. No new Claude seat was launched; coordinator quota approval remains required. Research questions remain open; this pair is not merge-ready.
