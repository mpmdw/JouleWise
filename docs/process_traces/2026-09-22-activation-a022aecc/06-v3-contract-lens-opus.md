# Contract-lens review: branch feat/2026-09-23-qpe01-registration-v3-nonobserver at 16900e3d

Reviewer: Opus 5.5, read-only contract lens. Worktree `/Users/edr/code/JouleWise-wt-v3-a022aecc`, clean at 16900e3d. The only file written is this report. Scratch re-derivations ran in `tempfile` directories under /tmp, the same way the branch's own tests do; nothing inside the worktree or the archives was touched.

Question asked: does the code do exactly what brief 04 and its authorities say, no more and no less? The authorities are ruling 10, synthesis 15, ruling 31 §2, and synthesis 35, which binds the interim. Brief item 8, the seat report, does not exist, so the regression ledger at the end is rebuilt from the tests and from counterfactual runs I executed.

Terms used below:
- **Main** is `origin/main` at 3b921fe1, the code before this branch.
- **Whole** is `whole_envelope_observer_cpu_s`: the collector process's own CPU plus the CPU of every child it reaped, measured over one envelope.
- **Span** is `end_stamp.monotonic_before_s − start_stamp.monotonic_before_s`, the collector's own clock window.
- **Counterfactual** means the input or code state on which a test must fail if the defect it guards were present.

---

## BLOCKER

None. Every ruled text, number, field, refusal detail and reason code that the brief makes binding is present, apart from the two deliberate text deviations listed under NIT (N1, N2). Both are authorised by a later authority or by the brief itself. Nothing the interim holds back is implemented.

---

## SHOULD-FIX

**S1. The load recorder is not inside "whole". So the registered `observer_floor.definition` is false for that component, `power_recorder_residue` is understated, and the "components sum to the whole" regression can never fail.** This defect is in the authorities, not the seat: the seat implemented brief 6(a) exactly. It must be decided before the v3 digest is pinned, because fixing the definition text changes the registration bytes.
- Evidence, collector side: `scripts/sample_quiet_predicate_evidence.py:1066` and `:1164` compute whole as `cpu_total() - envelope_cpu_start` inside the collector. `cpu_total()` (`:177-180`) is `RUSAGE_SELF + RUSAGE_CHILDREN` of the collector.
- Evidence, recorder side: the 30 s load recorder is launched by the executor, not by the collector (`joulewise/quiet_predicate_campaign.py:1433-1434`, `launch("recorder", …)`; the collector is a separate `launch("collector", …)` at `:1462`). Its `observer_cpu_s` is measured inside the recorder's own process (`quiet_predicate_campaign.py:876-883`). The seat's own regression-0 fixture says so: "recorder and collector are SIBLINGS" (`tests/test_quiet_predicate_campaign.py`, `chain_table` docstring).
- Consequences:
  - (a) `pilot_protocol_v3.json:46`, "including collector, power recorder, load recorder and census", is false for the load recorder. The same holds for the stale summary string at `quiet_predicate_campaign.py:1292`.
  - (b) `power_recorder_residue = whole − round_block − load_recorder` (`quiet_predicate_campaign.py:1245-1247`) subtracts a term that is not part of whole. The residue is therefore understated by the recorder's share. Executed: mean `load_recorder` share 0.00725 cores on 20260922-0217 and 0.00715 on 20260922-2100, against a residue of 0.11601 and 0.09986.
  - (c) The floor itself (whole ÷ span) leaves out the load recorder's roughly 0.007 cores. The true apparatus cost is about 0.183 / 0.166 cores, not 0.176 / 0.159. The stop still fires either way.
  - (d) The brief-6(d) regression "components summing to the whole within 1e-6" (`tests/test_quiet_predicate_campaign.py:3331` and the archive test at `:3371`) is true by construction, because the residue is defined as the remainder. It has no failing counterfactual.
- The magistrate's own addendum in commit 90c30e4f repeats the same decomposition ("≈ 0.116 … power recorder, ≈ 0.052 round block and 0.007 the 30 s load recorder").
- Cure options, for the magistrate:
  - Report `load_recorder` as a separate term outside whole: residue = whole − round_block, and floor = (whole + load_recorder) ÷ span.
  - Or amend the definition sentence.
  - Either way this is a registration-text change and needs authority, because the sentence is quoted verbatim from ruling 31.

