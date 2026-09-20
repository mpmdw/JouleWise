# Record 77 — bench round 3 on the Stage A branch: outcome repair (consult 76) + S4 records, 2026-09-19 15:40 PDT

Delta re-audit 64 (Astra xhigh, read-only, at `12dcc3f5`; filed as `64-delta-reaudit-stage-a-astra.md`): ten of eleven ruled items FIXED (61 B1/B2/S1/S2/S3, 56c R1/R2, 56x R1/R2, 62 N1), one should_fix open — **61 S4 NOT FIXED**: both `RULED_REGISTRATIONS` entries named prose authority, not tracked record paths, and the serialization pin test deferred the existence check. Its V1/V2 failures reproduce at the base inside the seat sandbox (census `ps` PermissionError; journal watchdog) — environmental, settled by the lead's unsandboxed replays. Its wrapper status `SCOPE_VIOLATION/failed_preserved` is the known rc-77 class (`docs/paper/build/out/draft-v1.html` + `__pycache__`), no repository write.

Bench commits on `feat/2026-09-19-stage-a-evidence-executor` after the reviewed head `12dcc3f5`:

| sha | what | authority |
|---|---|---|
| `17f374f2` | first outcome-repair attempt (unlink-then-create; two regressions) | 74 R1 |
| `dbbe2441` | `_evidence_cleanup_error` replaced by consult 76's total function verbatim; regressions for missing / invalid-JSON (`{not-json`, `\xff`) / list / `{}` / list-state / numeric-state / unknown-state outcomes, and for complete / partial / refused-with-refusal untouched | 76, 76a |
| `49a0f44e` | integration merge of the bookkeeping branch `318a3b8e` (records 01–76a, lanes 248/249, main `6032b9e9`); one conflict in `tests/test_sample_quiet_predicate_evidence.py` resolved by keeping main's method name and darwin skip reason for the join-ladder test plus the branch's N3 Pipe-closure test | — |
| `df5c483e` | S4: every entry carries `records` (repo-relative paths; `#D-165`/`#D-166` decision-log anchors; cold-gate ruling 10 + sizing ruling 46b records); test asserts each is a tracked file / heading; pin re-dated; handback sentence extended (clause test updated) | 61a S4, 64 R1 |

Bench ruling on the S4 shape: 61a said the entry's `ruling` names the record path. Implemented as a separate `records` key so the receipt's human label `registration_ruling` (asserted by the C1 test and read by the courier prose) stays a label while the existence guard binds to paths; D-165/D-166 have no `docs/process_traces/` ruling record — their authority IS the decision log, so the anchor form is the honest reference. Any later entry must add records or the test fails.

Executed: `tests.test_night_gate tests.test_gen_evidence_night tests.test_run_night` → 288 OK (106 s); `tests.test_sample_quiet_predicate_evidence` → 57 OK at the merge. Next: fresh-eyes seat (78) on `12dcc3f5..df5c483e`; replay 70 (at `12dcc3f5`) then 70b at `df5c483e`; terminal review; PR.
