# Record 93 — magistrate terminal review, EVIDENCE-PLAN-PATH-BINDING-01, final head `cf17e865` (`cf17e86521c14dc3db38de88a409b1874ebed503`), 2026-09-19 evening

**Verdict: MERGE** on the records-only merge candidate built from this head (row 12), subject to replay 90b (section 3) and hosted gate-ledger + quick on the PR head (Ubuntu also independently checks the test-portability closure of 92 R1).

## 1. What the branch does (read, not summarised)
Two production sites, eight lines: `scripts/gen_evidence_night.py` seals `EVIDENCE_PLAN_PATH` as the content-derived published path `<custody_root>/night_plan.json` and refuses a relative custody root at the desk; `joulewise/night_agent_install.evidence_probe_bindings` compares plan-file identity resolved on both sides (so the installer's resolved `--plan` and a symlinked/aliased custody root both pass) and the sealed literal lexically, and refuses an evidence install from any plan not at its published path. Tests: fixture plan at the published name; regressions for staged render → atomic publication → bindings pass, staged-path refusal, byte-identical artefacts from either copy, an explicit symlinked custody root under both spellings, a relative root refusal; the publication class above `unittest.main()`.

## 2. Gauntlet ledger (unique catches)
- Seat 87 (arm scripts): found the defect on a fixture before any arm — the whole reason for this lane.
- Refuter 89 (execution) and Opus 90 (contract) independently found the resolve-vs-absolute trap on the first seat commit (`/tmp` vs `/private/tmp`; symlinked root); Opus added the missing absolute-root guard and the mutants that pin both halves.
- Fresh eyes 92: mutants a/b/c killed; F4 no other mismatched sibling comparison; caught the lead's own host-layout assumption in the alias regression (would have failed on Ubuntu CI).
- Lead diff gate 91; rulings 87a / 90a / 92a; bench closures verified under both temp layouts.

## 3. Replays and bench
- Record 90b: full sharded replay at `9f452559` (production code identical to the final head) — PENDING, filled in by addendum before the PR opens.
- Record 90c: the two edited test modules alone at `cf17e865`: 73 OK.
- Bench, unsandboxed: five modules 392 OK at `9a0d8fa8`; focused classes at each bench commit OK.

## 4. Deferred and stated honestly
Queue data DOCS-EVIDENCE-REFUSALS-01 (the two new refusal strings into the runbook refusal table, the handback cold-gate table, the traceability row) — a docs lane. N3 (census check on the no-longer-emitted staging path) kept as belt-and-braces. The fixture temp-name flake (lane 253) was sighted again during verification.

## 5. Merge shape
Records-only merge of `bookkeeping/2026-09-19-activation-d0b83820` into the branch = the exact candidate (no code delta vs `cf17e865`); ledger validated with `scripts/check_gate_ledger.py`; merge under D-072 on hosted gate-ledger + quick green; matrix post-merge (fix forward if red). After the merge: lane 254 retired; `87-arm-scripts-qpe01-pilot/arm-env.zsh` H re-pinned to the merge; the pilot arm hands to a fresh activation.

## Addendum 20:25 PDT — replay 90b filled in
Record 90b at `9f452559`: 6,587 tests / 245 module runs, 244 PASS; the lone census error re-run alone at `cf17e865` with no seat alive → 76 OK; record 90c (edited test modules at `cf17e865`) 73 OK. Section 3's condition is met. **Verdict stands: MERGE** on the records-only candidate.
