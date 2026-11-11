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

## Round 2

RL-54's two W-7 sections were read verbatim at audit ref `f0d9b0676`.
Audit section 8 Q10 and the lane plan at `a119b5556` remain the scope.
This round started at `c81ec9564` on the existing
`test/2026-11-11-w1-finality-tests` branch, as the seat brief requires.
Here k=C1, k+1=C2 and k+2=C3. ACCEPTED means the real packet build,
rebuild comparison, latest-record check, cadence triage and series binding
all accept. Hardware predicates retain the synthetic fixture inputs.

| Question | Answer | Execution evidence |
|---|---|---|
| 1. Desk final before C2's first commit? | ACCEPTED for the C3 arm. | `test_order1_*`: C2 has one record commit and carries C1's `previous_final` at that commit; C1's late exclusion lowers its replayed count. |
| 2. Desk final after C2's first commit; tail re-issued? | ACCEPTED after a new record commit, ledger commit and packet rebuild. | `test_order2_*`: decoded-record diff changes only `previous_final`; removing it restores the original record bytes exactly, including the newline. |
| 3. C2 record held until C1's desk is final? | ACCEPTED for the C3 arm. No earlier C2-record dependency found for C2's own arm or eligibility receipt. | `test_order3_*`: C2's own final receipt runs with no C2 record; C2 is then committed exactly once with C1's final sources. |
| 4. Analysis consumes a stale saved pool list? | No such reader found on this ref. Executed eligibility/count readers use roster membership plus exclusions. | `test_final_receipt_and_desk_counts_recompute_despite_stale_stored_pool`: saved lists still include the late-excluded member; final eligibility and both count paths drop it. |

Order 2 compares the decoded old committed record with the new record before
committing. Their changed-key set is exactly `{'previous_final'}`. It also
compares both actual committed blobs with those checked bytes. The synthetic
re-issue commit says `Re-issue C2: compared decoded records; only previous_final
changed`. The original blob remains readable and is an ancestor. This is a
test of the ruled procedure, not a new production restriction on record edits.
The old packet fails `_record_bound`. Before the ledger is re-committed, the
builder refuses exactly `series previous record binding mismatch`
(`scripts/align_v4_next_arm_packet.py:633-634`). The repaired packet passes.

**Every latest-record reader in the packet/arm path.** The search was
`rg -n -i 'latest.*record|record.*latest|log.*--format=%H|last_passed_record|previous_record' scripts/align_v4_*.py joulewise/align -g '*.py'`.
These are the readers and consumers reached between a window's end and the
next arm; they do not discover an uncommitted future record:

- `align_v4_next_arm_packet.build_packet`, `:628-634`, reads the explicitly
  named previous record and its ledger binding. `committed`, `:660-675`,
  proves that same record is finalized, byte-bound and reachable from the
  named local remote-tracking ref. For C2's arm this is C1. For C3's packet
  it must be C2: holding C2 starves that build until C2 is committed.
- `last_desk_state`, `:743-764`, follows `last_passed_record` and any
  `final_record` named by the ledger. The C2-arm fixture names W1 as the
  last passed desk while C1 is provisional. Holding C2 does not starve it.
- The builder's chain walk, `:924-966`, follows only predecessor links from
  that named tail and pairs immediate successors. It needs C2 for C3's
  history, including C1's finality. It does not need C2 for C2's arm.
- `align_v4_session._record_bound`, `:675-689`, reads the packet's blob,
  the latest commit **at that record path**, and the canonical ledger at
  HEAD. `arm_checks`, `:780-791`, calls it after the rebuild. Before C2 is
  committed, C1's record and HEAD ledger still bind the C2-arm packet.
  After C2 and its ledger are committed, that old packet is stale.
- `v4_cadence.next_arm_triage`, `:180-184,235-238`, consumes the record
  identity/binding result. `align_v4_series.bind_packet`, `:694-724`,
  consumes the rebuilt history and enforces k-final-before-k+2. Neither
  independently reads a latest record. Both pass the held order after
  release; neither needs C2 for C2's own arm.

