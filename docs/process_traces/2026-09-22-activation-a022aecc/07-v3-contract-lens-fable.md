# Contract-lens review — branch `feat/2026-09-23-qpe01-registration-v3-nonobserver` at 16900e3d

Reviewer: Fable 5.1 contract lens (read-only). Reviewed 2026-09-23. Worktree `/Users/edr/code/JouleWise-wt-v3-a022aecc` (not modified). Diff read whole: `/Users/edr/.claude/jobs/7a0f14bd/tmp/v3.diff` (13 files; the 17-file `origin/main..HEAD` stat includes four files that only moved on main after the merge base 3b921fe1 and are not seat changes). Authorities read whole: brief 04, ruling 10, synthesis 15, ruling 31, synthesis 35; synthesis 25 and ruling 21 grepped for the 0.3125 W withdrawal.

Question answered: does the code do exactly what brief 04 and the binding rulings (10, 15, 31 as adjudicated by 35) say — no more, no less?

Disclosures of what I executed and where it wrote:
- Read-only Python in the worktree (re-derivations, digests) writing only to `/tmp` tempdirs the campaign code creates itself.
- The branch's regression tests, individually (58 of 58 named tests OK; one "error" in my first batch was my own mistyped test name).
- The diagnostic script; output compared with the committed JSON.
- A fail-before counterfactual: `git archive 3b921fe1` extracted to `/Users/edr/.claude/jobs/7a0f14bd/tmp/pre-3b921fe1/` (the job's scratch area, outside every worktree), with the branch's four test files and `pilot_protocol_v3.json` overlaid; log at `/Users/edr/.claude/jobs/7a0f14bd/tmp/fail-before.log`. One test hung there because the pre-change recorder has no guard and started the real 30 s sampling loop; I killed that process (pid 44278, identified by its scratch-tree working directory; nothing in the worktree was touched). Two `top -l 2 -s 30` samples it had spawned ended on their own.

Terms used below, in plain words: "observer" = the measurement's own processes (executor, collector, `sudo`, `powermetrics`, `top`, census, recorder); "non-observer" = everything else on the machine; "envelope" = one 600 s capture; "journal" = the recorder's `evidence_busy_cores.jsonl`; "core-seconds" = busy cores multiplied by seconds, summed over rows; "t0" = the night's start gate; "arm check" = the pre-arm inspection `evidence_night.check`.

---

## BLOCKER

None found. Every ruled text and number I could compare is either verbatim or deviates only where a later authority (synthesis 25, brief 04 item 6(c)) licenses the change; those deviations are listed under SHOULD-FIX so the magistrate ratifies them explicitly, since the seat report that would have recorded them was never written.

## SHOULD-FIX

**S1. The arm-check half of the predicate crashes instead of failing typed when the observation is unreadable or the sampler raises.**
`joulewise/evidence_night.py:776-798` (`machine_quiet_check`) calls `night_gate.non_observer_offender`, which raises `night_gate.ProbeError` on a malformed or unflagged observation, and calls the live sampler with no wrap. `ProbeError` derives from `RuntimeError` (`night_gate.py:298`), and `check`'s `inspect` catches only `(Refused, OSError, ValueError, KeyError, TypeError)` (`evidence_night.py:919-926`). So at the arm check these escape `inspect`, `check.json` is never written and no `armable: false` record exists — a traceback instead of the ruled verdict. The t0 half handles the same cases correctly (`night_gate.py:1516-1527` wraps the sampler in `except Exception` → `ProbeError` → `night_probe_error`, tested at `tests/test_night_gate.py:1477`). Executed:
```
$ python3 -B -c '... entry.machine_quiet_check(obs) ...'
sampler TimeoutExpired -> TimeoutExpired (would inspect() catch it? False)
ProbeError: no metrics -> ProbeError (would inspect() catch it? False)
unflagged consumer -> ProbeError (would inspect() catch it? False)
```
Direction is fail-closed (nothing is admitted), but the ruling's "same predicate, same text, `armable: false`" symmetry (ruling 10 §3(i); brief item 4) is not met on this path, and the test at `tests/test_evidence_night.py:226` covers only the busy/marked cases. Fix shape: in `machine_quiet_check`, wrap the observation call and `non_observer_offender` so `night_gate.ProbeError` and any sampler exception become `Refused("non-observer interval observation failed: …")`; add the three counterfactual cases to the arm-check test.

**S2. Three files edited outside the brief's exhaustive WRITE_SCOPE.**
`joulewise/arm_retry.py` (+1 row, edited `night_refused_not_quiet` prose), `tests/test_arm_retry.py`, `docs/phase_2/derivation_night_runbook.md` are not in brief 04's scope list. The edits are mechanically forced: adding the ruled reason `non_observer_process_busy` to `NIGHT_DRIVER_REASON_CODES` (`night_gate.py:229`) makes `tests/test_arm_retry.py:102` (`COLD_GATE_CODES == NIGHT_GATE_REASON_CODES | NIGHT_DRIVER_REASON_CODES`) and the docs cross-check (`DOCS` at `tests/test_arm_retry.py:50`) fail otherwise, and the ruling forbids the alternative (a generic `night_probe_error` reason). The rows added to the runbook are identical to the in-scope NIGHT_HANDBACK rows. Under the repo's own rule ("never infer additional scope from tests") the seat should have returned NEEDS_SCOPE; it did not, and was killed before a report could record the deviation. Ask: ratify the three files by name in the PR body (recommended — content is correct and forced), or revert and re-brief.

**S3. `observer_floor.supersedes` is not verbatim from ruling 31: 0.176 / 0.159 in place of the ruling's 0.178 / 0.161.**
`configs/campaigns/quiet_predicate_evidence_01/pilot_protocol_v3.json:55` reads "…corrected whole-envelope values 0.176 and 0.159 cores". Ruling 31 §2's field text says "0.178 and 0.161". The ruling is internally inconsistent: 0.178/0.161 are its §1 "Σ whole / round support" figures, a denominator the same ruling's §3 calls wrong ("neither is the accounting window … Ruled: the session's monotonic span"); its own statistic gives 0.17572/0.15909, its archived-summary addendum text says 0.176 [0.159], brief 04 item 6(c) says 0.176/0.159, and the magistrate's landed addenda (main 90c30e4f) say 0.176 / 0.159. The seat followed the brief and the statistic. Correct in substance; needs one dated line of ratification because the brief said "verbatim" and the numbers differ from the ruling's text.

**S4. `non_observer_process_busy.bar_basis` is not ruling 10's exact text; the rewrite is licensed but seat-authored.**
`pilot_protocol_v3.json:46` replaces ruling 10's "~7.5 J … at 0.3125 W per busy core (night 20260922-2100, C8)" with "~7.7 J … at 0.3194 W per busy core (exhibit C8, night 20260922-2100; synthesis 25 withdrew the 0.3125 W figure ruling 10 quoted)". Synthesis 25 §1 (verified by grep: "the 0.3125 W figure is withdrawn everywhere in favour of C8's 0.3194 W") licenses the number; 0.05 × 0.3194 × 480 = 7.67 J ≈ 7.7 J checks. No authority issued the replacement sentence, so the parenthetical is the seat's. Ratify the wording or shorten it.

**S5. Brief 6(d)'s byte-equality claim is verified for the 21:00 night only; for the 02:17 night the test is silently vacuous.**
`tests/test_quiet_predicate_campaign.py:3371-3409` guards the energy comparisons with `if report["status"] != campaign.REPLAY_NEVER_EVIDENCE`. Executed re-derivation with the branch code:
```
night 0217 under v2: status='REPLAY_NEVER_EVIDENCE'  joules equal: False  retained [] (archived 2)  block_two_stop None
night 2100 under v2: status='SPREAD_RECORDED'        joules equal: True  pair_sd_j 144.2791108429115 == archived  s_upper 254.23420803393725 == archived  excluded equal: True  block_two_stop causes ['sized_pairs_above_24','observer_floor_above_smallest_holdable_share'] == archived
```
The 02:17 archive predates `power.recorder_kind`, so today's replay-fidelity guard (PR #383) blanks its energies — an artefact of re-deriving old bytes with new code, not of this branch, and the test's comment says so. But the brief's regression text ("`joules`, `pair_sd_j`, `s_upper` byte-equal to the archives") is therefore only half-proven, and "cause PRESENT" for 02:17 is asserted by calling `stop_branch` directly rather than reading `block_two_stop` (which is `None` there). Fix: assert the guard state explicitly per night (`assertEqual(report["status"], REPLAY_NEVER_EVIDENCE)` for 02:17, `SPREAD_RECORDED` for 21:00) so the branch can never become vacuous unnoticed, and record in the PR body that the 02:17 byte-equality is not verifiable by this route.

**S6. `configs/campaigns/quiet_predicate_evidence_01/README.md` is in scope and untouched; it still names `pilot_protocol_v1.json` as the frozen registration (lines 8 and 66) and describes no non-observer rule, t0 share or abort.** Stale since v2, now two versions behind. A reader following it cannot rebuild the v3 rules from it.

**S7. The two halves of the predicate have different scopes.** t0 runs it only when `payload_kind == "quiet_predicate_evidence"` (`night_gate.py:1515`, tested at `tests/test_night_gate.py:1466`); the arm check runs it for every candidate unconditionally (`evidence_night.py:947`). Ruling 10 §3(i) scopes it to "v2 and v3 plans alike" (the pilot). Either scope is defensible; having both is not. Pick one and state it.

## NIT

- N1. `pilot_protocol_v3.json` is not in the canonical form v2 was (v2 bytes == `json.dumps(sort_keys=True, indent=2)+"\n"`; v3 is not, because the two new nested objects keep the rulings' key order). Harmless today (only the digest is pinned) but a future re-canonicalisation would change the digest. Executed: `v2 canonical: True / v3 canonical: False`.
- N2. The registration file's `ruling` string (`pilot_protocol_v3.json:62`, ruling 10's exact append) and the `RULED_REGISTRATIONS` v3 entry's `ruling` (`night_gate.py:105-108`, adds "ruling 31 reporting limbs as adjudicated by synthesis 35" per brief item 1) now differ; for v2 they were identical. Nothing compares them.
- N3. `t0_non_observer_share_max: 0.5` in the registration and `T0_NON_OBSERVER_SHARE_MAX = 0.5` in `night_gate.py:186` are not bound by any test; the ruling says the gate constant governs.
- N4. C3's PASS detail text (`night_gate.py:1545-1546`) still lists "agent, HID, AC, display, load, and thermal predicates" and does not name the non-observer predicate.
- N5. Executor envelope rows always carry `non_observer_process_busy: []` (`quiet_predicate_campaign.py:1515`) while summary rows for re-derived archives omit the key when empty (`:1106-1108`); `tests/…:3137` asserts the key is absent on the clean fixture. Two shapes for one meaning.
- N6. `test_regression_0_the_chain_root_marks_the_power_sampler_the_recorder_pid_does_not` (`tests/…:3048`) passes BEFORE the change (executed: `ok` in the fail-before run) — it exercises unchanged `quiet_admission.interval_metrics`; it documents the mechanism but is not defect-shaped on its own. The defect-shaped halves are `:3075` and `:3097`.
- N7. `test_regression_0_the_recorder_refuses_to_run_without_a_chain_root` (`tests/…:3067`) hangs, rather than fails, on the pre-change code (it starts the real sampler). Harmless after the change; worth a comment.
- N8. No guard that a v3 journal carries at least one `observer: true` consumer. If ancestry marking ever silently failed in production, the night would be lost (fail-closed) but every exclusion would name `powermetrics` — exactly what the 02:17 re-derivation under v3 shows: 12/12 excluded, offender `powermetrics` 65.1 core-s. A one-line refusal ("journal carries no observer-marked consumer") would name the real cause. Beyond the contract; recommendation only.
- N9. The summary's `observer_definition` string (`quiet_predicate_campaign.py:1292`) is unchanged and still differs from the two strings in `scripts/sample_quiet_predicate_evidence.py:1064,1165` (refuter 32 B2). Not asked for by the interim; noting it stays open.
- N10. `write_refusal` now validates `reason` against the registries (`quiet_predicate_campaign.py:324-339`) — a small hardening not asked for; correct.

---

## Verified conformances (one line each; file:line or executed command)

Item 1 — registration v3 and the pin
- v3 keys differing from v2 are exactly {exclusions, ruling, non_observer_process_busy, t0_non_observer_share_max, observer_floor}; keys only in v3 {non_observer_process_busy, observer_floor, t0_non_observer_share_max}. Executed JSON diff.
- `exclusions` == v2's + `["non_observer_process_busy"]` (eleventh). Executed: `exclusions ok: True`.
- `non_observer_process_busy.statistic`, `.bar_core_seconds: 30`, `.observer`, `.abort_after_consecutive: 2` verbatim from ruling 10 §3 (`pilot_protocol_v3.json:44-48`); only `bar_basis` reworded (S4).
- `t0_non_observer_share_max: 0.5` (`:102`); `busy_cores_role` unchanged `covariate_only` (`:20`).
- `ruling` string == v2's + "; cold gate 10 QPE01-DAEMON-CONTAMINATION-01 (2026-09-23) Q1(c)/Q2/Q3(a)" — ruling 10's exact append. Executed print.
- `chain_source_sha256` unchanged from v2 AND equals the current bytes of `scripts/night_chains/quiet_predicate_evidence.zsh` (executed: `568a2771… == v3 pin: True`).
- `block_two` and `stop_branches` byte-identical to v2 (executed: both `True`); no `observer_floor_tolerance`, no top-level `observer_variation`, no `block_two_required_fields` (grep of v3; asserted at `tests/…:1177-1179`).
- v3 digest `b6cb513fe4aa8b2c5557b589fae07ef4149d480cd1c831aa267ecb37c97104fa` == `night_gate.QPE01_PILOT_REGISTRATION_SHA256` (`night_gate.py:67`; executed shasum).
- v2 stays in `RULED_REGISTRATIONS` under its own literal `QPE01_PILOT_REGISTRATION_V2_SHA256` (`night_gate.py:72,97-104`) with `superseded_by` == v3 (executed `True`); v1's `superseded_by` re-pointed to v2 (`:94`).
- `armable_registration(v2)` is `None`; v3 armable (executed). New plan pinned to v2 → `night_refused_registration` with "superseded by <v3>" detail: `tests/test_night_gate.py:1391` (OK on branch; ERROR before).
- Table digest `c91f6898…` re-pinned with a dated comment: `tests/test_night_gate.py:1350-1366` (OK on branch; FAIL before).
- Retained root recorded under v2 still classifies retained: `evidence_night.retained_roots` (`evidence_night.py:710-747`) never reads the registration digest — classification depends only on terminal markers, custody path and plan span — so supersession cannot change it; `tests/test_evidence_night.py:942` OK (61 s). No NEW regression names v2 explicitly; holds by construction.
- `frozen_protocol` refuses v1 and v2 bytes, accepts v3: `tests/…:1152` (OK; FAIL before).

Item 2 — observer marking by ancestry
- `record_covariates(protocol, night_dir, observer_pid=None)` passes the pid to every `sample_interval` call (`quiet_predicate_campaign.py:850,878`) and refuses a missing/non-positive/non-int pid (`:863-865`).
- Executor launches the recorder with `--observer-pid <its own pid>` (`:1433-1434`); CLI accepts it (`:1628,1645-1646`).
- Ancestry from the chain root marks executor, collector, `powermetrics` (grandchild via the collector), recorder and `top`; recorder-only root leaves `powermetrics` unmarked: `tests/…:3048` (mechanism), `:3075` (pid handed through; ERROR before: unexpected kwarg), `:3097` (executor argv; FAIL before: `--observer-pid` absent).

Item 3 — per-envelope integral
- Identity = (pid, start_identity); Σ busy_cores × interval_s over the envelope's support rows; ≥ `bar_core_seconds` → hit with basename, pid, core-seconds (`:923-968`); exclusion appended and offenders recorded on the row (`:1104-1108`).
- Support join is the registration's existing one (intervals fully inside the envelope, `:971-979`), i.e. "journal rows joined to the envelope" as the registration's summary line 7 defines it; one row stricter than the ruling's own [scheduled, scheduled+600) join, same twelve exclusions (diagnostic docstring; executed: production names `fseventsd` 575.6 core-s in envelope 1 vs the ruling's 605.8).
- Reads only the `observer` flag to skip consumers (`:953-954`), never the total.
- v2 (no rule) never emits the reason; a half-written rule refuses: `tests/…:3191` (ERROR before).
- Executed on the 21:00 archive under v3: 12/12 excluded; offenders `{fseventsd, mediaanalysisd, powermetrics}` (the last because the archived rows are unmarked — expected and documented at `tests/…:3411`).
- Diagnostic re-analysis: re-run output identical to the committed JSON (executed `diff` → "IDENTICAL"); 21:00 twelve exclusions all naming `fseventsd` 574.7–605.8 core-s, envelope 1 also `mediaanalysisd` 528.1; 02:17 zero exclusions, largest 6.3 — ruling 10 §4's expectations exactly; label text verbatim; observer basename set stated; lives under the trace dir, never a summary field.

