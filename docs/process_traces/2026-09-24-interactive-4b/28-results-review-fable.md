# Results review of session C (fresh Fable 5.1 seat, read-only): STAND WITH LISTED CORRECTIONS

Filed by the lead from the seat's hand-back. The scratch scripts are `/tmp/4b-osaudit/results-fable/{recompute.py,census.py}`.

## Independent recomputation

The seat's own code read the raw summary_metrics of the 12 cells named in the six non-discarded block_accepted records. It inverted t numerically (df = 5), checking itself against the textbook 2.5706 at 97.5 %, and got **t = 4.5257**.

| Quantity | Result | Match |
|---|---|---|
| E | 0.99991 [0.99548, 1.00435]; per-block logs +0.00369, −0.00235, −0.00225, −0.00164, +0.00109, +0.00089; SD 0.00240 | identical |
| R | 0.99471 [0.99192, 0.99751]; SD 0.00152; excludes 1 | identical |
| Absolute E | −0.000037 [−0.001764, +0.001690] J/token | identical |
| C3 v2.5 gates | SD of log E: I 0.30 %, SH 0.22 %; max idle 0.207 W | pass |
| Drift ÷ net | 5.4–12.0 % | identical |
| Every cell | the same output-token hash, 512 tokens, succeeded | |
| R5 | I median 131.847 ms (131.67–132.00); 300 × median = 39.55 s; zero invalid I runs | identical |
| Probes | I 7.694 s (18 repeats), SH 7.614, D 7.556 (6 repeats), B 57.274 | identical |
| Census totals | | match |

## Corrections required, all applied in 26

- The widened-interval recipe must be stated. The spec reading gives [0.866, 1.154] against the harness's [0.861, 1.161], and both cross δ.
- The workload scope must be stated: one prompt, one model, 512 tokens, ≈ 6.4 s.
- The launch facts must be disclosed: SH is a Claude Code/Terminal descendant at 0x21; I at 0x15; D at 0x11 (the coalescing class); B at 0x09.
- "D does not throttle" rests on 2 cold probe-only cells against hot I/SH probes. Keep it descriptive, with a thermal caveat.
- Network time: rc 0, but the `Error:-99` output means "paused" rests on the return code; anchor bounds ≤ 4 ms show it did not matter.
- List the largest per-cell census flags (corespotlightd at 30 % in C1-04 SH idle; PerfPowerServices at 16 % in C1-03 I), not only the totals.
- Note that every bundle's claim precheck is ineligible, which is why nothing is claim-bearing.
