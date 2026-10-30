GPT-6 (exact deployment model identifier is not exposed by this runtime)
VERDICT: ACCEPT_WITH_FIXES

Reviewed mpmdw/JouleWise `574f13d2f..9615ea4a152bf5992472ffec4936356fb0ba3025`, draft PR #598, target `lane/2026-10-28-bytes-pass2-open`. Authority: registration §21 item 3 and §7, W1–W6 and the retained earlier rulings. Python 3.13.5; `JW_B5_SYNTHETIC_ONLY=1`, `PYTHONDONTWRITEBYTECODE=1`. Synthetic fixtures only, no hardware or real BYTES data. No production file was edited. Paths below are relative to this checkout; evidence is in `.codex-report/by-therm-lines-rev-sol-4/`.

1. **MAJOR — Matching seals still turn unusable journals into trusted membership decisions.** `scripts/bytes_thermal_lines.py:213`, `:246`, `:266`, `:277`. `read_monitor_journal` can return no usable readings without raising: all lines can be unparsable, every observation can lack `level`, or every `level` can have the wrong type. The caller only emits a malformed-line notice. With the correct pass and matching digest, `reason` remains null. The production thermal helper then finds no OS code in the empty usable-read set, and the tool restores an originally OS-excluded science member as `evaluated`. W1 requires untrusted evidence to retain that member's original codes and mark it undefined. This changes which members count, rather than merely representing the same decision differently. An empty sealed journal has the same problem. This is a trust-input hole in the new predicate's callers; the predicate itself obeys its supplied truth table.

   Repro from repository root:

   ```sh
   JW_B5_SYNTHETIC_ONLY=1 PYTHONDONTWRITEBYTECODE=1 python3.13 .codex-report/by-therm-lines-rev-sol-4/journal_repro.py
   ```

   Output tail:

   ```text
   SEALED_JOURNAL not-json exit 0 status evaluated restored ['a'] codes []
   SEALED_JOURNAL missing-level exit 0 status evaluated restored ['a'] codes []
   SEALED_JOURNAL wrong-level exit 0 status evaluated restored ['a'] codes []
   SEALED_JOURNAL empty exit 0 status evaluated restored ['a'] codes []
   ```

   Each archive has a single science member `a` carrying the OS code, explicit pass 1, valid integer spans, and a seal matching the journal bytes. These cases must reach W1 with an untrusted reason. No thermal arithmetic, tolerance or new exclusion policy is needed. This finding does not require treating every partly malformed journal as wholly unusable: the existing positive fixture with valid observations plus an unrelated malformed line still passes.

2. **MAJOR — Unparsable surrounding JSON is accepted as trusted evidence, including false equality.** `scripts/bytes_thermal_lines.py:49`, `:70`, `:157`, `:232`. `selected` decodes only the selected subtree and never validates the containing document. An assessment or spans document with trailing junk, a missing final root brace, or an invalid later sibling still supplies apparently trusted evidence. The same happens to `bytes_pass` inside a malformed plan document. Five code-free request-end cells also stop on an apparent would-add instead of reaching their untrusted-evidence invariant result. These are provably unparsable inputs: the probe checks that a whole-document JSON decoder rejects each fault before invoking the real CLI. Mutable members are nevertheless labelled equal or evaluated, and codes can change. This defeats W1's explicit unparsable-source protection, rather than introducing a new science requirement.

   Repro:

   ```sh
   JW_B5_SYNTHETIC_ONLY=1 PYTHONDONTWRITEBYTECODE=1 python3.13 .codex-report/by-therm-lines-rev-sol-4/documents.py
   ```

   Output excerpt (tuple fields: mode, original code present, candidate agrees, fault, control kind, exit, status, line equality, kept codes):

   ```text
   DOCUMENT FAIL ('hull-p2', False, False, 'trailing-junk', 'untrusted', 0, 'evaluated', False, ['thermal.os_level_nonzero'])
   DOCUMENT FAIL ('hull-p2', False, True, 'trailing-junk', 'untrusted', 0, 'equals registered line', True, [])
   DOCUMENT FAIL ('request-end-p1', True, True, 'plan-truncated-root', 'untrusted', 0, 'equals registered line', True, ['thermal.os_level_nonzero'])
   SUMMARY_DOCUMENTS 80 cells 25 failures
   ```

   The first case drops a previously code-free member using an invalid assessment. The other two certify equality for undetermined members. Preserve opaque measurement handling while validating source structure before treating selected fields as trusted. The independent 360-cell matrix's initial `bad-json` cases damaged the beginning of a document; they did not cover an intact selected subtree inside an invalid document. This additional matrix supplies both candidate states, both original-code states, both directions and paired valid-document controls.