**S2. The regression-5 test is circular. It passes even when the summary does not re-derive anything.**
- Test: `tests/test_quiet_predicate_campaign.py:3269`.
- Mechanism: the executor writes its own `non_observer_process_busy` list onto every envelope entry (`quiet_predicate_campaign.py`, the `envelopes.append({... NON_OBSERVER_EXCLUSION: non_observer ...})` hunk). `pilot_summary` overwrites that key only when it finds offenders (`quiet_predicate_campaign.py:1109`). Otherwise the executor's value passes through, and the test compares exactly that key.
- Executed mutation probe: I patched `pilot_summary` to receive a protocol with `non_observer_process_busy` removed, so it re-derives nothing. Output:
  - `test_regression_5_the_summary_re_derives_the_executors_own_exclusion_set -> with the summary's re-derivation DISABLED: PASSES`
  - `test_regression_3_one_exclusion_then_a_clean_envelope_never_aborts -> … fails: + [['non_observer_process_busy'], [], ['non_observer_process_busy'], []]`
- So the rule is covered by regression 3, but ruling 10 §5's regression 5 ("summary re-derived from disk equals the executor's exclusion set") is not proven by its own test.
- Latent record defect: if the in-chain verdict and the summary ever disagreed in the direction "executor found an offender, summary found none", the summary row would carry an offender list while `excluded` lacks the reason, which contradicts itself.
- Fix: the summary always writes its own derived list, and keeps the executor's under a distinct key. The test compares the summary's `excluded` and derived list against the executor's key.

**S3. At the arm check, a malformed observation or a sampler failure escapes `check()` as an uncaught exception, instead of being written as `armable: false`.**
- `check()` records a check's failure only for `(Refused, OSError, ValueError, KeyError, TypeError)` (`joulewise/evidence_night.py:924`). `machine_quiet_check` (`:776`) raises `night_gate.ProbeError`, which is a `RuntimeError` (`joulewise/night_gate.py:298`). Any `RuntimeError` or `subprocess.SubprocessError` from the sampler also passes straight through.
- Executed: `unflagged -> ESCAPES inspect(): ProbeError True malformed consumer in the non-observer observation`; `sampler raises RuntimeError -> ESCAPES inspect(): RuntimeError False top died`; `no metrics -> ESCAPES inspect(): ProbeError True non-observer observation carries no metrics`.
- It still fails closed: no arm proceeds. But `check.json` is never written, and the operator gets a traceback rather than the "reports armable false" the brief requires.
- The t0 path does handle these cases correctly (`night_gate.py:1515-1528`, wrapped into `night_probe_error`; tested at `tests/test_night_gate.py:1477`). The arm check has no matching test.

**S4. When the arm check refuses, it throws away the observation its own refusal text points to.**
- Ruling 10's detail text ends "observation in top_consumers_at_decision". At t0 the receipt's C3 row does carry that field (`night_gate.py:1528`).
- At the arm check, `machine_quiet_check` returns `top_consumers_at_decision` only on a pass. On a refusal, `check.json` holds only `{verdict, reason}`. The seat's test asserts this: `tests/test_evidence_night.py:280`, `dict(verdict="fail", reason=expected)`.
- So the arm-check refusal names a field that does not exist in the arm-check record. The text is identical as ruled, but the pointer leads nowhere. Fix: persist the consumers on the failing path too.

**S5. Three files were edited outside the brief's exhaustive write scope.**
- The files: `joulewise/arm_retry.py`, `docs/phase_2/derivation_night_runbook.md`, `tests/test_arm_retry.py`.
- The edits were forced. The ruled abort reason must be a registered driver code (`night_gate.py`, `NIGHT_DRIVER_REASON_CODES`), and `tests/test_arm_retry.py:103-105` requires `COLD_GATE_CODES` to equal gate codes plus driver codes. `tests/test_arm_retry.py:50` pins the table text in both documents.
- The content is correct and consistent across the three places. `tests.test_arm_retry`: 33 tests OK (run together with 5 other targeted tests, 38 OK in total).
- Doctrine says scope is exhaustive and must never be inferred from tests. The seat should have stopped early and asked for more scope (a NEEDS_SCOPE return). The magistrate should record a written retroactive scope grant, or reject.

