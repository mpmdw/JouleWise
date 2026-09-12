# MAGISTRATE SYNTHESIS — evauth cold-gate sitting (2026-08-12, T6)

Split verdicts synthesized by the magistrate per rule 9 (never majority-voted).
Sitting: cold Fable adjudicator (`ruling-adjudicator.md`) + paired Opus
contract-lens refuter (`ruling-refuter-brief.md`) on `packet.md`. Trigger:
second fix round on defect B1 (mandatory, rule 11).

## Adopted condition set for the round (final, merge-gating)

1. **C1 — public-surface hygiene lock** (adjudicator 1+2, refuter-corrected):
   `DERIVERS` → `_DERIVERS` as a PLAIN dict (no MappingProxyType — both
   readers demoted it; the refuter proved it rebindable and misleading);
   `DERIVERS` AND the twelve `derive_*` names dropped from `__all__` (the
   refuter's sharper census: the public namespace keeps only the author
   function, the error class, and the four constants); the sentinel tests
   repoint at `_DERIVERS` (mock.patch.dict is restorative — the delta's
   "leakage" reading corrected); regression asserting the exact `__all__`
   census and `not hasattr(module, "DERIVERS")`.
2. **C2 — self-binding + same-tree guard** (refuter NEW-FINDING A; subsumes
   adjudicator condition 11 mechanically): `joulewise/arm_readiness_evidence.py`
   and `scripts/author_arm_readiness_evidence.py` enter the primary artifacts
   of at least one authored kind via `_committed_artifact` (pins the deriving
   code in the receipts AND makes authoring from an uncommitted tree refuse);
   entry guard: `readiness._repo_for_pack(root)` must resolve equal to the
   CLI's own REPO_ROOT, named reason code on mismatch. Regressions for both.
3. **N1 — hermetic child env, RESCOPED** (adjudicator 3; included over the
   refuter's deferral because it is the same ambient-input defect family and
   cheap): allowlisted env (no `os.environ.copy()`), `LC_ALL`/`LANG` pinned,
   `-I` retained, `-B` explicit; hash-seed determinism NOT required (an `-I`
   design property, recorded as accepted).
4. **N2 — process-group supervision** (both readers): `start_new_session=True`
   + kill the whole group on completion AND timeout; the two prescribed
   grandchild regressions.
5. **Suites green** ×2 interpreters (author suite + dry-run + integration +
   schemas), no new skips.
6. **Delta re-audit with a fresh forgery attempt** against the new surface;
   a third same-signature public injection route → consult, never round 3.
7. **Land clean**: rebase onto current origin/main, commit all three files,
   re-run 1–5 at the landed HEAD.

## Freeze-night gate (tonight)

8. Author-then-reauthenticate at the freeze HEAD, LEAD-RUN (adjudicator 8).
9. Live boot-session confirmation vs `sysctl kern.bootsessionuuid`
   (adjudicator 9).
10. Canonical-suite disposition — **ALREADY SATISFIED**: the magistrate's
    dual-interpreter canonical at dc162bc ran to completion (3,216 tests ×2;
    the only errors are the three registered WO-CRASHMATRIX-RELIABILITY
    load-pathology tests, hosted-green at the same content on fresh runners
    across four PRs today). Lead triage recorded here.
11. Subsumed by C2.
12. **C3 runbook** (refuter NEW-FINDING D): the freeze checklist and the CLI
    PASS payload carry the exact sequence — author → `git add` of the TWO
    explicit evidence/source paths (never `git add .`) → commit → push to
    origin/main equality → freeze; plus the recovery fact (reboot or HEAD
    change voids all twelve receipts; `git rm -r` both directories before
    re-authoring).

## Registered, NOT required tonight

- Refuter NEW-FINDING B: consumer layers validate custody, not truth — the
  packet's defense-in-depth premise was FALSE; the author + its C2 code
  binding is the sole truth-establishing layer. Registered as a D-134
  limitation for the queue (candidate: an arm-time spot-re-derivation row).
- Refuter NEW-FINDING C: the receipts' `committed_pack_tree_sha256` is
  unverifiable by construction (pre-evidence digest; freeze passes
  pack_sha256=None). Registered; field documented as informational.
- Any further in-process attribute-substitution hardening: the class is
  refuted (probes 1–4); the boundary declaration in the adjudicator's Q1(a)
  is adopted as corrected by the refuter's cl.6 reading (an in-process
  Python caller is not an "operator" under D-134 cl.6).

## Record

The pairing again produced what neither reader alone did: the adjudicator's
executed re-verification + boundary adjudication, and the refuter's four
probes (1-of-53 census; forgery through the REAL deriver with DERIVERS
untouched) plus the sitting's load-bearing catch — the author's own bytes
bound to nothing (NEW-FINDING A) — which no prior layer (two lenses, the
fix round, the delta, the packet author) saw on the same bytes.
