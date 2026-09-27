# BFG-S S2 round 1: Opus contract lens on `4ea4b26b`

Reviewer: Claude Opus 5.5, contract lens, one foreground session, no subagents, no background tasks. I edited no repository file. Scratch lives under `/tmp/s2lens/`: probe scripts, the base module copy `base_qpc.py` from `git show 1417c0c4:joulewise/quiet_predicate_campaign.py`, and a `git archive 4ea4b26b` overlay in `/tmp/s2lens/mut/` for the mutation runs.

I read the lens charge, the seat brief, the seat report, Final texts v1.1 §4 (texts 1, 5, 6, 15, §E, §F), AD2 §5 amendments 20 and 28, ERR §2 to §6 (amendments 30, 32, 33 and 34), and Q35 §1, §3 (B-1 to B-6, J-1), §5 and §6, plus Flag 4 of the earlier QPE ruling. I did not read RUN_STATE, TASK_QUEUE, CLAUDE*, AGENTS, the decision log, or any memory or skill file.

## Verdict

- **BLOCKER:** 0
- **SHOULD-FIX:** 3
- **NIT:** 6

Every ruled sentence has implementing code. Every ruled test row has at least one test that goes through the real call site the ruling names: `collect`, `pilot_summary`, `summarize` or `execute`. The standing constraints hold:
- the excluded paths are byte-identical;
- the registration digest has not moved;
- the exclusion-reason set is unchanged;
- `CustodyFailure` is never caught or turned into a status;
- the collector has no new exit path.

The three SHOULD-FIX items are:
- **S-1:** code that goes beyond the ruled texts and weakens an existing refusal.
- **S-2:** an "as today" clause that the new code only partly honours.
- **S-3:** a load-bearing custody condition that no test pins.

## 1. Executed evidence

```
$ git -C …/JouleWise-wt-s2lens-92472459 rev-parse HEAD
4ea4b26b18f0e6bb6e3463c194ba6e8dc482c5fd

$ git diff --stat 1417c0c4 4ea4b26b -- joulewise/battery_float.py joulewise/evidence_night.py joulewise/night_gate.py configs/campaigns/quiet_predicate_evidence_01 scripts/night_chains
(empty)

$ git diff --name-only 1417c0c4 4ea4b26b | grep -v -x <the eight S2 WRITE_SCOPE paths>
(empty)

registration: protocol configs/campaigns/quiet_predicate_evidence_01/pilot_protocol_v3.json 69321c693b3370b949b0a4a1b8548e35dd081a36165ba8f6799a387c2d813616
              pinned   69321c693b3370b949b0a4a1b8548e35dd081a36165ba8f6799a387c2d813616
exclusions: ['census_not_clean_or_unknown', 'ac_not_AC_Power_or_probe_error', 'CPU_Speed_Limit_below_100_or_thermal_probe_error',
 'clock_anchor_unresolved', 'incomplete_interior_support', 'collect_error', 'cleanup_unproven', 'start_drift',
 'network_time_slew_attested', 'network_time_unattested', 'non_observer_process_busy']
(new code emits only collect_error and incomplete_interior_support; no reason literal is added)

$ python3 -m unittest <S2 classes> tests.test_battery_float_sweep <3 text-15 rows> <no-skipped-state row>
Ran 37 tests in 10.164s
OK
$ python3 -m unittest tests.test_quiet_predicate_campaign
Ran 184 tests in 26.284s
OK
$ python3 -m unittest tests.test_sample_quiet_predicate_evidence tests.test_night_kinds tests.test_battery_float_sweep
Ran 118 tests in 108.320s
OK
```

The pilot-night archives exist on this machine (`~/night-archive/qpe01-pilot-n1-20260922-{0217,2100}-harvest-20260922/night`), so the historical-night row ran here rather than being skipped.

Mutation runs, each done in the `/tmp` overlay by replacing exactly one production text:

| Mutant | Result |
|---|---|
| m1: X-1 handler returns normally (`outcome, error = "refused", …`) | `FAILED (failures=1)`, X-1 RED |
| m2: guard widened to `RuntimeError`, custody handler removed | `FAILED (failures=1)`, X-1 RED |
| m5: excuse taken before `authenticate_quiet_session` | `FAILED (failures=7, errors=2)`: T6-f, g/h/i, j/k, q/s, r, v, 32(a) |
| m7: collector passes `time.monotonic_ns` instead of the clock | `FAILED (failures=7)`: every T5 clock row |
| **m3: carve-out ignores `raw/round-*` directories** | **`OK`, survives** |
| **m4: carve-out ignores `rounds.jsonl`** | **`OK`, survives** |

## 2. Clause table

Line numbers refer to the candidate. File abbreviations:
- `SQ` = `scripts/sample_quiet_predicate_evidence.py`
- `QPC` = `joulewise/quiet_predicate_campaign.py`
- `TSQ` = `tests/test_sample_quiet_predicate_evidence.py`, class `BatteryCollectorTests`
- `TQPC` = `tests/test_quiet_predicate_campaign.py`, classes `BatteryFloatSummaryTests`, `BatteryFloatExecuteTests` and `BatteryFloatInterruptedCollectorTests`