**S6. The third limb of regression 4 has no test.** The limb is: "a retained custody root recorded under v2 still classifies retained in `check`".
- The branch tests only the first two limbs: a new plan pinned to v2 is refused with `night_refused_registration`, and v3 is armable (`tests/test_night_gate.py:1391`).
- The limb holds by construction today: `evidence_night.retained_roots` (`evidence_night.py:710-747`) never reads the registration digest.
- It is still a brief-mandated regression, and it should exist as a guard labelled "not defect-shaped".

**S7. Brief item 8 was not delivered, so item 7's failing-before evidence does not exist.** There is no seat report: no regression ledger, no failing-before evidence, and no record of deviations (N1, N2, S5). This review reconstructs the ledger below, with executed counterfactuals for the summary-level tests. The deviations must be recorded in the PR body or a trace note before merge.

---

## NIT

- **N1. The `observer_floor.supersedes` note is not verbatim ruling 31.** The branch says "0.176 and 0.159" (`pilot_protocol_v3.json:49`); ruling 31 §2 says "0.178 and 0.161". Ruling 31's own figure divides by the round support (its §1: "Σ whole / round support = 0.17789 / 0.16135"), which contradicts its own ruled statistic (whole ÷ span). Its §2 addendum text, brief 6(c) and the magistrate's addendum all use 0.176 / 0.159. The seat's choice is the correct one and matches the executed numbers. It is simply unrecorded (see S7).
- **N2. `non_observer_process_busy.bar_basis` is not verbatim ruling 10.** It reads "~7.7 J … at 0.3194 W … synthesis 25 withdrew the 0.3125 W figure" (`pilot_protocol_v3.json:40`), where ruling 10 has "~7.5 J … 0.3125 W". Synthesis 25 §16 withdraws 0.3125 W "everywhere", and brief 04 says a synthesis governs where it amends a ruling. So this is authorised; the arithmetic is 0.05 × 480 × 0.3194 = 7.67 J. The only record of the deviation is the string itself.
- **N3. The v3 table entry's evidence trail is uneven.** The `records` list (`night_gate.py:104-115`) cites synthesis 25, which was not adopted, but not ruling 31 or synthesis 35, even though the entry's `ruling` string names "ruling 31 reporting limbs as adjudicated by synthesis 35". The comment at `night_gate.py:60` says "rulings 10/21/31"; ruling 21 was not adopted (synthesis 25).
- **N4. The byte-equality check covers only one archive.** The test at `tests/test_quiet_predicate_campaign.py:3400` compares `joules`, `pair_sd_j` and `s_upper` only when the replay guard did not fire, so only on 20260922-2100. The 0217 re-derivation trips the existing replay guard (`REPLAY_NEVER_EVIDENCE`) on main too, so this is not introduced here. I verified the claim for 0217 separately (see V14). Suggest a test that neutralises the guard in the temporary copy, as I did.
- **N5. Stale or unlinked text.**
  - The summary's `observer_definition` (`quiet_predicate_campaign.py:1292`) still carries the pre-v3 wording, one of the three conflicting strings refuter 32 named. The brief did not demand a change, but ruling 31 asked for a v3 string.
  - The v3 `summary` list item 6 keeps v2's "whole-round observer cpu-s" wording. This is forced by the byte-for-byte rule.
  - `configs/campaigns/quiet_predicate_evidence_01/README.md:8` still says the frozen registration is v1. That was already stale before this branch, but the README is in scope and does not mention the new rule, the t0 predicate or the abort.
