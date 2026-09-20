# Record 73 — magistrate terminal review, STAGE-A-EVIDENCE-EXECUTOR-01, final head `87c38078` (`87c380781d7025cde9954a28309bc45ede3a38db`), 2026-09-19 evening

**Verdict: MERGE** on the records-only merge candidate built from this head (row 12 names it), subject to replay 70c at this head (section 4) and the hosted gate-ledger + quick checks on the PR head.

## 1. What the branch delivers (read, not summarised from seat reports)
The cold-gate-ruled executor (packet 10 → 10a; consults 44/45; seat rulings 46a/46b/65a): a separate evidence payload under the unchanged v2 `DIAGNOSTIC_NO_PACK` plan; the digest-keyed ruled-registration table (now naming its tracked records, S4); the typed evidence probe receipt dispatched by one `NIGHT_PAYLOAD_KIND` export; `scripts/gen_evidence_night.py` with a sealed manifest; the evidence chain template; the frozen idle-only pilot protocol v1; the campaign reduction (disjoint pairs, chi-square upper bound, exclusions by named mechanism, `busy_cores` a covariate only); driver inventory and cleanup; harness admissibility; and — the class the gauntlet forced — THE COURIER ALWAYS RUNS, now as a structural boundary (consult 79 / ruling 79a / seat 80) rather than a case list.

## 2. Gauntlet ledger (what each layer uniquely caught)
- Refuters 56c/56x + Opus 61 (`087bf3af`): the three courier-suppression blockers of one class, the unfrozen sizing constants, killpg EPERM, the unread recorder journal, the prose-only table.
- Replay 60: two REAL cross-module findings no module run could see (hand-edited generated policy block; direct git init) → fix round 2.
- Delta re-audit 64: 10/11 fixed; S4 not fixed → landed at `df5c483e`.
- Opus 71 → Astra 74 → escalation 74a → consult 76 → ruling 76a: the outcome repair became a total function (the escalation rule caught the lead's own two-round point-fixing).
- Astra 78 → escalation 78a → consult 79 → ruling 79a → seat 80 → diff gate 82 → re-audit 81: the boundary; 81 E6 closure holds; two diagnostic-preservation gaps bench-closed (81a).
- Astra 83: bench closure verified; three residual diagnostic-loss sites → ruling 83a: DEFERRED as lane 252 (class not shrinking; delivery unaffected). The lead records this as its own stop decision under Ed's anti-spiral ruling and rule 11's same-signature trigger.
- Lead diff gates 72 (parts 1–3, rounds 1–2) and 82 (round 4): every production hunk read; the two 82 nits are queue data.

## 3. Deferred, registered, and stated honestly
Lanes 250 COURIER-LOCK-OWNERSHIP-FLOCK-01 (cold gate first; pre-existing on main), 251 COURIER-UNWRITABLE-CUSTODY-01, 252 COURIER-DIAGNOSTIC-PERSISTENCE-01 (consult first), 253 FIXTURE-TMPNAME-CENSUS-SUBSTRING-01. Queue data not yet lanes: record 82 nits (retry log duplication; unguarded packet `json.dumps` whose inputs are JSON by existing contract), memo-lane nits, timings refresh for the new modules.

## 4. Replays and bench
- Record 60 (`087bf3af`), 70 (`12dcc3f5`: 6,541 tests, 243/244 modules), 70b (`9f4dda28`: 6,580 tests, 244/245 module runs); the one error in each is the live-seat census argv class (TEST-PGREP-DIALECT-MULTILINE-01), re-run alone OK in earlier records.
- Record 70c (`87c38078`): PENDING — filled in by addendum below before the PR opens.
- Bench, unsandboxed: driver + gate + generator modules 304 OK at `9f4dda28`; `tests.test_run_night` 226 OK at `87c38078`; kernel tests 44 OK at 216 lanes.

## 5. Hosted CI and merge shape
Records-only merge of `bookkeeping/2026-09-19-activation-d0b83820` into the branch = the exact candidate (no code delta vs `87c38078`); PR body ledger validated with `scripts/check_gate_ledger.py`; merge under D-072 on hosted gate-ledger + quick green (matrix post-merge per Ed's 2026-09-16 ruling; the darwin-only guards keep the spawn-based tests off the stdin runner).

## Addendum 18:10 PDT — replay 70c filled in
Record 70c at `87c38078`: 6,582 tests / 245 module runs, 244 PASS; the lone census error re-run alone with no seat alive → 76 OK. Section 4's condition is met. **Verdict stands: MERGE** on the records-only candidate.
