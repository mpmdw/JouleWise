# Refuter, Phase 1: independent check of `candidate_acceptance_25g83_rev6.json`

Seat: independent refuter (Claude Opus 5.5), cold. Before writing this I read no judge output.
I read only the packet, the registration, the issuer and the modules it imports, the predecessor P8,
the pinned chain, cap-rule and roster files, the two committed harvest records, the disposition
registry the issuer reads, and member evidence under
`/Users/edr/night-custody/<plan id>/runs/instrument_validation/`. All scratch scripts are in
`/tmp/refuter/` (`members.py`, `frames.py`, `tq.py`, plus inline runs). Interpreter: `python3`.
The C2 venv was used only for the plist parse. mpmath is not installed in any interpreter on
this machine, so the quantile route below is my own code. It uses no library special functions.

## Bottom line

**Correct application: YES.** The candidate applies Revision 6 correctly to this corpus: the
Revision 5 issuance arithmetic (S, C, zero-headroom, the 0.25 s refusal, the `excursion_limited`
label, n ≥ 12) plus §9's window-blocked Q99, with the D-125 floor and ceiling. I re-derived every
member, statistic, quantile, prediction, operative and rule outcome by my own route, and each one
matches the candidate digit for digit. No refusal should have fired, and none did. The screen
challenge (4 members above 0.032898493715362) is correctly kept as a diagnostic and not a veto.
Revision 1 would have vetoed on it; Revisions 5 and 6 dropped that veto.

**One finding the gate must rule on explicitly (F1).** It sits upstream of the candidate and
moves no number. Both windows were admitted on a network-time-OFF receipt whose stdout is
`Network Time is already off.` The sealed text requires stdout to be exactly
`setUsingNetworkTime: Off` (§5; §7 `"stdout_exact"`). The admission was widened to accept that
wording by commit `2431dcaa` at 2026-09-30 21:13 PDT. That is about 6 h after the Revision 6 seal
`46643f1d` (15:09 PDT), and no sealed amendment followed. My physical judgment is that the
condition is still met in substance, but the sealed literal was not met. Details are below.

## Checks, each with its command and outcome

### C1. Packet integrity and pins
- `shasum -a 256 -c MANIFEST.sha256` (in the packet): every file is OK **except 9 `.log` files
  that are absent** (F2). `shasum -a 256 -c REFERENCES.sha256` (from the repo root): all 7 OK.
  The harvest records, the issuer `dc346fb0…`, chain `b5beea46…`, cap rule `6b4bcaea…`, roster
  `d8fbb403…` and P8 `52e3d18a…` all match.
- The registration hashes to `d0034003…7b78`, the same as the packet copy (`cmp`), both harvest
  records' `preregistration_sha256`, and the arm notices of C1 and C2 (`grep -r`).
- Placeholder greps: `grep -c 'TO BE PINNED AT S[E]AL'` → 0; the Revision 5 placeholder grep → 0.
- The candidate file sha256 is `aa59ebb2…9884`, matching `invocation.md` run 3. The R9 record
  sha256 is `8be16a20…18a2`, matching `derivation_notes.revision6_campaign_r9`.
- At both measurement heads (`f0e211cb`, `f54473f3`), `git show <head>:<file> | shasum` matches
  all four estimator pins, chain `b5beea46`, validator `3dc75857` and prewindow `d8458eea`. Each
  window's `custody-arm/chain.zsh.chain-source.sha256` equals `b5beea46…`.

### C2. Ledger, sessions and membership (`/tmp/refuter/members.py`)
- The predecessor-digest chain over all 376 rows links unbroken. The head is seq 376 `a5b825b7…`,
  which equals the head pin and `ledger_cutoff`. Row 276's receipt is `476e2ae8…`, which equals
  `pins.ledger_head_pin_at_first_window`.
- Derivation-kind sessions opened after seq 276: exactly two, seq 278
  `d079-epoch-25g83-r6-20261001T0617Z` and seq 328 `…20261001T2252Z`. Each declares 12 slots and
  each id matches `^d079-epoch-25g83-r6-[0-9]{8}T[0-9]{4}Z$`. Neither is null: each has 12
  finalized rows. They are the sessions the candidate names.
