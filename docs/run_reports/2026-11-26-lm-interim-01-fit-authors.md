# lm-interim-01: as-built authorship of the fit and twin paths (RL-218 §6.3)

Source: `git log 97cbe9b16 -- <path>` with the `Co-Authored-By` trailers, grouped by model family. Git author is the
repository owner's identity unless stated. Lead-assembled 2026-11-26.

| Path | Anthropic (Claude) commits | OpenAI (Sol) commits | Other |
|---|---|---|---|
| `joulewise/cadence_looks/fit_interim.py` | Opus 5.5: 12 (dc9ba1967 … 191947d16, 11-14/15) | Sol 6.1: 2 (ac2e1ce33, a33b37a00); Sol 6.2: 4 (67623ba03, d3fb89dfd, f09469894, 6feb4f8e5) | 1 commit with no model trailer, by a different git author (087ae10db, 11-18, "verify RL-175 custody CLI and handle singular onset fits") |
| `joulewise/cadence_looks/interim_twin.py` | Mythos 5.2: 2 (6eafc9ab3, ecc548634); Opus 5.5: 1 (4eaa14016) | Sol 6.2: 3 (6feb4f8e5, 233c9179a, f66545750) | — |
| `scripts/cadence_interim_twin.py` | Mythos 5.2: 2 (6eafc9ab3, ecc548634) | Sol 6.2: 3 (6feb4f8e5, 3917d8404, 233c9179a) | — |
| `scripts/cadence_interim_twin_pins.py` | Mythos 5.2: 1 (ecc548634); Opus 5.5: 1 (4eaa14016) | — | — |

Reading: the primary fit was first written by Opus and later amended by Sol (and one untrailered commit). The twin was
first written by Sol and later amended by Mythos (custody handling) and Opus (path removal). `fit.authors` in the
manifest gives the ruled roles (RL-218 §6.3), not this history.
