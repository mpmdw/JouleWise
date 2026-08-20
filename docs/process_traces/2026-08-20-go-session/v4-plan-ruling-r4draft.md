# `_v4` transaction plan ruling + D-148.5 r4 amendments — DRAFT for cold pairing (2026-08-20)

Inputs: sol-design.md + opus-design.md (independent, blind), the two
debate responses (v4plan/ dir; near-total convergence, every
concession evidence-driven), lead bench verifications (GIT in the
type enum :1771; sudoers observability-only in quiet_window_clock.sh
sync_state fallback). BIG classification per r3 A-5.5 binds:
implementation gauntlet + Fable final review + pre-merge seat pass.

## r4-1 (THE ALLOWLIST — supersedes r1 §1c's `[]` and its rationale)

`irrelevant_path_allowlist: []` is EXECUTABLY FATAL: the changed-set
gate diffs the whole repository from the evidence derivation commit
(joulewise/arm_readiness.py:3105-3113, refusal :3210-3218) and the
transaction necessarily commits at the measurement checkout after
authoring. Both seats converged; Sol's clone probe is dispositive
(EMPTY=REFUSE:DEPENDENCY_CHANGED_SET; EXACT=PASS_PAST_3212;
TAMPER=REFUSE:DEPENDENCY_MANIFEST). Ruled value: the determinate
111-path expansion (37 exact paths × the three `_v4` roots: the
eleven applicable slugs' sources/evidence/evidence-sha files +
freeze-0004.json(+sha) + plan_tree.json + plan_tree.sha256), plus
exactly two marker paths iff Ed rules V6 option (a) with a tracked
marker. No identity-projection or producer_contract path is
admitted — U11 precedes derivation by order (r4-3). Companion code
delta: freeze-slot normalization extends to ALL THREE
registry-declared successor plan trees (PACK_FAMILY binds siblings).
The applicability census (exactly eleven generic receipts per pack)
is mechanically confirmed before the value is accepted.

## r4-2 (S-0 — the gate on everything)

Before any registry byte lands: the FULL three-pack transaction in a
throwaway clone — U11 ×3, common-head evidence authoring, evidence
commit, freeze ×3, marker construction, arm generation AND
verification per pack — proving: all items cross :3212; both arm and
verification paths return governed results; an ordinary changed path
refuses; an unexpected output-directory file refuses; a non-freeze
mutation in current AND sibling plan trees refuses (this also
executes L5-F2's outstanding mutation falsifier — sitting ruling
C-3); missing/extra/unused allowlist entries fail the candidate
contract; AND the poison question answered: whether a
refusal-carrying mint writes a plan-pinned freeze-0004 that
idempotent replay then locks (if yes, the runsheet gains a
pre-mint refusal check so a refused mint cannot occur).

## r4-3 (ORDER — supersedes r1 R-4.5's kernel-last)

The converged 10-step order (Sol's F3 formulation): S-0 → all
registry/code/marker-consumer/scheduler/reference commits → U11 ×3
committed → kernel/runbook/custody + canonical at the final
pre-evidence tree → Ed's tree-preserving terminal-review attestation
(THE common derivation head) → evidence ×3 at that head, one commit
→ freeze-0004 ×3 → dry-run ceremony (B-4 form: dry-run +
file-09-probe P1/P2/P3; NO real arm) + marker candidate + Ed's
exact-byte step-6 → atomic publication → published-head suite with
zero further ordinary commits, then shakedown → windows with the
checkout pinned. Docs-only commits to main DISARM T-0
(exact_match=false — executed, sitting §6.2): the runsheet carries a
commit-freeze on the measurement checkout's main from attestation
through window close.

## r4-4 (HORIZON — to Ed; the transaction is unmintable without)

168h (604_800_000_000_000 ns; policy id
r1.execution_bound.freeze_generic_168h.v1) for the ten live generic
kinds. 24h fails at ALPHA's arm under the ratified one-window-per-
night shape; 72h fails the clean nightly schedule (~T+74h) and any
refused night (~T+146h). Freshness cost stated to Ed verbatim from
the debate: the ten generic facts may be legally reused up to seven
days; the widened undetected interval is bounded by the four
detectors that do NOT relax (changed-set, boot binding, per-window
T-0 re-derivation, D-134 disk/git) and closed further by the
REQUIRED per-window re-pin (same boot, reviewed HEAD, earliest
remaining deadline, acceptance + estimator shas — recorded in each
GO receipt). The T0+24h HARD DEADLINE ON ED IS DROPPED (rule-11
inversion; Opus refutation stands); replaced by machinery: the
step-6 packet carries the live fuse deadline; the window scheduler's
mechanical minimum-fuse gate refuses arming when insufficient fuse
remains; an idle unpublished family is a safe state.

## r4-5 (code-delta manifest additions)

Both EvidenceLifecycleError escape sites caught (:6139-6141 AND
:6334-6336), each with a defect-shaped regression; the four-type V4
allocation POLICY {CLASS_MISMATCH, UNKNOWN_POLICY} / LIFECYCLE
{DEPENDENCY_CHANGED_SET, DEPENDENCY_MANIFEST, TEMPORAL_BUDGET,
V1_GRANDFATHERING} / CUSTODY {FAMILY_PUBLICATION} / GIT
{SUCCESSOR_CHAIN} (GIT verified in the registry enum :1771 —
supersedes r3's IDENTITY typing for SUCCESSOR_CHAIN); the sitting's
B-12 (now_monotonic_ns at both freeze-replay sites) joins the same
manifest (sitting ruling C-12 blocker).

## r4-6 (B-δ — unattended windows are impossible today; to Ed)

CLOCK_ATTESTATION is OPERATOR_ATTESTATION by construction
(:884-889): every window's T-0 needs a human attestation — D-149
auto-GO cannot run unattended without a privileged-scope (D-127)
change AND a code change. Ed chooses: (a) attended-T-0 windows for
the `_v4` campaign (Ed present at each T-0; windows otherwise
automated), or (b) authorize the scope+code change as its own
gauntleted work order first. The sudoers -getusingnetworktime item
is DOWNGRADED to observability (verified: only
quiet_window_clock.sh's failure-tolerant sync_state calls it).

## r4-7 (stage decomposition)

Several bounded sessions, S-0 gating all: S-0 lifecycle
correction + clone proof; S-1 registry bytes + code deltas + load
closure; S-2 marker (per Ed's V6 ruling) + scheduler mechanical
gates (fuse minimum + halt bounds); S-3 family emission + U11 +
docs/kernel; S-4 evidence + mints (lead + Ed gates per r4-3); S-5
publication + shakedown. Each through the C-028 gauntlet; delta
re-audits on every fix round; the pre-merge seat pass covers the
composed artifact.

## Consolidated Ed packet (supersedes prior lists)

1. HORIZON 168h approval (r4-4) — transaction unmintable without.
2. V6 marker option (a)/(b) — TRANSACTION-BLOCKING (r2 A-1; B-7
   pricing corrections applied: pre-mint schema+consumer is calendar
   cost, not fuse cost; cross-term recorded).
3. B-δ: attended-T-0 vs scope+code change (r4-6).
4. Mint-license installation for the six `_v4` commands (verified
   absent; D-148.1's snippet was never installed).
5. ED-QUAL-L6-1 re-scope + ED-L10-1 scope ruling (sitting C-5).
6. The sitting's group-(d) rows (E-1..E-11), E-11 expiring today.
7. Terminal-review attestation + step-6 exact-byte confirmation
   scheduling inside the fuse (r4-3) — Ed's two in-fuse touchpoints.
