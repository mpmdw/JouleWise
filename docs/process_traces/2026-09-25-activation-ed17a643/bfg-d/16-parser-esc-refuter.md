# 21 — Opus 5.5 contract-lens refuter, cold gate BFG-D-PARSER-ESC-01

Paired refuter for the Fable cold gate charged at `00-charge.md` (packet commit `783e46ac`). Code under review: `faf0ea01` (BFG-D fix round 1). Written 2026-09-25 ≈20:57–21:10 PDT, in one foreground session, with no background tasks and no subagents.

## Contamination disclosure

- **Auto-loaded context.** My context loaded the global and project `CLAUDE.md` files and the auto-memory **index** (`MEMORY.md`, one-line hooks only). One hook paraphrases #421 ("battery-float gate every window"). I opened no memory file, and no `RUN_STATE.md`, `TASK_QUEUE.md`, council log or run report.
- **What I read.**
  - This packet: the charge and exhibits ex-00 to ex-05. All six digests match the manifest.
  - `bfg-d/00-final-texts-v1.1-source.md` on the BFG-D branch, by grep for parser clauses.
  - `10-coldgate-packet-bfg/ex-00-directive.md`, the #421 text.
  - `configs/calibration/preregistration_d079_epoch_25g83_rev1.md`, lines 597–646, by grep.
  - Code at `faf0ea01`, exported by `git archive` to `/tmp/ref-opus-esc/tree`.
- **Drift.** `origin/feat/2026-09-25-bfg-d` has moved to `422bfca2`, a descendant of `faf0ea01`. The code diff between them (`git diff --stat faf0ea01 422bfca2 -- joulewise scripts tests configs`) is **empty**; the new commit adds review reports only.
- **Live read.** I ran one read-only `/usr/sbin/ioreg -r -c AppleSmartBattery` at ≈20:55 (rc 0, 64 lines, sha256 `c0a40c19…`).
- **Consult prototypes.** I copied `/tmp/bfg_design_check.py` (Sol) and `/tmp/ed17a643/esc/astra-consult/grammar_probe.py` (Astra) into my scratch directory and ran them unmodified.

## Phase 1 — independent answers with executed evidence

### E1 — defects reproduced; both consult grammars verified

Harness: `/tmp/ref-opus-esc/harness.py`. It imports the production `joulewise.battery_float.parse` from the `faf0ea01` export. The "current" column below shows `PASS` when `parse()` returns `passed=True`, with wall time = UpdateTime + 10 s.

| Check | Result |
|---|---|
| Existing `tests.test_battery_float.ParserTests` at `faf0ea01` | `Ran 7 tests … OK`. The suite is green while both defects below are live, so it does not detect them. |
| R2a: header `<class OtherBattery, …>`, otherwise the real capture | current **PASS**, Sol refuse, Astra refuse |
| R2b: `"Outer" = {` / `"Inner" = {` / `}` followed by the four required lines, outer never closed | current **PASS**, Sol refuse, Astra refuse |
| Sol prototype, its own list | capture `(59, 62, 2)` accepted; all 19 listed mutations refused; rc 0 |
| Astra prototype, its own list | `positives=8/8 negatives=62/62 PASS`; capture accepted with 0 lines rejected; both round-2 false GOs reproduced against production; rc 0 |
| Both grammars on today's **live** read | Sol ACCEPT, Astra ACCEPT |

**E1 confirmed.** Both defects are real at `faf0ea01`. Each consult grammar accepts ex-03 and refuses every counterexample on its own list.

### Adversarial outputs I built against the grammars (none of these come from the consults' lists)

| Case | current | Sol | Astra |
|---|---|---|---|
| X1 header `<anything at all>` | **PASS** | refuse | refuse |
| X2 required keys only inside a multi-line nested dict, outer closed | refuse | refuse | refuse |
| X3 unclosed nested dict, required keys after it | refuse | refuse | refuse |
| X4/X5 CR inside a line; required key smuggled after the CR | refuse | refuse | refuse |
| X6 tab-indented required line | refuse | refuse | refuse |
| X7 duplicated **optional** key (`Voltage` twice, conflicting) | **PASS** | refuse | refuse |
| **X8 malformed recorded property `"AppleRawCurrentCapacity" = Yes`** | **PASS** | **ACCEPT** | **ACCEPT** |
| X9/X10 unbalanced top-level value `{"a"=1` / `(1,2` | **PASS** | refuse | refuse |
| X11 property line after `    }` | refuse | refuse | refuse |
| X12 leading blank line | refuse | refuse | refuse |
| X13 CRLF throughout | **PASS** | refuse | refuse |
| X14 no final LF | **PASS** | refuse | refuse |
| X15 object name `OtherBattery`, class correct | refuse | refuse | refuse |
| X16 indented child `  +-o Child` after close | refuse | refuse | refuse |
| X17 homoglyph key (Cyrillic а) | refuse | refuse | refuse |
| X18 21-digit zero-padded `InstantAmperage` (= 0) | PASS | ACCEPT | refuse |

