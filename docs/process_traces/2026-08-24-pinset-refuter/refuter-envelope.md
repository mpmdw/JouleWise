# Custody: PR #182 pinset-cure refuter envelope (F1 should-fix)

**Provenance.** Recovered 2026-08-24 from the T23 session record. PR #182 (the
pinset-builder cure) was merged while this refuter was still running, so its
returned envelope never entered the repository record at the time; kernel row
`PINSET-GRAMMAR-EXCLUSION-01` was registered as a stub with an anomaly note
because of that absence. The magistrate recovered the task-notification from
the session record and custodied it here.

- Refuter agent: "Pinset cure refuter", task-id `afa98fc4eaa4512e1`
- Subject: PR #182 (pinset-builder cure, `fix/pinset-builder-projected`)
- Adjudicated verdict: **SOUND FOR MERGE** — one registered should_fix, no blocker
- Payload this custody exists for: the section **"## The should_fix to carry (F1)"**
  below, which is the authoritative wording of the finding that
  `PINSET-GRAMMAR-EXCLUSION-01` closes. The row's GOAL is restated from that
  section's own text.

Everything below the rule is the recovered task-notification **verbatim**.

---

<task-notification>
<task-id>afa98fc4eaa4512e1</task-id>
<tool-use-id>toolu_01EXUKUhTxFTjz2R9uFoeQLP</tool-use-id>
<output-file>/private/tmp/claude-501/-Users-edr-code-JouleWise/eac3ed1d-1740-4cf1-9ab3-b4c539575666/tasks/afa98fc4eaa4512e1.output</output-file>
<status>completed</status>
<summary>Agent "Pinset cure refuter" finished</summary>
<note>A task-notification fires each time this agent stops with no live background children of its own. The user can send it another message and resume it, so the same task-id may notify more than once.</note>
<result># ADJUDICATED VERDICT: SOUND FOR MERGE — with one registered should_fix hardening gap (no blocker)

Terra (gpt-5.6-terra, xhigh, default tier, `codex-run-v3`) returned a final well-formed `claude-codex-report/v1` envelope with formal verdict **DEFECT / F1 should_fix**. I replayed every load-bearing check myself; the mechanism findings corroborate, and the severity adjudicates to should_fix, not blocker. The cure does what it claims and every smuggling path Terra or I constructed terminates in a refusal at a layered gate.

## Protocol status (disclosed plainly)

- Envelope: present, single, final, well-formed. Report at `/private/tmp/claude-501/-Users-edr-code-JouleWise/eac3ed1d-1740-4cf1-9ab3-b4c539575666/scratchpad/refute-pinset-cure.md`; manifest/log/status alongside it.
- Wrapper `run_status=SCOPE_VIOLATION` (exit 77) — **attribution is mine, not Terra's**: I ran the repo-venv pytest suite inside the shared audited worktree mid-run; the evidence bundle's changed paths are exclusively `.pytest_cache/` and `joulewise/__pycache__/*.cpython-313.pyc` (my venv is 3.13; Terra ran python3.14 with `PYTHONDONTWRITEBYTECODE=1` and had no pytest). Tracked-file diff was clean (Terra V8 + my own `git status`: empty). No repository write by the refuter occurred.
- Baseline drift flag E2: branch advanced 24a6f93 → 41d9db1 during review. I diffed it: **runsheet-only citation-anchor refresh**, zero code change, §3.7 `--historical-head "$EVIDENCE_DERIVATION_HEAD"` invocation untouched. Immaterial to the verdict; the code review head equals the PR's code content.

## Per attack line (Terra's finding, my replay)

