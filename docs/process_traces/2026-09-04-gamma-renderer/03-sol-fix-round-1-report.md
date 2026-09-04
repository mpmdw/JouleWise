# Gamma renderer — Sol fix round 1 report (2026-09-04)

## Status and authority

Complete under the magistrate's R2 amendment in
`docs/process_traces/2026-09-04-paper-i/07-magistrate-rulings-addendum.md`.
The resumed HEAD was the required `8381bb377481948c081a4c36377880de31720a45`;
HEAD did not move and no commit was created.

The amendment wins over contract-refuter S2 and the original Q-R2-2 wording:
`joulewise.claim_verdicts.v1` remains production, and the claim-side bound is
the separately content-addressed `joulewise.claim_side_bound.v1` sidecar bound
to the exact v1 bytes by `claim_verdicts_sha256`. The v2 producer/validator
edits were reverted; `joulewise/analysis_engine/__init__.py` and
`joulewise/analysis_engine/artifact.py` are byte-identical to `origin/main`.

The addendum also wins where the refuters requested verdict-absence prose:
absence is non-issuance. DS-32/PG-08 now stay `STOP_FILL` until the future
`CLAIM-NONISSUANCE-RECEIPT-01`; no caller-authored earlier-stop wire was
invented.

## Finding → cure → regression

### Execution B1 — authenticated floor bytes did not govern rendered F

Cure: the renderer reopens the embedded floor artifact, authenticates its
digest/schema/ID, resolves both distinct exact source cell IDs, and requires
each resolution's `floor_abs_j`, `floor_cmp_j`, and `floor_gate_j` to equal the
source cell before rendering any claim result.

- Code: `joulewise/results_fill_gamma.py:396-472`
- Regression: `tests/test_results_fill_gamma.py:622-641`

```text
RED (refuter): validator [] + self-consistent internal floor rewrite rendered F=1.7
GREEN: the same re-content-addressed internal rewrite still validates as v1,
       but DS-28, DS-32, PG-04, and PG-08 are all STOP_FILL
```

### Execution B2 / Contract B3 — absence inferred refusal authority

Cure: contrast absence emits no prose. The registry records the addendum's
future-receipt gate for both exact absent-verdict sentences.

- Code: `joulewise/results_fill_gamma.py:484-488`
- Registry: `docs/paper/results-fill-registry.md:903,912`
- Regression: `tests/test_results_fill_gamma.py:545-551`

```text
RED (refuters): removing a contrast rendered "not evaluated — required ... verdict absent"
GREEN: authenticated removal of either contrast leaves DS-32 or PG-08 exactly STOP_FILL
```

### Execution B3 / Contract B4 — valid partial outcomes were unreachable

Cure: authenticated outcome/reason rendering occurs before numeric parents;
estimate, interval, floor, bound, and gate cells then render independently.
No missing named bound receives a number.

- Code: `joulewise/results_fill_gamma.py:501-643`
- Regression: `tests/test_results_fill_gamma.py:552-564`

```text
RED (refuters): valid not_estimable bytes returned all STOP_FILL
GREEN: both issued not-estimable verdicts and four "not evaluated — <issued reasons>"
       gate strings render; both B cells remain STOP_FILL
```

### Execution B4 / Contract B1 — v2 broke the v1 producer and refusals

Cure: the v2 edits were reverted. The new sidecar producer projects the exact
named term when present and issues an empty, digest-bound sidecar for a valid
refusal artifact rather than crashing or defaulting a number.

- Producer/validator restored: `joulewise/analysis_engine/__init__.py`,
  `joulewise/analysis_engine/artifact.py`
- Sidecar: `joulewise/claim_side_bound.py:146-268`
- Regressions: `tests/test_analysis_engine_artifact.py:13-39`,
  `tests/test_analysis_integration.py:1564-1590`,
  `tests/test_claim_side_bound.py:38-135`

```text
RED (refuter): ClaimArtifactError on governed refusals; producer v2 changed the pinned ID/SHA
GREEN: v1 ID/SHA producer integration passes; clean sidecar value is the issued 0.2 term;
       refusal sidecar bounds == []; no producer exception
```

### Contract B2 — refused G2-a became a 4096 selection

Cure: the refused record is validated for consistency and then terminates
before exposing its collection fallback as a selected length.

- Code: `joulewise/results_fill_gamma.py:227-238`
- Regression: `tests/test_results_fill_gamma.py:604-620`

```text
RED (refuter): refused G2-a / collection fallback 4096 rendered supported PG-08
GREEN: re-digested refused G2-a bytes return global STOP_FILL
```

### Execution S1 — mutation test omitted boundaries and hid semantic gaps

Cure: held-pin attacks now cover sidecar plus 47 digest, 41 census, 53
outcome, and 40 boundary occurrences. Separate re-content-addressed attacks
exercise floor lineage, sidecar value identity, G2-a status/census coupling,
and refusal non-authority.

- Regressions: `tests/test_results_fill_gamma.py:604-702`

```text
RED (refuter): 46 digest / 41 census / 53 outcome / 0 boundary; every attack died at authentication
GREEN: 47 digest / 41 census / 53 outcome / 40 boundary held-pin attacks stop,
       and the re-authenticated floor, bound, G2-a, and absence counterfactuals also stop
```

### Contract S1 — registry contradicted its issued prefill family

Cure: the registry now says the symmetric family exists while values remain
G2-a-unresolved/unissued; refused G2-a is explicitly terminal. The obsolete
gap and double-check prose were reconciled.

- Registry: `docs/paper/results-fill-registry.md:361-399,948-950,998-1007`

```text
RED (refuter): introduction said the prefill family did not exist while its rows registered it
GREEN: both registry test modules pass with one unambiguous issued-family/value-unissued state
```

### Contract S2 — registered production contracts remained v1

RULING WINS: the addendum says they must remain v1 and expressly withholds the
frozen renderer and ladder/flow contracts from this seat. The scoped gamma
renderer now consumes v1 plus the digest-bound sidecar; no v2 consumer path or
out-of-scope contract edit remains.

- Guide/registry: `docs/paper/artifact-guide.md:141`,
  `docs/paper/results-fill-registry.md:377,386,391,900,909`
- Renderer join: `joulewise/results_fill_gamma.py:657-753`

## Verification

```text
python3 -m unittest tests.test_results_fill_gamma
Ran 1 test in 1.334s
OK

python3 -m unittest tests.test_analysis_engine_artifact tests.test_claim_side_bound
Ran 5 tests in 0.081s
OK

python3 -m unittest tests.test_analysis_integration.AnalysisIntegrationTests.test_v3_abba_engine_and_d093_refusal_precedence tests.test_analysis_integration.AnalysisIntegrationTests.test_complete_strict_current_bundle_set_derives_deterministic_fail_closed_artifact
Ran 2 tests in 1.243s
OK

R7F_CORPUS_ROOT=/Users/edr/code/JouleWise python3 -m unittest tests.test_paper_first_use_ledger tests.test_paper_terms_lint
Ran 13 tests in 2.717s
OK

git diff --exit-code origin/main -- joulewise/analysis_engine/__init__.py joulewise/analysis_engine/artifact.py
(no output; exit 0)

git diff --check
(no output; exit 0)
```

The preflight forbade the canonical suite, so it was not run. All evidence is
fixture/counterfactual-only; no live data or hardware claim was exercised.