**Result: none of my structurally wrong outputs produces a false GO under either grammar.** The one input that both grammars accept is X8. X8 is a contract gap, not a grammar defect; see C1.

**Legitimate-looking variants: this is an availability risk, not a safety risk.** A refusal here means `probe_error`, which is never a pass.

| Variant | Sol | Astra |
|---|---|---|
| V1 nested empty data `<>` | refuse | accept |
| V2 ioreg's ASCII rendering of data `<"AppleSmartBattery">` | refuse | refuse |
| V3 header `busy 1 (13 ms), retain 12` | accept | accept |
| V4 header `!registered` | refuse | refuse |
| V5 header id in uppercase hex | accept | refuse |
| V6 nested key with a space `{"A B"=1}` | accept | refuse |
| V7 top-level key `"a.b"` | refuse | accept |
| V8 string containing `\n` escape | accept | refuse |
| V9 70,000-byte line | refuse | accept |
| V10 1.02 MB output | refuse | refuse |
| V11 non-ASCII nested string | refuse | refuse |

The real capture and the live read contain none of V1–V11. Other measurements from the two files:
- Longest line: 9,179 bytes.
- `<"` occurrences: 0.
- Nested keys containing a space: 0.
- All 11 registered property names are present exactly once at top level, in both files.

The two grammars differ only on availability. Neither admits anything the other refuses on safety grounds.

### Contract findings the ruling must close

**C1 — MATERIAL. The registered predicate text is stricter than obligations §5.1, and both grammars follow the looser text.**
- The registered **Predicate** paragraph (00-final-texts line 158) says: "A missing, duplicated, malformed or unreadable **property** … is not a pass." It names 11 properties.
- Obligations §5.1 (line 87) narrows this to "…**required** property".
- Production (`battery_float.py`, the optional loop after the predicate) maps a malformed recorded value to `None`. Both consult grammars type-check only the four gated keys.
- So X8 is accepted everywhere, and the stored record then carries `apple_raw_current_capacity_mah: null`. `delta_q_mah` then goes null without any flag.
- **Closure.** Adopt the registered text literally. All 11 named properties must appear exactly once at top level:
  - `ExternalConnected`, `IsCharging`, `FullyCharged` must be `Yes|No`;
  - `InstantAmperage`, `Amperage`, `UpdateTime`, `Voltage`, `Temperature`, `CurrentCapacity`, `AppleRawCurrentCapacity`, `AppleRawMaxCapacity` must be `[0-9]{1,20}` and below 2^64.
- Anything else is `probe_error`.
- Cost on this machine: zero. The capture and the live read carry all 11 with exactly these types.
- If the ruling prefers the obligations reading instead, it must say so explicitly. Either way, the §5.1 text needs a one-line amendment so the two texts stop disagreeing.

**C2 — MATERIAL. The ruling needs a grammar-freeze clause.**
- Every harvest consumer re-parses raw bytes with the *current* module (`validate_window` → `parse`) and demands `compare_verdict(record, recomputed) is None`.
- Both consults' compatibility notes say a newly observed legitimate format needs "an explicit grammar extension".
- If the grammar is extended after a Revision-5 verdict has been committed, the replay can flip a slot from `evidence_missing` to `pass`. That verdict then mismatches, and the session becomes unconsumable. Worse, a gate outcome would change after the window without any registration act.
- **Closure.** The grammar is frozen for the Revision-5 epoch. Any change to `parse` needs two things:
  - a replay of every committed Revision-5 verdict with zero `compare_verdict` differences, shown in the PR;
  - and, if any differ, a registration amendment instead.

