# P2-046 closed-form fixtures

Status: **PROVISIONAL fixture evidence only**. These synthetic rows do not
measure a Mac, validate a physical interval-support bound, or amend P2-038.

The low/high plateau values are the medians of the declared stable-state
samples (`[1,1]` and `[9,9]`). The frozen midpoint threshold is therefore
`(low_plateau_w + high_plateau_w) / 2 = (1 + 9) / 2 = 5 W`. A response begins
at the first of two consecutive target samples. Offset is the response-support
midpoint minus the marker; each transition bound is the maximum absolute
support endpoint relative to the marker.

Hand calculation for `valid_observations.json`:

| Direction | Response supports relative to marker (s) | Offsets (s) | Median center (s) | Residuals (s) | Direction bound (s) |
|---|---|---|---:|---|---:|
| idle→load | `[0,2]`, `[2,4]`, `[0,2]`, `[2,4]` | `1,3,1,3` | 2 | `-1,+1,-1,+1` | 4 |
| load→idle | `[-1,1]`, `[1,3]`, `[-1,1]`, `[1,3]` | `0,2,0,2` | 1 | `-1,+1,-1,+1` | 3 |

Therefore the overall fixture-only conservative support bound is
`max(4, 3) = 4 s`. It is not a confidence or tolerance bound.

`malformed_observations.json` omits the required `transitions` member.
`missing_transition_observations.json` supplies none of the eight frozen
transition IDs. Both must be refused before artifact emission.
