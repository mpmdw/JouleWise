# Executing review of the number-bearing hunks on PR #896 (C1 chain closure)

- **Reviewer:** Fable 5.2 (`claude-fable-5-2`), cold executing reviewer.
- **Seat:** this review **replaces the unavailable Sol 6.1 seat**. Sol's command sandbox failed to
  initialize on this machine (`sandbox_apply: Operation not permitted`); gate policy rule 3 lets
  Fable replace either seat. An Opus 5.5 reviewer worked in parallel; I did not coordinate with it
  or read its paper.
- **Non-author:** I wrote none of the code, tests or documents under review.
- **Date:** 2026-11-22. Interpreter: `python3.13` (3.13.18), macOS.
- **Verdict: ADMIT-WITH-FIXES.** No HIGH. Two MED (preflight admits what the reservation consumer
  refuses), three LOW. The number-bearing hunks themselves showed no defect.

## Scope and identity

Reviewed head `765c4a1262fbf701d29d860ff6defad81a723d4a`; base `b2e01464d6d4fbf2901ff4d4154df9455104a12a`.

| Commit | `joulewise/b5/chain.py` | `joulewise/calibration_ledger.py` | `scripts/run_campaign.py` |
|---|---|---|---|
| base `b2e01464d` | `5b944e3b705360bf23ceae55a7befc31274f64ed` | `b1b3fdf7287ed810010d6872974350ad12beb091` | `2181546feaf0d0db659142533029918c5e9b747c` |
| `3ae356e818e1b8bd9cec88597f9ba36d62bddd1a` | `03a2eaf3c2ac83c49fc2fa24dc430469945ac398` | `e1ef407f57da4613aa72ee0976878c3ebc0a144c` | `829c88cf33f350fe6963057dc11801ca8091e4d2` |
| `949298c7c1eb52f10223b6d7fe2237e30bf2d590` | `5b7143ee3c18f47c5b4452046cab72ed18e866c1` | unchanged | `2181546feaf0d0db659142533029918c5e9b747c` |
| `e6da6a0be00aec2fc7ad44948e8d925252defd26` | `5ab4e51f1a91e005499f414c7906650351db7306` | unchanged | unchanged |
| `88139ebffa4289eb79a87892df585a7accbad4c0` | `5fe788036f359f864c4decb2a862c1a2908a47c4` | unchanged | unchanged |
| `765c4a1262fbf701d29d860ff6defad81a723d4a` | `a1ec520cc2c9d045a83d77c9a2c644170dcdea88` | `e1ef407f57da4613aa72ee0976878c3ebc0a144c` | `2181546feaf0d0db659142533029918c5e9b747c` |

- `scripts/run_campaign.py` is byte-identical to the base from `949298c7c` onward (`git diff --quiet`
  base..commit for each of the last four commits; same blob). Only `3ae356e81` differs, and
  `949298c7c` reverts it.
- Context files read at the head (not number-bearing): `joulewise/align/apple/v4_registration.py`
  `b099e3f71f0fc272fa4671d4e0df1771ea2e3dc5`, `scripts/reserve_calibration_window_bracket.py`
  `348af3e398509038b4ba3c6beaabb2c288f1b348`, `scripts/validate_powermetrics_fiducial.py`
  `4f7e4d9004c39ab1123e1305f4114ac22a9a2551`, `joulewise/align/shade/upstream.py`.
- **The repository moved during this review.** `HEAD` was `765c4a126` when I started; the builder
  later committed `90ee255f9` (01:31, `configs/gates/hazard_refusals.json` only) and `6355ffda5`
  (02:42, `v4_registration.py`, the reservation script and tests). **This paper covers `765c4a126`
  only.** Every result below was produced in, or re-run in, a scratch clone checked out at exactly
  `765c4a126` (`$TMPDIR/fable-rev/mut`, clean `git status` before and after), except where a line
  says otherwise. I modified no file in the repository.

## Findings

### F1 (MED). Preflight admits a reservation that its own consumer refuses

A3 asks preflight to run every refusal a chain consumer raises before host work. At `765c4a126`
`_check_consumers` runs `runtime_ledger`, `verify_frozen_plan` and `_declared_slot_sources` for the
reservation and stops. `reserve_calibration_window_bracket.main` next calls
`validate_bracket_session_reservation_inputs` (session, runs root, slot and custody arguments), and
only reserves when `--execute` is present. Neither is checked.

Reproduction (probe `fable_probes.ReservationProbe.test_probe_reservation_input_validation_gap`,
synthetic frozen fixture `valid_24_closure`, unmodified):

