# Opus contract-lens refuter — findings against MAGISTRATE-RULING.md r1 (2026-08-20)

(Verbatim final report of the paired refuter; basis of the r2
amendments. Worktree @ d33f34f; all cites verified there.)

F1 REFUTES (V6 authority): 14-r2-ruling.md:117-120 is not a ratified
disposition — :119 is the heading "Open items routed to Ed"; the
marker sentence (:120-122) is routed to Ed ("both seats recommend;
magistrate concurs"). D-147's ratified spec is S1-S9
(decision_log.md:8850-8854). Items routed to Ed cannot bound a values
council whose values Ed delegated (D-148 ruling 5, decision_log:171).
Aggravating: same non-resolving-anchor defect r1 registers against the
packet in R-5.

F2 REFUTES (V6 economics): family_publication_marker_schema is a
REGISTRY field (arm_readiness.py:543-545); R-4 item 3 rules post-_v4
registry edits force a _v5. UNBUILT.v0 therefore guarantees either
FAMILY_PUBLICATION unwired for the whole campaign or a _v5 to build
it. Terra's install-with-real-marker is the option consistent with R2
S8 bind-at-birth and the runsheet's construction rule
(phase2-transaction-runsheet.md:85-88). r1 inverted the economics.

F3 REFUTES (no Ed gate at the irreversible point): runsheet step 6
(:96-99 "publish ONLY on his explicit yes"); D-139 A3 reserved
publication confirmation (decision_log:10086-10089); R1 clause 6
(decision_log:9243-9250); D-149 retains claim publication +
exact-byte confirmation (decision_log:172). D-148.2 gate-authorizes
merges, not family publication. R-4's order omits the gate.

F4 REFUTES (V3 not assemblable): arm_readiness.py:1622-1627 requires
positive horizons for every EXECUTION_BOUND policy;
require_resolved=True rejects ED_RESERVED. r1 supplies 12/16 and
marks four "non-authoritative" WITHOUT bytes.

F5 REFUTES (V2 placement): R1 clause 7 requires environment-comparison
semantics "resolved in the single registry" (decision_log:9306-9308).
r1 resolves the registry token to a no-op and relocates the real
comparison to author-side vocabulary — unregistered, outside the
readiness_* census, edit-able without council: the pattern V6's canary
forbids. D-139 A3 reserved env-fingerprint comparison semantics
(decision_log:10084-10086); RECORD_ONLY is a net relaxation of a
fail-closed seam ruled by council rather than Ed.

F6 REFUTES (campaign envelope unchecked): arm validity =
min(evaluated_at + capability, *evidence_expirations)
(:6221-6242) with freeze-bound items included (:6146-6149); boot
mismatch raises readiness_record_expired (:4262-4268). Under V3 every
_v4 arm/consumption is capped at freeze-0004 + 24h, one boot session.
Ratified budgets ~6.28h + ~6.48h per pack (decision_log:8917-8920) +
contrast + shakedown-first: ~12.8h+ of the 24h, no reboot. r1 does the
arithmetic nowhere and R-4 carries no scheduling constraint —
structurally re-arms the same lapse at _v5 cost.

F7 WEAKENS (R-2 grounds): "R1 clause 5 bars revalidation" governs the
33 expired v1 receipts' migration (decision_log:9238-9240), not a
general expiry rule; D-131 has no such clause and its cold gate said
the opposite ("it nowhere says time forces reissue",
2026-08-15-r1-freeze-lifecycle-consult/coldgate-adjudicator-ruling.md:44).
Executed the check the seats did not: same-family re-authoring is
closed BY CODE — generate_freeze_receipt returns the idempotent replay
when a plan-pinned freeze receipt exists (:5437-5477); next ordinal
derives only from --predecessor-pack-root with generation parsed from
the pack DIRECTORY NAME (:5427-5432, :5489-5500). Right answer, wrong
authorities.

F8 WEAKENS (V5 measured after frozen): both rehearsal conditions
unmeasured; R-4 schedules the only measurement after the bytes are
frozen, no abort clause. Unpriced alternative: harvest author→arm→
consume on live _v3 before 17:00Z (rehearsal-operator-card E-4→E-10;
ED-FIRST steps, card written against _v2) — an Ed-decision item inside
a 5-hour fuse that r1 never surfaced.

F9 WEAKENS (executability): (a) D-148.1 freeze-mint license
precondition not carried; (b) "clean-arm dry run" conflates dry-run
(DRY_RUN_REHEARSAL) with a receipt-consuming arm under D-078;
(c) "runsheet step-7 refusal" mis-anchors (runsheet step 7 is
Post-publication; R-4's own step 7 is kernel rows); (d) no D-149
automation analysis of the 300s horizon, which packet 05 demanded.

F10 REFUTES (D-144 BIG dropped): 07-council-brief.md:23-28 proposed
BIG for magistrate confirmation (gauntlet + Fable final review + one
more pre-merge seat pass). r1 contains no occurrence of BIG/D-144/
gauntlet. Precedent (D-146 ruling) carries the classification block.

F11 NO-ATTACK (R-1 counting verified: 23 leaves / 16 unique).
F12 NO-ATTACK (spot checks held: patterns admit _v4; grandfathering
receipts 11+1 confirmed by direct read; archival sha matches; class
census confirmed; V2 frozenset sufficiency confirmed; V3 24h = status
quo, no D-139 A3 horizon conflict).

RECOMMENDATION: do not ratify as composed — REMAND for amendment
(blocking: F1+F2, F3, F4, F5, F6, F10). Survivable: R-1, R-5, R-6,
censuses, V4 spellings, and R-2's conclusion on F7's substituted
grounds. V6: reopen against terra's binding set with the marker built
at _v4 birth, or put to Ed explicitly.