| Ruled sentence | Implementing lines | Pinning test(s) | Verdict |
|---|---|---|---|
| T5 "One pair per envelope"; pre in `collect` after the `session` dict, before `envelope_cpu_start` | SQ:1081-1092 | `test_t5_capture_pair_clock_and_two_row_witness` | exact |
| T5 pre present in **both** first writes | SQ:1092 (before the refusal write at :1109 and the capture write at :1112) | `test_t5_pre_is_in_first_writes_and_failed_probe_does_not_abort` | exact |
| T5 post on the refusal path after `error_class`, before the write | SQ:1105-1109 | `test_t5_refusal_has_both_reads_and_no_count`, `…first_writes…` (refusal leg) | exact |
| T5 post on the capture path in `finally`, after `whole_envelope_observer_cpu_s`, before the final write | SQ:1191-1194 | capture row; `test_t5_scripted_clock…` (capture) | exact |
| T5 raw files `raw/battery_float.{pre,post}.ioreg` digested in each row's `raw.sha256` | SQ:1082, 1089; SQ:1229-1231 (parent == raw) | capture row asserts both digests on `rows[0]`; `test_t5_attestation_rewrite_does_not_repair…` (disagreement → `CustodyFailure`) | exact |
| T5 the collector's clock goes to `observe(monotonic_ns=…)` (AD2 20: `lambda: monotonic_ns_from_s(clock.monotonic())`, the same `Clock` whose `stamp()` writes the stamps; never `time.monotonic_ns`) | SQ:1084 | `test_t5_scripted_clock_conversion_on_capture_and_refusal` (m7 RED) | exact |
| AD2 20 `NETWORK_TIME_REFUSAL == QUIET_REFUSAL_ERROR_CLASS` | SQ:86 | scripted-clock and capture rows | exact |
| T5 a failing probe is recorded and the collector continues; no new exit path | `observe` catches every `Exception`; `battery_read` adds no raise and no return | `…failed_probe_does_not_abort` (probe `OSError`: two rows, `error` None, `evidence_missing`) | exact |
| T5 "never keys on a `session.json` digest" | S0 helper (unchanged) | `…attestation_rewrite…` (`record_attestation`, then `pass`) | exact |
| §F T5 "post-missing on any path is `evidence_missing`" | helper | `test_t5_missing_post_on_both_collector_paths_is_evidence_missing` (edits real `collect` output) | exact |
| §F T5 / text 16: an injected 2 s probe shifts only `start_drift_s` | SQ:1092 before `clock.stamp()` | `test_t5_two_second_pre_probe_moves_start_drift_only` | exact |
| 33 `journal_rows = len(rows)` immediately before the finalization rewrite; only on the final write | SQ:1234-1236 | `test_t5_capture…` (a); `test_t5_partial_sampler_keeps_finalized_row_count` (b); `test_t5_refusal_has_both_reads_and_no_count` (c); first-write key absence in `…first_writes…` | exact |
| 34 atomic `write_json` (temp file in the same directory, `fsync`, `os.replace`) and atomic finalization journal; appends stay appends | SQ:142-159, 1235; the append at SQ:~1167 is unchanged | `test_t5_atomic_replace_failure_preserves_previous_json_and_journal`, `test_t5_atomic_final_journal_failure_uses_collect` | exact; the temp-name clause is pinned only indirectly (N-4) |
| 32(1) / 35 item 1: executor witness and no `session.json`, no `rounds.jsonl` (`lstat`), no `raw/round-*` directory → `collect_error`, no authentication | QPC:1150-1168 | `test_amendment32_empty_crash_has_collect_error_without_custody` (positive only) | **partial**: the row is not "as today" (S-2); the two negative conditions are unpinned (S-3) |
| 32(2) / 35 item 2: authenticate before the summary's own read and before any decision; custody propagates | QPC:1169, before the booking at :1178 and the reads at :1221/:1271 | T6-h in `test_t6_g_h_i…`; 32(a) and (b) rows (m5 RED) | exact |
| 32 `summarize` enumerates the union of the parents of `session.json` and `rounds.jsonl`, authenticating each before its journal is read | SQ:1493-1504 | 32(b) via `harness.summarize`; `test_t6_m_summarize_has_no_executor_excuse` | exact |
| 32 T6 (a) `{` session raises, no summary | helper and QPC:1169 | `test_amendment32_a_unparseable_session_raises` (both entry points) | exact |
| 32 T6 (b) deleted completed journal raises through both | helper | `test_amendment32_b_missing_completed_journal_raises` | exact |
| 32 T6 (c) historical pilot fixture → `evidence_missing` | QPC:1470-1486 | `test_t6_historical_pilot_nights_re_summarize_as_evidence_missing` (skipUnless the archives exist; ran here) | exact; skips in CI (N-4) |
| 32 T6 (d) exit 1 with only `raw/` → `collect_error`, summary written | QPC:1155-1168 | empty-crash row (its `raw/` also holds a post raw file, so the input differs from the ruled one; N-4) | exact (input drift) |
| 32 T6 (e) | superseded by T6-f (Q35 §5) | — | n/a |
| Text 6: blank `retained`, pairs, sizing, spreads, `joules`/`combined_joules`/`interior`; status and `evidence_status`, confounded first | QPC:1470-1486 | T6-g/i field loop; `test_t6_confounded_precedes_evidence_missing` | exact |
| Text 6: `battery_float_envelopes` (index, status, reasons, digests) | QPC:1171-1177, 1400 | T6-f, g/i, p, t | exact |
| Text 6: `summary.md` states it | QPC:1488-1501 | T6-f and T6-p check the sentences | exact on the battery branch; the replay branch omits the sentences (N-3) |
| Text 6: registration digest unchanged | — | `test_t6_f_first_write_is_excused` (both pins) | exact |
| Text 6: interaction with the existing replay refusal | QPC:1440 `if replay_recorders and not battery_statuses` | none | **overreach** (S-1) |
| 35 definitions: completed, refusal, unfinished, first-write, executor witness, `<code>` | QPC:1151-1152, 1247-1252, 1263 | T6-i types (`0`, absent, `True`, `"124"`, `1.0`); T6-q sub-row; T6-r five shapes | exact |
| 35 item 3(a) completed pass summarized as today, stays in the floor | fall-through | `test_t6_t_u_completed_timeout_keeps_observer_floor_guard` (T6-t) | exact |
| 35 item 3(b) refusal record, pass, witness → refused envelope; error text | QPC:1254-1256 | `test_t6_p_refusal_pair_routes_only_with_witness` | exact |
| 35 item 3(c) other pass (refusal without witness) → today's floor `ValueError` | fall-through | T6-p sub-row (exit 0); T6-u | exact |
| 35 item 4 excuse (all four conditions), disposition `excluded_collect_error`, error text | QPC:1257-1259 | T6-f, l, n, o, v | exact |
| 35 item 5 every other non-pass blanks; unfinished or refusal records also routed with `collector record has no end_stamp, collector_exit <code>` | QPC:1260-1264 | T6-g, i, j, k, q, r | exact |
| 35 item 6 routing: booked reasons plus `incomplete_interior_support`, `error`, null energies, journal not read, replay check still runs | QPC:1265-1270 (the replay check at :1236-1246 precedes it) | T6-f, l (four journal variants), p | exact |
| 35 Record: rows carry `collector_exit` and `disposition`; `summary.md` names excused and refused envelopes | QPC:1171-1177, 1493-1498, 1515-1521 | T6-f, p | exact (N-3 for the replay branch) |
| 35 `summarize` unchanged: raises naming the directory, status and reasons | SQ:1500-1501 | T6-m (`'envelope-05.*battery_float_evidence_missing'`) | exact |
| Q35 T6-n: real `collect` in a child, blocking `finish()`, real `cleanup_groups` | — | `test_t6_n_real_collect_killed_after_first_provisional_row`; the child's SIGTERM→`KeyboardInterrupt` mirrors production (SQ:1711) | exact |
| Q35 T6-o / T6-s / T6-u / T6-v | — | `test_t6_o…`, `test_t6_q_s…`, `test_t6_t_u…`, `test_t6_v…` | exact |
| Q35 §6 Flag 3 (earlier Flag 4): filter `abort` rows from fixtures | `archive_summary` in TQPC | used by the historical rows | exact |
| X-1: guard not widened; custody printed with `flush=True` and re-raised bare; the handler writes nothing | QPC:1773-1775 | `test_x1_custody_is_printed_and_reraised_without_refusal_documents` (m1 and m2 RED) | exact |
| Text 15 S2 clause: QPE `battery_brackets=True` in the same PR; QPE armable by the fence only with the flip; derivation unchanged; unknown kind not armable | `joulewise/night_kinds.py:66` | `test_qpe_candidate_is_armable_by_battery_fence_after_s2` (RED with the flag patched back); `test_battery_bracket_flags_open_qpe_without_changing_derivation`; `test_unknown_payload_kind_has_a_failed_battery_brackets_check`; `test_battery_brackets_has_no_skipped_state_or_exemption` | exact |
| Text 1 / brief item 6: sweep `OBSERVE_CALLERS` rows; `observe(phase=…)` literals in `PHASES` | `tests/test_battery_float_sweep.py:74-76`; SQ:1085/1087 use literals | `test_every_production_observe_phase_is_registered` | exact (see N-6 for the lead's bench line) |

## 3. Findings

### S-1 (SHOULD-FIX). The battery status removes the night's replay record, so `execute` no longer refuses a night whose sessions say `replay`

`QPC:1440` changes `if replay_recorders:` to `if replay_recorders and not battery_statuses:`. When any battery non-pass blanks the night, the report no longer carries `replay_recorder_envelopes` or `replay_recorder_reason`, and its status is not `REPLAY_NEVER_EVIDENCE`.

`execute` (QPC:1762-1772) makes both of its decisions from exactly those two keys:
- it refuses at the harvest boundary (outcome `refused`, rc 2) when the status is `REPLAY_NEVER_EVIDENCE`;
- its outcome document says `recorder_kind: replay` when `replay_recorder_envelopes` is non-empty.

In the case the existing code calls "the disagreement that matters, and it wins" (sessions say `replay`, the executor's environment does not), a battery non-pass now leaves the night unrefused. Its `evidence_outcome.json` then says `recorder_kind` is the production recorder.

Text 6 does rule that the status becomes the battery status, and text 6's historical sentence requires the 02:17 night, which trips the replay guard, to read `BATTERY_FLOAT_EVIDENCE_MISSING`. No ruled text removes the replay record or the executor's replay refusal.

Probe `/tmp/s2lens/probes.py` P1: twelve replay sessions, envelope 5 a first-write record with exit 0:
```
with env5 first-write exit 0 -> status: BATTERY_FLOAT_EVIDENCE_MISSING | replay_recorder_envelopes in report: False
```
The control, the same replay night with every pair passing, gives `status: REPLAY_NEVER_EVIDENCE | replay_recorder_envelopes in report: True`. No test covers replay together with a battery non-pass.

No energy number escapes, because the battery branch blanks the same fields. The damage is to the night's record, and to any gate that counts "a real QPE night under S2" (text 5's stop-rule precondition).

**Closure:**
1. In `pilot_summary`, keep the battery status precedence. Whenever `replay_recorders` is non-empty, also put `replay_recorder_envelopes` and `replay_recorder_reason` into the report, whatever the battery status.
2. In `execute`, refuse on `report.get("replay_recorder_envelopes")` as well as on the replay status, so that the outcome is `refused`, rc 2, and `recorder_kind` is `replay`.
3. Add a row through `execute`: sessions say `replay`, the environment is unset, envelope 5 is a non-excused battery non-pass. Expected: status `BATTERY_FLOAT_EVIDENCE_MISSING`, outcome `refused`, `recorder_kind` `replay`, rc 2. It must be RED on `4ea4b26b`.

If the magistrate prefers the replay status to win, that choice contradicts text 6's historical sentence and needs a ruling.

### S-2 (SHOULD-FIX). The amendment 32 step (1) row is not "excluded `collect_error` as today"

Amendment 32(1), restated unchanged as amendment 35 item 1, says the no-record envelope "is excluded `collect_error` as today, without authentication". Item 6 defines the booked reasons as "`collect_error`, and `cleanup_unproven` or the non-observer reason where they apply".

The candidate's carve-out (QPC:1165-1168) takes its `continue` before the booking block at QPC:1178-1212. So its row:
- hard-codes `["collect_error", "incomplete_interior_support"]` and drops `cleanup_unproven` and `non_observer_process_busy`;
- carries no `busy_cores` covariates;
- skips `require_observer_marked(support)`, the fail-closed check on the recorder journal that today's code runs for every envelope.

Probe P2 (exit 124, `cleanup_proven: False`, empty `raw/`), candidate against base:
```
candidate excluded: ['collect_error', 'incomplete_interior_support'] | keys has busy_cores: False | error: collector left no record, collector_exit 124
base excluded: ['collect_error', 'cleanup_unproven', 'incomplete_interior_support'] | keys has busy_cores: True | error: [Errno 2] No such file or directory: …/envelope-05/session.json
```

**Closure:**
1. Factor the booking block (`collect_error`, `cleanup_unproven`, the non-observer rule including `require_observer_marked`, and the busy-core enrichment) into one helper. Call it on the carve-out path, and on the main path after authentication.
2. Build the carve-out row from that helper's `excluded` plus `incomplete_interior_support`.
3. Extend `test_amendment32_empty_crash_has_collect_error_without_custody` with `cleanup: {cleanup_proven: False}` and assert `cleanup_unproven` is in the row's `excluded`. It must be RED on `4ea4b26b`.

Authentication must stay the first decision for every envelope that is not carved out.

### S-3 (SHOULD-FIX). Two of the carve-out's three conditions are unpinned, and both protect "custody is never an exclusion"

`QPC:1164` requires no `session.json`, no `rounds.jsonl` (by `lstat`) and no `raw/round-*` directory. Mutants m3 (ignore round directories) and m4 (ignore `rounds.jsonl`) both leave every S2 test green (`OK`, section 1).

Under either mutant, an envelope with exit ≠ 0, no `session.json`, and a surviving journal or round directory would be excluded instead of raising amendment 29's `CustodyUnreadable`. That is exactly the custody-to-exclusion conversion the class rule forbids.

The candidate itself behaves correctly (probe `/tmp/s2lens/p5.py`):
```
journal_only -> CustodyUnreadable session.json unreadable: missing | summary.json exists: False
round_dir_only -> CustodyUnreadable session.json unreadable: missing | summary.json exists: False
```

**Closure:** add two rows through `pilot_summary`, each with exit 1 and `session.json` deleted:
- (i) `rounds.jsonl` kept;
- (ii) `rounds.jsonl` deleted and `raw/round-0001/` present.

Each expects `CustodyFailure` and no `summary.json`, and each must be RED under m4 and m3 respectively. Optionally add a dangling-symlink `session.json` row to pin `lstat` against `exists()`.

### N-1 (NIT; tension between ruled texts, flagged for the magistrate)

A historical completed envelope has no `battery_float` key, so amendment 30 does not read its journal. If that journal is missing, the candidate raises `CustodyUnreadable("rounds.jsonl unreadable after authentication: …")` at QPC:1271-1273, and no summary is written.

Probe P4:
```
verdict: battery_float_evidence_missing
pilot_summary -> CustodyUnreadable rounds.jsonl unreadable after authentication: [Errno 2] …
```

The rulings point both ways:
- Text 6 says "Unreadable envelopes are excluded as today", and amendment 30 exempts this population.
- The seat brief's hard constraint says no reader converts a read failure into an exclusion except for 32(1) and amendment 35's routing.

The candidate follows the brief. It fails closed and affects neither archived pilot night (their historical row is green), but the "after authentication" wording is inaccurate for this population, because the helper never read the journal.

**Closure:** either the magistrate confirms the raise (and the message is reworded, e.g. `rounds.jsonl unreadable: …`), or text 6's "excluded as today" is applied to envelopes without a `battery_float` key. A ruling is needed either way; do not change the code at the bench.

### N-2 (NIT; outside the ruled text). Refusal-path write order leaves an honest-kill window that reads as custody

On the refusal path, `session.json` is written at SQ:1109 before `rounds.jsonl` at SQ:1110. A kill between the two leaves a refusal record with no journal. Amendment 30 shape (i) turns that into `CustodyUnreadable("round journal missing")`, and the carve-out cannot apply because `session.json` exists.

Probe P3:
```
session.json exists: True rounds.jsonl exists: False
authenticate_quiet_session -> CustodyUnreadable round journal missing
```

In practice this cannot happen: the refusal path finishes in seconds, and the executor only kills at `envelope_s + 30`. The order predates S2.

**Closure (magistrate's choice):** write the empty `rounds.jsonl` before the refusal `session.json`.

### N-3 (NIT). The replay branch's `summary.md` omits the excused and refused sentences

Amendment 35 Record says `summary.md` names every excused and every refused envelope. The replay branch (QPC:1502-1514) returns before the `notes` string is built.

**Closure:** append `notes` to the replay `summary.md` as well.

### N-4 (NIT). Test inputs and assertions that are narrower than the ruled rows

| Row | Gap |
|---|---|
| T6-f | Asserts `[0]['disposition']` but not "exactly one row, status `battery_float_evidence_missing`". |
| T6-p | Does not assert "status is not a battery status". |
| T6-q | Does not assert disposition `blanks_night`. |
| 32(d) | The `raw/` holds both fixture raw files, not "empty or a lone pre raw". |
| 34 | "Temp name is not `session.json` or `rounds.jsonl`" is shown only indirectly, through the preserved target. |
| T6-h | Exact input missing: T6-f bytes with exit 124, non-charging, pre raw deleted. Only the T6-g variant and other exit codes are present. |
| Historical row | `skipUnless` the local archives, so it does not run in CI. |

**Closure:** add the listed assertions and inputs. For the historical case, add a synthetic 12-envelope night whose sessions carry no `battery_float` key, run through `pilot_summary`, and expect `BATTERY_FLOAT_EVIDENCE_MISSING` in CI.

### N-5 (NIT). `test_L2_a_replay_night_that_wrote_no_session_still_refuses` now tests a different case

The test's name and history describe collectors killed before writing, which is a non-zero exit and therefore the amendment 32(1) carve-out. Its body now deletes the records under exit-0 entries and asserts custody. That is correct under amendment 32, but it drops the coverage "every collector crashed before writing, replay environment set → refused, rc 2", which is now reachable through the carve-out.

**Closure:** rename the test to match its body, and add the original scenario with `collector_exit` 124 on every entry. Expect the summary written, outcome `refused`, rc 2, and `recorder_kind` `replay`.

### N-6 (NIT; integration). The lead's sweep line will conflict with S1

`tests/test_battery_float_sweep.py:136` reads `set(PHASES[:7]) | {"quiet_pre","quiet_post"}`. S1 edits the same line for `bundle_*`. At integration the assertion must become exactly `set(battery_float.PHASES)`. Record this in the S1+S2 integration brief.

## 4. No findings

I found nothing on the following items:
- T5 collector placement (pre and post on both paths);
- the AD2 20 clock rule;
- amendment 33 in full;
- amendment 34's production code;
- text 6 blanking, confounded precedence and `battery_float_envelopes`;
- amendment 35 items 2 to 6 and the definitions;
- T6-f through T6-v and X-1 as implemented;
- text 15's flip and its tests;
- the sweep `OBSERVE_CALLERS` rows;
- every standing constraint in the lens charge.
