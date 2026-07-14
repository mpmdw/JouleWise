# Per-cell lens briefs (driver extracts its cell's section verbatim into {{LENS}})

## KEEP-PRIOR (append to D1, D4, D7 lenses only)

Keep-prior: this domain carries the highest mistaken-simplification cost in
the repository. Before proposing delete/simplify for anything that looks
like a safeguard, redundancy, or ceremony, actively search for the invariant
it protects (git log the file, grep decision/council references, check tests
that would catch its absence) and record what you found in
`counterevidence` — an empty counterevidence field on a delete proposal in
this domain means you did not look. Deletion proposals here will face
keep-defender refuters; pre-empt them or don't propose.

## D1 — Run lifecycle and evidence kernel (effort high)

Mission lenses in order. M2 (excess inventory): dead config keys, unused
schema fields, CLI flags with no consumers, duplicated validation logic,
stdlib reimplementations, copy-pasted bundle/provenance handling. M1 (value
challenge): single-implementation abstractions in config/controller/clock/
bundle plumbing, speculative generality (hooks nothing uses), indirection
without payoff, machinery-to-risk ratio of the validation stack. Consider
the roadmap ONLY as tie-breaker for keep. [KEEP-PRIOR applies.]

## D2 — Platform boundaries (effort high)

M2: unused adapter surface, duplicated transport/telemetry handling, node
client/worker code with no live caller, obsolete compatibility shims. M1:
adapter abstraction payoff vs the 2-3 real runtimes, speculative multi-node
generality that W3 will separately assess as architecture (flag overlap in
`seams`), config surface nobody sets.

## D3 — Campaign and workload orchestration (effort high)

M2: generator/suite/manifest duplication, campaign-runner paths never
exercised by any queue item or test, stale manifests, dead workload knobs.
M1: is the suite/generator machinery proportionate to the campaigns the
queue actually plans? Premature parameterization; manifest indirection
without payoff.

## D4 — Reduction, analysis, uncertainty, claim gates (effort high)

M2: duplicated statistical helpers, dead reducer versions beyond the frozen
legacy arms (frozen arms are KEEP by decision — flag only if unfrozen code
duplicates them), unused verdict paths. M1: lattice/versioning machinery vs
actual analysis needs; over-parameterized gates; indirection in the
claim-gating chain. Numerical CORRECTNESS is SCI's job — hand suspicions to
`seams: ["SCI"]` rather than deep-diving yourself. [KEEP-PRIOR applies.]

## D5 — Reporting, figures, packaging, privacy, site publication (effort high)

M2: dead figure/report paths, duplicated packing logic between site build
and capsule pack, unused privacy-pack rules, site_capsule server/client code
with no live route. M1: is the site/publication machinery proportionate to a
capstone demo? Base85/gzip shard machinery value vs Lakebed constraints
(constraints are real — check LAKEBED_FEEDBACK.md before calling them
overengineering); packaging generality beyond the one real deployment.

## D6 — Test portfolio (effort high)

M2: duplicated test coverage (same invariant tested N times), vacuous tests
(pass if the guarded behavior is deleted — spot-check by reading the
asserted path, name your method), fixture inflation, obsolete compatibility
tests for retired schemas/paths, mock-asserting-mock patterns. M1: test
architecture value — where does the suite test implementation detail instead
of contract (brittle to refactors the roadmap will force)? Do NOT report
missing coverage here (that is W5/architecture); report EXCESS and VACUITY.

## D7 — Governance and process stack (effort high)

Scope: tracked process docs, state kernel + gen_state, bridge contract +
scripts/bridge + adapters/skills/commands dotfiles, orchestration docs.
M2: duplicated normative prose (one-home violations), stale pointers,
process docs no session reads (check git log for consumption evidence),
generated-vs-source drift. M1: for EACH process mechanism, name its value to
the undergrad-capstone deliverable vs its cost (session time,
doc-maintenance burden, token spend) — process cost is admissible evidence;
"an audit/court would want it" is not sufficient value on its own.
Every row: `author_conflict: true` (the audit's authors built this stack —
downstream handles it; you scan honestly, favoring neither prosecution nor
defense). [KEEP-PRIOR applies.]

