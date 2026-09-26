# BFG-D fix round 2 (seat round 6): implementation seat report

Seat: a fresh Opus 5.5 session that wrote no earlier parser. Worktree `/Users/edr/code/JouleWise-wt-ed17a643-bfgd`, branch `feat/2026-09-25-bfg-d`, started at `d0f275cc` (its code is identical to `faf0ea01`: `git diff --stat faf0ea01 d0f275cc -- joulewise scripts tests configs docs/phase_2` is empty). Written 2026-09-25.

Commits (not pushed):
- `cf3ba566` R2-1, R2-8, R2-9, R2-11: the battery grammar and the bytes-only feeders.
- `dedc683b` R2-2, R2-3, R2-4, R2-10, and one R2-5 proof test: the Revision-5 refusals, the dry-run bound, the runbook flags.
- this report's commit: the R2-5 sweep guard test and this report.

Sources followed: the contract `18-fix-contract-r6.md` and the ruling `15-parser-esc-ruling-source.md` (§4 grammar, §5, §6 R2-1..R2-7). I also read the refuter `16-parser-esc-refuter.md` for the detail behind R2-8..R2-11.

## 0. Process disclosure

- **What I read.** The three documents above; the code and tests under my write scope; the fixture builders `tests/fixtures/epoch_bootstrap/build.py` and `tests/fixtures/epoch_continuation/build.py`; read-only greps of `joulewise/` and `scripts/` for the R2-5 sweep. The auto-loaded `CLAUDE.md` files and the memory index were in context. I opened no memory file and no `RUN_STATE`, `TASK_QUEUE` or council log.
- **Machine contact.** One read-only `/usr/sbin/ioreg -r -c AppleSmartBattery` (§6). There was no launchctl, powermetrics, sudo, installer or model inference.
- **Background tasks: two, not started on purpose.** Twice a foreground test command ran past the 600 s tool limit, and the harness moved it to the background by itself. The first was a combined unittest run, which I stopped at once (TaskStop) and re-ran in the foreground. The second was the final `tests.test_night_agent_install` run, which takes 626 s. I let it finish, and I read its result from its log before writing the tail below. I started no subagents and no watchers.
- **RED copies.** "RED" means the new test run against the old code and failed. The RED runs used `/tmp/bfgd-r6-faf0`, a `git archive faf0ea01` export with the new tests copied in. Where a new test fails at `faf0ea01` only because it uses an API that this round adds (`ProbeResult.stdout_bytes`, `_structure`), I also ran a semantic RED script, `/tmp/bfgd-r6-red-semantic.py`, against the old production shapes. That script shows the old behaviour itself, not an `AttributeError`.

## 1. Obligations: file:line, then RED at `faf0ea01` and GREEN

