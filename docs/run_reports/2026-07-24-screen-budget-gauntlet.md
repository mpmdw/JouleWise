# 2026-07-24/25 — NEG-8 screen+budget: four audit rounds, a new refuter pairing, PR #85, and the capsule CI unblock

Continuation of the collection-arc report (2026-07-23). The Ed-ratified
SCREEN + BUDGET design (D-078 clause 10, C-044 debate) was implemented,
put through an adversarial gauntlet that ran until dry, landed as
PR #85, and then forced a site-capsule repair before CI would go green.
This report records the arc, the numbers, and what was deliberately
left undone.

## Arc summary

The wave itself was checkpointed pre-audit at `e7cbf35` (23 files,
+3115/−243 on `02f8773`) while origin/main had moved to `125a48d`. The
rebase onto `125a48d` was clean by construction: `125a48d` touched only
`PROJECT_STATUS.md`, `docs/council_log.md`, `docs/decision_log.md` and
`docs/site/DRIFT.md`, none of which the wave's 23 paths overlap. The
rebased wave is `b120d07`.

From there the gauntlet ran: four audit rounds (fresh read-only Sol per
round; rounds 1–3 xhigh, round 4 high), per-severity refuter tiers using
the new **Opus-contract + Sol-execution** pairing, three Sol fix rounds,
and lead bench fixes between them. Round 3 came back with three
should-fix and no blockers; round 4 with one should-fix (test honesty);
that was dry. The merge range `125a48d..c3e2647` is 56 files,
+6012/−439.

The tail of the session was site infrastructure: `release-chain` had
been failing on main since the decision log crossed the capsule's
30,000-byte page-shard budget, and the audit-era addenda made it worse.
The durable fix (deterministic decision-log pagination + D-076
artifact-cap redirects) landed on the branch as the CI unblock, and the
Lakebed capsule was redeployed after the merge.

## Commit chain

| Commit | Role |
|---|---|
| `b120d07` | NEG-8 screen+budget wave (rebased pre-audit checkpoint `e7cbf35`) |
| `69b65e5` | D-078 clause-10 addendum 2 — wave spellings + anchor-fallback ruling (lead bench, audit F5) |
| `ad75542` | Fix round 1 — F1 dispatch, F3 allowances, F4 anchor gate, F7 regressions, F2 documented-superseded |
| `315810a` | D-078 clause-10 addendum 3 — terminal mock bar + config-derived mockness (lead ruling, round-2 triage) |
| `a5a7acf` | Trim addenda 2/3 prose under the 30k capsule shard budget (lead bench; registry content unchanged) |
| `907ee58` | Fix round 2 — G1 symmetric/eligibility-scoped drift groups, G2 config-derived mockness, A1 terminal mock bar, G3 bounded registry regression |
| `dbf6339` | Fix round 3 — named error on malformed basis values, `bundle_strict_invalid` at the whole-window barrier (incl. the NEG-8 sentinel route), positive-path integration coverage |
| `19e15d9` | Restore the two affected-contrast assertions in the replacement companion (round-4 residue, lead bench) |
| `60b12af` | Deterministic decision-log capsule pagination + D-076 artifact-cap redirects (CI unblock) |
| `c3e2647` | Merge PR #85 |

## The gauntlet

Round 1 (5 blockers) found the mechanisms that mattered: the row shape
itself selecting the legacy gross-only evaluator, missing allowances
silently becoming no allowance, the existing-bundle re-verdict bypassing
the anchor-fallback gate, and a refusal-registry gap that was a live
test failure. Round 2 found the coordinated downgrade v2 (strip basis
*and* the whole drift group together) and the mock-label seam. Round 3
found a TypeError on malformed basis values, a telemetry-triangle
downgrade into the frozen arm, and lost positive-path integration
coverage. Round 4 found two omitted assertions.