- **N6. The t0 bar exists twice with no link between them.** The gate constant `T0_NON_OBSERVER_SHARE_MAX = 0.5` (`night_gate.py:186`) and the registration's `t0_non_observer_share_max: 0.5` are each checked separately. No test asserts they are equal. Ruling 10 makes the gate constant the binding one, so this is only a drift guard.
- **N7. The test comment at `tests/test_quiet_predicate_campaign.py:1152`ff says "exactly the four ruled fields"**, but the asserted set has five keys (`exclusions`, `ruling`, `non_observer_process_busy`, `t0_non_observer_share_max`, `observer_floor`).
- **N8. `test_the_floor_is_the_whole_envelope_over_the_collectors_own_span` fails on main for an incidental reason.** Executed: `TypeError: unsupported operand type(s) for -: 'NoneType' and 'float'`. Its comment claims the v2 statistic would read 0.0017 and pass. It is still defect-detecting (the archive test at `:3371` fails on main on the number: `0.05309837244298898 != 0.17572`), but its stated counterfactual is not what actually happens.
- **N9. Regression 0 has no single end-to-end test.** Ruling 10 asks to "run the executor's recorder path with the chain root pid". The seat proves it in three pieces:
  - ancestry marking in `interval_metrics` (`:3048`), which passes on main because `quiet_admission` is unchanged, so it documents the mechanism rather than guarding the cure;
  - `record_covariates` forwarding the pid (`:3075`);
  - the executor passing `os.getpid()` (`:3097`).

  Together they suffice, but no one test runs recorder → `sample_interval` → marking with a chain-shaped process table.
- **N10. Scope of the arm-check path, which I could not fully verify.**
  - The predicate also runs on the `legacy_load=False` branch, `evaluate_dynamic_hard`. On main that function is called from the driver's bind loop (`scripts/run_night.py:2795`, phases pre, post and final), not from the operator's arm check. The operator's arm check is `evidence_night.check`, which the seat also wired (S3, S4).
  - On a bind-loop plan carrying an evidence payload, each hard phase would now spend 30 s. The README says pilot plans use v2 `DIAGNOSTIC_NO_PACK` admission, not the bind loop, so this is probably off the pilot path. I did not verify bind-deadline interaction.
  - There is a theoretical race in the in-chain verdict: the executor reads the journal once the envelope ends, while the summary reads it at the end of the night. A recorder row landing late could make them disagree. S2 makes that disagreement invisible to the test.

---

## Verified conformances