- Preflight: build `0`, install `0`, direct arm `admit`, host checkpoint entered once on each route.
- The reservation consumer, called through its own `main` on the rendered argv inside the rendered
  environment (`closure.consumer_environment`): exit `2`,
  `calibration_reservation_input_invalid`, `reason: custody_outside_runs_root, slot: pre`; ledger
  bytes unchanged. The fixture binds `--pre-custody-locator` to `<work>/pre_calibration_dir` and
  `--runs-root` to `<work>/claim_runs_root`.
- Control on the validator alone: custody under `<runs>/instrument_validation` is accepted, the
  fixture's layout is refused with the same reason.
- The same rendered reservation has no `--execute` (`execute_flag: false`). The committed
  `align_v4` template carries it; the frozen fixture does not, and preflight admits it. Without the
  flag the reservation validates and exits without reserving.

An honest stale or mis-bound custody locator, or a template that lost `--execute`, therefore passes
install and arm and fails at the chain's first stage. Nothing is measured and no ledger byte is
written, so this is MED under the brief's scale. Fix: call the reservation's own input validator
and require `--execute` in `_check_consumers`.

Not covered by this review: `6355ffda5` (committed while I worked) adds
`reservation.reservation_inputs` and a `--execute` requirement to `_check_consumers`. I read that
diff and re-ran this probe on a clone of it, for information only. The fixture there carries
`--execute` and the `custody_outside_runs_root` reason is gone. `main` still exits `2` with an
unspecific `reservation is malformed`; the identity vectors are measured on the host at launch, so
my off-host call with invented vectors does not show a remaining gap. I did not review that commit.

### F2 (MED). A sole stale `--head-pin` is admitted; preflight never judges the pin the reservation uses

Reproduction (probe `fable_probes.Probes.test_probe_sole_stale_head_pin`): the reservation template
names one `--head-pin` (no duplicate) that points at another committed pin file inside R,
`configs/calibration/retired-head.json` with `sequence 7`.

- Preflight: build `0`, install `0`, arm `admit`, host checkpoint entered. The rendered chain
  exports `LEDGER_HEAD_PIN=<view>/configs/calibration/retired-head.json`.
