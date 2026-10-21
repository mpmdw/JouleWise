# B2 NR1 cold passes: disposition (lead, activation 283e9802, 2026-10-21)

Code: `lane/2026-10-20-bytes-analysis-a8` at 19f88e5b7, reviewed as `ci/2026-10-21-b2-nr1` a6bcfbd1c (draft PR #515).
Passes, blind to each other, both executing (whole module 57 OK in each):

- Fable 5.1: `VERDICT: ACCEPT` (JouleWise-data `claude/b2-nr1-cold-fable` 3f2324615, `reports/b2-nr1-cold/fable.md`).
- Opus 5.5: `VERDICT: ACCEPT WITH CHANGES` (JouleWise-data `claude/b2-nr1-cold-opus` d11ba9203, `reports/b2-nr1-cold/opus.md`).

Both found registered arithmetic bit-identical against 1d6f18fbf, the fixture identical to the judge's variant A, their
own C_j within the 1% HC3 half-width bar of the module, and blinding intact. The Opus pass counts as ledger row 1
(independent executing review); both count as row 4.

## Dispositions

| Finding | Disposition |
| --- | --- |
| Opus M1 = Fable L2: C_j is `mean_pass(P_max·τ / T_p)`; the exact coherent-offset support of the ratio-of-means power is `mean_pass(P_max·τ) / mean_pass(T_p)` | **Fixed (fix round below).** Both seats agree the second form is exact. Fable shows the implemented form is smaller than the exact one when the longer pass has the higher edge power, so it is not conservative in general. The ruling's "averaged as B is" and the registration's "T_i the model's decode time" mean the exact form; the a017 fix brief's per-run `/ duration_s` was the lead's wording error. Carry the per-run term in joules, average over passes, divide by the point's mean duration. This is a labelled alternative on uncollected data; no registered number changes. |
| Opus L1, Fable L1: a non-finite bound or sensitivity refuses the fit stage | **Fixed.** The ruling says missing bound = flag, no refusal. Non-finite per-point bound or sensitivity gives the flag and keeps the registered fit. |
| Opus L2: nonnegative/finite check on the point mean, not per run | **Fixed** with L1: check each run's term; a bad run gives the flag. |
| Opus L3: before-edge sample ill-defined on an exact tie | Rejected, no change: arises only on the knife-edge fixture the ruling removed; on a bench it adds noise of order label error / Δt. |
| Opus L4: `primary_intervals` omits `sensitivity_flag` | **Fixed:** copy it as `systematics_flag` is copied. |
| Opus L5: `3.182446305` without derivation | **Fixed:** comment (t 0.975 at df 3). |
| Fable L3: `p = (10/1000)/.1` restates knob values | **Fixed:** read the latency and sample interval from the fixture. |
| Fable L4: "22 to 25 ms" in a code string without derivation | **Fixed:** comment citing the judge's §2.1 (Δt + round trip 21.8 to 24.9 ms on the two committed recordings). |
| Fable L5: RNG constant 7919 | Rejected: not a tolerance or measured quantity; purpose already stated. |
| Fable L2 tail: registration should name the normalisation | **Fixed** on `docs/2026-10-20-bytes-registration`: one sentence in the H2 offset paragraph stating C uses pass-averaged joules over the point's mean decode time. |

M1 changes a printed number (the alternative's C), so the fix gets a delta cold pass from both models, blind and executing.

## Executed evidence

Lead check on the Mac at 19f88e5b7 before the passes (fresh TMPDIR, `JW_B5_SYNTHETIC_ONLY=1`):

```
$ /opt/homebrew/bin/python3.13 -m unittest tests.test_bytes_analysis.ProductionArchiveTests.test_nr1_offset_term_covers_constant_label_offset
Ran 1 test in 12.544s
OK
exit 0
```

Program comparison of the fix report's 60-campaign table against the judge's variant A table (`fable.md` lines 210-227):
18 rows, 72 registered rates compared, 0 differ.

## Delta passes on the fix (19f88e5b7..0743a7b90, registration 9c91e9b8d..91b20d7c2)

Fix: Sol 6.1 high, Codex Cloud thread 01a15dc5; report JouleWise-data `codex/bytes-b2-nr1-coldfix`
`reports/bytes-b2-nr1-coldfix/REPORT.md`. Both delta passes blind, executing, whole module 58 OK:

- Opus 5.5: `VERDICT: ACCEPT` (`claude/b2-nr1-delta-opus` 1f55497e6, `reports/b2-nr1-delta/opus.md`). One info item
  (fallback flag text unreachable through the CLI; the old-fit/new-heldout path refuses before any arithmetic).
- Fable 5.1: `VERDICT: ACCEPT` (`claude/b2-nr1-delta-fable` a2edc54b0, `reports/b2-nr1-delta/fable.md`). Registered
  arithmetic bit-identical in three worlds; own C (exact rational A, raw streams) equal to the bit or within 1e-11;
  a per-run sign-check mutant is killed by the new regression.

| Finding | Disposition |
| --- | --- |
| Fable F1: the flag names the run id, which repeats across passes | Rejected for now (representation only): the pass row carries the null on the right pass. |
| Fable F2 / Opus info: a bound that is null with no per-run flag prints no run name | Rejected (representation only): unreachable through the stage chain. |
