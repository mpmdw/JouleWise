# Cold review: stage-parallel ALIGN v4 desk and laptop replay (eng-desk)

- **Reviewer:** Opus 5.5, cross-family cold review (Sol 6.1 built it).
- **Date:** 2026-11-08.
- **Reviewed:** `origin/perf/2026-11-08-eng-desk` @ `2fd82914c` (code `f1ff965fc`). Diff base: merge base `50c99e4f8` with `origin/align/2026-11-08-v4-r11`.
- **Scope:** engineering only. Nothing measured; no estimand, threshold, refusal or registration change proposed.
- **Sources:** `docs/perf/2026-11-08-latency-synthesis.md` §4 rank 1; RUN_STATE 213-217; R12 B2 `NEXT_ARM_TRIAGE` (`joulewise/align/apple/v4_cadence.py` on `align/2026-11-08-v4-r11` @ `05b6d04cb`).

## Verdict: ADMIT_WITH_FIXES

**The parallel desk is equivalent to the serial one.** The pilot member, analysis and v4 thermal stages, run through `DeskExecution`, gave the same bytes as the whole base tree in every case I tried:

- workers 1, 2, 3, 4 and 8;
- with and without harvest;
- the pending-U3 refusal;
- the isolated-U3 thermal and residual rendering, with live LOO, thresholds and spreads;
- an uncaught member error that refuses.

The comparison covered the full set of files written, every file's bytes, stdout, and the refusal's type and message. Worker death is a refusal and never a pass. The parallel path can be used on the MBP-side `desk --workers N` and on the thermal manifest desk now.

**The laptop replay (`desk_record.py`, `align_v4_record_desk.py`) needs fixes before it can be the `full_desk_gate`:**

- **H1** (witnessed, failing) lets the laptop mark members chain-eligible when the MBP desk refuses them.
- **H2:** the branch does not take the expensive part, the harvest, off the MBP. So it does not deliver the B2 saving of about 100 MBP minutes per window.

## Findings

### HIGH

**H1. The laptop replay trusts operator-written target-precheck paths. An empty list turns the MBP's ineligible member into a chain-eligible one.**

Where:
- `joulewise/align/apple/desk_record.py:140-144` and `:157`;
- compare `scripts/align_pilot_session.py:331-336`;
- and `joulewise/align/apple/diagnostics.py:118-131`.

How it happens:
- On the MBP, a session with `inputs.pack_root` (every `bytes_h_session.prepare` session; `scripts/bytes_h_session.py:355`) gets each member's target paths from `harvest.build_roster(pack_root, ...)`.
- The replay instead takes them word for word from the layout or descriptor. It checks only that every `run_id` has *some* list.
- `evidence_precheck(bundle, [])` selects no windows, so it returns `eligible = bool(rows) and all([]) = True` whenever any precheck row exists.
- So a descriptor entry `[]` for a member whose pack target is `['gross_request']` (ineligible) gives `chain_eligible: True` and can pass the `chain_eligibility` instrument check. The MBP desk refuses that member.
- The doc even asks the operator to write "explicit empty lists where appropriate".

Witness: `tests/align/test_desk_equivalence_review.py::ReplayTargetBindingWitness`, **failing first on `2fd82914c`**:

```
{'m000': True, 'm001': False, 'm002': True, ...}  (laptop)
!= {'m000': False, 'm001': False, 'm002': False, ...}  (MBP, pack-derived)
```

Fix:
- Export the pack, or the harvest's own per-member target record. Derive the targets in replay through the same `build_roster` call.
- Alternatively, `describe` computes them with `build_roster` and replay recomputes and refuses on any mismatch.
- Never accept hand-written targets for a gating check.
- The witness accepts either fix: equal eligibility, or a `ValueError` refusal.

**H2. The harvest is not moved off the MBP. A laptop pass does not show that the harvest succeeded. (Scope and plan; not a defect in what the code documents.)**

Where:
- `desk_record.py:155-166`;
- `scripts/align_v4_record_desk.py:46`;
- compare `scripts/align_pilot_session.py:509` and the `harvest_status` logic at `:430-431`.

What the replay does:
- It is the `--no-harvest` desk. It reads the archive the MBP harvest already wrote (`archive/derived/exclusions.json`, `flags.jsonl`, `withheld/battery-assist.json`).
- So `harvest_b6_session.py` must still run on the MBP before every export.

