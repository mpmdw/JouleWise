# Qualification child t0 guard successor, 2026-11-17

Tier 2, [AGENT], user-selected. M0 found no active stop card. The lead's
2026-11-17 decision authorizes Builder C's recorded-t0 guard on a
qualification successor. RL-165 §8.1 and RL-167 Part B Q2 still govern the
two admission lines. RL-175 C.1 closes the independent-seed question and
C.4 governs future arms. No phase exit-checklist row closes.

## Exact pin and kits

The measurement pin is `0576ed76d3a74d20ce3c6b6b96711e360775a25f` on
`align/2026-11-17-qual-pin-t0guard`, one commit directly on
`e1b85a59c53bfbeaa3477df46bcbe9dd8fdfc427`. The two production files
apply Builder C's patch verbatim. The launcher forwards the authorized
local date and exclusive cutoff. The runner checks the receipt's actual
start stamp before directory creation or span work. The remaining changed
file adds a regression. The soak, references and leg-runtime code are
outside this diff. [Exact old-pin comparison](https://github.com/mpmdw/JouleWise/compare/e1b85a59c53bfbeaa3477df46bcbe9dd8fdfc427...0576ed76d3a74d20ce3c6b6b96711e360775a25f)

The audit generator applies that pin's `pin-kit` to the three exact #794
kit documents at `6010985a3312c77bb8e4bb4bf5c920c4d49b8512`. All 38
frozen path hashes per kit were verified against Git blobs at each pin.
Only the two entry-script hashes and `frozen.commit` changed. Queue
bytes change only at each span's kit hash. The six items, exact predecessor
bindings, queue hashes and derived plans were regenerated together.

| Kit | Successor SHA-256 | Line 1 | Line 2 |
|---|---|---|---|
| cl-qual-01 | `8d9ec7143d2e7b60d303a52ede374075bdaf807c4bbb214b418c269dba2dabbc` | Builder diff, plans and mocks pass. Named attestation open. | PASS. Empty red set at both pins. |
| cl-qual-02 | `612327b4fe5bbbcb0da28676a4d54e92c7d855a4c286157dbb3f4cc6073f923b` | Builder diff, plans and mocks pass. Named attestation open. | PASS. Empty red set at both pins. |
| cl-qual-03 | `85dfa025a84c7bdbcb79ecd0fa87bd52d1ffc7624e40fa94c5877646abd03bf9` | Builder diff, plans and mocks pass. Named attestation open. | PASS. Empty red set at both pins. |

**Line 1.** Rechecked the per-kit finding census, the class-B diff scope,
rosters, plans and both synthetic spans at the successor. Each first leg
captures, and the next five consume. #794 still has zero conversation
comments, inline comments and submitted reviews. RL-175 C.1 dispositions
M0-F7 for all three kits. The lead still needs LQ1 (the named Mythos Q2
confirmation per exact kit) and LQ2 (M1-F3 retry-reader/RL-128 probe
evidence and signoff). #800 supplies supporting retried-soak controller
evidence. See the [original finding census](../research-audits/2026-11-10-fable/evidence/align-v4-campaign/qual-lines-794/LINES.md)
and [RL-175](../research-audits/2026-11-10-fable/RESEARCH-LEAD-DECISIONS.md#c-qualification).

**Line 2.** Compare the successor's full hosted suite with the merged W1
baseline `c3f4bacd8013ca98c19cf8d41f830c701930cd41`. Confirm the logged
Actions checkout tree equals the pin's complete tree and verify the 38
frozen paths for each kit. The baseline's red set is empty at
[run 43670925240](https://github.com/mpmdw/JouleWise/actions/runs/43670925240).
[Draft PR #812](https://github.com/mpmdw/JouleWise/pull/812) targets
the same v1.1 ancestor as #794. The PR body was read back byte for byte.
The direct pin comparison above isolates this change.

| Side | Full CI run | Logged Actions checkout | Source tree SHA | Jobs | Canonical tests | Failing tests |
|---|---|---|---|---|---|---|
| Successor | [44186932495](https://github.com/mpmdw/JouleWise/actions/runs/44186932495) | `f74cbccecdeee5091438060ca4cab1a58c2ac01b` | `9806d42684541594598014535827e9d9360fea0f` | 21/21 pass | 15,264 | Empty |
| Merged W1 baseline | [43670925240](https://github.com/mpmdw/JouleWise/actions/runs/43670925240) | `f5c37c4feb0a350c7ebbbe32c7d7e6784aaebcf6` | `5bb381d904101408e79251350725d4fa42f4a51d` | 21/21 pass | 15,081 | Empty |

Each run executed all 12 ordinary shards and three exclusive test jobs.
The logged Actions checkout tree equals the full source tree for each
run. All 38 frozen paths match the tested tree for each successor kit.
The failing-test sets match test for test. The successor run is attempt
1. Its downloaded log SHA-256 is
`8838769ce9beb0cf82abab1b5d4705ea5bc714b014edcbc412789c4c911cc533`. The job snapshots and per-shard summaries are
in `/Volumes/JW-EXT/scratch/qual-pin-t0guard-1117/ci/`.

The [six drafts](https://github.com/mpmdw/JouleWise/commit/c0051b1cfb4275a12a75af0fc2941fb150ae6de1)
were pushed to `audit/2026-11-10-fable` after pull with rebase.

## RL-175 qualification draft gates

C.3 keys the date plan to all six spans. Each recorded t0 must match its
own entry. A span with a recorded t0 cannot arm again. Recovery keeps
s01's date and exact kit, moves missing s02 to the next unused legal date
with attempt 1, and moves later untouched blocks whole. The queue gate
checks the authenticated date, roster, kit, attempt and finite expiry.
The generator accepts a fresh finite expiry with an explicit offset when
the original cannot cover the dates.

C.4 uses each pinned plan's expected duration and the existing
boot + 12 h + 48 s daily prediction. The hold starts when expected close
would reach the batch and ends at batch start plus 27 minutes,
including arms whose soak would overlap the batch. Start and Run read
boot independently. A safe pre-batch arm passes the earlier of the
existing t0 bound and the next hold boundary to the child.

The default queue, kit, pinned-plan and standing-F0 bytes retain their
original hashes. The two new gates live in the audit drafts.

## Verification and handoff

The focused runner regression passed midnight crossing, a wrong date
before the numeric cutoff, expiry before work and the last authorized
fractional second. The old code reproduced a launcher CLI refusal in all
four cases because it lacks the arguments. The audit regression exercises
the actual successor extraction for all three kits. The local verification
uses in-process mocks and disposable fixtures. Hosted CI supplies the
canonical full-suite run because local whole-suite cases signal processes.

Both `bash tests/run_all_gates.sh` and `zsh tests/run_all_gates.sh`
passed. Each reported 1,154 gate checks, 246 close/copy regressions, 91
pinned checks (both mock spans per kit), 21 standing-F0 checks, nine
Round 10 tests, seven regeneration checks, 74 shell syntax checks and
62 Python compilations. The tracked F0 renewal and earlier raw logs
retain their bytes.

Both wrappers passed again after C.3 and C.4. Each run reported 1,336
gate checks, 246 close/copy regressions, 91 pinned checks, 21 standing-F0
checks, nine Round 10 tests and 13 regeneration checks. This exercised
all three half-run recoveries with authenticated synthetic queues, the
27-minute release boundary, a fresh boot read in Run, and the exact
tightened cutoff passed to the stubbed child launch. The final wrapper
logs are in `rl175-final/{bash,zsh}` under the scratch path below.

Qualification remains HOLD_FOR_FIT_FREEZE. The lead owns the exact line
records, freeze 2, queue and operational pointers, and issue. The PR
remains draft and unmerged. Scratch test output lives at
`/Volumes/JW-EXT/scratch/qual-pin-t0guard-1117`.