3. **MINOR — Combined record damage and verification inside a source bypass W5's no-write behavior.** `scripts/bytes_thermal_lines.py:539`, `:552`, `:594`. Source roots are reconstructed only from a dict-valued `source_sha256`. Copy a valid output view inside its recorded source archive: verification correctly prints the flag and leaves the source unchanged. Damage that copied view's `source_sha256` to a list, and verification recovers the record with an empty root list, then rewrites `thermal_line.json` inside the source. Exit remains 0. Standalone field-damage recovery and intact-record inside-source protection each pass, but their combination does not. The demonstrated write is a control-record change, so severity is capped at MINOR.

   Repro:

   ```sh
   JW_B5_SYNTHETIC_ONLY=1 PYTHONDONTWRITEBYTECODE=1 python3.13 .codex-report/by-therm-lines-rev-sol-4/verify_extra.py
   ```

   Output tail:

   ```text
   SYMLINK 0 view verified
   MISSING 0 output missing False
   INSIDE_SOURCE 0 True UNCHANGED True
   INSIDE_SOURCE_DAMAGED_ROOTS 0 UNCHANGED False TAIL ['withheld/spans.json']
   ```

## Predicate and status-path audit

The literal claim that no status writer bypasses the predicate is false. All thermal-evidence branches converge on `member_status` at line 277, but structural/export overrides deliberately bypass it. These exceptions implement W4 and earlier export rulings; I do not report their existence as another defect.

Every status-writing path is:

| Path | Predicate relationship |
|---|---|
| Hull assessment, request-end journal/spans, and pass-identity branches | Converge at 277; assignment at 280. Findings 1–2 supply incorrectly trusted inputs. |
| Structural acceptance/roster fault or exclusion missing code | Calls predicate, then overrides at 278–280 as W4 requires. |
| `undefined` helper, 219–221 | Direct undefined assignment. Main-loop call at 282 repeats the predicate/structural result. |
| Missing acceptance `session_id`, 301 | Calls `undefined`; rolls back all science changes. W4 override. |
| Non-UTF-8 CSV, 332 | Calls `undefined` for all science members; rollback through `bad`. W4 override. |
| Invalid CSV header/shape, 350 | Same direct records-fault override. |
| CSV/archive disagreement or duplicate row, 358 | Direct member-specific records-fault override. |
| Changed member absent from export, 367 | Direct member-specific records-fault override. |
| Output `member_statuses`, 412–415 | Serializes the map; fallback equality is for unchanged references. Every well-formed roster science entry traverses the loop. Withheld `blinded_status` is a separate stage label. |

Line equality at 395–397 and 417 requires no changed codes and no undefined status. In the independent fault matrix, every direction-invariant member remained equal rather than wrongly becoming undefined. The 360-cell matrix failures are the originally excluded request-end members under the four unusable-journal faults in finding 1. The separate document matrix additionally demonstrates the false-equality class in finding 2.

## Earlier-review dispositions

Read both complete reviews and the entire implementation report, especially Fix round 4. Reran the pinned scripts from Sol `d332aefca` and Opus `3f0b7ce`; preserved originals under `prior_sol/` and `prior_opus/`.