The refuter pairing changed the triage outcome in every round it ran.
The contract lens collapsed one blocker outright (F2 — the "broken
frozen replay" claim rested on a misread of the freshness addendum's
scoping; it landed as documented superseded wire, not code), re-priced
two more (G1 as a subclass of registered limitation L1; G2 against the
ratified non-mock carve-out and D-030's strict/raw-evidence binding),
refuted two proposed fixes before they landed, and produced the
session's best catch that no auditor saw: an *honest* mock member could
reach claim evidence with every mock-exempted barrier disabled — no
attacker required. The execution lens supplied the runnable proof:
stripping the drift group and restoring headline floors validates clean
(repo fixture gate `20.799350577898302 → 20.399350577898304`, exactly
its 0.4 J allowance; asymmetric removal also validates), the adjacent
reduce-layer blocker (G2A), the authoritative mockness source
(custody-bound `config().hardware_target.telemetry_backend`), and the
`mock:*` tagged-source caveat that saved the fixtures. Where the two
lenses split (G1, G2) the lead synthesized rather than voted. Full
per-layer catch record in the council log (C-033).

## Lead gates

Full-suite runs at each commit gate (lead-side pytest on the
lead bench, macOS/py3.13; session-transcript receipts only — these
intermediate heads have no CI runs, the PR-head CI below is the
independently receipted gate):

| Head | Result |
|---|---|
| `e7cbf35` | 2113 passed / 21 skipped, **1 failed** — the D-078 registry test, fixed by addendum 2 |
| `ad75542` | 2121 passed / 21 skipped |
| `907ee58` | 2128 passed / 21 skipped |
| `dbf6339` | 2140 passed / 21 skipped |
| final head | 2141 passed / 21 skipped, +1 battery-timing flake that passes on rerun |

Sol's independent unittest runs corroborate the same trees: 2142 ran
(skipped 24) at fix round 1, 2149 ran at fix round 2 alignment, 2161
ran (skipped 24) at fix round 3, and 2163 ran / OK (skipped 22) at
`19e15d9` — the same 2141 passing tests as the final lead gate.

CI on the final PR head (run 30138589862) is green on all five checks:
`build`, `installed-wheel`, `release-chain`, `test (3.11)`,
`test (3.14)`. The preceding run (30135876410) failed on
`release-chain` — that failure is what the pagination commit fixed.

## Site capsule and deploy

`release-chain` failed on the packer's 30,000-byte runtime page-shard
budget (`MAX_SHARD_BASE64_BYTES`); zlib version variance flipped the
verdict between local and CI, so the failure looked intermittent. The
durable fix paginates the decision log deterministically at top-level
`D-NNN` boundaries with an independently enforced 24,000-byte target
(`DECISION_LOG_SHARD_BASE64_TARGET_BYTES`). Byte figures vary a few
tens of bytes with the zlib/Python environment; as measured on the
lead bench at the deployed head (py3.13, Lakebed 0.0.29): decision
pages 19,328 and 13,628 base64 bytes (≥4.6k margin each), packed
content 271,049 bytes, measured Lakebed validator artifact 974,118
bytes against the 1,000,000-byte measured budget and 1 MiB hard cap.
Final CI (py3.11) measured the same tree at 270,480 packed /
972,322 artifact bytes — the environment spread the margin now absorbs. The lead-ruled D-076 artifact-cap
redirects retire the two deep views from the capsule
(full-project-status → project-status, run-state → live-status); both
remain in git and per-page freshness provenance is preserved.

Redeployed after the merge: deploy `dep_2I04CG6tQ4t0mzY7`, capsule
config rewritten 2026-07-25T01:46Z (merge was 01:45Z).
`/decision_log.html` and `/decision_log_archive_1.html` both serve 200
live, and the main page carries D-078 and the archive link.

## Deferrals registered

- **FLOOR-BIND-01** — full-strip-vs-legacy floor discrimination beyond
  the eligibility scope stays inside registered limitation **L1**
  (TASK_QUEUE row A3, P1, READY).
- **G2A** — reduce-layer label trust in the environment and
  CPU-admission barriers (refuter-confirmed adjacent blocker).
- **Drift-bound seal authentication** (A3 in the PR body).
- **Dead no-freshness accommodation** (the round-1 adjacent finding).
- **`artifact_schema_invalid` mislabel.**
- **F6 consumer-boundary condition transport** — NOT a deferral:
  contract-REFUTED and non-obligating (the gate stays closed; the
  contract's distinctness requirement is discharged at the condition
  level, and a consumer-boundary code would itself require a registry
  amendment). Recorded as rejected; no queue row owed. The other four
  items above are owned by kernel row **CUSTODY-HARDEN-01** (G2A, seal
  authentication, dead accommodation, mislabel) or **FLOOR-BIND-01**.

## Environmental notes

Two battery-timing flakes were adjudicated, both timing-sensitive and
both passing on rerun: the P2-038 `mode='wide'` subtest (also seen
independently by Sol at fix round 2, flagged transient there) and one
unidentified ~21 s test. The machine ran on battery throughout, which
is the direct cause: **no quiet-Mac measurement was consumed this
session**, correctly — agent sessions were active the whole time.

The `codex-usage` ledger reads all zeros across both the 5h and 24h
windows with "local quota signal: unavailable in referenced session
logs". The feed is suspected broken; no spend snapshot is recorded for
this arc beyond the session counts in C-033.

## NEXT

1. **Quiet-window measurement chain** — needs AC power and a governed
   display; this is the blocking dependency for everything downstream
   (settled-reference corpus → derived bound → a8 re-verdict →
   governed extraction).
2. **Run-book landing** — `window_runbook.md` was drafted and
   lead-reviewed pre-audit and held for post-merge reconciliation; it
   should land against merged main before the next window.
3. **Bookkeeping kernel rows** — RUN_STATE / state kernel refresh for
   the deferrals above, and the C-033 council entry.
