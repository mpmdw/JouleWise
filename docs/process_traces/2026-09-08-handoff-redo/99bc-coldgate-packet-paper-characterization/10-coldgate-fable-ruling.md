CONTAMINATION DISCLOSURE: the harness injected the global `~/.claude/CLAUDE.md` and the auto-memory index `MEMORY.md` (one-line pointers incl. a 2026-09-08 checkpoint) before I read anything; I opened no memory file, RUN_STATE.md, repo CLAUDE.md/AGENTS.md, or doctrine. Packet sha256 verified `abef6b8a…8ce00f`; checkout `e241e0b7`.

# Cold-gate Fable ruling — Window C characterization inclusion

**Line-number note.** Registry citations in the packet drifted: DS-02/03 sit at lines 888–890 and DS-05/06 at 899–900, not 883/893. Content matches the packet's claim (all four `RETIRED_FALLBACK 2026-09-05 (D-174)`).

## Decisions

**1. Included characterization questions and explicit exclusions — Option A.**
The paper includes the four registered characterization *methods* (workload response, identical-condition null, phase accounting, drift/recovery) as prospective protocol at `prospective-comparison-protocol.md:56–78`, and includes **no** empirical characterization result. Exclusions stay exclusions: the small-difference challenge (X16, `paper_comparison_placements.md:104`, DO_NOT_START) and between-session stability (DS-07 at `results-fill-registry.md:901`, X16-between-session at placements `:105`). Nothing is restored silently.

**2. Selected custody family and producer owner — none adopted.**
The closed public wire at `paper_supply_custody.md:66–76` lists exactly five families (ReportedEnergyParents, D165Closeout, WholeWindowVerdict, ClaimEvidence, TransferProjection); no complete characterization-report family exists, and `paper_comparison_placements.md:30` and `:138` forbid inventing a sixth. All X13–X15 rows record "producer absent" (`paper_supply_custody.md:475–478`). A repo-wide search for a Python producer of `characterization_result_report` returned nothing; the only code touching characterization is the renderer's Variant-0 refusal path (`scripts/render_results_fills.py:919–923`). Under A no producer is owned. Option C is rejected outright: extending Claims or Whole-Window custody would authenticate floor-building blocks as characterization evidence, which `prospective-comparison-protocol.md:77` forbids, and `paper_supply_custody.md:106` already states related parents do not extend grants.

**3. Prospectively frozen comparator mode and disjointness proof — preserved, not exercised.**
The schema's predicate (`characterization_result_schema_v1.json:6`, `c2_floor_mode.activation_predicate`) selects `issued_floor_comparator` only if a same-cell operative floor with a strictly earlier freeze ordinal exists AND its evidence digests are disjoint from the null-ladder digests; otherwise `heldout_train_test`; evaluated once at freeze, recorded in `selected_at_freeze`, never re-evaluated. `selected_at_freeze` is `null` at this checkout. DS-01 (registry `:887`) shows no operative floor issued, so if a campaign were ever frozen today the predicate would select `heldout_train_test` (ten blocks per magnitude, guard factor 1.5). Ruling: the paper carries the predicate verbatim as method; no mode is declared selected. Disjointness proof under A: **NOT APPLICABLE**, no ladder digests exist to compare.

**4. Member census, predecessor/report publication, anti-selection — carried as design requirements only.**
Minimum basis (forty bundles over five lengths; five disjoint A/B/B/A blocks per magnitude; twenty-four bundles plus two brackets; six references, three held-out probes, three cooldown pairs) at `prospective-comparison-protocol.md:176–183` is explicitly "design requirements, not counts collected for this paper" (`:182`). Anti-selection rule (`characterization_result_schema_v1.json:2–3`): predecessor link required, both reports publish, sequence reported never the favourable member. Under A these obligations bind any *future* campaign and are stated as such; the paper reports zero members and zero reports. Ordering gates (`criteria_not_prior`, `limit_supplier_not_prior`) remain in the schema unchanged.

**5. Withdrawal and no-characterization wording.**
Adopt, without edit, the existing Variant-0 text already installed and rendered by the refusal path (`docs/paper/fill-rehearsal/rendered-refusal.md:18–22`; `render_results_fills.py:921`):

> No characterization result, row-level outcome, or between-session contribution is reported. The collection must retain the paper's calibration, admission, custody, floor, and whole-window verdict rules. Its paired per-token comparisons must also require both arms to record the SAME tokenizer identity; no resulting number may be compared with a stack carrying a different tokenizer.

Plus the protocol sentence at `:72–78` ("registered characterization methods, not issued empirical results … No such report is supplied in this submission"). Withdrawal wording at `:180–182` ("Failure withdraws the relevant per-token conversion, floor, or phase-specific claim") stays as a conditional on a future campaign. "D is not a fourth global outcome" (custody `:475`) is preserved: no D-prefixed characterization outcome renders.

**6. Adopted placements/grants and implementation scope — none.**
X13, X14, X15 (both rows), X16 (both rows) remain `PROPOSED_STOP_FILL` at `paper_comparison_placements.md:100–105`; the P.2 summary row at `:134` stays UNRESOLVED / STOP_FILL. No supply-map key, no grant, no producer, no schema field is added. Implementation scope is zero code; the only text change permitted is confirming the disposition sentence in item 5 appears once in the successor's P.2 and once in §6 Variant 0.

## Charge answers

**(1) Soundness or scope?** Scope only. The comparison's soundness rests on calibration, admission predicates, floors, and whole-window verdicts, all of which the protocol treats as separate from characterization (`:56`, `:60–61` "before any campaign result may rely on the instrument" is a *claim about the instrument*, and the paper makes no instrument-generality claim at `:633`). Omitting characterization narrows what the paper may say about the instrument, which the advisor will notice, but introduces no circularity, post-hoc choice, or unauthenticated number. Including it via an incomplete custody route (Option C) *would* be a soundness defect.

**(2) If included, minimal closed route and mode.** Option B only: a new sixth family with its own producer, complete report census, `selected_at_freeze` fixed at freeze, predecessor link, and per-row grants, adopted through `open_paper_input` before any collection. Mode would be `heldout_train_test` unless an earlier-ordinal same-cell floor with digest-disjoint evidence is issued first. That is a separate design ruling, not opened here.

**(3) Exact wording under A.** The two block quotes in item 5, verbatim.

**NOT EXECUTED:** running the renderer's Variant-0 path end-to-end; a runs-root scan for issued floor artifacts (registry state relied on instead).

**Verdict: A — omit empirical Window C characterization; retain prospective methods, the frozen comparator-mode predicate, and the installed Variant-0 refusal wording; adopt no family, producer, grant, or placement.**
