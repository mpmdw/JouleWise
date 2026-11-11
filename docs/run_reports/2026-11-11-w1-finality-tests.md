# W1 finality tests, 2026-11-11

This is synthetic execution evidence for RL-53 W-7, audit section 8 Q10 and its
finality invariant. It changes no bound code or claim contract. The starting
branch is `test/2026-11-11-w1-finality-tests`, based on W1
`b4a6c217f0285a20aff33a8407160dd77af2a8a6`.

A holds. `test_late_exclusion_replays_final_counts_with_successor_pool` first
admits C2 with C1 provisional and C1's member in the committed pool. The final
desk then excludes that member through C2's `previous_final`. Rebuilding for C3
admits, reports C1 final, and reduces exactly its pair's count by one. C2's pool
contains C2 members. `scripts/align_v4_next_arm_packet.py:237-242,292-298` selects
the successor's final pilot, and `:957-971` recomputes the rows. The exclusion
check at `:963-966` compares with the current ledger pool.

`test_stale_pool_refuses_cohort_first_and_new_series_commit_repairs_it` proves
the negative and repair. The first failing requirement is
`pool members outside previous D roster` at
`scripts/align_v4_next_arm_packet.py:847`, in `cohort_pool_rules`. The builder
continues and also reports `R17: a finally excluded member of C1 is in the pool`
at `:965-966` as `calibration_error`. A wrapping spy observes the order without
changing either decision. Correcting only `pool_members` in a new series commit
clears both failures. The old packet becomes stale; the rebuilt packet passes
the real latest-record and series checks.

B holds at the arm's series-binding gate. The packet builder alone does not
enforce the ceiling. `test_final_counts_above_desk_ceiling_refuse_at_series_binding`
first admits a provisional count of zero for one pair. A final desk restoring
that member produces one eligible member against a ceiling of zero. The packet
build and rebuild succeed, but `bind_packet(..., authenticated_by_rebuild=True)`
refuses with `final adjudication may lower the desk counts, never raise them`.
The deciding comparison is `scripts/align_v4_series.py:611-614`, called by
`:702`. The packet carries the ceiling at
`scripts/align_v4_next_arm_packet.py:1014-1018`. A covers lowering; D covers
equality.

C does not hold as worded about the R17 diagnostic. The immediate-successor
restriction holds, and C1 remains non-final.
`test_ACTUAL_non_successor_final_fails_binding_before_R17` commits C2 without
`previous_final` and C3 with a `previous_final` naming C1. The C4-arm packet
refuses with `previous_final must name this record and carry exactly the full
desk sources`. `scripts/align_v4_next_arm_packet.py:942-943` pairs adjacent
records; `:305-308` compares C3's named digest with C2's digest and refuses
before the R17 scan. The fail-closed history sentinel is `[{}]`, from
`:1043-1050`. `test_missing_successor_final_refuses_R17_even_after_another_record`
is the control without C3's misplaced final sources. It refuses with
`R17: final eligibility of C1 must be recorded`, through `:947-953,962` and
`:395-397`. Merely committing another record never finalizes C1.

D holds. No deadlock was found in the tested tail-record repair.
`test_reissued_tail_record_and_recommitted_ledger_accept_finality_repair`
starts with the C3-arm R17 refusal, re-issues C2 at the same path while C2 is
still the chain tail, and changes its record content only by adding
`previous_final` naming C1. The original committed bytes remain readable.
Before the ledger is updated, the builder refuses with
`series previous record binding mismatch` at
`scripts/align_v4_next_arm_packet.py:633-634`. Recommitting the canonical ledger
with the new C2 link in `previous_record` and `last_passed_record` repairs that.
The rebuilt C3 packet reports C1 and C2 final and passes series binding.

The D test calls `rebuild_and_compare` at
`scripts/align_v4_next_arm_packet.py:512-516` and
`committed_artifact_set_digest` at `:519-521` without replacing either. Digests
at the original code commit, original C2 commit and re-issued C2 commit equal
the current artifact digest. `last_desk_state` validates the passing record
and code digest at `:743-764`. The real `scripts/align_v4_session.py:675-689`
accepts the new latest record plus HEAD ledger and rejects the stale packet.
The wording "a re-committed record refuses" in its docstring at `:659-660`
describes an old packet becoming stale; it does not forbid a rebuilt packet
that names the new commit. Series binding also runs the count and finality
checks at `scripts/align_v4_series.py:702-724`.

The only files changed are `tests/align/test_v4_finality_paths.py`, one inserted
timing-map line in `scripts/test_timings.json`, and this report. The seat's
explicit three-file limit overrides the common CANONICAL-row instruction.
Coordination state and the runbook are lead-owned and unchanged. No fixture
data files are added. No agent delegation or external review was performed.

