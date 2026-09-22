# A267 fix round 2 — delta re-audit, CONTRACT LENS (Fable, read-only)

Head `56ea8ae0`, `/Users/edr/code/JouleWise-wt-a267-review2` (tree clean before and after). Authority order: sealed ruling 10 > synthesis 15 / addendum 16 > brief 09. Single module at head: `Ran 108 tests in 12.300s OK`. No mutations run by this lens; the seat's kills were read, not re-run.

## Findings

**BLOCKER: none.**

**SHOULD-FIX: none.**

**NIT 1 — item 8 (S2), `joulewise/quiet_predicate_campaign.py:476-478`.** The added `timed_log_window_epoch_s` paragraph claims: "`log show` is handed the same strings and has the same choice to make, so the record and the query agree either way." The ruling dictated only that the naive parse "resolves an ambiguous daylight-saving fall-back hour to its first occurrence, and the ruled argv strings carry the same ambiguity." String agreement is established; epoch agreement is not — nothing shows how `log show` resolves a fold-ambiguous string. Failure scenario: `log` resolves `01:30:00` to the second (PST) occurrence, Python to the first (PDT); `window_argv_epoch_s` names an interval 3600 s earlier than the one queried, and the docstring says they agree. Cure: delete the clause or say the choice `log show` makes is not established. Docstring-only.

**NIT 2 — against the RULED text of item 5, not the seat (`:766`).** The dictated `temporary.unlink(missing_ok=True)` sits unguarded inside `except OSError`. If the temp was written, `os.replace` then fails with EACCES (directory made unwritable between the two calls), `unlink` raises the same EACCES, escapes `record_attestation`, and `execute`'s outer `except OSError` (`:1183`) leaves `outcome = "refused"` (`:1079`) — one envelope's annotation refuses the NIGHT, contradicting the comment at `:752-757`. Narrow; the seat correctly implemented the ruling verbatim (a guard would have been a deviation). Record for a future round.

**NIT 3 — process.** Supplementary S1–S3 exist only in synthesis 15 and an 11:38 resume message (record 01 step 24); brief 09 on disk (11:24) carries none. Append S1–S3 to brief 09 as a dated addendum.

**NIT 4 — `tests/fixtures/qpe01_pilot_n1_20260922/SOURCES.md`.** Describes only exhibit D; the two syslog fixtures are unrecorded. Deviation 4 is correct (outside WRITE_SCOPE); the magistrate owns the follow-up.

## Specific questions

**(a) Guard constant.** Byte-identical to the ruling's literal: `'Timestamp                       (process)[PID]'`, 46 chars, 23 spaces (brief's "31" was wrong; ruling governs). D3 first line right-stripped == constant (four trailing spaces, `da1b28ef…718b`, 51 B); D2 likewise (`dba7fb7c…eb63`); both digests equal the 07c captures and the test pins (`test:614-615`). The whole ruled block (comment + constant + function) is VERBATIM (`diff` empty). Compact first line → False.

**(b) R2.5 and Deviation 2.** The seat's reading is right. At the `attest_network_time` level, R2.3 (compact → 12 × `asserted`, reason `timed log query returned no header`) and the NIT's "state equal" are jointly unsatisfiable: the syslog twin can only be `slew_attested`. The seat's test (`test:764-818`) pins the strongest consistent form: `timed_log_matches` 10 / marker lines 30 on both bodies (S3), per-envelope counts equal across the pair, `log_sha256` different and each equal to its fixture's digest, states differ with the reason recorded, and the syslog twin yields the state/count the compact fixture produced at `489b0953`. Regression 12 runs over both formats plus the zero-match capture (`test:845-863`). The NIT is satisfied in every part that can be; the rest is R2.3's own consequence.

**(c) Q3 domain and R3.3.** Docstring (`:619-636`) states the invariant holds with equality for gap ≥ 6 and overruns below. Verified arithmetically: for gap ≥ 6, `cleanup = gap−5 ≥ 1`, `attestation = max(5, 5) = 5`, sum = gap; for gap ≤ 5 (including non-integers in (5, 6)), cleanup = 1, attestation = 5, sum = 6 > gap. Correct; supersedes the ruling's illustrative "gap ≤ 10" (synthesis MATERIAL 4). R3.3 (`test:1387-1418`): invariant over v2, SCALED, 700 s pitch, and the gap = 6 boundary (pitch 606), each with `gap ≥ FLOOR+1` asserted as precondition; negative pin at gap = 3 (pitch 603): cleanup 1, attestation 5, sum 6 > 3, `start_drift_abort_s` named. Exactly S1's shape. Expression at `:638` is the ruled one; five pins moved, SCALED unchanged; reserve comment names `attestation_timeout_s`; `validate_protocol` untouched. The seat's note that the boundary row survives the R3.4 kill is correct and does not weaken it (v2 and 700 s rows go red).

