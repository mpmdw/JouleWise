# 2026-07-12 — Agent-lane triple: SITE-01 + P2-049 + P2-028 (+ queue reconciliation)

## Deliverable check (§0)

The session's primary deliverables were the next [AGENT]-lane artifacts after
the C-028 close. SHIPPED to PR (not yet merged): P2-049 (PR #61, fully gated,
merge blocked only by a harness permission denial on lead self-merge), P2-028
(PR #62), SITE-01 (PR #63). Bookkeeping deliverables landed on main: the
post-#59/#60 queue reconciliation (`ec7814b`), the C-028 spend-snapshot
addendum (`7c075ae`), and the P2-028 kernel authority-pointer fix (`507f600`).
NOT shipped: the live Lakebed redeploy (post-merge, lead-owned) and the two
delta re-audits (blocked by upstream outage, owed pre-merge on #62/#63).

## Product outcomes

- **Queue reconciliation**: INT-59 + DOC-008 retired to Completed (D-023
  evidence cells); DOC-008 removed from the state kernel — DOC-010's trigger
  converted to an `event` dependency (the generator requires pending task
  deps to name live tasks); pinned fidelity tests updated (live set 32→31);
  `gen_state.py --check` green. Fresh-head verification: `Ran 1258 tests,
  OK (skipped=10)` at `194ea39`.
- **P2-049** (PR #61): explicit-root-or-fail-closed resolution in
  `analysis_manifest.py` via a lazy `_resolve_repository_paths` resolver;
  installed layouts refuse with an actionable two-marker message; explicit
  roots stay authoritative; manifest identity untouched. Lens CLEAN; lead
  replay 24 focused OK + live refusal probe + suite 1261 OK/12; CI green.
- **P2-028** (PR #62): `joulewise determinism-gate` CLI verb +
  `determinism_gate.py` (744 lines) + 38 tests. Named verdicts; canonical
  config-hash comparability; identity-provenance comparison with honest
  absence recording; per-item eligibility {succeeded, capped} with
  cross-sibling status matching; fail-closed on duplicate JSON keys,
  `--output`-inside-bundle, zero/one bundle, zero items. Both real rep
  groups formally `determinism_supported`. Lead gate: suite 1296 OK/13.
- **SITE-01** (PR #63): eight bounded gzip+Base64 page shards, all 45
  pages/aliases kept; measured Lakebed artifact 865,973 B vs 1,048,576 cap
  (17.4% headroom); pack postcondition prefers MEASURED artifact (estimator
  demoted to labeled advisory — regression proves it misses non-generated
  growth); validator scan covers all server sources + omitted-initializer
  loop forms; node-driven shard round-trip test. Lead gate: measured-mode
  pack + suite 1271 OK/12.

## Verification ledger (lead-side tails)

| Gate | Tail |
|---|---|
| Main intake @194ea39 | `Ran 1258 tests ... OK (skipped=10)` |
| p2049 focused | `Ran 24 tests ... OK` + live refusal probe |
| p2049 full (worktree) | `Ran 1261 tests ... OK (skipped=12)` |
| p2028 focused (final head) | `Ran 38 tests ... OK (skipped=1)` |
| p2028 full (final head) | `Ran 1296 tests ... OK (skipped=13)` |
| p2028 real corpus | both groups `determinism_supported`, identity fields recorded absent |
| site01 pack (measured) | `865973 bytes (budget 943718; cap 1048576; Lakebed 0.0.25)` |
| site01 full (final head) | `Ran 1271 tests ... OK (skipped=12)` |

## Restart instructions (next session)

1. Merge PR #61 (fully gated; harness denied lead self-merge — Ed clicks or
   re-authorizes). 2. When upstream is stable: run the two delta re-audits
   (fresh read-only Sol, **`--effort xhigh` EXPLICITLY**) over the final
   heads of #62 and #63; triage; then CI-green merge both. 3. After #63
   merges: regen site on main, pack (measured mode must pass), `npx lakebed
   deploy`, verify the five endpoints + the instruction meter on a cold
   worst-shard request, clear the freshness-drift banner, append the Lakebed
   feedback entry. 4. Window A remains the [QUIET-MAC + ED] head.

## Process Trace Appendix

**Shape.** S1 bookkeeping (bench) + three standard-tier Sol pipelines in
worktrees (site01 / p2049 / p2028), disjoint footprints. Design rounds were
folded into implementation prompts (DESIGN-section requirement) rather than
separate pre-rounds — judged proportionate for these scopes.

**Catches (unique per layer).**
- Implementer (p2028): kernel P2-028 authority pointer stale — REAL, but its
  proposed correct home was ALSO wrong; lead archaeology found the CP-5
  resume report. Fixed on main (`507f600`).
- Contract lens (p2028): 5 blocker claims → lead bench adjudication:
  B2 (True==1 config laundering) CONFIRMED; B5 (--output overwrites input
  evidence) CONFIRMED; B3 partially refuted (bundle-level covered; per-item
  variant real); B1 ruled as design (identity-provenance comparability with
  honest absence recording); B4 reproduce-first (confirmed in fix round).
- Test-audit lens (p2028): 6 should-fix coverage gaps incl. SUT-imported
  constants and the Unicode NFC trap — all inspection-verified, no refuters
  spent.
- Runtime lens (site01): estimator-drift proof (105 kB payload passes
  estimate, real artifact over cap) — drove the measured-mode postcondition
  (SITE01-4); narrower-than-Lakebed loop regex; incomplete source scan.
- **Lead gate (validated the doctrine again): the p2028 fix round's literal
  `succeeded`-only per-item rule would have refused legitimate `capped`
  campaign cells** (AP capped-cell rules) — caught at the lead gate, fixed
  as FIX-14 with ledger supersession. Fix rounds introduce defects: third
  occurrence on record.

**Interventions.**
- I-1: codex-run-v3 `--write-scope` requires a `WRITE_SCOPE:` field in the
  prompt body — 3 instant rc=64 launch failures; folded to codex-delegation.
- I-2: upstream (chatgpt.com backend) stream-disconnection outage killed the
  site01 fix round (206k tokens in), two delta-audit attempts (one exited
  "OK" with a THIN-OUTPUT empty report — wrapper defect: stream death can
  masquerade as success), and the site01 resume (watchdog SIGTERM 143).
  Recovery: session resume preserved the fix round's completed work (all
  FIX-1..5 verified landed by lead inspection); delta re-audits deferred.
- I-3: **every Sol session this arc ran at `ultra` effort** — 
  `~/.codex/config.toml` sets `model_reasoning_effort = "ultra"` (C-028
  residue) and codex-run-v3 passes it through when `--effort` is omitted.
  Violates the xhigh-default doctrine (global rule 10); explains the weekly
  quota draw 22%→32%. Mitigation: explicit `--effort` on every future call
  (skill fold); wrapper default fix queued on TOOL-01; config residue is
  Ed's call (also affects his interactive sessions).
- I-4: harness auto-mode classifier denied the lead self-merge of PR #61
  (policy-authorized but harness-blocked; not worked around) and was itself
  intermittently unavailable during the upstream outage.

**Delegation calibration (schema v2).**

| id | to | unit | altitude | outcome | catches | lead-rework |
|---|---|---|---|---|---|---|
| p2049-impl | sol-ultra* | impl | design-freedom | one-shot-clean | — | none |
| p2049-lens | sol-ultra* | review | pinned | clean-useful | test-audit confirmations | none |
| p2028-impl | sol-ultra* | impl | design-freedom | clean+finding | kernel pointer (half-right) | pointer archaeology |
| p2028-lens-contract | sol-ultra* | review | pinned | high-yield | 2 confirmed blockers + 1 design Q | bench adjudication |
| p2028-lens-tests | sol-ultra* | review | pinned | high-yield | 6 real gaps | none |
| p2028-fixround | sol-ultra* | fix | pinned FIX-1..13 | clean-with-defect | — | FIX-14 ruling (capped) |
| p2028-fix14 | sol-ultra* | fix | pinned ruling | one-shot-clean | — | none |
| site01-impl | sol-ultra* | impl | design-freedom | one-shot-clean (strong design) | byte-breakdown scout | none |
| site01-lens | sol-ultra* | review | pinned | high-yield | estimator-drift proof | none |
| site01-fixround(+resume) | sol-ultra* | fix | pinned FIX-1..5 | complete-despite-outage | — | lead verified landing |

*unintended ultra — see I-3. Design-freedom delegation again ran hot: the
site01 shard design (instruction-budget-aware, Base85 alternative rejected
with quantified loop-body evidence) beat the lead's rough pagination prior.

**Yield + spend.** Layers: implementer flags 2 real catches (1 half-right);
fresh lenses 3-for-3 sessions with unique catches; lead gate 1 unique
doctrine-grade catch (capped); delta re-audit layer produced nothing this
session (outage) — no drop signal, it never ran. Spend: 13 Sol invocations
(3 launch failures rc=64 excluded), ALL at unintended ultra; weekly quota
22%→32%. Fable lead: heavy bench adjudication session.

**Skill-usage rows appended to ~/.claude/skills/skill-usage-log.md.**