- All 24 finalizations are `valid` at os_build 25G83. For each one:
  - `manifest.json` and `instrument_evidence.json` hash to the row's `artifact_sha256`.
  - The content id that I recompute myself (sha256 of canonical JSON of the two hashes) equals
    the row's `content_id`.
  - The raw JSON text holds exactly one `b_fiducial_s` lexeme, and it equals the row's
    `exact_bound_lexeme_s` and the candidate member value.
  - The candidate's `manifest_sha256`, `instrument_evidence_sha256` and `source_directory`
    match.
  - `clock_anchor.method` = `powermetrics_native_second_rate_aware_set_membership_v1`
    (= `CLOCK_METHOD_V3`), `status` = `bounded`, `clock_anchor_resolved` = true, no `reason`.
  - Bindings: powermetrics `b762e5bf…`, MLX 0.31.2, 59 pulses, all detected. All 24 T1
    bindings are identical.
- Members in the candidate but not in the ledger: ∅. Valid ledger rows not in the candidate: ∅.
  **n = 24, with no missing or extra member.**
- Exclusions: none were warranted. No unresolved anchor and no out-of-range frame, and neither
  window is adverse. The candidate's `excluded_members` is `[]`, which is correct.
- Foreign rows: there are 47 valid 25G83 rows. The 23 outside this registration are 12 W1/W2
  rows plus 11 rows from 2026-09-19. All 23 content ids are in
  `configs/calibration/observation_dispositions.json` (sha256 `4a3d96da…`, as pinned). The 12
  W1/W2 ids equal the registration's `set_aside_w1w2_content_ids` exactly. Foreign rows: none.
- Prior set: 110 reservations and 110 finalizations, with nothing unfinalized. Dispositions
  {valid 77, ordinary-invalid 31, systematic-invalid 2} equal `candidate_inventory`. The prior
  set's content ids equal the ledger's finalization content ids. Both disposing decision ids are
  declared.

### C3. Median frames and R9, from raw bytes (`/tmp/refuter/frames.py`)
- For all 24 captures, `raw/powermetrics.plist` hashes to the ledger digest. I split it on NUL,
  ran `plistlib` over every sample and took the median of `elapsed_ns`. All 24 medians equal the
  R9 record's `median_frame_ms` (differences ≤ 1e-14 ms, float repr only). Range 124.81–130.34 ms,
  so every capture is inside 100–150 ms.
- Per-window median of medians: C1 129.672 ms and C2 129.648 ms, both ≤ 150. STOP-CADENCE did
  not fire.
- R9 slots: cap_trigger null everywhere; cells ≥ 1; `ratio == cells/1710000`; maximum ratio
  0.1035 ≤ 0.5. Every frame is reported, every capture is counted, and counted = 24. I did not
  recompute cells: the registration says the issuer does not, and doing so would need the
  harness.

### C4. Battery float, from raw bytes
- 48 ioreg observations (24 captures × pre and post). For each, the raw sha256 equals the
  recorded digest, and exactly one AppleSmartBattery object is present. The top-level lines read
  `ExternalConnected = Yes` and `IsCharging = No`, and |InstantAmperage| ≤ 200 after the
  two's-complement correction. `UpdateTime` is 0–180 s before the observation's wall time. Zero
  failures. Both window verdicts are `pass`, which matches the harvest records and the
  `battery_float_verdict.json` digests (`6b8ce0c5…`, `eb138080…`).

### C5. Exact-decimal source statistics (Decimal, prec 100)
I recomputed each value; each equals the candidate's string exactly.

| Statistic | Value |
|---|---|
| min | 0.02193176218569716 (C1-d07) |
| max | 0.03646286164497997 (C2-d08) |
| range | 0.01453109945928281 |
| mean, ROUND_HALF_EVEN to 1e-18 | 0.028444120869643095 |
| sample SD, df = n−1 = 23, ROUND_HALF_EVEN to 1e-18 | 0.003803438860221064 (unrounded …064389…) |
| s_within, K = 2, df = n−K = 22, same quantum | 0.003888840415839957 |

### C6. t quantiles by an independent route (`/tmp/refuter/tq.py`)
- My route computes P(|T| ≤ t) = I_y(1/2, df/2) with y = t²/(df+t²). I_y is a hypergeometric
  power series. Γ at half-integers is exact. π comes from the Gauss–Legendre AGM. The inversion is
  300-step bisection at 90 digits. It shares nothing with the issuer's routes (Lentz continued
  fraction; A&S 26.7.3/4 with π by Machin).