## W1 — One-run lifecycle walk (effort xhigh)

Walk config → controller/adapters → raw bundle → strict validation →
reduction END TO END, including EVERY failure and cleanup path. Hunt
architecture oversights only (M3): seam contract mismatches, error paths
that lose evidence or leave partial state, cleanup that can destroy
evidence on crash, fail-open defaults, inconsistent failure vocabulary
across stages, places where a stage trusts an upstream invariant nothing
enforces. Excess/duplication belongs to the D cells — hand off via `seams`.

## W2 — Campaign-to-claim walk (effort xhigh)

Walk campaign design/order → corpus → floors/uncertainty → aggregation →
claims → figures/report. Hunt: aggregation seams that silently change
units/denominators, claim gates bypassable by artifact shape, floor logic
consuming inputs no stage validates, report/figure generation trusting
unvalidated intermediate state, missing downgrade paths when inputs are
partial. Statistical CORRECTNESS is SCI2's job — flag suspicions to seams.

## W3 — Local-to-remote and future-split walk (effort xhigh)

Walk local/SSH/node-worker paths and the schema-evolution story toward
offline replay/multi-node/NVIDIA-Orin. Hunt: concurrency/locking assumptions
that break with a second writer, schema versioning without migration or
rejection paths, cleanup races, PROVISIONAL boundaries not enforced in code,
transport error semantics that differ silently between local and remote,
and SPECIFICALLY: what breaks FIRST when the roadmap's split lands — name
the weakest seam explicitly even if it is not yet a defect.

## W4 — Clean-clone-to-publication walk (effort xhigh)

Walk install/preflight → reproducible run → artifact regeneration →
package/privacy/site AS DOCUMENTED (README, docs). You are read-only: derive
the documented path and enumerate every step a fresh user must take; verify
each step's preconditions exist in the tree (the EXECUTED clean-clone
reproduction runs separately — your job is the architectural walk: gaps,
undocumented prerequisites, steps that depend on untracked state,
CI-vs-docs drift, pyproject/env lockfile consistency).

## W5 — Authority-to-enforcement-to-test walk (effort xhigh)

Walk decisions/contracts → code gates → tests/live gates → queue/status →
public claims. Hunt: normative rules with no enforcing code or test
(conventions that only prompts uphold — name each), enforcement stricter or
looser than its authority text, test oracles that restate implementation
instead of authority, status/public claims not derivable from recorded
evidence, and authority conflicts between documents (which one wins is
undefined).

## SCI1 — Measurement/reduction validity (effort xhigh)

Examine, with the skepticism of an external metrology reviewer: units and
time bases (monotonic vs wall, ms/s mixing), energy integration method and
its error, idle-subtraction model validity, denominators (tokens: which
tokenizer, whose count, prompt-vs-decode attribution), boundary alignment
(marker-to-sample alignment error), missingness/exclusion handling (what
gets dropped and does the record say so). MUST sample at least one retained
real bundle under runs/ (untracked; read-only) and trace real recorded
numbers through the reduction path — a wrong estimand baked into evidence is
invisible to code-only review. Report which bundle and which numbers.

## SCI2 — Statistical/claim validity (effort xhigh)

Examine: estimands (does each claim gate estimate what its authority text
says), dependence assumptions (HAC/ESS usage vs actual sampling structure),
ratio statistics (bias, zero-denominator handling), multiplicity across
cells/campaigns, floor logic (detection-floor identity and its
assumptions), uncertainty propagation end-to-end, sensitivity of verdicts
to arbitrary constants (name each magic number that flips a verdict), claim
downgrade paths, and whether tests provide an INDEPENDENT oracle for any of
this or merely restate the implementation.