Order 3 replays the C2-arm packet after C2's synthetic result and own final
receipt exist, while the C2 record path does not exist and has no Git history.
No packet evidence names that path. An attempted C3 build naming the absent
C2 blob refuses exactly `source is not a committed regular blob:
w-C2/record.json`, at the regular-blob check `:119-121`. Only then does
C1's final desk finish; C2 receives `previous_final` and is committed once.

The own-window post-processing readers use session files, not the committed
window-record chain. `align_v4_harvest_off.cmd_triage`, `:199-214`, and
`cmd_final`, `:240-257`, read the session, collection roster, desk/thermal
evidence and capture presence. Order 3 executes `cmd_final` before C2's
record exists. By source inspection, `cmd_finalize_manifest`, `:435-459`,
and `cmd_pack`, `:153-165`, require the terminal `night/result.json` and
finalized manifest; `cmd_unpack`, `:173-185`, requires the named manifest
and mirror identity. Their phrase "record binding" refers to those
manifest bytes, not discovery of the latest committed window record.
No offload, harvest, installer or hardware flow was executed in this round.

**Pool-reader census.** This command returns exactly four matches:

```
rg -n -i 'pool_members|pool_list|pool_membership|pool_ids|calibration_pool' joulewise/align scripts/align_v4_*
scripts/align_v4_session.py:449              # diagnostic writer
scripts/align_v4_next_arm_packet.py:484      # template writer
scripts/align_v4_next_arm_packet.py:844      # current-ledger roster check
scripts/align_v4_next_arm_packet.py:965      # final-exclusion check
```

The broader `rg -n -i '\bpool\b|pool_|_pool' joulewise/align scripts/align_v4_*`
returns 84 lines. Outside the packet builder, the relevant counting readers
are `light_triage.is_calibrator/calibration_row`, `:103-120`, which read
planned `pool_role` plus `member_eligibility`, and `align_v4_series.desk_row`,
`:645-657`, which reads the frozen manifest's `pool` labels plus current
captured/excluded rows. The new test executes both, and executes
`align_v4_harvest_off.cmd_final` without replacing any of these readers.
It writes a stale ledger list and stale PILOT diagnostic list, then applies
a harvest exclusion. The member remains in both lists but leaves final
eligibility with reason `harvest.excluded`; exactly its pair loses one count.
Restoring only its exclusion bit restores the separate desk count.
`align_v4_session.py:449` writes planned lists before exclusions; it is
not an eligibility reader. Its desk count calls `desk_row` at `:550-563`.

`pilot_analysis.py:189-205,270` accepts explicit member rows and uses their
exclusion flags for its registered scope. Its `:88-93` "pool" strings are
printed pilot-reference labels. `v4_estimands.py` accepts explicit score,
carrier, member or diagnostic rows; it does not select a series pool or
replay record finality. `v4_u3.py:137-162` accepts explicitly eligible
prespecified pilot/R1 pairs; its roster is comparison scope, not a saved
calibration-member list. None contains `pool_members` or a stored-pool-list
reader. The other broad matches are allocation writers, worker pools or
unrelated within-module statistics. This is not evidence that every
row-based analysis function automatically filters late exclusions.

The same pool search over the release/analysis entry points present here
(`scripts/release_check.py`, `b6_release_subset.py`,
`finalize_analysis_manifest.py`, `joulewise/analysis_engine/`, the three
`analysis_manifest` modules, `b6/analysis_lane.py`, `bytes_analysis.py`)
finds no series-pool-list reader. The only broad "pool" matches there are
`analysis_engine/registry.py:327`'s speculation guard and
`bytes_analysis.py:1433`'s no-pooling comment. These files were searched as
code only; no analysis or release command ran. `compare_v4_recompute.py`
and the separate v4 release-tool line are not on this ref. No claim is made
about consumers on other refs.

