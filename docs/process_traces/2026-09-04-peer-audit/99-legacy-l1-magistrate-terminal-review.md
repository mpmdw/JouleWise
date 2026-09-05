# Legacy-L1 void cure — magistrate terminal review (apex read)

Read: the producer diffs (scripts/build_capstone.py, scripts/make_figures.py, scripts/claims_lint.py) against
main, the generated page, the claims-index dialect, reports 20/21/23/26, refuter 22, delta 24, Opus 25.

Design questions. (1) Is the cure at the producer, not the page? Yes: generate_results_page emits the void page;
make_figures renders void placeholders for every full-route artifact; claims_lint gains a first-class
voided-legacy dialect (status "voided", no metrics) and the exact-hash v1 grandfather is only ever projected as
void. (2) Can any current route assemble the voided numbers? No: refuter 22 found the --full route, round 3
enumerated all twelve artifacts, delta 24 re-ran the route from a tracked-only copy and scanned every byte;
Opus 25 re-verified zero leakage and v1 byte-identity. (3) Frozen evidence? analysis/rpt001-v1 and
figures/rpt001-v1 untouched; raw bundles untouched. (4) Contracts: the RPT-001 spec clauses contradicted by the
cure are amended by one adjudication row (C1, docs/specs/c027/ADJUDICATION.md); D-161 one-line addendum ruled in
17 Q7 lands with the decision-log edit after the cold gate. (5) Overbuild: the void SVG/CSV placeholders are
the minimum that keeps the artifact manifest and --check meaningful; make_figures' unreachable value
functions (C3) are a parked nit.

Bench (this session, this tree): tests.test_build_capstone 2 OK; tests.test_rpt001_report_slice 19 OK
(skipped 2); tests.test_claims_index_lint 30 OK; build_capstone --check OK; grep of the four means, the
retired label and "primary basis" across analysis/rpt001-v2, figures/rpt001-v2, docs/report_src,
docs/phase_4: none.

Verdict: LANDABLE. Full-suite replay tail to be appended below before merge.