**C3 — MATERIAL, and it shapes E3. `issue_epoch_continuation` must refuse Revision 5 outright; the battery gate there is not enough.**
- Preregistration rev line 614: "Revision 2's equivalence look is NOT taken for this epoch … There is no PASS continuation branch or FAIL branch for this epoch."
- At `faf0ea01`, `scripts/issue_epoch_continuation.py:86-107` *gates* Revision-5 sessions: a `pass` verdict proceeds to derive a continuation record. That offers a branch the registration says does not exist.
- The tool also cross-checks against an `epoch_equivalence_check.v1` record (`:297-308`, `_s9_projection :201`).
- So the same outright refusal must cover **both** `epoch_equivalence_check.py` (Sol F1) and `issue_epoch_continuation.py`.

**C4 — MATERIAL. The consumers use different predicates to decide whether a session is "battery-bearing".**
- `check` (`issue_calibration_acceptance_generation.py:234`) and continuation (`:86`) gate only when `identity_epoch == REVISION_FIVE_EPOCH`.
- `_battery_computed_set` (`:1300-1312`) instead uses `… or not battery_float.predates_battery_float(session)`.
- `calibration_cadence_report.py:81` gates every session unconditionally.
- Three scoping rules leave room for a sibling bypass: a session whose evidence carries `battery_float` but whose epoch differs from the constant is gated by one consumer and not by another.
- **Closure.** Define one helper, `battery_bearing(session) = any Rev-5 epoch row OR not predates_battery_float(session)`. `predates` already returns False when authentication fails, so custody damage cannot create the exemption. Every consumer and every refuse-outright tool must use this helper.

**C5 — NIT. The ruling should pin the exact text of these unifying choices.**
- Sol's spec says 1 MiB, but its prototype uses 1,000,000 bytes.
- Sol refuses `<>`; Astra accepts it.
- Astra's header regex accepts lowercase hex only.
- **Recommendation.** Take Astra's value profile, which is the stricter of the two:
  - `DATA := <(?:[0-9a-fA-F]{2})*>`;
  - atoms `Yes|No|[0-9]+`;
  - per-dict duplicate-key refusal;
  - 262,144-byte line cap and 1,048,576-byte total cap.
- Use Sol's quoted-key production for nested keys. Nested keys never feed the predicate, so this costs no safety.
- Header id: `0x[0-9a-f]+`, which is what was observed.

**C6 — NIT, a recommendation.** Before arming W1, run the new `parse` on ≥20 live reads over ≥10 min at float, and retain the raws.
- Arm and t0 already use the same parser (`observe` → `parse`), so format drift would surface at arm.
- A mid-window variant, though, costs a whole window as `evidence_missing`. The soak costs minutes.

### E2 — my independent grammar answer

- **Structure.** A whole-stdout grammar, exactly as in the Astra document pseudocode:
  - header on line 1;
  - `    {` on line 2;
  - a BODY of six-space `"KEY" = VALUE` lines, each fully consumed by the recursive VALUE grammar;
  - the first exact `    }` line moves to TAIL, where only `' *'` lines are allowed;
  - EOF before the close is a refusal.
- **Framing.** LF-only split, ASCII 0x20–0x7e plus LF, final LF required. No `splitlines`, `strip` or `decode`-with-replace.
- **Properties.** Duplicates of any top-level key are refused, plus C1's 11-property typing.
- **Carrying state across lines.** No state survives from one physical line to the next except the BODY/TAIL flag. By construction, nothing counts nesting depth across lines.
- **Refusal classes.** The union of both consults' lists, plus X1, X7–X10, X13 and X14, plus C1's malformed-recorded-property class.
- **`-a` (plist).** Do **not** ask the owner now. The text grammar is now fail-closed. `-a` changes the registered text and the retained-raw format, and adds a second bespoke parser (a type/duplicate-key-checked plist). Ask only if a legitimate text variant is ever refused in practice. It is not required for W1.

### E3 — independent answer