**(d) Behaviour outside the ruled items.** None. Every production hunk maps to a ruled item. The one non-obvious side effect — `window_argv_epoch_s` moving into the skeleton changes dict insertion order on the SUCCESS path too — is neutralised: `session.json` is written `sort_keys=True` (`:751`) and the journal row carries only state/wall/matched_lines (`:1171-1173`). A no-failure night's bytes change only by the ruled 15→5 timeout and the ruled acceptance of real syslog output. Commit `56ea8ae0` is two test-only lines, no assertion changed.

## Items

1. Q2 guard + fixtures + R2.1–R2.6 — **CONFORMS** (verbatim block; fixtures sha-pinned; R2.3 both halves; R2.4 includes both formats' second lines).
2. Q3 bound + pins + docstrings + R3.1–R3.4 + S1 — **CONFORMS** (R3.4 kill executed as ruled: re-introduced `gap − CLEANUP_BUDGET_RESERVE_S` → 2 failures → restored green).
3. Q4 null-init + R4 — **CONFORMS** (`:661`, immediately after `window_epoch_s`; blocked and both window-unavailable paths pinned, JSON round trip).
4. Q5.1 R5.1 — **CONFORMS** (exact cure text `:734-741`; absent + malformed + end-to-end vanishing record).
5. Q5.2 R5.2 — **CONFORMS** (unlink first; `.tmp` assertion moved onto the `os.replace`-raises variant, which also proves the temp was complete and `authenticated` at failure).
6. Q5.3 R5.3 — **CONFORMS as accepted by addendum 16** (see NEEDS_RULING 1 below).
7. Q5.4 R5.4 — **CONFORMS** (exact print text, `flush=True`, `except Exception as exc`).
8. Q5.5 docstring + S2 — **CONFORMS with NIT 1** (paragraph not sentence: Deviation 3; one unsupported clause).
9. Q5.6 R5.5 — **CONFORMS** (`*, timeout`, no default; signature, bare call and positional third arg pinned; `:1165-1166` passes `attestation_timeout_s(protocol)`).
10. Q5.7 — no change, as ruled.

## Deviations and NEEDS_RULING

- **Deviation 1 (23 not 31 spaces) — HOLDS.** Verified by byte count; the ruling and both live captures carry 23.
- **Deviation 2 (states differ across the twins) — HOLDS.** See (b).
- **Deviation 3 (paragraph not sentence) — HOLDS** as a deviation in length only; content carries NIT 1.
- **Deviation 4 (SOURCES.md untouched) — HOLDS.** Outside WRITE_SCOPE; NIT 4 assigns the follow-up.
- **Deviation 5 (derived test constant, pinned to live bytes) — HOLDS.** Satisfies "syslog header + `"\n"`"; drift is caught by R2.1 over sha-pinned fixtures and by `test:1461-1462` (`ZERO_MATCH_FIXTURE.read_text() == constant + "    \n"`).
- **Deviation 6 (cosmetic commit) — HOLDS.** Two test-only lines, no assertion change.
- **NEEDS_RULING 1 (R5.3 counterfactual inert) — HOLDS; addendum 16 option (a) not contested.** The clause `and cleanup["cleanup_proven"]` (`:1218`) is unreachable as a discriminator: the `finally` (`:1195-1196`) sets `outcome = "refused"` whenever the final sweep is unproven, so no document can read `complete` with `cleanup_proven False` — the ruling's literal row cannot exist. The ruled AXIS is pinned by execution: the two new rows (`test:1568-1577`) assert `cleanup_proven is False` and rc 2, and the seat's kill B (delete the `finally` refusal) goes red; kill C returns rc 0 on a direct probe. The harness's `final_cleanup_unproven` fails the night-level sweep (the `exclude`-less call), the correct injection point.

Verdict: round 2 conforms to the sealed ruling in every item; no fix-round-introduced defect found in the production delta; four NITs, none blocking merge staging.
