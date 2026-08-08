# Q3 successor numerical-kernel evidence

Status: **PARTIAL — the required mpmath oracle could not be installed in this
sandbox.** The independent fallback below is useful numerical evidence, but it
is not represented as the synthesis-mandated mpmath cross-check. The re-convened
gate must not treat this document as closing that named requirement.

## Required-oracle environment result

The requested isolated environment was created at
`/tmp/joulewise-u2-q3-venv`. The exact install command was:

```text
python3 -m venv /tmp/joulewise-u2-q3-venv && /tmp/joulewise-u2-q3-venv/bin/python -m pip install 'mpmath>=1.3,<2'
```

It exited 1 after five connection attempts: sandbox DNS/network access was
unavailable, and neither the system interpreter nor local package caches held
mpmath. A browser-mediated download was also unavailable. No repository
dependency was added. Consequently there is no honest mpmath maximum-deviation
claim or mpmath evidence table in this run.

## Kernel stopping rules and error envelope

The production kernel uses an 80-decimal-digit local context.

- Modified Lentz iteration guards denominators at `1e-72`. It returns only
  when both the final multiplicative change differs from one by at most
  `1e-68` and the complete continued-fraction value changes by at most
  `1e-68 * max(1, abs(value))` over the iteration. Failure to meet both tests
  within 10,000 iterations raises the governed reason
  `successor_quantile_continued_fraction_nonconvergence`; no bare
  `ArithmeticError` remains.
- Quantile bisection preserves a monotone sign-changing bracket and stops only
  when its width is at most `1e-72`. Conditional on exact survival-function
  evaluation, returning the midpoint therefore has absolute quantile error at
  most `5e-73`.
- The Lentz successive-iterate threshold is an operational convergence bound,
  not by itself a theorem bounding the infinite continued-fraction tail.
  End-to-end error therefore needs an independent oracle. The fallback below
  supplies empirical evidence; the required mpmath run remains open.

## Independent fallback cross-check (not mpmath)

A separate 120-digit Decimal program inverted the Student-t survival function
with the hypergeometric power series
`I_x(a,b) = x^a / (a B(a,b)) * 2F1(a, 1-b; a+1; x)` and Newton updates using
the analytic Student-t density. It did not call the production incomplete-beta
continued fraction. The grid was every `df=1..79` (all corpus sizes 2..80) at
`p in {0.975, 0.995}`. The compatibility pin was bypassed for every production
call, including df=18.

Maximum absolute production-vs-fallback quantile deviation was
`2.46909407839843915716446447142908700400257330351623e-69` at
`(df=59, p=0.975)`. Maximum fallback probability residual after inversion was
`1.6e-120`; the longest hypergeometric evaluation used 5,414 terms.

| df | abs deviation, p=.975 | abs deviation, p=.995 |
|---:|---:|---:|
| 1 | 1.492E-73 | 4.688E-74 |
| 2 | 9.587E-74 | 1.115E-73 |
| 3 | 4.365E-72 | 1.133E-73 |
| 4 | 7.989E-72 | 5.665E-72 |
| 5 | 2.291E-71 | 8.513E-72 |
| 6 | 6.671E-72 | 1.456E-72 |
| 7 | 1.424E-71 | 4.973E-72 |
| 8 | 1.993E-70 | 4.860E-72 |
| 9 | 5.563E-71 | 9.292E-71 |
| 10 | 1.386E-70 | 1.883E-71 |
| 11 | 1.956E-70 | 7.882E-71 |
| 12 | 1.814E-70 | 1.890E-70 |
| 13 | 1.228E-70 | 1.421E-71 |
| 14 | 5.829E-70 | 1.815E-71 |
| 15 | 2.380E-70 | 3.004E-70 |
| 16 | 6.475E-70 | 2.172E-70 |
| 17 | 1.933E-70 | 1.332E-70 |
| 18 | 3.602E-70 | 7.174E-71 |
| 19 | 5.649E-70 | 4.108E-70 |
| 20 | 7.646E-70 | 1.698E-70 |
| 21 | 9.132E-70 | 6.554E-71 |
| 22 | 9.804E-70 | 2.340E-70 |
| 23 | 9.591E-70 | 7.728E-71 |
| 24 | 8.656E-70 | 2.170E-70 |
| 25 | 7.281E-70 | 5.387E-70 |
| 26 | 5.753E-70 | 1.484E-70 |
| 27 | 4.312E-70 | 3.132E-70 |
| 28 | 3.077E-70 | 6.025E-70 |
| 29 | 9.310E-70 | 1.488E-70 |
| 30 | 5.974E-70 | 2.548E-70 |
| 31 | 3.713E-70 | 4.070E-70 |
| 32 | 9.213E-70 | 6.124E-70 |
| 33 | 5.303E-70 | 1.376E-70 |
| 34 | 1.175E-69 | 1.912E-70 |
| 35 | 6.352E-70 | 2.536E-70 |
| 36 | 1.279E-69 | 3.222E-70 |
| 37 | 6.574E-70 | 3.923E-70 |
| 38 | 1.219E-69 | 4.605E-70 |
| 39 | 6.017E-70 | 5.223E-70 |
| 40 | 1.039E-69 | 5.740E-70 |
| 41 | 1.721E-69 | 6.128E-70 |
| 42 | 8.042E-70 | 6.361E-70 |
| 43 | 1.259E-69 | 6.442E-70 |
| 44 | 1.907E-69 | 6.375E-70 |
| 45 | 8.542E-70 | 6.167E-70 |
| 46 | 1.235E-69 | 5.850E-70 |
| 47 | 1.736E-69 | 5.441E-70 |
| 48 | 7.538E-70 | 4.975E-70 |
| 49 | 1.020E-69 | 4.471E-70 |
| 50 | 1.347E-69 | 3.956E-70 |
| 51 | 1.741E-69 | 3.452E-70 |
| 52 | 2.203E-69 | 2.970E-70 |
| 53 | 9.165E-70 | 1.072E-69 |
| 54 | 1.128E-69 | 8.871E-70 |
| 55 | 1.363E-69 | 7.266E-70 |
| 56 | 1.618E-69 | 5.887E-70 |
| 57 | 1.892E-69 | 4.728E-70 |
| 58 | 2.177E-69 | 3.761E-70 |
| 59 | 2.469E-69 | 1.166E-69 |
| 60 | 9.895E-70 | 9.017E-70 |
| 61 | 1.102E-69 | 6.919E-70 |
| 62 | 1.211E-69 | 5.277E-70 |
| 63 | 1.315E-69 | 3.997E-70 |
| 64 | 1.411E-69 | 1.119E-69 |
| 65 | 1.497E-69 | 8.290E-70 |
| 66 | 1.572E-69 | 6.107E-70 |
| 67 | 1.634E-69 | 4.478E-70 |
| 68 | 1.682E-69 | 1.169E-69 |
| 69 | 1.716E-69 | 8.413E-70 |
| 70 | 1.734E-69 | 6.032E-70 |
| 71 | 1.738E-69 | 1.499E-69 |
| 72 | 1.728E-69 | 1.057E-69 |
| 73 | 1.705E-69 | 7.433E-70 |
| 74 | 1.669E-69 | 5.211E-70 |
| 75 | 1.623E-69 | 1.227E-69 |
| 76 | 1.567E-69 | 8.484E-70 |
| 77 | 1.503E-69 | 5.851E-70 |
| 78 | 1.433E-69 | 1.324E-69 |
| 79 | 1.357E-69 | 9.031E-70 |

