# Refuter review — NIGHT-GATE-STUB-CHAIN-01, CONTRACT lens (Opus, fresh non-author, read-only)

**Head reviewed:** `bb7090e2b8d4cfe30effbfb7e89cef802277d448` on branch `fix/2026-09-09-night-gate-stub-chain`,
in the detached read-only worktree `/Users/edr/code/JouleWise-wt-ref-stub-astra`.
**Diff under review:** `git diff 83ab38ed..bb7090e2` — `joulewise/night_gate.py` (+70/−61),
`scripts/run_night.py` (+6/−1), `tests/test_night_gate.py` (+40), `tests/test_run_night.py` (+45).
**Lens:** CONTRACT (does the change stay inside its ruled envelope; does it amend anything reserved to the
cold gate or Ed; does the receipt say only true things).
**Independent execution performed:** `python3 -m unittest tests.test_night_gate tests.test_run_night` in the
review worktree → `Ran 135 tests in 8.703s / OK`, rc 0.

**Governing texts read (all paths in the review worktree at bb7090e2 unless noted):**

- Seat contract: `/Users/edr/code/JouleWise-wt-magistrate-1ef89702/docs/process_traces/2026-09-09-rehearsal-harvest/01-brief-night-gate-stub-chain-astra.md` (F1/F2/F3, WRITE_SCOPE).
- Seat report: `.../02-seat-night-gate-stub-chain-astra-report.md`.
- `joulewise/night_gate.py` — `class_table()` (:428–457), receipt/condition key sets (:132–145),
  `evaluate_night` C5 construction (:972–1110), `validate_receipt` basis rules (:1421–1434), plan key
  requirements (:118–130, :290–291).
- `tests/test_night_gate.py::test_the_class_table_matches_the_ruled_condition_matrix` (:391–413) and
  `test_reason_code_registry_is_exactly_the_ruled_set` (:923–962).
- `docs/process_traces/2026-09-01-unattended/MAGISTRATE-RULING-UNATTENDED-STAGE1.md` — R-4 class/condition
  matrix (:89–99), R-4 truthfulness rationale (:85–91), chain-identity refusal path (:288), WO-2 stub-chain
  scope (:236).
- `docs/decision_log.md` — D-175 (:11138–11156), D-176 (:11164–11232), index rows (:221–222).
- `docs/process/NIGHT_HANDBACK.md` (:1–90, the `rehearsal-20260909` section at :51–75).
- `docs/contracts/pack_night_go_receipt.md` — §9 pin tables (:844–891, :946–974, :1025) and the seat-scope
  table (:637–639).
- `docs/process/d149-go-receipt-template.md` (:28–56, C5 semantics and "C5: no evidence").
- `docs/process/state_kernel.json` — `/tasks/CONTRACT-PIN-DRIFT-01` (:1268–1290).
- Consumer sweep: `grep` over `joulewise/`, `scripts/`, `tests/`, `docs/` for `unattended_night_receipt`,
  `chain_sha256`, `chain_path`, `chain_stub`, `"measured"`, `night gate verdict`.

---

## Blockers

None.

---

## Should-fix

### S1 — The C5 detail sentence asserts a check the stub never performed

(a) Quote — `joulewise/night_gate.py:1107–1110`, now reached by the `REHEARSAL_STUB` branch as well:

```python
    rows["C5"].status = "PASS"
    rows["C5"].measured["detail"] = (
        "window, plan freshness, measurement HEAD, and chain identity passed"
    )
```

For a `REHEARSAL_STUB` receipt the new branch at `joulewise/night_gate.py:1043–1050` reads neither
`plan.chain_path` nor `plan.chain_sha256_path`, so no chain identity was established, yet the custodied
receipt records the sentence "… and chain identity passed".