- **Sol F1 (BLOCKER, confirmed).**
  - `epoch_equivalence_check.py:353-413` (`_slot_outcomes`) reads `evidence["b_fiducial_s"]` for every valid-resolved slot. It has no battery reference: `grep -c battery` = 0.
  - **Closure.** Refuse outright, per C3. Immediately after `resolve_session` (`:631`), and before `evaluate_session` or any `_read_member_evidence`, raise `EquivalenceRefusal("revision_five_no_equivalence_branch")` when `battery_bearing(session)`. Apply the identical refusal in `issue_epoch_continuation.derive_record`, before `:108`.
  - **Tests.** RED at `faf0ea01`: a Revision-5 fixture with no verdict file writes a record containing `b_fiducial_s`, as Sol's V4 did. GREEN: rc ≠ 0, no output file, and a spy on `_read_member_evidence` records zero calls. Run the same pair with a *passing* committed verdict, to prove that the refusal is outright and not a gate.
- **Astra M1 (MATERIAL, confirmed by reading).**
  - `issue_calibration_acceptance_generation.py:360-361` reads `except battery_float.NoRecord: continue`.
  - **Closure.** Append the blocker `computed session {id}: battery harvest verdict missing or uncommitted ({reason})` and set `battery_gate_blocked`. Then assert that `check` returns non-zero with registration inadmissible.
  - **Test.** Astra's repro: W1 omitted, W1's verdict deleted from the working tree. RED at `faf0ea01` is rc 0 plus "admissible: yes"; GREEN is rc ≠ 0 with the blocker naming W1.
- **Sol F2 = Astra M2 (MATERIAL).** Runbook §2.2 and §4.1 (`derivation_night_runbook.md:2495, :2950`) must carry `--preregistration` and `--preregistration-sha256`.
  - **Test.** Extract every `issue_calibration_acceptance_generation.py check` block from the runbook and run each against the Revision-5 fixture. Expect the documented rc; RED is today's rc 5. At minimum, a grep test that every such block carries both flags.

### E4 — sweep inventory at `faf0ea01` (grep-derived; the file:line references are the gate sites)

**A. Live-probe consumers.** All go through `observe` → `parse`, so the parser cure closes all of them without per-site edits. Each needs one RED/GREEN test that a structural refusal yields `probe_error` and refuses at that site.

| Site | Phase |
|---|---|
| `joulewise/night_gate.py:1515` | arm_check/t0 |
| `joulewise/evidence_night.py:1365, :1788` | `require_pass` |
| `joulewise/night_agent_install.py:1221` | publish/validate_install |
| `joulewise/arm_readiness_evidence_t0.py:1877` | t0_power_row |
| `scripts/validate_powermetrics_fiducial.py:2173` | slot_pre/slot_post writer |
| `scripts/run_night.py:47` | timeout wiring, FX-9 |

**B. Harvest-verdict consumers** (`validate_window` + `load_committed_verdict` + `compare_verdict`):

| Site | Gate status |
|---|---|
| `issue_calibration_acceptance_generation.py:233-275` (`check`) | gated; epoch-scoped (C4) |
| `…:340-368` `_dry_run_epoch_bound` | **swallows NoRecord (M1)** |
| `…:1300-1312` `_battery_computed_set` | `predates`-scoped (C4) |
| `…:1420-1445` prepare/verdict writer | writer |
| `…:1581-1597` | gated |
| `scripts/calibration_cadence_report.py:81-93` | gated, unconditional |
| `scripts/issue_epoch_continuation.py:86-107` | gated, **must refuse outright (C3)** |

**C. Readers of B-bearing evidence with no battery reference** (`grep -c battery` = 0 in each):

| Site | What it reads | Status |
|---|---|---|
| `scripts/epoch_equivalence_check.py:398-413` | member `b_fiducial_s` | **UNGATED: F1/C3, refuse outright** |
| `scripts/calibration_ledger_backfill.py:79` | member `b_fiducial_s` → `exact_bound_lexeme_s` of UNRATIFIED candidate rows | **UNGATED.** Not a claim path, but it writes B into proposed ledger rows. Refuse evidence that is `battery_bearing`, or name it an explicit exemption in the ruling |
| `scripts/reissue_calibration_acceptance.py:127-205` | members of an *issued* acceptance | transitively gated (inputs only from the gated issuer) |
| `joulewise/whole_window.py:724, :802, :4339-4517`; `detection_floor.py`; `scripts/run_campaign.py:2112` | B from an issued acceptance/bracket | transitively gated for derivation B |
| `scripts/mint_floor_artifact_generalized.py:2221-2225`; `calibration_bracketing.py:1189-1218, :1691, :2425` | **bracket-row** `exact_bound_lexeme_s` (pre/post calibration brackets) | **UNGATED, and outside BFG-D's derivation scope.** #421 §1 covers "calibration, evidence and claim-bearing windows", so the sweep must name the lane that owns the bracket-session harvest check. Silence here is the same signature one level up |
| `scripts/paper_excursion_decomposition.py`, `paper_anchor_correction_quantified.py`, `check_paper_*` | pinned historical bundles (constant `0.030067931757111657`) | out of scope; pre-Revision-5 |
| `scripts/sim_acc_25g83_rev5.py` | synthetic | out of scope |

