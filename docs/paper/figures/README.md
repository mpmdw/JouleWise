# Paper figures

The article uses the SVG sources directly. Printed labels, rather than legacy
filename numbers, determine the contiguous article sequence. The prospective
protocol has its own Figure P1. Existing `png/` files are historical exports,
not suppliers for this draft.

| Printed label | SVG | Evidence and placement |
|---|---|---|
| Figure 1 | `fig1_boundary_attribution.svg` | Synthetic boundary allocation, article §2; SYN-08. One 30-W record is split at 1.040 or 1.050 s. The full-height 0.010-s slice transfers 0.30 J; both allocations total 3.00 J. |
| Figure 2 | `fig4_edge_excursions.svg` | Historical current-method pulse re-derivation, article §4; DX-001/003/010–013. Marks are fitted lags from the retained capture, not schematic power values. |
| Figure 3 | `fig5_phase_record_overlap.svg` | Schematic record support, article §4. Two and three overlaps illustrate the cutoff, not population frequencies; widths and positions are not to scale. |
| Figure A1 | `figA_partial_record_enclosure.svg` | Synthetic partial-record enclosure, first cited in §1 and displayed in Appendix A.6; PE-01. Point assignment, timing envelope and fixed-window physical allocation enclosure remain distinct. |
| Figure A2 | `fig2_window_timeline.svg` | Measurement-window schematic, first cited in §2 and displayed in Appendix A.7. A/B/B/A cancels linear drift only with equal condition-midpoint sums. References sample selected times and do not bound arbitrary between-reference excursions. |
| Figure A3 | `figA3_block_corners.svg` | Synthetic endpoint enumeration, article §3; SYN-05. Four corners, each complete bound, the maximum, and the enumeration limit are labelled. |
| Figure A4 | `figA5_shared_signs.svg` | Synthetic shared/local sign calculation, article §3; SYN-01. Block allowances feed the eight cases in Table 4; one shared energy sign is not one physical time shift. |
| Figure A5 | `figA4_clock_polygon.svg` | Synthetic clock-constraint intersection, Appendix A.3.9; SYN-07. Constraints, vertices, axis projections and an empty-set refusal are labelled. |
| Figure A6 | `figA6_pulse_fit.svg` | Historical current-anchor pulse 9, Appendix A.3.9; DG-134. Gray records, blue predicted averages, dashed commands and an outward-rounded enclosing rectangle use the registered sidecar. |
| Figure P1 | `fig3_decision_gates.svg` | Prospective protocol P.3 only. Invalid evidence is refused before the magnitude and direction gates. Direction requires both intervals and Holm to pass; usable below-floor evidence is not resolvable and does not establish equality. |

Every article figure has a caption identifying its elements and whether it is
historical, synthetic or schematic. The registry binds empirical marks and
worked arithmetic; the schematic layouts encode no measured value.
The retained P1 label in Figure A1 identifies the partial-record example;
article Appendix A.6 explains it before the artwork.

`reproduce_worked_examples.py` produces `worked-examples.json` and
`pulse-table.md` from the pinned synthetic fixture and retained historical
sources. Repository-only synthetic replay works at the article’s development
pin `2d96783857741f03ad9d634328efaf8bc6d676bc`:

```bash
python3 -B -c 'import json, runpy; m = runpy.run_path("docs/paper/figures/reproduce_worked_examples.py"); print(json.dumps(m["synthetic"](), indent=2, sort_keys=True))'
```

Any later explicitly issued replay pin supersedes that development pin.
Compare this output with the `synthetic` member of the registered sidecar.
With the unreleased historical corpus, reproduce the full sidecar in a
separate output directory and compare it with the registered parents:

```bash
python3 -B docs/paper/figures/reproduce_worked_examples.py --corpus-root /path/to/corpus --output-dir /tmp/paper-m-worked-replay
```

The native-label fields use raw whole-second metadata, not interpolated parser
timestamps. The sidecar retains all native constraints, clock and command
stamps, local pulse predictions/losses, overlap examples with zero-overlap
neighbors, and all synthetic sign cases with member-envelope integrals.

To regenerate the mechanisms from the retained sidecar, use:

```bash
python3 -B docs/paper/figures/build_mechanism_figures.py
```

The builder writes eight SVGs: Figures 1, 3, A2–A6 and P1. Figure 2’s producer
is `scripts/paper_excursion_decomposition.py`; Figure A1’s producer and exact
invocation are in article Appendix A.6. Both retain their registered bytes.
