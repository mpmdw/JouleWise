# Executing review, C1 round 12, PR #896 (Fable seat)

- **Reviewer / model:** Fable 5.2 (`claude-fable-5-2`), cold executing reviewer.
- **Seat:** the Sol 6.1 seat of gate policy rule 3 (`docs/process/gate_policy.md`). Sol's command sandbox cannot
  initialize on this machine (`sandbox_apply: Operation not permitted`), and the policy lets Fable replace either
  seat. The policy text names "Fable 5.1"; this seat was run by Fable 5.2. The other seat (Opus 5.5) worked
  independently; I did not read its paper or coordinate with it.
- **Non-author statement:** I wrote none of the code or tests under review and modified no file in the repository.
- **Date:** 2026-11-22. Repository `/Volumes/JW-EXT/scratch/mythos-build-896/repo`, HEAD `3daea0447`.

## Verdict: ADMIT-WITH-FIXES

The number-bearing commit `bc224942e` is sound: default behavior and every existing caller are unchanged, the new
flag is used only by the read-only preflight, and its line is load-bearing and killed by the spec. The ruling's
named cases (policy, sampler, reservation rollback pin, caller ledger pointer) are implemented and behave as ruled.
One MED remains (F1): a capture's own `--head-pin` is still not checked, which is a consumer refusal decidable from
prepared inputs. Nothing HIGH was found: no probed honest-mistake input is consumed.

## Commits and blobs covered

Diff `c5b8b8047cc3eef361e4da1cabb8c9ee718e8ec8..3daea0447f571683a97ae8579c3a7436a0fc32c7`.

| Commit | Path | Blob |
|---|---|---|
| `7f2155750528ce6e0469ec226857356a8aa1a22b` | `tests/align/test_c1_closure.py` | `ce38b4653537daff4a1f887e1a254c4bfcbdc076` |
| `7f2155750` | `tests/align/c1_closure_lite/adapter.py` | `1cf4cc2326fe9a826df43a04f118b641515e2da1` |
| `bc224942e83b4833a860d0824f297709fa69c727` (number-bearing, F8) | `joulewise/calibration_ledger.py` | `37fa093f0a2b8f7e62b94f770e43a3abb4effcb3` |
| `3daea0447f571683a97ae8579c3a7436a0fc32c7` | `joulewise/align/apple/v4_registration.py` | `8fdb4db7a32e684d3b69c8555e7f2ca181b839d9` |
| `3daea0447` | `scripts/reserve_calibration_window_bracket.py` | `81418de78c39e3c6db64a0c3424a829a05a3eb9a` |
| `3daea0447` | `scripts/validate_powermetrics_fiducial.py` | `5bf434e92005b408a9996386c9b3ecfa26ed0f76` |
| `3daea0447` | `configs/gates/hazard_refusals.json` | `abcad516da893a145f58cfa2b1983b7f5468e947` |

Spec order holds: both test files have the same blob at `7f2155750` and at `3daea0447`, so the acceptance cases
were committed before the fix and not edited after. `tests/align/c1_closure_lite/suite/` (the frozen 94 cases and
manifest) has no change in the diff.

## Findings

### F1 (MED) A capture's `--head-pin` that selects a rollback pin is admitted; the capture refuses at launch

Preflight applies the pre-reserve pin check to the reservation's `--head-pin` only. For a capture it only fences
the path (`view.locate(args.head_pin)`). A capture whose `--head-pin` names the same in-tree retired pin the
ruling's rollback case uses is admitted on both routes.

- Reproduction (probe `probe_c1.py::test_a_capture_head_pin`): the r11 rollback test's tree and pin
  (`sequence 7`, digest `7`x64), but `set_option(capture_arguments(tree, slot), '--head-pin', 'repo_path', retired)`
  instead of the reservation's. Observed for `pre` and for `post`, each mutated independently:
  `(build, install, direct arm, host entries) = (0, 0, 'admit', 1, 1)`.
