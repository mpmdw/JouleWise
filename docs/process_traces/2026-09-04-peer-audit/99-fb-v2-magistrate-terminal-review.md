# FB-PLANNING-METADATA-01 v2 — magistrate terminal review (apex read)

Read: read_single_count_discipline and check_single_count_cohort in joulewise/detection_floor.py (Mapping check;
required-by-label; absent vs null; rule_id must be a string BEFORE any set/dict lookup; exact keys, scalar types
and values against the canonical emitter; frozen DisciplineV1/V2 views; cohort compares admitted ids only), the
census test's exemption policy (source exemption = the census itself; exact raw-adapter/parser exceptions, no
module-wide exemptions), the documented v2 object in docs/contracts/adapter_contracts.md (planning_sizing_expression,
both roles mandatory, gating false, role prospective_sizing_diagnostic, not_an_acceptance_gate true, note naming the
two gates plus multiplicity), and the lane traces 31–47.

Design-level questions. (1) Is the ratified shape (43 Q-17-3) implemented without touching the decision rule? Yes:
two gates unchanged (the 6/5/4 witness stays direction_supported), F+B is metadata only. (2) Are frozen v1 bytes
intact? Yes: the four fill-rehearsal JSONs and df-ph-decode-floor-mint1.json are byte-identical to main and validate
through the v1 branch. (3) Is the four-round missed-consumer class structurally closed? Yes: one validating
accessor routed through every reader (271-entry census manifest, zero unclassified raw readers; four in-memory
census mutations fail; the 15/16-shape matrix across every carrier and admission path never yields TypeError).
(4) Contract text matches the emitter field for field, including the multiplicity clause (Opus S1). (5) The retired
site page is unpinned (D-136; its generator broke at 731a0a74 — a main-side defect recorded for the docs lane).
(6) Overbuild: the accessor and census are the ruled structural cure; nothing beyond.

Bench (this session, final head): the seven modules green (497 tests, one skip); frozen-file diff empty.

Verdict: LANDABLE. Full-suite replay on the merged head before merge.
