# Restart close: PRs #61–#63 merged at audited heads; site live under cap (2026-07-13)

Session shape: fresh-thread continuation executing the recorded restart
sequence from `RUN_STATE.md` (authorized by Ed verbatim: merge #61, run
the two delta re-audits at explicit xhigh, merge #62/#63, deploy the
site and check the instruction meter live), ending at a deliberate
whole-project pause point for a comprehensive audit (method consult
separately recorded).

## Deliverable check (§0)

SHIPPED. All three agent-lane PRs are merged at delta-audited heads;
the live capsule is deployed under the Lakebed cap with a clear
freshness banner; the post-merge integration review ran and its one
finding is fixed and CI-validated on main.

## What landed

1. **PR #61 (P2-049)** merged unchanged (its audit had completed in the
   prior session's gate shape: fresh lens CLEAN + lead replay + CI).
2. **PR #62 (P2-028)** merged after its delta re-audit (fresh Sol xhigh,
   read-only) found one blocker, fixed at the lead bench:
   - **DRA-001 (blocker, FIXED):** equal-but-malformed identity hashes
     were accepted as compared identity evidence (garbage == garbage →
     pass). Hash-shaped identity fields
     (`artifact_identity.sha256`/`folded_sha256`) now require valid
     sha256 hex; malformed values refuse with
     `identity_evidence_malformed`, surface per-bundle in
     `evidence_problems`, and appear in the new
     `identity_fields_malformed` payload array. Two regressions prove
     strict validation alone does NOT catch this. Ledger `P2028-5`.
   - **DRA-002 (should-fix, FIXED):** ledger completed to the promised
     P2028-1..5.
3. **PR #63 (SITE-01)** merged after its delta re-audit found **no
   blockers**; dispositions recorded on the PR:
   - D1 (executable discovery can falsely enter advisory mode off this
     machine) and D2 (node decode test executes rewritten JS, not the
     emitted TS) — ACCEPTED AS FOLLOW-UP, queue row SITE-02.
   - D3 (ledger metric-snapshot mixing) — fixed on the branch.
4. **Post-merge integration review** (fresh Sol xhigh over merged main):
   no cross-stream functional defects. One should-fix, **XSI-1**: the
   installed-wheel CI job ran only `--help`, exercising neither new
   fail-closed surface. FIXED at the lead bench: the job now smoke-tests
   the determinism-gate refusal envelope (exit 2,
   `fewer_than_two_bundles`) and the analysis-manifest installed-layout
   root refusal. Validated green on main CI.
5. **Live deploy (SITE-01 acceptance):** `npx lakebed deploy` ACCEPTED
   the 854,349-byte measured artifact (prior arc: rejected over the
   1,048,576-byte cap). Live checks: `/index`, `/status.html`,
   `/style.css`, `/api/freshness`, `/api/live-status` all 200; the worst
   shard (`/task_queue.html`, 71,864 B served) cold-decoded in ~0.5 s
   within the instruction meter; freshness reports deployed commit
   `7d3ea57` with 14/14 sources current, zero stale/moved.

## Verification ledger (lead-side)

| Gate | Evidence |
|---|---|
| P2-028 post-DRA focused | `Ran 40 tests … OK (skipped=1)` |
| P2-028 post-DRA full suite (worktree) | `Ran 1298 tests … OK (skipped=13)` |
| Real-corpus gate (both groups, post-DRA) | `determinism_supported`, `identity_fields_malformed: []` |
| Merged-main canonical suite (lead backstop for the review's environment-blocked run) | `Ran 1314 tests in 116.911s — OK (skipped=10)` |
| Main CI incl. new installed-wheel smokes | green (`MAIN-CI-GREEN`) |
| Deploy | accepted; measured mode (Lakebed 0.0.25); artifact 854,349 B / cap 1,048,576 B |
| Live routes | 5/5 HTTP 200; worst-shard cold decode OK; freshness 14/14 current |

Suite-count conventions held: worktree replays `skipped=12–13`
(sandbox/corpus gates), final main `skipped=10`.

## Process trace appendix

- **Shape:** sequential restart execution (no parallel streams); two
  read-only delta audits + one integration review, all explicit
  `--effort xhigh` (verified in the manifest rows — the prior session's
  unintended-ultra defect did not recur); two lead bench fixes
  (DRA-001, XSI-1) each with defect-shaped regressions.
- **Catches:** delta-audit layer 1 blocker (DRA-001) + 1 bookkeeping
  (DRA-002) on P2-028 — unique, no other layer saw it; 2 should-fix +
  1 nit on SITE-01 (D1/D2 deferred with dissent-free disposition, D3
  fixed); integration-review layer 1 unique should-fix (XSI-1,
  installed-wheel coverage). Lead-live layer: deploy acceptance +
  freshness + meter checks (not reachable by any static layer).
- **Interventions:** none new; wrapper effort passthrough fixed in the
  prior session held.
- **Worktrees:** p2049/p2028/site01 removed after merge (ledgers
  committed). ~25 stale worktrees from earlier arcs remain deliberately
  untouched pending the comprehensive audit (bridge dirs may hold
  evidence; R-016-class preservation applies before any removal).
- **Delegation calibration:** delta-audit p2028 | Sol xhigh | review |
  judgment-call | 1 real blocker confirmed by bench (strong); delta-audit
  site01 | Sol xhigh | review | judgment-call | should-fixes, correctly
  no blocker; integration review | Sol xhigh | review | judgment-call |
  1 unique catch, suite environment-blocked (lead backstop required —
  recurring pattern: read-only sandboxes cannot run tempfile suites; the
  lead suite replay is structural, not optional).

## State at close

- `main` = `origin/main`, CI green, canonical 1314 OK (skipped=10).
- Live capsule current at the deployed commit; drift banner clear.
- Queue heads: Window A ([QUIET-MAC + ED]) is the next object-level
  work; agent-lane heads P2-050 (needs adjudication), SITE-02
  (follow-ups), TOOL-01 (lead tooling).
- **PAUSE POINT:** whole-project comprehensive audit requested by Ed
  before further feature work; method proposal (Sol consult) recorded in
  the session summary and pending Ed's approval.

## Addendum: concurrent bridge landing (lead-verified same session)

A concurrent Ed-directed thread landed the bidirectional Claude↔Sol
bridge (`docs/run_reports/2026-07-12-claude-sol-bridge.md`) into the
same working tree mid-session. Lead investigation and verification
before commit: read the full diff set (reverse adapter
`scripts/claude-bridge-mcp.mjs` — origin/hops guards before spawn,
argv-array spawn, bounded output, timeout, empty strict MCP registry,
plan mode, read-only tools; `.mcp.json` model/effort/one-hop pins;
`codex-bridge` model+effort plumbing; policy surfaces coherent);
re-ran its verification myself: protocol checker 8/8 PASS, bridge
tests 4/4 OK, static checks clean. One cross-thread breakage found and
fixed: my P2-028 kernel retirement broke two `tests/test_gen_state.py`
fidelity cases (the bridge thread's suite run caught it; mutation
subjects moved to P2-016/P1-008, exact-ID set updated). Final
whole-tree canonical suite: `Ran 1318 tests in 111.017s — OK
(skipped=10)`.

Spend snapshot (2026-07-13 ~07:00Z, `codex-usage` 24h window): 3 xhigh
sessions ≈ 7.0M tokens / 29.9 min (this session's two delta audits +
integration review — explicit-effort fix holding); 3 ultra ≈ 17.7M /
935.6 min (the prior session's unintended-ultra residue aging out).
Weekly quota reset: 1% used.
