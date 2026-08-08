# Q3 successor numerical-kernel evidence

Status: **COMPLETE — the ratified parent-pin/successor-kernel method split is backed by a reproducible 120-dps mpmath oracle grid.**

## Governing method split

The issued D-102 parent remains byte-compatible with its retained df=18
quantile pins. Successor derivations bypass those pins and use the production
Decimal incomplete-beta kernel. This preserves the authenticated parent while
preventing its historical numerical-CDF error from propagating into successor
arithmetic.

## Reproduction

The committed generator is `q3_generate_oracle_grid.py` beside this document.
It was run with mpmath 1.4.1 at 120 decimal digits:

```text
<mpmath-venv>/bin/python docs/process_traces/2026-08-07-u2-coldgate/q3_generate_oracle_grid.py
```

The oracle evaluates the Student-t CDF through mpmath's regularized incomplete
beta and root-inverts it with a monotone bracket whose final width is at most
`1e-110`. The production call uses
`decimal_student_t_quantile(..., use_compatibility_pin=False)`.

`Q3-MPMATH-ORACLE-GRID.json` contains all 160 combinations of `df=1..80` and
`p in {0.975, 0.995}`. Serialization is full precision rather than the former
`mpmath.nstr(..., 40)` truncation: production-kernel strings carry 79-80
significant digits, and every oracle and absolute-deviation string carries 120
significant digits. The maximum serialized precision is therefore 120 digits.
Absolute deviations retain their scientific-notation exponents.

## Kernel result

The maximum absolute kernel-versus-oracle deviation in the committed grid is
`3.10638246932799211069600959065213388441787905218272926740874913105498101116557403636213483644459624373160098778527978589e-69`
at `df=80`, `p=0.975`. The kernel agrees with the independent oracle to about
69 decimal digits over the complete grid.

The production kernel uses an 80-decimal-digit local context. Its modified
Lentz iteration guards denominators at `1e-72` and returns only when both the
final multiplicative change and the complete continued-fraction iterate meet
the `1e-68` convergence tests. Its quantile bisection stops at bracket width
`1e-72`; nonconvergence within 10,000 continued-fraction iterations raises
`successor_quantile_continued_fraction_nonconvergence`.

## df=18 compatibility-pin discrepancy

The sign convention below is **truth minus retained pin**. Both differences are
positive, so both retained pins sit below the independently computed truth.

| p | oracle truth | retained compatibility pin | truth − pin |
|---:|---:|---:|---:|
| 0.975 | 2.10092204024103848806087164373011747754043993585955219121843031408622721057283397917968704798460692226688100613217330597 | 2.1009220402410352934446802481715190309096147708883899652987837826492167345329145 | 3.19461619139555859844663082516497116222591964653143701047603991947917968704798460692226688100613217330597e-15 |
| 0.995 | 2.87844047273860811780587872656463160790303236088691152668372774663886840409304052841714891733135781686944226047712609343 | 2.8784404727135853941939366597008136821841052811738896572381901955286218320347263 | 2.502272361194206686381792571892707971302186944553755111024657205831422841714891733135781686944226047712609343e-11 |

The ratified bench literal `2.878440472713585` is likewise below truth by
`2.502311780587872656463160790303236088691152668372774663886840409304052841714891733135781686944226047712609343e-11`.
The discrepancy is physically negligible for the issued bound, but it is
scientifically material to provenance: pins reproduce the parent; the
oracle-verified kernel derives successors.
