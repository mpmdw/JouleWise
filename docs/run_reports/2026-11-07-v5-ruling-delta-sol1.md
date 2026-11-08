# v5 ruling delta — Sol1 handoff

Session date: 2026-11-07 (environment date); reviewed ruling/source branch
names are dated 2026-11-08. Task: independent documentary delta review of
revision 2, not an implementation or a signed ruling.

## Authority and workspace

- Used the requested clean seat branch already checked out at intake:
  `align/2026-11-08-v5design-ruling-delta-sol1`.
- Initial HEAD / reviewed candidate:
  `7d2e434648303c715f1ad07c183ebccea28d57dd`.
- The user's explicit docs-only task overrides ordinary queue selection;
  coordination-state edits/registration, network, full suites and sealed-data
  access are explicitly prohibited. No such actions were taken.
- Mission M0: read AGENTS/CLAUDE, playbook M0, generated restart/stop-card
  region (NONE active), Current Project Status, Known Workspace State,
  current queue and Do-Not-Do-Yet list, AGENT_PLAN source map and orchestration.
  Read targeted R11 and D-050/D-062 authority and analysis-plan contract.
  Workspace was clean; no unrelated work was present to preserve.
- No new subagent, external consult, network tool or integration was used.
  The requested second independent seat remains the lead's separate review.

## Deliverables and findings

Changed files:

1. `docs/align/squeeze/v5-design/ruling-delta-review-sol1.md` — verdict
   **SIGN_WITH_CHANGES**, separate disposition rows for all 8 numbered S1 and
   10 numbered S2 findings, plus the unnumbered authority/reviewer issues.
   Every disposition cites/quotes the operative revised section.
2. This report.

Three HIGH findings remain: ambiguous/contradictory S/E receipt and feature
permissions; an unknown-success imputation that can favor the joint detector
in the paired effect; and unqualified finite-date t inference. A synthetic
independent-date mean-zero example rejects with probability at least
0.081308 at 28 dates even at the first Holm cutoff .0125. This is a
counterexample, not an estimate of actual v5 operating characteristics.

The requested headline ledger sums reproduce: 693.5 / 866.875 h at 900 s,
898.966667 / 1123.708333 h at 1200 s. The one-date calibration margin is
correct: seven full sessions give 49/pair, a joint date loss leaves 42/pair,
and a valid eighth date restores 49/pair. Post-T3 local quarantine fixes the
principal leakage defect. Remaining MED billing questions concern G10's
software/replay coverage, removal of still-needed G6 qualification in the
all-twin cut, and capacity/reserve definitions. No design policy was changed.

## Verification and evidence

- `git diff 18f35ae06..HEAD` (candidate HEAD at intake), local source reads
  with `git show`, and the two review commit pins: **PASS**, read-only.
  Revision 2 touches only the ruling (295 additions / 167 deletions).
- `python3.13 -B /private/tmp/jw-v5-ruling-delta-sol1/check_arithmetic.py`:
  **PASS** after correcting an initial exact-equality assertion to use
  `Fraction` rather than finite-precision Decimal division. That initial
  harness assertion failed after printing the ledger; no repo source/test
  failure occurred. The final script prints all assertions passing.
- The temporary script is stdlib-only, takes no arguments, reads no data
  files, imports no project modules and uses literal counts/synthetic date
  differences. Numeric output, formulas, null probabilities and limitations
  are quoted in the review. Nominal Student-t tails use a 2048-panel Simpson
  integral, checked against t(1) and symmetry identities; null-subset
  probabilities are analytic, not Monte Carlo estimates.
- Temporary arithmetic script SHA-256:
  `4dfe116688d196d8e99995daf895584e065f80e123374d0647cdc43dbeefae2a`.
- A separate stdlib documentation check: **PASS**, all 18 numbered finding
  identifiers present in review tables, balanced code fences, clean trailing
  whitespace, verdict and quoted ledger values present. This is a document
  completeness check, not a runtime test or scientific qualification.
- `git diff --check`: **PASS** before handoff; final staged checks and the
  documentation-only commit are recorded in the session result.
- No unit/full/sharded suite or compileall was run: only Markdown changed,
  no runtime/test behavior changed, and the blinded-job machine-load rule
  prohibits broad testing. No MLX/native claim is made.
- No measurement pipeline, real measurement loader, process/job inspection,
  filesystem access to sealed/outside-user sources, weights download, quiet
  capture, push or merge occurred. Absolute paths in repo text were not
  followed. Coordination state and existing source documents were preserved.

## Open questions and next exact step

The lead must disposition D1–D5 in the review, revise the ruling and §9,
then obtain the companion independent delta review and agreement on that
exact candidate. Specific choices are the H4 deployable/forensic identity,
declared-versus-observed counter law, paired missingness bounds, finite-date
test/weights/zero-variance/size gate, G10/G6 allocation and dated CAP schedule.
This seat recommends a repaired charter, not immediate registration.

Actual test-date count, receipt availability, workloads/capacity, source
performance, novelty and venue dates remain unverified. The lead's eventual
MLX tiny-synthetic unittest modules must cover actual/declared replay,
history/cache/RNG identity, receipt partitioning, concurrent helpers,
teardown and tails; identify their integrated paths then. Live capacity,
DC-in/clock/battery closure, storage and capability gates require the later
lead-controlled clean lane outside this sandbox. No current gate is marked
passed on fixture or documentary evidence.

Local-only commit; no push is authorized or pending from this seat. The final
response supplies its SHA; this report is included in that same commit.
