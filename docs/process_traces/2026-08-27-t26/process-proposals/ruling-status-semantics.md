# PROPOSED process rule (magistrate, 2026-08-27) — NOT ratified; routes to a cold gate per doctrine rule 11

## Rule text (proposed)

A decision-log ruling that carries an IMPLEMENTATION CLAUSE (a value that
"enters" a manifest, a check the code "refuses" on, a runbook line, a
generator output) is recorded with status `decided`, not `done`, until the
index row cites the commit or PR that installed it AND names the
producer-side check that refuses its absence. The kernel work-selection
gate treats `decided` clauses touching a transaction as OPEN pre-window
items (W-list entries), never as satisfied.

## Forcing evidence

Three instances in one session (T26, 2026-08-26/27) of a ruled contract
with no route or no check in code: CONSUME-CONFIRMATION-SUPPLY-01 (Opus
3f), the launcher runbook arguments (S1 runbook delta, PR #205), and
D-157 (D-139 A2 ruled 2026-08-17, never installed; estate 10 passed while
minting an inadmissible manifest). Each was found by a reader, not by the
instrument. The cost of the third was one to two transaction nights.

## Why a cold gate

This amends how rulings are recorded and how the kernel selects work —
a meta-process change the magistrate may not ratify alone (rule 11:
"ratifying or amending process rules" is forbidden to the lieutenant and
routes the magistrate's own proposals to a cold Fable instance paired
with an Opus contract-lens refuter). The S9 ruled-not-installed sweep
supplies the packet's evidence; the cold gate convenes when the sweep
lands.

## Addendum (S9 sweep, 2026-08-27) — second proposal for the same cold gate

**The D-118/D-121 merge-gate ledger has no mechanical existence**: no PR
template, no CI job, no mention in `orchestration.md`, `agent_playbook.md`,
or any loaded skill. Every merge since D-118 has been gated by memory.
PROPOSED: a PR-template checklist that names the D-118 gate items and a
CI check that refuses a merge whose body lacks the ledger block. Same
cold gate as the ruling-status rule; the S9 sweep is the packet.

## Addendum 2 (S2, 2026-08-27) — cold-gate item: the T-0 ruling's 5 s bound is ill-typed

MAGISTRATE-RULING-T0-UNATTENDED's ruled `validity_origin − R1_completion
≤ 5 s` compares CLOCK_UPTIME_RAW (validity origin, ordinary monotonic on
Darwin) with CLOCK_MONOTONIC_RAW (R1 endpoints) and cannot hold at HEAD's
derivation order. The implementing stream stopped correctly (endpoint
published on the right clock; no bound; no inert substitute). Reinterpreting
a prior verdict is a mandatory cold-gate trigger; the cold seat rules the
clock and the constant. Packet: PR #212's `impl/reason-code-coverage-delta.md`.
