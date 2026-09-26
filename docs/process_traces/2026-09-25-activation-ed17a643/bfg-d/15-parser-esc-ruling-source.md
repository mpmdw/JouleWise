# Cold-gate ruling BFG-D-PARSER-ESC-01 (Fable 5.1, cold judge)

Written 2026-09-25 ≈21:05 PDT from worktree `/Users/edr/code/JouleWise-wt-ed17a643-cg-pe` at `783e46ac`. Single foreground session; no background tasks, subagents or watchers. Read-only except `/tmp` scratch (removed at the end).

**Verdicts.** E1 AFFIRM (both round-2 defects reproduce at `faf0ea01`; both consult grammars accept the real capture and refuse every counterexample they list; BLOCKER). E2 issued below as exact final text; `-a` is not to be requested for W1 and not recommended now. E3: Sol F1 AFFIRM BLOCKER, closure = refuse Revision-5 sessions outright; Astra M1 AFFIRM MATERIAL; runbook flags AFFIRM MATERIAL. E4 issued below. Under charter §9 this round is licensed because it is a redesign (grammar replacement), not a third same-shape patch; the licence ends if the round-2 delta finds any structural false-GO.

## 0. Contamination disclosure

I read: the charge and its six exhibits; `docs/process/coldgate_charter.md` and `docs/process/coldgate_charter_registry.md`; the BFG-D branch code at `faf0ea01` (`git show`, and a detached `/tmp/cg-pe-faf0` worktree); the BFG-D trace directory at `422bfca2` (obligations v1.1 `06-…`, fix contract `12-…`, seat report `13-…` header only); packets `../10-coldgate-packet-bfg/` and `../41-coldgate-packet-harvest-final/` (ruling files and charge, grep-bounded); `docs/decision_log.md` at `faf0ea01` lines 12140-12217 (A-R5b-1 entry); the A-R5b amendment text at `ad7565a7` (PR #423's head, `configs/calibration/preregistration_d079_epoch_25g83_rev1.md:648-664`); `gh pr view 423` metadata. I also read and executed the two consult seats' scratch prototypes still on disk (`/tmp/bfg_design_check.py`, `/tmp/ed17a643/esc/astra-consult/grammar_probe.py`) and the two delta seats' repro scripts (`/tmp/bfgd_delta_probes.py`, `/tmp/bfg-delta-astra-ub8g2ihp/delta_repros.py`); these are not in the manifest and are treated as code I verified, not as exhibits. I ran `/usr/sbin/ioreg -r -c AppleSmartBattery` once (read-only) for a second real sample. I did not read RUN_STATE, TASK_QUEUE, council logs, run reports, memory, or any other process trace. I carry the standing knowledge that I ruled packets 10 and 41 as the cold judge; I re-verified everything cited here rather than relying on those texts.

## 1. Verification before the merits

| Item | Expected | Observed | Method |
|---|---|---|---|
| Charter digest | `099de884b1d081ffa547dfd8ff5837e75813a870ff8c7285c749c1b440c95d81` (charge) and the same value in `docs/process/coldgate_charter_registry.md:16`, which is independent of the packet | `099de884…c95d81` | `shasum -a 256 docs/process/coldgate_charter.md` |
| Exhibit manifest | six digests in the charge | all six match | `shasum -a 256 ex-*` |
| BFG-D candidate | `faf0ea01` | exists, type commit; branch tip `origin/feat/2026-09-25-bfg-d` = `422bfca2`; `faf0ea01` → `1fda46c1` (adds `14-delta-charge.md` only, `git diff --stat`) → `422bfca2` (adds the two delta reports). The delta seats' `head_start` `1fda46c1` is therefore code-identical to `faf0ea01`. | `git cat-file -t`, `git log`, `git diff --stat faf0ea01 1fda46c1` |
| Real capture ex-03 | — | 17337 bytes, 64 LF-terminated lines, 0 CR, 0 TAB, 0 non-printable bytes; header line, `    {`, 59 property lines at exactly six spaces, `    }` at line 62, then a four-space line and an empty line | Python byte census |
| Second real capture (live, 21:00 PDT) | — | 17352 bytes, same 64-line shape, same 59 keys, same value categories (34 uint, 10 Yes/No, 6 inline dict, 5 tuple, 3 string, 1 hex data), no atom other than `Yes`, `No`, or an unsigned integer anywhere, no backslash anywhere, three empty nested values (`"K"=,`), one key outside `[A-Za-z0-9_]` (`built-in`) | same census on `/tmp/cg-pe-scratch/live.ioreg` |
| Existing tests | — | `tests.test_battery_float.ParserTests`: 7 tests OK at `faf0ea01` | focused unittest |

## 2. Packet hygiene (charter §6)

- **PR #423 is OPEN, not merged** (`gh pr view 423`: state OPEN, no merge commit). The charge says "Registration A-R5b (PR #423) names that exact command"; the text does (`ad7565a7:…rev1.md:652`), but it is an unmerged amendment. Effect: none on E2's argv question (the branch is built to that text and both consults treat it as fixed), but the ruling's "registered" below means "registered in the A-R5b text at `ad7565a7`". `faf0ea01` itself contains no `ioreg` string in `configs/` (grep), so the argv is registered only in code (`battery_float.py:18`) plus the open PR.
- **The consult exhibits are arguments**, as the charge says. Their executed evidence is re-established here from their on-disk scratch files, whose outputs match the exhibits' V1 tails exactly (Sol: `capture: (59, 62, 2)`, 20 mutations refused; Astra: `positives=8/8 negatives=62/62`, both baseline false-GOs reproduced).
- **Compound questions.** E3 bundles three items and E4 bundles a plan with a sweep. Ruled per sub-item.
- **One omission that matters for E4:** the packet does not say that obligations v1.1 §4.5 (`06-…:170-174` at `422bfca2`) lists only three "other consumers" (dry run, cadence report, continuation tool) and never names `scripts/epoch_equivalence_check.py`; nor does the runbook's §2.2a list (`:2532-2534`). Sol F1 is therefore not a regression of fix round 1 but a gap in the obligations' consumer enumeration. That is exactly why E4 needs a sweep with a named list rather than another contract-item fix.
- No cherry-picking or asymmetric treatment found. The lead labels no disposition on the merits; it poses questions.

## 3. E1 — verified: the round-2 defects and the two consult grammars. AFFIRM. Severity BLOCKER.

**3.1 The current parser (`joulewise/battery_float.py` at `faf0ea01`).** Executed in `/tmp/cg-pe-faf0` with the real capture ex-03 and a wall time one second after its `UpdateTime`:

| Case | Result at `faf0ea01` | Why (file:line) |
|---|---|---|
| real capture ex-03 | parse OK, `passed=True` | — |
| **R2-A**: only `<class AppleSmartBattery,` → `<class OtherBattery,` | **parse OK, `passed=True`** | `_HEADER = rb'^\+-o AppleSmartBattery  <[^>\r\n]+>$'` (`:24`) authenticates the object name only; anything inside `<…>` is accepted |
| **R2-B**: `"Outer" = {` / `"Inner" = {` / `}` / four required keys, all at six spaces, outer never closed | **parse OK, `passed=True`** | `"Outer" = {` increments `nested_depth` (`:135-136`); `"Inner" = {` is skipped by `if nested_depth: continue` (`:126-127`) BEFORE the `endswith(b" = {")` increment, so the inner `}` (`:116-120`) returns depth to 0 and the required keys are recorded as top level |
| R2-B with the required keys at eight spaces | refused ("inconsistent top-level indentation") | the indentation check, not the structure check, catches it |
| round-1 cases (missing `}`, `+-o OtherBattery`, keys only in a nested dictionary) | refused | fix round 1 closed the three literal counterexamples |
| header `<anything at all,…>` | passed | same as R2-A |
| CRLF line endings | passed | `raw.splitlines()` (`:93`) strips `\r` |
| duplicate optional key (`Amperage` twice) | passed, value silently dropped | `values` keeps only singletons (`:148`); no refusal |
| blank line inside the block | passed | `if stripped and not nested_depth` (`:123`) skips blank lines |
| unbalanced inline brace `{{"CarrierModeLowVoltage"…` | passed | no value grammar at all |
| second object appended, header only, empty stdout, 8-space closing brace, quoted `UpdateTime`, trailing text after a value | refused | — |

Astra's delta script, re-run here, shows both R2 cases reaching `evaluate_night` GO, `evaluate_dynamic_hard` PENDING with no refusal, and `validate_window` `pass` (`/tmp/cg-pe-scratch/astra_repro.out` lines 1-8). A-R5b "Predicate" (`ad7565a7:…rev1.md:652`) requires "exactly one AppleSmartBattery object" and reading "only from that object's top-level property lines"; R2-A is not an AppleSmartBattery object and R2-B reads keys that are not top level. Both are false GOs. AFFIRM; BLOCKER.

**Structural diagnosis (why the signature repeated).** The parser infers structure from partial matches and carries state across physical lines: a header regex with a wildcard where the class field is; a depth counter driven by one suffix test that runs only at top level; `splitlines()`; no grammar for the value side of a property line. Fix round 1 patched the three literal counterexamples and its regression tests are those same three inputs (`tests/test_battery_float.py:30-49`), so the test oracle could not see a fourth. Charter §9 applies: the next spend is a redesign, and both consults independently propose the same one.

**3.2 The consult grammars, executed.** Sol's prototype (`/tmp/bfg_design_check.py`): accepts ex-03 as `(59 properties, close at line 62, 2 trailing lines)`, refuses all 20 listed mutations, and accepts the live capture. Astra's prototype (`grammar_probe.py`): 8 positives accepted, 62 negatives refused, ex-03 accepted with the four required values as reported, live capture accepted with 59 properties. Both refuse R2-A and R2-B. AFFIRM the packet's statement that each grammar accepts ex-03 and refuses every counterexample it lists.

**Differences between the two, and how E2 resolves them.** Sol's atom class `[A-Za-z0-9_+.-]+` admits `-1`, `1.5` and bare words; Astra's `Yes|No|[0-9]+` matches what both real captures contain. Sol allows escapes `\n \r \t`; Astra allows only `\"` and `\\`; no real capture contains a backslash. Sol's hex id and data accept uppercase; Astra's id is lowercase but data accepts uppercase; both real captures are lowercase only. Sol's key class starts with a letter; Astra's `[A-Za-z0-9_][A-Za-z0-9_.-]*` also covers `built-in`. E2 takes the narrower reading in each case (fail-closed by construction; a future legitimate variant refuses a window rather than passing a wrong one, and the raw bytes are retained so the variant can be reviewed).

## 4. E2 — the parser grammar (exact final text)

**Construction rule.** The whole stdout is checked as a sequence of physical lines, each of which must fullmatch exactly one line type determined by position and by a two-state machine (BODY, TAIL). No state other than "which line type is expected next" and the set of top-level keys seen crosses a line boundary. Nested structure exists only inside one property line's value and is checked by a recursive-descent function that must consume the value to its last byte. Any byte, line, token or count outside the whitelist raises `ProbeError`; the observation is then `probe_error=True, passed=False` (`observe`, `:228-254`), a slot is `battery_float_evidence_missing` (`validate_window` E5, `:345-350`), and the gate refuses `night_probe_error`. Predicate evaluation runs only after the whole document is accepted.

**Byte framing (checked first, on the raw bytes).**
1. `raw` is `bytes`, non-empty, at most 1 048 576 bytes.
2. Every byte is `0x0A` or in `0x20..0x7E`. This refuses CR, TAB, NUL, other controls and every non-ASCII byte.
3. `raw` ends with `0x0A`. Split on `b"\n"` only (never `splitlines()`, never `strip()`, never text decoding before the check). The final empty element after the last LF is discarded; nothing else is.

**Line grammar (Python `re`, bytes, `fullmatch` on every line).**
```
HEADER   = \+-o AppleSmartBattery  <class AppleSmartBattery, id 0x[0-9a-f]+, registered, matched, active, busy [0-9]+ \([0-9]+ ms\), retain [0-9]+>
OPEN     = the exact bytes b"    {"            (four spaces)
PROPERTY = {6}"([A-Za-z0-9_][A-Za-z0-9_.-]*)" = (.+)      i.e. exactly six spaces, KEY, one space, '=', one space, VALUE (non-empty)
CLOSE    = the exact bytes b"    }"
TAIL     =  *                                   (zero or more spaces)
Document = HEADER  OPEN  PROPERTY+  CLOSE  TAIL*
```
- Line 1 must fullmatch HEADER; line 2 must equal OPEN. In BODY, a line equal to CLOSE moves to TAIL; every other BODY line must fullmatch PROPERTY. In TAIL every line must fullmatch TAIL. EOF in BODY refuses ("close"). A PROPERTY line longer than 262 144 bytes refuses.
- A key already seen at top level refuses ("duplicate key"), whether required, optional or unknown, and whether the values agree.
- The two-space gap between `AppleSmartBattery` and `<` in HEADER is literal (ioreg prints two spaces).

**Value grammar (recursive descent over VALUE; cursor must end at `len(VALUE)`; nesting depth at most 64).**
```
VALUE  := BOOL | UINT | STRING | DATA | ARRAY | DICT
BOOL   := 'Yes' | 'No'
UINT   := [0-9]+
DATA   := '<' ([0-9a-f]{2})* '>'
ARRAY  := '(' [ VALUE (',' VALUE)* ] ')'
DICT   := '{' [ MEMBER (',' MEMBER)* ] '}'
MEMBER := KEY '=' [ VALUE ]          -- the VALUE may be absent only when the next byte is ',' or '}' (ioreg prints "AdapterPower"=, for members it cannot serialise; three occur in every real capture)
STRING := '"' ( any byte 0x20..0x7E except '"' and '\' | '\"' | '\\' )* '"'
KEY    := '"' [A-Za-z0-9_][A-Za-z0-9_.-]* '"'
```
No whitespace anywhere in a VALUE outside a STRING. Duplicate keys inside one DICT refuse. `BOOL` is tried before `UINT` only in the sense that the token regex is `Yes|No|[0-9]+`; nothing else is an atom (no sign, no decimal point, no bare word, no square bracket).

**Required and recorded properties (after structural acceptance).**
- `ExternalConnected`, `IsCharging`, `InstantAmperage`, `UpdateTime` must each be present exactly once at top level (the duplicate rule above already guarantees "at most once").
- `ExternalConnected` and `IsCharging` must be exactly `Yes` or `No`. `InstantAmperage` and `UpdateTime` must fullmatch `[0-9]{1,20}` and be below 2^64; `InstantAmperage` is read as n − 2^64 when n ≥ 2^63. The existing `_unsigned`/`_signed` (`:75-86`), the 200 mA and 180 s rules (`:151-157`, `:175-176`) and the record fields are unchanged. `object_count` stays 1.
- Optional recorded keys (`Amperage`, `Voltage`, `Temperature`, `FullyCharged`, `CurrentCapacity`, `AppleRawCurrentCapacity`, `AppleRawMaxCapacity`): a duplicate refuses (structural rule); a present key with a structurally valid value of the wrong type records `None` as today (`:163-169`), because they are never gated.
- `property_lines` (`:179`) keeps the verbatim top-level lines of the required and optional keys.

**Refusal classes (each is a `ProbeError` with the stated reason prefix; the test list names one input per class).**
framing: type/size; framing: byte; framing: final LF; header; open; close; line N: length; line N: property (wrong indentation, malformed key, missing or doubled spaces around `=`, empty value, blank or space-only line inside the block, escaped quote in a top-level key); line N: duplicate key; line N: tail (anything non-space after CLOSE: trailing garbage, a property, a second object, an extra `}`); line N: value suffix (bytes remain after a complete value: two values, a second assignment, trailing space, `0}`); nested key; duplicate nested key; unclosed string; escape; unclosed dict; unclosed array; token (bad hex, odd hex, uppercase hex, `[`, sign, decimal, bare word, trailing comma, empty element); depth; required K; boolean; uint64.

**Reference implementation.** The grammar above was implemented verbatim as `/tmp/cg-pe-scratch/grammar_fable.py` (about 80 lines, stdlib only, no cross-line state) and run against the corpus below: 11 positives accepted, 85 negatives refused, zero failures. The same 85 negatives were fed to `battery_float.parse` at `faf0ea01`: 47 of them still return `passed=True` there (listed in the scratch output; they include both R2 cases, Sol's `outer_map_unclosed`, header garbage, CRLF, every inline-delimiter fault, duplicate optional keys, blank body lines and every bad atom). The fix seat may take this implementation or either consult's; the grammar text above is the authority, not any prototype.

**Test list (all as repository tests; RED at `faf0ea01` where marked).**
- Positives: ex-03 real capture (add as `tests/fixtures/battery_float/float-2026-09-25-2047.ioreg`, with its sha256 `5824752…851631` in the README); the existing `float.ioreg`, `charging-…` and `stale-…` fixtures (all accepted by the grammar); minimal four-property object; reordered properties; nested empty RHS `{"A"=,"B"=0,"C"=}`; string containing `{(< >)}` and both escapes; empty containers `({},(),<>,"")`; nested shadow names (`{"ExternalConnected"=No,…}` inside a value must not satisfy or contradict the top-level keys); trailing space-only and empty lines; hyphen key `built-in`; `18446744073709551458` → −158 mA pass.
- Negatives (RED at `faf0ea01` marked †): R1 missing close, other object name, required only in nested multiline dict, trailer; R2-A class field †; R2-B early depth return †; R2-B same-indent variant †; Sol's outer-map-unclosed †; header garbage †, class suffix †, extra class field †, uppercase hex id †; leading blank line; required only nested inline; duplicate required; duplicate optional †; duplicate unknown †; duplicate nested key †; escaped quote in top key; escaped quote in nested key †; alias `AppleRawExternalConnected`; alias `Amperage`; missing required; CRLF †; bare CR †; tab indent; tab in string †; NUL; non-ASCII †; vertical tab; missing final LF †; empty; header only; header+open only; empty object; 1 MiB+ stdout †; 262 145-byte line †; depth 70 †; trailing garbage; property after close; second object; extra close; missing open; open indent wrong; close indent wrong; all properties at 8 spaces †; one property at 8 spaces; blank line in body †; space-only line in body †; trailing space after value; two spaces around `=`; no spaces around `=`; unclosed inline dict (synthetic and in the real capture) †; mismatched delimiter (both) †; extra `{` †; delimiter underflow †; unclosed quote (both) †; dangling escape †; bad escape †; bare garbage †; balanced garbage †; two values †; second assignment on a line †; empty top value; empty array element †; array trailing comma †; dict trailing comma †; odd hex †; bad hex †; uppercase hex data †; square array †; negative atom †; float atom †; bare word atom †; uint overflow; signed lexeme; quoted required; nested required value; bool as `0`; lowercase bool; 21-digit `UpdateTime`; the existing `malformed-synthetic-from-real.ioreg`.
- Every negative is asserted at four sites: `parse` raises `ProbeError`; `observe` (fake runner returning the bytes with exit 0) records `probe_error=True, passed=False`; `night_gate.evaluate_night` and `evaluate_dynamic_hard` refuse with `night_probe_error`; `validate_window` on a session whose pre or post raw file holds the bytes reports `battery_float_evidence_missing` (never `pass`, never `confounded`).
- Predicate boundaries stay as today: ±200 pass, ±201 fail, age 180 pass and 181 refuse, `IsCharging = Yes` fails.
- One mutation test on the parser itself: delete or replace each of the 12 refusal `raise` sites in turn and assert that at least one corpus negative is accepted (a guard against a future "helpful" relaxation).

**The `-a` (plist) question.** Not required for W1, and the owner should not be asked now. Reasons: (1) the text route with this grammar closes the defect class by construction, verified on two real captures; (2) `-a` changes the registered command in A-R5b (an open PR), the retained raw format (`raw/battery_float.*.ioreg` bytes and their digests in the hashed evidence, A-R5b "Per-slot evidence"), and every reader of that format, which is a registration amendment plus a re-validation of the writer and all consumers before W1; (3) a plist parser would still need exact object, type, uniqueness and count checks, so it removes little bespoke code. Sol's G3 and Astra's argv row agree it is not a dependency. The one condition under which an amendment should be raised later: a legitimate ioreg text output is refused by this grammar on a real window (the raw bytes will show exactly which rule), in which case the choice is between a reviewed grammar extension with positive and negative fixtures and a registration amendment to `-a`; either goes through the owner and a gate. Record Sol's F1 residual risk as accepted: the whitelist is validated on two captures from one machine.

## 5. E3 — the other delta items

**5.1 Sol F1 (`scripts/epoch_equivalence_check.py`). AFFIRM. BLOCKER. Closure: refuse Revision-5 sessions outright.**
Reproduced: with the Revision-5 fixture from `tests/fixtures/epoch_bootstrap/build.py` (`build_derivation_ledger(…, [Slot('0.03')], verdict_records=False)`), whose row epoch equals `REVISION_FIVE_EPOCH`, the tool exits 5 and writes an output record whose `slot_outcomes` carries `b_fiducial_s = '0.03'` with no verdict file present; the same happens with `verdict_records=True`, and the tool has no `--preregistration-sha256` argument at all (parser `:672-712`). The read is `_slot_outcomes` (`:398` `_read_member_evidence`, `:405` `evidence.get("b_fiducial_s")`, `:413` written to the record), with no battery check anywhere in the file (grep `battery`: none). A-R5b "Window verdict" says the check happens "before the cadence report, before the count-only dry run and before any B value is read"; this tool reads and prints B.
Why refuse rather than gate: the registration text that governs this epoch says "Revision 2's equivalence look is NOT taken for this epoch" (`faf0ea01:configs/calibration/preregistration_d079_epoch_25g83_rev1.md:614`; the tool's own docstring `:2-9` binds it to directive 316 and the r6 envelope). There is no legitimate run of this tool on a Revision-5 session, so a gate would build and test a verdict-loading path whose only use is forbidden. Refusal shape: in `evaluate_session` (or at the top of `_slot_outcomes`), before any `_read_member_evidence` call, if any finalized row's `dict(row.identity_epoch) == REVISION_FIVE_EPOCH` (import the constant from the issuer module, which the file already imports from at `:108`), raise `EquivalenceRefusal("revision_five_session: the equivalence look is not taken for epoch 25G83/v3 (registration Revision 5); this tool does not judge it")`, which exits 3 and writes nothing (`run` `:634-638` writes only after `evaluate_session` returns). Runbook §2.4-area text at `:2845-2872` gains one sentence saying the tool refuses Revision-5 sessions and why.
Tests: RED at `faf0ea01`: Revision-5 fixture → expect exit 3, no `--out` file, `_read_member_evidence` never called (patch it to raise); the existing 26 tests in `tests/test_epoch_equivalence_check.py` (none Revision-5) stay green; a session with zero finalized rows is unaffected.

**5.2 Astra M1 (`_dry_run_epoch_bound`, `scripts/issue_calibration_acceptance_generation.py:332-368`). AFFIRM. MATERIAL.**
Reproduced with Astra's script: W1, W1-prime, W2 all clean and recorded; W1's committed verdict deleted from the working tree; `check --session-ids W1-prime --session-ids W2` exits 0 with `registration admissible for prepare-candidate: yes`, while `prepare-candidate` exits 3 refusing W1. Cause: `except battery_float.NoRecord: continue` at `:359-360`. The docstring's justification (`:336-338`, "its own line already carries a blocker") is false for a computed session that is not named: no line is emitted for it. FX-6's principle (the dry run agrees with `prepare-candidate`) is violated for authentication failures.
Closure: replace `continue` with `blockers.append(f"computed session {candidate_id}: battery harvest verdict missing or uncommitted ({missing.reason})")` and keep iterating; the function returns those blockers with the others. No B-bearing read is involved.
Test: RED at `faf0ea01`: Astra's fixture as above → non-zero exit, `registration admissible … : no`, blocker text names W1 and the reason `working tree differs from HEAD`; `prepare-candidate` still exits 3 with the same reason. Also: a computed session recorded with a wrong `preregistration_sha256` produces the same blocker (`NoRecord("identity mismatch: preregistration_sha256")`).

**5.3 Runbook flags (Sol F2 = Astra M2). AFFIRM. MATERIAL.**
Verified at `faf0ea01:docs/phase_2/derivation_night_runbook.md`: §2.2 `:2495-2496` passes only `--session-ids`; §4.1 `:2950-2952` passes `--preregistration` and `--session-ids` but no `--preregistration-sha256`; `:2956` promises rc 0. Both shapes exit 5 on a Revision-5 fixture with the blocker `--preregistration and --preregistration-sha256 are required` (reproduced by both delta seats' scripts and re-run here). The correct shape already exists at `:2585-2588` (§2.2a step vii).
Closure: both invocations carry `--preregistration configs/calibration/preregistration_d079_epoch_25g83_rev1.md --preregistration-sha256 "$PREREGISTRATION_SHA256"`; §2.2's prose says both flags are required for any Revision-5 session and that rc 5 without them is the flag blocker, not a window fault; §4.1's expected-result paragraph adds the two new blocker classes (verdict missing or uncommitted; verdict cannot be re-established) to its list of rc-5 causes.
Test: a light-tier doc test that extracts every fenced `issue_calibration_acceptance_generation.py check` invocation containing `--session-ids` from the runbook and asserts both flags are present (RED at `faf0ea01`: two of four fail); plus the executed shape test the seats already wrote (each documented shape, on the Revision-5 fixture, exits 0).

## 6. E4 — fix-round-2 plan

Licence: charter §9 permits this round because the parser change is a redesign under a grammar the cold gate has fixed, not a third patch of the same shape. The seat that implements it must not be the seat that wrote the round-1 parser, and the delta reviewer must not reuse the corpus as its only oracle (see R2-6). If the round-2 delta finds any structural false GO, stop: the next step is council, not round three.

Ordered obligations (each: RED on `faf0ea01` in a `/tmp` copy, paste RED then GREEN; focused tests only):
- **R2-1 Parser grammar** (§4). Replace `parse`'s structural stage with the grammar; keep the predicate stage. Tests: the corpus of §4 at the four sites; the parser mutation test; the new real-capture fixture. Acceptance: all 85 negatives refused, all 11 positives accepted, `ParserTests`, `GateTests`, `WindowTests` green.
- **R2-2 Equivalence tool refuses Revision 5** (§5.1). Tests as stated.
- **R2-3 Dry-run bound propagates NoRecord** (§5.2). Tests as stated.
- **R2-4 Runbook §2.2 and §4.1** (§5.3). Doc test plus executed shapes.
- **R2-5 Same-signature sweep** (the enumeration is the deliverable; every row gets file:line, what it reads or decides, the gate it sits behind, and the test that proves the gate; any row without a gate becomes an obligation with the R2-2 or R2-3 shape). Framing: B is loaded into memory by every ledger snapshot (`exact_bound_lexeme_s` on each row, written at finalization by `calibration_ledger.py:6040-6077`), so the obligation A-R5b imposes is on outputs and decisions, not on memory: no B lexeme may be printed, written to any file, compared, or used in a decision for a Revision-5 session before an authentic committed verdict is loaded, and never for a non-pass window.
  Readers of B-bearing evidence reachable for a Revision-5 derivation session, as found by `git grep` at `faf0ea01` over `joulewise/` and `scripts/` (tests excluded):
  1. `scripts/issue_calibration_acceptance_generation.py` `registration_dry_run` `:285` (gated `:233-280`, FX-5); `_dry_run_epoch_bound` `:355` (R2-3); `_prepare_candidate` member read `:1205,:1222` (gated `:1563-1600`); `battery-verdict` writer `:1404-1460` (reads raw battery bytes only).
  2. `scripts/calibration_cadence_report.py` `:81-96` (gated; reads plists, not B).
  3. `scripts/issue_epoch_continuation.py` `:86-109` gate, `:133-141` read.
  4. `scripts/epoch_equivalence_check.py` `:398,:405,:413` — ungated (R2-2).
  5. `joulewise/calibration_epoch_continuation.py` `:94-112,:250-264` — validates a continuation record's lexemes; confirm it is reachable only through the gated tool's output.
  6. `scripts/calibration_ledger_backfill.py` `:44-80` — reads evidence `b_fiducial_s` to build rows; confirm it cannot run on a Revision-5 custody root, or refuse as R2-2.
  7. `scripts/reissue_calibration_acceptance.py` `:180-205` — reads members' evidence; members come from an issued acceptance; confirm no Revision-5 path before issuance.
  8. `scripts/check_paper_round7_artifacts.py`, `scripts/check_paper_replay_fence.py`, `scripts/paper_anchor_correction_quantified.py`, `scripts/paper_excursion_decomposition.py` — paper tools over historical corpora; confirm each is pinned to pre-A-R5b captures by path or id.
  9. `joulewise/calibration_ledger.py` `:3059` (lexeme extraction at finalization) and `:6040-6077` (writer path) — writer side, before harvest; not a consumer; confirm nothing prints B there.
  10. `joulewise/calibration_bracketing.py`, `joulewise/controller.py:438`, `joulewise/reduce.py`, `joulewise/whole_window.py`, `joulewise/detection_floor.py`, `scripts/run_campaign.py:2112`, `scripts/validate_powermetrics_fiducial.py:514-520,:1290-1299` — consumers of an ISSUED acceptance or of a measurement window's own evidence; confirm none reads a derivation session's B before issuance.
  11. `scripts/sim_acc_25g83_rev5.py` `:109` — synthetic values; confirm it never opens custody.
  Consumers of the verdict (must load it through `load_committed_verdict` with the registration digest, refuse on `NoRecord`, `CustodyFailure` and `compare_verdict` disagreement): `check` dry run `:233-280`; `_dry_run_epoch_bound` `:346-368`; `_prepare_candidate` `:1563-1600`; cadence report `:80-96`; `issue_epoch_continuation` `:86-109`; the runbook invocations §2.2, §2.2a, §4.1 and `docs/process/NIGHT_HANDBACK.md:182`; the arm-record item 6 lines (runbook `:2407`).
  Feeders of `parse` at t0, arm and harvest (all one home; the grammar covers them, but each must pass BYTES, not text): `night_gate.py:1515`, `evidence_night.py:1365,:1788`, `night_agent_install.py:1221`, `arm_readiness_evidence_t0.py:1877`, `validate_powermetrics_fiducial.py:2173` (writer), `run_night.py:343` (timeout), and `observe`'s `str` branch (`battery_float.py:216`), which re-encodes text a runner already decoded. Sweep obligation: show that the production runner used at each site captures `stdout` as bytes; if any captures text, universal-newline decoding happens before the grammar sees the bytes, which would let a CR-bearing output through as LF. Not verified here; MATERIAL if true.
- **R2-6 Independent delta.** The round-2 delta reviewer runs the §4 corpus AND authors at least ten fresh structural mutations not in the corpus (their own oracle), drives each through the four sites, and re-runs the Revision-5 fixtures for R2-2 and R2-3. The reviewer must be a different model family from the implementing seat.
- **R2-7 Bookkeeping.** Fixture README gains the ex-03 capture line; obligations v1.1 §4.5's consumer list gains `epoch_equivalence_check` with its refusal; the decision log needs no new entry (A-R5b text unchanged).

**Plain summary for Ed (5 lines).**
The battery check that decides whether a window counts reads the output of one Apple command as text. Its reader accepted two malformed outputs as "all good" for the second time in a row, so instead of patching it again this ruling fixes an exact allow-list format that the reader must match byte for byte, tested on two real readings from your Mac and 85 broken ones.
A second tool (the old "epoch equivalence" checker) could print battery-window results before the battery verdict existed; it will now refuse such windows outright, since Revision 5 says that check is not used.
Two smaller fixes: the pre-check must say "not admissible" when a computed window's verdict is missing, and two runbook commands need the two registration flags.
Nothing changes in the registered command; switching to plist output is not needed for W1 and is not requested.
If the next review finds the reader accepting a malformed output again, work stops and goes back to council.

## 7. Verdict and severity summary

| Question | Verdict | Severity | Load-bearing evidence |
|---|---|---|---|
| E1 defects real | AFFIRM | BLOCKER | `battery_float.py:24,:116-136`; executed R2-A/R2-B `passed=True`; gate GO/PENDING; window `pass` |
| E1 consult grammars | AFFIRM | — | both prototypes executed: ex-03 and live accepted; all listed counterexamples refused |
| E2 grammar | issued (§4) | — | reference implementation: 11/11 accepted, 85/85 refused; 47 of the 85 pass at `faf0ea01` |
| E2 `-a` | not for W1; do not ask now | — | A-R5b `:652,:656` (registered command and raw format); both consults |
| E3 Sol F1 | AFFIRM, refuse outright | BLOCKER | `epoch_equivalence_check.py:398-413`; no battery flag; registration `:614` |
| E3 Astra M1 | AFFIRM | MATERIAL | `:359-360`; check 0 vs prepare 3 |
| E3 runbook | AFFIRM | MATERIAL | `:2495-2496`, `:2950-2956`; rc 5 both shapes |
| E4 plan | issued (§6) | — | sweep list from `git grep` at `faf0ea01` |

**Disagreements with the lead's labeled disposition.** None labeled; the charge poses questions. Where I differ from the consults: narrower atom, escape and hex classes than Sol; lowercase-only hex data unlike Astra; Astra's "ask the owner for a future `-a` migration" is not adopted now (§4, last paragraph). The R2-5 bytes-vs-text item is my own and unverified.

## 8. Scratch cleanup

`/tmp/cg-pe-faf0` (detached worktree) removed with `git worktree remove --force`; `/tmp/cg-pe-scratch` removed. The consult and delta seats' `/tmp` files were not created by this session and are left in place.