Item 4 — t0 and arm-check predicate
- `production_interval_observation` = one `sample_interval(30, observer_pid=os.getpid())` (`night_gate.py:792-806`; constant `:187`).
- `_check_machine` runs it after the thermal probe, OUTSIDE the `if legacy_load:` block, so both branches reach it (`:1442-1467` legacy block closes; predicate at `:1503-1541`); tested on both `evaluate_night` and `evaluate_dynamic_hard`: `tests/test_night_gate.py:1422` (ERROR before: `Probes` had no `observe_interval`).
- Refusal reason `night_refused_not_quiet`; detail built by `non_observer_refusal_detail` (`:852-859`) — format matches ruling 10's text character for character ("bar 0.5" from the constant); test asserts the literal string at `tests/test_night_gate.py:1441-1443` and `tests/test_evidence_night.py:244-245`.
- C3 receipt row carries `top_consumers_at_decision` (`:1528`; key already in `_QUIET_RECEIPT_KEYS` `:279-283`); same consumer marked `observer: true` is admitted (`tests/…:1447-1454`).
- Malformed / sampler-raising / unflagged observation at t0 → `night_probe_error`, never a pass: `tests/test_night_gate.py:1477` (ERROR before).
- Predicate spent only on evidence payloads at t0: `tests/…:1466`.
- Arm check: `machine_quiet_check` (`evidence_night.py:776-798`) raises `Refused` with the same detail; `check` records `armable: false`, `rehearsal_ready: false`, `checks.machine_quiet == {verdict: fail, reason: <text>}` and surfaces the text itself (`:959`): `tests/test_evidence_night.py:226` (ERROR before: no `quiet_observer` kwarg). Note the arm check does not call `night_gate.evaluate_*` (grep: only `scripts/run_night.py:2280-2795,3044-3060` do), so the 30 s cost is paid once per path, not twice.