Why that matters:
- The 98-103 min "desk" is mostly harvest. LATENCY-AUDIT-sol1 M23 measured B6 harvest at 88 min and BYTES harvest at 89-109 min, inside desk totals of 114/117 min ("totals overlap").
- So the branch moves at most the non-harvest remainder, which is probably 10-15 min, off the MBP. The 100 min does not move.

The pass does not depend on the harvest's outcome:
- The replay CLI exits 0 on `instrument_ok` alone.
- `REPLAY.json` says `"harvest": "previously recorded; not rerun"` without reading any harvest receipt.
- Suppose the MBP harvest wrote `exclusions.json` and then failed (`program_fault`). The MBP desk exits 2, but the laptop replay can exit 0.

Fix (lead decision):
- Either run the harvest on the laptop over the export (the harvest compresses `runs/`, so it needs a writable copy),
- or require an authenticated MBP harvest receipt (exit code, stdout/stderr, archive manifest) in the descriptor and fold `harvest_status` into the replay's status and exit code.

### MED

**M1. How it fits with R12 B2 `NEXT_ARM_TRIAGE`.**

No code conflicts:
- The eng-desk branch predates R12, and `git merge-tree` with `align/2026-11-08-v4-r11` @ `05b6d04cb` is clean.
- On the merged tree these all pass: `test_v4_cadence` 16/16 (including `test_full_desk_gate_is_required_after_w1_and_after_code_or_config_change`), `test_desk_parallel` 13/13, `test_v4_powermode_record` 9/9 and the new equivalence module 7/7. H1 still fails there, as expected.
- `full_desk_gate` still refuses `deferred` after W1 and after a code or config change.

Three gaps remain:
1. **Nothing ties a `pass` to an artifact.** The triage takes any non-empty `basis` string (`v4_cadence.py`, `next_arm_triage`). A `full_desk_gate: pass` could cite a laptop replay with `harvest_status: not_run`, or one with H1. The packet should cite the record commit, the descriptor path, and the `PILOT.json`/`REPLAY.json` SHA-256s, and require a recorded harvest success (H2).
2. **Desk outputs still gate every arm.** `thermal_escalation` (U1-U3) and `member_eligibility` (final exclusions, X5, U3 pairs) can never be `deferred`, and `not_applicable` is allowed only before W1. Their inputs are desk outputs: U1-U3 from `powermode_desk_check` → `window_report`, and exclusions from the harvest. So even with `full_desk_gate: deferred`, the harvest and thermal parts of the desk are on the arm path every window. The lead should say whether those two checks can come from the lighter standalone `align_v4_thermal_desk.py --manifest --workers N` (also parallel and byte-equal here) plus the harvest exclusions, rather than the full desk.
3. **Landing this branch counts as a code change.** It sets `code_or_config_changed = True`, so the full desk must pass before the next arm after it lands.

**M2. The descriptor's provenance is not tied to the MBP's finalized record.**

Where: `desk_record.py:29-53` and `:72-109`.
- `describe` hashes whatever local tree it is given, and replay authenticates against that self-written descriptor.
- If `describe` runs on the laptop after transfer, authentication says nothing about the transfer or about the MBP bytes.
- `committed_descriptor` accepts any local commit. It does not check that the commit is on the pushed records branch.
- Replay never checks `session_id` or the plan id against `custody/night/result.json`.

Fix: write the descriptor on the MBP at finalize, or derive it from the finalize hash manifest. Require the commit to be reachable from the pushed record ref, and cross-check the session against the terminal result.

**M3. Nothing enforces that the export is complete, and missing parts degrade silently.**

- A missing KM003C custody directory turns the DC-in section into `unavailable` (`scripts/align_v4_session.py:180-189` swallows the error). Ed's rule says every analysis analyzes DC-in.
- Missing `custody/collection/run_clock.jsonl` or `hazards/monitor/thermal.jsonl` makes `member_thermal_readings` return `{}` silently (`diagnostics.py:139-146`), so `os_thermal` is null.
- On the MBP these files exist. An export that leaves them out still replays to a status.

Fix: the descriptor schema lists the required layout files, and replay refuses if any is absent.

**M4. Nothing stops a multi-worker desk on the MBP while the next window measures.**

- Under B1 back-to-back, the previous window's `night/result.json` exists while the next window runs. That is the only terminal check (`align_pilot_session.py:314-315`).
- `--workers 8` on the MBP during capture would be severe contention. The help text ("only after the window is terminal") is not enforced.

