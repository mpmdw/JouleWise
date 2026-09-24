VERDICT: MERGE

# 43 — Cold Fable final pass on A280 PR A, merge candidate bedcc0ae

Judge: Claude Fable 5.1, fresh non-interactive session, activation d8cc9c0a, 2026-09-23 22:21–22:35 PDT. Charge: record 41.

## Disclosure
Auto-loaded before I acted: `~/.claude/CLAUDE.md` (global), the project `CLAUDE.md`, and the memory index `MEMORY.md` (one-line pointers only). Not read: CLAUDE.local.md, RUN_STATE.md, TASK_QUEUE.md, memory bodies, council logs, any trace other than records 41, 36, 42 and the code via git. All execution happened in `/tmp` clones of cdc05e9b and bedcc0ae (git clone --no-hardlinks of this worktree, detached at those commits; a clone rather than a bare archive because the new test module needs `git archive cdc05e9b` and `git clone --bare` of its own root). Interpreter: Homebrew python3 3.14.7, stdlib only. No sudo, launchctl, powermetrics, networksetup; canonical root, night-custody, measurement roots and LaunchAgents untouched; no tracked file edited.

## Q1 — executed evidence (all mine, this session)

1. `git diff cdc05e9b..bedcc0ae`: 7 files, +613/−59. Production: night_kinds.py (new), evidence_night.py, night_gate.py, quiet_predicate_campaign.py, gen_evidence_night.py. Tests: test_night_kinds.py (new), one fixture line in test_evidence_night.py. Read in full.
2. Base-vs-head real `prepare` (own probe, same t0, local bare remote of each tree, builder symlinks python, TZ=UTC), then `render_notice`, then the refusal entries:
   - `night_plan.json`: byte-identical after normalising work path and head.
   - `chain.zsh`: identical except the `EVIDENCE_MANIFEST_SHA256` line. `chain.zsh.chain-source.sha256`: identical. `chain.zsh.sha256`: differs only as a consequence.
   - `evidence_manifest.json`: same keys; `files` gains exactly `joulewise/night_kinds.py`; the only pre-existing digests that change are `night_gate.py` and `quiet_predicate_campaign.py`, the two manifest-tracked modules PR A edits. This is the ruled R1 delta and nothing else.
   - Notice: every prose line identical (intro, envelope noun, work, follow-up, subject with receipt class); differences confined to the digest column of plan, chain, manifest and plist lines, which embed the above.
   - Refusals: `unknown_kind` and `calibration` at `prepare` → `Refused: invalid or unresolved kind` at both revisions.
3. Named modules in the head clone: `tests.test_night_kinds tests.test_gen_evidence_night tests.test_quiet_predicate_campaign tests.test_git_fixture_maintenance` → Ran 185, OK. `tests.test_night_gate tests.test_evidence_night` → Ran 240, 1 failure: `PrepareTests.test_same_day_distinct_roots_and_staging` ("attempt 2" missing; second plan_id rolled to 20260924-0000). Re-run in isolation at base and at head: OK both. Cause: the fixture's t0 is now+90 min rounded to the minute; the run started at 22:29 local, so t0 was 23:59 and t0+60 was the next date, giving attempt 1. Pre-existing day-boundary flake in code PR A does not touch (the prefix-per-date logic is unchanged); fires for one wall-clock minute per day. Not a PR A defect; worth a one-line fixture fix in a follow-up (pin t0 away from 23:59).
4. Code reading, Q3 focus (arm/t0 predicates): `check()` now keys corecaptured and machine_quiet on the row flags of `NIGHT_KINDS.get(payload_kind)`; `probe_payload_kind` raises for any non-table kind so `row is None` cannot occur silently; calibration rows carry both flags False → both `skipped`, as before; the idle row carries both True → both inspected in the same order as before. `_check_machine` and `_check_registration` conditions are `in NIGHT_KINDS and <flag>`, and measured `payload_kind` is only recorded inside the `authenticate_chain_source` branch, so the calibration path is unchanged. `probe_payload_kind` accepts exactly the rows with `payload_kind=True`, i.e. only the idle kind today. `prepare` validates `kind == KIND` before any `kind_row(kind)` call, so `UnknownNightKind` never replaces the `Refused` text. The plan-authoring, sealing and census subprocess strings read the table at H with a literal fallback for pre-table H; values equal the removed literals.