Item 5 — abort
- Counter `consecutive_non_observer` resets on a clean envelope (`:1539`); at `abort_after_consecutive` raises `NonObserverAbort` (`:1540-1547`), a `ValueError` subclass so the existing handler catches it (`:1550-1554`); `write_refusal(..., reason="non_observer_process_busy")` (`:1592-1593`, `:324-339`).
- Two consecutive → rc 2, outcome refused, 2 envelopes attempted, `refusal.json` reason `non_observer_process_busy`, verdict REFUSED, no third envelope: `tests/…:3236` (FAIL before: 0 != 2).
- One exclusion then clean → no abort, all envelopes attempted, excluded pattern [X, [], X, []]: `tests/…:3256` (FAIL before).
- Summary re-derived from disk equals the executor's set: `tests/…:3269` (ERROR before: KeyError).
- No successor arranged anywhere (grep of `execute` and `write_refusal`: none). Reason code registered in `NIGHT_DRIVER_REASON_CODES` (`night_gate.py:229`), `COLD_GATE_CODES`, NIGHT_HANDBACK.md and the runbook with the same row text; `classify_abort` → cold_gate (`tests/test_arm_retry.py:102`, OK; FAIL before).

Item 6 — observer floor interim (synthesis 35)
- Statistic Σ `whole_envelope_observer_cpu_s` / Σ span, span = `end_stamp.monotonic_before_s − start_stamp.monotonic_before_s` (`:982-994`, `:1194`, `:1236-1251`).
- Missing whole or span → `ValueError("… absent evidence is never a pass")` (`:1240-1241`); `tests/…:3363` (FAIL before: not raised).
- Components per envelope `round_block` = `observer_cpu_s`, `load_recorder` = `recorder_observer_cpu_s`, `power_recorder_residue` = whole − both, labelled "unattributed by PID at this revision" (`:1243-1248`, `:1280-1283`).
- `observer_variation_cores` = `statistics.stdev` of per-envelope shares (`:1252`, `:1279`); REPORTED only — `stop_branch` signature and body unchanged from v2 (`:1061-1078`, not in the diff), still fed `observer_floor` (`:1257`).
- Executed on both archives (branch code, v2 protocol): floors 0.17571586… / 0.15909366… (brief: 0.176 ± 0.002 / 0.159 ± 0.002 ✓); variation 0.0021403… / 0.0026738… (brief: 0.0021 ± 0.0005 / 0.0027 ± 0.0005 ✓); components sum to the whole within 1.4e-14 (brief: 1e-6 ✓); residue share 0.10–0.12 cores, load recorder 0.0073 (synthesis 35's figures ✓); cause PRESENT on the 21:00 `block_two_stop` and via `stop_branch` for 02:17 (S5).
- `observer_floor.statistic`, `.definition`, `.limitation_sentence` verbatim from ruling 31 §2 (`pilot_protocol_v3.json:51,52,56`); `.supersedes` verbatim except the two numbers (S3); ruling 31's `role` line ("never a stop") correctly OMITTED because the interim keeps the stop; `.components` and `.variation` strings are seat-authored descriptors licensed by synthesis 35 §3 ("names its components … reports the per-envelope variation").
- Item 6(e) addenda: not the seat's; landed on main at 90c30e4f (not reviewed here).

Item 7 — tests: all named regressions present and green on the branch (executed individually; 58/58 OK); the caller's full-module run was not repeated. Fail-before evidence: 20 of 21 tests I ran against the pre-change code do not pass (14 failures, 16 errors including subtests); the one that passes is N6.

Item 8 — scope: no other unasked additions found beyond S2 (files) and N10 (`write_refusal` validation). Nothing asked for is missing except the README (S6), the seat report (known), and the arm-check error path (S1).

---

## Reconstructed regression ledger (brief item 7 / ruling 10 §5 / brief 6(d))

| test (file:line) | brief / ruling regression it proves | counterfactual it fails on (executed before-state) |
|---|---|---|
| `NonObserverProcessTests.test_regression_0_the_chain_root_marks_the_power_sampler_the_recorder_pid_does_not` (tqpc:3048) | reg. 0 mechanism: chain-root ancestry marks `powermetrics` (grandchild via collector); recorder-only root does not | none — passes before (unchanged `interval_metrics`); documents the defect shape only |
| `…test_regression_0_the_recorder_refuses_to_run_without_a_chain_root` (tqpc:3067) | reg. 0 cure is mandatory: no pid → ValueError | pre-change: hangs (real sampler starts); not run in the counterfactual |
| `…test_regression_0_record_covariates_hands_the_pid_to_every_observation` (tqpc:3075) | reg. 0: `record_covariates` → `sample_interval(interval, observer_pid=chain root)` | ERROR before: `unexpected keyword argument 'observer_pid'` |
| `…test_regression_0_the_executor_launches_the_recorder_with_its_own_pid` (tqpc:3097) | reg. 0: executor passes its pid via `--observer-pid` | FAIL before: `'--observer-pid' not found in [...]` |
| `…test_regression_1_a_full_core_daemon_excludes_every_envelope_it_ran_in` (tqpc:3106) | reg. 1 (synthetic, archive magnitudes): 12× `fseventsd` ≈ 606 core-s excluded, `mediaanalysisd` 528 in env 1; clean shape 6.4 core-s → zero | FAIL before: `[[], [], …] != [['non_observer_process_busy'], …]` |
| `ObserverFloorTests.test_the_contaminated_night_loses_every_envelope_under_v3` (tqpc:3411) | reg. 1 on the night's own bytes: 12/12 excluded; clean night names only the unmarked sampler | FAIL before (same shape) |
| `…test_regression_6_the_integral_catches_the_burst_a_median_would_admit` (tqpc:3144) | reg. 6: 8×1.5 cores then 12×0 → 360 core-s excluded with median < 0.10; 8×0.09 → 21.6, kept | FAIL before: `[] != ['non_observer_process_busy']` |
| `…test_a_v2_night_never_emits_a_reason_its_registration_does_not_carry` (tqpc:3191) | v2 byte-pinned exclusions: rule absent → None; half-written rule → ValueError | ERROR before: no `non_observer_rule` |
| `NonObserverAbortTests.test_regression_3_two_consecutive_exclusions_abort_the_chain_by_name` (tqpc:3236) | reg. 3 / brief 5: typed refusal `non_observer_process_busy` after envelope 2, no successor | FAIL before: `0 != 2` (rc) |
| `…test_regression_3_one_exclusion_then_a_clean_envelope_never_aborts` (tqpc:3256) | reg. 3 counterfactual: X, clean, X, clean → complete, no refusal | FAIL before: excluded lists all empty |
| `…test_regression_5_the_summary_re_derives_the_executors_own_exclusion_set` (tqpc:3269) | reg. 5: executor set == disk re-derivation | ERROR before: `KeyError 'non_observer_process_busy'` |
| `StartDriftCadenceTests.test_regression_2_frozen_protocol_takes_v3_and_refuses_v1_and_v2` (tqpc:1152) | brief 1: v3 = v2 + exactly five ruled keys; chain digest unchanged; v1/v2 refused; held items absent | FAIL before: PROTOCOL_PATH still v2 |
| `EvidenceRegistrationTests.test_every_superseded_registration_is_history_and_never_armable` (tng:1391) | reg. 4: v2 pinned new plan → `night_refused_registration` "superseded by <v3>"; v3 armable | ERROR before: no `QPE01_PILOT_REGISTRATION_V2_SHA256` |
| `…test_ruled_registration_serialization_requires_dated_ruling_amendment` (tng:1350) | reg. 4: table digest re-pinned with dated amendment | FAIL before: digest differs |
| `…test_a_busy_non_observer_process_refuses_at_t0_and_at_the_arm_check` (tng:1422) | reg. 2 (t0, both `legacy_load` branches): 0.6 cores unmarked → refusal with the exact text + `top_consumers_at_decision`; marked → admitted | ERROR before: `Probes` has no `observe_interval` |
| `…test_the_non_observer_predicate_is_spent_only_on_an_evidence_night` (tng:1466) | scope: no sampler call on non-evidence payloads | ERROR before (same) |
| `…test_an_unreadable_or_unmarked_observation_is_a_probe_error_never_a_pass` (tng:1477) | absent evidence never a pass at t0 (sampler raises / no metrics / no interval / unflagged consumer) | ERROR before (same) |
| `PrepareTests.test_the_arm_check_refuses_a_busy_non_observer_with_the_gates_own_text` (ten:226) | reg. 2 arm half / brief 4: `armable: false`, same text; marked → pass with bar 0.5 | ERROR before: no `quiet_observer` kwarg |
| `ObserverFloorTests.test_the_floor_is_the_whole_envelope_over_the_collectors_own_span` (tqpc:3331) | brief 6(a)/(b): 105 s over 600 s → 0.175, cause PRESENT, components 1 / 0.2 / 103.8 sum to whole | ERROR before: `envelope_span_s` None |
| `…test_the_variation_is_the_sample_sd_of_the_per_envelope_shares` (tqpc:3352) | brief 6(a): sample SD; uneven spans honoured | ERROR before: no `observer_variation_cores` |
| `…test_a_session_without_the_whole_envelope_cost_or_span_refuses` (tqpc:3363) | brief 6(d): missing whole / start_stamp / end_stamp → ValueError | FAIL before: not raised |
| `…test_both_archived_nights_re_derive_to_the_corrected_floor` (tqpc:3371) | brief 6(d): 0.176 / 0.159 (±0.0005 asserted), variation 0.0021 / 0.0027, components sum, cause present, energies byte-equal (21:00 only — S5) | FAIL before: `0.0531 != 0.17572`, `0.0528 != 0.15909` |
| `ArmRetryTests.test_every_cold_assignment_is_explicit` (tar:102) | reason-code registry consistency (forced S2 edits) | FAIL before: `'non_observer_process_busy'` missing |

(tqpc = tests/test_quiet_predicate_campaign.py; tng = tests/test_night_gate.py; ten = tests/test_evidence_night.py; tar = tests/test_arm_retry.py.)

Not verifiable by me: item 6(e) addenda (magistrate's, on main); the quick tier (brief 7, "if documented") — not run, not checked; the seat's own module-suite runs (report never written; the caller's full run covers this).

---

## Verdict

**MERGEABLE AFTER FIXES.** The branch implements brief 04 items 1–6 as the binding interim (synthesis 35) requires: v3 is v2 plus exactly the five ruled keys with the chain digest unchanged and every held item absent; the observer tree is marked by ancestry from the chain root; the per-envelope integral, the 0.5-core t0/arm predicate with ruling 10's exact text, the two-consecutive abort with the ruled typed reason and no successor, and the corrected whole-envelope floor with components and variation all reproduce the authorities' numbers on both archives (0.17572 / 0.15909, sd 0.00214 / 0.00267, 21:00 energies byte-equal) and the diagnostic re-analysis matches ruling 10 §4 exactly. What must land before merge: S1 (the arm-check half must fail typed, not crash, on an unreadable observation — a few lines plus three test cases), S6 (README in scope, two versions stale), and S5 (make the 02:17 vacuity explicit). What needs the magistrate's written ratification rather than code: S2 (three files outside WRITE_SCOPE, mechanically forced), S3 (0.176/0.159 over ruling 31's inconsistent 0.178/0.161), S4 (seat-authored `bar_basis` wording under synthesis 25), S7 (pick one scope for the predicate). No ruled text or number is wrong in the code; nothing measured has been touched.
