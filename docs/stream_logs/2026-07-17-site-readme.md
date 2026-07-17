# Site README + educational guide stream ledger (2026-07-17)

Scope: restructure the Lakebed site's reader journey as a project README,
add a measurement-science guide for a CS undergraduate, keep the generated
site/capsule machinery intact, and verify without deployment.

## Decisions

### SR-001 — Make `docs/site_src/` the authored home for the reframed pages

- Decision: author `index.html`, `research.html`, `results.html`, and their
  shared CSS as generator inputs under `docs/site_src/`. The generator applies
  navigation, page shell, source chips, and footers at build time.
- Why: the old hand pages lived in the generated `docs/site/` tree. The new
  source home separates authored narrative from built output while keeping the
  existing generated-page model.
- Constraint: `docs/site/**` is outside this delegated write scope. Verification
  therefore builds into an isolated temporary repository copy; no generated
  site file is modified in the working tree.

### SR-002 — Use the existing `/research` house route as the new Learn section

- Decision: relabel `research.html` as **Learn** and expand it into the requested
  top-to-bottom interactive guide. Retain the research-question arc in its final
  chapter.
- Why: this preserves the established route and every existing page while
  adding a genuine new site section without changing the capsule route contract
  or creating a redirect-only page. The route remains reachable as
  `/research`/`research.html`; navigation presents its reader-facing purpose.
- Rejected: add `learn.html`. That would require widening the canonical route
  fixture outside the exhaustive write scope. A duplicate page would also spend
  capsule bytes without improving the reader journey.

### SR-003 — Order the site like a README and put measurements last

- Decision: navigation order is Project → Learn → Status → Roadmap → Process →
  Record → Sources → Measurements. The index follows the same arc: definition,
  motivation, mechanism, current state, then measurements.
- Why: a new reader needs to understand the instrument and its claim discipline
  before interpreting results. All former top-level routes remain reachable.

### SR-004 — Enforce the D-069 harness/benchmark terminology split

- Decision: call JouleWise an extensible **measurement harness**. Use
  **benchmark** only for a frozen workload suite, run rules, and strict validator
  layered on the harness.
- Authority: D-069 and the repository README.

### SR-005 — Enforce D-067 beside every energy value

- Decision: gross energy within the named `powermetrics` SoC-rail boundary is
  the comparison headline; idle-subtracted energy is explicitly labeled a
  within-device secondary view; phase energy is gross-only. Toy interactive
  outputs are labeled illustrative and state their basis.
- Authority: D-067 (and D-032 for phase energy).
- Consequence: the Measurements and Learn tables repeat basis labels row by row
  rather than relying on a distant footnote.

### SR-006 — Parse the verified floor artifact fail-closed

- Decision: `build_site.py` reads
  `docs/process_traces/2026-07-17-floor-extraction/extraction-verified.json`,
  requires confirmed DF-RQ/DF-PH/DF-SU verification families, resolves named
  rows, validates positive finite values, and injects formatted values into both
  reader pages.
- Why: one machine-readable source prevents copied-number drift. Comparative
  values retain the extraction schema's documented `floor_abs_j` carrier but
  are labeled as comparative floors on the site.
- Claim posture: strict-valid/collection-usable is kept distinct from
  claim-ready. The universal claim-evidence flags and drift/cooldown caveats are
  displayed with the numbers.

### SR-007 — Keep interactives dependency-free and pedagogical

- Decision: use inline SVG and small inline JavaScript only. The trace lab lets
  readers drag window start/end, sample spacing, and sample phase; it recomputes
  illustrative gross and idle-secondary integrals. The floor lab compares a
  hypothetical effect with each verified gate and states that clearing the
  numeric floor is necessary, not sufficient.
- Why: no network requests, frameworks, or asset pipeline are needed, and the
  controls teach the difference between a trace, samples, an integration window,
  and a claim gate.

### SR-008 — Treat the Lakebed runtime decode budget as a first-class limit

- Decision: append shared authored CSS through the generator, but keep
  guide-only bundle/floor-lab rules inline on the Learn page so every request
  does not pay their decompression cost.
- Evidence: the first integration attempt exceeded the first-request decode
  loop budget; moving guide-only rules out of the shared archive restored the
  conservative budget without dropping content or interactivity.

### SR-009 — Verification and release boundary

- Decision: run site generation, capsule packing, route inspection, focused
  unit suites, and local browser QA only. Do not deploy, commit, or mutate the
  checked-in generated `docs/site/` tree.
- Authority: D-068 plus the runner's explicit “NO deploy” instruction and
  exhaustive write scope.

## Evidence pointers

- Source page model and provenance: `scripts/build_site.py`
- Capsule sharding/budget machinery: `scripts/pack_capsule.py` and
  `site_capsule/README.md`
- Basis and terminology authorities: D-067 and D-069 in
  `docs/decision_log.md`
- Floor values and independent verification:
  `docs/process_traces/2026-07-17-floor-extraction/extraction-verified.json`
- Replay commands and observed byte/route evidence: runner return envelope for
  this delegated session.