**My fix-round-2 order, each step with RED at `faf0ea01` then GREEN:**
1. Parser rewrite (E2 + C1 + C5), with the full refusal table as tests, including X1, X7–X10, X13, X14 and X8.
2. Grammar-freeze clause (C2), written into the module docstring and the obligations text.
3. `battery_bearing` helper (C4), adopted by every B consumer.
4. F1 + continuation refuse outright (C3).
5. M1.
6. Runbook flags.
7. The sweep table above, committed as a test. Every `__main__` script whose source matches `b_fiducial_s|exact_bound_lexeme_s` must either reference the helper or appear on an explicit, reasoned exemption list. A new ungated reader then fails CI instead of waiting for a third review round.
8. C6 soak before arm.

## Phase 2 — refutation of the Fable ruling

**The ruling I refuted.** `/Users/edr/code/JouleWise-wt-ed17a643-cg-pe/…/20-coldgate-fable-parser-esc-ruling.md`: 33,712 bytes, sha256 `3804f9157a24628f50bfd4d374ee31a476479479ea4758b58e2f79a0c5b0159f`. It appeared at 21:06:35 PDT, and its size was stable across a 30 s recheck.

**How I tested it.** Fable's reference implementation was removed, so I implemented §4's grammar text **verbatim and independently** (`/tmp/ref-opus-esc/fable_grammar.py`) and ran it on:
- my Phase 1 corpus (X1–X18, V1–V11);
- the four repository fixtures;
- six new edge cases (A1–A6).

**Correction to my own Phase 1.** Sol's prototype list has **20** mutations, not 19; Fable's count is right.

### Headline

The grammar text is sound. Verbatim, it:
- accepts ex-03, today's live read, and `float.ioreg`, `charging-…` and `stale-…`;
- refuses `malformed-synthetic-from-real.ioreg`, R2-A, R2-B and every structural adversary I built.

Two MATERIAL contract gaps remain, plus one MATERIAL item that is now confirmed: the ruling left it conditional, and I executed it. None of these is a reason to reject the redesign. Each must be added as a named obligation before the fix seat starts.

### Item by item

**§0 Contamination disclosure; §1 verification table.** AGREE. I independently confirm:
- all six exhibit digests;
- that `faf0ea01` and `422bfca2` carry identical code;
- ParserTests 7/7 OK at `faf0ea01`;
- the shape and key census of ex-03 and the live capture.

**§2 Packet hygiene.** AGREE, including two points: PR #423 is unmerged, so "registered" means the A-R5b text at `ad7565a7`; and the obligations' consumer list never named `epoch_equivalence_check`. I checked `ad7565a7:…rev1.md:652`. Its Predicate wording matches `00-final-texts` line 158 word for word, which matters for M-1 below.

**§3.1 E1, the current parser.** AGREE, BLOCKER. My harness reproduces R2-A and R2-B as `passed=True`, and also X1 (header garbage), X7 (duplicate optional), X9/X10 (unbalanced values), X13 (CRLF) and X14 (no final LF). The ruling's structural diagnosis (wildcard header, a depth counter that runs only at top level, `splitlines`, no value grammar) matches the code at `battery_float.py:24, :93, :113-137`.

**§3.2 E1, the consult grammars.** AGREE. I executed both prototypes unmodified:
- Sol: capture accepted as `(59, 62, 2)`; 20/20 mutations refused.
- Astra: `positives=8/8 negatives=62/62 PASS`.

**§4 E2 grammar: structure, framing, line grammar, value grammar.** AGREE. Executed against my verbatim implementation:

| Case | Result |
|---|---|
| ex-03, live read (sha `c0a40c19…`), `float.ioreg`, `charging-synthetic-from-real.ioreg`, `stale-synthetic-from-real.ioreg` | ACCEPT |
| `malformed-synthetic-from-real.ioreg` | refuse (`token`) |
| R2-A / R2-B / X1 | refuse (`header` / `nested key` / `header`) |
| X7 duplicate optional | refuse (`duplicate key`) |
| X9 / X10 | refuse (`unclosed dict` / `unclosed array`) |
| X13 CRLF, X4/X5 CR smuggle, X6 tab, X17 non-ASCII | refuse (`framing: byte`) |
| X14 | refuse (`framing: final LF`) |
| X11 / X16 | refuse (`tail`) |
| X18 21-digit zero-padded amperage | refuse (`uint64`) |
| A2 depth 65 | refuse (`depth`) |
| A4 `{"A"=,}` | refuse |
| A5 top-level `,` | refuse |
| A3 `{"A"=}`, A6 `({"A"=,"B"=})` | ACCEPT, as the MEMBER rule intends |
| V1 `<>`, V3 busy/retain change, V7 key `a.b`, V9 70 kB line | ACCEPT |
| V2 `<"…">`, V4 `!registered`, V5 uppercase id, V6 nested key with a space, V8 `\n` escape, V10 >1 MiB, V11 non-ASCII | refuse. These are availability-only; none occurs in either real capture. Accepted as the ruling's recorded residual risk. |

**No structural false GO found.** The narrower-class choices (atoms, escapes, lowercase hex) are fail-closed and cost nothing on the two real captures.

**§4 "Required and recorded properties", the clause that optional wrong-type values record `None`. MATERIAL (M-1, my C1).**
- The registered Predicate (`ad7565a7:…rev1.md:652`, identical to `00-final-texts:158`) reads: "A missing, duplicated, **malformed** or unreadable **property** … is not a pass."
- That sentence closes the paragraph that names the 11 properties. Nothing in it limits "malformed" to the four gated keys; only obligations §5.1 (`00-final-texts:87`) narrows it to "required".
- The ruling adopts the narrow reading ("because they are never gated") without saying that it departs from the registered sentence. Executed: X8 `"AppleRawCurrentCapacity" = Yes` is **accepted** by the ruling's grammar and by production. The record then carries `apple_raw_current_capacity_mah: null`, and `delta_q_mah` silently goes null.
- **Required cure.** Either:
  - (a) type-check all seven recorded keys when present (`FullyCharged` `Yes|No`; the other six `[0-9]{1,20}` < 2^64) and refuse otherwise. Cost on this machine: zero, because both captures carry all 11 with exactly these types. Or:
  - (b) state explicitly that the ruling reads "malformed … property" as "required property", and amend the obligations text so that the two documents agree.
- I recommend (a), because it is the reading that cannot be wrong against the registered sentence. "Missing" recorded keys can stay `null` under either option. The registration says each observation "records" them, which is a recording duty, not a gate.

**§4 `-a` question.** AGREE: not for W1, do not ask now. It would re-register the command and the raw format and re-validate every reader, for little gain. The condition for raising it later is correctly stated.

**§4 Test list.** AGREE, with one NIT (N-1). The mutation test says "each of the 12 refusal `raise` sites", but §4's refusal-class list names about 25 classes. The number 12 is not built anywhere. Replace it with "every `raise ProbeError` site in the structural stage, enumerated by AST".

**The grammar-extension paragraph (§4, last paragraph, "a reviewed grammar extension with positive and negative fixtures"). MATERIAL (M-2, my C2).**
- The ruling has no freeze clause.
- Every harvest consumer replays with the *current* `parse` and requires `compare_verdict(record, recomputed) is None` (`battery_float.py:530-543`). A verdict path may be added exactly once (`load_committed_verdict` step 2, a single adding commit).
- `battery_float_module_sha256` is written into the record (`:430`), but **no consumer checks it**. I grepped `scripts/*.py` and `battery_float.py` and found no reader.
- Consequence: an "extension" landed after W1's verdict is committed changes the replay of any slot the old grammar refused. That window becomes permanently unconsumable, because its verdict mismatches and cannot be re-added. A tightening would do the same to a pass.
- **Required cure (one paragraph).** The grammar is frozen for the Revision-5 epoch. Any change to `parse` must carry, in its PR, a replay of every committed Revision-5 verdict with zero `compare_verdict` differences; otherwise it is a registration amendment with an owner ruling. Add a test that pins `sha256(joulewise/battery_float.py)`'s structural stage, or the grammar corpus, so that an unannounced change fails CI.