- What the consumer does: the capture's `_begin_once` calls `calibration_readiness(phase="pre-slot",
  enforcing_under_lease=True, ...)` on its own pin and raises the refusal. Executed on a synthetic ledger with an
  open session and the capture's HAZARD arguments (`probe_preslot.py`): reservation's pin -> `ready`; retired pin
  -> `blocked calibration_ledger_rollback`. I did not run the capture CLI end to end.
- Why MED and not LOW: the refusal comes before any sample, so nothing is consumed, but it comes after arm (host
  checkpoint entered) and after the reservation has appended its session to the live ledger.
- Scope: the ruling's bullet names the reservation's pin; its headline ("every consumer refusal that can be
  decided from prepared inputs, including agreements between consumers") covers this. Simplest fix: require each
  capture's resolved `--head-pin` to equal the reservation's, with a per-slot regression.
- Not probed: the campaign runner's `--head-pin` (also only fenced). I do not know whether the runner refuses on it.

### F2 (LOW) Surviving mutants: four refusal properties the ruling names are not pinned by the spec

Head behaves correctly in each case (probed); the tests would not notice a regression.

- **M17** (entry check keeps the fence but drops `check_ledger`): survives `test_r11_caller_ledger_pointer_is_refusal_only`.
  Its "different path" cases are missing or outside the fence. No case supplies a different file inside the fence.
- **M7** (desk T1 before desk epoch): survives the r11 policy test and `test_reserve_calibration_hazard.DeskIdentityTests`.
  The ruled precedence is untested. Probes B1-B3 show head correct (T1-only policy honored; epoch beats T1).
- **M3** (preflight passes `hazard=False`): survives the r11 rollback test. No control admits a lagging
  (`PHYSICAL_AHEAD`) pin, so "preserve the consumer's pin-relation semantics" is unpinned at preflight.
- **M12** (preflight forces `pre_reserve_strict=True`): survives. Only a resumable existing session distinguishes it.

### F3 (LOW) The default live-writer probe has no coverage in `tests.test_calibration_ledger`

**M1b** inverts the new condition (`or probe_live_writer`), which disables the probe for every default caller. All
95 tests in `tests.test_calibration_ledger` still pass. The gap predates the diff, but the diff adds the switch. A
direct two-line test (holder process, flag True -> `calibration_live_writer_contention`, flag False -> `ready`)
would pin both values; `probe_contention.py` shows exactly that result at head.

### F4 (LOW) A case-variant spelling of the sampler is refused

`reserved_identity_refusal` compares `os.path.realpath` strings. On this case-insensitive volume
`/usr/bin/POWERMETRICS` names the reservation's sampler but refuses `calibration_reserved_slot_mismatch` on both
routes (probe D). Fails closed, before host. A symlink alias to the default is admitted. Note only.

### F5 (NOTE) A relative `CALIBRATION_LEDGER` is resolved against the launch view, not the caller's directory

`CALIBRATION_LEDGER=runs/calibration_observation_ledger.jsonl` is admitted from any working directory (probe C).
The check selects nothing and the chain replaces the variable, so nothing follows from it.

### F6 (NOTE, not from this diff) One reservation CLI test fails on this machine at base and at head

`test_reserve_calibration_hazard.HistoricalCustodyAtReservationTests.test_unreadable_historical_capture_times_out_legacy_and_is_never_read_on_hazard`
fails ("custody refusal exceeded 3.0s budget + 2.0s cleanup tolerance") identically at `c5b8b8047` and `3daea0447`.

## Answers to the brief's probe questions

1. **`bc224942e` default and callers.** The only change is `if enforcing_under_lease or not probe_live_writer`.
   Callers of `calibration_readiness`: `recover_calibration_ledger.py:521`, `validate_powermetrics_fiducial.py:1814`,
   `reserve_calibration_window_bracket.py:403` (via `pre_reserve_readiness`, default `True` from `main`). The only
   `probe_live_writer=False` in the tree is `v4_registration.py:1265` (preflight).
2. **Read-only readiness creates, locks or modifies nothing.** `probe_readiness.py`: 13 synthetic ledger/pin
   states x hazard x strict = 52 comparisons. A full recursive listing (size, mtime, mode) of the ledger directory
   was identical before and after every read-only call, including the first, when no lock file existed yet. In the
   C1 harness the ledger directory held only the ledger after refusals and admissions.
3. **Same decision as the lease-held call.** In all 52 comparisons the read-only outcome (return or refusal code)
   equalled the lease-held one: ready, rollback, malformed/missing pin, open session, lagging pin (ready on HAZARD,
   `reservation_head_mismatch` on legacy), divergent pin, torn tail. The one intended difference is a live writer:
   read-only returns `ready` where the probing call refuses; the reservation's own lease catches that at use.
4. **Reservation `main`.** The moved block is the same statements with the same arguments; the `else` branch became
   `if readiness.status == "ready"`. `tests.test_calibration_ledger` (95), `DeskIdentityTests` (5) and the refusal
   census (24) pass at head. I found no behavioral difference.
5. **Policy/sampler agreement.** Not fooled by any probed honest mistake (B2, B3, B4, sampler mismatches, absent
   sampler); equivalent spellings pass except F4. The sampler is never opened: the absent-path case refuses.
6. **Other undecided refusals.** F1. `reserved_policy`/`reserved_sampler` cannot be unbound: `stage_plan` requires
   the reservation to be the first chain stage.

## Commands executed and results

All with `python3.13`, one test process at a time. Baselines ran in the repository with `-B`; probes and mutants
ran in `$TMPDIR/fable-r12` (`git archive 3daea0447`), `PYTHONPATH=tests:.`.

| Command | Result |
|---|---|
| `unittest -v align.test_c1_closure.C1ClosureTests.test_r11_*` (the four named cases, repo) | 4 tests OK, 465 s |
| `scripts/quick_suite.py --module tests.test_calibration_ledger` (repo) | 95 tests, PASS, 1 skipped |
| `unittest hazards.test_refusal_allowlist` (scratch) | 24 tests OK, 1 skipped (moved `hazard_refusals.json` rows match) |
| `unittest test_reserve_calibration_hazard.DeskIdentityTests` (scratch) | 5 tests OK |
| `probe_readiness.py` | 52/52 equal decisions, 52/52 unchanged listings |
| `probe_preslot.py` | reservation pin `ready`; retired pin `calibration_ledger_rollback` |
| `probe_contention.py` | flag True `calibration_live_writer_contention`; flag False `ready`; holder exited 0 |
| `probe_c1.py` A | capture `--head-pin` retired, pre and post: admitted (F1) |
| `probe_c1.py` B | B1 T1-only matched: admit. B2 T1-only, default captures: refuse. B3 epoch over T1: refuse. B4 integer desk policy: refuse. B5 malformed desk epoch, default captures: admit |
| `probe_c1.py` C | relative canonical: admit (F5). `/./` and trailing slash: admit. Outside symlink to canonical: `outside R/S`. Directory, whitespace, `..` alias, upper-cased name: refuse |
| `probe_c1.py` D | symlink alias: admit. Case variant: refuse (F4) |

Every refusal in B and D was `(2, 2, 'refuse', 0, 0)` with `calibration_reserved_slot_mismatch`, ledger bytes
unchanged, ledger directory holding only the ledger.

## Mutants

Each applied alone to the scratch copy, run against the named test, then restored (scratch verified pristine).

| ID | Mutation | Test | Result |
|---|---|---|---|
| M1 | `calibration_ledger.py` (bc224942e line): drop `or not probe_live_writer` | r11 rollback | **killed** |
| M1b | same line: `or probe_live_writer` (default never probes) | `tests.test_calibration_ledger` | **SURVIVED** (F3) |
| M2 | preflight passes `probe_live_writer=True` | r11 rollback | killed |
| M3 | preflight passes `hazard=False` | r11 rollback | **SURVIVED** (F2) |
| M11 | preflight skips `pre_reserve_readiness` | r11 rollback | killed |
| M12 | preflight forces `pre_reserve_strict=True` | r11 rollback | **SURVIVED** (F2) |
| M13 | `pre_reserve_readiness`: return instead of raise on session-not-found | r11 rollback | killed |
| M4 | `reserved_identity_refusal`: policy check disabled | r11 policy | killed |
| M14 | policy check on `pre` only | r11 policy | killed (post) |
| M8 | `reserved_power_policy` ignores the desk files | r11 policy | killed (control) |
| M7 | `_desk_power_policy`: T1 before epoch | r11 policy; `DeskIdentityTests` | **SURVIVED** both (F2) |
| M5 | sampler check disabled | r11 sampler | killed |
| M15 | sampler check on `pre` only | r11 sampler | killed (post) |
| M6 | sampler compared by string, no `realpath` | r11 sampler | killed (equivalent spelling) |
| M16 | preflight's reserved sampler set to `/usr/bin/true` | r11 sampler | killed (default control) |
| M9 | entry check back to `os.environ.get` (empty passes) | r11 caller ledger | killed |
| M10 | entry check disabled | r11 caller ledger | killed |
| M17 | entry check keeps `view.locate`, drops `check_ledger` | r11 caller ledger | **SURVIVED** (F2) |

M1 and M2 die for the real reason: with the probe on, the build-time preflight leaves
`calibration_observation_ledger.jsonl.lock` in the stage, and install then refuses
`unlisted staged file: runs/calibration_observation_ledger.jsonl.lock` instead of the rollback code.

## Limits

- The 94-case frozen suite was not run, per the brief. No custody, energy, power, meter, transcript, slot, sealed
  or restricted data was opened; all inputs were synthetic. No network, push, fetch or ssh.
- F1's consumer-side refusal rests on an executed readiness call plus reading `_begin_once`, not on a capture run.
- Whether the HAZARD route is the one taken at launch depends on launch lineage, which does not exist at preflight;
  I accepted the preflight's `hazard=True` on that basis.
- Probe and mutation scripts are in `/Volumes/JW-EXT/tmp/fable-r12-probes/`; the scratch copy is
  `/Volumes/JW-EXT/tmp/fable-r12/`. No background process was left running.

---

## Fix-round delta, 2026-11-22 (gate policy rule 4)

Same reviewer and seat (Fable 5.2 in the Sol 6.1 seat), same non-author statement. Only the fix diff
`3daea0447..062698aff` was reviewed. I did not read the parallel review.

### Delta verdict: ADMIT

Nothing above LOW. F1 is closed for captures, collections and the bound derivation. Earlier survivors M7 and M17
are now killed. `fcfc0dee4`'s default and existing callers are unchanged, and capture `main`'s custody locator is
unchanged. No refusal was observed on any control or default chain.

### Commits and blobs

| Commit | Path | Blob |
|---|---|---|
| `48b50958c9b2986ecadf683168c0cb86b73c371a`, `ddd369dc6cabfcb2f5ef7c8813df36aa87d5b33a` (spec) | `tests/align/test_c1_closure.py` | `e32aa159e4ff7e36205f6d49abd5fbe49d228642` at `ddd369dc6` |
| `fcfc0dee489e649d641ac34793eeed1a5000ddaa` (number-bearing) | `joulewise/calibration_ledger.py` | `fcd1bbdcca032c86d8d889f7fa2e3790bffeb33b` |
| `062698aff48cebec883137cf08e9a25a08d26ef9` | `joulewise/align/apple/v4_registration.py` | `5cd823e6bf16890ac8d9d160febcba0d0417b9a6` |
| `062698aff` | `scripts/reserve_calibration_window_bracket.py` | `a76cb6cf9c50c2c9bebc75e9f36ede837b751bd2` |
| `062698aff` | `scripts/validate_powermetrics_fiducial.py` | `26b836495b0e6d72442a9288f8e852aa60c778c2` |

Spec order holds: `tests/` has no change between `ddd369dc6` and `062698aff` (the test file blob is identical).
The frozen suite directory is untouched. I did not re-run the new cases on `3daea0447`; the earlier section's
probe A already showed the capture head-pin cases admit there.

### What was asked, and what I found

1. **F1 closed.** `same_head_pin` holds every capture and campaign stage to the reservation's located pin file.
   `test_r11_every_consumer_reads_the_reserved_head_pin` passes (pre, post, collection refuse; explicit default
   admits). Probe Pa: a `bound_derivation` stage with the retired pin also refuses on both routes
   (`C1 campaign head pin differs from the reservation's head pin`), ledger unchanged.