- **V1. v3 is v2 plus only the listed additions.** `diff pilot_protocol_v2.json pilot_protocol_v3.json` shows only: the eleventh `exclusions` entry `"non_observer_process_busy"`; the `non_observer_process_busy` object; the `observer_floor` object; the `ruling` suffix `"; cold gate 10 QPE01-DAEMON-CONTAMINATION-01 (2026-09-23) Q1(c)/Q2/Q3(a)"`, exactly as ruling 10 gives it; and `"t0_non_observer_share_max": 0.5`. `stop_branches`, `block_two` and `summary` are byte-identical to v2.
- **V2. The chain digest is unchanged, correctly.** `shasum -a 256 scripts/night_chains/quiet_predicate_evidence.zsh` gives `568a2771…51b7ea`, equal to v3's `chain_source_sha256`. `git diff origin/main HEAD --stat -- scripts/night_chains` is empty.
- **V3. Digests and the table.** v3 = `b6cb513fe4aa8b2c5557b589fae07ef4149d480cd1c831aa267ecb37c97104fa` and v2 = `2c5392401a79…79f1` (`shasum -a 256`). `night_gate.py:66-67` makes v3 current. v2 keeps its own literal (`:72`) and has `superseded_by` = v3 (`:100`). v1's `superseded_by` now points to v2 (`:94`).
- **V4. A new plan pinned to v2 refuses.** `tests.test_night_gate.EvidenceRegistrationTests.test_every_superseded_registration_is_history_and_never_armable` passes, including `night_refused_registration` with the detail "superseded by <v3>".
- **V5. Ruling 10's `non_observer_process_busy` field texts.** `statistic`, `bar_core_seconds` 30, `observer` and `abort_after_consecutive` 2 match ruling 10 verbatim, in the ruled key order. `bar_basis` is the exception (N2). Checked by a regex-and-JSON comparison against `10-coldgate-fable-ruling.md`.
- **V6. Ruling 31's `observer_floor` texts.** `statistic`, `definition` and `limitation_sentence` are verbatim. `supersedes` is the exception (N1). The ruled `role` key ("never a stop") is correctly left out under the interim.
- **V7. The held items are absent.** `grep -rn "observer_floor_tolerance|block_two_required_fields|observer_variation_above|observer_arm_symmetry" joulewise scripts configs tests` returns only the test's `assertNotIn`. `stop_branch` (`quiet_predicate_campaign.py:1061-1076`) is byte-unchanged from main, with the v2 form and cause name, and is fed the corrected floor (`:281` of the diff hunk).
- **V8. Observer marking by ancestry.** `record_covariates(protocol, night_dir, observer_pid=…)` refuses a missing or invalid pid (`quiet_predicate_campaign.py:866`) and passes the pid to `sample_interval` (`:878`). The executor launches `record --observer-pid <os.getpid()>` (`:1434`), and the CLI forwards it (`:1645`).
- **V9. The per-envelope integral.** Per non-observer identity (pid, start identity), Σ busy_cores × interval_s over rows fully inside the envelope, compared with `>= bar_core_seconds`. Each hit carries the basename, pid, start identity and core-seconds (`quiet_predicate_campaign.py`, `non_observer_busy`). v2 never emits the reason (`non_observer_rule` returns None; `tests/...:3191`).
- **V10. The t0 predicate on both branches.** It is one `sample_interval(30, observer_pid=os.getpid())` (`night_gate.py`, `production_interval_observation`). It runs on both `legacy_load` branches, only for an evidence payload (`:1515`), and C3 carries `top_consumers_at_decision` (`:1528`). The refusal detail format matches ruling 10 exactly (`:852`). Executed `test_a_busy_non_observer_process_refuses_at_t0_and_at_the_arm_check`: OK, with detail `non-observer process busy: fseventsd pid 341 at 0.600 busy cores over 30.4 s (bar 0.5); observation in top_consumers_at_decision`.
- **V11. The arm check.** `evidence_night.check` refuses with the same text and records `armable: false` (executed `tests.test_evidence_night.PrepareTests.test_the_arm_check_refuses_a_busy_non_observer_with_the_gates_own_text`: OK), subject to S3 and S4.
- **V12. The abort.** Two consecutive exclusions raise `NonObserverAbort` (`quiet_predicate_campaign.py:1542`). The refusal document's reason is `non_observer_process_busy` (`:1554`, with `write_refusal` validating the code). One exclusion followed by a clean envelope does not abort. Executed `NonObserverAbortTests`: OK.
- **V13. No automatic successor.** `non_observer_process_busy` is not in D-182's eligible set (`joulewise/arm_retry.py:210-211`, `zero_capture_successor_allowed`), and `classify_abort` puts it in the cold-gate group (`tests/test_arm_retry.py`: OK).
- **V14. The ruled floor numbers, executed by re-deriving both archives with the branch code** (`tests.test_quiet_predicate_campaign.archive_summary` into /tmp):
  - 0217: floor 0.17572, variation 0.00214. 2100: floor 0.15909, variation 0.00267. Both fall inside brief 6(d)'s 0.176 ± 0.002 / 0.159 ± 0.002 and 0.0021 ± 0.0005 / 0.0027 ± 0.0005.
  - 2100 under v2 rules: stop `{'outcome': 'no cutoff qualifies', 'causes': ['sized_pairs_above_24', 'observer_floor_above_smallest_holdable_share']}`, with `joules`, `pair_sd_j` and `s_upper` (254.23420803393725) all equal to the archive.
  - 0217: the replay guard fires on main too (executed with main's module loaded in memory: `status REPLAY_NEVER_EVIDENCE`). With `recorder_kind` set to production in a temporary copy, the branch gives `joules==archive True, pair_sd== True, s_upper== True`, and the cause `observer_floor_above_smallest_holdable_share` is present. Main and the branch differ only in `envelopes`, `observer_floor_cores`, `observer_support_s`, `observer_variation_cores` and `observer_floor_components_role`.
- **V15. A missing key is a ValueError.** A session lacking whole, `start_stamp` or `end_stamp` raises `ValueError` "absent evidence is never a pass" (`quiet_predicate_campaign.py:1239`; executed test at `:3363`: OK).
- **V16. The diagnostic re-analysis.** `python3 -B …/05-nonobserver-predicate-seat/diagnostic_reanalysis.py | diff - …/diagnostic_reanalysis.json` is IDENTICAL. 2100: 12/12 excluded, `fseventsd` 574.7–605.8 core-s, `mediaanalysisd` 528.1 in envelope 1. 0217: 0 excluded, maximum 6.3. The label is verbatim ruling 10 §4, and the observer basename set is exactly ruling 10's seven names. It is a separate script output, not a summary field.
- **V17. Tests executed.** The three new campaign classes: 19 OK in 4.3 s, with the archive tests not skipped (`-v` shows `ok`). The four gate tests, the evidence-night arm test, the v3 frozen-protocol test and `tests.test_arm_retry`: 38 OK in 8.5 s. I did not repeat the whole suite, which is running separately.

---

## Reconstructed regression ledger (brief item 7)

"Main" is the code before the change. Where I executed the counterfactual (the summary-level tests were run against main's `pilot_summary`, loaded in memory), the output is quoted. Otherwise the failure-at-main is reasoned from the diff.

| Test (file:line) | Brief / ruling regression proved | Counterfactual it fails on | Failing at main |
|---|---|---|---|
| `test_quiet_predicate_campaign.py:3048` `test_regression_0_the_chain_root_marks_the_power_sampler_the_recorder_pid_does_not` | R0, the mechanism: the chain root marks `powermetrics`, the recorder pid does not | Sibling process table (the collector's child `powermetrics`) | PASSES at main (`quiet_admission` unchanged); documents the mechanism, does not guard the cure (N9) |
| `:3067` `test_regression_0_the_recorder_refuses_to_run_without_a_chain_root` | R0: an unmarked tree is refused | `record_covariates` with no pid, or pid 0, -1, "1000", 1000.0 | Reasoned: main has no `observer_pid` parameter, so no ValueError (main would start recording) |
| `:3075` `test_regression_0_record_covariates_hands_the_pid_to_every_observation` | R0: pid forwarded to `sample_interval` | `sample_interval` called without `observer_pid` | Reasoned: TypeError on the `observer_pid=4242` keyword |
| `:3097` `test_regression_0_the_executor_launches_the_recorder_with_its_own_pid` | R0: the executor passes the chain root | Recorder argv without `--observer-pid` | Reasoned: main's argv lacks the flag |
| `:3106` `test_regression_1_a_full_core_daemon_excludes_every_envelope_it_ran_in` | R1, synthetic at archive magnitudes: 12 exclusions naming `fseventsd` (plus `mediaanalysisd` in envelope 1); the clean shape gives 0 | Twenty rows at 0.9995 cores × 30.355 s | Executed: FAILS at main (`+ ['non_observer_process_busy']]`) |
| `:3411` `test_the_contaminated_night_loses_every_envelope_under_v3` | R1 and R5 on the 2100 archive's own bytes: 12/12 excluded, retained 0 | Archived journal | Executed: FAILS at main (same diff line) |
| Diagnostic script plus committed JSON (not a unit test) | R1's "prior night → zero" under the explicit observer set | Archived journals | n/a; executed output identical (V16). No unit test pins it |
| `test_night_gate.py:1422` `test_a_busy_non_observer_process_refuses_at_t0_and_at_the_arm_check` | R2: both `legacy_load` branches, exact detail text, C3 `top_consumers_at_decision`; the same consumer marked observer is admitted | `fseventsd` at 0.6 cores, unmarked, then marked | Reasoned: main's `Probes` has no `observe_interval`; no predicate |
| `test_night_gate.py:1466` `test_the_non_observer_predicate_is_spent_only_on_an_evidence_night` | R2 scope: evidence payload only | Calibration payload | Reasoned: fixture construction fails at main |
| `test_night_gate.py:1477` `test_an_unreadable_or_unmarked_observation_is_a_probe_error_never_a_pass` | R2 fail-closed at t0 | Sampler raises; no metrics; no interval; unflagged consumer | Reasoned (as above) |
| `test_evidence_night.py:226` `test_the_arm_check_refuses_a_busy_non_observer_with_the_gates_own_text` | R2, arm-check half: `armable: false`, same text | `fseventsd` at 0.998, unmarked, then marked | Reasoned: main's `check()` has no `quiet_observer` |
| `test_quiet_predicate_campaign.py:3236` `test_regression_3_two_consecutive_exclusions_abort_the_chain_by_name` | R3: abort after envelope 2, typed `refusal.json` reason `non_observer_process_busy`, only two envelope directories | Busy envelopes {1, 2} | Reasoned: main's `exercise` has no `busy_rows`; main never aborts |
| `:3256` `test_regression_3_one_exclusion_then_a_clean_envelope_never_aborts` | R3 counterfactual: {1, 3} gives no abort, complete, excluded pattern [x, -, x, -] | Busy envelopes {1, 3} | Reasoned. Also kills a summary with re-derivation disabled (executed, S2) |
| `test_night_gate.py:1391` `test_every_superseded_registration_is_history_and_never_armable` | R4 limbs 1–2: v3 pinned, v2 `superseded_by` v3, a new v2 plan gets `night_refused_registration` | v2 bytes as the plan registration | Reasoned: main has v2 as current and armable |
| `test_quiet_predicate_campaign.py:1152` `test_regression_2_frozen_protocol_takes_v3_and_refuses_v1_and_v2` | Item 1: v3 = v2 plus only the ruled keys; same chain digest; no held items; `stop_branches` unchanged | v2 bytes into `frozen_protocol` | Reasoned: main accepts v2 |
| (missing) | R4 limb 3: a retained v2 root classifies retained in `check` | none | S6 |
| `:3269` `test_regression_5_the_summary_re_derives_the_executors_own_exclusion_set` | R5 (claimed) | Busy {1, 3} | Executed mutation: still PASSES with re-derivation disabled, so it is circular (S2) |
| `:3144` `test_regression_6_the_integral_catches_the_burst_a_median_would_admit` | R6: 8 × 1.5 cores gives 360 core-s, excluded, median < 0.10; 8 × 0.09 gives 21.6, kept | Burst rows | Executed: FAILS at main (`+ ['non_observer_process_busy']`) |
| `:3191` `test_a_v2_night_never_emits_a_reason_its_registration_does_not_carry` | Guard: the rule arrives only with v3; a half-written rule refuses | v2 protocol; malformed rules | Reasoned: `non_observer_rule` absent at main |
| `:3331` `test_the_floor_is_the_whole_envelope_over_the_collectors_own_span` | 6(a)/(b): floor = Σ whole ÷ Σ span; components; cause PRESENT | Round block 1 s, whole 105 s | Executed: FAILS at main, but by `TypeError` (N8). The components-sum limb is tautological (S1) |
| `:3352` `test_the_variation_is_the_sample_sd_of_the_per_envelope_shares` | 6(a): sample SD; uneven spans honoured | Alternating ±2 s; spans 597–608 s | Executed: FAILS at main (`KeyError: 'observer_variation_cores'`) |
| `:3363` `test_a_session_without_the_whole_envelope_cost_or_span_refuses` | 6(d): a missing key raises ValueError | Drop whole, `start_stamp` or `end_stamp` | Executed: FAILS at main (`ValueError not raised`) |
| `:3371` `test_both_archived_nights_re_derive_to_the_corrected_floor` | 6(d): 0.1757 / 0.1591, SD 0.0021 / 0.0027, cause present, byte-equal energies (2100 only, N4) | Archive bytes | Executed: FAILS at main (`0.05309837244298898 != 0.17572 within 3 places`) |
| `test_arm_retry.py` (COLD set) | Registry consistency for the new driver code | none | Guard; forced S5 |

---

## Verdict

**MERGEABLE AFTER FIXES.** The branch implements what brief 04 and the interim in synthesis 35 require:
- v3 is v2 plus exactly the ruled additions, with the chain digest correctly left unchanged and v2 kept in the table as superseded;
- the recorder is run with the chain root so the measurement's own processes are marked;
- the 30 core-second per-envelope integral names each offender;
- the 0.5-core t0 and arm-check predicate uses the exact ruled refusal text;
- the typed abort after two consecutive exclusions arranges no successor;
- the observer floor is corrected to 0.176 / 0.159 cores with variation 0.0021 / 0.0027, feeding a stop branch that keeps its v2 form. None of the held items is present.

Nothing is a blocker, but seven items should be fixed or ruled on before the digest is pinned and the branch merged:
- **S1** needs the magistrate's ruling: the registered definition and the component split wrongly place the 30 s load recorder inside the collector's accounting. Fixing it changes the registration bytes, so it must be settled before pinning.
- **S2**: make the regression-5 test real.
- **S3** and **S4**: make the arm check record `armable: false` on malformed observations, and keep the observation its refusal text points to.
- **S5**: record a scope ratification for the three forced out-of-scope files.
- **S6**: add the missing retained-root guard.
- **S7**: record the deviations (N1, N2, S5) in the PR, since the seat report was never written.
