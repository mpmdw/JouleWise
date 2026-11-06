# ALIGN v4 operating-characteristics table (Ruling 6)

**Status:** secondary, print-only simulation. It neither imports nor changes the
frozen alternative desk (`4d54cb47b`), calibration (`7fbd95e31`), or any
`pilot_analysis` registered path. Reproduce with:

```sh
python3 scripts/align_v4_oc_sim.py --seed 20261106 --draws 100000
```

The seed is fixed. Inputs are the chair's pair SD **2.97 J**, within-window
noise **2.1--5 J**, pilot-8--10 residual scales **4.511563 and 4.029927 J**, and
independent exclusion probabilities **5%, 10%, 14%**. Probabilities below use
100,000 draws except the extension table, which is the exact binomial result.

## Acceptance-set OC and proposed bars

Allocate a 2% nominal false-fail probability to each of U1--U6. Each criterion
therefore has `(pass, inconclusive, fail) = (0.980, 0, 0.020)` at the nominal
point in this sizing model; the whole-series values are **(0.88584, 0,
0.11416)**. Thus the proposed equal allocation keeps false fail below the
chair's 15% ceiling. The physical bars carried into the simulation are U3 =
`3 × 2.97 = 8.91 J` and U5 = `0.1 × min(s_r) = 0.402993 J`; U1, U2, U4 and U6
retain their ruled bars, with the 2% allocation used only for OC sizing.

## Extension rule

Probability of the stated eligible-pair count after the indicated look:

| exclusion | D3 ≥19 / ≥21 | D4 ≥19 / ≥21 | D5 ≥19 / ≥21 |
|---:|---:|---:|---:|
| 5% | .97782 / .69815 | .99904 / .97022 | .99997 / .99849 |
| 10% | .82807 / .33920 | .97234 / .78574 | .99702 / .96014 |
| 14% | .62833 / .16594 | .89141 / .56132 | .97798 / .85360 |

## Deciding contrast

Cells are `P(pass) / P(inconclusive) / P(fail)`. “Stage” adds the ruled stage
indicator (one further fitted degree of freedom).

| δ J | σ J | no stage | stage |
|---:|---:|---:|---:|
|0|2.1|0/.02858/.97142|0/.04632/.95368|
|0|3|0/.24237/.75763|0/.31724/.68276|
|0|4.5|0/.59941/.40059|0/.67966/.32034|
|6|2.1|0/.98316/.01684|0/.99090/.00910|
|6|3|.00005/.98368/.01627|.00002/.99103/.00895|
|6|4.5|.00040/.98335/.01625|.00019/.99080/.00901|
|10|2.1|.01657/.98343/0|.00915/.99085/0|
|10|3|.01663/.98336/.00001|.00879/.99120/.00001|
|10|4.5|.01544/.98413/.00043|.00912/.99069/.00019|
|15|2.1|.89276/.10724/0|.84596/.15404/0|
|15|3|.58589/.41411/0|.50026/.49974/0|
|15|4.5|.28685/.71315/0|.21676/.78324/0|

## Chair §C MDE

Simulating uniformly over §C's `m=19..26` and `σ=2.1..5 J` inputs gives an
MDE distribution (J): minimum **10.9582**, p05 **11.0989**, median **11.7402**,
p95 **12.4197**, maximum **12.6683**. The draw evaluates `10 +
1.645 σ sqrt(2/m)`; it is prospective sizing, not a re-analysis of a pilot.

The tests pin byte-for-byte seeded determinism and two independent closed-form
oracles: an exact binomial tail and the finite-sample conformal ceiling rank.