2. **`fcfc0dee4` default and callers.** One line changed:
   `live_writer = writer_lease_is_live(ledger_path) if probe_live_writer else False`. Callers
   (`b5/plan.py:663`, `controller.py:963`, `calibration_ledger.py:6393`, `recover_calibration_ledger.py:427/438/511`)
   pass nothing and keep the probe. Reservation `main` reaches it with the default `True`. The only `False` is the
   preflight (`v4_registration.py:1273`, via `pre_reserve_readiness`). Executed under a live holder in another
   process: default and `True` report `live_writer True, calibration_live_writer_contention`; `False` reports
   `False, None`.
3. **Resumable route is read-only and decides as the lease-held call.** Three states (same open session; other
   session; same session with a rollback pin) x strict: 6/6 equal outcomes, 6/6 unchanged directory listings, and
   no lock file created after I removed it before each read-only call.
4. **Capture `main` custody locator unchanged.** `bracket_custody_locator(root, id)` equals the replaced
   `normalize_calibration_custody_path(root / id)` for 5 root spellings x 2 ids (10/10), including the non-bracket
   timestamp id, which `main` still passes.
5. **Slot agreement.** `test_r11_capture_slot_binding_must_match_the_reservation` passes; session, attempt and
   output-root mismatches refuse `calibration_reserved_slot_mismatch` on both routes.