- Results, which also sit in the candidate rounded to 20 dp:

  | df | p | t |
  |---|---|---|
  | 23 | 0.975 | 2.06865761041904865151 |
  | 23 | 0.995 | 2.80733568376999900293 |
  | 22 | 0.975 | 2.07387306790402616585 |
  | 22 | 0.995 | 2.81875606060014349853 |

  `quantize(1e-20)` matches all four. My forward residuals |P(T>t) − (1−p)| are ≤ 1e-89. As a
  cross-check, my route also reproduces Revision 6 §9's worked constants: t(0.995,11) =
  3.105807, t(0.995,10) = 3.169273, t(0.995,35) = 2.723806, t(0.995,33) = 2.733277.
- **df is correct**: 23 = n−1 for the plain predictions and 22 = n−K for the within-window one.
- Quantile-proof blocks (packet items 5 and 7 are byte-verbatim copies of the candidate): the
  forward residuals 2.4E-80, 2.6E-81, 1.7E-80 and 1.4E-81 are all ≤ 1e-30. Agreement digits 56,
  56, 55 and 57 are all ≥ 30. Precision is 80, and the method string and both declared bounds
  are present.

### C7. Predictions (binary64, shortest repr, left-to-right `t*s*sqrt(2)`)
| Prediction | Value |
|---|---|
| P95 | 0.01112705033143238 |
| Q99 | 0.015100307220104515 |
| Q99_within | 0.01550217418713139 |

All three match the candidate exactly. Note N3: the other binary64 association,
`t*(s*sqrt2)`, gives 0.015502174187131392 for Q99_within. The candidate follows the order the
rule string is written in. The exact-decimal product is 0.0155021741871313900…, so the
candidate's value is also the nearer one. Either way the effect is at most 2e-18 s.

### C8. Operatives and rule outcomes
- Predecessor read from the P8 file: id `d079_calibration_acceptance_v2_n17_r8`, `issued`,
  derivation `911d06c3…` (= registration), ceiling `0.010164834757777545`. **This is the right
  predecessor and the right ceiling.**
- S = max(range quantized to 1e-6 with ROUND_HALF_EVEN → 0.014531, 0.010818) = **0.014531**.
  The floor does not bind, so `screen_floor_bound: false` is correct.
- C = max(0.010164834757777545, Q99 0.015100307220104515, Q99_within 0.01550217418713139, S
  0.014531) = **0.01550217418713139**, set by Q99_within. This matches `ceiling_set_by`. C − S =
  **0.00097117418713139** > 0, so `positive_headroom` is correct, with no zero_headroom and no
  clamp. The level screen is max quantized to 1e-15 = **0.036462861644980**. All match.
- Refusals and labels:
  - B > 0.25 s: 0, so no PLATEAU_INSET refusal.
  - B > 0.075 s: 0, so no `excursion_limited` label (`excursion_label: null`).
  - n = 24 ≥ 12.
  - S < C, so Revision 1's `successor_screen_exceeds_budget_ceiling` would not fire either.
  - The d125_ruling reference is present.
  - The id `…_v2_n24_25g83_r2` matches the pattern with N = n = 24 and is not r1.
- Diagnostics, correctly not vetoes:
  - Screen challenge: 4 members exceed 0.032898493715362 (C1-d03, C1-d09, C2-d04, C2-d08), and
    the candidate records 4. Under Revision 1 this would refuse (≥ 2). Revision 5 dropped it as
    a veto and Revision 6 §1 says it "stays dropped (diagnostic only)". **The candidate applied
    the right revision.**
  - P8 max + range = 0.04262208300415633, recomputed from P8's own `source_statistics`. The new
    max does not exceed it (`false`).
- Report-only §9 figures:
  - MSB 1.36e-8 and MSW 1.512e-5 give F = 0.0009 and ICC = max(0, ·) = **0**.
  - Window medians are 0.0278972433872466365 and 0.027748370766401152; their range ÷ S =
    0.0102451738… All three match.
  - ρ1 over 22 adjacent same-window member pairs, with exact Fraction ranks, is −319/1771 =
    **−29/161** = −0.180124…, which matches.
  - Per-window n, mean and SD match.

