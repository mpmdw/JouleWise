# Executing review — PR #896 number-bearing hunks (C1 chain, rounds 9–11)

- **Reviewer:** Claude Opus 5.5 (`claude-opus-5-5`), Claude Code agent session, 2026-11-22. Executing seat of gate_policy rule 3.
- **Non-author:** I did not write, co-write or prompt any of the reviewed commits; this session first saw them through `git show`. **Process note:** 765c4a126 carries `Co-Authored-By: Claude Opus 5.5`, the same model as this seat. My independence for that commit is per session, not per family; the Sol seat is the cross-family check for 765c4a126.
- **Repository:** `/Volumes/JW-EXT/scratch/mythos-build-896/repo` (not modified). Base `b2e01464d6d4fbf2901ff4d4154df9455104a12a` (origin/ops/2026-11-11-w1-presign, an ancestor of head). Head `765c4a1262fbf701d29d860ff6defad81a723d4a` (local).
- **Execution:** `git archive` copies only: head in `$TMPDIR/opus-rev-896`; base files via `git show b2e01464:<path>` (plus a temporary base archive for the custody comparison, since removed); tools in `$TMPDIR/opus-tools-896`. Synthetic inputs only (the frozen C1 suite's invented history bundle and the committed alpha/beta/gamma plan trees). Python 3.13.18 unless noted. One test process at a time.

## Coverage

| Commit | Path | Blob after commit |
|---|---|---|
| (base) | joulewise/b5/chain.py | 5b944e3b705360bf23ceae55a7befc31274f64ed |
| (base) | joulewise/calibration_ledger.py | b1b3fdf7287ed810010d6872974350ad12beb091 |
| (base) | scripts/run_campaign.py | 2181546feaf0d0db659142533029918c5e9b747c |
| 3ae356e818e1b8bd9cec88597f9ba36d62bddd1a | joulewise/b5/chain.py | 03a2eaf3c2ac83c49fc2fa24dc430469945ac398 |
| 3ae356e818e1b8bd9cec88597f9ba36d62bddd1a | joulewise/calibration_ledger.py | e1ef407f57da4613aa72ee0976878c3ebc0a144c |
| 3ae356e818e1b8bd9cec88597f9ba36d62bddd1a | scripts/run_campaign.py | 829c88cf33f350fe6963057dc11801ca8091e4d2 |
| 949298c7c1eb52f10223b6d7fe2237e30bf2d590 | joulewise/b5/chain.py | 5b7143ee3c18f47c5b4452046cab72ed18e866c1 |
| 949298c7c1eb52f10223b6d7fe2237e30bf2d590 | scripts/run_campaign.py | 2181546feaf0d0db659142533029918c5e9b747c |
| e6da6a0be00aec2fc7ad44948e8d925252defd26 | joulewise/b5/chain.py | 5ab4e51f1a91e005499f414c7906650351db7306 |
| 88139ebffa4289eb79a87892df585a7accbad4c0 | joulewise/b5/chain.py | 5fe788036f359f864c4decb2a862c1a2908a47c4 |
| 765c4a1262fbf701d29d860ff6defad81a723d4a | joulewise/b5/chain.py | a1ec520cc2c9d045a83d77c9a2c644170dcdea88 |
| 765c4a1262fbf701d29d860ff6defad81a723d4a | joulewise/calibration_ledger.py (unchanged since 3ae356e) | e1ef407f57da4613aa72ee0976878c3ebc0a144c |
| 765c4a1262fbf701d29d860ff6defad81a723d4a | scripts/run_campaign.py | 2181546feaf0d0db659142533029918c5e9b747c |

Context read at head (not number-bearing): v4_registration.py `b099e3f71f0fc272fa4671d4e0df1771ea2e3dc5`, reserve_calibration_window_bracket.py `348af3e398509038b4ba3c6beaabb2c288f1b348`, validate_powermetrics_fiducial.py `4f7e4d9004c39ab1123e1305f4114ac22a9a2551`; tests: test_c1_closure.py `45868340d8d1b1929f0d76aec1ef98f043f94580`, adapter.py `5b6fd5e135fcd097f3abe153b0773a3412395bea`.

`scripts/run_campaign.py` is byte-identical to the base after 949298c7c: its blob at 949298c7c and at head is the base blob `2181546f…`, and `git diff base head -- scripts/run_campaign.py` is empty. `git log base..head` over the 16 registered paths plus the F8 list returns exactly the five commits above.

## Verdict: ADMIT-WITH-FIXES

No HIGH. I found no honest-mistake input that preflight admits and a chain consumer then consumes. The non-C1 render path is byte-identical to the base, `run_campaign.py` is unchanged, and the calibration-ledger hooks are inert when `JOULEWISE_C1_INPUTS` is absent. The A5 block closes every variable in the chain modules' read inventory. Mutation: all 7 production-line mutants in chain.py and at the A3 site are killed. Of the 4 calibration_ledger.py mutants, 1 is killed and 3 survive (LOW-6), so the tests miss defense-in-depth checks but no consumption path. One MED remains: A3's list of consumer pre-host checks is incomplete. Preflight admits rendered launches that a consumer's own gate refuses before host work. The fix is to share those gates the same way `verify_frozen_plan` is now shared.

## Findings

### MED-1: A3 coverage is incomplete. Preflight admits launches that the reservation, capture and runner refuse on argv alone.

`_check_consumers` (v4_registration.py:1160–1299) calls `runtime_ledger`, `verify_frozen_plan` and `_declared_slot_sources` for the reservation. It does not call the next argv-only gate in reservation `main` (reserve_calibration_window_bracket.py:424): `validate_bracket_session_reservation_inputs` (calibration_ledger.py:4774). That gate refuses a custody locator outside `<runs_root>/instrument_validation` (`custody_outside_runs_root`, calibration_ledger.py:4843), and it also checks the session-identity fields. Preflight also skips the capture writer's `CustodyDeadline(args.custody_budget_s, args.custody_deadline_epoch_s)` (validate_powermetrics_fiducial.py:2248, refusal `writer_bracket_arguments`), which runs before launch authentication. On the runner side, it skips the `--shakedown-gate` requires `--backup` refusal (run_campaign.py:10468). Preflight independently refuses any `--backup`, so a C1 stage carrying `--shakedown-gate` can never run.

Reproduction (`$TMPDIR/opus-tools-896/probe_med.py <head-copy> {reservation|capture-budget|shakedown}`). Each mode builds the frozen suite's invented `valid_24_closure` attempt through `adapter.Attempt`, runs the production packet builder, delivers the packet, calls `prepared_closure`, then evaluates the consumer's own code on the rendered launch (`chain.c1_chain_environment`):

- `reservation`, the unmodified valid fixture: builder exit 0, `prepared_closure` admits. Rendered `--runs-root …/claim_runs_root`, `--pre-custody-locator …/pre_calibration_dir`. `validate_bracket_session_reservation_inputs` on the rendered args, with well-formed synthetic identity vectors, refuses with `calibration_reservation_input_invalid {'slot': 'pre', 'reason': 'custody_outside_runs_root'}`. Control: the same call with the locators under `runs_root/instrument_validation` admits. The frozen tape's "admit" rows therefore include attempts whose reservation would refuse.
- `capture-budget`, which adds `--custody-budget-s 0` to the capture template: builder exit 0, preflight admits, rendered `custody_budget_s = 0.0`. `CustodyDeadline(0.0, None)` raises `ValueError: custody budget must be finite and positive`. `main` maps that to `writer_bracket_arguments` (by code reading, lines 2245–2252).
- The same admitted valid fixture renders its reservation without `--execute` (`execute = False` in the probe output). Preflight requires `session_kind == 'bracket'` but not `--execute`, and it does not refuse `--verify-only`. Without `--execute`, reservation `main` validates, prints `validated_not_reserved` and returns 0 (reserve_calibration_window_bracket.py:438–447, 606), so the chain does not stop. The pre capture then refuses before any hardware capture because no slot was reserved (validate_powermetrics_fiducial.py:2521–2524). This is by code reading; I did not run the capture.
- `shakedown`, which adds `--shakedown-gate production_uncertainty_v1` to a collection template: builder exit 0, preflight admits, rendered `shakedown_gate='production_uncertainty_v1'`, `backup=None`. I did not execute the runner refusal; it is from code reading at run_campaign.py:10467–10469.

Severity is MED under the brief's rule: preflight admits an honest mistake (a stale or wrong template value) and a consumer refuses it before host measurement. The runner case refuses after the pre-calibration capture, so it costs the window but not its numbers. Fix: move the argv-only part of each gate into a function that `main` and `_check_consumers` share. For the reservation that part covers session kind, declared slots, runs_root normalization, custody containment and non-empty identity strings, without the measured identity vectors. For the capture, construct `CustodyDeadline` from the rendered args. For the runner, call its argument-pair refusals. Add a named regression per gate. The frozen tape need not change. The invented kit lives in the frozen `suite/history.bundle`, but the bindings and the completed reservation flags come from the unfrozen `adapter.py` (`complete_arguments`, `bindings`). Those can follow `plan.py`'s rule `pre_calibration_dir=claim_runs_root/instrument_validation/pre_attempt_id` and add `--execute`.

### LOW-1: Non-C1 ledger readers now depend on an ambient `JOULEWISE_C1_INPUTS`

The 3ae356e hooks (`runtime_ledger` in `load_calibration_ledger_snapshot`, `CalibrationWriterLease`, `inspect_calibration_ledger`, `_locked_append` and `append_bracket_session_receipt`, plus `runtime_input_context` in `_committed_pin_bytes` and `PinnedUpstream`) activate whenever the variable is present, on any lane. When it is absent they reduce to the base code (read line by line). Non-C1 chains do not unset it; `scripts/run_night.py:_chain_environment` copies `os.environ`. Reproduction: `stale_c1_env_nonc1.py` uses a synthetic empty ledger in a temp dir. With no variable, `inspect_calibration_ledger` returns an inspection and `CalibrationWriterLease` returns a path. With a stale variable naming another ledger, both raise an untyped `ValueError: ledger does not resolve to the canonical C1 path`. This fails closed, so nothing is consumed. It does turn a leftover desk variable into a non-C1 crash outside the refusal registry. Suggested fix: pop `JOULEWISE_C1_INPUTS` in `run_night._chain_environment` for non-C1 plans, or convert the `ValueError` to a registered refusal.

### LOW-2: A2 duplicate refusal relies on a CPython-private return shape

`_c1_parse.RecordingParser._parse_optional` records an option only when `super()._parse_optional` returns a one-element list of tuples. Executed: on 3.13.18 and 3.14.6 (`dup_probe.py`), `--ledger x --ledger y`, `--ledger x --ledger=y` and `--ledger x --ledg y` are all refused. Not executed: `pyproject.toml` allows Python ≥3.11. By my reading of argparse, CPython 3.11 and early 3.12 return a single 3-tuple there. That would make the hook record nothing: A2 silently off, and `replace_option` appending instead of replacing. Fix: assert the shape (fail closed), or require ≥3.13 for the arm interpreter.

### LOW-3: A5 is closed over its stated inventory; ambient values still reach consumers through indirect reads

The A5 inventory covers direct `os.environ` and `os.getenv` reads in `joulewise/` and `scripts/` modules reachable from the five chain programs. I recomputed it at head: 40 names across 252 modules, matching `C1_ENVIRONMENT_NAMES` plus the patterns. There are no import-time reads (AST scan), so preflight's in-process judgement is not skewed by module constants captured from the caller. Indirect reads remain ambient: `HOME` via `expanduser`/`Path.home()` (e.g. `mlx_runtime` `model.source`, measurement_liveness `~/night-custody`), `TMPDIR`, `PATH`, `GIT_*` other than the three that `v4_registration.git` strips, and third-party libraries. One interaction is new in 765c4a126. Unsetting `JOULEWISE_CUSTODY_PARENT` / `JOULEWISE_ADDITIONAL_CUSTODY_PARENTS` makes run_campaign publish its active-campaign registry under the `HOME` default. measurement_liveness asks for "the same JOULEWISE_CUSTODY_PARENT in measurement and publication environments", so a census run with a configured parent would not see a C1 campaign. No repo code sets the variable (grep), so this is latent. Lead to decide: bind it from the packet, or refuse at arm when the arm environment sets a non-default parent.

### LOW-4: Preflight still reads the caller's `CALIBRATION_LEDGER`

`check_selections` (v4_registration.py:1150–1151) runs `check_ledger` on the caller's ambient `CALIBRATION_LEDGER` before it builds the closed environment. A5 says preflight validates "never the caller's ambient environment". The read only refuses, and the frozen row `external_calibration_ledger` requires it, so this is a spurious-refusal risk (an operator shell holding another lane's ledger), not a consumption risk. The A5 sweep test special-cases it. The lead should reconcile A5 with the frozen O2a row.

### LOW-5: One non-C1 diagnostic text changed

88139eb split the capture-command check in the `c1=False` branch of `stage_plan`. A calibration capture with two commands still raises `ChainRenderError`, but the message is now "has exactly one command" where the base said "names exactly one --slot" (`stageplan_errors.py`, base vs head). Duplicate `--slot` and `--slot=value` give identical messages. Only the message changed.

### LOW-6: The runtime C1 hooks in calibration_ledger.py have no killing test

M10 (the snapshot reader's canonical-ledger check), M12 (the append's starting-digest check) and M13 (`_locked_append`'s canonical-ledger check) survive every targeted test and frozen row I ran. M11 (the committed pin from the execution commit) is killed by the frozen row `audit8-bare-ledger/default`. The hooks work at head. In the positive control `hooks_probe.py` (synthetic files, C1 variable set), `load_calibration_ledger_snapshot` and `CalibrationWriterLease` accept the canonical ledger and raise `ValueError: ledger does not resolve to the canonical C1 path` for a same-byte copy. No test pins that behavior. `test_o2a…` calls `runtime_ledger` directly, and reservation `main` re-checks the starting digest before append. These hooks are defense in depth behind preflight, which checks every ledger spelling, so this is a test gap, not a consumption path. Suggested fix: a regression that runs the snapshot, append and lease readers under `ledger_environment` with a same-byte copy and with a changed starting byte.

## Probes that found nothing

- **Non-C1 render identity.** `noncl_identity.py` loads base `chain.py` (blob 5b944e3b) next to head `chain.py`. It renders the committed alpha/beta/gamma plan trees with `c1_inputs=None`, using `scripts.check_b5_chain.synthetic_bindings`, under 3 measurement roots (Path, str, and the copy root) × 5 keyword sets (default, `settle_s` 0 and 2.5, `horizon_s` 0 and 600) × spare retries on/off. All 90 renders are byte-identical. `stage_plan` tuples, every in-chain `stage_argv` and every `spare_argv` count (3 spare stages per pack) are also identical. The fixtures, packs, runbook and `check_b5_chain.py` are unchanged in base..head.
- **A5 environment block.** `C1ClosedEnvironmentTests` passes at head: 4 tests in 643 s, a 47-variable stale sweep, an inventory of 40 variables across 252 modules, and 14 near-miss digests refused. The rendered block comes after the inspection-mode refusal and `NIGHT_DIR` check and before the first `export REPO`, so no process runs before it. `unset -m 'JOULEWISE_*' 'PYTHON*'` precedes the chain's own `PYTHONPATH`/`PYTHONDONTWRITEBYTECODE` exports.
- **A1 parse path.** I compared `c1_stage_command` overrides (`--max-failures` = expected_count; `--arm-countdown-s` when present or with `--arm-quiet-mode`), `spare_argv` (config_dir located by the parser, `--max-failures` = count) and the derivation substitution with the non-C1 `stage_argv` by reading. They apply the same overrides, but locate options through the consumer's parser, so attached and abbreviated spellings are also handled. The consumer parsers have no short options other than `-h` and no aliases (`shortopts.py`), so the per-action duplicate check sees every spelling. Reads of the ledger, head pin and session ID in the rendered chain come from the reservation's parsed namespace, and the chain exports the same values the preflight parse used.
- **calibration_ledger.py non-C1.** Every hook falls back to `Path(path)` or the base branch when `runtime_input_context()` is `None` and `c1_inputs` is not passed. `_ledger_lock_path` already resolves, so the C1 change from an alias to the physical path keeps one lock file.

## Commands executed (all in `$TMPDIR` copies; `R=$TMPDIR/opus-rev-896`, `T=$TMPDIR/opus-tools-896`)

| Command | Result |
|---|---|
| `git show <c> -- <path>` for the 5 commits; `git rev-parse <c>:<path>`; `git log base..head -- <16 registered + F8 paths>` | Read all hunks; blobs as tabulated; exactly 5 commits |
| `cd $R && PYTHONPATH=tests:. python3.13 -B -m unittest -v align.test_c1_closure.C1ClosedEnvironmentTests` | **OK**, 4 tests, 643.5 s (47-variable stale sweep; inventory of 40 variables across 252 modules; 14 near-miss digests) |
| `cd $R && PYTHONPATH=tests:. python3.13 -B -m unittest -v C1ClosureTests.{test_reservation_plan_digest_covers_the_trailing_newline, test_shade_uses_the_rendered_cache_instead_of_stale_xdg_cache_home, test_gemini_6_1_shade_check_uses_the_rendered_cache_home, test_gemini_6_1_absent_cache_home_is_unset_and_shade_refuses, test_gemini_6_2_g2a_pre_bracket_plan_never_reaches_a_consumer}` | **OK**, 5 tests, 166.8 s |
| `python3.13 -B $T/noncl_identity.py $R` (base chain.py from `git show b2e01464:joulewise/b5/chain.py`) | 90/90 non-C1 renders byte-identical; stage_argv and spare_argv identical |
| `python3.13 -B $T/stageplan_errors.py $R` | Only the two-command capture message differs (LOW-5) |
| `python3.13 -B $T/inventory.py $R`; `$T/toplevel_env.py $R` | 40 names / 252 modules, all closed; 0 import-time reads |
| `python3.13 -B $T/dup_probe.py $R`; same under `python3.14` | Repeated, `=`-spelled and abbreviated `--ledger` refused on 3.13.18 and 3.14.6 |
| `python3.13 -B $T/shortopts.py $R` | Five consumer parsers: only `-h` short option, no aliases |
| `python3.13 -B $T/stale_c1_env_nonc1.py $R` | LOW-1 reproduction |
| `python3.13 -B $T/probe_med.py $R reservation`, `capture-budget`, `shakedown` | MED-1 reproductions |
| `cd $R && PYTHONPATH=tests:. python3.13 -B -m unittest tests.test_calibration_ledger tests.test_b5_chain_static_check tests.test_b5_chain.StagePlanTests tests.test_b5_chain.HelperTests` | **OK**, 106 tests (1 skipped), 250 s |
| `… -m unittest -v tests.test_b5_chain …` (zsh chain-run classes) | 12 of 12 that completed passed. I stopped the rest (about 40 s per test on this shared host). Byte-identical non-C1 renders cover them |
| `… -m unittest -v -f tests.test_calibration_ledger_custody` at head, then the first failing test at base and at head | 23 ok, then `NightBudgetAbortPathTests.test_a_blocked_slot_other_than_the_next_one_is_never_read` fails its 5 s wall-clock bound at base ("custody refusal exceeded 3.0s budget + 2.0s cleanup tolerance") and at head (FAIL, then `TimeoutExpired` on a rerun). Plain `CalibrationWriterLease` construction takes 4.2–5.7 s at base and 2.0–2.6 s at head on this host, so these failures come from host load, not from the PR. The module was not completed |
| `python3.13 -B $T/hooks_probe.py $R` | LOW-6 positive control: the hooks refuse a same-byte copy at head |
| `$T/driver.sh`, one process at a time: HEAD baselines (`test_o2a…`, `test_duplicate_reservation_head_pin_refuses`, frozen rows `audit8-bare-ledger/default`, `reservation-start-digest/normal` via `$T/scenarios.py`), then each mutant | Baselines OK/MATCH; mutant results below |

## Mutants (`$T/mutate.py`: exact unique-line edits applied to `$R`, run one at a time, reverted after each; HEAD baselines for every target passed first)

| ID | File:line at head | Mutation | Target test(s) | Result |
|---|---|---|---|---|
| R1 | v4_registration.py:1235 | delete preflight `verify_frozen_plan` call (A3 site) | test_reservation_plan_digest_covers_the_trailing_newline | **killed**: exact=False attempt admitted, observed (0, 0, admit, 1, 1) where (2, 2, refuse, 0, 0) was expected; FAILED in 57 s. Head passes, so this is the fail-before/pass-after |
| M2 | chain.py:1239,1252 | revert A5 for XDG: drop `XDG_CACHE_HOME` from the closed names; export it only when `cache_home` is set (ambient value otherwise kept) | test_gemini_6_1_absent_cache_home_is_unset_and_shade_refuses | **killed**: build refused for the wrong reason, "prepared chain differs from the resolved C1 dispatch" instead of "no cache_home binds its cache", because preflight judged the caller's XDG_CACHE_HOME; FAILED in 10 s |
| M1 | chain.py:1252 | never export `cache_home` (`XDG_CACHE_HOME: None`) | test_gemini_6_1_shade_check_uses_the_rendered_cache_home | **killed**: preflight judged XDG_CACHE_HOME=None, not the handoff cache_home; FAILED in 10 s |
| M3 | chain.py:1232 | patterns `("PYTHON*",)` (drop `JOULEWISE_*`) | test_gemini_6_2_g2a_pre_bracket_plan_never_reaches_a_consumer | **killed**: preflight judged the caller's stale JOULEWISE_G2A_PRE_BRACKET_PLAN (seen = [stale path], not [None]); FAILED in 36 s |
| M4 | chain.py:1271 | `apply_c1_environment` keeps the caller's closed names | test_gemini_6_2_… | **killed**: preflight judged the stale value (seen = [stale path]); FAILED in 47 s |
| M9 | chain.py:1282 | drop the `unset -m` line from the rendered block | test_gemini_6_2_… | **killed** only by the rendered-text assertion: the outcome (admit) and the preflight-judged value (None) both matched head; FAILED in 51 s |
| M6 | chain.py:1112–1113 | delete A2 duplicate refusal in `RecordingParser` | test_duplicate_reservation_head_pin_refuses | **killed**: both subtests (separate, and attached `=`) admitted, observed (0, 0, admit, 1, 1); FAILED in 134 s |
| M10 | calibration_ledger.py:2621 | snapshot reader skips the C1 canonical-ledger check | test_o2a_separate_same_byte_ledger_refuses_in_a_fully_pinned_stage; frozen row audit8-bare-ledger/default | **survived**: test_o2a OK (38 s); frozen row MATCH. See LOW-6 |
| M11 | calibration_ledger.py:1333 | `_committed_pin_bytes` ignores the runtime C1 context | frozen row audit8-bare-ledger/default | **killed**: frozen row DIFF, `CalibrationLedgerError: calibration_head_pin_not_committed` raised in observe_reservation |
| M12 | calibration_ledger.py:4903 | `append_bracket_session_receipt` skips the starting-digest check | frozen row reservation-start-digest/normal | **survived**: frozen row MATCH. Reservation `main` checks the starting digest itself before it calls append, so this guard is redundant on the tested route. See LOW-6 |
| M13 | calibration_ledger.py:4682 | `_locked_append` skips the canonical-ledger check | frozen row audit8-bare-ledger/default | **survived**: frozen row MATCH. See LOW-6 |
| M7 | chain.py:1596 | spare keeps the stage's `--max-failures` | not run: equivalent. run_campaign stops at `failures >= max_failures` (run_campaign.py:10782 etc.), and a spare set of `count` members cannot exceed `count` failures | equivalent |
| M5/M8 | chain.py (e6da6a0/88139eb ledger and head-pin threading) | use the bindings ledger and default head pin instead of the reservation's parsed values | not run: equivalent for every spelling preflight admits. All ledger spellings must resolve to the one canonical file (`check_ledger` on each), and the frozen explicit forms equal the defaults as strings | equivalent |

## Process notes

- The repository HEAD moved during this review: `90ee255f9a57c2d08cfae3ffcec15bd7ec6ee8d5` (01:31) changes only `configs/gates/hazard_refusals.json` (2 lines) and touches no number-bearing path. This paper covers `765c4a126` and earlier only.
- I did not run the frozen 94-case suite (`test_frozen_lite_decisions`), per the brief. I ran two of its rows individually through the production adapter (`$T/scenarios.py`), and they match the tape at head.
- The scratch copy and tools are under `$TMPDIR/opus-rev-896` and `$TMPDIR/opus-tools-896`. Every mutant was reverted; I did not modify the repository.

## Fix-round delta, 2026-11-22: 765c4a126..6355ffda5 (gate policy rule 4)

Scope: only the fix diff. 90ee255f9 is `configs/gates/hazard_refusals.json` only. 6355ffda5 touches v4_registration.py `985461864a50879e761694bcd29cc5c38505c3d5`, reserve_calibration_window_bracket.py `613383c27b82959828e41dbdbc83b389e27354fd`, adapter.py `17c4b22ab99088d1f8d4c80022667fb85df3fee1` and test_c1_closure.py `86174c00a016f3cc38597a9ad900ab2b362ba374`. No registered number-bearing path changed: `git diff --stat 765c4a1 6355ffd -- chain.py calibration_ledger.py run_campaign.py` is empty. Same reviewer and constraints as above: a git-archive copy in `$TMPDIR/opus-fix-896`, one test process at a time, no frozen suite. Like 765c4a126, 6355ffda5 is co-authored by Claude Opus 5.5.

### Delta verdict: ADMIT-WITH-FIXES

All four MED-1 items are closed and each is killed by the new named regression. Reservation `main` is unchanged in behavior. The remaining MED is the same defect class (A3: preflight admits what a consumer refuses before hardware capture), now across consumers: the capture compares its own argv-derived identity with the identity the reservation records. This is the class's second appearance, so under rule 4 the lead should write the structural rule.

### Findings

**D-MED-1: Preflight admits a capture whose identity cannot match the reservation's. The stand-in hides the one non-measured field.** The capture refuses `calibration_reserved_slot_mismatch` before any hardware capture when its planned identity differs from the reserved one (`_validate_reserved_bracket_slot`, validate_powermetrics_fiducial.py:1558–1577, called at 2525–2531 "before directory creation, sampler launch, and all hardware capture"). Two argv-derived fields are compared:
- **`--power-policy`:** the capture uses `args.power_policy`. The HAZARD reservation records the desk epoch's or desk T1's `power_policy`, else `b5.plan.POWER_POLICY` (`'ac_high_power'`), per `_hazard_measured_identity`, reserve…py:101–102. This is a prepared value, not a host measurement, but preflight replaces it with `MEASURED_AT_LAUNCH`.
- **`--sampler-binary`:** the capture's T1 `powermetrics_sha256` is `sha256(args.sampler_binary)` (2962). The reservation hashes `writer.POWER_METRICS`.

Executed (`probe_fix.py power|sampler`, frozen valid fixture, capture template edited):
- `--power-policy ac_low_power`: builder exit 0 (admitted). The reservation's own identity function on these inputs gives `power_policy='ac_high_power'`, a mismatch for both captures.
- `--sampler-binary /usr/bin/true`: builder exit 0. The hash differs from the reservation's (`088666fa…` vs `3381c286…`).

The final refusal step is from code reading; I did not run the capture writer. Fix: in C1, require each capture's `--power-policy` to equal the value the reservation will record (the prepared desk value, else `POWER_POLICY`), and refuse a non-default `--sampler-binary`. Or compute both identities' argv- and prepared-derived fields with the consumers' own code and compare them. Add a named regression per field.

**D-LOW-1: The stand-in cannot see a HAZARD fallback that leaves a field empty.** A failed host read falls back to the prepared desk value (reserve…py:84–89). The fixture's desk JSONs are `{}`. Executed (`probe_fix.py valid`): preflight admits. On this review host `mlx` is not importable, so `_hazard_measured_identity({}, {})` leaves `mlx_version=None`, and `reservation_inputs` with that real identity refuses `calibration_reservation_input_invalid`. This depends on the host (the measurement `.venv` presumably has mlx). It is recorded so the lead can choose: either require non-empty desk fallbacks for the read-backed fields (`os_build`, `hardware_model`, `powermetrics_sha256`, `mlx_version`, `protocol_sha256`), or accept it. No other prepared-input refusal is masked. Every other validator check (session identity, runs root, custody containment, distinct attempts, slot shape) runs on real argv values, and the HAZARD route reads the desk JSONs only as fallbacks (A6: "a record, never a refusal").

**D-LOW-2: The reservation-side `CustodyDeadline` call has no killing test.** Mutant F2 survives (below). The named regression zeroes only the capture's budget. Add a reservation `--custody-budget-s 0` subcase.

**D-LOW-3: Remaining argv seams outside the fix diff.** These are pre-existing, and preflight admits them.
- **Runner `--max-blocks`:** refuses in C1 by code reading. The purpose is not G2B_SHAKEDOWN, or else the renderer-forced `--max-failures` (≠ 1) conflicts (run_campaign.py:3287–3315, 10463).
- **Runner `--dry-run`:** the runner measures nothing and exits normally (code reading).
- **Capture `*_for_test` seams:** executed, `--time-scale-for-test 0.5` is admitted (builder exit 0). By code, the writer switches to the logical test clock and pulse driver (2475–2482, 2644–2651) and cannot complete a live capture.

The reservation already refuses its own test flags. Suggest refusing `--max-blocks`, `--dry-run`, every capture `*_for_test` and `--sampler-direct-for-test` as unsupported C1 modes.

### Checks that found nothing

- **Main unchanged.** `main_diff.py` runs reservation `main` at 765c4a126 and at 6355ffda5 on identical synthetic legacy-route inputs in validate-only mode, comparing exit code, stdout and stderr byte for byte. All 7 cases are identical: valid, custody outside, empty identity JSON, duplicate attempt IDs, derivation kind with bracket flags, plan hash mismatch, missing post flags. `reservation_inputs` is a verbatim move, and the returned `slots` is the object `main` used before.
- **`--execute` / `--verify-only`.** They are an argparse mutually exclusive group, so `not args.execute or args.verify_only` equals `not args.execute` (mutant F3b is equivalent and was not run).
- **Crash authorization.** The capture's `_configure_writer_crash_authorization` never refuses, and is inert with `JOULEWISE_*` unset, so no refusal is skipped there.

### Executed

| Command (in `$TMPDIR/opus-fix-896`, `PYTHONPATH=tests:.`) | Result |
|---|---|
| `python3.13 -B -m unittest -v C1ClosureTests.{test_opus_med_1_consumer_input_gates_refuse_before_host, test_reservation_plan_digest_covers_the_trailing_newline, test_gemini_6_1_absent_cache_home_is_unset_and_shade_refuses}` | **OK**, 3 tests, 145.5 s |
| `$T/main_diff.py <765c4a1 copy> <6355ffd copy>` | 7/7 identical |
| `$T/probe_fix.py <copy> valid\|power\|sampler\|timescale` | Builder exit 0 in all four; results as in D-MED-1, D-LOW-1 and D-LOW-3 |
| `$T/driver_fix.sh`: mutants via `$T/mutate_fix.py`, each reverted, target = the new named regression | Below |

| Mutant (v4_registration.py at 6355ffd) | Result |
|---|---|
| F1: drop the `reservation_inputs` call | **killed** (`outside_custody`: 0 != 2) |
| F2: drop the reservation `CustodyDeadline` call | **survived** (OK, 57.6 s): D-LOW-2 |
| F3: drop the `--execute` requirement | **killed** (`no_execute`) |
| F3b: `not args.execute` only | equivalent (argparse exclusivity); not run |
| F4: drop the capture `CustodyDeadline` call | **killed** (`zero_budget`) |
| F5: drop the `--shakedown-gate` refusal | **killed** (`shakedown`) |

The scratch copy was reverted to the 6355ffda5 bytes (`cmp` against the original). I did not modify the repository and left no processes running.