Fix: refuse `workers > 1`, or any desk, when the host's run_night/arm lock shows a live window.

### LOW

- **L1.** `--output` is created before member reads (`align_pilot_session.py:316-320`), so a refusal or crash leaves an empty report directory. My worker-death test confirms it.
- **L2.** The profile receipt is written in `DeskExecution.__exit__` (`desk_execution.py:42-53`). In replay that is after `staging.rename(output)`. If the profile write fails (for example a missing parent directory), a completed replay exits 1 with its output already published. The failure can also mask the original exception.
- **L3.** The exists check and the rename are separate steps (`desk_record.py:121` and `:164`). POSIX `rename` replaces an empty directory created in between. Use an exclusive rename (`renamex_np(RENAME_EXCL)`), or mkdir and then move the contents.
- **L4.** Spawn re-runs the caller's `__main__` *file* in every worker. An unguarded driver script that calls `desk(workers>1)` re-executes itself. My first scratch benchmark did this: the workers died, the result was `BrokenProcessPool`, and it refused safely. The production entry points are guarded. Document this for magistrate wrappers.
- **L5.** `tests/align/desk_benchmark.py:27-36,58-59` splices only two base modules. `thermal_desk` and `align_v4_thermal_desk` stay at the current version. The whole-tree witness below closes this.
- **L6.** The equality fixture in `tests/align/test_desk_parallel.py:36-55` is weak. Its members are byte copies of one bundle with identical constant power. It cannot see a member/summary swap or a change in summation order, and residual analysis never runs (`mock` source). The witness below fixes that.
- **L7.** There is no per-task timeout, so a hung worker hangs the desk, as the serial desk would. Worker-tree RSS is unmeasured. Measure it on a real record before going above 2 workers on the 24 GB Air.
- **L8.** A worker exception that cannot be unpickled would show up as `BrokenProcessPool` instead of the original refusal text. It is still a refusal. `BundleReadError` round-trips correctly; my KeyError fault case checked this.

## Checks performed

### 1. Exact equivalence

I added the stronger module `tests/align/test_desk_equivalence_review.py`. Its reference is the whole base tree: `git archive 50c99e4f8 scripts joulewise configs`, run in its own interpreter.

The fixture has 10 different fake-native bundles:
- seeds 1-3, benign and sabotage, two pairs, and one sampled replay;
- member-specific, noisy GPU-labelled power, so residual fit, LOO, grouped thresholds, tamper curves and spreads are all live;
- plus a missing member, a corrupt member, a harvest exclusion, flags and battery assist.

| Case | Workers | Result |
|---|---|---|
| Harvest (inert receipt), pending-U3 refusal | 1, 2, 4, 8 | identical file set, file bytes, stdout and error |
| Harvest, isolated U3 (thermal + residual rendering) | 1, 2, 4, 8 | identical |
| `--no-harvest` inspection path (directory name normalized) | 1, 3 | identical |
| Uncaught member error during thermal read (`BundleReadError` refusal) | 1, 2, 8 | identical exception and message; no PILOT/desk written by either |
| Worker death (`os._exit`) in `DeskExecution.map` and mid-desk | 2 | `BrokenProcessPool`; nothing published; CLI returns 1, never 0 |
| Production `scripts/align_v4_session.py desk` as `__main__` (spawn pickles `__main__._thermal_desk_member`) | 1 vs 2 | identical bytes; profile shows `v4.thermal_members` ran |

Mutation check: making `_ordered` yield LIFO when workers > 1 makes the harvest case fail at workers 2, 4 and 8. The witness does detect order changes.

Floating-point note: every summation stays in single-process code over pickled inputs. Pickle round-trips IEEE-754 doubles exactly, including NaN, infinity and -0.0. The reductions run in fixed stage order, and no reduction is ever done in completion order.

### 2. Concurrency hazards

- **Shared mutable state:** the analysis reductions get pickled copies of `members`. I found no reduction that mutates `members`, so `instrument_checks`, `sampling_checks` and `residual_analysis` behave as they do serially. The bytes confirm this.
- **Caches:** the `attribution._last_reconstruction` cache is per process and keyed by identity. It affects speed only.
- **Temp files:** workers write nothing; the file sets are equal. zstd reads use pipes. Fixed-name writes stay serial in the parent, and replay staging uses a unique `TemporaryDirectory`.
- **Iteration order:** the FIFO is bounded at `2*workers` and consumed in roster order.
- **Errors:** the first roster error wins, even when a later member fails first.
- **Crashes:** a worker crash raises `BrokenProcessPool`, a `RuntimeError`, which both CLIs map to exit 1.

