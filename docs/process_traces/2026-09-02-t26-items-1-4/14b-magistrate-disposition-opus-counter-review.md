# Opus counter-review (file 14, PR #273 @ 10845c14) — magistrate disposition 2026-09-02

Opus report verdict: `SHOULD-FIX 5`, `NIT 10`, plus one observation. Nothing
is applied silently; each row names the disposition and where it lands.

| Finding | Disposition | Where |
|---|---|---|
| SF1 — ruling §B4 "S9 rows register at the bench" never done; D-170 carries no affirmative clause | ACCEPTED. Kernel half: seven S9 rows drafted by a Sol seat into file 15 (detached worktree), applied to `state_kernel.json` at the bench with the hard/start/pending D-170 dependency. Doc half: D-170 body sentence naming the seven row IDs (terra fix round). | file 15, bench kernel commit, terra fix round |
| SF2 — `tests/test_docs_freshness.py:628-637` pins the dated-ruling census to an exact two-path list; fails once the t26-c lane's `16-MAGISTRATE-RULING-gateledger-splitter.md` is present | ACCEPTED (the integration-tree suite exposes it). `assertIn` on the two known paths; census non-empty; shape loop kept. | terra fix round |
| SF3 — `_assert_clause_map` demands exactly three cells; contract §1 reads as permitting a quote column | ACCEPTED. Columns located by header index; body rows must match the header's cell count; the three required cells non-empty; contract wording "at least these three cells (a quote column is permitted)"; four-column positive control + cell-count negative control. | terra fix round |
| SF4 — `tests/test_gen_state.py:607` comment arithmetic "116 + 3 = 119" vs assertion 120 | ACCEPTED. Comment corrected to the four rows added on this lane. | terra fix round |
| SF5 — `decision_log.md:10529` cites the superseded enforcement paragraph `COLD-GATE-RULING.md:270-282` | ACCEPTED. Quote keeps its measured source span; sentence points at the dated addendum. | terra fix round |
| NIT1 — S1/S2 cited without the ruling path (§1, §10 row, playbook M0) | ACCEPTED | terra fix round |
| NIT2 — "biting assertion" and "dated ≥ 2026-09-03" unglossed at first use | ACCEPTED (Ed's writing standard: first-use test) | terra fix round |
| NIT3 — `NOT PINNED:` scope (first cell only; whole row skipped) undocumented | ACCEPTED | terra fix round |
| NIT4 — mid-file T-0 Horizon AMENDED paragraph duplicates the t26-b lane's custody-form record (STRUCK marker + EOF addendum) | ACCEPTED. This branch's paragraph is deleted; the t26-b lane (merges last) is the single record. Between the two merges main carries the amendment in D-170 and the T26 ruling only — accepted. | terra fix round |
| NIT5 — gen_state's evidence-pointer grammar for satisfied decision deps undocumented in the How-To | ACCEPTED | terra fix round |
| NIT6 — D-170 close sequence not written down | RECORDED here: D-170 moves to `adopted` in the post-merge kernel batch after all three T26 PRs (#273, #275, #274) are on main; the row `T26-RULING-INSTALL-01` retires in the same batch; `V5-TRANSACTION-01`'s D-170 dependency moves to `satisfied` with the pointer at the arm_readiness 600 s boundary regression (t26-b lane); the S9 rows' dependencies move to `satisfied` with the same pointer class, one per mechanism they wait on. | this file |
| NIT7 — `_has_executed_evidence` heading match (`tests/test_docs_freshness.py:139-143`) is not fence-aware: a `## Executed evidence` line quoted inside a code fence opens a section | RECORDED, no change: the opened section must still satisfy a branch (Opus: "harmless today"); a fence-aware scanner is a second edit to the B1 predicate and not justified by materiality (same reasoning as file 13). | this file |
| NIT8 — `D110-MINT-DEP-RECONCILE-01` sits in the `agent` lane (`state_kernel.json:1182`) while ruling §B3 says "Ed's call, batched" | DELIBERATE: Ed's 2026-08-14 instruction (magistrate rules all non-hardware/sudo items) makes the reconcile the magistrate's to execute; the call itself is still put to Ed in the batch email, and the row moves to `ed_external` only if Ed takes it. | this file + Ed batch |
| NIT9 — `accepted` gloss lost "binding until revisited" | ACCEPTED | terra fix round |
| NIT10 — item 2's ruled text lives at D-170 with D-118 (`decision_log.md:7830`) holding a pointer, inverting the ruling's named ONE home (`COLD-GATE-RULING.md:155-156`) | RECORDED, no change: text-once-plus-pointer is the better shape and D-170 declares the inversion at `:10536-10537`; the record here keeps it from being silent. | this file |
| Observation — B1's `NEEDS-RULING-` exclusion applies to branch (b) only (`tests/test_docs_freshness.py:127-131`, faithful to `COLD-GATE-RULING.md:322-324`); a future dated directory holding a `NEEDS-RULING-*-MAGISTRATE-RULING.md` file (live example one day outside the cutoff: `docs/process_traces/2026-08-28-workload-scored-v6/NEEDS-RULING-01-MAGISTRATE-RULING.md`) would be selected by branch (a) and required to prove executed evidence of a question | RECORDED for the next cold-gate packet as a ruling-level gap; not an install defect. | next cold gate |

Rule-11 check: SF1–SF5 are five distinct defect classes (missing registration,
over-pinned census, cell-count contract mismatch, comment arithmetic, stale
citation); none is a second fix on a defect already fixed on this lane (luna
226 closures: selector/test-limb/document shape; Sol 230: citation path
predicate + acceptance wording). No same-signature trigger. The fix round is
one seat (terra xhigh) followed by a delta re-audit by a different model.

Executed at the bench this session: `git checkout --detach 10845c14` in
`JouleWise-wt-t26-a2` (Sol S9 draft seat); the kernel read confirming zero
`S9-` task IDs among the 120 tasks (`python3 -c` over
`docs/process/state_kernel.json`); agent-lane max rank 119 observed.
