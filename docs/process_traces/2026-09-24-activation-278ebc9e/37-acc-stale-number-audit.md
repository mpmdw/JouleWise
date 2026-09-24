# ACCEPTANCE-25G83-01 — stale-number audit (2026-09-24)

Authority: cold gate ACCEPTANCE-25G83-01, `docs/process_traces/2026-09-24-activation-278ebc9e/31-coldgate-packet-acceptance/20-coldgate-fable-acceptance-ruling.md` §3 item 2(j). Issued r6/r7 artifacts and their historical validator rows remain immutable.

| r6-keyed number | Current role | 25G83/v4 disposition | Reason |
|---|---|---|---|
| 0.032898493715362 s | r6 preflight level screen; revision 1 screen challenge | Replace as operative level screen with the new corpus maximum, quantized to 1e-15 s. Retain only the count above r6 as diagnostic. | The new cadence changes the B distribution; the r6 level is not a physical issue barrier. |
| 0.009724 s | r6 bracket screen (quantized corpus range) | Replace with S = max(new range quantized to 1e-6 s, 0.010818 s). | The successor's own corpus supplies its range; the D-125 genesis floor remains binding. |
| 0.010165 s (exact r6 ceiling 0.010164834757777545 s) | Predecessor maximum budgetable drift | Retain as the inherited predecessor-C input, then replace operative C with max(predecessor C, new Q99, S). | D-125 lineage monotonicity prevents lowering the ceiling; v4 may raise it. |
| 0.010818 s | D-125 genesis floor for S | Stay. | The floor is a ratified lower bound independent of the r6 cadence and may not be lowered. |
| `calibration_bracket_max_drift_s` 0.010 s | Production policy field documented in `docs/contracts/run_bundle_layout.md` | Stay as a policy value until the registered successor's operative S/C and the pack policy are reconciled in the atomic re-freeze; do not silently interpret it as v4's S or C. | This policy bound is separate from the acceptance artifact's derived screen and ceiling. A 0.010 s hard policy can refuse a drift that v4 would otherwise admit, conservatively. |

The r6 maximum-plus-range diagnostic 0.04262208300415633 s also stays diagnostic only. Its arithmetic is tied to r6 and never sets the successor level screen.
