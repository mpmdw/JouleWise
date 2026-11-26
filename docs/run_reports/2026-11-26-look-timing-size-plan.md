# RL-217 E.6 timing fixture size plan

The lead assigned this [AGENT] fixture repair against `align/2026-11-14-look-manifest` at `8c2570349`. Mission M0 found no active stop card. The public manifest supplies the generated span IDs, leg IDs, bundle and stream paths, and target byte counts.

The timing helper keeps the synthetic records used by the look's readers, extends the generated meter polls, and sizes the remaining streams with synthetic records and format-preserving padding. Synthetic pin creation hashes one file at a time with bounded memory. The size-manifest invocation measures one stage-2 trial.

The focused `CampaignTimingSizes` checks passed on a small synthetic manifest and verified that CSV readers still see the original column names and literal timestamp cells after sizing. A write-counting generation run against the committed public manifest passed `check_sizes` for 14 spans, 72 legs, and all 1,010 stream paths. It counted 38,158,707,774 bytes with a maximum deviation of 0.800%. The manifest's code pin list had no overlap with the diff. Hosted CI runs the larger suites under the standing local test budget.

The lead runs the literal timing on the Air outside an agent seat. The generated fixture uses about 38.2 GB of temporary space.

```sh
env OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1 taskpolicy -c utility python3 -B -m tests.cadence.look_campaign_timing --size-manifest docs/process/cadence/looks/lm-interim-01.json
```