| Obligation | Where (file:line at `dedc683b`) | RED at `faf0ea01` | GREEN |
|---|---|---|---|
| **R2-1** grammar (§4) | `joulewise/battery_float.py:96` `_structure`: byte framing `:175-181`, line machine `:182-210`, value grammar `:115-173` (`value`, `string`, `container`); `parse` `:237` keeps the predicate stage unchanged; `_UINT` `:36` is now `[0-9]{1,20}` | Semantic script: of 108 corpus negatives, **68** return `passed=True` from `parse`. `evaluate_night` gives **GO on 68/108**. `validate_window` gives **`pass` on 68/108**. The control (ex-03) is GO. The 68 names are `tests/battery_float_corpus.py` `RED`; they include R2-A, R2-B (both variants), CRLF, bare CR, the CR smuggle, header garbage, duplicate optional/unknown/nested keys, every inline-delimiter fault, blank body lines and every bad atom. The corpus tests at `faf0ea01`: `FAILED (failures=209, errors=19)` (`/tmp/bfgd-r6-red-r21.log`) | `tests.test_battery_float.GrammarCorpusTests` (7 tests; the 4-site loops run 108 negatives at `parse`+`observe`, 2×108 at both gate entries, 2×108 at the window) OK |
| R2-1 real-capture fixture | `tests/fixtures/battery_float/float-2026-09-25-2047.ioreg` (sha256 `582475270c35c51cc05c2020f500d8c7dfba3eb9a6436a0186cb5ce18a851631`, the same bytes as trace `17-…`); README line added | — (new fixture) | `test_real_capture_fixture_is_ex03`, `test_real_capture_records_every_registered_property` OK |
| R2-1 mutation test | `tests/test_battery_float.py:708` `GrammarMutationTests`; sites found by AST (`_structural_raise_sites`) | At `faf0ea01` it ERRORs (there is no `_structure` to enumerate) | OK: **20/20** structural refusal sites are load-bearing (table in §1a) |
| **R2-8** type-check every recorded property | `joulewise/battery_float.py:213` `_recorded_values`: `Yes`/`No` for `ExternalConnected`, `IsCharging` and `FullyCharged`; `[0-9]{1,20}` below 2^64 for the other 8 | The semantic script: all **9** recorded-type negatives give window `pass` at `faf0ea01` (X8 `x8_apple_raw_current_capacity_yes`, `recorded_amperage_bool`, `recorded_voltage_string`, `recorded_temperature_data`, `recorded_fully_charged_int`, `recorded_current_capacity_dict`, `recorded_apple_raw_current_capacity_array`, `recorded_apple_raw_max_capacity_overflow`, `recorded_voltage_21_digits`) | Refused at all four sites inside `GrammarCorpusTests`; ex-03 and `float.ioreg` still pass |
| **R2-9** grammar freeze | Docstring sentence `joulewise/battery_float.py:9-13`; pin `tests/test_battery_float.py` `STRUCTURAL_STAGE_SHA256 = 1a9c3297…395d4f`, with the freeze comment above it. The pin is sha256 of `inspect.getsource(_structure) + inspect.getsource(_recorded_values)` | At `faf0ea01`: `test_structural_stage_is_pinned` ERROR and all 3 `test_mutating_the_structural_stage_fails_the_pin` subtests FAIL (there is no stage to hash) | `GrammarFreezeTests` OK: three file-backed mutants (depth 64→65, a signed atom, a lowercase boolean) each change the digest |
| **R2-11** bytes-only feeders | `observe` refuses non-bytes `battery_float.py:305-312`; `night_gate.ProbeResult.stdout_bytes` `night_gate.py:337`, used `:1518-1520`; `run_night._probe_runner` captures the ioreg argv without text mode `scripts/run_night.py:342-363`; `evidence_night.probe_command` `joulewise/evidence_night.py:674-681`; `arm_readiness_evidence_t0._ProbeResult.stdout_bytes` `:289`, filled `:478-485`, used `:1881-1883` | Semantic script, the refuter's CR-smuggled output through each production runner at `faf0ea01`: **t0** `verdict=GO passed=True`, recorded digest ≠ sha256(bytes), no CR left in `probe.stdout`; **arm_check** `passed=True probe_error=False`, digest ≠; **publish_install** `passed=True`, digest ≠; **t0_power_row** `passed=True`, digest = (that runner already kept bytes; the old parser accepted the CR through `splitlines`) | `BytesFeederTests` (2), `test_run_night…test_t0_battery_runner_passes_exact_bytes_and_refuses_cr_smuggle`, `test_evidence_night…test_arm_check_battery_runner_…`, `…test_publication_battery_runner_…`, `test_arm_readiness_evidence_t0…test_power_row_battery_probe_passes_exact_bytes_and_refuses_cr_smuggle`. Each drives a real child process that writes the bytes, through the real `subprocess.run` with the site's own keyword arguments: refused (`framing: byte`), with the recorded digest equal to sha256 of the child's bytes. Each has a real-capture control that passes |
| **R2-2** equivalence tool refuses Revision 5 | `scripts/epoch_equivalence_check.py:463-476` (`evaluate_session`, before `_slot_outcomes`/`_read_member_evidence` `:399`); import `:111` | `test_revision_five_session_is_refused_before_any_member_read` FAIL `AssertionError: member evidence read` (both `verdict_records=False/True`) | OK: exit 3, no `--out`, zero reads, no B lexeme printed; the zero-row session is unaffected (exit 5, INCONCLUSIVE); all 26 older tests OK |
| **R2-10** continuation refuses Revision 5 | `scripts/issue_epoch_continuation.py:78-87` (right after `session_absent`, before the first `_read_member_evidence` `:116`); the old gate, now unreachable, is removed; `--preregistration-sha256` is still accepted, for invocation compatibility (help text says so) | `test_revision_five_session_with_a_passing_verdict_is_refused_outright` FAIL `member evidence read` (the committed verdict is `pass`) | OK: rc 3, empty stdout, no candidate written, `read.call_count == 0` |
| **R2-3** dry-run bound | `scripts/issue_calibration_acceptance_generation.py:332-376`; the blocker is at `:362-365` | `…unnamed_computed_session_without_an_authentic_verdict` FAIL `0 != 5` (`admissible: yes`); `…recorded_under_another_registration` FAIL `0 != 5` | OK: the blocker `computed session W1: battery harvest verdict missing or uncommitted (working tree differs from HEAD)`, respectively `(identity mismatch: preregistration_sha256)`; `prepare-candidate` still exits 3 with the same reason |
| **R2-4** runbook flags | `docs/phase_2/derivation_night_runbook.md` §2.2 `:2492-2507`, §4.1 `:2962-2985`, equivalence-tool refusal `:2862-2867` and `:2885-2887` | Doc test: FAIL on **2 of 3** fenced invocations (§2.2 has neither flag; §4.1 lacks `--preregistration-sha256`); executed shapes: FAIL `5 != 0` on both | `RunbookDryRunFlagsTests` OK; `test_every_documented_dry_run_shape_is_admissible_on_a_clean_revision_five_epoch` OK (all 3 shapes rc 0, `admissible: yes`) |
| **R2-5** sweep | §2 below; guard `tests/test_battery_float_sweep.py`; proof test `tests/test_validate_powermetrics_fiducial_derivation_only.py` `RevisionFiveRederiveTests` | The guard and proof tests are inventory and proof tests. They pass at `faf0ea01` by design: they pin what exists, and they are not RED/GREEN tests | OK |
| **R2-6** | Not this seat's (it belongs to the delta reviewer, who must be a different model family) | — | — |
| **R2-7** bookkeeping | The fixture README line is done. The consumer list in obligations v1.1 §4.5 (`06-…`) is **NEEDS_SCOPE** (finding F3) | — | — |

