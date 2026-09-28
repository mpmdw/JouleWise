```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "clean",
  "completion": "complete",
  "summary": "Independent re-derivation matches all published member values, digests, statistics, quantile-proof fields, and Revision 5 rule outcomes.",
  "workspace": {
    "base_requested": null,
    "base_mode": null,
    "head_start": "f783a3fd348df984e3278e25842dc396059443a4",
    "head_end": "f783a3fd348df984e3278e25842dc396059443a4",
    "upstream_end": "e7c8bcc68d9a1c4f20e11c1904e49552c81ffcd1",
    "branch": null
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "findings": [],
    "rederivation": "MATCH",
    "candidate_sha256": "dbad7cc782945691701c2ee11188179a61b333dbd0a5588b970636716554b5b2",
    "measurement_head": "e7c8bcc68d9a1c4f20e11c1904e49552c81ffcd1",
    "captures": 24,
    "valid_members": 12,
    "dropped_valid_members": 0,
    "mismatches": 0
  },
  "verification": [
    {
      "id": "V1",
      "kind": "other",
      "cmd": "/opt/homebrew/bin/python3 /tmp/sci-rederive-77b1bee2/audit.py",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["INDEPENDENT_AUDIT_PASS"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "^INDEPENDENT_AUDIT_PASS$"
      }
    },
    {
      "id": "V2",
      "kind": "other",
      "cmd": "/opt/homebrew/bin/python3 -B /tmp/sci-rederive-77b1bee2/crosscheck.py",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["CROSSCHECK_PASS"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "^CROSSCHECK_PASS$"
      }
    }
  ],
  "flags": []
}
```

## Findings

**No BLOCKER, SHOULD-FIX, or NIT findings. No published-digit mismatches or departures from the applicable registration rules were found.**

The candidate’s full SHA-256 matches the requested artifact. Repository and custody files remained unchanged; scripts and results are confined to [scratch](/tmp/sci-rederive-77b1bee2/audit.json).

**Membership and stored values.** W1 and W2 below mean `d079-epoch-25g83-derivation-w1-20260927` and `d079-epoch-25g83-derivation-w2-20260927`; append the listed slot to obtain each capture’s complete ID.

`OI-A` means **ordinary-invalid**, with `clock_anchor_unresolved`. `OI-D` means **ordinary-invalid**, with `detection_nonconvergent`. Both also record `not_all_pulses_detected` and `pulse_count_below_protocol:0!=59`; their stored B is null.

| Slot | W1 disposition | W1 stored B, seconds | W2 disposition | W2 stored B, seconds |
|---|---|---:|---|---:|
| d01 | OI-A | null | valid | 0.03203051441482298 |
| d02 | OI-D | null | OI-D | null |
| d03 | OI-D | null | valid | 0.027705716700833778 |
| d04 | valid | 0.03610911339816257 | valid | 0.03245902112381383 |
| d05 | valid | 0.0247300413330314 | valid | 0.028014781845868017 |
| d06 | valid | 0.02626709931386116 | OI-D | null |
| d07 | valid | 0.02930916584265009 | OI-A | null |
| d08 | OI-A | null | OI-D | null |
| d09 | OI-D | null | valid | 0.02952480316956647 |
| d10 | valid | 0.024377093921897318 | valid | 0.03807857930294817 |
| d11 | OI-A | null | OI-D | null |
| d12 | valid | 0.02649306058292668 | OI-D | null |

Each session contributes exactly six valid captures. The candidate includes **all and only these 12**, with no duplicates or dropped valid captures. Every retained member has a resolved anchor and 59 detected pulses.

For every member, both primary-file digests match **actual custody bytes = ledger row = candidate**. Every stored B lexeme matches **evidence = ledger `exact_bound_lexeme_s` = candidate**, including trailing digits. Additionally:

- All 120 ledger-recorded artifact digests across the 24 captures match custody.
- All 276 ledger receipt hashes and predecessor links authenticate through the candidate’s cutoff.
- The candidate’s 86 prior observations match the ledger finalizations.
- All 48 raw battery observations pass the registered predicate; both committed harvest-verdict records match their candidate digests and single-addition histories.

