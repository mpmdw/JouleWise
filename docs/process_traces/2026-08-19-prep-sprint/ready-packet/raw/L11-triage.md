# RAW TRIAGE EXTRACT — L11-retained-characterization-basis

Source: docs/process_traces/2026-08-15-readiness-council/triage.json (seat entry `L11-retained-characterization-basis`)
Seat report: docs/process_traces/2026-08-15-readiness-council/seat-reports/

- seat verdict as reported: **NOT_READY**
- coverage: 14/16 (evidence_universe_count=16)
- findings: 5; falsifiers: 5

## FINDINGS (verbatim)

### F1 [should_fix] Paper presents the ±31 ms / 33 W / ~1 J triple as 'the measured corpus figure'; it is a single-member maximum plus a derived quotient
- file_line: `docs/paper/draft-v1.md:108 (also :7 abstract, :112 caption, :240)`
- failure_scenario (verbatim): A metrology-literate referee asks which retained artifact records a 33 W power step. None does: composed anchor bounds across the 30 a10 phase members span 25.6–31.1 ms (mean 27.3; ±31 ms is the single widest member, prefill-abs-r01); operative phase envelopes span 0.57–1.57 J; '33 W' is that one member's envelope/bound quotient (1.016 J / 31.07 ms = 32.7 W), while corpus-wide quotients span ~21–58 W and r01's trace-measured prefill-vs-decode mean-power step is 18.6 W (45.6 → 27.0 W). The exhibit's conclusion survives, but 'corpus precision' / 'the measured corpus figure' overstates provenance and invites a credibility hit on the paper's central limitation exhibit.

### F2 [should_fix] Paper attributes the phase mis-attribution evidence to 'the a9 and a10 windows'; a9 contains zero phase-absolute members
- file_line: `docs/paper/draft-v1.md:7, :108, :240`
- failure_scenario (verbatim): A reviewer requests the a9 phase members backing the ±31 ms boundary characterization and finds only 7 request-level reference bundles (anchor bounds up to ±33.5 ms, which would even strain the ±31 ms headline if counted) plus a 12-member refcorpus. The phase-boundary basis is a10-only; a9 is the reference/bracket-context window. The corpus framing as written cannot be backed member-for-member.

### F3 [should_fix] Whole-window PASSED verdicts for a9/a10 exist only as close-out prose; no verdict artifact is retained anywhere findable
- file_line: `~/JouleWise-window-custody/window_a10_20260725/CLOSE_OUT.md; detection-floor-extraction.json (refuses whole_window_neg8_verdict_missing)`
- failure_scenario (verbatim): Anyone auditing the publication basis (this seat, a referee, or a future re-derivation) cannot produce the PASSED verdict ('excursions 0.509 J both families; 37-member basis c3a4f4e1...') from any retained artifact — not in the runs dirs, the bound dirs, the custody dir, the repo, or the iCloud archive mirror; the retained extraction itself refused for the verdict's absence. I re-derived the excursions exactly (0.5094 J both families for a10; 0.310/0.305 J for a9, all under allowances), so the fix is cheap: commit the re-derivation beside the custody close-out so the PASSED context is artifact-backed rather than prose-backed.

### F4 [nit] a9 MANIFEST.sha256 lists ./backup.log, which is neither resident nor covered by PRUNED.md's enumeration
- file_line: `/Users/edr/code/JouleWise/runs_window_a9_20260724/MANIFEST.sha256 (last entry) vs PRUNED.md`
- failure_scenario (verbatim): A strict manifest verification reports 29 missing entries where the prune note authorizes exactly 28 plists; the unexplained backup.log discrepancy costs an auditor time or seeds doubt about the prune's completeness. All 173 resident files re-hash clean.

### F5 [nit] Two D-054 decision-log prose details do not reproduce exactly from the retained bundles
- file_line: `docs/decision_log.md:4674-4684 (D-054 attribution-limited amendment)`
- failure_scenario (verbatim): The 'settled reference pair three hours apart agreed to 0.007 J' matches no unique retained pair (best ~3.7 h candidates agree to 0.0013–0.0019 J gross / 0.0080 J idle-sub), and 'fiducial 24.9 ms (80–87%)' understates the actual fiducial share range (80–97% across the 30 members). Neither figure is paper-cited; risk is only that future prose inherits them as artifact-backed.

## WORK ORDERS (verbatim)

- WO-1 (draft-v1.md:7,:108,:112,:240): restate the characterization as what the artifacts hold — composed clock-anchor bounds up to ±31 ms (25.6–31.1 ms across the 30 a10 phase members), per-member phase mis-attribution envelopes ~0.6–1.6 J (about one joule typical), equivalent to effective boundary power steps of tens of watts (e.g. 1.02 J / 31 ms ≈ 33 W for the widest-bound member) — or keep the triple but pin it explicitly to its defining member and derivation instead of calling it 'the measured corpus figure'.

- WO-2 (draft-v1.md:7,:108,:240): attribute the phase-boundary evidence to a10's 30 phase-absolute members, naming a9 as the reference/bracket-context window of the retained corpus rather than a co-source of the phase characterization.

- WO-3 (custody + repo): make the a9/a10 whole-window PASSED context artifact-backed — commit the excursion re-derivation (a10 0.5094 J both families vs 0.6523/0.6579 J allowances; a9 0.310/0.305 J vs 0.624/0.609 J) beside the custody close-out, or recover the original verdict artifacts from wherever they were emitted; alternatively strip PASSED context from consuming docs.

- WO-4 (optional bookkeeping): annotate a9 MANIFEST/PRUNED for the backup.log entry and correct the two D-054 prose figures (nits N1/N2).

## ED-QUALIFICATION ROWS (verbatim)

## UNEXECUTED OBLIGATIONS (verbatim)

- Full power-trace re-integration for the remaining 29 a10 phase members (1/30 done exactly; the other 29 envelopes were accepted from sha-bound summaries whose digests I verified against the custody extraction).

- Code audit of the reducer-side envelope method implementation (common_trace_shift_plus_independent_edge_corners_v3) in joulewise/reduce.py — I re-derived its output numerically for one member but did not read the implementation.

- Deep audit of joulewise/whole_window.py verdict machinery (surveyed for schema/semantics only; the verdict artifact itself is absent — finding SF3).

- a9 custody operator logs (window-chain/calibration logs) read in detail; a10's were read.

- campaign_log.jsonl deep audit and raw plist parsing for the reference members.

- Byte-parity verification of the iCloud archive mirrors against local dirs (layout and existence checked only; a9 parity rests on the PRUNED.md-documented verification).