Both arm-stack generations were read with `git show`, without checkout or
fetch. The local `origin/main` is `84ad2c5beea5f823723e6f6f83ccf8caabf9e476`;
it has no `scripts/align_v4_next_arm_packet.py`. The W1 ref is the base above.
The relevant differences are the legacy courier marker versus W1's
`courier.delivery.json`, W1's `chain_exit_nonzero:<rc>`, and the named watchdog
holds and `STRANDED`. The synthetic chain mixes legacy sent evidence with
C2's digest-bound delivery receipt. These tests exercise successful terminal
records; they do not re-test driver fault classification or watchdog states.

All test repositories are created by `TemporaryDirectory` under `/private/tmp`.
The existing synthetic-custody fence runs around this module. The arm is
represented by its production rebuild, triage, record-pointer and series-binding
functions. No installer, host probe, measurement, harvest or analysis pipeline
runs. No model weights or MLX are needed. This is no live-hardware evidence.

Implementation commit: `b83bc97a4` (`test(align): prove W1 finality replay and
tail-record repair`). This report is committed separately. Nothing is pushed.

The unittest commands below used `TMPDIR=/private/tmp`,
`GIT_CONFIG_GLOBAL=/dev/null`, `GIT_CONFIG_NOSYSTEM=1`,
`JW_B5_SYNTHETIC_ONLY=1`, `JOULEWISE_BACKUP_ROOTS=''`, and `/usr/bin/time -p`.
The two hygiene commands also set `PYTHONNOUSERSITE=1`. Modules ran serially.

- `python3.13 -B -m unittest -v tests.align.test_v4_finality_paths`:
  first iteration ran 6 tests in 60.372 s, with 2 failures. The fixture needed
  to omit an already-excluded provisional member from its pool, and the C test
  needed to assert the actual `[{}]` error sentinel. Both were corrected in
  this new module. The final run passed all 6 tests in 79.245 s. The custody
  fence recorded zero forbidden accesses in both runs. The timing map uses
  the final local observation; it is a scheduling hint, not a hosted median.
- `python3.13 -B -m unittest -v tests.align.test_v4_next_arm_packet.R17ProvisionalTests tests.align.test_v4_next_arm_packet.R17ReviewFinalityTests`:
  12 tests passed in 116.288 s.
- `python3.13 -B -m unittest tests.test_fixture_orphan_census`:
  16 tests in 1.104 s; 1 failure, 2 subtest errors, 2 skips. The unchanged
  `test_launch_record_is_informational` supplies a `Mock` storage whose
  `glob_plans()` is not iterable. The W1 watchdog's `start_session` now reaches
  `_launch_fence` and `load_plans` (`scripts/magistrate_watchdog.py:3278,2175,766`).
  Both subtests raise `TypeError: 'Mock' object is not iterable`; the final
  assertion then sees zero spawns instead of two. The watchdog and this test
  are byte-identical to the W1 base, verified by `git diff --exit-code` against
  `origin/align/2026-11-08-v4-r11`. No repair was made outside this seat's scope.
- `python3.13 -B -m unittest tests.test_gen_state`:
  44 tests passed in 4.969 s.
- `python3.13 -m compileall -q tests/align/test_v4_finality_paths.py`:
  passed. This is the only Python file touched. Python 3.11 grammar parsing
  via `ast.parse(..., feature_version=(3, 11))` and timing JSON parsing also
  passed. No native Python 3.11 execution was performed.
- `git diff --check`: passed. The timing-map diff is exactly one inserted
  line in alphabetical position.

Reported unittest time, including the failed iteration, totals 261.978 s.
Neither hygiene module approached the three-minute limit. The full suite was
not run, as instructed. No native MLX test is required for this stdlib-only
change. The required hygiene gate is not all green because of the unchanged
orphan-census test above.

The next step is lead review and mutation testing, followed by the lead-owned
runbook correction before registration. State explicitly that only the
immediate successor carries a window's final sources, and that a tail successor
can be re-issued with its ledger re-committed before rebuilding the packet.
This report supplies evidence; the research lead retains registration authority.

Not covered: re-issuing C2 after C3 already exists, repairing bound desk defects,
analysis-side readers of older pool ledgers, real anchor identities, or live
custody. Those cases cannot be inferred from this synthetic tail repair. No
new scientific or naming ruling was made. Lead disposition of the orphan-census
failure is still needed; a lead-owned fixture repair is recommended. It does
not alter the A-D evidence, but this branch must not be described as passing
every required check.