Nothing in the diff changes what a real night is refused for or armed with, beyond the ruled manifest entry. MERGE.

## Q2 — Sol 36 F1 and F2

Both are test-strength findings; neither masks a live defect. Executed counterexamples:

- F1 (window). I committed `window_max_s=8999` into a /tmp clone of bedcc0ae and ran the real `prepare` against it: `Refused: python failed (2): REFUSED: window_max_s must equal the frozen protocol's 9000 s`. So plan authoring provably consumes the row's window, and the frozen protocol pin (P5) refuses the night before sealing. A wrong row window fails closed; it cannot mis-arm. Ruling: follow-up lane, not before merge. The durable test is a committed-mutant fixture (bare-clone ROOT, commit a night_kinds.py with 8999, `update-ref main`, `prepare` with that head, assert the refusal text above). It needs a fixture commit helper and is not a bench one-liner.
- F2 (prefix/suffix tautology). Confirmed: `assert_prepared_candidate_head` asserts the row equals the literal before it asserts anything about the plan, so any in-process mutant fails there and `test_k3_kills_prefix_and_suffix_mutations` passes without proving consumption. I ran `prepare` under an in-process mutant row (`plan_id_prefix="mutant-"`, `measurement_root_suffix="mutantroot"`): it completed with plan_id `mutant-20260924-0701` and root `…-mutantroot`. So live `prepare` does consume both fields; only the test is weak. Ruling: not merge-blocking. Land the exact change below as the next test-only commit (before or after merge at the magistrate's discretion); it needs only `tests.test_night_kinds` green, no further delta pass, no further cold gate.

Exact test change (bench-verified in the /tmp head clone: the three K3-family tests pass, Ran 3 OK; with `locations()` pinned back to the literals the new test fails `AssertionError: False is not true`):

In `assert_prepared_candidate_head`, replace the four assertions after `plan = json.loads(...)` with
```python
        self.assertTrue(plan["plan_id"].startswith(row.plan_id_prefix))
        self.assertTrue(Path(plan["measurement_root"]).name.endswith("-" + row.measurement_root_suffix))
        self.assertEqual(plan["window_max_s"], row.window_max_s)
        self.assertEqual(plan["receipt_class"], row.receipt_class)
        self.assertEqual(plan["registration_path"], row.protocol_path)
```
keep the `measurement_head` and `bindings` assertions, and end the method with `return plan`. Replace `test_k3_kills_prefix_and_suffix_mutations` (same skipUnless decorator) with
```python
    def test_prepare_consumes_row_prefix_and_suffix(self):
        row = replace(kind_row("quiet_predicate_evidence"),
                      plan_id_prefix="mutant-", measurement_root_suffix="mutantroot")
        table = MappingProxyType(dict(NIGHT_KINDS, quiet_predicate_evidence=row))
        with mock.patch.object(night_kinds, "NIGHT_KINDS", table):
            plan = self.assert_prepared_candidate_head()
        self.assertTrue(plan["plan_id"].startswith("mutant-"))
        self.assertTrue(Path(plan["measurement_root"]).name.endswith("-mutantroot"))
```
The literal assertions on the row already live in `test_rows_and_unknown_kind`, so no literal coverage is lost. The three added plan-vs-row equalities also give K3 the row-to-authored-plan relationship F1 asked for (an in-process window mutant now fails K3 by disagreement with the committed plan), while P5 stays protocol-only in production.

## Q3 — anything missed
No mis-arm or wrong-refusal path found. Two carry-forward notes for PR B, not PR A defects: (a) the t0 corecaptured and non-observer flags only take effect for a kind whose `authenticate_chain_source` is True, because C5 records `payload_kind` only in that branch; PR B's row must set it True or the flags are silently inert at t0 (the arm check does not share this coupling). (b) `sealed_candidate` and the census subprocess hard-code `kind_row('quiet_predicate_evidence')` rather than the plan's kind; correct today, must be routed in PR B.

## Probes not executed
Full replay (record 42 covers it at 50dc2272; bedcc0ae differs by one test line, which I ran). No live hardware gate. Nothing else in the charge was skipped.
