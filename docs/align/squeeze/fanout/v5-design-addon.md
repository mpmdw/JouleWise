# v5-design-addon — Sol1 handoff

2026-11-08; independent design seat. Base `32ba49285`;
branch `align/2026-11-08-v5design-addon-sol1`. Local commit message:
`docs(align): design conditional v5 add-on squeeze study`.

Built [the ADD-ON proposal](../v5-design/addon-sol1.md): frozen 8-bit D and
original SHADE pairs, API frontier monitor, adaptive/native/external/low-compute
attacks, software-rerun baseline, whole-member DC-in authority, controls,
registration/blinding, estimands, power, FPR and the Mac calendar. Recommendation:
conditional go after capability/budget/meter gates; 120 confirmatory attempts
over 60 nights, 79 core slots including inherited v4 work, 87 with contingency
or 90 with extra engineering and full 10% replacements. Subjective chance of
a main-track-strength scoped squeeze: ~25% (15–40%), conditional on resources.

Only repository files touched:

- `docs/align/squeeze/v5-design/addon-sol1.md`
- `docs/align/squeeze/fanout/v5-design-addon.md` (this report)

Assumed lead rulings: Q4/Q6 registration grade (m≥39/pair plus held-out test);
R10 is a real admission gate, not an already-solved budget; original frozen
configuration is preserved; KM003C covers all delivered power and DC-in decides
small effects; scoped sandboxed on-host adversary permitted; frontier API
monitor primary, no v4 transcript scoring before registration; runtime-external
positive controls required; escape per attempt primary, all-cells descriptive.
No independent authority decision, live gate or in-flight component acceptance
is claimed. Coordination state and R1's lane were untouched.

Verification (synthetic arithmetic/text only, one process at a time):

- `python3.13 -B /private/tmp/v5-addon-sol1-audit/check_design.py` — **7 tests
  PASS**, ~0.001 s. Initially RED because the proposed artifact did not exist;
  subsequently caught a mistyped exact-probability reference in the temporary
  audit, corrected before the final pass. This is an artifact/arithmetic audit,
  not production-code TDD or a statistical-method validation.
- Audit recomputes window envelopes, sample sizes, two-channel rank bounds,
  exact binomial limits/power, conditional-success denominators, paired gain,
  ICC planning discount, total cost and calendar. Script SHA-256:
  `9000b8268a82f894c17edbbc2a8ca85d1f13b0b25b49bea8cee8fc6324403715`.
  The scratch script is not committed; all numeric inputs/formulas are in the
  design, including a machine-readable JSON block.
- Local Markdown validation — **PASS**, two documents, six existing local
  links, balanced code fences. Final staged whitespace/diff check also passed.
- `python3.13 -B scripts/fixture_orphan_census.py --fail-on-orphans` — **exit 2,
  inconclusive**: sandbox denied `ps` (`PermissionError`). No process was
  signaled or changed; this is not a clean census.
- Full suite, pipeline, model execution and network access were not run.
  Docs-only work needed no production unittest module or compileall; the
  standing blinded-job restriction also forbids the full suite.

Material uncertainty: v4 LOO/session scores do not automatically justify an
exchangeable rank-FPR guarantee; the power table is IID orientation with an
explicit cluster sensitivity, not 93% power for the whole claim. The lead must
freeze and size-validate the actual cluster interval procedure before execution.
Controls cannot establish natural adversary capability. API snapshot/prices,
floor validity, T1–T3 probe compatibility and available long nights are unverified.

**NEEDS_RULING — authoritative A0–A13 crosswalk.** Question: which baseline
artifact defines these class identities? Options: attach/map the canonical
taxonomy, or explicitly authorize a new taxonomy. Recommendation: use the
existing taxonomy and map the proposal's C00–C13 semantic coverage to it.
Blocked work: any claim of complete A0–A13 coverage and live registration.
An asynchronous source-location question was sent; no mapping was invented.

Next exact step: lead adjudicates the crosswalk, reuse/fit/FPR semantics, API
snapshot/budget, existing-tool external-compute surface and Mac allocation;
then runs the cheap capability gate before reserving confirmation. Outside this
sandbox the lead must validate native MLX history/cache/hold token identity,
R0/R1 full-last-turn/deadman admission, actual actor capability, real external
compute controls and synchronized meter/rail/battery capture. No native result
is implied by these synthetic checks. No push or external publication.