**§5.1 Sol F1: refuse outright.** AGREE on shape, BLOCKER.
- Executed and confirmed: `REFUSAL_EXIT = 3` (`epoch_equivalence_check.py:121`); `main_args` maps `EquivalenceRefusal` to it (`:716-723`); `run` writes only after `evaluate_session`; `REVISION_FIVE_EPOCH` is importable through the existing `:108` import.
- The refusal site is correct: before `_slot_outcomes`, and therefore before `_read_member_evidence` at `:398`.

**§5.1 reasoning applied to `issue_epoch_continuation.py`. MATERIAL (M-3, my C3); the ruling is internally inconsistent here.**
- The ruling refuses the equivalence tool because registration `:614` says "no PASS continuation branch or FAIL branch for this epoch".
- `scripts/issue_epoch_continuation.py` *is* the PASS continuation branch. Its docstring, `:2-18`: "A continuation lets an unchanged acceptance judge another identity epoch … The EQUIVALENCE NIGHT … judged … against the envelope."
- Yet §6 R2-5 item 3 lists it as merely "gated" (`:86-109`). At `faf0ea01` a Revision-5 session with a `pass` verdict proceeds past that gate to `:133-141` and derives a continuation record, for a branch the registration says does not exist.
- **Required cure.** Apply the identical outright refusal in `derive_record`, before `:108` (the first `_read_member_evidence`), with the same RED/GREEN pair (Revision-5 fixture with a **passing** committed verdict → exit ≠ 0, nothing written, zero member reads). Obligations §4.5 then lists it as refusing, not gated.

**§5.2 Astra M1.** AGREE, MATERIAL. I confirmed `:359-360` (`except battery_float.NoRecord: continue`) by reading, and the docstring claim at `:336-338` is false for an unnamed computed session. The closure and both tests are right.

**§5.3 Runbook flags.** AGREE, MATERIAL.

**§6 E4, licence and stop rule ("any structural false GO → council").** AGREE.

**§6 R2-1 to R2-4.** AGREE, subject to M-1 and M-2 being folded into R2-1 and M-3 into R2-2.

**§6 R2-5 sweep: the enumeration.** AGREE on coverage; I checked it against my Phase 1 grep. Items 1–11 cover every `b_fiducial_s` / `exact_bound_lexeme_s` reader I found.
- Item 1's ordering claim holds: in `_prepare_candidate`, `_select_members` (member reads, `:1700`) runs after the battery block (`:1563-1600`).
- Item 3 needs M-3.
- **N-2 (NIT).** Items 6, 7, 8, 10 and 11 are phrased "confirm …", which leaves a verification without an owner or a test. Make R2-5 deliver a committed test that fails when any `__main__` script matching `b_fiducial_s|exact_bound_lexeme_s` neither calls the battery gate or refusal nor appears on a reasoned exemption list. That turns the sweep into a guard instead of a one-off read.

**§6 R2-5 feeder paragraph (bytes vs text; "Not verified here; MATERIAL if true"). CONFIRMED TRUE, MATERIAL (M-4). It must become a named obligation, not a "show that".**

Read at `faf0ea01`, the text-mode runners are:
- `joulewise/evidence_night.py:674-676`: `probe_command` runs `subprocess.run(…, capture_output=True, text=True, …)`. It is the default `runner` at `:1326`, so it feeds `observe` for **arm_check** (`:1365`) and **publish_install** (`:1788`).
- `scripts/run_night.py:337-358`: `_probe_runner` runs `subprocess.run(…, capture_output=True, text=True, …)`. It feeds the **t0** C3 row (`night_gate.py:1510-1518`).