(b) Governing text — `docs/process_traces/2026-09-01-unattended/MAGISTRATE-RULING-UNATTENDED-STAGE1.md:85–91`
is the ruling's own reason for the v2 schema: "The v1 evaluator demands the exact key set and PASS on every
condition …; a pack-less night cannot truthfully say PASS to C2 (the pack's arm ceremony), so v1 does not fit
and **must not be bent**." The `NOT_APPLICABLE`/`basis` machinery exists precisely so a night receipt never
claims a check it did not perform. The same truthfulness rule governs the free-text `measured.detail` that a
human harvester (and `NIGHT_HANDBACK.md`'s courier, which is told the result record is authoritative) reads.
The row's `status: PASS` with null basis is correct and ruled (`class_table()` `REHEARSAL_STUB` C5 =
`("PASS", None)`, pinned at `tests/test_night_gate.py:391`); only the sentence is false.

(c) Proposed correction — in the stub branch set a distinct detail, e.g.
`"window, plan freshness, and measurement HEAD passed; chain identity not evaluated (driver substitutes the
built-in stub)"`, and pin that string in `test_rehearsal_stub_does_not_read_missing_chain_or_sidecar`.

### S2 — The diff silently staled eleven `docs/contracts/pack_night_go_receipt.md` §9 line pins

(a) Quote — the diff hunks `@@ -1040,61 +1040,70 @@` (night_gate.py, +9 lines), `@@ -131,6 +131,18 @@` and
`@@ -417,6 +429,34 @@` (test_night_gate.py, +12 then +28), `@@ -289,6 +289,51 @@` (test_run_night.py, +45)
displace every pinned symbol below them. Verified pre/post in the review worktree
(`git show 83ab38ed:<file> | sed -n '<L>p'` vs `sed -n '<L>p' <file>`):

| Contract pin | Pinned symbol | Now at |
|---|---|---|
| `night_gate.py:1103–1113` (contract `:236` and `:1025`) | `if plan.receipt_class == "TRANSACTION_PACK" and plan.pack_night is None:` | 1112–1122 |
| `night_gate.py:1357` (`validate_receipt`, contract `:861`) | `def validate_receipt(...)` | 1366 |
| `tests/test_night_gate.py:402` (contract `:952`) | `test_a_green_diagnostic_plan_yields_a_valid_go_receipt` | 414 |
| `tests/test_night_gate.py:420` (contract `:853`) | `test_a_transaction_plan_is_refused_until_stage_three_exists` | 460 |
| `tests/test_night_gate.py:943` (contract `:853`) | `test_valid_v3_pack_without_driver_arguments_lifts_unbuilt_fence` | 983 |
| `tests/test_run_night.py:1865` (contract `:861`) | `test_driver_self_authors_arm_before_go_and_pins_all_eight_flags` | 1910 |
| `tests/test_run_night.py:1929` (contract `:853`) | `test_gate_reauthenticates_c1_and_c2_despite_forged_driver_pass_rows` | 1974 |
| `tests/test_run_night.py:1969` (contract `:861`) | `test_pack_standard_refusal_receipt_preserves_each_actual_cause` | 2014 |
| `tests/test_run_night.py:2000` (contract `:858`) | `test_gate_checks_authorization_fields_and_confirmation_bytes` | 2045 |
| `tests/test_run_night.py:2113` (contract `:861`) | `test_machine_refusal_and_refused_receipt_never_publish_go` | 2158 |
| `tests/test_run_night.py:2156` (contract `:858`) | `test_go_producer_enforces_two_by_two_purpose_window_table` | 2201 |

(b) Governing text — D-176 §6 and the §9 tables make those pins contract text ("contract §9 final pins",
`docs/contracts/pack_night_go_receipt.md:637–639`), and `docs/process/state_kernel.json`
`/tasks/CONTRACT-PIN-DRIFT-01` records that 99gi found 55/186 stale pins and that 99gj/99gl "record
mechanical repinning" landed through PR #307 at `58d9225b`. No test enforces pins today
(CONTRACT-PIN-DRIFT-01 is still `queued`: "Propose a pin-check test"), so nothing in the green 135-test run
catches this; the just-completed repin regresses by eleven entries.

(c) Proposed correction — the merging magistrate repins those eleven citations in
`docs/contracts/pack_night_go_receipt.md` in the landing commit (the seat could not: `docs/` is outside its
exhaustive WRITE_SCOPE), or records the drift explicitly against CONTRACT-PIN-DRIFT-01.

### S3 — The new tests pin "tolerates missing chain files", not the contract's "does NOT read"

(a) Quote — the only stub regression, `tests/test_night_gate.py:432–446`, exercises exclusively the
missing-file case:

```python
        plan = make_plan("REHEARSAL_STUB")
        source = MissingChainProbeSource(plan)
        ...
        self.assertNotIn(plan.chain_path, source.read_calls)
        self.assertNotIn(plan.chain_sha256_path, source.read_calls)
```

`MissingChainProbeSource.read_text` (`tests/test_night_gate.py:134–143`) appends to `read_calls` only on the
two paths it then raises for. A hypothetical implementation that still reads the chain *when it exists* and
refuses `night_chain_digest_mismatch` on a mismatch would pass every assertion in this test unchanged, while
restoring exactly the gate/driver divergence the cure exists to remove.

(b) Governing text — brief `01-…-astra.md` F1: "for `plan.receipt_class == "REHEARSAL_STUB"` **do NOT read**
the chain or sidecar" (unconditional), and F2's requirement that `read_calls` contain neither path.

(c) Proposed correction — add one subtest: a `REHEARSAL_STUB` plan evaluated against a plain
`FakeProbeSource(chain_digest="0" * 64)` (chain present, sidecar deliberately mismatched) still yields
`REHEARSAL_ONLY` with neither path in `read_calls` — the same source that refuses
`night_chain_digest_mismatch` for `make_plan()` at `tests/test_night_gate.py:586–600`.

### S4 — The narrowing of a ruled refusal path's class coverage is recorded nowhere in a standing doc

(a) Quote — `joulewise/night_gate.py:1043` `if plan.receipt_class == "REHEARSAL_STUB":` … `else:` (the
unconditional read moves under the `else`). After this head, `night_chain_digest_mismatch` is unreachable at
night for one of the three ruled classes.

(b) Governing text — stage-1 ruling `:288` states the mechanism class-agnostically: "Chain bytes differ from
the reviewed runsheet block → identity test (R-2 item 3) fails in CI; **at night, the sidecar sha mismatch
refuses `night_chain_digest_mismatch`**." Nothing in `docs/`, on this head, says that the stub class is
exempt; the only text that describes the substitution is per-night prose rewritten every night
(`docs/process/NIGHT_HANDBACK.md:60–61`, "The chain is the driver's built-in stub (`sleep 2; echo
REHEARSAL`)") plus the stage-1 WO-2 scope line `:236`. The narrowing is substantively correct — the stub's
declared chain is never executed (`scripts/run_night.py:1572–1575` substitutes `/dev/null` +
`sleep 2; echo REHEARSAL`) — and it was authorized by the magistrate's own brief, so this is a record-keeping
gap, not an unauthorized amendment (see "Checks that PASSED", rule-11 item).

(c) Proposed correction — one dated line in `docs/decision_log.md` (or the harvest record for
`rehearsal-20260909`) stating that for `REHEARSAL_STUB` the gate performs no chain-identity check because the
driver substitutes the built-in stub, so `night_chain_digest_mismatch` covers `DIAGNOSTIC_NO_PACK` and
`TRANSACTION_PACK` only.

---

## Nits

### N1 — The stub receipt no longer records which chain the plan declared

`joulewise/night_gate.py:1043–1050` omits the `chain_path` / `chain_sha256_path` measured keys and the two
evidence citations (`rows["C5"].evidence.extend((f"chain:…", f"chain_sha256:…"))`, now `:1072–1074`, is inside
the `else`). `_RECEIPT_KEYS` (`:132–140`) carries no plan path, so the stub receipt alone no longer shows what
the plan pointed at. Provenance survives in the committed plan file and in `d149-go-receipt-template.md:55`
("C5: no evidence — it is the issuer's binding acknowledgment"), which the empty evidence list actually
matches better than the pre-cure behaviour. Correction if wanted: keep `chain_path`/`chain_sha256_path` in the
stub's `measured` alongside `chain_stub`.

### N2 — `chain_path` / `chain_sha256_path` are now dead required plan inputs for the stub class

`joulewise/night_gate.py:290–291` (`chain_path = require_text("chain_path")`) still demands both keys of every
plan, including `REHEARSAL_STUB`; after this head nothing on the stub path reads or validates their values, so
an arming operator can put any non-empty string there. Risk is bounded by D-175's arming conditions
(`--render-only` validation from the pinned checkout, `decision_log.md:11149–11153`). No change proposed.

### N3 — The F3 log regression recomputes the production transform rather than pinning literal text

`tests/test_run_night.py:292–310` builds its expectation with
`expected_detail = " ".join(refusal["detail"].splitlines())[:200]`. It does assert
`self.assertEqual(200, len(expected_detail))`, so truncation and the newline join are genuinely exercised and a
changed cap or join character fails the comparison; but a defect that is *identical in shape* on both sides
would be invisible. Correction if wanted: assert against a literal expected string built from the known census
stdout.

### N4 — `reason=None detail=` is representable in the log line

`scripts/run_night.py:1520–1522` falls back to `{}` and `refusal.get("detail", "")`, so a `REFUSED` receipt
with a missing refusal object would log `reason=None detail=`. `validate_receipt`
(`joulewise/night_gate.py:1450–1456`) makes that unreachable for receipts this driver writes. No change
proposed.

---

## Checks that PASSED

1. **Class table untouched.** `class_table()` (`joulewise/night_gate.py:428–457`) is byte-identical to
   `83ab38ed`; `test_the_class_table_matches_the_ruled_condition_matrix` (`tests/test_night_gate.py:391`) is
   unmodified and green, and its expected dict still matches the stage-1 R-4 matrix
   (`MAGISTRATE-RULING-UNATTENDED-STAGE1.md:93–96`).
2. **Basis rules untouched.** No line of `validate_receipt` (`:1366`+) appears in the diff; the
   PASS/FAIL-with-null-basis rule (`:1429–1434`) is unchanged, and the new stub receipt satisfies it —
   `validate_receipt(...) == []` is asserted at `tests/test_night_gate.py:438`.
3. **Real classes byte-for-byte.** Diffing the `else:` block against `83ab38ed` shows indentation-only change:
   the read, the `ProbeError` on non-text, the four sidecar-defect checks (token count, hex form, basename,
   digest equality) and the `night_chain_digest_mismatch` refusal are otherwise identical. The pre-existing
   defect tests (`test_chain_sidecar_accepts_bare_hex_and_gnu_shasum_forms`,
   `test_chain_sidecar_refuses_case_name_and_token_count_defects`, `tests/test_night_gate.py:577–600`) are
   unmodified and green.
4. **Reason-code registry unchanged.** `test_reason_code_registry_is_exactly_the_ruled_set`
   (`tests/test_night_gate.py:923`) is unmodified; `night_chain_digest_mismatch` keeps its named coverage test,
   which uses the default `DIAGNOSTIC_NO_PACK` plan, so the code stays reachable and pinned.
5. **Gate predicate and driver predicate are ONE truth.** `scripts/run_night.py:1525–1541` returns
   `EXIT_REFUSED` whenever `rehearsal and plan.receipt_class != "REHEARSAL_STUB"`, so at the substitution point
   `rehearsal_effective` (`:1545`) is logically equivalent to `plan.receipt_class == "REHEARSAL_STUB"` — the
   gate's new predicate cannot diverge from the driver's substitution predicate. This was the specific
   asymmetry I looked for; it does not exist.
6. **The forcing defect is closed and the counterfactual is real.** On `83ab38ed` the new stub test fails with
   `night_probe_error` / `FileNotFoundError` (seat report 02, "Verification notes"); on this head it passes,
   and `test_diagnostic_still_refuses_missing_chain_or_sidecar` (`tests/test_night_gate.py:448`) pins that both
   paths still refuse `night_probe_error` for `DIAGNOSTIC_NO_PACK`, subtested per path.
7. **No receipt-schema or consumer break.** `_RECEIPT_KEYS`/`_CONDITION_KEYS`/`_CONDITION_IDS`
   (`:132–145`) are unchanged; `measured` is validated only as "must be an object" (`:1414–1417`), so the added
   `chain_stub` key and the `null` digests are schema-legal. A repo-wide grep finds no consumer of
   `C5.measured` outside `night_gate.py`: the only cross-module `measured` reads are
   `scripts/run_night.py:1208` (C4 `boot_session_uuid`, `TRANSACTION_PACK` only) and `:1228` (pack GO copy),
   and `joulewise/arm_readiness.py:2843–2851` (shape only). No doc lists the C5 measured keys.
8. **No pack-path contamination.** `_evaluate_pack_conditions` (`:905`), `_pack_bytes`/`window_chain_sha256`
   (`:776–781`), `evaluate_g5` and the whole `joulewise/t0_rehearsal.py` replay surface are untouched; the
   `TRANSACTION_PACK` branch still runs the unconditional read.
9. **F3 is scoped as contracted.** The only `scripts/run_night.py` change is the five-line log construction at
   `:1518–1523`; no new production seam, no new flag, no exit-code change. The non-refused form is pinned
   exactly (`tests/test_run_night.py:312–319`, `"night gate verdict=GO"`) and the stub form too
   (`:321–335`, `"night gate verdict=REHEARSAL_ONLY"`). A repo-wide grep shows no doc, script or courier text
   parses the `night gate verdict=` line, so the appended fields break no consumer; the truncation is bounded
   at 200 chars and newline-joined, so one refusal cannot flood `night.log`.
10. **WRITE_SCOPE respected.** The diff touches exactly the four declared files; no docs, plans, `RUN_STATE`,
    `TASK_QUEUE`, kernel or other test module is modified, and the branch carries the single seat commit.
11. **Rule-11 reservation (brief question 3).** Nothing in the diff amends a process rule, a skill, a decision
    entry, the ruled condition matrix, a basis value, a reason code, a cadence number or a stop signal, and no
    irreversible action is taken. The one governance-adjacent effect — the class narrowing of
    `night_chain_digest_mismatch` — was authorized in advance by the magistrate's own brief (F1) and does not
    reinterpret any verdict; it needs recording (S4), not a cold gate.
12. **Suite re-run independently.** `python3 -m unittest tests.test_night_gate tests.test_run_night` in the
    review worktree: `Ran 135 tests in 8.703s`, `OK`, rc 0 — matching the seat's reported V1.

---

## Verdict

**Mergeable after the listed should-fixes.** The cure is correctly scoped and correctly reasoned: it keys on
the ruled `receipt_class` rather than on any driver flag, leaves `class_table()` and the `validate_receipt`
basis rules literally untouched, preserves the chain and sidecar checks byte-for-byte for
`DIAGNOSTIC_NO_PACK` and `TRANSACTION_PACK`, closes the live `rehearsal-20260909` forcing defect with a
regression that genuinely fails on `83ab38ed`, and adds the refusal reason and a bounded one-line detail to
the driver log line that had been hiding the defect — with no schema, consumer, exit-code or courier change
that I can find, and 135 scoped tests green on my own run. Nothing here is a blocker and nothing here needed a
cold gate. Four things should be fixed before it lands: the C5 detail sentence still tells a custodied receipt
that "chain identity passed" on a night where no chain was read (S1 — the one in-code fix, and the one the
stage-1 ruling's own truthfulness reasoning speaks to); the hunks displace eleven `pack_night_go_receipt.md`
§9 pins that the 99gi/99gj repin had just corrected and that no test guards (S2, doc-only and outside the
seat's WRITE_SCOPE, so it falls to the merging magistrate); the stub regression pins only the missing-file
case, so an existence-guarded re-read would slip past it (S3, one added subtest); and the fact that
`night_chain_digest_mismatch` no longer covers the stub class is written down nowhere a future session would
read (S4, one dated line). S1 and S3 are minutes of bench work; S2 and S4 are the magistrate's to land with
the merge.