### 3. Committed-record-only reads

The replay reads only the descriptor (`git show <sha>:<path>`, `GIT_NO_LAZY_FETCH=1`) and the local export:
- every host locator is replaced;
- the `restricted` path component, symlinks and paths that escape the export are refused;
- there is no measurement launch, host admission or harvest.

The witness passes `/unavailable/...` locators and replay succeeds, so no host path is followed. The bundle and custody readers (`read_bundle_record`, `km003c.session_report`) resolve only relative to the bundle or the custody root.

Two caveats:
- The "committed record" is a self-written descriptor plus a separately transported export of 18.7-26.5 GB per copy. See M2 and M3.
- The replay still needs the MBP harvest's archive (H2).

### 4. R12 B2 interaction

See M1.

### 5. Speed

Air M4 (4P+6E), Python 3.13.18. The host was heavily loaded (load average 28-36), so these are noisy. 18 members, 48,000 samples each, 2 repeats. Every run was byte-equal to the original serial bytes.

| Path | Repeat 1 (s) | Repeat 2 (s) | Mean (s) | vs original |
|---|---:|---:|---:|---:|
| Original serial (base) | 18.57 | 18.55 | 18.56 | 1.00× |
| Current, 1 worker | 18.75 | 16.68 | 17.71 | 1.05× |
| Current, 2 workers | 9.48 | 11.23 | 10.36 | 1.79× |
| Current, 4 workers | 6.68 | 7.23 | 6.95 | 2.67× |
| Current, 8 workers | 5.99 | 6.57 | 6.28 | 2.96× |

By stage:
- `pilot.members`: 12.6-14.3 s serial → 4.7-5.2 s at 8 workers.
- `v4.thermal_members`: 3.6-4.1 s → 0.85 s.
- `pilot.analysis`: 0.03 s. Residual analysis is inactive in this fixture; it is live in the witness fixture, but that fixture was not timed.

These numbers agree with Sol's 1.85× at 2 workers.

**Estimate for a real window.** The ALIGN split between harvest and the rest of the desk has not been measured. The `--profile` receipt times `pilot.harvest` separately, so the first real profile will settle it.

- **If the harvest dominates, as the B6/BYTES evidence (88-109 min) suggests:** only about 10-15 min of member and thermal extraction speeds up. At 4 workers that becomes about 4-6 min.
  - An MBP desk falls from 98-103 min to about 90-95 min, a saving of about 7-10%.
  - The laptop replay removes the same 10-15 min from the MBP. The harvest, finalize and export stay on the MBP.
  - On the laptop, the replay takes transfer time (minutes to tens of minutes for 18.7-26.5 GB), plus two SHA-256 passes (about 1-2 min), plus about 4-6 min of desk.
- **If the harvest is small:** the ceiling is about 2.7-3× on the whole desk, roughly 35-40 min.
- **Either way:** this branch alone does not meet the 30-45 min MBP turnaround (RUN_STATE 213). Rank 1's real lever is moving or parallelizing the harvest.

## Commands (one module per process)

`python3.13 -B -m unittest <module>` on the review head:

| Module | Result |
|---|---|
| `tests.align.test_desk_parallel` | 13 OK |
| `tests.align.test_thermal_desk` | 25 OK |
| `tests.align.test_pilot3.DeskTests` | 3 OK |
| `tests.align.test_pilot4.AnalysisTests` | 8 OK |
| `tests.align.test_v4_powermode_record` | 9 OK |
| `tests.align.test_desk_equivalence_review` | 7 OK, 1 FAIL: the H1 witness, failing first by design |

On a scratch merge with `align/2026-11-08-v4-r11` @ `05b6d04cb` (not pushed): `test_v4_cadence` 16 OK, `test_desk_parallel` 13 OK, `test_v4_powermode_record` 9 OK, equivalence 7 OK plus the H1 failure.

The timing script is a guarded copy of `tests/align/desk_benchmark.py` that loops over 1/2/4/8 workers. It is not committed.

## Required before the replay is used as `full_desk_gate`

H1 (bind the targets to the pack), H2 (a harvest receipt or a relocated harvest), M1.1 (tie the triage basis to an artifact) and M2 (tie the descriptor to the MBP finalize manifest). M3 and M4 should land with them. The LOWs are optional.