**Independent arithmetic.** I used 90-digit Python Decimal arithmetic and independently inverted the Student-t CDF by integrating its transformed density. No issuer numerical code was used for that derivation. The registered final prediction step deliberately uses binary64.

| Quantity | Independently reproduced value |
|---|---:|
| Minimum | 0.024377093921897318 |
| Maximum | 0.03807857930294817 |
| Range | 0.013701485381050852 |
| Mean, registered presentation | 0.029591582579198539 |
| Sample SD, registered presentation | 0.004330477884879059 |
| Range, ROUND_HALF_EVEN to 1e-6 | 0.013701 |
| S = max(quantized range, 0.010818) | 0.013701 |
| Floor binds | false |
| Level screen, maximum quantized to 1e-15 | 0.038078579302948 |
| t(0.975, 11), published precision | 2.20098516009163986788 |
| t(0.995, 11), published precision | 3.10580651553928100710 |
| 95% two-draw prediction | 0.013479318561660503 |
| Q99, using p = 0.995 | 0.01902064410651988 |
| C = max(0.010164834757777545, Q99, S) | 0.01902064410651988 |
| C − S | 0.00531964410651988 |
| Headroom status | positive_headroom |

The issuer cross-check subsequently reproduced the **entire `quantile_proof` object exactly**, including residual strings `4.000E-81` and `2.000E-81`, and both 57-digit agreement counts. My independently derived quantiles agree with the issuer’s unrounded results to 57 significant digits. Those residual strings describe the issuer’s internal full-precision calculation; they are not residuals of the printed 20-place quantiles.

**Registered diagnostics and vetoes.**

- B > 0.075 s: **0**; no `excursion_limited` label.
- B > 0.25 s: **0**; no plateau-inset refusal.
- B > 0.032898493715362 s: **2**, namely **W1-d04** and **W2-d10**.
- New maximum > 0.04262208300415633 s: **false**.

Revision 5 removes the screen-challenge issuance veto explicitly:

> “The predecessor screen challenge is recorded as a diagnostic, not an issuance veto for this epoch”

Its authority paragraph also says it:

> “drops Revision 1's ‘Screen challenge.’ as an issuance veto for this epoch.”

See the [registration](/Users/edr/code/JouleWise-wt-corpus-fp-77b1bee2/configs/calibration/preregistration_d079_epoch_25g83_rev1.md:632). The [D-125 addendum](/Users/edr/code/JouleWise-wt-corpus-fp-77b1bee2/docs/decision_log.md:12201) independently confirms `C = max(predecessor C, successor Q99, S)` and permits zero headroom. The issuer applies these amendments correctly.

**Physics sanity.** The retained values are plausible relative to the identical r6/r7 source statistics:

| Statistic | r6/r7 | Candidate |
|---|---:|---:|
| Minimum, ms | 23.174904 | 24.377094 |
| Maximum, ms | 32.898494 | 38.078579 |
| Mean, ms | 26.848580 | 29.591583 |
| Sample SD, ms | 2.460856 | 4.330478 |

The new mean is about 10.2% higher and SD about 76.0% higher. This is a broader distribution of comparable magnitude, consistent with the registration’s anticipated cadence sensitivity; it does not establish the cause of the increase.

Raw retained-frame cadence reproduces the candidate’s **128.024375 ms median / 140.908791 ms maximum**. The registered per-session median-of-capture-medians is **128.799979 ms for W1** and **129.302291 ms for W2**, both below 150 ms.

Two instrument effects warrant disclosure without constituting a mismatch: the **50% capture yield**, and all retained captures’ `baseline_w = 0` / `robust_sigma_w = 0.001`. The latter is the estimator’s explicit noise floor, so the very large reported SNRs should not be interpreted as independently measured analog precision. No custody corruption, duplicate content, or implausible retained B outlier was identified.

## Residual risk

This audit independently verifies stored membership, custody, arithmetic, and the requested rule applications. It does not independently rerun the complete pulse estimator, establish historical blindness or launch-context compliance, or provide fresh hardware validation. The comparisons concern the retained valid population.

Reproducible detail is in [audit results](/tmp/sci-rederive-77b1bee2/audit.json) and [proof/custody cross-check results](/tmp/sci-rederive-77b1bee2/crosscheck.json). The lead retains issuance authority.

REDERIVATION: MATCH