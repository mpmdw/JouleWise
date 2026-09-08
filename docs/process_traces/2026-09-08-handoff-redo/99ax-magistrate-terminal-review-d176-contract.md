# Magistrate terminal review — D-176 seat-1 contract `docs/contracts/pack_night_go_receipt.md` (interactive magistrate, 2026-09-08 ~11:40 PDT)

Merge candidate: `feat/2026-09-08-d176-stage3-ruling`, head named in the PR ledger row 12 (contract head 515fb58f +
trace commit). DOCS ONLY: the seat-1 contract for the pack-night GO receipt (`joulewise.pack_night_go_receipt.v1`),
its consumption v3 record, the consumer keywords/argv seams, the seat 2/3/4 WRITE_SCOPEs, the D-170 clause map, the
§10 wire addendum (B1–B5, S1–S6, N1–N2) and §10.1 third-pass rulings (F1–F11 + N1–N6); D-176 decision-log entry
plus a dated addendum; report 85; cold-gate packet files 15–18. No code; no seat 2/3/4 scope is issued by this PR.

## Why
D-169 stage 3 (unattended pack-night launch) was ruled by cold gate (packet 78: cold Fable 10, Opus 11, synthesis 13)
as D-176. The synthesis' §6 ordered: contract first, refuted by Opus before any code. This PR is that contract.

## Gauntlet record
| Pass | Seat | Report | Unique catches |
|---|---|---|---|
| Install 1–2 (bfedd6fa, d3cab2d4) | Astra medium | 85, 99at | — |
| Opus refutation 1 | Opus | packet 15 | B1–B5 (plan sha binding, reader mode, …), S1–S6, N1–N2 |
| Opus refutation 2 | Opus | packet 16 | F1 no consumer path to the night plan (BLOCKER), F2 GO keys collide with night_gate `_RECEIPT_KEYS` (BLOCKER), F3–F8, F9–F11 |
| Fix 4 + F3 ruling seat 5 (07dfd03a, 3a8b101e) | Astra medium | 99au, 99av | seat flagged F3 as NEEDS_RULING correctly (lineage caller passes True) |
| Opus delta 3 | Opus | packet 17 | N1 authorization row retyped to the GO path (BLOCKER introduced by the fix round), N2–N6 |
| Fix 6 (515fb58f) | Astra medium | 99aw | — |
| Opus closing delta | Opus | packet 18 | none; LAND |

Same-signature statement: each pass found a different class; the one fix-round-introduced defect (N1) was caught by
the delta and cured in one round. Rule-11 count for this lane: cold gate ×1 (design), no second fix round on the same
defect.

## Magistrate rulings recorded in the contract
F1 `--night-plan` keyword/argv; F2 GO receipt in its own create-once 0600 `night/go_receipt.json`, `night/receipt.json`
shape unchanged for every class, refused pack night writes no GO; F3 the consumption reader forwards
`require_current_boot` (live True, historical False, lineage forwards its caller); F7 `--go-receipt` argv with
omission refusal; N5 dated decision-log addendum owned by seat 1.

## Live verification (lead-owned)
Bench, rc-gated on each commit: `tests.test_docs_freshness` (31) and `tests.test_gen_state` → OK. Bench read of the
authorization row (:205) and the ten GO-path occurrences after N1. Full-suite replay: ledger row 9.

## Verdict
LAND after CI is green on the final head and the replay tail is recorded. Next: seats 2 and 3 in parallel worktrees
under the contract's §7.1 scopes (D169-STAGE3-01 implementation), seat 4 after seat 2.
