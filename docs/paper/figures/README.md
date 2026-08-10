# Schematic figures

Three publication-grade schematic figures for the MVP paper. They are drawings
of mechanism, not renderings of evidence: every quantity that appears in them
is illustrative, chosen to make the geometry legible, and none of it comes from
a measurement window, a bundle, or an issued artifact. They therefore sit
outside the results-figure contract in `../figures-plan.md` and consume no
registry row. Each file is a self-contained SVG with a white background and
generic `sans-serif` type, sized for a wide page column and legible at 50%
reduction.

## `fig1_boundary_attribution.svg` — the attribution mechanism

Power against time across the handoff from prompt processing to token
generation. Sampler interval-average power is drawn as step rectangles about
112 ms wide; power is high while prompt processing saturates the compute units
and steps down when token generation begins and spends much of each step
waiting on memory. The boundary the runtime records is a vertical line, the
calibrated timing bound is a shaded band around it, and the hatched sliver
between the recorded boundary and the edge of that band is the energy that
changes phase when the boundary moves — bounded by the shift times the power
step, annotated at an illustrative 0.030 s × 33 W ≈ 1 J. The figure also states
that the request total is unchanged, since energy removed from one phase is
added to the other. Every number in it, including the ±30 ms bound, the 33 W
step, and both axis scales, is illustrative and marked as such. It belongs to
§4, beside "Worst-case timing attribution", and is the figure by which a
metrologist will judge whether the phase split is defensible.

## `fig2_window_timeline.svg` — window structure and counterbalanced order

A horizontal session timeline for one measurement window: pre-window
calibration pulse train, admission gate, reference runs, science stages built
from ABBA blocks, a midpoint reference, more science stages, closing reference
runs, and the post-window calibration pulse train, with the calibration bracket
drawn as a span underneath. The reference cadence is deliberately left generic
— the note states that the schedule is pre-registered per campaign — so the
figure is not pinned to any one collection night. An inset expands a single
ABBA block: four runs at slots one to four, labelled A, B, B, A, on a slanted
drift line, with nested brackets showing that the two A runs and the two B runs
share the same average position in time, so a steady drift subtracts out of the
A-versus-B difference while curvature does not and is measured separately. Stage
widths are illustrative and not to scale; no measured value appears. It belongs
to §3 (the bracket and the operative timing bound) and §5 (admission,
counterbalanced order, and the never-zero drift allowance).

## `fig3_decision_gates.svg` — the two claim gates

A compact decision flow from a measured contrast — carried as a point estimate
plus its composed uncertainty interval — through two gates checked separately:
first whether the magnitude exceeds the cell's detection floor, then whether the
whole uncertainty interval points one way. Passing both yields a directional
claim; failing the floor yields *not resolvable*, explicitly not zero, equal, or
no difference; passing the floor without a one-way interval yields *unresolved*;
and a separate side inlet, taken whenever an admission or custody check fails,
yields *refused* without reaching either gate. A side note records that the sum
of the floor and the claim-side interval is disclosed only for sizing and is
never used as a single acceptance threshold. The figure contains no numbers at
all, and its layout implies no threshold. It belongs to §4, beside the
"Publication label and the two claim gates" paragraph.

## Captions in the paper

Captions written for these three figures must stay in plain language and must
not cite internal decision-log identifiers, registry row keys, campaign
codenames, or window labels; each caption must also say that the figure is
schematic and that its values are illustrative.