Both arm-stack generations were read again using `git show`, without
checkout or network. `origin/main` remains `84ad2c5be`; it has neither
`align_v4_session.py` nor `align_v4_series.py` nor the packet builder.
W1 remains `b4a6c217f`. Its delivery receipt, nonzero-exit reason and named
watchdog holds differ from main. All three orders mix main-era sent evidence
and W1 digest-bound delivery evidence through the existing synthetic fixture.
Production files and the two hygiene modules are byte-identical to W1.

Round 2 changes only this report and the existing test module. There is no
new module, timing-map insertion or CANONICAL row. Coordination state and
the runbook remain lead-owned. No delegation, network, model weights,
real custody or measurement data were used. The existing custody fence
remains active. Empty synthetic bundle directories test capture-presence
logic; they are not live hardware or harvest evidence.

The order-1 and order-2 tests extend and rename the round-1 late-exclusion
and tail-reissue tests. Order 3 and the outside-builder count test are new
cases in the same module. No classifier or success fallback was added.

All commands below used `TMPDIR=/private/tmp`, `GIT_CONFIG_GLOBAL=/dev/null`,
`GIT_CONFIG_NOSYSTEM=1`, `JW_B5_SYNTHETIC_ONLY=1`,
`JOULEWISE_BACKUP_ROOTS=''` and `PYTHONNOUSERSITE=1`. Unittest modules ran
serially, under `/usr/bin/time -p`.

- Baseline `python3.13 -B -m unittest -v tests.align.test_v4_finality_paths`:
  6 tests passed in 183.635 s, before the additions.
- Final `python3.13 -B -m unittest -v tests.align.test_v4_finality_paths`:
  8 tests passed in 142.298 s. Both runs reported zero forbidden custody
  accesses and zero home custody probes. This is a local observation, not
  a throughput comparison under the machine's unrelated job.
- `python3.13 -B -m unittest tests.test_fixture_orphan_census`:
  16 tests in 0.177 s; 1 failure, 2 subtest errors, 2 skips. The unchanged
  `test_launch_record_is_informational` again supplies a non-iterable
  `Mock.glob_plans()` to W1's `_launch_fence`; see the round-1 traceback
  above. No out-of-scope repair was made. The two live census tests skip
  because this sandbox denies `ps`.
- `python3.13 -B -m unittest tests.test_gen_state`:
  44 tests passed in 5.951 s. Neither hygiene module approached 3 minutes.
- `python3.13 -m compileall -q tests/align/test_v4_finality_paths.py` and
  `python3.13 -m compileall -q joulewise tests scripts`: both passed.
  `ast.parse` of the touched module with `feature_version=(3, 11)` passed;
  no native Python 3.11 run was available.
- `python3.13 -B scripts/fixture_orphan_census.py --fail-on-orphans`:
  exit 2, `PermissionError: [Errno 1] Operation not permitted: 'ps'`.
  No census rows or count were obtainable. This is not a clean live census.
- `git diff --check`: passed. The W1 diff over `joulewise/` and `scripts/`
  names only round 1's `scripts/test_timings.json` insertion. The watchdog,
  finality readers and hygiene modules remain unchanged.

Reported unittest time totals 332.061 s, under the 20-minute limit. The
full suite was not run. No native MLX check is needed for these stdlib-only
tests. The lead must repair or disposition the existing census mock fixture
and run the live census checks where `ps` is available. The required hygiene
gate remains red; the three ACCEPTED orders do not change that finding.

Open questions: no new contract ruling is requested. Reader absence is
limited to this ref. A separate analysis implementation or release-tool
ref still needs its own consumer audit. Re-issue after a descendant record,
real offload transport, real desks and hardware remain untested here.
Next: the lead reviews and mutation-tests this two-file change, updates the
runbook with the `previous_final`-only comparison and ledger/rebuild steps,
then returns the three-order result to the research lead before registration.
Round 2 implementation commit: `ea6ba14f9e429b95fcbc9d421c500bb8e99922a1`
(`test(align): cover RL-54 finality orders and pool readers`). This report
is committed separately after the verification results were recorded.
Local commits only; no push or registration was performed.