6. **No regression.** All nine r11 cases, `ReservedIdentityTests` and `tests.test_calibration_ledger` (95, 1
   skipped) pass at `062698aff`.

### Findings (all LOW or NOTE)

- **D1 (LOW) N6 survives.** Disabling the attempt-id comparison in `reserved_slot_refusal` still passes the slot
  test: the wrong attempt id also changes the derived custody locator, so the locator check refuses. The attempt
  check matters only when the reservation's own attempt id and custody locator disagree with each other; no case
  builds that.
- **D2 (LOW) N1b survives.** Inverting the new `calibration_session_status` default (default callers never probe)
  passes all 95 tests in `tests.test_calibration_ledger`. Same class as F3. `tests/test_calibration_exits.py` has a
  live-writer witness that may cover it; I did not run that module.
- **D3 (NOTE) The pin agreement is by file, not content.** A capture `--head-pin` naming a separate file with the
  same pin content is refused at preflight (probe Pb), where the capture itself would judge it identically. It
  fails closed before host, and matches the rule as written ("the pin the reservation judged").
- **D4 (NOTE, pre-existing, outside the fix).** On the non-strict route a session status that returns with its own
  `refusal_code` set is not acted on by `pre_reserve_readiness`; it only reacts to a raised error. Preflight mirrors
  `main` exactly here, so there is no disagreement between them. I did not probe what `main` does next.
