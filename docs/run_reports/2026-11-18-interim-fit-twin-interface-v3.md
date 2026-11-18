# Interim fit twin interface revision 3

This revision resolves T12 in [the round 3 audit](2026-11-18-interim-fit-twin-rl184-audit-3.md). The lead's code-blind handoff identifies the 91 fixed output keys checked against the standalone Step 3 source pinned by RL-166 Q6. The pinned source SHA-256 is `84a1a5530ab06e688b000c84f248b2c4e561e8330f37d3132ec47aa2572eb173`. The key set in [the twin](../../scripts/cadence_interim_twin.py) has SHA-256 `4e20f7dd300b9b45de4854b9932420a98a8a9a221829591432c791339955f02e` when sorted bytewise with one LF following every key. [RL-166 Q6](https://github.com/mpmdw/JouleWise/blob/61e8c9c2ccfd023c82e0da048dd89f4ed854a5bc/docs/research-audits/2026-11-10-fable/RESEARCH-LEAD-DECISIONS.md#L15879-L15887)

## T12 histogram keys

- Collect keys contributed by surviving legs in `(turn_start, last_token]`. Missing or non-string pressure contributes the string `None`.
- Reject a key first if its lowercase form contains `joule`, `watt`, `power_w`, `gpu_power`, `energy_j`, `_mj`, or `_wh`, ends in `_j` or `_w`, or equals `e`.
- Accept an exact case-sensitive match to a fixed key, a leg ID bound to the cell's Step 3 call, or one of `Nominal`, `Moderate`, `Heavy`, `Trapping`, `Sleeping`, `Unknown`, `None`, and `not_read`. The interim twin binds each surviving leg by its full Stage 1 `leg_key` within its own prompt-size cell.
- When a surviving leg contributes any other in-window key, give that cell `status = "not_run"` and `gamma_estimable = null`. Other cells continue. [RL-183a §3](https://github.com/mpmdw/JouleWise/blob/61e8c9c2ccfd023c82e0da048dd89f4ed854a5bc/docs/research-audits/2026-11-10-fable/RESEARCH-LEAD-DECISIONS.md#L20422-L20431)

## Regression and census handoff

| Clause | Synthetic regression | Result |
| --- | --- | --- |
| Fixed and state keys | Verify the 91-key digest and admit every fixed key and all eight state names. Missing and non-string pressure produce only `None` in the histogram. | PASS |
| Cell bindings and precedence | Admit another surviving leg's same-cell ID. Refuse an ID belonging only to another cell and a bound ID ending in `_W`. Exercise all listed forbidden forms using bound IDs. The other cell keeps its valid result. | PASS |
| Raw Step 3 cell regression | Admit `slope` and `gamma_estimability`. Refuse `gamma_estimable`, `SLOPE`, and `UnregisteredState` when they are absent from the cell's bindings. An unknown value exactly at turn start leaves the cell unchanged. | PASS |
| Bound child | The actual `python -I -B` child accepts a full Stage 1 leg ID in a surviving leg's histogram with the registered decoder and initializer. The outer digit scan and prior acceptance controls pass. | PASS |

All 46 focused tests passed with the registered decoder and initializer. For a component rerun, `step3_cells` takes `(prompt_tokens, leg_key, read_leg)` entries. The bundle reader returns the observations and its set of histogram keys together.

The twin candidate for the paired census is draft PR #816, `scripts/cadence_interim_twin.py`, SHA-256 `e9493f1101d9124c4c8afc7f59a264472e39e3c82c6f9985650ee17fd6a184ad`. Astra's rerun pairs that candidate with the primary and parent head supplied by their owners. P01 through P03 and the primary Stage 1 malformed-input refusals remain with those owners. [RL-184 §§3.1–3.2](https://github.com/mpmdw/JouleWise/blob/61e8c9c2ccfd023c82e0da048dd89f4ed854a5bc/docs/research-audits/2026-11-10-fable/RESEARCH-LEAD-DECISIONS.md#L21083-L21119)