- The consumer's own gate on the same inputs, `calibration_readiness(ledger, retired pin,
  phase='pre-reserve')` under the chain's C1 context: `status='blocked'`,
  `refusal_code=calibration_ledger_rollback`. `main` raises that readiness before it reserves.

Preflight checks only that the selected pin resolves inside the view. The ledger readiness that
prepare computes uses the default pin, so the check and the consumer read different files. This is
the round-9 head-pin case without the duplicate. MED: the reservation refuses before any capture.
Fix: run the reservation's pre-reserve readiness on `args.ledger` and `args.head_pin` at preflight,
or require the selected pin to be the head pin the readiness check used. For information only: the
same probe on a clone of `6355ffda5` gives the same result (admitted; readiness `blocked`,
`calibration_ledger_rollback`).

### F3 (LOW). C1 render branches that select numbers have no repository regression

Mutants M6, M7 and M8 (below) change which command the C1 chain runs: no `--max-failures`
override, the bound derivation keeps the unpruned corpus manifest, the spare retry keeps the main
config directory. Each survives the focused repository test that covers its stage. `verify_chain`
compares the staged chain with a render from the same code, so it cannot see them. My probe kills
all three by asserting that, for a canonical template, each C1 launch argv equals `stage_argv`,
`spare_argv` agrees, and the C1 render equals the non-C1 render plus the environment block. At the
head that equality holds. Fix: add that equality as a regression. I did not run the 28-minute
frozen suite against these mutants.

### F4 (LOW). The duplicate-option guard depends on a private argparse return shape

`RecordingParser._parse_optional` records an option only when `len(result) == 1`, the list shape of
Python 3.13 and 3.14 (executed: `list 1` on 3.13.18 and 3.14.6; all four duplicate spellings refuse
on 3.14.6). `pyproject.toml` declares `requires-python >= 3.11`. On the older tuple shape (executed
on 3.9.6: `tuple 3`) the guard is false, nothing is recorded, and A2 would stop refusing repeats
without any error. I had no 3.11 or 3.12 interpreter, so the shape on those versions is not
verified. Fix: refuse an unrecognized shape, or pin the interpreter floor to 3.13.

### F5 (LOW). Notes on the closed environment and SHADE detection

- `check_selections` still reads the caller's `CALIBRATION_LEDGER` and refuses when it names
  another file. A5 says preflight never validates the caller's ambient environment. The check only
  refuses and selects nothing, and the frozen tape expects it. Recorded as a literal deviation.
- The inventory test covers `os.environ` and `os.getenv` reads in repository modules, as A5 words
  it. Child processes still inherit the launch shell's other variables (`HOME`, `GIT_*`, `TZ`,
  third-party cache variables). `v4_registration.git` strips three `GIT_*` names; nothing else is
  closed. Read from the code, not executed.
- `config_references` calls `shade_dependency` only for the factory
  `joulewise.align.apple.pilot:offline_shade_task` or a workload name containing `shade`. Another
  factory that builds a default `PinnedUpstream` skips the preflight check. In C1 the resolver
  itself confines the cache to R/S and disables fetch, so an outside cache is not consumed. Read
  from the code, not executed.
- With `c1_inputs` set, the chain emits the `session-status` record whenever the parser resolves a
  plan, because the head pin defaults. The non-C1 render emits it only when both options are
  explicit. Observed in the probe; C1 only; no change needed.

## Probes

**Non-C1 render is unchanged.** Differential harness: the base `chain.py` blob loaded beside the
head module, same inputs, `c1_inputs=None`.

- All 30 committed `plan_tree.json` files, with and without `spare_retries`: 60 of 60 renders
  byte-identical (run in the repository at 01:18 and re-run in the pinned clone).
- Perturbation sweep on four trees (`align_v4`, `bytes-s1-p1`, one contrast, one floor): drop a
  binding, drop or duplicate an option pair, drop a flag, attach `--opt=value`, duplicate or remove
  a command. 1,904 cases: 1,570 identical renders, 326 identical errors, 8 differences. All 8 are
  the message text of a `ChainRenderError` for a calibration capture with two commands (`names
  exactly one --slot` became `has exactly one command`). Both sides refuse.
- An earlier sweep over all 30 trees printed the same class only in its last 40 lines; I cut its
  summary line with `tail` and do not cite its totals.
- `tests.test_b5_chain` and `tests.test_b5_chain_static_check`: 31 tests, OK.

**C1 launches equal the non-C1 commands.** Probe on a spare-enabled synthetic attempt: 7 launch
argv and the spare argv equal the non-C1 ones; with an explicit `--head-pin` the C1 render minus its
8-line block is byte-identical to the non-C1 render, and equals the staged chain.

**`calibration_ledger.py` hooks.** Without `JOULEWISE_C1_INPUTS` each hook returns `Path(path)`.
Probe `LedgerHookProbe` on an admitted attempt, under the chain's context: a same-byte copy of the
ledger refuses in `load_calibration_ledger_snapshot` (environment and `c1_inputs` routes),
`CalibrationWriterLease` and `inspect_calibration_ledger`; `_committed_pin_bytes` returns the
execution commit's pin after the authority's `HEAD` moves to a different pin, and `None` outside R;
`append_bracket_session_receipt` refuses a wrong starting digest with the ledger unchanged; the
valid route reserves on the one live file. The new import in these paths loads only
`joulewise.align.apple.v4_registration` and light package parents.

**Closed environment.** The rendered block precedes every command the chain runs. After it the
chain sets `PYTHONPATH`, `PYTHONDONTWRITEBYTECODE` and `GIT_OPTIONAL_LOCKS` itself.

## Commands and results

All in the pinned clone unless marked. `PYTHONPATH=tests:.` and `python3.13 -B -m unittest`.

| Command | Result |
|---|---|
| `align.test_c1_closure.C1ClosedEnvironmentTests` (repository, 01:14 to 01:25, tree then equal to `765c4a126` in code) | 4 tests OK, 628 s; 47 stale variables swept, 40 variables read across 252 modules, 14 near-miss digests refused |
| `align.test_c1_closure.C1ClosedEnvironmentTests` (pinned clone) | 4 tests OK, 280 s; same three counts |
| `…C1ClosureTests.test_reservation_plan_digest_covers_the_trailing_newline` | OK |
| `…test_shade_uses_the_rendered_cache_instead_of_stale_xdg_cache_home` | OK |
| `…test_gemini_6_1_shade_check_uses_the_rendered_cache_home` | OK |
| `…test_gemini_6_1_absent_cache_home_is_unset_and_shade_refuses` | OK |
| `…test_gemini_6_2_g2a_pre_bracket_plan_never_reaches_a_consumer` | OK |
| `…test_duplicate_reservation_head_pin_refuses`, `…test_single_attached_derivation_option_selects_same_manifest_for_pruning`, `…test_spare_dispatch_uses_the_same_scoped_ancestor_lookup_and_pin`, `…test_o2a_separate_same_byte_ledger_refuses_in_a_fully_pinned_stage` | OK |
| `tests.test_b5_chain tests.test_b5_chain_static_check` | 31 tests OK |
| `tests.test_calibration_ledger` | 95 tests OK (1 skipped) |
| Reviewer probes at the head (`fable_probes.py`) | pass, except the two that record F1 and F2 |

Not run: the frozen 94-case suite (`test_frozen_lite_decisions`), the rest of `C1ClosureTests`,
`tests.test_b5_chain_prune2`, `tests.test_calibration_ledger_custody`.

## Mutants

One production line each, applied in the pinned clone and restored; the clone was clean after the
runs. "Repository test" is the named `C1ClosureTests` case; "probe" is mine.

| Mutant | Repository test | Probe |
|---|---|---|
| M1 `chain.py`: revert round 11, `XDG_CACHE_HOME` neither exported nor unset | **killed** by `test_gemini_6_1_shade_check_uses_the_rendered_cache_home` (`(0,0,'admit',1,1) != (2,2,'refuse',0,0)`) | not run |
| M2 `chain.py`: chain omits `unset -m` | **killed** by `test_gemini_6_2…` | not run |
| M3 `chain.py`: preflight model ignores the patterns | **killed** by `test_gemini_6_2…` | not run |
| M4 `chain.py`: chain omits the name `unset` | **killed** by `test_gemini_6_1_absent_cache_home…` | not run |
| M5 `chain.py`: duplicate check disabled | **killed** by `test_duplicate_reservation_head_pin_refuses` | killed |
| M6 `chain.py`: C1 drops the `--max-failures` override | **survives** `test_spare_dispatch…` | killed |
| M7 `chain.py`: C1 derivation keeps the unpruned manifest | **survives** `test_single_attached_derivation…` | killed |
| M8 `chain.py`: C1 spare retry keeps the main config directory | **survives** `test_spare_dispatch…` | killed |
| M9 `chain.py`: `CALIBRATION_LEDGER` exported from the binding, not the parse | **survives** `test_gemini_6_2…` | survives |
| M10 `chain.py`: attached option replaced as if split | **killed** by `test_single_attached_derivation…` | not run |
| M11 `calibration_ledger.py`: snapshot reader skips the runtime path check | **survives** `test_o2a…` | killed |
| M12 `calibration_ledger.py`: `_committed_pin_bytes` ignores the C1 context | **survives** `test_o2a…`, `test_gemini_6_2…` | killed |
| M13 `calibration_ledger.py`: reservation append skips the starting digest | **survives** `test_o2a…` | killed |
| M14 `calibration_ledger.py`: `c1_inputs` route skips `check_ledger` | **survives** `test_o2a…` | killed |
| M15 `calibration_ledger.py`: writer lease skips the path check | not run | killed |
| M16 `calibration_ledger.py`: `inspect_calibration_ledger` skips the path check | not run | killed |
| M17 `calibration_ledger.py`: `_locked_append` skips the path check | not run | **survives** |
| M18 `calibration_ledger.py`: pin read from the authority `HEAD`, not the execution commit | not run | killed |

Fail-before, pass-after for round 11: with M1 applied, `test_gemini_6_1_shade_check_uses_the_rendered_cache_home`
fails (preflight admits on the caller's stale cache); at `765c4a126` unmodified it passes (control
run of the same nine tests, all OK).

Reading the survivors:

- M6 to M8: no repository test in my focused set pins these branches (F3).
- M9: equivalent in every admitted attempt. Preflight requires the binding, the parsed option and
  the exported value to resolve to the one canonical ledger file.
- M11 to M14: `test_o2a…` refuses at preflight and never reaches the runtime hooks. The frozen
  suite's `observe_reservation` and `wrong_reservation` rows exercise the valid append and the
  script-level digest check; I did not run them, so I cannot say which of these it kills.
- M17: the reservation path reaches `_locked_append` only after
  `append_bracket_session_receipt` has already checked the path. My probe has no direct case.
- In an earlier pass my render-equality probe had a comparison bug on templates without
  `--head-pin`; its "kills" for M7 and M9 in that pass were not valid. The table reports the re-run
  with an explicit pin, where the unmutated control passes.

## Files

- Probes, harnesses and mutant specifications (scratch, outside the repository):
  `$TMPDIR/fable-rev/tools/` (`fable_probes.py`, `diff_render.py`, `diff_fuzz.py`, `mutate.py`,
  `mutants.json`, `mutants2.json`, `mutants3.json`).
- Logs: `$TMPDIR/fable-rev/` (`base-closedenv.log`, `fuzz4.log`, `probes-head*.log`,
  `mut-control.log`, `mutants.log`, `mutants2.log`, `clone-runs.log`, `later-probes.log`).