- F2's M3 and M12 gaps, F3 and F4 were not in this fix's scope and stand as written above.

### Mutants (fresh copy of `062698aff`, one at a time, restored and verified pristine)

| ID | Mutation | Test | Result |
|---|---|---|---|
| N1 | `fcfc0dee4` line: always probe | r11 resumable | killed (install refuses, `(0, 2, 'refuse', 0, 0)`) |
| N1b | same line: probe only when the flag is False | `tests.test_calibration_ledger` | **SURVIVED** (D2) |
| N2 | `pre_reserve_readiness` drops the pass-through to session status | r11 resumable | killed |
| N3 | capture: `same_head_pin` back to `view.locate` | r11 head pin | killed (pre capture) |
| N4 | campaign: `same_head_pin` back to `view.locate` | r11 head pin | killed (collection) |
| N5 | session-id check disabled | r11 slot binding | killed |
| N6 | attempt-id check disabled | r11 slot binding | **SURVIVED** (D1) |
| N7 | custody-locator check disabled | r11 slot binding | killed |
| M7 again | desk T1 before desk epoch | `ReservedIdentityTests` | killed (was a survivor) |
| M17 again | entry check drops `check_ledger` | r11 caller ledger | killed at `different staged file` (was a survivor) |

### Commands executed

- Repo, `-B`, `PYTHONPATH=tests:.`: the three new r11 cases plus `ReservedIdentityTests` (4 tests OK, 434 s);
  policy, rollback and caller-ledger cases (3 OK, 465 s); sampler case (OK, 247 s);
  `scripts/quick_suite.py --module tests.test_calibration_ledger` (95 tests PASS, 1 skipped).
- Scratch `/Volumes/JW-EXT/tmp/fable-r12d` (`git archive 062698aff`): `probe_delta.py`, `probe_c1_delta.py`
  (Pa, Pb), `mutate_delta.py` for the ten mutants above. Scripts and raw outputs are in
  `/Volumes/JW-EXT/tmp/fable-r12-probes/`.

### Limits

- Not run, as instructed: the frozen suite, `tests.test_reserve_calibration_hazard`, the p2_vpf module. So the
  reservation CLI's own tests were not re-executed against the one-line pass-through in
  `reserve_calibration_window_bracket.py`; I rely on reading it and on hosted CI.
- The machine was heavily loaded (one attempt took 55 to 220 s), so I ran no explicit-equivalent-spelling controls
  for `--session-id`, `--attempt-id` or `--output-root`. The absence of false refusals rests on every default-chain
  control admitting.
- Two of my own wait commands hit the tool's time limit while a mutant batch ran; the batches themselves finished
  normally. No background process is left. The repository was not modified.