| Prior finding | Disposition at this head |
|---|---|
| Sol 1 / Opus 1: missing/mismatched seal plus agreeing candidate labelled equal | Closed by W1 for those repros. Independent output now says undefined and false line equality. Finding 1 above exposes a different untrusted-evidence input. |
| Sol 2 / Opus 3: structurally damaged record and symlinked verify path | Original repros closed by W5: exit 0, flag true on damage; resolved output link verifies. The combined fault is finding 3 above. |
| Sol 3: integer `excluded` accepted as bool | Closed by W2; independent CLI integer/list/null and unavailable-field cases preserve codes with the correct direction rule. The unchanged Sol probe lacks hull pass identity, so its numeric cases are masked by W3; the independent matrix supplies the identity. |
| Opus 2: five remaining stops | Closed by W4; every named case writes a record, exits 0 and affects the correct science members. Missing exclusion code is member-specific; missing roster identity, null excluding, non-UTF-8 CSV and absent session identity have the ruled broader effects. |
| Opus 4: absent pass identity treated as a match | Original missing-identity repros closed by W3: absent tree/field, bool/string identity, wrong pass and a plan whose selected field cannot be parsed. Malformed surrounding plan structure remains finding 2. Invariant members stay equal under W1 in the closed cases. |
| Opus 5: invalid CSV reason overwritten | Closed by W6; empty/header-invalid CSV reasons survive on changed members. |
| Opus 6: verify creates nonexistent output | Closed by W5; `output missing`, exit 0, no directory created. |
| Opus 7: root record is not self-bound | Knowingly unchanged by the explicit ruling. Edited membership fields alone still verify; not a new finding. |

Confirmed the builder's positive-fixture claim: the unchanged sealed Sol probe fails its restoration assertion, and the unchanged sealed census prints exactly eight target/status failures, with no census failure. `pass_port.py` adds only the command's `bytes_pass` to each positive fixture, preserving other plan fields; it does not reseal journals or change production code. These ports give `PROBES_PASS` and `SUMMARY fails []`. W3 is the only cause of those sealed positive failures.

The retained historical repros have additional obsolete expectations. Original `sol_probes.py` lacks U2 provenance and W3 identity; original `delta_probes.py` stops at U1's required reused-output refusal. `delta_probes_u1.py` completes and preserves sources. Original `opus_chain_test.py` remains 22/24: pass-mismatch refusal and all-linked-files-read-only were superseded by the earlier rulings. Original `opus_chain_analysis.py` is 25/30: its five failed target-change checks lack W3 identities (pass-1 injections also lack U2 seals). The required module's explicit-identity/seal positive port supplies the stronger positive chain. `opus_probe_postcommit_heldout.py` first failed only at its hardcoded `/tmp/jw` fixture path; a separately recorded path-only port succeeds with 100 records and the same two models in source/output. No original failure was silently counted as passing.

## Executed

Commands ran from `/workspace/JouleWise`, with the two required environment variables and Python 3.13; `JW` and `PYTHONPATH` point to that checkout for legacy scripts. No compound command used `cd`.

- `matrix.py`: independent real-CLI cross product, 360 cells, 352 pass and 8 fail, as detailed in finding 1. A separate 80-cell document matrix has 55 passes and 25 failures: 10 false-equality records, 10 changed-member records and 5 unexpected stops, supplying finding 2. Hull cases cover missing/unparsable assessment, absent member/needed field, integer/list/null excluded, absent/integer availability, unavailable journal and wrong member container. Request-end cases cover absent/unparsable spans, missing member/field, wrong request/container types, float/bool stamps, absent/differing journal, absent/unparsable/incomplete/wrong-type seal, and sealed unusable journals. Both cover missing/malformed/mismatched pass identity and evidence-roster gaps. Both original-code states and agreeing/differing candidate controls execute; every fault is paired with a trusted control. Checks include exact kept code sets, drops, member status and line equality. Trusted request-end would-add controls stop before writing. Initial 180-cell run and strengthened paired-control run both reproduce finding 1.
- Prior Sol `independent.py`, `safety.py`, `exact_ns.py`; Opus `probes_v.py` and all three `adapted/` scripts; all inherited Sol delta scripts and Opus `probes_delta.py`/`census_t1.py`. Original scripts and separate ports have individual logs. Campaign and delta campaign complete `CAMPAIGN_DONE`; `view_and_gap.py` confirms exact OS projection on three real-gap variants and flags added/deleted files. The randomized gap probe reports 24,000 comparisons, zero OS differences.
- `journal_repro.py`, `documents.py`, `verify_extra.py`, `w4.py` (all five named faults in both directions with source-byte checks), W3-only positive ports, and guarded `sentinels.py` execute separately.
- `python3.13 -m unittest tests.test_bytes_thermal_lines tests.b6.test_bytes_p2_thermal_window tests.test_harvest_b5_window -q`: exit 0, `Ran 234 tests in 1271.553s`, `OK (skipped=11)`. Grouped analysis is 30/30 and the real harvest/acceptance chain is 29/29, including compressed journals; pass-1, block-5 and alpha replays each compare 177 files exactly.
- Overlap, existing/dangling/linked output, and matching-seal would-add repros refuse before source writes. Mismatched/unsealed would-add no longer stops; direction-invariant members remain equal. U1's existing-output refusal remains an explicit retained ruling.
- All ordinary W5 record-field damages tested exit 0, list `thermal_line.json`, and set the flag. Output symlink, intact view inside source, and nonexistent output pass their requested behavior. Finding 3 records the combination that does not.
- `git diff --check` passes; fixture orphan census `[]`, count 0, exit 0. Production diff is empty.