**Stop rule.** The stop rule applies if the new grammar accepts a structurally wrong output. None of the 108 negatives, and none of my own adversarial variants, is accepted. I built no third parser.

### 1a. The mutation table

**What a relaxation is.** For each `raise ProbeError` site in `_structure`, found by AST, the test builds a mutant module in which that one refusal is replaced by one relaxation of it:
- `pass` deletes the refusal;
- `continue` skips the offending line; this is the `faf0ea01` failure shape, and it is used only for sites inside the line loop;
- `consume` returns `len(text)`, which means "treat the rest of the value as consumed"; it is used only inside the value helpers.

**The pass condition.** A site passes if some relaxation of it lets at least one corpus negative return from `parse` without raising.

| line | refusal | killing relaxation | negatives accepted | example |
|---|---|---|---|---|
| 176 | framing: type/size | pass | 1 | over_1_mib |
| 178 | framing: byte | pass | 4 | tab_in_string |
| 180 | framing: final LF | pass | 1 | missing_final_lf |
| 183 | header | pass | 6 | r1_other_object_name |
| 185 | open | pass | 2 | missing_open |
| 209 | close | pass | 1 | r1_missing_close_at_eof |
| 127 | value: token | consume | 8 | bare_garbage |
| 139 | unclosed string | consume | 1 | unclosed_quote_top |
| 198 | line length | pass | 1 | line_262145_bytes |
| 201 | property | continue | 5 | escaped_quote_top_key |
| 204 | duplicate key | pass | 3 | duplicate_required |
| 206 | value suffix | pass | 4 | delimiter_underflow |
| 123 | depth | pass | 2 | depth_65 |
| 172 | container: token | consume | 2 | mismatched_delimiter_dict |
| 192 | tail | pass | 6 | r1_trailer |
| 135 | escape | pass | 1 | bad_escape |
| 153 | nested key | consume | 6 | sol_outer_map_unclosed |
| 155 | duplicate nested key | pass | 1 | duplicate_nested_key |
| 159 | member `=` token | pass | 1 | dict_member_without_equals |
| 171 | unclosed dict/array | consume | 3 | unclosed_inline_dict_synthetic |

