# W1 pre-signing: Opus cold second read of `c64049b66` and `f41ee4e7c`

- **Date:** 2026-11-11 06:23 PST (`date`).
- **Reader:** Claude Opus 5.5, cold. I did not write either commit.
- **Branch:** `ops/2026-11-11-w1-presign`. I reviewed it at `82c14c9ea`. The remote then moved to `1bca029f7`
  (RL-77 row edits), and I also read that commit against RL-77.
- **Rulings read verbatim:** RL-29, RL-58, RL-61, RL-62, RL-63, RL-65, RL-67, RL-68, plus RL-69 and RL-77
  (the follow-ups that amend RL-68 and the rows), in `origin/audit/2026-11-10-fable:docs/research-audits/2026-11-10-fable/RESEARCH-LEAD-DECISIONS.md`.
- **Blinding:** code, configuration and registration text only. I opened no v4, Block 6 or BYTES outputs, no
  custody, no night-* or archive paths, and nothing from the ALIGN v4 protocol beyond what the rows quote.
  The one configuration file I read is `configs/b6/flag_catalog_b6.json`, and from it only the `effect`
  field of four codes.
- **Worktree:** a fresh `/Users/edr/code/CapstoneProject/jw-wt/rev-presign`, removed afterwards.

## Verdict: ADMIT

Both commits do what the rulings say, and nothing else. The binding is additive and strict, and it falls
under RL-29's standing ratification. The new test catches every mutation I tried. The receipt template only
gains two entries and is still PENDING. The trace differs from the W1 line only by the new module. The five
rows carry the content each ruling requires. RL-77 has since tightened the rows, and with `1bca029f7` they
match RL-77 word for word. Nothing below blocks admission. F-1 has to be closed before signing, but it is
not a defect in these commits.

## Checks

| # | Check | Result | Evidence |
|---|---|---|---|
| 1 | Binding | PASS | Against W1 `b4a6c217f`, `git diff -- joulewise/align/apple/v4_registration.py` adds exactly two `_NAMED_ARTIFACTS` entries: `joulewise/align/apple/r1_phase_table.py` (from the phase-table merge) and `configs/b6/flag_catalog_b6.json` (`c64049b66`). Nothing else changes in the file. Every path is strict, because `AMENDMENT_ALLOWLIST = ()` and `is_strict(p)` is `p not in AMENDMENT_ALLOWLIST`. |
| 2 | Test drives the real resolution | PASS | The test asserts four things: the v4 registration directory has no `acceptance.json`; `joulewise.b6.registration.load(v4_dir)` raises `(OSError, ValueError)`, the exception the harvest catches; the harvest's resolution expression is present verbatim in `scripts/harvest_b6_session.py`; and `DEFAULTS['catalog']` resolves to the path, which is bound and strict, with digest `01767fe4…1dd0c`, listed in the receipt. **An independent execution probe:** I ran the real `scripts.harvest_b6_session._run` with the v4 registration directory and a stubbed `resolve_inputs` that records its overrides. It gave `catalog_path = configs/b6/flag_catalog_b6.json`, SHA-256 `01767fe4e75ed961798f4e6b68cf055a5b3946a474129e93d2b5e7c239a1dd0c`. **Mutations, 8 of 8 caught:** one byte appended to the catalog; `DEFAULTS['catalog']` pointed at a byte-identical copy at another path; the harvest expression replaced; the test's digest altered by one nibble; the binding removed from `_NAMED_ARTIFACTS`; an `acceptance.json` placed in the v4 directory; a wrong digest in a signed receipt; the receipt entry removed. All were reverted and `git status` was clean. |
| 3 | Receipt template | PASS | Parsed as JSON against `b4a6c217f`: no top-level key added or removed, and no value outside `artifacts` changed. The existing `artifacts` keys keep their order and their `null` values. Two keys are appended at the end. `status` is still `PENDING_LEAD_REGISTRATION` and `lead_signature` is still `PENDING_LEAD_SIGNATURE`. |
| 4 | Trace | PASS | A structural JSON diff of `docs/align/v4/dynamic_closure_trace.json` against `b4a6c217f` finds `joulewise/align/apple/r1_phase_table.py` added to `executed`, `child_process_paths` and `by_event.{compiled,modules,opened}`, and nothing removed. The only other changes are in scenario metadata: `r1_synthetic_arm.tests_run` goes from 76 to 78 and `new_paths` from 4 to 5. The +2 matches the count of `def test_` in `tests/align/test_r1_rehearsal.py`, which goes from 74 to 76. `not_bound` and `not_strict` are both `[]`. |
| 5 | DEVIATIONS rows | PASS (see F-2, F-3) | See the row-by-row table below. |
| 6 | Tests | PASS | `python3.13 -B -m unittest tests.align.test_v4_executed_closure tests.align.test_v4_dynamic_closure`: 16 tests, OK, 64 s. That run includes the new catalog test, and the new test alone is also OK. As a supporting run, `tests.align.test_measurement_core_boundary tests.align.test_r1_rehearsal`: 82 tests, OK, 16.5 s. I also started the two PREQUAL test modules. They ran for more than 20 minutes on the shared Air, and I stopped them before they finished, so I have no PREQUAL test result of my own. The R1-PHASE-TABLE row's statement that PREQUAL passes rests on the lane's run and on Fable's review at `82c14c9ea`. `scripts/align_v4_prequal.py` is byte-identical to its W1 version. |