1. **Exclusion soundness — the real finding (F1).** The shared predicate `_histsem_tree_has_authoring_custody` tests only `PurePosixPath(path).parts[0]` (`joulewise/arm_readiness.py:2906-2918`), so the exclusion is an **unbounded directory exception**: I confirmed by direct probe that `identity_pin_projection.receipts/arm_readiness.evidence/x.json` returns False at both call sites (builder `scripts/build_v4_histsem_pinset.py:128-144`, verifier `arm_readiness.py:3466-3483`). However, in Terra's executed nested tamper the builder still refused on the next check ("plan tree has no pinned freeze receipt"), and any nonconforming entry under that namespace is refused by the identity membrane `readiness_identity_receipt_namespace_anomalous` (`joulewise/identity_pins.py:957-981`, invoked via `verify_frozen_projection` ~:1977-1993) and by the PACK_AUTHENTICATION exact-addition fence (`joulewise/arm_readiness_evidence.py:1516-1544`, projected path selection :1647-1669). No unauthenticated consumer of that directory's bytes was found at mint or verify time.
2. **Kept delta consumers.** Confirmed: both delta checks (builder :80-118, verifier `arm_readiness.py:3350-3404`) admit arbitrary added bytes under the directory — Terra's temp-clone tamper got `verifier_status=PASS` with `identity_pin_projection.receipts/evil.bin` in the added list — **but only after recomputing and committing a modified pinset row**, i.e. it requires pinset-mint + external-confirmation authority; K12 (`current_pack_sha256`, :3437-3445) refuses any pack-byte change against the existing pin, and deletions are categorically refused (I verified `result["deleted"]` → refusal, which also closes smuggle-then-delete). This was the pre-cure status quo for the other three custody directories too; not introduced by the cure.
3. **Verifier symmetry.** Premise corrected by Terra: `_gate_receipt_histsem` verifies the supplied root; `verify_all_receipt_histsem` (:3654-3676) iterates rows. All nine v1 packs verify PASS at the cure head (9/9 packs, 99/99 receipts, zero advisories — Terra V5); v1 historical coordinates have empty custody, so old and new predicates are both False — no behavior change.
4. **Set arithmetic.** I executed it myself: FULL = {arm_readiness.evidence, arm_readiness.freeze.receipts, arm_readiness.sources, identity_pin_projection.receipts}; AUTHORING = FULL minus identity_pin_projection.receipts only. `arm_readiness.sources` retained. Exact.
5. **Tests.** I ran the full `tests/test_receipt_histsem.py` under the repo venv: **27 passed + 48 subtests** (Terra ran the 6-test class under unittest, OK; its pytest was an environment gap only). Terra ran two original tampers (nested custody; post-historical addition) from temp clones — scripts preserved at `/tmp/histsem_nested_projection_tamper.py` and `/tmp/histsem_posthistorical_projection_tamper.py`. Note: the new `PreAuthoringProjectionCustodyTests` do **not** cover the nested case (`tests/test_receipt_histsem.py:882-887` is the only positive projection case).

Also verified: `scripts/build_v4_histsem_pinset.py.sha256` matches file bytes (replayed, OK); no forgotten consumer of `_HISTSEM_CUSTODY_DIRECTORIES` repo-wide; runsheet §3.7 change present and correctly reasoned.

## The should_fix to carry (F1)

The "projection receipt" exception is implemented as a whole-directory exception. Recommended follow-up (post-merge is fine): bound the pre-authoring exclusion to the projection freeze grammar (`projection-[0-9]{4,}.(json|sha256)` directly under the directory — the same grammar `identity_pins.py:957-964` already enforces), or minimally add the nested-authoring-custody case to `PreAuthoringProjectionCustodyTests` so the layered refusal is pinned by test rather than by adjacency.

## Strongest losing-side argument (for blocking DEFECT)

The histsem gate now contains a namespace where bytes are neither pre-authoring-refused nor grammar-checked *within that gate*, and the defense rests on gates that run at different times (authoring-time fence, arm-time membrane) — a future refactor could sever that adjacency silently, and the new tests would not notice. That is a genuine defense-in-depth erosion argument; it loses because every constructed exploit requires authority (pinset mint + external confirmation) that already implies game-over, the histsem contract explicitly designates K7 as layered hardening rather than the sole boundary, and the pre-cure code had the identical top-level-only shape for all four directories.

PR #182 is clear to proceed on this seat's account.</result>
<usage><subagent_tokens>80846</subagent_tokens><tool_uses>10</tool_uses><duration_ms>148125</duration_ms></usage>
</task-notification>