Two negatives were added so that a site had a killer: `r1_missing_close_at_eof` (the close site) and `dict_member_without_equals` (the `=` site). The typing stage `_recorded_values` is outside the mutation test. Its refusals repeat `_signed`/`_unsigned` for the required keys, so deleting one of them leaves the input refused, not accepted. It is covered by the corpus and by the freeze pin.

### 1b. The grammar as coded, against §4

The code follows §4 verbatim, with these readings:
- **Depth.** "At most 64" counts open containers inside one value. 64 nested containers are accepted (positive `depth_64`); 65 are refused.
- **Length.** The 262 144-byte limit applies to BODY lines, as §4 says ("a PROPERTY line"). A 262 144-byte property line is accepted (positive `line_262144_bytes`); 262 145 bytes are refused.
- **Empty object.** `    }` right after `    {` is refused as a property line, because PROPERTY+ needs one.
- **The type/size class** also covers a non-`bytes` input.

## 2. The R2-5 sweep

**The framing, from ruling §6 R2-5.** No B lexeme of a Revision-5 derivation session may be printed, written, compared or used in a decision before an authentic committed battery verdict is loaded, and never for a non-pass window. B is the calibration bound; its lexeme is the stored string of `b_fiducial_s` or `exact_bound_lexeme_s`.

**How the list was built.** The rows come from every production file under `joulewise/` and `scripts/` whose source names a B lexeme: 23 files, pinned by `tests/test_battery_float_sweep.py::test_every_b_lexeme_reader_is_classified`. Added to those are the verdict consumers and the `parse` feeders.

