# lt-92 — Twelve-row gate ledger DRAFT, transactional installer (successor to lt-90)

Draft only. **No PR was opened and nothing was merged.** Head at drafting:
**`53d95227`** on `feat/2026-09-15-install-windows-transactional`, pushed.
`int/2026-09-15-install-windows` is frozen at `073a9763` and superseded by this
branch.

Rows are `RUN <repo-relative-path>` or `RUN <sha>`; OPEN rows say why.

| # | Gate item | Evidence | State |
| --- | --- | --- | --- |
| 1 | Independent audit by a fresh non-author reviewer | RUN docs/process_traces/2026-09-15-activation-d6888966/lt-27-refuters-fixes-delta.md | SATISFIED — three fresh auditors (contract refuter, delta 1, delta 2+3), none an author |
| 2 | Paired distinct lenses: contract + execution | RUN docs/process_traces/2026-09-15-activation-d6888966/lt-28-opus-execution-lens.md | see lt-28 — the contract lens ran as Astra xhigh; the execution lens ran as a FRESH OPUS seat after three Codex attempts failed on a tooling signature |
| 3 | Lead-written FIX contract with dictated closure shapes | RUN docs/process_traces/2026-09-15-activation-d6888966/lt-25-T1-rulings-R1-R7.md | SATISFIED — three fix rounds, each dictated; ten rulings R1–R10 recorded |
| 4 | Delta re-audit of every fix round | RUN docs/process_traces/2026-09-15-activation-d6888966/lt-30-delta-fix-rounds-2-3.md | see lt-30 — delta 1 covered round 1; delta 2 covers rounds 2 and 3 |
| 5 | Same-signature statement from every delta | RUN docs/process_traces/2026-09-15-activation-d6888966/lt-30-delta-fix-rounds-2-3.md | see lt-30 — answered ONLY by the two executed predicates |
| 6 | Opus counter-review on the near-final head | NOT-RUN | OPEN — requires a DIFFERENT Opus seat from the execution lens; not spent this session |
| 7 | Apex Fable code-reading diff gate | NOT-RUN | OPEN — magistrate-owned, not delegable |
| 8 | Overbuild / merge-ability prune | RUN docs/process_traces/2026-09-15-activation-d6888966/lt-27-refuters-fixes-delta.md | PARTIAL — the design itself is the prune (387-line shell to 81); no new constants, no duration ceiling, §3 byte-identical |
| 9 | Lead unpiped full-suite replay on the integration tree | RUN docs/process_traces/2026-09-15-activation-d6888966/lt-93-replay-and-pr-body.md | see lt-93 — sharded full suite at `53d95227` plus the acceptance script |
| 10 | Final-head fresh-eyes review after every post-review commit | NOT-RUN | OPEN — gated on rows 6 and the delta verdict |
| 11 | CI green on final head + post-merge cross-unit review | NOT-RUN | OPEN — no PR opened |
| 12 | Magistrate terminal review of the exact merge candidate | NOT-RUN | OPEN — not delegable |

## Scope notes (not contract changes)

Two WRITE_SCOPE expansions, both granted by the magistrate and both
bench-verified by it before granting:
1. **The uninstall path** (cold gate 28 Q2), same three files.
2. **`tests/test_run_night.py`**, limited to the three installer fixtures'
   launchctl stubs and the KeepAlive test, every behavioural assertion preserved.
   A third assertion of the same class (`schedule --plan` in the shell text) was
   ported by the lieutenant at the bench under the grant's governing principle
   and is **flagged for the magistrate as a boundary judgment** (lt-29).

## RESIDUAL RISK — Bridge protocol §7 (baseline and lease), stated plainly

`docs/contracts/bridge_protocol.md` §7 requires `scripts/bridge baseline` to
create an immutable manifest before **every** workspace-write session, and the
prompt to carry `BASE_HEAD`, `BASELINE_MANIFEST` and `BASELINE_DIGEST`. The
lease machinery (`bridge lease-acquire`) governs path attribution.

**Sessions that ran WITHOUT baseline or lease:**
- **The lieutenant's, before compliance began at 12:06 PDT:** the docs↔code reconciliation seat; fix rounds 1 and 2 of the old installer; the FIX-5, render-only, round-3 and edit-1 seats; the `test_run_night` stub seat; and the three workspace-write delta auditors. Every one of those sessions' work is already committed.
- **The magistrate's own seats today**, on the same footing: record 07's four seats, the GAMMA root-keys seat, and the six lanes seats — all launched via `codex-run-v3` without `--base`, with scope_action `not_enforced`.
- **Compliant from 12:06 onward:** every seat in the transactional lane carries a baseline captured on a clean tree and lease `lease-f4382692e249483db223325dfa87bde1` (expanded to six paths).

**What compensated, and it is not nothing:** every seat's output was committed
**by the lead, by explicit pathspec**, never by the seat itself, so no file
entered history without a human-directed selection; every round was audited by an
**independent refuter or delta auditor** that re-derived the evidence rather than
trusting the seat's report; and the lead **re-ran the decisive verifications at
the bench** — the module suites, the must-die campaigns and the acceptance script
— rather than accepting any seat's green. The gap is one of attribution
provenance, not of unreviewed code.

**Disposition:** recorded as a process finding, **not re-run**. The lane
**BRIDGE-BASELINE-COMPLIANCE-01** goes to the council / cold gate to decide
whether the launch procedure permanently carries `lease-acquire` + `baseline`;
under rule 11 that is not the lieutenant's or the magistrate's to ratify alone.

## Commit series

| Sha | What |
|---|---|
| `8f334b8f` | D9 operator docs (T2) |
| `e867dee9` | the three-valued fake launchctl (the instrument) |
| `6dc86461` | the system-interpreter import guard (R5) |
| `490be1a3` | the engine (D1–D8/D10) |
| `96dee838` | fix round 1 — contract-refuter findings |
| `3b339ac9` | fix round 2 — the oracle correction |
| `53d95227` | fix round 3 — the caller tests; tree fully green |