### Rows against their rulings

| Row | Ruling content required | Finding |
|---|---|---|
| EST-RESTORE | RL-58 has four requirements: restore the file to `70f47086…e5e4`; the memo goes outside the estimator under five conditions; a test that the estimator digest equals the pin; and one line saying which option was done. | Met. The file on the branch hashes to `70f47086b2445e88…16e5e4`. `document_memo` in `joulewise/b5/harvest.py` is a context-scoped memo, keyed by SHA-256, returning a pickle copy on each hit, storing only after a successful parse, and putting the original back in `finally`. `test_every_estimator_file_matches_issued_acceptance` checks all four `ESTIMATOR_CODE_PATHS`. RL-77 edit 4 is applied in `1bca029f7`. |
| R1-PHASE-TABLE | RL-61 has four requirements: a pure move; a module that imports nothing; binding it strict under RL-29; and condition 13. RL-72 and RL-77 add `workload.py` and the sentence that the slots name the commit. | Met. The module has no import statements and holds `phase_plan` and six constants. `run_night.py` and `align_r1_rehearsal.py` import it, and `git diff b4a6c217f -- scripts/align_v4_prequal.py` is empty. `1bca029f7` adds RL-77 edit 1. See F-1. |
| B6-CATALOG-BIND | RL-62 item 2 and RL-65 require: how the harvest selects the catalog by fall-through, and the three points of the order of authority. | Met. The fall-through matches the code exactly. Points (1) to (3) restate RL-65. See F-3. |
| IDENTITY-FLAGS | The RL-63 quoted text, plus RL-77 edit 2. | It matched RL-63 verbatim at `c64049b66`. At `1bca029f7` it carries RL-77's sentences verbatim. I confirmed in the bound catalog that all three codes have `effect: DISCLOSE`. |
| DRIVER-P9-W1 | RL-67 requires the six commits and their rulings, what changed, and what did not change, with the diff read in full. RL-68 adds the per-file DC-in sentence. RL-77 adds edit 3. | Met. `git log 3c9c47a4e..b4a6c217f -- joulewise/b5/driver.py` lists the six named commits exactly. I read the whole diff (+189/−10). Every hunk falls under admission, meter supervision, fault and outcome fields, or the unproven-termination marker. None touches how a member is launched, sampled or written. The RL-68 sentence is verbatim. See F-2. |

## Findings

| ID | Severity | Finding | Action |
|---|---|---|---|
| F-1 | MEDIUM (signing gate, not a defect in these commits) | After RL-77, the R1-PHASE-TABLE row says: "The slots file names that commit, and a registration test compares the files." No such test exists on the branch yet. `git grep` across `tests/` and `v4_registration.py` finds only `test_r1_phase_table_is_named_and_strict`, which checks the binding, not the byte identity with the slot-producing commit. The row is phrased as a condition at signing, so it is not false today. But it becomes false if the registration is signed before that test lands. | Land RL-61's condition-13 test, covering the six files against the commit the slots name, before signing. Do not sign while it is missing. |
| F-2 | LOW | DRIVER-P9-W1 says the commits "do not change how a member's run is launched, sampled or written". That is true of the capture code. One effect it does not mention: the driver's one-second supervision pass now also calls `MeterLiveness.check()`, which reads the new bytes of each meter stream every 10 s while members run. That adds a little host work during capture. It does not change any sample or record, so RL-67's capture-path condition still holds. The row stays within what RL-68 allows. | None required. If the research lead wants that overhead disclosed, it fits under "in-chain supervision". |
| F-3 | INFO | RL-62 item 2 lists "the battery exclusion B, the capture faults" among the protocol's own rules. The row names them only through "by A9's union" and does not list them. RL-77 says "B6-CATALOG-BIND stands as written", so the research lead accepted this omission. | None. |
| F-4 | INFO | `f41ee4e7c`'s message says the only difference is the new module. The `tests_run` and `new_paths` counters also moved, and both changes are explained above. | None. |
| F-5 | INFO | Still owed before signing, from RL-65 and RL-77 and outside these commits: the row for held windows, as RL-71 restated it; the row for the RL-53 bound edits and the RL-72 `workload.py` callback; RL-65's native check of `model.identity_underivable` (the catalog marks it `EXCLUDE_MEMBER`); and RL-62 item 4, the desk catalog digest compared at the W1 smoke. | Track on the signing checklist. |
