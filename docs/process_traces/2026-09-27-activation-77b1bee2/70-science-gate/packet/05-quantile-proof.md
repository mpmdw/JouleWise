# 05 — Quantile proof

Primary source: `docs/process_traces/2026-09-27-activation-77b1bee2/60-prepare-record/30-run1/candidate_acceptance_25g83.json` (sha256 `dbad7cc782945691701c2ee11188179a61b333dbd0a5588b970636716554b5b2`), JSON path `decimal_derivation.quantile_proof`. The block below is copied field-for-field; bounds are the issuer-declared values carried by the candidate.

```json
{
  "degrees_of_freedom": 11,
  "probabilities": [
    "0.975",
    "0.995"
  ],
  "quantiles": {
    "0.975": "2.20098516009163986788",
    "0.995": "3.10580651553928100710"
  },
  "forward_residuals": {
    "0.975": "4.000E-81",
    "0.995": "2.000E-81"
  },
  "forward_residual_bound": "1E-30",
  "closed_form_agreement_digits": {
    "0.975": 57,
    "0.995": 57
  },
  "closed_form_agreement_bound": 30,
  "closed_form_method": "Abramowitz & Stegun 26.7.3 (odd df) / 26.7.4 (even df) finite closed form, inverted by bisection; pi by Machin's formula",
  "precision": 80,
  "bounds_origin": "issuer-declared bounds, stated in the pre-registration's quantile-proof clause and recorded here in the candidate: a forward residual of at most 1e-30 and agreement of at least 30 significant digits between the two routes, each chosen tighter than the 20 published digits the artifact records and looser than the agreement the implementation realizes"
}
```