| # | file:line | reads or decides | gate | proving test |
|---|---|---|---|---|
| 1 | `scripts/issue_calibration_acceptance_generation.py:181-322` `registration_dry_run` (member read `:285`) | exclusion counts from member evidence | `:233-280` Revision-5 battery block: committed verdict loaded with the registration digest; refuses on `NoRecord`, `CustodyFailure` or a `compare_verdict` difference, or on non-pass, before `:285` | `test_dry_run_never_reads_member_evidence_without_authentic_verdict`, `test_dry_run_names_the_recorded_verdict_and_blocks_without_one` |
| 1b | same file `:332-376` `_dry_run_epoch_bound` | the recorded non-pass count over the computed set (verdicts only, no B) | R2-3: every computed session needs an authentic verdict | R2-3 tests (§1) |
| 1c | same file `:1485` `_prepare_candidate` → `_select_members` `:1705` → member read `:1210` | issuance | the battery block `:1548-1610` runs before `_select_members` | `test_replacement_issues_without_reading_confounded_b_or_a7_refusal` (a confounded window's B of 0.999 s would refuse issuance if it were read) |
| 1d | same file `:1375` `battery_verdict` | raw battery bytes only | the writer of the verdict | `CommittedVerdictTests`, `test_separate_pin_and_verdict_commits_refused_by_all_consumers` |
| 2 | `scripts/calibration_cadence_report.py:60-96` | cadence plists, no B | verdict loaded at `:85` before any window row | `test_cadence_report_requires_the_record_and_labels_from_it` |
| 3 | `scripts/issue_epoch_continuation.py:116` | member B | **refused outright** `:78-87` (R2-10) | R2-10 test |
| 4 | `scripts/epoch_equivalence_check.py:399,:406` | member B, printed and written | **refused outright** `:463-476` (R2-2) | R2-2 tests |
| 5 | `joulewise/calibration_epoch_continuation.py:94-112,:250-302` | a continuation record's lexemes | records come only from row 3's tool, which refuses Revision 5, plus a registry pin (`authenticate_epoch_continuation`) | R2-10 test; `test_unregistered_or_rotated_continuation_refuses_with_epoch_reason` |
| 6 | `scripts/calibration_ledger_backfill.py:78-80` | evidence `b_fiducial_s` → `exact_bound_lexeme_s` of UNRATIFIED candidate rows, written to the output, for any root it is given | **UNGATED** | **NEEDS_SCOPE** (F2) |
| 7 | `scripts/reissue_calibration_acceptance.py:127-205` | members of an issued acceptance | the predecessor must authenticate as issued (`:579-582`); a Revision-5 member reaches an issued acceptance only through row 1c | row 1c's test |
| 8a | `scripts/paper_excursion_decomposition.py:84-89`, `scripts/check_paper_replay_fence.py:82-83` | one pinned historical member, `20260722T145535-e941c821` | pinned by id and path | sweep guard (classification) |
| 8b | `scripts/check_paper_round7_artifacts.py:110` | committed paper artifacts | reads no custody | sweep guard |
| 8c | `scripts/paper_anchor_correction_quantified.py:96,:452-465,:700-709` | **every** capture under `<--corpus-root>/runs/instrument_validation`, B written to its output | **UNGATED** (operator names the root; nothing refuses a Revision-5 root) | **NEEDS_SCOPE** (F2) |
| 9 | `joulewise/calibration_ledger.py:3055,:6072-6077` | lexeme extraction at finalization (the writer side) | its print sites (`:295,:2169,:2322,:5459,:5483,:5509`) carry custody diagnostics and counts, never a lexeme | sweep guard |
| 10a | `joulewise/calibration_bracketing.py`, `joulewise/reduce.py`, `joulewise/powermetrics_fiducial.py` (pinned, forbidden) | issued acceptance, bracket rows, the capture's own bound | outside the derivation scope | pin proof §5 |
| 10b | `joulewise/whole_window.py:724,:802,:4339-4517`, `joulewise/detection_floor.py:775-830`, `scripts/mint_floor_artifact_generalized.py:2221-2225` | **bracket-row** B, and B from an issued acceptance | outside BFG-D's derivation scope; the bracket-session harvest check has no named owner (refuter C row) | F2 |
| 10c | `joulewise/controller.py:438-490`, `scripts/run_campaign.py:2112` | B of an operator-named instrument-calibration attachment, used in a decision and embedded in run metadata | **UNGATED** against a Revision-5 capture directory | **NEEDS_SCOPE** (F2) |
| 10d | `scripts/validate_powermetrics_fiducial.py:513-520,:2637,:2733` | the capture writer's own lexeme, into its evidence and its stdout JSON | the writer side, before harvest. The stdout JSON reaches the chain's output, which the runbook §2.2a step viii order keeps unread before the verdict. That is procedure, not code (F6) | — |
| 10e | same file `:1239-1300` `--rederive-from` | the stored and re-derived B of any source directory, written to `--output` | the protocol check `:1253-1257` accepts only v1/v2 40-pulse evidence; every Revision-5 capture is v3, so it refuses before any bound is read | **new** `RevisionFiveRederiveTests` (a v3 source with `battery_float` → refused, the rederive function never called, nothing written) |
| 11 | `scripts/sim_acc_25g83_rev5.py:109,:230` | synthetic values | opens no file (grep: no `read_*`/`open`/`glob`) | sweep guard |
| 12 | `joulewise/receipt_oracle.py:135`, `joulewise/arm_readiness.py:8240` | constant lexemes in synthetic receipts | none needed | sweep guard |

**Feeders of `parse`.** Pinned by `test_every_battery_observe_caller_is_listed_with_a_bytes_runner`.

| site | runner, and why it passes bytes | test |
|---|---|---|
| `night_gate.py:1521` (t0) | `probes.run` → `run_night._probe_runner`: bytes for the ioreg argv (`run_night.py:342-363`) → `stdout_bytes` | `test_t0_battery_runner_…` |
| `evidence_night.py:1369` (arm_check) and `:1792` (publish_install) | `probe_command`: `text=False` for the ioreg argv (`:678`) | the two `evidence_night` tests |
| `night_agent_install.py:1221` (validate_install) | `BATTERY_PROBE_RUNNER = None` → `observe`'s own `subprocess.run` without text mode | `test_default_runner_captures_bytes_without_text_mode` |
| `arm_readiness_evidence_t0.py:1882` (t0_power_row) | `_execute_probe` tempfile bytes → `stdout_bytes` | `test_power_row_battery_probe_…` |
| `validate_powermetrics_fiducial.py:2173` (slot_pre/post, the writer) | runner `None` (live), or the test fixture's bytes | `test_default_runner_captures_bytes_without_text_mode` |
| `battery_float.py:305-312` (`observe`'s old `str` branch) | removed: a `str` stdout is a probe error | `test_observe_refuses_text_stdout_and_never_re_encodes` |

**Verdict consumers.** The consumers of the committed verdict are the dry run (row 1), the epoch bound (1b), `prepare-candidate` (1c), the cadence report (2), and now two outright refusals (3, 4). Each goes through `load_committed_verdict` with the registration digest and refuses on `NoRecord`, `CustodyFailure` and a `compare_verdict` difference. The runbook invocations §2.2, §2.2a and §4.1 all carry both flags (R2-4). `docs/process/NIGHT_HANDBACK.md:182` holds a template line, not an invocation.

## 3. Expected-value and fixture edits

No assertion was weakened. Each edit below either changes a fixture's shape to match the new production behaviour, or replaces a gate expectation with the stricter outright refusal.

| file | before | after | why |
|---|---|---|---|
| `tests/test_night_gate.py` `result()` | `stdout: str` only | a `bytes` stdout also sets `stdout_bytes` (the text is its lossless decode) | the fake now matches the bytes-capturing production runner (R2-11) |
| `tests/test_night_gate.py` ×3 and `tests/test_run_night.py` ×1 | battery fixture `.read_text()` | `.read_bytes()` | same |
| `tests/test_night_gate.py` legacy-engine comparison ×2 | `engine.ProbeResult(**asdict(value))` | only fields the engine defines | the pre-v4 engine at `a90ab4e8` has no `stdout_bytes` |
| `tests/test_run_night.py` `fake_run` | always returned `""` | returns `""` in text mode and `b""` otherwise | models `subprocess.run` faithfully |
| `tests/test_battery_float.py` `GateTests` ×3 | `stdout=changed.decode()`, `charging.decode()` | bytes; `raw_stdout` is compared with `charging.decode()` | R2-11 |
| `tests/test_arm_readiness_evidence_t0.py` `_probe_result`, `_float_ioreg` | str | bytes, with `stdout_bytes` set | matches `_execute_probe` |
| `tests/test_evidence_night.py` ×4 battery fakes | str stdout | `.encode()` | matches `probe_command` for the ioreg argv |
| `tests/battery_float_fixture.py` `answer()` | text-mode stdout | bytes stdout | same |
| `tests/test_epoch_equivalence_check.py` `build()` | default epoch `TARGET_EPOCH` (= `REVISION_FIVE_EPOCH`) | default `SUCCESSOR_EPOCH` (os_build `25G99`); assertions unchanged | R2-2 refuses Revision 5; 13 of the 26 old tests would otherwise exit 3 |
| `tests/test_epoch_continuation.py` `build()` and the slot-count case | `TARGET_EPOCH` | `SUCCESSOR`; `judged_epochs`, the identity-field loop, `evaluate()` and the later night use `SUCCESSOR_EPOCH` | R2-10 |
| `tests/test_epoch_continuation.py` `test_revision_five_registration_digest_missing_or_wrong_refuses` | expected `preregistration_sha256_required` / `identity mismatch: preregistration_sha256` | `revision_five_session` for None, a wrong digest and the right digest | the outright refusal |
| `…test_revision_five_session_is_gated_on_battery_float_like_the_issuer` (renamed `…_is_refused_whatever_its_battery_float`) | `battery_float_confounded` / `battery_float_evidence_missing` | `revision_five_session` | same |
| `…test_revision_five_session_refuses_without_a_record_or_on_custody_failure` | `battery_float_verdict_missing: absent or uncommitted` / `battery_float_custody_failure: d04/post …` | `revision_five_session` (both) | same |
| `…test_retained_epochs_must_be_unanimous…` third case | `battery_float_verdict_missing: identity mismatch: identity_epoch`; `content_id` case on `TARGET_EPOCH` | `revision_five_session`; `content_id` case on the successor epoch | same |
| `tests/test_issue_calibration_acceptance_generation.py` `test_separate_pin_and_verdict_commits_refused_by_all_consumers` (continuation leg) | rc 3 with `verdict not committed with its ledger head pin` | rc 3 with `revision_five_session`, plus an assert that no output file exists | R2-10 |
| same file, `test_dry_run_names_the_recorded_verdict_and_blocks_without_one` | rc 0 after harvesting W1 only | W1 and W2 are both harvested before the rc-0 assertion | R2-3: W2 is computed, and it blocks while it has no verdict (exactly Astra M1's case) |
| `tests/fixtures/epoch_continuation/build.py` | the night on `TARGET_EPOCH` | the night on `CONTINUED_EPOCH` (`25G99`) | no continuation can exist for Revision 5 |
| `tests/test_validate_powermetrics_fiducial.py` | `TARGET_EPOCH` (22 uses) | `CONTINUED_EPOCH` | same fixture |
| `tests/test_validate_powermetrics_fiducial_derivation_only.py` `test_ordinary_continued_epoch_capture_requires_registered_continuation` | `_epoch("25G83")` | `_epoch(CONTINUED_EPOCH["os_build"])` | same |

## 4. Test tails (GREEN at `dedc683b`)

```
tests.test_battery_float                                  Ran 47 tests in 40.098s   OK
tests.test_night_gate                                     Ran 104 tests in 0.889s   OK
tests.test_evidence_night                                 Ran 161 tests in 242.682s OK
tests.test_install_night_agent                            Ran 65 tests in 55.159s   OK
tests.test_night_agent_install                            Ran 82 tests in 625.896s  OK
tests.test_arm_readiness_evidence_t0                      Ran 78 tests in 361.652s  OK
tests.test_run_night                                      Ran 237 tests in 110.610s OK
tests.test_validate_powermetrics_fiducial_derivation_only Ran 27 tests in 199.452s  OK
tests.test_issue_calibration_acceptance_generation        Ran 141 tests in 122.073s OK
tests.test_calibration_cadence_report                     Ran 9 tests in 1.866s     OK
tests.test_epoch_continuation                             Ran 68 tests in 49.045s   OK
tests.test_epoch_equivalence_check                        Ran 28 tests in 10.788s   OK
tests.test_acc_25g83_rev5                                 Ran 12 tests in 14.941s   OK
tests.test_custody_mode_inventory                         Ran 7 tests in 37.940s    OK
tests.test_docs_freshness                                 Ran 31 tests in 0.465s    OK
tests.test_gen_state                                      Ran 44 tests in 1.803s    OK
tests.test_battery_float_sweep (new)                      Ran 2 tests in 0.051s     OK
```

Outside the list: `tests.test_validate_powermetrics_fiducial` ran 12 tests, **FAILED (failures=5)**. The same 5 fail with the same assertion (`('calibration_ledger_head_mismatch', …) != ()` in `_continuation_snapshot`) on an untouched `git archive HEAD` export (`/tmp/bfgd-r6-head`), so they predate this round (finding F4).

## 5. Pin proof

```
$ git diff --stat c6814dd8 -- joulewise/calibration_bracketing.py joulewise/adapters/powermetrics.py joulewise/powermetrics_fiducial.py joulewise/uncertainty_evidence.py joulewise/reduce.py protocol_v3.json scripts/night_chains configs
[empty]
```

## 6. A live read against the new grammar

One read-only `/usr/sbin/ioreg -r -c AppleSmartBattery`, rc 0: 17352 bytes, 64 lines, 0 CR, sha256 `5d71cb5d709a2bf5…`. It is accepted with 59 top-level keys and `passed=True` (UpdateTime age 48 s, InstantAmperage 0). That is a third real sample; the ruling saw two.

## 7. Findings

- **F1. The ruling's premise does not hold for the fixtures (MATERIAL for review; closed here).** Ruling §5.1 says the 26 existing equivalence tests are "none Revision-5". In fact every fixture in `tests/fixtures/epoch_bootstrap/build.py` defaults to `TARGET_EPOCH`, which equals `REVISION_FIVE_EPOCH`, and the same holds for the continuation suite and the continuation fixture builder. The rule-mechanics tests therefore now run on a hypothetical successor build (os_build `25G99`), with their assertions unchanged (§3). The delta reviewer should confirm that this is the right domain for the tools' surviving mechanics.
- **F2. NEEDS_SCOPE: three ungated readers, plus a lane question.**
  - `scripts/calibration_ledger_backfill.py:78-80` writes B from any root it is given.
  - `scripts/paper_anchor_correction_quantified.py:700-709` reads B from every capture under the named corpus root.
  - `joulewise/controller.py:438-490` (with `scripts/run_campaign.py:2112`) uses the B of an operator-named calibration attachment in a decision.

  Each is reachable for a Revision-5 capture only when an operator names that directory. None refuses it. The cure has the R2-2 shape: refuse when the evidence carries `battery_float`, or when its identity epoch equals `REVISION_FIVE_EPOCH`. All three are outside my write scope. Separately, the bracket-row B readers (sweep row 10b) have no named owner for a bracket-session battery harvest check (refuter row C).
- **F3. NEEDS_SCOPE: R2-7 and N-3 bookkeeping.** Two edits to obligations v1.1 (`06-harvest-final-obligations-v1.1-source.md`) remain. The consumer list in §4.5 gains `epoch_equivalence_check` and `issue_epoch_continuation` (both refusing), and §5.1's `^\s+"Key" = value$` sentence becomes a pointer to ruling §4. My scope names this directory only for my report, so I did not edit it.
- **F4. Pre-existing failures.** 5 tests in `tests.test_validate_powermetrics_fiducial` fail at branch HEAD, independent of this round (§4). The module is not on the contract's list; I made no fix attempt.
- **F5. Refuter C4 not adopted.** The contract did not adopt refuter C4, the single `battery_bearing` helper. The consumers still scope "Revision 5" by `identity_epoch == REVISION_FIVE_EPOCH`. The two new refusals use the same predicate, as ruling §5.1 specifies.
- **F6. The runbook narrative (MATERIAL, outside R2-4's text).** I added the required sentence, but the runbook's PASS route for this lane still describes an equivalence night for epoch 25G83/v3, judged by `epoch_equivalence_check` and followed by a D-102 continuation addendum. Both tools now refuse that epoch, and registration Revision 5 says the look is not taken. The surrounding §2.4/§2.5/§4 prose needs a reconciliation pass that is larger than R2-4's text. Also, the writer's stdout JSON carries B into the chain output (sweep row 10d); only the runbook's read order keeps it unread before the verdict.
- **F7. The power-row RED is not a digest RED.** At `faf0ea01` the `t0_power_row` path already kept the bytes: the digest matched, and the old parser accepted the CR through `splitlines`. The new grammar alone closes that path. R2-11 there makes the bytes, not the decoded text, the grammar's input.
- **F8. The freeze pin covers the typing stage too.** The pin hashes `_structure` and `_recorded_values` together, and the docstring's freeze sentence names both. The ruling's "structural stage" is read as everything that decides whether a document is accepted.

## 8. Scratch

The /tmp scratch is `/tmp/bfgd-r6-faf0` (the `faf0ea01` export with the new tests), `/tmp/bfgd-r6-head` (the HEAD export), `/tmp/bfgd-r6-*.log`, `/tmp/bfgd-r6-red-semantic.py`, `/tmp/bfgd-r6-corpus-check.py`, `/tmp/bfgd-r6-red-set.txt`, `/tmp/bfgd-r6-live.ioreg` and `/tmp/bfgd_new_parse.py`. They stay in place for the delta reviewer's reproduction and are removed at the lead's discretion.