Census from the W3-only sealed port, source equals output at every stage:

| Sessions | Public + withheld physical rows | Science before commit | Science after commit / archive |
|---|---|---|---|
| s2, passes 1 and 2 | 63 + 50 = 113 | 50 | 100 |
| s5, passes 1 and 2 | 13 + 50 = 63 | 0 | 50 |

The port checks row identities, exact changed codes, all other fields, model preservation and the withheld-store opening gate. Guarded sentinel output is `decoded-sentinels []`, `sentinels-in-stdout-or-record []`, and `withheld-copy-bytes (True, 1)`. Energy, power, duration and rail fields do not reach the decoders or tool stdout/control records. Payload bytes are opened for opaque copying/hashing under the retained T4 design; this is not value interpretation. The probe itself prints a synthetic sidecar for inspection; that print is not tool disclosure.

Comparisons remain exact on codes, counts, integer nanoseconds, hashes and identity metadata. No float tolerance or agreement bar was introduced, and none was chosen in this review. The inherited boundary probe above `2**60` ns changes exactly as expected when the endpoint moves 1 ns. The helper's pre-existing gap computation is discarded for this OS-code projection, not an agreement tolerance. Pinned SHA-256 values match exactly:

```text
18582818c7e03bad148b54dce8b8d60a62e2ffc5597e701ae3ab0418dffc0a71  joulewise/bytes_analysis.py
2aec65877b3a7e6da096171eb305833750932e2b5e0674eb835f408a0ad6c744  joulewise/b5/harvest.py
```

CI was read through the GitHub connector on PR #598's exact head `9615ea4a152bf5992472ffec4936356fb0ba3025`. [CI run 40910211697](https://github.com/mpmdw/JouleWise/actions/runs/40910211697) completed successfully. Every job is successful: changes; fences; build; quick; installed-wheel; calibration-exits-exclusive (3.13); calibration-writer-crash-matrix-exclusive (3.13, 1); calibration-writer-crash-matrix-exclusive (3.13, 2); test (3.13, 1); test (3.13, 2); test (3.13, 3); test (3.13, 4); test (3.13, 5); test (3.13, 6); test (3.13, 7); test (3.13, 8); test (3.13, 9); test (3.13, 10); test (3.13, 11); test (3.13, 12). Separate gate-ledger run 40910211666 is skipped. No red job exists to attribute. Green CI does not cover the independent failures above.

## Decisions I made

- Treat unusable journal contents as W1 evidence faults even when their digest matches. A seal establishes identity, not usable required fields. Keep production thermal arithmetic and its valid numeric-reading semantics intact.
- Rate findings 1–2 MAJOR because they demonstrably change membership; cap finding 3 at MINOR because the demonstrated write changes only a control record. All fixes are determined by W1/W5; no new science ruling or process is proposed.
- Treat the archived assessment as hull evidence; hull does not reopen the journal. Journal/seal faults matter directly to request-end and through assessment availability to hull.
- Do not report W4's required structural/export overrides as another defect merely because they bypass the thermal predicate. Explicitly disclose that limit on the builder's structural claim.
- Preserve historical scripts and distinguish W3-only, seal and path adaptations. Retain U1/T4/T7 and the expressly unchanged root-record design.
- The runtime identifies me as GPT-6 but does not expose an exact deployment identifier; I cannot honestly manufacture one from the requested filename or the prior builder's model.
- Write only the requested report and script directory, on `codex/2026-10-29-by-therm-lines-rev-sol-4` from the requested head. No lead-owned state file or implementation was changed.

Review artifacts pushed on [codex/2026-10-29-by-therm-lines-rev-sol-4](https://github.com/mpmdw/JouleWise/tree/codex/2026-10-29-by-therm-lines-rev-sol-4). Report: `.codex-report/BY-THERM-LINES-REV-SOL-4.md`.
