# LEAD SYNTHESIS — cold pair on the PR #166 gate question (2026-08-20 ~23:30 PDT)

Inputs: cold-packet-166.md (lead-assembled), cold-ruling-166.md (cold Fable),
the Opus contract-lens refutation (30 findings, in the session transcript;
key claims lead-verified against docs/decision_log.md:7765-7771 and
TASK_QUEUE.md:288-295 verbatim).

## Synthesis verdict: the cold ruling's R1 severance DOES NOT ISSUE.

The refuter established, and the lead verified: (a) the recorded gate is the
D-118 twelve-item GATE LEDGER in the PR body — #166 carries none, so it is
non-merge-eligible independent of calexits ("regardless of CI state");
(b) TASK_QUEUE.md:288-295 is a standing registered rule directly governing
calexits shard failures ("re-run-once-then-investigate, never waved through
silently") that the packet omitted — packet-assembly defect, conceded;
(c) the "docs-only breaking window" bisect is FALSE — the same signature
failed on main 2026-08-19T23:08Z, before the green runs; it is an
intermittent, and aedf530's commit message repeats the false bisect plus a
UTC-mislabeled-PDT timestamp (ERRATA E-2); (d) #163-#165 had GREEN local
canonicals, so their precedent never reached #166's red-canonical situation;
(e) the paper diff adds a custody/evidence-bytes prose claim whose guarding
witness (the N-5 test, red in gate run 1 at that head post-fix) is exactly
the failing module — severance was epistemically wrong, not just
procedurally.

No severance is needed now anyway: the calexits CI fix landed (aedf530) and
both branches are rebased onto it. The honest path for #166 is to SATISFY
the gate: (1) register the defect rows below; (2) full quiet canonical at
the actual merge head 7b8f3f5, with the two red a8f1549 runs recorded
regardless of the new outcome (they are evidence about the module, never
erased by a later green); (3) a D-118 gate ledger in the PR body;
(4) recorded deviation for the a8f1549 bench cure's missing delta re-audit
(compensating layer: the refuter's own executed probes — finding 12 verified
both cures against code — plus the lead full read); (5) merge only then.

## Adopted rulings (cold R2-R4 as amended by the refutation)

R2 rows (register in TASK_QUEUE now; kernel transaction at next kernel
touch): CALEXITS-CLEANUP-RACE-CI311 (blocker; aedf530 is its candidate fix,
pending CI confirmation + retro-review — see below); CALEXITS-CENSUS-PIDRACE
(high; int('') at tests/test_calibration_exits.py:2207; fix shape: read
non-empty content, normal gauntlet); N-5 record amendment (46d710f's
"resolved" is falsified by a post-fix recurrence under load at a8f1549;
record must say so); CALEXITS-TIMING-HYGIENE umbrella (now FIVE+ mechanisms:
#121, REDERIVE, N-5, tonight's two, the 2026-08-19 parameterized-witnesses
failure, and #164's red 3.14 instance — module-wide timing audit,
should-fix).

R3 as strengthened (refuter finding 28): the deviation note for #163-#165
must cite TASK_QUEUE.md:288-295 BY NAME and state the standing rule was
breached (red shard neither re-run-once nor investigated at merge time);
local canonical greens at their heads are the compensating evidence; the
corrective convention binds: any merge over any red required check needs an
explicit recorded disposition at merge time.

R4: #167 waits for a FULL UNQUARANTINED quiet-machine canonical green at its
rebased head (in progress). The cold ruling's quarantine fallback is
REJECTED per refuter finding 29: the repo has no test-quarantine mechanism
and minting one under time pressure is the rule-11 failure shape. #167 also
requires a D-118 gate ledger before merge.

New obligations adopted from the refutation: ERRATA E-2 (UTC/PDT + false
bisect in aedf530's message and the cold packet); aedf530 retro-disposition
(assertion-widening on a claim-bearing witness landed direct-to-main without
independent review; compensating evidence: refuter finding 26's executed
probes — no RACE_EXERCISED escape hatch opened, causal account matches —
plus the terra root-cause session's own reproduction; a light independent
retro-review rides the CALEXITS-CLEANUP-RACE-CI311 row's closure).

Magistrate note, recorded for Ed: the lead's packet failed mechanical
neutrality on two counts (gate understatement, standing-rule omission) and
the cold Fable ruled permissively on that defective packet; the Opus
contract-lens refuter is the layer that caught it. Layer catch-rates:
cold Fable — verification depth + the N-5-in-head catch; Opus refuter —
five ruling-changing catches. Both layers earned their seats tonight.