## df=18 compatibility-pin discrepancy — gate ruling required

The independent fallback agrees with the bypassed production algorithm at
df=18 within the deviations shown above. The retained D-102 compatibility pins
do not agree with that computed path:

| p | retained compatibility pin | pin-bypassed production quantile | absolute deviation |
|---:|---:|---:|---:|
| .975 | 2.1009220402410352934446802481715190309096147708883899652987837826492167345329145 | 2.1009220402410384880608716437301174775404399358595521912184303140862268503844858 | 3.194616191395558598446630825E-15 |
| .995 | 2.8784404727135853941939366597008136821841052811738896572381901955286218320347263 | 2.8784404727386081178058787265646316079030323608869115266837277466388683323490518 | 2.502272361194206686381792572E-11 |

The exhibit retains the governed compatibility pins. Changing them would alter
authenticated derivation bytes and exceeds this remand's authority. The
reassembled packet must present whether df=18 keeps the ratified literals or
adopts independently verified algorithm values; the missing mpmath run should
be completed before that ruling.

## Checked-in non-pinned regression reference

The non-pinned df=37, p=.995 fallback reference is
`2.71540872154998830130830201963737496013944012008966094097330087289823817193540197518371053830804074116858911770212594477`.
The repository regression compares the production result to this value within
`1e-60`. This is independent-series evidence, not the still-owed mpmath-derived
reference required by the synthesis.

## MPMATH ORACLE RUN (lead bench, 2026-08-08 — closes the environment-blocked mandate)

The Sol rework sandbox had no network, so the mandated mpmath oracle ran
at the LEAD'S bench instead (mpmath 1.4.1, dps=120, venv outside the
repo; script + raw grid custodied: `Q3-MPMATH-ORACLE-GRID.json` beside
this file; scratchpad `mpmath_oracle.py`). Oracle: Student-t CDF via
regularized incomplete beta, root-inverted at tol 1e-110.

**Results (pin-bypassed kernel vs oracle, df=1..80, p in {0.975, 0.995},
160 points):**

- **Max absolute deviation: 3.106e-69.** The kernel is numerically
  exact at every grid point to ~69 digits — this independently confirms
  the 120-digit hypergeometric fallback grid above.

**Pin-vs-truth (the F2 discrepancy, now exact):**

| quantity | value |
|---|---|
| pin(18, 0.975) − truth | 3.194616191395558598446630825e-15 |
| pin(18, 0.995) − truth | 2.502272361194206686381792572e-11 |
| D-102 ratified bench 2.878440472713585 − truth | 2.502311780587872656463160790e-11 |

**Interpretation for the gate:** the retained compatibility pins are
faithful ~79-digit extensions of the RATIFIED BENCH VALUES; the bench's
July numerical-CDF inversion itself was in error at the 11th decimal
for the 0.995 quantile (and the 15th for 0.975). The kernel is right;
the pins reproduce the ratified-but-imperfect parent derivation. The
issued artifact's derivation therefore embeds a t-quantile ~2.5e-11 too
small — relative error ~8.7e-12, shifting the derived budget cap at the
~1e-14 s scale against a 1.08e-2 s screen: physically nil, but it makes
the compatibility-pin split (pins reproduce the PARENT exactly; the
oracle-verified kernel derives all SUCCESSORS) the only coherent
resolution, and the reassembled packet must present exactly that as
Q3's decision with this table as evidence.
