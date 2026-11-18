# PR #812 delta-audit repair

Astra confirmed the five repairs on `57ed7334e` and raised two new high
findings. `ab32a6c915a9a78f92554a89c5d0eb93333b7a39` is the code pin.
The six regenerated qualification drafts are a patch for the lead against
`audit/2026-11-10-fable` at `163fa6194d30b1bc3139f2f7d2e7ac773493c700`.

| Finding | Repair | Regression |
| --- | --- | --- |
| A wall rollback before the arm sample allowed an early child start | Run forwards the greatest of the start window, issue, watcher observation, authenticated queue commit, predecessor close, declared prior close, latest proven close and RL-175 C.4 cooldown. The draft refuses a sample below that bound and the child enforces it on its own wall sample and projected interval. | Exact Bash and Zsh Run blocks refuse a two-second rollback after the gates. The child rejects epoch 1795111199 against lower bound 1795111200 and allows equality. |
| Sleep hid elapsed time from the expiry check | The pinned `t0-anchor` verb, launcher fallback and child use the same sleep-inclusive clock. On Darwin `CLOCK_MONOTONIC_RAW` maps to `mach_continuous_time`. Darwin `CLOCK_MONOTONIC` uses realtime minus boot time. Linux uses `CLOCK_BOOTTIME`. | `test_handoff_clock_counts_suspend_at_both_ends` uses the real clock selection and simulates 60 seconds asleep, five awake and a ten-second backward wall correction. Watcher expiry still refuses. |
| RL-179 F-2 close proof | The qualifying predecessor and latest close must be recorded, and the latest proof binds restore, stopped feeds and process absence to the actual receipt. The first-to-second planning reserve drops the retired close wait. | Both shells admit immediate proven campaign and noncampaign closes, and refuse stale proof, a missing record, an incomplete restore or shutdown, and live foreign processes. |

The accepted conservative refusal when the projected sampling interval
straddles a bound remains. The child records `started.continuous_ns` for
the handoff clock and keeps `started.monotonic_ns` in the same clock
domain as the other span stamps. A same-host comparison bracketed Python's
Darwin reads with the corresponding native `clock_gettime_nsec_np` reads.
Sleep behavior follows Apple's clock documentation and libc mapping.
[Apple clock documentation](https://developer.apple.com/documentation/driverkit/mach_continuous_time) · [Apple libc source](https://github.com/apple-oss-distributions/Libc/blob/main/gen/clock_gettime.c)

| Kit | SHA-256 | Frozen paths |
| --- | --- | --- |
| cl-qual-01 | `fe5b692a39b8646b81fc4e7b738a1802ba00ab51bd09158d1525e2bec0ccbac4` | 38/38 |
| cl-qual-02 | `a1b964faec281cf351e6387759a84178097ad6f8c94011a0856647a3197e2742` | 38/38 |
| cl-qual-03 | `f977eff89859d3111b9dee7afee7e9ac0c5232463dd7f980b2dfa7015b4ba4b1` | 38/38 |

All 114 frozen blob hashes verified. The runner hash is the only frozen
path hash changed from the previous pin. GitHub's test-merge tree matches
the final head's tree `a4039eecdc49762a5c6f3934d6d6d950cfbe67f9`.

The 107 focused Python 3.13 tests passed. The draft wrapper passed 1,540
gates and 246 close/copy assertions in Bash and Zsh, 91 pinned checks,
74 shell syntax checks, 68 Python compile checks, 21 historical standing
checks, nine Round 10 tests and 13 generator checks. Local execution used
synthetic fixtures and left the tests that send process signals to hosted CI.
Qualification remains `HOLD_FOR_FIT_FREEZE`. This change applies RL-179 F-2
to the six qualification items. The existing issue, queue and watcher
authority remains in those items for the requested handoff cases.
[PR #812](https://github.com/mpmdw/JouleWise/pull/812) · [Exact-head CI](https://github.com/mpmdw/JouleWise/actions/runs/44260250147)
