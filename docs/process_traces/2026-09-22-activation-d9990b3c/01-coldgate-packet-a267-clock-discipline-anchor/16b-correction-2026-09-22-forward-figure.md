# 16b — Correction to addendum 16 and to A269 ruling 10 §Q5's forward figure (dated; sealed files untouched)

Correction 2026-09-22 07:50 PDT (activation e4b4ead6, executed at the bench on the A267 seat head 447fd6bf, file 16b): the forward figure "9 retained / 3 pairs" above assumed A267 cures EVERY clock_anchor_unresolved exclusion. It does not, and must not: replaying the twelve 09-22 fixtures through derive_powermetrics_anchor_v3 under CLOCK_METHOD_V3_1 bounds envelopes 02, 05, 06, 08, 09, 11, 12 (seven) and still refuses 01, 03, 04, 10 (affine_clock_fit_empty: an adjtime slew inside the capture) and 07 (wall_minus_monotonic_span_exceeded: 22.36 ms against the 15 ms backstop). On the 09-22 data the post-A267 set is therefore 7 retained / 3 disjoint pairs ((5,6), (8,9), (11,12)), which start_drift (03, 06, 09) cuts to 5 retained / 1 pair — the figure ruling 14 R6's parenthetical "(5 retained / 1 pair against 8 / 4)" carried, which is thus CORRECT as a forward projection on this night's data and is NOT withdrawn. The "9 retained / 3 pairs" figure is the forward projection for a RE-RUN under the A267 chain (network time OFF, no slews, exact tiling), where start_drift alone would cut 12 to 9 and pairs to 3. Both projections sustain the p1 standing (start_drift costs 2 envelopes and 2 pairs on the observed data; 3 envelopes and 3 pairs on a clean re-run). The withdrawn claim remains only the AS-OBSERVED one: no envelope on 09-22 was excluded for start_drift alone.

Executed evidence (this activation, worktree `JouleWise-wt-a267-review` at `447fd6bf`, fixtures `tests/fixtures/qpe01_pilot_n1_20260922/envelope-NN.json`, sha-pinned in that directory's SOURCES.md):

```
1 ('unknown', 'affine_clock_fit_empty', None, None)
2 ('bounded', None, 0.0011225390628275716, 0.00041604042053222656)
3 ('unknown', 'affine_clock_fit_empty', None, None)
4 ('unknown', 'affine_clock_fit_empty', None, None)
5 ('bounded', None, 0.00298029913760496, 0.001191854476928711)
6 ('bounded', None, 0.0021636609755001234, 0.0011534690856933594)
7 ('unknown', 'wall_minus_monotonic_span_exceeded', None, 0.022360801696777344)
8 ('bounded', None, 0.00507678015689001, 0.004542350769042969)
9 ('bounded', None, 0.00534816707993159, 0.004525184631347656)
10 ('unknown', 'affine_clock_fit_empty', None, None)
11 ('bounded', None, 0.004014973497705664, 0.0015206336975097656)
12 ('bounded', None, 0.0019389689890733398, 0.0015079975128173828)
bounded under v3.1: [2, 5, 6, 8, 9, 11, 12] count 7
```

Effect on rulings: none on any disposition. A269 ruling 10 §Q5 and refuter 11 §Q5 adopted the "9 / 3" figure by deleting both exclusion classes wholesale (their probe P1); the refuter's own caveat — "the forward argument is a prediction about unlanded code … must be re-checked against A267's twelve-envelope replay" — is what this file executes. The p1 standing of A269 is confirmed on both projections. The sentence in addendum 16 that calls the parenthetical wrong is withdrawn by this file.
