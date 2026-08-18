# Contract-lens refuter report (Opus 5, 2026-08-18) — position CONCUR-WITH-AMENDMENTS on (a) and on B1 ratification

(Verbatim summary of findings; full text in the agent transcript. All anchors
mechanically resolved at 0cb9bf2 / main by the refuter.)

F1 VERIFIED: circularity real where it matters, but "ANY serialized transition
invalidates the receipt" is OVERBROAD — pack_identity pins only {pack_id,
plan_id, window_id, pack_root, plan_path, plan_sha256(calibration_plan bytes)};
freeze itself rewrites plan_tree.json/sha AFTER identity computation
(consistent); _pack_record (pack_sha256/plan_tree_sha256) computed at :3437 and
NEVER USED in generate_freeze_receipt (purity assertion only); freeze evidence
re-authenticated with pack_sha256=None/head_commit=None. README,
analysis_manifest_v3, order_manifests, consumer_family_declaration,
generate_configs.py are OUTSIDE the pin. Narrow the verdict sentence to the
pack_identity transitive closure.

F2 VERIFIED: packet 06 (runbook v1-precedent text) was authored by the M-2
remedy batch itself (ac3fe1d, #149) — the 2026-08-15 M-2 gate's own refuter
recorded "that sentence IS M-2". Strike as independent corroboration. Its final
sentence affirmatively contemplates future packs emitting freeze-aware status
text — option (a) narrows the cited authority, doesn't apply it.

F3 VERIFIED: M-2(d) (decision_log :9164-9165) — exhaustive scope = the three
2026-08-13 receipt hashes, "may never be cited for any other pack." (a)
therefore requires a fresh DATED AMENDMENT extending the receipts-govern core
to successors, plus a runsheet row for the M-2(b) informational operator note
before the arm gate. Neither exists today (runsheet has no M-2 mention).

F4 VERIFIED: consult §B3/R-7 unambiguously commanded serialized transition —
this is a REVERSAL on unread mechanics, not a re-reading. The consult's D-7
claimed all anchors resolved, but every packet-02 anchor is generator-side; it
never opened joulewise/arm_readiness.py. Record the defect class: consults
ruling on a transaction must resolve the transaction's own module.

F5 VERIFIED (new mandated work): D-139 A3 (decision_log :9712, Ed-approved)
requires chain-monotonic freeze-0002 with explicit predecessor bindings;
generate_freeze_receipt hardwires number=1 and refuses a second receipt — the
approved freeze-0002 CANNOT be minted by current code, falsifying the
runsheet's step-4 "NO code edits (delta-proven installable)". Supersession
machinery exists arm-side (:2095-2108, :4122-4131, vocabulary :131/:4412);
attachment builder already selects committed_receipts[-1] (:1951). Do not
foreclose (b); route it as a first-class candidate inside the mandated
freeze-numbering work at runsheet steps 4-5.

F6 (new option, REQUIRED): (d) freeze-neutral PRE-freeze wording. Current v2
draft branch emits README "unfrozen draft … It is not armable and makes no
data, verdict, receipt, or artifact-byte claim" (gamma generator :1706-1712)
— an affirmative false statement on an armed pack, advisor-visible. Zero _v2
pack committed yet (git ls-files | grep -c "_v2/" = 0) → fix is FREE now:
emit wording true in both states, naming the D-134 receipt + plan-tree pin as
the status authority (text exists verbatim in the unreachable frozen branch
:1697-1704); draft_status value/sibling that does not assert non-armability.
Require (d) before any v2 freeze receipt is minted.

F7: REJECT (c) on merits (stale attestation + split-brain), not impossibility.

F8 VERIFIED: under (a), post-freeze default --check fail-closes for every
successor pack ("the current frozen identity requires preserve mode") — the
runbook's post-freeze custody step assumes the default works; operator trap,
should-fix before step 5. The frozen-emission branches become permanently
unreachable dead code — state it in the amendment or the next implementer
re-derives B2.

F9: anchor hygiene — packet 07 gamma :741→:749-750 (round-5 shifted delta-5's
whole gamma list ~+9); B1 comment anchors off by 2-5; M-2 core is :9157-9158
not :9155-9157. Correct before the verdict.

F10: probe evidence = refusal-CODE CHANGE (fixture receipts were genuine
REFUSE receipts; pre-transition code readiness_dependency_refused →
post-transition readiness_freeze_receipt_mismatch at the earlier unconditional
check), not PASS→REFUSE. Also: "full frozen regeneration exit 0" proves
coherent frozen bytes ARE producible — which keeps (b)/(d) live.

F11: B1 CONCUR on disposition, REFUTE rationale scope — D-139 A1 is a
MEASUREMENT-environment threat model; the write boundary is desk-time
generation. Restate on desk-time single-operator grounds, citing A1 by
analogy. Tested non-adversarial candidates (backup daemons, editors, sync):
none produce ancestor-symlink substitution; realistic concurrent risk is the
worktree fleet (clobbering, not symlinks). Registered residual must live in
docs/risk_register.md (no entry today), not only in code comments.

F12: closure conditioned on the canonical suite run + alpha/beta __pycache__
filter alignment (concurs with cold C5, adds the canonical-suite condition).

Summary of 11 required amendments: narrow F1 sentence; strike 06; dated
successor extension + M-2(b) note row; record reversal + consult defect class;
D-139 A3/freeze-0002 on the record + runsheet false-claim raised; REQUIRE (d)
pre-freeze wording; reject (c) on merits; register the --check trap + dead
code; correct anchors; B1 rationale rewrite + risk-register entry; canonical
suite before closure.