The byte-preserving sites are:
- `night_agent_install` (runner `None`, so `observe`'s own bytes `subprocess.run`);
- the writer (runner `None`, or a test fixture returning bytes);
- `arm_readiness_evidence_t0._execute_probe`, which reads the tempfile as bytes and then does `.decode("utf-8", errors="replace")`. That decode keeps CR; the `str` branch of `observe` re-encodes, and replacement characters become non-ASCII, which the grammar refuses.

Executed (`/tmp/ref-opus-esc/demo_text.py`). The input is a stdout whose four required keys exist **only** as CR-separated tails inside one string-valued top-level line (`"N" = "a"\r      "ExternalConnected" = Yes\r…`):
- raw bytes → ruling grammar: **refuse** (`framing: byte`);
- through a `text=True` runner → `observe` → the bytes the parser sees contain no CR → **ruling grammar ACCEPT**. The recorded `raw_stdout_sha256` **differs** from the sha256 of the real stdout. `faf0ea01` production also returns `passed=True` on both routes.

So at the three admission sites (arm, publish, t0), the "fail-closed by construction" claim does not hold, and the record's digest is not the digest of the raw standard output that A-R5b says is retained. Harvest is unaffected, because the writer captures bytes. A smuggled admission would therefore surface as `battery_float_evidence_missing` at harvest rather than as a false science result, which is why this is MATERIAL rather than BLOCKER. It is still the escalated signature (wrong structure passing a gate), at the admission gate.

**Required cure.**
- `observe` refuses non-`bytes` stdout: delete the `str` branch at `battery_float.py:216` and raise `ProbeError("probe stdout is not bytes")`.
- The two text-mode runners get a battery-argv branch that captures bytes, or those sites pass `runner=None`.
- Tests:
  - RED at `faf0ea01`: the CR-smuggle bytes through each of the three runners → `passed=True`.
  - GREEN: `probe_error=True`, and `raw_stdout_sha256 == sha256(actual stdout)`.
  - A static test that every `battery_float.observe(` call site's runner yields `bytes`.

**§6 R2-6 independent delta.** AGREE. Add one item: the delta must drive the fresh mutations through the **production runners** (M-4), not only through `parse`/`observe` with a bytes fake. A bytes-only oracle is exactly what hid M-4.

**§6 R2-7 bookkeeping.** AGREE, with N-3 (NIT). Obligations §5.1's `^\s+"Key" = value$` sentence (`00-final-texts:81`) must be replaced by a pointer to the ruling's §4 grammar. Otherwise a later reviewer will hold the six-space whitelist to the looser text, or the reverse.

**§6 "no new decision-log entry".** AGREE only if M-1 is cured by option (a). Option (b) reinterprets a registered sentence and needs an entry.

**Plain summary for Ed.** AGREE: 5 lines, no internal shorthand beyond "Revision 5" and "council", and accurate. After M-4 the claim "tested on two real readings … and 85 broken ones" stays true, but it should add that the reader now also receives the command's exact bytes at every check.

**§7 verdict table.** AGREE with E1, E2 (subject to M-1 and M-2), E3 F1, E3 M1, E3 runbook and E4 (subject to M-3, M-4 and N-2).

### Phase 2 summary

| ID | Severity | Ruling section | Finding | Cure |
|---|---|---|---|---|
| M-1 | MATERIAL | §4 recorded properties | Wrong-type recorded properties are accepted, against the registered "malformed … property is not a pass" (X8 executed) | Type-check all 7 recorded keys (cost zero on real captures), or state the reading and amend the obligations |
| M-2 | MATERIAL | §4 extension clause | No grammar freeze; a post-verdict grammar change permanently strands committed windows; module sha is recorded but unchecked | Freeze for Revision 5; any change replays all committed verdicts with zero diff, else amendment |
| M-3 | MATERIAL | §5.1 / §6 R2-5 item 3 | `issue_epoch_continuation` is the registered-nonexistent PASS continuation branch, but is only gated | Refuse Revision 5 outright there too, with a passing-verdict RED/GREEN |
| M-4 | MATERIAL (confirmed) | §6 R2-5 feeders | `text=True` runners at arm, publish and t0 let CR-smuggled keys pass the new grammar and record a non-raw digest (executed) | `observe` refuses `str`; bytes runners for the battery argv; three-runner RED/GREEN |
| N-1 | NIT | §4 tests | "12 raise sites" is an unbuilt number | Enumerate by AST |
| N-2 | NIT | §6 R2-5 | "confirm …" items have no test | Committed guard test with an exemption list |
| N-3 | NIT | §6 R2-7 | Obligations §5.1 `\s+` text left standing | Replace with a pointer to §4 |

No BLOCKER against the ruling itself. Its BLOCKERs (E1, F1) stand.

**Scratch.** `/tmp/ref-opus-esc` (export of `faf0ea01`, harnesses, the live read) is removed at the end of this session. The consult seats' `/tmp` files were not created by me and are left in place.