### C9. Count-rule replay and stop lines
- C1 (first counting window): counted 12, valid 12 (≥ 6, so no futility stop), members 12, no
  stop, not adverse. 12 < 24 → clause [4] → NEXT_WINDOW.
- C2: totals counted 24, members 24 → clause [3] → **CLOSE_AND_DERIVE**.
- This matches both harvest records' `next_window` and the candidate's `revision6_count_replay`.
  `stop_flags` is `[]` in both harvests. No C3 exists, and none was due.

### C10. Start-condition records
- Both windows' `night/start_conditions.json` (`da1b4df0…`, `e46d5fce…`) equal the hashes in the
  harvest records and the candidate. Each has entries (a) to (g) and `result: admitted`.
- (g): script `d8458eea…` (the pin), exit 0, continuous_clean_s 600.
- (f): same boot (`cd5b815a…`). The receipt is about 1245 s older than the first capture on both
  wall and monotonic clocks (≥ 600). Exit code 0.
- **But stdout = `Network Time is already off.\n` in both windows → F1.**

## Findings

**F1: registration-fidelity departure in start condition (f), both windows. Severity: must be
ruled on; not number-moving.**

- The sealed text (§5 and §7 JSON) requires stdout to be exactly `setUsingNetworkTime: Off`.
- `joulewise/network_time_off.py` now admits a second statement, `network time is already off`.
  That came from commit `2431dcaa`. `git merge-base --is-ancestor 2431dcaa 46643f1d` → NOT an
  ancestor of the seal. Both measurement heads contain it.
- The commit message records the cause: the first C1 attempt (`c1-20261001T0137Z`, packet
  `unregistered-attempts/`) was refused at t0 for exactly this wording. The admission was then
  widened in code, without a sealed amendment.
- §5 states that "a change to any of [these items] voids this revision", and §7 says
  continuation after a refusal is "only by a sealed amendment… no command-line ruling".
- My physical reading: D-186's purpose is that network time is OFF and settled ≥ 600 s before the
  first capture. `already off` is systemsetup's own statement of that end state, so the purpose
  is served. The R9 record lists zero clock-movement or empty-fit refusals, and every anchor
  resolved.
- My view is that F1 changes no member and no number, and that a sealed erratum could cure it.
  But it is a literal breach of a sealed §5 item, so a PASS must name and dispose of it rather
  than pass it silently.

**F2: packet incompleteness, runbook §4.3 item 3.**

- 9 files that `MANIFEST.sha256` and `SOURCES.tsv` list are absent from the committed packet:
  - `c1/` and `c2/`: `night.log`, `operator_logs/derivation-chain.log`, `night/chain.stdout.log`
    and `night/chain.stderr.log`;
  - `unregistered-attempts/c1-20261001T0137Z/night.log`.
- Cause: `.gitignore:45 docs/process_traces/**/*.log` (`git check-ignore -v`).
- Their manifest digests equal the digests in the harvest inventories, so they are consistent
  but unreadable here. As a result, the chain's `slot_start`, `slot_end` and abort lines are not
  in the packet.
- This does not affect correctness: the ledger shows all 24 slots finalized and none unused.

**Notes (not defects):**
- **N1.** The packet item 4 assertion should be read as "the only *anchor* exclusion mechanism".
  Revision 6 §8 adds two non-anchor exclusions, `frame_out_of_covered_range` and `adverse_window`
  (issuer lines ~1619–1631). Neither fired here. In code, an unresolved anchor with any other
  detail refuses (`_select_members`, `REGISTERED_CORPUS_EXCLUSION_REASONS = {affine_clock_fit_empty}`).
- **N2.** Revision 1's glossary says t(p, df) is what |T| stays within "with probability p". Read
  literally, that gives t = 2.3979 at df 23, p 0.975. The operative clauses fix the one-sided
  convention the issuer uses: the forward check P(T>t) = 1−p, the name Q99, and Revision 6 §9's
  worked numbers. The difference is in wording only.
- **N3.** See C7: the binary64 association order affects only the 18th significant digit.
- **N4.** The successor id was produced by the issuer's default. The registration requires it to
  be set explicitly at issuance, which is D-138's act and not the candidate's. Separately,
  `backfill_candidate.required_verification` still uses Revision 1 wording ("screen-challenge
  outcome… D-125 default").
